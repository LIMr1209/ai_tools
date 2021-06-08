from pathlib import Path
import torch
from torchvision.utils import make_grid
from dalle_pytorch import OpenAIDiscreteVAE, DiscreteVAE, DALLE, VQGanVAE1024
from dalle_pytorch.tokenizer import tokenizer
from flask import current_app

from app.helpers.common import img_to_base64


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
    tags = ['tag-c', 'tag-m', 'tag-f', 'tag-y', 'tag-zl', 'tag-lg', 'tag-fz']
    row = ['', ]
    for i in tags:
        if i in params:
            value = params[i]
            if i == 'tag-c':
                row.append(c[c_zh.index(value)])
            elif i == 'tag-m':
                row.append(m[m_zh.index(value)])
            elif i == 'tag-f':
                row.append(f[f_zh.index(value)])
            elif i == 'tag-y':
                row.append(y[y_zh.index(value)])
            elif i == 'tag-zl':
                row.append(zl[zl_zh.index(value)])
            elif i == 'tag-lg':
                row.append(lg[lg_zh.index(value)])
            elif i == 'tag-fz':
                row.append(fz[fz_zh.index(value)])
        else:
            row.append('')

    text = f"A {c[int(row[2]) - 1]} {f[int(row[4]) - 1]} {m[int(row[3]) - 1]} shell {lg[int(row[5]) - 1]}-rod {y[int(row[7]) - 1]} suitcase in {fz[int(row[8]) - 1]} style with {zl[int(row[6]) - 1]}."
    return text


def intelligent(params, type):
    text_o = generate_text(params)
    DALLE_PATH = current_app.config['']
    dalle_path = Path(DALLE_PATH)
    loaded_obj = torch.load(str(dalle_path), map_location=torch.device('cpu'))
    dalle_params, vae_params, weights = loaded_obj['hparams'], loaded_obj['vae_params'], loaded_obj['weights']
    vae = VQGanVAE1024()  # DiscreteVAE(**vae_params)
    dalle_params = dict(
        #         vae = vae,
        **dalle_params
    )
    vae = VQGanVAE1024()  # OpenAIDiscreteVAE()
    dalle = DALLE(vae=vae, **dalle_params)
    dalle.load_state_dict(weights)
    text = tokenizer.tokenize(text_o, dalle.text_seq_len)
    output = dalle.generate_images(text, filter_thres=0.9)
    image = make_grid(output.cpu()).numpy()
    image_base64 = img_to_base64(image)
    return image_base64
