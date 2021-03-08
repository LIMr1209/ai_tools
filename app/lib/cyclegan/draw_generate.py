from PIL import Image
import torch
from app.helpers.constant import draw_generate_category
from app.helpers.common import img_to_base64
from app.lib.cyclegan import load_cycle_single, image_loader, tensor2im


# demo  绘制草图生成
def draw_generate(image=None, type=None):
    model = load_cycle_single(draw_generate_category(type)['name'],'200_net_G_A.pth')
    res, input_tensor = image_loader(image=image)
    if not res:
        return False, input_tensor
    torch.set_grad_enabled(False)
    output = model(input_tensor)
    result = tensor2im(output)
    img_new = Image.fromarray(result)
    torch.set_grad_enabled(True)
    # img_new = Image.open('test.png')
    base64_str_data = img_to_base64(img_new)
    return True, base64_str_data
