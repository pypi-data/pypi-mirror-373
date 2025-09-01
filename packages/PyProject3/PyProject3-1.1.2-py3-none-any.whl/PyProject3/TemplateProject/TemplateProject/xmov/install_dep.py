import os
import sys
import subprocess
import tempfile

if os.name != "nt":
    print("不支持的操作系统", os.name)
    input("按回车键退出程序")
    sys.exit(0)


PKG_SOURCE_PATH = [
    r"T:\Xuhui_Public\python36_packages",
    r"python36_packages",
]


def get_install_cmd(requirements, cache_path):

    install_cmd = [sys.executable, "-m", "pip", "install", "--upgrade"]
    install_cmd.extend(["-r", requirements])
    install_cmd.extend(["--no-index", "-f", cache_path])
    return install_cmd


if __name__ == "__main__":
    CACHE_PATH = None
    if len(sys.argv) > 1:
        PKG_SOURCE_PATH.extend(sys.argv[1:])
    for path in PKG_SOURCE_PATH:
        if os.path.isdir(path):
            CACHE_PATH = path
            break
    if CACHE_PATH is None:
        input("找不到安装目录，请检查安装目录是否存在 \n\n\n按回车键退出本程序")
        sys.exit(0)
    REQUIREMENTS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "requirements.txt")
    if not os.path.isfile(REQUIREMENTS):
        input("找不到依赖文件，请检查文件是否存在 requrements\n\n\n按回车键退出本程序" % REQUIREMENTS)
        sys.exit(0)
    CMD = get_install_cmd(REQUIREMENTS, CACHE_PATH)
    try:
        print("即将执行命令：\n\n", " ".join(CMD))
        subprocess.check_call(CMD)
        print("命令已经执行成功:\n\n\n")
    except subprocess.CalledProcessError as exc:
        print("执行命令时发生错误\n\n\n", exc)
    input("按回车键退出程序")
