from typing import Optional, Union
import torch


def unify_tensors(*tensors: tuple[torch.Tensor], device: Optional[Union[str, torch.device, int]] = None):
    """
    Checks if a list of tensors are on the same device. If not, attempts to move them
    to CUDA. If that fails (e.g., due to OOM), moves them to the CPU.

    Args:
        *tensors: A variable number of torch tensors. Non-tensor objects are ignored.
        device: Optional target device on which to move all tensors. If None, uses the device of the first tensor.

    Returns:
        A tuple of the tensors, all on the same device.
    """
    if not tensors:
        return ()

    # Get the first tensor to determine the target device and filter out non-tensors
    first_tensor = next((t for t in tensors if isinstance(t, torch.Tensor)), None)
    if first_tensor is None:
        return tensors

    target_device = first_tensor.device if device is None else device

    # Check if all tensors are on the same device
    devices = {t.device for t in tensors if isinstance(t, torch.Tensor)}

    if len(devices) <= 1 and target_device in devices:
        return tensors

    # If not all on the same device or target device, try to unify to CUDA (if CPU wasn't explicitly requested)
    if str(target_device) != 'cpu' and torch.cuda.is_available():
        try:
            unified_tensors = []
            for t in tensors:
                if isinstance(t, torch.Tensor):
                    unified_tensors.append(t.to("cuda"))
                else:
                    unified_tensors.append(t)
            return tuple(unified_tensors)

        except torch.cuda.OutOfMemoryError:
            print("CUDA out of memory. Moving tensors to CPU.")
            # Fall through to the CPU section below

    # If CUDA is not available, it failed, or the CPU was explicitly requested, unify to CPU
    unified_tensors = []
    for t in tensors:
        if isinstance(t, torch.Tensor):
            unified_tensors.append(t.to("cpu"))
        else:
            unified_tensors.append(t)

    return tuple(unified_tensors)
