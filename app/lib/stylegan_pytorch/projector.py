import base64
import copy
import os
from io import BytesIO

import numpy as np
import torch
import torch.nn.functional as F
from PIL import Image
from flask import current_app

import dnnlib_pytorch as dnnlib
from app.lib.stylegan_pytorch import legacy
from app.helpers.common import img_to_base64
from app.helpers.constant import fuse_divergence_category


def project(
        G,
        target: torch.Tensor,  # [C,H,W] and dynamic range [0,255], W & H must match G output resolution
        *,
        num_steps=10,
        w_avg_samples=10000,
        initial_learning_rate=0.1,
        initial_noise_factor=0.05,
        lr_rampdown_length=0.25,
        lr_rampup_length=0.05,
        noise_ramp_length=0.75,
        regularize_noise_weight=1e5,
        device: torch.device
):
    assert target.shape == (G.img_channels, G.img_resolution, G.img_resolution)
    G = copy.deepcopy(G).eval().requires_grad_(False).to(device)  # type: ignore
    z_samples = np.random.RandomState(123).randn(w_avg_samples, G.z_dim)
    w_samples = G.mapping(torch.from_numpy(z_samples).to(device), None)  # [N, L, C]
    w_samples = w_samples[:, :1, :].cpu().numpy().astype(np.float32)  # [N, 1, C]
    w_avg = np.mean(w_samples, axis=0, keepdims=True)  # [1, 1, C]
    w_std = (np.sum((w_samples - w_avg) ** 2) / w_avg_samples) ** 0.5

    # Setup noise inputs.
    noise_bufs = {name: buf for (name, buf) in G.synthesis.named_buffers() if 'noise_const' in name}

    # Load VGG16 feature detector.
    url = 'https://nvlabs-fi-cdn.nvidia.com/stylegan2-ada-pytorch/pretrained/metrics/vgg16.pt'
    with dnnlib.util.open_url(url) as f:
        vgg16 = torch.jit.load(f).eval().to(device)

    # Features for target image.
    target_images = target.unsqueeze(0).to(device).to(torch.float32)
    if target_images.shape[2] > 256:
        target_images = F.interpolate(target_images, size=(256, 256), mode='area')
    target_features = vgg16(target_images, resize_images=False, return_lpips=True)

    w_opt = torch.tensor(w_avg, dtype=torch.float32, device=device, requires_grad=True)  # pylint: disable=not-callable
    w_out = torch.zeros([num_steps] + list(w_opt.shape[1:]), dtype=torch.float32, device=device)
    optimizer = torch.optim.Adam([w_opt] + list(noise_bufs.values()), betas=(0.9, 0.999), lr=initial_learning_rate)

    # Init noise.
    for buf in noise_bufs.values():
        buf[:] = torch.randn_like(buf)
        buf.requires_grad = True
    losses = []
    for step in range(num_steps):
        # Learning rate schedule.
        t = step / num_steps
        w_noise_scale = w_std * initial_noise_factor * max(0.0, 1.0 - t / noise_ramp_length) ** 2
        lr_ramp = min(1.0, (1.0 - t) / lr_rampdown_length)
        lr_ramp = 0.5 - 0.5 * np.cos(lr_ramp * np.pi)
        lr_ramp = lr_ramp * min(1.0, t / lr_rampup_length)
        lr = initial_learning_rate * lr_ramp
        for param_group in optimizer.param_groups:
            param_group['lr'] = lr

        # Synth images from opt_w.
        w_noise = torch.randn_like(w_opt) * w_noise_scale
        ws = (w_opt + w_noise).repeat([1, G.mapping.num_ws, 1])
        synth_images = G.synthesis(ws, noise_mode='const')

        # Downsample image to 256x256 if it's larger than that. VGG was built for 224x224 images.
        synth_images = (synth_images + 1) * (255 / 2)
        if synth_images.shape[2] > 256:
            synth_images = F.interpolate(synth_images, size=(256, 256), mode='area')

        # Features for synth images.
        synth_features = vgg16(synth_images, resize_images=False, return_lpips=True)
        dist = (target_features - synth_features).square().sum()

        # Noise regularization.
        reg_loss = 0.0
        for v in noise_bufs.values():
            noise = v[None, None, :, :]  # must be [1,1,H,W] for F.avg_pool2d()
            while True:
                reg_loss += (noise * torch.roll(noise, shifts=1, dims=3)).mean() ** 2
                reg_loss += (noise * torch.roll(noise, shifts=1, dims=2)).mean() ** 2
                if noise.shape[2] <= 8:
                    break
                noise = F.avg_pool2d(noise, kernel_size=2)
        loss = dist + reg_loss * regularize_noise_weight

        # Step
        optimizer.zero_grad(set_to_none=True)
        loss.backward()
        optimizer.step()
        losses.append({
            'step': step,
            'loss': round(float(loss), 2),
        })

        # Save projected W for each optimization step.
        w_out[step] = w_opt.detach()[0]

        # Normalize noise.
        with torch.no_grad():
            for buf in noise_bufs.values():
                buf -= buf.mean()
                buf *= buf.square().mean().rsqrt()

    return w_out.repeat([1, G.mapping.num_ws, 1]), losses

def run_projection(base64_data_1, base64_data_2, type):

    device = torch.device('cuda')
    path = fuse_divergence_category(type)['name']
    with dnnlib.util.open_url(os.path.join(current_app.config["MODEL_PATH"],'stylegan', path,'network-snapshot-000160.pkl')) as fp:
        G = legacy.load_network_pkl(fp)['G_ema'].requires_grad_(False).to(device)  # type: ignore
    images = [base64_data_1, base64_data_2]
    result = []
    for i in images:
        image = base64.b64decode(i)
        image = BytesIO(image)
        target_pil = Image.open(image).convert('RGB')
        w, h = target_pil.size
        s = min(w, h)
        target_pil = target_pil.crop(((w - s) // 2, (h - s) // 2, (w + s) // 2, (h + s) // 2))
        target_pil = target_pil.resize((G.img_resolution, G.img_resolution), Image.LANCZOS)
        target_uint8 = np.array(target_pil, dtype=np.uint8)

        projected_w_steps, losses = project(
            G,
            target=torch.tensor(target_uint8.transpose([2, 0, 1]), device=device),  # pylint: disable=not-callable
            device=device,
        )
        losses.sort(key=lambda i: i['loss'])
        index_a, index_b = losses[-1]['step'], losses[-3]['step']
        img_1 = get_img(projected_w_steps, index_a, G)
        img_2 = get_img(projected_w_steps, index_b, G)
        image_base64_1 = img_to_base64(img_1)
        image_base64_2 = img_to_base64(img_2)
        result.append(image_base64_1)
        result.append(image_base64_2)
    return result

def run_projection_test(path):

    device = torch.device('cuda')
    with dnnlib.util.open_url(current_app.config['STYLEGAN_PATH']) as fp:
        G = legacy.load_network_pkl(fp)['G_ema'].requires_grad_(False).to(device)  # type: ignore
    target_pil = Image.open(path).convert('RGB')
    w, h = target_pil.size
    s = min(w, h)
    target_pil = target_pil.crop(((w - s) // 2, (h - s) // 2, (w + s) // 2, (h + s) // 2))
    target_pil = target_pil.resize((G.img_resolution, G.img_resolution), Image.LANCZOS)
    target_uint8 = np.array(target_pil, dtype=np.uint8)

    projected_w_steps, losses = project(
        G,
        target=torch.tensor(target_uint8.transpose([2, 0, 1]), device=device),  # pylint: disable=not-callable
        device=device,
    )
    losses.sort(key=lambda i: i['loss'])
    index_a, index_b = losses[-10]['step'], losses[-50]['step']
    img_1 = get_img(projected_w_steps, index_a, G)
    img_2 = get_img(projected_w_steps, index_b, G)
    img_1.save('test_1.jpg')
    img_2.save('test_2.jpg')

def get_img(projected_w_steps, index, G):
    projected_w = projected_w_steps[index]
    synth_image = G.synthesis(projected_w.unsqueeze(0), noise_mode='const')
    synth_image = (synth_image + 1) * (255 / 2)
    synth_image = synth_image.permute(0, 2, 3, 1).clamp(0, 255).to(torch.uint8)[0].cpu().numpy()
    img = Image.fromarray(synth_image, 'RGB')
    return img
