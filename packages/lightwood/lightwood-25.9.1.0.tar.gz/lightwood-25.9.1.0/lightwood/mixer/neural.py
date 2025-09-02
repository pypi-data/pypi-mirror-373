import time
from copy import deepcopy
from collections import deque
from typing import Dict, List, Optional

import torch
import numpy as np
import pandas as pd
from torch import nn
import torch_optimizer as ad_optim
from sklearn.metrics import r2_score
from torch.cuda.amp import GradScaler
from torch.utils.data import DataLoader
from torch.nn.modules.loss import MSELoss
from torch.optim.optimizer import Optimizer

from type_infer.dtype import dtype
from lightwood.helpers.log import log
from lightwood.encoder.base import BaseEncoder
from lightwood.helpers.torch import LightwoodAutocast
from lightwood.data.encoded_ds import EncodedDs
from lightwood.mixer.base import BaseMixer
from lightwood.mixer.helpers.ar_net import ArNet
from lightwood.mixer.helpers.default_net import DefaultNet
from lightwood.api.types import PredictionArguments
from lightwood.mixer.helpers.transform_corss_entropy_loss import TransformCrossEntropyLoss


class Neural(BaseMixer):
    model: nn.Module
    dtype_dict: dict
    target: str
    epochs_to_best: int
    fit_on_dev: bool
    supports_proba: bool

    def __init__(
            self,
            stop_after: float,
            target: str,
            dtype_dict: Dict[str, str],
            target_encoder: BaseEncoder,
            net: str,
            fit_on_dev: bool,
            search_hyperparameters: bool,
            n_epochs: Optional[int] = None,
            lr: Optional[float] = None,
    ):
        """
        The Neural mixer trains a fully connected dense network from concatenated encoded outputs of each of the features in the dataset to predicted the encoded output. 
        
        :param stop_after: How long the total fitting process should take
        :param target: Name of the target column
        :param dtype_dict: Data type dictionary
        :param target_encoder: Reference to the encoder used for the target
        :param net: The network type to use (`DeafultNet` or `ArNet`)
        :param fit_on_dev: If we should fit on the dev dataset
        :param search_hyperparameters: If the network should run a more through hyperparameter search (currently disabled)
        :param n_epochs: amount of epochs that the network will be trained for. Supersedes all other early stopping criteria if specified.
        :param lr: learning rate for the network. By default, it is automatically selected based on an initial search process.
        """ # noqa
        super().__init__(stop_after)
        self.dtype_dict = dtype_dict
        self.target = target
        self.target_encoder = target_encoder
        self.num_hidden = 1
        self.epochs_to_best = 0
        self.n_epochs = n_epochs
        self.lr = lr
        self.loss_hist_len = 7  # length of queue to use for early stopping
        self.fit_on_dev = fit_on_dev
        self.net_name = net
        self.supports_proba = dtype_dict[target] in [dtype.binary, dtype.categorical]
        self.search_hyperparameters = search_hyperparameters
        self.stable = True

    def _final_tuning(self, data):
        if self.dtype_dict[self.target] in (dtype.integer, dtype.float, dtype.quantity):
            self.model = self.model.eval()
            with torch.no_grad():
                acc_dict = {}
                for decode_log in [True, False]:
                    self.target_encoder.decode_log = decode_log
                    decoded_predictions = []
                    decoded_real_values = []
                    for X, Y in data:
                        X = X.to(self.model.device)
                        Y = Y.to(self.model.device)
                        Yh = self._net_call(X)

                        Yh = torch.unsqueeze(Yh, 0) if len(Yh.shape) < 2 else Yh
                        Y = torch.unsqueeze(Y, 0) if len(Y.shape) < 2 else Y

                        decoded_predictions.extend(self.target_encoder.decode(Yh))
                        decoded_real_values.extend(self.target_encoder.decode(Y))

                    acc_dict[decode_log] = r2_score(decoded_real_values, decoded_predictions)

            self.target_encoder.decode_log = acc_dict[True] > acc_dict[False]

    def _select_criterion(self) -> torch.nn.Module:
        if self.dtype_dict[self.target] in (dtype.categorical, dtype.binary):
            criterion = TransformCrossEntropyLoss(weight=self.target_encoder.index_weights.to(self.model.device))
        elif self.dtype_dict[self.target] in (dtype.tags, dtype.cat_tsarray):
            criterion = nn.BCEWithLogitsLoss()
        elif self.dtype_dict[self.target] in (dtype.cat_array, ):
            criterion = nn.L1Loss()
        elif self.dtype_dict[self.target] in (dtype.integer, dtype.float, dtype.quantity, dtype.num_array):
            criterion = MSELoss()
        else:
            criterion = MSELoss()

        return criterion

    def _select_optimizer(self, model, lr) -> Optimizer:
        optimizer = ad_optim.Ranger(model.parameters(), lr=lr, weight_decay=2e-2)
        return optimizer

    def _find_lr(self, train_data):
        lr = 1e-4  # good starting point as search escalates
        lrs = deque([5e-4, 1e-3, 2e-3, 3e-3, 5e-3, 1e-2, 5e-2, 1e-1])
        starting_model = deepcopy(self.model)
        criterion = self._select_criterion()
        scaler = GradScaler()

        running_losses = deque(maxlen=self.loss_hist_len)
        lr_log = deque(maxlen=self.loss_hist_len)
        best_model = self.model
        stop = False

        n_steps = 10
        cum_loss = 0

        while stop is False:
            # overfit learning on first n_steps samples (biased, but we only want an intuition on what LR is decent)
            dl = DataLoader(train_data,
                            batch_size=min(len(train_data.data_frame), 32, self.batch_size),
                            shuffle=False)
            dl_iter = iter(dl)
            self.model = deepcopy(starting_model)
            self.model.train()
            optimizer = self._select_optimizer(self.model, lr=lr)

            for i in range(n_steps):
                try:
                    X, Y = next(dl_iter)
                except StopIteration:
                    dl_iter = iter(dl)
                    X, Y = next(dl_iter)

                X = X.to(self.model.device)
                Y = Y.to(self.model.device)

                with LightwoodAutocast():
                    optimizer.zero_grad()
                    Yh = self._net_call(X)
                    loss = criterion(Yh, Y)
                    if LightwoodAutocast.active:
                        scaler.scale(loss).backward()
                        scaler.step(optimizer)
                        scaler.update()
                    else:
                        loss.backward()
                        optimizer.step()
                cum_loss += loss.item()

            log.info(f'Loss of {cum_loss} with learning rate {lr}')
            running_losses.append(cum_loss)
            lr_log.append(lr)
            cum_loss = 0
            lr = lrs.popleft()
            if len(lrs) == 0:
                stop = True

            # store model if best so far
            inv_running_losses = list(running_losses)[::-1]  # invert so when tied we pick the most aggresive LR
            best_loss_idx = np.nanargmin(inv_running_losses)  # nanargmin ignores nans that may arise
            if best_loss_idx == 0:
                best_model = deepcopy(self.model)  # store model for slight time savings
                best_loss_lr = lr_log[-1]

        lr = best_loss_lr
        log.info(f'Found learning rate of: {lr}')
        return lr, best_model

    def _max_fit(self, train_dl, dev_dl, criterion, optimizer, scaler, stop_after, return_model_after):
        epochs_to_best = 0
        best_dev_error = pow(2, 32)
        running_errors = deque(maxlen=self.loss_hist_len)
        best_model = self.model

        for epoch in range(1, return_model_after + 1):
            self.model = self.model.train()
            running_losses: List[float] = []
            for i, (X, Y) in enumerate(train_dl):
                X = X.to(self.model.device)
                Y = Y.to(self.model.device)
                with LightwoodAutocast():
                    optimizer.zero_grad()
                    Yh = self._net_call(X)
                    loss = criterion(Yh, Y)
                    if LightwoodAutocast.active:
                        scaler.scale(loss).backward()
                        scaler.step(optimizer)
                        scaler.update()
                    else:
                        loss.backward()
                        optimizer.step()

                running_losses.append(loss.item())
                if (time.time() - self.started) > stop_after:
                    break

            train_error = np.mean(running_losses)
            epoch_error = self._error(dev_dl, criterion)
            running_errors.append(epoch_error)
            log.info(f'Loss @ epoch {epoch}: {epoch_error}')

            if np.isnan(train_error) or np.isnan(
                    running_errors[-1]) or np.isinf(train_error) or np.isinf(
                    running_errors[-1]):
                break

            if best_dev_error > running_errors[-1]:
                best_dev_error = running_errors[-1]
                best_model = deepcopy(self.model)
                epochs_to_best = epoch

            # manually set epoch limit
            if self.n_epochs is not None:
                if epoch > self.n_epochs:
                    break

            # automated early stopping
            else:
                if len(running_errors) >= self.loss_hist_len:
                    delta_mean = np.average([
                        running_errors[-i - 1] - running_errors[-i] for i in range(len(running_errors) - 1)],
                        weights=[(1 / 2)**i for i in range(len(running_errors) - 1)])
                    if delta_mean >= 0:
                        break
                elif (time.time() - self.started) > stop_after:
                    break
                elif running_errors[-1] < 0.0001 or train_error < 0.0001:
                    break

        if np.isnan(best_dev_error):
            best_dev_error = pow(2, 32)
        return best_model, epochs_to_best, best_dev_error

    def _error(self, dev_dl, criterion) -> float:
        self.model = self.model.eval()
        running_losses: List[float] = []
        with torch.no_grad():
            for X, Y in dev_dl:
                X = X.to(self.model.device)
                Y = Y.to(self.model.device)
                Yh = self._net_call(X)
                running_losses.append(criterion(Yh, Y).item())
            return np.mean(running_losses)

    def _init_net(self, ds: EncodedDs):
        self.net_class = DefaultNet if self.net_name == 'DefaultNet' else ArNet

        X, Y = ds[0]
        net_kwargs = {'input_size': len(X),
                      'output_size': len(Y),
                      'num_hidden': self.num_hidden,
                      'dropout': 0}

        if self.net_class == ArNet:
            net_kwargs['encoder_span'] = ds.encoder_spans
            net_kwargs['target_name'] = self.target

        self.model = self.net_class(**net_kwargs)

    def _net_call(self, x: torch.Tensor) -> torch.Tensor:
        return self.model(x)

    # @TODO: Compare partial fitting fully on and fully off on the benchmarks!
    # @TODO: Writeup on the methodology for partial fitting
    def _fit(self, train_data: EncodedDs, dev_data: EncodedDs) -> None:
        """
        Fits the Neural mixer on some data, making it ready to predict

        :param train_data: The network is fit/trained on this
        :param dev_data: Data used for early stopping and hyperparameter determination
        """
        # ConcatedEncodedDs
        self.started = time.time()
        self.batch_size = min(200, int(len(train_data) / 10))
        self.batch_size = max(40, self.batch_size)

        dev_dl = DataLoader(dev_data, batch_size=self.batch_size, shuffle=False)
        train_dl = DataLoader(train_data, batch_size=self.batch_size, shuffle=False)

        # Find learning rate & keep initial weights
        self._init_net(train_data)
        if not self.lr:
            self.lr, self.model = self._find_lr(train_data)

        # Keep on training
        optimizer = self._select_optimizer(self.model, lr=self.lr)
        criterion = self._select_criterion()
        scaler = GradScaler()

        # Only 0.8 of the remaining time budget is used to allow some time for the final tuning and partial fit
        self.model, epoch_to_best_model, _ = self._max_fit(
            train_dl, dev_dl, criterion, optimizer, scaler, (self.stop_after - (time.time() - self.started)) * 0.8,
            return_model_after=20000)

        self.epochs_to_best += epoch_to_best_model

        if self.fit_on_dev:
            self.partial_fit(dev_data, train_data)

    def fit(self, train_data: EncodedDs, dev_data: EncodedDs) -> None:
        self._fit(train_data, dev_data)
        self._final_tuning(dev_data)

    def partial_fit(self, train_data: EncodedDs, dev_data: EncodedDs, args: Optional[dict] = None) -> None:
        """
        Augments the mixer's fit with new data, nr of epochs is based on the amount of epochs the original fitting took

        :param train_data: The network is fit/trained on this
        :param dev_data: Data used for early stopping and hyperparameter determination
        """

        # Based this on how long the initial training loop took, at a low learning rate as to not mock anything up tooo badly # noqa
        self.started = time.time()
        train_dl = DataLoader(train_data, batch_size=self.batch_size, shuffle=True)
        dev_dl = DataLoader(dev_data, batch_size=self.batch_size, shuffle=True)
        optimizer = self._select_optimizer(self.model, lr=self.lr)
        criterion = self._select_criterion()
        scaler = GradScaler()

        self.model, _, _ = self._max_fit(train_dl, dev_dl, criterion, optimizer, scaler,
                                         self.stop_after * 0.1, max(1, int(self.epochs_to_best / 3)))

    def __call__(self, ds: EncodedDs,
                 args: PredictionArguments = PredictionArguments()) -> pd.DataFrame:
        """
        Make predictions based on datasource with the same features as the ones used for fitting

        :param ds: Predictions are generate from it
        :param arg: Any additional arguments used in predicting

        :returns: A dataframe cotaining the decoded predictions and (depending on the args) additional information such as the probabilites for each target class
        """ # noqa
        self.model = self.model.eval()
        decoded_predictions: List[object] = []
        all_probs: List[List[float]] = []
        rev_map = {}

        with torch.no_grad():
            for idx, (X, Y) in enumerate(ds):
                X = X.to(self.model.device)
                Yh = self._net_call(X)
                Yh = torch.unsqueeze(Yh, 0) if len(Yh.shape) < 2 else Yh

                kwargs = {}
                for dep in self.target_encoder.dependencies:
                    kwargs['dependency_data'] = {dep: ds.data_frame.iloc[idx][[dep]].values}

                if args.predict_proba and self.supports_proba:
                    decoded_prediction, probs, rev_map = self.target_encoder.decode_probabilities(Yh, **kwargs)
                    all_probs.append(probs)
                else:
                    decoded_prediction = self.target_encoder.decode(Yh, **kwargs)

                decoded_predictions.extend(decoded_prediction)

            ydf = pd.DataFrame({'prediction': decoded_predictions})

            if args.predict_proba and self.supports_proba:
                raw_predictions = np.array(all_probs).squeeze(axis=1)

                for idx, label in enumerate(rev_map.values()):
                    ydf[f'__mdb_proba_{label}'] = raw_predictions[:, idx]

            return ydf
