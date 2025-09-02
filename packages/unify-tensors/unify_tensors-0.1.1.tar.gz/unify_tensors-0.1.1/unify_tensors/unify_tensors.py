from typing import Optional, Union, Any
import torch


def unify_tensors(*args: Any, device: Optional[Union[str, torch.device, int]] = None):
    """
    Checks if a list of tensors and modules are on the same device. If not, attempts to move them
    to the target device. If moving to CUDA fails, it gracefully falls back to the CPU.

    Args:
        *args: A variable number of objects, each with a .to() method.
        device: Optional target device on which to move all objects. If None, uses the device of the first object.

    Returns:
        A tuple of the objects, all on the same device.
    """
    if not args:
        return ()

    # Get the first object with a .to() method to determine the target device
    first_object = next((obj for obj in args if hasattr(obj, 'to') and callable(getattr(obj, 'to'))), None)
    if first_object is None:
        return args

    # If a specific device is not provided, use the device of the first object.
    if device is None:
        try:
            target_device = first_object.device
        except AttributeError:
            # Handle modules and other objects that don't have a .device attribute
            target_device = "cuda" if torch.cuda.is_available() else "cpu"
    else:
        target_device = device

    # Check if all objects are already on the target device
    devices = set()
    for obj in args:
        if isinstance(obj, torch.Tensor):
            devices.add(obj.device)
        elif isinstance(obj, torch.nn.Module):
            # A module's device is determined by its parameters
            devices.add(next(obj.parameters()).device)

    if len(devices) <= 1 and str(target_device) in [str(d) for d in devices]:
        return args

    # If not all on the same device, attempt to unify
    try:
        unified_objects = []
        for obj in args:
            if hasattr(obj, 'to') and callable(getattr(obj, 'to')):
                unified_objects.append(obj.to(target_device))
            else:
                unified_objects.append(obj)
        return tuple(unified_objects)

    except (RuntimeError, torch.cuda.OutOfMemoryError) as e:
        print(f"Failed to move all objects to {target_device}. Moving to CPU instead.")

        # Fallback to CPU
        unified_objects = []
        for obj in args:
            if hasattr(obj, 'to') and callable(getattr(obj, 'to')):
                unified_objects.append(obj.to("cpu"))
            else:
                unified_objects.append(obj)
        return tuple(unified_objects)