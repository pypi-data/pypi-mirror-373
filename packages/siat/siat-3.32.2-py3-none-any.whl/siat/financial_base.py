# -*- coding: utf-8 -*-
"""
本模块功能：上市公司的财务报表分析，数据层
所属工具包：证券投资分析工具SIAT 
SIAT：Security Investment Analysis Tool
创建日期：2020年9月1日
最新修订日期：2020年9月8日
作者：王德宏 (WANG Dehong, Peter)
作者单位：北京外国语大学国际商学院
版权所有：王德宏
用途限制：仅限研究与教学使用，不可商用！商用需要额外授权。
特别声明：作者不对使用本工具进行证券投资导致的任何损益负责！

注释：容易出现无规律的抓取失败，需要多次重复才能成功。
本部分功能作为备胎使用，当yfinance和yahooquery的财务报表功能失效时。
"""

#==============================================================================
#关闭所有警告
import warnings; warnings.filterwarnings('ignore')
from siat.common import *
from siat.translate import *
from siat.security_prices import *
from siat.security_price2 import *
#==============================================================================
#本模块直接使用爬虫抓取雅虎财经
#==============================================================================
class YahooFin():
    
    BASE_URL = 'https://query1.finance.yahoo.com/v10/finance/quoteSummary/'

    def __init__(self, ticker):
      """Initiates the ticker
          Args: ticker (str): Stock-ticker Ex. 'AAPL'
      """
      self.ticker = ticker

    def make_request(self, url):
        """Makes a GET request"""
        import requests
        headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }        
        return requests.get(url,headers=headers)

    def get_data(self):
      """Returns a json object from a GET request"""
      try:
          return self.make_request(self.url).json()
      except KeyError as e:
            print("#Error(get_data):",e)
        
    def data(self):
      """Returns query result from json object"""
      data_temp = self.get_data()
      try:
            return data_temp.get('quoteSummary').get("result")
      except KeyError as e:
            print("Something went wrong:",e)

    def convert_timestamp(self, raw):
      """Converts UNIX-timestamp to YYYY-MM-DD"""
      from datetime import datetime
      return datetime.utcfromtimestamp(raw).strftime('%Y-%m-%d')

    def extract_raw(func):
      """Decorator to remove keys from from json data 
      that is retreived from the yahoo-module
      """
      def wrapper_extract_raw(self, *args, **kwargs):
        sheet = func(self)
        for items in sheet:
            for key, value in items.items():
                if type(value) == dict and 'fmt' in value:
                    del value['fmt']
                if type(value) == dict and 'longFmt' in value:
                    del value['longFmt']
        return sheet
      return wrapper_extract_raw

    def create_dict(self):
      """Creates a dict from extracted data"""
      balance_sheet = []
      temp_data = self._dict
      for d in temp_data:
            temp_dict = {}
            for key, value in d.items():
                if type(value) == dict and 'raw' in value:
                    v = value['raw']
                    temp_dict[key] = v
            balance_sheet.append(temp_dict)
      return balance_sheet


    def to_df(self):
      """Creates a pandas Dataframe from dict"""
      import pandas as pd
      self._df = pd.DataFrame.from_dict(self.create_dict())
      for index, row in self._df.iterrows():
            self._df.loc[index, 'endDate'] = self.convert_timestamp(self._df.at[index, 'endDate'])
      self._df = self._df.iloc[::-1]
      return self._df

#==============================================================================
class BalanceSheetQ(YahooFin):

  def __init__(self, ticker):
    super().__init__(ticker)
    self._module = 'balanceSheetHistoryQuarterly'
    self._url = (f'https://query1.finance.yahoo.com/v10/finance/quoteSummary/'
                    f'{self.ticker}?'
                    f'modules={self.module}')
    self._dict = self._balance_sheet()
    self._df = None

  @property
  def module(self):
      return self._module

  @property
  def url(self):
      return self._url

  @property
  def df(self):
      return self._df

  @YahooFin.extract_raw
  def _balance_sheet(self):
    """Returns a balance sheet statement"""
    data = self.data()
    query =  data[0]
    balance_sheet_qty = query['balanceSheetHistoryQuarterly']
    balance_sheet_statements = balance_sheet_qty['balanceSheetStatements']
    return balance_sheet_statements

#==============================================================================
def get_bsQ(ticker):
    """
    功能： 获取最近4个季度资产负债表
    注意：数字单位为K
    """
    try:
        bsdata = BalanceSheetQ(ticker)
    except:
        bsdata = BalanceSheetQ(ticker)
    
    bsdf=bsdata.to_df()
    bsdf['ticker']=ticker
    bsdf['date']=bsdf['endDate']
    bsdf.set_index(['date'],inplace=True)
    return bsdf

if __name__ == '__main__':
    ticker='AAPL'
    bsq = get_bsQ(ticker)

#==============================================================================
class BalanceSheetA(YahooFin):

  def __init__(self, ticker):
    super().__init__(ticker)
    self._module = 'balanceSheetHistory'
    self._url = (f'https://query1.finance.yahoo.com/v10/finance/quoteSummary/'
                    f'{self.ticker}?'
                    f'modules={self.module}')
    self._dict = self._balance_sheet()
    self._df = None

  @property
  def module(self):
      return self._module

  @property
  def url(self):
      return self._url

  @property
  def df(self):
      return self._df

  @YahooFin.extract_raw
  def _balance_sheet(self):
    """Returns a balance sheet statement"""
    data = self.data()
    
    #print(data)
    query =  data[0]
    balance_sheet_qty = query['balanceSheetHistory']
    balance_sheet_statements = balance_sheet_qty['balanceSheetStatements']
    return balance_sheet_statements

#==============================================================================
def get_bsA(ticker):
    """
    功能： 获取最近4个年度资产负债表
    注意：数字单位为K
    """
    try:
        bsdata = BalanceSheetA(ticker)
    except:
        bsdata = BalanceSheetA(ticker)
    
    bsdf=bsdata.to_df()
    bsdf['ticker']=ticker
    bsdf['date']=bsdf['endDate']
    bsdf.set_index(['date'],inplace=True)
    return bsdf

if __name__ == '__main__':
    ticker='AAPL'
    bsa = get_bsA(ticker)

#==============================================================================
class IncomeStatementQ(YahooFin):

  def __init__(self, ticker):
        super().__init__(ticker)
        self._module = 'incomeStatementHistoryQuarterly'
        self._url = (f'https://query1.finance.yahoo.com/v10/finance/quoteSummary/'
                    f'{self.ticker}?'
                    f'modules={self.module}')
        self._dict = self._income_statement()
        self._df = None

  @property
  def module(self):
      return self._module

  @property
  def url(self):
      return self._url

  @property
  def df(self):
      return self._df

  @YahooFin.extract_raw
  def _income_statement(self):
    """Returns a income statement"""
    data = self.data()
    query =  data[0]
    income_statement_qty = query['incomeStatementHistoryQuarterly']
    income_statement_statements = income_statement_qty['incomeStatementHistory']
    return income_statement_statements


if __name__ == '__main__':
    isdata = IncomeStatementQ('AAPL')
    isdf=isdata.to_df()
    print(isdf)
    
#==============================================================================
def get_isQ(ticker):
    """
    功能： 获取最近4个季度利润表
    注意：数字单位为K
    """
    try:
        isdata = IncomeStatementQ(ticker)
    except:
        isdata = IncomeStatementQ(ticker)
    
    isdf=isdata.to_df()
    
    isdf['ticker']=ticker
    isdf['date']=isdf['endDate']
    isdf.set_index(['date'],inplace=True)
    return isdf

if __name__ == '__main__':
    ticker='AAPL'
    isq = getQ(ticker)

#==============================================================================  
class IncomeStatementA(YahooFin):

  def __init__(self, ticker):
        super().__init__(ticker)
        self._module = 'incomeStatementHistory'
        self._url = (f'https://query1.finance.yahoo.com/v10/finance/quoteSummary/'
                    f'{self.ticker}?'
                    f'modules={self.module}')
        self._dict = self._income_statement()
        self._df = None

  @property
  def module(self):
      return self._module

  @property
  def url(self):
      return self._url

  @property
  def df(self):
      return self._df

  @YahooFin.extract_raw
  def _income_statement(self):
    """Returns a income statement"""
    data = self.data()
    #print(data)
    query =  data[0]
    income_statement_qty = query['incomeStatementHistory']
    income_statement_statements = income_statement_qty['incomeStatementHistory']
    return income_statement_statements


if __name__ == '__main__':
    isdata = IncomeStatementA('AAPL')
    isdf=isdata.to_df()
    print(isdf)

#==============================================================================
def get_isA(ticker):
    """
    功能： 获取最近4个年度利润表
    注意：数字单位为K
    """
    try:
        isdata = IncomeStatementA(ticker)
    except:
        isdata = IncomeStatementA(ticker)
    
    isdf=isdata.to_df()
    
    isdf['ticker']=ticker
    isdf['date']=isdf['endDate']
    isdf.set_index(['date'],inplace=True)
    return isdf

if __name__ == '__main__':
    ticker='AAPL'
    isa = get_isA(ticker)

#==============================================================================
class CashFlowQ(YahooFin):

  def __init__(self, ticker):
        super().__init__(ticker)
        self._module = 'cashflowStatementHistoryQuarterly'
        self._url = (f'https://query1.finance.yahoo.com/v10/finance/quoteSummary/'
                    f'{self.ticker}?'
                    f'modules={self.module}')
        self._dict = self._cash_flow()
        self._df = None

  @property
  def module(self):
      return self._module

  @property
  def url(self):
      return self._url

  @property
  def df(self):
      return self._df

  @YahooFin.extract_raw
  def _cash_flow(self):
    """Returns a cash flow statement"""
    data = self.data()
    query =  data[0]
    #print(data)
    cash_flow_qty = query['cashflowStatementHistoryQuarterly']
    #print(cash_flow_qty)
    cash_flow_statements = cash_flow_qty['cashflowStatements']
    return cash_flow_statements


if __name__ == '__main__':
    cfdata = CashFlowQ('AAPL')
    cfdf=cfdata.to_df()
    print(cfdf)

#==============================================================================
def get_cfQ(ticker):
    """
    功能： 获取最近4个季度现金流量表
    注意：数字单位为K
    """
    try:
        cfdata = CashFlowQ(ticker)
    except:
        cfdata = CashFlowQ(ticker)
    
    cfdf=cfdata.to_df()
    cfdf['ticker']=ticker
    cfdf['date']=cfdf['endDate']
    cfdf.set_index(['date'],inplace=True)
    return cfdf

if __name__ == '__main__':
    ticker='AAPL'
    cfq = get_cfQ(ticker)


#==============================================================================
class CashFlowA(YahooFin):

  def __init__(self, ticker):
        super().__init__(ticker)
        self._module = 'cashflowStatementHistory'
        self._url = (f'https://query1.finance.yahoo.com/v10/finance/quoteSummary/'
                    f'{self.ticker}?'
                    f'modules={self.module}')
        self._dict = self._cash_flow()
        self._df = None

  @property
  def module(self):
      return self._module

  @property
  def url(self):
      return self._url

  @property
  def df(self):
      return self._df

  @YahooFin.extract_raw
  def _cash_flow(self):
    """Returns a cash flow statement"""
    data=self.data()
    #print(data)
    #print(data)
    query=data[0]
    #print(query)
    
    cash_flow_qty = query['cashflowStatementHistory']
    #print(cash_flow_qty)
    
    cash_flow_statements = cash_flow_qty['cashflowStatements']
    #print(cash_flow_qty)
    
    return cash_flow_statements


if __name__ == '__main__':
    cfdata = CashFlowA('AAPL')
    cfdf=cfdata.to_df()
    print(cfdf)

    
#==============================================================================
def get_cfA(ticker):
    """
    功能： 获取最近4个年度现金流量表
    注意：数字单位为K
    """
    try:
        cfdata = CashFlowA(ticker)
    except:
        try:
            cfdata = CashFlowA(ticker)
        except:
            cfdata = CashFlowA(ticker)
    
    cfdf=cfdata.to_df()
    cfdf['ticker']=ticker
    cfdf['date']=cfdf['endDate']
    cfdf.set_index(['date'],inplace=True)
    return cfdf

if __name__ == '__main__':
    ticker='AAPL'
    cfa = get_cfA(ticker)

#==============================================================================
def get_balance_sheet(ticker):
    """
    功能：获取雅虎财经上一只股票所有的年度和季度资产负债表
    """
    #获取年报
    try:
        fsa = get_bsA(ticker)
    except:
        print("#Error(get_balance_sheet): no annual info available for",ticker)
        return None
    fsa['reportType']="Annual"
    colsa=list(fsa)
    
    #获取季度报
    try:
        fsq = get_bsQ(ticker)
    except:
        print("#Error(get_balance_sheet): no quarterly info available for",ticker)
        return None
    fsq['reportType']="Quarterly"    
    colsq=list(fsq)

    #两个列表中的共同部分
    cols= [x for x in colsa if x in colsq]   #两个列表中都存在
    colsdiff=[y for y in (colsa + colsq) if y not in cols] #两个列表中的不同元素
    
    #合并年度和季度报表
    import pandas as pd
    fs=pd.concat([fsa[cols],fsq[cols]])
    #排序
    fs.sort_values(by=['endDate','reportType'],inplace=True)
    #去掉重复记录
    fs.drop_duplicates(subset=['endDate'],keep='first',inplace=True)
    
    return fs    
    
if __name__ == '__main__':
    ticker='AAPL'  
    fs=get_balance_sheet('AAPL')
    fs_aapl=get_balance_sheet('AAPL')
    fs_msft=get_balance_sheet('MSFT')
    fs_c=get_balance_sheet('C')

#==============================================================================
def get_income_statements(ticker):
    """
    功能：获取雅虎财经上一只股票所有的年度和季度利润表
    """
    #获取年报
    try:
        fsa = get_isA(ticker)
    except:
        print("#Error(get_income_statements): no annual info available for",ticker)
        return None
    fsa['reportType']="Annual"
    colsa=list(fsa)
    
    #获取季度报
    try:
        fsq = get_isQ(ticker)
    except:
        print("#Error(get_income_statements): no quarterly info available for",ticker)
        return None
    fsq['reportType']="Quarterly"    
    colsq=list(fsq)

    #两个列表中的共同部分
    cols= [x for x in colsa if x in colsq]   #两个列表中都存在
    colsdiff=[y for y in (colsa + colsq) if y not in cols] #两个列表中的不同元素
    
    #合并年度和季度报表
    import pandas as pd
    fs=pd.concat([fsa[cols],fsq[cols]])
    #排序
    fs.sort_values(by=['endDate','reportType'],inplace=True)
    #去掉重复记录
    fs.drop_duplicates(subset=['endDate'],keep='first',inplace=True)
    
    return fs    
    
if __name__ == '__main__':
    ticker='AAPL'  
    fs=get_income_statements('AAPL')
    fs_aapl=get_income_statements('AAPL')
    fs_msft=get_income_statements('MSFT')
    fs_c=get_income_statements('C')

#==============================================================================
def get_cashflow_statements(ticker):
    """
    功能：获取雅虎财经上一只股票所有的年度和季度现金流量表
    """
    #获取年报
    try:
        fsa = get_cfA(ticker)
    except:
        print("#Error(get_cashflow_statements): no annual info available for",ticker)
        return None
    fsa['reportType']="Annual"
    colsa=list(fsa)
    
    #获取季度报
    try:
        fsq = get_cfQ(ticker)
    except:
        print("#Error(get_cashflow_statements): no quarterly info available for",ticker)
        return None
    fsq['reportType']="Quarterly"    
    colsq=list(fsq)

    #两个列表中的共同部分
    cols= [x for x in colsa if x in colsq]   #两个列表中都存在
    colsdiff=[y for y in (colsa + colsq) if y not in cols] #两个列表中的不同元素
    
    #合并年度和季度报表
    import pandas as pd
    fs=pd.concat([fsa[cols],fsq[cols]])
    #排序
    fs.sort_values(by=['endDate','reportType'],inplace=True)
    #去掉重复记录
    fs.drop_duplicates(subset=['endDate'],keep='first',inplace=True)
    
    return fs    
    
if __name__ == '__main__':
    ticker='AAPL'  
    fs=get_cashflow_statements('AAPL')
    fs_aapl=get_cashflow_statements('AAPL')
    fs_msft=get_cashflow_statements('MSFT')
    fs_c=get_cashflow_statements('C')

#==============================================================================
def get_financial_statements(ticker):
    """
    功能：获取雅虎财经上一只股票所有的年度和季度财务报表
    """
    print("...Searching for financial info of",ticker,"\b, please wait...")
    #获取资产负债表
    try:
        fbs = get_balance_sheet(ticker)
    except:
        import time; time.sleep(3)
        try:
            fbs = get_balance_sheet(ticker)
        except:
            import time; time.sleep(5)
            try:
                fbs = get_balance_sheet(ticker)
            except:
                print("#Error(get_financial_statements): balance sheet info not available for",ticker)
                return None
    if fbs is None:
        print("#Error(get_financial_statements): balance sheet info not available for",ticker)
        return None
    
    #获取利润表
    try:
        fis = get_income_statements(ticker)
    except:
        import time; time.sleep(3)
        try:
            fis = get_income_statements(ticker)
        except:
            import time; time.sleep(5)
            try:
                fis = get_income_statements(ticker)
            except:
                print("#Error(get_financial_statements): income info not available for",ticker)
                return None
    if fis is None:
        print("#Error(get_financial_statements): income info not available for",ticker)
        return None
    
    #获取现金流量表
    try:
        fcf = get_cashflow_statements(ticker)
    except:
        import time; time.sleep(3)
        try:
            fcf = get_cashflow_statements(ticker)
        except:
            import time; time.sleep(5)
            try:
                fcf = get_cashflow_statements(ticker)
            except:
                print("#Error(get_financial_statements): cash flow info not available for",ticker)
                return None
    if fcf is None:
        print("#Error(get_financial_statements): cash flow info not available for",ticker)
        return None
    
    #合并1：资产负债表+利润表
    cols= [x for x in fis if x not in fbs]   #不在第2个列表中在第1个列表
    import pandas as pd
    fbs_fis=pd.merge(fbs,fis[cols+['endDate']],on='endDate')
    #合并2：+现金流量表
    cols= [x for x in fcf if x not in fbs_fis]   #不在第1个列表中只在第2个列表
    fbs_fis_fcf=pd.merge(fbs_fis,fcf[cols+['endDate']],on='endDate')
    
    #建立索引
    fbs_fis_fcf['date']=fbs_fis_fcf['endDate']
    bic=fbs_fis_fcf.set_index('date')
    
    #某些金融企业缺乏一些字段，特殊处理：
    cols=list(bic)
    cols_special=['inventory','totalCashFromOperatingActivities','interestExpense','dividendsPaid']
    for e in cols_special:
        if not (e in cols):
            bic[e]=0
    
    return bic    
    
if __name__ == '__main__':
    ticker='AAPL'  
    fs=get_financial_statements('AAPL')
    fs_aapl=get_financial_statements('AAPL')
    fs_msft=get_financial_statements('MSFT')
    fs_c=get_financial_statements('C')

"""
最终获得的bic表结构：
['cash',
 'shortTermInvestments',
 'netReceivables',
 'inventory',
 'otherCurrentAssets',
 'totalCurrentAssets',
 'longTermInvestments',
 'propertyPlantEquipment',
 'otherAssets',
 'totalAssets',
 'accountsPayable',
 'shortLongTermDebt',
 'otherCurrentLiab',
 'longTermDebt',
 'otherLiab',
 'totalCurrentLiabilities',
 'totalLiab',
 'commonStock',
 'retainedEarnings',
 'treasuryStock',
 'otherStockholderEquity',
 'totalStockholderEquity',
 'netTangibleAssets',
 
 'ticker',
 'reportType',
 
 'totalRevenue',
 'costOfRevenue',
 'grossProfit',
 'researchDevelopment',
 'sellingGeneralAdministrative',
 'totalOperatingExpenses',
 'operatingIncome',
 'totalOtherIncomeExpenseNet',
 'ebit',
 'interestExpense',
 'incomeBeforeTax',
 'incomeTaxExpense',
 'netIncomeFromContinuingOps',
 'netIncome',
 'netIncomeApplicableToCommonShares',
 
 'depreciation',
 'changeToNetincome',
 'changeToAccountReceivables',
 'changeToLiabilities',
 'changeToInventory',
 'changeToOperatingActivities',
 'totalCashFromOperatingActivities',
 'capitalExpenditures',
 'investments',
 'otherCashflowsFromInvestingActivities',
 'totalCashflowsFromInvestingActivities',
 'dividendsPaid',
 'netBorrowings',
 'otherCashflowsFromFinancingActivities',
 'totalCashFromFinancingActivities',
 'changeInCash',
 
 'repurchaseOfStock',
 'issuanceOfStock']
"""

#==============================================================================
def get_EPS(fsdf):
    """
    功能：抓取股票的EPS，并计算流通股数
    """
    ticker=list(fsdf['ticker'])[0]
    print("...Searching for EPS info of",ticker,"\b, please wait...")    
    
    #局限：目前取不到非美股的EPS信息！
    from yahoo_earnings_calendar import YahooEarningsCalendar
    # 实例化装饰器
    yec = YahooEarningsCalendar()
    earnings = yec.get_earnings_of(ticker)
    
    import pandas as pd
    earnings_df = pd.DataFrame.from_records(earnings) 
    if (earnings_df is None) or (len(earnings_df)==0):
        print("#Error(get_EPS): no EPS info available for",ticker)
        return False,fsdf
    
    earnings_df['datedt']=pd.to_datetime(earnings_df.startdatetime)
    datecvt=lambda x: str(x)[0:10]
    earnings_df['publish_date']=earnings_df['datedt'].apply(datecvt)
    eps=earnings_df[['ticker','epsactual','publish_date']]
    eps.dropna(inplace=True)
    if (eps is None) or (len(eps)==0):
        print("#Error(get_EPS): no EPS info available for",ticker)
        return False,fsdf
    
    eps.drop_duplicates(['publish_date'],keep='first',inplace=True)
    eps.sort_values('publish_date',inplace=True)

    epsdf=pd.DataFrame(columns=('endDate','publishDate','EPS'))

    edatelist=list(fsdf['endDate'])
    for d in edatelist:
        eps_sub=eps[eps['publish_date']>d]
        pdate=list(eps_sub['publish_date'])[0]
        epsactual=list(eps_sub['epsactual'])[0]

        #记录股价
        row=pd.Series({'endDate':d,'publishDate':pdate,'EPS':epsactual})
        try:
            epsdf=epsdf.append(row,ignore_index=True)
        except:
            epsdf=epsdf._append(row,ignore_index=True)

    fsdf1=pd.merge(fsdf,epsdf,on='endDate')
    fsdf1['outstandingStock']=fsdf1['netIncomeApplicableToCommonShares']/fsdf1['EPS']

    return True,fsdf1

if __name__ == '__main__':
    fsdf=get_financial_statements('AAPL')  
    result,fsdf1=get_EPS(fsdf)
    fsdf=get_financial_statements('0700.HK')  
    result,fsdf1=get_EPS(fsdf)

#==============================================================================
def get_PE(fsdf):
    """
    功能：计算PE
    """
    #获得各个报表的日期范围，适当扩大以规避非交易日
    start=min(list(fsdf['endDate']))
    fromdate=date_adjust(start,adjust=-30)
    end=max(list(fsdf['endDate']))
    todate=date_adjust(end,adjust=30)

    #获取股价
    ticker=list(fsdf['ticker'])[0]
    prices=get_price(ticker, fromdate, todate)
    prices['datedt']=prices.index.date
    datecvt=lambda x: str(x)[0:10]
    prices['Date']=prices['datedt'].apply(datecvt)

    #报表日期列表
    datelist_fs=list(fsdf['endDate'])
    #价格日期列表    
    datelist_price=list(prices['Date'])
    date_price_min=min(datelist_price)
    date_price_max=max(datelist_price)
    
    #股价列表
    pricelist=list(prices['Close'])
    
    import pandas as pd
    pricedf=pd.DataFrame(columns=('endDate','actualDate','Price'))
    for d in datelist_fs:
        found=False
        d1=d
        if d in datelist_price:
            found=True
            pos=datelist_price.index(d)
            p=pricelist[pos]
        else:
            while (d1 >= date_price_min) and not found:
                d1=date_adjust(d1,adjust=-1)
                if d1 in datelist_price:
                    found=True
                    pos=datelist_price.index(d1)
                    p=pricelist[pos]
            while (d1 <= date_price_max) and not found:
                d1=date_adjust(d1,adjust=1)
                if d1 in datelist_price:
                    found=True
                    pos=datelist_price.index(d1)
                    p=pricelist[pos]            
        #记录股价
        row=pd.Series({'endDate':d,'actualDate':d1,'Price':p})
        try:
            pricedf=pricedf.append(row,ignore_index=True)
        except:
            pricedf=pricedf._append(row,ignore_index=True)

    #合成表
    fsdf1=pd.merge(fsdf,pricedf,on='endDate')
    fsdf1['PE']=fsdf1['Price']/fsdf1['EPS']

    return fsdf1

if __name__ == '__main__':
    fs=get_financial_statements('AAPL')   
    fsdf=get_EPS(fs)
    fsdf1=get_PE(fsdf)

#==============================================================================
def calcFinRates(fsdf):
    """
    功能：基于财报计算各种指标
    """
    #前后填充缺失值
    fs = fsdf.fillna(method='ffill').fillna(method='bfill')
    
    #短期偿债能力指标
    #流动比率：流动资产 / 流动负债
    fs['Current Ratio']=fs['totalCurrentAssets']/fs['totalCurrentLiabilities']
    fs['Current Ratio']=round(fs['Current Ratio'],2)
    #速动比率：（流动资产-存货） / 流动负债
    fs['Quick Ratio']=(fs['totalCurrentAssets']-fs['inventory'])/fs['totalCurrentLiabilities']
    fs['Quick Ratio']=round(fs['Quick Ratio'],2)
    #现金比率: （现金+现金等价物） / 流动负债
    fs['Cash Ratio']=fs['cash']/fs['totalCurrentLiabilities']
    fs['Cash Ratio']=round(fs['Cash Ratio'],2)
    #现金流量比率：经营活动现金流量 / 流动负债
    fs['Cash Flow Ratio']=fs['totalCashFromOperatingActivities']/fs['totalCurrentLiabilities']
    fs['Cash Flow Ratio']=round(fs['Cash Flow Ratio'],2)
    #到期债务本息偿付比率：经营活动现金净流量 / （本期到期债务本金+现金利息支出）
    fs['Debt Service Ratio']=fs['totalCashFromOperatingActivities']/(fs['shortLongTermDebt']+fs['interestExpense'])
    fs['Debt Service Ratio']=round(fs['Debt Service Ratio'],2)
    
    #长期偿债能力指标
    #资产负债率：负债总额 / 资产总额
    fs['Debt to Asset Ratio']=fs['totalLiab']/fs['totalAssets']
    fs['Debt to Asset Ratio']=round(fs['Debt to Asset Ratio'],2)
    #股东权益比率：股东权益总额 / 资产总额
    fs['Equity to Asset Ratio']=fs['totalStockholderEquity']/fs['totalAssets']
    fs['Equity to Asset Ratio']=round(fs['Equity to Asset Ratio'],2)
    #权益乘数：资产总额 / 股东权益总额
    fs['Equity Multiplier']=fs['totalAssets']/fs['totalStockholderEquity']
    fs['Equity Multiplier']=round(fs['Equity Multiplier'],2)
    #负债股权比率：负债总额 / 股东权益总额
    fs['Debt to Equity Ratio']=fs['totalLiab']/fs['totalStockholderEquity']
    fs['Debt to Equity Ratio']=round(fs['Debt to Equity Ratio'],2)
    #有形净值债务率：负债总额 / （股东权益-无形资产净额）
    fs['netIntangibleAssets']=fs['totalAssets']-fs['netTangibleAssets']
    fs['Debt to Tangible Net Asset Ratio']=fs['totalAssets']/(fs['totalStockholderEquity']-fs['netIntangibleAssets'])
    fs['Debt to Tangible Net Asset Ratio']=round(fs['Debt to Tangible Net Asset Ratio'],2)
    #偿债保障比率：负债总额 / 经营活动现金净流量
    fs['Debt Service Coverage Ratio']=fs['totalLiab']/fs['totalCashFromOperatingActivities']
    fs['Debt Service Coverage Ratio']=round(fs['Debt Service Coverage Ratio'],2)
    #利息保障倍数：（税前利润+利息费用）/ 利息费用
    fs['Times Interest Earned Ratio']=fs['incomeBeforeTax']/fs['interestExpense']+1
    fs['Times Interest Earned Ratio']=round(fs['Times Interest Earned Ratio'],2)
    #现金利息保障倍数：（经营活动现金净流量+付现所得税） / 现金利息支出    
    fs['Cash Interest Coverage Ratio']=(fs['totalCashFromOperatingActivities']+fs['incomeTaxExpense'])/fs['interestExpense']
    fs['Cash Interest Coverage Ratio']=round(fs['Cash Interest Coverage Ratio'],2)
    
    #营运能力指标
    #存货周转率：销售成本 / 平均存货
    fs['avgInventory']=(fs['inventory']+fs['inventory'].shift(1))/2.0  
    fs['Inventory Turnover']=fs['costOfRevenue']/fs['avgInventory']
    fs['Inventory Turnover']=round(fs['Inventory Turnover'],2)    
    #应收账款周转率：赊销收入净额 / 平均应收账款余额    
    fs['avgReceivables']=(fs['netReceivables']+fs['netReceivables'].shift(1))/2.0  
    fs['Receivable Turnover']=fs['totalRevenue']/fs['avgReceivables']
    fs['Receivable Turnover']=round(fs['Receivable Turnover'],2)
    #流动资产周转率：销售收入 / 平均流动资产余额
    fs['avgCurrentAssets']=(fs['totalCurrentAssets']+fs['totalCurrentAssets'].shift(1))/2.0  
    fs['Current Asset Turnover']=fs['totalRevenue']/fs['avgCurrentAssets']
    fs['Current Asset Turnover']=round(fs['Current Asset Turnover'],2)
    #固定资产周转率：销售收入 / 平均固定资产净额
    fs['avgPPE']=(fs['propertyPlantEquipment']+fs['propertyPlantEquipment'].shift(1))/2.0  
    fs['Fixed Asset Turnover']=fs['totalRevenue']/fs['avgPPE']
    fs['Fixed Asset Turnover']=round(fs['Fixed Asset Turnover'],2)
    #总资产周转率：销售收入 / 平均资产总额
    fs['avgTotalAssets']=(fs['totalAssets']+fs['totalAssets'].shift(1))/2.0  
    fs['Total Asset Turnover']=fs['totalRevenue']/fs['avgTotalAssets']
    fs['Total Asset Turnover']=round(fs['Total Asset Turnover'],2)
    
    #主营业务利润率=主营业务利润/主营业务收入*100%
    fs['Operating Profit%']=fs['operatingIncome']/fs['totalRevenue']*100.0
    fs['Operating Profit%']=round(fs['Operating Profit%'],2)
    
    #发展潜力指标
    #营业收入增长率：本期营业收入增长额 / 上年同期营业收入总额
    fs['Revenue Growth%']=(fs['totalRevenue']-fs['totalRevenue'].shift(1))/(fs['totalRevenue'].shift(1))*100.0
    fs['Revenue Growth%']=round(fs['Revenue Growth%'],2)
    #资本积累率：本期所有者权益增长额 / 年初所有者权益
    fs['Capital Accumulation%']=(fs['totalStockholderEquity']-fs['totalStockholderEquity'].shift(1))/(fs['totalStockholderEquity'].shift(1))*100.0
    fs['Capital Accumulation%']=round(fs['Capital Accumulation%'],2)
    #总资产增长率：本期总资产增长额 / 年初资产总额    
    fs['Total Asset Growth%']=(fs['totalAssets']-fs['totalAssets'].shift(1))/(fs['totalAssets'].shift(1))*100.0
    fs['Total Asset Growth%']=round(fs['Total Asset Growth%'],2)
    #固定资产成新率：平均固定资产净值 / 平均固定资产原值。又称“固定资产净值率”或“有用系数”
    #fs['avgPPE']=(fs['propertyPlantEquipment']+fs['propertyPlantEquipment'].shift(1))/2.0
    fs['avgLTInvestments']=(fs['longTermInvestments']+fs['longTermInvestments'].shift(1))/2.0
    fs['Fixed Asset Net Value%']=fs['avgPPE']/fs['avgLTInvestments']*100.0
    fs['Fixed Asset Net Value%']=round(fs['Fixed Asset Net Value%'],2)
    
    #其他指标

    #盈利能力指标
    #资产报酬率（息前税后）：利润总额+利息支出 / 平均资产总额        
    #fs['avgTotalAssets']=(fs['totalAssets']+fs['totalAssets'].shift(1))/2.0  
    fs['Return on Asset']=(fs['netIncome']+fs['interestExpense'])/fs['avgTotalAssets']
    fs['Return on Asset']=round(fs['Return on Asset'],2)
    fs['ROA']=fs['Return on Asset']
    #资本回报率（Return on Invested Capital，简称ROIC）
    #ROIC=NOPLAT(息前税后经营利润)/IC(投入资本)
    #NOPLAT=EBIT×(1－T)=(营业利润+财务费用－非经常性投资损益) ×(1－所得税率)
    #IC=有息负债+净资产－超额现金－非经营性资产
    fs['Return on Invested Capital']=(fs['netIncome']+fs['interestExpense'])/fs['avgTotalAssets']
    fs['Return on Invested Capital']=round(fs['Return on Invested Capital'],2)
    fs['ROIC']=fs['Return on Invested Capital']
    #净资产报酬率：净利润 / 平均净资产    
    fs['avgTotalEquity']=(fs['totalStockholderEquity']+fs['totalStockholderEquity'].shift(1))/2.0  
    fs['Return on Net Asset']=fs['netIncome']/fs['avgTotalEquity']
    fs['Return on Net Asset']=round(fs['Return on Net Asset'],2)
    #股东权益报酬率：净利润 / 平均股东权益总额
    fs['Return on Equity']=fs['netIncome']/fs['avgTotalEquity']
    fs['Return on Equity']=round(fs['Return on Equity'],2)
    fs['ROE']=fs['Return on Equity']
    #毛利率：销售毛利 / 销售收入净额    
    fs['Gross Profit%']=fs['grossProfit']/fs['totalRevenue']*100.0
    fs['Gross Profit%']=round(fs['Gross Profit%'],2)
    #销售净利率：净利润 / 销售收入净额
    fs['Net Profit%']=fs['netIncome']/fs['totalRevenue']*100.0
    fs['Net Profit%']=round(fs['Net Profit%'],2)
    #成本费用净利率：净利润 / 成本费用总额
    fs['Net Profit on Costs%']=fs['netIncome']/fs['costOfRevenue']*100.0
    fs['Net Profit on Costs%']=round( fs['Net Profit on Costs%'],2)
    #股利发放率：每股股利 / 每股利润   
    fs['Payout Ratio%']=fs['dividendsPaid']/fs['netIncome']*100.0
    fs['Payout Ratio%']=round(fs['Payout Ratio%'],2)

    ###每股指标，受EPS可用性影响    
    #每股利润：（净利润-优先股股利） / 流通在外股数。基本EPS
    #注意：流通股股数=期初commonStock-treasuryStock,加本年增加的股数issuanceOfStock*月份占比-本年减少的股数repurchaseOfStock*月份占比
    fsdf=fs.copy()
    result,fs=get_EPS(fsdf)
    if not result: 
        ticker=list(fsdf['ticker'])[0]
        print("#Error(calcFinRates): EPS info unavailable for",ticker)
        print("#Side effect: per-share related rates are not calculateable, others are still useable.")
    else:
        fs['Earnings per Share']=fs['EPS']
        #每股现金流量：（经营活动现金净流量-优先股股利） / 流通在外股数
        fs['Cash Flow per Share']=fs['totalCashFromOperatingActivities']/fs['outstandingStock']
        fs['Cash Flow per Share']=round(fs['Cash Flow per Share'],2)
        fs['CFPS']=fs['Cash Flow per Share']
        #每股股利：（现金股利总额-优先股股利） /流通在外股数    
        fs['Dividend per Share']=fs['dividendsPaid']/fs['outstandingStock']
        fs['Dividend per Share']=round(fs['Dividend per Share'],2)
        fs['DPS']=fs['Dividend per Share']
        #每股净资产：股东权益总额 / 流通在外股数  
        fs['Net Asset per Share']=fs['totalStockholderEquity']/fs['outstandingStock']
        fs['Net Asset per Share']=round(fs['Net Asset per Share'],2)
    
        #市盈率：每股市价 / 每股利润，依赖EPS反推出的流通股数量
        fsdf=fs.copy()
        fs=get_PE(fsdf)
        fs['Price Earnings Ratio']=fs['PE']
    
    fs['date']=fs['endDate']
    fs.set_index('date',inplace=True)    
    
    return fs
    
    
if __name__ == '__main__':
    ticker='AAPL'     
    fsdf=get_financial_statements('AAPL')   
    fs=calcFinRates(fsdf)

#==============================================================================
def get_financial_rates(ticker):
    """
    功能：获得股票的财务报表和财务比率
    财务报表：资产负债表，利润表，现金流量表
    财务比率：短期还债能力，长期还债能力，营运能力，盈利能力，发展能力

短期偿债能力分析：
1、流动比率，计算公式： 流动资产 / 流动负债
2、速动比率，计算公式： （流动资产-存货） / 流动负债
3、现金比率，计算公式： （现金+现金等价物） / 流动负债
4、现金流量比率，计算公式： 经营活动现金流量 / 流动负债
5、到期债务本息偿付比率，计算公式： 经营活动现金净流量 / （本期到期债务本金+现金利息支出）

长期偿债能力分析：
1、资产负债率，计算公式： 负债总额 / 资产总额
2、股东权益比率，计算公式： 股东权益总额 / 资产总额
3、权益乘数，计算公式： 资产总额 / 股东权益总额
4、负债股权比率，计算公式： 负债总额 / 股东权益总额
5、有形净值债务率，计算公式： 负债总额 / （股东权益-无形资产净额）
6、偿债保障比率，计算公式： 负债总额 / 经营活动现金净流量
7、利息保障倍数，计算公式： （税前利润+利息费用）/ 利息费用
8、现金利息保障倍数，计算公式： （经营活动现金净流量+付现所得税） / 现金利息支出

营运分析
1、存货周转率，计算公式： 销售成本 / 平均存货
2、应收账款周转率，计算公式： 赊销收入净额 / 平均应收账款余额
3、流动资产周转率，计算公式： 销售收入 / 平均流动资产余额
4、固定资产周转率，计算公式： 销售收入 / 平均固定资产净额
5、总资产周转率，计算公式： 销售收入 / 平均资产总额

盈利分析
1、资产报酬率，计算公式： 利润总额+利息支出 / 平均资产总额
2、净资产报酬率，计算公式： 净利润 / 平均净资产
3、股东权益报酬率，计算公式： 净利润 / 平均股东权益总额
4、毛利率，计算公式： 销售毛利 / 销售收入净额
5、销售净利率，计算公式： 净利润 / 销售收入净额
6、成本费用净利率，计算公式： 净利润 / 成本费用总额
7、每股利润，计算公式： （净利润-优先股股利） / 流通在外股数
8、每股现金流量，计算公式： （经营活动现金净流量-优先股股利） / 流通在外股数
9、每股股利，计算公式： （现金股利总额-优先股股利） /流通在外股数
10、股利发放率，计算公式： 每股股利 / 每股利润
11、每股净资产，计算公式： 股东权益总额 / 流通在外股数
12、市盈率，计算公式： 每股市价 / 每股利润
13、主营业务利润率=主营业务利润/主营业务收入*100%

发展分析
1、营业增长率，计算公式： 本期营业增长额 / 上年同期营业收入总额
2、资本积累率，计算公式： 本期所有者权益增长额 / 年初所有者权益
3、总资产增长率，计算公式： 本期总资产增长额 / 年初资产总额
4、固定资产成新率，计算公式： 平均固定资产净值 / 平均固定资产原值

    返回：报表+比率    
    """
    # 变换港股代码5位-->4位
    result,prefix,suffix=split_prefix_suffix(ticker)
    if result & (suffix=='HK'):
        if len(prefix)==5:
            ticker=ticker[1:]    
    
    print("\nAnalyzing financial rates of",ticker,"\b, it may take lots of time...")
    
    #抓取股票的财务报表
    try:
        fsdf=get_financial_statements(ticker)
    except:
        print("......Failed to get financial statements of",ticker,"\b!")
        print("......If the stock code",ticker,"\b is correct, please try a few minutes later.")
        return None
        
    #抓取股票的稀释后EPS，计算财务比率
    fsr=calcFinRates(fsdf)
    """
    try:
        fsr=calcFinRates(fsdf)
    except:
        print("......Failed to calculate financial rates of",ticker,"\b, please retry later!")
        return None
    """    
    #整理列名：将股票代码、截止日期、报表类型排在开头
    cols=list(fsr)
    cols.remove('endDate')
    cols.remove('ticker')
    cols.remove('reportType')
    fsr2=fsr[['ticker','endDate','reportType']+cols]
    
    return fsr2


#==============================================================================
#==============================================================================
#==============================================================================
#==============================================================================
#==============================================================================
#==============================================================================
#==============================================================================











    