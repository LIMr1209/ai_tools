import os
from flask import current_app
from PIL import Image
from app.lib.u2net import detect
import numpy as np

def remove(catalog):
    for j, i in enumerate(os.listdir(catalog)):
        path = os.path.join(catalog, i)
        if os.path.isdir(path):
            remove(path)
        else:
            print('正在处理')
            image = Image.open(path).convert("RGB")
            model = current_app.config["U2NET_MODEL"]
            roi = detect.predict(model, np.array(image))
            roi = roi.resize((image.size), resample=Image.LANCZOS)

            empty = Image.new("RGBA", (image.size), 0)
            new_dir = path.rsplit('\\',1)[0]+'_new'
            if not os.path.isdir(new_dir):
                os.makedirs(new_dir)
            out = Image.composite(image, empty, roi.convert("L"))
            bg = Image.new("RGB", out.size, (255, 255, 255))
            bg.paste(out, out)
            bg.save(new_dir+'\\'+i)
            print('保存成功')


# path = "C:\\Users\\aaa10\\Desktop\\拉杆箱-去底"


