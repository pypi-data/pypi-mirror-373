import torch
def b_get_flops(model, input_shape: tuple, verbose=False):
    """
    获取FLOPs
    :param model:
    :param input_shape: (C, ...)
    :return:
    """
    try:
        from thop import profile
    except ImportError:
        raise ImportError("[get_flops] 请先安装thop库: pip install thop")

    # 获取模型的 device
    device = next(model.parameters()).device

    # 定义输入
    input_tensor = torch.randn(1, *input_shape).to(device)

    # 计算 FLOPs 和参数量
    flops, params = profile(model, inputs=(input_tensor,), verbose=verbose)

    return flops


if __name__ == '__main__':

    import torchvision.models as models
    # 实例化模型
    model = models.resnet18()
    # 输入形状
    input_shape = (3, 224, 224)
    # 计算 FLOPs 和参数量
    print(b_get_flops(model, input_shape))
