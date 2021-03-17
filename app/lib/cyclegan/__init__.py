import base64
import os
from io import BytesIO

import cv2
import numpy as np
import requests
import torch
from PIL import Image
from flask import current_app
from torchvision import transforms as T, transforms
from app.helpers.common import formatSize, bool_simple
from app.lib.cyclegan import networks


# tensor 转换 为 image np


def tensor2im(input_image, imtype=np.uint8):
    """"Converts a Tensor array into a numpy image array.
    Parameters:
        input_image (tensor) --  the input image tensor array
        imtype (type)        --  the desired type of the converted numpy array
    """
    if not isinstance(input_image, np.ndarray):
        if isinstance(input_image, torch.Tensor):  # get the data from a variable
            image_tensor = input_image.data
        else:
            return input_image
        image_numpy = image_tensor[0].cpu().float().numpy()  # convert it into a numpy array
        if image_numpy.shape[0] == 1:  # grayscale to RGB
            image_numpy = np.tile(image_numpy, (3, 1, 1))
        image_numpy = (np.transpose(image_numpy, (1, 2, 0)) + 1) / 2.0 * 255.0  # post-processing: tranpose and scaling
    else:  # if it is a numpy array, do nothing
        image_numpy = input_image
    return image_numpy.astype(imtype)


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


# transforms = T.Compose(
#     [
#         T.Resize([256, 256], Image.BICUBIC),
#         T.RandomCrop(256),
#         T.ToTensor(),
#         T.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5)),
#     ]
# )
def crop_and_normalize(pil_img, offset=20):
    w, h = pil_img.size
    img_array = np.array(pil_img.convert('L'))
    boundary = np.argwhere(img_array == 0)
    x = [element[1] for element in boundary]
    y = [element[0] for element in boundary]

    if min(x) - offset < 0:
        left = min(x)
    else:
        left = min(x) - offset
    if max(x) + offset > w:
        right = max(x)
    else:
        right = max(x) + offset
    if min(y) - offset < 0:
        up = min(y)
    else:
        up = min(y) - offset
    if max(y) + offset > h:
        down = max(y)
    else:
        down = max(y) + offset

    # long_edge = max(max(x) - min(x), max(y) - min(y))
    # half = int(long_edge / 2)
    # centerX, centerY = int((min(x) + max(x)) / 2), int((min(y) + max(y)) / 2)
    #
    # left, up, right, down = centerX - half - offset, centerY - half - offset, centerX + half + offset, centerY + half + offset
    #
    # left = 0 if left < 0 else left
    # up = 0 if up < 0 else up
    # right = 256 if right > 256 else right
    # down = 256 if down > 256 else down

    box = (left, up, right, down)
    crop_img = pil_img.crop(box)

    return crop_img


def resize_equal(img):
    image = cv2.cvtColor(np.asarray(img), cv2.COLOR_RGB2BGR)
    top, bottom, left, right = (0, 0, 0, 0)

    # 获取图像尺寸
    h, w, _ = image.shape

    # 对于长宽不相等的图片，找到最长的一边
    longest_edge = max(h, w)

    # 计算短边需要增加多上像素宽度使其与长边等长
    if h < longest_edge:
        dh = longest_edge - h
        top = dh // 2
        bottom = dh - top
    elif w < longest_edge:
        dw = longest_edge - w
        left = dw // 2
        right = dw - left
    else:
        pass

    # RGB颜色
    color = [255, 255, 255]

    # 给图像增加边界，是图片长、宽等长，cv2.BORDER_CONSTANT指定边界颜色由value指定
    constant = cv2.copyMakeBorder(image, top, bottom, left, right, cv2.BORDER_CONSTANT, value=color)
    image = Image.fromarray(cv2.cvtColor(constant, cv2.COLOR_BGR2RGB))
    return image


# 加载图片 转换为 input
def image_loader(load_size, url=None, image=None, base64_data=None, path=None):
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
    elif base64_data:
        image = base64.b64decode(base64_data)
        image = BytesIO(image)
        image = Image.open(image).convert('RGB')
        simple_img = bool_simple(image)  # 判断纯色
        if simple_img:
            return False, "纯色图片"
        image = crop_and_normalize(image)
        # image = image.resize((256, 256), Image.ANTIALIAS).convert('RGB')
    elif path:
        image = Image.open(path).convert('RGB')
    simple_img = bool_simple(image) # 判断纯色
    if simple_img:
        return False, "纯色图片"
    w, h = image.size
    if w != h:
        image = resize_equal(image) # 等 宽 高
    transform_func = get_transform(load_size)
    input = transform_func(image)
    # input = input.unsqueeze(0)
    if current_app.config['TORCH_GPU']:
        input = input.view(1, 3, load_size, load_size).to(torch.device('cuda'))
    else:
        input = input.view(1, 3, load_size, load_size).to(torch.device('cpu'))
    return True, input


def get_transform(load_size, params=None, grayscale=False, method=Image.BICUBIC, convert=True):
    preprocess = 'resize'
    no_flip = True  # 不翻转

    transform_list = []
    if grayscale:
        transform_list.append(transforms.Grayscale(1))

    if 'resize' in preprocess:
        osize = [load_size, load_size]
        transform_list.append(transforms.Resize(osize, method))

    if not no_flip:
        if params is None:
            transform_list.append(transforms.RandomHorizontalFlip())

    if convert:
        transform_list += [transforms.ToTensor()]
        if grayscale:
            transform_list += [transforms.Normalize((0.5,), (0.5,))]
        else:
            transform_list += [transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))]
    return transforms.Compose(transform_list)


# 加载草图生成模型cycle
def load_cycle_model(path, index, s, type=''):
    complete_path = os.path.join(current_app.config["MODEL_PATH"], type, path, s).replace('\\', '/')
    files = os.listdir(complete_path)
    files.sort(key=lambda x: int(x[:-12]), reverse=True)
    if current_app.config['TORCH_GPU']:
        model = networks.define_G(
            3, 3, 64, "resnet_9blocks", "instance", False, "normal", 0.02, [0]
        )
    else:
        model = networks.define_G(
            3, 3, 64, "resnet_9blocks", "instance", False, "normal", 0.02,
        )
    if isinstance(model, torch.nn.DataParallel):
        model = model.module
    state_dict = torch.load(os.path.join(complete_path, files[index]))
    if hasattr(state_dict, "_metadata"):
        del state_dict._metadata
    # for key in list(state_dict.keys()):  # need to copy keys here because we mutate in loop
    #     __patch_instance_norm_state_dict(state_dict, model, key.split('.'))
    model.load_state_dict(state_dict)
    model.eval()
    return model


# 加载草图生成模型pix2pix
def load_pix2pix_model(path, index, s):
    complete_path = os.path.join(current_app.config["MODEL_PATH"], path, s)
    files = os.listdir(complete_path)
    files.sort(key=lambda x: int(x[:-10]), reverse=True)
    model = networks.define_G(3, 3, 64, 'unet_256', 'batch', True, 'normal', 0.02, [0])
    if isinstance(model, torch.nn.DataParallel):
        model = model.module
    state_dict = torch.load(os.path.join(complete_path, files[index]))
    if hasattr(state_dict, "_metadata"):
        del state_dict._metadata
    # for key in list(state_dict.keys()):  # need to copy keys here because we mutate in loop
    #     __patch_instance_norm_state_dict(state_dict, model, key.split('.'))
    model.load_state_dict(state_dict)
    model.eval()
    return model
