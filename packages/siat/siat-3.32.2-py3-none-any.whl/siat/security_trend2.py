# -*- coding: utf-8 -*-
"""
本模块功能：证券指标趋势分析，部分支持投资组合
所属工具包：证券投资分析工具SIAT 
SIAT：Security Investment Analysis Tool
创建日期：2024年3月24日
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
from siat.stock import *
from siat.security_prices import *
from siat.security_price2 import *
from siat.capm_beta2 import *
from siat.risk_adjusted_return2 import *
from siat.valuation import *
from siat.grafix import *

import pandas as pd
import datetime as dt; todaydt=str(dt.date.today())
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
    ticker_type='auto'
    
    #测试组4
    ticker=["GCZ25.CMX","GCZ24.CMX"]
    indicator='Close'
    start="2020-1-1"
    end="2020-6-30"
    ticker_type='auto'
    
    
    #测试组5
    ticker=["180801.SZ","180101.SZ"]
    indicator='Close'
    start="2024-1-1"
    end="2024-5-30"   
    ticker_type='fund'
    
    #测试组6
    ticker="851242.SW"
    ticker='807110.SW'
    indicator='Close'; adjust=''
    start="2024-1-1"
    end="2024-9-30"
    ticker_type='auto'  
    
    #测试组6
    ticker='301161.SZ'
    indicator='sharpe'; adjust=''
    start="2024-1-1"
    end="2024-9-30"
    ticker_type='auto' 
    
    
    attention_value=''; average_value=False
    kline=False; kline_demo=False; mav=[5,10,20]
    dividend=False; split=False
    ret_type='Annual Adj Ret%'; RF=0; regression_period=365; market_index="auto"
    sortby='tpw_mean'; trailing=7; trend_threshhold=0.05
    band_area=''
    graph=True; twinx=False; loc1='best'; loc2='best'
    datatag=False; power=0
    smooth=True; date_range=False; date_freq=False
    preprocess='none'; scaling_option='change%'
    annotate=False; annotate_value=False
    mark_top=True; mark_bottom=True; mark_end=True
    printout=True; source='auto'
    ticker_type='auto'
    facecolor='papayawhip'  
    
    dividend=True
    
    df=security_trend(ticker,indicator,start,end,ticker_type=ticker_type)
    
    
def security_trend(ticker,indicator='Close',adjust='', \
                   start='default',end='default', \
                   #纵轴水平线
                   attention_value='',attention_value_area='', \

                   average_value=False, \
                   #横轴垂直线
                   attention_point='',attention_point_area='', \
                       
                   kline=False,kline_demo=False,mav=[5,20], \
                       
                   dividend=False,split=False, \
                   
                   #计算RAR和贝塔系数的基础参数    
                   ret_type='Annual Adj Ret%',RF=0,regression_period=365,market_index="auto", \
                   sortby='tpw_mean',trailing=7,trend_threshhold=0.05, \
                   
                   #绘制河流图的上下边界，由变量指定    
                   band_area='', \
                   
                       
                   graph=True,twinx=False,loc1='best',loc2='best', \
                   datatag=False,power=0, \
                   smooth=True,date_range=False,date_freq=False, \
                   
                   #数据预处理    
                   preprocess='none',scaling_option='change%', \
                       
                   annotate=False,annotate_value=False, \
                   mark_top=False,mark_bottom=False, \
                       mark_high=False,mark_low=False, \
                   mark_start=False,mark_end=False, \
                       
                   printout=False,source='auto', \
                   ticker_type='auto', \
                   facecolor='papayawhip'):

    """
    ===========================================================================
    功能：组合指令，分析证券指标走势，支持多个证券、多个指标和多种绘图方式。
    主要参数：
    ticker：证券代码，支持多个经济体的证券，包括股票、基金、部分欧美衍生品。
    股票：单一股票，股票列表，支持全球主要证券市场的股票。
    债券：因数据来源关系，本指令暂不支持债券，计划首先支持最活跃的沪深可转债。
    基金：因数据来源关系，仅支持下列市场的部分基金：
    沪深交易所(ETF/LOF/REIT基金)，美市(ETF/REIT/共同基金)，日韩欧洲(部分ETF/REIT基金)。
    利率产品：因数据来源关系，仅支持欧美市场的部分利率产品。
    衍生品：因数据来源关系，仅支持欧美市场的部分商品、金融期货和期权产品（如股票期权）。
    投资组合：使用字典表示法，成分股仅支持全球交易所上市的主要股票（限同币种）。
    投资组合仅支持RAR指标和CAPM贝塔系数，其他指标暂不支持。
    
    indicator：支持证券价格、收益率、风险指标、估值指标、RAR指标和CAPM贝塔系数。
    证券价格：支持开盘价、收盘价、最高最低价。
    收益率：支持基本的日收益率、滚动收益率和扩展收益率。滚动收益率支持周、月、季度和年。
    风险指标：支持滚动收益率和扩展收益率的标准差（波动风险）和下偏标准差（损失风险）。
    RAR指标：支持夏普比率、詹森阿尔法、索替诺比率和特雷诺比率。
    估值指标：支持市盈率、市净率和市值。仅支持中国内地、中国香港、美股和波兰上市的股票。
    市值指标不支持市场指数。
    
    start：指定分析的开始日期或期间。日期格式：YYYY-mm-dd
    作为期间时，支持最近的1个月、1个季度、半年、1年、2年、3年、5年、8年、10年或今年以来。
    省略时默认为最近的1个月。
    end：指定分析的结束日期。日期格式：YYYY-mm-dd。省略时默认为今日。
    
    attention_value：绘图时绘制一条水平线，用以强调一个阈值。默认不绘制。
    average_value：开关打开时，绘图时绘制一条均值线，仅适用于绘制单条曲线。默认关闭。
    
    attention_point：绘制横轴竖线，可为单个横轴点或列表，默认不绘制
    attention_point_area：为两个横轴点的列表，其间区域着色，默认不绘制。
    可与attention_point配合使用。
    
    kline：开关打开时，绘制一条K线图，仅适用于单只股票。默认关闭。
    kline_demo参数：与kline开关同时打开时，绘制一条K线图原理演示图，仅适用于单只股票。
    mav参数：仅当kline开关打开时有效，用于指定K线图中单条或多条移动平均线的天数。
    
    stock_dividend和stock_split：显示一只股票的分红和分拆历史，支持全球主要市场的股票。
    注意：本参数需要特殊访问获取数据。
    
    ret_type、RF、regression_period和market_index：仅用于计算RAR指标和CAPM贝塔系数。
    ret_type：指定计算RAR的收益率类型，支持滚动和扩展收益率，不同种类的计算结果之间不可比。
    RF：指定年化无风险利率，非百分比数值。
    regression_period：指定CAPM回归时的日期期间跨度，为日历日（自然日），默认一年。
    market_index：用于计算CAPM回归贝塔系数时的市场收益率。
    系统能够自动识别全球主要证券市场的指数，其他证券市场可由人工指定具体的市场指数代码。
    
    graph：指定是否将分析结果绘制曲线，默认绘制。
    twinx：指定绘图时是否使用双轴绘图法，仅用于两条曲线且其数量级差异较大时。
    loc1和loc2：用于指定绘图时图例的位置，包括左右上角（下角、中间）、上下中间或图中央。
    loc1用于指定非双轴图或双轴图中第1条曲线图例的位置，loc2用于指定双轴图中第2条曲线的位置。
    datatag：用于指定绘图时是否绘制数据标签，仅当数据稀疏时适用，默认关闭。
    power：用于指定绘图时是否使用多项式绘制趋势线，可指定多项式的阶数，1为直线，默认不绘制。
    smooth：指定绘图时是否对曲线进行平滑处理，仅适用于少量数据构造的曲线，默认打开。
    date_range：绘制时序图时强制横轴的开始和结束日期，默认关闭。
    date_freq：绘制时序图时强制横轴的日期间隔大小。默认关闭，由系统自动决定。
    annotate：绘图时是否将曲线名称标注在曲线末端。默认关闭（使用传统图例），以避免重叠。
    
    preprocess：绘图前是否进行数据预处理，默认不使用。
    预处理方式：支持标准化、正态化、取对数和同步缩放法，常用的为同步缩放法。
    scaling_option：指定同步缩放法的对齐选项，支持均值、最小值、起点值、百分比和变化率方法。
    其中，百分比和变化率方法常用。适用于数值差异大的价格走势对比分析，其他指标不适用或效果不明显。
    
    printout：仅适用于有相关功能的指标（例如RAR）打开结果表格输出，默认关闭。
    
    source：指定证券基础数据来源，默认由系统决定。当系统找到的数据不理想时，可手动指定。
    若指定雅虎财经数据源，需要拥有访问该网站的权限。
    
    示例：
    stocks1=find_peers_china('门户网站',top=10)
    df=security_trend(stocks1,
                  indicator='sharpe',
                  start='MRY',
                  graph=False,printout=True)
    df=security_trend(stocks1,
                  indicator='Exp Ret%',
                  start='MRY')
    """    
    DEBUG=False
    is_yfinance_work=False
    
    if mark_high: mark_top=True
    if mark_low: mark_bottom=True  
        
    print(f"  Looking for info of specified securities ...")
    
    #critical_value=attention_value
        
    portfolio_flag=False #标志：ticker中是否含有投资组合
    ticker=tickers_cvt2yahoo(ticker) #支持多种形式证券代码格式
    
    # 检查证券代码
    if isinstance(ticker,str):
        ticker_num=1
        tickers=[ticker]
    elif isinstance(ticker,list):
        ticker_num=len(ticker)
        tickers=ticker
        for t in tickers: #检查列表中是否存在投资组合
            if isinstance(t,dict):
                portfolio_flag=True
                #print("  #Warning(security_trend): only RAR and CAPM beta indicators support portfolio")
                #print("  All other indicators do not support portfolio")
    elif isinstance(ticker,dict): #检查是否投资组合
        portfolio_flag=True
        ticker_num=1
        tickers=[ticker]
        #print("  #Warning(security_trend): only RAR and CAPM beta indicators support portfolio")
        #print("  All other indicators do not support portfolio")
    else:
        print("  #Warning(security_trend): unrecognizable security codes",ticker)
        return None
    
    # 检查日期：如有错误自动更正
    fromdate,todate=start_end_preprocess(start=start,end=end)
    
    # 处理K线图=================================================================
    if kline and not kline_demo:
        if portfolio_flag:
            print("  #Warning(security_trend): ticker of or with portfolio does not support for K line")
            return None
        
        # 跟踪
        #print(tickers[0],fromdate,todate)
        if start in ['default']:
            fromdate=date_adjust(todate,adjust=-60)
        if not isinstance(mav,list):
            mav=[mav]
        df=candlestick(stkcd=tickers[0],start=fromdate,end=todate,mav=mav, \
                       ticker_type=ticker_type,facecolor=facecolor,loc=loc1)
        return df

    if kline and kline_demo:
        if portfolio_flag:
            print("  #Warning(security_trend): ticker of or with portfolio does not support for K line")
            return None
        
        if start in ['default']:
            fromdate=date_adjust(todate,adjust=-7)
        
        df=candlestick_demo(tickers[0],start=fromdate,end=todate, \
                            ticker_type=ticker_type,facecolor=facecolor)
        return df

    # 处理股票分红和股票分拆：境外股票需要访问雅虎财经=============================
    if dividend:
        if portfolio_flag:
            print("  #Warning(security_trend): investment portfolio does not support for stock dividend")
            return None
        
        if start in ['default']:
            fromdate=date_adjust(todate,adjust=-365*5)  
            
        if is_A_share(tickers[0]):
            stock_profile_china(tickers[0],category='dividend', \
                                    start=fromdate,facecolor=facecolor)
            return None
        else:
            #print("  Trying to access Yahoo via yfinance for stock dividend ...")   
            df=None
            if is_yfinance_work:
                df=stock_dividend(ticker=tickers[0],start=fromdate,end=todate,facecolor=facecolor)
            if df is None:
                df=get_dividend_yq(ticker=tickers[0],start=fromdate,end=todate,facecolor=facecolor)

            return df

    if split:
        if portfolio_flag:
            print("  #Warning(security_trend): investment portfolio does not support for stock split")
            return None
        
        if start in ['default']:
            fromdate=date_adjust(todate,adjust=-365*5)  
        #print("  Trying to access Yahoo via yfinance for stock split ...")    
        df=None
        if is_yfinance_work:
            df=stock_split(ticker=tickers[0],start=fromdate,end=todate,facecolor=facecolor)
        if df is None:
            df=get_split_yq(ticker=tickers[0],start=fromdate,end=todate,facecolor=facecolor)
            
        return df
    

    # 检查趋势指标：是否字符串或列表=================================================
    if isinstance(indicator,str):
        measures=[indicator]
        indicator_num=1
    elif isinstance(indicator,list):
        measures=indicator
        indicator_num=len(indicator)
    else:
        print("  #Warning(security_trend): unrecognizeable indicator(s) for",indicator)
        return None
            
    # 检查趋势指标
    indicator_list1=['Open','Close','Adj Close','High','Low',
             'Daily Ret','Daily Ret%','Daily Adj Ret','Daily Adj Ret%',
             'log(Daily Ret)','log(Daily Adj Ret)',
             'Weekly Ret','Weekly Ret%','Weekly Adj Ret','Weekly Adj Ret%',
             'Monthly Ret','Monthly Ret%',
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
             'Weekly Adj Ret LPSD', 'Weekly Adj Ret LPSD%', 
             'Monthly Ret LPSD',
             'Monthly Ret LPSD%', 'Monthly Adj Ret LPSD', 'Monthly Adj Ret LPSD%',
             'Quarterly Ret LPSD', 'Quarterly Ret LPSD%', 'Quarterly Adj Ret LPSD',
             'Quarterly Adj Ret LPSD%', 'Annual Ret LPSD', 'Annual Ret LPSD%',
             'Annual Adj Ret LPSD', 'Annual Adj Ret LPSD%', 'Exp Ret LPSD',
             'Exp Ret LPSD%', 'Exp Adj Ret LPSD', 'Exp Adj Ret LPSD%',
             ]

    indicator_list2=['treynor','sharpe','sortino','alpha','Treynor','Sharpe','Sortino','Alpha']
    indicator_list3=['pe','pb','mv','PE','PB','MV','Pe','Pb','Mv','ROE','roe','Roe']
    indicator_list4=['beta','Beta','BETA']
    
    # 是否属于支持的指标
    for m in measures:
        if not (m in indicator_list1 + indicator_list2 + indicator_list3 + indicator_list4):
            print("  #Error(security_trend): unsupported indicator for",m)
            print("  Supported indicators:")
            printlist(indicator_list1,numperline=4,beforehand='  ',separator='   ')
            printlist(indicator_list2,numperline=5,beforehand='  ',separator='   ')
            printlist(indicator_list3,numperline=5,beforehand='  ',separator='   ')
            printlist(indicator_list4,numperline=5,beforehand='  ',separator='   ')
            return None
        
    #检查是否跨组比较：不能同时支持indicator_list1/2/3/4的指标，即不能跨组比较！
    indicator_group1=False #组1：普通指标（股价，收益率，风险）
    indicator_group2=False #组2：RAR指标（夏普/阿尔法/索替诺/特雷诺指标）
    indicator_group3=False #组3：估值指标（市盈率，市净率，市值）
    indicator_group4=False #组4：贝塔系数
    
    list_group1=list_group2=list_group3=list_group4=0
    for m in measures:
        if m in indicator_list4:
            list_group4=1
            indicator_group4=True    
            measures = [x.lower() for x in measures]  
            
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
            
    if list_group1+list_group2+list_group3+list_group4 >= 2:
        print("  #Error(security_trend): cannot support hybrid indicators together for",list2str(measures))
        return None
    
    #检查指标是否支持投资组合：暂不支持组1/3的指标
    """
    if portfolio_flag and (indicator_group1 or indicator_group3):
        print("  #Warning(security_trend): ticker of or with portfolio does not support indicator",list2str(measures))
        return None
    """
    # 情形1：单个证券，单个普通指标===============================================
    # 绘制零线：由绘图函数自动判断
    zeroline=False
    """
    if (critical_value != ''):
        if isinstance(critical_value,float) or isinstance(critical_value,int):
            zeroline=critical_value
    """
    if ticker_num==1 and indicator_num==1 and indicator_group1:
        df=security_indicator(ticker=tickers[0],indicator=measures[0],adjust=adjust, \
                              fromdate=fromdate,todate=todate, \
                              zeroline=zeroline, \
                              average_value=average_value, \
                                    attention_value=attention_value,attention_value_area=attention_value_area, \
                                    attention_point=attention_point,attention_point_area=attention_point_area, \
                              datatag=datatag,power=power,graph=graph, \
                              source=source,loc=loc1, \
                              mark_top=mark_top,mark_bottom=mark_bottom, \
                              mark_start=mark_start,mark_end=mark_end, \
                              ticker_type=ticker_type, \
                              facecolor=facecolor)
        return df
    
    # 情形2：单个证券，两个普通指标，twinx==True/UD/LR ===========================
    if ticker_num==1 and indicator_num == 2 and indicator_group1 and twinx:
        if DEBUG:
            print("Scenario 2: ticker_num==1 and indicator_num == 2 and indicator_group1 and twinx")
            print("attention_value=",attention_value)
            print("attention_point=",attention_point)
        
        df=compare_security(tickers=tickers[0],measures=measures[:2], \
                            adjust=adjust, \
                            fromdate=fromdate,todate=todate,twinx=twinx, \
                                attention_value=attention_value,attention_value_area=attention_value_area, \
                                attention_point=attention_point,attention_point_area=attention_point_area, \
                            loc1=loc1,loc2=loc2,graph=graph,source=source, \
                            ticker_type=ticker_type,facecolor=facecolor)
        return df
    
    # 情形3：单个证券，两个及以上普通指标，twinx==False ==========================
    if ticker_num==1 and indicator_num >= 2 and indicator_group1 and not twinx:
        if DEBUG:
            print("Scenario 3: ticker_num==1 and indicator_num >= 2 and indicator_group1 and not twinx")
            print("attention_value=",attention_value)
            print("attention_point=",attention_point)
        
        df=security_mindicators(ticker=tickers[0],measures=measures, \
                                adjust=adjust, \
                                fromdate=fromdate,todate=todate, \
                                    attention_value=attention_value,attention_value_area=attention_value_area, \
                                    attention_point=attention_point,attention_point_area=attention_point_area, \
                                graph=graph,smooth=smooth,band_area=band_area,loc=loc1, \
                                date_range=date_range,date_freq=date_freq, \
                                annotate=annotate,annotate_value=annotate_value, \
                                source=source,
                                mark_top=mark_top,mark_bottom=mark_bottom, \
                                mark_start=mark_start,mark_end=mark_end, \
                                ticker_type=ticker_type,facecolor=facecolor)
        return df
    
    # 情形4：两个证券，取第一个普通指标，twinx==True =============================
    if ticker_num==2 and indicator_group1 and twinx:
        if DEBUG:
            print("Scenario 4: ticker_num==2 and indicator_group1 and twinx")
            print("attention_value=",attention_value)
            print("attention_point=",attention_point)
        
        df=compare_security(tickers=tickers,measures=measures[0], \
                            adjust=adjust, \
                            fromdate=fromdate,todate=todate,twinx=twinx, \
                                attention_value=attention_value,attention_value_area=attention_value_area, \
                                attention_point=attention_point,attention_point_area=attention_point_area, \
                            loc1=loc1,loc2=loc2,graph=graph,source=source, \
                            ticker_type=ticker_type,facecolor=facecolor)
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
    """
    if (critical_value != ''):
        if isinstance(critical_value,float) or isinstance(critical_value,int):
            axhline_value=critical_value
            axhline_label='零线'
    """    
    if ((ticker_num == 2 and not twinx) or ticker_num > 2) and indicator_group1:
        if DEBUG:
            print("Scenario 5: ((ticker_num == 2 and not twinx) or ticker_num > 2) and indicator_group1")
            print("attention_value=",attention_value)
            print("attention_point=",attention_point)

        df=compare_msecurity(tickers=tickers,measure=measures[0], \
                      start=fromdate,end=todate, \
                        attention_value=attention_value,attention_value_area=attention_value_area, \
                        attention_point=attention_point,attention_point_area=attention_point_area, \
                      adjust=adjust, \
                      axhline_value=axhline_value,axhline_label=axhline_label, \
                      preprocess=preprocess,linewidth=linewidth, \
                      scaling_option=scaling_option, \
                        band_area=band_area, \
                      graph=graph,loc=loc1, \
                      annotate=annotate,annotate_value=annotate_value, \
                      smooth=smooth, \
                      source=source, \
                      mark_top=mark_top,mark_bottom=mark_bottom, \
                      mark_start=mark_start,mark_end=mark_end, \
                      ticker_type=ticker_type,facecolor=facecolor)
        return df

    # 情形6：单个或多个证券，单个或多个RAR指标，支持投资组合=======================
    # 注意：收益率类型支持滚动收益率和扩展收益率，但不建议混合使用，因为难以解释结果
    # 复权价：使用ret_type为xx Adj Ret%即可
    if indicator_group2:
        if DEBUG:
            print("Scenario 6: indicator_group2 RAR")
            print("attention_value=",attention_value)
            print("attention_point=",attention_point)
        
        # ret_type要使用复权价
        df=compare_rar_security(ticker=tickers,start=fromdate,end=todate,indicator=measures, \
                                 ret_type=ret_type,RF=RF,regression_period=regression_period, \
                                     attention_value=attention_value,attention_value_area=attention_value_area, \
                                     attention_point=attention_point,attention_point_area=attention_point_area, \
                                         band_area=band_area, \
                                 graph=graph,axhline_value=0,axhline_label='',power=power, \
                                 loc1=loc1, \
                                 printout=printout, \
                                 sortby=sortby,trailing=trailing,trend_threshhold=trend_threshhold, \
                                 annotate=annotate,annotate_value=annotate_value, \
                                 mark_top=mark_top,mark_bottom=mark_bottom, \
                                 mark_start=mark_start,mark_end=mark_end, \
                                 mktidx=market_index,source=source, \
                                 ticker_type=ticker_type,facecolor=facecolor)  
        return df
    
    # 情形7：单个或多个证券，CAPM贝塔系数=========================================
    if indicator_group4:
        #if 'adj' in ret_type.lower() and adjust == '':
        if adjust == '':
            # 使用前复权价
            adjust='qfq'
            
        df=compare_beta_security(ticker=tickers,start=fromdate,end=todate, \
                adjust=adjust, \
                RF=RF,regression_period=regression_period, \
                    attention_value=attention_value,attention_value_area=attention_value_area, \
                    attention_point=attention_point,attention_point_area=attention_point_area, \
                        band_area=band_area, \
                graph=graph,facecolor=facecolor,loc=loc1,power=power, \
                annotate=annotate,annotate_value=annotate_value, \
                mark_top=mark_top,mark_bottom=mark_bottom, \
                mark_start=mark_start,mark_end=mark_end, \
                mktidx=market_index,source=source, \
                ticker_type=ticker_type)
        
        return df
    
    
    # 情形8：估值指标PE/PB/MV/ROE，仅针对股票/行业指数代码，无需ticker_type========
    if indicator_group3:
        df=security_valuation(tickers=tickers,indicators=measures,start=fromdate,end=todate, \
                              preprocess=preprocess,scaling_option=scaling_option, \
                              twinx=twinx,loc1=loc1,loc2=loc2, \
                              graph=graph,facecolor=facecolor, \
                                     attention_value=attention_value,attention_value_area=attention_value_area, \
                                     attention_point=attention_point,attention_point_area=attention_point_area, \
                                         band_area=band_area, \
                              annotate=annotate,annotate_value=annotate_value, \
                              mark_top=mark_top,mark_bottom=mark_bottom, \
                              mark_start=mark_start,mark_end=mark_end)
        return df
    
    # 其他未预料情形
    print("  #Warning(security_trend): unexpected combination of security(ies) and indicator(s):-(")
    
    return None

#==============================================================================

#==============================================================================
#==============================================================================
#==============================================================================











