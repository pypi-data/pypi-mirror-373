# -*- coding: utf-8 -*-
"""
本模块功能：中国大陆的内盘和外盘期货
所属工具包：证券投资分析工具SIAT 
SIAT：Security Investment Analysis Tool
创建日期：2021年9月26日
最新修订日期：2021年9月28日
作者：王德宏 (WANG Dehong, Peter)
作者单位：北京外国语大学国际商学院
版权所有：王德宏
用途限制：仅限研究与教学使用，不可商用！商用需要额外授权。
特别声明：作者不对使用本工具进行证券投资导致的任何损益负责！
"""

#==============================================================================
#关闭所有警告
import warnings; warnings.filterwarnings('ignore')
from siat.common import *
from siat.grafix import *
#==========================================================================================
if __name__=='__main__':
    trade_date='2023-5-18'

def future_type_china_0(trade_date):
    """
    中国内盘期货：代码和品种的基础数据
    """
    #日期变换
    trade_date1=convert_date_ts(trade_date)
    
    import akshare as ak
    df=ak.futures_rule(date=trade_date1)
    
    try:
        cols = df.columns.tolist()
    except:
        return None
    cols1 = cols[2:3] + cols[1:2] + cols[0:1] + cols[3:] # 将基金代码列名放前面
    
    #改变字段顺序
    df1=df[cols1]
    
    #去掉期权项目
    df2=df1[~df1['品种'].str.contains("期权")]  
    df2.sort_values(by=['代码'],ascending=True,inplace=True)
    df2.reset_index(inplace=True)
    del df2['index']
    
    return df2

#======================================================================================
def SBC2DBC(ustring):
    """
    字符串转换：半角转全角，便于打印对齐
    """
    rstring = ''
    for uchar in ustring:
        inside_code = ord(uchar)
        if inside_code == 0x0020:
            inside_code = 0x3000
        else:
            if not (0x0021 <= inside_code and inside_code <= 0x7e):
                rstring += uchar
                continue
        inside_code += 0xfee0
        rstring += chr(inside_code)
    return rstring
#======================================================================================
if __name__=='__main__':
    trade_date='2020-7-13'
    df=future_type_china_0(trade_date)    

def future_type_china_1(df):
    """
    列示中国内盘期货的全部代码和品种，每4个一行
    """
    print("\n===== 中国内盘期货代码品种一览表 =====\n")
    #遍历，合成一行
    itemlist=[]
    for row in df.itertuples():
        code=SBC2DBC(getattr(row,'代码'))
        name=SBC2DBC(getattr(row,'品种'))
        itemlist=itemlist+[code+'（'+name+'）']
    
    maxlen=0
    for i in itemlist:
        ilen=len(i)
        if maxlen < ilen: maxlen=ilen
    maxlen=maxlen+1
    
    rownum=0
    linetxt=''
    iteminline=3
    for i in itemlist:
        if rownum < iteminline:
            ifull=i+SBC2DBC('.')*(maxlen-len(i))
            linetxt=linetxt+ifull
            rownum=rownum+1
        else:
            print(linetxt)
            rownum=0; linetxt=''
        
    import datetime
    today = datetime.date.today()
    print('\n*** 数据来源：国泰君安,',today)
    
    return

if __name__=='__main__':
    future_type_china_1(df)     
#======================================================================================
if __name__=='__main__':
    code='BB2007'
    df=future_type_china_0(trade_date) 

def get_future_symbol(code):
    """
    获得一个具体期货合约的品种代码
    """
    code1=code.upper()
    
    letterlist=[chr(i).upper() for i in range(97,123)]
    symbol=''
    
    for ch in code1:
        if ch in letterlist:
            symbol=symbol+ch
        else:
            break
    
    return symbol
#======================================================================================

def future_type_china_2(df,code):
    """
    列示中国内盘期货的品种明细
    """
    symbol=get_future_symbol(code)
    
    df1=df[df['代码']==symbol]
    cols=list(df1)
    cols.pop()

    print("\n===== 中国内盘期货品种概况 =====\n")
    maxlen=0
    for c in cols:
        clen=hzlen(c)
        if maxlen < clen: maxlen=clen
    
    contract='合约'
    print(contract+' '*(maxlen-hzlen(contract))+':',code)
    import numpy as np
    for c in cols:
        value=df1[c].values[0]
        if value != np.nan:
            print(c+' '*(maxlen-hzlen(c))+':',df1[c].values[0])
        else:
            continue

    import datetime
    today = datetime.date.today()
    print('\n数据来源：国泰君安,',today)
    
    return

if __name__=='__main__':
    future_type_china_2(df,'BB2007') 

#======================================================================================
if __name__=='__main__':
    tradedate=''
    tradedate='2025-8-2'
    
    exchange='大商所'
    
    future_type_china(tradedate)

def future_type_china(tradedate='',exchange=''):
    """
    功能：中国内盘期货的常见品种，含合约品种明细
    """
    
    # 检查交易日期，默认当前日期
    import datetime
    import calendar
    if tradedate=='':
        tradedate = datetime.date.today()
        
    #若为非工作日，则调整为工作日
    tradedate=adjust_to_workday(tradedate)
        
    result,fdate=check_date2(tradedate)
    year=fdate[:4]; month=fdate[5:7]; day=fdate[8:10]
    date_week = calendar.weekday(int(year),int(month),int(day))
    weekday=calendar.day_name[date_week]
    
    if weekday in ['Saturday','Sunday']:
        print("  #Warning(future_type_china):",tradedate,"is not a working day")
        print("  Solution: specify a working date of market using tradedate option")
        return None
    else:
        today=year+month+day
    
    df=future_type_china_0(today)
    while df is None:
        today=date_adjust(today, adjust=-1)
        df=future_type_china_0(today)
    
    df.drop(['调整备注','特殊合约参数调整'], axis=1, inplace=True)
    
    titletxt="中国内盘期货常见品种"
    if exchange != '':
        df2=df[df['交易所'].str.contains(exchange, na=False)]
        if len(df2) == 0:
            exchange_list = list(set(list(df['交易所'])))
            print(f"  #Warning(future_type_china): exchange {exchange} not found")
            print(f"  Supported exchanges: {exchange_list}")
            return None
            
        exchange_name=df2['交易所'].values[0]
        titletxt=titletxt + "：" + exchange_name
    else:
        df2=df
        
    footnote="数据来源：国泰君安, "+str(tradedate)
    df_display_CSS(df2,titletxt=titletxt,footnote=footnote,facecolor='papayawhip', \
                       first_col_align='center',second_col_align='center', \
                       last_col_align='center',other_col_align='center')
        
    return df


#======================================================================================
if __name__=='__main__':
    code='PG'
    start='2025-5-1'
    end='2025-5-30'
    power=1

def future_price_china(code,start='MRM',end='today', \
                       power=0,loc1='upper left',loc2='upper right',facecolor="papayawhip"):
    """
    综合程序：
    绘制内盘期货交易曲线：收盘价vs结算价vs成交量
    """
    start,end=start_end_preprocess(start,end)
    
    print("Searching for contract "+code+", it may take time ...")
    #日期变换
    start1=convert_date_ts(start)
    end1=convert_date_ts(end)
    
    #获得中国内盘期货品种代码
    try:
        varietydf=future_type_china_0(end1)
    except:
        print("  #Error(future_price_china): no info for the end date", end, "\b, try an earlier date")
        return None
        
    #获得期货合约code的品种代码
    variety=get_future_symbol(code)
    #variety=get_future_symbol(code).lower()
    
    try:
        vdf=varietydf[varietydf['代码']==variety]
    except:
        print("  #Error(future_price_china): the end date", end, "shall not be later than today")
        return None
        
    if len(vdf)==0:
        print("  #Error(future_price_china): future variety",variety,'not found')
        return None
    varietyname=vdf['品种'].values[0]
    
    #查找交易所代码
    mktname=vdf['交易所'].values[0]
    mktnamelist=['大商所','郑商所','上期所','中金所','能源中心']
    mktnamelistfull=['大连商品交易所','郑州商品交易所','上海期货交易所','中国金融期货交易所','上海国际能源交易中心']
    mktcodelist=['DCE','CZCE','SHFE','CFFEX','INE']
    pos=mktnamelist.index(mktname)
    market=mktcodelist[pos]
    mktnamefull=mktnamelistfull[pos]
    
    import akshare as ak
    try:
        p=ak.get_futures_daily(start_date=start1,end_date=end1,market=market)
    except:
        print("  #Warning(future_price_china): failed to get data for",code)
        print("  Solution: try make date period shorter (e.g. within same month), and try again")
        return None
        
    if p is None:
        print("  #Error(future_price_china): future transaction info not found from", start, "to",end,"in market",market)
        print("  Try earlier start date")
        return None
    
    p1=p[p['symbol']==code.lower()]
    if len(p1)==0: 
        print("  #Warning(future_price_china): future contract",code,'not found in market',market)
        contracts=set(list(p[p['variety']==variety]['symbol']))
        contracts1=sorted(contracts) 
        print("\n提示：当前可用的"+varietyname+variety+'期货合约：'+mktnamefull+', '+str(end))
        #print(contracts1)
        printlist(contracts1,numperline=10,beforehand='',separator=' ')
        return None        
    
    #转换日期格式
    import pandas as pd
    p1['date1']=pd.to_datetime(p1['date'])
    p2=p1.set_index('date1')
    
    import pandas as pd
    p2a=pd.DataFrame(p2['close']) #收盘价
    p2a['close']=p2a['close'].astype('float')
    
    p2b=pd.DataFrame(p2['settle']) #结算价  
    p2b['settle']=p2b['settle'].astype('float')
    
    p2c=pd.DataFrame(p2['volume']) #成交量
    p2c['volume']=p2c['volume'].astype('int64')
    
    p2d=pd.DataFrame(p2['turnover']) #成交金额
    p2d['turnover']=p2d['turnover'].astype('int64')
    
    p2e=pd.DataFrame(p2['open_interest']) #持仓量
    p2e['open_interest']=p2e['open_interest'].astype('int64')
    
    #绘图
    import datetime
    today = datetime.date.today()
    footnote="数据来源："+mktnamefull+', '+str(today)
    
    print("  Rendering trading trend graphics ...")
    titletxt="中国期货交易走势分析："+varietyname+code
    #避免code被翻译
    acode=' '+code
    #"""
    #收盘价vs结算价
    plot_line2(p2a,acode,"close","收盘价", \
               p2b,acode,"settle","结算价", \
               '价格',titletxt,footnote, \
               power=power,twinx=False,loc1=loc1,loc2=loc2,facecolor=facecolor)
    #"""
    #收盘价vs成交量
    plot_line2(p2a,acode,"close","收盘价", \
               p2c,acode,"volume","成交量", \
               '',titletxt,footnote, \
               power=power,twinx=True,loc1=loc1,loc2=loc2,facecolor=facecolor)
    #"""
    #收盘价vs持仓量
    plot_line2(p2a,acode,"close","收盘价", \
               p2e,acode,"open_interest","持仓量", \
               '',titletxt,footnote, \
               power=power,twinx=True,loc1=loc1,loc2=loc2,facecolor=facecolor)
    #"""
    return p2

if __name__=='__main__':
    code='SC2110'
    df=future_type_china(code) 
    
#===========================================================================================
if __name__=='__main__':
    symbol="ZSD"

def future_type_foreign_0(symbol="ZSD"):
    """
    获得某个外盘期货品种symbol详情
    """
    import akshare as ak
    try:
        df=ak.futures_foreign_detail(symbol=symbol)
    except:
        print("  #Error(future_type_foreign_0): future variety",symbol,'not found')
        return None
    
    #构造df
    col1=df.iloc[0,0]; col1value=df.iloc[0,1]
    if "并非期货" in col1value:
        col1value=col1value.replace("并非期货",'')
    
    col2=df.iloc[0,2]; col2value=df.iloc[0,3]
    col3=df.iloc[0,4]; col3value=df.iloc[0,5]
    
    col4=df.iloc[1,0]; col4value=df.iloc[1,1]
    col5=df.iloc[1,2]; col5value=df.iloc[1,3]
    col6=df.iloc[1,4]; col6value=df.iloc[1,5]
    
    col7=df.iloc[2,0]; col7value=df.iloc[2,1]
    col8=df.iloc[2,2]; col8value=df.iloc[2,3]
    
    col9=df.iloc[3,0]; col9value=df.iloc[3,1]
    col10=df.iloc[3,2]; col10value=df.iloc[3,3]  
    
    future_dict={col9:col9value,col1:col1value,col10:col10value,col2:col2value, \
                 col3:col3value,col4:col4value,col5:col5value,col6:col6value, \
                     col7:col7value,col8:col8value}
    import pandas as pd
    df1=pd.DataFrame(future_dict,index=[0])
    
    return df1

if __name__=='__main__':
    df=future_type_foreign_0(symbol="ZSD")  
    print(df.T)
#===========================================================================================
if __name__=='__main__':
    symbol="ZSD"

def future_type_foreign_1():
    """
    获得中国所有外盘期货品种详情
    """
    import akshare as ak  
    varietylist=ak.futures_foreign_commodity_subscribe_exchange_symbol()
    varietylist.sort()
    
    try:
        df=future_type_foreign_0(symbol=varietylist[0])
    except:
        pass
    for v in varietylist:
        try:
            df_tmp=future_type_foreign_0(symbol=v)
            #print(v)
            try:
                df=df.append(df_tmp)
            except:
                df=df._append(df_tmp)
        except:
            pass
    df.drop_duplicates(inplace=True)
    
    return df
    
#===========================================================================================
if __name__=='__main__':
    symbol="ZSD"
    df=future_type_foreign_1()

def future_type_foreign_2(df,symbol="ZSD"):
    """
    打印中国外盘期货某个品种详情
    """
    
    df1=df[df['交易代码']==symbol]
    cols=list(df1)

    print("\n===== 中国外盘期货品种概况 =====\n")
    maxlen=0
    for c in cols:
        clen=hzlen(c)
        if maxlen < clen: maxlen=clen
    
    for c in cols:
        print(c+' '*(maxlen-hzlen(c))+':',df1[c].values[0])

    import datetime
    today = datetime.date.today()
    print('\n*** 数据来源：新浪财经,',today)
    
    return

if __name__=='__main__':
    future_type_foreign_2(df,symbol="ZSD")  
    
#======================================================================================
if __name__=='__main__':
    exchange = '伦敦'
    future_type_foreign()

def future_type_foreign(exchange = ''):
    """
    功能：中国外盘期货的常见品种，含合约明细
    """
    
    df=future_type_foreign_1()
    #cols=['交易代码','交易品种','上市交易所','交易单位','报价单位','合约交割月份']
    cols=['交易代码','交易品种','上市交易所','交易单位','报价单位']
    df1=df[cols]
    df1.reset_index(drop=True,inplace=True)

    titletxt="中国外盘期货常见品种"
    if exchange != '':
        df2 = df1[df1['交易品种'].str.contains(exchange,na=False) | \
                  df1['上市交易所'].str.contains(exchange,na=False)]
        if len(df2) == 0:
            print(f"  #Warning(future_type_foreign): exchange {exchange} not found")
            exchange_list=list(set(list(df1['上市交易所'])))
            print(f"  Supported exchanges: {exchange_list}")
            return None

        exchange_name=df2['上市交易所'].values[0]    
        titletxt=titletxt+"：" +  exchange_name
    else:
        df2=df1
    
    import datetime
    todaydt = datetime.date.today()
    footnote="数据来源：新浪财经, "+str(todaydt)
    
    df_display_CSS(df2,titletxt=titletxt,footnote=footnote, \
                   facecolor='papayawhip', \
                       first_col_align='center',second_col_align='center', \
                       last_col_align='center',other_col_align='center')
    
    return df1

if __name__=='__main__':
    df=future_type_foreign(code='') 
    df=future_type_foreign(code='CT')
    df=future_type_foreign(code='OIL')

#====================================================================================== 
if __name__=='__main__':
    code='ZSD'
    start='2021-8-1'
    end='2021-9-27'
    power=0

def future_price_foreign(code,start='MRM',end='today', \
                         power=0,loc1='upper left',loc2='upper right', \
                             facecolor="papayawhip"):
    """
    综合程序：
    绘制中国外盘期货的交易趋势：收盘价vs成交量
    """
    start,end=start_end_preprocess(start,end)
    
    print("Searching for contract "+code+", it costs great time, just take a break...")
    #日期变换
    flag,start1,end1=check_period(start,end)
    
    #获得中国外盘期货品种代码
    varietydf=future_type_foreign_0(symbol=code)
    #获得期货合约code的品种代码
    if len(varietydf)==0:
        print("  #Error(future_price_foreign): future variety",code,'not found')
        return None
    varietyname=varietydf['交易品种'].values[0]
    
    #查找交易所代码
    mktnamefull=varietydf['上市交易所'].values[0]
    
    import akshare as ak
    p0=ak.futures_foreign_hist(symbol=code) 
    p01=p0[p0['date']>=start1]
    p1=p01[p01['date']<=end1]
    
    if len(p1)==0: 
        print("  #Error(future_price_foreign): prices not found for",code,'from',start,'to',end)
        return None        
    
    #转换日期格式
    p2=p1.set_index('date')
    
    import pandas as pd
    p2a=pd.DataFrame(p2['close']) #收盘价
    p2a['close']=p2a['close'].astype('float')
    
    p2c=pd.DataFrame(p2['volume']) #成交量
    p2c['volume']=p2c['volume'].astype('int64')
    
    #绘图
    import datetime
    today = datetime.date.today()
    footnote="数据来源：新浪财经"+', '+str(today)
    
    titletxt="中国外盘期货交易走势分析："+varietyname+code
    
    #收盘价vs成交量
    #print("code =",code)
    #避免code被翻译
    acode=' '+code
    plot_line2(p2a,acode,"close","收盘价", \
               p2c,acode,"volume","成交量", \
               '',titletxt,footnote, \
               power=power,twinx=True,loc1=loc1,loc2=loc2,facecolor=facecolor)

    return p2

if __name__=='__main__':
    df=future_price_foreign('CT','2021-8-1','2021-9-28')
    
#===========================================================================================   