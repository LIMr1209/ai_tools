import base64
from pathlib import Path

import cv2
import torch
from PIL import Image
from torchvision.utils import make_grid
from dalle_pytorch import OpenAIDiscreteVAE, DiscreteVAE, DALLE, VQGanVAE1024
from dalle_pytorch.tokenizer import tokenizer
from flask import current_app

from app.helpers.common import img_to_base64
from app.lib.cyclegan import tensor2im


def generate_text(params):
    c = ['black', 'white', 'red', 'pink', 'yellow', 'grey', 'silver', 'purple', 'blue', 'green', 'golden', 'brown',
         'pink']
    m = ['rigid', 'fabric', 'leather']
    f = ['matte', 'glossy', 'rough']
    lg = ['double', 'single']  # pull rod
    zl = ['universal wheel', 'one-way wheel']
    y = ['large', 'small']
    fz = ['business', 'child', 'casual', 'sports', 'vintage']
    c_zh = ['黑色', '白色', '红色', '粉红色', '黄色', '灰色', '银色', '紫色', '蓝色', '绿色', '金色', '褐色', '粉色']
    m_zh = ['硬质', '尼龙/帆布', '皮革']
    f_zh = ['氧化/磨砂', '玻璃', '粗糙']
    lg_zh = ['双杆', '单杆']
    zl_zh = ['万向轮', '单向轮']
    y_zh = ['托运箱', '登机箱']
    fz_zh = ['商务', '儿童', '休闲', '运动', '复古']
    # tags = ['tag-c', 'tag-m', 'tag-f', 'tag-y', 'tag-zl', 'tag-lg', 'tag-fz']
    text = 'a '
    if 'tag-c' in params and params['tag-c']:
        text += c[c_zh.index(params['tag-c'])] + ' '
    if 'tag-f' in params and params['tag-f']:
        text += f[f_zh.index(params['tag-f'])] + ' '
    if 'tag-m' in params and params['tag-m']:
        text += m[m_zh.index(params['tag-m'])] + ' '
    text += 'shell '
    if 'tag-lg' in params and params['tag-lg']:
        text += lg[lg_zh.index(params['tag-lg'])] + '-rod '
    if 'tag-y' in params and params['tag-y']:
        text += y[y_zh.index(params['tag-y'])] + ' suitcase in '
    if 'tag-fz' in params and params['tag-fz']:
        text += fz[fz_zh.index(params['tag-fz'])] + ' style'
    if 'tag-zl' in params and params['tag-zl']:
        text += 'with '+zl[zl_zh.index(params['tag-zl'])] + '.'
    return text


def intelligent(params, type):
    text_o = generate_text(params)
    DALLE_PATH = './dalle_10.pt'
    dalle_path = Path(DALLE_PATH)
    loaded_obj = torch.load(str(dalle_path), map_location=torch.device('cpu'))
    dalle_params, vae_params, weights = loaded_obj['hparams'], loaded_obj['vae_params'], loaded_obj['weights']
    vae = VQGanVAE1024()  # DiscreteVAE(**vae_params)
    # dalle_params = dict(
    #     #         vae = vae,
    #     **dalle_params
    # )
    # vae = VQGanVAE1024()  # OpenAIDiscreteVAE()
    dalle = DALLE(vae=vae, **dalle_params)
    dalle.load_state_dict(weights)
    text = tokenizer.tokenize(text_o, dalle.text_seq_len)
    output = dalle.generate_images(text, filter_thres=0.9)
    result = tensor2im(output)
    img_new = Image.fromarray(result)
    base64_str_data = img_to_base64(img_new)
    return base64_str_data
    # image = make_grid(output.cpu()).numpy()
    # retval, buffer = cv2.imencode('.jpg', image)
    # pic_str = base64.b64encode(buffer)
    # pic_str = pic_str.decode()
    # image_base64 = "data:image/jpg;base64,"+pic_str
    # return image_base64
