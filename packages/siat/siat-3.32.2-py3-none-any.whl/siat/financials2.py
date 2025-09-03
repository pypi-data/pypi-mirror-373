# -*- coding: utf-8 -*-
"""
本模块功能：计算财务报表比例，应用层
所属工具包：证券投资分析工具SIAT 
SIAT：Security Investment Analysis Tool
创建日期：2023年11月23日
最新修订日期：2023年11月23日
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
#本模块的公共引用
from siat.common import *
from siat.translate import *
from siat.financial_statements import *
from siat.financials import *
from siat.stock import *
from siat.grafix import *
#==============================================================================
import matplotlib.pyplot as plt

#plt.rcParams['figure.figsize']=(12.8,7.2)
plt.rcParams['figure.figsize']=(12.8,6.4)
plt.rcParams['figure.dpi']=300
plt.rcParams['font.size'] = 13
plt.rcParams['xtick.labelsize']=11 #横轴字体大小
plt.rcParams['ytick.labelsize']=11 #纵轴字体大小

title_txt_size=16
ylabel_txt_size=14
xlabel_txt_size=14
legend_txt_size=14

#设置绘图风格：网格虚线
plt.rcParams['axes.grid']=True
#plt.rcParams['grid.color']='steelblue'
#plt.rcParams['grid.linestyle']='dashed'
#plt.rcParams['grid.linewidth']=0.5
#plt.rcParams['axes.facecolor']='whitesmoke'

#处理绘图汉字乱码问题
import sys; czxt=sys.platform
if czxt in ['win32','win64']:
    plt.rcParams['font.sans-serif'] = ['SimHei']  # 设置默认字体
    mpfrc={'font.family': 'SimHei'}

if czxt in ['darwin']: #MacOSX
    plt.rcParams['font.family']= ['Heiti TC']
    mpfrc={'font.family': 'Heiti TC'}

if czxt in ['linux']: #website Jupyter
    plt.rcParams['font.family']= ['Heiti TC']
    mpfrc={'font.family':'Heiti TC'}

# 解决保存图像时'-'显示为方块的问题
plt.rcParams['axes.unicode_minus'] = False 
#==============================================================================
if __name__=='__main__':
    #测试1
    tickers="JD"
    analysis_type='Balance Sheet'
    fsdates='2023-12-31'
    
    font_size='16px'
    business_period='annual'
    
    
    tickers=["JD","00700.HK",'BABA','09999.HK']
    fsdates='2023-12-31'
    
    analysis_type='Balance Sheet'
    analysis_type='Income Statement'
    analysis_type='Cash Flow Statement'
    
    fs_analysis(tickers,fsdates,analysis_type='balance sheet')
    fs_analysis(tickers,fsdates,analysis_type='income statement')
    fs_analysis(tickers,fsdates,analysis_type='cash flow statement')

    tickers=["000002.SZ","600266.SS",'600383.SS','600048.SS']    
    fsdates=['2021-12-31','2020-12-31','2019-12-31','2018-12-31']
    fs_analysis(tickers,fsdates,analysis_type='fs summary')
    fs_analysis(tickers,fsdates,analysis_type='financial indicator')
    
    tickers='00700.HK'
    analysis_type='profile'
    category='profile'
    fs_analysis(tickers,fsdates,analysis_type='profile')
    fs_analysis(tickers,fsdates,analysis_type='profile',category='shareholder')
    fs_analysis(tickers,fsdates,analysis_type='profile',category='dividend')
    fs_analysis(tickers,fsdates,analysis_type='profile',category='business')
    fs_analysis(tickers,fsdates,analysis_type='profile',category='business',business_period='annual')
    fs_analysis(tickers,fsdates,analysis_type='profile',category='valuation')
    fs_analysis(tickers,fsdates,analysis_type='profile',category='financial')
    
    tickers='03333.HK'; analysis_type='financial indicator'

def fs_analysis(tickers,fsdates=[],analysis_type='balance sheet', \
                category='profile',business_period='annual', \
                    items_included='all', \
                scale1=10,scale2=10,dupont_sort='PM',
                printout=True, \
               #entry_sort=False, \
                facecolor='papayawhip',font_size='16px'
                ):
    """
    ===========================================================================
    功能：分析境外上市公司财报信息
    
    主要参数：
    tickers：股票列表，对比分析时需要多个股票，单列财报时仅取第一个股票
    fsdates：财报日期，可为单个日期或日期列表，注意境外上市公司财报日期与中国大陆的不同
    
    analysis_type：分析类型，可为企业概况('profile')、资产负债表简表('balance sheet')、
    利润表简表('income statement')、现金流量表简表('cash flow')、财报概况('financial summary')、
    财务比率('financial indicator')、杜邦分析('dupont identity')
    
    category：企业概况分类，，仅当analysis_type='profile'时有效，
    可为基本信息'profile'、高管概况('officers')、分红('dividend')、股票分拆('split')、市场表现('market')、
    财务状况('financial')、一般风险('risk')、ESG风险('esg')
    
    business_period：业务期间类型，可为季报'quarterly'，默认年报'annual'、最近的6次报告'recent', 所有'all' 
    items_included：默认输出所有报表项目，可以列表形式选择其中一部分。
    scale1：仅用于杜邦分析，放大倍数（以便缩小与EM之间的数量级差异），用于Profit Margin，默认10
    scale2：仅用于杜邦分析，放大倍数，用于Total Asset Turnover，默认10
    dupont_sort：仅用于杜邦分析，用于排序指标，默认净利润率'PM'，还可为总资产周转率'TAT'或权益乘数'EM'
    printout：是否显示数据表，默认是True
    facecolor：背景颜色，默认小麦黄'papayawhip'
    font_size：标题字体大小，默认'16px'
    
    示例：
    #指定上市公司的股票代码：苹果
    ticker='AAPL'
    #指定进行对比的上市公司股票代码：苹果，微软，英伟达，高通
    tickers=['AAPL','MSFT','NVDA','QCOM']
    # 公司基本信息
    profile=fs_analysis(ticker,analysis_type='profile')
    # 证券分红
    dividend=fs_analysis(ticker,analysis_type='profile',category='dividend')
    # 证券分拆
    split=fs_analysis(ticker,analysis_type='profile',category='split')
    # 基本市场指标
    frates=fs_analysis(ticker,analysis_type='profile',category='market')
    # 基本财务比率
    frates=fs_analysis(ticker,analysis_type='profile',category='financial')
    # 一般风险评估
    frates=fs_analysis(ticker,analysis_type='profile',category='risk')
    # ESG风险评估
    frates=fs_analysis(ticker,analysis_type='profile',category='esg')
    # Balance sheet
    bs=fs_analysis(ticker,
               analysis_type='balance sheet')
    # Income statement
    ist=fs_analysis(ticker,
               analysis_type='income statement')
    # Cash flow statement
    cfs=fs_analysis(ticker,
               analysis_type='cash flow statement')
    # Financial summary
    fs=fs_analysis(ticker,
               analysis_type='financial summary')
    # Financial ratios：单个企业
    fs=fs_analysis(ticker,
               analysis_type='financial indicator')
    # Financial ratios：同行对比。注意：美股上市公司年报日期不统一，可比性较差！
    fs=fs_analysis(tickers,
                   analysis_type='financial indicator')
    # Dupont identity：同行对比
    fs=fs_analysis(tickers,
               analysis_type='dupont identity')
    
    注意1：仅从雅虎财经获取数据
    注意2：不同经济体上市公司报表币种可能不同，金额项目仅进行同公司对比，不进行公司间对比
    注意3：公司间仅对比财务比率和杜邦分析
    注意4：不同经济体上市公司年报季报日期不同，需要列示报表日期和类型(年报或季报)
       
    """
    DEBUG=False
    
    import numpy as np
    import pandas as pd

    #屏蔽函数内print信息输出的类
    import os, sys
    class HiddenPrints:
        def __enter__(self):
            self._original_stdout = sys.stdout
            sys.stdout = open(os.devnull, 'w')

        def __exit__(self, exc_type, exc_val, exc_tb):
            sys.stdout.close()
            sys.stdout = self._original_stdout
        
    # 统一转小写，便于判断
    analysis_type1=analysis_type.lower()
    
    # 今日
    import datetime as dt
    todaydt=dt.date.today().strftime('%Y-%m-%d')
    
    # 定义数量级
    million=1000000
    billion=million * 1000
    
    #确定表格字体大小
    titile_font_size=font_size
    heading_font_size=data_font_size=str(int(font_size.replace('px',''))-3)+'px'
    
    # 基于analysis_type1的类型分别处理
    #if ('profile' in analysis_type1):
    if contains_any(analysis_type1,['profile']):
        # 股票需为单只股票，若为列表则仅取第一个        
        if not isinstance(tickers,str):
            if isinstance(tickers,list): tickers=tickers[0]
            else:
                print("  #Warning(fs_analysis_china): {} must be one ticker or ticker list".format(tickers))
                return  None      

        # 检查category
        #category_list=['profile','officers','market_rates','dividend','split','fin_rates','risk_general','risk_esg']
        category_list=['profile','officers','market rates','dividend','split','financial rates','general risk','esg']
        
        #if category == 'profile':
        if contains_any(category,['profile']):
            info=get_stock_profile(tickers)
        #elif category == 'dividend':
        elif contains_any(category,['dividend']):
            #info=stock_dividend(tickers,start='1990-1-1',end=todaydt)
            info=stock_dividend(tickers)
        #elif category == 'stock_split':    
        elif contains_any(category,['split']):
            #info=stock_split(tickers,start='1990-1-1',end=todaydt)
            info=stock_split(tickers)
        elif contains_any(category,['market']):
            category='market_rates'
            info=get_stock_profile(tickers,info_type=category)
        elif contains_any(category,['financial']):
            category='fin_rates'
            info=get_stock_profile(tickers,info_type=category)
            
        elif contains_any(category,['risk']):
            #这里的是风险指标，数值越大风险越高，数值越小越好
            category='risk_general'
            info=get_stock_profile(tickers,info_type=category)
        elif contains_any(category,['esg']):
            #这里的ESG为风险指标，数值越大风险越高，数值越小越好
            category='risk_esg'
            info=get_stock_profile(tickers,info_type=category)
        else:
            print("  Unsupported category {}, supported categories:".format(category))
            print_list(category_list,leading_blanks=2)
            
        return info
    #elif ('balance' in analysis_type1) or ('sheet' in analysis_type1) or ('asset' in analysis_type1) or ('liability' in analysis_type1):
    #elif contains_any(analysis_type1,['balance','sheet','asset','liability']):
    elif contains_any(analysis_type1,['balance','sheet','asset','liability']):
        # 股票需为单只股票，若为列表则仅取第一个        
        if not isinstance(tickers,str):
            if isinstance(tickers,list): tickers=tickers[0]
            else:
                print("  #Warning(fs_analysis_china): must be one ticker or first ticker in a list for",tickers)
                return None
        
        # 分析资产负债表       
        fsdf=get_balance_sheet(symbol=tickers)
        if fsdf is None:
            print(f"  #Warning(fs_analysis): failed to access financial info for {tickers}")
            if test_yahoo_access():
                print(f"  Solution: if {tickers} are correct, then try again later")
            else:
                print("  Problem: no internet connection to Yahoo for retrieveing data")
            return None
        
        fsdf['reportDate']=fsdf['asOfDate'].apply(lambda x: x.strftime('%y-%m-%d'))
        fsdf.set_index('reportDate',inplace=True)
        fsdf.fillna(0,inplace=True)     
        
        fsdf2=fsdf.copy()
        collist=list(fsdf2)
        for c in collist:
            try:
                fsdf2[c]=round(fsdf2[c] / billion,2)
            except:
                continue
        
        # 变换年报/季报
        fsdf2['periodType']=fsdf2['periodType'].apply(lambda x: 'Annual' if x=='12M' else 'Quarterly')
        
        # 删除不用的列
        currency=fsdf2['currencyCode'].values[0]
        #droplist=['currencyCode','TA-TL-TE','asOfDate']
        droplist=['currencyCode','asOfDate']
        fsdf2.drop(droplist,axis=1,inplace=True)

        # 打印前处理
        if printout:        
            # 降序排列
            fsdf3=fsdf2.sort_index(ascending=False)
            
            business_period=business_period.lower()
            if business_period == 'recent':
                fsdf4=fsdf3.head(6)
            elif business_period == 'quarterly':
                fsdf4=fsdf3[fsdf3['periodType']=='Quarterly']
            elif business_period == 'annual':
                fsdf4=fsdf3[fsdf3['periodType']=='Annual']   
            else: #'all'
                #fsdf4=fsdf3[fsdf3['periodType'].isin(['Annual','Quarterly'])]     
                fsdf4=fsdf3
                
            # 转置
            fsdf4=fsdf4.T
            
            fsdf4.replace(0,'---',inplace=True)
            
            #titletxt="\n***** "+ticker_name(tickers)+": BALANCE SHEET"+' *****\n'
            titletxt=ticker_name(tickers,'stock')+text_lang("：资产负债简表",": BALANCE SHEET")
            #print(titletxt)
            """
            tablefmt_list=["plain","simple","github","grid","simple_grid","rounded_grid", \
                           "heavy_grid","mixed_grid","double_grid","fancy_grid","outline", \
                           "simple_outline","rounded_outline","heavy_outline", \
                           "mixed_outline","double_outline","fancy_outline","pipe", \
                           "orgtbl","asciidoc","jira","presto","pretty","psql", \
                           "rst","mediawiki","moinmoin","youtrack","html","unsafehtml", \
                           "latex","latex_raw","latex_booktabs","latex_longtable", \
                           "textile","tsv"]
            for t in tablefmt_list:
                print("\n\n  ========== tablefmt: "+t+" ============\n")
                alignlist=['left']+['right']*(len(list(fsdf3))-1)
                print(fsdf3.to_markdown(tablefmt=t,index=True,colalign=alignlist))
            """
            #print(fsdf3)
            """
            collist=list(fsdf3)
            fsdf3['Item']=fsdf3.index
            fsdf4=fsdf3[['Item']+collist]
            pandas2prettytable(fsdf4,titletxt,firstColSpecial=False,leftColAlign='l',otherColAlign='r')
            """
            collist=list(fsdf4)
            fsdf4['Item']=fsdf4.index
            fsdf5=fsdf4[['Item']+collist]   
            fsdf6=df_filter_row(fsdf5,exclude_collist=['Item'],symbol='---')
            
            fsdf6=df_sort_priority_list(fsdf6,sort_column='Item',priorityList=['periodType'],ascending=True)
            """
            alignlist=['left']+['right']*(len(list(fsdf5))-1)
            print(fsdf6.to_markdown(tablefmt='plain',index=False,colalign=alignlist))                
            """
            
            footnote1="Amount unit: "+currency+" billion, exchange's local accounting standards"
            footnote2="Data source: Yahoo Finance, "+str(todaydt)
            footnote='Note:\n'+footnote1+'\n'+footnote2
            #print('\n',footnote1,'\n',footnote2)  
            
            # 将Item科目名称拆分加空格和转大写
            fsdf6['Item']=fsdf6['Item'].apply(lambda x: text_separate(x))
            
            # 判断是否仅输出部分科目
            if 'all' in items_included:
                fsdf7=fsdf6
            else:
                mask=fsdf6['Item'].isin(items_included)
                fsdf7=fsdf6[mask]
                # 将Item列转为分类类型，指定顺序
                fsdf7['Item'] = pd.Categorical(fsdf7['Item'], categories=items_included, ordered=True)    
                # 按分类顺序排序
                fsdf7=fsdf7.sort_values(by='Item')
            
            df_display_CSS(fsdf7,titletxt=titletxt,footnote=footnote,facecolor=facecolor, \
                           titile_font_size=titile_font_size,heading_font_size=heading_font_size, \
                               data_font_size=data_font_size)
            
            return fsdf6
        
        else:
            return fsdf2
    #elif ('income' in analysis_type1) or ('cost' in analysis_type1) or ('expense' in analysis_type1) or ('earnings' in analysis_type1):
    elif contains_any(analysis_type1,['income','revenue','cost','expense','earnings']):
        # 股票需为单只股票，若为列表则仅取第一个        
        if not isinstance(tickers,str):
            if isinstance(tickers,list): tickers=tickers[0]
            else:
                print("  #Warning(fs_analysis_china): must be one ticker or first ticker in a list for",tickers)
                return   None 
        
        # 分析利润表
        fsdf=get_income_statements(symbol=tickers)
        if fsdf is None:
            print("  #Warning(fs_analysis): financial info unaccessible for",tickers)
            if test_yahoo_access():
                print(f"  Solution: if {tickers} are correct, then try again later")
            else:
                print("  Problem: no internet connection to Yahoo for retrieveing data")

            return None
        
        fsdf['reportDate']=fsdf['asOfDate'].apply(lambda x: x.strftime('%y-%m-%d'))
        fsdf.set_index('reportDate',inplace=True)
        fsdf.fillna(0,inplace=True)     
        
        fsdf2=fsdf.copy()
        collist=list(fsdf2)
        for c in collist:
            try:
                fsdf2[c]=round(fsdf2[c] / billion,2)
            except:
                continue
        
        # 变换年报/季报
        fsdf2['periodType']=fsdf2['periodType'].apply(lambda x: 'Annual' if x=='12M' else 'Quarterly')
        
        # 删除不用的列
        currency=fsdf2['currencyCode'].values[0]
        droplist=['currencyCode','asOfDate']
        fsdf2.drop(droplist,axis=1,inplace=True)

        # 打印前处理
        if printout:        
            # 降序排列
            fsdf3=fsdf2.sort_index(ascending=False)
            
            business_period=business_period.lower()
            if business_period == 'recent':
                fsdf4=fsdf3.head(6)
            elif business_period == 'quarterly':
                fsdf4=fsdf3[fsdf3['periodType']=='Quarterly']
            elif business_period == 'annual':
                fsdf4=fsdf3[fsdf3['periodType']=='Annual']  
            else:
                fsdf4=fsdf3[fsdf3['periodType']=='Annual']                
                
            # 转置
            fsdf4=fsdf4.T
            
            fsdf4.replace(0,'---',inplace=True)
            
            #titletxt="\n***** "+ticker_name(tickers)+": INCOME STATEMENTS"+' *****\n'
            titletxt=ticker_name(tickers,'stock')+text_lang("：利润简表",": INCOME STATEMENTS")
            #print(titletxt)
            
            collist=list(fsdf4)
            fsdf4['Item']=fsdf4.index
            fsdf5=fsdf4[['Item']+collist]  
            fsdf6=df_filter_row(fsdf5,exclude_collist=['Item'],symbol='---')
            
            fsdf6=df_sort_priority_list(fsdf6,sort_column='Item',priorityList=['periodType'],ascending=True)
            """
            alignlist=['left']+['right']*(len(list(fsdf5))-1)
            print(fsdf6.to_markdown(tablefmt='plain',index=False,colalign=alignlist))                
            """    
            footnote1="Amount unit: "+currency+" billion, exchange's local accounting standards"
            footnote2="Data source: Yahoo Finance, "+str(todaydt)
            footnote='Note:\n'+footnote1+'\n'+footnote2
            #print('\n',footnote1,'\n',footnote2)    
            
            # 将Item科目名称拆分加空格和转大写
            fsdf6['Item']=fsdf6['Item'].apply(lambda x: text_separate(x))
            
            # 判断是否仅输出部分科目
            if 'all' in items_included:
                fsdf7=fsdf6
            else:
                mask=fsdf6['Item'].isin(items_included)
                fsdf7=fsdf6[mask]
                # 将Item列转为分类类型，指定顺序
                fsdf7['Item'] = pd.Categorical(fsdf7['Item'], categories=items_included, ordered=True)    
                # 按分类顺序排序
                fsdf7=fsdf7.sort_values(by='Item')
            
            df_display_CSS(fsdf7,titletxt=titletxt,footnote=footnote,facecolor=facecolor, \
                           titile_font_size=titile_font_size,heading_font_size=heading_font_size, \
                               data_font_size=data_font_size)
            
            return fsdf6
        
        return fsdf2
    #elif ('cash' in analysis_type1) or ('flow' in analysis_type1):
    elif contains_any(analysis_type1,['cash','flow']):
        # 股票需为单只股票，若为列表则仅取第一个        
        if not isinstance(tickers,str):
            if isinstance(tickers,list): tickers=tickers[0]
            else:
                print("  #Warning(fs_analysis_china): must be one ticker or first ticker in a list for",tickers)
                return None     
        
        # 分析现金流量表
        fsdf=get_cashflow_statements(symbol=tickers)
        if fsdf is None:
            print("  #Warning(fs_analysis): financial info unaccessible for",tickers)
            if test_yahoo_access():
                print(f"  Solution: if {tickers} are correct, then try again later")
            else:
                print("  Problem: no internet connection to Yahoo for retrieveing data")

            return None
        
        fsdf['reportDate']=fsdf['asOfDate'].apply(lambda x: x.strftime('%y-%m-%d'))
        fsdf.set_index('reportDate',inplace=True)
        fsdf.fillna(0,inplace=True)     
        
        fsdf2=fsdf.copy()
        collist=list(fsdf2)
        for c in collist:
            try:
                fsdf2[c]=round(fsdf2[c] / billion,2)
            except:
                continue
        
        # 变换年报/季报
        fsdf2['periodType']=fsdf2['periodType'].apply(lambda x: 'Annual' if x=='12M' else 'Quarterly')
        
        # 删除不用的列
        currency=fsdf2['currencyCode'].values[0]
        droplist=['currencyCode','asOfDate']
        fsdf2.drop(droplist,axis=1,inplace=True)

        # 打印前处理
        if printout:        
            # 降序排列
            fsdf3=fsdf2.sort_index(ascending=False)
            
            business_period=business_period.lower()
            if business_period == 'recent':
                fsdf4=fsdf3.head(6)
            elif business_period == 'quarterly':
                fsdf4=fsdf3[fsdf3['periodType']=='Quarterly']
            elif business_period == 'annual':
                fsdf4=fsdf3[fsdf3['periodType']=='Annual'] 
            else:
                fsdf4=fsdf3[fsdf3['periodType']=='Annual']
                    
            # 转置
            fsdf4=fsdf4.T
            
            fsdf4.replace(0,'---',inplace=True)
            
            #titletxt="\n***** "+ticker_name(tickers)+": CASHFLOW STATEMENTS"+' *****\n'
            titletxt=ticker_name(tickers,'stock')+text_lang("：现金流量简表",": CASHFLOW STATEMENTS")
            #print(titletxt)
            
            collist=list(fsdf4)
            fsdf4['Item']=fsdf4.index
            fsdf5=fsdf4[['Item']+collist] 
            fsdf6=df_filter_row(fsdf5,exclude_collist=['Item'],symbol='---')
            
            fsdf6=df_sort_priority_list(fsdf6,sort_column='Item',priorityList=['periodType'],ascending=True)
            """
            alignlist=['left']+['right']*(len(list(fsdf5))-1)
            print(fsdf6.to_markdown(tablefmt='plain',index=False,colalign=alignlist))                
            """  
            footnote1="Amount unit: "+currency+" billion, exchange's local accounting standards"
            footnote2="Data source: Yahoo Finance, "+str(todaydt)
            footnote='Note:\n'+footnote1+'\n'+footnote2
            #print('\n',footnote1,'\n',footnote2)     
            
            # 将Item科目名称拆分加空格和转大写
            fsdf6['Item']=fsdf6['Item'].apply(lambda x: text_separate(x))
            
            # 判断是否仅输出部分科目
            if 'all' in items_included:
                fsdf7=fsdf6
            else:
                mask=fsdf6['Item'].isin(items_included)
                fsdf7=fsdf6[mask]
                # 将Item列转为分类类型，指定顺序
                fsdf7['Item'] = pd.Categorical(fsdf7['Item'], categories=items_included, ordered=True)    
                # 按分类顺序排序
                fsdf7=fsdf7.sort_values(by='Item')
            
            df_display_CSS(fsdf7,titletxt=titletxt,footnote=footnote,facecolor=facecolor, \
                           titile_font_size=titile_font_size,heading_font_size=heading_font_size, \
                               data_font_size=data_font_size)
            return fsdf6
            
        return fsdf2
    #elif ('summary' in analysis_type1):
    elif contains_any(analysis_type1,['summary']):
        itemlist1=[
            #资产负债表
            'CashAndCashEquivalents','AccountsReceivable','Inventory', \
            'CurrentAssets','NetPPE','Goodwill','TotalAssets', \
            'CurrentLiabilities','LongTermDebt','TotalLiabilities','TotalEquities', \
            #利润表
            'TotalRevenue','GrossProfit','OperatingRevenue','OperatingIncome', \
            'GeneralAndAdministrativeExpense','EBITDA','PretaxIncome', \
            'NetIncome', \
            'NetIncomeCommonStockholders','NetIncomeContinuousOperations', \
            #现金表
            'OperatingCashFlow', \
            'FreeCashFlow', \
            ]
            
        itemlist2=[            
            #财务指标
            'BasicEPS','DilutedEPS', \
            'Gross Margin','Operating Margin','Profit Margin', \
            'Return on Equity','Return on Asset','Debt to Asset', \
            ]  
        itemlist=itemlist1+itemlist2
        
        # 股票可为单只股票(单只股票深度分析)       
        if isinstance(tickers,str):
            print("  Getting financial rates for financial summary of",tickers,"...")
            with HiddenPrints():
                fsdf=get_financial_rates(tickers)
            if fsdf is None:
                print("  #Warning(fs_analysis): financial info unaccessible for",tickers)
            if test_yahoo_access():
                print(f"  Solution: if {tickers} are correct, then try again later")
            else:
                print("  Problem: no internet connection to Yahoo for retrieveing data")

                return None
        
            fsdf['reportDate']=fsdf['asOfDate'].apply(lambda x: x.strftime('%y-%m-%d'))
            fsdf.set_index('reportDate',inplace=True)
            
            fsdf.replace([np.inf, -np.inf], np.nan, inplace=True)
            fsdf.fillna(0,inplace=True) 
            
            currency=fsdf['currencyCode'].values[0]
            
            # 变换年报/季报
            fsdf['periodType']=fsdf['periodType'].apply(lambda x: 'Annual' if x=='12M' else 'Quarterly')

            # 删除不用的列
            fsdf2=fsdf.copy()
            collist=list(fsdf2)
            keeplist=[]
            for c in itemlist:
                if c in collist:
                    keeplist=keeplist+[c]
                    if c in itemlist1:
                        try:
                            fsdf2[c]=fsdf2[c].apply(lambda x: round(x / billion,2))
                        except: pass
                    else:
                        fsdf2[c]=fsdf2[c].apply(lambda x: round(x,4))
                else: pass
                    
            keeplist=['periodType']+keeplist       
            fsdf2=fsdf2[keeplist]
    
            # 打印处理
            if printout:        
                # 降序排列
                fsdf3=fsdf2.sort_index(ascending=False)
                
                business_period=business_period.lower()
                if business_period == 'recent':
                    fsdf4=fsdf3.head(6)
                elif business_period == 'quarterly':
                    fsdf4=fsdf3[fsdf3['periodType']=='Quarterly']
                elif business_period == 'annual':
                    fsdf4=fsdf3[fsdf3['periodType']=='Annual']
                elif business_period == 'all':
                    fsdf4=fsdf3                    
                    #fsdf4=fsdf3[fsdf3['periodType'].isin(['Annual','Quarterly'])]
                else:
                    #fsdf4=fsdf3[fsdf3['periodType']=='Annual']
                    fsdf4=fsdf3
                    
                # 转置
                fsdf4=fsdf4.T
                
                fsdf4.replace(0,'---',inplace=True)
                
                #titletxt="\n***** "+ticker_name(tickers)+": FINANCIAL STATEMENT SUMMARY"+' *****\n'
                titletxt=ticker_name(tickers,'stock')+text_lang("：财报摘要",": FINANCIAL STATEMENT SUMMARY")
                #print(titletxt)
                
                collist=list(fsdf4)
                fsdf4['Item']=fsdf4.index
                fsdf5=fsdf4[['Item']+collist]   
                fsdf6=df_filter_row(fsdf5,exclude_collist=['Item'],symbol='---')
                
                fsdf6=df_sort_priority_list(fsdf6,sort_column='Item',priorityList=['periodType'],ascending=True)
                """
                alignlist=['left']+['right']*(len(list(fsdf5))-1)
                print(fsdf6.to_markdown(tablefmt='plain',index=False,colalign=alignlist))                
                """
                footnote1="Amount unit: "+currency+" billion, exchange's local accounting standards"
                footnote2="ROx/EM/turnover rates are based on periodic mean, others on end-term"
                footnote3="Data source: Yahoo Finance, "+todaydt
                footnote='Note:\n'+footnote1+'\n'+footnote2+'\n'+footnote3
                #print('\n',footnote1,'\n',footnote2,'\n',footnote3)     
            
                # 将Item科目名称拆分加空格和转大写
                fsdf6['Item']=fsdf6['Item'].apply(lambda x: text_separate(x))
                
                # 判断是否仅输出部分科目
                if 'all' in items_included:
                    fsdf7=fsdf6
                else:
                    mask=fsdf6['Item'].isin(items_included)
                    fsdf7=fsdf6[mask]
                    # 将Item列转为分类类型，指定顺序
                    fsdf7['Item'] = pd.Categorical(fsdf7['Item'], categories=items_included, ordered=True)    
                    # 按分类顺序排序
                    fsdf7=fsdf7.sort_values(by='Item')
                
                df_display_CSS(fsdf7,titletxt=titletxt,footnote=footnote,facecolor=facecolor, \
                               titile_font_size=titile_font_size,heading_font_size=heading_font_size, \
                                   data_font_size=data_font_size)                
                return fsdf6

            return fsdf2
                
        # 股票可为股票列表(多只股票对比)        
        if isinstance(tickers,list):
            
            business_period=business_period.lower()
            fsdf=pd.DataFrame()
            for t in tickers:
                print("  Getting financial rates for financial summary of",t,"...")
                with HiddenPrints():
                    dftmp=get_financial_rates(t)
                if dftmp is None:
                    print("  #Warning(fs_analysis): financial info unaccessible for",t)
                    if test_yahoo_access():
                        print(f"  Solution: if {t} are correct, then try again later")
                    else:
                        print("  Problem: no internet connection to Yahoo for retrieveing data")
                    return None
                
                if not last_in_list(t,tickers):
                    sleep_random(max_sleep=60)

                if business_period=='recent':
                    dftmp2=dftmp.tail(1)
                elif business_period=='annual':
                    dftmp2=dftmp[dftmp['periodType']=='12M'].tail(1)
                elif business_period=='quarterly':
                    dftmp2=dftmp[dftmp['periodType']=='3M'].tail(1)
                else:
                    dftmp2=dftmp.tail(1)
                    
                """
                dftmp2=pd.DataFrame(dftmp2)
                fsdf=pd.concat([fsdf,dftmp2])
                """
                #删除重复的列名，若存在重复列会出现错误InvalidIndexError: Reindexing
                dftmp2t=dftmp2.T
                dftmp2t['item']=dftmp2t.index
                dftmp2t.drop_duplicates(keep='first',inplace=True)
                dftmp2t.drop(columns=['item'],inplace=True)
                dftmp3=dftmp2t.T
                
                if fsdf is None:
                    fsdf=dftmp3
                else:
                    fsdf=pd.concat([fsdf,dftmp3],ignore_index=True)                
                
            # 变换年报/季报
            fsdf['periodType']=fsdf['periodType'].apply(lambda x: 'Annual' if x=='12M' else 'Quarterly')
            fsdf['reportDate']=fsdf['asOfDate'].apply(lambda x: x.strftime('%y-%m-%d'))
            fsdf['Name']=fsdf['ticker'].apply(lambda x: ticker_name(x))
            fsdf.set_index('Name',inplace=True)
            
            fsdf.replace([np.inf, -np.inf], np.nan, inplace=True)
            fsdf.fillna(0,inplace=True) 
            currency=fsdf['currencyCode'].values[0]

            # 删除不用的列
            fsdf2=fsdf.copy()
            collist=list(fsdf2)
            keeplist=[]
            for c in itemlist:
                if c in collist:
                    keeplist=keeplist+[c]
                    if c in itemlist1:
                        try:
                            fsdf2[c]=fsdf2[c].apply(lambda x: round(x / billion,2))
                        except: pass
                    else:
                        fsdf2[c]=fsdf2[c].apply(lambda x: round(x,4))
                else: pass
                    
            keeplist=['periodType','reportDate','currencyCode']+keeplist       
            fsdf2=fsdf2[keeplist]            
    
            # 打印处理
            if printout:        
                # 降序排列
                #fsdf3=fsdf2.sort_index(ascending=False)
                fsdf4=fsdf2    
                # 转置
                fsdf4=fsdf4.T
                
                fsdf4.replace(0,'---',inplace=True)
                
                #titletxt="\n***** PEER COMPARISON OF FINANCIAL STATEMENT SUMMARY *****\n"
                titletxt=text_lang("财报摘要对比","FINANCIAL STATEMENT SUMMARY: COMPARISON")
                #print(titletxt)
                
                collist=list(fsdf4)
                fsdf4['Item']=fsdf4.index
                fsdf5=fsdf4[['Item']+collist]   
                fsdf6=df_filter_row(fsdf5,exclude_collist=['Item'],symbol='---')
                
                fsdf6=df_sort_priority_list(fsdf6,sort_column='Item',priorityList=['periodType','reportDate','currencyCode'],ascending=True)
                """
                alignlist=['left']+['right']*(len(list(fsdf5))-1)
                print(fsdf6.to_markdown(tablefmt='plain',index=False,colalign=alignlist))                
                """  
                footnote1="Amount unit: billion, based on exchange's local accounting standards"
                footnote2="ROx/EM/turnover rates are based on periodic mean, others on end-term"
                footnote3="Data source: Yahoo Finance, "+str(todaydt)
                footnote='Note:\n'+footnote1+'\n'+footnote2+'\n'+footnote3
                #print('\n',footnote1,'\n',footnote2,'\n',footnote3)    
            
                # 将Item科目名称拆分加空格和转大写
                fsdf6['Item']=fsdf6['Item'].apply(lambda x: text_separate(x))
                
                # 判断是否仅输出部分科目
                if 'all' in items_included:
                    fsdf7=fsdf6
                else:
                    mask=fsdf6['Item'].isin(items_included)
                    fsdf7=fsdf6[mask]
                    # 将Item列转为分类类型，指定顺序
                    fsdf7['Item'] = pd.Categorical(fsdf7['Item'], categories=items_included, ordered=True)    
                    # 按分类顺序排序
                    fsdf7=fsdf7.sort_values(by='Item')
                    
                df_display_CSS(fsdf7,titletxt=titletxt,footnote=footnote,facecolor=facecolor, \
                               titile_font_size=titile_font_size,heading_font_size=heading_font_size, \
                                   data_font_size=data_font_size)                
                return fsdf6

        return fsdf2     
    #elif ('indicator' in analysis_type1):
    elif contains_any(analysis_type1,['indicator']):
        itemlist=[
            #短期偿债能力
            'Current Ratio','Quick Ratio','Cash Ratio','Cash Flow Ratio', \
            'Times Interest Earned', \
            #长期偿债能力
            'Debt to Asset','Equity to Asset','Equity Multiplier','Debt to Equity', \
            'Debt Service Coverage', \
            #营运能力
            'Inventory Turnover','Receivable Turnover','Current Asset Turnover', \
            'Fixed Asset Turnover','Total Asset Turnover', \
            #盈利能力
            'Gross Margin','Operating Margin','Profit Margin', \
            'Net Profit on Costs','ROA','ROE','ROIC', \
            #股东持股
            #'Payout Ratio', \
            'Cashflow per Share', \
            #'Dividend per Share', \
            'Net Asset per Share','BasicEPS','DilutedEPS', \
            #发展潜力
            #'Revenue Growth', \
            #'Capital Accumulation', \
            #'Total Asset Growth' \
            ]        
        
        # 股票可为单只股票(单只股票深度分析)       
        if isinstance(tickers,str):
            print("  Getting financial rates for financial indicators of",tickers,"...")
            with HiddenPrints():
                fsdf=get_financial_rates(tickers)
            if fsdf is None:
                print("  #Warning(fs_analysis): financial info unaccessible for",tickers)
                if test_yahoo_access():
                    print(f"  Solution: if {tickers} are correct, then try again later")
                else:
                    print("  Problem: no internet connection to Yahoo for retrieveing data")

                return None
        
            fsdf['reportDate']=fsdf['asOfDate'].apply(lambda x: x.strftime('%y-%m-%d'))
            fsdf.set_index('reportDate',inplace=True)
            
            fsdf.replace([np.inf, -np.inf], np.nan, inplace=True)
            fsdf.fillna(0,inplace=True) 
            
            currency=fsdf['currencyCode'].values[0]
            
            # 变换年报/季报
            fsdf['periodType']=fsdf['periodType'].apply(lambda x: 'Annual' if x=='12M' else 'Quarterly')

            # 删除不用的列
            fsdf2=fsdf.copy()
            collist=list(fsdf2)
            keeplist=[]
            for c in itemlist:
                if c in collist:
                    keeplist=keeplist+[c]
                    try:
                        fsdf2[c]=fsdf2[c].apply(lambda x: round(x,4))
                    except: pass
                else: pass
                    
            keeplist=['periodType']+keeplist       
            fsdf2=fsdf2[keeplist]
    
            # 打印处理
            if printout:        
                # 降序排列
                fsdf3=fsdf2.sort_index(ascending=False)
                
                business_period=business_period.lower()
                if business_period == 'recent':
                    fsdf4=fsdf3.head(6)
                elif business_period == 'quarterly':
                    fsdf4=fsdf3[fsdf3['periodType']=='Quarterly']
                elif business_period == 'annual':
                    fsdf4=fsdf3[fsdf3['periodType']=='Annual']
                elif business_period == 'all':
                    fsdf4=fsdf3                    
                    #fsdf4=fsdf3[fsdf3['periodType'].isin(['Annual','Quarterly'])]
                else:
                    #fsdf4=fsdf3[fsdf3['periodType']=='Annual']
                    fsdf4=fsdf3
                    
                # 转置
                fsdf4=fsdf4.T
                
                fsdf4.replace(0,'---',inplace=True)
                
                #titletxt="\n***** "+ticker_name(tickers)+": FINANCIAL INDICATORS"+' *****\n'
                titletxt=ticker_name(tickers,'stock')+text_lang("：财务比率",": FINANCIAL INDICATORS")
                #print(titletxt)
                
                collist=list(fsdf4)
                fsdf4['Item']=fsdf4.index
                fsdf5=fsdf4[['Item']+collist]   
                fsdf6=df_filter_row(fsdf5,exclude_collist=['Item'],symbol='---')
                
                fsdf6=df_sort_priority_list(fsdf6,sort_column='Item',priorityList=['periodType'],ascending=True)
                """
                alignlist=['left']+['right']*(len(list(fsdf5))-1)
                print(fsdf6.to_markdown(tablefmt='plain',index=False,colalign=alignlist))                
                """  
                footnote1="Amount unit: "+currency+" billion, exchange's local accounting standards"
                footnote2="ROx/EM/turnover rates are based on periodic mean, others on end-term"
                footnote3="Data source: Yahoo Finance, "+str(todaydt)
                footnote='Note:\n'+footnote1+'\n'+footnote2+'\n'+footnote3
                #print('\n',footnote1,'\n',footnote2,'\n',footnote3)   
            
                # 将Item科目名称拆分加空格和转大写
                fsdf6['Item']=fsdf6['Item'].apply(lambda x: text_separate(x))
                
                # 判断是否仅输出部分科目
                if 'all' in items_included:
                    fsdf7=fsdf6
                else:
                    mask=fsdf6['Item'].isin(items_included)
                    fsdf7=fsdf6[mask]
                    # 将Item列转为分类类型，指定顺序
                    fsdf7['Item'] = pd.Categorical(fsdf7['Item'], categories=items_included, ordered=True)    
                    # 按分类顺序排序
                    fsdf7=fsdf7.sort_values(by='Item')
                    
                df_display_CSS(fsdf7,titletxt=titletxt,footnote=footnote,facecolor=facecolor, \
                               titile_font_size=titile_font_size,heading_font_size=heading_font_size, \
                                   data_font_size=data_font_size)                
                return fsdf6

            return fsdf2
                
        # 股票可为股票列表(多只股票对比)        
        if isinstance(tickers,list):
            
            business_period=business_period.lower()
            fsdf=pd.DataFrame()
            print("  Working on financial rates, it may take long time ...")

            for t in tickers:
                print("  Getting financial rates for financial indicators of",t,"...")
                with HiddenPrints():
                    dftmp=get_financial_rates(t)
                if dftmp is None:
                    print("  #Warning(fs_analysis): financial info unaccessible for",t)
                    if test_yahoo_access():
                        print(f"  Solution: if {t} are correct, then try again later")
                    else:
                        print("  Problem: no internet connection to Yahoo for retrieveing data")

                    return None
                
                if len(dftmp) == 0:
                    print("  #Warning(fs_analysis): zero financial indicators found for stock",t)
                    continue
                
                if not last_in_list(t,tickers):
                    sleep_random(max_sleep=60)
                
                if business_period=='recent':
                    dftmp2=dftmp.tail(1)
                elif business_period=='annual':
                    dftmp2=dftmp[dftmp['periodType']=='12M'].tail(1)
                elif business_period=='quarterly':
                    dftmp2=dftmp[dftmp['periodType']=='3M'].tail(1)
                else:
                    dftmp2=dftmp.tail(1)
                
                #dftmp2=pd.DataFrame(dftmp2)
                #dftmp2['ticker1']=dftmp2['ticker']
                #dftmp2.set_index('ticker1',inplace=True)
                
                #删除重复的列名，若存在重复列会出现错误InvalidIndexError: Reindexing only valid with uniquely valued Index objects
                dftmp2t=dftmp2.T
                dftmp2t['item']=dftmp2t.index
                dftmp2t.drop_duplicates(keep='first',inplace=True)
                dftmp2t.drop(columns=['item'],inplace=True)
                dftmp3=dftmp2t.T
                
                if fsdf is None:
                    fsdf=dftmp3
                else:
                    fsdf=pd.concat([fsdf,dftmp3],ignore_index=True)
            
            # 变换年报/季报
            fsdf['periodType']=fsdf['periodType'].apply(lambda x: 'Annual' if x=='12M' else 'Quarterly')
            fsdf['reportDate']=fsdf['asOfDate'].apply(lambda x: x.strftime('%y-%m-%d'))
            fsdf['Name']=fsdf['ticker'].apply(lambda x: ticker_name(x))
            fsdf.set_index('Name',inplace=True)
            
            fsdf.replace([np.inf, -np.inf], np.nan, inplace=True)
            fsdf.fillna(0,inplace=True) 
            currency=fsdf['currencyCode'].values[0]

            # 删除不用的列
            fsdf2=fsdf.copy()
            collist=list(fsdf2)
            keeplist=[]
            for c in itemlist:
                if c in collist:
                    keeplist=keeplist+[c]
                    try:
                        fsdf2[c]=fsdf2[c].apply(lambda x: round(x,4))
                    except: pass
                else: pass
                    
            keeplist=['periodType','reportDate','currencyCode']+keeplist       
            fsdf2=fsdf2[keeplist]            
    
            # 打印处理
            if printout:        
                # 降序排列
                #fsdf3=fsdf2.sort_index(ascending=False)
                fsdf4=fsdf2    
                # 转置
                fsdf4=fsdf4.T
                
                fsdf4.replace(0,'---',inplace=True)
                
                #titletxt="\n***** PEER COMPARISON OF FINANCIAL INDICATORS *****\n"
                titletxt=text_lang("财务比率对比","FINANCIAL INDICATORS: COMPARISON")
                #print(titletxt)
                
                collist=list(fsdf4)
                fsdf4['Item']=fsdf4.index
                fsdf5=fsdf4[['Item']+collist]   
                fsdf6=df_filter_row(fsdf5,exclude_collist=['Item'],symbol='---')
                
                fsdf6=df_sort_priority_list(fsdf6,sort_column='Item',priorityList=['periodType','reportDate','currencyCode'],ascending=True)
                """
                alignlist=['left']+['right']*(len(list(fsdf5))-1)
                print(fsdf6.to_markdown(tablefmt='plain',index=False,colalign=alignlist))                
                """  
                footnote1="Amount unit: billion, based on exchange's local accounting standards"
                footnote2="ROx/EM/turnover rates are based on periodic mean, others on end-term"
                footnote3="Data source: Yahoo Finance, "+str(todaydt)
                footnote='Note:\n'+footnote1+'\n'+footnote2+'\n'+footnote3
                #print('\n',footnote1,'\n',footnote2,'\n',footnote3) 
            
                # 将Item科目名称拆分加空格和转大写
                fsdf6['Item']=fsdf6['Item'].apply(lambda x: text_separate(x))
            
                # 将Item科目名称拆分加空格和转大写
                fsdf6['Item']=fsdf6['Item'].apply(lambda x: text_separate(x))
                
                # 判断是否仅输出部分科目
                if 'all' in items_included:
                    fsdf7=fsdf6
                else:
                    mask=fsdf6['Item'].isin(items_included)
                    fsdf7=fsdf6[mask]
                    # 将Item列转为分类类型，指定顺序
                    fsdf7['Item'] = pd.Categorical(fsdf7['Item'], categories=items_included, ordered=True)    
                    # 按分类顺序排序
                    fsdf7=fsdf7.sort_values(by='Item')
                
                df_display_CSS(fsdf7,titletxt=titletxt,footnote=footnote,facecolor=facecolor, \
                               titile_font_size=titile_font_size,heading_font_size=heading_font_size, \
                                   data_font_size=data_font_size)                
                return fsdf6

        return fsdf2     
       
    #elif ('dupont' in analysis_type1) and (('identity' in analysis_type1) or ('analysis' in analysis_type1)):
    elif contains_any(analysis_type1,['dupont','identity']):
        # 股票需为股票列表        
        if not isinstance(tickers,list):
            print("  #Warning(fs_analysis_china): must be a ticker list for",tickers)
            return None    
            
        business_period=business_period.lower()
        fsdf=pd.DataFrame()
        print("  Working on dupont identity, it may take long time ...")
        for t in tickers:
            print("  Getting financial rates for dupont identity of",t,"...")
            with HiddenPrints():            
                dftmp=get_financial_rates(t)
            if dftmp is None:
                print("  #Warning(fs_analysis): financial info unaccessible for",t)
                if test_yahoo_access():
                    print(f"  Solution: if {t} are correct, then try again later")
                else:
                    print("  Problem: no internet connection to Yahoo for retrieveing data")

                return None
            
            if not last_in_list(t,tickers):
                sleep_random(max_sleep=60)

            if business_period=='recent':
                dftmp2=dftmp.tail(1)
            elif business_period=='annual':
                dftmp2=dftmp[dftmp['periodType']=='12M'].tail(1)
            elif business_period=='quarterly':
                dftmp2=dftmp[dftmp['periodType']=='3M'].tail(1)
            else:
                dftmp2=dftmp.tail(1)
            
            """
            dftmp2=pd.DataFrame(dftmp2)
            fsdf=pd.concat([fsdf,dftmp2])      
            """
            #删除重复的列名，若存在重复列会出现错误InvalidIndexError: Reindexing
            dftmp2t=dftmp2.T
            dftmp2t['item']=dftmp2t.index
            dftmp2t.drop_duplicates(keep='first',inplace=True)
            dftmp2t.drop(columns=['item'],inplace=True)
            dftmp3=dftmp2t.T
            
            if fsdf is None:
                fsdf=dftmp3
            else:
                fsdf=pd.concat([fsdf,dftmp3],ignore_index=True)            
            
        # 多只股票的杜邦分析对比  
        fsdf['periodType']=fsdf['periodType'].apply(lambda x: 'Annual' if x=='12M' else 'Quarterly')
        fsdf['Company']=fsdf['ticker'].apply(lambda x: ticker_name(x))
        
        
        collist=['Company','periodType','endDate','Profit Margin','Total Asset Turnover','Equity Multiplier','Return on Equity']
        df=fsdf[collist]
        ticker='Company'
        name1='Profit Margin'
        name2='Total Asset Turnover'
        name3='Equity Multiplier'
        name4='Return on Equity'
        name5='endDate'     
        
        if dupont_sort=='PM':
            df.sort_values(name1,ascending=False,inplace=True)
        elif dupont_sort=='TAT':
            df.sort_values(name2,ascending=False,inplace=True)
        elif dupont_sort=='EM':
            df.sort_values(name3,ascending=False,inplace=True)
        else:
            df.sort_values(name1,ascending=False,inplace=True)        
        
        df2=df.copy()
        df2[name1]=df2[name1].apply(lambda x: x * scale1) 
        df2[name2]=df2[name2].apply(lambda x: x * scale2)
        
        fin_period=df2['endDate'].values[0]

        #f,ax1 = plt.subplots(1,figsize=(10,5))
        f,ax1 = plt.subplots(1,figsize=(12.8,6.4))
        w = 0.75
        x = [i+1 for i in range(len(df2[name1]))]
        tick_pos = [i for i in x]
        
        hatchlist=['.', 'o', '\\']
        ax1.bar(x,df2[name3],width=w,bottom=[i+j for i,j in zip(df2[name1],df2[name2])], \
                label=name3,alpha=0.5,color='green',hatch=hatchlist[0], \
                edgecolor='black',align='center')
        ax1.bar(x,df2[name2],width=w,bottom=df2[name1],label=name2,alpha=0.5,color='red', \
                hatch=hatchlist[1], edgecolor='black',align='center')
        ax1.bar(x,df2[name1],width=w,label=name1,alpha=0.5,color='blue', \
                hatch=hatchlist[2], edgecolor='black',align='center')
    
        plt.xticks(tick_pos,df2[ticker])
        plt.ylabel("Items (Amplified)")
            
        footnote1="[Bar amplifier] "+name1+'：x'+str(scale1)+'，'+name2+'：x'+str(scale2)
        footnote2='Statement period: '+fin_period+'. Bar height does not indicate ROE value.'
        footnote3="Data source: Yahoo Finance，"+todaydt
        footnote ='\n'+footnote1+'\n'+footnote2+'\n'+footnote3
        plt.xlabel(footnote,fontsize=10)
        
        plt.legend(loc='best',fontsize=10)
        plt.title(text_lang("杜邦分析对比","Dupont Identity Analysis"))
        plt.xlim([min(tick_pos)-w,max(tick_pos)+w])
        
        plt.gca().set_facecolor(facecolor)
        plt.show()    
        
        if printout:
            #title_txt="\n***** Dupont Identity Fact Sheet *****\n"
            titletxt=text_lang("杜邦分析数据表","Dupont Identity Fact Sheet")
            #print(titletxt)
            
            # 保留四位小数
            collist=list(df)
            for c in collist:
                try:
                    df[c]=round(df[c],4)
                except:
                    continue            
            
            for d in list(df):
                df[d]=df[d].apply(lambda x: round(x,5) if isinstance(x,float) else x)
            """
            alignlist=['left']+['right']*(len(list(df))-1)
            print(df.to_markdown(tablefmt='plain',index=False,colalign=alignlist))                
            """    
            footnote1="Based on exchange's local accounting standards, EM/TAT are on periodic mean"
            footnote2="Data source: Yahoo Finance, "+str(todaydt)
            footnote='Note:\n'+footnote1+'\n'+footnote2
            #print('\n',footnote1,'\b.',footnote2)  
            
            # 将Item科目名称拆分加空格和转大写
            df['Item']=df['Item'].apply(lambda x: text_separate(x))
             
            df_display_CSS(df,titletxt=titletxt,footnote=footnote,facecolor=facecolor,decimals=4, \
                           titile_font_size=titile_font_size,heading_font_size=heading_font_size, \
                               data_font_size=data_font_size)        
        return  df2      
    
    else:   # analysis_type1
        print("  #Warning(fs_analysis): sorry, no idea on what to do for",analysis_type)
    return None


#==============================================================================

if __name__ == '__main__':
    sort_column='Item'
    priorityList=['periodType']
    
    df_sort_priority_list(df,sort_column='Item',priorityList=['periodType'],ascending=True)
    df_sort_priority_list(df,sort_column='Item',priorityList=['periodType'],ascending=False)
    
def df_sort_priority_list(df,sort_column='',priorityList=[],ascending=True):
    """
    功能：为df排序，但保持某些优先项目按顺序排在前面
    """
    if sort_column == '': #无需排序
        return df
    
    if len(priorityList) > 0: # 存在优先项目
        df['priority_seq']=df[sort_column].apply(lambda x: priorityList.index(x) if x in priorityList else 9)
        
        df.sort_values(by=['priority_seq',sort_column],ascending=[True,ascending],inplace=True)
        
        df.drop('priority_seq',axis=1,inplace=True) #删除列
    else:
        df.sort_values(by=[sort_column],ascending=ascending,inplace=True)
    
    return df
        
    
#==============================================================================
#==============================================================================