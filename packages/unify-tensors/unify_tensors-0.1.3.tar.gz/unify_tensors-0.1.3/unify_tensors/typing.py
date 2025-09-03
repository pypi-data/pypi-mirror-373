from typing import TypeVar, Protocol
import torch

class TorchDevice(Protocol):
    ...

class Movable(Protocol):
    def __init__(self):
        self.device = None

    def to(self, device: TorchDevice) -> "Movable":
        ...

MovableType = TypeVar("MovableType", bound=Movable)
TorchDeviceType = TypeVar("TorchDeviceType", str, torch.device, int)