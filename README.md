

### 环境布署
- 进入当前项目目录  
- 创建虚拟环境(只在第一次布署时创建 < 3.6)：```virtualenv env```  
- 创建虚拟环境(只在第一次布署时创建 >= 3.6)：```python3 -m venv env``` 
- 切换到虚拟环境：```source env/bin/activate```  
- CPU 安装 PyTorch pip install torch==1.8.1+cpu torchvision==0.9.1+cpu -f https://download.pytorch.org/whl/torch_stable.html)
- GPU 安装 PyTorch pip install torch==1.8.1 torchvision==0.9.1 -f https://download.pytorch.org/whl/torch_stable.html)
- CPU 安装 TensorFlow pip install tensorflow==1.15
- GPU 安装 TensorFlow pip install tensorflow-gpu==1.15
- 安装其他依赖: ```pip3 install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple```   

### 首次配置
- 把根目录文件```.env_example```复制到根目录```.env```，作为当前环境的配置文件  

### 开发环境启动
- 切换当前虚拟环境: ```source env/bin/activate``` 
- 启动程序: ``` python manage.py run ```  
- 浏览地址：``` http://localhost:8002 ```  
- 启动控制台：``` python manage.py shell ```  

### 启动程序uwsgi:
- 切换当前虚拟环境: ```source env/bin/activate```  
- 启动uwsgi服务器: ```uwsgi --ini ./uwsgi.ini --vhost```  
- 快捷启动脚本: ```sh deploy.sh start|stop|restart```  

### 退出当前虚拟环境
```
deactivate
``` 

