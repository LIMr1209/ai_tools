import errno
import os
import sys
import numpy as np
import torch
from PIL import Image
from torchvision import transforms
from . import data_loader, u2net
from flask import current_app


def load_model(model_name: str = "u2net"):
    if model_name == "u2netp":
        net = u2net.U2NETP(3, 1)
        net.load_state_dict(torch.load(current_app.config['U2NETP_PATH'], map_location='cpu'))
        # if current_app.config['TORCH_GPU']:
        #     net.load_state_dict(torch.load(current_app.config['U2NETP_PATH'],map_location='cuda:1'))
        # else:
        #     net.load_state_dict(torch.load(current_app.config['U2NETP_PATH'],map_location='cpu'))
    elif model_name == "u2net":
        net = u2net.U2NET(3, 1)
        net.load_state_dict(torch.load(current_app.config['U2NET_PATH'], map_location='cpu'))
        # if current_app.config['TORCH_GPU']:
        #     net.load_state_dict(torch.load(current_app.config['U2NET_PATH'],map_location='cuda:1'))
        # else:
        #     net.load_state_dict(torch.load(current_app.config['U2NET_PATH'], map_location='cpu'))
    else:
        print("Choose between u2net or u2netp", file=sys.stderr)
        return None
    net.eval()

    return net


def norm_pred(d):
    ma = torch.max(d)
    mi = torch.min(d)
    dn = (d - mi) / (ma - mi)

    return dn


def preprocess(image):
    label_3 = np.zeros(image.shape)
    label = np.zeros(label_3.shape[0:2])

    if 3 == len(label_3.shape):
        label = label_3[:, :, 0]
    elif 2 == len(label_3.shape):
        label = label_3

    if 3 == len(image.shape) and 2 == len(label.shape):
        label = label[:, :, np.newaxis]
    elif 2 == len(image.shape) and 2 == len(label.shape):
        image = image[:, :, np.newaxis]
        label = label[:, :, np.newaxis]

    transform = transforms.Compose(
        [data_loader.RescaleT(320), data_loader.ToTensorLab(flag=0)]
    )
    sample = transform({"imidx": np.array([0]), "image": image, "label": label})

    return sample


def predict(net, item):
    sample = preprocess(item)

    with torch.no_grad():
        inputs_test = torch.FloatTensor(sample["image"].unsqueeze(0).float())
        # if current_app.config['TORCH_GPU']:
        #     device = torch.device('cuda:1')
        #     inputs_test = inputs_test.to(device)
        # if current_app.config['TORCH_GPU']:
        #     inputs_test = torch.cuda.FloatTensor(sample["image"].unsqueeze(0).float())
        # else:
        #     inputs_test = torch.FloatTensor(sample["image"].unsqueeze(0).float())
        # if torch.cuda.is_available():
        #     inputs_test = torch.cuda.FloatTensor(sample["image"].unsqueeze(0).float())
        # else:
        #     inputs_test = torch.FloatTensor(sample["image"].unsqueeze(0).float())

        d1, d2, d3, d4, d5, d6, d7 = net(inputs_test)

        pred = d1[:, 0, :, :]
        predict = norm_pred(pred)

        predict = predict.squeeze()
        predict_np = predict.cpu().detach().numpy()
        img = Image.fromarray(predict_np * 255).convert("RGB")

        del d1, d2, d3, d4, d5, d6, d7, pred, predict, predict_np, inputs_test, sample

        return img
