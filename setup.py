import sys
# from distutils.core import setup
from setuptools import setup


try:
    from Cython.Build import cythonize
except:
    print("你没有安装Cython，请安装 pip install Cython")
    print("本项目需要 Visual Studio 2022 的C++开发支持，请确认安装了相应组件")

arg_list = sys.argv
f_name = arg_list[1]
sys.argv.pop(1)

setup(ext_modules=cythonize(f_name))