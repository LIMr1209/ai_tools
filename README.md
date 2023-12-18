# 测试私有化部署

## 模型文件加解密
- 事先 设置一个固定字符串通过 md5 加密成 AES key 通过AES 对称加密算法 加密模型文件
- 运行时 通过固定字符串 md5 加密成 AES key 通过AES 对称加密算法 解密模型文件 为 bytes
- torch.load bytes
## Cython 编译
- 通过 Cython 编译项目所有 py 文件为 共享链接库 (windows pyd, linux so), 保持项目结构 
- 入口 manage.py 文件 不编译 
- 依赖现有 python 环境运行 manage.py 文件
- `python setup_main.py` 
- `python manage.py`
## Nuitka 编译
- 通过 Cython 编译项目所有 py 文件为 共享链接库 (windows pyd, linux so), 保持项目结构 
- 入口 manage.py 文件 不编译 
- 依赖现有 python 环境运行 manage.py 文件
- `python nuitka_build.py` 
- `python manage.py`
## pyarmor 加密
- `pyarmor-7 init --entry=manage.py`
- `pyarmor-7 config --manifest "global-include *.py, prune venv, prune dist, exclude nuitka_build.py, exclude setup.py, exclude setup_main.py"`
- `pyarmor-7 build `
- 全局密钥箱是存放在用户主目录的一个文件 .pyarmor_capsule.zip 。当 PyArmor 加密脚本或者生成加密脚本的许可文件的时候，都需要从这个文件中读取数据。 所有的试用版本使用同一个密钥箱 公共密钥箱 ，这个密钥箱使用 1024 位 RSA 密钥对。 而对于正式版本，每一个用户都会收到一个专用的 私有密钥箱 ，这种密钥箱使用 2048 位 RSA 密钥对。 通过密钥箱是无法恢复加密后的脚本，所以即便都使用 公共密钥箱 ，加密后的脚本也是 安全的，但是使用相同的密钥箱为加密脚本生成的许可是通用的。使用 公共密钥箱 是无 法真正的限制加密脚本的使用期限或者绑定到某一台指定设备上，因为别人同样可以使用 公共密钥箱 为你的加密脚本生成合法的许可。 运行加密脚本并不需要密钥箱，只有在加密脚本和为加密脚本生成许可的时候才会用到。

## gunicron 部署测试
- 正常使用 `gunicorn -w 4 'manage:app'`

## 问题
- 需要测试性能
- 没有解决设备绑定问题
- 复杂Pytorch代码和环境未测试