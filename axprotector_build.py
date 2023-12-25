import logging
import os
import subprocess
import threading
from concurrent.futures.thread import ThreadPoolExecutor

import yaml

os.environ[
    "AXPROTECTOR_PYTHON_SDK"] = '"C:\\Program Files (x86)\\WIBU-SYSTEMS\\AxProtector\\Devkit\\bin\\python_nc\\AxProtector.py"'

# 项目根目录下不用（能）转译的py文件（夹）名，用于启动的入口脚本文件一定要加进来
ignore_files = [
    "env", "codemeter"
]
# 不需要原样复制到编译文件夹的文件或者文件夹
ignore_move = ["env", ".idea", ".github", ".git", "codemeter"]
# 需要编译的文件夹绝对路径
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# 将以上不需要转译的文件(夹)加上绝对路径
ignore_files = [os.path.join(BASE_DIR, x) for x in ignore_files]
# 打包文件夹名
package_name = "codemeter"
# 打包文件夹路径
package_path = os.path.join(BASE_DIR, package_name)
# 若没有打包文件夹，则生成一个
if not os.path.exists(package_path):
    os.mkdir(package_path)
# 多并发统计进度需要一个锁,如果这里不统计我们不需要锁
_lock = threading.Lock()
num = 0
all_num = 0
command_list = []
t = 0


# 编译需要的py文件
def translate_dir(path):
    global t
    pathes = os.listdir(path)
    for p in pathes:
        f_path = os.path.join(path, p)
        if f_path in ignore_files:
            continue
        if os.path.isdir(f_path):
            translate_dir(f_path)
        else:
            if not f_path.endswith('.py'):
                continue
            with open('./protect_folder.yaml', 'r', encoding='utf-8') as f:
                result = yaml.load(f.read(), Loader=yaml.FullLoader)
            result["FilesToEncrypt"]["Input"] = f_path
            out_dir = path.replace(BASE_DIR, package_path)
            if not os.path.exists(out_dir):
                os.makedirs(out_dir)
            result["FilesToEncrypt"]["OutputFolder"] = out_dir
            yaml_dir = os.path.join(package_path, "axprotector_yaml")
            if not os.path.exists(yaml_dir):
                os.makedirs(yaml_dir)
            with open(f'codemeter/axprotector_yaml/protect_folder_{t}.yaml', 'w+', encoding='utf-8') as f:
                yaml.dump(data=result, stream=f, allow_unicode=True)
            a = os.getenv("AXPROTECTOR_PYTHON_SDK")
            command = f"python {a}  codemeter/axprotector_yaml/protect_folder_{t}.yaml"
            command_list.append(command)
            t += 1


def handle_package(command):
    """
    执行单条命令
    :param command: 需要被执行的命令
    :return: 无
    """

    try:
        val = os.system(command)
        if val == 0:
            logging.warning("执行:{}成功".format(command))
        with _lock:
            global num
            num += 1
            logging.warning("完成了{}/{}".format(num, all_num))
    except Exception as e:
        logging.error("执行:{},失败:{}".format(command, e), exc_info=True)
    finally:
        return


def execute(max_workers=2):
    global all_num
    all_num = len(command_list)
    pool = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        for command in command_list:
            print(command)
            t = executor.submit(handle_package, command=command)
            pool.append(t)
        for p in pool:
            p.result()


# 移动编译后的文件至指定目录
def mv_to_packages(path):
    pathes = os.listdir(path)
    for p in pathes:
        if p in ignore_move:
            continue
        f_path = os.path.join(path, p)
        if f_path == package_path:
            continue
        p_f_path = f_path.replace(BASE_DIR, package_path)
        if os.path.isdir(f_path):
            if not os.path.exists(p_f_path):
                os.mkdir(p_f_path)
            mv_to_packages(f_path)
        else:
            if not f_path.endswith('.py'):
                with open(f_path, 'rb') as f:
                    content = f.read()
                    with open(p_f_path, 'wb') as f:
                        f.write(content)


def run():
    translate_dir(BASE_DIR)
    execute(max_workers=4)
    mv_to_packages(BASE_DIR)


if __name__ == '__main__':
    run()
