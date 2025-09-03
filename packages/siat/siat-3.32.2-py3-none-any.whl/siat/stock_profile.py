# -*- coding: utf-8 -*-
"""
本模块功能：
所属工具包：提供全球股票基本信息，初版 
SIAT：Security Investment Analysis Tool
创建日期：2020年1月16日
最新修订日期：2020年2月4日
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
#以下使用雅虎财经数据源
#==============================================================================
if __name__ =="__main__":
    ticker='AAPL'
    ticker='1398.HK'
    ticker='601398.SS'
    ticker='000002.SZ'
    
    option='basic'
    option='financial'
    option='market'


def profile(ticker,option="basic"):
    """
    功能：显示企业基本信息
    输入：股票代码
    输出：企业基本信息
    """
    print(".....Searching for company profile of",ticker,".....")
    
    if not(option in ["basic","financial","market"]):
        print(".....Valid options: basic, financial, market")
        return None
    
    import datetime as dt
    today=dt.date.today()
    
    import yfinance as yf
    firm=yf.Ticker(ticker)

    # get stock info
    try:
        i=firm.info
    except:
        print("Stock code not found:",ticker)
        return None
    
    if option == "basic":
        print("\n=== Corporate Profile - Basics ===")
        print("Today:",today)
        
        print('Company Name:',i['shortName'])
        print('Stock Code:',i['symbol'])
        print('Trading Currency:',i['currency'])

        print('Sector:',i['sector'])
        print('Industry:',i['industry'])
        
        print('Company Location:',i['city']+', '+i['country'])
        try: addr2=i['address2']
        except: addr2=""
        print('Company Address:',i['address1']+', '+addr2)
        try:    
            print('Head Office Phone:',i['phone'])
        except: pass
        print('Website:',i['website'])
        
        try:
            print('Full Time Employees:',format(i['fullTimeEmployees'],'0,d'))
        except: pass
    
        try:
            print('Green Finance(ESG Population):',i['isEsgPopulated'])
        except: pass

        print('Exchange Code:',i['exchange'])
        print('Exchange City:',i['exchangeTimezoneName'])

    if option == "financial":
        print("\n=== Corporate Profile - Financials ===")
        print("Today:",today)
        print('Company Name:',i['shortName'])        
        #print('Dividend Yield:',i['dividendYield'])
        #print('Trailing Annual Dividend Yield:',i['trailingAnnualDividendYield'])                
        #print('5-year Avg Dividend Yield:',i['fiveYearAvgDividendYield'])
        
        print('Dividend Rate('+i['currency']+'):',i['dividendRate'])
        print('Trailing Annual Dividend Rate:',i['trailingAnnualDividendRate'])    
        
        """
        注意：百分比的两种不同打印方法
        {:.2%}无需事先乘以100
        {:.2f}%需事先乘以100
        """
        print('Dividend Yield: {:.2%}'.format(i['dividendYield']))
        print('Trailing Annual Dividend Yield: {:.2%}'.format(i['trailingAnnualDividendYield']))
        print('5-year Average Dividend Yield: {:.2f}%'.format(i['fiveYearAvgDividendYield']))
        
        print('Payout Ratio: {:.2%}'.format(i['payoutRatio']))
        
        print('Trailing PE:',round(i['trailingPE'],2))
        print('Forward PE:',round(i['forwardPE'],2))
        
        print('Trailing EPS:',round(i['trailingEps'],2))
        print('Forward EPS:',round(i['forwardEps'],2))
        
        print('Profit Margins: {:.2%}'.format(i['profitMargins']))
        print('Earnings Quarterly Growth: {:.2%}'.format(i['earningsQuarterlyGrowth']))
        
        print('Price To Sales TTM:',round(i['priceToSalesTrailing12Months'],2))   
        
        evr=i['enterpriseToRevenue']
        if not ((evr < 0) or (evr == None)):
            print('Enterprise To Revenue:',round(evr,2))        
        
        evebitda=i['enterpriseToEbitda']
        if not (evebitda is None):
            print('Enterprise To EBITDA:',round(evebitda,2))
        print('Price To Book:',round(i['priceToBook'],2))
        
        nitc=int(i['netIncomeToCommon']/1000000)
        print('Net Income to Common(million):',format(nitc,'0,d'))

    if option == "market":
        print("\n=== Corporate Profile - Market ===")
        print("Today:",today)
        print('Company Name:',i['shortName'])    
        print('Stock Code:',i['symbol'])
        print('Currency:',i['currency'])
        
        som=int(i['sharesOutstanding']/1000000)
        print('Shares Outstanding(million):',format(som,'0,d'))
        
        """
        Float shares=Shares outstanding - Shares held by company insiders and 
        controlling shareholders
        """
        #fsm=int(i['floatShares']/1000000)
        #print('Float Shares(million):',fsm)        
        
        #mktcap=int(i['marketCap']/1000000)
        #print('Market Capitalization(million):',format(mktcap,'0,d'))       
        
        try:
            print('Beta:',round(i['beta'],2))        
        except: pass
        print('Previous Close Price:',i['previousClose'])
        print('50-day Average Price:',round(i['fiftyDayAverage'],2))
        print('200-day Average Price:',round(i['twoHundredDayAverage'],2))                
        
        print('52-week High:',i['fiftyTwoWeekHigh'])
        print('52-week Low:',i['fiftyTwoWeekLow'])
        if not (i['heldPercentInstitutions'] is None):
            print('Held by Institutions: {:.4%}'.format(i['heldPercentInstitutions']))
        if not (i['heldPercentInsiders'] is None):
            print('Held by Insiders: {:.4%}'.format(i['heldPercentInsiders']))
        #print('Short% Of Float:',i['shortPercentOfFloat'])
    
    return i

if __name__ =="__main__":
    info=profile("600519.SS")
    info=profile("MSFT",option="market")
    info=profile("MSFT",option="financial")
    info=profile("600519.SS",option="financial")
    info=profile("0700.HK",option="financial")
    info=profile("TCS.NS",option="market")
    info=profile("BMW.DE",option="financial")

#==============================================================================
def get_sustainability(stocklist):
    """
    功能：根据股票代码列表，抓取企业最新的可持续性发展数据
    输入参数：
    stocklist：股票代码列表，例如单个股票["AAPL"], 多只股票["AAPL","MSFT","GOOG"]
    输出参数：    
    企业最新的可持续性发展数据，数据框
    """
        
    #引用插件
    import yfinance as yf
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
            print("...Searching data for",t,"...",end='')
            sst=tp.sustainability
            sst.rename(columns={'Value':t},inplace=True)
            sstt=sst.T            
        except: #本项目无数据，进入下一次循环
            print(", not found:-(")
            skiplist=skiplist+[t]
            continue
        skiplist=skiplist+[t]
        print(", done!")
        break

    #仅保留尚未处理的项目
    for t in skiplist: tickerlist.remove(t)
    
    #处理股票列表中的其他股票    
    for t in tickerlist:
        #print("---stock:",t)
        tp=yf.Ticker(t)        
        try: 
            print("...Searching data for",t,"...",end='')
            sst1=tp.sustainability
            sst1.rename(columns={'Value':t},inplace=True)
        except: 
            print(", not found:-(")
            continue #未抓取到数据
        sst1t=sst1.T
        try:
            sstt=sstt.append([sst1t])
        except:
            sstt=sstt._append([sst1t])
        print(", done!")
    
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
    stocklist=["PDD","BABA","JD","GOOG","WMT"]
    sust=get_sustainability(stocklist)


#==============================================================================
def print_sustainability(sustainability,option="ESG"):
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
    
    #显示分数和分位数
    if option=="ESG":
        s=s.sort_values(['ESGscore'],ascending=False)
        print("\n=== Corporate Sustainability Performance ===")
        esg=s[['ESGscore','ESGpercentile','ESGperformance','Peer Group','Count']]
        print(esg)
        print("\nSource: Yahoo Finance,",str(today))

    if option=="EP":
        s=s.sort_values(['EPscore'],ascending=False)
        print("\n=== Corporate Environment Protection Performance ===")
        ep=s[['EPscore','EPpercentile','Peer Group','Count']]
        print(ep)
        print("\nSource: Yahoo Finance,",str(today))

    if option=="CSR":
        s=s.sort_values(['CSRscore'],ascending=False)
        print("\n=== Corporate Social Responsibility Performance ===")
        print(s[['CSRscore','CSRpercentile','Peer Group','Count']])
        print("\nSource: Yahoo Finance,",str(today))

    if option=="CG":
        s=s.sort_values(['CGscore'],ascending=False)
        print("\n=== Corporate Governance Performance ===")
        print(s[['CGscore','CGpercentile','Peer Group','Count']])
        print("\nSource: Yahoo Finance,",str(today))
    
    return

if __name__ =="__main__":
    print_sustainability(sust,option="ESG")
    print_sustainability(sust,option="EP")
    print_sustainability(sust,option="CSR")
    print_sustainability(sust,option="CG")
    print_sustainability(sust,option="ABC")
    
#==============================================================================
def ploth_sustainability(sustainability,option="ESG"):
    """
    功能：显示企业的可持续性发展数据
    输入参数：
    sustainability：抓取到的企业可持续性数据框
    输出参数：无    
    """
        
    if not (option in ['ESG','EP','CSR','CG']):
        print("...Error 01(plot_sustainability): only ESG/EP/CSR/CG are valid")
        return
        
    s=sustainability.copy()
    import matplotlib.pyplot as plt
    import datetime as dt
    today=dt.date.today()
    n=len(s)

    #绘制分数图     
    if option=="ESG":
        #排序
        s=s.sort_values(['ESGscore'],ascending=True)
    
        titletxt="Corporate Sustainability Performance"
        plt.title(titletxt,fontsize=16,fontweight='bold') 
    
        xlabeltxt1="Score"        
        xlabeltxt=xlabeltxt1+'\n('+"Source: Yahoo Finance, "+str(today)+")"
        font1 = {'family':'Times New Roman','weight':'normal','size':14,}     
        plt.xlabel(xlabeltxt,font1)
        
        if n < 6:
            graf=plt.barh(s.index,s['ESGscore'],facecolor='b',height=0.6,alpha=0.8)
        else:
            graf=plt.barh(s.index,s['ESGscore'],facecolor='b',alpha=0.8)  
            
        plt.gca().set_facecolor('whitesmoke')
        plt.show()

    if option=="EP":
        s=s.sort_values(['EPscore'],ascending=True)
        
        titletxt="Corporate Environment Protection Performance"
        plt.title(titletxt,fontsize=13,fontweight='bold') 
    
        xlabeltxt1="Score"        
        xlabeltxt=xlabeltxt1+'\n('+"Source: Yahoo Finance, "+str(today)+")"
        font1 = {'family':'Times New Roman','weight':'normal','size':14,}     
        plt.xlabel(xlabeltxt,font1)
        
        if n < 6:
            graf=plt.barh(s.index,s['EPscore'],facecolor='g',height=0.6,alpha=0.8)  
        else:
            graf=plt.barh(s.index,s['EPscore'],facecolor='g',alpha=0.8)
            
        plt.gca().set_facecolor('whitesmoke')
        plt.show()

    if option=="CSR":
        s=s.sort_values(['CSRscore'],ascending=True)
        
        titletxt="Corporate Social Responsibility Performance"
        plt.title(titletxt,fontsize=13,fontweight='bold') 
    
        xlabeltxt1="Score"        
        xlabeltxt=xlabeltxt1+'\n('+"Source: Yahoo Finance, "+str(today)+")"
        font1 = {'family':'Times New Roman','weight':'normal','size':14,}     
        plt.xlabel(xlabeltxt,font1)
        
        if n < 6:
            graf=plt.barh(s.index,s['CSRscore'],facecolor='tan',height=0.6,alpha=0.8)
        else:
            graf=plt.barh(s.index,s['CSRscore'],facecolor='tan',alpha=0.8)  
            
        plt.gca().set_facecolor('whitesmoke')
        plt.show()

    if option=="CG":
        s=s.sort_values(['CGscore'],ascending=True)
        
        titletxt="Corporate Governance Performance"
        plt.title(titletxt,fontsize=16,fontweight='bold') 
    
        xlabeltxt1="Score"        
        xlabeltxt=xlabeltxt1+'\n('+"Source: Yahoo Finance, "+str(today)+")"
        font1 = {'family':'Times New Roman','weight':'normal','size':14,}     
        plt.xlabel(xlabeltxt,font1)
        
        if n < 6:
            graf=plt.barh(s.index,s['CGscore'],facecolor='y',height=0.6,alpha=0.9)
        else:
            graf=plt.barh(s.index,s['CGscore'],facecolor='y',alpha=0.9)  
            
        plt.gca().set_facecolor('whitesmoke')
        plt.show()
    
    #绘制分位数图     
    if option=="ESG":
        #排序
        s=s.sort_values(['ESGpercentile'],ascending=True)
    
        titletxt="Corporate Sustainability Performance"
        plt.title(titletxt,fontsize=16,fontweight='bold') 
    
        xlabeltxt1="Percentile in industrial sector"        
        xlabeltxt=xlabeltxt1+'\n('+"Source: Yahoo Finance, "+str(today)+")"
        font1 = {'family':'Times New Roman','weight':'normal','size':14,}     
        plt.xlabel(xlabeltxt,font1)
        
        if n < 6:
            graf=plt.barh(s.index,s['ESGpercentile'],facecolor='b',height=0.6,alpha=0.8)
        else:
            graf=plt.barh(s.index,s['ESGpercentile'],facecolor='b',alpha=0.8)  
            
        plt.gca().set_facecolor('whitesmoke')
        plt.show()

    if option=="EP":
        s=s.sort_values(['EPpercentile'],ascending=True)
        
        titletxt="Corporate Environment Protection Performance"
        plt.title(titletxt,fontsize=13,fontweight='bold') 
    
        xlabeltxt1="Percentile in industrial sector"        
        xlabeltxt=xlabeltxt1+'\n('+"Source: Yahoo Finance, "+str(today)+")"
        font1 = {'family':'Times New Roman','weight':'normal','size':14,}     
        plt.xlabel(xlabeltxt,font1)
        
        if n < 6:
            graf=plt.barh(s.index,s['EPpercentile'],facecolor='g',height=0.6,alpha=0.8)
        else:
            graf=plt.barh(s.index,s['EPpercentile'],facecolor='g',alpha=0.8)  
            
        plt.gca().set_facecolor('whitesmoke')
        plt.show()

    if option=="CSR":
        s=s.sort_values(['CSRpercentile'],ascending=True)
        
        titletxt="Corporate Social Responsibility Performance"
        plt.title(titletxt,fontsize=13,fontweight='bold') 
    
        xlabeltxt1="Percentile in industrial sector"        
        xlabeltxt=xlabeltxt1+'\n('+"Source: Yahoo Finance, "+str(today)+")"
        font1 = {'family':'Times New Roman','weight':'normal','size':14,}     
        plt.xlabel(xlabeltxt,font1)
        
        if n < 6:
            graf=plt.barh(s.index,s['CSRpercentile'],facecolor='tan',height=0.6,alpha=0.8)
        else:
            graf=plt.barh(s.index,s['CSRpercentile'],facecolor='tan',alpha=0.8)  
            
        plt.gca().set_facecolor('whitesmoke')
        plt.show()

    if option=="CG":
        s=s.sort_values(['CGpercentile'],ascending=True)
        
        titletxt="Corporate Governance Performance"
        plt.title(titletxt,fontsize=16,fontweight='bold') 
    
        xlabeltxt1="Percentile in industrial sector"        
        xlabeltxt=xlabeltxt1+'\n('+"Source: Yahoo Finance, "+str(today)+")"
        font1 = {'family':'Times New Roman','weight':'normal','size':14,}     
        plt.xlabel(xlabeltxt,font1)
        
        if n < 6:
            graf=plt.barh(s.index,s['CGpercentile'],facecolor='y',height=0.6,alpha=0.9)
        else:
            graf=plt.barh(s.index,s['CGpercentile'],facecolor='y',alpha=0.9)  
            
        plt.gca().set_facecolor('whitesmoke')
        plt.show()
        
    return 

if __name__ =="__main__":
    ploth_sustainability(sust,option="ESG")
    ploth_sustainability(sust,option="EP")
    ploth_sustainability(sust,option="CSR")
    ploth_sustainability(sust,option="CG")

#==============================================================================
def plot_sustainability(sustainability,option="ESG"):
    """
    功能：显示企业的可持续性发展数据，同时显示分数和分位数
    输入参数：
    sustainability：抓取到的企业可持续性数据框
    输出参数：无    
    """
        
    if not (option in ['ESG','EP','CSR','CG']):
        print("...Error 01(plot_sustainability): only ESG/EP/CSR/CG are valid")
        return
        
    s=sustainability.copy()
    
    import numpy as np
    import matplotlib.pyplot as plt
    #from matplotlib.ticker import MultipleLocator
    import datetime as dt
    
    today=dt.date.today()
    l=len(s.index)
    n=np.arange(l)
    if l < 6: width=0.45 #经验值，0.45*6=2.7
    else: width=round(2.9/l,2)
    #print("Firms:",s.index,", Width:",width)

    #fig,ax=plt.subplots(figsize=(10,6))
    fig,ax=plt.subplots(figsize=(12.8,6.4))

    #绘制分数和分位数图     
    if option=="ESG":
        s=s.sort_values(['ESGscore'],ascending=False)        
        
        b1=ax.bar(n-width/2,s['ESGscore'],width,tick_label=s.index,label='Score')
        b2=ax.bar(n+width/2,s['ESGpercentile'],width,label='Percentile (%)')

        plt.legend(loc='best')
        
        for b in b1+b2:
            h=b.get_height()
            ax.text(b.get_x()+b.get_width()/2,h,h,ha='center',va='bottom')
        
        fontlabel={'family':'Times New Roman','weight':'normal','size':16}
        plt.ylabel('ESG Index',fontlabel)
        plt.ylim(0,100)
        xlabeltxt='\n'+"Source: Yahoo Finance, "+str(today)
        plt.xlabel(xlabeltxt,fontlabel)
        
        titletxt="Corporate Sustainability Performance (ESG)"
        fonttitle={'family':'Times New Roman','weight':'normal','size':24}
        plt.title(titletxt,fonttitle) 
        
        plt.gca().set_facecolor('whitesmoke')
        plt.show()

    if option=="EP":
        s=s.sort_values(['EPscore'],ascending=False)        
        
        b1=ax.bar(n-width/2,s['EPscore'],width,tick_label=s.index,label='Score')
        b2=ax.bar(n+width/2,s['EPpercentile'],width,label='Percentile (%)')
        plt.legend(loc='best')
        
        for b in b1+b2:
            h=b.get_height()
            ax.text(b.get_x()+b.get_width()/2,h,h,ha='center',va='bottom')
        
        fontlabel={'family':'Times New Roman','weight':'normal','size':16}
        plt.ylabel('EP Index',fontlabel)
        plt.ylim(0,100)
        xlabeltxt='\n'+"Source: Yahoo Finance, "+str(today)
        plt.xlabel(xlabeltxt,fontlabel)
        
        titletxt="Corporate Environment Protection Performance (EP)"
        fonttitle={'family':'Times New Roman','weight':'normal','size':22}
        plt.title(titletxt,fonttitle) 
        
        plt.gca().set_facecolor('whitesmoke')
        plt.show()      

    if option=="CSR":
        s=s.sort_values(['CSRscore'],ascending=False)        
        
        b1=ax.bar(n-width/2,s['CSRscore'],width,tick_label=s.index,label='Score')
        b2=ax.bar(n+width/2,s['CSRpercentile'],width,label='Percentile (%)')
        plt.legend(loc='best')
        
        for b in b1+b2:
            h=b.get_height()
            ax.text(b.get_x()+b.get_width()/2,h,h,ha='center',va='bottom')
        
        fontlabel={'family':'Times New Roman','weight':'normal','size':16}
        plt.ylabel('CSR Index',fontlabel)
        plt.ylim(0,100)
        xlabeltxt='\n'+"Source: Yahoo Finance, "+str(today)
        plt.xlabel(xlabeltxt,fontlabel)
        
        titletxt="Corporate Social Responsibility Performance (CSR)"
        fonttitle={'family':'Times New Roman','weight':'normal','size':22}
        plt.title(titletxt,fonttitle) 
        
        plt.gca().set_facecolor('whitesmoke')
        plt.show()  

    if option=="CG":
        s=s.sort_values(['CGscore'],ascending=False)        
        
        b1=ax.bar(n-width/2,s['CGscore'],width,tick_label=s.index,label='Score')
        b2=ax.bar(n+width/2,s['CGpercentile'],width,label='Percentile (%)')
        plt.legend(loc='best')
        
        for b in b1+b2:
            h=b.get_height()
            ax.text(b.get_x()+b.get_width()/2,h,h,ha='center',va='bottom')
        
        fontlabel={'family':'Times New Roman','weight':'normal','size':16}
        plt.ylabel('CG Index',fontlabel)
        plt.ylim(0,100)
        xlabeltxt='\n'+"Source: Yahoo Finance, "+str(today)
        plt.xlabel(xlabeltxt,fontlabel)
        
        titletxt="Corporate Governance Performance (CG)"
        fonttitle={'family':'Times New Roman','weight':'normal','size':24}
        plt.title(titletxt,fonttitle) 
        
        plt.gca().set_facecolor('whitesmoke')
        plt.show()  
       
    return 

if __name__ =="__main__":
    plot_sustainability(sust,option="ESG")
    plot_sustainability(sust,option="EP")
    plot_sustainability(sust,option="CSR")
    plot_sustainability(sust,option="CG")
    
    stocklist2=["AMZN","EBAY","BABA","JD","VIPS","WMT"]
    sust2=get_sustainability(stocklist2)  
    plot_sustainability(sust2)
#==============================================================================
def sustainability(stocklist):
    """
    功能：抓取、打印和绘图企业的可持续性发展数据，演示用
    输入参数：
    stocklist：股票代码列表，例如单个股票["AAPL"], 多只股票["AAPL","MSFT","GOOG"]
    输出参数：    
    企业最新的可持续性发展数据，数据框    
    """
        
    #抓取数据
    sust=get_sustainability(stocklist)
    
    #打印和绘图ESG
    ploth_sustainability(sust,option="ESG")
    print_sustainability(sust,option="ESG")
    #打印和绘图EP
    ploth_sustainability(sust,option="EP")
    print_sustainability(sust,option="EP")
    #打印和绘图CSR
    ploth_sustainability(sust,option="CSR")
    print_sustainability(sust,option="CSR")
    #打印和绘图CG
    ploth_sustainability(sust,option="CG")
    print_sustainability(sust,option="CG")

    return sust

if __name__ =="__main__":
    stocklist1=["AMZN","EBAY","BABA"]
    sust1=sustainability(stocklist1)
    stocklist2=["AMZN","EBAY","BABA","JD","VIPS","WMT"]
    sust2=sustainability(stocklist2)    

#==============================================================================
#==============================================================================
def sustainability2(stocklist):
    """
    功能：抓取、打印和绘图企业的可持续性发展数据，演示用
    输入参数：
    stocklist：股票代码列表，例如单个股票["AAPL"], 多只股票["AAPL","MSFT","GOOG"]
    输出参数：    
    企业最新的可持续性发展数据，数据框    
    """
        
    #抓取数据
    sust=get_sustainability(stocklist)
    
    #打印和绘图ESG
    plot_sustainability(sust,option="ESG")
    print_sustainability(sust,option="ESG")
    #打印和绘图EP
    plot_sustainability(sust,option="EP")
    print_sustainability(sust,option="EP")
    #打印和绘图CSR
    plot_sustainability(sust,option="CSR")
    print_sustainability(sust,option="CSR")
    #打印和绘图CG
    plot_sustainability(sust,option="CG")
    print_sustainability(sust,option="CG")

    return sust

if __name__ =="__main__":
    stocklist1=["AMZN","EBAY","BABA"]
    sust1=sustainability2(stocklist1)
    stocklist2=["AMZN","EBAY","BABA","JD","VIPS","WMT"]
    sust2=sustainability2(stocklist2)   









        