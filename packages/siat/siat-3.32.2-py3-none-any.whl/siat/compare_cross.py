# -*- coding: utf-8 -*-
"""
本模块功能：跨类别对比证券投资产品的业绩指标走势
所属工具包：证券投资分析工具SIAT 
SIAT：Security Investment Analysis Tool
创建日期：2023年4月4日
最新修订日期：2023年4月5日
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
#==============================================================================
from siat.common import *
from siat.translate import *
from siat.security_prices import *
from siat.security_price2 import *
from siat.transaction import *
from siat.risk_adjusted_return import *
from siat.sector_china import *
from siat.grafix import *

import pandas as pd
#==============================================================================

#==============================================================================
if __name__=='__main__':
    ticker='600519.SS'
    start='2023-1-1'
    end='2023-4-4'
    info_types=['Close','Volume']
    
    df1=fetch_price_stock(ticker,start,end)
    
def fetch_price_stock(ticker,start,end,info_types=['Close','Volume'], \
                      adjust=-2*365,ticker_type='auto'):
    """
    功能：获取股票、大盘指数、ETF和REITS的价格
    ticker：股票代码
    start,end：日期期间
    info_types：信息测度，默认['Close']，还可以为['Close','Open','High','Low',
                                     'Volume','Adj Close']
    特点：为compare_indicator使用，包括股票名称
    """
    start1=date_adjust(start,adjust=adjust)
    try:
        prices=get_prices(ticker,start1,end)
    except:
        print("  #Error(fetch_price_stock): failed to fetch stock prices for",ticker)
        return None

    if prices is None:
        print("  #Warning(fetch_price_stock): no info found for",ticker,"during",start,"and",end)
        return None

    if len(prices)==0:
        print("  #Warning(fetch_price_stock): zero record found for",ticker,"during",start,"and",end)
        return None
    
    if isinstance(info_types,str):
        typelist=[info_types]
    else:
        typelist=info_types

    import pandas as pd
    df=pd.DataFrame()
        
    for t in typelist:
        try:
            df[t]=prices[t]
        except:
            continue

    df['Adj Close']=df['Close']        
    df['Code']=ticker
    df['Type']='stock'
    
    #预处理ticker_type
    ticker_type=ticker_type_preprocess_mticker_mixed(ticker,ticker_type)    
    df['Name']=ticker_name(ticker,ticker_type)
    
    return df
     

#==============================================================================
if __name__=='__main__':
    Market={'Market':('China','000300.SS','白酒组合1号')}
    Stocks1={'600519.SS':.5,'000858.SZ':.3}
    Stocks2={'000596.SZ':.1,'000568.SZ':.1}
    portfolio=dict(Market,**Stocks1,**Stocks2)
    
    start='2023-1-1'
    end='2023-4-4'
    info_types=['Close','Volume']
    
    df2=fetch_price_stock_portfolio(portfolio,start,end)

def fetch_price_stock_portfolio(portfolio,start,end,info_types=['Close','Volume'],adjust=-2*365):
    """
    功能：获取股票投资组合的信息
    portfolio：股票投资组合
    start,end：日期期间
    info_types：信息测度，默认['Close']，还可以为['Close','Open','High','Low',
                                     'Volume','Adj Close']
    特点：为compare_indicator使用，包括投资组合名称
    """
    start1=date_adjust(start,adjust=adjust)
    try:
        prices=get_portfolio_prices(portfolio,start1,end)
    except:
        print("  #Error(fetch_price_stock_portfolio): failed to fetch stock prices for the portfolio")
        return None

    if prices is None:
        print("  #Warning(fetch_price_stock_portfolio): no info found for the portfolio during",start,"and",end)
        return None

    if len(prices)==0:
        print("  #Warning(fetch_price_stock_portfolio): zero record found for the portfolio during",start,"and",end)
        return None
    
    if isinstance(info_types,str):
        typelist=[info_types]
    else:
        typelist=info_types

    import pandas as pd
    df=pd.DataFrame()
        
    for t in typelist:
        try:
            df[t]=prices[t]
        except:
            continue

    df['Adj Close']=df['Close']        
        
    df['Code']='stock_portfolio'
    df['Type']='stock_portfolio'
    df['Name']=portfolio_name(portfolio)
    
    return df


#==============================================================================
if __name__=='__main__':
    dflist=[df1,df2,df3]
    
    measure='Weekly Ret%'
    start='2023-1-1'
    end='2023-4-4'
    graph=True

def compare_msecurity_cross(dflist,measure,start,end,graph=True, \
                            loc='best',annotate=False):
    """
    功能：基于多个数据表df中的列Close计算指标measure，绘图比较
    输入要求：各个数据表df需要，索引为datetime，Close，Code，Type和Name
    """
    #检查日期期间
    result,startpd,endpd=check_period(start,end)
    if not result:
        print("  #Error(compare_msecurity_cross): invalid date period from",start,'to',end)
        if graph: return      
        else: return None
    
    #检查是否支持该measure
    measurelist=['Close','Adj Close','Daily Ret','Daily Ret%','Daily Adj Ret','Daily Adj Ret%',
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
             'Exp Ret LPSD%', 'Exp Adj Ret LPSD', 'Exp Adj Ret LPSD%']
    if measure not in measurelist:
        print("  #Error(compare_msecurity_cross): unsupported measurement",measure)
        print("  Supported measurements:",measurelist)
        if graph: return      
        else: return None   
    
    print("  Calculating measurement, please wait ......")
    
    import pandas as pd
    dfg=pd.DataFrame()
    
    for dfi in dflist:
        
        if 'Exp' in measure:
            dfi=dfi[(dfi.index >= startpd) & (dfi.index <= endpd)]
        
        dfic=calc_indicators(dfi,measure)
        dfic2=dfic[(dfic.index >= startpd) & (dfic.index <= endpd)]
        dfic3=pd.DataFrame(dfic2[measure])
        
        dfic3.columns=[dfi['Name'].values[0]]
        
        if len(dfg)==0:
            dfg=dfic3
        else:
            dfg=pd.merge(dfg,dfic3,how='outer',left_index=True,right_index=True)

    dfg2=dfg[(dfg.index >= startpd) & (dfg.index <= endpd)]

    if graph:
        # 绘制多条线
        title_txt="比较跨品种证券的指标走势"
        y_label=ectranslate(measure)
        
        import datetime
        today = datetime.date.today().strftime("%Y-%m-%d")
        x_label="数据来源：综合新浪/雅虎/stooq/FRED/申万宏源，"+today    
    
        if 'Ret%' in measure:
            axhline_value=0
            axhline_label='收益零线'
        else:
            axhline_value=0
            axhline_label=''
    
        dfg2.dropna(inplace=True)
        draw_lines(dfg2,y_label,x_label,axhline_value,axhline_label,title_txt, \
                   data_label=False,resample_freq='H',smooth=True,linewidth=1.5, \
                   loc=loc,annotate=annotate)        
        
        
    if graph: return      
    else: return dfg2  

#==============================================================================
#==============================================================================

if __name__=='__main__':
    start='2022-1-1'
    end='2022-10-31'
    
    rar_name="sharpe"
    rar_name="alpha"
    RF=False
    window=30
    
    axhline_value=0
    axhline_label=''
    graph=True
    printout=True
    sortby='tpw_mean'
    scope='China'
    
    graph=False

def compare_mrar_cross(dflist,rar_name,start,end, \
                 RF=False,window=252, \
                 axhline_value=0,axhline_label='零线',graph=True,printout=False, \
                 sortby='tpw_mean',scope='China', \
                 loc='best',annotate=False,ticker_type='auto'):
    """
    功能：计算多种证券的rar比率，并绘图对比
    比率：支持夏普比率、特雷诺比率、索替诺比率、阿尔法比率等
    特点：支持跨种类比较，如股票/投资组合/申万行业指数/债券指数等
    
    注意1：当RF=False时可能有bug
    注意2：当股票为非国内A股时，需要定义scope指定区域。这个很不灵活，需要修改：手工指定市场指数和RF
    """    
    #检查日期期间
    result,startpd,endpd=check_period(start,end)
    if not result:
        print("  #Error(compare_mrar_cross): invalid date period from",fromdate,'to',todate)
        if graph: return      
        else: return None
    
    
    #检查rar指标的种类
    rarlist=['treynor','sharpe','sortino','alpha']
    if not (rar_name.lower() in rarlist):
        print("  #Error(compare_mrar_cross): unsupported rar name",rar_name)
        return None
    
    import pandas as pd
    df=pd.DataFrame() 
    print("  *** Starting to calculate rar ratios, please wait ......")
    for dfi in dflist:
        name=dfi['Name'].values[0]
        df_tmp=rar_ratio_rolling_df(dfi,ratio_name=rar_name,RF=RF,window=window,scope=scope)
        if df_tmp is None:
            print("  #Warning(compare_mrar_cross): data not available for",t)
            continue
        else:
            dft=df_tmp[['RAR']]
            dft.rename(columns={'RAR':name},inplace=True)
            
        if len(df)==0:#第一个
            df=dft
        else:
            df=pd.merge(df,dft,how='outer',left_index=True,right_index=True)

    if len(df)==0:
        print("  #Warning(compare_mrar_cross): no data available for the above securities between",start,end)        
        return None
    
    df.fillna(method='ffill')
    df.fillna(method='bfill')
    
    df2=df[(df.index >= startpd) & (df.index <= endpd)]
    
    #绘制多条曲线
    rar_list=['treynor','sortino','sharpe','alpha']
    rar_list_e=['Treynor Ratio','Sortino Ratio','Sharpe Ratio','Jensen alpha']
    rar_list_c=['特雷诺比率','索替诺比率','夏普比率','阿尔法指标']
    
    pos=rar_list.index(rar_name)
    
    import datetime; today = datetime.date.today()
    
    lang=check_language()
    if lang == 'English':
        
        y_label=rar_list_e[pos]
        x_label="Source: sina/stooq, "+str(today)
        title_txt="Compare Multiple Risk-adjusted Return Performance"
    else:
        y_label=rar_list_c[pos]
        x_label="数据来源: 综合新浪/雅虎/stooq/FRED/申万宏源，"+str(today)
        title_txt="比较跨品种证券的风险调整收益指标走势"

    # 是否绘图
    if graph:
        draw_lines(df2,y_label,x_label, \
                   axhline_value=axhline_value,axhline_label=axhline_label, \
                   title_txt=title_txt,data_label=False, \
                   loc=loc,annotate=annotate)
    ds=None
    if printout:
        dfcols=list(df2)
        
        #预处理ticker_type
        ticker_type_list=ticker_type_preprocess_mticker_mixed(dfcols,ticker_type)        
        
        for c in dfcols:
            #ccn=ticker_name(c)+'('+c+')'
            pos=dfcols.index(c)
            tt=ticker_type_list[pos]
            ccn=ticker_name(c,tt)
            df2.rename(columns={c:ccn},inplace=True)
        
        if sortby=='tpw_mean':
            sortby_txt='按推荐标记+近期优先加权平均值降序排列'
        elif sortby=='min':
            sortby_txt='按推荐标记+最小值降序排列'
        elif sortby=='mean':
            sortby_txt='按推荐标记+平均值降序排列'
        elif sortby=='median':
            sortby_txt='按推荐标记+中位数值降序排列'
        else:
            pass
        
        title_txt='*** '+title_txt+'：'+y_label+'，'+sortby_txt
        additional_note="*** 注：列表仅显示有星号标记或特定数量的证券。"
        footnote='比较期间：'+start+'至'+end
        ds=descriptive_statistics(df2,title_txt,additional_note+footnote,decimals=4, \
                               sortby=sortby,recommend_only=False)

    return df2,ds

if __name__=='__main__':
    tickers = ['000858.SZ','600779.SS','000596.SZ','603589.SS','000001.SS']
    df=compare_mrar(tickers,'sharpe','2022-1-1','2022-10-31')
    df=compare_mrar(tickers,'alpha','2022-10-1','2022-10-31')

#==============================================================================
if __name__=='__main__':
    df=df1
    ratio_name='sharpe'
    ratio_name='alpha'
    RF=True
    window=240
    scope='China'
    
def rar_ratio_rolling_df(df,ratio_name='sharpe',RF=True,window=252,scope='China'):
    """
    功能：滚动计算一个证券投资产品经风险调整后的收益率指数
    输入：证券产品价格时间序列，rar名称，滚动窗口宽度(天数)
    输出：风险调整后的收益率指数序列
    
    注意：当RF=False时有bug
    """
    
    #提取开始结束日期
    t0=df.head(1).index.values[0]
    t1=pd.to_datetime(str(t0))
    start=t1.strftime("%Y-%m-%d")
    
    t0=df.tail(1).index.values[0]
    t1=pd.to_datetime(str(t0))
    end=t1.strftime("%Y-%m-%d")    
    
    #第1步：各种准备和检查工作
    #设定错误信息的函数名
    func_name='rar_ratio_rolling_df'
    
    ratio_list=['treynor','sharpe','sortino','alpha']
    if ratio_name not in ratio_list:
        message="  #Error("+func_name+"): "+"unsupported rar ratio type"
        print(message,ratio_name)
        return None   
    
    #第2步：计算投资组合的日收益率序列
    #计算日收益率，表示为百分比
    ret_pf=pd.DataFrame(df['Close'].pct_change())*100.0
    ret_pf=ret_pf.dropna()

    #第3步：获得无风险收益率/市场收益率序列
    #屏蔽函数内print信息输出的类
    import os, sys
    class HiddenPrints:
        def __enter__(self):
            self._original_stdout = sys.stdout
            sys.stdout = open(os.devnull, 'w')

        def __exit__(self, exc_type, exc_val, exc_tb):
            sys.stdout.close()
            sys.stdout = self._original_stdout
    
    rf_df=None
    if RF or ratio_name=='alpha':
        #获得期间的日无风险收益率(抓取的RF为百分比) 
        #print("  Searching for risk-free interest rate ...")
        if scope=='China':
            mktidx='000300.SS'
            with HiddenPrints():
                rf_df=get_mkt_rf_daily_china(mktidx,start,end,rate_period='1Y',rate_type='shibor',RF=RF)
        else:
            rf_df=get_rf(start,end,scope=scope,freq='daily')  
            if rf_df is None:
                message="  #Error("+func_name+"): "+"no data available for rf in"
                print(message,scope,start,end)
                return None,None 
        #rf_df=get_rf(start,end,scope=scope,freq='daily')  
        
    #第4步：合并投资组合日收益率与无风险利率/市场收益率序列
    #合并rf_df与ret_pf
    reg=ret_pf
    if rf_df is None:
        reg['RF']=0
    else:
        reg=pd.merge(reg,rf_df,how='left',left_index=True,right_index=True)
    if len(reg) == 0:
        message="  #Error("+func_name+"): "+"empty data for ratio calculation"
        print(message)
        return None     
    
    #填补缺失的RF
    reg.fillna(axis=0,method='ffill',inplace=True)
    
    reg['Ret-RF']=reg['Close']-reg['RF']
    reg=reg.dropna()
    try:
        reg.drop(columns=['SMB','HML'],inplace=True)
    except: pass
    
    #第5步：滚动计算风险调整后的收益率
    ##########风险调整后的收益率，计算开始##########
    #用于保存rar和ret_rf_mean
    import numpy as np
    datelist=reg.index.to_list()
    calc_func='calc_'+ratio_name+'_ratio'
    
    rars=pd.DataFrame(columns=('Date','RAR','Mean(Ret)')) 
    for i in np.arange(0,len(reg)):
        i1=i+window-1
        if i1 >= len(reg): break
        
        #构造滚动窗口
        windf=reg[reg.index >= datelist[i]]
        windf=windf[windf.index <= datelist[i1]]
        #print(i,datelist[i],i1,datelist[i1],len(windf))
        
        #使用滚动窗口计算
        try:
            rar,ret_mean=eval(calc_func)(windf)
        except:
            print("  #Error(rar_ratio_rolling_df): failed in linear regression by",calc_func,'\b, in',df['Code'].values[0])
            #print("  windf:\n",windf)
            continue
        
        #记录计算结果
        row=pd.Series({'Date':datelist[i1],'RAR':rar,'Mean(Ret)':ret_mean})
        try:
            rars=rars.append(row,ignore_index=True)
        except:
            rars=rars._append(row,ignore_index=True)
    
    rars.set_index(['Date'],inplace=True) 
    ##########风险调整后的收益率，计算结束##########
    
    return rars

#==============================================================================
if __name__=='__main__':
    # 混合对比
    start='2023-1-1'; end='2023-11-18'
    
    # 股票
    ticker1='600519.SS'
    df1=fetch_price_stock(ticker1,start,end)
    
    # 指数
    ticker2='000300.SS'
    df2=fetch_price_stock(ticker2,start,end)
    
    # 投资组合
    Market={'Market':('China','000300.SS','白酒组合1号')}
    Stocks1={'600519.SS':.5,'000858.SZ':.3}
    Stocks2={'000596.SZ':.1,'000568.SZ':.1}
    portfolio=dict(Market,**Stocks1,**Stocks2)
    df3=fetch_price_stock_portfolio(portfolio,start,end)
    
    # 申万行业指数
    swindex='850831'
    df4=fetch_price_swindex(swindex,start,end)
    
    # 合并
    dflist=[df1,df2,df3,df4]
    measure='Exp Ret%'
    dfa=compare_msecurity_cross(dflist,measure,start,end)
    
    dfb=compare_mrar_cross(dflist,rar_name='sharpe',start=start,end=end)
    
    # 测试
    tickers=['600519.SS','000300.SS','850831.SW']
    df=compare_cross(tickers)

def compare_cross(tickers,indicator='Close',start='default',end='default', \
                  scope='China',loc='best',annotate=False):
    """
    功能：跨越证券产品品种比较趋势
    品种：股票，指数，ETF和REIT基金(仅限中国)，交易所债券(仅限中国)，
    股票投资组合，行业指数(仅限申万行业指数)
    指标：基于股价的相关指标，风险调整收益(rar)
    期间：默认近一个月MRM，后续考虑MRQ/MRY/YTD
    """
    
    # 检查日期：截至日期
    import datetime as dt; today=dt.date.today()
    end=end.lower()
    if end in ['default','today']:
        todate=today
    else:
        validdate,todate=check_date2(end)
        if not validdate:
            print("  #Warning(compare_cross): invalid date for",end)
            todate=today

    # 检查日期：开始日期
    start=start.lower()
    if start in ['default','mrm']:  # 默认近一个月
        fromdate=date_adjust(todate,adjust=-31)
    elif start in ['mrq']:  # 近三个月
        fromdate=date_adjust(todate,adjust=-63)   
    elif start in ['mry']:  # 近一年
        fromdate=date_adjust(todate,adjust=-366)   
    elif start in ['lty']:  # 近三年以来
        fromdate=date_adjust(todate,adjust=-366*3)  
    elif start in ['lfy']:  # 近五年以来
        fromdate=date_adjust(todate,adjust=-366*5)          
    elif start in ['ytd']:  # 今年以来
        fromdate=str(today.year)+'-1-1'        
    else:
        validdate,fromdate=check_date2(start)
        if not validdate:
            print("  #Warning(compare_cross): invalid date for",start,"/b, set to MRM")
            fromdate=date_adjust(todate,adjust=-31)    

    # 检查tickers
    if isinstance(tickers,str) or isinstance(tickers,dict):
        tickers=[tickers]
        
    if isinstance(tickers,list) and (len(tickers)==0):
        tickers=['000001.SS','399001.SZ','899050.BJ']
    
    # 基于类型，循环抓取数据
    dflist=[]
    names=locals()
    for t in tickers:
        pos=tickers.index(t)
        if isinstance(t,str):   # 字符串
            t1=t.upper()
            if '.' not in t1:   # 不带后缀，美股
                #exec("dft{}=fetch_price_stock(t1,fromdate,todate)".format(pos))
                names['dft%s'%pos]=fetch_price_stock(t1,fromdate,todate)
            else:
                tlist=t1.split('.')
                if tlist[1] not in ['SW']:
                    names['dft%s'%pos]=fetch_price_stock(t1,fromdate,todate)
                else:   #申万行业指数
                    names['dft%s'%pos]=fetch_price_swindex(tlist[0],fromdate,todate)
        elif isinstance(t,dict):    # 投资组合
            names['dft%s'%pos]=fetch_price_stock_portfolio(t,fromdate,todate)
        else:
            continue
        
        dflist=dflist+[names['dft%s'%pos]]
        
    rarlist=['treynor','sharpe','sortino','alpha']
    if indicator in rarlist:
        indicator=indicator.lower()
        df=compare_mrar_cross(dflist,rar_name=indicator,start=fromdate,end=todate, \
                              scope=scope,loc=loc,annotate=annotate)
    else:
        indicator=indicator.title()    # 字符串每个单词首字母大写
        df=compare_msecurity_cross(dflist,measure=indicator,start=fromdate,end=todate, \
                                   loc=loc,annotate=annotate)
        
    return df
    
#==============================================================================

#==============================================================================
