from typing import Optional, Union, Any, List, Tuple
import torch
from .typing import Movable, TorchDevice


def unify_tensors(*args: Any, device: Optional[TorchDevice] = None) -> Union[Movable, Tuple]:
    """
    Checks if a list of objects with a .to() method are on the same device. If not, attempts to move them
    to the target device. If moving to CUDA fails, it gracefully falls back to the CPU.

    Args:
        *args: A variable number of objects. Only objects with a .to() method will be moved.
        device: Optional target device on which to move all objects. If None, uses the device of the first object.

    Returns:
        A tuple of the objects, all on the same device, in their original order.
    """
    if not args:
        return ()

    # Keep track of original objects and their "movability"
    objects_to_move: List[Movable] = []
    original_indices: List[int] = []
    has_to_method: List[bool] = []

    for i, obj in enumerate(args):
        can_move = hasattr(obj, 'to') and callable(getattr(obj, 'to'))
        has_to_method.append(can_move)
        if can_move:
            objects_to_move.append(obj)
            original_indices.append(i)

    if not objects_to_move:
        return args

    # If a specific device is not provided, use the device of the first movable object.
    if device is None:
        try:
            target_device = objects_to_move[0].device
        except AttributeError:
            target_device = "cuda" if torch.cuda.is_available() else "cpu"
    else:
        target_device = device

    # Check if all movable objects are already on the target device
    devices = {
        obj.device for obj in objects_to_move
        if isinstance(obj, torch.Tensor) or (
                    isinstance(obj, torch.nn.Module) and hasattr(next(obj.parameters(), None), 'device'))
    }

    if len(devices) <= 1 and str(target_device) in [str(d) for d in devices]:
        if len(args) == 1:
            return args[0]
        return args

    unified_movable_objects = []
    # If not all on the same device, attempt to unify
    try:
        for obj in objects_to_move:
            unified_movable_objects.append(obj.to(target_device))

    except (RuntimeError, torch.cuda.OutOfMemoryError):
        print(f"Failed to move all objects to {target_device}. Moving to CPU instead.")
        unified_movable_objects = [obj.to("cpu") for obj in objects_to_move]

    # Reassemble the final tuple with all original objects and the moved ones
    final_result = list(args)
    for i, unified_obj in zip(original_indices, unified_movable_objects):
        final_result[i] = unified_obj

    if len(args) == 1:
        return final_result[0]
    return tuple(final_result)
