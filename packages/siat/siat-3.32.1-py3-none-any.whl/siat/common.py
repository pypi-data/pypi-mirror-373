# -*- coding: utf-8 -*-
"""
本模块功能：SIAT公共基础函数
所属工具包：证券投资分析工具SIAT 
SIAT：Security Investment Analysis Tool
创建日期：2019年7月16日
最新修订日期：2025年2月15日
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
import pandas as pd
#==============================================================================
SUFFIX_LIST_CN=['SS','SZ','BJ','SW','SH']
SUFFIX_LIST_HK=['HK']
#==============================================================================

if __name__=='__main__':
    ticker='000858.SZ'
    ticker='AAPL'
    
    security_in_China(ticker)
    
def security_in_China(ticker):
    """
    功能：判断证券代码，是否在中国市场
    """
    
    tlist=ticker.split('.')
    if len(tlist) == 1: return False
    else:
        if tlist[1] in SUFFIX_LIST_CN:
            return True
        else:
            return False
    
#==============================================================================    
#设置全局语言环境
import pickle

def check_language():
    """
    查询全局语言设置
    """
    try:
        with open('siat_language.pkl','rb') as file:
            lang=pickle.load(file)
    except:
        lang='Chinese'
        
    return lang

def set_language(lang='Chinese'):
    """
    修改全局语言设置
    """
    
    if lang in ['English','Chinese']:
        with open('siat_language.pkl','wb') as file:
            pickle.dump(lang,file)
        print("  Global language is set to",lang)
    else:
        print("  Warning: undefined language",lang)
        
    return

def text_lang(txtcn,txten):
    """
    功能：适应双语文字，中文环境返回txtcn，英文环境返回txten
    """
    lang=check_language()
    
    if lang=='Chinese': txt=txtcn
    else: txt=txten
    
    return txt


#==============================================================================
"""
def today():
    \"""
    返回今日的日期
    \"""
    import datetime; now=datetime.datetime.now()
    jinri=now.strftime("%Y-%m-%d")
    
    return jinri

if __name__=='__main__':
    today()
"""
#==============================================================================

def now():
    """
    返回今日的日期
    """
    import datetime; dttime=datetime.datetime.now()
    xianzai=dttime.strftime("%Y-%m-%d %H:%M:%S")
    
    return xianzai

if __name__=='__main__':
    now()
#==============================================================================

def hello():
    """
    返回当前环境信息
    """
    #当前系统信息
    import platform
    ossys=platform.system()
    (arch,_)=platform.architecture()
    osver=platform.platform()    
    print(ossys,arch,osver)
    
    #Python版本信息
    import sys
    pyver=sys.version
    pos=pyver.find(' ')
    pyver1=pyver[:pos]
    print("Python",pyver1,end=', ')
    
    #siat版本信息
    import pkg_resources
    siatver=pkg_resources.get_distribution("siat").version    
    print("siat",siatver)
    
    #运行环境
    import sys; pypath=sys.executable
    pos=pypath.rfind('\\')
                     
    pypath1=pypath[:pos]
    print("Located in",pypath1)

    from IPython import get_ipython
    ipy_str = str(type(get_ipython())) 
    if 'zmqshell' in ipy_str:
        print("Working in Jupyter environment")
    else:
        print("NOT in Jupyter environment")
    
    #当前日期时间
    print("Currently",now())
    
    return

if __name__=='__main__':
    hello()
#==============================================================================
def ticker_check(ticker, source="yahoo"):
    """
    检查证券代码，对于大陆证券代码、香港证券代码和东京证券代码进行修正。
    输入：证券代码ticker，数据来源source。
    上交所证券代码后缀为.SS或.SH或.ss或.sh，深交所证券代码为.SZ或.sz
    港交所证券代码后缀为.HK，截取数字代码后4位
    东京证交所证券代码后缀为.T，截取数字代码后4位
    source：yahoo或tushare
    返回：字母全部转为大写。若是大陆证券返回True否则返回False。
    若选择yahoo数据源，上交所证券代码转为.SS；
    若选择tushare数据源，上交所证券代码转为.SH
    """
    #测试用，完了需要注释掉
    #ticker="600519.sh"
    #source="yahoo"
    
    #将字母转为大写
    ticker1=ticker.upper()
    #截取字符串最后2/3位
    suffix2=ticker1[-2:]
    suffix3=ticker1[-3:]
    
    #判断是否大陆证券
    if suffix3 in ['.SH', '.SS', '.SZ']:
        prc=True
    else: prc=False

    #根据数据源的格式修正大陆证券代码
    if (source == "yahoo") and (suffix3 in ['.SH']):
        ticker1=ticker1.replace(suffix3, '.SS')        
    if (source == "tushare") and (suffix3 in ['.SS']):
        ticker1=ticker1.replace(suffix3, '.SH')  

    #若为港交所证券代码，进行预防性修正，截取数字代码后4位，加上后缀共7位
    if suffix3 in ['.HK']:
        ticker1=ticker1[-7:]     

    #若为东交所证券代码，进行预防性修正，截取数字代码后4位，加上后缀共6位
    if suffix2 in ['.T']:
        ticker1=ticker1[-6:]  
    
    #返回：是否大陆证券，基于数据源/交易所格式修正后的证券代码
    return prc, ticker1        

#测试各种情形
if __name__=='__main__':
    prc, ticker=ticker_check("600519.sh","yahoo")
    print(prc,ticker)
    print(ticker_check("600519.SH","yahoo"))    
    print(ticker_check("600519.ss","yahoo"))    
    print(ticker_check("600519.SH","tushare"))    
    print(ticker_check("600519.ss","tushare"))    
    print(ticker_check("000002.sz","tushare"))
    print(ticker_check("000002.sz","yahoo"))
    print(ticker_check("00700.Hk","yahoo"))
    print(ticker_check("99830.t","yahoo"))

#==============================================================================
def tickers_check(tickers, source="yahoo"):
    """
    检查证券代码列表，对于大陆证券代码、香港证券代码和东京证券代码进行修正。
    输入：证券代码列表tickers，数据来源source。
    上交所证券代码后缀为.SS或.SH或.ss或.sh，深交所证券代码为.SZ或.sz
    港交所证券代码后缀为.HK，截取数字代码后4位
    东京证交所证券代码后缀为.T，截取数字代码后4位
    source：yahoo或tushare
    返回：证券代码列表，字母全部转为大写。若是大陆证券返回True否则返回False。
    若选择yahoo数据源，上交所证券代码转为.SS；
    若选择tushare数据源，上交所证券代码转为.SH
    """
    #检查列表是否为空
    if tickers[0] is None:
        print("*** 错误#1(tickers_check)，空的证券代码列表:",tickers)
        return None         
    
    tickers_new=[]
    for t in tickers:
        _, t_new = ticker_check(t, source=source)
        tickers_new.append(t_new)
    
    #返回：基于数据源/交易所格式修正后的证券代码
    return tickers_new

#测试各种情形
if __name__=='__main__':
    tickers=tickers_check(["600519.sh","000002.sz"],"yahoo")
    print(tickers)
#==============================================================================
def check_period(fromdate, todate):
    """
    功能：根据开始/结束日期检查日期与期间的合理性
    输入参数：
    fromdate：开始日期。格式：YYYY-MM-DD
    enddate：开始日期。格式：YYYY-MM-DD
    输出参数：
    validity：期间合理性。True-合理，False-不合理
    start：开始日期。格式：datetime类型
    end：结束日期。格式：datetime类型
    """
    import pandas as pd
    
    #测试开始日期的合理性
    try:
        start=pd.to_datetime(fromdate)
    except:
        print("    #Error(check_period), invalid date:",fromdate)
        return None, None, None         
    
    #开始日期不能晚于今日
    import datetime
    todaydt = pd.to_datetime(datetime.date.today())
    if start > todaydt:
        print("    #Error(check_period), invalid start date:",fromdate)
        return None, None, None         
    
    #测试结束日期的合理性
    try:
        end=pd.to_datetime(todate)
    except:
        print("    #Error(check_period): invalid date:",todate)
        return None, None, None          
    
    #测试日期期间的合理性
    if start > end:
        print("    #Error(check_period): invalid period: from",fromdate,"to",todate)
        return None, None, None     

    return True, start, end

if __name__ =="__main__":
    check_period('2020-1-1','2020-2-4')
    check_period('2020-1-1','2010-2-4')
    
    start='2020-1-1'; end='2022-12-20'
    result,startpd,endpd=check_period(start,end)

#==============================================================================
def check_period2(fromdate, todate):
    """
    功能：根据开始/结束日期检查日期与期间的合理性
    输入参数：
    fromdate：开始日期。格式：YYYY-MM-DD
    enddate：开始日期。格式：YYYY-MM-DD
    输出参数：
    validity：期间合理性。True-合理，False-不合理
    start：开始日期。格式：规范字符串类型
    end：结束日期。格式：规范字符串类型
    """
    
    result,startpd,endpd=check_period(fromdate, todate)
    if result:
        start=startpd.strftime("%Y-%m-%d")
        end=endpd.strftime("%Y-%m-%d")
    else:
        start=end=None
        

    return result, start, end

if __name__ =="__main__":
    check_period2('2020-1-1','2020-2-4')
#==============================================================================
if __name__ =="__main__":
    start_date = "2022-1-1"
    end_date = "2022-1-31"
    result = calculate_days(start_date, end_date)
    print("日期间隔天数为:", result)
 
def calculate_days(start_date, end_date):
    
    _,start_date1=check_date2(start_date)
    _,end_date1=check_date2(end_date)
    
    from datetime import date
    start = date.fromisoformat(start_date1)
    end = date.fromisoformat(end_date1)
    
    delta = (end - start).days + 1
    return delta
 

#==============================================================================
if __name__ =="__main__":
    basedate='2020-3-17' 
    adjust=-365    
    newdate = date_adjust(basedate, adjust)
    print(newdate) 
    
def date_adjust(basedate, adjust=0):
    """
    功能：将给定日期向前或向后调整特定的天数
    输入：基础日期，需要调整的天数。
    basedate: 基础日期。
    adjust：需要调整的天数，负数表示向前调整，正数表示向后调整。
    输出：调整后的日期。
    """
    #检查基础日期的合理性
    import pandas as pd    
    try:
        bd=pd.to_datetime(basedate)
    except:
        print("  #Error(date_adjust): invalid:",basedate)
        return None

    #调整日期
    from datetime import timedelta
    nd = bd+timedelta(days=adjust)    
    
    #重新提取日期
    newdate=nd.date()   
    return str(newdate)
 
if __name__ =="__main__":
    basedate='2024-3-17' 
    
    adjust_year=-1; adjust_month=-1; adjust_day=-1
    adjust_year=-1; adjust_month=-1; adjust_day=-17
    adjust_year=-1; adjust_month=0; adjust_day=-17
    adjust_year=0; adjust_month=-3; adjust_day=0
    adjust_year=0; adjust_month=-13; adjust_day=0
    adjust_year=0; adjust_month=-15; adjust_day=0
    adjust_year=0; adjust_month=-27; adjust_day=0
    adjust_year=0; adjust_month=-27; adjust_day=0
    
    adjust_year=0; adjust_month=0; adjust_day=15
    adjust_year=0; adjust_month=10; adjust_day=0
    adjust_year=0; adjust_month=22; adjust_day=0
    
    adjust_year=0; adjust_month=-1; adjust_day=-1
    adjust_year=0; adjust_month=-2; adjust_day=-1
    adjust_year=0; adjust_month=-3; adjust_day=-1
    adjust_year=0; adjust_month=-6; adjust_day=-1
    adjust_year=-1; adjust_month=0; adjust_day=0
    adjust_year=-2; adjust_month=0; adjust_day=0
    adjust_year=-3; adjust_month=0; adjust_day=0
    adjust_year=-5; adjust_month=0; adjust_day=0
    
    to_prev_month_end=False    
    to_prev_month_end=True
    
    to_prev_year_end=False    
    to_prev_year_end=True
    
    date_adjust2(basedate,adjust_year,adjust_month,adjust_day,to_prev_month_end,to_prev_year_end)

def date_adjust2(basedate,adjust_year=0,adjust_month=0,adjust_day=0, \
                 to_prev_month_end=False,to_prev_year_end=False):
    """
    功能：将给定日期向前或向后调整特定的天数，按照年月日精确调整
    输入：基础日期，需要调整的天数。
    basedate: 基础日期。
    adjust_year, adjust_month, adjust_day：分别调整的年月日数量，负数向前调整，正数向后调整。
    输出：调整后的日期字符串。
    """
    import pandas as pd    
    from datetime import datetime, timedelta

    #检查基础日期的合理性
    try:
        bd=pd.to_datetime(basedate)
    except:
        print("  #Error(date_adjust2): invalid date",basedate)
        return None

    #将基础日期分解为年月日
    bd_year=bd.year
    bd_month=bd.month
    bd_day=bd.day
    
    #预处理调整的月数
    if adjust_month <= -12:
        adjust_year=adjust_year + int(adjust_month / 12)
        adjust_month=adjust_month % -12
    if adjust_month >= 12:
        adjust_year=adjust_year + int(adjust_month / 12)
        adjust_month=adjust_month % 12        
    
    #调整年
    new_year=bd_year + adjust_year
    
    #调整月份
    new_month=bd_month + adjust_month
    if new_month <= 0:
        new_month=new_month + 12
        new_year=new_year - 1
    if new_month > 12:
        new_month=new_month % 12
        new_year=new_year + 1
        
    #合成中间日期：新年份，新月份，原日期
    while True:
        try:
            ndym=datetime(new_year,new_month,bd_day)
            break
        except:
            bd_day=bd_day - 1
            continue
        
    #调整日期
    nd=ndym + timedelta(days=adjust_day)
    
    #如果还需要调整到上年年末，但不可同时使用调整到上月月末
    if to_prev_year_end:
        to_prev_month_end=False
        
        nd_year=nd.year - 1
        nd=datetime(nd_year,12,31)
    
    #如果还需要调整到上月月末
    if to_prev_month_end:
        nd_day=nd.day
        nd=nd + timedelta(days=-nd_day)

    #提取日期字符串
    newdate=nd.date()  
    
    return str(newdate)
    
#==============================================================================
if __name__ =="__main__":
    portfolio={'Market':('US','^GSPC'),'EDU':0.4,'TAL':0.3,'TEDU':0.2}
    
    portfolio={'Market':('China','000001.SS','股债基组合'),'600519.SS':50,'sh010504':150,'sh010504':300}
    
    Market={'Market':('China','000300.SS','股债基组合')}
    Stocks={'600519.SS':0.4,#股票：贵州茅台
            'sh010504':[0.3,'bond'],#05国债⑷
            '010504':('fund',0.2),#招商稳兴混合C基金
            }
    portfolio=dict(Market,**Stocks)
    
    decompose_portfolio(portfolio)

def decompose_portfolio(portfolio):
    """
    功能：将一个投资组合字典分解为股票代码列表和份额列表
    投资组合的结构：{'Market':('US','^GSPC'),'AAPL':0.5,'MSFT':0.3,'IBM':0.2}
    输入：投资组合
    输出：市场，市场指数，股票代码列表和份额列表
    
    注意：字典中相同的键会被合并为一个
    新功能：分辨股票、债券和基金
    """
    #从字典中提取信息
    keylist=list(portfolio.keys()) #注意：字典中相同的键会被合并为一个
    scope=portfolio[keylist[0]][0]
    mktidx=portfolio[keylist[0]][1]
    
    slist=[]
    plist=[]
    for key,value in portfolio.items():
        slist=slist+[key]
        plist=plist+[value]
    stocklist=slist[1:]    
    portionlist=plist[1:]
    
    #识别证券类别
    stype_list=['auto','stock','bond','fund']
    ticker_type=[]
    new_portionlist=[]
    for p in portionlist:
        if isinstance(p,int) or isinstance(p,float):
            ticker_type=ticker_type+['auto']
            new_portionlist=new_portionlist+[p]
        elif isinstance(p,list) or isinstance(p,tuple):
            ptype=False; pportion=False
            p0=p[0]; p1=p[1]
            
            if isinstance(p0,int) or isinstance(p0,float):
                pportion=True
                new_portionlist=new_portionlist+[p0]
            elif isinstance(p0,str):
                ptype=True
                if p0 not in stype_list:
                    p0='auto'
                ticker_type=ticker_type+[p0]
            
            if isinstance(p1,int) or isinstance(p1,float):
                pportion=True
                new_portionlist=new_portionlist+[p1]
            elif isinstance(p1,str):
                ptype=True
                if p1 not in stype_list:
                    p1='auto'
                ticker_type=ticker_type+[p1]         
            
            #未能确定
            if ptype==False: 
                ticker_type=ticker_type+['auto']
            if pportion==False:
                new_portionlist=new_portionlist+[0]
        

    return scope,mktidx,stocklist,new_portionlist,ticker_type

if __name__=='__main__':
    portfolio1={'Market':('US','^GSPC'),'EDU':0.4,'TAL':0.3,'TEDU':0.2}
    decompose_portfolio(portfolio1)

def portfolio_name(portfolio):
    """
    功能：解析一个投资组合的名字
    输入：投资组合
    输出：投资组合的自定义名称，未定义的返回"投资组合"
    注意：为了维持兼容性，特此定义此函数
    """
    #从字典中提取信息
    keylist=list(portfolio.keys())
    try:
        name=portfolio[keylist[0]][2]
    except:
        #name="PF1"
        name=text_lang("投资组合","Portfolio")

    return name    

if __name__=='__main__':
    portfolio={'Market':('US','^GSPC','我的组合001'),'EDU':0.4,'TAL':0.3,'TEDU':0.2}
    portfolio_name(portfolio)

if __name__=='__main__':
    portfolio={'Market':('US','^GSPC','China Edtraining'),'EDU':0.4,'TAL':0.3,'TEDU':0.2}
    portfolio='600519.SS'
    
    isinstance_portfolio(portfolio)

def isinstance_portfolio(portfolio):
    """
    功能：判断是否投资组合
    输入：投资组合
    输出：True, False
    注意：为了维持兼容性，特此定义此函数
    """    
    result=True
    
    try:
        scope,mktidx,tickerlist,sharelist,ticker_type=decompose_portfolio(portfolio)
    except:
        result=False
        
    return result
    
#==============================================================================
def calc_monthly_date_range(start,end):
    """
    功能：返回两个日期之间各个月份的开始和结束日期
    输入：开始/结束日期
    输出：两个日期之间各个月份的开始和结束日期元组对列表
    """
    #测试用
    #start='2019-01-05'
    #end='2019-06-25'    
    
    import pandas as pd
    startdate=pd.to_datetime(start)
    enddate=pd.to_datetime(end)

    mdlist=[]
    #当月的结束日期
    syear=startdate.year
    smonth=startdate.month
    import calendar
    sdays=calendar.monthrange(syear,smonth)[1]
    from datetime import date
    slastday=pd.to_datetime(date(syear,smonth,sdays))

    if slastday > enddate: slastday=enddate
    
    #加入第一月的开始和结束日期
    import bisect
    bisect.insort(mdlist,(startdate,slastday))
    
    #加入结束月的开始和结束日期
    eyear=enddate.year
    emonth=enddate.month
    efirstday=pd.to_datetime(date(eyear,emonth,1))   
    if startdate < efirstday:
        bisect.insort(mdlist,(efirstday,enddate))
    
    #加入期间内各个月份的开始和结束日期
    from dateutil.relativedelta import relativedelta
    next=startdate+relativedelta(months=+1)
    while next < efirstday:
        nyear=next.year
        nmonth=next.month
        nextstart=pd.to_datetime(date(nyear,nmonth,1))
        ndays=calendar.monthrange(nyear,nmonth)[1]
        nextend=pd.to_datetime(date(nyear,nmonth,ndays))
        bisect.insort(mdlist,(nextstart,nextend))
        next=next+relativedelta(months=+1)
    
    return mdlist

if __name__=='__main__':
    mdp1=calc_monthly_date_range('2019-01-01','2019-06-30')
    mdp2=calc_monthly_date_range('2000-01-01','2000-06-30')   #闰年
    mdp3=calc_monthly_date_range('2018-09-01','2019-03-31')   #跨年
    
    for i in range(0,len(mdp1)):
        start=mdp1[i][0]
        end=mdp1[i][1]
        print("start =",start,"end =",end)


#==============================================================================
def calc_yearly_date_range(start,end):
    """
    功能：返回两个日期之间各个年度的开始和结束日期
    输入：开始/结束日期
    输出：两个日期之间各个年度的开始和结束日期元组对列表
    """
    #测试用
    #start='2013-01-01'
    #end='2019-08-08'    
    
    import pandas as pd
    startdate=pd.to_datetime(start)
    enddate=pd.to_datetime(end)

    mdlist=[]
    #当年的结束日期
    syear=startdate.year
    from datetime import date
    slastday=pd.to_datetime(date(syear,12,31))

    if slastday > enddate: slastday=enddate
    
    #加入第一年的开始和结束日期
    import bisect
    bisect.insort(mdlist,(startdate,slastday))
    
    #加入结束年的开始和结束日期
    eyear=enddate.year
    efirstday=pd.to_datetime(date(eyear,1,1))   
    if startdate < efirstday:
        bisect.insort(mdlist,(efirstday,enddate))
    
    #加入期间内各个年份的开始和结束日期
    from dateutil.relativedelta import relativedelta
    next=startdate+relativedelta(years=+1)
    while next < efirstday:
        nyear=next.year
        nextstart=pd.to_datetime(date(nyear,1,1))
        nextend=pd.to_datetime(date(nyear,12,31))
        bisect.insort(mdlist,(nextstart,nextend))
        next=next+relativedelta(years=+1)
    
    return mdlist

if __name__=='__main__':
    mdp1=calc_yearly_date_range('2013-01-05','2019-06-30')
    mdp2=calc_yearly_date_range('2000-01-01','2019-06-30')   #闰年
    mdp3=calc_yearly_date_range('2018-09-01','2019-03-31')   #跨年
    
    for i in range(0,len(mdp1)):
        start=mdp1[i][0]
        end=mdp1[i][1]
        print("start =",start,"end =",end)

#==============================================================================

def sample_selection(df,start,end):
    """
    功能：根据日期范围start/end选择数据集df的子样本，并返回子样本
    """
    flag,start2,end2=check_period(start,end)
    df_sub=df[df.index >= start2]
    df_sub=df_sub[df_sub.index <= end2]
    
    return df_sub
    
if __name__=='__main__':
    portfolio={'Market':('US','^GSPC'),'AAPL':1.0}
    market,mktidx,tickerlist,sharelist,_=decompose_portfolio(portfolio)
    start='2020-1-1'; end='2020-3-31'
    pfdf=get_portfolio_prices(tickerlist,sharelist,start,end)
    start2='2020-1-10'; end2='2020-3-18'
    df_sub=sample_selection(pfdf,start2,end2)    
    
#==============================================================================
def init_ts():
    """
    功能：初始化tushare pro，登录后才能下载数据
    """
    import tushare as ts
    #设置token
    token='49f134b05e668d288be43264639ac77821ab9938ff40d6013c0ed24f'
    pro=ts.pro_api(token)
    
    return pro
#==============================================================================
def convert_date_ts(y4m2d2):
    """
    功能：日期格式转换，YYYY-MM-DD-->YYYYMMDD，用于tushare
    输入：日期，格式：YYYY-MM-DD
    输出：日期，格式：YYYYMMDD
    """
    import pandas as pd
    try: date1=pd.to_datetime(y4m2d2)
    except:
        print("  #Error(convert_date_ts): invalid date:",y4m2d2)
        return None 
    else:
        date2=date1.strftime('%Y')+date1.strftime('%m')+date1.strftime('%d')
    return date2

if __name__ == '__main__':
    convert_date_ts("2019/11/1")
#==============================================================================
def gen_yearlist(start_year,end_year):
    """
    功能：产生从start_year到end_year的一个年度列表
    输入参数：
    start_year: 开始年份，字符串
    end_year：截止年份
    输出参数：
    年份字符串列表    
    """
    #仅为测试使用，完成后应注释掉
    #start_year='2010'
    #end_year='2019'    
    
    import numpy as np
    start=int(start_year)
    end=int(end_year)
    num=end-start+1    
    ylist=np.linspace(start,end,num=num,endpoint=True)
    
    yearlist=[]
    for y in ylist:
        yy='%d' %y
        yearlist=yearlist+[yy]
    #print(yearlist)
    
    return yearlist

if __name__=='__main__':
    yearlist=gen_yearlist('2013','2019')
#==============================================================================
def print_progress_bar(current,startnum,endnum):
    """
    功能：打印进度数值，每个10%打印一次，不换行
    """
    for i in [9,8,7,6,5,4,3,2,1]:
        if current == int((endnum - startnum)/10*i)+1: 
            print(str(i)+'0%',end=' '); break
        elif current == int((endnum - startnum)/100*i)+1: 
            print(str(i)+'%',end=' '); break
    if current == 2: print('0%',end=' ')

if __name__ =="__main__":
    startnum=2
    endnum=999
    L=range(2,999)
    for c in L: print_progress_bar(c,startnum,endnum)

#==============================================================================
def save_to_excel(df,filedir,excelfile,sheetname="Sheet1"):
    """
    函数功能：将df保存到Excel文件。
    如果目录不存在提示出错；如果Excel文件不存在则创建之文件并保存到指定的sheet；
    如果Excel文件存在但sheet不存在则增加sheet并保存df内容，原有sheet内容不变；
    如果Excel文件和sheet都存在则追加df内容到已有sheet的末尾
    输入参数：
    df: 数据框
    filedir: 目录
    excelfile: Excel文件名，不带目录，后缀为.xls或.xlsx
    sheetname：Excel文件中的sheet名
    输出：
    保存df到Excel文件
    无返回数据
    
    注意：如果df中含有以文本表示的数字，写入到Excel会被自动转换为数字类型保存。
    从Excel中读出后为数字类型，因此将会与df的类型不一致
    """
    DEBUG=True

    #检查目录是否存在
    import os
    try:
        os.chdir(filedir)
    except:
        print("  #Error(save_to_excel): folder does not exist",filedir)        
        return
                
    #取得df字段列表
    dflist=df.columns
    #合成完整的带目录的文件名
    #filename=filedir+'\\'+excelfile
    filename=filedir+'/'+excelfile
    
    import pandas as pd
    try:
        file1=pd.ExcelFile(excelfile)
    except:
        #不存在excelfile文件，直接写入
        #df.to_excel(filename,sheet_name=sheetname,header=True,encoding='utf-8')
        df.to_excel(filename,sheet_name=sheetname,header=True)
        print("  Successfully saved in",filename,"@ sheet",sheetname)
        return
    else:
        #已存在excelfile文件，先将所有sheet的内容读出到dict中        
        dict=pd.read_excel(file1, None)
    file1.close()
    
    #获得所有sheet名字
    sheetlist=list(dict.keys())
    
    #检查新的sheet名字是否已存在
    try:
        pos=sheetlist.index(sheetname)
    except:
        #不存在重复
        dup=False
    else:
        #存在重复，合并内容
        dup=True
        #合并之前可能需要对df中以字符串表示的数字字段进行强制类型转换.astype('int')
        df1=dict[sheetlist[pos]][dflist]
        dfnew=pd.concat([df1,df],axis=0,ignore_index=True)        
        dict[sheetlist[pos]]=dfnew
    
    #将原有内容写回excelfile    
    result=pd.ExcelWriter(filename)
    for s in sheetlist:
        df1=dict[s][dflist]
        #df1.to_excel(result,s,header=True,index=True,encoding='utf-8')
        df1.to_excel(result,s,header=True,index=True)
    #写入新内容
    if not dup: #sheetname未重复
        #df.to_excel(result,sheetname,header=True,index=True,encoding='utf-8')
        df.to_excel(result,sheetname,header=True,index=True)
        if DEBUG:
            #result.save()
            result.close()
        else:
            try:
                #result.save()
                result.close()
            except:
                print("  #Error(save_to_excel): writing file failed for",filename)
                print("  Solution: change file name and try again")
                return

    print("  Successfully saved in",filename,"@ sheet",sheetname)
    return       
#==============================================================================
def set_df_period(df,df_min,df_max):
    """
    功能： 去掉df中日期范围以外的记录
    """
    df1=df[df.index >= df_min]
    df2=df1[df1.index <= df_max]
    return df2

if __name__=='__main__':
    import siat.security_prices as ssp
    df=ssp.get_price('AAPL','2020-1-1','2020-1-31')    
    df_min,df_max=get_df_period(df)    
    df2=set_df_period(df,df_min,df_max)

#==============================================================================
def sigstars(p_value):
    """
    功能：将p_value转换成显著性的星星
    """
    if p_value >= 0.1: 
        stars="   "
        return stars
    if 0.1 > p_value >= 0.05:
        stars="*  "
        return stars
    if 0.05 > p_value >= 0.01:
        stars="** "
        return stars
    if 0.01 > p_value:
        stars="***"
        return stars

#==============================================================================

def regparms(results):
    """
    功能：将sm.OLS回归结果生成数据框，包括变量名称、系数数值、t值、p值和显著性星星
    """
    import pandas as pd
    #取系数
    params=results.params
    df_params=pd.DataFrame(params)
    df_params.columns=['coef']
    
    #取t值
    tvalues=results.tvalues
    df_tvalues=pd.DataFrame(tvalues)
    df_tvalues.columns=['t_values']

    #取p值
    pvalues=results.pvalues
    df_pvalues=pd.DataFrame(pvalues)
    df_pvalues.columns=['p_values']            

    #取rsquared_adj值：单个数值，非数组
    rsquared=results.rsquared
    rsquared_adj=results.rsquared_adj
    
    #生成星星
    df_pvalues['sig']=df_pvalues['p_values'].apply(lambda x:sigstars(x))
    
    #合成
    parms1=pd.merge(df_params,df_tvalues, \
                    how='inner',left_index=True,right_index=True)
    parms2=pd.merge(parms1,df_pvalues, \
                    how='inner',left_index=True,right_index=True)
    
        
    return parms2

#==============================================================================
if __name__=='__main__':
    txt='QDII-指数'

def strlen(txt):
    """
    功能：计算中英文混合字符串的实际长度
    注意：有时不准
    """
    lenTxt = len(txt) 
    lenTxt_utf8 = len(txt.encode('utf-8')) 
    size = int((lenTxt_utf8 - lenTxt)/2 + lenTxt)    

    return size

#==============================================================================

def sort_pinyin(hanzi_list): 
    """
    功能：对列表中的中文字符串按照拼音升序排序
    """
    from pypinyin import lazy_pinyin       
    hanzi_list_pinyin=[]
    hanzi_list_pinyin_alias_dict={}
    
    for single_str in hanzi_list:
        py_r = lazy_pinyin(single_str)
        # print("整理下")
        single_str_py=''
        for py_list in py_r:
            single_str_py=single_str_py+py_list
        hanzi_list_pinyin.append(single_str_py)
        hanzi_list_pinyin_alias_dict[single_str_py]=single_str
    
    hanzi_list_pinyin.sort()
    sorted_hanzi_list=[]
    
    for single_str_py in hanzi_list_pinyin:
        sorted_hanzi_list.append(hanzi_list_pinyin_alias_dict[single_str_py])
    
    return sorted_hanzi_list


#==============================================================================
if __name__=='__main__':
    end_date='2021-11-18'
    pastyears=1

def get_start_date(end_date,pastyears=1):
    """
    输入参数：一个日期，年数
    输出参数：几年前的日期
    """

    import pandas as pd
    try:
        end_date=pd.to_datetime(end_date)
    except:
        print("  #Error(get_start_date): invalid date,",end_date)
        return None
    
    from datetime import datetime,timedelta
    start_date=datetime(end_date.year-pastyears,end_date.month,end_date.day)
    start_date2=start_date-timedelta(days=1)
    # 日期-1是为了保证计算收益率时得到足够的样本数量
    
    start_date3=str(start_date2.year)+'-'+str(start_date2.month)+'-'+str(start_date2.day)
    return start_date3
    
#==============================================================================
def get_ip():
    """
    功能：获得本机计算机名和IP地址    
    """
    #内网地址
    import socket
    hostname = socket.gethostname()
    internal_ip = socket.gethostbyname(hostname)
    
    #公网地址

    return hostname,internal_ip

if __name__=='__main__':
    get_ip()
#==============================================================================
def check_date(adate):
    """
    功能：检查一个日期是否为有效日期
    输入参数：一个日期
    输出：合理日期为True，其他为False
    """
    #仅为测试使用，测试完毕需要注释掉
    #adate='2019-6-31'

    result=True
    import pandas as pd
    try:    
        bdate=pd.to_datetime(adate)
    except:
        print("  #Error(check_date): invalid date",adate)
        #print("Variable(s):",adate)
        result=False
        
    return result

if __name__ =="__main__":
    print(check_date('2019-6-31'))

#==============================================================================
def check_date2(adate):
    """
    功能：检查一个日期是否为有效日期，并转换标准的形式YYYY-MM-DD以便比较大小
    输入参数：一个日期
    输出：合理日期为True，其他为False
    """
    #仅为测试使用，测试完毕需要注释掉
    #adate='2019-6-31'

    result=True
    import pandas as pd
    try:    
        bdate=pd.to_datetime(adate)
    except:
        print("  #Error(check_date2): invalid date",adate)
        #print("Variable(s):",adate)
        result=False
        bdate=None
    
    if result:
        import datetime as dt
        fdate=dt.datetime.strftime(bdate,'%Y-%m-%d')
    else:
        fdate=adate
        
    return result,fdate

if __name__ =="__main__":
    adate='2023-1-25'
    print(check_date2('2019-6-31'))
    print(check_date2('2019-6-30'))
#==============================================================================
def check_start_end_dates(start,end):
    """
    功能：检查一个期间的开始/结束日期是否合理
    输入参数：开始和结束日期
    输出：合理为True，其他为False
    """
    #仅为测试使用，测试完毕需要注释掉
    #adate='2019-6-31'

    if not check_date(start):
        print("Error #1(check_start_end_dates): invalid start date")
        print("Variable(s):",start)
        return False

    if not check_date(end):
        print("Error #2(check_start_end_dates): invalid end date")
        print("Variable(s):",end)
        return False       
    
    if start > end:
        print("Error #3(check_start_end_dates): irrational start/end dates")
        print("Variable(s): from",start,"to",end)
        return False
        
    return True

if __name__ =="__main__":
    print(check_start_end_dates('2019-1-1','2019-8-18'))

#==============================================================================
if __name__ =="__main__":
    date1="2022-9-19"
    date2="2022-9-26"
    
def date_delta(date1,date2):
    """
    功能：计算两个日期之间相隔的天数
    """
    import pandas as pd    
    date1pd=pd.to_datetime(date1)
    date2pd=pd.to_datetime(date2)
    num=(date2pd - date1pd).days

    return num

if __name__ =="__main__":
    date_delta(date1,date2)
#==============================================================================

if __name__=='__main__':
    txt0="上市公司/家"        
        
def hzlen(txt0):
    """
    功能：计算含有汉字的字符串的长度
    """
    #strlen=int((len(txt.encode('utf-8')) - len(txt)) / 2 + len(txt))
    #strlen=int((len(txt.encode('gb18030')) - len(txt)) / 2 + len(txt))
    txt=str(txt0)
    
    import unicodedata
    #Unicode字符有不同的类别
    txtlist=list(unicodedata.category(c) for c in txt)
    strlen=0
    for t in txtlist:
        #类别Lo表示一个非拉丁文字
        if t == 'Lo':
            strlen=strlen+2
        else:
            strlen=strlen+1
    
    return strlen

#==============================================================================
def int10_to_date(int10):
    """
    功能：将10位数字的时间戳转换为日期。
    输入：10位数字的时间戳int10。
    返回：日期字符串。
    """
    import time
    tupTime = time.localtime(int10)
    y4m2d2 = time.strftime("%Y-%m-%d", tupTime)    
    return y4m2d2

if __name__ =="__main__":
    int10=9876543210
    print(int10_to_date(int10))    
#==============================================================================
def equalwidth(string,maxlen=20,extchar='.',endchar='：'):
    """
    输入：字符串，中英文混合
    输出：设定等宽度，自动补齐
    """
    reallen=hzlen(string)
    if maxlen < reallen:
        maxlen = reallen
    return string+extchar*(maxlen-reallen)+endchar

if __name__ =="__main__":
    equalwidth("中文1英文abc",maxlen=20)
#==============================================================================
if __name__ =="__main__":
    longlist=['豆粕', '玉米', '铁矿石', '棉花', '白糖', 'PTA', '甲醇', '橡胶', '沪铜', '黄金', '菜籽粕', '液化石油气', '动力煤']
    numperline=5
    beforehand=' '*4
    separator=' '
    
def printlist(longlist,numperline=5,beforehand='',separator=' '):
    """
    打印长列表，每numperline个一行，超过换行，分隔符为separator
    """
    listlen=len(longlist)
    if listlen==0:
        print("  #Warning(printlist): print list is empty")
        return
    
    counter=0
    lastone=longlist[-1]
    print(beforehand,end='')
    for l in longlist:
        if l == lastone:
            print(l)
            break
        
        counter=counter+1
        if counter <=numperline:
            print(l,end=separator)
        else:
            print('')
            print(beforehand,end='')
            counter=0
        
    print('')
    
    return        

#==============================================================================
if __name__=='__main__':
    ticker='600519.SS'
    ticker='AAPL'
    result,prefix,suffix=split_prefix_suffix(ticker)

def split_prefix_suffix(ticker):
    """
    将证券代码拆分为前后两部分
    """
    #ticker=ticker.upper()
    result=False
    try:
        pos=ticker.index('.')
        prefix=ticker[:pos]
        suffix=ticker[pos+1:]
        result=True
    except:
        prefix=ticker
        suffix=''
        
    return result,prefix,suffix

if __name__=='__main__':
    split_prefix_suffix('600519.SS')
    split_prefix_suffix('600519.ss')
    split_prefix_suffix('AAPL')
    split_prefix_suffix('aapl')
#==================================================================================
if __name__=='__main__': 
    start='2022-1-1'
    end='2023-3-4'

shibor_period_list=['ON','1W','2W','1M','3M','6M','9M','1Y']

def get_shibor_rates_bs(start,end,rate_period='3M'):
    """
    功能：基于Baostock获得指定期间和期限的shibor利率
    start：开始日期
    end：结束日期
    rate_period：利率类型
    
    注意：这里得到的是年化利率，不带百分号，不是日利率！（日利率=年化利率/365）
    """
    #检查日期期间
    valid,start1,end1=check_period(start,end)
    if not valid:
        print("  #Error(get_shibor_rates): invalid date period from",start,"to",end)
        return None
    
    #检查利率类型
    if not (rate_period in shibor_period_list):
        print("  #Error(get_shibor_rates): unsupported rate period",rate_period)
        print("  Supported shibor rate periods:",shibor_period_list)
        return None
    
    #屏蔽函数内print信息输出的类
    import os, sys
    class HiddenPrints:
        def __enter__(self):
            self._original_stdout = sys.stdout
            sys.stdout = open(os.devnull, 'w')

        def __exit__(self, exc_type, exc_val, exc_tb):
            sys.stdout.close()
            sys.stdout = self._original_stdout
    
    import pandas as pd
    import baostock as bs
    # 登陆系统：不显示信息login success!
    with HiddenPrints():
        lg = bs.login()
    # 登陆失败处理
    if not (lg.error_code=='0'):
        print('  Baostock: login respond error_code:'+lg.error_code)
        print('  Baostock: login respond error_msg:'+lg.error_msg)
        return None

    # 获取银行间同业拆放利率
    rs = bs.query_shibor_data(start_date=start,end_date=end)
    if not (rs.error_code=='0'):
        print('  Baostock: query_shibor_data error_code:'+rs.error_code)
        print('  Baostock: query_shibor_data respond  error_msg:'+rs.error_msg)
        return None

    # 登出系统：不显示信息
    with HiddenPrints():
        lo=bs.logout()
    
    #提取数据，生成pandas格式
    rs_data=rs.data
    data_list = []
    for l in rs_data:
        data_list.append(l)

    rs_fields=rs.fields
    result = pd.DataFrame(data_list, columns=rs.fields)
    
    result['Date']=pd.to_datetime(result['date'])
    result.set_index(['Date'],inplace=True)
    
    result['rate']=round(result['shibor'+rate_period].astype('float')/100,5)
    result['period']=rate_period
    result1=result[['date','rate','period']]
    
    return result1
    
if __name__=='__main__': 
    get_shibor_rates_bs('2021-10-1','2021-11-28')   
    
#=============================================================================
if __name__=='__main__': 
    date='2023-12-15'
    rate_period='3M'
    rate_period='1Y'
    daysahead=360
    

def shibor_rate(date,rate_period='3M',daysahead=365*2):
    """
    获取指定日期和期限的shibor利率
    若无最新利率，则取最近日期的利率替代
    
    注意：这里得到的是年化利率，不带百分号，不是日利率！（日利率=年化利率/365）
    """    
    
    #检查日期有效性
    import datetime; todaydt = datetime.date.today().strftime('%Y-%m-%d')
    try:
        valid_date=check_date(date)
    except:
        date=todaydt
    if not valid_date:
        date=todaydt
        """
        print("  #Error(shibor_rate): invalid date",date)
        return None
        """
    start=date_adjust(date, adjust=-daysahead)
    
    rate_period=rate_period.upper()
    
    #检查利率期间有效性
    if not (rate_period in shibor_period_list):
        print("  #Error(shibor_rate): invalid shibor rate period",rate_period)
        print("  Supported shibor rate periods:",shibor_period_list)
        return None
    
    df=get_shibor_rates_bs(start,date,rate_period) 
    if df is None:
        rate=0
        return rate
    else:
        rate=float(df[-1:]['rate'].values[0])
    
    return rate
    
if __name__=='__main__': 
    shibor_rate('2021-11-19',rate_period='3M')
    shibor_rate('2021-11-19',rate_period='ON')
#==============================================================================        
if __name__=='__main__':
    start='2023-11-1'
    end='2024-10-30'
    term='1Y'

    treasury_yields_china(start,end,term='1Y')
    
def treasury_yields_china(start,end='today',term='1Y'):
    """
    功能：抓取指定期间和期限的国债收益率
    
    注意：这里得到的是年化利率，不带百分号，不是日利率！（日利率=年化利率/365）
    """
    start,end=start_end_preprocess(start,end)
    
    #检查日期期间
    valid,start1,end1=check_period(start,end)
    if not valid:
        print("  #Warning(treasury_yields_china): invalid date period from",start,"to",end)
        return None
    
    #检查利率期间有效性
    term_list=['3M','6M','1Y','3Y','5Y','7Y','10Y','30Y']
    if not (term in term_list):
        print("  #Warning(treasury_yields_china): invalid rate period",term)
        print("  Supported rate periods:",term_list)
        return None
    
    #抓取中债国债收益率
    import akshare as ak
    start2=start1.strftime("%Y%m%d")
    end2=end1.strftime("%Y%m%d")
    df = ak.bond_china_yield(start_date=start2,end_date=end2)
    if len(df)==0:
        print("  #Warning(treasury_yields_china): empty data found, try again later")
        return None
    
    df1=df[df['曲线名称']=='中债国债收益率曲线']
    df1.columns=['curve','date']+term_list
    df1.sort_values(by=['date'],ascending=True,inplace=True)
    
    df1['Date']=pd.to_datetime(df1['date'])
    df1.set_index(['Date'],inplace=True)    
    
    df1['rate']=df1[term]/100
    df1['period']=term
    df2=df1[['date','rate','period']]
    
    
    return df2

if __name__=='__main__':
    treasury_yields_china('2021-11-1','2021-11-28',term='1Y')
    
    
if __name__=='__main__':
    today='2023-3-4'
    term='1Y'
    daysahead=360
    
def treasury_yield_china(today,term='1Y',daysahead=360):
    """
    功能：抓取指定日期和期限的国债收益率
    
    注意：这里得到的是年化利率，不带百分号，不是日利率！（日利率=年化利率/365）
    """
    #检查日期
    valid=check_date(today)
    if not valid:
        print("  #Error(treasury_yield_china): invalid date",today)
        return None
    start = date_adjust(today, adjust=-daysahead)

    #检查利率期间有效性
    term_list=['3M','6M','1Y','3Y','5Y','7Y','10Y','30Y']
    if not (term in term_list):
        print("  #Error(treasury_yield_china): invalid rate period",term)
        print("  Supported rate periods:",term_list)
        return None
    
    rates=treasury_yields_china(start,today,term=term)
    rate=rates[-1:]['rate'].values[0]
        
    return rate
        
if __name__=='__main__':
    treasury_yield_china('2021-11-20',term='1Y')  
    treasury_yield_china('2021-11-18')
#==============================================================================
if __name__=='__main__':
    start='2019-1-1'
    end='2020-12-31'
    rate_period='1Y'
    rate_type='treasury'
    
def rf_daily_china(start,end,rate_period='1Y',rate_type='shibor'):
    """
    功能：抓取指定期间和期限的无风险利率
    
    注意：这里得到的是日利率，不带百分号，不是年化利率！（日利率=年化利率/365）
    """
    rate_type1=rate_type.upper()
    gotit=True
    
    if rate_type1=="TREASURY":
        if rate_period in ['3M','6M','1Y']:
            #使用国债收益率
            df=treasury_yields_china(start,end,rate_period)
        else:
            #使用shibor收益率
            df=get_shibor_rates_bs(start,end,rate_period)
    elif rate_type1=="SHIBOR":
        #使用shibor收益率
        df=get_shibor_rates_bs(start,end,rate_period)
        
        if df is None:
            #未能获取数据，Baostock获取的shibor利率一般滞后一个月左右
            gotit=False
        elif len(df)==0:
            gotit=False
        
        if not gotit:
            start1=date_adjust(start,adjust=-60)
            df=get_shibor_rates_bs(start1,end,rate_period)
    else:
        print("  #Warning(rf_daily_china): invalid rf rate type",rate_type)
        print("  Only support 2 types of rf: shibor rate, treasury yield")
        return None
    
    if df is None:
        gotit=False
    elif len(df)==0:
        gotit=False
    
    if not gotit:
        print("  #Warning(rf_daily_china): no rf data available between",start,end)
        return None
    
    #使用最近日期的利率填补空缺的日期
    latest_date=df['date'][-1:].values[0]
    lastest_rate=df['rate'][-1:].values[0]
    period=df['period'][-1:].values[0]

    collist=list(df)
    df_temp = pd.DataFrame(columns=collist)
    end_dt=pd.to_datetime(end)
    for i in range(100):
        date1=date_adjust(latest_date,adjust=i+1)
        date1_dt=pd.to_datetime(date1)
        if date1_dt <=end_dt:
            try:
                df_temp=df_temp.append({'date':date1,'rate':lastest_rate,'period':period},ignore_index=True)
            except:
                df_temp=df_temp._append({'date':date1,'rate':lastest_rate,'period':period},ignore_index=True)
        else:
            break
    
    df_temp['Date']=pd.to_datetime(df_temp['date'])
    df_temp.set_index(['Date'],inplace=True)    

    try:
        df1=df.append(df_temp)
    except:
        df1=df._append(df_temp)
    df1.sort_values(by=['date'],ascending=[True],inplace=True)
    
    df1['rf_daily']=df1['rate']/365
    
    return df1
    
if __name__=='__main__':
    rfd=rf_daily_china('2021-10-1','2021-11-28',rate_period='1Y',rate_type='shibor')
    rfd=rf_daily_china('2021-11-1','2021-11-28',rate_period='3M',rate_type='shibor')
    rfd=rf_daily_china('2021-11-1','2021-11-28',rate_period='1Y',rate_type='treasury')
    
#==============================================================================
if __name__=='__main__':
    current=0
    total=9
    steps=5
    leading_blanks=2

def print_progress_percent(current,total,steps=5,leading_blanks=2):
    """
    功能：打印进度百分比
    current：当前完成个数
    total：总个数
    steps：分成几个进度点显示
    leading_blanks：前置空格数
    
    注意：此函数起点计数应为0，放在循环体尾部。
    """
    
    #间隔区间，最小为1
    fraction=int(total/steps)
    if fraction ==0:
        fraction=1
    
    if total < steps:
        steps=total
    
    #生成进度个数点位
    point_list=[]
    pct_list=[]
    for s in range(steps):
        #print("step=",s+1)
        point_list=point_list+[fraction*(s+1)-1]
        pct_list=pct_list+[str(int(100/steps*(s+1)))+'%']
    
    #当前完成第一个数时显示，其他时候不显示
    if current == 0: #range函数产生的第一个数是0
        print(' '*(leading_blanks - 1),"Progress...",end=' ')
    
    #打印当前进度百分比：到达点位时打印，否则无显示
    for p in point_list:
        if current == p:
            pos=point_list.index(p)
            pct=pct_list[pos]
            
            if pct=="100%":
                #print("100% completing")
                print("100%, finalizing ...")
            else:
                print(pct,end=' ')
    
    return

if __name__=='__main__':
    for i in range(total): print_progress_percent(i,total,steps=5,leading_blanks=4)
    for i in range(total): print_progress_percent(i,total,steps=10,leading_blanks=4)

#==============================================================================
if __name__=='__main__':
    current='1'
    total_list=[str(x) for x in range(1000)]
    steps=5
    leading_blanks=4

def print_progress_percent2(current,total_list,steps=5,leading_blanks=4):
    """
    功能：打印进度百分比，注意需要放在循环体的开始处，不能放在循环体的末尾！
    current：当前完成
    total：需要完成的列表
    steps：分成几个进度点显示
    leading_blanks：前置空格数
    """
    
    #间隔区间
    fraction=int(len(total_list)/steps)
    
    #生成进度个数点位
    point_list=[]
    pct_list=[]
    for s in range(steps):
        #print("step=",s+1)
        point_list=point_list+[fraction*(s+1)-1]
        pct_list=pct_list+[str(int(100/steps*(s+1)))+'%']
    
    #当前完成第一个数时显示，其他时候不显示
    pos=total_list.index(current)
    if pos == 0: #range函数产生的第一个数是0
        print(' '*(leading_blanks - 1),"Progress...",end=' ')
    
    #打印当前进度百分比：到达点位时打印，否则无显示
    for p in point_list:
        if pos == p:
            pos=point_list.index(p)
            pct=pct_list[pos]
            
            if pct=="100%":
                print("100%, finalizing ...")
            else:
                print(pct,end=' ')
    
    return

if __name__=='__main__':
    for i in total_list: print_progress_percent2(i,total_list,steps=5,leading_blanks=4)
    for i in total_list: print_progress_percent2(i,total_list,steps=10,leading_blanks=4)

#==============================================================================
#==============================================================================
if __name__ == '__main__':
    numberPerLine=5
    leadingBlanks=2
    aList=['1', '2', '3', '4', '5', \
           '6', '7', '8', '9', '10', \
           '11', '12', '13', '14', '15', \
           '16', '17', '18', '19', '20', \
           '21', '22', '23', '24', '25', \
           '26', '27', '28']

def printInLine(aList,numberPerLine=5,leadingBlanks=2):
    """
    功能：将一个长列表等行分组打印
    """
    
    #分组
    groupedList=[]
    tmpList=[]
    n=0
    for a in aList:
        n=n+1
        if n <= numberPerLine:
            tmpList=tmpList+[a]
        else:
            groupedList=groupedList+[tmpList]
            n=1
            tmpList=[a]

    if len(tmpList) > 0:
        groupedList=groupedList+[tmpList]

    #按组打印
    for g in groupedList:
        if leadingBlanks >=1:
            print(' '*(leadingBlanks-1),*g,sep=' ')
        
    return
#==============================================================================
if __name__ == '__main__':
    numberPerLine=5
    leadingBlanks=2
    aList=['1', '2', '3', '4', '5', \
           '6', '7', '8', '9', '10', \
           '11', '12', '13', '14', '15', \
           '16', '17', '18', '19', '20', \
           '21', '22', '23', '24', '25', \
           '26', '27', '28']
    printInLine_md(aList,numberPerLine=8,colalign='center')

def printInLine_md(aList,numberPerLine=5,colalign='left',font_size='16px'):
    """
    功能：将一个长列表等行分组打印，使用df.to_markdown方式打印，实现自动对齐
    aList：用于打印的数据列表
    numberPerLine：每行打印个数，默认5
    colalign：每个打印元素的对齐方式，默认左对齐'left'，居中'center'，右对齐'right'
    """
    
    #分组
    groupedList=[]
    tmpList=[]
    n=0
    for a in aList:
        n=n+1
        if n <= numberPerLine:
            tmpList=tmpList+[a]
        else:
            groupedList=groupedList+[tmpList]
            n=1
            tmpList=[a]

    if len(tmpList) > 0:
        groupedList=groupedList+[tmpList]
        
    #装入df
    #cols=[' ']*numberPerLine
    cols=[i+1 for i in range(numberPerLine)]
    
    import pandas as pd
    df=pd.DataFrame(groupedList,columns=cols)
    
    """
    alignlist=[colalign]*numberPerLine
    print(df.to_markdown(index=False,tablefmt='plain',colalign=alignlist))
    """
    
    #确定表格字体大小
    titile_font_size=font_size
    heading_font_size=data_font_size=str(int(font_size.replace('px',''))-1)+'px'
    
    df_display_CSS(df,titletxt='',footnote='',facecolor='papayawhip',decimals=2, \
                       first_col_align='left',second_col_align='left', \
                       last_col_align='left',other_col_align='left', \
                       titile_font_size=titile_font_size,heading_font_size=heading_font_size, \
                       data_font_size=data_font_size)
    
    return

#==============================================================================
def df_corr(df,fontsize=20):
    """
    功能：绘制df各个字段之间的Pearson相关系数的热力图
    """

    # 计算相关矩阵
    correlation_matrix = df.corr()
    
    # 导入seaborn
    import seaborn as sns
    # 创建热图
    sns.heatmap(correlation_matrix,annot=True,cmap="YlGnBu",linewidths=3,
            annot_kws={"size":fontsize})
    plt.title("皮尔逊相关系数示意图",fontsize=18)
    plt.ylabel("")
    
    footnote1=""
    import datetime as dt; stoday=dt.date.today()    
    footnote2="统计日期："+str(stoday)
    #plt.xlabel(footnote1+footnote2)
    #plt.xticks(rotation=30); plt.yticks(rotation=0) 
    
    plt.gca().set_facecolor('whitesmoke')
    plt.show()

    return    

if __name__=='__main__':
    Market={'Market':('US','^GSPC','我的组合001')}
#==============================================================================
#==============================================================================
def pandas2prettytable(df,titletxt,firstColSpecial=True,leftColAlign='l',otherColAlign='c',tabborder=False):
    """
    功能：将一个df转换为prettytable格式，打印，在Jupyter Notebook下整齐
    通用，但引入表格的字段不包括索引字段，利用prettytable插件
    注意：py文件最开始处要加上下面的语句
            from __future__ import unicode_literals
    """ 
    #列名列表
    col=list(df)
    
    # 第一列长度取齐处理
    if firstColSpecial:
        #第一列的最长长度
        firstcol=list(df[col[0]])
        maxlen=0
        for f in firstcol:
            flen=hzlen(f.strip())
            if flen > maxlen:
                maxlen=flen
        
        #将第一列内容的长度取齐
        df[col[0]]=df[col[0]].apply(lambda x:equalwidth(x.strip(),maxlen=maxlen,extchar=' ',endchar=' '))    
    
    itemlist=list(df)
    item1=itemlist[0]
    items_rest=itemlist[1:]
    
    from prettytable import PrettyTable
    import sys
    # 传入的字段名相当于表头
    tb = PrettyTable(itemlist, encoding=sys.stdout.encoding) 
    
    for i in range(0,len(df)): 
        tb.add_row(list(df.iloc[i]))
    
    # 第一个字段靠左
    tb.align[item1]=leftColAlign
    # 其余字段靠右
    for i in items_rest:
        tb.align[i]=otherColAlign
    
    # 边框设置：使用dir(tb)查看属性
    if not tabborder:
        # 无边框
        #tb.set_style(pt.PLAIN_COLUMNS) 
        # 空一行，分离标题行与表体
        #print()
        tb.junction_char=' '
        tb.horizontal_char=' '
        tb.vertical_char=' '
    
    # 设置标题
    tb.title=titletxt
        
    # 若有多个表格接连打印，可能发生串行。这时，第一个表格使用end=''，后面的不用即可
    print(tb)
    
    return

#==============================================================================
if __name__=='__main__':
    mstring="123王德宏456测试"
    mstring2number(mstring,numberType='int')
    mstring2number(mstring,numberType='float')

def mstring2number(mstring,numberType='int'):
    """
    功能：将含有非数字字符的数值字符串强行转化为数字
    numberType：输出类型，默认转换为整数类型int，亦可指定转换为浮点数类型float
    """
    digitlist=['0','1','2','3','4','5','6','7','8','9','.','-','+']
    for c in mstring:
        if not (c in digitlist):
            mstring=mstring.replace(c,'')
    
    if numberType == 'int':
        value=int(mstring)
    else:
        value=float(mstring)
        
    return value

#==============================================================================
if __name__=='__main__':
    time_priority_weighted_average(df,'蔚来汽车',decimals=4)

def time_priority_weighted_average(df,colname,decimals=4):
    """
    功能：对df中的colname列进行时间优先加权平均
    算法：将df索引列的datetime转换为8位数字，然后将每列的8位数字减去初始行的8位数字
    将其差作为权重
    """
    df['time_weight']=df.index.asi8
    df0=df.head(1)
    initial_weight=df0['time_weight'][0]
    df['relative_weight']=df['time_weight']-initial_weight
    
    # 双倍近期优先
    df['relative_weight2']=df['relative_weight'].apply(lambda x: x*2)
    
    import numpy as np
    try:
        tpwavg=np.average(df[colname],weights=df['relative_weight2'])
    except:
        return None
    
    return round(tpwavg,decimals)

#==============================================================================

if __name__=='__main__':
    tickers=['NIO','LI','XPEV','TSLA']
    df=compare_mrar(tickers,
                    rar_name='sharpe',
                    start='2022-1-1',end='2023-1-31',
                    market='US',market_index='^GSPC',
                    window=240,axhline_label='零线')    
    titletxt="This is the title text"
    footnote="This is the footnote"

def descriptive_statistics(df,titletxt,footnote,decimals=4,sortby='tpw_mean', \
                           recommend_only=False,trailing=7,trend_threshhold=0.01, \
                           facecolor='papayawhip',font_size='16px'):
    """
    功能：进行描述性统计，并打印结果
    df的要求：
    索引列为datetime格式，不带时区
    各个列为比较对象，均为数值型，降序排列
    
    sortby='tpw_mean'：按照近期时间优先加权(time priority weighted)平均数排序
    recommend_only=False：是否仅打印推荐的证券
    """
    
    # 检查df
    if df is None:
        print("  #Error(descriptive_statistics): df is None")
        return
    if len(df) == 0:
        print("  #Error(descriptive_statistics): df is empty")
        return
    
    # 计算短期趋势
    #df20=df[-trailing:]
    df20=df.tail(trailing)
    """
    df20ds=df20.describe()
    df20mean=df20ds[df20ds.index=='mean'].T
    
    df20tail=df20.tail(1).T
    df20tail.columns=['last']
    
    import pandas as pd
    df20trailing=pd.merge(df20tail,df20mean,left_index=True,right_index=True)
    df20trailing['trailing']=df20trailing['last']-df20trailing['mean']
    """
    ds=df.describe(include='all',percentiles=[.5])
    dst=ds.T   
    cols=['min','max','50%','mean','std']
    #cols=['min','max','50%','mean','trailing']
    
    dst['item']=dst.index
    #dstt=pd.merge(dst,df20trailing['trailing'],left_index=True,right_index=True)
    cols2=['item','min','max','50%','mean','std']
    #cols2=['item','min','max','50%','mean','trailing']
    
    #dst2=dstt[cols2]
    dst2=dst[cols2]
    for c in cols:
        dst2[c]=dst2[c].apply(lambda x: round(x,decimals))
    
    if sortby != 'tpw_mean': 
        if sortby=='median':
            sortby='50%'
        dst2.sort_values(by=sortby,ascending=False,inplace=True)

    cols2cn=['比较对象','最小值','最大值','中位数','平均值','标准差']
    #cols2cn=['比较对象','最小值','最大值','中位数','平均值','最新均值差']
    dst2.columns=cols2cn
    
    # 近期优先加权平均
    dst2['近期优先加权平均']=dst2['比较对象'].apply(lambda x:time_priority_weighted_average(df,x,4))
    if sortby == "tpw_mean":
        dst2.sort_values(by='近期优先加权平均',ascending=False,inplace=True)
    
    # 去掉带有缺失值的行
    #dst3=dst2.dropna()
    dst3=dst2
    #dst3=dst3[not (dst3['比较对象'] in ['time_weight','relative_weight']) ]
    dst3=dst3[(dst3['比较对象'] != 'time_weight') & (dst3['比较对象'] != 'relative_weight')]
    
    dst3.reset_index(drop=True,inplace=True)
    dst3.index=dst3.index+1
    
    # 趋势标记
    #dst3['期间趋势']='➠'
    #dst3['期间趋势']='➷'
    #dst3['期间趋势']=dst3.apply(lambda x: '➹' if (x['近期优先加权平均']>x['平均值']) & (x['近期优先加权平均']>x['中位数']) else x['期间趋势'],axis=1)
    #dst3['期间趋势']=dst3.apply(lambda x: '➷' if (x['近期优先加权平均']<x['平均值']) & (x['近期优先加权平均']<x['中位数']) else x['期间趋势'],axis=1)
    #dst3['期间趋势']=dst3['比较对象'].apply(lambda x:curve_trend_regress(df,x,trend_threshhold))
    dst3['期间趋势']=dst3['比较对象'].apply(lambda x:curve_trend_direct(df,x,trend_threshhold))

    #dst3['近期趋势']='➠'
    #dst3['近期趋势']='➷'
    #dst3['近期趋势']=dst3.apply(lambda x: '➹' if x['最新均值差'] > 0.0 else x['近期趋势'],axis=1)
    #dst3['期间趋势']=dst3.apply(lambda x: '➷' if x['最新均值差'] < 0.0 else x['近期趋势'],axis=1)
    #dst3['近期趋势']=dst3['比较对象'].apply(lambda x:curve_trend_direct(df20,x,trend_threshhold))
    #dst3['近期趋势']=dst3['比较对象'].apply(lambda x:curve_trend_regress(df20,x,trend_threshhold))
    dst3['近期趋势']=dst3['比较对象'].apply(lambda x:curve_trend_direct(df20,x,trend_threshhold))
    
    # 推荐标记
    dst3['推荐标记']=''
    """
    if sortby in ['tpw_mean','trailing']: #稳健推荐
        dst3['推荐标记']=dst3.apply(lambda x: '✮' if (x['近期优先加权平均']>0) else x['推荐标记'],axis=1)
        
        dst3['推荐标记']=dst3.apply(lambda x: '✮✮' if (x['中位数']>0) & (x['平均值']>0) & (x['近期优先加权平均']>0) else x['推荐标记'],axis=1)   
        
        maxvalue=dst3['近期优先加权平均'].max()
        dst3['推荐标记']=dst3.apply(lambda x: '✮✮✮' if (x['近期优先加权平均']==maxvalue) & (x['推荐标记']=='✮✮') else x['推荐标记'],axis=1)
        
    elif sortby == 'min': #保守推荐
        dst3['推荐标记']=dst3.apply(lambda x: '✮' if (x['近期优先加权平均']>0) else x['推荐标记'],axis=1)
        
        dst3['推荐标记']=dst3.apply(lambda x: '✮✮' if (x['最小值']>0) else x['推荐标记'],axis=1)   
        
        maxvalue=dst3['最小值'].max()
        dst3['推荐标记']=dst3.apply(lambda x: '✮✮✮' if (x['最小值']==maxvalue) & (x['推荐标记']=='✮✮') else x['推荐标记'],axis=1)
        
    elif sortby == 'mean': #进取推荐，均值
        dst3['推荐标记']=dst3.apply(lambda x: '✮' if (x['平均值']>0) else x['推荐标记'],axis=1)
        
        dst3['推荐标记']=dst3.apply(lambda x: '✮✮' if (x['中位数']>0) & (x['推荐标记']=='✮') else x['推荐标记'],axis=1)   
        
        maxvalue=dst3['平均值'].max()
        dst3['推荐标记']=dst3.apply(lambda x: '✮✮✮' if (x['平均值']==maxvalue) & (x['推荐标记']=='✮✮') else x['推荐标记'],axis=1)
        
    elif sortby == 'median': #进取推荐，中位数
        dst3['推荐标记']=dst3.apply(lambda x: '✮' if (x['中位数']>0) else x['推荐标记'],axis=1)
        
        dst3['推荐标记']=dst3.apply(lambda x: '✮✮' if (x['平均值']>0) & (x['推荐标记']=='✮') else x['推荐标记'],axis=1)   
        
        maxvalue=dst3['中位数'].max()
        dst3['推荐标记']=dst3.apply(lambda x: '✮✮✮' if (x['中位数']==maxvalue) & (x['推荐标记']=='✮✮') else x['推荐标记'],axis=1)   
    else:
        pass
    """
    if sortby in ['tpw_mean','trailing']: #稳健推荐
        dst3['推荐标记']=dst3.apply(lambda x: change_recommend_stars(x['推荐标记'],'+') if (x['近期优先加权平均']>0) else x['推荐标记'],axis=1)
        
        dst3['推荐标记']=dst3.apply(lambda x: change_recommend_stars(x['推荐标记'],'+') if (x['中位数']>0) & (x['平均值']>0) & (x['中位数']>x['平均值']) else x['推荐标记'],axis=1)  
        
        dst3['推荐标记']=dst3.apply(lambda x: change_recommend_stars(x['推荐标记'],'+') if (x['中位数']>0) & (x['平均值']>0) & (x['近期优先加权平均']>max(x['中位数'],x['平均值'])) else x['推荐标记'],axis=1)
        """
        maxvalue=dst3['近期优先加权平均'].max()
        dst3['推荐标记']=dst3.apply(lambda x: change_recommend_stars(x['推荐标记'],'+') if (x['近期优先加权平均']==maxvalue) else x['推荐标记'],axis=1)
        """
    elif sortby == 'min': #保守推荐
        dst3['推荐标记']=dst3.apply(lambda x: '✮' if (x['近期优先加权平均']>0) else x['推荐标记'],axis=1)
        
        dst3['推荐标记']=dst3.apply(lambda x: '✮✮' if (x['最小值']>0) else x['推荐标记'],axis=1)   
        
        maxvalue=dst3['最小值'].max()
        dst3['推荐标记']=dst3.apply(lambda x: '✮✮✮' if (x['最小值']==maxvalue) & (x['推荐标记']=='✮✮') else x['推荐标记'],axis=1)
        
    elif sortby == 'mean': #进取推荐，均值
        dst3['推荐标记']=dst3.apply(lambda x: '✮' if (x['平均值']>0) else x['推荐标记'],axis=1)
        
        dst3['推荐标记']=dst3.apply(lambda x: '✮✮' if (x['中位数']>0) & (x['推荐标记']=='✮') else x['推荐标记'],axis=1)   
        
        maxvalue=dst3['平均值'].max()
        dst3['推荐标记']=dst3.apply(lambda x: '✮✮✮' if (x['平均值']==maxvalue) & (x['推荐标记']=='✮✮') else x['推荐标记'],axis=1)
        
    elif sortby == 'median': #进取推荐，中位数
        dst3['推荐标记']=dst3.apply(lambda x: '✮' if (x['中位数']>0) else x['推荐标记'],axis=1)
        
        dst3['推荐标记']=dst3.apply(lambda x: '✮✮' if (x['平均值']>0) & (x['推荐标记']=='✮') else x['推荐标记'],axis=1)   
        
        maxvalue=dst3['中位数'].max()
        dst3['推荐标记']=dst3.apply(lambda x: '✮✮✮' if (x['中位数']==maxvalue) & (x['推荐标记']=='✮✮') else x['推荐标记'],axis=1)   
    else:
        pass
    
    
    # 下降趋势时，星星个数降一级，执行顺序不可颠倒
    dst4=dst3
    
    # 减少星星的情形
    #droplist1=['➷','➠']
    droplist1=['➷']
    droplist2=['➷']
    dst4['推荐标记']=dst4.apply(lambda x: change_recommend_stars(x['推荐标记'],'-') if (x['期间趋势'] in droplist1) else x['推荐标记'],axis=1)
    dst4['推荐标记']=dst4.apply(lambda x: change_recommend_stars(x['推荐标记'],'-') if (x['近期趋势'] in droplist2) else x['推荐标记'],axis=1)
    """
    # 一颗星颗星-->无星
    dst4['推荐标记']=dst4.apply(lambda x: '' if (x['推荐标记']=='✮') & (x['期间趋势'] in droplist) else x['推荐标记'],axis=1) 
    dst4['推荐标记']=dst4.apply(lambda x: '' if (x['推荐标记']=='✮') & (x['近期趋势'] in droplist) else x['推荐标记'],axis=1)   
    
    
    # 两颗星颗星-->一颗星
    dst4['推荐标记']=dst4.apply(lambda x: '✮' if (x['推荐标记']=='✮✮') & (x['期间趋势'] in droplist) else x['推荐标记'],axis=1)
    dst4['推荐标记']=dst4.apply(lambda x: '✮' if (x['推荐标记']=='✮✮') & (x['近期趋势'] in droplist) else x['推荐标记'],axis=1)   
    
    # 三颗星-->两颗星✮
    #dst4['推荐标记']=dst4.apply(lambda x: '✮✮✩' if (x['推荐标记']=='✮✮✮') & (x['趋势']=='➷') else x['推荐标记'],axis=1)
    dst4['推荐标记']=dst4.apply(lambda x: '✮✮' if (x['推荐标记']=='✮✮✮') & (x['期间趋势'] in droplist) else x['推荐标记'],axis=1)
    dst4['推荐标记']=dst4.apply(lambda x: '✮✮' if (x['推荐标记']=='✮✮✮') & (x['近期趋势'] in droplist) else x['推荐标记'],axis=1)
    """
    
    # 上升趋势时，星星个数加一级，执行顺序不可颠倒
    dst4['推荐标记']=dst4.apply(lambda x: change_recommend_stars(x['推荐标记'],'+') if (x['期间趋势']=='➹') & (x['近期趋势']=='➹') else x['推荐标记'],axis=1)
    
    """
    # 两颗星颗星-->三颗星
    dst4['推荐标记']=dst4.apply(lambda x: '✮✮✮' if (x['推荐标记']=='✮✮') & (x['期间趋势']=='➹') else x['推荐标记'],axis=1) 
    dst4['推荐标记']=dst4.apply(lambda x: '✮✮✮' if (x['推荐标记']=='✮✮') & (x['近期趋势']=='➹') else x['推荐标记'],axis=1)   
    
    # 一颗星颗星-->两颗星
    dst4['推荐标记']=dst4.apply(lambda x: '✮✮' if (x['推荐标记']=='✮') & (x['期间趋势']=='➹') else x['推荐标记'],axis=1) 
    dst4['推荐标记']=dst4.apply(lambda x: '✮✮' if (x['推荐标记']=='✮') & (x['近期趋势']=='➹') else x['推荐标记'],axis=1)   
    
    # 零颗星-->一颗星
    dst4['推荐标记']=dst4.apply(lambda x: '✮' if (x['推荐标记']=='') & (x['期间趋势']=='➹') & (x['近期趋势']=='➹') else x['推荐标记'],axis=1) 
    dst4['推荐标记']=dst4.apply(lambda x: '✮' if (x['推荐标记']=='') & (x['期间趋势']=='➹') else x['推荐标记'],axis=1) 
    dst4['推荐标记']=dst4.apply(lambda x: '✮' if (x['推荐标记']=='') & (x['近期趋势']=='➹') else x['推荐标记'],axis=1)  
    """
    
    # 重排序：按照星星个数+数值，降序
    dst5=dst4
    if sortby == "tpw_mean":
        dst5.sort_values(by=['推荐标记','近期优先加权平均'],ascending=[False,False],inplace=True)
        #dst5.sort_values(by=['推荐标记','近期优先加权平均'],ascending=False,inplace=True)
    elif sortby == "min":
        dst5.sort_values(by=['推荐标记','最小值'],ascending=[False,False],inplace=True)
    elif sortby == "mean":
        dst5.sort_values(by=['推荐标记','平均值'],ascending=[False,False],inplace=True)
    elif sortby == "median":
        dst5.sort_values(by=['推荐标记','中位数'],ascending=[False,False],inplace=True)
    elif sortby == "trailing":
        dst5.sort_values(by=['推荐标记','最新均值差'],ascending=[False,False],inplace=True)
    else:
        pass
    
    #是否过滤无推荐标志的证券，防止过多无推荐标志的记录使得打印列表过长
    if recommend_only:
        dst6=dst5[dst5['推荐标记'] != '']
        dst_num=len(dst6)
        #若无推荐标志也要显示头十个
        if dst_num < 10:
            dst6=dst5.head(10)
        else:
            dst6=dst5.head(dst_num+3)
    else:
        dst6=dst5
    
    dst6.reset_index(drop=True,inplace=True)
    dst6.index=dst6.index+1
    
    """
    print("\n"+titletxt+"\n")
    #alignlist=['right','left']+['center']*(len(list(dst4))-1)
    alignlist=['right','left']+['center']*(len(list(dst6))-3)+['center','left']
    try:   
        print(dst6.to_markdown(index=True,tablefmt='plain',colalign=alignlist))
    except:
        #解决汉字编码gbk出错问题
        dst7=dst6.to_markdown(index=True,tablefmt='plain',colalign=alignlist)
        dst8=dst7.encode("utf-8",errors="strict")
        print(dst8)
    print("\n"+footnote)
    """
    
    #确定表格字体大小
    titile_font_size=font_size
    heading_font_size=data_font_size=str(int(font_size.replace('px',''))-1)+'px'
    
    df_display_CSS(dst6,titletxt=titletxt,footnote=footnote,facecolor=facecolor, \
                   titile_font_size=titile_font_size,heading_font_size=heading_font_size, \
                       data_font_size=data_font_size)
    
    return dst5

#==============================================================================

if __name__=='__main__':
    tickers=['NIO','LI','XPEV','TSLA']
    df=compare_mrar(tickers,
                    rar_name='sharpe',
                    start='2022-1-1',end='2023-1-31',
                    market='US',market_index='^GSPC',
                    window=240,axhline_label='零线')   
    
    titletxt="This is the title text"
    footnote="This is the footnote"
    decimals=4
    sortby='tpw_mean'
    recommend_only=False
    trailing=7
    trend_threshhold=0.01

def descriptive_statistics2(df,titletxt,footnote,decimals=4,sortby='tpw_mean', \
                           recommend_only=False,trailing=7,trend_threshhold=0.01, \
                           printout=True,style_print=True, \
                           facecolor='whitesmoke',font_size='16px'):
    """
    功能：进行描述性统计，并打印结果
    df的要求：
    索引列为datetime格式，不带时区
    各个列为比较对象，均为数值型，降序排列
    
    sortby='tpw_mean'：按照近期时间优先加权(time priority weighted)平均数排序
    recommend_only=False：是否仅打印推荐的证券
    """
    
    # 检查df
    if df is None:
        print("  #Error(descriptive_statistics2): none info found")
        return
    if len(df) == 0:
        print("  #Error(descriptive_statistics2): zero data found")
        return
    
    #为避免nan的影响，对nan进行填充
    df.fillna(method='bfill',inplace=True)
    df.fillna(method='ffill',inplace=True)
    
    #转换字符为数值
    import pandas as pd
    for c in list(df):
        try:
            df[c] = pd.to_numeric(df[c], errors='coerce')
        except:
            continue
    
    dfn=df.select_dtypes(include='number')
    if dfn.empty:
        print("  #Error(descriptive_statistics2): no numeric columns found to describe")
        return
    
    # 计算短期趋势
    df20=df.tail(trailing)

    ds=df.describe(include='number',percentiles=[.5])
    dst=ds.T   
    cols=['min','max','50%','mean','std']
    
    dst['item']=dst.index
    cols2=['item','min','max','50%','mean','std']
    
    dst2=dst[cols2]
    for c in cols:
        dst2[c]=dst2[c].apply(lambda x: round(x,decimals))
    
    if sortby != 'tpw_mean': 
        if sortby=='median':
            sortby='50%'
        dst2.sort_values(by=sortby,ascending=False,inplace=True)

    cols2cn=['比较对象','最小值','最大值','中位数','平均值','标准差']
    dst2.columns=cols2cn
    
    # 近期优先加权平均
    dst2['近期优先加权平均']=dst2['比较对象'].apply(lambda x:time_priority_weighted_average(df,x,4))
    if sortby == "tpw_mean":
        dst2.sort_values(by='近期优先加权平均',ascending=False,inplace=True)
    
    dst3=dst2
    dst3=dst3[(dst3['比较对象'] != 'time_weight') & (dst3['比较对象'] != 'relative_weight')]
    
    dst3.reset_index(drop=True,inplace=True)
    dst3.index=dst3.index+1
    
    # 趋势标记
    dst3['期间趋势']=dst3['比较对象'].apply(lambda x:curve_trend_direct(df,x,trend_threshhold))
    dst3['近期趋势']=dst3['比较对象'].apply(lambda x:curve_trend_direct(df20,x,trend_threshhold))
    
    # 推荐标记：最大五颗星
    dst3['推荐标记']=''
    if sortby in ['tpw_mean','trailing']: #重视近期趋势
        #注意：务必先加后减！
        #若近期优先加权平均>0，给3星
        dst3['推荐标记']=dst3.apply(lambda x: change_stars2(x['推荐标记'],'+++') if (x['近期优先加权平均']>0) else x['推荐标记'],axis=1)
        #若近期趋势➹，加2星
        dst3['推荐标记']=dst3.apply(lambda x: change_stars2(x['推荐标记'],'++') if (x['近期趋势']=='➹') else x['推荐标记'],axis=1)  
        #若期间趋势➹，加1星        
        dst3['推荐标记']=dst3.apply(lambda x: change_stars2(x['推荐标记'],'+') if (x['期间趋势']=='➹') else x['推荐标记'],axis=1) 
        #若平均值或中位数>0，加1星
        dst3['推荐标记']=dst3.apply(lambda x: change_stars2(x['推荐标记'],'+') if (x['平均值']>0) | (x['中位数']>0) else x['推荐标记'],axis=1)
        #若最小值>0，加1星        
        dst3['推荐标记']=dst3.apply(lambda x: change_stars2(x['推荐标记'],'+') if (x['最小值']>0) else x['推荐标记'],axis=1)  

        #若近期趋势➷，减2星
        dst3['推荐标记']=dst3.apply(lambda x: change_stars2(x['推荐标记'],'-') if (x['近期趋势']=='➷') else x['推荐标记'],axis=1)         
        #若期间趋势➷，减1星        
        dst3['推荐标记']=dst3.apply(lambda x: change_stars2(x['推荐标记'],'-') if (x['期间趋势']=='➷') else x['推荐标记'],axis=1)         
        #若平均值且中位数<0，减1星
        dst3['推荐标记']=dst3.apply(lambda x: change_stars2(x['推荐标记'],'-') if (x['平均值']<0) & (x['中位数']<0) else x['推荐标记'],axis=1)
        #若最小值<0，减1星        
        dst3['推荐标记']=dst3.apply(lambda x: change_stars2(x['推荐标记'],'-') if (x['最小值']<0) else x['推荐标记'],axis=1)  
        
        #若近期优先加权平均<0，星星清零
        dst3['推荐标记']=dst3.apply(lambda x: '' if (x['近期优先加权平均']<0) else x['推荐标记'],axis=1)
        
    elif sortby == 'min': #保守推荐
        #若最小值>0，加5星
        dst3['推荐标记']=dst3.apply(lambda x: change_stars2(x['推荐标记'],'+++++') if (x['最小值']>0) else x['推荐标记'],axis=1)
        #若近期优先加权平均>0，加1星
        dst3['推荐标记']=dst3.apply(lambda x: change_stars2(x['推荐标记'],'+') if (x['近期优先加权平均']>0) else x['推荐标记'],axis=1)
        #若近期趋势➹，加1星
        dst3['推荐标记']=dst3.apply(lambda x: change_stars2(x['推荐标记'],'+') if (x['近期趋势']=='➹') else x['推荐标记'],axis=1)  
        #若期间趋势➹，加1星        
        dst3['推荐标记']=dst3.apply(lambda x: change_stars2(x['推荐标记'],'+') if (x['期间趋势']=='➹') else x['推荐标记'],axis=1) 
        #若平均值或中位数>0，加1星
        dst3['推荐标记']=dst3.apply(lambda x: change_stars2(x['推荐标记'],'+') if (x['平均值']>0) | (x['中位数']>0) else x['推荐标记'],axis=1)

        #若近期优先加权平均<0，减1星
        dst3['推荐标记']=dst3.apply(lambda x: change_stars2(x['推荐标记'],'-') if (x['近期优先加权平均']<0) else x['推荐标记'],axis=1)
        #若平均值且中位数<0，减1星
        dst3['推荐标记']=dst3.apply(lambda x: change_stars2(x['推荐标记'],'-') if (x['平均值']<0) & (x['中位数']<0) else x['推荐标记'],axis=1)
        #若近期趋势➷，减1星
        dst3['推荐标记']=dst3.apply(lambda x: change_stars2(x['推荐标记'],'-') if (x['近期趋势']=='➷') else x['推荐标记'],axis=1)  
        #若期间趋势➷，减1星        
        dst3['推荐标记']=dst3.apply(lambda x: change_stars2(x['推荐标记'],'-') if (x['期间趋势']=='➷') else x['推荐标记'],axis=1) 
        
    elif sortby == 'mean': #进取推荐，均值，重视整体趋势，不在乎近期趋势
        #若平均值>0，给3星
        dst3['推荐标记']=dst3.apply(lambda x: change_stars2(x['推荐标记'],'+++') if (x['平均值']>0) else x['推荐标记'],axis=1)
        #若期间趋势➹，加2星        
        dst3['推荐标记']=dst3.apply(lambda x: change_stars2(x['推荐标记'],'++') if (x['期间趋势']=='➹') else x['推荐标记'],axis=1) 
        #若中位数>0，加1星
        dst3['推荐标记']=dst3.apply(lambda x: change_stars2(x['推荐标记'],'+') if (x['中位数']>0) else x['推荐标记'],axis=1)
        #若近期趋势➹，加1星
        dst3['推荐标记']=dst3.apply(lambda x: change_stars2(x['推荐标记'],'+') if (x['近期趋势']=='➹') else x['推荐标记'],axis=1)  
        #若近期优先加权平均>0，加1星
        dst3['推荐标记']=dst3.apply(lambda x: change_stars2(x['推荐标记'],'+') if (x['近期优先加权平均']>0) else x['推荐标记'],axis=1)
        #若最小值>0，加1星        
        dst3['推荐标记']=dst3.apply(lambda x: change_stars2(x['推荐标记'],'+') if (x['最小值']>0) else x['推荐标记'],axis=1)    

        #若期间趋势➷，减2星        
        dst3['推荐标记']=dst3.apply(lambda x: change_stars2(x['推荐标记'],'-') if (x['期间趋势']=='➷') else x['推荐标记'],axis=1) 
        #若近期趋势➷，减1星
        dst3['推荐标记']=dst3.apply(lambda x: change_stars2(x['推荐标记'],'-') if (x['近期趋势']=='➷') else x['推荐标记'],axis=1)  
        #若近期优先加权平均<0，减1星
        dst3['推荐标记']=dst3.apply(lambda x: change_stars2(x['推荐标记'],'-') if (x['近期优先加权平均']<0) else x['推荐标记'],axis=1)
        #若中位数<0，减1星
        dst3['推荐标记']=dst3.apply(lambda x: change_stars2(x['推荐标记'],'-') if (x['中位数']<0) else x['推荐标记'],axis=1)
        #若最小值<0，减1星        
        dst3['推荐标记']=dst3.apply(lambda x: change_stars2(x['推荐标记'],'-') if (x['最小值']<0) else x['推荐标记'],axis=1)    
        
        #若平均值<0，星星清零
        dst3['推荐标记']=dst3.apply(lambda x: '' if (x['平均值']<0) else x['推荐标记'],axis=1)
        
    elif sortby == 'median': #进取推荐，中位数，看重整体趋势，不在乎近期短期变化
        #若中位数>0，给3星
        dst3['推荐标记']=dst3.apply(lambda x: change_stars2(x['推荐标记'],'+++') if (x['中位数']>0) else x['推荐标记'],axis=1)
        #若期间趋势➹，加2星        
        dst3['推荐标记']=dst3.apply(lambda x: change_stars2(x['推荐标记'],'++') if (x['期间趋势']=='➹') else x['推荐标记'],axis=1) 
        #若平均值>0，加1星
        dst3['推荐标记']=dst3.apply(lambda x: change_stars2(x['推荐标记'],'+') if (x['平均值']>0) else x['推荐标记'],axis=1)
        
        #若近期趋势➹，加1星
        dst3['推荐标记']=dst3.apply(lambda x: change_stars2(x['推荐标记'],'+') if (x['近期趋势']=='➹') else x['推荐标记'],axis=1)  
        #若近期优先加权平均>0，加1星
        dst3['推荐标记']=dst3.apply(lambda x: change_stars2(x['推荐标记'],'+') if (x['近期优先加权平均']>0) else x['推荐标记'],axis=1)
        #若最小值>0，加1星        
        dst3['推荐标记']=dst3.apply(lambda x: change_stars2(x['推荐标记'],'+') if (x['最小值']>0) else x['推荐标记'],axis=1)    

        #若期间趋势➷，减2星        
        dst3['推荐标记']=dst3.apply(lambda x: change_stars2(x['推荐标记'],'-') if (x['期间趋势']=='➷') else x['推荐标记'],axis=1) 
        #若近期趋势➷，减1星
        dst3['推荐标记']=dst3.apply(lambda x: change_stars2(x['推荐标记'],'-') if (x['近期趋势']=='➷') else x['推荐标记'],axis=1)  
        #若近期优先加权平均<0，减1星
        dst3['推荐标记']=dst3.apply(lambda x: change_stars2(x['推荐标记'],'-') if (x['近期优先加权平均']<0) else x['推荐标记'],axis=1)
        #若平均值<0，减1星
        dst3['推荐标记']=dst3.apply(lambda x: change_stars2(x['推荐标记'],'-') if (x['平均值']<0) else x['推荐标记'],axis=1)
        #若最小值<0，减1星        
        dst3['推荐标记']=dst3.apply(lambda x: change_stars2(x['推荐标记'],'-') if (x['最小值']<0) else x['推荐标记'],axis=1)    
        
        #若中位数<0，星星清零
        dst3['推荐标记']=dst3.apply(lambda x: '' if (x['中位数']<0) else x['推荐标记'],axis=1)
    else:
        pass
    
    #最多5颗星星
    dst3['推荐标记']=dst3.apply(lambda x: x['推荐标记'][:5] if (hzlen(x['推荐标记'])>5) else x['推荐标记'],axis=1)
    #为了打印对齐，强制向左移动，不管用！
    #dst3['推荐标记']=dst3.apply(lambda x: x['推荐标记']+'  ' if (hzlen(x['推荐标记'])>4) else x['推荐标记'],axis=1)
    
    dst4=dst3
    
    # 重排序：按照星星个数+数值，降序
    dst5=dst4
    if sortby == "tpw_mean":
        dst5.sort_values(by=['推荐标记','近期优先加权平均'],ascending=[False,False],inplace=True)
        #dst5.sort_values(by=['推荐标记','近期优先加权平均'],ascending=False,inplace=True)
    elif sortby == "min":
        dst5.sort_values(by=['推荐标记','最小值'],ascending=[False,False],inplace=True)
    elif sortby == "mean":
        dst5.sort_values(by=['推荐标记','平均值'],ascending=[False,False],inplace=True)
    elif sortby == "median":
        dst5.sort_values(by=['推荐标记','中位数'],ascending=[False,False],inplace=True)
    elif sortby == "trailing":
        dst5.sort_values(by=['推荐标记','最新均值差'],ascending=[False,False],inplace=True)
    else:
        pass
    
    #是否过滤无推荐标志的证券，防止过多无推荐标志的记录使得打印列表过长
    if recommend_only:
        dst6=dst5[dst5['推荐标记'] != '']
        dst_num=len(dst6)
        #若无推荐标志也要显示头十个
        if dst_num < 10:
            dst6=dst5.head(10)
        else:
            dst6=dst5.head(dst_num+3)
    else:
        dst6=dst5
    
    dst6.reset_index(drop=True,inplace=True)
    dst6.index=dst6.index+1
    
    if printout:
        #控制显示的小数点位数
        for c in dst6.columns:
            try:
                dst6[c]=dst6[c].apply(lambda x: round(x,4))
            except:
                pass
            #确保display显示时不再自动在数值尾部添加零至6位小数
            dst6[c]=dst6[c].apply(lambda x: str(x))
        """
        if not style_print: #markdown打印
            print("\n"+titletxt+"\n")
            #如果index=True则显示index，这样alignlist的长度就需要dst6列数+1
            alignlist=['right','left']+['center']*(len(list(dst6))-3)+['center','left']
            try:   
                print(dst6.to_markdown(index=True,tablefmt='plain',colalign=alignlist))
            except:
                #解决汉字编码gbk出错问题
                dst7=dst6.to_markdown(index=True,tablefmt='plain',colalign=alignlist)
                dst8=dst7.encode("utf-8",errors="strict")
                print(dst8)
            print("\n"+footnote)
            
        else: #style打印
            print("\n"+titletxt)
            dst6sd= dst6.style.set_properties(**{'text-align': 'center'})
            from IPython.display import display
            display(dst6sd)
            print(footnote+"\n")
            disph=dst6.style.hide() #不显示索引列
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
                print("  #Warning(descriptive_statistics2): color",facecolor,"is unsupported, changed to default setting")
                dispf2=dispf.set_properties(**{'background-color':'whitesmoke','color':'black'})
                
            from IPython.display import display
            display(dispf2)
            print(footnote+"\n")
        """
        #确定表格字体大小
        titile_font_size=font_size
        heading_font_size=data_font_size=str(int(font_size.replace('px',''))-1)+'px'
        
        dst6.rename(columns={"比较对象":text_lang("比较对象","Securities"), \
                             "最小值":text_lang("最小值","Min"), \
                             "最大值":text_lang("最大值","Max"), \
                             "中位数":text_lang("中位数","Median"), \
                             "平均值":text_lang("平均值","Mean"), \
                             "标准差":text_lang("标准差","Std Dev"), \
                             "近期优先加权平均":text_lang("近期优先加权平均","RWA"), \
                             "期间趋势":text_lang("期间趋势","Period Trend"), \
                             "近期趋势":text_lang("近期趋势","Recent Trend"), \
                             "推荐标记":text_lang("推荐标记","Recommend")},inplace=True)
        
        df_display_CSS(dst6,titletxt=titletxt,footnote=footnote,facecolor=facecolor, \
                       titile_font_size=titile_font_size,heading_font_size=heading_font_size, \
                           data_font_size=data_font_size)
            
    return dst5


#==============================================================================
if __name__=='__main__':
    alist=['NIO','LI','XPEV','TSLA']
    print_list(alist)

def print_list(alist,leading_blanks=1,end='\n'):
    """
    功能：打印一个字符串列表，不带引号，节省空间
    """
    print(' '*leading_blanks,end='')
    
    for i in alist:
        print(i,end=' ')
    print(end,end='')
    
    return

if __name__=='__main__':
    alist=['NIO','LI','XPEV','TSLA']
    list2str(alist)
    
def list2str(alist):
    """
    功能：将列表转换为字符串，不带引号，节省空间
    """
    if len(alist) > 1:
        result='['
        for i in alist:
            result=result+str(i)
            if i != alist[-1]:
                result=result+', '
        result=result+']'
        
    elif len(alist) == 1:
        result=str(alist[0])
        
    else:
        result=''
    
    return result

#==============================================================================
# FUNCTION TO REMOVE TIMEZONE
def remove_timezone_dt(dt):
   
    # HERE `dt` is a python datetime
    # object that used .replace() method
    return dt.replace(tzinfo=None)
#==============================================================================
def remove_df_index_timezone(df):
    df['timestamp']=df.index
    df['timestamp'] = df['timestamp'].apply(remove_timezone_dt)
    df.index=df['timestamp']
    del df['timestamp']
    
    return df
#==============================================================================
if __name__=='__main__':
    ltext='景顺长城沪深300指数增强A,景顺长城量化精选股票,景顺长城量化新动力股票,景顺长城量化平衡混合'

def print_long_text(ltext,separators=[',','，'],numberPerLine=4,colalign='left'):
    """
    功能：分行打印有规律的长字符串，每行打印numPerLine，分隔符列表为separators
    """
    # 分隔符合成
    reSeparator=''
    for s in separators:
        reSeparator=reSeparator+s+'|'
    reSLen=len(reSeparator) 
    reSeparator=reSeparator[:-1]           
    
    # 分割长字符串，形成列表
    import re
    aList=re.split(reSeparator,ltext)
    aListLen=len(aList)
    printInLine_md(aList,numberPerLine=numberPerLine,colalign=colalign)
    
    return aListLen
    
#==============================================================================
if __name__=='__main__':
    printInMarkdown(df)

def printInMarkdown(df,titletxt='',footnote='', \
                    firstAlign='center',restAlign='center'):
    """
    功能：使用markdown格式打印df
    """
    colList=list(df)
    colNum=len(colList)

    # 打印标题
    if not titletxt == '':
        print(' ')
        print(titletxt,'\n')
    else:
        print(' ')
    
    # 打印表体
    alignList=[firstAlign]+[restAlign]*(colNum-1)
    print(df.to_markdown(index=False,tablefmt='plain',colalign=alignList))
    
    # 打印尾注
    if not footnote == '':
        print('\n',footnote)
    
    return
#==============================================================================
if __name__=='__main__':
    df=security_price("600519.SS","2023-1-1","2023-6-30")
    col='Close'
    threshhold=0.1
    curve_trend_regress(df,col,threshhold=0.1)
    
    df=security_price("AAPL","2023-1-1","2023-6-30")
    curve_trend_regress(df,col,threshhold=0.1)    
    
    df=security_price("AAPL","2023-1-1","2023-1-10")
    curve_trend_regress(df,col,threshhold=0.1) 

    
def curve_trend_regress(df,col,threshhold=0.0001):
    """
    功能：回归简单方程y=a+b*x，并判断系数b的显著性星星。目的为判断曲线走势
    
    输入项：
    df: 数据框，假设其索引为日期项，且已升序排列
    col: 因变量，检查该变量的走势，向上，向下，or 不明显（无显著性星星）
    
    返回值：
    '？'：回归不成功
    '➠'：回归结果不显著或斜率接近零(其绝对值小于threshhold)
    '➷'：斜率为负数且其绝对值不小于threshhold且显著
    '➹'：斜率为正数且其绝对值不小于threshhold且显著
    """    
    # 检查df是否为空
    if df is None:
        return ' '
    if len(df)==0:
        return ' '
    
    # 按照索引升序排列，以防万一
    df1=df.copy()
    df1.sort_index(ascending=True,inplace=True)
    df1['id']=range(len(df1))
    
    from scipy import stats
    try:
        output=stats.linregress(df1['id'],df1[col])
        (b,a,r_value,p_value,std_err)=output
    except:
        # 处理可能的空值
        df1.fillna(method='ffill',inplace=True)
        df1.fillna(method='bfill',inplace=True)
        try:
            output=stats.linregress(df1['id'],df1[col])
            (b,a,r_value,p_value,std_err)=output
        except:
            return ' '
    
    # 生成显著性星星
    stars=sigstars(p_value)
    
    # 判断斜率方向
    b_abs=abs(b)
    result='➠'
    #if b_abs >= threshhold and b > 0 and '*' in stars:
    if b_abs >= threshhold and b > 0:    
        result='➹'
    #if b_abs >= threshhold and b < 0 and '*' in stars:
    if b_abs >= threshhold and b < 0:    
        result='➷'
    
    return result

def curve_trend_direct(df,col,threshhold=0.01):
    """
    功能：直接对比首尾值大小。目的为判断曲线走势
    
    输入项：
    df: 数据框，假设其索引为日期项，且已升序排列
    col: 考察变量，检查该变量的走势，向上，向下，or 不明显（无显著性星星）
    threshhold：相对值
    返回值：(尾值-首值)/首值
    '➠'：变化率接近零(其绝对值小于threshhold)
    '➷'：变化率为负数且其绝对值不小于threshhold
    '➹'：变化率为正数且其绝对值不小于threshhold
    """    
    # 检查df是否为空
    if df is None:
        return ' '
    if len(df)==0:
        return ' '
    
    # 按照索引升序排列，以防万一
    df1=df.copy()
    df1.sort_index(ascending=True,inplace=True)
    first_value=df1.head(1)[col].values[0]
    last_value=df1.tail(1)[col].values[0]
    
    #采用相对值，避免数量级差异，同时避免负负得正
    if first_value != 0.0:
        diff=(last_value - first_value)/abs(first_value)
    elif last_value != 0.0:
        #不得已
        diff=(last_value - first_value)/abs(last_value)
    else:
        #实在不得已
        diff=last_value - first_value
        
    diff_abs=abs(diff)
    
    # 判断斜率方向
    result='➠'
    """
    if diff_abs >= threshhold and diff > 0:    
        result='➹'
    if diff_abs >= threshhold and diff < 0:    
        result='➷'
    """
    #留出区间-threshhold至threshhold视为平行趋势
    if diff > threshhold:    
        result='➹'
    if diff < -threshhold:    
        result='➷'
    
    return result    
#==============================================================================
if __name__=='__main__':
    stars_current=''
    change_recommend_stars(stars_current,change='+')
    change_recommend_stars(stars_current,change='-')
    
    stars_current='✮'
    change_recommend_stars(stars_current,change='+')
    change_recommend_stars(stars_current,change='-')
    
    stars_current='✮✮'
    change_recommend_stars(stars_current,change='+')
    change_recommend_stars(stars_current,change='-')
    
    stars_current='✮✮✮'
    change_recommend_stars(stars_current,change='+')
    change_recommend_stars(stars_current,change='-')
    
    
def change_recommend_stars(stars_current,change='+'):
    """
    功能：增减推荐的星星个数
    """   
    stars0=''
    stars1='✮'
    stars2='✮✮'
    stars3='✮✮✮'
    
    # 计算当前的星星个数
    if stars_current==stars0:
        num=0
    elif stars_current==stars1:
        num=1
    elif stars_current==stars2:
        num=2
    elif stars_current==stars3:
        num=3
    else:
        num=3
        
    if change == '+':
        if stars_current==stars0:
            stars_new=stars1
        elif stars_current==stars1:
            stars_new=stars2
        elif stars_current==stars2:
            stars_new=stars3
        elif stars_current==stars3:
            stars_new=stars3
        else:
            stars_new=stars3
        
    if change == '-':
        if stars_current==stars0:
            stars_new=stars0
        elif stars_current==stars1:
            stars_new=stars0
        elif stars_current==stars2:
            stars_new=stars1
        elif stars_current==stars3:
            stars_new=stars2
        else:
            stars_new=stars2   
            
    return stars_new

#==============================================================================
if __name__=='__main__':
    stars_current=''
    stars_current='✮✮'
    
    change='+'
    change='++'
    change='-'
    
    change_stars2(stars_current,change)
    
def change_stars2(stars_current,change='+'):
    """
    功能：增减推荐的星星个数
    注意：change中不能同时出现+-符号，只能出现一种，但可以多个
    """   
    stars1='✮'
    
    num_plus=change.count('+')
    if num_plus > 0:
        stars_new=stars_current+stars1 * num_plus

    num_minus=change.count('-')
    if num_minus >= 1:
        stars_new=stars_current
        for n in range(1,num_minus+1):
            stars_new=stars_new[:-1]
            if hzlen(stars_new)==0: break
    """
    if hzlen(stars_new)>5:
        stars_new=stars_new[:5]
    """    
    return stars_new

#==============================================================================
if __name__=='__main__':
    symbol='---'
    exclude_collist=['c1']
    
    import pandas as pd
    df=pd.DataFrame({'c1':[10,11,12],'c2':['---',110,'---'],'c3':['---',1100,'---']})
    df_filter_row(df,exclude_collist=['c1'],symbol='---')
    
def df_filter_row(df,exclude_collist=[],symbol=''):
    """
    功能：删除df中的全部行，如果该行除去exclude_collist外其全部列的1值均为symbol
    """
    # 若为空直接返回
    if len(df)==0:
        return df
    
    # 找出需要判断的列列表
    collist=list(df)
    for e in exclude_collist:
        collist.remove(e)
    
    # 逐行打是否为symbol标记
    df2=df.copy()
    df2['EmptyRow']=True    # 假定所有行都符合条件
    for index,row in df2.iterrows():
        for c in collist:
            #if row[c] not in [symbol,' ',0]:
            if row[c] not in [symbol]:
                df2.loc[index,'EmptyRow']=False

    # 删除符合条件的行                
    df3=df2[df2['EmptyRow']==False]
    df3.drop('EmptyRow',axis=1,inplace=True)
    
    return df3
        
        

#==============================================================================
if __name__=='__main__':
    a=65
    a=6.6000000000000005
    decimal=4
    sround(a,decimal=4)
    
def sround(a,decimal=4):
    """
    功能：解决round小数位偶尔无法截取问题，采取转字符串截取再转数值的方法
    注意：适合哪些偶尔但顽固出现小数位无法截取成功的难题
    """
    a1=str(a)
    a1list=a1.split('.')
    if len(a1list)==1:#无小数点，无需round
        return a
    
    a2=a1list[1]  
    a3=a2[:decimal]
    a4=a1list[0]+'.'+a3
    a5=float(a4)
    
    return a5

    
#==============================================================================
if __name__=='__main__':
    file='stooq.py'
    package='pandas_datareader'

def fix_package_x(file='stooq.py',package='pandas_datareader'):
    """
    功能：修复stooq.py，使用siat包中的stooq.py覆盖pandas_datareader中的同名文件
    注意：执行本程序需要系统管理员权限，可以系统管理员权限启动Jupyter或Spyder
    
    改进：建立一个Excel文件，记录需要修复的文件和包，例如：
    file                package
    stooq.py            pandas_datareader
    bond_zh_sina.py     akshare
    
    注意：在Python 3.13出错，暂时废弃！
    """
    #判断操作系统
    import sys; czxt=sys.platform
    if czxt in ['win32','win64']:
        os='windows'
    elif czxt in ['darwin']: #MacOSX
        os='mac'
    elif czxt in ['linux']: #linux
        os='linux'
    else:
        os='windows'
    
    #源文件
    import siat
    srcpath=siat.__path__[0]
    if os == 'windows':
        srcpath1=srcpath.replace("\\",'/')
        srcfile=srcpath1+'/'+file
    else:
        srcpath1=srcpath
        srcfile=srcpath1+'/'+file
    
    #目标地址
    cmdstr1='import '+package
    exec(cmdstr1)   #无返回值地执行字符串代码，此句在Python 3.13后台不管用了！
    #import pandas_datareader
    #objpath=pandas_datareader.__path__[0]
    cmdstr2=package+'.__path__[0]'
    objpath=eval(cmdstr2)   #有返回值地执行字符串代码
    
    if os == 'windows':
        objpath1=objpath.replace("\\",'/')
        objfile=objpath1+'/'+file
    else:
        objpath1=objpath
        objfile=objpath1+'/'+file
    
    #复制文件
    from shutil import copyfile
    from sys import exit
    
    #例外处理
    try:
        result=copyfile(srcfile,objfile)
    except IOError as e:
        print("  #Error(fix_package): Unable to copy file. %s" % e)
        print("  Program failed, most likely becos of incorrect source/target directories.")
        print("  Solution: manually copy the file",srcfile,"to the folder",objpath1)
        #exit(1)
    except:
        print("  #Error(fix_package): Unexpected error:", sys.exc_info())
        #exit(1) 
    else:
        print("  Overrided",file,"in",package)
        print("  Please RESTART Python kernel before using siat")
    
    return    

def fix_package(file='stooq.py', package='pandas_datareader'):
    """
    功能：修复指定包中的文件，例如将 siat 中的 stooq.py 覆盖 pandas_datareader 中的同名文件。
    注意：执行本程序需要系统管理员权限，可以系统管理员权限启动 Jupyter 或 Spyder。
    """

    import sys
    import importlib.util
    import siat
    from shutil import copyfile

    # 判断操作系统
    platform = sys.platform
    if platform.startswith('win'):
        os_type = 'windows'
    elif platform == 'darwin':
        os_type = 'mac'
    elif platform.startswith('linux'):
        os_type = 'linux'
    else:
        os_type = 'unknown'

    # 获取源文件路径
    src_path = siat.__path__[0].replace("\\", "/") if os_type == 'windows' else siat.__path__[0]
    src_file = f"{src_path}/{file}"

    # 获取目标包路径
    spec = importlib.util.find_spec(package)
    if spec is None or not spec.submodule_search_locations:
        print(f"  #Error(fix_package): Package '{package}' not found.")
        return

    obj_path = spec.submodule_search_locations[0].replace("\\", "/") if os_type == 'windows' else spec.submodule_search_locations[0]
    obj_file = f"{obj_path}/{file}"

    # 执行文件复制
    try:
        copyfile(src_file, obj_file)
    except IOError as e:
        print(f"  #Error(fix_package): Unable to copy file. {e}")
        print("  Solution: manually copy the file", src_file, "to the folder", obj_path)
    except Exception as e:
        print(f"  #Error(fix_package): Unexpected error: {e}")
    else:
        print(f"  Overrided '{file}' in '{package}'")
        print("  Please RESTART Python kernel before using siat")

    return
    


#==============================================================================
if __name__=='__main__':
    file='stock_info.pickle'
    package='siat'
    mode='read'
    developer=False
    
    file_position()

def file_position_x(file='stock_info.pickle',package='siat',mode='read'):
    """
    功能：给定文件名file，返回其路径
    注意：执行本程序可能需要系统管理员权限，可以系统管理员权限启动Jupyter或Spyder
    
    改进：建立一个Excel文件，记录需要修复的文件和包，例如：
    file                package
    stooq.py            pandas_datareader
    bond_zh_sina.py     akshare
    
    问题：在Python 3.13上后台运行出错，暂时废弃！
    """
    #判断操作系统
    import sys; czxt=sys.platform
    if czxt in ['win32','win64']:
        os='windows'
    elif czxt in ['darwin']: #MacOSX
        os='mac'
    elif czxt in ['linux']: #linux
        os='linux'
    else:
        os='windows'
   
    #目标地址
    cmdstr1='import '+package
    exec(cmdstr1)   #无返回值地执行字符串代码
    #import pandas_datareader
    #objpath=pandas_datareader.__path__[0]
    cmdstr2=package+'.__path__[0]'
    objpath=eval(cmdstr2)   #有返回值地执行字符串代码
    
    if os == 'windows':
        objpath1=objpath.replace("\\",'/')
        objfile=objpath1+'/'+file
    else:
        objpath1=objpath
        objfile=objpath1+'/'+file
    
    if mode=='read':
        with open(objfile,'rb') as test:
            df = pickle.load(test) 
        return df
    else:
        return objfile    
#==============================================================================
import sys
import pickle
import importlib

def file_position(file='stock_info.pickle', package='siat', mode='read'):
    """
    功能：给定文件名file，返回其路径或读取其内容
    参数：
      file    - 目标文件名
      package - 存放该文件的 Python 包名
      mode    - 'read' 则加载并返回 pickle 中的对象，否则返回文件路径
    注意：执行本程序可能需要系统管理员权限
    """
    # 1. 判断操作系统
    czxt = sys.platform
    if czxt in ('win32', 'win64'):
        os_type = 'windows'
    elif czxt == 'darwin':
        os_type = 'mac'
    elif czxt.startswith('linux'):
        os_type = 'linux'
    else:
        os_type = 'windows'

    # 2. 动态导入 package
    try:
        pkg = importlib.import_module(package)
    except ImportError as e:
        raise ImportError(f"无法导入包 '{package}': {e}")

    # 3. 获取 package 的安装路径
    try:
        objpath = pkg.__path__[0]
    except (AttributeError, IndexError):
        # 如果是单文件模块，退而求其次取 __file__ 的目录
        objpath = importlib.util.find_spec(package).origin
        objpath = objpath.rsplit('/', 1)[0]

    # 4. 拼接目标文件路径
    if os_type == 'windows':
        objpath_norm = objpath.replace('\\', '/')
        objfile = objpath_norm + '/' + file
    else:
        objfile = objpath + '/' + file

    # 5. 根据 mode 读取或返回路径
    if mode == 'read':
        with open(objfile, 'rb') as f:
            return pickle.load(f)
    else:
        return objfile


#==============================================================================
#==============================================================================

def df_preprocess(dfs,measure,axhline_label,x_label,y_label, \
                  preprocess='scaling',scaling_option='change%'):
    """
    功能：对于dfs中的数据进行预处理变换，以便克服数量级压制现象更好地展现多条曲线的趋势
    """
    #填充空值，防止后续处理出错
    dfs.fillna(method='ffill') #使用前一个非NaN值填充（向下填充）
    dfs.fillna(method='bfill') #使用下一个非NaN值填充（向上填充）
    
    plus_sign=False
    
    preprocess1=preprocess.lower()
    #预处理方法：标准化，正态化，对数，缩放
    preplist=['standardize','normalize','logarithm','scaling']
    if preprocess1 in preplist:
        dfs2=dfs.copy(deep=True)

        collist=list(dfs2)
        meanlist=[]
        for c in collist:
            
            if preprocess1 == 'standardize': #标准化
                cmean=dfs2[c].mean()
                cstd=dfs2[c].std()
                dfs2[c]=dfs2[c].apply(lambda x: (x-cmean)/cstd)
                
            if preprocess1 == 'normalize': #正态化
                cmax=dfs2[c].max()
                cmin=dfs2[c].min()
                dfs2[c]=dfs2[c].apply(lambda x: (x-cmin)/(cmax-cmin))
                
            if preprocess1 == 'logarithm': #取对数
                import numpy as np
                dfs2[c]=dfs2[c].apply(lambda x: np.log(x) if x>0 else (0 if x==0 else -np.log(-x)))
                
            if preprocess1 == 'scaling': #缩放
                #缩放选项：均值，最小值，起点值，相对起点值的百分数（起点值为100），
                #相对起点值变化的百分数（起点值为0）
                scalinglist=['mean','min','start','percentage','change%']
                if not (scaling_option in scalinglist):
                    print("  #Error(df_preprocess): invalid scaling option",scaling_option)
                    print("  Valid scaling option:",scalinglist)
                    return None
                if scaling_option == 'mean':
                    cmean=dfs2[c].mean()   #使用均值
                    scalingOptionText=text_lang('均值','mean value')
                    
                if scaling_option == 'min':
                    cmean=dfs2[c].min()    #使用最小值
                    scalingOptionText=text_lang('最小值','min value')
                    
                #if scaling_option == 'start':
                if scaling_option in ['start','percentage','change%']:
                    # 从头寻找第一个非空数值
                    import numpy as np
                    for n in range(0,len(dfs2)):
                        try:
                            checknan=np.isnan(dfs2[c][n])
                        except: continue
                        if checknan: continue
                        else:
                            cmean=dfs2[c][n] #使用第一个非空值
                            break
                    
                    if scaling_option in ['start']:
                        scalingOptionText=text_lang('起点值','starting value')  
                    elif scaling_option in ['percentage']:
                        scalingOptionText=text_lang('百分比','percentage') 
                    else:
                        scalingOptionText=text_lang('变化率%','change%')
                try:
                    meanlist=meanlist+[cmean]
                except: continue
            
            #print(cmean,cstd,dfs2[c])

        if (preprocess1 == 'scaling') and ('Exp Ret' not in measure):
            # 加上后一个条件是为了防止出现division by zero错误
            if len(meanlist)==0:
                return None
            
            if scaling_option not in ['percentage','change%']:
                meanlistmin=min(meanlist)
                meanlist2= [x / meanlistmin for x in meanlist]
                    
                for c in collist:
                    pos=collist.index(c)
                    cfactor=meanlist2[pos]
                    #dfs2[c]=dfs2[c].apply(lambda x: x/cfactor)
                    dfs2[c]=dfs2[c].apply(lambda x: x/abs(cfactor))
            elif scaling_option == 'percentage': #相对起点值的百分数（起点值为100）
                for c in collist:
                    pos=collist.index(c)
                    cfactor=meanlist[pos]
                    #dfs2[c]=dfs2[c].apply(lambda x: round(x/cfactor*100,2))
                    #dfs2[c]=dfs2[c].apply(lambda x: round(x/abs(cfactor)*100,4))
                    dfs2[c]=dfs2[c].apply(lambda x: x/abs(cfactor)*100)
            elif scaling_option == 'change%': #相对起点值变化的百分数（起点值为0）
                plus_sign=True
                for c in collist:
                    pos=collist.index(c)
                    cfactor=meanlist[pos]
                    #dfs2[c]=dfs2[c].apply(lambda x: round((x/cfactor-1)*100,4))
                    dfs2[c]=dfs2[c].apply(lambda x: (x/cfactor-1)*100)
                
        #设置中英文的脚注和纵轴标记
        lang=check_language()        
        if lang == 'English':
            if preprocess1 == 'standardize':
                std_notes="Note: for ease of comparison, data are standardized "
                measure_suffix='(standardized)'
            if preprocess1 == 'normalize':
                std_notes="Note: for ease of comparison, data are normalized"
                measure_suffix='(normalized)'
            if preprocess1 == 'logarithm':
                std_notes="Note: for ease of comparison, data are logarithmed"
                measure_suffix='(logarithmed)'
            if preprocess1 == 'scaling':
                if scaling_option == 'mean':
                    std_notes="Note: for ease of comparison, data are scaled by mean value"
                    measure_suffix='(scaling by mean)'
                elif scaling_option == 'min':
                    std_notes="Note: for ease of comparison, data are scaled by min value"
                    measure_suffix='(scaling by min)'
                elif scaling_option == 'start':
                    std_notes="Note: for ease of comparison, data are scaled by starting value"
                    measure_suffix='(scaling by start)'
                elif scaling_option == 'percentage':
                    std_notes="Note: for ease of comparison, data are in percentage of starting value"
                    measure_suffix='(in prcentage%)'
                elif scaling_option == 'change%':
                    std_notes="Note: for ease of comparison, data are in change % of starting value"
                    measure_suffix='(change %)'                
        else:
            if preprocess1 == 'standardize':
                std_notes="注意：为突出变化趋势，对数据进行了标准化处理，非原值"
                measure_suffix='(标准化处理后)'
            if preprocess1 == 'normalize':
                std_notes="注意：为突出变化趋势，对数据进行了归一化处理，非原值"
                measure_suffix='(归一化处理后)'
            if preprocess1 == 'logarithm':
                std_notes="注意：为突出变化趋势，对数据进行了对数处理，非原值"
                measure_suffix='(对数处理后)'
            if preprocess1 == 'scaling':
                if scaling_option == 'mean':
                    std_notes="注意：为突出变化趋势，按均值对原始数据进行了比例缩放，非原值"
                    measure_suffix='(按均值比例缩放后)'
                elif scaling_option == 'min':
                    std_notes="注意：为突出变化趋势，按最小值对原始数据进行了比例缩放，非原值"
                    measure_suffix='(按最小值比例缩放后)'
                elif scaling_option == 'start':
                    std_notes="注意：为突出变化趋势，按起点值对原始数据进行了比例缩放，非原值"
                    measure_suffix='(按起点值比例缩放后)'
                elif scaling_option == 'percentage':
                    std_notes="注释：为突出变化趋势，期间起点数值=100%，其他数值为相对百分比，非原值"
                    measure_suffix='(相对百分数%)'
                elif scaling_option == 'change%':
                    std_notes="注释：为突出变化趋势，图中数值为相对期间起点的增减百分比，非原值"
                    #measure_suffix='(增/减%)'
                    measure_suffix='(涨跌幅度%)'
                    axhline_label='零线' #可以在security_trend中使用critical_value选项指定水平线位置，默认0
                    #axhline_value=0
                    
        if 'Exp Ret' not in measure:
            x_label=std_notes+'\n'+x_label
            y_label=y_label+measure_suffix
            
    else:
        dfs2=dfs
        
    #返回内容
    return dfs2,axhline_label,x_label,y_label,plus_sign
#==============================================================================
if __name__=='__main__':
    is_running_in_jupyter()


def is_running_in_jupyter():
    """
    功能：检测当前环境是否在Jupyter中，误判Spyder为Jupyter，不行！
    """
    try:
        # 尝试导入IPython的一些模块
        from IPython import get_ipython
 
        ipython = get_ipython()
        if 'IPKernelApp' not in ipython.config:
            return False
        return True
    
    except ImportError:
        return False
    
#==============================================================================
if __name__=='__main__':
    date1=pd.to_datetime('2024-1-2')
    date2=pd.to_datetime('2024-1-9')
    days_between_dates(date1, date2)
 
def days_between_dates(date1, date2):
    """
    注意：date1和date2为datetime类型
    """
    from datetime import datetime
    delta = date2 - date1
    return delta.days

#==============================================================================
if __name__=='__main__':
    stars_num=0
    stars_num=3
    stars_num=4.2
    stars_num=4.6
    
    generate_stars(stars_num)
    
def generate_stars(stars_num):
    """
    功能：基于星星个数stars_num生成推荐星星符号，支持半颗星
    """   
    stars1='✮'
    starsh='☆'
    
    stars_int=int(stars_num)
    result=stars_int * stars1
    
    if (stars_num - stars_int) >= 0.5:
        result=result + starsh
        
    return result
    

#==============================================================================
if __name__=='__main__':
    df=get_price('000001.SS','2000-1-1','2024-3-22')
    column='Close'
    minimum=30
    method='max'
    
    df1=df[column].resample('4H').max()
    df2=df1.interpolate(method='cubic')
    
    period='24H'
    df2=df_resampling(df,column,period,method='mean',minimum=minimum)
    df2[column].plot(title=period)

    
    period='auto'; method='mean'; minimum=50
    df2=df_resampling(df,column,period,method='mean',minimum=minimum)
    df2[column].plot()


def df_resampling(df,column,period='auto',method='max',minimum=30):
    """
    注意：未完成状态。遇到的问题：平滑后数据的后面时间段丢失严重！
    目的：将大量时间序列数据绘制重新采样，减少极端值，使得数据趋势简洁明了，可能丢失部分细节
    功能：将df按照period对column字段数值重新采样，采样方法为method，采样前个数不少于minimum
    注意：df需为时间序列；column为单个字段，需为数值型
    period：采样间隔，支持小时'H'或'nH'(n=2,3,...)、周'W'、月'M'、季'Q'或年'Y'，默认由系统决定
    method：暂仅支持平均值方法mean(典型)和求和方法sum
    minimum：采样后需保留的最少数据个数，默认30个
    """
    DEBUG=True
    
    import pandas as pd
    import numpy as np
    
    #检查df长度：是否需要重新采样
    if len(df) <= minimum: 
        if DEBUG: print("  #Notice(df_resampling): no need to resample",len(df))
        return df #无需重新采样，返回原值
    
    #仅对采样字段进行处理
    if column not in df.columns: 
        if DEBUG: print("  #Warning(df_resampling): non-exist column",column)
        return df #返回原值
    
    #取出采样字段    
    df1=df[[column]].copy() #避免影响到原值
    
    #寻求最佳采样间隔
    period_list=['2H','4H','6H','8H','12H','24H']
    std_list=[]
    dft_list=[]
    for p in period_list:
        dft1=df1[column].resample(p).mean()
        dft2=dft1.interpolate(method='linear')
        stdt=dft2.std()
        std_list=std_list+[stdt]
        dft_list=dft_list+[dft2]
    
    std_min=min(std_list)
    pos=std_list.index(std_min)
    period_min=period_list[pos]
    df2=dft_list[pos]
    
    
    #再次检查采样后的长度
    if len(df2) < minimum: 
        if DEBUG: print("  #Warning(df_resampling): resampled number",len(df2),"< minimum",minimum)
        return df #返回原值
    
    return df2

#==============================================================================
if __name__=='__main__':
    df=get_price('000001.SS','2000-1-1','2024-3-22')
    
    
def linewidth_adjust(df):
    """
    功能：根据df中元素个数多少调节绘制曲线时线段的宽度linewidth
    """    

    dflen=len(df)
    if dflen > 100: lwadjust=1.2
    elif dflen > 200: lwadjust=1.0
    elif dflen > 300: lwadjust=0.8
    elif dflen > 500: lwadjust=0.4
    elif dflen > 1000: lwadjust=0.2
    elif dflen > 2000: lwadjust=0.1
    elif dflen > 3000: lwadjust=0.05
    elif dflen > 5000: lwadjust=0.01
    else: lwadjust=1.5
    
    return lwadjust

#==============================================================================
if __name__=='__main__':
    start='MRM'
    start='L3M'
    start='MRY'
    start='L30Y'
    
    start='default'; end='default'
    
    start='2024-1-1'; end='2023-1-1'
    
    start_end_preprocess(start,end='today')

def start_end_preprocess(start,end='today'):
    """
    功能：处理简约日期为具体日期，并检查日期的合理性
    """

    # 检查日期：截至日期
    import datetime as dt; 
    todaydt=dt.date.today();todaystr=todaydt.strftime('%Y-%m-%d')
    
    end=end.lower()
    if end in ['default','today']:
        todate=todaystr
    else:
        validdate,todate=check_date2(end)
        if not validdate:
            print("  #Warning(start_end_preprocess): invalid date for",end)
            todate=todaystr

    # 检查日期：开始日期
    start=start.lower()
    
    if start in ['default','mrm','l1m']:  # 默认近一个月
        fromdate=date_adjust2(todate,adjust_month=-1,adjust_day=-1) #有利于绘图横坐标日期标示
    elif start in ['mrw','l1w']:  # 近1个周
        fromdate=date_adjust2(todate,adjust_month=0,adjust_day=-7-1)        
    elif start in ['lhm','l2w']:  # 近2个周
        fromdate=date_adjust2(todate,adjust_month=0,adjust_day=-7*2-1)        
    elif start in ['l3w']:  # 近3个周
        fromdate=date_adjust2(todate,adjust_month=0,adjust_day=-7*3-1)        
    elif start in ['l2m']:  # 近2个月
        fromdate=date_adjust2(todate,adjust_month=-2,adjust_day=-1)        
    elif start in ['mrq','l3m']:  # 近三个月
        fromdate=date_adjust2(todate,adjust_month=-3,adjust_day=-1) 
    elif start in ['l6m','mrh']:  # 近6个月
        fromdate=date_adjust2(todate,adjust_month=-6,adjust_day=-1)         
    elif start in ['mry','l12m','l1y']:  # 近一年
        fromdate=date_adjust2(todate,adjust_year=-1,to_prev_month_end=True)  
    elif start in ['l2y']:  # 近两年以来
        fromdate=date_adjust2(todate,adjust_year=-2,to_prev_month_end=True)  
    elif start in ['l3y']:  # 近三年以来
        fromdate=date_adjust2(todate,adjust_year=-3,to_prev_month_end=True)  
    elif start in ['l4y']:  # 近三年以来
        fromdate=date_adjust2(todate,adjust_year=-4,to_prev_month_end=True)  
        
    elif start in ['l5y']:  # 近五年以来
        fromdate=date_adjust2(todate,adjust_year=-5,to_prev_year_end=True)  
    elif start in ['l6y']:  # 近五年以来
        fromdate=date_adjust2(todate,adjust_year=-6,to_prev_year_end=True)  
    elif start in ['l7y']:  # 近五年以来
        fromdate=date_adjust2(todate,adjust_year=-7,to_prev_year_end=True)  
        
    elif start in ['l8y']:  # 近八年以来
        fromdate=date_adjust2(todate,adjust_year=-8,to_prev_year_end=True)   
    elif start in ['l10y']:  # 近十年以来
        fromdate=date_adjust2(todate,adjust_year=-10,to_prev_year_end=True)  
    elif start in ['l20y']:  # 近20年以来
        fromdate=date_adjust2(todate,adjust_year=-20,to_prev_year_end=True)  
    elif start in ['l15y']:  # 近五年以来
        fromdate=date_adjust2(todate,adjust_year=-15,to_prev_year_end=True)  
    elif start in ['l25y']:  # 近五年以来
        fromdate=date_adjust2(todate,adjust_year=-25,to_prev_year_end=True)  
        
    elif start in ['l30y']:  # 近30年以来
        fromdate=date_adjust2(todate,adjust_year=-30,to_prev_year_end=True)   
    elif start in ['l40y']:  # 近五年以来
        fromdate=date_adjust2(todate,adjust_year=-40,to_prev_year_end=True)  
    elif start in ['l50y']:  # 近五年以来
        fromdate=date_adjust2(todate,adjust_year=-50,to_prev_year_end=True)  
        
    elif start in ['ytd']:  # 今年以来
        fromdate=str(todaydt.year-1)+'-12-31'        
    else:
        validdate,fromdate=check_date2(start)
        if not validdate:
            print("  #Warning(security_trend): invalid date",start)
            fromdate=date_adjust2(todate,adjust_month=-1,adjust_day=-1)    
    
    result,_,_=check_period(fromdate,todate)
    if not result:
        todate=todaystr
        print("  #Warning(start_end_preprocess): invalid date period between",fromdate,todate)
        
    return fromdate,todate

#==============================================================================
if __name__=='__main__':
    text_cn="这是中文"
    text_en="This is in English"
    
    set_language('English')
    set_language('Chinese')
    
    text_lang(text_cn, text_en)
    
def text_lang(text_cn, text_en):
    """
    功能：检测当前语言环境，若为中文返回text_cn，否则返回text_cn
    """
    lang=check_language()
    
    if lang == 'Chinese':
        result=text_cn
    else:
        result=text_en
        
    return result

#==============================================================================
if __name__=='__main__':
    df,_=get_price_1ticker('sh010504',fromdate='2024-1-1',todate='2024-4-6',fill=False)

def df_have_data(df):
    """
    功能：判断df内是否有数据
    返回：有数据-Found，df存在但无数据-Empty，其余-None
    """
    found=None
    if df is None:
        found='None'
    elif len(df)==0:
        found='Empty'
    else:
        found='Found'
        
    return found

#==============================================================================
if __name__=='__main__':
    df,_=get_price_1ticker('sz149976',fromdate='2024-1-1',todate='2024-4-6',fill=False)
    colname='Close'
    extend_business_date=False
    
    df4=df_fill_extend(df,colname='Close',extend_business_date=False)

def df_fill_extend(df,colname='Close',extend_business_date=False):
    """
    功能：对df进行填充
    colname：基于此判断是否为空，默认为'Close'
    extend_business_date：False=仅对df现有值进行填充，
    True=对于现有开始结束日期之间的所有非周末日期进行扩展后填充
    """
    import numpy as np
    
    df1=df.copy()
    #仅对现有数据中的缺失值进行填充
    if not extend_business_date:
        df1['filled']=df1[colname].apply(lambda x: True if np.isnan(x) else False)
        df4=df1.ffill(axis=0) #从开始向尾部填充
        #df5=df4.bfill(axis=0) #从尾部向开始填充，容易对后续的分析结果造成误导，慎用！
    else:
        fromdate=df1.head(1).index[0].strftime('%Y-%m-%d')
        todate=df1.tail(1).index[0].strftime('%Y-%m-%d')
        
        df2dt=pd.bdate_range(start=fromdate,end=todate)
        df2dt=pd.to_datetime(df2dt)
        df2=pd.DataFrame(index=df2dt)
        df3=pd.merge(df2,df1,how='outer',left_index=True,right_index=True)
        
        df3['filled']=df3[colname].apply(lambda x: True if np.isnan(x) else False)
        df4=df3.ffill(axis=0) #从开始向尾部填充
        #df5=df4.bfill(axis=0) #从尾部向开始填充
 
    return df4
    
#==============================================================================
if __name__=='__main__':
    url="https://finance.yahoo.com"
    url="https://finance.sina.com.cn"
    
    test_website(url)

def test_website(url="https://finance.yahoo.com"):
    """
    功能：测试一个网址是否可访问
    """
    import requests
    headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    try:
        response = requests.get(url,headers=headers)
        if response.status_code == 200:
            #print(f"{url} is accessible.")
            return True
        else:
            #print(f"{url} is not accessible. Status code: {response.status_code}")
            return False
    except requests.exceptions.RequestException:
        #print(f"{url} is not accessible. Network error occurred.")
        return False

if __name__=='__main__':
    test_yahoo_finance()
    
def test_yahoo_finance():
    url="https://finance.yahoo.com"
    return test_website(url) 
       
#==============================================================================
if __name__=='__main__':
    check_os()

def check_os():
    """
    功能：检测操作系统的类型
    """
    import platform
    system = platform.system()
    if system == "Windows":
        return "Windows"
    elif system == "Linux":
        return "Linux"
    elif system == "Darwin":
        return "Mac OSX"
    else:
        return "Unknown OS"  
    
#==============================================================================
if __name__=='__main__':
    check_python_version()

def check_python_version():
    """
    功能：检测Python的版本号
    """
    import sys
    python_version = sys.version_info
    ver=f"{python_version.major}.{python_version.minor}.{python_version.micro}"
    return ver

#==============================================================================
if __name__=='__main__':
    ticker='AAPL'
    fromdate='2011-1-1'
    todate='2020-12-31'
    retry_count=3
    pause=1
    
    ticker='ABCD'
    
    ticker=['AAPL','MSFT']
    ticker=['AAPL','MSFT','ABCD']
    
    ticker=['600011.SS']
    fromdate='2020-1-1'
    todate='2020-6-30'    

def upper_ticker(ticker):
    """
    功能：改成大写，字符串或列表
    """
    if isinstance(ticker,str):
        return ticker.upper()
    elif isinstance(ticker,list):
        tlist=[]
        for t in ticker:
            try:
                tupper=t.upper()
            except:
                tupper=t
            tlist=tlist+[tupper]
        return tlist


#==============================================================================
if __name__=='__main__':
    ticker='600519.SS'
    ticker=['600519.SS','000858.SZ']
    ticker=['600519.SS','000858.SZ',pf]
    
    ticker_type='auto'
    ticker_type='bond'
    ticker_type=['auto','bond']
    ticker_type=['xyz','bond']
    
    ticker_type_preprocess_1str(ticker,ticker_type)
    
def ticker_type_preprocess_1str(ticker,ticker_type='auto'):
    """
    功能：根据ticker情况(单个原生证券)处理ticker_type，使之与ticker对应    
    """
    if isinstance(ticker,str):
        if isinstance(ticker_type,str):
            ticker_type9=ticker_type
        if isinstance(ticker_type,list):
            if len(ticker_type) >= 1:
                ticker_type9=ticker_type[0]
            else:
                ticker_type9='auto'
    else:
        ticker_type9=ticker_type

    if ticker_type9 not in ['auto','stock','fund','bond']:
        ticker_type9='auto'
            
    return ticker_type9

if __name__=='__main__':
    pf={'Market':('China','000001.SS','股债基组合'),'600519.SS':50,'sh018003':150,'sh010504':300}
    ticker=['600519.SS','000858.SZ','000002.SZ']
    ticker=['600519.SS','000858.SZ',pf]
    
    ticker_type='auto'
    ticker_type='bond'
    ticker_type=['auto','bond']
    ticker_type=['xyz','bond']
    
    ticker_type_preprocess_mstr(ticker,ticker_type)

def ticker_type_preprocess_mstr(ticker,ticker_type='auto'):
    """
    功能：根据ticker情况(多个原生证券)处理ticker_type，使之与ticker对应    
    """
    if isinstance(ticker,list):
        if isinstance(ticker_type,str):
            ticker_type8=[ticker_type]*len(ticker)
            
        if isinstance(ticker_type,list):
            if len(ticker) > len(ticker_type):
                ticker_type8=ticker_type+[ticker_type[-1]]*(len(ticker)-len(ticker_type))
            else:
                ticker_type8=ticker_type
                
        ticker_type9=[]
        for tt in ticker_type8:
            if tt  not in ['auto','stock','fund','bond']:
                tt='auto'
            ticker_type9=ticker_type9+[tt]
        
    else:
        ticker_type9=ticker_type
        
    return ticker_type9

if __name__=='__main__':
    ticker={'Market':('China','000001.SS','股债基组合'),'600519.SS':50,'sh018003':150,'sh010504':300}
    
    ticker_type='auto'
    ticker_type='bond'
    ticker_type=['auto','bond']
    ticker_type=['xyz','bond']
    
    ticker_type_preprocess_1portfolio(ticker,ticker_type)

def ticker_type_preprocess_1portfolio(ticker,ticker_type='auto'):
    """
    功能：根据ticker情况(单个投资组合)处理ticker_type，使之与ticker对应    
    """    
    if isinstance(ticker,dict):
        _,_,tickerlist,_,ticker_type=decompose_portfolio(ticker)
        if len(tickerlist)==1:
            ticker_type9=ticker_type_preprocess_1str(tickerlist[0],ticker_type)
        else:
            ticker_type9=ticker_type_preprocess_mstr(tickerlist,ticker_type)
    else:
        ticker_type9=ticker_type
        
    return ticker_type9
    
if __name__=='__main__':
    pf={'Market':('China','000001.SS','股债基组合'),'600519.SS':50,'sh018003':150,'sh010504':300}
    ticker='600519.SS'
    ticker=['600519.SS','000858.SZ','000002.SZ']
    ticker={'Market':('China','000001.SS','股债基组合'),'600519.SS':50,'sh018003':150,'sh010504':300}

    ticker=['600519.SS','000858.SZ',pf]
    
    ticker_type='auto'
    ticker_type='bond'
    ticker_type=['auto','bond']
    ticker_type=['xyz','bond']
    
    ticker_type_preprocess_mticker_mixed(ticker,ticker_type)
    
def ticker_type_preprocess_mticker_mixed(ticker,ticker_type='auto'):
    """
    功能：根据ticker(可为列表，列表中可含有投资组合)情况处理ticker_type，使之与ticker对应    
    """
    #单个证券，非投资组合
    if isinstance(ticker,str):
        ticker_type9=ticker_type_preprocess_1str(ticker,ticker_type)  
        return ticker_type9
              
    #单个证券，投资组合
    if isinstance(ticker,dict):
        ticker_type9=ticker_type_preprocess_1portfolio(ticker,ticker_type)
        return ticker_type9
        
    #混合列表
    if isinstance(ticker,list):
        if isinstance(ticker_type,str):
            ticker_type8=[ticker_type]*len(ticker)
        if isinstance(ticker_type,list):
            if len(ticker) > len(ticker_type):
                ticker_type8=ticker_type+[ticker_type[-1]]*(len(ticker)-len(ticker_type))
            else:
                ticker_type8=ticker_type
        
        ticker_type9=[]
        for t in ticker:
            pos=ticker.index(t)
            tt8=ticker_type8[pos]
            tt9=tt8
            
            if isinstance(t,str):
                tt9=ticker_type_preprocess_1str(t,tt8)
            
            if isinstance(t,dict):
                tt9=ticker_type_preprocess_1portfolio(t,tt8)
    
            ticker_type9=ticker_type9+[tt9]    
    else:
        ticker_type9=ticker_type

    return ticker_type9


#==============================================================================
if __name__=='__main__':
    df=get_price('600519.SS','2024-4-1','2024-4-20')
    titletxt='This is the Tilte'
    titletxt=''
    footnote='This is the footnote'
    facecolor='papayawhip'
    decimals=2
    
    #在Spyder中无法测试效果
    df_display_CSS(df,titletxt,footnote,facecolor,decimals)

def df_display_CSS(df,titletxt='',footnote='',facecolor='papayawhip',decimals=2, \
                   hide_columns=False,
                   first_col_align='left',second_col_align='right', \
                   last_col_align='right',other_col_align='right', \
                   titile_font_size='16px',heading_font_size='15px', \
                   data_font_size='14px',footnote_font_size='13px'):
    """
    功能：采样CSS式样显示df，适用于Jupyter环境，整齐紧凑，不挑浏览器
    注意：若facecolor不被支持，则自动改为papayawhip
    
    特别注意：运行show_df()后将发生格式错乱（表格位置自动居中，标题从表格上方移到下方，原脚注仍然居左）
    因此，不要轻易使用show_df()
    """
    import pandas as pd
    import numpy as np

    # 重置为Pandas默认样式, 无效！
    pd.reset_option('all')

    #检查df是否为空
    if len(df)==0: return
    
    #替换nan和inf
    df.replace([np.inf, -np.inf],'-', inplace=True)
    df.replace([np.nan],'-', inplace=True)

    #默认的facecolor，一旦不支持则改为这个颜色
    facecolor_default='papayawhip' 
    
    #不显示索引列，注意style1已经不是DaraFrame了
    style1=df.style.hide()
    
    if hide_columns:
        style1=df.style.hide(axis='index').hide(axis='columns')
    
    #设置数值字段的千分位符号，同时设置数值字段的小数点精度
    style2=style1.format(precision=decimals,thousands=',',na_rep='-') 
    
    #设置标题/列名：对齐，颜色，背景
    try:
        style3=style2.set_caption(titletxt).set_table_styles(
            [{'selector':'caption', #设置标题对齐
              'props':[('color','black'),('font-size',titile_font_size),('font-weight','bold')]}, \
             
             {'selector':'th.col_heading', #设置列名对齐
              'props':[('color','black'),('background-color',facecolor), \
                       ('font-size',heading_font_size),('text-align','center'),('margin','auto')]}])        
    except:
        style3=style2.set_caption(titletxt).set_table_styles(
            [{'selector':'caption', #设置标题对齐
              'props':[('color','black'),('font-size',titile_font_size),('font-weight','bold')]}, \
             
             {'selector':'th.col_heading', #设置列名对齐
              'props':[('color','black'),('background-color',facecolor_default), \
                       ('font-size',heading_font_size),('text-align','center'),('margin','auto')]}])        
            
    #设置数据：字体大小
    style4=style3.set_properties(**{'font-size':data_font_size})
    
    #设置数据：对齐，第一列，最后列，中间列
    col_list=list(df)
    style5=style4.set_properties(**{'text-align':other_col_align}).\
                  set_properties(**{'text-align':first_col_align},subset=[col_list[0]]).\
                  set_properties(**{'text-align':second_col_align},subset=[col_list[1]]).\
                  set_properties(**{'text-align':last_col_align},subset=[col_list[-1]])
    
    #设置数据：背景颜色
    try:
        style6=style5.set_properties(**{'background-color':facecolor,'color':'black'})
    except:
        print("  #Warning(df_display_CSS): unsupported color",facecolor,"\b, changed to default")
        style6=style5.set_properties(**{'background-color':facecolor_default,'color':'black'})

    #打印数据框本身
    print('') #空一行
    from IPython.display import display
    display(style6)    

    if not footnote=='':
        #print(footnote)
        
        from IPython.display import display, HTML
        ft_list=footnote.split('\n') #分行显示，因下列显示方式无法识别换行
        for ft in ft_list:
            # 使用HTML和CSS设置字体大小
            html_code = f'<p style="font-size:{footnote_font_size};">{ft}</p>'
            display(HTML(html_code))
    #print('') #空一行

    return


def df_display_CSS2(df,titletxt='',footnote='',facecolor='papayawhip',decimals=2, \
                   hide_columns=False,
                   first_col_align='left',second_col_align='right', \
                   last_col_align='right',other_col_align='right', \
                   titile_font_size='16px',heading_font_size='15px', \
                   data_font_size='14px',footnote_font_size='13px'):
    """
    功能：采样CSS式样显示df，适用于Jupyter环境，整齐紧凑，不挑浏览器
    注意：若facecolor不被支持，则自动改为papayawhip
    
    特别注意：运行show_df()后将发生格式错乱（表格位置自动居中，标题从表格上方移到下方，原脚注仍然居左）
    因此，不要轻易使用show_df()
    """
    import pandas as pd
    import numpy as np

    # 重置为Pandas默认样式, 无效！
    pd.reset_option('all')

    #检查df是否为空
    if len(df)==0: return
    
    #替换nan和inf
    df.replace([np.inf, -np.inf],'-', inplace=True)
    df.replace([np.nan],'-', inplace=True)

    #默认的facecolor，一旦不支持则改为这个颜色
    facecolor_default='papayawhip' 
    
    #不显示索引列，注意style1已经不是DaraFrame了
    style1=df.style.hide()
    
    if hide_columns:
        style1=df.style.hide(axis='index').hide(axis='columns')
    
    #设置数值字段的千分位符号，同时设置数值字段的小数点精度
    style2=style1.format(precision=decimals,thousands=',',na_rep='-') 
    
    #设置标题/列名：对齐，颜色，背景
    try:
        style3=style2.set_caption(titletxt).set_table_styles(
            [{'selector':'caption', #设置标题对齐
              'props':[('color','black'),('font-size',titile_font_size),('font-weight','bold')]}, \
             
             {'selector':'th.col_heading', #设置列名对齐
              'props':[('color','black'),('background-color',facecolor), \
                       ('font-size',heading_font_size),('text-align','center'),('margin','auto')]}])        
    except:
        style3=style2.set_caption(titletxt).set_table_styles(
            [{'selector':'caption', #设置标题对齐
              'props':[('color','black'),('font-size',titile_font_size),('font-weight','bold')]}, \
             
             {'selector':'th.col_heading', #设置列名对齐
              'props':[('color','black'),('background-color',facecolor_default), \
                       ('font-size',heading_font_size),('text-align','center'),('margin','auto')]}])        
            
    #设置数据：字体大小
    style4=style3.set_properties(**{'font-size':data_font_size})
    
    #设置数据：对齐，第一列，最后列，中间列
    col_list=list(df)
    style5=style4.set_properties(**{'text-align':other_col_align}).\
                  set_properties(**{'text-align':first_col_align},subset=[col_list[0]]).\
                  set_properties(**{'text-align':second_col_align},subset=[col_list[1]]).\
                  set_properties(**{'text-align':last_col_align},subset=[col_list[-1]])
    
    #设置数据：背景颜色
    try:
        style6=style5.set_properties(**{'background-color':facecolor,'color':'black'})
    except:
        print("  #Warning(df_display_CSS): unsupported color",facecolor,"\b, changed to default")
        style6=style5.set_properties(**{'background-color':facecolor_default,'color':'black'})

    # 压缩行间距
    style7 = style6.set_properties(
        subset=pd.IndexSlice[:, :],       # 全表
        **{
            'padding': '2px 4px',
            'line-height': '1.1',
            'vertical-align': 'top'
        }
    )

    #打印数据框本身
    print('') #空一行
    from IPython.display import display
    display(style7)    

    if not footnote=='':
        #print(footnote)
        
        from IPython.display import display, HTML
        ft_list=footnote.split('\n') #分行显示，因下列显示方式无法识别换行
        for ft in ft_list:
            # 使用HTML和CSS设置字体大小
            html_code = f'<p style="font-size:{footnote_font_size};">{ft}</p>'
            display(HTML(html_code))
    #print('') #空一行

    return

#==============================================================================
if __name__=='__main__':
    upgrade_siat()

def upgrade_siat(module_list=['siat','akshare','pandas','pandas_datareader', \
                 'yfinance','yahooquery','urllib3','tabulate','twine', \
                 'mplfinance','openpyxl','pip','bottleneck','ipywidgets'], \
                 pipcmd="python -m pip install --upgrade --user", \
                 mirror="aliyun"):
    """
    功能：一次性升级siat及其相关插件
    
    注意：pip的路径问题! 
    可在Anaconda Prompt下先执行python -m ensurepip再尝试。
    或python -m pip install --upgrade pip
    如果上述方法不适用，您可能需要重新安装Python，并确保在安装过程中选中了“Add Python to PATH”
    """
    DEBUG=False
    
    print("Upgrading siat and related modules, please wait ... ...")
    alternative=mirror

    #获取系统目录
    import sys
    syspath=sys.path
    
    #判断目录分隔符号
    win_sep='\\'; win_flag=False
    mac_sep='//'; mac_flag=False
    
    sp_list=syspath[0].split(win_sep)
    if len(sp_list) > 1:
        win_flag=True
        
    sp_list=syspath[0].split(mac_sep)
    if len(sp_list) > 1:
        win_flag=True   
    
    if win_flag:
        sep_flag=win_sep
    else:
        sep_flag=mac_sep
    
    #寻找anaconda3的安装目录
    for sp in syspath:
        sp_list=sp.split(sep_flag)
        if sp_list[-1] == 'anaconda3': break
    
    #生成pip命令字符串前半段，仅缺插件名
    #cmdstr=sp+sep_flag+'Scripts'+sep_flag+pipcmd+' '
    cmdstr=sp+sep_flag+pipcmd+' '
    
    #检查是否使用镜像源
    if alternative == "":
        alter_source=''
    elif alternative == "tsinghua":
        alter_source="-i https://pypi.tuna.tsinghua.edu.cn/simple/"
    elif alternative in ["alibaba","ali","aliyun"]:
        alter_source="-i https://mirrors.aliyun.com/pypi/simple/"
    elif alternative == "bfsu":
        alter_source="-i https://mirrors.bfsu.edu.cn/pypi/"
    elif alternative == "baidu":
        alter_source="-i https://mirror.baidu.com/pypi/simple/"        
    elif alternative == "tencent":
        alter_source="-i https://mirrors.cloud.tencent.com/pypi/simple/"  
    else:
        alter_source="-i https://mirrors.aliyun.com/pypi/simple/"
        
    #逐个升级插件
    import subprocess
    fail_list=[]
    
    """
    tqdm进度条：
    100%|██████████| 9/11 [02:18<02:30, 12.59s/it]
    9/11：一共11项，正在进行第9项
    02:18<02:30：已经花费时间02:18，预计花费时间02:30
    12.59s/it：平均每项花费时间12.59秒
    """
    from tqdm import tqdm
    for m in tqdm(module_list):
        #print("Upgrading",m,"... ...",end='')
        #print_progress_percent2(m,module_list,steps=5,leading_blanks=2)
        if DEBUG:
            print("  DEBUG: m={}".format(m))
        
        if alternative == "":
            cmdstr1=cmdstr+m
        else:
            cmdstr1=cmdstr+m+' '+alter_source
        if DEBUG:
            print("  DEBUG: cmdstr1={}".format(cmdstr1))
        
        #proc=subprocess.run(cmdstr1.split(' '),stdout=subprocess.PIPE)
        try:
            proc=subprocess.run(cmdstr1.split(' '))
            rcode=proc.returncode
            if rcode !=0: fail_list=fail_list+[m]
        except:
            print("  #Error(upgrade_siat): executable file python not found in {}".format(sp))
            print("  Solution: find out the exact path where the executable file python locates")
            return
    
    if len(fail_list) == 0:
        print("All specified modules are successfully upgraded!")
    else:
        print("All specified modules are successfully upgraded except",end='')
        print_list(fail_list,leading_blanks=1)
        
        if 'pip' in fail_list:
            print("Upgrading for pip, in Anaconda Prompt (Windows) or Terminal (Mac):")
            print("  python -m pip install --upgrade --user pip")
    print("Please RESTART Python kernel to enforce the upgraded modules!")    
    return

def df_index_timezone_remove(df):
    """
    功能：去掉df索引日期中的时区信息，避免日期过滤时出错
    注意：从雅虎财经获取的数据中日期索引项很可能带有时区
    """
    DEBUG=False
    
    # 检查是否因为处理时区而丢失了数据
    if DEBUG:
        print(f"BEFORE processing timezone, counts={len(df)}, from {df.index[0]} to {df.index[-1]}")
    
    import pandas as pd
    
    #可能无法处理某些复杂的时区情况
    df.index = pd.to_datetime(df.index,utc=True)
    df.index = df.index.tz_localize(None)
    
    if DEBUG:
        print(f"AFTER processing timezone, counts={len(df)}, from {df.index[0]} to {df.index[-1]}")
    
    return df
#==============================================================================

def df_swap_columns(df, col1, col2):
    """
    功能：交换df中的两个列的位置
    """
    cols = df.columns.tolist()
    i1, i2 = cols.index(col1), cols.index(col2)
    cols[i2], cols[i1] = cols[i1], cols[i2]
    
    return df[cols]

#==============================================================================
if __name__=='__main__':
    adate="2024-6-8"
    week_day(adate)
    week_day("2024-11-16")
    week_day("2024-11-17")
 
def week_day(adate):
    import pandas as pd
    try:
        datepd=pd.to_datetime(adate)
    except:
        return 0,False
    
    weekday = datepd.weekday()
    return weekday  # 周六和周日的索引值分别为5和6

#==============================================================================
if __name__=='__main__':
    adate="2024-6-8"
    is_weekend(adate)
 
def is_weekend(adate):
    import pandas as pd
    try:
        datepd=pd.to_datetime(adate)
    except:
        return False
    
    weekday = datepd.weekday()
    return weekday == 5 or weekday == 6  # 周六和周日的索引值分别为5和6


#==============================================================================
if __name__=='__main__':
    alist=['EMA40','EMA5','EMA','EMA20']
    alist=['EMA20','EMA5']
    sort_list_by_len(alist)
    
def sort_list_by_len(alist,reverse=False):
    """
    功能：基于字符串列表中元素的长度和大小排序
    """
    import pandas as pd
    adf=pd.DataFrame(columns=('item','len'))
    for a in alist:
        row=pd.Series({'item':a,'len':len(a)})
        try:
            adf=v.append(row,ignore_index=True)
        except:
            adf=adf._append(row,ignore_index=True)
    if not reverse:    
        adf.sort_values(by=['len','item'],ascending=True,inplace=True)
    else:
        adf.sort_values(by=['len','item'],ascending=False,inplace=True)
    
    alist_sorted=list(adf['item'])
    
    return alist_sorted
#==============================================================================
if __name__=='__main__':
    data=security_trend("AAPL")
    search_mode=True
    
    show_df(data,search_mode=False)
    show_df(data,search_mode=True)
    
    x=5
    show_df(x)

def show_df(data,search_mode=False):
    """
    功能：在Jupyter中查看dataframe，并可下载成Excel
    注意：将改变Jupyter中pandas的显示式样，谨慎使用
    """
    
    import pandas as pd
    
    if not isinstance(data,pd.DataFrame):
        print("#Warning: the first parameter must be a dataframe")
        return
    
    import datetime
    from itables import init_notebook_mode, show
    init_notebook_mode(all_interactive=True)

    df=data.copy()
    
    if not search_mode:
        show(df, buttons=["copyHtml5", "csvHtml5", "excelHtml5"])
    else:
        #需要所有日期字段都是datetime格式，有错误，不能用
        columns = df.columns
        # 判断哪些字段是日期，并转换
        date_columns=[]
        for col in columns:
            if 'date' in col.lower() or '日期' in col:
                try:
                    df[col]=df[col].apply(lambda x: pd.to_datetime(x))
                    date_columns=date_columns+[col]
                except:
                    continue
        
        firstCol=list(df)[0]
        firstValue=df[firstCol].values[0]
        
        show(df,
             layout={"tool":"searchBuilder"},
             searchBuilder={"preDefined":{
                 "criteria":[{"data":firstCol,"condition":"=","value":firstValue}]
             }})
    
    # 重置为Pandas默认样式, 无效！
    pd.reset_option('all')
    
    return

#==============================================================================
if __name__ == '__main__':
    text="MRQ个股流通市值均值"
    text=["开盘价","收盘价"]
    to_language='en'
    list_sep='!'
    printout=False
    
    translate_text_google(text=["开盘价","收盘价"])
    translate_text_google(text="证券趋势对比")
    translate_text_google(text="市盈率")
    translate_text_google(text="MRQ个股流通市值均值")

def translate_text_google(text,to_language='en',list_sep='!',printout=False):
    """
    功能：联网翻译，最终都是使用谷歌翻译
    """
    from py_trans import PyTranslator
    #需要谷歌翻译联网
    try:
        tr = PyTranslator()
    except:
        if printout:
            print("  #Warning(translate_text_google): translation failed as of no internet connection to Google")
        return text
    
    #检测语言
    #lang=tr.detect(text)
    
    #处理列表
    text1=text
    list_type=False
    if isinstance(text,list):
        list_type=True
        text1=list_sep.join(text)
    
    success=False
    #Translate text using Google
    tresult=tr.google(text1,to_language)
    if tresult['status']=='success':
        success=True
    
    #Translate text using My Memory
    if not success:
        tresult=tr.my_memory(text1,to_language)
        if tresult['status']=='success':
            success=True
    
    #Translate text using My Memory
    if not success:
        tresult=tr.translate_dict(text1,to_language)
        if tresult['status']=='success':
            success=True
    
    #Translate text using Translate.com
    if not success:
        tresult=tr.translate_com(text1,to_language)
        if tresult['status']=='success':
            success=True
            
    if success:            
        to_text=tresult['translation']
    else:
        to_text=text
        
    #处理列表
    if list_type:
        to_text=to_text.split(list_sep)
        
        to_text2=[]
        for t in to_text:
            tt=firstLetterUpper(t.strip())
            to_text2=to_text2 + [tt]
            
        return to_text2
    else:
        return firstLetterUpper(to_text)
    

#==============================================================================
if __name__ == '__main__':
    text="MRQ close price"    
    
def firstLetterUpper(text):
    """
    功能：把英文一句话中每个单词的第一个字母大写，但不改变其余字母的大小写
    """    
    text_list=text.split(' ')
    utext_list=[]
    for t in text_list:
        tt=t[0].upper() + t[1:]
        utext_list=utext_list + [tt]
        
    utext=' '.join(utext_list)

    return utext


#==============================================================================
if __name__ == '__main__':
    long_text = "Hello, this is a test string."
    short_text = "test strng"
     
    similar_substring, similarity = find_similar_substring(long_text, short_text)
    if similarity:
        print(f"Similar substring found: {similar_substring}, Similarity: {similarity}")
    else:
        print("No similar substring found.")

 
def find_similar_substring(long_string, short_string, threshold=0.7):
    """
    
    功能：判断一个字符串中是否存在与另一个字符串相似度较高的子串
    注意：尚未测试
    """
    
    import difflib
    
    # 使用SequenceMatcher比较字符串
    matcher = difflib.SequenceMatcher(None, long_string, short_string)
    
    # 遍历所有可能的子串长度
    for size in range(len(short_string), len(long_string) + 1):
        for start in range(0, len(long_string) - size + 1):
            # 获取子串并计算相似度
            substring = long_string[start:start + size]
            similarity = matcher.ratio()
            
            # 如果相似度超过阈值，返回子串
            if similarity > threshold:
                return substring, similarity
    
    # 如果没有找到相似度较高的子串，返回None
    return None, None   

    
#==============================================================================
if __name__ == '__main__':
    str1 = "kitten"
    str2 = "sitting"
    
    string_similarity(str1,str2)
    

def string_similarity(str1,str2,ignore_cases=True):
    """
    
    功能：计算两个字符串的文本相似度
    """
    import difflib
    
    if ignore_cases:
        string1=str1.lower()
        string2=str2.lower()
    else:
        string1=str1
        string2=str2
    
    # 创建SequenceMatcher对象
    matcher = difflib.SequenceMatcher(None, string1, string2)
    
    # 计算相似度
    similarity = matcher.ratio()
    #print(f"SequenceMatcher Similarity: {similarity:.2f}")

    return similarity

#==============================================================================
if __name__ == '__main__':
    string = "HeLLo, Welcome to this New WorLd!"
    words = ["Hello", "World"]

    contains_any(string, words)

def contains_any(string, words):
    """
    
    功能：测试字符串string中是否含有字符串列表words中的任意一个元素，忽略字母大小写
    参数：
    string：字符串，大小写不限
    words：字符串列表，大小写不限
    注意：为避免大小写字母的影响，比较前需要先将两边的字母全部小写化
    """
    #将字符串列表中的元素小写，避免大小写差异导致比较失败
    if not isinstance(words,list):
        words_list=[words]
    else:
        words_list=words
    new_words=words_list.copy() #不改变原列表的内容
    
    new_words_list=[]
    for w in new_words:
        if isinstance(w,str):
            new_words_list=new_words_list+[w.lower()]
        else: continue #过滤列表中非字符串的元素
        
    if isinstance(string,str):
        new_string=string.lower()
    else:
        return False
    
    #检查字符串new_string是否包含列表new_words_list中的任何元素
    return any((word in new_string) for word in new_words_list)    

#==============================================================================
if __name__ == '__main__':
    string = "HeLLo, Welcome to this New WorLd!"
    words = ["Hello", "World"]
    words = ["Hello", "World","the"]

    contains_all(string, words)

def contains_all(string, words):
    """
    
    功能：测试字符串string中是否含有字符串列表words中的全部元素，忽略字母大小写
    参数：
    string：字符串，大小写不限
    words：字符串列表，大小写不限
    注意：为避免大小写字母的影响，比较前需要先将两边的字母全部小写化
    """
    
    result=True
    for w in words:
        if not contains_any(string,w):
            result=False
            break
        
    return result


#==============================================================================
if __name__ == '__main__':
    alist = ["CurrentDebt",
            "CurrentDebtAndCapitalLeaseObligation",
            "CurrentDeferredLiabilities",
            "CurrentLiabilities",
            "OtherCurrentBorrowings",
            "OtherCurrentLiabilities",
            "OtherNonCurrentLiabilities",
            "TotalNonCurrentLiabilitiesNetMinorityInterest"]

    alist = [
            "CurrentDebtAndCapitalLeaseObligation",
            "CurrentDeferredLiabilities",
            "CurrentLiabilities",
            "OtherCurrentBorrowings",
            "OtherCurrentLiabilities",
            "OtherNonCurrentLiabilities",
            "TotalNonCurrentLiabilitiesNetMinorityInterest"]
    
    item_words = ["Current", "Debt"]
    item_words = ["Current", "Liabilities"]
    
    perfect_match=True

    list_contains_all(alist, item_words)

def list_contains_all(alist, item_words,perfect_match=True):
    """
    
    功能：测试列表alist中是否有元素含有字符串列表item_words中的全部元素，忽略字母大小写
    参数：
    alist：字符串列表，大小写不限
    item_words：字符串列表，大小写不限
    注意：为避免大小写字母的影响，比较前需要先将两边的字母全部小写化
    返回值：
        若列表alist中有多个元素含有字符串列表item_words中的全部元素，返回相似度最高的元素
        若无则返回False
    """
    DEBUG=False
    
    #将item_words合成为一个字符串，以便比较相似度
    words=''
    for w in item_words:
        words=words+w
    if DEBUG:
        print(f"  DEBUG: item_words={item_words}, words={words}")
    
    result=False
    best_similarity=0
    for e in alist:
        similarity=0
        
        if DEBUG:
            print(f"  DEBUG: e={e}")
            
        if perfect_match: #要求e精确含有item_words中的每个元素
            if contains_all(e,item_words):
                similarity=string_similarity(e,words)
        else:
            similarity=string_similarity(e,words)
            
        if DEBUG:
            print(f"  DEBUG: item_words={item_words}, e={e}, similarity={similarity}")
        
        if similarity > best_similarity:
            best_similarity=similarity
            result=e
                
        
    return result,best_similarity

if __name__ == '__main__':
    alist = ["CurrentDebt",
            "CurrentDebtAndCapitalLeaseObligation",
            "CurrentDeferredLiabilities",
            "CurrentLiabilities",
            "OtherCurrentBorrowings",
            "OtherCurrentLiabilities",
            "OtherNonCurrentLiabilities",
            "TotalNonCurrentLiabilitiesNetMinorityInterest"]

    alist = [
            "CurrentDebtAndCapitalLeaseObligation",
            "CurrentDeferredLiabilities",
            "CurrentLiabilities",
            "OtherCurrentBorrowings",
            "OtherCurrentLiabilities",
            "OtherNonCurrentLiabilities",
            "TotalNonCurrentLiabilitiesNetMinorityInterest"]
    
    item_words_list=[["Current","Debt"],["Current","Liabilities"]]
    item_words_list=[["Current","Liabilibities"],["Current","Debt"]]
    
    list_contains_all_list(alist, item_words_list)
    
def list_contains_all_list(alist, item_words_list):
    """
    
    功能：测试列表alist中是否有元素含有字符串列表组中item_words_list各个item_words中的全部元素，忽略字母大小写
    参数：
    alist：字符串列表，大小写不限
    item_words_list：字符串列表组，大小写不限。第1个为最佳字符串列表，后面可跟多个替代最佳字符串列表
    注意：为避免大小写字母的影响，比较前需要先将两边的字母全部小写化
    返回值：
        若列表alist中有多个元素含有字符串列表item_words中的全部元素，返回相似度最高的元素
        若出现多个最高相似度相同的，则返回第一个
        若无则返回False
    """
    DEBUG=False
    
    best_result=False
    best_similarity=0
    
    for iwords in item_words_list:
        result,similarity=list_contains_all(alist, iwords,perfect_match=False)
        if DEBUG:
            print("  DEBUG: iwords={0}, alist={1}".format(iwords,alist))
            #print("  DEBUG: result={0}, similarity={1}".format(result,similarity))
            print('')
            print(f"  DEBUG: result={result}, similarity={similarity:.2f}")
        
        if similarity > best_similarity:
            best_similarity=similarity
            best_result=result
        
    return best_result


#==============================================================================
if __name__ == '__main__':
    max_sleep=30

    sleep_random(max_sleep)

def sleep_random(max_sleep=30):
    """
    
    功能：随机睡眠秒数，以防被数据源封堵IP地址，适用于连续抓取同种信息时。
    参数：
    max_sleep：最大挂起秒数，默认30秒。随机挂起1-30秒。
    """
    
    import time; import random
    
    random_int=random.randint(1,max_sleep)
    time.sleep(random_int)

    return
    
#==============================================================================
if __name__ == '__main__':
    s = "Hello, 世界! This is a test string with symbols #$%^&*()."

    cleaned_s = remove_symbols(s)
 
def remove_symbols(s):
    """
     
    功能：删除字符串中除字母、数字和汉字外的所有符号
    """
    import re
    # 正则表达式匹配字母、数字和汉字
    pattern = re.compile(r'[^\w\u4e00-\u9fa5]')
    # 使用sub()函数将所有不匹配的符号替换为空字符
    return pattern.sub('', s)


#==============================================================================
if __name__ == '__main__':
    swcy = ['宁德时代(300750.SZ)',
            '东方财富(300059.SZ)',
            '阳光电源(300274.SZ)',
            '迈瑞医疗(300760.SZ)',
            '中际旭创(300308.SZ)',
            '汇川技术(300124.SZ)',
            '温氏股份(300498.SZ)',
            '新易盛(300502.SZ)',
            '爱尔眼科(300015.SZ)',
            '亿纬锂能(300014.SZ)',
            '三环集团(300408.SZ)',
            '智飞生物(300122.SZ)',
            '同花顺(300033.SZ)',]
    sw50 = ['贵州茅台(600519.SS)',
            '宁德时代(300750.SZ)',
            '中国平安(601318.SS)',
            '美的集团(000333.SZ)',
            '招商银行(600036.SS)',
            '五粮液(000858.SZ)',
            '紫金矿业(601899.SS)',
            '比亚迪(002594.SZ)',
            '中信证券(600030.SS)',
            '东方财富(300059.SZ)',]
    lists=[swcy,sw50]

    list2_intersection(swcy,sw50)
    
def list2_intersection(list1,list2):
    #寻找两个列表的共同元素
    result=[]
    for i in list1:
        if i in list2:
            result=result+[i]
            
    return result

if __name__ == '__main__':
    list1 = [1,2,3,4,5,6,7,8,9,10]
    list2 = [4,5,6,7,8,9,10,11,12]
    list3 = [5,6,7,8,9,10,11,12,13]
    
    lists = [list1,list2,list3]
    numberPerLine=5; printout=True; return_result=False
    
    list_intersection(lists) 
    
    list_intersection([swcy,sw50])

def list_intersection(lists=[],numberPerLine=5,printout=True,return_result=False):
    # 求多个列表的共同元素，即其交集，通过转化为集合求得。注意集合是无序的，谨慎使用！
    
    if len(lists)==0:
        print("  #Warning(list_intersection): no list found for intersection")
        if return_result: return []
        else: return
    
    if len(lists)==1:
        if return_result: return lists[0]
        else: return 
        
    list1=lists[0]; list2=lists[1]
    result=list2_intersection(list1,list2)
    
    for l in lists[2:]:
        result=list2_intersection(result,l)
        
    """
    #貌似也没问题
    result=[]
    for l in lists:
        if result==[]:
            result=l
        else:
            result=list2_intersection(result,l)
    """

    if len(result) == 0:
        if printout:
            print("  #Warning(list_intersection): intersection result is empty")
        if return_result: return result
        else: return
    else:
        if printout:
            prompt_text=text_lang("\n*** 交集成份：","\n*** Intersection result: ")

            if len(result) < numberPerLine:
                print(prompt_text,end='')
                for e in result:
                    print(e,end=' ')
                print('')
            else:
                print(prompt_text+str(len(result)),end='')
                printInLine_md(result,numberPerLine=numberPerLine,colalign="center")
            
    if return_result: return result
    else: return
                        
#==============================================================================
if __name__ == '__main__':
    hpr=3.17
    years=20
    
    annual_return1(hpr,years)
    
def annual_return1(hpr,years):
    """
    功能：计算年均复合增长率，1个
    """
    #text1="Holding period return for "+str(years)+" years: "+str(hpr*100)+'%'
    text1=str(years)+"年的持有期收益率："+str(round(hpr*100,3))+'%'
    print(text1,end='，')
    
    #text2="Annualized compound return:"
    text2="年均复合收益率："+str(round((pow(1+hpr,1/years)-1)*100,3))+'%'
    print(text2)
    
    return

if __name__ == '__main__':
    hpr=3.17
    hpr=[3.17,2.5]
    years=20
    
    annual_return(hpr,years)

def annual_return(hpr,years):
    """
    功能：hpr可为多个
    """
    if isinstance(hpr,float) or isinstance(hpr,int):
        hpr=[hpr]
        
    for h in hpr:
        annual_return1(h,years)
        
    return

if __name__ == '__main__':
    df=security_trend(['801811.SW','801813.SW'],
                      indicator='Exp Adj Ret%',
                      start='L5Y',
                      annotate=True,annotate_value=True)
    
    df_annual_return(df)
    
def df_annual_return(df):
    """
    功能：计算df1中每列的年复合收益率
    """
    
    #计算年数
    date1=df.index[0]
    date2=df.index[-1]
    delta=date2-date1
    years=round(delta.days/365,2)
    months=int(delta.days/30)

    #计算每列的年均复合增长率   
    collist=list(df)
    for c in collist:
        hpr=df[c][-1]
        hpr1=hpr/100
        annual_rate=str(round((pow(1+hpr1,1/years)-1)*100,3))+'%'
        
        if years >=1:
            text=c+": "+str(years)+"年持有期收益率"+str(round(hpr,3))+'%，年均复合收益率'+annual_rate
        else:
            text=c+": "+str(months)+"个月持有期收益率"+str(round(hpr,3))+'%，年均复合收益率'+annual_rate
        print(text)
        
    return

#==============================================================================

if __name__ == '__main__':
    df=security_trend("600519.SS",graph=False)
    option="save"
    
    df_save(df,file="moutai")
    mt=df_restore(file="moutai")
    
def df_save(df,file="df"):
    """
    功能：保存df数据，适用于那些需要大量时间获取的df，以便使用时可以恢复
    """
    
    if ".pkl" in file:
        file_name=file
    else:
        file_name=file+'.pkl'
    
    try:        
        df.to_pickle(file_name)
        
        import os; path=os.getcwd()
        print("  Saved to",path+"\\"+file_name)
    except:
        print("  #Error(df_save): failed to save data to file",file_name)
        
    return
        
def df_restore(file):
    """
    功能：从文件恢复df数据，适用于那些需要大量时间获取的df
    """
    
    import pandas as pd
    
    if ".pkl" in file:
        file_name=file
    else:
        file_name=file+'.pkl'
    
    try:
        df=pd.read_pickle(file_name)
        
        import os; path=os.getcwd()
        print("  Data is restored from file",path+"\\"+file_name)
    except:
        print("  #Error(df_restore): file not found for",file_name)
        df=None
    return df
            

#==============================================================================
if __name__ == '__main__':
    df=security_trend("600519.SS",start="L5Y",graph=False)
    column='Close'
    
    annual_compound_growth(df,"Close")
    annual_compound_growth(df,"High")
    
def annual_compound_growth(df,column="Close"):
    """
    
    功能：计算df[column]的简单年均复合增长率，假定df按照日期顺序升序排列
    适用于计算长期股价/指数的年均复合增长率，不适用于收益率的年均复合增长率计算
    """
    if not column in list(df):
        print("  Sorry, column",column,"not found in the dataframe")
        return
    
    day1=df.index[0]; day2=df.index[-1]
    days=days_between_dates(day1, day2)
    
    years=days / 365
    
    import numpy as np  
    growth_rate=round((np.power(df[column][-1]/df[column][0],1/years)-1)*100,3)
    rate_str=str(growth_rate)+'%'
    
    day1str=day1.strftime("%Y-%m-%d"); day2str=day2.strftime("%Y-%m-%d")
    print("Annualized compound growth",rate_str,"from",day1str,"to",day2str)
    
    return 
#==============================================================================
#==============================================================================
if __name__ == '__main__':
    sample1=[1,2,3]
    sample2=0
    
    ttest(sample1,sample2)
    

def ttest(sample1,sample2):
    """
    
    功能：对比sample1与sample2之间是否存在显著差异，配对学生检验
    sample1：可为数值型的列表或序列，不可为空
    sample2：可为数值型的列表或序列或单个数值，若为列表或序列需与sample1个数相同
    """
    import pandas as pd
    import numpy as np
    from scipy import stats
    
    #检查与预处理
    if not (isinstance(sample1,list) or isinstance(sample1,pd.Series)):
        print("  #Error(ttest): sample1 must be a list or series",sample1)
        return None
    
    if not (isinstance(sample2,list) or isinstance(sample2,pd.Series)):
        if isinstance(sample2,int) or isinstance(sample2,float):
            sample2=[sample2]
            sample2=[item for s in sample2 for item in [s]*len(sample1)]           
        else:
            print("  #Error(ttest): sample2 must be a list or series or a value",sample2)
            return None
    
    
    # 转换样本数据
    sample1 = pd.Series(sample1)
    sample1=sample1.astype(float)
    sample1 = np.array(sample1)
    
    sample2 = pd.Series(sample2)
    sample2=sample2.astype(float)
    sample2 = np.array(sample2)
     
    # 执行t检验
    t_stat, p_value = stats.ttest_ind(sample1, sample2)
    
    return round(p_value,4)

#==============================================================================
import sys,os

# —— 在程序最开始处，打印并校验 Python 版本 —— 
def _check_python_version_jupyter2pdf():
    ver = sys.version_info
    version_str = f"{ver.major}.{ver.minor}.{ver.micro}"
    #print(f"使用的 Python 版本：{version_str}")

    # 只允许 3.7 <= 版本 < 3.13
    usable=True
    if not (ver.major == 3 and 7 <= ver.minor <= 12):
        usable = False
        print(f"不支持的 Python 版本：{version_str}，仅支持 Python 3.7–3.12")
        print(f"解决方案：改用ipynb2pdf或ipynb2docx")
        """
        raise RuntimeError(
            f"不支持的 Python 版本：{version_str}。"
            " 请使用 Python 3.7–3.12。"
        )
        """

    return usable

async def jupyter2pdf(notebook_path, output_pdf_path, size="A3"):
    """
    将 Jupyter Notebook 转换为 PDF 文件
    参数:
        notebook_path (str): Jupyter Notebook文件（.ipynb文件，含路径）
        output_pdf_path (str): 输出的PDF文件（含路径）
        size：PDF页面大小，默认"A3"幅面，支持"A4"幅面
        
    返回:
        None
    注意1：pip install playwright之后可能还要执行playwright install
    注意2：调用本函数的格式是异步await开头
    await convert_notebook_to_pdf(notebook_path, output_pdf_path)
    注意3：notebook_path和output_pdf_path中可以带路径
    """
    if not _check_python_version_jupyter2pdf():
        return
    
    size=size.upper()
    if not size in ['A4','A3','letter']:
        size='A3'
    
    import os
    from nbconvert import HTMLExporter
    from playwright.async_api import async_playwright
    
    html_file = ""
    
    try:
        # 导出 Notebook 为 HTML
        html_exporter = HTMLExporter()
        try:
            html_content, _ = html_exporter.from_filename(notebook_path)
            print("Start to convert ipynb file to pdf in {} size, ...".format(size))

        except:
            print("File not found for {}".format(notebook_path))
            return
        
        # 创建临时 HTML 文件
        html_file = "temp_notebook.html"
        with open(html_file, "w", encoding="utf-8") as f:
            f.write(html_content)

        # 使用 Playwright 打开 HTML 并保存为 PDF
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            page = await browser.new_page()
            await page.goto(f"file://{os.path.abspath(html_file)}")
            await page.pdf(path=output_pdf_path, format=size)
            await browser.close()

        print(f"PDF created as {output_pdf_path}")

    except Exception as e:
        print(f"Conversion failed: {e}")
        return
    
    finally:
        if html_file == "":
            return
        # 删除临时 HTML 文件
        elif os.path.exists(html_file):
            os.remove(html_file)    
    
    return
    
if __name__ == '__main__':
    # 定义 Notebook 路径和输出 PDF 路径
    notebook_path = r"S:\SIA\机工社版本\脚本测试\证券投资分析-第一章案例Python脚本-检测2.ipynb"  # 替换为你的 Notebook 文件路径
    output_pdf_path = "E:/output_notebook.pdf"  # 替换为你想保存的 PDF 文件路径
    #await jupyter2pdf(notebook_path, output_pdf_path)
    # 注意：上面的await命令会导致编译失败，测试后要注释掉

#==============================================================================
if __name__ == '__main__':
    # 定义 Notebook 路径和输出 PDF 路径
    notebook_dir = r"E:\北外工作-25春\SICA-BFSU\Session 2"  # 替换为你的 Notebook 文件路径
    notebook_file= r"Session 2-Market index v3en"  # 替换为你想保存的 PDF 文件路径
    
async def jupyter2pdf2(notebook_dir, notebook_file):
    """
    ===========================================================================
    将 Jupyter Notebook 转换为 PDF 文件，异步方式。
    主要参数:
    notebook_dir (str): Jupyter Notebook文件所在的目录，不含文件名
    notebook_file (str): Jupyter Notebook文件名
    
    输出：
        同时生成A4和A3两种幅面的pdf文件，由使用者自行挑选一个效果最好的。        
    返回:
        None
        
    注意1：如果指令异常，可能还要执行python -m playwright install
    注意2：调用本函数的格式是异步await开头，例如：
    await jupyter2pdf2(notebook_dir, notebook_file)
    """
    if not _check_python_version_jupyter2pdf():
        return
    
    # 路径分割符号
    if ('/' in notebook_dir) and not ('\\' in notebook_dir):
        sep='/'
    else:
        sep='\\'
    
    #import os; sep=os.sep
    
    # ipynb文件的完整路径
    if ('.ipynb' in notebook_file):
        notebook_file1=notebook_file.replace('.ipynb','')
    else:
        notebook_file1=notebook_file
    notebook_path=notebook_dir+sep+notebook_file1+'.ipynb'
    
    # pdf文件的完整路径        
    output_pdf_path1=notebook_dir+sep+notebook_file1+' A4.pdf'
    output_pdf_path2=notebook_dir+sep+notebook_file1+' A3.pdf'
    
    from nbconvert import HTMLExporter
    
    """
    import nest_asyncio
    nest_asyncio.apply()  # 修复 Notebook 的事件循环问题
    """
    
    try:
        from playwright.async_api import async_playwright
        #from playwright.sync_api import sync_playwright
    except:
        print("  #Warning(jupyter2pdf2): playwright seems not fully installed yet")
        print("  [Solution] execute the command before re-run: playwright install")
        return
    
    html_file = ""
    
    try:
        # 导出 Notebook 为 HTML
        html_exporter = HTMLExporter()
        try:
            html_content, _ = html_exporter.from_filename(notebook_path)
            print("Converting notebook file to pdf in both A4 and A3 sizes ...")

        except:
            print("File not found for {}".format(notebook_path))
            return
        
        # 创建临时 HTML 文件
        html_file = "temp_notebook.html"
        with open(html_file, "w", encoding="utf-8") as f:
            f.write(html_content)

        # 使用 Playwright 打开 HTML 并保存为 PDF
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            page = await browser.new_page()
            await page.goto(f"file://{os.path.abspath(html_file)}")
            
            # 避免加载html文件超时，用于macOS
            if not sys.platform.startswith('win'):
                page.wait_for_selector(".jp-Notebook", state="visible", timeout=60000)  # 等待笔记本主体出现
            
            await page.pdf(path=output_pdf_path1, format='A4')
            await page.pdf(path=output_pdf_path2, format='A3')
            
            await browser.close()
        """
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()
            page.goto(f"file://{os.path.abspath(html_file)}")
            
            # 避免加载html文件超时，用于macOS
            if not sys.platform.startswith('win'):
                page.wait_for_selector(".jp-Notebook", state="visible", timeout=60000)  # 等待笔记本主体出现
            
            page.pdf(path=output_pdf_path1, format='A4')
            page.pdf(path=output_pdf_path2, format='A3')
            
            browser.close()
        """
        
        print(f"2 PDFs created in the same directory, pick 1 you think best")

    except Exception as e:
        if str(e)=='':
            e="because of issues in your playwright or Python environment"
        print(f"PDF conversion failed {e}")
        return
    
    finally:
        if html_file == "":
            return
        # 删除临时 HTML 文件
        elif os.path.exists(html_file):
            os.remove(html_file)    
    
    return
    
if __name__ == '__main__':
    # 替换为你的Notebook文件路径
    notebook_dir = r"S:\北外工作-25春\周4.财经与生活附校\Session 1"  
    # 替换为你想转存PDF的Notebook文件名
    notebook_file = "Session 1 全球证券市场-简化版.ipynb"  
    #await jupyter2pdf2(notebook_dir, notebook_file)
    # 注意：上面的await命令会导致编译失败，测试后要注释掉

#==============================================================================


async def jupyter2pdf3(notebook_path):
    """
    ===========================================================================
    将 Jupyter Notebook 转换为 PDF 文件，异步方式。
    主要参数:
    notebook_path: Jupyter Notebook文件的完整路径，包括所在的目录和文件名
        获取方法：在Jupyter Notebook中执行下列命令(仅在交互环境中工作)
            notebook_path=globals().get("__session__")
    输出：
        同时生成A4和A3两种幅面的pdf文件，由使用者自行挑选一个效果最好的。        
    返回:
        None
        
    注意1：如果指令异常，可能还要执行python -m playwright install
    注意2：调用本函数的格式是异步await开头，例如：
    await jupyter2pdf3(notebook_path)
    """
    DEBUG=False

    if not _check_python_version_jupyter2pdf():
        return
    
    import os,sys
    # 分离目录和文件名
    notebook_dir, notebook_file = os.path.split(notebook_path)
    
    if DEBUG:
        print("目录路径：", notebook_dir)    # 输出：/Users/peterwang/Documents/project
        print("文件名：", notebook_file)     # 输出：data.csv
        
        # 如果还想拆出文件名和扩展名
        name_only, ext = os.path.splitext(notebook_file)
        print("文件名（不含扩展名）：", name_only)  # 输出：data
        print("扩展名：", ext)                       # 输出：.csv
    
    # 路径分割符号
    if ('/' in notebook_dir) and not ('\\' in notebook_dir):
        sep='/'
    else:
        sep='\\'
    
    #import os; sep=os.sep
    
    # ipynb文件的完整路径
    if ('.ipynb' in notebook_file):
        notebook_file1=notebook_file.replace('.ipynb','')
    else:
        notebook_file1=notebook_file
    notebook_path=notebook_dir+sep+notebook_file1+'.ipynb'
    
    # pdf文件的完整路径        
    output_pdf_path1=notebook_dir+sep+notebook_file1+' A4.pdf'
    #output_pdf_path2=notebook_dir+sep+notebook_file1+' A3.pdf'
    output_pdf_path2=notebook_dir+sep+notebook_file1+'.pdf'
    
    from nbconvert import HTMLExporter
    
    """
    import nest_asyncio
    nest_asyncio.apply()  # 修复 Notebook 的事件循环问题
    """
    
    try:
        from playwright.async_api import async_playwright
        #from playwright.sync_api import sync_playwright
    except:
        print("  #Warning(jupyter2pdf3): playwright seems not fully installed yet")
        print("  [Solution] execute the command before re-run: playwright install")
        return
    
    html_file = ""
    
    try:
        # 导出 Notebook 为 HTML
        html_exporter = HTMLExporter()
        try:
            html_content, _ = html_exporter.from_filename(notebook_path)
            #print(f"Converting {notebook_file} to pdf ...")
            print(f"Converting from {notebook_file} ...")

        except:
            print("Source file not found from {}".format(notebook_path))
            return
        
        # 创建临时 HTML 文件
        html_file = "temp_notebook.html"
        with open(html_file, "w", encoding="utf-8") as f:
            f.write(html_content)

        # 使用 Playwright 打开 HTML 并保存为 PDF
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            page = await browser.new_page()
            await page.goto(f"file://{os.path.abspath(html_file)}")
            
            # 避免加载html文件超时，用于macOS
            if not sys.platform.startswith('win'):
                page.wait_for_selector(".jp-Notebook", state="visible", timeout=60000)  # 等待笔记本主体出现
            
            #await page.pdf(path=output_pdf_path1, format='A4')
            await page.pdf(path=output_pdf_path2, format='A3')
            
            await browser.close()
        """
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()
            page.goto(f"file://{os.path.abspath(html_file)}")
            
            # 避免加载html文件超时，用于macOS
            if not sys.platform.startswith('win'):
                page.wait_for_selector(".jp-Notebook", state="visible", timeout=60000)  # 等待笔记本主体出现
            
            page.pdf(path=output_pdf_path1, format='A4')
            page.pdf(path=output_pdf_path2, format='A3')
            
            browser.close()
        """
        
        #print(f"2 PDFs created in {notebook_dir}")
        print(f"PDF created in {notebook_dir}")

    except Exception as e:
        if str(e)=='':
            e="because of issues in your playwright or Python environment"
        print(f"PDF conversion failed {e}")
        return
    
    finally:
        if html_file == "":
            return
        # 删除临时 HTML 文件
        elif os.path.exists(html_file):
            os.remove(html_file)    
    
    return
    
#==============================================================================
if __name__ == '__main__':
    df=security_trend("600519.SS",indicator=['Close','Open','High','Low'],graph=False)
    col_name='持股总数'; position=3

    df=shift_column_position(df,col_name='Low',position=0)
    
def shift_column_position(df,col_name,position=1):
    """
    功能：将df中的字段col_name挪动到位置position，其余字段不动。
    注意：位置顺序从0开始。
    """
    # 获取所有列名
    columns = df.columns.tolist()
    if col_name not in columns:
        raise ValueError(f"  #Warning: column '{col_name}' does not exist in the DataFrame.")
        return df
    
    # 移除要移动的列
    columns.remove(col_name)
    
    # 插入到指定位置
    columns.insert(position, col_name)
    
    # 重新排列 DataFrame
    df = df[columns]
    
    return df
#==============================================================================
if __name__ == '__main__':
    text='accountsReceivable'
    text='periodType'
    text='reportDate'
    text='currencyCode'
    text='BasicEPS'
    text='EBITDA'
    text='CashAndCashEquivalents'
    text='Debt to Asset'
    
    text_separate(text)

def text_separate(text):
    """
    功能：将连写在一起的专业术语拆分成为正常的形式
    参数：
    text：待拆分短语，例如accountsReceivable
    输出：拆分后短语，例如Accounts Receivable
    """
    DEBUG=False
    
    if not text:
        return ""
    
    articles={"and","from","in","on","the","of","to","for","not","non","as","per"}
    
    words = []
    current_word = [text[0].upper()]  # 首字母默认大写
    for i in range(1, len(text)):
        prev_char, curr_char = text[i-1], text[i]
        
        # 分割条件：当前大写且前一个字符为小写，或当前大写后跟小写（保留连续大写）
        if (curr_char.isupper() and prev_char.islower()) or \
           (curr_char.isupper() and prev_char.isupper() and i < len(text)-1 and text[i+1].islower()):
            words.append(''.join(current_word))
            current_word = [curr_char]
        else:
            current_word.append(curr_char)
    words.append(''.join(current_word))
    
    # 处理虚词：除首单词外，虚词首字母小写
    formatted_words = [words[0]]
    for word in words[1:]:
        lower_word = word.lower()
        formatted_words.append(lower_word if lower_word in articles else word)
    
    words2=' '.join(formatted_words)
    
    if DEBUG:
        print(f"BEFORE: {text}, AFTER: {words2}")
        
    return words2
    
#==============================================================================
if __name__ == '__main__':
    alist=['a','b','c']
    element='b'
    element='c'
    
    last_in_list(element,alist)

def last_in_list(element,alist):
    """
    功能：测试element是否alist的最后一个元素
    参数：
    element：alist的元素，用于循环
    alist：列表，用于循环
    """
    result=False
    if alist.index(element) == len(alist)-1:
        result=True
        
    return result
#==============================================================================
if __name__ == '__main__':
    ticker='600519.SS'
    ticker='09998.HK'
    ticker='AAPL'
    
    is_A_share(ticker)

def is_A_share(ticker):
    """
    功能：判断是否中国A股
    ticker：单个股票代码
    返回值：True, False
    """
    if not isinstance(ticker,str):
        return False
    
    tlist=ticker.split('.')
    if len(tlist) < 2:
        return False
    
    # SUFFIX_LIST_CN=['SS','SZ','BJ','SW','SH']
    if tlist[1] in SUFFIX_LIST_CN:
        return True
    else:
        return False
    
    
#==============================================================================

def print2CSS(data_dict, \
              titletxt='',footnote='',facecolor='papayawhip',decimals=2, \
              hide_columns=True,
              first_col_align='left',second_col_align='right', \
              last_col_align='right',other_col_align='right', \
              titile_font_size='14px',heading_font_size='14px', \
              data_font_size='14px',footnote_font_size='11px'):
    """
    功能：将字典中的数据转化为df，使用CSS形式实现整齐输出
    """
    import pandas as pd
    disp_df=pd.DataFrame(columns=['Item','Value'])    
    
    keys=list(data_dict.keys())
    for key in keys:
        value=data_dict[key]
        
        s=pd.Series({'Item':key,'Value':value}) 
        disp_df=disp_df._append(s,ignore_index=True)        

    df_display_CSS(disp_df,titletxt=titletxt,footnote=footnote, \
                   facecolor=facecolor,decimals=decimals, \
                       hide_columns=hide_columns,
                   first_col_align=first_col_align,second_col_align=second_col_align, \
                   last_col_align=last_col_align,other_col_align=other_col_align, \
                   titile_font_size=titile_font_size,heading_font_size=heading_font_size, \
                   data_font_size=data_font_size,footnote_font_size=footnote_font_size)
        
    return

#==============================================================================
    
import datetime as dt
import pandas_market_calendars as mcal

def adjust_to_workday(tradedate,exchange='SSE'):
    """
    将输入日期调整为最近的工作日（以上海证券交易所交易日为准）
    :param tradedate: 输入日期（datetime.date或str类型，如'2023-10-01'）
    :return: 调整后的工作日（datetime.date类型）
    """
    # 转换输入为date类型
    if isinstance(tradedate, str):
        tradedate = dt.datetime.strptime(tradedate, '%Y-%m-%d').date()
    
    # 获取上海证券交易所日历
    sh_exchange = mcal.get_calendar(exchange)  # SSE代表上海证券交易所
    # 检查日期是否为交易日
    is_trading_day = sh_exchange.valid_days(start_date=tradedate, end_date=tradedate).size > 0
    
    if is_trading_day:
        return str(tradedate)
    else:
        # 向前寻找最近的工作日
        delta = 1
        while True:
            prev_day = tradedate - dt.timedelta(days=delta)
            if sh_exchange.valid_days(start_date=prev_day, end_date=prev_day).size > 0:
                return str(prev_day)
            delta += 1

# 示例用法
if __name__ == "__main__":
    test_dates = ['2023-10-01', '2023-10-07', '2023-12-30', dt.date(2024, 2, 10)]
    for date_str in test_dates:
        adjusted_date = adjust_to_workday(date_str)
        print(f"原始日期: {date_str} -> 调整后工作日: {adjusted_date}")
        
    tradedate='2025-8-2'
    tradedate='2025-8-1'
    adjust_to_workday(tradedate)
#==============================================================================
#==============================================================================
#==============================================================================
#==============================================================================
#==============================================================================
#==============================================================================
#==============================================================================

