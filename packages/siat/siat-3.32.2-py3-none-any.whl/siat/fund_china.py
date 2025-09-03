# -*- coding: utf-8 -*-
"""
本模块功能：中国基金市场案例分析
所属工具包：证券投资分析工具SIAT 
SIAT：Security Investment Analysis Tool
创建日期：2020年10月17日
最新修订日期：2025年3月28日
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
from siat.grafix import *
from siat.bond_base import *
from siat.security_trend2 import *
#==============================================================================
#好习惯
import akshare as ak
import pandas as pd

#==============================================================================
def compare_fund_holding_china(ticker,quarters,rank=10,font_size='14px'):
    """
    功能：套壳函数fund_stock_holding_compare_china
    """
    if len(quarters) < 2:
        print("  #Warning(compare_fund_holding_china): need 2 quarters to compare at",quarters)
        return None
    """
    if quarters[0] >= quarters[1]:
        print("  #Warning(compare_fund_holding_china):",quarters[0],"is supposed to be earlier than",quarters[1])
        return None
    """
    #保证较早的季度排在前面
    quarters.sort()  
    
    df=fund_stock_holding_compare_china(fund=ticker,quarter1=quarters[0],quarter2=quarters[1], \
                                        rank=rank,font_size=font_size)
    
    return df

if __name__=='__main__':
    fund='000592.SS'
    quarter1='2023Q4'
    quarter2='2024Q1'
    
    df=fund_stock_holding_compare_china(fund,quarter1,quarter2,rank=10)

#比较两个季度之间的基金持仓变化
def fund_stock_holding_compare_china(fund,quarter1,quarter2,rank=10, \
                                     font_size='14px'):
    """
    功能：基金fund在两个季度quarter1和quarter2的持仓股票对比（股数和金额），前rank名股票
    参数：
    fund,str,基金代码;
    quarter1,str,靠前的季度, 格式为 'YYYYQ1',例如: '2021Q2';
    quarter2,str,靠后的季度, 格式为 'YYYYQ1',例如: '2021Q2';
    
    注意：监管仅要求基金披露前十大重仓股，因此其持仓比例之和一般小于100%；若大于100%，
    则为基金以其净资产作为抵押加了杠杆融资，买进更多成份股，导致成份股总价值（基金总资产）超过了基金的净资产。
    基金总资产 = 基金负债 + 基金净资产
    """
    print("Searching fund holding info, which may take time, please wait ...\n")
    
    #import akshare as ak
    #import pandas as pd    
    
    code=fund[:6]
    s1=quarter1.upper()
    s2=quarter2.upper()
    years=[s1[0:4],s2[0:4]]

    s1_share = s1+'持股数'
    s2_share = s2+'持股数'
    s1_value = s1+'持仓市值'
    s2_value = s2+'持仓市值'
    s1_ratio = s1+'持仓比例'
    s2_ratio = s2+'持仓比例'

    """
    try:
        data = ak.fund_portfolio_hold_em(symbol=fund,date=years[0])
    except:
        print("  #Error(fund_stock_holding_compare_china): stock fund",fund,"not found or wrong year",years[0])
        return
    if len(data)==0:
        print("  #Error(fund_stock_holding_compare_china): stock fund",fund,"not found or wrong year",years[0])
        return      
    """
    
    data=pd.DataFrame()
    for yr in years:
        try:
            df_tmp = ak.fund_portfolio_hold_em(symbol=code,date=yr)
        except:
            print("  #Error(fund_stock_holding_compare_china): wrong year",yr)
            break

        if len(df_tmp)==0:
            print("  #Error(fund_stock_holding_compare_china): stock fund",fund,"not found or wrong year",years[0])
            break
        
        if len(data)==0:
            data=df_tmp
        else:
            try:
                data = data.append(df_tmp)
            except:
                data = data._append(df_tmp)
            
    data.drop_duplicates(keep='first', inplace=True)

    data['季度']=data['季度'].apply(lambda x:x[:6])
    data['季度'] = data['季度'].str.replace('年','Q')
    data['占净值比例'] = pd.to_numeric(data['占净值比例'])

    df1 =data[data['季度']==s1]
    if len(df1)==0:
        print("  #Error(fund_stock_holding_compare_china): no data available for",s1)
        return        
    
    df1 = df1[['股票代码', '股票名称','持股数','持仓市值','占净值比例']]
    df1 = df1.rename(columns={'持股数':s1_share,'持仓市值':s1_value,'占净值比例':s1_ratio})
    num1=len(df1)
    
    df2 =data[data['季度']==s2]
    if len(df2)==0:
        print("  #Error(fund_stock_holding_compare_china): no data available for",s2)
        return 
    
    df2 = df2[['股票代码', '股票名称','持股数','持仓市值','占净值比例']]
    df2 = df2.rename(columns={'持股数':s2_share,'持仓市值':s2_value,'占净值比例':s2_ratio})
    num2=len(df2)

    df_merge = pd.merge(df1,df2,on=['股票代码','股票名称'],how='outer')

    # Q2 和 Q4，即半年度和年度报告，是需要披露全部持仓的
    # 合并后，在dataframe 中 NaN 的数据应为 0

    if s1.endswith('Q2') or s1.endswith('Q4'):
        df_merge[s1_share] = df_merge[s1_share].fillna(0)
        df_merge[s1_value] = df_merge[s1_value].fillna(0)
        df_merge[s1_ratio] = df_merge[s1_ratio].fillna(0)

    if s2.endswith('Q2') or s2.endswith('Q4'):
        df_merge[s2_share] = df_merge[s2_share].fillna(0)
        df_merge[s2_value] = df_merge[s2_value].fillna(0)
        df_merge[s2_ratio] = df_merge[s2_ratio].fillna(0)

    df_merge.fillna(0,inplace=True)    

    df_merge['持股数变化'] = df_merge[s2_share] - df_merge[s1_share]
    df_merge['持仓比例变化'] = df_merge[s2_ratio] - df_merge[s1_ratio]
    df_merge['持仓市值变化'] = df_merge[s2_value] - df_merge[s1_value]
    df_merge = df_merge.sort_values(s2_value,ascending=False)
    
    #df_merge['股票名称'] = df_merge['股票名称_y']
    #df_merge.loc[df_merge['股票名称'].isna(),'股票名称'] = df_merge.loc[df_merge['股票名称'].isna(),'股票名称_x']
    df_merge = df_merge[['股票名称','股票代码',s1_share,s2_share,'持股数变化',s1_ratio,s2_ratio,'持仓比例变化',s1_value,s2_value,'持仓市值变化']]
    
    df_merge.reset_index(drop=True,inplace=True)
    if rank>0:
        df=df_merge.head(rank)
    else:
        df=df_merge.tail(-rank)
    """
    #持股数和持仓比例取整数
    df.fillna(0)
    try:
        df[s1_share]=df[s1_share].astype('int')
    except: pass
    try:
        df[s2_share]=df[s2_share].astype('int')
    except: pass
    try:
        df[s1_value]=df[s1_value].astype('int')
    except: pass
    try:
        df[s2_value]=df[s2_value].astype('int')
    except: pass
    df['持股数变化'] = df[s2_share] - df[s1_share]
    """
    #设置打印对齐
    pd.set_option('display.max_columns', 1000)
    pd.set_option('display.width', 1000)
    pd.set_option('display.max_colwidth', 1000)
    pd.set_option('display.unicode.ambiguous_as_wide', True)
    pd.set_option('display.unicode.east_asian_width', True)

    #获取基金名称
    """
    #names = ak.fund_em_fund_name()
    names = ak.fund_name_em()
    namedf=names[names['基金代码']==code]
    if len(namedf)==0:
        name=fund
    else:
        name=namedf['基金简称'].values[0]
    """
    name=get_fund_name_china2(fund)
    
    order='前'
    if rank <0: 
        order='后'
        rank=-rank
        
    # 替换空值
    df.fillna('---')
    """
    print("===== 中国基金持仓股票分析："+name+'，'+s1+"对比"+s2,"(按后者持仓比例高低排列，"+order+str(rank)+"名重仓股) =====\n")
    print(df.to_string(index=False))
    import datetime; today = datetime.date.today()
    print("\n*** 注：持股数为万股，持仓市值为万元，持仓比例为占基金资产净值比例%，包括A股与非A股")
    print("    数据来源：天天基金/东方财富, 期间持仓股票总计"+str(len(df_merge))+"只,",today)      
    """
    titletxt="基金持仓转移明细："+name+'基金，'+s1+"对比"+s2+"（按后者持仓比例降序排列，"+order+str(rank)+"名重仓股）"
    
    footnote1="【注】持仓数单位为万股，持仓市值单位为万元，持仓比例为成份股价值为占基金资产净值%（以最新期间为准列示）\n"
    #footnote2=s1+'/'+s2+"期末持仓证券数"+str(num1)+'/'+str(num2)+"只"+'\n'
    footnote2='监管仅要求披露前十大重仓股，其持仓比例之和一般小于100%；若大于100%则为基金加了杠杆，总资产多于净资产\n'
    import datetime; todaydt = datetime.date.today()
    footnote9="数据来源：天天基金/东方财富，"+str(todaydt)+"统计"
    footnote=footnote1+footnote2+footnote9
    
    #调整字段顺序
    collist=list(df)
    df['序号']=df.index + 1
    df=df[['序号']+collist]
    """
    shares=[]; ratios=[]; values=[]
    for c in collist:
        if "持股数" in c:
            shares=shares+[c]
        if "持仓比例" in c:
            ratios=ratios+[c]
        if "持仓市值" in c:
            values=values+[c]
    collist1=['序号','股票名称','股票代码']+shares+ratios+values
    df=df[collist1]
    """
    df.replace(0,'---',inplace=True); df.replace('0','---',inplace=True)

    #确定表格字体大小
    titile_font_size=font_size
    heading_font_size=data_font_size=str(int(font_size.replace('px',''))-2)+'px'
    
    df_display_CSS(df,titletxt=titletxt,footnote=footnote,facecolor='papayawhip',decimals=2, \
                       first_col_align='center',second_col_align='left', \
                       last_col_align='right',other_col_align='right', \
                       titile_font_size=titile_font_size, \
                       heading_font_size=heading_font_size, \
                       data_font_size=data_font_size)     
    
    return df_merge

#==============================================================================
def fund_holding_china(ticker,rank=10,pastyears=2,reverse=False,font_size='16px'):
    """
    功能：套壳函数fund_stock_holding_rank_china
    """
    df,data=fund_stock_holding_rank_china(fund=ticker,rank=rank,year_num=pastyears, \
                                          reverse=reverse,font_size=font_size)
    
    return df,data

if __name__=='__main__':
    fund='000592.SS'
    year_num=2
    rank=10
    
    df=fund_stock_holding_rank_china(fund,year_num=2)
    
# 获取单只基金的十大股票名称信息
def fund_stock_holding_rank_china(fund,rank=10,year_num=2, \
                                  reverse=False,font_size='16px'):
    """
    基金的成份股持仓转移矩阵
    比较股票型基金fund近year_num年持仓的前10大股票排名变化
    """
    print("Searching fund stock holding info, which takes time, please wait ...\n")
    code=fund[:6]
    
    #import akshare as ak
    #import pandas as pd

    import datetime; today = datetime.date.today()
    year_0_num=int(str(today)[0:4])
    years=[]
    for yr in range(0,year_num):
        yri=str(year_0_num - yr)
        years=years+[yri]
    years.sort(reverse=False)    
    """
    #抓取第一年的信息
    data = ak.fund_portfolio_hold_em(symbol=fund,date=years[0])
    if len(data)==0:
        print("  #Error(fund_stock_holding_rank_china): stock fund",fund,"not found")
        return          
    """
    data=pd.DataFrame()
    try:
        for yr in years:
            df_tmp = ak.fund_portfolio_hold_em(symbol=code,date=yr)
            try:
                data = data.append(df_tmp)
            except:
                data = data._append(df_tmp)
    except:
        years_1=[]
        for yr in years:
            yr_1=str(int(yr)-1)
            years_1=years_1+[yr_1]
            
        for yr in years_1:
            df_tmp = ak.fund_portfolio_hold_em(symbol=code,date=yr)
            try:
                data = data.append(df_tmp)
            except:
                data = data._append(df_tmp)
            
    data.drop_duplicates(keep='first', inplace=True)

    # data['季度']=data['季度'].apply(lambda x:x[:8])
    data['季度']=data['季度'].apply(lambda x:x[:6])
    data['季度'] = data['季度'].str.replace('年','Q')
    #data['占净值比例'] = pd.to_numeric(data['占净值比例'])
    #data.fillna(0,inplace=True)
    #data=data.replace('',0)
    data['占净值比例'] = pd.to_numeric(data['占净值比例'])
    
    # 序号中，有些是字符串，并且包含字符 “*”，需要替换，最后转换为数字
    data['序号'] = data['序号'].astype(str)
    data['序号'] = data['序号'].str.replace('\*','',regex=True)
    data['序号'] = pd.to_numeric(data['序号'])
    
    data = data.sort_values(['季度','持仓市值'],ascending=[True,False])
    #data.drop_duplicates(keep='first',inplace=True)
    
    yqlist=list(set(list(data['季度'])))
    yqlist.sort(reverse=False)
    #import pandas as pd
    data2=pd.DataFrame()
    
    for yq in yqlist:
        dft=data[data['季度']==yq]
        dft.sort_values(by='占净值比例',ascending=False,inplace=True)
        dft.reset_index(drop=True,inplace=True)
        dft['序号']=dft.index + 1
        dft2=dft.head(rank)
        
        if len(data2)==0:
            data2=dft2
        else:
            try:
                data2=data2.append(dft2)
            except:
                data2=data2._append(dft2)
    
    # 合成信息
    data2['持股状况']=data2.apply(lambda x: x['股票名称']+'('+str(x['占净值比例'])+'，'+str(x['持股数'])+')',axis=1)
    
    df = data2.set_index(['序号','季度']).stack().unstack([1,2]).head(rank)
    
    #df = df.loc[:,(slice(None), '股票名称')] # 只选取 股票名称
    df = df.loc[:,(slice(None), '持股状况')] # 只选取 持股状况
    
    df = df.droplevel(None,axis=1)
    df.columns.name=None
    df.reset_index(inplace=True)
    """
    df['基金代码']=code
    cols = df.columns.tolist()
    cols = cols[:1] + cols[-1:] + cols[1:-1] # 将基金代码列名放前面
    df = df[cols]
    """
    #设置打印对齐
    pd.set_option('display.max_columns', 1000)
    pd.set_option('display.width', 1000)
    pd.set_option('display.max_colwidth', 1000)
    pd.set_option('display.unicode.ambiguous_as_wide', True)
    pd.set_option('display.unicode.east_asian_width', True)

    #获取基金名称
    """
    #names = ak.fund_em_fund_name()
    names = ak.fund_name_em()
    namedf=names[names['基金代码']==fund]
    if len(namedf)==0:
        name=fund
    else:
        name=namedf['基金简称'].values[0]
    """
    name=get_fund_name_china2(fund)
    
    #print("=== 基金持仓股票排行分析："+name+"，按照占净值比例高低排列 ===\n")
    titletxt="基金持仓转移矩阵："+name+"基金，按照占净值比例降序排列，前"+str(rank)+"名重仓股"
    import datetime; todaydt = datetime.date.today()
    #print("\n*** 注：包括A股与非A股。持股结构：股票简称(占净值比例%，持股数万股),",str(todaydt)) 
    footnote="【注】持仓结构：证券简称(占净值比例%，持仓数万股)，"+str(todaydt)+"统计"

    if reverse:
        #最新的日期放前面
        collist=list(df)
        collist.sort(reverse=True)
        df=df[collist]

    #确定表格字体大小
    titile_font_size=font_size
    heading_font_size=data_font_size=str(int(font_size.replace('px',''))-1)+'px'    
    
    df_display_CSS(df,titletxt=titletxt,footnote=footnote,facecolor='papayawhip',decimals=3, \
                       first_col_align='center',second_col_align='left', \
                       last_col_align='left',other_col_align='left', \
                       titile_font_size=titile_font_size, \
                       heading_font_size=heading_font_size, \
                       data_font_size=data_font_size)     
      
    """    
    alignlist=['center']+['left']*(len(list(df))-1)
    print(df.to_markdown(index=False,tablefmt='plain',colalign=alignlist))
    #print(df.to_string(index=False))
    """
    
    return df,data

#==============================================================================
if __name__=='__main__':
    fund='180801'
    rank=10

def reits_jsl_china(fund='',rank=10):
    """
    功能：REITs基金信息概述和列表
    目前不能正常工作，因为集思录数据源现在需要会员登陆才能显示和下载信息
    """
    #import akshare as ak
    try:
        df1 = ak.reits_info_jsl()
        df2 = ak.reits_realtime_em()
    except:
        print("Sorry, data source rejected access")
        return None
    
    #合成基金类型信息
    #import pandas as pd
    df = pd.merge(df1,df2,on = ['代码'],how='left')    
    df.rename(columns={'涨幅':'涨幅%','成交额_x':'成交额(万元)','折价率':'折价率%','规模':'规模(亿元)','剩余年限':'剩余年限(年)','涨跌幅':'涨跌幅%'}, inplace=True)
    num=len(df)
    
    df.sort_values(by=['昨收'],ascending=False,inplace=True)
    df.reset_index(drop=True,inplace=True)
    import datetime
    today = datetime.date.today()
    
    dfa=df[df['代码']==fund]
    # 未找到
    if len(dfa)==0:
        if rank > 0:
            dfa=df.head(rank)
        else:
            dfa=df.tail(-rank)
        dfb=dfa[['代码','名称','昨收','规模(亿元)','到期日']]
        
        #设置打印对齐
        pd.set_option('display.max_columns', 1000)
        pd.set_option('display.width', 1000)
        pd.set_option('display.max_colwidth', 1000)
        pd.set_option('display.unicode.ambiguous_as_wide', True)
        pd.set_option('display.unicode.east_asian_width', True)
        
        order='前'
        if rank <0: 
            order='后'
            rank=-rank
        print("\n===== 中国REITs基金列表(按最新价高低排列，"+order+str(rank)+"名) =====\n")
        print(dfb)

        print("*** 数据来源：东方财富/集思录, 总计"+str(num)+"只REITs基金,",today)         
        return dfb

    #单列一只基金的具体信息
    collist=['代码','简称','名称','全称','项目类型','基金公司','规模(亿元)','到期日','剩余年限(年)','净值','净值日期','现价','涨幅%','开盘价','最高价','最低价','昨收','成交额(万元)']
    maxcollen=0
    for i in collist:
        ilen=hzlen(i)
        if maxcollen < ilen:
            maxcollen=ilen
            
    dfb=dfa[collist]
    print("\n===== 中国REITs基金详情(代码"+fund+") =====\n")
    for i in collist:
        print(i,' '*(maxcollen-hzlen(i))+'：',dfb[i].values[0])

    print("*** 数据来源：东方财富/集思录,",today)         
    return dfb  

#==============================================================================
def reit_rank_china(indicator='最新价',rank=5):
    """
    功能：套壳函数reits_list_china
    """
    
    df=reits_list_china(indicator=indicator,rank=rank)
    
    return df


if __name__=='__main__':
    rank=10
    
    df=reits_list_china(rank=10)

def reits_list_china(indicator='最新价',rank=5):
    """
    功能：REITs基金信息概述和列表
    目前能正常工作
    """
    #import akshare as ak
    import math
    try:
        df2 = ak.reits_realtime_em()
    except:
        print("  #Error(reits_profile_china): akshare does not work properly now")
        return None
    df2.drop('序号', axis=1, inplace=True)
    #使用-999标记空缺值，避免后续处理出错，同时避免与真正的0混淆
    df2.fillna(-999,inplace=True)
    #df2['成交额']=df2['成交额'].apply(lambda x: int(x) if not math.isnan(x) else x)
    df2['成交额']=df2['成交额'].apply(lambda x: int(x))
    df2['成交量']=df2['成交量'].apply(lambda x: int(x))
    
    df2=df_swap_columns(df2, col1='代码', col2='名称')
    num=len(df2)

    indicatorlist=list(df2)
    if indicator not in indicatorlist:
        print("  #Error(reits_list_china):",indicator,"is not supported")
        print("  Supported indicators:",indicatorlist)
        return None
    
    #df2.indicator_values(by=['昨收'],ascending=False,inplace=True)
    df2.sort_values(by=[indicator],ascending=False,inplace=True)
    df2.replace(-999,"---",inplace=True)
    
    df2.reset_index(drop=True,inplace=True)
    df2=df2[df2[indicator] != "---"]
    num1=len(df2)

    collist=list(df2)
    
    for i in ['名称','代码',indicator]:
        collist.remove(i)
    collist1=['名称','代码',indicator]+collist 
    
    df2['序号']=df2.index + 1
    df2=df2[['序号']+collist1]
    """
    #设置打印对齐
    pd.set_option('display.max_columns', 1000)
    pd.set_option('display.width', 1000)
    pd.set_option('display.max_colwidth', 1000)
    pd.set_option('display.unicode.ambiguous_as_wide', True)
    pd.set_option('display.unicode.east_asian_width', True)
    """    
    if rank > 0:
        order='前'
        dfb=df2.head(rank)
    else: 
        order='后'
        rank=-rank
        dfb=df2.tail(rank)
    
    #print("\n===== 中国REITs基金列表(按最新价高低排列，"+order+str(rank)+"名) =====\n")
    titletxt="中国REITs基金列表（按"+indicator+"降序排列，"+order+str(rank)+"名）"
    """
    print(dfb.to_string(index=False))
    """
    #print('')   #在标题与表格之间空一行
    """
    alignlist=['right','center','left']+['right']*9
    try:   
        print(dfb.to_markdown(index=False,tablefmt='plain',colalign=alignlist))
    except:
        #解决汉字编码gbk出错问题
        print_df=dfb.to_markdown(index=False,tablefmt='plain',colalign=alignlist)
        print_df2=print_df.encode("utf-8",errors="strict")
        print(print_df2)       
    """    
    import datetime; todaydt = datetime.date.today()
    #print("\n*** 数据来源：东方财富, 总计"+str(num)+"只REITs基金,",today)  
    if num == num1 or order=='前':
        footnote="数据来源：新浪财经/天天基金，共找到"+str(num)+"只REITs基金，"+str(todaydt)  
    else:
        footnote="数据来源：新浪财经/天天基金，共找到"+str(num)+"只REITs基金（其中"+str(num-num1)+"只没有"+indicator+"信息），"+str(todaydt)

    df_display_CSS(dfb,titletxt=titletxt,footnote=footnote,facecolor='papayawhip',decimals=3, \
                       first_col_align='center',second_col_align='left', \
                       last_col_align='right',other_col_align='right', \
                       titile_font_size='15px',heading_font_size='13px', \
                       data_font_size='13px')     
    
    return df2

#==============================================================================

if __name__=='__main__':
    fund_type='全部类型'
    fund_type='债券型'
    printout=True

def pof_list_china(rank=10,fund_type='全部类型',printout=True):
    """
    功能：抓取公募基金列表，按照基金类型列表，按照基金名称拼音排序
    """
    print("Searching for publicly offering fund (POF) information in China ...")
    #import akshare as ak
    
    #基金基本信息：基金代码，基金简称，基金类型
    #df = ak.fund_em_fund_name()
    df = ak.fund_name_em()
    
    df.sort_values(by=['拼音全称'],na_position='first',inplace=True)
    df.drop_duplicates(subset=['基金代码','基金类型'], keep='first',inplace=True) 
    df=df[df['基金类型'] != '']
    df['基金类型']=df['基金类型'].apply(lambda x: x.upper())
    
    #获取基金类型列表，并去掉重复项
    typelist=list(set(list(df['基金类型'])))
    #判断类型是否支持
    matchtype=False
    for t in typelist+['全部类型']:
        if fund_type in t:
            matchtype=True
            break
        
    if not matchtype:
        print("  #Error(fund_list_china): unsupported fund type:",fund_type)
        print("  Supported fund_type:",typelist+['全部类型'])
        return None

    #摘取选定的基金类型
    if fund_type != '全部类型':
        #df2=df[df['基金类型']==fund_type]
        df2=df[df['基金类型'].apply(lambda x: fund_type in x)]
    else:
        df2=df
        
    df3=df2[['基金简称','基金代码','基金类型']]
    df3.reset_index(drop=True,inplace=True) 
    
    #打印种类数量信息    
    if printout:
        num=len(df3)
        if fund_type != '全部类型':
            print(texttranslate("共找到")+str(num)+texttranslate("支基金, 类型为")+fund_type)
            return df3
        
        titletxt="中国公募基金的类型与分布（前"+str(rank)+"名）"
        footnote1="共有"+str(len(typelist))+"种类型，"+str("{:,}".format(num))+'支基金\n'
        
        maxlen=0
        for t in typelist:
            tlen=hzlen(t)
            if tlen > maxlen: maxlen=tlen
        maxlen=maxlen+1
        
        #排序
        dfg0=pd.DataFrame(df.groupby("基金类型").size())
        dfg0.sort_values(by=[0], ascending=False, inplace=True)
        dfg=dfg0.head(rank)
        
        typelist2=list(dfg.index)
        try:
            typelist2.remove('')
        except:
            pass
        
        dfg.rename(columns={0:'基金数量'}, inplace=True)
        dfg['数量占比']=dfg['基金数量'].apply(lambda x: str(round(x/num*100,3))+'%')
        dfg.reset_index(inplace=True)
        
        collist=list(dfg)
        dfg['序号']=dfg.index+1
        dfg=dfg[['序号']+collist]

        footnote2="表中类型的数量占比为"+str(round(dfg['基金数量'].sum()/num*100,2))+"%\n"        
        import datetime; todaydt = datetime.date.today()
        footnote9="数据来源：东方财富/天天基金，"+str(todaydt)
        footnote=footnote1+footnote2+footnote9
        
        df_display_CSS(dfg,titletxt=titletxt,footnote=footnote,facecolor='papayawhip',decimals=3, \
                           first_col_align='center',second_col_align='left', \
                           last_col_align='right',other_col_align='right', \
                           titile_font_size='16px',heading_font_size='15px', \
                           data_font_size='15px')
        
    return df3

if __name__=='__main__':
    df=pof_list_china()

#==============================================================================
if __name__=='__main__':
    df=get_oef_rank_china()
    
def get_oef_rank_china():
    """
    功能：中国开放式基金排名，单位净值，累计净值，手续费
    不分类
    """
    
    print("Searching for open-ended fund (OEF) information in China ...")
    
    #import pandas as pd
    #import akshare as ak   
    
    #获取开放式基金实时信息
    try:
        print("  Looking for OEF net value information ...")
        df1 = ak.fund_open_fund_daily_em()
    except:
        print("  #Error(oef_rank_china): data source tentatively busy or unavailable, try later")
        return None
        
    collist=list(df1)
    nvname1=collist[2]
    nvname1_num_all=len(df1)
    nvname1_num_eq=len(df1[df1[nvname1]==''])
    nvname1_ratio_eq=nvname1_num_eq / nvname1_num_all
    
    nvname2=collist[3]
    #if df1[nvname1].eq('').all():
    if nvname1_ratio_eq > 0.5: #空缺率超过50%？        
        nvname1=collist[4]
        nvname2=collist[5]
    nvdate=nvname1[:10]
    
    df1x=df1[df1[nvname1] != '']
    
    #修改列名
    df1x.rename(columns={nvname1:'单位净值',nvname2:'累计净值'}, inplace=True) 
    df1c=df1x[['基金代码','基金简称','单位净值','累计净值','日增长率','申购状态','赎回状态','手续费']]
    
    #获取所有公募基金类型信息
    print("  Looking for OEF category information ...")
    df2 = ak.fund_name_em()
    
    print("  Analyzing OEF query requests ...")
    df2a=df2[['基金代码','基金类型']]
    
    #合成基金类型信息
    df3 = pd.merge(df1c,df2a,on = ['基金代码'],how='left')
    
    df3.fillna(0,inplace=True)
    df3=df3.replace('',0)
    df3['单位净值']=df3['单位净值'].astype('float')
    df3['累计净值']=df3['累计净值'].astype('float')
    df3['日增长率']=df3['日增长率'].astype('float')
    
    # 避免该字段出现非字符串类型引起后续出错
    df3['基金类型']=df3['基金类型'].astype(str)
    df3['净值日期']=nvdate

    print("Successfully retrieved",len(df3),"OEF products on",nvdate)

    return df3

#==============================================================================
if __name__=='__main__':
    fund_type='全部类型'
    fund_type='QDII'
    fund_type='REIT'
    fund_type='FOF'
    fund_type='LOF'
    fund_type='FOF-LOF'
    fund_type='MOM'
    
    rank=5
    indicator='单位净值'
    
    qdii=oef_rank_china2(df,fund_type='QDII',rank=5)

def oef_rank_china2(df,fund_type='全部类型',rank=5,indicator='单位净值'):
    """
    功能：中国开放式基金排名，单位净值，累计净值，手续费
    仅分类用
    """
    
    typelist=['单位净值','累计净值','手续费','增长率']
    if indicator not in typelist:
        print("  #Error(oef_rank_china2): unsupported indicator",indicator)
        print("  Supported indicators:",typelist)
        return None
    
    nvdate=df['净值日期'].values[0]

    #过滤基金类型
    if fund_type not in ['全部类型','','all']:
        fundtypelist=list(set(list(df['基金类型'])))
        try: fundtypelist.remove('0')
        except: pass
    
        fundtypelist=fundtypelist+['LOF','FOF-LOF','REITs','REIT','MOM']
        #检查基金类型是否存在
        found=False
        for ft in fundtypelist:
            if ft==0: continue
            if fund_type in ft: 
                found=True
                break
        
        #未找到基金类型            
        if not found:
            print("  Notice: unpredefined fund type",fund_type)
            print("  Predefined fund types:")
            fundtypelist.sort(reverse=True)
            printlist(fundtypelist,numperline=5,beforehand=' '*4,separator=' ')
            print("  Continue to search key word",fund_type,"among fund type and fund name ...")
            #return None
        
        df.dropna(inplace=True)
        
        df['基金类型s']=False
        df['基金类型s']=df.apply(lambda x: True if fund_type in x['基金类型'] else x['基金类型s'],axis=1)
        df['基金类型s']=df.apply(lambda x: True if fund_type in x['基金简称'] else x['基金类型s'],axis=1)
        
        if fund_type == 'QDII':
            df['基金类型s']=df.apply(lambda x: False if '不含' in x['基金类型'] else x['基金类型s'],axis=1)
        
        if fund_type == 'FOF':
            df['基金类型s']=df.apply(lambda x: True if (fund_type in x['基金类型'] or fund_type in x['基金简称']) else x['基金类型s'],axis=1)  
            #df['基金类型s']=df.apply(lambda x: False if ('LOF' in x['基金类型'] or 'LOF' in x['基金简称']) else x['基金类型s'],axis=1) 
        
        if fund_type == 'LOF':
            df['基金类型s']=df.apply(lambda x: True if (fund_type in x['基金类型'] or fund_type in x['基金简称']) else x['基金类型s'],axis=1)  
            #df['基金类型s']=df.apply(lambda x: False if ('FOF' in x['基金类型'] or 'FOF' in x['基金简称']) else x['基金类型s'],axis=1) 
        
        if fund_type == 'FOF-LOF':
            df['基金类型s']=df.apply(lambda x: True if (fund_type in x['基金类型'] or fund_type in x['基金简称']) else x['基金类型s'],axis=1)  
            
            
        df=df[df['基金类型s']==True]    
    
    num=len(df)
    if num==0:
        print("Sorry, no OEF products found in China with key word",fund_type)
        return None
    
    if indicator == '单位净值':
        df['单位净值']=df['单位净值'].apply(lambda x: round(x,2))
        df.sort_values(by=['单位净值'],ascending=False,inplace=True)
        #dfprint=df[['基金简称','基金代码','基金类型','单位净值','申购状态','赎回状态']]
        dfprint=df[['基金简称','基金代码','基金类型','单位净值','累计净值']]
        #print(texttranslate("\n===== 中国开放式基金排名：单位净值 ====="))
        titletxt="中国开放式基金排名：单位净值"
    
    if indicator == '累计净值':
        df['累计净值']=df['累计净值'].apply(lambda x: round(x,2))
        df.sort_values(by=['累计净值'],ascending=False,inplace=True)
        #dfprint=df[['基金简称','基金代码','基金类型','累计净值','申购状态','赎回状态']]
        dfprint=df[['基金简称','基金代码','基金类型','累计净值','单位净值']]
        #print(texttranslate("\n===== 中国开放式基金排名：累计净值 =====")) 
        titletxt="中国开放式基金排名：累计净值"
    
    if indicator == '手续费':
        try:
            df['手续费'] = df['手续费'].astype(str)
            df.sort_values(by=['手续费'],ascending=False,inplace=True)
        except: pass
        #dfprint=df[['基金简称','基金代码','基金类型','手续费','申购状态','赎回状态']]
        dfprint=df[['基金简称','基金代码','基金类型','手续费','单位净值']]
        #print(texttranslate("\n===== 中国开放式基金排名：手续费 =====")) 
        titletxt="中国开放式基金排名：手续费"         
    
    if indicator == '增长率':
        df.sort_values(by=['日增长率'],ascending=False,inplace=True)
        #dfprint=df[['基金简称','基金代码','基金类型','日增长率','申购状态','赎回状态']]
        dfprint=df[['基金简称','基金代码','基金类型','日增长率','单位净值']]
        #print(texttranslate("\n===== 中国开放式基金排名：增长率% ====="))  
        titletxt="中国开放式基金排名：增长率%"         
    
    df=df.replace(0,'--')
    
    #重新设置序号
    dfprint.dropna(inplace=True)
    dfprint.reset_index(drop=True,inplace=True)
    dfprint.index=dfprint.index + 1
    
    collist=list(dfprint)
    dfprint['序号']=dfprint.index
    dfprint=dfprint[['序号']+collist]
    
    if rank >= 0:
        dfprint10=dfprint.head(rank)
        order="前"
    else:
        dfprint10=dfprint.tail(-rank)
        order="后"
    titletxt=titletxt+"（"+order+str(abs(rank))+"名，降序排列）"
    footnote1="披露净值的开放式基金数量："+str(num)+'，'
    footnote2="基金类型："+str(fund_type)+'\n'
    
    footnote3="净值日期："+str(nvdate)+'，'
    
    import datetime; todaydt = datetime.date.today()
    #footnote4="数据来源：东方财富/天天基金，"+str(todaydt)
    footnote4="数据来源：新浪财经/天天基金\n"
    
    import time; current_time = time.localtime()
    formatted_hour = time.strftime("%H", current_time)
    footnote5=''
    if (formatted_hour >= '18' or formatted_hour <= '06') and not is_weekend(todaydt):
        footnote5="注意：此时若为数据源更新时段，获取的信息可能不全\n"
    
    footnote=footnote1+footnote2+footnote3+footnote4+footnote5
    
    df_display_CSS(dfprint10,titletxt=titletxt,footnote=footnote,facecolor='papayawhip',decimals=4, \
                       first_col_align='center',second_col_align='left', \
                       last_col_align='right',other_col_align='right', \
                       titile_font_size='16px',heading_font_size='15px', \
                       data_font_size='15px')
    
    return df
#==============================================================================

if __name__=='__main__':
    indicator='单位净值'
    indicator='增长率'
    
    fund_type='全部类型'
    
    fund_type='股票型'
    fund_type='FOF'
    fund_type='LOF'
    fund_type='FOF-LOF'
    fund_type='QDII'
    
    rank=10
    

def oef_rank_china(indicator='单位净值',fund_type='全部类型',rank=5):
    """
    功能：中国开放式基金排名，单位净值，累计净值，手续费
    """
    info_type=indicator
    
    typelist=['单位净值','累计净值','手续费','增长率']
    if info_type not in typelist:
        print("  #Error(oef_rank_china): unsupported indicator",info_type)
        print("  Supported indicators:",typelist)
        return None
    
    print("Searching for open-ended fund (OEF) information in China ...")
    #import akshare as ak   
    
    #获取开放式基金实时信息
    try:
        print("  Looking for OEF net value information ...")
        df1 = ak.fund_open_fund_daily_em()
    except:
        print("  #Error(oef_rank_china): data source tentatively busy or unavailable, try later")
        return None
        
    collist=list(df1)
    nvname1=collist[2]
    nvname1_num_all=len(df1)
    nvname1_num_eq=len(df1[df1[nvname1]==''])
    nvname1_ratio_eq=nvname1_num_eq / nvname1_num_all
    
    nvname2=collist[3]
    #if df1[nvname1].eq('').all():
    if nvname1_ratio_eq > 0.5: #空缺率超过50%？        
        nvname1=collist[4]
        nvname2=collist[5]
    nvdate=nvname1[:10]
    
    df1x=df1[df1[nvname1] != '']
    
    #修改列名
    df1x.rename(columns={nvname1:'单位净值',nvname2:'累计净值'}, inplace=True) 
    #df1a=df1.drop(df1[df1['单位净值']==''].index)
    #df1b=df1a.drop(df1a[df1a['累计净值']==''].index)
    df1c=df1x[['基金代码','基金简称','单位净值','累计净值','日增长率','申购状态','赎回状态','手续费']]
    
    
    #获取所有公募基金类型信息
    #df2 = ak.fund_em_fund_name()
    print("  Looking for OEF category information ...")
    df2 = ak.fund_name_em()
    
    print("  Analyzing OEF query requests ...")
    df2a=df2[['基金代码','基金类型']]
    
    #合成基金类型信息
    #import pandas as pd
    import numpy as np
    df3 = pd.merge(df1c,df2a,on = ['基金代码'],how='left')
    
    df3.fillna(0,inplace=True)
    df3=df3.replace('',0)
    df3['单位净值']=df3['单位净值'].astype('float')
    df3['累计净值']=df3['累计净值'].astype('float')
    df3['日增长率']=df3['日增长率'].astype('float')
    
    """
    df=df3[(df3['基金类型'] is not np.nan) and (df3['基金类型'] != 0)]
    """
    # 避免该字段出现非字符串类型引起后续出错
    df3['基金类型']=df3['基金类型'].astype(str)
    df=df3
    
    #过滤基金类型
    if fund_type != '全部类型':
        fundtypelist=list(set(list(df['基金类型'])))
        try: fundtypelist.remove('0')
        except: pass
    
        fundtypelist=fundtypelist+['LOF','FOF-LOF','REITs','REIT','MOM']
        """
        while np.nan in fundtypelist:
            fundtypelist.remove(np.nan)
        while 0 in fundtypelist:
            fundtypelist.remove(0)            
        """   
        #检查基金类型是否存在
        found=False
        for ft in fundtypelist:
            if ft==0: continue
            if fund_type in ft: 
                found=True
                break
        
        #未找到基金类型            
        if not found:
            print("  #Error(oef_rank_china): unsupported fund type",fund_type)
            print("  Supported fund types:",fundtypelist)
            return None
        
        #df.dropna(inplace=True)
        fund_filter=lambda x: fund_type in x
        df['基金类型s']=df['基金类型'].apply(fund_filter)
        df['基金类型s']=df['基金简称'].apply(fund_filter)
        
        if fund_type == 'QDII':
            df['基金类型s']=df.apply(lambda x: False if '不含' in x['基金类型'] else x['基金类型s'],axis=1)
        
        if fund_type == 'FOF':
            df['基金类型s']=df.apply(lambda x: True if (fund_type in x['基金类型'] or fund_type in x['基金简称']) else x['基金类型s'],axis=1)  
            #df['基金类型s']=df.apply(lambda x: False if ('LOF' in x['基金类型'] or 'LOF' in x['基金简称']) else x['基金类型s'],axis=1) 
        
        if fund_type == 'LOF':
            df['基金类型s']=df.apply(lambda x: True if (fund_type in x['基金类型'] or fund_type in x['基金简称']) else x['基金类型s'],axis=1)  
            #df['基金类型s']=df.apply(lambda x: False if ('FOF' in x['基金类型'] or 'FOF' in x['基金简称']) else x['基金类型s'],axis=1) 
        
        if fund_type == 'FOF-LOF':
            df['基金类型s']=df.apply(lambda x: True if (fund_type in x['基金类型'] or fund_type in x['基金简称']) else x['基金类型s'],axis=1)  
            
            
        df=df[df['基金类型s']==True]    
    
    num=len(df)
    
    if info_type == '单位净值':
        df['单位净值']=df['单位净值'].apply(lambda x: round(x,2))
        df.sort_values(by=['单位净值'],ascending=False,inplace=True)
        #dfprint=df[['基金简称','基金代码','基金类型','单位净值','申购状态','赎回状态']]
        dfprint=df[['基金简称','基金代码','基金类型','单位净值','累计净值']]
        #print(texttranslate("\n===== 中国开放式基金排名：单位净值 ====="))
        titletxt="中国开放式基金排名：单位净值"
    
    if info_type == '累计净值':
        df['累计净值']=df['累计净值'].apply(lambda x: round(x,2))
        df.sort_values(by=['累计净值'],ascending=False,inplace=True)
        #dfprint=df[['基金简称','基金代码','基金类型','累计净值','申购状态','赎回状态']]
        dfprint=df[['基金简称','基金代码','基金类型','累计净值','单位净值']]
        #print(texttranslate("\n===== 中国开放式基金排名：累计净值 =====")) 
        titletxt="中国开放式基金排名：累计净值"
    
    if info_type == '手续费':
        df.sort_values(by=['手续费'],ascending=False,inplace=True)
        #dfprint=df[['基金简称','基金代码','基金类型','手续费','申购状态','赎回状态']]
        dfprint=df[['基金简称','基金代码','基金类型','手续费','单位净值']]
        #print(texttranslate("\n===== 中国开放式基金排名：手续费 =====")) 
        titletxt="中国开放式基金排名：手续费"         
    
    if info_type == '增长率':
        df.sort_values(by=['日增长率'],ascending=False,inplace=True)
        #dfprint=df[['基金简称','基金代码','基金类型','日增长率','申购状态','赎回状态']]
        dfprint=df[['基金简称','基金代码','基金类型','日增长率','单位净值']]
        #print(texttranslate("\n===== 中国开放式基金排名：增长率% ====="))  
        titletxt="中国开放式基金排名：增长率%"         
    
    df=df.replace(0,'--')
    
    #设置打印对齐
    pd.set_option('display.max_columns', 1000)
    pd.set_option('display.width', 1000)
    pd.set_option('display.max_colwidth', 1000)
    pd.set_option('display.unicode.ambiguous_as_wide', True)
    pd.set_option('display.unicode.east_asian_width', True)
    
    dfprint.dropna(inplace=True)
    dfprint.reset_index(drop=True,inplace=True)
    dfprint.index=dfprint.index + 1
    
    collist=list(dfprint)
    dfprint['序号']=dfprint.index
    dfprint=dfprint[['序号']+collist]
    
    if rank >= 0:
        dfprint10=dfprint.head(rank)
        order="前"
    else:
        dfprint10=dfprint.tail(-rank)
        order="后"
    titletxt=titletxt+"（"+order+str(abs(rank))+"名，降序排列）"
    #print(dfprint10.to_string(index=False))
    """
    print(dfprint10)
    """
    """
    alignlist=['left','left']+['center']*(len(list(amac_sum_df.head(10)))-3)+['right']
    """
    """
    print('')   #在标题与表格之间空一行
    alignlist=['right','left','center','center','right','center','center']
    try:   
        print(dfprint10.to_markdown(index=True,tablefmt='plain',colalign=alignlist))
    except:
        #解决汉字编码gbk出错问题
        print_df=dfprint10.to_markdown(index=True,tablefmt='plain',colalign=alignlist)
        print_df2=print_df.encode("utf-8",errors="strict")
        print(print_df2)    
    
    print('\n'+texttranslate("共找到披露净值信息的开放式基金数量:"),len(dfprint),'\b，',end='')
    print(texttranslate("基金类型:"),fund_type)
    
    print(texttranslate("净值日期:"),nvdate,'\b. ',end='')
    import datetime
    today = datetime.date.today()
    print(texttranslate("数据来源：东方财富/天天基金,"),today)        
    """
    footnote1="披露净值的开放式基金数量："+str(num)+'，'
    footnote2="基金类型："+str(fund_type)+'\n'
    footnote3="净值日期："+str(nvdate)+'，'
    
    import datetime; todaydt = datetime.date.today()
    #footnote4="数据来源：东方财富/天天基金，"+str(todaydt)
    
    import time; current_time = time.localtime()
    formatted_hour = time.strftime("%H", current_time)
    footnote4=''
    if formatted_hour > '17':
        footnote4="此时若为数据源更新时段，获取的信息可能不全\n"
    
    footnote5="数据来源：新浪财经/天天基金"
    footnote=footnote1+footnote2+footnote3+footnote4+footnote5
    
    df_display_CSS(dfprint10,titletxt=titletxt,footnote=footnote,facecolor='papayawhip',decimals=4, \
                       first_col_align='center',second_col_align='left', \
                       last_col_align='right',other_col_align='right', \
                       titile_font_size='16px',heading_font_size='15px', \
                       data_font_size='15px')
    
    return df

if __name__=='__main__':
     df=oef_rank_china(info_type='单位净值')
     df=oef_rank_china(info_type='累计净值')
     df=oef_rank_china(info_type='手续费')

#==============================================================================
if __name__=='__main__':
    fund_code='000009'
    fund_code='0000XX'
    fund_name,fund_type=get_oef_name_china(fund_code)
    
def get_oef_name_china(fund_code):
    """
    功能：获得基金的名称和类型
    """
    
    #import akshare as ak 
    try:
        names=ak.fund_name_em() 
    except:
        return fund_code,'未知类型'
    
    dft=names[names['基金代码']==fund_code]
    if len(dft) != 0:
        fund_name=dft['基金简称'].values[0]
        fund_type=dft['基金类型'].values[0]
    else:
        return fund_code,'未知类型'
    
    return fund_name,fund_type

#==============================================================================
if __name__=='__main__':
    fund='050111.SS'
    fund='000592.SS'
    start='MRM'
    end='today'
    trend_type='净值'
    power=0
    twinx=False
    zeroline=False

def oef_trend_china(ticker,start,end='today',indicator='净值', \
                    power=0,twinx=False, \
                    average_value=True,facecolor='whitesmoke',
                    loc1='best',loc2='best'):
    """
    功能：开放式基金业绩趋势，单位净值，累计净值，近三个月收益率，同类排名，总排名
    """
    fund=ticker
    fromdate,todate=start_end_preprocess(start,end)
    trend_type=indicator
    
    #检查走势类型
    trendlist=["净值","单位净值","累计净值","收益率","排名"]
    if trend_type not in trendlist:
        print("  #Error(oef_trend_china): unsupported trend type:",trend_type)
        print("  Supported trend types:",trendlist)
        return None
    
    #检查日期
    result,start,end=check_period(fromdate,todate)
    if not result:
        print("  #Error(oef_trend_china): invalid date period:",fromdate,todate)
        return None
    """
    #转换日期格式
    import datetime
    startdate=datetime.datetime.strftime(start,"%Y-%m-%d")
    enddate=str(datetime.datetime.strftime(end,"%Y-%m-%d"))
    """
    print("Searching for open-ended fund (OEF) trend info in China ...")
    #import akshare as ak   
    #import pandas as pd

    #开放式基金-历史数据
    import datetime; today = datetime.date.today()
    source=texttranslate("数据来源：东方财富/天天基金")

    fund1=fund[:6]
    fund_name=ticker_name(fund1,'fund')

    #绘制单位/累计净值对比图
    if trend_type == '净值':
        df1 = ak.fund_open_fund_info_em(fund1, indicator="单位净值走势")
        df1.rename(columns={'净值日期':'date','单位净值':'单位净值'}, inplace=True)
        df1['日期']=df1['date']
        df1.set_index(['date'],inplace=True) 
        
        df2 = ak.fund_open_fund_info_em(fund1, indicator="累计净值走势")
        df2.rename(columns={'净值日期':'date','累计净值':'累计净值'}, inplace=True)
        df2.set_index(['date'],inplace=True)       
        
        #合并
        df = pd.merge(df1,df2,left_index=True,right_index=True,how='inner')
        df['日期']=df['日期'].apply(lambda x: pd.to_datetime(x))
        
        dfp=df[(df['日期'] >= start)]
        dfp=dfp[(dfp['日期'] <= end)]
        if len(dfp) == 0:
            print("  #Error(oef_trend_china): no info found for",fund,"in the period:",fromdate,todate)
            return
        
        #绘制双线图
        ticker1=fund1; colname1='单位净值';label1=texttranslate('单位净值')
        ticker2=fund1; colname2='累计净值';label2=texttranslate('累计净值')
        #ylabeltxt='人民币元'
        ylabeltxt=texttranslate('净值')
        
        titletxt=texttranslate("开放式基金的净值趋势：")+fund_name
        
        #footnote=source+', '+str(today)
        footnote='注意：图中为交易市场数据，存在溢价或折价，可能与基金公司公布的净值存在差异\n'+source+', '+str(today)
        
        plot_line2(dfp,ticker1,colname1,label1, \
                   dfp,ticker2,colname2,label2, \
                   ylabeltxt,titletxt,footnote,power=power,twinx=twinx, \
                   facecolor=facecolor, \
                   loc1=loc1,loc2=loc2)
        return df

    #绘制单位净值图
    if trend_type == '单位净值':
        df1 = ak.fund_open_fund_info_em(fund1, indicator="单位净值走势")
        df1.rename(columns={'净值日期':'date','单位净值':'单位净值'}, inplace=True)
        df1['日期']=df1['date']
        df1.set_index(['date'],inplace=True) 
        """
        df2 = ak.fund_open_fund_info_em(fund1, indicator="累计净值走势")
        df2.rename(columns={'净值日期':'date','累计净值':'累计净值'}, inplace=True)
        df2.set_index(['date'],inplace=True)       
        """
        #合并
        #df = pd.merge(df1,df2,left_index=True,right_index=True,how='inner')
        df = df1
        df['日期']=df['日期'].apply(lambda x: pd.to_datetime(x))
        
        dfp=df[(df['日期'] >= start)]
        dfp=dfp[(dfp['日期'] <= end)]
        if len(dfp) == 0:
            print("  #Error(oef_trend_china): no info found for",fund,"in the period:",fromdate,todate)
            return
        
        #绘图
        ticker1=fund1; colname1='单位净值';label1=texttranslate('单位净值')
        #ticker2=fund1; colname2='累计净值';label2=texttranslate('累计净值')
        #ylabeltxt='人民币元'
        ylabeltxt=texttranslate('单位净值')
        
        titletxt=texttranslate("开放式基金的净值趋势：")+fund_name
        
        #footnote=source+', '+str(today)
        footnote='图中为交易市场数据，存在溢价或折价，可能与基金公司公布的净值存在差异\n'+source+', '+str(today)
        
        plot_line(dfp,colname1,label1,ylabeltxt,titletxt,footnote,power=power,loc=loc1, \
                  average_value=average_value,facecolor=facecolor)    
        """
        plot_line2(dfp,ticker1,colname1,label1, \
                   dfp,ticker2,colname2,label2, \
                   ylabeltxt,titletxt,footnote,power=power,twinx=twinx, \
                   facecolor=facecolor, \
                   loc1=loc1,loc2=loc2)
        """
        return df

    #绘制累计净值图
    if trend_type == '累计净值':
        df2 = ak.fund_open_fund_info_em(fund1, indicator="累计净值走势")
        df2.rename(columns={'净值日期':'date','累计净值':'累计净值'}, inplace=True)
        df2['日期']=df2['date']
        df2.set_index(['date'],inplace=True)     
        
        #合并
        df = df2
        df['日期']=df['日期'].apply(lambda x: pd.to_datetime(x))
        
        dfp=df[(df['日期'] >= start)]
        dfp=dfp[(dfp['日期'] <= end)]
        if len(dfp) == 0:
            print("  #Error(oef_trend_china): no info found for",fund,"in the period:",fromdate,todate)
            return
        
        #绘图
        ticker2=fund1; colname2='累计净值';label2=texttranslate('累计净值')
        #ylabeltxt='人民币元'
        ylabeltxt=texttranslate('累计净值')
        
        titletxt=texttranslate("开放式基金的净值趋势：")+fund_name
        
        #footnote=source+', '+str(today)
        footnote='图中为交易市场数据，存在溢价或折价，可能与基金公司公布的净值存在差异\n'+source+', '+str(today)
        
        plot_line(dfp,colname2,label2,ylabeltxt,titletxt,footnote,power=power,loc=loc1, \
                  average_value=average_value,facecolor=facecolor)    

        return df
    
    
    #绘制累计收益率单线图
    if trend_type == '收益率':
        df = ak.fund_open_fund_info_em(fund1, indicator="累计收益率走势")
        #df.rename(columns={'净值日期':'date','累计收益率':'累计收益率'}, inplace=True)
        df['date']=df['日期']
        df.set_index(['date'],inplace=True) 
        df['日期']=df['日期'].apply(lambda x: pd.to_datetime(x))
        dfp=df[(df['日期'] >= start)]
        dfp=dfp[(dfp['日期'] <= end)]  
        if len(dfp) == 0:
            print("  #Error(oef_trend_china): no info found for",fund,"in the period:",fromdate,todate)
            return        
    
        colname='累计收益率'; collabel=texttranslate('累计收益率%')
        ylabeltxt=texttranslate('累计收益率%')
        titletxt=texttranslate("开放式基金的累计收益率趋势：")+fund_name
        footnote=source+'，'+str(today)
        plot_line(dfp,colname,collabel,ylabeltxt,titletxt,footnote,power=power,loc=loc1, \
                  average_value=average_value,facecolor=facecolor)    
        return df
    
    #绘制同类排名图：近三个月收益率
    if trend_type == '排名':
        df1 = ak.fund_open_fund_info_em(fund1, indicator="同类排名走势")
        df1.rename(columns={'报告日期':'date','同类型排名-每日近三月排名':'同类排名','总排名-每日近三月排名':'总排名'}, inplace=True)
        df1['日期']=df1['date']
        df1['总排名']=df1['总排名'].astype('int64')
        df1.set_index(['date'],inplace=True) 
        
        df2 = ak.fund_open_fund_info_em(fund1, indicator="同类排名百分比")
        df2.rename(columns={'报告日期':'date','同类型排名-每日近3月收益排名百分比':'同类排名百分比'}, inplace=True)
        df2.set_index(['date'],inplace=True)       
        
        #合并
        df = pd.merge(df1,df2,left_index=True,right_index=True,how='inner')
        df['日期']=df['日期'].apply(lambda x: pd.to_datetime(x))
        dfp=df[(df['日期'] >= start)]
        dfp=dfp[(dfp['日期'] <= end)]
        if len(dfp) == 0:
            print("  #Error(oef_trend_china): no info found for",fund,"in the period:",fromdate,todate)
            return        

        #绘制双线图：同类排名，总排名
        ylabeltxt=''
        titletxt=texttranslate("开放式基金的近三个月收益率排名趋势：")+fund_name
        
        footnote=source+', '+str(today)        
        
        ticker1=fund1; colname1='同类排名';label1=texttranslate('同类排名')
        """
        ticker2=fund1; colname2='同类排名百分比';label2=texttranslate('同类排名百分比')
        dfp1=pd.DataFrame(dfp[colname1])
        dfp2=pd.DataFrame(dfp[colname2])
        plot_line2(dfp1,ticker1,colname1,label1, \
               dfp2,ticker2,colname2,label2, \
               ylabeltxt,titletxt,footnote,power=power,twinx=True)
        """
        #    
        ticker2=fund1; colname2='总排名';label2=texttranslate('开放式基金总排名')  
        dfp1=pd.DataFrame(dfp[colname1])
        dfp2=pd.DataFrame(dfp[colname2])        
        plot_line2(dfp1,ticker1,colname1,label1, \
                   dfp2,ticker2,colname2,label2, \
                   ylabeltxt,titletxt,footnote,power=power,twinx=twinx, \
                   facecolor=facecolor, \
                   loc1=loc1,loc2=loc2)            
        
        return df
    
#==============================================================================
if __name__=='__main__':
    indicator="万份收益"
    rank=5

def mmf_rank_china(indicator="7日年化%",rank=5):
    """
    功能：中国货币型基金排名，7日年化收益率%
    货币基金的万份收益指的是基金公司每日公布的当日每万份基金单位产生的收益金额，即万份基金单位收益。
    注意:万份基金单位收益与万份基金累计收益是不一样的，投资者想要买货币基金应改看基金的万份基金单位收益。
    货币基金具体的收益计算方式是：
    货币基金收益=已确认金额/10000*当日万分收益。
    另外，货币基金每日公布一次收益，周末及节假日，通常在节后首个交易日公布周末或这节假日期间的累计收益。
    """
    indicator_list=["万份收益","7日年化%"]
    if indicator not in indicator_list:
        print("  #Warning(mmf_rank_china): unsupported indicator",indicator)
        print("  Supported indicators:",indicator_list)
        #indicator="7日年化%"
        return None
    
    print("Searching for money market fund (OEF) information in China ...")
    #import akshare as ak   
    #import pandas as pd
    
    #获取货币型基金实时信息
    df = ak.fund_money_fund_daily_em()
    collist=list(df)
    nvname1=collist[2]
    nvname2=collist[3]
    if df[nvname1].eq('').all() or df[nvname1].eq('---').all():
        nvname1=collist[5]
        nvname2=collist[6]
        
    nvdate=nvname1[:10]
    
    #修改列名
    df.rename(columns={nvname1:'万份收益',nvname2:'7日年化%'}, inplace=True) 
    #dfa=df.drop(df[df['7日年化%']==''].index)
    dfb=df[['基金代码','基金简称','万份收益','7日年化%','成立日期','基金经理','手续费']].copy()
    dfb=dfb[dfb['7日年化%'] != '---']
    
    if indicator=='7日年化%':
        dfb.sort_values(by=['7日年化%'],ascending=False,inplace=True)
        dfprint=dfb[['基金简称','基金代码','7日年化%','万份收益']].copy()
        titletxt="中国货币型基金排名：7日年化收益率"
    if indicator=='万份收益':
        dfb.sort_values(by=['万份收益'],ascending=False,inplace=True)
        dfprint=dfb[['基金简称','基金代码','万份收益','7日年化%']].copy()
        titletxt="中国货币型基金排名：万份收益金额(元)"
    
    if len(dfprint)==0:
        print("  #Warning(mmf_rank_china): zero records found for",indicator)
        return None
        
    #设置打印
    dfprint.dropna(inplace=True)
    dfprint.reset_index(drop=True,inplace=True)
    dfprint.index=dfprint.index + 1
    
    collist=list(dfprint)
    dfprint['序号']=dfprint.index
    dfprint=dfprint[['序号']+collist]
    
    if rank >0:
        dfprint10=dfprint.head(rank)
        order="前"
    else:
        dfprint10=dfprint.tail(-rank)
        order="后"
    titletxt=titletxt+"("+order+str(abs(rank))+"名，降序)"

    footnote1="披露信息的货币型基金数量："+str(len(dfprint))+'，'
    footnote2=str(nvdate)+'\n'
    import datetime; todaydt = datetime.date.today()
    footnote3="数据来源：新浪财经/天天基金，"+str(todaydt)+"统计"
    footnote=footnote1+footnote2+footnote3
    
    df_display_CSS(dfprint10,titletxt=titletxt,footnote=footnote,facecolor='papayawhip',decimals=4, \
                       first_col_align='center',second_col_align='left', \
                       last_col_align='right',other_col_align='right', \
                       titile_font_size='16px',heading_font_size='15px', \
                       data_font_size='15px')    
    
    return df

if __name__=='__main__':
     df=mmf_rank_china()

#==============================================================================
if __name__=='__main__':
    fund='320019.SS'
    fromdate='2020-1-1'
    todate='2020-10-16'
    power=0

def mmf_trend_china(ticker,start,end='today',indicator='7日年化%',power=0, \
                    average_value=True,facecolor='whitesmoke'):
    """
    功能：货币型基金业绩趋势，7日年化收益率
    """
    fund=ticker
    
    fromdate,todate=start_end_preprocess(start,end)
    #检查日期
    result,start,end=check_period(fromdate,todate)
    if not result:
        print("  #Error(mmf_trend_china): invalid date period:",fromdate,todate)
        return None
    import datetime; todaydt = datetime.date.today()
    startdate=datetime.datetime.strftime(start,"%Y-%m-%d")
    enddate=str(datetime.datetime.strftime(end,"%Y-%m-%d"))
    
    print("Searching for money market fund (MMF) info in China ...")
    #import akshare as ak   
    #import pandas as pd

    #基金历史数据
    source=texttranslate("数据来源：东方财富/天天基金")
    
    #绘制收益率单线图
    fund1=fund[:6]
    df = ak.fund_money_fund_info_em(fund1)
    df['7日年化%']=df['7日年化收益率'].astype("float")
    df['万份收益']=df['每万份收益'].astype("float")

    df.sort_values(by=['净值日期'],ascending=True,inplace=True)
    
    df['date']=pd.to_datetime(df['净值日期'])
    df.set_index(['date'],inplace=True) 
    
    dfp = df[(df.index >= startdate)]
    dfp = dfp[(dfp.index <= enddate)]    
    if len(dfp) == 0:
        print("  #Error(mmf_trend_china): no info found for",fund,"in the period:",fromdate,todate)
        return    
    
    if indicator=='7日年化%':
        colname='7日年化%'; collabel='7日年化%'
    else:
        colname='万份收益'; collabel="万份收益（元）"
        
    ylabeltxt=''
    titletxt="货币型基金的收益趋势："+get_fund_name_china2(fund)+"，"+collabel
    footnote=source+', '+str(todaydt)
    plot_line(dfp,colname,collabel,ylabeltxt,titletxt,footnote,power=power, \
              average_value=average_value,facecolor=facecolor)    
    
    return df
    
#==============================================================================
if __name__=='__main__':
    indicator='单位净值'
    
    fund_type='全部类型'
    fund_type='股票'
    fund_type='固收'
    fund_type='海外'
    rank=10

def etf_rank_china(indicator='单位净值',fund_type='全部类型',rank=5, \
                   DEBUG=False):
    """
    功能：中国ETF基金排名，单位净值，累计净值，手续费
    """
    info_type=indicator
    
    typelist=['单位净值','累计净值','市价','增长率']
    if info_type not in typelist:
        print("  #Error(etf_rank_china): unsupported indicator",info_type)
        print("  Supported indicators:",typelist)
        return None
    
    print("Searching for exchange traded fund (ETF) info in China ...")
    #import akshare as ak   
    
    #获取ETF基金实时信息
    df1 = ak.fund_etf_fund_daily_em()
    if DEBUG:
        print(f"\n=== df1")
        display(df1)
    #删除全部为空值'---'的列
    df1t=df1.T
    df1t['idx']=df1t.index
    df1t.drop_duplicates(subset=['idx'],keep='last',inplace=True)
    df2=df1t.T
    #删除空值'---'的列
    
    #提取净值日期
    collist=list(df2)
    nvname1=collist[3]
    nvname2=collist[4]
    if df2[nvname1].eq('').all() or df2[nvname1].eq('---').all():
        nvname1=collist[5]
        nvname2=collist[6]
    nvdate=nvname1[:10]
    
    if DEBUG:
        print(f"\n=== df2")
        display(df2)
    
    #修改列名
    df3=df2.rename(columns={nvname1:'单位净值',nvname2:'累计净值'}) 
    # 过滤idx行
    df3=df3[df3.index != 'idx']

    #筛选列，不全为0
    df3=df3.replace('---',0)
    if df3['单位净值'].eq(0).all():
        # 获取所有包含"单位净值"的列名
        matched_columns = [col for col in df3.columns if "单位净值" in col]
        second_column = matched_columns[1]  # 索引1表示第二个元素
        df3['单位净值']=df3[second_column]
        nvdate=second_column[:10]
        
    if df3['累计净值'].eq(0).all():
        # 获取所有包含"累计净值"的列名
        matched_columns = [col for col in df3.columns if "累计净值" in col]
        second_column = matched_columns[1]  # 索引1表示第二个元素
        df3['累计净值']=df3[second_column] 
        nvdate=second_column[:10]
        
    if DEBUG:
        print(f"\n=== df3")
        display(df3)
    
    df=df3[['基金简称','基金代码','类型','单位净值','累计净值','增长率','市价']].copy()
        
    if DEBUG:
        print(f"\n=== df: not filtered by {fund_type}")
        display(df)
    
    #过滤基金类型
    if fund_type != '全部类型':
        fundtypelist0=list(set(list(df['类型'])))
        # 去掉列表可能出现的nan
        fundtypelist = [x for x in fundtypelist0 if not pd.isna(x)]

        df = df.dropna(subset=['类型'])  # 直接删除'类型'列中包含NaN的行，否则出错
        if fund_type == 'QDII':
            fund_type = '海外'
        if fund_type in ['债券','债券型']:
            fund_type = '固收'            
        if fund_type in ['股票型']:
            fund_type = '股票'    
        if fund_type in ['其他型']:
            fund_type = '其他'  
        
        found=False
        for ft in fundtypelist:
            if fund_type in ft: 
                found=True
                break
        if not found:
            print("  #Error(etf_rank_china): unsupported fund type",fund_type)
            print("  Supported fund types:",fundtypelist)
            return None
            
        df['基金类型s']=df['类型'].apply(lambda x: fund_type in x)
        df=df[df['基金类型s']==True]  
        
    if DEBUG:
        print(f"\n=== df: filtered by {fund_type}")
        display(df)
    
    if info_type == '单位净值':
        df['单位净值']=df['单位净值'].astype(float)
        df.sort_values(by=['单位净值'],ascending=False,inplace=True)
        dfprint=df[['基金简称','基金代码','类型','单位净值','市价']].copy()
        titletxt="中国ETF基金排名：单位净值"
        dfprint=dfprint[dfprint['单位净值'] != 0]
    
    if info_type == '累计净值':
        df['累计净值']=df['累计净值'].astype(float)
        df.sort_values(by=['累计净值'],ascending=False,inplace=True)
        dfprint=df[['基金简称','基金代码','类型','累计净值','单位净值']].copy()
        titletxt="中国ETF基金排名：累计净值"
        dfprint=dfprint[dfprint['累计净值'] != 0]
    
    if info_type == '市价':
        df['市价']=df['市价'].astype(float)
        df.sort_values(by=['市价'],ascending=False,inplace=True)
        dfprint=df[['基金简称','基金代码','类型','市价','单位净值']].copy()
        titletxt="中国ETF基金排名：市价"   
        dfprint=dfprint[dfprint['市价'] != 0]
    
    if info_type == '增长率':
        df['增长率']=df['增长率'].astype(str)
        df.sort_values(by=['增长率'],ascending=False,inplace=True)
        dfprint=df[['基金简称','基金代码','类型','增长率','市价','单位净值']].copy()
        titletxt="中国ETF基金排名：增长率"
        dfprint=dfprint[dfprint['增长率'] != 0]
        
    dfprint.reset_index(drop=True,inplace=True)
    dfprint.index=dfprint.index + 1
        
    if DEBUG:
        print(f"\n=== dfprint")
        display(dfprint)
    
    collist=list(dfprint)
    dfprint['序号']=dfprint.index
    dfprint=dfprint[['序号']+collist]
    
    if rank >=0:
        dfprint10=dfprint.head(rank)
        order="前"
    else:
        dfprint10=dfprint.tail(-rank)
        order="后"
        
    if DEBUG:
        print(f"\n=== dfprint10")
        display(dfprint)
        
    titletxt=titletxt+"（"+order+str(abs(rank))+"名，降序排列）"
        
    footnote1="披露净值信息的ETF基金数量："+str(len(dfprint))+'，'
    footnote2="基金类型："+str(fund_type)+'\n'
    footnote3="披露日期："+str(nvdate)+'，'
    import datetime; todaydt = datetime.date.today()
    footnote4="数据来源：东方财富/天天基金，"+str(todaydt)
    footnote=footnote1+footnote2+footnote3+footnote4
    
    df_display_CSS(dfprint10,titletxt=titletxt,footnote=footnote,facecolor='papayawhip',decimals=3, \
                       first_col_align='center',second_col_align='left', \
                       last_col_align='right',other_col_align='right', \
                       titile_font_size='16px',heading_font_size='15px', \
                       data_font_size='15px')
    
    return dfprint

if __name__=='__main__':
     df=etf_rank_china(info_type='单位净值',fund_type='全部类型')
     df=etf_rank_china(info_type='累计净值')
     df=etf_rank_china(info_type='市价')

#==============================================================================
if __name__=='__main__':
    ticker='159922.SS'
    ticker='510580'
    start='2025-1-1'
    end='2025-5-30'

def etf_trend_china(ticker,start,end='today',indicator='净值',power=0, \
                    average_value=True,facecolor='whitesmoke', \
                    loc1='best',loc2='best',twinx=False,graph=True):
    """
    功能：ETF基金业绩趋势，单位净值，累计净值
    """
    fund=ticker
    fromdate,todate=start_end_preprocess(start,end)
    
    indicator_list=['净值','单位净值','累计净值']
    if indicator not in indicator_list:
        indicator='净值'
    
    #检查日期
    result,start,end=check_period(fromdate,todate)
    if not result:
        print("  #Error(oef_trend_china): invalid date period:",fromdate,todate)
        return None
    #转换日期格式
    import datetime; todaydt = datetime.date.today()
    startdate=str(datetime.datetime.strftime(start,"%Y-%m-%d"))
    enddate=str(datetime.datetime.strftime(end,"%Y-%m-%d"))

    print("Searching for exchange traded fund (ETF) trend info in China ...")
    #import akshare as ak   
    #import pandas as pd

    source=texttranslate("数据来源：东方财富/天天基金")
    
    #获取基金数据
    fund1=fund[:6]
    df = ak.fund_etf_fund_info_em(fund1)
    df['date']=pd.to_datetime(df['净值日期'])
    df.set_index(['date'],inplace=True) 
    df['单位净值']=df['单位净值'].astype("float")
    df['累计净值']=df['累计净值'].astype("float")
    
    df['净值日期']=df['净值日期'].apply(lambda x: pd.to_datetime(x))        
    dfp=df[(df['净值日期'] >= start)]
    dfp=dfp[(dfp['净值日期'] <= end)]
    if len(dfp) == 0:
        print("  #Error(etf_trend_china): no info found for",fund,"in the period:",fromdate,todate)
        return    
        
    #绘制双线图
    if graph:
        ticker1=fund1; colname1='单位净值';label1=texttranslate('单位净值')
        ticker2=fund1; colname2='累计净值';label2=texttranslate('累计净值')
        titletxt=texttranslate("ETF基金的净值趋势：")+get_fund_name_china2(fund)
        footnote=source+', '+str(todaydt)

        if indicator=='净值':
            ylabeltxt=texttranslate('净值（元）')
            plot_line2(dfp,ticker1,colname1,label1, \
                       dfp,ticker2,colname2,label2, \
                       ylabeltxt,titletxt,footnote, twinx=twinx, \
                       facecolor=facecolor,loc1=loc1,loc2=loc2)
    
        if indicator=='单位净值':  
            ylabeltxt=texttranslate('单位净值（元）')
            plot_line(dfp,colname1,label1,ylabeltxt,titletxt,footnote,power=power,loc=loc1, \
                      average_value=average_value,facecolor=facecolor)    
    
        if indicator=='累计净值':  
            ylabeltxt=texttranslate('累计净值（元）')
            plot_line(dfp,colname2,label2,ylabeltxt,titletxt,footnote,power=power,loc=loc1, \
                      average_value=average_value,facecolor=facecolor)    
    
    return dfp
    
if __name__=='__main__':
    df=etf_trend_china('510580','2019-1-1','2020-9-30')
    
#==============================================================================

def fund_summary_china(rank=10):
    """
    功能：中国基金投资机构概况（AMAC会员单位）
    爬虫来源地址：https://zhuanlan.zhihu.com/p/97487003
    """
    print("Searching for investment fund institutions in China ...")
    #import akshare as ak

    #会员机构综合查询：
    #机构类型：'商业银行','支付结算机构','证券公司资管子公司','会计师事务所',
    #'保险公司子公司','独立服务机构','证券投资咨询机构','证券公司私募基金子公司',
    #'私募基金管理人','公募基金管理公司','地方自律组织','境外机构','期货公司',
    #'独立第三方销售机构','律师事务所','证券公司','其他机构','公募基金管理公司子公司',
    #'期货公司资管子公司','保险公司'
    try:
        amac_df = ak.amac_member_info()
    except:
        print("  #Error(fund_summary_china): data source tentatively inaccessible, try later")
        return None
    
    """    
    typelist=['公募基金管理公司','公募基金管理公司子公司','私募基金管理人', \
                '期货公司','期货公司资管子公司','证券公司', \
                '证券公司私募基金子公司','证券公司资管子公司','境外机构']
    """
    typelist=list(set(list(amac_df["机构类型"])))
    
    #import pandas as pd
    titletxt="中国基金机构类型与分布（AMAC会员单位，前"+str(rank)+"名）"
    
    amac_sum_df=pd.DataFrame(columns=['机构类型','机构数量','数量占比%'])
    totalnum=0
    for t in typelist:
        df_sub=amac_df[amac_df['机构类型']==t]
        n=len(list(set(list(df_sub['机构（会员）名称']))))
        if n==0: continue
        totalnum=totalnum+n
        
        s=pd.Series({'机构类型':t,'机构数量':n})
        try:
            amac_sum_df=amac_sum_df.append(s,ignore_index=True)
        except:
            amac_sum_df=amac_sum_df._append(s,ignore_index=True)        
    
    amac_sum_df['数量占比%']=amac_sum_df['机构数量'].apply(lambda x: round(x/totalnum*100,2))
    
    amac_sum_df.sort_values(by=['机构数量'],ascending=False,inplace=True)
    amac_sum_df.reset_index(drop=True,inplace=True)        
    amac_sum_df.index=amac_sum_df.index + 1  
    
    collist=list(amac_sum_df)
    amac_sum_df['序号']=amac_sum_df.index
    amac_sum_df=amac_sum_df[['序号']+collist]
    
    df10=amac_sum_df.head(rank)

    footnote1="共有"+str(len(typelist))+'个类型，'
    footnote2=str(totalnum)+'家AMAC会员机构；'
    footnote3="表中类型数量占比"+str(round(df10['机构数量'].sum()/totalnum*100,2))+'%\n'
    
    import datetime; todaydt = datetime.date.today()
    footnote9="数据来源：中国证券投资基金业协会（AMAC），"+str(todaydt)
    footnote=footnote1+footnote2+footnote3+footnote9
    
    df_display_CSS(df10,titletxt=titletxt,footnote=footnote,facecolor='papayawhip',decimals=2, \
                       first_col_align='center',second_col_align='left', \
                       last_col_align='right',other_col_align='right', \
                       titile_font_size='16px',heading_font_size='15px', \
                       data_font_size='15px')
    
    return amac_df


#==============================================================================
if __name__=='__main__':
    location='全国'
    df=pef_manager_china(location='全国')

def pef_manager_china(location='全国'):
    """
    功能：中国私募基金管理人地域分布概况
    爬虫来源地址：https://zhuanlan.zhihu.com/p/97487003
    """
    
    print("Searching for private equity fund (PEF) managers info in China ...")
    #import akshare as ak
    #import pandas as pd

    #私募基金管理人综合查询
    manager_df = ak.amac_manager_info()
    num=len(list(manager_df["法定代表人/执行事务合伙人(委派代表)姓名"]))
    
    #注册地检查
    if location != '全国':
        typelist=sort_pinyin(list(set(list(manager_df['注册地']))))
        typelist.remove('')
        if location not in typelist:
            print("  #Error(pef_manager_china): failed to find registration place-"+location)
            print("  Supported registration place：",typelist+['全国'])
            return

    #设置打印对齐
    pd.set_option('display.max_columns', 1000)
    pd.set_option('display.width', 1000)
    pd.set_option('display.max_colwidth', 1000)
    pd.set_option('display.unicode.ambiguous_as_wide', True)
    pd.set_option('display.unicode.east_asian_width', True)

    import datetime; today = datetime.date.today()
    source=texttranslate("数据来源：中国证券投资基金业协会")
    footnote=source+', '+str(today)          
    
    if location != '全国':
        manager_df=manager_df[manager_df['注册地']==location]
        print(texttranslate("\n===== 中国私募基金管理人角色分布 ====="))
        print(texttranslate("地域：")+location)
        print(texttranslate("法定代表人/执行合伙人数量："),end='')
        num1=len(list(manager_df["法定代表人/执行事务合伙人(委派代表)姓名"]))
        print("{:,}".format(num1),texttranslate('\b, 占比全国'),round(num1/num*100.0,2),'\b%')
        
        print(texttranslate("其中, 角色分布："))
        #instlist=list(set(list(manager_df['机构类型'])))
        instlist=['私募股权、创业投资基金管理人','私募证券投资基金管理人','私募资产配置类管理人','其他私募投资基金管理人']
        mtype=pd.DataFrame(columns=['管理人类型','人数','占比%'])
        for t in instlist:
            df_sub=manager_df[manager_df['机构类型']==t]
            n=len(list(df_sub['法定代表人/执行事务合伙人(委派代表)姓名']))
            pct=round(n/num1*100,2)
            s=pd.Series({'管理人类型':t,'人数':n,'占比%':pct})
            try:
                mtype=mtype.append(s,ignore_index=True)
            except:
                mtype=mtype._append(s,ignore_index=True)
        mtype.sort_values(by=['人数'],ascending=False,inplace=True)
        mtype.reset_index(drop=True,inplace=True)        
        mtype.index=mtype.index + 1
        
        print(mtype)
        print(footnote)
        return manager_df
    
    print(texttranslate("\n===== 中国私募基金管理人地域分布概况 ====="))
    print(texttranslate("法定代表人/执行合伙人数量："),end='')
    num=len(list(manager_df["法定代表人/执行事务合伙人(委派代表)姓名"]))
    print("{:,}".format(num))  
        
    typelist=sort_pinyin(list(set(list(manager_df['注册地']))))
    typelist.remove('')
        
    print(texttranslate("其中分布在："))
    location=pd.DataFrame(columns=['注册地','人数','占比%'])
    for t in typelist:
        df_sub=manager_df[manager_df['注册地']==t]
        n=len(list(df_sub['法定代表人/执行事务合伙人(委派代表)姓名']))
        pct=round(n/num*100,2)
        s=pd.Series({'注册地':t,'人数':n,'占比%':pct})
        try:
            location=location.append(s,ignore_index=True)
        except:
            location=location._append(s,ignore_index=True)
    location.sort_values(by=['人数'],ascending=False,inplace=True)
        
    location.reset_index(drop=True,inplace=True)
    location.index=location.index + 1
    
    location10=location.head(10)
    pctsum=round(location10['占比%'].sum(),2)
    
    print(location10)
    print(texttranslate("上述地区总计占比:"),pctsum,'\b%')
    print(footnote)             
    
    """
    print("\n===== 中国私募基金管理人角色分布 =====")
    print("地域："+location)
    print("法定代表人/执行合伙人数量：",end='')
    num1=len(list(manager_df["法定代表人/执行事务合伙人(委派代表)姓名"]))
    print("{:,}".format(num1),'\b, 占比全国',round(num1/num*100.0,2),'\b%')
        
    print("其中, 角色分布：")
    #instlist=list(set(list(manager_df['机构类型'])))
    instlist=['私募股权、创业投资基金管理人','私募证券投资基金管理人','私募资产配置类管理人','其他私募投资基金管理人']
    mtype=pd.DataFrame(columns=['管理人类型','人数','占比%'])
    for t in instlist:
        df_sub=manager_df[manager_df['机构类型']==t]
        n=len(list(df_sub['法定代表人/执行事务合伙人(委派代表)姓名']))
        pct=round(n/num1*100,2)
        s=pd.Series({'管理人类型':t,'人数':n,'占比%':pct})
        mtype=mtype.append(s,ignore_index=True) 
    mtype.sort_values(by=['人数'],ascending=False,inplace=True)
    mtype.reset_index(drop=True,inplace=True)        
        
    print(mtype)
    print(footnote)
    """
    
    return manager_df


#==============================================================================
if __name__=='__main__':
    start_page=1
    end_page=10
    step_pages=5
    DEBUG=True
    
    df,failedpages=get_pef_product_china_pages(start_page,end_page,step_pages)

def get_pef_product_china_pages(start_page,end_page,step_pages,DEBUG=True):   
    """
    功能：获取中国私募基金产品运营方式和状态信息，指定页数范围和页数跨度
    返回：获取的数据，失败的页数范围列表。
    """
    #DEBUG=DEBUG
    if DEBUG:
        print("  Starting to retrieve pef info from",start_page,"to",end_page,"by every",step_pages,"pages ...")
   
    #import akshare as ak
    #import pandas as pd
    
    df=pd.DataFrame()
    pg=start_page
    failedpages=[]
    while pg <= end_page:
        pg_end=pg+step_pages-1
        try:
            if DEBUG:
                print("    Getting pef info from page",pg,"to",pg_end)
            dft = ak.amac_fund_info(start_page=str(pg),end_page=str(pg_end))
            
            if len(df)==0:
                df=dft
            else:
                #df=df.append(dft)
                df=pd.concat([df,dft],ignore_index=True)
        except:
            if DEBUG:
                print("  Warning: failed to get pef pages from",pg,'to',pg_end)
            failedpages=failedpages+[[pg,pg_end]]
        
        pg=pg_end + 1
    
    if DEBUG:
        print('\n',end='')
        print("  Successfully retrieved pef info",len(df),"records, with failed page range",len(failedpages),'pairs')

    return df,failedpages


if __name__=='__main__':
    start_page = 1
    retry_num = 5
    DEBUG = False
    
    df1p=get_pef_product_china_1page(1)
    
def get_pef_product_china_1page(start_page,retry_num=5,max_sleep=30,DEBUG=False):   
    """
    功能：获取中国私募基金产品运营方式和状态信息，指定页号，每次1页
    返回：获取的数据。
    """
    if DEBUG:
        print("  Retrieving pef info on page",start_page,"...")

    # 这个方法可以有效屏蔽akshare中tqdm输出进度信息，又不产生副作用！！！
    from IPython.utils import io
    def get_data_silent(*args, **kwargs):
        # capture_output 会拦截所有 print() 和 sys.stderr.write()
        with io.capture_output() as captured:
            result = ak.amac_fund_info(*args, **kwargs)
        return result    
    
    #import pandas as pd
    df=pd.DataFrame()
    
    pg=start_page
    i = 1
    for i in range(retry_num):
        try:
            df = get_data_silent(start_page=str(pg),end_page=str(pg))
        except:
            if DEBUG:
                print("  #Warning(get_pef_product_china_1page): failed to get pef on page",pg)
            
            # API 出错，无法继续
            return df
        
        if len(df) > 0:
            # 成功获取到数据，退出循环
            break
        
        # 未获取到数据，随机睡眠后再试
        sleep_random(max_sleep)
    
    if DEBUG:
        if len(df) > 0:
            print("  Successfully retrieved pef info",len(df),"records on page",pg)
        else:
            print("  Eventually failed to retrieve pef info on page",pg)

    return df

if __name__=='__main__':
    start_page=1
    end_page=5
    page_stop=5
    retry_num=5
    max_sleep=30
    DEBUG=False
    
    dfmp=get_pef_product_china_mpages(1,5)
    
def get_pef_product_china_mpages(start_page,end_page, \
                                 page_stop=10, \
                                 retry_num=5,max_sleep=30,DEBUG=False):   
    """
    功能：获取中国私募基金产品运营方式和状态信息，指定页数范围和页数跨度
    返回：获取的数据，失败的页数范围列表。
    """
    if DEBUG:
        print("  Starting to retrieve pef info from page",start_page,"to",end_page,"...")
    
    ##import pandas as pd
    df=pd.DataFrame()
    
    pg=start_page; pg_end=end_page
    page_stop_count=0
    failedpages=[]
    for i in range(pg,pg_end+1):
        dft=get_pef_product_china_1page(start_page=i,retry_num=retry_num, \
                                        max_sleep=max_sleep,DEBUG=DEBUG)
        
        if len(dft) > 0:
            if len(df)==0:
                df=dft
            else:
                df=pd.concat([df,dft],ignore_index=True)
        else:
            failedpages=failedpages+[i]
            # 遇到page_stop个空页后停止
            page_stop_count=page_stop_count+1
            if page_stop_count > page_stop:
                break
            
        #print_progress_bar(i,pg,pg_end)
        print_progress_percent(i - pg,pg_end - pg,steps=10,leading_blanks=2)
        #print_progress_percent2(i,total_list,steps=5,leading_blanks=4)
    
    if DEBUG:
        print('\n',end='')
        print(f"  Successfully retrieved {len(df)} pef records from page {start_page} to {end_page}")
        if len(failedpages) > 0:
            print(f"  Notice: encountered {len(failedpages)} failed pages from page {start_page} to {end_page}")

    return df,failedpages

#==============================================================================
if __name__=='__main__':
    max_pages=2000
    step_page_list=[100,10,1]
    DEBUG=True

def get_pef_product_china(max_pages=2000,step_page_list=[100,20,1],DEBUG=True):   
    """
    功能：获取中国私募基金产品运营方式和状态信息，耗时较长
    注意：由于获取过程极易失败，因此分割为三个阶段进行下载，然后合成。
    """
    print("  Downloading in pages, which may take hours upon internet quality")
    print("  ONLY recommend to run this command under high-speed wired network")
    print("  If failed, RESTART Python kernel or even Jupyter, then run again")
    #import pandas as pd
    
    # 第1步：页数跨度最大
    per_step=1
    step_pages=step_page_list[per_step-1]
    df1,failedpages1=get_pef_product_china_pages(start_page=1,end_page=max_pages,step_pages=step_pages,DEBUG=DEBUG)
    
    # 第2步：页数跨度第二大
    per_step=2
    df2=df1.copy(deep=True)
    failedpages2=[]
    
    if len(failedpages1) > 0:
        
        step_pages=step_page_list[per_step-1]
        
        for fp in failedpages1:
            start_page=fp[0]
            end_page=fp[1]
            
            dft,failedpagest=get_pef_product_china_pages(start_page=start_page,end_page=end_page,step_pages=step_pages,DEBUG=DEBUG)
            if len(dft) > 0:
                #df1=df1.append(dft)
                df2=pd.concat([df2,dft],ignore_index=True)
                
            if len(failedpagest) > 0:
                failedpages2=failedpages2+failedpagest
    
    # 第3步：页数跨度小
    per_step=3
    df3=df2.copy(deep=True)
    failedpages3=[]
    
    if len(failedpages2) > 0:
        
        step_pages=step_page_list[per_step-1]
        
        for fp in failedpages2:
            start_page=fp[0]
            end_page=fp[1]
            
            dft,failedpagest=get_pef_product_china_pages(start_page=start_page,end_page=end_page,step_pages=step_pages,DEBUG=DEBUG)
            if len(dft) > 0:
                #df1=df1.append(dft)
                df3=pd.concat([df3,dft],ignore_index=True)
                
            if len(failedpagest) > 0:
                failedpages3=failedpages3+failedpagest

    if DEBUG:
        print("  Finally retrieved pef info",len(df3),"records, with failed pages",failedpages3)
    
    return df3


#==============================================================================
if __name__=='__main__':
    rank=10
    max_pages=15
    facecolor='papayawhip'
    DEBUG=False
    
    

def pef_product_china(rank=10,max_pages=2500, \
                      facecolor='papayawhip',DEBUG=False):
    
    """
    功能：中国私募基金管理人的产品管理概况
    爬虫来源地址：https://zhuanlan.zhihu.com/p/97487003
    注意：下载数据需要极长时间，需要网络非常非常稳定（建议高速有线网），谨慎运行！
    """
    
    print("Searching for private equity fund (PEF) info in China ...")
    print("It may take up to hours upon internet quality, please wait ...")
    #import pandas as pd

    #私募基金管理人基金产品
    #product_df = get_pef_product_china(max_pages=max_pages,step_page_list=[page_size,page_num,1],DEBUG=DEBUG)
    product_df,_ = get_pef_product_china_mpages(1,max_pages, \
                                     page_stop=10, \
                                     retry_num=5,max_sleep=5,DEBUG=DEBUG)
    
    product_df['私募基金管理人类型']=product_df['私募基金管理人类型'].apply(lambda x: '方式不明' if x=='' or x is None else x)
    product_df['运行状态']=product_df['运行状态'].apply(lambda x: '状态不明' if x=='' or x is None else x)
    
    #num=len(list(product_df["基金名称"])) #统计可能有问题，原因不明
    #footnote1="找到产品数量："+str("{:,}".format(num))+'\n'
    import datetime; todaydt = datetime.date.today()
    footnote9="数据来源：中国证券投资基金业协会，"+str(todaydt)       
    
    # 产品运营方式==============================================================
    titletxt="中国私募基金管理人的产品运营方式"

    #typelist=['受托管理','顾问管理','自我管理']
    typelist=list(set(list(product_df['私募基金管理人类型'])))
    dfprint=pd.DataFrame(columns=['运营方式','产品数量','数量占比%'])
    totalnum=0
    for t in typelist:
            df_sub=product_df[product_df['私募基金管理人类型']==t]
            n=len(list(set(list(df_sub['基金名称']))))
            totalnum=totalnum+n
            
            s=pd.Series({'运营方式':t,'产品数量':n})
            try:
                dfprint=dfprint.append(s,ignore_index=True)
            except:
                dfprint=dfprint._append(s,ignore_index=True) 
                
    dfprint['数量占比%']=dfprint['产品数量'].apply(lambda x: round(x/totalnum*100,3))
    dfprint['产品数量']=dfprint['产品数量'].apply(lambda x: str("{:,}".format(x)))
    
    dfprint.sort_values(by=['数量占比%'],ascending=False,inplace=True)
    dfprint.reset_index(drop=True,inplace=True)        
    dfprint.index=dfprint.index + 1 
    collist=list(dfprint)
    dfprint['序号']=dfprint.index
    dfprint=dfprint[['序号']+collist]

    footnote1="找到管理产品"+str("{:,}".format(totalnum))+'个\n'
    footnote=footnote1+footnote9

    print('')
    df_display_CSS(dfprint,titletxt=titletxt,footnote=footnote,facecolor=facecolor,decimals=3, \
                       first_col_align='center',second_col_align='left', \
                       last_col_align='right',other_col_align='right', \
                       titile_font_size='16px',heading_font_size='15px', \
                       data_font_size='15px')                
                
    #运营状态===================================================================
    titletxt="中国私募基金管理人的产品运营状态"
    typelist=list(set(list(product_df['运行状态'])))
    dfprint=pd.DataFrame(columns=['运营状态','产品数量','数量占比%'])  
    #totalnum=0
    for t in typelist:
            df_sub=product_df[product_df['运行状态']==t]
            n=len(list(set(list(df_sub['基金名称']))))
            if n==0: continue
            #totalnum=totalnum+n
            
            s=pd.Series({'运营状态':t,'产品数量':n})
            try:
                dfprint=dfprint.append(s,ignore_index=True)
            except:
                dfprint=dfprint._append(s,ignore_index=True)               
                
    dfprint['数量占比%']=dfprint['产品数量'].apply(lambda x: round(x/totalnum*100,3))
    dfprint['产品数量']=dfprint['产品数量'].apply(lambda x: str("{:,}".format(x)))
    
    dfprint.sort_values(by=['数量占比%'],ascending=False,inplace=True)
    dfprint.reset_index(drop=True,inplace=True)        
    dfprint.index=dfprint.index + 1 
    collist=list(dfprint)
    dfprint['序号']=dfprint.index
    dfprint=dfprint[['序号']+collist]

    footnote1="找到运营产品"+str("{:,}".format(totalnum))+'个\n'
    footnote=footnote1+footnote9

    print('')                
    df_display_CSS(dfprint,titletxt=titletxt,footnote=footnote,facecolor=facecolor,decimals=3, \
                       first_col_align='center',second_col_align='left', \
                       last_col_align='right',other_col_align='right', \
                       titile_font_size='16px',heading_font_size='15px', \
                       data_font_size='15px')  
        
    #推出产品数量排行===========================================================
    titletxt="中国推出产品数量最多的私募基金管理人（前"+str(rank)+"名）"
    pef_num=len(set(list(product_df['私募基金管理人名称'])))
    subttl=pd.DataFrame(product_df.groupby(by=['私募基金管理人名称'])['基金名称'].count())
    subttl.rename(columns={'基金名称':'产品数量'}, inplace=True)
    subttl['数量占比‰']=round(subttl['产品数量']/totalnum*1000.0,2)
    subttl.sort_values(by=['产品数量'],ascending=False,inplace=True)
    subttl.reset_index(inplace=True)
    
    subttl.index=subttl.index + 1
    subttl10=subttl.head(rank)
    
    dfprint=subttl10
    dfprint.sort_values(by=['数量占比‰'],ascending=False,inplace=True)
    dfprint.reset_index(drop=True,inplace=True)        
    dfprint.index=dfprint.index + 1 
    collist=list(dfprint)
    dfprint['序号']=dfprint.index
    dfprint=dfprint[['序号']+collist]
    
    pctsum=round(subttl10['数量占比‰'].sum(),2)   
    footnote1="找到私募基金管理人"+str("{:,}".format(pef_num))+"家公司，找到产品"+str("{:,}".format(totalnum))+"个，上述产品合计占比"+str(pctsum)+'‰'+'\n'
    footnote=footnote1+footnote9
    
    print('')
    df_display_CSS(dfprint,titletxt=titletxt,footnote=footnote,facecolor=facecolor,decimals=2, \
                       first_col_align='center',second_col_align='left', \
                       last_col_align='right',other_col_align='right', \
                       titile_font_size='16px',heading_font_size='15px', \
                       data_font_size='15px')      
    
    
    # 托管产品==================================================================
    titletxt="中国私募基金管理人的产品托管概况（前"+str(rank)+"名）"
    tnum=len(list(set(list(product_df['托管人名称']))))
    footnote1="找到产品"+str("{:,}".format(totalnum))+"个，托管机构"+str("{:,}".format(tnum))+'家\n'
    
    subttl=pd.DataFrame(product_df.groupby(by=['托管人名称'])['基金名称'].count())
    subttl.rename(columns={'基金名称':'产品数量'}, inplace=True)
    subttl.sort_values(by=['产品数量'],ascending=False,inplace=True)
    subttl.reset_index(inplace=True)
        
    subttl=subttl[subttl['托管人名称']!='']
    #subttl.drop(subttl.index[0], inplace=True)       # 删除第1行
    subttl.reset_index(drop=True,inplace=True)
    subttl['数量占比%']=round(subttl['产品数量']/totalnum*100.0,3)
    
    subttl.index=subttl.index + 1
    subttl10=subttl.head(rank)
        
    pctsum=round(subttl10['数量占比%'].sum(),2)
    #print(subttl10)
    #print(texttranslate("上述金融机构托管产品总计占比:"),pctsum,'\b%')
    footnote2="上述机构托管产品合计占比："+str(pctsum)+'%\n'
    footnote=footnote1+footnote2+footnote9
    
    dfprint=subttl10
    dfprint.sort_values(by=['数量占比%'],ascending=False,inplace=True)
    dfprint.reset_index(drop=True,inplace=True)        
    dfprint.index=dfprint.index + 1 
    collist=list(dfprint)
    dfprint['序号']=dfprint.index
    dfprint=dfprint[['序号']+collist]    

    print('')
    df_display_CSS(dfprint,titletxt=titletxt,footnote=footnote,facecolor=facecolor,decimals=3, \
                       first_col_align='center',second_col_align='left', \
                       last_col_align='right',other_col_align='right', \
                       titile_font_size='16px',heading_font_size='15px', \
                       data_font_size='15px')  
        
    return product_df   


#==============================================================================
#==============================================================================
if __name__=='__main__':
    fund_list=['510050.SS','510210.SS']
    start='2022-1-1'
    end='2022-10-31'
    ftype='单位净值'
    loc1='best'
    loc2='best'
    graph=True    

def compare_metf_china(fund_list,start,end,ftype='单位净值',graph=True):
    """
    功能：比较多只交易所基金的单位净值或累计净值，仅限中国内地
    """
    
    #检查日期期间的合理性
    result,startpd,endpd=check_period(start,end)
    if not result:
        print("  #Error(compare_metf): invalid date period",start,end)
        return None
    
    #检查净值类型
    typelist=['单位净值','累计净值']
    if not (ftype in typelist):
        print("  #Error(compare_metf): invalid fund value type",ftype)
        print("  Supported fund value type:",typelist)
        return None

    import os, sys
    class HiddenPrints:
        def __enter__(self):
            self._original_stdout = sys.stdout
            sys.stdout = open(os.devnull, 'w')

        def __exit__(self, exc_type, exc_val, exc_tb):
            sys.stdout.close()
            sys.stdout = self._original_stdout
    
    #循环获取基金净值
    #import pandas as pd
    fdf=pd.DataFrame()
    print("Searching for ETF fund information, please wait ...")
    for f in fund_list:
        
        f6=f[:6]
        try:
            with HiddenPrints():
                dft=etf_trend_china(f6,start,end,graph=False)
        except:
            print("  #Error(compare_metf): ETF fund not found for",f)
            return None
        
        dft2=pd.DataFrame(dft[ftype])
        dft2.rename(columns={ftype:get_fund_name_china2(f)}, inplace=True)
        if len(fdf)==0:
            fdf=dft2
        else:
            fdf=pd.merge(fdf,dft2,how='outer',left_index=True,right_index=True)
            
    #绘图
    y_label=ftype
    import datetime; todaydt = datetime.date.today()
    
    lang=check_language()
    if lang == 'English':
        x_label="Source: eastmoney/tiantian funds, "+str(todaydt)
        title_txt="Compare Multiple ETF Fund Performance"
    else:
        x_label="数据来源: 东方财富/天天基金，"+str(todaydt)
        title_txt="比较多只ETF基金的净值指标"

    draw_lines(fdf,y_label,x_label,axhline_value=0,axhline_label='',title_txt=title_txt, \
                   data_label=False,resample_freq='H',smooth=True)
        
    return fdf
    
if __name__=='__main__':
    fund_list=['510050.SS','510210.SS','510880.SS','510180.SS']
    fdf=compare_metf_china(fund_list,start,end,ftype='单位净值',graph=True)
    
#==============================================================================
#==============================================================================
#==============================================================================
#以下信息专注于中国内地基金信息，来源于akshare，尚未利用
#==============================================================================
def fund_info_china0():
    
    #证券公司集合资管产品
    cam_df = ak.amac_securities_info()
    
    #证券公司直投基金：
    #中国证券投资基金业协会-信息公示-私募基金管理人公示-基金产品公示-证券公司直投基金
    sdif_df = ak.amac_aoin_info()
    
    #证券公司私募投资基金
    speif_df = ak.amac_fund_sub_info()
    
    #证券公司私募基金子公司管理人信息
    spesub_manager_df = ak.amac_member_sub_info()
    
    #基金公司及子公司集合资管产品
    #中国证券投资基金业协会-信息公示-私募基金管理人公示-基金产品公示-基金公司及子公司集合资管产品
    sscam_df = ak.amac_fund_account_info()
    
    #期货公司集合资管产品
    #中国证券投资基金业协会-信息公示-私募基金管理人公示-基金产品公示-期货公司集合资管产品
    fccam_df = ak.amac_futures_info()
    
    #==========================================================================
    #以下为公募数据：
    
    #基金净值估算数据，当前获取在交易日的所有基金的净值估算数据
    #爬虫来源：https://zhuanlan.zhihu.com/p/140478554?from_voters_page=true
    #信息内容：基金代码，基金类型，单位净值，基金名称
    fnve_df = ak.fund_value_estimation_em()
    
    #挑选QDII产品
    fnve_list=list(set(list(fnve_df['基金类型'])))
    qdii=lambda x: True if 'QDII' in x else False
    fnve_df['is_QDII']=fnve_df['基金类型'].apply(qdii)
    fnve_qdii_df=fnve_df[fnve_df['is_QDII']==True]
    
    #基金持股：获取个股的基金持股数据
    #爬虫来源：https://my.oschina.net/akshare/blog/4428824
    #持股的基金类型：symbol="基金持仓"; choice of {"基金持仓", "QFII持仓", "社保持仓", "券商持仓", "保险持仓", "信托持仓"}
    #返回：单次返回指定 symbol 和 date 的所有历史数据
    df = ak.stock_report_fund_hold(symbol="基金持仓", date="20200630")
    
    ###Fama-French三因子回归A股实证（附源码）
    #代码来源：https://mp.weixin.qq.com/s?__biz=MzU5NDY0NDM2NA==&mid=2247486057&idx=1&sn=0fb3f8558da4e55789ce340c03b648cc&chksm=fe7f568ac908df9c22bae8b52207633984ec91ef7b2728eea8c6a75089b8f2db284e3d611775&scene=21#wechat_redirect

    ###Carhart四因子模型A股实证（附源码）
    #代码来源：https://my.oschina.net/akshare/blog/4340998
    
    #==========================================================================
    ###其他公募基金实时/历史行情
    #爬虫来源：https://cloud.tencent.com/developer/article/1624480
    
    ###########XXX理财型基金-实时数据
    #基金代码，基金简称，当前交易日-7日年化收益率，封闭期，申购状态
    wmf_df = ak.fund_financial_fund_daily_em()
    #理财型基金-历史数据
    #净值日期，7日年化收益率，申购状态，赎回状态
    wmf_hist_df = ak.fund_financial_fund_info_em("000134")
    
    ###########分级基金(结构化基金)-实时数据
    #基金代码，基金简称，单位净值，累计净值，市价，折价率，手续费
    gsf_df = ak.fund_graded_fund_daily_em()
    #分级基金-历史数据
    #净值日期，7日年化收益率，申购状态，赎回状态
    gsf_hist_df = ak.fund_graded_fund_info_em("150232")
    
    ###抓取沪深股市所有指数关联的公募基金列表（含ETF、增强、分级等）
    #代码来源：https://blog.csdn.net/leeleilei/article/details/106124894
    
    ###pyecharts绘制可伸缩蜡烛图
    #代码地址：https://segmentfault.com/a/1190000021999451?utm_source=sf-related
    
#==============================================================================
if __name__=='__main__':
    etflist=choose_etf_china(etf_type='股票型',startpos=0,endpos=10,printout=True)

def choose_etf_china(etf_type='股票型',startpos=0,endpos=10,printout=True):
    """
    功能：从数据库中挑选中国ETF基金
    输入：
    startpos=0,endpos=10：同型ETF列表的起始终止位置，同型ETF内部按照基金简称顺序排列
    输出：基金代码列表
    """    
    
    # 检查ETF类型
    etf_types=['股票型','债券型','商品型','货币型','QDII','全部']
    etf_type1=etf_type.upper()
    if not (etf_type1 in etf_types):
        print("  #Error(choose_etf_china): unsupported ETF type:",etf_type)
        print("  Supported ETF types:",etf_types)
        return None
    
    # 搜索处理ETF类型
    #import akshare as ak
    names = ak.fund_name_em()

    names['ETF']=names['基金简称'].apply(lambda x: 1 if 'ETF' in x else 0)
    names_etf=names[names['ETF']==1]
    
    if etf_type != '全部':
        ftypea=['QDII','债券型-中短债','债券型-可转债','债券型-长债','商品（不含QDII）','指数型-股票','货币型']
        ftypes=['QDII','债券型','债券型','债券型','商品型','股票型','货币型']
        names_etf['基金分类']=names_etf['基金类型'].apply(lambda x:ftypes[ftypea.index(x)])
        names_etf2=names_etf[names_etf['基金分类']==etf_type]
    else:
        names_etf2=names_etf
        
    names_etf2.sort_values(by=['基金分类','基金代码'],ascending=[True,True],inplace=True)
    etfcols=['基金代码','基金简称','基金分类','基金类型']
    names_etf2=names_etf2[etfcols]
    
    names_etf3=names_etf2[startpos:endpos]
    if len(names_etf3)==0:
        print("  #Error(choose_etf_china): no records of ETF selected")
        print("  Parameter startpos",startpos,'should be smaller than endpos',endpos)
        return None
    
    names_etf4=names_etf3[etfcols]    
    names_etf4.reset_index(drop=True,inplace=True)
    names_etf4.index=names_etf4.index+1
    
    print("\n")
    alignlist=['right','center','left']+['center']*(len(list(names_etf4))-2)
    print(names_etf4.to_markdown(index=True,tablefmt='plain',colalign=alignlist))
    print("\n*** ETF基金("+etf_type+")总数:",len(names_etf2),"\b。",end='')
    
    import datetime; today = datetime.date.today().strftime("%Y-%m-%d")
    footnote=texttranslate("数据来源：新浪财经，")+today
    print(footnote)

    
    return list(names_etf4['基金代码']),names_etf2

#==============================================================================
#==============================================================================
if __name__=='__main__':
    fund='sh510170'
    fund='sh000311'
    
    info=fund_info_china('sh510170')
    info=fund_info_china('510170.SS')
    
    fund='510170.SS'

def fund_info_china(fund,rank=15):
    """
    功能：查询中国基金代码和类型
    注意：实际仅需6位数字代码
    
    数据来源：东方财富，天天基金网
    """
    print("Searching for fund info, it may take time, please wait ...")
    
    # 代码中提取6位数字
    fund1=fund.upper()
    exchlist=['SH','SZ','.SS','.SZ']
    for exch in exchlist:
        fund1=fund1.replace(exch,'')
    
    #import pandas as pd
    #import akshare as ak
    
    # 检查基金是否存在
    try:
        names = ak.fund_name_em()
        namedf=names[names['基金代码']==fund1]
        
        if len(namedf) >= 1:
            df1=namedf[['基金代码','基金简称','基金类型']]
            fname=namedf['基金简称'].values[0]
            ftype=namedf['基金类型'].values[0]
        else:
            print("  #Warning(fund_info_china): info not found for fund",fund)
            return None
    except:
            print("  #Warning(fund_info_china): info source inaccessible for now, try later")
            return None
    
    # 基金评级
    df6=pd.DataFrame()
    titletxt6="基金概况与评级"
    footnote6="注：评级机构为上海证券、招商证券和济安金信，数字表示星星个数，在同类基金中通常越高越好"
    try:
        dft6 = ak.fund_rating_all()
        dft6t=dft6[dft6['代码']==fund1]
        dft6t.fillna('---',inplace=True)
        fmanager=dft6t['基金经理'].values[0]
        
        if len(dft6t) >= 1:
            df6=dft6t
            #printInMarkdown(df6,titletxt=titletxt6,footnote=footnote6)
            df_display_CSS(df6,titletxt=titletxt6,footnote=footnote6,facecolor='papayawhip', \
                               first_col_align='left',second_col_align='left', \
                               last_col_align='center',other_col_align='center')

    except:
        pass
    
    # 指数型基金信息
    df2=pd.DataFrame()
    titletxt2="指数型基金的相关信息"
    footnote2="注：单位净值元，日/今年来/今年来的增长率及手续费为百分比"
    try:
        dft2 = ak.fund_info_index_em(symbol="全部", indicator="全部")
        dft2.sort_values('基金代码',inplace=True)
        dft2t=dft2[dft2['基金代码']==fund1]
        
        if len(dft2t) >= 1:
            df2=dft2t[['基金代码','单位净值','日期','日增长率','今年来','手续费']]
            #printInMarkdown(df2,titletxt=titletxt2,footnote=footnote2)
            df_display_CSS(df2,titletxt=titletxt2,footnote=footnote2,facecolor='papayawhip', \
                               first_col_align='left',second_col_align='left', \
                               last_col_align='center',other_col_align='center')
            
    except:
        pass
    
    # 基金持仓：股票
    titletxt3="基金持仓情况："+fname+"，股票持仓"
    footnote3="注：占净值比例为百分比，持股数为万股，持仓市值为万元"
    df3=pd.DataFrame()
    import datetime; today = datetime.date.today()
    thisYear=str(today)[:4]
    try:
        dft3 = ak.fund_portfolio_hold_em(symbol=fund1,date=thisYear)
        dft3.sort_values(by=['季度','占净值比例'],ascending=[False,False],inplace=True)
        
        jidu=dft3['季度'].values[0]
        dft3recent=dft3[dft3['季度'] == jidu]
        dft3recent.reset_index(drop=True,inplace=True)
        dft3recent['序号'] = dft3recent.index + 1
        zanbi_stock = dft3recent['占净值比例'].sum()
        
        num_stock=len(dft3recent)
        if num_stock >= 1:
            df3=dft3recent
            df3['持仓类型']='股票'
            df3r=df3.head(min(rank,num_stock))
            zanbi_rank=df3r['占净值比例'].sum()
            footnote3=footnote3+'；披露的股票占比净值'+str(round(zanbi_stock,2))+ \
                '%，表中股票占比净值'+str(round(zanbi_rank,2))+'%'
            
            #printInMarkdown(df3,titletxt=titletxt3,footnote=footnote3)
            df_display_CSS(df3r,titletxt=titletxt3,footnote=footnote3,facecolor='papayawhip', \
                               first_col_align='center',second_col_align='left', \
                               last_col_align='center',other_col_align='center')

    except:
        #pass
        print('')
        print(titletxt3)
        print("Notice: no stock holding information for",fund,"@",thisYear)

    
    # 基金持仓：债券
    titletxt4="基金持仓情况："+fname+"，债券持仓"
    df4=pd.DataFrame()
    try:
        dft4 = ak.fund_portfolio_bond_hold_em(symbol=fund1,date=thisYear)
        dft4.sort_values(by=['季度','占净值比例'],ascending=[False,False],inplace=True)

        jidu=dft4['季度'].values[0]
        dft4recent=dft4[dft4['季度'] == jidu]
        dft4recent.reset_index(drop=True,inplace=True)
        dft4recent['序号'] = dft4recent.index + 1
        zanbi_bond = dft4recent['占净值比例'].sum()
        
        num_bond=len(dft4recent)
        
        if num_bond >= 1:
            df4=dft4recent
            df4['持仓类型']='债券'
            #printInMarkdown(df4,titletxt=titletxt4)
            df4r=df4.head(min(rank,num_bond))
            zanbi_rank=df4r['占净值比例'].sum()
            footnote4='注：披露的债券占比净值'+str(round(zanbi_bond,2))+ \
                '%，表中债券占比净值'+str(round(zanbi_rank,2))+'%'
            
            df_display_CSS(df4r,titletxt=titletxt4,footnote=footnote4,facecolor='papayawhip', \
                               first_col_align='center',second_col_align='left', \
                               last_col_align='center',other_col_align='center')

    except:
        print('')
        print(titletxt4)
        #print("\n #Warning(fund_info_china): unable to retrieve bond holding info for",fund,"@",thisYear)
        print("Notice: no bond holding information for",fund,"@",thisYear)

    
    # 基金持仓：行业配置
    titletxt5="基金的行业配置："+fname
    footnote5="注：占净值比例为百分比，市值为万元"
    df5=pd.DataFrame()
    try:
        dft5 = ak.fund_portfolio_industry_allocation_em(symbol=fund1,date=thisYear)
        dft5.sort_values(by=['截止时间','占净值比例'],ascending=[False,False],inplace=True)
        
        jiezi=dft5['截止时间'].values[0]
        dft5recent=dft5[dft5['截止时间'] == jiezi]
        dft5recent.reset_index(drop=True,inplace=True)
        dft5recent['序号'] = dft5recent.index + 1
        zanbi_hangye = dft5recent['占净值比例'].sum()
        
        num_hangye=len(dft5recent)
        
        if num_hangye >= 1:
            df5=dft5recent
            df5['持仓类型']='行业配置'   
            df5r=df5.head(min(rank,num_hangye))
            zanbi_rank = df5r['占净值比例'].sum()
            footnote5=footnote5+'；披露的行业占比净值'+str(round(zanbi_hangye,2))+ \
                '%，表中行业占比净值'+str(round(zanbi_rank,2))+'%'
            
            #printInMarkdown(df5,titletxt=titletxt5,footnote=footnote5)
            df_display_CSS(df5r,titletxt=titletxt5,footnote=footnote5,facecolor='papayawhip', \
                               first_col_align='center',second_col_align='left', \
                               last_col_align='center',other_col_align='center')

    except:
        pass
    
    # 基金经理
    titletxt7="基金经理的相关情况"
    source="数据来源：东方财富/天天基金"
    footnote7="注：从业时间为天数，现任基金资产总规模为该基金经理管辖所有基金的总规模(亿元)，最佳回报为历史业绩(百分比)\n"+source+"，"+str(today)
    
    df7=pd.DataFrame()
    try:
        dft7 = ak.fund_manager(adjust='0')
        dft7t=dft7[dft7['姓名']==fmanager]
        
        if len(dft7t) >= 1:
            current=dft7t['现任基金'].values[0]
            df7=dft7t[['姓名','所属公司','累计从业时间','现任基金资产总规模','现任基金最佳回报']]
            
            #printInMarkdown(df7,titletxt=titletxt7)
            df_display_CSS(df7,titletxt=titletxt7,footnote='',facecolor='papayawhip', \
                               first_col_align='left',second_col_align='left', \
                               last_col_align='center',other_col_align='center')

            
            print(' ')
            print("基金经理当前兼任情况：")
            num=print_long_text(current)
            print(' ')
            print(footnote7)
    except:
        pass
    
        #print('')
        #print(titletxt7)
        #print("\n #Warning(fund_info_china): unable to retrieve job info for",fmanager)
        #print("Notice: no job info found for fund manager",fmanager)
    
    return 

#==============================================================================
#==============================================================================
#==============================================================================
if __name__=='__main__':
    num_quarters=8
    
    get_past_quarters()
    

def get_past_quarters(num_quarters=8,date_format="%Y%m%d",date_reverse=False):
    """
    功能：生成最近多个季度结束日期列表
    参数：
    num_quarters：最近的季度个数，默认8.
    
    返回值：列表，日期格式为YYYYMMDD，适合akshare的要求
    """
    
    from datetime import datetime, date
    from dateutil.relativedelta import relativedelta
    
    # 获取当前日期
    today = date.today()
    # 确定当前季度的结束日期
    current_year = today.year
    current_month = today.month
    current_quarter = (current_month - 1) // 3 + 1  # 计算当前季度
    quarter_end_month = current_quarter * 3  # 当前季度的结束月份
    quarter_end_day = 31 if quarter_end_month in [3, 12] else 30  # 3月和12月是31天，其他季度末月份是30天
    current_quarter_end_date = date(current_year, quarter_end_month, quarter_end_day)
    
    # 如果今天还没到季度末，需要调整为上一个季度的结束日期
    if today < current_quarter_end_date:
        current_quarter_end_date -= relativedelta(months=3)
        quarter_end_month = current_quarter_end_date.month
        quarter_end_day = 31 if quarter_end_month in [3, 12] else 30
        current_quarter_end_date = date(current_quarter_end_date.year, quarter_end_month, quarter_end_day)
    
    # 生成过去连续的 num_quarters 个季度结束日期
    quarter_dates = []
    for _ in range(num_quarters):
        quarter_dates.append(current_quarter_end_date)
        current_quarter_end_date -= relativedelta(months=3)
        
        current_year = current_quarter_end_date.year
        current_month = current_quarter_end_date.month
        quarter_end_day = 31 if current_month in [3, 12] else 30  # 3月和12月是31天，其他季度末月份是30天
        current_quarter_end_date = date(current_year, current_month, quarter_end_day)
        
    
    # 格式化日期为 YYYY-MM-DD
    quarter_dates = [date.strftime(date_format) for date in quarter_dates]
    
    if not date_reverse:
        quarter_dates.reverse()
    
    return quarter_dates


#==============================================================================
if __name__=='__main__':
    date_str='20241231'
    from_format="%Y%m%d"; to_format="%Y-%m-%d"
    
    format_date(date_str,from_format="%Y%m%d",to_format="%Y-%m-%d")

def format_date(date_str,from_format="%Y%m%d",to_format="%Y-%m-%d"):
    # 将 YYYYMMDD 格式的字符串解析为日期对象
    
    from datetime import datetime
    
    date_obj = datetime.strptime(date_str, "%Y%m%d")
    # 将日期对象格式化为 YYYY-MM-DD 格式
    formatted_date = date_obj.strftime("%Y-%m-%d")
    
    return formatted_date

#==============================================================================
if __name__=='__main__':
    top=10
    sortby='持有基金家数'
    sortby='持股变动数值'
    holder_type="基金持仓"

def fund_holding_stock_rank_china(ticker='',top=5,sortby='持有基金家数',holder_type="基金持仓"):
    """
    ===========================================================================
    功能：列出基金持股比例最高的股票及其持股信息
    参数：
    ticker：股票代码，默认空''，对全市场股票进行排行；若指定股票代码，则着重显示该股票的排行。
    top=5：若不指定股票代码，列出基金持股比例最高的股票个数，默认10；
    若指定股票代码，则列示该股票及其前后的排行。
    sortby：排行指标，默认'持有基金家数'。
    支持指标：'持有基金家数','持股总数','持股市值','持股变动数值','持股变动比例'（百分比）
    
    holder_type：持仓基金类别，默认"基金持仓"。
    支持类别："基金持仓", "QFII持仓", "社保持仓", "券商持仓", "保险持仓", "信托持仓"
    1. 基金持仓：主要反映公募基金和私募基金的持仓情况。
    2. QFII持仓：反映合格境外机构投资者（QFII）的持仓情况。
    3. 社保持仓：反映社保基金的持仓情况。
    4. 券商持仓：反映证券公司的自营业务持仓情况。
    5. 保险持仓：反映保险资金的持仓情况。
    6. 信托持仓：反映信托公司的持仓情况。
    在东方财富网中，“基金持仓”不包括QFII持仓、社保持仓、券商持仓、保险持仓或信托持仓。
    
    • 基金持仓：多样化投资策略，专业管理，透明度高，追求相对收益。
    公募基金通常具有较高的流动性，投资者可以方便地申购和赎回。
    公募基金通常追求超越基准指数的收益，注重长期业绩表现。
    • QFII持仓：注重基本面和估值，长期投资，偏好高ROE和成长股，行业集中度较高。
    QFII倾向于选择基本面良好、估值合理的股票，偏好行业龙头。
    QFII的投资策略较为长期，持股时间较长，注重公司的长期增长潜力。
    QFII偏好高净资产收益率（ROE）的个股，近年来也逐渐增加对成长股的投资。
    重仓行业通常集中在相对安全、稳健的行业，如银行、食品饮料、医药等。
    QFII在市场趋势判断方面表现出色，能够在市场高点前加仓，在低点前减仓。
    • 社保持仓：长期价值投资，稳健投资，风险控制严格，市场风向标。
    社保基金注重长期投资，追求稳定收益，通常持有股票的时间较长。
    偏好稳健的股票，注重公司的基本面和盈利能力。
    社保基金对风险控制要求高，投资决策较为谨慎。
    社保基金的持仓变化被视为市场的风向标，其增仓或减仓行为可能预示市场趋势。
    • 券商持仓：灵活性高，信息优势，强周期性，注重短期收益。
    券商可能更注重短期的市场波动和交易机会，追求短期收益。
    • 保险持仓：稳健保守，长期投资，资产配置多元化，风险控制严格。
    保险资金注重资产的安全性和流动性，追求稳健收益。
    保险资金的投资期限较长，通常进行长期投资。
    对风险控制要求高，注重资产负债匹配管理。
    • 信托持仓：灵活性高，定制化服务，风险与收益平衡，专业管理。
    信托可以根据委托人的需求提供定制化的投资方案。

    
    返回值：df
    """
    holder_type_list=["基金持仓", "QFII持仓", "社保持仓", "券商持仓", "保险持仓", "信托持仓"]
    if not (holder_type in holder_type_list):
        print(f"  #Warning(fund_holding_stock_rank): {holder_type} not supported")
        print(f"  Supported types: {holder_type_list}")
        holder_type="基金持仓"
    
    #import akshare as ak
    
    quarter_dates=get_past_quarters(num_quarters=4,date_format="%Y%m%d",date_reverse=False)
    recent_quarter_date=quarter_dates[-1]
    recent_quarter_date2=format_date(recent_quarter_date,from_format="%Y%m%d",to_format="%Y-%m-%d")
    
    # symbol="基金持仓"; choice of {"基金持仓", "QFII持仓", "社保持仓", "券商持仓", "保险持仓", "信托持仓"}
    df = ak.stock_report_fund_hold(symbol=holder_type, date=recent_quarter_date)
    
    sortby_list=['持有基金家数','持股总数','持股市值','持股变化','持股变动数值','持股变动比例']
    if sortby not in sortby_list:
        print("  #Warning: sortby option only supports the following:")
        print(f"  {sortby_list}")
        sortby=sortby_list[0]

    if sortby != '持有基金家数':
        df.sort_values(sortby,ascending=False,inplace=True)
    else:
        df = df.sort_values(by=[sortby, '持股总数'], ascending=[False, False])

    df.reset_index(drop=True,inplace=True)
    df['序号']=df.index+1
        
    # 挪动排名项目
    df=shift_column_position(df,sortby,position=3)
    
    df2=df.copy()
    
    wan=10000; yiyuan=100000000
    df2['持股总数'] =df2['持股总数']/wan
    df2['持股总数'] =df2['持股总数'].apply(lambda x: round(x,2))
    
    df2['持股变动数值'] =df2['持股变动数值']/wan
    df2['持股变动数值'] =df2['持股变动数值'].apply(lambda x: round(x,2))

    df2['持股市值'] =df2['持股市值']/yiyuan
    df2['持股市值'] =df2['持股市值'].apply(lambda x: round(x,2))
    
    if top > 0:
        df3=df2.head(top)
    elif top < 0:
        df3=df2.tail(-top)
    else:
        df3=df2.head(5)
        
    #强制显示所选股票
    #if force_show_stock and rank != 10:
    if ticker != '':
        #所选股票是否在其中？
        if not ticker[:6] in list(df3["股票代码"]):
            try:
                ticker_seq=df2[df2["股票代码"]==ticker[:6]]["序号"].values[0]
            except:
                print(f"  #Error(fund_holding_stock_rank): {ticker} not found in {holder_type}")
                return None
            
            num_before=int(top/2)
            if num_before * 2 == top: num_before=num_before-1
            num_after=top-num_before-1
            
            #seq1=ticker_seq-4; seq2=ticker_seq+5
            seq1=ticker_seq-num_before; seq2=ticker_seq+num_after
            #如果超出开头
            if seq1 <=0:
                seq1=1; seq2=top
            #如果超出结尾    
            if seq2 > len(df2):
                seq2=len(df2); seq1=len(df2)-(top-1)
                
            #注意：此处的&不能换为and    
            df3=df2[(df2["序号"]>=seq1) & (df2["序号"]<=seq2)]
    
    titletxt=holder_type+'排名：基于'+sortby
    import datetime
    todaydt = datetime.date.today()
    #footnote0="【注释】排名方法："+sortby
    footnote0="【注释】数据截至"+recent_quarter_date2
    footnote1='；持股总数/持股变动数值：万股，持股市值：亿元'
    footnote2='。数据来源：东方财富/天天基金，'+str(todaydt)
    footnote=footnote0+footnote1+footnote2
    
    df_display_CSS(df3,titletxt=titletxt,footnote=footnote, \
                   facecolor='papayawhip',decimals=2, \
                       first_col_align='left',second_col_align='left', \
                       last_col_align='right',other_col_align='right', \
                       titile_font_size='16px',heading_font_size='15px', \
                       data_font_size='14px',footnote_font_size='13px')
    
    return df

#==============================================================================
if __name__=='__main__':
    ticker='689009.SS'
    num_quarters=8
    

def fund_holding_stock_trend_china(ticker,num_quarters=8,holder_type="基金持仓", \
                             close_price=False):
    """
    ===========================================================================
    功能：列出一只股票被基金持股的变动趋势
    参数：
    ticker：股票代码
    num_quarters：最近基金持股的季度个数，默认8。
    holder_type：持仓基金类别，默认"基金持仓"；若为'ALL'则扫描所有机构持股信息，时间较长。
    
    返回值：df
    """
    holder_type_list=["基金持仓", "QFII持仓", "社保持仓", "券商持仓", "保险持仓", "信托持仓"]
    if not (holder_type in holder_type_list):
        print(f"  #Warning(fund_holding_stock_trend): {holder_type} not supported")
        print(f"  Supported types: {holder_type_list}")
        holder_type="基金持仓"
    
    #import akshare as ak
    #import pandas as pd
    
    quarter_dates=get_past_quarters(num_quarters=num_quarters,date_format="%Y%m%d",date_reverse=False)
    

    df=pd.DataFrame()
    for d in quarter_dates:
        print(f"  Searching {holder_type} info on {ticker} in {d} ...")
        
        # symbol="基金持仓"; choice of {"基金持仓", "QFII持仓", "社保持仓", "券商持仓", "保险持仓", "信托持仓"}
        try:
            dftmp = ak.stock_report_fund_hold(symbol=holder_type, date=d)
        except:
            continue
        
        try:
            dftmp2=dftmp[dftmp['股票代码']==ticker[:6]]
        except:
            break
    
        d2=format_date(d,from_format="%Y%m%d",to_format="%Y-%m-%d")
        dftmp2['季度']=d2
        #dftmp2['机构类别']=holder_type
        
    
        if len(df)==0:
            df=dftmp2
        else:
            df=pd.concat([df, dftmp2], axis=0, ignore_index=True)

    # 未找到股票
    if len(df)==0:
        print(f"  #Error(fund_holding_stock_trend): stock {ticker} not found or not holded by fund")
        return None

    # 重排字段
    stock_name=df['股票简称'].values[0]
    col_list=['季度','持股变化','持股变动数值','持股变动比例','持有基金家数','持股总数','持股市值']
    df2=df[col_list]

    
    wan=10000; yiyuan=100000000
    df2['持股总数'] =df2['持股总数']/wan
    df2['持股总数'] =df2['持股总数'].apply(lambda x: round(x,2))
    
    df2['持股变动数值'] =df2['持股变动数值']/wan
    df2['持股变动数值'] =df2['持股变动数值'].apply(lambda x: round(x,2))

    df2['持股市值'] =df2['持股市值']/yiyuan
    df2['持股市值'] =df2['持股市值'].apply(lambda x: round(x,2))
    
    if not close_price:
        df4=df2
    else:
        ticker2=tickers_cvt2ak(ticker)
        fromdate=df2['季度'].values[0]; fromdate=date_adjust(fromdate, adjust=-30)
        todate=df2['季度'].values[-1]; todate=date_adjust(todate, adjust=30)
        result,start,end=check_period(fromdate,todate)
        start1=start.strftime('%Y%m%d'); end1=end.strftime('%Y%m%d')
        prices=security_trend(ticker,start=fromdate,end=todate,graph=False)
        prices.index = pd.to_datetime(prices.index, format='%Y-%m-%d')
        prices['收盘价']=prices['Close']
        prices['季度']=prices.index.strftime('%Y-%m-%d')
        prices2=prices[['季度','收盘价']]
        
        
        df3=pd.merge(df2,prices2,on='季度',how='outer')
        # 使用前一个非空值填充某一列的空缺值
        df3['收盘价'] = df3['收盘价'].fillna(method='ffill')
        # 使用后一个非空值填充某一列的空缺值
        df3['收盘价'] = df3['收盘价'].fillna(method='bfill')
        # 删除列 'A' 中包含空缺值的所有行
        df4 = df3.dropna(subset=['持有基金家数'])
    
    titletxt=holder_type+'变动趋势：'+stock_name
    import datetime
    todaydt = datetime.date.today()
    #footnote0="【注释】排名方法："+sortby
    footnote0="【注释】"
    footnote1='持股总数/持股变动数值：万股，持股市值：亿元'
    footnote2='。数据来源：东方财富/天天基金，'+str(todaydt)
    footnote=footnote0+footnote1+footnote2
    
    df_display_CSS(df4,titletxt=titletxt,footnote=footnote, \
                   facecolor='papayawhip',decimals=2, \
                       first_col_align='left',second_col_align='left', \
                       last_col_align='right',other_col_align='right', \
                       titile_font_size='16px',heading_font_size='15px', \
                       data_font_size='14px',footnote_font_size='13px')
    
    return df

#==============================================================================
if __name__=='__main__':
    ticker='689009.SS'
    ticker='600519.SS'
    num_quarters=8
    

def fund_holding_stock_trend_all_china(ticker,num_quarters=4):
    """
    ===========================================================================
    功能：列出一只股票被所有机构类别持股的变动趋势
    参数：
    ticker：股票代码
    num_quarters：最近基金持股的季度个数，默认8。
    
    返回值：df
    """
    holder_type_list=["基金持仓", "QFII持仓", "社保持仓", "券商持仓", "保险持仓", "信托持仓"]
    
    #import akshare as ak
    #import pandas as pd
    
    quarter_dates=get_past_quarters(num_quarters=num_quarters,date_format="%Y%m%d",date_reverse=False)
    

    df=pd.DataFrame()
    for ht in holder_type_list:
        print(f"  Searching {ht} info on {ticker} ...")

        for d in quarter_dates:
            
            try:
                dftmp = ak.stock_report_fund_hold(symbol=ht, date=d)
            except:
                continue
            
            try:
                dftmp2=dftmp[dftmp['股票代码']==ticker[:6]]
            except:
                break
        
            d2=format_date(d,from_format="%Y%m%d",to_format="%Y-%m-%d")
            dftmp2['季度']=d2
            dftmp2['机构类别']=ht
            
        
            if len(df)==0:
                df=dftmp2
            else:
                df=pd.concat([df, dftmp2], axis=0, ignore_index=True)

    # 未找到股票
    if len(df)==0:
        print(f"  #Error(fund_holding_stock_trend): stock {ticker} not found or not holded by fund")
        return None

    # 重排字段
    stock_name=df['股票简称'].values[0]
    col_list=['季度','机构类别','持股变化','持股变动数值','持股变动比例','持有基金家数','持股总数','持股市值']
    df2=df[col_list]
    df2= df2.sort_values(['季度'],ascending=[True])

    
    wan=10000; yiyuan=100000000
    df2['持股总数'] =df2['持股总数']/wan
    df2['持股总数'] =df2['持股总数'].apply(lambda x: round(x,2))
    
    df2['持股变动数值'] =df2['持股变动数值']/wan
    df2['持股变动数值'] =df2['持股变动数值'].apply(lambda x: round(x,2))

    df2['持股市值'] =df2['持股市值']/yiyuan
    df2['持股市值'] =df2['持股市值'].apply(lambda x: round(x,2))
    
    titletxt='机构持仓变动趋势：'+stock_name
    import datetime
    todaydt = datetime.date.today()
    #footnote0="【注释】排名方法："+sortby
    footnote0="【注释】"
    footnote1='持股总数/持股变动数值：万股，持股市值：亿元'
    footnote2='。数据来源：东方财富/天天基金，'+str(todaydt)
    footnote=footnote0+footnote1+footnote2
    
    df_display_CSS(df2,titletxt=titletxt,footnote=footnote, \
                   facecolor='papayawhip',decimals=2, \
                       first_col_align='left',second_col_align='left', \
                       last_col_align='right',other_col_align='right', \
                       titile_font_size='16px',heading_font_size='15px', \
                       data_font_size='14px',footnote_font_size='13px')
    
    return df


#==============================================================================
if __name__=='__main__':
    ticker='600519.SS'
    ticker='600305.SS'
    top=3

def stock_heldby_fund_detail_china(ticker,top=5):
    """
    ===========================================================================
    功能：列示持有一只股票最多的前几名基金列表。
    参数：
    ticker：股票代码
    top：列示前几名，默认5
    
    返回值：数据表
    """
    
    #import akshare as ak

    # 获取某只股票被基金持股的数据
    try:
        df = ak.stock_fund_stock_holder(symbol=ticker[:6])
    except:
        print(f"Sorry, no fund holding details found for {ticker} in data source")
        return None
    
    df2=df.copy()
    
    wan=10000; yiyuan=100000000
    df2['持仓数量'] =df2['持仓数量']/wan
    df2['持仓数量'] =df2['持仓数量'].apply(lambda x: round(x,2))

    df2['持股市值'] =df2['持股市值']/yiyuan
    df2['持股市值'] =df2['持股市值'].apply(lambda x: round(x,2))
    
    # 按持股比例降序排列
    df3 = df2.sort_values(by='占流通股比例', ascending=False)
    
    # 取前五名基金
    df4 = df3.head(top)
    df4['序号']=df4.index+1
    df4=shift_column_position(df4,col_name='序号',position=0)
    
    ddl_date=df4['截止日期'].values[0]
    del df4['截止日期']
        
    quarter_dates=get_past_quarters(num_quarters=8,date_format="%Y%m%d",date_reverse=False)
    recent_quarter_date=quarter_dates[-1]
    recent_quarter_date2=format_date(recent_quarter_date,from_format="%Y%m%d",to_format="%Y-%m-%d")
    if str(ddl_date) < str(recent_quarter_date2):
        print("Pity, fund holding stock info may be far out of date:-(")
    
    titletxt=ticker_name(ticker)+'：机构持仓情况，截至'+str(ddl_date)
    import datetime
    todaydt = datetime.date.today()
    #footnote0="【注释】排名方法："+sortby
    footnote0="【注释】"
    footnote1='持仓数量：万股，持股市值：亿元'
    footnote2='。数据来源：新浪财经，'+str(todaydt)
    footnote=footnote0+footnote1+footnote2
    
    df_display_CSS(df4,titletxt=titletxt,footnote=footnote, \
                   facecolor='papayawhip',decimals=2, \
                       first_col_align='center',second_col_align='left', \
                       last_col_align='right',other_col_align='right', \
                       titile_font_size='16px',heading_font_size='15px', \
                       data_font_size='14px',footnote_font_size='13px')
    
    return df
#==============================================================================



def fund_holding_stock_china(ticker='',top=5,sortby='持有基金家数', \
                             holder_type="基金持仓",quarter='recent', \
                             detail=False, \
                             close_price=False):
    """
    ===========================================================================
    功能：列示中国内地机构持股情况。
    参数：
    ticker：股票代码，默认''，列示最受机构追捧的股票排行及其被机构持仓情况。
    若为一个股票代码，则列示该股票的排行情况及其被机构持仓情况。
    top：列示排行时的个数，默认5。
    sortby：当列示排行时标示排行的指标，默认'持有基金家数'。
    holder_type：机构持仓的类别，默认"基金持仓"。
    当为ALL时列示所有机构类别的持仓情况。
    仅有少数热门股票在除“基金持仓”以外的类别有数据，数据亦可能较久远。
    quarter：指示列示数据的季度，默认'recent'仅列示最近一个季度末的披露数据。
    若为数字则列示近若干个季度的机构持仓变动趋势。
    与holder_type='ALL'配合时列示近若干个季度的所有机构类别的持仓变动趋势。
    detail：是否列示持有一只股票的机构持仓情况，仅当ticker不为空时有效，默认False。
    close_price：当列示持有一只股票的机构持仓情况是否同时列示股价，默认False。
    
    返回值：数据表，无数据时返回空。
    """
    
    if quarter=='recent' and holder_type.upper() != 'ALL' and not detail:
        df=fund_holding_stock_rank_china(ticker=ticker,top=top, \
                                         sortby=sortby,holder_type=holder_type)
            
    elif ticker != '' and isinstance(quarter,int) and holder_type.upper() != 'ALL' and not detail:
        df=fund_holding_stock_trend_china(ticker=ticker,num_quarters=quarter, \
                                          holder_type=holder_type, \
                                          close_price=close_price)

    elif ticker != '' and isinstance(quarter,int) and holder_type.upper() == 'ALL' and not detail:
        df=fund_holding_stock_trend_all_china(ticker=ticker,num_quarters=quarter)
   
    elif ticker != '' and detail:
        df=stock_heldby_fund_detail_china(ticker=ticker,top=top)
        
    else:
        print("Sorry, no idea on what you expect to do:-(")
        
    return df


#==============================================================================
#==============================================================================
#==============================================================================
#==============================================================================
#==============================================================================
#==============================================================================
#==============================================================================
#==============================================================================




























