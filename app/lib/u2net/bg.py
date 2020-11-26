import base64
import io
import numpy as np
import requests
from PIL import Image
from flask import current_app
from app.lib.u2net import detect
from app.helpers.common import formatSize, img_to_base64


def remove(image=None, url=None, model_name="u2netp"):
    if model_name == "u2netp":
        model = current_app.config["U2NETP_MODEL"]
    else:
        model = current_app.config["U2NET_MODEL"]
    if image:
        f_size = formatSize(len(image.read()))
        if f_size > 5:
            return False, "传入图片需小于5M"
        img = Image.open(image).convert("RGB")
    elif url:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36"
        }
        response = requests.get(url, headers=headers, timeout=5)
        f_size = formatSize(len(io.BytesIO(response.content).getvalue()))
        if f_size > 5:
            return False, "传入图片需小于5M"
        img = Image.open(io.BytesIO(response.content)).convert("RGB")
    roi = detect.predict(model, np.array(img))
    roi = roi.resize((img.size), resample=Image.LANCZOS)

    empty = Image.new("RGBA", (img.size), 0)
    out = Image.composite(img, empty, roi.convert("L"))
    base64_str_data = img_to_base64(out)
    # bio = io.BytesIO()
    # out.save(bio, "PNG")

    return True, base64_str_data
