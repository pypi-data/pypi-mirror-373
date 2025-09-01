import torch
import torch.nn as nn
import argparse
from FloBid.FlopsCountEngine import FlopsAnalyzer

if __name__ == "__main__":
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