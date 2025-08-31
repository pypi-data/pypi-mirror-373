# -*- coding: utf-8 -*-
"""
本模块功能：证券投资组合理论优化分析
所属工具包：证券投资分析工具SIAT 
SIAT：Security Investment Analysis Tool
创建日期：2020年7月1日
最新修订日期：2020年7月29日
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
from siat.fama_french import *

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
#plt.rcParams['axes.facecolor']='whitesmoke'

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
                            label_list=[]):
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
        hstart0=retgroup.index[0]; hstart=str(hstart0.date())
        hend0=retgroup.index[-1]; hend=str(hend0.date())
        
        lang = check_language()
        import datetime as dt; stoday=dt.date.today()
        if lang == 'Chinese':
            footnote1="观察期间: "+hstart+'至'+hend
            footnote2="\n数据来源：Sina/EM/Stooq/Yahoo, "+str(stoday)
        else:
            footnote1="Period of observation: "+hstart+' to '+hend
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
    
    plt.gca().set_facecolor('whitesmoke')
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
                     rate_period='1Y',rate_type='shibor',RF=True, \
                         printout=True,graph=True):
    """
    功能：套壳函数portfolio_cumret
    """
    dflist=portfolio_cumret(portfolio=portfolio,thedate=thedate,pastyears=pastyears, \
                     rate_period=rate_period,rate_type=rate_type,RF=RF, \
                         printout=printout,graph=graph)

    return dflist

#==============================================================================
if __name__=='__main__':
    Market={'Market':('US','^GSPC')}
    Market={'Market':('US','^GSPC','我的组合001')}
    Stocks1={'AAPL':.3,'MSFT':.15,'AMZN':.15,'FB':.01,'GOOG':.01}
    Stocks2={'XOM':.02,'JNJ':.02,'JPM':.01,'TSLA':.3,'SBUX':.03}
    portfolio=dict(Market,**Stocks1,**Stocks2)

    ticker_name(portfolio)
    
    thedate='2023-2-17'
    pastyears=1
    rate_period='1Y'
    rate_type='shibor'
    RF=False
    printout=True    

def portfolio_cumret(portfolio,thedate,pastyears=1, \
                     rate_period='1Y',rate_type='shibor',RF=False, \
                         printout=True,graph=True):
    """
    功能：绘制投资组合的累计收益率趋势图，并与等权和期间内交易额加权组合比较
    注意：中国部分历史区段的treasury历史可能无法取得；
    无论是shibor还是treasury的近期利率均可能空缺，只能以最近期的数值填补
    """
    print("\n  Searching for portfolio info, which may take time ...")
    # 解构投资组合
    scope,_,tickerlist,sharelist0,ticker_type=decompose_portfolio(portfolio)
    pname=portfolio_name(portfolio)

    #如果持仓份额总数不为1，则将其转换为总份额为1
    import numpy as np
    totalshares=np.sum(sharelist0)
    if abs(totalshares - 1) >= 0.00001:
        print("\n  #Warning(portfolio_cumret): total weights is",totalshares,"\b, expecting 1.0 here")
        print("  Action: automatically converted into total weights 1.0")
        sharelist=list(sharelist0/totalshares) 
    else:
        sharelist=sharelist0

    #..........................................................................    
    # 计算历史数据的开始日期
    start=get_start_date(thedate,pastyears)
    
    #一次性获得无风险利率，传递给后续函数，避免后续每次获取，耗费时间  
    if RF:
        rf_df=get_rf_daily(start,thedate,scope,rate_period,rate_type)
        #结果字段中，RF是日利率百分比，rf_daily是日利率数值
        if rf_df is None:
            #print("  #Error(portfolio_cumret): failed to retrieve risk-free interest rate in",scope)
            print("  #Warning: all subsequent portfolio optimizations cannot proceed")
            print("  Solution1: try again after until success to include risk-free interest rate in calculation")
            print("  Solution2: use RF=False in script command to ignore risk-free interest rate in calculation")
            return None
    else:
        rf_df=None

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
    
    if printout:
        prices=get_prices_simple(tickerlist,start,thedate)
    else:
        with HiddenPrints():
            prices=get_prices_simple(tickerlist,start,thedate)
            ntickers=len(list(prices['Close']))
            nrecords=len(prices)
        #print("  Successfully retrieved",ntickers,"stocks with",nrecords,"record(s) respectively")
        print("  Successfully retrieved prices of",ntickers,"stocks for",pname)
        
    if prices is None:
        print("  #Error(portfolio_cumret): failed to get portfolio prices",pname)
        return None
    if len(prices) == 0:
        print("  #Error(portfolio_cumret): retrieved empty prices for",pname)
        return None
    #..........................................................................
    
    # 取各个成份股的收盘价
    aclose=prices['Close']    
    member_prices=aclose
    # 计算各个成份股的日收益率，并丢弃缺失值
    StockReturns = aclose.pct_change().dropna()
    if len(StockReturns) == 0:
        print("\n  #Error(portfolio_cumret): retrieved empty returns for",pname)
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
    lang = check_language()
    #..........................................................................
    
    # 绘制原投资组合的收益率曲线，以便使用收益率%来显示
    if graph:
        plotsr = StockReturns['Portfolio']
        plotsr.plot(label=pname)
        plt.axhline(y=0,ls=":",c="red")
        
        if lang == 'Chinese':
            title_txt="投资组合: 日收益率的变化趋势"
            ylabel_txt="日收益率"
            source_txt="数据来源: Sina/EM/Stooq/Yahoo, "
        else:
            title_txt="Investment Portfolio: Daily Return"
            ylabel_txt="Daily Return"
            source_txt="Data source: Sina/EM/Stooq/Yahoo, "
        
        plt.title(title_txt)
        plt.ylabel(ylabel_txt)
        
        stoday = datetime.date.today()
        plt.xlabel(source_txt+str(stoday))
        plt.legend()
        
        plt.gca().set_facecolor('whitesmoke')
        plt.show()
    #..........................................................................
    
    # 计算原投资组合的持有收益率，并绘图
        name_list=["Portfolio"]
        label_list=[pname]
        
        if lang == 'Chinese':    
            titletxt="投资组合: 持有收益率的变化趋势"
            ylabeltxt="持有收益率"
            xlabeltxt="数据来源: Sina/EM/Stooq/Yahoo, "+str(stoday)
        else:
            titletxt="Investment Portfolio: Holding Return"
            ylabeltxt="Holding Return"
            xlabeltxt="Data source: Sina/EM/Stooq/Yahoo, "+str(stoday)
    
    #绘制持有收益率曲线
    if graph:
        cumulative_returns_plot(StockReturns,name_list,titletxt,ylabeltxt,xlabeltxt,label_list)
    #..........................................................................
    
    # 构造等权重组合Portfolio_EW的持有收益率
    numstocks = len(tickerlist)
    # 平均分配每一项的权重
    portfolio_weights_ew = np.repeat(1/numstocks, numstocks)
    # 合成等权重组合的收益，按行横向加总
    StockReturns['Portfolio_EW']=stock_return.mul(portfolio_weights_ew,axis=1).sum(axis=1)
    #..........................................................................
    
    # 创建交易额加权组合：按照成交金额计算期间内交易额均值
    tamount=prices['Close']*prices['Volume']
    tamountlist=tamount.mean(axis=0)    #求列的均值
    tamountlist_array = np.array(tamountlist)
    # 计算成交金额权重
    portfolio_weights_lw = tamountlist_array / np.sum(tamountlist_array)
    # 计算成交金额加权的组合收益
    StockReturns['Portfolio_LW'] = stock_return.mul(portfolio_weights_lw, axis=1).sum(axis=1)

    #绘制累计收益率对比曲线
    if lang == 'Chinese':
        title_txt="投资组合策略：业绩对比"
        Portfolio_EW_txt="等权重策略"
        Portfolio_LW_txt="交易额加权策略"
    else:
        title_txt="Investment Portfolio Strategies: Performance Comparison"
        Portfolio_EW_txt="Equal-weight"
        Portfolio_LW_txt="Amount-weight"
    
    name_list=['Portfolio', 'Portfolio_EW', 'Portfolio_LW']
    label_list=[pname, Portfolio_EW_txt, Portfolio_LW_txt]
    titletxt=title_txt
    
    #绘制各个投资组合的持有收益率曲线
    if graph:
        cumulative_returns_plot(StockReturns,name_list,titletxt,ylabeltxt,xlabeltxt,label_list)

    #打印各个投资组合的持股比例
    member_returns=stock_return
    if printout:
        portfolio_expectation_universal(pname,member_returns,portfolio_weights,member_prices)
        portfolio_expectation_universal(Portfolio_EW_txt,member_returns,portfolio_weights_ew,member_prices)
        portfolio_expectation_universal(Portfolio_LW_txt,member_returns,portfolio_weights_lw,member_prices)

    #返回投资组合的综合信息
    member_returns=stock_return
    portfolio_returns=StockReturns[name_list]
    
    #投资组合名称改名
    portfolio_returns=cvt_portfolio_name(pname,portfolio_returns)
    
    #打印现有投资组合策略的排名
    if printout:
        portfolio_ranks(portfolio_returns,pname)
    
    return [[portfolio,thedate,member_returns,rf_df,member_prices], \
            [portfolio_returns,portfolio_weights,portfolio_weights_ew,portfolio_weights_lw]]

if __name__=='__main__':
    X=portfolio_cumret(portfolio,'2021-9-30')

if __name__=='__main__':
    pf_info=portfolio_cumret(portfolio,'2021-9-30')

#==============================================================================

def portfolio_expret(portfolio,today,pastyears=1, \
                     rate_period='1Y',rate_type='shibor',RF=False,printout=True,graph=True):
    """
    功能：绘制投资组合的持有期收益率趋势图，并与等权和期间内交易额加权组合比较
    套壳原来的portfolio_cumret函数，以维持兼容性
    expret: expanding return，以维持与前述章节名词的一致性
    hpr: holding period return, 持有（期）收益率
    注意：实验发现RF对于结果的影响极其微小难以观察，默认设为不使用无风险利率调整收益，以加快运行速度
    """
    #处理失败的返回值
    results=portfolio_cumret(portfolio,today,pastyears, \
                     rate_period,rate_type,RF,printout,graph)
    if results is None: return None
    
    [[portfolio,thedate,member_returns,rf_df,member_prices], \
            [portfolio_returns,portfolio_weights,portfolio_weights_ew,portfolio_weights_lw]] = results

    return [[portfolio,thedate,member_returns,rf_df,member_prices], \
            [portfolio_returns,portfolio_weights,portfolio_weights_ew,portfolio_weights_lw]]

if __name__=='__main__':
    pf_info=portfolio_expret(portfolio,'2021-9-30')

#==============================================================================
def portfolio_corr(pf_info):
    """
    功能：绘制投资组合成份股之间相关关系的热力图
    """
    [[portfolio,thedate,stock_return,_,_],_]=pf_info
    pname=portfolio_name(portfolio)
    
    #取出观察期
    hstart0=stock_return.index[0]; hstart=str(hstart0.date())
    hend0=stock_return.index[-1]; hend=str(hend0.date())
        
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
    footnote2="\n数据来源：Sina/EM/Stooq/Yahoo, "+str(stoday)
    plt.xlabel(footnote1+footnote2)
    plt.xticks(rotation=90); plt.yticks(rotation=0) 
    
    plt.gca().set_facecolor('whitesmoke')
    plt.show()

    return    

if __name__=='__main__':
    Market={'Market':('US','^GSPC','我的组合001')}
    Stocks1={'AAPL':.1,'MSFT':.13,'XOM':.09,'JNJ':.09,'JPM':.09}
    Stocks2={'AMZN':.15,'GE':.08,'FB':.13,'T':.14}
    portfolio=dict(Market,**Stocks1,**Stocks2)
    pf_info=portfolio_expret(portfolio,'2019-12-31')
    
    portfolio_corr(pf_info)
#==============================================================================
def portfolio_covar(pf_info):
    """
    功能：计算投资组合成份股之间的协方差
    """
    [[portfolio,thedate,stock_return,_,_],_]=pf_info
    pname=portfolio_name(portfolio)
    
    #取出观察期
    hstart0=stock_return.index[0]; hstart=str(hstart0.date())
    hend0=stock_return.index[-1]; hend=str(hend0.date())

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
    footnote2="\n数据来源：Sina/EM/Stooq/Yahoo, "+str(stoday)
    plt.xlabel(footnote1+footnote2)
    plt.xticks(rotation=90)
    plt.yticks(rotation=0) 
    
    plt.gca().set_facecolor('whitesmoke')
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
    
    portfolio_expectation(pf_info)

#==============================================================================
def portfolio_expectation_universal(pname,member_returns,portfolio_weights,member_prices):
    """
    功能：计算给定成份股收益率和持股权重的投资组合年均收益率和标准差
    输入：投资组合名称，成份股历史收益率数据表，投资组合权重series
    输出：年化收益率和标准差
    用途：求出MSR、GMV等持仓策略后计算投资组合的年化收益率和标准差
    """
    
    #观察期
    hstart0=member_returns.index[0]; hstart=str(hstart0.date())
    hend0=member_returns.index[-1]; hend=str(hend0.date())
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
        print("  期末1手组合单位价值:","约"+str(round(portfolio_value_thedate/10000*100,2))+"万")
        print("  观察期间:",hstart+'至'+hend)
        print("  年化收益率:",round(annual_return,4))
        print("  年化标准差:",round(annual_std,4))
        print("  ***投资组合持仓策略***")
        print_tickerlist_sharelist(tickerlist,portfolio_weights,4)
       
        print("  *数据来源：Sina/EM/Stooq/Yahoo, "+str(stoday))
    else:
        print("\n  ======= Investment Portfolio: Return and Risk =======")
        print("  Investment portfolio:",pname)
        print("  Date of analysis:",str(hend))
        print("  Value of portfolio:","about "+str(round(portfolio_value_thedate/1000,2))+"K/portfolio unit")
        print("  Period of observation:",hstart+' to '+hend)
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
def portfolio_expectation(pname,pf_info,portfolio_weights):
    """
    功能：计算给定pf_info和持仓权重的投资组合年均收益率和标准差
    输入：投资组合名称，pf_info，投资组合权重series
    输出：年化收益率和标准差
    用途：求出持仓策略后计算投资组合的年化收益率和标准差，为外部独立使用方便
    """
    [[_,_,member_returns,_,member_prices],_]=pf_info
    
    portfolio_expectation_universal(pname,member_returns,portfolio_weights,member_prices)
    
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
def portfolio_ranks(portfolio_returns,pname):
    """
    功能：区分中英文
    """
    lang = check_language()
    if lang == 'Chinese':
        df=portfolio_ranks_cn(portfolio_returns=portfolio_returns,pname=pname)
    else:
        df=portfolio_ranks_en(portfolio_returns=portfolio_returns,pname=pname)

    return df

#==============================================================================

def portfolio_ranks_cn(portfolio_returns,pname):
    """
    功能：打印现有投资组合的收益率、标准差排名，收益率降序，标准差升序，中文
    """
    #临时保存，避免影响原值
    pr=portfolio_returns.copy()
    
    #以pname组合作为基准
    import numpy as np
    mean_return_pname=pr[pname].mean(axis=0)
    annual_return_pname=round(((1 + mean_return_pname)**252 - 1)*100,2)
    """
    if annual_return_pname > 0:
        pct_style=True  #百分比模式
    else:   #数值模式，直接加减
        pct_style=False
    """
    pct_style=False
    
    std_return_pname=pr[pname].std(axis=0)
    annual_std_pname= round((std_return_pname*np.sqrt(252))*100,2)
    
    import pandas as pd  
    #prr=pd.DataFrame(columns=["名称","年化收益率","收益率变化","年化标准差","标准差变化","收益/风险"])    
    prr=pd.DataFrame(columns=["名称","年化收益率%","收益率变化","年化标准差%","标准差变化","收益/风险"])    
    cols=list(pr)
    for c in cols:
        
        #年化收益率：按列求均值
        mean_return=pr[c].mean(axis=0)
        annual_return = round(((1 + mean_return)**252 - 1)*100,2)
        
        if pct_style:
            return_chg=round((annual_return - annual_return_pname) / annual_return_pname * 100,2)
        else:
            return_chg=round((annual_return - annual_return_pname),2)
        
        #收益率变化    
        if return_chg==0:
            return_chg_str="基准"
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
        annual_std = round((std_return*np.sqrt(252))*100,2)
        
        sharpe_ratio=round(annual_return / annual_std,2)
        
        if pct_style:
            std_chg=round((annual_std - annual_std_pname) / annual_std_pname * 100,1)
        else:
            std_chg=round((annual_std - annual_std_pname),2)
        
        #标准差变化
        if std_chg==0:
            std_chg_str="基准"
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
                       "年化标准差%":annual_std,"标准差变化":std_chg_str,"收益/风险":sharpe_ratio})
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
                  "收益/风险"]]
    prr2.sort_values(by="年化收益率%",ascending=False,inplace=True)
    #prr2.reset_index(inplace=True)
    
    #打印
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

    return prr2   

if __name__=='__main__':
    portfolio_ranks(portfolio_returns,pname)

#==============================================================================

def portfolio_ranks_en(portfolio_returns,pname):
    """
    功能：打印现有投资组合的收益率、标准差排名，收益率降序，标准差升序，英文
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
        
        sharpe_ratio=round(annual_return / annual_std,2)
        
        if pct_style:
            std_chg=round((annual_std - annual_std_pname) / annual_std_pname *100,1)
        else:
            std_chg=round((annual_std - annual_std_pname),5)
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
    simulation=1000
    simulation=50000

def portfolio_es(pf_info,simulation=50000):
    """
    功能：基于随机数，生成大量可能的投资组合，计算各个投资组合的年均收益率和标准差，绘制投资组合的可行集
    """
    [[portfolio,thedate,stock_return,_,_],_]=pf_info
    pname=portfolio_name(portfolio)
    _,_,tickerlist,_,ticker_type=decompose_portfolio(portfolio)
    
    #取出观察期
    hstart0=stock_return.index[0]; hstart=str(hstart0.date())
    hend0=stock_return.index[-1]; hend=str(hend0.date())    
    
    #获得成份股个数
    numstocks=len(tickerlist)

    # 设置空的numpy数组，用于存储每次模拟得到的成份股权重、投资组合的收益率和标准差
    import numpy as np
    random_p = np.empty((simulation,numstocks+2))
    # 设置随机数种子，这里是为了结果可重复
    np.random.seed(RANDOM_SEED)

    # 循环模拟n次随机的投资组合
    print("\n  Calculating portfolio efficient set, please wait ...")    
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
    plt.scatter(pf_volatilities, pf_returns, c=pf_ratio,cmap='RdYlGn', edgecolors='black',marker='o') 
    #plt.grid(True)
    
    import datetime as dt; stoday=dt.date.today()
    lang = check_language()
    if lang == 'Chinese':  
        if pname == '': pname='投资组合'
        
        plt.colorbar(label='收益率/标准差')
        plt.title(pname+": 马科维茨可行(有效)集",fontsize=title_txt_size)
        plt.ylabel("年化收益率",fontsize=ylabel_txt_size)
        
        footnote1="年化收益率标准差-->"
        footnote2="\n\n基于给定的成份证券构造"+str(simulation)+"个投资组合"
        footnote3="\n观察期间："+hstart+"至"+hend
        footnote4="\n数据来源: Sina/EM/Stooq/Yahoo, "+str(stoday)
    else:
        if pname == '': pname='Investment Portfolio'
        
        plt.colorbar(label='Return/Std')
        plt.title(pname+": Efficient Set",fontsize=title_txt_size)
        plt.ylabel("Annualized Return",fontsize=ylabel_txt_size)
        
        footnote1="Annualized Std -->\n\n"
        footnote2="Based on given component securities, constructed "+str(simulation)+" portfolios\n"
        footnote3="Period of sample: "+hstart+" to "+hend
        footnote4="\nData Source: Sina/EM/Stooq/Yahoo, "+str(stoday)
    
    plt.xlabel(footnote1+footnote2+footnote3+footnote4,fontsize=xlabel_txt_size)
    
    plt.gca().set_facecolor('whitesmoke')
    plt.show()

    return [pf_info,RandomPortfolios]

if __name__=='__main__':
    Market={'Market':('US','^GSPC','我的组合001')}
    Stocks1={'AAPL':.1,'MSFT':.13,'XOM':.09,'JNJ':.09,'JPM':.09}
    Stocks2={'AMZN':.15,'GE':.08,'FB':.13,'T':.14}
    portfolio=dict(Market,**Stocks1,**Stocks2)
    pf_info=portfolio_expret(portfolio,'2019-12-31')
    
    es=portfolio_es(pf_info,simulation=50000)

#==============================================================================
if __name__=='__main__':
    simulation=1000
    rate_period='1Y'
    rate_type='treasury'

def portfolio_es_sharpe(pf_info,simulation=1000,rate_period='1Y',rate_type='treasury',RF=True):
    """
    功能：基于随机数，生成大量可能的投资组合，计算各个投资组合的年均风险溢价及其标准差，绘制投资组合的可行集
    """
    print("  Calculating possible portfolio combinations, please wait ...")    
    
    [[portfolio,thedate,stock_return0,rf_df,_],_]=pf_info
    pname=portfolio_name(portfolio)
    scope,_,tickerlist,_,ticker_type=decompose_portfolio(portfolio)
    
    #取出观察期
    hstart0=stock_return0.index[0]; hstart=str(hstart0.date())
    hend0=stock_return0.index[-1]; hend=str(hend0.date())    

    import pandas as pd
    #获得期间内无风险利率
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

def portfolio_es_sortino(pf_info,simulation=1000,rate_period='1Y',rate_type='treasury',RF=True):
    """
    功能：基于随机数，生成大量可能的投资组合，计算各个投资组合的年均风险溢价及其下偏标准差，绘制投资组合的可行集
    """
    print("  Calculating possible portfolio combinations, please wait ...")    
    
    [[portfolio,thedate,stock_return0,rf_df,_],_]=pf_info
    pname=portfolio_name(portfolio)
    scope,_,tickerlist,_,ticker_type=decompose_portfolio(portfolio)
    
    #取出观察期
    hstart0=stock_return0.index[0]; hstart=str(hstart0.date())
    hend0=stock_return0.index[-1]; hend=str(hend0.date())    

    import pandas as pd
    #获得期间内无风险利率
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

def portfolio_es_alpha(pf_info,simulation=1000,rate_period='1Y',rate_type='treasury',RF=True):
    """
    功能：基于随机数，生成大量可能的投资组合，计算各个投资组合的年化标准差和阿尔法指数，绘制投资组合的可行集
    """
    print("  Calculating possible portfolio combinations, please wait ...")    
    
    [[portfolio,thedate,stock_return0,rf_df,_],_]=pf_info
    pname=portfolio_name(portfolio)
    scope,mktidx,tickerlist,_,ticker_type=decompose_portfolio(portfolio)
    
    #取出观察期
    hstart0=stock_return0.index[0]; hstart=str(hstart0.date())
    hend0=stock_return0.index[-1]; hend=str(hend0.date())    

    #计算市场指数的收益率
    import pandas as pd
    start1=date_adjust(hstart,adjust=-30)
    mkt=get_prices(mktidx,start1,hend)
    mkt['Mkt']=mkt['Close'].pct_change()
    mkt.dropna(inplace=True)
    mkt1=pd.DataFrame(mkt['Mkt'])

    stock_return0m=pd.merge(stock_return0,mkt1,how='left',left_index=True,right_index=True)
    #获得期间内无风险利率
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
        #回归求截距项作为阿尔法指数
     
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

def portfolio_es_treynor(pf_info,simulation=1000,rate_period='1Y',rate_type='treasury',RF=True):
    """
    功能：基于随机数，生成大量可能的投资组合，计算各个投资组合的风险溢价和贝塔系数，绘制投资组合的可行集
    """
    print("  Calculating possible portfolio combinations, please wait ...")    
    
    [[portfolio,_,stock_return0,rf_df,_],_]=pf_info
    pname=portfolio_name(portfolio)
    scope,mktidx,tickerlist,_,ticker_type=decompose_portfolio(portfolio)
    
    #取出观察期
    hstart0=stock_return0.index[0]; hstart=str(hstart0.date())
    hend0=stock_return0.index[-1]; hend=str(hend0.date())    

    #计算市场指数的收益率
    import pandas as pd
    start1=date_adjust(hstart,adjust=-30)
    mkt=get_prices(mktidx,start1,hend)
    mkt['Mkt']=mkt['Close'].pct_change()
    mkt.dropna(inplace=True)
    mkt1=pd.DataFrame(mkt['Mkt'])

    stock_return0m=pd.merge(stock_return0,mkt1,how='left',left_index=True,right_index=True)
    #获得期间内无风险利率
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
        # 生成numstocks个随机数放入random9，计算成份股持仓比例放入random_weight，得到一组随机的权重数据
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
        
        #显示完成进度
        print_progress_percent(i,simulation,steps=10,leading_blanks=2)
    
    # 将numpy数组转化成DataFrame数据框
    RandomPortfolios = pd.DataFrame(random_p)
    
    # 设置数据框RandomPortfolios每一列的名称
    RandomPortfolios.columns = [ticker + "_weight" for ticker in tickerlist]  \
                         + ['Risk premium', 'beta']
    
    return [pf_info,RandomPortfolios]

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
                              hiret_point,lorisk_point):
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
    
    #RandomPortfolios.plot(col_x,col_y,kind='scatter',color='y',edgecolors='k')
    
    pf_ratio = np.array(RandomPortfolios[col_y] / RandomPortfolios[col_x])
    pf_returns = np.array(RandomPortfolios[col_y])
    pf_volatilities = np.array(RandomPortfolios[col_x])

    #plt.figure(figsize=(12.8,6.4))
    plt.scatter(pf_volatilities, pf_returns, c=pf_ratio,cmap='RdYlGn', edgecolors='black',marker='o') 
    plt.colorbar(label=colorbartxt)

    lang = check_language()
    if lang == 'Chinese':
        if pname == '': pname='投资组合'
        
        plt.title(pname+": 马科维茨有效(可行)集，基于"+title_ext,fontsize=title_txt_size)
        plt.ylabel(ylabeltxt,fontsize=ylabel_txt_size)
        
        import datetime as dt; stoday=dt.date.today()
        footnote1=x_axis_name+" -->\n\n"
        footnote2="基于设定的成份证券构造"+str(simulation)+"个投资组合"
        footnote3="\n观察期间："+hstart+"至"+hend
        footnote4="\n数据来源: Sina/EM/Stooq/Yahoo, "+str(stoday)
    else:
        if pname == '': pname='Investment Portfolio'
        
        plt.title(pname+": Efficient Set, Based on "+title_ext,fontsize=title_txt_size)
        plt.ylabel(ylabeltxt,fontsize=ylabel_txt_size)
        
        import datetime as dt; stoday=dt.date.today()
        footnote1=x_axis_name+" -->\n\n"
        footnote2="Based on given component securities, constructed "+str(simulation)+" portfolios"
        footnote3="\nPeriod of sample: "+hstart+" to "+hend
        footnote4="\nData source: Sina/EM/Stooq/Yahoo, "+str(stoday)
    
    plt.xlabel(footnote1+footnote2+footnote3+footnote4,fontsize=xlabel_txt_size)
    
    #解析最大比率点和最低风险点信息，并绘点
    [hiret_x,hiret_y,name_hiret]=hiret_point
    #plt.scatter(hiret_x, hiret_y, color='red',marker='*',s=150,label=name_hiret)
    plt.scatter(hiret_x, hiret_y, color='blue',marker='*',s=200,label=name_hiret)
    
    [lorisk_x,lorisk_y,name_lorisk]=lorisk_point
    #plt.scatter(lorisk_x, lorisk_y, color='m',marker='8',s=100,label=name_lorisk)
    plt.scatter(lorisk_x, lorisk_y, color='red',marker='8',s=150,label=name_lorisk)
    
    plt.legend(loc='best')
    
    plt.gca().set_facecolor('whitesmoke')
    plt.show()
    
    return
#==============================================================================
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
        pclist=[pname,'等权重组合','交易额加权组合','MSR组合','GMVS组合','MSO组合','GML组合', \
                'MAR组合','GMBA组合', 'MTR组合','GMBT组合']
    else:
        pclist=[pname,'Equal-weight','Amount-weight','MSR','GMVS','MSO','GML', \
                'MAR','GMBA', 'MTR','GMBT']
        
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

def portfolio_optimize_sharpe(es_info,RF=False,graph=True):
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
        if RF:
            colorbartxt='夏普比率(经无风险利率调整后)' #用于彩色棒标签
            ylabeltxt="年化风险溢价" #用于纵轴名称
            x_axis_name="年化风险溢价标准差"   #用于横轴名称 
        else:
            colorbartxt='夏普比率(未经无风险利率调整)' #用于彩色棒标签
            ylabeltxt="年化收益率" #用于纵轴名称
            x_axis_name="年化标准差"   #用于横轴名称 
    else:
        title_ext="Sharpe Ratio"   #用于标题区别
        if RF:
            colorbartxt='Sharpe Ratio(Rf adjusted)' #用于彩色棒标签
            ylabeltxt="Annualized Risk Premium" #用于纵轴名称
            x_axis_name="Annualized Std of Risk Premium"   #用于横轴名称 
        else:
            colorbartxt='Sharpe Ratio(Rf unadjusted)' #用于彩色棒标签
            ylabeltxt="Annualized Return" #用于纵轴名称
            x_axis_name="Annualized Std"   #用于横轴名称 

    #定制部分结束...............................................................
    
    #计算指数，寻找最大指数点和风险最低点，并绘图标注两个点
    hiret_weights,lorisk_weights,portfolio_returns = \
        portfolio_optimize_rar(es_info,col_ratio,col_y,col_x,name_hiret,name_lorisk, \
                           colorbartxt,title_ext,ylabeltxt,x_axis_name,graph=graph)

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

def portfolio_optimize_sortino(es_info,RF=False,graph=True):
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

    title_ext="索替诺比率"   #用于标题区别
    if RF:
        colorbartxt='索替诺比率(经无风险利率调整后)' #用于彩色棒标签
        ylabeltxt="年化风险溢价" #用于纵轴名称
        x_axis_name="年化风险溢价之下偏标准差"   #用于横轴名称 
    else:
        colorbartxt='索替诺比率(未经无风险利率调整)' #用于彩色棒标签
        ylabeltxt="年化收益率" #用于纵轴名称
        x_axis_name="年化下偏标准差"   #用于横轴名称 
    #定制部分结束...............................................................
    
    #计算指数，寻找最大指数点和风险最低点，并绘图标注两个点
    hiret_weights,lorisk_weights,portfolio_returns = \
        portfolio_optimize_rar(es_info,col_ratio,col_y,col_x,name_hiret,name_lorisk, \
                           colorbartxt,title_ext,ylabeltxt,x_axis_name,graph=graph)

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

def portfolio_optimize_alpha(es_info,RF=False,graph=True):
    """
    功能：计算投资组合的最高詹森阿尔法组合，并绘图
    MAR: Maximium Alpha Ratio, 最高阿尔法指数方案
    GMBA: Global Minimum Beta by Alpha, 全局最小贝塔系数方案
    """

    #需要定制：定义名称变量......................................................
    col_ratio='Sharpe'  #指数名称
    col_y='alpha' #指数分子
    col_x='beta'         #指数分母
    
    name_hiret='MAR' #Maximum Alpha Ratio，指数最高点
    name_lorisk='GMBA' #Global Minimum Beta by Alpha，风险最低点

    title_ext="阿尔法指数"   #用于标题区别
    if RF:
        colorbartxt='阿尔法指数(经无风险利率调整后)' #用于彩色棒标签
    else:
        colorbartxt='阿尔法指数(未经无风险利率调整)' #用于彩色棒标签
    ylabeltxt="阿尔法指数" #用于纵轴名称
    x_axis_name="贝塔系数"   #用于横轴名称 
    #定制部分结束...............................................................
    
    #计算指数，寻找最大指数点和风险最低点，并绘图标注两个点
    hiret_weights,lorisk_weights,portfolio_returns = \
        portfolio_optimize_rar(es_info,col_ratio,col_y,col_x,name_hiret,name_lorisk, \
                           colorbartxt,title_ext,ylabeltxt,x_axis_name,graph=graph)

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

def portfolio_optimize_treynor(es_info,RF=True,graph=True):
    """
    功能：计算投资组合的最高特雷诺比率组合，并绘图
    MTR: Maximium Treynor Ratio, 最高特雷诺指数方案
    GMBT: Global Minimum Beta by Treynor, 全局最小贝塔系数方案
    """

    #需要定制：定义名称变量......................................................
    col_ratio='Treynor'  #指数名称
    col_y='Risk premium' #指数分子
    col_x='beta'         #指数分母
    
    name_hiret='MTR' #Maximum Treynor Ratio，指数最高点
    name_lorisk='GMBT' #Global Minimum Beta in Treynor，风险最低点

    title_ext="特雷诺比率"   #用于标题区别
    if RF:
        colorbartxt='特雷诺比率(经无风险利率调整后)' #用于彩色棒标签
        ylabeltxt="年化风险溢价" #用于纵轴名称
    else:
        colorbartxt='特雷诺比率(未经无风险利率调整)' #用于彩色棒标签
        ylabeltxt="年化收益率" #用于纵轴名称
    x_axis_name="贝塔系数"   #用于横轴名称 
    #定制部分结束...............................................................
    
    #计算指数，寻找最大指数点和风险最低点，并绘图标注两个点
    hiret_weights,lorisk_weights,portfolio_returns = \
        portfolio_optimize_rar(es_info,col_ratio,col_y,col_x,name_hiret,name_lorisk, \
                           colorbartxt,title_ext,ylabeltxt,x_axis_name,graph=graph)

    return name_hiret,hiret_weights,name_lorisk,lorisk_weights,portfolio_returns

#==============================================================================
    
    
def portfolio_optimize_rar(es_info,col_ratio,col_y,col_x,name_hiret,name_lorisk, \
                           colorbartxt,title_ext,ylabeltxt,x_axis_name,graph=True):
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
    #解析传入的数据
    [[[portfolio,thedate,stock_return,_,_],[StockReturns,_,_,_]],RandomPortfolios]=es_info
    _,_,tickerlist,_,ticker_type=decompose_portfolio(portfolio)
    numstocks=len(tickerlist)  
    pname=portfolio_name(portfolio)
    
    #取出观察期
    hstart0=StockReturns.index[0]; hstart=str(hstart0.date())
    hend0=StockReturns.index[-1]; hend=str(hend0.date())
    
    #识别并计算指数..........................................................
    if col_ratio in ['Alpha']:
        RandomPortfolios[col_ratio] = RandomPortfolios[col_y]
    elif col_ratio in ['Treynor','Sharpe','Sortino']:
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
                              hiret_point,lorisk_point)    

    #返回数据，供进一步分析
    portfolio_returns=StockReturns.copy()
    
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

def portfolio_optimize_strategy(pf_info,ratio='sharpe',simulation=50000,RF=False, \
                                graph=True,MSR_return=False,GMVS=True):
    """
    功能：集成式投资组合优化策略
    注意：实验发现RF对于结果的影响极其微小难以观察，默认设为不使用无风险利率调整收益
    """   
    
    ratio_list=['treynor','sharpe','sortino','alpha']
    if not (ratio in ratio_list):
        print("  #Error(portfolio_optimize_strategy): invalid strategy ratio",ratio)
        print("  Supported strategy ratios",ratio_list)
        return
    
    print("  Optimizing portfolio configuration based on",ratio,"ratio ...")
    
    [[portfolio,_,_,_,_],_]=pf_info
    pname=portfolio_name(portfolio)
    
    #观察马科维茨可行集：风险溢价-标准差，用于夏普比率优化
    func_es="portfolio_es_"+ratio
    es_info=eval(func_es)(pf_info=pf_info,simulation=simulation,RF=RF)


    #寻找比率最优点：最大夏普比率策略MSR和最小风险策略GMV
    func_optimize="portfolio_optimize_"+ratio
    name_hiret,hiret_weights,name_lorisk,lorisk_weights,portfolio_returns= \
        eval(func_optimize)(es_info=es_info,RF=RF,graph=graph)

    lang = check_language()
    if lang == 'Chinese':
        zhuhe_txt='组合'
        mingcheng_txt='名称'
        titletxt="投资组合策略：业绩比较"
        ylabeltxt="持有收益率"
    else:
        zhuhe_txt=''
        mingcheng_txt='Portfolio'
        titletxt="Investment Portfolio Strategy: Performance Comparison"
        ylabeltxt="Holding Return"
    
    #打印投资组合构造和业绩表现
    hi_name=name_hiret+zhuhe_txt
    lo_name=name_lorisk+zhuhe_txt
    portfolio_expectation(hi_name,pf_info,hiret_weights)
    
    if MSR_return:
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
        
    if GMVS:
        portfolio_expectation(lo_name,pf_info,lorisk_weights)

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
    
    if MSR_return:
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
    问题：很可能出现上下边界折叠的情况，难以解释，弃用
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
    
    plt.gca().set_facecolor('whitesmoke')
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
    问题：很可能出现上下边界折叠的情况，难以解释，弃用
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
    plt.gca().set_facecolor('whitesmoke')
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

def security_correlation(tickers,start='L5Y',end='today',info_type='Close'):
    """
    ===========================================================================
    功能：股票/指数收盘价之间的相关性
    参数：
    tickers：指标列表，至少两个
    start：起始日期，格式YYYY-MM-DD，支持简易格式
    end：截止日期
    info_type：指标的数值类型，默认'Close', 还可为Open/High/Low/Volume
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

    print("  Searching for security prices, please wait ...")
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
                        ,vmax=1,vmin=-1
                        , fmt='.2f',ax = ax1,annot_kws={"size": 5})
    
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
    font_dict={'size':5}
    
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
    
    plt.title("序列相关性分析："+info_type_cn)
    plt.tick_params(labelsize=5)
    
    footnote1="\n显著性数值：***非常显著(<0.001)，**很显著(<0.01)，*显著(<0.05)，其余为不显著"
    footnote2="\n系数绝对值：>=0.8极强相关，0.6-0.8强相关，0.4-0.6相关，0.2-0.4弱相关，否则为极弱(不)相关"

    footnote3="\n观察期间: "+start+'至'+end
    import datetime as dt; stoday=dt.date.today()    
    footnote4="；数据来源：Sina/EM/Stooq/Yahoo，"+str(stoday)
    
    fontxlabel={'size':5}
    plt.xlabel(footnote1+footnote2+footnote3+footnote4,fontxlabel)
    #plt.xticks(rotation=45)
    
    plt.gca().set_facecolor('whitesmoke')
    plt.show()
    
    return df_coor

#==============================================================================
if __name__ =="__main__":
    portfolio={'Market':('US','^GSPC','Test 1'),'EDU':0.4,'TAL':0.3,'TEDU':0.2}

def describe_portfolio(portfolio):
    """
    功能：描述投资组合的信息
    输入：投资组合
    输出：市场，市场指数，股票代码列表和份额列表
    """
    
    scope,mktidx,tickerlist,sharelist,ticker_type=decompose_portfolio(portfolio)
    pname=portfolio_name(portfolio)
    
    print("*** 投资组合信息:",pname)
    print("\n所在市场:",ectranslate(scope))
    print("市场指数:",ticker_name(mktidx,'bond')+'('+mktidx+')')
    print("成分股及其份额：")    

    num=len(tickerlist)
    #seqlist=[]
    tickerlist1=[]
    sharelist1=[]
    for t in range(num):
        #seqlist=seqlist+[t+1]
        tickerlist1=tickerlist1+[ticker_name(tickerlist[t],'bond')+'('+tickerlist[t]+')']
        sharelist1=sharelist1+[str(round(sharelist[t],2))+'%']

    import pandas as pd
    #df=pd.DataFrame({'序号':seqlist,'成分股':tickerlist1,'份额':sharelist1})    
    df=pd.DataFrame({'成分股':tickerlist1,'份额':sharelist1})    
    df.index=df.index+1
    
    alignlist=['center','left','right']
    print(df.to_markdown(index=True,tablefmt='plain',colalign=alignlist))

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
#==============================================================================
#==============================================================================
#==============================================================================


