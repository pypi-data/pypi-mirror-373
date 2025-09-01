import torch
import torch.nn as nn
import torch.nn.functional as F
class B_SimpleCNN(nn.Module):
    def __init__(self, in_channels, num_classes, interpolate=True):
        super().__init__()

        self.interpolate = interpolate

        self.conv1 = nn.Conv2d(in_channels, 32, kernel_size=3, padding=1)  # -> 32x32x32
        self.relu1 = nn.ReLU()
        self.conv2 = nn.Conv2d(32, 64, kernel_size=3, padding=1) # -> 64x32x32
        self.relu2 = nn.ReLU()
        self.pool1 = nn.MaxPool2d(2, 2) # -> 64x16x16

        self.conv3 = nn.Conv2d(64, 128, kernel_size=3, padding=1) # -> 128x16x16
        self.relu3 = nn.ReLU()
        self.pool2 = nn.MaxPool2d(2, 2)                                    # -> 128x8x8

        self.flatten = nn.Flatten()
        self.fc1 = nn.Linear(128 * 8 * 8, 256)
        self.relu4 = nn.ReLU()
        self.fc2 = nn.Linear(256, num_classes)

    def forward(self, x):
        if self.interpolate:
            x = F.interpolate(x, size=(32, 32), mode='bilinear', align_corners=False)

        x = self.relu1(self.conv1(x))  # -> 32x32x32
        x = self.relu2(self.conv2(x))  # -> 64x32x32
        x = self.pool1(x)              # -> 64x16x16
        x = self.relu3(self.conv3(x))  # -> 128x16x16
        x = self.pool2(x)              # -> 128x8x8

        x = self.flatten(x)           # flatten
        x = self.relu4(self.fc1(x))   # -> 256
        x = self.fc2(x)               # -> num_classes
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
    net = B_SimpleCNN(in_channels=1, num_classes=2)
    net.init_weights()
    a = torch.randn(50, 1, 32, 35)
    result = net(a)
    print(result.shape)