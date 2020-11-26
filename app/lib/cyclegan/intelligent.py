import os
from io import BytesIO
import requests
from flask import current_app
from app.lib.cyclegan import networks
from torchvision import transforms as T
from PIL import Image
import torch
import numpy as np
from app.helpers.common import formatSize
from app.helpers.constant import intelligent_category
from app.helpers.common import img_to_base64


# tensor 转换 为 image np
def tensor2im(input_image, imtype=np.uint8):
    if not isinstance(input_image, np.ndarray):
        if isinstance(input_image, torch.Tensor):  # get the data from a variable
            image_tensor = input_image.data
        else:
            return input_image
        image_numpy = (
            image_tensor[0].cpu().float().numpy()
        )  # convert it into a numpy array
        if image_numpy.shape[0] == 1:  # grayscale to RGB
            image_numpy = np.tile(image_numpy, (3, 1, 1))
        image_numpy = (
                (np.transpose(image_numpy, (1, 2, 0)) + 1) / 2.0 * 255.0
        )  # post-processing: tranpose and scaling
    else:  # if it is a numpy array, do nothing
        image_numpy = input_image
    return image_numpy.astype(imtype)


# def __crop(img, pos, size):
#     ow, oh = img.size
#     x1, y1 = pos
#     tw = th = size
#     if (ow > tw or oh > th):
#         return img.crop((x1, y1, x1 + tw, y1 + th))
#     return img
#
#
# transforms = T.Compose([
#     T.Resize(size=[256, 256], interpolation=PIL.Image.BICUBIC),
#     T.Lambda(lambda img: __crop(img, (0, 0), 256)),
#     T.ToTensor(),
#     T.Normalize(mean=(0.5, 0.5, 0.5), std=(0.5, 0.5, 0.5))
# ])

transforms = T.Compose(
    [
        T.Resize([256, 256], Image.BICUBIC),
        T.RandomCrop(256),
        T.ToTensor(),
        T.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5)),
    ]
)


def __patch_instance_norm_state_dict(state_dict, module, keys, i=0):
    """Fix InstanceNorm checkpoints incompatibility (prior to 0.4)"""
    key = keys[i]
    if i + 1 == len(keys):  # at the end, pointing to a parameter/buffer
        if module.__class__.__name__.startswith("InstanceNorm") and (
                key == "running_mean" or key == "running_var"
        ):
            if getattr(module, key) is None:
                state_dict.pop(".".join(keys))
        if module.__class__.__name__.startswith("InstanceNorm") and (
                key == "num_batches_tracked"
        ):
            state_dict.pop(".".join(keys))
    else:
        __patch_instance_norm_state_dict(state_dict, getattr(module, key), keys, i + 1)


# 加载图片 转换为 input
def image_loader(url=None, image=None):
    if url:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36"
        }
        try:
            response = requests.get(url, headers=headers, timeout=5)
            f_size = formatSize(len(BytesIO(response.content).getvalue()))
            if f_size > 2:
                return False, "传入图片需小于2M"
        except:
            response = None
        image = Image.open(BytesIO(response.content)).convert("RGB")
    elif image:
        f_size = formatSize(len(image.read()))
        if f_size > 2:
            return False, "传入图片需小于2M"
        image = Image.open(image).convert("RGB")
    input = transforms(image)
    input = input.view(1, 3, 256, 256).to(torch.device('cuda:1'))
    return True, input


# 加载模型
def load_cycle_model(path, index, s):
    complete_path = os.path.join(current_app.config["MODEL_PATH"], path, s)
    files = os.listdir(complete_path)
    files.sort(key=lambda x: int(x[:-12]), reverse=True)
    model = networks.define_G(
        3, 3, 64, "resnet_9blocks", "instance", False, "normal", 0.02, [0]
    )
    if isinstance(model, torch.nn.DataParallel):
        model = model.module
    state_dict = torch.load(os.path.join(complete_path, files[index]), map_location={'cuda:0':'cuda:1'})
    if hasattr(state_dict, "_metadata"):
        del state_dict._metadata
    # for key in list(state_dict.keys()):  # need to copy keys here because we mutate in loop
    #     __patch_instance_norm_state_dict(state_dict, model, key.split('.'))
    model.load_state_dict(state_dict)
    model.eval()
    return model


def load_pix2pix_model(path, index, s):
    complete_path = os.path.join(current_app.config["MODEL_PATH"], path, s)
    files = os.listdir(complete_path)
    files.sort(key=lambda x: int(x[:-10]), reverse=True)
    model = networks.define_G(3, 3, 64, 'unet_256', 'batch', True, 'normal', 0.02, [0])
    if isinstance(model, torch.nn.DataParallel):
        model = model.module
    state_dict = torch.load(os.path.join(complete_path, files[index]), map_location={'cuda:0':'cuda:1'})
    if hasattr(state_dict, "_metadata"):
        del state_dict._metadata
    # for key in list(state_dict.keys()):  # need to copy keys here because we mutate in loop
    #     __patch_instance_norm_state_dict(state_dict, model, key.split('.'))
    model.load_state_dict(state_dict)
    model.eval()
    return model


# demo
def intelligent(url=None, image=None, index=0, type=None, model_name='cycle'):
    torch.cuda.set_device(1)
    if model_name == 'cycle':
        a_model = load_cycle_model(intelligent_category(type)['name'], index=index, s='A')
        try:
            b_model = load_cycle_model(intelligent_category(type)['name'], index=index, s='B')
        except:
            b_model = ''
    else:
        a_model = load_pix2pix_model(intelligent_category(type)['name'], index=index, s='C')
        b_model = ''
    # bas64_str = []
    input_tensor = ''
    res = ''
    if url:
        res, input_tensor = image_loader(url=url)
    elif image:
        res, input_tensor = image_loader(image=image)
    if not res:
        return False, input_tensor
    torch.set_grad_enabled(False)
    if  b_model:
        input_tensor = b_model(input_tensor)
        result = tensor2im(input_tensor)
        img_new = Image.fromarray(result)
        input = transforms(img_new)
        input_tensor = input.view(1, 3, 256, 256).to(torch.device('cuda:1'))
    output = a_model(input_tensor)
    result = tensor2im(output)
    img_new = Image.fromarray(result)
    torch.set_grad_enabled(True)
    base64_str_data = img_to_base64(img_new)
    # bas64_str.append(base64_str_data)
    return True, base64_str_data
