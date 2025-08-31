# -*- coding: utf-8 -*-
"""
本模块功能：SIAT公共转换函数，获取雅虎证券代码英文名称
所属工具包：证券投资分析工具SIAT 
SIAT：Security Investment Analysis Tool
创建日期：2024年7月12日
最新修订日期：
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
if __name__=='__main__':
    test_yahoo_access()
    
def test_yahoo_access():
    """
    功能：测试雅虎财经是否可达
    """
    url="https://finance.yahoo.com/"
    result=test_website(url)
    
    return result    

if __name__=='__main__':
    url="https://finance.yahoo.com"
    test_website(url)
    
def test_website(url):
    import requests
    headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    try:
        response = requests.get(url,headers=headers)
        if response.status_code == 200:
            #print(f"Website {url} is accessible")
            return True
        else:
            #print(f"Website {url} access failed，Code：{response.status_code}")
            return False
    except requests.exceptions.RequestException:
        print(f"  #Warning: website {url} is inaccessible")
        return False
 
if __name__=='__main__':
    s = "Hello, world. Python is fun!"
    split_string(s)
 
def split_string(s):
    import re
    # 使用正则表达式匹配空格、逗号或句点
    return re.split(r'[ ,.]', s)

if __name__=='__main__':
    s = "Hello, world. Python is fun!"
    filter_string(s)
    
def filter_string(s):
    #排除证券名称中的多余空格、逗号和句号
    slist=split_string(s)
    s1=''
    for sl in slist:
        if sl != '':
            if s1=='':
                s1=sl
            else:
                s1=s1+' '+sl
            
    return s1
#==============================================================================
if __name__=='__main__':
    ticker='1155.KL'
    ticker='MSFT'
    ticker='G13.SI'
    ticker='S63.SI'
    ticker='SUS.ST'
    ticker='600519.SS'
    ticker='U11.SI'
    ticker='1295.KL'
    ticker='BMW.DE'
    ticker='MBG.DE'
    ticker='005930.KS'
    ticker='LI'
    ticker='600599.SS'
    ticker='600123.SS'
    ticker='600123.ss'
    ticker='600999.ss'
    ticker='600111.ss'
    ticker='600333.ss'
    ticker='600444.ss'
    ticker='600777.ss'
    ticker='GC=F'
    
    yahoo_name1(ticker)
    
    #极端测试
    inamelist=[]
    for i in range(100,150+1):
        icode=str(600000+i)+'.SS'
        iname=yahoo_name1(icode)
        print(icode+':',iname)
        inamelist=inamelist+[iname]
    
    #发现问题后单独测试
    ticker='600087.SS'
    yahoo_name1(ticker)
    
    yahoo_name1(ticker,short_name=True)
    
    ticker_name(ticker)
    
def yahoo_name1x(ticker,short_name=False,add_suffix=True,maxlen=80):
    """
    功能：从雅虎财经取得全球证券名称，仅限英文。需要去掉常用词，如Corporation
    优点：对未定义的证券代码也可给出英文名称，即使在中文语言环境中
    现存问题：需要访问雅虎，且耗时稍长
    废弃！！！
    """
    #测试雅虎
    if not test_yahoo_access():
        return ticker
    
    #需要去掉的单词，注意顺序不要轻易颠倒！子串包含的，要长文在前！
    remove_list=['Corporation','Berhad','Bhd','PLC','plc','Plc', \
                 ', Inc.','Inc.', \
                 'AG ST','AG','NA O.N.', \
                 'Aktiengesellschaft','(publ)', \
                 ', LLC','LLC', \
                 'Co., Ltd.','Co., Ltd','Co.,Ltd.','Co.,Ltd','Co,.Ltd','co.,ltd', \
                 'Co. LTD','CO.,LTD','Co., Limited', \
                 'Ltd.','Ltd', \
                 'Company', \
                 'Incorporated', \
                 'Corp., Ltd.','Corp.','Corp','AB', \
                'Limited', \
                
                #强行缩短名称长度，去掉不影响名称的花哨词语
                '(Group)','Group', \
                'Science & Technology','High-Tech','High Technology', \
                
                #扫尾漏网之逗号句点
                 '.',',']
        
    """
    remove_list=['Corporation','Berhad','Bhd','PLC','plc','Limited', \
                 'Inc', \
                 'AG ST','AG','NA O.N.', \
                 'Aktiengesellschaft','(publ)', \
                 'LLC', \
                 'Co., Ltd.','Ltd.','Ltd', \
                 'Company', \
                 'Incorporated','Corp.','AB']
    """
    #去掉ticker中的.US后缀
    ticker=ticker.upper()
    ticker1=ticker.replace('.US', "")
    
    import yfinance as yf
    ticker_info = yf.Ticker(ticker1)
    
    try:
        t_info=ticker_info.info
    except:
        pass
        return ticker
    
    try:
        if short_name:
            t_name0=t_info['shortName']
        else:
            t_name0=t_info['longName']
            if len(t_name0) > maxlen:
                t_name0=t_info['shortName']
    except:
        pass
        return ticker #未找到ticker
    
    #过滤逗号句点?过滤也可能带来更多复杂性！
    #t_name1=filter_string(t_name0)
    t_name1=t_name0
    
    for r in remove_list:
        t_name1=t_name1.replace(r, "")

    #排除前后空格        
    t_name=t_name1.strip()
    
    #增加交易所后缀
    if add_suffix:
        tlist=ticker.split('.')
        if len(tlist)==2:
            sid=tlist[1]
            if sid not in ['SS','SZ','BJ']:
                t_name=t_name+'('+sid+')'
    
    return t_name

#==============================================================================
def replace_multiple_spaces(s):
    import re
    return re.sub(r'\s+', ' ', s)

#==============================================================================
if __name__=='__main__':
    ticker='1155.KL'
    ticker='MSFT'
    ticker='G13.SI'
    ticker='S63.SI'
    ticker='SUS.ST'
    ticker='600519.SS'
    ticker='U11.SI'
    ticker='1295.KL'
    ticker='BMW.DE'
    ticker='MBG.DE'
    ticker='005930.KS'
    ticker='LI'
    ticker='600599.SS'
    ticker='600123.SS'
    ticker='600123.ss'
    ticker='600999.ss'
    ticker='600111.ss'
    ticker='600333.ss'
    ticker='600444.ss'
    ticker='600777.ss'
    ticker='CPL.WA'
    
    ticker='SWMCX'
    
    yahoo_name1(ticker)
    
    #极端测试
    inamelist=[]
    for i in range(0,50+1):
        icode=str(600000+i)+'.SS'
        iname=yahoo_name2(icode)
        print(icode+':',iname)
        inamelist=inamelist+[iname]
    
    #发现问题后单独测试
    ticker='600088.SS'
    ticker="ALI=F"
    ticker="ZS=F"
    ticker="ES=F"

    ticker_info(ticker)
    
    yahoo_name1(ticker)
    yahoo_name2(ticker)
    
    yahoo_name2(ticker,short_name=True)
    
    ticker_name(ticker)

    numeric_to_date(1734652800)
    
def numeric_to_date(numeric):
    # 数值转日期
    from datetime import datetime, timedelta
    epoch = datetime(1970, 1, 1)
    return (epoch + timedelta(seconds=numeric)).strftime('%Y-%m-%d')

if __name__=='__main__':
    ticker="ES=F" #期货
    ticker="VIX241120C00035000" #期权

    ticker_info(ticker, info="interest")
    ticker_info(ticker, info="open interest")
    ticker_info(ticker, info="volume")
    ticker_info(ticker, info="average volume")
    ticker_info(ticker, info="REGULAR CLOSE")
    ticker_info(ticker, info="day average")
    
    ticker_info(ticker, info=["regular close","fifty day average","two hundred day average"])

def ticker_info(ticker,info="all"):
    """
    
    功能：显示yahoo证券代码的信息，可多个信息类型
    """   
    if isinstance(info,str):
        infos=[info]
    elif isinstance(info,list):
        infos=info
    else:
        print("  Sorry, unsupported info type:",info)
        return
    
    first_time=True
    for i in infos:
        if first_time:
            ticker_info1(ticker,info=i,test_access=True,print_title=True)
            first_time=False
        else:
            ticker_info1(ticker,info=i,test_access=False,print_title=False)
            
    return

if __name__=='__main__':
    ticker="TSLA260618C00330000" 
    
    ticker_info1(ticker)
    ticker_info1(ticker, info="open interest")
    
def ticker_info1(ticker,info="all",test_access=True,print_title=True):
    """
    
    功能：显示yahoo证券代码的信息，1个信息类型
    """    
    #测试雅虎
    if test_access:
        if not test_yahoo_access():
            print("  Sorry, data source Yahoo is currently not reachable")
            return
        
    #去掉ticker中的.US后缀
    ticker=ticker.upper()
    ticker1=ticker.replace('.US', "")
    
    import yfinance as yf
    ticker_info = yf.Ticker(ticker1)

    import datetime
    stoday = datetime.date.today().strftime("%Y-%m-%d")
    
    info_list=info.split(); found=False
    """
    info_yahoo=(info_list[0]).lower()
    for i in info_list[1:]:
        info_yahoo=info_yahoo+(i.lower()).capitalize()
    """
    
    try:
        t_info=ticker_info.info
        
        if print_title:
            print("*** Ticker",ticker,'Information @'+stoday)
        
        if ('all' in info) or ('All' in info) or ('ALL' in info):
            for k in t_info.keys():
                if not 'Date' in k:
                    print('  '+k+':',t_info[k])
                else:
                    print('  '+k+':',numeric_to_date(t_info[k]))
            #display(t_info)
        else:
            for k in t_info.keys():
                for i in info_list:
                    if (not i.lower() in k) and (not (i.lower()).capitalize() in k):
                        found=False; break
                    else:
                        found=True
                if not found: continue
             
                if not 'Date' in k:
                    print('  '+k+':',t_info[k])
                else:
                    print('  '+k+':',numeric_to_date(t_info[k]))

    except:
        print("  Sorry, ticker",ticker,"is not found in data source Yahoo")
    
    return
        

if __name__=='__main__':
    ticker="SGC=F"
    ticker="XAUUSD"
    short_name=False;add_suffix=True;maxlen=80
    
    yahoo_name1y(ticker)
    
def yahoo_name1y(ticker,short_name=False,add_suffix=True,maxlen=80):
    """
    功能：从雅虎财经取得全球证券名称，仅限英文。需要去掉常用词，如Corporation
    优点：对未定义的证券代码也可给出英文名称，即使在中文语言环境中
    现存问题：需要访问雅虎，且耗时稍长；当ticker不存在时会提示一大堆错误信息
    仅作备用
    """
    
    #测试雅虎
    if not test_yahoo_access():
        return ticker
        
    #去掉ticker中的.US后缀
    ticker=ticker.upper()
    ticker1=ticker.replace('.US', "")
    
    import yfinance as yf
    ticker_info = yf.Ticker(ticker1)

    import os, sys
    class HiddenPrints:
        def __enter__(self):
            self._original_stdout = sys.stdout
            sys.stdout = open(os.devnull, 'w')

        def __exit__(self, exc_type, exc_val, exc_tb):
            sys.stdout.close()
            sys.stdout = self._original_stdout

    try:
        with HiddenPrints():
            t_info=ticker_info.info
    except:
        pass
        return ticker
    
    try:
        if short_name:
            try:
                t_name0=t_info['shortName']
            except:
                t_name0=t_info['longName']
        else:
            try:
                t_name0=t_info['longName']
            except:
                try:
                    t_name0=t_info['shortName']
                except:
                    pass
                    return ticker

                
            if len(t_name0) > maxlen:
                t_name0=t_info['shortName']
    except:
        pass
        return ticker #未找到ticker
    
    #过滤名称中多余的尾部词汇
    t_name=filter_stock_name(t_name0)
    
    #增加交易所后缀
    if add_suffix:
        tlist=ticker.split('.')
        if len(tlist)==2:
            sid=tlist[1]
            if sid not in ['SS','SZ','BJ']:
                t_name=t_name+'('+sid+')'
    
    return t_name

#==============================================================================
if __name__ == '__main__':
    stock_code='KSL.AX'
    stock_code='AAPL'
    stock_code='600519.SS'
    stock_code='6758.T'
    stock_code='6758.JP'
    stock_code='ULVR.L'
    stock_code='ULVR.UK'
    
    stock_code='1155.KL'
    stock_code='MSFT'
    
    stock_code='SWMCX'
    stock_code='SGC=F'
    
    yahoo_name1_direct(stock_code)

 
def yahoo_name1_direct(stock_code,add_suffix=True):
    """
    功能：网页直接抓取，有的带后缀的股票代码可能失败，原因未知
    """
    import requests
    from bs4 import BeautifulSoup
    
    stock_code1=stock_code.upper()
    
    #抓取证券名称
    headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }   
    # https://finance.yahoo.com/quote/SWMCX/
    url = f"https://finance.yahoo.com/quote/{stock_code1}/"
    response = requests.get(url,headers=headers)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        soup_title=soup.title
        soup_text=soup_title.text
        soup_text_list=soup_text.split('(')
        
        t_name = soup_text_list[0].strip()
    else:
        #未找到证券代码
        pass
        return stock_code
    
    #过滤名称中多余的尾部词汇
    t_name=filter_stock_name(t_name)
    
    
    return t_name   
#==============================================================================
if __name__=='__main__':
    original_name='Oponeo.pl SA'
    original_name='Apple Inc'
    original_name='Schwab  US Mid-Cap Index'
    
    original_name='Shanghai Gold (CNH) Futures,Apr'
    
    filter_stock_name(original_name)
    
def filter_stock_name(original_name):
    """
    功能：过滤从网站上抓取到的证券名称，去掉尾部的公司类别词汇，缩短长度，便于显示
    """
        
    #将字符串中的多个空格变为单个空格
    original_name=replace_multiple_spaces(original_name)
    
    #定义需要去掉的单词，注意顺序不要轻易颠倒！子串包含的，要长文在前！前置留空格的为避免误删
    remove_list=[' CORPORATION',' BERHAD',' BHD',' PLC',' INC',' AG ST',' NA O N', \
                 ' AKTIENGESELLSCHAFT','(PUBL)',' LLC', \
                 ' CO LTD',' CO LIMITED',' LTD',' LIMITED',' COMPANY',' INCORPORATED', \
                 ' CORP LTD',' CORP',' AB',' CO', \
                 ' GROUP CO','(GROUP)',' GROUP', \
                 ' PL S A',' PL SA',' AG', \
                 ' SCIENCE & TECHNOLOGY',' HIGH-TECH',' HIGH TECHNOLOGY', \
                     
                 ' APR',' MAY',' JUN',' JUL',' AUG',' SEP',' SEPT',' OCT',' NOV',' DEC',    
                 ' JAN',' FEB',' MAR',    
                     
                ]

    #去掉逗号和句点
    name1=original_name.replace(',',' ')
    name1=name1.replace('  ',' ')
    name2=name1.replace('.',' ')
    
    #将字符串字母全部大写
    name4=name2.upper()
    
    name5=name4
    for ss in remove_list:
        name5=name5.replace(ss,'')

    name6=name5.strip()
    
    name7=original_name[:len(name6)+1]
    name7=name7.replace(',','').replace('.','')
    
    shorter_name=name7
    return shorter_name
        

#==============================================================================
if __name__ == '__main__':
    stock_code='OPN.PL'
    stock_code='AAPL'
    stock_code='600519.SS'
    stock_code='6758.T'
    stock_code='6758.JP'
    stock_code='ULVR.L'
    stock_code='ULVR.UK'
    
    stock_code='1155.KL'
    stock_code='MSFT'
    
    stock_code='GC.F'
    stock_code='XAUUSD'
    
    stooq_name1(stock_code)

 
def stooq_name1(stock_code,add_suffix=True):
    
    import requests
    from bs4 import BeautifulSoup
    
    stock_code1=stock_code.lower()
    
    #美股：尾部增加.us
    stock_code_list=stock_code1.split('.')
    if len(stock_code_list)==1:
        stock_code1=stock_code1+'.us'
    
    #其他国家股票
    if len(stock_code_list)==2:
        code=stock_code_list[0]
        sid=stock_code_list[1]
        
        #中国股票：尾部变为.cn
        if sid in ['ss','sz','bj']:
            stock_code1=code+'.cn'
        
        #日本股票：尾部变为.jp
        if sid in ['t']:
            stock_code1=code+'.jp'        
        
        #英国股票：尾部变为.uk
        if sid in ['l']:
            stock_code1=code+'.uk'          
        
        #XX国股票
        
        #波兰股票：去掉尾部.PL
        stock_code1=stock_code1.replace('.pl','')
    
    #抓取证券名称
    headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }    
    url = f"https://stooq.com/q/?s={stock_code1}"
    response = requests.get(url,headers=headers)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        soup_title=soup.title
        soup_text=soup_title.text
        soup_text_list=soup_text.split(' - ')
        
        t_name = soup_text_list[1].strip()
    else:
        pass
        return stock_code
    
    #未找到证券代码
    if t_name == 'Stooq':
        
        #尝试不加后缀'.us'
        url = f"https://stooq.com/q/?s={stock_code}"
        response = requests.get(url,headers=headers)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            soup_title=soup.title
            soup_text=soup_title.text
            soup_text_list=soup_text.split(' - ')
            
            t_name = soup_text_list[1].strip()
        else:
            pass
            return stock_code
        
        if t_name == 'Stooq':
            return stock_code
    
    #过滤名称中多余的尾部词汇
    t_name=filter_stock_name(t_name)
    
    #增加交易所后缀
    if add_suffix:
        tlist=stock_code1.split('.')
        if len(tlist)==1: sid='PL'
        if len(tlist)==2:
            sid=tlist[1].upper()
            
        if sid not in ['CN','US']:
            t_name=t_name+'('+sid+')'
    
    t_name=t_name.strip()
    
    return t_name   
 
#==============================================================================
#==============================================================================
if __name__ == '__main__':
    stock_code='AAPL'
    stock_code='600519.SS'
    stock_code='6758.T'
    stock_code='6758.JP'
    stock_code='ULVR.L'
    stock_code='1155.KL'
    stock_code='MSFT'
    
    stock_code='GC=F'
    stock_code='XAUUSD'
    
    yahoo_name1(stock_code)

 
def yahoo_name1(stock_code):
    
    import requests
    from bs4 import BeautifulSoup
    
    stock_code1=stock_code.lower()
    
    #抓取证券名称
    headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }    
    url = f"https://finance.yahoo.com/quote/{stock_code1}"
    response = requests.get(url,headers=headers)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        soup_title=soup.title
        soup_text=soup_title.text
        
        stock_code2=stock_code1.upper()
        try:
            pos=soup_text.index(stock_code2)
        except:
            pass
            return stock_code
        t_name = soup_text[:pos-1].strip()
    else:
        pass
        return stock_code
    
    #过滤名称中多余的尾部词汇
    t_name=filter_stock_name(t_name).strip()
    t_name=filter_stock_name(t_name).strip()
    
    return t_name   
 
#==============================================================================




if __name__=='__main__':
    ticker='1155.KL'
    ticker='MSFT'
    ticker='G13.SI'
    ticker='S63.SI'
    ticker='SUS.ST'
    ticker='SUN.UK'
    ticker='IUI1.DE'
    
    ticker='600519.SS'
    ticker='U11.SI'
    ticker='1295.KL'
    ticker='BMW.DE'
    ticker='MBG.DE'
    ticker='005930.KS'
    ticker='LI'
    ticker='ULVR.L'
    ticker='KSL.AX'
    
    ticker='SGC=F'
    
    ticker='IBM'
    
    ticker='XAUUSD'
    short_name=False;add_suffix=True;maxlen=80
    
    get_stock_name1_en(ticker)

def get_stock_name1_en(ticker,short_name=False,add_suffix=True,maxlen=80):
    """
    功能：分别从stooq和yahoo网站获取证券名称，优先stooq(因为不需要vpn)
    """
    sname=ticker
    
    try:
        sname=stooq_name1(ticker,add_suffix=add_suffix)
    except:
        pass
    
    if sname==ticker:
        try:
            sname=yahoo_name1(ticker,short_name=short_name,add_suffix=add_suffix,maxlen=maxlen)
        except:
            pass
        
    return sname

#==============================================================================
#==============================================================================
if __name__ == '__main__':
    ticker='600519.SS'
    ticker='600305.SS'
    ticker='200725.SZ'
    ticker='000725.SZ'
    
    get_stock_name_china_sina(ticker)

def get_stock_name_china_sina(ticker):
    """
    功能：抓取股票的申万行业分类名称
    """
    
    import requests
    from bs4 import BeautifulSoup

    ticker6=ticker[:6]    
    headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }    
    url=f"https://vip.stock.finance.sina.com.cn/corp/go.php/vCI_CorpOtherInfo/stockid/{ticker6}/menu_num/2.phtml"
    response = requests.get(url,headers=headers)
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        soup_text=soup.find(id="stockName").text

        soup_text_list=soup_text.split('(')
        
        t_name = soup_text_list[0].strip()
                
        return t_name
    else:
        return ticker

#==============================================================================
#==============================================================================
#==============================================================================
#==============================================================================
#==============================================================================
#==============================================================================
#==============================================================================