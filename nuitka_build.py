import os
import sys
import shutil
import logging
import time
import threading
from concurrent.futures import ThreadPoolExecutor

if sys.platform.startswith("win"):
    command_base = " {}  -m nuitka --mingw64  --module --remove-output --output-dir={}  {}"
    max_workers = 8
    python_path = "python"
else:
    command_base = " {}  -m nuitka  --module --remove-output --output-dir={}  {}"
    max_workers = 8
    python_path = "python3"

# 项目根目录下不用（能）转译的py文件（夹）名，用于启动的入口脚本文件一定要加进来
ignore_files = [
    'nuitka_build.py', "nuitka_build", "cython_build", 'setup_main.py', 'setup.py', 'venv', "env", 'manage.py'
]
# 不需要原样复制到编译文件夹的文件或者文件夹
ignore_move = ['venv', 'env', ".git", ".idea", '__pycache__', 'setup.py', 'setup_main.py', "nuitka_build.py", "nuitka_build", "cython_build",
               "README.md", ".env_example"]
# # 以下文件或者目录是不需要打包的,只要是文件包含以下字段,均不打包
no_need_file = ("__init__.py")
# 需要编译的文件夹绝对路径
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# 将以上不需要转译的文件(夹)加上绝对路径
# ignore_files = [os.path.join(BASE_DIR, x) for x in ignore_files]
# 打包文件夹名
package_name = "nuitka_build"
# 打包文件夹路径
package_path = os.path.join(BASE_DIR, package_name)
# 若没有打包文件夹，则生成一个
if not os.path.exists(package_path):
    os.mkdir(package_path)
# 多并发统计进度需要一个锁,如果这里不统计我们不需要锁
_lock = threading.Lock()
num = 0
all_num = 0


def _copy(srt_file, dst_file):
    """
    将srt_file拷贝到dst_file
    :param srt_file:原始绝对路径
    :param dst_file: 目标绝对路径
    :return:
    """
    try:
        # 使用shutil进行拷贝,文件与目录的拷贝方法不一样,因此需要分别进行判断
        if os.path.isfile(srt_file):
            shutil.copy(srt_file, dst_file)
        elif os.path.isdir(srt_file):
            shutil.copytree(srt_file, dst_file)
        else:
            pass
        logging.warning("拷贝:{}到{}".format(srt_file, dst_file))
    except Exception as e:
        logging.error("拷贝{}到{}失败：{}".format(srt_file, dst_file, e), exc_info=True)
    return


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


def main(max_workers=1):
    t1 = time.time()
    command_list = []
    # 每次打包之前先删除目标目录
    if os.path.exists(package_path):
        shutil.rmtree(package_path)
    # 然后递归创建此目录
    if not os.path.exists(package_path):
        os.makedirs(package_path)
    logging.warning("当前目录为：{}".format(BASE_DIR))

    for i in os.listdir(BASE_DIR):
        srt_file = os.path.join(BASE_DIR, i)
        if i in ignore_files:
            if i not in ignore_move:
                dst_file = os.path.join(package_path, i)
                _copy(srt_file, dst_file)
        else:
            if os.path.isfile(srt_file):
                if i.endswith(".py") and i not in no_need_file:
                    command = command_base.format(python_path, package_path, srt_file)
                    command_list.append(command)
                elif i not in ignore_move:
                    dst_file = os.path.join(package_path, i)
                    _copy(srt_file, dst_file)
            else:
                if i in ignore_move:
                    continue
                for root, dirs, files in os.walk(srt_file, topdown=False):
                    if sys.platform.startswith("win"):
                        if root.split("\\")[-1] in ignore_move:
                            continue
                    else:
                        if root.split("/")[-1] in ignore_move:
                            continue
                    for name in files:
                        new_root = root.replace(BASE_DIR, package_path)
                        srt_file = os.path.join(root, name)
                        if not os.path.exists(new_root):
                            os.makedirs(new_root)
                        if not name.endswith(".py") or name in no_need_file:
                            # 不需要打包的直接拷贝即可
                            dst_file = os.path.join(new_root, name)
                            _copy(srt_file, dst_file)
                        else:
                            command = command_base.format(python_path, new_root, srt_file)
                            command_list.append(command)
    logging.warning("总共需要打包：{}个".format(len(command_list)))
    global all_num
    all_num = len(command_list)
    pool = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        for command in command_list:
            t = executor.submit(handle_package, command=command)
            pool.append(t)
        for p in pool:
            p.result()
    cost = time.time() - t1
    batch_rename(package_path)
    batch_delete(package_path)
    minute, second = divmod(cost, 60)
    logging.warning(
        "共计打包：{}个文件，此次导出共花费了:{}分{}秒,平均每秒{}个导出".format(len(command_list), minute, second,
                                                                              round((len(command_list) / cost), 2)))
    return


def batch_rename(src_path):
    filenames = os.listdir(src_path)
    same_name = []
    count = 0
    for filename in filenames:
        old_name = os.path.join(src_path, filename)
        if os.path.isdir(old_name):
            batch_rename(old_name)
        if filename[-4:] == ".pyd" or filename[-3:] == ".so":
            old_pyd = filename.split(".")
            new_pyd = str(old_pyd[0]) + "." + str(old_pyd[2])
        else:
            continue
        change_name = new_pyd
        count += 1
        new_name = os.path.join(src_path, change_name)
        if change_name in filenames:
            same_name.append(change_name)
            continue
        os.rename(old_name, new_name)


def batch_delete(src_path):
    filenames = os.listdir(src_path)
    for filename in filenames:
        old_name = os.path.join(src_path, filename)
        if os.path.isdir(old_name):
            batch_delete(old_name)
        if filename[-4:] == ".pyi":
            os.remove(old_name)
        else:
            continue


if __name__ == '__main__':
    main(max_workers=max_workers)
