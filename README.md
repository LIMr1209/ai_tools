# 测试私有化部署

## 模型文件加解密
- 事先 设置一个固定字符串通过 md5 加密成 AES key 通过AES 对称加密算法 加密模型文件
- 运行时 通过固定字符串 md5 加密成 AES key 通过AES 对称加密算法 解密模型文件 为 bytes
- torch.load bytes
## python 源代码编译
- 通过 Cython 编译项目所有 py 文件为 共享链接库 (windows pyd, linux so), 保持项目结构 
- 入口 main.py 文件 不编译 
- 依赖现有 python 环境运行 main.py 文件

## Linux 系统未测试

## gunicron 部署未测试