# -*- coding: utf-8 -*-
"""
本模块功能：为维持兼容性，套壳stock的模块
所属工具包：证券投资分析工具SIAT 
SIAT：Security Investment Analysis Tool
创建日期：2021年5月16日
最新修订日期：
作者：王德宏 (WANG Dehong, Peter)
作者单位：北京外国语大学国际商学院
作者邮件：wdehong2000@163.com
版权所有：王德宏
用途限制：仅限研究与教学使用，不可商用！商用需要额外授权。
特别声明：作者不对使用本工具进行证券投资导致的任何损益负责！
"""
#==============================================================================
#屏蔽所有警告性信息
import warnings; warnings.filterwarnings('ignore')
#==============================================================================
from siat.common import *
from siat.translate import *
from siat.grafix import *
from siat.security_prices import *
from siat.security_price2 import *

# 复制股票分析函数
from siat.stock import *
#==============================================================================
#==============================================================================
#==============================================================================
# 功能：灵活比较证券指标：先获取收盘价，再行计算、比较和绘图
# 特点1：比compare_security更灵活，可处理债券指数与股票指数的比较
# 特点2：可处理短期国债与长期国债的收益率，模拟短期和长期无风险收益率
#==============================================================================
if __name__=='__main__':
    df1=get_prices('000300.SS','2018-1-1','2020-12-31')

    from siat.bond import *
    df2=bond_prices_china('中债-综合指数','2018-1-1','2020-12-31',graph=False)    
    
    indicator='Annual Ret%'
    fromdate='2019-7-1'
    todate='2020-6-30'
    graph=True
    power=0
    zeroline=True
    twinx=False

def compare_indicator(df1,df2,indicator,fromdate,todate, \
                      graph=True,power=0,zeroline=True, \
                      twinx=False,loc1='upper left',loc2='lower left'):
    """
    功能：基于两个数据表df1/df2中的列Close/Adj Close计算指标indicator，绘图比较
    输入要求：数据表df1/df2中需要，索引为datetime，Close， Adj Close，ticker，source和footnote
    当footnote为空时不需要显示
    """
    #检查日期期间
    result,start,end=check_period(fromdate,todate)
    if not result:
        print("  #Error(compare_indicator): invalid date period from",fromdate,'to',todate)
        if graph: return      
        else: return None
    
    #检查是否支持该indicator
    indlist=['Close','Adj Close','Daily Ret','Daily Ret%','Daily Adj Ret','Daily Adj Ret%',
             'log(Daily Ret)','log(Daily Adj Ret)','Weekly Ret','Weekly Ret%',
             'Weekly Adj Ret','Weekly Adj Ret%','Monthly Ret','Monthly Ret%',
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
             'Weekly Adj Ret LPSD', 'Weekly Adj Ret LPSD%', 'Monthly Ret LPSD',
             'Monthly Ret LPSD%', 'Monthly Adj Ret LPSD', 'Monthly Adj Ret LPSD%',
             'Quarterly Ret LPSD', 'Quarterly Ret LPSD%', 'Quarterly Adj Ret LPSD',
             'Quarterly Adj Ret LPSD%', 'Annual Ret LPSD', 'Annual Ret LPSD%',
             'Annual Adj Ret LPSD', 'Annual Adj Ret LPSD%', 'Exp Ret LPSD',
             'Exp Ret LPSD%', 'Exp Adj Ret LPSD', 'Exp Adj Ret LPSD%']
    if indicator not in indlist:
        print("  #Error(compare_indicator): unsupported indicator",indicator)
        print("  Supported indicators:",indlist)
        if graph: return      
        else: return None   
    
    print("  Calculating indicators ......")
    #计算df1中的indicator
    df1i=calc_indicators(df1,indicator)   
    df1i1=df1i[df1i.index >=start]
    df1i2=df1i1[df1i1.index <= end]
    
    #计算df2中的indicator
    df2i=calc_indicators(df2,indicator)
    df2i1=df2i[df2i.index >=start]
    df2i2=df2i1[df2i1.index <= end]    
    
    #绘图
    ticker1=ticker_name(df1i2['ticker'][0])
    colname1=indicator
    label1=ectranslate(indicator)

    ticker2=ticker_name(df2i2['ticker'][0])
    colname2=indicator
    label2=ectranslate(indicator)
    
    ylabeltxt=label1
    titletxt="证券指标走势比较"
    
    note=''
    note1=df1i2['footnote'][0]
    if note1 != '':
        #note="证券1："+note1
        note=note1
    note2=df2i2['footnote'][0]
    if note2 != '':
        #note=note+"，证券2："+note2
        note=note+"；"+note2
    if note != '':
        note=note+'\n'
    
    source1=df1i2['source'][0]
    source2=df2i2['source'][0]
    if source1 == source2:
        source=source1
    else:
        source=source1+'，'+source2
    
    import datetime
    today = datetime.date.today().strftime("%Y-%m-%d")
    source="数据来源："+source+'，'+today    
    
    footnote=''
    if note != '':
        footnote=note+source
    else:
        footnote=source
    
    plot_line2(df1i2,ticker1,colname1,label1, \
               df2i2,ticker2,colname2,label2, \
               ylabeltxt,titletxt,footnote, \
               power=power,zeroline=zeroline, \
               twinx=twinx,loc1=loc1,loc2=loc2)

    if graph: return      
    else: return df1i2,df2i2  

if __name__=='__main__':
    compare_indicator(df1,df2,'Annual Ret%','2019-7-1','2020-6-30')
    compare_indicator(df1,df2,'Annual Ret Volatility%','2019-7-1','2020-6-30')
    
    from siat.bond import *
    search_bond_index_china(keystr='国债',printout=True)
    df1=bond_index_china('中债-0-1年国债指数','2018-1-1','2020-12-31',graph=False)
    df2=bond_index_china('中债-10年期国债指数','2018-1-1','2020-12-31',graph=False)
    compare_indicator(df1,df2,'Annual Ret%','2019-7-1','2020-6-30')
    compare_indicator(df1,df2,'Annual Ret Volatility%','2019-7-1','2020-6-30')
    compare_indicator(df1,df2,'Exp Ret%','2019-7-1','2020-6-30')
    
    
#==============================================================================
if __name__=='__main__':
    from siat.bond import *
    search_bond_index_china(keystr='国债',printout=True)
    df1=bond_index_china('中债-10年期国债指数','2018-1-1','2020-12-31',graph=False)
    
    indicator='Annual Ret%'
    fromdate='2019-7-1'
    todate='2020-6-30'
    graph=True
    power=0
    zeroline=True
    twinx=False

def draw_indicator(df1,indicator,fromdate,todate, \
                      graph=True,power=0,zeroline=True):
    """
    功能：基于单个数据表df1中的列Close/Adj Close计算指标indicator，绘图
    输入要求：数据表df1中需要，索引为datetime，Close， Adj Close，ticker和footnote
    当footnote为空时不需要显示
    """
    #检查日期期间
    result,start,end=check_period(fromdate,todate)
    if not result:
        print("  #Error(calc_indicator): invalid date period from",fromdate,'to',todate)
        if graph: return      
        else: return None
    
    #检查是否支持该indicator
    indlist=['Close','Adj Close','Daily Ret','Daily Ret%','Daily Adj Ret','Daily Adj Ret%',
             'log(Daily Ret)','log(Daily Adj Ret)','Weekly Ret','Weekly Ret%',
             'Weekly Adj Ret','Weekly Adj Ret%','Monthly Ret','Monthly Ret%',
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
             'Weekly Adj Ret LPSD', 'Weekly Adj Ret LPSD%', 'Monthly Ret LPSD',
             'Monthly Ret LPSD%', 'Monthly Adj Ret LPSD', 'Monthly Adj Ret LPSD%',
             'Quarterly Ret LPSD', 'Quarterly Ret LPSD%', 'Quarterly Adj Ret LPSD',
             'Quarterly Adj Ret LPSD%', 'Annual Ret LPSD', 'Annual Ret LPSD%',
             'Annual Adj Ret LPSD', 'Annual Adj Ret LPSD%', 'Exp Ret LPSD',
             'Exp Ret LPSD%', 'Exp Adj Ret LPSD', 'Exp Adj Ret LPSD%']
    if indicator not in indlist:
        print("  #Error(calc_indicator): unsupported indicator",indicator)
        print("  Supported indicators:",indlist)
        if graph: return      
        else: return None   
    
    print("  Calculating indicators ......")
    #计算df1中的indicator
    df1i=calc_indicators(df1,indicator)   
    df1i1=df1i[df1i.index >=start]
    df1i2=df1i1[df1i1.index <= end]
    
    
    #绘图
    ticker1=ticker_name(df1i2['ticker'][0])
    colname1=indicator
    label1=ectranslate(indicator)

    ylabeltxt=label1
    titletxt="证券指标走势："+ticker1
    
    note=''
    note1=df1i2['footnote'][0]
    if note1 != '':
        note="证券1："+note1
    if note != '':
        note=note+'\n'
    
    source1=df1i2['source'][0]
    source=source1
    
    import datetime
    today = datetime.date.today().strftime("%Y-%m-%d")
    source="数据来源："+source+'，'+today    
    
    footnote=''
    if note != '':
        footnote=note+source
    else:
        footnote=source
    
    plot_line(df1i2,colname1,label1,ylabeltxt,titletxt,footnote, \
              power=power,zeroline=zeroline)
    #print("power=",power,"zeroline=",zeroline)

    if graph: return      
    else: return df1i2

if __name__=='__main__':
    draw_indicator(df1,'Annual Ret%','2019-7-1','2020-6-30')
#==============================================================================
if __name__=='__main__':
    indicator=''
    df=df1

def calc_indicators(df,indicator):
    """
    功能：基于df中的列Close/Adj Close计算indicator，生成新的列indicator
    """
    
    #计算indicator
    #import siat.stock as sst
    import siat.security_prices as sst
    #加入日收益率
    df1=sst.calc_daily_return(df)
    df1.dropna(subset=['Daily Ret'],inplace=True)
    fromdate=df1.index[0].strftime("%Y-%m-%d")
    
    #加入滚动收益率
    df1a=sst.calc_rolling_return(df1, "Weekly") 
    df1b=sst.calc_rolling_return(df1a, "Monthly")
    df1c=sst.calc_rolling_return(df1b, "Quarterly")
    df1d=sst.calc_rolling_return(df1c, "Annual")         
    #加入扩展收益率
    df2=sst.calc_expanding_return(df1d,fromdate)    
    collist=list(df2)
    if indicator in collist:
        return df2
    
    #加入滚动价格波动风险
    df2a=sst.rolling_price_volatility(df2, "Weekly") 
    df2b=sst.rolling_price_volatility(df2a, "Monthly")
    df2c=sst.rolling_price_volatility(df2b, "Quarterly")
    df2d=sst.rolling_price_volatility(df2c, "Annual") 
    #加入累计价格波动风险
    df3=sst.expanding_price_volatility(df2d,fromdate)    
    collist=list(df3)
    if indicator in collist:
        return df3
    
    #加入滚动收益率波动风险
    df3a=sst.rolling_ret_volatility(df3, "Weekly") 
    df3b=sst.rolling_ret_volatility(df3a, "Monthly")
    df3c=sst.rolling_ret_volatility(df3b, "Quarterly")
    df3d=sst.rolling_ret_volatility(df3c, "Annual") 
    #加入累计收益率波动风险
    df4=sst.expanding_ret_volatility(df3d,fromdate)    
    collist=list(df4)
    if indicator in collist:
        return df4
    
    #加入滚动收益率下偏标准差
    df4a=sst.rolling_ret_lpsd(df4, "Weekly") 
    df4b=sst.rolling_ret_lpsd(df4a, "Monthly")
    df4c=sst.rolling_ret_lpsd(df4b, "Quarterly")
    df4d=sst.rolling_ret_lpsd(df4c, "Annual") 
    #加入扩展收益率下偏标准差
    df5=sst.expanding_ret_lpsd(df4d,fromdate)    

    return df5

if __name__=='__main__':
    df1i=calc_indicators(df1,'')

#==============================================================================
#==============================================================================
#==============================================================================

#==============================================================================

    