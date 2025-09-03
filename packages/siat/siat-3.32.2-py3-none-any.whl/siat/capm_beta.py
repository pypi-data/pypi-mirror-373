# -*- coding: utf-8 -*-
"""
本模块功能：CAPM模型贝塔系数计算
所属工具包：证券投资分析工具SIAT 
SIAT：Security Investment Analysis Tool
创建日期：2018年7月16日
最新修订日期：2020年1月15日
作者：王德宏 (WANG Dehong, Peter)
作者单位：北京外国语大学国际商学院
作者邮件：wdehong2000@163.com
版权所有：王德宏
用途限制：仅限研究与教学使用，不可商用！商用需要额外授权。
特别声明：作者不对使用本工具进行证券投资导致的任何损益负责！
"""

#==============================================================================
import warnings; warnings.filterwarnings('ignore')
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
def get_price_excel(ticker,fromdate,todate,excelfile,sheetname='Sheet1'):
    """
    功能：抓取股价，保存到Excel文件中
    输出：指定收盘价格序列，最新日期的股价排列在前
    ticker: 股票代码。大陆股票代码加上后缀.SZ或.SS，港股代码去掉前导0加后缀.HK
    fromdate: 样本开始日期，尽量远的日期，以便取得足够多的原始样本
    todate: 样本结束日期，既可以是今天日期，也可以是一个历史日期
    excelfile：保存到Excel文件名，含目录。如果目录不存在，将会导致错误。
    """
    
    #仅为调试用的函数入口参数，正式使用前需要注释掉！
    #ticker='000300.SS'
    #fromdate='01/01/2018'
    #todate='06/30/2019'
    #---------------------------------------------
    
    #仅为测试使用
    #ticker='601857.SS'
    #fromdate='2019-1-1'
    #todate='2019-8-31'
    #excelfile='C:/temp/myexcel1.xlsx'
    #sheetname='601857.SS'

    price=get_price(ticker,fromdate,todate)
    if price is None:
        print("  #Error(get_price_excel): failed to retrieve stock data")
        print("  Information:",ticker,fromdate,todate) 
        return
    try:
        price.to_excel(excelfile,sheetname,encoding='utf-8')             
    except:
        print("  #Error((get_price_excel): failed to stock data to excel file")        
        print("  Information:",excelfile,sheetname)
        return
    print("***Results saved in",excelfile,"with sheet",sheetname)
    return 
    

if __name__=='__main__':
    df601857=get_price_excel('601857.SS','2019-1-1','2019-12-31', \
                             'C:/temp/myexcel1.xlsx','601857.SS')


#==============================================================================
def prepare_capm_data(stkcd,mktidx,start,end):
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
    #stkcd='600028.SS'; mktidx='000001.SS'
    #start="12/31/2011"; end="12/31/2018"

    #抓取股价和指数
    import siat.security_prices as ssp
    stock=get_price(stkcd,start,end)
    if stock is None:
        print("  #Error(prepare_capm_data): failed to get stock price")
        print("  Information:",stkcd,start,end)              
        return None    
    market=get_price(mktidx,start,end)
    if market is None:
        print("  #Error(prepare_capm_data): failed to get market index")
        print("  Information:",mktidx,start,end)              
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

#==============================================================================
def capm_beta(ticker,mktidx,start,end='today'):
    """
    函数功能：计算一只股票的静态CAPM模型贝塔系数
    输入参数：
    ticker: 股票代码
    mktidx: 指数代码
    start：使用股票价格数据的开始日期，MM/DD/YYYY
    end：使用股票价格数据的结束日期，MM/DD/YYYY
    输出数据：
    显示CAPM市场模型回归的alpha, beta, 以及显著性和拟合优度
    无返回数据
    """
    start,end=start_end_preprocess(start,end)
        
    #读取股价并准备好收益率数据
    R=prepare_capm_data(ticker,mktidx,start,end)
    if R is None:
        print("  #Error(capm_beta): failed to prepare capm data")
        print("  Info:",ticker,mktidx,start,end)              
        return   

    #全数据OLS回归
    from scipy import stats 
    (beta,alpha,r_value,p_value,std_err)= \
        stats.linregress(R['Close_x'],R['Close_y'])

    #显示回归结果
    print(" \n===== 计算CAPM贝塔系数 =====")
    print("回归模型：市场模型")
    print(equalwidth("股票",16), ticker_name(ticker))
    print(equalwidth("市场指数",16), ticker_name(mktidx))
    print(equalwidth("样本期间开始于",16), start)
    print(equalwidth("样本期间结束于",16), end)
    print(equalwidth("截距项",16), round(alpha,4))
    print(equalwidth("贝塔系数",16), round(beta,4))
    print(equalwidth("R-square",16), round(r_value**2,4))
    print(equalwidth("p-value",16), round(p_value,4))
    
    import datetime
    today = datetime.date.today()
    print("*数据来源: 新浪/stooq/fred,",today)

    return  beta  
    
if __name__=='__main__':
    capm_beta('002504.SZ','000001.SS','12/31/2011','12/31/2018')    

#==============================================================================

def plot_trend(titletxt,footnotetxt,df,power=1,axhline_value=1,axhline_label=''):
    """
    功能：绘制散点数据的平滑曲线图及其趋势线
    titletxt: 标题
    footnotetxt：脚注
    df: 数据框，其索引为字符型年份，第1列与年份对应的数值1，
    第2列与年份对应的数值2，。。。
    power: 趋势线拟合的幂阶数，默认为三阶多项式
    """
    #将字符型年份转化为整数型
    yearstr=df.index
    year=[]
    for t in yearstr:
        tt=int(t)
        year=year+[tt]    
    
    #取得列名
    rowlist=df.columns.values.tolist()
    n=len(rowlist)
    
    import numpy as np
    import scipy.interpolate as itp

    #由于年度为连续整数，为插值方便，先将所有年度放大10倍
    year0=[]
    for t in year:
        tt=t*10
        year0=year0+[tt]

    #形成用于插值的连续整数自变量xx
    x1=year0[0]
    x2=year0[-1]+1
    xx=np.array(range(x1,x2,1))   
    
    #将用于插值的自变量缩小10倍，以便自变量在x轴上的尺度统一
    x=[]
    for t in xx:
        tt=t/10.0
        x=x+[tt]
    
    #循环处理每个因变量
    for i in np.array(range(0,n,1)):
        number=df[rowlist[i]]

        #进行插值: linear=线性插值, cubic=立方插值
        y=itp.interp1d(year0,number,kind='cubic')
        #生成插值出来的模拟数据因变量
        y2=y(xx)
        #绘图1：插值出来的大量模拟点构成的平滑曲线
        plt.plot(x,y2)
        #绘图2：原数据点

        #进行拟合: 1=线性拟合, 2=二次拟合，3=三次拟合
        p=np.polyfit(year0,number,power)
        #生成拟合出来的模拟数据因变量
        p2=np.polyval(p,xx)
        #绘图2：拟合出来的大量模拟点构成的平滑趋势曲线
        plt.plot(x,p2,linestyle=':',linewidth=3)

        #绘图3：原数据点
        plt.plot(year,number,'*',label=rowlist[i])
    
    #是否绘制水平线
    if axhline_label !="":
        if '市场' in axhline_label:
            axhline_label=''
        plt.axhline(y=axhline_value,label=axhline_label,color='black',linestyle=':',linewidth=2)  
        #plt.axhline(y=axhline_value,color='purple',linestyle=':',linewidth=1.5)
    
    #x轴刻度：使用原数据点的自变量
    plt.xticks(year,rotation=30)
    plt.legend(loc='best')
    plt.title(titletxt)
    plt.xlabel(footnotetxt)
    
    plt.gca().set_facecolor('whitesmoke')
    plt.show()
    
    return
#==============================================================================

def capm_beta_yearly(ticker,mktidx,yearlist):
    """
    函数功能：分年度计算一只股票的CAPM模型贝塔系数
    输入参数：
    ticker: 股票代码
    mktidx: 指数代码
    yearlist: 年度列表，start日期要给第一个年份留出至少一年数据供回归使用
    输出数据：
    按年份显示CAPM市场模型回归的alpha, beta, 以及显著性和拟合优度
    无返回数据
    """
    
    #运行开始信息
    print("*** Analysing yearly CAPM betas, please wait ...")
    
    #生成开始结束日期
    Y4=str(int(yearlist[0])-1)
    start=Y4+'-01-01'
    end=yearlist[-1]+'-12-31' 
        
    #读取股价并准备好收益率数据
    R=prepare_capm_data(ticker,mktidx,start,end)
    if R is None:
        print("  #Error(capm_beta_yearly): failed to prepare capm data")
        print("  Information:",ticker,mktidx,start,end)              
        return      

    #print("\n***CAPM yearly beta: Stock_return=alpha+beta*Market_return")
    #print("Stock code:",ticker)
    #print("Market index:",mktidx)
    #print("Year Beta   R-sqr  p-value")

    #用于保存beta(CAPM)
    import pandas as pd
    betas=pd.DataFrame(columns=('Year','Beta','alpha','R-sqr','p-value'))
    
    #分年度OLS回归
    from scipy import stats
    for year in yearlist:
        #print(year,' ',end='')
        r=R[R['Year']==year]
        if len(r)==0: continue
        try:
            output=stats.linregress(r['Close_x'],r['Close_y'])
        except:
            print("  #Error(capm_beta_yearly): no data for regression")
            print("  Information:",stkcd,year,R,r)
            return             
        (beta,alpha,r_value,p_value,std_err)=output
        
        row=pd.Series({'Year':year,'Beta':beta,'alpha':alpha, \
                       'R-sqr':r_value**2,'p-value':p_value})
        try:
            betas=betas.append(row,ignore_index=True)
        except:
            betas=betas._append(row,ignore_index=True)
        #print(year,round(beta,4),round(r_value**2,3),round(p_value,4))
    
    betas['Significance']=betas['p-value'].apply(lambda x: '***' if x<0.01 \
                                                 else '**' if x<0.05 else '*' if x<0.1 else '')
    
    #设置打印标题与数据对齐
    """
    pd.set_option('display.unicode.ambiguous_as_wide', True)
    pd.set_option('display.unicode.east_asian_width', True)
    pd.set_option('display.width', 180) # 设置打印宽度(**重要**)
    
    print("\n ===== 分年度静态贝塔系数:",ticker_name(ticker),"=====")
    print(betas.to_string(index=False))
    import datetime as dt; todaydt=dt.date.today()    
    print("数据来源：新浪/stooq/fred，基于"+ticker_name(mktidx)+'，'+str(dttoday))
    print('') #空一行
    """
    titletxt="分年度静态贝塔系数: "+ticker_name(ticker)
    import datetime as dt; todaydt=dt.date.today()
    footnote="数据来源：新浪/stooq/fred，基于"+ticker_name(mktidx)+', '+str(todaydt)
    df_display_CSS(betas,titletxt=titletxt,footnote=footnote,facecolor='papayawhip', \
                   decimals=4, \
                       first_col_align='center',second_col_align='center', \
                       last_col_align='center',other_col_align='center')

    #准备绘图
    betas.set_index('Year',inplace=True)
    
    #绘图：年度贝塔系数趋势
    df=pd.DataFrame(betas['Beta'])
    title="分年度静态贝塔系数: "+ticker_name(ticker)
    foot="\n数据来源：新浪/stooq/fred，基于"+ticker_name(mktidx)+'，'+str(todaydt)
    plot_trend(title,foot,df,power=3,axhline_value=1,axhline_label='市场风险线')
    
    return betas   
    
if __name__=='__main__':
    yearlist=['2013','2014','2015','2016','2017','2018','2019']
    capm_beta_yearly('AAPL','^GSPC',yearlist)    

#==============================================================================
#新增投资组合贝塔系数部分
#==============================================================================
#==============================================================================
def prepare_capm_portfolio(tickerlist,sharelist,mktidx,start,end):
    """
    函数功能：准备计算股票投资组合CAPM模型贝塔系数的数据，并标记年度
    输入参数：
    tickerlist: 股票代码列表
    sharelist：持有份额列表
    mktidx: 市场指数代码
    start：使用股票价格数据的开始日期，'YYYY-MM-DD'
    end：使用股票价格数据的结束日期
    输出数据：
    返回数据：带年度标记的可直接用于capm模型回归的数据表
    """
        
    #仅用于调试，正式使用前应注释掉
    #tickerlist=['AAPL','MSFT']
    #sharelist=[2,1]
    #mktidx='^GSPC'
    #start="1/1/2019"; end="8/31/2019"

    #抓取投资组合股价和指数
    import siat.security_prices as ssp
    stock=get_price_portfolio(tickerlist,sharelist,start,end)
    if (stock is None) or (len(stock)==0):
        print("  #Error(prepare_capm_portfolio): failed to get stock prices")
        print("  Info:",tickerlist,start,end)              
        return None    
    market=get_price(mktidx,start,end)
    if (market is None) or (len(market)==0):
        print("  #Error(prepare_capm_portfolio): failed to get market index")
        print("  Info:",mktidx,start,end)              
        return None

    #计算日收益率
    import pandas as pd
    stkret=pd.DataFrame(stock['Close'].pct_change())
    mktret=pd.DataFrame(market['Close'].pct_change())

    #合并：mktret作为Close_x，stkret作为Close_y，去掉空缺
    R=pd.merge(mktret,stkret,how='left',left_index=True,right_index=True)
    R=R.dropna()

    #标记各个年度
    R['Year']=R.index.strftime("%Y")

    #返回带年份的股票收益率序列
    return R

#==============================================================================
def capm_beta_portfolio(tickerlist,sharelist,mktidx,start,end):
    """
    函数功能：计算投资组合的静态CAPM模型贝塔系数
    输入参数：
    tickerlist: 股票代码列表
    sharelist：持有份额列表
    mktidx: 指数代码
    start：使用股票价格数据的开始日期，MM/DD/YYYY
    end：使用股票价格数据的结束日期，MM/DD/YYYY
    输出数据：
    显示CAPM市场模型回归的截距, beta, 以及显著性和拟合优度
    无返回数据
    """
        
    #读取股价并准备好收益率数据
    R=prepare_capm_portfolio(tickerlist,sharelist,mktidx,start,end)
    if R is None:
        print("  #Error(capm_beta_portfolio): failed to prepare capm data")
        print("  Information:",tickerlist,sharelist,mktidx,start,end)              
        return   

    #全数据OLS回归
    from scipy import stats 
    (beta,alpha,r_value,p_value,std_err)= \
        stats.linregress(R['Close_x'],R['Close_y'])

    #显示回归结果
    print("\n *** Portfolio CAPM Beta Coefficient \
          \n Model: Stock_return=intercept + beta * Market_return")
    print(" Portfolio stocks:",tickerlist)
    print(" Stock portions  :",sharelist)
    print(" Market index    :",mktidx)
    print(" Intercept       :",round(alpha,4))
    print(" Portfolio beta  :",round(beta,4))
    print(" R-sqr       :",round(r_value**2,4))
    print(" p-value         :",round(p_value,4))

    return beta


#==============================================================================
def capm_beta_portfolio_yearly(tickerlist,sharelist,mktidx,yearlist):
    """
    函数功能：分年度计算投资组合的CAPM模型贝塔系数，并绘图
    输入参数：
    tickerlist: 投资组合中各个成分股的股票代码
    sharelist: 各个成分股的持股比例
    mktidx: 指数代码
    yearlist: 年度列表，start日期要给第一个年份留出至少一年数据供回归使用
    输出数据：
    按年份绘图beta
    无返回数据
    """
    
    #运行开始信息
    print("*** Analysing yearly portfolio CAPM betas, please wait ...")
    
    #生成开始结束日期
    Y4=str(int(yearlist[0])-1)
    start=Y4+'-01-01'
    end=yearlist[-1]+'-12-31' 
        
    #读取股价并准备好收益率数据
    R=prepare_capm_portfolio(tickerlist,sharelist,mktidx,start,end)
    if (R is None) or (len(R)==0):
        print("  #Error(capm_beta_portfolio_yearly): failed to prepare capm data")
        print("  Info:",tickerlist,sharelist,mktidx,start,end)              
        return      

    #用于保存beta(CAPM)和beta
    import pandas as pd
    betas=pd.DataFrame(columns=('Year','Beta','intercept','R-sqr','p-value'))
    
    #分年度OLS回归
    from scipy import stats
    for year in yearlist:
        #print(year,' ',end='')
        r=R[R['Year']==year]
        if len(r)==0: continue
        try:
            output=stats.linregress(r['Close_x'],r['Close_y'])
        except:
            print("  #Error(capm_beta_portfolio_yearly): no data for regression")
            print("  Information:",year,R,r)
            return         
        (beta,alpha,r_value,p_value,std_err)=output
        
        row=pd.Series({'Year':year,'Beta':beta,'intercept':alpha, \
                       'R-sqr':r_value**2,'p-value':p_value})
        try:
            betas=betas.append(row,ignore_index=True)
        except:
            betas=betas._append(row,ignore_index=True)

    betas['Significance']=betas['p-value'].apply(lambda x: '***' if x<0.01 \
                                                 else '**' if x<0.05 else '*' if x<0.1 else '')        
    #print("\n",betas)
    
    titletxt="投资组合的静态年度贝塔系数"
    import datetime as dt; todaydt=dt.date.today()
    footnote="数据来源：新浪/stooq/fred，基于"+ticker_name(mktidx)+', '+str(todaydt)
    df_display_CSS(betas,titletxt=titletxt,footnote=footnote,facecolor='papayawhip', \
                   decimals=4, \
                       first_col_align='center',second_col_align='center', \
                       last_col_align='center',other_col_align='center')    
    
    betas.set_index('Year',inplace=True)
    
    #绘图：年度贝塔系数变化
    df=pd.DataFrame(betas['Beta'])
    title="投资组合的静态年度贝塔系数"+ \
            "\n成分股: "+str(ticker_name(tickerlist,'bond'))+"\n持仓权重: "+str(sharelist)
    import datetime; today = datetime.date.today()
    foot="数据来源: 新浪/stooq/fred，"+str(today)
    plot_trend(title,foot,df,power=2,axhline_value=1,axhline_label='市场风险线')
    
    return  betas  
    
if __name__=='__main__':
    yearlist=['2013','2014','2015','2016','2017','2018','2019']
    capm_beta_portfolio_yearly(['AAPL','MSFT'],[2,1],'^GSPC',yearlist)
    capm_beta_portfolio_yearly(['600028.SS','600036.SS'],[2,1],'000001.SS',yearlist)    

#==============================================================================
def capm_beta_portfolio_yearly_excel(tickerlist,sharelist,mktidx,yearlist, \
                                     excelfile,sheetname='Sheet1'):
    """
    函数功能：分年度计算投资组合的CAPM模型贝塔系数，绘图，结果保存到Excel
    输入参数：
    tickerlist: 投资组合中各个成分股的股票代码
    sharelist: 各个成分股的持股比例
    mktidx: 指数代码
    yearlist: 年度列表
    excelfile: 带目录的Excel文件名，如果目录不存在则出错
    sheetname：Excel文件中的sheet名
    输出：
    按年份绘图beta系数, 并保存到Excel文件
    无返回数据
    """
    
    #运行开始信息
    print("\n*** Analysing yearly portfolio CAPM betas, please wait ...")
    
    #生成开始结束日期
    Y4=str(int(yearlist[0])-1)
    start=Y4+'-01-01'
    end=yearlist[-1]+'-12-31' 
        
    #读取股价并准备好收益率数据
    R=prepare_capm_portfolio(tickerlist,sharelist,mktidx,start,end)
    if R is None:
        print("  #Error(capm_beta_portfolioyearly_excel): failed to prepare capm data")
        print("  Information:",tickerlist,sharelist,mktidx,start,end)              
        return      

    #用于保存beta(CAPM)和beta
    import pandas as pd
    betas=pd.DataFrame(columns=('Year','Beta','intercept','R-sqr','p-value'))
    
    #分年度OLS回归
    from scipy import stats
    for year in yearlist:
        #print(year,' ',end='')
        r=R[R['Year']==year]
        if len(r)==0: continue
        try:
            output=stats.linregress(r['Close_x'],r['Close_y'])
        except:
            print("  #Error(capm_beta_portfolio_yearly_excel): no data available for regressing beta")
            print("  Information:",year,R,r)
            return         
        (beta,alpha,r_value,p_value,std_err)=output
        
        row=pd.Series({'Year':year,'Beta':beta,'intercept':alpha, \
                       'R-sqr':r_value**2,'p-value':p_value})
        try:
            betas=betas.append(row,ignore_index=True)
        except:
            betas=betas._append(row,ignore_index=True)
        
    betas2=betas.copy() #用于保存excel   
    betas2['Year']=betas2['Year'].astype('int')
    betas2['Portfolio']=str(tickerlist)
    betas2['Share Ratio']=str(sharelist)
    betas2['Market Index']=mktidx
    
    betas.set_index('Year',inplace=True)    #用于绘图
    
    #绘图：年度贝塔系数变化
    df=pd.DataFrame(betas['Beta'])
    title="Investment Portfolio's Annual CAPM Betas"+ \
            "\nPortfolio: "+str(tickerlist)+"\nComposition: "+str(sharelist)
    foot="\nSource: Sina Finance/Yahoo Finance"
    plot_trend(title,foot,df,power=2)
    
    """
    #为折线加数据标签
    for a,b in zip(betas.index,betas['Beta']):
        plt.text(a,b+0.02,str(round(b,2)),ha='center',va='bottom',fontsize=7)
    plt.show()
    """
    
    #保存到Excel   
    import pandas as pd
    try:
        file1=pd.ExcelFile(excelfile)
    except:
        #不存在excelfile文件，直接写入
        betas2.to_excel(excelfile,sheet_name=sheetname, \
                       header=True,encoding='utf-8')
        print("***Results saved in",excelfile,"@ sheet",sheetname)
        return
    else:
        #已存在excelfile文件，先将所有已有内容读出        
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
        #print(dict[sheetlist[pos]],betas2)
        df1=dict[sheetlist[pos]][['Year','Beta','intercept','R-sqr','p-value','Portfolio','Share Ratio','Market Index']]
        df=pd.concat([df1,betas2],axis=0,ignore_index=True)        
        dict[sheetlist[pos]]=df
    
    #将原有内容写回excelfile    
    result=pd.ExcelWriter(excelfile)
    for s in sheetlist:
        df1=dict[s][['Year','Beta','intercept','R-sqr','p-value','Portfolio','Share Ratio','Market Index']]
        df1.to_excel(result,s,header=True,index=True,encoding='utf-8')
    #写入新内容
    if not dup: #sheetname未重复
        betas2.to_excel(result,sheetname,header=True,index=True,encoding='utf-8')
    try:
        result.save()
        result.close()
    except:
        print("  #Error(capm_beta_portfolio_yearly_excel): writing file permission denied")
        print("  Information:",excelfile)  
        return
    print("***Results saved in",excelfile,"@ sheet",sheetname)
    return  betas  
    
if __name__=='__main__':
    yearlist=['2013','2014','2015','2016','2017','2018','2019']
    excelfile='C:/temp/myexcel.xls'
    capm_beta_portfolio_yearly_excel(['AAPL','MSFT'],[2,1],'^GSPC',yearlist, excelfile,'p01')

#==============================================================================
def compare2_betas_yearly(ticker1,ticker2,mktidx,yearlist):
    """
    函数功能：分年度计算两只股票的CAPM模型贝塔系数，并绘图对比其风险特征的对冲性
    输入参数：
    ticker1: 股票代码
    ticker2: 股票代码
    mktidx: 指数代码
    yearlist: 年度列表，start日期要给第一个年份留出至少一年数据供回归使用
    输出数据：
    按年份绘图贝塔系数的变化
    无返回数据
    """
    #仅用于测试，完成后应注释掉
    #stkcd1='600028.SS'
    #stkcd2='600036.SS'
    #mktidx='000001.SS'
    #yearlist=['2013','2014','2015','2016','2017','2018','2019']

    
    #运行开始信息
    print("  Comparing stock CAPM betas, please wait ...")
    
    #生成开始结束日期
    Y4=str(int(yearlist[0])-1)
    start=Y4+'-01-01'
    end=yearlist[-1]+'-12-31' 
        
    #读取股价并准备好收益率数据
    R1=prepare_capm_data(ticker1,mktidx,start,end)
    if R1 is None:
        print("  #Error(compare2_betas_yearly): failed to prepare capm data")
        print("  Information:",ticker1,mktidx,start,end)              
        return      

    R2=prepare_capm_data(ticker2,mktidx,start,end)
    if R2 is None:
        print("  #Error(compare2_betas_yearly): failed to prepare capm data")
        print("  Information:",ticker2,mktidx,start,end)              
        return 

    #用于保存beta(CAPM)
    import pandas as pd
    betas1=pd.DataFrame(columns=('Year','Beta','alpha','R-sqr','p-value'))
    #分年度OLS回归
    from scipy import stats
    for year in yearlist:
        r=R1[R1['Year']==year]
        if len(r)==0: continue
        try:
            output=stats.linregress(r['Close_x'],r['Close_y'])
        except:
            print("  #Error(compare2_betas_yearly): no data for regression")
            print("  Information:",stkcd1,year,r,R1)
            continue         
        (beta,alpha,r_value,p_value,std_err)=output
        
        row=pd.Series({'Year':year,'Beta':beta,'alpha':alpha, \
                       'R-sqr':r_value**2,'p-value':p_value})
        try:
            betas1=betas1.append(row,ignore_index=True)   
        except:
            betas1=betas1._append(row,ignore_index=True)
        #print("  Calculated CAPM beta of",stkcd1,'on year',year)
        
    betas1.set_index('Year',inplace=True)

    betas2=pd.DataFrame(columns=('Year','Beta','alpha','R-sqr','p-value'))
    for year in yearlist:
        #print(year,' ',end='')
        r=R2[R2['Year']==year]
        if len(r)==0: continue
        try:
            output=stats.linregress(r['Close_x'],r['Close_y'])
        except:
            print("  #Error(compare2_betas_yearly): no data for regression")
            print("  Information:",stkcd2,year,r,R2)
            continue         
        (beta,alpha,r_value,p_value,std_err)=output        
        row=pd.Series({'Year':year,'Beta':beta,'alpha':alpha, \
                       'R-sqr':r_value**2,'p-value':p_value})
        try:
            betas2=betas2.append(row,ignore_index=True)
        except:
            betas2=betas2._append(row,ignore_index=True)
        #print("  Calculated CAPM beta of",stkcd2,'on year',year)
        
    betas2.set_index('Year',inplace=True)
    
    #绘图：年度贝塔系数变化
    plt.plot(betas1['Beta'],label=ticker_name(ticker1),c='red',marker='o',lw=1)
    plt.plot(betas2['Beta'],label=ticker_name(ticker2),c='blue',marker='D',lw=2,linestyle='--')
    
    #plt.axhline(y=1.0,color='b',linestyle=':',c='green',label='市场平均风险')  
    plt.axhline(y=1.0,color='b',linestyle=':',c='black')  
    
    plt.ylabel("贝塔系数",fontweight='bold')
    plt.xticks(rotation=45,fontweight='bold')
    trtitle="比较证券之间的贝塔系数"+"\n"+ticker_name(ticker1)+" vs "+ticker_name(ticker2)
    plt.title(trtitle,fontweight='bold')
    plt.legend(loc='best')
    
    import datetime; today = datetime.date.today()
    plt.xlabel("数据来源：新浪/stooq/fred，基于"+ticker_name(mktidx)+'，'+str(today))
    
    plt.gca().set_facecolor('whitesmoke')
    plt.show()
    
    return  betas1,betas2  
    
if __name__=='__main__':
    yearlist=['2013','2014','2015','2016','2017','2018','2019']
    compare2_betas_yearly('AMZN','WMT','^GSPC',yearlist)    
    compare2_betas_yearly('601857.SS','600036.SS','000001.SS',yearlist)

#==============================================================================
#==============================================================================
#==============================================================================