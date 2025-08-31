# -*- coding: utf-8 -*-
"""
版权：王德宏，北京外国语大学国际商学院
功能：
1、获取证券价格，多种方法
2、首先获取单一证券的价格，其后证券列表的价格
3、支持股票、基金、债券、申万行业指数
版本：0.1，2024-4-3，经过多方测试
"""

#==============================================================================
#关闭所有警告
import warnings; warnings.filterwarnings('ignore')
from siat.common import *
from siat.translate import *
from siat.security_prices import *
from siat.other_indexes import *
#==============================================================================
import pandas as pd
#==============================================================================
SUFFIX_LIST_CN=['SS','SZ','BJ','SW','SH']
SUFFIX_LIST_HK=['HK']
#==============================================================================

#==============================================================================
#==============================================================================
if __name__=='__main__':
    ticker='AAPL' #股票
    ticker='600519.SS' 
    ticker='00700.HK'
    ticker='OPN.PL'
    
    ticker='000001.SS' #指数
    ticker='000300.SS'
    
    ticker='sh018003' #债券
    ticker='sz149808'
    ticker='sz159998' #基金
    
    ticker='801010.SW' #申万
    ticker='851242.SW' #申万
    ticker='807110.SW'
    
    ticker='AAPL'
    
    ticker='GC=F'
    
    ticker="006257"
    ticker_type='auto'
    
    fromdate='2024-5-1'; todate='2024-5-20'
    
    ticker_type='auto'
    ticker_type='bond'
    
    ticker='000418'
    ticker='180202.SZ'
    ticker_type='fund'
    
    source='auto'
    #source='yahoo'
    
    adjust=''
    adjust='qfq'
    
    fill=False
    fill=True
    
    # 新测试组
    ticker="XAUUSD"
    ticker="^NSEI"
    fromdate='2024-5-1'; todate='2024-5-20'
    
    ticker="BMW.DE"
    fromdate='2022-6-1'; todate='2025-6-15'
    
    ticker_type='auto';source='auto'
    adjust='';fill=False
    
    
    price,found=get_price_1ticker(ticker=ticker,fromdate=fromdate,todate=todate, \
                                  ticker_type=ticker_type)
    
def get_price_1ticker(ticker,fromdate,todate, \
                      ticker_type='auto',source='auto', \
                      adjust='',fill=False):
    """
    功能：抓取一只证券的价格序列，不处理列表，不处理投资组合
    类型优先顺序：ticker_type，auto-自动，stock-指定股票，fund-指定基金，bond-指定债券
    数据源优先顺序：1-source，2-ticker属地，3-ticker_type
    adjust：""-未复权，qfq-前复权，hfq-后复权，qfq-factor：前复权因子和调整，hfq-factor: 后复权因子和调整
    返回值：
    df: None-未找到ticker，空df-找到ticker但规定时间段内无数据
    found: 字符串，Found-找到且有数据，Empty-找到但规定时间段内无数据，None-未找到ticker。
    简化使用者判断
    fill：为现有数据开始结束日期之间的工作日填充=True
    """ 
    #设置雅虎yfinance开关
    YF=False
    #设置雅虎pandas_datareader开关，避免在此花费时间
    PDR_yahoo=False
    
    #返回值初始状态，确保各种情况下都有返回值
    df=None
    found='None'
    
    #只处理字符串
    if not isinstance(ticker,str):
        print("  #Warning(get_price_1ticker):",ticker,"is not a single security code")
        return df,found

    #检查日期期间合理性
    valid_period,fromdatepd,todatepd=check_period(fromdate,todate)
    if not valid_period:
        pass
        #print("  #Warning(get_price_1ticker): invalid date period from",fromdate,"to",todate)
        return df,found
        
    #检查复权选项合理性：adj_only特别指最高最低价开盘收盘价全为复权价
    ak_fq_list=['','qfq','hfq','qfq-factor','hfq-factor','adj_only']
    if adjust not in ak_fq_list:
        adjust='qfq'
    
    #变换ticker为内部格式（yahoo格式）
    ticker1=ticker1_cvt2yahoo(ticker)
    _,prefix,suffix=split_prefix_suffix(ticker1)
    
    #预处理ticker_type
    ticker_type=ticker_type_preprocess_1str(ticker,ticker_type)
    
    #数据源情形1：akshare
    if source in ['auto','sina','em']:
        #中国的证券
        if suffix in SUFFIX_LIST_CN:
            #含处理证券类型优先级
            dft=get_price_ak_cn(ticker1,fromdate,todate,adjust=adjust,ticker_type=ticker_type)
            found=df_have_data(dft)
            
        #香港的证券
        if suffix in SUFFIX_LIST_HK and found not in ['Found','Empty']:
            dft=get_price_ak_hk(ticker1,fromdate,todate,adjust=adjust)
            found=df_have_data(dft)
            
        #是否美股
        if found not in ['Found','Empty']:
            adjust='qfq' if adjust != '' else ''
            dft=get_price_ak_us(ticker1,fromdate,todate,adjust=adjust)
            found=df_have_data(dft)
    """
    if ticker_type in ['fund']:
        #变换代码格式
        ticker2=tickers_cvt2ak(ticker1)
        try:
            #优先抓取开放式基金单位净值
            dft =get_price_oef_china(ticker2,fromdate,todate)
            dft['Date']=dft.index
        except: 
            dft=None
        found=df_have_data(dft)

    if ticker_type in ['bond']:
        #变换代码格式
        ticker2=tickers_cvt2ak(ticker1)
        try:
            #最后抓取交易所债券行情
            dft = exchange_bond_price(ticker2,fromdate,todate,graph=False,data_crop=False)
            dft['Date']=dft.index
        except: 
            #print("  #Error(get_price_ak_cn): failed to find prices for",ticker)
            return None
        found=df_have_data(dft)
    """            
    #数据源情形2：stooq
    if source in ['auto','stooq'] and found not in ['Found','Empty']:
        dft=get_price_stooq(ticker1,fromdate,todate)
        found=df_have_data(dft)
    
    #访问雅虎财经
    if source in ['auto','yahoo'] and found not in ['Found','Empty']:
        dft=None
        if test_yahoo_finance():
            #数据源情形3a：yahoo, yahooquery, 需要访问yahoo
            dft=get_price_yq(ticker1,fromdate,todate)
            found=df_have_data(dft) 
            
            #数据源情形3b：yahoo, yfinance, 需要访问yahoo，直接为复权价
            if found not in ['Found','Empty']:
                if YF:
                    dft=get_price_yf(ticker1,fromdate,todate)
                    found=df_have_data(dft) 
        
            #数据源情形4：yahoo, pandas_datareader，需要访问yahoo，似乎不工作了！
            if found not in ['Found','Empty']:
                if PDR_yahoo:
                    dft=get_prices_yahoo(ticker1,fromdate,todate)
                    found=df_have_data(dft) 
        else:
            if source in ['yahoo']:
                print("  #Warning(get_price_1ticker): sorry, yahoo is currently inaccessible")
            
    #数据源情形5：FRED, 仅用于几个常用指数，备用
    if source in ['auto'] and found not in ['Found','Empty']:
        dft=get_index_fred(ticker1,fromdate,todate)
        found=df_have_data(dft)         
            
    #数据源情形6：仅用于几个另类非常用指数，例如胡志明指数/卡拉奇指数/埃及指数等，新浪/东方财富
    if source in ['auto','sina','em'] and found not in ['Found','Empty']:
        dft=get_other_index_ak(ticker1,fromdate,todate)
        found=df_have_data(dft)   
        
    #数据源情形7：Tiingo，每日限1000次调用
    if source in ['auto','ti'] and found not in ['Found','Empty']:
        dft=get_price_tiingo(ticker1,fromdate,todate)
        found=df_have_data(dft)  
        
    #数据源情形8：alpha_vantage，每日限25次调用
    if source in ['auto','av'] and found not in ['Found','Empty']:
        dft=get_prices_av(ticker1,fromdate,todate)
        found=df_have_data(dft)   
        
    #数据源情形9：Alpha Vantage, pandas_datareader, 可进行模糊匹配，但匹配准确度不确定！
    if source in ['auto','av'] and found not in ['Found','Empty']:
        dft=get_prices_av_pdr(ticker1,fromdate,todate)
        found=df_have_data(dft)   
    
    """
    IEX：获得投资交易信息，需要API_KEY
    Econdb：提供超过90家官方统计机构提供的经济数据，免费
    Enigma：交易数据，需要API
    Quandl：股价和基金交易数据，需要API_KEY
    FRED：来自FRED的金融研究数据，编码特殊，需要转换
    Fama/French：来自Fama/French数据实验室的数据
    World Bank：世行数据
    OECD：经合组织数据
    Eurostat：欧洲统计局数据
    TSP Fund Data：TSP(Thrift Savings Plan) 基金数据
    Nasdaq Trader Symbol Definitions：Nasdaq 股票代码定义文档 (包含公司名，上市状态等一些数据)
    MOEX Data：莫斯科交易所数据
    Bank of Canada：加拿大银行数据
    """
        
    #整理字段
    if found in ['Found','Empty']:
        dft1_cols=['Open','High','Low','Close','Volume','Adj Close','source','ticker']
        dft1=dft[dft1_cols]
        
        dft1['name']=ticker_name(ticker1,ticker_type=ticker_type)
        dft1['Amount']=dft1.apply(lambda x: x['Close'] * x['Volume'],axis=1)
    else:
        dft1=dft
        
    if found == 'None':
        print("  Sorry, tried all means,",ticker,'info not found or inaccessible')
    if found == 'Empty':
        print("  Pity, zero record available for",ticker,'from',fromdate,'to',todate)
    
    if found in ['Found'] and fill:
        #需要产生连续工作日日期，以便对缺失值填充
        dft1=df_fill_extend(dft1,colname='Close',extend_business_date=True)
        dft1['Volume']=dft1.apply(lambda x: 0 if x['filled']==True else x['Volume'],axis=1)
        dft1['Amount']=dft1.apply(lambda x: 0 if x['filled']==True else x['Amount'],axis=1)
    
    return dft1,found

#==============================================================================
if __name__=='__main__':
    ticker=["430047.BJ","600519.SS","000858.SZ"] #全股票
    ticker_type='auto'
    ticker_type=['auto','stock']
    
    ticker=["sz169107","sh510050","sh010504","000858.SZ"] #LOF基金,ETF基金,国债，股票
    ticker_type='bond'
    
    ticker=['801002.SW',"600519.SS","sh510050","sh010504"] #申万指数，股票,ETF基金,国债
    ticker_type='bond'
    
    ticker=["180801.SZ","180101.SZ"]
    fromdate="2024-3-1"
    todate="2024-4-1"
    ticker_type='fund'
    
    adjust=''
    adjust=['','qfq']
    
    source='auto'
    fill=True
    
    #测试复权价
    ticker=['300750.SZ','300014.SZ']
    fromdate="2023-4-20"
    todate="2023-4-30"
    ticker_type='fund'
    
    adjust='qfq'
    source='auto'
    fill=False
    
    
    prices,found=get_price_mticker(ticker,fromdate,todate,adjust,source,ticker_type,fill)

def get_price_mticker(ticker,fromdate,todate, \
                      adjust='',source='auto',ticker_type='auto',fill=False):
    """
    功能：多个证券(股票，指数，基金，债券)，不含投资组合(否则容易引起递归调用)
    ticker_type：若为'auto'则基金优先于债券(代码重合时)，亦可为列表分别指定优先抓取类型。
    'stock', 'fund', 'bond'，不足部分自动补充为最后项
    其中，'auto'/'stock'/'fund'优先抓取指数、股票和基金；'bond'优先抓取债券；
    
    注意：adjust,source,ticker_type既可以指定单个值，也可以使用列表分别指定各个证券
    不足部分由最后1个值补全
    """
    DEBUG=False
    
    df=None; found='None'
    
    #将证券代码列表化
    if isinstance(ticker,list): ticker_list=ticker
    else: ticker_list=[ticker]
    ticker_num=len(ticker_list)
    
    #将adjust列表化：不足部分由列表中最后1个值补全
    if isinstance(adjust,list): adjust_list=adjust
    else: adjust_list=[adjust]
    adjust_len=len(adjust_list)
    
    if ticker_num > adjust_len: 
        adjust1=adjust_list[-1] #延续最后项
        adjust_list=adjust_list + [adjust1]*(ticker_num - adjust_len)
    
    #将source列表化
    if isinstance(source,list): source_list=source
    else: source_list=[source]
    source_len=len(source_list)
    
    if ticker_num > source_len: 
        source1=source_list[-1] #延续最后项
        source_list=source_list + [source1]*(ticker_num - source_len)   
    
    #预处理ticker_type
    ticker_type_list=ticker_type_preprocess_mstr(ticker,ticker_type)

    #单个普通证券的特殊处理，不产生MultiIndex，避免后续程序识别出错
    if ticker_num == 1:
        df,found=get_price_1ticker(ticker=ticker_list[0],fromdate=fromdate,todate=todate, \
                             adjust=adjust_list[0],source=source_list[0], \
                             ticker_type=ticker_type_list[0],fill=fill)

    #多个普通证券
    if ticker_num > 1:
        for t in ticker_list:
            pos=ticker_list.index(t)
            at=adjust_list[pos]
            st=source_list[pos]
            tt=ticker_type_list[pos]
            
            #普通单个证券
            dft,found=get_price_1ticker(t,fromdate,todate,adjust=at,source=st, \
                                        ticker_type=tt,fill=fill)
            if found=='Found':            
                columns=create_tuple_for_columns(dft,t)
                dft.columns=pd.MultiIndex.from_tuples(columns)
            else: continue
            
            if df is None: df=dft
            else: #合并
                df=pd.merge(df,dft,how='outer',left_index=True,right_index=True)
        
    found=df_have_data(df)
    
    return df,found

#==============================================================================
if __name__=='__main__':
    #股票组合
    ticker={'Market':('China','000001.SS','白酒组合'),'600519.SS':0.4,'000858.SZ':0.6}
    ticker_type='auto'
    
    #股债/股基组合
    ticker={'Market':('China','000001.SS','股债组合'),'600519.SS':0.4,'sh010504':0.6}
    ticker_type='bond' #股债组合
    ticker_type='auto' #股基组合

    #股债基组合：分别指定每个成份股的品种(股票，债券，基金)，份额自动换算
    ticker={'Market':('China','000001.SS','股债基组合'),'600519.SS':50,'sh018003':150,'sh010504':300}
    ticker_type=['stock','bond','fund']
    
    fromdate='2024-1-1'
    todate='2024-4-1'
    adjust=''
    source='auto'
    fill=True
    
    pf,found=get_price_1portfolio(ticker=ticker,fromdate=fromdate,todate=todate, \
                            adjust=adjust,source=source,ticker_type=ticker_type, \
                            fill=fill)

def get_price_1portfolio(ticker,fromdate,todate, \
                         adjust='',source='auto',ticker_type='bond',fill=True):  
    """
    功能：抓取1个投资组合的信息，不能处理单个证券或证券列表
    注意：
    投资组合采用字典格式，但各个成份股份额之和不一定为1
    fill默认为True，否则由于成份股股价为nan时投资组合价格会受影响
    """
    
    #返回值初始状态，确保各种情况下都有返回值
    df=None
    found='None'
    
    #只处理投资组合
    if not isinstance(ticker,dict):
        print("  #Warning(get_price_1portfolio): not in dict format for",ticker)
        return df,found

    #检查日期期间合理性
    valid_period,fromdatepd,todatepd=check_period(fromdate,todate)
    if not valid_period:
        print("  #Warning(v): invalid date period from",fromdate,"to",todate)
        return df,found
    
    #拆分投资组合为成份股列表和份额列表
    _,_,tickerlist,sharelist,ticker_type=decompose_portfolio(ticker) 
    
    #处理份额列表，确保其和为1
    share_sum=sum(sharelist)
    sharelist1=[x / share_sum for x in sharelist]

    #预处理ticker_type，是否还需要？
    ticker_type=ticker_type_preprocess_1portfolio(ticker,ticker_type)
    
    #抓取各个成份股的价格信息
    prices,found=get_price_mticker(ticker=tickerlist, \
                                   fromdate=fromdate,todate=todate, \
                                   adjust=adjust,source=source, \
                                   ticker_type=ticker_type,fill=fill)
        
    if found not in ['Found','Empty']:
        return df,found
    
    #加权平均，矩阵乘法
    df=pd.DataFrame() #为None时无法对其赋值
    collist=['Open','High','Low','Close','Adj Close','Amount']
    for c in collist:
        dfc=prices[c]
        df[c]=dfc.dot(sharelist1)
        
    df['Volume']=df.apply(lambda x: (x['Amount'] / x['Close']),axis=1)
    df['ticker']=portfolio_name(ticker)
    df['name']=df['ticker']
    df['source']=source
    df['component']=str(list(prices['name'].tail(1).values[0]))
    df['portion']=str(sharelist1)

    return df,found

#==============================================================================
if __name__=='__main__':
    #股票组合
    pf1={'Market':('China','000001.SS','白酒组合'),'600519.SS':0.4,'000858.SZ':0.6}
    pf2={'Market':('China','000001.SS','股债组合'),'600519.SS':0.4,'sh010504':0.6}
    pf3={'Market':('China','000001.SS','股债基组合'),'600519.SS':50,'sh018003':150,'sh010504':300}
    
    pflist=[pf1,pf2]
    pflist=[pf1,pf2,pf3]
    
    ticker_type='bond'
    ticker_type=['stock','bond','bond']
    
    fromdate='2024-1-1'
    todate='2024-4-1'
    adjust=''
    source='auto'
    fill=True
    
    pfs,found=get_price_mportfolio(ticker=pflist,fromdate=fromdate,todate=todate, \
                             adjust=adjust,source=source, \
                             ticker_type=ticker_type,fill=fill)


def get_price_mportfolio(ticker,fromdate,todate, \
                      adjust='',source='auto',ticker_type='bond',fill=True):
    """
    功能：多个投资组合(股票，指数，基金，债券)，不含非投资组合(否则容易引起递归调用)
    ticker_type：可为单个、列表或列表中含有列表
    
    注意：adjust,source,ticker_type既可以指定单个值，也可以使用列表分别指定各个投资组合
    不足部分由最后1个值补全
    """
    DEBUG=False
    
    df=None; found='None'
    
    #将投资组合列表化
    if isinstance(ticker,list): ticker_list=ticker
    elif isinstance(ticker,dict): ticker_list=[ticker]
    else: return df,found
    ticker_num=len(ticker_list)
    
    #将adjust列表化：不足部分由列表中最后1个值补全
    if isinstance(adjust,list): adjust_list=adjust
    else: adjust_list=[adjust]
    adjust_len=len(adjust_list)
    
    if ticker_num > adjust_len: 
        adjust1=adjust_list[-1] #延续最后项
        adjust_list=adjust_list + [adjust1]*(ticker_num - adjust_len)
    
    #将source列表化和补全
    if isinstance(source,list): source_list=source
    else: source_list=[source]
    source_len=len(source_list)
    
    if ticker_num > source_len: 
        source1=source_list[-1] #延续最后项
        source_list=source_list + [source1]*(ticker_num - source_len)   
        
    #预处理ticker_type
    ticker_type_list=ticker_type_preprocess_mticker_mixed(ticker,ticker_type)

    #单个投资组合的特殊处理，不产生MultiIndex，避免后续程序识别出错
    if ticker_num == 1:
        df,found=get_price_1portfolio(ticker=ticker_list[0],fromdate=fromdate,todate=todate, \
                                adjust=adjust_list[0],source=source_list[0], \
                                ticker_type=ticker_type_list[0],fill=fill)

    #多个投资组合
    if ticker_num > 1:
        for t in ticker_list:
            pos=ticker_list.index(t)
            at=adjust_list[pos]
            st=source_list[pos]
            tt=ticker_type_list[pos]
            
            #单个投资组合
            dft,found=get_price_1portfolio(ticker=t,fromdate=fromdate,todate=todate, \
                                           adjust=at,source=st,ticker_type=tt,fill=fill)
            if found=='Found': 
                tn=ticker_name(t)
                columns=create_tuple_for_columns(dft,tn)
                dft.columns=pd.MultiIndex.from_tuples(columns)
            else: continue
            
            if df is None: df=dft
            else: #合并
                df=pd.merge(df,dft,how='outer',left_index=True,right_index=True)
        
    found=df_have_data(df)
    
    return df,found

#==============================================================================
if __name__=='__main__':
    #股票/债券/基金+投资组合
    pf={'Market':('China','000001.SS','白酒组合'),'600519.SS':0.4,'000858.SZ':0.6}
    ticker=[pf,'000002.SZ','002594.SZ','sh018003','sh010504']
    ticker_type=[['auto','stock'],'auto','auto','bond'] #不足部分自动延续最后一个类型
    
    ticker=["180801.SZ","180101.SZ"]
    ticker_type='fund'
    
    fromdate='2024-1-1'
    todate='2024-4-1'
    adjust=''
    source='auto'
    fill=True
    
    mix,found=get_price_mticker_mixed(ticker=ticker,fromdate=fromdate,todate=todate,ticker_type=ticker_type)
    
def get_price_mticker_mixed(ticker,fromdate,todate, \
                         adjust='',source='auto',ticker_type='auto',fill=False):  
    """
    功能：混合抓取证券列表的价格信息，列表中的元素可为多个股票、基金、债券或投资组合
    注意：
    可为列表中的各个元素分别指定证券类型ticker_type
    若元素为投资组合可为其指定类型列表(即列表中的列表)
    某个元素为债券时证券类型需要选择'bond'(即优先寻找债券)，余者指定为'auto'即可
    
    """
    
    #返回值初始状态，确保各种情况下都有返回值
    df=None; found='None'
    
    #将ticker列表化
    if isinstance(ticker,list): ticker_list=ticker
    else: ticker_list=[ticker]
    ticker_num=len(ticker_list)
    
    #将adjust列表化和补全：不足部分由列表中最后1个值补全
    if isinstance(adjust,list): adjust_list=adjust
    else: adjust_list=[adjust]
    adjust_len=len(adjust_list)
    
    if ticker_num > adjust_len: 
        adjust1=adjust_list[-1] #延续最后项
        adjust_list=adjust_list + [adjust1]*(ticker_num - adjust_len)
    
    #将source列表化和补全
    if isinstance(source,list): source_list=source
    else: source_list=[source]
    source_len=len(source_list)
    
    if ticker_num > source_len: 
        source1=source_list[-1] #延续最后项
        source_list=source_list + [source1]*(ticker_num - source_len)   
        
    #预处理ticker_type
    ticker_type_list=ticker_type_preprocess_mticker_mixed(ticker,ticker_type)

    #若列表中仅有1个元素，不需要产生MultiIndex
    if ticker_num == 1:
        #单个证券
        if isinstance(ticker_list[0],str):
            df,found=get_price_1ticker(ticker=ticker_list[0],fromdate=fromdate,todate=todate, \
                                 ticker_type=ticker_type_list[0],source=source_list[0], \
                                 adjust=adjust_list[0],fill=fill)
        
        #单个投资组合
        if isinstance(ticker_list[0],dict):
            df,found=get_price_1portfolio(ticker=ticker_list[0],fromdate=fromdate,todate=todate, \
                                 ticker_type=ticker_type_list[0],source=source_list[0], \
                                 adjust=adjust_list[0],fill=fill)
                
        return df,found
        
    #若ticker是列表************************************************************
    if ticker_num > 1:
        for t in ticker_list:
            pos=ticker_list.index(t)
            at=adjust_list[pos]
            st=source_list[pos]
            tt=ticker_type_list[pos]
            
            #单个普通证券
            if isinstance(t,str):
                dft,found=get_price_1ticker(ticker=t,fromdate=fromdate,todate=todate, \
                                           adjust=at,source=st,ticker_type=tt,fill=fill)
                tn=t
                
            #单个投资组合
            if isinstance(t,dict):
                dft,found=get_price_1portfolio(ticker=t,fromdate=fromdate,todate=todate, \
                                           adjust=at,source=st,ticker_type=tt,fill=fill)
                tn=ticker_name(t)
                
            if found=='Found': 
                columns=create_tuple_for_columns(dft,tn)
                dft.columns=pd.MultiIndex.from_tuples(columns)
            else: continue
            
            if df is None: df=dft
            else: #合并
                df=pd.merge(df,dft,how='outer',left_index=True,right_index=True)
        
    found=df_have_data(df)
    
    return df,found

#==============================================================================
if __name__=='__main__':
    #股票/债券/基金+投资组合
    ticker={'Market':('China','000001.SS','白酒组合'),'600519.SS':0.4,'000858.SZ':0.6}
    ticker='sh018003'
    ticker_type='bond'
    
    ticker='180202.SZ'
    ticker_type='fund'
    
    ticker='851242.SW'
    ticker_type='auto'    
    
    fromdate='2021-1-1'
    todate='2024-5-30'
    
    ticker='BMW.DE'
    fromdate='2024-6-2'
    todate='2025-6-15'
    
    adjust=''
    source='auto'
    fill=True
    
    mixed,found=get_price_1ticker_mixed(ticker=ticker,fromdate=fromdate,todate=todate, \
                             ticker_type=ticker_type)
    
def get_price_1ticker_mixed(ticker,fromdate,todate, \
                         adjust='',source='auto',ticker_type='auto',fill=False):  
    """
    功能：混合抓取证券列表的价格信息，列表中的元素需为单个股票、基金、债券或投资组合
    方便仅需一只证券的调用
    """
    
    #返回值初始状态，确保各种情况下都有返回值
    df=None; found='None'
    
    #若ticker为列表则取其第1个元素
    if isinstance(ticker,list): ticker=ticker[0]
    
    #若adjust为列表则取其第1个元素
    if isinstance(adjust,list): adjust=adjust[0]
    
    #若source为列表则取其第1个元素
    if isinstance(source,list): source=source[0]
        
    #若ticker_type为列表则取其第1个元素
    if isinstance(ticker_type,list): ticker_type=ticker_type[0]

    #单个证券
    if isinstance(ticker,str):
        df,found=get_price_1ticker(ticker=ticker,fromdate=fromdate,todate=todate, \
                             ticker_type=ticker_type,source=source, \
                             adjust=adjust,fill=fill)
    
    #单个投资组合
    if isinstance(ticker,dict):
        df,found=get_price_1portfolio(ticker=ticker,fromdate=fromdate,todate=todate, \
                             ticker_type=ticker_type,source=source, \
                             adjust=adjust,fill=fill)
        #对空缺值填充，以免影响后续计算
        df=df.fillna(method='ffill')
        df=df.fillna(method='bfill')
            
    return df,found
    
    
#==============================================================================
#==============================================================================
#==============================================================================
