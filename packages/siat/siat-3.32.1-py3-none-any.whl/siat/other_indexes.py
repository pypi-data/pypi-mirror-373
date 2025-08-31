# -*- coding: utf-8 -*-
"""
本模块功能：另类证券市场指数
所属工具包：证券投资分析工具SIAT 
SIAT：Security Investment Analysis Tool
创建日期：2025年5月8日
最新修订日期：
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
#==============================================================================


def other_index_translate(index_code):
    """
    ===========================================================================
    功能：另类证券市场指数代码
    参数：
    index_code: 指数代码，非标准，来自东方财富和新浪。
    返回值：是否找到，基于语言环境为中文或英文解释。
    语言环境判断为check_language()
    
    数据结构：['指数代码','指数符号','指数名称中文','指数名称英文','数据来源']
    """
    
    import pandas as pd
    trans_dict=pd.DataFrame([
        
        ['INDEXCF','俄罗斯MICEX指数','俄罗斯MICEX指数','MICEX Index','sina'],
        ['RTS','俄罗斯RTS指数','俄罗斯RTS指数','RTS Index','em'],
        ['CASE','埃及CASE 30指数','埃及CASE30指数','CASE30 Index','sina'],
        ['VNINDEX','越南胡志明','越南胡志明指数','Ho Chi-Ming Index','em'],
        ['HSCEI','国企指数','港股国企指数','HK H-share Index','em'],
        ['HSCCI','红筹指数','港股红筹指数','HK Red-share Index','em'],
        ['CSEALL','斯里兰卡科伦坡','斯里兰卡科伦坡全指','Colombo Index','em'],
        ['UDI','美元指数','美元指数','US Dollar Index','em'],
        ['CRB','路透CRB商品指数','路透CRB商品指数','Reuters CRB Index','em'],
        ['BDI','波罗的海BDI指数','波罗的海BDI指数','Baltic Dry Index','em'],
        ['KSE100','巴基斯坦卡拉奇','巴基斯坦卡拉奇指数','KSE100 Index','em'],
        
        
        ], columns=['code','symbol','name_cn','name_en','source'])

    found=False; symbol=index_code
    try:
        dict_word=trans_dict[trans_dict['code']==index_code]
        found=True
    except:
        #未查到翻译词汇，返回原词
        pass
    
    if dict_word is None:
        found=False    
    elif len(dict_word) == 0:
        found=False
    
    source=''; name=''
    if found:
        symbol=dict_word['symbol'].values[0]
        
        lang=check_language()
        if lang == 'Chinese':
            name=dict_word['name_cn'].values[0]
        else:
            name=dict_word['name_en'].values[0]
            
        source=dict_word['source'].values[0]
            
    return symbol,name,source

if __name__=='__main__': 
    index_code='KSE100'
    index_code='CASE'
    index_code='XYZ'
    
    set_language('Chinese')
    set_language('English')
    other_index_translate(index_code)

#==============================================================================
def get_other_index_em(index_code,start,end):
    """
    功能：获取另类指数历史行情，东方财富
    参数：
    index_code：指数代码
    start,end：开始/结束日期
    """
    symbol,name,source=other_index_translate(index_code)
    if symbol == index_code:
        return None
    
    import akshare as ak
    try:
        dft = ak.index_global_hist_em(symbol=symbol)
    except:
        return None
    
    dft.rename(columns={'日期':'Date','代码':'ticker','名称':'Name','今开':'Open', \
                        '最新价':'Close','最高':'High','最低':'Low','振幅':'Change'}, \
               inplace=True)
    dft['Change']=dft['Change']/100.00
    dft['Adj Close']=dft['Close']
    dft['source']=source
    dft['Volume']=0
    dft['Name']=name
    
    import pandas as pd
    dft['date']=dft['Date'].apply(lambda x: pd.to_datetime(x))
    dft.set_index('date',inplace=True)
    
    startpd=pd.to_datetime(start); endpd=pd.to_datetime(end)
    df=dft[(dft.index >= startpd) & (dft.index <= endpd)]
    
    return df

if __name__=='__main__': 
    index_code='KSE100'
    start='2025-2-1'; end='2025-3-31'
    get_other_index_em(index_code,start,end)
#==============================================================================
if __name__=='__main__': 
    index_code='RTS'
    start='2025-2-1'; end='2025-3-31'
    get_other_index_em(index_code,start,end)

def get_other_index_sina(index_code,start,end):
    """
    功能：获取另类指数历史行情，新浪财经
    参数：
    index_code：指数代码
    start,end：开始/结束日期
    """
    symbol,name,source=other_index_translate(index_code)
    if symbol == index_code:
        return None
    
    import akshare as ak
    try:
        dft = ak.index_global_hist_sina(symbol=symbol)
    except:
        return None
    
    dft.rename(columns={'open':'Open','high':'High','low':'Low','close':'Close', \
                        'volume':'Volume'},inplace=True)
    dft['ticker']=index_code; dft['Name']=name; dft['Date']=dft['date']
    dft['Adj Close']=dft['Close']
    dft['source']=source
    
    import pandas as pd
    dft['date']=dft['Date'].apply(lambda x: pd.to_datetime(x))
    dft.set_index('date',inplace=True)
    
    startpd=pd.to_datetime(start); endpd=pd.to_datetime(end)
    df=dft[(dft.index >= startpd) & (dft.index <= endpd)]
    
    return df

if __name__=='__main__': 
    index_code='CASE'
    start='2025-2-1'; end='2025-3-31'
    get_other_index_sina(index_code,start,end)
#==============================================================================
def get_other_index_ak(index_code,start,end):
    """
    功能：获取另类指数历史行情，新浪财经或东方财富
    参数：
    index_code：指数代码
    start,end：开始/结束日期
    """
    symbol,name,source=other_index_translate(index_code)
    if symbol == index_code:
        return None
    
    if source == 'em':
        df=get_other_index_em(index_code,start,end)
    elif source == 'sina':
        df=get_other_index_sina(index_code,start,end)
    else:
        df=None
        
    return df

if __name__=='__main__': 
    index_code='CASE'
    index_code='KSE100'
    index_code='VNINDEX'
    start='2025-2-1'; end='2025-3-31'
    get_other_index(index_code,start,end)
#==============================================================================
if __name__=='__main__': 
    ticker='AAPL'
    ticker='^TVX'
    ticker='Apple'
    start='2025-4-1'; end='2025-4-30'
    
    get_prices_av(ticker,start,end)
    
def get_prices_av(ticker,start,end):
    """
    功能：从Alpha Vantage获取美股股价历史行情，使用Alpha Vantage
    参数：
    ticker：AV股票代码（假设与雅虎财经的股票代码相同），如不同可通过search_av获得准确代码
    start：起始日期
    end：结束日期
    """
    # 免费注册：wangdehong@bfsu.edu.cn，每日25次。
    api_key='VTRR3TA7L9O2DIX6'  
    
    from alpha_vantage.timeseries import TimeSeries
    ts = TimeSeries(key=api_key, output_format="pandas")
    try:
        dft, _ = ts.get_daily(symbol=ticker, outputsize="full")   
    except:
        pass
        return None
    
    dft.sort_index(ascending=True,inplace=True)
    dft.rename(columns={'1. open':'Open','2. high':'High','3. low':'Low', \
                        '4. close':'Close','5. volume':'Volume'},inplace=True)
    dft['Adj Close']=dft['Close']
    dft['source']='Alpha Vantage'
    dft['ticker']=ticker
    dft['Name']=ticker

    import pandas as pd
    startpd=pd.to_datetime(start); endpd=pd.to_datetime(end)
    df=dft[(dft.index >= startpd) & (dft.index <= endpd)]
    
    return df

    
#==============================================================================
if __name__=='__main__': 
    ticker='AAPL'
    ticker='Apple'
    start='2025-4-1'; end='2025-4-30'
    
    get_prices_av_pdr(ticker,start,end)
    
def get_prices_av_pdr(ticker,start,end):
    """
    功能：从Alpha Vantage获取美股股价历史行情，使用pandas_datareader
    参数：
    ticker：AV股票代码（可能与雅虎财经的股票代码不同），可以通过search_av获得准确代码
    start：起始日期
    end：结束日期
    """
    # 免费注册：wangdehong@bfsu.edu.cn，限每日25次。
    api_key='VTRR3TA7L9O2DIX6' 
    
    import pandas_datareader.data as pdr
    try:
        dft = pdr.DataReader(ticker, "av-daily", api_key=api_key,start=start,end=end)
        dft['ticker']=ticker
        dft['Name']=ticker
    except: # 拯救一次，查找字符串匹配的股票代码
        firstcode,firstname,_=search_av(ticker,api_key)
        if firstcode is None:
            pass
            return None
        print(f"  Notice: matching keyword {ticker} to stock code {firstcode}({firstname})")
        try:
            dft = pdr.DataReader(firstcode, "av-daily", api_key=api_key,start=start,end=end)
            dft['ticker']=firstcode
            dft['Name']=firstname
        except:
            pass
            return None
    
    if dft is None:
        pass
        return None
    if len(dft) == 0:
        pass
        return None
    
    dft.rename(columns={'open':'Open','high':'High','low':'Low','close':'Close', \
                        'volume':'Volume'},inplace=True)
    dft['Adj Close']=dft['Close']
    dft['source']='Alpha Vantage'
    
    import pandas as pd
    dft['Date']=dft['date']=dft.index
    dft['date']=dft['date'].apply(lambda x: pd.to_datetime(x))
    dft.set_index('date',inplace=True)
    
    #startpd=pd.to_datetime(start); endpd=pd.to_datetime(end)
    #df=dft[(dft.index >= startpd) & (dft.index <= endpd)]
    df=dft
    
    return df
    
    
#==============================================================================
if __name__=='__main__': 
    api_key='VTRR3TA7L9O2DIX6'
    keyword='AAPL'
    keyword='Apple'
    keyword='^TYX'
    
    search_av("microsoft")
    search_av("Apple")

def search_av(keyword,api_key='VTRR3TA7L9O2DIX6'):
    """
    过程：给定上市公司关键名称或不带后缀的股票代码，找出Alpha Vantage的股票代码。
    """
    DEBUG=False
    
    import requests
    url = f"https://www.alphavantage.co/query?function=SYMBOL_SEARCH&keywords={keyword}&apikey={api_key}"
    response = requests.get(url)
    if response.status_code != 200:
        pass
        return None,None,None
    
    data = response.json()
    if "bestMatches" in data:
        try:
            firstcode=data["bestMatches"][0]['1. symbol']
            firstname=data["bestMatches"][0]['2. name']
        except:
            if DEBUG:
                print(f"  #Warning(search_av): no contents found for {keyword} in Alpha Vantage")
            #未找到可匹配的股票代码
            return None,None,None
            
    else:
        if DEBUG:
            if "Information" in data:
                print(f"  #Warning(search_av): exceeded limit of requests per day in Alpha Vantage")
            else:
                print(f"  #Warning(search_av): keyword {keyword} not found in Alpha Vantage")
        #未找到可匹配的股票代码
        return None,None,None
    
    return firstcode,firstname,data

#==============================================================================
if __name__=='__main__': 
    ticker='AAPL'
    ticker='^TVX'
    start='2025-4-1'; end='2025-4-30'
    
    get_price_tiingo(ticker,start,end)
    
def get_price_tiingo(ticker,start,end):
    """
    功能：获取美股历史行情信息，基于TIINGO
    """
    DEBUG=False
    
    # 每日限1000次调用，基于wdehong2000@163.com
    api_token='0892bdb0533f8114535f354db596e6c244f5618d'
    
    from tiingo import TiingoClient
    # 通过配置字典
    config = {
        'api_key': api_token,  # 替换为实际密钥
        'session': True  # 启用HTTP会话复用，提升性能
    }
    client = TiingoClient(config)    


    # 获取历史行情（默认返回DataFrame）
    try:
        dft = client.get_dataframe(
                                    ticker,
                                    startDate=start,
                                    endDate=end,   
                                    frequency='daily'
                                   )
    except Exception as e:
        if DEBUG:
            print(f"  #Error(get_price_tiingo): {e}")    
            print(f"  #Error(get_price_tiingo): {ticker} not found or exceeded max requests per day")
        return None
        
    # 去掉时区
    dft.index = dft.index.tz_localize(None)
    
    # 整理数据项
    dft.rename(columns={'open':'Open','high':'High','low':'Low','close':'Close', \
                        'volume':'Volume'},inplace=True)
    
    dft.rename(columns={'adjOpen':'Adj Open','adjHigh':'Adj High','adjLow':'Adj Low', \
                        'adjClose':'Adj Close', \
                        'adjVolume':'Adj Volume'},inplace=True)
        
    dft['source']='Tiingo'
    dft['ticker']=ticker; dft['name']=ticker
        
    return dft
        
        
#==============================================================================
#==============================================================================
#==============================================================================


