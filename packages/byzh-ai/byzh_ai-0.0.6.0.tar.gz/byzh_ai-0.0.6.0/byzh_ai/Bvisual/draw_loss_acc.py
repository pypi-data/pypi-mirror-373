from pathlib import Path
import os
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
def b_draw_loss_acc(train_loss_batches_lst, train_acc_lst, val_acc_lst,
                  path: Path, if_show=False):
    """
    :param path: 如果以.csv结尾, 则保存为csv文件, 否则保存为图片
    :param if_show:
    :return:
    """
    path = Path(path)
    parent_path = path.parent
    os.makedirs(parent_path, exist_ok=True)
    file_name = path.name
    suffix = file_name.split('.')[-1]
    if suffix == 'csv':
        df = pd.DataFrame(
            data=[train_loss_batches_lst, train_acc_lst, val_acc_lst],
            index=["train_loss", "train_acc", "val_acc"]
        )
        df.to_csv(path, index=True, header=False)
        return

    if if_show == False:
        matplotlib.use('Agg')

    palette = sns.color_palette("Set2", 3)

    plt.figure(figsize=(12, 8))
    plt.subplots_adjust(hspace=0.4)

    plt.subplot(2, 1, 1)
    # 每十个画一次(防止点多卡顿)
    temp = [x for i, x in enumerate(train_loss_batches_lst) if (i + 1) % 10 == 0]
    plt.plot(temp, color="red", label="train_loss")
    plt.xlabel("iter 1/10", fontsize=18)
    plt.ylabel("loss", fontsize=18)
    plt.legend(loc='upper right', fontsize=16)
    plt.grid(True)

    plt.subplot(2, 1, 2)
    plt.plot(train_acc_lst, color="red", label="train_acc")
    plt.plot(val_acc_lst, color="blue", label="val_acc")
    # 找到train_acc的峰值点并标记
    train_acc_peak_index = np.argmax(train_acc_lst)
    plt.scatter(train_acc_peak_index, train_acc_lst[train_acc_peak_index], color="red", marker="v", s=100)
    # 找到val_acc的峰值点并标记
    val_acc_peak_index = np.argmax(val_acc_lst)
    plt.scatter(val_acc_peak_index, val_acc_lst[val_acc_peak_index], color="blue", marker="v", s=100)
    plt.xlabel("epoch", fontsize=18)
    plt.ylabel("acc", fontsize=18)
    plt.ylim(-0.05, 1.05)
    plt.legend(loc='lower right', fontsize=16)
    plt.grid(True)

    plt.tight_layout()
    plt.savefig(path)
    print(f"[draw] picture 已保存到{path}")
    if if_show:
        plt.show()
    plt.close()