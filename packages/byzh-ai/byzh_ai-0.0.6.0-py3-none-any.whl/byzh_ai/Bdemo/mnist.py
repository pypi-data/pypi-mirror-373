import os
import numpy as np
import torch
import torchvision
from torch import nn
from pathlib import Path

from ..Btrainer import B_Trainer
from ..Butils import b_get_device
from ..Bmodel import *
from ..Blr_schedulers import B_WarmupDecayLR

def get_dataloader(batch_size, saveDir):
    from torch.utils.data import random_split, DataLoader
    from torchvision import transforms

    os.makedirs(saveDir / "dataset", exist_ok=True)

    image_transform = transforms.Compose([
        # transforms.Resize((224, 224)),
        transforms.Resize((32, 32)),
        transforms.ToTensor(),
    ])
    datasets = torchvision.datasets.MNIST(saveDir / "dataset", train=True, download=True, transform=image_transform)
    train_datasets, val_datasets = random_split(datasets, [55000, 5000])
    train_datasets = torch.utils.data.Subset(train_datasets, np.arange(1000))
    val_datasets = torch.utils.data.Subset(val_datasets, np.arange(1000))

    train_dataloader = DataLoader(train_datasets, batch_size=batch_size, shuffle=True)
    val_dataloader = DataLoader(val_datasets, batch_size=8, shuffle=False)

    return train_dataloader, val_dataloader

def b_mnist(saveDir):
    saveDir = Path(saveDir)
    os.makedirs(saveDir, exist_ok=True)
    #### 超参数 ####
    lr = 1e-4
    batch_size = 128
    # epochs = 5
    epochs = 50
    device = b_get_device()

    #### 数据集 ####
    train_dataloader, val_dataloader = get_dataloader(batch_size, saveDir)

    #### 模型 ####
    # net = B_ResNet18(in_channels=1, num_classes=10)
    net = B_Lenet5(num_classes=10)
    net.blk0 = nn.Sequential(
        nn.Conv2d(in_channels=1, out_channels=64, kernel_size=7, stride=2, padding=3),
        nn.BatchNorm2d(64),
        nn.ReLU(),
        nn.MaxPool2d(kernel_size=3, stride=2, padding=1)
    )
    net.to(device)
    criterion = nn.CrossEntropyLoss()
    optimizer = torch.optim.Adam(net.parameters(), lr=lr)
    lr_scheduler = B_WarmupDecayLR(optimizer, 5e-5, 3, 3)
    #### Trainer ####
    myTrainer = B_Trainer(
        model=net,
        train_loader=train_dataloader,
        val_loader=val_dataloader,
        optimizer=optimizer,
        criterion=criterion,
        device=device,
        lrScheduler=lr_scheduler,
        isParallel=True
    )
    myTrainer.set_writer1(saveDir / 'logawa.txt', mode='w')

    # myTrainer.set_reload_by_loss(5, 10)
    # myTrainer.set_stop_by_acc(5, 0.01)
    # myTrainer.set_stop_by_loss(5, 0.01)
    # myTrainer.set_stop_by_acc_delta(5, 0.003)
    # myTrainer.set_stop_by_loss_delta(5, 0.01)
    # myTrainer.set_stop_by_overfitting(5, 0.01)

    #### 训练/测试 ####
    myTrainer.train_eval_s(epochs)

    #### 保存模型 ####
    myTrainer.save_best_checkpoint(saveDir / 'checkpoint/best_checkpoint.pth')

    myTrainer.calculate_model(dataloader=val_dataloader)
    myTrainer.load_model(saveDir / 'checkpoint/best_checkpoint.pth')
    myTrainer.calculate_model(dataloader=val_dataloader)

    #### 画图 ####
    myTrainer.draw_loss_acc(saveDir / 'checkpoint/latest_checkpoint.jpg', if_show=False)

if __name__ == '__main__':
    saveDir = '.'
    b_mnist(saveDir)