# -*- coding: utf-8 -*-
"""
本模块功能：股票的风险调整收益
所属工具包：证券投资分析工具SIAT 
SIAT：Security Investment Analysis Tool
创建日期：2024年3月16日
最新修订日期：2024年3月19日
作者：王德宏 (WANG Dehong, Peter)
作者单位：北京外国语大学国际商学院
作者邮件：wdehong2000@163.com
版权所有：王德宏
用途限制：仅限研究与教学使用，不可商用！
特别声明：作者不对使用本工具进行证券投资导致的任何损益负责！
"""

#==============================================================================
#关闭所有警告
import warnings; warnings.filterwarnings('ignore')
#==============================================================================
from siat.common import *
from siat.translate import *
from siat.security_prices import *
from siat.security_price2 import *
from siat.capm_beta2 import *
#from siat.fama_french import *
from siat.risk_adjusted_return import *
from siat.grafix import *

import pandas as pd
import numpy as np
#==============================================================================
#==============================================================================
#==============================================================================
if __name__=='__main__':
    ticker='301161.SZ'
    ticker="AAPL"
    ticker={'Market':('US','^SPX','中概教培组合'),'EDU':0.7,'TAL':0.3}
    
    start="2024-1-1"; end="2024-9-30"
    rar_name="sharpe"
    ret_type="Annual Adj Ret%"
    RF=0.055
    source='auto'; ticker_type='auto'
    
    sharpe1m0=get_rolling_sharpe_sortino(ticker,start,end,rar_name="sharpe",ret_type="Monthly Ret%",RF=0)
    sharpe2w=get_rolling_sharpe_sortino(ticker,start,end,rar_name="sharpe",ret_type="Weekly Ret%",RF=0.01759)
    sharpe2m=get_rolling_sharpe_sortino(ticker,start,end,rar_name="sharpe",ret_type="Monthly Ret%",RF=0.01759)
    sharpe2q=get_rolling_sharpe_sortino(ticker,start,end,rar_name="sharpe",ret_type="Quarterly Ret%",RF=0.01759)
    sharpe2y=get_rolling_sharpe_sortino(ticker,start,end,rar_name="sharpe",ret_type="Annual Ret%",RF=0.01759)

    sortino1=get_rolling_sharpe_sortino(ticker,start,end,rar_name="sortino",ret_type="Monthly Ret%",RF=0)
    sortino2=get_rolling_sharpe_sortino(ticker,start,end,rar_name="sortino",ret_type="Monthly Ret%",RF=0.01759)

def get_rolling_sharpe_sortino(ticker,start,end,rar_name="sharpe", \
                               ret_type="Monthly Adj Ret%",RF=0,source='auto', \
                               ticker_type='auto'):
    """
    功能：获取一只股票的夏普比率或索替诺比率，基于给定的滚动收益率类型，在指定期间内
    支持股票和投资组合
    RF: 年化利率，不带百分数
    """
    
    #估计滚动窗口日期的提前量
    ret_type_lower=ret_type.lower()
    if 'weekly' in ret_type_lower:
        dateahead=7*2+7 #考虑收益率标准差和节假日
        ret_period='Weekly'
        period_days=5
    elif 'monthly' in ret_type_lower:
        dateahead=31*2+7 #考虑收益率标准差和节假日
        ret_period='Monthly'
        period_days=21
    elif 'quarterly' in ret_type_lower:
        dateahead=(31*3+7)*2 #考虑收益率标准差和节假日
        ret_period='Quarterly'
        period_days=63
    else:
        dateahead=(366+7*3)*2 #考虑收益率滚动+标准差滚动和节假日
        ret_period='Annual'
        period_days=252

    start1=date_adjust(start,adjust=-dateahead)
    
    #判断复权价
    if ('adj' in ret_type_lower):
        adjust='qfq'
    else:
        adjust=''
    
    #抓取股价
    #pricedf=get_price(ticker,start1,end,source=source)
    #pricedf=get_price_security(ticker,start1,end,source=source)
    pricedf,found=get_price_1ticker_mixed(ticker=ticker,fromdate=start1,todate=end, \
                                          adjust=adjust, \
                                          source=source,ticker_type=ticker_type)
    
    if found !='Found':
        print("  #Error(get_rolling_sharpe_sortino): no records found for",ticker)
        return None
    
    #计算收益率和收益率标准差
    rardf1=calc_daily_return(pricedf)
    rardf2=calc_rolling_return(rardf1,period=ret_period)
    
    if '%' in ret_type:
        RF=RF*100
    if ret_period=='Weekly':
        RF_period=RF/52
    elif ret_period=='Monthly':
        RF_period=RF/12
    elif ret_period=='Quarterly':
        RF_period=RF/4
    else:
        RF_period=RF
            
    #收益率减去一个常数其实不影响其标准差的数值，即std(ret-RF)=std(ret)
    try:
        rardf2[ret_type]=rardf2[ret_type] - RF_period
    except:
        print("  #Warning(get_rolling_sharpe_sortino): unsupported ret_type",ret_type)
        return None
        
    rardf3=rolling_ret_volatility(rardf2, period=ret_period)
    rardf4=rolling_ret_lpsd(rardf3, period=ret_period)   
    
    #开始日期富余一段时间，有助于绘图时显示出期望的开始日期
    startpd=pd.to_datetime(date_adjust(start,adjust=-7))
    endpd=pd.to_datetime(end)

    rardf4['index_tmp']=rardf4.index
    rardf4['index_tmp']=rardf4['index_tmp'].apply(lambda x: pd.to_datetime(x))
    rardf4.set_index(['index_tmp'],inplace=True)  
    #rardf4.drop(['index_tmp'],inplace=True)
    
    rardf5=rardf4[(rardf4.index >=startpd) & (rardf4.index <=endpd)]
    
    #确定风险字段名
    pct_flag=False
    if '%' in ret_type:
        pct_flag=True

    rar_name_lower=rar_name.lower()
    ret_type_nopct=ret_type.replace('%','')
    if 'sharpe' in rar_name_lower:
        risk_type=ret_type_nopct+' Volatility'
        if pct_flag:
            risk_type=risk_type+'%'
        rardf5[rar_name]=rardf5.apply(lambda x: x[ret_type]/x[risk_type],axis=1)
    elif 'sortino' in rar_name_lower:
        risk_type=ret_type_nopct+' LPSD'
        if pct_flag:
            risk_type=risk_type+'%'
        rardf5[rar_name]=rardf5.apply(lambda x: x[ret_type]/x[risk_type],axis=1)

    #选择返回字段        
    #rardf6=rardf5[['date','source','ticker','footnote',ret_type,risk_type,rar_name]]
    rardf6=rardf5[[rar_name]]

    return rardf6
#==============================================================================
#==============================================================================
if __name__=='__main__':
    ticker="600519.SS"
    ticker={'Market':('US','^SPX','中概教培组合'),'EDU':0.7,'TAL':0.3}
    
    start="2023-1-1"
    end="2024-3-15"
    rar_name="sharpe"
    ret_type="Exp Ret%"
    RF=0.01759
    source='auto'
    
    sharpe1=get_expanding_sharpe_sortino(ticker,start,end,rar_name="sharpe",RF=0)
    sharpe2=get_expanding_sharpe_sortino(ticker,start,end,rar_name="sharpe",RF=0.01759)
    sortino2=get_expanding_sharpe_sortino(ticker,start,end,rar_name="sortino",RF=0.01759)
    
def get_expanding_sharpe_sortino(ticker,start,end,rar_name="sharpe", \
                                 ret_type="Exp Adj Ret%",RF=0,source='auto',ticker_type='auto'):
    """
    功能：获取一只股票的夏普比率或索替诺比率，基于扩展收益率，在指定期间内
    支持股票和投资组合
    RF: 年化利率，不带百分数
    """
    
    #估计扩展窗口日期的提前量
    dateahead=7
    start1=date_adjust(start,adjust=-dateahead)
    
    #判断复权价
    ret_type=ret_type.title()
    if ('Adj' in ret_type):
        adjust='qfq'
    else:
        adjust=''
    
    #抓取股价
    #pricedf=get_price(ticker,start1,end,source=source)
    #pricedf=get_price_security(ticker,start1,end,source=source)
    pricedf,found=get_price_1ticker_mixed(ticker=ticker,fromdate=start1,todate=end, \
                                          adjust=adjust, \
                                          source=source,ticker_type=ticker_type)
    
    #计算收益率和收益率标准差
    rardf2=calc_expanding_return(pricedf,start)
    
    if '%' in ret_type:
        RF=RF*100
    RF_daily=RF/365
    
    #增加距离开始日期的天数
    date0=pd.to_datetime(rardf2.index[0])
    if 'date' not in list(rardf2):
        if 'Date' in list(rardf2):
            rardf2['date']=rardf2['Date']
        else:
            rardf2['date']=rardf2.index
        
    rardf2['days']=rardf2['date'].apply(lambda x: days_between_dates(date0,pd.to_datetime(x)))
            
    rardf2[ret_type]=rardf2.apply(lambda x: x[ret_type] - RF_daily*x['days'],axis=1)
    
    #确定风险字段名，计算风险
    rar_name_lower=rar_name.lower()
    pct_flag=False
    if '%' in ret_type:
        pct_flag=True
    ret_type_nopct=ret_type.replace('%','')
    
    if 'sharpe' in rar_name_lower:
        risk_type=ret_type_nopct+' Volatility'
        if pct_flag:
            risk_type=risk_type+'%'
        
        #rardf2[risk_type]=rardf2[ret_type].expanding(min_periods=1).apply(lambda x: np.std(x,ddof=1)*np.sqrt(len(x)-1))
        rardf2[risk_type]=rardf2[ret_type].expanding(min_periods=1).apply(lambda x: np.std(x,ddof=1))
        #rardf2[risk_type]=rardf2[ret_type].expanding(min_periods=5).apply(lambda x: np.std(x,ddof=1))
    elif 'sortino' in rar_name_lower:
        risk_type=ret_type_nopct+' LPSD'
        if pct_flag:
            risk_type=risk_type+'%'
        
        #rardf2[risk_type]=rardf2[ret_type].expanding(min_periods=1).apply(lambda x: lpsd(x)*np.sqrt(len(x)-1))
        rardf2[risk_type]=rardf2[ret_type].expanding(min_periods=1).apply(lambda x: lpsd(x))
        #rardf2[risk_type]=rardf2[ret_type].expanding(min_periods=5).apply(lambda x: lpsd(x))
    
    
    #计算RAR
    rardf2[rar_name]=rardf2.apply(lambda x: x[ret_type]/x[risk_type],axis=1)
    rardf3=rardf2.replace(np.nan,0)

    #选择返回字段        
    #rardf4=rardf3[['date','source','ticker','footnote',ret_type,risk_type,rar_name]]
    rardf4=rardf3[[rar_name]]

    return rardf4

#==============================================================================
if __name__=='__main__':
    ticker="AAPL"
    ticker={'Market':('US','^SPX','中概教培组合'),'EDU':0.7,'TAL':0.3}
    
    start="2024-1-1"
    end="2024-6-30"
    rar_name="treynor"
    ret_type="Annual Adj Ret%"
    RF=0.055
    regression_period=365
    mktidx='auto'; source='auto'; ticker_type='auto'
    
    alpha1m0=get_rolling_treynor_alpha(ticker,start,end,rar_name="alpha",ret_type="Monthly Ret%",RF=0)
    alpha2w=get_rolling_treynor_alpha(ticker,start,end,rar_name="alpha",ret_type="Weekly Ret%",RF=0.01759)
    alpha2m=get_rolling_treynor_alpha(ticker,start,end,rar_name="alpha",ret_type="Monthly Ret%",RF=0.01759)
    alpha2q=get_rolling_treynor_alpha(ticker,start,end,rar_name="alpha",ret_type="Quarterly Ret%",RF=0.01759)
    alpha2y=get_rolling_treynor_alpha(ticker,start,end,rar_name="alpha",ret_type="Annual Ret%",RF=0.01759)

def get_rolling_treynor_alpha(ticker,start,end,rar_name="alpha", \
                              ret_type="Monthly Adj Ret%",RF=0, \
                              regression_period=365,mktidx='auto',source='auto',ticker_type='auto'):
    """
    功能：获取一只股票的特雷诺比率或阿尔法指数，基于给定的滚动收益率类型，在指定期间内
    支持股票和投资组合
    RF: 年化利率，不带百分数
    计算CAPM的期间：默认一年，252个交易日
    ***废弃！！！指标计算有问题
    """
    
    #估计需要的日期提前量
    ret_type_lower=ret_type.lower()
    if 'weekly' in ret_type_lower:
        dateahead=7*2+7 #考虑收益率标准差和节假日
        ret_period='Weekly'
        period_days=7
    elif 'monthly' in ret_type_lower:
        dateahead=31*2+7 #考虑收益率标准差和节假日
        ret_period='Monthly'
        period_days=30
    elif 'quarterly' in ret_type_lower:
        dateahead=(31*3+7)*2 #考虑收益率标准差和节假日
        ret_period='Quarterly'
        period_days=90
    else:
        dateahead=(366+7*3)*2 #考虑收益率标准差和节假日
        ret_period='Annual'
        period_days=365
        
    #计算日历日regression_period对应的交易日数
    regtrddays=int(252 / 365 * regression_period)

    #计算滚动查看需要的日期提前量
    start1=date_adjust(start,adjust=-dateahead)
    #计算CAPM需要的日期提前量
    start2=date_adjust(start1,adjust=-regression_period-7*2)
    
    #判断复权价
    ret_type=ret_type.title()
    if ('Adj' in ret_type):
        adjust='qfq'
    else:
        adjust=''
    
    #CAPM回归，计算贝塔系数
    reg_result,dretdf3=regression_capm(ticker,start2,end, \
                                       adjust=adjust, \
                                       RF=RF, \
                                       regtrddays=regtrddays,mktidx=mktidx, \
                                       source=source,ticker_type=ticker_type)
    
    #计算股票和指数的滚动收益率
    varx=ret_type+'_x' #指数收益率
    vary=ret_type+'_y' #股票收益率

    pretdf=dretdf3.copy()
    pretdfcols=list(pretdf)
    lndretx='ln_'+pretdfcols[0]
    lndrety='ln_'+pretdfcols[1]

    #对数法计算滚动收益率
    RF_period=RF/365 * period_days
    
    if '%' in ret_type_lower:
        pretdf[lndretx]=pretdf[pretdfcols[0]].apply(lambda x: np.log(1+x/100))
        pretdf[lndrety]=pretdf[pretdfcols[1]].apply(lambda x: np.log(1+x/100))
            
        pretdf[varx]=pretdf[lndretx].rolling(window=period_days).apply(lambda x: (np.exp(sum(x))-1)*100)
        pretdf[vary]=pretdf[lndrety].rolling(window=period_days).apply(lambda x: (np.exp(sum(x))-1)*100)
        
    else:
        pretdf[lndretx]=pretdf[pretdfcols[0]].apply(lambda x: np.log(1+x))
        pretdf[lndrety]=pretdf[pretdfcols[1]].apply(lambda x: np.log(1+x))
            
        pretdf[varx]=pretdf[lndretx].rolling(window=period_days).apply(lambda x: (np.exp(sum(x))-1))
        pretdf[vary]=pretdf[lndrety].rolling(window=period_days).apply(lambda x: (np.exp(sum(x))-1))
        
    #合成滚动收益率与贝塔系数
    pretdf1=pd.merge(pretdf[[varx,vary]],reg_result,how='inner',left_index=True,right_index=True)
    
    #计算特雷诺比率和阿尔法指标
    if 'treynor' in rar_name.lower():
        pretdf1[rar_name]=pretdf1.apply(lambda x: (x[vary]-RF_period)/x['beta'],axis=1)
    elif 'alpha' in rar_name.lower():    
        vary_pred=vary+'_pred'
        pretdf1[vary_pred]=pretdf1.apply(lambda x: RF_period+x['beta']*(x[varx]-RF_period),axis=1)
        pretdf1[rar_name]=pretdf1.apply(lambda x: x[vary]-x[vary_pred],axis=1)
    
    #开始日期富余一段时间，有助于绘图时显示出期望的开始日期
    startpd=pd.to_datetime(date_adjust(start,adjust=-7))
    endpd=pd.to_datetime(end)
    pretdf2=pretdf1[(pretdf1.index >=startpd) & (pretdf1.index <=endpd)]
    
    pretdf3=pretdf2[[rar_name,'beta']]

    return pretdf3


def get_rolling_treynor_alpha2(ticker,start,end,rar_name="alpha", \
                              ret_type="Monthly Adj Ret%",RF=0, \
                              regression_period=365,mktidx='auto',source='auto',ticker_type='auto'):
    """
    功能：获取一只股票的特雷诺比率或阿尔法指数，基于给定的滚动收益率类型，在指定期间内
    支持股票和投资组合
    RF: 年化利率，不带百分数
    计算CAPM的期间：默认一年，252个交易日
    """
    
    #估计滚动窗口日期的提前量
    ret_type_lower=ret_type.lower()
    if 'weekly' in ret_type_lower:
        dateahead=7*2+7 #考虑收益率标准差和节假日
        ret_period='Weekly'
        period_days=5
    elif 'monthly' in ret_type_lower:
        dateahead=31*2+7 #考虑收益率标准差和节假日
        ret_period='Monthly'
        period_days=21
    elif 'quarterly' in ret_type_lower:
        dateahead=(31*3+7)*2 #考虑收益率标准差和节假日
        ret_period='Quarterly'
        period_days=63
    else:
        dateahead=(366+7*3)*2 #考虑收益率标准差和节假日
        ret_period='Annual'
        period_days=252

    #计算滚动查看需要的日期提前量
    start1=date_adjust(start,adjust=-dateahead)
    #计算CAPM需要的日期提前量
    start2=date_adjust(start1,adjust=-regression_period-7*2)
    
    #判断复权价
    ret_type=ret_type.title()
    if ('Adj' in ret_type):
        adjust='qfq'
    else:
        adjust=''

    #获取股票收益率
    if '%' in ret_type:
        if 'Adj' in ret_type:
            dret_type="Daily Adj Ret%"
        else:
            dret_type="Daily Ret%"
    else:
        if 'Adj' in ret_type:
            dret_type="Daily Adj Ret"
        else:
            dret_type="Daily Ret"
    
    #抓取股价
    pricedfs,found=get_price_1ticker_mixed(ticker=ticker,fromdate=start2,todate=end, \
                                          adjust=adjust, \
                                          source=source,ticker_type=ticker_type)  
    if found !='Found':
        print("  #Error(get_rolling_treynor_alpha2): no records found for",ticker)
        return None

    #计算股票收益率
    rardf1s=calc_daily_return(pricedfs)
    rardf2s=calc_rolling_return(rardf1s,period=ret_period)   
    
    #抓取指数
    if isinstance(ticker,dict):
        _,mktidx,pftickerlist,_,ticker_type=decompose_portfolio(ticker)
        if 'auto' in mktidx.lower():
            mktidx=get_market_index_code(pftickerlist[0])
    else:
        if 'auto' in mktidx.lower():
            mktidx=get_market_index_code(ticker)
            
    marketdf,found=get_price_1ticker_mixed(ticker=mktidx,fromdate=start2,todate=end, \
                                           adjust=adjust, \
                                           source=source,ticker_type=ticker_type)
    if found !='Found':
        print("  #Error(get_rolling_treynor_alpha2): no records found for",mktidx)
        return None

    #计算指数收益率
    rardf1m=calc_daily_return(marketdf)
    rardf2m=calc_rolling_return(rardf1m,period=ret_period)   
    
    
    #计算日历日regression_period对应的交易日数
    regtrddays=int(252 / 365 * regression_period)
    
    #CAPM回归，计算贝塔系数
    reg_result,dretdf3=regression_capm_df(rardf1m,rardf1s,mktidx=mktidx,adjust=adjust,RF=RF,regtrddays=regtrddays)
        
    #合成滚动收益率与贝塔系数：_x为指数收益率，_y为股票收益率
    pretdfms=pd.merge(rardf2m[[ret_type]],rardf2s[[ret_type]],how='inner',left_index=True,right_index=True)
    pretdf1=pd.merge(pretdfms,reg_result,how='inner',left_index=True,right_index=True)
    
    if '%' in ret_type:
        RF=RF*100
    if ret_period=='Weekly':
        RF_period=RF/52
    elif ret_period=='Monthly':
        RF_period=RF/12
    elif ret_period=='Quarterly':
        RF_period=RF/4
    else:
        RF_period=RF
        
    #计算特雷诺比率和阿尔法指标
    if 'treynor' in rar_name.lower():
        pretdf1[rar_name]=pretdf1.apply(lambda x: (x[ret_type+'_y']-RF_period)/x['beta'],axis=1)
            
    elif 'alpha' in rar_name.lower():    
        vary_pred=ret_type+'_pred'
        pretdf1[vary_pred]=pretdf1.apply(lambda x: RF_period+x['beta']*(x[ret_type+'_x']-RF_period),axis=1)
        pretdf1[rar_name]=pretdf1.apply(lambda x: x[ret_type+'_y']-x[vary_pred],axis=1)

    if '%' in ret_type:
        pretdf1[rar_name]=pretdf1[rar_name]/100
    
    #开始日期富余一段时间，有助于绘图时显示出期望的开始日期
    startpd=pd.to_datetime(date_adjust(start,adjust=-7))
    endpd=pd.to_datetime(end)
    pretdf2=pretdf1[(pretdf1.index >=startpd) & (pretdf1.index <=endpd)]
    
    pretdf3=pretdf2[[rar_name,'beta']]

    return pretdf3

#==============================================================================
if __name__=='__main__':
    ticker="AAPL"
    ticker={'Market':('US','^SPX','中概教培组合'),'EDU':0.7,'TAL':0.3}
    
    start="2024-1-1"
    end="2024-6-30"
    rar_name="alpha"
    ret_type="Exp Adj Ret%"
    RF=0.055
    regression_period=365
    mktidx='auto'; source='auto'
    
    alpha1=get_expanding_treynor_alpha(ticker,start,end,rar_name="alpha",ret_type="Exp Ret%",RF=0)
    alpha2=get_expanding_treynor_alpha(ticker,start,end,rar_name="alpha",ret_type="Exp Ret%",RF=0.01759)


def get_expanding_treynor_alpha(ticker,start,end,rar_name="alpha", \
                              ret_type="Exp Adj Ret%",RF=0, \
                              regression_period=365,mktidx='auto',source='auto',ticker_type='auto'):
    """
    功能：获取一只股票的特雷诺比率或阿尔法指数，基于扩展收益率类型，在指定期间内
    支持股票和投资组合
    RF: 年化利率，不带百分数
    计算CAPM的期间：默认一年，252个交易日=365个日历日
    ***废弃！！！收益率计算有问题
    """
    ret_type_lower=ret_type.lower()        
    #计算日历日regression_period对应的交易日数
    regtrddays=int(252 / 365 * regression_period)

    #计算滚动查看需要的日期提前量：无滚动
    start1=date_adjust(start,adjust=0)
    #计算CAPM需要的日期提前量
    start2=date_adjust(start1,adjust=-regression_period-7*2)
    
    #判断复权价
    ret_type=ret_type.title()
    if ('Adj' in ret_type):
        adjust='qfq'
    else:
        adjust=''
    
    #CAPM回归，计算贝塔系数
    reg_result,dretdf3=regression_capm(ticker,start2,end, \
                                       adjust=adjust, \
                                       RF=RF, \
                                       regtrddays=regtrddays,mktidx=mktidx, \
                                       source=source,ticker_type=ticker_type)
    
    #计算股票和指数的扩展收益率
    varx=ret_type+'_x'
    vary=ret_type+'_y'

    startpd=pd.to_datetime(start)
    endpd=pd.to_datetime(end)
    pretdf=dretdf3[(dretdf3.index >= startpd) & (dretdf3.index <= endpd)].copy()
    date0=pd.to_datetime(pretdf.index[0])
    
    pretdfcols=list(pretdf)
    #日期首日累计收益率应该为零，先用nan代替，最后再替换为零
    dretx=pretdfcols[0]
    drety=pretdfcols[1]
    lagdretx='lag_'+dretx
    lagdrety='lag_'+drety
    pretdf[lagdretx]=pretdf[dretx].shift(1)
    pretdf[lagdrety]=pretdf[drety].shift(1)
    
    pretdf=pretdf.replace(np.nan,0)
    
    lndretx='ln_'+dretx
    lndrety='ln_'+drety

    #对数法计算扩展收益率
    RF_daily=RF/365
    if '%' in ret_type_lower:
        RF_daily=RF/365 * 100
        pretdf[lndretx]=pretdf[lagdretx].apply(lambda x: np.log(1+x/100))
        pretdf[lndrety]=pretdf[lagdrety].apply(lambda x: np.log(1+x/100))
        pretdf[varx]=pretdf[lndretx].expanding(min_periods=1).apply(lambda x: (np.exp(sum(x))-1)*100)
        pretdf[vary]=pretdf[lndrety].expanding(min_periods=1).apply(lambda x: (np.exp(sum(x))-1)*100)
        """
        pretdf[varx]=pretdf[lndretx].expanding(min_periods=5).apply(lambda x: (np.exp(sum(x))-1)*100)
        pretdf[vary]=pretdf[lndrety].expanding(min_periods=5).apply(lambda x: (np.exp(sum(x))-1)*100)
        """
    else:
        pretdf[lndretx]=pretdf[pretdfcols[0]].apply(lambda x: np.log(1+x))
        pretdf[lndrety]=pretdf[pretdfcols[1]].apply(lambda x: np.log(1+x))
        pretdf[varx]=pretdf[lndretx].expanding(min_periods=1).apply(lambda x: (np.exp(sum(x))-1))
        pretdf[vary]=pretdf[lndrety].expanding(min_periods=1).apply(lambda x: (np.exp(sum(x))-1))
        """
        pretdf[varx]=pretdf[lndretx].expanding(min_periods=5).apply(lambda x: (np.exp(sum(x))-1))
        pretdf[vary]=pretdf[lndrety].expanding(min_periods=5).apply(lambda x: (np.exp(sum(x))-1))
        """
    pretdf['Date']=pretdf.index
    pretdf['days']=pretdf['Date'].apply(lambda x: days_between_dates(date0,pd.to_datetime(x)))
    
    #合成扩展收益率与贝塔系数
    pretdf1=pd.merge(pretdf[[varx,vary,'days']],reg_result,how='inner',left_index=True,right_index=True)
    
    #计算特雷诺比率和阿尔法指标
    if 'treynor' in rar_name.lower():
        pretdf1[rar_name]=pretdf1.apply(lambda x: (x[vary]-RF_daily*x['days'])/x['beta'],axis=1)
    elif 'alpha' in rar_name.lower():    
        vary_pred=vary+'_pred'
        pretdf1[vary_pred]=pretdf1.apply(lambda x: RF_daily*x['days']+x['beta']*(x[varx]-RF_daily*x['days']),axis=1)
        pretdf1[rar_name]=pretdf1.apply(lambda x: x[vary]-x[vary_pred],axis=1)
    
    
    pretdf3=pretdf1[[rar_name,'beta']]

    return pretdf3


def get_expanding_treynor_alpha2(ticker,start,end,rar_name="alpha", \
                              ret_type="Exp Adj Ret%",RF=0, \
                              regression_period=365,mktidx='auto',source='auto',ticker_type='auto'):
    """
    功能：获取一只股票的特雷诺比率或阿尔法指数，基于扩展收益率类型，在指定期间内
    支持股票和投资组合
    RF: 年化利率，不带百分数
    计算CAPM的期间：默认一年，252个交易日=365个日历日
    """
    ret_type_lower=ret_type.lower()        

    #计算滚动查看需要的日期提前量：无滚动
    start1=date_adjust(start,adjust=0)
    #计算CAPM需要的日期提前量
    start2=date_adjust(start1,adjust=-regression_period-7*2)
    
    #判断复权价
    ret_type=ret_type.title()
    if ('Adj' in ret_type):
        adjust='qfq'
    else:
        adjust=''

    #抓取股价
    pricedfs,found=get_price_1ticker_mixed(ticker=ticker,fromdate=start2,todate=end, \
                                          adjust=adjust, \
                                          source=source,ticker_type=ticker_type)  
    if found !='Found':
        print("  #Error(get_expanding_treynor_alpha2): no records found for",ticker)
        return None
    
    #计算股票扩展收益率
    rardf1s=calc_daily_return(pricedfs)
    rardf2s=calc_expanding_return(pricedfs,start)
    
    if '%' in ret_type:
        RF=RF*100
    RF_daily=RF/365
    
    #增加距离开始日期的天数
    date0=pd.to_datetime(rardf2s.index[0])
    if 'date' not in list(rardf2s):
        if 'Date' in list(rardf2s):
            rardf2s['date']=rardf2s['Date']
        else:
            rardf2s['date']=rardf2s.index
        
    rardf2s['days']=rardf2s['date'].apply(lambda x: days_between_dates(date0,pd.to_datetime(x)))
    rardf2s[ret_type+'_RP']=rardf2s.apply(lambda x: x[ret_type] - RF_daily*x['days'],axis=1)

    #抓取指数
    if isinstance(ticker,dict):
        _,mktidx,pftickerlist,_,ticker_type=decompose_portfolio(ticker)
        if 'auto' in mktidx.lower():
            mktidx=get_market_index_code(pftickerlist[0])
    else:
        if 'auto' in mktidx.lower():
            mktidx=get_market_index_code(ticker)
            
    marketdf,found=get_price_1ticker_mixed(ticker=mktidx,fromdate=start2,todate=end, \
                                           adjust=adjust, \
                                           source=source,ticker_type=ticker_type)
    if found !='Found':
        print("  #Error(get_expanding_treynor_alpha2): no records found for",mktidx)
        return None
    
    #计算指数扩展收益率
    rardf1m=calc_daily_return(marketdf)
    rardf2m=calc_expanding_return(marketdf,start)
    #增加距离开始日期的天数
    date0=pd.to_datetime(rardf2m.index[0])
    if 'date' not in list(rardf2m):
        if 'Date' in list(rardf2m):
            rardf2m['date']=rardf2m['Date']
        else:
            rardf2m['date']=rardf2m.index
        
    rardf2m['days']=rardf2m['date'].apply(lambda x: days_between_dates(date0,pd.to_datetime(x)))
    rardf2m[ret_type+'_RP']=rardf2m.apply(lambda x: x[ret_type] - RF_daily*x['days'],axis=1)

    #计算日历日regression_period对应的交易日数
    regtrddays=int(252 / 365 * regression_period)
    #CAPM回归，计算贝塔系数
    reg_result,dretdf3=regression_capm_df(rardf1m,rardf1s,mktidx=mktidx,adjust=adjust,RF=RF,regtrddays=regtrddays)

    #合成扩展收益率与贝塔系数：_x为指数收益率，_y为股票收益率，_RP为股票风险溢价
    pretdfms=pd.merge(rardf2m[[ret_type,ret_type+'_RP','days']],rardf2s[[ret_type,ret_type+'_RP']],how='inner',left_index=True,right_index=True)
    pretdf1=pd.merge(pretdfms,reg_result,how='inner',left_index=True,right_index=True)
    
    #计算特雷诺比率和阿尔法指标
    if 'treynor' in rar_name.lower():
        pretdf1[rar_name]=pretdf1.apply(lambda x: x[ret_type+'_RP_y']/x['beta'],axis=1)
    elif 'alpha' in rar_name.lower():    
        vary_pred=ret_type+'_y_pred'
        pretdf1[vary_pred]=pretdf1.apply(lambda x: RF_daily*x['days']+x['beta']*x[ret_type+'_RP_x'],axis=1)
        pretdf1[rar_name]=pretdf1.apply(lambda x: x[ret_type+'_y']-x[vary_pred],axis=1)

    if '%' in ret_type:
        pretdf1[rar_name]=pretdf1[rar_name]/100    
    
    pretdf3=pretdf1[[rar_name,'beta']]

    return pretdf3
#==============================================================================
if __name__=='__main__':
    ticker='301161.SZ'
    ticker="600519.SS"
    ticker={'Market':('US','^SPX','中概教培组合'),'EDU':0.7,'TAL':0.3}
    
    rar_name="sharpe"
    rar_name="alpha"
    
    ret_type="Annual Adj Ret%"
    ret_type="Monthly Adj Ret%"
    ret_type="Exp Ret%"
    
    start="2024-1-1"; end="2024-9-30"
    RF=0.01759
    regression_period=365
    mktidx='auto'; source='auto'; ticker_type='auto'
    
    alpha1=get_rar(ticker,start,end,rar_name="alpha",ret_type="Exp Ret%",RF=0)
    alpha2=get_rar(ticker,start,end,rar_name="alpha",ret_type="Exp Ret%",RF=0.01759)


def get_rar(ticker,start,end,rar_name="sharpe",ret_type="Monthly Adj Ret%", \
            RF=0,regression_period=365,mktidx='auto',source='auto',ticker_type='auto'):
    """
    功能：获取一只股票的收益-风险性价比指标，在指定期间内，支持股票和投资组合
    支持滚动收益率和扩展收益率
    滚动收益率支持周、月、季度和年度，默认为年度
    支持特雷诺比率、夏普比率、所提诺比率和阿尔法指标
    
    RF: 年化利率，不带百分数
    计算CAPM的期间：默认一年，252个交易日=365个日历日
    """
    
    ret_type_lower=ret_type.lower()
    ret_type_title=ret_type.title() #字符串每个单词首字母大写
    rar_name_lower=rar_name.lower()
    
    rardf=None
    #判断是否扩展收益率
    if 'exp' not in ret_type_lower:
        if ('sharpe' in rar_name_lower) or ('sortino' in rar_name_lower):
            rardf=get_rolling_sharpe_sortino(ticker=ticker,start=start,end=end, \
                                             rar_name=rar_name_lower, \
                                             ret_type=ret_type_title,RF=RF, \
                                             source=source,ticker_type=ticker_type)
        elif ('alpha' in rar_name_lower) or ('treynor' in rar_name_lower):
            rardf=get_rolling_treynor_alpha2(ticker=ticker,start=start,end=end, \
                                            rar_name=rar_name_lower, \
                                            ret_type=ret_type_title,RF=RF, \
                                            regression_period=regression_period, \
                                            mktidx=mktidx,source=source,ticker_type=ticker_type)
                
    else:
        if ('sharpe' in rar_name_lower) or ('sortino' in rar_name_lower):
            rardf=get_expanding_sharpe_sortino(ticker=ticker,start=start,end=end, \
                                               rar_name=rar_name_lower, \
                                               ret_type=ret_type_title,RF=RF, \
                                               source=source,ticker_type=ticker_type)
        elif ('alpha' in rar_name_lower) or ('treynor' in rar_name_lower):
            rardf=get_expanding_treynor_alpha2(ticker=ticker,start=start,end=end, \
                                              rar_name=rar_name_lower, \
                                              ret_type=ret_type_title,RF=RF, \
                                              regression_period=regression_period, \
                                              mktidx=mktidx,source=source,ticker_type=ticker_type)
        
    return rardf

#==============================================================================
if __name__=='__main__':
    ticker="301161.SZ"
    ticker="600519.SS"
    ticker={'Market':('US','^SPX','中概教培组合'),'EDU':0.7,'TAL':0.3}
    
    start="2024-1-1"; end="2024-9-30"
    rar='sharpe'
    rar=['sharpe','sortino','treynor','alpha']
    
    ret_type="Annual Adj Ret%"
    ret_type="Monthly Adj Ret%"
    RF=0.01759
    regression_period=365
    
    graph=True; axhline_value=0; axhline_label=''
    printout=False; sortby='tpw_mean'; trailing=20; trend_threshhold=0.001
    annotate=False
    mktidx='auto'; source='auto'; ticker_type='auto'
    
    rars=compare_1ticker_mrar(ticker=ticker,start=start,end=end,rar=rar,printout=True)

def compare_1ticker_mrar(ticker,start,end,rar=['sharpe','sortino','treynor','alpha'], \
                         ret_type="Annual Adj Ret%",RF=0,regression_period=365, \
                             attention_value='',attention_value_area='', \
                             attention_point='',attention_point_area='', \
                                 band_area='', \
                         graph=True,loc1='best', \
                         axhline_value=0,axhline_label='',power=0,facecolor='whitesmoke', \
                         printout=False,sortby='tpw_mean',trailing=7,trend_threshhold=0.01, \
                         annotate=False,annotate_value=False, \
                         mark_top=False,mark_bottom=False, \
                         mark_start=False,mark_end=False, \
                         mktidx='auto',source='auto',ticker_type='auto'):
    """
    功能：一只股票，对比其多个rar，支持股票和投资组合
    """
    
    import os,sys
    class HiddenPrints:
        def __enter__(self):
            self._original_stdout = sys.stdout
            sys.stdout = open(os.devnull, 'w')

        def __exit__(self, exc_type, exc_val, exc_tb):
            sys.stdout.close()
            sys.stdout = self._original_stdout
    
    if isinstance(ticker,list):
        ticker=ticker[0] #将列表转换为字符串
    if isinstance(rar,str):
        rar=[rar] #将字符串转换为列表，避免下面的循环出错
    if isinstance(ret_type,list):
        ret_type=ret_type[0]
    if isinstance(RF,list):
        RF=RF[0]
    if isinstance(regression_period,list):
        regression_period=regression_period[0]
    
    tname=ticker_name(ticker,ticker_type)
    print("  Working on different rars for",tname,"\b, please wait ......\n")

    #预处理ticker_type
    ticker_type=ticker_type_preprocess_mticker_mixed(ticker,ticker_type)
        
    df=pd.DataFrame() 
    for t in rar:
        #关闭print输出
        with HiddenPrints():
            df_tmp=get_rar(ticker,start,end,t,ret_type=ret_type, \
                        RF=RF,regression_period=regression_period, \
                        mktidx=mktidx,source=source,ticker_type=ticker_type)
        
        if df_tmp is None:
            break
        else:
            dft=df_tmp[[t]]
            
        if len(df)==0:
            df=dft #第一个
        else:
            df=pd.merge(df,dft,how='outer',left_index=True,right_index=True)

    if len(df)==0:
        print("  #Error(compare_1ticker_mrar): rar data inaccessible for",tname,"between",start,end)        
        return None
    
    #以下仅用于绘图或制表
    df1=df.copy()
    for c in list(df1):
        if df1[c].max() > axhline_value and df1[c].min() < axhline_value:
            axhline_label='零线'   
        
        cname=ectranslate(c)
        df1.rename(columns={c:cname},inplace=True)
        
        # 将band_area中的ticker替换为tname
        if band_area != '':
            for index, item in enumerate(band_area):
                if item == c:
                    band_area[index] = cname           
    
    footnote1=text_lang("评估值基于","Note: RaR based on ")+ectranslate(ret_type)
    if RF !=0:
        footnote2=text_lang("，年化无风险利率为",", RF = ")+str(round(RF*100,4))+text_lang('%','% pa')
    else:
        footnote2=text_lang("，不考虑年化无风险利率时。",", RF = 0 pa")

    footnote3=''
    if 'treynor' in rar or 'alpha' in rar:
        if mktidx != 'auto':
            mktidx_text=ticker_name(mktidx)
            footnote3x=text_lang("，市场指数基于",", using ")+mktidx_text
            footnote3=text_lang("\nCAPM回归期间","\nCAPM rolling ")+str(regression_period)+text_lang("个自然日"," days, ")+footnote3x
        else:
            footnote3=text_lang("，CAPM回归期间",", CAPM rolling ")+str(regression_period)+text_lang("个自然日"," days")
                
    
    import datetime; todaydt = datetime.date.today()
    footnote4=text_lang("数据来源: 综合新浪/EM/Stooq/Yahoo/SWHY，","Data source: Sina/Stooq/Yahoo, ")+str(todaydt)
    if footnote3 !='':
        footnotex=footnote1+footnote2+footnote3+'\n'+footnote4
    else:
        footnotex=footnote1+footnote2+footnote3+'\n'+footnote4
    
    #绘图
    if graph:
        y_label=''
        import datetime; todaydt = datetime.date.today()
        x_label=text_lang("数据来源: 综合新浪/EM/Stooq/Yahoo/SWHY，","Data source: Sina/Stooq/Yahoo, ")+str(todaydt)
        title_txt=text_lang("风险调整收益：","Risk-adjusted Return: ")+tname

        # 英文环境下将label首字母大写
        for c in list(df1):
            df1.rename(columns={c:c.title()},inplace=True)
            
        draw_lines(df1,y_label,x_label=footnotex, \
                   axhline_value=axhline_value,axhline_label=axhline_label, \
                   title_txt=title_txt,data_label=False, \
                        attention_value=attention_value,attention_value_area=attention_value_area, \
                        attention_point=attention_point,attention_point_area=attention_point_area, \
                   annotate=annotate,annotate_value=annotate, \
                       band_area=band_area, \
                   mark_top=mark_top,mark_bottom=mark_bottom, \
                   mark_start=mark_start,mark_end=mark_end, \
                   facecolor=facecolor,loc=loc1,power=power)
            
    #制表
    recommenddf=pd.DataFrame()
    if printout:
        if sortby=='tpw_mean':
            sortby_txt=text_lang('按推荐标记+近期优先加权平均值降序排列',"by Recommend + RWA, Descending")
        elif sortby=='min':
            sortby_txt=text_lang('按推荐标记+最小值降序排列',"by Recommend + Min, Descending")
        elif sortby=='mean':
            sortby_txt=text_lang('按推荐标记+平均值降序排列',"by Recommend + Mean, Descending")
        elif sortby=='median':
            sortby_txt=text_lang('按推荐标记+中位数值降序排列',"by Recommend + Median, Descending")
        elif sortby=='trailing':
            sortby_txt=text_lang('按推荐标记+短期均值走势降序排列',"by Recommend + Recent Trend, Descending")
        
        #title_txt='***** 风险调整收益评估：'+tname+'，'+sortby_txt+' *****'
        if isinstance(rar,list) and len(rar)==1:
            rar=rar[0]
        title_txt=text_lang('风险调整收益评估：',"RaR Evaluation: ")+str(ectranslate(rar))+text_lang('，',', ')+sortby_txt
        
        footnote6=text_lang('期间：',"Period: ")+str(start)+text_lang('至'," to ")+str(end)+text_lang("；近期指近","\nRecent trend: ")+str(trailing)+text_lang("个交易日。趋势变化率阈值：", " days. Trend threshhold ")+str(trend_threshhold)
        footnote7=text_lang("近期优先趋势和星号为风险调整收益指标加趋势等多项因素综合研判，最多五颗星","Recommend max 5 stars. RWA = Recent-priority Weighted Average")        
        footnotey=footnote6+'\n'+footnote7+'\n'+footnotex

        recommenddf=descriptive_statistics2(df1,title_txt,footnotey,decimals=4, \
                               sortby=sortby,recommend_only=True,trailing=trailing, \
                               trend_threshhold=trend_threshhold,facecolor=facecolor)            
 
    return df,recommenddf

#==============================================================================
if __name__=='__main__':
    ticker=["600519.SS","000858.SZ"]
    ticker={'Market':('US','^SPX','中概教培组合'),'EDU':0.7,'TAL':0.3}
    
    ticker=['601628.SS','601319.SS','601318.SS','00966.HK']
    
    start="2023-6-27"
    end="2024-6-27"
    rar='sharpe'
    RF=0.01692
    printout=True
    
    ret_type="Annual Ret%"; regression_period=365
    graph=True; loc1='best'
    axhline_value=0; axhline_label=''
    sortby='tpw_mean'; trailing=7; trend_threshhold=0.01
    annotate=False; annotate_value=False
    mark_top=False; mark_bottom=False; mark_end=False
    mktidx='auto'; source='auto'
    style_print=True; ticker_type='auto';facecolor='whitesmoke'
    
    rars=compare_mticker_1rar(ticker=["600519.SS","000858.SZ"],start="2024-1-1",end="2024-6-16",rar='sharpe',printout=True)

def compare_mticker_1rar(ticker,start,end,rar='sharpe', \
                         ret_type="Annual Adj Ret%",RF=0,regression_period=365, \
                             attention_value='',attention_value_area='', \
                             attention_point='',attention_point_area='', \
                                 band_area='', \
                         graph=True,loc1='best', \
                         axhline_value=0,axhline_label='', \
                         printout=False,sortby='tpw_mean',trailing=7,trend_threshhold=0.01, \
                         annotate=False,annotate_value=False, \
                         mark_top=False,mark_bottom=False, \
                         mark_start=False,mark_end=False, \
                         mktidx='auto',source='auto', \
                         style_print=True,ticker_type='auto',facecolor='whitesmoke'):
    """
    功能：多只股票，对比其同一个rar，支持股票和投资组合
    """
    
    import os,sys
    class HiddenPrints:
        def __enter__(self):
            self._original_stdout = sys.stdout
            sys.stdout = open(os.devnull, 'w')

        def __exit__(self, exc_type, exc_val, exc_tb):
            sys.stdout.close()
            sys.stdout = self._original_stdout
    
    #转换字符串和列表，避免下面的循环出错
    if not isinstance(ticker,list):
        ticker=[ticker]
    if isinstance(rar,list):
        rar=rar[0]
    if isinstance(ret_type,list):
        ret_type=ret_type[0]
    if isinstance(RF,list):
        RF=RF[0]
    if isinstance(regression_period,list):
        regression_period=regression_period[0]
    print("  Working on",rar,"ratio, please wait ......\n")
    
    #预处理ticker_type
    ticker_type_list=ticker_type_preprocess_mticker_mixed(ticker,ticker_type)
    
    df=pd.DataFrame() 
    for t in ticker:
        pos=ticker.index(t)
        tt=ticker_type_list[pos]
        #关闭print输出
        with HiddenPrints():
            df_tmp=get_rar(t,start,end,rar_name=rar,ret_type=ret_type, \
                        RF=RF,regression_period=regression_period, \
                        mktidx=mktidx,source=source,ticker_type=tt)
        
        if df_tmp is None:
            #break
            print("  #Warning(compare_mticker_1rar): data not available for",ticker_name(t,tt),"between",start,"and",end)
            continue
        else:
            dft=df_tmp[[rar]]
            tname=ticker_name(t,tt)
            dft.rename(columns={rar:tname},inplace=True)
        
            # 将band_area中的ticker替换为tname
            if band_area != '':
                for index, item in enumerate(band_area):
                    if item == t:
                        band_area[index] = tname        
            
        if len(df)==0: #第一个
            df=dft 
        else:
            df=pd.merge(df,dft,how='outer',left_index=True,right_index=True)

    if len(df)==0:
        print("  #Error(compare_mticker_1rar): data not available for",ticker,"between",start,"and",end)        
        return None
    
    #仅用于绘图和制表
    df1=df.copy()
    #进行空缺值填充，以便绘图连续
    df1.fillna(method='bfill',inplace=True)
    df1.fillna(method='ffill',inplace=True)
    
    for c in list(df1):
        if df1[c].max() > axhline_value and df1[c].min() < axhline_value:
            axhline_label='零线'   #显示零线，但不标注图例        
        #df1.rename(columns={c:ticker_name(c)},inplace=True)
    
    #共同脚注   
    rar_text=ectranslate(rar)
    if check_language()=="English":
        if rar != "alpha":
            rar_text=rar_text.title()+" Ratio"
        else:
            #rar_text=rar_text.title()
            rar_text="Jensen Alpha"
    
    footnote1=text_lang("注：","Note: ")+rar_text.capitalize()+text_lang("基于"," based on ")+ectranslate(ret_type)+text_lang("。",", ")
    """
    if RF !=0:
        footnote2=text_lang("年化无风险利率","RF = ")+str(round(RF*100,4))+text_lang('%。','% pa')
    else:
        footnote2=text_lang("假设年化无风险利率为零。","assuming RF = 0 pa.")
    """
    footnote2=text_lang("年化无风险利率","RF = ")+str(round(RF*100,4))+text_lang('%。','% pa')
    
    footnote3=''
    if rar.lower() in ['treynor','alpha']:
        mktidx_text=''
        if mktidx != 'auto':
            mktidx_text=ticker_name(mktidx)
            
        if mktidx != 'auto':
            footnote3=text_lang("CAPM回归期间","\nCAPM rolling ")+str(regression_period)+text_lang("个自然日，"," days, ")+ \
                text_lang("市场指数基于","using ")+mktidx_text
        else:
            footnote3=text_lang("CAPM回归期间","\nCAPM rolling ")+str(regression_period)+text_lang("个自然日"," days")
    
    import datetime; todaydt = datetime.date.today()
    footnote4=text_lang("数据来源: 综合新浪/EM/Stooq/Yahoo/SWHY，","Data source: Sina/Stooq/Yahoo, ")+str(todaydt)
    if footnote3 !='':
        footnotex=footnote1+footnote2+footnote3+'\n'+footnote4
    else:
        footnotex=footnote1+footnote2+footnote3+'\n'+footnote4

    #绘图
    if graph:
                
        title_txt=text_lang("风险调整收益：","Risk-adjusted Return: ")+rar_text
        y_label=rar_text

        draw_lines(df1,y_label,x_label=footnotex, \
                   axhline_value=axhline_value,axhline_label=axhline_label, \
                   title_txt=title_txt,data_label=False, \
                        attention_value=attention_value,attention_value_area=attention_value_area, \
                        attention_point=attention_point,attention_point_area=attention_point_area, \
                            band_area=band_area, \
                   annotate=annotate,annotate_value=annotate, \
                   mark_top=mark_top,mark_bottom=mark_bottom, \
                   mark_start=mark_start,mark_end=mark_end, \
                   facecolor=facecolor,loc=loc1)
            
    #制表
    recommenddf=pd.DataFrame()
    if printout:
        if sortby=='tpw_mean':
            sortby_txt=text_lang('按推荐标记+近期优先加权平均值降序排列',"by Recommend + RWA, Descending")
        elif sortby=='min':
            sortby_txt=text_lang('按推荐标记+最小值降序排列',"by Recommend + Min, Descending")
        elif sortby=='mean':
            sortby_txt=text_lang('按推荐标记+平均值降序排列',"by Recommend + Mean, Descending")
        elif sortby=='median':
            sortby_txt=text_lang('按推荐标记+中位数值降序排列',"by Recommend + Median, Descending")
        elif sortby=='trailing':
            sortby_txt=text_lang('按推荐标记+短期均值走势降序排列',"by Recommend + Recent Trend, Descending")
        
        #title_txt='***** 风险调整收益评估：基于'+ectranslate(rar)+'，'+sortby_txt+' *****'
        title_txt=text_lang('风险调整收益评估：',"RaR Evaluation: ")+rar_text+text_lang('，',', ')+sortby_txt
        
        footnote6=text_lang('期间：',"Period: ")+str(start)+text_lang('至'," to ")+str(end)+text_lang("；近期指近","\nRecent trend: ")+str(trailing)+text_lang("个交易日。趋势变化率阈值：", " trading days. Trend change threshhold: ")+str(trend_threshhold)
        footnote7=text_lang("近期优先趋势和星号为风险调整收益指标加趋势等多项因素综合研判，最多五颗星","Recommend max 5 stars. RWA = Recent-priority Weighted Average")
        footnotey=footnote6+'\n'+footnote7+'\n'+footnotex
        
        #不能简单删除含有Nan的行，否则导致清空df1，应该进行填充
        #df1.dropna(inplace=True,axis=1)    
        recommenddf=descriptive_statistics2(df1,title_txt,footnotey,decimals=4, \
                               sortby=sortby,recommend_only=True,trailing=trailing, \
                               trend_threshhold=trend_threshhold, \
                               style_print=style_print,facecolor=facecolor)            
 
    return df,recommenddf

#==============================================================================
if __name__=='__main__':
    ticker=["600519.SS","000858.SZ"]
    ticker={'Market':('US','^SPX','中概教培组合'),'EDU':0.7,'TAL':0.3}
    
    start="2024-1-1"
    end="2024-3-15"
    rar=['sharpe','alpha']
    ret_type="Monthly Ret%"
    RF=0.01759
    regression_period=365
    
    graph=False; axhline_value=0; axhline_label=''
    printout=True; sortby='tpw_mean'; trailing=5; trend_threshhold=0.01
    annotate=False
    mktidx='auto'; source='auto'
    
    rars=compare_mticker_mrar(ticker,start,end,rar,graph=False,printout=True)

def compare_mticker_mrar(ticker,start,end,rar=['sharpe','alpha','sortino','treynor'], \
                         ret_type="Annual Adj Ret%",RF=0,regression_period=365, \
                            attention_value='',attention_value_area='', \
                            attention_point='',attention_point_area='', \
                                band_area='', \
                         graph=True,loc1='best', \
                         axhline_value=0,axhline_label='', \
                         printout=True,sortby='tpw_mean',trailing=7,trend_threshhold=0.01, \
                         annotate=False,annotate_value=False, \
                         mark_top=False,mark_bottom=False, \
                         mark_start=False,mark_end=False, \
                         mktidx='auto',source='auto', \
                         ticker_type='auto',facecolor='whitesmoke'):
    """
    功能：多只股票，多个rar，综合对比和排列。支持股票和投资组合
    """
    
    #避免下面的循环出错
    if isinstance(rar,str):
        rar=[rar] 
    if isinstance(ret_type,list):
        ret_type=ret_type[0] 
    if isinstance(RF,list):
        RF=RF[0] 
    if isinstance(regression_period,list):
        regression_period=regression_period[0] 
    
    #print("  Starting to compare multiple tickers with multiple RARs ......")
    
    df=pd.DataFrame() 
    for r in rar:
        #with HiddenPrints(): #此项将压制所有print输出，造成表头脚注不显示
        _,df_tmp=compare_mticker_1rar(ticker=ticker,start=start,end=end,rar=r, \
                                 ret_type=ret_type,RF=RF,regression_period=regression_period, \
                                    attention_value=attention_value,attention_value_area=attention_value_area, \
                                    attention_point=attention_point,attention_point_area=attention_point_area, \
                                        band_area=band_area, \
                                 graph=graph,facecolor=facecolor, \
                                 axhline_value=axhline_value,axhline_label=axhline_label, \
                                 printout=printout,sortby=sortby, \
                                 trailing=trailing,trend_threshhold=trend_threshhold, \
                                 annotate=annotate,annotate_value=annotate, \
                                 mark_top=mark_top,mark_bottom=mark_bottom, \
                                 mark_start=mark_start,mark_end=mark_end, \
                                 mktidx=mktidx,source=source,style_print=True, \
                                 ticker_type=ticker_type,loc1=loc1)        
        if df_tmp is None:
            break
        else:
            dft=df_tmp[['比较对象','推荐标记']]
            dft.rename(columns={'推荐标记':r},inplace=True)
            
        if len(df)==0: #第一个
            df=dft 
        else:
            df=pd.merge(df,dft,how='left',left_on='比较对象',right_on='比较对象')
    
    df['综合推荐']=df[rar].sum(axis=1)
    df.sort_values(by='综合推荐',ascending=False,inplace=True)
    
    df['综合推荐']=df['综合推荐'].apply(lambda x: generate_stars(hzlen(x) / len(rar)))
    for c in list(df):
        df.rename(columns={c:ectranslate(c)},inplace=True)
    
    if printout:
        # 设置显示选项为True，开启Unicode字符支持
        pd.set_option('display.unicode.ambiguous_as_wide', True)
        pd.set_option('display.unicode.east_asian_width', True)
        pd.set_option('display.width', 180) #设置打印宽度(**重要**)

        if sortby=='tpw_mean':
            sortby_txt=text_lang('按推荐标记+近期优先加权平均值降序排列',"by Recommend + RWA, Descending")
        elif sortby=='min':
            sortby_txt=text_lang('按推荐标记+最小值降序排列',"by Recommend + Min, Descending")
        elif sortby=='mean':
            sortby_txt=text_lang('按推荐标记+平均值降序排列',"by Recommend + Mean, Descending")
        elif sortby=='median':
            sortby_txt=text_lang('按推荐标记+中位数值降序排列',"by Recommend + Median, Descending")
        elif sortby=='trailing':
            sortby_txt=text_lang('按推荐标记+短期均值走势降序排列',"by Recommend + Recent Trend, Descending")
        
        df1=df.copy()
        df1.reset_index(drop=True,inplace=True)
        df1.index=df1.index + 1
        
        # 处理表格标题
        #titletxt='===风险调整收益综合对比：'+sortby_txt+'==='
        titletxt=text_lang('风险调整收益综合对比：',"Risk-adjusted Return Overall Evaluation: ")+sortby_txt
        """
        #print("\n"+titletxt)
        df2=df1.style.set_caption(titletxt).set_table_styles(
            [{'selector':'caption',
              'props':[('color','black'),('font-size','16px'),('font-weight','bold')]}])        
        
        df3= df2.set_properties(**{'text-align':'center'})
        from IPython.display import display
        display(df3)
        """
        """
        disph=df1.style.hide() #不显示索引列
        dispp=disph.format(precision=3) #设置带有小数点的列精度调整为小数点后3位
        #设置标题/列名
        dispt=dispp.set_caption(titletxt).set_table_styles(
            [{'selector':'caption', #设置标题
              'props':[('color','black'),('font-size','16px'),('font-weight','bold')]}, \
             {'selector':'th.col_heading', #设置列名
               'props':[('color','black'),('font-size','16px'),('background-color',facecolor),('text-align','center'),('margin','auto')]}])        
        #设置列数值对齐
        dispt1=dispt.set_properties(**{'font-size':'16px'})
        dispf=dispt1.set_properties(**{'text-align':'center'})
        #设置前景背景颜色
        try:
            dispf2=dispf.set_properties(**{'background-color':facecolor,'color':'black'})
        except:
            print("  #Warning(compare_mticker_mrar): color",facecolor,"is unsupported, changed to default setting")
            dispf2=dispf.set_properties(**{'background-color':'whitesmoke','color':'black'})
    
        from IPython.display import display
        display(dispf2)
        """
        
        """
        print(df1.to_string(justify='left'))
        
        justify_dict={}
        for c in df1.columns:
            if c=='比较对象':
                justify_dict[c]='left'
            else:
                justify_dict[c]='center'
        print(df1.to_string(justify=justify_dict))
        """
        
        """
        alignlist=['right','left']+['center']*(len(list(df1))-3)+['center','center']
        try:   
            print(df1.to_markdown(index=True,tablefmt='plain',colalign=alignlist))
        except:
            #解决汉字编码gbk出错问题
            df2=df1.to_markdown(index=True,tablefmt='plain',colalign=alignlist)
            df3=df2.encode("utf-8",errors="strict")
            print(df3)
        
        print("\n$$$$$$$$ 左调节打印")
        df2=df1.copy()
        max_len=max([len(col) for col in df2.columns]) #找到最长的列名长度
        for col in df2.columns:
            df2[col]=df2[col].astype(str) #将每列的值强制转换为字符串类型
            df2[col]=df2[col].apply(lambda x: x.ljust(max_len)) #调整每列的宽度
        print(df2)
        
        print("\n$$$$$$$$ tabulate打印")
        from tabulate import tabulate
        print(tabulate(df1,headers=list(df1)))
        """
        
        #脚注
        footnote1=text_lang("风险调整收益基于","RaR based on ")+ectranslate(ret_type)+text_lang("，",', ')
        """
        if RF !=0:
            footnote2=text_lang("年化无风险利率","RF = ")+str(round(RF*100,4))+text_lang('%','% pa')
        else:
            footnote2=text_lang("假设年化无风险利率为零","assuming RF = 0 pa")
        """
        footnote2=text_lang("年化无风险利率","RF = ")+str(round(RF*100,4))+text_lang('%','% pa')
        
        footnote3=''
        if 'treynor' in rar or 'alpha' in rar:
            if mktidx=='auto':
                mktidx=get_market_index_code(ticker[0] if isinstance(ticker,list) else ticker)
            mktidx_name=ticker_name(mktidx)
            footnote3=text_lang("CAPM基于","CAPM using ")+mktidx_name+text_lang("，回归期间",", rolling ")+str(regression_period)+text_lang("个自然日"," days")
        
        import datetime; todaydt = datetime.date.today()
        footnote4=text_lang("数据来源: 综合新浪/EM/Stooq/Yahoo/SWHY，","Data source: Sina/Stooq/Yahoo, ")+str(todaydt)+text_lang("统计",'')
        if footnote3 !='':
            footnotex=footnote1+footnote2+'\n'+footnote3+'\n'+footnote4
        else:
            footnotex=footnote1+footnote2+'\n'+footnote4
    
        #print("\n"+footnotex)
        #print(footnotex)
        if check_language()=="English":
            df1.rename(columns={"比较对象":"Securities","sharpe":"Sharpe Ratio","sortino":"Sortino Ratio","alpha":"Jensen Alpha","treynor":"Treynor Ratio","综合推荐":"Overall Recommend"},inplace=True)
            
        df_display_CSS(df1,titletxt=titletxt,footnote=footnotex,decimals=4, \
                       first_col_align='left',second_col_align='center', \
                       last_col_align='center',other_col_align='center')
 
    return df

#==============================================================================
if __name__=='__main__':
    ticker="600519.SS"
    ticker={'Market':('US','^SPX','中概教培组合'),'EDU':0.7,'TAL':0.3}
    
    start="2024-1-1"
    end="2024-3-15"
    rar='sharpe'
    ret_type=["Monthly Ret%","Annual Ret%"]
    RF=0.01759
    regression_period=365
    
    graph=True; axhline_value=0; axhline_label=''
    printout=False; sortby='tpw_mean'; trailing=5; trend_threshhold=0.001
    annotate=False
    mktidx='auto'; source='auto'
    
    rars=compare_1ticker_1rar_mret(ticker,start,end,rar,ret_type,printout=True)

def compare_1ticker_1rar_mret(ticker,start,end,rar='sharpe', \
                         ret_type=["Annual Adj Ret%","Monthly Adj Ret%"], \
                         RF=0,regression_period=365, \
                             attention_value='',attention_value_area='', \
                             attention_point='',attention_point_area='', \
                                 band_area='', \
                         graph=True,loc1='best', \
                         axhline_value=0,axhline_label='',facecolor='whitesmoke', \
                         printout=False,sortby='tpw_mean',trailing=7,trend_threshhold=0.01, \
                         annotate=False,annotate_value=False, \
                         mark_top=False,mark_bottom=False, \
                         mark_start=False,mark_end=False, \
                         mktidx='auto',source='auto',ticker_type='auto'):
    """
    功能：一只股票，同一个rar，对比其不同的收益率类型，支持股票和投资组合
    """
    
    import os,sys
    class HiddenPrints:
        def __enter__(self):
            self._original_stdout = sys.stdout
            sys.stdout = open(os.devnull, 'w')

        def __exit__(self, exc_type, exc_val, exc_tb):
            sys.stdout.close()
            sys.stdout = self._original_stdout
    
    #转换字符串和列表，避免下面的循环出错
    if isinstance(ticker,list):
        ticker=ticker[0]
    if isinstance(rar,list):
        rar=rar[0]
    if isinstance(ret_type,str):
        ret_type=[ret_type]
    if isinstance(RF,list):
        RF=RF[0]
    if isinstance(regression_period,list):
        regression_period=regression_period[0]
    print("  Working on",rar,"ratio for",ticker_name(ticker,ticker_type),"in different return types ......\n")
        
    df=pd.DataFrame() 
    for t in ret_type:
        #关闭print输出
        with HiddenPrints():
            df_tmp=get_rar(ticker,start,end,rar,ret_type=t, \
                        RF=RF,regression_period=regression_period,mktidx=mktidx, \
                        source=source,ticker_type=ticker_type)
        
        if df_tmp is None:
            break
        else:
            dft=df_tmp[[rar]]
            tname=text_lang("基于","Based on ")+ectranslate(t)
            dft.rename(columns={rar:text_lang("基于","Based on ")+ectranslate(t)},inplace=True)
            
            # 将band_area中的ticker替换为tname
            if band_area != '':
                for index, item in enumerate(band_area):
                    if item == t:
                        band_area[index] = tname               
            
        if len(df)==0: #第一个
            df=dft 
        else:
            df=pd.merge(df,dft,how='outer',left_index=True,right_index=True)

    if len(df)==0:
        print("  #Error(compare_mticker_1rar): rar data not available for",ticker_name(ticker,ticker_type),"between",start,end)        
        return None
    
    #仅用于绘图和制表
    df1=df.copy()
    for c in list(df1):
        if df1[c].max() > axhline_value and df1[c].min() < axhline_value:
            axhline_label='零线'   
        #df1.rename(columns={c:"基于"+ectranslate(c)},inplace=True)
        
    #共同脚注    
    footnote1=text_lang("注：","Note: ")
    """
    if RF !=0:
        footnote2=text_lang("年化无风险利率为","RF = ")+str(round(RF*100,4))+text_lang('%。','% pa. ')
    else:
        footnote2=text_lang("假设年化无风险利率为零。","Assuming RF = 0 pa")
    """
    footnote2=text_lang("年化无风险利率为","RF = ")+str(round(RF*100,4))+text_lang('%。','% pa. ')
    
    footnote3=''
    if rar.lower() in ['treynor','alpha']:
        footnote3=text_lang("CAPM回归期间","CAPM rolling ")+str(regression_period)+text_lang("个自然日"," days")
    
    import datetime; todaydt = datetime.date.today()
    footnote4=text_lang("数据来源: 综合新浪/EM/Stooq/Yahoo/SWHY，","Data source: Sina/Stooq/Yahoo, ")+str(todaydt)
    if footnote3 !='':
        footnotex=footnote1+footnote2+footnote3+'\n'+footnote4
    else:
        footnotex=footnote1+footnote2+footnote3+'\n'+footnote4

    #绘图
    if graph:
        
        title_txt=text_lang("风险调整收益：","Risk-adjusted Return: ")+ticker_name(ticker,ticker_type)
        y_label=ectranslate(rar)

        draw_lines(df1,y_label,x_label=footnotex, \
                   axhline_value=axhline_value,axhline_label=axhline_label, \
                   title_txt=title_txt,data_label=False, \
                        attention_value=attention_value,attention_value_area=attention_value_area, \
                        attention_point=attention_point,attention_point_area=attention_point_area, \
                   annotate=annotate,annotate_value=annotate, \
                       band_area=band_area, \
                   mark_top=mark_top,mark_bottom=mark_bottom, \
                   mark_start=mark_start,mark_end=mark_end, \
                   facecolor=facecolor,loc=loc1)
            
    #制表
    recommenddf=pd.DataFrame()
    if printout:
        if sortby=='tpw_mean':
            sortby_txt=text_lang('按推荐标记+近期优先加权平均值降序排列',"by Recommend + RWA, Descending")
        elif sortby=='min':
            sortby_txt=text_lang('按推荐标记+最小值降序排列',"by Recommend + Min, Descending")
        elif sortby=='mean':
            sortby_txt=text_lang('按推荐标记+平均值降序排列',"by Recommend + Mean, Descending")
        elif sortby=='median':
            sortby_txt=text_lang('按推荐标记+中位数值降序排列',"by Recommend + Median, Descending")
        elif sortby=='trailing':
            sortby_txt=text_lang('按推荐标记+短期均值走势降序排列',"by Recommend + Recent Trend, Descending")
        
        #title_txt='***** 风险调整收益评估：'+'基于'+ectranslate(rar)+'，'+ticker_name(ticker,ticker_type)+'，'+sortby_txt+' *****'
        title_txt=text_lang('风险调整收益评估：',"RaR Evaluation: ")+ectranslate(rar)+text_lang('，',', ')+sortby_txt
        
        footnote6=text_lang('期间：',"Period: ")+str(start)+text_lang('至'," to ")+str(end)+text_lang("；近期指近","\nRecent trend: ")+str(trailing)+text_lang("个交易日。趋势变化率阈值：", " days. Trend threshhold ")+str(trend_threshhold)
        footnote7=text_lang("近期优先趋势和星号为风险调整收益指标加趋势等多项因素综合研判，最多五颗星","Recommend max 5 stars. RWA = Recent-priority Weighted Average")        
        footnotey=footnote6+'\n'+footnote7+'\n'+footnotex

        #删除含有Nan的行
        df1.dropna(inplace=True)    

        recommenddf=descriptive_statistics2(df1,title_txt,footnotey,decimals=4, \
                               sortby=sortby,recommend_only=True,trailing=trailing, \
                               trend_threshhold=trend_threshhold,facecolor=facecolor)            
 
    return df,recommenddf

#==============================================================================
if __name__=='__main__':
    ticker="600519.SS"
    ticker={'Market':('US','^SPX','中概教培组合'),'EDU':0.7,'TAL':0.3}
    ticker={'Market':('China','000300.SS','白酒组合'),'600519.SS':0.2,'000858.SZ':0.3,'600809.SS':0.5}
    
    start="2024-3-18"; end="2024-3-22"
    rar='alpha'
    rar='sharpe'
    ret_type="Annual Ret%"
    RF=[0.005,0.01759,0.05]
    regression_period=365
    
    graph=True; axhline_value=0; axhline_label=''
    printout=False; sortby='tpw_mean'; trailing=5; trend_threshhold=0.001
    annotate=False
    mktidx='auto'; source='auto'
    
    rars=compare_1ticker_1rar_1ret_mRF(ticker,start,end,rar,ret_type,RF)

def compare_1ticker_1rar_1ret_mRF(ticker,start,end,rar='sharpe', \
                         ret_type="Annual Adj Ret%",RF=[0,0.02,0.05],regression_period=365, \
                            attention_value='',attention_value_area='', \
                            attention_point='',attention_point_area='', \
                                band_area='', \
                         graph=True,loc1='best', \
                         axhline_value=0,axhline_label='',facecolor='whitesmoke', \
                         printout=False,sortby='tpw_mean',trailing=7,trend_threshhold=0.01, \
                         annotate=False,annotate_value=False, \
                         mark_top=False,mark_bottom=False, \
                         mark_start=False,mark_end=False, \
                         mktidx='auto',source='auto',ticker_type='auto'):
    """
    功能：一只股票，相同的rar，相同的收益率类型，不同的无风险收益率
    支持股票和投资组合
    """
    
    import os,sys
    class HiddenPrints:
        def __enter__(self):
            self._original_stdout = sys.stdout
            sys.stdout = open(os.devnull, 'w')

        def __exit__(self, exc_type, exc_val, exc_tb):
            sys.stdout.close()
            sys.stdout = self._original_stdout
    
    #转换字符串和列表，避免下面的循环出错
    if isinstance(ticker,list):
        ticker=ticker[0]
    if isinstance(rar,list):
        rar=rar[0]
    if isinstance(ret_type,list):
        ret_type=[ret_type]
    if isinstance(RF,float):
        RF=[RF]
    if isinstance(regression_period,list):
        regression_period=regression_period[0]
    print("  Working on",rar,"ratio for",ticker_name(ticker,ticker_type),"in different RF levels ......\n")
        
    df=pd.DataFrame() 
    for t in RF:
        #关闭print输出
        with HiddenPrints():
            df_tmp=get_rar(ticker,start,end,rar,ret_type, \
                        RF=t,regression_period=regression_period,mktidx=mktidx, \
                            source=source,ticker_type=ticker_type)
        
        if df_tmp is None:
            break
        else:
            dft=df_tmp[[rar]]
            tname=text_lang("RF=","RF=")+str(round(t*100,4))+'%'
            dft.rename(columns={rar:tname},inplace=True)
            
            # 将band_area中的ticker替换为tname
            if band_area != '':
                for index, item in enumerate(band_area):
                    if item == t:
                        band_area[index] = tname              
            
        if len(df)==0: #第一个
            df=dft 
        else:
            df=pd.merge(df,dft,how='outer',left_index=True,right_index=True)

    if len(df)==0:
        print("  #Error(compare_mticker_1rar): rar data inaccessible for",ticker_name(ticker,ticker_type),"between",start,end)        
        return None
    
    #仅用于绘图和制表
    df1=df.copy()
    for c in list(df1):
        if df1[c].max() > axhline_value and df1[c].min() < axhline_value:
            axhline_label='零线'   
        #df1.rename(columns={c:"基于无风险利率"+c},inplace=True)
        
    #共同脚注    
    footnote1=text_lang("注：","Note: ")+ectranslate(rar)+text_lang("基于"," based on ")+ectranslate(ret_type)+text_lang('。','')
    footnote2=""
        
    footnote3=""
    if rar.lower() in ['treynor','alpha']:
        footnote3="贝塔系数回归期间"+str(regression_period)+"个自然日"
    
    import datetime; todaydt = datetime.date.today()
    footnote4=text_lang("数据来源: 综合新浪/EM/Stooq/Yahoo/SWHY，","Data source: Sina/Stooq/Yahoo, ")+str(todaydt)
    if footnote3 !='':
        footnotex=footnote1+footnote3+'\n'+footnote4
    else:
        footnotex=footnote1+footnote4

    #绘图
    if graph:
        
        title_txt=text_lang("风险调整收益：","Risk-adjusted Return: ")+ticker_name(ticker,ticker_type)
        y_label=ectranslate(rar)

        draw_lines(df1,y_label,x_label=footnotex, \
                   axhline_value=axhline_value,axhline_label=axhline_label, \
                   title_txt=title_txt,data_label=False, \
                        attention_value=attention_value,attention_value_area=attention_value_area, \
                        attention_point=attention_point,attention_point_area=attention_point_area, \
                   annotate=annotate,annotate_value=annotate, \
                       band_area=band_area, \
                   mark_top=mark_top,mark_bottom=mark_bottom, \
                   mark_start=mark_start,mark_end=mark_end, \
                   facecolor=facecolor,loc=loc1)
            
    #制表
    recommenddf=pd.DataFrame()
    if printout:
        if sortby=='tpw_mean':
            sortby_txt=text_lang('按推荐标记+近期优先加权平均值降序排列',"by Recommend + RWA, Descending")
        elif sortby=='min':
            sortby_txt=text_lang('按推荐标记+最小值降序排列',"by Recommend + Min, Descending")
        elif sortby=='mean':
            sortby_txt=text_lang('按推荐标记+平均值降序排列',"by Recommend + Mean, Descending")
        elif sortby=='median':
            sortby_txt=text_lang('按推荐标记+中位数值降序排列',"by Recommend + Median, Descending")
        elif sortby=='trailing':
            sortby_txt=text_lang('按推荐标记+短期均值走势降序排列',"by Recommend + Recent Trend, Descending")
        
        #title_txt='***** 风险调整收益评估：'+'基于'+ectranslate(rar)+'，'+ticker_name(ticker,ticker_type)+'，'+sortby_txt+' *****'
        title_txt=text_lang('风险调整收益评估：',"RaR Evaluation: ")+ectranslate(rar)+text_lang('，',', ')+sortby_txt
        
        footnote6=text_lang('期间：',"Period: ")+str(start)+text_lang('至'," to ")+str(end)+text_lang("；近期指近","\nRecent trend: ")+str(trailing)+text_lang("个交易日。趋势变化率阈值：", " days. Trend threshhold ")+str(trend_threshhold)
        footnote7=text_lang("近期优先趋势和星号为风险调整收益指标加趋势等多项因素综合研判，最多五颗星","Recommend max 5 stars. RWA = Recent-priority Weighted Average")        
        footnotey=footnote6+footnote7+'\n'+footnotex

        #删除含有Nan的行
        df1.dropna(inplace=True)    

        recommenddf=descriptive_statistics2(df1,title_txt,footnotey,decimals=4, \
                               sortby=sortby,recommend_only=True,trailing=trailing, \
                               trend_threshhold=trend_threshhold,facecolor=facecolor)            
 
    return df,recommenddf

#==============================================================================
# 合成函数
#==============================================================================
if __name__=='__main__':
    ticker="301161.SZ"
    ticker="600519.SS"
    ticker=["600519.SS","000858.SZ"]
    ticker={'Market':('US','^SPX','中概教培组合'),'EDU':0.7,'TAL':0.3}
    
    start="2024-1-1"; end="2024-9-30"
    
    rar='sharpe'
    rar='alpha'
    rar=['sharpe','alpha']
    
    ret_type="Monthly Adj Ret%"
    ret_type="Annual Adj Ret%"
    ret_type=["Monthly Adj Ret%","Annual Adj Ret%"]
    
    RF=0.01759
    RF=[0.005,0.01759,0.05]
    
    regression_period=365
    
    graph=True; axhline_value=0; axhline_label=''
    printout=False; sortby='tpw_mean'; trailing=5; trend_threshhold=0.001
    annotate=False
    mark_top=True; mark_bottom=True; mark_end=True
    mktidx='auto'; source='auto'; ticker_type='auto'
    
    rars=compare_rar_security(ticker,start,end,rar,ret_type,RF,
                              mark_top=True,mark_bottom=True,mark_end=True,
                              printout=True)
    

def compare_rar_security(ticker,start,end='today',indicator='sharpe', \
                         ret_type="Annual Adj Ret%", \
                         RF=0, \
                         regression_period=365, \
                            attention_value='',attention_value_area='', \
                            attention_point='',attention_point_area='', \
                                band_area='', \
                         graph=True,loc1='best', \
                         axhline_value=0,axhline_label='',power=0,facecolor='whitesmoke', \
                         printout=False,sortby='tpw_mean',trailing=7,trend_threshhold=0.05, \
                         annotate=False,annotate_value=False, \
                         mark_top=False,mark_bottom=False, \
                         mark_start=False,mark_end=False, \
                         mktidx='auto',source='auto', \
                         ticker_type='auto'):
    """
    功能：组合情况，可能多只股票，多个rar，多个收益率类型，多个无风险收益率
    
    注意：trailing=7,trend_threshhold=0.05，更加贴合视觉效果
    """
    start,end=start_end_preprocess(start,end)
    rar=indicator
    
    #情形1：多个证券
    if isinstance(ticker,list):
        if len(ticker) > 1:
            if isinstance(ret_type,list):
                ret_type=ret_type[0] 
            if isinstance(RF,list):
                RF=RF[0]  
            
            rar_num=0
            if isinstance(rar,str):
                rar_num=1
            if isinstance(rar,list):
                rar_num=len(rar)
                if rar_num==1: rar=rar[0]
                
            if rar_num ==1:   #一个RAR             
                df=compare_mticker_1rar(ticker=ticker,start=start,end=end,rar=rar, \
                            ret_type=ret_type,RF=RF,regression_period=regression_period, \
                                attention_value=attention_value,attention_value_area=attention_value_area, \
                                attention_point=attention_point,attention_point_area=attention_point_area, \
                                    band_area=band_area, \
                            graph=graph,loc1=loc1, \
                            axhline_value=axhline_value,axhline_label=axhline_label, \
                            printout=printout, \
                            sortby=sortby,trailing=trailing,trend_threshhold=trend_threshhold, \
                            annotate=annotate,annotate_value=annotate, \
                            mark_top=mark_top,mark_bottom=mark_bottom, \
                            mark_start=mark_start,mark_end=mark_end, \
                            mktidx=mktidx,source=source, \
                            ticker_type=ticker_type,facecolor=facecolor)
                return df
                
            if rar_num >1:    #多个RAR，此项的主要意图并非绘图，而是进行多指标综合推荐   
                printout=True #否则无法运行descriptive_statistics2函数
                df=compare_mticker_mrar(ticker=ticker,start=start,end=end,rar=rar, \
                            ret_type=ret_type,RF=RF,regression_period=regression_period, \
                                attention_value=attention_value,attention_value_area=attention_value_area, \
                                attention_point=attention_point,attention_point_area=attention_point_area, \
                                    band_area=band_area, \
                            graph=graph,loc1=loc1, \
                            axhline_value=axhline_value,axhline_label=axhline_label, \
                            printout=printout, \
                            sortby=sortby,trailing=trailing,trend_threshhold=trend_threshhold, \
                            annotate=annotate,annotate_value=annotate, \
                            mark_top=mark_top,mark_bottom=mark_bottom, \
                            mark_start=mark_start,mark_end=mark_end, \
                            mktidx=mktidx,source=source, \
                            ticker_type=ticker_type,facecolor=facecolor)
                return df            
        else:
            #实际上是单个证券
            ticker=ticker[0]                
    
    #情形2：1只证券，多个RAR
    if isinstance(rar,list):
        if len(rar) > 1:
            if isinstance(ret_type,list):
                ret_type=ret_type[0] 
            if isinstance(RF,list):
                RF=RF[0]  
                
            df=compare_1ticker_mrar(ticker=ticker,start=start,end=end,rar=rar, \
                            ret_type=ret_type,RF=RF,regression_period=regression_period, \
                                attention_value=attention_value,attention_value_area=attention_value_area, \
                                attention_point=attention_point,attention_point_area=attention_point_area, \
                                    band_area=band_area, \
                            graph=graph,loc1=loc1, \
                            axhline_value=axhline_value,axhline_label=axhline_label, \
                            printout=printout,facecolor=facecolor, \
                            sortby=sortby,trailing=trailing,trend_threshhold=trend_threshhold, \
                            annotate=annotate,annotate_value=annotate, \
                            mark_top=mark_top,mark_bottom=mark_bottom, \
                            mark_start=mark_start,mark_end=mark_end, \
                            mktidx=mktidx,source=source, \
                            ticker_type=ticker_type)
            return df
        else:
            #实际上是单个RAR
            rar=rar[0]      
    
    #情形3：1只证券，1个RAR，多个收益率类型
    if isinstance(ret_type,list):
        if len(ret_type) > 1:
            if isinstance(RF,list):
                RF=RF[0]  
                
            df=compare_1ticker_1rar_mret(ticker=ticker,start=start,end=end,rar=rar, \
                            ret_type=ret_type,RF=RF,regression_period=regression_period, \
                                attention_value=attention_value,attention_value_area=attention_value_area, \
                                attention_point=attention_point,attention_point_area=attention_point_area, \
                                    band_area=band_area, \
                            graph=graph,loc1=loc1, \
                            axhline_value=axhline_value,axhline_label=axhline_label, \
                            printout=printout, \
                            sortby=sortby,trailing=trailing,trend_threshhold=trend_threshhold, \
                            annotate=annotate,annotate_value=annotate, \
                            mark_top=mark_top,mark_bottom=mark_bottom, \
                            mark_start=mark_start,mark_end=mark_end, \
                            mktidx=mktidx,source=source, \
                            ticker_type=ticker_type,facecolor=facecolor)
            return df
        else:
            #实际上是单个收益率类型
            ret_type=ret_type[0]     
    
    #情形4：1只证券，1个RAR，1个收益率类型，多个RF
    if isinstance(RF,list):
        if len(RF) > 1:
                
            df=compare_1ticker_1rar_1ret_mRF(ticker=ticker,start=start,end=end,rar=rar, \
                            ret_type=ret_type,RF=RF,regression_period=regression_period, \
                                attention_value=attention_value,attention_value_area=attention_value_area, \
                                attention_point=attention_point,attention_point_area=attention_point_area, \
                                    band_area=band_area, \
                            graph=graph,loc1=loc1, \
                            axhline_value=axhline_value,axhline_label=axhline_label, \
                            printout=printout,facecolor=facecolor, \
                            sortby=sortby,trailing=trailing,trend_threshhold=trend_threshhold, \
                            annotate=annotate,annotate_value=annotate, \
                            mark_top=mark_top,mark_bottom=mark_bottom, \
                            mark_start=mark_start,mark_end=mark_end, \
                            mktidx=mktidx,source=source, \
                            ticker_type=ticker_type)
            return df
        else:
            #实际上是单个RF
            RF=RF[0]       

    #情形5：1只证券，1个RAR，1个收益率类型，1个RF
    df=compare_1ticker_mrar(ticker=ticker,start=start,end=end,rar=rar, \
                             ret_type=ret_type,RF=RF,regression_period=regression_period, \
                                attention_value=attention_value,attention_value_area=attention_value_area, \
                                attention_point=attention_point,attention_point_area=attention_point_area, \
                             graph=graph,loc1=loc1, \
                             axhline_value=axhline_value,axhline_label=axhline_label,power=power, \
                             printout=printout,sortby=sortby, \
                             trailing=trailing,trend_threshhold=trend_threshhold, \
                             annotate=annotate,annotate_value=annotate, \
                             mark_top=mark_top,mark_bottom=mark_bottom, \
                             mark_start=mark_start,mark_end=mark_end, \
                             mktidx=mktidx,source=source, \
                             ticker_type=ticker_type,facecolor=facecolor)
        
    return df


#==============================================================================
#==============================================================================

#==============================================================================
#==============================================================================
#==============================================================================
#==============================================================================
#==============================================================================
