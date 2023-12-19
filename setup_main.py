import logging
import os
import threading
from concurrent.futures import ThreadPoolExecutor

# 项目根目录下不用（能）转译的py文件（夹）名，用于启动的入口脚本文件一定要加进来
ignore_files = [
    'nuitka_build.py', "nuitka_build", "cython_build", 'setup_main.py', 'setup.py', 'venv', "env", 'manage.py'
]
# 不需要原样复制到编译文件夹的文件或者文件夹
ignore_move = ['venv', 'env', ".git", ".idea", '__pycache__', 'setup.py', 'setup_main.py', "nuitka_build.py", "nuitka_build", "cython_build"
               "README.md", ".env_example"]
# 需要编译的文件夹绝对路径
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# 将以上不需要转译的文件(夹)加上绝对路径
ignore_files = [os.path.join(BASE_DIR, x) for x in ignore_files]
# 打包文件夹名
package_name = "cython_build"
# 打包文件夹路径
package_path = os.path.join(BASE_DIR, package_name)
# 若没有打包文件夹，则生成一个
if not os.path.exists(package_path):
    os.mkdir(package_path)
translate_pys = []
# 多并发统计进度需要一个锁,如果这里不统计我们不需要锁
_lock = threading.Lock()
num = 0
all_num = 0
command_list = []


# 编译需要的py文件
def translate_dir(path):
    global command_list
    pathes = os.listdir(path)
    for p in pathes:
        # if p.startswith('__') or p.startswith('.') or p.startswith('build'):
        #     continue
        if p.startswith('__') or p.startswith('build'):
            if p != "__init__.py":
                continue
        f_path = os.path.join(path, p)
        if f_path in ignore_files:
            continue
        if os.path.isdir(f_path):
            translate_dir(f_path)
        else:
            if not f_path.endswith('.py') and not f_path.endswith('.pyx'):
                continue
            # if f_path.endswith('__init__.py') or f_path.endswith('__init__.pyx'):
            #     continue
            with open(f_path, 'r', encoding='utf8') as f:
                content = f.read()
                if not content.startswith('# cython: language_level=3'):
                    content = '# cython: language_level=3\n' + content
                    with open(f_path, 'w', encoding='utf8') as f1:
                        f1.write(content)
            command_list.append('python setup.py ' + f_path + ' build_ext --inplace')
            translate_pys.append(f_path)


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


# 移除编译临时文件
def remove_dir(path, rm_path=True):
    if not os.path.exists(path):
        return
    pathes = os.listdir(path)
    for p in pathes:
        f_path = os.path.join(path, p)
        if os.path.isdir(f_path):
            remove_dir(f_path, False)
            os.rmdir(f_path)
        else:
            os.remove(f_path)
    if rm_path:
        os.rmdir(path)


# 移动编译后的文件至指定目录
def mv_to_packages(path=BASE_DIR):
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
            # if not f_path.endswith('.py') or f_path not in translate_pys:
            if f_path not in translate_pys:
                with open(f_path, 'rb') as f:
                    content = f.read()
                    with open(p_f_path, 'wb') as f:
                        f.write(content)
            if f_path.endswith('.pyd') or f_path.endswith('.so'):
                os.remove(f_path)


# 将编译后的文件重命名成：源文件名+.pyd，否则编译后的文件名会类似：myUtils.cp39-win_amd64.pyd
def batch_rename(src_path):
    filenames = os.listdir(src_path)
    same_name = []
    count = 0
    for filename in filenames:
        old_name = os.path.join(src_path, filename)
        if old_name == package_path:
            continue
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


def batch_remove():
    for f_path in translate_pys:
        f_name = '.'.join(f_path.split('.')[:-1])
        py_file = '.'.join([f_name, 'py'])
        c_file = '.'.join([f_name, 'c'])
        print(f"f_path: {f_path}, c_file: {c_file}, py_file: {py_file}")
        if os.path.exists(c_file):
            os.remove(c_file)


def run():
    translate_dir(BASE_DIR)
    execute(max_workers=4)
    remove_dir(os.path.join(BASE_DIR, 'build'))
    mv_to_packages()
    batch_remove()
    batch_rename(os.path.join(BASE_DIR, package_name))


if __name__ == '__main__':
    run()
