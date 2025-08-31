# -*- coding: utf-8 -*-
"""
本模块功能：投资组合的风险调整收益率教学插件
所属工具包：证券投资分析工具SIAT 
SIAT：Security Investment Analysis Tool
创建日期：2023年11月30日
最新修订日期：2023年11月30日
作者：王德宏 (WANG Dehong, Peter)
作者单位：北京外国语大学国际商学院
作者邮件：wdehong2000@163.com
版权所有：王德宏
用途限制：仅限研究与教学使用！
特别声明：作者不对使用本工具进行证券投资导致的任何损益负责！
"""

#==============================================================================
#关闭所有警告
import warnings; warnings.filterwarnings('ignore')
#==============================================================================
from siat.common import *
from siat.translate import *
from siat.stock import *
from siat.security_prices import *
from siat.security_price2 import *
from siat.sector_china import *
from siat.valuation_china import *
from siat.grafix import *

import pandas as pd
import akshare as ak

import datetime as dt; todaydt=str(dt.date.today())
#==============================================================================
#==============================================================================
if __name__=='__main__':
    ticker='PZU.PL'
    ticker='PZU.WA'
    
    indicators='pe'
    indicators=['pe','pb']
    indicators=['pe','pb','mv']
    
    start='2023-1-1'; end='2023-11-30'
    
    df_pl=get_stock_valuation_pl(ticker,indicators,start,end)
    
def get_stock_valuation_pl(ticker,indicators,start,end):
    """
    功能：抓取一只波兰股票估值信息pe/pb/mv
    """
    currency='PLN'
    million=1000000
    kilo=1000
    # 判断是否波兰股票
    ticker1=ticker.upper()
    result,prefix,suffix=split_prefix_suffix(ticker1)
    if (not result) or (suffix not in ['PL','WA']):
        return None
    iname=ticker_name(ticker)
    
    if isinstance(indicators,str):
        indicators=[indicators]
    
    indicators1=[]
    for i in indicators:
        indicators1=indicators1+[i.upper()]

    #屏蔽函数内print信息输出的类
    import os, sys
    class HiddenPrints:
        def __enter__(self):
            self._original_stdout = sys.stdout
            sys.stdout = open(os.devnull, 'w')

        def __exit__(self, exc_type, exc_val, exc_tb):
            sys.stdout.close()
            sys.stdout = self._original_stdout

    df=None        
    for i in indicators1:
        t=prefix+'_'+i+'.PL'
        with HiddenPrints():
            dft=get_price(t,start,end)
        if dft is None: 
            print("  #Warning(get_stock_valuation_pl): failed to retrieve",t)
            continue
    
        dft['ticker']=ticker1
        dft['name']=iname
        dft['currency']='CNY'
        
        if i=='MV':
            #dft[i]=dft['Close'] * million
            dft[i]=dft['Close'] / kilo
        else:
            dft[i]=dft['Close']
            
        dft1=dft[[i,'name','currency']]
        
        if df is None:
            df=dft1
        else:
            #df=pd.merge(df,dft1,how='inner',left_index=True,right_index=True)
            df=pd.merge(df,dft1,how='outer',left_index=True,right_index=True)
    
    # 去掉多余的name/currency重复列
    if df is None: return None
    collist=list(df)
    if not (('name' in collist) and ('currency' in collist)):
        df.rename(columns={'name_x':'name','currency_x':'currency'},inplace=True)

    collist=list(df)
    collist1=[]
    for c in collist:
        if "_" not in c:
            collist1=collist1+[c]        

    df1=df[collist1]
    
    return df1    


#==============================================================================
if __name__=='__main__':
    ticker='JD'
    ticker='NIO'
    ticker='XPEV'
    
    indicators='PE'
    indicators=['pe','pb']
    indicators=['pe','pb','mv']
    
    start='2023-1-1'; end='2023-11-30'
    
    df_us=get_stock_valuation_us(ticker,indicators,start,end)
    
def get_stock_valuation_us(ticker,indicators,start,end):
    """
    功能：抓取一只美股股票估值信息pe/pb/mv
    """
    currency='USD'
    million=1000000
    kilo=1000
    
    # 判断是否美股股票
    ticker1=ticker.upper()
    result,prefix,suffix=split_prefix_suffix(ticker1)
    if result or suffix != '': # 非美股
        return None
    iname=ticker_name(ticker)
    
    if isinstance(indicators,str):
        indicators=[indicators]
    
    indicators1=[]
    for i in indicators:
        indicators1=indicators1+[i.upper()]

    #屏蔽函数内print信息输出的类
    import os, sys
    class HiddenPrints:
        def __enter__(self):
            self._original_stdout = sys.stdout
            sys.stdout = open(os.devnull, 'w')

        def __exit__(self, exc_type, exc_val, exc_tb):
            sys.stdout.close()
            sys.stdout = self._original_stdout

    df=None        
    for i in indicators1:
        t=prefix+'_'+i+'.US'
        with HiddenPrints():
            dft=get_price_stooq(t,start,end)
        if dft is None: 
            print("  #Warning(get_stock_valuation_us): failed to retrieve",t)
            continue
            
        dft['ticker']=ticker1
        dft['name']=iname
        dft['currency']='CNY'
        
        if i=='MV':
            #dft[i]=dft['Close'] * million
            dft[i]=dft['Close'] / kilo
        else:
            dft[i]=dft['Close']
        dft1=dft[[i,'name','currency']]
        
        if df is None:
            df=dft1
        else:
            df=pd.merge(df,dft1,how='outer',left_index=True,right_index=True)
    
    # 去掉多余的name/currency重复列
    if df is None: return None    
    collist=list(df)
    if not (('name' in collist) and ('currency' in collist)):
        df.rename(columns={'name_x':'name','currency_x':'currency'},inplace=True)

    collist=list(df)
    collist1=[]
    for c in collist:
        if "_" not in c:
            collist1=collist1+[c]        

    df1=df[collist1]
    
    return df1 

#==============================================================================
if __name__=='__main__':
    ticker='600519.SS'
    ticker='002504.SZ'
    ticker='835579.BJ'
    ticker='00700.HK'
    
    indicators='pe'
    indicators=['pe','pb']
    indicators=['pe','pb','mv']
    
    start='2023-1-1'; end='2023-11-30'
    
    df_cnhk=get_stock_valuation_cn_hk(ticker,indicators,start,end)
    
def get_stock_valuation_cn_hk(ticker,indicators,start,end):
    """
    功能：抓取一只A股或港股股票估值信息pe/pb/mv
    """
    result,startdt,enddt=check_period(start,end)
    
    yi=100000000
    ten=10
    # 判断是否A股或港股股票
    ticker1=ticker.upper()
    result,prefix,suffix=split_prefix_suffix(ticker1)
    if (not result) or (suffix not in ['SS','SZ','BJ','HK']):
        return None
    iname=ticker_name(ticker)
    
    if suffix in ['SS','SZ','BJ']: currency='CNY'
    else: currency='HKD'
    
    if isinstance(indicators,str):
        indicators=[indicators]
    
    indicators1=[]
    for i in indicators:
        indicators1=indicators1+[i.upper()]

    #屏蔽函数内print信息输出的类
    import os, sys
    class HiddenPrints:
        def __enter__(self):
            self._original_stdout = sys.stdout
            sys.stdout = open(os.devnull, 'w')

        def __exit__(self, exc_type, exc_val, exc_tb):
            sys.stdout.close()
            sys.stdout = self._original_stdout

    # 评估时间间隔: 取样日期间隔长短不同，必须做
    delta=date_delta(start,end)
    if delta <= 365:
        period="近一年"
    elif delta <= 365*3:
        period="近三年"
    elif delta <= 365*5:
        period="近五年"
    elif delta <= 365*10:
        period="近十年"  
    else:
        period="全部"

    indicator_list_en=['PE','PB','MV','PCF']
    indicator_list_cn=['市盈率(TTM)','市净率','总市值','市现率']
    # 市现率PCF=股价 / 每股现金流
    # 市销率PS或PSR=股价 / 每股销售额
    df=None       
    for i in indicators1:
        pos=indicator_list_en.index(i)
        t=indicator_list_cn[pos]
        """
        with HiddenPrints():
            if suffix in ['SS','SZ','BJ']:
                dft=ak.stock_zh_valuation_baidu(symbol=prefix,indicator=t,period=period)
            elif suffix in ['HK']:
                dft=ak.stock_hk_valuation_baidu(symbol=prefix,indicator=t,period=period)
        """
        try:
            if suffix in ['SS','SZ','BJ']:
                dft=ak.stock_zh_valuation_baidu(symbol=prefix,indicator=t,period=period)
            elif suffix in ['HK']:
                dft=ak.stock_hk_valuation_baidu(symbol=prefix,indicator=t,period=period)
        except:
            print("  #Warning(get_stock_valuation_cn_hk): failed to retrieve",i,"for",prefix)
            continue
        
        dft['Date']=dft['date'].apply(lambda x: pd.to_datetime(x))
        dft.set_index('Date',inplace=True)
        dft['ticker']=ticker1
        dft['name']=iname
        dft['currency']='CNY'        
        if i=='MV':
            #dft[i]=dft['value'] * yi
            dft[i]=dft['value'] / ten
        else:
            dft[i]=dft['value']
        dftp=dft[(dft.index >= startdt) & (dft.index <= enddt)]
        dft1=dftp[[i,'name','currency']]
        
        if df is None:
            df=dft1
        else:
            df=pd.merge(df,dft1,how='outer',left_index=True,right_index=True)
    
    # 去掉多余的name/currency重复列
    if df is None: return None    
    collist=list(df)
    if not (('name' in collist) and ('currency' in collist)):
        df.rename(columns={'name_x':'name','currency_x':'currency'},inplace=True)

    collist=list(df)
    collist1=[]
    for c in collist:
        if "_" not in c:
            collist1=collist1+[c]        

    df1=df[collist1]
    
    return df1 

#==============================================================================
if __name__=='__main__':
    ticker='光伏设备(申万)'
    ticker='中证500'
    ticker='801735.SW'
    
    ticker='中证红利'
    ticker='000922.ZZ'
    ticker='中证央企红利'
    
    indicators='pe'
    indicators=['pe','pb','div yield']
    indicators=['pe','pb']
    
    start='2023-1-1'; end='2023-11-30'
    
    df_index=get_index_valuation_funddb(ticker,indicators,start,end)
    
def get_index_valuation_funddb(ticker,indicators,start,end):
    """
    功能：抓取一个申万或中证行业估值信息pe/pb/dividend(股息率)
    """
    result,startdt,enddt=check_period(start,end)
    
    # 判断是否申万或中证股票
    ticker1=ticker.upper()
    result,prefix,suffix=split_prefix_suffix(ticker1)
    if result and suffix in ['SW']:
        iname=industry_sw_name(prefix)+"(申万)"
    else:
        iname=ticker1
    
    if isinstance(indicators,str):
        indicators=[indicators]
    
    indicators1=[]
    for i in indicators:
        indicators1=indicators1+[i.upper()]

    indicator_list_en=['PE','PB','DIV YIELD']
    indicator_list_cn=['市盈率','市净率','股息率']
    indicators2=[]
    for i in indicators1:
        if i in indicator_list_en:
            indicators2=indicators2+[i]

    #屏蔽函数内print信息输出的类
    import os, sys
    class HiddenPrints:
        def __enter__(self):
            self._original_stdout = sys.stdout
            sys.stdout = open(os.devnull, 'w')

        def __exit__(self, exc_type, exc_val, exc_tb):
            sys.stdout.close()
            sys.stdout = self._original_stdout

    # 股息率=每股股利 / 股价
    df=None       
    for i in indicators2:
        pos=indicator_list_en.index(i)
        t=indicator_list_cn[pos]
        try:
            with HiddenPrints():
                dft=ak.index_value_hist_funddb(symbol=iname,indicator=t)
        except:
            print("  #Error(get_index_valuation_funddb): failed to retrieve info for industry",ticker)
            industry_list=list(ak.index_value_name_funddb()['指数名称'])
            industry_sw=[]
            industry_zz=[]
            industry_gz=[]
            industry_others=[]
            for i in industry_list:
                if '(申万)' in i:
                    industry_sw=industry_sw+[i]
                elif '中证' in i:
                    industry_zz=industry_zz+[i]
                elif '国证' in i:
                    industry_gz=industry_gz+[i] 
                else:
                    industry_others=industry_others+[i]
            print("  Supported industry indexes:")
            printlist(industry_sw,numperline=5,beforehand='  ',separator=' ')
            printlist(industry_zz,numperline=5,beforehand='  ',separator=' ')
            printlist(industry_gz,numperline=5,beforehand='  ',separator=' ')
            printlist(industry_others,numperline=5,beforehand='  ',separator=' ')
            
            return None
        
        if dft is None: continue
        
        dft['Date']=dft['日期'].apply(lambda x: pd.to_datetime(x))
        dft.set_index('Date',inplace=True)
        dft['name']=iname
        dft['currency']=''
        dft[i]=dft[t]
        dftp=dft[(dft.index >= startdt) & (dft.index <= enddt)]
        
        dft1=dftp[[i,'name','currency']]
        """
        if not (dft1 is None):
            columns=create_tuple_for_columns(dft1,iname)
            dft1.columns=pd.MultiIndex.from_tuples(columns)        
        """
        if df is None:
            df=dft1
        else:
            df=pd.merge(df,dft1,how='outer',left_index=True,right_index=True)
    
    # 去掉多余的name/currency重复列
    if df is None: return None    
    collist=list(df)
    if not (('name' in collist) and ('currency' in collist)):
        df.rename(columns={'name_x':'name','currency_x':'currency'},inplace=True)

    collist=list(df)
    collist1=[]
    for c in collist:
        if "_" not in c:
            collist1=collist1+[c]        

    df1=df[collist1]
    
    return df1 

#==============================================================================
if __name__=='__main__':
    print(is_alphanumeric("abc123"))   # True
    print(is_alphanumeric("abcd123!"))  # False
    print(is_alphanumeric("1234567890")) # True
    print(is_alphanumeric("Hello World")) # False
    print(is_alphanumeric("中证500"))
 
def is_alphanumeric(string):
    import re
    pattern = r'^[a-zA-Z0-9]+$' # 定义正则表达式模式
    
    if re.match(pattern, string):
        return True
    else:
        return False


#==============================================================================
if __name__=='__main__':
    code='H30533.ZZ'
    code='801730.SW'
    
    funddb_name(code)
    

def funddb_name(code):
    """
    翻译指数代码为韭圈儿名称。指数估值专用！
    输入：指数代码。输出：韭圈儿指数名称
    """
    import pandas as pd
    ecdict=pd.DataFrame([
        
        # 申万行业/主题指数
        ['801735.SW','光伏设备(申万)'],
        ['801730.SW','电力设备(申万)'],
        ['801780.SW','银行(申万)'],
        ['801740.SW','国防军工(申万)'],
        ['801720.SW','建筑装饰(申万)'],
        ['801110.SW','家用电器(申万)'],
        ['801102.SW','通信设备(申万)'],
        ['801194.SW','保险Ⅱ(申万)'],
        ['801770.SW','通信(申万)'],
        ['801050.SW','有色金属(申万)'],
        ['801812.SW','中盘指数(申万)'],
        ['801152.SW','生物制品(申万)'],
        ['801811.SW','大盘指数(申万)'],
        ['801970.SW','环保(申万)'],
        ['801120.SW','食品饮料(申万)'],
        ['801170.SW','交通运输(申万)'],
        ['801150.SW','医药生物(申万)'],
        ['801980.SW','美容护理(申万)'],
        ['801160.SW','公用事业(申万)'],
        ['801950.SW','煤炭(申万)'],
        ['801151.SW','化学制药(申万)'],
        ['801130.SW','纺织服饰(申万)'],
        ['801960.SW','石油石化(申万)'],
        ['801890.SW','机械设备(申万)'],
        ['801790.SW','非银金融(申万)'],
        ['801813.SW','小盘指数(申万)'],
        ['801030.SW','基础化工(申万)'],
        ['801193.SW','券商Ⅱ(申万)'],
        ['801210.SW','社会服务(申万)'],
        ['801140.SW','轻工制造(申万)'],
        ['801760.SW','传媒(申万)'],
        ['801710.SW','建筑材料(申万)'],
        ['801080.SW','电子(申万)'],
        ['801040.SW','钢铁(申万)'],
        ['801200.SW','商贸零售(申万)'],        
        ['801017.SW','养殖业(申万)'],        
        ['801180.SW','房地产(申万)'],        
        ['801230.SW','综合(申万)'],
        ['801010.SW','农林牧渔(申万)'],
        ['801880.SW','汽车(申万)'],
        ['801736.SW','风电设备(申万)'],
        ['801750.SW','计算机(申万)'],

        # 沪深交易所行业指数
        ['000688.SS','科创50'],#上证科创板50成份指数由上海证券交易所科创板中市值大、流动性好的50只证券组成
        ['399976.SZ','CS新能车'],
        ['399995.SZ','中证基建工程'],
        ['399812.SZ','养老产业'],
        ['000986.SS','全指能源'],        
        ['399986.SZ','中证银行'],        
        ['000992.SS','全指金融地产'],        
        ['000991.SS','全指医药'],        
        ['399285.SZ','物联网50'],        
        ['399997.SZ','中证白酒'],        

        ['000987.SS','全指材料'],
        ['000993.SS','全指信息'],
        ['399610.SZ','TMT50'],#深证TMT50指数, 科技（Technology）、媒体（Media）和电信(Telecom)类上市公司
        ['399975.SZ','证券公司'],        
        ['399804.SZ','中证体育'],        
        ['399285.SZ','物联网50'],        
        ['399998.SZ','中证煤炭'],  
        ['000932.SS','中证消费'],  
        ['399970.SZ','中证移动互联'],  
        ['399971.SZ','中证传媒'],  
        ['000827.SS','中证环保'],  
        ['399808.SZ','中证新能'],  
        ['399967.SZ','中证军工'],  
        ['000933.SS','中证医药'],  
        ['000934.SS','中证金融'],  
        ['399989.SZ','中证医疗'],  
        ['399441.SZ','国证生物医药'],  
        ['399707.SZ','CSSW证券'],#中证申万证券行业指数(CSSW证券)和中证全指证券公司指数(证券公司),完全是关于证券行业的指数
        ['000057.SS','全指成长'], 
        ['000058.SS','全指价值'], 
        
        # 中证行业指数
        ['930599.ZZ','中证高装'],#中证高端装备制造指数
        ['930707.ZZ','中证畜牧'],
        ['930606.ZZ','中证钢铁'],
        ['931865.ZZ','中证半导'],
        ['930743.ZZ','中证生科'],
        ['930708.ZZ','中证有色'],  
        ['930641.ZZ','中证中药'],   
        ['930771.ZZ','中证新能源'],
        ['000949.ZZ','中证农业'],   
        ['932000.ZZ','中证2000'],#中证规模指数系列
        
        ['H30533.ZZ','中国互联网50'],#中证海外中国互联网50指数选取海外交易所上市的50家中国互联网企业
        ['H30178.ZZ','医疗保健'],  
        ['H30217.ZZ','医疗器械'],#中证全指医疗保健设备与服务指数
        ['H30205.ZZ','饮料指数'],  
        ['H30199.ZZ','中证全指电力指数'],  
        ['H30184.ZZ','中证全指半导体'],          
        ['H30171.ZZ','中证全指运输指数'],     
        ['H30202.ZZ','软件指数'],
        ['H11052.ZZ','智能电车'],
        
        ['931151.ZZ','光伏产业'],
        ['930614.ZZ','环保50'],
        ['000812.ZZ','细分机械'],
        ['931755.ZZ','SEEE碳中和'],
        
        ['931719.ZZ','CS电池'],
        ['930820.ZZ','CS高端制'],          
        ['930632.ZZ','CS稀金属'],#中证稀有金属主题指数
        ['930716.ZZ','CS物流'],#中证现代物流指数选
        ['930726.ZZ','CS生医'],  
        ['930712.ZZ','CS物联网'],#中证物联网主题指数
        ['931484.ZZ','CS医药创新'],  
        ['930651.ZZ','CS计算机'],  
        ['930652.ZZ','CS电子'],#中证电子指数
        ['930713.ZZ','CS人工智'],  
        ['930838.ZZ','CS高股息'],  
        ['931152.ZZ','CS创新药'],  
        ['930721.ZZ','CS智汽车'],  
        ['931139.ZZ','CS消费50'],  
        
        ['930697.ZZ','家用电器'],
        ['931160.ZZ','通信设备'],
        
        ['000811.ZZ','细分有色'],  
        ['000813.ZZ','细分化工'],  
        ['000815.ZZ','细分食品'],  
        ['000812.ZZ','细分机械'],  
        
        ['000990.ZZ','全指消费'],  
        ['000995.ZZ','全指公用'],  
        ['000988.ZZ','全指工业'], 
        ['000994.ZZ','全指通信'], 
        
        ['930598.ZZ','稀土产业'],  
        ['930851.ZZ','云计算'],  
        ['931079.ZZ','5G通信'],  
        ['931456.ZZ','中国教育'],  
        ['931009.ZZ','建筑材料'],  
        ['931775.ZZ','中证全指房地产'],  
        
        ['931663.ZZ','SHS消费龙头'],#中证沪港深消费龙头企业指数
        ['931524.ZZ','SHS科技龙头'],#中证沪港深科技龙头指数
        ['930917.ZZ','SHS高股息(CNY)'],#中证沪港深高股息指数
        ['930625.ZZ','SHS互联网'],#中证沪港深互联网指数
        ['931470.ZZ','SHS云计算'],#中证沪港深云计算指数
        ['931409.ZZ','SHS创新药'],#中证沪港深创新药指数

        ['000859.ZZ','国企一带一路'],   
        ['931165.ZZ','新兴科技100'],#中证新兴科技100策略指数, 沪深A股新兴科技相关产业中选取高盈利能力、高成长且兼具估值水平低的股票
        
        # 主要市场通用指数
        ['399001.SZ','深证成指'],
        ['399330.SZ','深证100'],
        ['399006.SZ','创业板指'],#创业板指数
        ['399102.SZ','创业板综'],#创业板综合指数
        ['399303.SZ','国证2000'],        
        
        ['000001.SS','上证指数'],
        ['000016.SS','上证50'],
        ['000010.SS','上证180'],
        ['000009.SS','上证380'],
        
        ['000300.SS','沪深300'],
        ['000903.SS','中证100'],
        ['000905.SS','中证500'],
        ['000906.SS','中证800'],
        ['000852.SS','中证1000'],

        ['899050.BJ','北证50'],
        
        ['^FTSE','英国富时100'],
        ['^HSI','恒生指数'],
        ['^CAC','法国CAC40'],['^FCHI','法国CAC40'],
        ['^RTS','俄罗斯RTS'],
        ['^VN30','胡志明指数'],['VNINDEX','胡志明指数'],
        ['^BSESN','印度SENSEX30'],
        ['^N225','日经225'],
        ['^SPX','标普500'],['^GSPC','标普500'],
        ['^KS11','韩国综合指数'],
        ['^DJI','道琼斯工业指数'],
        ['^NDX','纳斯达克100'],
        ['^AXAT','澳洲标普200'],#澳大利亚标普200指数
        
        # 其他特色指数
        ['HSCEI.HK','ESG120策略'],#中证ESG120策略指数从沪深300指数样本股中选取ESG得分较高的120只股票
        ['HSCEI.HK','恒生中国企业指数'],#中国企业以H股形式在香港联合交易所（「联交所」）上市
        ['930931.ZZ','港股通50(HKD)'],#港股通范围内的最大50家公司
        ['HSIII.ZZ','沪港深500'],#中证沪港深500指数, 沪港深交易所上市的互联互通范围内股票
        ['HSIII.HK','恒生互联网科技业'],
        ['HSTECH.HK','恒生科技指数'],
        ['931637.ZZ','HKC互联网'],#中证港股通互联网指数, 港股通内互联网主题上市公司
        ['746059.MI','MSCI中国A50互联互通'],#上海和深圳交易所上市的中国A股大盘和中盘股票，且可通过北向交易互联互通
        ['S5HLTH','标普500医疗'],#标普500成分股中属于GICS health care sector
        ['S5INFT','标普500信息技术'],#标普500成分股中属于GICS information technology sector
        ['HSHCI.HK','恒生医疗保健'],#恒生综合指数里主要经营医疗保健业务成份股公司的表现
        ['884251.WD','猪产业指数'],#万得指数，包含种猪、肉猪养殖，肉猪屠宰及猪肉销售、猪饲料类公司
        ['884252.WD','鸡产业指数'],#万得指数，包含鸡苗、肉鸡养殖，肉鸡屠宰及鸡肉销售类公司
        ['^SOX','费城半导体指数'],#费城交易所指数，全球半导体业景气主要指标
        ['ERGLU','富时发达市场REITs'],
        
        ['980032.GZ','新能电池'],#国证新能源电池指数
        
        ['931468.ZZ','红利质量'],#中证红利质量指数，连续现金分红、股利支付率较高且具备较高盈利能力特征的上市公司股
        ['000922.ZZ','中证红利'],#中证红利指数以沪深A股中现金股息率高、分红比较稳定、具有一定规模及流动性的100只股票
        ['000825.ZZ','中证央企红利'],#中证中央企业红利指数，中央企业中现金股息率高、分红比较稳定、且有一定规模及流动性的30只股票
        ['000969.ZZ','沪深300非周期'],
        ['000821.ZZ','沪深300红利'],
        ['000968.ZZ','沪深300周期'],
        
        ], columns=['eword','cword'])

    try:
        cword=ecdict[ecdict['eword']==code]['cword'].values[0]
    except:
        #未查到代码名称，返回原代码
        cword=code
   
    return cword
#==============================================================================

if __name__=='__main__':
    tickers='AAPL'
    tickers='PZU.PL'
    tickers='JD'
    tickers='NIO'
    tickers='600519.SS'
    tickers='00700.HK'
    tickers='光伏设备(申万)'
    tickers='中证500'
    tickers='801735.SW'
    tickers='801853.SW'
    
    tickers=['PZU.PL','WIG.PL']
    tickers=['PZU.PL','JD','600519.SS','00700.HK','801735.SW','光伏设备(申万)','中证500']
    
    indicators='PE'
    indicators='PB'
    indicators=['pe','pb']
    indicators=['pe','pb','mv']
    indicators='ROE'
    
    start='2023-1-1'; end='2023-11-30'
    
    df_mix=get_valuation(tickers,indicators,start,end)

def get_valuation(tickers,indicators,start,end):
    """
    功能：获取估值信息pe/pb/mv
    若tickers为多个，则indicators取第一个
    若tickers为单个，则indicators取所有
    """
    
    if isinstance(tickers,str):
        tickers=[tickers]

    # 若遇到指数，先转换为韭圈儿的行业名称，以免被误认为股票代码
    tickers1=[]
    for t in tickers:
        t1=funddb_name(t)
        tickers1=tickers1+[t1]
        
    if isinstance(indicators,str):
        indicators=[indicators]

    # 若为多个证券代码，则仅取第一个指标        
    if len(tickers)>1:
        indicators1=[indicators[0]]
    else:
        indicators1=indicators
    
    #处理ROE，赋值indicators2，保留indicators1
    ROE_flag=False
    if 'ROE' in indicators1:
        ROE_flag=True
        indicators2=indicators1.copy() #注意：若不加copy，则仅为指针赋值，两者将联动
        indicators2.remove('ROE')
        if 'PE' not in indicators2:
            indicators2=indicators2+['PE']
        if 'PB' not in indicators2:
            indicators2=indicators2+['PB']
    
    # 百度股市百事通不支持指数估值，遇到指数代码需要先转为名称获取韭圈儿估值数据
    """
    tickers1=[]
    for t in tickers:
        t1=funddb_name(t)
        tickers1=tickers1+[t1]
    """
    df=None
    for t in tickers1:
        print("  Searchng valuation info for",t,"......")
        t1=t.upper()
        result,prefix,suffix=split_prefix_suffix(t1)
        iname=ticker_name(t1)
        
        gotit=False
        # A股或港股？
        if not gotit and (result and suffix in ['SS','SZ','BJ','HK']):   
            if ROE_flag:
                dft=get_stock_valuation_cn_hk(t1,indicators2,start,end)
                dft['ROE']=dft.apply(lambda x: x['PB']/x['PE'],axis=1)
                dft=dft[indicators1]
            else:
                dft=get_stock_valuation_cn_hk(t1,indicators1,start,end)
            if dft is not None: gotit=True
        
        # 波兰股？
        if not gotit and (result and suffix in ['PL','WA']):
            if ROE_flag:
                dft=get_stock_valuation_pl(t1,indicators2,start,end)
                dft['ROE']=dft.apply(lambda x: x['PB']/x['PE'],axis=1)
                dft=dft[indicators1]
            else:
                dft=get_stock_valuation_pl(t1,indicators1,start,end)
            if dft is not None: gotit=True

        # 行业指数代码？
        suffix_list=['SW','SI',#申万行业
                     'GI',#谷歌
                     'CSI',#中证
                     'CNI',#国证
                     'SH','SZ','BJ',#沪深京交易所
                     'WI',#万得
                     'HI',#恒生
                     'SPI',#标普
                     'MI',#MSCI
                     'BO',#孟买
                     ]
        if not gotit and (result and suffix in suffix_list) and not ROE_flag:
            
            #dft=get_index_valuation_funddb(t1,indicators1,start,end)
            indicator1=indicators1[0]
            dft0=industry_valuation_history_sw(industry=t1,
                                               start=start,end=end,
                                               vtype=indicator1,
                                               graph=False)
            dft0[indicator1]=dft0[list(dft0)[0]]
            dft0['name']=industry_sw_name(t1)
            dft0['currency']=''
            dft=dft0[[indicator1,'name','currency']]
            
            if dft is not None: 
                gotit=True 
                iname=industry_sw_name(t1)
              
        # 美股？
        if not gotit and (not result and (is_alphanumeric(prefix) or '^' in prefix)):
            if ROE_flag:
                dft=get_stock_valuation_us(t1,indicators2,start,end)
                dft['ROE']=dft.apply(lambda x: x['PB']/x['PE'],axis=1)
                dft=dft[indicators1]
            else:
                dft=get_stock_valuation_us(t1,indicators1,start,end)
            if dft is not None: gotit=True
            
       # 行业指数名称？     
        if not gotit and (not result):
            if ROE_flag:
                dft=get_index_valuation_funddb(t1,indicators2,start,end)
                dft['ROE']=dft.apply(lambda x: x['PB']/x['PE'],axis=1)
                dft=dft[indicators1]
            else:
                dft=get_index_valuation_funddb(t1,indicators1,start,end)
            if dft is not None: gotit=True
           
        if not gotit:
           print("  #Warning(get_valuation): failed to retrieve info for",t1)
           continue
       
        if not (dft is None):
            columns=create_tuple_for_columns(dft,iname)
            dft.columns=pd.MultiIndex.from_tuples(columns)  
        
        # 合成    
        if df is None:
            df=dft
        else:
            #df=pd.merge(df,dft,how='inner',left_index=True,right_index=True)
            df=pd.merge(df,dft,how='outer',left_index=True,right_index=True)
    
    # 缺失值填充
    if not (df is None):
        #df.fillna(method='backfill',inplace=True)
        df.fillna(method='ffill',inplace=True)
    else:
        return None
    
    # 处理字段名称后面的_x/_y/_z
    df_collist=list(df)
    df1=df
    df1_collist=[]
    
    for c in df_collist:
        c1,c2=c
        c1x=c1.split('_')[0]
        cx=(c1x,c2)
        cx=tuple(cx)    #必须为元组
        
        df1_collist=df1_collist+[cx]    #列表中必须为元组
        
    df1.columns=pd.MultiIndex.from_tuples(df1_collist)  #统一修改元组型列名
    df1.dropna(inplace=True)    
        
    return df1


#==============================================================================
if __name__=='__main__':
    tickers='PZU.PL'
    indicators='PE'
    start='2023-1-1'; end='2023-11-30'
    loc1='best'
    
    tickers='PZU.PL'
    indicators=['PE','PB']
    start='2023-1-1'; end='2023-11-30'
    twinx=True
    loc1='lower left'; loc2='upper right'
    
    tickers=['JD','PDD']
    indicators='PE'
    start='2023-1-1'; end='2023-11-30'
    twinx=True
    loc1='lower left'; loc2='upper right'
    
    tickers=['600519.SS','000858.SZ']
    indicators='PE'
    start='2023-1-1'; end='2023-11-30'
    twinx=True
    loc1='lower left'; loc2='upper right'
    
    tickers=['JD','PDD','BABA']
    indicators='PE'
    start='2023-1-1'; end='2023-11-30'
    loc1='best'
    
    tickers='JD'
    indicators=['PE','PB','MV']
    start='2023-1-1'; end='2023-11-30'
    loc1='best'
    
    tickers=['AAPL','MSFT']
    indicators='ROE'
    indicators='PE'
    indicators='PB'
    start='2023-1-1'; end='2023-12-31'
    loc1='best'
    
    val=security_valuation(tickers,indicators,start,end)

def security_valuation(tickers,indicators,start,end, \
                       preprocess='none',scaling_option='start', \
                       twinx=False,loc1='best',loc2='best', \
                       graph=True,facecolor='whitesmoke', \
                            attention_value='',attention_value_area='', \
                            attention_point='',attention_point_area='', \
                                band_area='', \
                       annotate=False,annotate_value=False, \
                       mark_top=False,mark_bottom=False, \
                       mark_start=False,mark_end=False):
    """
    功能：绘制估值走势
    """
    
    # 获取估值信息
    df=get_valuation(tickers,indicators,start,end)
    if df is None:
        print("  #Warning(security_valuation): retrieved none of",indicators,"for",tickers)
        return None

    if not graph: return df

    # 判断估值信息结构
    names=[]
    indicators=[]
    
    mcollist=list(df)
    for mc in mcollist:
        if mc[0] not in ['name','currency']:
            indicators=indicators+[mc[0]]
            names=names+[mc[1]]
    
    names1=list(set(names))
    indicators1=list(set(indicators))
    
    name_num=len(names1)
    indicator_num=len(indicators1)

        
    # 将band_area中的ticker替换为tname
    if band_area != '':
        if name_num > 1:
            # 假定band_area里面的是ticker
            for index, item in enumerate(band_area):
                tname=ticker_name(item)
                if tname in names1:
                    band_area[index] = tname    
                else:
                    band_area.remove(item)

        if name_num == 1 and indicator_num > 1:
            # 假定band_area里面的是indicator
            for index, item in enumerate(band_area):
                if item not in indicators1:
                    band_area.remove(item)
                    
        if len(band_area) != 2:
            band_area=''
            print("  #Warning(security_valuation): band_area does not match ticker or indicator")

    import datetime
    # 绘制一条线+均值/中位数虚线
    if name_num * indicator_num == 1:
        i=indicators1[0]
        t=names1[0]
        df2=df[i]
        df2.rename(columns={t:i},inplace=True)
        
        df2['平均值']=df2[i].mean()
        df2['中位数']=df2[i].median()
        
        #ylabeltxt=i
        ylabeltxt=ectranslate(i)
        df2.rename(columns={i:ectranslate(i)},inplace=True)
        
        titletxt="证券估值走势："+t   
        
        footnote1=""
        if i=='MV':
            if preprocess=='none':
                footnote1="注：市值金额：十亿，本币单位\n"
                
        todaydt = datetime.date.today()
        footnote9="数据来源: Baidu/Stooq/FundDB/SWHY，"+str(todaydt)
        footnote=footnote1+footnote9
        
        draw_lines(df2,y_label=ylabeltxt,x_label=footnote, \
                   axhline_value=0,axhline_label='', \
                   title_txt=titletxt,data_label=False, \
                   resample_freq='D',loc=loc1,facecolor=facecolor, \
                        attention_value=attention_value,attention_value_area=attention_value_area, \
                        attention_point=attention_point,attention_point_area=attention_point_area, \
                   annotate=annotate,annotate_value=annotate_value, \
                   mark_top=mark_top,mark_bottom=mark_bottom, \
                   mark_start=mark_start,mark_end=mark_end)        
        
        return df
        
    # 绘制双线: 一只证券，两个指标。twinx双轴绘图，注意twinx曲线容易误导走势
    if name_num == 1 and indicator_num == 2 and twinx: 
        t=names1[0]
        i1=indicators1[0]; i2=indicators1[1]
        df2_1=df[i1]; df2_2=df[i2]
        
        df2_1.rename(columns={t:i1},inplace=True)
        df2_2.rename(columns={t:i2},inplace=True)
        
        titletxt="证券估值走势："+t   
        
        footnote1=""
        if i1=='MV' or i2=='MV':
            if preprocess=='none':
                footnote1="注：市值金额：十亿，本币单位\n"
                
        todaydt = datetime.date.today()
        footnote9="数据来源: Baidu/Stooq/FundDB/SWHY，"+str(todaydt)
        footnote=footnote1+footnote9
        
        df2_1.rename(columns={i1:ectranslate(i1)},inplace=True)
        df2_2.rename(columns={i2:ectranslate(i2)},inplace=True)
        
        colname1=label1=ectranslate(i1)
        colname2=label2=ectranslate(i2)
        
        plot_line2(df2_1,'',colname1,label1, \
                   df2_2,'',colname2,label2, \
                   ylabeltxt='',titletxt=titletxt,footnote=footnote, \
                   twinx=twinx, \
                   resample_freq='D',loc1=loc1,loc2=loc2, \
                   color1='red',color2='blue',facecolor=facecolor, \
                        yline=attention_value,attention_value_area=attention_value_area, \
                        xline=attention_point,attention_point_area=attention_point_area, \
                  )
            
        return df
   
    # 绘制双线: 两只证券，一个指标。twinx双轴绘图
    if name_num == 2 and indicator_num == 1 and twinx:
        t1=names1[0]; t2=names1[1]
        i=indicators1[0]
        df2_1=pd.DataFrame(df[i,t1])[i]; df2_2=pd.DataFrame(df[i,t2])[i]
        df2_1.rename(columns={t1:i},inplace=True)
        df2_2.rename(columns={t2:i},inplace=True)
        
        #titletxt="证券估值走势："+i
        titletxt="证券估值走势："+ectranslate(i)
        
        footnote1=""
        if i=='MV':
            if preprocess=='none':
                footnote1="注：市值金额：十亿，本币单位\n"
                
        todaydt = datetime.date.today()
        footnote9="数据来源: Baidu/Stooq/FundDB/SWHY，"+str(todaydt)
        footnote=footnote1+footnote9
        
        colname1=i; label1=t1
        colname2=i; label2=t2
        
        if twinx:
            ylabeltxt=''
        else:
            #ylabeltxt=i
            ylabeltxt=ectranslate(i)
        
        plot_line2(df2_1,'',colname1,label1, \
                   df2_2,'',colname2,label2, \
                   ylabeltxt=ylabeltxt,titletxt=titletxt,footnote=footnote, \
                   twinx=twinx, \
                   resample_freq='D',loc1=loc1,loc2=loc2, \
                   color1='red',color2='blue',facecolor=facecolor, \
                        yline=attention_value,attention_value_area=attention_value_area, \
                        xline=attention_point,attention_point_area=attention_point_area, \
                 )

        return df                
   
    lang=check_language()
    # 绘制多线：多只证券，一个指标。简单多线绘图
    if name_num >= 2 and indicator_num == 1 and not twinx: 
        i=indicators1[0]
        df2=df[i]
        
        titletxt="证券估值走势："+ectranslate(i)   
        
        footnote1=""
        if i=='MV':
            if preprocess=='none':
                footnote1="注：市值金额：十亿，本币单位\n"
                
        todaydt = datetime.date.today()
        footnote9="数据来源: Baidu/Stooq/FundDB/SWHY，"+str(todaydt)
        footnote=footnote1+footnote9
        
        #ylabeltxt=i
        ylabeltxt=ectranslate(i) 

        # 标准化处理
        dfs2,axhline_label,x_label,y_label,plus_sign=df_preprocess(df2,measure=indicators1, \
                axhline_label='',x_label=footnote,y_label=ylabeltxt, \
                preprocess=preprocess,scaling_option=scaling_option)

        draw_lines(dfs2,y_label=y_label,x_label=x_label, \
                   axhline_value=0,axhline_label=axhline_label, \
                   title_txt=titletxt,data_label=False, \
                   resample_freq='D',loc=loc1, \
                   annotate=annotate,annotate_value=annotate_value, \
                       band_area=band_area, \
                   plus_sign=plus_sign, \
                   facecolor=facecolor, \
                        attention_value=attention_value,attention_value_area=attention_value_area, \
                        attention_point=attention_point,attention_point_area=attention_point_area, \
                   mark_top=mark_top,mark_bottom=mark_bottom, \
                   mark_start=mark_start,mark_end=mark_end)        
        
        return df        
   
    # 绘制多线：一只证券，多个指标。简单多线绘图。可能数量级差异较大，意义有限
    if name_num == 1 and indicator_num >= 2 and not twinx: 
        t=names1[0]
        df2=None
        for i in indicators1:
            dft=pd.DataFrame(df[i,t])[i]
            dft.rename(columns={t:i},inplace=True)
            
            if df2 is None:
                df2=dft
            else:
                df2=pd.merge(df2,dft,left_index=True,right_index=True)
                
            df2.rename(columns={i:ectranslate(i)},inplace=True)
        
        titletxt="证券估值走势："+t   
        
        footnote1=''
        if 'MV' in indicators1:
            if preprocess=='none':
                footnote1="注：市值金额：十亿，本币单位\n"
            
        todaydt = datetime.date.today()
        footnote9="数据来源: Baidu/Stooq/FundDB/SWHY，"+str(todaydt)
        footnote=footnote1+footnote9
        
        #ylabeltxt=''
        ylabeltxt="估值"
        
        # 标准化处理
        dfs2,axhline_label,x_label,y_label,plus_sign=df_preprocess(df2,measure=indicators1, \
                axhline_label='',x_label=footnote,y_label=ylabeltxt, \
                preprocess=preprocess,scaling_option=scaling_option)
        
        draw_lines(dfs2,y_label=y_label,x_label=x_label, \
                   axhline_value=0,axhline_label=axhline_label, \
                   title_txt=titletxt,data_label=False, \
                   resample_freq='D',loc=loc1,plus_sign=plus_sign, \
                   annotate=annotate,annotate_value=annotate_value, \
                       band_area=band_area, \
                   facecolor=facecolor, \
                        attention_value=attention_value,attention_value_area=attention_value_area, \
                        attention_point=attention_point,attention_point_area=attention_point_area, \
                   mark_top=mark_top,mark_bottom=mark_bottom, \
                   mark_start=mark_start,mark_end=mark_end)        
        
        return df 
                
        
#==============================================================================
if __name__=='__main__':
    bank_big=find_peers_china('国有大型银行Ⅱ',top=25)
    df=security_trend(bank_big,indicator='PE',start='MRY',graph=False) 
    indicator='PE'
    base='601398.SS'
    
    
def print_valuation(df,indicator='PE',base='',facecolor='whitesmoke'):
    """
    功能：显示同行估值数字，并进行对比
    """
    try:
        df1=df[indicator]
    except:
        print(f"  #Warning(print_valuation): unsupported indicator {indicator} in current dataframe")
        return
    
    collist=list(df1)
    base=base.upper()
    base=ticker_name(base)
    if not (base in collist):
        """
        print("  #Warning(print_valuation): invalid item",base,"for current dataframe")
        print("  Valid items in current dataframe:\n",collist)
        return
        """
        base=collist[0]
    
    df2=df1.T
    latest_date=list(df2)[-1]   #最后日期
    col_latest_date=latest_date.strftime('%y-%m-%d')
    start_date=list(df2)[0]   #开始日期
    col_start_date=start_date.strftime('%y-%m-%d')    
    """
    col_mean="期间内"+indicator+'均值'
    col_mean_rel=indicator+'均值相对倍数'
    col_mean_pct=indicator+'均值分位数'
    """
    col_mean="期间内均值"
    col_mean_rel='均值相对倍数'
    
    df2[col_mean]=df2.mean(axis=1)
    
    df2[col_mean]=df2[col_mean].apply(lambda x: round(x,2))
    
    df2.sort_values(col_mean,ascending=False,inplace=True)
    
    df3=df2[df2[col_mean] > 0]
    diff=len(df2) - len(df3)
    if diff > 0:
        df3t=df2[df2[col_mean] <= 0]
        diff_list=list(df3t.index)
    
    df3['均值排名']=range(len(df3))
    df3['均值排名']=df3['均值排名'] + 1
    df3['证券名称']=df3.index
    
    # 均值基准
    base_value=df3[df3.index == base][col_mean].values[0]
    df3[col_mean_rel]=df3[col_mean].apply(lambda x: round(x / base_value,2))

    # 最新值基准
    base_value_latest=df3[df3.index == base][latest_date].values[0]
    df3[col_latest_date]=df3[latest_date]
    col_latest_rel='相对倍数@'+col_latest_date
    df3[col_latest_rel]=df3[col_latest_date].apply(lambda x: round(x / base_value_latest,2))
    
    df3.sort_values(col_latest_date,ascending=False,inplace=True)
    df3['排名@'+col_latest_date]=range(len(df3))
    df3['排名@'+col_latest_date]=df3['排名@'+col_latest_date] + 1
    df3.sort_values(col_mean,ascending=False,inplace=True)
    
    # 变化    
    df3['均值对比']=df3[col_mean_rel].apply(lambda x: '0%' if x == 1 else '+'+str(round((x-1)*100,2))+'%' if x >1 else '-'+str(round((1-x)*100,2))+'%')
    df3['对比@'+col_latest_date]=df3[col_latest_rel].apply(lambda x: '0%' if x == 1 else '+'+str(round((x-1)*100,2))+'%' if x >1 else '-'+str(round((1-x)*100,2))+'%')
    
    df3['均值对比']=df3.apply(lambda x: '<---基准' if x['证券名称'] == base else x['均值对比'],axis=1)
    df3['对比@'+col_latest_date]=df3.apply(lambda x: '<---基准' if x['证券名称'] == base else x['对比@'+col_latest_date],axis=1)

    #df4=df3[['序号','证券名称',col_mean,col_mean_rel,'均值对比',col_latest_date,col_latest_rel,'对比@'+col_latest_date]]
    df4=df3[['证券名称',col_mean,'均值排名',col_latest_date,'排名@'+col_latest_date,col_mean_rel,col_latest_rel,'均值对比','对比@'+col_latest_date]]
    
    #titletxt="估值对比："+ectranslate(indicator)+"，降序排列"
    titletxt="证券估值对比：{0}({1})，降序排列".format(ectranslate(indicator),indicator)
    """
    print("\n",titletxt,'\n')
    alignlist=['left','right','center','right','center']+['right']*(len(list(df4))-5)
    print(df4.to_markdown(index=False,tablefmt='simple',colalign=alignlist))
    """
    disph=df4.style.hide() #不显示索引列
    dispp=disph.format(precision=2) #设置带有小数点的列精度调整为小数点后2位
    #设置标题/列名
    dispt=dispp.set_caption(titletxt).set_table_styles(
        [{'selector':'caption', #设置标题
          'props':[('color','black'),('font-size','16px'),('font-weight','bold')]}, \
         {'selector':'th.col_heading', #设置列名
           'props':[('color','black'),('text-align','center'),('margin','auto')]}])        
    #设置列数值对齐
    dispf=dispt.set_properties(**{'text-align':'center'})
    #设置前景背景颜色
    #dispf2=dispf.set_properties(**{'background-color':facecolor,'color':fontcolor})
    dispf2=dispf.set_properties(**{'background-color':facecolor})

    from IPython.display import display
    display(dispf2)
    
    #print(" ")
    if diff > 0:
        print("【注】未列出"+str(diff)+"只估值为非正数的证券："+str(diff_list))
    import datetime; todaydt = datetime.date.today()
    footnote="估值期间："+col_start_date+"至"+col_latest_date+"，数据来源: baidu/stooq/funddb/swhysc，"+str(todaydt)
    print(footnote)   

    return


#==============================================================================
if __name__=='__main__':
    df=security_trend("00700.HK",start="MRY",power=8)
    valuation_summary(df,column='Close',decimal=1)
    
def valuation_summary(df,column='Close',decimal=1):
    """
    功能：快速概括df中某列column的统计特点
    """
    if not (column in list(df)):
        print("  #Warning: "+column+" is not a valid column of the dataframe")
        return
    
    val_min=round(df[column].min(),decimal)
    date_min=df[column].idxmin()
    date_min=pd.to_datetime(date_min).strftime('%Y-%m-%d')
    
    val_max=round(df[column].max(),decimal)
    date_max=df[column].idxmax()
    date_max=pd.to_datetime(date_max).strftime('%Y-%m-%d')
    
    val_mean=df[column].mean()
    val_std_pct=df[column].std() / val_mean
    val_std_pct_str=str(round(val_std_pct*100,1))+'%'
    val_median=round(df[column].median(),decimal)
    
    # 计算分位数
    from scipy.stats import percentileofscore
    sspos=lambda x:percentileofscore(df[column],x,kind='weak')
    df['PCT']=df[column].apply(sspos)    
    
    latest=round(df.tail(1)[column].values[0],decimal)
    latest_pct=round(df.tail(1)['PCT'].values[0],1)
    latest_date=pd.to_datetime(df.tail(1).index.values[0])
    latest_date=latest_date.strftime('%Y-%m-%d')
    
    start_date=pd.to_datetime(df.head(1).index.values[0])
    start_date=start_date.strftime('%Y-%m-%d')
    
    print('')
    print("期间：从"+start_date+'至'+latest_date)
    print("\n范围：最低"+str(val_min)+' @'+date_min,'\b，最高'+str(val_max)+' @'+date_max)
    print('均值:',round(val_mean,decimal),'\b, 中位数:',val_median,end=', ')
    print('波动率:',val_std_pct_str)
    
    print("\n末端:",latest,'\b, 分位数:',str(latest_pct)+'%, @'+latest_date)
    
    return
     
#==============================================================================
#==============================================================================
#==============================================================================
#==============================================================================
#==============================================================================

