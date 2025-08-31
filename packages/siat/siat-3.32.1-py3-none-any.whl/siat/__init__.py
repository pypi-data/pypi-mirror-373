# -*- coding: utf-8 -*-
"""
功能：一次性引入SIAT的所有模块
作者：王德宏，北京外国语大学国际商学院
版权：2021-2025(C) 仅限教学使用，商业使用需要授权
联络：wdehong2000@163.com
"""

#==============================================================================
#屏蔽所有警告性信息
import warnings; warnings.filterwarnings('ignore')
#==============================================================================
from siat.allin import *

import pkg_resources
current_version=pkg_resources.get_distribution("siat").version
#current_list=current_version.split('.')

#==============================================================================
# 处理stooq.py修复问题
restart=False
tagfile='fix_package.pkl'

#判断操作系统
import sys; czxt=sys.platform
if czxt in ['win32','win64']:
    os='windows'
elif czxt in ['darwin']: #MacOSX
    os='mac'
elif czxt in ['linux']: #linux
    os='linux'
else:
    os='windows'

# 确定标记文件存放地址
import pandas
srcpath=pandas.__path__[0]
if os == 'windows':
    srcpath1=srcpath.replace("\\",'/')
    srcfile=srcpath1+'/'+tagfile
else:
    srcpath1=srcpath
    srcfile=srcpath1+'/'+tagfile

try:
    with open(srcfile,'rb') as file:
        siat_ver=pickle.load(file)
        if siat_ver != current_version:
            restart=True
            with open(srcfile,'wb') as file:
                pickle.dump(current_version,file)
except:
    restart=True
    with open(srcfile,'wb') as file:
        pickle.dump(current_version,file)

#屏蔽函数内print信息输出的类
import os, sys
class HiddenPrints:
    def __enter__(self):
        self._original_stdout = sys.stdout
        sys.stdout = open(os.devnull, 'w')

    def __exit__(self, exc_type, exc_val, exc_tb):
        sys.stdout.close()
        sys.stdout = self._original_stdout

if not restart:
    print("  Successfully enabled siat v{}".format(current_version))
else:
    with HiddenPrints():
        fix_package()
    print("  A new version of siat installed, please RESTART Python kernel")

#==============================================================================
