import torch
import torch.nn as nn
from functorch.compile import aot_module, make_boxed_func
from .ops_tool import _IGNORED_OPS, _PYTHON_IGNORED_OPS, _SUPPORTED_OPS
from typing import Dict, List, Union
from warnings import warn

class FlopsAnalyzer():
    def __init__(self, model:nn.Module, input_example:Union[Dict, List], device="cuda:0", ignore_unknown_ops=True) -> None:
        self.model = model
        self.input_example = input_example
        self.device = device
        self.model.to(self.device)

        if isinstance(self.input_example, Dict):
            self.input_example = {k:v.to(self.device) if isinstance(v, torch.Tensor) else v for k, v in self.input_example.items()}
        elif isinstance(self.input_example, List):
            self.input_example = [v.to(self.device) if isinstance(v, torch.Tensor) else v for v in self.input_example]
        else:
            raise f"'input_example should be 'Dict' or 'List'!!!"
        self.FLOPs_fw = 0
        self.FLOPs_bw = 0

        self.ignore_unknown_ops = ignore_unknown_ops
        if self.ignore_unknown_ops:
            self.ignored_ops = set()

    def analyze(self, loss_fn=None, loss_fun_input:List=None):
        
        FLOPs = {}
        model = aot_module(self.model, fw_compiler=self.compiler_fn_fw, bw_compiler=self.compiler_fn_bw)
        if isinstance(self.input_example, Dict):
            output = model(**self.input_example)
        else:
            output = model(*self.input_example)
        FLOPs['Forward: '] = self.FLOPs_fw
        if loss_fn is not None:
            assert loss_fun_input is not None, "If 'loss_fn' is provided, 'loss_fun_input' must be provided."
            if not isinstance(loss_fun_input, List):
                loss_fun_input = [loss_fun_input]
            loss = loss_fn(*loss_fun_input, output)
            loss.backward()
            FLOPs['Backward: '] = self.FLOPs_bw
        
        FLOPs['TOTAL: '] = self.FLOPs_bw + self.FLOPs_fw

        print('*' * 40)
        for name, v in FLOPs.items():
            print(f"{name} {v} FLOPs, {v/1e9 :.6f} GFLOPs.")
        
        print('*' * 40)
        if len(self.ignored_ops):
            print(f"Following operators are ignored: {self.ignored_ops}")
        

        
    def compiler_fn_fw(self, fx_module: torch.fx.GraphModule, _):
        call_function_ops = set()
        call_method_ops = set()
        call_module_ops = set()

        call_function_nodes = []
        call_method_nodes = []
        call_module_nodes = []

        for node in fx_module.graph.nodes:
            

            if node.target in _IGNORED_OPS:
                # print(f"Ignoring node: {node.name} with target {node.target} and op {node.op}")
                continue

            if node.target in _PYTHON_IGNORED_OPS:
                # print(f"Ignoring node: {node.name} with target {node.target} and op {node.op}")
                continue
            
            if node.op == 'call_function':
                if node.target._name in _IGNORED_OPS:
                    continue
                call_function_ops.add(node.target._name)
                call_function_nodes.append(node)

                try:
                    flops = _SUPPORTED_OPS[node.target._name](node.args)
                except Exception as e:
                    if self.ignore_unknown_ops:
                        warn(f"Ignored operator: {node.name}")
                        flops = 0
                        self.ignored_ops.add(node.name)
                    else:
                        raise e
                self.FLOPs_fw = self.FLOPs_fw + flops

            elif node.op == 'call_method':
                if node.target._name in _IGNORED_OPS:
                    continue
                call_method_ops.add(node.target._name)
                call_method_nodes.append(node)
                flops = _SUPPORTED_OPS[node.target._name](node.args)
                self.FLOPs_fw = self.FLOPs_fw + flops
            elif node.op == 'call_module':
                if node.target._name in _IGNORED_OPS:
                    continue
                call_module_ops.add(node.target._name)
                call_module_nodes.append(node)
                flops = _SUPPORTED_OPS[node.target._name](node.args)
                self.FLOPs_fw = self.FLOPs_fw + flops
            elif node.op == 'placeholder':
                pass
            elif node.op == 'get_attr':
                pass
            elif node.op == 'output':
                pass
            else:
                warn(f"!!! Unknown operation: {node.op} with target {node.target}. We ignore it !!!")
        # print(fx_module.code)
        return make_boxed_func(fx_module.forward)
        
    def compiler_fn_bw(self, fx_module: torch.fx.GraphModule, _):
        call_function_ops = set()
        call_method_ops = set()
        call_module_ops = set()

        call_function_nodes = []
        call_method_nodes = []
        call_module_nodes = []

        for node in fx_module.graph.nodes:

            if node.target in _IGNORED_OPS:
                # print(f"Ignoring node: {node.name} with target {node.target} and op {node.op}")
                continue

            if node.target in _PYTHON_IGNORED_OPS:
                # print(f"Ignoring node: {node.name} with target {node.target} and op {node.op}")
                continue
            
            if node.op == 'call_function':
                if node.target._name in _IGNORED_OPS:
                    continue
                call_function_ops.add(node.target._name)
                call_function_nodes.append(node)

                try:
                    flops = _SUPPORTED_OPS[node.target._name](node.args)
                except Exception as e:
                    if self.ignore_unknown_ops:
                        warn(f"Ignored operator: {node.name}")
                        flops = 0
                        self.ignored_ops.add(node.name)
                    else:
                        raise e
                self.FLOPs_bw = self.FLOPs_bw + flops

            elif node.op == 'call_method':
                if node.target._name in _IGNORED_OPS:
                    continue
                call_method_ops.add(node.target._name)
                call_method_nodes.append(node)
                flops = _SUPPORTED_OPS[node.target._name](node.args)
                self.FLOPs_bw = self.FLOPs_bw + flops
            elif node.op == 'call_module':
                if node.target._name in _IGNORED_OPS:
                    continue
                call_module_ops.add(node.target._name)
                call_module_nodes.append(node)
                flops = _SUPPORTED_OPS[node.target._name](node.args)
                self.FLOPs_bw = self.FLOPs_bw + flops
            elif node.op == 'placeholder':
                pass
            elif node.op == 'get_attr':
                pass
            elif node.op == 'output':
                pass
            else:
                warn(f"!!! Unknown operation: {node.op} with target {node.target}. We ignore it !!!")
        # print(fx_module.code)
        return make_boxed_func(fx_module.forward)
    

if __name__ == "__main__":

    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--linear_no_bias", action='store_true')
    parser.add_argument("--add_one", action='store_true')
    inp_args = parser.parse_args()

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
    model.train()
    for n, p in model.named_parameters():
        p.requires_grad_(True)
    x = torch.randn(16, 50, requires_grad=True).cuda()
    def loss_fn(y_pred, y_true):
        result = (y_pred - y_true).pow(2).mean()
        return result
    flops_analyzer = FlopsAnalyzer(model, {'x':x})
    flops_analyzer.analyze(loss_fn=loss_fn, loss_fun_input=[torch.randn(16, 4).cuda()])