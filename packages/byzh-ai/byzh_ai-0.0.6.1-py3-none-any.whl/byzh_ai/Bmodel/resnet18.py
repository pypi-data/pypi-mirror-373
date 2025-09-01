from torch import nn
from torch.nn import functional as F
import torch


'''
输入：[b,3,224,224]

-> [b,64,112,112]
   [b,64,56,56] (maxpool不算参数)

-> [b,64,56,56]
   [b,64,56,56] 
   [b,64,56,56] 
   [b,64,56,56]

-> [b,128,28,28]
   [b,128,28,28] 
   [b,128,28,28] 
   [b,128,28,28]

-> [b,256,14,14]
   [b,256,14,14] 
   [b,256,14,14] 
   [b,256,14,14]

-> [b,512,7,7]
   [b,512,7,7] 
   [b,512,7,7] 
   [b,512,7,7]

-> [b,512,1,1] （avgpool不算参数）
   [b,512] （view不算参数）
   [b,10]

输出：[b,10]
'''


# 残差块基本单元
class Residual(nn.Module):
    def __init__(self, ch_in, ch_out, stride=1):
        super(Residual, self).__init__()

        self.conv1 = nn.Conv2d(ch_in, ch_out, kernel_size=3, stride=stride, padding=1)
        self.bn1 = nn.BatchNorm2d(ch_out)
        self.conv2 = nn.Conv2d(ch_out, ch_out, kernel_size=3, stride=1, padding=1)
        self.bn2 = nn.BatchNorm2d(ch_out)

        # 残差连接
        self.extra = nn.Sequential()  # 不做变化，直接加
        if ch_out != ch_in:  # shape不一，改变shape，再直接加
            self.extra = nn.Sequential(
                nn.Conv2d(ch_in, ch_out, kernel_size=1, stride=stride),
                nn.BatchNorm2d(ch_out)
            )

    def forward(self, x):
        out = self.bn1(self.conv1(x))
        out = F.relu(out)
        out = self.bn2(self.conv2(out))
        # 残差连接
        out = self.extra(x) + out
        out = F.relu(out)
        return out


# 大残差块
def ResBlk(ch_in, ch_out, num_residuals, first_block=False):
    blk = []
    for i in range(num_residuals):
        if i == 0 and not first_block:
            # 第一个ch_in,ch_out设置相同
            blk.append(Residual(ch_in, ch_out, stride=2))
        else:
            blk.append(Residual(ch_out, ch_out))
    return blk


# ResNet18
class B_ResNet18(nn.Module):
    def __init__(self, in_channels, num_classes):
        super().__init__()

        self.blk0 = nn.Sequential(
            # conv -> bn -> relu
            nn.Conv2d(in_channels=in_channels, out_channels=64, kernel_size=7, stride=2, padding=3),  # /2
            nn.BatchNorm2d(64),
            nn.ReLU(),
            nn.MaxPool2d(kernel_size=3, stride=2, padding=1)
        )
        # 4个大残差块
        # [b, 64, h, w] => [b, 128, h, w]
        self.blk1 = nn.Sequential(*ResBlk(64, 64, 2, first_block=True))
        # [b, 128, h, w] => [b, 256, h, w]
        self.blk2 = nn.Sequential(*ResBlk(64, 128, 2))
        # [b, 256, h, w] => [b, 512, h, w]
        self.blk3 = nn.Sequential(*ResBlk(128, 256, 2))
        # [b, 512, h, w] => [b, 512, h, w]
        self.blk4 = nn.Sequential(*ResBlk(256, 512, 2))

        self.outlayer = nn.Linear(512, num_classes)

    def forward(self, x):
        # 第一层单独卷积，毕竟没有残差块（1个权重层）
        x = self.blk0(x)
        # 接下是4个大残差块（也就是16个权重层）
        x = self.blk1(x)
        x = self.blk2(x)
        x = self.blk3(x)
        x = self.blk4(x)
        x = F.adaptive_avg_pool2d(x, output_size=[1, 1])  # 自适应池化（后两维变为[1,1]）
        x = x.view(x.size(0), -1)  # 转换为[batch,512]
        # 全连接输出层（1个权重层）
        x = self.outlayer(x)

        return x
    def init_weights(self):
        for m in self.modules():
            if isinstance(m, nn.Conv2d):
                nn.init.kaiming_normal_(m.weight, mode='fan_out', nonlinearity='relu')
                if m.bias is not None:
                    nn.init.constant_(m.bias, 0)
            elif isinstance(m, nn.BatchNorm2d):
                nn.init.constant_(m.weight, 1)
                nn.init.constant_(m.bias, 0)
            elif isinstance(m, nn.Linear):
                nn.init.kaiming_normal_(m.weight, mode='fan_in', nonlinearity='relu')
                if m.bias is not None:
                    nn.init.constant_(m.bias, 0)

if __name__ == '__main__':
    net = B_ResNet18(3, 10)
    net.init_weights()
    a = torch.randn(50, 3, 224, 224)
    result = net(a)
    print(result.shape)