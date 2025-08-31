# -*- coding: utf-8 -*-

"""
本模块功能：债券，仅用于中国，目前针对交易所债券，仿照股票分析模式
所属工具包：证券投资分析工具SIAT 
SIAT：Security Investment Analysis Tool
创建日期：2023年5月25日
最新修订日期：2023年5月25日
作者：王德宏 (WANG Dehong, Peter)
作者单位：北京外国语大学国际商学院
版权所有：王德宏
用途限制：仅限研究与教学使用，不可商用！商用需要额外授权。
特别声明：作者不对使用本工具进行证券投资导致的任何损益负责！

注意：未完工，暂不使用！
"""

#==============================================================================
#关闭所有警告
import warnings; warnings.filterwarnings('ignore')
from siat.grafix import *
from siat.common import *
from siat.translate import *
from siat.bond_base import *
from siat.bond import *
from siat.stock import *
from siat.security_prices import *
from siat.security_price2 import *
#==============================================================================
import matplotlib.pyplot as plt
#plt.rcParams['figure.figsize']=(12.8,7.2)
plt.rcParams['figure.figsize']=(12.8,6.4)
plt.rcParams['figure.dpi']=300
plt.rcParams['font.size'] = 13
plt.rcParams['xtick.labelsize']=11 #横轴字体大小
plt.rcParams['ytick.labelsize']=11 #纵轴字体大小

title_txt_size=16
ylabel_txt_size=14
xlabel_txt_size=14
legend_txt_size=14

#处理绘图汉字乱码问题
import sys; czxt=sys.platform
if czxt in ['win32','win64']:
    plt.rcParams['font.sans-serif'] = ['SimHei']  # 设置默认字体
    mpfrc={'font.family': 'SimHei'}

if czxt in ['darwin']: #MacOSX
    plt.rcParams['font.family']= ['Heiti TC']
    mpfrc={'font.family': 'Heiti TC'}

if czxt in ['linux']: #website Jupyter
    plt.rcParams['font.family']= ['Heiti TC']
    mpfrc={'font.family':'Heiti TC'}

# 解决保存图像时'-'显示为方块的问题
plt.rcParams['axes.unicode_minus'] = False 
#==============================================================================
if __name__ =="__main__":
    ticker="010107.SS"
    ticker="102229.SZ"
    ticker2symbol(ticker)

def ticker2symbol(ticker):
    """
    功能：将xxxxxx.SS格式转换为shxxxxxx
    """
    ticker1=ticker.upper()
    exchTag=ticker1[-3:]
    bondCode=ticker1[:-3]

    exchList=['.SS','.SZ']
    if not (exchTag in exchList):
        print("  #Error(): unsupported type of exchange for bond",ticker)
        print("  Supported exchange bond suffix:",exchList) 
        return None
    
    if exchTag=='.SS':
        symbol='sh'+bondCode
    
    if exchTag=='.SZ':
        symbol='sz'+bondCode

    return symbol

#==============================================================================
if __name__ =="__main__":
    ticker="010107.SS"
    fromdate="2023-1-1"
    todate="2023-5-20"
    rtype="Daily Ret%"
    datatag=False
    power=3
    retinfo=exchbond_ret(ticker,fromdate,todate,power=power)





