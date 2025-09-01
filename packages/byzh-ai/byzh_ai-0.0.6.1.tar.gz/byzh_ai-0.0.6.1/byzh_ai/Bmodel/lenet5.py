import torch
import torch.nn as nn
import torch.nn.functional as F

class B_Lenet5(nn.Module):
    def __init__(self, num_classes, interpolate=True):
        super().__init__()

        self.interpolate = interpolate

        # [b, 6, 32, 32]
        self.layer1 = nn.Sequential(
            nn.Conv2d(1, 6, kernel_size=5, stride=1, padding=0),
            nn.BatchNorm2d(6),
            nn.ReLU(),
        )
        # [b, 6, 28, 28]
        self.subsample1 = nn.MaxPool2d(kernel_size=2, stride=2)  # 下采样
        # [b, 6, 14, 14]
        self.layer2 = nn.Sequential(
            nn.Conv2d(6, 16, kernel_size=5, stride=1, padding=0),
            nn.BatchNorm2d(16),
            nn.ReLU(),
        )
        # [b, 16, 10, 10]
        self.subsample2 = nn.MaxPool2d(kernel_size=2, stride=2)  # 下采样
        # [b, 16, 5, 5]

        # 全连接
        self.L1 = nn.Linear(400, 120)
        self.relu = nn.ReLU()
        self.L2 = nn.Linear(120, 84)
        self.relu1 = nn.ReLU()
        self.L3 = nn.Linear(84, num_classes)

    def forward(self, x):
        if self.interpolate:
            x = F.interpolate(x, size=(32, 32), mode='bilinear', align_corners=False)

        x = self.layer1(x)
        x = self.subsample1(x)
        x = self.layer2(x)
        x = self.subsample2(x)
        # 将上一步输出的16个5×5特征图中的400个像素展平成一维向量，以便下一步全连接
        x = x.reshape(x.size(0), -1)
        # 全连接
        x = self.L1(x)
        x = self.relu(x)
        x = self.L2(x)
        x = self.relu1(x)
        x = self.L3(x)
        return x

    def init_weights(self):
        for m in self.modules():
            if isinstance(m, nn.Conv2d):
                # fan_out模式会根据输出通道的数量来计算标准差
                nn.init.kaiming_normal_(m.weight, mode='fan_out', nonlinearity='relu')
            elif isinstance(m, nn.Linear):
                nn.init.kaiming_normal_(m.weight, mode='fan_in', nonlinearity='relu')
                if m.bias is not None: # 当bias=False时，bias=None
                    nn.init.constant_(m.bias, 0)


if __name__ == '__main__':
    net = B_Lenet5(2)
    a = torch.randn(50, 1, 32, 33)
    result = net(a)
    print(result.shape)