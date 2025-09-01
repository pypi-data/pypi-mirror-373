import torch
import torch.nn as nn
import torch.nn.functional as F
import math
from spikingjelly.activation_based import surrogate, layer

class OneLayer_RNN(nn.Module):
    '''
    input_size: C
    seq_len: L
    hidden_size: H
    num_layers: N
    '''
    def __init__(self, input_size, hidden_size):
        super().__init__()
        self.input_size = input_size
        self.hidden_size = hidden_size

        self.W_ih = nn.Parameter(torch.randn(input_size, hidden_size)) # [C, H]
        self.W_hh = nn.Parameter(torch.randn(hidden_size, hidden_size)) # [H, H]
        self.b = nn.Parameter(torch.zeros(hidden_size)) # [H]

    def forward(self, x, state=None):
        # x: [L, B, C]
        seq_len, batch_size, input_size = x.shape

        # h: [B, H]
        if state is None:
            state = torch.zeros(batch_size, self.hidden_size).to(x)

        outputs = []
        for t in range(seq_len):
            x_t = x[t] # [B, C]
            state = torch.tanh(x_t @ self.W_ih + state @ self.W_hh + self.b) # self.b会被广播成[B, H]
            outputs.append(state)

        return torch.stack(outputs, dim=0), state # [L, B, H], [B, H]


class Layers_RNN(nn.Module):
    '''
    input_size: C
    seq_len: L
    hidden_size: H
    num_layers: N
    '''
    def __init__(self, input_size, hidden_size, num_layers=1, batch_first=False):
        '''
        如果batch_first=False, 输入的x的形状为[L, B, C]

        如果batch_first=True, 输入的x的形状为[B, L, C]
        '''
        super().__init__()
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        self.batch_first = batch_first


        self.W_ih_list = nn.ModuleList() # [C, H], [H, H], [H, H], ...
        self.W_hh_list = nn.ModuleList() # [H, H], [H, H], [H, H], ...
        self.b_list = nn.ParameterList() # H, H, H, ......

        for layer in range(num_layers):
            in_size = input_size if layer == 0 else hidden_size # C, H, H, ......
            self.W_ih_list.append(nn.Linear(in_size, hidden_size, bias=False))
            self.W_hh_list.append(nn.Linear(hidden_size, hidden_size, bias=False))
            self.b_list.append(nn.Parameter(torch.zeros(hidden_size)))

    def forward(self, x, state=None):
        '''

        :param x:
        :param state: [L, B, H]
        :return: x, h <-> [L, B, H], [L, B, H]
        '''
        if self.batch_first:
            x = x.transpose(0, 1) # [B, L, C] -> [L, B, C]

        # x: [L, B, C]
        seq_len, batch_size, input_size = x.size()

        # state: [N, B, H]
        if state is None:
            state = torch.zeros(self.num_layers, batch_size, self.hidden_size, device=x.device).to(x)

        layer_input = x # 第一次为[L, B, C], 后续变为[L, B, H]
        for layer in range(self.num_layers):
            outputs = []
            # clone避免in_place操作 -> 导致报错
            h = state[layer].clone()

            for t in range(seq_len):
                x_t = layer_input[t] # `for layer`第一次为[B, C], 后续变为[B, H]
                h = torch.tanh(
                    self.W_ih_list[layer](x_t)
                    + self.W_hh_list[layer](h)
                    + self.b_list[layer]
                )
                outputs.append(h)

            layer_input = torch.stack(outputs, dim=0)
            state[layer] = h

        if self.batch_first:
            layer_input = layer_input.transpose(0, 1) # [L, B, H] -> [B, L, H]
        return layer_input, state # [L, B, H], [N, B, H]

class Spike_RNN(nn.Module):
    '''
    input_size: C
    seq_len: L/T
    hidden_size: H
    num_layers: N
    '''
    def __init__(self, input_size, hidden_size, num_layers=1, batch_first=False,
                 surrogate_function=surrogate.Erf()):
        '''
        如果batch_first=False, 输入的x的形状为[L, B, C]

        如果batch_first=True, 输入的x的形状为[B, L, C]
        '''
        super().__init__()
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        self.batch_first = batch_first
        self.surrogate_function = surrogate_function


        self.W_ih_list = nn.ModuleList() # [C, H], [H, H], [H, H], ...
        self.W_hh_list = nn.ModuleList() # [H, H], [H, H], [H, H], ...
        self.b_list = nn.ParameterList() # H, H, H, ......

        for layer in range(num_layers):
            in_size = input_size if layer == 0 else hidden_size # C, H, H, ......
            self.W_ih_list.append(nn.Linear(in_size, hidden_size, bias=False))
            self.W_hh_list.append(nn.Linear(hidden_size, hidden_size, bias=False))
            self.b_list.append(nn.Parameter(torch.zeros(hidden_size)))

        self.reset_parameters()

    def forward(self, x, state=None):
        '''

        :param x:
        :param state: [L, B, H]
        :return: x, h <-> [L, B, H], [L, B, H]
        '''
        if self.batch_first:
            x = x.transpose(0, 1) # [B, L, C] -> [L, B, C]

        # x: [L, B, C]
        seq_len, batch_size, input_size = x.size()

        # state: [N, B, H]
        if state is None:
            state = torch.zeros(self.num_layers, batch_size, self.hidden_size, device=x.device).to(x)

        layer_input = x # 第一次为[L, B, C], 后续变为[L, B, H]
        for layer in range(self.num_layers):
            outputs = [] # 替换x ->
            # clone避免in_place操作 -> 导致报错
            h = state[layer].clone() # 替换state ->

            for t in range(seq_len):
                x_t = layer_input[t] # `for layer`第一次为[B, C], 后续变为[B, H]
                h = self.surrogate_function(
                    self.W_ih_list[layer](x_t)
                    + self.W_hh_list[layer](h)
                    + self.b_list[layer]
                )
                outputs.append(h)

            layer_input = torch.stack(outputs, dim=0) # -> 替换x
            state[layer] = h # -> 替换state

        if self.batch_first:
            layer_input = layer_input.transpose(0, 1) # [L, B, H] -> [B, L, H]
        return layer_input, state # [L, B, H], [N, B, H]

    def reset_parameters(self):
        '''
        初始化所有可学习参数。
        '''
        sqrt_k = math.sqrt(1 / self.hidden_size) # 标准差缩放因子
        for param in self.parameters():
            nn.init.uniform_(param, -sqrt_k, sqrt_k) # 均匀分布 -> 区间 [-sqrt_k, sqrt_k]



if __name__ == '__main__':
    seq_len, batch_size, input_size, hidden_size, num_layers = 7, 4, 8, 16, 3
    x = torch.randn(seq_len, batch_size, input_size)

    # OneLayer_RNN
    rnn = OneLayer_RNN(input_size, hidden_size)
    rnn_out, h_n = rnn(x)
    print("OneLayer_RNN output:", rnn_out.shape, h_n.shape)  # [seq_len, batch, hidden_size]

    # Layers_RNN
    rnn = Layers_RNN(input_size, hidden_size, num_layers)
    rnn_out, h_n = rnn(x)
    print("Layers_RNN output:", rnn_out.shape, h_n.shape)  # [seq_len, batch, hidden_size]

    # Spike_RNN
    rnn = Spike_RNN(input_size, hidden_size)
    rnn_out, h_n = rnn(x)
    print("Spike_RNN output:", rnn_out.shape, h_n.shape)  # [T, batch, hidden_size]