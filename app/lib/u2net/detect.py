# cython: language_level=3
import errno
import io
import os
import sys
import numpy as np
import torch
from PIL import Image
from torchvision import transforms
from . import data_loader, u2net
from flask import current_app

# pip install pycryptodome
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import hashlib

k = b"lizhenbin"
hash = hashlib.md5()
hash.update(k)
b = hash.hexdigest().encode()


def encrypt_file(key, in_filename, out_filename=None, chunksize=64 * 1024):
    # if not out_filename:
    #     out_filename = in_filename + '.enc'
    iv = os.urandom(16)
    encryptor = AES.new(key, AES.MODE_CBC, iv)
    filesize = os.path.getsize(in_filename)
    with open(in_filename, 'rb') as infile:
        with open(out_filename, 'wb') as outfile:
            # prefix = struct.pack('<Q', filesize)
            # outfile.write(prefix)
            outfile.write(iv)
            pos = 0
            while pos < filesize:
                chunk = infile.read(chunksize)
                pos += len(chunk)
                if pos == filesize:
                    chunk = pad(chunk, AES.block_size, style='pkcs7')
                outfile.write(encryptor.encrypt(chunk))


# def decrypt_file(key, in_filename, out_filename=None, chunksize=64 * 1024):
#     # if not out_filename:
#     #     out_filename = in_filename + '.dec'
#     with open(in_filename, 'rb') as infile:
#         # prefix = struct.unpack('<Q', infile.read(8))[0]
#         iv = infile.read(16)
#         encryptor = AES.new(key, AES.MODE_CBC, iv)
#         with open(out_filename, 'wb') as outfile:
#             encrypted_filesize = os.path.getsize(in_filename)
#             pos = 16  # the filesize and IV.
#             while pos < encrypted_filesize:
#                 chunk = infile.read(chunksize)
#                 pos += len(chunk)
#                 chunk = encryptor.decrypt(chunk)
#                 if pos == encrypted_filesize:
#                     chunk = unpad(chunk, AES.block_size, style='pkcs7')
#                 outfile.write(chunk)

def decrypt_file(key, in_filename, out_filename=None, chunksize=64 * 1024):
    # if not out_filename:
    #     out_filename = in_filename + '.dec'
    chunks = b""
    with open(in_filename, 'rb') as infile:
        # prefix = struct.unpack('<Q', infile.read(8))[0]
        iv = infile.read(16)
        encryptor = AES.new(key, AES.MODE_CBC, iv)
        encrypted_filesize = os.path.getsize(in_filename)
        pos = 16  # the filesize and IV.
        while pos < encrypted_filesize:
            chunk = infile.read(chunksize)
            pos += len(chunk)
            chunk = encryptor.decrypt(chunk)
            if pos == encrypted_filesize:
                chunk = unpad(chunk, AES.block_size, style='pkcs7')
            chunks += chunk
    return chunks


def load_model(model_name: str = "u2net"):
    if model_name == "u2netp":
        net = u2net.U2NETP(3, 1)
        model_path = current_app.config['U2NETP_PATH']

    elif model_name == "u2net":
        net = u2net.U2NET(3, 1)
        model_path = current_app.config['U2NET_PATH']
    else:
        print("Choose between u2net or u2netp", file=sys.stderr)
        return None
    chunks = decrypt_file(b, model_path)
    net.load_state_dict(torch.load(io.BytesIO(chunks), map_location='cpu'))
    # if current_app.config['TORCH_GPU']:
    #     net.load_state_dict(torch.load(current_app.config['U2NETP_PATH'],map_location='cuda:1'))
    # else:
    #     net.load_state_dict(torch.load(current_app.config['U2NETP_PATH'],map_location='cpu'))
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
