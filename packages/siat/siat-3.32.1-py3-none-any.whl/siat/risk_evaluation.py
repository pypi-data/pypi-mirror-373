# -*- coding: utf-8 -*-
"""
本模块功能：单项证券的VaR(在险价值)和ES(预期损失)计算函数包
所属工具包：证券投资分析工具SIAT 
SIAT：Security Investment Analysis Tool
创建日期：2018年10月10日
最新修订日期：2019年10月10日
作者：王德宏 (WANG Dehong, Peter)
作者单位：北京外国语大学国际商学院
作者邮件：wdehong2000@163.com
版权所有：王德宏
用途限制：仅限研究与教学使用，不可商用！商用需要额外授权。
特别声明：作者不对使用本工具进行证券投资导致的任何损益负责！
"""
#==============================================================================
#统一屏蔽一般性警告
import warnings; warnings.filterwarnings("ignore")     

from siat.common import *
from siat.translate import *
from siat.security_prices import *
from siat.security_price2 import *
#==============================================================================
import pandas as pd
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
plt.rcParams['axes.grid']=True
#plt.rcParams['grid.color']='steelblue'
#plt.rcParams['grid.linestyle']='dashed'
#plt.rcParams['grid.linewidth']=0.5
#plt.rcParams['axes.facecolor']='whitesmoke'
#==============================================================================
if __name__ == '__main__':
    ticker='BABA'
    start_date='2021-11-1'
    end_date='2021-11-10'
    
def get_stock_quotes(ticker,start_date,end_date):
    """
    输入参数：股票代码，开始日期，结束日期
    输出参数：
    股票价格序列(日期，开盘价，最高价，最低价，收盘价，调整收盘价，交易量)	
    """
    
    df=get_prices(ticker,start_date,end_date)
    
    if df is None: 
        print("  #Error(get_stock_quotes): retrieving prices failed for",ticker,start_date,end_date)
        return None
    if len(df) == 0: 
        print("  #Error(get_stock_quotes): zero record found for",ticker,start_date,end_date)
        return None
    
    return df    

if __name__ == '__main__':
    get_stock_quotes('BABA','2021-11-1','2021-11-10')
#==============================================================================
def get_end_price(stock_quotes):
    """
    输入参数：股票价格序列
    输出参数：最新股价(金额)
    """
    end_price=stock_quotes['Close'][-1]
    return end_price

if __name__ == '__main__':
    get_end_price(stock_quotes)
#==============================================================================
def get_ret_series(stock_quotes):
    """
    输入参数：股票价格序列
    输出参数：股票日收益率序列(注意不是DataFrame)
    """
    stock_quotes['ret']=stock_quotes['Close'].pct_change()
    stock_quotes=stock_quotes.dropna()
    ret_series=stock_quotes['ret']  
    return ret_series
    # ret_series是序列类型

if __name__ == '__main__':
    ret_series=get_ret_series(stock_quotes)
#==============================================================================
def VaR_normal_standard(position,ret_series,future_days=1,alpha=0.99):
    
    """
    标准正太法VaR基本算法
    输入参数：当前持有头寸金额，收益率序列(非百分比)，未来持有时间(天)，置信度
    输出参数：VaR(金额，单位与当前头寸的金额单位相同)，负数
    """
    #去掉空值
    r=ret_series[~ret_series.isnull()]
    
    import numpy as np
    from scipy import stats
    
    z=stats.norm.ppf(1-alpha)
    miu_daily=np.mean(r)
    miu_days=np.power(miu_daily+1,future_days)-1
    sigma_daily=np.std(r)    
    sigma_days=np.sqrt(future_days)*sigma_daily
    
    ratio=miu_days+z*sigma_days
    VaR_days=position*ratio

    return VaR_days

if __name__ == '__main__':
    VaR_normal_standard(10000,ret_series,future_days=1,alpha=0.99)
#==============================================================================
def stock_VaR(ticker,shares,today,future_days=1,alpha=0.99, \
              pastyears=1,printout=True,random=10000,mctype='random', \
              model="normal_standard"):
    """
    功能：持有股票的VaR，支持选择四种模型
    输入参数：股票代码，持有股数，当前日期，未来持有时间(天)，置信度，
    使用历史数据的年数，是否打印结果，模型方法
    模型方法：标准正态法normal_standard，修正正态法normal_modified，
    蒙特卡洛模拟法montecarlo，历史排序模拟法historical
    输出：VaR(负数金额，单位与股价的金额单位相同)，VaR比率
    """
    # 检查支持的模型
    modellist=['normal_standard','normal_modified','montecarlo', \
               'historical','allmodels']
    if not (model in modellist):
        print("  #Error(stock_VaR): unsupported model",model)
        print("  Supported models:",modellist)
        return None,None
    
    if model in ['normal_standard']:
        VaR,VaR_ratio=stock_VaR_normal_standard(ticker=ticker,shares=shares, \
                      today=today,future_days=future_days,alpha=alpha, \
                      pastyears=pastyears,printout=printout)
        return VaR,VaR_ratio
    
    if model in ['normal_modified']:
        VaR,VaR_ratio=stock_VaR_normal_modified(ticker=ticker,shares=shares, \
                      today=today,future_days=future_days,alpha=alpha, \
                      pastyears=pastyears,printout=printout)
        return VaR,VaR_ratio    
    
    if model in ['montecarlo']:
        VaR,VaR_ratio=stock_VaR_montecarlo(ticker=ticker,shares=shares, \
                      today=today,future_days=future_days,alpha=alpha, \
                      pastyears=pastyears,random=random,mctype=mctype, \
                      printout=printout)
        return VaR,VaR_ratio      
    
    if model in ['historical']:
        VaR,VaR_ratio=stock_VaR_historical_grouping(ticker=ticker,shares=shares, \
                      today=today,future_days=future_days,alpha=alpha, \
                      pastyears=pastyears, \
                      printout=printout)
        return VaR,VaR_ratio  
    
    if model in ['allmodels']:    
        get_VaR_allmodels(ticker=ticker,shares=shares,today=today, \
                          future_days=future_days,alpha=alpha,pastyears=pastyears)
            
    return
            
#==============================================================================
def security_VaR(ticker,shares,today,future_days=1,alpha=0.99, \
              pastyears=1,printout=True,random=10000,mctype='random', \
              model="normal_standard"):
    """
    功能：持有证券的VaR，支持选择四种模型
    输入参数：证券代码，持有股数，当前日期，未来持有时间(天)，置信度，
    使用历史数据的年数，是否打印结果，模型方法
    模型方法：标准正态法normal_standard，修正正态法normal_modified，
    蒙特卡洛模拟法montecarlo，历史排序模拟法historical
    输出：VaR(负数金额，单位与股价的金额单位相同)，VaR比率
    说明：套壳函数stock_VaR
    """     
    stock_VaR(ticker=ticker,shares=shares,today=today,future_days=future_days,alpha=alpha, \
              pastyears=pastyears,printout=printout,random=random,mctype=mctype, \
                  model=model)
        
    return
    
#==============================================================================
if __name__ == '__main__':
    ticker='BABA'
    shares=10000
    today='2021-11-18'
    future_days=1
    alpha=0.99
    pastyears=1
    printout=True

def stock_VaR_normal_standard(ticker,shares,today, \
                future_days=1,alpha=0.99,pastyears=1,printout=True):
    """
    功能：持有股票的VaR，标准正态法
    输入参数：股票代码，持有股数，当前日期，未来持有时间(天)，置信度，使用历史数据的年数
    输出：VaR(负数金额，单位与股价的金额单位相同)，VaR比率
    """
    start=get_start_date(today,pastyears)
    p=get_stock_quotes(ticker,start,today)  
    if p is None: 
        print("  #Error(stock_VaR_normal_standard): no obs retrieved.")        
        return None,None
    if len(p)==0: 
        print("  #Error(stock_VaR_normal_standard): zero obs retrieved.")        
        return None,None
    
    r=get_ret_series(p)
    p_end=get_end_price(p)
    position=shares*p_end
    VaR=VaR_normal_standard(position,r,future_days,alpha)
    if VaR is None: return None,None
    #最大为全损
    if abs(VaR) > position: VaR=-position
    
    VaR_ratio=abs(VaR/position)
    
    #from rich import print as rprint
    import pandas as pd
    disp_df=pd.DataFrame(columns=['Item','Value'])
    if printout == True:
        """
        print("\n=== 计算在险价值：标准正态模型 ===")
        print("持有股票    :",ticker_name(ticker))
        print("持有股数    :",format(shares,','))
        print("持有日期    :",today)
        print("预计持有天数:",future_days)
        print("置信度      : ",alpha*100,'%',sep='')
        print("在险价值VaR :",format(round(VaR,2),','))
        print("VaR比率     : ",round(VaR_ratio*100,2),'%',sep='')
        
        import datetime as dt; today=dt.date.today()   
        footnote="*数据来源：新浪/stooq，"+str(today)
        print(footnote)
        """
        titletxt="在险价值：标准正态模型"
        import datetime as dt; todaydt=dt.date.today()   
        footnote="数据来源：新浪/stooq，"+str(todaydt)
        """
        s=pd.Series({'Item':'持有股票','Value':ticker_name(ticker)}) 
        disp_df=disp_df._append(s,ignore_index=True)
        
        s=pd.Series({'Item':'持有股数','Value':format(shares,',')}) 
        disp_df=disp_df._append(s,ignore_index=True)
        
        s=pd.Series({'Item':'持有日期','Value':today}) 
        disp_df=disp_df._append(s,ignore_index=True)
        
        s=pd.Series({'Item':'预计持有天数','Value':future_days}) 
        disp_df=disp_df._append(s,ignore_index=True)
        
        s=pd.Series({'Item':'置信度','Value':str(alpha*100)+'%'}) 
        disp_df=disp_df._append(s,ignore_index=True)
        
        s=pd.Series({'Item':'在险价值VaR','Value':format(round(VaR,2),',')}) 
        disp_df=disp_df._append(s,ignore_index=True)
        
        s=pd.Series({'Item':'VaR比率','Value':str(round(VaR_ratio*100,2))+'%'}) 
        disp_df=disp_df._append(s,ignore_index=True)
        
        df_display_CSS(disp_df,titletxt=titletxt,footnote=footnote,facecolor='papayawhip',decimals=2, \
                           hide_columns=True,
                           first_col_align='left',second_col_align='right', \
                           last_col_align='right',other_col_align='right', \
                           titile_font_size='14px',footnote_font_size='12px')
        """
        
        data_dict={'持有股票：':ticker_name(ticker), \
                   '持有股数：':format(shares,','), \
                   '持有日期：':today, \
                   '预计持有天数：':future_days, \
                   '置信度：':str(alpha*100)+'%', \
                   '在险价值VaR金额：':format(round(VaR,2),','), \
                   '在险价值VaR比率：':str(round(VaR_ratio*100,2))+'%'}
            
        print2CSS(data_dict,titletxt=titletxt,footnote=footnote,
                  #facecolor='whitesmoke',
                  )
                      
    return VaR,VaR_ratio

if __name__ == '__main__':
    var1,ratio1=stock_VaR_normal_standard('BABA',10000,'2019-08-08',1,0.99)

#==============================================================================
def series_VaR_normal_standard(ticker,shares,datelist, \
                future_days=1,alpha=0.99,pastyears=1,printout=True):
    """
    功能：一步计算在多个日期持有一定天数股票资产的VaR
    输入参数：股票代码，持有股数，日期列表(日期型列表)，未来持有时间(天数)，置信度，使用历史数据的年数
    输出：多个日期的VaR(日期，股票代码，VaR金额，VaR比率(即单位头寸的VaR))
    # datelist是datetime类型日期的列表
    """

    import pandas as pd
    result=pd.DataFrame(columns=['date','ticker','VaR','ratio'])
    for d in datelist:
        VaR,ratio=stock_VaR_normal_standard(ticker,shares,d, \
                future_days,alpha,pastyears,printout=False)
        if (VaR is None) or (ratio is None): continue
        
        s = pd.Series({'date':d,'ticker':ticker,'VaR':VaR,'ratio':ratio})
        try:
            result=result.append(s,ignore_index=True)
        except:
            result=result._append(s,ignore_index=True)
            
    result2=result.set_index(['date'])    
    # result2是dateframe类型
    
    if printout == False: return result2
    
    #打印
    result3=result2.copy()
    result3['VaR金额']=round(result3['VaR'],2)
    result3['VaR比例%']=round(result3['ratio']*100,2)
    result3.drop(columns=['ticker','VaR','ratio'],inplace=True)
    
    text1="= "+ticker_name(ticker)+": VaR比例，持有"+str(future_days)+"天 ="
    print(text1)    
    print(result3)
    import datetime as dt; today=dt.date.today()    
    print("数据来源：新浪/stooq，"+str(today))    
    
    #绘图    
    #VaR金额绘图    
    plt.plot(result3['VaR金额'],c='r',lw=2)  
    title1=ticker_name(ticker)+": VaR金额的变化，持有"+str(future_days)+"天"
    plt.title(title1)
    plt.ylabel('VaR金额')  
    #plt.gcf().autofmt_xdate() # 优化标注（自动倾斜）
    plt.xticks(rotation=30)
    
    import datetime as dt; today=dt.date.today()   
    footnote="数据来源：新浪/stooq，"+str(today)    
    plt.xlabel(footnote)
    
    plt.gca().set_facecolor('whitesmoke')
    plt.show()    
    
    plt.plot(result3['VaR比例%'],c='r',lw=2)  
    title2=ticker_name(ticker)+": VaR比例的变化， 持有"+str(future_days)+"天"
    plt.title(title2)
    plt.ylabel('VaR比例%')  
    #plt.gcf().autofmt_xdate() # 优化标注（自动倾斜）
    plt.xticks(rotation=30)
    plt.xlabel(footnote)
    
    plt.gca().set_facecolor('whitesmoke')
    plt.show()
    
    return result2

if __name__ == '__main__':
    datelist=['2018-01-01','2018-04-01','2018-07-01','2018-10-01', \
              '2019-01-01','2019-04-01','2019-07-01']
    result=series_VaR_normal_standard('BABA',10000,datelist,1,0.99)


#==============================================================================
def compare_VaR(ticker,shares,datelist, \
                future_days=1,alpha=0.99,pastyears=1,model='normal_standard'):
    """
    功能：比较多个日期持有一定天数股票资产的VaR高低
    输入参数：股票列表，持有股数，日期列表(日期型列表)，未来持有时间(天数)，
    置信度，使用历史数据的年数，选择的模型方法
    模型方法：目前仅支持normal_standard和normal_modified
    输出：无
    显示：折线图，各个资产的VaR金额和比率对比
    """
    tickerlist=ticker
    
    modellist=['normal_standard','normal_modified']
    if not (model in modellist):
        print("  #Error(compare_VaR): unsupported model",model)
        print("  Supported models at present:",modellist)
        return 
   
    if model in ['normal_standard']:
        compare_VaR_normal_standard(tickerlist=tickerlist,shares=shares, \
                datelist=datelist,future_days=future_days,alpha=alpha, \
                pastyears=pastyears)
        return
   
    if model in ['normal_modified']:
        compare_VaR_normal_modified(tickerlist=tickerlist,shares=shares, \
                datelist=datelist,future_days=future_days,alpha=alpha, \
                pastyears=pastyears)
        return    
    
        


#==============================================================================
if __name__ == '__main__':
    tickerlist=['BABA','PDD','JD']
    shares=10000
    datelist=['2019-01-01','2019-02-01','2019-03-01','2019-04-01', \
              '2019-05-01','2019-06-01','2019-07-01']
    future_days=1
    alpha=0.99
    pastyears=1


def compare_VaR_normal_standard(tickerlist,shares,datelist, \
                future_days=1,alpha=0.99,pastyears=1):
    """
    功能：比较多个日期持有一定天数股票资产的VaR高低
    输入参数：股票列表，持有股数，日期列表(日期型列表)，未来持有时间(天数)，置信度，使用历史数据的年数
    输出：无
    显示：折线图，各个资产的VaR金额和比率对比
    """
    
    import os, sys
    class HiddenPrints:
        def __enter__(self):
            self._original_stdout = sys.stdout
            sys.stdout = open(os.devnull, 'w')
        def __exit__(self, exc_type, exc_val, exc_tb):
            sys.stdout.close()
            sys.stdout = self._original_stdout    
    
    print("  The comparison may take time, please wait ...")
    markerlist=['.','o','s','*','+','x','1','2']
    for t in tickerlist:
        pos=tickerlist.index(t)
        thismarker=markerlist[pos]  
        
        with HiddenPrints():        
            r=series_VaR_normal_standard(t,shares,datelist, \
                future_days,alpha,pastyears,printout=False)
        rr=r.copy()
        rr['VaR amount']=round(rr['VaR'],2)
        rr.drop(columns=['ticker','VaR','ratio'],inplace=True)      
        
        rr['date']=rr.index
        import pandas as pd
        rr['date']=rr['date'].apply(lambda x: pd.to_datetime(x))
        rr.set_index(['date'],inplace=True)
        
        plt.plot(rr['VaR amount'],label=ticker_name(t),lw=2,marker=thismarker)

    title1="比较VaR金额，持有"+str(future_days)+"天"
    plt.title(title1)
    plt.ylabel('VaR金额')  
    plt.xticks(rotation=30)
    plt.legend(loc='best')
    
    notes="【注】VaR计算模型：标准正态法"
    import datetime as dt; today=dt.date.today()   
    source="数据来源：新浪/stooq，"+str(today)   
    footnote=notes+'\n'+source
    plt.xlabel(footnote)    
    
    plt.gca().set_facecolor('whitesmoke')
    plt.show() 
    
    for t in tickerlist:
        pos=tickerlist.index(t)
        thismarker=markerlist[pos]   

        with HiddenPrints():                
            r=series_VaR_normal_standard(t,shares,datelist, \
                future_days,alpha,pastyears,printout=False)
        rr=r.copy()
        rr['VaR ratio %']=round(rr['ratio']*100,2)
        rr.drop(columns=['ticker','VaR','ratio'],inplace=True)  
        
        rr['date']=rr.index
        import pandas as pd
        rr['date']=rr['date'].apply(lambda x: pd.to_datetime(x))
        rr.set_index(['date'],inplace=True)

        
        plt.plot(rr['VaR ratio %'],label=ticker_name(t),lw=2,marker=thismarker)

    title2="比较VaR比例，持有"+str(future_days)+"天"
    plt.title(title2)
    plt.ylabel('VaR比例%')  
    plt.xticks(rotation=30)
    plt.legend(loc='best')
    plt.xlabel(footnote)
    
    plt.gca().set_facecolor('whitesmoke')
    plt.show() 

    return 

if __name__ == '__main__':
    tickerlist=['BABA','PDD','JD']
    datelist=['2019-01-01','2019-02-01','2019-03-01','2019-04-01', \
              '2019-05-01','2019-06-01','2019-07-01']
    compare_VaR_normal_standard(tickerlist,10000,datelist,1,0.99)

#==============================================================================
def ES_normal_standard(position,ret_series,future_days=1,alpha=0.99):
    """
    功能：计算ES，标准正态法
    输入参数：持有头寸金额，日收益率序列，未来持有日期，置信度
    输出：预期损失(金额)
    """
    import numpy as np
    from scipy import stats
    
    z=stats.norm.ppf(1-alpha)
    miu_daily=np.mean(ret_series)
    miu_days=np.power(miu_daily+1,future_days)-1
    sigma_daily=np.std(ret_series)    
    sigma_days=np.sqrt(future_days)*sigma_daily
    
    zES=-stats.norm.pdf(z)/(1-alpha)
    ratio=miu_days+zES*sigma_days
    ES_days=position*ratio
    
    #return -ES_days
    return ES_days

#==============================================================================
def stock_ES(ticker,shares,today,future_days=1,alpha=0.99, \
              pastyears=1,printout=True,random=10000,mctype='random', \
              model="normal_standard"):
    """
    功能：持有股票的ES，支持选择模型
    输入参数：股票代码，持有股数，当前日期，未来持有时间(天)，置信度，
    使用历史数据的年数，是否打印结果，模型方法
    模型方法：标准正态法normal_standard
    输出：VaR(负数金额，单位与股价的金额单位相同)，VaR比率
    """
    # 检查支持的模型
    modellist=['normal_standard']
    if not (model in modellist):
        print("  #Error(stock_VaR): unsupported model",model)
        print("  Supported models at present:",modellist)
        return None,None
    
    if model in ['normal_standard']:
        ES,ratio=stock_ES_normal_standard(ticker=ticker,shares=shares, \
                      today=today,future_days=future_days,alpha=alpha, \
                      pastyears=pastyears,printout=printout)
        return ES,ratio

#==============================================================================
def security_ES(ticker,shares,today,future_days=1,alpha=0.99, \
              pastyears=1,printout=True,random=10000,mctype='random', \
              model="normal_standard"):
    """
    功能：持有证券的预期不足ES，支持选择模型
    输入参数：证券代码，持有股数，当前日期，未来持有时间(天)，置信度，
    使用历史数据的年数，是否打印结果，模型方法
    模型方法：默认标准正态法normal_standard
    说明：套壳函数stock_ES
    """
    ES,ESratio=stock_ES(ticker=ticker,shares=shares,today=today,future_days=future_days,alpha=alpha, \
                  pastyears=pastyears,printout=printout,random=random,mctype=mctype, \
                  model=model)
        
    return

#==============================================================================
if __name__ == '__main__':
    ticker='JD'
    shares=1000
    today='2023-2-6'
    future_days=1
    alpha=0.99
    pastyears=1
    printout=True


def stock_ES_normal_standard(ticker,shares,today, \
                future_days=1,alpha=0.99,pastyears=1,printout=True):
    """
    功能：计算持有股票资产的ES，标准正态法
    输入参数：股票代码，持有股数，当前日期，未来持有日期(天数)，置信度，使用历史数据的年数
    #输出参数：预期损失(金额)负数，预期损失与头寸的比率
    """
    start=get_start_date(today,pastyears)
    p=get_stock_quotes(ticker,start,today)
    
    if p is None: 
        print("  #Error(stock_ES_normal_standard): no obs retrieved.")                
        return None,None
    if len(p)==0: 
        print("  #Error(stock_ES_normal_standard): zero obs retrieved.")                
        return None,None

    r=get_ret_series(p)
    p_end=get_end_price(p)
    position=shares*p_end
    ES=ES_normal_standard(position,r,future_days,alpha)
    #最大为全损
    if abs(ES) > position: ES=-position
    
    ratio=abs(ES/position)
    
    if printout == True:
        """
        print("\n=== 计算预期不足ES：标准正态模型 ===")
        print("持有股票    :",ticker_name(ticker))
        print("持有股数    :",format(shares,','))
        print("持有日期    :",today)
        print("预计持有天数:",future_days)
        print("置信度      : ",alpha*100,'%',sep='')
        print("ES金额     :",format(round(ES,2),','))
        print("ES比例     : ",round(ratio*100,2),'%',sep='')    
        
        import datetime as dt; today=dt.date.today()
        print("数据来源：新浪/stooq，"+str(today))
        """
        
        titletxt="预期不足：标准正态模型"
        import datetime as dt; todaydt=dt.date.today()
        footnote="数据来源：新浪/stooq，"+str(todaydt)
        
        data_dict={'持有股票：':ticker_name(ticker), \
                   '持有股数：':format(shares,','), \
                   '持有日期：':today, \
                   '预计持有天数：':future_days, \
                   '置信度：':str(alpha*100)+'%', \
                   '预期不足ES金额：':format(round(ES,2),','), \
                   '预期不足ES比例：':str(round(ratio*100,2))+'%'}
        
        print2CSS(data_dict,titletxt=titletxt,footnote=footnote)
    
    return ES,ratio


#==============================================================================
def series_ES_normal_standard(ticker,shares,datelist, \
                future_days=1,alpha=0.99,pastyears=1,printout=True):
    """
    功能：一步计算在多个日期持有一定天数股票资产的ES，标准正态法
    输入参数：股票代码，持有股数，日期列表(日期型列表)，未来持有时间(天数)，置信度，使用历史数据的年数
    输出：多个日期的ES(日期，股票代码，ES金额，ES比率(即单位头寸的ES))
    # datelist是datetime类型日期的列表
    """

    import pandas as pd
    result=pd.DataFrame(columns=['date','ticker','ES','ratio'])
    for d in datelist:
        ES,ratio=stock_ES_normal_standard(ticker,shares,d, \
                future_days,alpha,pastyears,printout=False)
        if (ES is None) or (ratio is None): continue
        
        s = pd.Series({'date':d,'ticker':ticker,'ES':ES,'ratio':ratio})
        try:
            result=result.append(s,ignore_index=True)
        except:
            result=result._append(s,ignore_index=True)
            
    result2=result.set_index(['date'])    
    # result2是dateframe类型
    
    if printout == False: return result2
    
    #打印
    result3=result2.copy()
    result3['ES金额']=round(result3['ES'],2)
    result3['ES比例%']=round(result3['ratio']*100,2)
    result3.drop(columns=['ticker','ES','ratio'],inplace=True)
    
    text1="=== "+ticker_name(ticker)+": ES比例，持有"+str(future_days)+"天 ==="
    print(text1)    
    print(result3)
    import datetime as dt; today=dt.date.today()    
    print("数据来源：新浪/stooq，"+str(today))
    
    #绘图    
    #VaR金额绘图    
    plt.plot(result3['ES金额'],c='r',lw=2)  
    title1=ticker_name(ticker)+": ES金额的变化，持有"+str(future_days)+"天"
    plt.title(title1)
    plt.ylabel('ES金额')  
    plt.xticks(rotation=30)
    
    plt.gca().set_facecolor('whitesmoke')
    plt.show()    
    
    plt.plot(result3['ES比例%'],c='r',lw=2)  
    title2=ticker_name(ticker)+": ES比例的变化，持有"+str(future_days)+"天"
    plt.title(title2)
    plt.ylabel('ES比例%')  
    plt.xticks(rotation=30)
    
    plt.gca().set_facecolor('whitesmoke')
    plt.show()
    
    return result2

if __name__ == '__main__':
    datelist=['2018-01-01','2018-04-01','2018-07-01','2018-10-01', \
              '2019-01-01','2019-04-01','2019-07-01']
    result=series_ES_normal_standard('BABA',10000,datelist,1,0.99)

#==============================================================================
def compare_ES(ticker,shares,datelist, \
                future_days=1,alpha=0.99,pastyears=1,model='normal_standard'):
    """
    功能：比较多个日期持有一定天数股票资产的ES高低
    输入参数：股票列表，持有股数，日期列表(日期型列表)，未来持有时间(天数)，
    置信度，使用历史数据的年数，选择的模型方法
    模型方法：目前仅支持normal_standard
    输出：无
    显示：折线图，各个资产的ES金额和比率对比
    """
    tickerlist=ticker
    
    modellist=['normal_standard']
    if not (model in modellist):
        print("  #Error(compare_ES): unsupported model",model)
        print("  Supported models at present:",modellist)
        return 
   
    if model in ['normal_standard']:
        compare_ES_normal_standard(tickerlist=tickerlist,shares=shares, \
                datelist=datelist,future_days=future_days,alpha=alpha, \
                pastyears=pastyears)
        return
    
#==============================================================================

import contextlib
import io


def compare_ES_normal_standard(tickerlist,shares,datelist, \
                future_days=1,alpha=0.99,pastyears=1):
    """
    功能：比较多个日期持有一定天数股票资产的ES高低，标准正态法
    输入参数：股票列表，持有股数，日期列表(日期型列表)，未来持有时间(天数)，置信度，使用历史数据的年数
    输出：无
    显示：折线图，各个资产的ES金额和比率对比
    """

    import os, sys
    class HiddenPrints:
        def __enter__(self):
            self._original_stdout = sys.stdout
            sys.stdout = open(os.devnull, 'w')
        def __exit__(self, exc_type, exc_val, exc_tb):
            sys.stdout.close()
            sys.stdout = self._original_stdout
    
    buf = io.StringIO()
    
    print("  The comparison may take time, please wait ...")
    markerlist=['.','o','s','*','+','x','1','2']
    for t in tickerlist:
        pos=tickerlist.index(t)
        thismarker=markerlist[pos]   
        
        with HiddenPrints():             
            r=series_ES_normal_standard(t,shares,datelist, \
                future_days,alpha,pastyears,printout=False)
        rr=r.copy()
        rr['ES amount']=round(rr['ES'],2)
        rr.drop(columns=['ticker','ES','ratio'],inplace=True)   
        
        #plt.plot(rr['ES amount'],label=ticker_name(t),lw=2,marker=thismarker)
        x = pd.to_datetime(rr.index)
        y = pd.to_numeric(rr['ES amount'], errors='coerce')

        plt.plot(x, y, label=ticker_name(t), lw=2, marker=thismarker)


    title1="比较ES金额，持有"+str(future_days)+"天"
    plt.title(title1)
    plt.ylabel('ES金额')  
    plt.xticks(rotation=30)
    plt.legend(loc='best')

    notes="【注】ES计算模型：标准正态法"    
    import datetime as dt; today=dt.date.today() 
    source="数据来源：新浪/stooq，"+str(today)    
    footnote=notes+'\n'+source
    plt.xlabel(footnote)    
    plt.show() 

    for t in tickerlist:
        pos=tickerlist.index(t)
        thismarker=markerlist[pos] 
        
        with HiddenPrints():             
            r=series_ES_normal_standard(t,shares,datelist, \
                future_days,alpha,pastyears,printout=False)
        rr=r.copy()
        rr['ES ratio %']=round(rr['ratio']*100,2)
        rr.drop(columns=['ticker','ES','ratio'],inplace=True)      
        
        x = pd.to_datetime(rr.index)
        y = pd.to_numeric(rr['ES ratio %'], errors='coerce')

        plt.plot(x,y,label=ticker_name(t),lw=2,marker=thismarker)

    title2="比较ES比例，持有"+str(future_days)+"天"
    plt.title(title2)
    plt.ylabel('ES比例%')  
    plt.xticks(rotation=30)
    plt.legend(loc='best')
    plt.xlabel(footnote)
    plt.show() 

    return 

if __name__ == '__main__':
    tickerlist=['BABA','PDD','JD']
    datelist=['2019-01-01','2019-02-01','2019-03-01','2019-04-01', \
              '2019-05-01','2019-06-01','2019-07-01']
    shares=10000
    future_days=1
    alpha=0.99
    pastyears=1
    
    compare_ES_normal_standard(tickerlist,shares,datelist,1,0.99)


#==============================================================================
def normfunc(x,mu,sigma):
    #计算正态分布的概率密度，带有均值和标准差
    import numpy as np
    pdf = np.exp(-((x - mu)**2)/(2*sigma**2)) / (sigma * np.sqrt(2*np.pi))
    return pdf

#==============================================================================
def plot_rets_histogram(ticker,start,end,num_bins=20):
    """
    功能：绘制收益率分布的直方图，并于相应的正态分布图对照
    输入：股票代码，开始/结束时间
    显示：收益率分布的直方图(实线)，相应的正态分布图(虚线)
    x轴为收益率(非百分比)，y轴为频度(Frequency)
    """
    #抓取股价并计算收益率
    quotes=get_stock_quotes(ticker,start,end)
    if (quotes is None) or (len(quotes)==0):
        print("#Error(plot_rets_histogram): Fetching data failed")
        print("Information:",ticker,start,end)
        return    
    rets=get_ret_series(quotes)

    #计算收益率的均值和标准差
    mu=rets.mean()
    sigma=rets.std()
    
    #绘制股票收益率直方图
    #plt.figure(figsize=(8,4))
    plt.figure(figsize=(12.8,6.4))
    n,bins,patches=plt.hist(rets,num_bins,facecolor='blue',alpha=0.5,label=ticker_name(ticker))
    
    #生成与直方图柱子对应的正态分布概率密度
    y=normfunc(bins,mu,sigma)
    #绘制正态分布曲线
    plt.plot(bins,y,'r--',label='正态分布',lw=2)
    plt.ylabel('Frequency')
    plt.xlabel('Stock return')
    titletxt="正态性检验："+ticker_name(ticker)+"收益率, "+start+"至"+end
    plt.title(titletxt)
    plt.legend(loc='best')
    
    import datetime as dt; today=dt.date.today() 
    footnote="数据来源：新浪/stooq，"+str(today)
    plt.xlabel(footnote)    
    plt.show()    
    
    return

if __name__ == '__main__':
    plot_rets_histogram('JD','2019-1-1','2019-6-30')

#==============================================================================
def plot_rets_curve(ticker,start='MRY',end='today'):
    """
    功能：绘制收益率分布的曲线，并于相应的正态分布图对照
    输入：股票代码，开始/结束时间
    显示：收益率分布的直方图(实线)，相应的正态分布图(虚线)
    x轴为收益率(非百分比)，y轴为频度(Frequency)
    """
    start,end=start_end_preprocess(start,end)
    
    #抓取股价并计算收益率
    quotes=get_stock_quotes(ticker,start,end)
    if (quotes is None) or (len(quotes)==0):
        print("#Error(plot_rets_curve): Fetching data failed")
        print("Information:",ticker,start,end)
        return
    rets=get_ret_series(quotes)

    #计算收益率的均值和标准差
    mu=rets.mean()
    sigma=rets.std()

    #生成符合正态分布的随机数，符合股票收益率的均值和标准差
    import numpy as np
    x=mu+sigma*np.random.randn(1000000)    
        
    #plt.figure(figsize=(12.8,6.4))
    import seaborn as sns
    #绘制曲线：股票收益率
    sns.kdeplot(data=rets,shade=True,color='blue',legend=True,label=ticker_name(ticker),lw=2) 
    #绘制曲线：对应的正态分布
    sns.kdeplot(data=x,shade=True,color='r',legend=True,label='正态分布',ls='--')
    #设置标题、图例、坐标轴标签
    plt.ylabel('',fontsize=ylabel_txt_size)
    #plt.xlabel('收益率')
    plt.legend(loc='best',fontsize=legend_txt_size)
    titletxt="正态性检验: "+ticker_name(ticker)+"，收益率, "+start+"至"+end
    plt.title(titletxt,fontsize=title_txt_size)
    
    import datetime as dt; today=dt.date.today() 
    footnote="数据来源：新浪/stooq，"+str(today)
    plt.xlabel(footnote,fontsize=xlabel_txt_size)
    plt.show()

    return
    

if __name__ == '__main__':
    plot_rets_curve('JD','2019-1-1','2019-6-30')


#===========================================================================
def stock_ret_Normality_SW(ticker,start='MRY',end='today',siglevel=0.05):
    """
    功能：测试一个日收益率序列是否符合正态分布，原假设：符合正态分布
    输入参数：股票代码，开始日期，结束日期
    输出：日收益率序列正态性检验的p-value
    start_date,end_date均为datetime类型
    【Shapiro-Wilk正态性检验】原假设：服从正态分布
    """
    start_date,end_date=start_end_preprocess(start,end)
    
    from scipy import stats
    
    quotes=get_stock_quotes(ticker,start_date,end_date)
    if quotes is None: return None
    if len(quotes) == 0: return None
    
    ret=get_ret_series(quotes)
    (W,p_value)=stats.shapiro(ret)
    
    """
    print("\n= Shapiro-Wilk正态性检验: 股票收益率 =")
    print("股票  ：",ticker_name(ticker)) 
    print("期间  ：",start_date,"至",end_date)
    print("原假设： 符合正态分布")
    print("W值   ：",round(W,4))
    print("p值   ：",round(p_value,4))
    if p_value >= siglevel:
        print("结果  ： 接受原假设, 符合正态分布")
    else:
        print("结果  ： 拒绝原假设, 不符合正态分布")
    import datetime as dt; today=dt.date.today()
    print("*数据来源：新浪/stooq，"+str(today))
    """
    
    titletxt="Shapiro-Wilk检验: 收益率"
    data_dict1={'股票：':ticker_name(ticker), \
                '期间：':start_date+"至"+end_date, \
                '原假设：':'符合正态分布', \
                'W值：':round(W,4), \
                'p值：':round(p_value,4)}
    
    if p_value >= siglevel:
        result="接受原假设, 符合正态分布"
    else:
        result="拒绝原假设, 不符合正态分布"
    data_dict2={'结果：':result}
    data_dict={**data_dict1,**data_dict2}

    import datetime as dt; todaydt=dt.date.today()
    footnote="数据来源：新浪/stooq，"+str(todaydt)
    
    print2CSS(data_dict,titletxt=titletxt,footnote=footnote)
    
    return p_value
    
#==============================================================================
def VaR_normal_modified(position,ret_series,future_days=1,alpha=0.99):
    """
    功能：VaR基本算法，修正正态法
    #输入参数：持有头寸金额，日收益率序列，未来持有日期，置信度
    #输出参数：VaR(金额)
    """
    #去掉空值
    r=ret_series[~ret_series.isnull()]
    
    from scipy import stats
    import numpy as np

    z=np.abs(stats.norm.ppf(1-alpha))
    S=stats.skew(r)
    K=stats.kurtosis(r)
    
    t1=1/6*(np.power(z,2)-1)*S
    t2=1/24*(np.power(z,3)-3*z)*K
    t3=1/36*(2*np.power(z,3)-5*z)*np.power(S,2)
    t=z+t1+t2-t3
    
    miu_daily=np.mean(r)
    miu_days=np.power(miu_daily+1,future_days)-1
    sigma_daily=np.std(r)    
    sigma_days=np.sqrt(future_days)*sigma_daily
    
    ratio=miu_days+t*sigma_days
    VaR_days=position*ratio
    
    return -abs(VaR_days)

#==============================================================================
def stock_VaR_normal_modified(ticker,shares,today, \
                future_days=1,alpha=0.99,pastyears=1,printout=True):
    """
    功能：计算持有一定量股票若干天的VaR，修正正态法
    输入参数：股票代码，持有股数，当前日期，未来持有天数，置信度，使用历史数据的年数
    注：当前日期可以为过去的任意一天，历史年数为使用几年的历史数据来分析
    输出：VaR(金额，负数)，VaR比率
    注释：VaR比率，即每单位持有金额的在险价值
    """
    start=get_start_date(today,pastyears)
    p=get_stock_quotes(ticker,start,today)  
    if (p is None) or (len(p)==0): 
        print("  #Error(stock_VaR_normal_modified): no observation retrieved.")                        
        return None,None
    
    r=get_ret_series(p)
    p_end=get_end_price(p)
    position=shares*p_end
    VaR=VaR_normal_modified(position,r,future_days,alpha)
    #最大为全损
    if abs(VaR) > position: VaR=-position
    
    VaR_ratio=abs(VaR/position)
    
    if printout == True:
        """
        print("\n=== 在险价值VaR： 修正正态模型 ===")
        print("持有股票    :",ticker_name(ticker))
        print("持有股数    :",format(shares,','))
        print("持有日期    :",today)
        print("预计持有天数:",future_days)
        print("置信度      : ",alpha*100,'%',sep='')
        print("VaR金额     :",format(round(VaR,2),','))
        print("VaR比例     : ",round(VaR_ratio*100,2),'%',sep='')    
        
        import datetime as dt; today=dt.date.today()
        print("*数据来源：新浪/stooq，"+str(today))
        """
        titletxt="在险价值：修正正态模型"
        import datetime as dt; todaydt=dt.date.today()
        footnote="数据来源：新浪/stooq，"+str(todaydt)
        
        data_dict={'持有股票：':ticker_name(ticker), \
                   '持有股数：':format(shares,','), \
                   '持有日期：':today, \
                   '预计持有天数：':future_days, \
                   '置信度：':str(alpha*100)+'%', \
                   '在险价值VaR金额：':format(round(VaR,2),','), \
                   '在险价值VaR比例：':str(round(VaR_ratio*100,2))+'%'}
        
        print2CSS(data_dict,titletxt=titletxt,footnote=footnote)
        
    return VaR,VaR_ratio    
    
#==============================================================================
def series_VaR_normal_modified(ticker,shares,datelist, \
                future_days=1,alpha=0.99,pastyears=1,printout=True):
    """
    功能：一步计算多个日期的VaR，修正正态分布法
    输入参数：股票代码，持有股数，日期列表，未来持有天数，置信度，使用历史数据的年数
    注释：当前日期可以为过去的任意一天，历史年数为使用几年的历史数据来分析
    输出：VaR信息表(日期，股票代码，VaR金额，VaR比率)
    """
    # datelist是datetime类型日期的列表
    import pandas as pd
    result=pd.DataFrame(columns=['date','ticker','VaR','ratio'])
    for d in datelist:
        VaR,ratio=stock_VaR_normal_modified(ticker,shares,d, \
                future_days,alpha,pastyears,printout=False)
        s = pd.Series({'date':d,'ticker':ticker,'VaR':VaR,'ratio':ratio})
        try:
            result=result.append(s,ignore_index=True)
        except:
            result=result._append(s,ignore_index=True)
            
    result2=result.set_index(['date'])    
    # result2是dateframe类型
    
    if printout == False: return result2
    
    #打印
    result3=result2.copy()
    result3['VaR金额']=round(result3['VaR'],2)
    result3['VaR比例%']=round(result3['ratio']*100,2)
    result3.drop(columns=['ticker','VaR','ratio'],inplace=True)
    
    text1="= "+ticker_name(ticker)+": VaR比例，持有"+str(future_days)+"天 ="
    print(text1)    
    print(result3)
    import datetime as dt; today=dt.date.today()
    print("数据来源：新浪/stooq，"+str(today))
    
    #绘图    
    #VaR金额绘图    
    plt.plot(result3['VaR金额'],c='r',lw=2)  
    title1=ticker_name(ticker)+": VaR金额的变化，持有"+str(future_days)+"天"
    plt.title(title1)
    plt.ylabel('VaR金额')  
    plt.xticks(rotation=30)
    
    footnote="数据来源：新浪/stooq，"+str(today)
    plt.xlabel(footnote)
    plt.show()    
    
    plt.plot(result3['VaR比例%'],c='r',lw=2)  
    title2=ticker_name(ticker)+": VaR比例的变化，持有"+str(future_days)+"天"
    plt.title(title2)
    plt.ylabel('VaR比例%')  
    plt.xticks(rotation=30)
    plt.xlabel(footnote)
    plt.show()

    return result2


#==============================================================================
def compare_VaR_normal_modified(tickerlist,shares,datelist, \
                future_days=1,alpha=0.99,pastyears=1):
    """
    功能：比较多个日期持有一定天数股票资产的VaR高低，修正正态法
    输入参数：股票列表，持有股数，日期列表(日期型列表)，未来持有时间(天数)，置信度，使用历史数据的年数
    输出：无
    显示：折线图，各个资产的VaR金额和比率对比
    """

    import os, sys
    class HiddenPrints:
        def __enter__(self):
            self._original_stdout = sys.stdout
            sys.stdout = open(os.devnull, 'w')
        def __exit__(self, exc_type, exc_val, exc_tb):
            sys.stdout.close()
            sys.stdout = self._original_stdout
    
    print("  The comparison may take time, please wait ...")
    markerlist=['.','o','s','*','+','x','1','2']
    for t in tickerlist:
        pos=tickerlist.index(t)
        thismarker=markerlist[pos]   

        with HiddenPrints():             
            r=series_VaR_normal_modified(t,shares,datelist, \
                future_days,alpha,pastyears,printout=False)
        rr=r.copy()
        rr['VaR amount']=round(rr['VaR'],2)
        rr.drop(columns=['ticker','VaR','ratio'],inplace=True)        
        plt.plot(rr['VaR amount'],label=ticker_name(t),lw=2,marker=thismarker)

    title1="比较VaR金额，持有"+str(future_days)+"天"
    plt.title(title1)
    plt.ylabel('VaR金额')  
    plt.xticks(rotation=30)
    plt.legend(loc='best')

    notes="【注】VaR计算模型：修正正态法"    
    import datetime as dt; today=dt.date.today() 
    source="数据来源：新浪/stooq，"+str(today)    
    footnote=notes+'\n'+source
    plt.xlabel(footnote)   
    plt.show() 

    for t in tickerlist:
        pos=tickerlist.index(t)
        thismarker=markerlist[pos]  
        
        with HiddenPrints():            
            r=series_VaR_normal_modified(t,shares,datelist, \
                future_days,alpha,pastyears,printout=False)
        rr=r.copy()
        rr['VaR ratio %']=round(rr['ratio']*100,2)
        rr.drop(columns=['ticker','VaR','ratio'],inplace=True)        
        plt.plot(rr['VaR ratio %'],label=ticker_name(t),lw=2,marker=thismarker)

    title2="比较VaR比例，持有"+str(future_days)+"天"
    plt.title(title2)
    plt.ylabel('VaR比例%')  
    plt.xticks(rotation=45)
    plt.legend(loc='best')
    plt.xlabel(footnote)
    plt.show() 

    return 

if __name__ == '__main__':
    tickerlist=['BABA','PDD','JD']
    datelist=['2019-01-01','2019-02-01','2019-03-01','2019-04-01', \
              '2019-05-01','2019-06-01','2019-07-01']
    compare_VaR_normal_standard(tickerlist,10000,datelist,1,0.99)


#==============================================================================
def VaR_historical_1d(position,ret_series,alpha=0.99):
    """
    功能：计算VaR基本算法，历史模拟法，持有1天
    输入参数：持有头寸金额，历史日收益率序列，置信度
    输出：持有一天的VaR(金额)
    """
    #去掉空值
    r=ret_series[~ret_series.isnull()]
    
    import numpy as np
    n=len(r)
    t=int(n*(1-alpha))
    SR=np.sort(r)
    if t>=1:
        A=SR[t-1]   #SR的第一个元素的序号是0
    else:
        A=SR[0]
    VaR_1d=position*A
    
    return -abs(VaR_1d)


#==============================================================================
def stock_VaR_historical_1d(ticker,shares,today,alpha=0.99, \
                            pastyears=1,printout=True):
    """
    功能：计算持有股票的VaR，历史模拟法，持有1天
    输入参数：股票代码，持有股数，当前日期，置信度，使用历史数据的年数
    输出：持有一天的VaR(金额和比率)
    """
    start=get_start_date(today,pastyears)
    p=get_stock_quotes(ticker,start,today)  
    if (p is None) or (len(p)==0): 
        print("#Error(stock_VaR_historical_1d): no obs retrieved.")        
        return None,None
    
    r=get_ret_series(p)
    p_end=get_end_price(p)
    position=shares*p_end
    VaR_1d=VaR_historical_1d(position,r,alpha)
    #最高为全损
    if abs(VaR_1d)>position: VaR_1d=-position
    VaR_ratio=abs(VaR_1d/position)

    if printout == True:
        """
        print("\n=== 计算在险价值VaR：历史模拟方法 ===")
        print("持有股票    :",ticker_name(ticker))
        print("持有股数    :",format(shares,','))
        print("持有日期    :",today)
        future_days=1
        print("预计持有日期:",future_days)
        print("置信度     : ",alpha*100,'%',sep='')
        print("VaR金额    :",format(round(VaR_1d,2),','))
        print("VaR比例    : ",round(VaR_ratio*100,2),'%',sep='')    
        
        import datetime as dt; today=dt.date.today()
        print("*数据来源：新浪/stooq，"+str(today))
        """
        titletxt="在险价值：历史模拟方法"
        import datetime as dt; todaydt=dt.date.today()
        footnote="数据来源：新浪/stooq，"+str(todaydt)
        
        future_days=1
        data_dict={'持有股票：':ticker_name(ticker), \
                   '持有股数：':format(shares,','), \
                   '持有日期：':today, \
                   '预计持有天数：':future_days, \
                   '置信度：':str(alpha*100)+'%', \
                   '在险价值VaR金额：':format(round(VaR_1d,2),','), \
                   '在险价值VaR比例：':str(round(VaR_ratio*100,2))+'%'}
        
        print2CSS(data_dict,titletxt=titletxt,footnote=footnote)
        
    return VaR_1d,VaR_ratio 

if __name__ == '__main__':
    ticker='BABA'
    shares=1000
    today='2020-7-1'
    alpha=0.99
    pastyears=1
    printout=True
    VaR,Ratio=stock_VaR_historical_1d(ticker,shares,today)
#==============================================================================
def VaR_historical_grouping(position,ret_series,future_days=1,alpha=0.99):
    """
    功能：计算VaR基本算法，历史模拟法，持有多天(基本分组法，无组内收益率波动调整)
    输入参数：当前头寸金额，历史日收益率序列，未来持有天数，置信度
    注意：分组法需要更长时间的历史数据，不然准确度不高！
    输出：持有多天的VaR(金额)
    """
    #去掉空值
    r=ret_series[~ret_series.isnull()]
    
    import pandas as pd
    #将收益率序列转变为df
    r1=pd.DataFrame(r)
    
    #定义组内累计收益率计算方法
    cumret=lambda x:(x+1.0).prod()-1.0
    #使用滚动窗口分组，计算各组收益率gret
    r1['gret']=r1.rolling(future_days).apply(cumret)
    #将各组收益率转换为组收益率序列
    r2=pd.Series(r1['gret'])
    
    #利用单日历史模拟法计算VaR
    VaR_days=VaR_historical_1d(position,r2,alpha)

    return -abs(VaR_days) 

if __name__ == '__main__':
    ticker='BABA'
    start='2020-6-1'
    today='2020-7-1'
    p=get_stock_quotes(ticker,start,today)
    ret_series=get_ret_series(p)    
    future_days=2

    shares=1000
    alpha=0.99
    pastyears=1
    printout=True   
    position=1

    VaR=VaR_historical_grouping(position,ret_series,future_days)
    

#==============================================================================
def VaR_historical(position,ret_series,future_days=1,alpha=0.99):
    """
    功能：同名函数，为了后面函数名称合成方便
    """
    VaR=VaR_historical_grouping(position,ret_series,future_days,alpha)
    return VaR

#==============================================================================
def stock_VaR_historical_grouping(ticker,shares,today, \
                future_days=1,alpha=0.99,pastyears=1,printout=True):
    """
    功能：计算持有股票的VaR，历史模拟法，持有多天(基本分组法，无组内收益率波动调整)
    输入参数：股票代码，持有股数，当前日期，未来持有天数，置信度，使用历史数据的年数
    注意：分组法需要更长时间的历史数据，不然准确度不高！
    建议：pastyears的数值大于等于future_days的数值
    输出：基本分组法，持有多天的VaR(金额和比率)
    """
    start=get_start_date(today,pastyears)
    p=get_stock_quotes(ticker,start,today)
    if (p is None) or (len(p)==0): 
        print("#Error(stock_VaR_historical_grouping): no obs retrieved.")
        return None,None
    p_end=get_end_price(p); position=shares*p_end
    
    #产生历史收益率序列
    r=get_ret_series(p)
    #分组计算
    VaR_days=VaR_historical_grouping(position,r,future_days,alpha)
    #最大为全损
    if abs(VaR_days) > position: VaR_days=-position
    
    VaR_ratio=abs(VaR_days/position)
    
    if future_days == 1:
        modeltxt="历史排序模拟法"
    else:
        modeltxt="分组历史模拟法"
    
    if printout == True:
        """
        print("\n=== 在险价值VaR："+modeltxt+" ===")
        print("持有股票    :",ticker_name(ticker))
        print("持有股数    :",format(shares,','))
        print("持有日期    :",today)
        print("预计持有天数:",future_days)
        print("置信度      :",alpha*100,'%',sep='')
        print("VaR金额     :",format(round(VaR_days,2),','))
        print("VaR比例     :",round(VaR_ratio*100,2),'%',sep='')      
        
        import datetime as dt; today=dt.date.today()
        print("*数据来源：新浪/stooq，"+str(today))
        """
        
        titletxt="在险价值："+modeltxt
        import datetime as dt; todaydt=dt.date.today()
        footnote="数据来源：新浪/stooq，"+str(todaydt)
        
        data_dict={'持有股票：':ticker_name(ticker), \
                   '持有股数：':format(shares,','), \
                   '持有日期：':today, \
                   '预计持有天数：':future_days, \
                   '置信度：':str(alpha*100)+'%', \
                   '在险价值VaR金额：':format(round(VaR_days,2),','), \
                   '在险价值VaR比例：':str(round(VaR_ratio*100,2))+'%'}
        
        print2CSS(data_dict,titletxt=titletxt,footnote=footnote)
        
        
    return -abs(VaR_days),VaR_ratio 
  
#==============================================================================
def VaR_montecarlo(position,ret_series, \
                future_days=1,alpha=0.99,random=10000,mctype='random'):
    """
    功能：计算VaR基本算法，蒙特卡洛模拟法，持有多日
    输入参数：当前头寸金额，历史日收益率序列，未来持有天数，置信度，重复模拟次数
    注：重复模拟次数越多，准确率就越高，但耗时也越多
    输出：持有多天的VaR(金额)
    """
    #去掉空值
    r=ret_series[~ret_series.isnull()]
    
    import pandas as pd
    #蒙特卡洛模拟类型：随机数or超采样
    if mctype=='random':    #随机数产生新的序列
        import numpy as np
        #取得历史日收益率的均值和标准差
        miu=np.mean(r)
        sigma=np.std(r)
        #生成随机数序列
        np.random.seed(12345)
        #按照历史日收益率的均值和标准差重复模拟一定次数，生成新的日收益率序列
        RR=pd.Series(np.random.normal(miu,sigma,random))
    else:   #超采样产生新的序列
        #将收益率序列转变为df
        r1=pd.DataFrame(r)
        r2=r1.sample(n=random,replace=True)
        r2.sort_index(inplace=True)
        RR=pd.Series(r2.iloc[:,0])
        
    #基于新的日收益率序列，使用标准正态法计算VaR
    VaR_days=VaR_historical_grouping(position,RR,future_days,alpha)
    
    return -abs(VaR_days)


#==============================================================================
def stock_VaR_montecarlo(ticker,shares,today,future_days=1,alpha=0.99, \
                         pastyears=1,random=10000,printout=True,mctype='random'):
    """
    功能：计算持有股票的VaR，蒙特卡洛模拟法，持有多日
    输入参数：股票代码，持有股数，当前日期，未来持有天数，置信度，使用历史数据的年数，
    重复模拟次数
    输出：持有股票多天的VaR(金额和比率)
    """
    start=get_start_date(today,pastyears)
    p=get_stock_quotes(ticker,start,today)  
    if (p is None) or (len(p)==0): 
        print("#Error(stock_VaR_montecarlo): no obs retrieved.")               
        return None,None
    r=get_ret_series(p)
    p_end=get_end_price(p)
    position=shares*p_end
    
    VaR_days=VaR_montecarlo(position,r,future_days,alpha,random,mctype=mctype)
    ratio=abs(VaR_days/position)
    #最大为全损
    if abs(VaR_days) > position: VaR_days=-position
    
    if printout == True:
        """
        print("\n=== 在险价值VaR：蒙特卡洛模拟法 ===")
        print("持有日期    :",today)
        print("持有股票    :",ticker_name(ticker))
        print("持有股数    :",format(shares,','))
        print("持有头寸    :",format(round(position,2),','))
        print("预计持有天数:",future_days)
        print("置信度      : ",alpha*100,'%',sep='')
        print("序列生成方法:",mctype)
        print("VaR金额     :",format(round(VaR_days,2),','))
        #四舍五不入
        print("VaR比例     : ",(int(ratio*10000))/100,'%',sep='')      
        
        import datetime as dt; today=dt.date.today()
        print("*数据来源：新浪/stooq，"+str(today))
        """
        titletxt="在险价值：蒙特卡洛模拟法"
        import datetime as dt; todaydt=dt.date.today()
        footnote="数据来源：新浪/stooq，"+str(todaydt)
        
        data_dict={'持有股票：':ticker_name(ticker), \
                   '持有股数：':format(shares,','), \
                   '持有头寸：':format(round(position,2),','), \
                   '持有日期：':today, \
                   '预计持有天数：':future_days, \
                   '序列生成方法：':mctype, \
                   '置信度：':str(alpha*100)+'%', \
                   '在险价值VaR金额：':format(round(VaR_days,2),','), \
                   '在险价值VaR比例：':str(round(ratio*100,2))+'%'}
        
        print2CSS(data_dict,titletxt=titletxt,footnote=footnote)
        
    return VaR_days,ratio


#==============================================================================
def calc_VaR_tlcp(ticker,today,alpha=0.99, \
                  pastyears=1,model="normal_standard",printout=True):
    """
    功能：计算一只股票的VaR全损临界点，即VaR达到持有全部头寸的最小天数
    输入：股票代码，持有日期，置信度，使用历史数据的年数，
    使用的模型，是否打印结果
    输出：股票的VaR全损临界点天数，与使用的模型有关
    显示：无
    """
    print("\n...Calculatiing tlcp of",ticker,"\b, please wait...")
    
    #检查model类型
    modellist=['normal_standard','normal_modified','montecarlo']
    model=model.lower()
    if model not in modellist:
        print("#Error(calc_VaR_tlcp): Unsupported type of model")
        print("Information:",model)
        print("Supported models:",modellist)
        return    
    
    #抓取股价，计算历史收益率序列和当前头寸
    start=get_start_date(today,pastyears)
    p=get_stock_quotes(ticker,start,today)  
    if (p is None) or (len(p)==0): 
        print("#Error(calc_VaR_tlcp): no obs retrieved.")
        return None
    r=get_ret_series(p)
    p_end=get_end_price(p)
    shares=1
    position=shares*p_end
    
    #第1轮搜索，步长1000天
    func="VaR_"+model
    import numpy as np
    stop1=0; max1=9000
    for d in np.arange(0,max1+1000,1000):
        VaR=eval(func)(position,r,d,alpha)
        ratio=abs(VaR)/position*100
        if ratio >= 100.0:
            stop1=d
            break
    if stop1==0:
        if printout == True:
            """
            print("\n=== VaR的全损临界点TLCP ===")
            print("持有股票  :",ticker_name(ticker))
            print("持有日期  :",today)
            print("使用的模型:",model)
            print("置信度    : ",alpha*100,'%',sep='')
            print("TLCP天数  : >",format(max1,','))
            
            print("*注：实际发生全损的概率极小")
            import datetime as dt; today=dt.date.today()
            print("数据来源：新浪/stooq，"+str(today))
            """
            titletxt="VaR全损临界点"
            import datetime as dt; todaydt=dt.date.today()
            ft0="*注：实际发生全损的概率极小"
            footnote=ft0+'\n'+"数据来源：新浪/stooq，"+str(todaydt)
            
            data_dict={'持有股票：':ticker_name(ticker), \
                       '持有日期：':today, \
                       '使用的模型：':model, \
                       '置信度：':str(alpha*100)+'%', \
                       '全损临界点TLCP天数 >':format(max1,',')}
            
            print2CSS(data_dict,titletxt=titletxt,footnote=footnote)
            
        return max1        
    
    #第2轮搜索，步长100天  
    stop2=100
    for d in np.arange(stop1-1000,stop1+100,100):
        VaR=eval(func)(position,r,d,alpha)
        ratio=abs(VaR)/position*100
        if ratio >= 100.0:
            stop2=d
            break        
    
    #第3轮搜索，步长10天    
    stop3=10
    for d in np.arange(stop2-100,stop2+10,10):
        VaR=eval(func)(position,r,d,alpha)
        ratio=abs(VaR)/position*100
        if ratio >= 100.0:
            stop3=d
            break 
    
    #第4轮搜索，步长1天  
    stop4=1
    for d in np.arange(stop3-10,stop3+1,1):
        VaR=eval(func)(position,r,d,alpha)
        ratio=abs(VaR)/position*100
        if ratio >= 100.0:
            stop4=d
            break 
    
    if printout == True:
        """
        print("\n=== VaR的全损临界点TLCP ===")
        print("持有股票  :",ticker_name(ticker))
        print("持有日期  :",today)
        print("使用的模型:",model)
        print("置信度    : ",alpha*100,'%',sep='')
        print("TLCP天数  : >",format(stop4,','))
        """
        
        titletxt="VaR全损临界点"
        import datetime as dt; todaydt=dt.date.today()
        ft0="*注：实际发生全损的概率极小"
        footnote=ft0+'\n'+"数据来源：新浪/stooq，"+str(todaydt)
        
        data_dict={'持有股票：':ticker_name(ticker), \
                   '持有日期：':today, \
                   '使用的模型：':model, \
                   '置信度：':str(alpha*100)+'%', \
                   '全损临界点TLCP天数 >':format(stop4,',')}
        
        print2CSS(data_dict,titletxt=titletxt,footnote=footnote)
        
        
    return stop4

if __name__ == "__main__":
    ticker='AAPL'
    today='2020-7-20'
    alpha=0.99
    pastyears=1
    model="montecarlo"
    printout=True
    tlcp=calc_VaR_tlcp('MSFT','2019-8-8')

#==============================================================================
def series_VaR_tlcp(tickerlist,today,alpha=0.99,pastyears=1,model="montecarlo"):
    """
    功能：计算股票列表中各个股票的VaR全损临界点(天数)
    输出：各个股票的VaR全损临界点(天数)列表
    显示：柱状图，从小到大排序
    """

    #仅测试用
    #tickerlist=['BABA','JD','VIPS','PDD']
    #today='2019-8-8'
    #alpha=0.99
    #pastyears=1
    #model="montecarlo"
    print("\n*** It may need very long time to calculate, please wait ...")

    import pandas as pd
    tlcpdf=pd.DataFrame(columns=['Ticker','Holding date','Alpha','Model','TLCP'])
    for t in tickerlist:
        tlcp=calc_VaR_tlcp(t,today,alpha,pastyears,model,printout=False)
        row=pd.Series({'Ticker':t,'Holding date':today,'Alpha':alpha, \
                       'Model':model,'TLCP':tlcp})
        try:
            tlcpdf=tlcpdf.append(row,ignore_index=True)
        except:
            tlcpdf=tlcpdf._append(row,ignore_index=True)
            
        #print("TLCP for stock ",t,": ",tlcp," days",sep='')
    #tlcpdf=tlcpdf.set_index('Ticker')    
    tlcpdf=tlcpdf.sort_values(axis=0,ascending=True,by = 'TLCP')
    #tlcpdf.reset_index(drop=True)    
    tlcpdf.set_index('Ticker',drop=True,inplace=True)
    """
    #ax=plt.figure(figsize=(12.8,6.4))
    tlcpdf.plot.barh(x='Ticker',y='TLCP',color='r',grid=True)
    plt.ylabel('股票')
    titlel1="VaR全损临界点(TLCP)"
    titlel2="\n"+str(today)+", 使用模型"+model+", 置信度"+str(alpha*100)+"%"
    titletxt=titlel1+titlel2
    plt.title(titletxt)
    
    import datetime as dt; today=dt.date.today() 
    footnote='TLCP天数-->'+"\n数据来源：新浪/stooq，"+str(today)
    plt.xlabel(footnote)
    plt.show() 
    """
    titlel1="VaR全损临界点(TLCP)"
    titlel2="\n"+str(today)+", 使用模型"+model+", 置信度"+str(alpha*100)+"%"
    titletxt=titlel1+titlel2    
    import datetime as dt; today=dt.date.today() 
    footnote='TLCP天数-->'+"\n数据来源：新浪/stooq，"+str(today)    
    import siat.grafix as g
    g.plot_barh(tlcpdf,'TLCP',titletxt,footnote)
    
    """
    print("===== VaR全损临界点(TLCP, 天数) =====")
    print("持有日期  :",today)
    print("使用的模型:",model)
    print("置信度    :",alpha*100,'%',sep='') 
    print(tlcpdf)
    print("数据来源：新浪/stooq，"+str(today))
    """
    
    titletxt="VaR全损临界点(TLCP, 天数)"
    import datetime as dt; todaydt=dt.date.today()
    footnote="数据来源：新浪/stooq，"+str(todaydt)
    
    data_dict={'持有日期：':today, \
               '使用的计算模型：':model, \
               '置信度：':str(alpha*100)+'%'}
    
    print2CSS(data_dict,titletxt='',footnote='')
    df_display_CSS(tlcpdf,titletxt=titletxt,footnote=footnote,facecolor='papayawhip',decimals=2, \
                       hide_columns=False,
                       first_col_align='left',second_col_align='right', \
                       last_col_align='right',other_col_align='right', \
                       titile_font_size='14px',heading_font_size='14px', \
                       data_font_size='14px',footnote_font_size='12px')
    
    return tlcpdf


#==============================================================================
def plot_VaR_days_changes(ticker,shares,today,dayslist,alpha=0.99, \
                        pastyears=1,model="montecarlo", \
                        printout=True, markertype='.'):
    """
    功能：计算持有股票的VaR，持有多个日期
    输入参数：股票代码，持有股数，当前日期，未来持有天数列表，置信度，
    使用历史数据的年数，算法，默认为蒙特卡洛模拟法
    输出：持有股票多个日期的VaR(金额和比率)，数据框格式
    """
    
    #仅测试用
    #ticker='AAPL'
    #shares=1000
    #today='2019-8-8'
    #dayslist=[1,5,10,15,30,90,180]
    #alpha=0.99
    #pastyears=1
    #model="montecarlo"
    #printout=True    
    
    print("\n... Calculating VaR may take great time, please wait...")
    #抓取股价，计算历史收益率序列和当前头寸
    start=get_start_date(today,pastyears)
    p=get_stock_quotes(ticker,start,today)  
    if (p is None) or (len(p)==0): return None
    r=get_ret_series(p)
    p_end=get_end_price(p)
    position=shares*p_end

    #计算各个持有天数的VaR
    import pandas as pd
    vardf=pd.DataFrame(columns=['ticker','holding date','holding days','VaR','ratio%'])
    for d in dayslist:
        func="VaR_"+model
        #print(ticker,shares,today,d,alpha)
        VaR=round((eval(func)(position,r,d,alpha)),0)
        ratio=round((abs(VaR)/position*100),2)
        if ratio >= 100.0: ratio=100.0
        s = pd.Series({'ticker':ticker,'holding date':today,'holding day(s)':d, \
                       'VaR':VaR,'ratio%':ratio})
        try:
            vardf=vardf.append(s,ignore_index=True)
        except:
            vardf=vardf._append(s,ignore_index=True)
            
    vardf=vardf.set_index(['holding day(s)']) 

    #绘图
    if printout == True:
        #plt.figure(figsize=(8,4))
        plt.figure(figsize=(12.8,6.4))
        #绘制曲线：ratio
        plt.plot(vardf['ratio%'],color='red',lw=2,label=ticker_name(ticker),marker=markertype)
        #设置标题、图例、坐标轴标签
        plt.ylabel('VaR比例%')
        plt.legend(loc='best')
        titlel1="持有股票期间与VaR比例的变化趋势"
        titlel2="\n"+ticker_name(ticker)+", "+today+", 使用模型"+model
        titletxt=titlel1+titlel2
        plt.title(titletxt)
        
        import datetime as dt; today=dt.date.today() 
        footnote='持有天数-->'+"\n数据来源：新浪/stooq，"+str(today)
        plt.xlabel(footnote)
        plt.show()

    return vardf  

#==============================================================================
def compare_VaR_days_changes(tickerlist,shares,today,dayslist,alpha=0.99, \
                          pastyears=1,model="montecarlo"):
    """
    功能：计算多个股票的持有VaR，分别持有多个日期
    输入参数：股票代码列表，持有股数，当前日期，未来持有天数列表，置信度，
    使用历史数据的年数，算法，默认为蒙特卡洛模拟法
    输出：比较多支股票多个日期的VaR(金额和比率)，数据框格式
    显示：绘图比较
    """
    
    #仅测试用
    #tickerlist=['BABA','JD','PDD']
    #shares=1000
    #today='2019-8-8'
    #dayslist=[1,5,10,15,30,60,90,120,150,180,210,240,270,300,330,365]
    #alpha=0.99
    #pastyears=1
    #model="montecarlo"

    #检查model类型
    modellist=['normal_standard','normal_modified','historical','montecarlo']
    model=model.lower()
    if model not in modellist:
        print("#Error(compare_VaR_days_changes): Unsupported type of model")
        print("Information:",model)
        print("Supported models:",modellist)
        return
    
    #依次绘图tickerlist中的各个股票
    #plt.figure(figsize=(8,4))
    plt.figure(figsize=(12.8,6.4))
    
    markerlist=['.','o','s','*','+','x','1','2']
    for t in tickerlist:
        pos=tickerlist.index(t)
        thismarker=markerlist[pos]
        vardf=plot_VaR_days_changes(t,shares,today,dayslist,alpha, \
                pastyears,model,printout=False,markertype=thismarker)
        if vardf is None: 
            print("#Error(compare_VaR_days_changes): No available data")
            print("Information:",t,today,pastyears,model)
            continue        
        
        plt.plot(vardf['ratio%'],lw=2,label=ticker_name(t),marker=thismarker)
    
    #设置标题、图例、坐标轴标签
    plt.ylabel('VaR比例%')
    plt.legend(loc='best')
    titlel1="持有股票期间与VaR比例的变化趋势"
    titlel2="\n股票: "+str(tickerlist)+", "+today+", 使用模型"+model
    titlel3="\n注: 水平线表示VaR全损"
    titletxt=titlel1+titlel2+titlel3
    plt.title(titletxt)
    
    import datetime as dt; today=dt.date.today() 
    footnote='持有天数-->'+"\n数据来源：新浪/stooq，"+str(today)
    plt.xlabel(footnote)
    plt.show()

    return

if __name__ =="__main__":
    dayslist=[1,5,15,30,60,90,180,365]
    compare_VaR_days_changes('AAPL','JD',1000,'2019-8-8',dayslist)

#==============================================================================
def get_VaR_allmodels(ticker,shares,today, \
                      future_days=1,alpha=0.99,pastyears=1):
    """
    功能：一次性计算各种模型方法的VaR
    输入参数：股票代码，持有股数，当前日期，未来持有天数，置信度，使用历史数据的年数
    股票代码：美股代码格式
    当前日期：datetime类型
    输出参数：各种模型的VaR金额和比率
    模型：标准正态法，修正正态法，历史模拟基本分组法，蒙特卡洛模拟法
    """
    #计算最低年数以保证历史模拟法至少拥有30个分组来确保结果的有效性
    py=int(future_days*30/252)+1
    if py > pastyears:
        print("Warning: Historical samples too few, historical simulation may not work properly")
    
    #抓取开始日期
    start=get_start_date(today,pastyears)
    #抓取股价序列
    quotes=get_stock_quotes(ticker,start,today)
    if (quotes is None) or (len(quotes)==0): 
        print("#Error(get_VaR_allmodels): no obs retrieved.")
        return None,None
    #计算当前头寸
    position=shares*get_end_price(quotes)
    #计算收益率序列
    rets=get_ret_series(quotes)
    
    #模型1：标准正太法。加0.5取整相当于四舍五入
    VaR1=int(VaR_normal_standard(position,rets,future_days,alpha)+0.5)
    ratio1=abs(round(VaR1/position,4))
    
    #模型2：修正正太法
    VaR2=int(VaR_normal_modified(position,rets,future_days,alpha)+0.5)
    ratio2=abs(round(VaR2/position,4))
    
    #模型3：历史模拟法-分组法
    #VaR3=int(VaR_historical_cumulative(position,rets,future_days,alpha)+0.5)
    VaR3=int(VaR_historical_grouping(position,rets,future_days,alpha)+0.5)
    ratio3=abs(round(VaR3/position,4))
                
    #模型4：蒙特卡洛模拟法(标准正态分布)
    VaR4=int(VaR_montecarlo(position,rets,future_days,alpha)+0.5)
    ratio4=abs(round(VaR4/position,4))
    
    """
    print("\n==== 不同模型下VaR的计算结果 ====")
    print("持有日期    :",today)
    print("持有股票    :",ticker_name(ticker))
    print("持有股数    :",format(shares,','))
    print("持有头寸    :",format(round(position,2),','))   
    print("预计持有天数:",future_days)
    print("置信度      : ",alpha*100,'%',sep='')
    
    print("\n*** 各模型计算的VaR金额:")
    print("标准正态模型  :",format(VaR1,','))
    print("修正正态模型  :",format(VaR2,','))
    print("历史模拟法    :",format(VaR3,','))
    print("蒙特卡洛模拟法:",format(VaR4,','))
    
    print("\n*** 各模型计算的VaR比例:")
    print("标准正态模型  :",round(ratio1*100,2),'%',sep='')
    print("修正正态模型  :",round(ratio2*100,2),'%',sep='')
    print("历史模拟法    :",round(ratio3*100,2),'%',sep='')
    print("蒙特卡洛模拟法:",round(ratio4*100,2),'%',sep='')   

    import datetime as dt; today=dt.date.today()
    print("\n数据来源：新浪/stooq，"+str(today))   
    """
    
    import datetime as dt; todaydt=dt.date.today()
    footnote="数据来源：新浪/stooq，"+str(todaydt)
    
    titletxt="持有资产的状况"
    data_dict={'持有日期：':today, \
               "持有股票：":ticker_name(ticker), \
               "持有股数：":format(shares,','), \
               "持有股数：":format(shares,','), \
               "持有头寸：":format(round(position,2),','), \
               "预计持有天数：":future_days, \
               '置信度：':str(alpha*100)+'%'}
    print2CSS(data_dict,titletxt=titletxt,footnote='')
    
    titletxt="各模型的VaR金额"
    data_dict={"标准正态模型：":format(VaR1,','), \
               "修正正态模型：":format(VaR2,','), \
               "历史模拟模型：":format(VaR3,','), \
               "蒙特卡洛模拟：":format(VaR4,',')}
    print2CSS(data_dict,titletxt=titletxt,footnote='')    
    
    titletxt="各模型的VaR比例"
    data_dict={"标准正态模型：":str(round(ratio1*100,2))+'%', \
               "修正正态模型：":str(round(ratio2*100,2))+'%', \
               "历史模拟模型：":str(round(ratio3*100,2))+'%', \
               "蒙特卡洛模拟：":str(round(ratio4*100,2))+'%'}
    print2CSS(data_dict,titletxt=titletxt,footnote=footnote)   
    
    VaRlist=[VaR1,VaR2,VaR3,VaR4]
    ratiolist=[ratio1,ratio2,ratio3,ratio4]
    
    return VaRlist,ratiolist 

#==============================================================================
def get_ret_portfolio(tickerlist,shareslist,today,pastyears=1):
    """
    功能：计算投资组合的历史收益率序列和当前头寸金额
    输入参数：投资组合的股票列表，投资组合的持有股数列表，当前日期，使用历史数据的年数
    输出参数：投资组合的历史日收益率序列，当前持有头寸金额
    注意：
    #tickerlist为字符串列表类型，内容为投资组合内各个股票的代码
    #shareslist为整数列表类型，内容为投资组合内各个股票的持股数量，不是金额
    #tickerlist和shareslist中的元素个数必须一一对等
    """
    import pandas as pd
    start=get_start_date(today,pastyears)
    prices=pd.DataFrame()
    for t in range(len(tickerlist)):
        ticker=tickerlist[t]
        q=get_stock_quotes(ticker,start,today)
        q['date']=q.index.strftime('%Y'+'%m'+'%d')
        q['ticker']=ticker
        q['price']=q['Close']    
        q['shares']=shareslist[t]
        q['value']=q['price']*q['shares']
        try:
            prices=prices.append(q)
        except:
            prices=prices._append(q)

    prices2=prices.sort_values('date')
    groupKey='date'; groupWay=prices2.groupby(groupKey)
    prices3=groupWay['value'].sum()  
    position=prices3[-1]
    ret=prices3.pct_change()
    ret=ret.dropna()
    return ret,position

#==============================================================================     
def get_ret_portfolio2(tickerlist,shareslist,today,pastyears=1):
    """
    功能：计算投资组合的历史收益率序列、当前头寸金额和各个成分股的历史日收益率序列 
    输入参数：投资组合的股票列表，投资组合的持有股数列表，当前日期，使用历史数据的年数
    输出：投资组合的历史日收益率序列，当前持有头寸金额，各个成分股的历史日收益率序列
    注意：
    #tickerlist为字符串列表类型，内容为投资组合内各个股票的代码
    #shareslist为整数列表类型，内容为投资组合内各个股票的持股数量，不是金额
    #tickerlist和shareslist中的元素个数必须一一对等
    """
    import pandas as pd
    start=get_start_date(today,pastyears)
    prices=pd.DataFrame()
    for t in range(len(tickerlist)):
        ticker=tickerlist[t]
        q=get_stock_quotes(ticker,start,today)
        q['date']=q.index.strftime('%Y'+'%m'+'%d')
        q['ticker']=ticker
        q['price']=q['Close']    
        q['shares']=shareslist[t]
        q['value']=q['price']*q['shares']
        q['ret']=q['price'].pct_change()
        try:
            prices=prices.append(q)
        except:
            prices=prices._append(q)
    
    #portfolio收益率
    prices2=prices.sort_values('date')
    groupKey='date'; groupWay=prices2.groupby(groupKey)
    prices3=groupWay['value'].sum()  
    pret=prices3.pct_change()
    pret=pret.dropna()
    
    #portfolio当前持有头寸
    position=prices3[-1]
    
    #成分股收益率
    sret=prices[['date','ticker','price','shares','value','ret']]
    sret=sret.dropna()
    
    return pret,position,sret

#==============================================================================     
def get_portfolio_info(tickerlist,today,pastyears=1):
    """
    功能：返回一组股票的历史价格和历史日收益率
    输入参数：股票列表，当前日期，使用历史数据的年数
    输出：成分股收益率数据表
    """
    import pandas as pd
    start=get_start_date(today,pastyears)
    prices=pd.DataFrame()

    for t in range(len(tickerlist)):
        ticker=tickerlist[t]
        q=get_stock_quotes(ticker,start,today)
        q['date']=q.index.strftime('%Y'+'%m'+'%d')
        q['ticker']=ticker
        q['price']=q['Close']    
        q['shares']=0
        q['value']=0
        q['ret']=q['price'].pct_change()
        try:
            prices=prices.append(q)
        except:
            prices=prices._append(q)
   
    #成分股收益率
    tickers_info=prices[['date','ticker','price','shares','value','ret']]
    return tickers_info

#==============================================================================     
def get_portfolio_rets(tickerlist,shareslist,tickers_info,today,pastyears=1):
    """
    功能：计算投资组合的历史日收益率序列和当前头寸金额，不重新抓取股价
    输入参数：股票列表，持有股数列表，股票信息数据框，当前日期，使用历史数据的年数
    输出：投资组合的历史日收益率序列和当前头寸
    注意：
    #tickerlist为字符串列表类型，内容为投资组合内各个股票的代码
    #shareslist为整数列表类型，内容为投资组合内各个股票的持股数量，不是金额
    #tickerlist和shareslist中的元素个数必须一一对等
    """
    import pandas as pd
    start=get_start_date(today,pastyears)
    startdate=start.strftime('%Y'+'%m'+'%d')
    enddate  =today.strftime('%Y'+'%m'+'%d')
    ti=pd.DataFrame()
    for index, row in tickers_info.iterrows():
        if (row['date'] >= startdate) and (row['date'] <= enddate):
            ticker=row['ticker']
            p=tickerlist.index(ticker)
            shares=shareslist[p]
            row['shares']=shares  
            row['value']=row['price']*shares
            try:
                ti=ti.append(row,ignore_index=True)
            except:
                ti=ti._append(row,ignore_index=True)
          
    ti1=ti.sort_values('date')
    groupKey='date'; groupWay=ti1.groupby(groupKey)
    ti2=groupWay['value'].sum()  
    position=ti2[-1]
    pret=ti2.pct_change()
    pret=pret.dropna()
    
    return pret,position

#==============================================================================  
def get_ret_cumulative(ret_series):
    """
    功能：计算累计收益率
    输入参数：收益率序列
    输出：累积收益率    
    """
    c=1
    for r in ret_series:
        c=c*(1+r)
    retcum=c-1    
    return retcum

#==============================================================================     
def get_portfolio_ret_risk(tickerlist,shareslist,tickers_info, \
                           today,future_days=1,alpha=0.99,pastyears=1):
    """
    功能：一次性计算投资组合的所有收益率和风险信息，避免重复抓取网络股价
    输入参数：投资组合的股票列表，投资组合的持有股数列表，投资组合的成分股信息，当前日期，
    未来持有天数，置信度，使用历史数据的年数
    输出：投资组合的累积收益率、VaR金额与比率、ES金额与比率；各个成分股的累积收益率、
    VaR金额与比率、ES金额与比率  
    """
    #合成投资组合历史信息
    Pret,Pposition=get_portfolio_rets(tickerlist,shareslist, \
                                tickers_info,today,pastyears)

    #投资组合累积收益率：例13.82%
    Pretcum=round(get_ret_cumulative(Pret),4)
    #投资组合VaR金额和比率：例-$8851，0.0304
    PVaR=int(VaR_normal_standard(Pposition,Pret,future_days,alpha)+0.5)
    PVaRratio=round(abs(PVaR/Pposition),4)
    #投资组合ES金额和比率：例-$10166，0.035
    PES=int(ES_normal_standard(Pposition,Pret,future_days,alpha)+0.5)
    PESratio=round(abs(PES/Pposition),4)

    #成分股累积回报率列表：[-0.0113,0.3278]
    retlist=[]
    for t in tickerlist:
        r=tickers_info[tickers_info['ticker']==t]['ret']
        r=r.dropna()
        retcum=round(get_ret_cumulative(r),4)
        retlist=retlist+[retcum]

    #VaR金额和比率列表：例[-$4650,-$6691],[0.0329,0.0447]
    VaRlist=[]
    VaRratiolist=[]
    for t in range(len(tickerlist)):
        ticker=tickerlist[t]
        r=tickers_info[tickers_info['ticker']==ticker]['ret']
        r=r.dropna()
    
        shares=shareslist[t]
        price=tickers_info[tickers_info['ticker']==ticker]['price'][-1]
        position=shares*price
            
        VaR=int(VaR_normal_standard(position,r,future_days,alpha)+0.5)
        ratio=round(abs(VaR/position),4)
        VaRlist=VaRlist+[VaR]
        VaRratiolist=VaRratiolist+[ratio]

    #ES金额和比率列表：例[-$5329,-$7695],[0.0377,0.0515]
    ESlist=[]
    ESratiolist=[]
    for t in range(len(tickerlist)):
        ticker=tickerlist[t]
        r=tickers_info[tickers_info['ticker']==ticker]['ret']
        r=r.dropna()
            
        shares=shareslist[t]
        price=tickers_info[tickers_info['ticker']==ticker]['price'][-1]
        position=shares*price
            
        ES=int(ES_normal_standard(position,r,future_days,alpha)+0.5)
        ratio=round(abs(ES/position),4)
        ESlist=ESlist+[ES]
        ESratiolist=ESratiolist+[ratio]    
    
    return Pretcum,PVaR,PVaRratio,PES,PESratio, \
            retlist,VaRlist,VaRratiolist,ESlist,ESratiolist


#==============================================================================     
def get_portfolio_ret_risk2(tickerlist,shareslist,tickers_info, \
                           today,future_days=1,alpha=0.99,pastyears=1):
    """
    功能：一次性计算投资组合的所有收益率和风险信息，仅返回比率
    输入参数：投资组合的股票列表，投资组合的持有股数列表，投资组合的成分股信息，当前日期，
    未来持有天数，置信度，使用历史数据的年数
    输出参数：投资组合的累积收益率、VaR比率、ES比率；各个成分股的累积收益率、VaR比率、ES比率  
    """
    Pretcum,PVaR,PVaRratio,PES,PESratio, \
            retlist,VaRlist,VaRratiolist,ESlist,ESratiolist= \
            get_portfolio_ret_risk(tickerlist,shareslist,tickers_info, \
                           today,future_days,alpha,pastyears)

    return Pretcum,PVaRratio,PESratio,retlist,VaRratiolist,ESratiolist 


#==============================================================================     
def get_portfolio_ret_risk3(tickerlist,shareslist,tickers_info, \
                           today,future_days=1,alpha=0.99,pastyears=1):
    """
    功能：一次性计算投资组合的所有收益率和风险信息，仅返回投资组合的比率
    输入参数：投资组合的股票列表，投资组合的持有股数列表，投资组合的成分股信息，当前日期，
    未来持有天数，置信度，使用历史数据的年数
    输出：投资组合的累积收益率、VaR比率、ES比率
    """
    Pretcum,PVaR,PVaRratio,PES,PESratio, \
            retlist,VaRlist,VaRratiolist,ESlist,ESratiolist= \
            get_portfolio_ret_risk(tickerlist,shareslist,tickers_info, \
                           today,future_days,alpha,pastyears)

    return Pretcum,PVaRratio,PESratio   


#==============================================================================





