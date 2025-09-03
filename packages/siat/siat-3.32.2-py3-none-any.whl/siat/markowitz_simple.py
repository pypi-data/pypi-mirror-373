# -*- coding: utf-8 -*-
"""
本模块功能：马科维茨投资组合快速示意图
所属工具包：证券投资分析工具SIAT 
SIAT：Security Investment Analysis Tool
创建日期：2023年7月8日
最新修订日期：2023年7月9日
作者：王德宏 (WANG Dehong, Peter)
作者单位：北京外国语大学国际商学院
作者邮件：wdehong2000@163.com
版权所有：王德宏
用途限制：仅限研究与教学使用，不可商用！商用需要额外授权。
特别声明：作者不对使用本工具进行证券投资导致的任何损益负责！
"""

#==============================================================================
#关闭所有警告
import warnings; warnings.filterwarnings('ignore')
from siat.security_prices import *

#==============================================================================
import matplotlib.pyplot as plt

#统一设定绘制的图片大小：数值为英寸，1英寸=100像素
plt.rcParams['figure.figsize']=(12.8,7.2)
plt.rcParams['figure.dpi']=300
plt.rcParams['font.size'] = 13
plt.rcParams['xtick.labelsize']=11 #横轴字体大小
plt.rcParams['ytick.labelsize']=11 #纵轴字体大小

title_txt_size=16
ylabel_txt_size=14
xlabel_txt_size=14
legend_txt_size=14

#设置绘图风格：网格虚线
plt.rcParams['axes.grid']=True
#plt.rcParams['grid.color']='steelblue'
#plt.rcParams['grid.linestyle']='dashed'
#plt.rcParams['grid.linewidth']=0.5
#plt.rcParams['axes.facecolor']='whitesmoke'

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

# 全局引用，函数中无需再import
from datetime import date
import pandas as pd 
import numpy as np 
import scipy.optimize as opt

import seaborn as sns
g=sns.set_style("whitegrid")#横坐标有标线，纵坐标没有标线，背景白色
g=sns.set_style("darkgrid") #默认，横纵坐标都有标线，组成一个一个格子，背景稍微深色
g=sns.set_style("dark")#背景稍微深色，没有标线线
g=sns.set_style("white")#背景白色，没有标线线
g=sns.set_style("ticks")#xy轴都有非常短的小刻度
g=sns.despine(offset=30,left=True)#去掉上边和右边的轴线，offset=30表示距离轴线（x轴）的距离,left=True表示左边的轴保留
g=sns.set(font='SimHei',rc={'figure.figsize':(10,6)})# 图片大小和中文字体设置

#==============================================================================
if __name__=='__main__':
    components = {
                  'AAPL':'苹果',
                  'AMZN':'亚马逊',
                  'GOOGL':'谷歌',
                  'BABA':'阿里巴巴'
                 }

    start='2022-1-1'    
    end='2022-12-31'
    
    risk_free=0.015
    simulation=25000
    price_trend=True
    feasible_set=True
    efficient_frontier=True
    MOP=True #Markowitz Optimized Point
    MSR=True #Maximized Sharpe Ratio
    
    ef_adjust=1.008
    
    markowitz_sharpe(components,start,end)
    markowitz_sharpe(components,start,end,ef_adjust=1.008)
    markowitz_sharpe(components,start,end,MOP=True)
    markowitz_sharpe(components,start,end,MSR=True)
    markowitz_sharpe(components,start,end,MOP=True,MSR=True)

def markowitz_sharpe(components,start,end,risk_free=0.015,simulation=25000, \
                     price_trend=True,feasible_set=True,efficient_frontier=True, \
                     MOP=False,MSR=False,ef_adjust=1.008): 
    """
    功能：使用期间内夏普比率寻找马科维茨最优点，绘制可行集、有效边界和最优点
    components：投资组合成分股票代码与名称，节省搜索股票名称的时间
    start,end：开始/结束日期
    risk_free：人工指定无风险利率，节省搜索时间，减少搜索失败概率
    simulation：生成可行集的模拟次数
    price_trend：是否绘制各个成分股票的价格走势，采用股价/起点股价的比值，可一图绘制多只股票
    feasible_set：是否绘制可行集
    efficient_frontier：是否绘制有效边界
    MOP：是否标注MOP点，Markowitz Optimized Point，可能与MSR点不同
    MSR：是否标注MSR点，Maximized Sharpe Ratio，可能与MOP点不同
    ef_adjust：对有效边界曲线微调，使其处于可行集的上边沿
    """
    #获取股票数据
    tickers=list(components)
    
    # 使用Adj Close避免分红分拆引起股价不连续导致结果异常
    #cprices=get_prices(tickers,start,end)
    stock_data=get_prices(tickers,start,end)['Adj Close']
    stock_data.rename(columns=components,inplace=True)
     
    stock_data=stock_data.iloc[::-1]
    #stock_data.head()
     
    # 绘制成分股价格走势，采用股价/起点股价的相对股价，增加可比性
    if price_trend:
        (stock_data/stock_data.iloc[0]).plot()
        titletxt='投资组合的成分股价格走势示意图'
        plt.xlabel('')
        plt.ylabel("价格/起点值")
        plt.title(titletxt)
        plt.show()
    
    #------------------------------------------------------------------------------
    # 计算收益率和风险
    # 收益率
    R=stock_data/stock_data.shift(1)-1
    #R.head()
    
    # 对数收益率 
    stock_data_shift1=stock_data.shift(1)
    log_r=np.log(stock_data/stock_data.shift(1))
    #log_r.head()
    
    # 年化收益率 
    r_annual=np.exp(log_r.mean()*250)-1
    #r_annual
    
    # 风险
    std = np.sqrt(log_r.var() * 250)#假设协方差为0
    #std
    
    #------------------------------------------------------------------------------
    # 投资组合的收益和风险
    def gen_weights(n):
        w=np.random.rand(n)
        return w /sum(w)
     
    n=len(list(tickers))
    #w=gen_weights(n)
    #list(zip(r_annual.index,w))
    
    #投资组合收益
    def port_ret(w):
        return -np.sum(w*r_annual)
    #pret=port_ret(w)
    
    #投资组合的风险
    def port_std(w):
        return np.sqrt((w.dot(log_r.cov()*250).dot(w.T)))
    #pstd=port_std(w)
    
    #若干投资组合的收益和风险
    def gen_ports(times):
        for _ in range(times):#生成不同的组合
            w=gen_weights(n)#每次生成不同的权重
            yield (port_std(w),port_ret(w),w)#计算风险和期望收益 以及组合的权重情况
    
    # 投资组合模拟次数
    print("\n  Generating portfolio feasible set ...")
    df=pd.DataFrame(gen_ports(25000),columns=["std","ret","w"])
    #df.head()
    std_min=df['std'].min()
    std_max=df['std'].max()
    
    #------------------------------------------------------------------------------
    #计算可行集中每个投资组合期间内的夏普比率
    df['sharpe'] = (df['ret'] - risk_free) / df['std']
    #list(zip(r_annual.index, df.loc[df.sharpe.idxmax()].w))
    
    # 画出投资可行集
    df_ef=df.rename(columns={'std':'收益率标准差','ret':'收益率','sharpe':'夏普比率'})
    fig, ax = plt.subplots()
    titletxt="马科维茨投资组合示意图"
    plt.title(titletxt)
    
    #df.plot.scatter('std','ret',c='sharpe',s=30,alpha=0.3,cmap='cool',marker='o',ax=ax)
    df_ef.plot.scatter('收益率标准差','收益率',c='夏普比率',s=30,alpha=0.3,cmap='cool',marker='o',ax=ax)
    plt.style.use('ggplot')
    plt.rcParams['axes.unicode_minus'] = False# 显示负号
    
    #绘制有效边界曲线    
    if efficient_frontier:
        frontier=pd.DataFrame(columns=['std','ret'])
        for std in np.linspace(std_min,std_max):    
            res=opt.minimize(lambda x:-port_ret(x),
                        x0=((1/n),)*n,
                        method='SLSQP',
                        bounds=((0,1),)*n,
                        constraints=[
                           {"fun":lambda x:port_std(x)-std,"type":"eq"},
                           {"fun":lambda x:(np.sum(x)-1),"type":"eq"}
                        ])
            if res.success:
                frontier=frontier._append({"std":std,"ret":-res.fun},ignore_index=True)
        
        # 略微上调有效边界
        frontier2=frontier.copy()
        """
        fstd0=frontier2['std'].values[0]
        frontier2['ret']=frontier2['ret'] * ef_adjust*fstd0/frontier2['std']
        """
        frontier2['ret']=frontier2['ret'] * ef_adjust
        frontier3=frontier2.rename(columns={'std':'收益率标准差','ret':'收益率'})
        frontier3.plot('收益率标准差','收益率',label='有效边界',lw=3,c='blue',ax=ax)
        plt.legend()
        fig
    
    #------------------------------------------------------------------------------
    #单个投资组合的收益和风险
    def one_ports(w):
        return (port_std(w),port_ret(w),w)#计算风险和期望收益 以及组合的权重情况
    
    # 计算最优资产配置情况
    if MOP:
        res=opt.minimize(lambda x:-((port_ret(x)-risk_free)/port_std(x)),
                        x0=((1/n),)*n,
                        method='SLSQP',
                        bounds=((0,1),)*n,
                        constraints={"fun":lambda x:(np.sum(x)-1), "type":"eq"})
        
        ax.scatter(port_std(res.x),port_ret(res.x),label='MOP点',marker="*",c="brown",s=300)
        ax.legend()
        fig
        
        print("\n***马科维茨优化后组合(MOP)配置:")
        ticker_names=components.values()
        best_proportion=res.x.round(3)
        #best_config = dict(zip(tickers, best_proportion))
        best_config = dict(zip(ticker_names, best_proportion))
        print(best_config)
        
        #计算期间内投资组合收益率均值
        best_std,best_ret,_=one_ports(best_proportion)
        print("收益率标准差:",round(best_std,4),"\b，投资组合收益率:",round(best_ret,4))
        
        """
        #绘制MOP组合价格走势
        stock_data2=stock_data.copy()
        stock_data2['MOP']=stock_data2.dot(best_proportion)
        (stock_data2/stock_data2.iloc[0]).plot()
        
        titletxt='投资组合及其成分股价格走势示意图'
        plt.xlabel('')
        plt.ylabel("价格/起点值")
        plt.title(titletxt)
        plt.show()
        """
        
    if MSR:
        sharpe_max=df['sharpe'].max()
        std_msr=df[df['sharpe']==sharpe_max]['std'].values[0]
        ret_msr=df[df['sharpe']==sharpe_max]['ret'].values[0]
        w_msr=df[df['sharpe']==sharpe_max]['w'].values[0]
        
        ax.scatter(std_msr,ret_msr,label='MSR点',marker="*",c="orange",s=300)
        ax.legend()
        fig
        
        print("\n***最大夏普比率组合(MSR)配置:")    
        ticker_names=components.values()
        best_proportion=w_msr
        best_config = dict(zip(ticker_names, best_proportion.round(3)))
        print(best_config)
        
        #计算期间内投资组合收益率均值
        best_std,best_ret,_=one_ports(best_proportion)
        print("收益率标准差:",round(best_std,4),"\b，投资组合收益率:",round(best_ret,4))
        
        #绘制MOP组合价格走势
        """
        stock_data3=stock_data.copy()
        stock_data3['MOP']=stock_data3.dot(best_proportion)
        (stock_data3/stock_data3.iloc[0]).plot()
        
        titletxt='投资组合及其成分股价格走势示意图'
        plt.xlabel('')
        plt.ylabel("价格/起点值")
        plt.title(titletxt)
        plt.show()
        """
        
    if MOP or MSR:
        std_min=df['std'].min()
        ret_gmvs=df[df['std']==std_min]['ret'].values[0]
        w_gmvs=df[df['std']==std_min]['w'].values[0]
        
        ax.scatter(std_min,ret_gmvs,label='LVS点',marker="o",c="green",s=300)
        ax.legend()
        fig
        
        print("\n***最小波动风险组合(LVS)配置:")    
        ticker_names=components.values()
        best_proportion=w_gmvs
        best_config = dict(zip(ticker_names, best_proportion.round(3)))
        print(best_config)
        
        #计算期间内投资组合收益率均值
        best_std,best_ret,_=one_ports(best_proportion)
        print("收益率标准差:",round(best_std,4),"\b，投资组合收益率:",round(best_ret,4))
        
        #绘制GMVS组合价格走势
        """
        stock_data4=stock_data.copy()
        stock_data4['GMVS']=stock_data4.dot(best_proportion)
        (stock_data4/stock_data4.iloc[0]).plot()

        titletxt='投资组合及其成分股价格走势示意图'
        plt.xlabel('')
        plt.ylabel("价格/起点值")
        plt.title(titletxt)
        plt.show()
        """
        
    return 


#------------------------------------------------------------------------------
#------------------------------------------------------------------------------
#------------------------------------------------------------------------------
#------------------------------------------------------------------------------
#------------------------------------------------------------------------------
#------------------------------------------------------------------------------
#------------------------------------------------------------------------------
#------------------------------------------------------------------------------
#------------------------------------------------------------------------------
#------------------------------------------------------------------------------
#------------------------------------------------------------------------------



















