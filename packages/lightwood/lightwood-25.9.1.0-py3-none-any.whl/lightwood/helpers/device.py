import torch
import os
from random import randint
from torch.cuda import device_count, get_device_capability


def is_cuda_compatible():
    """
    Check if the system has CUDA-compatible devices with the required architecture and
    compiled CUDA version.

    This function checks the compatibility of CUDA devices available on the system by
    comparing their architectures and the compiled CUDA version. It iterates through
    the available devices and verifies if their architectures meet the minimum
    requirement specified by the function, and also checks if the compiled CUDA
    version is greater than a specific version.

    Returns:
        bool: True if there are compatible CUDA devices, otherwise False.

    Example:
        >>> is_compatible = is_cuda_compatible()
        >>> print(is_compatible)
        True
    """
    compatible_device_count = 0
    if torch.version.cuda is not None:
        for d in range(device_count()):
            capability = get_device_capability(d)
            major = capability[0]
            minor = capability[1]
            current_arch = major * 10 + minor
            min_arch = min((int(arch.split("_")[1]) for arch in torch.cuda.get_arch_list()), default=35)
            if (not current_arch < min_arch
                    and not torch._C._cuda_getCompiledVersion() <= 9000):
                compatible_device_count += 1

    if compatible_device_count > 0:
        return True
    return False


def get_devices():
    """
    Get the appropriate Torch device(s) based on CUDA availability and compatibility.

    This function determines the appropriate Torch device(s) to be used for
    computations based on the availability of CUDA and compatible devices. It checks
    if CUDA is available and if the available CUDA devices are compatible according to
    the 'is_cuda_compatible()' function. If compatible devices are found, the function
    selects either the first available CUDA device or a randomly selected one based on
    the 'RANDOM_GPU' environment variable. If CUDA is not available or no compatible
    devices are found, the function returns the CPU device.

    Returns:
        Tuple: A tuple containing the selected Torch device and the number of available
        devices.
    Example:
        >>> device, num_devices = get_devices()
        >>> print(device)
        cuda:0
        >>> print(num_devices)
        1
    """
    if torch.cuda.is_available() and is_cuda_compatible():
        device_str = "cuda"
        available_devices = torch.cuda.device_count()

        if available_devices > 1:
            if os.environ.get('RANDOM_GPU', False) in ['1', 'true', 'True', True, 1]:
                device_str = 'cuda:' + str(randint(0, available_devices - 1))
                available_devices = 1
    else:
        device_str = "cpu"
        available_devices = 0

    return torch.device(device_str), available_devices


def get_device_from_name(device_name=''):
    """
    Get a Torch device based on the specified device name or default behavior.

    This function returns a Torch device based on the specified device name or the
    default behavior, which is to return the output of the 'get_devices()' function.

    Args:
        device_name (str, optional): Name of the device to use. Default is an empty
        string.
        
    Returns:
        torch.device: The selected Torch device.

    Example:
        >>> device = get_device_from_name('cuda:1')
        >>> print(device)
        cuda:1
    """ # noqa E501
    if(device_name != ''):
        device = torch.device(device_name)
    else:
        device, _ = get_devices()
    return device
