from PIL import Image
import torch
from flask import current_app
from app.helpers.constant import draw_generate_category
from app.helpers.common import img_to_base64
from app.lib.cyclegan import image_loader, tensor2im
import cv2
import base64


# demo  绘制草图生成
def draw_generate(image=None, base64_data=None, type=None):
    res, input_tensor = image_loader(image=image, base64_data=base64_data)
    if not res:
        return False, input_tensor
    torch.set_grad_enabled(False)
    output = current_app.config['DRAW_MODEL_1'](input_tensor)
    result = tensor2im(output)
    torch.set_grad_enabled(True)
    img_new = Image.fromarray(result)
    image_base64 = img_to_base64(img_new)
    # img = cv2.cvtColor(result, cv2.COLOR_RGB2BGR) # cv2 默认BGR 需要转换RGB
    # retval, buffer = cv2.imencode('.jpg', img)
    # image_base64 = "data:image/jpg;base64," + str(base64.b64encode(buffer), encoding='utf-8')
    return True, image_base64
