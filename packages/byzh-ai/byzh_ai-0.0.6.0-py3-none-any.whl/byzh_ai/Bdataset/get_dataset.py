import numpy as np
import os

from byzh_core import B_os

def save_npys(save_dir, images, labels, prefix):
    os.makedirs(save_dir, exist_ok=True)
    np.save(os.path.join(save_dir, f'{prefix}_images.npy'), images)
    np.save(os.path.join(save_dir, f'{prefix}_labels.npy'), labels)
    print(f"Saved: {prefix}_images.npy, {prefix}_labels.npy")

def check_mnist(dir='./mnist'):
    flag1 = os.path.exists(os.path.join(dir, 'mnist_train_images.npy'))
    flag2 = os.path.exists(os.path.join(dir, 'mnist_train_labels.npy'))
    flag3 = os.path.exists(os.path.join(dir, 'mnist_test_images.npy'))
    flag4 = os.path.exists(os.path.join(dir, 'mnist_test_labels.npy'))
    return flag1 and flag2 and flag3 and flag4

def b_get_mnist1(save_dir='./mnist', mean=0.1307, std=0.3081) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    '''
    采用 torchvision 下载 mnist 数据集\n

    :param save_dir:
    :return: train_images, train_labels, test_images, test_labels
    '''
    if check_mnist(save_dir):
        train_images = np.load(os.path.join(save_dir,'mnist_train_images.npy'))
        train_labels = np.load(os.path.join(save_dir,'mnist_train_labels.npy'))
        test_images = np.load(os.path.join(save_dir,'mnist_test_images.npy'))
        test_labels = np.load(os.path.join(save_dir,'mnist_test_labels.npy'))
        return train_images, train_labels, test_images, test_labels

    from torchvision import datasets
    # 未标准化
    train_data = datasets.MNIST(root='config', train=True, download=True)
    test_data = datasets.MNIST(root='config', train=False, download=True)

    # 转换为 numpy 数组
    train_images = np.stack([np.array(img) for img, _ in train_data])
    train_images = train_images[:, np.newaxis, :, :]
    train_labels = np.array([label for _, label in train_data])

    test_images = np.stack([np.array(img) for img, _ in test_data])
    test_images = test_images[:, np.newaxis, :, :]
    test_labels = np.array([label for _, label in test_data])

    # print(train_images[4000][0][6])

    from .standard import b_data_standard2d
    train_images, test_images = b_data_standard2d(
        datas=[train_images, test_images],
        template_data=train_images,
        mean=mean,
        std=std
    )
    # print(train_images[4000][0][6])

    save_npys(save_dir, train_images, train_labels, 'mnist_train')
    save_npys(save_dir, test_images, test_labels, 'mnist_test')
    B_os.rm('config')

    return train_images, train_labels, test_images, test_labels

def b_get_mnist2(save_dir='./mnist', mean=0.1307, std=0.3081) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    '''
    采用 datasets 下载 mnist 数据集\n
    https://huggingface.co/datasets/ylecun/mnist\n
    https://hf-mirror.com/datasets/ylecun/mnist\n

    :param save_dir:
    :return: train_images, train_labels, test_images, test_labels
    '''
    if check_mnist(save_dir):
        train_images = np.load(os.path.join(save_dir,'mnist_train_images.npy'))
        train_labels = np.load(os.path.join(save_dir,'mnist_train_labels.npy'))
        test_images = np.load(os.path.join(save_dir,'mnist_test_images.npy'))
        test_labels = np.load(os.path.join(save_dir,'mnist_test_labels.npy'))
        return train_images, train_labels, test_images, test_labels

    from datasets import load_dataset
    # 未标准化
    dataset = load_dataset("mnist")

    train_images = np.stack([np.array(example['image']) for example in dataset['train']])
    train_images = train_images[:, np.newaxis, :, :]
    train_labels = np.array([example['label'] for example in dataset['train']])

    test_images = np.stack([np.array(example['image']) for example in dataset['test']])
    test_images = test_images[:, np.newaxis, :, :]
    test_labels = np.array([example['label'] for example in dataset['test']])

    # print(train_images[4000][0][6])

    from .standard import b_data_standard2d
    train_images, test_images = b_data_standard2d(
        datas=[train_images, test_images],
        template_data=train_images,
        mean=mean,
        std=std
    )
    # print(train_images[4000][0][6])

    save_npys(save_dir, train_images, train_labels, 'mnist_train')
    save_npys(save_dir, test_images, test_labels, 'mnist_test')

    return train_images, train_labels, test_images, test_labels


if __name__ == '__main__':
    b_get_mnist2('mnist')