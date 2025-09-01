import torch
import torch.nn as nn
import torch.nn.functional as F
from .liquidneuron import LiquidNeuron

class LiquidNeuralNetwork(nn.Module):
    def __init__(self, input_size: int, hidden_size: int, tau: float = 0.5,
                 scaling_factor_W: float = 0.05, scaling_factor_U: float = 0.05,
                 scaling_factor_alpha: float = 0.05, num_layers: int = 1):
        super().__init__()
        self.num_layers = num_layers
        self.layers = nn.ModuleList([
            LiquidNeuron(
                input_size if i == 0 else hidden_size,
                hidden_size,
                tau=tau,
                scaling_factor_W=scaling_factor_W,
                scaling_factor_U=scaling_factor_U,
                scaling_factor_alpha=scaling_factor_alpha
            ) for i in range(num_layers)
        ])

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        x: (batch, seq_len, input_size)
        returns: (batch, hidden_size) -> last hidden layer output
        """
        h_list = [None] * self.num_layers

        for t in range(x.size(1)):
            x_t = x[:, t, :]
            for l, layer in enumerate(self.layers):
                h_list[l] = layer(x_t, h_list[l])
                x_t = h_list[l]  # pass output to next layer

        return h_list[-1]



class LTCLayer(nn.Module):
    def __init__(self, input_size, hidden_size,num_layers):
        super().__init__()
        self.hidden_size = hidden_size
        self.fc_in = nn.Linear(input_size, hidden_size)
        self.fc_rec = nn.Linear(hidden_size, hidden_size)

        # Learnable time constants (tau), one per neuron
        self.tau = nn.Parameter(torch.ones(hidden_size) * 0.5)
        self.num_layers=num_layers
    def forward(self, x):
        h = torch.zeros(x.size(0), self.hidden_size).to(x.device)
        dt = 0.1  # timestep
        tau=torch.clamp(self.tau,min=0.1,max=5.0)
        for t in range(x.size(1)):
            for _ in range(self.num_layers):
              activation = torch.tanh(self.fc_in(x[:, t, :]) + self.fc_rec(h))
              # LTC update rule
              h = h + (dt /tau) * (activation - h)
        return h


class LiquidCNN(nn.Module):
    def __init__(self, input_channels, hidden_size ,num_layers_liq,num_layers_conv=1):
        super().__init__()
        self.hidden_size = hidden_size
        self.hidden_channels=input_channels*4
        self.num_layers_liq=num_layers_liq
        self.num_layers_conv=num_layers_conv
        self.conv1=nn.Conv2d(input_channels,(input_channels*4),kernel_size=1,stride=1)
        self.convlayer=nn.Conv2d((input_channels*4),(input_channels*4),kernel_size=1,stride=1)
        self.convend=nn.Conv2d((input_channels*4),1,kernel_size=1,stride=1)
        self.fc_in = nn.LazyLinear(hidden_size)
        self.fc_rec = nn.Linear(hidden_size, hidden_size)

        # Learnable time constants (tau), one per neuron
        self.tau = nn.Parameter(torch.ones(hidden_size) * 0.5)
        self.num_layers=num_layers_liq
    def forward(self, x):
        x=self.conv1(x)
        for _ in range(self.num_layers_conv):
          x=self.convlayer(x)
        x=self.convend(x)
        x=x.squeeze(1)
        h = torch.zeros(x.size(0), self.hidden_size).to(x.device)
        dt = 0.1  # timestep
        tau=torch.clamp(self.tau,min=0.1,max=5.0)
        for t in range(x.size(1)):
            for _ in range(self.num_layers_liq):
              activation = torch.tanh(self.fc_in(x[:, t, :]) + self.fc_rec(h))
              # LTC update rule
              h = h + (dt /tau) * (activation - h)
        return h
    


class LiquidRNN(nn.Module):
    def __init__(self, input_size, hidden_size ,num_layers_liq=1,num_layers_rnn=1):
        super().__init__()
        self.hidden_size = hidden_size
        self.num_layers_liq=num_layers_liq
        self.rnn=nn.RNN(input_size,hidden_size,num_layers_rnn)
        
        self.fc_in = nn.Linear(hidden_size, hidden_size)
        self.fc_rec = nn.Linear(hidden_size, hidden_size)

        # Learnable time constants (tau), one per neuron
        self.tau = nn.Parameter(torch.ones(hidden_size) * 0.5)
        self.num_layers=num_layers_liq
    def forward(self, x):
        x,_=self.rnn(x)
        h = torch.zeros(x.size(0), self.hidden_size).to(x.device)
        dt = 0.1  # timestep
        tau=torch.clamp(self.tau,min=0.1,max=5.0)
        for t in range(x.size(1)):
            for _ in range(self.num_layers_liq):
              activation = torch.tanh(self.fc_in(x[:, t, :]) + self.fc_rec(h))
              # LTC update rule
              h = h + (dt /tau) * (activation - h)
        return h
    



class LiquidLSTM(nn.Module):
    def __init__(self, input_size, hidden_size ,num_layers_liq=1,num_layers_lstm=1,batch_first=True,bidirectional=True):
        super().__init__()
        self.hidden_size = hidden_size
        self.num_layers_liq=num_layers_liq
        self.rnn=nn.LSTM(input_size,hidden_size,num_layers_lstm,batch_first,bidirectional)
        
        self.fc_in = nn.Linear(hidden_size, hidden_size)
        self.fc_rec = nn.Linear(hidden_size, hidden_size)

        # Learnable time constants (tau), one per neuron
        self.tau = nn.Parameter(torch.ones(hidden_size) * 0.5)
        self.num_layers=num_layers_liq
    def forward(self, x):
        x,_=self.rnn(x)
        h = torch.zeros(x.size(0), self.hidden_size).to(x.device)
        dt = 0.1  # timestep
        tau=torch.clamp(self.tau,min=0.1,max=5.0)
        for t in range(x.size(1)):
            for _ in range(self.num_layers_liq):
              activation = torch.tanh(self.fc_in(x[:, t, :]) + self.fc_rec(h))
              # LTC update rule
              h = h + (dt /tau) * (activation - h)
        return h
    




class HeightBlock(nn.Module):
  def __init__(self,input_dim,hidden_dim,height):
    super().__init__()
    self.fc=nn.Linear(input_dim,hidden_dim)
    self.feedback=nn.Linear(hidden_dim,hidden_dim)
    self.height=height
  def forward(self,x):
    h=F.relu(self.fc(x))
    for _ in range(self.height):
      h=F.relu(self.feedback(h)+h)
    return h



class HDNN(nn.Module):
  def __init__(self,input_dim,hidden_dim,output_dim,height,depth):
    super().__init__()
    self.blocks=nn.ModuleList([HeightBlock(input_dim if i==0 else hidden_dim,hidden_dim,height) for i in range(depth)])
    self.classifier=nn.Linear(hidden_dim,output_dim)
  def forward(self,x):
    h=x
    for block in self.blocks:
      h=F.relu(block(h))
    h=self.classifier(h)
    return h