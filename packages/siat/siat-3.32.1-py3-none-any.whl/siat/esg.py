# -*- coding: utf-8 -*-
"""
本模块功能：提供全球股票ESG信息
所属工具包：证券投资分析工具SIAT 
SIAT：Security Investment Analysis Tool
创建日期：2019年8月18日
最新修订日期：2020年7月25日
作者：王德宏 (WANG Dehong, Peter)
作者单位：北京外国语大学国际商学院
版权所有：王德宏
用途限制：仅限研究与教学使用，不可商用！商用需要额外授权。
特别声明：作者不对使用本工具进行证券投资导致的任何损益负责！
"""
#==============================================================================
#屏蔽所有警告性信息
import warnings; warnings.filterwarnings('ignore')
from siat.common import *
from siat.translate import *
from siat.grafix import *
#==============================================================================
#==============================================================================
#以下使用yfinance数据源
#==============================================================================
def get_esg(stocklist):
    """
    功能：根据股票代码列表，抓取企业最新的可持续性发展ESG数据
    输入参数：
    stocklist：股票代码列表，例如单个股票["AAPL"], 多只股票["AAPL","MSFT","GOOG"]
    输出参数：    
    企业最新的可持续性发展ESG数据，数据框
    """
        
    #引用插件
    try:
        import yfinance as yf
    except:
        print("#Error(get_esg), need plugin: yfinance")
        print("   Solution: open Anaconda Prompt, type in command \"pip install yfinance\", Enter!")
        return None
    tickerlist=stocklist.copy()
    
    #测试数据，使用后请注释掉
    """
    tickerlist=["PDD","MSFT","BABA","JD","GOOG"]
    """

    #处理股票列表中的第一只股票，跳过无数据的项目
    skiplist=[]
    for t in tickerlist:
        tp=yf.Ticker(t)        
        try:
            print("...正在搜索ESG信息:",t,"...",end='')
            sst=tp.sustainability
            sst.rename(columns={'Value':t},inplace=True)
            sstt=sst.T            
        except: #本项目无数据，进入下一次循环
            print("未找到:-(")
            skiplist=skiplist+[t]
            continue
        skiplist=skiplist+[t]
        print("完成!")
        break

    #仅保留尚未处理的项目
    for t in skiplist: tickerlist.remove(t)
    
    #处理股票列表中的其他股票    
    for t in tickerlist:
        #print("---stock:",t)
        tp=yf.Ticker(t)        
        try: 
            print("...正在搜索ESG信息:",t,"...",end='')
            sst1=tp.sustainability
            sst1.rename(columns={'Value':t},inplace=True)
        except: 
            print("未找到:-(")
            continue #未抓取到数据
        sst1t=sst1.T
        try:
            sstt=sstt.append([sst1t])
        except:
            sstt=sstt._append([sst1t])
        print("完成!")
    
    try:
        if len(sstt)==0: return None
    except:
        return None
    
    #只保留需要的列
    sust=sstt[['totalEsg','percentile','esgPerformance','environmentScore', \
               'environmentPercentile','socialScore','socialPercentile', \
               'governanceScore','governancePercentile','peerGroup','peerCount']].copy()
    sust.rename(columns={'totalEsg':'ESGscore','percentile':'ESGpercentile', \
            'esgPerformance':'ESGperformance','environmentScore':'EPscore', \
               'environmentPercentile':'EPpercentile','socialScore':'CSRscore', \
               'socialPercentile':'CSRpercentile','governanceScore':'CGscore', \
               'governancePercentile':'CGpercentile', \
               'peerGroup':'Peer Group','peerCount':'Count'},inplace=True)
    
    return sust

if __name__ =="__main__":
    stocklist=["VIPS","BABA","JD","MSFT","WMT"]
    sust=get_esg(stocklist)


#==============================================================================
def print_esg(sustainability,option="ESG"):
    """
    功能：显示企业的可持续性发展数据
    输入参数：
    sustainability：抓取到的企业可持续性数据框
    输出参数：无    
    """
    
    if not (option in ['ESG','EP','CSR','CG']):
        print("...Error 01(print_sustainability): only ESG/EP/CSR/CG are valid")
        return
    
    import datetime as dt
    today=dt.date.today()
    s=sustainability.copy()
    
    #修改评级为中文
    s['ESGperformance']=s['ESGperformance'].apply(lambda x: "高" if x=='OUT_PERF' else x)
    s['ESGperformance']=s['ESGperformance'].apply(lambda x: "中" if x=='AVG_PERF' else x)
    
    #列改中文名，并删除含0的无效列
    colnames=list(s)
    for c in colnames:
        if len(s[s[c]==0]) >= 1:
            del s[c]; continue
        s.rename(columns={c:ectranslate(c)},inplace=True)
    
    #打印输出对齐
    import pandas as pd
    pd.set_option('display.unicode.ambiguous_as_wide', True)
    pd.set_option('display.unicode.east_asian_width', True)
    pd.set_option('display.width', 180) # 设置打印宽度(**重要**)
    
    #显示分数和分位数
    colnames=list(s)
    printnames=[]
    if option=="ESG":
        s=s.sort_values([ectranslate('ESGscore')],ascending=False)
        esgnames=[ectranslate('ESGscore'),ectranslate('ESGperformance'), \
                  ectranslate('ESGpercentile'),ectranslate('Peer Group')]
        for i in esgnames:
            if i in colnames: printnames=printnames+[i]
        print("\n=== 企业发展可持续性：ESG综合风险 ===\n")
        print(s[printnames])
        print("来源: 雅虎财经,",str(today))

    if option=="EP":
        s=s.sort_values([ectranslate('EPscore')],ascending=False)
        esgnames=[ectranslate('EPscore'), \
                  ectranslate('EPpercentile'),ectranslate('Peer Group')]
        for i in esgnames:
            if i in colnames: printnames=printnames+[i]
        print("\n=== 企业发展可持续性：环保风险指数 ===\n")
        print(s[printnames])
        print("来源: 雅虎财经,",str(today))

    if option=="CSR":
        s=s.sort_values([ectranslate('CSRscore')],ascending=False)
        esgnames=[ectranslate('CSRscore'), \
                  ectranslate('CSRpercentile'),ectranslate('Peer Group')]
        for i in esgnames:
            if i in colnames: printnames=printnames+[i]
        print("\n=== 企业发展可持续性：社会责任风险指数 ===\n")
        print(s[printnames])
        print("来源: 雅虎财经,",str(today))

    if option=="CG":
        s=s.sort_values([ectranslate('CGscore')],ascending=False)
        esgnames=[ectranslate('CGscore'), \
                  ectranslate('CGpercentile'),ectranslate('Peer Group')]
        for i in esgnames:
            if i in colnames: printnames=printnames+[i]
        print("\n=== 企业发展可持续性：公司治理风险指数 ===\n")
        print(s[printnames])
        print("来源: 雅虎财经,",str(today))
    
    return

if __name__ =="__main__":
    print_esg(sust,option="ESG")
    print_esg(sust,option="EP")
    print_esg(sust,option="CSR")
    print_esg(sust,option="CG")
    print_esg(sust,option="ABC")


    
#==============================================================================
def ploth_esg(sustainability,option="ESG"):
    """
    功能：绘制ESG水平直方图
    输入参数：抓取到的企业可持续性数据框sustainability；选项option。
    输出参数：无    
    """
        
    if not (option in ['ESG','EP','CSR','CG']):
        print("...Error 01(ploth_esg): only ESG/EP/CSR/CG are valid")
        return
        
    s=sustainability.copy()
    import datetime as dt; today=dt.date.today()
    footnote="注：数值越小，风险越低。来源：雅虎财经，"+str(today)

    #绘制分数和分位数图     
    if option=="ESG":
        #排序
        s=s.sort_values(['ESGscore'],ascending=True)    
        titletxt1="企业发展可持续性：ESG综合风险指数"
        plot_barh(s,'ESGscore',titletxt1,footnote)
        titletxt2="企业发展可持续性：ESG综合风险行业分位数%"
        plot_barh(s,'ESGpercentile',titletxt2,footnote)

    if option=="EP":
        s=s.sort_values(['EPscore'],ascending=True)        
        titletxt="企业发展可持续性：环保风险指数"
        plot_barh(s,'EPscore',titletxt,footnote)

    if option=="CSR":
        s=s.sort_values(['CSRscore'],ascending=True)        
        titletxt="企业发展可持续性：社会责任风险指数"
        plot_barh(s,'CSRscore',titletxt,footnote) 

    if option=="CG":
        s=s.sort_values(['CGscore'],ascending=True)        
        titletxt="企业发展可持续性：公司治理风险指数"
        plot_barh(s,'CGscore',titletxt,footnote)  
        
    return 

if __name__ =="__main__":
    ploth_esg(sust,option="ESG")
    ploth_esg(sust,option="EP")
    ploth_esg(sust,option="CSR")
    ploth_esg(sust,option="CG")

#==============================================================================
def esg(stocklist):
    """
    功能：抓取、打印和绘图企业的可持续性发展数据，演示用
    输入参数：
    stocklist：股票代码列表，例如单个股票["AAPL"], 多只股票["AAPL","MSFT","GOOG"]
    输出参数：    
    企业最新的可持续性发展数据，数据框    
    """
        
    #抓取数据
    try:
        sust=get_esg(stocklist)
    except:
        print("#Error(esg), fail to get ESG data for",stocklist)
        return None
    if sust is None:
        print("#Error(esg), fail to get ESG data for",stocklist)
        return None
        
    #处理小数点
    from pandas.api.types import is_numeric_dtype
    cols=list(sust)    
    for c in cols:
        if is_numeric_dtype(sust[c]):
            sust[c]=round(sust[c],2)        
    
    #打印和绘图ESG
    ploth_esg(sust,option="ESG")
    print_esg(sust,option="ESG")
    #打印和绘图EP
    ploth_esg(sust,option="EP")
    print_esg(sust,option="EP")
    #打印和绘图CSR
    ploth_esg(sust,option="CSR")
    print_esg(sust,option="CSR")
    #打印和绘图CG
    ploth_esg(sust,option="CG")
    print_esg(sust,option="CG")

    return sust

if __name__ =="__main__":
    stocklist1=["AMZN","EBAY","BABA"]
    sust1=esg(stocklist1)
    stocklist2=["AMZN","EBAY","BABA","JD","VIPS","WMT"]
    sust2=esg(stocklist2)    

#==============================================================================
def portfolio_esg(portfolio):
    """
    功能：抓取、打印和绘图投资组合portfolio的可持续性发展数据，演示用
    输入参数：
    企业最新的可持续性发展数据，数据框    
    """
    #解构投资组合
    _,_,stocklist,_,ticker_type=decompose_portfolio(portfolio)
    
    #抓取数据
    try:
        sust=get_esg(stocklist)
    except:
        print("#Error(portfolio_esg), fail to get ESG data for",stocklist)
        return None
    if sust is None:
        #print("#Error(portfolio_esg), fail to get ESG data for",stocklist)
        return None
        
    #处理小数点
    from pandas.api.types import is_numeric_dtype
    cols=list(sust)    
    for c in cols:
        if is_numeric_dtype(sust[c]):
            sust[c]=round(sust[c],2)        
            
    #显示结果
    print("\n***** Portfolio ESG Risk *****")
    print("Portfolio:",stocklist)
    #显示各个成分股的ESG分数
    sust['Stock']=sust.index
    esgdf=sust[['Stock','ESGscore','EPscore','CSRscore','CGscore']]
    print(esgdf.to_string(index=False))
    
    print("\nPortfolio ESG Evaluation:")
    #木桶短板：EPScore
    esg_ep=esgdf.sort_values(['EPscore'], ascending = True)
    p_ep=esg_ep['EPscore'][-1]
    p_ep_stock=esg_ep.index[-1]   
    str_ep="   EP score (from "+str(p_ep_stock)+")"
    len_ep=len(str_ep)

    #木桶短板：CSRScore
    esg_csr=esgdf.sort_values(['CSRscore'], ascending = True)
    p_csr=esg_csr['CSRscore'][-1]
    p_csr_stock=esg_csr.index[-1] 
    str_csr="   CSR score (from "+str(p_csr_stock)+")"
    len_csr=len(str_csr)
    
    #木桶短板：CGScore
    esg_cg=esgdf.sort_values(['CGscore'], ascending = True)
    p_cg=esg_cg['CGscore'][-1]
    p_cg_stock=esg_cg.index[-1]     
    str_cg="   CG score (from "+str(p_cg_stock)+")"
    len_cg=len(str_cg)

    str_esg="   Overall ESG score"
    len_esg=len(str_esg)
    
    #计算对齐冒号中间需要的空格数目
    len_max=max(len_ep,len_csr,len_cg,len_esg)
    str_ep=str_ep+' '*(len_max-len_ep+1)+':'
    str_csr=str_csr+' '*(len_max-len_csr+1)+':'
    str_cg=str_cg+' '*(len_max-len_cg+1)+':'
    str_esg=str_esg+' '*(len_max-len_esg+1)+':'
    
    #对齐打印
    print(str_ep,p_ep)
    print(str_csr,p_csr)    
    print(str_cg,p_cg)      
    #计算投资组合的ESG综合风险
    p_esg=round(p_ep+p_csr+p_cg,2)
    print(str_esg,p_esg)

    import datetime as dt; today=dt.date.today()
    footnote="The higher the score, the higher the risk. \
        \nSource: Yahoo Finance, "+str(today)
    print(footnote)
    
    return p_esg

if __name__ =="__main__":
    #market={'Market':('China','^HSI')}
    market={'Market':('US','^GSPC')}
    #stocks={'0939.HK':2,'1398.HK':1,'3988.HK':3}
    stocks={'VIPS':3,'JD':2,'BABA':1}
    portfolio=dict(market,**stocks)
    esg=portfolio_esg(portfolio)
#==============================================================================
#==============================================================================
#==============================================================================
#==============================================================================
#====以下使用yahooquery数据源===================================================
if __name__ =="__main__":
    stocklist=["BAC", "TD","PNC"]
    
def get_esg2(stocklist):
    """
    功能：根据股票代码列表，抓取企业最新的可持续性发展ESG数据
    输入参数：
    stocklist：股票代码列表，例如单个股票["AAPL"], 多只股票["AAPL","MSFT","GOOG"]
    输出参数：    
    企业最新的可持续性发展ESG数据，数据框
    """
    
    import pandas as pd
    collist=['symbol','totalEsg','environmentScore','socialScore','governanceScore']
    sust=pd.DataFrame(columns=collist)
    for t in stocklist:
        try:
            info=stock_info(t).T
        except:
            print("#Error(get_esg2): esg info not available for",t)
            continue
        if (info is None) or (len(info)==0):
            print("#Error(get_esg2): failed to get esg info for",t)
            continue
        sub=info[collist]
        sust=pd.concat([sust,sub])
    
    newcols=['Stock','ESGscore','EPscore','CSRscore','CGscore']
    sust.columns=newcols
    """
    sust=sust.rename(columns={'symbol':'Stock','totalEsg':'ESGscore', \
                         'environmentScore':'EPscore', \
                             'socialScore':'CSRscore', \
                                 'governanceScore':'CGscore'})
    """
    sust.set_index('Stock',inplace=True)
    
    return sust

if __name__ =="__main__":
    stocklist=["VIPS","BABA","JD","MSFT","WMT"]
    sust=get_esg(stocklist)

#==============================================================================
if __name__ =="__main__":
    market={'Market':('China','^HSI')}
    stocks={'0700.HK':3,'9618.HK':2,'9988.HK':1}
    portfolio=dict(market,**stocks)

def portfolio_esg2(portfolio):
    """
    功能：抓取、打印和绘图投资组合portfolio的可持续性发展数据，演示用
    输入参数：
    企业最新的可持续性发展数据，数据框    
    """
    #解构投资组合
    _,_,stocklist,_,ticker_type=decompose_portfolio(portfolio)
    
    #抓取数据
    try:
        sust=get_esg2(stocklist)
    except:
        print("#Error(portfolio_esg), fail to get ESG data for",stocklist)
        return None
    if sust is None:
        #print("#Error(portfolio_esg), fail to get ESG data for",stocklist)
        return None
        
    #处理小数点
    from pandas.api.types import is_numeric_dtype
    cols=list(sust)    
    for c in cols:
        if is_numeric_dtype(sust[c]):
            sust[c]=round(sust[c],2)        
            
    #显示结果
    print("\n***** Portfolio ESG Risk *****")
    print("Portfolio:",stocklist)
    #显示各个成分股的ESG分数
    sust['Stock']=sust.index
    esgdf=sust[['Stock','ESGscore','EPscore','CSRscore','CGscore']]
    print(esgdf.to_string(index=False))
    
    print("\nPortfolio ESG Evaluation:")
    #木桶短板：EPScore
    esg_ep=esgdf.sort_values(['EPscore'], ascending = True)
    p_ep=esg_ep['EPscore'][-1]
    p_ep_stock=esg_ep.index[-1]   
    str_ep="   EP score (from "+str(p_ep_stock)+")"
    len_ep=len(str_ep)

    #木桶短板：CSRScore
    esg_csr=esgdf.sort_values(['CSRscore'], ascending = True)
    p_csr=esg_csr['CSRscore'][-1]
    p_csr_stock=esg_csr.index[-1] 
    str_csr="   CSR score (from "+str(p_csr_stock)+")"
    len_csr=len(str_csr)
    
    #木桶短板：CGScore
    esg_cg=esgdf.sort_values(['CGscore'], ascending = True)
    p_cg=esg_cg['CGscore'][-1]
    p_cg_stock=esg_cg.index[-1]     
    str_cg="   CG score (from "+str(p_cg_stock)+")"
    len_cg=len(str_cg)

    str_esg="   Overall ESG score"
    len_esg=len(str_esg)
    
    #计算对齐冒号中间需要的空格数目
    len_max=max(len_ep,len_csr,len_cg,len_esg)
    str_ep=str_ep+' '*(len_max-len_ep+1)+':'
    str_csr=str_csr+' '*(len_max-len_csr+1)+':'
    str_cg=str_cg+' '*(len_max-len_cg+1)+':'
    str_esg=str_esg+' '*(len_max-len_esg+1)+':'
    
    #对齐打印
    print(str_ep,p_ep)
    print(str_csr,p_csr)    
    print(str_cg,p_cg)      
    #计算投资组合的ESG综合风险
    p_esg=round(p_ep+p_csr+p_cg,2)
    print(str_esg,p_esg)

    import datetime as dt; today=dt.date.today()
    footnote="The higher the score, the higher the risk. \
        \nSource: Yahoo Finance, "+str(today)
    print(footnote)
    
    return p_esg

if __name__ =="__main__":
    #market={'Market':('China','^HSI')}
    market={'Market':('US','^GSPC')}
    #stocks={'0939.HK':2,'1398.HK':1,'3988.HK':3}
    stocks={'VIPS':3,'JD':2,'BABA':1}
    portfolio=dict(market,**stocks)
    esg=portfolio_esg(portfolio)
#==============================================================================

#==============================================================================










        