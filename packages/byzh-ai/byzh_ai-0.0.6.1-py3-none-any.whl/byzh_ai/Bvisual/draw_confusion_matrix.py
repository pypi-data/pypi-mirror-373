import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.metrics import confusion_matrix


def b_draw_confusion_matrix1(y_true: np.ndarray|list, y_pred: np.ndarray|list):
    y_true, y_pred = np.array(y_true), np.array(y_pred)

    # 计算混淆矩阵
    labels = sorted(set(y_true))  # 确保标签按顺序
    cm = confusion_matrix(y_true, y_pred, labels=labels)
    labels = [i for i in range(len(cm))]

    # 绘制热力图
    plt.figure(figsize=(7, 6))
    ax = sns.heatmap(cm, annot=True, fmt="d", cmap="Reds", xticklabels=labels, yticklabels=labels)
    ax.xaxis.set_ticks_position("top")  # 将 X 轴的刻度移动到顶部
    ax.xaxis.set_label_position("top")  # 将 X 轴的标签移动到顶部
    plt.xlabel("Predicted Label", fontsize=14)
    plt.ylabel("True Label", fontsize=14)

    return plt

def b_draw_confusion_matrix2(cm):
    cm = np.array(cm)
    labels = [i for i in range(len(cm))]

    # 绘制热力图
    plt.figure(figsize=(7, 6))
    ax = sns.heatmap(cm, annot=True, fmt="d", cmap="Reds", xticklabels=labels, yticklabels=labels)
    ax.xaxis.set_ticks_position("top")  # 将 X 轴的刻度移动到顶部
    ax.xaxis.set_label_position("top")  # 将 X 轴的标签移动到顶部
    plt.xlabel("Predicted Label", fontsize=14)
    plt.ylabel("True Label", fontsize=14)

    return plt

if __name__ == '__main__':
    cm = np.array(
        [[140, 0, 5, 0, 0, 0, 2, 0, 1, 1, 0, 0],
         [1, 155, 3, 0, 0, 0, 1, 3, 0, 0, 1, 0],
         [2, 0, 129, 0, 0, 0, 2, 0, 1, 0, 0, 1],
         [0, 1, 2, 110, 1, 1, 4, 3, 0, 1, 0, 1],
         [0, 0, 3, 2, 102, 2, 0, 1, 0, 0, 0, 1],
         [1, 1, 7, 1, 2, 98, 2, 6, 1, 0, 0, 0],
         [1, 2, 9, 0, 1, 3, 124, 1, 1, 0, 0, 3],
         [3, 0, 4, 0, 4, 2, 4, 127, 1, 0, 0, 2],
         [1, 1, 2, 1, 1, 0, 2, 6, 97, 2, 13, 2],
         [0, 2, 3, 0, 1, 0, 0, 1, 5, 100, 7, 5],
         [0, 5, 0, 1, 1, 1, 0, 1, 9, 5, 97, 1],
         [1, 4, 4, 0, 1, 2, 1, 1, 3, 3, 2, 116]]
    )
    plt = b_draw_confusion_matrix2(cm)
    plt.show()