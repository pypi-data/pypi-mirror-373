# # 导入setuptools模块，用于打包和分发Python项目
# # 导入re模块，用于正则表达式操作
# import re

# # 导入requests模块，用于发送HTTP请求
# import requests
# import setuptools
# # 导入BeautifulSoup模块，用于解析HTML文档
# from bs4 import BeautifulSoup

# package_name = "docualgo"


# def curr_version():
#     """
#     参数：无
#     返回值：当前官网上最新的版本号，格式为x.y.z
#     原理是从PyPi网站上面获取最新的版本号
#     """

#     # 从官网获取版本号
#     # 定义URL，使用f-string格式化字符串，将package_name插入URL中
#     url = f"https://pypi.org/project/{package_name}/"
#     # url = f"https://test.pypi.org/project/{package_name}/"

#     # 请求头

#     # headers = {
#     #     "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36 Edg/127.0.0.0"
#     # }
#     # # 发送GET请求，获取响应
#     # response = requests.get(url, headers=headers)

#     # # 检查是否响应成功
#     # if response.status_code == 200:
#     #     try:
#     #         print(f"成功获取官网的{package_name}的响应，响应code：{response.status_code}")
#     #         # 使用BeautifulSoup解析响应内容
#     #         soup = BeautifulSoup(response.content, "html.parser")

#     #         print(f"获取到的soup内容是：{soup}")

#     #         # 使用CSS选择器，选择.release__version类下的第一个元素，获取其文本内容，并去除首尾空格
#     #         latest_version = soup.select_one(".release__version").text.strip()
#     #         # print(f"当前PyPi上面的最新的版本号是：{latest_version}")
#     #         # 返回最新版本号

#     #         return str(latest_version)
#     #     except Exception as e:
#     #         print(f"test.pypi获取{package_name}的响应失败，错误信息：{e}")
#     #         print(
#     #             f"test.pypi获取{package_name}的响应失败，状态码：{response.status_code}，尝试从文件中获取版本号"
#     #         )
#     #         # 通过文件的存储版本号
#     #         with open("version.txt", "r", encoding="utf-8") as f:
#     #             # 读取所有行
#     #             lines = f.readlines()
#     #         # 获取最后一行
#     #         latest_version = lines[-1]
#     #         # 打印最新版本号
#     #         print(latest_version)
#     #         return str(latest_version)
#     #     pass

#     # 通过文件的存储版本号
#     with open("version.txt", "r", encoding="utf-8") as f:
#         # 读取所有行
#         lines = f.readlines()
#     # 获取最后一行
#     latest_version = lines[-1]
#     # 打印最新版本号
#     print(latest_version)

#     # latest_version = '0.2.2'

#     return str(latest_version)

#     pass


# def get_version():
#     """
#     参数：无
#     返回值：由官网上的最新的版本好计算出当前最新的版本号，格式为x.y.z
#     """

#     # 从版本号字符串中提取三个数字并将它们转换为整数类型
#     # 使用正则表达式匹配当前版本号
#     match = re.search(r"(\d+)\.(\d+)\.(\d+)", curr_version())
#     # 将匹配到的第一个数字转换为整数，作为主版本号
#     major = int(match.group(1))
#     # 将匹配到的第二个数字转换为整数，作为次版本号
#     minor = int(match.group(2))
#     # 将匹配到的第三个数字转换为整数，作为补丁号
#     patch = int(match.group(3))

#     # 对三个数字进行加一操作
#     patch += 1
#     # 如果patch大于9，则将patch置为0，并将minor加一
#     if patch > 9:
#         patch = 0
#         minor += 1
#         # 如果minor大于9，则将minor置为0，并将major加一
#         if minor > 9:
#             minor = 0
#             major += 1
#     # 将major、minor、patch拼接成新的版本号字符串
#     new_version_str = f"{major}.{minor}.{patch}"
#     # 返回新的版本号字符串

#     # # # 手动指定版本号
#     # new_version_str = '0.2.1'

#     return new_version_str


# def upload():
#     # 打开README.md文件，以只读模式读取文件内容
#     with open("README.md", "r", encoding="utf-8", errors="ignore") as fh:
#         long_description = fh.read()
#     # 打开requirements.txt文件，读取文件内容，并按行分割
#     with open("requirements.txt", encoding="utf-8", errors="ignore") as f:
#         required = f.read().splitlines()

#     setuptools.setup(
#         name=package_name,
#         version=get_version(),
#         author="宇千思",  # 作者名称
#         author_email="",  # 作者邮箱
#         description="Python helper tools",  # 库描述
#         long_description=long_description,  # 设置长描述
#         long_description_content_type="text/markdown",  # 设置长描述的内容类型为Markdown
#         url="https://pypi.org/project/docualgo/",  # 库的官方地址
#         # 查找项目中的所有包
#         packages=setuptools.find_packages(include=["docualgo", "docualgo.*"]),
#         data_files=["requirements.txt"],  # docualgo库依赖的其他库
#         classifiers=[
#             "License :: OSI Approved :: Apache Software License",  # 授权协议
#         ],
#         # 指定Python版本要求，这里要求Python版本大于等于
#         python_requires=">=3.6",
#         # 指定安装依赖，这里使用required变量，该变量应该是一个包含所有依赖的列表
#         install_requires=required,
#     )


# # 定义一个函数，用于写入当前版本号
# def write_now_version():
#     # 打开名为VERSION的文件，以写入模式
#     with open("version.txt", "a", encoding="utf-8", errors="ignore") as version_f:
#         # 将当前版本号写入文件
#         version_f.write(get_version())
#         # 写完后换行
#         version_f.write("\n")
#         pass


# def main():
#     try:
#         # 尝试执行上传操作
#         upload()
#         write_now_version()
#         # 打印上传成功信息，并显示当前版本号
#         print("已经成功准备好包，可以进行打包操作, 更新后的最新版本号将是:", get_version())
#     except Exception as e:
#         # 如果上传过程中出现异常，则抛出异常，并显示异常信息
#         raise Exception("上传出现异常", e)


# if __name__ == "__main__":
#     main()
#     pass


# 说明：
# 1. 程序首先尝试从官网获取最新版本号，如果失败则从 version.txt 文件中获取最后一行符合 x.y.z 格式的版本号，
#    并输出“文件当前版本: 当前版本号”。
# 2. 版本号的更新规则为：基于当前版本号的补丁号加 1（当补丁号超过 9 时，进位至次版本号；依此类推）。
# 3. 允许通过命令行手动指定版本号，使用指令：python setup.py --manual-version=1.2.3
#    手动指定后，程序将直接使用该版本号，不再自动计算。


import re
import sys

import setuptools
from bs4 import BeautifulSoup

package_name = "docualgo"
_current_version_cache = None
manual_version = None


def curr_version():
    """
    获取当前版本号：
    首先尝试从官网获取，如果出错则从 version.txt 文件中读取最后一行符合 x.y.z 格式的版本号，
    并输出文件当前版本。
    """
    import requests

    global _current_version_cache
    if _current_version_cache is not None:
        return _current_version_cache

    url = f"https://pypi.org/project/{package_name}/"
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/127.0.0.0 Safari/537.36 Edg/127.0.0.0"
        )
    }
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, "html.parser")
            latest_version = soup.select_one(".release__version").text.strip()
            _current_version_cache = latest_version
            return _current_version_cache
    except Exception as e:
        print("官网获取失败，报错信息为{e}，尝试从version.txt文件中读取版本号")
        pass

    # 官网获取失败，从 version.txt 中读取
    with open("version.txt", "r", encoding="utf-8") as f:
        valid_lines = [
            line.strip().lstrip("\ufeff")
            for line in f
            if re.match(r"^\d+\.\d+\.\d+$", line.strip().lstrip("\ufeff"))
        ]
    if not valid_lines:
        raise ValueError("version.txt文件中没有有效版本号")
    _current_version_cache = valid_lines[-1]
    print(f"文件当前版本: {_current_version_cache}")
    return _current_version_cache


def get_version():
    """
    根据当前版本号计算更新后的版本号（x.y.z格式）。
    如果通过命令行手动指定了版本号，则直接返回该版本号。
    """
    global manual_version
    if manual_version:
        return manual_version

    current_ver = curr_version().strip()
    match = re.search(r"(\d+)\.(\d+)\.(\d+)", current_ver)
    if not match:
        raise ValueError("版本号格式不正确")
    major, minor, patch = int(match.group(1)), int(match.group(2)), int(match.group(3))
    patch += 1
    if patch > 9:
        patch = 0
        minor += 1
        if minor > 9:
            minor = 0
            major += 1
    return f"{major}.{minor}.{patch}"


def upload():
    with open("README.md", "r", encoding="utf-8", errors="ignore") as fh:
        long_description = fh.read()
    with open("requirements.txt", encoding="utf-8", errors="ignore") as f:
        required = f.read().splitlines()

    setuptools.setup(
        name=package_name,
        version=get_version(),
        author="宇千思",
        author_email="",
        description="Python helper tools",
        long_description=long_description,
        long_description_content_type="text/markdown",
        url="https://pypi.org/project/docualgo/",
        packages=setuptools.find_packages(include=["docualgo", "docualgo.*"]),
        data_files=["requirements.txt"],
        # classifiers=[
        #     # "License :: OSI Approved :: Apache Software License",
        # ],
        # license="Apache-2.0",
        # license_files=["LICENSE"],
        python_requires=">=3.6",
        install_requires=required,
    )


def write_now_version():
    with open("version.txt", "a", encoding="utf-8", errors="ignore") as version_f:
        version_f.write(get_version() + "\n")


def main():
    global manual_version
    new_args = []
    for arg in sys.argv:
        if arg.startswith("--manual-version="):
            manual_version = arg.split("=", 1)[1]
            print(f"手动指定版本号: {manual_version}")
        else:
            new_args.append(arg)
    sys.argv = new_args

    try:
        upload()
        write_now_version()
        print(f"更新后的版本号: {get_version()}")
    except Exception as e:
        raise Exception("上传出现异常", e)


if __name__ == "__main__":
    main()
