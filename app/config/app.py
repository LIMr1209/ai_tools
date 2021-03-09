#  常规配置
import os
from app.env import cf
from app.helpers.constant import get_tag, draw_generate_category

ENV = "development" if cf.getint("base", "debug") == 1 else "production"
DEBUG = True if cf.getint("base", "debug") == 1 else False  # 当 env 为 development 本变量启动
RUN_PORT = cf.get("base", "run_port", fallback="8012")
SECRET_KEY = cf.get("base", "secret_key")
PROJECT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
CONFDIR = os.path.join(PROJECT_DIR, "config")

BABEL_DEFAULT_LOCALE = "zh"
BABEL_SUPPORTED_LOCALES = ["zh"]

COOKIE_EXPIRES = cf.getint("base", "cookie_expires")

MODEL_PATH = cf.get("checkpoint", "model_path")

STYLEGAN_PATH = cf.get("checkpoint", "stylegan_path", fallback='')
STYLEGAN_TE_PATH = cf.get("checkpoint", "stylegan_te_path", fallback='')
FACTOR_PATH = cf.get("checkpoint", "factor_path", fallback='')
#
# if STYLEGAN_TE_PATH:
#     from app.lib.stylegan_tensorflow.demo import load_model
#
#     GS, GS_KWARGS, NOISE_VARS = load_model(STYLEGAN_TE_PATH)
# 画笔生成模型
DRAW_MODEL_EPOCH_1 = cf.get("checkpoint", "draw_model_epoch_1", fallback='')
if DRAW_MODEL_EPOCH_1:
    from app.lib.cyclegan import load_cycle_single
    DRAW_MODEL_1 = load_cycle_single(MODEL_PATH, draw_generate_category(1)['name'],'{}_net_G_A.pth'.format(DRAW_MODEL_EPOCH_1))

# 图像识别模型预加载
MODEL_NAME = cf.get("ai", "model", fallback='')
LOAD_MODEL_PATH = cf.get("ai", "load_model_path", fallback='')
if LOAD_MODEL_PATH:
    IMAGE_SIZE = 224
    CATE_CLASSES = get_tag()
    NUM_CLASSES = len(CATE_CLASSES)
    from app.lib.img_recognition.load_model import load_model

    MODEL = load_model(NUM_CLASSES, LOAD_MODEL_PATH, MODEL_NAME)
# 图像去背景模型预加载
U2NETP_PATH = cf.get("ai", "u2netp_path", fallback='')

if U2NETP_PATH:
    from app.lib.u2net.detect import load_model

    U2NETP_MODEL = load_model(path=U2NETP_PATH)

# 图像去背景模型预加载
U2NET_PATH = cf.get("ai", "u2net_path", fallback='')
if U2NET_PATH:
    from app.lib.u2net.detect import load_model

    U2NET_MODEL = load_model(model_name="u2net", path=U2NET_PATH)