# -*- coding: utf-8 -*-
"""
TinyShare - A lightweight wrapper for tushare financial data API
"""

__version__ = "0.1013.0"

# 动态加载字节码模块
import sys
import os
import shutil
from pathlib import Path

def get_python_version_short():
    """获取当前Python版本的短格式，如 3.9 -> 39"""
    major, minor = sys.version_info[:2]
    return "{}{}".format(major, minor)

version_short = get_python_version_short()

# print(f"当前Python版本: {version_short}")

# 获取当前包目录
_pkg_dir = Path(__file__).parent
folderName = f"py{version_short}"

_main_pyc = _pkg_dir / "__init__.pyc"

# 如果根目录下没有__init__.pyc文件，把folder目录中所有pyc文件复制到根目录下
if not _main_pyc.exists():
    # print(f"根目录下没有__init__.pyc文件，开始复制文件...")
    _folder = _pkg_dir / folderName
    for file in os.listdir(_folder):
        if file.endswith('.pyc'):
            shutil.copy(_folder / file, _pkg_dir / file)
            # print(f"复制文件: {file}")

# 加载主模块字节码

if _main_pyc.exists():
    # print(_main_pyc)
    # print(f"找到Python {version_short}版本的字节码文件，开始加载...")
    # 使用exec直接执行字节码文件
    with open(_main_pyc, 'rb') as f:
        bytecode = f.read()
    
    # 创建代码对象并执行
    import marshal
    import types
    
    # 跳过.pyc文件头部信息（通常是16字节）
    code_offset = 16
    if len(bytecode) > code_offset:
        try:
            code_obj = marshal.loads(bytecode[code_offset:])
            exec(code_obj, globals())
        except Exception as e:
            print(f"字节码加载失败: {e}")
            # 如果字节码加载失败，尝试导入原始模块
            try:
                from . import *
            except ImportError:
                pass
else:
    # 如果没有字节码文件，尝试导入原始模块
    try:
        from . import *
    except ImportError:
        pass
