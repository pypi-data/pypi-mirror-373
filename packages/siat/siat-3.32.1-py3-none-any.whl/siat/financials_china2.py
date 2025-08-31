# -*- coding: utf-8 -*-

"""
本模块功能：计算财务报表指标，基于东方财富，仅限于中国大陆上市的企业
所属工具包：证券投资分析工具SIAT 
SIAT：Security Investment Analysis Tool
创建日期：2024年4月21日
最新修订日期：2022年5月18日
作者：王德宏 (WANG Dehong, Peter)
作者单位：北京外国语大学国际商学院
作者邮件：wdehong2000@163.com
版权所有：王德宏
用途限制：仅限研究与教学使用，不可商用！商用需要额外授权。
特别声明：作者不对使用本工具进行证券投资导致的任何损益负责！
"""
#==============================================================================
#本模块的公共引用
import pandas as pd
import akshare as ak

# 这条语句似乎有时失灵！?
from siat.stock_china import *
from siat.financials_china import *
from siat.translate import *
#==============================================================================
#==============================================================================
if __name__=='__main__':
    tickers=["000002.SZ","600266.SS",'600383.SS','600048.SS']
    fsdates=['2021-12-31','2020-12-31','2019-12-31','2018-12-31']
    
    tickers = ['002415.SZ',#海康威视
               '002236.SZ',#大华股份
               "002528.SZ",#英飞拓
               "300275.SZ",#梅安森
               "603019.SS",#中科曙光
              ]  
    
    fsdates = ['2022-12-31','2021-12-31','2020-12-31','2019-12-31']
    
    df=get_fin_stmt_ak_multi(tickers,fsdates)         
    
def get_fin_stmt_ak_multi(tickers,fsdates):
    """
    功能：获得多个股票的全部财报，基于akshare，合成，排序：股票代码+财报日期降序
    选择：仅保留fsdates日期的数据。注意：fsdates要比预计的多一项，以便计算期初数
    """
    from siat.financials_china import get_fin_stmt_ak
    from siat.financials_china import fs_entry_begin_china         
    
    #循环获取全部股票的财报，并合成
    df=pd.DataFrame()
    for t in tickers:
        dft=get_fin_stmt_ak(t)
        if dft is None:
            print("  #Warning(get_fin_stmt_ak_multi): currently data unavailable for",t)
            continue
        if len(dft) ==0:
            print("  #Warning(get_fin_stmt_ak_multi): zero records available for",t)
            continue
            
        #按日期升序
        dft.sort_index(ascending=True,inplace=True)
        #选择指定的日期
        dfs=dft[dft['endDate'].isin(fsdates)]
        
        #列改名
        dfs.rename(columns={'所有者权益(或股东权益)合计':'所有者权益合计',
                            '一、营业总收入':'营业总收入',
                            '加:营业外收入':'营业外收入',
                            '二、营业总成本':'营业总成本',
                            '三、营业利润':'营业利润',
                            '四、利润总额':'利润总额',
                            '归属于母公司所有者的净利润':'归母净利润',
                            '减：所得税费用':'所得税费用',    
                            '处置固定资产、无形资产和其他长期资产的损失':'资产处置损失',
                            '减：营业外支出':'营业外支出',
                            
                           #'经营活动产生现金流量净额':'经营活动现金流净额',
                            '经营活动产生的现金流量净额':'经营活动现金流净额',
                            '经营活动现金流入小计':'经营活动现金流入',
                            '经营活动现金流出小计':'经营活动现金流出',
                            '投资活动产生的现金流量净额':'投资活动现金流净额',
                            '投资活动现金流入小计':'投资活动现金流入',
                            '投资活动现金流出小计':'投资活动现金流出',
                            '筹资活动产生的现金流量净额':'筹资活动现金流净额',
                            '筹资活动现金流入小计':'筹资活动现金流入',
                            '筹资活动现金流出小计':'筹资活动现金流出',
                            '汇率变动对现金及现金等价物的影响':'汇率对现金流的影响',
                            '现金及现金等价物净增加额':'现金流量净增加额',
                            '基本每股收益(元/股)':'基本每股收益',
                            '稀释每股收益(元/股)':'稀释每股收益',
                            
                            #特殊改名，针对银行业
                            
                                },inplace=True)
        
        #计算指标
        entry_list=list(dfs)
        #dfs['应收账款占比%']=round(dfs['应收账款']/dfs['资产总计']*100,2)
        dfs['应收账款占比%']=dfs.apply(lambda x:round(x['应收账款']/x['资产总计']*100,2),axis=1)
        
        #dfs['存货占比%']=round(dfs['存货']/dfs['资产总计']*100,2)
        dfs['存货占比%']=dfs.apply(lambda x:round(x['存货']/x['资产总计']*100,2),axis=1)
        
        if ('流动资产合计' in entry_list) and ('流动负债合计' in entry_list):
            dfs['流动比率%']=dfs.apply(lambda x:round(x['流动资产合计']/x['流动负债合计']*100,2),axis=1)
            dfs['速动资产合计']=dfs.apply(lambda x:x['流动资产合计']-x['存货'],axis=1)
            dfs['速动比率%']=dfs.apply(lambda x:round(x['速动资产合计']/x['流动负债合计']*100,2),axis=1)
        dfs['资产负债率%']=dfs.apply(lambda x:round(x['负债合计']/x['资产总计']*100,2),axis=1)

        if not ('营业总收入' in entry_list) and ('营业收入' in entry_list):
            dfs['营业总收入']=dfs['营业收入']
        if not ('营业成本' in entry_list) and ('营业收入' in entry_list) and ('营业利润' in entry_list):
            dfs['营业成本']=dfs['营业收入'] - dfs['营业利润']

        dfs['毛利润']=dfs.apply(lambda x:x['营业总收入']-x['营业成本'],axis=1)
        dfs['毛利润率%']=dfs.apply(lambda x:round(x['毛利润']/x['营业总收入']*100,2),axis=1)
        dfs['营业利润率%']=dfs.apply(lambda x:round(x['营业利润']/x['营业总收入']*100,2),axis=1)
        
        if '销售费用' in entry_list:
            dfs['销售费用率%']=dfs.apply(lambda x:round(x['销售费用']/x['营业总收入']*100,2),axis=1)
            
        if not ('管理费用' in entry_list) and ('业务及管理费用' in entry_list):
            dfs['管理费用']=dfs['业务及管理费用']
        dfs['管理费用率%']=dfs.apply(lambda x:round(x['管理费用']/x['营业总收入']*100,2),axis=1)
        try:
            dfs['研发费用率%']=dfs.apply(lambda x:round(x['研发费用']/x['营业总收入']*100,2),axis=1)
        except:
            dfs['研发费用率%']='-'
        
        if not ('营业外收入' in entry_list) and ('加:营业外收入' in entry_list):
            dfs['营业外收入']=dfs['加:营业外收入']
        if not ('营业外支出' in entry_list) and ('减:营业外支出' in entry_list):
            dfs['营业外支出']=dfs['减:营业外支出']
        dfs['营业外收支']=dfs.apply(lambda x:x['营业外收入']-x['营业外支出'],axis=1)
        dfs['税前利润']=dfs['利润总额']
        dfs['税前利润率%']=dfs.apply(lambda x:round(x['利润总额']/x['营业总收入']*100,2),axis=1)
        
        if not ('所得税费用' in entry_list) and ('减:所得税' in entry_list):
            dfs['所得税费用']=dfs['减:所得税']
        if '所得税费用' in list(dfs):
            dfs['实际所得税率%']=dfs.apply(lambda x:round(x['所得税费用']/x['利润总额']*100,2),axis=1)
            
        dfs['净利润率%']=dfs.apply(lambda x:round(x['净利润']/x['营业总收入']*100,2),axis=1)
        
        #dfs['流通股股数']=dfs.apply(lambda x:round(x['净利润']/x['基本每股收益'],0),axis=1)
        """
        if '流动负债合计' in entry_list:
            dfs['短期现金偿债能力%']=dfs.apply(lambda x:round(x['经营活动现金流净额']/x['流动负债合计']*100,2),axis=1)
        dfs['长期现金偿债能力%']=dfs.apply(lambda x:round(x['经营活动现金流净额']/x['负债合计']*100,2),axis=1)
        #dfs['现金支付股利能力(元)']=dfs.apply(lambda x:round(x['经营活动现金流净额']/x['流通股股数'],2),axis=1)
        
        if not ('所有者权益合计' in entry_list) and ('负债及股东权益总计' in entry_list) and ('负债合计' in entry_list):
            dfs['所有者权益合计']=dfs['负债及股东权益总计'] - dfs['负债合计']
        dfs['现金综合支付能力%']=dfs.apply(lambda x:round(x['经营活动现金流净额']/x['所有者权益合计']*100,2),axis=1)
        dfs['销售现金比率%']=dfs.apply(lambda x:round(x['经营活动现金流入']/x['营业总收入']*100,2),axis=1)
        dfs['盈利现金比率%']=dfs.apply(lambda x:round(x['经营活动现金流净额']/x['净利润'],2),axis=1)
        dfs['资产现金回收率%']=dfs.apply(lambda x:round(x['经营活动现金流净额']/x['资产总计']*100,2),axis=1)
        dfs['现金流入流出比率%']=dfs.apply(lambda x:round(x['经营活动现金流入']/x['经营活动现金流出']*100,2),axis=1)
        
        if not (((dfs['销售商品、提供劳务收到的现金']==0).all()) or ((dfs['购买商品、接受劳务支付的现金']==0).all())):
            dfs['现金购销比率%']=dfs.apply(lambda x:round(x['购买商品、接受劳务支付的现金']/x['销售商品、提供劳务收到的现金']*100,2),axis=1)
            dfs['营业现金回笼率%']=dfs.apply(lambda x:round(x['销售商品、提供劳务收到的现金']/x['营业总收入']*100,2),axis=1)
            dfs['支付给职工的现金比率%']=dfs.apply(lambda x:round(x['支付给职工以及为职工支付的现金']/x['销售商品、提供劳务收到的现金']*100,2),axis=1)
        """
        # 自定义财务比率
        
        #获取字段列表,增加期初项目
        #去掉重复的列
        dfst=dfs.T
        dfst['index_tmp']=dfst.index #防止仅仅因为数值相同而被当作重复项误删
        dfst.drop_duplicates(subset='index_tmp',keep='first',inplace=True)
        dfst.drop(columns=['index_tmp'],axis=1,inplace=True)
        dfs=dfst.T
        
        col_list=list(dfs)   
        for c in col_list:
            #print(c)
            """
            if isinstance(c,float) or isinstance(c,int):
                dfs[c+"_期初"]=dfs[c].shift(1)
            """
            """
            if not (c+"_期初" in col_list):
                try:
                    dfs[c+"_期初"]=dfs[c].shift(1)
                except:
                    print("  #Warning(get_fin_stmt_ak_multi): problematic column",c,'in the fin statements of',t)
            else:
                continue
            """
            dfs=fs_entry_begin_china(dfs,account_entry=c,suffix='_期初')
            
        #给字段排序，便于检查对比
        col_list_qc=list(dfs)
        col_list2=sorted(col_list_qc)
        dfs2=dfs[col_list2]
        
        #合成
        try:
            df=df.append(dfs2)
        except:
            df=df._append(dfs2)

    if df is None:
        return None
    if len(df)==0:
        return None

    #删除空值行：谨慎！！！
    #df.dropna(inplace=True)
    
    #删除多余的列，修改列名
    #del df['ticker_期初']
    df.rename(columns={'endDate_期初':'endDate_上期'},inplace=True)
    
    #标注股票简称,去掉其中的(A股)字样
    df["股票简称"]=df['ticker'].apply(lambda x: ticker_name(x,'stock').replace("(A股)",''))

    """
    # 替换nan为-
    df.fillna('-',inplace=True)
    df.replace(0,'-',inplace=True)
    """
    
    return df

#==============================================================================
if __name__=='__main__':
    tickers=["000002.SZ","600266.SS",'600383.SS','600048.SS']
    fsdates=['2021-12-31','2020-12-31','2019-12-31','2018-12-31']
    df=get_fin_stmt_ak_multi(tickers,fsdates) 
    
    ticker="000002.SZ"
    fsdate='2021-12-31'
    item="货币资金"
    
    select_item(df,ticker,fsdate,item)
    
def select_item(df,ticker,fsdate,item):
    """
    功能：根据股票代码、财报日期和科目(含期初)查询金额；若全为零则提示
    """
    
    col_list=['ticker',"股票简称",'endDate',"endDate_上期",item,item+"_期初"]
    dfs=df[(df['ticker']==ticker) & (df['endDate']==fsdate)][col_list]
    
    try:
        item_value=dfs[item].values[0]
        item_value_qc=dfs[item+"_期初"].values[0]
    except:
        print("  #Warning(select_item):",ticker+"在"+fsdate+"的"+item+"未找到")
        nann=float("nan")
        return nann,nann,nann
    
    #全为零提示
    """
    if (item_value==0) & (item_value_qc==0):
        print("  #Warning(select_item):",ticker+"在"+fsdate+"的"+item+"及其期初数均为零")
    """
    return item_value,item_value_qc,dfs
#==============================================================================
if __name__=='__main__':
    tickers=["000002.SZ","600266.SS",'600383.SS','600048.SS']
    fsdates=['2021-12-31','2020-12-31','2019-12-31','2018-12-31']
    df=get_fin_stmt_ak_multi(tickers,fsdates) 
    
    itemword1="固定资产"
    itemword1="资产"
    itemword2="计"
    
    dfs=find_fs_items(df,itemword1,itemword2)

def find_fs_items(df,itemword1,itemword2='',printout=True):
    """
    功能：搜索财务报表中含有关键词itemword的项目，并判断这些项目是否整列全为零
    """
    
    col_list=list(df)
    col_yes=[]
    for c in col_list:
        if (itemword1 in c) & (itemword2 in c):
            col_yes=col_yes+[c]
    
    dfs=pd.DataFrame(columns=['报表项目','是否全为零'])
    for cy in col_yes:
        allzero=(df[cy].std()==0)

        row=pd.Series({'报表项目':cy,'是否全为零':allzero})
        try:
            dfs=dfs.append(row,ignore_index=True)
        except:
            dfs=dfs._append(row,ignore_index=True)
        
    if printout:
        #设置打印对齐
        pd.set_option('display.max_columns', 1000)
        pd.set_option('display.width', 1000)
        pd.set_option('display.max_colwidth', 1000)
        pd.set_option('display.unicode.ambiguous_as_wide', True)
        pd.set_option('display.unicode.east_asian_width', True)    
        
        #无序号打印
        print('')
        print(dfs.to_string(index=False))
    
    return dfs
    
#==============================================================================
if __name__=='__main__':
    title_txt="===== 重要指标的同行业对比 ====="

def title_position_original(title_txt,dfp):
    """
    废弃
    功能：对dfp直接打印时计算让标题居中的位置，通过寻找各个回车符的位置。
    """
    
    #各个记录的长度
    cuan=dfp.to_string(index=False)
    pos_prev=0
    pos=cuan.find('\n')
    rowlen=pos
    while pos != -1:
        pos_prev=pos
        pos=cuan.find('\n',pos_prev+1)
        rowlen_new=pos - pos_prev
        if rowlen_new > rowlen:
            rowlen=rowlen_new
    
    #抬头的长度
    collist=list(dfp)
    collen=0
    for c in collist:
        collen=collen+len(c)
    collen=collen+(len(collist)-1)*2
    if collen > rowlen:
        rowlen=collen
    
    blanknum=int((rowlen - len(title_txt))/2)    

    return blanknum-4
#==============================================================================
if __name__=='__main__':
    title_txt="===== 重要指标的同行业对比 ====="

def title_position(title_txt,dfp):
    """
    功能：对dfp直接打印时计算让标题居中的位置，通过寻找各个回车符的位置。
    """
    
    #各个记录的长度
    cuan=dfp.to_string(index=False)+'\n'
    pos=0
    rowlen=0
    while pos != -1:
        pos_new=cuan.find('\n',pos+1)
        sub_cuan=cuan[pos+1:pos_new]
        rowlen_new=hzlen(sub_cuan)
        #print(pos,pos_new,rowlen_new,sub_cuan)
        
        if rowlen_new > rowlen:
            rowlen=rowlen_new
        pos=pos_new
    
    title_len=hzlen(title_txt)+2
    #blanknum=int((rowlen - title_len)/2)    
    blanknum=int((rowlen - title_len)/2)+(len(list(dfp))-2)    

    return blanknum

if __name__=='__main__':
    title_txt="===== 重要指标的同行业对比 ====="
    blanknum=title_position(title_txt,dfp)
    
    print(' '*blanknum,title_txt) 
    print(dfp.to_string(index=False))

#==============================================================================
if __name__=='__main__':
    title_txt="万科A财报：重要指标的同行业对比\n（财报截止日期：2021-12-31）"
    footnote="*数据来源：新浪财经，2022年5月23日\n**股票列表第一项为分析对象\n*日期列表第一项为分析日期"
    title_break=False
    foot_break=True
    foot_center=False
    foot_start=4

def df_directprint_original(dfp,title_txt,footnote, \
                   title_break=True,foot_break=True,foot_center=False,foot_start=1, \
                   facecolor='papayawhip'):
    """
    功能：对dfp直接打印，让标题居中，让脚注居中或指定开始位置。
    """
    print('')
    
    #解析标题各行并居中打印
    title_txt1=title_txt+'\n'
    pos,pos_new=0,0
    while pos_new != -1:
        pos_new=title_txt1.find('\n',pos)
        linetxt=title_txt1[pos:pos_new]
        #print(linetxt)
        
        blanknum=title_position(linetxt,dfp)
        
        if linetxt != '\n':
            print(' '*blanknum,linetxt) 
            
        pos=pos_new+1
    
    #设置打印对齐
    """
    pd.set_option('display.max_columns', 1000)
    pd.set_option('display.width', 1000)
    pd.set_option('display.max_colwidth', 1000)
    pd.set_option('display.unicode.ambiguous_as_wide', True)
    pd.set_option('display.unicode.east_asian_width', True)  
    """
    
    #打印数据框本身    
    #print(dfp.to_string(index=False))
    colalign=['left']+['right']*(len(list(dfp)) - 1)
    print(dfp.to_markdown(tablefmt='Simple',index=False,colalign=colalign))
        
    #解析脚注各行并打印
    if foot_break: print('')
    footnote1=footnote+'\n'
    pos,pos_new=0,0
    while pos_new != -1:
        pos_new=footnote1.find('\n',pos)
        linetxt=footnote1[pos:pos_new]
        #print(linetxt)
        if foot_center:
            blanknum=title_position(linetxt,dfp)
        else:
            blanknum=foot_start-1
        
        if linetxt != '\n':
            if blanknum >2:
                print(' '*blanknum,linetxt) 
            else:
                print(linetxt)
            
        pos=pos_new+1

    return 

#==============================================================================
"""
def df_directprint(dfp,title_txt,footnote, \
                   title_break=True,foot_break=True,foot_center=False,foot_start=1, \
                   decimals=2,facecolor='papayawhip'):
"""
def df_directprint(dfp,title_txt,footnote,decimals=2,facecolor='papayawhip',font_size='16px'):
    """
    功能：对dfp直接打印，使用pandas style打印，套壳函数df_display_CSS
    """
    #替换nan和inf
    import pandas as pd
    import numpy as np
    dfp.replace([np.inf, -np.inf],'-', inplace=True)
    dfp.replace([np.nan],'-', inplace=True)
    
    #print('') #空一行
    
    """
    #解析标题各行并居中打印
    title_txt1=title_txt+'\n'
    pos,pos_new=0,0
    while pos_new != -1:
        pos_new=title_txt1.find('\n',pos)
        linetxt=title_txt1[pos:pos_new]
        #print(linetxt)
        
        blanknum=title_position(linetxt,dfp)
        
        if linetxt != '\n':
            print(' '*blanknum,linetxt) 
            
        pos=pos_new+1
    """
    
    #确定表格字体大小
    titile_font_size=font_size
    heading_font_size=data_font_size=str(int(font_size.replace('px',''))-1)+'px'
    
    df_display_CSS(dfp,titletxt=title_txt,footnote=footnote,facecolor=facecolor, \
                   titile_font_size=titile_font_size,heading_font_size=heading_font_size, \
                       data_font_size=data_font_size)
    
    """
    disph=dfp.style.hide() #不显示索引列
    dispp=disph.format(precision=decimals) #设置带有小数点的列精度调整为小数点后2位
    
    #设置标题/列名
    dispt=dispp.set_caption(title_txt).set_table_styles(
        [{'selector':'caption', #设置标题对齐
          'props':[('color','black'),('font-size','18px'),('font-weight','bold')]}, \
         {'selector':'th.col_heading', #设置列名对齐
          'props':[('color','black'),('background-color',facecolor), \
                   ('font-size','17px'),('text-align','center'),('margin','auto')]}])        
    
    #设置数据对齐
    dispt1=dispt.set_properties(**{'font-size':'17px'})
    dispf=dispt1.set_properties(**{'text-align':'center'})
    
    #设置前景背景颜色
    try:
        dispf2=dispf.set_properties(**{'background-color':facecolor,'color':'black'})
    except:
        print("  #Warning(df_directprint): unknown color",facecolor,"\b, changed to default one")
        dispf2=dispf.set_properties(**{'background-color':'papayawhip','color':'black'})

    #打印数据框本身
    from IPython.display import display
    display(dispf2)    
    """
    """    
    #print(dfp.to_string(index=False))
    colalign=['left']+['right']*(len(list(dfp)) - 1)
    print(dfp.to_markdown(tablefmt='Simple',index=False,colalign=colalign))
    """
    
    #解析脚注各行并打印
    """
    if foot_break: print('')
    footnote1=footnote+'\n'
    pos,pos_new=0,0
    while pos_new != -1:
        pos_new=footnote1.find('\n',pos)
        linetxt=footnote1[pos:pos_new]
        #print(linetxt)
        if foot_center:
            blanknum=title_position(linetxt,dfp)
        else:
            blanknum=foot_start-1
        
        if linetxt != '\n':
            if blanknum >2:
                print(' '*blanknum,linetxt) 
            else:
                print(linetxt)
            
        pos=pos_new+1
    """
    #print('') #空一行
    #print(footnote,'\n')    
    
    return 
#==============================================================================

if __name__=='__main__':
    tickers=["000002.SZ","600266.SS",'600383.SS','600048.SS']
    fsdates=['2021-12-31','2020-12-31','2019-12-31','2018-12-31']
    
    tickers=['601328.SS','601398.SS','601288.SS','601988.SS','601939.SS','601658.SS']
    fsdates=['2022-12-31','2021-12-31','2010-12-31','2019-12-31']
    
    df=get_fin_stmt_ak_multi(tickers,fsdates) 
    
    ticker="601328.SS"
    fsdate='2022-12-31'
    items=["货币资金","应收票据","应收账款"]
    dfp=fs_item_analysis_1(df,ticker,fsdate,items)

def fs_item_analysis_1(df,ticker,fsdate,items,title_txt='',notes='', \
                       facecolor='papayawhip',font_size='16px'):
    """
    功能：比较给定财报日期的资产项目、期初数、期末数、变动额和变动幅度%
    """
    
    #循环获取科目
    dfp=pd.DataFrame(columns=['报表项目','期初数', '期末数', '变动额', '变动幅度%'])
    yiyuan=100000000
    
    import math
    for i in items:
        i_value,i_value_qc,dft=select_item(df,ticker,fsdate,i)
        
        """
        if not(i_value != 0 or i_value_qc != 0): 
            print("  #Warning(income_cost_analysis_1): 因其零值而忽略"+i+"项目")
            continue
        """
        
        if not math.isnan(i_value):
            i_value_yy=round(i_value/yiyuan,4)
            i_value_qc_yy=round(i_value_qc/yiyuan,4)
            i_value_chg_yy=round(i_value_yy - i_value_qc_yy,2)
            if not(i_value_qc_yy==0):
                i_value_chg_pct=round(i_value_chg_yy/i_value_qc_yy*100,2)
            #对于变动幅度符号的修正
                if (i_value_chg_pct < 0) and (i_value_qc_yy < 0):
                    i_value_chg_pct=abs(i_value_chg_pct)
            else:
                i_value_chg_pct='-'
        else:
            i_value_qc_yy,i_value_yy,i_value_chg_yy,i_value_chg_pct='-','-','-','-'
        
        row=pd.Series({'报表项目':i,'期初数':i_value_qc_yy, \
                       '期末数':i_value_yy, '变动额':i_value_chg_yy, \
                       '变动幅度%':i_value_chg_pct})
        try:
            dfp=dfp.append(row,ignore_index=True)
        except:
            dfp=dfp._append(row,ignore_index=True)
    
    dfp=dfp.replace(0,'-')  
    dfp=dfp.fillna('-')        
    
    #无序号打印
    if title_txt=='':
        tname=ticker_name(ticker,'stock').replace("(A股)",'')
        title_txt=tname+"财报分析：重要项目的变动情况\n（截至"+fsdate+"）"
    import datetime; todaydt=datetime.date.today()
    #footnote="*单位：亿元，数据来源：新浪财经，"+str(today) 
    #footnote="*单位：亿元，本期报表日期："+fsdate+'，数据来源：新浪财经'
    footnote="单位：亿元，数据来源：新浪财经，"+str(todaydt)
    
    if notes=='':
        foottext=footnote
    else:
        foottext=notes+'\n'+footnote

    #确定表格字体大小
    titile_font_size=font_size
    heading_font_size=data_font_size=str(int(font_size.replace('px',''))-1)+'px'
        
    #df_directprint(dfp,title_txt,foottext,facecolor=facecolor) 
    df_display_CSS(df=dfp,titletxt=title_txt,footnote=foottext, \
                   first_col_align='left', \
                   facecolor=facecolor,decimals=2, \
                   titile_font_size=titile_font_size,heading_font_size=heading_font_size, \
                   data_font_size=data_font_size)    
        
    return dfp


#==============================================================================
if __name__=='__main__':
    tickers=["000002.SZ","600266.SS",'600383.SS','600048.SS']
    fsdates=['2021-12-31','2020-12-31','2019-12-31','2018-12-31']
    df=get_fin_stmt_ak_multi(tickers,fsdates) 
    
    ticker="000002.SZ"
    fsdates=['2021-12-31','2020-12-31','2019-12-31']
    items=["应收账款","资产总计"]
    find_fs_items(df,itemword1="应收账款",itemword2='')
    find_fs_items(df,itemword1="资产",itemword2='计')
    
    dfp=fs_item_analysis_2(df,ticker,fsdates,items)

def fs_item_analysis_2(df,ticker,fsdates,items,title_txt='',notes='', \
                       facecolor='papayawhip',font_size='16px'):
    """
    功能：比较给定财报日期的报表项目、最近几年fsdates、占比%
    """
    fsdates1=sorted(fsdates,reverse=True)
    
    #循环获取科目
    col_list=['报表项目(亿元)']+fsdates1
    dfp=pd.DataFrame(columns=col_list)
    
    yiyuan=100000000
    import math
    
    for i in items:
        row_list=[i]
        for fd in fsdates1:
            i_value,_,_=select_item(df,ticker,fd,i)
            row_list=row_list+[round(i_value/yiyuan,4)]
        dfp.loc[len(dfp)] = row_list
    
    last_row=[items[0]+"占比%"]
    for fd in fsdates1:
        rate=round(dfp[fd][0]/dfp[fd][1]*100,2)
        last_row=last_row+[rate]
    dfp.loc[len(dfp)] = last_row
    
    dfp=dfp.replace(0,'-')
    dfp=dfp.fillna('-')  
        
    #无序号打印
    if title_txt=='':
        tname=ticker_name(ticker,'stock').replace("(A股)",'')
        title_txt=tname+"财报分析：重要项目占比的变动趋势"
    import datetime; todaydt=datetime.date.today()
    footnote="数据来源：新浪财经，"+str(todaydt) 
    
    if notes=='':
        foottext=footnote
    else:
        foottext=notes+'\n'+footnote

    #确定表格字体大小
    titile_font_size=font_size
    heading_font_size=data_font_size=str(int(font_size.replace('px',''))-1)+'px'
        
    #df_directprint(dfp,title_txt,foottext,facecolor=facecolor) 
    df_display_CSS(df=dfp,titletxt=title_txt,footnote=foottext, \
                   first_col_align='left', \
                   facecolor=facecolor,decimals=2, \
                   titile_font_size=titile_font_size,heading_font_size=heading_font_size, \
                   data_font_size=data_font_size)    
        
    return dfp

#==============================================================================
if __name__=='__main__':
    tickers=["000002.SZ","600266.SS",'600383.SS','600048.SS']
    fsdates=['2021-12-31','2020-12-31','2019-12-31','2018-12-31']
    df=get_fin_stmt_ak_multi(tickers,fsdates) 
    
    ticker="000002.SZ"
    fsdates=['2021-12-31','2020-12-31','2019-12-31']
    
    dfp=fs_item_analysis_3(df,ticker,fsdates)

def fs_item_analysis_3(df,ticker,fsdates,title_txt='',notes='', \
                       facecolor='papayawhip',font_size='16px'):
    """
    功能：比较给定财报日期的流动比率、最近几年fsdates
    """
    fsdates1=sorted(fsdates,reverse=True)
    
    #循环获取科目
    col_list=['报表项目(亿元)']+fsdates1
    dfp=pd.DataFrame(columns=col_list)
    yiyuan=100000000

    items=['流动资产合计','流动负债合计']    
    for i in items:
        row_list=[i]
        for fd in fsdates1:
            i_value,_,_=select_item(df,ticker,fd,i)
            row_list=row_list+[round(i_value/yiyuan,4)]
        dfp.loc[len(dfp)] = row_list
    
    last_row=["流动比率%"]
    for fd in fsdates1:
        rate=round(dfp[fd][0]/dfp[fd][1]*100,2)
        last_row=last_row+[rate]
    dfp.loc[len(dfp)] = last_row

    dfp=dfp.replace(0,'-')
    dfp=dfp.fillna('-')  
        
    #无序号打印
    if title_txt=='':
        tname=ticker_name(ticker,'stock').replace("(A股)",'')
        title_txt=tname+"财报分析：流动比率的变动趋势"
    import datetime; todaydt=datetime.date.today()
    footnote="数据来源：新浪财经，"+str(todaydt) 
    
    if notes=='':
        foottext=footnote
    else:
        foottext=notes+'\n'+footnote

    #确定表格字体大小
    titile_font_size=font_size
    heading_font_size=data_font_size=str(int(font_size.replace('px',''))-1)+'px'

    #确定表格字体大小
    titile_font_size=font_size
    heading_font_size=data_font_size=str(int(font_size.replace('px',''))-1)+'px'
        
    #df_directprint(dfp,title_txt,foottext,facecolor=facecolor)    
    df_display_CSS(df=dfp,titletxt=title_txt,footnote=foottext, \
                   first_col_align='left', \
                   facecolor=facecolor,decimals=2, \
                   titile_font_size=titile_font_size,heading_font_size=heading_font_size, \
                   data_font_size=data_font_size)       
    
    return dfp

#==============================================================================
if __name__=='__main__':
    tickers=["000002.SZ","600266.SS",'600383.SS','600048.SS']
    fsdates=['2021-12-31','2020-12-31','2019-12-31','2018-12-31']
    df=get_fin_stmt_ak_multi(tickers,fsdates) 
    
    ticker="000002.SZ"
    fsdates=['2021-12-31','2020-12-31','2019-12-31']
    
    dfp=fs_item_analysis_4(df,ticker,fsdates)

def fs_item_analysis_4(df,ticker,fsdates,title_txt='',notes='', \
                       facecolor='papayawhip',font_size='16px'):
    """
    功能：比较给定财报日期的流动比率、最近几年fsdates
    """
    fsdates1=sorted(fsdates,reverse=True)

    #循环获取科目
    col_list=['报表项目(亿元)']+fsdates1
    dfp=pd.DataFrame(columns=col_list)
    yiyuan=100000000
    
    i='流动资产合计'
    row_list=[i]
    for fd in fsdates1:
        i_value,_,_=select_item(df,ticker,fd,i)
        row_list=row_list+[round(i_value/yiyuan,4)]
    dfp.loc[len(dfp)] = row_list
    
    i='存货'
    row_list=['其中：'+i]
    for fd in fsdates1:
        i_value,_,_=select_item(df,ticker,fd,i)
        row_list=row_list+[round(i_value/yiyuan,4)]
    dfp.loc[len(dfp)] = row_list 
    
    i='速动资产合计'
    row_list=[i]
    for fd in fsdates1:
        rate=round(dfp[fd][0]-dfp[fd][1],2)
        row_list=row_list+[rate]
    dfp.loc[len(dfp)] = row_list
    
    i='流动负债合计'
    row_list=[i]
    for fd in fsdates1:
        i_value,_,_=select_item(df,ticker,fd,i)
        row_list=row_list+[round(i_value/yiyuan,4)]
    dfp.loc[len(dfp)] = row_list
    
    last_row=["速动比率%"]
    for fd in fsdates1:
        rate=round(dfp[fd][2]/dfp[fd][3]*100,2)
        last_row=last_row+[rate]
    dfp.loc[len(dfp)] = last_row

    dfp=dfp.replace(0,'-')
    dfp=dfp.fillna('-')  
    
    #无序号打印
    if title_txt=='':
        tname=ticker_name(ticker,'stock').replace("(A股)",'')
        title_txt=tname+"财报分析：速动比率的变动趋势"
    import datetime; todaydt=datetime.date.today()
    footnote="数据来源：新浪财经，"+str(todaydt) 
    
    if notes=='':
        foottext=footnote
    else:
        foottext=notes+'\n'+footnote

    #确定表格字体大小
    titile_font_size=font_size
    heading_font_size=data_font_size=str(int(font_size.replace('px',''))-1)+'px'
        
    #df_directprint(dfp,title_txt,foottext,facecolor=facecolor)   
    df_display_CSS(df=dfp,titletxt=title_txt,footnote=foottext, \
                   first_col_align='left', \
                   facecolor=facecolor,decimals=2, \
                   titile_font_size=titile_font_size,heading_font_size=heading_font_size, \
                   data_font_size=data_font_size)       
    return dfp

#==============================================================================
if __name__=='__main__':
    tickers=["000002.SZ","600266.SS",'600383.SS','600048.SS']
    fsdates=['2021-12-31','2020-12-31','2019-12-31','2018-12-31']
    df=get_fin_stmt_ak_multi(tickers,fsdates) 
    
    ticker="000002.SZ"
    fsdates=['2021-12-31','2020-12-31','2019-12-31']
    
    dfp=fs_item_analysis_5(df,ticker,fsdates)

def fs_item_analysis_5(df,ticker,fsdates,title_txt='',notes='', \
                       facecolor='papayawhip',font_size='16px'):
    """
    功能：比较给定财报日期的流动比率、最近几年fsdates
    """
    
    #循环获取科目
    col_list=['报表项目(亿元)']+fsdates
    dfp=pd.DataFrame(columns=col_list)
    yiyuan=100000000
    
    fsdates1=sorted(fsdates,reverse=True)
    items=['资产总计','负债合计']    
    for i in items:
        row_list=[i]
        for fd in fsdates1:
            i_value,_,_=select_item(df,ticker,fd,i)
            row_list=row_list+[round(i_value/yiyuan,4)]
        dfp.loc[len(dfp)] = row_list
    
    last_row=["资产负债率%"]
    for fd in fsdates1:
        rate=round(dfp[fd][1]/dfp[fd][0]*100,2)
        last_row=last_row+[rate]
    dfp.loc[len(dfp)] = last_row

    dfp=dfp.replace(0,'-')
    dfp=dfp.fillna('-')  
    
    #无序号打印
    if title_txt=='':
        tname=ticker_name(ticker,'stock').replace("(A股)",'')
        title_txt=tname+"财报分析：资产负债率的变动趋势"
    import datetime; todaydt=datetime.date.today()
    footnote="数据来源：新浪财经，"+str(todaydt) 
    
    if notes=='':
        foottext=footnote
    else:
        foottext=notes+'\n'+footnote

    #确定表格字体大小
    titile_font_size=font_size
    heading_font_size=data_font_size=str(int(font_size.replace('px',''))-1)+'px'
        
    #df_directprint(dfp,title_txt,foottext,facecolor=facecolor)    
    df_display_CSS(df=dfp,titletxt=title_txt,footnote=foottext, \
                   first_col_align='left', \
                   facecolor=facecolor,decimals=2, \
                   titile_font_size=titile_font_size,heading_font_size=heading_font_size, \
                   data_font_size=data_font_size)       
    return dfp

#==============================================================================
if __name__=='__main__':
    tickers=["000002.SZ","600266.SS",'600383.SS','600048.SS']
    fsdates=['2021-12-31','2020-12-31','2019-12-31','2018-12-31']
    df=get_fin_stmt_ak_multi(tickers,fsdates) 
    
    ticker="000002.SZ"
    fsdates=['2021-12-31','2020-12-31']
    items=['应收账款','营业收入']
    
    dfp=fs_item_analysis_6(df,ticker,fsdates,items)

def fs_item_analysis_6_original(df,ticker,fsdates,items,title_txt='',notes=''):
    """
    废弃!!!
    功能：比较给定财报日期的应收账款与营业收入增幅、最近几年fsdates
    """
    
    #循环获取科目
    items1=[]
    for i in items:
        items1=items1+[i+'(亿元)']
    
    col_list=['报表日期']+items1
    dfp=pd.DataFrame(columns=col_list)
    yiyuan=100000000
    
    fsdates1=sorted(fsdates,reverse=False)
    for fd in fsdates1:
        row_list=[fd]
        for i in items:
            i_value,_,_=select_item(df,ticker,fd,i)
            row_list=row_list+[round(i_value/yiyuan,4)]
        dfp.loc[len(dfp)] = row_list
    
    last_row=["增幅%"]
    for i in items1:
        rate=round((dfp[i][1]/dfp[i][0]-1)*100,2)
        last_row=last_row+[rate]
    dfp.loc[len(dfp)] = last_row
    
    # 替换nan
    dfp=dfp.fillna('-')
    dfp=dfp.replace(0,'-')
    
    #无序号打印
    if title_txt=='':
        tname=ticker_name(ticker,'stock').replace("(A股)",'')
        title_txt=tname+"财报分析：重要关联项目的增幅对比"
    import datetime; todaydt=datetime.date.today()
    footnote="数据来源：新浪财经，"+str(todaydt) 
    
    if notes=='':
        foottext=footnote
    else:
        foottext=notes+'\n'+footnote
        
    df_directprint(dfp,title_txt,foottext)    
    
    return dfp
#==============================================================================
if __name__=='__main__':
    tickers=["000002.SZ","600266.SS",'600383.SS','600048.SS']
    fsdates=['2021-12-31','2020-12-31','2019-12-31','2018-12-31']
    df=get_fin_stmt_ak_multi(tickers,fsdates) 
    
    ticker="000002.SZ"
    fsdates=['2021-12-31','2020-12-31']
    items=['应收账款','营业收入']
    
    dfp=fs_item_analysis_6(df,ticker,fsdates,items)

def fs_item_analysis_6(df,ticker,fsdates,items,title_txt='',notes='', \
                       facecolor='papayawhip',font_size='16px'):
    """
    功能：比较给定财报日期的应收账款与营业收入增幅、最近几年fsdates
    """
    
    col_list=['报表日期']+items
    dfp=pd.DataFrame(columns=col_list)
    yiyuan=100000000
    yiyuan_foot=False
    
    fsdates1=sorted(fsdates,reverse=False)
    for fd in fsdates1:
        row_list=[fd]
        for i in items:
            i_value,_,_=select_item(df,ticker,fd,i)
            if not('%' in i) and not('(元)' in i):
                row_list=row_list+[round(i_value/yiyuan,4)]
                yiyuan_foot=True
            else:
                row_list=row_list+[i_value]
        dfp.loc[len(dfp)] = row_list
    
    last_row=["增幅%"]
    for i in items:
        rate=round((dfp[i][1]/dfp[i][0]-1)*100,2)
        last_row=last_row+[rate]
    dfp.loc[len(dfp)] = last_row

    # 替换nan
    dfp=dfp.fillna('-')
    dfp=dfp.replace(0,'-')
    
    #无序号打印
    if title_txt=='':
        tname=ticker_name(ticker,'stock').replace("(A股)",'')
        title_txt=tname+"财报分析：重要关联项目的增幅对比"
    import datetime; todaydt=datetime.date.today()
    if yiyuan_foot:
        footnote="单位：亿元，数据来源：新浪财经，"+str(todaydt) 
    else:
        footnote="数据来源：新浪财经，"+str(todaydt)
        
    if notes=='':
        foottext=footnote
    else:
        foottext=notes+'\n'+footnote

    #确定表格字体大小
    titile_font_size=font_size
    heading_font_size=data_font_size=str(int(font_size.replace('px',''))-1)+'px'
        
    #df_directprint(dfp,title_txt,foottext,facecolor=facecolor) 
    df_display_CSS(df=dfp,titletxt=title_txt,footnote=foottext, \
                   first_col_align='left', \
                   facecolor=facecolor,decimals=2, \
                   titile_font_size=titile_font_size,heading_font_size=heading_font_size, \
                   data_font_size=data_font_size)       
    return dfp

#==============================================================================
if __name__=='__main__':
    tickers=["000002.SZ","600266.SS",'600383.SS','600048.SS']
    fsdates=['2021-12-31','2020-12-31','2019-12-31','2018-12-31']
    df=get_fin_stmt_ak_multi(tickers,fsdates) 

    tickers=["000002.SZ","600266.SS",'600383.SS','600048.SS']
    fsdate='2021-12-31'
    items=['存货','资产总计','存货占比%']
    
    dfp=fs_item_analysis_7(df,tickers,fsdate,items)

def fs_item_analysis_7_original(df,tickers,fsdate,items,title_txt=''):
    """
    废弃!!!
    功能：比较给定财报日期fsdate的项目和指标，与同业相比
    """
    
    #循环获取科目
    items1=[]
    for i in items:
        if not('%' in i):
            items1=items1+[i+'(亿元)']
        else:
            items1=items1+[i]
    
    col_list=['上市公司']+items1
    dfp=pd.DataFrame(columns=col_list)
    yiyuan=100000000
    yiyuan_foot=False
    
    for t in tickers:
        tname=ticker_name(t,'stock').replace("(A股)",'')
        row_list=[tname]
        for i in items:
            i_value,_,_=select_item(df,t,fsdate,i)
            if not('%' in i) and not('(元)' in i):
                row_list=row_list+[round(i_value/yiyuan,4)]
                yiyuan_foot=True
            else:
                row_list=row_list+[i_value]
        dfp.loc[len(dfp)] = row_list
    
    #主要项目排序
    
    dfp=dfp.replace(0,'-')
    dfp=dfp.fillna('-')  
    
    #无序号打印
    if title_txt=='':
        title_txt="=== 重要指标的同行业对比 ==="
        ticker=tickers[0]
        tname=ticker_name(ticker,'stock').replace("(A股)",'')
        title_txt=tname+"财报分析：重要指标的同行业对比\n（截至"+fsdate+"）"
    import datetime; todaydt=datetime.date.today()
    if yiyuan_foot:
        footnote="单位：亿元，数据来源：新浪财经，"+str(todaydt) 
    else:
        footnote="数据来源：新浪财经，"+str(todaydt)
    df_directprint(dfp,title_txt,footnote) 
    
    return dfp
#==============================================================================
if __name__=='__main__':
    tickers=["000002.SZ","600266.SS",'600383.SS','600048.SS']
    fsdates=['2021-12-31','2020-12-31','2019-12-31','2018-12-31']
    df=get_fin_stmt_ak_multi(tickers,fsdates) 

    tickers=["000002.SZ","600266.SS",'600383.SS','600048.SS']
    fsdate='2021-12-31'
    items=['存货','资产总计','存货占比%']
    
    dfp=fs_item_analysis_7(df,tickers,fsdate,items)

def fs_item_analysis_7(df,tickers,fsdate,items,title_txt='',notes='', \
                       facecolor='papayawhip',font_size='16px'):
    """
    功能：比较给定财报日期fsdate的项目和指标，与同业相比
    """
    
    col_list=['上市公司']+items
    dfp=pd.DataFrame(columns=col_list)
    yiyuan=100000000
    yiyuan_foot=False
    
    for t in tickers:
        tname=ticker_name(t,'stock').replace("(A股)",'')
        row_list=[tname]
        for i in items:
            i_value,_,_=select_item(df,t,fsdate,i)
            if not('%' in i) and not('(元)' in i):
                row_list=row_list+[round(i_value/yiyuan,4)]
                yiyuan_foot=True
            else:
                row_list=row_list+[i_value]
        dfp.loc[len(dfp)] = row_list

    dfp=dfp.replace(0,'-')
    dfp=dfp.fillna('-')  
    
    #对主要项目排序
    lastitem=items[1]
    for i in items:
        if '%' in i:
            lastitem=i
            break
        else:
            continue
    
    try:
        dfp.sort_values(by=lastitem,ascending=False,inplace=True)
    except:
        #因混有字符串和数值而排序失败，全转换为字符串再度排序
        dfp[lastitem]=dfp[lastitem].apply(lambda x: str(x))
        dfp.sort_values(by=lastitem,ascending=False,inplace=True)
        
    dfp.reset_index(drop=True,inplace=True)
    dfp.index=dfp.index+1
    
    #无序号打印
    if title_txt=='':
        title_txt="=== 重要指标的同行业对比 ==="
        ticker=tickers[0]
        tname=ticker_name(ticker,'stock').replace("(A股)",'')
        title_txt=tname+"财报分析：重要指标的同行业对比\n（截至"+fsdate+"）"
    import datetime; todaydt=datetime.date.today()
    if yiyuan_foot:
        #footnote="*单位：亿元，数据来源：新浪财经，"+str(today) 
        #footnote="*单位：亿元，本期报表日期："+fsdate+'，数据来源：新浪财经'
        footnote="单位：亿元，数据来源：新浪财经，"+str(todaydt)       
    else:
        #footnote="*数据来源：新浪财经，"+str(today)
        #footnote="*本期报表日期："+fsdate+'，数据来源：新浪财经' 
        footnote='数据来源：新浪财经，'+str(todaydt)
        
    if notes=='':
        foottext=footnote
    else:
        foottext=notes+'\n'+footnote

    #确定表格字体大小
    titile_font_size=font_size
    heading_font_size=data_font_size=str(int(font_size.replace('px',''))-1)+'px'
        
    #df_directprint(dfp,title_txt,foottext,facecolor=facecolor)         
    df_display_CSS(df=dfp,titletxt=title_txt,footnote=foottext, \
                   first_col_align='left', \
                   facecolor=facecolor,decimals=2, \
                   titile_font_size=titile_font_size,heading_font_size=heading_font_size, \
                   data_font_size=data_font_size)       
    return dfp

#==============================================================================
if __name__=='__main__':
    tickers=["000002.SZ","600266.SS",'600383.SS','600048.SS']
    fsdates=['2021-12-31','2020-12-31','2019-12-31','2018-12-31']
    df=get_fin_stmt_ak_multi(tickers,fsdates) 

    tickers=["000002.SZ","600266.SS",'600383.SS','600048.SS']
    fsdate='2021-12-31'
    items=['资产总计','资产负债率%','流动比率%','速动比率%']    
    dfp=fs_item_analysis_8(df,tickers,fsdate,items)

def fs_item_analysis_8(df,tickers,fsdate,items,title_txt='',notes='', \
                       facecolor='papayawhip',font_size='16px'):
    """
    功能：比较给定财报日期fsdate的项目和指标，与同业相比
    区别：项目不带‘(亿元)’字样，避免行过长
    """
    
    #循环获取科目
    col_list=['上市公司']+items
    dfp=pd.DataFrame(columns=col_list)
    yiyuan=100000000
    yiyuan_foot=False
    
    for t in tickers:
        tname=ticker_name(t,'stock').replace("(A股)",'')
        row_list=[tname]
        for i in items:
            i_value,_,_=select_item(df,t,fsdate,i)
            if not('%' in i) and not('(元)' in i):
                row_list=row_list+[round(i_value/yiyuan,4)]
                yiyuan_foot=True
            else:
                row_list=row_list+[i_value]
        dfp.loc[len(dfp)] = row_list
    
    #对主要项目排序
    lastitem=items[1]
    for i in items:
        if '%' in i:
            lastitem=i
            break
        else:
            continue
    
    try:
        dfp.sort_values(by=lastitem,ascending=False,inplace=True)
    except:
        #因混有字符串和数值而排序失败，全转换为字符串再度排序
        dfp[lastitem]=dfp[lastitem].apply(lambda x: str(x))
        dfp.sort_values(by=lastitem,ascending=False,inplace=True)
        
    dfp.reset_index(drop=True,inplace=True)
    dfp.index=dfp.index+1

    dfp=dfp.replace(0,'-')
    dfp=dfp.fillna('-')  
    
    #无序号打印
    if title_txt=='':
        ticker=tickers[0]
        tname=ticker_name(ticker,'stock').replace("(A股)",'')
        title_txt=tname+"财报分析：重要指标的同行业对比\n（截至"+fsdate+"）"

    import datetime; todaydt=datetime.date.today()
    if yiyuan_foot:
        #footnote="*单位：亿元，数据来源：新浪财经，"+str(today) 
        #footnote="*单位：亿元，本期报表日期："+fsdate+'，数据来源：新浪财经'
        footnote="单位：亿元，"+'数据来源：新浪财经，'+str(todaydt)
    else:
        #footnote="*数据来源：新浪财经，"+str(today)
        #footnote="*本期报表日期："+fsdate+'，数据来源：新浪财经'
        footnote='数据来源：新浪财经，'+str(todaydt)
    
    if notes=='':
        foottext=footnote
    else:
        foottext=notes+'\n'+footnote

    #确定表格字体大小
    titile_font_size=font_size
    heading_font_size=data_font_size=str(int(font_size.replace('px',''))-1)+'px'
        
    #df_directprint(dfp,title_txt,foottext,facecolor=facecolor) 
    df_display_CSS(df=dfp,titletxt=title_txt,footnote=foottext, \
                   first_col_align='left', \
                   facecolor=facecolor,decimals=2, \
                   titile_font_size=titile_font_size,heading_font_size=heading_font_size, \
                   data_font_size=data_font_size)       
    return dfp

#==============================================================================
if __name__=='__main__':
    tickers=["000002.SZ","600266.SS",'600383.SS','600048.SS']
    fsdates=['2022-12-31','2021-12-31','2020-12-31','2019-12-31']
    asset_liab_structure_china(tickers,fsdates)

def asset_liab_china(tickers,fsdates,facecolor='papayawhip',font_size='16px'):
    """
    套壳函数asset_liab_structure_china
    """
    asset_liab_structure_china(tickers,fsdates,facecolor=facecolor,font_size=font_size)
    
    return

    
def asset_liab_structure_china(tickers,fsdates,facecolor='papayawhip',font_size='16px'):
    """
    功能：分析上市公司的资产负债基本结构，并与同业公司对比。
    注意1：分析近三期情况，fsdates要给出四个报表日期，以便获得期初数。
    注意2：可以分析连续的年报或季报，但不能混个年报和季报。
    注意3：tickers中的第一家公司为主要分析对象。
    注意4：fsdates中的日期要降序排列，第一个日期建议为最近的财报日。
    """  
    # 检查证券个数
    if isinstance(tickers,str):
        print("  #Warning(asset_liab_structure_china): expecting multiple tickers in a list for",tickers)
        return
    
    # 检查财报日期个数
    if isinstance(fsdates,str):
        
        fsdateslist=[fsdates]
        y4int=int(fsdates[0:4])
        mmddstr=fsdates[4:len(fsdates)]
        for y in range(1,4):
            y4next=y4int - y
            fsdateslist=fsdateslist+[str(y4next)+mmddstr]
        print("  #Notice(asset_liab_structure_china): extended to 4 dates for financial statements")
        fsdates=fsdateslist
    
    # 检查日期个数是否为4个，最后一个作为上期对比。最终列示前3项的结果
    if len(fsdates) <= 3:
        print("  #Warning(asset_liab_structure_china): expecting 4 consecutive dates for financial statements")
        return
    
    comparator=tickers[0]
    comparee=tickers[1:]
    print("  Conducting asset-liability analysis ...")
    print("  Focus on:",ticker_name(comparator,'stock'))
    #print("  Comparee  :",ticker_name(comparee))
    print("  Peers:",end='')
    if comparee != []:
        print_list(ticker_name(comparee,'stock'))
    else:
        print(" N/A")
        
    #主要分析对象
    ticker=tickers[0]
    
    #将日期规范化，以便排序正确
    fsdates1=[]
    for d in fsdates:
        result,fd=check_date2(d)
        if not result:
            print("  #Warning(asset_liab_structure_china): invalid date",d)
            return
        fsdates1=fsdates1+[fd]
    fsdates=fsdates1
    
    #检查是否定期报告日期
    reportdates=['03-31','06-30','09-30','12-31']
    for d in fsdates:
        mm_dd=d[5:]
        if not (mm_dd in reportdates):
            print("  #Warning(asset_liab_structure_china): invalid date for financial statements in China",d)
            return
    
    #最近的财报日
    fsdates=sorted(fsdates,reverse=True)
    fsdate=fsdates[0]
    
    #获取所有比较公司tickers的所有财报fsdates
    df=get_fin_stmt_ak_multi(tickers,fsdates) 
    if df is None:
            print("  #Warning(asset_liab_structure_china): failed to retrieve any info for tickers in the periods")
            print("  Solution: check ticker spelling and try at least 10 minutes later")
            return
    
    #title_head=ticker_name(comparator,'stock')+"资产负债分析："
    title_head=ticker_name(comparator,'stock')+"："
    
    ### 资产负债表的主要项目
    #资产变动趋势2
    title_txt=title_head+"主要资产项目，"+fsdate
    items2=["货币资金","应收账款","存货","长期股权投资","固定资产净额","资产总计"]
    """
    notes1="注1：货币资金包括库存现金、银行存款和其他货币资金三个部分"
    notes2="注2：其他货币资金包括银行汇(本)票存款、信用证保证金存款和信用卡存款等"
    notes3="注3：长期股权投资是指企业对其子公司、合营企业及联营企业的权益性投资"
    notes4="注4：固定资产净额 = 固定资产原值 - 累计折旧 - 资产减值准备"
    """
    notes1="注：\n货币资金包括库存现金、银行存款和其他货币资金三个部分"
    notes2="其他货币资金包括银行汇(本)票存款、信用证保证金存款和信用卡存款等"
    notes3="长期股权投资是指企业对其子公司、合营企业及联营企业的权益性投资"
    notes4="固定资产净额 = 固定资产原值 - 累计折旧 - 资产减值准备"
    
    notes=notes1+'\n'+notes2+'\n'+notes3+'\n'+notes4
    dfp2=fs_item_analysis_1(df,ticker,fsdate,items2,title_txt,notes, \
                            facecolor=facecolor,font_size=font_size)
    
    #负债变动趋势
    title_txt=title_head+"主要负债项目，"+fsdate
    items3=["短期借款","长期借款","应付账款","预收款项","应交税费","应付职工薪酬","负债合计"]
    dfp3=fs_item_analysis_1(df,ticker,fsdate,items3,title_txt, \
                            facecolor=facecolor,font_size=font_size)
    
    #所有者权益变动趋势
    title_txt=title_head+"主要权益项目，"+fsdate
    items4=["实收资本(或股本)","资本公积","盈余公积","未分配利润","所有者权益合计"]
    """
    notes1="注1：实收资本(或股本，Paid-in Capital)指企业实际收到的投资人投入的资本"
    notes2="注2：资本公积是由股东投入的因故不能计入实收资本(或股本)中的那部分投入资金"
    notes3="     资本公积包括资本(股本)溢价、其他资本公积、资产评估增值、资本折算差额"
    notes4="     资本(股本)溢价是公司发行权益证券时价格超出票面价值的部分"
    notes5="     其他资本公积包括金融资产公允价值变动、被投资单位净利润以外的变动等"
    notes6="     资产评估增值是重估企业资产时，重估价高于资产的账面净值的部分"
    notes7="     资本折算差额是外币资本因汇率变动产生的差额"
    notes8="注3：盈余公积是企业按照要求从税后利润中提取的、属于留存收益范畴的资金"
    notes9="     企业从历年利润中提取的留存于企业的内部积累，包括盈余公积和未分配利润"
    notes10="     公司制企业的盈余公积包括法定盈余公积和任意盈余公积"
    notes11="     法定盈余公积是指企业按照规定比例从净利润中必须提取的盈余公积"
    notes12="     任意盈余公积是指企业内部可自主决定比例提取的盈余公积"
    notes13="     企业提取的盈余公积可用于弥补亏损、转增资本、发放现金股利或利润等"
    notes14="注4：未分配利润是净利润经弥补亏损、提取盈余公积和向投资者分配利润后的资金"
    """
    notes1="注：\n实收资本(或股本，Paid-in Capital)指企业实际收到的投资人投入的资本"
    notes2="资本公积是由股东投入的因故不能计入实收资本(或股本)中的那部分投入资金"
    notes3="资本公积包括资本(股本)溢价、其他资本公积、资产评估增值、资本折算差额"
    notes4="资本(股本)溢价是公司发行权益证券时价格超出票面价值的部分"
    notes5="其他资本公积包括金融资产公允价值变动、被投资单位净利润以外的变动等"
    notes6="资产评估增值是重估企业资产时，重估价高于资产的账面净值的部分"
    notes7="资本折算差额是外币资本因汇率变动产生的差额"
    notes8="盈余公积是企业按照要求从税后利润中提取的、属于留存收益范畴的资金"
    notes9="企业从历年利润中提取的留存于企业的内部积累，包括盈余公积和未分配利润"
    notes10="公司制企业的盈余公积包括法定盈余公积和任意盈余公积"
    notes11="法定盈余公积是指企业按照规定比例从净利润中必须提取的盈余公积"
    notes12="任意盈余公积是指企业内部可自主决定比例提取的盈余公积"
    notes13="企业提取的盈余公积可用于弥补亏损、转增资本、发放现金股利或利润等"
    notes14="未分配利润是净利润经弥补亏损、提取盈余公积和向投资者分配利润后的资金"
    
    notesA=notes1+'\n'+notes2+'\n'+notes3+'\n'+notes4+'\n'+notes5+'\n'+notes6+'\n'+notes7
    notesB=notes8+'\n'+notes9+'\n'+notes10+'\n'+notes11+'\n'+notes12+'\n'+notes13+'\n'+notes14
    
    notes=notesA+'\n'+notesB
    dfp4=fs_item_analysis_1(df,ticker,fsdate,items4,title_txt,notes, \
                            facecolor=facecolor,font_size=font_size)
    
    ### 货币资金与应收项目    
    #资产变动趋势1："货币资金","应收票据","应收账款"
    title_txt=title_head+"货币资金与应收项目，"+fsdate
    items1=["货币资金","应收票据","应收账款"]
    dfp1=fs_item_analysis_1(df,ticker,fsdate,items1,title_txt, \
                            facecolor=facecolor,font_size=font_size)
    
    #应收账款占比变动分析
    fsdates1=fsdates[:3]
    items5=["应收账款","资产总计"]
    title_txt=title_head+"应收账款占比变动情况"
    dfp5=fs_item_analysis_2(df,ticker,fsdates1,items5,title_txt, \
                            facecolor=facecolor,font_size=font_size)

    #应收与营业收入增幅对比    
    fsdates2=fsdates[:2]
    items6=['应收账款',"应收票据",'营业总收入']
    title_txt=title_head+"应收项目与营业收入增幅对比"
    dfp6=fs_item_analysis_6(df,ticker,fsdates2,items6,title_txt, \
                            facecolor=facecolor,font_size=font_size)

    #应收账款占比同行对比
    items7=['应收账款','资产总计','应收账款占比%']
    #title_txt=title_head+"应收账款占比同行对比"
    title_txt="应收账款占比同行对比："+fsdate
    dfp7=fs_item_analysis_7(df,tickers,fsdate,items7,title_txt, \
                            facecolor=facecolor,font_size=font_size)        

    ### 存货
    #存货占比变动分析
    items8=["存货","资产总计"]
    title_txt=title_head+"存货占比变动情况"
    dfp8=fs_item_analysis_2(df,ticker,fsdates1,items8,title_txt, \
                            facecolor=facecolor,font_size=font_size)
    """
    items9=["存货","营业总收入"]
    dfp9=fs_item_analysis_6(df,ticker,fsdates2,items9)
    """
    #存货与营业收入增幅对比分析            
    items10=['存货','流动资产合计',"速动资产合计","资产总计"]
    title_txt=title_head+"存货与资产项目增幅对比"
    dfp10=fs_item_analysis_6(df,ticker,fsdates2,items10,title_txt, \
                             facecolor=facecolor,font_size=font_size)

    #存货占比与行业对比        
    items11=['存货','资产总计','存货占比%']
    #title_txt=title_head+"存货占比情况同行对比"
    title_txt="存货占比情况同行对比："+fsdate
    dfp11=fs_item_analysis_7(df,tickers,fsdate,items11,title_txt, \
                             facecolor=facecolor,font_size=font_size)

    ### 偿债能力
    #流动比率变动分析
    title_txt=title_head+"流动比率变动情况"
    dfp12=fs_item_analysis_3(df,ticker,fsdates1,title_txt, \
                             facecolor=facecolor,font_size=font_size)    

    #速动比率变动分析
    title_txt=title_head+"速动比率变动情况"
    dfp13=fs_item_analysis_4(df,ticker,fsdates1,title_txt, \
                             facecolor=facecolor,font_size=font_size)    

    #资产负债率变动分析
    title_txt=title_head+"资产负债率变动情况"
    dfp14=fs_item_analysis_5(df,ticker,fsdates1,title_txt, \
                             facecolor=facecolor,font_size=font_size)    

    #资产负债率同行比较
    #title_txt=title_head+"资产负债率同行比较"
    title_txt="资产负债率同行比较："+fsdate
    items15=['资产总计','资产负债率%','流动比率%','速动比率%']
    dfp15=fs_item_analysis_8(df,tickers,fsdate,items15,title_txt, \
                             facecolor=facecolor,font_size=font_size)

    return    
    
#==============================================================================
if __name__=='__main__':
    tickers=["000002.SZ","600266.SS",'600383.SS','600048.SS']
    fsdates=['2021-12-31','2020-12-31','2019-12-31','2018-12-31']
    income_cost_structure_china(tickers,fsdates)

def income_cost_china(tickers,fsdates,facecolor='papayawhip',font_size='16px'):    
    """
    套壳函数income_cost_structure_china
    """
    income_cost_structure_china(tickers,fsdates,facecolor=facecolor,font_size=font_size)
    
    return
    
def income_cost_structure_china(tickers,fsdates,facecolor='papayawhip',font_size='16px'):
    """
    功能：分析上市公司的收入成本基本结构，并与同业公司对比。
    注意1：分析近三期情况，fsdates要给出四个报表日期，以便获得期初数。
    注意2：可以分析连续的年报或季报，但不能混个年报和季报。
    注意3：tickers中的第一家公司为主要分析对象。
    注意4：fsdates中的日期要降序排列，第一个日期建议为最近的财报日。
    """ 
    # 检查证券个数
    if isinstance(tickers,str):
        print("  #Warning(income_cost_structure_china): expecting multiple tickers in a list for",tickers)
        return
    
    # 检查财报日期个数
    if isinstance(fsdates,str):
        fsdateslist=[fsdates]
        y4int=int(fsdates[0:4])
        mmddstr=fsdates[4:len(fsdates)]
        for y in range(1,4):
            y4next=y4int - y
            fsdateslist=fsdateslist+[str(y4next)+mmddstr]
        print("  #Warning(income_cost_structure_china): extended to 4 dates for financial statements")
        fsdates=fsdateslist
    
    # 检查日期个数是否为4个，最后一个作为上期对比。最终列示前3项的结果
    if len(fsdates) <= 3:
        print("  #Warning(income_cost_structure_china): expecting 4 consecutive dates for financial statements")
        return

    #将日期规范化，以便排序正确
    fsdates1=[]
    for d in fsdates:
        result,fd=check_date2(d)
        if not result:
            print("  #Warning(income_cost_structure_china): invalid date",d)
            return
        fsdates1=fsdates1+[fd]
    fsdates=fsdates1
    
    comparator=tickers[0]
    comparee=tickers[1:]
    print("  Conducting income-cost analysis ...")
    print("  Focus on:",ticker_name(comparator,'stock'))
    #print("  Comparee  :",ticker_name(comparee))
    print("  Peers:",end='')
    if comparee != []:
        print_list(ticker_name(comparee,'stock'))
    else:
        print(" N/A")
    
    #主要分析对象
    ticker=tickers[0]
    #最近的财报日
    fsdates=sorted(fsdates,reverse=True)
    fsdate=fsdates[0]
    
    #获取所有比较公司tickers的所有财报fsdates
    df=get_fin_stmt_ak_multi(tickers,fsdates) 
    if df is None:
            print("  #Warning(income_cost_structure_china): failed to retrieve info for the tickers in the dates")
            #print("  Possible reasons: no access to data source or invalid tickers")
            return
    
    title_head=ticker_name(comparator,'stock')+"："
    
    #收入成本总体变动趋势
    title_txt=title_head+"主要利润表项目，"+fsdate
    items1=["营业总收入","营业总成本","营业成本","毛利润","营业利润","营业外收支","税前利润","所得税费用","净利润","归母净利润"]
    dfp1=fs_item_analysis_1(df,ticker,fsdate,items1,title_txt, \
                            facecolor=facecolor,font_size=font_size)
    
    #成本变动趋势
    title_txt=title_head+"主要成本费用项目，"+fsdate
    print('')
    """
    items2=["营业总成本","营业成本","营业税金及附加","销售费用","管理费用","研发费用",
            "应付利息","公允价值变动损失","非流动资产处置损失",
            "资产减值损失","营业外支出"]
    """
    items2=["营业总成本","营业成本","营业税金及附加","销售费用","管理费用","研发费用",
            "应付利息","非流动资产处置损失",
            "资产减值损失","营业外支出"]
    dfp2=fs_item_analysis_1(df,ticker,'2021-12-31',items2,title_txt, \
                            facecolor=facecolor,font_size=font_size)
    
    #占比变动分析：近三年
    title_txt=title_head+"营业总成本占营业总收入比例情况"
    fsdates1=fsdates[:3]
    items3=["营业总成本","营业总收入"]
    """
    notes1="注1：营业总成本包括营业成本、营业税金及附加、三大费用和资产减值损失"
    notes2="注2：营业收入=主营业务收入和其他非主营业务收入"
    notes3="注3：营业总收入=营业收入+非营业收入(投资收益、营业外收入等)"
    """
    notes1="注：\n营业总成本包括营业成本、营业税金及附加、三大费用和资产减值损失"
    notes2="营业收入=主营业务收入和其他非主营业务收入"
    notes3="营业总收入=营业收入+非营业收入(投资收益、营业外收入等)"
    
    notes=notes1+'\n'+notes2+'\n'+notes3
    dfp3=fs_item_analysis_2(df,ticker,fsdates1,items3,title_txt,notes, \
                            facecolor=facecolor,font_size=font_size)
    #====================================================================
    title_txt=title_head+"营业成本占营业总成本比例情况"
    items4=["营业成本","营业总成本"]
    """
    notes1="注1：营业成本是经营活动中发生的可归属于产品/劳务成本等的费用"
    notes2="注2：营业总成本包括营业成本、营业税金及附加、三大费用和资产减值损失"
    """
    notes1="注：\n营业成本是经营活动中发生的可归属于产品/劳务成本等的费用"
    notes2="营业总成本包括营业成本、营业税金及附加、三大费用和资产减值损失"
    
    notes=notes1+'\n'+notes2
    dfp4=fs_item_analysis_2(df,ticker,fsdates1,items4,title_txt,notes, \
                            facecolor=facecolor,font_size=font_size)
    
    title_txt=title_head+"营业成本占营业总收入比例情况"
    items5=["营业成本","营业总收入"]
    dfp5=fs_item_analysis_2(df,ticker,fsdates1,items5,title_txt, \
                            facecolor=facecolor,font_size=font_size)

    title_txt=title_head+"营业成本增幅分析"
    fsdates2=fsdates[:2]
    items12=['营业成本','营业总成本','营业总收入']
    dfp12=fs_item_analysis_6(df,ticker,fsdates2,items12,title_txt, \
                             facecolor=facecolor,font_size=font_size)

    #====================================================================
    title_txt=title_head+"销售费用占营业总收入比例情况"
    items6=["销售费用","营业总收入"]
    
    notes="注：销售费用是企业销售过程中发生的各种费用"
    dfp6=fs_item_analysis_2(df,ticker,fsdates1,items6,title_txt,notes, \
                            facecolor=facecolor,font_size=font_size)
    #====================================================================
    title_txt=title_head+"管理费用占营业总收入比例情况"
    items7=["管理费用","营业总收入"]
    
    notes="注：管理费用是行政管理部门为组织生产/经营活动发生的各种费用"
    dfp7=fs_item_analysis_2(df,ticker,fsdates1,items7,title_txt,notes, \
                            facecolor=facecolor,font_size=font_size)
    
    #title_txt=title_head+"三项费用率同行对比"
    title_txt="三项费用率同行对比："+fsdate
    items14=['营业总收入','销售费用率%','管理费用率%','研发费用率%']
    """
    notes1="注1：销售费用率 = 销售费用 / 营业总收入"
    notes2="注2：管理费用率 = 管理费用 / 营业总收入"
    notes3="注3：研发费用率 = 研发费用 / 营业总收入"
    """
    notes1="注：\n销售费用率 = 销售费用 / 营业总收入"
    notes2="管理费用率 = 管理费用 / 营业总收入"
    notes3="研发费用率 = 研发费用 / 营业总收入"
    
    notes=notes1+'\n'+notes2+'\n'+notes3
    
    dfp12=fs_item_analysis_8(df,tickers,fsdate,items14,title_txt,notes, \
                             facecolor=facecolor,font_size=font_size)    
    #====================================================================
    title_txt=title_head+"毛利润占营业总收入比例情况"
    items8=["毛利润","营业总收入"]
    dfp8=fs_item_analysis_2(df,ticker,fsdates1,items8,title_txt, \
                            facecolor=facecolor,font_size=font_size)
    #====================================================================
    title_txt=title_head+"营业利润占营业总收入比例情况"
    items9=["营业利润","营业总收入"]
    dfp8=fs_item_analysis_2(df,ticker,fsdates1,items9,title_txt, \
                            facecolor=facecolor,font_size=font_size)
    #====================================================================
    title_txt=title_head+"税前利润占营业总收入比例情况"
    items10=["税前利润","营业总收入"]
    dfp9=fs_item_analysis_2(df,ticker,fsdates1,items10,title_txt, \
                            facecolor=facecolor,font_size=font_size)
    #====================================================================
    title_txt=title_head+"净利润占营业总收入比例情况"
    items11=["净利润","营业总收入"]
    dfp9=fs_item_analysis_2(df,ticker,fsdates1,items11,title_txt, \
                            facecolor=facecolor,font_size=font_size)

    #增幅分析：近两年  
    title_txt=title_head+"四种利润对比"
    items13=['毛利润','营业利润','税前利润','净利润']
    dfp11=fs_item_analysis_6(df,ticker,fsdates2,items13,title_txt, \
                             facecolor=facecolor,font_size=font_size)

    #同行比较
    #title_txt=title_head+"利润率同行对比"
    title_txt="利润率同行对比："+fsdate
    #items15=['营业利润','营业利润率%','税前利润率%','实际所得税率%','净利润','净利润率%']
    #items15=['毛利润率%','营业利润率%','税前利润率%','净利润率%']
    items15=['净利润率%','税前利润率%','营业利润率%','毛利润率%']
    dfp12=fs_item_analysis_8(df,tickers,fsdate,items15,title_txt, \
                             facecolor=facecolor,font_size=font_size)

    return    

#==============================================================================
if __name__=='__main__':
    tickers=["000002.SZ","600266.SS",'600383.SS','600048.SS']
    fsdates=['2021-12-31','2020-12-31','2019-12-31','2018-12-31']
    cash_flow_structure_china(tickers,fsdates)

def cash_flow_china(tickers,fsdates,facecolor='papayawhip',font_size='16px'):
    """
    套壳函数cash_flow_structure_china
    """
    cash_flow_structure_china(tickers,fsdates,facecolor=facecolor,font_size=font_size)
    
    return
    
    
def cash_flow_structure_china(tickers,fsdates,facecolor='papayawhip',font_size='16px'):
    """
    功能：分析上市公司的现金流量基本结构，并与同业公司对比。
    注意1：分析近三期情况，fsdates要给出四个报表日期，以便获得期初数。
    注意2：可以分析连续的年报或季报，但不能混个年报和季报。
    注意3：tickers中的第一家公司为主要分析对象。
    注意4：fsdates中的日期要降序排列，第一个日期建议为最近的财报日。
    """  
    if isinstance(tickers,str):
        print("  #Warning(cash_flow_structure_china): expecting multiple tickers in a list for",tickers)
        return
    
    # 检查财报日期个数
    if isinstance(fsdates,str):
        fsdateslist=[fsdates]
        y4int=int(fsdates[0:4])
        mmddstr=fsdates[4:len(fsdates)]
        for y in range(1,4):
            y4next=y4int - y
            fsdateslist=fsdateslist+[str(y4next)+mmddstr]
        print("  #Warning(cash_flow_structure_china): extended to 4 dates for financial statements")
        fsdates=fsdateslist
    
    # 检查日期个数是否为4个，最后一个作为上期对比。最终列示前3项的结果
    if len(fsdates) <= 3:
        print("  #Warning(cash_flow_structure_china): expecting 4 consecutive dates for financial statements")
        return

    #将日期规范化，以便排序正确
    fsdates1=[]
    for d in fsdates:
        result,fd=check_date2(d)
        if not result:
            print("  #Warning(cash_flow_structure_china): invalid date",d)
            return
        fsdates1=fsdates1+[fd]
    fsdates=fsdates1
    
    comparator=tickers[0]
    comparee=tickers[1:]
    print("  Conducting cash flow analysis ...")
    print("  Focus on:",ticker_name(comparator,'stock'))
    print("  Peers:",end='')
    if comparee != []:
        print_list(ticker_name(comparee,'stock'))
    else:
        print(" N/A")
   
    #主要分析对象
    ticker=tickers[0]
    #最近的财报日
    fsdates=sorted(fsdates,reverse=True)
    fsdate=fsdates[0]
    
    #获取所有比较公司tickers的所有财报fsdates
    df=get_fin_stmt_ak_multi(tickers,fsdates) 
    if df is None:
            print("  #Warning(cash_flow_structure_china): failed to retrieve info for the tickers in the dates")
            #print("  Possible reasons: no access to data source or invalid tickers")
            return    
    
    title_head=ticker_name(comparator,'stock')+"："
    
    #总体变动趋势
    title_txt=title_head+"主要现金流项目，"+fsdate
    items1=["经营活动现金流净额","经营活动现金流入","经营活动现金流出",
            "投资活动现金流净额","投资活动现金流入","投资活动现金流出",
            "筹资活动现金流净额","筹资活动现金流入","筹资活动现金流出",
            "汇率对现金流的影响","现金流量净增加额"]
    dfp1=fs_item_analysis_1(df,ticker,fsdate,items1,title_txt, \
                            facecolor=facecolor,font_size=font_size)
    
    #占比变动分析：近三年
    title_txt=title_head+"经营活动现金流入占比情况"
    fsdates1=fsdates[:3]
    items3=["经营活动现金流入","营业总收入"]
    dfp3=fs_item_analysis_2(df,ticker,fsdates1,items3,title_txt, \
                            facecolor=facecolor,font_size=font_size)

    title_txt=title_head+"经营活动现金流净额占比情况"
    items4=["经营活动现金流净额","营业利润"]
    dfp3=fs_item_analysis_2(df,ticker,fsdates1,items4,title_txt, \
                            facecolor=facecolor,font_size=font_size)

    #增幅分析：近两年 
    title_txt=title_head+"经营活动现金流增幅情况"
    fsdates2=fsdates[:2]
    items12=['经营活动现金流入','经营活动现金流出','经营活动现金流净额']
    dfp12=fs_item_analysis_6(df,ticker,fsdates2,items12,title_txt, \
                             facecolor=facecolor,font_size=font_size)

    #同行比较
    title_txt=title_head+"现金收入能力同行比较，"+fsdate
    items16=['销售现金比率%','现金购销比率%','营业现金回笼率%']
    """
    notes1="注1：销售现金比率 = 经营活动现金流入 / 营业总收入"
    notes2="注2：现金购销比率 = 经营活动现金流出 / 经营活动现金流入"
    notes3="注3：营业现金回笼率 = 经营活动现金流入 / 营业总收入"
    """
    notes1="注：\n销售现金比率 = 经营活动现金流入 / 营业总收入"
    notes2="现金购销比率 = 经营活动现金流出 / 经营活动现金流入"
    notes3="营业现金回笼率 = 经营活动现金流入 / 营业总收入"
    
    notes=notes1+'\n'+notes2+'\n'+notes3
    dfp12=fs_item_analysis_8(df,tickers,fsdate,items16,title_txt,notes, \
                             facecolor=facecolor,font_size=font_size)  
    
    title_txt=title_head+"现金偿债能力同行比较，"+fsdate
    items14=['短期现金偿债能力%','长期现金偿债能力%']
    """
    notes1="注1：短期现金偿债能力 = 经营活动现金流净额 / 流动负债合计"
    notes2="注2：长期现金偿债能力 = 经营活动现金流净额 / 负债合计"
    """
    notes1="注：\n短期现金偿债能力 = 经营活动现金流净额 / 流动负债合计"
    notes2="长期现金偿债能力 = 经营活动现金流净额 / 负债合计"
    
    notes=notes1+'\n'+notes2
    dfp12=fs_item_analysis_8(df,tickers,fsdate,items14,title_txt,notes, \
                             facecolor=facecolor,font_size=font_size)
    
    title_txt=title_head+"现金支付能力同行比较，"+fsdate
    items15=['现金支付股利能力(元)','现金综合支付能力%','支付给职工的现金比率%']
    """
    notes1="注1：现金支付股利能力 = 经营活动现金流净额 / 流通股股数"
    notes2="注2：现金综合支付能力 = 经营活动现金流净额 / 所有者权益合计"
    notes3="注3：支付给职工的现金比率 = 支付给(为)职工支付的现金 / 经营活动现金流入"
    """
    notes1="注：\n现金支付股利能力 = 经营活动现金流净额 / 流通股股数"
    notes2="现金综合支付能力 = 经营活动现金流净额 / 所有者权益合计"
    notes3="支付给职工的现金比率 = 支付给(为)职工支付的现金 / 经营活动现金流入"
    
    notes=notes1+'\n'+notes2+'\n'+notes3
    dfp12=fs_item_analysis_8(df,tickers,fsdate,items15,title_txt,notes, \
                             facecolor=facecolor,font_size=font_size)

    title_txt=title_head+"财务指标含金量同行比较，"+fsdate
    items17=['盈利现金比率%','现金流入流出比率%','资产现金回收率%']
    """
    notes1="注1：盈利现金比率 = 经营活动现金流净额 / 净利润"
    notes2="注2：现金流入流出比率 = 经营活动现金流入 / 经营活动现金流出"
    notes3="注3：资产现金回收率 = 经营活动现金流净额 / 资产总计"
    """
    notes1="注：\n盈利现金比率 = 经营活动现金流净额 / 净利润"
    notes2="现金流入流出比率 = 经营活动现金流入 / 经营活动现金流出"
    notes3="资产现金回收率 = 经营活动现金流净额 / 资产总计"
    
    notes=notes1+'\n'+notes2+'\n'+notes3
    dfp12=fs_item_analysis_8(df,tickers,fsdate,items17,title_txt,notes, \
                             facecolor=facecolor,font_size=font_size)
    
    return

#==============================================================================
if __name__=='__main__':
    date1='2022-12-31'
    num=4
    gen_yoy_dates(date1,4)
    
def gen_yoy_dates(date1,num=4):
    """
    功能：生成date1的num个同比的日期
    """
    if not isinstance(date1,str):
        print("  #Error(gen_yoy_dates): invalid date",date1)
        return date1

    y4=int(date1[:4])
    mmdd=date1[4:]
    
    datelist=[]
    for i in range(0,num):
        date_tmp=str(y4-i)+mmdd
        datelist=datelist+[date_tmp]
        
    return datelist



if __name__=='__main__':
    tickers=["000002.SZ","600266.SS",'600383.SS','600048.SS']
    fsdates='2021-12-31'
    analysis_type='Balance Sheet'
    analysis_type='Income Statement'
    analysis_type='Cash Flow Statement'
    
    fs_analysis_china(tickers,fsdates,analysis_type='balance sheet')
    fs_analysis_china(tickers,fsdates,analysis_type='income statement')
    fs_analysis_china(tickers,fsdates,analysis_type='cash flow statement')

    tickers=["000002.SZ","600266.SS",'600383.SS','600048.SS']    
    fsdates=['2021-12-31','2020-12-31','2019-12-31','2018-12-31']
    fs_analysis_china(tickers,fsdates,analysis_type='fs summary')
    fs_analysis_china(tickers,fsdates,analysis_type='financial indicator')
    
    tickers='000001.SZ'
    fs_analysis_china(tickers,fsdates,analysis_type='profile')
    fs_analysis_china(tickers,fsdates,analysis_type='profile',category='shareholder')
    fs_analysis_china(tickers,fsdates,analysis_type='profile',category='dividend')
    fs_analysis_china(tickers,fsdates,analysis_type='profile',category='business')
    fs_analysis_china(tickers,fsdates,analysis_type='profile',category='business',business_period='annual')
    fs_analysis_china(tickers,fsdates,analysis_type='profile',category='valuation')
    fs_analysis_china(tickers,fsdates,analysis_type='profile',category='financial')

def fs_analysis_china(tickers,fsdates=[],analysis_type='balance sheet', \
                      category='profile',business_period='recent', \
                      sort='PM',printout=False,gview=False, \
                      loc1='best',loc2='best', \
                      facecolor='papayawhip',font_size='16px'):
    """
    ===========================================================================
    功能：财务报表分析，仅适用于中国A股，注意不适用于港股和美股（含中概股）
    
    选项tickers：必选
        单只股票：用于单只股票历史财报对比
        股票列表：用于股票之间同期财报横向对比
        
    选项fsdates：必选   
        单个财报日期：适用于选项tickers为股票列表时
        财报日期列表：适用于选项tickers为单只股票时，至少四个财报日期，便于对比
    
    选项analysis_type: 
        资产负债表分析(默认)：balance sheet, asset liability
        利润表分析：income statement, cost, expense, earning
        现金流量表分析：cash flow, cashflow statement
        财报概述：financial summary
        财务指标：financial indicator
        股票画像：stock profile, 下面还可分别选择不同的category项目
        杜邦分析：dupont identify, dupont analysis
        杜邦分解：dupont decompose，需要安装graphviz插件
    
    选项category: 
        基本信息(默认)：profile
        股东信息：shareholder
        历史分红：dividend
        主营业务：business，目前无法获取数据！
        市场估值：valuation
        财务概况：financial    
    
    选项business_period：
        最新(默认)：recent，可能为最新可获得的季报或中报或年报
        最新的季报：quarterly
        最新的中报：semiannual
        最新的年报：annual
    
    选项loc1/loc2：适用于需要绘图时指定图例的位置，仅在双图例重叠时手动调整
    
    选项facecolor：指定表格/绘图的背景颜色
        烟白色(默认)：whitesmoke
        其他颜色：参见matplotlib颜色列表，例如淡雅小麦色papayawhip
    
    示例：
    千方科技='002373.SZ'
    # 企业快照1：大股东
    sp1=fs_analysis_china(千方科技,analysis_type='profile',category='shareholder')
    # 企业快照2：主营业务
    sp2 = fs_analysis_china(千方科技, analysis_type='profile', category='business')
    # 企业快照3：股利分红
    sp3=fs_analysis_china(千方科技,analysis_type='profile',category='dividend')
    # 企业快照4：财务概况
    sp4 = fs_analysis_china(千方科技, analysis_type='profile', category='financial')
    # 同行业绩对比
    # 主要竞争对手：并非所有业务重叠
    peers=[ #定义主要竞争对手
           '002279.SZ',#久其软件
           '002368.SZ',#太极股份
           '600410.SS',#华胜天成
           '603927.SS',#中科软
           '002405.SZ',#四维图新
           ]
    players=[千方科技]+peers
    competitors = fs_analysis_china(players, fsdates='2023-12-31', analysis_type='summary')
    # 资产负债表分析
    fsdates=['2023-12-31','2022-12-31','2021-12-31','2020-12-31','2019-12-31']
    fs_analysis_china(千方科技,fsdates,analysis_type='balance sheet')
    # 利润表分析
    fs_analysis_china(千方科技,fsdates,analysis_type='income statement')
    # 现金流量表分析
    fs_analysis_china(千方科技,fsdates,analysis_type='cashflow statement')
    # 杜邦分析
    dd = fs_analysis_china(千方科技, fsdates='2023-12-31', analysis_type='dupont decompose')
    # 投资-风险性价比分析
    # 以一年期国债收益率作为无风险收益率
    RF=0.01657
    # 短期分析
    rar1=security_trend(players,indicator='sharpe',ret_type='Exp Ret%',start='MRM',RF=RF,loc1='lower left')
    rar2 = security_trend(players, indicator='alpha', ret_type='Exp Ret%', start='MRM', RF=RF, loc1='lower left')
    # 中长期分析
    rar3=security_trend(players,indicator='sharpe',ret_type='Exp Ret%',start='L3Y',RF=RF,loc1='lower left')
    
    备注：封装说明
    套壳函数1：tickers为股票列表，fsdates为财报日期，可为单个日期或日期列表
    asset_liab_china, income_cost_china, cash_flow_china
    
    套壳函数2：tickers为股票列表，fsdates为财报日期，可为单个日期或日期列表
    compare_fin_summary_china
    
    套壳函数3：tickers为股票代码或股票列表，fsdates为财报日期列表    
    compare_fin_indicator_china
    
    套壳函数4：tickers为股票代码，fsdates不需要，
    stock_profile_china
    
    套壳函数5/6：杜邦分析compare_dupont_china / 杜邦分解dupont_decompose
    """
        
    # 统一转小写，便于判断
    analysis_type1=analysis_type.lower()
    
    if ('balance' in analysis_type1) or ('sheet' in analysis_type1) \
       or ('asset' in analysis_type1) or ('liability' in analysis_type1):
        # 检查股票列表
        if not isinstance(tickers,list):
            tickers=[tickers]
        
        if not isinstance(fsdates,list):
            fsdates=gen_yoy_dates(fsdates,num=4)
        
        # 分析资产负债表       
        asset_liab_china(tickers,fsdates,facecolor=facecolor,font_size=font_size)
        return
    
    elif ('income' in analysis_type1) or ('cost' in analysis_type1) \
         or ('expense' in analysis_type1) or ('earning' in analysis_type1):
        # 检查股票列表        
        if not isinstance(tickers,list):
            tickers=[tickers]
        
        if not isinstance(fsdates,list):
            fsdates=gen_yoy_dates(fsdates,num=4)      
        
        # 分析利润表
        income_cost_china(tickers,fsdates,facecolor=facecolor,font_size=font_size)
        return
    
    elif ('cash' in analysis_type1) or ('flow' in analysis_type1):
        # 检查股票列表        
        if not isinstance(tickers,list):
            tickers=[tickers]
        
        if not isinstance(fsdates,list):
            fsdates=gen_yoy_dates(fsdates,num=4)      
        
        # 分析现金流量表
        cash_flow_china(tickers,fsdates,facecolor=facecolor,font_size=font_size)
        return
    
    elif ('summary' in analysis_type1):
        # 股票可为单只股票(单只股票深度分析)或股票列表(多只股票对比)   
        # 检查股票        
        if isinstance(tickers,str):
            if not isinstance(fsdates,list):
                fsdates=gen_yoy_dates(fsdates,num=4)
                """
                print("  #Warning(fs_analysis_china): must be date list for",fsdates)
                return
                """
                
        # 检查股票列表        
        if isinstance(tickers,list):
            if not isinstance(fsdates,str):
                fsdates=fsdates[0]
                """
                print("  #Warning(fs_analysis_china): must be a date for",fsdates)
                return
                """

        # 分析财报摘要 
        from siat.financials_china import compare_fin_summary_china          
        df_summary=compare_fin_summary_china(tickers,fsdates,facecolor=facecolor,font_size=font_size)
        return        
    
    elif ('indicator' in analysis_type1):
        # 股票可为单只股票(单只股票深度分析)或股票列表(多只股票对比)        
        # 检查股票        
        if isinstance(tickers,str):
            if not isinstance(fsdates,list):
                fsdates=gen_yoy_dates(fsdates,num=4)
                """
                print("  #Warning(fs_analysis_china): must be date list for",fsdates)
                return
                """
                
        # 检查股票列表        
        if isinstance(tickers,list):
            if not isinstance(fsdates,str):
                fsdates=fsdates[0]
                """
                print("  #Warning(fs_analysis_china): must be a date for",fsdates)
                return
                """

        # 分析主要财务指标和比率 
        from siat.financials_china import compare_fin_indicator_china           
        df_ind=compare_fin_indicator_china(tickers,fsdates,facecolor=facecolor,font_size=font_size)
        return        
    
    elif ('profile' in analysis_type1):
        # 股票需为单只股票        
        if not isinstance(tickers,str):
            print("  #Warning(fs_analysis_china): must be one ticker for",tickers)
            return        

        # 分析单只股票的全方位概况      
        stock_profile_china(tickers,category,business_period,loc1=loc1,loc2=loc2, \
                            facecolor=facecolor,font_size=font_size)
        return        
    
    elif ('dupont' in analysis_type1) and (('identity' in analysis_type1) or ('analysis' in analysis_type1)):
        # 股票需为股票列表        
        if not isinstance(tickers,list):
            print("  #Warning(fs_analysis_china): must be ticker list for",tickers)
            return        
        # 日期需为一个日期        
        if not isinstance(fsdates,str):
            fsdates=fsdates[0]
            """
            print("  #Warning(fs_analysis_china): must one date for",fsdates)
            return
            """        

        # 多只股票的杜邦分析对比      
        from siat.financials_china import compare_dupont_china           
        df_db=compare_dupont_china(tickers,fsdate=fsdates,sort=sort,printout=printout, \
                                   facecolor=facecolor,font_size=font_size,loc=loc1)
        return        
    
    elif ('dupont' in analysis_type1) and ('decompose' in analysis_type1):
        # 股票需为单只股票列表        
        if not isinstance(tickers,str):
            if isinstance(tickers,list):
                tickers=tickers[0]
            else:
                print("  #Warning(fs_analysis_china): must be one ticker for",tickers)
                return        
        # 日期需为一个日期        
        if not isinstance(fsdates,str):
            if isinstance(fsdates,list):
                fsdates=fsdates[0]
            else:
                print("  #Warning(fs_analysis_china): must one date for",fsdates)
                return        
            
        # 单只股票的多层杜邦分解      
        from siat.financials_china import dupont_decompose_china           
        df_dbd=dupont_decompose_china(ticker=tickers,fsdate=fsdates,gview=gview,facecolor=facecolor)
        return        
    
    else:
        print("  #Warning(fs_analysis_china): sorry, no idea on what to do for",analysis_type)
        
    return


#==============================================================================
#==============================================================================
#==============================================================================
