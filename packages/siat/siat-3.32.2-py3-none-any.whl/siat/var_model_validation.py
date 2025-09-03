# -*- coding: utf-8 -*-
"""
本模块功能：检验VaR(在险价值)模型计算结果的有效性
所属工具包：证券投资分析工具SIAT 
SIAT：Security Investment Analysis Tool
创建日期：2019年7月16日
最新修订日期：2019年8月19日
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
#==============================================================================
def calc_ret(price_series,groupsize=1):
    """
    功能：计算日收益率，根据分组大小，计算组内累计收益率
    输入参数：价格序列数据框，分组大小(默认为1，即不分组)
    输出：带分组的收益率序列，数据框
    """  

    #仅用于测试
    #price_series=get_price(['AAPL'],[1],'2019-1-1','2019-8-18')       
    #groupsize=3
        
    #计算日收益率
    import pandas as pd
    #rets=pd.DataFrame(price_series['Value'].pct_change())
    rets=pd.DataFrame(price_series['Close'].pct_change())
    
    import numpy as np
    if groupsize >1:        
        group=np.arange(1,groupsize)        
        colname=rets.columns.to_list()[0]
        for i in group:
            #print(i)
            newcol="Shift"+i.astype('str')
            rets[newcol]=rets[colname].shift(i)            
    rets=rets.dropna()
    rets['Ret']=rets.apply(lambda row:np.product(1+row),axis=1)-1 

    #ret_group=pd.DataFrame(rets['Ret'])  
    ret_group=rets['Ret']        
    return ret_group        
        
        
if __name__ =="__main__":
    p=get_prices_portfolio(['AAPL','MSFT'],[1,1],'2019-1-1','2019-8-18')
    rg=calc_ret(p,5)            
        
        
#==============================================================================
def VaR_normal_standard(position,ret_series,future_days=1,alpha=0.99):
    
    """
    标准正太法VaR基本算法
    输入参数：当前持有头寸金额，收益率序列(非百分比)，未来持有时间(天)，置信度
    输出参数：VaR(金额，单位与当前头寸的金额单位相同)，负数
    """
    import numpy as np
    from scipy import stats
    
    #注意：这里z为负数
    z=stats.norm.ppf(1-alpha)
    miu_daily=np.mean(ret_series)
    #print("DEBUG: miu_daily",miu_daily)
    miu_days=np.power(miu_daily+1,future_days)-1
    sigma_daily=np.std(ret_series) 
    #print("DEBUG: sigma_daily",sigma_daily)
    sigma_days=np.sqrt(future_days)*sigma_daily
    
    ratio=miu_days+z*sigma_days
    #print("DEBUG: ratio",ratio)
    #损失份额最多100%全损
    if np.abs(ratio) > 1.0: ratio=-1.0
    VaR_days=position*ratio
    return -abs(VaR_days)


if __name__ == "__main__":
    price=get_prices_portfolio(['AAPL'],[1],'2019-1-1','2019-8-8')
    position=price['Close'][-1]
    ret=calc_ret(price)
    VaR=VaR_normal_standard(position,ret)
#==============================================================================
def VaR_normal_modified(position,ret_series,future_days=1,alpha=0.99):
    """
    功能：VaR基本算法，修正正态法
    #输入参数：持有头寸金额，日收益率序列，未来持有日期，置信度
    #输出参数：VaR(金额)
    """
    from scipy import stats
    import numpy as np

    z=np.abs(stats.norm.ppf(1-alpha))
    S=stats.skew(ret_series)
    K=stats.kurtosis(ret_series)
    
    t1=1/6*(np.power(z,2)-1)*S
    t2=1/24*(np.power(z,3)-3*z)*K
    t3=1/36*(2*np.power(z,3)-5*z)*np.power(S,2)
    t=z+t1+t2-t3
    
    miu_daily=np.mean(ret_series)
    miu_days=np.power(miu_daily+1,future_days)-1
    sigma_daily=np.std(ret_series)    
    sigma_days=np.sqrt(future_days)*sigma_daily
    
    #最多100%全损
    ratio=miu_days+t*sigma_days
    if np.abs(ratio) > 1.0: ratio=-1.0
    VaR_days=position*ratio
    return -abs(VaR_days)
#==============================================================================
def VaR_historical_1d(position,ret_series,alpha=0.99):
    """
    功能：计算VaR基本算法，历史模拟法，持有1天
    输入参数：持有头寸金额，历史日收益率序列，置信度
    输出：持有一天的VaR(金额)
    """
    import numpy as np
    n=len(ret_series)
    t=int(n*(1-alpha))
    SR=np.sort(ret_series)
    A=SR[t-1]   #SR的第一个元素的序号是0
    VaR_1d=position*A
    return -abs(VaR_1d)
#==============================================================================
def VaR_montecarlo(position,ret_series, \
                future_days=1,alpha=0.99,random=10000):
    """
    功能：计算VaR基本算法，蒙特卡洛模拟法，持有多日
    输入参数：当前头寸金额，历史日收益率序列，未来持有天数，置信度，重复模拟次数
    注：重复模拟次数越多，准确率就越高，但耗时也越多
    输出：持有多天的VaR(金额)
    """
    import numpy as np
    #取得历史日收益率的均值和标准差
    miu=np.mean(ret_series)
    sigma=np.std(ret_series)
    #生成随机数序列
    np.random.seed(12345)
    #按照历史日收益率的均值和标准差重复模拟一定次数，生成新的日收益率序列
    RR=np.random.normal(miu,sigma,random)
    #基于新的日收益率序列，使用标准正态法计算VaR
    VaR_days=VaR_normal_standard(position,RR,future_days,alpha)
    
    #最多100%全损
    if abs(VaR_days) > position: VaR_days=-position
    
    return -abs(VaR_days)
#==============================================================================
def calc_VaR_1d(position,ret_series,alpha=0.99,model="montecarlo", \
                random=10000):
    """
    功能：计算一个期间的VaR，允许指定不同的模型
    输入参数：当前头寸，各个期间的收益率序列，置信度，模型，模拟次数(仅适用于蒙特卡洛模型)
    输出：VaR金额
    """
    
    future_days=1
    #判断模型选择
    modeltype=model.lower()
    if modeltype in ['normal_standard','normal standard','ns']:
        #标准正态法
        mtype='normal_standard'
        VaR=VaR_normal_standard(position,ret_series,future_days,alpha)
    elif modeltype in ['normal_modified','normal modified','nm']:
        #修正正态法
        mtype='normal_modified'
        VaR=VaR_normal_modified(position,ret_series,future_days,alpha)
    elif modeltype in ['historical','historic','history','hist']:
        #历史模拟法
        mtype='historical'
        VaR=VaR_historical_1d(position,ret_series,alpha)
    elif modeltype in ['montecarlo','monte carlo','monte_carlo','mc']:
        #蒙特卡洛模拟法
        mtype='montecarlo'
        VaR=VaR_montecarlo(position,ret_series,future_days,alpha,random)
    else:
        print("Error #1(calc_VaR_1d): Type of model unsupported")        
        print("Variable(s):",model)
        print("Models supported: normal_standard, normal_modificed, historical, montecarlo")
        return None

    return mtype,VaR
    

if __name__ == "__main__":
    tickerlist=['AAPL','MSFT']
    sharelist=[1,2]
    start='2019-1-1'
    end='2019-6-30'     
    price=get_prices_portfolio(tickerlist,sharelist,start,end)
    
    groupsize=5
    ret=calc_ret(price,groupsize)
    
    position=price['Close'][-1]
    alpha=0.99
    type,VaR=calc_VaR_1d(position,ret,alpha,model="montecarlo")
    ratio=abs(VaR/position)
    
    threshhold_expected=round(len(ret)*(1-alpha),2)
    threshhold_actual=len(ret[ret['Ret']<-ratio])


#==============================================================================



def backtest_VaR(tickerlist,sharelist,today,future_days=1, \
                alpha=0.99,pastyears=1,model="montecarlo",random=10000):
    """
    功能：检验VaR模型的有效性，历史回溯测试
    输入参数：股票代码列表，持有股数列表，当前日期，预期持有天数，置信度，
    使用历史书据的年数，模型类型，模拟次数(仅适用于蒙特卡洛法)
    """
    
    #检查当前日期的合理性
    if not check_date(today): return
    
    #计算开始日期
    startdate=get_start_date(today,pastyears)
    import pandas as pd
    enddate=pd.to_datetime(today)
    
    #下载股价数据
    price=get_prices_portfolio(tickerlist,sharelist,startdate,enddate)
    #计算收益率，以future_days作为分组大小
    ret=calc_ret(price,future_days)
    
    #计算当前持有的头寸
    position=price['Close'][-1]
    #计算VaR
    type,VaR=calc_VaR_1d(position,ret,alpha,model)
    #计算VaR比率
    ratio=abs(VaR/position)
    
    #预期：收益率低于VaR比率的期数（天数或组数）
    threshhold_expected=round(len(ret)*(1-alpha),2)
    #实际：收益率低于VaR比率的期数（天数或组数）
    threshhold_actual=len(ret[ret<-ratio])
    alpha_actual=1-threshhold_actual/len(ret)
    
    #结果判读
    if abs(alpha_actual-alpha) < 0.001:
        result="准确"
    elif alpha_actual < alpha:
        result="低估"
    else: 
        result="高估"
    
    #打印结果
    """
    print("\n======= VaR模型：回溯测试 =======")
    #print("投资组合          :",ticker_name(tickerlist))
    print("投资组合          :",end='')
    print_list(ticker_name(tickerlist,'bond'))
    
    print("成分股票配置      :",sharelist)
    print("持有日期          :",today)
    print("当前头寸          :",format(round(position,2),','))
    print("预计持有天数      :",future_days,"天")
    print("置信度水平        : ",alpha*100,"%",sep='')
    print("使用的历史样本数据:",pastyears,"年")
    print("使用的VaR模型     :",type)
    
    print("\n*** 在险价值 ***")
    print("VaR金额:",format(round(VaR,2),','))
    print("VaR比率: ",round(ratio*100,2),"%",sep='')
    
    print("\n*** 回溯测试 ***")
    print("期望的置信度水平       : ",alpha*100,"%",sep='')
    print("损失超过VaR的预期天数  :",threshhold_expected,'天')
    print("损失超过VaR的实际天数  :",threshhold_actual,'天')  
    print("实际的置信度水平       : ",round(alpha_actual*100,2),"%",sep='')
    print("模型验证的回溯测试结果 :",result)
    """
    
    titletxt="VaR模型：回溯测试"
    import datetime as dt; todaydt=dt.date.today()
    footnote="数据来源：新浪/stooq，"+str(todaydt)
    ticker_name_list=list2str(ticker_name(tickerlist,'bond'))
    shares=sharelist
    if len(sharelist)==1: shares=sharelist[0]
    
    data_dict={'持有资产：':ticker_name_list, \
               '资产配置：':shares, \
               '持有日期：':today, \
               '预计持有天数：':str(future_days)+'天', \
               '置信度：':str(alpha*100)+'%', \
               "使用的历史样本数据：":str(pastyears)+"年", \
               "使用的VaR模型：":type, \
                   
               "*** 在险价值 ***":'', \
               "VaR金额：":format(round(VaR,2),','), \
               "VaR比率：":str(round(ratio*100,2))+"%", \
               
               "*** 回溯测试 ***":'', \
               "期望的置信度水平：":str(alpha*100)+"%", \
               "损失超过VaR的预期天数：":str(threshhold_expected)+'天', \
               "损失超过VaR的实际天数：":str(threshhold_actual)+'天', \
               "实际的置信度水平：":str(round(alpha_actual*100,2))+"%", \
               "模型验证的回溯测试结果：":result}
    
    print2CSS(data_dict,titletxt=titletxt,footnote=footnote)
    
    
    return
    
if __name__ == "__main__": 
    tickerlist=['AAPL']
    sharelist=[1]
    backtest_VaR(tickerlist,sharelist,'2019-8-8',1, \
                 pastyears=1,model="montecarlo")
    backtest_VaR(tickerlist,sharelist,'2019-8-8',1, \
                 pastyears=1,model="normal_standard")    
    backtest_VaR(tickerlist,sharelist,'2019-8-8',1, \
                 pastyears=1,model="normal_modified") 
    backtest_VaR(tickerlist,sharelist,'2019-8-8',1, \
                 pastyears=1,model="historical")     

#==============================================================================
def backtest_VaR_portfolio(portfolio,today,future_days=1, \
                alpha=0.99,pastyears=1,model="montecarlo",random=10000):
    """
    功能：检验VaR模型的有效性，历史回溯测试
    输入参数：股票代码列表，持有股数列表，当前日期，预期持有天数，置信度，
    使用历史书据的年数，模型类型，模拟次数(仅适用于蒙特卡洛法)
    """
    
    #检查当前日期的合理性
    if not check_date(today): return
    
    #解构投资组合
    _,_,tickerlist,sharelist,ticker_type=decompose_portfolio(portfolio)
    
    #计算开始日期
    startdate=get_start_date(today,pastyears)
    import pandas as pd
    enddate=pd.to_datetime(today)
    
    #下载股价数据
    price=get_prices_portfolio(tickerlist,sharelist,startdate,enddate)
    #计算收益率，以future_days作为分组大小
    ret=calc_ret(price,future_days)
    
    #计算当前持有的头寸
    position=price['Close'][-1]
    #计算VaR
    type,VaR=calc_VaR_1d(position,ret,alpha,model)
    #计算VaR比率
    ratio=abs(VaR/position)
    
    #预期：收益率低于VaR比率的期数（天数或组数）
    threshhold_expected=round(len(ret)*(1-alpha),2)
    #实际：收益率低于VaR比率的期数（天数或组数）
    threshhold_actual=len(ret[ret<-ratio])
    alpha_actual=1-threshhold_actual/len(ret)
    
    #结果判读
    if abs(alpha_actual-alpha) < 0.001:
        result="准确"
    elif alpha_actual < alpha:
        result="低估"
    else: 
        result="高估"
    
    #打印结果
    """
    print("\n======= VaR模型：回溯测试 =======")
    print("投资组合          :",tickerlist)
    print("成分股票配置      :",sharelist)
    print("持有日期          :",today)
    print("当前头寸          :",format(round(position,2),','))
    print("预计持有天数      :",future_days,"天")
    print("置信度水平        : ",alpha*100,"%",sep='')
    print("使用的历史样本数据:",pastyears,"年")
    print("使用的VaR模型     :",type)
    
    print("\n*** 在险价值 ***")
    print("VaR金额:",format(round(VaR,2),','))
    print("VaR比率: ",round(ratio*100,2),"%",sep='')
    
    print("\n*** 回溯测试 ***")
    print("期望的置信度水平       : ",alpha*100,"%",sep='')
    print("损失超过VaR的预期天数  :",threshhold_expected,'天')
    print("损失超过VaR的实际天数  :",threshhold_actual,'天')  
    print("实际的置信度水平       : ",round(alpha_actual*100,2),"%",sep='')
    print("模型验证的回溯测试结果 :",result)
    """
    
    titletxt="VaR模型：回溯测试"
    import datetime as dt; todaydt=dt.date.today()
    footnote="数据来源：新浪/stooq，"+str(todaydt)
    
    data_dict={'投资组合：':portfolio_name(portfolio), \
               '持有日期：':today, \
               "当前头寸：":format(round(position,2),','), \
               '预计持有天数：':str(future_days)+'天', \
               '置信度水平：':str(alpha*100)+'%', \
               "使用的历史样本数据：":str(pastyears)+"年", \
               "使用的VaR模型：":type, \
                   
               "*** 在险价值 ***":'', \
               "VaR金额：":format(round(VaR,2),','), \
               "VaR比率：":str(round(ratio*100,2))+"%", \
               
               "*** 回溯测试 ***":'', \
               "期望的置信度水平：":str(alpha*100)+"%", \
               "损失超过VaR的预期天数：":str(threshhold_expected)+'天', \
               "损失超过VaR的实际天数：":str(threshhold_actual)+'天', \
               "实际的置信度水平：":str(round(alpha_actual*100,2))+"%", \
               "模型验证的回溯测试结果：":result}
    
    print2CSS(data_dict,titletxt=titletxt,footnote=footnote)
    
    
    return
    
if __name__ == "__main__": 
    tickerlist=['AAPL']
    sharelist=[1]
    backtest_VaR(tickerlist,sharelist,'2019-8-8',1, \
                 pastyears=1,model="montecarlo")
    backtest_VaR(tickerlist,sharelist,'2019-8-8',1, \
                 pastyears=1,model="normal_standard")    
    backtest_VaR(tickerlist,sharelist,'2019-8-8',1, \
                 pastyears=1,model="normal_modified") 
    backtest_VaR(tickerlist,sharelist,'2019-8-8',1, \
                 pastyears=1,model="historical")     

#==============================================================================
