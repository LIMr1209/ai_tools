import os
import sys
import shutil
import logging
import time
import threading
from concurrent.futures import ThreadPoolExecutor

# 想看内存和进度可以加上--show-memory --show-progress,由于我这里都是对单个py文件进行编码,避免太多打印,就没有加
# windows与linux命令不一样,因此分开构造,线程主要是看自身电脑配置,服务器配置高一些就可以多配置一点
# 由于linux下可能会有多个python,因此这里要配置绝对路径或者环境变量中的python3
if sys.platform.startswith("win"):
    command_base = " {}  -m nuitka --mingw64  --module --remove-output --output-dir={}  {}"
    max_workers = 2
    python_path = "python"
else:
    command_base = " {}  -m nuitka  --module --remove-output --output-dir={}  {}"
    max_workers = 8
    python_path = "python3"

# 这里是需要打包的目录
need_walk = ("app",)
# 这些文件是根目录下需要直接拷贝的,不打包的
need_copy_dir = ("checkpoint", ".env", "manage.py", "requirements.txt")
# 以下文件或者目录是不需要打包的,只要是文件包含以下字段,均不打包
no_need_file = ("__init__.py", "__pycache__", ".idea")
# 多并发统计进度需要一个锁,如果这里不统计我们不需要锁
_lock = threading.Lock()
num = 0


def check(path):
    """
    检查路径是否是包含了不打包的字段,如果包含,则返回一个True
    :param path: 需要被检查的路径
    :return:
    """
    for i in no_need_file:
        if i in path:
            return True
    return False


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


def main(max_workers=1, _current_path=None, end_dir=""):
    _current_path = _current_path or os.path.abspath(os.path.dirname(__file__))
    t1 = time.time()
    command_list = []
    # 每次打包之前先删除目标目录
    if os.path.exists(end_dir):
        shutil.rmtree(end_dir)
    # 然后递归创建此目录
    if not os.path.exists(end_dir):
        os.makedirs(end_dir)
    logging.warning("当前目录为：{}".format(_current_path))

    for i in os.listdir(_current_path):
        srt_file = os.path.join(_current_path, i)
        if i not in need_walk and i in need_copy_dir:
            # 不需要打包的直接拷贝即可
            dst_file = os.path.join(end_dir, i)
            _copy(srt_file, dst_file)

        elif i in need_walk:
            if not os.path.isdir(srt_file):
                continue
            for root, dirs, files in os.walk(srt_file, topdown=False):
                for name in files:
                    new_root = root.replace(_current_path, end_dir)
                    srt_file = os.path.join(root, name)
                    if not os.path.exists(new_root):
                        os.makedirs(new_root)
                    if not name.endswith(".py") or check(srt_file):
                        # 不需要打包的直接拷贝即可
                        dst_file = os.path.join(new_root, name)
                        _copy(srt_file, dst_file)
                    else:
                        command = command_base.format(python_path, new_root, srt_file)
                        command_list.append(command)
        else:
            pass
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
    batch_rename(end_dir)
    batch_delete(end_dir)
    minute, second = divmod(cost, 60)
    logging.warning("共计打包：{}个文件，此次导出共花费了:{}分{}秒,平均每秒{}个导出".format(len(command_list), minute, second,
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
    current_path = os.path.dirname(os.path.abspath(__file__))
    end_dir = os.path.join(current_path, "nuitka_build")
    main(_current_path=current_path, end_dir=end_dir, max_workers=max_workers)