import torch
import torch.nn as nn

class LiquidNeuron(nn.Module):
    def __init__(self, input_size: int, hidden_size: int, tau: float = 0.5,
                 scaling_factor_W: float = 0.05, scaling_factor_U: float = 0.05,
                 scaling_factor_alpha: float = 0.05):
        super().__init__()
        self.hidden_size = hidden_size
        self.tau = tau
        
        self.W = nn.Parameter(torch.randn(hidden_size, hidden_size) * scaling_factor_W)
        self.U = nn.Parameter(torch.randn(hidden_size, input_size) * scaling_factor_U)
        self.alpha = nn.Parameter(torch.randn(hidden_size, hidden_size) * scaling_factor_alpha)
        self.bias = nn.Parameter(torch.randn(hidden_size))
        self.activation = torch.tanh

    def forward(self, x: torch.Tensor, h: torch.Tensor = None) -> torch.Tensor:
        if h is None:
            h = torch.zeros(x.size(0), self.hidden_size).to(x.device)
        
        dh = (-h + self.activation(
            torch.matmul(h, self.W.T) +
            torch.matmul(x, self.U.T) +
            torch.matmul(h, self.alpha.T) +
            self.bias
        )) * self.tau
        h = h + dh
        return h
