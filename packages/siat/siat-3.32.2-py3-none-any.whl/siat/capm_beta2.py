# -*- coding: utf-8 -*-
"""
本模块功能：CAPM beta
所属工具包：证券投资分析工具SIAT 
SIAT：Security Investment Analysis Tool
创建日期：2024年3月22日
最新修订日期：2024年3月22日
作者：王德宏 (WANG Dehong, Peter)
作者单位：北京外国语大学国际商学院
作者邮件：wdehong2000@163.com
版权所有：王德宏
用途限制：仅限研究与教学使用，不可商用！
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
from siat.grafix import *

import pandas as pd
import numpy as np
#==============================================================================
#==============================================================================
#==============================================================================
if __name__=='__main__':
    ticker="600519.SS"

def get_market_index_code(ticker):
    """
    功能：基于股票ticker确定其所在市场的大盘指数代码
    """
    ticker=tickers_cvt2yahoo(ticker)
    _,_,suffix=split_prefix_suffix(ticker)
    
    if suffix in ['SS']:
        mktidx='000001.SS' #上证综合指数
    elif suffix in ['SZ']:
        mktidx='399001.SZ'
    elif suffix in ['BJ']:
        mktidx='899050.BJ' #北证50指数   
    elif suffix in ['CN']:
        mktidx='000300.SS' #沪深300指数          
    elif suffix in ['HK']:
        mktidx='^HSI'      #恒生指数
    elif suffix in ['TW']:
        mktidx='^TWII'     #台湾加权指数    
    elif suffix in ['SI']:
        mktidx='^STI'      #新加坡海峡时报指数
    elif suffix in ['T']:
        mktidx='^N225'     #日经225指数
    elif suffix in ['KS']:
        mktidx='^KS11'     #韩国综合指数
    elif suffix in ['NS','BO']:
        mktidx='^SNX'      #孟买敏感指数
    elif suffix =='':
        mktidx='^SPX'      #标普500指数
    elif suffix in ['L','UK']:
        mktidx='^FTSE'     #英国富时100指数
    elif suffix in ['DE']:
        mktidx='^DAX'      #德国DAX30指数
    elif suffix in ['F']:
        mktidx='^CAC'      #法国CAC40指数
    else:
        mktidx='^SPX'      #标普500指数
        
    return mktidx

#==============================================================================
if __name__=='__main__':
    ticker="600519.SS"
    ticker={'Market':('US','^SPX','中概教培组合'),'EDU':0.7,'TAL':0.3}
    
    start2='2022-10-31'
    end='2024-3-23'
    RF=0.01759
    regtrddays=252
    
    mktidx='auto'; source='auto'
    
    reg_result,dretdf3=regression_capm(ticker,start2,end,RF,regtrddays)

def regression_capm(ticker,start2,end, \
                    adjust='qfq', \
                    RF=0,regtrddays=252, \
                    mktidx='auto',source='auto',ticker_type='auto'):
    """
    功能：进行CAPM回归，R-Rf=beta*(Rm-Rf)，无截距项回归
    x为(Rm-Rf)，y为R-Rf，均为日收益率，默认回归样本长度一年（365日历日或252交易日）
    返回：beta系数
    注意：回归基于传统的日收益率，而非滚动收益率
    """
    DEBUG=False

    #抓取股价，计算股票日收益率
    if DEBUG:
        print("*** DEBUG:",ticker,start2,end)
    #pricedf=get_price(ticker,start2,end,source=source)
    #pricedf=get_price_security(ticker,start2,end,source=source)
    pricedf,found=get_price_1ticker_mixed(ticker=ticker,fromdate=start2,todate=end, \
                                          adjust=adjust, \
                                          source=source,ticker_type=ticker_type)
    
    if pricedf is None:
        print("  #Error(regression_capm): info of security",ticker_name(ticker,ticker_type),"not found or inaccessible")
        return None,None
    
    #计算股票滚动收益率
    pricedf1=calc_daily_return(pricedf)
    
    #抓取大盘指数，计算指数日收益率
    """
    if 'auto' in mktidx.lower():
        mktidx=get_market_index_code(ticker)
    """
    if isinstance(ticker,dict):
        _,mktidx,pftickerlist,_,ticker_type=decompose_portfolio(ticker)
        if 'auto' in mktidx.lower():
            mktidx=get_market_index_code(pftickerlist[0])
    else:
        if 'auto' in mktidx.lower():
            mktidx=get_market_index_code(ticker)
        
    #marketdf=get_price(mktidx,start2,end,source=source)
    #大盘指数实际上无复权价？
    marketdf,found=get_price_1ticker_mixed(ticker=mktidx,fromdate=start2,todate=end, \
                                           adjust=adjust, \
                                           source=source,ticker_type=ticker_type)

    if marketdf is None:
        print("  #Error(regression_capm): info of market index",mktidx,"not found or inaccessible")
        return None,None
    
    marketdf1=calc_daily_return(marketdf)
    
    #合并股票和大盘指数日收益率
    dretdf1=pd.merge(marketdf1,pricedf1,how='inner',left_index=True,right_index=True)

    #准备CAPM回归文件
    if adjust == '':
        dretname='Daily Ret'
    else:
        dretname='Daily Adj Ret'
        
    #计算日无风险利率
    RF_daily=RF / 365 
        
    dretx=dretname+'_x' #指数日收益率
    drety=dretname+'_y' #股票日收益率
    dretdf2=dretdf1[[dretx,drety]]
    dretdf2.dropna(inplace=True)

    #计算股票和指数收益率的风险溢价R-RF
    dretdfcols=list(dretdf2)    
    for c in dretdfcols:
        dretdf2[c]=dretdf2[c].apply(lambda x: x-RF_daily)
    dretdf2=dretdf2.reset_index()
    #dretdf2.rename(columns={'index':'Date'},inplace=True)
    if 'Date' not in list(dretdf2):
        dretdf2['Date']=dretdf2['index']
    
    #CAPM回归，计算贝塔系数
    dretnum=len(dretdf2)
    if regtrddays >= dretnum:
        regtrddays=dretnum - 31 *2
        
    import statsmodels.api as sm
    reg_result=pd.DataFrame(columns=('Date','beta'))
    for i in range(dretnum):
        i2=dretnum-i
        i1=i2-regtrddays
        if i1 < 0: break
    
        regdf=dretdf2[i1:i2]
        lastdate=regdf.tail(1)['Date'].values[0]
        
        X=regdf[dretx] #无截距项回归
        Y=regdf[drety]
        model = sm.OLS(Y,X)	#定义回归模型R-Rf=beta(Rm-Rf)，X可为多元矩阵
        results = model.fit()	#进行OLS回归
        beta=results.params[0]	#提取回归系数
        
        row=pd.Series({'Date':lastdate,'beta':beta})
        try:
            reg_result=reg_result.append(row,ignore_index=True)        
        except:
            reg_result=reg_result._append(row,ignore_index=True)
        
    reg_result.set_index(['Date'],inplace=True) 
    reg_result.sort_index(inplace=True) #按日期升序排列 
    
    dretdf3=dretdf2.set_index(['Date']) 
    if 'index' in list(dretdf3):
        del dretdf3['index']
    
    reg_result['mktidx']=mktidx
    
    return reg_result,dretdf3


def regression_capm_df(marketdf,pricedf,mktidx,adjust='qfq',RF=0,regtrddays=252):
    """
    功能：进行CAPM回归，R-Rf=beta*(Rm-Rf)，无截距项回归
    x为(Rm-Rf)，y为R-Rf，均为日收益率，默认回归样本长度一年（365日历日或252交易日）
    返回：beta系数
    注意：回归基于传统的日收益率，而非滚动收益率
    """
    
    #合并股票和大盘指数日收益率
    dretdf1=pd.merge(marketdf,pricedf,how='inner',left_index=True,right_index=True)

    #准备CAPM回归文件
    if adjust == '':
        dretname='Daily Ret'
    else:
        dretname='Daily Adj Ret'
        
    #计算日无风险利率
    RF_daily=RF / 365 
        
    dretx=dretname+'_x' #指数日收益率
    drety=dretname+'_y' #股票日收益率
    dretdf2=dretdf1[[dretx,drety]]
    dretdf2.dropna(inplace=True)

    #计算股票和指数收益率的风险溢价R-RF
    dretdfcols=list(dretdf2)    
    for c in dretdfcols:
        dretdf2[c]=dretdf2[c].apply(lambda x: x-RF_daily)
    dretdf2=dretdf2.reset_index()
    #dretdf2.rename(columns={'index':'Date'},inplace=True)
    if 'Date' not in list(dretdf2):
        dretdf2['Date']=dretdf2['index']
    
    #CAPM回归，计算贝塔系数
    dretnum=len(dretdf2)
    if regtrddays >= dretnum:
        regtrddays=dretnum - 31 *2
        
    import statsmodels.api as sm
    reg_result=pd.DataFrame(columns=('Date','beta'))
    for i in range(dretnum):
        i2=dretnum-i
        i1=i2-regtrddays
        if i1 < 0: break
    
        regdf=dretdf2[i1:i2]
        lastdate=regdf.tail(1)['Date'].values[0]
        
        X=regdf[dretx] #无截距项回归
        Y=regdf[drety]
        model = sm.OLS(Y,X)	#定义回归模型R-Rf=beta(Rm-Rf)，X可为多元矩阵
        results = model.fit()	#进行OLS回归
        beta=results.params[0]	#提取回归系数
        
        row=pd.Series({'Date':lastdate,'beta':beta})
        try:
            reg_result=reg_result.append(row,ignore_index=True)        
        except:
            reg_result=reg_result._append(row,ignore_index=True)
        
    reg_result.set_index(['Date'],inplace=True) 
    reg_result.sort_index(inplace=True) #按日期升序排列 
    
    dretdf3=dretdf2.set_index(['Date']) 
    if 'index' in list(dretdf3):
        del dretdf3['index']
    
    reg_result['mktidx']=mktidx
    
    return reg_result,dretdf3

#==============================================================================
if __name__=='__main__':
    ticker="600519.SS"
    ticker={'Market':('US','^SPX','中概教培组合'),'EDU':0.5,'TAL':0.3,'TEDU':0.2}
    
    start="2024-1-1"
    end="2024-3-23"
    RF=0.01759
    regtrddays=252
    mktidx='auto'; source='auto'
    
    beta1=get_capm_beta(ticker,start,end,RF,regtrddays)
    beta1.plot()

def get_capm_beta(ticker,start,end,adjust='qfq',RF=0,regtrddays=252,mktidx='auto', \
                  source='auto',ticker_type='auto'):
    """
    功能：套壳函数regression_capm，仅返回滚动的贝塔系数，基于日收益率
    滚动窗口长度为regtrddays，默认为一年的交易日
    注意函数regression_capm没有向前调整日期，需要本函数内进行调整。
    """
    start2=date_adjust(start,adjust=-365/252 * regtrddays -31*2)
    
    reg_result,_=regression_capm(ticker=ticker,start2=start2,end=end, \
                                 adjust=adjust, \
                                 RF=RF, \
                                 regtrddays=regtrddays,mktidx=mktidx, \
                                 source=source,ticker_type=ticker_type)
    
    startpd=pd.to_datetime(date_adjust(start,adjust=-7))
    endpd=pd.to_datetime(end)
    
    try:
        reg_result2=reg_result[(reg_result.index >= startpd) & (reg_result.index <= endpd)]
    except:
        print("  #Error(get_capm_beta): none obtained from capm regression")
    
    return reg_result2
    
#==============================================================================
#==============================================================================
if __name__=='__main__':
    ticker=["600519.SS","000858.SZ"]
    ticker={'Market':('US','^SPX','中概教培组合'),'EDU':0.5,'TAL':0.3,'TEDU':0.2}
    
    start="2024-1-1"
    end="2024-3-23"
    RF=0.01759
    regression_period=365
    
    graph=True; axhline_value=1; axhline_label=''
    printout=False
    annotate=False
    mktidx='auto'
    source='auto'
    ticker_type='auto'
    
    betas=compare_mticker_1beta(ticker,start,end)

def compare_mticker_1beta(ticker,start,end, \
                         adjust='qfq', \
                         RF=0,regression_period=365, \
                            attention_value='',attention_value_area='', \
                            attention_point='',attention_point_area='', \
                         axhline_value=1,axhline_label='零线', \
                             band_area='', \
                         graph=True,facecolor='whitesmoke',loc='best',power=0, \
                         annotate=False,annotate_value=False, \
                         mark_top=False,mark_bottom=False, \
                         mark_start=False,mark_end=False, \
                         mktidx='auto',source='auto',ticker_type='auto'):
    """
    功能：多只股票，对比其贝塔系数
    """
    
    import os,sys
    class HiddenPrints:
        def __enter__(self):
            self._original_stdout = sys.stdout
            sys.stdout = open(os.devnull, 'w')

        def __exit__(self, exc_type, exc_val, exc_tb):
            sys.stdout.close()
            sys.stdout = self._original_stdout
    
    #转换字符串和列表，避免下面的循环出错
    if isinstance(ticker,str) or isinstance(ticker,dict):
        ticker=[ticker]
    if isinstance(RF,list):
        RF=RF[0]
    if isinstance(regression_period,list):
        regression_period=regression_period[0]
    print("  Working on capm beta, please wait ......")
        
    #计算日历日regression_period对应的交易日数
    regtrddays=int(252 / 365 * regression_period)

    #预处理ticker_type
    ticker_type_list=ticker_type_preprocess_mticker_mixed(ticker,ticker_type)  
    
    df=pd.DataFrame() 
    for t in ticker:
        pos=ticker.index(t)
        tt=ticker_type_list[pos] 
        
        #关闭print输出
        with HiddenPrints():
            df_tmp=get_capm_beta(t,start,end,adjust,RF,regtrddays,mktidx,source,ticker_type=tt)
        
        if df_tmp is None:
            break
        else:
            dft=df_tmp[['beta']]
            
            tname=ticker_name(t,tt)
            dft.rename(columns={'beta':tname},inplace=True)
            mktidx_name=ticker_name(df_tmp['mktidx'].values[0])
            
            # 将band_area中的ticker替换为tname
            if band_area != '':
                for index, item in enumerate(band_area):
                    if item == t:
                        band_area[index] = tname        
            
        if len(df)==0: #第一个
            df=dft 
        else:
            df=pd.merge(df,dft,how='outer',left_index=True,right_index=True)

    if len(df)==0:
        print("  #Error(compare_mticker_1beta): beta data not available for",t,"between",start,end)        
        return None
    
    #仅用于绘图和制表
    df1=df.copy()
    beta_list=list(df1)
    
    for c in beta_list:
        #是否绘制水平线
        if df1[c].max() > axhline_value and df1[c].min() < axhline_value:
            axhline_label='零线'
        #df1.rename(columns={c:ticker_name(c)},inplace=True)
    
    #共同脚注    
    footnote1=text_lang("注：","Notes: ")
    """
    if RF !=0:
        footnote2=text_lang("年化无风险利率为","RF = ")+str(round(RF*100,4))+text_lang('%。','% pa. ')
    else:
        footnote2="假设年化无风险利率为零。"
    """
    footnote2=text_lang("年化无风险利率为","RF = ")+str(round(RF*100,4))+text_lang('%。','% pa. ')
    
    footnote3=text_lang("基于","Beta using ")+mktidx_name+text_lang("，CAPM回归期间为",", CAPM rolling ")+str(regression_period)+text_lang("个自然日"," days")
    
    import datetime; todaydt = datetime.date.today()
    footnote4=text_lang("数据来源: 综合新浪/Stooq/Yahoo，","Data source: Sina/Stooq/Yahoo, ")+str(todaydt)+text_lang("统计",'')
    if footnote3 !='':
        footnotex=footnote1+footnote2+footnote3+'\n'+footnote4
    else:
        footnotex=footnote1+footnote2+footnote3+footnote4

    #绘图
    if graph:
        title_txt=text_lang("CAPM贝塔系数","CAPM Beta Coefficient")
        y_label=text_lang("贝塔系数","Beta")

        draw_lines(df1,y_label,x_label=footnotex, \
                   axhline_value=axhline_value,axhline_label=axhline_label, \
                   title_txt=title_txt,data_label=False, \
                        attention_value=attention_value,attention_value_area=attention_value_area, \
                        attention_point=attention_point,attention_point_area=attention_point_area, \
                            band_area=band_area, \
                   annotate=annotate,annotate_value=annotate, \
                   mark_top=mark_top,mark_bottom=mark_bottom, \
                   mark_start=mark_start,mark_end=mark_end, \
                   facecolor=facecolor,loc=loc,precision=4,power=power)
 
    return df

#==============================================================================
if __name__=='__main__':
    ticker="600519.SS"
    ticker="000858.SZ"
    ticker={'Market':('China','000300.SS','白酒组合'),'600519.SS':0.2,'000858.SZ':0.3,'600809.SS':0.5}
    
    start="2024-3-11"
    end="2024-3-23"
    RF=[0,0.01759,0.05]
    regression_period=365
    
    graph=True; axhline_value=1; axhline_label=''
    annotate=False
    mktidx='auto'
    source='auto'
    ticker_type='auto'
    
    betas=compare_1ticker_mRF(ticker,start,end,RF)

def compare_1ticker_mRF(ticker,start,end, \
                        adjust='qfq', \
                        RF=[0,0.02,0.05], \
                        regression_period=365, \
                            attention_value='',attention_value_area='', \
                            attention_point='',attention_point_area='', \
                        axhline_value=1,axhline_label='零线', \
                            band_area='', \
                        graph=True,facecolor='whitesmoke',loc='best', \
                        annotate=False,annotate_value=False, \
                        mark_top=False,mark_bottom=False, \
                        mark_start=False,mark_end=False, \
                        mktidx='auto',source='auto', \
                        ticker_type='auto'):
    """
    功能：一只股票，不同的无风险收益率
    """
    
    import os,sys
    class HiddenPrints:
        def __enter__(self):
            self._original_stdout = sys.stdout
            sys.stdout = open(os.devnull, 'w')

        def __exit__(self, exc_type, exc_val, exc_tb):
            sys.stdout.close()
            sys.stdout = self._original_stdout
    
    #转换字符串和列表，避免下面的循环出错
    if isinstance(ticker,list):
        ticker=ticker[0]
    if isinstance(RF,float):
        RF=[RF]
    if isinstance(regression_period,list):
        regression_period=regression_period[0]
    print("  Working on capm beta with different RFs, please wait ......")
        
    #计算日历日regression_period对应的交易日数
    regtrddays=int(252 / 365 * regression_period)
    
    #预处理ticker_type
    ticker_type=ticker_type_preprocess_mticker_mixed(ticker,ticker_type)
        
    df=pd.DataFrame() 
    for t in RF:
        #关闭print输出
        with HiddenPrints():
            df_tmp=get_capm_beta(ticker,start,end,adjust,t,regtrddays,mktidx,source,ticker_type=ticker_type)
        
        if df_tmp is None:
            break
        else:
            dft=df_tmp[['beta']]
            
            #tname="基于无风险利率"+str(round(t*100,4))+'%'
            tname="RF="+str(round(t*100,4))+'%'
            dft.rename(columns={'beta':tname},inplace=True)
            mktidx_name=ticker_name(df_tmp['mktidx'].values[0])
            
            # 将band_area中的ticker替换为tname
            if band_area != '':
                for index, item in enumerate(band_area):
                    if item == t:
                        band_area[index] = tname                

        if len(df)==0: #第一个
            df=dft 
        else:
            df=pd.merge(df,dft,how='outer',left_index=True,right_index=True)

    if len(df)==0:
        print("  #Error(compare_1ticker_mRF): data not available for",ticker,"between",start,end)        
        return None
    
    #仅用于绘图和制表
    df1=df.copy()
    beta_list=list(df1)
    
    for c in beta_list:
        #是否绘制水平线
        if df1[c].max() > axhline_value and df1[c].min() < axhline_value:
            axhline_label='零线'
        #df1.rename(columns={c:"基于无风险利率"+c},inplace=True)
    
    #去掉提前的数据
    start1=pd.to_datetime(date_adjust(start,adjust=-2))
    df1=df1[df1.index >= start1]
    
    #共同脚注    
    footnote1="注："
    footnote2=""
        
    #footnote3="贝塔系数基于日收益率，回归期间跨度为"+str(regression_period)+"个自然日。"
    footnote3="基于"+mktidx_name+"，回归期间为"+str(regression_period)+"个自然日。"
    
    import datetime; todaydt = datetime.date.today()
    footnote4="数据来源: 综合新浪/stooq/Yahoo，"+str(todaydt)+"统计"
    if footnote3 !='':
        footnotex=footnote1+footnote3+'\n'+footnote4
    else:
        footnotex=footnote4

    #绘图
    if graph:
        title_txt="CAPM贝塔系数："+ticker_name(ticker,ticker_type)
        y_label="贝塔系数"

        draw_lines(df1,y_label,x_label=footnotex, \
                   axhline_value=axhline_value,axhline_label=axhline_label, \
                   title_txt=title_txt,data_label=False, \
                        attention_value=attention_value,attention_value_area=attention_value_area, \
                        attention_point=attention_point,attention_point_area=attention_point_area, \
                            band_area=band_area, \
                   annotate=annotate,annotate_value=annotate, \
                   mark_top=mark_top,mark_bottom=mark_bottom, \
                   mark_start=mark_start,mark_end=mark_end, \
                   facecolor=facecolor,loc=loc, \
                       precision=4)
            
    return df

#==============================================================================
if __name__=='__main__':
    ticker="600519.SS"
    ticker={'Market':('China','000300.SS','白酒组合'),'600519.SS':0.2,'000858.SZ':0.3,'600809.SS':0.5}
    
    start="2024-1-1"
    end="2024-3-15"
    RF=0.01759
    regression_period=[365,183,730]
    
    graph=True; axhline_value=1; axhline_label=''
    annotate=False
    mktidx='auto'
    source='auto'
    
    betas=compare_1ticker_mregression_period(ticker,start,end,RF,regression_period)

def compare_1ticker_mregression_period(ticker,start,end, \
                         adjust='qfq', \
                         RF=0, \
                         regression_period=[183,365,730], \
                            attention_value='',attention_value_area='', \
                            attention_point='',attention_point_area='', \
                         axhline_value=1,axhline_label='零线', \
                             band_area='', \
                         graph=True,facecolor='whitesmoke',loc='best', \
                         annotate=False,annotate_value=False, \
                         mark_top=False,mark_bottom=False, \
                         mark_start=False,mark_end=False, \
                         mktidx='auto',source='auto', \
                         ticker_type='auto'):
    """
    功能：一只股票或一个投资组合，不同的回归期间
    """
    
    import os,sys
    class HiddenPrints:
        def __enter__(self):
            self._original_stdout = sys.stdout
            sys.stdout = open(os.devnull, 'w')

        def __exit__(self, exc_type, exc_val, exc_tb):
            sys.stdout.close()
            sys.stdout = self._original_stdout
    
    #转换字符串和列表，避免下面的循环出错
    if isinstance(ticker,list):
        ticker=ticker[0]
    if isinstance(RF,list):
        RF=RF[0]
    if isinstance(regression_period,int):
        regression_period=[regression_period]
    print("  Working on capm beta with different regression periods ......")

    #预处理ticker_type
    ticker_type=ticker_type_preprocess_mticker_mixed(ticker,ticker_type)
        
    df=pd.DataFrame() 
    for t in regression_period:
        #计算日历日regression_period对应的交易日数
        regtrddays=int(252 / 365 * t)
        
        #关闭print输出
        with HiddenPrints():
            df_tmp=get_capm_beta(ticker,start,end,adjust,RF,regtrddays,mktidx,source,ticker_type=ticker_type)
        
        if df_tmp is None:
            break
        else:
            dft=df_tmp[['beta']]
            
            #tname="基于"+str(t)+"自然日回归"
            tname="基于"+str(t)+"自然日回归"
            dft.rename(columns={'beta':tname},inplace=True)
            mktidx_name=ticker_name(df_tmp['mktidx'].values[0])
            
            # 将band_area中的ticker替换为tname
            if band_area != '':
                for index, item in enumerate(band_area):
                    if item == t:
                        band_area[index] = tname   
            
        if len(df)==0: #第一个
            df=dft 
        else:
            df=pd.merge(df,dft,how='outer',left_index=True,right_index=True)

    if len(df)==0:
        print("  #Error(compare_1ticker_mregression_period): data not available for",ticker,"between",start,end)        
        return None
    
    #仅用于绘图和制表
    df1=df.copy()
    beta_list=list(df1)
    
    for c in beta_list:
        #是否绘制水平线
        if df1[c].max() > axhline_value and df1[c].min() < axhline_value:
            axhline_label='零线'
        #df1.rename(columns={c:"基于"+str(c)+"自然日回归"},inplace=True)
        
    #共同脚注    
    footnote1="注："
    footnote2=""
        
    #footnote3="贝塔系数基于日收益率，无风险利率为"+str(round(RF*100,4))+'%'
    footnote3="基于"+mktidx_name+"，回归期间为"+str(regression_period)+"个自然日。"

    import datetime; todaydt = datetime.date.today()
    footnote4="数据来源: 综合新浪/stooq/Yahoo，"+str(todaydt)+"统计"
    if footnote3 !='':
        footnotex=footnote1+footnote3+'\n'+footnote4
    else:
        footnotex=footnote4

    #绘图
    if graph:
        title_txt="CAPM贝塔系数："+ticker_name(ticker,ticker_type)
        y_label="贝塔系数"

        draw_lines(df1,y_label,x_label=footnotex, \
                   axhline_value=axhline_value,axhline_label=axhline_label, \
                   title_txt=title_txt,data_label=False, \
                        attention_value=attention_value,attention_value_area=attention_value_area, \
                        attention_point=attention_point,attention_point_area=attention_point_area, \
                            band_area=band_area, \
                   annotate=annotate,annotate_value=annotate, \
                   mark_top=mark_top,mark_bottom=mark_bottom, \
                   mark_start=mark_start,mark_end=mark_end, \
                   facecolor=facecolor,loc=loc,precision=4)
            
    return df


#==============================================================================
# 合成函数
#==============================================================================
if __name__=='__main__':
    ticker="600519.SS"
    ticker=["600519.SS","000858.SZ"]
    ticker={'Market':('US','^SPX','中概教培组合'),'EDU':0.5,'TAL':0.3,'TEDU':0.2}
    
    start="2024-1-1"; end="2024-3-20"
    
    RF=0.01759
    RF=[0.005,0.01759,0.05]
    
    regression_period=365
    
    graph=True
    annotate=False
    source='auto'
    
    betas=compare_beta_security(ticker,start,end,RF)

def compare_beta(ticker,start,end, \
                          adjust='qfq', \
                          RF=0,regression_period=365, \
                            attention_value='',attention_value_area='', \
                            attention_point='',attention_point_area='', \
                                band_area='', \
                          graph=True,facecolor='whitesmoke', \
                          annotate=False,annotate_value=False, \
                          mark_high=False,mark_low=False, \
                          mark_start=False,mark_end=False, \
                          mktidx='auto',source='auto', \
                          ticker_type='auto',loc="best"):
    """
    功能：组合情况，可能多只股票、多个投资组合或投资组合与股票的混合，多个无风险收益率
    
    """
    df=compare_beta_security(ticker=ticker,start=start,end=end, \
                adjust=adjust, \
                RF=RF,regression_period=regression_period, \
                  attention_value=attention_value,attention_value_area=attention_value_area, \
                  attention_point=attention_point,attention_point_area=attention_point_area, \
                      band_area=band_area, \
                graph=graph,facecolor=facecolor, \
                annotate=annotate,annotate_value=annotate_value, \
                mark_top=mark_high,mark_bottom=mark_low, \
                mark_start=mark_start,mark_end=mark_end, \
                mktidx=mktidx,source=source, \
                ticker_type=ticker_type,loc=loc)
    
    
def compare_beta_security(ticker,start,end, \
                          adjust='qfq', \
                          RF=0,regression_period=365, \
                            attention_value='',attention_value_area='', \
                            attention_point='',attention_point_area='', \
                                band_area='', \
                          graph=True,power=0,facecolor='whitesmoke', \
                          annotate=False,annotate_value=False, \
                          mark_top=False,mark_bottom=False, \
                          mark_start=False,mark_end=False, \
                          mktidx='auto',source='auto', \
                          ticker_type='auto',loc="best"):
    """
    功能：组合情况，可能多只股票、多个投资组合或投资组合与股票的混合，多个无风险收益率
    
    """
    
    #情形1：多个证券
    if isinstance(ticker,list):
        if len(ticker) > 1:
            if isinstance(RF,list):
                RF=RF[0]  
                
            df=compare_mticker_1beta(ticker,start,end, \
                                     adjust=adjust, \
                                     RF=RF,regression_period=regression_period, \
                                        attention_value=attention_value,attention_value_area=attention_value_area, \
                                        attention_point=attention_point,attention_point_area=attention_point_area, \
                                            band_area=band_area, \
                                     graph=graph,facecolor=facecolor,loc=loc, \
                                     annotate=annotate,annotate_value=annotate, \
                                     mark_top=mark_top,mark_bottom=mark_bottom, \
                                     mark_start=mark_start,mark_end=mark_end, \
                                     mktidx=mktidx,source=source, \
                                     ticker_type=ticker_type)
            return df
        else:
            #实际上是单个证券
            ticker=ticker[0]                
    
    #情形2：1只证券，多个RF。时间区间要尽可能短，不然难以看出差异！
    if isinstance(RF,list):
        if len(RF) > 1:
            df=compare_1ticker_mRF(ticker,start,end, \
                                   adjust=adjust, \
                                   RF=RF,regression_period=regression_period, \
                                        attention_value=attention_value,attention_value_area=attention_value_area, \
                                        attention_point=attention_point,attention_point_area=attention_point_area, \
                                            band_area=band_area, \
                                   graph=graph,facecolor=facecolor,loc=loc, \
                                   annotate=annotate,annotate_value=annotate, \
                                   mark_top=mark_top,mark_bottom=mark_bottom, \
                                   mark_start=mark_start,mark_end=mark_end, \
                                   mktidx=mktidx,source=source, \
                                   ticker_type=ticker_type)
            return df
        else:
            #实际上是单个RF
            RF=RF[0]       
    
    #情形3：1只证券，多个回归天数
    if isinstance(regression_period,list):
        if len(regression_period) > 1:
            df=compare_1ticker_mregression_period(ticker,start,end, \
                                     adjust=adjust, \
                                     RF=RF,regression_period=regression_period, \
                                        attention_value=attention_value,attention_value_area=attention_value_area, \
                                        attention_point=attention_point,attention_point_area=attention_point_area, \
                                            band_area=band_area, \
                                     graph=graph,facecolor=facecolor,loc=loc, \
                                     annotate=annotate,annotate_value=annotate, \
                                     mark_top=mark_top,mark_bottom=mark_bottom, \
                                     mark_start=mark_start,mark_end=mark_end, \
                                     mktidx=mktidx,source=source, \
                                     ticker_type=ticker_type)
            return df
        else:
            #实际上是单个regression_period
            regression_period=regression_period[0]  
            
    #情形4：1只证券，1个RF，1个回归天数?
    df=compare_mticker_1beta(ticker,start,end, \
                             adjust=adjust, \
                             RF=RF,regression_period=regression_period, \
                                attention_value=attention_value,attention_value_area=attention_value_area, \
                                attention_point=attention_point,attention_point_area=attention_point_area, \
                                    band_area=band_area, \
                             graph=graph,power=power,facecolor=facecolor,loc=loc, \
                             annotate=annotate,annotate_value=annotate, \
                             mark_top=mark_top,mark_bottom=mark_bottom, \
                             mark_start=mark_start,mark_end=mark_end, \
                             mktidx=mktidx,source=source, \
                             ticker_type=ticker_type)
        
    return df


#==============================================================================
#==============================================================================

#==============================================================================
#==============================================================================
#==============================================================================
#==============================================================================
#==============================================================================
