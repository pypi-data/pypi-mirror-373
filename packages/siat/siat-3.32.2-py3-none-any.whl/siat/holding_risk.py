# -*- coding: utf-8 -*-
"""
本模块功能：投资组合的VaR(在险价值)和ES(预期损失)分析
所属工具包：证券投资分析工具SIAT 
SIAT：Security Investment Analysis Tool
创建日期：2018年6月16日
最新修订日期：2020年7月23日
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
from siat.common import *
from siat.translate import *
from siat.security_prices import *
from siat.security_price2 import *
#==============================================================================
import matplotlib.pyplot as plt

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

#==============================================================================
import os, sys
class HiddenPrints:
    def __enter__(self):
        self._original_stdout = sys.stdout
        sys.stdout = open(os.devnull, 'w')

    def __exit__(self, exc_type, exc_val, exc_tb):
        sys.stdout.close()
        sys.stdout = self._original_stdout
#==============================================================================

#==============================================================================
if __name__ == '__main__':
    portfolio={'Market':('China','000001.SS'),'300782.SZ':1}
    fromdate='2022-1-1'
    todate='2022-4-18'

def get_portfolio_prices0(portfolio,fromdate,todate):
    """
    功能：抓取投资组合portfolio的每日价值
    输入：投资组合portfolio，开始日期，结束日期
    fromdate: 样本开始日期。格式：'YYYY-MM-DD'
    todate: 样本结束日期。既可以是今天日期，也可以是一个历史日期    
    
    输出：投资组合的价格序列，按照日期升序排列
    """
    
    #解构投资组合
    _,mktidx,tickerlist,sharelist,ticker_type=decompose_portfolio(portfolio)
    
    #检查股票列表个数与份额列表个数是否一致
    if len(tickerlist) != len(sharelist):
        print("#Error(get_portfolio_prices0): numbers of stocks and shares mismatch.")
        return None        
    
    #抓取股票价格
    p=get_prices(tickerlist,fromdate,todate)
    if p is None: return None
    
    import pandas as pd
    #计算投资组合的开盘价
    op=p[['Open']]
    #计算投资组合的价值
    oprice=pd.DataFrame(op.dot(sharelist))
    oprice.rename(columns={0: 'Open'}, inplace=True)    

    #计算投资组合的收盘价
    cp=p[['Close']]
    #计算投资组合的价值
    cprice=pd.DataFrame(cp.dot(sharelist))
    cprice.rename(columns={0: 'Close'}, inplace=True) 
    
    #计算投资组合的调整收盘价
    acp=p[['Adj Close']]
    #计算投资组合的价值
    acprice=pd.DataFrame(acp.dot(sharelist))
    acprice.rename(columns={0: 'Adj Close'}, inplace=True) 
    
    #计算投资组合的交易量
    vol=p[['Volume']]
    #计算投资组合的价值
    pfvol=pd.DataFrame(vol.dot(sharelist))
    pfvol.rename(columns={0: 'Volume'}, inplace=True) 
    
    #计算投资组合的交易金额
    if len(tickerlist)==1:
        p['Amount']=p['Close']*p['Volume']
    else:
        for t in tickerlist:
            p['Amount',t]=p['Close',t]*p['Volume',t]
    amt=p[['Amount']]
    #计算投资组合的价值
    pfamt=pd.DataFrame(amt.dot(sharelist))
    pfamt.rename(columns={0: 'Amount'}, inplace=True) 

    #合成开盘价、收盘价、调整收盘价、交易量和交易金额
    pf1=pd.merge(oprice,cprice,how='inner',left_index=True,right_index=True)    
    pf2=pd.merge(pf1,acprice,how='inner',left_index=True,right_index=True)
    pf3=pd.merge(pf2,pfvol,how='inner',left_index=True,right_index=True)
    pf4=pd.merge(pf3,pfamt,how='inner',left_index=True,right_index=True)
    pf4['Ret']=pf4['Close'].pct_change()

    #获得期间的市场收益率：假设无风险收益率非常小，可以忽略
    m=get_prices(mktidx,fromdate,todate)
    m['Mkt']=m['Close'].pct_change()
    rf_df=m[['Mkt']]
    
    #合并pf4与rf_df
    prices=pd.merge(pf4,rf_df,how='left',left_index=True,right_index=True)

    #提取日期和星期几
    prices['Date']=prices.index.strftime("%Y-%m-%d")
    prices['Weekday']=prices.index.weekday+1

    prices['Portfolio']=str(tickerlist)
    prices['Shares']=str(sharelist)
    prices['Adjustment']=prices.apply(lambda x: \
          False if x['Close']==x['Adj Close'] else True, axis=1)

    pfdf=prices[['Portfolio','Shares','Date','Weekday', \
                 'Open','Close','Adj Close','Adjustment', \
                'Volume','Amount','Ret','Mkt']]  

    #判断空值，控制空值可能引起的程序崩溃
    if pfdf is None:
        print("#Error(get_portfolio_prices0): failed to retrieve portfolio data")
        return None
    pfdf.dropna(inplace=True)
    if (pfdf is None) or (len(pfdf)==0):
        print("#Error(get_portfolio_prices0): failed to retrieve portfolio data")
        return None   

    return pfdf      

    
#==============================================================================
def calc_VaR_normal_standard(ret_series,future_days=1,alpha=0.99):
    
    """
    功能：VaR算法之标准正态法
    输入参数：收益率序列(非百分比)，未来持有时间(天)，置信度
    输出参数：VaR比率，正数
    """
    #去掉空值
    r=ret_series[~ret_series.isnull()]
    
    import numpy as np
    from scipy import stats
    
    z=stats.norm.ppf(1-alpha)
    
    miu_daily=np.mean(r)
    miu_days=np.power(miu_daily+1,future_days)-1
    
    sigma_daily=np.std(r)    
    sigma_days=np.sqrt(future_days)*sigma_daily
    
    VaR_ratio=abs(miu_days+z*sigma_days)

    return VaR_ratio

#==============================================================================
def calc_ES_normal_standard(ret_series,future_days=1,alpha=0.99):
    """
    功能：计算ES，标准正态法
    输入参数：收益率序列，未来持有日期，置信度
    输出：ES比率，正数
    """
    #去掉空值
    r=ret_series[~ret_series.isnull()]
    
    import numpy as np
    from scipy import stats
    
    z=stats.norm.ppf(1-alpha)
    miu_daily=np.mean(r)
    miu_days=np.power(miu_daily+1,future_days)-1
    
    sigma_daily=np.std(r)    
    sigma_days=np.sqrt(future_days)*sigma_daily
    
    zES=-stats.norm.pdf(z)/(1-alpha)
    ratio=abs(miu_days+zES*sigma_days)
    
    return ratio

#==============================================================================
def calc_VaR_normal_modified(ret_series,future_days=1,alpha=0.99):
    """
    功能：VaR算法之修正正态法
    #输入参数：日收益率序列(非百分比)，未来持有日期，置信度
    #输出参数：VaR比率，正数
    """
    #去掉空值
    r=ret_series[~ret_series.isnull()]
    
    from scipy import stats
    import numpy as np

    z=np.abs(stats.norm.ppf(1-alpha))
    S=stats.skew(r)
    K=stats.kurtosis(r)
    
    t1=1/6*(np.power(z,2)-1)*S
    t2=1/24*(np.power(z,3)-3*z)*K
    t3=1/36*(2*np.power(z,3)-5*z)*np.power(S,2)
    t=z+t1+t2-t3
    
    miu_daily=np.mean(r)
    miu_days=np.power(miu_daily+1,future_days)-1
    sigma_daily=np.std(r)    
    sigma_days=np.sqrt(future_days)*sigma_daily
    
    ratio=abs(miu_days+t*sigma_days)
    
    return ratio

#==============================================================================
def calc_ES_normal_modified(ret_series,future_days=1,alpha=0.99):
    """
    功能：ES算法之修正正态法
    #输入参数：日收益率序列(非百分比)，未来持有日期，置信度
    #输出参数：ES比率，正数
    """
    #去掉空值
    r=ret_series[~ret_series.isnull()]
    
    from scipy import stats
    import numpy as np
    
    #计算替代z的t值
    z=np.abs(stats.norm.ppf(1-alpha))
    S=stats.skew(r)
    K=stats.kurtosis(r)
    
    t1=1/6*(np.power(z,2)-1)*S
    t2=1/24*(np.power(z,3)-3*z)*K
    t3=1/36*(2*np.power(z,3)-5*z)*np.power(S,2)
    t=z+t1+t2-t3
    
    miu_daily=np.mean(r)
    miu_days=np.power(miu_daily+1,future_days)-1
    sigma_daily=np.std(r)    
    sigma_days=np.sqrt(future_days)*sigma_daily
    
    #使用t替代原来的z    
    zES=-stats.norm.pdf(t)/(1-alpha)
    ratio=abs(miu_days+zES*sigma_days)
    
    return ratio

#==============================================================================
def get_grouped_rets(ret_series,groupsize=1):
    """
    功能：给定收益率序列pfdf，按照组的大小，在pfdf内创建滚动分组，
    计算每组组内的累计收益率，消除空值，返回组收益率序列
    """
    #测试用数据，测试后应注释掉
    """
    portfolio={'Market':('US','^GSPC'),'AAPL':0.5,'MSFT':0.3,'IBM':0.2}
    fromdate='2019-7-31'
    todate  ='2019-8-31'
    groupsize=2
    #获得投资组合的收益率
    pfdf=get_portfolio_prices0(portfolio,fromdate,todate)    
    import pandas as pd
    ret_series=pd.Series(pfdf['Ret'])
    """    

    #定义组内累计收益率计算方法
    cumret=lambda x:(x+1.0).prod()-1.0
    #使用滚动窗口分组，计算各组收益率gret    
    gret_series=ret_series.rolling(groupsize).apply(cumret)
    gret_series=gret_series[~gret_series.isnull()]
    
    #返回组收益率序列
    return gret_series

#==============================================================================
def calc_VaR_historical(ret_series,future_days=1,alpha=0.99):
    """
    功能：VaR算法之历史模拟法
    输入参数：历史日收益率序列，未来持有日期，置信度
    输出：VaR比率，正数
    """
    #去掉空值
    r0=ret_series[~ret_series.isnull()]
    #按未来持有期间数计算分组收益率
    r=get_grouped_rets(r0,future_days)
    
    import numpy as np
    n=len(r)
    t=int(n*(1-alpha))
    SR=np.sort(r)
    
    if t>=1:
        A=SR[t-1]   #SR的第一个元素的序号是0
    else:
        A=SR[0]
    
    VaR_ratio=abs(A)
    
    return VaR_ratio

#==============================================================================
def calc_ES_historical(ret_series,future_days=1,alpha=0.99):
    """
    功能：ES算法之历史模拟法
    输入参数：历史日收益率序列，未来持有日期，置信度
    输出：ES比率，正数
    要求：足够多的历史数据
    """
    #去掉空值
    r0=ret_series[~ret_series.isnull()]
    #按未来持有期间数计算分组收益率
    r=get_grouped_rets(r0,future_days)
    
    import numpy as np
    n=len(r)
    t=int(n*(1-alpha))
    SR=np.sort(r)
    
    if t>2:
        #SR中第t个元素是VaR，第0~(t-1)个元素的均值是ES
        #SR的第一个元素的序号是0
        A=np.mean(SR[0:(t-2)])  
    else:
        A=SR[0]
    
    ratio=abs(A)
    
    return ratio

if __name__ == '__main__':
    Market={'Market':('China','000001.SS')}
    Stocks={'300782.SZ':2,'300661.SZ':3,'688019.SS':4}
    portfolio=dict(Market,**Stocks)
    prices=get_portfolio_prices0(portfolio,'2019-7-20','2020-7-20')
    ret_series=prices['Ret']
    future_days=3
    alpha=0.99
    
#==============================================================================
def calc_VaR_montecarlo(ret_series,future_days=1,alpha=0.99, \
                        random=10000,mctype='random'):
    """
    功能：VaR算法之蒙特卡洛模拟法，持有多日
    输入参数：历史日收益率序列，未来持有天数，置信度，重复模拟次数，模拟类型
    注：重复模拟次数越多，准确率就越高，但耗时也越多
    输出：持有多天的VaR(金额)
    """
    #去掉空值
    r=ret_series[~ret_series.isnull()]
    
    import pandas as pd
    import numpy as np
    #蒙特卡洛模拟类型：随机数or超采样
    if mctype=='random':    #随机数产生新的序列
        #取得历史日收益率的均值和标准差
        miu=np.mean(r)
        sigma=np.std(r)
        
        #指定随机数种子
        np.random.seed(12345)
        #按照历史日收益率的均值和标准差重复模拟一定次数，生成新的日收益率序列
        RR=pd.Series(np.random.normal(miu,sigma,random))
    else:   #超采样产生新的序列
        #将收益率序列转变为df
        r1=pd.DataFrame(r)
        r2=r1.sample(n=random,replace=True)
        r2.sort_index(inplace=True)
        RR=pd.Series(r2.iloc[:,0])
        """
        r1=np.random.choice(r,size=random,replace=True)
        RR=pd.Series(r1)
        """
        
    #基于新的日收益率序列，使用标准正态法计算VaR
    ratio=calc_VaR_normal_standard(RR,future_days,alpha)        
    #ratio=calc_VaR_historical(RR,future_days,alpha)
    
    return ratio

if __name__ == '__main__':
    random=1000
    mctype='oversampling'

#==============================================================================
def calc_ES_montecarlo(ret_series,future_days=1,alpha=0.99, \
                        random=10000,mctype='random'):
    """
    功能：ES算法之蒙特卡洛模拟法，持有多日
    输入参数：历史日收益率序列，未来持有天数，置信度，重复模拟次数，模拟类型
    注：重复模拟次数越多，准确率就越高，但耗时也越多
    输出：持有多天的ES比率
    """
    #去掉空值
    r=ret_series[~ret_series.isnull()]
    
    import pandas as pd
    import numpy as np
    #蒙特卡洛模拟类型：随机数or超采样
    if mctype=='random':    #随机数产生新的序列
        #取得历史日收益率的均值和标准差
        miu=np.mean(r)
        sigma=np.std(r)
        
        #指定随机数种子
        np.random.seed(12345)
        #按照历史日收益率的均值和标准差重复模拟一定次数，生成新的日收益率序列
        RR=pd.Series(np.random.normal(miu,sigma,random))
    else:   #超采样产生新的序列
        #将收益率序列转变为df
        r1=pd.DataFrame(r)
        r2=r1.sample(n=random,replace=True)
        r2.sort_index(inplace=True)
        RR=pd.Series(r2.iloc[:,0])
        """
        r1=np.random.choice(r,size=random,replace=True)
        RR=pd.Series(r1)
        """
        
    #基于新的日收益率序列，使用标准正态法计算ES
    ratio=calc_ES_normal_standard(RR,future_days,alpha)        
    
    return ratio

#==============================================================================
if __name__ == '__main__':
    portfolio={'Market':('China','000001.SS'),'000661.SZ':2,'603392.SS':3,'300601.SZ':4}
    today='2020-7-20'
    future_days=1
    alpha=0.99
    pastyears=1
    model='all'
    printout=True


def get_VaR_portfolio(portfolio,today,future_days=1,alpha=0.99, \
                      pastyears=1,model='normal_standard',printout=True):
    """
    功能：基于指定模型model，计算投资组合portfolio的VaR金额和比率
    """
    print("  Start working on portfolio VaR, please wait ...")

    #检查model类型
    modellist=['normal_standard','normal_modified','historical','montecarlo', \
               'mc_oversampling','all']
    modeltyp=model.lower()
    if modeltyp not in modellist:
        print("  #Error(get_VaR_portfolio): Unsupported type of model,",model)
        print("  Supported models:",modellist)
        return None,None
    
    #获得样本起始日期
    start=get_start_date(today,pastyears)
    if start is None: return None,None
    
    #抓取投资组合股价和收益率
    print("  Searching for portfolio prices from",start,'to',today)
    prices=get_portfolio_prices0(portfolio,start,today)
    #判断空值，控制空值可能引起的程序崩溃
    if prices is None:
        print("  #Error(get_VaR_portfolio): failed to retrieve portfolio prices")
        return None,None

    prices.dropna(inplace=True)
    if len(prices)==0:
        print("  #Error(get_VaR_portfolio): zero records found for the portfolio")
        return None,None  
    
    num=len(prices)
    ret_series=prices['Ret']
    
    print("  Calculating portfolio VaR ...")
    #计算当日头寸
    position=round(prices['Close'][-1],2)
    VaRlist=[]; ratiolist=[]
    #标准正态法
    if modeltyp in ['normal_standard','all']:
        ratio=calc_VaR_normal_standard(ret_series,future_days,alpha)
        VaR=-round(position*ratio,2)
        VaRlist=VaRlist+[VaR]
        VaR_ratio=round(ratio,4)
        ratiolist=ratiolist+[VaR_ratio]
    
    #修正正态法
    if modeltyp in ['normal_modified','all']:
        ratio=calc_VaR_normal_modified(ret_series,future_days,alpha)
        VaR=-round(position*ratio,2)
        VaRlist=VaRlist+[VaR]
        VaR_ratio=round(ratio,4)
        ratiolist=ratiolist+[VaR_ratio]
    
    #历史模拟法
    if modeltyp in ['historical','all']:
        ratio=calc_VaR_historical(ret_series,future_days,alpha)
        VaR=-round(position*ratio,2)
        VaRlist=VaRlist+[VaR]
        VaR_ratio=round(ratio,4)
        ratiolist=ratiolist+[VaR_ratio]    
    
    #蒙特卡洛模拟法，随机数，默认
    if modeltyp in ['montecarlo','all']:
        ratio=calc_VaR_montecarlo(ret_series,future_days,alpha,mctype='random')
        VaR=-round(position*ratio,2)
        VaRlist=VaRlist+[VaR]
        VaR_ratio=round(ratio,4)
        ratiolist=ratiolist+[VaR_ratio]
    
    #蒙特卡洛模拟法，超采样
    if modeltyp in ['mc_oversampling','all']:
        ratio=calc_VaR_montecarlo(ret_series,future_days,alpha, \
                                  mctype='mc_oversampling')
        VaR=-round(position*ratio,2)
        VaRlist=VaRlist+[VaR]
        VaR_ratio=round(ratio,4)
        ratiolist=ratiolist+[VaR_ratio]    
    
    if not printout: return VaRlist,ratiolist
    
    #输出VaR金额和比率
    print("\n===== 在险价值VaR：投资组合 =====")
    #_,_,tickerlist,sharelist,ticker_type=decompose_portfolio(portfolio)
    #print("成分股列表  :",tickerlist)
    #print("成分股的配置:",sharelist)
    print("投资组合：",portfolio_name(portfolio))
    print("当前日期：",today)
    print("当前头寸(1份投资组合)：",format(position,','))
    print("预计持有天数：",future_days)
    print("置信度水平：",str(int(alpha*100))+'%')
    print("历史样本年数：",pastyears)
    print("样本数量：",num)
    
    import datetime as dt; today=dt.date.today()
    footnote="\n数据来源：新浪/stooq，"+str(today)
    if not (modeltyp == 'all'):
        print("使用的模型：",model)
        print("VaR金额/比率：",format(VaR,','), \
              '\b，',str(round(VaR_ratio*100,2))+'%')
        
        print(footnote)
        return VaR,VaR_ratio
    
    print("\n*** VaR金额/比率 ***")
    modellist.pop()
    for m in modellist:
        pos=modellist.index(m)
        v=VaRlist[pos]
        r=ratiolist[pos]
        print("  ",format(v,','),'\b,', \
              str(round(r*100,2))+'%'+' ('+m+')')

    print(footnote)

    return VaRlist,ratiolist

if __name__ == '__main__':
    portfolio={'Market':('China','000001.SS'),'000661.SZ':1,'603392.SS':2, \
               '300601.SZ':3}
    today='2020-7-20'
    future_days=1
    alpha=0.99
    pastyears=1
    model='all'
    printout=True

#==============================================================================
def get_ES_portfolio(portfolio,today,future_days=1,alpha=0.99, \
                      pastyears=1,model='normal_standard',printout=True):
    """
    功能：基于指定模型model，计算投资组合portfolio的ES金额和比率
    """

    #检查model类型
    modellist=['normal_standard','normal_modified','historical','montecarlo', \
               'mc_oversampling','all']
    modeltyp=model.lower()
    if modeltyp not in modellist:
        print("#Error(get_ES_portfolio): Unsupported type of model,",model)
        print("Supported models:",modellist)
        return None,None
    
    #获得样本起始日期
    start=get_start_date(today,pastyears)
    if start is None: return None,None
    #抓取投资组合股价和收益率
    prices=get_portfolio_prices0(portfolio,start,today)
    #判断空值，控制空值可能引起的程序崩溃
    if prices is None:
        print("#Error(get_ES_portfolio): failed to retrieve portfolio prices")
        return None,None
    prices.dropna(inplace=True)
    if (prices is None) or (len(prices)==0):
        print("#Error(get_ES_portfolio): failed to retrieve portfolio prices")
        return None,None        
    
    num=len(prices)
    ret_series=prices['Ret']
    
    #计算当日头寸
    position=round(prices['Close'][-1],2)
    ESlist=[]; ratiolist=[]
    #标准正态法
    if modeltyp in ['normal_standard','all']:
        ratio=calc_ES_normal_standard(ret_series,future_days,alpha)
        ES=-round(position*ratio,2)
        ESlist=ESlist+[ES]
        ES_ratio=round(ratio,4)
        ratiolist=ratiolist+[ES_ratio]
    
    #修正正态法
    if modeltyp in ['normal_modified','all']:
        ratio=calc_ES_normal_modified(ret_series,future_days,alpha)
        ES=-round(position*ratio,2)
        ESlist=ESlist+[ES]
        ES_ratio=round(ratio,4)
        ratiolist=ratiolist+[ES_ratio]
    
    #历史模拟法
    if modeltyp in ['historical','all']:
        ratio=calc_ES_historical(ret_series,future_days,alpha)
        ES=-round(position*ratio,2)
        ESlist=ESlist+[ES]
        ES_ratio=round(ratio,4)
        ratiolist=ratiolist+[ES_ratio]    
    
    #蒙特卡洛模拟法，随机数，默认
    if modeltyp in ['montecarlo','all']:
        ratio=calc_ES_montecarlo(ret_series,future_days,alpha,mctype='random')
        ES=-round(position*ratio,2)
        ESlist=ESlist+[ES]
        ES_ratio=round(ratio,4)
        ratiolist=ratiolist+[ES_ratio]
    
    #蒙特卡洛模拟法，超采样
    if modeltyp in ['mc_oversampling','all']:
        ratio=calc_ES_montecarlo(ret_series,future_days,alpha, \
                                  mctype='mc_oversampling')
        ES=-round(position*ratio,2)
        ESlist=ESlist+[ES]
        ES_ratio=round(ratio,4)
        ratiolist=ratiolist+[ES_ratio]    
    
    if not printout: return ESlist,ratiolist
    
    #输出ES金额和比率
    print("\n===== 投资组合的预期不足ES =====")
    #_,_,tickerlist,sharelist,ticker_type=decompose_portfolio(portfolio)
    #print("成分股列表  :",tickerlist)
    #print("成分股配置  :",sharelist)
    print("投资组合：",portfolio_name(portfolio))
    print("当前日期：",today)
    print("当前头寸(1份投资组合)：",format(position,','))
    print("预计持有天数：",future_days)
    print("置信度水平：",str(int(alpha*100))+'%')
    print("历史样本年数：",pastyears)
    print("样本个数：",num)

    import datetime as dt; today=dt.date.today()
    footnote="\n数据来源：新浪/stooq，"+str(today)
    
    if not (modeltyp == 'all'):
        print("使用的模型：",model)
        print("ES金额/比率：",format(ES,','), \
              '\b,',str(round(ES_ratio*100,2))+'%')
        print(footnote)
        return ES,ES_ratio
    
    print("ES金额/比率：")
    modellist.pop()
    for m in modellist:
        pos=modellist.index(m)
        v=ESlist[pos]
        r=ratiolist[pos]
        print("  ",format(v,','),'\b,', \
              str(round(r*100,2))+'%'+' ('+m+')')

    print(footnote)

    return ESlist,ratiolist

if __name__ == '__main__':
    portfolio={'Market':('China','000001.SS'),'000661.SZ':1,'603392.SS':2, \
               '300601.SZ':3}
    today='2020-7-20'
    future_days=1
    alpha=0.99
    pastyears=1
    model='all'
    printout=True

#===========================================================================
def ret_Normality_SW(ret_series,siglevel=0.05):
    """
    功能：测试一个投资组合portfolio在给定期间内（fromdate,todate）的收益率序列
    是否符合正态分布
    输入参数：投资组合，开始日期，结束日期，显著性要求水平
    输出：收益率序列正态性检验的W, p-value, Skewness, Kurtosis
    【Shapiro-Wilk正态性检验】原假设：服从正态分布
    """
    #去掉空值
    ret_series=ret_series[~ret_series.isnull()]

    from scipy import stats
    (W,p_value)=stats.shapiro(ret_series)
    
    S=stats.skew(ret_series)
    K=stats.kurtosis(ret_series)
    
    return round(W,4),round(p_value,4),round(S,2),round(K,2)

#===========================================================================
def portfolio_ret_Normality_SW(portfolio,fromdate,todate, \
                               siglevel=0.05,printout=True):
    """
    功能：测试一个投资组合portfolio在给定期间内（fromdate,todate）的收益率序列
    是否符合正态分布
    输入参数：投资组合，开始日期，结束日期，显著性要求水平
    输出：收益率序列正态性检验的p-value
    【Shapiro-Wilk正态性检验】原假设：服从正态分布
    """
    #抓取投资组合股价和收益率
    prices=get_portfolio_prices0(portfolio,fromdate,todate)
    if prices is None: return None,None
    ret_series=prices['Ret']
    num=len(prices)-1
    
    #检验正态分布
    W,p_value,S,K=ret_Normality_SW(ret_series,siglevel)    
    
    if not printout: return W,p_value,S,K
    
    _,_,tickerlist,sharelist,ticker_type=decompose_portfolio(portfolio)
    print("*** Shapiro-Wilk Normality Test ***")
    print("    Stock(s):",tickerlist)
    print("    Holding proportion:",sharelist)    
    print("    Sampling period   :",fromdate,'to',todate)
    print("    Observations      :",num)
    print("    Null hypothesis   : Normal")
    print("    W statistic       :",round(W,4))
    print("    p-value           :",round(p_value,4))
    print("    Skewness          :",round(S,2))
    print("    Kurtosis          :",round(K,2))
    if p_value >= siglevel:
        print("Result: Accept null hypothesis, normal")
    else:
        print("Result: Reject null hypothesis, not normal")
    
    footnote="... Data source: Yahoo Finance"
    print(footnote)
    
    return W,p_value,S,K

#==============================================================================
if __name__ == '__main__':
    portfolio={'Market':('China','000001.SS'),'000661.SZ':0.1,'603392.SS':0.2, \
               '300601.SZ':0.7}
    fromdate='2022-1-1'
    todate='2022-4-18'

def portfolio_rets_curve(portfolio,start='MRY',end='today'):
    """
    功能：绘制投资组合portfolio在给定期间（fromdate,todate）收益率分布的曲线，
    并于相应的正态分布图对照
    显示：收益率分布的直方图(实线)，相应的正态分布图(虚线)
    x轴为收益率(非百分比)，y轴为频度(Frequency)
    """
    fromdate,todate=start_end_preprocess(start,end)
    
    #抓取投资组合股价和收益率
    prices=get_portfolio_prices0(portfolio,fromdate,todate)
    if prices is None: return None,None
    
    num=len(prices)
    rets=prices['Ret']
    W,p_value,S,K=ret_Normality_SW(rets)
    _,_,tickerlist,sharelist,ticker_type=decompose_portfolio(portfolio)
    #计算收益率的均值和标准差
    mu=rets.mean()
    sigma=rets.std()

    #生成符合正态分布的随机数，符合股票收益率的均值和标准差
    import numpy as np
    x=mu+sigma*np.random.randn(10000)    
            
    #plt.figure(figsize=(8,4))
    plt.figure(figsize=(12.8,6.4))
    import seaborn as sns
    #绘制曲线：股票收益率
    sns.kdeplot(data=rets,shade=True,color='blue',legend=True,label='投资组合',lw=4) 
    #绘制曲线：对应的正态分布
    sns.kdeplot(data=x,shade=True,color='r',legend=True,label='正态分布线',ls='--')
    #设置标题、图例、坐标轴标签
    #plt.ylabel('Frequency')
    
    footnote1='日收益率%'
    footnote2='\n【注】Shapiro-Wilk检验：W值'+str(W)+'，p值'+str(p_value)
    footnote3="。偏度"+str(S)+"，峰度"+str(K)
    
    import datetime as dt; today=dt.date.today()
    footnote4="。数据来源：新浪/stooq，"+str(today)
    
    footnote=footnote1+footnote2+footnote3+footnote4
    plt.xlabel(footnote)
    
    plt.legend(loc='best')
    """
    titletxt1="投资组合收益率的正态分布检验"
    titletxt2="\n成分股"+str(tickerlist)
    titletxt3="\n持仓配置"+str(sharelist)
    titletxt4="\n样本期间："+str(fromdate)+'至'+str(todate)+ \
                '，样本数量'+str(num)+'个'
    titletxt=titletxt1+titletxt2+titletxt3+titletxt4
    """
    titletxt="投资组合收益率的正态分布检验："+portfolio_name(portfolio)
    plt.title(titletxt)
    
    plt.gca().set_facecolor('whitesmoke')
    plt.show()

    return
    

#==============================================================================
