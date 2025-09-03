# -*- coding: utf-8 -*-
"""
本模块功能：证券事件分析法
所属工具包：证券投资分析工具SIAT 
SIAT：Security Investment Analysis Tool
创建日期：2024年11月14日
最新修订日期：
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
#from siat.security_trend2 import *

from siat.stock import *
#from siat.security_prices import *
#from siat.security_price2 import *
#from siat.capm_beta2 import *
#from siat.risk_adjusted_return2 import *
#from siat.valuation import *

from siat.grafix import *

import pandas as pd; import numpy as np

import datetime as dt; stoday=str(dt.date.today())
#==============================================================================
#==============================================================================
if __name__=='__main__':
    #测试组1
    ticker='600519.SS'
    
    event_date='2024-4-2' #贵州茅台2023年报于2024年4月2日晚披露
    start='2024-3-1'; end='2024-4-30'
    event_window=[1,1] #事件发生时股市已经收盘，故检测下一个交易日的股市反应
    market_index='000001.SS' #贵州茅台在上交所上市，故使用上证综合指数
    RF=0

    #测试组1b
    ticker='600519.SS'
    
    event_date='2024-4-2' #贵州茅台2023年报于2024年4月2日晚披露
    start='2024-3-1'; end='2024-4-30'
    event_window=[0,2] #事件发生时股市已经收盘，故检测下一个交易日的股市反应
    market_index='000001.SS' #贵州茅台在上交所上市，故使用上证综合指数
    RF=0
    
    #测试组2
    ticker=['600519.SS','399997.SZ']
    
    event_date='2024-3-15' #315晚会
    start='2024-3-1'; end='2024-3-30'
    event_window=[1,2]
    market_index='000300.SS'
    RF="market model"
    
    #测试组3
    ticker=['600519.SS','399997.SZ']
    
    event_date='2024-4-2' #贵州茅台2023年报披露日
    start='auto'; end='auto'
    event_window=[0,1]
    method='CAPM'
    market_index='000001.SS'
    RF="1YCNY.B"   
    
    #共同部分
    post_event_days=7
    method='CAPM'
    early_response_days=-2
    estimation_window_days=-365
    
    ret_type="Daily Adj Ret%"
    ticker_type='stock' #贵州茅台为股票
    facecolor="whitesmoke"
    show_AR=True
    show_RF=True
    show_BHAR=True
    loc='best'
    
    es=event_study("600519.SS",event_date="2024-4-2", \
                   start='2024-3-1',end='2024-4-30', \
                   event_window=[0,0],post_event_days=7, \
                   method='CAPM', \
                   market_index='000001.SS',RF=0.0143)
    
    es=event_study("600519.SS",event_date="2024-4-2", \
                   start='2024-3-15',end='2024-4-20', \
                   event_window=[0,1],post_event_days=7, \
                   method='CAPM', \
                   market_index='000001.SS',RF=0.0143) 
        
    es=event_study("600519.SS",event_date="2024-4-2", \
                   start='2024-3-1',end='2024-4-30', \
                   event_window=[0,0],post_event_days=7, \
                   method='market',market_index='000001.SS')
    
    es=event_study("600519.SS",event_date="2024-4-2", \
                   start='2024-3-1',end='2024-4-30', \
                   event_window=[0,0],post_event_days=7, \
                   method='random walk')        
        
        
def event_study(ticker,event_date, \
                start='auto',end='auto', \
                event_window=[1,3], \
                post_event_days=0, \
                method='CAPM', \
                early_response_days=-2, \
                estimation_window_days=-365, \
                market_index='000300.SS', \
                RF="market index", \
                ret_type="Daily Adj Ret%", \
                ticker_type='auto', \
                show_AR='auto',show_RF=False,show_BHAR=False, \
                draw_CAR=True,draw_BHAR=False, \
                facecolor="whitesmoke",loc='best'):
    """
    ===========================================================================
    功能：展示事件研究法的累计异常收益率CAR。
    参数：
    ticker：证券代码，可为股票、债券、基金、指数、国债收益率等。可为单个或多个。
    event_date：事件发生日（注意时区的影响），以此日期为基期0，注意该日期可能在周末或假日。
        注意：允许标注多个事件日，但仅以第一个事件日计算相关日期。
    start/end：展示事件影响的起止日期，至少需要将事件日、事件窗口和事件后窗口包括在内，主要用于绘图。
        注意：如果不绘制AR仅绘制CAR，事件窗口前CAR均为空，start日期在绘图中将不起作用。
    event_window：事件窗口的起止日期，为相对事件日的相对日期
        默认[0,0]，即事件当日一天。注意窗口期不宜过长，因为过长的期间中可能混杂其他事件的影响。
        注意：事件窗口不一定包括事件日（适用于事件日在非交易日的情形，例如周末或假日，或者在当日闭市后发生）
        如果事件日为非交易日，事件窗口需要后移至事件日后的第一个交易日。
        如果怀疑市场提前对事件发生反应，可以考虑前移事件窗口的开始日期。
        使用CAR时，事件窗口长度一般为数日；使用BHAR时可长达数月。
    post_event_days：用于分析事件窗口后的漂移效应，取事件窗口后多少天。
        默认不分析，取0天。可以指定天数，注意是否跨过非交易日情形，过长的窗口期也可能混杂其他事件的影响。
    method：估计事件窗口以及事件后窗口收益率预期值的方法
        默认为CAPM（主要用于ticker为股票等），即通常所说的市场模型法。
        如果ticker为股票等，也可直接使用指数收益率为其预期收益率，此时method为Market或Index，即常说的市场调整模型。
        如果ticker为指数，无法再借助指数，method只能使用Random Walk，即使用前一个收益率为预期收益率。
        注意：不管多个ticker时里面的不同证券类型，仅按第一个ticker的类型判断，并使用同一种证券类型。
        使用CAR时，对每日异常收益率相加，反映短期逐日异常收益的累积；使用BHAR时则为复利累积，反映长期异常收益。
    early_response_days：默认为-2，即提前2天市场就开始有反应。
        市场很可能对事件提前发生反应（因为泄密等原因），例如中国市场规定上市公司董事会开完后两天内必须披露。
        很可能刚开完董事会，市场就得到了消息。为规避这种情况对估计窗口的影响，可以调节此参数。
    estimation_window_days：当method使用CAPM时，用于估计贝塔系数和截距项，以便计算预期收益率。
        默认在事件窗口开始日期+提前反应天数前的365个自然日（约250个交易日）。
    market_index：当method为CAPM时，用于计算市场收益率。默认中国市场采用000300.SS。
        注意：需要根据不同市场采取不同的市场指数，例如香港市场为恒生指数，美国市场为标普500指数等。
    RF：年化无风险收益率
        默认使用市场模型"market index"自动计算，无需指定。
        可直接指定具体数值。
        也可指定特定指标替代，例如一年期中国国债收益率"1YCNY.B"或一年期美债收益率"1YUSY.B"等。
    ticker_type：显式指明ticker的证券类型，当siat误判其类型（中国内地股票/债券/基金）时使用，默认'auto'。
    show_RF：在使用市场模型或指定指标时是否显示计算出的RF均值，默认为False。
    show_AR：是否绘图时绘制异常收益率AR
        默认'auto'（单个ticker时绘制，多个时不绘制）。
        也可指定True/False强行绘制/不绘制。
    show_BHAR；是否显示BHAR数值，适用于长期窗口，默认否False。
    draw_CAR：是否绘制CAR曲线，默认是True。
    draw_BHAR：是否绘制BHAR曲线，默认否False。
        注意：对于短期窗口，CAR曲线与BHAR曲线差异微小，可能基本重合，因此建议仅绘制其中之一。
    facecolor：显式指定绘图背景颜色，默认"whitesmoke"。

    
    示例：美的收购库卡事件对股价的影响
    es=event_study(["000333.SZ"],
                     event_date="2021-11-24",
                     start='2021-11-20',end='2021-12-25',
                     event_window=[1,10],
                     post_event_days=15,
                     method='CAPM',
                     market_index='399001.SZ')
    """
    
    DEBUG=False
    DEBUG2=False
    
    #=====事件研究各个日期的计算与调整===========================================
    if isinstance(event_date,str):
        event_date=[date_adjust(event_date,adjust=0)]
    elif isinstance(event_date,list):
        event_date=[date_adjust(ed,adjust=0) for ed in event_date]
    else:
        print("  #Warning(event_study): invalid date or list of dates {}".format(event_date))
        return None
    event_date.sort() #升序排序
    
    #事件窗口日期：遇到周末需要调整，提前或顺延至最近的工作日
    event_window_new=event_window.copy() #列表的普通赋值仅为指针，新列表的改动也会影响原列表
    adjust_start=0
    event_window_start=date_adjust(event_date[0],adjust=event_window[0])
    if week_day(event_window_start) == 5: #周六
        if event_window[0] >= 0:
            adjust_start=2
        else:
            adjust_start=-1
    elif week_day(event_window_start) == 6: #周日
        if event_window[0] >= 0:
            adjust_start=1
        else:
            adjust_start=-2
    event_window_start=date_adjust(event_window_start,adjust=adjust_start)
    event_window_new[0]=event_window[0]+adjust_start

    adjust_end=0
    event_window_end=date_adjust(event_window_start,adjust=event_window[1]-event_window[0])
    if week_day(event_window_end) == 5: #周六
        if event_window[1] >= 0:
            adjust_end=2
        else:
            adjust_end=-1
    elif week_day(event_window_end) == 6: #周日
        if event_window[1] >= 0:
            adjust_end=1
        else:
            adjust_end=-2
    event_window_end=date_adjust(event_window_end,adjust=adjust_end)
    event_window_new[1]=event_window[1]+adjust_start+adjust_end
    
    if DEBUG:
        print("  DEBUG: event window is between {0} to {1}".format(event_window_start,event_window_end))

    if event_window_new != event_window:
        print("  #Notice: event window adjusted from {0} to {1} because of weekend".format(event_window,event_window_new))

    #事件后窗口日期
    post_event_start=date_adjust(event_window_end,adjust=0)
    if week_day(post_event_start) == 5: #周六
        post_event_start=date_adjust(post_event_start,adjust=2)
    elif week_day(post_event_start) == 6: #周日
        post_event_start=date_adjust(post_event_start,adjust=1)
    
    post_event_end=date_adjust(post_event_start,adjust=post_event_days)
    if week_day(post_event_end) == 5: #周六
        post_event_end=date_adjust(post_event_end,adjust=2)
    elif week_day(post_event_end) == 6: #周日
        post_event_end=date_adjust(post_event_end,adjust=1)
    
    if post_event_end > stoday:
        post_event_end = stoday
        
    if DEBUG:
        print("  DEBUG: post event window is between {0} to {1}".format(post_event_start,post_event_end))
    

    #事件窗口前日期
    event_eve_date=date_adjust(event_window_start,adjust=-1)
    if week_day(event_eve_date) == 5: #周六
        event_eve_date=date_adjust(event_eve_date,adjust=-1)
    elif week_day(event_eve_date) == 6: #周日
        event_eve_date=date_adjust(event_eve_date,adjust=-2)

    if DEBUG:
        print("  DEBUG: event eve is on {}".format(event_eve_date))
    
    #提前反应日期
    early_response_date=date_adjust(event_date[0],adjust=early_response_days)
    if week_day(early_response_date) == 5: #周六
        early_response_date=date_adjust(early_response_date,adjust=-1)
    elif week_day(early_response_date) == 6: #周日
        early_response_date=date_adjust(early_response_date,adjust=-2)

    if DEBUG:
        print("  DEBUG: early response started on {}".format(early_response_date))
        
    #估计窗口日期的计算
    est_window_end=date_adjust(early_response_date,adjust=-1)
    est_window_start=date_adjust(est_window_end,adjust=estimation_window_days)   
    if DEBUG:
        print("  DEBUG: regression period starts from {0} to {1}".format(est_window_start,est_window_end))
     
    #处理绘图时显示的日期范围
    if start=='auto':
        start=date_adjust(early_response_date,adjust=-7)
    if end=='auto':
        if len(ticker) == 1 or show_AR:
            end=date_adjust(post_event_end,adjust=7)
        else:
            end=date_adjust(post_event_end,adjust=2)
    
    #=====判断ticker是否为指数，调整预期收益率计算方法============================
    if isinstance(ticker,str):
        ticker=[ticker]
    elif isinstance(ticker,list):
        ticker=ticker
    else:
        print("  #Warning(event_study): unexpected type of ticker {}".format(ticker))
        return None
        
    if market_index in ticker:
        print("  #Warning(event_study): market_index {0} duplicated in and removed from ticker {1}".format(market_index,ticker))
        ticker.remove(market_index)        
    
    #tname=ticker_name(ticker[0],ticker_type)
    #检查ticker是否为指数或国债收益率
    """
    if ("指数" in tname or "index" in tname.lower()) or ("收益率" in tname or "yield" in tname.lower()):
        if not ("random" in method.lower() or "walk" in method.lower()):
            print("  #Notice: check the applicability of ticker {0}, method {1} with market index {2}".format(ticker[0],method,market_index))
    """
    
    #=====获取证券价格和/或相关指数数据==========================================
    #基于CAPM获取数据
    if 'capm' in method.lower(): 
        method_type="capm"
        df_ret=compare_msecurity(tickers=ticker+[market_index],measure=ret_type, \
                                 start=est_window_start,end=end, \
                                 ticker_type=ticker_type, \
                                 graph=False)
        
        if isinstance(RF,int) or isinstance(RF,float):
            #RF为具体数值
            RF_type="value"
        
        elif "market" in (str(RF)).lower() or "index" in (str(RF)).lower():
            #RF通过市场模型计算，无需指定
            RF_type="model"
        else:
            #指定RF代码，例如1YCNY.B，注意1：得到的是年化收益率%，注意2：中国的只有近一年的数据
            RF_type="code"

        if RF_type=="code":
            df_rf=compare_msecurity(tickers=RF,measure='Close', \
                                     start=est_window_start,end=end, \
                                     graph=False)
            RF=df_rf[list(df_rf)[0]].mean() / 100.0
            
    #基于市场指数获取数据
    elif 'market' in method.lower() or 'index' in method.lower(): 
        method_type="market"
        df_ret=compare_msecurity(tickers=ticker+[market_index],measure=ret_type, \
                                   start=est_window_start,end=end, \
                                   ticker_type=ticker_type, \
                                   graph=False)
            
    elif 'random' in method.lower() or 'walk' in method.lower(): 
        method_type="random"
        df_ret=compare_msecurity(tickers=ticker,measure=ret_type, \
                                   start=est_window_start,end=end, \
                                   ticker_type=ticker_type, \
                                   graph=False)
        for t in ticker_name(ticker,ticker_type):
            try:
                df_ret[t+"_predicted"]=df_ret[t].shift(1)
            except:
                #print("  #Warning(event_study): info not found for ticker {}".format(t))
                continue

    else:
        print("  #Warning(event_study): unexpected type of AR method {}".format(method))
        return None
        
    #=====计算异常收益率AR=====
    df_cols=list(df_ret)
    if method_type=='market': 
        for t in ticker_name(ticker,ticker_type):
            try:
                df_ret[t+'_AR']=df_ret[t] - df_ret[ticker_name(market_index)]
            except: continue
        
    elif method_type=='random':
        for t in ticker_name(ticker,ticker_type):
            try:
                df_ret[t+'_AR']=df_ret[t] - df_ret[t+"_predicted"]
            except: continue
            
    else: #按CAPM计算
        #CAPM回归期间数据
        est_window_startpd=pd.to_datetime(est_window_start)
        est_window_endpd  =pd.to_datetime(est_window_end)
        df_reg=df_ret[(df_ret.index >=est_window_startpd) & (df_ret.index <=est_window_endpd)].copy()
        
        #删除空缺值，否则回归会出错
        df_reg=df_reg.replace([np.nan, None], np.nan).dropna()
        
        import statsmodels.api as sm
        if RF_type in ["value","code"]:
            if not ("%" in ret_type): #注意：RF是年化收益率(需要转化为日收益率)，这里不是百分比
                X=df_reg[ticker_name(market_index)] - RF/365.0 #无截距项回归，指定RF具体数值
            else:
                X=df_reg[ticker_name(market_index)] - RF/365.0 * 100.0 #这里需要转化为日收益率百分比%
                
        else: #RF_type=="model"
            X=df_reg[ticker_name(market_index)]
            X=sm.add_constant(X) #有截距项回归，基于市场模型 

        if DEBUG:
            print("  DEBUG: method_type={0}, RF_type={1}, RF={2}".format(method_type,RF_type,RF))
        
        #CAPM回归
        beta_dict={}; intercept_dict={}; pvalue_dict={}; rf_dict={}
        for t in ticker_name(ticker,ticker_type):
            try:
                if RF_type in ["value","code"]:
                    if not ("%" in ret_type): #注意：RF是年化收益率(需要转化为日收益率)，不是百分比
                        y=df_reg[t] - RF/365.0
                    else:
                        y=df_reg[t] - RF/365.0 * 100.0
                
                else: #RF_type=="model"
                        y=df_reg[t]
            except: continue
            
            model = sm.OLS(y,X)	#定义回归模型y=X
            results = model.fit()	#进行OLS回归
            
            if DEBUG2:
                print("  DEBUG: RF_type={0}, results.params={1},results.pvalues={2}".format(RF_type,results.params,results.pvalues))
            
            #提取回归系数，详细信息见results.summary()
            if RF_type=="model":
                intercept=results.params[0]
                beta=results.params[1]; pvalue=results.pvalues[1]
                try:
                    #此处回归得到的rf应该为日收益率，转为年化收益率。
                    #注意：不同证券回归出的结果可能差异较大，原因可能是混入了回归残差！
                    if not ("%" in ret_type):
                        rf=intercept / (1-beta) * 365.0
                    else:
                        rf=intercept / (1-beta) / 100.0 * 365.0
                except: rf=0
                
            else: #RF_type in ["value","code"]
                intercept=0
                beta=results.params[0]; pvalue=results.pvalues[0]
                rf=RF
            
            beta_dict[t] = beta; intercept_dict[t] = intercept; pvalue_dict[t] = pvalue; rf_dict[t]=rf
            if DEBUG2:
                print("  DEBUG: t={0}, intercept={1}, beta={2}, pvalue={3}, annualized rf={4}".format(t,round(intercept,4),round(beta,4),round(pvalue,4),round(rf,4)))

        #计算收益率预期和AR
        for t in ticker_name(ticker,ticker_type):
            try:
                if RF_type in ["value","code"]:
                    #CAPM模型：E(R) = RF + (Rm-RF)*beta
                    RF_text=str(round(RF*100.0,4))[:6]+'%'
                    if not ("%" in ret_type): #注意：RF是年化收益率，此处不是百分比
                        df_ret[t+"_predicted"]=(df_ret[ticker_name(market_index)] - RF/365.0)*beta_dict[t] + RF/365.0  
                    else:
                        df_ret[t+"_predicted"]=(df_ret[ticker_name(market_index)] - RF*100.0/365.0)*beta_dict[t] + RF*100.0/365.0
                        
                else: #RF_type=="model"
                    #市场模型：E(R) = intercept + Rm*beta
                    RF_text="基于市场模型回归"
                    df_ret[t+"_predicted"]=df_ret[ticker_name(market_index)]*beta_dict[t] + intercept_dict[t]
                        
                df_ret[t+"_AR"]=df_ret[t] - df_ret[t+"_predicted"]
            except: continue
            
        if DEBUG2:
            print("  DEBUG: RF_type={0}, RF_text={1}, rf_dict={2}".format(RF_type,RF_text, rf_dict))
        
    #=====计算CAR和BHAR==============================================================
    for t in ticker_name(ticker,ticker_type):
        try:
            df_ret[t+"_CAR"]=0
            df_ret[t+"_BHAR"]=0
        except: continue
        
    event_window_startpd=pd.to_datetime(event_window_start)
    event_window_endpd=pd.to_datetime(event_window_end)
    post_event_endpd=pd.to_datetime(post_event_end)
    startpd=pd.to_datetime(start); endpd=pd.to_datetime(end)
    
    #计算CAR和BHAR
    df_ret_event=df_ret[(df_ret.index >=event_window_startpd) & (df_ret.index <=endpd)]
    for t in ticker_name(ticker,ticker_type):
        try:
            # CAR：单利累加求和（每日异常收益相加）
            df_ret_event[t+'_CAR'] = df_ret_event[t+'_AR'].cumsum(skipna=True)
            # BHAR：复利累积
            df_ret_event[t+'_BHAR'] = ((1+df_ret_event[t+'_AR']/100).cumprod()-1)*100
        except: continue
    
    #合成事件前期间
    df_ret_before_event=df_ret[(df_ret.index >=startpd) & (df_ret.index < event_window_startpd)]
    for t in ticker_name(ticker,ticker_type):
        try:
            df_ret_before_event[t+'_CAR']=np.nan
            df_ret_before_event[t+'_BHAR']=np.nan
        except: continue
    
    df_show=pd.concat([df_ret_before_event,df_ret_event])
    
    #是否显示AR：默认单证券显示，多证券时不显示
    df_show_cols=[]
    for c in list(df_show):
        if show_AR=='auto':
            if len(ticker)==1:
                if 'AR' in c or 'CAR' in c:
                    df_show_cols=df_show_cols+[c]
                    show_AR=True
            else:
                if 'CAR' in c:
                    df_show_cols=df_show_cols+[c]
                    show_AR=False
        elif show_AR==True:
            if 'AR' in c or 'CAR' in c:
                df_show_cols=df_show_cols+[c]
        else: #show_AR==False
            if 'CAR' in c:
                df_show_cols=df_show_cols+[c]
            
    df_show2=df_show[df_show_cols]

    #=====绘图=================================================================
    #设置标签   
    df0=df_show2
    
    y_label="收益率%"
    
    #横轴注释    
    footnote1="首事件日{0}，事件窗口{1}，事件后窗口天数{2}，市场提前反应天数{3}".format(event_date[0],event_window_new,post_event_days,early_response_days)
    footnote2="收益率类型："+ectranslate(ret_type)
    
    if method_type == "market":
        method_name="市场指数基准"
    elif method_type == "random":
        method_name="随机漫步模型"
    else:
        method_name="CAPM模型"
        
    footnote3="，收益率预期方法："+method_name
    if not method_type == "random":
        footnote4='，市场指数：'+ticker_name(market_index)
    else:
        footnote4=''
    
    #显著性检验：异于零的t检验，事件窗口
    df_event_window=df0[(df0.index >=event_window_start) & (df0.index <=event_window_end)]
    #footnote5="事件窗口CAR(终值，p值)："
    footnote5="事件窗口CAR(终值，均值，中位数，p值)："
    for c in list(df_event_window):
        if 'CAR' in c.upper():
            c_name=c[:-4]
            
            event_window_endpd=pd.to_datetime(event_window_end)
            #car_value=df_event_window[df_event_window.index == event_window_endpd][c].values[0]
            car_value=df_event_window[c][-1]
            car_mean=df_event_window[c].mean()
            car_median=df_event_window[c].median()            
            
            if car_value > 0:
                car_value_str=str(round(car_value,4))[:6]
            else:
                car_value_str=str(round(car_value,4))[:7]
            
            if car_mean > 0:
                car_mean_str=str(round(car_mean,4))[:6]
            else:
                car_mean_str=str(round(car_mean,4))[:7]
            
            if car_median > 0:
                car_median_str=str(round(car_median,4))[:6]
            else:
                car_median_str=str(round(car_median,4))[:7]
            
            if len(df_event_window[c])==1:
                if  abs(df_event_window[c].values[0]) > 0.01:
                    p_value=0.0
                else:
                    p_value=1.0
            else:
                p_value=ttest(df_event_window[c],0)
            if p_value > 0:
                p_value_str=str(round(p_value,4))[:6]
            else:
                p_value_str=str(round(p_value,4))[:7]
            #footnote5=footnote5+c_name+p_value_str+"，"
            #footnote5=footnote5+"{0}({1}, {2}), ".format(c_name,car_value_str,p_value_str)
            footnote5=footnote5+"{0}({1}, {2}, {3}, {4}), ".format(c_name,car_value_str,car_mean_str, \
                                                              car_median_str,p_value_str)
            
        if 'BHAR' in c.upper():
            bhar_value=df_event_window[c][-1]
            if bhar_value > 0:
                bhar_value_str=str(round(bhar_value,4))[:6]
            else:
                bhar_value_str=str(round(bhar_value,4))[:7]
                
            if show_BHAR:
                footnote5=footnote5+"BHAR终值: {0}; ".format(bhar_value_str)
            
    footnote5=footnote5.strip(", "); footnote5=footnote5.strip("; ")

    #显著性检验：异于零的t检验，事件后窗口
    df_post_event_window=df0[(df0.index >event_window_end) & (df0.index <=post_event_end)]
    if len(df_post_event_window) == 0:
        footnote6=''
    elif len(df_post_event_window) == 0:
        footnote6=''
    else:
        #footnote6="事件后窗口CAR(终值，p值)："
        footnote6="事件后窗口CAR(终值，均值，中位数，p值)："
        for c in list(df_post_event_window):
            if 'CAR' in c.upper():
                c_name=c[:-4]
                post_event_endpd=pd.to_datetime(post_event_end)
                if DEBUG2:
                    print("  DEBUG: c={0},post_event_end={1},df_post_event_window={2}".format(c,post_event_end,df_post_event_window))
                #car_value=df_post_event_window[df_post_event_window.index == post_event_endpd][c].values[0]
                car_value=df_post_event_window[c][-1]
                car_mean=df_post_event_window[c].mean()
                car_median=df_post_event_window[c].median()
                
                if car_value > 0:
                    car_value_str=str(round(car_value,4))[:6]
                else:
                    car_value_str=str(round(car_value,4))[:7]
                
                if car_mean > 0:
                    car_mean_str=str(round(car_mean,4))[:6]
                else:
                    car_mean_str=str(round(car_mean,4))[:7]
                
                if car_median > 0:
                    car_median_str=str(round(car_median,4))[:6]
                else:
                    car_median_str=str(round(car_median,4))[:7]
                
                if len(df_post_event_window[c])==1:
                    if  abs(df_post_event_window[c].values[0]) > 0.01:
                        p_value=0.0
                    else:
                        p_value=1.0
                else:
                    p_value=ttest(df_post_event_window[c],0)
                if p_value > 0:
                    p_value_str=str(round(p_value,4))[:6]
                else:
                    p_value_str=str(round(p_value,4))[:7]
                    
                #footnote6=footnote6+c[:-4]+str(p_value)[:6]+"，"
                footnote6=footnote6+"{0}({1}, {2}, {3}, {4}), ".format(c_name,car_value_str,car_mean_str,car_median_str,p_value_str)
                        
            if 'BHAR' in c.upper():
                bhar_value=df_post_event_window[c][-1]
                if bhar_value > 0:
                    bhar_value_str=str(round(bhar_value,4))[:6]
                else:
                    bhar_value_str=str(round(bhar_value,4))[:7]
                    
                if show_BHAR:
                    footnote6=footnote6+"BHAR终值: {0}; ".format(bhar_value_str)

        footnote6=footnote6.strip(", "); footnote6=footnote6.strip("; ")
    
    footnote7="数据来源：Sina/EM/Yahoo/Stooq/SWHY，"+stoday

    #x_label=footnote1+'\n'+footnote2+footnote3+footnote4+'\n'+footnote5+'\n'+footnote6+'\n'+footnote7
    x_label=footnote1+'\n'+footnote2+footnote3+footnote4+'\n'+footnote7

    
    axhline_value=0
    axhline_label="零线"
    title_txt="事件影响分析："
    for t in ticker_name(ticker,ticker_type):
        title_txt=title_txt+t+'，'
    title_txt=title_txt.strip("，")

    #判断最新可获得日期
    last_date=df0.index[-1].strftime("%Y-%m-%d")
    if DEBUG:
        print("  DEBUG: last_date={}".format(last_date))
    if post_event_end > last_date:
        post_event_end = last_date
    
    if event_window_new[0] != event_window_new[1]:
        attention_point_area=[event_window_start,event_window_end]
    else:
        attention_point_area=[event_window_start,post_event_end]
    
    #去掉重复日期项标注且不改变顺序
    event_date_new=[]
    for d in event_date:
        d_new=date_adjust(d,adjust=0)
        event_date_new=event_date_new+[d_new]

    attention_point=[event_eve_date,event_window_start,event_window_end,post_event_end]+event_date_new
    if not show_AR:
        period_days=calculate_days(event_eve_date,post_event_end)
        if DEBUG:
            print("  DEBUG: period_days={}".format(period_days))

        if period_days< 6:
            #绘图时横轴若少于6天会出现时间刻度，易误导需避免
            draw_start_date=date_adjust(event_eve_date,adjust=period_days-6)
            attention_point=[draw_start_date,event_window_start,event_window_end,post_event_end]+event_date_new
    """
    if show_AR:        
        attention_point=[event_eve_date,event_window_start,event_window_end,post_event_end]+event_date_new
    else:
        attention_point=[event_eve_date,event_window_start,event_window_end,post_event_end]+event_date_new
        df0=df0[(df0.index >= start) & (df0.index <=post_event_end)]
    """    
    attention_point.sort(reverse=False)
    attention_point=list({}.fromkeys(attention_point).keys())    
    
    # 是否绘制CAR或BHAR曲线：对于短期窗口，CAR曲线和BHAR曲线很可能基本重合，建议仅绘制其中之一！
    df0draw=df0.copy()
    for c in list(df0draw):
        if not draw_CAR and 'CAR' in c:
            del df0draw[c]
        if not draw_BHAR and 'BHAR' in c:
            del df0draw[c]
    
    #绘图
    draw_lines(df0draw,y_label,x_label,axhline_value,axhline_label,title_txt, \
               data_label=False, \
               loc=loc,resample_freq='D',smooth=False, \
               annotate=True,annotate_value=False, \
               attention_point=attention_point, \
               attention_point_area=attention_point_area, \
               ticker_type=ticker_type,facecolor=facecolor)
    
    #=====输出AR和/或CAR或BHAR表格====================================================
    df1=df0.copy()
    #df1=df1.replace([np.nan, None], np.nan).dropna()
    df1=df1.replace([np.nan, None],'-')
    df1["日期"]=df1.index
    df1["日期"]=df1["日期"].apply(lambda x: x.strftime("%Y-%m-%d"))

    df1=df1[(df1["日期"] >= event_date[0]) & (df1["日期"] <= post_event_end)]
    df1["星期"]=df1["日期"].apply(lambda x: week_day(x)+1)
    
    df1["事件标记"]=''
    for d in event_date_new:
        if len(event_date_new)==1:
            event_text="事件日"
        else:
            pos=event_date_new.index(d)
            if pos==1:
                event_text="首事件日"
            else:
                event_text="事件日"+str(pos+1)
        df1["事件标记"]=df1.apply(lambda x: event_text if x["日期"]==d else x["事件标记"],axis=1)

    #event_text="，事件窗口开始日"
    event_text="\n事件窗开始"
    df1["事件标记"]=df1.apply(lambda x: x["事件标记"]+event_text if x["日期"]==event_window_start else x["事件标记"],axis=1)
    #event_text="，事件窗口结束日"
    event_text="\n事件窗结束"
    df1["事件标记"]=df1.apply(lambda x: x["事件标记"]+event_text if x["日期"]==event_window_end else x["事件标记"],axis=1)
    
    #event_text="，事件后窗口结束日"
    if post_event_end > event_window_end:
        event_text="\n事件后窗结束"
        df1["事件标记"]=df1.apply(lambda x: x["事件标记"]+event_text if x["日期"]==post_event_end else x["事件标记"],axis=1)
        
    event_text="\n事件窗"
    df1["事件标记"]=df1.apply(lambda x: x["事件标记"]+event_text if (x["日期"] > event_window_start) and (x["日期"] < event_window_end) else x["事件标记"],axis=1)
        
    event_text="\n事件后窗"
    df1["事件标记"]=df1.apply(lambda x: x["事件标记"]+event_text if (x["日期"] > event_window_end) and (x["日期"] < post_event_end) else x["事件标记"],axis=1)

    df1["事件标记"]=df1["事件标记"].apply(lambda x: x.strip('\n'))
    
    #显示表格
    df0_list=list(df0)
    df1_list=["事件标记","日期","星期"]+df0_list
    df1=df1[df1_list]
    #title_txt=title_txt+"，窗口收益率"
    
    if "CAPM" in method.upper():
        footnotex="CAPM回归期间：{0}至{1}，无风险收益率{2}".format(est_window_start,est_window_end,RF_text)
        footnotey="CAPM贝塔系数："
        for k in beta_dict:
            footnotey=footnotey+k+str(round(beta_dict[k],4))[:6]+"，"
        footnotey=footnotey.strip("，")
        
        if show_RF:
            footnotez="无风险收益率均值："
            for r in rf_dict:
                footnotez=footnotez+r+str(round(rf_dict[r]*100.0,4))[:6]+"%, "
                
            footnotez=footnotez.strip(", ")
            footnote=footnote2+footnote3+footnote4+'\n'+footnotex+'\n'+footnotey+'\n'+footnotez+'\n'+footnote5+'\n'+footnote6
        else:
            footnote=footnote2+footnote3+footnote4+'\n'+footnotex+'\n'+footnotey+'\n'+footnote5+'\n'+footnote6
    else:
        footnote=footnote2+footnote3+footnote4+'\n'+footnote5+'\n'+footnote6
    
    for c in list(df1):
        if not show_BHAR and 'BHAR' in c:
            del df1[c]

    #显示结果表格
    df_display_CSS(df1,titletxt=title_txt,footnote=footnote,facecolor=facecolor,decimals=4, \
                   first_col_align='left',second_col_align='left', \
                   last_col_align='center',other_col_align='center')


    return df_show2
    
    
    
    
    
    
    
    
    
    
    
    
    