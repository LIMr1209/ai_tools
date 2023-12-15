# cython: language_level=3
import torch as t
from io import BytesIO
from torchvision import transforms as T
import requests
from PIL import Image
from flask import current_app
from PIL import ImageFile

from app.lib.img_recognition.load_model import load_model

ImageFile.LOAD_TRUNCATED_IMAGES = True  # 图片文件允许截断


normalize = T.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])


# 图片处理
def data_handle():
    transforms = T.Compose(
        [
            T.Resize(
                (current_app.config["IMAGE_SIZE"], current_app.config["IMAGE_SIZE"])
            ),
            T.ToTensor(),
            normalize,
        ]
    )
    return transforms


# 加载图片
def image_loader(url=None, image=None):
    if url:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36"
        }
        try:
            response = requests.get(url, headers=headers, timeout=5)
        except:
            response = None
        image = Image.open(BytesIO(response.content)).convert("RGB")
    elif image:
        image = Image.open(image).convert("RGB")
    return data_handle()(image)


# 识别
def recognition(url=None, image=None):
    with t.no_grad():  # 用来标志计算要被计算图隔离出去
        if url:
            image = image_loader(url=url)
        elif image:
            image = image_loader(image=image)
        model = load_model()
        image = image.view(
            1, 3, current_app.config["IMAGE_SIZE"], current_app.config["IMAGE_SIZE"]
        )  # 转换image
        outputs = model(image)
        results = outputs.max(dim=1)[1].detach()
        index = results.tolist()[0]
        # result = {}
        # for i in range(current_app.config['NUM_CLASSES']):  # 计算各分类比重
        #     result[current_app.config['CATE_CLASSES'][i]] = \
        #         t.nn.functional.softmax(outputs, dim=1)[:, i].detach().tolist()[0]
        # result = sorted(result.items(), key=lambda x: x[1], reverse=True)
        return current_app.config["CATE_CLASSES"][index]
