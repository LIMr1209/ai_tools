import torch
import numpy as np
from torchvision import transforms as T
from PIL import Image


# tensor 转换 为 image np
def tensor2im(input_image, imtype=np.uint8):
    if not isinstance(input_image, np.ndarray):
        if isinstance(input_image, torch.Tensor):  # get the data from a variable
            image_tensor = input_image.data
        else:
            return input_image
        image_numpy = (
            image_tensor[0].cpu().float().numpy()
        )  # convert it into a numpy array
        if image_numpy.shape[0] == 1:  # grayscale to RGB
            image_numpy = np.tile(image_numpy, (3, 1, 1))
        image_numpy = (
                (np.transpose(image_numpy, (1, 2, 0)) + 1) / 2.0 * 255.0
        )  # post-processing: tranpose and scaling
    else:  # if it is a numpy array, do nothing
        image_numpy = input_image
    return image_numpy.astype(imtype)


transforms = T.Compose(
    [
        T.Resize([256, 256], Image.BICUBIC),
        T.RandomCrop(256),
        T.ToTensor(),
        T.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5)),
    ]
)


image = Image.open('test4.jpg').convert("RGB")
input = transforms(image)
input = input.view(1, 3, 256, 256)
result = tensor2im(input)
img_new = Image.fromarray(result)
img_new.save('test.jpg')