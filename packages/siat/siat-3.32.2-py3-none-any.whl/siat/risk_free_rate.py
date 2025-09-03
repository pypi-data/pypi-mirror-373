# -*- coding: utf-8 -*-
"""
版权：王德宏，北京外国语大学国际商学院
功能：
1、基于股票或股票组合计算无风险收益率
2、绘制无风险收益率的变化趋势图：日，周，月
3、与实际的无风险收益率比较
版本：1.0，2021-2-6
"""

#==============================================================================
#关闭所有警告
import warnings; warnings.filterwarnings('ignore')
import siat.common as com
from siat.translate import *
#==============================================================================
#==============================================================================
#==============================================================================
def compare_rf(rf1,col1,rf2,col2,fromdate,todate,power=0,zeroline=True,twinx=False):
    """
    功能：比较两个无风险收益率的时间序列，并绘制趋势线
    """
    #检查日期期间的合理性
    result,start,end=com.check_period(fromdate,todate)
    if not result:
        print(" Error(compare_rf): invalide date period from",fromdate,"to",todate)
        return None
    
    #检查并筛选两个无风险收益率的时间序列
    if rf1 is None:
        print(" Error(compare_rf): 1st risk-free-rate series is empty")
        return None        
    if rf2 is None:
        print(" Error(compare_rf): 2nd risk-free-rate series is empty")
        return None  
    df1a=rf1[rf1.index >= start]
    df1b=df1a[df1a.index <= end]
    df1b[col1+'%']=df1b[col1]*100.0
    
    df2a=rf2[rf2.index >= start]
    df2b=df2a[df2a.index <= end]
    df2b[col2+'%']=df2b[col2]*100.0

    #绘制对比图
    import siat.grafix as g
    ticker1=g.ticker_name(df1b['ticker'][0])
    colname1=col1+'%'
    label1=col1+'%'
    ticker2=g.ticker_name(df2b['ticker'][0])
    colname2=col2+'%'
    label2=col2+'%'   
    ylabeltxt='无风险收益率%'
    titletxt="基于CAPM计算的无风险收益率变化趋势"
    
    import datetime; today = datetime.date.today()
    rf1note=df1b['footnote'][0]
    rf2note=df2b['footnote'][0]
    footnote="无风险收益率1："+str(rf1note)+ \
             "\n无风险收益率2："+str(rf2note)+ \
             "\n数据来源：雅虎财经, "+str(today)
    
    g.plot_line2(df1b,ticker1,colname1,label1, \
               df2b,ticker2,colname2,label2, \
               ylabeltxt,titletxt,footnote, \
               power=power,zeroline=zeroline,twinx=twinx)

    return

if __name__=='__main__':
    df1=get_rf_capm('AAPL','^GSPC','2018-1-1','2020-12-31',window=40)
    df2=get_rf_capm('MSFT','^GSPC','2018-1-1','2020-12-31',window=40)
    compare_rf(df1,'Rf',df2,'Rf','2019-1-1','2019-12-31')
    compare_rf(df1,'Rf',df2,'Rf','2019-1-1','2019-12-31',twinx=True)

    df1['Rf_20']=df1['Rf'].rolling(window=20).mean()
    compare_rf(df1,'Rf',df1,'Rf_20','2019-1-1','2019-12-31')

#==============================================================================

def calc_rolling_cumret(dfc,col,period='Weekly'):
    """
    传入日收益率col的数据表dfc
    传出不同期间的累计收益率序列cumret
    """
    df=dfc.copy()
    #检查period类型
    periodlist = ["Weekly","Biweekly","Monthly","Quarterly","Semiannual","Annual"]
    if not (period in periodlist):
        print("  Error(calc_rolling_cumret): only supports:",periodlist)
        return None

    #换算期间对应的实际交易天数
    perioddays=[5,10,20,60,120,240]
    rollingnum=perioddays[periodlist.index(period)]      
    
    import numpy as np
    df['logdret']=np.log(df[col]+1)
    df['cumret']=np.exp(df['logdret'].rolling(rollingnum).sum())-1.0
    
    return df['cumret']

#==============================================================================

if __name__ =="__main__":
    col='Rf'
    limits=[0.01,0.01]
    
def winsor(df,col,limits=[0.01,0.01]):
    """
    功能：对于数据表df1中的列col进行下1%（参数1）和上1%（参数2）的处理
    """
    import numpy as np
    from scipy.stats.mstats import winsorize

    a = np.array(df[col])
    aw=winsorize(a,limits=limits)
    
    return aw.data
#==============================================================================
if __name__=='__main__':
    ticker='399001.SZ'
    mktidx='000300.SS'
    fromdate='2020-1-1'
    todate='2020-12-31'
    window=240

def get_rf_capm(ticker,mktidx,fromdate,todate,window=240,sharelist=[]):
    """
    功能：计算无风险收益率的时间序列
    ticker：股票或股票组合
    mktidx：股票市场指数
    fromdate：开始时间
    todate：截止时间
    window：每次回归的样本个数
    sharelist：第一个参数为投资组合的持股比例，默认为等权重；为单个股票时无用
    """
    #检查日期期间的合理性
    result,start,end=com.check_period(fromdate,todate)
    if not result:
        print(" Error(get_rf_capm): invalide date period from",fromdate,"to",todate)
        return None

    #提前开始日期，留出回归窗口
    start1=com.date_adjust(start,adjust=-window*2)
    
    #获得股票或股票组合的历史收益率
    import siat.security_prices as sp
    #单个股票情形
    if isinstance(ticker,str):
        spdf=sp.get_prices(ticker,start1,end)
    #股票组合情形
    if isinstance(ticker,list):
        if sharelist == []:
            num=len(ticker)
            sharelist=[1]*num
        spdf=sp.get_prices_portfolio(ticker,sharelist,start1,end)
    if spdf is None:
        print("  Error(get_rf_capm): info not found or unavailable for",ticker)
        return None
    
    spdf['Stock_dailyRet']=spdf['Close'].pct_change()  
    
    #获取市场指数的历史收益率
    rmdf=sp.get_prices(mktidx,start1,end)
    if rmdf is None:
        print("  Error(get_rf_capm): info not found or unavailable for",mktidx)
        return None    
    rmdf['Market_dailyRet']=rmdf['Close'].pct_change()  
    
    #合并股票（组合）与市场指数的收益率为一个数据集
    import pandas as pd
    df=pd.merge(rmdf['Market_dailyRet'],spdf['Stock_dailyRet'],how='inner',left_index=True,right_index=True)
    df['Date']=df.index.strftime("%Y-%m-%d")
    
    datelist_ts=list(df.index)    
    datelist=list(df['Date'])
    fromdate=start.strftime("%Y-%m-%d")
    #start_pos=lookup_datelist(datelist,fromdate,direction='more')
    todate=end.strftime("%Y-%m-%d")
    #end_pos=lookup_datelist(datelist,todate,direction='less')
    
    #用于滚动的日期期间
    datelist_rolling=[]
    for d in datelist:
        if (d >= fromdate) and (d <= todate):
            datelist_rolling=datelist_rolling+[d]
    
    #滚动回归
    if sharelist == []:
        #footnote=[ticker,mktidx,fromdate,todate,window]
        footnote=[ticker,mktidx,window]
    else:
        #footnote=[ticker,mktidx,fromdate,todate,window,sharelist]
        footnote=[ticker,mktidx,window,sharelist]
    betas=pd.DataFrame(columns=('date','Beta','alpha','R-sqr','p-value','sig','Rf','ticker','footnote'))    
    from scipy import stats
    import numpy as np
    
    for d in datelist_rolling:
        pos2=lookup_datelist(datelist,d)
        pos1=pos2 - window
        sdate2=datelist_ts[pos2]
        sdate1=datelist_ts[pos1]

        sampledf=df[df.index >= sdate1].copy()
        sampledf=sampledf[sampledf.index < sdate2]
        
        (beta,alpha,r_value,p_value,std_err)= \
            stats.linregress(sampledf['Market_dailyRet'],sampledf['Stock_dailyRet'])
        sig=sig_stars(p_value)
        try:
            rf=alpha/(1-beta)
        except:
            rf=np.nan    
        
        row=pd.Series({'date':sdate2,'Beta':beta,'alpha':alpha, \
            'R-sqr':r_value**2,'p-value':p_value,'sig':sig,'Rf':rf,'ticker':ticker,'footnote':footnote})
        try:
            betas=betas.append(row,ignore_index=True)
        except:
            betas=betas._append(row,ignore_index=True)
    
    betas.set_index('date',inplace=True)
    
    return betas

if __name__=='__main__':   
    df1=get_rf_capm('399001.SZ','000001.SS','2020-1-1','2020-12-31',window=240)
    df1['Rf'].plot()

    df2=get_rf_capm('000001.SS','399001.SZ','2020-1-1','2020-12-31',window=240)
    df2['Rf'].plot()

    df3=get_rf_capm('000001.SS','000300.SS','2020-1-1','2020-12-31',window=240)
    df3['Rf'].plot()    

    df4=get_rf_capm('AAPL','^GSPC','2020-1-1','2020-12-31',window=240)
    df4['Rf'].plot()  

    df5=get_rf_capm('^DJI','^GSPC','2020-1-1','2020-12-31',window=240)
    df5['Rf'].plot()  
#==============================================================================
if __name__=='__main__':   
    datelist=['2019-12-30','2019-12-31','2020-01-02','2020-01-03','2020-01-06']
    adate='2020-01-01'
    adate='2020-01-04'
    direction='less'
    direction='more'
    
def lookup_datelist(datelist,adate,direction='less'):
    """
    功能：在日期列表datelist查找与日期adate最接近日期的位置
    direction='more'：若无匹配的日期，则往日期增加的方向查找最接近日期的位置
    direction='less'：若无匹配的日期，则往日期减少的方向查找最接近日期的位置
    """
    i=0
    found=False
    while not found:
        try:
            pos=datelist.index(adate)
        except:
            if direction == 'more':
                i=i+1
            else:
                i=i-1
            adate=com.date_adjust(adate,adjust=i)
        else:
            found=True    

    return pos

#==============================================================================
if __name__=='__main__':   
    p_value=0.07
    p_value=0.02
    p_value=0.0009
    criteria='accounting'
    criteria='financial'
    
def sig_stars(p_value,criteria='accounting'):
    """
    功能：基于p_value给出星号的个数
    p_value：显著性水平
    criteria='accounting'：默认的显著性基准，<0.1为一颗星；若为'financial'，<0.05为一颗星
    """
    sig=''
    if criteria == 'accounting':
        if p_value < 0.1: sig='*'*1
        if p_value < 0.05: sig='*'*2
        if p_value < 0.01: sig='*'*3
    else:
        if p_value < 0.05: sig='*'*1
        if p_value < 0.01: sig='*'*2
        if p_value < 0.001: sig='*'*3        

    return sig

if __name__=='__main__': 
    sig_stars(0.1)
    sig_stars(0.07)
    sig_stars(0.04)
    sig_stars(0.009)

#==============================================================================
def calc_capm_rf(rmdf,rdf):
    """
    功能：CAPM回归
    返回：截距项，贝塔系数，无风险收益率
    """
    #OLS回归
    from scipy import stats 
    (beta,alpha,r_value,p_value,std_err)=stats.linregress(rmdf,rdf)    
    
    rf=alpha/(1-beta)
    
    return [beta,alpha,r_value,p_value,std_err,rf]

#==============================================================================
#==============================================================================
#==============================================================================
#==============================================================================
if __name__=='__main__': 
    start='2018-1-1'
    end='2020-12-31'
    scope='US'
    freq='daily'

def get_rf_kfdl(start,end,scope='US',freq='daily'):
    """
    功能：从Kenneth R. French's Data Library获得无风险收益率
    start/end：日期期间
    scope：国家/地区，支持美国/北美/欧洲/日本/不含日本的亚太/不含美国的全球。全球
    freq：支持日/月/年收益率，其中美国还支持周数据
    返回：无风险收益率，市场收益率
    """
    import siat.fama_french as ff
    factor='FF3'
    df=ff.get_ff_factors(start,end,scope,factor,freq)
    
    df['Market_dailyRet']=df['Mkt-RF']+df['RF']
    df['Rf']=df['RF']
    df['ticker']=scope
    footnote=[scope,freq]
    df['footnote']=df['ticker'].apply(lambda x:footnote)
    
    df1=df[['Market_dailyRet','Rf','ticker','footnote']]
    
    return df1


#==============================================================================
