# cython: language_level=3
from configparser import ConfigParser, ExtendedInterpolation
import os

basedir = os.path.abspath(os.path.dirname(__file__))
# 读取.env 配置
cf = ConfigParser(interpolation=ExtendedInterpolation())
cf.read(os.path.abspath(os.path.join(basedir, "..", ".env")))
