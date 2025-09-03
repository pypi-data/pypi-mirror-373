# -*- coding: utf-8 -*-
"""
版权：王德宏，北京外国语大学国际商学院
功能：Fama-French股票市场资产定价因子（中国大陆市场为估计值）
版本：2.1，2019-10-10
"""
#==============================================================================
#关闭所有警告
import warnings; warnings.filterwarnings('ignore')
#==============================================================================
from siat.common import *
from siat.translate import *
from siat.security_prices import *
from siat.security_price2 import *
#==============================================================================
import matplotlib.pyplot as plt

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
#==============================================================================
def convert2freq(df,new_freq='daily'):
    """
    功能：将月度或年度频度的数据均匀化为日度数据
    """
    dfcols=list(df)
    
    import pandas as pd
    df['datetmp']=df.index
    df['Date']=df['datetmp'].apply(lambda x: x.to_timestamp())
    df.set_index('Date',inplace=True)
    #df['Date']=df['date']
    if not isinstance(df.index, pd.DatetimeIndex):
        df.index = pd.to_datetime(df.index)
    
    if new_freq == 'daily':
        df = df.asfreq('D')
    elif new_freq == 'monthly':
        df = df.asfreq('M')
    else:
        df = df.asfreq('Y')
        
    for c in dfcols:
        df[c] = df[c].ffill()
        df[c] = df[c].bfill()
        
    df.drop(columns=['datetmp'], inplace=True)
    
    #df=df[['Date']+dfcols]
    
    return df
#==============================================================================
#==============================================================================        
if __name__=='__main__':
    start='auto'; end='today'
    
    scope='US'
    factor='FF3'
    freq='yearly'
    
    show_ff_factors(ticker='US',indicator='FF3',freq='yearly')

def show_ff_factors(market='US',indicator='FF3', \
                    start='auto',end='today',freq='yearly'):
    """
    功能：套壳函数get_ff3_factors/get_ffc4_factors/get_ff5_factors
    
    【支持的因子种类(factor)】
    FF3: FF3各个因子
    FFC4: FFC4各个因子
    FF5: FF5各个因子

    【支持的国家/地区(scope)】
    US: 美国
    North_America：北美(美国+加拿大)
    Global: 全球
    Global_ex_US: 全球(除美国外)
    Asia_Pacific_ex_Japan: 亚太(除日本外)
    China: 中国
    Japan: 日本
    Europe: 欧洲

    【支持的取样频率(freq)】
    yearly: 年
    monthly: 月
    daily: 日
    """
    ticker=market
    
    indicator1=indicator.lower()
    factorlist=['ff3','ffc4','ff5']
    if not (indicator1 in factorlist):
        print(f"  #Error(show_ff_factors): unsupported factor {indicator}")
        print(f"  Supported factors for FF models: {factorlist}")
        return
    
    import datetime; todaydt = datetime.date.today(); todaystr=str(todaydt)
    if end == 'today': end=todaystr
    
    if start == 'auto':
        if freq == 'yearly':
            start=date_adjust(end,adjust=-365*5)
        elif freq == 'monthly':
            start=date_adjust(end,adjust=-31*8)
        else: #freq=='daily'
            start=date_adjust(end,adjust=-60)
            
    start,end=start_end_preprocess(start,end)
    
    freq=freq.lower()
    if freq == 'daily':
        print("Looking for daily factors, it may take time ...")
    
    if indicator1=='ff3':
        df=get_ff3_factors(start=start,end=end,scope=ticker,freq=freq)
    elif indicator1=='ffc4':
        df=get_ffc4_factors(start=start,end=end,scope=ticker,freq=freq)
    elif indicator1=='ff5':
        df=get_ff5_factors(start=start,end=end,scope=ticker,freq=freq)
    else:
        pass
    
    #处理无数据情形
    if df is None:
        print(f"  #Warning(show_ff_factors): got none data from {start} to {end}")
        print(f"  Suggestion: may specify an earlier start date and try again")
        return
    if len(df) == 0:
        print(f"  #Warning(show_ff_factors): got zero data from {start} to {end}")
        print(f"  Suggestion: may specify an earlier start date and try again")
        return    
    
    #处理RF小数位数
    df['RF']=df['RF'].apply(lambda x: str(round(x,4)))
    
    #titletxt="Asset Pricing Factors: "+indicator.upper()+'Model, '+freq+' @ '+ticker
    titletxt=indicator.upper()+'模型定价因子：'+freq.title()+' @'+ticker
    
    if freq == 'yearly':
        ft0="说明：RF为年化无风险利率%(美短债收益率)"
    elif freq == 'monthly':
        ft0="说明：RF为月度无风险利率%(美短债收益率)"
    else:
        ft0="说明：RF为日频无风险利率%(基于短期美债收益率)"
        
    #footnote="Data source: Dartmouth College, "+todaystr
    footnote=ft0+'\n'+"数据来源：Dartmouth College，"+todaystr
    
    df_display_CSS(df,titletxt=titletxt,footnote=footnote,facecolor='papayawhip', \
                   decimals=2, \
                   first_col_align='center',second_col_align='center', \
                   last_col_align='center',other_col_align='center')    

    return

#==============================================================================        
if __name__=='__main__':
    start='2020-1-1'; end='2025-4-30'
    
    scope='Europe'
    factor='Mom'
    freq='yearly'
        
    scope='US'
    factor='FF3'
    freq='yearly'
    freq='daily'
    
    ff3d=get_ff_factors(start,end,scope,factor,freq='daily')
    ff3mth=get_ff_factors(start,end,scope,factor,freq='monthly')
    ff3y=get_ff_factors(start,end,scope,factor,freq='yearly')

def get_ff_factors(start,end,scope='US',factor='FF3',freq='monthly',retry=10):
    """
    功能：套壳函数get_ff_factors0，应对freq='daily'经常失败的变通方法
    """
    import pandas as pd
    startpd=pd.to_datetime(start)
    endpd=pd.to_datetime(end)
    
    fff=None
    for i in range(retry):
        if not (fff is None): break
        fff=get_ff_factors0(start=start,end=end,scope=scope,factor=factor,freq=freq)
    
    #多次尝试后仍未成功做变通处理：针对日度数据，使用月/年数据均匀化为日度数据
    if fff is None:
        if freq == 'daily':
            start1=date_adjust(start,adjust=-31)
            end1=date_adjust(end,adjust=31)
            fff=get_ff_factors0(start=start1,end=end1,scope=scope,factor=factor,freq='monthly')
            if not (fff is None):
                ff_factors0=convert2freq(fff,new_freq='daily')
                ff_factors=ff_factors0[(ff_factors0.index >=startpd) & (ff_factors0.index <=endpd)]
            else:
                ff_factors=fff

        elif freq == 'monthly':
            start1=date_adjust(start,adjust=-365)
            end1=date_adjust(end,adjust=365)
            fff=get_ff_factors0(start=start1,end=end1,scope=scope,factor=factor,freq='yearly') 
            if not (fff is None):
                ff_factors=convert2freq(fff,new_freq='monthly')
            else:
                ff_factors=fff

        else:
            start1=date_adjust(start,adjust=-365)
            end1=date_adjust(end,adjust=365)
            fff=get_ff_factors0(start=start1,end=end1,scope=scope,factor=factor,freq='yearly')
            ff_factors=fff
    else:
        ff_factors=fff            

    #加入日期
    cols=list(ff_factors)
    ff_factors['Date']=ff_factors.index
    if freq == 'daily':
        ff_factors['Date']=ff_factors['Date'].apply(lambda x: x.strftime("%Y-%m-%d"))
    
    ff_factors=ff_factors[['Date']+cols]
    
    return ff_factors


def get_ff_factors0(start,end,scope='US',factor='FF3',freq='yearly'):
   """
   【支持的因子种类(factor)】
   FF3: FF3各个因子
   FF5: FF5各个因子
   Mom: 动量因子
   ST_Rev: 短期反转因子
   LT_Rev: 长期反转因子

   【支持的国家/地区(scope)】
   US: 美国
   North_America：北美(美国+加拿大)
   Global: 全球
   Global_ex_US: 全球(除美国外)
   Asia_Pacific_ex_Japan: 亚太(除日本外)，拟作近似中国
   Japan: 日本
   Europe: 欧洲

   【支持的取样频率(freq)】
   yearly: 年
   monthly: 月
   weekly: 周(仅支持美国FF3)
   daily: 日
   """
    
   import pandas as pd
   s=pd.DataFrame([
        ['US','FF3','monthly','F-F_Research_Data_Factors',0],
        ['US','FF3','yearly','F-F_Research_Data_Factors',1],
        ['US','FF3','weekly','F-F_Research_Data_Factors_weekly',0],
        ['US','FF3','daily','F-F_Research_Data_Factors_daily',0],
        ['US','FF5','monthly','F-F_Research_Data_5_Factors_2x3',0],
        ['US','FF5','yearly','F-F_Research_Data_5_Factors_2x3',1],
        ['US','FF5','daily','F-F_Research_Data_5_Factors_2x3_daily',0],  
        ['US','Mom','monthly','F-F_Momentum_Factor',0],
        ['US','Mom','yearly','F-F_Momentum_Factor',1],
        ['US','Mom','daily','F-F_Momentum_Factor_daily',0],  
        ['US','ST_Rev','monthly','F-F_ST_Reversal_Factor',0],
        ['US','ST_Rev','yearly','F-F_ST_Reversal_Factor',1],
        ['US','ST_Rev','daily','F-F_ST_Reversal_Factor_daily',0],    
        ['US','LT_Rev','monthly','F-F_LT_Reversal_Factor',0],
        ['US','LT_Rev','yearly','F-F_LT_Reversal_Factor',1],
        ['US','LT_Rev','daily','F-F_LT_Reversal_Factor_daily',0],   \
        
        ['Global','FF3','monthly','Global_3_Factors',0],
        ['Global','FF3','yearly','Global_3_Factors',1],
        ['Global','FF3','daily','Global_3_Factors_Daily',0],   
        ['Global_ex_US','FF3','monthly','Global_ex_US_3_Factors',0],
        ['Global_ex_US','FF3','yearly','Global_ex_US_3_Factors',1],
        ['Global_ex_US','FF3','daily','Global_ex_US_3_Factors_Daily',0],  
        ['Europe','FF3','monthly','Europe_3_Factors',0],
        ['Europe','FF3','yearly','Europe_3_Factors',1],
        ['Europe','FF3','daily','Europe_3_Factors_Daily',0],  
        ['Japan','FF3','monthly','Japan_3_Factors',0],
        ['Japan','FF3','yearly','Japan_3_Factors',1],
        ['Japan','FF3','daily','Japan_3_Factors_Daily',0],    
        ['Asia_Pacific_ex_Japan','FF3','monthly','Asia_Pacific_ex_Japan_3_Factors',0],
        ['Asia_Pacific_ex_Japan','FF3','yearly','Asia_Pacific_ex_Japan_3_Factors',1],
        ['Asia_Pacific_ex_Japan','FF3','daily','Asia_Pacific_ex_Japan_3_Factors_Daily',0],   
        ['North_America','FF3','monthly','North_America_3_Factors',0],
        ['North_America','FF3','yearly','North_America_3_Factors',1],
        ['North_America','FF3','daily','North_America_3_Factors_Daily',0], \
         
        ['Global','FF5','monthly','Global_5_Factors',0],
        ['Global','FF5','yearly','Global_5_Factors',1],
        ['Global','FF5','daily','Global_5_Factors_Daily',0],   
        ['Global_ex_US','FF5','monthly','Global_ex_US_5_Factors',0],
        ['Global_ex_US','FF5','yearly','Global_ex_US_5_Factors',1],
        ['Global_ex_US','FF5','daily','Global_ex_US_5_Factors_Daily',0],  
        ['Europe','FF5','monthly','Europe_5_Factors',0],
        ['Europe','FF5','yearly','Europe_5_Factors',1],
        ['Europe','FF5','daily','Europe_5_Factors_Daily',0],  
        ['Japan','FF5','monthly','Japan_5_Factors',0],
        ['Japan','FF5','yearly','Japan_5_Factors',1],
        ['Japan','FF5','daily','Japan_5_Factors_Daily',0],    
        ['Asia_Pacific_ex_Japan','FF5','monthly','Asia_Pacific_ex_Japan_5_Factors',0],
        ['Asia_Pacific_ex_Japan','FF5','yearly','Asia_Pacific_ex_Japan_5_Factors',1],
        ['Asia_Pacific_ex_Japan','FF5','daily','Asia_Pacific_ex_Japan_5_Factors_Daily',0],   
        ['North_America','FF5','monthly','North_America_5_Factors',0],
        ['North_America','FF5','yearly','North_America_5_Factors',1],
        ['North_America','FF5','daily','North_America_5_Factors_Daily',0], \

        ['Global','Mom','monthly','Global_Mom_Factor',0],
        ['Global','Mom','yearly','Global_Mom_Factor',1],
        ['Global','Mom','daily','Global_Mom_Factor_Daily',0],   
        ['Global_ex_US','Mom','monthly','Global_ex_US_Mom_Factor',0],
        ['Global_ex_US','Mom','yearly','Global_ex_US_Mom_Factor',1],
        ['Global_ex_US','Mom','daily','Global_ex_US_Mom_Factor_Daily',0],  
        ['Europe','Mom','monthly','Europe_Mom_Factor',0],
        ['Europe','Mom','yearly','Europe_Mom_Factor',1],
        ['Europe','Mom','daily','Europe_Mom_Factor_Daily',0],  
        ['Japan','Mom','monthly','Japan_Mom_Factor',0],
        ['Japan','Mom','yearly','Japan_Mom_Factor',1],
        ['Japan','Mom','daily','Japan_Mom_Factor_Daily',0],    
        ['Asia_Pacific_ex_Japan','Mom','monthly','Asia_Pacific_ex_Japan_MOM_Factor',0],
        ['Asia_Pacific_ex_Japan','Mom','yearly','Asia_Pacific_ex_Japan_MOM_Factor',1],
        ['Asia_Pacific_ex_Japan','Mom','daily','Asia_Pacific_ex_Japan_MOM_Factor_Daily',0],   
        ['North_America','Mom','monthly','North_America_Mom_Factor',0],
        ['North_America','Mom','yearly','North_America_Mom_Factor',1],
        ['North_America','Mom','daily','North_America_Mom_Factor_Daily',0]                 
        ], columns=['scope','factor','freq','symbol','seq'])

   #数据源
   source='famafrench'
   if scope in ["China","HK","TW"]:
       scope="Asia_Pacific_ex_Japan"
    
   #匹配：scope+factor+freq
   ss=s[s['scope'].isin([scope]) & s['factor'].isin([factor]) \
                                  & s['freq'].isin([freq])]  
   #如果未找到匹配的模式，显示信息后返回
   if len(ss)==0:
        print("  #Warning(get_ff_factors): no data available for",scope,factor,freq)
        print("  If all parameters are correct, try earlier dates than",start)
        return None

   #重新索引，第1行的索引编号为0
   sss=ss.reset_index(drop=True)    
   #取出对应的symbol
   symbol=sss.iloc[0]['symbol']    
   #取出对应的月(0)/年(1)编号
   seq=sss.iloc[0]['seq']

   #抓取数据
   import pandas_datareader.data as web
   try:
        ds = web.DataReader(symbol, source, start, end)
   except:
        print(f"  #Warning(get_ff_factors): time out to get {freq} data, working around ...")        
        return None
    
   #提取希望的资产定价因子
   try:
       factor_df=ds[seq]
   except:
       factor_df=extract_DESCR(ds)
       
   if len(factor_df)==0 or factor_df is None:
        print("  #Warning(get_ff_factors): no data available for",start,end,scope,factor,freq)
        #print("Tracing process:"s,ss,sss,symbol,seq,ds)
        print("  If all parameters are correct, try earlier dates than",start)
        return None    
   
   return factor_df

if __name__=='__main__':
    ff3_factors_us=get_ff_factors("01/01/2009","07/18/2019",scope='US', \
                                  factor='FF3',freq='yearly')

    ff3_factors_jp=get_ff_factors("01/01/2009","07/18/2019",scope='Japan', \
                                  factor='FF3',freq='yearly')

    ff3_factors_eu=get_ff_factors("2009-01-01","2019-07-18",scope='Europe', \
                                  factor='FF3',freq='yearly')


#==============================================================================
def get_rf(start,end,scope='US',freq='daily'):
    """
    功能：按照市场获得无风险收益率，百分比表示
    输入：开始日期，解释日期，市场，频率
    
    注意：这里的rf利率指的是freq利率（日利率、周利率、月利率或年利率），而不都是年化利率！
    """    

    try:
        rf_df=get_ff_factors(start,end,scope,'FF3',freq)
    except:
        print("  #Error(get_rf): rf server did not respond.")
        return None    
    if rf_df is None:
        #print("  #Warning(get_rf): fetching risk-free return failed")
        return None

    #强制转换索引格式，彻底消除后续并表的潜在隐患
    rf_df['ffdate']=rf_df.index.astype('str')
    import pandas as pd
    rf_df['ffdate']=pd.to_datetime(rf_df['ffdate'])
    rf_df.set_index(['ffdate'],inplace=True)    
    
    return rf_df

#==============================================================================
if __name__=='__main__':
    mktidx='000001.SS'
    start='2021-10-1'
    end='2021-11-30'
    rate_period='1Y'
    rate_type='shibor'

def get_mkt_rf_daily_china(mktidx,start,end,rate_period='1Y',rate_type='shibor',RF=True):
    """
    功能：为了某些特殊需要(RAR, Markowitz)，构造中国内地的日频Mkt-RF和RF数据表，以百分比%表示
    RF=True为抓取无风险利率，否则不使用无风险利率。
    """
    #抓取日指数价格
    from siat.security_prices import get_prices
    prices=get_prices(mktidx,start,end)
    #计算日收益率，表示为百分比
    import pandas as pd
    mkt_pf=pd.DataFrame(prices['Close'].pct_change())
    mkt_pf=mkt_pf.dropna()
    
    if RF:
        #抓取无风险利率
        rf_pf=rf_daily_china(start,end,rate_period,rate_type)
        
        #合成
        if not (rf_pf is None):
            df=pd.merge(mkt_pf,rf_pf,how='inner',left_index=True,right_index=True)
        else:
            df=mkt_pf
            df['rf_daily']=0
    else:
        df=mkt_pf
        df['rf_daily']=0     
        
    df['Mkt-RF']=(df['Close']-df['rf_daily'])*100
    df['RF']=df['rf_daily']*100

    rf_df=df[['Mkt-RF','RF']]    

    return rf_df  

if __name__=='__main__':
    get_mkt_rf_daily_china('000001.SS','2021-1-1','2021-11-30','1Y','shibor')
    get_mkt_rf_daily_china('000001.SS','2021-1-1','2021-11-30','3M','shibor')
    get_mkt_rf_daily_china('000001.SS','2021-1-1','2021-11-30','1Y','treasury')
#==============================================================================
if __name__=='__main__':
    start='2021-1-1'
    end='2021-11-30'
    scope='US'
    rate_period='1Y'
    rate_type='shibor'
    
    rfd=get_rf_daily(start,end)

def get_rf_daily(start,end,scope='US',rate_period='1Y',rate_type='shibor'):
    """
    功能：获得指定期间的日无风险利率，近期缺失部分使用最近的日期填补
    """
    print("  Searching risk-free interest rates in",scope,'\b, which may take time ...')
    
    if scope=='China':
       rf_china=rf_daily_china(start,end,rate_period,rate_type)
       rf_china['RF']=rf_china['rf_daily']
       rf_df=rf_china[['date','RF']]
    else:
        rf_fred=get_rf(start,end,scope=scope,freq='daily')  
        if rf_fred is None:
            print("  Recovering risk-free interest rates in FRED for",scope,'...')
            start1=date_adjust(start, adjust=-60)
            rf_fred=get_rf(start1,end,scope=scope,freq='daily')
            if rf_fred is None:
                return None
        
        #使用最近日期的利率填补空缺的日期
        rf_fred['date_dt']=rf_fred.index.date
        rf_fred['date']=rf_fred['date_dt'].apply(lambda x: str(x))
        rf_df0=rf_fred[['date','RF']]
        latest_date=rf_df0['date'][-1:].values[0]
        lastest_rate=rf_df0['RF'][-1:].values[0]

        collist=list(rf_df0)
        df_temp = pd.DataFrame(columns=collist)
        end_dt=pd.to_datetime(end)
        for i in range(100):
            date1=date_adjust(latest_date,adjust=i+1)
            date1_dt=pd.to_datetime(date1)
            if date1_dt <= end_dt:
                try:
                    df_temp=df_temp.append({'date':date1,'RF':lastest_rate},ignore_index=True)
                except:
                    df_temp=df_temp._append({'date':date1,'RF':lastest_rate},ignore_index=True)
            else:
                break
    
        df_temp['Date']=pd.to_datetime(df_temp['date'])
        df_temp.set_index(['Date'],inplace=True)    

        try:
            rf_df=rf_df0.append(df_temp)
        except:
            rf_df=rf_df0._append(df_temp)
        rf_df.sort_values(by=['date'],ascending=[True],inplace=True) 
        
        rf_df['rf_daily']=rf_df['RF']/100
    
    print("  Successfully retrieved",len(rf_df),"risk-free interest rates in",scope) 
    
    return rf_df

if __name__=='__main__':
     rf=get_rf_daily(start,end,scope='US',rate_period='1Y',rate_type='shibor')
#==============================================================================
def extract_DESCR(ds):
    """
    归纳：从字典的DESCR中提取年度因子信息 ，用于seq缺失1但误放置在DESCR中的情形
    """ 
    try:       
        descr_str=factor_df=ds['DESCR']
    except:
        return None
    
    wml_pos=descr_str.find("WML")
    nn_pos=descr_str.find("\n\n ")
    wml_post=descr_str[wml_pos+4:nn_pos]
    wml_post1=wml_post.replace('  ,',',')
    wml_post2=wml_post1.replace(' ,',',')
    wml_post3=wml_post2+' '
    
    #正则表达式提取配对
    import re
    wml_post_list=re.findall(r"(.+?),(.+?) ", wml_post3)    
    
    #将提取的配对串列表转换为pandas
    import pandas as pd
    df = pd.DataFrame(columns=('Date', 'WML'))
    for i in wml_post_list:
        #print(i[0],i[1])
        s = pd.Series({'Date':pd.Period(i[0],freq='A-DEC'), 'WML':float(i[1])})
        # 这里 Series 必须是 dict-like 类型
        try:
            df = df.append(s, ignore_index=True)
        except:
            df = df._append(s, ignore_index=True)
        # 这里必须选择ignore_index=True 或者给 Series一个index值    
    df.set_index('Date',drop=True, inplace=True)
    
    return df


#==============================================================================

def get_ff3_factors(start,end,scope='US',freq='yearly'):    
    """
    功能：抓取Fama-French三因子模型的三个市场因子
    1）市场风险溢价(Rmarket-Rf，收益率风险溢价) 
    2）小市值风险溢价(SMB，规模因子，即小市值股票对比大市值股票的超额收益率)
    3）高市净率风险溢价(HML，价值因子，高溢价股票对比低溢价股票的超额收益率)
    
    输入参数：
    start/end：开始/结束日期，格式为YYYY-MM-DD或MM/DD/YYYY
    scope：地区(美国，日本，欧洲，全球，除美国外的全球，除日本外的亚太)
    freq：采样周期(日、周、月、年，其中周仅支持美国市场)
    输出：按照采样周期排列的指定地区的FF3因子(pandas格式)
    """
    
    #仅为测试用
    #start="2018-01-01"
    #end="2018-12-31"
    #scope='US'
    #freq='monthly'
    
    #抓取FF3因子
    factor='FF3'
    ff3_factors=get_ff_factors(start,end,scope,factor,freq)   
    
    return ff3_factors

if __name__=='__main__':
    factors=get_ff3_factors("2018-01-01","2018-12-31",scope='US', \
                                  freq='monthly')
    print("\n",factors)

#==============================================================================
def test_ff3_factors():
    """
    功能：交互式测试资产定价模型FF3的因子
    输入：用户输入
    显示：各个因子
    返回值：无
    """
    
    import easygui as g

    title="Test the Factors of Fama-French 3-factor Model"
    msg="Please fill in the information below"
    fldnames=["Start date (YYYY-MM-DD)","End date (YYYY-MM-DD)", \
          "Scope (US, China, Japan, Europe)", \
          "Frequency (yearly, monthly, daily)"]
    fldvalues=[]
    values=("2018-01-01","2019-04-30","US","monthly")
    fldvalues=g.multenterbox(msg,title=title,fields=fldnames,values=values)
    """
    如果用户输入的值比选项少的话，则返回列表中的值用空字符串填充用户为输入的选项。
    如果用户输入的值比选项多的话，则返回的列表中的值将截断为选项的数量。
    如果用户取消操作，则返回域中的列表的值或者None值
    """
    
    if fldvalues:
        start=fldvalues[0]
        end=fldvalues[1]
        scope=fldvalues[2]
        freq=fldvalues[3]
        
        ff_factors=get_ff3_factors(start,end,scope,freq)
        if ff_factors is None:
            g.msgbox(msg="Sorry, no factor data available under the condition.", \
                     title=title)                       
        else: 
            g.msgbox(msg=ff_factors,title=title)
    else:
        g.msgbox(msg="Sorry, user cancelled the operation, no data retrieved.", \
                 title=title)
        
    return

if __name__=='__main__':
    test_ff3_factors()        

#==============================================================================
def draw1_ff_factors(model,scope,factors,factor_type):    
    """
    功能：绘制单曲线的FF因子变化图
    输入参数：
    model: 模型类型, 任意字符串(例如FF3, FFC4, FF5)
    scope: 市场范围, 任意字符串(例如US, China, Europe)
    factors：包括FF各个因子的数据框
    factor_type：因子类型，严格限于RF/Mkt-RF/SMB/HML/MOM/RMW/CMA
    输出：图形
    返回值：无
    """
    #仅用作测试，完成后应注释掉
    #model="Fama-French 3-factor Model"
    #scope="US"
    #factor_type='ALL'
    
    if factor_type in ['Mkt-RF']:    
        #绘制市场收益率风险溢价变化图
        """
        线段的颜色：c='r'，红色
        线型：ls='-'，实线；':'则为虚线
        线段的粗细：lw=3
        节点形状：marker='o'，圆形
        节点大小：ms=10
        节点颜色：mfc='y'，黄色
        """
        try:
            factors.plot(y=['Mkt-RF'], \
                     c='r',ls='-',lw=3,marker='o',ms=10,mfc='y')
        except:
            print("  #Warning(draw1_ff_factors): no MKT factor data available")
            return
        plt.axhline(y=0.0,color='b',linestyle=':')  #画0点虚线X轴做基准
        title1="\n"+model+": "+scope+", "+" Mkt-RF Factor"
        plt.title(title1,fontsize=12,fontweight='bold')
        plt.ylabel('Mkt-RF',fontsize=12,fontweight='bold')
        plt.xticks(factors.index,fontsize=8,rotation=30)
        plt.legend(loc='best')  
        
        plt.gca().set_facecolor('whitesmoke')
        plt.show()   
        
    if factor_type in ['SMB']:            
        #绘制规模因子变化图
        try:
            factors.plot(y=['SMB'], \
                     c='b',ls='-',lw=3,marker='o',ms=10,mfc='r')
        except:
            print("  #Warning(draw1_ff_factors): no SMB factor data available")
            return
        plt.axhline(y=0.0,color='b',linestyle=':')
        title1="\n"+model+": "+scope+", "+"SMB Factor"
        plt.title(title1,fontsize=12,fontweight='bold')
        plt.ylabel('SMB',fontsize=12,fontweight='bold')
        plt.xticks(factors.index,fontsize=8,rotation=30)
        plt.legend(loc='best')
        
        plt.gca().set_facecolor('whitesmoke')
        plt.show()   

    if factor_type in ['HML']:     
        #绘制价值因子变化图
        try:
            factors.plot(y=['HML'], \
                     c='c',ls='-',lw=3,marker='o',ms=10,mfc='r')
        except:
            print("  #Warning(draw1_ff_factors): no HML factor data available")
            return
        plt.axhline(y=0.0,color='b',linestyle=':')  #画一条0点的虚线做基准参考
        title1="\n"+model+": "+scope+", "+"HML Factor"
        plt.title(title1,fontsize=12,fontweight='bold')
        plt.ylabel('HML',fontsize=12,fontweight='bold')
        plt.xticks(factors.index,fontsize=8,rotation=30)
        plt.legend(loc='best')
        
        plt.gca().set_facecolor('whitesmoke')
        plt.show()   

    if factor_type in ['RF']:      
        #绘制无风险收益率变化图
        try:
            factors.plot(y=['RF'], \
                     c='g',ls='-',lw=3,marker='*',ms=14,mfc='r')
        except:
            print("  #Warning(draw1_ff_factors): no RF data available")
            return
        title1="\n"+model+": "+scope+", "+"HML Factor"
        plt.title(title1,fontsize=12,fontweight='bold')
        plt.ylabel('RF %',fontsize=12,fontweight='bold')
        plt.xticks(factors.index,fontsize=8,rotation=30)
        plt.legend(loc='best')
        
        plt.gca().set_facecolor('whitesmoke')
        plt.show()  

    if factor_type in ['MOM']:         
        #绘制动量因子变化图
        try:
            factors.plot(y=['MOM'], \
                     c='deeppink',ls='-',lw=3,marker='*',ms=15,mfc='y')
        except:
            print("  #Warning(draw1_ff_factors): no MOM factor data available")
            return
        plt.axhline(y=0.0,color='b',linestyle=':')
        title1="\n"+model+": "+scope+", "+"MOM Factor"
        plt.title(title1,fontsize=12,fontweight='bold')
        plt.ylabel('Mom',fontsize=12,fontweight='bold')
        plt.xticks(factors.index,fontsize=8)
        plt.legend(loc='best')
        
        plt.gca().set_facecolor('whitesmoke')
        plt.show()  


    if factor_type in ['RMW']:      
        #绘制盈利因子变化图
        try:
            factors.plot(y=['RMW'], \
                     c='blue',ls='-',lw=3,marker='*',ms=15,mfc='r')
        except:
            print("  #Warning(draw1_ff_factors): no RMW factor data available")
            return        
        plt.axhline(y=0.0,color='b',linestyle=':')
        title1="\n"+model+": "+scope+", "+"RMW Factor"
        plt.title(title1,fontsize=12,fontweight='bold')
        plt.ylabel('RMW',fontsize=12,fontweight='bold')
        plt.xticks(factors.index,fontsize=8)
        plt.legend(loc='best')
        
        plt.gca().set_facecolor('whitesmoke')
        plt.show()  

    if factor_type in ['CMA']:          
        #绘制投资因子变化图
        try:
            factors.plot(y=['CMA'], \
                     c='black',ls='-',lw=3,marker='*',ms=15,mfc='r')
        except:
            print("  #Warning(draw1_ff_factors): no CMA factor data available")
            return
        plt.axhline(y=0.0,color='b',linestyle=':')
        title1="\n"+model+": "+scope+", "+"CMA Factor"
        plt.title(title1,fontsize=12,fontweight='bold')
        plt.ylabel('CMA',fontsize=12,fontweight='bold')
        plt.xticks(factors.index,fontsize=8)
        plt.legend(loc='best')
        
        plt.gca().set_facecolor('whitesmoke')
        plt.show() 
    
    return


if __name__=='__main__':
    factors1=get_ff3_factors("2018-01-01","2018-12-31",scope='US', \
                                  freq='monthly')
    factors2=get_ff3_factors("2018-01-01","2018-12-31",scope='China', \
                                  freq='monthly')    
    draw1_ff_factors("FF3 model","US",factors1,"SMB")
    draw1_ff_factors("FF3 model","Japan",factors2,"SMB")

#==============================================================================
def draw2_ff_factors(model,scope1,scope2,factors1,factors2,factor_type):    
    """
    功能：绘制双曲线的FF因子变化图
    输入参数：
    model: 模型类型, 任意字符串(例如FF3, FFC4, FF5)
    scope: 市场范围, 任意字符串(例如US, China, Europe)
    factors1/2：用于对比的包括FF各个因子的两个数据框
    factor_type：因子类型，严格限于RF/MKT/SMB/HML/MOM/RMW/CMA
    输出：图形
    返回值：无
    """
    #仅用作测试，完成后应注释掉
    #model="FF3 Model"
    #scope1="US"
    #scope2="Europe"
    #factor_type='Mkt-RF'
   
    #转换索引类型为DatetimeIndex，便于后续处理
    import pandas as pd
    factors1['Date']=factors1.index.strftime("%Y-%m-%d")
    factors1['Date']=pd.to_datetime(factors1['Date'])
    factors1.set_index('Date',inplace=True)
    
    factors2['Date']=factors2.index.strftime("%Y-%m-%d")
    factors2['Date']=pd.to_datetime(factors2['Date'])
    factors2.set_index('Date',inplace=True)    

    try:
        plt.plot(factors1[factor_type],label=scope1,marker='o')
        plt.plot(factors2[factor_type],label=scope2,marker='*')
    except:
        print("  #Warning(draw2_ff_factors): no available data for factor",factor_type)
        return
    plt.axhline(y=0.0,color='b',linestyle=':')  
    title1="\n"+model+": "+scope1+" vs. "+scope2+", "+" Factor "+factor_type
    plt.title(title1,fontsize=12,fontweight='bold')
    plt.ylabel(factor_type,fontsize=12,fontweight='bold')
    plt.legend(loc='best')  
    
    plt.gca().set_facecolor('whitesmoke')
    plt.show()       
    
    return

if __name__=='__main__':
    factors1=get_ff3_factors("2009-01-01","2018-12-31",scope='US', \
                                  freq='yearly')
    factors2=get_ff3_factors("2009-01-01","2018-12-31",scope='Europe', \
                                  freq='yearly')
    draw2_ff_factors("FF3 model","US","Europe",factors1,factors2,"Mkt-RF")
    draw2_ff_factors("FF3 model","US","Europe",factors1,factors2,"SMB")
    draw2_ff_factors("FF3 model","US","Europe",factors1,factors2,"HML")

#==============================================================================
if __name__=='__main__':
    start='2016-1-1'
    end='2021-1-1'
    scope='Europe'
    freq='yearly'

def get_ffc4_factors(start,end,scope='US',freq='yearly'):    
    """
    功能：抓取Fama-French-Carhart四因子模型的四个市场因子
    1）市场风险溢价(Rmarket-Rf，收益率风险溢价) 
    2）小市值风险溢价(SMB，规模因子，即小市值股票对比大市值股票的超额收益率)
    3）高市净率风险溢价(HML，价值因子，高溢价股票对比低溢价股票的超额收益率)
    4）交易动量因子(MOM，市场交易中资本利差最高的那部分股票被称为赢家winner，
    而最低的那部分股票被称为输家loser。短期内，赢家具有保持作为赢家的趋势，
    输家具有继续作为输家的趋势。这种现象称为交易惯性，惯性即动量。动量因子
    就是高收益率股票对比低收益率股票的超额收益率)
    
    输入参数：
    start/end：开始/结束日期，格式为YYYY-MM-DD或MM/DD/YYYY
    scope：地区(美国，日本，欧洲，全球，除美国外的全球，除日本外的亚太)
    freq：采样周期(日、周、月、年，其中周仅支持美国市场)
    输出：按照采样周期排列的指定地区的FFC4因子(pandas格式)
    """
    
    #仅为测试用
    #start="2018-01-01"
    #end="2018-12-31"
    #scope='US'
    #freq='monthly'
    
    #抓取FF3因子
    factor='FF3'
    ff3=get_ff_factors(start,end,scope,factor,freq)   
    
    #抓取Mom因子
    factor='Mom'
    try:
        Mom=get_ff_factors(start,end,scope,factor,freq)  
    except:
        print("  #Error(get_ffc4_factors): connection to data source failed:-( Try later!")
        return None
    
    if (ff3 is None) or (Mom is None):
        return None
    
    #将动量数据列名一致化
    if scope == 'US':
        Mom=Mom.rename(columns={'Mom   ':'MOM'})    #针对US数据
    else:
        Mom=Mom.rename(columns={'WML':'MOM'})    #针对非US数据        

    #合成FF3+Mom因子
    import pandas as pd
    #每日因子的日期类型需要转换，不然在非US时合成匹配不成功
    if freq=='daily':
        ff3['date']=ff3.index
        ff3['date']=pd.to_datetime(ff3['date'].astype('str'))
        ff3.set_index('date',drop=True, inplace=True)
    
        Mom['date']=Mom.index
        Mom['date']=pd.to_datetime(Mom['date'].astype('str'))
        Mom.set_index('date',drop=True, inplace=True)
    
    #ffc4_factors=pd.merge(ff3,Mom,how='left',left_index=True,right_index=True)
    ffc4_factors=pd.merge(ff3,Mom,how='inner',on='Date')
    #del ffc4_factors['date']
    
    return ffc4_factors


if __name__=='__main__':
    start="2018-01-01"
    end="2018-12-31"
    scope='Europe'
    freq="monthly"
    factors1=get_ffc4_factors("2009-01-01","2018-12-31",scope='US', \
                                  freq='yearly')
    factors2=get_ffc4_factors("2009-01-01","2018-12-31",scope='Japan', \
                                  freq='yearly')
    draw1_ff_factors("FFC4 model","US",factors1,"MOM")


#==============================================================================
def test_ffc4_factors():
    """
    功能：交互式测试资产定价模型FFC4的因子
    输入：用户输入
    显示：各个因子
    返回值：无
    """
    
    import easygui as g

    title="Test the Factors of Fama-French-Carhart 4-factor Model"
    msg="Please fill in the information below"
    fldnames=["Start date (YYYY-MM-DD)","End date (YYYY-MM-DD)", \
          "Scope (US, China, Japan, Europe)", \
          "Frequency (yearly, monthly, daily)"]
    fldvalues=[]
    values=("2018-01-01","2019-04-30","US","monthly")
    fldvalues=g.multenterbox(msg,title=title,fields=fldnames,values=values)
    """
    如果用户输入的值比选项少的话，则返回列表中的值用空字符串填充用户为输入的选项。
    如果用户输入的值比选项多的话，则返回的列表中的值将截断为选项的数量。
    如果用户取消操作，则返回域中的列表的值或者None值
    """
    
    if fldvalues:
        start=fldvalues[0]
        end=fldvalues[1]
        scope=fldvalues[2]
        freq=fldvalues[3]
        
        ff_factors=get_ffc4_factors(start,end,scope,freq)
        if ff_factors is None:
            g.msgbox(msg="  Sorry, no factor data available under the condition.", \
                     title=title)                       
        else: 
            g.msgbox(msg=ff_factors,title=title)
    else:
        g.msgbox(msg="  Sorry, user cancelled the operation, no data retrieved.", \
                 title=title)
        
    return

if __name__=='__main__':
    test_ffc4_factors()        


#==============================================================================
def get_ff5_factors(start,end,scope='US',freq='yearly'):    
    """
    功能：抓取Fama-French五因子模型的五个市场因子
    1）市场风险溢价(Rmarket-Rf，收益率风险溢价) 
    2）小市值风险溢价(SMB，规模因子，即小市值股票对比大市值股票的超额收益率)
    3）高市净率风险溢价(HML，价值因子，高溢价股票对比低溢价股票的超额收益率)
    4）盈利因子(RMW，盈利好和盈利差的多元化股票组合收益之间的差异。其中，盈利
    定义为年营业收入减去营业成本、利息费用、销售费用和管理费用后再除以t-1财年
    末的账面权益)
    5）投资因子(CMA：投资低和投资高的多元化股票组合收益之间的差异(投资高对长远
    未来有利，但将影响当年业绩。其中，投资定义为t-1财年的新增总资产除以t-2财年
    末的总资产)
    
    输入参数：
    start/end：开始/结束日期，格式为YYYY-MM-DD或MM/DD/YYYY
    scope：地区(美国，日本，欧洲，全球，除美国外的全球，除日本外的亚太)
    freq：采样周期(日、周、月、年，其中周仅支持美国市场)
    输出：按照采样周期排列的指定地区的FF5因子(pandas格式)
    """
    
    #仅为测试用
    #start="2018-01-01"
    #end="2018-12-31"
    #scope='US'
    #freq='monthly'
    
    #抓取FF5因子
    factor='FF5'
    ff5_factors=get_ff_factors(start,end,scope,factor,freq)   
    
    return ff5_factors

if __name__=='__main__':
    factors1=get_ff5_factors("2018-01-01","2018-12-31",scope='US', \
                                  freq='monthly')
    draw1_ff_factors("FFC4 model","US",factors1,"RMW")
    
    factors2=get_ff5_factors("2018-01-01","2018-12-31",scope='Europe', \
                                  freq='monthly')    
    draw1_ff_factors("FFC4 model","US",factors2,"CMA")
    draw2_ff_factors("FFC4 model","US","Europe",factors1,factors2,"RMW")    

#==============================================================================
def test_ff5_factors():
    """
    功能：交互式测试资产定价模型FF5的因子
    输入：用户输入
    显示：各个因子
    返回值：无
    """
    
    import easygui as g

    title="Test the Factors of Fama-French 5-factor Model"
    msg="Please fill in the information below"
    fldnames=["Start date (YYYY-MM-DD)","End date (YYYY-MM-DD)", \
          "Scope (US, China, Japan, Europe)", \
          "Frequency (yearly, monthly, daily)"]
    fldvalues=[]
    values=("2018-01-01","2019-04-30","US","monthly")
    fldvalues=g.multenterbox(msg,title=title,fields=fldnames,values=values)
    """
    如果用户输入的值比选项少的话，则返回列表中的值用空字符串填充用户为输入的选项。
    如果用户输入的值比选项多的话，则返回的列表中的值将截断为选项的数量。
    如果用户取消操作，则返回域中的列表的值或者None值
    """
    
    if fldvalues:
        start=fldvalues[0]
        end=fldvalues[1]
        scope=fldvalues[2]
        freq=fldvalues[3]
        
        ff_factors=get_ff5_factors(start,end,scope,freq)
        if ff_factors is None:
            g.msgbox(msg="  Sorry, no factor data available under the condition.", \
                     title=title)                       
        else: 
            g.msgbox(msg=ff_factors,title=title)
    else:
        g.msgbox(msg="  Sorry, user cancelled the operation, no data retrieved.", \
                 title=title)
        
    return

if __name__=='__main__':
    test_ff5_factors()   


#==============================================================================
if __name__=='__main__':
    ticker='BIDU'
    start='2025-1-1'
    end='2025-5-30'
    scope='US'
    graph=True
    
    
def reg_ff3_betas(ticker,start,end,scope='US',graph=True):
    """
    功能：测试一只股票对于FF3各个因子的系数大小、符号方向和显著性
    输入：
    ticker: 股票代码
    start/end: 开始/结束日期，格式：YYYY-MM-DD或MM/DD/YYYY
    scope: 股票市场地域
    输出：FF3模型对于一只股票日收益率的回归结果
    """
    
    #仅为测试使用，过后应注释掉
    #scope='Japan'
    #ticker='9983.T'
    #start='01/01/2018'
    #end='06/30/2019'        

    #抓取每日股价
    price=get_price(ticker,start,end)
    
    #计算股票日收益率
    import pandas as pd
    ret=pd.DataFrame(price['Close'].pct_change()*100)
    ret=ret.dropna()
    #命名日收益率字段为dRet
    ret=ret.rename(columns={'Close':'dRet'})

    #抓取FF3因子
    print("  Looking for factors for FF3 model ...")
    freq='daily'
    ff3=get_ff3_factors(start,end,scope,freq)
    if ff3 is None:
        print("  #Warning(reg_ff3_betas): factors unavailable for",scope,freq,'from',start,'to',end)
        return None
    if len(ff3) == 0:
        print("  #Warning(reg_ff3_betas): zero factors retrieved for",scope,freq,'from',start,'to',end)
        return None
    
    #改造索引类型为时间戳索引（DatetimeIndex），便于与ret合成
    ff3['Date']=ff3.index.strftime("%m/%d/%Y")
    ff3['Date']=pd.to_datetime(ff3['Date'])
    ff3.set_index('Date',inplace=True)

    #内连接：股票日收益率+每日FF3因子
    sample=pd.merge(ret,ff3,how='inner',left_index=True,right_index=True)
    sample=sample.dropna()

    #回归FF3模型
    import statsmodels.api as sm
    y=sample['dRet']
    X=sample[['Mkt-RF','SMB','HML']]
    X1=sm.add_constant(X)
    results=sm.OLS(y,X1).fit() 
    
    #生成回归参数
    #dir(results)    #查看回归结果results的属性
    parms=regparms(results)

    #输出结果并绘制横向柱状图    
    if graph == True:
        gparms=parms.iloc[[1,2,3]]
        #print("\n",parms)
        title=ticker_name(ticker)+": FF3模型的贝塔系数"
        plt.title(title,fontsize=12,fontweight='bold')
        plt.ylabel("贝塔系数",fontsize=12,fontweight='bold')
        
        import datetime; today = datetime.date.today()
        footnote="FF3因子"+"\n数据来源：雅虎财经, "+str(today)
        plt.xlabel(footnote,fontsize=12,fontweight='bold')
        plt.bar(gparms.index,gparms.coef,0.5,color=['r','g','b'],alpha=0.5)
        plt.axhline(y=0.0,color='blue',linestyle=':')

    return parms

if __name__=='__main__':
    reg_ff3_betas=reg_ff3_betas('9983.T',"2018-01-01","2018-12-31",scope='Japan')
    
#==============================================================================
def test_ff3_betas():
    """
    功能：交互式测试资产定价因子的贝塔系数
    输入：用户输入
    显示：各个因子的贝塔系数
    返回值：无
    """
    
    import easygui as g

    title="Calculate A Stock's Betas Using FF3 Model"
    msg="Please fill in the information below"
    fldnames=["Start date (YYYY-MM-DD)","End date (YYYY-MM-DD)", \
          "Scope (US, China, Japan, Europe)", \
          "Stock code (mind the suffix for no-US stocks)"]
    fldvalues=[]
    values=("2018-01-01","2019-04-30","US","AAPL")
    fldvalues=g.multenterbox(msg,title=title,fields=fldnames,values=values)
    
    if fldvalues:
        start=fldvalues[0]
        end=fldvalues[1]
        scope=fldvalues[2]
        if scope == "China": scope="Asia_Pacific_ex_Japan"
        ticker=fldvalues[3]
        
        parms=reg_ff3_betas(ticker,start,end,scope)
        if parms is None:
            g.msgbox(msg="  Sorry, no beta data available under the condition.", \
                     title=title)                       
        else: 
            title=ticker+"'s Betas Using FF3 Model"
            g.msgbox(msg=parms,title=title)
    else:
        g.msgbox(msg="  Sorry, user cancelled the operation, no data retrieved.", \
                 title=title)
        
    return

if __name__=='__main__':
    test_ff3_betas()   

    
#==============================================================================
if __name__=='__main__':
    ticker='MSFT'
    start='2022-5-1'; end='2025-4-30'
    scope='US'; graph=True
    
    
    
def reg_ffc4_betas(ticker,start,end,scope='US',graph=True):
    """
    功能：测试一只股票对于FFC4各个因子的系数大小、符号方向和显著性
    输入：
    ticker: 股票代码
    start/end: 开始/结束日期，格式：YYYY-MM-DD或MM/DD/YYYY
    scope: 股票市场地域
    输出：FFC4模型对于一只股票日收益率的回归结果
    """
    
    #仅为测试使用，过后应注释掉
    #scope='US'
    #ticker='AAPL'
    #start='01/01/2018'
    #end='06/30/2019'        

    #抓取每日股价
    import siat.security_prices as ssp
    price=get_price(ticker,start,end)
    
    #计算股票日收益率
    import pandas as pd
    ret=pd.DataFrame(price['Close'].pct_change()*100)
    ret=ret.dropna()
    #命名日收益率字段为dRet
    ret=ret.rename(columns={'Close':'dRet'})

    #抓取每日FFC4因子
    print("  Looking for factors for FFC4 model ...")
    freq='daily'
    ffc4=get_ffc4_factors(start,end,scope,freq)
    if ffc4 is None:
        print("  #Warning(reg_ffc4_betas): factors not available for",scope,freq,'from',start,'to',end)
        return None    
    if len(ffc4) == 0:
        print("  #Warning(reg_ffc4_betas): zero factors retrieved for",scope,freq,'from',start,'to',end)
        return None    
    
    #改造索引类型为时间戳索引（DatetimeIndex），便于与ret合成
    #ffc4['Date']=ffc4.index.strftime("%m/%d/%Y")
    ffc4['Date']=pd.to_datetime(ffc4['Date'])
    ffc4.set_index('Date',drop=True,inplace=True)    

    #合成股票日收益率+每日FF3因子
    sample=pd.merge(ret,ffc4,how='inner',left_index=True,right_index=True)
    sample=sample.dropna()

    #回归FF3模型
    import statsmodels.api as sm
    y=sample['dRet']
    try:
        X=sample[['Mkt-RF','SMB','HML','MOM']]
    except:
        X=sample[['Mkt-RF','SMB','HML','Mom']]
    X1=sm.add_constant(X)
    results=sm.OLS(y,X1).fit() 
    
    #生成回归参数
    parms=regparms(results)

    #输出结果并绘制横向柱状图
    gparms=parms.iloc[[1,2,3,4]]
    if graph == True:
        #print("\n",parms)
        title=ticker_name(ticker)+": FFC4模型的贝塔系数"
        plt.title(title,fontsize=12,fontweight='bold')
        plt.ylabel("贝塔系数",fontsize=12,fontweight='bold')
        
        import datetime; today = datetime.date.today()
        footnote="FFC4因子"+"\n数据来源：雅虎财经, "+str(today)        
        plt.xlabel(footnote,fontsize=12,fontweight='bold')
        plt.bar(gparms.index,gparms.coef,0.5,color=['r','g','b'],alpha=0.5)
        plt.axhline(y=0.0,color='blue',linestyle=':')

    return parms


if __name__=='__main__':
    ffc4=reg_ffc4_betas('AAPL',"2018-01-01","2019-06-30",scope='US')
    
#==============================================================================
def test_ffc4_betas():
    """
    功能：交互式测试资产定价因子的贝塔系数
    输入：用户输入
    显示：各个因子的贝塔系数
    返回值：无
    """
    
    import easygui as g

    title="Calculate A Stock's Betas Using FFC4 Model"
    msg="Please fill in the information below"
    fldnames=["Start date (YYYY-MM-DD)","End date (YYYY-MM-DD)", \
          "Scope (US, China, Japan, Europe)", \
          "Stock code (mind the suffix for no-US stocks)"]
    fldvalues=[]
    values=("2018-01-01","2019-04-30","Europe","BMW.DE")
    fldvalues=g.multenterbox(msg,title=title,fields=fldnames,values=values)
    
    if fldvalues:
        start=fldvalues[0]
        end=fldvalues[1]
        scope=fldvalues[2]
        if scope == "China": scope="Asia_Pacific_ex_Japan"
        ticker=fldvalues[3]
        
        parms=reg_ffc4_betas(ticker,start,end,scope)
        if parms is None:
            g.msgbox(msg="  Sorry, no beta data available under the condition.", \
                     title=title)                       
        else: 
            title=ticker+"'s Betas Using FFC4 Model"
            g.msgbox(msg=parms,title=title)
    else:
        g.msgbox(msg="  Sorry, user cancelled the operation, no data retrieved.", \
                 title=title)
        
    return

if __name__=='__main__':
    test_ffc4_betas() 
    
#==============================================================================
if __name__=='__main__':
    ticker='MSFT'
    start='2024-5-1'; end='2025-4-30'
    scope='US'; graph=True

def reg_ff5_betas(ticker,start,end,scope='US',graph=True):
    """
    功能：测试一只股票对于FF5各个因子的系数大小、符号方向和显著性
    输入：
    ticker: 股票代码
    start/end: 开始/结束日期，格式：YYYY-MM-DD或MM/DD/YYYY
    scope: 股票市场地域
    输出：FF5模型对于一只股票日收益率的回归结果
    """
    
    #仅为测试使用，过后应注释掉
    #scope='US'
    #ticker='AAPL'
    #start='01/01/2018'
    #end='06/30/2019'        

    #抓取每日股价
    import siat.security_prices as ssp
    price=get_price(ticker,start,end)
    
    #计算股票日收益率
    import pandas as pd
    ret=pd.DataFrame(price['Close'].pct_change()*100)
    ret=ret.dropna()
    #命名日收益率字段为dRet
    ret=ret.rename(columns={'Close':'dRet'})

    #抓取每日FF5因子
    print("  Looking for factors for FF5 model ...")
    freq='daily'
    ff5=get_ff5_factors(start,end,scope,freq)
    if ff5 is None:
        print("  #Warning(reg_ff5_betas): factors not available for",scope,freq,'from',start,'to',end)
        return None       
    if len(ff5) is None:
        print("  #Warning(reg_ff5_betas): zero factors retrieved for",scope,freq,'from',start,'to',end)
        return None       
    
    #改造索引类型为时间戳索引（DatetimeIndex），便于与ret合成
    ff5['Date']=ff5.index.strftime("%m/%d/%Y")
    ff5['Date']=pd.to_datetime(ff5['Date'])
    ff5.set_index('Date',inplace=True)    

    #合成股票日收益率+每日FF3因子
    sample=pd.merge(ret,ff5,how='inner',left_index=True,right_index=True)
    sample=sample.dropna()

    #回归FF3模型
    import statsmodels.api as sm
    y=sample['dRet']
    X=sample[['Mkt-RF','SMB','HML','RMW','CMA']]
    X1=sm.add_constant(X)
    results=sm.OLS(y,X1).fit() 
    
    #生成回归参数
    parms=regparms(results)

    #输出结果并绘制横向柱状图
    gparms=parms.iloc[[1,2,3,4,5]]
    if graph == True:
        #print("\n",parms)
        title=ticker_name(ticker)+"：FF5模型的贝塔系数"
        plt.title(title,fontsize=12,fontweight='bold')
        plt.ylabel("贝塔系数",fontsize=12,fontweight='bold')
        
        import datetime; today = datetime.date.today()
        footnote="FF5因子"+"\n数据来源：雅虎财经, "+str(today)           
        plt.xlabel(footnote,fontsize=12,fontweight='bold')
        plt.bar(gparms.index,gparms.coef,0.5,color=['r','g','b'],alpha=0.5)
        plt.axhline(y=0.0,color='blue',linestyle=':')

    return parms


if __name__=='__main__':
    ff5_betas=reg_ff5_betas('AAPL',"2018-01-01","2019-07-18",scope='US')
    
#==============================================================================
def test_ff5_betas():
    """
    功能：交互式测试资产定价因子的贝塔系数
    输入：用户输入
    显示：各个因子的贝塔系数
    返回值：无
    """
    
    import easygui as g

    title="Calculate A Stock's Betas Using FF5 Model"
    msg="Please fill in the information below"
    fldnames=["Start date (YYYY-MM-DD)","End date (YYYY-MM-DD)", \
          "Scope (US, China, Japan, Europe)", \
          "Stock code (mind the suffix for no-US stocks)"]
    fldvalues=[]
    values=("2018-01-01","2019-04-30","Japan","9983.T")
    fldvalues=g.multenterbox(msg,title=title,fields=fldnames,values=values)
    
    if fldvalues:
        start=fldvalues[0]
        end=fldvalues[1]
        scope=fldvalues[2]
        if scope == "China": scope="Asia_Pacific_ex_Japan"
        ticker=fldvalues[3]
        
        parms=reg_ff5_betas(ticker,start,end,scope)
        if parms is None:
            g.msgbox(msg="Sorry, no beta data available under the condition.", \
                     title=title)                       
        else: 
            title=ticker+"'s Betas Using FF5 Model"
            g.msgbox(msg=parms,title=title)
    else:
        g.msgbox(msg="Sorry, user cancelled the operation, no data retrieved.", \
                 title=title)
        
    return

if __name__=='__main__':
    test_ff5_betas() 
    
#==============================================================================



def reg_ff_betas(ticker,start,end='today',indicator='FF3',market='US'):
    """
    功能：套壳函数reg_ff3_betas/reg_ffc4_betas/reg_ff5_betas
    参数：
    indicator：默认'FF3',还可为'FFC4'或'FF5'
    scope：默认'US',还可为'China'或'Japan'或'Europe'等
    """
    scope=market
    
    start,end=start_end_preprocess(start,end)
    
    indicator1=indicator.lower()
    factorlist=['ff3','ffc4','ff5']
    if not (indicator1 in factorlist):
        print(f"  #Error(show_ff_factors): unsupported factor {indicator}")
        print(f"  Supported factors for FF models: {factorlist}")
        return    
        
    if indicator1=='ff3':
        df=reg_ff3_betas(ticker=ticker,start=start,end=end,scope=scope)
    elif indicator1=='ffc4':
        df=reg_ffc4_betas(ticker=ticker,start=start,end=end,scope=scope)
    elif indicator1=='ff5':
        df=reg_ff5_betas(ticker=ticker,start=start,end=end,scope=scope)
    else:
        pass   
    
    #打印回归结果
    cols=list(df)
    df['const']=df.index
    df=df[['const']+cols]
    
    titletxt=ticker_name(ticker)+"："+indicator.upper()+'模型回归结果'  
    import datetime; todaydt = datetime.date.today(); todaystr=str(todaydt)
    footnote="数据来源：Dartmouth College/sina/stooq/Yahoo等，"+todaystr    
    
    df.rename(columns={'const':'Constant','coef':'Coefficient', \
                       'sig':'Significance'},inplace=True)
    
    df_display_CSS(df,titletxt=titletxt,footnote=footnote,facecolor='papayawhip', \
                   decimals=4, \
                   first_col_align='center',second_col_align='center', \
                   last_col_align='center',other_col_align='center')       
        
    return df