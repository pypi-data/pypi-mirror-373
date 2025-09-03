# -*- coding: utf-8 -*-
"""
本模块功能：上市公司的财务报表分析，数据层
所属工具包：证券投资分析工具SIAT 
SIAT：Security Investment Analysis Tool
创建日期：2020年9月10日
最新修订日期：2020年9月14日
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
import pandas as pd
#==============================================================================
#本模块使用yahooquery插件
#==============================================================================
if __name__=='__main__':
    symbol='JD'
    symbol='INTL' 
    symbol='MSFT'
    symbol='600519.SS'
    symbol='00700.HK'
    
    symbol='601398.SS'
    symbol='601328.SS'
    
    fsdf=get_balance_sheet(symbol)

def get_balance_sheet(symbol):
    """
    功能：获取雅虎财经上一只股票所有的年度和季度资产负债表
    """
    print("  Searching for balance info of {}, please wait...".format(symbol))
    
    result,prefix,suffix=split_prefix_suffix(symbol)
    if result & (suffix=='HK'):
        if len(prefix)==5:
            symbol=symbol[1:]
    
    from yahooquery import Ticker
    stock = Ticker(symbol)    
    
    import time
    #获取年报
    try:
        stmta=stock.balance_sheet()  # Defaults to Annual
    except:
        print("  #Warning(get_balance_sheet): no annual info available for",symbol)
        return None
        
    if isinstance(stmta,dict):
            print("  #Warning(get_balance_sheet): Yahoo Finance currently unaccessable for",symbol)
            return None
        
    """
    #判断是否抓取到了数据
    import pandas as pd
    if not isinstance(stmta,pd.DataFrame):
        print("\n  #Error(get_balance_sheet): no annual info available for",symbol)
        return None
    """
    #获取季度报
    try:
        stmtq=stock.balance_sheet(frequency="q")
    except:
        print("  #Warning(get_balance_sheet): no quarterly info available for",symbol)
        return None
        
    if isinstance(stmtq,dict):
            print("  #Warning(get_balance_sheet): Yahoo Finance currently unaccessable for",symbol)
            return None
        
    """
    if (len(stmta)==0) and (len(stmtq)==0):
        print("  #Error(get_balance_sheet): no reports available for",symbol)
        return None
    """
    #合并年度和季度报表
    if not (stmta is None) and not (stmtq is None):
        stmt=pd.concat([stmta,stmtq])
    elif not (stmta is None):
        stmt=stmta
    elif not (stmtq is None):
        stmt=stmtq        
    else:
        print("  #Error(get_balance_sheet): no reports available for",symbol)
        return None    
    
    #字段缺失替代处理
    #流动（有息）债务
    if 'CurrentDebt' not in list(stmt):
        stmt['CurrentDebt']=0.0
    #流动负债（有息债务+应付）
    if 'CurrentLiabilities' not in list(stmt):
        stmt['CurrentLiabilities']=stmt['CurrentDebt']
    #总（有息）债务
    if 'TotalDebt' not in list(stmt):
        stmt['TotalDebt']=0.0
    #少数股东权益
    if 'MinorityInterest' not in list(stmt):
        if 'TotalEquityGrossMinorityInterest' in list(stmt):
            stmt['MinorityInterest']= \
                stmt['TotalEquityGrossMinorityInterest']-stmt['StockholdersEquity']
        elif 'TotalLiabilitiesNetMinorityInterest' in list(stmt):
            stmt['MinorityInterest']=stmt['TotalAssets']- \
                stmt['TotalLiabilitiesNetMinorityInterest']- \
                    stmt['StockholersEquity']
        else:
            stmt['MinorityInterest']=0.0
    #总负债
    if 'TotalLiabilities' not in list(stmt): 
        if 'TotalLiabilitiesNetMinorityInterest' in list(stmt):
            stmt['TotalLiabilities']=stmt['TotalLiabilitiesNetMinorityInterest']+ \
                stmt['MinorityInterest']
        else:
            stmt['TotalLiabilities']=stmt['TotalDebt']+stmt['MinorityInterest']
    #权益总额
    if 'TotalEquities' not in list(stmt):
        stmt['TotalEquities']=stmt['TotalEquityGrossMinorityInterest']- \
            stmt['MinorityInterest']    
    #存货
    if 'Inventory' not in list(stmt):
        stmt['Inventory']=0.0
        
    #流动资产
    if 'Receivables' not in list(stmt):
        stmt['Receivables']=0.0
    
    if 'CurrentAssets' not in list(stmt):
        stmt['CurrentAssets']=stmt['CashAndCashEquivalents']+ \
            stmt['Receivables']+stmt['Inventory']
    #应收账款
    if 'AccountsReceivable' not in list(stmt):
        stmt['AccountsReceivable']=stmt['Receivables']
    
    #总检查：总资产=总负债+总权益是否成立
    #stmt['TA-TL-TE']=stmt['TotalAssets']-stmt['TotalLiabilities']-stmt['TotalEquities']
    
    #排序
    stmt.sort_values(by=['asOfDate','periodType'],inplace=True)
    #去掉重复记录: 保留年报数据项多，去掉数据项少的季报
    stmt.drop_duplicates(subset=['asOfDate'],keep='first',inplace=True)

    #print(", done")
    
    return stmt    
    
if __name__ == '__main__':
    fs=get_balance_sheet('AAPL')
    fs_msft=get_balance_sheet('MSFT')
    fs_c=get_balance_sheet('C')
    fs_maotai=get_balance_sheet('600519.SS')

#==============================================================================
if __name__=='__main__':
    symbol='AAPL' 
    symbol='MST'
    
    fsdf=get_income_statements(symbol)

def get_income_statements(symbol):
    """
    功能：获取雅虎财经上一只股票所有的年度和季度利润表
    """
    print("  Searching for income info of",symbol,"\b, please wait...")
    
    result,prefix,suffix=split_prefix_suffix(symbol)
    if result & (suffix=='HK'):
        if len(prefix)==5:
            symbol=symbol[1:]    
    
    from yahooquery import Ticker
    stock = Ticker(symbol)    
    
    import time
    #获取年报
    try:
        stmta=stock.income_statement()  # Defaults to Annual
    except:
        print("  #Warning(get_income_statements): no annual info available for",symbol)
        return None

    if isinstance(stmta,dict):
        print("  #Warning(get_balance_sheet): Yahoo Finance currently unaccessable for",symbol)
        return None
        
    """
    #判断是否抓取到了数据
    import pandas as pd
    if not isinstance(stmta,pd.DataFrame):
        print("  #Error(get_income_statements): no annual info available for",symbol)
        return None
    """
    #获取季度报
    try:
        stmtq=stock.income_statement(frequency="q")
    except:
        print("  #Warning(get_income_statements): no quarterly info available for",symbol)
        return None
        
    if isinstance(stmtq,dict):
        print("  #Warning(get_balance_sheet): Yahoo Finance currently unaccessable for",symbol)
        return None
        
    """
    if (len(stmta)==0) and (len(stmtq)==0):
        print("  #Error(get_income_statements): no reports available for",symbol)
        return None
    """
    #合并年度和季度报表
    if not (stmta is None) and not (stmtq is None):
        stmt=pd.concat([stmta,stmtq])
    elif not (stmta is None):
        stmt=stmta
    elif not (stmtq is None):
        stmt=stmtq        
    else:
        print("  #Error(get_income_statements): no reports available for",symbol)
        return None 
    
    #排序
    stmt.sort_values(by=['asOfDate','periodType'],inplace=True)
    #去掉重复记录: 保留年报数据项多，去掉数据项少的季报
    stmt.drop_duplicates(subset=['asOfDate'],keep='first',inplace=True)
    
    #把periodType中的TTM改成3M
    stmt['periodType']=stmt['periodType'].apply(lambda x: '3M' if x=='TTM' else x)

    #字段缺失处理
    if 'InterestExpense' not in list(stmt):
        #import numpy as np
        #stmt['InterestExpense']=np.nan
        stmt['InterestExpense']=0
    
    # 服务型企业无此项
    if 'CostOfRevenue' not in list(stmt):
        stmt['CostOfRevenue']=0
        
    if 'OperatingExpense' not in list(stmt):
        stmt['OperatingExpense']=stmt['CostOfRevenue']
        
    # 服务型企业
    if 'OperatingIncome' not in list(stmt):
        stmt['OperatingIncome']=stmt['OperatingRevenue']-stmt['OperatingExpense']
    
    # 服务型企业
    if 'GrossProfit' not in list(stmt):
        stmt['GrossProfit']=stmt['PretaxIncome']

    
    #print(", done")
    return stmt    
    
if __name__ == '__main__':
    stmt=get_income_statements('AAPL')
    stmt_msft=get_income_statements('MSFT')
    stmt_c=get_income_statements('C')
    stmt_maotai=get_income_statements('600519.SS')

#==============================================================================
if __name__=='__main__':
    symbol='AAPL' 
    
    fsdf=get_cashflow_statements(symbol)

def get_cashflow_statements(symbol):
    """
    功能：获取雅虎财经上一只股票所有的年度和季度现金流量表
    """
    print("  Searching for cashflow info of",symbol,"\b, please wait...")
    
    result,prefix,suffix=split_prefix_suffix(symbol)
    if result & (suffix=='HK'):
        if len(prefix)==5:
            symbol=symbol[1:]    
    
    from yahooquery import Ticker
    stock = Ticker(symbol)    
    
    import time
    #获取年报
    try:
        stmta=stock.cash_flow()  # Defaults to Annual
    except:
        print("  #Warning(get_cashflow_statements): no annual info available for",symbol)
        return None

    if isinstance(stmta,dict):
        print("  #Warning(get_balance_sheet): Yahoo Finance currently unaccessable for",symbol)
        return None    
        
    """
    #判断是否抓取到了数据
    import pandas as pd
    if not isinstance(stmta,pd.DataFrame):
        print("\n  #Error(get_cashflow_statements): no annual info available for",symbol)
        return None
    """
    #获取季度报
    try:
        stmtq=stock.cash_flow(frequency="q")
    except:
        print("  #Warning(get_cashflow_statements): no quarterly info available for",symbol)
        return None
        
    if isinstance(stmtq,dict):
        print("  #Warning(get_balance_sheet): Yahoo Finance currently unaccessable for",symbol)
        return None
        
    """
    if (len(stmta)==0) and (len(stmtq)==0):
        print("  #Error(get_cashflow_statements): no reports available for",symbol)
        return None
    """
    #合并年度和季度报表
    if not (stmta is None) and not (stmtq is None):
        stmt=pd.concat([stmta,stmtq])
    elif not (stmta is None):
        stmt=stmta
    elif not (stmtq is None):
        stmt=stmtq        
    else:
        print("  #Error(get_cashflow_statements): no reports available for",symbol)
        return None 
    
    #排序
    stmt.sort_values(by=['asOfDate','periodType'],inplace=True)
    #去掉重复记录: 保留年报数据项多，去掉数据项少的季报
    stmt.drop_duplicates(subset=['asOfDate'],keep='first',inplace=True)
    
    #把periodType中的TTM改成3M
    stmt['periodType']=stmt['periodType'].apply(lambda x: '3M' if x=='TTM' else x)

    #字段缺失处理
    if 'CashDividendsPaid' not in list(stmt):
        #import numpy as np
        #stmt['CashDividendsPaid']=np.nan
        stmt['CashDividendsPaid']=0

    #print(", done")
    return stmt    
    
if __name__ == '__main__':
    stmt=get_cashflow_statements('AAPL')
    stmt_msft=get_cashflow_statements('MSFT')
    stmt_c=get_cashflow_statements('C')
    stmt_maotai=get_cashflow_statements('600519.SS')

#==============================================================================
if __name__=='__main__':
    ticker='AAPL' 
    ticker='00700.HK' 
    
    fsdf=get_financial_statements(ticker)

def get_financial_statements(ticker):
    """
    功能：获取雅虎财经上一只股票所有的年度和季度财务报表
    """
    
    # 变换港股代码5位-->4位
    result,prefix,suffix=split_prefix_suffix(ticker)
    if result & (suffix=='HK'):
        if len(prefix)==5:
            ticker=ticker[1:]
    
    print("  Searching for financial statements of",ticker,"\b, please wait")
    #获取资产负债表
    try:
        fbs = get_balance_sheet(ticker)
    except:
        print("  #Error(get_financial_statements): balance sheet not available for",ticker)
        return None
    if fbs is None:
        print("  #Error(get_financial_statements): financial statements not available for",ticker)
        return None
    
    #获取利润表
    try:
        fis = get_income_statements(ticker)
    except:
        print("  #Error(get_financial_statements): income info not available for",ticker)
        return None
    if fis is None:
        print("  #Error(get_financial_statements): financial statements not available for",ticker)
        return None
    
    #获取现金流量表
    try:
        fcf = get_cashflow_statements(ticker)
    except:
        print("  #Error(get_financial_statements): cash flow info not available for",ticker)
        return None
    if fcf is None:
        print("  #Error(get_financial_statements): financial statements not available for",ticker)
        return None
    
    #合并1：资产负债表+利润表
    import pandas as pd
    #fbs_fis=pd.merge(fbs,fis,on=['asOfDate','periodType'])
    fbs_fis=pd.merge(fbs,fis,how='left',on=['asOfDate'],suffixes=('', '_y'))
    
    #合并2：+现金流量表
    #fbs_fis_fcf=pd.merge(fbs_fis,fcf,on=['asOfDate','periodType','NetIncome'])
    fbs_fis_fcf=pd.merge(fbs_fis,fcf,how='left',on=['asOfDate'],suffixes=('', '_y'))
    
    fbs_fis_fcf['ticker']=ticker
    #将所有的nan替换为0
    #fbs_fis_fcf.fillna(0,inplace=True)

    print("  ...Successfully retrieved financial statements of",ticker,"\b!")    
    return fbs_fis_fcf    
    
if __name__ == '__main__':
    fs=get_financial_statements('AAPL')
    fs_aapl=get_financial_statements('AAPL')
    fs_msft=get_financial_statements('MSFT')
    fs_c=get_financial_statements('C')
    fs_maotai=get_financial_statements('600519.SS')

"""
最终获得的表结构：
['asOfDate',
 'periodType',
 
 'AccountsPayable(应付账款)',
 'AccountsReceivable(应收账款)',
 'AccumulatedDepreciation（累计折旧）',
 'AdditionalPaidInCapital（资本公积，资本溢价，附加资本；paid-in capital：实收资本；缴入资本）',
 'AllowanceForDoubtfulAccountsReceivable（备抵应收呆帐）',
 'AvailableForSaleSecurities（可供出售金融资产；trading securities: 交易性金融资产）',
 'BuildingsAndImprovements（建筑物改良）',
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
 'InvestmentinFinancialAssets（金融资产投资？）',
 'LandAndImprovements（土地改良）',
 'MachineryFurnitureEquipment（机械家具设备？）',
 'MinorityInterest（少数股东损益？）',
 'NetPPE（固定资产净值）',
 'NetTangibleAssets（有形资产净值）',
 'NonCurrentDeferredAssets（非流动递延资产）',
 'NonCurrentDeferredTaxesAssets（非流动递延税项资产？）',
 'NonCurrentDeferredTaxesLiabilities（非流动递延税金负债？）',
 'OrdinarySharesNumber（普通股数量？）',
 'OtherCurrentAssets（其他流动资产）',
 'OtherCurrentLiabilities（其他流动负债）',
 'OtherEquityInterest（其他股权）',
 'OtherIntangibleAssets（其他有形资产）',
 'OtherNonCurrentAssets（其他非流动资产）',
 'OtherPayable（其它应付款）',
 'OtherProperties（？）',
 'OtherReceivables（其他应收款）',
 'Payables（应付款项）',
 'PrepaidAssets（预付资产；预付费用）',
 'Properties（财产？）',
 'RawMaterials（原材料）',
 'RetainedEarnings（留存收益）',
 'ShareIssued（股票发行）',
 'StockholdersEquity（股东权益）',
 'TangibleBookValue（有形资产账面价值）',
 'TotalAssets（总资产）',
 'TotalCapitalization（资本总额？）',
 'TotalEquityGrossMinorityInterest（少数股东权益总额）',
 'TotalLiabilitiesNetMinorityInterest（？）',
 'TotalNonCurrentAssets（非流动资产总额）',
 'TotalNonCurrentLiabilitiesNetMinorityInterest（？）',
 'TotalTaxPayable（应缴税款总额）',
 'TradeandOtherPayablesNonCurrent（？）',
 'WorkInProcess（在制品）',
 'WorkingCapital（营运资本）',
 'Amortization（摊销）',
 
 'BasicAverageShares（未稀释的平均股数？）',
 'BasicEPS（ 基本每股收益，指属于普通股股东的当期净利润，除以发行在外普通股的加权平均数，可按存在月数加权）',
 'CostOfRevenue（主营业务成本，营收成本）',
 'DepreciationAndAmortizationInIncomeStatement（损益表中的折旧和摊销）',
 'DepreciationIncomeStatement（损益表中的折旧）',
 'DilutedAverageShares（稀释后平均股数？）',
 'DilutedEPS（考虑了可转换债券和股票期权可能行权对于流通在外股数的影响）',
 'EBIT（息税前利润）',
 'EBITDA（未计利息、税项、折旧及摊销前的利润）',
 'GeneralAndAdministrativeExpense（一般管理费用）',
 'GrossProfit（营业毛利）',
 'ImpairmentOfCapitalAssets（资本资产减值）',
 'InterestExpense（利息费用）',
 'InterestExpenseNonOperating（非经营性利息费用）',
 'InterestIncome（利息收益）',
 'InterestIncomeNonOperating（非经营性利息收入）',
 'MinorityInterests（少数股东权益）',
 'NetIncome（净利润）',
 'NetIncomeCommonStockholders（归属于普通股股东的净利润，用于计算EPS和PE）',
 'NetIncomeContinuousOperations（扣非后净利润）',
 'NetIncomeFromContinuingAndDiscontinuedOperation（来自持续经营和停止经营业务的净收入）',
 'NetIncomeFromContinuingOperationNetMinorityInterest（不归属少数股东的扣非后净利润？）',
 'NetIncomeIncludingNoncontrollingInterests（包括非控股权的净收入？）',
 'NetInterestIncome（净利息收入）',
 'NetNonOperatingInterestIncomeExpense（？）',
 'NormalizedEBITDA（调整后EBITDA？）',
 'NormalizedIncome（调整后利润？）',
 'OperatingExpense（营业费用）',
 'OperatingIncome（营业利润）',
 'OperatingRevenue（营业收入）',
 'OtherNonOperatingIncomeExpenses（其他营业外收入支出？）',
 'OtherOperatingExpenses（其它营业费用）',
 'OtherSpecialCharges（其他特殊费用）',
 'OtherunderPreferredStockDividend（优先股股利下的其他项目）',
 'PretaxIncome（税前利润）',
 'ReconciledCostOfRevenue（对账后的经营收入成本？）',
 'ReconciledDepreciation（对账后的折旧）',
 'RentAndLandingFees（租金及土地费用？）',
 'RentExpenseSupplemental（补充租金费用？）',
 'ResearchAndDevelopment（研发费用？）',
 'SellingAndMarketingExpense（销售和市场营销费用）',
 'SellingGeneralAndAdministration（销售及一般管理费用）',
 'SpecialIncomeCharges（特殊的收入费用？）',
 'TaxEffectOfUnusualItems（特殊项目的税收效应？）',
 'TaxProvision（税金？）',
 'TaxRateForCalcs（计算用的税率）',
 'TotalExpenses（总费用）',
 'TotalOperatingIncomeAsReported（报告的总营业利润）',
 'TotalOtherFinanceCost（其他财务成本合计）',
 'TotalRevenue（总收入）',
 'TotalUnusualItems（非经常性项目总计）',
 'TotalUnusualItemsExcludingGoodwill（不包括商誉的非经常项目合计）',
 'WriteOff（冲销？）',
 
 'BeginningCashPosition（期初现金头寸）',
 'CapitalExpenditure（资本支出）',
 'CashDividendsPaid（现金股利支付）',
 'ChangeInCashSupplementalAsReported（现金补充变更报告？）',
 'ChangeInInventory（存货变化）',
 'ChangeInWorkingCapital（营运资本的变动额）',
 'DepreciationAndAmortization（折旧摊销）',
 'EndCashPosition（期末现金头寸）',
 'FreeCashFlow（自有现金流）',
 'InvestingCashFlow（投资现金流）',
 'NetOtherFinancingCharges（其他融资费用净额）',
 'NetOtherInvestingChanges（其他投资变动净额）',
 'OperatingCashFlow（营运现金流）',
 'OtherNonCashItems（其他非现金项目）'
 ]
"""

#==============================================================================
if __name__ == '__main__':
    fsdf=get_financial_statements('601398.SS')
    account_entry='TotalAssets'
    
    fsdf1=fs_entry_begin(fsdf,account_entry='TotalAssets',suffix='_begin')

def fs_entry_begin(fsdf,account_entry='TotalAssets',suffix='_begin'):
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
