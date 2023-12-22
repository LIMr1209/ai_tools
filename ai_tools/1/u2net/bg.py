# cython: language_level=3
import base64
import io
import numpy as np
from PIL import Image
from .detect import predict


def formatSize(bytes):
    try:
        bytes = float(bytes)
        kb = bytes / 1024
    except:
        print("传入的字节格式不对")
        return "Error"

    return kb / 1024


def img_to_base64(img):
    img_buffer = io.BytesIO()
    img.save(img_buffer, format="PNG", quality=100)
    byte_data = img_buffer.getvalue()
    base64_str = base64.b64encode(byte_data)
    base64_str = "data:image/jpg;base64," + base64_str.decode(encoding="ascii")
    return base64_str


def remove(in_0, net):
    image = io.BytesIO(in_0[0])
    img = Image.open(image).convert('RGB')

    roi = predict(net, np.array(img))

    roi = roi.resize((img.size), resample=Image.LANCZOS)

    empty = Image.new("RGBA", (img.size), 0)
    out = Image.composite(img, empty, roi.convert("L"))

    img_bytes = io.BytesIO()
    out.save(img_bytes, format='PNG')

    out_0 = np.array(img_bytes.getvalue())
    return out_0
