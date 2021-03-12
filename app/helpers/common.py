# 工具函数
import base64
import datetime
import re
from io import BytesIO
from PIL import Image
from werkzeug import security

# 加密
import hashlib
from bson import ObjectId


def isset(v):
    try:
        type(eval(v))
    except:
        return False
    else:
        return True


def force_int(value, default=0):
    try:
        return int(value)
    except:
        return default


def force_float_2(value, default=0):
    try:
        value = float(value)
        return float("%.2f" % value)
    except:
        return default


# md5
def gen_md5(str):
    m = hashlib.md5()
    m.update(str.encode("utf8"))
    return m.hexdigest()


# sha1
def gen_sha1(str):
    m = hashlib.sha1()
    m.update(str.encode("utf8"))
    return m.hexdigest()


# 返回指定key对应值
def filter_key(keys, row):
    data = {}
    for f in keys:
        if f in row:
            data[f] = row[f]

    return data


# 字符串转列表
def str_list(value):
    list = re.split("[,，、；;]", value)
    if "" in list:
        list.remove("")
    return list


# 随机生成BsonId
def gen_mongo_id():
    return ObjectId().__str__()


# 生成随机字符串（指定长度）
def generate_str(length=16):
    return security.gen_salt(length)


# 数组去重、去两边空格、去空
def list_clear(arr):
    # 去重
    arr = list(set(arr))
    # 去两边空格
    for i, d in enumerate(arr):
        if isinstance(d, str):
            arr[i] = d.strip()
    # 去空
    if "" in arr:
        arr.remove("")
    if None in arr:
        arr.remove(None)

    return arr


# 时间戳转 datetime
def timeStamp_datetime(timeStamp):
    return datetime.datetime.utcfromtimestamp(int(timeStamp))


def formatSize(bytes):
    try:
        bytes = float(bytes)
        kb = bytes / 1024
    except:
        print("传入的字节格式不对")
        return "Error"

    return kb / 1024


def img_to_base64(img):
    img_buffer = BytesIO()
    img.save(img_buffer, format="PNG", quality=100)
    byte_data = img_buffer.getvalue()
    base64_str = base64.b64encode(byte_data)
    base64_str = "data:image/jpg;base64," + base64_str.decode(encoding="ascii")
    return base64_str



def pil_to_base64(file):
    image = Image.open(file).convert("RGB")
    image_base64 = img_to_base64(image)
    return image_base64