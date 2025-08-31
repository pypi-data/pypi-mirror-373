# -*- coding: utf-8 -*-
"""
版权：王德宏，北京外国语大学国际商学院
功能：
1、获取证券价格，多种方法，解决不稳定网络超时问题
2、既可获取单一证券的价格，也可获取证券组合的价格
3、与爬虫过程有关的错误信息尽可能都在本过程中处理
版本：1.0，2021-1-31
"""

#==============================================================================
#关闭所有警告
import warnings; warnings.filterwarnings('ignore')
from siat.common import *
from siat.translate import *

#==============================================================================
import pandas as pd

#==============================================================================
#==============================================================================
if __name__=='__main__':
    ticker="430047.BJ"
    ticker="430047.BJ"
    ticker="600519.SS"
    ticker="000858.SZ"
    ticker_type='auto'
    
    ticker="sz169107" #LOF基金
    ticker="sh510050" #ETF基金
    
    
    ticker="sh010504" #国债
    ticker_type='bond'
    
    ticker='801002.SW'
    ticker_type='auto'
    
    ticker={'Market':('China','000001.SS','白酒组合'),'600519':0.4,'000858':0.6}
    
    fromdate="2024-1-1"
    todate="2024-4-1"
    adj=False
    retry_count=3
    pause=1
    source='auto'
    
    prices=get_prices_all(ticker,fromdate,todate,ticker_type=ticker_type)

def get_prices_all(ticker,fromdate,todate,adj=False,source='auto',ticker_type='auto'):
    """
    功能：多个证券(股票，指数，基金，债券)，或投资组合(可含股票和/或债券)
    ticker_type：若为'auto'则基金优先于债券(代码重合时)，亦可为列表分别指定优先抓取类型。
    'stock', 'fund', 'bond','swindex','portfolio'，不足部分自动补充为'auto'
    其中，'auto'/'stock'/'fund'优先抓取指数、股票和基金；'bond'优先抓取债券；
    'swindex'优先抓取申万行业指数
    
    注意：未经充分测试！！！
    """
    
    #补足ticker_type
    if isinstance(ticker_type,str):
        ticker_type_list=[ticker_type]
    
    if isinstance(ticker,str) or isinstance(ticker,dict):
        ticker_list=[ticker]
        
    ticker_num=len(ticker_list)
    ticker_type_len=len(ticker_type_list)
    if ticker_num > ticker_type_len:
        ticker_type_list=ticker_type_list + ['auto'*(ticker_type_len - ticker_num)]

    #单个证券的特殊处理
    if ticker_num == 1:
        #普通证券
        if isinstance(ticker_list[0],str):
            df=get_prices(ticker_list[0],fromdate,todate,adj=adj,source=source,ticker_type=ticker_type_list[0])

        #投资组合            
        if isinstance(ticker_list[0],dict):
            _,_,tickerlist,sharelist,ticker_type=decompose_portfolio(ticker_list[0])
            df=get_price_portfolio(tickerlist,sharelist,fromdate,todate,adj=adj, \
                                    source=source,ticker_type=ticker_type)
        return df

    #多个证券
    df=pd.DataFrame()        
    for t in ticker_list:
        pos=ticker_list.index(t)
        tt=ticker_type_list[pos]
        
        #普通证券
        if isinstance(t,str):
            dft=get_prices(t,fromdate,todate,adj=adj,source=source,ticker_type=tt)

        #投资组合            
        if isinstance(t,dict):
            _,_,tickerlist,sharelist,ticker_type=decompose_portfolio(t)
            dft=get_price_portfolio(tickerlist,sharelist,fromdate,todate,adj=adj, \
                                    source=source,ticker_type=ticker_type)
            t=portfolio_name(t)
            
        columns=create_tuple_for_columns(dft,t)
        dft.columns=pd.MultiIndex.from_tuples(columns)
        
        if len(df)==0:
            df=dft
        else:
            #合并
            df=pd.merge(df,dft,how='outer',left_index=True,right_index=True)
    
    return df

#==============================================================================
if __name__=='__main__':
    ticker="430047.BJ"
    ticker="430047.BJ"
    ticker="600519.SS"
    ticker="000858.SZ"
    ticker_type='auto'
    
    ticker="sz169107" #LOF基金
    ticker="sh510050" #ETF基金
    
    ticker="sh010504" #国债
    ticker_type='bond'
    
    ticker='801002.SW'
    ticker_type='auto'
    
    ticker=['600519','000858']
    ticker_type='bond'
    
    ticker='GEM25.CME'
    
    ticker=['^SPX']
    
    fromdate="2025-1-1"
    todate="2025-6-1"
    adj=False
    retry_count=3
    pause=1
    source='auto'
    ticker_type='auto'

    prices=get_prices(ticker,fromdate,todate,ticker_type=ticker_type)

def get_prices(ticker,fromdate,todate,adj=False,source='auto', \
               retry_count=3,pause=1,ticker_type='auto'):
    """
    功能：抓取证券价格，pandas_datareader + yfinance + akshare
    输出：指定收盘价格序列，日期升序排列
    ticker: 证券代码或其列表。大陆证券代码加上后缀.SZ或.SS或.BJ，港股代码去掉前导0加后缀.HK
    start: 样本开始日期，yyyy-mm-dd
    end: 样本结束日期，既可以是今天日期，也可以是一个历史日期
    retry_count：网络失败时的重试次数，仅用于雅虎
    pause：每次重试前的间隔秒数，仅用于雅虎
    """
    # yfinance可用性
    YF=False
    # pandas_datareader对yahoo可用性
    PDR_yahoo=False
    
    prices=None
    
    #检查日期期间的合理性
    result,start,end=check_period(fromdate,todate)
    if not result:
        print("  #Error(get_prices): invalid date period from",fromdate,'to',todate)
        return None     
    
    print("  Searching prices of security, please wait ...")
    ticker=tickers_cvt2yahoo(ticker)

    if source in ['auto']:
        #尝试AkShare+Sina+EM（新浪，对中国内地股票、港股和美股有效，但不包括国外市场指数）
        print("  Trying to capture prices from sina/EM for",ticker,"...")
        try:
            prices=get_prices_ak(ticker,fromdate,todate,ticker_type=ticker_type) #支持多个证券
        except:
            print("    #Warning(get_prices): info retrieving failed from sina/EM for",ticker)
        else:
            if prices is None: 
                print("    #Warning(get_prices): info not found from sina/EM for",ticker)
            else:
                num=len(prices)
                if num==0:
                    print("    #Warning(get_prices):",ticker,"may be suspended or delisted")
                    return prices
                else:
                    prices2=remove_timezone(prices)
                    #prices2=remove_df_index_timezone(prices)
                    return prices2 #找到有效数据就返回，否则继续       

    if source in ['auto','stooq']:
        #尝试pandas_datareader+stooq（对美股、港股、欧股、国外市场指数有效，但对深交所股票无效）
        #注意stooq代码与新浪/stooq的不同
        print("  Trying to capture info from stooq for",ticker)
        try:
            prices=get_prices_stooq(ticker,fromdate,todate) #仅支持单只证券
            #prices=get_prices_stooq(ticker,fromdate,todate)?
        except:
            print("    #Warning(get_prices): info retrieving failed from stooq for",ticker)
        else:
            if prices is None: 
                print("    #Warning(get_prices): info not found from stooq for",ticker)
            else:
                num=len(prices)
                if num==0:
                    print("    #Warning(get_prices): zero record found for",ticker)
                else:
                    prices2=remove_timezone(prices)
                    #prices2=remove_df_index_timezone(prices)
                    return prices2 #找到有效数据就返回，否则继续      

    if source in ['auto','yahoo']:
        #使用yahoo+yfinance抓取数据                
        #由于雅虎无法访问，建议暂时关闭，2021-10-24
        #抓取证券（列表）价格，需要调整收盘价：yfinance优先，线程极易出错，先尝试关闭线程
        try:
            if YF:
                print("  Trying to capture info from Yahoo Finance using non-threads")
                prices=get_prices_yf(ticker,start,end,threads=False) #支持多个证券
            else:
                print("  Trying to capture info from Yahoo Finance ...")
                prices=get_prices_yq(ticker,start,end)
                
        except:
            print("    #Warning(get_prices): retrieving using non-threads failed from yahoo")
        else:
            if prices is None: 
                print("    #Warning(get_prices): info not found using non-threads failed from yahoo")
            else:
                num=len(prices)
                if num==0:
                    print("    #Warning(get_prices): zero record found")
                else:
                    prices2=remove_timezone(prices)
                    #prices2=remove_df_index_timezone(prices)
                    return prices2 #找到有效数据就返回，否则继续      

        #抓取证券（列表）价格，需要调整收盘价：yfinance优先，尝试打开线程
        try:
            if YF:
                print("  Trying to capture info from Yahoo Finance using threads")
                prices=get_prices_yf(ticker,start,end,threads=True) #支持多个证券
        except:
            print("    #Warning(get_prices): retrieving using threads failed from yahoo")
        else:
            if prices is None: 
                print("    #Warning(get_prices): info not found using non-threads failed from yahoo")
            else:
                num=len(prices)
                if num==0:
                    print("    #Warning(get_prices): zero record found")
                else:
                    prices2=remove_timezone(prices)
                    #prices2=remove_df_index_timezone(prices)
                    return prices2 #找到有效数据就返回，否则继续        
    
        #抓取证券（列表）价格，不考虑是否需要调整收盘价：pandas_datareader，使用雅虎
        try:    
            print("  Trying to capture info from Yahoo Finance traditionally")
            if PDR_yahoo:
                prices=get_prices_yahoo(ticker,start,end,retry_count=retry_count,pause=pause)
        except:    
            print("    #Warning(get_prices): info retrieving failed from Yahoo traditionally")    
            return None    
        else:
            if prices is None: 
                print("    #Warning(get_prices): info not found  from Yahoo traditionally")
            else:
                num=len(prices)
                if num==0:
                    print("    #Warning(get_prices): zero record found from Yahoo traditionally")
                else:
                    #print("  Successfully retrieved",num,"records for",ticker)
                    prices2=remove_timezone(prices)
                    #prices2=remove_df_index_timezone(prices)
                    return prices2        
    
    #若能够抓取到数据均已提前返回，到达此处时表面未能抓取到任何数据
    print("  #Warning(get_prices): tried everything but nothing found for",ticker)
    
    return None

if __name__=='__main__':
    get_prices('INTC','2021-11-1','2021-11-5')
    get_prices('BMW.DE','2021-11-1','2021-11-5')
    get_prices(['INTC'],'2021-11-1','2021-11-5')
    get_prices(['XYZ'],'2021-11-1','2021-11-5')
    df4=get_prices(['INTC','MSFT'],'2021-11-1','2021-11-5')
    df5=get_prices(['INTC','UVW'],'2021-11-1','2021-11-5')
    df6=get_prices(['00988.HK','000858.SZ'],'2021-11-1','2021-11-5')
    df7=get_prices(['INTL','MSFT','00988.HK','000858.SZ'],'2021-11-1','2021-11-5')

#==============================================================================

def get_price(ticker,fromdate,todate,adj=False,source='auto',ticker_type='auto'):
    """
    套壳函数get_prices，为保持兼容
    """
    df=get_prices(ticker,fromdate,todate,adj=adj,source=source,ticker_type=ticker_type)
    
    df2=remove_timezone(df)
    #df2=remove_df_index_timezone(df)
    
    return df2

#==============================================================================
if __name__ =="__main__":
    ticker="BMW.DE"
    fromdate="2023-1-1"
    todate="2023-5-20"
    
    ticker=["600519.SS",'000858.SZ']
    pricedf=get_prices(ticker,fromdate,todate)
    
def remove_timezone(pricedf):
    """
    功能：去掉df索引中可能存在的时区信息，避免时区错误
    """
    if pricedf is None:
        return None
    
    import datetime as dt
    import pandas as pd

    pricedf.index=pd.Series(pd.to_datetime(pricedf.index)).dt.tz_localize(None)  
    
    return pricedf
    
def remove_timezone_tmp(pricedf):
    """
    功能：去掉df索引中可能存在的时区信息，避免时区错误
    注意：有问题，应该改用common中的df_index_timezone_remove函数
    """
    #去掉时区
    pricedf2=df_index_timezone_remove(pricedf)    
    return pricedf2

    """
    if pricedf is None:
        return pricedf
    
    pricedf['date_tz']=pricedf.index
    pricedf['date_y4m2d2']=pricedf['date_tz'].astype(str)
    
    import pandas as pd
    pricedf['date']=pricedf['date_y4m2d2'].apply(lambda x: pd.to_datetime(x))
    pricedf2=pricedf.reset_index(drop=True)
    try:
        pricedf2=pricedf2.set_index('Date',drop=True)
    except:
        pricedf2=pricedf2.set_index('date',drop=True)
        
    pricedf2.drop(['date_tz','date_y4m2d2'],axis=1,inplace=True)
    
    return pricedf2
    """
    
#==============================================================================
if __name__=='__main__':
    ticker='430047.BJ'
    ticker='600519.SS'
    ticker='000001.SZ'
    
    ticker='GEM25.CME'
    
    fromdate='2025-1-1'
    todate='2025-6-15'
    
    adjust=''; ticker_type='auto'
    
    get_price_ak_em(ticker,fromdate,todate)

#在common中定义SUFFIX_LIST_CN

def get_price_ak_em(ticker,fromdate,todate,adjust='',ticker_type='auto'):
    """
    功能：基于东方财富从akshare获得中国国内的股票和指数历史行情，只能处理单个股票，处理指数有时出错
    ticker：雅虎格式，沪市股票为.SS，深市为.SZ，北交所为.BJ，其他的不处理，直接返回None
    fromdate：格式为YYYY-m-d，需要改造为YYYYMMDD
    todate：格式为YYYY-m-d，需要改造为YYYYMMDD
    adjust：不考虑复权为''，后复权为'hfq'，前复权为'qfq'
    返回结果：雅虎格式，日期升序，列明首字母大写等
    
    缺陷：处理指数容易出错或返回错误数据！！！
    """
    #变换代码格式
    ticker1=ticker.upper()
    result,prefix,suffix=split_prefix_suffix(ticker1)
    
    #若不是A股则返回
    if not (suffix in SUFFIX_LIST_CN):
        print("  #Warning(get_price_ak_em): function not suitable for",ticker)
        return None
    else:
        ticker2=prefix
    
    #变换日期格式
    result,start,end=check_period(fromdate,todate)
    if not result:
        print("  #Warning(get_price_ak_em): invalid date period from",fromdate,'to',todate)
        return None   
    start1=start.strftime('%Y%m%d')
    end1=end.strftime('%Y%m%d')
    
    #检查复权选项
    adjustlist=['','none','hfq','qfq']
    if adjust not in adjustlist:
        print("  #Warning(get_price_ak_em): invalid close adjustment",adjust)
        return None          
    if adjust=='none': adjust=''
    
    #抓取股价，含复权选项
    import akshare as ak
    try:
        #bug: 股票代码为399xxx时出错
        df=ak.stock_zh_a_hist(symbol=ticker2,period="daily",start_date=start1,end_date=end1,adjust=adjust)
    except:
        print("  #Warning(get_price_ak_em): failed to find prices from EM for",ticker)
        return None
    
    #检查抓取到的结果
    if df is None:
        print("  #Warning(get_price_ak_em): no record found from EM for",ticker)
        return None
    if len(df)==0:
        print("  #Warning(get_price_ak_em): zero record found from EM for",ticker)
        return None

    #升序排序
    df.sort_values(by=['日期'],ascending=[True],inplace=True)
    
    #调整数据格式
    df['Date']=pd.to_datetime(df['日期'])
    df.set_index(['Date'],inplace=True)

    df.rename(columns={'开盘':'Open','收盘':'Close','最高':'High','最低':'Low', \
                       '成交量':'Volume','成交额':'Amount','换手率':'Turnover'},inplace=True)
    df1=df[['Open','Close','High','Low','Volume','Amount','Turnover']]
    
    df1['source']=text_lang('东方财富','EM')
    df1['ticker']=str(ticker)
    df1['Adj Close']=df1['Close']
    df1['footnote']=adjust   
    
    num=len(df1)
    """
    ptname=ticker_name(ticker,ticker_type)
    if ptname == ticker: ptname=''
    """
    if num > 0:
        #print("  Successfully retrieved",num,"records for",ticker,ptname)
        print("  Successfully retrieved",num,"records for",ticker)
    else:
        #print("  Sorry, no records retrieved for",ticker,ptname)
        print("  Sorry, no records retrieved for",ticker)

    return df1
    

if __name__=='__main__':
    df1=get_price_ak_em('600519.SS','2020-12-1','2020-12-5',adjust='none')
    df2=get_price_ak_em('600519.SS','2020-12-1','2021-2-5',adjust='hfq')
    df3=get_price_ak_em('399001.SZ','2020-12-1','2021-2-5') #出错
    df4=get_price_ak_em('000688.SS','2020-12-1','2021-2-5')
    df5=get_price_ak_em('AAPL','2020-12-1','2021-2-5')
    df6=get_price_ak_em('000001.SS','2020-12-1','2021-2-5')
    df7=get_price_ak_em('000002.SS','2020-12-1','2021-2-5')
    df7=get_price_ak_em('000300.SS','2020-12-1','2021-2-5')

#==============================================================================
def cvt_stooq_suffix(symbol):
    """
    映射雅虎后缀符号至stooq后缀符号
    输入：雅虎后缀符号。输出：stooq后缀符号
    """
    import pandas as pd
    suffix=pd.DataFrame([
        ['SS','CN'], ['SH','CN'], ['SZ','CN'], ['BJ','CN'], 
        ['T','JP'],['L','UK'], 
        
        ], columns=['yahoo','stooq'])

    try:
        stooq=suffix[suffix['yahoo']==symbol]['stooq'].values[0]
    except:
        #未查到翻译词汇，返回原词
        stooq=symbol
   
    return stooq

if __name__=='__main__':
    cvt_stooq_suffix('SS')
    cvt_stooq_suffix('SZ')
    cvt_stooq_suffix('T')
#==================================================================================
def cvt_stooq_symbol(symbol):
    """
    映射雅虎指数符号至stooq指数符号
    输入：雅虎指数符号。输出：stooq指数符号
    注意：^IXIC/^NDQ是纳斯达克综合指数，^NDX是纳斯达克100指数
    """
    import pandas as pd
    suffix=pd.DataFrame([
        ['^GSPC','^SPX'], ['^IXIC','^NDQ'],  
        ['^RUT','QR.F'],
        ['000001.SS','^SHC'],  
        ['^N225','^NKX'], ['^TWII','^TWSE'], ['^KS11','^KOSPI'],
        ['^BSESN','^SNX'],['^FTSE','^FTM'], ['^GDAXI','^DAX'],
        ['^FCHI','^CAC'], ['IMOEX.ME','^MOEX'], 
        
        ], columns=['yahoo','stooq'])

    result=True
    try:
        stooq=suffix[suffix['yahoo']==symbol]['stooq'].values[0]
    except:
        #未查到翻译词汇，返回原词
        stooq=symbol
   
    return result,stooq

if __name__=='__main__':
    cvt_stooq_symbol('^GSPC')
    cvt_stooq_symbol('^IXIC')
    cvt_stooq_symbol('000001.SS')
    cvt_stooq_symbol('600619.SS')
    
#==================================================================================
if __name__=='__main__':
    ticker='600519.SS'
    ticker='0LNG.L'
    
    cvt_stooq_ticker(ticker)

def cvt_stooq_ticker(ticker):
    """
    映射雅虎证券符号至stooq证券符号
    输入：雅虎证券符号。输出：stooq证券符号
    局限：无法处理深交所股票代码！stooq里没有深交所股票
    """
    #直接转换
    result,ticker_stooq=cvt_stooq_symbol(ticker)
    if not result:
        return ticker_stooq
    
    #拆分前缀后缀
    result,prefix,suffix=split_prefix_suffix(ticker)
    
    #去掉前导0
    prefix2=prefix.lstrip('0')
    
    #无后缀
    if not result:
        _,ticker_stooq=cvt_stooq_symbol(prefix2)
        
    #有后缀
    if result:
        _,prefix3=cvt_stooq_symbol(prefix2)
        ticker_stooq=prefix3+'.'+cvt_stooq_suffix(suffix)
        
    return ticker_stooq    

if __name__=='__main__':
    cvt_stooq_ticker('^GSPC')   
    cvt_stooq_ticker('000001.SS') 
    cvt_stooq_ticker('0700.HK') 
    
    #有问题
    cvt_stooq_ticker('002504.SZ')
#==============================================================================
if __name__=='__main__':
    ticker='1YCNY.B'
    start='2025-7-1'; end='2025-7-21'
    
    market_RF("1YCNY.B")
    
def market_RF(ticker='1YCNY.B',start='MRW',end='today',printout=True):
    """
    功能：获取一个经济体市场的无风险收益率，以国债收益率替代。
        默认1年期国债收益率最近一周的均值    
    """
    start,end=start_end_preprocess(start,end)
    
    #屏蔽函数内print信息输出的类
    import os, sys
    class HiddenPrints:
        def __enter__(self):
            self._original_stdout = sys.stdout
            sys.stdout = open(os.devnull, 'w')

        def __exit__(self, exc_type, exc_val, exc_tb):
            sys.stdout.close()
            sys.stdout = self._original_stdout

    with HiddenPrints():    
        RFdf=get_price_stooq(ticker,start=start,end=end)

    if RFdf is None:
        print(f"  #Error(market_RF): yield {ticker} not found or unavailable in the period")
        return None
    
    RF=round(RFdf['Close'].mean()/100,6)

    if printout:
        print(f"  Proxy: {ticker1_name(ticker).replace('(B)','')}")
        print(f"  {round(RF*100,4)}% in average from {start} to {end}")

    return RF

#==============================================================================

if __name__=='__main__':
    ticker='AAPL'
    ticker='^HSI'
    ticker='^GSPC'
    ticker='^DJI'
    ticker='000001.SS'
    ticker='00700.HK'
    ticker='IBM'
    ticker='0LNG.UK'
    ticker='CNYUSD'
    ticker='CPIYCN.M'
    ticker='INPYCN.M'
    ticker='TRBNCN.M'
    ticker='RSAYCN.M'
    ticker='600519.SS'
    
    ticker='GC.F'   #无法下载
    ticker='XAUCNY' #一盎司黄金的现货人民币价格
    ticker='XAUUSD' #一盎司黄金的现货美元价格
    
    ticker=['AAPL','MSFT']
    start='2025-6-1'; end='2025-6-1' 
    
    ticker='BMW.DE'
    start='2022-6-1'; end='2025-6-15' 
    
    ticker='GEM25.CME'
    start='2024-6-1'; end='2025-6-15' 
    
    p=get_price_stooq(ticker,start,end)

def get_price_stooq(ticker,start='MRM',end='today'):
    """
    从stooq抓取单个股价
    """
    start,end=start_end_preprocess(start,end)
    
    #转换证券代码
    ticker2=cvt_stooq_ticker(ticker)
    
    #从stooq抓取每日价格
    import pandas_datareader.data as web
    """
    #尝试重指向pandas_datareader中的stooq.py为siat中的stooq.py
    import importlib
    import siat
    importlib.reload(siat.stooq)
    """
    try:
        prices=web.DataReader(ticker2,start=start,end=end,data_source='stooq')
    except:
        symbol_parts = ticker2.split(".")
        if len(symbol_parts) == 1:
            ticker2 = ".".join([ticker2, 'US']) #若出错尝试当作美股代码处理，挽救第一次
            prices=web.DataReader(ticker2,start=start,end=end,data_source='stooq')
        else:
            print("  #Warning(get_price_stooq): inaccessible from stooq for",ticker)
            return None
    
    #添加附注
    if not (prices is None):
        if len(prices)==0:
            symbol_parts = ticker2.split(".")
            if len(symbol_parts) == 1:
                ticker2 = ".".join([ticker2, 'US']) #若为空尝试当作美股代码处理，挽救第二次
                prices=web.DataReader(ticker2,start=start,end=end,data_source='stooq')
            else:            
                #print("  Sorry, zero records found from stooq for",ticker,"from",start,'to',end)
                return None   
            
            #仍然无记录
            if len(prices)==0:return None
            
        prices.sort_index(axis=0, ascending=True, inplace=True)
        #prices.dropna(inplace=True)
        
        prices['Adj Close']=prices['Close']
        prices['source']='Stooq'
        prices['ticker']=str(ticker)
        prices['footnote']=''
        
        if 'Volume' not in list(prices):
            prices['Volume']=0
        
        _,start1,end1=check_period(start,end)
        prices2=prices[(prices.index >= start1) & (prices.index <= end1)]
        
        num=len(prices2)
        """
        ptname=ticker_name(ticker,'stock')
        if ptname == ticker: ptname=''
        """
        if num > 0:
            print("  Successfully retrieved",num,"records for",ticker)
            return prices2
        else:
            print("  Sorry, no records found from stooq for",ticker,"from",start,'to',end)
            return None   
    else:
        return None
    
if __name__=='__main__':
    get_price_stooq('AAPL','2021-11-1','2021-11-5')    
    get_price_stooq('BMW.DE','2021-11-1','2021-11-5')
    hsi=get_price_stooq('^HSI','2021-11-1','2021-11-5')
    get_price_stooq('0700.HK','2021-11-1','2021-11-5')
    get_price_stooq('^N225','2021-11-1','2021-11-5')
    get_price_stooq('^DJI','2021-11-1','2021-11-5')    

#==============================================================================
if __name__=='__main__':
    ticker=['AAPL','MSFT']
    ticker=['^SPX']
    fromdate,todate='2025-1-1','2025-1-31'
    
    prices=get_prices_stooq(ticker,fromdate,todate)

def get_prices_stooq(ticker,fromdate,todate):
    """
    功能：获取stooq股票或指数的历史行情，多个股票
    注意：stooq不能抓取深交所和北交所的股票
    """
    #检查是否为多个证券:单个证券代码
    if isinstance(ticker,str):
        if security_in_China(ticker):
            df=get_price_ak(ticker,fromdate,todate)
        else:
            df=get_price_stooq(ticker,fromdate,todate)
        return df
    
    #检查是否为多个证券:空的列表
    if isinstance(ticker,list) and len(ticker) == 0:
        pass
        return None        
    
    #检查是否为多个证券:列表中只有一个代码
    if isinstance(ticker,list) and len(ticker) == 1:
        ticker1=ticker[0]
        #抓取单个证券
        if security_in_China(ticker1):
            df=get_price_ak(ticker1,fromdate,todate)
        else:
            df=get_price_stooq(ticker1,fromdate,todate)
        return df       
    
    import pandas as pd
    #处理列表中的第一个证券
    i=0
    df=None
    while df is None:
        #注意列表序号超界
        if i <= len(ticker)-1:
            t=ticker[i]
        else:
            return df

        #抓取单个证券
        if security_in_China(t):
            df=get_price_ak(t,fromdate,todate)
        else:
            df=get_price_stooq(t,fromdate,todate)
            
        if not (df is None):
            columns=create_tuple_for_columns(df,t)
            df.columns=pd.MultiIndex.from_tuples(columns)
        else:
            i=i+1
            
    if (i+1) == len(ticker):
        pass
        #已经到达代码列表末尾
        return df
        
    #处理列表中的其余证券
    if i+1 <= len(ticker)-1:
        for t in ticker[(i+1):]:
            #抓取单个证券
            if security_in_China(t):
                df=get_price_ak(t,fromdate,todate)
            else:
                df=get_price_stooq(t,fromdate,todate)
                
            if not (dft is None):
                columns=create_tuple_for_columns(dft,t)
                dft.columns=pd.MultiIndex.from_tuples(columns)
            
                df=pd.merge(df,dft,how='inner',left_index=True,right_index=True)
     
    return df


#==============================================================================
if __name__=='__main__':
    ticker='600340.SS'
    ticker='000338.SZ'
    ticker='600519.SS'
    ticker_type='auto'
    
    ticker='859811.SW'
    ticker_type='auto'
    
    fromdate='2024-1-1'
    todate='2024-4-1'
    adjust='none'
    
    df=get_price_ak(ticker,fromdate,todate,ticker_type=ticker_type)

#在common中定义SUFFIX_LIST_CN

def get_price_ak(ticker,fromdate,todate,adjust='none',ticker_type='auto'):
    """
    功能：基于akshare抓取A股、港股和美股单只股价
    若抓取A股，调用get_price_ak_cn
    若抓取港股，调用get_price_ak_hk
    若抓取美股，调用get_price_ak_us
    
    注意：忽略了复权价格
    """
    #提取交易所后缀
    ticker1=ticker.upper()
    result,prefix,suffix=split_prefix_suffix(ticker1)
    
    df=pd.DataFrame()
    # A股股票、指数、基金、债券，申万行业指数
    if suffix in SUFFIX_LIST_CN:
        try:
            #抓取单个中国的证券
            df=get_price_ak_cn(ticker1,fromdate,todate,ticker_type=ticker_type)
        except:
            #抓取东方财富，处理股指有时出错，所以要放在后面做planB
            df=get_price_ak_em(ticker1,fromdate,todate)
        
        if df is None:
            print("    #Error(get_price_ak): no info found for",ticker1)
            return df
            
        if len(df) ==0:
            print("    #Warning(get_price_ak): no record found for",ticker1,'between',fromdate,todate)
            return df
            
        return df

    if adjust=='none':
        adjust=''
        
    #抓取新浪港股，不能处理股指
    if suffix in ['HK']:
        #df=get_price_ak_hk(ticker,fromdate,todate,adjust=adjust)
        df=get_price_ak_hk(ticker1,fromdate,todate)
        return df   
    
    # 美股，不能处理股指
    #df=get_price_ak_us(ticker,fromdate,todate,adjust=adjust)
    df=get_price_ak_us(ticker1,fromdate,todate)
    
    return df 

#==============================================================================
if __name__=='__main__':
    ticker='600340.SS' #股票
    ticker='159990.SZ' #ETF基金
    ticker='169201.SZ' #LOF基金
    ticker='180801.SZ' #封闭式基金
    
    ticker="006257"
    
    ticker_type='auto'
    
    ticker='sh019319' #国债
    ticker='sh018084' #政策性金融债
    ticker='sz149996' #公司债
    ticker='sh018003' #政策性金融债
    ticker_type='bond'
    
    ticker='801002.SW'
    ticker='807110.SW'
    
    ticker='sz100303'
    ticker='100303.SZ'
    ticker_type='auto'
    
    ticker='000418'
    ticker='180202.SZ'
    ticker_type='fund'
    
    fromdate='2024-1-1'; todate='2024-3-31'
    adjust=''
    
    prices=get_price_ak_cn(ticker,fromdate,todate)

#def get_price_ak_cn(ticker,fromdate,todate,adjust='none',ticker_type='auto'):
def get_price_ak_cn(ticker,fromdate,todate,adjust='',ticker_type='auto'):
    """
    功能：从akshare获得中国国内的股票、交易所基金、指数和债券历史行情，只能处理单个证券
    ticker：雅虎格式，其他的不处理，直接返回None
    fromdate：格式为YYYY-m-d，需要改造为YYYYMMDD
    todate：格式为YYYY-m-d，需要改造为YYYYMMDD
    adjust：不复权为''，后复权为'hfq'，前复权为'qfq'
    ticker_type：抓取数据的优先顺序，'auto'/'stock'/'fund'为指数、股票和基金优先，'bond'为债券优先
    其目的是解决基金和债券代码部分重合的问题
    返回结果：雅虎格式，日期升序，列明首字母大写等
    """
    import akshare as ak
    import pandas as pd
    import datetime as dt
    
    df=None; found='None'

    #变换代码格式
    ticker2=tickers_cvt2ak(ticker)

    #变换日期格式
    result,start,end=check_period(fromdate,todate)
    if not result:
        print("  #Warning(get_price_ak_cn): invalid date period from",fromdate,'to',todate)
        return None   
    start1=start.strftime('%Y%m%d')
    end1=end.strftime('%Y%m%d')
    
    #adjustlist=['none','hfq','qfq']
    adjustlist=['','qfq','hfq','qfq-factor','hfq-factor','adj_only']
    if adjust not in adjustlist:
        print("  #Warning(get_price_ak_cn): adjust only supports",adjustlist)
        return None          

    _,prefix,suffix=split_prefix_suffix(ticker2)
    #考虑股票复权情形：仅收盘价为复权价，指数/基金/债券无复权
    if adjust not in ['','adj_only']:
        if ticker_type in ['auto','stock'] and suffix not in ['SW']:
            try:
                #仅用于股票的历史行情数据（考虑复权）
                dffqno=ak.stock_zh_a_daily(ticker2,start1,end1,adjust='')
                dffq=ak.stock_zh_a_daily(ticker2,start1,end1,adjust=adjust)
                dffq.rename(columns={'close':'Adj Close'},inplace=True)
                
                df=pd.merge(dffqno,dffq[['date','Adj Close']],on=['date'])
                df['Date']=df['date']
            except:
                df=None
            found=df_have_data(df)

    #考虑股票复权情形：所有价格均为复权价，指数/基金/债券无复权
    if adjust == 'adj_only':
        if ticker_type in ['auto','stock'] and suffix not in ['SW']:
            try:
                #仅用于股票的历史行情数据（考虑复权）
                df=ak.stock_zh_a_daily(ticker2,start1,end1,adjust='qfq')
                df['Adj Close']=df['close']
                df['Date']=df['date']
            except:
                df=None
            found=df_have_data(df)
    
    #股票(无复权)指数/基金/债券
    if found != 'Found': 
        if ticker_type in ['auto','stock'] and suffix not in ['SW']:
            try:
                #指数/股票/基金
                df = ak.stock_zh_index_daily(symbol=ticker2)  
                df['Date']=df['date'].apply(lambda x: pd.to_datetime(x))
            except: 
                df=None
            found=df_have_data(df)
            
            if found != 'Found':
                try:
                    #特殊函数（不考虑复权）
                    df=ak.stock_zh_a_cdr_daily(ticker2,start1,end1)
                    df['Date']=pd.to_datetime(df['date'])
                except: 
                    df=None
                found=df_have_data(df)
            
            if found != 'Found':
                try:
                    #最后抓取交易所债券行情
                    df = exchange_bond_price(ticker2,fromdate,todate,graph=False,data_crop=False)
                    df['Date']=df.index
                except: 
                    try:
                        #再次尝试抓取开放式基金单位净值
                        df =get_price_oef_china(ticker2,fromdate,todate)
                        df['Date']=df.index
                        
                        df['ticker']=ticker
                        df['Adj Close']=df['Close']
                        df['source']='Sina'
                    except: 
                        df=None
                        #print("  #Error(get_price_ak_cn): failed to find prices for",ticker)
                        return None
                found=df_have_data(df)
                
                #已找到证券信息，或在规定时段无数据
                if found in ['Empty','Found']: return df
        
        #债券优先，然后查找指数、股票和基金。因部分债券代码(特别是国债)与基金代码重合，需要甄别！
        #例如；sh010504既是"05国债⑷"也是"招商稳兴混合C"基金的代码:-(
        if ticker_type in ['bond'] and suffix not in ['SW']:
            try:
                #优先抓取交易所债券行情
                df = exchange_bond_price(ticker2,fromdate,todate,graph=False,data_crop=False)
                df['Date']=df.index
            except: 
                df=None
            found=df_have_data(df)
            
            #已找到证券信息，但在规定时段无数据
            if found=='Empty': return df
        
            if found != 'Found':
                try:
                    #其次仅抓取股票行情
                    df=ak.stock_zh_a_daily(ticker2,start1,end1,adjust=adjust)
                    df['Date']=df['date']
                    df['Date']=df['Date'].dt.tz_localize(None)
                except: 
                    df=None
                found=df_have_data(df)
                
            if found != 'Found':
                try:
                    #接着查找指数
                    df = ak.stock_zh_index_daily(symbol=ticker2)  
                    df['Date']=df['date'].apply(lambda x: pd.to_datetime(x))
                except: 
                    df=None
                found=df_have_data(df)
                
            if found != 'Found':
                try:
                    #最后查找开放式基金
                    df =get_price_oef_china(ticker2,fromdate,todate)
                    df['Date']=df.index
                except: 
                    df=None
                found=df_have_data(df)
                
        #基金。因部分债券代码(特别是国债)与基金代码重合，需要甄别！
        if ticker_type in ['fund'] and suffix not in ['SW']:
            try:
                #优先抓取开放式基金单位净值
                df =get_price_oef_china(ticker2,fromdate,todate)
                df['Date']=df.index
            except: 
                df=None
            found=df_have_data(df)
            
            #已找到证券信息，但在规定时段无数据
            #if found=='Empty': return df
        
            if found != 'Found':  #未找到，其次从股票爬虫抓取基金行情
                try:
                    df=ak.stock_zh_a_daily(ticker2,start1,end1,adjust=adjust)
                    df['Date']=df['date']
                    df['Date']=df['Date'].dt.tz_localize(None)
                except: 
                    df=None
                found=df_have_data(df)
                
            if found != 'Found':
                try:
                    #再次查找股票指数
                    df = ak.stock_zh_index_daily(symbol=ticker2)  
                    df['Date']=df['date'].apply(lambda x: pd.to_datetime(x))
                except: 
                    df=None
                found=df_have_data(df)

            if found != 'Found':
                try:
                    #最后从债券爬虫查找基金信息
                    df = exchange_bond_price(ticker2,fromdate,todate,graph=False,data_crop=False)
                    df['Date']=df.index
                except: 
                    df=None
                found=df_have_data(df)

        #申万指数                
        if suffix in ['SW']:
            try:
                df = fetch_price_swindex(prefix,fromdate,todate)
                df['Date']=df.index
            except: 
                df=None
                #print("  #Error(get_price_ak_cn): failed to retrieve prices for",ticker)
            found=df_have_data(df)
    
    if found in ['Found','Empty']:
        #设置新的索引
        df.set_index(['Date'],inplace=True)
        df.rename(columns={'open':'Open','high':'High','low':'Low','close':'Close','volume':'Volume'},inplace=True)

    try:
        df1=df[df.index >= start]
        df2=df1[df1.index <= end]
    except:
        df2=df
    found=df_have_data(df2)

    if found in ['Found','Empty']:
        df2['source']=text_lang('新浪','sina')
        df2['ticker']=str(ticker)
        if 'Adj Close' not in list(df2):
            df2['Adj Close']=df2['Close']
        df2['footnote']=adjust  
        
        """
        ptname=ticker_name(ticker,ticker_type)
        if ptname == ticker: ptname=''
        """
        
        if len(df2) > 0:
            print("  Successfully retrieved",len(df2),"records for",ticker)
    
    return df2

if __name__=='__main__':
    dfx=get_price_ak_cn('600519.SS','2020-12-1','2020-12-5',adjust='none')
    dfy=get_price_ak_cn('600519.SS','2020-12-1','2021-2-5',adjust='hfq')
    df399001=get_price_ak_cn('399001.SZ','2020-12-1','2021-2-5')
    df000688=get_price_ak('000688.SS','2020-12-1','2021-2-5')
    dfz=get_price_ak_cn('AAPL','2020-12-1','2021-2-5')

#==============================================================================
if __name__=='__main__':
    symbol='AAPL'
    symbol='GEM25.CME'
    fromdate='2024-5-1'
    todate='2025-5-20'
    adjust="qfq"
    
    get_price_ak_us(symbol, fromdate, todate, adjust)

def get_price_ak_us(symbol, fromdate, todate, adjust=""):
    """
    抓取单个美股股价，不能处理股指
    """
    import pandas as pd #此处需要，去掉会出错！
    DEBUG=False
    
    #检查日期期间
    result,start,end=check_period(fromdate,todate)
    if not result:
        print("  #Warning(get_price_ak_us): invalid date period from",fromdate,'to',todate)
        return None  
    
    symbol=symbol.upper()
    #printmsg=str(symbol)+" from "+fromdate+" to "+todate    

    import akshare as ak
    if DEBUG:
        print("  Searching info in Sina for",symbol,"... ...")
    try:
        if adjust=='':
            df=ak.stock_us_daily(symbol=symbol,adjust=adjust)
        elif adjust=='Adj_only':
            df=ak.stock_us_daily(symbol=symbol,adjust='qfq')
            df['Adj Close']=df['close']
    
        else:
            #分别获取收盘价和复权价，并合成
            dffqno=ak.stock_us_daily(symbol=symbol,adjust='')
            dffq=ak.stock_us_daily(symbol=symbol,adjust='qfq')
            dffq.rename(columns={'close':'Adj Close'},inplace=True)
            
            df=pd.merge(dffqno,dffq[['date','Adj Close']],on=['date'])
    except:
        if DEBUG:
            print("  #Error(get_price_ak_us): no info found for",symbol)
        return None
    
    #去掉可能出现的时区信息，必须使用datetime中的tz_localize
    df['date']=pd.to_datetime(df['date'])
    #df['date']=df['date'].tz_localize(None)
    
    #设置新的索引
    df.set_index(['date'],inplace=True)    
    
    #选取时间范围
    df1=df[df.index >=start]    
    df2=df1[df1.index <=end] 
    if df2 is None:
        print("  #Error(get_price_ak_us): failed to find prices for",symbol)
        return None    
    num=len(df2)
    if num==0:
        print("  #Error(get_price_ak_us): found zero record for",symbol)
        return None 
    
    df2.rename(columns={'open':'Open','high':'High','low':'Low','close':'Close','volume':'Volume'},inplace=True)
    df2['ticker']=symbol
    if 'Adj Close' not in list(df2):
        df2['Adj Close']=df2['Close']
    df2['source']=text_lang('新浪','Sina')
    df2['footnote']=adjust   
    
    """
    ptname=ticker_name(symbol,'stock')
    if ptname == symbol: ptname=''
    """
    
    print("  Successfully retrieved",num,"records for",symbol)    
    
    return df2

if __name__=='__main__':
    get_price_ak_us('AAPL', '2021-11-1', '2021-11-5')
    get_price_ak_us('^DJI', '2021-11-1', '2021-11-5')
#==============================================================================
if __name__=='__main__':
    symbol='0700.HK'
    symbol='0700.hk'
    
    symbol='00700.HK'
    fromdate='2014-5-1'
    todate  ='2014-5-31'
    adjust="qfq"
    
    tx=get_price_ak_hk(symbol='00700.HK',fromdate='2014-5-1',todate='2014-5-30',adjust="qfq")

def get_price_ak_hk(symbol,fromdate,todate,adjust=""):
    """
    抓取单个港股股价，不能处理股指，股指无.HK后缀
    """
    import pandas as pd
    
    DEBUG=False
    if DEBUG:
        print("Start searching HK stock prices for",symbol,"...")
    
    #检查日期期间
    result,start,end=check_period(fromdate,todate)
    if not result:
        print("  #Warning(get_price_ak_hk): invalid date period from",fromdate,'to',todate)
        return None  
    
    #printmsg=str(symbol)+" from "+fromdate+" to "+todate  

    import akshare as ak
    #print("  Searching info in Sina for",symbol,"... ...")
    symbol1=symbol.upper()
    symbol2 = symbol1.strip('.HK')
    if len(symbol2)==4:
        symbol3='0'+symbol2
    else:
        symbol3=symbol2
    
    try:
        if adjust == '':
            df=ak.stock_hk_daily(symbol=symbol3, adjust=adjust)
        elif adjust == 'Adj_only':
            df=ak.stock_hk_daily(symbol=symbol3, adjust='qfq')
            df['Adj Close']=df['close']
        else:
            dffqno=ak.stock_hk_daily(symbol=symbol3, adjust='')
            dffq  =ak.stock_hk_daily(symbol=symbol3,adjust='qfq')
            dffq.rename(columns={'close':'Adj Close'},inplace=True)
            
            df=pd.merge(dffqno,dffq[['date','Adj Close']],on=['date'])            
    except:
        print("  #Error(get_price_ak_hk): no info found for",symbol)
        return None
    
    #去掉可能出现的时区信息
    df['Date']=pd.to_datetime(df['date'])
    #设置新的索引
    df.set_index(['Date'],inplace=True)  
    
    #选取时间范围
    df1=df[df.index >=start]    
    df2=df1[df1.index <=end] 
    if df2 is None:
        print("  #Error(get_price_ak_hk): failed to find prices for",symbol)
        return None
    num=len(df2)
    if num==0:
        print("  #Error(get_price_ak_hk): found zero record for",symbol)
        return None
    
    df2.rename(columns={'open':'Open','high':'High','low':'Low','close':'Close','volume':'Volume'},inplace=True)
    df2['ticker']=symbol
    if 'Adj Close' not in list(df2):
        df2['Adj Close']=df2['Close']
    df2['source']=text_lang('新浪','Sina')
    
    """
    ptname=ticker_name(symbol,'stock')
    if ptname == symbol: ptname=''
    """
    
    print("  Successfully retrieved",num,"records for",symbol)
    
    return df2

if __name__=='__main__':
    df=get_price_ak_hk('0700.hk', '2021-11-1', '2021-11-5')
    df=get_price_ak_hk('0700.HK', '2021-11-1', '2021-11-5')
    df=get_price_ak_hk('00700.hk', '2021-11-1', '2021-11-5')
#==============================================================================
if __name__=='__main__':
    ticker=['600519.SS','000858.SZ']
    fromdate='2020-12-1'
    todate='2021-1-31'
    adjust='none'   
    
    prices=get_prices_ak(ticker,fromdate,todate,adjust,ticker_type)

def get_prices_ak(ticker,fromdate,todate,adjust='none',ticker_type='auto'):
    """
    功能：获取中国国内股票或指数的历史行情，多个股票
    """
    #检查是否为多个证券:单个证券代码
    if isinstance(ticker,str):
        df=get_price_ak(ticker,fromdate,todate,adjust=adjust,ticker_type=ticker_type)
        return df
    
    #检查是否为多个证券:空的列表
    if isinstance(ticker,list) and len(ticker) == 0:
        pass
        return None        
    
    #检查是否为多个证券:列表中只有一个代码
    if isinstance(ticker,list) and len(ticker) == 1:
        ticker1=ticker[0]
        #抓取单个证券
        df=get_price_ak(ticker1,fromdate,todate,adjust=adjust,ticker_type=ticker_type)
        return df       
    
    import pandas as pd
    #处理列表中的第一个证券
    i=0
    df=None
    while df is None:
        if i <= len(ticker)-1:
            t=ticker[i]
        else:
            return df

        #抓取单个证券
        df=get_price_ak(t,fromdate,todate,adjust=adjust,ticker_type=ticker_type)
        if not (df is None):
            columns=create_tuple_for_columns(df,t)
            df.columns=pd.MultiIndex.from_tuples(columns)
        else:
            i=i+1
    if (i+1) == len(ticker):
        #已经到达代码列表末尾
        return df
        
    #处理列表中的其余证券
    if i+1 <= len(ticker)-1:
        for t in ticker[(i+1):]:
            #抓取单个证券
            dft=get_price_ak(t,fromdate,todate,adjust=adjust,ticker_type=ticker_type)
            if not (dft is None):
                columns=create_tuple_for_columns(dft,t)
                dft.columns=pd.MultiIndex.from_tuples(columns)
            
            df=pd.merge(df,dft,how='inner',left_index=True,right_index=True)
     
    return df

if __name__=='__main__':
    dfm=get_prices_ak(['600519.SS','000858.SZ'],'2020-12-1','2021-1-31')
    dfm2=get_prices_ak(['600519.SS','AAPL'],'2020-12-1','2021-1-31')

#==============================================================================
if __name__=='__main__':
    ticker=['600519.SS','000858.SZ']
    fromdate='2020-12-1'
    todate='2021-1-31'
    adjust='none'    

def get_prices_simple(ticker,fromdate,todate,adjust='none'):
    """
    功能：直接循环获取股票或指数的历史行情，多个股票
    """
    #检查是否为多个股票:单个股票代码
    if isinstance(ticker,str):
        df=get_prices(ticker,fromdate,todate,adjust=adjust)
        return df
    
    #检查是否为多个股票:空的列表
    if isinstance(ticker,list) and len(ticker) == 0:
        pass
        return None        
    
    #检查是否为多个股票:列表中只有一个代码
    if isinstance(ticker,list) and len(ticker) == 1:
        ticker1=ticker[0]
        df=get_prices(ticker1,fromdate,todate,adjust=adjust)
        return df       
    
    import pandas as pd
    #处理列表中的第一个股票
    i=0
    df=None
    while df is None:
        t=ticker[i]
        #df=get_prices(t,fromdate,todate,adjust=adjust)
        df=get_prices(t,fromdate,todate)
        if not (df is None):
            columns=create_tuple_for_columns(df,t)
            df.columns=pd.MultiIndex.from_tuples(columns)
        else:
            i=i+1
    if (i+1) == len(ticker):
        #已经到达股票代码列表末尾
        return df
    
    #对抗时区不匹配问题
    df.index=pd.to_datetime(df.index)
    #处理列表中的其余股票
    for t in ticker[(i+1):]:
        #dft=get_prices(t,fromdate,todate,adjust=adjust)
        dft=get_prices(t,fromdate,todate)
        if dft is None: continue
        if len(dft)==0: continue
        
        if not (dft is None):
            columns=create_tuple_for_columns(dft,t)
            dft.columns=pd.MultiIndex.from_tuples(columns)
    
        dft.index=pd.to_datetime(dft.index)
        df=pd.merge(df,dft,how='inner',left_index=True,right_index=True)
     
    return df

if __name__=='__main__':
    dfm=get_prices_simple(['600519.SS','000858.SZ'],'2020-12-1','2021-1-31')
    dfm2=get_prices_simple(['600519.SS','AAPL'],'2020-12-1','2021-1-31')

#==============================================================================

if __name__=='__main__':
    ticker='AAPL'
    ticker='^JN0U.JO'
    
    start='2024-3-1'
    end='2024-3-31'
    retry_count=3
    pause=1
    
    ticker='^RUT'
    
    ticker=['AAPL','MSFT']
    ticker=['AAPL','MSFT','ABCD']
    
    df=get_prices_yahoo(ticker,start,end)

def get_prices_yahoo(ticker,start,end,retry_count=3,pause=1):
    """
    功能：抓取股价，使用pandas_datareader
    输出：指定收盘价格序列，最新日期的股价排列在前
    ticker: 股票代码。大陆股票代码加上后缀.SZ或.SS或.BJ，港股代码去掉前导0加后缀.HK
    start: 样本开始日期，尽量远的日期，以便取得足够多的原始样本，yyyy-mm-dd
    end: 样本结束日期，既可以是今天日期，也可以是一个历史日期
    retry_count：网络失败时的重试次数
    pause：每次重试前的间隔秒数
    """
    
    #抓取新浪/stooq股票价格
    from pandas_datareader import data as pdr
    
    """
    #临时修正新浪/stooq网站问题: 2021-7-14
    #yfinance极易出现线程失败，不再覆盖pdr，2021-10-24
    import yfinance as yfin
    yfin.pdr_override()
    """
    p=None
    
    try:
        #p=data.DataReader(ticker,'yahoo',start,end,retry_count=retry_count,pause=pause)
        p=pdr.get_data_yahoo(ticker,start=start,end=end)
    except: pass
    found=df_have_data(p)
    
    if found in ['Found']:
        cols=list(p)
        if 'Adj Close' not in cols:
            p['Adj Close']=p['Close']
    
        p['ticker']=ticker
        #p['Adj Close']=p['Close']
        p['source']=text_lang('雅虎','Yahoo')
    
        """
        ptname=ticker_name(ticker,'stock')
        if ptname == ticker: ptname=''
        """
        
        print("  Successfully retrieved",len(p),"records for",ticker)

        #去掉时区
        p=df_index_timezone_remove(p)
    
    return p

if __name__=='__main__':
    df1=get_prices_yahoo('AAPL','2020-12-1','2021-1-31')
    df2=get_prices_yahoo('ABCD','2020-12-1','2021-1-31')
    df3=get_prices_yahoo(['AAPL','MSFT'],'2020-12-1','2021-1-31')
    df4=get_prices_yahoo(['AAPL','EFGH','MSFT','ABCD'],'2020-12-1','2021-1-31')
    df5=get_prices_yahoo(['0700.HK','600519.SS'],'2020-12-1','2021-1-31')
    df6=get_prices_yahoo(['AAPL','MSFT','0700.HK','600519.SS'],'2020-12-1','2021-1-31')

#==============================================================================
def get_price_yf(ticker,start,end,threads=False):
    """
    套壳函数get_prices_yf，保持兼容
    """
    df=get_prices_yf(ticker,start,end,threads=threads)
    
    return df


if __name__=='__main__':
    start='2024-12-1'
    end='2025-1-31'
    
    ticker='AAPL'
    ticker='GC=F'
    
    ticker='XAUUSD'
    
    ticker=['AAPL','MSFT']
    ticker=['0700.HK','600519.SS']
    ticker=['AAPL','MSFT','0700.HK','600519.SS']
    
    threads=False
    threads=True
    
    df=get_price_yf(ticker,start,end,threads)


def get_prices_yf(ticker,start,end,threads=False):
    """
    功能：抓取股价，使用yfinance(对非美股抓取速度快，但有时不太稳定)
    输入：股票代码或股票代码列表，开始日期，结束日期
    ticker: 股票代码或股票代码列表。大陆股票代码加上后缀.SZ或.SS或.BJ，港股代码去掉前导0加后缀.HK
    start: 样本开始日期，尽量远的日期，以便取得足够多的原始样本，yyyy-mm-dd
    end: 样本结束日期，既可以是今天日期，也可以是一个历史日期
    
    输出：指定收盘价格序列，最新日期的股价排列在前
    特别注意：yfinance中的收盘价Close其实是Yahoo Finance中的调整收盘价Adj Close。
    """
    p=None

    #支持多个证券
    import yfinance as yf
    ticker1,islist=cvt_yftickerlist(ticker)
    if not islist:
        #下载单一股票的股价
        stock=yf.Ticker(ticker1)
        try:
            #p=stock.history(start=start,end=end,threads=threads)
            p=stock.history(start=start,end=end)
            #仅针对雅虎情况
            if p is not None:
                if len(p)==0: p=None
        except:
            p=None
    else: 
        #下载股票列表的股价
        try:
            p=yf.download(ticker1,start=start,end=end,progress=False,threads=threads)
            #仅针对雅虎情况
            if p is not None:
                if len(p)==0: p=None
        except:
            p=None
            
    found=df_have_data(p)
    if found in ['Found','Empty']:
        if 'Adj Close' not in list(p):
            p['Adj Close']=p['Close']  
        p['ticker']=ticker
        p['source']=text_lang('雅虎','Yahoo')
        
        if len(p) > 0:
            """
            ptname=ticker_name(ticker1,'stock')
            if ptname == ticker: ptname=''
            """
            
            print("  Successfully retrieved",len(p),"records for",ticker1)  
            
            #去掉时区
            p=df_index_timezone_remove(p)
    else:
        pass
        #print("  #Error(get_prices_yf):",ticker1,"not found or no prices in the period or inaccessible to yahoo")

    return p

if __name__=='__main__':
    df1=get_prices_yf('AAPL','2020-12-1','2021-1-31')
    df1b=get_prices_yf('EFGH','2020-12-1','2021-1-31')
    df2=get_prices_yf(['AAPL'],'2020-12-1','2021-1-31')
    df3=get_prices_yf(['AAPL','MSFT'],'2020-12-1','2021-1-31')
    df3b=get_prices_yf(['AAPL','MSFS'],'2020-12-1','2021-1-31')
    df4=get_prices_yf(['0700.HK','600519.SS'],'2020-12-1','2021-1-31')
    df5=get_prices_yf(['AAPL','MSFT','0700.HK','600519.SS'],'2020-12-1','2021-1-31')
    df6=get_prices_yf(['ABCD','EFGH','0700.HK','600519.SS'],'2020-12-1','2021-1-31')

#==============================================================================
if __name__=='__main__':
    ticker='^TYX'
    ticker='AMZN'
    ticker='AAPL'
    start='2020-12-1'; end='2025-1-31'

    ticker='GEM25.CME'
    start='2025-1-1'; end='2025-5-30'
    
    p=get_price_yq(ticker,start,end)
    
def get_price_yq(ticker,start,end):
    """
    功能：从雅虎财经抓取股价，使用yahooquery(注意插件版本问题)
    输入：股票代码或股票代码列表，开始日期，结束日期
    ticker: 股票代码或股票代码列表。大陆股票代码加上后缀.SZ或.SS或.BJ，港股代码去掉前导0加后缀.HK
    start: 样本开始日期，尽量远的日期，以便取得足够多的原始样本，yyyy-mm-dd
    end: 样本结束日期，既可以是今天日期，也可以是一个历史日期
    
    输出：指定收盘价格序列，最新日期的股价排列在前
    """
    DEBUG=False
    
    p=None

    #支持多个证券
    import yahooquery as yq
    ticker1,islist=cvt_yftickerlist(ticker)
    
    try:
        #下载单一股票的股价；下载股票列表的股价，与单股票情况相同，但需注意MultiInex结构
        stock=yq.Ticker(ticker1, asynchronous=True)
    except:
        if DEBUG:
            print("  Yahoo api is tentatively inaccessible, recovering ...")
        sleep_random(max_sleep=60)
        try:
            stock=yq.Ticker(ticker1, asynchronous=True)
        except:
            if DEBUG:
                print(f"  Sorry, failed to retrieve info from Yahoo for {ticker}")
            p=None
            return p
        
    if not islist:
        try:
            p=stock.history(start=start,end=end)
            #仅针对雅虎情况
            if p is not None:
                if len(p)==0: p=None
        except:
            p=None
    else: 
        try:
            p=stock.history(start=start,end=end)
            #仅针对雅虎情况
            if p is not None:
                if len(p)==0: p=None
        except:
            p=None
            
    found=df_have_data(p)
    if found in ['Found','Empty']:
        p.rename(columns={'open':'Open','high':'High','low':'Low','close':'Close', \
                          'adjclose':'Adj Close','volume':'Volume'},inplace=True)
        
        if 'Adj Close' not in list(p):
            p['Adj Close']=p['Close']  
        p['ticker']=ticker
        p['source']=text_lang('雅虎','Yahoo')
        
        # 去掉一级Index
        p=p.droplevel('symbol')
        p['date']=p.index
        if len(p) > 0:
            print("  Successfully retrieved",len(p),"records for",ticker1)  
            
            #去掉时区
            p=df_index_timezone_remove(p)
    else:
        pass
        #print("  #Error(get_prices_yf):",ticker1,"not found or no prices in the period or inaccessible to yahoo")

    return p

#==============================================================================
if __name__=='__main__':
    ticker=['600519.SS','000858.SZ']
    fromdate='2020-12-1'
    todate='2021-1-31'
    
    ticker=['ICBC','SNP','HNP']
    fromdate,todate='2025-6-1','2025-6-20'    

    
    prices=get_prices_yq(ticker,fromdate,todate)

def get_prices_yq(ticker,fromdate,todate):
    """
    功能：获取yahooquery股票或指数的历史行情，多个股票
    """
    #检查是否为多个证券:单个证券代码
    if isinstance(ticker,str):
        df=get_price_yq(ticker,fromdate,todate)
        return df
    
    #检查是否为多个证券:空的列表
    if isinstance(ticker,list) and len(ticker) == 0:
        pass
        return None        
    
    #检查是否为多个证券:列表中只有一个代码
    if isinstance(ticker,list) and len(ticker) == 1:
        ticker1=ticker[0]
        #抓取单个证券
        df=get_price_yq(ticker1,fromdate,todate)
        return df       
    
    import pandas as pd
    #处理列表中的第一个证券
    i=0
    df=None
    while df is None:
        if i <= len(ticker)-1:
            t=ticker[i]
        else:
            return df
        
        #抓取单个证券
        df=get_price_yq(t,fromdate,todate)
        if not (df is None):
            columns=create_tuple_for_columns(df,t)
            df.columns=pd.MultiIndex.from_tuples(columns)
        else:
            i=i+1
            
    if (i+1) == len(ticker):
        pass
        #已经到达代码列表末尾
        return df
        
    #处理列表中的其余证券
    if i+1 <= len(ticker)-1:
        for t in ticker[(i+1):]:
            #抓取单个证券
            dft=get_price_yq(t,fromdate,todate)
            if not (dft is None):
                columns=create_tuple_for_columns(dft,t)
                dft.columns=pd.MultiIndex.from_tuples(columns)
            
            df=pd.merge(df,dft,how='inner',left_index=True,right_index=True)
     
    return df

if __name__=='__main__':
    dfm=get_prices_yq(['600519.SS','000858.SZ'],'2020-12-1','2021-1-31')
    dfm2=get_prices_yq(['600519.SS','AAPL'],'2020-12-1','2021-1-31')
#==============================================================================
if __name__=='__main__':
    ticker='AMZN'
    ticker='AAPL'
    start='2020-12-1'; end='2025-1-31'    
    
def get_dividend_yq(ticker,start,end,facecolor="papayawhip"):
    """
    功能：获得股票分红历史数据
    """
    
    print(f"  Looking for dividend info for {ticker} from Yahoo ...")
    try:
        p=get_price_yq(ticker,start,end)
    except:
        print(f"  #Error(get_dividend_yq): crump problem. If {ticker} is correct, try again later")
        return None
    if p is None:
        print(f"  #Error(get_dividend_yq): failed to get dividend info for {ticker}, may try again later")
        return None
        
    pcols=list(p)
    if not ('dividends' in pcols):
        print(f"  No dividend info found for {ticker} from {start} to {end}")
        return None
    
    div1=p[['date','dividends','Close','Adj Close']]
    div2=div1[div1['dividends'] != 0]
    
    if len(div2) == 0:
        print(f"  No dividend info found for {ticker} during {start} to {end}")
        return None
        
    div2['dividends']=div2['dividends'].apply(lambda x: str(round(x,5)))
    div2['Close']=div2['Close'].apply(lambda x: round(x,2))
    div2['Adj Close']=div2['Adj Close'].apply(lambda x: round(x,2))
    div2.rename(columns={"date":text_lang("除息日期","Ex-Dividend"), \
                         "dividends":text_lang("每股分红(本币，税前)","Div per Share (Pre-tax)"), \
                         "Close":text_lang("收盘价","Close Price"), \
                         "Adj Close":text_lang("调整收盘价(前复权价)","Adjusted Close Price")}, \
                inplace=True)
        
    titletxt=ticker_name(ticker,"stock")+": "+text_lang("股票分红历史","Stock Dividend History")
    import datetime
    todaydt = datetime.date.today()
    footnote_cn=f"【注】期间：{start}至{end}, 数据来源：雅虎, {todaydt}"
    footnote_en=f"Period：{start} to {end}. Data source：Yahoo, {todaydt}"
    footnote=text_lang(footnote_cn,footnote_en)
    df_display_CSS(div2,titletxt=titletxt,footnote=footnote,facecolor=facecolor,decimals=2, \
                       first_col_align='center',second_col_align='center', \
                       last_col_align='center',other_col_align='center')

    
    return div2

def get_split_yq(ticker,start,end,facecolor="papayawhip"):
    """
    功能：获得股票分拆历史数据
    """
    
    print(f"  Looking for split info for {ticker} from Yahoo ...")
    try:
        p=get_price_yq(ticker,start,end)
    except:
        print(f"  #Error(get_split_yq): crump problem. If {ticker} is correct, try again later")
        return None
    if p is None:
        print(f"  #Error(get_split_yq): split info not found for {ticker}, may try again later")
        return None
        
    pcols=list(p)
    if not ('splits' in pcols):
        print(f"  No split info found for {ticker} from {start} to {end}")
        return None
    
    div1=p[['date','splits','Close','Adj Close']]
    div2=div1[div1['splits'] != 0]
    
    if len(div2) == 0:
        print(f"  No split info found for {ticker} during {start} to {end}")
        return None
        
    div2['Close']=div2['Close']*div2['splits']
    div2['splits']=div2['splits'].apply(lambda x: str(int(x)) if x.is_integer() else str(round(x,1)))
    div2['Close']=div2['Close'].apply(lambda x: round(x,2))
    div2['Adj Close']=div2['Adj Close'].apply(lambda x: round(x,2))
    div2.rename(columns={"date":text_lang("分拆日期","Split Date"), \
                         "splits":text_lang("分拆比例","Split Ratio"), \
                         "Close":text_lang("收盘价","Close Price"), \
                         "Adj Close":text_lang("调整收盘价(前复权价)","Adjusted Close Price")}, \
                inplace=True)
        
    titletxt=ticker_name(ticker,"stock")+": "+text_lang("股票分拆历史","Stock Split History")
    import datetime
    todaydt = datetime.date.today()
    footnote_cn=f"【注】期间：{start}至{end}, 数据来源：雅虎, {todaydt}"
    footnote_en=f"Period：{start} to {end}. Data source：Yahoo, {todaydt}"
    footnote=text_lang(footnote_cn,footnote_en)
    df_display_CSS(div2,titletxt=titletxt,footnote=footnote,facecolor=facecolor,decimals=2, \
                       first_col_align='center',second_col_align='center', \
                       last_col_align='right',other_col_align='center')

    
    return div2

#==============================================================================
if __name__=='__main__':
    ticker='^GSPC'
    start='1991-1-1'
    end='2000-12-31'

def get_index_fred(ticker,start,end):
    """
    功能：临时解决方案，获取标普500、道琼斯等国外市场指数
    """
    yahoolist=['^GSPC','^DJI','^VIX','^IXIC','^N225','^NDX']
    fredlist=['sp500','djia','vixcls','nasdaqcom','nikkei225','nasdaq100']
    
    if not (ticker in yahoolist):
        return None
    
    import pandas as pd
    import pandas_datareader.data as web
    if ticker in yahoolist:
        pos=yahoolist.index(ticker)
        id=fredlist[pos]
        
        try:
            df = web.DataReader([id], start=start, end=end, data_source='fred')
        except:
            print("  #Warning(get_index_fred): connection failed, trying to recover ...")
            import time
            time.sleep(5) # 暂停 5秒
            try:
                df = web.DataReader([id], start=start, end=end, data_source='fred')
            except:
                pass
                return None
        if len(df)==0:
            return None
        df.rename(columns={id:'Close'},inplace=True)
    
    #删除空值记录
    #df.dropna(inplace=True)
    
    df['ticker']=ticker
    df['Adj Close']=df['Close']
    df['source']='FRED'
    
    num=len(df)
    if num > 0:
        """
        ptname=ticker_name(ticker,'stock')
        if ptname == ticker: ptname=''
        """
        
        print("  Successfully retrieved",num,"records for",ticker)    
    else:
        print("  Sorry, no records retrieved for",ticker)

    #去掉时区
    df=df_index_timezone_remove(df)
    
    return df

if __name__=='__main__':
    df1=get_index_fred('^VIX','1991-1-1','1991-12-31')    
    df2=get_index_fred('^DJI','1991-1-1','2020-12-31')  #始于2011-11-25
    df3=get_index_fred('^GSPC','1991-1-1','2020-12-31')  #始于2011-11-25
    df4=get_index_fred('^IXIC','1991-1-1','2020-12-31')
    df5=get_index_fred('^N225','1991-1-1','2020-12-31')
    df6=get_index_fred('^NDX','1991-1-1','2020-12-31')
#==============================================================================  
def create_tuple_for_columns(df_a, multi_level_col):
    """
    Create a columns tuple that can be pandas MultiIndex to create multi level column

    :param df_a: pandas dataframe containing the columns that must form the first level of the multi index
    :param multi_level_col: name of second level column
    :return: tuple containing (first_level_cols,second_level_col)
    """
    temp_columns = []
    for item in df_a.columns:
        try:
            temp_columns.append((item, multi_level_col))
        except:
            temp_columns._append((item, multi_level_col))
    
    return temp_columns    
#==============================================================================
#==============================================================================
#==============================================================================
#==============================================================================
def get_price_portfolio(tickerlist,sharelist,fromdate,todate,adj=False, \
                        source='auto',ticker_type='bond'):
    """
    套壳函数get_prices_portfolio
    经测试，已经能够支持capm_beta2
    ticker_type='bond'：抓取债券优先，因投资组合中配置债券的可能性远高于基金和指数
    """
    df=get_prices_portfolio(tickerlist,sharelist,fromdate,todate,adj=adj, \
                            source=source,ticker_type=ticker_type)
    return df

if __name__=='__main__':
    tickerlist=['INTC','MSFT']
    sharelist=[0.6,0.4]
    
    tickerlist=['600519.SS', '000858.SZ', '600809.SS']
    sharelist=[0.4,0.3,0.3]
    
    tickerlist=['JD']
    sharelist=[1000]
    
    tickerlist=['601988.SS']
    sharelist=[1000]
    
    fromdate='2024-1-1'
    todate='2024-4-1'
    adj=False
    source='auto'
    ticker_type='auto'
    
    ticker={'Market':('China','000001.SS','白酒组合'),'600519.SS':0.4,'000858.SZ':0.6}
    _,_,tickerlist,sharelist,ticker_type=decompose_portfolio(ticker)

    p=get_prices_portfolio(tickerlist,sharelist,fromdate,todate,source='auto')

def get_prices_portfolio(tickerlist,sharelist,fromdate,todate,adj=False, \
                         source='auto',ticker_type='bond'):
    """
    功能：抓取投资组合的每日价值
    输入：证券代码列表，份额列表，开始日期，结束日期
    tickerlist: 证券代码列表
    sharelist：持有份额列表，与股票代码列表一一对应
    fromdate: 样本开始日期。格式：'YYYY-MM-DD'
    todate: 样本结束日期。既可以是今天日期，也可以是一个历史日期    
    
    输出：投资组合的价格序列，按照日期升序排列
    """
    import pandas as pd
    
    #检查证券列表个数与份额列表个数是否一致
    if len(tickerlist) != len(sharelist):
        print("  #Error(get_prices_portfolio): numbers of stocks and shares mismatch.")
        return None        
    
    #抓取证券价格：如何只抓取股票和债券？？？
    p=get_prices(tickerlist,fromdate,todate,adj=adj,source=source,ticker_type=ticker_type)
    if p is None: return None
    
    #删除无用的空列preclose，避免引起后续程序误判
    try:
        del p['prevclose']
    except: pass
    
    #结果非空时，检查整列为空的证券代码
    nancollist=[] 
    collist=list(p)
    for c in collist:
        if p[c].isnull().all():
            nancollist=nancollist+[c]
    #查找错误的ticker
    wrongtickers=[]
    for w in tickerlist:
        nancolstr=str(nancollist)
        if nancolstr.find(w.upper()) != -1:    #找到
            wrongtickers=wrongtickers+[w]
        
    if len(wrongtickers) > 0:
        print("  #Warning(get_prices_portfolio): price info not found for",wrongtickers)
        print("  #Warning(get_prices_portfolio): dropping all the rows related to",wrongtickers)
        p.dropna(axis=1,how="all",inplace=True)   # 丢弃全为缺失值的那些列
        
        #删除投资组合中相关的权重
        for w in wrongtickers:
            pos=tickerlist.index(w)
            try:
                del tickerlist[pos]
                del sharelist[pos]
            except: pass

    if len(sharelist) > 1:    
        #计算投资者的开盘价
        op=p['Open']
        #计算投资组合的价值
        oprice=pd.DataFrame(op.dot(sharelist))
        oprice.rename(columns={0: 'Open'}, inplace=True)    

        #计算投资者的收盘价
        cp=p['Close']
        #计算投资组合的价值
        cprice=pd.DataFrame(cp.dot(sharelist))
        cprice.rename(columns={0: 'Close'}, inplace=True) 
    
        #计算投资者的调整收盘价
        acp=p['Adj Close']
        #计算投资组合的价值
        acprice=pd.DataFrame(acp.dot(sharelist))
        acprice.rename(columns={0: 'Adj Close'}, inplace=True) 

        #合成开盘价、收盘价和调整收盘价
        ocprice=pd.merge(oprice,cprice,how='inner',left_index=True,right_index=True)
        prices=pd.merge(ocprice,acprice,how='inner',left_index=True,right_index=True)
    else:
        #prices=p*sharelist[0]
        prices=p
        pcols=list(prices)
        import pandas as pd
        for pc in pcols:
            #判断某列的数据类型
            if pd.api.types.is_float_dtype(prices[pc]):
                prices[pc]=prices[pc]*sharelist[0]
            else:
                continue
    
    #提取日期和星期几
    prices['Date']=prices.index.strftime("%Y-%m-%d")
    prices['Weekday']=prices.index.weekday+1

    prices['Portfolio']=str(tickerlist)
    prices['Shares']=str(sharelist)
    try:
        prices['Adjustment']=prices.apply(lambda x: \
              False if x['Close']==x['Adj Close'] else True, axis=1)
    
        stockdf=prices[['Portfolio','Shares','Date','Weekday', \
                        'Open','Close','Adj Close','Adjustment']]  
    except:
        return None
    
    return stockdf      

if __name__=='__main__':
    tickerlist=['INTC','MSFT']
    sharelist=[0.6,0.4]
    fromdate='2020-11-1'
    todate='2021-1-31'
    dfp=get_prices_portfolio(tickerlist,sharelist,fromdate,todate)

#==============================================================================
#==============================================================================
if __name__=='__main__':
    ticker='AAPL'

    ticker=['AAPL','MSFT','0700.HK','600519.SS']

def cvt_yftickerlist(ticker):
    """
    功能：转换pandas_datareader的tickerlist为yfinance的格式
    输入参数：单一股票代码或pandas_datareader的股票代码列表

    输出参数：yfinance格式的股票代码列表
    """
    #如果不是股票代码列表，直接返回股票代码
    if not isinstance(ticker,list): return ticker,False
    
    #如果是股票代码列表，但只有一个元素
    if len(ticker)==1: return ticker[0],False
    
    #如果是股票代码列表，有两个及以上元素
    yftickerlist=ticker[0]
    for t in ticker[1:]:
        yftickerlist=yftickerlist+' '+t.upper()
    
    return yftickerlist,True


if __name__=='__main__':
    cvt_yftickerlist('AAPL')
    cvt_yftickerlist(['AAPL'])
    cvt_yftickerlist(['AAPL','MSFT'])
    cvt_yftickerlist(['AAPL','MSFT','0700.hk'])
    
#==============================================================================
if __name__=='__main__':
    url='https://finance.yahoo.com'

def test_website(url='https://finance.yahoo.com'):
    """
    功能：测试网站的联通性和反应时间
    优点：真实
    缺点：运行过程非常慢
    """
    print("  Testing internet connection to",url,"...")
    import pycurl
    from io import BytesIO

    #进行网络测试
    c = pycurl.Curl()
    buffer = BytesIO()  # 创建缓存对象
    c.setopt(c.WRITEDATA, buffer)  # 设置资源数据写入到缓存对象
    c.setopt(c.URL, url)  # 指定请求的URL
    c.setopt(c.MAXREDIRS, 3)  # 指定HTTP重定向的最大数
    
    test_result=True
    test_msg=""
    try:
        c.perform()  # 测试目标网站
    except Exception as e:
        c.close()
        
        #print(e)
        print("  #Error(test_website2):",e)
              
        test_result=False
        test_msg="UNREACHABLE"        
        
        return test_result,test_msg
        
    #获得网络测试结果阐述
    http_code = c.getinfo(pycurl.HTTP_CODE)  # 返回的HTTP状态码
    dns_resolve = c.getinfo(pycurl.NAMELOOKUP_TIME)  # DNS解析所消耗的时间
    http_conn_time = c.getinfo(pycurl.CONNECT_TIME)  # 建立连接所消耗的时间
    http_pre_trans = c.getinfo(pycurl.PRETRANSFER_TIME)  # 从建立连接到准备传输所消耗的时间
    http_start_trans = c.getinfo(pycurl.STARTTRANSFER_TIME)  # 从建立连接到传输开始消耗的时间
    http_total_time = c.getinfo(pycurl.TOTAL_TIME)  # 传输结束所消耗的总时间
    http_size_download = c.getinfo(pycurl.SIZE_DOWNLOAD)  # 下载数据包大小
    http_size_upload = c.getinfo(pycurl.SIZE_UPLOAD)  # 上传数据包大小
    http_header_size = c.getinfo(pycurl.HEADER_SIZE)  # HTTP头部大小
    http_speed_downlaod = c.getinfo(pycurl.SPEED_DOWNLOAD)  # 平均下载速度
    http_speed_upload = c.getinfo(pycurl.SPEED_UPLOAD)  # 平均上传速度
    http_redirect_time = c.getinfo(pycurl.REDIRECT_TIME)  # 重定向所消耗的时间
    
    """
    print('HTTP响应状态： %d' % http_code)
    print('DNS解析时间：%.2f ms' % (dns_resolve * 1000))
    print('建立连接时间： %.2f ms' % (http_conn_time * 1000))
    print('准备传输时间： %.2f ms' % (http_pre_trans * 1000))
    print("传输开始时间： %.2f ms" % (http_start_trans * 1000))
    print("传输结束时间： %.2f ms" % (http_total_time * 1000))
    print("重定向时间： %.2f ms" % (http_redirect_time * 1000))
    print("上传数据包大小： %d bytes/s" % http_size_upload)
    print("下载数据包大小： %d bytes/s" % http_size_download)
    print("HTTP头大小： %d bytes/s" % http_header_size)
    print("平均上传速度： %d k/s" % (http_speed_upload / 1024))
    print("平均下载速度： %d k/s" % (http_speed_downlaod / 1024))
    """
    c.close()
    
    if http_speed_downlaod >= 100*1024: test_msg="FAST"
    if http_speed_downlaod < 100*1024: test_msg="GOOD"
    if http_speed_downlaod < 50*1024: test_msg="GOOD"
    if http_speed_downlaod < 10*1024: test_msg="VERY SLOW"
    if http_speed_downlaod < 1*1024: test_msg="UNSTABLE"
    
    return test_result,test_msg

if __name__=='__main__':
    test_website()
    
#==============================================================================
def calc_daily_return(pricedf):
    """
    功能：基于从新浪/stooq抓取的单个证券价格数据集计算其日收益率
    输入：从新浪/stooq抓取的单个证券价格数据集pricedf，基于收盘价或调整收盘价进行计算
    输出：证券日收益率序列，按照日期升序排列。
    """
    import numpy as np    
    #计算算术日收益率：基于收盘价
    pricedf["Daily Ret"]=pricedf['Close'].pct_change()
    pricedf["Daily Ret%"]=pricedf["Daily Ret"]*100.0
    
    #计算算术日收益率：基于调整收盘价
    pricedf["Daily Adj Ret"]=pricedf['Adj Close'].pct_change()
    pricedf["Daily Adj Ret%"]=pricedf["Daily Adj Ret"]*100.0
    
    #计算对数日收益率
    pricedf["log(Daily Ret)"]=np.log(pricedf["Daily Ret"]+1)
    pricedf["log(Daily Adj Ret)"]=np.log(pricedf["Daily Adj Ret"]+1)
    
    return pricedf 
    

if __name__ =="__main__":
    ticker='AAPL'
    fromdate='2018-1-1'
    todate='2020-3-16'
    pricedf=get_price(ticker, fromdate, todate)
    drdf=calc_daily_return(pricedf)   
    
    eu7=['GSK','ASML','NVS','NVO','AZN','SAP','SNY']
    for ticker in eu7:
        print("Processing",ticker,"...")
        pricedf,found=get_price_1ticker_mixed(ticker,fromdate='2022-1-1',todate='2024-6-16',source='yahoo')
        dret=calc_daily_return(pricedf)
    

#==============================================================================
def calc_rolling_return(drdf, period="Weekly"):
    """
    功能：基于单个证券的日收益率数据集, 计算其滚动期间收益率
    输入：
    单个证券的日收益率数据集drdf。
    期间类型period，默认为每周。
    输出：期间滚动收益率序列，按照日期升序排列。
    """
    #检查period类型
    periodlist = ["Weekly","Monthly","Quarterly","Annual"]
    if not (period in periodlist):
        print("  #Error(calc_rolling_return), periodic type only support：",periodlist)
        return None

    #换算期间对应的实际交易天数
    perioddays=[5,21,63,252]
    rollingnum=perioddays[periodlist.index(period)]    
    
    #计算滚动收益率：基于收盘价
    retname1=period+" Ret"
    retname2=period+" Ret%"
    import numpy as np
    drdf[retname1]=np.exp(drdf["log(Daily Ret)"].rolling(rollingnum,min_periods=1).sum())-1.0
    drdf[retname2]=drdf[retname1]*100.0
    
    #计算滚动收益率：基于调整收盘价
    retname3=period+" Adj Ret"
    retname4=period+" Adj Ret%"
    drdf[retname3]=np.exp(drdf["log(Daily Adj Ret)"].rolling(rollingnum,min_periods=1).sum())-1.0
    drdf[retname4]=drdf[retname3]*100.0
    
    return drdf

if __name__ =="__main__":
    ticker='000002.SZ'
    period="Weekly"
    prdf=calc_rolling_return(drdf, period) 
    prdf=calc_rolling_return(drdf, "Monthly")
    prdf=calc_rolling_return(drdf, "Quarterly")
    prdf=calc_rolling_return(drdf, "Annual")

#==============================================================================
def calc_expanding_return(drdf0,basedate):
    """
    功能：基于日收益率数据集，从起始日期开始到结束日期的扩展窗口收益率序列。
    输入：
    日收益率数据集drdf。
    输出：期间累计收益率序列，按照日期升序排列。
    """
    #去掉时区
    drdf0=df_index_timezone_remove(drdf0)
    
    import pandas as pd
    basedate_pd=pd.to_datetime(basedate)
    drdf=drdf0[drdf0.index >= basedate_pd]
    if len(drdf)==0:
        ticker=drdf0['ticker'].values[0]
        lastdate=drdf0.index.values[-1]
        print("\n  #Warning(calc_expanding_return): no records in",ticker,'after',basedate)
        """
        print("  basedate_pd=",basedate_pd)
        print("  drdf0=",drdf0)
        print("  drdf=",drdf)
        """
        return None
    """
    drdf0['date_tmp']=drdf0.index
    drdf0['date_tmp']=drdf0['date_tmp'].apply(lambda x: x.strftime('%Y-%m-%d'))
    basedate2=basedate_pd.strftime('%Y-%m-%d')
    drdf=drdf0[drdf0['date_tmp'] >= basedate2]
    """
    
    #计算累计收益率：基于收盘价
    retname1="Exp Ret"
    retname2="Exp Ret%"
    import numpy as np
    #drdf[retname1]=np.exp(drdf["log(Daily Ret)"].expanding(min_periods=1).sum())-1.0
    #drdf[retname1]=np.exp(drdf["log(Daily Ret)"].expanding(min_periods=5).sum())-1.0
    first_close=drdf.head(1)['Close'].values[0]
    drdf[retname1]=drdf['Close']/first_close-1
    drdf[retname2]=drdf[retname1]*100.0  
    
    #计算累计收益率：基于调整收盘价
    retname3="Exp Adj Ret"
    retname4="Exp Adj Ret%"
    #drdf[retname3]=np.exp(drdf["log(Daily Adj Ret)"].expanding(min_periods=1).sum())-1.0
    #drdf[retname3]=np.exp(drdf["log(Daily Adj Ret)"].expanding(min_periods=5).sum())-1.0
    first_aclose=drdf.head(1)['Adj Close'].values[0]
    drdf[retname3]=drdf['Adj Close']/first_aclose-1
    drdf[retname4]=drdf[retname3]*100.0  
    
    return drdf

if __name__ =="__main__":
    ticker='000002.SZ'
    basedate="2019-1-1"
    erdf=calc_expanding_return(prdf,basedate)  

#==============================================================================
def rolling_price_volatility(df, period="Weekly"):
    """
    功能：基于单个证券价格的期间调整标准差, 计算其滚动期间价格风险
    输入：
    单个证券的日价格数据集df。
    期间类型period，默认为每周。
    输出：期间滚动价格风险序列，按照日期升序排列。
    """
    #检查period类型
    periodlist = ["Weekly","Monthly","Quarterly","Annual"]
    if not (period in periodlist):
        print("*** 错误#1(calc_rolling_volatility)，仅支持期间类型：",periodlist)
        return None

    #换算期间对应的实际交易天数
    perioddays=[5,21,63,252]
    rollingnum=perioddays[periodlist.index(period)]    
    
    #计算滚动期间的调整标准差价格风险：基于收盘价
    retname1=period+" Price Volatility"
    import numpy as np
    #df[retname1]=df["Close"].rolling(rollingnum).apply(lambda x: np.std(x,ddof=1)/np.mean(x)*np.sqrt(len(x)))
    df[retname1]=df["Close"].rolling(rollingnum,min_periods=1).apply(lambda x: np.std(x,ddof=1)/np.mean(x))
    
    #计算滚动期间的调整标准差价格风险：基于调整收盘价
    retname3=period+" Adj Price Volatility"
    #df[retname3]=df["Adj Close"].rolling(rollingnum).apply(lambda x: np.std(x,ddof=1)/np.mean(x)*np.sqrt(len(x)))
    df[retname3]=df["Adj Close"].rolling(rollingnum,min_periods=1).apply(lambda x: np.std(x,ddof=1)/np.mean(x))
    
    return df

if __name__ =="__main__":
    period="Weekly"
    df=get_price('000002.SZ','2018-1-1','2020-3-16')
    vdf=rolling_price_volatility(df, period) 

#==============================================================================
def expanding_price_volatility(df0,basedate):
    """
    功能：基于日价格数据集，从起始日期开始到结束日期调整价格风险的扩展窗口序列。
    输入：
    日价格数据集df。
    输出：期间扩展调整价格风险序列，按照日期升序排列。
    """
    import pandas as pd
    basedate_pd=pd.to_datetime(basedate)
    df=df0[df0.index >= basedate_pd]
    
    #计算扩展窗口调整价格风险：基于收盘价
    retname1="Exp Price Volatility"
    import numpy as np
    #df[retname1]=df["Close"].expanding(min_periods=1).apply(lambda x: np.std(x,ddof=1)/np.mean(x)*np.sqrt(len(x)))
    df[retname1]=df["Close"].expanding(min_periods=1).apply(lambda x: np.std(x,ddof=1)/np.mean(x))
    #df[retname1]=df["Close"].expanding(min_periods=5).apply(lambda x: np.std(x,ddof=1)/np.mean(x))
    
    #计算扩展窗口调整价格风险：基于调整收盘价
    retname3="Exp Adj Price Volatility"
    #df[retname3]=df["Adj Close"].expanding(min_periods=1).apply(lambda x: np.std(x,ddof=1)/np.mean(x)*np.sqrt(len(x)))
    df[retname3]=df["Adj Close"].expanding(min_periods=1).apply(lambda x: np.std(x,ddof=1)/np.mean(x))
    #df[retname3]=df["Adj Close"].expanding(min_periods=5).apply(lambda x: np.std(x,ddof=1)/np.mean(x))
    
    return df

if __name__ =="__main__":
    df=get_price('000002.SZ','2018-1-1','2020-3-16')    
    evdf=expanding_price_volatility(df)  


#==============================================================================
if __name__ =="__main__":
    ticker='301161.SZ'; 
    ticker='600519.SS'; 
    start='2022-1-1'; end='2024-9-30'
    pricedf,found=get_price_1ticker_mixed(ticker=ticker,fromdate=start,todate=end)
    rardf1=calc_daily_return(pricedf)
    rardf2=calc_rolling_return(rardf1,period=ret_period)
    df=rardf2
    period="Annual"

def rolling_ret_volatility(df, period="Weekly"):
    """
    功能：基于单个证券的期间收益率, 计算其滚动收益率波动风险
    输入：
    单个证券的期间收益率数据集df。
    期间类型period，默认为每周。
    输出：滚动收益率波动风险序列，按照日期升序排列。
    """
    #检查period类型
    periodlist = ["Weekly","Monthly","Quarterly","Annual"]
    if not (period in periodlist):
        print("  #Warning(rolling_ret_volatility), only support",periodlist)
        return None

    #换算期间对应的实际交易天数
    perioddays=[5,21,63,252]
    rollingnum=perioddays[periodlist.index(period)]    
    
    #计算滚动标准差：基于普通收益率
    periodret=period+" Ret"
    retname1=period+" Ret Volatility"
    retname2=retname1+'%'
    import numpy as np
    #min_periods=1: 一些股票上市期间短，可能出现数据量不足，进而导致年度波动率全为空
    df[retname1]=df[periodret].rolling(window=rollingnum,min_periods=1).apply(lambda x: np.std(x,ddof=1))
    if df[retname1].isnull().all():
        print("  #Warning(rolling_ret_volatility): "+retname1+" is all nan becos of insufficient data for period "+period)
        
    df[retname2]=df[retname1]*100.0
    
    #计算滚动标准差：基于调整收益率
    periodadjret=period+" Adj Ret"
    retname3=period+" Adj Ret Volatility"
    retname4=retname3+'%'
    df[retname3]=df[periodadjret].rolling(window=rollingnum,min_periods=1).apply(lambda x: np.std(x,ddof=1))
    df[retname4]=df[retname3]*100.0
    
    return df

if __name__ =="__main__":
    period="Weekly"
    pricedf=get_price('000002.SZ','2018-1-1','2020-3-16')
    retdf=calc_daily_return(pricedf)
    vdf=rolling_ret_volatility(retdf, period) 

#==============================================================================
def expanding_ret_volatility_x(df0,basedate):
    """
    功能：基于日收益率数据集，从起始日期basedate开始的收益率波动风险扩展窗口序列。
    输入：
    日收益率数据集df。
    输出：扩展调整收益率波动风险序列，按照日期升序排列。
    
    注意：可能存在计算错误，暂时废弃！！！
    """
    df0["Daily Ret"]=df0['Close'].pct_change()
    df0["Daily Adj Ret"]=df0['Adj Close'].pct_change()
    
    import pandas as pd
    basedate_pd=pd.to_datetime(basedate)
    df=df0[df0.index >= basedate_pd]
    
    #计算扩展窗口调整收益率波动风险：基于普通收益率
    retname1="Exp Ret Volatility"
    retname2="Exp Ret Volatility%"
    import numpy as np
    
    #df[retname1]=df["Daily Ret"].expanding(min_periods=1).apply(lambda x: np.std(x,ddof=1)*np.sqrt(len(x)))
    df[retname1]=df["Daily Ret"].expanding(min_periods=1).apply(lambda x: np.std(x,ddof=1))
    #df[retname1]=df["Daily Ret"].expanding(min_periods=5).apply(lambda x: np.std(x,ddof=1))
    df[retname2]=df[retname1]*100.0
    
    #计算扩展窗口调整收益率风险：基于调整收益率
    retname3="Exp Adj Ret Volatility"
    retname4="Exp Adj Ret Volatility%"
    #df[retname3]=df["Daily Adj Ret"].expanding(min_periods=1).apply(lambda x: np.std(x,ddof=1)*np.sqrt(len(x)))
    df[retname3]=df["Daily Adj Ret"].expanding(min_periods=1).apply(lambda x: np.std(x,ddof=1))
    #df[retname3]=df["Daily Adj Ret"].expanding(min_periods=5).apply(lambda x: np.std(x,ddof=1))
    df[retname4]=df[retname3]*100.0
    
    return df

#==============================================================================
def expanding_ret_volatility(df0,basedate,min_periods=1):
    """
    功能：基于日收益率数据集，从起始日期basedate开始的收益率波动风险扩展窗口序列。
    输入：
    日收益率数据集df。
    输出：扩展调整收益率波动风险序列，按照日期升序排列。
    
    新算法：解决开始部分过度波动问题
    """
    collist=list(df0)

    if not ("Daily Ret" in collist):
        df0["Daily Ret"]=df0['Close'].pct_change()
        #df0["Daily Ret"]=df0["Daily Ret"].fillna(method='bfill', axis=1)
        df0["Daily Ret"]=df0["Daily Ret"].interpolate()

    if not ("Daily Adj Ret" in collist):    
        df0["Daily Adj Ret"]=df0['Adj Close'].pct_change()
        #df0["Daily Adj Ret"]=df0["Daily Adj Ret"].fillna(method='bfill', axis=1)
        df0["Daily Adj Ret"]=df0["Daily Adj Ret"].interpolate()
    
    import pandas as pd
    basedate_pd=pd.to_datetime(basedate)
    df=df0[df0.index >= basedate_pd]
    
    # 计算Exp Ret和Exp Adj Ret
    if not ('Exp Ret' in collist):
        df['Exp Ret'] = (1 + df['Daily Ret']).cumprod() - 1
        df['Exp Ret%'] = df['Exp Ret'] * 100.0
        
    if not ('Exp Adj Ret' in collist):
        df['Exp Adj Ret'] = (1 + df['Daily Adj Ret']).cumprod() - 1
        df['Exp Adj Ret%'] = df['Exp Adj Ret'] * 100.0  
        
    #计算扩展窗口调整收益率波动风险：基于普通收益率
    retname1="Exp Ret Volatility"
    retname2="Exp Ret Volatility%"
    #import numpy as np
    
    #df[retname1]=df["Exp Ret"].expanding(min_periods=min_periods).std(ddof=1)
    df[retname1]=df["Exp Ret"].expanding().std(ddof=1)
    df[retname2]=df[retname1]*100.0
    
    #计算扩展窗口调整收益率风险：基于调整收益率
    retname3="Exp Adj Ret Volatility"
    retname4="Exp Adj Ret Volatility%"
    #df[retname3]=df["Exp Adj Ret"].expanding(min_periods=min_periods).std(ddof=1)
    df[retname3]=df["Exp Adj Ret"].expanding().std(ddof=1)
    df[retname4]=df[retname3]*100.0
    
    return df

if __name__ =="__main__":
    basedate='2019-1-1'
    pricedf=get_price('000002.SZ','2018-1-1','2020-3-16')    
    retdf=calc_daily_return(pricedf)
    evdf=expanding_ret_volatility(retdf,'2019-1-1')  

#==============================================================================
def lpsd(ds):
    """
    功能：基于给定数据序列计算其下偏标准差。
    输入：
    数据序列ds。
    输出：序列的下偏标准差。
    """
    import numpy as np
    #若序列长度为0则直接返回数值型空值
    if len(ds) == 0: return np.nan
    
    #求均值
    import numpy as np
    miu=np.mean(ds)
    
    #计算根号内的下偏平方和
    sum=0; ctr=0
    for s in list(ds):
        if s < miu:
            sum=sum+pow((s-miu),2)
            ctr=ctr+1
    
    #下偏标准差
    if ctr > 1:
        result=np.sqrt(sum/(ctr-1))
    elif ctr == 1: result=np.nan
    else: result=np.nan
        
    return result
    
if __name__ =="__main__":
    df=get_price("000002.SZ","2020-1-1","2020-3-16")
    print(lpsd(df['Close']))

import numpy as np

def downside_std(returns, target_return=0):
    """
    功能：计算下偏标准差（下方风险）
    注意：暂时弃用，因为容易引起float divided zero问题。
    """
    downside_diff = np.maximum(target_return - returns, 0)
    return np.sqrt(np.mean(downside_diff ** 2))

#==============================================================================
def rolling_ret_lpsd(df, period="Weekly"):
    """
    功能：基于单个证券期间收益率, 计算其滚动收益率损失风险。
    输入：
    单个证券的期间收益率数据集df。
    期间类型period，默认为每周。
    输出：滚动收益率的下偏标准差序列，按照日期升序排列。
    """
    #检查period类型
    periodlist = ["Weekly","Monthly","Quarterly","Annual"]
    if not (period in periodlist):
        print("*** 错误#1(rolling_ret_lpsd)，仅支持期间类型：",periodlist)
        return None

    #换算期间对应的实际交易天数
    perioddays=[5,21,63,252]
    rollingnum=perioddays[periodlist.index(period)]    
    
    #计算滚动下偏标准差：基于普通收益率
    periodret=period+" Ret"
    retname1=period+" Ret LPSD"
    retname2=retname1+'%'
    #import numpy as np
    df[retname1]=df[periodret].rolling(rollingnum,min_periods=1).apply(lambda x: lpsd(x))
    #df[retname1]=df[periodret].rolling(rollingnum,min_periods=1).apply(downside_std, raw=True)
    df[retname2]=df[retname1]*100.0
    
    #计算滚动下偏标准差：基于调整收益率
    periodadjret=period+" Adj Ret"
    retname3=period+" Adj Ret LPSD"
    retname4=retname3+'%'
    df[retname3]=df[periodadjret].rolling(rollingnum,min_periods=1).apply(lambda x: lpsd(x))
    #df[retname3]=df[periodadjret].rolling(rollingnum,min_periods=1).apply(downside_std, raw=True)
    df[retname4]=df[retname3]*100.0
    
    return df

if __name__ =="__main__":
    period="Weekly"
    pricedf=get_price('000002.SZ','2018-1-1','2020-3-16')
    retdf=calc_daily_return(pricedf)
    vdf=rolling_ret_lpsd(retdf, period) 

#==============================================================================
def expanding_ret_lpsd_x(df0,basedate,min_periods=1):
    """
    功能：基于日收益率数据集，从起始日期basedate开始的收益率损失风险扩展窗口序列。
    输入：
    日收益率数据集df。
    输出：扩展调整收益率波动风险序列，按照日期升序排列。
    
    注意：算法可能存在错误，暂时废弃！！！
    """
    df0["Daily Ret"]=df0['Close'].pct_change()
    df0["Daily Adj Ret"]=df0['Adj Close'].pct_change()
    
    import pandas as pd
    basedate_pd=pd.to_datetime(basedate)
    df=df0[df0.index >= basedate_pd]
    
    #计算扩展窗口调整收益率下偏标准差：基于普通收益率
    retname1="Exp Ret LPSD"
    retname2=retname1+'%'
    import numpy as np
    #df[retname1]=df["Daily Ret"].expanding(min_periods=1).apply(lambda x: lpsd(x)*np.sqrt(len(x)))
    df[retname1]=df["Daily Ret"].expanding(min_periods=min_periods).apply(lambda x: lpsd(x))
    #df[retname1]=df["Daily Ret"].expanding(min_periods=5).apply(lambda x: lpsd(x))
    df[retname2]=df[retname1]*100.0
    
    #计算扩展窗口调整下偏标准差：基于调整收益率
    retname3="Exp Adj Ret LPSD"
    retname4=retname3+'%'
    #df[retname3]=df["Daily Adj Ret"].expanding(min_periods=1).apply(lambda x: lpsd(x)*np.sqrt(len(x)))
    df[retname3]=df["Daily Adj Ret"].expanding(min_periods=min_periods).apply(lambda x: lpsd(x))
    #df[retname3]=df["Daily Adj Ret"].expanding(min_periods=5).apply(lambda x: lpsd(x))
    df[retname4]=df[retname3]*100.0
    
    return df

#==============================================================================
def expanding_ret_lpsd(df0,basedate,min_periods=1):
    """
    功能：基于日收益率数据集，从起始日期basedate开始的收益率损失风险扩展窗口序列。
    输入：
    日收益率数据集df。
    输出：扩展调整收益率波动风险序列，按照日期升序排列。
    
    新算法：解决开始部分过度波动的诡异现象
    """
    collist=list(df0)
    
    if not ("Daily Ret" in collist):
        df0["Daily Ret"]=df0['Close'].pct_change()
        #df0["Daily Ret"]=df0["Daily Ret"].fillna(method='bfill', axis=1)
        df0["Daily Ret"]=df0["Daily Ret"].interpolate()

    if not ("Daily Adj Ret" in collist):
        df0["Daily Adj Ret"]=df0['Adj Close'].pct_change()
        #df0["Daily Adj Ret"]=df0["Daily Adj Ret"].fillna(method='bfill', axis=1)
        df0["Daily Adj Ret"]=df0["Daily Adj Ret"].interpolate()
    
    import pandas as pd
    basedate_pd=pd.to_datetime(basedate)
    df=df0[df0.index >= basedate_pd]
    
    # 计算Exp Ret和Exp Adj Ret
    if not ('Exp Ret' in collist):
        df['Exp Ret'] = (1 + df['Daily Ret']).cumprod() - 1
        df['Exp Ret%'] = df['Exp Ret'] * 100.0
        
    if not ('Exp Adj Ret' in collist):
        df['Exp Adj Ret'] = (1 + df['Daily Adj Ret']).cumprod() - 1
        df['Exp Adj Ret%'] = df['Exp Adj Ret'] * 100.0  
    
    #计算扩展窗口调整收益率下偏标准差：基于普通收益率
    retname1="Exp Ret LPSD"
    retname2=retname1+'%'
    import numpy as np
    #df[retname1]=df["Exp Ret"].expanding(min_periods=min_periods).apply(lambda x: lpsd(x))
    df[retname1]=df["Exp Ret"].expanding().apply(lambda x: lpsd(x))
    #df[retname1]=df["Exp Ret"].expanding().apply(downside_std, raw=True)
    df[retname2]=df[retname1]*100.0
    
    #计算扩展窗口调整下偏标准差：基于调整收益率
    retname3="Exp Adj Ret LPSD"
    retname4=retname3+'%'
    #df[retname3]=df["Exp Adj Ret"].expanding(min_periods=min_periods).apply(lambda x: lpsd(x))
    df[retname3]=df["Exp Adj Ret"].expanding().apply(lambda x: lpsd(x))
    #df[retname3]=df["Exp Adj Ret"].expanding().apply(downside_std, raw=True)
    df[retname4]=df[retname3]*100.0
    
    return df


if __name__ =="__main__":
    basedate='2019-1-1'
    pricedf=get_price('000002.SZ','2018-1-1','2020-3-16')    
    retdf=calc_daily_return(pricedf)
    evdf=expanding_ret_lpsd(retdf,'2019-1-1')  
#==============================================================================
if __name__ =="__main__":
    portfolio={'Market':('US','^GSPC'),'AAPL':1}
    portfolio={'Market':('China','^HSI'),'0823.HK':1.0}
    portfolio={'Market':('China','000001.SS'),'000661.SZ':2,'603392.SS':3,'300601.SZ':4}
    portfolio={'Market':('US','^SPX'),'^SPX':1}
    
    fromdate='2019-7-19'
    todate='2020-7-20'
    
    market={"Market":("China","000300.SS","我的地产组合")}
    stocks1={"600048.SS":.4,"001979":.3}
    stocks2={"600515.SS":.2,"600895":.1}
    portfolio=dict(market,**stocks1,**stocks2)
    
    fromdate="2024-1-1"; todate="2024-11-25"
    adj=False
    source='auto'
    
    df=get_portfolio_prices(portfolio,fromdate,todate,adj=False,source='auto')

def get_portfolio_prices(portfolio,fromdate,todate,adj=True,source='auto',RF=0):
    """
    功能：抓取投资组合portfolio的每日价值和FF3各个因子
    输入：投资组合portfolio，开始日期，结束日期
    fromdate: 样本开始日期。格式：'YYYY-MM-DD'
    todate: 样本结束日期。既可以是今天日期，也可以是一个历史日期    
    
    输出：投资组合的价格序列，按照日期升序排列
    """
    
    #解构投资组合
    _,mktidx,tickerlist,sharelist,ticker_type=decompose_portfolio(portfolio)
    
    #检查股票列表个数与份额列表个数是否一致
    if len(tickerlist) != len(sharelist):
        print("  #Error(get_portfolio_prices): numbers of stocks and shares mismatch.")
        return None        
    
    #抓取股票价格
    #print("  Searching portfolio prices for",tickerlist,'from',fromdate,'to',todate)
    p=get_prices(tickerlist,fromdate,todate,adj=adj,source=source)
    if p is None:
        print("  #Error(get_portfolio_prices): information inaccessible for",tickerlist)
        return None  

    #print("  Retrieved",len(p),'records of portfolio records')
    import pandas as pd
    if len(sharelist) > 0:    
        #计算投资组合的开盘价
        op=pd.DataFrame(p['Open'])
        #计算投资组合的价值
        try:
            oprice=pd.DataFrame(op.dot(sharelist))
        except:
            print("  #Error(get_portfolio_prices): Dot product shape mismatch for open price",tickerlist)
            return None
        oprice.rename(columns={0: 'Open'}, inplace=True)    

        #计算投资组合的收盘价
        cp=pd.DataFrame(p['Close'])
        #计算投资组合的价值
        cprice=pd.DataFrame(cp.dot(sharelist))
        cprice.rename(columns={0: 'Close'}, inplace=True) 
        
        #计算投资组合的调整收盘价
        acp=pd.DataFrame(p['Adj Close'])
        #计算投资组合的价值
        acprice=pd.DataFrame(acp.dot(sharelist))
        acprice.rename(columns={0: 'Adj Close'}, inplace=True) 
    
        #计算投资组合的交易量
        vol=pd.DataFrame(p['Volume'])
        #计算投资组合的价值
        pfvol=pd.DataFrame(vol.dot(sharelist))
        pfvol.rename(columns={0: 'Volume'}, inplace=True) 
    
        #计算投资组合的交易金额
        if len(sharelist) > 1:
            for t in tickerlist:
                p['Amount',t]=p['Close',t]*p['Volume',t]
        elif len(sharelist) == 1:
            p['Amount']=p['Close']*p['Volume']
        amt=pd.DataFrame(p['Amount'])
        
        #计算投资组合的价值
        pfamt=pd.DataFrame(amt.dot(sharelist))
        pfamt.rename(columns={0: 'Amount'}, inplace=True) 

        #合成开盘价、收盘价、调整收盘价、交易量和交易金额
        pf1=pd.merge(oprice,cprice,how='inner',left_index=True,right_index=True)    
        pf2=pd.merge(pf1,acprice,how='inner',left_index=True,right_index=True)
        pf3=pd.merge(pf2,pfvol,how='inner',left_index=True,right_index=True)
        pf4=pd.merge(pf3,pfamt,how='inner',left_index=True,right_index=True)
    """
    else:
        p['Amount']=p['Close']*p['Volume']
        pf4=p
    """
    pf4['Ret%']=pf4['Close'].pct_change()*100.0
    pf4['Ret-RF']=pf4['Ret%'] - RF*100/365

    #获得期间的市场收益率
    try:
        m=get_prices(mktidx,fromdate,todate)
    except:
        print("  #Error(get_portfolio_prices): info inaccesible for market index",mktidx)
        return None
    
    m['Mkt-RF']=m['Close'].pct_change()*100.0 - RF*100/365
    m['RF']=RF*100/365
    rf_df=m[['Mkt-RF','RF']]
    
    #合并pf4与rf_df
    prices=pd.merge(pf4,rf_df,how='left',left_index=True,right_index=True)

    #提取日期和星期几
    #prices['Date']=(prices.index).strftime("%Y-%m-%d")
    prices['Date']=prices.index
    prices['Date']=prices['Date'].apply(lambda x: x.strftime("%Y-%m-%d"))
    
    prices['Weekday']=prices.index.weekday+1

    prices['Portfolio']=str(tickerlist)
    prices['Shares']=str(sharelist)
    
    prices['Adjustment']=adj
    try:
        prices['Adjustment']=prices.apply(lambda x: \
          False if x['Close']==x['Adj Close'] else True, axis=1)
    except: pass
    
    pfdf=prices[['Portfolio','Shares','Date','Weekday', \
                 'Open','Close','Adj Close','Adjustment', \
                'Volume','Amount','Ret%','Ret-RF','Mkt-RF','RF']]  

    return pfdf      


#==============================================================================
if __name__ =="__main__":
    ticker='AAPL'  

def recent_stock_split(ticker):
    """
    功能：显示股票最近一年的分拆历史
    输入：单一股票代码
    输出：最近一年的分拆历史
    """   
    #获取今日日期
    import datetime
    today = datetime.date.today()
    fromdate = date_adjust(today,-365)
    
    import yfinance as yf
    stock = yf.Ticker(ticker)
    try:
        div=stock.splits
    except:
        print("#Error(recent_stock_split): no split info found for",ticker)
        return None    
    if len(div)==0:
        print("#Warning(recent_stock_split): no split info found for",ticker)
        return None      
    
    #过滤期间
    div2=div[div.index >= fromdate]
    if len(div2)==0:
        print("#Warning(stock_split): no split info from",fromdate,'to',today)
        return None          
    
    #对齐打印
    import pandas as pd    
    pd.set_option('display.max_columns', 1000)
    pd.set_option('display.width', 1000)
    pd.set_option('display.max_colwidth', 1000)
    
    divdf=pd.DataFrame(div2)
    divdf['Index Date']=divdf.index
    datefmt=lambda x : x.strftime('%Y-%m-%d')
    divdf['Split Date']= divdf['Index Date'].apply(datefmt)
    
    #增加星期
    from datetime import datetime
    weekdayfmt=lambda x : x.isoweekday()
    divdf['Weekdayiso']= divdf['Index Date'].apply(weekdayfmt)
    wdlist=['Mon','Tue','Wed','Thu','Fri','Sat','Sun']
    wdfmt=lambda x : wdlist[x-1]
    divdf['Weekday']= divdf['Weekdayiso'].apply(wdfmt)
    
    #增加序号
    divdf['Seq']=divdf['Split Date'].rank(ascending=1)
    divdf['Seq']=divdf['Seq'].astype('int')
    
    divdf['Splitint']=divdf['Stock Splits'].astype('int')
    splitfmt=lambda x: "1:"+str(x)
    divdf['Splits']=divdf['Splitint'].apply(splitfmt)
    
    divprt=divdf[['Seq','Split Date','Weekday','Splits']]
    
    print(text_lang("\n=== 近期股票分拆历史 ===","\n=== Recent Stock Split ==="))
    print(text_lang("股票:","Stock:"),ticker,'\b,',ticker)
    print(text_lang("期间:","Period:"),fromdate,"to",today)
    divprt.columns=[text_lang('序号','No.'),text_lang('日期','Date'),text_lang('星期','Weekday'),text_lang('分拆比例','Split Ratio')]
    print(divprt.to_string(index=False))   
    
    import datetime
    today = datetime.date.today()
    print(text_lang("数据来源: 综合新浪/yahoo,","Data source: Yahoo Finance,"),today)
    
    return divdf
    
    
if __name__ =="__main__":
    df=recent_stock_split('AAPL')

#==============================================================================
if __name__ =="__main__":
    ticker='AAPL'
    get_last_close(ticker)

def get_last_close(ticker):
    """
    功能：从新浪/stooq抓取股票股价或指数价格或投资组合价值，使用pandas_datareader
    输入：股票代码或股票代码列表，开始日期，结束日期
    ticker: 股票代码或者股票代码列表。
    大陆股票代码加上后缀.SZ或.SS，港股代码去掉前导0加后缀.HK
    输出：最新的收盘价和日期
    """
    #获取今日日期
    import datetime
    stoday = datetime.date.today()
    fromdate = date_adjust(stoday,-30)
    todate=str(stoday)
    
    #抓取新浪/stooq股票价格
    try:
        #price,found=get_price_1ticker_mixed(ticker,fromdate=fromdate,todate=todate,source='yahoo')
        price,found=get_price_1ticker_mixed(ticker,fromdate=fromdate,todate=todate)
    except:
        print("\n  #Error(get_last_close): failed in retrieving prices for",ticker)        
        return None,None            
    if price is None:
        print("\n  #Error(get_last_close): retrieved none info for",ticker)
        return None,None  
    if len(price)==0:
        print("\n  #Error(get_last_close): retrieved empty info for",ticker)
        return None,None         
    
    price['date']=price.index
    datecvt=lambda x:x.strftime("%Y-%m-%d")
    price['date']=price['date'].apply(datecvt)
    price.sort_values("date",inplace=True)

    #提取最新的日期和收盘价
    lasttradedate=list(price['date'])[-1]
    lasttradeclose=round(list(price['Close'])[-1],2)

    return lasttradedate,lasttradeclose

if __name__ =="__main__":
    get_last_close('AAPL')

#==============================================================================

if __name__=='__main__':
    security={'Market':('US','^SPX','中概教培组合'),'EDU':0.4,'TAL':0.3,'TCTM':0.2}
    security={'Market':('US','^SPX','China Edtraining'),'X01':0.4,'X02':0.3,'X03':0.2}
    security={'Market':('China','000300.SS','China Edtraining'),'600519.SS':0.4,'000858.SZ':0.3,'600809.SS':0.2}
    security={'Market':('China','auto','China Edtraining'),'600519.SS':0.4,'000858.SZ':0.3,'600809.SS':0.2}
    security='600519.SS'
    
    start='2024-1-1'; end='2024-3-23'
    source='auto'
    
    prices=get_price_security(security,start,end)
    
def get_price_security(security,start,end,source='auto'):
    """
    功能：获取股票或投资组合的价格
    经测试已经可以支持capm_beta2，risk_adjusted_return待测试？
    """
    
    if isinstance(security,dict): #投资组合
        scope,mktidx,tickerlist,sharelist,ticker_type=decompose_portfolio(security)
        prices=get_price_portfolio(tickerlist,sharelist,start,end,source=source)  

        pname=portfolio_name(security)
        if prices is None:
            print("  #Error(get_price_security): no price info retrieved for portfolio",pname)
            return None
        if len(prices) ==0:
            print("  #Error(get_price_security): zero info retrieved for portfolio",pname)  
            return None
    else: #股票或股票列表
        prices=get_price(security,start,end,source=source)  
        if prices is None:
            print("  #Error(get_price_security): no price info retrieved for",security)
            return None
        if len(prices) ==0:
            print("  #Error(get_price_security): zero info retrieved for",security)  
            return None

    return prices        
        
#==============================================================================
if __name__=='__main__':
    ticker='600519.SS'
    ticker='000858.SZ'
    
    ticker='SH600519'
    ticker='sh600519'
    ticker='sz000858'
    
    ticker='sz600519'
    ticker='sh000858'
    
    ticker='600519.SH'
    ticker='600519.sh'
    ticker='000858.sz'
    
    ticker='000858.sh'
    ticker='600519.sz'
    
    ticker='600519'
    ticker='000858'
    ticker='600519.CN'
    ticker='000858.CN'
    ticker='801010.SW'
    ticker='880410.ZZ'
    
    ticker='01210.HK'
    ticker='AAPL'
    ticker='6758.T'
    ticker='SONA.F'
    
    ticker1_cvt2yahoo(ticker)
    
def ticker1_cvt2yahoo(ticker):
    """
    功能：将一只股票、基金、债券代码转换为siat内部默认的yahoo格式
    情形：后缀，前缀，无后缀和前缀
    注意：中证行业代码若为沪深交易所收藏的，仍以SS/SZ为后缀，不可用ZZ后缀
    """
    ticker1=ticker.upper() #转为大写
    
    #后缀
    result,prefix,suffix=split_prefix_suffix(ticker1)
    if suffix in ['SS','SH','SZ','BJ','CN','SW','ZZ'] and len(prefix)==6:
        if suffix in ['SH']:
            suffix1='SS'
        elif suffix in ['CN']:
            suffix1,_=china_security_identify(prefix)
        else:
            suffix1=suffix
            
        """
        #检查是否搞错SS/SZ/BJ
        if suffix1 in ['SS','SZ','BJ']:
            suffix1,_=china_security_identify(prefix)
        """
        ticker2=prefix+'.'+suffix1            
        return ticker2

    #前缀
    head2=ticker1[:2]
    rest2=ticker1[2:]
    if head2 in ['SH','SZ','BJ','SW','ZZ'] and len(rest2)==6:
        #suffix1,_=china_security_identify(rest2)
        if head2 in ['SH']:
            suffix1='SS'
        else:
            suffix1=head2
        """    
        #检查是否搞错SS/SZ/BJ
        if suffix1 in ['SS','SZ','BJ']:
            suffix1,_=china_security_identify(rest2)
        """    
        ticker2=rest2+'.'+suffix1            
        return ticker2

    #无前后缀，6位数字，默认为A股
    if is_all_digits(ticker1) and len(ticker1) == 6:    
        suffix1,_=china_security_identify(ticker1)
        ticker2=ticker1+'.'+suffix1            
        return ticker2

    #其他：直接返回
    return ticker1
    
#==============================================================================
if __name__=='__main__':
    ticker=['600519.SS','sz000858','002594.sz','aapl']

    tickers_cvt2yahoo(ticker)

def tickers_cvt2yahoo(ticker):
    """
    功能：将多只股票、基金、债券代码转换为siat内部默认的yahoo格式
    """
    #单个字符串：返回字符串
    if isinstance(ticker,str):
        result=ticker1_cvt2yahoo(ticker)    
        return result

    #列表：返回列表    
    if isinstance(ticker,list): #避免下面的循环出错
        tickerlist=[]
        for t in ticker:
            t2=ticker1_cvt2yahoo(t)
            tickerlist=tickerlist+[t2]
        
        result=tickerlist
        return result
    
    #其他：直接返回
    return ticker    

#==============================================================================
if __name__=='__main__':
    ticker='SH600519'
    ticker='sh600519'
    ticker='sz000858'
    
    ticker='sz600519'
    ticker='sh000858'
    
    ticker='600519.SH'
    ticker='600519.sh'
    ticker='000858.sz'
    
    ticker='000858.sh'
    ticker='600519.sz'
    
    ticker='600519'
    ticker='000858'
    ticker='600519.CN'
    ticker='000858.CN'
    ticker='801010.SW'
    ticker='880410.ZZ'
    
    ticker='sh149996'
    
    ticker='01210.HK'
    ticker='AAPL'
    ticker='6758.T'
    ticker='SONA.F'
    
    ticker1_cvt2ak(ticker)
    
def ticker1_cvt2ak(ticker):
    """
    功能：将一只股票、基金、债券代码转换为akshare格式
    情形：后缀，前缀，无后缀和前缀
    注意：中证行业代码若为沪深交易所收藏的，仍以SS/SZ为后缀，不可用ZZ后缀
    """
    ticker1=ticker.upper() #转为大写
    
    #后缀
    result,prefix,suffix=split_prefix_suffix(ticker1)
    if suffix in ['SS','SH','SZ','BJ','CN'] and len(prefix)==6:
        if suffix in ['SH','SS']: prefix1='sh'
        if suffix in ['SZ']: prefix1='sz'
        if suffix in ['BJ']: prefix1='bj'
        if suffix in ['CN']:            
            suffix1,_=china_security_identify(prefix)
            prefix1='sh'
            if suffix1 in ['SS']: prefix1='sh'
            if suffix1 in ['SZ']: prefix1='sz'
            if suffix1 in ['BJ']: prefix1='bj'
        """
        #检查是否搞错SS/SZ/BJ
        if suffix in ['SS','SH','SZ','BJ']:
            suffix1,_=china_security_identify(prefix)
            if suffix1 in ['SS','SH']: prefix1='sh'
            if suffix1 == 'SZ': prefix1='sz'
            if suffix1 == 'BJ': prefix1='bj'
        """
        ticker2=prefix1+prefix            
        return ticker2

    #前缀
    head2=ticker1[:2]
    rest2=ticker1[2:]
    if head2 in ['SH','SS','SZ','BJ'] and len(rest2)==6:
        if head2 in ['SH','SS']: prefix1='sh'
        if head2 in ['SZ']: prefix1='sz'
        if head2 in ['BJ']: prefix1='bj'
        
        """            
        #检查是否搞错SS/SZ/BJ
        if head2 in ['SH','SS','SZ','BJ']:
            suffix1,_=china_security_identify(rest2)
            if suffix1 == 'SS': prefix1='sh'
            if suffix1 == 'SZ': prefix1='sz'
            if suffix1 == 'BJ': prefix1='bj'
        """    
        ticker2=prefix1+rest2            
        return ticker2

    #无前后缀，6位数字，默认为A股
    if is_all_digits(ticker1) and len(ticker1) == 6:    
        suffix1,_=china_security_identify(ticker1)
        prefix1='sh'
        if head2 in ['SH','SS']: prefix1='sh'
        if head2 in ['SZ']: prefix1='sz'
        if head2 in ['BJ']: prefix1='bj'
        
        ticker2=prefix1+ticker1            
        return ticker2

    #其他：直接返回
    return ticker1
    
#==============================================================================
if __name__=='__main__':
    ticker=['600519.SS','sz000858','002594.sz','aapl']

    tickers_cvt2ak(ticker)

def tickers_cvt2ak(ticker):
    """
    功能：将多只股票、基金、债券代码转换为akshare格式
    """
    #单个字符串：返回字符串
    if isinstance(ticker,str):
        result=ticker1_cvt2ak(ticker)    
        return result

    #列表：返回列表    
    if isinstance(ticker,list): #避免下面的循环出错
        tickerlist=[]
        for t in ticker:
            t2=ticker1_cvt2ak(t)
            tickerlist=tickerlist+[t2]
        
        result=tickerlist
        return result
    
    #其他：直接返回
    return ticker    


#==============================================================================
if __name__=='__main__':
    s='123456'
    s='123456.'
    s='123456a'

    is_all_digits(s)
 
def is_all_digits(s):
    """
    功能：检查字符串s是否为全数字构成
    """
    import re
    return bool(re.match(r'^\d+$', s))

#==============================================================================
if __name__=='__main__':
    ticker6='AAPL'
    ticker6='01211'
    ticker6='600519'
    ticker6='149996'
    
def china_security_identify(ticker6):
    """
    功能：区分中国内地证券代码前缀，返回后缀SS/SZ/BJ
    情形：股票，基金，债券，指数
    注意：ticker6需为6位数字字符，目前仅限沪深京交易所，未包括期货期权交易所
    """
    suffix='SS'
    stype='stock'
    
    #检查是否为6位数字字符
    if not is_all_digits(ticker6) or len(ticker6) != 6:
        suffix=''
        stype=''
        return suffix,stype
        
    head1=ticker6[:1]
    head2=ticker6[:2]
    head3=ticker6[:3]
    
    #股票代码
    if head2 in ['60','68']: #上交所：60-主板，68-科创板
        suffix='SS'
        stype='stock'
        return suffix,stype
    if head2 in ['00','30']: #深交所：00-主板，30-创业板
        suffix='SZ'
        stype='stock'
        return suffix,stype
    if head1 in ['8']: #北交所
        suffix='BJ'  
        stype='stock'
        return suffix,stype
    
    #沪深基金
    if head2 in ['50','51']: #上交所：50-封闭式，51-ETF
        suffix='SS'
        stype='fund'
        return suffix,stype
    if head2 in ['15','16','18']: #深交所：15-ETF，16-LOF，18-封闭式
        suffix='SZ'
        stype='fund'
        return suffix,stype
    
    #沪深债券
    if head3 in ['271','270','240','188','185','184','175','163','155','152', \
                 '143','138','137','136','127','124','122','118','115','113', \
                 '100','020','019','018','010']:
        suffix='SS'
        stype='bond'
        return suffix,stype
    
    #有重复
    if head3 in ['149','148','133','128','127','123','114','112','111','110', \
                 '108','102','101','100']:
        suffix='SZ'
        stype='bond'
        return suffix,stype
    
    #沪深B股
    if head3 in ['900']:
        suffix='SS'
        stype='stockb'
        return suffix,stype
    if head3 in ['200']:
        suffix='SZ'
        stype='stockb'
        return suffix,stype  

    #其他
    return '',''    
    
#==============================================================================
if __name__=='__main__':
    ticker='850831.SW'
    
    start='2024-1-1'
    end='2024-4-4'
    info_types=['Close','Volume']
    
    df3=fetch_price_swindex(ticker,start,end)

def fetch_price_swindex(ticker,start,end,info_types=['Close','Volume'],adjust=-2*365):
    """
    功能：获取申万行业指数的信息
    ticker：申万行业指数
    start,end：日期期间
    info_types：信息测度，默认['Close']，还可以为['Close','Open','High','Low',
                                     'Volume','Adj Close']
    特点：为compare_indicator使用，包括指数名称
    
    """
    df=None
    
    # 检查日期期间的合理性
    result,startpd,endpd=check_period(start,end)
    if not result:
        #print("  #Error(fetch_price_swindex): invalid date period between",start,"and",end)
        return None
    
    start1=date_adjust(start,adjust=adjust)
    _,start1pd,_=check_period(start1,end)
    
    import akshare as ak
    if len(ticker)==6:
        ticker=ticker+'.SW'
    ticker6=ticker[:6]
    try:
        # 注意：如果失败，尝试升级akshare
        prices= ak.index_hist_sw(symbol=ticker6,period="day")
    except: 
        try:
            dft = ak.index_hist_fund_sw(symbol=ticker6,period="day")
            dft['代码']=ticker6
            dft['收盘']=dft['收盘指数']
            dft['开盘']=dft['收盘指数']
            dft['最高']=dft['收盘指数']
            dft['最低']=dft['收盘指数']
            dft['成交量']=0; dft['成交额']=0
            
            prices=dft
        except:        
            print("  #Error(fetch_price_swindex): failed to fetch prices for",ticker)
            return None

    found=df_have_data(prices)
    if found not in ['Found','Empty']: 
        pass
        return df

    #强制修改列名
    #prices.columns=['Code','Date','Close','Open','High','Low','Volume','Amount']
    prices.rename(columns={'代码':'Code','日期':'Date','收盘':'Close','开盘':'Open', \
                           '最高':'High','最低':'Low','成交量':'Volume','成交额':'Amount'}, inplace=True)
    
    million=1000000
    prices['Volume']=prices['Volume']*million
    prices['Amount']=prices['Amount']*million
    
    import pandas as pd
    prices['date']=pd.to_datetime(prices['Date'])
    prices.set_index('date',inplace=True)
    
    prices2=prices[(prices.index >= start1pd) & (prices.index <= endpd)]

    
    if isinstance(info_types,str):
        typelist=[info_types]
    else:
        typelist=info_types

    import pandas as pd
    df=pd.DataFrame()
        
    for t in typelist:
        try:
            df[t]=prices2[t]
        except:
            continue

    collist=list(df)
    pcollist=['Open','High','Low','Adj Close']
    for p in pcollist:
        if p not in collist:
            df[p]=df['Close']
        
    df['Code']=ticker
    df['Type']='swindex'
    df['Name']=ticker_name(ticker)
    
    #print("  Successfully retrieved",len(df),"records for sw index",ticker)
    
    return df

#==============================================================================
if __name__=='__main__':
    ticker='sh018003'
    fromdate='2024-1-1'
    todate='2024-4-17'
    trend_type='净值'
    
    f=get_price_oef_china(ticker,fromdate,todate)

def get_price_oef_china(ticker,fromdate,todate):
    """
    功能：单纯获取中国开放式基金的单位净值趋势
    """
    #检查日期
    result,start,end=check_period(fromdate,todate)
    if not result:
        print("  #Error(get_price_oef_china): invalid date period:",fromdate,todate)
        return None

    #print("Searching for open-ended fund (OEF) trend info in China ...")
    import akshare as ak   

    fund1=ticker[:6]; fund2=ticker[-6:]
    if fund1.isdigit():
        fund=fund1
    elif fund2.isdigit():
        fund=fund2
    else:
        fund=ticker
        
    fund_name=ticker_name(fund,'fund')

    #单位净值
    found='None'; df2=None
    try:
        df1 = ak.fund_open_fund_info_em(fund, indicator="单位净值走势")
        df1.rename(columns={'净值日期':'date','单位净值':'Close'}, inplace=True)
        df1['Open']=df1['High']=df1['Low']=df1['Close']
        df1['Volume']=0
        df1['name']=ticker_name(fund,'fund')
        
        df1['date']=df1['date'].apply(lambda x: pd.to_datetime(x))
        df1.set_index(['date'],inplace=True) 
            
        df2=df1[['Open','Close','High','Low','Volume','name']]
        df2=df2[(df2.index >= start) & (df2.index <= end)]
        
        if len(df2)==0:
            found='Empty'
        else:
            found='Found'    
    except:
        pass
    
    return df2    

#==============================================================================

#==============================================================================
#==============================================================================
#==============================================================================
