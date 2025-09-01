import numpy as np
import torch


def b_data_standard1d(datas: list, template_data=None, dim=(0, 2), mean=None, std=None):
    '''
    对数据进行标准化\n
    如果没有传入mean和std，则根据template_data计算mean和std
    :param datas: 待标准化的数据
    :param template_data: 用于计算mean和std的模板数据
    :param dim: dim=(0, 2)代表 每个通道(dim=1)单独标准化
    :param mean:
    :param std:
    :return:
    '''
    flag1 = template_data is not None
    flag2 = mean is not None
    flag3 = std is not None

    # 如果没传入template_data和mean和std
    if not (flag1 or flag2 or flag3):
        raise ValueError("要么传入template_data; 要么传入mean,std")

    # 如果mean和std没有传入，则计算
    if not (flag2 and flag3):
        if type(template_data) == torch.Tensor:
            mean = torch.mean(template_data, dim=dim, keepdim=True)
            std = torch.std(template_data, dim=dim, keepdim=True) + 1e-8
        else:
            mean = np.mean(template_data, axis=dim, keepdims=True)
            std = np.std(template_data, axis=dim, keepdims=True) + 1e-8

    results = []
    for target_data in datas:
        target_data = (target_data - mean) / std
        results.append(target_data)

    return results

def b_data_standard2d(datas: list, template_data=None, dim=(0, 2, 3), mean=None, std=None):
    '''
    对数据进行标准化\n
    如果没有传入mean和std，则根据template_data计算mean和std
    :param datas: 待标准化的数据
    :param template_data: 用于计算mean和std的模板数据
    :param dim: dim=(0, 2, 3)代表 每个通道(dim=1)单独标准化
    :param mean:
    :param std:
    :return:
    '''
    flag1 = template_data is not None
    flag2 = mean is not None
    flag3 = std is not None

    # 如果没传入template_data和mean和std
    if not (flag1 or flag2 or flag3):
        raise ValueError("要么传入template_data; 要么传入mean,std")

    # 如果mean和std没有传入，则计算
    if not (flag2 and flag3):
        if type(template_data) == torch.Tensor:
            mean = torch.mean(template_data, dim=dim, keepdim=True)
            std = torch.std(template_data, dim=dim, keepdim=True) + 1e-8
        else:
            mean = np.mean(template_data, axis=dim, keepdims=True)
            std = np.std(template_data, axis=dim, keepdims=True) + 1e-8

    results = []
    for target_data in datas:
        target_data = (target_data - mean) / std
        results.append(target_data)
    return results


from sklearn.model_selection import train_test_split

def b_train_test_split(X, y, test_size=0.2, random_state=42):
     X_train, X_test, y_train, y_test = train_test_split(
         X, y, test_size=test_size, random_state=random_state
     )
     return X_train, X_test, y_train, y_test