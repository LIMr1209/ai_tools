import os

from PIL import Image
import dnnlib_pytorch as dnnlib
import numpy as np
import torch
import app.lib.stylegan_pytorch.legacy as legacy
from flask import current_app
import random
from app.helpers.constant import stylegan_ada_category

from app.helpers.common import img_to_base64


def generate(type):
    if current_app.config['TORCH_GPU']:
        device = torch.device('cuda')
        force_fp32 = False
    else:
        device = torch.device('cpu')
        force_fp32 = True
    truncation_psi = 1
    network_path = os.path.join(os.path.join(current_app.config['MODEL_PATH'], 'stylegan_ada', stylegan_ada_category(type)['name'], 'network.pkl'))
    with dnnlib.util.open_url(network_path) as f:
        G = legacy.load_network_pkl(f)['G_ema'].to(device)  # 必须保留目录结构，也就是说dnnlib_te 更换位dnnlib 才能复现加载模型
    label = torch.zeros([1, G.c_dim], device=device)
    seed = random.randint(1, 20000)
    z = torch.from_numpy(np.random.RandomState(seed).randn(1, G.z_dim)).to(device)
    img = G(z, label, truncation_psi=truncation_psi, noise_mode='const', force_fp32=force_fp32)
    img = (img.permute(0, 2, 3, 1) * 127.5 + 128).clamp(0, 255).to(torch.uint8)
    img_new = Image.fromarray(img[0].cpu().numpy(), 'RGB')
    image_base64 = img_to_base64(img_new)
    return True, image_base64
