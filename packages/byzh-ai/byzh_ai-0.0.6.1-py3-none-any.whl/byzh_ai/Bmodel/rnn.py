import torch
import torch.nn as nn
from .study_rnn import Layers_RNN
class B_RNN(nn.Module):
    def __init__(self, num_classes, input_size, hidden_size, num_layers=1):
        '''

        :param num_classes: label有多少个类别
        :param input_size: C, 将被H替代
        :param hidden_size: H, 用于取代C
        :param num_layers: 多少层RNN
        '''
        super().__init__()
        # self.rnn = nn.RNN(
        #     input_size=input_size,
        #     hidden_size=hidden_size,
        #     num_layers=num_layers,
        #     batch_first=True
        # )
        self.rnn = Layers_RNN(
            input_size=input_size,
            hidden_size=hidden_size,
            num_layers=num_layers,
            batch_first=True
        )
        self.fc = nn.Linear(hidden_size, num_classes)

    def forward(self, x):  # x [B, L, C]
        x, h = self.rnn(x)
        # x [B, L, H]
        # h [num_layers, B, H]

        # 法一: 取最后一个时间步的输出作为整个序列的表示
        out = x[:, -1, :]  # out [B, H]

        # 法二: 取最后一层的 hidden state 作为整个序列的表示
        # out = h[-1]  # out [B, H]

        out = self.fc(out)  # out [B, num_classes]

        return out

    def init_weights(self):
        for name, param in self.rnn.named_parameters():
            if 'weight_ih' in name:
                nn.init.xavier_uniform_(param)
            elif 'weight_hh' in name:
                nn.init.orthogonal_(param)
            elif 'bias' in name:
                nn.init.constant_(param, 0)

        nn.init.kaiming_normal_(self.fc.weight, mode='fan_in', nonlinearity='relu')
        if self.fc.bias is not None:
            nn.init.constant_(self.fc.bias, 0)

if __name__ == '__main__':
    model = B_RNN(num_classes=11, input_size=2, hidden_size=512, num_layers=4)
    model.init_weights()
    x = torch.randn(64, 2, 128) # 输入形状 [batch_size, input_size, seq_len]
    y = model(x)
    print(y.shape)