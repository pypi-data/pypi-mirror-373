# Unify Tensors
Tiny package to implement a safety function that moves all the tensors passed to the same device. 
Useful when a part of a big model has been offloaded and there's a risk of a runtime error because of tensors on different devices.
## Installation

```bash
pip install unify-tensors
```

or, if not available on PyPI, clone the repository and install it manually:

```bash
git clone https://github.com/giacomoguiduzzi/unify-tensors.git
cd unify-tensors
pip install .
```

## Usage
The `unify_tensors` function takes any number of tensor arguments and moves them all to the device of the first tensor provided.
If you want to move them to a specific device, you can pass the `device` keyword argument.

```python
from unify_tensors import unify_tensors
import torch

a = torch.randn(2, 2)
b = torch.randn(2, 2).to('cuda')
c = torch.randn(2, 2).to('cpu')

a, b, c = unify_tensors(a, b, c)

# Should print 'cpu' because the first tensor is on CPU
print(a.device, b.device, c.device)

a = a.to('cuda')
a, b, c = unify_tensors(a, b, c)

# Should print 'cuda' because the first tensor is on CUDA
print(a.device, b.device, c.device)

# You can also specify a device explicitly
a, b, c = unify_tensors(a, b, c, device='cpu')

# Should print 'cpu' because we specified the device
print(a.device, b.device, c.device)
```

## License
This project is licensed under the MIT License.
See the [LICENSE](LICENSE) file for details.
