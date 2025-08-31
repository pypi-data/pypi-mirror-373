# -*- coding: utf-8 -*-

"""
版权：王德宏，北京外国语大学国际商学院
功能：计算CAPM模型贝塔系数的调整值
版本：2.1，2019-7-25
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
def prepare_capm(stkcd,mktidx,start,end):
    """
    函数功能：准备计算一只股票CAPM模型贝塔系数的数据，并标记年度
    输入参数：
    stkcd: 股票代码
    mktidx: 指数代码
    start：使用股票价格数据的开始日期，MM/DD/YYYY
    end：使用股票价格数据的结束日期，MM/DD/YYYY
    输出数据：
    返回数据：带年度标记的可直接用于capm回归的股票收益率数据
    """
        
    #仅用于调试，正式使用前应注释掉
    #stkcd='002504.SZ'; mktidx='000001.SS'
    #start="12/31/2011"; end="12/31/2018"

    #抓取股价和指数
    stock=get_price(stkcd,start,end)
    if stock is None:
        print("  #Error(prepare_capm): no data retrieved from server!")
        return None
    market=get_price(mktidx,start,end)
    if market is None:
        print("  #Error(prepare_capm): no index data retrieved from server!")
        return None    

    #计算日收益率
    import pandas as pd
    stkret=pd.DataFrame(stock['Close'].pct_change())
    mktret=pd.DataFrame(market['Close'].pct_change())

    #合并，去掉空缺
    R=pd.merge(mktret,stkret,how='left',left_index=True,right_index=True)
    R=R.dropna()

    #标记各个年度
    R['Year']=R.index.strftime("%Y")

    #返回带年份的股票收益率序列
    return R

if __name__=='__main__':
    R1=prepare_capm('0700.HK','^HSI','2014-01-01','2018-12-31')

#==============================================================================
#==============================================================================
def get_beta_ML(stkcd,mktidx,yearlist,printout=True,graph=True):
    """
    函数功能：使用ML方法调整一只股票的CAPM模型贝塔系数
    输入参数：
    stkcd: 股票代码
    mktidx: 指数代码
    yearlist：年度列表，列出其中期间的贝塔系数
    输出数据：
    显示CAPM市场模型回归的beta, 以及ML调整后的beta系数
    返回数据:年度CAPM贝塔系数和ML调整后的beta系数
    """

    #仅为测试用，完成后应立即注释掉
    #stkcd='0700.HK'
    #mktidx='^HSI'
    #yearlist=['2015','2016','2017','2018']
    
    Y4=str(int(yearlist[0])-1)
    start=Y4+'-01-01'
    end=yearlist[-1]+'-12-31'    
        
    #读取股价并准备好收益率数据
    try:
        R=prepare_capm(stkcd,mktidx,start,end)
    except:
        print("  #Error(get_beta_ML): Preparing CAPM data failed!")
        return None

    if (R is None):
        print("  #Error(get_beta_ML): server time out")
        return None
    if (len(R) == 0):
        print("  #Error(get_beta_ML): server returned empty data")
        return None
    
    #用于保存beta(CAPM)和beta(ML)
    import pandas as pd
    betas=pd.DataFrame(columns=('Year','Beta(CAPM)','Beta(ML)'))

    #计算Merrill-Lynch方法贝塔系数调整
    from scipy import stats
    for year in yearlist:
        r=R[R['Year']==year]
        if len(r) != 0:
            output=stats.linregress(r['Close_x'],r['Close_y'])
            (beta,alpha,r_value,p_value,std_err)=output
            beta_ML=beta*2.0/3.0+1.0/3.0
            #整齐输出 
            #print(year,"%6.4f "%(beta),"%6.4f "%(beta_ML))

            row=pd.Series({'Year':year,'Beta(CAPM)':beta,'Beta(ML)':beta_ML})
            try:
                betas=betas.append(row,ignore_index=True)
            except:
                betas=betas._append(row,ignore_index=True)

    betas.set_index(["Year"], inplace=True)
    
    if printout == True: printdf_betas(betas,2)
    if graph == True:
        model="贝塔系数的简单调整法"
        draw2_betas(model,mktidx,stkcd,betas)

    return betas

#==============================================================================
def printdf_betas(df,decimal=2):
    """
    功能：整齐地显示数据框的内容，自动调整各列宽度
    """
    #打印时保留的小数点位数
    dec="%."+str(decimal)+"f"
    format=lambda x: dec % x
    df1=df.applymap(format)    
    
    import pandas as pd
    #调整最佳列宽
    old_width = pd.get_option('display.max_colwidth')
    pd.set_option('display.max_colwidth', -1)
    print(df1)
    pd.set_option('display.max_colwidth', old_width)

    return
    
if __name__=='__main__':
    yearlist=gen_yearlist['2010','2019']
    betas=get_beta_ML('AAPL','^GSPC',yearlist)    
    betas2=get_beta_ML('BILI','^GSPC',yearlist)
    betas3=get_beta_ML('0700.HK','^HSI',yearlist)
    yearlist1=['2015','2016','2017','2018']
    betas3=get_beta_ML('0700.HK','^HSI',yearlist1)

#==============================================================================
def draw2_betas(model,scope,ticker,betas):    
    """
    功能：绘制双曲线的贝塔因子变化图
    输入参数：
    model: 模型类型, 任意字符串(例如Merrill-Lynch Beta Adjustment)
    scope: 市场指数, 任意字符串(例如Standard & Poor 500)
    ticker：股票代码
    输出：图形
    """
    #仅用作测试，完成后应注释掉
    #model="Merrill-Lynch Beta Adjustment"
    #scope="Standard & Poor 500"
    #ticker="AAPL"

    #取得股票和指数名字，对于非美股可能耗时较长
    """
    import yfinance as yf
    mktidx= yf.Ticker(scope)
    idxinfo=mktidx.info
    idxname=idxinfo['shortName']
    stkcd=yf.Ticker(ticker)
    stkinfo=stkcd.info
    stkname=stkinfo['shortName']   
    title1="\n"+stkname+"\n"+model+"\n(Benchmark on "+idxname+")"
    """
    title1=ticker_name(ticker)+": "+model+"\n(基于"+ticker_name(scope)+")"
   
    #转换索引类型为DatetimeIndex，便于后续处理
    """
    import pandas as pd
    betas['Date']=betas.index
    betas['Date']=pd.to_datetime(betas['Date'])
    betas.set_index('Date',inplace=True)
    """

    #获得列明
    betalist=betas.columns.values.tolist()
    beta1=betalist[0]
    beta2=betalist[1]

    try:
        plt.plot(betas[beta1],label=beta1,marker='o',color='red')
        plt.plot(betas[beta2],label=beta2,marker='*',linewidth=2,ls='-.',color='blue')
    except:
        print("  #Error(draw2_betas): no available data for drawing!")
        return
    plt.axhline(y=1.0,color='b',linestyle=':',label='市场线')  
    plt.title(title1,fontsize=12,fontweight='bold')
    plt.ylabel("贝塔系数",fontsize=12,fontweight='bold')
    
    plt.gcf().autofmt_xdate() # 优化标注（自动倾斜）
    plt.gca().set_facecolor('whitesmoke')
    
    #plt.xticks(rotation=30)
    plt.legend(loc='best')    
    
    import datetime; today = datetime.date.today()
    plt.xlabel("数据来源：新浪，"+str(today))    
    
    plt.show()       
    
    return

if __name__=='__main__':
    model="ML Beta Adjustment"
    scope="SP500"
    ticker="AAPL"
    draw2_betas(model,scope,ticker,betas)


#==============================================================================
def get_beta_SW(stkcd,mktidx,yearlist,printout=True,graph=True):
    """
    函数功能：使用SW方法调整一只股票的CAPM模型贝塔系数
    输入参数：
    stkcd: 股票代码
    mktidx: 指数代码
    yearlist：年度列表，列出其中期间的贝塔系数
    输出数据：显示CAPM市场模型回归的beta, 以及调整后的beta系数
    返回数据：CAPM市场模型回归的beta, 以及调整后的beta系数
    """

    #仅为测试用，完成后应立即注释掉
    #stkcd='0700.HK'
    #mktidx='^HSI'
    #yearlist=['2015','2016','2017','2018']
    
    #生成开始结束日期
    Y4=str(int(yearlist[0])-1)
    start=Y4+'-01-01'
    end=yearlist[-1]+'-12-31'   
        
    #读取股价并准备好收益率数据
    try:
        R=prepare_capm(stkcd,mktidx,start,end)
    except:
        print("  #Error(get_beta_SW): preparing CAPM data failed!")
        return None

    if (R is None):
        print("  #Error(get_beta_SW): server time out")
        return None
    if (len(R) == 0):
        print("  #Error(get_beta_SW): server returned empty data")
        return None

    #用于保存beta(CAPM)和beta(SW)
    import pandas as pd
    betas=pd.DataFrame(columns=('Year','Beta(CAPM)','Beta(SW)'))

    #计算Scholes-William调整
    R['Close_x+1']=R['Close_x'].shift(1)    
    R['Close_x-1']=R['Close_x'].shift(-1)
    R=R.dropna()    #stats.linregress不接受空缺值

    from scipy import stats    
    for year in yearlist:
        r=R[R['Year']==year]
        if len(r) != 0:
            output=stats.linregress(r['Close_x'],r['Close_y'])
            (beta0,alpha,r_value,p_value,std_err)=output

            output=stats.linregress(r['Close_x+1'],r['Close_y'])
            (beta1,alpha,r_value,p_value,std_err)=output 

            output=stats.linregress(r['Close_x-1'],r['Close_y'])
            (beta_1,alpha,r_value,p_value,std_err)=output    

            output=stats.linregress(r['Close_x-1'],r['Close_x'])
            (rou,alpha,r_value,p_value,std_err)=output    

            beta_SW=(beta_1+beta0+beta1)/(1.0+2.0*rou)
            row=pd.Series({'Year':year,'Beta(CAPM)':beta0,'Beta(SW)':beta_SW})
            try:
                betas=betas.append(row,ignore_index=True)
            except:
                betas=betas._append(row,ignore_index=True)
    
    betas.set_index(["Year"], inplace=True)
    
    if printout == True: printdf_betas(betas,2)
    if graph == True:
        model="贝塔系数的Scholes-Williams调整法"
        draw2_betas(model,mktidx,stkcd,betas)
    
    return betas

    
if __name__=='__main__':
    yearlist=gen_yearlist('2010','2019')
    betas_AAPL=get_beta_SW('AAPL','^GSPC',yearlist)
    
    model="SW Beta Adjustment"
    scope="SP500"
    ticker="AAPL"
    draw2_betas(model,scope,ticker,betas_AAPL)

#==============================================================================
def get_beta_dimson(stkcd,mktidx,yearlist,printout=True,graph=True):
    """
    函数功能：使用Dimson(1979)方法调整一只股票的CAPM模型贝塔系数
    输入参数：
    stkcd: 股票代码
    mktidx: 指数代码
    yearlist：年度列表，用于计算年度贝塔系数
    输出数据：显示CAPM市场模型回归的beta, 以及调整后的beta系数
    返回数据：CAPM的beta, 以及调整后的beta系数
    """

    #仅为测试用，完成后应立即注释掉
    #stkcd='0700.HK'
    #mktidx='^HSI'
    #yearlist=['2015','2016','2017','2018']
    
    #生成开始结束日期
    Y4=str(int(yearlist[0])-1)
    start=Y4+'-01-01'
    end=yearlist[-1]+'-12-31'  
        
    #读取股价并准备好收益率数据
    try:
        R=prepare_capm(stkcd,mktidx,start,end)
    except:
        print("  #Error(get_beta_dimson): preparing CAPM data failed!")
        return None

    if (R is None):
        print("  #Error(get_beta_dimson): server did not respond")
        return None
    if (len(R) == 0):
        print("  #Error(get_beta_dimson): server returned empty data")
        return None

    #用于保存beta(CAPM)和beta(Dimson)
    import pandas as pd
    betas=pd.DataFrame(columns=('Year','Beta(CAPM)','Beta(Dimson)'))

    #计算Dimson(1979)调整
    R['Close_x+1']=R['Close_x'].shift(1)    
    R['Close_x-1']=R['Close_x'].shift(-1)   
    R=R.dropna()

    from scipy import stats    
    import statsmodels.api as sm
    for year in yearlist:
        r=R[R['Year']==year]
        if len(r) != 0:   
            output=stats.linregress(r['Close_x'],r['Close_y'])
            (beta_capm,alpha,r_value,p_value,std_err)=output               
            
            #三个解释变量
            RX=r[['Close_x-1','Close_x','Close_x+1']]
            X1=sm.add_constant(RX)	#要求回归具有截距项
            Y=r['Close_y']
            model = sm.OLS(Y,X1)	#定义回归模型，X1为多元矩阵
            results = model.fit()	#进行OLS回归

            (alpha,beta_1,beta0,beta1)=results.params	#提取回归系数
            beta_dimson=beta_1+beta0+beta1            

            row=pd.Series({'Year':year,'Beta(CAPM)':beta_capm, \
                           'Beta(Dimson)':beta_dimson})
            try:
                betas=betas.append(row,ignore_index=True)
            except:
                betas=betas._append(row,ignore_index=True)

    betas.set_index(["Year"], inplace=True)

    if printout == True: printdf_betas(betas,2)
    if graph == True:
        model="贝塔系数的Dimson调整法"
        draw2_betas(model,mktidx,stkcd,betas)

    return betas
    
if __name__=='__main__':
    yearlist=gen_yearlist('2010','2019')
    betas_MSFT=get_beta_dimson('MSFT','^GSPC',yearlist)
    
    model="Dimson Beta Adjustment"
    scope="SP500"
    ticker="MSFT"
    draw2_betas(model,scope,ticker,betas_MSFT)

    betas_MSFT2=get_beta_dimson('MSFT','^DJI',yearlist)
    
    model="Dimson Beta Adjustment"
    scope="DJIA"
    ticker="MSFT"
    draw2_betas(model,scope,ticker,betas_MSFT2)

#==============================================================================
#==============================================================================
#==============================================================================

def prepare_hamada_patch_is(ticker):
    """
    在雅虎财经接口获取利润表数据失败时，改从tushare获取
    获取的项目：所得税费用，税前利润
    """
    import pandas as pd
    import tushare as ts
    pro=init_ts()
    
    #财报期限
    import datetime
    today=datetime.date.today()
    thisyear=today.year
    fouryrsago=thisyear-4-2
    fromdate=str(fouryrsago)+"0101"
    todate=str(thisyear)+"1231"

    #利润表
    ticker1=ticker.upper()
    suffix=ticker1[-3:]
    if suffix in ['.SS']:
        ticker1=ticker1.replace('.SS','.SH',1)
    if not (suffix in ['.SS','.SZ']):
        print("  #Error(prepare_hamada_patch_is): no financials available for",ticker)
        return None
    
    fis=pro.income(ts_code=ticker1,start_date=fromdate,end_date=todate)
    #去除非年报
    stripfmt=lambda x:(x.strip())[-4:]
    fis['yrtag']=fis['end_date'].apply(stripfmt)
    fis1=fis[fis['report_type']=='1']   #合并报表
    fis2=fis1[fis1['yrtag']=="1231"]    #年报
    fis3=fis2.drop_duplicates(subset=['end_date'],keep='first') #去重
    fis4=fis3   #保留最新4年，与yfinance结果保持一致
    fis4.sort_values(by=['end_date'],ascending=True,inplace=True)   #升序排序

    #重建索引
    fis4['date']=pd.to_datetime(fis4['end_date'])
    fis4.set_index('date',inplace=True)

    #提取需要的项目：所得税费用，税前利润
    fis4['Income Tax Expense']=fis4['income_tax']
    fis4['Income Before Tax']=fis4['total_profit']
    fis5=fis4[['Income Tax Expense','Income Before Tax']].copy()

    return fis5

if __name__=='__main__':
    ticker="600519.SS"    


#==============================================================================
def prepare_hamada_patch_bs(ticker):
    """
    在雅虎财经接口获取资产负债表数据失败时，改从tushare获取
    获取的项目：负债合计，股东权益合计
    """
    import pandas as pd
    import tushare as ts
    pro=init_ts()
    
    #财报期限
    import datetime
    today=datetime.date.today()
    thisyear=today.year
    fouryrsago=thisyear-4-2
    fromdate=str(fouryrsago)+"0101"
    todate=str(thisyear)+"1231"

    #利润表
    ticker1=ticker.upper()
    suffix=ticker1[-3:]
    if suffix in ['.SS']:
        ticker1=ticker1.replace('.SS','.SH',1)
    if not (suffix in ['.SS','.SZ']):
        print("  #Error(prepare_hamada_patch_bs): no financials available for",ticker)
        return None
    
    fis=pro.balancesheet(ts_code=ticker1,start_date=fromdate,end_date=todate)
    #去除非年报
    stripfmt=lambda x:(x.strip())[-4:]
    fis['yrtag']=fis['end_date'].apply(stripfmt)
    fis1=fis[fis['report_type']=='1']   #合并报表
    fis2=fis1[fis1['yrtag']=="1231"]    #年报
    fis3=fis2.drop_duplicates(subset=['end_date'],keep='first') #去重
    fis4=fis3   #保留最新4年，与yfinance结果保持一致
    fis4.sort_values(by=['end_date'],ascending=True,inplace=True)   #升序排序

    #重建索引
    fis4['date']=pd.to_datetime(fis4['end_date'])
    fis4.set_index('date',inplace=True)

    #提取需要的项目：所得税费用，税前利润
    fis4['Total Liab']=fis4['total_liab']
    fis4['Total Stockholder Equity']=fis4['total_hldr_eqy_inc_min_int']
    fis5=fis4[['Total Liab','Total Stockholder Equity']].copy()

    return fis5

if __name__=='__main__':
    ticker="600519.SS"    


#==============================================================================
if __name__ =="__main__":
    ticker='0700.HK'

def prepare_hamada_yearly_yahoo(ticker):
    """
    功能：从雅虎财经下载财报数据，计算hamada模型需要的因子
    局限：只能下载最近4年的财报
    输入：股票代码
    输出：
        寻找数据项：所得税费用，税前利润，计算实际税率；
        总负债，所有者权益，计算财务杠杆
    数据框, CFLB，贝塔Lev对贝塔Unlev的倍数
    年度列表
    """
    print("... Searching for financial information, please wait ...")
    import yfinance as yf
    stock=yf.Ticker(ticker)    

    #利润表
    try:
        is0=stock.financials
        is1=is0.T
    except:
        is1=prepare_hamada_patch_is(ticker)
    
    if len(is0)==0: #yfinance失效
        is1=prepare_hamada_patch_is(ticker)

    is1['income tax expense']=is1['Income Tax Expense'].astype('float')
    is1['income before tax']=is1['Income Before Tax'].astype('float')
    is1['tax rate']=is1['income tax expense']/is1['income before tax']

    import pandas as pd
    is1['date']=pd.to_datetime(is1.index)
    is1.set_index(["date"], inplace=True)
    is2=is1.sort_index(axis=0,ascending=True)
    tax=pd.DataFrame(is2['tax rate'])

    #资产负债表
    try:
        bs0=stock.balance_sheet
        bs1=bs0.T
    except:
        bs1=prepare_hamada_patch_bs(ticker)
    if len(bs0)==0: #yfinance失效
        bs1=prepare_hamada_patch_bs(ticker)    

    bs1['total liabilities']=bs1['Total Liab'].astype('float')
    bs1['total equities']=bs1["Total Stockholder Equity"].astype('float')
    bs1['lev ratio']=bs1['total liabilities']/bs1['total equities']
    bs1['date']=pd.to_datetime(bs1.index)
    bs1.set_index(['date'],inplace=True)
    bs2=bs1.sort_index(axis=0,ascending=True)
    lev=pd.DataFrame(bs2['lev ratio'])
    
    #合成，计算
    fac=pd.merge(lev,tax,how='left',left_index=True,right_index=True)
    fac['CFLB%']=1/(1+(1/fac['lev ratio'])*(1/abs(1-fac['tax rate'])))*100
    fac['lev_unlev']=1+fac['lev ratio']*(1-fac['tax rate'])
    fac['year']=fac.index.strftime("%Y")
    yearlist=list(fac['year'])

    return fac,yearlist

if __name__ =="__main__":
    ticker="600519.SS"
    ticker="AAPL"
    ticker='000002.SZ'
    fac,yl=prepare_hamada_yearly_yahoo("MSFT")

#==============================================================================
if __name__ =="__main__":
    stkcd='0700.HK'
    mktidx='^HSI'
    yearlist=['2015','2016','2017','2018']


def get_beta_hamada(stkcd,mktidx,yearlist,printout=True,graph=True):
    """
    函数功能：使用Hamada(1972)方法，计算无杠杆贝塔系数
    输入参数：
    stkcd: 股票代码
    mktidx: 指数代码
    yearlist：年度列表，用于计算年度贝塔系数
    输出数据：显示CAPM市场模型回归的beta, 以及调整后的beta系数
    返回数据：CAPM的beta, Hamada beta，CFLB(债务融资对CAPM beta系数的贡献率)
    """
    
    #计算Hamada参数，并返回可用的年度列表
    fac,yearlist=prepare_hamada_yearly_yahoo(stkcd)
    if fac is None:
        print("#Error(get_beta_hamada): no financial info available for",stkcd)
        return None
    
    #生成开始结束日期
    Y4=str(int(yearlist[0])-1)
    start=Y4+'-01-01'
    end=yearlist[-1]+'-12-31'  
        
    #读取股价并准备好收益率数据
    try:
        R=prepare_capm(stkcd,mktidx,start,end)
    except:
        print("  #Error(get_beta_hamada): preparing CAPM data failed!")
        print("Info:",stkcd,mktidx,yearlist)              
        return None

    if (R is None):
        print("  #Error(get_beta_hamada): server time out")
        return None
    if (len(R) == 0):
        print("  #Error(get_beta_hamada): server returned empty data")
        return None
    R=R.dropna()
    
    #用于保存beta(CAPM)和beta(Hamada)
    import pandas as pd
    betas=pd.DataFrame(columns=('Year','Beta(CAPM)','Beta(Unlevered)','CFLB%'))

    from scipy import stats    
    for year in yearlist:
        r=R[R['Year']==year]
        if len(r) != 0:   
            output=stats.linregress(r['Close_x'],r['Close_y'])
            (beta_capm,alpha,r_value,p_value,std_err)=output               
            
            #Hamada无杠杆因子
            lev_unlev=fac[fac['year']==year]['lev_unlev'].values[0]
            beta_hamada=beta_capm/lev_unlev
            cflb=fac[fac['year']==year]['CFLB%'].values[0]            

            row=pd.Series({'Year':year,'Beta(CAPM)':beta_capm, \
                           'Beta(Unlevered)':beta_hamada,'CFLB%':cflb})
            try:
                betas=betas.append(row,ignore_index=True)
            except:
                betas=betas._append(row,ignore_index=True)

    betas.set_index(["Year"], inplace=True)

    if printout == True: 
        printdf_betas(betas,2)
    if graph == True:
        model="Hamada Unlevered Beta"
        draw2_betas(model,mktidx,stkcd,betas)
        
        #绘制CFLB
        if len(betas)<=1: return betas
        
        plt.plot(betas['CFLB%'],marker='o',color='red',lw=3)
        
        bmin=min(list(betas['CFLB%']))
        bmax=max(list(betas['CFLB%']))
        axhmin=(int(bmin/10)+1)*10
        if bmin <= axhmin <= bmax:
            plt.axhline(y=axhmin,color='b',linestyle=':') 
        axhmax=(int(bmax/10))*10
        if bmin <= axhmax <= bmax:
            plt.axhline(y=axhmax,color='b',linestyle=':')         
        
        title1=stkcd+": Contribution of Financial Leverage to Beta"+ \
            "\n(Benchmark on Market Index "+mktidx+")"
        plt.title(title1,fontsize=12,fontweight='bold')
        plt.ylabel("CFLB %",fontsize=12,fontweight='bold')
        #plt.legend(loc='best')         
        plt.grid(ls='-.')
        #查看可用的样式：print(plt.style.available)
        #样式：bmh(好),classic,ggplot(好，图大)，tableau-colorblind10，
        #样式：seaborn-bright，seaborn-poster，seaborn-whitegrid
        plt.style.use('bmh')
        
        plt.gca().set_facecolor('whitesmoke')
        plt.show()         

    return betas
    
if __name__=='__main__':
    stkcd='000002.SZ'
    mktidx='000001.SS'
    yearlist=gen_yearlist('2010','2019')
    betas1=get_beta_hamada('MSFT','^GSPC',yearlist)

#==============================================================================
#==============================================================================
#==============================================================================
def draw_hamada_factors(stkcd,mktidx,betas):
    """
    功能：绘制Hamada模型因子的变化折线图，企业实际所得税税率，资产负债率，CFLB
    """
    if len(betas)<=1: return
    
    #计算资产负债率：由 D/E到 D/(A=D+E)
    betas['Debt/Assets%']=1/(1+1/(betas['Debt Ratio%']/100))*100

    #fig=plt.figure(figsize=(12.8,6.4))
    fig=plt.figure()
    ax1=fig.add_subplot(111)
    ax1.plot(betas['CFLB%'],marker='o',color='green',lw=3,label='CFLB%')
    ax1.plot(betas['Debt/Assets%'],marker='o',color='red',lw=2,ls='--', \
             label='Debt/Assets%')
    ax1.set_ylabel("CFLB%, Debt/Assets%")
    ax1.legend(loc='upper left') 
    ax1.set_xticklabels(betas.index,rotation=45)
    
    ax2=ax1.twinx()
    ax2.plot(betas['Tax Rate%'],marker='o',color='black',lw=2,ls='-.', \
             label='Income Tax%')
    ax2.set_ylabel('Income Tax%')  
    ax2.legend(loc='lower right')
    ax2.set_xticklabels(betas.index,rotation=45)
    
    title1=stkcd+": Impact of Hamada Factors on Beta"+ \
            "\n(Benchmark on Market Index "+mktidx+")"
    plt.title(title1,fontsize=12,fontweight='bold')
    plt.style.use('ggplot')
    
    plt.gca().set_facecolor('whitesmoke')
    plt.show()     
    
    return
#==============================================================================
#==============================================================================
#==============================================================================
if __name__ =="__main__":
    stkcd='0700.HK'
    stkcd='AAPL'
    stkcd='GS'
    stkcd='BA'
    mktidx='^HSI'
    stkcd='000002.SZ'
    stkcd='600606.SS'
    mktidx='000001.SS'

def get_beta_hamada2(stkcd,mktidx,printout=True,graph=True):
    """
    函数功能：使用Hamada(1972)方法，计算无杠杆贝塔系数，绘图
    输入参数：
    stkcd: 股票代码
    mktidx: 指数代码
    输出数据：显示CAPM市场模型回归的beta, 以及调整后的beta系数
    返回数据：CAPM的beta, Hamada beta，CFLB(债务融资对CAPM beta系数的贡献率)
    """
    
    #计算Hamada参数，并返回可用的年度列表
    fac=prepare_hamada_yahoo(stkcd)
    if fac is None:
        print("  #Error(get_beta_hamada2): no financial info available for",stkcd)
        return None
    datecvt=lambda x: str(x.strftime("%Y-%m-%d"))
    fac['fsdate']=fac.index.date
    fac['fsdate']=fac['fsdate'].apply(datecvt)
    
    #生成开始结束日期
    end0=fac.index[-1]
    end=date_adjust(end0,adjust=14)
    start0=fac.index[0]
    start=date_adjust(start0,adjust=-366)
        
    #读取股价并准备好收益率数据
    try:
        R=prepare_capm(stkcd,mktidx,start,end)
    except:
        print("  #Error(get_beta_hamada2): preparing CAPM data failed for",stkcd,mktidx)
        return None
    if (R is None) or (len(R) == 0):
        print("  #Error(get_beta_hamada2): retrieved empty info in CAPM for",stkcd,mktidx)
        return None
    R=R.dropna()
    R['prcdate']=R.index.date
    R['prcdate']=R['prcdate'].apply(datecvt)
    
    #用于保存beta(CAPM)和beta(Hamada)
    import pandas as pd
    betas=pd.DataFrame(columns=('Date','Beta(CAPM)','Beta(Unlevered)','CFLB%'))
    fsdatelist=list(fac['fsdate'])
    from scipy import stats    
    for d in fsdatelist:
        dstart=date_adjust(d,adjust=-365)
        r=R[R['prcdate'] >= dstart]
        r=r[r['prcdate'] <= d]
        if len(r) != 0:   
            output=stats.linregress(r['Close_x'],r['Close_y'])
            (beta_capm,alpha,r_value,p_value,std_err)=output               
            
            #Hamada无杠杆因子
            lev_unlev=fac[fac['fsdate']==d]['lev_unlev'].values[0]
            beta_hamada=beta_capm/lev_unlev
            cflb=fac[fac['fsdate']==d]['CFLB%'].values[0]            

            row=pd.Series({'Date':d,'Beta(CAPM)':beta_capm, \
                           'Beta(Unlevered)':beta_hamada,'CFLB%':cflb})
            try:
                betas=betas.append(row,ignore_index=True)
            except:
                betas=betas._append(row,ignore_index=True)
    betas.set_index(["Date"], inplace=True)

    #打印
    if printout == True: 
        printdf_betas(betas,2)
    
    #绘图：两种杠杆对比图，CFLB图
    if graph == True:
        
        #绘制Hamada对比图
        model="滨田无杠杆贝塔系数"
        draw2_betas(model,mktidx,stkcd,betas)
        
        #绘制CFLB单图
        if len(betas)<=1: 
            print("  #Notice(get_beta_hamada2): too few info for graphics of",stkcd)
            return betas
        
        plt.plot(betas['CFLB%'],marker='o',color='red',lw=3,label='CFLB%')
        
        #绘制均值虚线
        cflb_avg=betas['CFLB%'].mean()
        cflb_avg_txt='均值: '+str(round(cflb_avg,1))+'%'
        plt.axhline(y=cflb_avg,color='b',linestyle=':',label=cflb_avg_txt)
        
        title1=ticker_name(stkcd)+": 财务杠杆对于贝塔系数的贡献度(CFLB)"
        #plt.title(title1,fontsize=12,fontweight='bold')
        plt.title(title1)
        #plt.ylabel("CFLB %",fontsize=12,fontweight='bold')
        footnote="注: 基于"+ticker_name(mktidx)
        
        import datetime; today = datetime.date.today()
        footnote2="\n数据来源: 新浪,"+str(today)
        plt.xlabel(footnote+footnote2)
        
        plt.grid(ls='-.')
        #查看可用的样式：print(plt.style.available)
        #样式：bmh(好),classic,ggplot(好，图大)，tableau-colorblind10，
        #样式：seaborn-bright，seaborn-poster，seaborn-whitegrid
        plt.style.use('bmh')
        plt.gcf().autofmt_xdate() # 优化标注（自动倾斜）
        plt.gca().set_facecolor('whitesmoke')
        plt.legend(loc='best')
        plt.show(); plt.close()
        
        #绘制CFLB+财务杠杆双图
        df1=betas; df2=fac.set_index(["fsdate"])
        ticker1=ticker2=stkcd
        colname1='CFLB%'; colname2='lev ratio'
        label1='CFLB%'; label2='财务杠杆'
        titletxt=ticker_name(stkcd)+": CFLB与财务杠杆之间的关系"
        footnote='注: 这里的财务杠杆使用的是负债/所有者权益'
        
        plot_line2_twinx(df1,ticker1,colname1,label1,df2,ticker2,colname2,label2, \
        titletxt,footnote+footnote2)
        
        #绘制CFLB+税率双图
        #df1=betas; df2=fac.set_index(["fsdate"])
        #ticker1=ticker2=stkcd
        colname1='CFLB%'; colname2='tax rate'
        label1='CFLB%'; label2='实际税率'
        titletxt=ticker_name(stkcd)+": CFLB与税率之间的关系"
        footnote='注: 这里使用的是实际税率'
        
        plot_line2_twinx(df1,ticker1,colname1,label1,df2,ticker2,colname2,label2, \
        titletxt,footnote+footnote2)
            
    return betas
    
if __name__=='__main__':
    betas1=get_beta_hamada2('MSFT','^GSPC')

#==============================================================================
if __name__ =="__main__":
    ticker='0700.HK'
    ticker="600519.SS"
    ticker="AAPL"
    ticker="BA"

def prepare_hamada_yahoo(ticker):
    """
    功能：从雅虎财经下载财报数据，计算hamada模型需要的因子
    局限：只能下载最近4年+4个季度的财报
    输入：股票代码
    输出：
        寻找数据项：所得税费用，税前利润，计算实际税率；
        总负债，所有者权益，计算财务杠杆
    数据框, CFLB，贝塔Lev对贝塔Unlev的倍数
    年度列表
    """
    print("...Searching for financial information, please wait ...")
    
    #利润表
    try:
        import siat.financial_statements as fs
        is1=fs.get_income_statements(ticker) 
    except:
        print("  #Error(prepare_hamada_yahoo): failed to retrieve income info of",ticker)
        return None
    if (is1 is None) or (len(is1)==0): 
        print("  #Error(prepare_hamada_yahoo): retrieve empty income info of",ticker)
        return None
    
    is1['tax rate']=is1['TaxRateForCalcs'].astype('float')
    is1['ticker']=is1.index
    is1['date']=is1['asOfDate']
    is1.set_index(["date"], inplace=True)
    is1.sort_index(axis=0,ascending=True,inplace=True)
    
    import pandas as pd
    tax=pd.DataFrame(is1['tax rate'])

    #资产负债表
    try:
        bs1=fs.get_balance_sheet(ticker)
    except:
        print("  #Error(prepare_hamada_yahoo): failed to retrieve balance sheet of",ticker)
        return None
    if (bs1 is None) or (len(bs1)==0):
        print("  #Error(prepare_hamada_yahoo): retrieve empty balance sheet of",ticker)
        return None

    bs1['lev ratio']=bs1['TotalLiabilities']/bs1['TotalEquities']
    bs1['date']=bs1['asOfDate']
    bs1.set_index(['date'],inplace=True)
    bs1.sort_index(axis=0,ascending=True,inplace=True)
    lev=pd.DataFrame(bs1['lev ratio'])
    
    #合成，计算
    fac=pd.merge(lev,tax,how='left',left_index=True,right_index=True)
    fac['CFLB%']=1/(1+(1/fac['lev ratio'])*(1/abs(1-fac['tax rate'])))*100
    fac['lev_unlev']=1+fac['lev ratio']*(1-fac['tax rate'])

    return fac

if __name__ =="__main__":
    fac,yl=prepare_hamada_yahoo("MSFT")

#==============================================================================

if __name__=='__main__':
    tickers = ['000858.SZ','600779.SS','000596.SZ','603589.SS']
    market_index="000001.SS"

def compare_mhamada(tickers,market_index="000001.SS"):
    """
    功能：计算多只股票的财务杠杆对贝塔系数贡献度比率CFLB，并绘图对比
    """    
    #检查tickers是否为列表且不少于两只股票
    
    #隐藏print输出
    import os,sys
    class HiddenPrints:
        def __enter__(self):
            self._original_stdout = sys.stdout
            sys.stdout = open(os.devnull, 'w')

        def __exit__(self, exc_type, exc_val, exc_tb):
            sys.stdout.close()
            sys.stdout = self._original_stdout
    
    import pandas as pd
    df=pd.DataFrame() 
    print("Starting to retrieve and calculate Hamada ratios, please wait ......")
    for t in tickers:
        
        with HiddenPrints():
            df_tmp=get_beta_hamada2(t,market_index,printout=False,graph=False)
        
        if df_tmp is None:
            print("  Warning(compare_mhamada): data not available for",t)
            continue
        else:
            dft=df_tmp[['CFLB%']]
            dft.rename(columns={'CFLB%':ticker_name(t)},inplace=True)
            
        if len(df)==0:
            #第一个
            df=dft
        else:
            df=pd.merge(df,dft,left_index=True,right_index=True)

    if len(df)==0:
        print("  Warning(compare_mhamada): no data available for",tickers)        
        return None
        
    #绘制多条曲线
    import datetime; today = datetime.date.today()
    
    lang=check_language()
    if lang == 'English':
        
        y_label='CFLB%'
        footnote0='CFLB: Contribution of Financial Leverage to Beta'
        x_label=footnote0+'\n'+"Source: sina/stooq, "+str(today)
        title_txt="Compare Multiple CFLB"
    else:
        y_label='CFLB%'
        footnote0='CFLB：财务杠杆对贝塔系数的贡献度'
        x_label=footnote0+'\n'+"数据来源: 新浪/stooq，"+str(today)
        title_txt="比较多只证券的CFLB指标"

    draw_lines(df,y_label,x_label,axhline_value=0,axhline_label='', \
               title_txt=title_txt,data_label=False)

    return df

if __name__=='__main__':
    tickers = ['000858.SZ','600779.SS','000596.SZ','603589.SS','000001.SS']
    df=compare_mhamada(tickers,market_index)

#==============================================================================
#==============================================================================
#==============================================================================
#==============================================================================
#==============================================================================











    