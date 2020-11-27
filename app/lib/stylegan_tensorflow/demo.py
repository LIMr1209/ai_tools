import random

from flask import current_app
import cv2
import dnnlib.tflib as tflib
from app.helpers.color_cluster_1126 import majoColor_inrange
from app.helpers.common import img_to_base64
from dnnlib import EasyDict
import numpy as np
from PIL import Image
import pickle


def load_model():
    network_path = current_app.config['STYLEGAN_TE_PATH']
    truncation_psi = 0.5
    stream = open(network_path, 'rb')
    tflib.init_tf()
    with stream:
        G, D, Gs = pickle.load(stream, encoding='latin1')
    noise_vars = [var for name, var in Gs.components.synthesis.vars.items() if name.startswith('noise')]

    Gs_kwargs = EasyDict()
    Gs_kwargs.output_transform = dict(func=tflib.convert_images_to_uint8, nchw_to_nhwc=True)
    Gs_kwargs.randomize_noise = False
    Gs_kwargs.truncation_psi = truncation_psi
    return Gs, Gs_kwargs, noise_vars




def get_sample(color=None):
    # import os
    # os.environ['CUDA_VISIBLE_DEVICES'] = "3"
    Gs, Gs_kwargs, noise_vars = load_model()
    # Gs = current_app.config['GS']
    # Gs_kwargs = current_app.config['GS_KWARGS']
    # noise_vars = current_app.config['NOISE_VARS']
    img_data_list = []
    seed_list = [random.randint(1, 100000) for i in range(500)]
    for i in seed_list:
        if len(img_data_list) >= 6:
            break
        rnd = np.random.RandomState(i)
        z = rnd.randn(1, *Gs.input_shape[1:])  # [minibatch, component]
        tflib.set_vars({var: rnd.randn(*var.shape.as_list()) for var in noise_vars})  # [height, width]
        images = Gs.run(z, None, **Gs_kwargs)  # [minibatch, height, width, channel]
        img = Image.fromarray(images[0], 'RGB')
        base64_str_data = img_to_base64(img)
        if color:
            np_array = np.asarray(img)
            image_cv2 = cv2.cvtColor(np_array, cv2.COLOR_RGB2BGR)
            color_tags = majoColor_inrange(image_cv2)
            if color_tags == color:
                img_data_list.append(base64_str_data)
        else:
            img_data_list.append(base64_str_data)
    return img_data_list