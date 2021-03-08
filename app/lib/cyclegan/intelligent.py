from PIL import Image
import torch
from app.helpers.constant import intelligent_category
from app.helpers.common import img_to_base64
from app.lib.cyclegan import load_cycle_model, load_pix2pix_model, image_loader, tensor2im, transforms


# demo 原草图上传生成
def intelligent(url=None, image=None, index=0, type=None, model_name='cycle'):
    # import os
    # os.environ['CUDA_VISIBLE_DEVICES'] = "4"
    # torch.cuda.set_device(2)
    if model_name == 'cycle':
        a_model = load_cycle_model(intelligent_category(type)['name'], index=index, s='A')
        try:
            b_model = load_cycle_model(intelligent_category(type)['name'], index=index, s='B')
        except:
            b_model = ''
    else:
        a_model = load_pix2pix_model(intelligent_category(type)['name'], index=index, s='C')
        b_model = ''
    # bas64_str = []
    input_tensor = ''
    res = ''
    if url:
        res, input_tensor = image_loader(url=url)
    elif image:
        res, input_tensor = image_loader(image=image)
    if not res:
        return False, input_tensor
    torch.set_grad_enabled(False)
    if  b_model:
        input_tensor = b_model(input_tensor)
        result = tensor2im(input_tensor)
        img_new = Image.fromarray(result)
        input = transforms(img_new)
        input_tensor = input.view(1, 3, 256, 256).to(torch.device('cpu'))
    output = a_model(input_tensor)
    result = tensor2im(output)
    img_new = Image.fromarray(result)
    torch.set_grad_enabled(True)
    base64_str_data = img_to_base64(img_new)
    # bas64_str.append(base64_str_data)
    return True, base64_str_data
