# -*- coding: utf-8 -*-
"""
本模块功能：提供全球证券信息，应用层，以股票为基础，兼容雅虎财经上的大多数其他证券产品
所属工具包：证券投资分析工具SIAT 
SIAT：Security Investment Analysis Tool
创建日期：2018年6月16日
最新修订日期：2020年8月28日
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

from siat.common import *
from siat.translate import *
from siat.grafix import *
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

import mplfinance as mpf

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

#设置绘图风格：关闭网格虚线
plt.rcParams['axes.grid']=False

#==============================================================================
def reset_plt():
    """
    功能：用于使用完mplfinance可能造成的绘图乱码问题，但不能恢复默认绘图尺寸
    """
    import matplotlib.pyplot as plt
    if czxt in ['win32','win64']:
        plt.rcParams['font.sans-serif'] = ['SimHei']
    if czxt in ['darwin']:
        plt.rcParams['font.sans-serif']=['Arial Unicode MS']
    plt.rcParams['axes.unicode_minus'] = False
    
    #尝试恢复绘图尺寸
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
    plt.rcParams['axes.grid']=False
    #plt.rcParams['grid.color']='steelblue'
    #plt.rcParams['grid.linestyle']='dashed'
    #plt.rcParams['grid.linewidth']=0.5
    #plt.rcParams['axes.facecolor']='whitesmoke'   
    
    return

#==============================================================================
#以下使用新浪/stooq数据源
#==============================================================================

if __name__ =="__main__":
    ticker='AAPL'
    ticker='00700.HK'
    
def get_profile(ticker):
    """
    功能：按照证券代码抓取证券基本信息。
    输入：证券代码ticker。
    返回：证券基本信息，数据框
    注意：经常出现无规律失败，放弃!!!
    """
    #引入插件
    try:
        import yfinance as yf
    except:
        print("  #Error(get_profile): need to install yfinance")
        return None    

    ticker1=ticker
    result,prefix,suffix=split_prefix_suffix(ticker)
    if result & (suffix=='HK'):
        if len(prefix)==5:
            ticker1=ticker[1:]

    #抓取证券信息，结果为字典
    tp=yf.Ticker(ticker1)
    try:
        dic=tp.info
    except:
        print(f"  #Error(get_profile): failed to retrieve info for {ticker}")
        print("  Solution: try get_stock_profile instead")
        return None    

    if dic is None:
        print(f"  #Error(get_profile): none retrieved for {ticker}")
        print("  Solution: upgrade yfinance if already accessible to Yahoo")
        return None    
        
    
    #将字典转换为数据框
    import pandas as pd
    df=pd.DataFrame([dic])
        
    #转换特殊列的内容：10位时间戳-->日期
    cols=list(df)
    import time
    if ('exDividendDate' in cols):
        df['exDividendDate']=int10_to_date(df['exDividendDate'][0])
    if ('lastSplitDate' in cols):
        df['lastSplitDate']=int10_to_date(df['lastSplitDate'][0])
    if ('sharesShortPreviousMonthDate' in cols):
        df['sharesShortPreviousMonthDate']=int10_to_date(df['sharesShortPreviousMonthDate'][0])
    if ('dateShortInterest' in cols):
        df['dateShortInterest']=int10_to_date(df['dateShortInterest'][0])
    if ('mostRecentQuarter' in cols):
        df['mostRecentQuarter']=int10_to_date(df['mostRecentQuarter'][0])
    if ('lastFiscalYearEnd' in cols):
        df['lastFiscalYearEnd']=int10_to_date(df['lastFiscalYearEnd'][0])
    if ('nextFiscalYearEnd' in cols):
        df['nextFiscalYearEnd']=int10_to_date(df['nextFiscalYearEnd'][0])
    
    #转换特殊列的内容：可交易标志
    """
    if df['tradeable'][0]: df['tradeable']="Yes"
    else: df['tradeable']="No"
    """
    
    return df

if __name__ =="__main__":
    ticker='AAPL'
    df=get_profile('AAPL')
#==============================================================================
def print_profile_detail(df,option='basic'):
    """
    功能：按照选项显示证券信息，更多细节。
    输入：证券基本信息df；分段选项option。
    输出：按照选项打印证券信息
    返回：证券信息，数据框
    注意：放弃
    """
    #检查数据框的有效性
    if (df is None) or (len(df)==0):
        print("...Error #1(print_profile), data input invalid!")
        return None         

    options=["basic","financial","market"]
    if not(option in options):
        print("...Error #2(print_profile), 仅支持选项: basic, financial, market")
        return None
    
    #遍历数据框，清洗数据
    cols=list(df)   #取得数据框的列名
    import numpy as np
    for c in cols:
        dfc0=df[c][0]
        #删除空值列
        if dfc0 is None:
            del df[c]; continue
        if dfc0 is np.nan:
            del df[c]; continue        
        #删除空表列
        if isinstance(dfc0,list):
            if len(dfc0)==0: del df[c]; continue
        
        #分类型清洗内容
        if isinstance(dfc0,float): df[c]=round(dfc0,4)
        if isinstance(dfc0,str): df[c]=dfc0.strip()
    newcols=list(df)    #取得清洗后数据框的列名
    
    #需要打印的字段，只要抓取到就打印
    basiccols=['symbol','quoteType','shortName','longName','sector','industry', \
            'fullTimeEmployees','address1','city','state','country','zip', \
            'phone','fax','website','currency','exchange','market']    
    financialcols=['symbol','shortName','currency','dividendRate',
            'trailingAnnualDividendRate','exDividendDate', \
            'dividendYield','trailingAnnualDividendYield', \
            'fiveYearAvgDividendYield','payoutRatio', \
            'lastSplitDate','lastSplitFactor','trailingPE','forwardPE', \
            'trailingEps','forwardEps','profitMargins','earningsQuarterlyGrowth', \
            'pegRatio','priceToSalesTrailing12Months','priceToBook', \
            'enterpriseToRevenue','enterpriseToEbitda','netIncomeToCommon','bookValue', \
            'lastFiscalYearEnd', \
            'mostRecentQuarter','nextFiscalYearEnd']     
    marketcols=['symbol','shortName','currency','beta','tradeable','open', \
                'regularMarketOpen','dayHigh','regularMarketDayHigh', \
                'dayLow','regularMarketLow','previousClose', \
                'regularMarketPreviousClose','regularMarketPrice','ask','bid', \
                'fiftyDayAvergae','twoHundredDayAverage','fiftyTwoWeekHigh', \
                'fiftyTwoWeekLow','52WeekChange','SandP52Change','volume', \
                'regularMarketVolume','averageVolume','averageDailyVolume10Day', \
                'averageVolume10days', \
                'sharesShortPriorMonth','sharesShortPreviousMonthDate', \
                'dateShortInterest','sharesPercentSharesOut', \
                'sharesOutstanding','floatShares','heldPercentInstitutions', \
                'heldPercentInsiders','enterpriseValue','marketCap', \
                'sharesShort','shortRatio','shortPercentOfFloat'] 

    typecn=["公司信息","财务信息","市场信息"]
    typeinfo=typecn[options.index(option)]
    print("\n===",texttranslate("证券快照：")+typeinfo,"===")
    typecols=[basiccols,financialcols,marketcols]
    cols=typecols[options.index(option)]
    
    from pandas.api.types import is_numeric_dtype
    for i in cols:
        if i in newcols:
            cn=ectranslate(i)
            if is_numeric_dtype(df[i][0]):      
                if abs(df[i][0]) >= 0.0001:
                    print(cn+':',format(df[i][0],','))  
            else:
                print(cn+':',df[i][0])

    import datetime as dt; todaydt=dt.date.today()    
    print('\n'+texttranslate("数据来源：雅虎，")+str(todaydt))
    
    return df

if __name__ =="__main__":
    option='basic'
    df=print_profile_detail(df, option='basic')
    df=print_profile_detail(df, option='financial')
    df=print_profile_detail(df, option='market')

#==============================================================================
def print_profile(df,option='basic'):
    """
    功能：按照选项显示证券信息，简化版。
    输入：证券基本信息df；分段选项option。
    输出：按照选项打印证券信息
    返回：证券信息，数据框
    注意：放弃
    """
    #检查数据框的有效性
    if (df is None) or (len(df)==0):
        print("  #Error(print_profile), data set input invalid!")
        return None         

    options=["basic","financial","market"]
    if not(option in options):
        print("  #Error(print_profile), only support types of basic, financial, market")
        return None
    
    #遍历数据框，清洗数据
    cols=list(df)   #取得数据框的列名
    import numpy as np
    for c in cols:
        dfc0=df[c][0]
        #删除空值列
        if dfc0 is None:
            del df[c]; continue
        if dfc0 is np.nan:
            del df[c]; continue        
        #删除空表列
        if isinstance(dfc0,list):
            if len(dfc0)==0: del df[c]; continue
        
        #分类型清洗内容
        if isinstance(dfc0,float): df[c]=round(dfc0,4)
        if isinstance(dfc0,str): df[c]=dfc0.strip()
    newcols=list(df)    #取得清洗后数据框的列名
    
    basiccols=['symbol','quoteType','shortName','sector','industry', \
            'fullTimeEmployees','city','state','country', \
            'website','currency','exchange']    
    financialcols=['symbol','dividendRate',
            'dividendYield', \
            'payoutRatio', \
            'trailingPE','forwardPE', \
            'trailingEps','forwardEps','profitMargins','earningsQuarterlyGrowth', \
            'pegRatio','priceToSalesTrailing12Months','priceToBook', \
            'bookValue', \
            'lastFiscalYearEnd']     
    marketcols=['symbol','beta','open', \
                'dayHigh', \
                'dayLow','previousClose', \
                'fiftyTwoWeekHigh', \
                'fiftyTwoWeekLow','52WeekChange','SandP52Change','volume', \
                'averageDailyVolume10Day', \
                'sharesOutstanding','floatShares','heldPercentInstitutions', \
                'heldPercentInsiders','marketCap'] 

    typecn=["公司信息","财务信息","市场信息"]
    typeinfo=typecn[options.index(option)]
    print("\n===",texttranslate("证券快照TTM：")+typeinfo,"===")
    typecols=[basiccols,financialcols,marketcols]
    cols=typecols[options.index(option)]
    
    from pandas.api.types import is_numeric_dtype
    for i in cols:
        if i in newcols:
            cn=ectranslate(i)
            if is_numeric_dtype(df[i][0]):                    
                print(cn+':',format(df[i][0],','))  
            else:
                print(cn+':',df[i][0])

    import datetime as dt; today=dt.date.today()    
    print(texttranslate("数据来源：Yahoo Finance，")+str(today))
    return df

if __name__ =="__main__":
    option='basic'
    df=print_profile(df, option='basic')
    df=print_profile(df, option='financial')
    df=print_profile(df, option='market')
#==============================================================================
def stock_profile(ticker,option='basic',verbose=False):
    """
    功能：抓取证券快照信息，包括静态公司信息、财务信息和市场信息。
    输入：证券代码ticker；选项verbose表示是否显示详细信息，默认否。
    输出：一次性打印公司信息、财务信息和市场信息。
    返回：证券快照信息数据表。
    注意：放弃
    """
    print("  Searching for security snapshot information, please wait ...")
    #抓取证券静态信息
    try:
        df=get_profile(ticker)
    except:
        print("  #Error(stock_profile), failed to retrieve or decode profile info of",ticker)
        return None        
    
    #检查抓取到的数据表
    if (df is None) or (len(df)==0):
        print("  #Error(stock_profile), retrieved empty profile info of",ticker)
        return None
    
    df=print_profile(df, option='basic')
    #详细版输出信息
    if verbose:
        df=print_profile_detail(df, option='financial')
        df=print_profile_detail(df, option='market')

    return df


#==============================================================================

if __name__ =="__main__":
    #美股
    info=stock_profile("MSFT")
    info=stock_profile("MSFT",option="market")
    info=stock_profile("MSFT",option="financial")
    #大陆股票
    info=stock_profile("000002.SZ")
    info=stock_profile("000002.SZ",option="financial")
    info=stock_profile("000002.SZ",option="market")
    #港股
    info=stock_profile("00700.HK",option="financial")
    info=stock_profile("00700.HK",option="market")
    info=stock_profile("00700.HK",option="basic")
    #印度股票
    info=stock_profile("TCS.NS",option="financial")
    info=stock_profile("TCS.NS",option="market")
    info=stock_profile("TCS.NS",option="basic")
    #德国股票
    info=stock_profile("BMW.DE",option="financial")
    info=stock_profile("BMW.DE",option="market")
    info=stock_profile("BMW.DE",option="basic")
    #日本股票
    info=stock_profile("6758.t",option="financial")
    info=stock_profile("6758.t",option="market")
    info=stock_profile("6758.t",option="basic")
    info=stock_profile("9501.t",option="financial")
    #ETF指数基金
    info=stock_profile("SPY")
    info=stock_profile("SPY",option="market")
    info=stock_profile("SPY",option="financial")
    #债券期货
    info=stock_profile("US=F")
    info=stock_profile("US=F",option="market")
    info=stock_profile("US=F",option="financial") 
    #债券基金
    info=stock_profile("LBNDX",option="basic")
    info=stock_profile("LBNDX",option="market")
    info=stock_profile("LBNDX",option="financial")
    #期货
    info=stock_profile("VXX",option="basic")
    info=stock_profile("VXX",option="market")
    info=stock_profile("VXX",option="financial")    

#==============================================================================
def security_price(ticker,fromdate,todate,adj=False, \
                   datatag=False,power=0,source='auto'):
    """
    功能：绘制证券价格折线图。为维持兼容性，套壳函数stock_price
    """
    df=stock_price(ticker=ticker,fromdate=fromdate,todate=todate, \
                   adj=adj,datatag=datatag,power=power,source=source)
    
    return df

if __name__ =="__main__":
    # 测试获取股价：沪深指数
    df=security_price("000001.SS","2022-11-1","2022-12-15")
    df=security_price("000300.SS","2022-11-1","2022-12-15")
    df=security_price("399001.SZ","2022-11-1","2022-12-15")
    df=security_price("399106.SZ","2022-11-1","2022-12-15")
    
    # 测试获取股价：上交所
    df=security_price("000001.SS","2022-11-1","2022-12-15")
    
    # 测试获取股价：深交所
    df=security_price("000001.SZ","2022-11-1","2022-12-15")
    
    # 测试获取股价：北交所
    df=security_price("430047.BJ","2022-11-1","2022-12-15")
    df=security_price("872925.BJ","2022-11-1","2022-12-15")
    
    # 测试获取股价：港股
    df=security_price("00700.HK","2022-11-1","2022-12-15")
    df=security_price("01810.HK","2022-11-1","2022-12-15")
    
    # 测试获取股价：美股
    df=security_price("JD","2022-11-1","2022-12-15")
    df=security_price("AAPL","2022-11-1","2022-12-15")

#==============================================================================
if __name__ =="__main__":
    ticker="185851.SS"
    fromdate="2023-1-1"
    todate="2023-5-20"


def stock_price(ticker,fromdate,todate,adj=False, \
                datatag=False,power=0,source='auto',facecolor='whitesmoke'):
    """
    功能：绘制证券价格折线图。
    输入：证券代码ticker；开始日期fromdate，结束日期todate；
    是否标注数据标签datatag，默认否；多项式趋势线的阶数，若为0则不绘制趋势线。
    输出：绘制证券价格折线图
    返回：证券价格数据表
    """
    #抓取证券价格
    from siat.security_prices import get_price
    df=get_price(ticker,fromdate,todate,adj=adj,source=source)
    
    if not (df is None):
        tickername=ticker_name(ticker)

        import datetime; today = datetime.date.today()
        lang=check_language()
        if lang == 'English':
            titletxt=texttranslate("Security Price Trend：")+tickername
            footnote=texttranslate("Data source: Sina/EM/Stooq/Yahoo/SWHY, ")+str(today)
        else:
            titletxt=texttranslate("证券价格走势图：")+tickername
            footnote=texttranslate("数据来源：Sina/EM/Stooq/Yahoo/SWHY，")+str(today)
        
        pricetype='Close'
        import pandas as pd
        df1=pd.DataFrame(df[pricetype])
        df1.dropna(inplace=True)
        
        collabel=ectranslate(pricetype)
        ylabeltxt=collabel
        plot_line(df1,pricetype,collabel,ylabeltxt,titletxt,footnote, \
                  datatag=datatag,power=power,facecolor=facecolor)
    
    return df

if __name__ =="__main__":
    priceinfo=stock_price("AAPL","2023-1-1","2023-6-16",power=3)

#==============================================================================
if __name__ =="__main__":
    fromdate='2023-1-1'
    fromdate1=date_adjust(fromdate,adjust=-730)
    pricedf=get_price("AAPL",fromdate1,'2023-6-16')


def ret_calculate(pricedf,fromdate):
    """
    功能：单纯计算各种收益率指标
    """
    #加入日收益率
    from siat.security_prices import calc_daily_return,calc_rolling_return,calc_expanding_return
    drdf=calc_daily_return(pricedf)
    #加入滚动收益率
    prdf1=calc_rolling_return(drdf, "Weekly") 
    prdf2=calc_rolling_return(prdf1, "Monthly")
    prdf3=calc_rolling_return(prdf2, "Quarterly")
    prdf4=calc_rolling_return(prdf3, "Annual") 
    
    #加入扩展收益率
    try:
        erdf=calc_expanding_return(prdf4,fromdate)
    except:
        print("  #Error(ret_calculate): A problem happens while calculating expanding returns based on",fromdate,prdf4)
        return None
        
    return erdf

if __name__ =="__main__":
    pricedf=get_price("AAPL",'2023-1-1','2023-6-16',adj=True)
    allind=all_calculate(pricedf,"AAPL",'2023-1-1','2023-6-16')
    list(allind)
    
def all_calculate(pricedf,ticker1,fromdate,todate,ticker_type='auto'):
    """
    功能：单纯计算所有基于证券价格的指标
    
    注意：对于滚动指标，起始日期需要提前至少一年以上
    """
    
    #计算其各种期间的收益率
    try:
        df1a=ret_calculate(pricedf,fromdate)
    except:
        print("  #Error(all_calculate): A problem occurs for calculating returns of",ticker1)
        return None
    if df1a is None:
        print("  #Warning(all_calculate): insufficient data for",ticker1,'\b, ignored.')
        return None
    
    #加入价格波动指标
    #df1b=price_volatility2(df1a,ticker1,fromdate,todate,graph=False)
    df1b=price_volatility2(pricedf,ticker1,fromdate,todate,graph=False,ticker_type=ticker_type)

    #加入收益率波动指标
    df1c=ret_volatility2(pricedf,ticker1,fromdate,todate,graph=False,ticker_type=ticker_type)

    #加入收益率下偏标准差指标
    df1d=ret_lpsd2(pricedf,ticker1,fromdate,todate,graph=False,ticker_type=ticker_type)
    
    # 横向拼接合并
    result=pd.concat([df1a,df1b,df1c,df1d],axis=1,join='outer')
    # 合并后产生的重复字段仅保留第一次出现的
    result3 = result.loc[:, ~result.columns.duplicated(keep='first')]

    
    # 去掉重复的列，但要避免仅仅因为数值相同而去掉有用的列，比如误删'Close'列
    """
    result1=result.T
    result1['item']=result1.index #在行中增加临时列名，避免误删
    result2=result1.drop_duplicates(subset=None,keep='first',ignore_index=False)
    result2.drop("item", axis=1, inplace=True) #去掉临时列名
    result3=result2.T
    """
    
    return result3


if __name__ =="__main__":
    # 测试组1
    ticker='NVDA'
    indicator="Exp Ret%"
    indicator="Annual Ret Volatility%"
    
    # 测试组2
    ticker='GCZ25.CMX'
    fromdate='2020-1-1'
    todate='2020-6-30'
    indicator="Close"
    
    # 测试组3
    ticker='GEM24.CME'
    fromdate='2023-7-1'
    todate='2023-9-17'
    indicator="Close"
    
    # 公共参数
    datatag=False
    power=0
    graph=True
    source='auto'
    zeroline=False
    average_value=False
    
    # 其他测试
    ticker='600519.SS'; indicator='Exp Ret Volatility%'
    
    ticker='180202.SZ'
    ticker_type='fund'
    
    fromdate='2024-1-1'; todate='2024-5-25'
    
    # 测试组4
    ticker='AAPL'
    indicator='Adj Close'
    fromdate='2024-5-1'; todate='2024-5-20'
    adjust=''
    zeroline=False; average_value=False; datatag=False; power=0; graph=True
    source='auto'
    mark_top=True; mark_bottom=True; mark_end=True
    ticker_type='auto'
    facecolor='whitesmoke'
    
    # 测试组5
    ticker='851242.SW'
    ticker='807110.SW'
    indicator='Close'
    fromdate='2024-5-1'; todate='2024-5-20'
    adjust=''
    zeroline=False; average_value=False; datatag=False; power=0; graph=True
    source='auto'
    mark_top=True; mark_bottom=True; mark_end=True
    ticker_type='auto'
    facecolor='whitesmoke'    
    
    # 测试组6
    ticker='XAUUSD'
    indicator='Close'
    fromdate='2024-5-1'; todate='2024-5-20'
    
    # 测试组7
    ticker='BMW.DE'
    indicator='Close'
    fromdate='2025-6-1'; todate='2025-6-15'
    
    # 测试组8
    ticker='GEM25.CME'
    indicator='Close'
    fromdate='2025-1-1'; todate='2025-6-15'
    
    # 测试组9
    ticker='JD'
    indicator='Exp Ret%'
    fromdate='2025-4-1'; todate='2025-6-30'
    
    zeroline=False; adjust=''
    attention_value='';attention_value_area=''
    attention_point='';attention_point_area=''
    average_value=False
    datatag=False;power=0;graph=True;source='auto'
    mark_top=True;mark_bottom=True;mark_end=True
    ticker_type='auto';facecolor='whitesmoke';loc='best'
   
    
    df=security_indicator(ticker,indicator,fromdate,todate,ticker_type=ticker_type)

def security_indicator(ticker,indicator='Close', \
                       fromdate='MRM',todate='today',adjust='', \
                       zeroline=False, \
                           attention_value='',attention_value_area='', \
                           attention_point='',attention_point_area='', \
                       average_value=False, \
                       datatag=False,power=0,graph=True,source='auto', \
                       mark_top=True,mark_bottom=True, \
                       mark_start=True,mark_end=True, \
                       ticker_type='auto',facecolor='whitesmoke',loc='best'):
    """
    功能：单只证券的全部指标
    """
    fromdate,todate=start_end_preprocess(fromdate,todate)
    
    #判断复权价
    adjust_list=['','qfq','hfq']
    if adjust not in adjust_list:
        print("  #Warning(security_indicator): invalid adjust",adjust)
        print("  Supported adjust:",adjust_list)
        adjust='qfq'

    if ('Adj' not in indicator):
        adjust=''            
    if ('Adj' in indicator) and (adjust == ''):
        adjust='qfq'
    
    fromdate1=date_adjust(fromdate,adjust=-365*3)
    
    from siat.security_price2 import get_price_1ticker_mixed
    #pricedf=get_prices_all(ticker,fromdate1,todate,source=source,ticker_type=ticker_type)
    pricedf,found=get_price_1ticker_mixed(ticker=ticker, \
                                          fromdate=fromdate1,todate=todate, \
                                          adjust=adjust, \
                                          source=source,ticker_type=ticker_type)
    if pricedf is None:
        print("  #Error(security_indicator): security info not found for",ticker)
        return None
    if len(pricedf) == 0:
        print("  #Error(security_indicator): zero record found for",ticker)
        return None

    #奇怪错误：仅仅抓取到1个记录，应对办法：改变开始时间，貌似仅存在于REIT基金
    if len(pricedf)==1:
        fromdate1=date_adjust(fromdate,adjust=-365*2)
        pricedf,found=get_price_1ticker_mixed(ticker=ticker,fromdate=fromdate1, \
                                              adjust=adjust, \
                                              todate=todate,source=source,ticker_type=ticker_type)
        if len(pricedf)==1:
            fromdate1=date_adjust(fromdate,adjust=-365*1)
            pricedf,found=get_price_1ticker_mixed(ticker=ticker,fromdate=fromdate1, \
                                                  adjust=adjust, \
                                                  todate=todate,source=source,ticker_type=ticker_type)        
            if len(pricedf)==1:
                fromdate1=fromdate
                pricedf,found=get_price_1ticker_mixed(ticker=ticker,fromdate=fromdate1, \
                                                      adjust=adjust, \
                                                      todate=todate,source=source,ticker_type=ticker_type)           

    if not found == "Found":
        print("  #Error(security_indicator): no security info found for",ticker)
        return None
        
    # 去掉时区信息，避免日期时区冲突问题
    pricedf=df_index_timezone_remove(pricedf)
    """
    import pandas as pd
    pricedf.index = pd.to_datetime(pricedf.index)
    pricedf.index = pricedf.index.tz_localize(None)
    """
    # 检查是否存在满足给定日期的记录
    fromdate_pd=pd.to_datetime(fromdate)
    tmp_df=pricedf[pricedf.index >= fromdate_pd]
    if len(tmp_df)==0:
        print("  #Warning(security_indicator): zero record exists from",fromdate,"for",ticker)
        return None
    
    erdf=all_calculate(pricedf,ticker,fromdate,todate)
    erdf2=erdf[erdf.index >= fromdate_pd]
    
    # 若indicator为Exp Ret%类指标，此处需要首行置零
    colList=list(erdf2)
    index1=erdf2.head(1).index.values[0]
    for c in colList:
        #if 'Exp Ret%' in c:
        if c == 'Exp Ret%':
            erdf2.loc[erdf2[erdf2.index==index1].index.tolist(),c]=0
    
    #erdf3=pd.DataFrame(erdf2[indicator])
    erdf3=erdf2

    # 绘图
    if not graph:
        return erdf3
    
    #titletxt=texttranslate("证券指标运动趋势：")+ticker_name(ticker)
    titletxt1=text_lang("证券趋势分析：","Security Trend: ")
    titletxt=titletxt1+ticker_name(ticker,ticker_type=ticker_type)
    import datetime; todaydt = datetime.date.today()
    sourcetxt=text_lang("数据来源：Sina/EM/Stooq/Yahoo/SWHY，","Data source: Sina/EM/Stooq/Yahoo/SWHY, ")
    footnote=sourcetxt+str(todaydt)
    collabel=ectranslate(indicator)
    
    ylabeltxt=ectranslate(indicator)
    try:
        tickersplit=ticker.split('.')
        if (len(tickersplit) > 1) and (indicator == 'Close'):
            if tickersplit[1].upper() in ['M','B']:
                ylabeltxt="stooq_MB" #特殊标志，告知绘图函数不显示某些标记
    except: pass
    
    ind_max=erdf3[indicator].max(); ind_min=erdf3[indicator].min()
    if ind_max * ind_min <0:
    #if 'Ret%' in indicator:
        zeroline=True
    
    plot_line(erdf3,indicator,collabel,ylabeltxt,titletxt,footnote,datatag=datatag, \
              power=power,zeroline=zeroline, \
              average_value=average_value, \
                  attention_value=attention_value,attention_value_area=attention_value_area, \
                  attention_point=attention_point,attention_point_area=attention_point_area, \
              mark_top=mark_top,mark_bottom=mark_bottom, \
              mark_start=mark_start,mark_end=mark_end, \
              facecolor=facecolor,loc=loc)
    
    return erdf3
    
    
def stock_ret(ticker,fromdate,todate, \
              adjust='', \
              rtype="Daily Ret%", \
              datatag=False,power=0,graph=True,source='auto',ticker_type='auto'):
    """
    功能：绘制证券收益率折线图，单个证券，单个指标。
    输入：证券代码ticker；开始日期fromdate，结束日期todate；收益率类型type；
    是否标注数据标签datatag，默认否；多项式趋势线的阶数，若为0则不绘制趋势线。
    输出：绘制证券价格折线图
    返回：证券价格数据表
    """
    #调整抓取样本的开始日期366*2=732，以便保证有足够的样本供后续计算
    fromdate1=date_adjust(fromdate, -732)

    #判断复权价
    adjust_list=['','qfq','hfq']
    if adjust not in adjust_list:
        print("  #Warning(stock_ret): invalid adjust",adjust)
        print("  Supported adjust:",adjust_list)
        adjust='qfq'    
    if 'Adj' in rtype: adjust='qfq'
    
    #抓取证券价格
    from siat.security_price2 import get_price_1ticker_mixed
    #pricedf=get_price(ticker,fromdate1,todate,adj=adj,source=source)
    pricedf,found=get_price_1ticker_mixed(ticker=ticker,fromdate=fromdate1, \
                                    todate=todate,adjust=adjust, \
                                    source=source,ticker_type=ticker_type)
    if pricedf is None:
        print("  #Error(stock_ret): failed to find price info for",ticker,fromdate,todate)
        return None
    pricedfcols=list(pricedf)    
    
    #加入日收益率
    from siat.security_prices import calc_daily_return
    drdf=calc_daily_return(pricedf)
    #加入滚动收益率
    prdf1=calc_rolling_return(drdf, "Weekly") 
    prdf2=calc_rolling_return(prdf1, "Monthly")
    prdf3=calc_rolling_return(prdf2, "Quarterly")
    prdf4=calc_rolling_return(prdf3, "Annual") 
    
    #加入扩展收益率：从fromdate开始而不是fromdate1
    erdf=calc_expanding_return(prdf4,fromdate)
    
    #如果不绘图则直接返回数据表
    if not graph: return erdf    
    
    #获得支持的收益率类型列名
    colnames=list(erdf)
    for c in pricedfcols:
        colnames.remove(c)
    
    #检查type是否在支持的收益率列名中
    if not (rtype in colnames):
        print("  #Error(stock_ret)：only support return types of",colnames)
        return        

    import datetime; todaydt = datetime.date.today()
    footnote=text_lang("数据来源：Sina/EM/Stooq/Yahoo/SWHY，","Data source: Sina/EM/Stooq/Yahoo/SWHY, ")+str(todaydt)
    collabel=ectranslate(rtype)
    ylabeltxt=ectranslate(rtype)
    titletxt=text_lang("证券趋势分析：","Security Trend: ")+ticker_name(ticker,ticker_type=ticker_type)+text_lang("，收益率",", Rate of Return")

    pltdf=erdf[erdf.index >= fromdate]
    plot_line(pltdf,rtype,collabel,ylabeltxt,titletxt,footnote,datatag=datatag, \
              power=power,zeroline=True)
    
    return erdf

if __name__ =="__main__":
    ticker="000002.SZ"
    fromdate="2020-1-1"
    todate="2020-3-16"
    type="Daily Ret%"
    datatag=False
    power=3
    retinfo=stock_ret("000002.SZ","2020-1-1","2020-3-16",power=3)
    retinfo=stock_ret("000002.SZ","2020-1-1","2020-3-16","Daily Adj Ret%",power=3)
    retinfo=stock_ret("000002.SZ","2020-1-1","2020-3-16","Weekly Ret%",power=3)
    retinfo=stock_ret("000002.SZ","2020-1-1","2020-3-16","Monthly Ret%",power=4)
    retinfo=stock_ret("000002.SZ","2020-1-1","2020-3-16","Quarterly Ret%",power=4)
    retinfo=stock_ret("000002.SZ","2019-1-1","2020-3-16","Annual Ret%",power=4)
    retinfo=stock_ret("000002.SZ","2019-1-1","2020-3-16","Cum Ret%",power=4)

#==============================================================
if __name__ =="__main__":
    ticker='600519.SS'
    ticker='OR.PA'
    measures=['Monthly Ret%','Quarterly Ret%','Annual Ret%','XYZ']
    
    ticker='NVDA'
    measures=['Close','Adj Close']
    
    fromdate='2024-5-20'
    todate='2024-6-20'
    adjust=''
    band_area=''
    graph=True
    smooth=True
    loc='best'
    facecolor='whitesmoke'
    date_range=False
    date_freq=False
    annotate=False
    annotate_value=False
    source='auto'
    mark_top=True; mark_bottom=True; mark_end=True
    ticker_type='auto'
    
    df=security_mindicators(ticker,measures,fromdate,todate)

def security_mindicators(ticker,measures,
                         fromdate,todate, \
                            attention_value='',attention_value_area='', \
                            attention_point='',attention_point_area='', \
                         adjust='', \
                         band_area='', \
                         graph=True,smooth=True,loc='best',facecolor='whitesmoke', \
                         date_range=False,date_freq=False, \
                         annotate=False,annotate_value=False, \
                         source='auto', \
                         mark_top=True,mark_bottom=True, \
                         mark_start=True,mark_end=True, \
                         ticker_type='auto'):
    """
    功能：单个证券，多个指标对比
    date_range=False：指定开始结束日期绘图
    date_freq=False：指定横轴日期间隔，例如'D'、'2D'、'W'、'M'等，横轴一般不超过25个标注，否则会重叠
    注意：
    annotate：这里仅为预留，暂时未作处理
    smooth：样本数目超过一定数量就默认忽略
    """
    DEBUG=False
    
    # 提前开始日期
    #fromdate1=date_adjust(fromdate,adjust=-365*3)
    
    #处理ticker，允许1个
    if isinstance(ticker,list):
        if len(ticker) >= 1:
            ticker=ticker[0]
        else:
            print("  #Error(security_mindicators): need a ticker for proceed")
            return None

    #处理measures，允许多个
    if isinstance(measures,str):
        measures=[measures]

    #屏蔽函数内print信息输出的类
    import os, sys
    class HiddenPrints:
        def __enter__(self):
            self._original_stdout = sys.stdout
            sys.stdout = open(os.devnull, 'w')

        def __exit__(self, exc_type, exc_val, exc_tb):
            sys.stdout.close()
            sys.stdout = self._original_stdout

    df=pd.DataFrame()
    for m in measures:
        print("  Searching",ticker,"for",m,"info ... ...")
        #复权价判断
        adjustm=adjust
        if ('Adj' in m) and (adjust ==''):
            adjustm='qfq'

        with HiddenPrints():
            #security_indicator未能做到同时获得Close和Adj Close
            dftmp=security_indicator(ticker=ticker,indicator=m,adjust=adjustm, \
                                  fromdate=fromdate,todate=todate, \
                                  source=source, \
                                  ticker_type=ticker_type, \
                                  graph=False)
        if dftmp is None:
            print("  #Error(security_mindicators): info not found for",ticker)
            return None
        if len(dftmp) ==0:
            print("  #Error(security_mindicators): empty record found for",ticker)
            return None            

        try:            
            dftmp1= dftmp[[m]]
        except:
            print("  #Error(security_mindicators): unsupported measure for",m)
            return None            
            
        if len(df)==0:
            df=dftmp1
        else:
            df=pd.merge(df,dftmp1,left_index=True,right_index=True)

    df['ticker']=ticker

    if graph:
        # 翻译指标名称
        for c in list(df):
            df.rename(columns={c:ectranslate(c)},inplace=True)
    
        y_label=text_lang('证券指标',"Indicator")
        import datetime; todaydt = datetime.date.today()
        x_label=text_lang("数据来源：Sina/EM/Stooq/Yahoo/SWHY，","Data source: Sina/EM/Stooq/Yahoo/SWHY, ")+str(todaydt)
    
        axhline_value=0; axhline_label=''
        above_zero=0; below_zero=0
        for c in list(df):
            c_max=df[c].max(); c_min=df[c].min()
            try:
                if c_max>0 or c_min>0: above_zero+=1
                if c_max<0 or c_min<0: below_zero+=1                
            except: continue
            
        if above_zero>0 and below_zero>0: #有正有负
            if DEBUG:
                print("DEBUG: draw axhline=0")
        #if 'Ret%' in c:
            axhline_value=0
            axhline_label='零线'
            
        titletxt=text_lang("证券趋势分析：","Security Trend: ")+ticker_name(ticker,ticker_type=ticker_type)       
        
        draw_lines2(df,y_label,x_label,axhline_value,axhline_label,titletxt, \
                   data_label=False,resample_freq='1D',smooth=smooth, \
                   date_range=date_range,date_freq=date_freq,date_fmt='%Y-%m-%d', \
                        attention_value=attention_value,attention_value_area=attention_value_area, \
                        attention_point=attention_point,attention_point_area=attention_point_area, \
                   annotate=annotate,annotate_value=annotate_value, \
                   mark_top=mark_top,mark_bottom=mark_bottom, \
                   mark_start=mark_start,mark_end=mark_end, \
                       facecolor=facecolor, \
                   band_area=band_area,loc=loc)

    return df

#==============================================================================
def stock_price_volatility(ticker,fromdate,todate,type="Weekly Price Volatility", \
                           datatag=False,power=0,graph=True):
    """
    功能：绘制证券价格波动风险折线图。
    输入：证券代码ticker；开始日期fromdate，结束日期todate；期间类型type；
    是否标注数据标签datatag，默认否；多项式趋势线的阶数，若为0则不绘制趋势线。
    输出：绘制证券价格波动折线图
    返回：证券价格数据表
    """
    #调整抓取样本的开始日期，以便保证有足够的样本供后续计算
    fromdate1=date_adjust(fromdate, -400)

    #抓取证券价格
    adj=False
    if 'Adj' in type: adj=True
    from siat.security_prices import get_price
    pricedf=get_price(ticker,fromdate1,todate,adj=adj)
    if pricedf is None:
        print("  #Error(stock_price_volatility)：failed to find price info for",ticker,fromdate,todate)
        return
    pricedfcols=list(pricedf)    
    
    #加入滚动价格波动风险
    prdf1=rolling_price_volatility(pricedf, "Weekly") 
    prdf2=rolling_price_volatility(prdf1, "Monthly")
    prdf3=rolling_price_volatility(prdf2, "Quarterly")
    prdf4=rolling_price_volatility(prdf3, "Annual") 
    
    #加入累计价格波动风险
    erdf=expanding_price_volatility(prdf4,fromdate)
    
    #如果不绘图则直接返回数据表
    if not graph: return erdf    
    
    #获得支持的价格波动风险类型列名，去掉不需要的列名
    colnames=list(erdf)
    for c in pricedfcols:
        colnames.remove(c)
    
    #检查type是否在支持的收益率列名中
    if not (type in colnames):
        print("  #Error(stock_price_volatility)：only support price risk types of",colnames)
        return        

    titletxt=texttranslate("证券价格波动风险走势图：")+ticker_name(ticker)
    import datetime; today = datetime.date.today()
    footnote=texttranslate("数据来源：Sina/EM/Stooq/Yahoo/SWHY，")+str(today)
    collabel=ectranslate(type)
    ylabeltxt=ectranslate(type)
    pltdf=erdf[erdf.index >= fromdate]
    plot_line(pltdf,type,collabel,ylabeltxt,titletxt,footnote,datatag=datatag, \
              power=power,zeroline=True)
    
    return erdf

if __name__ =="__main__":
    ticker="000002.SZ"
    fromdate="2020-1-1"
    todate="2020-3-16"
    type="Daily Ret%"
    datatag=False
    power=3

    pv=stock_price_volatility("000002.SZ","2019-1-1","2020-3-16","Annual Price Volatility")
    pv=stock_price_volatility("000002.SZ","2019-1-1","2020-3-16","Annual Exp Price Volatility")

#==============================================================================
def price_volatility2(pricedf,ticker,fromdate,todate, \
                      type="Weekly Price Volatility",datatag=False, \
                      power=4,graph=True,ticker_type='auto'):
    """
    功能：绘制证券价格波动风险折线图。与函数price_volatility的唯一区别是不抓取股价。
    输入：股价数据集pricedf；证券代码ticker；开始日期fromdate，结束日期todate；期间类型type；
    是否标注数据标签datatag，默认否；多项式趋势线的阶数，若为0则不绘制趋势线。
    输出：绘制证券价格波动折线图
    返回：证券价格数据表
    """
    pricedfcols=list(pricedf)
    #加入滚动价格波动风险
    from siat.security_prices import rolling_price_volatility,expanding_price_volatility
    prdf1=rolling_price_volatility(pricedf, "Weekly") 
    prdf2=rolling_price_volatility(prdf1, "Monthly")
    prdf3=rolling_price_volatility(prdf2, "Quarterly")
    prdf4=rolling_price_volatility(prdf3, "Annual") 
    
    #加入累计价格波动风险
    erdf=expanding_price_volatility(prdf4,fromdate)
    
    #如果不绘图则直接返回数据表
    if not graph: return erdf    
    
    #获得支持的价格波动风险类型列名，去掉不需要的列名
    colnames=list(erdf)
    for c in pricedfcols:
        colnames.remove(c)
    
    #检查type是否在支持的收益率列名中
    if not (type in colnames):
        print("  #Error(price_volatility2)：only support price risk types of",colnames)
        return        

    titletxt=text_lang("证券趋势分析：","Security Trend: ")+ticker_name(ticker,ticker_type=ticker_type)+text_lang("，价格波动风险",", Price Volatility Risk")
    import datetime; todaydt = datetime.date.today()
    footnote=texttranslate("数据来源：Sina/EM/Stooq/Yahoo/SWHY，")+str(todaydt)
    collabel=ectranslate(type)
    ylabeltxt=ectranslate(type)
    pltdf=erdf[erdf.index >= fromdate]
    plot_line(pltdf,type,collabel,ylabeltxt,titletxt,footnote,datatag=datatag, \
              power=power,zeroline=True)
    
    return erdf

if __name__ =="__main__":
    ticker="000002.SZ"
    fromdate="2020-1-1"
    todate="2020-3-16"
    type="Daily Ret%"
    datatag=False
    power=3
    
    df=get_price("000002.SZ","2019-1-1","2020-3-16")
    pv=price_volatility2(df,"000002.SZ","2019-1-1","2020-3-16","Annual Price Volatility")
    pv=price_volatility2(df,"000002.SZ","2019-1-1","2020-3-16","Annual Exp Price Volatility")

#==============================================================================
def stock_ret_volatility(ticker,fromdate,todate,type="Weekly Ret Volatility%",datatag=False,power=4,graph=True):
    """
    功能：绘制证券收益率波动风险折线图。
    输入：证券代码ticker；开始日期fromdate，结束日期todate；期间类型type；
    是否标注数据标签datatag，默认否；多项式趋势线的阶数，若为0则不绘制趋势线。
    输出：绘制证券收益率波动折线图
    返回：证券收益率波动数据表
    """
    #调整抓取样本的开始日期，以便保证有足够的样本供后续计算
    fromdate1=date_adjust(fromdate, -400)
    retdf=stock_ret(ticker,fromdate1,todate,graph=False)
    pricedfcols=list(retdf)
    
    #加入滚动收益率波动风险
    prdf1=rolling_ret_volatility(retdf, "Weekly") 
    prdf2=rolling_ret_volatility(prdf1, "Monthly")
    prdf3=rolling_ret_volatility(prdf2, "Quarterly")
    prdf4=rolling_ret_volatility(prdf3, "Annual") 
    
    #加入累计收益率波动风险
    erdf=expanding_ret_volatility(prdf4,fromdate)
    
    #如果不绘图则直接返回数据表
    if not graph: return erdf    
    
    #获得支持的收益率波动风险类型列名，去掉不需要的列名
    colnames=list(erdf)
    for c in pricedfcols:
        colnames.remove(c)
    
    #检查type是否在支持的收益率波动指标列名中
    if not (type in colnames):
        print("  #Error(stock_ret_volatility)，only support return risk types of",colnames)
        return        

    titletxt=texttranslate("证券收益率波动风险走势图：")+ticker_name(ticker)
    import datetime; today = datetime.date.today()
    footnote=texttranslate("数据来源：Sina/EM/Stooq/Yahoo/SWHY，")+str(today)
    collabel=ectranslate(type)
    ylabeltxt=ectranslate(type)
    pltdf=erdf[erdf.index >= fromdate]
    plot_line(pltdf,type,collabel,ylabeltxt,titletxt,footnote,datatag=datatag, \
              power=power,zeroline=True)
    
    return erdf

if __name__ =="__main__":
    ticker="000002.SZ"
    fromdate="2020-1-1"
    todate="2020-3-16"
    type="Daily Ret%"
    datatag=False
    power=3

    pv=stock_ret_volatility("000002.SZ","2019-1-1","2020-3-16","Annual Ret Volatility%")
    pv=stock_ret_volatility("000002.SZ","2019-1-1","2020-3-16","Annual Exp Ret Volatility%")


#==============================================================================
def ret_volatility2(retdf,ticker,fromdate,todate, \
                    type="Weekly Ret Volatility%",datatag=False, \
                    power=4,graph=True,ticker_type='auto'):
    """
    功能：绘制证券收益率波动风险折线图。与函数ret_volatility的唯一区别是不抓取股价。
    输入：股价数据集pricedf；证券代码ticker；开始日期fromdate，结束日期todate；期间类型type；
    是否标注数据标签datatag，默认否；多项式趋势线的阶数，若为0则不绘制趋势线。
    输出：绘制证券收益率波动折线图
    返回：证券收益率波动数据表
    """
    retdfcols=list(retdf)
    
    #retdf=calc_daily_return(pricedf)    
    #加入滚动价格波动风险
    from siat.security_prices import rolling_ret_volatility,expanding_ret_volatility
    prdf1=rolling_ret_volatility(retdf, "Weekly") 
    prdf2=rolling_ret_volatility(prdf1, "Monthly")
    prdf3=rolling_ret_volatility(prdf2, "Quarterly")
    prdf4=rolling_ret_volatility(prdf3, "Annual") 
    
    #加入累计价格波动风险
    erdf=expanding_ret_volatility(prdf4,fromdate)
    
    #如果不绘图则直接返回数据表
    if not graph: return erdf    
    
    #获得支持的价格波动风险类型列名，去掉不需要的列名
    colnames=list(erdf)
    for c in retdfcols:
        colnames.remove(c)
    
    #检查type是否在支持的收益率列名中
    if not (type in colnames):
        print("  #Error(ret_volatility2): only support return risk types of",colnames)
        return        

    titletxt=text_lang("证券趋势分析：","Security Trend: ")+ticker_name(ticker,ticker_type=ticker_type)+text_lang("，收益率波动风险",", Return Volatility Risk")
    import datetime; todaydt = datetime.date.today()
    footnote=text_lang("数据来源：Sina/EM/Stooq/Yahoo/SWHY，","Data source: Sina/EM/Stooq/Yahoo/SWHY, ")+str(todaydt)
    collabel=ectranslate(type)
    ylabeltxt=ectranslate(type)
    pltdf=erdf[erdf.index >= fromdate]
    plot_line(pltdf,type,collabel,ylabeltxt,titletxt,footnote,datatag=datatag, \
              power=power,zeroline=True)
    
    return erdf

if __name__ =="__main__":
    ticker="000002.SZ"
    fromdate="2020-1-1"
    todate="2020-3-16"
    type="Daily Ret%"
    datatag=False
    power=3
    
    df=get_price("000002.SZ","2019-1-1","2020-3-16")
    pv=price_volatility2(df,"000002.SZ","2019-1-1","2020-3-16","Annual Price Volatility")
    pv=price_volatility2(df,"000002.SZ","2019-1-1","2020-3-16","Annual Exp Price Volatility")

#==============================================================================
def ret_lpsd(ticker,fromdate,todate,type="Weekly Ret Volatility%",datatag=False,power=4,graph=True):
    """
    功能：绘制证券收益率波动损失风险折线图。
    输入：证券代码ticker；开始日期fromdate，结束日期todate；期间类型type；
    是否标注数据标签datatag，默认否；多项式趋势线的阶数，若为0则不绘制趋势线。
    输出：绘制证券收益率下偏标准差折线图
    返回：证券收益率下偏标准差数据表
    """
    #调整抓取样本的开始日期，以便保证有足够的样本供后续计算
    fromdate1=date_adjust(fromdate, -400)
    retdf=stock_ret(ticker,fromdate1,todate,graph=False)
    pricedfcols=list(retdf)
    
    #加入滚动收益率下偏标准差
    prdf1=rolling_ret_lpsd(retdf, "Weekly") 
    prdf2=rolling_ret_lpsd(prdf1, "Monthly")
    prdf3=rolling_ret_lpsd(prdf2, "Quarterly")
    prdf4=rolling_ret_lpsd(prdf3, "Annual") 
    
    #加入扩展收益率下偏标准差
    erdf=expanding_ret_lpsd(prdf4,fromdate)
    
    #如果不绘图则直接返回数据表
    if not graph: return erdf    
    
    #获得支持的收益率波动风险类型列名，去掉不需要的列名
    colnames=list(erdf)
    for c in pricedfcols:
        colnames.remove(c)
    
    #检查type是否在支持的收益率波动指标列名中
    if not (type in colnames):
        print("  #Error(ret_lpsd): only support return risk types of",colnames)
        return        

    titletxt=texttranslate("证券收益率波动损失风险走势图：")+ticker_name(ticker)
    import datetime; today = datetime.date.today()
    footnote=texttranslate("数据来源：Sina/EM/Stooq/Yahoo/SWHY，")+str(today)
    collabel=ectranslate(type)
    ylabeltxt=ectranslate(type)
    pltdf=erdf[erdf.index >= fromdate]
    plot_line(pltdf,type,collabel,ylabeltxt,titletxt,footnote,datatag=datatag, \
              power=power,zeroline=True)
    
    return erdf

if __name__ =="__main__":
    ticker="000002.SZ"
    fromdate="2020-1-1"
    todate="2020-3-16"
    type="Daily Ret%"
    datatag=False
    power=3

    pv=ret_lpsd("000002.SZ","2019-1-1","2020-3-16","Annual Ret Volatility%")
    pv=ret_lpsd("000002.SZ","2019-1-1","2020-3-16","Annual Exp Ret Volatility%")

#==============================================================================
def ret_lpsd2(retdf,ticker,fromdate,todate, \
              rtype="Weekly Ret Volatility%",datatag=False, \
              power=4,graph=True,ticker_type='auto'):
    """
    功能：绘制证券收益率波动损失风险折线图。与函数ret_lpsd的唯一区别是不抓取股价。
    输入：股价数据集pricedf；证券代码ticker；开始日期fromdate，结束日期todate；期间类型type；
    是否标注数据标签datatag，默认否；多项式趋势线的阶数，若为0则不绘制趋势线。
    输出：绘制证券收益率下偏标准差折线图。
    返回：证券收益率下偏标准差数据表。
    """
    retdfcols=list(retdf)
    #retdf=calc_daily_return(pricedf)    
    #加入滚动价格波动风险
    from siat.security_prices import rolling_ret_lpsd,expanding_ret_lpsd
    prdf1=rolling_ret_lpsd(retdf, "Weekly") 
    prdf2=rolling_ret_lpsd(prdf1, "Monthly")
    prdf3=rolling_ret_lpsd(prdf2, "Quarterly")
    prdf4=rolling_ret_lpsd(prdf3, "Annual") 
    
    #加入扩展收益率下偏标准差
    erdf=expanding_ret_lpsd(prdf4,fromdate)
    
    #如果不绘图则直接返回数据表
    if not graph: return erdf    
    
    #获得支持的价格波动风险类型列名，去掉不需要的列名
    colnames=list(erdf)
    for c in retdfcols:
        colnames.remove(c)
    
    #检查type是否在支持的收益率列名中
    if not (rtype in colnames):
        print("  #Error(ret_lpsd2): only support return risk types of",colnames)
        return        

    titletxt=text_lang("证券趋势分析：","Security Trend: ")+ticker_name(ticker,ticker_type=ticker_type)+text_lang("波动损失风险","Volatility Loss Risk")
    import datetime; todaydt = datetime.date.today()
    footnote=text_lang("数据来源：Sina/EM/Stooq/Yahoo/SWHY，","Data source: Sina/EM/Stooq/Yahoo/SWHY, ")+str(todaydt)
    collabel=ectranslate(rtype)
    ylabeltxt=ectranslate(rtype)
    pltdf=erdf[erdf.index >= fromdate]
    plot_line(pltdf,rtype,collabel,ylabeltxt,titletxt,footnote,datatag=datatag, \
              power=power,zeroline=True)
    
    return erdf

if __name__ =="__main__":
    ticker="000002.SZ"
    fromdate="2020-1-1"
    todate="2020-3-16"
    type="Daily Ret%"
    datatag=False
    power=3
    
    df=get_price("000002.SZ","2019-1-1","2020-3-16")
    pv=price_lpsd2(df,"000002.SZ","2019-1-1","2020-3-16","Annual Price Volatility")
    pv=price_lpsd2(df,"000002.SZ","2019-1-1","2020-3-16","Annual Exp Price Volatility")
#==============================================================================
def comp_1security_2measures(df,measure1,measure2,twinx=False, \
                                 attention_value='',attention_value_area='', \
                                 attention_point='',attention_point_area='', \
                             loc1='upper left',loc2='lower left', \
                             graph=True,facecolor='whitesmoke', \
                             ticker_type='auto'):
    """
    功能：对比绘制一只证券两个指标的折线图。
    输入：证券指标数据集df；行情类别measure1/2。
    输出：绘制证券行情双折线图，基于twinx判断使用单轴或双轴坐标
    返回：无
    """
    DEBUG=False
    
    #筛选证券指标，检验是否支持指标
    dfcols=list(df)
    #nouselist=['date','Weekday','ticker']
    #for c in nouselist: dfcols.remove(c)
    
    if not (measure1 in dfcols):
        print("  #Error(comp_1security_2measures): unsupported measures: ",measure1)
        print("  Supporting measures: ",dfcols)
        return        
    if not (measure2 in dfcols):
        print("  #Error(comp_1security_2measures): unsupported measures: ",measure2)
        print("  Supporting measures: ",dfcols)
        return 
    
    #判断是否绘制水平0线
    pricelist=['High','Low','Open','Close','Volume','Adj Close']
    if (measure1 in pricelist) or (measure2 in pricelist): 
        zeroline=False
    else: zeroline=True

    #提取信息
    ticker=df['ticker'][0]
    fromdate=str(df.index[0].date())
    todate=str(df.index[-1].date())
    label1=ectranslate(measure1)
    label2=ectranslate(measure2)
    ylabeltxt=""
    
    tname=ticker_name(ticker,ticker_type=ticker_type)
    titletxt=text_lang("证券趋势分析：","Security Trend: ")+tname
    
    import datetime; todaydt = datetime.date.today()
    footnote1=text_lang("数据来源：Sina/EM/Stooq/Yahoo/SWHY，","Source: Sina/EM/Stooq/Yahoo/SWHY, ")
    footnote=footnote1+str(todaydt)
    
    #绘图
    if DEBUG:
        print("plot_line2")
        print("attention_value=",attention_value)
        print("attention_point=",attention_point)
    
    plot_line2(df,ticker,measure1,label1,df,ticker,measure2,label2, \
               ylabeltxt,titletxt,footnote,zeroline=zeroline,twinx=twinx, \
                    yline=attention_value,attention_value_area=attention_value_area, \
                    xline=attention_point,attention_point_area=attention_point_area, \
               loc1=loc1,loc2=loc2,facecolor=facecolor)

    return 

if __name__ =="__main__":
    ticker='000002.SZ'
    measure1='Daily Ret%'
    measure2='Daily Adj Ret%'
    fromdate='2020-1-1'
    todate='2020-3-16'
    df=stock_ret(ticker,fromdate,todate,graph=False)
    comp_1security_2measures(df,measure1,measure2)
#==============================================================================
def comp_2securities_1measure(df1,df2,measure,twinx=False, \
                                  attention_value='',attention_value_area='', \
                                  attention_point='',attention_point_area='', \
                              loc1='best',loc2='best',graph=True, \
                              ticker_type=['auto','auto'],facecolor='whitesmoke'):
    """
    功能：对比绘制两只证券的相同指标折线图。
    输入：指标数据集df1/2；证券代码ticker1/2；指标类别measure。
    输出：绘制证券指标双折线图，基于twinx判断使用单轴或双轴坐标。
    返回：无
    """
    
    #筛选证券指标，检验是否支持指标
    dfcols=list(df1)
    #nouselist=['date','Weekday','ticker']
    #for c in nouselist: dfcols.remove(c)
    
    if not (measure in dfcols):
        print("  #Error(comp_2securities_1measure)：only support measurement types of",dfcols)
        return        

    #判断是否绘制水平0线
    pricelist=['High','Low','Open','Close','Volume','Adj Close']
    if measure in pricelist: zeroline=False
    else: 
        df_max=max([df1[measure].max(),df2[measure].max()])
        df_min=min([df1[measure].min(),df2[measure].min()])
        if df_max * df_min >0: #同正同负
            zeroline=False
        else:
            zeroline=True

    #提取信息
    try:
        ticker1=df1['ticker'][0]
    except:
        print("  #Error(comp_2securities_1measure)： none info found for the 1st symbol")
        return
    try:
        ticker2=df2['ticker'][0]
    except:
        print("  #Error(comp_2securities_1measure)： none info found for the 2nd symbol")
        return
    
    fromdate=str(df1.index[0].date())
    todate=str(df1.index[-1].date())
    label=ectranslate(measure)
    ylabeltxt=ectranslate(measure)

    tname1=ticker_name(ticker1,ticker_type=ticker_type[0])
    tname2=ticker_name(ticker2,ticker_type=ticker_type[1])
    
    #绘图
    print('')
    
    titletxt1=text_lang("证券趋势分析：","Security Trend: ")
    titletxt=titletxt1+tname1+" vs "+tname2
        
    import datetime; todaydt = datetime.date.today()
    footnote1=text_lang("数据来源：Sina/EM/Stooq/Yahoo/SWHY，","Data source: Sina/EM/Stooq/Yahoo/SWHY, ")
    footnote=footnote1+str(todaydt)+text_lang("统计","")

    plot_line2(df1,ticker1,measure,label,df2,ticker2,measure,label, \
               ylabeltxt,titletxt,footnote,zeroline=zeroline,twinx=twinx, \
                    yline=attention_value,attention_value_area=attention_value_area, \
                    xline=attention_point,attention_point_area=attention_point_area, \
               loc1=loc1,loc2=loc2,facecolor=facecolor)

    return 

if __name__ =="__main__":
    ticker1='000002.SZ'
    ticker2='600266.SS'
    measure='Daily Ret%'
    fromdate='2020-1-1'
    todate='2020-3-16'
    df1=stock_ret(ticker1,fromdate,todate,graph=False)
    df2=stock_ret(ticker2,fromdate,todate,graph=False)
    comp_2securities_1measure(df1,df2,measure)
#==============================================================================
if __name__ =="__main__":
    tickers=['MSFT','AAPL']
    measures='Annual Ret Volatility%'
    
    tickers='MSFT'
    measures=['Annual Ret Volatility%','Annual Ret%']
    
    tickers='NVDA'
    tickers='AAPL'
    measures=['Close','Adj Close']   
    
    tickers=['000001.SS','^DJI']
    measures='Close'
    
    fromdate='2024-5-1'
    todate='2025-6-23'
    adjust=''
    twinx=False
    loc1='best'
    loc2='lower left'
    graph=True
    source='auto'
    ticker_type='auto'
    facecolor='whitesmoke'
    
    attention_value=''; attention_value_area=''
    attention_point=''; attention_point_area=''
    

def compare_security(tickers,measures,fromdate,todate, \
                     adjust='', \
                     twinx=False, \
                         attention_value='',attention_value_area='', \
                         attention_point='',attention_point_area='', \
                     loc1='best',loc2='lower left',graph=True,source='auto', \
                     ticker_type='auto',facecolor='whitesmoke'):
    """
    功能：函数克隆compare_stock，只能处理两个ticker一个measure，或一个ticker两个measure
    可以处理twinx=True
    """
    """
    # 应对导入失灵的函数
    from siat.security_prices import upper_ticker
    tickers=upper_ticker(tickers)
    result=compare_stock(tickers=tickers,measures=measures, \
                         fromdate=fromdate,todate=todate, \
                         adjust=adjust, \
                         twinx=twinx, \
                         loc1=loc1,loc2=loc2,graph=graph,source=source, \
                         ticker_type=ticker_type,facecolor=facecolor)
    
    return result
    """
    #调试开关
    DEBUG=False
    
    # 应对导入失灵的函数
    from siat.common import upper_ticker
    tickers=upper_ticker(tickers)
    
    #判断证券代码个数
    #如果tickers只是一个字符串
    security_num = 0
    if isinstance(tickers,str): 
        security_num = 1
        ticker1 = tickers
    #如果tickers是一个列表
    if isinstance(tickers,list): 
        security_num = len(tickers)
        if security_num != 0:
            if security_num >= 1: ticker1 = tickers[0]
            if security_num >= 2: ticker2 = tickers[1]
        else:
            print("  #Error(compare_security)：security code/codes needed.")
            return None,None
            
    #判断测度个数
    #如果measures只是一个字符串
    measure_num = 0
    if isinstance(measures,str): 
        measure_num = 1
        #measure1 = measures
        measure1 = measure2 = measures
    #如果measures是一个列表
    if isinstance(measures,list): 
        measure_num = len(measures)
        if measure_num != 0:
            if measure_num >= 1: measure1 = measures[0]
            if measure_num >= 2: measure2 = measures[1]
        else:
            print("  #Error(compare_security)： a measurement indicator needed.")
            return None,None

    #解析ticker_type
    if isinstance(ticker_type,str):
        ticker_type1=ticker_type2=ticker_type
    if isinstance(ticker_type,list) and len(ticker_type)==1:
        ticker_type1=ticker_type2=ticker_type[0]
    if isinstance(ticker_type,list) and len(ticker_type) >= 2:
        ticker_type1=ticker_type[0]
        ticker_type2=ticker_type[1]
    ticker_type_list=[ticker_type1,ticker_type2]
    
    #屏蔽函数内print信息输出的类
    import os, sys
    class HiddenPrints:
        def __enter__(self):
            self._original_stdout = sys.stdout
            sys.stdout = open(os.devnull, 'w')

        def __exit__(self, exc_type, exc_val, exc_tb):
            sys.stdout.close()
            sys.stdout = self._original_stdout    

    #单一证券代码+两个测度指标
    if (security_num == 1) and (measure_num >= 2):
        
        print("  Searching",ticker1,"for",measure1,"info ... ...")
        #复权价判断1
        adjust1=adjust
        if ('Adj' in measure1) and (adjust1 ==''):
            adjust1='qfq'

        with HiddenPrints():
            #security_indicator未能做到同时获得Close和Adj Close
            df1tmp=security_indicator(ticker=ticker1,indicator=measure1,adjust=adjust1, \
                        fromdate=fromdate,todate=todate, \
                        source=source, \
                        ticker_type=ticker_type, \
                        graph=False)
                
        if df_have_data(df1tmp)=="Found":
            pltdf1= df1tmp[[measure1]]
        else:
            print("  #Error(compare_security)：no info found for",ticker1,"on",measure1)
            return None,None
        
        print("  Searching",ticker1,"for",measure2,"info ... ...")
        #复权价判断2
        adjust2=adjust
        if ('Adj' in measure2) and (adjust2 ==''):
            adjust2='qfq'

        with HiddenPrints():
            #security_indicator未能做到同时获得Close和Adj Close
            df2tmp=security_indicator(ticker=ticker1,indicator=measure2,adjust=adjust2, \
                            fromdate=fromdate,todate=todate, \
                            source=source, \
                            ticker_type=ticker_type, \
                            graph=False)
 
        if df_have_data(df2tmp)=="Found":
            pltdf2= df2tmp[[measure2]]
        else:
            print("  #Error(compare_security)：no info found for",ticker1,"on",measure2)
            return None,None
        
        pltdf=pd.merge(pltdf1,pltdf2,left_index=True,right_index=True)
        pltdf['ticker']=ticker1
            
        #绘制单个证券的双指标对比图
        if graph:
            if DEBUG:
                print("In compare_security:")
                print("Going to comp_1security_2measures ...")
                print("attention_value=",attention_value)
                print("attention_point=",attention_point)
            
            comp_1security_2measures(pltdf,measure1,measure2,twinx=twinx, \
                                         attention_value=attention_value,attention_value_area=attention_value_area, \
                                         attention_point=attention_point,attention_point_area=attention_point_area, \
                                     loc1=loc1,loc2=loc2,graph=graph, \
                                     ticker_type=ticker_type[0],facecolor=facecolor)
        
        try:
            result1=pltdf[['ticker',measure1]]
        except:
            result1=None
        try:
            result2=pltdf[['ticker',measure2]]
        except:
            result2=None
        return result1,result2
        
    elif (security_num >= 2) and (measure_num >= 1):
        #双证券+单个测度指标 
        if ('Adj' in measure1) and (adjust ==''):
            adjust='qfq'

        df1tmp=security_indicator(ticker=ticker1,indicator=measure1,adjust=adjust, \
                              fromdate=fromdate,todate=todate, \
                              source=source, \
                              ticker_type=ticker_type, \
                              graph=False) 
        if df_have_data(df1tmp)=="Found":
            pltdf1=df1tmp[['ticker',measure1]] 
        else:
            print("  #Error(compare_security)：no info found for",ticker1,"on",measure1)
            return None,None
        
        df2tmp=security_indicator(ticker=ticker2,indicator=measure1,adjust=adjust, \
                              fromdate=fromdate,todate=todate, \
                              source=source, \
                              ticker_type=ticker_type, \
                              graph=False) 
        if df_have_data(df2tmp)=="Found":
            pltdf2=df2tmp[['ticker',measure1]]   
        else:
            print("  #Error(compare_security)：no info found for",ticker2,"on",measure1)
            return None,None
        
        #绘制双证券单指标对比图
        if graph:
            if DEBUG:
                print("In compare_security ...")
                print("Going to comp_2securities_1measure")
                print("attention_value=",attention_value)
                print("attention_point=",attention_point)
            
            comp_2securities_1measure(pltdf1,pltdf2,measure1,twinx=twinx, \
                                      attention_value=attention_value,attention_value_area=attention_value_area, \
                                      attention_point=attention_point,attention_point_area=attention_point_area, \
                                      loc1=loc1,loc2=loc2,graph=graph, \
                                      ticker_type=ticker_type_list,facecolor=facecolor)
        
        try:
            result1=pltdf1[[measure1]]
        except:
            print("  #Error(compare_secuirty): measure",measure1,"not found for",ticker1)
            result1=None
        try:
            result2=pltdf2[[measure1]]
        except:
            print("  #Error(compare_secuirty): measure",measure1,"not found for",ticker2)
            result2=None
        return result1,result2
            
    else:
        print("  #Warning(compare_secuirty)：only support 1 ticker + 2 measures or 2 tickers + 1 measure.")
        return None,None
    
    
#==============================================================================
if __name__ =="__main__":
    tickers=['MSFT','AAPL']
    measures='Annual Ret Volatility%'
    fromdate='2023-1-1'
    todate='2023-12-31'
    adjust=''
    twinx=False
    loc1='best'
    loc2='lower left'
    graph=True
    source='auto'
    ticker_type='auto'
    facecolor='whitesmoke'


def compare_stock(tickers,measures,fromdate,todate, \
                  adjust='', \
                  twinx=False, \
                  loc1='best',loc2='lower left',graph=True,source='auto', \
                  ticker_type='auto',facecolor='whitesmoke'):    
    """
    功能：对比绘制折线图：一只证券的两种测度，或两只证券的同一个测度。
    输入：
    证券代码tickers，如果是一个列表且内含两个证券代码，则认为希望比较两个证券的
    同一个测度指标。如果是一个列表但只内含一个证券代码或只是一个证券代码的字符串，
    则认为希望比较一个证券的两个测度指标。
    测度指标measures：如果是一个列表且内含两个测度指标，则认为希望比较一个证券的
    两个测度指标。如果是一个列表但只内含一个测度指标或只是一个测度指标的字符串，
    则认为希望比较两个证券的同一个测度指标。
    如果两个判断互相矛盾，以第一个为准。
    开始日期fromdate，结束日期todate。
    输出：绘制证券价格折线图，手动指定是否使用单轴或双轴坐标。
    返回：无
    
    打算废弃？
    """
    #调试开关
    DEBUG=False
    # 应对导入失灵的函数
    from siat.common import upper_ticker
    tickers=upper_ticker(tickers)
    
    #判断证券代码个数
    #如果tickers只是一个字符串
    security_num = 0
    if isinstance(tickers,str): 
        security_num = 1
        ticker1 = tickers
    #如果tickers是一个列表
    if isinstance(tickers,list): 
        security_num = len(tickers)
        if security_num == 0:
            print("  #Error(compare_stock)：security code/codes needed.")
            return None,None
        if security_num >= 1: ticker1 = tickers[0]
        if security_num >= 2: ticker2 = tickers[1]
            
    #判断测度个数
    #如果measures只是一个字符串
    measure_num = 0
    if isinstance(measures,str): 
        measure_num = 1
        measure1 = measures
    #如果measures是一个列表
    if isinstance(measures,list): 
        measure_num = len(measures)
        if measure_num == 0:
            print("  #Error(compare_stock)： a measurement indicator needed.")
            return None,None
        if measure_num >= 1: measure1 = measures[0]
        if measure_num >= 2: measure2 = measures[1]

    #延伸开始日期
    fromdate1=date_adjust(fromdate,adjust=-365)

    #单一证券代码+两个测度指标
    if (security_num == 1) and (measure_num >= 2):
        if (('Adj' in measure1) or ('Adj' in measure2)) and (adjust ==''):
            adjust='qfq'
        
        #证券ticker1：抓取行情，并计算其各种期间的收益率
        df1a=stock_ret(ticker1,fromdate1,todate,adjust=adjust,graph=False,source=source,ticker_type=ticker_type)
        if df1a is None: return None,None
        if DEBUG: print("compare|df1a first date:",df1a.index[0])
        #加入价格波动指标
        df1b=price_volatility2(df1a,ticker1,fromdate1,todate,graph=False,ticker_type=ticker_type)
        if DEBUG: print("compare|df1b first date:",df1b.index[0])
        #加入收益率波动指标
        df1c=ret_volatility2(df1b,ticker1,fromdate1,todate,graph=False,ticker_type=ticker_type)
        if DEBUG: print("compare|df1c first date:",df1c.index[0])
        #加入收益率下偏标准差指标
        df1d=ret_lpsd2(df1c,ticker1,fromdate1,todate,graph=False,ticker_type=ticker_type)
        if DEBUG: print("compare|df1d first date:",df1d.index[0])
        
        #去掉开始日期以前的数据
        pltdf1=df1d[df1d.index >= fromdate1]
        #绘制单个证券的双指标对比图
        if graph:
            comp_1security_2measures(pltdf1,measure1,measure2,twinx=twinx, \
                                     loc1=loc1,loc2=loc2,graph=graph, \
                                     ticker_type=ticker_type,facecolor=facecolor)
        
        try:
            result1=pltdf1[[measure1]]
        except:
            return None,None
        try:
            result2=pltdf1[[measure2]]
        except:
            return result1,None
        
    elif (security_num >= 2) and (measure_num >= 1):
        #双证券+单个测度指标 
        if ('Adj' in measure1) and (adjust ==''):
            adjust='qfq'
        
        #解析ticker_type
        if isinstance(ticker_type,str):
            ticker_type1=ticker_type2=ticker_type
        if isinstance(ticker_type,list) and len(ticker_type)==1:
            ticker_type1=ticker_type2=ticker_type[0]
        if isinstance(ticker_type,list) and len(ticker_type) > 1:
            ticker_type1=ticker_type[0]
            ticker_type2=ticker_type[1]
        ticker_type_list=[ticker_type1,ticker_type2]
        
        #证券ticker1：抓取行情，并计算其各种期间的收益率
        df1a=stock_ret(ticker1,fromdate1,todate,adjust=adjust,graph=False,source=source,ticker_type=ticker_type1)
        if df1a is None: return None,None
        #加入价格波动指标
        df1b=price_volatility2(df1a,ticker1,fromdate1,todate,graph=False,ticker_type=ticker_type1)
        #加入收益率波动指标
        df1c=ret_volatility2(df1b,ticker1,fromdate1,todate,graph=False,ticker_type=ticker_type1)
        #加入收益率下偏标准差指标
        df1d=ret_lpsd2(df1c,ticker1,fromdate1,todate,graph=False,ticker_type=ticker_type1)        
        #去掉开始日期以前的数据
        pltdf1=df1d[df1d.index >= fromdate1]
        
        #证券ticker2：
        df2a=stock_ret(ticker2,fromdate1,todate,adjust=adjust,graph=False,source=source,ticker_type=ticker_type2)
        if df2a is None: return None,None
        df2b=price_volatility2(df2a,ticker2,fromdate1,todate,graph=False,ticker_type=ticker_type2)
        df2c=ret_volatility2(df2b,ticker2,fromdate1,todate,graph=False,ticker_type=ticker_type2)
        df2d=ret_lpsd2(df2c,ticker2,fromdate1,todate,graph=False,ticker_type=ticker_type2)
        pltdf2=df2d[df2d.index >= fromdate1]
        
        #绘制双证券单指标对比图
        if graph:
            comp_2securities_1measure(pltdf1,pltdf2,measure1,twinx=twinx, \
                                      loc1=loc1,loc2=loc2,graph=graph, \
                                      ticker_type=ticker_type_list,facecolor=facecolor)
        
        try:
            result1=pltdf1[[measure1]]
            result2=pltdf2[[measure1]]
        except:
            print("  #Error(compare_stock): unknown measure",measure1)
            return None,None
            
    else:
        print("  #Error(compare_stock)：do not understand what to compare.")
        return None,None

    return result1,result2

if __name__ =="__main__":
    tickers='000002.SZ'
    measures=['Close','Adj Close']
    fromdate='2020-1-1'
    todate='2020-3-16'
    compare_stock(tickers,measures,fromdate,todate)            

    tickers2=['000002.SZ','600266.SS']
    measures2=['Close','Adj Close']
    compare_stock(tickers2,measures2,fromdate,todate)

    tickers3=['000002.SZ','600266.SS']
    measures3='Close'
    compare_stock(tickers3,measures3,fromdate,todate)    

    tickers4=['000002.SZ','600606.SS','600266.SS']
    measures4=['Close','Adj Close','Daily Return']
    compare_stock(tickers4,measures4,fromdate,todate)      
    
#==============================================================================
if __name__ =="__main__":
    # 测试组1
    tickers=["AMZN","EBAY","SHOP","BABA","JD"]
    tickers=["AMZN","EBAY","SHOP","BABA","JD","PDD"]
    tickers=['000001.SS',"399001.SZ","000300.SS"]
    tickers=['000001.SS','^N225','^KS11']
    measure="Annual Ret%"
    measure="Exp Ret%"
    measure="Close"
    measure="Annual Ret Volatility%"
    
    start="2020-1-1"
    end="2022-7-31"
    
    preprocess='scaling'
    linewidth=1.5
    scaling_option='start'
    
    # 测试组2
    tickers=["GCZ25.CMX","GCZ24.CMX"]
    measure='Close'
    start="2020-1-1"
    end="2020-6-30"
    
    # 测试组3
    tickers=["MBG.DE", "BMW.DE"]
    measure='Close'
    start="2025-6-1"
    end="2025-6-15"    
    
    attention_value='';attention_value_area=''
    attention_point='';attention_point_area=''
    adjust=''
    axhline_value=0;axhline_label=''
    preprocess='none';linewidth=1.5
    scaling_option='start'
    plus_sign=False
    band_area=''
    graph=True;loc='best';facecolor='whitesmoke'
    annotate=False;annotate_value=False
    smooth=True
    source='auto'
    mark_top=True;mark_bottom=True
    mark_start=False;mark_end=False
    ticker_type='auto'
    
def compare_msecurity(tickers,measure,start,end, \
                        attention_value='',attention_value_area='', \
                        attention_point='',attention_point_area='', \
                      adjust='', \
                      axhline_value=0,axhline_label='', \
                      preprocess='none',linewidth=1.5, \
                      scaling_option='start', \
                      plus_sign=False, \
                        band_area='', \
                      graph=True,loc='best',facecolor='whitesmoke', \
                      annotate=False,annotate_value=False, \
                      smooth=True, \
                      source='auto', \
                      mark_top=True,mark_bottom=True, \
                      mark_start=False,mark_end=False, \
                      ticker_type='auto'):
    """
    功能：比较并绘制多条证券指标曲线（多于2条），个数可为双数或单数
    注意：
    tickers中须含有2个及以上股票代码，
    measure为单一指标，
    axhline_label不为空时绘制水平线
    
    preprocess：是否对绘图数据进行预处理，仅适用于股价等数量级差异较大的数据，
    不适用于比例、比率和百分比等数量级较为一致的指标。
        standardize: 标准化处理，(x - mean(x))/std(x)
        normalize: 归一化处理，(x - min(x))/(max(x) - min(x))
        logarithm: 对数处理，np.log(x)
        scaling：缩放处理，五种选项scaling_option
        （mean均值，min最小值，start开始值，percentage相对每条曲线起点值的百分比，
        change%相对每条曲线起点值变化的百分比）
        change%方式的图形更接近于持有收益率(Exp Ret%)，设为默认的缩放方式。
    
    """
    DEBUG=False
    
    # 应对导入失灵的函数
    from siat.common import upper_ticker
    tickers=upper_ticker(tickers)
    if not isinstance(tickers,list):
        tickers=[tickers]
    
    # 去掉重复代码：有必要，重复代码将导致后续处理出错KeyError: 0！
    tickers=list(set(tickers))
    """
    num=len(tickers)
    if num <2:
        print("  #Error(compare_msecurity): need more tickers")
        return None
    """
    if isinstance(measure,list):
        measure=measure[0]
    
    print("  Searching securities for",measure,"...") 
    #屏蔽函数内print信息输出的类
    import os, sys
    class HiddenPrints:
        def __enter__(self):
            self._original_stdout = sys.stdout
            sys.stdout = open(os.devnull, 'w')

        def __exit__(self, exc_type, exc_val, exc_tb):
            sys.stdout.close()
            sys.stdout = self._original_stdout
    
    #循环获取证券指标
    import pandas as pd
    from functools import reduce

    #预处理ticker_type成为列表ticker_type_list
    if isinstance(ticker_type,str):
        ticker_type_list=[ticker_type] * len(tickers)
    if isinstance(ticker_type,list):
        ticker_type_list=ticker_type
        if len(ticker_type_list) < len(tickers): #延续最后项的ticker_type
            ticker_type_list=ticker_type_list+[ticker_type_list[-1]]*(len(tickers)-len(ticker_type_list))

    dfs=pd.DataFrame()
    for t in tickers:
        print("  Looking security info for",t,'...')
        pos=tickers.index(t)
        tt=ticker_type_list[pos]
        
        with HiddenPrints():
            df_tmp=security_indicator(t,measure,start,end,adjust=adjust,graph=False,source=source,ticker_type=tt)
        if df_tmp is None:
            print("  #Warning(compare_msecurity): security info not found for",t)
            continue
        if len(df_tmp)==0:
            print("  #Warning(compare_msecurity): security info not found for",t,'between',start,'and',end)
            continue
        
        df_tmp1=pd.DataFrame(df_tmp[measure])
        
        tname=ticker_name(t,tt)
        df_tmp1.rename(columns={measure:tname},inplace=True) 
        
        # 将band_area中的ticker替换为tname
        if band_area != '':
            for index, item in enumerate(band_area):
                if item == t:
                    band_area[index] = tname        
        
        if len(dfs)==0:
            dfs=df_tmp1
        else:
            dfs=pd.concat([dfs,df_tmp1],axis=1,join='outer')
            
    if dfs is None:
        print("  #Error(compare_msecurity): no records found for",tickers)
        return None
    if len(dfs)==0:
        print("  #Error(compare_msecurity): zero records found for",tickers)
        return None
    
    dfs.sort_index(ascending=True,inplace=True)

    # 若不绘图则返回原始数据
    if not graph:
        return dfs

    #绘制多条曲线
    y_label=ectranslate(measure)
    tickersplit=tickers[0].split('.')
    if (len(tickersplit) > 1) and (measure == 'Close'):
        if tickersplit[1].upper() in ['M','B']:
            #y_label='指标'
            y_label='指标对比'
    
    x_label1cn="数据来源: Sina/EM/Stooq/Yahoo/SWHY，"
    x_label1en="Source: Sina/EM/Stooq/Yahoo/SWHY, "
    x_label1=text_lang(x_label1cn,x_label1en)   
    import datetime; todaydt = datetime.date.today()
    x_label=x_label1+str(todaydt)  

    title_txt1=text_lang("证券趋势分析","Security Trend") 
    if y_label != '':
        title_txt=title_txt1+": "+y_label
    else:
        title_txt=title_txt1
        
    if preprocess == 'scaling' and scaling_option == 'change%':
        title_txt2=text_lang("涨跌幅度","Changes")
        if ':' in title_txt:
            title_txt=title_txt+', '+title_txt2  
        else:
            title_txt=title_txt+': '+title_txt2
            
        axhline_value=0
        axhline_label="零线"

    # 标准化处理
    try:
        dfs2,axhline_label,x_label,y_label,plus_sign=df_preprocess(dfs,measure, \
                axhline_label=axhline_label,x_label=x_label,y_label=y_label, \
                preprocess=preprocess,scaling_option=scaling_option)
    except:
        print("  #Error(compare_msecurity): preprocess failed, returning dfs for further check")
        #df_display_CSS(dfs,titletxt='Unexpected Data in dfs')
        return dfs
        
    # 填充非交易日的缺失值，使得绘制的曲线连续
    dfs2.fillna(axis=0,method='ffill',inplace=True)
    #dfs2.fillna(axis=0,method='bfill',inplace=True)

    if DEBUG:
        print("DEBUG: dfs2=",list(dfs2))
        
    above_zero=0; below_zero=0
    for c in list(dfs2):
        c_max=dfs2[c].max(); c_min=dfs2[c].min()
        try:
            if c_max>0 or c_min>0: above_zero+=1
            if c_max<0 or c_min<0: below_zero+=1
        except: continue

    if DEBUG:
        print("DEBUG: above_zero=",above_zero,'below_zero=',below_zero)
    
    if above_zero>0 and below_zero>0: #有正有负
    #if 'Ret%' in measure:
        if axhline_label=='':
            axhline_label='零线'
     
    #持有类指标的首行置为零
    colList=list(dfs2)
    index1=dfs2.head(1).index.values[0]
    for c in colList:
        if 'Exp Ret%' in c:
            dfs2.loc[dfs2[dfs2.index==index1].index.tolist(),c]=0

    draw_lines(dfs2,y_label,x_label,axhline_value,axhline_label,title_txt, \
               data_label=False,resample_freq='H',smooth=smooth,linewidth=linewidth,loc=loc, \
                    attention_value=attention_value,attention_value_area=attention_value_area, \
                    attention_point=attention_point,attention_point_area=attention_point_area, \
               band_area=band_area, \
               annotate=annotate,annotate_value=annotate_value,plus_sign=plus_sign, \
               mark_top=mark_top,mark_bottom=mark_bottom, \
               mark_start=mark_start,mark_end=mark_end,facecolor=facecolor)

    return dfs2

if __name__ =="__main__":
    tickers=['000001.SS',"^HSI","^TWII"]
    df=compare_msecurity(tickers,'Close','2020-1-1','2022-12-14',preprocess='standardize')
    df=compare_msecurity(tickers,'Close','2020-1-1','2022-12-14',preprocess='normalize')
    df=compare_msecurity(tickers,'Close','2020-1-1','2022-12-14',preprocess='logarithm')
    df=compare_msecurity(tickers,'Close','2020-1-1','2022-12-14',preprocess='scaling')

#==============================================================================
if __name__ =="__main__":
    tickers=['JD','BABA','BIDU','VIPS','PDD']
    start='2023-5-1'
    end='2023-6-16'
    ret_measure='Exp Ret%'
    ret_measure='Annual Ret%'
    
    risk_type='Volatility'
    annotate=True
    graph=True
    smooth=False
    
    
def compare_mrrr(tickers,start,end,ret_measure='Exp Ret%',risk_type='Volatility', \
                 annotate=False,graph=True,smooth=True,winsorize_limits=[0.05,0.05], \
                 facecolor='whitesmoke'):
    """
    功能：rrr = return-risk ratio
    比较多个证券的简单收益-风险性价比，基于compare_msecurity
    ret_measure='Exp Ret%'：可以为持有收益率，或滚动收益率
    risk_type='Volatility'：可以为标准差，或下偏标准差
    
    winsorize_limits=[0.05,0.05]：去掉最低的5%（第一个参数），去掉最高的5%（第二个参数）
    """    
    #print("Searching for return-risk performance based on",ret_measure,"it takes great time, please wait ...")
    
    try:
        df_ret=compare_msecurity(tickers,ret_measure,start,end,graph=False)
    except:
        return None
    cols=list(df_ret)
    
    risk_measure=ret_measure[:-1]+' '+risk_type+'%'
    try:
        df_risk=compare_msecurity(tickers,risk_measure,start,end,graph=False)
    except:
        return None
    
    import pandas as pd
    df=pd.merge(df_ret,df_risk,left_index=True,right_index=True)
    #df.fillna(axis=0,method='ffill',inplace=True)
    #df.fillna(axis=0,method='bfill',inplace=True)
    
    for c in cols:
        df[c]=df[c+'_x']/df[c+'_y']
        
    df2=df[cols]
    
    from scipy.stats.mstats import winsorize
    # 若,ret_measure为Exp类指标，此处需要首行置零
    colList=list(df2)
    index1=df2.head(1).index.values[0]
    for c in colList:
        if 'Exp' in ret_measure:
            df2.loc[df2[df2.index==index1].index.tolist(),c]=0
        
        # 缩尾处理：先转换为数值类型，以防万一
        df2[c]=df2[c].astype('float')
        df2[c]=winsorize(df2[c],limits=winsorize_limits)
            
    #df2.interpolate(method='polynomial',order=2,axis=0,inplace=True)

    y_label="收益-风险性价比"
    
    measure1=ectranslate(ret_measure)[:-1]
    measure2=ectranslate(risk_measure)[:-1]
    footnote1="注：图中的收益-风险性价比定义为"+measure1+"与"+measure2+"之比"
    import datetime; today = datetime.date.today()    
    footnote2="数据来源：新浪财经/雅虎财经/stooq，"+str(today)
    x_label=footnote1+"\n"+footnote2
    
    #title_txt="比较多只证券的简单收益-风险性价比"
    title_txt="收益-风险性价比走势"
    
    print("Rendering graphics ...")
    draw_lines(df2,y_label,x_label,axhline_value=0,axhline_label='',title_txt=title_txt, \
               data_label=False,resample_freq='D',smooth=smooth,annotate=annotate, \
               facecolor=facecolor)

    return df2
        

#==============================================================================
if __name__ =="__main__":
    tickers1=["AMZN","EBAY","SHOP","BABA","JD"]
    tickers2=["AMZN","EBAY","SHOP","BABA","JD","PDD"]
    measure1="Annual Ret%"
    measure2="Exp Ret%"
    start="2022-1-1"
    end="2022-7-31"
    df=compare_msecurity(tickers1,measure1,start,end)
    df=compare_msecurity(tickers1,measure2,start,end)
    
    df=compare_msecurity(tickers2,measure1,start,end)
    df=compare_msecurity(tickers2,measure2,start,end)
#==============================================================================
def stock_Kline(ticker,start='default',end='default',volume=True, \
                style='China',facecolor='whitesmoke', \
                mav=[5,10]):
    """
    套壳函数，为了与stock_MACD等函数相似
    """
    
    #=========== 日期转换与检查
    # 检查日期：截至日期
    import datetime as dt; today=dt.date.today()
    if end in ['default','today']:
        end=today
    else:
        validdate,end=check_date2(end)
        if not validdate:
            print("  #Warning(stock_Kline): invalid date for",end)
            end=today

    # 检查日期：开始日期
    if start in ['default']:
        start=date_adjust(end,adjust=-31)
    else:
        validdate,start=check_date2(start)
        if not validdate:
            print("  #Warning(stock_Kline): invalid date for",start)
            start=date_adjust(todate,adjust=-31)
    
    df=candlestick(stkcd=ticker,fromdate=start,todate=end,volume=volume, \
                   style=style,facecolor=facecolor,mav=mav)
    
    return df

if __name__ =="__main__":
    stkcd="BABA"
    fromdate="2024-5-1"
    todate="2024-6-20"
    volume=True
    style='China'
    mav=[5,10]
    ticker_type='auto'
    facecolor='whitesmoke'
    loc='best'
    
    
    
def candlestick(stkcd,start,end,volume=True,style='China',mav=[5,10], \
                ticker_type='auto',facecolor='whitesmoke',loc='best'):
    """
    功能：绘制证券价格K线图。
    输入：证券代码ticker；开始日期fromdate，结束日期todate；
    绘图类型type：默认为蜡烛图；
    是否绘制交易量volume：默认否；
    绘图风格style：默认为黑白图；
    输出：绘制证券价格蜡烛图线图
    返回：证券价格数据表
    """
    fromdate=start; todate=end
    
    #找出mav的最长天数
    mav_max=0
    for mm in mav:
        # 移除移动平均步数1，否则出错
        if mm == 1:
            mav.remove(mm)
            print("  Warning: moving average at pace=1 is invalid and removed")
            
        if mm > mav_max:
            mav_max=mm
    # 如果mav为空，则默认为2
    if len(mav) == 0:
        mav=[2]

    #延长开始日期，以便绘制长期均线
    #fromdate1=date_adjust(fromdate, adjust=-mav_max*2)
    fromdate1=fromdate
    
    #检查命令参数
    stylelist=['binance','China','blueskies','brasil','charles','checkers','classic','default', \
               'mike','nightclouds','sas','starsandstripes','yahoo']
    if not (style in stylelist):
        print("  #Error(candlestick)，only support graphics styles of",stylelist)
        return
    if style != 'China':
        s = mpf.make_mpf_style(base_mpf_style=style,rc=mpfrc)
    else:
        #按照中国习惯：红涨绿跌
        mc = mpf.make_marketcolors(
            up="red",  # 上涨K线的颜色
            down="green",  # 下跌K线的颜色
            edge="inherit",  # 蜡烛图箱体的颜色
            volume="inherit",  # 成交量柱子的颜色
            wick="inherit"  # 蜡烛图影线的颜色 
            )        
        s = mpf.make_mpf_style(
            #gridaxis='both',
            #gridstyle='-.',
            y_on_right=True,
            marketcolors=mc,
            edgecolor='black',
            figcolor='white',
            facecolor=facecolor, 
            #gridcolor='cyan',
            rc=mpfrc)        
    
    #抓取证券价格
    """
    from siat.security_prices import get_prices_all
    daily=get_prices_all(stkcd,fromdate1,todate,ticker_type=ticker_type)
    """
    from siat.security_price2 import get_price_mticker_mixed
    daily,found=get_price_1ticker_mixed(ticker=stkcd,fromdate=fromdate1, \
                                  todate=todate,ticker_type=ticker_type)
    """
    if daily is None:
        print("  #Error(candlestick): failed to get price info of",stkcd)
        return
    if len(daily) == 0:
        print("  #Warning(candlestick): zero price info to draw K-line for",stkcd)
        return   
    """
    if found == 'None':
        print("  #Error(candlestick): failed to get price info of",stkcd)
        return
    if found == 'Empty':
        print("  #Warning(candlestick): zero price info to draw K-line for",stkcd)
        return   
    
    #如果抓取到的数据没有Volume字段，创造一个但填充为零
    if 'Volume' not in list(daily):
        daily['Volume']=0
    
    #绘制蜡烛图
    ylabel_txt=text_lang('价格','Price')
    ylabel_lower_txt=text_lang('成交量','Volume')
        
    #titletxt=ticker_name(stkcd)
    titletxt=ticker_name(stkcd,ticker_type=ticker_type)
    
    #空一行
    print('')
    
    fig, axlist = mpf.plot(daily,type='candle',
         volume=volume,
         show_nontrading=False,#自动剔除非交易日空白
         style=s,
         #title=titletxt,
         datetime_format='%Y-%m-%d',
         tight_layout=True,
         #tight_layout=False,
         xrotation=15,
         ylabel=texttranslate(ylabel_txt),
         ylabel_lower=texttranslate(ylabel_lower_txt),
         mav=mav,
         figratio=(12.8,7.2),
         #figscale=1.5,
         returnfig=True
         )       
    
    # add a title the the correct axes, 0=first subfigure
    titletxt=titletxt+text_lang("：K线图走势，日移动均线=",": Candlestick Chart, MAV Days=")+str(mav)
    axlist[0].set_title(titletxt,
                        fontsize=16,
                        #style='italic',
                        #fontfamily='fantasy',
                        loc='center')
    
    #设置图例，注意前两个为图中期间开始日期的线和柱子
    mav_labels=[text_lang('期间首日线','Day 1(line)'),text_lang('期间首日柱','Day 1(bar)')]
    #mav_labels=[None,None]
    for d in mav:
        mav_labels=mav_labels+[str(d)+text_lang("日移动均线","-day MAV line")]
    axlist[0].legend(labels=mav_labels,loc=loc)
    #axlist[0].legend(mav_labels[2:],loc=loc)
    """
    #去掉前两个无用的图例
    handles, labels = axlist[0].get_legend_handles_labels()
    axlist[0].legend(handles=handles[2:],labels=labels[2:],loc=loc)
    """
    fig.show()
    reset_plt()
    
    return daily

if __name__ =="__main__":
    stkcd='000002.SZ'
    fromdate='2020-2-1'
    todate='2020-3-10'
    type='candle'
    volume=True
    style='default'
    mav=0
    line=False
    price=candlestick("000002.SZ","2020-2-1","2020-2-29")    

#==============================================================================
def candlestick_pro(stkcd,start,end, \
                    colorup='#00ff00',colordown='#ff00ff',style='nightclouds', \
                    ticker_type='auto'):
    """
    功能：绘制证券价格K线图。
    输入：证券代码ticker；开始日期fromdate，结束日期todate；
    绘图类型type：默认为蜡烛图；
    是否绘制交易量volume：默认否；
    绘图风格style：nightclouds修改版；
    输出：绘制证券价格蜡烛图线图
    返回：证券价格数据表
    注意：可能导致其后的matplotlib绘图汉字乱码
    """
    fromdate=start; todate=end

    #抓取证券价格
    from siat.security_price2 import get_price_1ticker_mixed
    daily,found=get_price_1ticker_mixed(ticker=stkcd,fromdate=fromdate, \
                                        todate=todate,ticker_type=ticker_type)
    
    if found in ['None','Empty']:
        print("  #Error(candlestick_pro): failed to get price info of",stkcd,fromdate,todate)
        return None
   
    #绘制蜡烛图
    #在原有的风格nightclouds基础上定制阳线和阴线柱子的色彩，形成自定义风格s
    mc = mpf.make_marketcolors(up=colorup,down=colordown,inherit=True)
    s  = mpf.make_mpf_style(base_mpf_style=style,marketcolors=mc,rc=mpfrc)
    #kwargs = dict(type='candle',mav=(2,4,6),volume=True,figratio=(10,8),figscale=0.75)
    #kwargs = dict(type='candle',mav=(2,4,6),volume=True,figscale=0.75)
    kwargs = dict(type='candle',mav=5,volume=True)
    
    #titletxt=ticker_name(stkcd)
    titletxt=ticker_name(stkcd,ticker_type=ticker_type)
    
    mpf.plot(daily,**kwargs,
             style=s,
             datetime_format='%Y-%m-%d',
             tight_layout=True,
             xrotation=15,
             title=titletxt,
             ylabel=text_lang("价格","Price"),
             ylabel_lower=text_lang("成交量","Volume"),
             figratio=(12.8,7.2)             
             )       
    reset_plt()
    
    return daily

if __name__ =="__main__":
    stkcd='000002.SZ'
    fromdate='2020-2-1'
    todate='2020-3-10'
    type='candle'
    volume=True
    style='default'
    mav=0
    line=False
    price=candlestick_pro("000002.SZ","2020-2-1","2020-2-29")    
#==============================================================================
def stock_Kline_demo(ticker,start='default',end='default', \
                     colorup='red',colordown='green',width=0.5, \
                     ticker_type='auto',facecolor='whitesmoke'):
    """
    套壳函数，为了与stock_Kline保持一致
    """
    
    #=========== 日期转换与检查
    # 检查日期：截至日期
    import datetime as dt; today=dt.date.today()
    if end in ['default','today']:
        end=today
    else:
        validdate,end=check_date2(end)
        if not validdate:
            print("  #Warning(stock_Kline_demo): invalid date for",end)
            end=today

    # 检查日期：开始日期
    if start in ['default']:
        start=date_adjust(end,adjust=-7)
    else:
        validdate,start=check_date2(start)
        if not validdate:
            print("  #Warning(stock_Kline_demo): invalid date for",start)
            start=date_adjust(todate,adjust=-7)
    
    df=candlestick_demo(stkcd=ticker,fromdate=start,todate=end, \
                        colorup=colorup,colordown=colordown,width=width, \
                        ticker_type=ticker_type,facecolor=facecolor)
    
    return df


if __name__ =="__main__":
    stkcd='BABA'
    fromdate='2023-6-5'
    todate='2023-6-9'
    
    colorup='red';colordown='green';width=0.7
    
def candlestick_demo(stkcd,start,end, \
                     colorup='red',colordown='green',width=0.7, \
                     ticker_type='auto',facecolor='whitesmoke'):
    """
    功能：绘制证券价格K线图，叠加收盘价。
    输入：证券代码ticker；开始日期fromdate，结束日期todate；
    阳线颜色colorup='red'，阴线颜色colordown='green'，柱子宽度width=0.7
    输出：绘制证券价格蜡烛图线图
    返回：证券价格数据表
    """
    fromdate=start; todate=end
    
    #抓取证券价格
    from siat.security_price2 import get_price_1ticker_mixed
    p,found=get_price_1ticker_mixed(ticker=stkcd,fromdate=fromdate, \
                                    todate=todate,ticker_type=ticker_type)    
    if found in ['None','Empty']:
        print("  #Error(candlestick_demo): failed to get prices for:",stkcd,'\b,',fromdate,'-',todate)
        return p 
    
    p['Date']=p.index
    
    import numpy as np
    #b= np.array(p.reset_index()[['Date','Open','High','Low','Close']])
    b= np.array(p[['Date','Open','High','Low','Close']])
    
    #change 1st column of b to number type
    import matplotlib.dates as dt2
    b[:,0] = dt2.date2num(b[:,0])	
    
    print('')
    #specify the size of the graph
    #fig,ax=plt.subplots(figsize=(12.8,6.4))	
    fig,ax=plt.subplots()
    
    #绘制各个价格的折线图
    open_txt=text_lang('开盘价','Open')
    high_txt=text_lang('最高价','High')
    low_txt=text_lang('最低价','Low')
    close_txt=text_lang('收盘价','Close')
    
    plt.plot(p.index,p['Open'],color='green',ls="--",label=open_txt,marker='>',markersize=10,linewidth=2,alpha=0.5)
    plt.plot(p.index,p['High'],color='cyan',ls="-.",label=high_txt,marker='^',markersize=10,linewidth=2,alpha=0.5)
    plt.plot(p.index,p['Low'],color='k',ls=":",label=low_txt,marker='v',markersize=10,linewidth=2,alpha=0.5)
    plt.plot(p.index,p['Close'],color='blue',ls="-",label=close_txt,marker='<',markersize=10,linewidth=2,alpha=0.5)
    
    #绘制蜡烛图
    try:
        from mplfinance.original_flavor import candlestick_ohlc
        #from mplfinance.original_flavor import candlestick2_ohlc
    except:
        print("  #Error(candlestick_demo)： please install plugin mplfinance.")
        print("  Method:")
        print("  In Anaconda Prompt, key in a command: pip install mplfinance")
        return None    
        
    #candlestick_ohlc(ax,b,colorup=colorup,colordown=colordown,width=width,alpha=0.5)
    #candlestick_ohlc(ax,b,colorup=colorup,colordown=colordown,width=width,alpha=0.5)
    # opens, highs, lows, closes 可以是对应的序列，比如 b['open'], b['high']...
    # 画图并拿到返回值
    lines, patches = candlestick_ohlc(
        ax, b,
        colorup=colorup, colordown=colordown,
        width=width, alpha=0.5
    )
    
    # 对每个 Rectangle 补丁设置边框
    for rect in patches:
        rect.set_edgecolor('black')
        rect.set_linewidth(0.8)   # 或你想要的线宽    

    ax.xaxis_date()	#draw dates in x axis
    ax.autoscale_view()
    fig.autofmt_xdate()
    fig.gca().set_facecolor(facecolor)

    titletxt0=text_lang("K线图/蜡烛图演示：","Candlestick Chart Demo: ")
    titletxt=titletxt0 + ticker_name(str(stkcd),ticker_type=ticker_type)
    price_txt=text_lang('价格','Price')
    source_txt=text_lang("数据来源: Sina/EM/Stooq/Yahoo/SWHY","Data source: Sina/Stooq/Yahoo")

    plt.title(titletxt,fontsize=title_txt_size,fontweight='bold')
    plt.ylabel(price_txt,fontsize=ylabel_txt_size)
    
    plt.gcf().autofmt_xdate() # 优化标注（自动倾斜）
    plt.gca().set_facecolor(facecolor)
    #plt.xticks(rotation=30)        
    plt.legend(loc="best",fontsize=legend_txt_size)    
    plt.xlabel(source_txt,fontsize=xlabel_txt_size)   
    plt.show()
    
    return p

if __name__ =="__main__":
    price=candlestick_demo("000002.SZ","2020-3-1","2020-3-6") 

#==============================================================================   
#==============================================================================   
#==============================================================================   
if __name__ =="__main__":
    ticker="000001.SZ"
    fromdate="2021-1-1"
    todate="2022-9-26" 


def security_dividend(ticker,start="L5Y",end="today",facecolor='whitesmoke',fontcolor='black'):
    """
    功能：套壳函数stock_dividend
    """ 
    df=stock_dividend(ticker,start,end,facecolor,fontcolor)
    return df 
    

def stock_dividend(ticker,start="L3Y",end="today",facecolor='whitesmoke',fontcolor='black'):
    """
    功能：显示股票的分红历史
    输入：单一股票代码
    输出：分红历史
    """  
    start,end=start_end_preprocess(start,end)
    
    fromdate,todate=start,end
    
    print("  Searching for dividend info of stock",ticker,"...")
    result,startdt,enddt=check_period(fromdate,todate)
    if not result: 
        print("  #Error(stock_dividend): invalid period",fromdate,todate)
        return None

    result,prefix,suffix=split_prefix_suffix(ticker)
    if result & (suffix=='HK'):
        if len(prefix)==5:
            ticker=ticker[1:]
    
    import yfinance as yf
    stock = yf.Ticker(ticker)
    try:
        div=stock.dividends
    except:
        print(f"  #Error(stock_dividend): dividend info inaccessible for {ticker}")
        return None    
    if len(div)==0:
        print(f"  #Warning(stock_dividend): failed to get dividend info for {ticker}")
        return None      

    # 去掉时区信息，避免合并中的日期时区冲突问题
    import pandas as pd
    div.index = pd.to_datetime(div.index)
    div.index = div.index.tz_localize(None)
    
    #过滤期间
    div1=div[div.index >= startdt]
    div2=div1[div1.index <= enddt]
    if len(div2)==0:
        print(f"  #Warning(stock_dividend): no dividends found from {fromdate} to {todate}")
        return None          
    
    #对齐打印
    import pandas as pd    
    pd.set_option('display.unicode.ambiguous_as_wide', True)
    pd.set_option('display.unicode.east_asian_width', True)
    pd.set_option('display.width', 180) # 设置打印宽度(**重要**)
    pd.set_option('display.colheader_justify', 'center')
    """
    pd.set_option('display.max_columns', 1000)
    pd.set_option('display.width', 1000)
    pd.set_option('display.max_colwidth', 1000)
    """
    divdf=pd.DataFrame(div2)
    divdf['Index Date']=divdf.index
    datefmt=lambda x : x.strftime('%Y-%m-%d')
    divdf['Dividend Date']= divdf['Index Date'].apply(datefmt)
    
    #增加星期
    from datetime import datetime
    weekdayfmt=lambda x : x.isoweekday()
    divdf['Weekdayiso']= divdf['Index Date'].apply(weekdayfmt)
    #wdlist=['Mon','Tue','Wed','Thu','Fri','Sat','Sun']
    #wdlist=['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']
    #wdlist=['星期一','星期二','星期三','星期四','星期五','星期六','星期日']
    wdlist=[text_lang('星期一','Mon'),text_lang('星期二','Tue'),text_lang('星期三','Wed'), \
            text_lang('星期四','Thu'),text_lang('星期五','Fri'),text_lang('星期六','Sat'),text_lang('星期日','Sun')]
    
    wdfmt=lambda x : wdlist[x-1]
    divdf['Weekday']= divdf['Weekdayiso'].apply(wdfmt)
    
    #增加序号
    divdf['Seq']=divdf['Dividend Date'].rank(ascending=1)
    divdf['Seq']=divdf['Seq'].astype('int')
    divprt=divdf[['Seq','Dividend Date','Weekday','Dividends']]
    
    lang=check_language()
    tname=ticker_name(ticker,'stock')
    fromdatey2md=startdt.strftime('%Y/%m/%d')
    todatey2md=enddt.strftime('%Y/%m/%d')

    titletxt=text_lang("证券分红","Stock Dividend")+': '+tname
    periodtxt=text_lang("期间:","Period:")+' '+fromdatey2md+"-"+todatey2md
    #sourcetxt=text_lang("数据来源: 雅虎财经,","Data source: Yahoo Finance,")
    sourcetxt=text_lang("数据来源: Yahoo/Sina","Data source: Yahoo/Sina")
    footnote=periodtxt+'\n'+sourcetxt
    
    #修改列命为英文
    divprt.columns = [text_lang('序号','No.'),text_lang('日期','Date'),text_lang('星期','Weekday'),text_lang('每股(份)红利','Dividend/share')]
    
    """        
    print(divprt.to_string(index=False))   
    """
    #print('') #空一行
    
    df_display_CSS(divprt,titletxt=titletxt,footnote=footnote,facecolor=facecolor,decimals=4, \
                       first_col_align='center',second_col_align='center', \
                       last_col_align='right',other_col_align='center')

    """
    disph=divprt.style.hide() #不显示索引列
    dispp=disph.format(precision=4) #设置带有小数点的列精度调整为小数点后2位
    #设置标题/列名对齐
    dispt=dispp.set_caption(titletxt).set_table_styles(
        [{'selector':'caption', #设置标题
          'props':[('color','black'),('font-size','16px'),('font-weight','bold')]}, \
         {'selector':'th.col_heading', #设置列名
           'props':[('color','black'),('text-align','center'),('margin','auto')]}])        
    #设置列数值对齐
    dispf=dispt.set_properties(**{'text-align':'center'})
    #设置前景背景颜色
    dispf2=dispf.set_properties(**{'background-color':facecolor,'color':fontcolor})

    from IPython.display import display
    display(dispf2)
    
    print(periodtxt)
    import datetime; todaydt=datetime.date.today(); todayy2md=todaydt.strftime('%y/%m/%d')
    #print('\n*** '+sourcetxt,today)
    print(sourcetxt,todayy2md)
    """
    
    return divdf
    
    
if __name__ =="__main__":
    ticker='AAPL'  
    fromdate='2019-1-1'
    todate='2020-6-30'

#==============================================================================
def security_split(ticker,start="L10Y",end="today",facecolor='whitesmoke',fontcolor='black'):
    """
    功能：套壳函数stock_split
    """  
    df=stock_split(ticker,start,end,facecolor,fontcolor)
    return df

   
def stock_split(ticker,start="L10Y",end="today",facecolor='whitesmoke',fontcolor='black'):
    """
    功能：显示股票的分拆历史
    输入：单一股票代码
    输出：分拆历史
    """   
    start,end=start_end_preprocess(start,end)
    
    fromdate,todate=start,end
    
    print("  Searching for split info of stock",ticker,"...")
    result,startdt,enddt=check_period(fromdate,todate)
    if not result: 
        print("  #Error(stock_split): invalid period",fromdate,todate)
        return None

    result,prefix,suffix=split_prefix_suffix(ticker)
    if result & (suffix=='HK'):
        if len(prefix)==5:
            ticker=ticker[1:]
    
    import yfinance as yf
    stock = yf.Ticker(ticker)
    try:
        div=stock.splits
    except:
        print(f"  #Error(stock_split): split info inaccessible for {ticker}")
        return None    
    if len(div)==0:
        print(f"  #Warning(stock_split): no split info found for {ticker}")
        return None      

    # 去掉时区信息，避免合并中的日期时区冲突问题
    import pandas as pd
    div.index = pd.to_datetime(div.index)
    div.index = div.index.tz_localize(None)
    
    #过滤期间
    div1=div[div.index >= startdt]
    div2=div1[div1.index <= enddt]
    if len(div2)==0:
        print("  #Warning(stock_split): no split information in period",fromdate,todate)
        return None          
    
    #对齐打印
    import pandas as pd
    pd.set_option('display.unicode.ambiguous_as_wide', True)
    pd.set_option('display.unicode.east_asian_width', True)
    pd.set_option('display.width', 180) # 设置打印宽度(**重要**)
    """    
    pd.set_option('display.max_columns', 1000)
    pd.set_option('display.width', 1000)
    pd.set_option('display.max_colwidth', 1000)
    """
    divdf=pd.DataFrame(div2)
    divdf['Index Date']=divdf.index
    datefmt=lambda x : x.strftime('%Y-%m-%d')
    divdf['Split Date']= divdf['Index Date'].apply(datefmt)
    
    #增加星期
    from datetime import datetime
    weekdayfmt=lambda x : x.isoweekday()
    divdf['Weekdayiso']= divdf['Index Date'].apply(weekdayfmt)
    #wdlist=['Mon','Tue','Wed','Thu','Fri','Sat','Sun']
    wdlist=[text_lang('星期一','Mon'),text_lang('星期二','Tue'),text_lang('星期三','Wed'), \
            text_lang('星期四','Thu'),text_lang('星期五','Fri'),text_lang('星期六','Sat'),text_lang('星期日','Sun')]
    wdfmt=lambda x : wdlist[x-1]
    divdf['Weekday']= divdf['Weekdayiso'].apply(wdfmt)
    
    #增加序号
    divdf['Seq']=divdf['Split Date'].rank(ascending=1)
    divdf['Seq']=divdf['Seq'].astype('int')
    
    divdf['Splitint']=divdf['Stock Splits'].astype('int')
    splitfmt=lambda x: "1:"+str(x)
    divdf['Splits']=divdf['Splitint'].apply(splitfmt)
    
    divprt=divdf[['Seq','Split Date','Weekday','Splits']]

    lang=check_language()
    tname=ticker_name(ticker,'stock')
    """
    if lang == 'English':
        print('\n======== '+texttranslate("股票分拆历史")+' ========')
        print(texttranslate("股票:"),ticker,'\b,',ticker_name(ticker))
        print(texttranslate("历史期间:"),fromdate,"-",todate)
        divprt.columns=[texttranslate('序号'),texttranslate('日期'),texttranslate('星期'),texttranslate('分拆比例')]
        
        sourcetxt=texttranslate("数据来源: 雅虎财经,")
    else:
        print('\n======== '+"股票分拆历史"+' ========')
        print("股票:",ticker,'\b,',ticker_name(ticker))
        print("历史期间:",fromdate,"-",todate)
        divprt.columns=['序号','日期','星期','分拆比例']
        
        sourcetxt="数据来源: 雅虎财经,"
        
    print(divprt.to_string(index=False))   
    
    import datetime
    today = datetime.date.today()
    print('\n*** '+sourcetxt,today)
    """
    fromdatey2md=startdt.strftime('%Y/%m/%d')
    todatey2md=enddt.strftime('%Y/%m/%d')
    
    titletxt=text_lang("证券分拆","Stock Split")+': '+tname
    periodtxt=text_lang("期间:","Period:")+' '+fromdatey2md+"-"+todatey2md
    
    import datetime; todaydt=datetime.date.today(); todayy2md=str(todaydt.strftime('%y/%m/%d'))
    #sourcetxt=text_lang("数据来源: 雅虎财经, ","Data source: Yahoo Finance, ")+todayy2md
    sourcetxt=text_lang("数据来源: Yahoo/Sina","Data source: Yahoo Finance")
    footnote=periodtxt+'\n'+ sourcetxt
    
    #修改列命为英文
    divprt.columns = [text_lang('序号','No.'),text_lang('日期','Date'),text_lang('星期','Weekday'),text_lang('分拆比例','Split Ratio')]
    """        
    print(divprt.to_string(index=False))   
    """
    print(' ') #空一行
    
    df_display_CSS(divprt,titletxt=titletxt,footnote=footnote,facecolor=facecolor,decimals=2, \
                       first_col_align='center',second_col_align='center', \
                       last_col_align='right',other_col_align='center')
    """
    disph=divprt.style.hide() #不显示索引列
    dispp=disph.format(precision=4) #设置带有小数点的列精度调整为小数点后2位
    #设置标题/列名
    dispt=dispp.set_caption(titletxt).set_table_styles(
        [{'selector':'caption', #设置标题
          'props':[('color','black'),('font-size','16px'),('font-weight','bold')]}, \
         {'selector':'th.col_heading', #设置列名
           'props':[('color','black'),('text-align','center'),('margin','auto')]}])        
    #设置列数值对齐
    dispf=dispt.set_properties(**{'text-align':'center'})
    #设置前景背景颜色
    dispf2=dispf.set_properties(**{'background-color':facecolor,'color':fontcolor})

    from IPython.display import display
    display(dispf2)
    
    print(periodtxt)
    import datetime; todaydt=datetime.date.today(); todayy2md=todaydt.strftime('%y/%m/%d')
    #print('\n*** '+sourcetxt,today)
    print(sourcetxt,todayy2md)
    """
    
    return divdf
    
    
if __name__ =="__main__":
    ticker='AAPL'  
    fromdate='1990-1-1'
    todate='2020-6-30'

#==============================================================================   
#==============================================================================   
#==============================================================================
if __name__=='__main__':
    symbol='AAPL'
    symbol='BABA'
    symbol='01398.HK'
    symbol='03968.HK'
    symbol='601398.SS'

def stock_info(symbol):
    """
    功能：返回静态信息, 基于yahooquery
    尚能工作，不打印
    """
    DEBUG=False
    #print("  Searching for information of",symbol,"\b, please wait...")

    #symbol1=symbol
    result,prefix,suffix=split_prefix_suffix(symbol)
    if result & (suffix=='HK'):
        symbol=prefix[-4:]+'.'+suffix
    
    from yahooquery import Ticker 
    #如果出现类似于{'AAPL': 'Invalid Cookie'}错误，则需要升级yahooquery
    #如果出现crump相关的错误，则需要更换lxml的版本以便与当前的yahooquery版本匹配
    stock = Ticker(symbol)

    """
    Asset Profile:
    Head office address/zip/country, Officers, Employees, industry/sector, phone/fax,
    web site,
    Risk ranks: auditRisk, boardRisk, compensationRisk, overallRisk, shareHolderRightRisk,
    compensationRisk: 薪酬风险。Jensen 及 Meckling (1976)的研究指出薪酬與管理者的風險承擔
    具有關連性，站在管理者的立場來看，創新支出的投入使管理者承受更大的薪酬風險(compensation risk)，
    管理者自然地要求更高的薪酬來補貼所面臨的風險，因此企業創新投資對管理者薪酬成正相關。
    boardRisk: 董事会风险
    shareHolderRightRisk：股权风险
    """
    try:
        #如果出现类似于{'AAPL': 'Invalid Cookie'}错误，则需要升级yahooquery
        adict=stock.asset_profile
    except:
        print("  #Error(stock_info): failed to get info of",symbol)
        print("  Reasons: Wrong stock code, or poor internet connection, or need to upgrade yahooquery")
        return None
    
    if adict[symbol] == 'Invalid Cookie':
        print("  #Error(stock_info): failed in retrieving info of",symbol,"\b. Try upgrade yahooquery and run again")
        return None
    
    keylist=list(adict[symbol].keys())
    import pandas as pd    
    aframe=pd.DataFrame.from_dict(adict, orient='index', columns=keylist)
    ainfo=aframe.T
    info=ainfo.copy()


    """
    ESG Scores: Risk measurements
    peerGroup, ratingYear, 
    environmentScore, governanceScore, socialScore, totalEsg
    dict: peerEnvironmentPerformance, peerGovernancePerformance, peerSocialPerformance, 
    peerEsgScorePerformance
    """
    try:
        adict=stock.esg_scores
    except:
        print("#Error(stock_info): failed to get esg profile of",symbol)
        return None 
    
    if adict[symbol] == 'Invalid Cookie':
        print("  #Error(stock_info): failed in retrieving info of",symbol)
        return None
    
    try:    #一些企业无此信息
        keylist=list(adict[symbol].keys())
        aframe=pd.DataFrame.from_dict(adict, orient='index', columns=keylist)
        ainfo=aframe.T
        info=pd.concat([info,ainfo])
    except:
        pass

    """
    Financial Data: TTM???
    currentPrice, targetHighPrice, targetLowPrice, targetMeanPrice, targetMedianPrice, 
    currentRatio, debtToEquity, earningsGrowth, ebitda, ebitdaMargins, financialCurrency,
    freeCashflow, grossMargins, grossProfits, 
    operatingCashflow, operatingMargins, profitMargins,
    quickRatio, returnOnAssets, returnOnEquity, revenueGrowth, revenuePerShare, 
    totalCash, totalCashPerShare, totalDebt, totalRevenue, 
    """
    try:
        adict=stock.financial_data
    except:
        print("  #Error(stock_info): failed to get financial profile of",symbol)
        return None    
    
    if adict[symbol] == 'Invalid Cookie':
        print("  #Error(stock_info): failed in retrieving info of",symbol)
        return None
    
    keylist=list(adict[symbol].keys())
    aframe=pd.DataFrame.from_dict(adict, orient='index', columns=keylist)
    ainfo=aframe.T
    info=pd.concat([info,ainfo])    
    

    """
    Key Statistics: TTM???
    52WeekChang, SandP52WeekChang, beta, floatShares, sharesOutstanding, 
    bookValue, earningsQuarterlyGrowth, enterpriseToEbitda, enterpriseToRevenue,
    enterpriseValue, netIncomeToCommon, priceToBook, profitMargins, 
    forwardEps, trailingEps,
    heldPercentInsiders, heldPercentInstitutions, 
    lastFiscalYearEnd, lastSplitDate, lastSplitFactor, mostRecentQuarter, nextFiscalYearEnd,
    """
    try:
        adict=stock.key_stats
    except:
        print("  #Error(stock_info): failed to get key stats of",symbol)
        return None
    
    if adict[symbol] == 'Invalid Cookie':
        print("  #Error(stock_info): failed in retrieving info of",symbol)
        return None
    
    keylist=list(adict[symbol].keys())
    aframe=pd.DataFrame.from_dict(adict, orient='index', columns=keylist)
    ainfo=aframe.T
    info=pd.concat([info,ainfo]) 
    
    
    """
    Price Information:
    currency, currencySymbol, exchange, exchangeName, shortName, 
    longName, 
    marketCap, marketState, quoteType, 
    regularMarketChange, regularMarketChangPercent, regularMarketHigh, regularMarketLow, 
    regularMarketOpen, regularMarketPreviousClose, regularMarketPrice, regularMarketTime,
    regularMarketVolume, 
    """
    try:
        adict=stock.price
    except:
        print("  #Error(stock_info): failed to get stock prices of",symbol)
        return None 
    
    if adict[symbol] == 'Invalid Cookie':
        print("  #Error(stock_info): failed in retrieving info of",symbol)
        return None
    
    keylist=list(adict[symbol].keys())
    aframe=pd.DataFrame.from_dict(adict, orient='index', columns=keylist)
    ainfo=aframe.T
    info=pd.concat([info,ainfo]) 
    

    """
    Quote Type:
    exchange, firstTradeDateEpocUtc(上市日期), longName, quoteType(证券类型：股票), 
    shortName, symbol(当前代码), timeZoneFullName, timeZoneShortName, underlyingSymbol(原始代码), 
    """
    try:
        adict=stock.quote_type
    except:
        print("  #Error(stock_info): failed to get quote type of",symbol)
        return None  
    
    if adict[symbol] == 'Invalid Cookie':
        print("  #Error(stock_info): failed in retrieving info of",symbol)
        return None
    
    keylist=list(adict[symbol].keys())
    aframe=pd.DataFrame.from_dict(adict, orient='index', columns=keylist)
    ainfo=aframe.T
    info=pd.concat([info,ainfo]) 
    

    """
    Share Purchase Activity
    period(6m), totalInsiderShares
    """
    try:
        adict=stock.share_purchase_activity
    except:
        print("  #Error(stock_info): failed to get share purchase of",symbol)
        return None  
    
    if adict[symbol] == 'Invalid Cookie':
        print("  #Error(stock_info): failed in retrieving info of",symbol)
        return None
    
    keylist=list(adict[symbol].keys())
    aframe=pd.DataFrame.from_dict(adict, orient='index', columns=keylist)
    ainfo=aframe.T
    info=pd.concat([info,ainfo]) 


    """
    # Summary detail
    averageDailyVolume10Day, averageVolume, averageVolume10days, beta, currency, 
    dayHigh, dayLow, fiftyDayAverage, fiftyTwoWeekHigh, fiftyTwoWeekLow, open, previousClose, 
    regularMarketDayHigh, regularMarketDayLow, regularMarketOpen, regularMarketPreviousClose, 
    regularMarketVolume, twoHundredDayAverage, volume, 
    forwardPE, marketCap, priceToSalesTrailing12Months, 
    dividendRate, dividendYield, exDividendDate, payoutRatio, trailingAnnualDividendRate,
    trailingAnnualDividendYield, trailingPE, 
    """
    try:
        adict=stock.summary_detail
    except:
        print("  #Error(stock_info): failed to get summary detail of",symbol)
        return None   
    
    if adict[symbol] == 'Invalid Cookie':
        print("  #Error(stock_info): failed in retrieving info of",symbol)
        return None
    
    keylist=list(adict[symbol].keys())
    aframe=pd.DataFrame.from_dict(adict, orient='index', columns=keylist)
    ainfo=aframe.T
    info=pd.concat([info,ainfo]) 

    
    """
    summary_profile
    address/city/country/zip, phone/fax, sector/industry, website/longBusinessSummary, 
    fullTimeEmployees, 
    """
    try:
        adict=stock.summary_profile
    except:
        print("  #Error(stock_info): failed to get summary profile of",symbol)
        print("  Possible reasons:","\n  1.Wrong stock code","\n  2.Instable data source, try later")
        return None  
    
    if adict[symbol] == 'Invalid Cookie':
        print("  #Error(stock_info): failed in retrieving info of",symbol)
        return None
    
    keylist=list(adict[symbol].keys())
    aframe=pd.DataFrame.from_dict(adict, orient='index', columns=keylist)
    ainfo=aframe.T
    info=pd.concat([info,ainfo]) 
    

    # 清洗数据项目
    info.sort_index(inplace=True)   #排序
    
    import numpy as np
    colList=list(info)
    info[colList[0]]=info[colList[0]].apply(lambda x: np.nan if x==[] else x)
    info.dropna(inplace=True)   #去掉空值
    #去重
    info['Item']=info.index
    info.drop_duplicates(subset=['Item'],keep='first',inplace=True)
    
    #删除不需要的项目
    delrows=['adult','alcoholic','animalTesting','ask','askSize','bid','bidSize', \
             'catholic','coal','controversialWeapons','furLeather','gambling', \
                 'gmo','gmtOffSetMilliseconds','militaryContract','messageBoardId', \
                     'nuclear','palmOil','pesticides','tobacco','uuid','maxAge']
    for r in delrows:
       info.drop(info[info['Item']==r].index,inplace=True) 
    
    #修改列名
    info.rename(columns={symbol:'Value'}, inplace=True) 
    del info['Item']
    
    return info


if __name__=='__main__':
    info=stock_info('AAPL')
    info=stock_info('BABA')

#==============================================================================
if __name__=='__main__':
    info=stock_info('AAPL')

def stock_basic(info):
    
    wishlist=['sector','industry','quoteType', \
              #公司地址，网站
              'address1','address2','city','state','country','zip','phone','fax', \
              'website', \
              
              #员工人数
              'fullTimeEmployees', \
              
              #上市与交易所
              'exchangeName', \
              
              #其他
              'currency']
        
    #按照wishlist的顺序从info中取值
    rowlist=list(info.index)
    import pandas as pd
    info_sub=pd.DataFrame(columns=['Item','Value'])
    infot=info.T
    for w in wishlist:
        if w in rowlist:
            v=infot[w][0]
            s=pd.Series({'Item':w,'Value':v})
            try:
                info_sub=info_sub.append(s,ignore_index=True)
            except:
                info_sub=info_sub._append(s,ignore_index=True)
    
    return info_sub

if __name__=='__main__':
    basic=stock_basic(info)    

#==============================================================================
if __name__=='__main__':
    info=stock_info('AAPL')

def stock_officers(info):
    
    wishlist=['sector','industry','currency', \
              #公司高管
              'companyOfficers', \
              ]
        
    #按照wishlist的顺序从info中取值
    rowlist=list(info.index)
    import pandas as pd
    info_sub=pd.DataFrame(columns=['Item','Value'])
    infot=info.T
    for w in wishlist:
        if w in rowlist:
            v=infot[w][0]
            s=pd.Series({'Item':w,'Value':v})
            try:
                info_sub=info_sub.append(s,ignore_index=True)
            except:
                info_sub=info_sub._append(s,ignore_index=True)
    
    return info_sub

if __name__=='__main__':
    sub_info=stock_officers(info)    

#==============================================================================
def stock_risk_general(info):
    
    wishlist=['sector','industry', \
              
              'overallRisk','boardRisk','compensationRisk', \
              'shareHolderRightsRisk','auditRisk'
              ]
        
    #按照wishlist的顺序从info中取值
    rowlist=list(info.index)
    import pandas as pd
    info_sub=pd.DataFrame(columns=['Item','Value'])
    infot=info.T
    for w in wishlist:
        if w in rowlist:
            v=infot[w][0]
            s=pd.Series({'Item':w,'Value':v})
            try:
                info_sub=info_sub.append(s,ignore_index=True)
            except:
                info_sub=info_sub._append(s,ignore_index=True)
    
    return info_sub

if __name__=='__main__':
    risk_general=stock_risk_general(info)    

#==============================================================================
def stock_risk_esg(info):
    """
    wishlist=[
              'peerGroup','peerCount','percentile','esgPerformance', \
              'totalEsg','peerEsgScorePerformance', \
              'environmentScore','peerEnvironmentPerformance', \
              'socialScore','peerSocialPerformance','relatedControversy', \
              'governanceScore','peerGovernancePerformance'
              ]
    """
    wishlist=[
              'peerGroup','peerCount','percentile', \
              'totalEsg','peerEsgScorePerformance', \
              'environmentScore','peerEnvironmentPerformance', \
              'socialScore','peerSocialPerformance','relatedControversy', \
              'governanceScore','peerGovernancePerformance'
              ]
    
    #按照wishlist的顺序从info中取值
    rowlist=list(info.index)
    import pandas as pd
    info_sub=pd.DataFrame(columns=['Item','Value'])
    infot=info.T
    for w in wishlist:
        if w in rowlist:
            v=infot[w][0]
            s=pd.Series({'Item':w,'Value':v})
            try:
                info_sub=info_sub.append(s,ignore_index=True)
            except:
                info_sub=info_sub._append(s,ignore_index=True)
    
    return info_sub

if __name__=='__main__':
    risk_esg=stock_risk_esg(info)  
    
#==============================================================================
def stock_fin_rates(info):
    
    wishlist=['financialCurrency', \
              
              #偿债能力
              'currentRatio','quickRatio','debtToEquity', \
                  
              #盈利能力
              #'ebitdaMargins','operatingMargins','grossMargins','profitMargins', \
              'operatingMargins','profitMargins', \
                  
              #股东回报率
              'returnOnAssets','returnOnEquity', \
              'dividendRate','trailingAnnualDividendRate','trailingEps', \
              'payoutRatio','revenuePerShare','totalCashPerShare', \
              
              #业务发展能力
              #'revenueGrowth','earningsGrowth','earningsQuarterlyGrowth'
              'revenueGrowth','earningsQuarterlyGrowth',
              ]
        
    #按照wishlist的顺序从info中取值
    rowlist=list(info.index)
    import pandas as pd
    info_sub=pd.DataFrame(columns=['Item','Value'])
    infot=info.T
    for w in wishlist:
        if w in rowlist:
            v=infot[w][0]
            s=pd.Series({'Item':w,'Value':v})
            try:
                info_sub=info_sub.append(s,ignore_index=True)
            except:
                info_sub=info_sub._append(s,ignore_index=True)
    
    return info_sub

if __name__=='__main__':
    fin_rates=stock_fin_rates(info) 

#==============================================================================
def stock_fin_statements(info):
    
    wishlist=['financialCurrency','lastFiscalYearEnd','mostRecentQuarter','nextFiscalYearEnd', \
              
              #资产负债
              #'marketCap','totalAssets','totalDebt', \
              'marketCap', \
                  
              #利润表
              'totalRevenue','grossProfits','ebitda','netIncomeToCommon', \
                  
              #现金流量
              'operatingCashflow','freeCashflow','totalCash', \
              
              #股票数量
              'sharesOutstanding','totalInsiderShares'
              ]

    datelist=['lastFiscalYearEnd','mostRecentQuarter','nextFiscalYearEnd']
        
    #按照wishlist的顺序从info中取值
    rowlist=list(info.index)
    import pandas as pd
    info_sub=pd.DataFrame(columns=['Item','Value'])
    infot=info.T
    for w in wishlist:
        if w in rowlist:
            if not (w in datelist):
                v=infot[w][0]
            else:
                v=infot[w][0][0:10]
                
            s=pd.Series({'Item':w,'Value':v})
            try:
                info_sub=info_sub.append(s,ignore_index=True)
            except:
                info_sub=info_sub._append(s,ignore_index=True)
    
    return info_sub

if __name__=='__main__':
    fin_statements=stock_fin_statements(info) 

#==============================================================================
def stock_market_rates(info):
    
    wishlist=['beta','currency', \
              
              #市场观察
              'priceToBook','priceToSalesTrailing12Months', \
              
              #市场风险与收益
              '52WeekChange','SandP52WeekChange', \
              'trailingEps','forwardEps','trailingPE','forwardPE','pegRatio', \
              
              #分红
              'dividendYield', \
                  
              #持股
              'heldPercentInsiders','heldPercentInstitutions', \
              
              #股票流通
              'sharesOutstanding','currentPrice',
              'targetHighPrice','targetMeanPrice','targetMedianPrice','targetLowPrice',
              'numberOfAnalystOpinions',
              #'recommendationKey',
              ]
        
    #按照wishlist的顺序从info中取值
    rowlist=list(info.index)
    import pandas as pd
    info_sub=pd.DataFrame(columns=['Item','Value'])
    infot=info.T
    for w in wishlist:
        if w in rowlist:
            v=infot[w][0]
            s=pd.Series({'Item':w,'Value':v})
            try:
                info_sub=info_sub.append(s,ignore_index=True)
            except:
                info_sub=info_sub._append(s,ignore_index=True)
    
    return info_sub

if __name__=='__main__':
    market_rates=stock_market_rates(info) 

#==============================================================================
if __name__=='__main__':
    ticker='AAPL'
    ticker='00700.HK'
    ticker='03968.HK'
    ticker='01398.HK'
    
    info_type='fin_rates' 

    ticker='FIBI.TA'
    info_type='officers' 

def get_stock_profile(ticker,info_type='basic',printout=True):
    """
    功能：抓取和获得股票的信息
    basic: 基本信息
    officers：管理层
    fin_rates: 财务比率快照
    fin_statements: 财务报表快照
    market_rates: 市场比率快照
    risk_general: 一般风险快照
    risk_esg: 可持续发展风险快照（有些股票无此信息）
    """
    #print("\nSearching for snapshot info of",ticker,"\b, please wait...")

    typelist=['basic','officers','fin_rates','fin_statements','market_rates','risk_general','risk_esg']    
    if info_type not in typelist:
        print("  #Sorry, info_type not supported for",info_type)
        print("  Supported info_type:\n",typelist)
        return None
    
    #应对各种出错情形：执行出错，返回NoneType，返回空值
    try:
        info=stock_info(ticker)
    except:
        print("  #Warning(get_stock_profile): recovering info for",ticker,"...")
        import time; time.sleep(5)
        try:
            info=stock_info(ticker)
        except:
            print("  #Error(get_stock_profile): failed to access Yahoo for",ticker)
            return None
    if info is None:
        print("  #Error(get_stock_profile): retrieved none info of",ticker)
        print(f"  Solution: if {ticker} is correct, try again later!")
        return None
    if len(info) == 0:
        print("  #Error(get_stock_profile): retrieved empty info of",ticker)
        return None    
    """
    #处理公司短名字    
    name0=info.T['shortName'][0]
    name1=name0.split('.',1)[0] #仅取第一个符号.以前的字符串
    name2=name1.split(',',1)[0] #仅取第一个符号,以前的字符串
    name3=name2.split('(',1)[0] #仅取第一个符号(以前的字符串
    #name4=name3.split(' ',1)[0] #仅取第一个空格以前的字符串
    #name=ticker_name(name4)  #去掉空格有名字错乱风险
    name9=name3.strip()
    name=ticker_name(name9)   #从短名字翻译
    """
    if not printout: return info
    
    footnote=''
    name=ticker_name(ticker)  #从股票代码直接翻译
    if info_type in ['basic']:
        sub_info=stock_basic(info)
        info_text="公司基本信息"
    
    if info_type in ['officers']:
        sub_info=stock_officers(info)
        info_text="公司高管信息"
    
    if info_type in ['fin_rates']:
        sub_info=stock_fin_rates(info)
        info_text="基本财务比率TTM"
    
    if info_type in ['fin_statements']:
        sub_info=stock_fin_statements(info)
        info_text="财报主要项目"
    
    if info_type in ['market_rates']:
        sub_info=stock_market_rates(info)
        info_text="基本市场指标"
    
    if info_type in ['risk_general']:
        sub_info=stock_risk_general(info)
        info_text="一般风险评估"
        footnote="注：数值越小风险越低，最高10分"
    
    if info_type in ['risk_esg']:
        info_text="ESG风险评估"
        footnote="注：分数越小风险越低，最高100分"
        sub_info=stock_risk_esg(info)
        if len(sub_info)==0:
            print("  \n#Warning: ESG info not available for",ticker)
            return None
    
    # 显示信息
    lang=check_language()
    if lang == 'Chinese':    
        titletxt="===== "+name+": "+info_text+" =====\n"
        if len(footnote) > 0:
            footnote1='\n'+footnote
        else:
            footnote1=footnote
    else:
        titletxt="===== "+name+": "+texttranslate(info_text)+" =====\n"
        
        if len(footnote) > 0:
            footnote1='\n'+texttranslate(footnote)
        else:
            footnote1=footnote
        
    printdf(sub_info,titletxt,footnote1)
    
    return info

if __name__=='__main__':
    info=get_stock_profile(ticker,info_type='basic')
    info=get_stock_profile(ticker,info_type='officers')
    info=get_stock_profile(ticker,info_type='fin_rates')
    info=get_stock_profile(ticker,info_type='fin_statements')
    info=get_stock_profile(ticker,info_type='market_rates')
    info=get_stock_profile(ticker,info_type='risk_general')
    info=get_stock_profile(ticker,info_type='risk_esg')

#==============================================================================

def stock_snapshot(ticker='AAPL',info_type="all"):
    """
    功能：打印指定选项，套壳函数get_stock_profile
    """
    print("  Connecting to Yahoo Finance ... ...")
    typelist=['basic',
              'officers',
              'fin_rates',
              'fin_statements',
              'market_rates',
              'risk_general',
              'risk_esg'] 
    
    if info_type.lower() !="all" and info_type.lower() in typelist:
        info=get_stock_profile(ticker,info_type=info_type)
        return
    
    if info_type.lower() =="all":
        for t in typelist:
            info=get_stock_profile(ticker,info_type=t)    
            
            if info is None:
                break
        return
    else:
        print("  #Error(stock_snapshot): unsupported info type",info_type)
        print("  Supporting",typelist)
        return
        

def security_snapshot(ticker='AAPL'):
    """
    功能：一次性打印所有选项，套壳函数get_stock_profile
    """
    print("  Try connecting to Yahoo Finance ... ...")
    typelist=['basic',
              'officers',
              'fin_rates',
              'fin_statements',
              'market_rates',
              'risk_general',
              'risk_esg'] 
    for t in typelist:
        info=get_stock_profile(ticker,info_type=t)    
        
        if info is None:
            break
        
    return
#==============================================================================
if __name__=='__main__':
    ticker='AAPL'
    info=stock_info(ticker)
    sub_info=stock_basic(info)
    titletxt="===== "+ticker+": Snr Management ====="

def printdf(sub_info,titletxt,footnote):
    """
    功能：整齐显示股票信息快照，翻译中文，按照中文项目长度计算空格数
    """
    print("\n"+titletxt)

    for index,row in sub_info.iterrows():
        
        #----------------------------------------------------------------------
        #特殊打印：高管信息
        if row['Item']=="companyOfficers":
            print_companyOfficers(sub_info)
            continue
        
        #特殊打印：ESG同行状况
        peerlist=["peerEsgScorePerformance","peerEnvironmentPerformance", \
                 "peerSocialPerformance","peerGovernancePerformance"]
        if row['Item'] in peerlist:
            print_peerPerformance(sub_info,row['Item'])
            continue

        #特殊打印：ESG Social风险内容
        if row['Item']=="relatedControversy":
            print_controversy(sub_info,row['Item'])
            continue
        #----------------------------------------------------------------------

        print_item(row['Item'],row['Value'],10)
    
    import datetime; todaydt=datetime.date.today().strftime("%y-%m-%d")
    lang=check_language()
    if lang == 'Chinese':
        print(footnote+"\n数据来源: 雅虎/Sustainalytics,",todaydt)
    else:
        print(footnote+"\nSource: Yahoo/Sustainalytics,",todaydt)
    
    return

if __name__=='__main__':
    printdf(sub_info,titletxt)

#==============================================================================
if __name__=='__main__':
    item='currentPrice'
    value='110.08'
    maxlen=10
    
def print_item(item,value,maxlen):
    """
    功能：打印一个项目和相应的值，中间隔开一定空间对齐
    限制：只区分字符串、整数和浮点数
    """
    DEBUG=False
    
    print(ectranslate(item)+': ',end='')
    
    directprint=['zip','ratingYear','ratingMonth']
    if item in directprint:
        if DEBUG: print("...Direct print")
        print(value)
        return
    
    #是否整数
    if isinstance(value,int):
        if DEBUG: print("...Integer: ",end='')
        if value != 0:
            print(format(value,','))
        else:
            #print('---')
            print('0')
        return
    
    #是否浮点数
    ZERO=0.00001
    if isinstance(value,float):
        if DEBUG: print("...Float: ",end='')
        if value < 1.0: 
            value1=round(value,4)
        else:
            value1=round(value,2)
        if value <= -ZERO or value >= ZERO:
            print(format(value1,','))
        else:
            #print('---')
            print('0.0')
        return  
    
    #是否字符串
    if not isinstance(value,str):
        print(str(value))
    
    #是否字符串表示的整数
    if value.isdigit():
        value1=int(value)
        if DEBUG: print("...Integer in string: ",end='')
        if value1 != 0:
            print(format(value1,','))
        else:
            #print('---')
            print('0')
        return          
    
    #是否字符串表示的浮点数
    try:
        value1=float(value)
        if value1 < 1.0:
            value2=round(value1,4)
        else:
            value2=round(value1,2)
        if DEBUG: print("...Float in string")
        if value1 <= -ZERO or value1 >= ZERO:
            print(format(value2,','))
        else:
            #print('---')
            print('0.0')
    except:
        #只是字符串
        if DEBUG: print("...String")
        print(value)       
    
    return

if __name__=='__main__':
    print_item('currentPrice','110.08',10)
    
#==============================================================================
if __name__=='__main__':
    str1='哈哈哈ROA1'

def str_len(str1):
    """
    功能：计算中英文混合字符串的实际占位长度，不太准
    """
    len_d=len(str1)
    len_u=len(str1.encode('utf_8'))
    
    num_ch=(len_u - len_d)/2
    num_en=len_d - num_ch    
    totallen=int(num_ch*2 + num_en)
    
    return totallen

if __name__=='__main__':
    str_len('哈哈哈ROA1')

#==============================================================================
if __name__=='__main__':
    info=stock_info('AAPL')
    sub_info=stock_officers(info)

def print_companyOfficers(sub_info):
    """
    功能：打印公司高管信息
    """
    item='companyOfficers'
    
    lang=check_language()
    if lang == 'English':
        itemtxt=texttranslate('公司高管:')
    else:
        itemtxt='公司高管:'
        
    key1='name'
    key2='title'
    key3='yearBorn'
    key4='age'
    
    key6='totalPay'
    key7='fiscalYear'
    currency=list(sub_info[sub_info['Item'] == 'currency']['Value'])[0]
    alist=list(sub_info[sub_info['Item'] == item]['Value'])[0]
    
    print(itemtxt)
    if len(alist)==0:
        print("  #Warning(print_companyOfficers): company officer info not available")
    
    import datetime as dt; today=dt.date.today()
    thisyear=int(str(today)[:4])
    for i in alist:
        
        #测试是否存在：姓名，职位，出生年份
        try:
            ikey1=i[key1]
            ikey2=i[key2]
            ikey3=i[key3]
        except:
            continue
        ikey4=thisyear-ikey3
        print(' '*4,ikey1)    
        print(' '*8,ikey2,'\b,',ikey4,texttranslate('\b岁 (生于')+str(ikey3)+')')    
        
        #测试是否存在：薪酬信息
        try:
            ikey6=i[key6]
            ikey7=i[key7]
            if ikey6 > 0:
                print(' '*8,texttranslate('总薪酬'),currency+str(format(ikey6,',')),'@'+str(ikey7))
        except:
            continue
    return

if __name__=='__main__':
    print_companyOfficers(sub_info)

#==============================================================================
if __name__=='__main__':
    info=stock_info('AAPL')
    sub_info=stock_risk_esg(info)
    item="peerEsgScorePerformance"

def print_peerPerformance(sub_info,item):
    """
    功能：打印ESG信息
    """
    
    key1='min'
    key2='avg'
    key3='max'
    i=list(sub_info[sub_info['Item'] == item]['Value'])[0]
    
    """
    print(ectranslate(item)+':')
    print(' '*4,key1+':',i[key1],'\b,',key2+':',round(i[key2],2),'\b,',key3+':',i[key3])
    """
    print(ectranslate(item)+': ',end='')
    print(texttranslate("均值")+str(round(i[key2],2)),end='')
    print(" ("+str(i[key1])+'-'+str(i[key3])+")")
    
    return

if __name__=='__main__':
    print_peerPerformance(sub_info,item)

#==============================================================================
if __name__=='__main__':
    info=stock_info('AAPL')
    sub_info=stock_risk_esg(info)
    item='relatedControversy'

def print_controversy(sub_info,item):
    """
    功能：打印ESG Social风险内容
    """
    alist=list(sub_info[sub_info['Item'] == item]['Value'])[0]
    if len(alist)==0:
        print("  #Error(print_controversy): no relevant info found.")    
    
    print(ectranslate(item)+':')
    for i in alist:
        print(' '*4,ectranslate(i))
        
    return

if __name__=='__main__':
    print_controversy(sub_info,item)

#==============================================================================
if __name__ =="__main__":
    stocklist=["BAC", "TD","PNC"]
    
def get_esg2(stocklist):
    """
    功能：根据股票代码列表，抓取企业最新的可持续性发展ESG数据
    输入参数：
    stocklist：股票代码列表，例如单个股票["AAPL"], 多只股票["AAPL","MSFT","GOOG"]
    输出参数：    
    企业最新的可持续性发展ESG数据，数据框
    """
    
    import pandas as pd
    collist=['symbol','totalEsg','environmentScore','socialScore','governanceScore']
    sust=pd.DataFrame(columns=collist)
    for t in stocklist:
        try:
            info=stock_info(t).T
        except:
            print("  #Error(get_esg2): esg info not available for",t)
            continue
        if (info is None) or (len(info)==0):
            print("  #Error(get_esg2): failed to get esg info for",t)
            continue
        sub=info[collist]
        sust=pd.concat([sust,sub])
    
    newcols=['Stock','ESGscore','EPscore','CSRscore','CGscore']
    sust.columns=newcols
    """
    sust=sust.rename(columns={'symbol':'Stock','totalEsg':'ESGscore', \
                         'environmentScore':'EPscore', \
                             'socialScore':'CSRscore', \
                                 'governanceScore':'CGscore'})
    """
    sust.set_index('Stock',inplace=True)
    
    return sust

if __name__ =="__main__":
    sust=get_esg2(stocklist)

#==============================================================================
#==============================================================================
def portfolio_esg2(portfolio):
    """
    功能：抓取、打印和绘图投资组合portfolio的可持续性发展数据，演示用
    输入参数：
    企业最新的可持续性发展数据，数据框    
    """
    #解构投资组合
    _,_,stocklist,_,ticker_type=decompose_portfolio(portfolio)
    
    #抓取数据
    try:
        sust=get_esg2(stocklist)
    except:
        print("  #Error(portfolio_esg): fail to get ESG data for",stocklist)
        return None
    if sust is None:
        #print("#Error(portfolio_esg), fail to get ESG data for",stocklist)
        return None
        
    #处理小数点
    from pandas.api.types import is_numeric_dtype
    cols=list(sust)    
    for c in cols:
        if is_numeric_dtype(sust[c]):
            sust[c]=round(sust[c],2)        
            
    #显示结果
    print(texttranslate("\n===== 投资组合的ESG风险评估 ====="))
    print(texttranslate("投资组合:"),stocklist)
    #显示各个成分股的ESG分数
    sust['Stock']=sust.index
    esgdf=sust[['Stock','ESGscore','EPscore','CSRscore','CGscore']]
    print(esgdf.to_string(index=False))
    
    print("\n"+texttranslate("ESG评估分数:"))
    #木桶短板：EPScore
    esg_ep=esgdf.sort_values(['EPscore'], ascending = True)
    p_ep=esg_ep['EPscore'][-1]
    p_ep_stock=esg_ep.index[-1]   
    str_ep=texttranslate("   EP分数(基于")+str(p_ep_stock)+ticker_name(str(p_ep_stock))+")"
    len_ep=hzlen(str_ep)

    #木桶短板：CSRScore
    esg_csr=esgdf.sort_values(['CSRscore'], ascending = True)
    p_csr=esg_csr['CSRscore'][-1]
    p_csr_stock=esg_csr.index[-1] 
    str_csr=texttranslate("   CSR分数(基于")+str(p_csr_stock)+ticker_name(str(p_csr_stock))+")"
    len_csr=hzlen(str_csr)
    
    #木桶短板：CGScore
    esg_cg=esgdf.sort_values(['CGscore'], ascending = True)
    p_cg=esg_cg['CGscore'][-1]
    p_cg_stock=esg_cg.index[-1]     
    str_cg=texttranslate("   CG分数(基于")+str(p_cg_stock)+ticker_name(str(p_cg_stock))+")"
    len_cg=hzlen(str_cg)

    str_esg=texttranslate("   ESG总评分数")
    len_esg=hzlen(str_esg)
    
    #计算对齐冒号中间需要的空格数目
    len_max=max(len_ep,len_csr,len_cg,len_esg)
    str_ep=str_ep+' '*(len_max-len_ep+1)+':'
    str_csr=str_csr+' '*(len_max-len_csr+1)+':'
    str_cg=str_cg+' '*(len_max-len_cg+1)+':'
    str_esg=str_esg+' '*(len_max-len_esg+1)+':'
    
    #对齐打印
    print(str_ep,p_ep)
    print(str_csr,p_csr)    
    print(str_cg,p_cg)      
    #计算投资组合的ESG综合风险
    p_esg=round(p_ep+p_csr+p_cg,2)
    print(str_esg,p_esg)

    import datetime as dt; today=dt.date.today()
    footnote=texttranslate("注：分数越高, 风险越高.")+"\n"+texttranslate("数据来源：雅虎，")+str(today)
    print(footnote)
    
    return p_esg

if __name__ =="__main__":
    #market={'Market':('China','^HSI')}
    market={'Market':('US','^GSPC')}
    #stocks={'0939.HK':2,'1398.HK':1,'3988.HK':3}
    stocks={'VIPS':3,'JD':2,'BABA':1}
    portfolio=dict(market,**stocks)
    esg=portfolio_esg(portfolio)
#==============================================================================

if __name__ =="__main__":
    ticker='AAPL'
    measures=['High','Low',"Open",'Close']
    fromdate='2022-7-1'
    todate='2022-12-1'
    
    axhline_value=0
    axhline_label=''
    linewidth=1.5
    graph=True
    
    df=compare_mmeasure(ticker,measures,fromdate,todate)
    
    measures=['Daily Ret%',"Monthly Ret%",'Annual Ret%']
    df=compare_mmeasure(ticker,measures,fromdate,todate)
    
    measures=['Daily Ret%',"Exp Ret%",'Annual Ret%']
    df=compare_mmeasure(ticker,measures,fromdate,todate,axhline_value=0,axhline_label='零线')
    
    
def compare_mmeasure(ticker,measures,fromdate,todate, \
                     axhline_value=0,axhline_label='',linewidth=1.5, \
                     graph=True,smooth=True):
    """
    功能：绘制单证券多指标对比图
    """
    #检查期间的合理性
    result,startpd,endpd=check_period(fromdate,todate)
    if not result:
        print("  #Error(compare_mmeasure): invalid date period from",fromdate,"to",todate)
        return None
    
    ticker1=ticker.upper()
    #fromdate1=date_adjust(fromdate,adjust=-365)
    fromdate1=fromdate
    #抓取行情，并计算其各种期间的收益率
    df1a=stock_ret(ticker1,fromdate1,todate,graph=False)
    if df1a is None: 
        print("  #Error(compare_mmeasure): no price info found for",ticker,"from",fromdate,"to",todate)
        return None
    
    #加入价格波动指标
    df1b=price_volatility2(df1a,ticker1,fromdate1,todate,graph=False)
    #加入收益率波动指标
    df1c=ret_volatility2(df1b,ticker1,fromdate1,todate,graph=False)
    #加入收益率下偏标准差指标
    df1d=ret_lpsd2(df1c,ticker1,fromdate1,todate,graph=False)
    
    #去掉开始日期以前的数据
    df2=df1d[(df1d.index >= startpd) & (df1d.index <= endpd)]
    
    #提取绘图指标
    collist=[]; collist_notfound=[]
    dflist=list(df2)
    for m in measures:
        if m in dflist:
            collist=collist+[m]
        else:
            collist_notfound=collist_notfound+[m]
    if len(collist)==0:
        print("  #Error(compare_mmeasure): no measure info found for",ticker,"from",fromdate,"to",todate)
        return None
    
    if len(collist_notfound)>0:
        print("  #Warning(compare_mmeasure): unsupported measure(s) found ",collist_notfound)

    df3=pd.DataFrame(df2[collist])
    for c in collist:
        df3.rename(columns={c:ectranslate(c)},inplace=True)
    
    # 填充非交易日的缺失值，使得绘制的曲线连续
    df3.fillna(axis=0,method='ffill',inplace=True)
    #df3.fillna(axis=0,method='bfill',inplace=True)

    #绘制单个证券的多指标对比图
    y_label=''
    import datetime; today = datetime.date.today()
    
    x_label=text_lang("数据来源: Sina/EM/Stooq/Yahoo/SWHY，","Data source: Sina/Yahoo/Stooq/EM, ")+str(today)
    title_txt=text_lang("证券趋势分析：","Security Trend: ")+ticker_name(ticker)
        
    draw_lines(df3,y_label=y_label,x_label=x_label, \
               axhline_value=axhline_value,axhline_label=axhline_label, \
               title_txt=title_txt, \
               data_label=False,resample_freq='H',smooth=smooth,linewidth=linewidth)
    
    return df3

#==============================================================================
#==============================================================================
#==============================================================================
#==============================================================================
#==============================================================================   
def fix_mac_hanzi_plt():
    """
    功能：修复MacOSX中matplotlib绘图时汉字的乱码问题，安装SimHei.ttf字体
    注意：本函数未经测试，弃用
    """
    #判断当前的操作系统
    import platform
    pltf=platform.platform()
    os=pltf[0:5]    
    if not (os == "macOS"):
        print("#Warning(fix_mac_hanzi_plt): This command is only valid for MacOSX.")    
        return

    #查找模块的安装路径
    import os
    import imp
    dir1=imp.find_module('siat')[1]        
    dir2=imp.find_module('matplotlib')[1]

    #查找matplotlib的字体地址
    pltttf=dir2+'/mpl-data/fonts/ttf'    

    #复制字体文件
    cpcmd="cp -r "+dir1+"/SimHei.ttf "+pltttf
    result=os.popen(cpcmd)    

    #修改配置文件内容
    import matplotlib
    pltrc=matplotlib.matplotlib_fname()

    line1='\nfont.family : sans-serif\n'
    line2='font.sans-serif : SimHei,DejaVu Sans,Bitstream Vera Sans,Lucida Grande,Verdana,Geneva,Lucid,Arial,Helvetica,Avant Garde,sans-serif\n'
    line3='axes.unicode_minus : False\n'

    filehandler=open(pltrc,'a')
    filehandler.write(line1)
    filehandler.write(line2)
    filehandler.write(line3)
    filehandler.close()

    from matplotlib.font_manager import _rebuild
    _rebuild()
    print("  Fixed Mac Hanzi problems for matplotlib graphics!")
    print("  Please RESTART Python kernel to make it effective!")
    
    return



















