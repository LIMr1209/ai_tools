from flask import current_app
from torchvision.utils import make_grid
import torch
from app.helpers.common import img_to_base64

truncation = 1
truncation_mean = 4096
channel_multiplier = 2
device = "cuda:1"
size = 256


def load_model():
    ckpt = current_app.config['STYLEGAN_PATH']
    from .model import Generator
    g_ema = Generator(size, 512, 8, channel_multiplier=2).to(device)
    checkpoint = torch.load(ckpt, map_location=lambda storage, loc: storage)
    g_ema.load_state_dict(checkpoint["g_ema"])
    g_ema.eval()
    return g_ema


def get_sample(func, seed=0, **kwargs):
    torch.cuda.set_device(1)
    torch.set_grad_enabled(False)
    g_ema = load_model()
    if not seed:
        with open("seed.txt", mode="r", encoding="utf-8") as r_file:
            seed = int(r_file.readlines()[0])
        with open("seed.txt", mode="w", encoding="utf-8") as w_file:
            w_file.write(str(seed + 1))
    torch.manual_seed(seed)
    sample_z = torch.randn(1, 512, device=device)
    if func == "g":
        base64_str_data, seed = generate(seed, sample_z, g_ema,  **kwargs)
    else:
        base64_str_data, seed = latent(seed, sample_z, g_ema, **kwargs)
    return base64_str_data, seed


def generate(seed, sample_z, g_ema, **kwargs):
    sample, _ = g_ema(
        [sample_z], truncation=truncation, truncation_latent=None
    )
    from PIL import Image
    grid = make_grid(sample, nrow=1, padding=2, pad_value=0,
                     normalize=True, range=(-1, 1), scale_each=False)
    ndarr = grid.mul(255).add_(0.5).clamp_(0, 255).permute(1, 2, 0).to('cpu', torch.uint8).numpy()
    im = Image.fromarray(ndarr)
    base64_str_data = img_to_base64(im)
    return base64_str_data, seed


def latent(seed, sample_z, g_ema, **kwargs):
    factor = current_app.config['FACTOR_PATH']
    eigvec = torch.load(factor)["eigvec"].to(device)
    latent = g_ema.get_latent(sample_z)
    trunc = g_ema.mean_latent(truncation_mean)

    direction = kwargs['d'] * eigvec[:, kwargs['i']].unsqueeze(0)

    sample, _ = g_ema(
        [latent + direction],
        truncation=truncation,
        truncation_latent=trunc,
        input_is_latent=True,
    )
    from PIL import Image
    grid = make_grid(sample, nrow=1, padding=2, pad_value=0,
                     normalize=True, range=(-1, 1), scale_each=False)
    ndarr = grid.mul(255).add_(0.5).clamp_(0, 255).permute(1, 2, 0).to('cpu', torch.uint8).numpy()
    im = Image.fromarray(ndarr)
    base64_str_data = img_to_base64(im)
    return base64_str_data, seed
