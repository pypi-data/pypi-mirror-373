# -*- coding: utf-8 -*-
"""
本模块功能：数字货币及其MSA交易策略
所属工具包：证券投资分析工具SIAT 
SIAT：Security Investment Analysis Tool
创建日期：2018年9月19日
最新修订日期：2020年2月3日
作者：王德宏 (WANG Dehong, Peter)
作者单位：北京外国语大学国际商学院
版权所有：王德宏
用途限制：仅限研究与教学使用，不可商用！商用需要额外授权。
特别声明：作者不对使用本工具进行证券投资导致的任何损益负责！
"""

#关闭所有警告
import warnings; warnings.filterwarnings('ignore')
#引用Python插件 
from datetime import datetime
import numpy as np; import pandas as pd
#from scipy import stats
import json
from bs4 import BeautifulSoup; import requests
#==============================================================================
import matplotlib.pyplot as plt
#处理绘图汉字乱码问题
import sys; czxt=sys.platform
if czxt in ['win32','win64']:
    #设置绘图时的汉字显示
    #plt.rcParams['font.sans-serif'] = ['FangSong']  # 设置默认字体
    plt.rcParams['font.sans-serif'] = ['SimHei']  # 设置默认字体
if czxt in ['darwin']:
    plt.rcParams['font.sans-serif']=['Arial Unicode MS']
    #plt.rcParams['font.sans-serif']= ['Heiti TC']
# 解决保存图像时'-'显示为方块的问题
plt.rcParams['axes.unicode_minus'] = False 
#==============================================================================

#定义爬虫函数：抓取交易所信息
def fetchCrypto_Exchange(fsym,tsym,top=5):
    urlprefix="https://min-api.cryptocompare.com/data/top/exchanges/full?fsym="
    url      = urlprefix + fsym + "&tsym=" + tsym     
    headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }    
    
    response = requests.get(url,headers=headers)
    soup     = BeautifulSoup(response.content, "html.parser")
    dic      = json.loads(soup.prettify())

    #筛选可交易所选产品的交易所，并显示列表
    market = []
    d = dic['Data']['Exchanges']
    for i in range(len(d)):
        market.append(d[i]['MARKET'])

    #基于过去24小时内交易量进行交易所排名
    vol = []
    d = dic['Data']['Exchanges']
    for i in range(len(d)):
        volamt=round(float(d[i]['VOLUME24HOUR']),2)
        if volamt > 0:
            vol.append([d[i]['MARKET'], volamt])
 
    #基于子列表中的第二项对子列表排序
    vol = sorted(vol, key=lambda x: -x[1])
    
    #基于过去24小时交易量显示所选产品活跃的5个交易所名单
    print("\n全球最活跃的五家数字货币交易所：",fsym+"/"+tsym,"\n       (24小时交易金额，"+tsym+"百万)")
    for e in vol:
        print("%10s%15.2f" % (e[0], e[1]))
    import datetime as dt; nowtime=dt.datetime.now().strftime('%Y-%m-%d %H:%M')
    print("*数据来源：CryptoCompare,",nowtime)    
    #活跃交易所Top 5，markets
    markets = [e[0] for e in vol][0:top]
    """
    print("\n",markets,"\n")
    """
    return markets

if __name__=='__main__':
    fsym="ETH"
    tsym="USD"
    top=10
    markets=fetchCrypto_Exchange("ETH","USD")

#==============================================================================

#定义爬虫函数：从指定交易所抓取所选产品价格
#限制：考虑到网络传输量，一次抓取最多2000条交易（2000/365=5.5年最多）
def fetchCrypto_Price_byExchange(fsym, tsym, exchange):
    #数据源: https://www.cryptocompare.com/api/
    cols = ['date', 'timestamp', 'open', 'high', 'low', 'close']
    lst = ['time', 'open', 'high', 'low', 'close']
 
    timestamp_today = datetime.today().timestamp()
    curr_timestamp = timestamp_today
    
    headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    } 
    
    for j in range(2):
        df = pd.DataFrame(columns=cols)
        urlprefix="https://min-api.cryptocompare.com/data/histoday?fsym="
        url = urlprefix + fsym + \
              "&tsym=" + tsym + "&toTs=" + str(int(curr_timestamp)) + \
              "&limit=2000" + "&e=" + exchange
              
        response = requests.get(url,headers=headers)
        soup = BeautifulSoup(response.content, "html.parser")
        dic = json.loads(soup.prettify())        
        if len(dic['Data']) < 1:
            return None    #爬虫失败，返回空
        
        for i in range(1, 2001):
            tmp = []
            for e in enumerate(lst):
                x = e[0]; y = dic['Data'][i][e[1]]
                if(x == 0):
                    #将timestamp转换为日期
                    td = datetime.fromtimestamp(int(y)).strftime('%Y-%m-%d')
                    tmp.append(td)
                tmp.append(y)
            if(np.sum(tmp[-4::]) > 0):
                df.loc[len(df)] = np.array(tmp)
                
        df.index = pd.to_datetime(df.date)
        df.drop('date', axis=1, inplace=True)
        curr_timestamp = int(df.iloc[0][0])
 
        if(j == 0):
            df0 = df.copy()
        else:
            data = pd.concat([df, df0], axis=0)
 
    return data.astype(np.float64)

if __name__=='__main__':
    data=fetchCrypto_Price_byExchange("ETH", "USD", "Coinsbit")


#==============================================================================
def Crypto_Price_Trend(fsym, tsym, exchange,fromdate,todate,power=4):
    """
    功能：绘制价格趋势线
    fsym: 数字货币产品
    tsym: 交易币种
    exchange: 交易所
    
    """
    print("... Searching for information, please wait ...")
    
    #检查日期期间是否有效
    import siat.common as cmn
    result, start, end=cmn.check_period(fromdate, todate)
    if not result:
        print("#Error(Crypto_Price_Trend): invalid date period from",fromdate,'to',todate)
        return None

    #获得价格
    p=fetchCrypto_Price_byExchange(fsym, tsym, exchange)
    p1=p[p.index >= start]
    p2=p1[p1.index <= end]

    import siat.grafix as gfx        
    colname='close'
    collabel='收盘价'
    ylabeltxt='价格('+tsym+')'
    titletxt="数字货币价格趋势："+fsym+'/'+tsym+'，'+exchange
    import datetime as dt; nowtime=dt.datetime.now().strftime('%Y-%m-%d %H:%M')
    footnote="数据来源：CryptoCompare,"+str(nowtime)        
    
    import siat.grafix as g
    g.plot_line(p2,colname,collabel,ylabeltxt,titletxt,footnote,power=power)
    
    return p2

if __name__=='__main__':
    fsym="ETH"
    tsym="USD"
    exchange='Coinbase'
    fromdate='2020-7-1'
    todate='2020-12-31'
    power=3
    price=Crypto_Price_Trend(fsym, tsym, exchange,fromdate,todate,power)
#==============================================================================
def compCrypto_Price(product1,product2,days=30):
    """
    功能：比较两种数字货币的价格趋势，最近days天的情形
    输入：
    product1/product2：产品列表，格式：[数字货币价格数据框,产品,币种,市场]
    输出：
    绘制折线图
    无返回数据
    """
    
    #绘制折线图  
    label1=product1[1]+'/'+product1[2]+' @'+product1[3]
    p1=product1[0].tail(days)
    plt.plot(p1['close'],label=label1,lw=3)
    
    label2=product2[1]+'/'+product2[2]+' @'+product2[3]
    p2=product2[0].tail(days)
    plt.plot(p2['close'],label=label2,lw=3,ls=':')    

    #图示标题
    titletxt="数字货币产品：跨市场的价格套利机会"
    plt.title(titletxt,fontweight='bold')
    plt.ylabel("收盘价")
    plt.xticks(rotation=30)
    plt.legend(loc='best')
    
    plt.gca().set_facecolor('whitesmoke')
    plt.show()
    
    return    
    
if __name__=='__main__':
    prices1=fetchCrypto_Price_byExchange("ETH", "USD", "Coinsbit")
    product1=[prices1,"ETH", "USD", "Coinsbit"]
    prices2=fetchCrypto_Price_byExchange("ETH", "USD", "Coinbase")
    product2=[prices2,"ETH", "USD", "Coinbase"]
    compCrypto_Price(product1,product2)    


#==============================================================================
def compCrypto_Return(product1,product2,days=30):
    """
    功能：比较两种数字货币的收益率趋势，最近days天的情形
    输入：
    product1/product2：产品列表，格式：[数字货币价格数据框,产品,币种,市场]
    输出：
    绘制折线图
    无返回数据
    """
    import pandas as pd
    
    #绘制折线图      
    r1=product1[0]['close'].pct_change()
    r1df=pd.DataFrame(r1)
    r1df.columns=['ret']
    r1df['ret%']=round(r1df['ret']*100.0,2)    
    r1t=r1df.tail(days)
    label1=product1[1]+'/'+product1[2]+' @'+product1[3]
    plt.plot(r1t['ret%'],label=label1,lw=3)
    
    r2=product2[0]['close'].pct_change()
    r2df=pd.DataFrame(r2)
    r2df.columns=['ret']
    r2df['ret%']=round(r2df['ret']*100.0,2)    
    r2t=r2df.tail(days)    
    label2=product2[1]+'/'+product2[2]+' @'+product2[3]    
    plt.plot(r2t['ret%'],label=label2,lw=3,ls=':')  
    
    plt.axhline(y=0.0,color='green',linestyle='--')

    #图示标题
    titletxt="数字货币产品：跨市场的收益率套利机会"
    plt.title(titletxt,fontweight='bold')
    plt.ylabel("资本利得%")
    plt.xticks(rotation=30)
    plt.legend(loc='best')
    
    plt.gca().set_facecolor('whitesmoke')
    plt.show()
    
    return    
    
if __name__=='__main__':
    prices1=fetchCrypto_Price_byExchange("ETH", "USD", "Coinsbit")
    product1=[prices1,"ETH", "USD", "Coinsbit"]
    prices2=fetchCrypto_Price_byExchange("ETH", "USD", "Coinbase")
    product2=[prices2,"ETH", "USD", "Coinbase"]
    compCrypto_Return(product1,product2)    


#==============================================================================
#定义爬虫函数：抓取列表中每个交易所的价格数据，合并数据到cp中
#注意：在指定的时间段，并非每个交易所都有ETH交易，若无则以nan表示
def fetchCrypto_Price_byExchList(fsym,tsym,markets,begdate,enddate):
    cp=pd.DataFrame([]); print("\n%s/%s" % (fsym, tsym))
    for market in markets:
        print("%12s... " % market, end="")
        df = fetchCrypto_Price_byExchange(fsym, tsym, market)
        if df is None:
            print("price retrieving failed")
            continue   #爬虫失败，跳出本次循环，继续下一轮循环

        ts = df[(df.index >= begdate) & (df.index <= enddate)]["close"]
        ts.name = market
        if ('cp' in globals()) or ('cp' in locals()): #已经存在cp
            tsdf=pd.DataFrame(ts)
            cp = pd.merge(cp,tsdf,how='outer',left_index=True,right_index=True)
        else:    #第一次生成cp
            cp = pd.DataFrame(ts)
        print("price retrieved successfully")
    return cp
   
#==============================================================================

#定义函数：计算2个市场组合之间所选产品的价差估计：均值，标准差
def calcSpread_in2Markets(cp):
    dist = []   #存放每两个交易所组合之间价差的均值和标准差
    for i in range(cp.shape[1]):
        for j in range(i):
            if(i != j):
                x = np.array(cp.iloc[:,i], dtype=np.float32)
                y = np.array(cp.iloc[:,j], dtype=np.float32)
                diff = np.abs(x-y)
                avg = np.mean(diff)
                std = np.std(diff, ddof=1)
                dist.append([cp.columns[i], cp.columns[j], avg, std])

    import pandas as pd
    dist=pd.DataFrame(dist)
    dist.columns=['Market1','Market2','avg','std']
    dist=dist.dropna(axis=0,how='any')    #删除带有nan的行
    dist1=dist.sort_values(by=['avg','std'],ascending=(False,False))
    dist1=dist1.reset_index(drop = True)  #重新索引
    dist2=dist1.sort_values(by=['std','avg'],ascending=(True,False))
    
    #打印
    pd.set_option('display.max_columns', 1000)
    pd.set_option('display.width', 1000)
    pd.set_option('display.max_colwidth', 1000)
    pd.set_option('display.unicode.ambiguous_as_wide', True)
    pd.set_option('display.unicode.east_asian_width', True)
    
    # Descending by spread
    print("\n***Average inter-market spread:")
    print(dist1.to_string(index=False))
    # Descending by risk
    print("\n***Inter-market spread volatility:")
    print(dist2.to_string(index=False))
    return dist1,dist2

#==============================================================================

#定义函数：显示2个市场组合之间所选产品的价差估计：均值，标准差
def printSpread_in2Markets(dist1,dist2):
    
    dist1.rename(columns={'Market1':'市场1','Market2':'市场2','avg':'价差均值','std':'价差标准差'},inplace=True)
    dist2.rename(columns={'Market1':'市场1','Market2':'市场2','avg':'价差均值','std':'价差标准差'},inplace=True)
    dist2b=dist2[['市场1','市场2','价差标准差','价差均值']]
    
    import pandas as pd
    pd.set_option('display.unicode.ambiguous_as_wide', True)
    pd.set_option('display.unicode.east_asian_width', True)
    pd.set_option('display.width', 180) # 设置打印宽度(**重要**)

    print("\n ===== 市场间价差大小：按均值降序排列 =====")
    print(dist1)
    print("\n===== 市场间价差风险：按标准差降序排列 =====")
    print(dist2b)    
    
    dist2b['收益-风险性价比']=round(dist2b['价差均值']/dist2b['价差标准差'],4)
    dist3=dist2b[['市场1','市场2','收益-风险性价比','价差标准差','价差均值']]
    dist3=dist3.sort_values(by=['收益-风险性价比'],ascending=(False))
    print("\n       ===== 市场间价差：按收益-风险性价比降序排列 =====")
    print(dist3)       
    
    return 
#==============================================================================
if __name__=='__main__':
    fsym = "ETH"; tsym = "USD"
    begdate="2020-1-1"; enddate="2020-12-31"
    market1 = "primexbt"; market2 = "Coinbase"

#定义函数：绘图所选市场组合中的价差分布
def evalSpread_in2Markets(fsym,tsym,market1,market2,begdate,enddate):
    #抓取两个市场的价格数据 
    df1 = fetchCrypto_Price_byExchange(fsym, tsym, market1)
    df2 = fetchCrypto_Price_byExchange(fsym, tsym, market2)
 
    #过滤时间段
    df1 = df1[(df1.index > begdate) & (df1.index <= enddate)]
    df2 = df2[(df2.index > begdate) & (df2.index <= enddate)]
 
    #检查：两个市场在所选时间段每日必须都有交易，即收盘价数据表必须形状相同
    #如果数据表形状不同，需要寻找双方共同具有交易数据的时间段，并重设时间段
    #print(df1.close.shape[0], df2.close.shape[0])
 
    #绘图：观察两个市场间的价差分布，再次检查是否存在套利机会：曲线不完全重叠
    import pandas as pd
    df12=pd.merge(df1,df2,how='inner',left_index=True,right_index=True)
    df12['spread']=df12['close_x'] - df12['close_y']
    
    #plt.figure(figsize=(12,6))
    plt.figure(figsize=(12.8,6.4))
    labeltxt=market1+"与"+market2+"的价差"
    plt.plot(df12.spread, '.-', label=labeltxt)
    #plt.plot(df2.close, '.-', label=market2)
    plt.legend(loc='best')
    plt.title(fsym+"：在两个市场中的价格差异", fontsize=12)
    plt.ylabel("价差（"+tsym+"）", fontsize=12)
    plt.grid()

    return df1,df2
    
#==============================================================================

#定义函数：回测MSA投资策略 
def backtestMSA_Strategy(investment,account1,account2,position,df1,df2):
    roi = []                #投资回报率记录
    money = []              #资金头寸记录
    ac1 = [account1]; ac2 = [account2]
    #各个交易所的盈亏记录；pnl表示盈亏Profit and Loss
    pnl_exch1 = []; pnl_exch2 = []
    trade = False           #标识当前是否处于交易状态
    n = df1.close.shape[0]  #所选产品的收盘价样本个数
    trade_pnl=[]            #整体投资的盈亏记录
 
    #交易回测
    for i in range(n):  #对于每个日交易价格样本循环
        p1 = float(df1.close.iloc[i]); p2 = float(df2.close.iloc[i])
        if(p1 > p2):    #[if-A]若交易所1中产品的价格高于交易所2，卖出1买入2
            asset1 = "SHORT"; asset2 = "LONG"
            if(trade == False):
                #若当前未处于交易状态，则开始一个新的交易
                open_p1 = p1; open_p2 = p2
                open_asset1 = asset1; open_asset2 = asset2
                trade = True        #标识：当前处于交易状态
                print("new traded opened:")
                new_trade = False   #标识：当前已处于交易状态，并非新交易
            elif(asset1 == open_asset1):
                new_trade = False
            elif(asset1 == open_asset2):
                new_trade = True
 
        elif(p2 > p1):  #[if-A]若交易所1中产品的价格低于交易所2，买入1卖出2
            asset1 = "LONG"; asset2 = "SHORT"
            if(trade == False):
                #若当前未处于交易状态，则开始一个新的交易
                open_p1 = p1; open_p2 = p2
                open_asset1 = asset1; open_asset2 = asset2
                trade = True
                print("new traded opened:")
                new_trade = False
            elif(asset1 == open_asset1):
                new_trade = False
            elif(asset1 == open_asset2):
                new_trade = True
 
        if(i == 0):         #[if-B]抓取交易样本的起点
            print(df1.close.iloc[i], df2.close.iloc[i], \
                  asset1, asset2, trade, "----first trade info")
        else:               #[if-B]当前并非交易样本的起点，处于交易中间                   
            if(new_trade):  #[if-B:if-B1]当前处于交易空档期
                #核算当前账户头寸:交易所1卖出
                if(open_asset1 == "SHORT"): #[if-B:if-B1:if-B11]若交易所1卖出
                    #计算交易盈亏
                    pnl_asset1 = open_p1/p1 - 1
                    pnl_asset2 = p2/open_p2 -1
                    pnl_exch1.append(pnl_asset1)
                    pnl_exch2.append(pnl_asset2)
                    print(open_p1, p1, open_p2, p2, open_asset1, \
                          open_asset2, round(pnl_asset1,4), round(pnl_asset2,4))
                    #更新账户余额
                    account1 = account1 + position*pnl_asset1
                    account2 = account2 + position*pnl_asset2
                    print("accounts [USD] = ", round(account1,2), round(account2,2))
                    if((account1 <=0) or (account2 <=0)):
                        print("--trading halted")   #账户余额不足，停止交易
                        break
                    #计算投资回报ROI
                    total = account1 + account2
                    roi.append(total/investment-1)
                    ac1.append(account1); ac2.append(account2)
                    money.append(total)
                    print("ROI = ", round(roi[-1],4)); print("trade closed\n")
                    trade = False
 
                    #开始一个新的交易
                    if(asset1 == "SHORT"):  #交易所1卖出交易
                        open_p1 = p1; open_p2 = p2
                        open_asset1 = asset1; open_asset2 = asset2
                    else:
                        open_p1 = p1; open_p2 = p2
                        open_asset1 = asset1; open_asset2 = asset2
                    trade = True
                    print("new trade opened:", asset1, asset2, \
                          open_p1, open_p2)
 
                #核算当前账户头寸:交易所1买入
                if(open_asset1 == "LONG"):  #[if-B:if-B1:if-B12]若交易所1买入
                    #计算交易盈亏
                    pnl_asset1 = p1/open_p1 -1
                    pnl_asset2 = open_p2/p2 - 1
                    pnl_exch1.append(pnl_asset1)
                    pnl_exch2.append(pnl_asset2)
                    print(open_p1, p1, open_p2, p2, open_asset1, \
                          open_asset2, round(pnl_asset1,4), round(pnl_asset2,4))
                    #更新账户余额
                    account1 = account1 + position*pnl_asset1
                    account2 = account2 + position*pnl_asset2
                    print("accounts [USD] = ", round(account1,2), round(account2,2))
                    if((account1 <=0) or (account2 <=0)):
                        print("--trading halted")
                        break
                    #计算投资回报ROI
                    total = account1 + account2
                    roi.append(total/investment-1)
                    ac1.append(account1); ac2.append(account2)
                    money.append(total)
                    trade_pnl.append(pnl_asset1+pnl_asset2)
                    print("ROI = ", round(roi[-1],4))
                    print("trade closed\n")
                    trade = False
 
                    #开始一个新的交易
                    if(open_asset1 == "SHORT"): #若交易所1卖出
                        open_p1 = p1; open_p2 = p2
                        open_asset1 = asset1; open_asset2 = asset2
                    else:
                        open_p1 = p1; open_p2 = p2
                        open_asset1 = asset1; open_asset2 = asset2
                    new_trade = False
                    trade = True
                    print("new trade opened:", asset1, asset2, \
                          open_p1, open_p2)
 
            else:   #[if-B:if-B1]
                print("   ",df1.close.iloc[i], df2.close.iloc[i], \
                      asset1, asset2)

    return ac1,ac2,money,roi

#==============================================================================
        
#定义函数：绘图每个账户的头寸
def eval_Position(market1,market2,investment,ac1,ac2,money):
    
    
    ymax=(round(max(money)/1000)+1)*1000
    #plt.figure(figsize=(18,9))
    plt.figure(figsize=(12.8,6.4))
    # market1的账户ac1变化图
    plt.subplot(2,3,1)
    plt.plot(ac1)
    plt.title(market1 + "市场的资金账户余额")
    plt.xlabel("交易序列"); plt.ylabel("账户余额")
    plt.grid()
    plt.xlim([0, len(money)]); plt.ylim([0, ymax])    
    # market2的账户ac2变化图
    plt.subplot(2,3,2)
    plt.plot(ac2)
    plt.title(market2 + "市场的资金账户余额")
    plt.xlabel("交易序列"); plt.ylabel("账户余额")
    plt.grid()
    plt.xlim([0, len(money)]); plt.ylim([0, ymax])    
    # 总的账户money变化图
    plt.subplot(2,3,3)
    plt.plot(np.array(money))
    plt.title("资金总额")
    plt.xlabel("交易序列"); plt.ylabel("金额")
    plt.grid()
    plt.xlim([0, len(money)]); plt.ylim([investment, ymax])   
    
    return
    
#定义函数：绘图投资总收益ROI        
def eval_Roi(fsym,tsym,market1,market2,roi,begdate,enddate):
    
    
    ttltrdnum=len(roi)
    ymax=round(10*roi[-1])*10+10
    product=fsym+"/"+tsym+"："
    mktpair="市场配对("+market1+"，"+market2+")"
    #plt.figure(figsize=(8,5))
    plt.figure(figsize=(12.8,6.4))
    plt.plot(np.array(roi)*100, 'r')
    
    footnote1="交易序列(总计"+str(ttltrdnum)+"次)"
    footnote2="\n交易期间："+begdate+"至"+enddate
    plt.xlabel(footnote1+footnote2)
    
    plt.ylabel("收益率%")
    plt.title(product+mktpair+", ROI = %s%%" % str(round(100*roi[-1],2)))
    plt.xlim([0, len(roi)]); plt.ylim([0, ymax])
    plt.grid()
    
    return

#定义函数：显示任意2个市场间的平均价差和风险，供手动选择两个市场
def select2Markets(fsym,tsym,begdate,enddate):
    #抓取所选产品最活跃的交易所Top5，放入市场列表markets中
    markets=fetchCrypto_Exchange(fsym,tsym,5)

    #抓取指定交易所列表markets中所选产品在指定期间内的收盘价，放入收盘价cp中
    cp=fetchCrypto_Price_byExchList(fsym,tsym,markets,begdate,enddate) 

    #计算cp中任意2个市场组合之间所选产品的价差估计
    dist1,dist2=calcSpread_in2Markets(cp)
    
    return


#定义函数：选择价差均值avg最大的2个市场。风险偏好：进取型
def select2Markets_TopSpreadAvg(fsym,tsym,begdate,enddate):
    #抓取所选产品最活跃的交易所Top5，放入市场列表markets中
    markets=fetchCrypto_Exchange(fsym,tsym,5)

    #基于投资风险偏好，选择2个价差最大的交易所
    #抓取指定交易所列表markets中所选产品在指定期间内的收盘价，放入收盘价cp中
    cp=fetchCrypto_Price_byExchList(fsym,tsym,markets,begdate,enddate) 

    #计算cp中任意2个市场组合之间所选产品的价差估计
    dist1,dist2=calcSpread_in2Markets(cp)
    
    #显示任意2个市场组合收盘价价差的均值和标准差
    print("\n*****Sorted by descending average of market spread\n",dist1)
    
    market1=dist1.loc[0,'Market1']; market2=dist1.loc[0,'Market2']
    return market1,market2

#定义函数：选择价差标准差std最小的2个市场。风险偏好：保守型
def select2Markets_BottomSpreadStd(fsym,tsym,begdate,enddate):
    #抓取所选产品最活跃的交易所Top5，放入市场列表markets中
    markets=fetchCrypto_Exchange(fsym,tsym,5)

    #基于投资风险偏好，选择2个价差最大的交易所
    #抓取指定交易所列表markets中所选产品在指定期间内的收盘价，放入收盘价cp中
    cp=fetchCrypto_Price_byExchList(fsym,tsym,markets,begdate,enddate) 

    #计算cp中任意2个市场组合之间所选产品的价差估计
    dist1,dist2=calcSpread_in2Markets(cp)
    dist2=dist2.reset_index(drop = True)    #重新索引
    #显示任意2个市场组合收盘价价差的均值和标准差
    print("\n*****Sorted by descending std of market spread\n",dist2)
    
    market1=dist2.loc[len(dist2)-1,'Market1']
    market2=dist2.loc[len(dist2)-1,'Market2']
    return market1,market2   

#定义函数：选择市场后，一步实现所有MSA操作
def implementMSA_Strategy(fsym,tsym,investment,account1,account2,position, \
                          market1,market2,begdate,enddate,verbose=False):
   
   print("  Starting MSA spread trading and backtesting ......")
   print("    If expecting transaction details, please set verbose=True in command")
    
   df1,df2=evalSpread_in2Markets(fsym,tsym,market1,market2,begdate,enddate)
   
   #屏蔽函数内print信息输出的类
   import os, sys
   class HiddenPrints:
        def __enter__(self):
            self._original_stdout = sys.stdout
            sys.stdout = open(os.devnull, 'w')

        def __exit__(self, exc_type, exc_val, exc_tb):
            sys.stdout.close()
            sys.stdout = self._original_stdout
   
   if not verbose: 
       with HiddenPrints():
           ac1,ac2,money,roi=backtestMSA_Strategy( \
             investment,account1,account2,position,df1,df2)
   else:
       ac1,ac2,money,roi=backtestMSA_Strategy( \
             investment,account1,account2,position,df1,df2)
       
   #省略此步骤?
   eval_Position(market1,market2,investment,ac1,ac2,money)
   eval_Roi(fsym,tsym,market1,market2,roi,begdate,enddate) 
   return
#==============================================================================
