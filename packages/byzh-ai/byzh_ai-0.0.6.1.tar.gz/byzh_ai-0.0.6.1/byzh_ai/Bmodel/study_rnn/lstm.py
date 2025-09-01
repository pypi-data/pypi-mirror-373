import torch
import torch.nn as nn
import torch.nn.functional as F
import math
from spikingjelly.activation_based import surrogate, layer

class OneLayer_LSTM(nn.Module):
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

        # Input to hidden
        self.W_ih = nn.Parameter(torch.randn(input_size, 4 * hidden_size)) # [C, 4H]
        # Hidden to hidden
        self.W_hh = nn.Parameter(torch.randn(hidden_size, 4 * hidden_size)) # [H, 4H]
        self.b = nn.Parameter(torch.zeros(4 * hidden_size)) # [4H]

    def forward(self, x, state=None):
        # x: [L, B, C]
        seq_len, batch_size, input_size = x.shape

        # h: [B, H]
        # c: [B, H]
        if state is None:
            state_h = torch.zeros(batch_size, self.hidden_size).to(x)
            state_c = torch.zeros(batch_size, self.hidden_size).to(x)
        else:
            state_h, state_c = state

        outputs = []
        for t in range(seq_len):
            x_t = x[t] # [B, C]
            gates = x_t @ self.W_ih + state_h @ self.W_hh + self.b # [B, 4H]

            # .chunk将张量沿着指定维度分割成多个相等大小的块, 需要制定块数
            i, f, g, o = gates.chunk(4, dim=1) # i, f, g, o: [B, H]

            i = torch.sigmoid(i) # 输入门(input gate)
            f = torch.sigmoid(f) # 遗忘门(forget gate)
            g = torch.tanh(g)    # 候选记忆(cell gate)
            o = torch.sigmoid(o) # 输出门(output gate)

            state_c = f * state_c + i * g # [B, H]
            state_h = o * torch.tanh(state_c) # [B, H]

            outputs.append(state_h)

        return torch.stack(outputs, dim=0), (state_h, state_c)



class Layers_LSTM(nn.Module):
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

        self.W_ih_list = nn.ModuleList() # [C, 4H], [H, 4H], [H, 4H], ...
        self.W_hh_list = nn.ModuleList() # [H, 4H], [H, 4H], [H, 4H], ...
        self.b_list = nn.ParameterList() # 4H, 4H, 4H, ......
        for layer in range(num_layers):
            in_size = input_size if layer == 0 else hidden_size
            self.W_ih_list.append(nn.Linear(in_size, 4 * hidden_size, bias=False))
            self.W_hh_list.append(nn.Linear(hidden_size, 4 * hidden_size, bias=False))
            self.b_list.append(nn.Parameter(torch.zeros(4 * hidden_size)))

    def forward(self, x, state=None):
        '''
        h: 隐藏状态

        c: 细胞状态
        :param x:
        :param state: ([L, B, H], [L, B, H])
        :return: x, (h, c) <-> [L, B, H], ([L, B, H], [L, B, H])
        '''
        if self.batch_first:
            x = x.transpose(0, 1) # [B, L, C] -> [L, B, C]

        # x: [L, B, C]
        seq_len, batch_size, input_size = x.size()

        # state_h: [N, B, H]
        # state_c: [N, B, H]
        if state is None:
            state_h = torch.zeros(self.num_layers, batch_size, self.hidden_size).to(x)
            state_c = torch.zeros(self.num_layers, batch_size, self.hidden_size).to(x)

        layer_input = x
        for layer in range(self.num_layers):
            outputs = []
            # clone避免in_place操作 -> 导致报错
            h = state_h[layer].clone() # [B, H]
            c = state_c[layer].clone() # [B, H]
            for t in range(seq_len):
                x_t = layer_input[t] # [B, C]
                gates = (
                    self.W_ih_list[layer](x_t) # [B, C] * [C, 4H] -> [B, 4H]
                    + self.W_hh_list[layer](h) # [B, H] * [H, 4H] -> [B, 4H]
                    + self.b_list[layer] # 4H -> [B, 4H]
                )
                i, f, g, o = gates.chunk(4, dim=1) # i, f, g, o: [B, H]

                i = torch.sigmoid(i) # 输入门(input gate)
                f = torch.sigmoid(f) # 遗忘门(forget gate)
                g = torch.tanh(g)    # 候选记忆(cell gate)
                o = torch.sigmoid(o) # 输出门(output gate)

                c = f * c + i * g     # [B, H]
                h = o * torch.tanh(c) # [B, H]

                outputs.append(h)
            layer_input = torch.stack(outputs, dim=0)
            # 更新状态h_t, c_t
            state_h[layer] = h
            state_c[layer] = c

        if self.batch_first:
            layer_input = layer_input.transpose(0, 1) # [L, B, H] -> [B, L, H]
        return layer_input, (state_h, state_c)


class Spike_LSTM(nn.Module):
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
        self.surrogate_function1 = surrogate_function
        self.surrogate_function2 = surrogate_function

        self.W_ih_list = nn.ModuleList() # [C, 4H], [H, 4H], [H, 4H], ...
        self.W_hh_list = nn.ModuleList() # [H, 4H], [H, 4H], [H, 4H], ...
        self.b_list = nn.ParameterList() # 4H, 4H, 4H, ......
        for layer in range(num_layers):
            in_size = input_size if layer == 0 else hidden_size
            self.W_ih_list.append(nn.Linear(in_size, 4 * hidden_size, bias=False))
            self.W_hh_list.append(nn.Linear(hidden_size, 4 * hidden_size, bias=False))
            self.b_list.append(nn.Parameter(torch.zeros(4 * hidden_size)))

        self.reset_parameters()
    def forward(self, x, state=None):
        '''
        h: 隐藏状态

        c: 细胞状态
        :param x:
        :param state: ([L, B, H], [L, B, H])
        :return: x, (h, c) <-> [L, B, H], ([L, B, H], [L, B, H])
        '''
        if self.batch_first:
            x = x.transpose(0, 1) # [B, L, C] -> [L, B, C]

        # x: [L, B, C]
        seq_len, batch_size, input_size = x.size()

        # state_h: [N, B, H]
        # state_c: [N, B, H]
        if state is None:
            state_h = torch.zeros(self.num_layers, batch_size, self.hidden_size).to(x)
            state_c = torch.zeros(self.num_layers, batch_size, self.hidden_size).to(x)

        layer_input = x
        for layer in range(self.num_layers):
            outputs = []
            # clone避免in_place操作 -> 导致报错
            h = state_h[layer].clone() # [B, H]
            c = state_c[layer].clone() # [B, H]
            for t in range(seq_len):
                x_t = layer_input[t] # [B, C]
                gates = (
                    self.W_ih_list[layer](x_t) # [B, C] * [C, 4H] -> [B, 4H]
                    + self.W_hh_list[layer](h) # [B, H] * [H, 4H] -> [B, 4H]
                    + self.b_list[layer] # 4H -> [B, 4H]
                )
                i, f, g, o = gates.chunk(4, dim=1) # i, f, g, o: [B, H]

                i = self.surrogate_function1(i) # 输入门(input gate)
                f = self.surrogate_function1(f) # 遗忘门(forget gate)
                g = self.surrogate_function2(g) # 候选记忆(cell gate)
                o = self.surrogate_function1(o) # 输出门(output gate)

                c = f * c + i * g     # [B, H]

                # todo
                with torch.no_grad():
                    torch.clamp_max_(c, 1.)
                h = o * c # [B, H]

                outputs.append(h)
            layer_input = torch.stack(outputs, dim=0)
            # 更新状态h_t, c_t
            state_h[layer] = h
            state_c[layer] = c

        if self.batch_first:
            layer_input = layer_input.transpose(0, 1) # [L, B, H] -> [B, L, H]
        return layer_input, (state_h, state_c)

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

    # OneLayer_LSTM
    lstm = OneLayer_LSTM(input_size, hidden_size)
    lstm_out, (h_n, c_n) = lstm(x)
    print("OneLayer_LSTM output:", lstm_out.shape, h_n.shape, c_n.shape)  # [seq_len, batch, hidden_size]

    # Layers_LSTM
    lstm = Layers_LSTM(input_size, hidden_size, num_layers)
    lstm_out, (h_n, c_n) = lstm(x)
    print("Layers_LSTM output:", lstm_out.shape, h_n.shape, c_n.shape)  # [seq_len, batch, hidden_size]

    # Spike_LSTM
    rnn = Spike_LSTM(input_size, hidden_size)
    rnn_out, (h_n, c_n) = rnn(x)
    print("Spike_LSTM output:", rnn_out.shape, h_n.shape, c_n.shape)  # [T, batch, hidden_size]