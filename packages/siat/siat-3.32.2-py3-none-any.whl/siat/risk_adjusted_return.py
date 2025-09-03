# -*- coding: utf-8 -*-
"""
本模块功能：投资组合的风险调整收益率教学插件(算法II)
所属工具包：证券投资分析工具SIAT 
SIAT：Security Investment Analysis Tool
创建日期：2018年10月16日
最新修订日期：2025年6月20日
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
#==============================================================================
from siat.common import *
from siat.translate import *
from siat.security_prices import *
from siat.security_price2 import *
from siat.fama_french import *
from siat.grafix import *

import pandas as pd
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
#==============================================================================
#==============================================================================
def calc_treynor_ratio(regdf):
    """
    功能：计算一项特雷诺指数
    输入：数据框，至少含有Ret-Rf和Mkt-Rf两项
    输出：特雷诺指数，Ret-Rf均值
    """
    
    #计算风险溢价Ret-RF均值
    ret_rf_mean=regdf['Ret-RF'].mean()
    
    #使用CAPM回归计算投资组合的贝塔系数，这里得到的alpha就是Jensen's alpha
    from scipy import stats
    output=stats.linregress(regdf['Mkt-RF'],regdf['Ret-RF'])
    (beta,alpha,r_value,p_value,std_err)=output 
    
    #计算特雷诺指数
    tr=ret_rf_mean/beta
    
    #ret_mean=regdf['Ret%'].mean()
    rp_mean=ret_rf_mean
    return tr,rp_mean,beta

#==============================================================================
def calc_alpha_ratio(regdf):
    """
    功能：计算一项詹森阿尔法指数
    输入：数据框，至少含有Ret-Rf和Mkt-Rf两项
    输出：詹森阿尔法指数，Ret-Rf均值
    """
    #计算风险溢价Ret-RF均值
    ret_rf_mean=regdf['Ret-RF'].mean()
    #使用CAPM回归计算投资组合的贝塔系数，这里得到的alpha就是Jensen's alpha
    from scipy import stats
    output=stats.linregress(regdf['Mkt-RF'],regdf['Ret-RF'])
    (beta,alpha,r_value,p_value,std_err)=output 
    
    rp_mean=ret_rf_mean
    return alpha,rp_mean,beta

#==============================================================================
def calc_sharpe_ratio(regdf):
    """
    功能：计算一项夏普指数
    输入：数据框，至少含有Ret-Rf和Mkt-Rf两项
    输出：夏普指数，Ret-Rf均值
    """
    #计算风险溢价Ret-RF均值和标准差
    ret_rf_mean=regdf['Ret-RF'].mean()
    ret_rf_std=regdf['Ret-RF'].std()
    
    #计算夏普指数
    sr=ret_rf_mean/ret_rf_std
    
    rp_mean=ret_rf_mean
    beta=False
    return sr,rp_mean,beta

if __name__=='__main__':
    rfd=rf_daily_china('2021-10-1','2021-11-28',rate_period='1Y',rate_type='shibor')
    rfd=rf_daily_china('2021-11-1','2021-11-28',rate_period='3M',rate_type='shibor')
    
    prices=get_prices('837344.BJ','2021-11-1','2021-11-28')
    prices['ret_daily']=prices['Close'].pct_change()
    rp=pd.merge(prices,rfd,how='left',left_index=True,right_index=True)
    rp['r-rf']=rp['ret_daily']-rp['rf_daily']
    rp.dropna(inplace=True)
    sharpe1=rp['r-rf'].mean()/rp['r-rf'].std()
    sharpe2=rp['ret_daily'].mean()/rp['ret_daily'].std()
#==============================================================================
def calc_sortino_ratio(regdf):
    """
    功能：计算一项索替诺指数
    输入：数据框，至少含有Ret-Rf和Mkt-Rf两项
    输出：索替诺指数，Ret-Rf均值
    """
    
    #计算风险溢价Ret-RF均值和下偏标准差LPSD
    ret_rf_mean=regdf['Ret-RF'].mean()
    reg2=regdf[regdf['Ret-RF'] < 0]
    ret_rf_lpsd=reg2['Ret-RF'].std()
    
    #计算索梯诺指数
    sr=ret_rf_mean/ret_rf_lpsd
    
    rp_mean=ret_rf_mean
    beta=False
    return sr,rp_mean,beta

#==============================================================================
def print_rar_ratio(regdf,portfolio,rp_mean,beta,ratio_name,ratio):
    """
    功能：打印风险调整后的收益率
    输入：数据框，投资组合构成，收益溢价均值，贝塔系数，指数名称，指数
    输出：打印
    
    注意：若贝塔系数为False则不打印
    """

    #从字典中提取信息
    scope,mktidx,stocklist,portionlist,ticker_type=decompose_portfolio(portfolio)
    stocklist1,_=cvt_yftickerlist(stocklist)
    
    date_start=str(regdf.index[0].year)+'-'+str(regdf.index[0].month)+ \
            '-'+str(regdf.index[0].day)
    date_end=str(regdf.index[-1].year)+'-'+str(regdf.index[-1].month)+ \
            '-'+str(regdf.index[-1].day)            
    print("\n======== 风险调整收益率 ========")
    print("证券资产:",portfolio_name(portfolio))
    #print("市场指数:",ectranslate(scope),'\b,',ticker_name(mktidx))
    print("市场指数:",ticker_name(mktidx))
    #print("成分股  :",ticker_name(stocklist))
    #print("持仓权重:",portionlist)
    print("样本期间:",date_start,"至",date_end)
    """
    print("日均收益率:",round(ret_mean,4),'\b%')
    annual_ret=(1+ret_mean/100)**252-1
    print("年化收益率:",round(annual_ret,4))
    """
    if not isinstance(beta,bool):
        print("贝塔系数:",round(beta,4))
        
    print("风险溢价均值%:",round(rp_mean,4))

    #print(ratio_name.capitalize(),"\b比率:",round(ratio,4),'\b%')
    print(ratio_name.capitalize(),"\b比率%:",round(ratio,4))
    """
    print("***投资组合构成:")
    print_tickerlist_sharelist(stocklist,portionlist,2)
    """
    
    import datetime as dt; todaydt=dt.date.today()
    print("数据来源：新浪/stooq, "+str(todaydt))    
    
    return 
#==============================================================================
if __name__=='__main__':
    portfolio={'Market':('US','^GSPC'),'AAPL':0.5,'MSFT':0.3,'IBM':0.2}
    start='2024-6-1'
    end='2025-5-30'
    RF=0.04
    printout=True
    
    rate_period='ON'

def treynor_ratio_portfolio(portfolio,start,end,RF=True,printout=True):
    """
    功能：按天计算一个投资组合的特雷诺指数
    投资组合的结构：{'Market':('US','^GSPC'),'AAPL':0.5,'MSFT':0.3,'IBM':0.2}
    输入：投资组合，开始日期，结束日期
    输出：特雷诺指数
    """

    #第1步：各种准备和检查工作
    #设定错误信息的函数名
    func_name='treynor_ratio_portfolio'
    #设定需要计算的指数名称
    ratio_name="treynor"
    result,startdate,enddate=check_period(start,end)
    if not result:
        message="  #Error("+func_name+"): "+"invalid start or end date:"
        print(message,start,end)
        return None,None    
    
    #从字典中提取信息
    scope,mktidx,stocklist,portionlist,ticker_type=decompose_portfolio(portfolio)

    #第2步：获得无风险收益率/市场收益率序列
    #获得期间的日无风险收益率(抓取的RF为百分比) 
    if isinstance(RF,bool):
        print("  Searching for risk-free interest rate ...")
        if scope=='China':
            rf_df=get_mkt_rf_daily_china(mktidx,start,end,rate_period='1Y',rate_type='shibor',RF=RF)
        else:
            rf_df=get_rf(start,end,scope=scope,freq='daily')  
            if rf_df is None:
                message="  #Error("+func_name+"): "+"no data available for rf in"
                print(message,scope,start,end)
                return None,None 
        RF=rf_df['RF'].mean()
    
    #第3步：计算投资组合的日收益率序列
    #抓取日投资组合价格：内含Mkt-RF和RF
    sp=get_portfolio_prices(portfolio,start,end,RF=RF)
    #计算日收益率，表示为百分比
    """
    import pandas as pd
    ret_pf=pd.DataFrame(sp['Close'].pct_change())*100.0
    ret_pf=ret_pf.dropna()
    """
    ret_pf=sp
    
    #第4步：合并投资组合日收益率与无风险利率/市场收益率序列
    """
    if isinstance(RF,bool):
        #合并rf_df与ret_pf
        reg=pd.merge(ret_pf,rf_df,how='inner',left_index=True,right_index=True)
    else:
        reg=ret_pf
        reg['RF']=RF/365 #日度无风险收益率%
    reg['Ret-RF']=reg['Close']-reg['RF']
    """
    reg=ret_pf
    reg=reg.dropna()
    if len(reg) == 0:
        message="  #Error("+func_name+"): "+"empty ret-rf data for regression"
        print(message)
        return None,None 
    
    #第5步：计算风险调整后的收益率
    ##########风险调整后的收益率，计算开始##########
    tr,rp_mean,beta=calc_treynor_ratio(reg)
    ##########风险调整后的收益率，计算结束##########
    
    #第6步：打印结果
    if printout == True:
        print_rar_ratio(reg,portfolio,rp_mean,beta,ratio_name,tr)
    
    return tr,rp_mean


if __name__=='__main__':
    portfolio1={'Market':('US','^GSPC'),'AAPL':0.5,'MSFT':0.3,'IBM':0.2}
    tr1,ret1=treynor_ratio_portfolio(portfolio1,'2019-01-01','2019-01-31')


#==============================================================================
if __name__=='__main__':
    portfolio={'Market':('US','^GSPC'),'EDU':0.6,'TAL':0.4}
    start='2025-1-01'
    end  ='2025-5-30'
    RF=0.04; printout=True
    indicator='sharpe'
    indicator='alpha'


def rar_ratio_portfolio(portfolio,start='MRY',end='today', \
                        indicator='sharpe', \
                            RF=0,printout=True):
    """
    功能：按天计算一个投资组合的风险调整后的收益率指数
    投资组合的结构：{'Market':('US','^GSPC'),'AAPL':0.5,'MSFT':0.3,'IBM':0.2}
    输入：投资组合，开始日期，结束日期，rar种类
    输出：风险调整后的收益率指数
    """
    ratio_name=indicator
    
    #第1步：各种准备和检查工作
    #设定错误信息的函数名
    func_name='rar_ratio_portfolio'
    
    ratio_name=ratio_name.lower()
    ratio_list=['treynor','sharpe','sortino','alpha']
    if ratio_name not in ratio_list:
        message="  #Error("+func_name+"): "+"unsupported rar ratio type"
        print(message)
        return None,None       
    
    start,end=start_end_preprocess(start,end)
    result,startdate,enddate=check_period(start,end)
    if not result:
        message="  #Error("+func_name+"): "+"invalid start or end date"
        print(message,start,end)
        return None,None    
    
    print(f"  Calculating {ratio_name} ratio ...")
    #从字典中提取信息
    scope,mktidx,stocklist,portionlist,ticker_type=decompose_portfolio(portfolio)

    #第2步：获得无风险收益率/市场收益率序列
    #获得期间的日无风险收益率(抓取的RF为百分比) 
    rf_value_flag=True #RF以数值形式给出
    if isinstance(RF,bool):
        rf_value_flag=False
        if RF:
            print("  Searching for risk-free interest rate ...")
            if scope=='China':
                rf_df=get_mkt_rf_daily_china(mktidx,start,end,rate_period='1Y',rate_type='shibor',RF=RF)
            else:
                rf_df=get_rf(start,end,scope=scope,freq='daily')  
                if rf_df is None:
                    message="  #Error("+func_name+"): "+"no data available for rf in"
                    print(message,scope,start,end)
                    return None,None 
            RF=rf_df['RF'].mean()
        else:
            RF=0
            rf_value_flag=True
    
    #第3步：计算投资组合的日收益率序列
    import os,sys
    class HiddenPrints:
        def __enter__(self):
            self._original_stdout = sys.stdout
            sys.stdout = open(os.devnull, 'w')

        def __exit__(self, exc_type, exc_val, exc_tb):
            sys.stdout.close()
            sys.stdout = self._original_stdout
    
    #抓取日投资组合价格
    with HiddenPrints():
        sp=get_portfolio_prices(portfolio,startdate,enddate,RF=RF)
    if sp is None:
        print("  #Error(rar_ratio_portfolio): failed to retrieve portfolio information")
        return None,None
    if len(sp) == 0:
        print("  #Error(rar_ratio_portfolio): no portfolio information found during the period")
        return None,None
    """    
    #计算日收益率，表示为百分比
    import pandas as pd
    ret_pf=pd.DataFrame(sp['Close'].pct_change())*100.0
    ret_pf=ret_pf.dropna()
    
    #第4步：合并投资组合日收益率与无风险利率/市场收益率序列
    if not rf_value_flag:
        #合并rf_df与ret_pf
        reg=pd.merge(ret_pf,rf_df,how='inner',left_index=True,right_index=True)

    else:
        ret_pf['RF']=RF
        reg=ret_pf
        
    reg['Ret-RF']=reg['Close']-reg['RF']
    """
    reg=sp
    reg=reg.dropna()
    if len(reg) == 0:
        message="  #Error("+func_name+"): "+"empty data for ratio calculation"
        print(message)
        return None,None 
    
    #第4步：计算风险调整后的收益率
    ##########风险调整后的收益率，计算开始##########
    calc_func='calc_'+ratio_name+'_ratio'
    rar,rp_mean,beta=eval(calc_func)(reg)
    ##########风险调整后的收益率，计算结束##########
    
    #第5步：打印结果
    if printout == True:
        print_rar_ratio(reg,portfolio,rp_mean,beta,ratio_name,rar)
    
    return rar,rp_mean


if __name__=='__main__':
    pf1={'Market':('US','^GSPC'),'AAPL':0.5,'MSFT':0.3,'IBM':0.2}
    tr1,rp1=rar_ratio_portfolio(pf1,'2019-01-01','2019-01-31',ratio_name='treynor')

#==============================================================================
if __name__=='__main__':
    portfolio={'Market':('US','^GSPC'),'AAPL':1}
    start='2019-12-1'
    end  ='2021-1-31'
    scope='US'
    ratio_name='sharpe'
    window=30
    graph=True    
    
def rar_ratio_rolling(portfolio,start='MRY',end='today',indicator='sharpe',RF=0, \
                      window=21,graph=True,source='auto'):
    """
    功能：滚动计算一个投资组合的风险调整后的收益率指数
    投资组合的结构：{'Market':('US','^GSPC'),'AAPL':0.5,'MSFT':0.3,'IBM':0.2}
    输入：投资组合，开始日期，结束日期，指数名称，滚动窗口宽度(天数)
    输出：风险调整后的收益率指数序列
    注意：因需要滚动计算，开始和结束日期之间需要拉开距离，提前的月数为window/21取整+1；
    另外，无风率可用数据可能距离当前日期滞后约两个月
    
    注意：当RF=False时有bug
    """
    start,end=start_end_preprocess(start,end)
    
    ratio_name=indicator.lower()
    
    #第1步：各种准备和检查工作
    print("  Start to calculate rar ratios, please wait ...")
    #设定错误信息的函数名
    func_name='rar_ratio_portfolio'
    
    ratio_list=['treynor','sharpe','sortino','alpha']
    if ratio_name not in ratio_list:
        message="  #Error("+func_name+"): "+"unsupported rar ratio type"
        print(message,ratio_name)
        return None   
     
    result,startdate,enddate=check_period(start,end)
    if not result:
        message="  #Error("+func_name+"): "+"invalid start or end date"
        print(message,start,end)
        return None    
    #估算数据提前量，重设开始日历日期
    #startdate_delta=int(window/20*30)+30
    startdate_delta=int(window/20*31)
    startdate1=date_adjust(startdate, adjust=-startdate_delta)
    
    #从字典中提取信息
    scope,mktidx,stocklist,portionlist,ticker_type=decompose_portfolio(portfolio)
    pname=portfolio_name(portfolio)
    if pname == '': pname="投资组合"

    #第2步：获得无风险收益率/市场收益率序列
    #获得期间的日无风险收益率(抓取的RF为百分比) 
    rf_value_flag=True #RF以数值形式给出
    if isinstance(RF,bool):
        rf_value_flag=False
        if RF:
            print("  Searching for risk-free interest rate ...")
            if scope=='China':
                rf_df=get_mkt_rf_daily_china(mktidx,start,end,rate_period='1Y',rate_type='shibor',RF=RF)
            else:
                rf_df=get_rf(start,end,scope=scope,freq='daily')  
                if rf_df is None:
                    message="  #Error("+func_name+"): "+"no data available for rf in"
                    print(message,scope,start,end)
                    return None,None 
            RF=rf_df['RF'].mean()
        else:
            RF=0
            rf_value_flag=True  
            
    #第3步：计算投资组合的日收益率序列
    #抓取日投资组合价格
    sp=get_portfolio_prices(portfolio,startdate1,enddate,RF=RF)
    if sp is None:
        print("  #Error(rar_ratio_portfolio): failed to retrieve portfolio information")
        return None,None
    if len(sp) == 0:
        print("  #Error(rar_ratio_portfolio): no portfolio information found during the period")
        return None,None
    """    
    #计算日收益率，表示为百分比
    import pandas as pd
    ret_pf=pd.DataFrame(sp['Close'].pct_change())*100.0
    ret_pf=ret_pf.dropna()
    
    #第4步：合并投资组合日收益率与无风险利率/市场收益率序列
    if not rf_value_flag:
        #合并rf_df与ret_pf
        reg=pd.merge(ret_pf,rf_df,how='inner',left_index=True,right_index=True)

    else:
        ret_pf['RF']=RF
        reg=ret_pf
        
    reg['Ret-RF']=reg['Close']-reg['RF']
    """
    reg=sp
    reg=reg.dropna()
    if len(reg) == 0:
        message="  #Error("+func_name+"): "+"empty data for ratio calculation"
        print(message)
        return None,None 
    
    #第4步：滚动计算风险调整后的收益率
    ##########风险调整后的收益率，计算开始##########
    #用于保存rar和ret_rf_mean
    import pandas as pd
    import numpy as np
    datelist=reg.index.to_list()
    calc_func='calc_'+ratio_name+'_ratio'
    
    rars=pd.DataFrame(columns=('Date','RAR','Mean(Ret)')) 
    for i in np.arange(0,len(reg)):
        i1=i+window-1
        if i1 >= len(reg): break
        
        #构造滚动窗口
        windf=reg[reg.index >= datelist[i]]
        windf=windf[windf.index <= datelist[i1]]
        #print(i,datelist[i],i1,datelist[i1],len(windf))
        
        #使用滚动窗口计算
        try:
            rar,ret_mean=eval(calc_func)(windf)
        except:
            print("  #Error(rar_ratio_rolling): failed in linear regression for",calc_func)
            #print("  windf:\n",windf)
            continue
        
        #记录计算结果
        row=pd.Series({'Date':datelist[i1],'RAR':rar,'Mean(Ret)':ret_mean})
        try:
            rars=rars.append(row,ignore_index=True)        
        except:
            # 可能与Python 3.11有关，不确定
            rars=rars._append(row,ignore_index=True)
        
    rars.set_index(['Date'],inplace=True) 
    ##########风险调整后的收益率，计算结束##########
    
    #第5步：绘图
    if graph == True:
        print("  Rendering graphics ...")
        draw_rar_ratio(rars,portfolio,ratio_name,pname)
    
    return rars


if __name__=='__main__':
    pf1={'Market':('US','^GSPC'),'AAPL':0.5,'MSFT':0.3,'IBM':0.2}
    rars1=rar_ratio_rolling(pf1,'2020-1-1','2020-12-31',ratio_name='sharpe')
#==============================================================================
def draw_rar_ratio(rars,portfolio,ratio_name,pname):
    """
    功能：绘制滚动窗口曲线
    输入：滚动数据df，投资组合，指数名称
    """
    
    scope,mktidx,stocklist,portionlist,ticker_type=decompose_portfolio(portfolio)
    stocklist1,_=cvt_yftickerlist(stocklist)
    
    """
    #平滑处理
    rars1=rars.resample('H')
    #rars2=rars1.interpolate(method='pchip')
    #rars2=rars1.interpolate(method='akima')
    rars2=rars1.interpolate(method='cubic')
    """
        
    #plt.figure(figsize=(12.8,6.4))
 
    labeltxt=ratio_name.capitalize()+'指标'    
    plt.plot(rars['RAR'],label=labeltxt,color='red',lw=1)
    #plt.plot(rars['Mean(Ret)'],label='Stock(s) return(%)',color='blue',lw=1)
    plt.axhline(y=0.0,color='black',linestyle=':')
    """
    titletxt='风险调整收益的滚动趋势'+'\n'+str(ticker_name(stocklist))
    if len(stocklist) > 1:
        titletxt=titletxt+'\n持仓比例: '+str(portionlist)   
    """
    titletxt='风险调整收益的滚动趋势：'+pname
    """
    if len(stocklist) == 1:
        titletxt='风险调整收益的滚动趋势'+'\n（'+ticker_name(stocklist)+'）'   
    """
    #plt.title(titletxt,fontsize=12,fontweight='bold') 
    plt.title(titletxt,fontsize=12) 
    
    #ylabeltxt="比率/指数"
    #plt.ylabel(ylabeltxt,fontsize=12)
    #plt.xticks(rotation=45,fontsize=9)
    plt.gcf().autofmt_xdate() # 优化标注（自动倾斜）
    plt.gca().set_facecolor('whitesmoke')
    #plt.xticks(rotation=30,fontsize=8)
    plt.legend(loc='best') 
    
    import datetime as dt; today=dt.date.today() 
    footnote="数据来源：新浪/stooq/FRED，"+str(today)
    plt.xlabel(footnote)
    plt.show()

    #使用seaborn绘图
    """
    import seaborn as sns
    with sns.axes_style("whitegrid"):
        fig, ax = plt.subplots(figsize=(12.8,6.4))
        ax.plot(rars['RAR'],label=labeltxt,color='red',lw=3)
        #ax.plot(rars['Mean(Ret)'],label='Stock(s) return(%)',color='blue',lw=1)
        plt.axhline(y=0.0,label='Zero return',color='black',linestyle=':')
        ax.set_title(titletxt)
        #ax.set_ylabel(ylabeltxt)
        plt.xticks(rotation=45)
        ax.legend(loc='best')
        ax.set_ylim([1.2*(rars['RAR'].min()), 1.1*(rars['RAR'].max())])    
    """
    return
#==============================================================================
if __name__=='__main__':
    portfolio={'Market':('US','^GSPC'),'AAPL':0.2,'MSFT':0.6,'IBM':0.2}
    start='2019-01-01'
    end  ='2019-01-31'
    

def sharpe_ratio_portfolio(portfolio,start,end,RF=True,printout=True):
    """
    功能：按天计算一个投资组合的夏普指数
    投资组合的结构：{'Market':('US','^GSPC'),'AAPL':0.5,'MSFT':0.3,'IBM':0.2}
    输入：投资组合，开始日期，结束日期
    输出：夏普指数
    """
    #设定错误信息的函数名
    func_name='sharpe_ratio_portfolio'
    
    #检查日期期间的合理性
    valid,start1,end1=check_period(start,end)
    if not valid:
        print("  #Error(sharpe_ratio_portfolio): incorrect start/end date(s)",start,end)
        return None,None       

    #从字典中提取信息
    scope,mktidx,stocklist,portionlist,ticker_type=decompose_portfolio(portfolio)
    
    #检查份额配比是否合理
    """
    if round(sum(portionlist),1) != 1.0:
        print("  #Error(sharpe_ratio_portfolio): Incorrect total of portions")
        return None,None
    """
    
    #获得期间的无风险收益率 
    if isinstance(RF,bool):
        print("  Searching for risk-free interest rate ...")
        if scope=='China':
            rf_df=get_mkt_rf_daily_china(mktidx,start,end,rate_period='1Y',rate_type='shibor',RF=RF)
        else:
            rf_df=get_rf(start,end,scope=scope,freq='daily')  
            if rf_df is None:
                message="  #Error("+func_name+"): "+"no data available for rf in"
                print(message,scope,start,end)
                return None,None 
        RF=rf_df['RF'].mean()
        
    #抓取日投资组合价格：内含Mkt-RF和RF
    sp=get_portfolio_prices(portfolio,start,end,RF=RF)
    #计算日收益率，表示为百分比
    """
    import pandas as pd
    ret_pf=pd.DataFrame(sp['Close'].pct_change())*100.0
    """
    ret_pf=sp
    ret_pf=ret_pf.dropna()  

    #强制转换索引格式，彻底消除下面并表的潜在隐患
    """
    rf_df['ffdate']=rf_df.index.astype('str')
    rf_df['ffdate']=pd.to_datetime(rf_df['ffdate'])
    rf_df.set_index(['ffdate'],inplace=True)
    """
    """
    #合并rf_df与ret_pf
    reg=pd.merge(ret_pf,rf_df,how='inner',left_index=True,right_index=True)
    reg['Ret-RF']=reg['Close']-reg['RF']
    reg=reg.dropna()
    """
    #计算风险溢价Ret-RF均值和标准差
    reg=ret_pf
    ret_rf_mean=reg['Ret-RF'].mean()
    ret_rf_std=reg['Ret-RF'].std()
    
    #计算夏普指数
    sr=ret_rf_mean/ret_rf_std
    
    #打印报告
    if printout == True:
        date_start=str(reg.index[0].year)+'-'+str(reg.index[0].month)+ \
            '-'+str(reg.index[0].day)
        date_end=str(reg.index[-1].year)+'-'+str(reg.index[-1].month)+ \
            '-'+str(reg.index[-1].day)            
        print("\n===== 风险调整收益率 =====")
        """
        _,_,tickerlist,sharelist,ticker_type=decompose_portfolio(portfolio)
        if len(tickerlist)==1:
            product=str(ticker_name(tickerlist,'bond'))
        else:
            product=str(ticker_name(tickerlist,'bond'))+' by '+str(sharelist)
        """
        print("证券资产:",portfolio_name(portfolio))        
        print("样本期间:",date_start,"至",date_end,"(可用日期)")
        print("风险溢价均值%:",round(ret_rf_mean,4))
        print("风险溢价标准差%:",round(ret_rf_std,4))
        print("夏普比率%:",round(sr,4))
        import datetime as dt; today=dt.date.today()
        print("*数据来源：新浪/stooq/FRED，"+str(today))
    
    beta=False
    return sr,ret_rf_mean,beta


if __name__=='__main__':
    portfolio={'Market':('US','^GSPC'),'AAPL':0.2,'MSFT':0.5,'IBM':0.3}
    sr1,rp1=sharpe_ratio_portfolio(portfolio,'2019-01-01','2019-01-31')


#==============================================================================
if __name__=='__main__':
    portfolio={'Market':('US','^GSPC'),'AAPL':0.5,'MSFT':0.3,'IBM':0.2}
    start='2019-01-01'
    end  ='2019-01-31'    

def sortino_ratio_portfolio(portfolio,start,end,RF=True,printout=True):
    """
    功能：按天计算一个投资组合的索梯诺指数
    投资组合的结构：{'Market':('US','^GSPC'),'AAPL':0.5,'MSFT':0.3,'IBM':0.2}
    输入：投资组合，开始日期，结束日期
    输出：索梯诺指数
    """
    #设定错误信息的函数名
    func_name='sortino_ratio_portfolio'    
    
    #检查日期期间的合理性
    valid,start1,end1=check_period(start,end)
    if not valid:
        print("  #Error(sortino_ratio_portfolio): incorrect start/end date(s)")
        return None,None           

    #从字典中提取信息
    scope,mktidx,stocklist,portionlist,ticker_type=decompose_portfolio(portfolio)
    
    #检查份额配比是否合理
    """
    if round(sum(portionlist),1) != 1.0:
        print("  #Error(sortino_ratio_portfolio): Incorrect total of portions")
        return None,None
    """
    
    #获得期间的无风险收益率 
    if isinstance(RF,bool):
        print("  Searching for risk-free interest rate ...")
        if scope=='China':
            rf_df=get_mkt_rf_daily_china(mktidx,start,end,rate_period='1Y',rate_type='shibor',RF=RF)
        else:
            rf_df=get_rf(start,end,scope=scope,freq='daily')  
            if rf_df is None:
                message="  #Error("+func_name+"): "+"no data available for rf in"
                print(message,scope,start,end)
                return None,None 
        RF=rf_df['RF'].mean()
    
    #抓取日投资组合价格
    sp=get_portfolio_prices(portfolio,start,end,RF=RF)
    ret_pf=sp
    """
    #计算日收益率，表示为百分比
    import pandas as pd
    ret_pf=pd.DataFrame(sp['Close'].pct_change())*100.0
    ret_pf=ret_pf.dropna()
    
    #强制转换索引格式，彻底消除下面并表的潜在隐患
    rf_df['ffdate']=rf_df.index.astype('str')
    rf_df['ffdate']=pd.to_datetime(rf_df['ffdate'])
    rf_df.set_index(['ffdate'],inplace=True)
    
    #合并rf_df与ret_pf
    reg=pd.merge(ret_pf,rf_df,how='inner',left_index=True,right_index=True)
    reg['Ret-RF']=reg['Close']-reg['RF']
    """
    reg=ret_pf
    reg=reg.dropna()
    
    #计算风险溢价Ret-RF均值和下偏标准差LPSD
    ret_rf_mean=reg['Ret-RF'].mean()
    reg2=reg[reg['Ret-RF'] < 0]
    ret_rf_lpsd=reg2['Ret-RF'].std()
    
    #计算索梯诺指数
    sr=ret_rf_mean/ret_rf_lpsd
    
    #打印报告
    if printout == True:    
        date_start=str(reg.index[0].year)+'-'+str(reg.index[0].month)+ \
            '-'+str(reg.index[0].day)
        date_end=str(reg.index[-1].year)+'-'+str(reg.index[-1].month)+ \
            '-'+str(reg.index[-1].day)            
        print("\n===== 风险调整收益率 =====")
        """
        _,_,tickerlist,sharelist,ticker_type=decompose_portfolio(portfolio)
        if len(tickerlist)==1:
            product=str(ticker_name(tickerlist,'bond'))
        else:
            product=str(ticker_name(tickerlist,'bond'))+' by '+str(sharelist)
        """
        print("证券资产:",portfolio_name(portfolio))        
        print("样本期间:",date_start,"至",date_end,"(可用日期)")
        print("风险溢价均值%:",round(ret_rf_mean,4))
        print("下偏标准差%:",round(ret_rf_lpsd,4))
        print("索替诺比率%:",round(sr,4))
        
        import datetime as dt; today=dt.date.today()
        print("*数据来源：新浪/stooq/FRED，"+str(today))
    
    return sr,ret_rf_mean


if __name__=='__main__':
    portfolio={'Market':('US','^GSPC'),'AAPL':0.5,'MSFT':0.3,'IBM':0.2}
    sr1,rp1=sortino_ratio_portfolio(portfolio,'2019-01-01','2019-08-03')

#==============================================================================
if __name__=='__main__':
    portfolio={'Market':('China','000001.SS'),'600519.SS':1.0}
    start='2019-01-01'
    end  ='2019-01-31'


def jensen_alpha_portfolio(portfolio,start,end,RF=True,printout=True):
    """
    功能：按天计算一个投资组合的阿尔法指数
    投资组合的结构：{'Market':('US','^GSPC'),'AAPL':0.5,'MSFT':0.3,'IBM':0.2}
    输入：投资组合，开始日期，结束日期
    输出：阿尔法指数
    """
    #设定错误信息的函数名
    func_name='jensen_alpha_portfolio'    
    
    #检查日期期间的合理性
    valid,start1,end1=check_period(start,end)
    if not valid:
        print("  #Error(jensen_alpha_portfolio): incorrect start/end date(s)")
        return None,None          
    
    #从字典中提取信息
    scope,mktidx,stocklist,portionlist,ticker_type=decompose_portfolio(portfolio)    
    #检查份额配比是否合理
    """
    if round(sum(portionlist),1) != 1.0:
        print("  #Error(jensen_alpha_portfolio): incorrect total of portions.")
        return None,None
    """
    
    #获得期间的无风险收益率      
    if isinstance(RF,bool):
        print("  Searching for risk-free interest rate ...")
        if scope=='China':
            rf_df=get_mkt_rf_daily_china(mktidx,start,end,rate_period='1Y',rate_type='shibor',RF=RF)
        else:
            rf_df=get_rf(start,end,scope=scope,freq='daily')  
            if rf_df is None:
                message="  #Error("+func_name+"): "+"no data available for rf in"
                print(message,scope,start,end)
                return None,None 
        RF=rf_df['RF'].mean()
    
    #抓取日投资组合价格：内含Mkt-RF和RF
    sp=get_portfolio_prices(portfolio,start,end,RF=RF)
    #计算日收益率，表示为百分比
    ret_pf=sp
    """
    import pandas as pd
    ret_pf=pd.DataFrame(sp['Close'].pct_change())*100.0
    ret_pf=ret_pf.dropna()
    
    #强制转换索引格式，彻底消除下面并表的潜在隐患
    rf_df['ffdate']=rf_df.index.astype('str')
    rf_df['ffdate']=pd.to_datetime(rf_df['ffdate'])
    rf_df.set_index(['ffdate'],inplace=True)
    
    if rf_df is None:
        print("  #Error(jensen_alpha_portfolio): data source did not respond.")
        return None,None        
    if len(rf_df) == 0:
        print("  #Error(jensen_alpha_portfolio): data source returned empty data.")
        return None,None 
    
    #合并rf_df与ret_pf
    reg=pd.merge(ret_pf,rf_df,how='inner',left_index=True,right_index=True)
    reg['Ret-RF']=reg['Close']-reg['RF']
    """
    reg=ret_pf
    reg=reg.dropna()
    if len(reg) == 0:
        print("  #Error(jensen_alpha_portfolio): empty data for regression.")
        return None,None     
    ret_rf_mean=reg['Ret-RF'].mean()
    
    #使用CAPM回归计算投资组合的贝塔系数，这里得到的alpha就是Jensen's alpha
    from scipy import stats
    output=stats.linregress(reg['Mkt-RF'],reg['Ret-RF'])
    (beta,alpha,r_value,p_value,std_err)=output 
    
    #打印报告
    if printout == True:
        date_start=str(reg.index[0].year)+'-'+str(reg.index[0].month)+ \
            '-'+str(reg.index[0].day)
        date_end=str(reg.index[-1].year)+'-'+str(reg.index[-1].month)+ \
            '-'+str(reg.index[-1].day)            
        print("\n===== 风险调整收益率 =====")
        """
        _,_,tickerlist,sharelist,ticker_type=decompose_portfolio(portfolio)
        if len(tickerlist)==1:
            product=str(ticker_name(tickerlist,'bond'))
        else:
            product=str(ticker_name(tickerlist,'bond'))+' by '+str(sharelist)
        """
        print("证券资产:",portfolio_name(portfolio))        
        print("样本期间:",date_start,"至",date_end,"(可用日期)")
        print("贝塔系数:",round(beta,4))
        print("风险溢价均值%:",round(ret_rf_mean,4))
        print("詹森阿尔法%:",round(alpha,4))
        
        import datetime as dt; today=dt.date.today()
        print("*数据来源：新浪/stooq/FRED，"+str(today))        
    
    return alpha,ret_rf_mean,beta


if __name__=='__main__':
    portfolio={'Market':('US','^GSPC'),'AAPL':0.5,'MSFT':0.3,'IBM':0.2}
    alpha1=jensen_alpha_portfolio(portfolio,'2019-01-01','2019-08-03')

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
if __name__=='__main__':
    portfolio={'Market':('US','^GSPC'),'JD':0.3,'BABA':0.7}
    start='2019-01-01'
    end='2019-03-31'
    rar_type='sortino_ratio'    
    
def plot_rar_monthly(portfolio,start,end,rar_type):
    """
    功能：将风险调整收益率和风险溢价逐月绘图对比
    输入：投资组合，开始/结束日期，风险调整收益指数类别
    输出：风险调整收益率和风险溢价的逐月数据框
    显示：按月绘图投资组合的风险调整收益率和风险溢价
    """

    #检查日期期间的合理性
    valid,start1,end1=check_period(start,end)
    if not valid:
        print("  #Error(plot_rar_monthly): incorrect start/end date(s)",start,end)
        return None         
    
    #检查投资组合各个成分股份额的合理性
    """
    if round(sum(portionlist),1) != 1.0:
        print("  #Error(plot_rar_monthly): Incorrect total of portions")
        return None    
    """
    
    #检查支持的rar_type
    rar_list=['treynor_ratio','sharpe_ratio','sortino_ratio','jensen_alpha']
    if rar_type not in rar_list:
        print("  #Error(plot_rar_monthly): not supported rar type")
        print("  Supported rar type:",rar_list)              
        return None         

    #拆分start/end之间的各个年份和月份
    mdlist=calc_monthly_date_range(start,end)
    if len(mdlist) == 0:
        print("  #Error(plot_rar_monthly): start/end dates inappropriate",start,end)
        return None          

    #用于保存risk premium和rar
    print("\n  Calculating monthly",rar_type,"......")
    rarfunc=rar_type+'_portfolio'
    rars=pd.DataFrame(columns=('YM','rp','rar'))
    for i in range(0,len(mdlist)):
        start=mdlist[i][0]
        YM=start.strftime("%Y-%m")
        print('  ',YM,end=' ')
        end=mdlist[i][1]
        rar,rp=eval(rarfunc)(portfolio,start,end,printout=False)
        
        row=pd.Series({'YM':YM,'rp':rp,'rar':rar})
        try:
            rars=rars.append(row,ignore_index=True)
        except:
            rars=rars._append(row,ignore_index=True)
    print("  Searching completed.")
    rars.set_index('YM',inplace=True)    

    #绘图    
    plt.plot(rars['rp'],label='risk_premium',c='blue',marker='*',ls=':',lw=3)
    plt.plot(rars['rar'],label=rar_type,c='r',lw=3,marker='o')
    plt.axhline(y=0.0,color='black',linestyle=':',lw=1) 
    titletxt="投资组合的风险调整收益"
    plt.title(titletxt)
    plt.ylabel('收益率(%)')
    
    plt.gcf().autofmt_xdate() # 优化标注（自动倾斜）
    plt.gca().set_facecolor('whitesmoke')
    
    #plt.xticks(rotation=30)
    plt.legend(loc='best')

    import datetime as dt; today=dt.date.today() 
    footnote="数据来源：新浪/stooq/FRED，"+str(today)
    plt.xlabel(footnote)   
    
    plt.show()

    return


if __name__=='__main__':
    portfolio={'Market':('US','^GSPC'),'VIPS':0.1,'PDD':0.2,'JD':0.3,'BABA':0.4}
    plot_rar_monthly(portfolio,'2019-01-01','2019-06-30','treynor_ratio') 

    portfolio={'Market':('US','^GSPC'),'AAPL':1.0}
    plot_rar_monthly(portfolio,'2017-01-01','2017-12-31','sharpe_ratio')       
#==============================================================================
#==============================================================================
if __name__=='__main__':
    portfolio={'Market':('US','^GSPC'),'JD':0.3,'BABA':0.7}
    start='2013-01-01'
    end='2018-12-31'
    rar_type='sortino_ratio'    


def plot_rar_annual(portfolio,start,end,rar_type):
    """
    功能：将风险调整收益率和风险溢价逐年绘图对比
    输入：投资组合，开始/结束日期，风险调整收益指数类别
    输出：风险调整收益率和风险溢价的逐年数据框
    显示：按年绘图投资组合的风险调整收益率和风险溢价
    """
    #检查日期期间的合理性
    valid,start1,end1=check_period(start,end)
    if not valid:
        print("  #Error(plot_rar_annual): incorrect start/end date(s)",start.end)
        return None      
    
    #检查投资组合各个成分股份额的合理性
    """
    if round(sum(portionlist),1) != 1.0:
        print("  #Error(plot_rar_annual): Incorrect total of portions")
        return None    
    """

    #检查支持的rar_type
    rar_list=['treynor_ratio','sharpe_ratio','sortino_ratio','jensen_alpha']
    if rar_type not in rar_list:
        print("  #Error(plot_rar_annual): not supported rar type")
        print("  Supported rar type:",rar_list)              
        return None         

    #拆分start/end之间的各个年份和月份
    mdlist=calc_yearly_date_range(start,end)
    if len(mdlist) == 0:
        print("  #Error(plot_rar_annual): start/end dates inappropriate")
        return None          

    #用于保存risk premium和rar
    print("\n  Calculating yearly",rar_type,"......")
    rarfunc=rar_type+'_portfolio'
    rars=pd.DataFrame(columns=('YR','rp','rar'))
    for i in range(0,len(mdlist)):
        start=mdlist[i][0]
        YR=start.strftime("%Y")
        print('  ',YR,end=' ')
        end=mdlist[i][1]
        rar,rp=eval(rarfunc)(portfolio,start,end,printout=False)
        
        row=pd.Series({'YR':YR,'rp':rp,'rar':rar})
        try:
            rars=rars.append(row,ignore_index=True)
        except:
            rars=rars._append(row,ignore_index=True)
    print("  Searching completed.")
    rars.set_index('YR',inplace=True)    

    #绘图    
    plt.plot(rars['rp'],label='risk_premium',c='blue',marker='*',ls=':',lw=3)
    plt.plot(rars['rar'],label=rar_type,c='r',lw=3,marker='o')
    plt.axhline(y=0.0,color='black',linestyle=':',lw=1) 
    titletxt="投资组合的风险调整收益"
    plt.title(titletxt)
    plt.ylabel('收益率(%)')
    
    plt.gcf().autofmt_xdate() # 优化标注（自动倾斜）
    plt.gca().set_facecolor('whitesmoke')
    
    #plt.xticks(rotation=45)
    plt.legend(loc='best')
    
    import datetime as dt; today=dt.date.today() 
    footnote="数据来源：新浪/stooq/FRED，"+str(today)
    plt.xlabel(footnote)
    
    plt.show()

    return


if __name__=='__main__':
    portfolio={'Market':('US','^GSPC'),'VIPS':0.1,'PDD':0.2,'JD':0.3,'BABA':0.4}
    plot_rar_annual(portfolio,'2013-01-01','2019-06-30','treynor_ratio') 

    portfolio={'Market':('US','^GSPC'),'AAPL':1.0}
    plot_rar_annual(portfolio,'2015-01-01','2017-12-31','sharpe_ratio')       
#==============================================================================
# 新加入的滚动指标对比
#==============================================================================
if __name__=='__main__':
    portfolio1={'Market':('US','^GSPC'),'AAPL':1}
    portfolio2={'Market':('US','^GSPC'),'MSFT':1}
    
    start='2020-1-1'
    end  ='2020-12-31'
    scope='US'
    ratio_name='sharpe'
    window=30
    graph=True  

def compare_rar_portfolio(portfolio1,portfolio2,start,end,ratio_name='sharpe', \
                      window=240,graph=True):
    """
    功能：比较两个投资组合的风险调整收益率，并绘制曲线
    注意：无风险收益率有两个月的延迟
    """
    
    #检查日期的合理性
    result,startdate,enddate=check_period(start,end)
    if result is None:
        print("  #Error(compare_rar_portfolio): invalid period",start,end)
        return None     

    #检查支持的指标
    ratio_list=['treynor','sharpe','sortino','alpha']
    name_list=['特雷诺比率','夏普比率','索替诺比率','詹森阿尔法']
    if ratio_name not in ratio_list:
        message="  #Error(compare_rar_portfolio): "+"unsupported rar ratio type"
        print(message,ratio_name)
        return None    
    
    #计算开始日期的提前量：假定每月有20个交易日
    adjdays=int(window/20.0*30.0)+1
    import siat.common as cmn
    new_start=cmn.date_adjust(start, adjust=-adjdays)
    
    #获取第一个投资组合的数据
    rars1=rar_ratio_rolling(portfolio1,new_start,end,ratio_name=ratio_name, \
                            window=window,graph=False)
    if rars1 is None: return None
    #获取第二个投资组合的数据
    rars2=rar_ratio_rolling(portfolio2,new_start,end,ratio_name=ratio_name, \
                            window=window,graph=False)
    if rars2 is None: return None
    
    #绘制双线图
    ticker1="证券1"
    colname1='RAR'
    label1=name_list[ratio_list.index(ratio_name)]
    
    ticker2="证券2"
    colname2='RAR'
    label2=label1    
    
    ylabeltxt=label1 
    titletxt="证券风险调整收益的滚动趋势对比"
    
    _,_,tickers1,shares1,ticker_type=decompose_portfolio(portfolio1)
    if len(tickers1) == 1:
        ticker1=tickers1[0]
        pf1str=tickers1[0]
    else:
        pf1str=ticker1+'：成分'+str(tickers1)+'，比例'+str(shares1)
    
    _,_,tickers2,shares2,ticker_type=decompose_portfolio(portfolio2)
    if len(tickers2) == 1:
        ticker2=tickers2[0]
        pf2str=tickers2[0]
    else:
        pf2str=ticker2+'：成分'+str(tickers2)+'，比例'+str(shares2)
        
    footnote="日期 -->"
    if len(tickers1) > 1:
        footnote=footnote+'\n'+pf1str
    if len(tickers2) > 1:
        footnote=footnote+'\n'+pf2str        
        
    import datetime as dt; today=dt.date.today() 
    source="数据来源：新浪/stooq/FRED，"+str(today)    
    footnote=footnote+"\n"+source
    
    plot_line2(rars1,ticker1,colname1,label1, \
                 rars2,ticker2,colname2,label2, \
                 ylabeltxt,titletxt,footnote)

    #合并RAR
    import pandas as pd
    rarm=pd.merge(rars1,rars2,how='inner',left_index=True,right_index=True)
    rars=rarm[['RAR_x','RAR_y']]
    rars.rename(columns={'RAR_x':ticker1+'_'+ratio_name,'RAR_y':ticker2+'_'+ratio_name},inplace=True)
    
    return rars


if __name__=='__main__':
    pf1={'Market':('US','^GSPC'),'AAPL':1}
    pf2={'Market':('US','^GSPC'),'MSFT':1}    
    rars12=compare_rar_portfolio(pf1,pf2,'2019-11-1','2020-11-30')
    
    pfA={'Market':('China','000001.SS'),'600519.SS':1}
    pfB={'Market':('China','000001.SS'),'000858.SZ':1}
    rarsAB=compare_rar_portfolio(pfA,pfB,'2019-11-1','2020-11-30')
    
    pfbb={'Market':('US','^GSPC'),'BABA':1}
    pfjd={'Market':('US','^GSPC'),'JD':1}  
    rarsbj=compare_rar_portfolio(pfbb,pfjd,'2019-11-1','2020-11-30')
    
    pfbb={'Market':('US','^GSPC'),'BABA':1}
    pfpd={'Market':('US','^GSPC'),'PDD':1}  
    rarsbj=compare_rar_portfolio(pfbb,pfpd,'2019-11-1','2020-11-30')      

#==============================================================================
#==============================================================================

if __name__=='__main__':
    tickers = ['000858.SZ','600779.SS','000596.SZ','603589.SS']
    start='2022-1-1'
    end='2022-10-31'
    rar_name="sharpe"
    market_index="000300.SS"
    market="China"
    
    tickers=['AAPL','01810.HK','000063.SZ']
    start='2023-1-1'
    end='2023-7-1'
    
    RF=False
    window=240
    axhline_value=0
    axhline_label=''
    graph=True
    printout=True
    sortby='tpw_mean'
    
    graph=False
    source='auto'
    trailing=20

def compare_mrar(tickers,rar_name,start,end, \
                 market="China",market_index="000300.SS",RF=False,window=63, \
                 axhline_value=0,axhline_label='零线',graph=True,printout=True, \
                 sortby='tpw_mean',source='auto',trailing=20,trend_threshhold=0.001, \
                 annotate=False):
    """
    功能：计算多只股票的rar比率，并绘图对比。多只股票必须处于同一个经济体的证券市场
    比率：支持夏普比率、特雷诺比率、索替诺比率、阿尔法比率
    
    sortby: 
        tpw_mean(近期优先加权平均值降序排列)
        min(最小值降序排列)
        mean(平均值降序排列)
        median(中位数值降序排列)
        trailing(短期趋势，最新数值与近trailing个交易日均值的差值降序排列)
    
    注意：当RF=False时可能有bug
    """    
    #检查tickers是否为列表且不少于两只股票
    tickers=upper_ticker(tickers)
    
    #检查rar指标的种类
    rarlist=['treynor','sharpe','sortino','alpha']
    if not (rar_name.lower() in rarlist):
        print("  #Error(compare_mrar): unsupported rar name",rar_name)
        return None
    
    # 去掉重复代码
    tickers=list(set(tickers))
    
    #检查支持的比率种类
    
    #检查日期的合理性
    
    #将开始日期提前
    start1=date_adjust(start,-(int(window/20*31)+1))
    
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
    print("  Starting to retrieve and calculate",rar_name,"ratio, please wait ......")
    for t in tickers:
        
        pf={'Market':(market,market_index),t:1.0}
        #关闭print输出
        with HiddenPrints():
            df_tmp=rar_ratio_rolling(pf,start1,end,ratio_name=rar_name, \
                                     RF=RF,window=window,graph=False,source=source)
        
        if df_tmp is None:
            print("  #Warning(compare_mrar): data not available for",t)
            continue
        else:
            dft=df_tmp[['RAR']]
            #dft.rename(columns={'RAR':ticker_name(t)},inplace=True)
            dft.rename(columns={'RAR':t},inplace=True)
            
        if len(df)==0:
            #第一个
            df=dft
        else:
            df=pd.merge(df,dft,how='outer',left_index=True,right_index=True)

    if len(df)==0:
        print("  #Warning(compare_mrar): no data available for the above securities between",start,end)        
        return None
    
    # 填充空缺值
    df.fillna(method='ffill',inplace=True) #使用前值填充
    df.fillna(method='bfill',inplace=True) #使用后值填充
    
    #绘制多条曲线
    rar_list=['treynor','sortino','sharpe','alpha']
    rar_list_e=['Treynor Ratio','Sortino Ratio','Sharpe Ratio','Jensen alpha']
    #rar_list_c=['特雷诺比率','索替诺比率','夏普比率','阿尔法指数']
    rar_list_c=['特雷诺比率','索替诺比率','夏普比率','阿尔法指标']
    
    pos=rar_list.index(rar_name)
    
    import datetime; today = datetime.date.today()
    
    lang=check_language()
    if lang == 'English':
        
        y_label=rar_list_e[pos]
        x_label="Source: sina/stooq, "+str(today)
        title_txt="Compare Multiple Risk-adjusted Return Performance"
    else:
        y_label=rar_list_c[pos]
        x_label="数据来源: 新浪/stooq/Yahoo，"+str(today)
        title_txt="比较多只证券的风险调整收益滚动指标"

    startpd=pd.to_datetime(start)
    df1=df[df.index >= startpd]        

    # 是否绘图
    if graph:
        # 翻译证券名称
        for c in list(df1):
            df1.rename(columns={c:ticker_name(c)},inplace=True)
        
        draw_lines(df1,y_label,x_label, \
                   axhline_value=axhline_value,axhline_label=axhline_label, \
                   title_txt=title_txt,data_label=False,annotate=annotate)

    if printout:
        
        dfcols=list(df)
        for c in dfcols:
            ccn=ticker_name(c)+'('+c+')'
            df.rename(columns={c:ccn},inplace=True)
        
        if sortby=='tpw_mean':
            sortby_txt='按推荐标记+近期优先加权平均值降序排列'
        elif sortby=='min':
            sortby_txt='按推荐标记+最小值降序排列'
        elif sortby=='mean':
            sortby_txt='按推荐标记+平均值降序排列'
        elif sortby=='median':
            sortby_txt='按推荐标记+中位数值降序排列'
        elif sortby=='trailing':
            sortby_txt='按推荐标记+短期均值走势降序排列'
        else:
            pass
        
        title_txt='*** '+title_txt+'：'+y_label+'，'+sortby_txt
        additional_note="*** 注：列表仅显示有星号标记或特定数量的证券。"
        footnote='期间趋势范围：'+str(start)+'至'+str(end)+"；近期趋势范围：近"+str(trailing)+"个交易日"
        descriptive_statistics(df,title_txt,additional_note+footnote,decimals=4, \
                               sortby=sortby,recommend_only=True,trailing=trailing, \
                               trend_threshhold=trend_threshhold)

    return df1

if __name__=='__main__':
    tickers = ['000858.SZ','600779.SS','000596.SZ','603589.SS','000001.SS']
    df=compare_mrar(tickers,'sharpe','2022-1-1','2022-10-31')
    df=compare_mrar(tickers,'alpha','2022-10-1','2022-10-31')

#==============================================================================

if __name__=='__main__':
    ticker = '000858.SZ'
    start='2022-1-1'
    end='2022-10-31'
    rar_names=["sharpe",'sortino','alpha']
    market_index="000300.SS"
    market="China"
    
    RF=False
    window=60
    axhline_value=0
    axhline_label=''
    graph=True
    printout=False
    sortby='tpw_mean'
    
    graph=False
    source='auto'
    trailing=20

def compare_1security_mrar(ticker,rar_names,start,end, \
                 market="China",market_index="000300.SS",RF=False,window=63, \
                 axhline_value=0,axhline_label='零线',graph=True,printout=False, \
                 sortby='tpw_mean',source='auto',trailing=20,trend_threshhold=0.001, \
                 annotate=False):
    """
    功能：计算一只股票的多个rar比率，并绘图对比
    比率：支持夏普比率、特雷诺比率、索替诺比率、阿尔法比率等
    
    sortby: 
        tpw_mean(近期优先加权平均值降序排列)
        min(最小值降序排列)
        mean(平均值降序排列)
        median(中位数值降序排列)
        trailing(短期趋势，最新数值与近trailing个交易日均值的差值降序排列)
    """   
    DEBUG=True
    
    rar_list=['treynor','sharpe','sortino','alpha']
    rar_list_c=['特雷诺比率','夏普比率','索替诺比率','阿尔法指标']
    
    valid,start1,end1=check_period(start,end)
    if not valid:
        print("  #Error(compare_1security_mrar): invalid period from",start,'to',end)
        return None
    
    if isinstance(ticker,str):
        tickers=[ticker]
    elif isinstance(ticker,list):
        tickers=[ticker[0]]
    else:
        print("  #Warning(compare_1security_mrar): unsupported ticker for",ticker)
        return None
    
    import pandas as pd
    df=pd.DataFrame()
    for r in rar_names:
        if not (r in rar_list):
            print("  #Warning(compare_1security_mrar): unsupported rar indicator for",r)
            continue
        
        dft=compare_mrar(tickers=tickers,rar_name=r, \
                         start=start,end=end, \
                         market=market,market_index=market_index, \
                         RF=RF,window=window, \
                         axhline_value=0,axhline_label='零线', \
                         graph=False,printout=False, \
                         sortby=sortby,source=source,trailing=trailing,trend_threshhold=trend_threshhold)
        if dft is None:
            print("  #Error(compare_1security_mrar): information unaccessible for",tickers[0])
            break
        if len(dft)==0:
            print("  #Error(compare_1security_mrar): information unavailable for",tickers[0],'from',start,'to',end)
            break
        
        pos=rar_list.index(r)
        rcn=rar_list_c[pos]
        dft.columns=[rcn]
        
        if len(df)==0:
            df=dft
        else:
            df=pd.merge(df,dft,how='inner',left_index=True,right_index=True)
            
    if len(df)==0:
        return None
    
    import datetime; today = datetime.date.today()
    y_label="风险调整收益指标"
    x_label="数据来源: 综合新浪/stooq/Yahoo，"+str(today)
    title_txt="证券风险调整收益滚动指标："+ticker_name(tickers[0])

    # 是否绘图
    if graph:
        draw_lines(df,y_label,x_label, \
                   axhline_value=axhline_value,axhline_label=axhline_label, \
                   title_txt=title_txt,data_label=False,annotate=annotate)
    
    return df    
    
    
#==============================================================================


