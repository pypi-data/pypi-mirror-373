# -*- coding: utf-8 -*-
"""
本模块功能：投资组合的风险调整收益率教学插件
所属工具包：证券投资分析工具SIAT 
SIAT：Security Investment Analysis Tool
创建日期：2023年7月15日
最新修订日期：2023年7月16日
作者：王德宏 (WANG Dehong, Peter)
作者单位：北京外国语大学国际商学院
作者邮件：wdehong2000@163.com
版权所有：王德宏
用途限制：仅限研究与教学使用！
特别声明：作者不对使用本工具进行证券投资导致的任何损益负责！
"""

#==============================================================================
#关闭所有警告
import warnings; warnings.filterwarnings('ignore')
#==============================================================================
from siat.common import *
from siat.translate import *
from siat.stock import *
from siat.security_prices import *
from siat.security_price2 import *
from siat.risk_adjusted_return import *
from siat.valuation import *
from siat.grafix import *

import pandas as pd
import datetime as dt; today=str(dt.date.today())
#==============================================================================
#==============================================================================
if __name__=='__main__':
    #测试组1
    ticker='JD'
    indicator='Exp Ret%'
    start='2022-1-1'
    end='2022-12-31'
    datatag=False
    power=1
    graph=True
    source='auto'
    
    df=security_trend(ticker,indicator=indicator,power=1)
    
    #测试组2
    ticker='AAPL'
    indicator=['Close','Open']
    start='default'
    end='default'
    datatag=False
    power=0
    graph=True
    twinx=True
    loc1='upper left'
    loc2='lower right'
    source='auto'
    
    #测试组3
    ticker='AAPL'
    indicator=['Close','Open','High','Low']
    start='default'
    end='default'
    datatag=False
    power=0
    graph=True
    twinx=True
    loc1='upper left'
    loc2='lower right'
    source='auto'
    
    df=security_trend(ticker,indicator=indicator)
    
    #测试组4
    ticker=["GCZ25.CMX","GCZ24.CMX"]
    indicator='Close'
    start="2020-1-1"
    end="2020-6-30"
    
    
    
def security_trend(ticker,indicator='Close', \
                   start='default',end='default', \
                   critical_value='', \
                   average_value=False, \
                   kline=False,kline_demo=False,mav=[5,10,20], \
                   stock_dividend=False,stock_split=False, \
                   market="China",market_index="000300.SS",RF=False,window=252, \
                   sortby='tpw_mean',trailing=10,trend_threshhold=0.001, \
                   graph=True,twinx=False,loc1='best',loc2='best', \
                   datatag=False,power=0, \
                   smooth=True,date_range=False,date_freq=False,annotate=False, \
                   preprocess='none',scaling_option='start', \
                   printout=False, \
                   source='auto'):

    """
    功能：描述证券指标走势
    指标种类：默认为收盘价，包括收益率指标、风险指标、RAR指标、估值指标。
    窗口：滚动窗口，扩展窗口。
    数量变换：多种，默认不变换，常用的为scaling。
    
    注意：base='Annual Ret%'需要与window=252一致，如果不一致，以base为准。
    """    
    
    # 检查证券代码
    if isinstance(ticker,str):
        ticker_num=1
        tickers=[ticker]
    elif isinstance(ticker,list):
        ticker_num=len(ticker)
        tickers=ticker
    else:
        print("  #Error(security_trend): unrecognizable security codes",ticker)
        return None
    
    # 检查日期：截至日期
    import datetime as dt; today=dt.date.today()
    end=end.lower()
    if end in ['default','today']:
        todate=today
    else:
        validdate,todate=check_date2(end)
        if not validdate:
            print("  #Warning(security_trend): invalid date for",end)
            todate=today

    # 检查日期：开始日期
    start=start.lower()
    if start in ['default','mrm','l1m']:  # 默认近一个月
        fromdate=date_adjust(todate,adjust=-31-16) #多几天有利于绘图坐标标示
    elif start in ['mrq','l3m']:  # 近三个月
        fromdate=date_adjust(todate,adjust=-31*4-16) #多一个月有利于绘图坐标标示
    elif start in ['l6m','mrh']:  # 近6个月
        fromdate=date_adjust(todate,adjust=-31*7-16)         
    elif start in ['mry','l12m']:  # 近一年
        fromdate=date_adjust(todate,adjust=-31*13-16)  
    elif start in ['l2y']:  # 近两年以来
        fromdate=date_adjust(todate,adjust=-31*25-16)  
    elif start in ['l3y']:  # 近三年以来
        fromdate=date_adjust(todate,adjust=-31*37-16)  
    elif start in ['l5y']:  # 近五年以来
        fromdate=date_adjust(todate,adjust=-31*61-16)  
    elif start in ['l8y']:  # 近八年以来
        fromdate=date_adjust(todate,adjust=-31*97-16)   
    elif start in ['l10y']:  # 近十年以来
        fromdate=date_adjust(todate,adjust=-31*121-16)        
    elif start in ['ytd']:  # 今年以来
        fromdate=str(today.year-1)+'-12-1'        
    else:
        validdate,fromdate=check_date2(start)
        if not validdate:
            print("  #Warning(security_trend): invalid date for",start,"/b, reset to MRM")
            fromdate=date_adjust(todate,adjust=-31-16)    

    # 检查窗口长度
    if isinstance(window,str):
        if window.lower() == "weekly":
            window=5
        elif window.lower() == "monthly":
            window=21
        elif window.lower() == "quarterly":
            window=63
        elif window.lower() == "annual":
            window=252
        else:
            print("  #Warning(security_trend): invalid window size, reset to annual")
            window=252

    # 处理K线图=================================================================
    if kline and not kline_demo:
        # 跟踪
        #print(tickers[0],fromdate,todate)
        if start in ['default']:
            fromdate=date_adjust(todate,adjust=-60)
        if not isinstance(mav,list):
            mav=[mav]
        df=candlestick(stkcd=tickers[0],fromdate=fromdate,todate=todate,mav=mav)
        return df

    if kline and kline_demo:
        if start in ['default']:
            fromdate=date_adjust(todate,adjust=-7)
        
        df=candlestick_demo(tickers[0],fromdate=fromdate,todate=todate)
        return df

    # 处理股票分红和股票分拆：需要访问雅虎财经=====================================
    if stock_dividend:
        if start in ['default']:
            fromdate=date_adjust(todate,adjust=-365*5)  
            
        df=stock_dividend(ticker=tickers[0],fromdate=fromdate,todate=todate)
        return df

    if stock_split:
        if start in ['default']:
            fromdate=date_adjust(todate,adjust=-365*5)  
        
        df=stock_split(ticker=tickers[0],fromdate=fromdate,todate=todate)
        return df
    

    # 检查指标：是否字符串或列表=================================================
    if isinstance(indicator,str):
        measures=[indicator]
        indicator_num=1
    elif isinstance(indicator,list):
        measures=indicator
        indicator_num=len(indicator)
    else:
        print("  #Error(security_trend): invalid indicator(s) for",indicator)
        return None
            
    # 检查指标
    indicator_list1=['Open','Close','Adj Close','High','Low',
             'Daily Ret','Daily Ret%','Daily Adj Ret','Daily Adj Ret%',
             'log(Daily Ret)','log(Daily Adj Ret)','Weekly Ret','Weekly Ret%',
             'Weekly Adj Ret','Weekly Adj Ret%','Monthly Ret','Monthly Ret%',
             'Monthly Adj Ret','Monthly Adj Ret%','Quarterly Ret','Quarterly Ret%',
             'Quarterly Adj Ret','Quarterly Adj Ret%','Annual Ret','Annual Ret%',
             'Annual Adj Ret','Annual Adj Ret%','Exp Ret','Exp Ret%','Exp Adj Ret',
             'Exp Adj Ret%','Weekly Price Volatility','Weekly Adj Price Volatility',
             'Monthly Price Volatility','Monthly Adj Price Volatility',
             'Quarterly Price Volatility','Quarterly Adj Price Volatility',
             'Annual Price Volatility','Annual Adj Price Volatility',
             'Exp Price Volatility','Exp Adj Price Volatility',
             'Weekly Ret Volatility','Weekly Ret Volatility%',
             'Weekly Adj Ret Volatility','Weekly Adj Ret Volatility%',
             'Monthly Ret Volatility', 'Monthly Ret Volatility%',
             'Monthly Adj Ret Volatility', 'Monthly Adj Ret Volatility%',
             'Quarterly Ret Volatility', 'Quarterly Ret Volatility%',
             'Quarterly Adj Ret Volatility', 'Quarterly Adj Ret Volatility%',
             'Annual Ret Volatility', 'Annual Ret Volatility%',
             'Annual Adj Ret Volatility', 'Annual Adj Ret Volatility%',
             'Exp Ret Volatility', 'Exp Ret Volatility%', 'Exp Adj Ret Volatility',
             'Exp Adj Ret Volatility%', 'Weekly Ret LPSD', 'Weekly Ret LPSD%',
             'Weekly Adj Ret LPSD', 'Weekly Adj Ret LPSD%', 'Monthly Ret LPSD',
             'Monthly Ret LPSD%', 'Monthly Adj Ret LPSD', 'Monthly Adj Ret LPSD%',
             'Quarterly Ret LPSD', 'Quarterly Ret LPSD%', 'Quarterly Adj Ret LPSD',
             'Quarterly Adj Ret LPSD%', 'Annual Ret LPSD', 'Annual Ret LPSD%',
             'Annual Adj Ret LPSD', 'Annual Adj Ret LPSD%', 'Exp Ret LPSD',
             'Exp Ret LPSD%', 'Exp Adj Ret LPSD', 'Exp Adj Ret LPSD%',
             ]

    indicator_list2=['treynor','sharpe','sortino','alpha','Treynor','Sharpe','Sortino','Alpha']
    indicator_list3=['pe','pb','mv','PE','PB','MV','Pe','Pb','Mv','ROE','roe','Roe']
    
    # 是否属于支持的指标
    for m in measures:
        if not (m in indicator_list1 + indicator_list2 + indicator_list3):
            print("  #Error(security_trend): unsupported indicator for",m)
            print("  Supported indicators:")
            printlist(indicator_list1,numperline=4,beforehand='  ',separator='   ')
            printlist(indicator_list2,numperline=5,beforehand='  ',separator='   ')
            printlist(indicator_list3,numperline=5,beforehand='  ',separator='   ')
            return None
        
    # 不能同时支持indicator_list1、indicator_list2和indicator_list3的指标，即不能跨组比较！
    indicator_group1=False
    indicator_group2=False
    indicator_group3=False
    
    list_group1=list_group2=list_group3=0
    for m in measures:
        if m in indicator_list3:
            list_group3=1
            indicator_group3=True    
            measures = [x.upper() for x in measures]
            
        if m in indicator_list2:
            list_group2=1
            indicator_group2=True
            measures = [x.lower() for x in measures]
            
        if m in indicator_list1:
            list_group1=1
            indicator_group1=True
            measures = [x.title() for x in measures]
            measures = [x.replace('Lpsd','LPSD') if 'Lpsd' in x else x for x in measures]
            
    if list_group1+list_group2+list_group3 >= 2:
        print("  #Error(security_trend): cannot support in different indicator groups together for",measures)
        return None
    
    # 情形1：单个证券，单个普通指标===============================================
    # 绘制横线
    zeroline=False
    if (critical_value != ''):
        if isinstance(critical_value,float) or isinstance(critical_value,int):
            zeroline=critical_value
    
    if ticker_num==1 and indicator_num==1 and indicator_group1:
        df=security_indicator(ticker=tickers[0],indicator=measures[0], \
                              fromdate=fromdate,todate=todate, \
                              zeroline=zeroline, \
                              average_value=average_value, \
                              datatag=datatag,power=power,graph=graph, \
                              source=source)
        return df
    
    # 情形2：单个证券，两个普通指标，twinx==True =================================
    if ticker_num==1 and indicator_num == 2 and indicator_group1 and twinx:
        df=compare_security(tickers=tickers[0],measures=measures[:2], \
                            fromdate=fromdate,todate=todate,twinx=twinx, \
                            loc1=loc1,loc2=loc2,graph=graph,source=source)
        return df
    
    # 情形3：单个证券，两个及以上普通指标=========================================
    if ticker_num==1 and indicator_num >= 2 and indicator_group1 and not twinx:
        df=security_mindicators(ticker=tickers[0],measures=measures, \
                         fromdate=fromdate,todate=todate, \
                         graph=graph,smooth=smooth,loc=loc1, \
                         date_range=date_range,date_freq=date_freq, \
                         annotate=annotate, \
                         source=source)
        return df
    
    # 情形4：两个证券，取第一个普通指标，twinx==True =============================
    if ticker_num==2 and indicator_group1 and twinx:
        df=compare_security(tickers=tickers,measures=measures[0], \
                            fromdate=fromdate,todate=todate,twinx=twinx, \
                            loc1=loc1,loc2=loc2,graph=graph,source=source)
        return df

    # 情形5：两个及以上证券，取第一个普通指标=====================================
    if ticker_num==2:
        linewidth=2.5
    elif ticker_num==3:
        linewidth=2.0
    else:
        linewidth=1.5
    
    # 绘制横线
    axhline_value=0
    axhline_label=''
    if (critical_value != ''):
        if isinstance(critical_value,float) or isinstance(critical_value,int):
            axhline_value=critical_value
            axhline_label='零线'
        
    if ((ticker_num == 2 and not twinx) or ticker_num > 2) and indicator_group1:
        df=compare_msecurity(tickers=tickers,measure=measures[0], \
                             start=fromdate,end=todate, \
                      axhline_value=axhline_value,axhline_label=axhline_label, \
                      preprocess=preprocess,linewidth=linewidth, \
                      scaling_option=scaling_option, \
                      graph=graph,loc=loc1, \
                      annotate=annotate,smooth=smooth, \
                      source=source)
        return df

    # 情形6：单个证券，单个或多个RAR指标=========================================
    # 特别注意：与收益率对比时若使用扩展收益率可能导致矛盾，要使用滚动收益率
    if indicator_group2 and ticker_num==1 and indicator_num >= 1:
        df=compare_1security_mrar(ticker=tickers[0],rar_names=measures, \
                                  start=fromdate,end=todate, \
                        market=market,market_index=market_index,RF=RF,window=window, \
                        axhline_value=0,axhline_label='零线',graph=graph,printout=printout, \
                        sortby=sortby,source=source,trailing=trailing,trend_threshhold=trend_threshhold, \
                        annotate=annotate)
        return df

    # 情形7：多个证券，取第一个RAR指标===========================================
    # 特别注意：与收益率对比时若使用扩展收益率可能导致矛盾，要使用滚动收益率
    if indicator_group2 and ticker_num > 1:
        df=compare_mrar(tickers=tickers,rar_name=measures[0], \
                        start=fromdate,end=todate, \
                        market=market,market_index=market_index,RF=RF,window=window, \
                        axhline_value=0,axhline_label='零线',graph=graph,printout=printout, \
                        sortby=sortby,source=source,trailing=trailing,trend_threshhold=trend_threshhold, \
                        annotate=annotate)
        return df
    
    # 情形8：估值指标PE/PB/MV/ROE===============================================
    if indicator_group3:
        df=security_valuation(tickers=tickers,indicators=measures,start=fromdate,end=todate, \
                              preprocess=preprocess,scaling_option=scaling_option, \
                              twinx=twinx,loc1=loc1,loc2=loc2, \
                              graph=graph,annotate=annotate)
        return df
    
    # 其他未预料情形
    print("  Sorry, unsupported combination of security(ies) and indicator(s):-(")
    return None

#==============================================================================

#==============================================================================
#==============================================================================
#==============================================================================











