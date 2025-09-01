import numpy as np
from torch.utils.data import Dataset, DataLoader
import torch

class MyDataset(Dataset):
    def __init__(self, data, label):
        self.data = data
        self.label = label
    def __len__(self):
        return len(self.data)
    def __getitem__(self, index):
        return self.data[index], self.label[index]


def b_merge_dataset(*args: Dataset):
    datas_labels = []

    for dataset in args:
        if not isinstance(dataset, Dataset):
            raise TypeError("dataset must be an instance of Dataset")
        length = len(dataset)
        for i in range(length):
            data, label = dataset.__getitem__(i)
            datas_labels.append([data, label])

    # 根据label对datas_labels排序
    datas_labels = sorted(datas_labels, key=lambda x: x[1]) # 从小到大
    # 拆分开
    datas, labels = zip(*datas_labels)

    datas = torch.stack(datas, dim=0)
    labels = torch.tensor(labels)

    my_dataset = MyDataset(datas, labels)
    return my_dataset




