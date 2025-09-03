# -*- coding: utf-8 -*-
"""
本模块功能：证券投资组合理论优化分析，手动输入RF版
所属工具包：证券投资分析工具SIAT 
SIAT：Security Investment Analysis Tool
创建日期：2024年4月19日
最新修订日期：2024年4月19日
作者：王德宏 (WANG Dehong, Peter)
作者单位：北京外国语大学国际商学院
作者邮件：wdehong2000@163.com
版权所有：王德宏
用途限制：仅限研究与教学使用，不可商用！商用需要额外授权。
特别声明：作者不对使用本工具进行证券投资导致的任何损益负责！
"""
#==============================================================================
#统一屏蔽一般性警告
import warnings; warnings.filterwarnings("ignore")   
#==============================================================================
  
from siat.common import *
from siat.translate import *
from siat.security_prices import *
from siat.security_price2 import *
#from siat.fama_french import *
from siat.stock import *

import pandas as pd
import numpy as np
import datetime
#==============================================================================
import seaborn as sns
import matplotlib.pyplot as plt
#统一设定绘制的图片大小：数值为英寸，1英寸=100像素
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

#设置绘图风格：网格虚线
plt.rcParams['axes.grid']=True
#plt.rcParams['grid.color']='steelblue'
#plt.rcParams['grid.linestyle']='dashed'
#plt.rcParams['grid.linewidth']=0.5
#plt.rcParams['axes.facecolor']='papayawhip'

#处理绘图汉字乱码问题
import sys; czxt=sys.platform
if czxt in ['win32','win64']:
    plt.rcParams['font.sans-serif'] = ['SimHei']  # 设置默认字体
    mpfrc={'font.family': 'SimHei'}
    sns.set_style('whitegrid',{'font.sans-serif':['simhei','Arial']})

if czxt in ['darwin','linux']: #MacOSX
    #plt.rcParams['font.family'] = ['Arial Unicode MS'] #用来正常显示中文标签
    plt.rcParams['font.family']= ['Heiti TC']
    mpfrc={'font.family': 'Heiti TC'}
    sns.set_style('whitegrid',{'font.sans-serif':['Arial Unicode MS','Arial']})


# 解决保存图像时'-'显示为方块的问题
plt.rcParams['axes.unicode_minus'] = False 
#==============================================================================
#全局变量定义
RANDOM_SEED=1234567890

#==============================================================================
def portfolio_config(tickerlist,sharelist):
    """
    将股票列表tickerlist和份额列表sharelist合成为一个字典
    """
    #整理sharelist的小数点
    ratiolist=[]
    for s in sharelist:
        ss=round(s,4); ratiolist=ratiolist+[ss]
    #合成字典
    new_dict=dict(zip(tickerlist,ratiolist))
    return new_dict

#==============================================================================
def ratiolist_round(sharelist,num=4):
    """
    将股票份额列表sharelist中的数值四舍五入
    """
    #整理sharelist的小数点
    ratiolist=[]
    for s in sharelist:
        ss=round(s,num); ratiolist=ratiolist+[ss]
    return ratiolist

#==============================================================================
def varname(p):
    """
    功能：获得变量的名字本身。
    """
    import inspect
    import re    
    for line in inspect.getframeinfo(inspect.currentframe().f_back)[3]:
        m = re.search(r'\bvarname\s*\(\s*([A-Za-z_][A-Za-z0-9_]*)\s*\)', line)
        if m:
            return m.group(1)    

#==============================================================================
if __name__=='__main__':
    end_date='2021-12-3'
    pastyears=3

def get_start_date(end_date,pastyears=1):
    """
    输入参数：一个日期，年数
    输出参数：几年前的日期
    start_date, end_date是datetime类型
    """
    import pandas as pd
    try:
        end_date=pd.to_datetime(end_date)
    except:
        print("  #Error(get_start_date): invalid date,",end_date)
        return None
    
    from datetime import datetime,timedelta
    start_date=datetime(end_date.year-pastyears,end_date.month,end_date.day)
    start_date=start_date-timedelta(days=1)
    # 日期-1是为了保证计算收益率时得到足够的样本数量
    
    start=start_date.strftime("%Y-%m-%d")
    
    return start

#==============================================================================
#==============================================================================
#==============================================================================
if __name__=='__main__':
    retgroup=StockReturns

def cumulative_returns_plot(retgroup,name_list="",titletxt="投资组合策略：业绩比较", \
                            ylabeltxt="持有收益率",xlabeltxt="", \
                            label_list=[],facecolor='papayawhip'):
    """
    功能：基于传入的name_list绘制多条持有收益率曲线，并从label_list中取出曲线标记
    注意：最多绘制四条曲线，否则在黑白印刷时无法区分曲线，以此标记为实线、点虚线、划虚线和点划虚线四种
    """
    if name_list=="":
        name_list=list(retgroup)
    
    if len(label_list) < len(name_list):
        label_list=name_list
    
    if xlabeltxt=="":
        #取出观察期
        hstart0=retgroup.index[0]
        #hstart=str(hstart0.date())
        hstart=str(hstart0.strftime("%Y-%m-%d"))
        hend0=retgroup.index[-1]
        #hend=str(hend0.date())
        hend=str(hend0.strftime("%Y-%m-%d"))
        
        lang = check_language()
        import datetime as dt; stoday=dt.date.today()
        if lang == 'Chinese':
            footnote1="观察期间: "+hstart+'至'+hend
            footnote2="\n数据来源：Sina/EM/Stooq/Yahoo，"+str(stoday)
        else:
            footnote1="Period of sample: "+hstart+' to '+hend
            footnote2="\nData source: Sina/EM/Stooq/Yahoo, "+str(stoday)
            
        xlabeltxt=footnote1+footnote2
    
    # 持有收益曲线绘制函数
    lslist=['-','--',':','-.']
    markerlist=['.','h','+','x','4','3','2','1']
    for name in name_list:
        pos=name_list.index(name)
        rlabel=label_list[pos]
        if pos < len(lslist): 
            thisls=lslist[pos]        
        else: 
            thisls=(45,(55,20))
        
        # 计算持有收益率
        CumulativeReturns = ((1+retgroup[name]).cumprod()-1)
        if pos-len(lslist) < 0:
            CumulativeReturns.plot(label=ectranslate(rlabel),ls=thisls)
        else:
            thismarker=markerlist[pos-len(lslist)]
            CumulativeReturns.plot(label=ectranslate(rlabel),ls=thisls,marker=thismarker,markersize=4)
            
    plt.axhline(y=0,ls=":",c="red")
    plt.legend(loc='best')
    plt.title(titletxt); plt.ylabel(ylabeltxt); plt.xlabel(xlabeltxt)
    
    plt.gca().set_facecolor(facecolor)
    plt.show()
    
    return

if __name__=='__main__':
    retgroup=StockReturns
    cumulative_returns_plot(retgroup,name_list,titletxt,ylabeltxt,xlabeltxt, \
                            label_list=[])

def portfolio_expret_plot(retgroup,name_list="",titletxt="投资组合策略：业绩比较", \
                            ylabeltxt="持有收益率",xlabeltxt="", \
                            label_list=[]):
    """
    功能：套壳函数cumulative_returns_plot
    """
    
    cumulative_returns_plot(retgroup,name_list,titletxt,ylabeltxt,xlabeltxt,label_list) 
    
    return

#==============================================================================
def portfolio_hpr(portfolio,thedate,pastyears=1, \
                  RF=0, \
                  printout=True,graph=True):
    """
    功能：套壳函数portfolio_build
    """
    dflist=portfolio_build(portfolio=portfolio,thedate=thedate,pastyears=pastyears, \
                           printout=printout,graph=graph)

    return dflist

#==============================================================================
if __name__=='__main__':
    #测试1
    Market={'Market':('US','^GSPC')}
    Market={'Market':('US','^GSPC','我的组合001')}
    Stocks1={'AAPL':.3,'MSFT':.15,'AMZN':.15,'GOOG':.01}
    Stocks2={'XOM':.02,'JNJ':.02,'JPM':.01,'TSLA':.3,'SBUX':.03}
    portfolio=dict(Market,**Stocks1,**Stocks2)
    
    #测试2
    Market={'Market':('China','000300.SS','养猪1号组合')}
    porkbig={'000876.SZ':0.20,#新希望
             '300498.SZ':0.15,#温氏股份
            }
    porksmall={'002124.SZ':0.10,#天邦股份
               '600975.SS':0.10,#新五丰
               '603477.SS':0.10,#巨星股份
               '000735.SZ':0.07,#罗牛山
              }
    portfolio=dict(Market,**porkbig,**porksmall)    

    #测试3
    Market={'Market':('China','000300.SS','股债基组合')}
    Stocks={'600519.SS':0.3,#股票：贵州茅台
            'sh010504':[0.5,'bond'],#05国债⑷
            '010504.SS':('fund',0.2),#招商稳兴混合C基金
            }
    portfolio=dict(Market,**Stocks)

    printout=True 
    graph=False
    
    indicator='Adj Close'
    adjust='qfq'; source='auto'; ticker_type='bond'
    thedate='2024-6-19'
    pastyears=2

    
    #测试3
    Market={'Market':('China','000300.SS','股债基组合')}
    Stocks={'600519.SS':0.3,#股票：贵州茅台
            'sh010504':[0.5,'bond'],#05国债⑷
            '010504.SS':('fund',0.2),#招商稳兴混合C基金
            }
    portfolio=dict(Market,**Stocks)

    indicator='Close'
    adjust=''; source='auto'; ticker_type='auto'
    thedate='2024-6-19'
    pastyears=1
    printout=True 
    graph=False
    
    
    pf_info=portfolio_build(portfolio,thedate,pastyears,printout,graph)

"""
def portfolio_cumret(portfolio,thedate,pastyears=1, \
                     RF=0, \
                     printout=True,graph=True):
"""
def portfolio_build(portfolio,thedate='default',pastyears=3, \
                    indicator='Adj Close', \
                    adjust='qfq',source='auto',ticker_type='auto', \
                    printout=False,graph=False,facecolor='papayawhip'):    
    """
    功能：收集投资组合成份股数据，绘制收益率趋势图，并与等权和期间内交易额加权策略组合比较
    注意：
    1. 此处无需RF，待到优化策略时再指定
    2. printout=True控制下列内容是否显示：
        获取股价时的信息
        是否显示原始组合、等权重组合和交易金额加权组合的成分股构成
        是否显示原始组合、等权重组合和交易金额加权组合的收益风险排名
    3. pastyears=3更有可能生成斜向上的椭圆形可行集，短于3形状不佳，长于3改善形状有限。
        需要与不同行业的证券搭配。同行业证券相关性较强，不易生成斜向上的椭圆形可行集。
    4. 若ticker_type='fund'可能导致无法处理股票的复权价！
    5. 若要指定特定的证券为债券，则需要使用列表逐一指定证券的类型（股票，债券，基金）
    6. 默认采用前复权计算收益率，更加平稳
    """
    #判断复权标志
    indicator_list=['Close','Adj Close']
    if indicator not in indicator_list:
        print("  Warning(portfolio_build): invalid indicator",indicator)
        print("  Supported indicator:",indicator_list)
        indicator='Adj Close'
    
    adjust_list=['','qfq','hfq']
    if adjust not in adjust_list:
        print("  Warning(portfolio_build): invalid indicator",adjust)
        print("  Supported adjust:",adjust_list)
        adjust='qfq'
    
    import datetime
    stoday = datetime.date.today()
    if thedate=='default':
        thedate=str(stoday)
    else:
        if not check_date(thedate):
            print("  #Warning(portfolio_build): invalid date",thedate)
            return None
    
    print("  Searching for portfolio info, which may take time ...")
    # 解构投资组合
    scope,_,tickerlist,sharelist0,ticker_type=decompose_portfolio(portfolio)
    pname=portfolio_name(portfolio)

    #如果持仓份额总数不为1，则将其转换为总份额为1
    import numpy as np
    totalshares=np.sum(sharelist0)
    if abs(totalshares - 1) >= 0.00001:
        print("  #Warning(portfolio_build): total weights is",totalshares,"\b, expecting 1.0 here")
        print("  Action taken: automatically converted into total weights 1.0")
        sharelist=list(sharelist0/totalshares) 
    else:
        sharelist=sharelist0

    #..........................................................................    
    # 计算历史数据的开始日期
    start=get_start_date(thedate,pastyears)
    
    #处理无风险利率，不再需要，但为兼容考虑仍保留，根据手动输入的RF构造rf_df以便后续改动量较小
    import pandas as pd
    date_series = pd.date_range(start=start,end=thedate,freq='D')
    rf_df=pd.DataFrame(index=date_series)
    rf_df['date']=rf_df.index
    rf_df['date']=rf_df['date'].apply(lambda x: x.strftime('%Y-%m-%d'))
    rf_df['RF']=RF=0
    rf_df['rf_daily']=RF/365
    """
    #一次性获得无风险利率，传递给后续函数，避免后续每次获取，耗费时间  
    if RF:
        rf_df=get_rf_daily(start,thedate,scope,rate_period,rate_type)
        #结果字段中，RF是日利率百分比，rf_daily是日利率数值
        if rf_df is None:
            #print("  #Error(portfolio_build): failed to retrieve risk-free interest rate in",scope)
            print("  #Warning: all subsequent portfolio optimizations cannot proceed")
            print("  Solution1: try again after until success to include risk-free interest rate in calculation")
            print("  Solution2: use RF=False in script command to ignore risk-free interest rate in calculation")
            return None
    else:
        rf_df=None
    """
    #..........................................................................
    import os, sys
    class HiddenPrints:
        def __enter__(self):
            self._original_stdout = sys.stdout
            sys.stdout = open(os.devnull, 'w')

        def __exit__(self, exc_type, exc_val, exc_tb):
            sys.stdout.close()
            sys.stdout = self._original_stdout
    
    # 抓取投资组合股价
    #prices=get_prices(tickerlist,start,thedate)
    #判断是否赚取复权价
    if indicator == 'Adj Close' and adjust == '':
        adjust='qfq'
    if indicator == 'Close' and adjust != '':
        indicator = 'Adj Close'
        
    if printout:
        #prices=get_prices_simple(tickerlist,start,thedate) #有待改造？
        #债券优先
        prices,found=get_price_mticker(tickerlist,start,thedate, \
                              adjust=adjust,source=source,ticker_type=ticker_type,fill=False)
    else:
        with HiddenPrints():
            #prices=get_prices_simple(tickerlist,start,thedate) #有待改造？
            prices,found=get_price_mticker(tickerlist,start,thedate, \
                                  adjust=adjust,source=source,ticker_type=ticker_type,fill=False)
                
    if found == 'Found':
        ntickers=len(list(prices['Close']))
        nrecords=len(prices)
        #print("  Successfully retrieved",ntickers,"stocks with",nrecords,"record(s) respectively")
        print("  Successfully retrieved prices of",ntickers,"securities for",pname)

        if ntickers != len(tickerlist):
            print("  However, failed to access some securities, unable to build portfolio",pname)
            return None
        
    #if prices is None:
    if found == 'None':
        print("  #Error(portfolio_build): failed to get portfolio prices",pname)
        return None
    #if len(prices) == 0:
    if found == 'Empty':
        print("  #Error(portfolio_build): retrieved empty prices for",pname)
        return None
    #..........................................................................
    #判断是否使用复权价：若是，使用Adj Close直接覆盖Close。方法最简单，且兼容后续处理！
    if (indicator =='Adj Close') or (adjust !=''):
        prices_collist=list(prices) 
        for pc in prices_collist:
            pc1=pc[0]; pc2=pc[1]
            if pc1=='Close':
                pc_adj=('Adj Close',pc2)
                prices[pc]=prices[pc_adj]
    
    # 取各个成份股的收盘价
    aclose=prices['Close']    
    member_prices=aclose
    # 计算各个成份股的日收益率，并丢弃缺失值
    StockReturns = aclose.pct_change().dropna()
    if len(StockReturns) == 0:
        print("\n  #Error(portfolio_build): retrieved empty returns for",pname)
        return None
    
    # 保存各个成份股的收益率数据，为了后续调用的方便
    stock_return = StockReturns.copy()
    
    # 将原投资组合的权重存储为numpy数组类型，为了合成投资组合计算方便
    import numpy as np
    portfolio_weights = np.array(sharelist)
    # 合成portfolio的日收益率
    WeightedReturns = stock_return.mul(portfolio_weights, axis=1)
    # 原投资组合的收益率
    StockReturns['Portfolio'] = WeightedReturns.sum(axis=1)
    #..........................................................................
    #lang = check_language()
    #..........................................................................
    
    # 绘制原投资组合的收益率曲线，以便使用收益率%来显示
    if graph:
        plotsr = StockReturns['Portfolio']
        plotsr.plot(label=pname)
        plt.axhline(y=0,ls=":",c="red")
        
        title_txt=text_lang("投资组合: 日收益率的变化趋势","Investment Portfolio: Daily Return")
        ylabel_txt=text_lang("日收益率","Daily Return")
        source_txt=text_lang("来源: 综合新浪/东方财富/Stooq/雅虎等, ","Data source: Sina/EM/Stooq/Yahoo, ")
        
        plt.title(title_txt)
        plt.ylabel(ylabel_txt)
        
        stoday = datetime.date.today()
        plt.xlabel(source_txt+str(stoday))
        
        plt.gca().set_facecolor(facecolor)
        
        plt.legend(); plt.show(); plt.close()
        #..........................................................................
        
        # 计算原投资组合的持有收益率，并绘图
        name_list=["Portfolio"]
        label_list=[pname]
        
        
        titletxt=text_lang("投资组合: 持有收益率的变化趋势","Investment Portfolio: Holding Period Return%")
        ylabeltxt=text_lang("持有收益率","Holding Period Return%")
        xlabeltxt1=text_lang("数据来源: 综合新浪/东方财富/Stooq/雅虎等, ","Data source: Sina/EM/Stooq/Yahoo, ")
        xlabeltxt=xlabeltxt1+str(stoday)
    
    #绘制持有收益率曲线
    if graph:
        cumulative_returns_plot(StockReturns,name_list,titletxt,ylabeltxt,xlabeltxt,label_list,facecolor=facecolor)
    #..........................................................................
    
    # 构造等权重组合Portfolio_EW的持有收益率
    numstocks = len(tickerlist)
    # 平均分配每一项的权重
    portfolio_weights_ew = np.repeat(1/numstocks, numstocks)
    # 合成等权重组合的收益，按行横向加总
    StockReturns['Portfolio_EW']=stock_return.mul(portfolio_weights_ew,axis=1).sum(axis=1)
    #..........................................................................
    
    # 创建交易额加权组合：按照成交金额计算期间内交易额均值。债券和基金信息中无交易量！
    if ('bond' not in ticker_type) and ('fund' not in ticker_type):
        tamount=prices['Close']*prices['Volume']
        tamountlist=tamount.mean(axis=0)    #求列的均值
        tamountlist_array = np.array(tamountlist)
        # 计算成交金额权重
        portfolio_weights_lw = tamountlist_array / np.sum(tamountlist_array)
        # 计算成交金额加权的组合收益
        StockReturns['Portfolio_LW'] = stock_return.mul(portfolio_weights_lw, axis=1).sum(axis=1)

    #绘制累计收益率对比曲线
    title_txt=text_lang("投资组合策略：业绩对比","Portfolio Strategies: Performance")
    Portfolio_EW_txt=text_lang("等权重策略","Equal-weighted")
    if ('bond' not in ticker_type) and ('fund' not in ticker_type):
        Portfolio_LW_txt=text_lang("交易额加权策略","Amount-weighted")
    
        name_list=['Portfolio', 'Portfolio_EW', 'Portfolio_LW']
        label_list=[pname, Portfolio_EW_txt, Portfolio_LW_txt]
    else:
        name_list=['Portfolio', 'Portfolio_EW']
        label_list=[pname, Portfolio_EW_txt]
        
        
    titletxt=title_txt
    
    #绘制各个投资组合的持有收益率曲线
    if graph:
        cumulative_returns_plot(StockReturns,name_list,titletxt,ylabeltxt,xlabeltxt,label_list)

    #打印各个投资组合的持股比例
    member_returns=stock_return
    if printout:
        portfolio_expectation_universal(pname,member_returns,portfolio_weights,member_prices,ticker_type)
        portfolio_expectation_universal(Portfolio_EW_txt,member_returns,portfolio_weights_ew,member_prices,ticker_type)
        
        if ('bond' not in ticker_type) and ('fund' not in ticker_type):
            portfolio_expectation_universal(Portfolio_LW_txt,member_returns,portfolio_weights_lw,member_prices,ticker_type)

    #返回投资组合的综合信息
    member_returns=stock_return
    portfolio_returns=StockReturns[name_list]
    
    #投资组合名称改名
    portfolio_returns=cvt_portfolio_name(pname,portfolio_returns)
    
    #打印现有投资组合策略的排名
    if printout:
        portfolio_ranks(portfolio_returns,pname)
    
    #
    if ('bond' not in ticker_type) and ('fund' not in ticker_type):
        return [[portfolio,thedate,member_returns,rf_df,member_prices], \
                [portfolio_returns,portfolio_weights,portfolio_weights_ew,portfolio_weights_lw]]
    else:
        return [[portfolio,thedate,member_returns,rf_df,member_prices], \
                [portfolio_returns,portfolio_weights,portfolio_weights_ew,None]]
        

if __name__=='__main__':
    X=portfolio_build(portfolio,'2021-9-30')

if __name__=='__main__':
    pf_info=portfolio_build(portfolio,'2021-9-30')

#==============================================================================

def portfolio_expret(portfolio,today,pastyears=1, \
                     RF=0,printout=True,graph=True):
    """
    功能：绘制投资组合的持有期收益率趋势图，并与等权和期间内交易额加权组合比较
    套壳原来的portfolio_build函数，以维持兼容性
    expret: expanding return，以维持与前述章节名词的一致性
    hpr: holding period return, 持有（期）收益率
    注意：实验发现RF对于结果的影响极其微小难以观察，默认设为不使用无风险利率调整收益，以加快运行速度
    """
    #处理失败的返回值
    results=portfolio_build(portfolio,today,pastyears, \
                     rate_period,rate_type,RF,printout,graph)
    if results is None: return None
    
    [[portfolio,thedate,member_returns,rf_df,member_prices], \
            [portfolio_returns,portfolio_weights,portfolio_weights_ew,portfolio_weights_lw]] = results

    return [[portfolio,thedate,member_returns,rf_df,member_prices], \
            [portfolio_returns,portfolio_weights,portfolio_weights_ew,portfolio_weights_lw]]

if __name__=='__main__':
    pf_info=portfolio_expret(portfolio,'2021-9-30')

#==============================================================================
def portfolio_correlate(pf_info):
    """
    功能：绘制投资组合成份股之间相关关系的热力图
    """
    [[portfolio,thedate,stock_return,_,_],_]=pf_info
    pname=portfolio_name(portfolio)
    
    #取出观察期
    hstart0=stock_return.index[0]; hstart=str(hstart0.strftime("%Y-%m-%d"))
    hend0=stock_return.index[-1]; hend=str(hend0.strftime("%Y-%m-%d"))
        
    sr=stock_return.copy()
    collist=list(sr)
    for col in collist:
        #投资组合中名称翻译以债券优先处理，因此几乎没有人把基金作为成分股
        sr.rename(columns={col:ticker_name(col,'bond')},inplace=True)

    # 计算相关矩阵
    correlation_matrix = sr.corr()
    
    # 导入seaborn
    import seaborn as sns
    # 创建热图
    sns.heatmap(correlation_matrix,annot=True,cmap="YlGnBu",linewidths=0.3,
            annot_kws={"size": 16})
    plt.title(pname+": 成份股收益率之间的相关系数")
    plt.ylabel("成份股票")
    
    footnote1="观察期间: "+hstart+'至'+hend
    import datetime as dt; stoday=dt.date.today()    
    footnote2="\n来源：Sina/EM/stooq，"+str(stoday)
    plt.xlabel(footnote1+footnote2)
    plt.xticks(rotation=90); plt.yticks(rotation=0) 
    
    plt.gca().set_facecolor('papayawhip')
    plt.show()

    return    

if __name__=='__main__':
    Market={'Market':('US','^GSPC','我的组合001')}
    Stocks1={'AAPL':.1,'MSFT':.13,'XOM':.09,'JNJ':.09,'JPM':.09}
    Stocks2={'AMZN':.15,'GE':.08,'FB':.13,'T':.14}
    portfolio=dict(Market,**Stocks1,**Stocks2)
    pf_info=portfolio_expret(portfolio,'2019-12-31')
    
    portfolio_correlate(pf_info)
#==============================================================================
def portfolio_covar(pf_info):
    """
    功能：计算投资组合成份股之间的协方差
    """
    [[portfolio,thedate,stock_return,_,_],_]=pf_info
    pname=portfolio_name(portfolio)
    
    #取出观察期
    hstart0=stock_return.index[0]; hstart=str(hstart0.strftime("%Y-%m-%d"))
    hend0=stock_return.index[-1]; hend=str(hend0.strftime("%Y-%m-%d"))

    # 计算协方差矩阵
    cov_mat = stock_return.cov()
    # 年化协方差矩阵，252个交易日
    cov_mat_annual = cov_mat * 252
    
    # 导入seaborn
    import seaborn as sns
    # 创建热图
    sns.heatmap(cov_mat_annual,annot=True,cmap="YlGnBu",linewidths=0.3,
            annot_kws={"size": 8})
    plt.title(pname+": 成份股之间的协方差")
    plt.ylabel("成份股票")
    
    footnote1="观察期间: "+hstart+'至'+hend
    import datetime as dt; stoday=dt.date.today()    
    footnote2="\n来源：Sina/EM/stooq，"+str(stoday)
    plt.xlabel(footnote1+footnote2)
    plt.xticks(rotation=90)
    plt.yticks(rotation=0) 
    
    plt.gca().set_facecolor('papayawhip')
    plt.show()

    return 

#==============================================================================
def portfolio_expectation_original(pf_info):
    """
    功能：计算原始投资组合的年均收益率和标准差
    输入：pf_info
    输出：年化收益率和标准差
    """
    [[portfolio,_,member_returns,_,member_prices],[_,portfolio_weights,_,_]]=pf_info
    pname=portfolio_name(portfolio)
    
    portfolio_expectation_universal(pname,member_returns,portfolio_weights,member_prices)
    
    return 

if __name__=='__main__':
    Market={'Market':('US','^GSPC','我的组合001')}
    Stocks1={'AAPL':.1,'MSFT':.13,'XOM':.09,'JNJ':.09,'JPM':.09}
    Stocks2={'AMZN':.15,'GE':.08,'FB':.13,'T':.14}
    portfolio=dict(Market,**Stocks1,**Stocks2)
    pf_info=portfolio_expret(portfolio,'2019-12-31')
    
    portfolio_expectation_original(pf_info)

#==============================================================================
def portfolio_expectation_universal(pname,member_returns,portfolio_weights,member_prices,ticker_type):
    """
    功能：计算给定成份股收益率和持股权重的投资组合年均收益率和标准差
    输入：投资组合名称，成份股历史收益率数据表，投资组合权重series
    输出：年化收益率和标准差
    用途：求出MSR、GMV等持仓策略后计算投资组合的年化收益率和标准差
    """
    
    #观察期
    hstart0=member_returns.index[0]
    #hstart=str(hstart0.date())
    hstart=str(hstart0.strftime("%Y-%m-%d"))
    hend0=member_returns.index[-1]
    #hend=str(hend0.date())
    hend=str(hend0.strftime("%Y-%m-%d"))
    tickerlist=list(member_returns)

    #合成投资组合的历史收益率，按行横向加权求和
    preturns=member_returns.copy() #避免改变输入的数据
    preturns['Portfolio']=preturns.mul(portfolio_weights,axis=1).sum(axis=1)
    
    #计算一手投资组合的价格，最小持股份额的股票需要100股
    import numpy as np
    min_weight=np.min(portfolio_weights)
    # 将最少持股的股票份额转换为1
    portfolio_weights_1=portfolio_weights / min_weight * 1
    portfolio_values=member_prices.mul(portfolio_weights_1,axis=1).sum(axis=1)
    portfolio_value_thedate=portfolio_values[-1:].values[0]

    #计算年化收益率：按列求均值，需要有选项：滚动的年化收益率或月度收益率？
    mean_return=preturns['Portfolio'].mean(axis=0)
    annual_return = (1 + mean_return)**252 - 1
    
    #计算年化标准差
    std_return=preturns['Portfolio'].std(axis=0)
    import numpy as np
    annual_std = std_return*np.sqrt(252)
    
    lang=check_language()
    import datetime as dt; stoday=dt.date.today()    
    if lang == 'Chinese':
        print("\n  ======= 投资组合的收益与风险 =======")
        print("  投资组合:",pname)
        print("  分析日期:",str(hend))
    # 投资组合中即使持股比例最低的股票每次交易最少也需要1手（100股）
        print("  1手组合单位价值:","约"+str(round(portfolio_value_thedate/10000*100,2))+"万")
        print("  观察期间:",hstart+'至'+hend)
        print("  年化收益率:",round(annual_return,4))
        print("  年化标准差:",round(annual_std,4))
        print("  ***投资组合持仓策略***")
        print_tickerlist_sharelist(tickerlist,portfolio_weights,leading_blanks=4,ticker_type=ticker_type)
       
        print("  *数据来源：Sina/EM/Stooq/Yahoo，"+str(stoday)+"统计")
    else:
        print("\n  ======= Investment Portfolio: Return and Risk =======")
        print("  Investment portfolio:",pname)
        print("  Date of analysis:",str(hend))
        print("  Value of portfolio:","about "+str(round(portfolio_value_thedate/1000,2))+"K/portfolio unit")
        print("  Period of sample:",hstart+' to '+hend)
        print("  Annualized return:",round(annual_return,4))
        print("  Annualized std of return:",round(annual_std,4))
        print("  ***Portfolio Constructing Strategy***")
        print_tickerlist_sharelist(tickerlist,portfolio_weights,4)
       
        print("  *Data source: Sina/EM/Stooq/Yahoo, "+str(stoday))

    return 

if __name__=='__main__':
    Market={'Market':('US','^GSPC','我的组合001')}
    Stocks1={'AAPL':.1,'MSFT':.13,'XOM':.09,'JNJ':.09,'JPM':.09}
    Stocks2={'AMZN':.15,'GE':.08,'FB':.13,'T':.14}
    portfolio=dict(Market,**Stocks1,**Stocks2)
    pf_info=portfolio_expret(portfolio,'2019-12-31')

    [[portfolio,thedate,member_returns,_,_],[_,portfolio_weights,_,_]]=pf_info
    pname=portfolio_name(portfolio)
    
    portfolio_expectation2(pname,member_returns, portfolio_weights)

#==============================================================================
def portfolio_expectation(pname,pf_info,portfolio_weights,ticker_type):
    """
    功能：计算给定pf_info和持仓权重的投资组合年均收益率和标准差
    输入：投资组合名称，pf_info，投资组合权重series
    输出：年化收益率和标准差
    用途：求出持仓策略后计算投资组合的年化收益率和标准差，为外部独立使用方便
    """
    [[_,_,member_returns,_,member_prices],_]=pf_info
    
    portfolio_expectation_universal(pname,member_returns,portfolio_weights,member_prices,ticker_type)
    
    return 

if __name__=='__main__':
    Market={'Market':('US','^GSPC','我的组合001')}
    Stocks1={'AAPL':.1,'MSFT':.13,'XOM':.09,'JNJ':.09,'JPM':.09}
    Stocks2={'AMZN':.15,'GE':.08,'FB':.13,'T':.14}
    portfolio=dict(Market,**Stocks1,**Stocks2)
    pf_info=portfolio_expret(portfolio,'2019-12-31')

    [[portfolio,thedate,member_returns,_,_],[_,portfolio_weights,_,_]]=pf_info
    pname=portfolio_name(portfolio)
    
    portfolio_expectation2(pname,member_returns, portfolio_weights)


#==============================================================================

    
def portfolio_ranks(portfolio_returns,pname,facecolor='papayawhip'):
    """
    功能：区分中英文
    """
    """
    lang = check_language()
    if lang == 'Chinese':
        df=portfolio_ranks_cn(portfolio_returns=portfolio_returns,pname=pname,facecolor=facecolor)
    else:
        df=portfolio_ranks_en(portfolio_returns=portfolio_returns,pname=pname)
    """
    df=portfolio_ranks_cn(portfolio_returns=portfolio_returns,pname=pname,facecolor=facecolor)
    
    return df

#==============================================================================

def portfolio_ranks_cn(portfolio_returns,pname,facecolor='papayawhip'):
    """
    功能：打印现有投资组合的收益率、标准差排名，收益率降序，标准差升序，中文/英文
    """
    #临时保存，避免影响原值
    pr=portfolio_returns.copy()
    
    #统一核定小数位数
    ndecimals=2
    
    #以pname组合作为基准
    import numpy as np
    mean_return_pname=pr[pname].mean(axis=0)
    annual_return_pname=round(((1 + mean_return_pname)**252 - 1)*100,ndecimals)
    """
    if annual_return_pname > 0:
        pct_style=True  #百分比模式
    else:   #数值模式，直接加减
        pct_style=False
    """
    pct_style=False
    
    std_return_pname=pr[pname].std(axis=0)
    annual_std_pname= round((std_return_pname*np.sqrt(252))*100,ndecimals)
    
    import pandas as pd  
    #prr=pd.DataFrame(columns=["名称","年化收益率","收益率变化","年化标准差","标准差变化","收益/风险"])    
    #prr=pd.DataFrame(columns=["名称","年化收益率%","收益率变化","年化标准差%","标准差变化","收益/风险"])
    prr=pd.DataFrame(columns=["名称","年化收益率%","收益率变化","年化标准差%","标准差变化","收益率/标准差"])    
    cols=list(pr)
    for c in cols:
        
        #年化收益率：按列求均值
        mean_return=pr[c].mean(axis=0)
        annual_return = round(((1 + mean_return)**252 - 1)*100,ndecimals)
        
        if pct_style:
            return_chg=round((annual_return - annual_return_pname) / annual_return_pname * 100,ndecimals)
        else:
            return_chg=round((annual_return - annual_return_pname),ndecimals)
        
        #收益率变化    
        if return_chg==0:
            return_chg_str=text_lang("基准","Benchmark")
        elif return_chg > 0:
            if pct_style:
                return_chg_str='+'+str(return_chg)+'%'
            else:
                return_chg_str='+'+str(return_chg)
        else:
            if pct_style:
                return_chg_str='-'+str(-return_chg)+'%'
            else:
                return_chg_str='-'+str(-return_chg)
    
        #年化标准差
        std_return=pr[c].std(axis=0)
        annual_std = round((std_return*np.sqrt(252))*100,ndecimals)
        
        #sharpe_ratio=round(annual_return / annual_std,2)
        sharpe_ratio=round((annual_return) / annual_std,ndecimals)
        
        if pct_style:
            std_chg=round((annual_std - annual_std_pname) / annual_std_pname * 100,ndecimals)
        else:
            std_chg=round((annual_std - annual_std_pname),ndecimals)
        
        #标准差变化
        if std_chg==0:
            std_chg_str=text_lang("基准","Benchmark")
        elif std_chg > 0:
            if pct_style:
                std_chg_str='+'+str(std_chg)+'%'
            else:
                std_chg_str='+'+str(std_chg)
        else:
            if pct_style:
                std_chg_str='-'+str(-std_chg)+'%'
            else:
                std_chg_str='-'+str(-std_chg)
        
        row=pd.Series({"名称":c,"年化收益率%":annual_return, \
                       "收益率变化":return_chg_str, \
                       "年化标准差%":annual_std,"标准差变化":std_chg_str,"收益率/标准差":sharpe_ratio})
        try:
            prr=prr.append(row,ignore_index=True)
        except:
            prr=prr._append(row,ignore_index=True)
    
    #先按风险降序排名，高者排前面
    prr.sort_values(by="年化标准差%",ascending=False,inplace=True)
    prr.reset_index(inplace=True)
    prr['风险排名']=prr.index+1
    
    #再按收益降序排名，高者排前面
    prr.sort_values(by="年化收益率%",ascending=False,inplace=True)
    prr.reset_index(inplace=True)
    prr['收益排名']=prr.index+1    
    
    #prr2=prr[["名称","收益排名","风险排名","年化收益率","年化标准差","收益率变化","标准差变化","收益/风险"]]
    prr2=prr[["名称","收益排名","年化收益率%","收益率变化", \
              "风险排名","年化标准差%","标准差变化", \
                  "收益率/标准差"]]
    prr2.sort_values(by="年化收益率%",ascending=False,inplace=True)
    #prr2.reset_index(inplace=True)
    
    #打印
    """
    print("\n========= 投资组合策略排名：平衡收益与风险 =========\n")
    #打印对齐
    pd.set_option('display.max_columns', 1000)
    pd.set_option('display.width', 1000)
    pd.set_option('display.max_colwidth', 1000)
    pd.set_option('display.unicode.ambiguous_as_wide', True)
    pd.set_option('display.unicode.east_asian_width', True)
    
    #print(prr2.to_string(index=False,header=False))
    #print(prr2.to_string(index=False))
    
    alignlist=['left']+['center']*(len(list(prr2))-2)+['right']
    print(prr2.to_markdown(index=False,tablefmt='plain',colalign=alignlist))
    """
    #一点改造
    print('') #空一行
    prr2.index=prr2.index + 1
    prr2.rename(columns={'名称':'投资组合名称/策略'},inplace=True)
    for c in list(prr2):
        try:
            prr2[c]=prr2[c].apply(lambda x: str(round(x,4)) if isinstance(x,float) else str(x))
        except: pass
    
    titletxt=text_lang('投资组合策略排名：平衡收益与风险','Investment Portfolio Strategies: Performance, Balancing Return and Risk')
    """
    dispt=prr2.style.set_caption(titletxt).set_table_styles(
        [{'selector':'caption',
          'props':[('color','black'),('font-size','16px'),('font-weight','bold')]}])        
    dispf=dispt.set_properties(**{'text-align':'center'})
    
    from IPython.display import display
    display(dispf)
    """
    
    prr2.rename(columns={"投资组合名称/策略":text_lang("投资组合名称/策略","Strategy"), \
                         "收益排名":text_lang("收益排名","Return#"), \
                         "年化收益率%":text_lang("年化收益率%","pa Return%"), \
                         "收益率变化":text_lang("收益率变化","Return%+/-"), \
                         "风险排名":text_lang("风险排名","Risk#"), \
                         "年化标准差%":text_lang("年化标准差%","pa Std%"), \
                         "标准差变化":text_lang("标准差变化","Std%+/-"), \
                         "收益率/标准差":text_lang("收益/风险性价比","Return/Std")}, \
                inplace=True)
    
    #重新排名：相同的值赋予相同的序号
    prr2[text_lang("年化收益率%","pa Return%")]=prr2[text_lang("年化收益率%","pa Return%")].apply(lambda x: round(float(x),ndecimals))
    prr2[text_lang("收益排名","Return#")]=prr2[text_lang("年化收益率%","pa Return%")].rank(ascending=False,method='dense')
    prr2[text_lang("收益排名","Return#")]=prr2[text_lang("收益排名","Return#")].apply(lambda x: int(x))
    
    prr2[text_lang("年化标准差%","pa Std%")]=prr2[text_lang("年化标准差%","pa Std%")].apply(lambda x: round(float(x),ndecimals))
    prr2[text_lang("风险排名","Risk#")]=prr2[text_lang("年化标准差%","pa Std%")].rank(ascending=False,method='dense')
    prr2[text_lang("风险排名","Risk#")]=prr2[text_lang("风险排名","Risk#")].apply(lambda x: int(x))
    
    prr2[text_lang("收益/风险性价比","Return/Std")]=prr2[text_lang("收益/风险性价比","Return/Std")].apply(lambda x: round(float(x),ndecimals))
    prr2[text_lang("性价比排名","Ret/Std#")]=prr2[text_lang("收益/风险性价比","Return/Std")].rank(ascending=False,method='dense')
    prr2[text_lang("性价比排名","Ret/Std#")]=prr2[text_lang("性价比排名","Ret/Std#")].apply(lambda x: int(x))
    
    df_display_CSS(prr2,titletxt=titletxt,footnote='',facecolor='papayawhip',decimals=ndecimals, \
                       first_col_align='left',second_col_align='center', \
                       last_col_align='center',other_col_align='center', \
                       titile_font_size='15px',heading_font_size='13px', \
                       data_font_size='13px')
    
    """
    print(' ') #空一行
    
    disph=prr2.style.hide() #不显示索引列
    dispp=disph.format(precision=2) #设置带有小数点的列精度调整为小数点后2位
    #设置标题/列名
    dispt=dispp.set_caption(titletxt).set_table_styles(
        [{'selector':'caption', #设置标题属性
          'props':[('color','black'),('font-size','18px'),('font-weight','bold')]}, \
         {'selector':'th.col_heading', #设置列名属性
          'props':[('color','black'),('font-size','17px'),('background-color',facecolor),('text-align','center'),('margin','auto')]}])        
    #设置列数值对齐
    dispt1=dispt.set_properties(**{'font-size':'17px'})
    dispf=dispt1.set_properties(**{'text-align':'center'})
    #设置前景背景颜色
    try:
        dispf2=dispf.set_properties(**{'background-color':facecolor,'color':'black'})
    except:
        print("  #Warning(portfolio_ranks_cn): color",facecolor,"is unsupported, changed to default setting")
        dispf2=dispf.set_properties(**{'background-color':'papayawhip','color':'black'})

    from IPython.display import display
    display(dispf2)
    
    print('') #空一行
    """
    return prr2   

if __name__=='__main__':
    portfolio_ranks(portfolio_returns,pname)

#==============================================================================

def portfolio_ranks_en(portfolio_returns,pname):
    """
    功能：打印现有投资组合的收益率、标准差排名，收益率降序，标准差升序，英文
    废弃！！！
    """
    #临时保存，避免影响原值
    pr=portfolio_returns.copy()
    
    #以pname组合作为基准
    import numpy as np
    mean_return_pname=pr[pname].mean(axis=0)
    annual_return_pname=(1 + mean_return_pname)**252 - 1
    if annual_return_pname > 0:
        pct_style=True
    else:
        pct_style=False
    
    std_return_pname=pr[pname].std(axis=0)
    annual_std_pname= std_return_pname*np.sqrt(252)
    
    import pandas as pd  
    prr=pd.DataFrame(columns=["Portfolio","Annualized Return","Change of Return","Annualized Std","Change of Std","Return/Risk"])    
    cols=list(pr)
    for c in cols:
        #计算年化收益率：按列求均值
        mean_return=pr[c].mean(axis=0)
        annual_return = (1 + mean_return)**252 - 1
        
        if pct_style:
            return_chg=round((annual_return - annual_return_pname) / annual_return_pname *100,1)
        else:
            return_chg=round((annual_return - annual_return_pname),5)
            
        if return_chg==0:
            return_chg_str="base"
        elif return_chg > 0:
            if pct_style:
                return_chg_str='+'+str(return_chg)+'%'
            else:
                return_chg_str='+'+str(return_chg)
        else:
            if pct_style:
                return_chg_str='-'+str(-return_chg)+'%'
            else:
                return_chg_str='-'+str(-return_chg)
    
        #计算年化标准差
        std_return=pr[c].std(axis=0)
        annual_std = std_return*np.sqrt(252)
        
        sharpe_ratio=round(annual_return / annual_std,4)
        
        if pct_style:
            std_chg=round((annual_std - annual_std_pname) / annual_std_pname *100,4)
        else:
            std_chg=round((annual_std - annual_std_pname),4)
        if std_chg==0:
            std_chg_str="base"
        elif std_chg > 0:
            if pct_style:
                std_chg_str='+'+str(std_chg)+'%'
            else:
                std_chg_str='+'+str(std_chg)
        else:
            if pct_style:
                std_chg_str='-'+str(-std_chg)+'%'
            else:
                std_chg_str='-'+str(-std_chg)
        
        row=pd.Series({"Portfolio":c,"Annualized Return":annual_return,"Change of Return":return_chg_str, \
                       "Annualized Std":annual_std,"Change of Std":std_chg_str,"Return/Risk":sharpe_ratio})
        try:
            prr=prr.append(row,ignore_index=True)
        except:
            prr=prr._append(row,ignore_index=True)
    
    #处理小数位数，以便与其他地方的小数位数一致
    prr['Annualized Return']=round(prr['Annualized Return'],4)
    prr['Annualized Std']=round(prr['Annualized Std'],4)
    
    #先按风险降序排名，高者排前面
    prr.sort_values(by="Annualized Std",ascending=False,inplace=True)
    prr.reset_index(inplace=True)
    prr['Risk Rank']=prr.index+1
    
    #再按收益降序排名，高者排前面
    prr.sort_values(by="Annualized Return",ascending=False,inplace=True)
    prr.reset_index(inplace=True)
    prr['Return Rank']=prr.index+1    
    
    prr2=prr[["Portfolio","Return Rank","Risk Rank","Annualized Return","Annualized Std","Change of Return","Change of Std","Return/Risk"]]
    prr2.sort_values(by="Annualized Return",ascending=False,inplace=True)
    #prr2.reset_index(inplace=True)
    
    #打印
    print("\n========= Investment Portfolio Strategy Ranking: Balancing Return & Risk =========\n")
    #打印对齐
    pd.set_option('display.max_columns', 1000)
    pd.set_option('display.width', 1000)
    pd.set_option('display.max_colwidth', 1000)
    pd.set_option('display.unicode.ambiguous_as_wide', True)
    pd.set_option('display.unicode.east_asian_width', True)
    
    #print(prr2.to_string(index=False,header=False))
    print(prr2.to_string(index=False))

    return prr2   

#==============================================================================
if __name__=='__main__':
    #Define market information and name of the portfolio: Banking #1
    Market={'Market':('China','000300.SS','Banking #1')}
    #First batch of component stocks
    Stocks1={'601939.SS':.3,#CCB Bank
             '600000.SS':.3, #SPDB Bank
             '600036.SS':.2, #CMB Bank
             '601166.SS':.2,#Industrial Bank
            }
    portfolio=dict(Market,**Stocks1)    
    
    pf_info=portfolio_build(portfolio,thedate='2024-7-17')
    
    simulation=50000
    convex_hull=True; frontier="both"; facecolor='papayawhip'
    
    portfolio_eset(pf_info,simulation=50000)

def portfolio_feset(pf_info,simulation=10000,convex_hull=True,frontier="both",facecolor='papayawhip'):
    """
    功能：套壳函数portfolio_eset
    当frontier不在列表['efficient','inefficient','both']中时，绘制可行集
    当frontier == 'efficient'时绘制有效边界
    当frontier == 'inefficient'时绘制无效边界
    当frontier == 'both'时同时绘制有效边界和无效边界
    当绘制有效/无效边界时，默认使用凸包绘制（convex_hull=True）
    注：若可行集形状不佳，首先尝试pastyears=3，再尝试增加simulation数量
    """
    if frontier is None:
        convex_hull=False
    elif isinstance(frontier,str):
        frontier=frontier.lower()
    
        frontier_list=['efficient','inefficient','both']
        if not any(element in frontier for element in frontier_list):
            convex_hull=False
        else:
            convex_hull=True
    else:
        convex_hull=False
        
    results=portfolio_eset(pf_info,simulation=simulation,convex_hull=convex_hull,frontier=frontier,facecolor=facecolor)
    
    return results


def portfolio_eset(pf_info,simulation=50000,convex_hull=False,frontier="both",facecolor='papayawhip'):
    """
    功能：基于随机数，生成大量可能的投资组合，计算各个投资组合的年均收益率和标准差，绘制投资组合的可行集
    默认绘制散点图凸包：convex_hull=True
    """
    DEBUG=True; MORE_DETAIL=False
    
    frontier_list=['efficient','inefficient','both']
    if isinstance(frontier,str):
        if any(element in frontier for element in frontier_list):
            efficient_set=True
        else:
            efficient_set=False
    else:
        efficient_set=False
    
    [[portfolio,thedate,stock_return,_,_],_]=pf_info
    pname=portfolio_name(portfolio)
    _,_,tickerlist,_,ticker_type=decompose_portfolio(portfolio)
    
    #取出观察期
    hstart0=stock_return.index[0]; hstart=str(hstart0.strftime("%Y-%m-%d"))
    hend0=stock_return.index[-1]; hend=str(hend0.strftime("%Y-%m-%d"))    
    
    #获得成份股个数
    numstocks=len(tickerlist)

    # 设置空的numpy数组，用于存储每次模拟得到的成份股权重、投资组合的收益率和标准差
    import numpy as np
    random_p = np.empty((simulation,numstocks+2))
    # 设置随机数种子，这里是为了结果可重复
    np.random.seed(RANDOM_SEED)

    # 循环模拟n次随机的投资组合
    print("  Calculating portfolio feasible set, please wait ...")    
    for i in range(simulation):
        # 生成numstocks个随机数，并归一化，得到一组随机的权重数据
        random9 = np.random.random(numstocks)
        random_weight = random9 / np.sum(random9)
    
        # 计算随机投资组合的年化平均收益率
        mean_return=stock_return.mul(random_weight,axis=1).sum(axis=1).mean(axis=0)
        annual_return = (1 + mean_return)**252 - 1
    
        # 计算随机投资组合的年化平均标准差
        std_return=stock_return.mul(random_weight,axis=1).sum(axis=1).std(axis=0)
        annual_std = std_return*np.sqrt(252)

        # 将上面生成的权重，和计算得到的收益率、标准差存入数组random_p中
        # 数组矩阵的前numstocks为随机权重，其后为年均收益率，再后为年均标准差
        random_p[i][:numstocks] = random_weight
        random_p[i][numstocks] = annual_return
        random_p[i][numstocks+1] = annual_std
        
        #显示完成进度
        print_progress_percent(i,simulation,steps=10,leading_blanks=2)
    
    # 将numpy数组转化成DataFrame数据框
    import pandas as pd
    RandomPortfolios = pd.DataFrame(random_p)
    # 设置数据框RandomPortfolios每一列的名称
    RandomPortfolios.columns = [ticker + "_weight" for ticker in tickerlist]  \
                         + ['Returns', 'Volatility']

    # 绘制散点图
    """
    RandomPortfolios.plot('Volatility','Returns',kind='scatter',color='y',edgecolors='k')
    """
    #RandomPortfolios['Returns_Volatility']=RandomPortfolios['Returns'] / RandomPortfolios['Volatility']
    #pf_ratio = np.array(RandomPortfolios['Returns_Volatility'])
    pf_ratio = np.array(RandomPortfolios['Returns'] / RandomPortfolios['Volatility'])
    pf_returns = np.array(RandomPortfolios['Returns'])
    pf_volatilities = np.array(RandomPortfolios['Volatility'])

    #plt.style.use('seaborn-dark') #不支持中文
    #plt.figure(figsize=(12.8,6.4))
    plt.scatter(pf_volatilities,pf_returns,c=pf_ratio,cmap='RdYlGn',edgecolors='black',marker='o') 
    #plt.grid(True)
    
    #绘制散点图轮廓线凸包（convex hull）
    if convex_hull:
        print("  Calculating convex hull ...")
        
        from scipy.spatial import ConvexHull
        
        #构造散点对的列表
        pf_volatilities_list=list(pf_volatilities)
        pf_returns_list=list(pf_returns)
        points=[]
        for x in pf_volatilities_list:
            pos=pf_volatilities_list.index(x)
            y=pf_returns_list[pos]
            points=points+[[x,y]]
        
        #寻找最左侧的坐标：在x最小的同时，y要最大
        points_df = pd.DataFrame(points, columns=['x', 'y'])
        points_df.sort_values(by=['x','y'],ascending=[True,False],inplace=True)
        x1,y1=points_df.head(1).values[0]
        if DEBUG and MORE_DETAIL:
            print("\n*** Leftmost point (x1,y1):",x1,y1)
        
        #寻找最高点的坐标：在y最大的同时，x要最小
        points_df.sort_values(by=['y','x'],ascending=[False,True],inplace=True)
        x2,y2=points_df.head(1).values[0]
        if DEBUG and MORE_DETAIL:
            print("*** Highest point (x2,y2):",x2,y2)
        
        if DEBUG:
            plt.plot([x1,x2],[y1,y2],ls=':',lw=2,alpha=0.5)
        
        #建立最左侧和最高点之间的拟合直线方程y=a+bx
        a=(x1*y2-x2*y1)/(x1-x2); b=(y1-y2)/(x1-x2)
        def y_bar(x_bar):
            return a+b*x_bar
        
        # 计算散点集的外轮廓
        hull = ConvexHull(points)  
        
        # 绘制外轮廓线
        firsttime_efficient=True; firsttime_inefficient=True
        for simplex in hull.simplices:
            #p1中是一条线段起点和终点的横坐标
            p1=[points[simplex[0]][0], points[simplex[1]][0]]
            px1=p1[0];px2=p1[1]
            #p2中是一条线段起点和终点的纵坐标
            p2=[points[simplex[0]][1], points[simplex[1]][1]]
            py1=p2[0]; py2=p2[1]
            
            if DEBUG and MORE_DETAIL:
                print("\n*** Hull line start (px1,py1):",px1,py1)
                print("*** Hull line end (px2,py2):",px2,py2)

            """
            plt.plot([points[simplex[0]][0], points[simplex[1]][0]],
                     [points[simplex[0]][1], points[simplex[1]][1]], 'k-.')   
            """
            
            #线段起点：px1,py1；线段终点：px2,py2
            if DEBUG and MORE_DETAIL:
                is_efficient=(py1>=y_bar(px1) or py1==y1) and (py2>=y_bar(px2) or py2==y2)
                print("\n*** is_efficient:",is_efficient)
                print("py1=",py1,"y_bar1",y_bar(px1),"y1=",y1,"py2=",py2,"ybar2=",y_bar(px2),"y2=",y2)
                if px1==x1 and py1==y1:
                    print("====== This is the least risk point !")
                if px2==x2 and py2==y2:
                    print("====== This is the highest return point !")
            
            #坐标对[px1,py1]既可能作为开始点，也可能作为结束点，[px2,py2]同样
            if ((py1>=y_bar(px1) or py1==y1) and (py2>=y_bar(px2) or py2==y2)) or \
               ((py1>=y_bar(px2) or py1==y2) and (py2>=y_bar(px1) or py2==y1)):
                   
                #有效边界
                if frontier.lower() in ['both','efficient']:
                    if firsttime_efficient:
                        plt.plot(p1,p2, 'r--',label=text_lang("有效边界","Efficient Frontier"),lw=3,alpha=0.5)   
                        firsttime_efficient=False
                    else:
                        plt.plot(p1,p2, 'r--',lw=3,alpha=0.5)   
                else:
                    pass
            else:
                #其余边沿
                if frontier.lower() in ['both','inefficient']:
                    if firsttime_inefficient:
                        plt.plot(p1,p2, 'k-.',label=text_lang("无效边界","Inefficient Frontier"),alpha=0.5)
                        firsttime_inefficient=False
                    else:
                        plt.plot(p1,p2, 'k-.',alpha=0.5)
                else:
                    pass
    else:
        pass
    
    # 空一行
    print('')
      
    
    import datetime as dt; stoday=dt.date.today()
    lang = check_language()
    if lang == 'Chinese':  
        if pname == '': pname='投资组合'
        
        plt.colorbar(label='收益率/标准差')
        
        if efficient_set:
            if frontier == 'efficient':
                titletxt0=": 马科维茨有效集(有效边界)"
            elif frontier == 'inefficient':
                titletxt0=": 马科维茨无效集(无效边界)"
            elif frontier == 'both':
                titletxt0=": 马科维茨有效边界与无效边界"
            else:
                titletxt0=": 马科维茨可行集"
        else:
            titletxt0=": 马科维茨可行集"
            
        plt.title(pname+titletxt0,fontsize=title_txt_size)
        plt.ylabel("年化收益率",fontsize=ylabel_txt_size)
        
        footnote1="年化收益率标准差-->"
        footnote2="\n\n基于给定的成份证券构造"+str(simulation)+"个投资组合"
        footnote3="\n观察期间："+hstart+"至"+hend
        footnote4="\n数据来源: Sina/EM/Stooq/Yahoo, "+str(stoday)
    else:
        if pname == '': pname='Investment Portfolio'
        
        if efficient_set:
            if frontier == 'efficient':
                titletxt0=": Markowitz Efficient Set (Efficient Frontier)"
            elif frontier == 'inefficient':
                titletxt0=": Markowitz Inefficient Set (Inefficient Frontier)"
            elif frontier == 'both':
                titletxt0=": Markowitz Efficient & Inefficient Frontier"
            else:
                titletxt0=": Markowitz Feasible Set"
        else:
            titletxt0=": Markowitz Feasible Set"
            
        plt.colorbar(label='Return/Std')
        plt.title(pname+titletxt0,fontsize=title_txt_size)
        plt.ylabel("Annualized Return",fontsize=ylabel_txt_size)
        
        footnote1="Annualized Std -->\n\n"
        footnote2="Built "+str(simulation)+" portfolios of given securities\n"
        footnote3="Period of sample: "+hstart+" to "+hend
        footnote4="\nData source: Sina/EM/Stooq/Yahoo, "+str(stoday)
    
    plt.xlabel(footnote1+footnote2+footnote3+footnote4,fontsize=xlabel_txt_size)
    
    plt.gca().set_facecolor(facecolor)
    if efficient_set:
        plt.legend(loc='best')
    plt.show()

    return [pf_info,RandomPortfolios]

if __name__=='__main__':
    Market={'Market':('US','^GSPC','我的组合001')}
    Stocks1={'AAPL':.1,'MSFT':.13,'XOM':.09,'JNJ':.09,'JPM':.09}
    Stocks2={'AMZN':.15,'GE':.08,'FB':.13,'T':.14}
    portfolio=dict(Market,**Stocks1,**Stocks2)
    pf_info=portfolio_expret(portfolio,'2019-12-31')
    
    es=portfolio_eset(pf_info,simulation=50000)

#==============================================================================
if __name__=='__main__':
    simulation=1000
    rate_period='1Y'
    rate_type='treasury'

def portfolio_es_sharpe(pf_info,simulation=50000,RF=0):
    """
    功能：基于随机数，生成大量可能的投资组合，计算各个投资组合的年均风险溢价及其标准差，绘制投资组合的可行集
    """
    print("  Calculating possible portfolio combinations, please wait ...")    
    
    [[portfolio,thedate,stock_return0,rf_df,_],_]=pf_info
    pname=portfolio_name(portfolio)
    scope,_,tickerlist,_,ticker_type=decompose_portfolio(portfolio)
    
    #取出观察期
    hstart0=stock_return0.index[0]; hstart=str(hstart0.strftime("%Y-%m-%d"))
    hend0=stock_return0.index[-1]; hend=str(hend0.strftime("%Y-%m-%d"))    

    import pandas as pd
    #处理无风险利率
    """
    if RF:
        #rf_df=get_rf_daily(hstart,hend,scope,rate_period,rate_type)
        if not (rf_df is None):
            stock_return1=pd.merge(stock_return0,rf_df,how='inner',left_index=True,right_index=True)
            for t in tickerlist:
                #计算风险溢价
                stock_return1[t]=stock_return1[t]-stock_return1['rf_daily']
        
            stock_return=stock_return1[tickerlist]
        else:
            print("  #Error(portfolio_es_sharpe): failed to retrieve risk-free interest rate, please try again")
            return None
    else:
        #不考虑RF
        stock_return=stock_return0
    """
    rf_daily=RF/365
    for t in tickerlist:
        #计算风险溢价
        stock_return0[t]=stock_return0[t]-rf_daily
    stock_return=stock_return0[tickerlist]
    
    #获得成份股个数
    numstocks=len(tickerlist)

    # 设置空的numpy数组，用于存储每次模拟得到的成份股权重、组合的收益率和标准差
    import numpy as np
    random_p = np.empty((simulation,numstocks+2))
    # 设置随机数种子，这里是为了结果可重复
    np.random.seed(RANDOM_SEED)

    # 循环模拟n次随机的投资组合
    for i in range(simulation):
        # 生成numstocks个随机数，并归一化，得到一组随机的权重数据
        random9 = np.random.random(numstocks)
        random_weight = random9 / np.sum(random9)
    
        # 计算随机投资组合的年化平均收益率
        mean_return=stock_return.mul(random_weight,axis=1).sum(axis=1).mean(axis=0)
        annual_return = (1 + mean_return)**252 - 1
    
        # 计算随机投资组合的年化平均标准差
        std_return=stock_return.mul(random_weight,axis=1).sum(axis=1).std(axis=0)
        annual_std = std_return*np.sqrt(252)

        # 将上面生成的权重，和计算得到的收益率、标准差存入数组random_p中
        # 数组矩阵的前numstocks为随机权重，其后为年均收益率，再后为年均标准差
        random_p[i][:numstocks] = random_weight
        random_p[i][numstocks] = annual_return
        random_p[i][numstocks+1] = annual_std
        
        #显示完成进度
        print_progress_percent(i,simulation,steps=10,leading_blanks=2)
    
    # 将numpy数组转化成DataFrame数据框
    RandomPortfolios = pd.DataFrame(random_p)
    # 设置数据框RandomPortfolios每一列的名称
    RandomPortfolios.columns = [ticker + "_weight" for ticker in tickerlist]  \
                         + ['Risk premium', 'Risk premium volatility']

    return [pf_info,RandomPortfolios]

if __name__=='__main__':
    Market={'Market':('US','^GSPC','我的组合001')}
    Stocks1={'AAPL':.1,'MSFT':.13,'XOM':.09,'JNJ':.09,'JPM':.09}
    Stocks2={'AMZN':.15,'GE':.08,'FB':.13,'T':.14}
    portfolio=dict(Market,**Stocks1,**Stocks2)
    pf_info=portfolio_expret(portfolio,'2019-12-31')
    
    es_sharpe=portfolio_es_sharpe(pf_info,simulation=50000)

#==============================================================================
if __name__=='__main__':
    simulation=1000
    rate_period='1Y'
    rate_type='treasury'

def portfolio_es_sortino(pf_info,simulation=50000,RF=0):
    """
    功能：基于随机数，生成大量可能的投资组合，计算各个投资组合的年均风险溢价及其下偏标准差，绘制投资组合的可行集
    """
    print("  Calculating possible portfolio combinations, please wait ...")    
    
    [[portfolio,thedate,stock_return0,rf_df,_],_]=pf_info
    pname=portfolio_name(portfolio)
    scope,_,tickerlist,_,ticker_type=decompose_portfolio(portfolio)
    
    #取出观察期
    hstart0=stock_return0.index[0]; hstart=str(hstart0.strftime("%Y-%m-%d"))
    hend0=stock_return0.index[-1]; hend=str(hend0.strftime("%Y-%m-%d"))    

    import pandas as pd
    #处理无风险利率
    """
    if RF:
        #rf_df=get_rf_daily(hstart,hend,scope,rate_period,rate_type)
        if not (rf_df is None):
            stock_return1=pd.merge(stock_return0,rf_df,how='inner',left_index=True,right_index=True)
            for t in tickerlist:
                #计算风险溢价
                stock_return1[t]=stock_return1[t]-stock_return1['rf_daily']
        
            stock_return=stock_return1[tickerlist]
        else:
            print("  #Error(portfolio_es_sortino): failed to retrieve risk-free interest rate, please try again")
            return None
    else:
        #不考虑RF
        stock_return=stock_return0
    """
    rf_daily=RF/365
    for t in tickerlist:
        #计算风险溢价
        stock_return0[t]=stock_return0[t]-rf_daily
    stock_return=stock_return0[tickerlist]
    
    #获得成份股个数
    numstocks=len(tickerlist)

    # 设置空的numpy数组，用于存储每次模拟得到的成份股权重、组合的收益率和标准差
    import numpy as np
    random_p = np.empty((simulation,numstocks+2))
    # 设置随机数种子，这里是为了结果可重复
    np.random.seed(RANDOM_SEED)
    # 与其他比率设置不同的随机数种子，意在产生多样性的随机组合

    # 循环模拟n次随机的投资组合
    for i in range(simulation):
        # 生成numstocks个随机数，并归一化，得到一组随机的权重数据
        random9 = np.random.random(numstocks)
        random_weight = random9 / np.sum(random9)
    
        # 计算随机投资组合的年化平均收益率
        mean_return=stock_return.mul(random_weight,axis=1).sum(axis=1).mean(axis=0)
        annual_return = (1 + mean_return)**252 - 1
    
        # 计算随机投资组合的年化平均下偏标准差
        sr_temp0=stock_return.copy()
        sr_temp0['Portfolio Ret']=sr_temp0.mul(random_weight,axis=1).sum(axis=1)
        sr_temp1=sr_temp0[sr_temp0['Portfolio Ret'] < mean_return]
        sr_temp2=sr_temp1[tickerlist]
        lpsd_return=sr_temp2.mul(random_weight,axis=1).sum(axis=1).std(axis=0)
        annual_lpsd = lpsd_return*np.sqrt(252)

        # 将上面生成的权重，和计算得到的收益率、标准差存入数组random_p中
        # 数组矩阵的前numstocks为随机权重，其后为年均收益率，再后为年均标准差
        random_p[i][:numstocks] = random_weight
        random_p[i][numstocks] = annual_return
        random_p[i][numstocks+1] = annual_lpsd
        
        #显示完成进度
        print_progress_percent(i,simulation,steps=10,leading_blanks=2)
    
    # 将numpy数组转化成DataFrame数据框
    RandomPortfolios = pd.DataFrame(random_p)
    # 设置数据框RandomPortfolios每一列的名称
    RandomPortfolios.columns = [ticker + "_weight" for ticker in tickerlist]  \
                         + ['Risk premium', 'Risk premium LPSD']

    return [pf_info,RandomPortfolios]

if __name__=='__main__':
    Market={'Market':('US','^GSPC','我的组合001')}
    Stocks1={'AAPL':.1,'MSFT':.13,'XOM':.09,'JNJ':.09,'JPM':.09}
    Stocks2={'AMZN':.15,'GE':.08,'FB':.13,'T':.14}
    portfolio=dict(Market,**Stocks1,**Stocks2)
    pf_info=portfolio_expret(portfolio,'2019-12-31')
    
    es_sortino=portfolio_es_sortino(pf_info,simulation=50000)

#==============================================================================
#==============================================================================
if __name__=='__main__':
    simulation=1000
    rate_period='1Y'
    rate_type='treasury'

def portfolio_es_alpha(pf_info,simulation=50000,RF=0):
    """
    功能：基于随机数，生成大量可能的投资组合，计算各个投资组合的年化标准差和阿尔法指数，绘制投资组合的可行集
    """
    print("  Calculating possible portfolio combinations, please wait ...")    
    
    [[portfolio,thedate,stock_return0,rf_df,_],_]=pf_info
    pname=portfolio_name(portfolio)
    scope,mktidx,tickerlist,_,ticker_type=decompose_portfolio(portfolio)
    
    #取出观察期
    hstart0=stock_return0.index[0]; hstart=str(hstart0.strftime("%Y-%m-%d"))
    hend0=stock_return0.index[-1]; hend=str(hend0.strftime("%Y-%m-%d"))    

    #计算市场指数的收益率
    import pandas as pd
    start1=date_adjust(hstart,adjust=-30)
    mkt=get_prices(mktidx,start1,hend)
    mkt['Mkt']=mkt['Close'].pct_change()
    mkt.dropna(inplace=True)
    mkt1=pd.DataFrame(mkt['Mkt'])

    stock_return0m=pd.merge(stock_return0,mkt1,how='left',left_index=True,right_index=True)
    #必须舍弃空值，否则下面的回归将得不到系数!!!
    stock_return0m.dropna(inplace=True)
    
    #处理期间内无风险利率
    """
    if RF:
        #rf_df=get_rf_daily(hstart,hend,scope,rate_period,rate_type)
        if not (rf_df is None):
            stock_return1=pd.merge(stock_return0m,rf_df,how='inner',left_index=True,right_index=True)
            for t in tickerlist:
                #计算风险溢价
                stock_return1[t]=stock_return1[t]-stock_return1['rf_daily']
        
            stock_return1['Mkt']=stock_return1['Mkt']-stock_return1['rf_daily']
            stock_return=stock_return1[tickerlist+['Mkt']]
        else:
            print("  #Error(portfolio_es_alpha): failed to retrieve risk-free interest rate, please try again")
            return None
    else:
        #不考虑RF
        stock_return=stock_return0m[tickerlist+['Mkt']]    
    """
    rf_daily=RF/365
    for t in tickerlist:
        #计算风险溢价
        stock_return0m[t]=stock_return0m[t]-rf_daily
    stock_return0m['Mkt']=stock_return0m['Mkt']-rf_daily
    stock_return=stock_return0m[tickerlist+['Mkt']]
    
    #获得成份股个数
    numstocks=len(tickerlist)

    # 设置空的numpy数组，用于存储每次模拟得到的成份股权重、组合的收益率和标准差
    import numpy as np
    random_p = np.empty((simulation,numstocks+2))
    # 设置随机数种子，这里是为了结果可重复
    np.random.seed(RANDOM_SEED)
    # 与其他比率设置不同的随机数种子，意在产生多样性的随机组合

    # 循环模拟n次随机的投资组合
    from scipy import stats
    for i in range(simulation):
        # 生成numstocks个随机数，并归一化，得到一组随机的权重数据
        random9 = np.random.random(numstocks)
        random_weight = random9 / np.sum(random9)
    
        # 计算随机投资组合的历史收益率
        stock_return['pRet']=stock_return[tickerlist].mul(random_weight,axis=1).sum(axis=1)
        """
        #使用年化收益率，便于得到具有可比性的纵轴数据刻度
        stock_return['pReta']=(1+stock_return['pRet'])**252 - 1
        stock_return['Mkta']=(1+stock_return['Mkt'])**252 - 1
        """
        #回归求截距项作为阿尔法指数：参与回归的变量不能有空值，否则回归系数将为空值！！！
        (beta,alpha,_,_,_)=stats.linregress(stock_return['Mkt'],stock_return['pRet'])        
        """
        mean_return=stock_return[tickerlist].mul(random_weight,axis=1).sum(axis=1).mean(axis=0)
        annual_return = (1 + mean_return)**252 - 1
    
        # 计算随机投资组合的年化平均标准差
        std_return=stock_return[tickerlist].mul(random_weight,axis=1).sum(axis=1).std(axis=0)
        annual_std = std_return*np.sqrt(252)
        """
        # 将上面生成的权重，和计算得到的阿尔法指数、贝塔系数存入数组random_p中
        # 数组矩阵的前numstocks为随机权重，其后为收益指标，再后为风险指标
        random_p[i][:numstocks] = random_weight
        random_p[i][numstocks] = alpha
        random_p[i][numstocks+1] = beta
        
        #显示完成进度
        print_progress_percent(i,simulation,steps=10,leading_blanks=2)
    
    # 将numpy数组转化成DataFrame数据框
    RandomPortfolios = pd.DataFrame(random_p)
    # 设置数据框RandomPortfolios每一列的名称
    RandomPortfolios.columns = [ticker + "_weight" for ticker in tickerlist]  \
                         + ['alpha', 'beta']

    return [pf_info,RandomPortfolios]

if __name__=='__main__':
    Market={'Market':('US','^GSPC','我的组合001')}
    Stocks1={'AAPL':.1,'MSFT':.13,'XOM':.09,'JNJ':.09,'JPM':.09}
    Stocks2={'AMZN':.15,'GE':.08,'FB':.13,'T':.14}
    portfolio=dict(Market,**Stocks1,**Stocks2)
    pf_info=portfolio_expret(portfolio,'2019-12-31')
    
    es_alpha=portfolio_es_alpha(pf_info,simulation=50000)

#==============================================================================
if __name__=='__main__':
    simulation=1000
    rate_period='1Y'
    rate_type='treasury'

def portfolio_es_treynor(pf_info,simulation=50000,RF=0):
    """
    功能：基于随机数，生成大量可能的投资组合，计算各个投资组合的风险溢价和贝塔系数，绘制投资组合的可行集
    """
    print("  Calculating portfolio combinations, please wait ...")    
    
    # rf_df已不用；stock_return0为个股日收益率
    [[portfolio,_,stock_return0,rf_df,_],_]=pf_info
    pname=portfolio_name(portfolio)
    scope,mktidx,tickerlist,_,ticker_type=decompose_portfolio(portfolio)
    
    #取出观察期
    hstart0=stock_return0.index[0]; hstart=str(hstart0.strftime("%Y-%m-%d"))
    hend0=stock_return0.index[-1]; hend=str(hend0.strftime("%Y-%m-%d"))    

    #计算市场指数的收益率
    import pandas as pd
    start1=date_adjust(hstart,adjust=-30)
    mkt=get_prices(mktidx,start1,hend)
    mkt['Mkt']=mkt['Close'].pct_change()
    mkt.dropna(inplace=True)
    mkt1=pd.DataFrame(mkt['Mkt'])

    stock_return0m=pd.merge(stock_return0,mkt1,how='left',left_index=True,right_index=True)
    #处理无风险利率
    """
    if RF:
        #rf_df=get_rf_daily(hstart,hend,scope,rate_period,rate_type)
        if not (rf_df is None):
            stock_return1=pd.merge(stock_return0m,rf_df,how='inner',left_index=True,right_index=True)
            for t in tickerlist:
                #计算风险溢价
                stock_return1[t]=stock_return1[t]-stock_return1['rf_daily']
        
            stock_return1['Mkt']=stock_return1['Mkt']-stock_return1['rf_daily']
            stock_return=stock_return1[tickerlist+['Mkt']]
        else:
            print("  #Error(portfolio_es_treynor): failed to retrieve risk-free interest rate, please try again")
            return None
    else:
        #不考虑RF
        stock_return=stock_return0m[tickerlist+['Mkt']]    
    """
    rf_daily=RF/365
    for t in tickerlist:
        #计算风险溢价
        stock_return0m[t]=stock_return0m[t]-rf_daily
        
    stock_return0m['Mkt']=stock_return0m['Mkt']-rf_daily
    # 注意此处stock_return0m和stock_return已不再是stock return，而是风险溢价
    stock_return=stock_return0m[tickerlist+['Mkt']]    
    
    
    #获得成份股个数
    numstocks=len(tickerlist)

    # 设置空的numpy数组，用于存储每次模拟得到的成份股权重、组合的收益率和标准差
    import numpy as np
    random_p = np.empty((simulation,numstocks+2))
    # 设置随机数种子，这里是为了结果可重复
    np.random.seed(RANDOM_SEED)
    # 与其他比率设置不同的随机数种子，意在产生多样性的随机组合

    # 循环模拟simulation次随机的投资组合
    from scipy import stats
    for i in range(simulation):
        # 生成numstocks个随机数放入random9，计算成份股持仓比例放入random_weight
        # 得到一组随机的权重数据
        random9 = np.random.random(numstocks)
        random_weight = random9 / np.sum(random9)
    
        # 计算随机投资组合的历史收益率
        stock_return['pRet']=stock_return[tickerlist].mul(random_weight,axis=1).sum(axis=1)
        
        #回归求贝塔系数作为指数分母
        (beta,alpha,_,_,_)=stats.linregress(stock_return['Mkt'],stock_return['pRet'])        
        
        #计算年化风险溢价
        mean_return=stock_return[tickerlist].mul(random_weight,axis=1).sum(axis=1).mean(axis=0)
        annual_return = (1 + mean_return)**252 - 1
        """
        # 计算随机投资组合的年化平均标准差
        std_return=stock_return.mul(random_weight,axis=1).sum(axis=1).std(axis=0)
        annual_std = std_return*np.sqrt(252)
        """
        # 将上面生成的权重，和计算得到的风险溢价、贝塔系数存入数组random_p中
        # 数组矩阵的前numstocks为随机权重，其后为收益指标，再后为风险指标
        random_p[i][:numstocks] = random_weight
        random_p[i][numstocks] = annual_return
        random_p[i][numstocks+1] = beta
        
        #显示完成进度：需要位于循环体尾部
        print_progress_percent(i,simulation,steps=10,leading_blanks=2)
    
    # 将numpy数组转化成DataFrame数据框
    RandomPortfolios = pd.DataFrame(random_p)
    
    # 设置数据框RandomPortfolios每一列的名称
    RandomPortfolios.columns = [ticker + "_weight" for ticker in tickerlist]  \
                         + ['Risk premium', 'beta']
    # 新增
    RandomPortfolios['Treynor']=RandomPortfolios['Risk premium']/RandomPortfolios['beta']
    
    #return [pf_info,RandomPortfolios]
    return RandomPortfolios

if __name__=='__main__':
    Market={'Market':('US','^GSPC','我的组合001')}
    Stocks1={'AAPL':.1,'MSFT':.13,'XOM':.09,'JNJ':.09,'JPM':.09}
    Stocks2={'AMZN':.15,'GE':.08,'FB':.13,'T':.14}
    portfolio=dict(Market,**Stocks1,**Stocks2)
    pf_info=portfolio_expret(portfolio,'2019-12-31')
    
    es_treynor=portfolio_es_treynor(pf_info,simulation=50000)

#==============================================================================
def RandomPortfolios_plot(RandomPortfolios,col_x,col_y,colorbartxt,title_ext, \
                          ylabeltxt,x_axis_name,pname,simulation,hstart,hend, \
                          hiret_point,lorisk_point,convex_hull=True,frontier='efficient', \
                          facecolor="papayawhip"):
    """
    功能：将生成的马科维茨可行集RandomPortfolios绘制成彩色散点图
    """
    
    """
    #特雷诺比率，对照用
    #RandomPortfolios.plot('beta','Risk premium',kind='scatter',color='y',edgecolors='k')
    pf_ratio = np.array(RandomPortfolios['Risk premium'] / RandomPortfolios['beta'])
    pf_returns = np.array(RandomPortfolios['Risk premium'])
    pf_volatilities = np.array(RandomPortfolios['beta'])

    plt.figure(figsize=(12.8,6.4))
    plt.scatter(pf_volatilities, pf_returns, c=pf_ratio,cmap='RdYlGn', edgecolors='black',marker='o') 
    plt.colorbar(label='特雷诺比率')

    plt.title("投资组合: 马科维茨可行集，基于特雷诺比率")
    plt.ylabel("年化风险溢价")
    
    import datetime as dt; stoday=dt.date.today()
    footnote1="贝塔系数-->"
    footnote2="\n\n基于"+pname+"之成份股构造"+str(simulation)+"个投资组合"
    footnote3="\n观察期间："+hstart+"至"+hend
    footnote4="\n来源: Sina/EM/stooq/fred, "+str(stoday)
    plt.xlabel(footnote1+footnote2+footnote3+footnote4)
    plt.show()
    """    
    DEBUG=False
    
    #RandomPortfolios.plot(col_x,col_y,kind='scatter',color='y',edgecolors='k')
    if not(col_y in ['Alpha']):
        pf_ratio = np.array(RandomPortfolios[col_y] / RandomPortfolios[col_x])
    else:
        pf_ratio = np.array(RandomPortfolios[col_y])
                            
    pf_returns = np.array(RandomPortfolios[col_y])
    pf_volatilities = np.array(RandomPortfolios[col_x])

    #plt.figure(figsize=(12.8,6.4))
    plt.scatter(pf_volatilities, pf_returns, c=pf_ratio,cmap='RdYlGn', edgecolors='black',marker='o') 
    plt.colorbar(label=colorbartxt)

    #绘制散点图轮廓线凸包（convex hull）
    if convex_hull:
        print("  Calculating convex hull ...")
        from scipy.spatial import ConvexHull
        
        #构造散点对的列表
        pf_volatilities_list=list(pf_volatilities)
        pf_returns_list=list(pf_returns)
        points=[]
        for x in pf_volatilities_list:
            pos=pf_volatilities_list.index(x)
            y=pf_returns_list[pos]
            points=points+[[x,y]]
        
        #寻找最左侧的坐标：在x最小的同时，y要最大
        points_df = pd.DataFrame(points, columns=['x', 'y'])
        points_df.sort_values(by=['x','y'],ascending=[True,False],inplace=True)
        x1,y1=points_df.head(1).values[0]
        
        #寻找最高点的坐标：在y最大的同时，x要最小
        points_df.sort_values(by=['y','x'],ascending=[False,True],inplace=True)
        x2,y2=points_df.head(1).values[0]
        
        if DEBUG:
            plt.plot([x1,x2],[y1,y2],ls=':',lw=2,alpha=0.5)
        
        #建立最左侧和最高点之间的拟合直线方程y=a+bx
        a=(x1*y2-x2*y1)/(x1-x2); b=(y1-y2)/(x1-x2)
        def y_bar(x_bar):
            return a+b*x_bar
        
        # 计算散点集的外轮廓
        hull = ConvexHull(points)  
        
        # 绘制外轮廓线
        firsttime_efficient=True; firsttime_inefficient=True
        for simplex in hull.simplices:
            #p1中是一条线段起点和终点的横坐标
            p1=[points[simplex[0]][0], points[simplex[1]][0]]
            px1=p1[0];px2=p1[1]
            #p2中是一条线段起点和终点的纵坐标
            p2=[points[simplex[0]][1], points[simplex[1]][1]]
            py1=p2[0]; py2=p2[1]

            """
            plt.plot([points[simplex[0]][0], points[simplex[1]][0]],
                     [points[simplex[0]][1], points[simplex[1]][1]], 'k-.')   
            """
            #线段起点：px1,py1；线段终点：px2,py2。但也可能互换起点和终点
            if ((py1>=y_bar(px1) or py1==y1) and (py2>=y_bar(px2) or py2==y2)) or \
               ((py1>=y_bar(px2) or py1==y2) and (py2>=y_bar(px1) or py2==y1)) :
                #有效边界
                if frontier.lower() in ['both','efficient']:
                    if firsttime_efficient:
                        plt.plot(p1,p2, 'r--',label=text_lang("有效边界","Efficient Frontier"),lw=3,alpha=0.5)   
                        firsttime_efficient=False
                    else:
                        plt.plot(p1,p2, 'r--',lw=3,alpha=0.5)   
                else:
                    pass
            else:
                #其余边沿
                if frontier.lower() in ['both','inefficient']:
                    if firsttime_inefficient:
                        plt.plot(p1,p2, 'k-.',label=text_lang("无效边界","Inefficient Frontier"),alpha=0.5)
                        firsttime_inefficient=False
                    else:
                        plt.plot(p1,p2, 'k-.',alpha=0.5)
                else:
                    pass
    else:
        #无convex hull
        pass
    
    # 空一行
    print('')

    lang = check_language()
    if lang == 'Chinese':
        if pname == '': pname='投资组合'
        
        plt.title(pname+": 投资组合优化策略，基于"+title_ext,fontsize=title_txt_size)
        plt.ylabel(ylabeltxt,fontsize=ylabel_txt_size)
        
        import datetime as dt; stoday=dt.date.today()
        footnote1=x_axis_name+" -->\n\n"
        footnote2="基于给定证券构造"+str(simulation)+"个投资组合"
        footnote3="\n观察期间："+hstart+"至"+hend
        footnote4="\n数据来源: Sina/EM/Stooq/Yahoo, "+str(stoday)
    else:
        if pname == '': pname='Investment Portfolio'
        
        #plt.title(pname+": Portfolio Optimization, Based on "+title_ext,fontsize=title_txt_size)
        plt.title("Portfolio Optimization: "+pname+", Based on "+title_ext,fontsize=title_txt_size)
        plt.ylabel(ylabeltxt,fontsize=ylabel_txt_size)
        
        import datetime as dt; stoday=dt.date.today()
        footnote1=x_axis_name+" -->\n\n"
        footnote2="Built "+str(simulation)+" portfolios of given securities"
        footnote3="\nPeriod of sample: "+hstart+" to "+hend
        footnote4="\nData source: Sina/EM/Stooq/Yahoo, "+str(stoday)
    
    plt.xlabel(footnote1+footnote2+footnote3+footnote4,fontsize=xlabel_txt_size)
    
    #解析最大比率点和最低风险点信息，并绘点
    [hiret_x,hiret_y,name_hiret]=hiret_point
    #plt.scatter(hiret_x, hiret_y, color='red',marker='*',s=150,label=name_hiret)
    plt.scatter(hiret_x, hiret_y, color='red',marker='*',s=300,label=name_hiret,alpha=0.5)
    
    [lorisk_x,lorisk_y,name_lorisk]=lorisk_point
    #plt.scatter(lorisk_x, lorisk_y, color='m',marker='8',s=100,label=name_lorisk)
    plt.scatter(lorisk_x, lorisk_y, color='blue',marker='8',s=150,label=name_lorisk,alpha=0.5)
    
    plt.legend(loc='best')
    
    plt.gca().set_facecolor(facecolor)
    plt.show()
    
    return
#==============================================================================
#==============================================================================
if __name__=='__main__':
    pname="MSR组合"
    modify_portfolio_name(pname)

def modify_portfolio_name(pname):
    """
    功能：将原来的类似于MSR组合修改为更易懂的名称，仅供打印时使用
    """
    pclist=['等权重组合','交易额加权组合','MSR组合','GMVS组合','MSO组合','GML组合', \
            'MAR组合','GMBA组合', 'MTR组合','GMBT组合']
    
    pclist1=['等权重组合','交易额加权组合', \
            '最佳夏普比率组合(MSR)','夏普比率最小风险组合(GMVS)', \
            '最佳索替诺比率组合(MSO)','索替诺比率最小风险组合(GML)', \
            '最佳阿尔法指标组合(MAR)','阿尔法指标最小风险组合(GMBA)', \
            '最佳特雷诺比率组合(MTR)','特雷诺比率最小风险组合(GMBT)']
    
    if pname not in pclist:
        return pname
    
    pos=pclist.index(pname)
    
    return pclist1[pos]
    
#==============================================================================
def cvt_portfolio_name(pname,portfolio_returns):
    """
    功能：将结果数据表中投资组合策略的名字从英文改为中文
    将原各处portfolio_optimize函数中的过程统一起来
    """

    pelist=['Portfolio','Portfolio_EW','Portfolio_LW','Portfolio_MSR','Portfolio_GMVS', \
           'Portfolio_MSO','Portfolio_GML','Portfolio_MAR','Portfolio_GMBA', \
            'Portfolio_MTR','Portfolio_GMBT']

    lang=check_language()
    if lang == "Chinese":
        """
        pclist=[pname,'等权重组合','交易额加权组合','MSR组合','GMVS组合','MSO组合','GML组合', \
                'MAR组合','GMBA组合', 'MTR组合','GMBT组合']
        """
        pclist=[pname,'等权重组合','交易额加权组合', \
                '最佳夏普比率组合(MSR)','夏普比率最小风险组合(GMVS)', \
                '最佳索替诺比率组合(MSO)','索替诺比率最小风险组合(GML)', \
                '最佳阿尔法指标组合(MAR)','阿尔法指标最小风险组合(GMBA)', \
                '最佳特雷诺比率组合(MTR)','特雷诺比率最小风险组合(GMBT)']
        
    else:
        #"""
        pclist=[pname,'Equal-weighted','Amount-weighted','MSR','GMVS','MSO','GML', \
                'MAR','GMBA', 'MTR','GMBT']
        """
        pclist=[pname,'Equal-weighted','Amount-weighted','Max Sharpe Ratio(MSR)', \
                'Min Risk in Sharpe Ratio(GMVS)','Max Sortino Ratio(MSO)', \
                'Min Risk in Sortino Ratio(GML)','Max Alpha(MAR)','Min Risk in Alpha(GMBA)', \
                'Max Treynor Ratio(MTR)','Min Risk in Treynor Ratio(GMBT)']
        """
        
    pecols=list(portfolio_returns)
    for p in pecols:
        try:
            ppos=pelist.index(p)
        except:
            continue
        else:
            pc=pclist[ppos]
            portfolio_returns.rename(columns={p:pc},inplace=True)

    return portfolio_returns

#==============================================================================

def portfolio_optimize_sharpe(es_info,graph=True,convex_hull=False,frontier='efficient',facecolor='papayawhip'):
    """
    功能：计算投资组合的最高夏普比率组合，并绘图
    MSR: Maximium Sharpe Rate, 最高夏普指数方案
    GMVS: Global Minimum Volatility by Sharpe, 全局最小波动方案
    """

    #需要定制：定义名称变量......................................................
    col_ratio='Sharpe'  #指数名称
    col_y='Risk premium' #指数分子
    col_x='Risk premium volatility'         #指数分母
    
    name_hiret='MSR' #Maximum Sharpe Ratio，指数最高点
    name_lorisk='GMVS' #Global Minimum Volatility by Sharpe，风险最低点

    lang = check_language()
    if lang == 'Chinese':
        title_ext="夏普比率"   #用于标题区别
        """
        if RF:
            colorbartxt='夏普比率(经无风险利率调整后)' #用于彩色棒标签
            ylabeltxt="年化风险溢价" #用于纵轴名称
            x_axis_name="年化风险溢价标准差"   #用于横轴名称 
        else:
            colorbartxt='夏普比率(未经无风险利率调整)' #用于彩色棒标签
            ylabeltxt="年化收益率" #用于纵轴名称
            x_axis_name="年化标准差"   #用于横轴名称 
        """
        colorbartxt='夏普比率' #用于彩色棒标签
        ylabeltxt="年化风险溢价" #用于纵轴名称
        x_axis_name="年化风险溢价标准差"   #用于横轴名称 
        
    else:
        title_ext="Sharpe Ratio"   #用于标题区别
        """
        if RF:
            colorbartxt='Sharpe Ratio(Rf adjusted)' #用于彩色棒标签
            ylabeltxt="Annualized Risk Premium" #用于纵轴名称
            x_axis_name="Annualized Std of Risk Premium"   #用于横轴名称 
        else:
            colorbartxt='Sharpe Ratio(Rf unadjusted)' #用于彩色棒标签
            ylabeltxt="Annualized Return" #用于纵轴名称
            x_axis_name="Annualized Std"   #用于横轴名称 
        """
        colorbartxt='Sharpe Ratio' #用于彩色棒标签
        ylabeltxt="Annualized Risk Premium" #用于纵轴名称
        x_axis_name="Annualized Risk Premium STD"   #用于横轴名称 
        
    #定制部分结束...............................................................
    
    #计算指数，寻找最大指数点和风险最低点，并绘图标注两个点
    hiret_weights,lorisk_weights,portfolio_returns = \
        portfolio_optimize_rar(es_info,col_ratio,col_y,col_x,name_hiret,name_lorisk, \
                           colorbartxt,title_ext,ylabeltxt,x_axis_name,graph=graph, \
                           convex_hull=convex_hull,frontier=frontier,facecolor=facecolor)

    print(text_lang("【注释】","[Notes]"))
    print("★MSR ：Maximized Sharpe Ratio"+text_lang("，最大夏普比率点",''))
    print("◍GMVS：Global Minimized Volatility by Sharpe Ratio"+text_lang("，全局最小夏普比率波动点",''))
    
    return name_hiret,hiret_weights,name_lorisk,lorisk_weights,portfolio_returns
    

if __name__=='__main__':
    Market={'Market':('US','^GSPC','我的组合001')}
    Stocks1={'AAPL':.1,'MSFT':.13,'XOM':.09,'JNJ':.09,'JPM':.09}
    Stocks2={'AMZN':.15,'GE':.08,'FB':.13,'T':.14}
    portfolio=dict(Market,**Stocks1,**Stocks2)
    
    pf_info=portfolio_expret(portfolio,'2019-12-31')
    es_sharpe=portfolio_es_sharpe(pf_info,simulation=50000)
    
    MSR_weights,GMV_weights,portfolio_returns=portfolio_optimize_sharpe(es_sharpe)
    

#==============================================================================

def portfolio_optimize_sortino(es_info,graph=True,convex_hull=False,frontier='efficient',facecolor="papayawhip"):
    """
    功能：计算投资组合的最高索替诺比率组合，并绘图
    MSO: Maximium Sortino ratio, 最高索替诺比率方案
    GML: Global Minimum LPSD volatility, 全局最小LPSD下偏标准差方案
    """

    #需要定制：定义名称变量......................................................
    col_ratio='Sortino'  #指数名称
    col_y='Risk premium' #指数分子
    col_x='Risk premium LPSD'         #指数分母
    
    name_hiret='MSO' #Maximum SOrtino ratio，指数最高点
    name_lorisk='GML' #Global Minimum LPSD，风险最低点

    title_ext=text_lang("索替诺比率","Sortino Ratio")   #用于标题区别
    colorbartxt=text_lang("索替诺比率","Sortino Ratio") #用于彩色棒标签
    ylabeltxt=text_lang("年化风险溢价","Annualized Risk Premium") #用于纵轴名称
    x_axis_name=text_lang("年化风险溢价之下偏标准差","Annualized Risk Premium LPSD")   #用于横轴名称 

    #定制部分结束...............................................................
    
    #计算指数，寻找最大指数点和风险最低点，并绘图标注两个点
    hiret_weights,lorisk_weights,portfolio_returns = \
        portfolio_optimize_rar(es_info,col_ratio,col_y,col_x,name_hiret,name_lorisk, \
                           colorbartxt,title_ext,ylabeltxt,x_axis_name,graph=graph, \
                           convex_hull=convex_hull,frontier=frontier,facecolor=facecolor)

    print(text_lang("【注释】","[Notes]"))
    print("★MSO：Maximum SOrtino ratio"+text_lang("，最大索替诺比率点",''))
    print("◍GML：Global Minimum LPSD"+text_lang("，全局最小LPSD点",''))

    return name_hiret,hiret_weights,name_lorisk,lorisk_weights,portfolio_returns


if __name__=='__main__':
    Market={'Market':('US','^GSPC','我的组合001')}
    Stocks1={'AAPL':.1,'MSFT':.13,'XOM':.09,'JNJ':.09,'JPM':.09}
    Stocks2={'AMZN':.15,'GE':.08,'FB':.13,'T':.14}
    portfolio=dict(Market,**Stocks1,**Stocks2)
    
    pf_info=portfolio_expret(portfolio,'2019-12-31')
    es_sortino=portfolio_es_sortino(pf_info,simulation=50000)
    
    MSO_weights,GML_weights,portfolio_returns=portfolio_optimize_sortino(es_Sortino)
    
    
#==============================================================================
if __name__=='__main__':
    graph=True; convex_hull=False
    
def portfolio_optimize_alpha(es_info,graph=True,convex_hull=False,frontier='efficient',facecolor='papayawhip'):
    """
    功能：计算投资组合的最高詹森阿尔法组合，并绘图
    MAR: Maximium Alpha Ratio, 最高阿尔法指数方案
    GMBA: Global Minimum Beta by Alpha, 全局最小贝塔系数方案
    """

    #需要定制：定义名称变量......................................................
    col_ratio='Alpha'  #指数名称
    col_y='alpha'      #指数：直接做纵轴
    #col_y='Risk premium' #指数分子
    col_x='beta'       #做横轴
    
    name_hiret='MAR' #Maximum Alpha Ratio，指数最高点
    name_lorisk='GMBA' #Global Minimum Beta by Alpha，风险最低点

    title_ext=text_lang("阿尔法指数","Jensen Alpha")   #用于标题区别
    colorbartxt=text_lang("阿尔法指数","Jensen Alpha") #用于彩色棒标签
    ylabeltxt=text_lang("阿尔法指数","Jensen Alpha") #用于纵轴名称
    x_axis_name=text_lang("贝塔系数","Beta")   #用于横轴名称 
    #定制部分结束...............................................................
    
    #计算指数，寻找最大指数点和风险最低点，并绘图标注两个点
    hiret_weights,lorisk_weights,portfolio_returns = \
        portfolio_optimize_rar(es_info,col_ratio,col_y,col_x,name_hiret,name_lorisk, \
                           colorbartxt,title_ext,ylabeltxt,x_axis_name,graph=graph, \
                           convex_hull=convex_hull,frontier=frontier,facecolor=facecolor)

    print(text_lang("【注释】","[Notes]"))
    print("★MAR ：Maximum Alpha Ratio"+text_lang("，最大阿尔法点",''))
    print("◍GMBA：Global Minimum Beta by Alpha"+text_lang("，全局最小阿尔法-贝塔点",''))

    return name_hiret,hiret_weights,name_lorisk,lorisk_weights,portfolio_returns


if __name__=='__main__':
    Market={'Market':('US','^GSPC','我的组合001')}
    Stocks1={'AAPL':.1,'MSFT':.13,'XOM':.09,'JNJ':.09,'JPM':.09}
    Stocks2={'AMZN':.15,'GE':.08,'FB':.13,'T':.14}
    portfolio=dict(Market,**Stocks1,**Stocks2)
    
    pf_info=portfolio_expret(portfolio,'2019-12-31')
    es_alpha=portfolio_es_alpha(pf_info,simulation=50000)
    
    MAR_weights,GMB_weights,portfolio_returns=portfolio_optimize_alpha(es_alpha)
    
#==============================================================================

def portfolio_optimize_treynor(pf_info,RandomPortfolios, \
                               graph=True,convex_hull=False,frontier='efficient', \
                                   facecolor='papayawhip'):
    """
    功能：计算投资组合的最高特雷诺比率组合，并绘图
    MTR: Maximium Treynor Ratio, 最高特雷诺指数方案
    GMBT: Global Minimum Beta by Treynor, 全局最小贝塔系数方案
    """

    #需要定制：定义名称变量......................................................
    col_ratio='Treynor'  #指数名称
    col_y='Risk premium' #绘图纵轴：风险溢价
    #col_y='Treynor'     #纵轴：指数。问题：可行集形状不理想！
    col_x='beta'         #绘图横轴：风险
    
    name_hiret='MTR' #Maximum Treynor Ratio，指数最高点
    name_lorisk='GMBT' #Global Minimum Beta in Treynor，风险最低点

    title_ext=text_lang("特雷诺比率","Treynor Ratio")   #用于标题区别
    colorbartxt=text_lang("特雷诺比率","Treynor Ratio") #用于彩色棒标签
    ylabeltxt=text_lang("年化风险溢价","Annualized Risk Premium") #用于纵轴名称
    #ylabeltxt=text_lang("特雷诺比率·","Treynor Ratio") #用于纵轴名称
    x_axis_name=text_lang("贝塔系数","Beta")   #用于横轴名称 
    #定制部分结束...............................................................
    
    #计算指数，寻找最大指数点和风险最低点，并绘图标注两个点
    hiret_weights,lorisk_weights,portfolio_returns = \
        portfolio_optimize_rar(pf_info,RandomPortfolios, \
                               col_ratio,col_y,col_x,name_hiret,name_lorisk, \
                           colorbartxt,title_ext,ylabeltxt,x_axis_name,graph=graph, \
                           convex_hull=convex_hull,frontier=frontier,facecolor=facecolor)

    print(text_lang("【注释】","[Notes]"))
    print("★MTR ：Maximum Treynor Ratio"+text_lang("，最大特雷诺比率点",''))
    print("◍GMBT：Global Minimum Beta in Treynor"+text_lang("，全局最小特雷诺-贝塔点",''))

    return name_hiret,hiret_weights,name_lorisk,lorisk_weights,portfolio_returns

#==============================================================================
if __name__=='__main__':
    col_ratio,col_y,col_x,name_hiret,name_lorisk,colorbartxt,title_ext,ylabeltxt,x_axis_name= \
        ('Sharpe', 'alpha', 'beta', 'MAR', 'GMBA', '阿尔法指数', '阿尔法指数', '阿尔法指数', '贝塔系数')
    
def portfolio_optimize_rar(pf_info,RandomPortfolios, \
                           col_ratio,col_y,col_x,name_hiret,name_lorisk, \
                           colorbartxt,title_ext,ylabeltxt,x_axis_name,graph=True, \
                           convex_hull=False,frontier='efficient',facecolor='papayawhip'):
    """
    功能：提供rar比率优化的共同处理部分
    基于RandomPortfolios中的随机投资组合，计算相应的指数，寻找最大指数点和风险最小点，并绘图标注两个点
    输入：以特雷诺比率为例
    col_ratio='Treynor'  #指数名称
    col_y='Risk premium' #指数分子
    col_x='beta'         #指数分母
    name_hiret='MTR' #Maximum Treynor Ratio，指数最高点
    name_lorisk='GMBT' #Global Minimum Beta in Treynor，风险最低点
    
    colorbartxt='特雷诺比率' #用于彩色棒标签
    title_ext="特雷诺比率"   #用于标题区别
    ylabeltxt="年化风险溢价" #用于纵轴名称
    x_axis_name="贝塔系数"   #用于横轴名称 
   
    """    
    #解析传入的数据：stock_return为个股日收益率，StockReturns为各个投资组合的日收益率
    #[[[portfolio,thedate,stock_return,_,_],[StockReturns,_,_,_]],RandomPortfolios]=es_info
    [[portfolio,thedate,stock_return,_,_],[StockReturns,_,_,_]]=pf_info
    _,_,tickerlist,_,ticker_type=decompose_portfolio(portfolio)
    numstocks=len(tickerlist)  
    pname=portfolio_name(portfolio)
    
    #取出观察期
    hstart0=StockReturns.index[0]; hstart=str(hstart0.strftime("%Y-%m-%d"))
    hend0=StockReturns.index[-1]; hend=str(hend0.strftime("%Y-%m-%d"))
    
    #识别并计算指数..........................................................
    #if col_ratio.title() in ['Alpha','Treynor']:
    if col_ratio.title() in ['Treynor']:
        #RandomPortfolios中已含有col_ratio字段
        pass
    elif col_ratio.title() in ['Alpha']:
        RandomPortfolios[col_ratio] = RandomPortfolios[col_y]
    elif col_ratio.title() in ['Sharpe','Sortino']:
        RandomPortfolios[col_ratio] = RandomPortfolios[col_y] / RandomPortfolios[col_x]
    else:
        print("  #Error(portfolio_optimize_rar): invalid rar",col_ratio)
        print("  Supported rar(risk-adjusted-return): Treynor, Sharpe, Sortino, Alpha")
        return None
    
    # 找到指数最大数据对应的索引值
    max_index = RandomPortfolios[col_ratio].idxmax()
    # 找出指数最大的点坐标并绘制该点
    hiret_x = RandomPortfolios.loc[max_index,col_x]
    hiret_y = RandomPortfolios.loc[max_index,col_y]
    
    # 提取最高指数组合对应的权重，并转化为numpy数组
    import numpy as np    
    hiret_weights = np.array(RandomPortfolios.iloc[max_index, 0:numstocks])
    # 计算最高指数组合的收益率
    StockReturns['Portfolio_'+name_hiret] = stock_return[tickerlist].mul(hiret_weights, axis=1).sum(axis=1)
    
    # 找到风险最小组合的索引值
    min_index = RandomPortfolios[col_x].idxmin()
    # 提取最小风险组合对应的权重, 并转换成Numpy数组
    # 找出风险最小的点坐标并绘制该点
    lorisk_x = RandomPortfolios.loc[min_index,col_x]
    lorisk_y = RandomPortfolios.loc[min_index,col_y]
    
    # 提取最小风险组合对应的权重，并转化为numpy数组
    lorisk_weights = np.array(RandomPortfolios.iloc[min_index, 0:numstocks])
    # 计算风险最小组合的收益率
    StockReturns['Portfolio_'+name_lorisk] = stock_return[tickerlist].mul(lorisk_weights, axis=1).sum(axis=1)

    #绘制散点图
    simulation=len(RandomPortfolios)
    
    lang = check_language()
    if lang == 'Chinese':
        point_txt="点"
    else:
        point_txt=" Point"
        
    hiret_point=[hiret_x,hiret_y,name_hiret+point_txt]
    lorisk_point=[lorisk_x,lorisk_y,name_lorisk+point_txt]
    if graph:
        RandomPortfolios_plot(RandomPortfolios,col_x,col_y,colorbartxt,title_ext, \
                              ylabeltxt,x_axis_name,pname,simulation,hstart,hend, \
                              hiret_point,lorisk_point,convex_hull=convex_hull, \
                              frontier=frontier,facecolor=facecolor)    

    #返回数据，供进一步分析
    import copy
    #portfolio_returns=StockReturns.copy()
    portfolio_returns=copy.deepcopy(StockReturns)
    
    #将投资组合策略改为中文
    portfolio_returns=cvt_portfolio_name(pname,portfolio_returns)
    
    return hiret_weights,lorisk_weights,portfolio_returns


if __name__=='__main__':
    Market={'Market':('US','^GSPC','我的组合001')}
    Stocks1={'AAPL':.1,'MSFT':.13,'XOM':.09,'JNJ':.09,'JPM':.09}
    Stocks2={'AMZN':.15,'GE':.08,'FB':.13,'T':.14}
    portfolio=dict(Market,**Stocks1,**Stocks2)
    
    pf_info=portfolio_expret(portfolio,'2019-12-31')
    es_treynor=portfolio_es_treynor(pf_info,simulation=50000)
    
    MTR_weights,GMB2_weights,portfolio_returns=portfolio_optimize_treynor(es_treynor)

#==============================================================================
#==============================================================================
if __name__=='__main__':
    ratio='sharpe'
    ratio='alpha'
    ratio='treynor'
    simulation=1000
    simulation=50000
    
    pf_info0=pf_info
    ratio='treynor'    
    
    simulation=10000
    RF=0.046
    graph=True
    hirar_return=True; lorisk=True
    convex_hull=True; frontier='efficient'; facecolor='papayawhip'
    
    

def portfolio_optimize(pf_info0,ratio='sharpe',simulation=10000,RF=0, \
                       graph=True,hirar_return=False,lorisk=True, \
                       convex_hull=True,frontier='efficient',facecolor='papayawhip'):
    """
    功能：集成式投资组合优化策略
    注意：实验发现RF较小时对于结果的影响极其微小难以观察，默认设为不使用无风险利率调整收益
        但RF较大时对于结果的影响明显变大，已经不能忽略！
        若可行集形状不佳，优先尝试pastyears=3，再尝试增加simulation次数。
        simulation数值过大时将导致速度太慢。
    """   
    # 防止原始数据被修改
    import copy
    pf_info=copy.deepcopy(pf_info0)
    
    ratio_list=['treynor','sharpe','sortino','alpha']
    ratio=ratio.lower()
    if not (ratio in ratio_list):
        print("  #Error(portfolio_optimize_strategy): invalid strategy ratio",ratio)
        print("  Supported strategy ratios",ratio_list)
        return
    
    print("  Optimizing portfolio configuration by",ratio,"ratio ...")
    
    [[portfolio,_,_,_,_],_]=pf_info
    pname=portfolio_name(portfolio)
    _,_,_,_,ticker_type=decompose_portfolio(portfolio)
    
    #观察马科维茨可行集：风险溢价-标准差，用于夏普比率优化
    func_es="portfolio_es_"+ratio
    #es_info=eval(func_es)(pf_info=pf_info,simulation=simulation,RF=RF)
    RandomPortfolios=eval(func_es)(pf_info=pf_info,simulation=simulation,RF=RF)


    #寻找比率最优点：最大比率策略和最小风险策略
    func_optimize="portfolio_optimize_"+ratio
    """
    name_hiret,hiret_weights,name_lorisk,lorisk_weights,portfolio_returns= \
        eval(func_optimize)(es_info=es_info,RF=RF,graph=graph)
    """
    """
    name_hiret,hiret_weights,name_lorisk,lorisk_weights,portfolio_returns= \
        eval(func_optimize)(es_info=es_info,graph=graph,convex_hull=convex_hull, \
                            frontier=frontier,facecolor=facecolor)
    """
    name_hiret,hiret_weights,name_lorisk,lorisk_weights,portfolio_returns= \
        eval(func_optimize)(pf_info,RandomPortfolios, \
                            graph=graph,convex_hull=convex_hull, \
                            frontier=frontier,facecolor=facecolor)
    
    
    lang = check_language()
    if lang == 'Chinese':
        zhuhe_txt='组合'
        mingcheng_txt='投资组合名称/策略'
        titletxt="投资组合策略：业绩比较"
        ylabeltxt="持有期收益率"
    else:
        zhuhe_txt=''
        mingcheng_txt='Strategy'
        titletxt="Investment Portfolio Strategy: Performance Comparison"
        ylabeltxt="Holding Period Return"
    
    #打印投资组合构造和业绩表现
    hi_name=modify_portfolio_name(name_hiret+zhuhe_txt)
    lo_name=modify_portfolio_name(name_lorisk+zhuhe_txt)
    portfolio_expectation(hi_name,pf_info,hiret_weights,ticker_type)
    
    if hirar_return:
        scope,mktidx,tickerlist,_,ticker_type=decompose_portfolio(portfolio)
        hwdf=pd.DataFrame(hiret_weights)
        hwdft=hwdf.T
        hwdft.columns=tickerlist
        hwdftt=hwdft.T
        hwdftt.sort_values(by=[0],ascending=False,inplace=True)
        hwdftt['ticker']=hwdftt.index
        hwdftt['weight']=hwdftt[0].apply(lambda x:round(x,4))
        stocks_new=hwdftt.set_index(['ticker'])['weight'].to_dict()
        pname=portfolio_name(portfolio)
        
        Market={'Market':(scope,mktidx,pname)}
        portfolio_new=dict(Market,**stocks_new)
        
    if lorisk:
        portfolio_expectation(lo_name,pf_info,lorisk_weights,ticker_type)

    #现有投资组合的排名
    ranks=portfolio_ranks(portfolio_returns,pname)

    #绘制投资组合策略业绩比较曲线：最多显示4条曲线，否则黑白打印时无法区分
    top4=list(ranks[mingcheng_txt])[:4]
    for p in top4:
        if p in [pname,hi_name,lo_name]:
            continue
        else:
            break
    name_list=[pname,hi_name,lo_name,p]
    
    if graph:
        portfolio_expret_plot(portfolio_returns,name_list,titletxt=titletxt,ylabeltxt=ylabeltxt)
    
    if hirar_return:
        return portfolio_new
    else:
        return
    
#==============================================================================
#==============================================================================
#==============================================================================
#==============================================================================
#==============================================================================
#==============================================================================

def translate_tickerlist(tickerlist):
    newlist=[]
    for t in tickerlist:
        name=ticker_name(t,'bond')
        newlist=newlist+[name]
        
    return newlist
#==============================================================================
# 绘制马科维茨有效边界
#==============================================================================
def ret_monthly(ticker,prices): 
    """
    功能：
    """
    price=prices['Adj Close'][ticker]
    
    import numpy as np
    div=price.pct_change()+1
    logret=np.log(div)
    import pandas as pd
    lrdf=pd.DataFrame(logret)
    lrdf['ymd']=lrdf.index.astype("str")
    lrdf['ym']=lrdf['ymd'].apply(lambda x:x[0:7])
    lrdf.dropna(inplace=True)
    
    mret=lrdf.groupby(by=['ym'])[ticker].sum()
    
    return mret

if __name__=='__main__':
    ticker='MSFT'
    fromdate,todate='2019-1-1','2020-8-1'

#==============================================================================
def objFunction(W,R,target_ret):
    
    import numpy as np
    stock_mean=np.mean(R,axis=0)
    port_mean=np.dot(W,stock_mean) # portfolio mean
    
    cov=np.cov(R.T) # var-cov matrix
    port_var=np.dot(np.dot(W,cov),W.T) # portfolio variance
    penalty = 2000*abs(port_mean-target_ret)# penalty 4 deviation
    
    objfunc=np.sqrt(port_var) + penalty # objective function 
    
    return objfunc   

#==============================================================================
def portfolio_ef_0(stocks,fromdate,todate):
    """
    功能：绘制马科维茨有效前沿，不区分上半沿和下半沿
    问题：很可能出现上下边界折叠的情况，难以解释，弃用!!!
    """
    #Code for getting stock prices
    prices=get_prices(stocks,fromdate,todate)
    
    #Code for generating a return matrix R
    R0=ret_monthly(stocks[0],prices) # starting from 1st stock
    n_stock=len(stocks) # number of stocks
    import pandas as pd
    import numpy as np
    for i in range(1,n_stock): # merge with other stocks
        x=ret_monthly(stocks[i],prices)
        R0=pd.merge(R0,x,left_index=True,right_index=True)
        R=np.array(R0)    

    #Code for estimating optimal portfolios for a given return
    out_mean,out_std,out_weight=[],[],[]
    import numpy as np
    stockMean=np.mean(R,axis=0)
    
    from scipy.optimize import minimize
    for r in np.linspace(np.min(stockMean),np.max(stockMean),num=100):
        W = np.ones([n_stock])/n_stock # starting from equal weights
        b_ = [(0,1) for i in range(n_stock)] # bounds, here no short
        c_ = ({'type':'eq', 'fun': lambda W: sum(W)-1. }) #constraint
        result=minimize(objFunction,W,(R,r),method='SLSQP'
                                    ,constraints=c_, bounds=b_)
        if not result.success: # handle error raise    
            BaseException(result.message)
        
        try:
            out_mean.append(round(r,4)) # 4 decimal places
        except:
            out_mean._append(round(r,4))
            
        std_=round(np.std(np.sum(R*result.x,axis=1)),6)
        try:
            out_std.append(std_)
            out_weight.append(result.x)
        except:
            out_std._append(std_)
            out_weight._append(result.x)

    #Code for plotting the efficient frontier
    
    plt.title('Efficient Frontier of Portfolio')
    plt.xlabel('Standard Deviation of portfolio (Risk))')
    plt.ylabel('Return of portfolio')
    
    out_std_min=min(out_std)
    pos=out_std.index(out_std_min)
    out_mean_min=out_mean[pos]
    x_left=out_std_min+0.25
    y_left=out_mean_min+0.5
    
    #plt.figtext(x_left,y_left,str(n_stock)+' stock are used: ')
    plt.figtext(x_left,y_left,"投资组合由"+str(n_stock)+'种证券构成: ')
    plt.figtext(x_left,y_left-0.05,' '+str(stocks))
    plt.figtext(x_left,y_left-0.1,'观察期间：'+str(fromdate)+'至'+str(todate))
    plt.plot(out_std,out_mean,color='r',ls=':',lw=4)
    
    plt.gca().set_facecolor('papayawhip')
    plt.show()    
    
    return

if __name__=='__main__':
    stocks=['IBM','WMT','AAPL','C','MSFT']
    fromdate,todate='2019-1-1','2020-8-1'   
    portfolio_ef_0(stocks,fromdate,todate)

#==============================================================================
def portfolio_ef(stocks,fromdate,todate):
    """
    功能：多只股票的马科维茨有效边界，区分上半沿和下半沿，标记风险极小点
    问题：很可能出现上下边界折叠的情况，难以解释，弃用!!!
    """
    print("\n  Searching for portfolio information, please wait...")
    #Code for getting stock prices
    prices=get_prices(stocks,fromdate,todate)
    
    #Code for generating a return matrix R
    R0=ret_monthly(stocks[0],prices) # starting from 1st stock
    n_stock=len(stocks) # number of stocks
    
    import pandas as pd
    import numpy as np
    for i in range(1,n_stock): # merge with other stocks
        x=ret_monthly(stocks[i],prices)
        R0=pd.merge(R0,x,left_index=True,right_index=True)
        R=np.array(R0)    

    #Code for estimating optimal portfolios for a given return
    out_mean,out_std,out_weight=[],[],[]
    stockMean=np.mean(R,axis=0)
    
    from scipy.optimize import minimize
    for r in np.linspace(np.min(stockMean),np.max(stockMean),num=100):
        W = np.ones([n_stock])/n_stock # starting from equal weights
        b_ = [(0,1) for i in range(n_stock)] # bounds, here no short
        c_ = ({'type':'eq', 'fun': lambda W: sum(W)-1. }) #constraint
        result=minimize(objFunction,W,(R,r),method='SLSQP'
                                    ,constraints=c_, bounds=b_)
        if not result.success: # handle error raise    
            BaseException(result.message)
        
        try:
            out_mean.append(round(r,4)) # 4 decimal places
            std_=round(np.std(np.sum(R*result.x,axis=1)),6)
            out_std.append(std_)
            out_weight.append(result.x)
        except:
            out_mean._append(round(r,4)) # 4 decimal places
            std_=round(np.std(np.sum(R*result.x,axis=1)),6)
            out_std._append(std_)
            out_weight._append(result.x)
            
    #Code for positioning
    out_std_min=min(out_std)
    pos=out_std.index(out_std_min)
    out_mean_min=out_mean[pos]
    x_left=out_std_min+0.25
    y_left=out_mean_min+0.5
    
    import pandas as pd
    out_df=pd.DataFrame(out_mean,out_std,columns=['mean'])
    out_df_ef=out_df[out_df['mean']>=out_mean_min]
    out_df_ief=out_df[out_df['mean']<out_mean_min]

    #Code for plotting the efficient frontier
    
    plt.title('投资组合：马科维茨有效边界（理想图）')
    
    import datetime as dt; stoday=dt.date.today()    
    plt.xlabel('收益率标准差-->'+"\n数据来源：新浪/EM/stooq, "+str(stoday))
    plt.ylabel('收益率')
    
    plt.figtext(x_left,y_left,"投资组合由"+str(n_stock)+'种证券构成: ')
    plt.figtext(x_left,y_left-0.05,' '+str(stocks))
    plt.figtext(x_left,y_left-0.1,'观察期间：'+str(fromdate)+'至'+str(todate))
    plt.plot(out_df_ef.index,out_df_ef['mean'],color='r',ls='--',lw=2,label='有效边界')
    plt.plot(out_df_ief.index,out_df_ief['mean'],color='k',ls=':',lw=2,label='无效边界')
    plt.plot(out_std_min,out_mean_min,'g*-',markersize=16,label='风险最低点')
    
    plt.legend(loc='best')
    plt.gca().set_facecolor('papayawhip')
    plt.show()    
    
    return

if __name__=='__main__':
    stocks=['IBM','WMT','AAPL','C','MSFT']
    fromdate,todate='2019-1-1','2020-8-1' 
    df=portfolio_ef(stocks,fromdate,todate)

#==============================================================================
if __name__=='__main__':
    tickers=['^GSPC','000001.SS','^HSI','^N225','^BSESN']
    start='2023-1-1'
    end='2023-3-22'
    info_type='Volume'
    df=security_correlation(tickers,start,end,info_type='Close')


def cm2inch(x,y):
    return x/2.54,y/2.54

def security_correlation(tickers,start='L5Y',end='today',info_type='Close', \
                         facecolor='white'):
    """
    ===========================================================================
    功能：股票/指数收盘价之间的相关性
    参数：
    tickers：指标列表，至少两个
    start：起始日期，格式YYYY-MM-DD，支持简易格式
    end：截止日期
    info_type：指标的数值类型，默认'Close', 还可为Open/High/Low/Volume
    facecolor：背景颜色，默认'papayawhip'
    
    返回：相关系数df
    """
        
    start,end=start_end_preprocess(start,end)

    info_types=['Close','Open','High','Low','Volume']
    info_types_cn=['收盘价','开盘价','最高价','最低价','成交量']
    if not(info_type in info_types):
        print("  #Error(security_correlation): invalid information type",info_type)
        print("  Supported information type:",info_types)
        return None
    pos=info_types.index(info_type)
    info_type_cn=info_types_cn[pos]
    
    #屏蔽函数内print信息输出的类
    import os, sys
    class HiddenPrints:
        def __enter__(self):
            self._original_stdout = sys.stdout
            sys.stdout = open(os.devnull, 'w')

        def __exit__(self, exc_type, exc_val, exc_tb):
            sys.stdout.close()
            sys.stdout = self._original_stdout

    print("  Searching for security prices, please wait ...\n")
    with HiddenPrints():
        prices=get_prices_simple(tickers,start,end)
    df=prices[info_type]
    df.dropna(axis=0,inplace=True)
    
    # here put the import lib
    import seaborn as sns
    sns.set(font='SimHei')  # 解决Seaborn中文显示问题
    #sns.set_style('whitegrid',{'font.sans-serif':['SimHei','Arial']}) 
    #sns.set_style('whitegrid',{'font.sans-serif':['FangSong']}) 
    
    import numpy as np
    from scipy.stats import pearsonr

    collist=list(df)
    for col in collist:
        df.rename(columns={col:ticker_name(col,'bond')},inplace=True)
    df_coor = df.corr()


    #fig = plt.figure(figsize=(cm2inch(16,12)))
    #fig = plt.figure(figsize=(cm2inch(12,8)))
    #fig = plt.figure(figsize=(12.8,7.2))
    fig = plt.figure(figsize=(12.8,6.4))
    ax1 = plt.gca()
    
    #构造mask，去除重复数据显示
    mask = np.zeros_like(df_coor)
    mask[np.triu_indices_from(mask)] = True
    mask2 = mask
    mask = (np.flipud(mask)-1)*(-1)
    mask = np.rot90(mask,k = -1)
    
    im1 = sns.heatmap(df_coor,annot=True,cmap="YlGnBu"
                        , mask=mask#构造mask，去除重复数据显示
                        , vmax=1,vmin=-1
                        , cbar=False
                        , fmt='.2f',ax = ax1,annot_kws={"size": 16})
    
    ax1.tick_params(axis = 'both', length=0)
    
    #计算相关性显著性并显示
    rlist = []
    plist = []
    for i in df.columns.values:
        for j in df.columns.values:
            r,p = pearsonr(df[i],df[j])
            try:
                rlist.append(r)
                plist.append(p)
            except:
                rlist._append(r)
                plist._append(p)
    
    rarr = np.asarray(rlist).reshape(len(df.columns.values),len(df.columns.values))
    parr = np.asarray(plist).reshape(len(df.columns.values),len(df.columns.values))
    xlist = ax1.get_xticks()
    ylist = ax1.get_yticks()
    
    widthx = 0
    widthy = -0.15
    
    # 星号的大小
    font_dict={'size':10}
    
    for m in ax1.get_xticks():
        for n in ax1.get_yticks():
            pv = (parr[int(m),int(n)])
            rv = (rarr[int(m),int(n)])
            if mask2[int(m),int(n)]<1.:
                if abs(rv) > 0.5:
                    if  pv< 0.05 and pv>= 0.01:
                        ax1.text(n+widthx,m+widthy,'*',ha = 'center',color = 'white',fontdict=font_dict)
                    if  pv< 0.01 and pv>= 0.001:
                        ax1.text(n+widthx,m+widthy,'**',ha = 'center',color = 'white',fontdict=font_dict)
                    if  pv< 0.001:
                        #print([int(m),int(n)])
                        ax1.text(n+widthx,m+widthy,'***',ha = 'center',color = 'white',fontdict=font_dict)
                else: 
                    if  pv< 0.05 and pv>= 0.01:
                        ax1.text(n+widthx,m+widthy,'*',ha = 'center',color = 'k',fontdict=font_dict)
                    elif  pv< 0.01 and pv>= 0.001:
                        ax1.text(n+widthx,m+widthy,'**',ha = 'center',color = 'k',fontdict=font_dict)
                    elif  pv< 0.001:
                        ax1.text(n+widthx,m+widthy,'***',ha = 'center',color = 'k',fontdict=font_dict)
    
    #plt.title(text_lang("时间序列相关性分析：","Time Series Correlation Analysis: ")+text_lang(info_type_cn,info_type),fontsize=16)
    plt.title(text_lang("时间序列相关性分析","Time Series Correlation Analysis"),fontsize=16)
    plt.tick_params(labelsize=10)
    
    footnote1=text_lang("\n显著性数值：***非常显著(<0.001)，**很显著(<0.01)，*显著(<0.05)，其余为不显著", \
                        "\nSig level: *** Extremely sig(p<0.001), ** Very sig(<0.01), * Sig(<0.05), others unsig")
    footnote2=text_lang("\n系数绝对值：>=0.8极强相关，0.6-0.8强相关，0.4-0.6相关，0.2-0.4弱相关，否则为极弱(不)相关", \
                        "\nCoef. abs: >=0.8 Extreme corr, 0.6-0.8 Strong corr, 0.4-0.6 Corr, <0.4 Weak or uncorr")

    footnote3=text_lang("\n观察期间: ","\nPeriod of sample: ")+start+text_lang('至',' to ')+end
    import datetime as dt; stoday=dt.date.today()    
    footnote4=text_lang("；数据来源：Sina/EM/Stooq/Yahoo，",". Data source: Sina/EM/Stooq/Yahoo, ")+str(stoday)
    
    fontxlabel={'size':8}
    plt.xlabel(footnote1+footnote2+footnote3+footnote4,fontxlabel)
    #plt.xticks(rotation=45)
    
    plt.gca().set_facecolor(facecolor)
    
    #plt.xticks(fontsize=10, rotation=90)
    plt.xticks(fontsize=10, rotation=30)
    plt.yticks(fontsize=10, rotation=0)
    
    plt.show()
    
    return df_coor

#==============================================================================
if __name__ =="__main__":
    portfolio={'Market':('US','^GSPC','Test 1'),'EDU':0.4,'TAL':0.3,'TEDU':0.2}

def portfolio_describe(portfolio):
    describe_portfolio(portfolio)
    return

def describe_portfolio(portfolio):
    """
    功能：描述投资组合的信息
    输入：投资组合
    输出：市场，市场指数，股票代码列表和份额列表
    """
    
    scope,mktidx,tickerlist,sharelist,ticker_type=decompose_portfolio(portfolio)
    pname=portfolio_name(portfolio)
    
    print(text_lang("*** 投资组合名称:","*** Portfolio name:"),pname)
    print(text_lang("所在市场:","Market:"),ectranslate(scope))
    print(text_lang("市场指数:","Market index:"),ticker_name(mktidx,'bond')+'('+mktidx+')')
    print(text_lang("\n*** 成分股及其份额：","\n*** Members and shares:"))    

    num=len(tickerlist)
    #seqlist=[]
    tickerlist1=[]
    sharelist1=[]
    totalshares=0
    for t in range(num):
        #seqlist=seqlist+[t+1]
        tickerlist1=tickerlist1+[ticker_name(tickerlist[t],'bond')+'('+tickerlist[t]+')']
        sharelist1=sharelist1+[str(round(sharelist[t]*100,2))+'%']
        
        totalshares=totalshares+sharelist[t]

    import pandas as pd
    #df=pd.DataFrame({'序号':seqlist,'成分股':tickerlist1,'份额':sharelist1})    
    df=pd.DataFrame({text_lang('成分股','Members'):tickerlist1,text_lang('份额','Shares'):sharelist1})    
    df.index=df.index+1
    
    alignlist=['center','left','right']
    print(df.to_markdown(index=True,tablefmt='plain',colalign=alignlist))
    
    print("*** "+text_lang("成分股份额总和：","Total shares: ")+str(totalshares*100)+'%')
    if totalshares != 1:
        print("  #Warning: total shares is expecting to be 100%")

    return

#==============================================================================    
def portfolio_drop(portfolio,last=0,droplist=[],new_name=''):
    """
    功能：删除最后几个成分股
    """
    scope,mktidx,tickerlist,sharelist,ticker_type=decompose_portfolio(portfolio)  
    pname=portfolio_name(portfolio)
    
    if not (last ==0):
        for i in range(last):
            #print(i)
            tmp=tickerlist.pop()
            tmp=sharelist.pop()

    if not (droplist==[]):
        for d in droplist:
            pos=tickerlist.index(d)
            tmp=tickerlist.pop(pos)
            tmp=sharelist.pop(pos)
        
    stocks_new=dict(zip(tickerlist,sharelist))
    
    if new_name=='':
        new_name=pname
        
    Market={'Market':(scope,mktidx,new_name)}
    portfolio_new=dict(Market,**stocks_new)
    
    return portfolio_new

#==============================================================================
if __name__ =="__main__":
    Market={'Market':('US','^SPX','Meigu #1')}
    Stocks1={'AAPL':.05,#苹果(高科技)
             'MSFT':.2, #微软(高科技)
             'XOM' :.2, #埃克森(石油)
             'JNJ' :.15,#强生(医疗)
             'JPM' :.05,#摩根大通(金融)
            }  
    Stocks2={'AMZN':.15,#亚马逊(电商)
             'META':.10,#元宇宙(社交&电商)
             'T'   :.05,#美国电报电话(通讯)
             'KO'  :.05,#可口可乐(食品饮料)
            }
    portfolio=dict(Market,**Stocks1,**Stocks2)  
    
    name='Meigu #1'
    market='US'
    market_index='000001.SS'
    members={'AAPL':.05,#苹果(高科技)
             'MSFT':.2, #微软(高科技)
             'XOM' :.2, #埃克森(石油)
             'JNJ' :.15,#强生(医疗)
             'JPM' :.05,#摩根大通(金融)
            }  
    
    
    
def portfolio_define(name='My Portfolio', \
                     market='CN', \
                     market_index='000001.SS', \
                         members={}, \
                             check=False):
    """
    功能：定义一个投资组合
    参数：
    name: 投资组合的名字
    economy_entity: 投资组合的成分股所在的经济体
    market_index: 经济体的代表性市场指数
    members: 数据字典，投资组合的各个成分股代码及其所占的股数份额
    
    返回值：投资组合的字典型描述
    """
    
    # 检查市场名称
    market=market.upper()
    if len(market) != 2:
        print("  #Warning(portfolio_define): need a country code of 2 letters")
        return None
    
    #屏蔽函数内print信息输出的类
    import os, sys
    class HiddenPrints:
        def __enter__(self):
            self._original_stdout = sys.stdout
            sys.stdout = open(os.devnull, 'w')

        def __exit__(self, exc_type, exc_val, exc_tb):
            sys.stdout.close()
            sys.stdout = self._original_stdout
    
    error_flag=False
    govt_bond='1Y'+market+'Y.B'
    with HiddenPrints():
        rf_df=get_price_stooq(govt_bond,start='MRW')
    if not(rf_df is None):
        RF=round(rf_df['Close'].mean() / 100.0,6)
        print(f"  Notice: recent annualized RF for {market} market is {RF} (or {round(RF*100,4)}%)")
    else:
        error_flag=True
        print(f"  #Warning(portfolio_define): no RF info found for market {market}")
        print("     Solution: manually define annualized RF value without %")
    
    # 检查是否存在成分股
    if not isinstance(members,dict):
        print("  #Warning(portfolio_define): invalid structure for portfolio members")
        return None
    
    if len(members) == 0:
        print("  #Warning(portfolio_define): no members found in the portfolio")
        return None
    
    try:
        keys=members.keys()
        values=members.values()
    except:
        print("  #Warning(portfolio_define): invalid dict for portfolio members")
        return None
    if len(keys) != len(values):
        print("  #Warning(portfolio_define): number of members and their portions mismatch")
        return None
    
    marketdict={'Market':(market,market_index,name)}
    portfolio=dict(marketdict,**members)
    
    if check:
        print("  Checking portfolio information ...")
        df=None
        with HiddenPrints():
            df=security_indicator(market_index,fromdate='MRW',graph=False)
        if df is None:
            error_flag=True
            print(f"  #Warning(portfolio_define): market index {market_index} not found")
            
        for t in keys:
            with HiddenPrints():
                df=security_indicator(t,fromdate='MRW',graph=False)
            if df is None:
                error_flag=True
                print(f"  #Warning(portfolio_define): portfolio member {t} not found")
    
    if not check:
        print(f"  Notice: portfolio information not fully checked")
    else:
        if not error_flag:
            print(f"  Congratulations! Portfolio is ready to go")
        else:
            print(f"  #Warning(portfolio_define): there are issues in portfolio definition")
            
    return portfolio,RF
        
        
#==============================================================================

def portfolio_feasible(pf_info,simulation=10000,facecolor='papayawhip'):
    """
    功能：绘制投资组合的可行集散点图，仅供教学演示，无实际用途
    """
    fset=portfolio_feset(pf_info,frontier=None, \
                         simulation=simulation,facecolor=facecolor)
    return
#==============================================================================

def portfolio_efficient(pf_info,frontier='Both',simulation=10000,facecolor='papayawhip'):
    """
    功能：绘制投资组合的有效边界散点图，仅供教学演示，无实际用途
    """
    frontier=frontier.title()
    frontier_list=['Efficient','Inefficient','Both']
    if not (frontier in frontier_list):
        print(f"  #Warning: invalid frontier {frontier}")
        print(f"  Valid options for frontier: {frontier_list}")
        return
    
    eset=portfolio_feset(pf_info,frontier=frontier, \
                         simulation=simulation,facecolor=facecolor)
    
    return
    
#==============================================================================


