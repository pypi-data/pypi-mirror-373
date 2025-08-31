# -*- coding: utf-8 -*-
"""
本模块功能：上市公司的财务报表分析，数据层
特点1：科目项目不采用字符串匹配方法，采用contains_any和contains_all匹配方法！
特点2：以苹果财报的项目名称为基准！其他股票的财报项目名称若不同则转换为苹果财报的名称
所属工具包：证券投资分析工具SIAT 
SIAT：Security Investment Analysis Tool
创建日期：2024年11月28日
最新修订日期：2024年11月28日
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

import pandas as pd
import numpy as np
#==============================================================================
#本模块使用yahooquery插件
#==============================================================================
if __name__=='__main__':
    symbol='AAPL' #以其财报项目名称作为基准
    
    symbol='JD'
    symbol='INTL' 
    symbol='MSFT'
    symbol='600519.SS'
    symbol='00700.HK'
    
    symbol='601398.SS'
    symbol='601328.SS'
    
    report_type="balance sheet"
    report_period="all"
    max_count=3; max_sleep=30
    fix_entry=False; printout=False
    auto_language=True
    
    bsdf_raw=get_1statement_yahoo2(symbol,report_type="balance sheet",fix_entry=False)
    bsdf_fix=get_1statement_yahoo2(symbol,report_type="balance sheet",fix_entry=True)
    
    isdf_raw=get_1statement_yahoo2(symbol,report_type="income statement",fix_entry=False)

    
    cfsdf_raw=get_1statement_yahoo2(symbol,report_type="cash flow",fix_entry=False)



def get_1statement_yahoo2(symbol,report_type="balance sheet", \
                          report_period="annual", \
                          max_count=3,max_sleep=30, \
                          fix_entry=False,printout=False, \
                          auto_language=False,language_engine='baidu', \
                          entry_split=True,split_improve=True):
    """
    功能：获取雅虎财经上一只股票所有的年度和季度资产负债表，采用contains匹配法
    
    参数：
    symbol：股票代码，五位港股需要转换为四位
    report_type：需要抓取的财报类型，默认资产负债表"balance sheet"
    report_period：财报期间，默认年报，可选年报+季报(all)或单纯季报(quarterly)
    max_count：抓取失败时的总尝试次数，默认3
    max_sleep=30：抓取失败时再次尝试间隔的随机秒数最大值
    fix_entry：是否对重点科目进行检查和填充，默认是False
    printout：是否打印抓取到的财报，默认否False
    auto_language：是否自动进行翻译，默认否False，自动翻译True
    
    返回值：成功时返回df，失败时返回None
    """
    
    report_type=report_type.lower()
    if 'balance' in report_type:
        report_type="balance sheet"
    elif 'income' in report_type:
        report_type="income statement"
    else:
        report_type="cash flow statement"
    print(f"  Retrieving {report_type} of {symbol} ... ...")
    
    symbol=symbol.upper()
    result,prefix,suffix=split_prefix_suffix(symbol)
    #处理港股代码：五位变四位
    if result & (suffix=='HK'):
        if len(prefix)==5:
            symbol=symbol[1:]
    
    #=====抓取财务报告==========================================================
    from yahooquery import Ticker
    #问题：如何判断无效的symbol?
    try:
        stock = Ticker(symbol)    
    except:
        print("  #Warning(get_1statement_yahoo2): currently unaccessable to Yahoo")
        return None
    
    if contains_any(report_period,['all','annual']):
        #获取近5年年报，最多尝试max_count次
        for c in range(max_count):
            if report_type=="balance sheet":
                stmta=stock.balance_sheet()  # Defaults to Annual
            elif report_type=="income statement":
                stmta=stock.income_statement()
                #去掉TTM，数据不全
                stmta=stmta[stmta['periodType'] != 'TTM']
            else:
                stmta=stock.cash_flow()
                
            #若抓取成功则直接结束
            if isinstance(stmta,pd.DataFrame): break
        
            #若能够访问雅虎则挂起一会儿再尝试访问，否则结束
            if test_yahoo_finance():
                sleep_random(max_sleep)
            else: break
    
        #获取信息失败，判断原因        
        if not isinstance(stmta,pd.DataFrame):
            if test_yahoo_finance():
                print("  #Warning(get_1statement_yahoo2): {} not found for annual reports".format(symbol))
            else:
                print("  #Warning(get_1statement_yahoo2): sorry, Yahoo Finance currently unaccessable")
            return None
    else:
        stmta=None

    if contains_any(report_period,['all','quarterly']):
        #获取近7个季度报，注意含其中跨过的年报，与年报合并时需要去重！
        for c in range(max_count):
            if report_type=="balance sheet":
                stmtq=stock.balance_sheet(frequency="q")  # Defaults to Annual
            elif report_type=="income statement":
                stmtq=stock.income_statement(frequency="q")
                #去掉TTM，数据不全
                stmtq=stmtq[stmtq['periodType'] != 'TTM']
            else:
                stmtq=stock.cash_flow(frequency="q")
            
            if isinstance(stmtq,pd.DataFrame): break
            else:
                sleep_random(max_sleep)
        
            #前面已经判断过雅虎是否能够访问以及symbol是否存在，此处无需再判断
    else:
        stmtq=None
    
    #合并年度和季度报表
    if not (stmta is None) and not (stmtq is None):
        stmt=pd.concat([stmta,stmtq])
    elif not (stmta is None):
        stmt=stmta
    elif not (stmtq is None):
        stmt=stmtq        
    else:
        print("  #Error(get_1statement_yahoo2): retrieved no periodic reports for",symbol)
        return None    

    #合并后排序+去重：季报中可能还含有年报
    stmt.sort_values(by=['asOfDate','periodType'],inplace=True)
    #去掉重复记录: 保留年报数据项多，去掉数据项少的季报
    stmt.drop_duplicates(subset=['asOfDate'],keep='first',inplace=True)
    
    
    #=====关键字段检查与缺失替代处理=============================================
    if fix_entry:
        
        if report_type=="balance sheet":
            #检查和填补资产负债表科目
            stmt=check_fill_bs_yahoo(stmt)
        elif report_type=="income statement":
            #检查和填补利润表科目
            stmt=check_fill_is_yahoo(stmt)
        else:
            #检查和填补现金流量表科目
            stmt=check_fill_cfs_yahoo(stmt)

    #字段再排序
    stmt_cols=list(stmt)
    head_cols=['asOfDate','periodType','currencyCode'] #不参与排序的字段
    for c in head_cols:
        stmt_cols.remove(c)
    stmt_cols.sort()
    stmt_cols=head_cols+stmt_cols
    stmt=stmt[stmt_cols]
    
    #总检查：总资产=总负债+总权益是否成立
    #stmt['TA-TL-TE']=stmt['TotalAssets']-stmt['TotalLiabilities']-stmt['TotalEquity']
    
    #是否打印供检查
    if printout:
        print_stmt_yahoo2(stmt,title_prefix=report_type.title(), \
                          auto_language=auto_language,language_engine=language_engine, \
                          entry_split=entry_split,split_improve=split_improve)
    
    return stmt    
    

#==============================================================================
if __name__=='__main__':
    symbol="AAPL"
    
    from yahooquery import Ticker
    stock = Ticker(symbol)
    stmt=stock.balance_sheet()
    
    df=check_fill_bs_yahoo(stmt)

def check_fill_bs_yahoo(stmt):
    """
    
    功能：检查和填补雅虎抓取到的资产负债表部分科目
    科目基准：苹果财报科目
    
    输入：雅虎抓取到的原始资产负债表
    输出：经过检查的资产负债表，缺失科目可不断填充
    
    注意：单纯在资产负债表内填充缺失项比较勉强
    抓取单表后可暂不填充，在在三表合成后综合填充！！！
    """
    #=====资产部分
    #应收账款
    entry_item='AccountsReceivable' #主项科目
    #entry_item in list(stmt)
    entry_words=["accounts","receivable"] #主项科目的关键词，忽略字母大小写
    #可替代科目组的关键词列表组
    entry_alternatives=[["receivables"]]
    stmt=check_fill_entry(stmt,entry_item,entry_words,entry_alternatives)
        
    
    #存货
    entry_item='Inventory' #主项科目
    #entry_item in list(stmt)
    entry_words=["inventory"] #主项科目的关键词，忽略字母大小写
    #可替代科目组的关键词列表组
    entry_alternatives=[]
    stmt=check_fill_entry(stmt,entry_item,entry_words,entry_alternatives)
    
    
    #=====负债部分
    #流动（有息）债务CurrentDebt：可替代科目-流动负债
    entry_item='CurrentDebt' #主项科目
    entry_words=["current","debt"] #主项科目的关键词，忽略字母大小写
    #可替代科目组的关键词列表组
    #entry_alternatives=[["current","liabilities"],["current","borrowing"],["current","obligation"]]
    entry_alternatives=[["current","liabilities"]]
    stmt=check_fill_entry(stmt,entry_item,entry_words,entry_alternatives)

        
    #流动负债（有息债务+应付）
    entry_item='CurrentLiabilities' #主项科目
    entry_words=["current","liabilities"] #主项科目的关键词，忽略字母大小写
    #可替代科目组的关键词列表组
    entry_alternatives=[["current","debt"]]
    stmt=check_fill_entry(stmt,entry_item,entry_words,entry_alternatives)
    

    #应付账款
    entry_item='AccountsPayable' #主项科目
    #entry_item in list(stmt)
    entry_words=["accounts","payable"] #主项科目的关键词，忽略字母大小写
    #可替代科目组的关键词列表组
    entry_alternatives=[["payables"]]
    stmt=check_fill_entry(stmt,entry_item,entry_words,entry_alternatives)

        
    #总（有息）债务
    entry_item='TotalDebt' #主项科目
    #entry_item in stmt_cols
    entry_words=["total","debt"] #主项科目的关键词，忽略字母大小写
    #可替代科目组的关键词列表组
    entry_alternatives=[["total","liabilities"]]
    stmt=check_fill_entry(stmt,entry_item,entry_words,entry_alternatives)
        
        
    #总负债
    entry_item='TotalLiabilities' #主项科目
    #entry_item in list(stmt)
    entry_words=["total","liabilities"] #主项科目的关键词，忽略字母大小写
    #可替代科目组的关键词列表组
    entry_alternatives=[["total","debt"]]
    stmt=check_fill_entry(stmt,entry_item,entry_words,entry_alternatives)

    
    #=====权益部分        
    #权益总额
    entry_item='TotalEquity' #主项科目
    #entry_item in list(stmt)
    entry_words=["total","equity"] #主项科目的关键词，忽略字母大小写
    #可替代科目组的关键词列表组
    entry_alternatives=[["stock","holder","quity"]]
    stmt=check_fill_entry(stmt,entry_item,entry_words,entry_alternatives)


    return stmt

#==============================================================================
if __name__=='__main__':
    from yahooquery import Ticker
    stock = Ticker("AAPL")
    stmt=stock.income_statement()
    
    df=check_fill_is_yahoo(stmt)

def check_fill_is_yahoo(stmt):
    """
    
    功能：检查和填补雅虎抓取到的利润表部分科目
    输入：雅虎抓取到的原始利润表
    输出：经过检查的利润表，缺失科目可不断填充
    
    注意：单纯在利润表内填充缺失项比较勉强，可在三表合成后综合填充！！！
    """

    #=====收入部分
    #成本与费用
    #利息费用
    entry_item='InterestExpense' #主项科目
    #entry_item in list(stmt)
    entry_words=["interest","expense"] #主项科目的关键词，忽略字母大小写
    #可替代科目组的关键词列表组
    entry_alternatives=[["interest","expense","operating"]]
    stmt=check_fill_entry(stmt,entry_item,entry_words,entry_alternatives)
        
    #收入成本
    entry_item='CostOfRevenue' #主项科目
    #entry_item in list(stmt)
    entry_words=["cost","revenue"] #主项科目的关键词，忽略字母大小写
    #可替代科目组的关键词列表组
    entry_alternatives=[["reconciled","cost","revenue"]]
    stmt=check_fill_entry(stmt,entry_item,entry_words,entry_alternatives)
        
    #营业成本
    entry_item='OperatingExpense' #主项科目
    #entry_item in list(stmt)
    entry_words=["operating","expense"] #主项科目的关键词，忽略字母大小写
    #可替代科目组的关键词列表组
    entry_alternatives=[["cost","revenue"]]
    stmt=check_fill_entry(stmt,entry_item,entry_words,entry_alternatives)
        
    #折旧与摊销
    entry_item='Depreciation' #主项科目
    #entry_item in list(stmt)
    entry_words=["depreciation"] #主项科目的关键词，忽略字母大小写
    #可替代科目组的关键词列表组
    entry_alternatives=[["reconciled","depreciation"]]
    stmt=check_fill_entry(stmt,entry_item,entry_words,entry_alternatives)
    
    #收入与利润    
    #营业收入
    entry_item='OperatingRevenue' #主项科目
    #entry_item in list(stmt)
    entry_words=["operating","revenue"] #主项科目的关键词，忽略字母大小写
    #可替代科目组的关键词列表组
    entry_alternatives=[["total","revenue"]]
    stmt=check_fill_entry(stmt,entry_item,entry_words,entry_alternatives)
        
    #营业利润
    entry_item='OperatingIncome' #主项科目
    #entry_item in list(stmt)
    entry_words=["operating","income"] #主项科目的关键词，忽略字母大小写
    #可替代科目组的关键词列表组
    entry_alternatives=[]
    stmt=check_fill_entry(stmt,entry_item,entry_words,entry_alternatives)
        
    empty = stmt[entry_item].isna().all()
    if empty:
        stmt[entry_item]=stmt['OperatingRevenue']-stmt['OperatingExpense']
    
    #EBITDA
    entry_item='EBITDA' #主项科目
    #entry_item in list(stmt)
    entry_words=["ebitda"] #主项科目的关键词，忽略字母大小写
    #可替代科目组的关键词列表组
    entry_alternatives=[]
    stmt=check_fill_entry(stmt,entry_item,entry_words,entry_alternatives)
    
    #EBIT
    entry_item='EBIT' #主项科目
    #entry_item in list(stmt)
    entry_words=["ebitda"] #主项科目的关键词，忽略字母大小写
    #可替代科目组的关键词列表组
    entry_alternatives=[]
    stmt=check_fill_entry(stmt,entry_item,entry_words,entry_alternatives)
    empty = stmt[entry_item].isna().all()
    if empty:
        stmt[entry_item]=stmt['EBITDA']+stmt['Depreciation']
    
    #毛利润
    entry_item='GrossProfit' #主项科目
    #entry_item in list(stmt)
    entry_words=["gross","profit"] #主项科目的关键词，忽略字母大小写
    #可替代科目组的关键词列表组
    entry_alternatives=[["operating","income"],["pretax","income"]]
    stmt=check_fill_entry(stmt,entry_item,entry_words,entry_alternatives)
        
    empty = stmt[entry_item].isna().all()
    if empty:
        stmt[entry_item]=stmt['OperatingRevenue']-stmt['OperatingExpense']
        
        empty = stmt[entry_item].isna().all()
        if empty:
            stmt[entry_item]=stmt['EBITDA']
        
    
    return stmt

#==============================================================================
if __name__=='__main__':
    from yahooquery import Ticker
    stock = Ticker("AAPL")
    stmt=stock.cash_flow()
    
    df=check_fill_cfs_yahoo(stmt)
    
def check_fill_cfs_yahoo(stmt):
    """
    
    功能：检查和填补雅虎抓取到的现金流量表部分科目
    输入：雅虎抓取到的原始现金流量表
    输出：经过检查的现金流量表，缺失科目可不断填充
    
    注意：单纯在现金流量表内填充缺失项比较勉强，可在三表合成后综合填充！！！
    """
    
    #现金股利支付
    entry_item='CashDividendsPaid' #主项科目
    #entry_item in list(stmt)
    entry_words=["cash","dividends","paid"] #主项科目的关键词，忽略字母大小写
    #可替代科目组的关键词列表组
    entry_alternatives=[["common","stock","dividend","paid"]]
    stmt=check_fill_entry(stmt,entry_item,entry_words,entry_alternatives)
    
    #融资活动现金流
    entry_item='CashFlowFromFinancingActivities' #主项科目
    #entry_item in list(stmt)
    entry_words=["cash","flow","from","financing","activities"] #主项科目的关键词，忽略字母大小写
    #可替代科目组的关键词列表组
    entry_alternatives=[["cash","flow","from","continuing","financing","activities"],["financing","cash","flow"]]
    stmt=check_fill_entry(stmt,entry_item,entry_words,entry_alternatives)
    
    #投资活动现金流
    entry_item='CashFlowFromInvestingActivities' #主项科目
    #entry_item in list(stmt)
    entry_words=["cash","flow","from","investing","activities"] #主项科目的关键词，忽略字母大小写
    #可替代科目组的关键词列表组
    entry_alternatives=[["cash","flow","from","continuing","investing","activities"],["investing","cash","flow"]]
    stmt=check_fill_entry(stmt,entry_item,entry_words,entry_alternatives)
    
    #经营活动现金流
    entry_item='CashFlowFromOperatingActivities' #主项科目
    #entry_item in list(stmt)
    entry_words=["cash","flow","from","operating","activities"] #主项科目的关键词，忽略字母大小写
    #可替代科目组的关键词列表组
    entry_alternatives=[["cash","flow","from","continuing","operating","activities"],["operating","cash","flow"]]
    stmt=check_fill_entry(stmt,entry_item,entry_words,entry_alternatives)

    return stmt
#==============================================================================
if __name__=='__main__':
    from yahooquery import Ticker
    stock = Ticker("AAPL")
    stmt=stock.income_statement()
    
    stmt=get_financial_statements2_yahoo('JD',printout=False)
    
    title_prefix="Balance Sheet"
    title_prefix="Cash Flow Statement"
    title_prefix="Integrated Financial Statements"
    
    auto_language=True
    entry_split=True
    split_improve=True
    language_engine=['baidu','sogou','bing','google']
    
    stmt=get_financial_statements2_yahoo('JD',printout=False)
    
    print_stmt_yahoo2(stmt,title_prefix)
    
def print_stmt_yahoo2(stmt,title_prefix, \
                      auto_language=True, \
                     #language_engine=['google','bing','sogou'], \
                      entry_split=True,split_improve=True):
    """
    
    功能：打印雅虎抓取的财报
    """
    
    stmtprt1=stmt.copy()
    
    if 'ticker' in list(stmtprt1):
        symbol=stmtprt1['ticker'][0]
        del stmtprt1['ticker']
    else:
        symbol=stmtprt1.index[0]
    
    stmtprt1['reportDate']=stmtprt1['asOfDate'].apply(lambda x: x.strftime("%y-%m-%d"))
    stmtprt1.set_index('reportDate',inplace=True)
    del stmtprt1['asOfDate']
    
    currencyCode=stmtprt1['currencyCode'].values[0]
    del stmtprt1['currencyCode']
    
    cols1=list(stmtprt1)
    cols1.remove('periodType')
    million=1000000
    for c in cols1:
        stmtprt1[c]=stmtprt1[c].apply(lambda x: round(x/million,2))
    
    #科目分词处理与翻译
    stmtprt2=stmtprt1.T
    cols=list(stmtprt2)
    cols.sort(reverse=True)
    stmtprt2=stmtprt2[cols]
    stmtprt2['Item']=stmtprt2.index
    stmtprt2=stmtprt2[['Item']+cols]
    
    lang=check_language()
    
    #科目分词，语言处理：英文
    title_prefix=title_prefix.title()
    titletxt=f"{ticker_name(symbol)}: {title_prefix}, in {currencyCode} millions"
    
    footnote1="Note: 12M = annual report, 3M = quaterly reports"
    import datetime as dt; todaydt=dt.date.today()
    footnote2=", data source: Yahoo, "+str(todaydt)
    footnote=footnote1 + footnote2
    
    if (auto_language and lang=='English') or entry_split:
        item_dict=dict(stmtprt2['Item'])
        item_list=list(stmtprt2['Item'])
        for i in item_list:
            i2=words_split_yahoo(i,split_improve=split_improve)
            item_dict[i]=i2
        stmtprt2['Item']=stmtprt2['Item'].apply(lambda x: item_dict[x])
        
    
    #语言处理：中文
    if 'balance' in title_prefix.lower():
        title_prefix_cn="资产负债表"
    elif 'income' in title_prefix.lower():
        title_prefix_cn="利润表" 
    elif 'cash' in title_prefix.lower():
        title_prefix_cn="现金流量表"
    else:
        title_prefix_cn="三大报表综合"
    title_cn=f"{ticker_name(symbol)}: {title_prefix_cn}, 单位：百万{currencyCode}"
    
    footnote1_cn="注：12M表示年报，3M表示季报"
    footnote2_cn="，数据来源：雅虎，"+str(todaydt)
    footnote_cn=footnote1_cn + footnote2_cn
    
    if auto_language and lang=='Chinese':
        print(f"  Translating into {lang} using AI, just for reference ...")
        
        item_dict=dict(stmtprt2['Item'])
        item_list=list(stmtprt2['Item'])
        for i in item_list:
            print_progress_percent2(i,item_list,steps=10,leading_blanks=4)
            
            #i2=lang_auto2(i,language_engine=language_engine)
            i2=lang_auto2(i)
            #i2=lang_auto(i)
            item_dict[i]=i2
        
        stmtprt2['Item']=stmtprt2['Item'].apply(lambda x: x+'('+item_dict[x]+')')
        """
        if 'bilingual' in str(auto_language).lower():
            stmtprt2['Item']=stmtprt2['Item'].apply(lambda x: x+'('+item_dict[x]+')')
        else:
            stmtprt2['Item']=stmtprt2['Item'].apply(lambda x: item_dict[x])
        """
        
    #语言合成
    titletxt=text_lang(title_cn,titletxt)  
    footnote=text_lang(footnote_cn,footnote)
    
    #删除全为零或空值的行：未做到！
    stmtprt3=stmtprt2.copy()
    cols3=list(stmtprt3)

    stmtprt3.set_index('Item',inplace=True)
    stmtprt3.replace(0,np.nan,inplace=True)
    stmtprt3.dropna(how='all',axis=1,inplace=True)
    stmtprt3['Item']=stmtprt3.index
    stmtprt3=stmtprt3[cols3]
    
    #检测Item是否存在重复值，若存在则df_display_CSS会失败
    index1=stmtprt3[stmtprt3[["Item"]].duplicated(keep="last")].index
    index2=stmtprt3[stmtprt3[["Item"]].duplicated(keep="first")].index
    if not len(index1)==0 and not len(index2)==0:
        cross_index=stmtprt3.loc[index1 | index2,:]
        print("  Unable to display becos of duplicate items [{list(cross_index['Item'])}]")
    else:
        df_display_CSS(stmtprt3,titletxt=titletxt,footnote=footnote, \
                       facecolor='papayawhip',decimals=2, \
                       first_col_align='left',second_col_align='right', \
                       last_col_align='right',other_col_align='right', \
                       titile_font_size='15px',heading_font_size='10px', \
                       data_font_size='10px',footnote_font_size='13px')

    return

#==============================================================================
if __name__ == '__main__':
    entry_item='CurrentDebt' #主项科目
    entry_words=["current","debt"] #主项科目的关键词，忽略字母大小写
    #可替代科目组的关键词列表组
    entry_alternatives=[["current","liabilities"],["current","borrowing"],["current","obligation"]]

    entry_item in list(stmt)
    stmt=check_fill_entry(stmt,entry_item,entry_words,entry_alternatives)
    stmt[entry_item]

def check_fill_entry(stmt,entry_item,entry_words,entry_alternatives):
    """

    功能：检查抓取的原始财报文件stmt中的科目entry_item
    若不存在则使用可替代科目。
    若存在但全为空，则使用可替代科目填充。
    若可替代科目也不存在，则赋值为全空。
    
    参数：
    stmt：赚取到的原始财报df
    entry_item：需要处理的科目
    entry_words：需处理科目的关键词列表
    entry_alternatives：可替代科目的关键词组列表
    
    返回值：更新后的财报df
    """    
    
    #合成所有的关键词列表组
    entry_options=[entry_words]+entry_alternatives
    
    #按照相似度匹配
    stmt_cols=list(stmt)
    entry_name=list_contains_all_list(stmt_cols,entry_options)
    
    if entry_name: #找到
        if entry_name != entry_item: #找到但不同名
            #若科目名称不同则映射该名称
            stmt[entry_item]=stmt[entry_name]
            #del stmt[entry_name] #删除替代项目名称
        else: #找到同名
            #检查该科目是否全为空
            empty = stmt[entry_item].isna().all()
            if empty:
                entry_name_alternative=list_contains_all_list(stmt_cols,entry_alternatives)
                stmt[entry_item]=stmt[entry_name_alternative]
    else: #主项未找到，可替代科目也未找到
        stmt[entry_item]=np.nan

    return stmt

#==============================================================================
#==============================================================================
if __name__=='__main__':
    ticker='AAPL' 
    ticker='00700.HK' 
    
    report_period="annual"
    max_count=3; max_sleep=30
    pre_fix_entry=False; post_fix_entry=True
    pre_printout=False; printout=True
    
    fsdf=get_financial_statements2_yahoo(ticker)

def get_financial_statements2_yahoo(ticker, \
                                    report_period="annual", \
                                    max_count=3,max_sleep=30, \
                                    pre_fix_entry=False,post_fix_entry=True, \
                                    auto_language=False, \
                                   #language_engine=['baidu','sogou','bing','google'], \
                                    entry_split=True,split_improve=False, \
                                    pre_printout=False,printout=False):
    """
    
    功能：获取雅虎财经上一只股票所有的年度和季度财务报表
    参数：
    ticker：一只股票的代码
    report_period：报告期间，默认年报"annual"，可选季报"quarterly"或所有"all"
    max_count：爬虫失败时的最大尝试次数，默认3
    max_sleep：每次抓取数据的时间间隔，规避反爬虫，默认30秒
    pre_fix_entry：抓取资产负债表、利润表、现金流量表时是否单独修复科目数据，默认否False
    post_fix_entry：抓取资产负债表、利润表、现金流量表后是否统一修复科目数据，默认是True
    auto_language：是否自动翻译科目语言，默认否False
    language_engine：语言翻译引擎，默认'baidu'，可选必应"bing"、谷歌"google"等
    entry_split：抓取数据后是否分拆科目名称单词，默认否False
    split_improve：抓取数据后分拆科目单词时是否调整，默认否False
    pre_printout：抓取资产负债表、利润表和现金流量表时是否单独显示，默认否False
    printout：抓取资产负债表、利润表和现金流量表后是否统一显示，默认否False
    """
    # 测试雅虎连通性
    if not test_yahoo_access():
        print("  Sorry, data source yahoo is inaccessible")
        return None
    
    # 变换港股代码5位-->4位
    result,prefix,suffix=split_prefix_suffix(ticker)
    if result & (suffix=='HK'):
        if len(prefix)==5:
            ticker=ticker[1:]
    
    print(f"  Searching for financial statements of {ticker} ... ...")
    
    #获取资产负债表
    df_bs=get_1statement_yahoo2(ticker,report_type="balance sheet", \
                              report_period=report_period, \
                              max_count=max_count,max_sleep=max_sleep, \
                              fix_entry=pre_fix_entry, \
                              auto_language=False, \
                             #language_engine=language_engine, \
                              entry_split=entry_split,split_improve=split_improve, \
                              printout=pre_printout)
    
    
    #获取利润表
    df_is=get_1statement_yahoo2(ticker,report_type="income statement", \
                              report_period=report_period, \
                              max_count=max_count,max_sleep=max_sleep, \
                              fix_entry=pre_fix_entry, \
                              auto_language=False, \
                             #language_engine=language_engine, \
                              entry_split=entry_split,split_improve=split_improve, \
                              printout=pre_printout)
    
    
    #获取现金流量表
    df_cfs=get_1statement_yahoo2(ticker,report_type="cash flow statement", \
                              report_period=report_period, \
                              max_count=max_count,max_sleep=max_sleep, \
                              fix_entry=pre_fix_entry, \
                              auto_language=False, \
                             #language_engine=language_engine, \
                              entry_split=entry_split,split_improve=split_improve, \
                              printout=pre_printout)
    
    #=====三表合并
    #合并1：资产负债表+利润表
    head_cols=['asOfDate','periodType','currencyCode']
    df_bs_is=pd.merge(df_bs,df_is,on=head_cols)
    
    #合并2：+现金流量表
    df=pd.merge(df_bs_is,df_cfs,on=head_cols)
    df['ticker']=ticker
    
    #合并后删除重复列
    df.rename(columns={'NetIncome_x':'NetIncome'},inplace=True)
    try:
        del df['NetIncome_y']
    except:
        pass
    
    #合成后填充缺失项
    if post_fix_entry:
        df1=check_fill_fs_yahoo(df)
    else:
        df1=df
        
    #print(f"  Successfully retrieved 3 financial statements of {ticker}")    
    
    if printout:
        df2=df1.copy()
        title_prefix="Comprehensive Financial Statement"
        
        print_stmt_yahoo2(df2,title_prefix="Integrated Financial Statements", \
                          auto_language=auto_language, \
                         #language_engine=language_engine, \
                          entry_split=entry_split,split_improve=split_improve)

    
    return df1    
    
#==============================================================================
if __name__=='__main__':
    from yahooquery import Ticker
    stock = Ticker("AAPL")
    stmt=stock.cash_flow()
    
    df=check_fill_cfs_yahoo(stmt)
    
def check_fill_fs_yahoo(stmt):
    """
    
    功能：检查和填补雅虎抓取到的三张表合成后缺失项
    输入：雅虎抓取到的三张表合成
    输出：经过检查的三张表合成，缺失科目可不断填充
    
    注意：单纯在资产负债表/利润表/现金流量表内填充缺失项比较勉强，可在三表合成后综合填充
    """
    df=stmt.copy()
    #为计算方便，将所有的nan替换为0
    df.fillna(0,inplace=True)
    
    
    
    
    
    
    
    
    return df



"""
最终获得的表结构：
['asOfDate（截止日期）',
 'periodType（期间类型）',
 
 'AccountsPayable(应付账款)',
 'AccountsReceivable(应收账款)',
 'AccumulatedDepreciation（累计折旧）',
 'AdditionalPaidInCapital（资本公积，资本溢价；paid-in capital：实收资本；缴入资本）',
 'AllowanceForDoubtfulAccountsReceivable（备抵应收呆帐）',
 'AvailableForSaleSecurities（可供出售金融资产；trading securities: 交易性金融资产）',
 'BuildingsAndImprovements（建筑物及其改良）',
 'CapitalStock（股本）',
 'CashAndCashEquivalents（现金及现金等价物）',
 'CashCashEquivalentsAndShortTermInvestments（现金、现金等价物及短期投资）',
 'CashEquivalents（现金等价物）',
 'CashFinancial（？）',
 'CommonStock（普通股）',
 'CommonStockEquity（普通股权益？）',
 'ConstructionInProgress（在建工程）',
 'CurrentAssets（流动资产）',
 'CurrentLiabilities（流动负债）',
 'DividendsPayable（应付股利）',
 'FinishedGoods（制成品）',
 'GoodwillAndOtherIntangibleAssets（商誉及其他无形资产）',
 'GrossAccountsReceivable（应收账款总额）',
 'GrossPPE（固定资产总额）',
 'InventoriesAdjustmentsAllowances（存货调整备抵）',
 'Inventory（存货）',
 'InvestedCapital（投入资本）',
 'InvestmentinFinancialAssets（金融资产投资）',
 'LandAndImprovements（土地及其改良）',
 'MachineryFurnitureEquipment（机械家具设备）',
 'MinorityInterest（少数股东利益）',
 'NetPPE（固定资产净值）',
 'NetTangibleAssets（有形资产净值）',
 'NonCurrentDeferredAssets（非流动递延资产）',
 'NonCurrentDeferredTaxesAssets（非流动递延税项资产）',
 'NonCurrentDeferredTaxesLiabilities（非流动递延税金负债）',
 'OrdinarySharesNumber（普通股？）',
 'OtherCurrentAssets（其他流动资产）',
 'OtherCurrentLiabilities（其他流动负债）',
 'OtherEquityInterest（其他股权）',
 'OtherIntangibleAssets（其他有形资产）',
 'OtherNonCurrentAssets（其他非流动资产）',
 'OtherPayable（其它应付款）',
 'OtherProperties（？）',
 'OtherReceivables（其他应收款）',
 'Payables（应付款项）',
 'PrepaidAssets（预付资产）',
 'Properties（财产？物业？）',
 'RawMaterials（原材料）',
 'RetainedEarnings（留存收益）',
 'ShareIssued（股票发行）',
 'StockholdersEquity（股东权益）',
 'TangibleBookValue（有形资产账面价值）',
 'TotalAssets（总资产）',
 'TotalCapitalization（资本总额？）',
 'TotalEquityGrossMinorityInterest（权益与少数股东利益总额）',
 'TotalLiabilitiesNetMinorityInterest（扣除少数股东利益的总负债）',
 'TotalNonCurrentAssets（非流动资产总额）',
 'TotalNonCurrentLiabilitiesNetMinorityInterest（扣除少数股东利益的非流动负债总额）',
 'TotalTaxPayable（应缴税款总额）',
 'TradeandOtherPayablesNonCurrent（贸易与其他非流动应付款）',
 'WorkInProcess（在制品）',
 'WorkingCapital（营运资本）',
 'Amortization（摊销）',
 
 'BasicAverageShares（未稀释的平均股数）',
 'BasicEPS（基本每股收益，指属于普通股股东的当期净利润，除以发行在外普通股的加权平均数，可按存在月数加权）',
 'CostOfRevenue（收入成本，营收成本）',
 'DepreciationAndAmortizationInIncomeStatement（损益表中的折旧和摊销）',
 'DepreciationIncomeStatement（损益表中的折旧）',
 'DilutedAverageShares（稀释后的平均股数）',
 'DilutedEPS（考虑了可转换债券和股票期权可能行权对于流通在外股数的影响）',
 'EBIT（息税前利润）',
 'EBITDA（未计利息、税项、折旧及摊销前的利润）',
 'GeneralAndAdministrativeExpense（一般管理费用）',
 'GrossProfit（毛利润）',
 'ImpairmentOfCapitalAssets（资本资产减值）',
 'InterestExpense（利息费用）',
 'InterestExpenseNonOperating（非经营性利息费用）',
 'InterestIncome（利息收益）',
 'InterestIncomeNonOperating（非经营性利息收入）',
 'MinorityInterests（少数股东利益）',
 'NetIncome（净利润）',
 'NetIncomeCommonStockholders（归属于普通股股东的净利润，用于计算EPS和PE）',
 'NetIncomeContinuousOperations（扣非后净利润）',
 'NetIncomeFromContinuingAndDiscontinuedOperation（来自持续经营和停止经营业务的净收入）',
 'NetIncomeFromContinuingOperationNetMinorityInterest（不归属少数股东的扣非后净利润？）',
 'NetIncomeIncludingNoncontrollingInterests（包括非控股权的净收入？）',
 'NetInterestIncome（净利息收入）',
 'NetNonOperatingInterestIncomeExpense（非营业外利息收入费用净值）',
 'NormalizedEBITDA（调整后EBITDA）',
 'NormalizedIncome（调整后利润）',
 'OperatingExpense（营业费用）',
 'OperatingIncome（营业利润）',
 'OperatingRevenue（营业收入）',
 'OtherNonOperatingIncomeExpenses（其他营业外收入支出）',
 'OtherOperatingExpenses（其它营业费用）',
 'OtherSpecialCharges（其他特殊费用）',
 'OtherunderPreferredStockDividend（优先股股利下的其他项目）',
 'PretaxIncome（税前利润）',
 'ReconciledCostOfRevenue（对账后的经营收入成本）',
 'ReconciledDepreciation（对账后的折旧）',
 'RentAndLandingFees（租金及土地费用）',
 'RentExpenseSupplemental（补充租金费用）',
 'ResearchAndDevelopment（研发费用）',
 'SellingAndMarketingExpense（销售和市场营销费用）',
 'SellingGeneralAndAdministration（销售及一般管理费用）',
 'SpecialIncomeCharges（特殊收入的手续费）',
 'TaxEffectOfUnusualItems（非常项目的税收影响）',
 'TaxProvision（税金计提）',
 'TaxRateForCalcs（Calcs计算用的税率）',
 'TotalExpenses（总费用）',
 'TotalOperatingIncomeAsReported（报告的总营业利润）',
 'TotalOtherFinanceCost（其他财务成本合计）',
 'TotalRevenue（总收入）',
 'TotalUnusualItems（非经常性项目总计）',
 'TotalUnusualItemsExcludingGoodwill（不包括商誉的非经常项目合计）',
 'WriteOff（冲销，核销）',
 
 'BeginningCashPosition（期初现金头寸）',
 'CapitalExpenditure（资本支出）',
 'CashDividendsPaid（现金股利支付）',
 'ChangeInCashSupplementalAsReported（报告的补充现金变更）',
 'ChangeInInventory（存货变化）',
 'ChangeInWorkingCapital（营运资本的变动额）',
 'DepreciationAndAmortization（折旧摊销）',
 'EndCashPosition（期末现金头寸）',
 'FreeCashFlow（自由现金流）',
 'InvestingCashFlow（投资现金流）',
 'NetOtherFinancingCharges（其他融资费用净额）',
 'NetOtherInvestingChanges（其他投资变动净额）',
 'OperatingCashFlow（营运现金流）',
 'OtherNonCashItems（其他非现金项目）'
 ]
"""

#==============================================================================
if __name__ == '__main__':
    fsdf=get_financial_statements2_yahoo('AAPL')
    account_entry='TotalAssets'
    
    fsdf1=fs_entry_begin(fsdf,account_entry='TotalAssets',suffix='_begin')

def fs_entry_begin_yahoo(fsdf,account_entry='TotalAssets',suffix='_begin'):
    """
    功能：以上年年报期末科目数值作为本期年报和季报的期初，仅适用于雅虎财报！
    """
    import pandas as pd
    import numpy as np
    #获取年报日期
    ar_mm_dd=pd.to_datetime(fsdf[fsdf['periodType']=='12M']['asOfDate'].values[0]).strftime("%Y-%m-%d")[-5:]
    
    fsdf['asOfDate_pd']=fsdf['asOfDate'].apply(lambda x: pd.to_datetime(x))
    fsdf['Date_y4']=fsdf['asOfDate'].apply(lambda x: pd.to_datetime(x).strftime("%Y"))
    fsdf['Date_begin_pd']=fsdf['Date_y4'].apply(lambda x: pd.to_datetime(str(int(x)-1)+'-'+ar_mm_dd))
    
    asOfDate_pd_list=list(fsdf['asOfDate_pd'])
    entry_begin=lambda x: fsdf[fsdf['asOfDate_pd']==x][account_entry].values[0] if x in asOfDate_pd_list else np.nan
    fsdf[account_entry+suffix]=fsdf['Date_begin_pd'].apply(entry_begin)
    
    fsdf.drop(['asOfDate_pd','Date_y4','Date_begin_pd'],axis=1,inplace=True)
    
    return fsdf

#==============================================================================
#==============================================================================
#==============================================================================
#==============================================================================
