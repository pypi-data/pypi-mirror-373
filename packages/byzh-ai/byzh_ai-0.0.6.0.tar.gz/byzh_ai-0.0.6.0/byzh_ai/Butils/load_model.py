import torch.nn as nn
import collections

def b_load_model(
    model: nn.Module,
    model_state_dict: collections.OrderedDict
):
    # print(type(model_state_dict))
    flag_model = isinstance(model, nn.DataParallel)
    flag_dict = list(model_state_dict.keys())[0].startswith('module.')
    if (not flag_model) and flag_dict:
        model_state_dict = {k[7:]: v for k, v in model_state_dict.items()}
    if flag_model and (not flag_dict):
        model_state_dict = {'module.' + k: v for k, v in model_state_dict.items()}

    model.load_state_dict(model_state_dict)

    return model