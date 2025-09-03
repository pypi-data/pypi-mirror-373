# -*- coding: utf-8 -*-
"""
本模块功能：中国行业板块市场分析
所属工具包：证券投资分析工具SIAT 
SIAT：Security Investment Analysis Tool
创建日期：2020年10月20日
最新修订日期：2020年10月21日
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
from siat.translate import *
from siat.bond_base import *
from siat.stock import *
from siat.risk_adjusted_return import *
from siat.financials_china2 import *
#==============================================================================

if __name__=='__main__':
    indicator="新浪行业"
    indicator="启明星行业"
    indicator="地域"
    indicator="行业"

def sector_list_china(indicator="新浪行业"):
    """
    功能：行业分类列表
    indicator="新浪行业","启明星行业","概念","地域","行业"
    来源网址：http://finance.sina.com.cn/stock/sl/#qmxindustry_1
    """
    #检查选项是否支持
    indicatorlist=["新浪行业","概念","地域","行业","启明星行业"]
    if indicator not in indicatorlist:
        print("  #Error(sector_list_china): unsupported sectoring method",indicator)
        print("  Supported sectoring methods:",indicatorlist)
        return None
    
    import akshare as ak
    try:
        df = ak.stock_sector_spot(indicator=indicator)
        
        #去掉空格，否则匹配容易失败
        df['板块']=df['板块'].apply(lambda x: x.strip())   
        df['label']=df['label'].apply(lambda x: x.strip())
        
    except:
        print("  #Error(sector_list_china): data source unavailable for",indicator)
        print("  Possible reason 1: data source is self-updating now.")
        print("  Possible reason 2: need to upgrade akshare.")
        print("  Possible reason 3: data source not reachable under vpn.")

        return None
    
    sectorlist=list(df['板块'])
    #按照拼音排序
    sectorlist=list(set(list(sectorlist)))
    sectorlist=sort_pinyin(sectorlist)
    #解决拼音相同带来的bug：陕西省 vs 山西省
    if '陕西省' in sectorlist:
        pos=sectorlist.index('陕西省')
        if sectorlist[pos+1] == '陕西省':
            sectorlist[pos] = '山西省'
    if '山西省' in sectorlist:
        pos=sectorlist.index('山西省')
        if sectorlist[pos+1] == '山西省':
            sectorlist[pos+1] = '陕西省'
    listnum=len(sectorlist)
    
    if indicator != "行业":
        method=indicator
    else:
        method="证监会门类/大类"
    print("\n===== 中国股票市场的行业/板块:",listnum,"\b个（按"+method+"划分） =====\n")

    if indicator in ["新浪行业","启明星行业","概念"]:
        #板块名字长度
        maxlen=0
        for s in sectorlist:        
            l=strlen(s)
            if l > maxlen: maxlen=l
        #每行打印板块名字个数
        rownum=int(80/(maxlen+2))
        
        for d in sectorlist:
            if strlen(d) < maxlen:
                dd=d+" "*(maxlen-strlen(d))
            else:
                dd=d
            print(dd,end='  ')
            pos=sectorlist.index(d)+1
            if (pos % rownum ==0) or (pos==listnum): print(' ')    

    #if indicator in ["地域","行业"]:
    if indicator in ["地域"]:    
        linemaxlen=60
        linelen=0
        for d in sectorlist:
            dlen=strlen(d)
            pos=sectorlist.index(d)+1
            #超过行长
            if (linelen+dlen) > linemaxlen:
                print(' '); linelen=0
            #是否最后一项
            if pos < listnum:
                print(d,end=', ')
            else:
                print(d+"。"); break
            linelen=linelen+dlen

    #证监会行业划分
    if indicator in ["行业"]:   
        df['csrc_type']=df['label'].apply(lambda x: x[8:9])
        csrc_type_list=list(set(list(df['csrc_type'])))
        csrc_type_list.sort()
        
        for t in csrc_type_list:
            dft=df[df['csrc_type']==t]
            sectorlist=list(dft['板块'])
            listnum=len(sectorlist)
            
            linemaxlen=80
            linelen=0
            print(t,end=': ')
            for d in sectorlist:
                dlen=strlen(d)
                pos=sectorlist.index(d)+1
                #超过行长
                if (linelen+dlen) > linemaxlen:
                    print(' '); linelen=0
                #是否最后一项
                if pos < listnum:
                    print(d,end=', ')
                else:
                    #print(d+"。"); break
                    print(d+" "); break
                linelen=linelen+dlen
            
            
    import datetime
    today = datetime.date.today()
    print("\n*** 信息来源：新浪财经,",today) 
    
    return df


#==============================================================================
if __name__=='__main__':
    sector_name="房地产"
    sector_name="房"
    sector_name="煤炭"
    sector_name="华为"
    
    indicator='新浪行业'
    indicator="启明星行业"
    indicator="地域"
    indicator="行业"
    
    sector_code_china(sector_name)

def sector_code_sina(sector_name):
    """
    功能：套壳sector_code_china
    """
    sector_code_china(sector_name)
    return

def sector_code_china(sector_name):
    """
    功能：查找行业、板块名称对应的板块代码
    """
    import akshare as ak
    print("\n===== 查询行业/板块代码 =====")
    
    indicatorlist=["新浪行业","概念","地域","启明星行业","行业"]
    sector_code=''; found=0
    for i in indicatorlist:
        dfi=ak.stock_sector_spot(indicator=i)
        
        #去掉空格，否则匹配容易失败
        dfi['板块']=dfi['板块'].apply(lambda x: x.strip())  
        dfi['label']=dfi['label'].apply(lambda x: x.strip())
        
        try:
            #sector_code=list(dfi[dfi['板块']==sector_name]['label'])[0]
            dfi['match']=dfi['板块'].apply(lambda x: 1 if sector_name in x else 0)
            found=found+dfi['match'].sum()
            
            sector_code=list(dfi[dfi['match']==1]['label'])
            sector_name1=list(dfi[dfi['match']==1]['板块'])
            
            #记录找到的板块分类
            indicator=i
            
            #if found > 0: print(" ")
            if indicator == "行业": indicator = "证监会行业"
            if indicator == "概念": indicator = "新浪概念"
            
            if len(sector_code)>0:
                """
                print("行业/板块名称:",sector_name1)
                #print_list(sector_name1,leading_blanks=1)
                
                print("行业/板块代码:",sector_code,end='')
                #print_list(sector_code,leading_blanks=1)
                
                print("（"+indicator+"分类）\n")
                """
                print("行业/板块名称:",end='')
                print_list(sector_name1,leading_blanks=1)
                
                print("行业/板块代码:",end='')
                print_list(sector_code,leading_blanks=1,end='')
                print("（"+indicator+"分类）\n")
                
                
        except:
            # 无意义，仅为调试
            pass
            continue
    
    #未找到板块代码
    if found==0:
        print("*** Sorry, no sector name found for",sector_name)
        return 
    
    return 

if __name__=='__main__':
    sector_name="房地产"
    df=sector_code_china(sector_name)
    df=sector_code_china("医药生物")
    df=sector_code_china("资本市场服务")
    
#==============================================================================
if __name__=='__main__':
    comp="xxx"
    comp="涨跌幅"
    comp="成交量"
    comp="平均价格"
    comp="公司家数"
    
    indicator="+++"
    indicator="新浪行业"
    indicator="启明星行业"
    indicator="地域"
    indicator="行业"
    num=10

def sector_rank_sina(indicator="涨跌幅",category="新浪行业",rank=5):
    """
    功能：套壳sector_rank_china
    """
    df=sector_rank_china(comp=indicator,indicator=category,num=rank)
    return df

#def sector_rank_china(comp="涨跌幅",indicator="新浪行业",num=10):
def sector_rank_china(ticker="新浪行业",indicator="涨跌幅",rank=10):    
    """
    功能：按照比较指标降序排列
    ticker="新浪行业","启明星行业","概念","地域","行业"
    indicator="涨跌幅",平均价格，公司家数
    rank：为正数时列出最高的前几名，为负数时列出最后几名
    
    注意：公司家数字段最大值为100，超过100仅显示为100
    """
    comp=indicator
    indicator=ticker
    num=rank
    
    #检查选项是否支持
    #complist=["涨跌幅","成交量","平均价格","公司家数"]
    complist=["涨跌幅","平均价格","公司家数"]
    if comp not in complist:
        print("  #Warning(sector_rank_china): unsupported measurement",comp)
        print("  Supported measurements:",complist)
        return None
    
    indicatorlist=["新浪行业","概念","地域","启明星行业","行业"]
    if indicator not in indicatorlist:
        print("  #Warning(sector_list_china): unsupported sectoring method",indicator)
        print("  Supported sectoring method:",indicatorlist)
        return None
    
    import akshare as ak
    try:
        df = ak.stock_sector_spot(indicator=indicator)  
        
        #去掉空格，否则匹配容易失败
        df['板块']=df['板块'].apply(lambda x: x.strip())   
        df['label']=df['label'].apply(lambda x: x.strip())
        
    except:
        print("  #Warning(sector_rank_china): data source tentatively unavailable for",indicator)
        print("  Possible reason: data source is self-updating.")
        print("  Solution: have a breath of fresh air and try later.")
        return None
    
    df.dropna(inplace=True)
    #出现列名重名，强制修改列名
    df.columns=['label','板块','公司家数','平均价格','涨跌额','涨跌幅', \
                '总成交量(手)','总成交额(万元)','个股代码','个股涨跌幅','个股股价', \
                '个股涨跌额','个股名称']
    df['均价']=round(df['平均价格'].astype('float'),2)
    df['涨跌幅%']=round(df['涨跌幅'].astype('float'),2)
    #平均成交量:万手
    df['平均成交量']=(df['总成交量(手)'].astype('float')/df['公司家数'].astype('float')/10000)
    df['平均成交量']=round(df['平均成交量'],2)
    #平均成交额：亿元
    df['平均成交额']=(df['总成交额(万元)'].astype('float')/df['公司家数'].astype('float'))/10000
    df['平均成交额']=round(df['平均成交额'],2)
    stkcd=lambda x: x[2:]
    df['个股代码']=df['个股代码'].apply(stkcd)
    try:
        df['个股涨跌幅%']=round(df['个股涨跌幅'].astype('float'),2)
    except:
        pass
    try:
        df['个股股价']=round(df['个股股价'].astype('float'),2)
    except:
        pass
    try:
        df['公司家数']=df['公司家数'].astype('int')
    except:
        pass
    df2=df[['板块','涨跌幅%','平均成交量','平均成交额','均价', \
            '公司家数','label','个股名称','个股代码','个股涨跌幅','个股股价']].copy()
    df2=df2.rename(columns={'个股名称':'代表个股','label':'板块代码'})
    
    #删除无效的记录
    df2=df2.drop(df2[df2['均价'] == 0.0].index)
    
    if comp == "涨跌幅":
        df3=df2[['板块','涨跌幅%','均价','公司家数','板块代码','代表个股']]
        df3.sort_values(by=['涨跌幅%'],ascending=False,inplace=True)
    """
    if comp == "成交量":
        df3=df2[['板块','平均成交量','涨跌幅%','均价','公司家数','板块代码','代表个股']]
        df3.sort_values(by=['平均成交量'],ascending=False,inplace=True)
    """
    if comp == "平均价格":
        df3=df2[['板块','均价','涨跌幅%','公司家数','板块代码','代表个股']]
        df3.sort_values(by=['均价'],ascending=False,inplace=True)
    if comp == "公司家数":
        df3=df2[['板块','公司家数','均价','涨跌幅%','板块代码','代表个股']]
        df3.sort_values(by=['公司家数'],ascending=False,inplace=True)
    df3.reset_index(drop=True,inplace=True)
        
    #设置打印对齐
    import pandas as pd
    pd.set_option('display.max_columns', 1000)
    pd.set_option('display.width', 1000)
    pd.set_option('display.max_colwidth', 1000)
    pd.set_option('display.unicode.ambiguous_as_wide', True)
    pd.set_option('display.unicode.east_asian_width', True)
    
    if indicator == "行业":
        indtag="证监会行业"
    else:
        indtag=indicator
    
    #处理空记录
    if len(df3) == 0:
        print("  #Warning(sector_rank_china):data source tentatively unavailable for",comp,indicator)
        print("  Possible reason: data source is self-updating.")
        print("  Solution: have a breath of fresh air and try later.")
        return
    
    df3.index=df3.index + 1
    
    df3_collist=list(df3)
    df3['序号']=df3.index
    df3=df3[['序号']+df3_collist]
    
    """
    print("\n===== 中国股票市场：板块"+comp+"排行榜（按照"+indtag+"分类） =====")
    if num > 0:
        print(df3.head(num))
    else:
        print(df3.tail(-num))
    
    import datetime
    today = datetime.date.today()
    footnote1="*注：代表个股是指板块中涨幅最高或跌幅最低的股票"
    print(footnote1)
    print(" 板块数:",len(df),"\b, 数据来源：新浪财经,",today,"\b（信息为上个交易日）") 
    """
    if num > 0:
        df4=df3.head(num)
    else:
        df4=df3.tail(-num)
    
    titletxt="中国股票市场：板块"+comp+"排行榜（按照"+indtag+"分类）"
    import datetime; stoday = datetime.date.today()
    footnote1="注：代表个股是指板块中涨幅最高或跌幅最低的股票\n"
    #footnote2="板块总数"+str(len(df))+"，数据来源：新浪财经，"+str(stoday)+"(截至昨日)"
    footnote2="板块总数"+str(len(df))+"，数据来源：新浪财经，"+str(stoday)
    footnote=footnote1+footnote2
    
    df_display_CSS(df4,titletxt=titletxt,footnote=footnote,facecolor='papayawhip',decimals=2, \
                   first_col_align='center',second_col_align='left', \
                       last_col_align='left',other_col_align='right', \
                       titile_font_size='16px',heading_font_size='15px', \
                       data_font_size='15px')

    return df3

#==============================================================================
if __name__=='__main__':
    sector="new_dlhy"
    sector="xyz"
        
    num=10

def sector_detail_sina(sector="new_dlhy",indicator="涨跌幅",rank=5):
    """
    功能：套壳sector_detail_china
    """
    df=sector_detail_china(sector=sector,comp=indicator,num=rank)
    return df
    

#def sector_detail_china(sector="new_dlhy",comp="涨跌幅",num=10):
def sector_detail_china(ticker="new_dlhy",indicator="涨跌幅",rank=10):
    """
    功能：按照板块内部股票的比较指标降序排列
    ticker：板块代码
    indicator：默认"涨跌幅"，还可选"换手率"、"收盘价"、"市盈率"、"市净率"、"总市值"、"流通市值"
    rank：为正数时列出最高的前几名，为负数时列出最后几名
    """
    sector=ticker
    comp=indicator
    num=rank
    
    debug=False

    #检查选项是否支持
    complist=["涨跌幅","换手率","收盘价","市盈率","市净率","总市值","流通市值"]
    if comp not in complist:
        print("  #Error(sector_detail_china): unsupported measurement",comp)
        print("  Supported measurements:",complist)
        return None
    
    #检查板块代码是否存在
    import akshare as ak
    indicatorlist=["新浪行业","概念","地域","启明星行业","行业"]
    sector_name=''
    for i in indicatorlist:
        dfi=ak.stock_sector_spot(indicator=i)
        
        #去掉字符串中的空格，否则匹配容易失败
        dfi['板块']=dfi['板块'].apply(lambda x: x.strip()) 
        dfi['label']=dfi['label'].apply(lambda x: x.strip())
        
        if debug: print("i=",i)
        try:
            sector_name=list(dfi[dfi['label']==sector]['板块'])[0]
            #记录找到的板块分类
            indicator=i
            #记录找到的板块概述
            dff=dfi[dfi['label']==sector]
            break
        except:
            continue
    #未找到板块代码
    if sector_name == '':
        print("  #Error(sector_detail_china): unsupported sector code",sector)
        return
    
    #板块成份股
    try:
        df = ak.stock_sector_detail(sector=sector)
    except:
        print("  #Error(sector_rank_china): data source tentatively unavailable for",sector)
        print("  Possible reason: data source is self-updating.")
        print("  Solution: have a breath of fresh air and try later.")
        return None
    
    df.dropna(inplace=True)
    df['个股代码']=df['code']
    df['个股名称']=df['name']
    df['涨跌幅%']=round(df['changepercent'].astype('float'),2)
    df['收盘价']=round(df['settlement'].astype('float'),2)
    #成交量:万手
    df['成交量']=round(df['volume'].astype('float')/10000,2)
    #成交额：亿元
    df['成交额']=round(df['amount'].astype('float')/10000,2)
    df['市盈率']=round(df['per'].astype('float'),2)
    df['市净率']=round(df['pb'].astype('float'),2)
    #总市值：亿元
    df['总市值']=round(df['mktcap'].astype('float')/10000,2)
    #流通市值：亿元
    df['流通市值']=round(df['nmc'].astype('float')/10000,2)
    df['换手率%']=round(df['turnoverratio'].astype('float'),2)
    
    #删除无效的记录
    df=df.drop(df[df['收盘价'] == 0].index)
    df=df.drop(df[df['流通市值'] == 0].index)
    df=df.drop(df[df['总市值'] == 0].index)
    df=df.drop(df[df['市盈率'] == 0].index)
    
    df2=df[[ '个股代码','个股名称','涨跌幅%','收盘价','成交量','成交额', \
            '市盈率','市净率','换手率%','总市值','流通市值']].copy()
    
    if comp == "涨跌幅":
        df3=df2[['个股名称','个股代码','涨跌幅%','换手率%','收盘价','市盈率','市净率','流通市值']]
        df3.sort_values(by=['涨跌幅%'],ascending=False,inplace=True)
    if comp == "换手率":
        df3=df2[['个股名称','个股代码','换手率%','涨跌幅%','收盘价','市盈率','市净率','流通市值']]
        df3.sort_values(by=['换手率%'],ascending=False,inplace=True)
    if comp == "收盘价":
        df3=df2[['个股名称','个股代码','收盘价','换手率%','涨跌幅%','市盈率','市净率','流通市值']]
        df3.sort_values(by=['收盘价'],ascending=False,inplace=True)
    if comp == "市盈率":
        df3=df2[['个股名称','个股代码','市盈率','市净率','收盘价','换手率%','涨跌幅%','流通市值']]
        df3.sort_values(by=['市盈率'],ascending=False,inplace=True)
    if comp == "市净率":
        df3=df2[['个股名称','个股代码','市净率','市盈率','收盘价','换手率%','涨跌幅%','流通市值']]
        df3.sort_values(by=['市净率'],ascending=False,inplace=True)
    if comp == "流通市值":
        df3=df2[['个股名称','个股代码','流通市值','总市值','市净率','市盈率','收盘价','换手率%','涨跌幅%']]
        df3.sort_values(by=['流通市值'],ascending=False,inplace=True)
    if comp == "总市值":
        df3=df2[['个股名称','个股代码','总市值','流通市值','市净率','市盈率','收盘价','换手率%','涨跌幅%']]
        df3.sort_values(by=['总市值'],ascending=False,inplace=True)  
        
    df3.reset_index(drop=True,inplace=True)
        
    #设置打印对齐
    import pandas as pd
    pd.set_option('display.max_columns', 1000)
    pd.set_option('display.width', 1000)
    pd.set_option('display.max_colwidth', 1000)
    pd.set_option('display.unicode.ambiguous_as_wide', True)
    pd.set_option('display.unicode.east_asian_width', True)
    
    df3.index=df3.index + 1

    df3_collist=list(df3)
    df3['序号']=df3.index
    df3=df3[['序号']+df3_collist]    
    """
    print("\n=== 中国股票市场："+sector_name+"板块，成份股排行榜（按照"+comp+"） ===\n")
    if num > 0:
        print(df3.head(num))
    else:
        print(df3.tail(-num))
    
    import datetime
    today = datetime.date.today()
    footnote1="\n 注：市值的单位是亿元人民币, "
    print(footnote1+"板块内成份股个数:",len(df))
    print(" 数据来源：新浪财经,",today,"\b（信息为上个交易日）") 
    """
    if num > 0:
        df4=df3.head(num)
    else:
        df4=df3.tail(-num)
    
    titletxt="中国股票市场："+sector_name+"板块，成份股排行榜（基于"+comp+"）"
    
    import datetime; stoday = datetime.date.today()
    if "流通市值" in df3_collist:
        footnote1="市值单位：亿元，板块成份股："+str(len(df))+'\n'
        #footnote2="数据来源：新浪财经，"+str(stoday)+"(截至昨日)"
        footnote2="数据来源：新浪财经，"+str(stoday)
    else:
        footnote1="板块成份股："+str(len(df))+'，'
        #footnote2="数据来源：新浪财经，"+str(stoday)+"(截至昨日)"
        footnote2="数据来源：新浪财经，"+str(stoday)
    footnote=footnote1+footnote2
    
    df_display_CSS(df4,titletxt=titletxt,footnote=footnote,facecolor='papayawhip',decimals=2, \
                   first_col_align='center',second_col_align='left', \
                       last_col_align='right',other_col_align='right', \
                       titile_font_size='16px',heading_font_size='15px', \
                       data_font_size='15px')    
    
    #return df2
    return df4

#==============================================================================
if __name__=='__main__':
    ticker='600021.SS'
    ticker='000661.SZ'
    ticker='999999.SS'
    sector="new_dlhy"
    sector="yysw"
    sector="xyz"
    
    ticker='000661.SZ'; sector="gn_swym"

def sector_position_sina(ticker,sector="new_dlhy",return_result=False):
    """
    功能：套壳sector_position_china
    """
    df=sector_position_china(ticker=ticker,sector=sector)
    
    if return_result:
        return df
    else:
        return

def sector_position_china(ticker,sector="new_dlhy"):
    """
    功能：查找一只股票在板块内的分位数位置
    ticker：股票代码
    sector：板块代码
    """
    ticker1=ticker[:6]
    
    import akshare as ak
    import numpy as np
    import pandas as pd    
    
    #检查板块代码是否存在
    indicatorlist=["新浪行业","概念","地域","启明星行业","行业"]
    sector_name=''
    for i in indicatorlist:
        dfi=ak.stock_sector_spot(indicator=i)
        
        #去掉空格，否则匹配容易失败
        dfi['板块']=dfi['板块'].apply(lambda x: x.strip())   
        dfi['label']=dfi['label'].apply(lambda x: x.strip())
        
        try:
            sector_name=list(dfi[dfi['label']==sector]['板块'])[0]
            #记录找到的板块分类
            indicator=i
            #记录找到的板块概述
            dff=dfi[dfi['label']==sector]
            break
        except:
            continue
        
    #未找到板块代码
    if sector_name == '':
        print("  #Warning(sector_position_china): unsupported sector code",sector)
        return None
    
    #板块成份股
    try:
        #注意：启明星行业分类没有成份股明细
        df = ak.stock_sector_detail(sector=sector)
    except:
        print("  #Warning(sector_position_china): sector detail not available for",sector,'by',indicator)
        if indicator !="启明星行业":
            print("  Possible reason: data source is self-updating.")
            print("  Solution: have a breath of fresh air and try later.")
        return None

    #清洗原始数据: #可能同时含有数值和字符串，强制转换成数值
    df['changepercent']=round(df['changepercent'].astype('float'),2)
    df['turnoverratio']=round(df['turnoverratio'].astype('float'),2)
    df['settlement']=round(df['settlement'].astype('float'),2)
    df['per']=round(df['per'].astype('float'),2)
    df['pb']=round(df['pb'].astype('float'),2)
    df['nmc']=round(df['nmc'].astype('int')/10000,2)
    df['mktcap']=round(df['mktcap'].astype('int')/10000,2)
    
    #检查股票代码是否存在
    sdf=df[df['code']==ticker1]
    if len(sdf) == 0:
        print("  #Warning(sector_position_china): retrieving",ticker,"failed in sector",sector,sector_name)
        print("  Solution: make sure stock code correct, try later if network is slow")
        return None       
    sname=list(sdf['name'])[0]
    
    #确定比较范围
    complist=['changepercent','turnoverratio','settlement','per','pb','nmc','mktcap']
    vminlist=['settlement','per','pb','nmc','mktcap'] #板块最小值若为零需要标记的列
    compnames=['涨跌幅%','换手率%','收盘价(元)','市盈率','市净率','流通市值(亿元)','总市值(亿元)']
    compdf=pd.DataFrame(columns=['指标名称','指标数值','板块排名','板块分位数%','板块中位数','板块最小值','板块最大值'])
    
    from scipy.stats import percentileofscore
    
    for c in complist:
        v=list(sdf[c])[0]
        #vlist=list(set(list(df[c])))
        vlist=list(df[c])
        vlist.sort() #升序
        vmin=round(min(vlist),2)
        if vmin==0.00 and c in vminlist:
            vmin='--'
        
        vmax=round(max(vlist),2)
        vmedian=round(np.median(vlist),2)
        
        pos=vlist.index(v)
        #pct=round((pos+1)/len(vlist)*100,2)
        #sector_rank=str(len(vlist)-pos)+'/'+str(len(vlist))
        sector_rank=str(len(vlist)-pos)
        
        pct=percentileofscore(vlist,v)
        
        s=pd.Series({'指标名称':compnames[complist.index(c)], \
                     '指标数值':v,'板块排名':sector_rank,'板块分位数%':pct,'板块中位数':vmedian, \
                    '板块最小值':vmin,'板块最大值':vmax})
        try:
            compdf=compdf.append(s,ignore_index=True)
        except:
            compdf=compdf._append(s,ignore_index=True)
        
    compdf.reset_index(drop=True,inplace=True)     
    """
    print("\n======= 股票在所属行业/板块的位置分析 =======")
    print("股票: "+sname+" ("+ticker+")")
    print("所属行业/板块："+sector_name+" ("+sector+", "+indicator+"分类)")
    print("")
    
    pd.set_option('display.max_columns', 1000)
    pd.set_option('display.width', 1000)
    pd.set_option('display.max_colwidth', 1000)
    pd.set_option('display.unicode.ambiguous_as_wide', True)
    pd.set_option('display.unicode.east_asian_width', True)
    
    print(compdf.to_string(index=False))
    
    import datetime
    today = datetime.date.today()
    print('') #空一行
    print("注：板块内成份股个数:",len(df),"\b, 数据来源：新浪财经,",today,"\b(信息为上个交易日)")
    """
    if indicator=="行业": indicator="证监会行业"
    
    titletxt="\n上市公司地位分析："+sname+"，"+sector_name+"行业/板块（"+indicator+"分类）"
    import datetime; stoday = datetime.date.today()
    footnote1=""
    #footnote2="成分股总数："+str(len(df))+"，数据来源：新浪财经，"+str(stoday)+"(截至昨日)"
    footnote2="成分股总数："+str(len(df))+"，数据来源：新浪财经，"+str(stoday)
    footnote=footnote1+footnote2
    
    #print("") #空一行
    df_display_CSS(compdf,titletxt=titletxt,footnote=footnote,facecolor='papayawhip',decimals=2, \
                   first_col_align='left',second_col_align='right', \
                       last_col_align='right',other_col_align='right', \
                       titile_font_size='16px',heading_font_size='15px', \
                       data_font_size='15px')    
    
    
    return df,compdf    
    

#==============================================================================

def invest_concept_china(num=10,max_sleep=30):
    """
    废弃！
    功能：汇总新浪投资概念股票名单，排行
    来源网址：http://finance.sina.com.cn/stock/sl/#qmxindustry_1
    
    注意：网站有反爬虫，循环做不下去！
    """
    print("\nWarning: This function might cause your IP address banned by data source!")
    print("Searching stocks with investment concepts in China, it may take long time ...")
    
    #找出投资概念列表
    import akshare as ak
    cdf = ak.stock_sector_spot(indicator="概念")
    
    #去掉空格，否则匹配容易失败
    cdf['板块']=cdf['板块'].apply(lambda x: x.strip())
    cdf['label']=cdf['label'].apply(lambda x: x.strip())    
    
    cdf.sort_values(by=['label'],ascending=True,inplace=True)
    clist=list(cdf['label'])
    cnames=list(cdf['板块'])
    cnum=len(clist)
    
    import pandas as pd
    totaldf=pd.DataFrame()
    import time; import random
    i=0
    #新浪财经有反爬虫，这个循环做不下去
    for c in clist:
        print("...Searching for conceptual sector",c,cnames[clist.index(c)],end='')
        try:
            sdf = ak.stock_sector_detail(c)
            sdf['板块']=cnames(clist.index(c))
            totaldf=pd.concat([totaldf,sdf],ignore_index=True)
            print(', found.')
        except:
            print(', failed:-(')
            #continue
                    #等待一会儿，避免被禁访问
        #time.sleep(max_sleep)
        random_int=random.randint(1,max_sleep)
        time.sleep(random_int)

        i=i+1
        if i % 20 == 0:
            print(int(i/cnum*100),'\b%',end=' ')
    print("...Searching completed.")
    
    if len(totaldf) == 0:
        print("  #Error(sector_concept_china): data source tentatively banned your access:-(")
        print("  Solutions:1) try a bit later, or 2) switch to another IP address.")
        return None
    
    #分组统计
    totaldfrank = totaldf.groupby('name')['板块','code'].count()
    totaldfrank.sort_values(by=['板块','code'],ascending=[False,True],inplace=True)
    totaldfrank['name']=totaldfrank.index
    totaldfrank.reset_index(drop=True,inplace=True)

    #更新每只股票持有的概念列表
    for i in totaldfrank.index:
        tdfsub=totaldf[totaldf['name']==totaldfrank.loc[i,"name"]]
        sectors=str(list(tdfsub['板块'])) 
        # 逐行修改列值
        totaldfrank.loc[i,"sectors"] = sectors

    #合成
    totaldf2=totaldf.drop('板块',axix=1)
    totaldf2.drop_duplicates(subset=['code'],keep='first',inplace=True)
    finaldf = pd.merge(totaldfrank,totaldf2,how='inner',on='name')
    
    return finaldf
    
    
#==============================================================================
def industry_sw_list_all():
    """
    功能：输出申万指数所有代码df。动态，每次重新获取，自动更新！
    输入：
    输出：df，包括市场表征指数F，一级行业指数I，二级行业T，风格指数S，三级行业3
    """
    import pandas as pd
    import akshare as ak
    
    symboltypes=["市场表征", "一级行业", "二级行业", "风格指数","大类风格指数","金创指数"] 
    indextypecodes=['F','1','2','S','B','C']
    industry=pd.DataFrame()
    for s in symboltypes:
        try:
            #目前有问题！
            dft = ak.index_realtime_sw(symbol=s)
        except: continue
        
        pos=symboltypes.index(s)
        dft['指数类别代码']=indextypecodes[pos]
        dft['指数类别名称']=s
        
        if len(industry)==0:
            industry=dft
        else:
            industry=pd.concat([industry,dft],ignore_index=True)
    
    industry2=industry[['指数类别代码','指数代码','指数名称']]    
    industry2.columns=['type','code','name']   
    
    #获取申万一级行业指数代码和名称
    #df1=ak.sw_index_first_info()
    
    #获取申万二级行业指数代码和名称
    #df2 = ak.sw_index_second_info()
    
    #获取申万三级行业指数代码和名称
    df3 = ak.sw_index_third_info()
    df3['type']='3'
    df3['code']=df3['行业代码'].apply(lambda x:x[:6])
    df3['name']=df3['行业名称']
    industry3=df3[['type','code','name']]
    
    industry_all=pd.concat([industry2,industry3],ignore_index=True)
    # 删除完全重复的行
    industry_all.drop_duplicates(inplace=True)

    
    return industry_all

if __name__=='__main__':
    idf=industry_sw_list()
    idf=industry_sw_list_all()

#==============================================================================
if __name__=='__main__':
    idf=industry_sw_list_all()
    
    industry_sw_list_print(idf,numberPerLine=3)
    
def industry_sw_list_print(idf,numberPerLine=3):
    """
    功能：打印df定义形式，每3个一行，需要定期更新，并复制到函数industry_sw_list()
    """

    #遍历
    counter=0
    for index,row in idf.iterrows():
        #print(row['type'],row['code'],row['name'])
        print('[\''+row['type']+'\',\''+row['code']+'\',\''+row['name']+'\']',end=',')
        counter=counter+1
        if counter % numberPerLine ==0:
            print()

    return

#==============================================================================

def display_industry_sw(sw_level='1',numberPerLine=4,colalign='left'):
    """
    按照类别打印申万行业列表，名称(代码)，每行5个, 套壳函数
    """
    #itype_list=['1','2','3','F','S','B','C']
    itype_list=['1','2','3','F','S','B']
    #sw_level_list=['1','2','3','F','S','B','C']
    sw_level_list=['1','2','3','F','S','B']
    
    try:
        pos=sw_level_list.index(sw_level)
    except:
        print(f"  #Warning(display_industry_sw): no such level in Shenwan system {sw_level}")
        print(f"  Supported Shenwan system: {sw_level_list}")
        
    itype=itype_list[pos]

    print_industry_sw(itype=itype,numberPerLine=numberPerLine,colalign=colalign) 
    
    return



if __name__=='__main__':
    itype='1'
    numberPerLine=5
    colalign='left'
    
    print_industry_sw(itype='1',numberPerLine=5,colalign='right')

def print_industry_sw(itype='1',numberPerLine=5,colalign='left'):
    """
    功能：按照类别打印申万行业列表，名称(代码)
    参数：
    itype：行业分级，默认'1'。
        F=市场表征, 1=一级行业, 2=二级行业, 3=三级行业, S="风格指数"，B=大类风格，C=金创
    numberPerLine：每行个数，默认5
    colalign：对齐方式，默认'left'
    
    示例：
    print_industry_sw(colalign='left')
    """
    df=industry_sw_list()
    df1=df[df['type']==itype]
    df1['name_code']=df1.apply(lambda x: x['name']+'('+x['code']+'.SW'+')',axis=1)
    
    symboltypes=["市场表征", "一级行业", "二级行业", "三级行业", "风格指数", "大类风格指数","金创指数"] 
    indextypecodes=['F','1','2','3','S','B','C']
    pos=indextypecodes.index(itype)
    iname=symboltypes[pos]
    
    ilist=list(df1['name_code'])
    print("\n*** 申万行业分类："+iname+"，共计"+str(len(ilist))+'个行业(板块)')
    
    if itype=='2': numberPerLine=4
    if itype=='3': numberPerLine=3
    
    printInLine_md(ilist,numberPerLine=numberPerLine,colalign=colalign)
    
    return

#==============================================================================
def display_industry_component_sw(industry,numberPerLine=5,colalign='left'):
    """
    打印申万行业的成分股，名称(代码), 包装函数
    industry: 申万行业名称或代码
    """
    industry1=industry.split('.')[0]
    if industry1.isdigit():
        print_industry_component_sw2(industry1,numberPerLine=numberPerLine,colalign=colalign)
    else:
        print_industry_component_sw(industry1,numberPerLine=numberPerLine,colalign=colalign)

    return


if __name__=='__main__':
    iname='食品饮料'
    iname='银行'
    iname='汽车'
    iname='高价股指数'
    iname='申万Ａ指'
    iname='大类风格-医药医疗'
    
    numberPerLine=5
    colalign='right'
    
    print_industry_component_sw(iname,numberPerLine=5,colalign='right')

def print_industry_component_sw(iname,numberPerLine=5,colalign='left', \
                                printout=True,return_result=False):
    """
    ===========================================================================
    功能：打印申万行业的成分股，名称(代码)
    iname：申万行业名称
    numberPerLine：输出时每行显示个数，默认5
    colalign：对齐方式，默认'left'
    printout：是否显示，默认True
    return_result：是否返回结果，默认False
    
    示例：
    print_industry_component_sw(iname="白酒Ⅲ")
    """
    try:
        icode=industry_sw_code(iname)
    except:
        print("  #Warning(print_industry_component_sw): failed to find index name for",iname)
        if return_result:
            return []
        else:
            return
    
    if icode=='':
        print("  #Warning(print_industry_component_sw): relevent index code not found for",iname)
        if return_result:
            return []
        else:
            return
    
    clist,cdf=industry_stock_sw(icode,top=1000)  
    if clist is None:
        if return_result:
            print("  #Warning(print_industry_component_sw): no component stock found for",iname)
            return []
        else:
            return
    
    #cdf['icode']=cdf['证券代码'].apply(lambda x: x+'.SS' if x[:1] in ['6'] else (x+'.SZ' if x[:1] in ['0','3'] else x+'.BJ' ))
    cdf['icode']=cdf['证券代码']
    
    # 删除'证券名称'为None的行
    cdf=cdf.mask(cdf.eq('None')).dropna()
    
    # 合成证券名称与代码
    cdf['name_code']=cdf.apply(lambda x: x['证券名称']+'('+x['icode']+')',axis=1)
    ilist=list(cdf['name_code'])

    if printout:    
        #标题
        import datetime as dt; stoday=dt.date.today()    
    
        titletxt=iname+"("+icode+")行业/板块成分股：计"+str(len(ilist))+'只，按行业指数权重降序排列，'+str(stoday)
        print("\n"+titletxt,end='')
        #表格
        printInLine_md(ilist,numberPerLine=numberPerLine,colalign=colalign)
    
    if return_result:
        return ilist
    else:
        return

#==============================================================================
if __name__=='__main__':
    icode='850831.SW'
    numberPerLine=5
    colalign='right'
    
    print_industry_component_sw2(icode,numberPerLine=5,colalign='right')

def print_industry_component_sw2(icode,numberPerLine=5,colalign='left'):
    """
    打印申万行业的成分股，名称(代码)
    输入：申万行业代码，一二三级均可
    """
    icode=icode.split('.')[0]
    
    iname=industry_sw_name(icode)
    
    clist,cdf=industry_stock_sw(icode,top=1000)   
    if cdf is None:
        print("  #Error(print_industry_component_sw2): failed to retrieve industry for",icode)
        print("  Solution: make sure the industry code correct")
        print("  If the code is correct, upgrade akshare, restart jupyter and try again")

        return

    #cdf['icode']=cdf['证券代码'].apply(lambda x: x+'.SS' if x[:1] in ['6'] else (x+'.SZ' if x[:1] in ['0','3'] else x+'.BJ' ))
    cdf['icode']=cdf['证券代码']
    
    # 删除'证券名称'为None的行
    cdf=cdf.mask(cdf.eq('None')).dropna()
    cdf['name_code']=cdf.apply(lambda x: x['证券名称']+'('+x['icode']+')',axis=1)
    
    ilist=list(cdf['name_code'])
    import datetime as dt; stoday=dt.date.today()    
    print("\n*** "+iname+'行业(板块)包括的股票：共计'+str(len(ilist))+'只，'+str(stoday)+"统计")
    
    printInLine_md(ilist,numberPerLine=numberPerLine,colalign=colalign)
    
    return
    

#==============================================================================
if __name__=='__main__':
    iname='大类风格--医药医疗'
    
    industry_sw_code('光伏设备')

def industry_sw_code(iname):
    """
    功能：将申万指数名称转换为指数代码。
    输入：指数名称
    输出：指数代码
    """
    industry=industry_sw_list()

    try:
        icode=industry[industry['name']==iname]['code'].values[0]
    except:
        #未查到
        #print("  #Warning(industry_sw_code): industry name not found",iname)
        return None
   
    return icode+'.SW'

if __name__=='__main__':
    iname='申万创业'
    industry_sw_code(iname)

#==============================================================================
def industry_sw_codes(inamelist):
    """
    功能：将申万指数名称/列表转换为指数代码列表。
    输入：指数名称/列表
    输出：指数代码列表
    """
    industry=industry_sw_list()

    icodelist=[]
    if isinstance(inamelist,str):
        icode=industry_sw_code(inamelist)
        if not (icode is None):
            icodelist=[icode]
        else:
            if inamelist.isdigit():
                return inamelist
            else:
                print("  #Warning(industries_sw_code): industry code not found for",inamelist)
                return None

    if isinstance(inamelist,list):
        if len(inamelist) == 0:
            print("  #Warning(industries_sw_code): no industry code found in for",inamelist)
            return None
        
        for i in inamelist:
            icode=industry_sw_code(i)
            if not (icode is None):
                icodelist=icodelist+[icode]
            else:
                if i.isdigit():
                    icodelist=icodelist+[i]
                else:
                    print("  #Warning(industries_sw_code): industry code not found",i)
                    return None
   
    return icodelist

if __name__=='__main__':
    inamelist='申万创业'
    industry_sw_codes(inamelist)
    
    inamelist=['申万创业','申万投资','申万制造','申万消费']
    industry_sw_codes(inamelist)
#==============================================================================
if __name__=='__main__':
    start='2018-1-1'
    end='2022-10-31'
    measure='Exp Ret%'
    itype='1'
    graph=True
    axisamp=0.8
    
def industry_ranking_sw(start,end,measure='Exp Ret%', \
                                itype='1',period="day", \
                                graph=True,axisamp=0.8):
    """
    完整版，全流程
    功能：模板，遍历某类申万指数，计算某项业绩指标，汇集排序
    itype: 
    股票类指数：F表征指数，n=1/2/3行业指数，S风格指数，B大类风格指数，C金创指数？
    基金类指数：J1/2/3基础一二三级，JF特色指数

    period="day"; choice of {"day", "week", "month"}
    绘图：柱状图，可选
    """
    #检查日期的合理性
    result,start1,end1=check_period(start,end)
    
    #检查itype的合理性
    
    #获得指数代码
    idf=industry_sw_list()
    idf1=idf[idf['type']==itype]
    ilist=list(idf1['code'])

    #循环获取指标
    import pandas as pd
    import akshare as ak
    import datetime
    df=pd.DataFrame(columns=['date','ticker','start','end','item','value'])

    print("\nSearching industry prices, it may take great time, please wait ...")
    
    fail_list=[]
    for i in ilist:
        
        print("  Processing index",i,"\b, please wait ...")
        #抓取指数价格，选取期间范围
        try:
            dft = ak.index_hist_sw(symbol=i,period="day")
        except:
            try:
                dft = ak.index_hist_fund_sw(symbol=i,period="day")
                dft['代码']=i
                dft['收盘']=dft['收盘指数']
                dft['开盘']=dft['收盘指数']
                dft['最高']=dft['收盘指数']
                dft['最低']=dft['收盘指数']
                dft['成交量']=0; dft['成交额']=0
            except:
                fail_list=fail_list+[i]
                continue
        
        dft['ticker']=dft['代码']
        dft['date']=dft['日期'].apply(lambda x: pd.to_datetime(x))
        dft.set_index('date',inplace=True)
        dft['Open']=dft['开盘']
        dft['High']=dft['最高']
        dft['Low']=dft['最低']
        dft['Close']=dft['收盘']
        dft['Adj Close']=dft['收盘']
        dft['Volume']=dft['成交量']
        dft['Amount']=dft['成交额']
        
        dft.sort_index(ascending=True,inplace=True)
        #dft1=dft[(dft.index>=start1) & (dft.index<=end1)]
        dft2=dft[['ticker','Open','High','Low','Close','Adj Close','Volume','Amount']]

        #计算指标
        dft3=all_calculate(dft2,i,start,end)
        dft4=dft3.tail(1)
        
        #记录
        idate=dft4.index.values[0]
        idate=pd.to_datetime(idate)
        iend=idate.strftime('%Y-%m-%d')
        try:
            ivalue=round(dft4[measure].values[0],2)
            s=pd.Series({'date':idate,'ticker':i,'start':start,'end':iend,'item':measure,'value':ivalue})
            try:
                df=df.append(s,ignore_index=True)
            except:
                df=df._append(s,ignore_index=True)
        except:
            print("  #Error(industry_ranking_sw): measure not supported",measure)
            return None
        
    df.sort_values(by='value',ascending=True,inplace=True)
    df['name']=df['ticker'].apply(lambda x: industry_sw_name(x))
    df.set_index('name',inplace=True)
    colname='value'
    titletxt="行业/指数分析：业绩排名"
    import datetime; today=datetime.date.today()
    footnote0=ectranslate(measure)+' ==>\n'
    footnote1='申万行业/指数分类，观察期：'+start+'至'+iend+'\n'
    footnote2="数据来源: 申万宏源, "+str(today)
    footnote=footnote0+footnote1+footnote2
    
    plot_barh(df,colname,titletxt,footnote,axisamp=axisamp) 
    #plot_barh2(df,colname,titletxt,footnote)
    
    if len(fail_list) > 0:
        print("  Unable to retrieve",len(fail_list),"industry(ies) as follows:",end='')
        if len(fail_list) >= 10:
            printInLine_md(fail_list,numberPerLine=10,colalign='left',font_size='16px')
        else:
            printInLine_md(fail_list,numberPerLine=len(fail_list),colalign='left',font_size='16px')
        print('') #空一行

    return df
    
if __name__=='__main__':
    start='2018-1-1'
    end='2022-10-31'
    measure='Exp Ret%'
    itype='1'
    graph=True
    axisamp=0.8
    
    df=industry_ranking_sw(start,end,measure='Exp Ret%',axisamp=0.8)
    
#==============================================================================
def industry_ranking_sw2(industrylist,start,end,measure='Exp Ret%', \
                         period="day", \
                         graph=True,axisamp=0.8):
    """
    完整版，全流程
    功能：模板，遍历某些指定的申万指数，计算某项业绩指标，汇集排序
    特点：不限类别，自由指定申万指数；指定行业指定指标横截面对比
    period="day"; choice of {"day", "week", "month"}
    绘图：柱状图，可选
    """
    industry_list1=[]
    for i in industrylist:
        i=i.split('.')[0]
        industry_list1=industry_list1+[i]
    industrylist=industry_list1    
    
    #检查日期的合理性
    result,start1,end1=check_period(start,end)
    
    #检查itype的合理性
    
    #获得指数代码
    ilist=industrylist

    #循环获取指标
    import pandas as pd
    import akshare as ak
    import datetime
    df=pd.DataFrame(columns=['date','ticker','start','end','item','value'])

    print("\nSearching industry prices, it may take great time, please wait ...")
    for i in ilist:
        
        print("  Processing industry",i,"\b, please wait ...")
        #抓取指数价格，选取期间范围
        try:
            dft = ak.index_hist_sw(symbol=i,period="day")
        except:
            try:
                dft = ak.index_hist_fund_sw(symbol=i,period="day")
                dft['代码']=i
                dft['收盘']=dft['收盘指数']
                dft['开盘']=dft['收盘指数']
                dft['最高']=dft['收盘指数']
                dft['最低']=dft['收盘指数']
                dft['成交量']=0; dft['成交额']=0
            except:                
                print("  #Warning(industry_ranking_sw2): index not found for",i)
                continue
        
        dft['ticker']=dft['代码']
        dft['date']=dft['日期'].apply(lambda x: pd.to_datetime(x))
        dft.set_index('date',inplace=True)
        dft['Open']=dft['开盘']
        dft['High']=dft['最高']
        dft['Low']=dft['最低']
        dft['Close']=dft['收盘']
        dft['Adj Close']=dft['收盘']
        dft['Volume']=dft['成交量']
        dft['Amount']=dft['成交额']
        
        dft.sort_index(ascending=True,inplace=True)
        #dft1=dft[(dft.index>=start1) & (dft.index<=end1)]
        dft2=dft[['ticker','Open','High','Low','Close','Adj Close','Volume','Amount']]

        #计算指标
        dft3=all_calculate(dft2,i,start,end)
        dft4=dft3.tail(1)
        
        #记录
        idate=dft4.index.values[0]
        idate=pd.to_datetime(idate)
        iend=idate.strftime('%Y-%m-%d')
        try:
            ivalue=round(dft4[measure].values[0],2)
            s=pd.Series({'date':idate,'ticker':i,'start':start,'end':iend,'item':measure,'value':ivalue})
            try:
                df=df.append(s,ignore_index=True)
            except:
                df=df._append(s,ignore_index=True)
        except:
            print("  #Error(industry_ranking_sw): measure not supported",measure)
            return None
        
    df.sort_values(by='value',ascending=True,inplace=True)
    df['name']=df['ticker'].apply(lambda x: industry_sw_name(x))
    df.set_index('name',inplace=True)
    
    df.dropna(inplace=True)
    
    colname='value'
    titletxt="行业/指数分析：业绩排名"
    import datetime; today=datetime.date.today()
    footnote0=ectranslate(measure)+' ==>\n'
    footnote1='申万行业/指数分类，观察期：'+start+'至'+iend+'\n'
    footnote2="数据来源: 申万宏源, "+str(today)
    footnote=footnote0+footnote1+footnote2
    
    plot_barh(df,colname,titletxt,footnote,axisamp=axisamp) 
    #plot_barh2(df,colname,titletxt,footnote)

    return df
#==============================================================================
if __name__=='__main__':
    start='2018-1-1'
    end='2022-10-31'
    measure='Exp Ret%'
    itype='F'
    period="day"
    industry_list='all'    
    
def get_industry_sw(itype='1',period="day",industry_list='all',max_sleep=30):
    """
    功能：遍历某类申万指数，下载数据
    itype: 
    股票类指数：F表征指数，n=1/2/3行业指数，S风格指数，B大类风格指数，C金创指数？
    基金类指数：J1/2/3基础一二三级，JF特色指数

    period="day"; choice of {"day", "week", "month"}
    industry_list: 允许选择部分行业
    """
    
    #检查itype的合理性
    typelist=['F','1','2','3','S','B','C','A']
    if not (itype in typelist):
        print("  #Error(get_industry_sw): unsupported industry category",itype)
        print("  Supported industry category",typelist)
        print("  F: Featured, n-Level n industry, S-Styled, B- Big Styled, C- Financial Innovation, A-All (more time))")
        return None
    
    #获得指数代码
    if industry_list=='all':
        idf=industry_sw_list()
        
        if itype == 'A':
            ilist=list(idf['code'])
        else:
            idf1=idf[idf['type']==itype]
            ilist=list(idf1['code'])
    else:
        ilist=industry_list
        
    #循环获取指标
    import pandas as pd
    import akshare as ak
    import datetime; import random; import time
    df=pd.DataFrame()

    print("  Searching industry data, it takes time, please wait ...")
    num=len(ilist)
    if num <= 10:
        steps=5
    else:
        steps=10
        
    total=len(ilist)
    fail_list=[]
    for i in ilist:
        #print_progress_percent2(i,ilist,steps=5,leading_blanks=4)
        #print("  Retrieving information for industry",i)
        
        #抓取指数价格
        try:
            dft = ak.index_hist_sw(symbol=i,period="day")
        except:
            try:
                dft = ak.index_hist_fund_sw(symbol=i,period="day")
                dft['代码']=i
                dft['收盘']=dft['收盘指数']
                dft['开盘']=dft['收盘指数']
                dft['最高']=dft['收盘指数']
                dft['最低']=dft['收盘指数']
                dft['成交量']=0; dft['成交额']=0
            except:            
                #print("  #Warning(get_industry_sw): unsupported industry",i)
                fail_list=fail_list+[i]
                continue
        
        dft['ticker']=dft['代码']
        dft['date']=dft['日期'].apply(lambda x: pd.to_datetime(x))
        dft.set_index('date',inplace=True)
        dft['Open']=dft['开盘']
        dft['High']=dft['最高']
        dft['Low']=dft['最低']
        dft['Close']=dft['收盘']
        dft['Adj Close']=dft['收盘']
        dft['Volume']=dft['成交量']
        dft['Amount']=dft['成交额']
        
        dft.sort_index(ascending=True,inplace=True)
        dft2=dft[['ticker','Open','High','Low','Close','Adj Close','Volume','Amount']]
        try:
            df=df.append(dft2)
        except:
            df=df._append(dft2)
        
        current=ilist.index(i)
        #print_progress_percent(current,total,steps=steps,leading_blanks=2)
        
        print_progress_percent2(i,ilist,steps=steps,leading_blanks=4)
        #生成随机数睡眠，试图防止被反爬虫，不知是否管用！
        random_int=random.randint(1,max_sleep)
        time.sleep(random_int)        
    
    #num=list(set(list(df['ticker'])))
    if len(df)>0: 
        print("  Successfully retrieved",len(df),"records in",len(ilist)-len(fail_list),"industries")
    
    if len(fail_list) > 0:
        print("  Failed to retrieve",len(fail_list),"industry(ies) as follows:")
        if len(fail_list) >= 10:
            printInLine_md(fail_list,numberPerLine=10,colalign='left',font_size='16px')
        else:
            printInLine_md(fail_list,numberPerLine=len(fail_list),colalign='left',font_size='16px')
    
    return df

    
if __name__=='__main__':
    df=get_industry_sw('F')

#==============================================================================
if __name__=='__main__':
    start='2018-1-1'
    end='2022-10-31'
    measure='Exp Ret%'
    period="day"
    industry_list=['850831.SW','801785.SW','801737.SW','801194.SW',
                   '801784.SW','801783.SW','801782.SW']    
    
def get_industry_sw2(industry_list,period="day",max_sleep=30):
    """
    功能：遍历指定的申万指数列表，下载数据
    period="day"; choice of {"day", "week", "month"}
    """
    industry_list1=[]
    for i in industry_list:
        i=i.split('.')[0]
        industry_list1=industry_list1+[i]
    industry_list=industry_list1
    
    #循环获取指标
    import pandas as pd
    import akshare as ak
    import datetime; import random; import time
    df=pd.DataFrame()

    print("  Searching industry information, it takes time, please wait ...")
    ilist=industry_list
    num=len(ilist)
    if num <= 10:
        steps=5
    else:
        steps=10
        
    total=len(ilist)
    fail_list=[]
    for i in ilist:
        #print("  Retrieving information for industry",i)
        #抓取指数价格
        try:
            dft = ak.index_hist_sw(symbol=i,period="day")
        except:
            try:
                dft = ak.index_hist_fund_sw(symbol=i,period="day")
                dft['代码']=i
                dft['收盘']=dft['收盘指数']
                dft['开盘']=dft['收盘指数']
                dft['最高']=dft['收盘指数']
                dft['最低']=dft['收盘指数']
                dft['成交量']=0; dft['成交额']=0
            except:            
                #print("  #Warning(get_industry_sw): unsupported industry",i)
                fail_list=fail_list+[i]
                continue
        
        dft['ticker']=dft['代码']
        dft['date']=dft['日期'].apply(lambda x: pd.to_datetime(x))
        dft.set_index('date',inplace=True)
        dft['Open']=dft['开盘']
        dft['High']=dft['最高']
        dft['Low']=dft['最低']
        dft['Close']=dft['收盘']
        dft['Adj Close']=dft['收盘']
        dft['Volume']=dft['成交量']
        dft['Amount']=dft['成交额']
        
        dft.sort_index(ascending=True,inplace=True)
        dft2=dft[['ticker','Open','High','Low','Close','Adj Close','Volume','Amount']]
        try:
            df=df.append(dft2)
        except:
            df=df._append(dft2)
        
        current=ilist.index(i)
        print_progress_percent(current,total,steps=steps,leading_blanks=2)
        
        #生成随机数睡眠，试图防止被反爬虫，不知是否管用！
        random_int=random.randint(1,max_sleep)
        time.sleep(random_int)        
    
    #num=list(set(list(df['ticker'])))
    if len(df) > 0:
        print("\n  Successfully retrieved",len(df),"records in",len(ilist)-len(fail_list),"industries")

    if len(fail_list) > 0:
        print("  Failed to retrieve",len(fail_list),"industry(ies) as follows:")
        if len(fail_list) >= 10:
            printInLine_md(fail_list,numberPerLine=10,colalign='left',font_size='16px') 
        else:
            printInLine_md(fail_list,numberPerLine=len(fail_list),colalign='left',font_size='16px')
        
    
    return df

#==============================================================================
if __name__=='__main__':
    start='2023-8-31'
    end='2024-9-30'
    df=get_industry_sw('F')
    
def calc_industry_sw(df,start,end):
    """
    功能：遍历某类申万指数，计算某项业绩指标，汇集排序
    df: 来自于get_industry_sw
    输出：最新时刻数据idf，全部时间序列数据idfall
    """
    #检查日期的合理性
    result,start1,end1=check_period(start,end)
    if not result:
        print("  #Warning(calc_industry_sw): invalid date period",start,end)
        return None

    #屏蔽函数内print信息输出的类
    import os, sys
    class HiddenPrints:
        def __enter__(self):
            self._original_stdout = sys.stdout
            sys.stdout = open(os.devnull, 'w')

        def __exit__(self, exc_type, exc_val, exc_tb):
            sys.stdout.close()
            sys.stdout = self._original_stdout
            
    #获得指数代码
    ilist=list(set(list(df['ticker'])))
    ilist.sort()

    #循环获取指标
    import pandas as pd
    import datetime
    idf=pd.DataFrame()
    idfall=pd.DataFrame()

    print("  Calculating industry performance, please wait ...")
    num=len(ilist)
    if num <= 10:
        steps=5
    else:
        steps=10
        
    total=len(ilist)
    ignored_list=[]
    for i in ilist:
        
        #print("  Processing industry",i)
        
        #切片一个指数的历史价格
        dft = df[df['ticker']==i]
        # 若无数据则处理下一个
        if len(dft)==0: continue
        
        dft.sort_index(ascending=True,inplace=True)
        dft2=dft

        #计算指标
        try:
            with HiddenPrints():
                dft3=all_calculate(dft2,i,start,end)
        except:
            ignored_list=ignored_list+[i]
            #print("  #Warning(calc_industry_sw): A problem occurs for industry",i)
            continue
        if dft3 is None:
            ignored_list=ignored_list+[i]
            #print("  #Warning(calc_industry_sw): Shenwan index",i,"may be discontinued before",start,"\b, ignored.")
            continue
        
        dft3['start']=start

        #截取绘图区间
        dft3a=dft3[(dft3.index >= start1) & (dft3.index <= end1)]
        
        dft4=dft3a.tail(1)
        try:
            idf=idf.append(dft4)
            idfall=idfall.append(dft3a)
        except:
            idf=idf._append(dft4)
            idfall=idfall._append(dft3a)

        current=ilist.index(i)
        print_progress_percent(current,total,steps=steps,leading_blanks=2) 
    
    ignored_num=len(ignored_list)
    print("  Successfully processed",len(ilist)-ignored_num,"industries,",ignored_num,"industry(ies) ignored")
    if ignored_num>0:
        print("  Ignored industry(ies):",ignored_list)
        
    return idf,idfall
    
if __name__=='__main__':
    start='2018-1-1'
    end='2022-10-31'
    idf,idfall=calc_industry_sw(df,start,end)
    
#==============================================================================
#==============================================================================
if __name__=='__main__':
    measure='Exp Ret%'
    industries=[]
    graph=True
    axisamp=0.8
    px=False
    maxitems=32
    printout=False
    
    industries=['801770.SW','801720.SW','医药生物']
    
def rank_industry_sw(idf,measure='Exp Ret%',industries=[], \
                     graph=True,axisamp=0.8,px=False,maxitems=32, \
                     printout=False,facecolor='papayawhip',font_size='16px'):
    """
    ===========================================================================
    功能：遍历某类申万指数的某项业绩指标，汇集排序，绘制水平柱状图
    主要参数：
    idf：行业基础数据，由下列指令生成：
        idf,idfall=get_industry_data_sw(start,end,sw_level='1')
    measure：排名指标，默认'Exp Ret%'
    industries：指定排名哪些特定行业，默认全部行业[]
    graph：是否绘图，默认True
    maxitems：一幅图最多绘制maxitems个项目，默认32
    axisamp=0.9：调节水平柱子伸缩比例，数值越大越收缩，数值越小越放大，有时也需要负数
    px=False：默认不使用plotly express
    printout：是否打印结果数值，默认False
    facecolor：背景颜色，默认'papayawhip'
    font_size：输出表格的字体大小，默认'16px'
    
    示例：
    df1=rank_industry_sw(idf,measure='Exp Ret%',
                     axisamp=0.85)
    # 选择感兴趣的行业，观察其持有收益率的发展趋势
    industries1=industry_sw_codes(['电力设备','食品饮料','国防军工','银行'])
    df1i=compare_industry_sw(idfall,industries1,measure='Exp Ret%')
    
    df1risk=rank_industry_sw(idf,measure='Exp Ret Volatility%',
                         axisamp=1.6)
    
    # 全行业，夏普比率横向对比
    df1sharpe=rank_industry_sw_sharpe(idfall,base_return='Exp Ret%',axisamp=0.8)
    """
    industry_list1=[]
    for i in industries:
        i=i.split('.')[0]
        industry_list1=industry_list1+[i]
    industries=industry_list1
    
    import pandas as pd
    import datetime as dt
    
    idf['Date']= pd.to_datetime(idf.index) 
    idf['end'] = idf['Date'].dt.strftime('%Y-%m-%d')    
    
    #获得指标数据
    try:
        gdf=idf[['ticker',measure,'start','end']]
        num1=len(gdf)
    except:
        print("  #Error(rank_industry_sw): unsupported measurement",measure)
        return None

    gdf.dropna(inplace=True)
    num2=len(gdf)
    if num2==0:
        print("  #Error(rank_industry_sw): no data found for",measure)
        return None

    if num2 < num1:
        print("  #Warning(rank_industry_sw):",num1-num2,"industries removed as no enough data found for",measure)
        
    gdf[measure]=gdf[measure].apply(lambda x: round(x,1))
    istart=gdf['start'].values[0]
    idate=gdf.index.values[0]
    idate=pd.to_datetime(idate)
    iend=idate.strftime('%Y-%m-%d')

    gdf['name']=gdf['ticker'].apply(lambda x: industry_sw_name(x))
    gdf.set_index('name',inplace=True)
    gdf.sort_values(by=measure,ascending=True,inplace=True)
    
    if len(industries) > 0:
        gdf1a=gdf[gdf.index.isin(industries)]
        gdf1b=gdf[gdf.ticker.isin(industries)]
        gdf1=pd.concat([gdf1a,gdf1b])
        gdf1.sort_values(by=measure,ascending=True,inplace=True)
    else:
        gdf1=gdf
    
    if printout or graph:
        titletxt="行业板块/指数分析：最新业绩排名"
        import datetime; today=datetime.date.today()
        footnote0=ectranslate(measure)+' -->\n\n'
        footnote1='申万行业/指数分类，'+iend+'快照'
        footnote2='观察期：'+istart+'至'+iend+'，'
        footnote3="数据来源: 申万宏源, "+str(today)+'统计'
        footnote=footnote0+footnote1+'\n'+footnote2+footnote3
    
    if printout or (len(gdf1) > maxitems):
        gdf2=gdf1.sort_values(by=measure,ascending=False)
        gdf2.reset_index(inplace=True)
        gdf2.index=gdf2.index+1
        gdf2.columns=['行业/指数名称','行业/指数代码',ectranslate(measure),'开始日期','结束日期']
        """
        print("***",titletxt,'\n')
        alignlist=['center']+['left']*(len(list(gdf2))-1)
        print(gdf2.to_markdown(index=True,tablefmt='plain',colalign=alignlist))
        """
        #确定表格字体大小
        titile_font_size=font_size
        heading_font_size=data_font_size=str(int(font_size.replace('px',''))-1)+'px'
        
        df_display_CSS(gdf2,titletxt=titletxt,footnote=footnote,facecolor=facecolor, \
                       titile_font_size=titile_font_size,heading_font_size=heading_font_size, \
                           data_font_size=data_font_size)

    if graph:
        if (len(gdf1) <= maxitems):
            colname=measure
            if not px:
                footnote=footnote0+footnote1+'\n'+footnote2+footnote3
                plot_barh(gdf1,colname,titletxt,footnote,axisamp=axisamp)
            else: #使用plotly_express
                titletxt="行业板块/指数业绩排名："+ectranslate(measure)
                footnote=footnote1+'。'+footnote2+footnote3
                plot_barh2(gdf1,colname,titletxt,footnote)
        else:
            print("\n  #Sorry, there are too much items to be illustrated")
            print("  Solution: select some of them and use the industries=[] option")
            
    return gdf
    
if __name__=='__main__':
    measure='Exp Ret%'
    axisamp=0.8
    
    gdf=analyze_industry_sw(idf,measure='Exp Ret%',axisamp=0.8)
    gdf=analyze_industry_sw(idf,measure='Exp Ret Volatility%',axisamp=1.6)
    gdf=analyze_industry_sw(idf,measure='Exp Ret LPSD%',axisamp=1.7)
    gdf=analyze_industry_sw(idf,measure='Annual Ret Volatility%',axisamp=1.3)
    gdf=analyze_industry_sw(idf,measure='Annual Ret%',axisamp=1.0)
    gdf=analyze_industry_sw(idf,measure='Quarterly Ret%',axisamp=0.3)
    gdf=analyze_industry_sw(idf,measure='Monthly Ret%',axisamp=0.6)
    
#==============================================================================
if __name__=='__main__':
    industry_list=['801050.SW','801080.SW']
    measure='Exp Ret%'
    start='2020-11-1'
    end='2022-10-31'
    itype='1'
    period="day"
    graph=True

def compare_mindustry_sw(industry_list,measure,start,end, \
                         itype='1',period="day",graph=True,printout=False,sortby='tpw_mean'):
    """
    功能：比较多个行业industry_list某个指标measure在时间段start/end的时间序列趋势
    industry_list: 至少有两项，若太多了则生成的曲线过于密集
    特点：完整过程
    """ 
    """
    #检查行业代码的个数不少于两个
    if len(industry_list) < 2:
        print("  #Warning(compare_mindustry_sw): need at least 2 indistries to compare")
        return None
    """
    industry_list1=[]
    for i in industry_list:
        i=i.split('.')[0]
        industry_list1=industry_list1+[i]
    industry_list=industry_list1
    
    #检查行业代码是否在范围内
    ilist_all=list(industry_sw_list()['code'])
    for i in industry_list:
        if not (i in ilist_all):
            print("  #Warning(compare_mindustry_sw): unsupported industry",i)
            return None
    
    
    #检查日期期间的合理性
    result,startpd,endpd=check_period(start,end)
    if not result:
        print("  #Error(compare_mindustry_sw): invalid date period",start,end)
        return None
    
    
    #获取数据
    ddf=get_industry_sw(itype=itype,period=period,industry_list=industry_list)
    found=df_have_data(ddf)
    if not found=='Found':
        print("  #Warning(compare_mindustry_sw): data tentatively unavailable for group",itype)
        print("  Data is sometimes unavialble at certain tie points, eg public holidays")
        return None
    
    #计算指标
    _,idf=calc_industry_sw(ddf,start,end)
    
    #转换数据表结构为横排并列，适应绘图要求
    ilist=list(set(list(idf['ticker'])))
    import pandas as pd
    dfs=pd.DataFrame()
    notfoundlist=[]
    for i in ilist:
        
        dft=idf[idf['ticker']==i]
        istart=idf['start'].values[0]
        
        try:
            dft1=pd.DataFrame(dft[measure])
        except:
            print("  #Error(compare_mindustry_sw) unsupported measurement",measure)
            return None
        dft1.dropna(inplace=True)
        if len(dft1)==0:
            notfoundlist=notfoundlist+[i]
            continue
        
        dft1.rename(columns={measure:industry_sw_name(i)},inplace=True)
        if len(dfs)==0:
            dfs=dft1
        else:
            dfs=pd.merge(dfs,dft1,how='outer',left_index=True,right_index=True)
    
    if len(notfoundlist) > 0:
        print("  #Warning(compare_mindustry_sw): industry measure not found",notfoundlist)
        
    #绘制多条曲线
    idate=dfs.index.values[-1]
    idate=pd.to_datetime(idate)
    iend=idate.strftime('%Y-%m-%d')

    #截取绘图区间
    result,istartpd,iendpd=check_period(istart,iend)
    dfs1=dfs[(dfs.index >= istartpd) & (dfs.index <= iendpd)]
    
    y_label=measure
    title_txt="行业板块/指数分析：市场业绩趋势与评价"
    import datetime; today = datetime.date.today()
    if graph:
        colname=measure
        
        import datetime; today=datetime.date.today()
        footnote1='\n申万行业/指数分类，观察期：'+istart+'至'+iend+'\n'
        footnote2="数据来源: 申万宏源, "+str(today)+'统计'
        footnote=footnote1+footnote2

        draw_lines(dfs1,y_label,x_label=footnote, \
                   axhline_value=0,axhline_label='', \
                   title_txt=title_txt, \
                   data_label=False,resample_freq='H',smooth=True)

    if printout:
        df2=dfs1
        dfcols=list(df2)
        for c in dfcols:
            ccn=ticker_name(c)+'('+c+')'
            df2.rename(columns={c:ccn},inplace=True)
        
        if sortby=='tpw_mean':
            sortby_txt='按推荐标记+近期优先加权平均值降序排列'
        elif sortby=='min':
            sortby_txt='按推荐标记+最小值降序排列'
        elif sortby=='mean':
            sortby_txt='按推荐标记+平均值降序排列'
        elif sortby=='median':
            sortby_txt='按推荐标记+中位数值降序排列'
        else:
            pass
        
        title_txt=title_txt+'：'+y_label+'，'+sortby_txt
        additional_note="注：列表仅显示有星号标记或特定数量的证券。"
        footnote='比较期间：'+start+'至'+end
        ds=descriptive_statistics(df2,title_txt,additional_note+footnote,decimals=4, \
                               sortby=sortby,recommend_only=False)
    
    return dfs
    
if __name__=='__main__':
    mdf=compare_mindustry_sw(industry_list,measure,start,end)

#==============================================================================
if __name__=='__main__':
    industry_list=['801050.SW','801080.SW']
    measure='Exp Ret%'
    start='2023-1-1'
    end='2023-4-11'
    period="day"
    graph=True
    printout=False
    sortby='tpw_mean'

def compare_mindustry_sw2(industry_list,measure,start,end, \
                         period="day",graph=True,printout=False,sortby='tpw_mean'):
    """
    功能：比较多个行业industry_list某个指标measure在时间段start/end的时间序列趋势
    industry_list: 至少有两项，若太多了则生成的曲线过于密集
    特点：完整过程，无需规定申万行业类别；多个行业，单一指标
    """ 
    """
    #检查行业代码的个数不少于两个
    if len(industry_list) < 2:
        print("  #Warning(compare_mindustry_sw): need at least 2 indistries to compare")
        return None
    """
    industry_list1=[]
    for i in industry_list:
        i=i.split('.')[0]
        industry_list1=industry_list1+[i]
    industry_list=industry_list1
    
    #检查行业代码是否在范围内
    ilist_all=list(industry_sw_list()['code'])
    for i in industry_list:
        if not (i in ilist_all):
            if not i.isdigit():
                print("  #Warning(compare_mindustry_sw): unsupported industry",i)
                return None
    
    #检查日期期间的合理性
    result,startpd,endpd=check_period(start,end)
    if not result:
        print("  #Error(compare_mindustry_sw): invalid date period",start,end)
        return None
    
    #获取数据
    ddf=get_industry_sw2(industry_list=industry_list,period=period)
    found=df_have_data(ddf)
    if not found=='Found':
        print("  #Warning(compare_mindustry_sw): data tentatively unavailable for",industry_list)
        print("  Data is sometimes unavialble at certain tie points, eg public holidays")
        return None
    
    #计算指标
    _,idf=calc_industry_sw(ddf,start,end)
    
    #转换数据表结构为横排并列，适应绘图要求
    ilist=list(set(list(idf['ticker'])))
    import pandas as pd
    dfs=pd.DataFrame()
    notfoundlist=[]
    for i in ilist:
        
        dft=idf[idf['ticker']==i]
        istart=idf['start'].values[0]
        
        try:
            dft1=pd.DataFrame(dft[measure])
        except:
            print("  #Error(compare_mindustry_sw) unsupported measurement",measure)
            return None
        dft1.dropna(inplace=True)
        if len(dft1)==0:
            notfoundlist=notfoundlist+[i]
            continue
        
        dft1.rename(columns={measure:industry_sw_name(i)},inplace=True)
        if len(dfs)==0:
            dfs=dft1
        else:
            dfs=pd.merge(dfs,dft1,how='outer',left_index=True,right_index=True)
    
    if len(notfoundlist) > 0:
        print("  #Warning(compare_mindustry_sw): industry measure not found for",notfoundlist)
        
    #绘制多条曲线
    idate=dfs.index.values[-1]
    idate=pd.to_datetime(idate)
    iend=idate.strftime('%Y-%m-%d')

    #截取绘图区间
    result,istartpd,iendpd=check_period(istart,iend)
    dfs1=dfs[(dfs.index >= istartpd) & (dfs.index <= iendpd)]
    
    y_label=measure
    title_txt="行业(板块)/指数分析：市场业绩趋势与评价"
    import datetime; today = datetime.date.today()
    if graph:
        colname=measure
        title_txt="行业(板块)/指数分析：市场业绩趋势"
        import datetime; today=datetime.date.today()
        footnote1='\n申万行业/指数分类，观察期：'+istart+'至'+iend+'\n'
        footnote2="数据来源: 申万宏源, "+str(today)+'统计'
        footnote=footnote1+footnote2

        draw_lines(dfs1,y_label,x_label=footnote, \
                   axhline_value=0,axhline_label='', \
                   title_txt=title_txt, \
                   data_label=False,resample_freq='H',smooth=True)

    if printout:
        df2=dfs1
        dfcols=list(df2)
        for c in dfcols:
            cname=ticker_name(c)
            if cname == c:
                ccn=c
            else:
                ccn=cname+'('+c+')'
                df2.rename(columns={c:ccn},inplace=True)
        
        if sortby=='tpw_mean':
            sortby_txt='按推荐标记+近期优先加权平均值降序排列'
        elif sortby=='min':
            sortby_txt='按推荐标记+最小值降序排列'
        elif sortby=='mean':
            sortby_txt='按推荐标记+平均值降序排列'
        elif sortby=='median':
            sortby_txt='按推荐标记+中位数值降序排列'
        else:
            pass
        
        title_txt='*** '+title_txt+'：'+y_label+'，'+sortby_txt
        additional_note="*** 注：列表仅显示有星号标记或特定数量的证券。"
        footnote='比较期间：'+start+'至'+end
        ds=descriptive_statistics(df2,title_txt,additional_note+footnote,decimals=4, \
                               sortby=sortby,recommend_only=False)
    
    return dfs
    
if __name__=='__main__':
    mdf=compare_mindustry_sw2(industry_list,measure,start,end)

#==============================================================================
if __name__=='__main__':
    industry_list=['801050.SW','801080.SW']
    measure='Exp Ret%'
    start='2020-11-1'
    end='2022-10-31'
    itype='1'
    period="day"
    graph=True

def compare_industry_sw(idfall,industry_list,measure,graph=True):
    """
    功能：比较多个行业industry_list某个指标measure在时间段start/end的时间序列趋势
    industry_list: 至少有两项，若太多了则生成的曲线过于密集
    特点：需要依赖其他前序支持
    #获取数据
    ddf=get_industry_sw(itype=itype,period=period,industry_list=industry_list)
    
    #计算指标
    idf=calc_industry_sw(ddf,start,end,latest=False)
    
    """    
    """
    #检查行业代码的个数不少于两个
    if len(industry_list) < 2:
        print("  #Warning(compare_industry_sw): need at least 2 indistries to compare")
        return None
    """
    industry_list1=[]
    for i in industry_list:
        i=i.split('.')[0]
        industry_list1=industry_list1+[i]
    industry_list=industry_list1
    
    #检查行业代码是否在范围内
    ilist_all=list(industry_sw_list()['code'])
    for i in industry_list:
        if not (i in ilist_all):
            if not i.isdigit():
                print("  #Warning(compare_mindustry_sw): unsupported or no such industry",i)
                return None
    
    #转换数据表结构为横排并列，适应绘图要求
    import pandas as pd
    dfs=pd.DataFrame()
    notfoundlist=[]
    for i in industry_list:
        
        try:
            dft=idfall[idfall['ticker']==i]
        except:
            print("  #Error(compare_mindustry_sw) unsupported or no such industry",i)
            return None
        
        if not (len(dft)==0):
            istart=dft['start'].values[0]
        else:
            print("  #Error(compare_mindustry_sw) unsupported or no such industry",i)
            return None

        try:
            dft1=pd.DataFrame(dft[measure])
        except:
            print("  #Error(compare_mindustry_sw) unsupported measurement",measure)
            return None
        dft1.dropna(inplace=True)
        if len(dft1)==0:
            notfoundlist=notfoundlist+[i]
            #print("  #Warning(compare_mindustry_sw): no data found for industry",i,"on",measure)
            continue
        
        dft1.rename(columns={measure:industry_sw_name(i)},inplace=True)
        if len(dfs)==0:
            dfs=dft1
        else:
            dfs=pd.merge(dfs,dft1,how='outer',left_index=True,right_index=True)
    
    if len(notfoundlist)>0:
        print("  #Warning(compare_mindustry_sw):",measure,"data not found for industries",notfoundlist)
    
    #绘制多条曲线
    idate=dfs.index.values[-1]
    idate=pd.to_datetime(idate)
    iend=idate.strftime('%Y-%m-%d')
    
    #截取数据区间
    result,istartpd,iendpd=check_period(istart,iend)
    dfs1=dfs[(dfs.index >= istartpd) & (dfs.index <= iendpd)]
    
    if graph:
        y_label=measure
        colname=measure
        title_txt="行业板块/指数分析：市场业绩趋势"
        
        import datetime; today=datetime.date.today()
        footnote1='\n申万行业/指数分类，观察期：'+istart+'至'+iend+'\n'
        footnote2="数据来源: 申万宏源, "+str(today)+'统计'
        footnote=footnote1+footnote2

        if 'Ret%' in measure:
            axhline_label='收益零线'
        else:
            axhline_label=''

        draw_lines(dfs1,y_label,x_label=footnote, \
                   axhline_value=0,axhline_label=axhline_label, \
                   title_txt=title_txt, \
                   data_label=False,resample_freq='H',smooth=True)

    return dfs1
    
if __name__=='__main__':
    mdf=compare_industry_sw(idfall,industry_list,measure)

#==============================================================================
if __name__=='__main__':
    start='2018-1-1'
    end='2022-10-31'
    df=get_industry_sw('F')
    idf,idfall=calc_industry_sw(df,start,end)
    base_return='Annual Ret%'
    graph=True

def compare_industry_sw_sharpe(idfall,industries,base_return='Annual Ret%',graph=True):
    """
    功能：比较申万行业的夏普比率
    idfall: 由calc_industry_sw函数获得
    industries: 仅限idfall中的行业
    
    缺陷：未考虑无风险利率
    """
    
    #获得年度收益率TTM
    aret=compare_industry_sw(idfall,industries,measure=base_return,graph=False)
    if aret is None:
        return None
    
    #获得年度收益率波动率TTM
    pos=base_return.index('%')
    base_risk=base_return[:pos]+' Volatility%'
    aretrisk=compare_industry_sw(idfall,industries,measure=base_risk,graph=False)
    
    #合成
    industrylist=list(aret)  
    atmp=pd.merge(aret,aretrisk,how='inner',left_index=True,right_index=True)
    for i in industrylist:
        atmp[i]=atmp[i+'_x']/atmp[i+'_y']
        
    sdf=atmp[industrylist]
    if graph:
        y_label='夏普比率（基于'+ectranslate(base_return)+'）'
        title_txt="行业板块/指数分析：市场发展趋势"
        
        istart=sdf.index[0].strftime('%Y-%m-%d')
        iend=sdf.index[-1].strftime('%Y-%m-%d')
        footnote1='\n申万行业/指数分类，观察期：'+istart+'至'+iend+'\n'
        import datetime; today=datetime.date.today()
        #footnote2="数据来源: 申万宏源, "+str(today)+'统计（未计入无风险利率）'
        footnote2="数据来源: 申万宏源, "+str(today)+'统计'
        footnote=footnote1+footnote2

        if 'Ret%' in base_return:
            axhline_label='收益零线'
        else:
            axhline_label=''

        draw_lines(sdf,y_label,x_label=footnote, \
                   axhline_value=0,axhline_label=axhline_label, \
                   title_txt=title_txt, \
                   data_label=False,resample_freq='H',smooth=True)
    
    return sdf

if __name__=='__main__':
    industries=['801005', '801270', '801250', '801260']
    sdf=compare_industry_sw_sharpe(idfall,industries,base_return='Annual Ret%')
    sdf=compare_industry_sw_sharpe(idfall,industries,base_return='Quarterly Ret%')
    
    sdf=compare_industry_sw_sharpe(idfall,industries,base_return='Exp Ret%')
    
#==============================================================================
if __name__=='__main__':
    start='2018-1-1'
    end='2022-10-31'
    df=get_industry_sw('F')
    idf,idfall=calc_industry_sw(df,start,end)
    base_return='Exp Ret%'
    graph=True
    
    df=rank_industry_sw_sharpe(idfall,base_return='Exp Ret%',axisamp=0.8)

def rank_industry_sw_sharpe(idfall,base_return='Exp Ret%',graph=True,axisamp=0.8,px=False):
    """
    功能：比较申万行业最近的夏普比率，绘制水平柱状图
    idfall: 由calc_industry_sw函数获得
    
    缺陷：未考虑无风险利率
    """

    allindustries=list(set(list(idfall['ticker'])))
    df=compare_industry_sw_sharpe(idfall,allindustries,base_return=base_return,graph=False)
    dftail1=df.tail(1)
    dftail2=dftail1.T
    col=list(dftail2)[0]
    
    dftail3=dftail2.sort_values(by=col,ascending=True)
    dftail3[col]=dftail3[col].apply(lambda x: round(x,2))
        
    istart=idfall['start'].values[0]
    idate=idfall.index.values[-1]
    idate=pd.to_datetime(idate)
    iend=idate.strftime('%Y-%m-%d')

    if graph:
        colname=col
        titletxt="行业板块/指数分析：最新业绩排名"
        import datetime; today=datetime.date.today()
        footnote0='夏普比率(基于'+ectranslate(base_return)+') -->\n\n'
        footnote1='申万行业/指数分类，'+iend+'快照'
        footnote2='观察期：'+istart+'至'+iend+'，'
        footnote3="数据来源: 申万宏源, "+str(today)+'统计'
        footnote=footnote0+footnote1+'\n'+footnote2+footnote3
        if not px:
            footnote=footnote0+footnote1+'\n'+footnote2+footnote3
            plot_barh(dftail3,colname,titletxt,footnote,axisamp=axisamp)
        else: #使用plotly_express
            titletxt="行业板块/指数业绩排名：夏普比率(基于"+ectranslate(base_return)+')'
            footnote=footnote1+'。'+footnote2+footnote3
            plot_barh2(dftail3,colname,titletxt,footnote)

    return dftail3

    
#==============================================================================
if __name__=='__main__':
    industry='850831.SW'
    industry='801193.SW'
    industry='851811.SW'
    industry='801181.SW'
    industry='801841.SW'
    
    top=5
    df=industry_stock_sw(industry)

def industry_stock_sw(industry='801270.SW',top=5,printout=False):
    """
    功能：获取申万行业指数的成分股
    排序：按照权重从大到小，重仓优先
    """
    industry=industry.split('.')[0]
    
    # 检查行业代码的合理性
    inddf=industry_sw_list()
    ilist=list(inddf['code'])
    if not (industry in ilist):
        if not industry.isdigit():
            print("  #Warning(industry_stock_sw): industry code not found for",industry)
            return None,None
    
    import akshare as ak
    try:
        cdf = ak.index_component_sw(industry)
    except:
        print("  #Warning(industry_stock_sw): failed to retrieve component for index",industry)
        print("  Try solution: upgrade akshare, restart jupyter and try again")
        return None,None

    #去重，保留最新日期的记录
    cdf.sort_values(by=['证券代码','计入日期'],ascending=[True,False],inplace=True)
    cdf.drop_duplicates(subset=['证券代码'],keep='first',inplace=True)
    
    # 删除'证券名称'为None的行
    cdf=cdf.mask(cdf.eq('None')).dropna()
    cdf_total=len(cdf)

    #排名
    cdf.sort_values(by='最新权重',ascending=False,inplace=True)    
    cdf.reset_index(drop=True,inplace=True)
    cdf['序号']=cdf.index+1
    
    if top > 0:
        cdf1=cdf.head(top)
    else:
        cdf1=cdf.tail(-top)
    cdf1['最新权重']=cdf1['最新权重'].apply(lambda x: round(x,2))
    cdf1['证券代码']=cdf1['证券代码'].apply(lambda x: x+'.SS' if x[:1] in ['6'] else (x+'.SZ' if x[:1] in ['0','3'] else x+'.BJ' ))
        
    clist=list(cdf1['证券代码'])
    """
    clist1=[]
    for c in clist:
        first=c[:1]
        if first == '6':
            clist1=clist1+[c+'.SS']
        else:
            clist1=clist1+[c+'.SZ']
    """
    if printout:
        if '.SW' not in industry:
            industry=industry+'.SW'
        titletxt="申万指数成分证券："+industry_sw_name(industry)+'('+industry+')'
        import datetime as dt; todaydt=str(dt.date.today())
        footnote="成分证券数量："+str(cdf_total)+"，申万宏源，"+str(todaydt)
        
        #df_directprint(cdf1,title_txt,footnote)
        df_display_CSS(cdf1,titletxt=titletxt,footnote=footnote,facecolor='papayawhip',decimals=3, \
                           first_col_align='center',second_col_align='left', \
                           last_col_align='left',other_col_align='right', \
                           titile_font_size='16px',heading_font_size='15px', \
                           data_font_size='15px')     
    
    #return clist1,cdf1
    return clist,cdf1
    
if __name__=='__main__':
    clist,cdf=industry_stock_sw(industry='801005',top=10)
    clist,cdf=industry_stock_sw(industry='850831',top=-10)
#==============================================================================

def get_industry_data_sw(start,end,sw_level='1'):
    """
    功能：获得申万行业历史数据, 套壳函数
    start: 开始日期
    end: 结束日期
    sw_level: '1', '2', '3', 'F', 'S', 'B', 'C'
    
    返回：idf, idfall，供进一步分析使用。
    """
    itype_list=['1','2','3','F','S', 'B', 'C']
    sw_level_list=['1','2','3','F','S', 'B', 'C']
    pos=sw_level_list.index(sw_level)
    itype=itype_list[pos]

    idf,idfall=get_industry_info_sw(start=start,end=end,itype=itype)
    
    return idf,idfall
    

if __name__ =="__main__":
    
    # 新冠疫情三年
    start='2023-1-1'; end='2023-4-10'
    itype='F'
    
    idf,idfall=get_industry_info_sw(start,end,itype='1')

def get_industry_info_sw(start,end,itype='1'):
    """
    功能：获得申万行业历史数据
    start: 开始日期
    end: 结束日期
    
    返回：idf, idfall，供进一步分析使用。
    """
    
    # 检查日期期间的合理性
    result,startpd,endpd=check_period(start,end)
    if not result:
        print("  #Error(get_industry_info_sw): invalid date period from",start,'to',end)
        return None,None
    
    print("This may need great great time depending on network/computer speed, take a break ...")
    print("\n*** Step 1:")
    # 获取行业历史数据，本步骤所需时间较长
    df=get_industry_sw(itype=itype)
    found=df_have_data(df)
    if not found=='Found':
        print("  #Warning(compare_mindustry_sw): data tentatively unavailable for group",itype)
        print("  Data is sometimes unavialble at certain time points, try again later")
        return None 
    
    print("\n*** Step 2:")
    # 计算基础数据，本步骤所需时间较长
    idf,idfall=calc_industry_sw(df,start,end)
    
    return idf,idfall    

#==============================================================================
if __name__ =="__main__":
    
    # 新冠疫情三年
    industry_list=['850831','801785','801737','801194','801784','801783','801782']
    start='2023-1-1'; end='2023-4-3'

def get_industry_info_sw2(industry_list,start,end):
    """
    功能：获得申万行业历史数据
    start: 开始日期
    end: 结束日期
    特点：指定行业，可以混合各种指数
    
    返回：idf, idfall，供进一步分析使用。
    """
    
    # 检查日期期间的合理性
    result,startpd,endpd=check_period(start,end)
    if not result:
        print("  #Error(get_industry_info_sw2): invalid date period from",start,'to',end)
        return None,None
    
    print("This may need great time depending on network/computer speed, take a break ...")
    print("\n*** Step 1:")
    # 获取行业历史数据，本步骤所需时间较长
    df=get_industry_sw2(industry_list)
    found=df_have_data(df)
    if not found=='Found':
        print("  #Warning(compare_mindustry_sw): data tentatively unavailable for",industry_list)
        print("  Data is sometimes unavialble at certain time points, try again later")
        return None 
    
    print("\n*** Step 2:")
    # 计算基础数据，本步骤所需时间较长
    idf,idfall=calc_industry_sw(df,start,end)
    
    return idf,idfall    

#==============================================================================
if __name__ =="__main__":
    start='2022-1-1'
    end='2022-12-20'
    tickers=['600600.SS','600132.SS','000729.SZ','002461.SZ','600573.SS']
    measures=['Exp Ret%']    
    market_index='000001.SS'
    window=252
    colalign='right'
    
    rs=rank_msecurity_performance(tickers,start,end,measures=['Exp Ret%'])

def rank_msecurity_performance(tickers,start,end, \
                            measures=['Exp Ret%'], \
                            market_index='000001.SS',window=252,colalign='right', \
                            facecolor='papayawhip',font_size='16px'):
    """
    功能：列示多只股票多个指标的对比，从高到低
    
    """
    print("Searching for multiple security information, please wait ......") 
    #屏蔽函数内print信息输出的类
    import os, sys
    class HiddenPrints:
        def __enter__(self):
            self._original_stdout = sys.stdout
            sys.stdout = open(os.devnull, 'w')

        def __exit__(self, exc_type, exc_val, exc_tb):
            sys.stdout.close()
            sys.stdout = self._original_stdout

    rar_list=['treynor','sharpe','sortino','alpha']
    rar_list_e=['Treynor Ratio','Sharpe Ratio','Sortino Ratio','Jensen alpha']
    rar_list_c=['特雷诺比率','夏普比率','索替诺比率','阿尔法值']

    import pandas as pd
    df=pd.DataFrame()
    allmeasures=measures+rar_list
    for m in allmeasures:
        # 显示进度条
        print_progress_percent2(m,allmeasures,steps=len(allmeasures),leading_blanks=4)
        
        if not (m in rar_list):
            with HiddenPrints():
                dft=compare_msecurity(tickers,measure=m,start=start,end=end,graph=False)
            
            #修改列明为股票名称(股票代码)格式，以便与compare_mrar的结果一致
            dft_new_cols=[]
            for t in tickers:
                c=ticker_name(t)+'('+t+')'
                dft_new_cols=dft_new_cols+[c]
            dft.columns=dft_new_cols
            
            dft['指标']=ectranslate(m)
        else:
            with HiddenPrints():
                dft=compare_mrar(tickers,rar_name=m,start=start,end=end, \
                             market_index=market_index,window=window,graph=False)
            mpos=rar_list.index(m)
            mname=rar_list_c[mpos]
            dft['指标']=mname
        
            del dft['time_weight']
            del dft['relative_weight']
        
        dft1=dft.tail(1)
        cols1=list(dft1)
        cols1.remove('指标')
        for c in cols1:
            dft1[c]=dft1[c].apply(lambda x: round(float(x),4))
            
        if len(df) == 0:
            df=dft1
        else:
            df=pd.concat([df,dft1])
            
    df.set_index('指标',inplace=True)
    df1=df.T
    cols=list(df1)
    
    # 横向指标求和，作为排序依据
    #df1['value']=df1.loc[:,cols].apply(lambda x: x.sum(),axis=1)
    df1.sort_values('夏普比率',ascending=False,inplace=True)
    #del df1['value']
    
    df1.reset_index(inplace=True)
    df1.rename(columns={'index':'股票'},inplace=True)
    
    """
    alignlist=['left']+[colalign]*(len(allmeasures)-1)
    
    print("\n*** 股票多重指标比较：按夏普比率降序排列\n")
    print(df1.to_markdown(index=False,tablefmt='plain',colalign=alignlist))
    
    print("\n*** 观察期：",start,'至',end,'\b，表中数据为',end+'快照')
    print("    表中的夏普比率/索替诺比率/阿尔法值均为TTM滚动值")
    import datetime; today=datetime.date.today()
    print("    数据来源：新浪财经/东方财富，"+str(today)+'统计')
    """
    titletxt="股票多重指标分析：按夏普比率降序排列"
    footnote1="观察期："+start+'至'+end+'，表中数据为'+end+'快照'
    footnote2="表中的夏普比率/索替诺比率/阿尔法值均为TTM滚动值"
    import datetime; todaydt=datetime.date.today()
    footnote3="数据来源：新浪财经/东方财富，"+str(todaydt)+'统计'
    footnote=footnote1+'\n'+footnote2+'n'+footnote3
    
    #确定表格字体大小
    titile_font_size=font_size
    heading_font_size=data_font_size=str(int(font_size.replace('px',''))-1)+'px'
    
    df_display_CSS(fsdf6,titletxt=titletxt,footnote=footnote,facecolor=facecolor, \
                   titile_font_size=titile_font_size,heading_font_size=heading_font_size, \
                       data_font_size=data_font_size)
    
    
    return df1
#==============================================================================
#==============================================================================
if __name__=='__main__':
    tickers=['801160','801120','801170','801710','801890','801040','801130','801180','801720','801970']
    start='2022-1-1'
    end='2023-3-22'
    info_type='Close'
    
    df=get_industry_sw('1')
    df=industry_correlation_sw(df,tickers,start,end,info_type='Close')

def cm2inch(x,y):
    return x/2.54,y/2.54

def industry_correlation_sw(df,tickers,start,end, \
                            info_type='Close',corr_size=6,star_size=5):
    """
    功能：股票/指数收盘价之间的相关性
    info_type='Close': 默认Close, 还可为Open/High/Low/Volume
    """
    # 检查行业个数
    if not isinstance(tickers,list) or len(tickers) < 2:
        print("  #Error(industry_correlation_sw): number of industries too few",tickers)
        return None
    
    # 检查信息类型
    info_types=['Close','Open','High','Low','Volume']
    info_types_cn=['收盘价','开盘价','最高价','最低价','成交量']
    if not(info_type in info_types):
        print("  #Error(industry_correlation_sw): invalid information type",info_type)
        print("  Supported information type:",info_types)
        return None
    pos=info_types.index(info_type)
    info_type_cn=info_types_cn[pos]
    
    # 检查日期
    result,startdt,enddt=check_period(start,end)
    if not result: 
        print("  #Error(industry_correlation_sw): invalid period",start,end)
        return None
    
    # 合成行业行情信息
    print("  Consolidating industry performance, please wait ...")
    import pandas as pd
    
    """
    tickercodes=industry_sw_codes(tickers)
    if tickercodes is None:
        tickercodes=tickers
    """
    
    dfs=None
    for ind in tickers:
        dft=df[df['ticker']==ind]
        if dft is None: 
            print("  #Warning(industry_correlation_sw): unknown industry code",ind)
            continue
    
        dft2=dft[(dft.index >= startdt) & (dft.index <= enddt)]
        dft3=pd.DataFrame(dft2[info_type])
        dft3.rename(columns={info_type:industry_sw_name(ind)},inplace=True)
        
        if dfs is None:
            dfs=dft3
        else:
            dfs=pd.merge(dfs,dft3,how='inner',left_index=True,right_index=True)
    dfs.dropna(axis=0,inplace=True)

    df_coor = dfs.corr()

    print("  Preparing cross-industry correlations, please wait ...")
    # here put the import lib
    import seaborn as sns
    sns.set(font='SimHei')  # 解决Seaborn中文显示问题

    #fig = plt.figure(figsize=(cm2inch(12,8)))
    fig = plt.figure(figsize=(12.8,6.4))
    ax1 = plt.gca()
    
    #构造mask，去除重复数据显示
    import numpy as np
    mask = np.zeros_like(df_coor)
    mask[np.triu_indices_from(mask)] = True
    mask2 = mask
    mask = (np.flipud(mask)-1)*(-1)
    mask = np.rot90(mask,k = -1)
    
    im1 = sns.heatmap(df_coor,annot=True,cmap="YlGnBu"
                        , mask=mask#构造mask，去除重复数据显示
                        ,vmax=1,vmin=-1
                        , fmt='.2f',ax = ax1,annot_kws={"size":corr_size})
    
    ax1.tick_params(axis = 'both', length=0)
    
    #计算相关性显著性并显示
    from scipy.stats import pearsonr
    rlist = []
    plist = []
    for i in dfs.columns.values:
        for j in dfs.columns.values:
            r,p = pearsonr(dfs[i],dfs[j])
            try:
                rlist.append(r)
                plist.append(p)
            except:
                rlist._append(r)
                plist._append(p)
    
    rarr = np.asarray(rlist).reshape(len(dfs.columns.values),len(dfs.columns.values))
    parr = np.asarray(plist).reshape(len(dfs.columns.values),len(dfs.columns.values))
    xlist = ax1.get_xticks()
    ylist = ax1.get_yticks()
    
    widthx = 0
    widthy = -0.15
    
    # 星号的大小
    font_dict={'size':star_size}
    
    for m in ax1.get_xticks():
        for n in ax1.get_yticks():
            pv = (parr[int(m),int(n)])
            rv = (rarr[int(m),int(n)])
            if mask2[int(m),int(n)]<1.:
                #if abs(rv) > 0.5:
                if rv > 0.3:
                    if  pv< 0.05 and pv>= 0.01:
                        ax1.text(n+widthx,m+widthy,'*',ha = 'center',color = 'white',fontdict=font_dict)
                    if  pv< 0.01 and pv>= 0.001:
                        ax1.text(n+widthx,m+widthy,'**',ha = 'center',color = 'white',fontdict=font_dict)
                    if  pv< 0.001:
                        #print([int(m),int(n)])
                        ax1.text(n+widthx,m+widthy,'***',ha = 'center',color = 'white',fontdict=font_dict)
                else: 
                    if  pv< 0.05 and pv>= 0.01:
                        ax1.text(n+widthx,m+widthy,'*',ha = 'center',color = 'k',fontdict=font_dict)
                    elif  pv< 0.01 and pv>= 0.001:
                        ax1.text(n+widthx,m+widthy,'**',ha = 'center',color = 'k',fontdict=font_dict)
                    elif  pv< 0.001:
                        ax1.text(n+widthx,m+widthy,'***',ha = 'center',color = 'k',fontdict=font_dict)
    
    plt.title("行业板块/指数"+info_type_cn+"之间的相关性")
    plt.tick_params(labelsize=corr_size)
    
    footnote1="\n显著性数值：***非常显著(<0.001)，**很显著(<0.01)，*显著(<0.05)，其余为不显著"
    footnote2="\n系数绝对值：>=0.8极强相关，0.6-0.8强相关，0.4-0.6相关，0.2-0.4弱相关，否则为极弱(不)相关"

    footnote3="\n观察期间: "+start+'至'+end
    import datetime as dt; stoday=dt.date.today()    
    footnote4="；来源：Sina/EM，"+str(stoday)+"；基于申万行业/指数分类"
    
    fontxlabel={'size':corr_size}
    plt.xlabel(footnote1+footnote2+footnote3+footnote4,fontxlabel)
    
    plt.gca().set_facecolor('whitesmoke')
    plt.show()
    
    return df_coor

#==============================================================================
#==============================================================================
if __name__=='__main__':
    industries=['煤炭','医药生物','801750']
    top=10
    printout=True

def mixed_industry_stocks(industries=['煤炭','医药生物'],top=10,printout=True, \
                          facecolor='papayawhip',font_size='16px'):
    """
    功能：将不同行业指数(industries)中的前top个(按指数内权重降序)成分股合成为字典，等权重
    """
    
    # 将行业列表转换为行业代码列表
    industries1=[]
    for i in industries:
        if i.isdigit():
            industries1=industries1+[i]
        else:
            industries1=industries1+[industry_sw_code(i)]
            
    # 抓取行业内成分股。合并
    import pandas as pd
    df=pd.DataFrame()
    for i in industries1:
        _,dft=industry_stock_sw(industry=i,top=top,printout=False)
        dft['行业代码']=i
        dft['行业名称']=industry_sw_name(i)
        
        if len(df)==0:
            df=dft
        else:
            df=pd.concat([df,dft])
            
    # 去掉重复的股票（假设可能有一只股票被计入多个指数）
    df.drop_duplicates(subset=['证券代码'], keep='first', inplace=True)
    df['初始权重']=round(1.0 / len(df),4)
    df.reset_index(drop=True,inplace=True)
    df['序号']=df.index+1
    
    df_print=df[['序号','证券名称','证券代码','初始权重','行业名称','行业代码']]
    
    if printout:
        #alignlist=['center']+['center']*(len(list(df_print))-1)
        
        if len(industries) > 1:
            #print("\n*** 混合行业投资组合的成分股：初始等权重\n")
            titletxt="多行业投资组合的成分股：初始等权重"
        else:
            #print("\n*** 单一行业投资组合的成分股：初始等权重\n")
            titletxt="单一行业投资组合的成分股：初始等权重"
            
        #print(df_print.to_markdown(index=False,tablefmt='plain',colalign=alignlist))
        import datetime; todaydt=datetime.date.today()
        #print("\n*** 数据来源：申万宏源，统计日期："+str(today))
        footnote="数据来源：申万宏源，统计日期："+str(todaydt)
    
        #确定表格字体大小
        titile_font_size=font_size
        heading_font_size=data_font_size=str(int(font_size.replace('px',''))-1)+'px'
        
        df_display_CSS(df_print,titletxt=titletxt,footnote=footnote,facecolor=facecolor, \
                       titile_font_size=titile_font_size,heading_font_size=heading_font_size, \
                           data_font_size=data_font_size)
    
    # 生成成分股字典
    stock_dict=df.set_index(['证券代码'])['初始权重'].to_dict()

    #return stock_dict
    return list(stock_dict)    
#==============================================================================
if __name__=='__main__':
    industry='房地产开发'
    industry='证券Ⅱ'
    top=5
    sw_level='2'
    
    
def find_peers_china(industry='',top=20,rank=20,sw_level='2'):
    """
    ===========================================================================
    功能：找出一个申万行业的上市公司排名
    主要参数：
    industry：申万行业名称。当industry = ''，显示的内容由sw_level控制。申万二级行业分类
    sw_level：申万一级行业'1'，二级行业'2'，三级行业'3'，其他'F'、'S'、'B'、'C'
    top：排名数量，为正数时表示前多少名，可为负数（代表倒数多少名）
    
    示例：
    stocks2=find_peers_china('通信工程及服务',top=10)
    """
    
    # 避免混淆
    if top < rank:
        rank=top
    
    # 默认情形处理
    if industry == '':
        itype_list=['1','2','3','F','S','B','C']
        sw_level_list=['1','2','3','F','S','B','C']
        pos=sw_level_list.index(sw_level)
        itype=itype_list[pos]
        
        print_industry_sw(itype=itype,numberPerLine=4,colalign='left')
        return None
    
    if industry != '':
        if not isinstance(industry,str):
            print("  #Error(find_peers_china): expecting an industry code or name for",industry)
            return None
        
        # 申万行业代码
        industry=industry.split('.')[0]
        if industry.isdigit():
            #industry=industry.split('.')[0]
            iname=industry_sw_name(industry)
            if iname is None:
                print("  #Warning(find_peers_china): Shenwan industry code not found for",industry)
                return None
            
            swlist,_=industry_stock_sw(industry=industry,top=rank,printout=True)
        else:
            icode=industry_sw_code(industry)
            if icode is None:
                industry_df=industry_sw_list()
                industry_name_list=list(industry_df['name'])
                industry_code_list=list(industry_df['code'])
                possible_industry_list=[]
                for ind in industry_name_list:
                    if industry in ind:
                        pos=industry_name_list.index(ind)
                        ind_code=industry_code_list[pos]+'.SW'
                        possible_industry_list=possible_industry_list+[ind+'('+ind_code+')']
                
                print("  #Warning(find_peers_china): Shenwan industry name not found for",industry)
                if len(possible_industry_list) >0:
                    print("  Do you mean the following Shenwan industry names?")
                    #print_list(possible_industry_list,leading_blanks=2)
                    printlist(possible_industry_list,numperline=5,beforehand='  ',separator=' ')
                else:
                    print("  Sorry, no similiar Shenwan industry name containing ",industry)
                
                return None
            else:
                swlist,_=industry_stock_sw(industry=icode,top=rank,printout=True)
        
        if not (swlist is None):
            tickerlist=swlist[:top]
            return tickerlist
        else:
            print("  #Warning(find_peers_china): failed in retrieving component stocks for Shenwan industry",industry)
            print("  Possible solution: upgrade akshare. if still fail, report to the author of siat for help")
            return []
        
#==============================================================================
# 申万行业指数历史行情
#==============================================================================
if __name__ =="__main__":
    ticker='859821'
    ticker='859821.SW'
    
    start='2023-1-1'
    end='2023-2-1'
    
    df=get_sw_index(ticker,start,end)

def get_sw_index(ticker,start,end):
    """
    功能：抓取单个申万行业指数历史行情
    ticker：申万行业指数以8x开始，容易与北交所股票代码混淆。建议带有后缀.SW
    """
    
    # 判断是否申万行业指数代码
    ticker=ticker.upper()
    ticker_split=ticker.split('.')
    """
    if not (len(ticker_split)==2 and ticker_split[1]=='SW'):
        return None
    else:
        symbol=ticker_split[0]
    """
    symbol=ticker_split[0]
    if len(ticker_split) == 2:
        if ticker_split[1] != 'SW':
            return None
    else:
        return None
    
    
    # 判断日期
    result,startts,endts=check_period(start,end)
    if not result:
        print("  #Error(get_sw_index): invalid date(s) in or period between",start,'and',end)
        return None
    
    import akshare as ak
    import pandas as pd
    
    try:
        dft = ak.index_hist_sw(symbol=symbol,period="day")
    except:
        try:
            dft = ak.index_hist_fund_sw(symbol=symbol,period="day")
            dft['代码']=symbol
            dft['收盘']=dft['收盘指数']
            dft['开盘']=dft['收盘指数']
            dft['最高']=dft['收盘指数']
            dft['最低']=dft['收盘指数']
            dft['成交量']=0; dft['成交额']=0
        except:        
            print("  #Error(get_sw_index): failed to retrieve index",symbol)
            return None
        
    dft['ticker']=dft['代码'].apply(lambda x: x+'.SW')
    
    dft['name']=dft['代码'].apply(lambda x:industry_sw_name(x)) 
    
    dft['date']=dft['日期'].apply(lambda x: pd.to_datetime(x))
    dft.set_index('date',inplace=True)
    dft['Close']=dft['收盘']
    dft['Adj Close']=dft['Close']
    dft['Open']=dft['开盘']
    dft['High']=dft['最高']
    dft['Low']=dft['最低']
    
    yi=100000000    #亿
    dft['Volume']=dft['成交量']*yi    #原始数据为亿股
    dft['Amount']=dft['成交额']*yi    #原始数据为亿元
    
    colList=['ticker','Close','Adj Close','Open','High','Low','Volume','Amount','name']
    dft2=dft[colList]
    dft3=dft2[(dft2.index >= startts)] 
    dft4=dft3[(dft3.index <= endts)] 
    dft4.sort_index(inplace=True)
    
    df=dft4
    
    return df

#==============================================================================
if __name__ =="__main__":
    tickers=['859821.SW','859822.Sw','600519.SS']
    
    start='2023-1-1'
    end='2023-2-1'
    
    df=get_sw_indexes(tickers,start,end)

def get_sw_indexes(tickers,start,end):
    """
    功能：抓取多个申万行业指数历史行情
    tickers：申万行业指数列表，要求带有后缀.SW
    """
    
    # 判断日期
    result,startts,endts=check_period(start,end)
    if not result:
        print("  #Error(get_sw_indexes): invalid date(s) in or period between",start,'and',end)
        return None
    
    #检查是否为多个指数:空的列表
    if isinstance(tickers,list) and len(tickers) == 0:
        pass
        return None        
    
    #检查是否为多个指数:单个指数代码
    if isinstance(tickers,str):
        tickers=[tickers]

    # 过滤申万行业指数代码
    tickers_sw=[]
    for t in tickers:
        t=t.upper()
        t_split=t.split('.')
        if not (len(t_split)==2 and t_split[1]=='SW'):
            continue
        else:
            tickers_sw=tickers_sw+[t]
        
    
    #检查是否为多个指数:列表中只有一个代码
    if isinstance(tickers_sw,list) and len(tickers_sw) == 1:
        ticker1=tickers_sw[0]
        df=get_sw_index(ticker1,startts,endts)
        return df       
    
    import pandas as pd
    #处理列表中的第一个指数
    i=0
    df=None
    while df is None:
        t=tickers_sw[i]
        df=get_sw_index(t,startts,endts)
        if not (df is None):
            columns=create_tuple_for_columns(df,t)
            df.columns=pd.MultiIndex.from_tuples(columns)
        else:
            i=i+1
    if (i+1) == len(tickers_sw):
        #已经到达指数代码列表末尾
        return df
        
    #处理列表中的其余指数
    for t in tickers_sw[(i+1):]:
        dft=get_sw_index(t,startts,endts)
        if not (dft is None):
            columns=create_tuple_for_columns(dft,t)
            dft.columns=pd.MultiIndex.from_tuples(columns)
        
        df=pd.merge(df,dft,how='inner',left_index=True,right_index=True)
     
    return df
    
#==============================================================================
if __name__ =="__main__":
    sw_level='F'
    sw_level='2'
    indicator='Exp Ret%'
    start='MRY'
    end='default'
    printout='smart'


def industry_scan_china(sw_level='F', \
                        indicator='Exp Adj Ret%', \
                        base_return='Exp Adj Ret%', \
                        start='MRY',end='default', \
                        RF=0, \
                        printout='smart', \
                        facecolor='papayawhip',font_size='16px'):
    """
    ===========================================================================
    功能：扫描申万行业指数，按照投资收益率排名。对网速要求高，可能需要较长时间。
    主要参数：
    sw_level：申万行业分类，默认'F'。
        F--市场表征（默认），S--投资风格（策略），B--大类风格，C--金创，
        1--一级行业，2--二级行业，3--三级行业
    indicator：行业排名使用的指标，默认'Exp Adj Ret%'，可使用RAR指标等
    start与end：评估期间。允许MRM/MRQ/MRY（默认）/YTD/L3Y(近三年)/L5Y(近五年)
    base_return：计算sharpe和sortino比率时使用的收益率类型，默认'Exp Adj Ret%'。
        当indicator不是sharpe或sortino比率时，base_return需要与indicator保持一致。
    RF：年化无风险收益率，默认0，可参照一年期国债收益率(Government Bond Yield)
    printout：筛选方式。
        smart--收益前10名与后10名（默认），winner--仅限收益为正的行业，
        loser--仅限收益为负的行业，50--收益前50名，-10--收益后10名，all--所有行业
    facecolor：背景颜色，默认'papayawhip'
    font_size：输出表格的字体大小，默认'16px'
    
    示例：
    info=industry_scan_china(sw_level='3',indicator='sharpe',start='MRY')
    """
    #indicator='Exp Ret%'
    
    #print("  Evaluating industry performance, it may take up to hours ... ...")

    #节省获取数据的量和时间
    if start=='MRY' and end=='default': #默认参数
        if 'Weekly' in indicator or 'Weekly' in base_return:
            start='MRM'
        if 'Monthly' in indicator or 'Monthly' in base_return:
            start='MRQ'
    
    # 检查申万行业
    sw_level_list=['1','2','3','F','S','B','C','J1','J2','J3','JF']
    if sw_level not in sw_level_list:
        print("  #Warning(industry_scan_china): invalid Shenwan industry types for",sw_level)
        print("  Valid Shenwan industry types:",end='')
        print_list(sw_level_list)
        return None

    # 检查支持的指标
    base_return_list=['Exp Ret%','Exp Ret Volatility%','Exp Ret LPSD%', \
                    'Exp Adj Ret%','Exp Adj Ret Volatility%','Exp Adj Ret LPSD%', \
                        
                    'Annual Ret%','Annual Ret Volatility%','Annual Ret LPSD%', \
                    'Annual Adj Ret%','Annual Adj Ret Volatility%','Annual Adj Ret LPSD%', \
                        
                    'Quarterly Ret%','Quarterly Ret Volatility%','Quarterly Ret LPSD%', \
                    'Quarterly Adj Ret%','Quarterly Adj Ret Volatility%','Quarterly Adj Ret LPSD%', \
                        
                    'Monthly Ret%','Monthly Ret Volatility%','Monthly Ret LPSD%', \
                    'Monthly Adj Ret%','Monthly Adj Ret Volatility%','Monthly Adj Ret LPSD%', \
                        
                    'Weekly Ret%','Weekly Ret Volatility%','Weekly Ret LPSD%', \
                    'Weekly Adj Ret%','Weekly Adj Ret Volatility%','Weekly Adj Ret LPSD%', \
                    ]
    if base_return not in base_return_list:
        print("  #Warning(industry_scan_china): unsupported base return type for",base_return)
        print("  Supported base return:")
        printlist(base_return_list,numperline=5,beforehand='  ',separator=', ')
        return None
    
        
    indicator_list=base_return_list + ['sharpe','sortino']
    
    if indicator.lower() in ['sharpe','sortino']:
        indicator=indicator.lower()

    if indicator not in indicator_list:
        print("  #Warning(industry_scan_china): unsupported indicator for",indicator)
        print("  Supported indicators:")
        printlist(indicator_list,numperline=5,beforehand='  ',separator=', ')
        return None
    
    # 检查日期：
    fromdate,todate=start_end_preprocess(start,end)
    import datetime as dt; todaydt=dt.date.today().strftime('%Y-%m-%d')
    """
    #截至日期
    import datetime as dt; todaydt=dt.date.today().strftime('%Y-%m-%d')
    end=end.lower()
    if end in ['default','today']:
        todate=todaydt
    else:
        validdate,todate=check_date2(end)
        if not validdate:
            print("  #Warning(industry_scan_china): invalid date for",end)
            todate=todaydt
    # 检查日期：开始日期
    start=start.lower()
    if start in ['default','mrm']:  # 默认近一个月
        fromdate=date_adjust(todate,adjust=-31)
    elif start in ['mrq']:  # 近三个月
        fromdate=date_adjust(todate,adjust=-63)   
    elif start in ['mry']:  # 近一年
        fromdate=date_adjust(todate,adjust=-366)   
    elif start in ['ytd']:  # 今年以来
        fromdate=str(today.year)+'-1-1'   
    elif start in ['lty']:  # 近三年以来
        fromdate=date_adjust(todate,adjust=-366*3)  
    elif start in ['lfy']:  # 近五年以来
        fromdate=date_adjust(todate,adjust=-366*5)          
    else:
        validdate,fromdate=check_date2(start)
        if not validdate:
            print("  #Warning(industry_scan_china): invalid date for",start,"/b, set to MRM")
            fromdate=date_adjust(todate,adjust=-31)      
    """
    # 获取申万行业类别内部标识
    #itype_list=['1','2','3','F','S','B','C']
    itype_list=sw_level_list
    pos=sw_level_list.index(sw_level)
    itype=itype_list[pos]
    
    #df1=industry_sw_list()
    #df2=dft[dft['type']==itype]      
    
    
    # 循环获取行业指数，简单计算指数增长率，排序
    #print("  Retrieving industry info, which may need up to hours, take a break ...")
    #print("\n  *** Step 1: Retrieving industry information")
    print("  *** Step 1: ")
    # 获取行业历史数据，本步骤所需时间较长
    df=get_industry_sw(itype=itype)    
    found=df_have_data(df)
    if not found=='Found':
        print("  #Warning(compare_mindustry_sw): data tentatively unavailable for group",itype)
        print("  Data is sometimes unavialble at certain time points, try again later")
        return None 
    
    # 计算指标
    #print("\n  *** Step 2: Computing performance indicators")
    print("\n  *** Step 2: ")
    # 计算基础数据，本步骤所需时间较长
    idf,idfall=calc_industry_sw(df,fromdate,todate)  
    
    #设置base_return：非['sharpe','sortino']时
    if not indicator in ['sharpe','sortino']:
        #以下的判断顺序不可轻易改变
        if 'Ret Volatility%' in indicator:
            base_return=indicator.replace('Ret Volatility%','Ret%')
        elif 'Ret Volatility' in indicator:
            base_return=indicator.replace('Ret Volatility','Ret')
        elif 'Ret LPSD%' in indicator:
            base_return=indicator.replace('Ret LPSD%','Ret%')
        elif 'Ret LPSD' in indicator:
            base_return=indicator.replace('Ret LPSD','Ret')
        else:
            base_return=indicator
            
            
    #计算期间内的无风险收益率：RF为小数，而idf中的收益率为百分数
    if '%' in base_return:
        RFS=RF*100 #百分数
        
        base_return_volatility=base_return.replace('Ret%','Ret Volatility%')
        base_return_lpsd=base_return.replace('Ret%','Ret LPSD%')
    else:
        RFS=RF
        
        base_return_volatility=base_return.replace('Ret','Ret Volatility')
        base_return_lpsd=base_return.replace('Ret','Ret LPSD')
        
    if 'Exp' in base_return:
        RF_daily=RFS/365
        RF_days=RF_daily * calculate_days(fromdate, todate)

    elif 'Annual' in base_return:
        RF_days=RFS
        
    elif 'Quarterly' in base_return:
        RF_days=RFS/4
        
    elif 'Monthly' in base_return:
        RF_days=RFS/12 
        
    elif 'Weekly' in base_return:
        RF_days=RFS/52        
        
    idf['sharpe']=(idf[base_return]-RF_days) / idf[base_return_volatility]
    idf['sortino']=(idf[base_return]-RF_days) / idf[base_return_lpsd]
        
    
    # 排序
    idf.sort_values(indicator,ascending=False,inplace=True)
    idf.reset_index(inplace=True)
    idf.index=idf.index+1
    
    idf['Industry Name']=idf['ticker'].apply(lambda x: industry_sw_name(x))
    idf['Industry Code']=idf['ticker'].apply(lambda x: x+'.SW')
    
    indicator_list1=indicator_list
    indicator_list1.remove(indicator)
    collist=['Industry Code','Industry Name',indicator]+indicator_list1
    df2=idf[collist]
    
    # 修改比率的小数位数
    for i in indicator_list:
        df2[i]=df2[i].apply(lambda x: round(x,2))
    
    # 筛选
    import pandas as pd
    #'smart':默认
    num=len(df2)
    if num > 20:
        df_high=df2.head(10)
        df_low=df2.tail(10)
        df_prt=pd.concat([df_high,df_low])
    else:
        df_prt=df2
    
    if printout=='all':
        df_prt=df2
    elif printout=='winner':
        df_prt=df2[df2[indicator] > 0]
    elif printout=='loser':
        df_prt=df2[df2[indicator] <= 0]    
    else:
        try:
            printoutd=int(printout)
            if printoutd>0:
                df_prt=df2.head(printoutd)
            else:
                df_prt=df2.tail(-printoutd)
        except: # 假定为smart
            pass
    
    # 标题改中文
    df_prt.rename(columns={'Industry Code':'代码','Industry Name':'名称', \
                           base_return:ectranslate(base_return), \
                           base_return_volatility:ectranslate(base_return_volatility), \
                           base_return_lpsd:ectranslate(base_return_lpsd), \
                           'sharpe':'夏普比率','sortino':'索替诺比率'}, \
                  inplace=True)
    
    # 显示
    if sw_level=='F':
        sw_level_txt='申万市场表征指数'
    elif sw_level=='S':
        sw_level_txt='申万投资风格指数'
    elif sw_level=='B':
        sw_level_txt='申万大类风格指数'
    elif sw_level=='C':
        sw_level_txt='申万金创指数'
    elif sw_level=='1':
        sw_level_txt='申万一级行业'
    elif sw_level=='2':
        sw_level_txt='申万二级行业'
    elif sw_level=='3':
        sw_level_txt='申万三级行业'
    elif sw_level=='J1':
        sw_level_txt='申万基金基础一级指数'  
    elif sw_level=='J2':
        sw_level_txt='申万基金基础二级指数'  
    elif sw_level=='J3':
        sw_level_txt='申万基金基础三级指数' 
    elif sw_level=='JF':
        sw_level_txt='申万基金特色指数'         
    else:
        sw_level_txt='未知类别'

    if printout=='all':
        printout_txt='所有指数'
    elif printout=='smart':
        printout_txt='前/后十个行业'
        if len(df2) <=20:
            printout_txt='所有指数'
    elif printout=='winner':
        printout_txt='收益为正者'
    elif printout=='loser':
        printout_txt='收益为负者'
    else:
        try:
            num=int(printout)
            if len(df2) > abs(num):
                if num > 0:
                    printout_txt='收益排名前'+printout+"名"
                else:
                    printout_txt='收益排名后'+str(abs(num))+"名"
            else:
                printout_txt='所有指数'
        except:
            printout_txt='未知筛选方式'
        
    #titletxt="申万行业业绩排行榜："+sw_level_txt+'，共'+str(len(df_prt))+"个指数符合条件"
    #titletxt="行业业绩排行榜："+sw_level_txt+'，'+ectranslate(indicator)+'，筛选方式：'+printout_txt
    titletxt="申万宏源行业/指数业绩龙虎榜："+sw_level_txt+'，'+printout_txt
    #print("\n***",titletxt,'\n')
    """
    alignlist=['center']+['left']*(len(list(df_prt))-1)
    print(df_prt.to_markdown(index=True,tablefmt='plain',colalign=alignlist))  
    """
    #print("\n *** 数据来源：综合申万宏源/东方财富/新浪财经,",todaydt,"\b；分析期间:",fromdate+'至'+todate)
    #footnote1="筛选方式：all-所有，smart-收益最高最低各10个，winner-收益为正，loser-收益为负"
    footnote1="注：夏普/索梯诺比率基于"+ectranslate(base_return)+"，年化无风险利率"+str(round(RF*100,4))+'%'
    footnote2="评估期间："+str(fromdate)+'至'+str(todate)+"，数据来源：申万宏源，"+str(todaydt)+"制表"
    footnote=footnote1+'\n'+footnote2
    #footnote=footnote2
    
    #确定表格字体大小
    titile_font_size=font_size
    heading_font_size=data_font_size=str(int(font_size.replace('px',''))-1)+'px'
    
    df_prt['序号']=df_prt.index
    if indicator=='sharpe':
        df_prt=df_prt[['序号','名称','代码','夏普比率','索替诺比率', \
                       ectranslate(base_return),ectranslate(base_return_volatility),ectranslate(base_return_lpsd)]]  
    elif indicator=='sortino':
        df_prt=df_prt[['序号','名称','代码','索替诺比率','夏普比率', \
                       ectranslate(base_return),ectranslate(base_return_volatility),ectranslate(base_return_lpsd)]]  

    elif 'Volatility' in indicator:
        df_prt=df_prt[['序号','名称','代码',ectranslate(base_return_volatility),ectranslate(base_return_lpsd), \
                       ectranslate(base_return),'夏普比率','索替诺比率']]
    elif 'LPSD' in indicator:
        df_prt=df_prt[['序号','名称','代码',ectranslate(base_return_lpsd),ectranslate(base_return_volatility), \
                       ectranslate(base_return),'夏普比率','索替诺比率']]  
    else:
        df_prt=df_prt[['序号','名称','代码',ectranslate(base_return), \
                       ectranslate(base_return_volatility),ectranslate(base_return_lpsd),'夏普比率','索替诺比率']]  
        
    #显示表格        
    df_display_CSS(df_prt,titletxt=titletxt,footnote=footnote,facecolor=facecolor, \
                   first_col_align='center',second_col_align='left', \
                   last_col_align='center',other_col_align='center', \
                   titile_font_size=titile_font_size,heading_font_size=heading_font_size, \
                   data_font_size=data_font_size)
    
    return df2   
    

#==============================================================================
if __name__=='__main__':
    ticker='600791.SS'
    ticker='东阿阿胶'

    contains_chinese(ticker)
 
def contains_chinese(text):
    """
    功能：判断字符串是否含有汉字
    """
    import re
    return re.search(r'[\u4e00-\u9fff]', text) is not None

#==============================================================================
if __name__=='__main__':
    ticker='600791.SS'
    ticker='689009.SS'
    
    ticker=['600791.SS','东阿阿胶']
    level='1'
    
    find_industry_sw(ticker,level='1')
    
def find_industry_sw(ticker,level='1',ticker_order=True,max_sleep=30):
    """
    ===========================================================================
    功能：寻找一只或一组股票所属的申万行业，支持股票代码和股票名称。
    level='1'：默认只查找申万1级行业；查找2/3级行业时间较久，可能触发反爬虫机制。
    ticker_order=True：默认输出结果按照ticker中的顺序,而非按照所属行业排序。
    max_sleep：为防止触发反爬虫机制，默认每次爬虫后睡眠最多30秒钟。
    
    返回值：查找结果df。
    """
    print("  Searching shenwan industries for securities ... ...")
    
    if isinstance(ticker,str):
        ticker=[ticker]
        
    tickerlist=[]
    for t in ticker:
        if not contains_chinese(t):
            tt=t[:6]
            tickerlist=tickerlist+[tt]
        else:
            tickerlist=tickerlist+[t]
    
    import akshare as ak
    if level == '3':
        df = ak.sw_index_third_info()
    elif level == '2':
        df = ak.sw_index_second_info()
    else:
        df = ak.sw_index_first_info()
    
    df['industry_code']=df['行业代码'].apply(lambda x: x[:6])
    industry_list=list(df['industry_code'])
    
    import pandas as pd; import random; import time
    result=pd.DataFrame(columns=['序号','证券名称','证券代码','行业名称','行业代码'])
    
    for i in industry_list:
        print_progress_percent2(i,industry_list,steps=10,leading_blanks=2)
        
        iname=df[df['industry_code']==i]['行业名称'].values[0]
        
        try:
            cdf = ak.index_component_sw(i)
        except:
            print("  #Warning(find_industry_sw): server banned this ip becos of too many requests") 
            print("  Solution: change to another ip or another computer, or try a few hours later.")
            return 
        """
        component_list=list(cdf['证券代码'])
        
        if ticker6 in component_list:
            stock_name=cdf[cdf["证券代码"]==ticker6]['证券名称'].values[0]
            print("\n\n股票代码："+ticker+"，"+stock_name)
            
            isi=i+'.SI'
            industry_name=df[df['行业代码']==isi]['行业名称'].values[0]
            print("申万"+str(level)+"级行业代码："+i+".SW，"+industry_name)
            
            break
        """
        for t in tickerlist:
            torder=tickerlist.index(t)+1
            
            if not contains_chinese(t):
                dft=cdf[cdf['证券代码']==t]
                if len(dft)==0: continue
                else:
                    tname=cdf[cdf['证券代码']==t]['证券名称'].values[0]
                    s=pd.Series({'序号':torder,'证券名称':tname,'证券代码':t,'行业名称':iname,'行业代码':i})
                    try:
                        result=result.append(s,ignore_index=True)
                    except:
                        result=result._append(s,ignore_index=True)   
            else:
                dft=cdf[cdf['证券名称']==t]
                if len(dft)==0: continue
                else:
                    tcode=cdf[cdf['证券名称']==t]['证券代码'].values[0]
                    s=pd.Series({'序号':torder,'证券名称':t,'证券代码':tcode,'行业名称':iname,'行业代码':i})
                    try:
                        result=result.append(s,ignore_index=True)
                    except:
                        result=result._append(s,ignore_index=True)   
                
        #是否都找到了？
        if len(result) == len(tickerlist): break
        
        #生成随机数睡眠，试图防止被反爬虫，不知是否管用！
        random_int=random.randint(1,max_sleep)
        time.sleep(random_int)
    
    #排序
    if not ticker_order:
        #按行业代码排序
        result.sort_values(by='行业代码',inplace=True)
    else:
        #按ticker顺序排序
        result.sort_values(by='序号',inplace=True)
        """
        if contains_chinese(tickerlist[0]):
            result.sort_values(by='证券名称',key=lambda x: x.map(dict(zip(tickerlist,range(len(tickerlist))))))
        else:
            result.sort_values(by='证券代码',key=lambda x: x.map(dict(zip(tickerlist,range(len(tickerlist))))))
        """
    #result.reset_index(drop=True,inplace=True)
    
    #显示结果
    titletxt="证券所属行业：申万"+str(level)+"级行业"
    import datetime; todaydt = datetime.date.today()
    footnote="数据来源：申万宏源，"+str(todaydt)+"统计"
    """
    collist=list(result)
    result['序号']=result.index+1
    result=result[['序号']+collist]
    """
    print('')
    df_display_CSS(result,titletxt=titletxt,footnote=footnote,facecolor='papayawhip',decimals=2, \
                       first_col_align='center',second_col_align='left', \
                       last_col_align='left',other_col_align='left', \
                       titile_font_size='16px',heading_font_size='15px', \
                       data_font_size='15px')
    
    return result

#==============================================================================
#东方财富板块分类：查找股票所属行业与主要同行
#==============================================================================
if __name__=='__main__':
    ticker='600519.SS'
    indicator="市盈率"
    rank=40
    
    font_size="16px"; facecolor="papayawhip"
    
    peers=stock_industry_peer_em(ticker,indicator="市盈率",rank=10)

def stock_peers_em(ticker='',indicator='市盈率',rank=10, \
                   force_show_stock=True, \
                   font_size="16px",facecolor="papayawhip", \
                   numberPerLine=5):
    """
    ===========================================================================
    功能：基于东方财富行业分类，查找股票所属的行业板块以及主要同行排名。
    特点：行业分类较粗糙，略胜于无。
    主要参数：
    ticker：股票代码，默认''显示所有板块名称。
    indicator：排名指标，默认''。例如："股价"、"流动性"、"市净率"、"市盈率"。
    rank：排名数量，默认10前十名。
    force_show_stock：是否显示股票信息，默认False。
    font_size：表格字体大小，默认"16px"。
    facecolor：输出表格的背景颜色，默认"papayawhip"。
    numberPerLine：输出表格中的每行显示个数，默认5。
    
    注意：若结果异常，可尝试升级插件akshare。
    
    示例：
    industries=stock_peers_em()     # 显示东方财富所有行业板块分类
    # 显示002373.SZ在所属东方财富板块中的股价排名
    peers=stock_peers_em(ticker="002373.SZ",
                     indicator="股价",
                     force_show_stock=True)
    peers=stock_peers_em(ticker="002373.SZ",
                     indicator="流动性",
                     force_show_stock=True)
    """
    if indicator in ["股价","股票价格","价格","收盘价","价位"]:
        indicator="最新价"
    if indicator in ["流动性","热门","活跃"]:
        indicator="换手率"   

    if rank==0:
        rank=5  
        
    import akshare as ak
    
    #股票基本信息
    try:
        info=ak.stock_individual_info_em(symbol=ticker[:6])
    except:
        if not ticker=='':
            print("  #Warning(stock_peer_em): stock info not found for",ticker)
            print("  Solution: if stock code is correct, upgrade akshare and try again")
            
        df_em=ak.stock_board_industry_name_em()
        #df_em.sort_values(by="板块名称",ascending=True,inplace=True)
        #industry_names_em=sorted(list(df_em["板块名称"]),reverse=True)
        industry_names_em=list(df_em["板块名称"])
        print("  List of stock industries in East Money:",len(df_em),end='')
        #printlist(industry_names_em,numperline=7,beforehand='  ')
        printInLine_md(industry_names_em,numberPerLine=numberPerLine,colalign="center")
        return None        
    
    #东方财富板块名称
    hangye=info[info['item']=='行业']['value'].values[0]
    
    #东方财富板块成分股
    cfg=ak.stock_board_industry_cons_em(symbol=hangye)
    
    cfg_col_list=list(cfg)
    indicator_col=''
    for i in cfg_col_list:
        if indicator in i:
            indicator_col=i
            break
        
    if indicator_col=='' or indicator=='':
        if indicator!='':
            print("  #Warning(stock_peer_em): unsupported indicator",indicator)
        
        remove_list=["序号","代码","名称"]
        cfg_col_list_tmp = [x for x in cfg_col_list if x not in remove_list]
        print("  Supported indicators:",)
        print_list(cfg_col_list_tmp,leading_blanks=2)
        return None        
    
    collist=['序号','名称','代码','市盈率-动态','市净率','最新价','涨跌幅','换手率']
    if not indicator_col in collist:
        collist=collist+[indicator_col]
        
    #重新排序
    #cfg.sort_values(by=indicator_col,ascending=False,inplace=True)
    cfg.sort_values(by=[indicator_col]+["代码"],ascending=[False,True],inplace=True)
    cfg.reset_index(drop=True,inplace=True)
    cfg['序号']=cfg.index+1
        
    #行业均值与中位数
    indicator_mean=cfg[indicator_col].mean()
    indicator_median=cfg[indicator_col].median()
    indicator_total=cfg["代码"].count()
    
    indicator_value=cfg[cfg['代码']==ticker[:6]][indicator_col].values[0]
    indicator_seq=cfg[cfg['代码']==ticker[:6]]["序号"].values[0]
    from scipy.stats import percentileofscore
    indicator_pct=percentileofscore(cfg[indicator_col],indicator_value)
    
    #筛选
    if rank > 0:
        rank_flag="前"
        df_disp=cfg[collist].head(rank)
    else:
        rank_flag="后"
        df_disp=cfg[collist].tail(abs(rank))
    
    #强制显示所选股票
    #if force_show_stock and rank != 10:
    if force_show_stock:
        #所选股票是否在其中？
        if not ticker[:6] in list(df_disp["代码"]):
            ticker_seq=cfg[cfg["代码"]==ticker[:6]]["序号"].values[0]
            seq1=ticker_seq-4; seq2=ticker_seq+5
            #如果超出开头
            if seq1 <=0:
                seq1=1; seq2=10
            #如果超出结尾    
            if seq2 > len(cfg):
                seq2=len(cfg); seq1=len(cfg)-9
                
            #注意：此处的&不能换为and    
            df_disp=cfg[(cfg["序号"]>=seq1) & (cfg["序号"]<=seq2)][collist]
    
    #制表
    tname=ticker_name(ticker)
    titletxt="行业板块及其上市公司排名："+hangye+"，"+indicator_col+"("+rank_flag+str(abs(rank))+"名)"
    
    footnote1="全行业的"+indicator_col+"状况：均值"+str(round(indicator_mean,2))+"，中位数"+str(round(indicator_median,2))+"\n"
    footnote2=tname+"的"+indicator_col+"："+str(round(indicator_value,2))+"，行业排名"+str(indicator_seq)+"/"+str(indicator_total)+"，分位"+str(round(indicator_pct,2))+"%\n"
    import datetime; stoday = datetime.date.today()
    footnote3="*** 信息来源：东方财富，"+str(stoday) 
    footnote=footnote1+footnote2+footnote3
    
    #确定表格字体大小
    titile_font_size=font_size
    heading_font_size=data_font_size=str(int(font_size.replace('px',''))-1)+'px'
    
    df_display_CSS(df_disp,titletxt=titletxt,footnote=footnote,facecolor=facecolor, \
                   first_col_align='center',second_col_align='left', \
                   titile_font_size=titile_font_size,heading_font_size=heading_font_size, \
                   data_font_size=data_font_size)
    
    return cfg
    
#==============================================================================
if __name__=='__main__':
    concept='酒'
    concept='股'
    concept='白酒'
    
    ticker="600519.SS"
    indicator="市盈率"
    rank=11
    
    force_show_stock=True
    
    font_size="16px"; facecolor="papayawhip"; numberPerLine=7
    

def concept_stocks_em(concept='',ticker='',indicator="市盈率",rank=10, \
                      force_show_stock=False, \
                      font_size="16px",facecolor="papayawhip",numberPerLine=5):
    """
    ===========================================================================
    功能：基于东方财富概念板块，查找关键字相关概念以及股票业绩。
    特点：概念板块划分细致，同一股票可能分属多个板块，与行业分类不同。
    参数：
    concept：概念板块名称，或名称中的关键字，默认''输出所有概念板块名称；
        若查找到多个名称，则优先输出查找到的名称；
        若仅仅找到一个板块，则按indicator输出该板块的股票排行。
    ticker：股票代码，默认''
    indicator：指标名称，默认"市盈率"，还支持：股价，市净率，涨跌幅，流动性，换手率。
    rank：排名，支持正负数，默认10。
    force_show_stock：若ticker不为空，且不在rank范围内，是否强制显示该股票，默认False。
    font_size：显示字体大小，默认"16px"。
    facecolor：表格背景颜色，默认"papayawhip"。
    numberPerLine：当显示板块名称时，每行显示个数，默认5。
    
    返回值：df
    """
    if indicator in ["股价","股票价格","价格","收盘价","价位"]:
        indicator="最新价"
    if indicator in ["流动性","热门","活跃"]:
        indicator="换手率"   

    if rank==0:
        rank=5  
        
    import akshare as ak
    
    #获取所有板块信息
    try:
        concept_df = ak.stock_board_concept_name_em()
    except:
        print("  #Warning(concept_stocks_em): data source is unaccessible, check network")
        return None
   
    concept_list=list(concept_df["板块名称"])
    concept_list2 = [x for x in concept_list if "昨日" not in x]
    concept_list_tmp = [x for x in concept_list2 if concept in x]
    
    #未找到
    if len(concept_list_tmp)==0 or concept=='':
        if concept!='':
            print("  #Warning(concept_stocks_em): concept not found with",concept)
        print("  Available concepts in East Money:",len(concept_list2),end='')
        printInLine_md(concept_list2,numberPerLine=numberPerLine,colalign="center")
        #print("  Tips: you can use one of the concepts above to re-run the command")
        
        return None    
        
    #找到多个概念板块
    if len(concept_list_tmp)>1 and len(concept_list_tmp)<numberPerLine:
        print("  Concepts found in East Money:",end='')
        print_list(concept_list_tmp,leading_blanks=2)
        #print("  Tips: you can use one of the concepts above to re-run the command")
        
        return None    

    if len(concept_list_tmp)>numberPerLine and concept!='':
        print("  Concepts found in East Money:",len(concept_list_tmp),end='')
        printInLine_md(concept_list_tmp,numberPerLine=numberPerLine,colalign="center")
        #print("  Tips: you can use one of the concepts above to re-run the command")
        
        return None    

    #找到一个概念板块，详细处理
    #if len(concept_list_tmp)==1:
    concept=concept_list_tmp[0]
    
    #东方财富概念板块成分股
    cfg=ak.stock_board_concept_cons_em(concept)
    
    cfg_col_list=list(cfg)
    indicator_col=''
    for i in cfg_col_list:
        if indicator in i:
            indicator_col=i
            break
        
    if indicator_col=='':
        print("  #Warning(concept_stocks_em): unsupported indicator",indicator)
        
        remove_list=["序号","代码","名称"]
        cfg_col_list_tmp = [x for x in cfg_col_list if x not in remove_list]
        print("  Supported indicators:",)
        print_list(cfg_col_list_tmp,leading_blanks=2)
        
        return None        
    
    collist=['序号','名称','代码','市盈率-动态','市净率','最新价','涨跌幅','换手率']
    if not indicator_col in collist:
        collist=collist+[indicator_col]
        
    #重新排序
    cfg.sort_values(by=[indicator_col]+["代码"],ascending=[False,True],inplace=True)
    cfg.reset_index(drop=True,inplace=True)
    cfg['序号']=cfg.index+1
        
    #行业均值与中位数
    indicator_mean=cfg[indicator_col].mean()
    indicator_median=cfg[indicator_col].median()
    indicator_total=cfg["代码"].count()
    
    found_stock=False
    stock_list=list(cfg['代码'])
    if ticker[:6] in stock_list:
        found_stock=True
    else:
        if not ticker=='':
            print("  #Warning(concept_stocks_em): stock not found for",ticker)
    
    if found_stock:
        indicator_value=cfg[cfg['代码']==ticker[:6]][indicator_col].values[0]
        indicator_seq=cfg[cfg['代码']==ticker[:6]]["序号"].values[0]
        from scipy.stats import percentileofscore
        indicator_pct=percentileofscore(cfg[indicator_col],indicator_value)
    
    #筛选
    if rank > 0:
        rank_flag="前"
        df_disp=cfg[collist].head(rank)
    else:
        rank_flag="后"
        df_disp=cfg[collist].tail(abs(rank))
    
    #强制显示所选股票
    if force_show_stock:
        #所选股票是否在其中？
        if not ticker[:6] in list(df_disp["代码"]):
            ticker_seq=cfg[cfg["代码"]==ticker[:6]]["序号"].values[0]
            seq1=ticker_seq-4; seq2=ticker_seq+5
            #如果超出开头
            if seq1 <=0:
                seq1=1; seq2=10
            #如果超出结尾    
            if seq2 > len(cfg):
                seq2=len(cfg); seq1=len(cfg)-9
                
            #注意：此处的&不能换为and    
            df_disp=cfg[(cfg["序号"]>=seq1) & (cfg["序号"]<=seq2)][collist]
        
    
    #制表
    titletxt="概念板块及其上市公司排名："+concept+"，"+indicator_col+"("+rank_flag+str(abs(rank))+"名)"

    footnote1="概念板块的"+indicator_col+"整体状况：均值"+str(round(indicator_mean,2))+"，中位数"+str(round(indicator_median,2))+"\n"
    footnote2=''
    if found_stock:
        tname=ticker_name(ticker)
        footnote2=tname+"的"+indicator_col+"："+str(round(indicator_value,2))+"，板块排名"+str(indicator_seq)+"/"+str(indicator_total)+"，分位"+str(round(indicator_pct,2))+"%\n"
    else:
        footnote2="概念板块："+concept+"，成分股数量"+str(len(cfg))+'\n'
        
    import datetime; stoday = datetime.date.today()
    footnote3="*** 信息来源：东方财富，"+str(stoday) 
    if found_stock:
        footnote=footnote1+footnote2+footnote3
    else:
        footnote=footnote2+footnote1+footnote3
    
    #确定表格字体大小
    titile_font_size=font_size
    heading_font_size=data_font_size=str(int(font_size.replace('px',''))-1)+'px'
    
    df_display_CSS(df_disp,titletxt=titletxt,footnote=footnote,facecolor=facecolor, \
                   first_col_align='center',second_col_align='left', \
                   titile_font_size=titile_font_size,heading_font_size=heading_font_size, \
                   data_font_size=data_font_size)
    
    return cfg
    



#==============================================================================
if __name__ == '__main__':
    ticker='600519.SS'
    ticker='600305.SS'
    
    get_stock_industry_sw(ticker)

def get_stock_industry_sw(ticker):
    """
    ===========================================================================
    功能：抓取股票的申万行业分类名称
    参数：
    ticker：A股股票代码
    
    返回：申万行业分类名称
    """
    
    import requests
    from bs4 import BeautifulSoup

    ticker6=ticker[:6]    
    url=f"https://vip.stock.finance.sina.com.cn/corp/go.php/vCI_CorpOtherInfo/stockid/{ticker6}/menu_num/2.phtml"
    headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }    
    response = requests.get(url,headers=headers)
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')

        t = soup.find('table',class_="comInfo1")
        industry = t.find_all("tr")[2].find("td").text
        
        return industry
    else:
        return ''

#==============================================================================
if __name__ == '__main__':
    ticker='600519.SS'
    ticker='600305.SS'  
    
    stock_peers_sw(ticker)
    
def stock_peers_sw(ticker):
    """
    ===========================================================================
    功能：显示股票的申万行业分类及其同行
    参数：
    ticker：A股股票代码
    返回：无
    """
    
    try:
        hangye=get_stock_industry_sw(ticker)
    except:
        print("  #Warning(stock_peers_sw): industry info not found for",ticker)
        return
    
    if hangye=='':
        print("  #Warning(stock_peers_sw): found empty industry for",ticker)
        return
    
    ilist=[]; hangye_final=''
    #三级行业优先
    hangye3=hangye+'Ⅲ'   
    try:
        ilist=print_industry_component_sw(iname=hangye3,return_result=True)
        hangye_final=hangye3
    except:
        #二级行业次优先
        hangye2=hangye+'Ⅱ'
        try:
            ilist=print_industry_component_sw(iname=hangye2,return_result=True)
            hangye_final=hangye2
        except:
            try:
                ilist=print_industry_component_sw(iname=hangye,return_result=True)
                hangye_final=hangye
            except:
                print("\n #Warning(stock_peers_sw): failed to search peers for",ticker)
                print("  Possible solutions:")
                print("  Try first: upgrade akshare, restart Jupyter and try again")
                #print("  If not working, uninstall anaconda and reinstall a newer version")

    #查找股票在行业板块中的位置
    ticker_item=''
    if not ilist=='':
        ticker6=ticker[:6]
        for i in ilist:
            if ticker6 in i:
                ticker_item=i
                ticker_pos=ilist.index(i)+1
                break
        if ticker_item != '':
            footnote0="注："
            footnote1=ticker_item+"在申万行业"+hangye_final+"指数中的权重排名为"+str(ticker_pos)+'/'+str(len(ilist))
            footnote2="该指数的权重排名依据主要包括公司的市值规模、流动性以及市场代表性"
            footnote=footnote0+'\n'+footnote1+'\n'+footnote2
            print(footnote)
    return
        
#==============================================================================
if __name__ == '__main__':
    sw_index=['绩优股指数','大盘指数','中市盈率指数','高市净率指数',]
    sw_index=['大类风格-先进制造','大类风格--医药医疗']
    
    index_intersection_sw(sw_index)

def index_intersection_sw(sw_index=[]):
    """
    ===========================================================================
    功能：寻找多个申万指数中共同的成分股
    主要参数：
    sw_index：申万行业分类指数列表，至少两个指数。
    返回值：无
    示例：
    sw_index=['绩优股指数','大盘指数','中市盈率指数','高市净率指数']
    """
    #寻找多个申万指数中共同的成分股
    if len(sw_index)==0:
        print("  #Warning(stock_intersection_sw): no index found for intersection")
        return
    
    if isinstance(sw_index,str):
        sw_index=[sw_index]
        
    result_list=[]
    for i in sw_index:
        try:
            ilist=print_industry_component_sw(i,printout=False,return_result=True)  
        except:
            print("  #Warning(stock_intersection_sw): failed to find component for index",i)
            continue
        
        if len(result_list)==0:
            result_list=[ilist]
        else:
            result_list=result_list+[ilist]
            
    list_intersection(result_list)
    
    return
#==============================================================================
#==============================================================================
#==============================================================================
#==============================================================================
#==============================================================================
#==============================================================================
    