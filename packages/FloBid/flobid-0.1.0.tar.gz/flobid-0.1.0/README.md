# **`FloBid`** #
## Introduction ##

`FloBid` is capable of calculating both the **`Forward`** and **`Backward`** FLOPs (Floating-Point Operations) of a PyTorch model. The core concept involves utilizing `AOTAutograd` to capture the forward computation graph and the backward computation graph. Subsequently, it accumulates the FLOPs of each node within each graph.

## Requirements
- torch >=2.0.0
- python >=3.10.18
- numpy == 1.24.0

### Usage
## Installation
```
pip install setuptools wheel build
python -m build
pip install dist/flobid-0.1.0-py3-none-any.whl
```


### Example
```python
import torch
import torch.nn as nn
import argparse
from FloBid.FlopsCountEngine import FlopsAnalyzer

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--linear_no_bias", action='store_true')
    parser.add_argument("--add_one", action='store_true')
    inp_args = parser.parse_args()

    # 1. Define your Module.
    class SimpleModel(nn.Module):
        def __init__(self, args) -> None:
            super().__init__()
            self.layer = nn.Linear(50, 4, bias=not args.linear_no_bias)
            self.__add_one = args.add_one

        def forward(self, x: torch.Tensor):
            x = self.layer(x)
            if self.__add_one:
                x += 1.
            return x
    
    model = SimpleModel(inp_args).cuda()

    # 2. 
    model.train()
    for n, p in model.named_parameters():
        p.requires_grad_(True)
    x = torch.randn(16, 50, requires_grad=True).cuda()

    # 3. Define a loss function (Only for )
    def loss_fn(y_pred, y_true):
        result = (y_pred - y_true).pow(2).mean()
        return result

    flops_analyzer = FlopsAnalyzer(model, {'x':x})
    flops_analyzer.analyze(loss_fn=loss_fn, loss_fun_input=[torch.randn(16, 4).cuda()])
```
The output is:
```
****************************************
Forward:  6400 FLOPs
Backward:  11860 FLOPs
TOTAL:  18260 FLOPs
****************************************
```

## Supported Operators ##

```
_SUPPORTED_OPS: Dict[str, Callable] = {
    "aten::convolution": conv_ops_counter,
    'aten::div.Tensor': div_tesnor_ops_counter,
    'aten::addmm': addmm_ops_counter,
    'aten::sum.dim_IntList': sum_dim_IntList_ops_counter,
    'aten::sigmoid': sigmoid_ops_counter,
    'aten::_softmax': _soft_max_ops_counter,
    'aten::mm': mm_ops_counter,
    'aten::remainder.Scalar': remainder_Scalar_ops_counter,
    'aten::bmm': bmm_ops_counter,
    'aten::add.Tensor': add_Tensor_ops_counter,
    'aten::native_layer_norm': native_layer_norm_ops_conuter,
    'aten::mul.Tensor': mul_ops_counter, 
    'aten::mean.dim': mean_dim_ops_counter,
    'aten::gelu': gelu_ops_counter, 
    'aten::_native_batch_norm_legit_functional': _native_batch_norm_legit_functional_ops_counter,
    'aten::remainder.Tensor': remainder_Tensor_ops_counter,
    'aten::floor': floor_ops_counter,
    'aten::floor_divide': floor_divide_ops_counter,
    'aten::remainder': None,
    'aten::scatter_add': scatter_add_ops_counter,
    'aten::gelu_backward': gelu_backward_ops_counter,
    'aten::convolution_backward': convolution_backward_ops_counter,
    'aten::native_layer_norm_backward': native_layer_norm_backward_ops_counter,
    'aten::native_batch_norm_backward': native_batch_norm_backward_ops_counter,
    'aten::_softmax_backward_data': _softmax_backward_data_ops_counter,
    'aten::sigmoid_backward': sigmoid_backward_ops_counter,
}
```

## Limitations ##
It only supports several operators.