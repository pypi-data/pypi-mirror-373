# Unify Tensors
Tiny package to implement a safety function that moves all the tensors passed to the same device. 
Useful when a part of a big model has been offloaded and there's a risk of a runtime error because of tensors on different devices.
## Installation

```bash
pip install unify-tensors
```

or, if you prefer to go directly through GitHub, clone the repository and install it manually:

```bash
git clone https://github.com/giacomoguiduzzi/unify-tensors.git
cd unify-tensors
pip install .
```

## Usage
The `unify_tensors` function takes any number of tensor arguments and moves them all to the device of the first tensor provided.
If you want to move them to a specific device, you can pass the `device` keyword argument.

```python
from unify_tensors import unify_tensors as unify_tensors
import torch
from torch import nn

# Example with Tensors
a = torch.randn(2, 2)
b = torch.randn(2, 2).to('cuda')
c = torch.randn(2, 2).to('cpu')

# Unifying tensors
a_unified, b_unified, c_unified = unify_tensors(a, b, c)

print(f"Tensors unified to: {a_unified.device}")

# Example with a Tensor and a Model
class MyModel(nn.Module):
    def __init__(self):
        super().__init__()
        self.param = nn.Parameter(torch.randn(1))

    def forward(self, x):
        return x * self.param

model = MyModel().to('cpu')
input_tensor = torch.randn(1).to('cuda')

# Unifying a tensor and a model
model_unified, input_unified = unify_tensors(model, input_tensor)

print(f"Model unified to: {next(model_unified.parameters()).device}")
print(f"Input tensor unified to: {input_unified.device}")

# Should print 'cpu' because we specified the device
print(a.device, b.device, c.device)
```

## License
This project is licensed under the MIT License.
See the [LICENSE](LICENSE) file for details.
