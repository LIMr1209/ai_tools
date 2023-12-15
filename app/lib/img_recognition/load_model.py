# cython: language_level=3
import torch
import torch.nn as nn
import app.lib.img_recognition.models as models
from flask import current_app


# 批量归一化融合
def fuse_bn_sequential(block):
    """
    This function takes a sequential block and fuses the batch normalization with convolution
    :param model: nn.Sequential. Source resnet model
    :return: nn.Sequential. Converted block
    """
    if not isinstance(block, nn.Sequential):
        return block
    stack = []
    for m in block.children():
        if isinstance(m, nn.BatchNorm2d):
            if isinstance(stack[-1], nn.Conv2d):
                bn_st_dict = m.state_dict()
                conv_st_dict = stack[-1].state_dict()

                # BatchNorm params
                eps = m.eps
                mu = bn_st_dict["running_mean"]
                var = bn_st_dict["running_var"]
                gamma = bn_st_dict["weight"]

                if "bias" in bn_st_dict:
                    beta = bn_st_dict["bias"]
                else:
                    beta = torch.zeros(gamma.size(0)).float().to(gamma.device)

                # Conv params
                W = conv_st_dict["weight"]
                if "bias" in conv_st_dict:
                    bias = conv_st_dict["bias"]
                else:
                    bias = torch.zeros(W.size(0)).float().to(gamma.device)

                denom = torch.sqrt(var + eps)
                b = beta - gamma.mul(mu).div(denom)
                A = gamma.div(denom)
                bias *= A
                A = A.expand_as(W.transpose(0, -1)).transpose(0, -1)

                W.mul_(A)
                bias.add_(b)

                stack[-1].weight.data.copy_(W)
                if stack[-1].bias is None:
                    stack[-1].bias = torch.nn.Parameter(bias)
                else:
                    stack[-1].bias.data.copy_(bias)

        else:
            stack.append(m)

    if len(stack) > 1:
        return nn.Sequential(*stack)
    else:
        return stack[0]


def fuse_bn_recursively(model):
    for module_name in model._modules:
        model._modules[module_name] = fuse_bn_sequential(model._modules[module_name])
        if len(model._modules[module_name]._modules) > 0:
            fuse_bn_recursively(model._modules[module_name])

    return model


def load_model(NUM_CLASSES, LOAD_MODEL_PATH, MODEL_NAME):
    model = getattr(models, MODEL_NAME)(NUM_CLASSES)
    if LOAD_MODEL_PATH:
        checkpoint = torch.load(LOAD_MODEL_PATH, map_location="cpu")
        model.load_state_dict(checkpoint["state_dict"])  # 加载模型参数
    model = fuse_bn_recursively(model)  # 加快识别速度
    model.eval()
    return model
