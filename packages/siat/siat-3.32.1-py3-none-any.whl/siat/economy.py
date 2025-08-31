# -*- coding: utf-8 -*-
"""
本模块功能：宏观经济基本面分析
所属工具包：证券投资分析工具SIAT 
SIAT：Security Investment Analysis Tool
创建日期：2020年8月31日
最新修订日期：2020年8月31日
作者：王德宏 (WANG Dehong, Peter)
作者单位：北京外国语大学国际商学院
版权所有：王德宏
用途限制：仅限研究与教学使用，不可商用！商用需要额外授权。
特别声明：作者不对使用本工具进行证券投资导致的任何损益负责！
"""
#==============================================================================
#关闭所有警告
import warnings; warnings.filterwarnings('ignore')
from siat.grafix import *
from siat.common import *
from siat.translate import *
#==============================================================================
if __name__=='__main__':
    start='2010-1-1'; end='2020-12-31'
    scope='China'; factor='Constant GDP'


def get_econ_factors(start,end,scope='China',factor='GDP'):
   """
   与函数get_econ_factors0的区别：
   1、将GNP替换为GNI
   2、将GNP Ratio替换为GNI Ration
   3、新增Currency Value，货币价值，衡量货币贬值速度
   """
   
   #替换GNP为GNI
   if factor == 'GNP':
       factor='GNI'
       ds=get_econ_factors0(start,end,scope,factor)
       return ds

   #替换GNP Ratio为GNI Ratio
   if factor in ['GNP Ratio','GNI Ratio']:
       ds_gni=get_econ_factors0(start,end,scope,'GNI')  
       if ds_gni is None: 
           print("  #Error(get_econ_factors): info not found for",scope,'GNI')
           return None
       
       import pandas as pd
       ds_gni1=pd.DataFrame(ds_gni['VALUE'])
       
       #ds_gdp=get_econ_factors0(start,end,scope,'GDP') 
       ds_gdp=get_econ_factors0(start,end,scope,'Current GDP') 
       if ds_gdp is None: return None
       
       ds_gdp1=pd.DataFrame(ds_gdp['VALUE'])
       
       ds1=pd.merge(ds_gni1,ds_gdp1,how='inner',left_index=True,right_index=True)
       ds1.dropna(inplace=True)
       ds1['VALUE']=ds1['VALUE_x']/ds1['VALUE_y']
       ds2=ds1.drop(['VALUE_x','VALUE_y'],axis=1)
       
       ds_gdp2=ds_gdp.drop('VALUE',axis=1)
       ds_gdp2['factor']='GNI Ratio'
       ds_gdp2['name']='GNI/GDP Ratio'
       ds_gdp2['symbol']='CUSTOMIZED'
       
       ds3=pd.merge(ds2,ds_gdp2,how='inner',left_index=True,right_index=True)
       
       return ds3

   #新增Currency Value
   if factor in ['Currency Value']:
       cv=get_econ_factors0(start,end,scope,'Constant CPI') 
       if cv is None: 
           print("  #Error(get_econ_factors): info not found for",scope,'Constant CPI')
           return None
       
       cv['CV']=(100.0/cv['VALUE'])*100.0
       cv1=cv.rename(columns={'VALUE':'Constant CPI'})
       cv2=cv1.rename(columns={'CV':'VALUE'})
       
       cv2['factor']='Currency Value'
       cv2['name']='Currency Purchasing Power Based on CPI'
       
       return cv2

   #其他正常情况
   df=get_econ_factors0(start,end,scope=scope,factor=factor)
    
   return df

#==============================================================================
def get_econ_factors0(start,end,scope='China',factor='GDP'):
   """
   【支持的因子种类(factor)】
   GDP, CPI, PPI,...

   【支持的国家/地区(scope)】
   US: 美国
   China: 中国
   Korea: 韩国
   Japan: 日本
   India: 印度

   【支持的取样频率(freq)】
   Annual: 年
   Quarterly: 季度
   Monthly: 月
   """
   s=fred_factor_codes() 

   #帮助1：国家列表
   if scope=='?':
       scopelist=list(set(list(s[s['factor']==factor]['scope'])))
       if len(scopelist)==0:
           print("  #Error(get_econ_factors0): no such economy factor,",factor)
       else:
           title="\n*** Supported scopes for factor, "+factor+':'
           print(title)
           linelen=0
           for i in range(len(scopelist)):
               print(scopelist[i],end='')
               linelen=linelen+len(scopelist[i])+2
               if (linelen >= len(title)-2): 
                   print(''); linelen=0
               else:
                   if (i+1) < len(scopelist): 
                       print(', ',end='')
                   else:
                       print('')
       return None
   
   #帮助2：经济指标
   if (scope != '?') and (factor=='?'):
       factorlist=list(set(list(s[s['scope']==scope]['factor'])))
       if len(factorlist)==0:
           print("  #Error(get_econ_factors0): no or unavailable country/region,",scope)
       else:
           title="\n*** Supported factors for scope, "+scope+':'
           print(title)
           linelen=0
           for i in range(len(factorlist)):
               print(factorlist[i],end='')
               linelen=linelen+len(factorlist[i])+2
               if (linelen >= len(title)-2): 
                   print(''); linelen=0
               else:
                   if (i+1) < len(factorlist): 
                       print(', ',end='')
                   else:
                       print('')
       return None

   #匹配：scope+factor+freq
   ss=s[s['scope'].isin([scope]) & s['factor'].isin([factor])]  
   #如果未找到匹配的模式，显示信息后返回
   if len(ss)==0:
        print("  #Error(get_econ_factors0): info are not available for",scope,factor)
        return None

   #取出对应的关键字symbol
   symbol=list(ss['symbol'])[0]

   #按照关键字抓取数据
   import pandas_datareader as web
   try:
        ds=web.get_data_fred(symbol,start,end)
   except:
        print("  #Error(get_econ_factors0): connection to data source failed!")        
        return None
   if len(ds)==0:
        print("  #Error(get_econ_factors0): server returned empty data!")        
        return None
   # 结果字段统一改名
   ds.columns=['VALUE'] 
   ds['scope']=list(ss['scope'])[0]
   ds['factor']=list(ss['factor'])[0]
   ds['freq']=list(ss['freq'])[0]
   ds['name']=list(ss['name'])[0]
   ds['symbol']=list(ss['symbol'])[0]
   ds['units']=list(ss['units'])[0]

   return ds

if __name__=='__main__':
    start='2010-1-1'; end='2020-8-31'
    scope='China'; factor='Real GDP Per Capita'
    
    ds1=get_econ_factors('2010-1-1','2020-8-31','China','GDP')
    ds2=get_econ_factors('2010-1-1','2020-8-31','China','Real GDP')
    ds3=get_econ_factors('2010-1-1','2020-8-31','India','Constant GDP')
    get_econ_factors('2010-1-1','2020-8-31','?','Constant GDP')
    get_econ_factors('2010-1-1','2020-8-31','China','?')
#==============================================================================
if __name__=='__main__':
    start='2010-1-1'; end='2022-12-31'
    scope='China'; factor='GDP'
    
    

def economy_trend0(ticker='China',start='L10Y',end='today',indicator='GDP', \
                  datatag=False,power=0, \
                  zeroline=False,yline=999,facecolor='papayawhip'):
    """
    ===========================================================================
    功能：绘制宏观经济指标，单线，可添加趋势线。
    主要参数：
    start：开始日期，格式YYYY-MM-DD
    end：结束日期
    scope：经济体名称，默认'China'，仅支持一部分经济体
    factor：经济指标，默认'GDP'
    datatag：是否在曲线上标记数据，默认False
    power：绘制趋势线的多项式阶数，默认0阶不绘制
    zeroline：是否绘制水平零线：默认False
    yline：绘制竖线的数值，默认999不绘制
    facecolor：背景颜色，默认小麦黄'papayawhip'    
    
    若需比较两个经济体的同一个指标，或同意经济体的两个指标，可用compare_economy
    """
    
    start,end=start_end_preprocess(start,end)
    #检查日期期间的合理性
    valid,_,_=check_period(start,end)
    if not valid:
        print('  Error(trend_economy): period not valid:',start,end)
        return

    scope=ticker; factor=indicator
    
    #获取指标
    ds=get_econ_factors(start,end,scope,factor)
    if (ds is None):
        print('  #Error(economy_trend): scope/economic factor not available:',scope,'/',factor)
        return

    #绘图
    ylabeltxt=ectranslate(factor)
    titletxt=ectranslate(list(ds['name'])[0])+'走势：'+ectranslate(scope)
    
    import datetime
    today=datetime.date.today()
    footnote='单位: '+list(ds['units'])[0]+', '+list(ds['freq'])[0]+ \
        '\n数据来源: OECD|IMF|WB|FRED, '+str(today)
    ds.dropna(inplace=True)

    if factor in ['GNP Ratio','GNI Ratio']:
        ylabeltxt='GNP(GNI)/GDP'
        if yline==999:
            yline=1 #绘制y=1的水平线
    if factor in ['Currency Value','Constant CPI']:
        ylabeltxt=ectranslate(factor)
        if yline==999:
            yline=100 #绘制y=100的水平线
    
    if yline !=999:
        zeroline=yline
    if power==0:
        power=3
        
    plot_line(ds,'VALUE',ectranslate(factor), \
              ylabeltxt=ylabeltxt,titletxt=titletxt,footnote=footnote,datatag=datatag, \
              power=power,zeroline=zeroline, \
              mark_top=False,mark_bottom=False,mark_end=False, \
              facecolor=facecolor)
    
    return ds


if __name__=='__main__':
    start='2010-1-1'; end='2020-8-31'
    scope='USA'; factor='Real GDP Per Capita'
    
    ds=economy_trend(start,end,scope='China',factor='GDP')
    ds=economy_trend(start,end,scope='Japan',factor='Real GDP')

#==============================================================================
if __name__=='__main__':
    #测试1
    tickers=['China','USA']
    measures='M2 GoB'
    measures='GNI'
    
    #测试2
    tickers=['China','USA']
    measures='Constant CPI'
    measures='Currency Value'
    
    
    
    fromdate='1999-12-1'
    todate='2022-4-1'
    power=0; twinx=False; loc1='upper left'; loc2='lower right'


def compare_economy(ticker,indicator='GDP',start='L10Y',end='today', \
                    power=0,twinx=False, \
                    yline=999, \
                    loc1='upper left',loc2='lower right',facecolor='papayawhip'):
    """
    ===========================================================================
    功能：对比绘制折线图：一个国家的两种测度，或两个国家的同一个测度。
    主要参数：
    tickers：经济体代码。如果是一个列表且内含两个代码，则认为希望比较两个国家的
    同一个测度指标。如果是一个列表但只内含一个国家代码或只是一个国家代码的字符串，
    则认为希望比较一个国家的两个测度指标。
    measures：经济指标。如果是一个列表且内含两个测度指标，则认为希望比较一个国家的
    两个测度指标。如果是一个列表但只内含一个测度指标或只是一个测度指标的字符串，
    则认为希望比较两个国家的同一个测度指标。
    如果两个判断互相矛盾，以第一个为准。
    start：开始日期，格式YYYY-MM-DD；end：结束日期。
    
    twinx：是否使用双轴绘图法，默认False
    yline：绘制纵轴竖线的数值，默认999不绘制
    loc1：图例1的位置，默认左上角'upper left'
    loc2：图例2的位置，默认右下角'lower right'
    facecolor：背景颜色，默认'papayawhip'
    """
    start,end=start_end_preprocess(start,end)
    fromdate=start; todate=end
    tickers=ticker; measures=indicator
    
    DEBUG=False
    if DEBUG:
        print("DEBUG: tickers =",tickers,"\b, measures =",measures)
    
    #检查日期期间的合理性
    valid,_,_=check_period(fromdate,todate)
    if not valid:
        print('  #Error(compare_economy): period not valid:',fromdate,todate)
        return
    
    #判断国家代码个数
    #如果tickers只是一个字符串
    security_num = 0
    if isinstance(tickers,str): 
        security_num = 1
        ticker1 = tickers
    #如果tickers是一个列表
    if isinstance(tickers,list): 
        security_num = len(tickers)
        if security_num == 0:
            print("  #Error(compare_economy): lack of country(s) for comparison")
            return
        if security_num >= 1: ticker1 = tickers[0]
        if security_num >= 2: ticker2 = tickers[1]
            
    #判断测度个数
    #如果measures只是一个字符串
    measure_num = 0
    if isinstance(measures,str): 
        measure_num = 1
        measure1 = measures
    #如果measures是一个列表
    if isinstance(measures,list): 
        measure_num = len(measures)
        if measure_num == 0:
            print("  #Error(compare_economy): lack of measure(s)")
            return
        if measure_num >= 1: measure1 = measures[0]
        if measure_num >= 2: measure2 = measures[1]

    import datetime; today=datetime.date.today()
    lang=check_language()
    if lang == 'English':
        source_txt='\nSource: OECD|IMF|WB|FRED, '
        addstr_txt='Starting date as benchmark 100\n'
        unit_txt='Notes: '
    else:
        source_txt='\n数据来源: OECD|IMF|WB|FRED, '
        #addstr_txt='开始时点作为基数100\n'
        addstr_txt=''
        unit_txt='单位: '
    
    #是否单一国家代码+两个测度指标
    if (security_num == 1) and (measure_num >= 2):
        #国家ticker1：抓取经济指标measure1
        result,measure1new=separate_measure(measure1,'Constant')
        """
        df1=get_econ_factors(fromdate,todate,ticker1,measure1new)
        """
        df1=get_econ_factors(fromdate,todate,ticker1,measure1)
        
        if df1 is None: return None, None
        
        #求GoB增速指标
        if result:
            df1.rename(columns={'VALUE':'VALUE0'}, inplace = True)
            comparend=df1.head(1)['VALUE0'][0]
            df1['VALUE']=df1['VALUE0']/comparend*100

        #国家ticker1：抓取经济指标measure2
        result,measure2new=separate_measure(measure2,'Constant')
        """
        df2=get_econ_factors(fromdate,todate,ticker1,measure2new)
        """
        df2=get_econ_factors(fromdate,todate,ticker1,measure2)
        
        if df2 is None: return None, None
        
        #求GoB增速指标
        if result:
            df2.rename(columns={'VALUE':'VALUE0'}, inplace = True)
            comparend=df2.head(1)['VALUE0'][0]
            df2['VALUE']=df2['VALUE0']/comparend*100
        
        #绘制单个国家的双指标对比图
        ylabeltxt=''
        titletxt=ectranslate(measure1)+' vs '+ectranslate(measure2)+ \
            '\n（'+ectranslate(ticker1)+'）'
        
        if result:
            addstr=addstr_txt
        else:
            addstr=''
        footnote=addstr+ectranslate(measure1)+': '+list(df1['units'])[0]+', '+list(df1['freq'])[0]+ \
            '\n'+ectranslate(measure2)+': '+list(df2['units'])[0]+', '+list(df2['freq'])[0]+ \
            source_txt+str(today)

        if lang == 'Chinese':
            """
            plot_line2(df1,ectranslate(ticker1),'VALUE',ectranslate(measure1), \
                   df2,ectranslate(ticker1),'VALUE',ectranslate(measure2), \
                   ylabeltxt,titletxt,footnote, \
                   power=power,twinx=twinx,loc1=loc1,loc2=loc2)    
            """
            plot_line2(df1,ticker1,'VALUE',ectranslate(measure1), \
                   df2,ticker1,'VALUE',ectranslate(measure2), \
                   ylabeltxt,titletxt,footnote, \
                   power=power,twinx=twinx,loc1=loc1,loc2=loc2,facecolor=facecolor)   
        else:
            plot_line2(df1,ticker1,'VALUE',measure1, \
                       df2,ticker1,'VALUE',measure2, \
                   ylabeltxt,titletxt,footnote, \
                   power=power,twinx=twinx,loc1=loc1,loc2=loc2,facecolor=facecolor)    
        
    elif (security_num >= 2) and (measure_num >= 1):
        #双国家+单个测度指标        
        #国家ticker1：抓取经济指标measure1
        result,measure1new=separate_measure(measure1,'Constant')
        """
        df1=get_econ_factors(fromdate,todate,ticker1,measure1new)
        """
        df1=get_econ_factors(fromdate,todate,ticker1,measure1)
        
        if df1 is None: return None, None
        
        #求GoB增速指标
        """
        if result:
            df1.rename(columns={'VALUE':'VALUE0'}, inplace = True)
            comparend=df1.head(1)['VALUE0'][0]
            df1['VALUE']=df1['VALUE0']/comparend*100
        """
        
        #国家ticker2：抓取经济指标measure1
        """
        df2=get_econ_factors(fromdate,todate,ticker2,measure1new)
        """
        df2=get_econ_factors(fromdate,todate,ticker2,measure1)
        
        if df2 is None: return None, None
        
        #求GoB增速指标
        """
        if result:
            df2.rename(columns={'VALUE':'VALUE0'}, inplace = True)
            comparend=df2.head(1)['VALUE0'][0]
            df2['VALUE']=df2['VALUE0']/comparend*100
        """
        
        #绘制双国家单指标对比图
        ylabeltxt=ectranslate(measure1)
        #这里的GNP指标实际上是GNP vs GDP的百分比
        #yline=999   #默认不绘制水平线
        if measure1 in ['GNP Ratio','GNI Ratio']:
            ylabeltxt='GNP(GNI)/GDP'
            if yline==999:
                yline=1 #绘制y=1的水平线
        if measure1 in ['Currency Value','Constant CPI']:
            ylabeltxt=ectranslate(measure1)
            if yline==999:
                yline=100 #绘制y=100的水平线
        
        if lang == 'Chinese':
            titletxt=ectranslate(list(df1['name'])[0])+'走势对比：'+ \
                '\n'+ectranslate(ticker1)+' vs '+ectranslate(ticker2)
        else:
            titletxt=list(df1['name'])[0]+', Trend Comparison'+ \
                '\n'+ticker1+' vs '+ticker2
            
        if result:
            addstr=addstr_txt
        else:
            addstr=''
        footnote=addstr+unit_txt+list(df1['units'])[0]+', '+list(df1['freq'])[0]+ \
            source_txt+str(today)
        
        if lang == 'Chinese':
            """
            plot_line2(df1,ectranslate(ticker1),'VALUE',ectranslate(measure1), \
                   df2,ectranslate(ticker2),'VALUE',ectranslate(measure1), \
                   ylabeltxt,titletxt,footnote, \
                   power=power,twinx=twinx,yline=yline,loc1=loc1,loc2=loc2)  
            """
            plot_line2(df1,ticker1,'VALUE',measure1, \
                   df2,ticker2,'VALUE',measure1, \
                   ylabeltxt,titletxt,footnote, \
                   power=power,twinx=twinx,yline=yline,loc1=loc1,loc2=loc2,facecolor=facecolor)                  
        else:
            plot_line2(df1,ticker1,'VALUE',measure1, \
                       df2,ticker2,'VALUE',measure1, \
                    ylabeltxt,titletxt,footnote, \
                    power=power,twinx=twinx,yline=yline,loc1=loc1,loc2=loc2,facecolor=facecolor)  
            
    else:
        print("  #Error(compare_economy): no idea on what to compare")
        return None,None

    return df1,df2

if __name__ =="__main__":
    tickers=['China','India']
    measures='GDP'
    fromdate='2010-1-1'
    todate='2020-8-31'
    
    df=compare_economy(tickers,measures,fromdate,todate)
    df=compare_economy(tickers,measures,fromdate,todate,twinx=True)

    df=compare_economy(tickers,'GDP Per Capita',fromdate,todate)
    df=compare_economy(tickers,'GDP Per Capita',fromdate,todate,twinx=True)

    df=compare_economy('India',['Real GDP','Real GDP Per Capita'],fromdate,todate,twinx=True)
    df=compare_economy('Japan',['Real GDP','Real GDP Per Capita'],fromdate,todate,twinx=True)
    df=compare_economy('Israel',['Real GDP','Real GDP Per Capita'],fromdate,todate,twinx=True)

#==============================================================================

def economy_trend(ticker='China',indicator='GDP',start='L10Y',end='today', \
                  power=0,twinx=False, \
                  attention_value=999,datatag=False,zeroline=False, \
                  loc1='upper left',loc2='lower right',facecolor='papayawhip'):
    """
    ===========================================================================
    功能：宏观经济指标趋势分析，支持单个国家单指标、单个国家双指标、两个国家单指标。
    主要参数：
    ticker：经济体名称，默认'China'。如果是列表且内含两个经济体名称，则比较两个国家的
    同一个指标
    indicator：宏观经济指标，默认'GDP'。如果ticker为一个经济体，而indicator为列表且
    有两个指标，则比较一个国家的两个指标。如果两个判断互相矛盾，以第一个为准
    start：开始日期，格式YYYY-MM-DD，支持简易格式，默认'L10Y;；end：结束日期
    power：趋势线的多项式阶数，默认0不绘制
    twinx：是否使用双轴绘图法，默认False，仅在两个国家或两个指标时有效
    yline：绘制纵轴水平线的数值，默认999不绘制。相当于attention_value，但仅一个数值
    datatag：是否绘制折线各点数值，默认False
    zeroline：是否绘制水平零线，默认False
    loc1：图例1的位置，默认左上角'upper left'，仅用于双国家或双指标情形
    loc2：图例2的位置，默认右下角'lower right'，仅用于双国家或双指标情形
    facecolor：背景颜色，默认'papayawhip'
    
    套壳函数：，economy_trend0
    """
    # 判断经济体个数：优先
    ticker_num=1
    if isinstance(ticker,list) and len(ticker)>=2:
        ticker_num=2
        
    # 判断指标个数：次优先
    indicator_num=1
    if isinstance(indicator,list) and len(indicator)>=2:
        indicator_num=2
        
    if ticker_num==2 or indicator_num==2:
        df=compare_economy(ticker=ticker,indicator=indicator, \
                           start=start,end=end, \
                           power=power,twinx=twinx, \
                           yline=attention_value, \
                           loc1=loc1,loc2=loc2,facecolor=facecolor)
    else:
        df=economy_trend0(ticker=ticker,start=start,end=end, \
                          indicator=indicator, \
                          datatag=datatag,power=power, \
                          zeroline=zeroline,yline=attention_value, \
                          facecolor=facecolor)
    
    return df
    
#==============================================================================
if __name__ =="__main__":
    measure='M2 MoM'
    measure_type='MoM'
    separate_measure(measure,measure_type)
    
    measure='M2'
    measure_type='MoM'
    separate_measure(measure,measure_type)

def separate_measure(measure,measure_type):
    """
    功能：若measure字符串含有子串measure_type，则返回True，并分离出第一个空格前的子串返回
    否则返回False和原measure
    例如：对于"M2 MoM"返回True和"M2"
    """
    if measure_type in measure:
        pos=measure.index(' ')
        new_measure=measure[pos+1:]
        return True,new_measure
    
    return False,measure
    

#==============================================================================
def econ_fin_depth(fromdate,todate,scope,power=0,graph=True):
    """
    功能：经济的金融化深度，一个国家
    """
    #检查日期期间的合理性
    valid,_,_=check_period(fromdate,todate)
    if not valid:
        print('  #Error(econ_fin_depth): period not valid:',fromdate,todate)
        return None   
    
    #获取GDP，按季度，本币
    gdp_qtr=get_econ_factors(fromdate,todate,scope,'GDP')
    if gdp_qtr is None:
        print(f"  #Error(econ_fin_depth): no GDP info found for {scope}")
        return None
    
    gdp_qtr['date']=gdp_qtr.index.date
    datecvt=lambda x: str(x)[0:4]
    gdp_qtr['date_str']=gdp_qtr['date'].apply(datecvt)

    import numpy as np
    gdp_annual=gdp_qtr.groupby(['date_str'])['VALUE'].agg(['count',np.sum])
    gdp_annual2=gdp_annual[gdp_annual['count']==4]

    #获取M2，按月，本币
    m2_mth=get_econ_factors(fromdate,todate,scope,'M2')
    if m2_mth is None:
        print(f"  #Error(econ_fin_depth): no M2 info found for {scope}")
        return None
    
    m2_mth['date']=m2_mth.index.date
    datecvt=lambda x: str(x)[0:4]
    m2_mth['date_str']=m2_mth['date'].apply(datecvt)

    m2_annual=m2_mth.groupby(['date_str'])['VALUE'].agg(['count',np.sum])
    m2_annual2=m2_annual[m2_annual['count']==12]

    #合并
    import pandas as pd
    m2_gdp=pd.merge(m2_annual2,gdp_annual2,on='date_str')
    m2_gdp.dropna(inplace=True)
    m2_gdp['m2/gdp']=m2_gdp['sum_x']/m2_gdp['sum_y']
    
    df=m2_gdp[['m2/gdp']]

    #绘图
    if not graph: return df
    colname='m2/gdp'
    collabel="经济的金融深度"
    ylabeltxt="M2/GDP比例"
    titletxt='经济金融深度走势：'+ectranslate(scope)
    footnote="数据来源: OECD|IMF|WB|FRED"
    plot_line(df,colname,collabel,ylabeltxt,titletxt,footnote,power=power)

    return df

if __name__=='__main__':
    fromdate='2000-1-1'; todate='2020-8-31'
    scope="China"
    cn=econ_fin_depth(fromdate,todate,scope,power=4)
    print(min(cn['m2/gdp']),max(cn['m2/gdp']))
    print(cn)
    jp=econ_fin_depth(fromdate,todate,'Japan',power=0)    
    us=econ_fin_depth(fromdate,todate,'USA',power=0)
    kr=econ_fin_depth(fromdate,todate,'Korea',power=0)

#==============================================================================
def compare_efd(fromdate,todate,scopelist,power=0):
    """
    功能：比较经济的金融化深度，两个国家
    """
    #检查日期期间的合理性
    valid,_,_=check_period(fromdate,todate)
    if not valid:
        print('  #Error(econ_fin_depth): period not valid:',fromdate,todate)
        return None,None   

    #检查国家列表
    if isinstance(scopelist,list): 
        if len(scopelist) < 2:
            print("  #Error(compare_efd): need a list with 2 countries",scopelist)
            return None,None
        scope1 = scopelist[0]; scope2 = scopelist[1]
    else:
        print("  #Error(compare_efd): need a list with 2 countries",scopelist)
        return None,None
 
    #计算scope1/2的efd。美国的M2指标单位是Billions Dollars
    df1=econ_fin_depth(fromdate,todate,scope1,graph=False)
    if df1 is None:
        print(f"  #Error(compare_efd): no M2/GDP info found for {scope1}")
        return None,None
    
    if scope1=='USA':
        df1['m2/gdp']=df1['m2/gdp']*1000000000.0
        
    df2=econ_fin_depth(fromdate,todate,scope2,graph=False)
    if df2 is None:
        print(f"  #Error(compare_efd): no M2/GDP info found for {scope2}")
        return None,None

    if scope2=='USA':
        df2['m2/gdp']=df2['m2/gdp']*1000000000.0
    
    #绘图
    ticker1=scope1; ticker2=scope2
    colname1='m2/gdp'; colname2='m2/gdp'
    label1="M2/GDP"; label2="M2/GDP"
    ylabeltxt="M2/GDP比例"
    titletxt='经济金融深度对比：'+ectranslate(scope1)+' vs '+ectranslate(scope2)
    
    import datetime
    today=datetime.date.today()
    footnote="数据来源：IMF/FRED，"+str(today)    
    plot_line2(df1,ectranslate(ticker1),colname1,label1, \
               df2,ectranslate(ticker2),colname2,label2, \
               ylabeltxt,titletxt,footnote, \
               power=power)
        
    return df1,df2

if __name__=='__main__':
    fromdate='2000-1-1'; todate='2020-8-31'
    scopelist=["China","Japan"]
    power=4
    cn,us=compare_efd(fromdate,todate,['China','USA'])
    cn,jp=compare_efd(fromdate,todate,['China','Japan'])
    cn,kr=compare_efd(fromdate,todate,['China','Korea'])

#==============================================================================

def efd_trend(ticker='China',start='L30Y',end='today',power=0):
    """
    ===========================================================================
    功能：基于M2/GDP比例分析经济的金融化深度，支持单个经济体和双经济体对比
    参数：
    ticker：经济体名称，默认'China',可为双经济体列表
    start：开始日期，格式YYYY-MM-DD，支持简易格式，默认'L30Y'
    end：截止日期，默认'today'
    power：趋势线的多项式阶数，默认0不绘制
    """
    # 处理日期
    fromdate,todate=start_end_preprocess(start,end)
    
    ticker_num=1
    if isinstance(ticker,list) and len(ticker) >= 2:
        ticker_num=2
        
    if ticker_num==1:
        df=econ_fin_depth(fromdate=fromdate,todate=todate,scope=ticker,power=power)
    else:
        df=compare_efd(fromdate=fromdate,todate=todate,scopelist=ticker,power=power)
    
    return df


#==============================================================================

def economy_security(scope,fromdate,todate,econ_factor,sec_ticker,loc1='upper left',loc2='lower right'):
    """
    功能：比较宏观经济与证券市场之间的关联关系
    scope: 国家/地区
    econ_factor: 例如GDP
    sec_ticker: 例如标普500指数、道琼斯指数、上证综合指数
    输出： df
    """
    #检查日期期间的合理性
    valid,_,_=check_period(fromdate,todate)
    if not valid:
        print('  Error(economy_security): period not valid:',fromdate,todate)
        return None,None

    #获得econ_factor
    econ=get_econ_factors(fromdate,todate,scope,econ_factor)
    if econ is None:
        print('  Error(economy_security): scope/economic factor not available:',scope,econ_factor)
        return None,None
    econ_growth='Growth %'
    econ[econ_growth]=econ['VALUE'].pct_change()*100.0
    
    #获得sec_ticker行情
    import siat.security_prices as ssp
    sec=ssp.get_price(sec_ticker,fromdate,todate)
    if sec is None:
        print('  Error(economy_security): ticker info not available:',sec_ticker)
        return None,None    

    #绘图1： 直接指标，双轴
    econ_min1,econ_max1=get_df_period(econ)    
    sec_min1,sec_max1=get_df_period(sec)
    min1=max(econ_min1,sec_min1)
    max1=min(econ_max1,sec_max1)
    econ1=set_df_period(econ,min1,max1)
    sec1=set_df_period(sec,min1,max1)    
    
    df1=econ1; ticker1=econ_factor; colname1='VALUE'; label1=econ_factor
    df2=sec1; ticker2=sec_ticker; colname2='Close'; label2=sec_ticker
    ylabeltxt=''
    titletxt=ectranslate(scope)+": 宏观经济与证券市场的关系"
    footnote="数据来源: FRED|Yahoo Finance"
    plot_line2(df1,ectranslate(ticker1),colname1,label1, \
               df2,ectranslate(ticker2),colname2,label2, \
               ylabeltxt,titletxt,footnote, \
               power=0,twinx=True,loc1=loc1,loc2=loc2)

    #绘图2： 增长指标，双轴
    econ2=econ.dropna()
    econ_min1,econ_max1=get_df_period(econ2)    
    sec_min1,sec_max1=get_df_period(sec)
    min1=max(econ_min1,sec_min1)
    max1=min(econ_max1,sec_max1)
    econ3=set_df_period(econ,min1,max1)    
    sec3=set_df_period(sec,min1,max1)    
    df1=econ3; df2=sec3
    
    colname1=econ_growth
    #label1=econ_growth
    label1="增长率%"
    titletxt=ectranslate(scope)+": 经济增长与证券市场的关系"
    plot_line2(df1,ectranslate(ticker1),colname1,label1, \
               df2,ectranslate(ticker2),colname2,label2, \
               ylabeltxt,titletxt,footnote, \
               power=0,twinx=True,loc1=loc1,loc2=loc2)
    return econ,sec

if __name__=='__main__':
    fromdate='2010-1-1'; todate='2019-12-31'
    scope='China'; econ_factor='GDP'; sec_ticker='000001.SS'

    df_cn1=economy_security('China','1995-1-1','2019-12-31','GDP Per Capita','000001.SS')    
    df_cn2=economy_security('China','1995-1-1','2019-12-31','Constant Price GDP','000001.SS')
    df_us1=economy_security('USA','1980-1-1','2019-12-31','GDP','^DJI')
    df_us2=economy_security('USA','1980-1-1','2019-12-31','GDP','^GSPC')
#==============================================================================
def get_df_period(df):
    """
    功能： 获得df中日期索引的最小最大值
    """
    df_min=min(df.index)
    df_max=max(df.index)
    return df_min,df_max

if __name__=='__main__':
    import siat.security_prices as ssp
    df=ssp.get_price('AAPL','2020-1-1','2020-1-31')
    get_df_period(df)
    

#==============================================================================
#==============================================================================
#==============================================================================

def fred_factor_codes():
   import pandas as pd
   s=pd.DataFrame([
        # GDP：年度指标，美元现价，未经季节性调整。未扣除通胀因素，含有汇率变化因素
        ['China','Current GDP','Annual','Gross Domestic Product','MKTGDPCNA646NWDB','Current USD, Not Seasonally Adjusted'],
        ['USA','Current GDP','Annual','Gross Domestic Product','MKTGDPUSA646NWDB','Current USD, Not Seasonally Adjusted'],
        ['Japan','Current GDP','Annual','Gross Domestic Product','MKTGDPJPA646NWDB','Current USD, Not Seasonally Adjusted'],
        ['India','Current GDP','Annual','Gross Domestic Product','MKTGDPINA646NWDB','Current USD, Not Seasonally Adjusted'],
        ['Korea','Current GDP','Annual','Gross Domestic Product','MKTGDPKRA646NWDB','Current USD, Not Seasonally Adjusted'],
        ['Russia','Current GDP','Annual','Gross Domestic Product','MKTGDPRUA646NWDB','Current USD, Not Seasonally Adjusted'],
        ['Singapore','Current GDP','Annual','Gross Domestic Product','MKTGDPSGA646NWDB','Current USD, Not Seasonally Adjusted'],
        ['Malaysia','Current GDP','Annual','Gross Domestic Product','MKTGDPMYA646NWDB','Current USD, Not Seasonally Adjusted'],
        ['Indonesia','Current GDP','Annual','Gross Domestic Product','MKTGDPIDA646NWDB','Current USD, Not Seasonally Adjusted'],
        ['Vietnam','Current GDP','Annual','Gross Domestic Product','MKTGDPVNA646NWDB','Current USD, Not Seasonally Adjusted'],
        ['Thailand','Current GDP','Annual','Gross Domestic Product','MKTGDPTHA646NWDB','Current USD, Not Seasonally Adjusted'],
        ['Australia','Current GDP','Annual','Gross Domestic Product','MKTGDPAUA646NWDB','Current USD, Not Seasonally Adjusted'],
        ['France','Current GDP','Annual','Gross Domestic Product','MKTGDPFRA646NWDB','Current USD, Not Seasonally Adjusted'],
        ['Germany','Current GDP','Annual','Gross Domestic Product','MKTGDPDEA646NWDB','Current USD, Not Seasonally Adjusted'],
        ['UK','Current GDP','Annual','Gross Domestic Product','MKTGDPGBA646NWDB','Current USD, Not Seasonally Adjusted'],
        ['Israel','Current GDP','Annual','Gross Domestic Product','MKTGDPILA646NWDB','Current USD, Not Seasonally Adjusted'],
        ['Italy','Current GDP','Annual','Gross Domestic Product','MKTGDPITA646NWDB','Current USD, Not Seasonally Adjusted'],
        ['Cambodia','Current GDP','Annual','Gross Domestic Product','MKTGDPKHA646NWDB','Current USD, Not Seasonally Adjusted'],
        
        # Real GDP at Constant National Prices：不变价格GDP，年度指标，百万元，2017年基准，未经季节性调整。扣除通胀因素，扣除汇率变化因素
        ['India','Constant GDP','Annual','Real GDP at Constant National Prices','RGDPNAINA666NRUG','2017 USD Millions, Not Seasonally Adjusted'],
        ['China','Constant GDP','Annual','Real GDP at Constant National Prices','RGDPNACNA666NRUG','2017 USD Millions, Not Seasonally Adjusted'],
        ['Japan','Constant GDP','Annual','Real GDP at Constant National Prices','RGDPNAJPA666NRUG','2017 USD Millions, Not Seasonally Adjusted'],
        ['Korea','Constant GDP','Annual','Real GDP at Constant National Prices','RGDPNAKRA666NRUG','2017 USD Millions, Not Seasonally Adjusted'],
        ['Thailand','Constant GDP','Annual','Real GDP at Constant National Prices','RGDPNATHA666NRUG','2017 USD Millions, Not Seasonally Adjusted'],
        ['Vietnam','Constant GDP','Annual','Real GDP at Constant National Prices','RGDPNAVNA666NRUG','2017 USD Millions, Not Seasonally Adjusted'],
        ['Cambodia','Constant GDP','Annual','Real GDP at Constant National Prices','RGDPNAKHA666NRUG','2017 USD Millions, Not Seasonally Adjusted'],
        ['Hong Kong','Constant GDP','Annual','Real GDP at Constant National Prices','RGDPNAHKA666NRUG','2017 USD Millions, Not Seasonally Adjusted'],
        ['Singapore','Constant GDP','Annual','Real GDP at Constant National Prices','RGDPNASGA666NRUG','2017 USD Millions, Not Seasonally Adjusted'],
        ['Malaysia','Constant GDP','Annual','Real GDP at Constant National Prices','RGDPNAMYA666NRUG','2017 USD Millions, Not Seasonally Adjusted'],
        ['Indonesia','Constant GDP','Annual','Real GDP at Constant National Prices','RGDPNAIDA666NRUG','2017 USD Millions, Not Seasonally Adjusted'],
        ['USA','Constant GDP','Annual','Real GDP at Constant National Prices','RGDPNAUSA666NRUG','2017 USD Millions, Not Seasonally Adjusted'],
        ['UK','Constant GDP','Annual','Real GDP at Constant National Prices','RGDPNAGBA666NRUG','2017 USD Millions, Not Seasonally Adjusted'],
        ['France','Constant GDP','Annual','Real GDP at Constant National Prices','RGDPNAFRA666NRUG','2017 USD Millions, Not Seasonally Adjusted'],
        ['Germany','Constant GDP','Annual','Real GDP at Constant National Prices','RGDPNADEA666NRUG','2017 USD Millions, Not Seasonally Adjusted'],
        ['Italy','Constant GDP','Annual','Real GDP at Constant National Prices','RGDPNAITA666NRUG','2017 USD Millions, Not Seasonally Adjusted'],
        ['Israel','Constant GDP','Annual','Real GDP at Constant National Prices','RGDPNAILA666NRUG','2017 USD Millions, Not Seasonally Adjusted'],
        ['Russia','Constant GDP','Annual','Real GDP at Constant National Prices','RGDPNARUA666NRUG','2017 USD Millions, Not Seasonally Adjusted'],
        ['Australia','Constant GDP','Annual','Real GDP at Constant National Prices','RGDPNAAUA666NRUG','2017 USD Millions, Not Seasonally Adjusted'],
        
        # Current Price GDP：季度指标，本币现价，经过季节性调整。未考虑通货膨胀因素，不受汇率变化影响
        # 美国的季节性调整调整方法：X-12 Arima
        # 季节性调整调整的思路：从当前的变化综扣除过去数年的平均变动，为了回答问题：目前的变化是纯粹的季节性现象，还是说明目前的变化是不寻常的。
        ['China','GDP','Quarterly','Current Price Gross Domestic Product','CHNGDPNQDSMEI','Local Currency, Seasonally Adjusted'],
        ['Japan','GDP','Quarterly','Current Price Gross Domestic Product','JPNGDPNQDSMEI','Local Currency, Seasonally Adjusted'],
        ['USA','GDP','Quarterly','Current Price Gross Domestic Product','USAGDPNQDSMEI','Local Currency, Seasonally Adjusted'],
        ['Korea','GDP','Quarterly','Current Price Gross Domestic Product','KORGDPNQDSMEI','Local Currency, Seasonally Adjusted'],
        ['Russia','GDP','Quarterly','Current Price Gross Domestic Product','RUSGDPNQDSMEI','Local Currency, Seasonally Adjusted'],
        ['India','GDP','Quarterly','Current Price Gross Domestic Product','INDGDPNQDSMEI','Local Currency, Seasonally Adjusted'],
        ['France','GDP','Quarterly','Current Price Gross Domestic Product','FRAGDPNQDSMEI','Local Currency, Seasonally Adjusted'],
        ['Germany','GDP','Quarterly','Current Price Gross Domestic Product','DEUGDPNQDSMEI','Local Currency, Seasonally Adjusted'],
        ['UK','GDP','Quarterly','Current Price Gross Domestic Product','GBRGDPNQDSMEI','Local Currency, Seasonally Adjusted'],
        ['Australia','GDP','Quarterly','Current Price Gross Domestic Product','AUSGDPNQDSMEI','Local Currency, Seasonally Adjusted'],
        
        # Ratio of GNP to GDP：年度指标，百分比%，未经季节性调整
        ['China','GNP Ratio','Annual','Ratio of GNP to GDP','GNPGDPCNA156NUPN','Percent, Not Seasonally Adjusted'],
        ['USA','GNP Ratio','Annual','Ratio of GNP to GDP','GNPGDPUSA156NUPN','Percent, Not Seasonally Adjusted'],
        ['Japan','GNP Ratio','Annual','Ratio of GNP to GDP','GNPGDPJPA156NUPN','Percent, Not Seasonally Adjusted'],
        
        # GDP Per Capita：人均GDP，年度指标，美元现价，未经季节性调整。未扣除通胀因素，受到汇率变化影响
        ['China','GDP Per Capita','Annual','Gross Domestic Product Per Capita','PCAGDPCNA646NWDB','Current USD, Not Seasonally Adjusted'],
        ['Japan','GDP Per Capita','Annual','Gross Domestic Product Per Capita','PCAGDPJPA646NWDB','Current USD, Not Seasonally Adjusted'],
        ['USA','GDP Per Capita','Annual','Gross Domestic Product Per Capita','PCAGDPUSA646NWDB','Current USD, Not Seasonally Adjusted'],
        ['Korea','GDP Per Capita','Annual','Gross Domestic Product Per Capita','PCAGDPKRA646NWDB','Current USD, Not Seasonally Adjusted'],
        ['India','GDP Per Capita','Annual','Gross Domestic Product Per Capita','PCAGDPINA646NWDB','Current USD, Not Seasonally Adjusted'],
        ['Singapore','GDP Per Capita','Annual','Gross Domestic Product Per Capita','PCAGDPSGA646NWDB','Current USD, Not Seasonally Adjusted'],
        ['Malaysia','GDP Per Capita','Annual','Gross Domestic Product Per Capita','PCAGDPMYA646NWDB','Current USD, Not Seasonally Adjusted'],
        ['Indonesia','GDP Per Capita','Annual','Gross Domestic Product Per Capita','PCAGDPIDA646NWDB','Current USD, Not Seasonally Adjusted'],
        ['Vietnam','GDP Per Capita','Annual','Gross Domestic Product Per Capita','PCAGDPVNA646NWDB','Current USD, Not Seasonally Adjusted'],
        ['Thailand','GDP Per Capita','Annual','Gross Domestic Product Per Capita','PCAGDPTHA646NWDB','Current USD, Not Seasonally Adjusted'],
        ['Cambodia','GDP Per Capita','Annual','Gross Domestic Product Per Capita','PCAGDPKHA646NWDB','Current USD, Not Seasonally Adjusted'],
        
        # Constant GDP per capita：不变价格人均GDP，2010年美元基准，未经季节性调整。扣除通胀因素和汇率变化因素
        ['China','Constant Price GDP Per Capita','Annual','Constant Price GDP Per Capita','NYGDPPCAPKDCHN','2010 USD, Not Seasonally Adjusted'],
        ['USA','Constant Price GDP Per Capita','Annual','Constant Price GDP Per Capita','NYGDPPCAPKDUSA','2010 USD, Not Seasonally Adjusted'],
        ['Japan','Constant Price GDP Per Capita','Annual','Constant Price GDP Per Capita','NYGDPPCAPKDJPN','2010 USD, Not Seasonally Adjusted'],
        ['Russia','Constant Price GDP Per Capita','Annual','Constant Price GDP Per Capita','NYGDPPCAPKDRUS','2010 USD, Not Seasonally Adjusted'],
        ['France','Constant Price GDP Per Capita','Annual','Constant Price GDP Per Capita','NYGDPPCAPKDFRA','2010 USD, Not Seasonally Adjusted'],
        ['Germany','Constant Price GDP Per Capita','Annual','Constant Price GDP Per Capita','NYGDPPCAPKDDEU','2010 USD, Not Seasonally Adjusted'],
        ['Italy','Constant Price GDP Per Capita','Annual','Constant Price GDP Per Capita','NYGDPPCAPKDITA','2010 USD, Not Seasonally Adjusted'],
        ['Singapore','Constant Price GDP Per Capita','Annual','Constant Price GDP Per Capita','NYGDPPCAPKDSGP','2010 USD, Not Seasonally Adjusted'],
        ['Malaysia','Constant Price GDP Per Capita','Annual','Constant Price GDP Per Capita','NYGDPPCAPKDMYS','2010 USD, Not Seasonally Adjusted'],
        ['Indonesia','Constant Price GDP Per Capita','Annual','Constant Price GDP Per Capita','NYGDPPCAPKDIDN','2010 USD, Not Seasonally Adjusted'],
        ['India','Constant Price GDP Per Capita','Annual','Constant Price GDP Per Capita','NYGDPPCAPKDIND','2010 USD, Not Seasonally Adjusted'],
        
        # CPI相对值%：月度数据，以2015年为基准值100，未经季节性调整
        ['China','Constant CPI','Monthly','Consumer Price Index: All Items','CHNCPIALLMINMEI','Index 2015=100, Not Seasonally Adjusted'],
        ['USA','Constant CPI','Monthly','Consumer Price Index: All Items','USACPIALLMINMEI','Index 2015=100, Not Seasonally Adjusted'],
        ['Japan','Constant CPI','Monthly','Consumer Price Index: All Items','JPNCPIALLMINMEI','Index 2015=100, Not Seasonally Adjusted'],
        ['Korea','Constant CPI','Monthly','Consumer Price Index: All Items','KORCPIALLMINMEI','Index 2015=100, Not Seasonally Adjusted'],
        ['India','Constant CPI','Monthly','Consumer Price Index: All Items','INDCPIALLMINMEI','Index 2015=100, Not Seasonally Adjusted'],
        ['France','Constant CPI','Monthly','Consumer Price Index: All Items','FRACPIALLMINMEI','Index 2015=100, Not Seasonally Adjusted'],
        ['Germany','Constant CPI','Monthly','Consumer Price Index: All Items','DEUCPIALLMINMEI','Index 2015=100, Not Seasonally Adjusted'],
        ['Australia','Constant CPI','Monthly','Consumer Price Index: All Items','AUSCPIALLMINMEI','Index 2015=100, Not Seasonally Adjusted'],
        ['UK','Constant CPI','Monthly','Consumer Price Index: All Items','GBRCPIALLMINMEI','Index 2015=100, Not Seasonally Adjusted'],
        ['Italy','Constant CPI','Monthly','Consumer Price Index: All Items','ITACPIALLMINMEI','Index 2015=100, Not Seasonally Adjusted'],
        ['Spain','Constant CPI','Monthly','Consumer Price Index: All Items','ESPCPIALLMINMEI','Index 2015=100, Not Seasonally Adjusted'],
        ['Russia','Constant CPI','Monthly','Consumer Price Index: All Items','RUSCPIALLMINMEI','Index 2015=100, Not Seasonally Adjusted'],
        ['Indonesia','Constant CPI','Monthly','Consumer Price Index: All Items','IDNCPIALLMINMEI','Index 2015=100, Not Seasonally Adjusted'],
        ['Israel','Constant CPI','Monthly','Consumer Price Index: All Items','ISRCPIALLMINMEI','Index 2015=100, Not Seasonally Adjusted'],
        

        # CPI环比%：月度数据，未经季节性调整
        ['USA','MoM CPI','Monthly','Consumer Price Index: All Items Growth Rate','CPALTT01USM657N','Growth Rate Previous Period, Not Seasonally Adjusted'],
        ['China','MoM CPI','Monthly','Consumer Price Index: All Items Growth Rate','CPALTT01CNM657N','Growth Rate Previous Period, Not Seasonally Adjusted'],
        ['Japan','MoM CPI','Monthly','Consumer Price Index: All Items Growth Rate','CPALTT01USM657N','Growth Rate Previous Period, Not Seasonally Adjusted'],
        ['Korea','MoM CPI','Monthly','Consumer Price Index: All Items Growth Rate','CPALTT01KRM657N','Growth Rate Previous Period, Not Seasonally Adjusted'],
        ['Russia','MoM CPI','Monthly','Consumer Price Index: All Items Growth Rate','CPALTT01RUM657N','Growth Rate Previous Period, Not Seasonally Adjusted'],
        ['India','MoM CPI','Monthly','Consumer Price Index: All Items Growth Rate','CPALTT01INM657N','Growth Rate Previous Period, Not Seasonally Adjusted'],
        ['France','MoM CPI','Monthly','Consumer Price Index: All Items Growth Rate','CPALTT01FRM657N','Growth Rate Previous Period, Not Seasonally Adjusted'],
        ['Germany','MoM CPI','Monthly','Consumer Price Index: All Items Growth Rate','CPALTT01DEM657N','Growth Rate Previous Period, Not Seasonally Adjusted'],
        ['Canada','MoM CPI','Monthly','Consumer Price Index: All Items Growth Rate','CPALTT01CAM657N','Growth Rate Previous Period, Not Seasonally Adjusted'],
        ['UK','MoM CPI','Monthly','Consumer Price Index: All Items Growth Rate','CPALTT01GBM657N','Growth Rate Previous Period, Not Seasonally Adjusted'],

        # PPI相对值%：月度数据，以2015年为基准，未经季节性调整
        ['Sweden','Constant PPI','Monthly','Producer Prices Index: Total Industrial Activities','PIEATI01SEM661N','Index 2015=100, Not Seasonally Adjusted'],
        ['Spain','Constant PPI','Monthly','Producer Prices Index: Total Industrial Activities','PIEATI01ESM661N','Index 2015=100, Not Seasonally Adjusted'],
        ['UK','Constant PPI','Monthly','Producer Prices Index: Total Industrial Activities','PIEATI01GBM661N','Index 2015=100, Not Seasonally Adjusted'],
        ['Italy','Constant PPI','Monthly','Producer Prices Index: Total Industrial Activities','PIEATI01ITM661N','Index 2015=100, Not Seasonally Adjusted'],
        ['Euro Area','Constant PPI','Monthly','Producer Prices Index: Total Industrial Activities','PIEATI01EZM661N','Index 2015=100, Not Seasonally Adjusted'],
        ['Switzerland','Constant PPI','Monthly','Producer Prices Index: Total Industrial Activities','PIEATI01CHM661N','Index 2015=100, Not Seasonally Adjusted'],
        ['France','Constant PPI','Monthly','Producer Prices Index: Total Industrial Activities','PIEATI01FRM661N','Index 2015=100, Not Seasonally Adjusted'],
        ['Germany','Constant PPI','Monthly','Producer Prices Index: Total Industrial Activities','PIEATI01DEM661N','Index 2015=100, Not Seasonally Adjusted'],
        ['USA','Constant PPI','Monthly','Producer Prices Index: Total Industrial Activities','PIEAMP01USM661N','Index 2015=100, Not Seasonally Adjusted'],
        ['Mexico','Constant PPI','Monthly','Producer Prices Index: Total Industrial Activities','PIEATI02MXM661N','Index 2015=100, Not Seasonally Adjusted'],
        ['Japan','Constant PPI','Monthly','Producer Prices Index: Total Industrial Activities','PIEATI02JPM661N','Index 2015=100, Not Seasonally Adjusted'],
        ['Korea','Constant PPI','Monthly','Producer Prices Index: Total Industrial Activities','PIEATI02KRM661N','Index 2015=100, Not Seasonally Adjusted'],
        ['Russia','Constant PPI','Monthly','Producer Prices Index: Total Industrial Activities','PIEATI02RUM661N','Index 2015=100, Not Seasonally Adjusted'],
        ['Canada','Constant PPI','Monthly','Producer Prices Index: Total Industrial Activities','PIEAMP01CAM661N','Index 2015=100, Not Seasonally Adjusted'],
        
        # PPI China相对值%, up to 2015 & Annual only
        ['China','Constant PPI','Annual','Producer Prices Index: Total Industrial Activities','PIEATI01CNA661N','Index 2015=100, Not Seasonally Adjusted'],

        # PPI同比%：月度数据，未经季节性调整
        ['China','YoY PPI','Monthly','Producer Prices Index: Industrial Activities','CHNPIEATI01GYM','Growth rate same period previous year, Not Seasonally Adjusted'],
        ['UK','YoY PPI','Monthly','Producer Prices Index: Industrial Activities','GBRPIEATI01GYM','Growth rate same period previous year, Not Seasonally Adjusted'],
        ['France','YoY PPI','Monthly','Producer Prices Index: Industrial Activities','FRAPIEATI01GYM','Growth rate same period previous year, Not Seasonally Adjusted'],
        ['Germany','YoY PPI','Monthly','Producer Prices Index: Industrial Activities','DEUPIEATI01GYM','Growth rate same period previous year, Not Seasonally Adjusted'],
        ['Japan','YoY PPI','Monthly','Producer Prices Index: Industrial Activities','JPNPIEATI02GYM','Growth rate same period previous year, Not Seasonally Adjusted'],
        ['Korea','YoY PPI','Monthly','Producer Prices Index: Industrial Activities','KORPIEATI02GYM','Growth rate same period previous year, Not Seasonally Adjusted'],
        ['Italy','YoY PPI','Monthly','Producer Prices Index: Industrial Activities','ITAPIEATI01GYM','Growth rate same period previous year, Not Seasonally Adjusted'],
        ['Spain','YoY PPI','Monthly','Producer Prices Index: Industrial Activities','ITAPIEATI01GYM','Growth rate same period previous year, Not Seasonally Adjusted'],
        ['Poland','YoY PPI','Monthly','Producer Prices Index: Industrial Activities','POLPIEATI01GYM','Growth rate same period previous year, Not Seasonally Adjusted'],
        ['USA','YoY PPI','Monthly','Producer Prices Index: Industrial Activities','PIEAMP02USM659N','Growth rate same period previous year, Not Seasonally Adjusted'],
        
        # Interest rate, Discount rate：中央银行贴现率，央行给予商业银行的短期贷款利率。月度数据，年华利率%，未经季节性调整
        ['China','Discount Rate','Monthly','Central Bank Discount Rate','INTDSRCNM193N','Percent per Annum, Not Seasonally Adjusted'],
        ['USA','Discount Rate','Monthly','Central Bank Discount Rate','INTDSRUSM193N','Percent per Annum, Not Seasonally Adjusted'],
        ['India','Discount Rate','Monthly','Central Bank Discount Rate','INTDSRINM193N','Percent per Annum, Not Seasonally Adjusted'],
        ['Japan','Discount Rate','Monthly','Central Bank Discount Rate','INTDSRJPM193N','Percent per Annum, Not Seasonally Adjusted'],
        ['Korea','Discount Rate','Monthly','Central Bank Discount Rate','INTDSRKRM193N','Percent per Annum, Not Seasonally Adjusted'],
        ['Brazil','Discount Rate','Monthly','Central Bank Discount Rate','INTDSRBRM193N','Percent per Annum, Not Seasonally Adjusted'],
        
        # Immediate Interest rate, less than 24 hours, interbank rate：即期利率%，银行间同业拆借利率，隔夜利率。月度数据，未经季节性调整
        ['China','Immediate Rate','Monthly','Immediate Rates: Less than 24 Hours: Interbank Rate','IRSTCI01CNM156N','Percent per Annum, Not Seasonally Adjusted'],
        ['USA','Immediate Rate','Monthly','Immediate Rates: Less than 24 Hours: Interbank Rate','IRSTCI01USM156N','Percent per Annum, Not Seasonally Adjusted'],
        ['Japan','Immediate Rate','Monthly','Immediate Rates: Less than 24 Hours: Interbank Rate','IRSTCI01JPM156N','Percent per Annum, Not Seasonally Adjusted'],
        ['Korea','Immediate Rate','Monthly','Immediate Rates: Less than 24 Hours: Interbank Rate','IRSTCI01KRM156N','Percent per Annum, Not Seasonally Adjusted'],
        ['India','Immediate Rate','Monthly','Immediate Rates: Less than 24 Hours: Interbank Rate','IRSTCI01INM156N','Percent per Annum, Not Seasonally Adjusted'],
        ['France','Immediate Rate','Monthly','Immediate Rates: Less than 24 Hours: Interbank Rate','IRSTCI01FRM156N','Percent per Annum, Not Seasonally Adjusted'],
        ['Germany','Immediate Rate','Monthly','Immediate Rates: Less than 24 Hours: Interbank Rate','IRSTCI01DEM156N','Percent per Annum, Not Seasonally Adjusted'],
        ['Australia','Immediate Rate','Monthly','Immediate Rates: Less than 24 Hours: Interbank Rate','IRSTCI01AUM156N','Percent per Annum, Not Seasonally Adjusted'],
        ['Indonesia','Immediate Rate','Monthly','Immediate Rates: Less than 24 Hours: Interbank Rate','IRSTCI01IDM156N','Percent per Annum, Not Seasonally Adjusted'],
        ['Russia','Immediate Rate','Monthly','Immediate Rates: Less than 24 Hours: Interbank Rate','IRSTCI01RUM156N','Percent per Annum, Not Seasonally Adjusted'],

        ['LIBOR','Immediate Rate','Daily','Overnight London Interbank Offered Rate, based on USD','USDONTD156N','Percent per Annum, Not Seasonally Adjusted'],
        ['UK','LIBOR','Daily','Overnight London Interbank Offered Rate, based on USD','USDONTD156N','Percent per Annum, Not Seasonally Adjusted'],
        
        # Spot Exchange Rate：即期汇率，本币/1USD。每日数据，未经季节性调整
        ['China','Exchange Rate','Daily','Local Currency/USD Foreign Exchange Rate','DEXCHUS','Chinese Yuan/1 US$, Not Seasonally Adjusted'],
        ['Japan','Exchange Rate','Daily','Local Currency/USD Foreign Exchange Rate','DEXJPUS','Japanese Yen/1 US$, Not Seasonally Adjusted'],
        ['Korea','Exchange Rate','Daily','Local Currency/USD Foreign Exchange Rate','DEXKOUS','South Korea Won/1 US$, Not Seasonally Adjusted'],
        ['Singapore','Exchange Rate','Daily','Local Currency/USD Foreign Exchange Rate','DEXSIUS','Singapore Dollars/1 US$, Not Seasonally Adjusted'],
        ['China Hong Kong','Exchange Rate','Daily','Local Currency/USD Foreign Exchange Rate','DEXHKUS','HK Dollars/1 US$, Not Seasonally Adjusted'],
        ['Australia','Exchange Rate','Daily','USD/Local Currency Foreign Exchange Rate','DEXUSAL','US Dollars/1 Australian Dollar, Not Seasonally Adjusted'],
        ['Euro','Exchange Rate','Daily','USD/Local Currency Foreign Exchange Rate','DEXUSEU','US Dollars/1 Euro, Not Seasonally Adjusted'],
        ['India','Exchange Rate','Daily','Local Currency/USD Foreign Exchange Rate','DEXINUS','Indian Rupees/1 US$, Not Seasonally Adjusted'],
        ['UK','Exchange Rate','Daily','USD/Local Currency Foreign Exchange Rate','DEXUSUK','US Dollars/1 British Pound, Not Seasonally Adjusted'],
        ['Canada','Exchange Rate','Daily','Local Currency/USD Foreign Exchange Rate','DEXCAUS','Canadian Dollars/1 US$, Not Seasonally Adjusted'],
        ['Mexico','Exchange Rate','Daily','Local Currency/USD Foreign Exchange Rate','DEXMXUS','Mexican New Pesos/1 US$, Not Seasonally Adjusted'],
        ['Brazil','Exchange Rate','Daily','Local Currency/USD Foreign Exchange Rate','DEXBZUS','Brazilian Reals/1 US$, Not Seasonally Adjusted'],
        ['Venezuela','Exchange Rate','Daily','Local Currency/USD Foreign Exchange Rate','DEXVZUS','Venezuelan Bolivares/1 US$, Not Seasonally Adjusted'],
        ['South Africa','Exchange Rate','Daily','Local Currency/USD Foreign Exchange Rate','DEXSFUS','South African Rand/1 US$, Not Seasonally Adjusted'],
        ['Sweden','Exchange Rate','Daily','Local Currency/USD Foreign Exchange Rate','DEXSDUS','Swedish Kronor/1 US$, Not Seasonally Adjusted'],
        ['Thailand','Exchange Rate','Daily','Local Currency/USD Foreign Exchange Rate','DEXTHUS','Thai Baht/1 US$, Not Seasonally Adjusted'],
        ['New Zealand','Exchange Rate','Daily','USD/Local Currency Foreign Exchange Rate','DEXUSNZ','US Dollars/1 New Zealand Dollar, Not Seasonally Adjusted'],
        ['China Taiwan','Exchange Rate','Daily','Local Currency/USD Foreign Exchange Rate','DEXTAUS','New Taiwan Dollars/1 US$, Not Seasonally Adjusted'],
        ['Malaysia','Exchange Rate','Daily','Local Currency/USD Foreign Exchange Rate','DEXMAUS','Malaysian Ringgit/1 US$, Not Seasonally Adjusted'],
        ['Denmark','Exchange Rate','Daily','Local Currency/USD Foreign Exchange Rate','DEXDNUS','Danish Kroner/1 US$, Not Seasonally Adjusted'],
        
        # M0，本币，月度数据，未经季节性调整，discontinued
        ['China','M0','Monthly','National Monetary Supply M0','MYAGM0CNM189N','National Currency, Seasonally Adjusted'],
        
        # M1，本币，月度数据，经季节性调整，discontinued
        ['China','M1','Monthly','National Monetary Supply M1','MANMM101CNM189S','National Currency, Seasonally Adjusted'],
        ['USA','M1','Monthly','National Monetary Supply M1','MANMM101USM189S','National Currency, Seasonally Adjusted'],
        ['Japan','M1','Monthly','National Monetary Supply M1','MANMM101JPM189S','National Currency, Seasonally Adjusted'],
        ['Euro Area','M1','Monthly','Euro Area Monetary Supply M1','MANMM101EZM189S','National Currency, Seasonally Adjusted'],
        ['Korea','M1','Monthly','National Monetary Supply M1','MANMM101KRM189S','National Currency, Seasonally Adjusted'],
        ['India','M1','Monthly','National Monetary Supply M1','MANMM101INM189S','National Currency, Seasonally Adjusted'],
        
        # M2，本币，月度数据，未经季节性调整，discontinued
        ['China','M2','Monthly','National Monetary Supply M2','MYAGM2CNM189N','National Currency, Not Seasonally Adjusted'],
        ['Japan','M2','Monthly','National Monetary Supply M2','MYAGM2JPM189N','National Currency, Seasonally Adjusted'],
        ['Korea','M2','Monthly','National Monetary Supply M2','MYAGM2KRM189N','National Currency, Not Seasonally Adjusted'],
        ['France','M2','Monthly','National Monetary Supply M2','MYAGM2FRM189N','National Currency, Not Seasonally Adjusted'],
        ['Italy','M2','Monthly','National Monetary Supply M2','MYAGM2ITM189N','National Currency, Not Seasonally Adjusted'],
        ['Russia','M2','Monthly','National Monetary Supply M2','MYAGM2RUM189N','National Currency, Not Seasonally Adjusted'],
        ['Indonesia','M2','Monthly','National Monetary Supply M2','MYAGM2IDM189N','National Currency, Not Seasonally Adjusted'],
        ['Brazil','M2','Monthly','National Monetary Supply M2','MYAGM2BRM189N','National Currency, Not Seasonally Adjusted'],
        ['USA','M2','Monthly','National Monetary Supply M2','M2NS','Billions of Dollars, Not Seasonally Adjusted'],

        # M3，本币，月度数据，经季节性调整，discontinued
        ['China','M3','Monthly','National Monetary Supply M3','MABMM301CNM189S','National Currency, Seasonally Adjusted'],
        ['USA','M3','Monthly','National Monetary Supply M3','MABMM301USM189S','National Currency, Seasonally Adjusted'],
        ['Japan','M3','Monthly','National Monetary Supply M3','MABMM301JPM189S','National Currency, Seasonally Adjusted'],
        ['UK','M3','Monthly','National Monetary Supply M3','MABMM301GBM189S','National Currency, Seasonally Adjusted'],
        ['Euro Area','M3','Monthly','Euro Area Monetary Supply M3','MABMM301EZM189S','National Currency, Seasonally Adjusted'],
        ['Australia','M3','Monthly','National Monetary Supply M3','MABMM301AUM189S','National Currency, Seasonally Adjusted'],

        # Stock Market Cap to GDP：股票市场市值对GDP比率%，年度数据，未经季节性调整，discontinued
        ['China','SMC to GDP','Annual','Stock Market Capitalization to GDP','DDDM01CNA156NWDB','Percent, Not Seasonally Adjusted'],
        ['USA','SMC to GDP','Annual','Stock Market Capitalization to GDP','DDDM01USA156NWDB','Percent, Not Seasonally Adjusted'],
        ['Japan','SMC to GDP','Annual','Stock Market Capitalization to GDP','DDDM01JPA156NWDB','Percent, Not Seasonally Adjusted'],
        ['Korea','SMC to GDP','Annual','Stock Market Capitalization to GDP','DDDM01KRA156NWDB','Percent, Not Seasonally Adjusted'],
        ['India','SMC to GDP','Annual','Stock Market Capitalization to GDP','DDDM01INA156NWDB','Percent, Not Seasonally Adjusted'],
        ['Singapore','SMC to GDP','Annual','Stock Market Capitalization to GDP','DDDM01SGA156NWDB','Percent, Not Seasonally Adjusted'],
        ['Malaysia','SMC to GDP','Annual','Stock Market Capitalization to GDP','DDDM01MYA156NWDB','Percent, Not Seasonally Adjusted'],
        ['Indonesia','SMC to GDP','Annual','Stock Market Capitalization to GDP','DDDM01IDA156NWDB','Percent, Not Seasonally Adjusted'],
        ['Vietnam','SMC to GDP','Annual','Stock Market Capitalization to GDP','DDDM01VNA156NWDB','Percent, Not Seasonally Adjusted'],
        ['China Hong Kong','SMC to GDP','Annual','Stock Market Capitalization to GDP','DDDM01HKA156NWDB','Percent, Not Seasonally Adjusted'],
        ['France','SMC to GDP','Annual','Stock Market Capitalization to GDP','DDDM01FRA156NWDB','Percent, Not Seasonally Adjusted'],
        ['Germany','SMC to GDP','Annual','Stock Market Capitalization to GDP','DDDM01DEA156NWDB','Percent, Not Seasonally Adjusted'],
        ['UK','SMC to GDP','Annual','Stock Market Capitalization to GDP','DDDM01GBA156NWDB','Percent, Not Seasonally Adjusted'],
        ['Italy','SMC to GDP','Annual','Stock Market Capitalization to GDP','DDDM01ITA156NWDB','Percent, Not Seasonally Adjusted'],
        ['Spain','SMC to GDP','Annual','Stock Market Capitalization to GDP','DDDM01ESA156NWDB','Percent, Not Seasonally Adjusted'],
        ['Israel','SMC to GDP','Annual','Stock Market Capitalization to GDP','DDDM01ILA156NWDB','Percent, Not Seasonally Adjusted'],
        ['Canada','SMC to GDP','Annual','Stock Market Capitalization to GDP','DDDM01CAA156NWDB','Percent, Not Seasonally Adjusted'],

        # 消费者信心综合指数：OECD。月度数据，基准=100，经季节性调整
        ['China','Consumer Confidence','Monthly','Consumer Confidence Composite Indicator by OECD','CSCICP03CNM665S','Normalised (Normal=100), Seasonally Adjusted'],
        ['USA','Consumer Confidence','Monthly','Consumer Confidence Composite Indicator by OECD','CSCICP03USM665S','Normalised (Normal=100), Seasonally Adjusted'],
        ['Japan','Consumer Confidence','Monthly','Consumer Confidence Composite Indicator by OECD','CSCICP03JPM665S','Normalised (Normal=100), Seasonally Adjusted'],
        ['Korea','Consumer Confidence','Monthly','Consumer Confidence Composite Indicator by OECD','CSCICP03KRM665S','Normalised (Normal=100), Seasonally Adjusted'],
        ['Indonesia','Consumer Confidence','Monthly','Consumer Confidence Composite Indicator by OECD','CSCICP03IDM665S','Normalised (Normal=100), Seasonally Adjusted'],
        ['France','Consumer Confidence','Monthly','Consumer Confidence Composite Indicator by OECD','CSCICP03FRM665S','Normalised (Normal=100), Seasonally Adjusted'],
        ['Germany','Consumer Confidence','Monthly','Consumer Confidence Composite Indicator by OECD','CSCICP03DEM665S','Normalised (Normal=100), Seasonally Adjusted'],
        ['Italy','Consumer Confidence','Monthly','Consumer Confidence Composite Indicator by OECD','CSCICP03ITM665S','Normalised (Normal=100), Seasonally Adjusted'],
        ['Spain','Consumer Confidence','Monthly','Consumer Confidence Composite Indicator by OECD','CSCICP03ESM665S','Normalised (Normal=100), Seasonally Adjusted'],

        # Crude Birth Rate粗出生率；又称出生率。指1年内平均每千人的出生人数。它反映一定时期内人口的出生水平。年度数据，未经季节性调整
        ['China','Birth Rate','Annual','Crude Birth Rate','SPDYNCBRTINCHN','Births per 1,000 People, Not Seasonally Adjusted'],
        ['USA','Birth Rate','Annual','Crude Birth Rate','SPDYNCBRTINUSA','Births per 1,000 People, Not Seasonally Adjusted'],
        ['Japan','Birth Rate','Annual','Crude Birth Rate','SPDYNCBRTINJPN','Births per 1,000 People, Not Seasonally Adjusted'],
        ['Korea','Birth Rate','Annual','Crude Birth Rate','SPDYNCBRTINKOR','Births per 1,000 People, Not Seasonally Adjusted'],
        ['France','Birth Rate','Annual','Crude Birth Rate','SPDYNCBRTINFRA','Births per 1,000 People, Not Seasonally Adjusted'],
        ['Germany','Birth Rate','Annual','Crude Birth Rate','SPDYNCBRTINDEU','Births per 1,000 People, Not Seasonally Adjusted'],
        ['India','Birth Rate','Annual','Crude Birth Rate','SPDYNCBRTININD','Births per 1,000 People, Not Seasonally Adjusted'],
        ['Indonesia','Birth Rate','Annual','Crude Birth Rate','SPDYNCBRTINIDN','Births per 1,000 People, Not Seasonally Adjusted'],
        ['Singapore','Birth Rate','Annual','Crude Birth Rate','SPDYNCBRTINSGP','Births per 1,000 People, Not Seasonally Adjusted'],
        ['Vietnam','Birth Rate','Annual','Crude Birth Rate','SPDYNCBRTINVNM','Births per 1,000 People, Not Seasonally Adjusted'],
        ['Pakistan','Birth Rate','Annual','Crude Birth Rate','SPDYNCBRTINPAK','Births per 1,000 People, Not Seasonally Adjusted'],
        ['Cambodia','Birth Rate','Annual','Crude Birth Rate','SPDYNCBRTINKHM','Births per 1,000 People, Not Seasonally Adjusted'],
        ['Malaysia','Birth Rate','Annual','Crude Birth Rate','SPDYNCBRTINMYS','Births per 1,000 People, Not Seasonally Adjusted'],
        ['Australia','Birth Rate','Annual','Crude Birth Rate','SPDYNCBRTINAUS','Births per 1,000 People, Not Seasonally Adjusted'],
        ['Italy','Birth Rate','Annual','Crude Birth Rate','SPDYNCBRTINITA','Births per 1,000 People, Not Seasonally Adjusted'],
        ['Spain','Birth Rate','Annual','Crude Birth Rate','SPDYNCBRTINESP','Births per 1,000 People, Not Seasonally Adjusted'],

        # Population Growth人口增长率；年出生率的变化率%。年度数据，未经季节性调整
        ['China','Population Growth','Annual','Population Growth by WB','SPPOPGROWCHN','Percent Change at Annual Rate, NSA'],
        ['USA','Population Growth','Annual','Population Growth by WB','SPPOPGROWUSA','Percent Change at Annual Rate, NSA'],
        ['Japan','Population Growth','Annual','Population Growth by WB','SPPOPGROWJPN','Percent Change at Annual Rate, NSA'],
        ['Korea','Population Growth','Annual','Population Growth by WB','SPPOPGROWKOR','Percent Change at Annual Rate, NSA'],
        ['India','Population Growth','Annual','Population Growth by WB','SPPOPGROWIND','Percent Change at Annual Rate, NSA'],

        # 青年人失业率%：WB。年度数据，未经季节性调整
        ['China','Youth Unemployment','Annual','Youth Unemployment Rate by WB','SLUEM1524ZSCHN','Percent(Age 15-24, seeking employment), NSA'],
        ['USA','Youth Unemployment','Annual','Youth Unemployment Rate by WB','SLUEM1524ZSUSA','Percent(Age 15-24, seeking employment), NSA'],
        ['Japan','Youth Unemployment','Annual','Youth Unemployment Rate by WB','SLUEM1524ZSJPN','Percent(Age 15-24, seeking employment), NSA'],
        ['Korea','Youth Unemployment','Annual','Youth Unemployment Rate by WB','SLUEM1524ZSKOR','Percent(Age 15-24, seeking employment), NSA'],
        ['India','Youth Unemployment','Annual','Youth Unemployment Rate by WB','SLUEM1524ZSIND','Percent(Age 15-24, seeking employment), NSA'],

        # 国民总收入GNI: Gross National Income。美元现价，年度数据，未经季节性调整
        ['China','GNI','Annual','Gross National Income','MKTGNICNA646NWDB','Current U.S. Dollars, Not Seasonally Adjusted'],
        ['USA','GNI','Annual','Gross National Income','MKTGNIUSA646NWDB','Current U.S. Dollars, Not Seasonally Adjusted'],
        ['Japan','GNI','Annual','Gross National Income','MKTGNIJPA646NWDB','Current U.S. Dollars, Not Seasonally Adjusted'],
        ['Korea','GNI','Annual','Gross National Income','MKTGNIKRA646NWDB','Current U.S. Dollars, Not Seasonally Adjusted'],
        ['India','GNI','Annual','Gross National Income','MKTGNIINA646NWDB','Current U.S. Dollars, Not Seasonally Adjusted'],
        ['Vietnam','GNI','Annual','Gross National Income','MKTGNIVNA646NWDB','Current U.S. Dollars, Not Seasonally Adjusted'],
        ['Thailand','GNI','Annual','Gross National Income','MKTGNITHA646NWDB','Current U.S. Dollars, Not Seasonally Adjusted'],
        ['Cambodia','GNI','Annual','Gross National Income','MKTGNIKHA646NWDB','Current U.S. Dollars, Not Seasonally Adjusted'],
        ['China Hong Kong','GNI','Annual','Gross National Income','MKTGNIHKA646NWDB','Current U.S. Dollars, Not Seasonally Adjusted'],
        ['Malaysia','GNI','Annual','Gross National Income','MKTGNIMYA646NWDB','Current U.S. Dollars, Not Seasonally Adjusted'],
        ['Singapore','GNI','Annual','Gross National Income','MKTGNISGA646NWDB','Current U.S. Dollars, Not Seasonally Adjusted'],
        ['Indonesia','GNI','Annual','Gross National Income','MKTGNIIDA646NWDB','Current U.S. Dollars, Not Seasonally Adjusted'],
        ['Australia','GNI','Annual','Gross National Income','MKTGNIAUA646NWDB','Current U.S. Dollars, Not Seasonally Adjusted'],
        ['New Zealand','GNI','Annual','Gross National Income','MKTGNINZA646NWDB','Current U.S. Dollars, Not Seasonally Adjusted'],
        ['UK','GNI','Annual','Gross National Income','MKTGNIGBA646NWDB','Current U.S. Dollars, Not Seasonally Adjusted'],
        ['Germany','GNI','Annual','Gross National Income','MKTGNIDEA646NWDB','Current U.S. Dollars, Not Seasonally Adjusted'],
        ['France','GNI','Annual','Gross National Income','MKTGNIFRA646NWDB','Current U.S. Dollars, Not Seasonally Adjusted'],
        ['Spain','GNI','Annual','Gross National Income','MKTGNIESA646NWDB','Current U.S. Dollars, Not Seasonally Adjusted'],

        # 出口对进口的比例Exports to Imports%：月度数据，经季节性调整。美国的季节性调整调整方法：X-12 Arima
        # 季节性调整调整的思路：从目前的变化综扣除过去数年的平均变动，为了回答问题：目前的变化是纯粹的季节性现象，还是说明目前的变化是不寻常的。
        ['China','Exports to Imports','Monthly','Ratio of Exports to Imports','XTEITT01CNM156S','Percent, Seasonally Adjusted'],
        ['India','Exports to Imports','Monthly','Ratio of Exports to Imports','XTEITT01INM156N','Percent, Seasonally Adjusted'],
        ['Brazil','Exports to Imports','Monthly','Ratio of Exports to Imports','XTEITT01BRM156S','Percent, Seasonally Adjusted'],
        ['Russia','Exports to Imports','Monthly','Ratio of Exports to Imports','XTEITT01RUM156S','Percent, Seasonally Adjusted'],
        ['Indonesia','Exports to Imports','Monthly','Ratio of Exports to Imports','XTEITT01IDM156S','Percent, Seasonally Adjusted'],

        # 人口受雇比例：就业比率%，年度数据，未经季节性调整
        ['China','Employment to Population','Annual','Employment to Population Ratio by WB','SLEMPTOTLSPZSCHN','Percent, Not Seasonally Adjusted'],
        ['USA','Employment to Population','Annual','Employment to Population Ratio by WB','SLEMPTOTLSPZSUSA','Percent, Not Seasonally Adjusted'],
        ['Japan','Employment to Population','Annual','Employment to Population Ratio by WB','SLEMPTOTLSPZSJPN','Percent, Not Seasonally Adjusted'],
        ['Korea','Employment to Population','Annual','Employment to Population Ratio by WB','SLEMPTOTLSPZSKOR','Percent, Not Seasonally Adjusted'],
        ['India','Employment to Population','Annual','Employment to Population Ratio by WB','SLEMPTOTLSPZSIND','Percent, Not Seasonally Adjusted'],

        # 人口总数Population：年度数据，未经季节性调整
        ['China','Population','Annual','Total Population','POPTOTCNA647NWDB','Persons, Not Seasonally Adjusted'],
        ['USA','Population','Annual','Total Population','POPTOTUSA647NWDB','Persons, Not Seasonally Adjusted'],
        ['Japan','Population','Annual','Total Population','POPTOTJPA647NWDB','Persons, Not Seasonally Adjusted'],
        ['Korea','Population','Annual','Total Population','POPTOTKRA647NWDB','Persons, Not Seasonally Adjusted'],
        ['India','Population','Annual','Total Population','POPTOTINA647NWDB','Persons, Not Seasonally Adjusted'],
        
        # 其他
        ], columns=['scope','factor','freq','name','symbol','units'])
    
   return s


#==============================================================================
#==============================================================================
#==============================================================================
#==============================================================================
if __name__ =="__main__":
    fromdate='2024-1-1'
    todate='2024-8-31'
    df=pmi_china(fromdate,todate)
    loc='best'; facecolor='papayawhip'

def pmi_china(fromdate,todate,date_range=True,loc='best',facecolor='papayawhip'):
    """
    功能：绘制中国的PMI指数制造业/非制造业单线图
    """
    #检查日期期间的合理性
    valid,start,end=check_period(fromdate,todate)
    if not valid:
        print('  Error(pmi_china): period not valid:',fromdate,todate)
        return None      
    
    #日期变换，将日都重置为每月的第一日
    year=start.year
    month=start.month    
    fromdate1=str(year)+'-'+str(month)+'-'+'1'

    year=end.year
    month=end.month    
    todate1=str(year)+'-'+str(month)+'-'+'1'
    _,start,end=check_period(fromdate1,todate1)
    
    #获取PMI数据
    import akshare as ak
    df = ak.macro_china_pmi()
    
    #截取日期区间数据
    import pandas as pd
    df['date']=pd.to_datetime(df['月份'],format='%Y年%m月份')
    from datetime import timedelta
    df['date']=df['date'].apply(lambda x:x+timedelta(days=15))
    
    df.set_index('date',inplace=True)    
    df1=df[df.index >= start]
    df2=df1[df1.index <= end]
    
    #形成水平50线
    df2['benchmark']=50   
    
    #将字符串表示的数值转换为数值型，否则绘图很乱
    df2['制造业PMI']=df2['制造业-指数'].astype('float')
    df2['非制造业PMI']=df2['非制造业-指数'].astype('float')
    
    """
    #绘图：制造业
    ticker1=ticker2='PMI'
    colname2="benchmark"
    label2="景气/衰退分界线"
    ylabeltxt=''
    
    import datetime
    today=datetime.date.today()
    footnote="数据来源：东方财富，"+str(today)
    
    colname1="制造业PMI"
    label1="制造业"    
    titletxt="中国采购经理人指数PMI：制造业"
    plot_line2(df2,ticker1,colname1,label1, \
               df2,ticker2,colname2,label2, \
               ylabeltxt,titletxt,footnote,loc1=loc,facecolor=facecolor)
    
    #绘图：非制造业
    colname1="非制造业PMI"
    label1="非制造业"    
    titletxt="中国采购经理人指数PMI：非制造业"
    plot_line2(df2,ticker1,colname1,label1, \
               df2,ticker2,colname2,label2, \
               ylabeltxt,titletxt,footnote,loc1=loc,facecolor=facecolor)    
    """
    titletxt="中国采购经理人指数PMI"
    ticker1=ticker2='PMI'
    colname1="制造业PMI"; label1="制造业"
    colname2="非制造业PMI"; label2="非制造业"
    ylabeltxt=''
        
    import datetime
    today=datetime.date.today()
    footnote="数据来源：东方财富，"+str(today)
    
    plot2_line2(df2,ticker1,colname1,label1, \
               df2,ticker2,colname2,label2, \
               yline=50, \
               ylabeltxt=ylabeltxt,titletxt=titletxt,footnote=footnote,loc1=loc, \
               date_range=date_range,date_fmt='%Y-%m',facecolor=facecolor)    
    
    #返回数据
    return df2

#==============================================================================
#==============================================================================
#==============================================================================
if __name__ =="__main__":
    fieldlist=['VALUE','scope','factor','freq','name','units']

def internal_growth_rate_df(df0,fieldlist=['VALUE','scope','factor','freq','name','units']):
    """
    功能：计算内部增长率IRR
    rdf的结构：VALUE为具体的数值，scope为国家或地区，factor为指标，freq为频度。
    """
    if df0 is None:
        print("  #Error(internal_growth_rate_df): no data provided")
        return
    
    df=df0.copy()
    df.dropna(inplace=True)
    
    fld_value=fieldlist[0]
    fld_scope=fieldlist[1]
    scope=df[fld_scope][0]
    
    fld_factor=fieldlist[2]
    factor=df[fld_factor][0]
    
    fld_freq=fieldlist[3]
    freq=df[fld_freq][0]
    
    fld_name=fieldlist[4]
    fld_units=fieldlist[5]
    
    #开始值和结束值
    value0=df[fld_value][0]
    value1=df[fld_value][-1]
    num=len(df)
    item_gr=pow(value1/value0,1/num)-1.0
    
    annual_gr=item_gr
    if freq == 'Daily':
        annual_gr=pow(1+item_gr,365)-1.0
    if freq == 'Monthly':
        annual_gr=pow(1+item_gr,12)-1.0
    if freq == 'Quarterly':
        annual_gr=pow(1+item_gr,4)-1.0
    
    #计算期间
    date0=str(df.index[0].year)
    date1=str(df.index[-1].year)
    
    if freq in ['Monthly','Daily']:
        date0=date0+'-'+str(df.index[0].month)+''
        date1=date1+'-'+str(df.index[-1].month)+''        
    
    if freq in ['Daily']:
        date0=date0+'-'+str(df.index[0].day)+'日'
        date1=date1+'-'+str(df.index[-1].day)+'日'     
    
    #显示增长率
    lang=check_language()
    #print('\n')
    if lang == 'Chinese':
        print('从'+date0+'至'+date1+'：')
        if freq != 'Annual':
            print('    '+ectranslate(scope)+ectranslate(factor)+'的'+ectranslate(freq)+'均环比复合增长率：',round(item_gr*100.0,4),'\b%')
        print('    '+ectranslate(scope)+ectranslate(factor)+'的年均复合增长率：',round(annual_gr*100.0,4),'\b%')
    else:
        print('From '+date0+' to '+date1+':')
        if freq != 'Annual':
            print('    '+scope+', '+factor+' mom compound growth rate:',round(item_gr*100.0,4),'\b%')
        print('    '+scope+', '+factor+' yoy compound growth rate:',round(annual_gr*100.0,4),'\b%')
        
    return 

if __name__ =="__main__":
    internal_growth_rate_df(df)
    

def internal_growth_rate(rvar,fieldlist=['VALUE','scope','factor','freq','name','units']):
    """
    功能：计算内部增长率IRR
    rvar：可能为df或dict。若为dict，里面的元素为两个df。
    每个df的结构：VALUE为具体的数值，scope为国家或地区，factor为指标，freq为频度。
    """
    print('')
    import pandas as pd
    if isinstance(rvar,pd.DataFrame):
        internal_growth_rate_df(rvar,fieldlist=['VALUE','scope','factor','freq','name','units'])
        return
    
    if isinstance(rvar,tuple):
        for k in rvar:
            internal_growth_rate_df(k,fieldlist=['VALUE','scope','factor','freq','name','units'])
        return
    
    return
        
if __name__ =="__main__":
    internal_growth_rate(df)
#==============================================================================
if __name__ =="__main__":
    ticker='China'
    indicator='GDP'


def macro_trend(ticker,indicator,start='L10Y',end='today', \
                power=0,twinx=False,attention_value=999,zeroline=False, \
                datatag=False,date_range=False, \
                loc1='best',loc2='best',facecolor='papayawhip'):
    """
    功能：套壳函数，compare_economy, economy_trend
    """
    
    # 处理日期
    fromdate,todate=start_end_preprocess(start,end)
    
    # 判断ticker个数
    if isinstance(ticker,str):
        ticker_num=1
    if isinstance(ticker,list):
        ticker_num=len(ticker)
        if ticker_num==1:
            ticker=ticker[0]
    
    # 判断indicator个数
    if isinstance(indicator,str):
        indicator_num=1
    if isinstance(indicator,list):
        indicator_num=len(indicator) 
        if indicator_num==1:
            indicator=indicator[0]        

    # 是否PMI
    if ticker_num==1 and indicator_num==1:
        if indicator.upper()=='PMI' and ticker.title()=='China':
            df=pmi_china(fromdate=fromdate,todate=todate, \
                         date_range=date_range,loc=loc1,facecolor=facecolor)
        
            return df
        
    # 双ticker或者双indicator
    if ticker_num>=2 or indicator_num>=2:
        if 'YoY PPI' in indicator:
            attention_value=0

        df=compare_economy(ticker=ticker,indicator=indicator, \
                           start=fromdate,end=todate, \
                           power=power,twinx=twinx, \
                           yline=attention_value, \
                           loc1=loc1,loc2=loc2,facecolor=facecolor)
        # 计算增长率
        # 有inf/nan错误，未找出原因，先避开
        if not 'YoY PPI' in indicator:
            internal_growth_rate(df)
        return df
        
    # 单ticker且单indicator
    if ticker_num==1 and indicator_num==1:
        if 'YoY PPI' in indicator:
            attention_value=0
        
        df=economy_trend0(start=fromdate,end=todate,ticker=ticker,indicator=indicator, \
                         datatag=datatag,power=power, \
                         zeroline=zeroline,yline=attention_value,facecolor=facecolor)    
        # 计算增长率
        # 有inf/nan错误，未找出原因，先避开
        if not 'YoY PPI' in indicator:
            internal_growth_rate(df)
            
        return df
    
    print("  #Warning(macro_trend): puzzled on what to for",ticker,"with",indicator)
    return None


#==============================================================================
#==============================================================================

    