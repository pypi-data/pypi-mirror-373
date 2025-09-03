# -*- coding: utf-8 -*-
"""
本模块功能：SIAT公共转换函数，证券代码转换，名词中英相互转换
所属工具包：证券投资分析工具SIAT 
SIAT：Security Investment Analysis Tool
创建日期：2021年5月16日
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
from siat.common import *
from siat.yf_name import *
#==============================================================================
def ectranslate(eword):
    """
    翻译证券词汇为证券名称，基于语言环境决定中英文。
    输入：证券词汇英文
    """
    
    lang=check_language()
    if lang == 'English':
        return ectranslate_e(eword)
    else:
        return ectranslate_c(eword)

#==============================================================================
def ectranslate_c(eword):
    """
    翻译英文专业词汇至中文，便于显示或绘图时输出中文而不是英文。
    输入：英文专业词汇。输出：中文专业词汇
    """
    import pandas as pd
    ecdict=pd.DataFrame([
        
        ['implied volatility','隐含波动率'],   
        ['delta','Delta'],['gamma','Gamma'],['theta','Theta'],
        ['vega','Vega'],['rho','Rho'],
        ['Call','看涨期权'],['Put','看跌期权'],
        ['call','看涨期权'],['put','看跌期权'],
        
        ['High','最高价'],['Low','最低价'],['Open','开盘价'],['Close','收盘价'],
        ['Current Price','现时股价'],
        ['Volume','成交量'],['Adj Close','调整收盘价'],
        ['Daily Ret','日资本利得率'],['Daily Ret%','日资本利得%'],
        ['Daily Adj Ret','日收益率'],['Daily Adj Ret%','日收益率%'],
        ['log(Daily Ret)','对数日资本利得率'],['log(Daily Adj Ret)','对数日收益率'],
        ['Weekly Ret','周资本利得率'],['Weekly Ret%','周资本利得率%'],
        ['Weekly Adj Ret','周收益率'],['Weekly Adj Ret%','周收益率%'],
        ['Monthly Ret','月资本利得率'],['Monthly Ret%','月资本利得率%'],
        ['Monthly Adj Ret','月收益率'],['Monthly Adj Ret%','月收益率%'],
        ['Quarterly Ret','季资本利得率'],['Quarterly Ret%','季资本利得率%'],
        ['Quarterly Adj Ret','季收益率'],['Quarterly Adj Ret%','季收益率%'],
        ['Annual Ret','年资本利得率'],['Annual Ret%','年资本利得率%'],
        ['Annual Adj Ret','年收益率'],['Annual Adj Ret%','年收益率%'],
        ['Exp Ret','持有期资本利得率'],['Exp Ret%','持有期资本利得%'],
        ['Exp Adj Ret','持有期收益率'],['Exp Adj Ret%','持有期收益率%'],
        
        ['Weekly Price Volatility','周股价波动风险'],
        ['Weekly Adj Price Volatility','周复权价波动风险'],
        ['Monthly Price Volatility','月股价波动风险'],
        ['Monthly Adj Price Volatility','月复权价波动风险'],
        ['Quarterly Price Volatility','季股价波动风险'],
        ['Quarterly Adj Price Volatility','季复权价波动风险'],
        ['Annual Price Volatility','年股价波动风险'],
        ['Annual Adj Price Volatility','年复权价波动风险'],  
        ['Exp Price Volatility','持有期股价波动风险'], 
        ['Exp Adj Price Volatility','持有期复权价波动风险'],
        
        ['Weekly Ret Volatility','周资本利得率波动风险'],
        ['Weekly Ret Volatility%','周资本利得率波动风险%'],
        ['Weekly Adj Ret Volatility','周收益率波动风险'],
        ['Weekly Adj Ret Volatility%','周收益率波动风险%'],
        ['Monthly Ret Volatility','月资本利得率波动风险'],
        ['Monthly Ret Volatility%','月资本利得率波动风险%'],
        ['Monthly Adj Ret Volatility','月收益率波动风险'],
        ['Monthly Adj Ret Volatility%','月收益率波动风险%'],
        ['Quarterly Ret Volatility','季资本利得率波动风险'],
        ['Quarterly Ret Volatility%','季资本利得率波动风险%'],
        ['Quarterly Adj Ret Volatility','季收益率波动风险'],
        ['Quarterly Adj Ret Volatility%','季收益率波动风险%'],
        ['Annual Ret Volatility','年资本利得率波动风险'],
        ['Annual Ret Volatility%','年资本利得率波动风险%'],
        ['Annual Adj Ret Volatility','年收益率波动风险'], 
        ['Annual Adj Ret Volatility%','年收益率波动风险%'], 
        ['Exp Ret Volatility','持有期资本利得风险'], 
        ['Exp Ret Volatility%','持有期资本利得风险%'],
        ['Exp Adj Ret Volatility','持有期收益率风险'],        
        ['Exp Adj Ret Volatility%','持有期收益率风险%'],
        
        ['Weekly Ret LPSD','周资本利得率损失风险'],
        ['Weekly Ret LPSD%','周资本利得率损失风险%'],
        ['Weekly Adj Ret LPSD','周收益率损失风险'],
        ['Weekly Adj Ret LPSD%','周收益率损失风险%'],
        ['Monthly Ret LPSD','月资本利得率损失风险'],
        ['Monthly Ret LPSD%','月资本利得率损失风险%'],
        ['Monthly Adj Ret LPSD','月收益率损失风险'],
        ['Monthly Adj Ret LPSD%','月收益率损失风险%'],
        ['Quarterly Ret LPSD','季资本利得率损失风险'],
        ['Quarterly Ret LPSD%','季资本利得率损失风险%'],
        ['Quarterly Adj Ret LPSD','季收益率损失风险'],
        ['Quarterly Adj Ret LPSD%','季收益率损失风险%'],
        ['Annual Ret LPSD','年资本利得率损失风险'],
        ['Annual Ret LPSD%','年资本利得率损失风险%'],
        ['Annual Adj Ret LPSD','年收益率损失风险'], 
        ['Annual Adj Ret LPSD%','年收益率损失风险%'], 
        ['Exp Ret LPSD','持有期资本利得率损失风险'], 
        ['Exp Ret LPSD%','持有期资本利得率损失风险%'],
        ['Exp Adj Ret LPSD','持有期收益率损失风险'],        
        ['Exp Adj Ret LPSD%','持有期收益率损失风险%'],
        
        ['roll_spread','罗尔价差比率'],['amihud_illiquidity','阿米胡德非流动性'],
        ['ps_liquidity','P-S流动性'],    
        
        ['Gross Domestic Product','国内生产总值'],['GNI','国民总收入'],    
        
        ['zip','邮编'],['sector','领域'],
        ['fullTimeEmployees','全职员工数'],['Employees','全职员工数'],
        ['longBusinessSummary','业务介绍'],['city','城市'],['phone','电话'],
        ['state','州/省'],['country','国家/地区'],['companyOfficers','高管'],
        ['website','官网'],['address1','地址1'],['address2','地址2'],['industry','行业'],
        ['previousClose','上个收盘价'],['regularMarketOpen','正常市场开盘价'],
        ['twoHundredDayAverage','200天均价'],['fax','传真'], 
        ['trailingAnnualDividendYield','年化股息率TTM'],
        ['payoutRatio','股息支付率'],['volume24Hr','24小时交易量'],
        ['regularMarketDayHigh','正常市场日最高价'],
        ['averageDailyVolume10Day','10天平均日交易量'],['totalAssets','总资产'],
        ['regularMarketPreviousClose','正常市场上个收盘价'],
        ['fiftyDayAverage','50天平均股价'],
        ['trailingAnnualDividendRate','年化每股股利金额TTM'],['open','当日开盘价'],
        ['averageVolume10days','10日平均交易量'],['expireDate','失效日'],
        ['yield','收益率'],['dividendRate','每股股利金额'],
        ['exDividendDate','股利除息日'],['beta','贝塔系数(5年月频)'],
        ['startDate','开始日期'],['regularMarketDayLow','正常市场日最低价'],
        ['priceHint','价格提示'],['currency','交易币种'],
        ['trailingPE','市盈率TTM'],['regularMarketVolume','正常市场交易量'],
        ['marketCap','市值'],['averageVolume','平均交易量'],
        ['priceToSalesTrailing12Months','市销率TTM'],
        ['TTM Price to Sales','市销率TTM'],
        ['dayLow','当日最低价'],
        ['ask','卖出价'],['askSize','卖出价股数'],['volume','当日交易量'],
        ['fiftyTwoWeekHigh','52周最高价'],['forwardPE','预期市盈率'],
        ['fiveYearAvgDividendYield','5年平均股息率'],
        ['fiftyTwoWeekLow','52周最低价'],['bid','买入价'],
        ['tradeable','今日是否可交易'],['dividendYield','股息率'],
        ['bidSize','买入价股数'],['dayHigh','当日最高价'],
        ['exchange','交易所'],['shortName','简称'],['longName','全称'],
        ['exchangeTimezoneName','交易所时区'],
        ['exchangeTimezoneShortName','交易所时区简称'],['quoteType','证券类别'],
        ['symbol','证券代码'],['messageBoardId','证券留言板编号'],
        ['market','证券市场'],['annualHoldingsTurnover','一年內转手率'],
        ['enterpriseToRevenue','市售率(EV/Revenue)'],['EV to Revenue','企业价值收入比'],        
        ['Price to Book','市净率'],['beta3Year','3年贝塔系数'],
        ['profitMargins','净利润率'],['enterpriseToEbitda','企业价值/EBITDA'],
        ['EV to EBITDA','企业价值倍数（EV/EBITDA)'],
        ['52WeekChange','52周股价变化率'],['morningStarRiskRating','晨星风险评级'],
        ['forwardEps','预期每股收益'],['revenueQuarterlyGrowth','季营收增长率'],
        ['sharesOutstanding','流通在外股数'],['fundInceptionDate','基金成立日'],
        ['annualReportExpenseRatio','年报费用比率'],['bookValue','每股净资产'],
        ['sharesShort','卖空股数'],['sharesPercentSharesOut','卖空股数/流通股数'],
        ['lastFiscalYearEnd','上个财年截止日期'],
        ['heldPercentInstitutions','机构持股比例'],
        ['netIncomeToCommon','归属普通股股东净利润'],['trailingEps','每股收益TTM'],
        ['lastDividendValue','上次股利价值'],
        ['SandP52WeekChange','标普指数52周变化率'],['priceToBook','市净率'],
        ['heldPercentInsiders','内部人持股比例'],
        ['nextFiscalYearEnd','下个财年截止日期'],
        ['mostRecentQuarter','上个财季截止日期'],['shortRatio','空头净额比率'],
        ['sharesShortPreviousMonthDate','上月做空日期'],
        ['floatShares','可交易股数'],['enterpriseValue','企业价值'],
        ['threeYearAverageReturn','3年平均回报率'],['lastSplitDate','上个拆分日期'],
        ['lastSplitFactor','上次拆分比例'],
        ['earningsQuarterlyGrowth','季度盈余同比增长率'],['dateShortInterest','做空日期'],
        ['pegRatio','市盈率与增长比率PEG'],['shortPercentOfFloat','空头占可交易股票比例'],
        ['sharesShortPriorMonth','上月做空股数'],
        ['fiveYearAverageReturn','5年平均回报率'],['regularMarketPrice','正常市场价'],
        ['logo_url','商标图标网址'],     ['underlyingSymbol','曾用代码'],     
        ['timeZoneShortName','时区简称'],['timeZoneFullName','时区全称'],
        ['exchangeName','交易所名称'],
        
        ['currentPrice','当前价格'],['targetHighPrice','预计最高价格'],['targetLowPrice','预计最低价格'],
        ['targetMeanPrice','预计价格均值(1年期)'],['targetMedianPrice','预计价格中位数'],
        ['numberOfAnalystOpinions','分析师意见数量'],
        
        ['ratingYear','评估年度'],['ratingMonth','评估月份'],
        ['currencySymbol','币种符号'],['recommendationKey','投资建议'],
        ['totalInsiderShares','内部人持股数'],['financialCurrency','财报币种'],
        ['currentRatio','流动比率'],['quickRatio','速动比率'],
        ['debtToEquity','负债-权益比%'],['ebitdaMargins','EBITDA利润率'],
        ['operatingMargins','经营利润率'],['grossMargins','毛利润率'],
        ['returnOnAssets','资产回报率'],['returnOnEquity','净资产回报率'],
        ['ROA','资产回报率'],['ROE','净资产回报率'],
        ['revenuePerShare','每股销售收入'],['totalCashPerShare','每股总现金'],
        ['revenueGrowth','季度收入同比增长率'],['earningsGrowth','盈余增长率'],
        ['totalDebt','总负债'],['totalRevenue','总销售收入'],['quoteType','证券品种'],
        ['grossProfits','毛利润'],['ebitda','EBITDA'],
        ['operatingCashflow','经营现金流'],['freeCashflow','自由现金流'],
        ['totalCash','总现金流'],
        ['Total Asset Turnover','总资产周转率'],['Fixed Asset Turnover','固定资产周转率'],
        ['PPE Residual','固定资产成新率'],['Capital Accumulation','资本积累'],
        ['Current Ratio','流动比'],['Quick Ratio','速动比'],['Cash Ratio','现金比'],
        ['Debt Service Coverage','偿债保障比率'],['Debt to Equity','负债-权益比%'],
        ['Debt to Asset','资产负债比'],['Times Interest Earned','利息保障倍数'],
        ['Inventory Turnover','存货周转率'],['Receivable Turnover','应收帐款周转率'],
        ['BasicEPS','基本每股收益'],['Cashflow per Share','每股现金流量'],
        ['Profit Margin','净利润率'],['Gross Margin','毛利润率'],
        ['EBITDA Margin','EBITDA利润率'],['Operating Margin','营业利润率'],
        ['Trailing EPS','每股收益TTM'],['Forward EPS','预期每股收益'],
        ['Trailing PE','市盈率TTM'],['Forward PE','预期市盈率'],
        ['Revenue Growth','销售收入增长率'],['Earnings Growth','年度盈余增长率'],
        ['Earnings Quarterly Growth','季度盈余增长率'],
        ['IGR','内部增长率(IGR)'],['SGR','可持续增长率(SGR)'],
        ['Payout Ratio','股利支付率'],
        
        ['PE','市盈率'],['PB','市净率'],['MV','市值'],['PS','市销率'],
        
        ['overallRisk','总风险指数'],
        ['boardRisk','董事会风险指数'],['compensationRisk','薪酬风险指数'],
        ['shareHolderRightsRisk','股东风险指数'],['auditRisk','审计风险指数'],
        
        ['totalEsg','ESG总分数'],['Total ESG','ESG总分数'],
        ['esgPerformance','ESG业绩评价'],
        ['peerEsgScorePerformance','ESG同业分数'],
        ['environmentScore','环保分数'],['Environment Score','环保分数'],
        ['peerEnvironmentPerformance','环保同业分数'],
        ['socialScore','社会责任分数'],['Social Score','社会责任分数'],
        ['peerSocialPerformance','社会责任同业分数'],
        ['governanceScore','公司治理分数'],['Governance Score','公司治理分数'],
        ['peerGovernancePerformance','公司治理同业分数'],['peerGroup','同业分组'],
        ['relatedControversy','相关焦点'],['Social Supply Chain Incidents','供应链事件'],
        ['Customer Incidents','客户相关事件'],['Business Ethics Incidents','商业道德事件'],
        ['Governance Incidents','公司治理事件'],
        ['Product & Service Incidents','产品与服务相关事件'],
        ['Society & Community Incidents','社会与社区相关事件'],
        ['Employee Incidents','雇员相关事件'],['Operations Incidents','运营相关事件'],
        ['peerCount','同业个数'],['percentile','同业所处分位数'],  
        
        ['ESGscore','ESG风险'],['ESGpercentile','ESG风险行业分位数%'],
        ['ESGperformance','ESG风险评价'],['EPscore','环保风险'],
        ['EPpercentile','环保风险分位数%'],['CSRscore','社会责任风险'],
        ['CSRpercentile','社会责任风险分位数%'],['CGscore','公司治理风险'],
        ['CGpercentile','公司治理风险分位数%'],
        ['Peer Group','业务分类'],['Count','数目'],     
        
        ['China','中国'],['Japan','日本'],['USA','美国'],['India','印度'],
        ['Russia','俄罗斯'],['Korea','韩国'],['Australia','澳大利亚'],
        ['Germany','德国'],['UK','英国'],['GBR','英国'],['France','法国'],
        ['Vietnam','越南'],['Indonesia','印度尼西亚'],['Malaysia','马来西亚'],
        ['Singapore','新加坡'],
        
        ['Gross Domestic Product','国内生产总值'],['GDP','国内生产总值'],  
        ['Constant GDP','国内生产总值'],['Current GDP','国内生产总值'],
        ['Current Price Gross Domestic Product','国内生产总值'],
        ['Real GDP at Constant National Prices','国内生产总值'],
        ['Constant GDP Per Capita','人均GDP'],
        ['GDP Per Capita','人均GDP'],
        ['Gross Domestic Product Per Capita','人均GDP'],
        ['Constant Price GDP Per Capita','人均GDP'],
        ['GNP','国民生产总值'],['GNP Ratio','GNP(GNI)与GDP的比例'],
        ['GNI/GDP Ratio','GNP(GNI)与GDP之比'],
        ['Ratio of GNP to GDP','GNP(GNI)与GDP之比'],
        
        ['Gross National Income','国民总收入'],
        
        ['CPI','消费者价格指数'],['YoY CPI','CPI%（同比）'],
        ['MoM CPI','CPI%（环比）'],['Constant CPI','CPI%（相对基准值）'],
        ['Consumer Price Index','消费者价格指数'],
        ['Consumer Price Index: All Items','消费者价格指数'],
        ['Consumer Price Index: All Items Growth Rate','消费者价格指数增速'],
        ['PPI','生产者价格指数'],['YoY PPI','PPI%（同比）'],
        ['MoM PPI','PPI%（环比）'],['Constant PPI','PPI%（相对基准值）'],
        ['Producer Prices Index: Industrial Activities','工业活动PPI'],
        ['Producer Prices Index: Total Industrial Activities','全部工业活动PPI'],
        
        ['Exchange Rate','汇率'],
        ['M0','流通中现金M0供应量'],['M1','狭义货币M1供应量'],['M2','广义货币M2供应量'],
        ['M3','金融货币M3供应量'],
        ['Constant M0','流通中现金M0相对数'],['Constant M1','狭义货币M1相对数'],
        ['Constant M2','广义货币M2相对数'],['Constant M3','金融货币M3相对数'],
        
        ['National Monetary Supply M0','流通中现金M0供应量'],
        ['National Monetary Supply M1','狭义货币M1供应量'],
        ['National Monetary Supply M2','广义货币M2供应量'],
        ['National Monetary Supply M3','金融货币M3供应量'],
        
        ['Discount Rate','贴现率%'],
        ['Central Bank Discount Rate','中央银行贴现率'],
        
        ['Immediate Rate','即期利率%'],
        ['Immediate Rates: Less than 24 Hours: Interbank Rate','银行间即期利率（24小时内）'],  
        
        ['Local Currency/USD Foreign Exchange Rate','本币/美元汇率'],  
        ['USD/Local Currency Foreign Exchange Rate','美元/本币汇率'],['Euro','欧元'],
        
        ['Daily','日'],['Monthly','月'],['Quarterly','季'],['Annual','年'],
        
        ['Stock Market Capitalization to GDP','基于股市总市值的经济金融深度'],
        ['SMC to GDP','股市总市值/GDP'],
        
        ['Currency Value','货币价值'],['Currency Purchasing Power Based on CPI','基于CPI的货币购买力'],
        
        ['Portfolio','投资组合'],['Portfolio_EW','等权重组合'],['Portfolio_OMCap','流通市值权重组合'],
        ['Portfolio_MSR','MSR组合'],['Portfolio_GMV','GMV组合'],
        
        ['sharpe','夏普比率'],['sortino','索替诺比率'],['treynor','特雷诺比率'],['alpha','阿尔法指标'],
        
        ], columns=['eword','cword'])

    try:
        cword=ecdict[ecdict['eword']==eword]['cword'].values[0]
    except:
        #未查到翻译词汇，返回原词
        cword=eword
   
    return cword

if __name__=='__main__':
    eword='Exp Adj Ret'
    print(ectranslate('Annual Adj Ret%'))
    print(ectranslate('Annual*Adj Ret%'))

    eword='Constant M1'
    print(ectranslate(eword))
    print(ectranslate('Annual*Adj Ret%'))

#==============================================================================
def ectranslate_e(eword):
    """
    翻译英文专业词汇至英文，便于显示或绘图时输出英文。绝大多数英文专业词汇无需翻译
    输入：英文专业词汇
    """
    import pandas as pd
    ecdict=pd.DataFrame([

        ['implied volatility','Implied Volatility'],        
        ['delta','Delta'],['gamma','Gamma'],['theta','Theta'],
        ['vega','Vega'],['rho','Rho'],
        ['Call','Call option'],['Put','Put option'],
        ['call','Call option'],['put','Put option'],

        ['Daily Ret%','Daily Return%'],['Daily Adj Ret','Daily Adjusted Return'],
        ['Daily Adj Ret%','Daily Adjusted Return%'],['log(Daily Ret)','log(Daily Return)'],
        ['log(Daily Adj Ret)','log(Daily Adjusted Return)'],['Weekly Ret','Weekly Return'],
        ['Weekly Ret%','Weekly Return%'],['Weekly Adj Ret','Weekly Adjusted Return'],
        ['Weekly Adj Ret%','Weekly Adjusted Return%'],['Monthly Ret','Monthly Return'],
        ['Monthly Ret%','Monthly Return%'],['Monthly Adj Ret','Monthly Adjusted Return'],
        ['Monthly Adj Ret%','Monthly Adjusted Return%'],['Quarterly Ret','Quarterly Return'],
        ['Quarterly Ret%','Quarterly Return%'],['Quarterly Adj Ret','Quarterly Adjusted Return'],
        ['Quarterly Adj Ret%','Quarterly Adjusted Return%'],['Annual Ret','Annual Return'],
        ['Annual Ret%','Annual Return%'],['Annual Adj Ret','Annual Adjusted Return'],
        ['Annual Adj Ret%','Annual Adjusted Return%'],['Exp Ret','Holding Period Capital Gain Rate'],
        ['Exp Ret%','Holding Period Capital Gain%'],['Exp Adj Ret','Holding Period Return'],
        ['Exp Adj Ret%','Holding Period Return%'],
        
        ['Weekly Price Volatility','Weekly Price Volatility'],
        ['Weekly Adj Price Volatility','Weekly Adjusted Price Volatility'],
        ['Monthly Price Volatility','Monthly Price Volatility'],
        ['Monthly Adj Price Volatility','Monthly Adjusted Price Volatility'],
        ['Quarterly Price Volatility','Quarterly Price Volatility'],
        ['Quarterly Adj Price Volatility','Quarterly Adjusted Price Volatility'],
        ['Annual Price Volatility','Annual Price Volatility'],
        ['Annual Adj Price Volatility','Annual Adjusted Price Volatility'],  
        ['Exp Price Volatility','Expanded Price Volatility'], 
        ['Exp Adj Price Volatility','Expanded Adjusted Price Volatility'],
        
        ['Weekly Ret Volatility','Weekly Return Volatility'],
        ['Weekly Ret Volatility%','Weekly Return Volatility%'],
        ['Weekly Adj Ret Volatility','Weekly Adjusted Return Volatility'],
        ['Weekly Adj Ret Volatility%','Weekly Adjusted Return Volatility%'],
        ['Monthly Ret Volatility','Monthly Return Volatility'],
        ['Monthly Ret Volatility%','Monthly Return Volatility%'],
        ['Monthly Adj Ret Volatility','Monthly Adjusted Return Volatility'],
        ['Monthly Adj Ret Volatility%','Monthly Adjusted Return Volatility%'],
        ['Quarterly Ret Volatility','Quarterly Return Volatility'],
        ['Quarterly Ret Volatility%','Quarterly Return Volatility%'],
        ['Quarterly Adj Ret Volatility','Quarterly Adjusted Return Volatility'],
        ['Quarterly Adj Ret Volatility%','Quarterly Adjusted Return Volatility%'],
        ['Annual Ret Volatility','Annual Return Volatility'],
        ['Annual Ret Volatility%','Annual Return Volatility%'],
        ['Annual Adj Ret Volatility','Annual Adjusted Return Volatility'], 
        ['Annual Adj Ret Volatility%','Annual Adjusted Return Volatility%'], 
        ['Exp Ret Volatility','Holding Period Capital Gain Volatility'], 
        ['Exp Ret Volatility%','Holding Period Capital Gain Volatility%'],
        ['Exp Adj Ret Volatility','Holding Period Return Volatility'],        
        ['Exp Adj Ret Volatility%','Holding Period Return Volatility%'],
        
        ['Weekly Ret LPSD','Weekly Loss Risk'],
        ['Weekly Ret LPSD%','Weekly Loss Risk%'],
        ['Weekly Adj Ret LPSD','Weekly Adjusted Loss Risk'],
        ['Weekly Adj Ret LPSD%','Weekly Adjusted Loss Risk%'],
        ['Monthly Ret LPSD','Monthly Loss Risk'],
        ['Monthly Ret LPSD%','Monthly Loss Risk%'],
        ['Monthly Adj Ret LPSD','Monthly Adjusted Loss Risk'],
        ['Monthly Adj Ret LPSD%','Monthly Adjusted Loss Risk%'],
        ['Quarterly Ret LPSD','Quarterly Loss Risk'],
        ['Quarterly Ret LPSD%','Quarterly Loss Risk%'],
        ['Quarterly Adj Ret LPSD','Quarterly Adjusted Loss Risk'],
        ['Quarterly Adj Ret LPSD%','Quarterly Adjusted Loss Risk%'],
        ['Annual Ret LPSD','Annual Loss Risk'],
        ['Annual Ret LPSD%','Annual Loss Risk%'],
        ['Annual Adj Ret LPSD','Annual Adjusted Loss Risk'], 
        ['Annual Adj Ret LPSD%','Annual Adjusted Loss Risk%'], 
        ['Exp Ret LPSD','Holding Period Capital Loss Risk'], 
        ['Exp Ret LPSD%','Holding Period Capital Loss Risk%'],
        ['Exp Adj Ret LPSD','Holding Period Loss Risk'],        
        ['Exp Adj Ret LPSD%','Holding Period Loss Risk%'],
        
        ['roll_spread','Roll Spread'],['amihud_illiquidity','Amihud Illiquidity'],
        ['ps_liquidity','P-S Liquidity'],    
        
        ['Gross Domestic Product','GDP'], 
        
        ['zip','Zip'],['sector','Sector'],
        ['fullTimeEmployees','Employees'],['Employees','Employees'],
        ['longBusinessSummary','Long business summary'],['city','City'],['phone','Phone'],
        ['state','State/Province'],['country','Country/Region'],['companyOfficers','Company officers'],
        ['website','Website'],['address1','Address'],['industry','Industry'],
        ['previousClose','Prev close'],['regularMarketOpen','Regular market open'],
        ['twoHundredDayAverage','200-day average'],['fax','Fax'], 
        ['trailingAnnualDividendYield','Annual Div Yield TTM'],
        ['payoutRatio','Payout ratio'],['volume24Hr','Volume 24-hour'],
        ['regularMarketDayHigh','Regular market high'],
        ['averageDailyVolume10Day','10-day avg daily volume'],['totalAssets','Total Assets'],
        ['regularMarketPreviousClose','Regular market prev close'],
        ['fiftyDayAverage','50-day average'],
        ['trailingAnnualDividendRate','Annual div rate TTM'],['open','Open'],
        ['averageVolume10days','10-day avg volume'],['expireDate','Expire date'],
        ['yield','Yield'],['dividendRate','Dividend rate'],
        ['exDividendDate','Ex-dividend date'],['beta','Beta'],
        ['startDate','Start date'],['regularMarketDayLow','Regular market day low'],
        ['priceHint','Price hint'],['currency','Currency'],
        ['trailingPE','PE TTM'],['regularMarketVolume','Regular market volume'],
        ['marketCap','Market capitalization'],['averageVolume','Average volume'],
        ['priceToSalesTrailing12Months','Price-to-sales TTM'],
        ['TTM Price to Sales','Price-to-sales TTM'],
        ['dayLow','Day low'],
        ['ask','Ask/sell'],['askSize','Ask size'],['volume','Volume'],
        ['fiftyTwoWeekHigh','52-week high'],['forwardPE','Forward PE'],
        ['fiveYearAvgDividendYield','5-year Avg div yield'],
        ['fiftyTwoWeekLow','52-week low'],['bid','Bid/Buy-in'],
        ['tradeable','Tradeable'],['dividendYield','Dividend yield'],
        ['bidSize','Bid size'],['dayHigh','Day high'],
        ['exchange','Exchange'],['shortName','Short name'],['longName','Fullname'],
        ['exchangeTimezoneName','Exchange timezone name'],
        ['exchangeTimezoneShortName','Exchange timezone short name'],['quoteType','Quote type'],
        ['symbol','Symbol'],['messageBoardId','Message board id'],
        ['market','Market'],['annualHoldingsTurnover','Annual holdings turnover'],
        ['enterpriseToRevenue','EV/Revenue'],['EV to Revenue','EV/Revenue'],        
        ['Price to Book','Price-to-book'],['beta3Year','3-year beta'],
        ['profitMargins','Profit margin'],['enterpriseToEbitda','EV/EBITDA'],
        ['EV to EBITDA','EV/EBITDA'],
        ['52WeekChange','52-week change'],['morningStarRiskRating','Morningstar risk rating'],
        ['forwardEps','Forward EPS'],['revenueQuarterlyGrowth','Revenue quarterly growth'],
        ['sharesOutstanding','Shares outstanding'],['fundInceptionDate','Fund inception date'],
        ['annualReportExpenseRatio','Annual report expense ratio'],['bookValue','Book value per share'],
        ['sharesShort','Shares short (sell)'],['sharesPercentSharesOut','Shares percent shares-out(Shares short/outstanding)'],
        ['lastFiscalYearEnd','Last fiscal year end'],
        ['heldPercentInstitutions','Held percent by institutions'],
        ['netIncomeToCommon','Netincome to common'],['trailingEps','EPS TTM'],
        ['lastDividendValue','Last dividend value'],
        ['SandP52WeekChange','52-week S&P500 change'],['priceToBook','Price-to-book'],
        ['heldPercentInsiders','Held percent by insiders'],
        ['nextFiscalYearEnd','Next fiscal year end'],
        ['mostRecentQuarter','Most recent quarter'],['shortRatio','空头净额比率'],
        ['sharesShortPreviousMonthDate','上月做空日期'],
        ['floatShares','可交易股数'],['enterpriseValue','Enterprise value'],
        ['threeYearAverageReturn','3年平均回报率'],['lastSplitDate','上个拆分日期'],
        ['lastSplitFactor','上次拆分比例'],
        ['earningsQuarterlyGrowth','Earnings growth(quarterly)'],['dateShortInterest','做空日期'],
        ['pegRatio','PEG ratio'],['shortPercentOfFloat','空头占可交易股票比例'],
        ['sharesShortPriorMonth','上月做空股数'],
        ['fiveYearAverageReturn','5年平均回报率'],['regularMarketPrice','正常市场价'],
        ['logo_url','商标图标网址'],     ['underlyingSymbol','曾用代码'],     
        ['timeZoneShortName','时区简称'],['timeZoneFullName','时区全称'],
        ['exchangeName','Exchange name'],
        
        ['currentPrice','Current price'],['targetHighPrice','Target high price'],
        ['targetLowPrice','Target low price'],
        ['targetMeanPrice','Target mean price'],['targetMedianPrice','Target median price'],
        ['numberOfAnalystOpinions','Number of analyst opinions'],
        
        ['ratingYear','评估年度'],['ratingMonth','评估月份'],
        ['currencySymbol','币种符号'],['recommendationKey','Recommendation'],
        ['totalInsiderShares','Total insider shares'],['financialCurrency','Currency'],
        ['currentRatio','Current ratio'],['quickRatio','Quick ratio'],
        ['debtToEquity','Debt-to-equity%'],['ebitdaMargins','EBITDA margins'],
        ['operatingMargins','Operating margins'],['grossMargins','Gross margins'],
        ['returnOnAssets','Return on assets'],['returnOnEquity','Return on equity'],
        ['ROA','Return on assets'],['ROE','Return on equity'],
        ['revenuePerShare','Revenue per share'],['totalCashPerShare','Cashflow per share'],
        ['revenueGrowth','Revenue growth(annual)'],['earningsGrowth','Earnings growth(annual)'],
        ['totalDebt','Total debt'],['totalRevenue','Total revenue'],
        ['grossProfits','Gross profits'],['ebitda','EBITDA'],
        ['operatingCashflow','Operating cashflow'],['freeCashflow','Free cashflow'],
        ['totalCash','Total cash'],
        ['Total Asset Turnover','Total asset turnover'],['Fixed Asset Turnover','Fixed asset turnover'],
        ['PPE Residual','PPE Residual'],
        ['Current Ratio','Current ratio'],['Quick Ratio','Quick ratio'],['Debt to Equity','Debt-to-Equity%'],
        ['Debt to Asset','Debt to assets'],['Times Interest Earned','Times interest earned'],
        ['Inventory Turnover','Inventory turnover'],['Receivable Turnover','Receivable turnover'],
        ['BasicEPS','Basic EPS'],['Cashflow per Share','Cashflow per share'],
        ['Profit Margin','Profit margins'],['Gross Margin','Gross margins'],
        ['EBITDA Margin','EBITDA margins'],['Operating Margin','Operating margins'],
        ['Trailing EPS','EPS TTM'],['Forward EPS','Forward EPS'],
        ['Trailing PE','PE TTM'],['Forward PE','Forward PE'],
        ['Revenue Growth','Revenue growth'],['Earnings Growth','Earnings growth(annual)'],
        ['Earnings Quarterly Growth','Earnings growth(quarterly)'],
        ['IGR','Internal growth rate'],['SGR','Sustainable growth rate'],
        
        ['overallRisk','Overall risk'],
        ['boardRisk','Board risk'],['compensationRisk','Compensation risk'],
        ['shareHolderRightsRisk','Shareholder rights risk'],['auditRisk','Audit risk'],
        
        ['totalEsg','Total ESG risk'],['Total ESG','Total ESG risk'],
        ['esgPerformance','ESG performance'],
        ['peerEsgScorePerformance','Peer ESG score performance'],
        ['environmentScore','Environment risk score'],['Environment Score','Environment risk score'],
        ['peerEnvironmentPerformance','Peer environment performance'],
        ['socialScore','CSR risk score'],['Social Score','CSR risk score'],
        ['peerSocialPerformance','Peer CSR performance'],
        ['governanceScore','Governance risk score'],['Governance Score','Governance risk score'],
        ['peerGovernancePerformance','Peer governance performance'],['peerGroup','Peer group'],
        ['relatedControversy','Related controversy'],['Social Supply Chain Incidents','Social supply chain incidents'],
        ['Customer Incidents','Customer incidents'],['Business Ethics Incidents','Business ethics incidents'],
        ['Product & Service Incidents','Product & service incidents'],
        ['Society & Community Incidents','Society & community incidents'],
        ['Employee Incidents','Employee incidents'],['Operations Incidents','Operations incidents'],
        ['peerCount','Peer count'],['percentile','Peer percentile'],  
        
        ['ESGscore','ESG risk score'],['ESGpercentile','ESG risk percentile%'],
        ['ESGperformance','ESG risk performance'],['EPscore','Environment risk score'],
        ['EPpercentile','Environment risk percentile%'],['CSRscore','CSR risk score'],
        ['CSRpercentile','CSR risk percentile%'],['CGscore','Governance risk score'],
        ['CGpercentile','Governance risk percentile%'],
        ['Peer Group','Peer Group'],['Count','Peer count'],     
        
        ['Gross Domestic Product','GDP'],
        ['Current Price Gross Domestic Product','GDP'],
        ['GNP Ratio','GNP(GNI)/GDP Ratio'],
        
        ['Consumer Price Index','CPI'],
        ['Consumer Price Index: All Items','CPI-All Items'],
        ['Consumer Price Index: All Items Growth Rate','CPI-All Items Growth Rate'],
        ['PPI','PPI'],['YoY PPI','YoY PPI%'],
        ['MoM PPI','MoM PPI%'],['Constant PPI','Constant PPI%'],
        ['Producer Prices Index: Industrial Activities','PPI-Industrial Activities'],
        ['Producer Prices Index: Total Industrial Activities','PPI-Total Industrial Activities'],
        
        ['National Monetary Supply M0','Outstanding Cash Supply M0'],
        ['National Monetary Supply M1','Monetary Supply M1'],
        ['National Monetary Supply M2','Monetary Supply M2'],
        ['National Monetary Supply M3','Monetary Supply M3'],
        
        ['Immediate Rate','Immediate Rate%'],
        ['Immediate Rates: Less than 24 Hours: Interbank Rate','Interbank Immediate Rates(in 24-hour)'],  
        
        ['Local Currency/USD Foreign Exchange Rate','Local/USD Exch Rate'],  
        ['USD/Local Currency Foreign Exchange Rate','USD/Local Exch Rate'],['Euro','Euro'],
        
        ['Stock Market Capitalization to GDP','Economic Depth in Finance Based on Stock Market Capitalization'],
        ['SMC to GDP','Total Market Cap/GDP'],
        
        ['Currency Value','Currency Value'],['Currency Purchasing Power Based on CPI','Currency Purchasing Power Based on CPI'],
        
        ['Portfolio','Portfolio'],['Portfolio_EW','Portfolio_EW'],['Portfolio_OMCap','Portfolio_OMCap'],
        ['Portfolio_MSR','Portfolio_MSR'],['Portfolio_GMV','Portfolio_GMV'],
        
        ['权益乘数','Equity Multiplier'],['销售净利率','Profit Margins'],['总资产周转率','Total Asset Turnover'],
        ['公司','Company'],['净资产收益率','ROE'],['财报日期','End Date'],['财报类型','Report Type'],
        
        ], columns=['eword','cword'])

    try:
        cword=ecdict[ecdict['eword']==eword]['cword'].values[0]
    except:
        #未查到翻译词汇，返回原词
        cword=eword
   
    return cword

if __name__=='__main__':
    eword='Exp Adj Ret'
    print(ectranslate('Annual Adj Ret%'))
    print(ectranslate('Annual*Adj Ret%'))

    eword='Constant M1'
    print(ectranslate(eword))
    print(ectranslate('Annual*Adj Ret%'))

#==============================================================================
def codetranslate(codelist):
    """
    翻译证券代码为证券名称，基于语言环境决定中英文。
    输入：证券代码列表。输出：证券名称列表
    """
    
    lang=check_language()
    if lang == 'English':
        return codetranslate_e(codelist)
    else:
        return codetranslate_c(codelist)

#==============================================================================
if __name__=='__main__':
    codelist=['601398.SS','01398.HK']
    codelist='PDD'
    
    code='601398.SS'
    code='01398.HK'
    
    codetranslate_e(codelist)

#在common中定义
#SUFFIX_LIST_CN=['SS','SZ','BJ','NQ']
    
def codetranslate_e(codelist):
    """
    翻译证券代码为证券名称英文。
    输入：证券代码列表。输出：证券名称列表
    """
    
    if isinstance(codelist,list):
        namelist=[]
        for code in codelist:
            if not code in ['USA','UK']:
                name=codetranslate1(code)
            else:
                name=code
                
            name1=name
            result,prefix,suffix=split_prefix_suffix(code)
            if suffix in SUFFIX_LIST_CN:
                if not ('A' in name):
                    name1=name
            elif suffix in ['HK']:
                if not ('HK' in name):
                    name1=name+'(HK)'            
            else:
                name1=name
            namelist=namelist+[name1]
        return namelist
    elif isinstance(codelist,str):
        code=codelist
        if not code in ['USA','UK']:
            name=codetranslate1(code)
        else:
            name=code
            
        if name==code:
            return name
        name1=name
        result,prefix,suffix=split_prefix_suffix(code)
        if suffix in SUFFIX_LIST_CN:
            if not ('A' in name) and not('Index' in name):
                name1=name
        if suffix in ['HK']:
            if not ('HK' in name):
                name1=name+'(HK)'            
        return name1
    else:
        return codelist
            
if __name__=='__main__':
    codetranslate(['601398.SS','01398.HK','JD','BABA'])
    codetranslate('601398.SS')
    codetranslate('01398.HK')
    codetranslate('JD')
    codetranslate('AMZN')
    codetranslate('AAPL')
    codetranslate('XYZ')
#==============================================================================
if __name__=='__main__':
    codelist=['601398.SS','01398.HK']
    code='601398.SS'
    code='01398.HK'

#在common中定义
#SUFFIX_LIST_CN=['SS','SZ','BJ','NQ']
    
def codetranslate_c(codelist):
    """
    翻译证券代码为证券名称中文。
    输入：证券代码列表。输出：证券名称列表
    """
    
    if isinstance(codelist,list):
        namelist=[]
        for code in codelist:
            name=codetranslate0(code)
            name1=name
            result,prefix,suffix=split_prefix_suffix(code)
            if suffix in SUFFIX_LIST_CN:
                if not ('A' in name):
                    name1=name
            elif suffix in ['HK']:
                if not ('港股' in name):
                    #name1=name+'(港股)'
                    name1=name+'(港)'
            else:
                name1=name
            namelist=namelist+[name1]
        return namelist
    elif isinstance(codelist,str):
        code=codelist
        name=codetranslate0(code)
        if name==code:
            return name
        name1=name
        result,prefix,suffix=split_prefix_suffix(code)
        if suffix in SUFFIX_LIST_CN:
            if not ('A' in name) and not('指数' in name):
                name1=name
        if suffix in ['HK']:
            if not ('港股' in name):
                #name1=name+'(港股)'
                name1=name+'(港)'
        return name1
    else:
        return codelist
            
if __name__=='__main__':
    codetranslate(['601398.SS','01398.HK','JD','BABA'])
    codetranslate('601398.SS')
    codetranslate('01398.HK')
    codetranslate('JD')
    codetranslate('AMZN')
    codetranslate('AAPL')
    codetranslate('XYZ')

#==============================================================================

def codetranslate0(code):
    """
    翻译证券代码为证券名称中文。
    输入：证券代码。输出：证券名称
    """
    #不翻译情况:以空格开头，去掉空格返回
    if code[:1]==' ':
        return code[1:]
    
    import pandas as pd
    codedict=pd.DataFrame([
            
        #股票：地产
        ['000002.SZ','万科A'],['600266.SS','城建发展'],['600376.SS','首开股份'],
        ['600340.SS','华夏幸福'],['600606.SS','绿地控股'],
        
        #股票：白酒
        ['600519.SS','贵州茅台'],['000858.SZ','五粮液'],['000596.SZ','古井贡酒'],
        ['000568.SZ','泸州老窖'],['600779.SS','水井坊'],['002304.SZ','洋河股份'],
        ['000799.SZ','酒鬼酒'],['603589.SS','口子窖'],['600809.SS','山西汾酒'],
        
        #股票：银行
        ['601398.SS','工商银行A股'],['601939.SS','建设银行A股'],
        ['601288.SS','农业银行A股'],['601988.SS','中国银行A股'],
        ['600000.SS','浦发银行'],['601328.SS','交通银行'],
        ['600036.SS','招商银行'],['000776.SZ','广发银行'],
        ['601166.SS','兴业银行'],['601169.SS','北京银行'],
        ['600015.SS','华夏银行'],['601916.SS','浙商银行'],
        ['600016.SS','民生银行'],['000001.SZ','平安银行'],
        ['601818.SS','光大银行'],['601998.SS','中信银行'],
        ['601229.SS','上海银行'],['601658.SS','邮储银行'],
        
        ['01398.HK','工商银行港股'],['00939.HK','建设银行港股'],
        ['01288.HK','农业银行港股'],['00857.HK','中国石油港股'],
        ['00005.HK','港股汇丰控股'],['02888.HK','港股渣打银行'],
        ['03988.HK','中国银行港股'],['BANK OF CHINA','中国银行'],
        
        ['CICHY','建设银行美股'],['CICHF','建设银行美股'],
        ['ACGBY','农业银行美股'],['ACGBF','农业银行美股'],
        ['IDCBY','工商银行美股'],['IDCBF','工商银行美股'],
        ['BCMXY','交通银行美股'],
        
        ['BAC','美国银行'],['Bank of America Corporation','美国银行'],
        ['JPM','摩根大通'],['JP Morgan Chase & Co','摩根大通'],
        ['WFC','富国银行'],
        ['MS','摩根士丹利'],['Morgan Stanley','摩根士丹利'],
        ['USB','美国合众银行'],['U','美国合众银行'],
        ['TD','道明银行'],['Toronto Dominion Bank','道明银行'],
        ['PNC','PNC金融'],['PNC Financial Services Group','PNC金融'],
        ['BK','纽约梅隆银行'],['The Bank of New York Mellon Cor','纽约梅隆银行'],    
        ['GS','高盛'],['C','花旗集团'],
        
        ['SIVB','硅谷银行'],['WFC','富国银行'],['SBNY','签字银行'],
        ['FRC','第一共和银行'],['CS','瑞士信贷'],['UBS','瑞银(美)'],
        ['SI','加密友好银行'],

        
        ['8306.T','三菱日联金融(日)'],['MUFG','三菱日联金融(美)'],
        ['MITSUBISHI UFJ FINANCIAL GROUP','三菱日联金融'],
        ['8411.T','瑞穗金融(日)'],['MIZUHO FINANCIAL GROUP','瑞穗金融'],
        ['7182.T','日本邮政银行'],['JAPAN POST BANK CO LTD','日本邮政银行'], 

        ['00005.HK','汇丰控股(港)'],['HSBC HOLDINGS','汇丰控股'],
        ['HSBA.L','汇丰控股(英)'],
        ['02888.HK','渣打银行(港)'],['STANCHART','渣打银行'],  
        
        ['UBSG.SW','瑞银(瑞士)'], 
        ['IBN','印度工商银行(美)'],['ICICIBANK.NS','印度工商银行(国)'],
        ['ICICIBANK.BO','印度工商银行(孟)'], 
        ['SBIN.NS','印度国家银行(国)'], 
        ['SCGLY','法国兴业银行(美)'],['GLE.PA','法国兴业银行(巴)'],         

        #股票：高科技
        ['AAPL','苹果'],['Apple','苹果'],['DELL','戴尔'],['IBM','国际商用机器'],
        ['MSFT','微软'],['Microsoft','微软'],['HPQ','惠普'],['AMD','超威半导体'],
        ['NVDA','英伟达'],['INTC','英特尔'],['QCOM','高通'],['BB','黑莓'],
        
        #股票：电商、互联网        
        ['AMZN','亚马逊'],['Amazon','亚马逊'],
        ['SHOP','Shopify'],['MELI','美客多'],
        ['EBAY','易贝'],['eBay','易贝'],['META','元宇宙(脸书)'],['ZM','ZOOM'],
        ['GOOG','谷歌'],['GOOGL','谷歌'],['TWTR','X(推特)'],
        ['VIPS','唯品会'],['Vipshop','唯品会'],
        ['PDD','拼多多美股'],['Pinduoduo','拼多多'],        
        ['BABA','阿里巴巴美股'],['Alibaba','阿里巴巴美股'],
        ['JD','京东美股'],['MPNGY','美团美股'],
        ['SINA','新浪网'],['BIDU','百度'],['NTES','网易'],
        
        ['00700.HK','腾讯港股'],['TENCENT','腾讯控股'],
        ['09988.HK','阿里巴巴港股'],['BABA-SW','阿里巴巴港股'],
        ['09618.HK','京东港股'],['JD-SW','京东港股'],
        ['02517.HK','锅圈食品'], 
        
        #股票：石油、矿业
        ['SLB','斯伦贝谢'],['BKR','贝克休斯'],['HAL','哈里伯顿'],
        ['WFTLF','威德福'],['WFTUF','威德福'],
        ['OXY','西方石油'],['COP','康菲石油'],
        ['FCX','自由港矿业'], ['AEM','伊格尔矿业'],   
        ['XOM','美孚石油'],['2222.SR','沙特阿美'],
        ['BP','英国石油'],['RDSA.AS','壳牌石油'],
        ['1605.T','国际石油开发帝石'],['5020.T','新日本石油'],['5713.T','住友金属矿山'],
        
        ['NEM','纽蒙特矿业'],['SCCO','南方铜业'],
        ['RGLD','皇家黄金'],['AA','美铝'],['CLF','克利夫兰-克利夫斯矿业'],
        ['BTU','皮博迪能源'],        
        
        ['601857.SS','中国石油A股'],['PTR','中石油美股'],
        ['00857.HK','中国石油港股'],['PETROCHINA','中国石油'],
        
        ['00883.HK','中国海油港股'],['601808.SS','中海油服A股'],
        ['02883.HK','中海油服港股'],['600583.SS','海油工程A股'],['600968.SS','海油发展A股'],
        
        ['600028.SS','中国石化A股'],['00386.HK','中国石化港股'],
        ['600871.SS','石化油服A股'],['01033.HK','石化油服港股'],
        
        ['600339.SS','中油工程A股'],
        
        ['03337.HK','安东油服港股'],['603619.SS','中曼石油A股'],['002476.SZ','宝莫股份A股'],
        ['002828.SZ','贝肯能源A股'],['300164.SZ','通源石油A股'],['300084.SZ','海默科技A股'],
        ['300023.SZ','宝德股份A股'],
        
        #股票：汽车
        ['F','福特汽车'],['GM','通用汽车'],['TSLA','特斯拉'],
        ['7203.T','日股丰田汽车'],['7267.T','日股本田汽车'],['7201.T','日股日产汽车'], 
        ['7270.T','日股斯巴鲁汽车'],['7269.T','日股铃木汽车'],['7261.T','日股马自达汽车'], 
        ['7211.T','日股三菱汽车'], 
        ['DAI.DE','德国奔驰汽车'],['MBG.DE','梅赛德斯奔驰集团'],['BMW.DE','宝马汽车'],
        ['XPEV','小鹏汽车'],['LI','理想汽车'],['00175.HK','吉利汽车'],
        ['02238.HK','广汽'],['000625.SZ','长安汽车'],['600104.SS','上汽'],['NIO','蔚来汽车'],        
        
        #股票：制药
        ['LLY','礼来制药'],['Eli','礼来制药'],
        ['JNJ','强生制药'],['Johnson','强生制药'],
        ['VRTX','福泰制药'],['Vertex','福泰制药'],
        ['PFE','辉瑞制药'],['Pfizer','辉瑞制药'],
        ['MRK','默克制药'],['Merck','默克制药'],
        ['NVS','诺华制药'],['Novartis','诺华制药'],
        ['AMGN','安进制药'],['Amgen','安进制药'],
        ['SNY','赛诺菲制药'],['Sanofi','赛诺菲制药'],
        ['AZN','阿斯利康制药'],['MRNA','莫德纳生物'],
        ['NBIX','神经分泌生物'],['Neurocrine','神经分泌生物'],
        ['REGN','再生元制药'],['Regeneron','再生元制药'],
        ['PRGO','培瑞克制药'],['Perrigo','培瑞克制药'],
        ['TEVA','梯瓦制药'],['SNDX','Syndax制药'],
        ['BPTH','Bio-Path'],
        
        #股票：教育、视频
        ['BILI','哔哩哔哩'],['TAL','好未来'],['EDU','新东方'],['RYB','红黄蓝'],       
        ['IQ','爱奇艺'],['HUYA','虎牙'],['01024.HK','快手港股'],
        
        #股票：服饰，鞋帽，化妆品，体育，奢侈品
        ['002612.SZ','朗姿股份'],['002832.SZ','比音勒芬'],
        ['002291.SZ','星期六'],['600398.SS','海澜之家'],
        ['600400.SS','红豆股份'],['300005.SZ','探路者'],
        ['603877.SS','太平鸟'],['002563.SZ','森马服饰'],
        ['002154.SZ','报喜鸟'],['002029.SZ','七匹狼'],
        ['601566.SS','九牧王'],['600107.SS','美尔雅'],
        ['603116.SS','红蜻蜓'],['002503.SZ','搜于特'],
        ['002193.SZ','如意集团'],['603001.SS','奥康国际'],
        ['300979.SZ','C华利'],['002269.SZ','美邦服饰'],
        ['600884.SS','杉杉股份'],['600177.SS','雅戈尔'],
        ['300526.SZ','中潜股份'],['601718.SS','际华集团'],
        ['603157.SS','拉夏贝尔A股'],['600295.SS','鄂尔多斯'],
        ['002293.SZ','罗莱生活'],['603587.SS','地素时尚'],
        ['002404.SZ','嘉欣丝绸'],['600612.SS','老凤祥'],
        ['300577.SZ','开润股份'],['600137.SS','浪莎股份'],
        
        ['02331.HK','李宁'],['02020.HK','安踏体育'],['01368.HK','特步国际'],
        ['01361.HK','361度'],['06116.HK','拉夏贝尔港股'],['03306.HK','江南布衣'],
        ['02298.HK','都市丽人'],['01388.HK','安莉芳'],['01749.HK','杉杉品牌'],
        ['01234.HK','中国利郎'],['02030.HK','卡宾'],['00709.HK','佐丹奴国际'],
        ['03998.HK','波司登'],['00592.HK','堡狮龙'],['02313.HK','申洲国际'],
        ['06110.HK','滔博'],['03813.HK','宝胜国际'],['06288.HK','迅销'],
        ['01913.HK','普拉达'],['00551.HK','裕元集团'],['02399.HK','虎都'],
        ['02232.HK','晶苑国际'],['01146.HK','中国服饰控股'],
        
        ['4911.T','资生堂(日)'],['4452.T','花王(日)'],
        ['9983.T','优衣库(日)'],['7453.T','无印良品(日)'],   
        
        ['CDI.PA','法国迪奥'],['DIO.F','法国迪奥'],['HMI.F','法国爱马仕'],
        ['BNP.PA','法国巴黎银行'],
        
        #股票：其他
        ['PG','宝洁'],['KO','可口可乐'],['PEP','百事可乐'],
        ['BRK.A','伯克希尔'],['BRK.B','伯克希尔'],['Berkshire','伯克希尔'],
        ['COST','好事多'],['WMT','沃尔玛'],['DIS','迪士尼'],['BA','波音'],
        ['DPW','Ault Global'],['RIOT','Riot Blockchain'],['MARA','Marathon Digital'],['NCTY','9th City'],

        ['000651.SZ','格力电器A股'],['000333.SZ','美的集团A股'],['601127.SS','赛力斯'],

        ['00992.HK','港股联想'],['LENOVO GROUP','联想集团'],
        ['01810.HK','港股小米'],
        ['01166.HK','港股星凯控股'],['00273.HK','港股茂宸集团'],

        ['2330.TW','台积电'],['2317.TW','鸿海精密'],['2474.TW','可成科技'],
        ['3008.TW','大立光'],['2454.TW','联发科'],  
        
        ['6758.T','日本索尼'],['6758.JP','日本索尼'],['7203.JP','日本丰田汽车'],
        
        ['005930.KS','三星电子'],
        
        ['TCS.NS','印度塔塔咨询'],['ULVR.UK','英国联合利华'],
        ['LOR.DE','巴黎欧莱雅'],['OR.PA','巴黎欧莱雅'],
        
        ['002594.SZ','比亚迪A股'],['01211.HK','比亚迪港股'],['81211.HK','比亚迪港股(人民币)'],
        ['00700.HK','腾讯港股'],['80700.HK','腾讯港股(人民币)'],
        ['09988.HK','阿里巴巴港股'],['89988.HK','阿里巴巴港股(人民币)'],
        ['03690.HK','美团港股'],['83690.HK','美团港股(人民币)'],
        ['09618.HK','京东集团港股'],['89618.HK','京东集团港股(人民币)'],
        ['09888.HK','百度集团港股'],['89888.HK','百度集团港股(人民币)'],
        ['02020.HK','安踏体育港股'],['82020.HK','安踏体育港股(人民币)'],
        ['01810.HK','小米集团港股'],['81810.HK','小米集团港股(人民币)'],
        ['01024.HK','快手港股'],['81024.HK','快手港股(人民币)'],
        ['02331.HK','李宁港股'],['82331.HK','李宁港股(人民币)'],
        ['00175.HK','吉利汽车港股'],['80175.HK','吉利汽车港股(人民币)'],
        ['00992.HK','联想集团港股'],['80992.HK','联想集团港股(人民币)'],
        ['00020.HK','商汤港股'],['80020.HK','商汤港股(人民币)'],
        ['02333.HK','长城汽车港股'],['82333.HK','长城汽车港股(人民币)'],
        ['00941.HK','中国移动港股'],['80941.HK','中国移动港股(人民币)'],
        ['00883.HK','中国海油港股'],['80883.HK','中国海油港股(人民币)'],
        ['02318.HK','中国平安港股'],['82318.HK','中国平安港股(人民币)'],
        ['02388.HK','中银香港港股'],['82388.HK','中银香港港股(人民币)'],
        ['06618.HK','京东健康港股'],['86618.HK','京东健康港股(人民币)'],
        
        # 英国知名上市公司
        ['SHEL.UK','壳牌石油'],['AZN.UK','阿斯利康'],['HSBA.UK','汇丰控股(英)'],
        ['HSBC.US','汇丰集团'],['ULVR.UK','联合利华'],['RIO.UK','力拓集团'],['HSBA.L','汇丰控股(英)'],
        ['BP.UK','英国石油'],['BATS.UK','英美烟草'],['GSK.UK','葛兰素史克'],
        ['LLOY.UK','劳埃德银行'],['PRU.UK','英国保诚'],['HLN.UK','赫利昂集团'],
        ['AAL.UK','英美资源集团'],['CPG.UK','金巴斯集团'],['NG.UK','英国电网'],
        ['RKT.UK','利洁时集团'],['REL.UK','励讯集团'],['DGE.UK','帝亚吉欧酒业'],
        ['TLW.UK','英国塔洛石油'],['HBR.UK','英国哈勃能源'],
        
        # 荷兰知名上市公司
        ['ASML.US','阿斯麦'],['0QB8.UK','阿斯麦'],
        ['1TY.DE','Prosus'],['STLA.US','斯特兰蒂斯'],
        ['HEIA.AS','喜力啤酒'],['0O26.UK','喜力啤酒'],
        ['NXPI.US','恩智浦半导体'],['ING.US','荷兰国际集团'],
        ['AHOG.DE','阿霍德·德尔海兹'],['ARGX.US','Argenx制药'],['WOSB.DE','荷兰威科集团'],
        ['EYX.DE','Exor投资集团'],['ARGX.US','Argenx制药'],['WOSB.DE','荷兰威科集团'],
        ['1N8.DE','Adyen支付'],['AVS.DE','ASM国际'],
        ['PHG.US','飞利浦美股'],['0LNG.UK','荷兰飞利浦'],
        
        # 德国知名上市公司
        ['SAP.DE','德国思爱普'],['SAP','思爱普'],
        ['SIE.DE','西门子集团'],
        ['P911.DE','保时捷'],['0JHU.UK','保时捷'],
        ['DTE.DE','德国电信'],['ALV.DE','德国安联集团'],
        ['MBG.DE','奔驰汽车'],['0NXX.UK','奔驰汽车'],
        ['BMW.DE','宝马汽车'],['MRK.DE','默克制药'],['SHL.DE','西门子医疗'],
        ['DHL.DE','德国邮政敦豪集团'],['IFX.DE','英飞凌半导体'],['BAYN.DE','拜耳制药'],
        ['RAA.DE','德国莱欣诺'],['UN01.DE','尤尼珀能源'],['BAS.DE','巴斯夫化工'],
        ['HLAG.DE','赫伯罗德海运'],['ADS.DE','阿迪达斯'],
        ['VOW.DE','大众汽车'],['VOW3.DE','大众汽车'],
        
        # 瑞典知名上市公司
        ['ATCO-A.ST','阿特拉斯-科普柯A'],['VOLCAR-B.ST','沃尔沃轿车'],['0AAK.UK','沃尔沃轿车'],
        ['VOLV-A.ST','沃尔沃集团A'],['VOLV-B.ST','沃尔沃集团B'],
        ['HEXA-B.ST','海克斯康科技B'],['SPOT.US','Spotify科技'],
        ['SAND.ST','山特维克机械'],['EQT.UK','EQT投资集团'],['SEB-A.ST','北欧斯安银行A'],
        ['ASSA-B.ST','亚萨合莱安防B'],['INVE-A.ST','银瑞达集团A'],['EQT.ST','EQT投资集团'],
        ['0RQ6.IL','进化博彩AB'],['0RQ6.UK','进化博彩AB'],
        
        
        # 捷克、匈牙利、波兰知名上市公司
        ['CEZ.PL','捷克CEZ能源'],['0NZF.UK','捷克CEZ能源'],
        ['KOMB.PR','捷克科梅尔奇尼银行'],['0IKH.UK','捷克科梅尔奇尼银行'],
        ['OTP.HU','匈牙利OTP银行'],
        ['MOL.HU','匈牙利MOL能源'],['PZU.PL','波兰PZU保险'],['PEO.PL','波兰Pekao银行'],
        ['PZU.WA','波兰PZU保险'],['CEZ.PR','捷克CEZ能源'],
        
        # 希腊知名上市公司
        ['OPAP.AT','希腊博彩公司'],['EUROB.AT','希腊欧洲银行'],['ETE.AT','希腊国家银行'],
        ['TENERGY.AT','希腊泰纳能源'],['CCH.UK','希腊可乐灌装公司'],
        
        # 其他知名欧洲上市公司
        ['AKRBP.OL','挪威AkerBP石油'],
        ['GZF.DE','法国燃气苏伊士集团'],['0LD0.UK','法国燃气苏伊士集团'],
        ['ENI.DE','意大利埃尼能源'],
        ['EQNR.US','挪威国家石油公司'],['0M2Z.UK','挪威国家石油公司'],
        ['OMV.DE','奥地利石油天然气集团'],['0MKH.UK','奥地利石油天然气集团'],
        ['REP.DE','西班牙雷普索尔公司'],['0NQG.UK','西班牙雷普索尔公司'],
        ['TTE.US','法国道达尔公司'],['0RDT.UK','法拉利汽车'],
        ['TSM.US','台积电美股'],
        
        
        #股票：指数==============================================================
        ['000300.SS','沪深300指数'],['399300.SS','沪深300指数'],
        ['000001.SS','上证综合指数'],['399001.SZ','深证成份指数'],
        ['000016.SS','上证50指数'],['000132.SS','上证100指数'],
        ['000133.SS','上证150指数'],['000010.SS','上证180指数'],
        ['000688.SS','科创板50指数'],['000043.SS','上证超大盘指数'],
        ['000044.SS','上证中盘指数'],['000046.SS','上证中小盘指数'],
        ['000045.SS','上证小盘指数'],['000004.SS','上证工业指数'],
        ['000005.SS','上证商业指数'],['000006.SS','上证地产指数'],
        ['000007.SS','上证公用指数'],['000038.SS','上证金融指数'],
        ['000057.SS','上证全指成长指数'],['000058.SS','上证全指价值指数'],
        ['000019.SS','上证治理指数'],['000048.SS','上证责任指数'],
        ['000015.SS','上证红利指数'],['899050.BJ','北证50指数'],
        ['399006.SZ','创业板指数'],['399975.SZ','中证证券公司指数'],
        
        ['399289.SZ','国证中财绿色债券指数'],['399481.SZ','国证企业债指数'],
        ['399302.SZ','深证公司债综合指数'],['399301.SZ','深证信用债综合指数'],
        
        ['000002.SS','上证A股指数'],['000003.SS','上证B股指数'],
        ['399107.SZ','深证A股指数'],['399108.SZ','深证B股指数'],
        ['399106.SZ','深证综合指数'],['399004.SZ','深证100指数'],
        ['399012.SZ','创业板300指数'],['399991.SZ','一带一路指数'],
        
        ['399232.SZ','深证采矿业指数'],['399233.SZ','深证制造业指数'],
        ['399234.SZ','深证水电煤气指数'],['399236.SZ','深证批发零售指数'],
        ['399237.SZ','深证运输仓储指数'],['399240.SZ','深证金融业指数'],
        ['399241.SZ','深证房地产指数'],['399244.SZ','深证公共环保指数'],
        ['399997.SZ','中证白酒指数'],['399913.SZ','沪深300医药指数'],
        ['399933.SZ','中证医药指数'],
        
        ['000903.SS','中证100指数'],['399903.SZ','中证100指数'],
        ['000904.SS','中证200指数'],['399904.SZ','中证200指数'],
        ['000905.SS','中证500指数'],['399905.SZ','中证500指数'],
        ['000907.SS','中证700指数'],['399907.SZ','中证700指数'],
        ['000906.SS','中证800指数'],['399906.SZ','中证800指数'],
        ['000852.SS','中证1000指数'],['399852.SZ','中证1000指数'],
        ['000985.SS','中证全指指数'],['399985.SZ','中证全指指数'],
        ['399808.SZ','中证新能指数'],['399986.SZ','中证银行指数'],
        
        ['000012.SS','上证国债指数'],['000013.SS','上证企业债指数'],
        ['000022.SS','上证公司债指数'],['000061.SS','上证企债30指数'],
        ['000116.SS','上证信用债100指数'],['000101.SS','上证5年期信用债指数'],
        ['000011.SS','上证基金指数'],['000139.SS','上证可转债指数'],
        ['000832.SS','中证转债指数'],['399307.SZ','深证转债指数'],
        ['000116.SS','上证信用债指数'],['399413.SZ','国证转债综合指数'],

        ['^GSPC','标普500指数'],['^SPX','标普500指数'],
        ['^DJI','道琼斯工业指数'],
        ['WISGP.SI','富时新加坡指数'], ['^STI','新加坡海峡时报指数'],
        ['^IXIC','纳斯达克综合指数'],
        ['^FTSE','英国富时100指数'],['^FTM','英国富时250指数'],
        ['^NKX','日经225指数'],['^N100','泛欧100指数'],
        ['^FMIB','富时意大利指数'],
        ['^GSPTSE','多伦多综合指数'],['^MXX','墨西哥IPC指数'],
        ['^NDX','纳斯达克100指数'],['^NDQ','纳斯达克综合指数'],
        ['^BET','罗马尼亚布加勒斯特指数'],
        ['^BUX','匈牙利布达佩斯指数'],['^PX','捷克布拉格PX指数'],
        ['^SAX','斯洛伐克SAX指数'],
        ['WIG.PL','波兰华沙WIG指数'],
        ['WIG20.PL','波兰华沙WIG20指数'],
        ['WIG30.PL','波兰华沙WIG30指数'],
        ['^OMXS','瑞典斯德哥尔摩指数'],['^DKDOW','道琼斯丹麦指数'],
        ['^HEX','芬兰赫尔辛基指数'],['^OMXV','立陶宛维尔纽斯指数'],
        ['^OMXR','拉脱维亚里加指数'],['^OMXT','爱沙尼亚塔林指数'],
        ['^ICEX','冰岛综合指数'],['^OMXC25','丹麦哥本哈根25指数'],
        ['^FMIB','富时意大利指数'],
        ['^IBEX','西班牙IBEX指数'],['^OSEAX','挪威奥斯陆指数'],
        ['^SMI','瑞士SMI指数'],['^MOEX','俄罗斯莫斯科指数(卢布计价)'],
        ['^UX','乌克兰UX指数'],['^RTS','俄罗斯市值加权指数(美元计价)'],
        ['^AEX','荷兰阿姆斯特丹指数'],['^ATH','希腊雅典综合指数'],
        ['^BEL20','比利时20指数'],['^BVSP','巴西圣保罗指数'],
        ['^MXX','墨西哥IPC指数'],['^IPSA','智利IPSA指数'],
        ['^JCI','印尼雅加达指数'],['^KOSPI','韩国综合指数'],
        ['^KLCI','马来西亚吉隆坡指数'],
        ['^MRV','阿根廷MERVAL指数'],['^MERV','阿根廷MERVAL指数'],['M.BA','阿根廷MERVAL指数'],
        ['^MT30','沙特TASI指数'],['^NZ50','新西兰50指数'],
        ['^PSI20','葡萄牙PSI20指数'],['^PSEI','菲律宾PSEi指数'],
        ['^SET','泰国SET指数'],['^STI','新加坡海峡时报指数'],
        ['^SOFIX','保加利亚索菲亚指数'],['^TWSE','中国台湾加权指数'],
        ['^IPC','墨西哥证交所指数'],['^BVP','巴西圣保罗指数'],
        
        ['^NYA','纽交所综合指数'],['^XAX','美交所综合指数'],
        ['^STOXX50E','欧洲斯托克50指数'],['^STOXX','欧洲斯托克600指数'],
        ['^N100','泛欧Euronext100指数'],['^BFX','比利时20指数'],
        ['^AXJO','澳洲ASX200指数'],['^AORD','澳洲综合指数'],['^AOR','澳洲综合指数'],
        ['^JKSE','印尼雅加达综合指数'],['^TSX','加拿大TSX综合指数'],
        ['^BVSP','巴西圣保罗指数'],['^MXX','墨西哥IPC指数'],
        ['^TA125.TA','特拉维夫125指数'],
        ['^JN0U.JO','JSE南非40指数'],['LDIIZA.M','南非领先指数'],
        ['FXNAX','Fidelity美债指数'],
        
        ['IB01.UK','iShares美债0-1年期ETF'],['TRS3.UK','SPDR美债1-3年期ETF'],
        ['TRS5.UK','SPDR美债3-7年期ETF'],['TRSX.UK','SPDR美债7-10年期ETF'],
        ['LUTR.UK','SPDR美债10+年期ETF'],
        
        # 除了^FTW5000，其他的貌似缺数据
        ['^FTW5000','威尔希尔5000全市场指数'],
        ['^W4500','威尔希尔4500指数'],
        ['^FTW2500','威尔希尔2500指数'],
        ['^FTWUSG','威尔希尔美国巨型公司指数'],['^FTWUSL','威尔希尔美国大型公司指数'],
        ['^FTWUSD','威尔希尔美国中型公司指数'],['^FTWUSS','威尔希尔美国小型公司指数'],
        ['^FTWUSO','威尔希尔美国微型公司指数'],
        
        ['FVTT.FGI','富时越南指数'],['SWMCX','嘉信美国中盘股指数ETF'],
        ['^RUT','罗素2000指数'],['^RUI','罗素1000指数'],
        
        ['^HSI','恒生指数'],['^N225','日经225指数'],
        ['WIKOR.FGI','富时韩国指数'],['^KS11','韩国综合指数'],
        ['^KOSPI','韩国综合指数'],
        ['^BSESN','孟买敏感指数'],['^SNX','孟买敏感指数'],['^NSEI','印度国交50指数'],
        ['^FCHI','法国CAC40指数'],['^GDAXI','德国DAX指数'], 
        ['^CAC','法国CAC40指数'],['^DAX','德国DAX指数'], 
        ['^ATX','奥地利ATX指数'],
        ['IMOEX.ME','俄罗斯MOEX指数'],['^MOEX','俄罗斯MOEX指数'], 
        ['^RTS','俄罗斯RTS指数（美元标价）'],
        ['^TASI','沙特TASI指数'],
        ['TA35.TA','以色列TA35指数'],['^TA125.TA','以色列TA125指数'],
        ['^BVSP','巴西BVSP指数'],['^JNX4.JO','南非40指数'],
        ['^KLSE','吉隆坡综合指数'],['^KLCI','吉隆坡综合指数'],
        ['^JCI','雅加达综合指数'],
        ['VNM','VanEck越南指数ETF'],['^VNINDEX.VN','胡志明指数(美元计价)'],
        ['^VIX','VIX恐慌指数'],
        ['ASEA','富时东南亚ETF'],['LIT','国际锂矿与锂电池ETF'],
        
        ['^HSCE','恒生H股指数'],['^HSNC','恒生工商业指数'],['^HSNU','恒生公用行业指数'], 
        ['^TWII','中国台湾加权指数'], 
        
        ['^XU100','伊斯坦布尔100指数'], ['10TRY.B','土耳其10年期国债收益率%'],
        
        # 另类指数
        ['INDEXCF','俄罗斯MICEX指数'],
        ['RTS','俄罗斯RTS指数'],
        ['CASE','埃及CASE30指数'],
        ['VNINDEX','越南胡志明指数'],
        ['HSCEI','港股国企指数'],
        ['HSCCI','港股红筹指数'],
        ['CSEALL','斯里兰卡科伦坡全指'],
        ['UDI','美元指数'],
        ['CRB','路透CRB商品指数'],
        ['BDI','波罗的海BDI指数'],
        ['KSE100','巴基斯坦卡拉奇指数'],

        
        #债券==================================================================
        ['sh019521','15国债21'],['sz128086','国轩转债'],['sz123027','蓝晓转债'],
        ['^IRX','三个月美债收益率%'],['^FVX','五年美债收益率%'],
        ['^TNX','十年期美债收益率%'],['^TYX','三十年美债收益率%'],
        
        #基金==================================================================
        ['000595','嘉实泰和混合基金'],['000592','建信改革红利股票基金'],
        ['050111','博时信债C'],['320019','诺安货币B基金'],
        ['510580','易方达中证500ETF'],['510210.SS','上证综指ETF'],
        ["510050.SS",'华夏上证50ETF基金'],['510880.SS','上证红利ETF基金'],
        ["510180.SS",'上证180ETF基金'],['159901.SZ','深证100ETF基金'],
        ["159902.SZ",'深证中小板ETF基金'],['159901.SZ','深证100ETF基金'],
        ["159919.SZ",'嘉实沪深300ETF基金'],["510300.SS",'华泰柏瑞沪深300ETF基金'],
        
        ["159915.SZ",'易方达创业板ETF基金'],["510500.SS",'南方中证500ETF基金'],
        ["588000.SS",'华夏上证科创板50ETF基金'],
        
        ["515220.SS",'国泰中证煤炭ETF基金'],["501011.SS",'添富中证中药ETF联接(LOF)A基金'],
        ["512200.SS",'南方中证全指房地产ETF基金'],["515790.SS",'华泰柏瑞中证光伏产业ETF基金'],
        ["516970.SS",'广发中证基建工程ETF基金'],["512400.SS",'南方中证申万有色金属ETF基金'],
        ["512660.SS",'国泰中证军工ETF基金'],["159928.SZ",'汇添富中证主要消费ETF基金'],
        ["516150.SS",'嘉实中证稀土产业ETF基金'],["516110.SS",'国泰中证800汽车与零部件ETF基金'],
        ["512800.SS",'华宝中证银行ETF基金'],["515030.SS",'华夏中证新能源汽车ETF基金'],
        ["159745.SZ",'国泰中证全指建筑材料ETF基金'],["512690.SS",'鹏华中证酒ETF基金'],
        ["159869.SZ",'华夏中证动漫游戏ETF基金'],["159996.SZ",'国泰中证全指家电ETF基金'],
        ["159852.SZ",'嘉实中证软件服务ETF基金'],["515880.SS",'国泰中证全指通信设备ETF基金'],
        ["512980.SS",'广发中证传媒ETF基金'],["512170.SS",'华宝中证医疗ETF基金'],
        ["515210.SS",'国泰中证钢铁ETF基金'],["512010.SS",'易方达沪深300医药ETF基金'],
        ["159870.SZ",'鹏华中证细分化工产业ETF基金'],["512880.SS",'国泰中证全指证券公司ETF基金'],
        ["159995.SZ",'华夏国证半导体芯片ETF基金'],["159605.SZ",'广发中证海外中国互联网30(QDII-ETF)基金'],
        ["159766.SZ",'富国中证旅游主题ETF基金'],["159611.SZ",'广发中证全指电力公用事业ETF基金'],
        ["516530.SS",'银华中证现代物流ETF基金'],["516670.SS",'畜牧养殖ETF'],
        
        ["515050.SS",'华夏中证5G通信主题ETF基金'],["510810.SS",'中证上海国企ETF基金'],
        ["515900.SS",'博时央企创新驱动ETF基金'],["516680.SS",'建信中证细分有色金属产业ETF基金'],        
        
        ["513360.SS",'博时全球中国教育(QDII-ETF)基金'],["513080.SS",'华安法国CAC40ETF(QDII)基金'],
        ["513060.SS",'博时恒生医疗保健(QDII-ETF)基金'],["513030.SS",'华安德国(DAX)ETF基金'],
        ["510900.SS",'易方达恒生国企ETF基金'],["159920.SZ",'华夏恒生ETF(QDII)基金'],
        ["513330.SS",'华夏恒生互联网科技业ETF(QDII)基金'],["513050.SS",'易方达中证海外中国互联网50(QDII-ETF)基金'],
        ["513130.SS",'华泰柏瑞南方东英恒生科技(QDII-ETF)基金'],["159866.SZ",'工银瑞信大和日经225ETF(QDII)基金'],
        ["513100.SS",'国泰纳斯达克100(QDII-ETF)基金'],
        
        ["511310.SS",'富国10年国债ETF基金'],["511020.SS",'平安活跃国债ETF基金'],
        ["511260.SS",'国泰10年国债ETF基金'],["511010.SS",'国泰国债ETF'],
        ["511520.SS",'富国政金债券ETF'],["159649.SZ",'华安国开债ETF基金'],
        ["159816.SZ",'鹏华0-4年地方债ETF基金'],["511060.SS",'海富通5年地方债ETF基金'],
        ["511270.SS",'海富通10年地方债ETF基金'],["159972.SZ",'鹏华5年地方债ETF'],
        ["511220.SS",'海富通城投债ETF基金'],["511360.SS",'海富通短融ETF基金'],
        ["511030.SS",'平安公司债ETF基金'],["511180.SS",'海富通上证可转债ETF基金'],
        ["511380.SS",'博时可转债ETF基金'],
        
        ["510170.SS",'国联安上证商品ETF基金'],["159980.SZ",'大成有色金属期货ETF基金'],
        ["159985.SZ",'华夏饲料豆粕期货ETF基金'],["159981.SZ",'建信易盛能源化工期货ETF基金'],
        ["165513.SZ",'信诚全球商品ETF基金'],["159812.SZ",'前海开源黄金ETF基金'],
        ["518803.SS",'国泰黄金ETF基金'],["159937.SZ",'博时黄金ETF'],
        
        ["159003.SZ",'招商快线ETF基金'],["260102.SZ",'景顺长城货币A基金'],
        ["519888.SS",'汇添富收益快线货币A基金'],
        
        ["004972",'长城收益宝货币A基金'],["004137",'博时合惠货币B基金'],
        ["002890",'交银天利宝货币E基金'],["004417",'兴全货币B基金'],
        ["005151",'红土创新优淳货币B基金'],["001909",'创金合信货币A基金'],
        ["001821",'兴全天添益货币B基金'],["000836",'国投瑞银钱多宝货币A基金'],
        ["000700",'泰达宏利货币B基金'],["001234",'国金众赢货币基金'],
        ["100051",'富国可转债A基金'],["217022",'招商产业债券A基金'],
        
        ["910004",'东方红启恒三年持有混合A'],["011724",'东方红启恒三年持有混合B'],
        ["166301",'华商新趋势优选灵活配置混合'],["240008",'华宝收益增长混合A'],
        ["015573",'华宝收益增长混合C'],["070006",'嘉实服务增值行业混合'],
        ["162204",'泰达宏利行业混合A'],["015601",'泰达宏利行业混合C'],
        ["660015",'农银行业轮动混合A'],["015850",'农银行业轮动混合C'],
        
        ["SPY",'SPDR标普500ETF'],['SPYD','SPDR标普500股利优先ETF'],
        ["SPYG",'SPDR标普500成长优先ETF'],['SPYV','SPDR标普500价值优先ETF'],
        ["GLD",'SPDR黄金ETF'],
        ["VOO",'Vanguard标普500ETF'],['VOOG','Vanguard标普500成长优先ETF'],
        ["VOOV",'Vanguard标普500价值优先ETF'],['IVV','iShares标普500ETF'],        
        ["DGT",'SPDR Global Dow ETF'],['ICF','iShares C&S REIT ETF'], 
        #["FRI",'FT S&P REIT Index Fund'],
        ["FRI",'FT标普REIT指数基金'],
        ['IEMG','iShares核心MSCI新兴市场ETF'],    
        ['245710.KS','KINDEX越南VN30指数ETF'],['02801.HK','iShares核心MSCI中国指数ETF'],
        
        #基金REITs
        ['180201.SZ','平安广州广河REIT'],['508008.SS','国金中国铁建REIT'],
        ['508001.SS','浙商沪杭甬REIT'],['508018.SS','华夏中国交建REIT'],
        ['180202.SZ','华夏越秀高速REIT'],['508066.SS','华泰江苏交控REIT'],
        ['508021.SS','国泰君安临港创新产业园REIT'],['508056.SS','中金普洛斯REIT'],
        ['508027.SS','东吴苏园产业REIT'],['508006.SS','富国首创水务REIT'],
        ['508099.SS',' 建信中关村REIT'],['508000.SS','华安张江光大REIT'],
        ['508088.SS',' 国泰君安东久新经济REIT'],['508098.SS',' 京东仓储REIT'],
        ['180103.SZ','华夏和达高科REIT'],['180301.SZ','红土创新盐田港REIT'],
        ['180101.SZ','博时蛇口产园REIT'],['508058.SS','中金厦门安居REIT'],
        ['508068.SS','华夏北京保障房REIT'],['508077.SS','华夏基金华润有巢REIT'],
        
        ['180801.SZ','中航首钢绿能REIT'],
        ['508028.SS','中信建投国家电投新能源REIT'],['508009.SS','中金安徽交控REIT'],
        ['180401.SZ','鹏华深圳能源REIT'],
        
        
        ['FFR','富时美国REITs指数'],
        ['AMT','美国电塔REIT'],['CCI','Crown Castle REIT'],
        ['EQUIX','Equinix REIT'],['LAMR','Lamar Advertising REIT'],
        ['OUT','Outfront Media REIT'],['CIO','City Office REIT'],
        ['NYC','New York City REIT'],['REIT','ALPS Active REIT'],
        ['EARN','Ellington RM REIT'], ['VNQ','Vanguard ETF REIT'],  
        
        ['00823.HK','领展房产REIT'], ['02778.HK','冠君产业REIT'], 
        ['087001.HK','汇贤产业REIT'], ['00808.HK','泓富产业REIT'], 
        ['01426.HK','春泉产业REIT'], ['00435.HK','阳光房地产REIT'], 
        ['00405.HK','越秀房产REIT'], ['00778.HK','置富产业REIT'], 
        ['01275.HK','开元产业REIT'], ['01881.HK','富豪产业REIT'], 
        ['01503.HK','招商局商房REIT'], ['02191.HK','顺丰房托REIT'],
        
        ['3283.T','日本安博REIT'],
        
        ['C38U.SI','凯德商业信托REIT'],['N2IU.SI','枫树商业信托REIT'],
        ['T82U.SI','Suntec REIT'],['HMN.SI','雅诗阁公寓REIT'],

        #期货==================================================================
        ["HG=F",'COMEX铜矿石期货'],
        ["CL=F",'NYM原油期货'],["BZ=F",'NYM布伦特原油期货'],
        ["NG=F",'NYM天然气期货'],["MTF=F",'NYM煤炭期货'],
        ["GC=F",'COMEX黄金期货'],["MGC=F",'COMEX微型黄金期货'],
        ["SGC=F",'上海黄金期货'],
        ["6B=F",'CME英镑兑美元期货'],
        ["S=F",'CBT大豆期货'],["C=F",'CBT玉米期货'],
        ["ES=F",'CME标普500指数期货'],["YM=F",'CBT道指期货'],
        ["NQ=F",'CME纳指100期货'],["RTY=F",'罗素2000指数期货'],
        ["ZB=F",'30年期美债期货'],["ZT=F",'2年期美债期货'],
        ["ZF=F",'5年期美债期货'],["ZN=F",'10年期美债期货'],        
        
        #======================================================================
        #=新加入
        ['30YCNY.B','中国30年期国债收益率%'],['20YCNY.B','中国20年期国债收益率%'],
        ['10YCNY.B','中国10年期国债收益率%'], ['5YCNY.B','中国5年期国债收益率%'],
        ['3YCNY.B','中国3年期国债收益率%'], ['2YCNY.B','中国2年期国债收益率%'],
        ['1YCNY.B','中国1年期国债收益率%'], ['7YCNY.B','中国7年期国债收益率%'],
        
        ['30YJPY.B','日本30年期国债收益率%'],['20YJPY.B','日本20年期国债收益率%'],
        ['10YJPY.B','日本10年期国债收益率%'], ['5YJPY.B','日本5年期国债收益率%'],
        ['3YJPY.B','日本3年期国债收益率%'], ['2YJPY.B','日本2年期国债收益率%'],
        ['1YJPY.B','日本1年期国债收益率%'], ['7YJPY.B','日本7年期国债收益率%'], 
        
        ['10YKZY.B','哈萨克斯坦10年期国债收益率%'],
        
        ['30YUSY.B','美国30年期国债收益率%'],['20YUSY.B','美国20年期国债收益率%'],
        ['10YUSY.B','美国10年期国债收益率%'], ['5YUSY.B','美国5年期国债收益率%'],
        ['3YUSY.B','美国3年期国债收益率%'], ['2YUSY.B','美国2年期国债收益率%'],
        ['1YUSY.B','美国1年期国债收益率%'], ['6MUSY.B','美国半年期国债收益率%'],       
        ['3MUSY.B','美国3个月期国债收益率%'], ['1MUSY.B','美国1个月期国债收益率%'],
        ['7YUSY.B','美国7年期国债收益率%'],
        
        ['30YUKY.B','英国30年期国债收益率%'],['20YUKY.B','英国20年期国债收益率%'],
        ['10YUKY.B','英国10年期国债收益率%'], ['5YUKY.B','英国5年期国债收益率%'],
        ['3YUKY.B','英国3年期国债收益率%'], ['2YUKY.B','英国2年期国债收益率%'],
        ['1YUKY.B','英国1年期国债收益率%'], ['6MUKY.B','英国半年期国债收益率%'],       
        ['3MUKY.B','英国3个月期国债收益率%'], ['7YUKY.B','英国7年期国债收益率%'],        
        
        ['30YFRY.B','法国30年期国债收益率%'],['20YFRY.B','法国20年期国债收益率%'],
        ['10YFRY.B','法国10年期国债收益率%'], ['5YFRY.B','法国5年期国债收益率%'],
        ['3YFRY.B','法国3年期国债收益率%'], ['2YFRY.B','法国2年期国债收益率%'],
        ['1YFRY.B','法国1年期国债收益率%'], ['6MFRY.B','法国半年期国债收益率%'],       
        ['3MFRY.B','法国3个月期国债收益率%'], ['7YFRY.B','法国7年期国债收益率%'],         
        ['1MFRY.B','法国1个月期国债收益率%'],

        ['30YCAY.B','加拿大30年期国债收益率%'],['20YCAY.B','加拿大20年期国债收益率%'],
        ['10YCAY.B','加拿大10年期国债收益率%'], ['5YCAY.B','加拿大5年期国债收益率%'],
        ['3YCAY.B','加拿大3年期国债收益率%'], ['2YCAY.B','加拿大2年期国债收益率%'],
        ['1YCAY.B','加拿大1年期国债收益率%'], ['6MCAY.B','加拿大半年期国债收益率%'],       
        ['7YCAY.B','加拿大7年期国债收益率%'], 

        ['30YAUY.B','澳大利亚30年期国债收益率%'],['20YAUY.B','澳大利亚20年期国债收益率%'],
        ['10YAUY.B','澳大利亚10年期国债收益率%'], ['5YAUY.B','澳大利亚5年期国债收益率%'],
        ['3YAUY.B','澳大利亚3年期国债收益率%'], ['2YAUY.B','澳大利亚2年期国债收益率%'],
        ['1YAUY.B','澳大利亚1年期国债收益率%'], ['7YAUY.B','澳大利亚7年期国债收益率%'], 
        
        ['10YKRY.B','韩国10年期国债收益率%'],['10YVNY.B','越南10年期国债收益率%'],
        ['10YTHY.B','泰国10年期国债收益率%'],['10YSGY.B','新加坡10年期国债收益率%'],
        ['10YMYY.B','马来西亚10年期国债收益率%'],['10YIDY.B','印尼10年期国债收益率%'],
        ['10YPHY.B','菲律宾10年期国债收益率%'],['10YINY.B','印度10年期国债收益率%'],
        ['10YPKY.B','巴基斯坦10年期国债收益率%'],['10YTRY.B','土耳其10年期国债收益率%'],
        ['10YILY.B','以色列10年期国债收益率%'],['10YNZY.B','新西兰10年期国债收益率%'],
        
        ['10YEGY.B','埃及10年期国债收益率%'],['10YNGY.B','尼日利亚10年期国债收益率%'],
        ['10YZAY.B','南非10年期国债收益率%'],['10YKEY.B','肯尼亚10年期国债收益率%'],
        ['10YZMY.B','赞比亚10年期国债收益率%'],

        ['10YISY.B','冰岛10年期国债收益率%'],['10YSEY.B','瑞典10年期国债收益率%'],
        ['10YDKY.B','丹麦10年期国债收益率%'],['10YNOY.B','挪威10年期国债收益率%'],
        ['10YFIY.B','芬兰10年期国债收益率%'],['10YRUY.B','俄罗斯10年期国债收益率%'],
        ['10YNLY.B','荷兰10年期国债收益率%'],['10YBEY.B','比利时10年期国债收益率%'],
        ['10YESY.B','西班牙10年期国债收益率%'],['10YPTY.B','葡萄牙10年期国债收益率%'],
        ['10YITY.B','意大利10年期国债收益率%'],['10YCHY.B','瑞士10年期国债收益率%'],
        ['10YDEY.B','德国10年期国债收益率%'],['10YROY.B','罗马尼亚10年期国债收益率%'],
        ['10YHRY.B','克罗地亚10年期国债收益率%'],['10YCZY.B','捷克10年期国债收益率%'],
        ['10YSKY.B','斯洛伐克10年期国债收益率%'],['10YSIY.B','斯洛文尼亚10年期国债收益率%'],
        ['10YHUY.B','匈牙利10年期国债收益率%'],['10YBGY.B','保加利亚10年期国债收益率%'],
        ['10YPLY.B','波兰10年期国债收益率%'],['10YATY.B','奥地利10年期国债收益率%'],
        ['10YIEY.B','爱尔兰10年期国债收益率%'],['10YRSY.B','塞尔维亚10年期国债收益率%'],
        ['10YGRY.B','希腊10年期国债收益率%'],
        
        ['10YMXY.B','墨西哥10年期国债收益率%'],['10YBRY.B','巴西10年期国债收益率%'],
        ['10YCOY.B','哥伦比亚10年期国债收益率%'],['10YPEY.B','秘鲁10年期国债收益率%'],
        ['10YCLY.B','智利10年期国债收益率%'],


        ['INPYCN.M','中国工业生产增速%(同比)'],['INPYJP.M','日本工业生产增速%(同比)'],
        ['INPYKR.M','韩国工业生产增速%(同比)'],['INPYSG.M','新加坡工业生产增速%(同比)'],
        ['INPYMY.M','马来西亚工业生产增速%(同比)'],['INPYIN.M','印度工业生产增速%(同比)'],
        ['INPYTR.M','土耳其工业生产增速%(同比)'],
        ['INPYUK.M','英国工业生产增速%(同比)'],['INPYIE.M','爱尔兰工业生产增速%(同比)'],
        ['INPYEU.M','欧元区工业生产增速%(同比)'],['INPYFR.M','法国工业生产增速%(同比)'],
        ['INPYES.M','西班牙工业生产增速%(同比)'],['INPYPT.M','葡萄牙工业生产增速%(同比)'],
        ['INPYIT.M','意大利工业生产增速%(同比)'],['INPYGR.M','希腊工业生产增速%(同比)'],
        ['INPYNO.M','挪威工业生产增速%(同比)'],
        ['INPYLT.M','立陶宛工业生产增速%(同比)'],
        ['INPYDE.M','德国工业生产增速%(同比)'],['INPYAT.M','奥地利工业生产增速%(同比)'],
        ['INPYCH.M','瑞士工业生产增速%(同比)'],
        ['INPYPL.M','波兰工业生产增速%(同比)'],['INPYRO.M','罗马尼亚工业生产增速%(同比)'],
        ['INPYHU.M','匈牙利工业生产增速%(同比)'],['INPYCZ.M','捷克工业生产增速%(同比)'],
        ['INPYSK.M','斯洛伐克工业生产增速%(同比)'],
        ['INPYUS.M','美国工业生产增速%(同比)'],['INPYMX.M','墨西哥工业生产增速%(同比)'],
        ['INPYBR.M','巴西工业生产增速%(同比)'],
        
        
        ['RSAYCN.M','中国零售业增长率%(同比)'],['RSAYBR.M','巴西零售业增长率%(同比)'],
        ['RSAYCZ.M','捷克零售业增长率%(同比)'],['RSAYCH.M','瑞士零售业增长率%(同比)'],
        ['RSAYCA.M','加拿大零售业增长率%(同比)'],['RSAYDE.M','德国零售业增长率%(同比)'],
        ['RSAYDK.M','丹麦零售业增长率%(同比)'],['RSAYEU.M','欧元区零售业增长率%(同比)'],
        ['RSAYES.M','西班牙零售业增长率%(同比)'],['RSAYIT.M','意大利零售业增长率%(同比)'],
        ['RSAYIE.M','爱尔兰零售业增长率%(同比)'],['RSAYKR.M','韩国零售业增长率%(同比)'],
        ['RSAYMX.M','墨西哥零售业增长率%(同比)'],['RSAYNO.M','挪威零售业增长率%(同比)'],
        ['RSAYNL.M','荷兰零售业增长率%(同比)'],['RSAYPT.M','葡萄牙零售业增长率%(同比)'],
        ['RSAYPL.M','波兰零售业增长率%(同比)'],['RSAYRO.M','罗马尼亚零售业增长率%(同比)'],
        ['RSAYTR.M','土耳其零售业增长率%(同比)'],['RSAYUS.M','美国零售业增长率%(同比)'],
        ['RSAYUK.M','英国零售业增长率%(同比)'],['RSAYZA.M','南非零售业增长率%(同比)'],
        ['RSAYSE.M','瑞典零售业增长率%(同比)'],['RSAYSG.M','新加坡零售业增长率%(同比)'],
        ['RSAYLT.M','立陶宛零售业增长率%(同比)'],
        
        ['RTTYGR.M','希腊零售业增长率%(同比)'],['RTTYJP.M','日本零售业增长率%(同比)'],
        ['RTTYSK.M','斯洛伐克零售业增长率%(同比)'],
        
        #======================================================================
        # 白酒行业
        ['603589.SS','口子窖'],['000568.SZ','泸州老窖'],['000858.SZ','五粮液'],
        ['600519.SS','贵州茅台'],['000596.SZ','古井贡酒'],['000799.SZ','酒鬼酒'],
        ['600809.SS','山西汾酒'],['600779.SS','水井坊'],['600559.SS','老白干酒'],

        # 房地产行业
        ['000002.SZ','万科A'],['600048.SS','保利发展'],['600340.SS','华夏幸福'],
        ['000031.SZ','大悦城'],['600383.SS','金地集团'],['600266.SS','城建发展'],
        ['600246.SS','万通发展'],['600606.SS','绿地控股'],['600743.SS','华远地产'],
        ['000402.SZ','金融街'],['000608.SZ','阳光股份'],['600376.SS','首开股份'],
        ['000036.SZ','华联控股'],['000620.SZ','新华联'],['600663.SS','陆家嘴'],

        # 银行业
        ['601328.SS','交通银行'],['601988.SS','中国银行'],['600015.SS','华夏银行'],
        ['601398.SS','工商银行'],['601169.SS','北京银行'],['601916.SS','浙商银行'],
        ['601288.SS','农业银行'],['601229.SS','上海银行'],['600016.SS','民生银行'],
        ['601818.SS','光大银行'],['601658.SS','邮储银行'],['600000.SS','浦发银行'],
        ['601939.SS','建设银行'],['601998.SS','中信银行'],['601166.SS','兴业银行'],
        ['600036.SS','招商银行'],['002142.SZ','宁波银行'],['000001.SZ','平安银行'],

        # 纺织服装行业
        ['002612.SZ','朗姿股份'],['601566.SS','九牧王'],['002269.SZ','美邦服饰'],
        ['600398.SS','海澜之家'],['600137.SS','浪莎股份'],['603001.SS','奥康国际'],
        ['603116.SS','红蜻蜓'],['002291.SZ','星期六'],['002832.SZ','比音勒芬'],
        ['600400.SS','红豆股份'],['300005.SZ','探路者'],['603877.SS','太平鸟'],
        ['002563.SZ','森马服饰'],['002154.SZ','报喜鸟'],['600177.SS','雅戈尔'],
        ['002029.SZ','七匹狼'],

        # 物流行业
        ['002352.SZ','顺丰控股'],['002468.SZ','申通快递'],['600233.SS','圆通速递'],
        ['002120.SZ','韵达股份'],['603128.SS','华贸物流'],['603056.SS','德邦股份'],
        ['601598.SS','中国外运'],['603967.SS','中创物流'],['603128.SS','华贸物流'],

        # 券商行业
        ['601995.SS','中金公司'],['601788.SS','光大证券'],['300059.SZ','东方财富'],
        ['600030.SS','中信证券'],['601878.SS','浙商证券'],['600061.SS','国投资本'],
        ['600369.SS','西南证券'],['600837.SS','海通证券'],['601211.SS','国泰君安'],
        ['601066.SS','中信建投'],['601688.SS','华泰证券'],['000776.SZ','广发证券'],
        ['000166.SZ','申万宏源'],['600999.SS','招商证券'],['002500.SZ','山西证券'],
        ['601555.SS','东吴证券'],['000617.SZ','中油资本'],['600095.SS','湘财股份'],
        ['601519.SS','大智慧'],

        # 中国啤酒概念股
        ['600600.SS','青岛啤酒'],['600132.SS','重庆啤酒'],['002461.SZ','珠江啤酒'],
        ['000729.SZ','燕京啤酒'],['600573.SS','惠泉啤酒'],['000929.SZ','兰州黄河'],
        ['603076.SS','乐惠国际'],

        # 建筑工程概念股
        ['601186.SS','中国铁建'],['601668.SS','中国建筑'],['601800.SS','中国交建'],
        ['601789.SS','宁波建工'],['601669.SS','中国电建'],['000498.SZ','山东路桥'],
        ['600170.SS','上海建工'],['600248.SS','陕西建工'],['600502.SS','安徽建工'],
        ['600284.SS','浦东建设'],['603815.SS','交建股份'],['600039.SS','四川路桥'],

        # 民用航空概念股
        ['600221.SS','海南航空'],['603885.SS','吉祥航空'],['600115.SS','中国东航'],
        ['600029.SS','南方航空'],['601021.SS','春秋航空'],['601111.SS','中国国航'],
        ['002928.SZ','华夏航空'],

        # 家电概念股
        ['600690.SS','海尔智家'],['600060.SS','海信视像'],['000333.SZ','美的集团'],
        ['000404.SZ','长虹华意'],['000651.SZ','格力电器'],['000521.SZ','长虹美菱'],
        ['603868.SS','飞科电器'],['600839.SS','四川长虹'],['000921.SZ','海信家电'],
        ['002035.SZ','华帝股份'],['002242.SZ','九阳股份'],['600336.SS','澳柯玛'],
        ['600854.SS','春兰股份'],['000418.SZ','小天鹅A'],['002508.SZ','老板电器'],
        ['000810.SZ','创维数字'],['603551.SS','奥普家居'],['002959.SZ','小熊电器'],
        ['000100.SZ','TCL科技'],['002032.SZ','苏泊尔'],['000016.SZ','深康佳A'],
        ['600690.SS','青岛海尔'],['000541.SZ','佛山照明'],['603515.SS','欧普照明'],

        # 体育用品概念股
        ['02020.HK','安踏体育'],['02331.HK','李宁'],['01368.HK','特步国际'],
        ['01361.HK','361度'],['ADS.DE','ADIDAS'],['NKE','NIKE'],
        ['8022.T','MIZUNO'],['PUM.DE','PUMA SE'],['FILA.MI','FILA'],
        ['SKG.L','Kappa'],['7936.T','ASICS'],

        # 新加坡著名股票
        ['D05.SI','星展银行DBS'],['Z74.SI','新加坡电信'],['O39.SI','华侨银行'],
        ['U11.SI','大华银行'],['C6L.SI','新加坡航空'],['CC3.SI','Starhub'],
        ['S08.SI','新加坡邮政'],['F34.SI','WILMAR'],['C31.SI','CapitaLand'],  
        
        # stooq: CPI/PPI/GDP/PMI/汇率数据
        # 需要修改：
        # 找到目录C:\Users\Peter\anaconda3\Lib\site-packages\pandas_datareader\
        # 打开stooq.py中的函数def _get_params(self, symbol, country="US")
        # 在函数列表中加入一项"m"即可避免自动在ticker加上后缀.us的问题
        # 或者使用fix_package()函数自动修正
        ['CPIYKR.M','韩国CPI(同比增速%)'],
        ['CPIYUK.M','英国CPI(同比增速%)'],['CPIYDE.M','德国CPI(同比增速%)'],
        ['CPIYJP.M','日本CPI(同比增速%)'],['CPIYCN.M','中国CPI(同比增速%)'],
        ['CPIYUS.M','美国CPI(同比增速%)'],['CPIYPL.M','波兰CPI(同比增速%)'],
        ['CPIYFR.M','法国CPI(同比增速%)'],['CPIYPH.M','菲律宾CPI(同比增速%)'],
        ['CPIYMY.M','马来西亚CPI(同比增速%)'],['CPIYSG.M','新加坡CPI(同比增速%)'],
        ['CPIYAU.M','澳大利亚CPI(同比增速%)'],['CPIYNZ.M','新西兰CPI(同比增速%)'],
        ['CPIYCA.M','加拿大CPI(同比增速%)'],['CPIYMX.M','墨西哥CPI(同比增速%)'],
        ['CPIYBR.M','巴西CPI(同比增速%)'],['CPIYSE.M','瑞典CPI(同比增速%)'],
        ['CPIYNO.M','挪威CPI(同比增速%)'],['CPIYDK.M','丹麦CPI(同比增速%)'],
        ['CPIYIS.M','冰岛CPI(同比增速%)'],['CPIYCH.M','瑞士CPI(同比增速%)'],
        ['CPIYNL.M','荷兰CPI(同比增速%)'],['CPIYIT.M','意大利CPI(同比增速%)'],
        ['CPIYGR.M','希腊CPI(同比增速%)'],['CPIYES.M','西班牙CPI(同比增速%)'],
        ['CPIYIE.M','爱尔兰CPI(同比增速%)'],['CPIYAT.M','奥地利CPI(同比增速%)'],
        ['CPIYCZ.M','捷克CPI(同比增速%)'],['CPIYSK.M','斯洛伐克CPI(同比增速%)'],
        ['CPIYRO.M','罗马尼亚CPI(同比增速%)'],['CPIYHU.M','匈牙利CPI(同比增速%)'],
        

        ['PPIYKR.M','韩国PPI(同比增速%)'],['PPIYSK.M','斯洛伐克PPI(同比增速%)'],
        ['PPIYUK.M','英国PPI(同比增速%)'],['PPIYDE.M','德国PPI(同比增速%)'],
        ['PPIYJP.M','日本PPI(同比增速%)'],['PPIYCN.M','中国PPI(同比增速%)'],
        ['PPIYUS.M','美国PPI(同比增速%)'],['PPIYPL.M','波兰PPI(同比增速%)'],
        
        ['GDPYUS.M','美国GDP(同比增速%)'],['GDPQUS.M','美国GDP(季度环比增速%)'],
        ['GDPYCN.M','中国GDP(同比增速%)'],
        ['GDPYSG.M','新加坡GDP(同比增速%)'],['GDPQSG.M','新加坡GDP(季度环比增速%)'],
        ['GDPYDE.M','德国GDP(同比增速%)'],['GDPQDE.M','德国GDP(季度环比增速%)'],
        ['GDPYAU.M','澳大利亚GDP(同比增速%)'],['GDPQAU.M','澳大利亚GDP(季度环比增速%)'],
        ['GDPYJP.M','日本GDP(同比增速%)'],['GDPQJP.M','日本GDP(季度环比增速%)'],
        ['GDPYUK.M','英国GDP(同比增速%)'],['GDPQUK.M','英国GDP(季度环比增速%)'],
        ['GDPYMY.M','马来西亚GDP(同比增速%)'],['GDPQMY.M','马来西亚GDP(季度环比增速%)'],
        ['GDPYKR.M','韩国GDP(同比增速%)'],['GDPQKR.M','韩国GDP(季度环比增速%)'],
        ['GDPYTR.M','土耳其GDP(同比增速%)'],['GDPQTR.M','土耳其GDP(季度环比增速%)'],
        ['GDPYNZ.M','新西兰GDP(同比增速%)'],
        ['GDPYIN.M','印度GDP(同比增速%)'],
        ['GDPYZA.M','南非GDP(同比增速%)'],
        ['GDPYMX.M','墨西哥GDP(同比增速%)'],
        ['GDPYBR.M','巴西GDP(同比增速%)'],
        ['GDPYIE.M','爱尔兰GDP(同比增速%)'],
        ['GDPYBE.M','比利时GDP(同比增速%)'],
        ['GDPYNL.M','荷兰GDP(同比增速%)'],
        ['GDPYPT.M','葡萄牙GDP(同比增速%)'],
        ['GDPYES.M','西班牙GDP(同比增速%)'],
        ['GDPYGR.M','希腊GDP(同比增速%)'],
        ['GDPYIT.M','意大利GDP(同比增速%)'],
        ['GDPYSE.M','瑞典GDP(同比增速%)'],
        ['GDPYIS.M','冰岛GDP(同比增速%)'],
        ['GDPYDK.M','丹麦GDP(同比增速%)'],
        ['GDPYPL.M','波兰GDP(同比增速%)'],
        ['GDPYCZ.M','捷克GDP(同比增速%)'],
        ['GDPYSK.M','斯洛伐克GDP(同比增速%)'],
        ['GDPYHU.M','匈牙利GDP(同比增速%)'],['GDPYRO.M','罗马尼亚GDP(同比增速%)'],
        ['GDPYAT.M','奥地利GDP(同比增速%)'],
        ['GDPYCH.M','瑞士GDP(同比增速%)'],
        ['GDPQFR.M','法国GDP(季度环比增速%)'],
        
        ['PMMNDE.M','德国PMI(制造业)'],['PMMNUS.M','美国PMI(制造业)'],
        ['PMMNEU.M','欧元区PMI(制造业)'],['PMMNFR.M','法国PMI(制造业)'],
        ['PMMNUK.M','英国PMI(制造业)'],['PMMNCN.M','中国PMI(制造业)'],
        ['PMMNJP.M','日本PMI(制造业)'],['PMMNKR.M','韩国PMI(制造业)'],
        ['PMMNSG.M','新加坡PMI(制造业)'],['PMMNMY.M','马来西亚PMI(制造业)'],
        ['PMMNIN.M','印度PMI(制造业)'],['PMMNTR.M','土耳其PMI(制造业)'],
        ['PMMNZA.M','南非PMI(制造业)'],['PMMNMX.M','墨西哥PMI(制造业)'],
        ['PMMNBR.M','巴西PMI(制造业)'],['PMMNIE.M','爱尔兰PMI(制造业)'],
        ['PMMNNL.M','荷兰PMI(制造业)'],['PMMNSE.M','瑞典PMI(制造业)'],
        ['PMMNNO.M','挪威PMI(制造业)'],['PMMNES.M','西班牙PMI(制造业)'],
        ['PMMNIT.M','意大利PMI(制造业)'],['PMMNGR.M','希腊PMI(制造业)'],
        ['PMMNAT.M','奥地利PMI(制造业)'],['PMMNCH.M','瑞士PMI(制造业)'],
        ['PMMNCZ.M','捷克PMI(制造业)'],['PMMNPL.M','波兰PMI(制造业)'],
        
        
        ['PMSRDE.M','德国PMI(服务业)'],['PMSRUS.M','美国PMI(服务业)'],
        ['PMSREU.M','欧元区PMI(服务业)'],['PMSRFR.M','法国PMI(服务业)'],
        ['PMSRUK.M','英国PMI(服务业)'],['PMSRCN.M','中国PMI(服务业)'],
        ['PMSRJP.M','日本PMI(服务业)'], ['PMSRAU.M','澳大利亚PMI(服务业)'], 
        ['PMSRIN.M','印度PMI(服务业)'], ['PMSRBR.M','巴西PMI(服务业)'],
        ['PMSRIE.M','爱尔兰PMI(服务业)'],['PMSRES.M','西班牙PMI(服务业)'],
        ['PMSRIT.M','意大利PMI(服务业)'],
        
        
        ['TRBNCN.M','中国贸易余额(百万美元)'],['TRBNJP.M','日本贸易余额(百万美元)'],
        ['TRBNPH.M','菲律宾贸易余额(百万美元)'],['TRBNSG.M','新加坡贸易余额(百万美元)'],
        ['TRBNMY.M','马来西亚贸易余额(百万美元)'],
        ['TRBNAU.M','澳大利亚贸易余额(百万美元)'],['TRBNNZ.M','新西兰贸易余额(百万美元)'],
        ['TRBNIN.M','印度贸易余额(百万美元)'],['TRBNTR.M','土耳其贸易余额(百万美元)'],
        ['TRBNZA.M','南非贸易余额(百万美元)'],
        ['TRBNUS.M','美国贸易余额(百万美元)'],['TRBNMX.M','墨西哥贸易余额(百万美元)'],
        ['TRBNUK.M','英国贸易余额(百万美元)'],['TRBNIE.M','爱尔兰贸易余额(百万美元)'],
        ['TRBNFR.M','法国贸易余额(百万美元)'],['TRBNBE.M','比利时贸易余额(百万美元)'],
        ['TRBNNL.M','荷兰贸易余额(百万美元)'],
        ['TRBNPT.M','葡萄牙贸易余额(百万美元)'],['TRBNIT.M','意大利贸易余额(百万美元)'],
        ['TRBNGR.M','希腊贸易余额(百万美元)'],
        ['TRBNDE.M','德国贸易余额(百万美元)'],['TRBNAT.M','奥地利贸易余额(百万美元)'],
        ['TRBNCH.M','瑞士贸易余额(百万美元)'],
        ['TRBNSE.M','瑞典贸易余额(百万美元)'],['TRBNNO.M','挪威贸易余额(百万美元)'],
        ['TRBNRO.M','罗马尼亚贸易余额(百万美元)'],['TRBNHU.M','匈牙利贸易余额(百万美元)'],
        ['TRBNCZ.M','捷克贸易余额(百万美元)'],['TRBNSK.M','斯洛伐克贸易余额(百万美元)'],
        ['TRBNEU.M','欧元区贸易余额(百万美元)'],['TRBNLT.M','立陶宛贸易余额(百万美元)'],
        
        
        #有问题：同比or环比or金额？都对不上；EXPRUS与EXPYUS的差别是什么？
        ['EXPRCN.M','中国出口增速%'],['IMPRCN.M','中国进口增速%'],
        ['EXPRJP.M','日本出口增速%'],['IMPRJP.M','日本进口增速%(同比)'],
        ['EXPRSG.M','新加坡出口增速%'],['IMPRSG.M','新加坡进口增速%(同比)'],
        ['EXPRMY.M','马来西亚出口增速%'],['IMPRMY.M','马来西亚进口增速%(同比)'],
        ['EXPRPH.M','菲律宾出口增速%'],['IMPRPH.M','菲律宾进口增速%(同比)'],
        ['EXPRIN.M','印度出口增速%'],['IMPRIN.M','印度进口增速%(同比)'],
        ['EXPRTR.M','土耳其出口增速%'],['IMPRTR.M','土耳其进口增速%(同比)'],
        ['EXPRAU.M','澳大利亚出口增速%'],['IMPRAU.M','澳大利亚进口增速%(同比)'],
        ['EXPRNZ.M','新西兰出口增速%'],['IMPRNZ.M','新西兰进口增速%(同比)'],
        ['EXPRZA.M','南非出口增速%'],['IMPRZA.M','南非进口增速%(同比)'],
        ['EXPRUS.M','美国出口增速%'],['IMPRUS.M','美国进口增速%'],
        ['EXPYUS.M','美国出口增速%(同比)'],#????
        ['EXPRCA.M','加拿大出口增速%'],['IMPRCA.M','加拿大进口增速%'],
        ['EXPRMX.M','墨西哥出口增速%'],['IMPRMX.M','墨西哥进口增速%'],
        
        #雅虎汇率
        ['CNYUSD=X','CCY人民币兑美元汇率'],['CNY=X','CCY美元兑人民币汇率'],
        ['JPYUSD=X','CCY日元兑美元汇率'],['JPY=X','CCY美元兑日元汇率'],
        ['KRWUSD=X','CCY韩元兑美元汇率'],['KRW=X','CCY美元兑韩元汇率'],
        ['HKDUSD=X','CCY港币兑美元汇率'],['HKD=X','CCY美元兑港币汇率'],
        ['TWDUSD=X','CCY新台币兑美元汇率'],['TWD=X','CCY美元兑新台币汇率'],
        ['PHPUSD=X','CCY菲律宾比索兑美元汇率'],['PHP=X','CCY比索美元兑菲律宾汇率'],
        ['IDRUSD=X','CCY印尼盾兑美元汇率'],['IDR=X','CCY美元兑印尼盾汇率'],
        ['THBUSD=X','CCY泰铢兑美元汇率'],['THB=X','CCY美元兑泰铢汇率'],
        ['MYRUSD=X','CCY马来西亚林吉特兑美元汇率'],['MYR=X','CCY美元兑马来西亚林吉特汇率'],
        ['SGDUSD=X','CCY新加坡币兑美元汇率'],['SGD=X','CCY美元兑新加坡币汇率'],
        ['INRUSD=X','CCY印度卢比兑美元汇率'],['INR=X','CCY美元兑印度卢比汇率'],
        ['AUDUSD=X','CCY澳大利亚元兑美元汇率'],['AUD=X','CCY美元兑澳大利亚元汇率'],
        ['NZDUSD=X','CCY新西兰元兑美元汇率'],['NZD=X','CCY美元兑新西兰元汇率'],
        ['TRYUSD=X','CCY土耳其里拉兑美元汇率'],['TRY=X','CCY美元兑土耳其里拉汇率'],
        ['ILSUSD=X','CCY新谢克尔兑美元汇率'],['ILS=X','CCY美元兑新谢克尔汇率'],
        ['VNDUSD=X','CCY越南盾兑美元汇率'],['VND=X','CCY美元兑越南盾汇率'],
        ['MOPUSD=X','CCY澳门元兑美元汇率'],['MOP=X','CCY美元兑澳门元汇率'],
        ['LAKUSD=X','CCY老挝基普兑美元汇率'],['LAK=X','CCY美元兑老挝基普汇率'],
        ['KHRUSD=X','CCY柬埔寨瑞尔兑美元汇率'],['KHR=X','CCY美元兑柬埔寨瑞尔汇率'],
        ['MMKUSD=X','CCY缅甸元兑美元汇率'],['MMK=X','CCY美元兑缅甸元汇率'],
        ['LKRUSD=X','CCY斯里兰卡卢比兑美元汇率'],['LKR=X','CCY美元兑斯里兰卡卢比汇率'],
        ['PKRUSD=X','CCY巴基斯坦卢比兑美元汇率'],['PKR=X','CCY美元兑巴基斯坦卢比汇率'],
        ['NPRUSD=X','CCY尼泊尔卢比兑美元汇率'],['NPR=X','CCY美元兑尼泊尔卢比汇率'],
        ['AFNUSD=X','CCY阿富汗尼兑美元汇率'],['AFN=X','CCY美元兑阿富汗尼汇率'],
        ['IRRUSD=X','CCY伊朗里亚尔兑美元汇率'],['IRR=X','CCY美元兑伊朗里亚尔汇率'],
        ['IQDUSD=X','CCY伊拉克第纳尔兑美元汇率'],['IQD=X','CCY美元兑伊拉克第纳尔汇率'],
        ['SYPUSD=X','CCY叙利亚镑兑美元汇率'],['SYP=X','CCY美元兑叙利亚镑汇率'],
        ['JODUSD=X','CCY约旦第纳尔兑美元汇率'],['JOD=X','CCY美元兑约旦第纳尔汇率'],
        ['SARUSD=X','CCY沙特亚尔兑美元汇率'],['SAR=X','CCY美元兑沙特亚尔汇率'],
        ['KWDUSD=X','CCY科威特第纳尔兑美元汇率'],['KWD=X','CCY美元兑科威特第纳尔汇率'],
        ['LBPUSD=X','CCY黎巴嫩镑兑美元汇率'],['LBP=X','CCY美元兑黎巴嫩镑汇率'],
        ['CADUSD=X','CCY加拿大元兑美元汇率'],['CAD=X','CCY美元兑加拿大元汇率'],
        ['MXNUSD=X','CCY墨西哥比索兑美元汇率'],['MXN=X','CCY美元兑墨西哥比索汇率'],
        ['ARSUSD=X','CCY阿根廷比索兑美元汇率'],['ARS=X','CCY美元兑阿根廷比索汇率'],
        ['CLPUSD=X','CCY智利比索兑美元汇率'],['CLP=X','CCY美元兑智利比索汇率'],
        ['BRLUSD=X','CCY巴西雷亚尔兑美元汇率'],['BRL=X','CCY美元兑巴西雷亚尔汇率'],
        ['EURUSD=X','CCY欧元兑美元汇率'],['EUR=X','CCY美元兑欧元汇率'],
        ['GBPUSD=X','CCY英镑兑美元汇率'],['GBP=X','CCY美元兑英镑汇率'],
        ['CHFUSD=X','CCY瑞士法郎兑美元汇率'],['CHF=X','CCY美元兑瑞士法郎汇率'],
        ['HUFUSD=X','CCY匈牙利福林兑美元汇率'],['HUF=X','CCY美元兑匈牙利福林汇率'],
        ['SEKUSD=X','CCY瑞典克朗兑美元汇率'],['SEK=X','CCY美元兑瑞典克朗汇率'],
        ['DKKUSD=X','CCY丹麦克朗兑美元汇率'],['DKK=X','CCY美元兑丹麦克朗汇率'],
        ['NOKUSD=X','CCY挪威克朗兑美元汇率'],['NOK=X','CCY美元兑挪威克朗汇率'],
        ['RUBUSD=X','CCY俄罗斯卢布兑美元汇率'],['RUB=X','CCY美元兑俄罗斯卢布汇率'],
        ['PLNUSD=X','CCY波兰兹罗提兑美元汇率'],['PLN=X','CCY美元兑波兰兹罗提汇率'],
        ['RONUSD=X','CCY罗马尼亚列伊兑美元汇率'],['RON=X','CCY美元兑罗马尼亚列伊汇率'],
        ['BGNUSD=X','CCY保加利亚列弗兑美元汇率'],['BGN=X','CCY美元兑保加利亚列弗汇率'],
        ['ZARUSD=X','CCY南非兰特兑美元汇率'],['ZAR=X','CCY美元兑南非兰特汇率'],
        ['EGPUSD=X','CCY埃及镑兑美元汇率'],['EGP=X','CCY美元兑埃及镑汇率'],
        ['MADUSD=X','CCY摩洛哥迪拉姆兑美元汇率'],
        ['NGNUSD=X','CCY尼日利亚奈拉兑美元汇率'],
        ['XOFUSD=X','CCY西非法郎兑美元汇率'],
        ['XAFUSD=X','CCY中非法郎兑美元汇率'],
        ['XCUUSD=X','CCY安巴东加元兑美元汇率'],
        ['XDRUSD=X','CCYIMF特别提款权兑美元汇率'],['XDR=X','CCY美元兑IMF特别提款权汇率'],
        
        ['USDCNY','美元兑人民币汇率'],['CNYUSD','人民币兑美元汇率'],
        ['AUDCNY','澳大利亚元兑人民币汇率'],['CNYAUD','人民币兑澳大利亚元汇率'],
        ['JPYCNY','日元兑人民币汇率'],['CNYJPY','人民币兑日元汇率'],
        ['USDJPY','美元兑日元汇率'],['JPYUSD','日元兑美元汇率'],
        ['SGDCNY','新加坡元兑人民币汇率'],['CNYSGD','人民币兑新加坡元汇率'],
        ['SGDMYR','新加坡元兑马来西亚林吉特汇率'],['MYRSGD','马来西亚林吉特兑新加坡元汇率'],
        ['EURCNY','欧元兑人民币汇率'],['CNYEUR','人民币兑欧元汇率'],
        ['GBPCNY','英镑兑人民币汇率'],['CNYGBP','人民币兑英镑汇率'],
        ['KRWCNY','韩元兑人民币汇率'],['CNYKRW','人民币兑韩元汇率'],
        ['HKDCNY','港币兑人民币汇率'],['CNYHKD','人民币兑港币汇率'],
        ['CADCNY','加拿大元兑人民币汇率'],['CNYCAD','人民币兑加拿大元汇率'],
        ['INRCNY','印度卢比兑人民币汇率'],['CNYINR','人民币兑印度卢比汇率'],
        ['RUBCNY','俄罗斯卢布兑人民币汇率'],['CNYRUB','人民币兑俄罗斯卢布汇率'],
        ['MOPCNY','澳门元兑人民币汇率'],['CNYMOP','人民币兑澳门元汇率'],
        
        ['AUDJPY','澳大利亚元兑日元汇率'],
        
        ['AUDUSD','澳大利亚元兑美元汇率'],
        ['KRWUSD','韩元兑美元汇率'],
        ['HKDUSD','港币兑美元汇率'],
        ['TWDUSD','新台币兑美元汇率'],
        ['PHPUSD','菲律宾比索兑美元汇率'],
        ['IDRUSD','印尼盾兑美元汇率'],
        ['THBUSD','泰铢兑美元汇率'],
        ['MYRUSD','马来西亚林吉特兑美元汇率'],
        ['SGDUSD','新加坡币兑美元汇率'],
        ['INRUSD','印度卢比兑美元汇率'],
        ['AUDUSD','澳大利亚元兑美元汇率'],
        ['NZDUSD','新西兰元兑美元汇率'],
        ['TRYUSD','土耳其里拉兑美元汇率'],
        ['ILSUSD','新谢克尔兑美元汇率'],
        ['CADUSD','加拿大元兑美元汇率'],
        ['MXNUSD','墨西哥比索兑美元汇率'],
        ['ARSUSD','阿根廷比索兑美元汇率'],
        ['CLPUSD','智利比索兑美元汇率'],
        ['BRLUSD','巴西雷亚尔兑美元汇率'],
        ['EURUSD','欧元兑美元汇率'],
        ['GBPUSD','英镑兑美元汇率'],
        ['CHFUSD','瑞士法郎兑美元汇率'],
        ['HUFUSD','匈牙利福林兑美元汇率'],
        ['SEKUSD','瑞典克朗兑美元汇率'],
        ['DKKUSD','丹麦克朗兑美元汇率'],
        ['NOKUSD','挪威克朗兑美元汇率'],
        ['RUBUSD','俄罗斯卢布兑美元汇率'],
        ['PLNUSD','波兰兹罗提兑美元汇率'],
        ['RONUSD','罗马尼亚列伊兑美元汇率'],
        ['BGNUSD','保加利亚列弗兑美元汇率'],
        ['ZARUSD','南非兰特兑美元汇率'],
        ['EGPUSD','埃及镑兑美元汇率'],
        ['XDRUSD','IMF特别提款权兑美元汇率'],
        
        ['^NYICDX','ICE美元指数'],['DX-Y.NYB','ICE美元指数'],
        ['EUR_I','STOOQ欧元指数'],
        
        ['XAUUSD','1盎司黄金现货兑美元'],['XAUCNY','1盎司黄金现货兑人民币'],
        
        #经济体基准利率
        ['INRTAU.M','澳大利亚基准利率'],
        ['INRTBR.M','巴西基准利率'],
        ['INRTCZ.M','捷克基准利率'],
        ['INRTCA.M','加拿大基准利率'],  
        ['INRTCH.M','瑞士基准利率'],              
        ['INRTEU.M','欧元区基准利率'],
        ['INRTHU.M','匈牙利基准利率'],
        ['INRTIN.M','印度基准利率'],
        ['INRTIS.M','冰岛基准利率'],
        ['INRTJP.M','日本基准利率'],
        ['INRTKR.M','韩国基准利率'],
        ['INRTMX.M','墨西哥基准利率'],
        ['INRTMY.M','马来西亚基准利率'],
        ['INRTNO.M','挪威基准利率'],
        ['INRTNZ.M','新西兰基准利率'],
        ['INRTPL.M','波兰基准利率'],
        ['INRTPH.M','菲律宾基准利率'],
        ['INRTRO.M','罗马尼亚基准利率'],
        ['INRTSE.M','瑞典基准利率'],
        ['INRTTR.M','土耳其基准利率'],
        ['INRTUS.M','美联储基准利率'],
        ['INRTUK.M','英国基准利率'],
        ['INRTZA.M','南非基准利率'],
        
        
        ], columns=['code','codename'])
    
    codename=code
    try:
        codename=codedict[codedict['code']==code]['codename'].values[0]
    except:
        """
        #未查到翻译词汇，查找证券字典文件，需要定期更新
        codename=get_names(code)
        if not (codename is None): return codename
        
        """
        return codename
    else:
        return codename

if __name__=='__main__':
    code='GOOG'
    print(codetranslate('000002.SZ'))
    print(codetranslate('09988.HK'))
#==============================================================================

def codetranslate1(code):
    """
    翻译证券代码为证券名称英文。
    输入：证券代码。输出：证券名称
    """
    #不翻译情况:以空格开头，去掉空格返回
    if code[:1]==' ':
        return code[1:]
    
    import pandas as pd
    codedict=pd.DataFrame([
            
        #股票：地产
        ['000002.SZ','Wanke A'],['600266.SS','城建发展'],['600376.SS','首开股份'],
        ['600340.SS','华夏幸福'],['600606.SS','绿地控股'],
        
        #股票：白酒
        ['600519.SS','Moutai'],['000858.SZ','Wuliangye'],['000596.SZ','Gujinggong'],
        ['000568.SZ','Luzhou Laojiao'],['600779.SS','Suijingfang'],['002304.SZ','Yanghe'],
        ['000799.SZ','Jiuguijiu'],['603589.SS','Kouzijiao'],['600809.SS','Shanxi Fenjiu'],
        
        #股票：银行
        ['601398.SS','ICBC Bank(A)'],['601939.SS','CCB Bank(A)'],
        ['601288.SS','ABC Bank(A)'],['601988.SS','Bank of China(A)'],
        ['600000.SS','SPDB Bank'],['601328.SS','Bank of Communications'],
        ['600036.SS','CMB Bank'],['000776.SZ','GDB Bank'],
        ['601166.SS','Industrial Bank'],['601169.SS','Bank of Beijing'],
        ['600015.SS','Huaxia Bank'],['601916.SS','CZBank'],
        ['600016.SS','Minsheng Bank'],['000001.SZ','Pingan Bank'],
        ['601818.SS','Everbright Bank'],['601998.SS','Citic Bank'],
        ['601229.SS','Bank of Shanghai'],['601658.SS','PSBC Bank'],
        
        ['01398.HK','ICBC(HK)'],['00939.HK','CCB(HK)'],
        ['01288.HK','ABC(HK)'],['00857.HK','Petro China(HK)'],
        ['00005.HK','HSBC(HK)'],['HSBA.L','HSBC(UK)'],
        ['02888.HK','Standard Chartered(HK)'],
        ['03988.HK','BOC(HK)'],['BANK OF CHINA','中国银行'],
        
        ['CICHY','CCB(US)'],['CICHF','CCB(US)'],
        ['ACGBY','ABC(US)'],['ACGBF','ABC(US)'],
        ['IDCBY','ICBC(US)'],['IDCBF','ICBC(US)'],
        ['BCMXY','BCM(US)'],
        
        ['BAC','Bank of America'],['Bank of America Corporation','Bank of America'],
        ['JPM','JP Morgan'],['JP Morgan Chase & Co','JP Morgan'],
        ['WFC','Wells Fargo'],
        ['MS','Morgan Stanley'],['Morgan Stanley','Morgan Stanley'],
        ['USB','US Bancorp'],['U','US Bancorp'],
        ['TD','Toronto Dominion'],['Toronto Dominion Bank','Toronto Dominion'],
        ['PNC','PNC Financial'],['PNC Financial Services Group','PNC Financial'],
        ['BK','NY Mellon'],['The Bank of New York Mellon Cor','NY Mellon'],    
        ['GS','Goldman Sachs'],['C','Citigroup'],
        
        ['SIVB','Silicon Valley Bank'],['WFC','Wells Fargo'],['SBNY','Signature Bank'],
        ['FRC','First Republic Bank'],['CS','Credit Suisse'],['UBS','UBS Group'],
        ['SI','Silvergate Capital'],
        
        ['8306.T','MITSUBISHI UFJ'],['MITSUBISHI UFJ FINANCIAL GROUP','MITSUBISHI UFJ'],
        ['8411.T','MIZUHO FINANCIAL'],['MIZUHO FINANCIAL GROUP','MIZUHO FINANCIAL'],
        ['7182.T','JAPAN POSTBANK'],['JAPAN POST BANK CO LTD','JAPAN POSTBANK'], 

        ['00005.HK','HSBC(HK)'],['HSBC HOLDINGS','HSBC'],['HSBA.L','HSBC(UK)'],
        ['02888.HK','Standard Chartered(HK)'],['STANCHART','Standard Chartered'],  
        
        ['UBSG.SW','UBS(SW)'],        

        #股票：高科技
        ['AAPL','Apple'],['Apple','Apple'],['DELL','DELL Corp'],['IBM','IBM Corp'],
        ['MSFT','Microsoft'],['Microsoft','Microsoft'],['HPQ','HP'],['AMD','AMD Corp'],
        ['NVDA','NVidia'],['INTC','Intel'],['QCOM','Qualcomm'],['BB','Blackberry'],
        
        #股票：电商、互联网        
        ['AMZN','Amazon'],['Amazon','Amazon'],
        ['SHOP','Shopify'],['MELI','Mercado Libre'],
        ['EBAY','eBay'],['eBay','eBay'],['META','META'],['ZM','ZOOM'],
        ['GOOG','Google'],['TWTR','Twitter'],
        ['VIPS','Vipshop'],['Vipshop','Vipshop'],
        ['PDD','PDD(US)'],['Pinduoduo','Pinduoduo'],        
        ['BABA','Alibaba(US)'],['Alibaba','Alibaba'],
        ['JD','JD(US)'],
        ['SINA','Sina'],['BIDU','Baidu'],['NTES','Netease'],
        
        ['00700.HK','Tencent(HK)'],['TENCENT','Tencent'],
        ['09988.HK','Alibaba(HK)'],['BABA-SW','Alibaba(HK)'],
        ['09618.HK','JD(HK)'],['JD-SW','JD(HK)'], 
        
        #股票：石油、矿业
        ['SLB','Schlumberger'],['BKR','Baker-Hughes'],['HAL','Halliburton'],
        ['WFTLF','Weatherford'],['WFTUF','Weatherford'],
        ['OXY','Occidental Petroleum'],['COP','Conoco Phillips'],
        ['FCX','Freeport-McMoRan'], ['AEM','Agnico Eagle Mines'],   
        ['XOM','Exxon Mobil'],['2222.SR','Saudi Aramco'],
        ['BP','British Petroleum'],['RDSA.AS','Shell Oil'],['SOEX','Shell Oil'],['SHEL.UK','Shell Oil'],
        ['1605.T','INPEX(JP)'],['5020.T','Nippon Oil(JP)'],['5713.T','Sumitomo Metalmining(JP)'],
        
        ['NEM','Newmont Mining'],['SCCO','Southern Copper'],
        ['RGLD','Royal Gold'],['AA','Alcoa'],['CLF','Cleveland-Cliffs'],
        ['BTU','Peabody Energy'],        
        
        ['601857.SS','Petro China(A)'],['PTR','Petro China(US)'],
        ['00857.HK','Petro China(HK)'],['PETROCHINA','Petro China'],
        
        ['00883.HK','CNOOC(HK)'],['601808.SS','COSL(A)'],
        ['02883.HK','COSL(HK)'],['600583.SS','CNOOC Engineering(A)'],['600968.SS','CNOOC Development(A)'],
        
        ['600028.SS','Sinopec(A)'],['00386.HK','Sinopec(HK)'],
        ['600871.SS','Sinopec Oilfield(A)'],['01033.HK','Sinopec Oilfield(HK)'],
        
        ['600339.SS','CNPC Engineering(A)'],
        
        ['03337.HK','安东油服港股'],['603619.SS','中曼石油A股'],['002476.SZ','宝莫股份A股'],
        ['002828.SZ','贝肯能源A股'],['300164.SZ','通源石油A股'],['300084.SZ','海默科技A股'],
        ['300023.SZ','宝德股份A股'],
        
        #股票：汽车
        ['F','Ford Motors'],['GM','General Motors'],['TSLA','Tesla Motors'],
        ['7203.T','Toyota Motors(JP)'],['7267.T','Honda Motors(JP)'],['7201.T','Nissan Motors(JP)'], 
        ['DAI.DE','Mercedes-Benz'],['MBG.DE','Mercedes-Benz Group'],['BMW.DE','BMW'],
        ['XPEV','XPENG Auto'],['LI','LI Auto'],['00175.HK','Geely Auto'],
        ['02238.HK','GAGC Auto'],['000625.SZ','Changan Auto'],['600104.SS','SAIC Auto'],['NIO','NIO Auto'],        
        
        #股票：制药
        ['LLY','Eli Lilly'],['Eli','Eli Lilly'],
        ['JNJ','Johnson Pharm'],['Johnson','Johnson Pharm'],
        ['VRTX','Vertex Pharm'],['Vertex','Vertex Pharm'],
        ['PFE','Pfizer'],['Pfizer','Pfizer'],
        ['MRK','Merck Pharm'],['Merck','Merck Pharm'],
        ['NVS','Novartis Pharm'],['Novartis','Novartis Pharm'],
        ['AMGN','Amgen'],['Amgen','Amgen'],
        ['SNY','Sanofi-Aventis'],['Sanofi','Sanofi-Aventis'],
        ['AZN','AstraZeneca'],['MRNA','Moderna Bio'],
        ['NBIX','Neurocrine Bio'],['Neurocrine','Neurocrine Bio'],
        ['REGN','Regeneron Pharm'],['Regeneron','Regeneron Pharm'],
        ['PRGO','Perrigo'],['Perrigo','Perrigo'],
        ['TEVA','Teva Pharm'],['SNDX','Syndax Pharm'],
        ['BPTH','Bio-Path'],
        
        #股票：教育、视频
        ['BILI','Bilibili'],['TAL','TAL Education'],['EDU','New Oriental'],['RYB','RYB Education'],       
        ['IQ','IQIYI'],['HUYA','Huya'],['01024.HK','Kuashou(HK)'],
        
        #股票：服饰，鞋帽，化妆品，体育，奢侈品
        ['002612.SZ','朗姿股份'],['002832.SZ','比音勒芬'],
        ['002291.SZ','星期六'],['600398.SS','海澜之家'],
        ['600400.SS','红豆股份'],['300005.SZ','探路者'],
        ['603877.SS','太平鸟'],['002563.SZ','森马服饰'],
        ['002154.SZ','报喜鸟'],['002029.SZ','七匹狼'],
        ['601566.SS','九牧王'],['600107.SS','美尔雅'],
        ['603116.SS','红蜻蜓'],['002503.SZ','搜于特'],
        ['002193.SZ','如意集团'],['603001.SS','奥康国际'],
        ['300979.SZ','C华利'],['002269.SZ','美邦服饰'],
        ['600884.SS','杉杉股份'],['600177.SS','雅戈尔'],
        ['300526.SZ','中潜股份'],['601718.SS','际华集团'],
        ['603157.SS','拉夏贝尔A股'],['600295.SS','鄂尔多斯'],
        ['002293.SZ','罗莱生活'],['603587.SS','地素时尚'],
        ['002404.SZ','嘉欣丝绸'],['600612.SS','老凤祥'],
        ['300577.SZ','开润股份'],['600137.SS','浪莎股份'],
        
        ['02331.HK','Lining Sports(HK)'],['02020.HK','Anta Sports(HK)'],['01368.HK','Xtep Intl(HK)'],
        ['01361.HK','361°(HK)'],['06116.HK','La Chapelle(HK)'],['03306.HK','JNBY(HK)'],
        ['02298.HK','Cosmo Lady(HK)'],['01388.HK','Embry Form(HK)'],['01749.HK','FIRS(HK)'],
        ['01234.HK','Lilanz(HK)'],['02030.HK','Cabbeen Fashion(HK)'],['00709.HK','Giordano(HK)'],
        ['03998.HK','Bosideng(HK)'],['00592.HK','Bossini(HK)'],['02313.HK','Shenzhou Intl(HK)'],
        ['06110.HK','Topsports Intl(HK)'],['03813.HK','Pou Sheng Intl(HK)'],['06288.HK','Fast Retailing(HK)'],
        ['01913.HK','PRADA(HK)'],['00551.HK','Yue Yuen(HK)'],['02399.HK','China Fordoo(HK)'],
        ['02232.HK','Crystal Intl(HK)'],['01146.HK','China Outfitters(HK)'],
        
        ['4911.T','Shiseido(JP)'],['4452.T','Kao(JP)'],
        ['9983.T','Fast Retailing(JP)'],['7453.T','Muji(HK)'],   
        
        ['CDI.PA','Dior(F)'],['DIO.F','Dior(F)'],['HMI.F','Hermes(F)'],
        
        ['LOR.DE','L\'Oréal'],['OR.PA','L\'Oréal'],
        
        #股票：其他
        ['PG','P&G'],['KO','Coca Cola'],['PEP','Pepsi-Cola'],
        ['BRK.A','Berkshire A'],['BRK.B','Berkshire B'],['Berkshire','伯克希尔'],
        ['COST','Costco'],['WMT','Wal Mart'],['DIS','Disney'],['BA','Boeing'],
        ['DPW','Ault Global'],['RIOT','Riot Blockchain'],['MARA','Marathon Digital'],['NCTY','9th City'],

        ['000651.SZ','Gree Electric(A)'],['000333.SZ','Midea(A)'],

        ['00992.HK','Lenovo(HK)'],['LENOVO GROUP','Lenovo'],
        ['01810.HK','Xiaomi(HK)'],
        ['01166.HK','Solartech(HK)'],['00273.HK','Mason Group(HK)'],

        ['2330.TW','TSMC(TW)'],['2317.TW','Hon Hai Precision(TW)'],['2474.TW','Catcher Tech(TW)'],
        ['3008.TW','Largan(TW)'],['2454.TW','MediaTek(TW)'],  
        
        ['6758.T','SONY(JP)'],
        
        ['005930.KS','Samsung(KS)'],
        
        ['TCS.NS','TCS(IN)'],
        
        #股票：指数==============================================================
        ['000300.SS','CSI300 Index'],['399300.SS','CSI300 Index'],
        ['000001.SS','SSE Composite Index'],['399001.SZ','SZSE Component Index'],
        ['000016.SS','SSE50 Index'],['000132.SS','SSE100 Index'],
        ['000133.SS','SSE150 Index'],['000010.SS','SSE180 Index'],
        ['000688.SS','STAR50 Index'],['000043.SS','SSE Supercap Index'],
        ['000044.SS','SSE Midcap Index'],['000046.SS','SSE Mid-small Cap Index'],
        ['000045.SS','SSE Smallcap Index'],['000004.SS','上证工业指数'],
        ['000005.SS','SSE Commercial Index'],['000006.SS','SSE Realestate Index'],
        ['000007.SS','SSE Utility Index'],['000038.SS','SSE Financial Index'],
        ['000057.SS','SSE Growth Index'],['000058.SS','SSE Value Index'],
        ['000019.SS','SSE Governance Index'],['000048.SS','SSE CSR Index'],
        
        ['899050.BJ','BSE50 Index'],['^SPX','Standard & Poor 500 Index'],
        ['^RUT','Russell 2000 Index'],['^RUI','Russell 1000 Index'],
        ['^NKX','Nikkei 225 Index'],
        ['^NDQ','NASDAQ Composite Index'],['^NDX','NASDAQ 100 Index'],
        ['IBM','IBM Corp'],
        
        ['1155.KL','Maybank(KL)'],['5347.KL','Tenaga Nasional(KL)'],
        ['1295.KL','Public Bank(KL)'],['1066.KL','RHB Bank(KL)'],
        ['5819.KL','Hong Leong Bank(KL)'],['5183.KL','Petronas Chemical(KL)'],
        ['7113.KL','Top Glove(KL)'],['3182.KL','Genting(KL)'],
        ['6888.KL','Axiata(KL)'],['1015.KL','AmBank(KL)'],
        
        ['D05.SI','DBS Bank(SG)'],['DBSDY','DBS Bank(US)'],
        ['U11.SI','UOB Bank(SG)'],['UOVEY','UOB Bank(US)'],
        ['O39.SI','OCBC Bank(SG)'],['OVCHY','OCBC Bank(US)'],
        ['S41.SI','Hong Leong Finance(SG)'],
        
        ['000002.SS','SSE A Index'],['000003.SS','SSE B Index'],
        ['399107.SZ','SZSE A Index'],['399108.SZ','SZSE B Index'],
        ['399106.SZ','SZSE Composite Index'],['399004.SZ','SZSE100 Index'],
        ['399012.SZ','GEM300 Index'],
        
        ['399232.SZ','SZSE Mining Index'],['399233.SZ','SZSE Manufacturing Index'],
        ['399234.SZ','SZSE Utility Index'],['399236.SZ','SZSE Commercial Index'],
        ['399237.SZ','SZSE Logistics Index'],['399240.SZ','SZSE Financial Index'],
        ['399241.SZ','SZSE Realestate Index'],['399244.SZ','SZSE EP Index'],
        ['399991.SZ','SZSE BRI Index'],['399997.SZ','CSI China Baijiu Index'],
        
        ['000903.SS','CSI100 Index'],['399903.SZ','CSI100 Index'],
        ['000904.SS','CSI200 Index'],['399904.SZ','CSI200 Index'],
        ['000905.SS','CSI500 Index'],['399905.SZ','CSI500 Index'],
        ['000907.SS','CSI700 Index'],['399907.SZ','CSI700 Index'],
        ['000906.SS','CSI800 Index'],['399906.SZ','CSI800 Index'],
        ['000852.SS','CSI1000 Index'],['399852.SZ','CSI1000 Index'],
        ['000985.SS','CSI Composite Index'],['399985.SZ','CSI Composite Index'],
        
        ['000012.SS','SSE T-Bond Index'],['000013.SS','SSE Ent Bond Index'],
        ['000022.SS','SSE Corpbond Index'],['000061.SS','SSE Entbond30 Index'],
        ['000116.SS','SSE Creditbond100 Index'],['000101.SS','SSE 5-year Creditbond Index'],
        
        ['002594.SZ','BYD Auto(A)'],['01211.HK','BYD Auto(HK)'],['81211.HK','BYD Auto(HK RMB)'],
        ['600941.SS','China Mobile'],['00941.HK','China Mobile (HK)'],['80941.HK','China Mobile (HK RMB)'],
        ['ULVR.UK','Unilever (UK)'],['605011.SS','Hangzou Power'],['000723.SZ','Meijin Energy'],
        ['EL','Estée Lauder'],['LOR.DE','L\'Oreal(DE)'],

        ['^GSPC','S&P500 Index'],['^DJI','Dow Jones Index'],
        ['WISGP.SI','FTSE Singapore Index'], ['^STI','Straits Times Index'],
        ['^IXIC','Nasdaq Composite Index'],['^FTSE','FTSE 100 Index'],
        ['^N100','Euronext 100 Index'],['^FMIB','FTSE Italy Index'],
        ['^TSX','Toronto Composite Index'],['^MXX','Mexico IPC Index'],
        ['^SNX','India SENSEX 30 Index'],['^FTM','UK FTSE 250 Index'],
        ['^KLCI','Kuala Lumpur Composite Index'],['^KLSE','Kuala Lumpur Composite Index'],
        
        ['FVTT.FGI','FTSE Viernam Index'],
        ['^RUT','Russell 2000 Index'],['^RUI','Russell 1000 Index'],
        ['^HSI','Hang Seng Index'],['^N225','Nikkei 225 Index'],
        ['WIKOR.FGI','FTSE Korea Index'],['^KS11','Korea Composite Index'],
        ['^KOSPI','Korea Composite Index'],['^BSESN','SENSEX Index'],
        ['^FCHI','France CAC40 Index'],['^GDAXI','Germany DAX30 Index'], 
        ['^CAC','France CAC40 Index'],['^DAX','Germany DAX30 Index'], 
        ['IMOEX.ME','MOEX Index'],['^MOEX','MOEX Index'], 
        ['^RTS','RTS(USD) Index'],
        ['^VIX','VIX Index'],['ASEA','FTSE SE Asia ETF'],['LIT','Global X Lithium & Battery Tech ETF'],
        
        ['^HSCE','Hang Seng H-share Index'],['^HSNC','Hang Seng Commercial Index'],
        ['^HSNU','Hang Seng Utility Index'], 
        ['^TWII','Taiwan Weighted Index'], 
        
        ['^XU100','ISE National-100 index'], ['10TRY.B','Turkey 10-year Treasurybond Yield%'],
        ['10CNY.B','10-Year China Treasurybond Yield%'],
        
        # 另类指数
        ['INDEXCF','Russia MICEX Index'],
        ['RTS','Russia RTS Index'],
        ['CASE','Egypt CASE30 Index'],
        ['VNINDEX','Ho Chi-Ming Index'],
        ['HSCEI','HK H-share Index'],
        ['HSCCI','HK Red-share Index'],
        ['CSEALL','Colombo Index'],
        ['UDI','US Dollar Index'],
        ['CRB','Reuters CRB Index'],
        ['BDI','Baltic Dry Index'],
        ['KSE100','Pakistan KSE100 Index'],
        
        
        #债券==================================================================
        ['sh019521','15国债21'],['sz128086','国轩转债'],['sz123027','蓝晓转债'],
        ['^IRX','13-week Treasury Yield%'],['^FVX','5-year Treasury Yield%'],
        ['^TNX','10-year Treasury Yield%'],['^TYX','30-year Treasury Yield%'],
        
        #基金==================================================================
        ['000595','嘉实泰和混合基金'],['000592','建信改革红利股票基金'],
        ['050111','博时信债C'],['320019','诺安货币B基金'],
        ['510580','Yifangda CSI500 ETF'],['510210.SS','SSE Composite Index ETF'],
        ["510050.SS",'Huaxia CSI50 ETF'],['510880.SS','SSE Dividend ETF'],
        ["510180.SS",'SSE180 ETF'],['159901.SZ','SZSE100 ETF'],
        ["159902.SZ",'SZSE SMB ETF'],['159901.SZ','SZSE100 ETF'],
        ["159919.SZ",'Jiashi CSI300 ETF'],["510300.SS",'Huaxia Borui CSI300 ETF'],
        
        ["004972",'长城收益宝货币A基金'],["004137",'博时合惠货币B基金'],
        ["002890",'交银天利宝货币E基金'],["004417",'兴全货币B基金'],
        ["005151",'红土创新优淳货币B基金'],["001909",'创金合信货币A基金'],
        ["001821",'兴全天添益货币B基金'],["000836",'国投瑞银钱多宝货币A基金'],
        ["000700",'泰达宏利货币B基金'],["001234",'国金众赢货币基金'],
        ["100051",'富国可转债A基金'],["217022",'招商产业债券A基金'],
        
        
        ["SPY",'SPDR SP500 ETF'],['SPYD','SPDR SP500 Div ETF'],
        ["SPYG",'SPDR SP500 Growth ETF'],['SPYV','SPDR SP500 Value ETF'],
        ["GLD",'SPDR Gold Shares ETF'],
        ["VOO",'Vanguard SP500 ETF'],['VOOG','Vanguard SP500 Growth ETF'],
        ["VOOV",'Vanguard SP500 Value ETF'],['IVV','iShares SP500 ETF'],        
        ["DGT",'SPDR Global Dow ETF'],['ICF','iShares C&S REIT ETF'], 
        ["FRI",'FT S&P REIT Index Fund'],['IEMG','iShares核心MSCI新兴市场ETF'],    
        ['245710.KS','KINDEX越南VN30指数ETF'],['02801.HK','iShares核心MSCI中国指数ETF'],
        ['VNM','VanEck越南ETF'],
        
        #基金REITs
        ['180201.SZ','平安广州广河REIT'],['508008.SS','国金中国铁建REIT'],
        ['508001.SS','浙商沪杭甬REIT'],['508018.SS','华夏中国交建REIT'],
        ['180202.SZ','华夏越秀高速REIT'],['508066.SS','华泰江苏交控REIT'],
        ['508021.SS','国泰君安临港创新产业园REIT'],['508056.SS','中金普洛斯REIT'],
        ['508027.SS','东吴苏园产业REIT'],['508006.SS','富国首创水务REIT'],
        ['508099.SS',' 建信中关村REIT'],['508000.SS','华安张江光大REIT'],
        ['508088.SS',' 国泰君安东久新经济REIT'],['508098.SS',' 京东仓储REIT'],
        ['180103.SZ','华夏和达高科REIT'],['180301.SZ','红土创新盐田港REIT'],
        ['180101.SZ','博时蛇口产园REIT'],['508058.SS','中金厦门安居REIT'],
        ['508068.SS','华夏北京保障房REIT'],['508077.SS','华夏基金华润有巢REIT'],
        
        ['180801.SZ','中航首钢绿能REIT'],
        ['508028.SS','中信建投国家电投新能源REIT'],['508009.SS','中金安徽交控REIT'],
        ['180401.SZ','鹏华深圳能源REIT'],
        
        
        ['FFR','FTSE USA REITs Index'],
        ['AMT','美国电塔REIT'],['CCI','Crown Castle REIT'],
        ['EQUIX','Equinix REIT'],['LAMR','Lamar Advertising REIT'],
        ['OUT','Outfront Media REIT'],['CIO','City Office REIT'],
        ['NYC','New York City REIT'],['REIT','ALPS Active REIT'],
        ['EARN','Ellington RM REIT'], ['VNQ','Vanguard ETF REIT'],  
        
        ['00823.HK','领展房产REIT'], ['02778.HK','冠君产业REIT'], 
        ['087001.HK','汇贤产业REIT'], ['00808.HK','泓富产业REIT'], 
        ['01426.HK','春泉产业REIT'], ['00435.HK','阳光房地产REIT'], 
        ['00405.HK','越秀房产REIT'], ['00778.HK','置富产业REIT'], 
        ['01275.HK','开元产业REIT'], ['01881.HK','富豪产业REIT'], 
        ['01503.HK','招商局商房REIT'], ['02191.HK','SF REIT'],
        
        ['3283.T','日本安博REIT'],
        
        ['C38U.SI','凯德商业信托REIT'],['N2IU.SI','枫树商业信托REIT'],
        ['T82U.SI','Suntec REIT'],['HMN.SI','雅诗阁公寓REIT'],

        #期货==================================================================
        ["HG=F",'COMEX铜矿石期货'],["CL=F",'NYM原油期货'],
        ["6B=F",'CME英镑兑美元期货'],
        ["S=F",'CBT大豆期货'],["C=F",'CBT玉米期货'],
        ["ES=F",'CME标普500指数期货'],["YM=F",'CBT道指期货'],
        ["NQ=F",'CME纳指100期货'],["RTY=F",'罗素2000指数期货'],
        ["ZB=F",'30年期美债期货'],["ZT=F",'2年期美债期货'],
        ["ZF=F",'5年期美债期货'],["ZN=F",'10年期美债期货'],        
        
        #======================================================================
        #=新加入
        #======================================================================
        # 白酒行业
        ['603589.SS','口子窖'],['000568.SZ','泸州老窖'],['000858.SZ','五粮液'],
        ['600519.SS','贵州茅台'],['000596.SZ','古井贡酒'],['000799.SZ','酒鬼酒'],
        ['600809.SS','山西汾酒'],['600779.SS','水井坊'],

        # 房地产行业
        ['000002.SZ','万科A'],['600048.SS','保利发展'],['600340.SS','华夏幸福'],
        ['000031.SZ','大悦城'],['600383.SS','金地集团'],['600266.SS','城建发展'],
        ['600246.SS','万通发展'],['600606.SS','绿地控股'],['600743.SS','华远地产'],
        ['000402.SZ','金融街'],['000608.SZ','阳光股份'],['600376.SS','首开股份'],
        ['000036.SZ','华联控股'],['000620.SZ','新华联'],['600663.SS','陆家嘴'],

        # 银行业
        ['601328.SS','交通银行'],['601988.SS','中国银行'],['600015.SS','华夏银行'],
        ['601398.SS','工商银行'],['601169.SS','北京银行'],['601916.SS','浙商银行'],
        ['601288.SS','农业银行'],['601229.SS','上海银行'],['600016.SS','民生银行'],
        ['601818.SS','光大银行'],['601658.SS','邮储银行'],['600000.SS','浦发银行'],
        ['601939.SS','建设银行'],['601998.SS','中信银行'],['601166.SS','兴业银行'],
        ['600036.SS','招商银行'],['002142.SZ','宁波银行'],['000001.SZ','平安银行'],

        # 纺织服装行业
        ['002612.SZ','朗姿股份'],['601566.SS','九牧王'],['002269.SZ','美邦服饰'],
        ['600398.SS','海澜之家'],['600137.SS','浪莎股份'],['603001.SS','奥康国际'],
        ['603116.SS','红蜻蜓'],['002291.SZ','星期六'],['002832.SZ','比音勒芬'],
        ['600400.SS','红豆股份'],['300005.SZ','探路者'],['603877.SS','太平鸟'],
        ['002563.SZ','森马服饰'],['002154.SZ','报喜鸟'],['600177.SS','雅戈尔'],
        ['002029.SZ','七匹狼'],

        # 物流行业
        ['002352.SZ','顺丰控股'],['002468.SZ','申通快递'],['600233.SS','圆通速递'],
        ['002120.SZ','韵达股份'],['603128.SS','华贸物流'],['603056.SS','德邦股份'],
        ['601598.SS','中国外运'],['603967.SS','中创物流'],['603128.SS','华贸物流'],

        # 券商行业
        ['601995.SS','中金公司'],['601788.SS','光大证券'],['300059.SZ','东方财富'],
        ['600030.SS','中信证券'],['601878.SS','浙商证券'],['600061.SS','国投资本'],
        ['600369.SS','西南证券'],['600837.SS','海通证券'],['601211.SS','国泰君安'],
        ['601066.SS','中信建投'],['601688.SS','华泰证券'],['000776.SZ','广发证券'],
        ['000166.SZ','申万宏源'],['600999.SS','招商证券'],['002500.SZ','山西证券'],
        ['601555.SS','东吴证券'],['000617.SZ','中油资本'],['600095.SS','湘财股份'],
        ['601519.SS','大智慧'],

        # 中国啤酒概念股
        ['600600.SS','青岛啤酒'],['600132.SS','重庆啤酒'],['002461.SZ','珠江啤酒'],
        ['000729.SZ','燕京啤酒'],['600573.SS','惠泉啤酒'],['000929.SZ','兰州黄河'],
        ['603076.SS','乐惠国际'],

        # 建筑工程概念股
        ['601186.SS','中国铁建'],['601668.SS','中国建筑'],['601800.SS','中国交建'],
        ['601789.SS','宁波建工'],['601669.SS','中国电建'],['000498.SZ','山东路桥'],
        ['600170.SS','上海建工'],['600248.SS','陕西建工'],['600502.SS','安徽建工'],
        ['600284.SS','浦东建设'],['603815.SS','交建股份'],['600039.SS','四川路桥'],

        # 民用航空概念股
        ['600221.SS','海南航空'],['603885.SS','吉祥航空'],['600115.SS','中国东航'],
        ['600029.SS','南方航空'],['601021.SS','春秋航空'],['601111.SS','中国国航'],
        ['002928.SZ','华夏航空'],

        # 家电概念股
        ['600690.SS','海尔智家'],['600060.SS','海信视像'],['000333.SZ','美的集团'],
        ['000404.SZ','长虹华意'],['000651.SZ','格力电器'],['000521.SZ','长虹美菱'],
        ['603868.SS','飞科电器'],['600839.SS','四川长虹'],['000921.SZ','海信家电'],
        ['002035.SZ','华帝股份'],['002242.SZ','九阳股份'],['600336.SS','澳柯玛'],
        ['600854.SS','春兰股份'],['000418.SZ','小天鹅A'],['002508.SZ','老板电器'],
        ['000810.SZ','创维数字'],['603551.SS','奥普家居'],['002959.SZ','小熊电器'],
        ['000100.SZ','TCL科技'],['002032.SZ','苏泊尔'],['000016.SZ','深康佳A'],
        ['600690.SS','青岛海尔'],['000541.SZ','佛山照明'],['603515.SS','欧普照明'],

        # 体育用品概念股
        ['02020.HK','Anta Sports(HK)'],['02331.HK','Li-Ning(H)'],['01368.HK','Xtep Intl(HK)'],
        ['01361.HK','361°(HK)'],['ADS.DE','ADIDAS(DE)'],['NKE','NIKE'],
        ['8022.T','Mizuno(JP)'],['PUM.DE','PUMA(DE)'],['FILA.MI','FILA(MI)'],
        ['SKG.L','Kappa(LSE)'],['7936.T','ASICS(JP)'],

        # 新加坡著名股票
        ['D05.SI','DBS(SI)'],['Z74.SI','Singtel(SI)'],['O39.SI','OCBC(SI)'],
        ['U11.SI','UOB(SI)'],['C6L.SI','Singapore Airlines(SI)'],['CC3.SI','Starhub(SI)'],
        ['S08.SI','Singpost(SI)'],['F34.SI','WILMAR(SI)'],['C31.SI','CapitaLand(SI)'],  
        
        ['XAUUSD','Gold(ozt)->USD'],['XAUCNY','Gold(ozt)->RMB'],

        
        ], columns=['code','codename'])
    
    codename=code
    try:
        codename=codedict[codedict['code']==code]['codename'].values[0]
    except:
        #未查到翻译词汇，查找证券字典文件，需要定期更新
        codename=get_names(code)
        if not (codename is None): return codename
        
        """
        #未查到翻译词汇，先用akshare查找中文名称
        #不是国内股票或中文名称未查到
        try:
            codename=securities_name(code)
        except:
            pass
        """
    else:
        return codename

if __name__=='__main__':
    code='GOOG'
    print(codetranslate('000002.SZ'))
    print(codetranslate('09988.HK'))


#==============================================================================
if __name__=='__main__':
    symbol='00700.HK'
    
    symbol='1234567'
    
    symbol='sh510170'
    
    symbol='510170.SS'
    
    get_names(symbol)
    
def get_names(symbol):
    """
    从文件中查询证券代码的短名称，速度较慢
    """
    # 查询股票名称
    name=get_names0(symbol)
    
    #未查到时再查询其他种类的证券
    if name == symbol:
        # 查询基金
        name=get_fund_name_china(symbol)
        
    #未查到时再查询其他种类的证券
    if name == symbol:
        # 查询债券：银行间债券信息
        name=get_bond_name_china(symbol)
        # 需要沪深债券信息，暂时无全面信息，仅能获得可转债信息
        #name=get_covbond_name_china(symbol)
        
    return name


#==============================================================================
if __name__=='__main__':
    symbol='00700.HK'
    symbol='001979.SZ'
    symbol='PDD'
    
    get_names0(symbol)
    
def get_names0(symbol):
    """
    从文件中查询证券代码的短名称
    """
    
    symbol2=symbol
    result,prefix,suffix=split_prefix_suffix(symbol)
    
    #若后缀是港股、前缀为五位数且首位为0，则去掉首位0
    if (suffix=='HK') and (len(prefix)==5):
        if prefix[:1]=='0':
            symbol2=prefix[1:]+'.'+suffix
    
    #查询现有数据库
    import pickle
    import siat
    import os
    siatpath=siat.__path__
    file_path = os.path.join(siatpath[0], 'stock_info.pickle')
    with open(file_path,'rb') as test:
        df = pickle.load(test)  
        
    df1=df[df['SYMBOL']==symbol2]
    
    #查询结果
    lang=check_language()
    name=symbol
    if not (len(df1)==0):
        #查到了
        if lang == 'Chinese':
            name=df1['CNAME'].values[0]
        else:
            name=df1['ENAME'].values[0]
    else:
        #未查到
        #若为A股，直接取股票名称
        if suffix in SUFFIX_LIST_CN:
            import akshare as ak
            
            try:
                allnames_cn=ak.stock_zh_a_spot_em()
                name=allnames_cn[allnames_cn['代码']==prefix]['名称'].values[0]
            except:
                pass
            
            #沪深京：股票代码-名称，有点慢
            try:
                allnames_cn=ak.stock_info_a_code_name()
                name=allnames_cn[allnames_cn['code']==prefix]['name'].values[0]
            except:
                pass
    
    #从结果中去掉某些子串
    #droplist=["公司","集团","有限","责任","股份"]
    droplist=["公司","集团","有限","责任"]
    for w in droplist:
        name=name.replace(w,'')
    
    #如果名称中含有"指数"字样，则去掉"(A股)"\"(港股)"\"(美股)"
    droplist2=["(A股)","(港股)","(美股)"]
    if "指数" in name:
        for w in droplist2:
            name=name.replace(w,'')
    
    return name

if __name__=='__main__':
    get_names('00700.HK')
    get_names('0700.HK')
    
#==============================================================================
if __name__=='__main__':
    fund='sh510170'
    fund='018021.SS'
    
    get_fund_name_china('sh510170')
    get_fund_name_china('510170.SS')
    get_fund_name_china('118034.SS')

def get_fund_name_china(fund):
    """
    功能：查询中国基金代码和类型
    注意：实际仅需6位数字代码
    """
    # 代码中提取6位数字
    fund1=fund.upper()
    exchlist=['SH','SZ','.SS','.SZ']
    for exch in exchlist:
        fund1=fund1.replace(exch,'')
    
    import akshare as ak
    try:
        names = ak.fund_name_em()
        namedf=names[names['基金代码']==fund1]
        
        if len(namedf) >= 1:
            fname=namedf['基金简称'].values[0]
            ftype=namedf['基金类型'].values[0]
        else:
            fname=fund
            ftype=''
    except:
        fname=fund
        
    #return fname,ftype
    return fname

#==============================================================================
if __name__=='__main__':
    fund='sh510170'
    fund='018021.SS'
    fund='320019.SS'
    fund='510580'
    
    get_fund_name_china2('sh510170')
    get_fund_name_china2(fund)

def get_fund_name_china2(fund):
    """
    功能：查询中国基金代码和类型
    注意：实际仅需6位数字代码
    """
    # 代码中提取6位数字
    fund1=fund.upper()
    exchlist=['.SS','.SZ','SH','SZ']
    for exch in exchlist:
        fund1=fund1.replace(exch,'')
    
    import pandas as pd
    import akshare as ak
    
    # 读取pkl
    """
    import os
    user_dir=os.path.expanduser('~')
    name_file=user_dir+'\\fund_china'
    """
    import siat
    import os
    siatpath=siat.__path__
    name_file = os.path.join(siatpath[0], 'fund_china.pickle')    
    
    try:
        df=pd.read_pickle(name_file)
    except:
        df=ak.fund_name_em()
        df.to_pickle(name_file)
    
    try:
        fname=df[df['基金代码']==fund1]['基金简称'].values[0]
    except:
        df=ak.fund_name_em()
        df.to_pickle(name_file)

        try:
            fname=df[df['基金代码']==fund1]['基金简称'].values[0]
        except:
            fname=fund
        
    #return fname,ftype
    return fname

#==============================================================================
if __name__=='__main__':
    update_fund_names_china()
    
def update_fund_names_china():
    """
    功能：更新fund_china.pickle
    注意：需要将fund_china.pickle加入文件MANIFEST.in中，不然打包不包括
    """
    import akshare as ak
    df=ak.fund_name_em()
    df.to_pickle('S:/siat/siat/fund_china.pickle')
    
    return
    
#==============================================================================
if __name__=='__main__':
    bond="185851.SS"
    bond="102229.SZ"
    
    get_bond_name_china('sh185851')
    get_bond_name_china('185851.SS')
    
    get_bond_name_china("102229.SZ")
    get_bond_name_china("113542.SS")
    get_bond_name_china("118034.SS")
    get_bond_name_china("018021.SS")
    

def get_bond_name_china(bond):
    """
    功能：查询中国债券名称：全国银行间债券信息
    注意：实际仅需6位数字代码
    """
    # 代码中提取6位数字
    bond1=bond.upper()
    # 顺序不可颠倒
    exchlist=['.SS','.SZ','SH','SZ']
    for exch in exchlist:
        bond1=bond1.replace(exch,'')
    
    import akshare as ak
    try:
        bname=ak.bond_info_cm(bond_code=bond1)['债券简称'].values[0]
    except:
        bname=bond
    
    return bname

#==============================================================================
if __name__=='__main__':
    bond="185851.SS"
    bond="102229.SZ"
    bond='sh111015'
    
    get_exchange_bond_name_china(bond)

def get_exchange_bond_name_china(bond):
    """
    功能：查询债券名称：沪深债券简称。每次重新下载债券名称信息，速度慢！
    注意：实际仅需6位数字代码
    """
    #print("  Looking for the short name of the bond",bond,"\b, it takes time ...")

    bond1=bond.lower()
    
    if '.ss' in bond1:
        bond2=bond1[:6]
        bond3='sh'+bond2
        
    elif '.sz' in bond1:
        bond2=bond1[:6]
        bond3='sz'+bond2        
    else:
        bond3=bond1
        
    import akshare as ak
    df=ak.bond_zh_hs_spot()
    try:
        bname=df[df['代码']==bond3]['名称'].values[0]
    except:
        bname=bond
    
    return bname

#==============================================================================
if __name__=='__main__':
    bond="185851.SS"
    bond="102229.SZ"
    bond="sh111015"
    
    get_exchange_bond_name_china2(bond)

def get_exchange_bond_name_china2(bond):
    """
    功能：查询债券名称：沪深债券简称
    特点：第一次保存为pkl文件，后续可快速查找
    注意：实际仅需6位数字代码
    """
    #print("  Looking for the short name of the bond",bond,"\b, it takes time ...")

    bond1=bond.lower()
    
    if '.ss' in bond1:
        bond2=bond1[:6]
        bond3='sh'+bond2
        
    elif '.sz' in bond1:
        bond2=bond1[:6]
        bond3='sz'+bond2        
    else:
        bond3=bond1
        
    import akshare as ak
    import pandas as pd
    
    # 读取pkl
    """
    import os
    user_dir=os.path.expanduser('~')
    name_file=user_dir+'\\exchange_bond'  
    """
    import siat
    import os
    siatpath=siat.__path__
    name_file = os.path.join(siatpath[0], 'exchange_bond_china.pickle')  
    # 需要将pickle文件放到S:/siat/siat目录下，并加入文件MANIFEST.in中，以便下次打包      
    
    try:
        df=pd.read_pickle(name_file)    
    except:
        # 未找到pkl文件，生成pkl文件
        df=ak.bond_zh_hs_spot()
        # 保存为pkl文件
        df.to_pickle(name_file)
        
    # 查找债券代码
    try:
        bname=df[df['代码']==bond3]['名称'].values[0]
    except:
        # 未查到，更新pkl
        df=ak.bond_zh_hs_spot()
        # 保存为pkl文件
        df.to_pickle(name_file)
        
        # 更新后再查找
        try:
            bname=df[df['代码']==bond3]['名称'].values[0]
        except:
            # 还未找到，放弃
            bname=bond
    
    return bname

#==============================================================================
if __name__=='__main__':
    update_exchange_bond_name_china()
    
def update_exchange_bond_name_china():
    """
    功能：更新exchange_bond_china.pickle
    注意：需要将exchange_bond_china.pickle加入文件MANIFEST.in中，不然打包不包括
    """
    import akshare as ak
    df=ak.bond_zh_hs_spot()
    df.to_pickle('S:/siat/siat/exchange_bond_china.pickle')
    
    return

#==============================================================================
if __name__=='__main__':
    bond="185851.SS"
    bond="102229.SZ"
    
    get_covbond_name_china("113542.SS")
    get_covbond_name_china("118034.SS")

def get_covbond_name_china(bond):
    """
    功能：查询中国债券名称：限沪深可转债信息
    注意：实际仅需6位数字代码
    """
    # 代码中提取6位数字
    bond1=bond.upper()
    # 顺序不可颠倒
    exchlist=['.SS','.SZ','SH','SZ']
    for exch in exchlist:
        bond1=bond1.replace(exch,'')
    
    import akshare as ak
    try:
        bname=ak.bond_zh_cov_info(symbol=bond1,indicator="基本信息")['SECURITY_NAME_ABBR'].values[0]
    except:
        bname=bond
    
    return bname

#==============================================================================    
#==============================================================================
def str_replace(str1):
    """
    删除给定字符串中的子串
    """
    replist=['Ltd.','Ltd','Co.','LTD.','CO.',' CO','LTD','Inc.','INC.', \
             'CORPORATION','Corporation','LIMITED','Limited','Company', \
             'COMPANY','(GROUP)','Corp.','CORP','GROUP','Group']
    
    for rc in replist:
        str2=str1.replace(rc, '')
        str1=str2
    
    twlist=[' ',',','，']    
    for tw in twlist:
        str2 = str2.strip(tw)
    
    return str2
    
#==============================================================================
if __name__=='__main__':
    update_stock_names()

def update_stock_names():
    """
    功能：套壳函数get_all_stock_names，更新stock_info.pickle
    注意：需要将stock_info.pickle加入文件MANIFEST.in中，不然打包不包括
    """
    df=get_all_stock_names()
    
    return

#==============================================================================
def get_all_stock_names():
    """
    获得股票代码和名称：中国A股、港股、美股。需要定期更新
    注意：若pandas版本更新，pickle文件可能存在不兼容问题，重新生成该文件即可。
    """
    import akshare as ak
    import pandas as pd
    
    #上证A股
    df_ss=ak.stock_info_sh_name_code(symbol="主板A股")
    #df_ss.rename(columns={'COMPANY_ABBR':'CNAME','ENGLISH_ABBR':'ENAME','LISTING_DATE':'LISTING'},inplace=True)
    df_ss.rename(columns={'证券简称':'CNAME','上市日期':'LISTING'},inplace=True)
    df_ss['ENAME']=df_ss['CNAME']
    df_ss['SYMBOL']=df_ss['证券代码']+'.SS'
    df_ss_1=df_ss[['SYMBOL','CNAME','ENAME','LISTING']]    
    
    #上证科创板
    df_ss2=ak.stock_info_sh_name_code(symbol="科创板")
    #df_ss.rename(columns={'COMPANY_ABBR':'CNAME','ENGLISH_ABBR':'ENAME','LISTING_DATE':'LISTING'},inplace=True)
    df_ss2.rename(columns={'证券简称':'CNAME','上市日期':'LISTING'},inplace=True)
    df_ss2['ENAME']=df_ss2['CNAME']
    df_ss2['SYMBOL']=df_ss2['证券代码']+'.SS'
    df_ss_2=df_ss2[['SYMBOL','CNAME','ENAME','LISTING']]  
    
    #深证A股
    df_sz=ak.stock_info_sz_name_code(symbol="A股列表")
    df_sz['SYMBOL']=df_sz['A股代码']+'.SZ'
    df_sz.rename(columns={'A股简称':'CNAME','A股上市日期':'LISTING'},inplace=True)
    df_sz['ENAME']=df_sz['CNAME']
    df_sz_1=df_sz[['SYMBOL','CNAME','ENAME','LISTING']]    
    
    #北交所
    df_bj=ak.stock_info_bj_name_code()
    df_bj['SYMBOL']=df_bj['证券代码']+'.BJ'
    df_bj.rename(columns={'证券简称':'CNAME','上市日期':'LISTING'},inplace=True)
    df_bj['ENAME']=df_bj['CNAME']
    df_bj_1=df_bj[['SYMBOL','CNAME','ENAME','LISTING']] 
    
    #美股
    df_us=ak.get_us_stock_name()
    df_us['LISTING']=' '
    df_us.rename(columns={'symbol':'SYMBOL','name':'ENAME','cname':'CNAME'},inplace=True)
    df_us_1=df_us[['SYMBOL','CNAME','ENAME','LISTING']] 
    
    #港股
    df_hk=ak.stock_hk_spot()
    df_hk['LISTING']=' '
    last4digits=lambda x:x[1:5]
    df_hk['symbol1']=df_hk['symbol'].apply(last4digits)
    df_hk['SYMBOL']=df_hk['symbol1']+'.HK'
    df_hk.rename(columns={'name':'CNAME','engname':'ENAME'},inplace=True)
    df_hk_1=df_hk[['SYMBOL','CNAME','ENAME','LISTING']] 
    
    #合成
    df=pd.concat([df_ss_1,df_ss_2,df_sz_1,df_bj_1,df_us_1,df_hk_1])
    df.sort_values(by=['SYMBOL'], ascending=True, inplace=True )
    df.reset_index(drop=True,inplace=True)
    
    rep=lambda x:str_replace(x)
    df['CNAME']=df['CNAME'].apply(rep)
    df['ENAME']=df['ENAME'].apply(rep)
    
    # 需要将pickle文件放到S:/siat/siat目录下，并加入文件MANIFEST.in中，以便下次打包
    df.to_pickle('S:/siat/siat/stock_info.pickle')

    """
    #读出文件
    with open('stock_info.pickle','rb') as test:
        df = pickle.load(test)
    """
    
    return df
#==============================================================================
def securities_name(code):
    """
    功能：搜索证券代码的名称，先中文后英文
    """
    codename=code
    
    #搜索国内股票的曾用名
    import akshare as ak
    suffix=code[-3:]
    stock=code[:-3]
    if suffix in ['.SS','.SZ','.BJ']:
        try:
            names = ak.stock_info_change_name(stock=stock)
            if not (names is None):
                #列表中最后一个为最新名称
                codename=names[-1]
                return codename
        except:
            pass
        
    #不是国内股票或中文名称未查到
    if not (suffix in ['.SS','.SZ','.BJ']) or (codename==code):
        try:
            import yfinance as yf
            tp=yf.Ticker(code)
            dic=tp.info
            codename=dic["shortName"]  
                
            #若倒数第2位是空格，最后一位只有一个字母，则截取
            if codename[-2]==' ':
                codename=codename[:-2]
                
            #若最后几位在下表中，则截取
            sl1=['Inc.','CO LTD','CO LTD.','CO. LTD.']
            sl2=['Co.,Ltd','Co.,Ltd.','Co., Ltd','Limited']
            sl3=['CO','Corporation']
            suffixlist=sl1+sl2+sl3
            for sl in suffixlist:
                pos=codename.find(sl)
                if pos <= 0: continue
                else:
                    codename=codename[:pos-1]
                    #print(codename)
                    break 
        except:
            pass
        
        return codename

if __name__=='__main__':
    securities_name('000002.SZ')
    securities_name('002504.SZ')
    securities_name('002503.SZ')
    securities_name('XPEV')
    securities_name('IBM')
    securities_name('NIO')
    securities_name('600519.SS')
    securities_name('601519.SS')
    securities_name('MSFT')

#==============================================================================
#==============================================================================


#==============================================================================
def texttranslate(code):
    """
    翻译文字为中文或英文。
    输入：文字。输出：翻译成中文或英文
    """
    import pandas as pd
    codedict=pd.DataFrame([
            
        ['数据来源: 新浪/stooq,','Source: sina/stooq,'],['数据来源: 雅虎财经,','Source: Yahoo Finance,'],
        ["证券快照：","证券快照："],
        ["证券价格走势图：","证券价格走势图："],
        ["证券收益率损失风险走势图：","证券收益率损失风险走势图："],
        ["证券指标走势对比图：","证券指标走势对比图："],
        ["证券价格走势蜡烛图演示：","证券价格走势蜡烛图演示："],
        ["股票分红历史","Stock Dividend History"],
        ["股票:","Stock: "],["历史期间:","Period: "],
        ['序号','Seq'],['日期','Date'],['星期','Weekday'],['股息','Div amount/share'],
        ["股票分拆历史","Stock Split History"],
        ['分拆比例','Split Ratio'],
        ["公司基本信息","Company Profile"],
        ["公司高管信息","Company Senior Management"],["公司高管:","Senior Management:"],
        ["基本财务比率","Key Financial Ratios"],["基本财务比率TTM","Key Financial Ratios TTM"],
        ["财报主要项目","Financial Statement Overview"],
        ["基本市场比率","Key Market Ratios"],
        ["一般风险指数","General Risk Indicators"],
        ["注：数值越小风险越低","Note: Smaller value indicates lower risk"],
        ["可持续发展风险","Risk of Sustainable Development"],
        ["注：分数越小风险越低","Note: Smaller score indicates lower risk"],
        #['\b岁 (生于','years old(born @'],['years old(born @','\b岁 (生于'],
        #['总薪酬','Total compensation'],['Total compensation','总薪酬'],
        ["均值","average "],
        ["投资组合的可持续发展风险","投资组合的可持续发展风险"],
        ["投资组合:","投资组合:"],
        ["ESG评估分数:","ESG risk score:"],
        ["   EP分数(基于","   EP risk score(based on"],
        ["   CSR分数(基于","   CSR risk score(based on"],
        ["   CG分数(基于","   CG risk score(based on"],
        ["   ESG总评分数","   Total ESG risk score"],
        ["注：分数越高, 风险越高.","Note: the higher the score, the higher the risk."],
        
        [": 基于年(季)报的业绩历史对比",": Performance Comparison Based on Annual(Quarterly) Reports"],
        [": 基于年(季)报的业绩历史",": Performance History Based on Annual(Quarterly) Reports"],
        
        ["中国债券市场月发行量","中国债券市场月发行量"],
        ["数据来源：中国银行间市场交易商协会(NAFMII)，","数据来源：中国银行间市场交易商协会(NAFMII)，"],
        ["发行量","发行量"],["金额(亿元)","金额(亿元)"],
        ["中国银行间市场债券现券即时报价","中国银行间市场债券现券即时报价"],
        ["，前","，前"],["名）***","名）***"],
        ["中国债券市场月发行量","中国债券市场月发行量"],
        ["价格","价格"],["成交量","成交量"],
        
        ["按照收益率从高到低排序","按照收益率从高到低排序"],
        ["按照发行时间从早到晚排序","按照发行时间从早到晚排序"],
        ["按照发行时间从晚到早排序","按照发行时间从晚到早排序"],
        ["按照报价机构排序","按照报价机构排序"],
        ["按照涨跌幅从高到低排序","按照涨跌幅从高到低排序"],
        ["按照涨跌幅从低到高排序","按照涨跌幅从低到高排序"],
        ["按照交易时间排序","按照交易时间排序"],
        ["按照成交量从高到低排序","按照成交量从高到低排序"],
        ["按照成交量从低到高排序","按照成交量从低到高排序"],
        ['时间','时间'],['债券代码','债券代码'],
        
        ['债券名称','债券名称'],['成交价','成交价'],['涨跌(元)','涨跌(元)'],
        ['开盘价','开盘价'],['最高价','最高价'],['最低价','最低价'],
        ['买入价','买入价'],['卖出价','卖出价'],['收盘价','收盘价'],
        ["沪深交易所债券市场现券即时成交价（","沪深交易所债券市场现券即时成交价（"],
        
        ["数据来源：新浪财经，","数据来源：新浪财经，"],
        ['沪深债券收盘价历史行情：','沪深债券收盘价历史行情：'],
        ["按照代码从小到大排序","按照代码从小到大排序"],
        ["按照代码从大到小排序","按照代码从大到小排序"],
        ["沪深交易所可转债现券即时行情（","沪深交易所可转债现券即时行情（"],
        ['沪深市场可转债收盘价历史行情：','沪深市场可转债收盘价历史行情：'],
        ["政府债券列表","政府债券列表"],
        ['中国','中国'],['美国','美国'],['日本','日本'],['韩国','韩国'],
        ['泰国','泰国'],['越南','越南'],['印度','印度'],['德国','德国'],
        ['法国','法国'],['英国','英国'],['意大利','意大利'],['西班牙','西班牙'],
        ['俄罗斯','俄罗斯'],['加拿大','加拿大'],['澳大利亚','澳大利亚'],
        ['新西兰','新西兰'],['新加坡','新加坡'],['马来西亚','马来西亚'],
        
        ['全球政府债券收盘价历史行情：','全球政府债券收盘价历史行情：'],
        ["数据来源：英为财情，","数据来源：英为财情，"],
        ['到期收益率变化','到期收益率变化'],
        ['到期收益率%','到期收益率%'],
        ['债券价格','债券价格'],
        ["债券价格与到期收益率的关系","债券价格与到期收益率的关系"],
        ["债券价格","债券价格"],
        ["到期收益率及其变化幅度","到期收益率及其变化幅度"],
        ["债券面值","债券面值"],
        ["，票面利率","，票面利率"],
        ["每年付息","每年付息"],
        ["次，到期年数","次，到期年数"],
        ["，到期收益率","，到期收益率"],
        ['到期时间(年)','到期时间(年)'],
        ['债券价格变化','债券价格变化'],
        ["债券价格的变化与到期时间的关系","债券价格的变化与到期时间的关系"],
        ["债券价格的变化","债券价格的变化"],
        ["次，期限","次，期限"],
        ["年","年"],
        ["债券价格的变化速度","债券价格的变化速度"],
        
        ["债券到期时间与债券价格的变化速度","债券到期时间与债券价格的变化速度"],
        ["收益率下降导致的债券价格增加","收益率下降导致的债券价格增加"],
        ["收益率上升导致的债券价格下降","收益率上升导致的债券价格下降"],
        ["收益率上升导致的债券价格下降(两次翻折后)","收益率上升导致的债券价格下降(两次翻折后)"],
        ["到期收益率与债券价格变化的非对称性","到期收益率与债券价格变化的非对称性"],
        ["到期收益率及其变化幅度","到期收益率及其变化幅度"],
        ["数据来源：中债登/中国债券信息网，","数据来源：中债登/中国债券信息网，"],
        ['中国债券信息网','中国债券信息网'],
        ["中国债券价格指数走势","中国债券价格指数走势"],
        ["到期期限对债券转换因子的影响","到期期限对债券转换因子的影响"],
        ["名义券利率         :","名义券利率         :"],
        ["债券票面利率       :","债券票面利率       :"],
        ["每年付息次数       :","每年付息次数       :"],
        ["到下个付息日的天数 :","到下个付息日的天数 :"],
        ['债券到期期限*','债券到期期限*'],
        ['转换因子','转换因子'],
        
        ["*指下一付息日后剩余的付息次数","*指下一付息日后剩余的付息次数"],
        ['债券的转换因子','债券的转换因子'],
        ["到期期限对债券转换因子的影响","到期期限对债券转换因子的影响"],
        ['下一付息日后剩余的付息次数','下一付息日后剩余的付息次数'],
        ["【债券描述】名义券利率：","【债券描述】名义券利率："],
        [", 债券票面利率：",", 债券票面利率："],
        [', 每年付息次数：',', 每年付息次数：'],
        ["到下一付息日的天数：","到下一付息日的天数："],
        ["债券票息率对转换因子的影响","债券票息率对转换因子的影响"],
        ["名义券利率                 :","名义券利率                 :"],
        ["每年付息次数               :","每年付息次数               :"],
        ["到下个付息日的天数         :","到下个付息日的天数         :"],
        ["下个付息日后剩余的付息次数 :","下个付息日后剩余的付息次数 :"],
        ['债券票息率','债券票息率'],
        ["债券票息率对转换因子的影响","债券票息率对转换因子的影响"],
        ['票息率','票息率'],
        ["下一付息日后剩余的付息次数：","下一付息日后剩余的付息次数："],
        ["债券票息率与债券价格变化风险的关系","债券票息率与债券价格变化风险的关系"],
        ["票息率及其变化幅度","票息率及其变化幅度"],
        ["债券面值","债券面值"],
        
        ["，票面利率","，票面利率"],
        ["每年付息","每年付息"],
        ["次，期限","次，期限"],
        ["，到期收益率","，到期收益率"],
        
        ["======= 中国公募基金种类概况 =======","======= 中国公募基金种类概况 ======="],
        ["公募基金总数：","公募基金总数："],
        ["其中包括：","其中包括："],
        ["数据来源：东方财富/天天基金,","数据来源：东方财富/天天基金,"],
        ["\n===== 中国开放式基金排名：单位净值最高前十名 =====","\n===== 中国开放式基金排名：单位净值最高前十名 ====="],
        ["\n===== 中国开放式基金排名：累计净值最高前十名 =====","\n===== 中国开放式基金排名：累计净值最高前十名 ====="],
        ["\n===== 中国开放式基金排名：手续费最高前十名 =====","\n===== 中国开放式基金排名：手续费最高前十名 ====="],
        ["共找到披露净值信息的开放式基金数量:","共找到披露净值信息的开放式基金数量:"],
        ["基金类型:","基金类型:"],
        ["  净值日期:","  净值日期:"],
        ['单位净值','单位净值'],
        ['累计净值','累计净值'],
        ['净值','净值'],
        ["开放式基金的净值趋势：","开放式基金的净值趋势："],
        ['累计收益率%','累计收益率%'],
        ['收益率%','收益率%'],
        ["开放式基金的累计收益率趋势：","开放式基金的累计收益率趋势："],
        ['同类排名','同类排名'],
        ['同类排名百分比','同类排名百分比'],
        ["开放式基金的近三个月收益率排名趋势：","开放式基金的近三个月收益率排名趋势："],
        ['开放式基金总排名','开放式基金总排名'],
        ["\n======= 中国货币型基金排名：7日年化收益率最高前十名 =======","\n======= 中国货币型基金排名：7日年化收益率最高前十名 ======="],
        ["共找到披露收益率信息的货币型基金数量:","共找到披露收益率信息的货币型基金数量:"],
        ["收益率日期:","收益率日期:"],
        ['7日年化%','7日年化%'],
        ["货币型基金的7日年化收益率趋势：","货币型基金的7日年化收益率趋势："],
        ["\n===== 中国ETF基金排名：单位净值最高前十名 =====","\n===== 中国ETF基金排名：单位净值最高前十名 ====="],
        ["\n===== 中国ETF基金排名：累计净值最高前十名 =====","\n===== 中国ETF基金排名：累计净值最高前十名 ====="],
        ["\n===== 中国开放式基金排名：市价最高前十名 =====","\n===== 中国开放式基金排名：市价最高前十名 ====="],
        ["共找到披露净值信息的ETF基金数量:","共找到披露净值信息的ETF基金数量:"],
        ["基金类型:","基金类型:"],
        
        ["  净值日期:","  净值日期:"],
        ["  数据来源：东方财富/天天基金,","  数据来源：东方财富/天天基金,"],
        ['人民币元','人民币元'],
        ["ETF基金的净值趋势：","ETF基金的净值趋势："],
        ["\n===== 中国基金投资机构概况 =====","\n===== 中国基金投资机构概况 ====="],
        ["机构（会员）数量：","机构（会员）数量："],
        ["其中包括：","其中包括："],
        ["数据来源：中国证券投资基金业协会","数据来源：中国证券投资基金业协会"],
        ["\n===== 中国基金投资机构会员代表概况 =====","\n===== 中国基金投资机构会员代表概况 ====="],
        ["会员代表人数：","会员代表人数："],
        ["其中工作在：","其中工作在："],
        ["\n===== 中国私募基金管理人角色分布 =====","\n===== 中国私募基金管理人角色分布 ====="],
        ["地域：","地域："],
        ["法定代表人/执行合伙人数量：","法定代表人/执行合伙人数量："],
        ['\b, 占比全国','\b, 占比全国'],
        ["其中, 角色分布：","其中, 角色分布："],
        ["\n== 中国私募基金管理人地域分布概况 ==","\n== 中国私募基金管理人地域分布概况 =="],
        ["其中分布在：","其中分布在："],
        ["上述地区总计占比:","上述地区总计占比:"],
        ["\n== 中国私募基金管理人的产品与运营概况 ==","\n== 中国私募基金管理人的产品与运营概况 =="],
        ["产品数量：","产品数量："],
        ["产品的运营方式分布：","产品的运营方式分布："],
        ["产品的运营状态分布：","产品的运营状态分布："],
        ["\n===== 中国推出产品数量最多的私募基金管理人 =====","\n===== 中国推出产品数量最多的私募基金管理人 ====="],
        ["上述产品总计占比:","上述产品总计占比:"],
        ["\n===== 中国私募基金管理人的产品托管概况 =====","\n===== 中国私募基金管理人的产品托管概况 ====="],
        ["上述金融机构托管产品总计占比:","上述金融机构托管产品总计占比:"],
        ["\n===== 股票分红历史 =====","\n===== 股票分红历史 ====="],
        ["\n===== 股票分拆历史 =====","\n===== 股票分拆历史 ====="],
        ["\n===== 投资组合的可持续发展风险 =====","\n===== 投资组合的可持续发展风险 ====="],
        
        ["杜邦分析分解项目","DuPont Identity Items"],
        ["财报日期及类型","End date & report type"],
        ["【图示放大比例】","[Barchart multiplier]"],
        ["杜邦分析对比图","DuPont Identity Comparison"],
        ["杜邦分析分项数据表","DuPont Identity Item Datasheet"],
        ["企业横向对比: 实际税率","Company Comparison: Actual Tax Rate"],
        ["实际所得税率","Actual Income Tax Rate"],
        ["杜邦分析分项数据表","DuPont Identity Item Datasheet"],
        
        
        ], columns=['code','codename'])

    try:
        codename=codedict[codedict['code']==code]['codename'].values[0]
    except:
        #未查到翻译文字，返回原文
        codename=code
   
    return codename

if __name__=='__main__':
    code='数据来源：新浪/stooq，'
    print(texttranslate(code))

#==============================================================================


def tickertranslate(code):
    """
    套壳函数
    输入：证券代码。输出：证券名称
    """
    codename=codetranslate(code)
    return codename

if __name__=='__main__':
    code='GOOG'
    print(tickertranslate('000002.SZ'))
    print(tickertranslate('09988.HK'))

#==============================================================================
if __name__=='__main__':
    _,_,tickerlist,sharelist,ticker_type=decompose_portfolio(portfolio)
    leading_blanks=2

def print_tickerlist_sharelist(tickerlist,sharelist,leading_blanks=2,ticker_type='auto'):
    """
    功能：纵向打印投资组合的成分股和持股比例
    输入：
    tickerlist：成分股列表
    sharelist：持股份额列表
    leading_blanks：打印前导空格数
    """
    #检查成分股与持仓比例个数是否一致
    if not (len(tickerlist) == len(sharelist)):
        print("  #Error(): numbers of tickers and shares are not same")
        return
    
    #计算最长的代码长度，便于对齐
    max_ticker_len=0
    for t in tickerlist:
        tlen=len(t)
        #print(t,tlen)
        if tlen > max_ticker_len: #if的执行语句放在这里可能有bug
            max_ticker_len=tlen
    
    # 将原投资组合的权重存储为numpy数组类型，为了合成投资组合计算方便
    import numpy as np
    sharelist_array = np.array(sharelist)
    total_shares=sharelist_array.sum()
    weights=sharelist_array/total_shares 

    #预处理ticker_type
    ticker_type_list=ticker_type_preprocess_mticker_mixed(tickerlist,ticker_type)
    
    import pandas as pd
    df=pd.DataFrame(columns=['证券代码','证券名称','持仓比例'])
    for t in tickerlist:
        pos=tickerlist.index(t)
        tt=ticker_type_list[pos]
        tname=ticker_name(t,tt)
        tweight=weights[pos]
        
        row=pd.Series({'证券代码':t,'证券名称':tname,'持仓比例':tweight})
        try:
            df=df.append(row,ignore_index=True)
        except:
            df=df._append(row,ignore_index=True)
    
    #按持仓比例降序
    df.sort_values(by='持仓比例',ascending=False,inplace=True)
    """
    #打印对齐
    pd.set_option('display.max_columns', 1000)
    pd.set_option('display.width', 1000)
    pd.set_option('display.max_colwidth', 1000)
    pd.set_option('display.unicode.ambiguous_as_wide', True)
    pd.set_option('display.unicode.east_asian_width', True)
    
    print(df.to_string(index=False,header=False))
    """
    
    #打印
    df.reset_index(inplace=True) #必须，不然排序不起作用
    for i in range(len(df)):
        rows = df.loc[[i]]
        tcode=rows['证券代码'].values[0]
        tname=rows['证券名称'].values[0]
        tweight=rows['持仓比例'].values[0]
        print(' '*leading_blanks,tcode+' '*(max_ticker_len-len(tcode))+':',tname,'\b,',round(tweight,4)) 
        """
        values = rows.to_string(index=False,header=False)
        """
    
    return
    
if __name__=='__main__':
    print_tickerlist_sharelist(tickerlist,sharelist,leading_blanks=2)

#==============================================================================
#==============================================================================
#整理证券名称
#==============================================================================
#==============================================================================
#==============================================================================
if __name__=='__main__':
    #更新所有证券名称
    update_all_names2files()

def update_all_names2files():
    """
    功能：更新股票(中港美)、基金(沪深)和债券(沪深)名称至文件中(S:/siat)
    """
    print("  Updating stock names in China, China HK and US markets ... ...")
    try:
        df1=update_stock_names()
    except:
        pass
    
    print("\n  Updating exchange fund names in China markets ... ...")
    try:
        df2=update_fund_names_china()
    except:
        pass
    
    print("\n  Updating exchange bond names in China markets ... ...")
    try:
        df3=update_exchange_bond_name_china()
    except:
        pass
    
    return

#==============================================================================
if __name__=='__main__':
    ticker=''
    base='fund'
    
    df_dup=check_duplicate_code(ticker='',base='fund')
    df_dup=check_duplicate_code(ticker='018003',base='fund')
    df_dup=check_duplicate_code(ticker='000001',base='fund')
    
def check_duplicate_code(ticker='',base='fund',printout=True):
    """
    功能；查询重叠的基金/债券代码
    若ticker不为空，且在基金中找到，则只查该代码，否则查询所有交易所基金代码
    """
    
    #取出所有交易所债券代码
    df_bond=file_position(file='exchange_bond_china.pickle',package='siat',mode='read')
    df_bond['code6']=df_bond['代码'].apply(lambda x: x[-6:])
    list_bond=list(df_bond['code6'])

    #取出所有基金代码
    df_fund=file_position(file='fund_china.pickle',package='siat',mode='read')
    list_fund=list(df_fund['基金代码'])
    
    #取出所有A股港股美股代码
    df_stock=file_position(file='stock_info.pickle',package='siat',mode='read')
    df_stock['A_Code6']=df_stock['SYMBOL'].apply(lambda x: x[:6] if '.SS' in x or '.SZ' in x or '.BJ' in x else '')
    df_stock_A=df_stock[df_stock['A_Code6'] != '']
    list_stock=list(df_stock_A['A_Code6'])

    df_dup=pd.DataFrame(columns=('code','stock code','stock name','bond code','bond name','fund code','fund name'))

    #查找所有代码：基于基金
    if ticker == '' and base == 'fund':
        for t in list_fund:
            code_fund=df_fund[df_fund['基金代码']==t]['基金代码'].values[0]
            name_fund=df_fund[df_fund['基金代码']==t]['基金简称'].values[0]
            
            #查找债券代码
            code_bond=''; name_bond=''
            if t in list_bond:
                try:
                    code_bond=df_bond[df_bond['code6']==t]['代码'].values[0]
                    name_bond=df_bond[df_bond['code6']==t]['名称'].values[0]
                except: pass
            
            #查找股票代码
            code_stock=''; name_stock=''
            if t in list_stock:
                try:
                    code_stock=df_stock_A[df_stock_A['A_Code6']==t]['SYMBOL'].values[0]
                    name_stock=df_stock_A[df_stock_A['A_Code6']==t]['CNAME'].values[0]
                except: pass
            
            if name_bond != '' or name_stock != '':
                row=pd.Series({'code':t,'stock code':code_stock,'stock name':name_stock,'bond code':code_bond,'bond name':name_bond,'fund code':code_fund,'fund name':name_fund})
                df_dup=df_dup._append(row,ignore_index=True)
            
            print_progress_percent2(t,list_fund,steps=10,leading_blanks=4)
            
    #查找单个代码
    if ticker != '':
        #截取6位数字
        prefix6=ticker[:6]; suffix6=ticker[-6:]
        if prefix6.isdigit():
            t=prefix6
        elif suffix6.isdigit():
            t=suffix6
        else:
            t=ticker
            
        #查找股票代码
        code_stock=''; name_stock=''
        if t in list_stock:
            try:
                code_stock=df_stock_A[df_stock_A['A_Code6']==t]['SYMBOL'].values[0]
                name_stock=df_stock_A[df_stock_A['A_Code6']==t]['CNAME'].values[0]
            except: pass
        
        #查找债券代码
        code_bond=''; name_bond=''
        if t in list_bond:
            try:
                code_bond=df_bond[df_bond['code6']==t]['代码'].values[0]
                name_bond=df_bond[df_bond['code6']==t]['名称'].values[0]
            except: pass
    
        #查找基金代码
        code_fund=''; name_fund=''
        if t in list_fund:
            try:
                code_fund=df_fund[df_fund['基金代码']==t]['基金代码'].values[0]
                name_fund=df_fund[df_fund['基金代码']==t]['基金简称'].values[0]
            except: pass
    
        row=pd.Series({'code':t,'stock code':code_stock,'stock name':name_stock,'bond code':code_bond,'bond name':name_bond,'fund code':code_fund,'fund name':name_fund})
        df_dup=df_dup._append(row,ignore_index=True)
        
        if printout:
            print('') #空一行
            if code_stock != '':
                print("  股票："+code_stock+'，'+name_stock)
            if code_bond != '':
                print("  债券："+code_bond+'，'+name_bond)                
            if code_fund != '':
                print("  基金："+code_fund+'，'+name_fund) 
                
            if code_stock == '' and code_bond == '' and code_fund == '':
                print("  未找到代码为"+ticker+"的证券")
                
    return df_dup


#==============================================================================
if __name__=='__main__':
    ticker='600519.SS' #股票
    ticker='159995.SZ' #基金
    ticker='010107.SS' #债券/基金重码
    ticker='sh010303' #国债/基金重码
    ticker='sh018001' #金融债
    ticker='PDD'
    ticker='IBM'
    ticker='600000.SS'
    ticker='ULVR.L'
    
    ticker_type='auto'
    ticker_type='bond'
    
    ticker={'Market':('US','^SPX','中概教培组合'),'EDU':0.5,'TAL':0.3,'TEDU':0.2}
    
    ticker1_name(ticker,ticker_type)
    ticker1_name(ticker)

def ticker1_name(ticker,ticker_type='auto'):
    """
    功能：翻译单个证券名称：股票，基金，债券，投资组合
    """
    DEBUG=False
    if DEBUG:
        print("DEBUG: ticker=",ticker)
    
    #投资组合
    if isinstance(ticker,dict):
        return portfolio_name(ticker)
    
    #非字符串
    if not isinstance(ticker,str):
        return ticker
    
    #快速转换
    """
    if ticker_type=='auto':
        tname=codetranslate(ticker)
        if tname != ticker: #翻译成功
            return tname
    """
    tname=codetranslate(ticker)
    if tname != ticker or ticker in ["IBM"]: #翻译成功，注意证券代码与其名称相同的情形，例如IBM
        return tname

    tname=ectranslate(ticker)
    if tname != ticker: 
        return tname
    
    symbol=ticker1_cvt2yahoo(ticker)
    
    #申万行业指数
    _,_,flag=split_prefix_suffix(ticker)
    if flag in ['SW']:
        swname=industry_sw_name(symbol)
        if '申万' not in swname: swname='申万' + swname
        if '指数' not in swname: swname=swname + '指数'       
        tname=swname
        return tname
    
    #确定查询优先顺序
    if isinstance(ticker_type,list):
        ticker_type=ticker_type[0]
    
    ttlist=['stock','bond','fund']
    if ticker_type in ['fund']:
        ttlist=['fund','stock','bond']
    elif ticker_type in ['bond']:
        ttlist=['bond','stock','fund']
    
    #循环查询，查到则跳出
    lang=check_language()
    tname=symbol
    for tt in ttlist:
        #查找证券名称文件：优先股票
        if tt in ['stock']:
            df1=file_position(file='stock_info.pickle',package='siat',mode='read')
            
            #港股
            if '.HK' in symbol and len(symbol)==8: symbol=symbol[1:]
            
            try:
                if lang == "Chinese":
                    tname=df1[df1['SYMBOL']==symbol]['CNAME'].values[0]
                else:
                    tname=df1[df1['SYMBOL']==symbol]['ENAME'].values[0]
            except: pass
            if tname != symbol or symbol in ['IBM']: break
            else:
                tname=get_stock_name_china_sina(symbol[:6])
                if tname=='': tname=symbol
                if tname != symbol and tname != '': break
                
        
        #查找证券名称文件：次优先交易所债券
        if tt in ['bond']:
            df3=file_position(file='exchange_bond_china.pickle',package='siat',mode='read')
            symbolak=ticker1_cvt2ak(symbol)
            try:
                tname=df3[df3['代码']==symbolak]['名称'].values[0]
                return tname
            except: pass   
            if tname != symbol: break
        
        #查找证券名称文件：最后基金
        if tt in ['fund']:
            df2=file_position(file='fund_china.pickle',package='siat',mode='read')
            symbol6=symbol[:6]
            try:
                tname=df2[df2['基金代码']==symbol6]['基金简称'].values[0]
            except: pass  
            if tname != symbol: 
                #注意：绘图时有基于‘基金’字符的判断，决定显示收盘价还是单位净值
                if '基金' not in tname: tname=tname + '基金'
                break
    
    #如未查到，尝试stooq和雅虎名称，限英文名称
    if tname==symbol or tname=='':
        #不包括中国大陆和香港证券，这些都应在前面查到?新上市的可能查不到
        #if ('.SS' not in symbol) and ('.SH' not in symbol) and ('.SZ' not in symbol) and ('.BJ' not in symbol) and ('.HK' not in symbol):
        tname=get_stock_name1_en(symbol)
        if tname!=symbol:
            return tname
    
    #加港股标记
    if ('.HK' in ticker) and not (text_lang("港股","(HK)") in tname):
        tname=tname+text_lang("港股","(HK)")
        #加港股人民币柜台标志
        HKcode=ticker.split('.')[0]
        if len(HKcode)==5 and HKcode[0]=='8' and not (text_lang("人民币","(RMB)") in tname):
            tname=tname+text_lang("人民币","(RMB)")
        
    #加美股标记：绝大多数中概股在前面已经查完，真正美股没必要标注美股
    """
    if len(ticker.split('.'))==1 and not (text_lang("美股","(US)") in tname):
        tname=tname+text_lang("美股","(US)")
    """
    
    return tname

#==============================================================================
if __name__=='__main__':
    ticker='600519.SS' #股票
    ticker='XAUUSD'    #一盎司黄金的美元价格
    ticker={'Market':('US','^SPX','中概教培组合'),'EDU':0.5,'TAL':0.3,'TEDU':0.2}
    pf={'Market':('US','^SPX','中概教培组合'),'EDU':0.5,'TAL':0.3,'TEDU':0.2}
    ticker=['600519.SS','sh018003',pf]
    
    ticker_type='auto'
    ticker_type=['auto','bond']
    
    ticker_name(ticker,ticker_type)
    
def ticker_name(ticker,ticker_type='auto'):
    """
    功能：翻译单个或多个证券名称：股票，基金，债券，投资组合
    """
    if isinstance(ticker,str) or isinstance(ticker,dict):
        #单只原生证券或投资组合
        tname=ticker1_name(ticker,ticker_type)
    elif isinstance(ticker,list):
        #多只原生证券或投资组合
        if isinstance(ticker_type,str):
            ticker_type=[ticker_type] * len(ticker)
        elif isinstance(ticker_type,list):
            if len(ticker) > len(ticker_type):
                ticker_type=ticker_type + [ticker_type[-1]] * (len(ticker) - len(ticker_type))
        else:
            ticker_type=['auto'] * len(ticker)
        
        tname=[]
        for t in ticker:
            pos=ticker.index(t)
            tname=tname + [ticker1_name(t,ticker_type[pos])]
    else: tname=ticker
            
    return tname

#==============================================================================
if __name__=='__main__':
    ticker='600519.SS'
    ticker='000858.SZ'
    
    ticker='SH600519'
    ticker='sh600519'
    ticker='sz000858'
    
    ticker='sz600519'
    ticker='sh000858'
    
    ticker='600519.SH'
    ticker='600519.sh'
    ticker='000858.sz'
    
    ticker='000858.sh'
    ticker='600519.sz'
    
    ticker='600519'
    ticker='000858'
    ticker='600519.CN'
    ticker='000858.CN'
    ticker='801010.SW'
    ticker='880410.ZZ'
    
    ticker='01210.HK'
    ticker='AAPL'
    ticker='6758.T'
    ticker='SONA.F'
    
    ticker1_cvt2yahoo(ticker)
    
def ticker1_cvt2yahoo(ticker):
    """
    功能：将一只股票、基金、债券代码转换为siat内部默认的yahoo格式
    情形：后缀，前缀，无后缀和前缀
    注意：中证行业代码若为沪深交易所收藏的，仍以SS/SZ为后缀，不可用ZZ后缀
    """
    ticker1=ticker.upper() #转为大写
    
    #后缀
    result,prefix,suffix=split_prefix_suffix(ticker1)
    if suffix in ['SS','SH','SZ','BJ','CN','SW','ZZ'] and len(prefix)==6:
        if suffix in ['SH']:
            suffix1='SS'
        elif suffix in ['CN']:
            suffix1,_=china_security_identify(prefix)
        else:
            suffix1=suffix
            
        """
        #检查是否搞错SS/SZ/BJ
        if suffix1 in ['SS','SZ','BJ']:
            suffix1,_=china_security_identify(prefix)
        """
        ticker2=prefix+'.'+suffix1            
        return ticker2

    #前缀
    head2=ticker1[:2]
    rest2=ticker1[2:]
    if head2 in ['SH','SZ','BJ','SW','ZZ'] and len(rest2)==6:
        #suffix1,_=china_security_identify(rest2)
        if head2 in ['SH']:
            suffix1='SS'
        else:
            suffix1=head2
        """    
        #检查是否搞错SS/SZ/BJ
        if suffix1 in ['SS','SZ','BJ']:
            suffix1,_=china_security_identify(rest2)
        """    
        ticker2=rest2+'.'+suffix1            
        return ticker2

    #无前后缀，6位数字，默认为A股
    if is_all_digits(ticker1) and len(ticker1) == 6:    
        suffix1,_=china_security_identify(ticker1)
        ticker2=ticker1+'.'+suffix1            
        return ticker2

    #其他：直接返回
    return ticker1
    
#==============================================================================
if __name__=='__main__':
    ticker=['600519.SS','sz000858','002594.sz','aapl']

    tickers_cvt2yahoo(ticker)

def tickers_cvt2yahoo(ticker):
    """
    功能：将多只股票、基金、债券代码转换为siat内部默认的yahoo格式
    """
    #单个字符串：返回字符串
    if isinstance(ticker,str):
        result=ticker1_cvt2yahoo(ticker)    
        return result

    #列表：返回列表    
    if isinstance(ticker,list): #避免下面的循环出错
        tickerlist=[]
        for t in ticker:
            t2=ticker1_cvt2yahoo(t)
            tickerlist=tickerlist+[t2]
        
        result=tickerlist
        return result
    
    #其他：直接返回
    return ticker    

#==============================================================================
if __name__=='__main__':
    ticker='SH600519'
    ticker='sh600519'
    ticker='sz000858'
    
    ticker='sz600519'
    ticker='sh000858'
    
    ticker='600519.SH'
    ticker='600519.sh'
    ticker='000858.sz'
    
    ticker='000858.sh'
    ticker='600519.sz'
    
    ticker='600519'
    ticker='000858'
    ticker='600519.CN'
    ticker='000858.CN'
    ticker='801010.SW'
    ticker='880410.ZZ'
    
    ticker='sh149996'
    
    ticker='01210.HK'
    ticker='AAPL'
    ticker='6758.T'
    ticker='SONA.F'
    
    ticker1_cvt2ak(ticker)
    
def ticker1_cvt2ak(ticker):
    """
    功能：将一只股票、基金、债券代码转换为akshare格式
    情形：后缀，前缀，无后缀和前缀
    注意：中证行业代码若为沪深交易所收藏的，仍以SS/SZ为后缀，不可用ZZ后缀
    """
    ticker1=ticker.upper() #转为大写
    
    #后缀
    result,prefix,suffix=split_prefix_suffix(ticker1)
    if suffix in ['SS','SH','SZ','BJ','CN'] and len(prefix)==6:
        if suffix in ['SH','SS']: prefix1='sh'
        if suffix in ['SZ']: prefix1='sz'
        if suffix in ['BJ']: prefix1='bj'
        if suffix in ['CN']:            
            suffix1,_=china_security_identify(prefix)
            prefix1='sh'
            if suffix1 in ['SS']: prefix1='sh'
            if suffix1 in ['SZ']: prefix1='sz'
            if suffix1 in ['BJ']: prefix1='bj'
        """
        #检查是否搞错SS/SZ/BJ
        if suffix in ['SS','SH','SZ','BJ']:
            suffix1,_=china_security_identify(prefix)
            if suffix1 in ['SS','SH']: prefix1='sh'
            if suffix1 == 'SZ': prefix1='sz'
            if suffix1 == 'BJ': prefix1='bj'
        """
        ticker2=prefix1+prefix            
        return ticker2

    #前缀
    head2=ticker1[:2]
    rest2=ticker1[2:]
    if head2 in ['SH','SS','SZ','BJ'] and len(rest2)==6:
        if head2 in ['SH','SS']: prefix1='sh'
        if head2 in ['SZ']: prefix1='sz'
        if head2 in ['BJ']: prefix1='bj'
        
        """            
        #检查是否搞错SS/SZ/BJ
        if head2 in ['SH','SS','SZ','BJ']:
            suffix1,_=china_security_identify(rest2)
            if suffix1 == 'SS': prefix1='sh'
            if suffix1 == 'SZ': prefix1='sz'
            if suffix1 == 'BJ': prefix1='bj'
        """    
        ticker2=prefix1+rest2            
        return ticker2

    #无前后缀，6位数字，默认为A股
    if is_all_digits(ticker1) and len(ticker1) == 6:    
        suffix1,_=china_security_identify(ticker1)
        prefix1='sh'
        if head2 in ['SH','SS']: prefix1='sh'
        if head2 in ['SZ']: prefix1='sz'
        if head2 in ['BJ']: prefix1='bj'
        
        ticker2=prefix1+ticker1            
        return ticker2

    #其他：直接返回
    return ticker1
    
#==============================================================================
if __name__=='__main__':
    ticker=['600519.SS','sz000858','002594.sz','aapl']

    tickers_cvt2ak(ticker)

def tickers_cvt2ak(ticker):
    """
    功能：将多只股票、基金、债券代码转换为akshare格式
    """
    #单个字符串：返回字符串
    if isinstance(ticker,str):
        result=ticker1_cvt2ak(ticker)    
        return result

    #列表：返回列表    
    if isinstance(ticker,list): #避免下面的循环出错
        tickerlist=[]
        for t in ticker:
            t2=ticker1_cvt2ak(t)
            tickerlist=tickerlist+[t2]
        
        result=tickerlist
        return result
    
    #其他：直接返回
    return ticker    


#==============================================================================
if __name__=='__main__':
    s='123456'
    s='123456.'
    s='123456a'

    is_all_digits(s)
 
def is_all_digits(s):
    """
    功能：检查字符串s是否为全数字构成
    """
    import re
    return bool(re.match(r'^\d+$', s))

#==============================================================================
if __name__=='__main__':
    ticker6='AAPL'
    ticker6='01211'
    ticker6='600519'
    ticker6='149996'
    
    china_security_identify(ticker6)
    
def china_security_identify(ticker6):
    """
    功能：区分中国内地证券代码前缀，返回后缀SS/SZ/BJ
    情形：股票，基金，债券，指数
    注意：ticker6需为6位数字字符，目前仅限沪深京交易所，未包括期货期权交易所
    """
    suffix='SS'
    stype='stock'
    
    #检查是否为6位数字字符
    if not is_all_digits(ticker6) or len(ticker6) != 6:
        suffix=''
        stype=''
        return suffix,stype
        
    head1=ticker6[:1]
    head2=ticker6[:2]
    head3=ticker6[:3]
    
    #股票代码
    if head2 in ['60','68']: #上交所：60-主板，68-科创板
        suffix='SS'
        stype='stock'
        return suffix,stype
    if head2 in ['00','30']: #深交所：00-主板，30-创业板
        suffix='SZ'
        stype='stock'
        return suffix,stype
    if head1 in ['8','4']: #北交所
        suffix='BJ'  
        stype='stock'
        return suffix,stype
    
    #沪深基金
    if head2 in ['50','51','56','58']: #上交所：50-封闭式，51-ETF
        suffix='SS'
        stype='fund'
        return suffix,stype
    if head2 in ['15','16','18']: #深交所：15-ETF，16-LOF，18-封闭式
        suffix='SZ'
        stype='fund'
        return suffix,stype
    
    #沪深债券
    if head3 in ['271','270','240','188','185','184','175','163','155','152', \
                 '143','138','137','136','127','124','122','118','115','113', \
                 '100','020','019','018','010']:
        suffix='SS'
        stype='bond'
        return suffix,stype
    
    #有重复
    if head3 in ['149','148','133','128','127','123','114','112','111','110', \
                 '108','102','101','100']:
        suffix='SZ'
        stype='bond'
        return suffix,stype
    
    #沪深B股
    if head3 in ['900']:
        suffix='SS'
        stype='stockb'
        return suffix,stype
    if head3 in ['200']:
        suffix='SZ'
        stype='stockb'
        return suffix,stype  

    #其他
    return '',''    
    
#==============================================================================
#==============================================================================
#申万行业分类：https://www.swhyresearch.com/institute_sw/allIndex/analysisIndex
#==============================================================================
def generate_industry_sw_list():
    """
    一次性生成更新申万行业列表：将输出的列表手工更新到translate.py中的函数industry_sw_list()
    """
    import akshare as ak
    
    #股票类指数
    sw_dff = ak.index_realtime_sw(symbol="市场表征")
    x=sw_dff.apply(lambda x: print(['F',x['指数代码'],x['指数名称']],'\b,'),axis=1)
    
    sw_df1 = ak.index_realtime_sw(symbol="一级行业")
    x=sw_df1.apply(lambda x: print(['1',x['指数代码'],x['指数名称']],'\b,'),axis=1)
    
    sw_df2 = ak.index_realtime_sw(symbol="二级行业")
    x=sw_df2.apply(lambda x: print(['2',x['指数代码'],x['指数名称']],'\b,'),axis=1)
    
    sw_df3=ak.sw_index_third_info() #三级行业
    sw_df3['行业代码']=sw_df3['行业代码'].apply(lambda x: x[:6])
    x=sw_df3.apply(lambda x: print(['3',x['行业代码'],x['行业名称']],'\b,'),axis=1)
    
    sw_dfs = ak.index_realtime_sw(symbol="风格指数")
    x=sw_dfs.apply(lambda x: print(['S',x['指数代码'],x['指数名称']],'\b,'),axis=1)
    
    sw_dfb = ak.index_realtime_sw(symbol="大类风格指数")
    x=sw_dfb.apply(lambda x: print(['B',x['指数代码'],x['指数名称']],'\b,'),axis=1)
    
    #目前问题：获取金创指数名称和历史行情出错！
    try:
        sw_dfc = ak.index_realtime_sw(symbol="金创指数")
        x=sw_dfc.apply(lambda x: print(['C',x['指数代码'],x['指数名称']],'\b,'),axis=1)
    except:
        pass
        
    #股票类指数的历史行情
    #sw_df = ak.index_hist_sw(symbol="801093", period="day") 
    #有效字段：['代码', '日期', '收盘', '开盘', '最高', '最低', '成交量', '成交额']
    
    #基金类指数
    sw_j1 = ak. index_realtime_fund_sw(symbol="基础一级")
    x=sw_j1.apply(lambda x: print(['J1',x['指数代码'],x['指数名称']],'\b,'),axis=1)
    
    sw_j2 = ak. index_realtime_fund_sw(symbol="基础二级")
    x=sw_j2.apply(lambda x: print(['J2',x['指数代码'],x['指数名称']],'\b,'),axis=1)
    
    sw_j3 = ak. index_realtime_fund_sw(symbol="基础三级")
    x=sw_j3.apply(lambda x: print(['J3',x['指数代码'],x['指数名称']],'\b,'),axis=1)
    
    sw_jf = ak. index_realtime_fund_sw(symbol="特色指数")
    x=sw_jf.apply(lambda x: print(['JF',x['指数代码'],x['指数名称']],'\b,'),axis=1)

    #基金类指数的历史行情
    #sw_fund_df = ak.index_hist_fund_sw(symbol="807110", period="day")
    #有效字段：['日期', '收盘指数', '涨跌幅']
    
    return   
    
#==============================================================================
if __name__=='__main__':
    swIndexList=industry_sw_list()

def industry_sw_list():
    """
    功能：输出申万指数代码df, 静态
    输入：
    输出：df
    
    生成方法：
    import akshare as ak
    sw_df2 = ak.index_realtime_sw(symbol="二级行业")
    sw_df2.apply(lambda x: print(['T',x['指数代码'],x['指数名称']],'\b,'),axis=1)
    """
    import pandas as pd
    industry=pd.DataFrame([
        
        #市场表征指数F，一级行业I，二级行业T，三级行业3，风格策略S，大类风格指数B，金创指数C
        ['F', '801001', '申万50'],['F', '801002', '申万中小'],['F', '801003', '申万Ａ指'],
        ['F', '801005', '申万创业'],['F', '801250', '申万制造'],['F', '801260', '申万消费'],
        ['F', '801270', '申万投资'],['F', '801280', '申万服务'],['F', '801300', '申万300指数'],    
        
        #一级行业
        ['1', '801010', '农林牧渔'],['1', '801030', '基础化工'],['1', '801040', '钢铁'],
        ['1', '801050', '有色金属'],['1', '801080', '电子'],['1', '801110', '家用电器'],
        ['1', '801120', '食品饮料'],['1', '801130', '纺织服饰'],['1', '801140', '轻工制造'],
        ['1', '801150', '医药生物'],['1', '801160', '公用事业'],['1', '801170', '交通运输'],
        ['1', '801180', '房地产'],['1', '801200', '商贸零售'],['1', '801210', '社会服务'],
        ['1', '801230', '综合'],['1', '801710', '建筑材料'],['1', '801720', '建筑装饰'],
        ['1', '801730', '电力设备'],['1', '801740', '国防军工'],['1', '801750', '计算机'],
        ['1', '801760', '传媒'],['1', '801770', '通信'],['1', '801780', '银行'],
        ['1', '801790', '非银金融'],['1', '801880', '汽车'],['1', '801890', '机械设备'],
        ['1', '801950', '煤炭'],['1', '801960', '石油石化'],['1', '801970', '环保'],
        ['1', '801980', '美容护理'],
        
        #二级行业
        ['2', '801012', '农产品加工'],['2', '801014', '饲料'],['2', '801015', '渔业'],
        ['2', '801016', '种植业'],['2', '801017', '养殖业'],['2', '801018', '动物保健Ⅱ'],
        ['2', '801032', '化学纤维'],['2', '801033', '化学原料'],['2', '801034', '化学制品'],
        ['2', '801036', '塑料'],['2', '801037', '橡胶'],['2', '801038', '农化制品'],
        ['2', '801039', '非金属材料Ⅱ'],['2', '801043', '冶钢原料'],['2', '801044', '普钢'],
        ['2', '801045', '特钢Ⅱ'],['2', '801051', '金属新材料'],['2', '801053', '贵金属'],
        ['2', '801054', '小金属'],['2', '801055', '工业金属'],['2', '801056', '能源金属'],
        ['2', '801072', '通用设备'],['2', '801074', '专用设备'],['2', '801076', '轨交设备Ⅱ'],
        ['2', '801077', '工程机械'],['2', '801078', '自动化设备'],['2', '801081', '半导体'],
        ['2', '801082', '其他电子Ⅱ'],['2', '801083', '元件'],['2', '801084', '光学光电子'],
        ['2', '801085', '消费电子'],['2', '801086', '电子化学品Ⅱ'],['2', '801092', '汽车服务'],
        ['2', '801093', '汽车零部件'],['2', '801095', '乘用车'],['2', '801096', '商用车'],
        ['2', '801101', '计算机设备'],['2', '801102', '通信设备'],['2', '801103', 'IT服务Ⅱ'],
        ['2', '801104', '软件开发'],['2', '801111', '白色家电'],['2', '801112', '黑色家电'],
        ['2', '801113', '小家电'],['2', '801114', '厨卫电器'],['2', '801115', '照明设备Ⅱ'],
        ['2', '801116', '家电零部件Ⅱ'],['2', '801124', '食品加工'],['2', '801125', '白酒Ⅱ'],
        ['2', '801126', '非白酒'],['2', '801127', '饮料乳品'],['2', '801128', '休闲食品'],
        ['2', '801129', '调味发酵品Ⅱ'],['2', '801131', '纺织制造'],['2', '801132', '服装家纺'],
        ['2', '801133', '饰品'],['2', '801141', '包装印刷'],['2', '801142', '家居用品'],
        ['2', '801143', '造纸'],['2', '801145', '文娱用品'],['2', '801151', '化学制药'],
        ['2', '801152', '生物制品'],['2', '801153', '医疗器械'],['2', '801154', '医药商业'],
        ['2', '801155', '中药Ⅱ'],
        ['2', '801156', '医疗服务'],
        ['2', '801161', '电力'],
        ['2', '801163', '燃气Ⅱ'],
        ['2', '801178', '物流'],
        ['2', '801179', '铁路公路'],
        ['2', '801181', '房地产开发'],
        ['2', '801183', '房地产服务'],
        ['2', '801191', '多元金融'],
        ['2', '801193', '证券Ⅱ'],
        ['2', '801194', '保险Ⅱ'],
        ['2', '801202', '贸易Ⅱ'],
        ['2', '801203', '一般零售'],
        ['2', '801204', '专业连锁Ⅱ'],
        ['2', '801206', '互联网电商'],
        ['2', '801218', '专业服务'],
        ['2', '801219', '酒店餐饮'],
        ['2', '801223', '通信服务'],
        ['2', '801231', '综合Ⅱ'],
        ['2', '801711', '水泥'],
        ['2', '801712', '玻璃玻纤'],
        ['2', '801713', '装修建材'],
        ['2', '801721', '房屋建设Ⅱ'],
        ['2', '801722', '装修装饰Ⅱ'],
        ['2', '801723', '基础建设'],
        ['2', '801724', '专业工程'],
        ['2', '801726', '工程咨询服务Ⅱ'],
        ['2', '801731', '电机Ⅱ'],
        ['2', '801733', '其他电源设备Ⅱ'],
        ['2', '801735', '光伏设备'],
        ['2', '801736', '风电设备'],
        ['2', '801737', '电池'],
        ['2', '801738', '电网设备'],
        ['2', '801741', '航天装备Ⅱ'],
        ['2', '801742', '航空装备Ⅱ'],
        ['2', '801743', '地面兵装Ⅱ'],
        ['2', '801744', '航海装备Ⅱ'],
        ['2', '801745', '军工电子Ⅱ'],
        ['2', '801764', '游戏Ⅱ'],
        ['2', '801765', '广告营销'],
        ['2', '801766', '影视院线'],
        ['2', '801767', '数字媒体'],
        ['2', '801769', '出版'],
        ['2', '801782', '国有大型银行Ⅱ'],
        ['2', '801783', '股份制银行Ⅱ'],
        ['2', '801784', '城商行Ⅱ'],
        ['2', '801785', '农商行Ⅱ'],
        ['2', '801881', '摩托车及其他'],
        ['2', '801951', '煤炭开采'],
        ['2', '801952', '焦炭Ⅱ'],
        ['2', '801962', '油服工程'],
        ['2', '801963', '炼化及贸易'],
        ['2', '801971', '环境治理'],
        ['2', '801972', '环保设备Ⅱ'],
        ['2', '801981', '个护用品'],
        ['2', '801982', '化妆品'],
        ['2', '801991', '航空机场'],
        ['2', '801992', '航运港口'],
        ['2', '801993', '旅游及景区'],
        ['2', '801994', '教育'],
        ['2', '801995', '电视广播Ⅱ'],
        
        #风格指数                
        ['S', '801811', '大盘指数'],
        ['S', '801812', '中盘指数'],
        ['S', '801813', '小盘指数'],
        ['S', '801821', '高市盈率指数'],
        ['S', '801822', '中市盈率指数'],
        ['S', '801823', '低市盈率指数'],
        ['S', '801831', '高市净率指数'],
        ['S', '801832', '中市净率指数'],
        ['S', '801833', '低市净率指数'],
        ['S', '801841', '高价股指数'],
        ['S', '801842', '中价股指数'],
        ['S', '801843', '低价股指数'],
        ['S', '801851', '亏损股指数'],
        ['S', '801852', '微利股指数'],
        ['S', '801853', '绩优股指数'],
        ['S', '801863', '新股指数'],
        
        #大类风格指数
        ['B', '801271', '大类风格-周期'],
        ['B', '801272', '大类风格-先进制造'],
        ['B', '801273', '大类风格-消费'],
        ['B', '801274', '大类风格-医药医疗'],
        ['B', '801275', '大类风格-科技(TMT)'],
        ['B', '801276', '大类风格-金融地产'],        
        
        #三级行业
        ['3', '850111', '种子'],
        ['3', '850113', '其他种植业'],
        ['3', '850122', '水产养殖'],
        ['3', '850142', '畜禽饲料'],
        ['3', '850151', '果蔬加工'],
        ['3', '850152', '粮油加工'],
        ['3', '850154', '其他农产品加工'],
        ['3', '850172', '生猪养殖'],
        ['3', '850173', '肉鸡养殖'],
        ['3', '850181', '动物保健Ⅲ'],
        ['3', '850322', '氯碱'],
        ['3', '850323', '无机盐'],
        ['3', '850324', '其他化学原料'],
        ['3', '850325', '煤化工'],
        ['3', '850326', '钛白粉'],
        ['3', '850335', '涂料油墨'],
        ['3', '850337', '民爆制品'],
        ['3', '850338', '纺织化学制品'],
        ['3', '850339', '其他化学制品'],
        ['3', '850382', '氟化工'],
        ['3', '850372', '聚氨酯'],
        ['3', '850135', '食品及饲料添加剂'],
        ['3', '850136', '有机硅'],
        ['3', '850341', '涤纶'],
        ['3', '850343', '粘胶'],
        ['3', '850351', '其他塑料制品'],
        ['3', '850353', '改性塑料'],
        ['3', '850354', '合成树脂'],
        ['3', '850355', '膜材料'],
        ['3', '850362', '其他橡胶制品'],
        ['3', '850363', '炭黑'],
        ['3', '850331', '氮肥'],
        ['3', '850332', '磷肥及磷化工'],
        ['3', '850333', '农药'],
        ['3', '850381', '复合肥'],
        ['3', '850523', '非金属材料Ⅲ'],
        ['3', '850442', '板材'],
        ['3', '850521', '其他金属新材料'],
        ['3', '850522', '磁性材料'],
        ['3', '850551', '铝'],
        ['3', '850552', '铜'],
        ['3', '850553', '铅锌'],
        ['3', '850531', '黄金'],
        ['3', '850544', '其他小金属'],
        ['3', '850812', '分立器件'],
        ['3', '850813', '半导体材料'],
        ['3', '850814', '数字芯片设计'],
        ['3', '850815', '模拟芯片设计'],
        ['3', '850817', '集成电路封测'],
        ['3', '850818', '半导体设备'],
        ['3', '850822', '印制电路板'],
        ['3', '850823', '被动元件'],
        ['3', '850831', '面板'],
        ['3', '850832', 'LED'],
        ['3', '850833', '光学元件'],
        ['3', '850841', '其他电子Ⅲ'],
        ['3', '850853', '品牌消费电子'],
        ['3', '850854', '消费电子零部件及组装'],
        ['3', '850861', '电子化学品Ⅲ'],
        ['3', '850922', '车身附件及饰件'],
        ['3', '850923', '底盘与发动机系统'],
        ['3', '850924', '轮胎轮毂'],
        ['3', '850925', '其他汽车零部件'],
        ['3', '850926', '汽车电子电气系统'],
        ['3', '850232', '汽车经销商'],
        ['3', '850233', '汽车综合服务'],
        ['3', '858811', '其他运输设备'],
        ['3', '858812', '摩托车'],
        ['3', '850952', '综合乘用车'],
        ['3', '850912', '商用载货车'],
        ['3', '850913', '商用载客车'],
        ['3', '851112', '空调'],
        ['3', '851116', '冰洗'],
        ['3', '851122', '其他黑色家电'],
        ['3', '851131', '厨房小家电'],
        ['3', '851141', '厨房电器'],
        ['3', '851151', '照明设备Ⅲ'],
        ['3', '851161', '家电零部件Ⅲ'],
        ['3', '851241', '肉制品'],
        ['3', '851246', '预加工食品'],
        ['3', '851247', '保健品'],
        ['3', '851251', '白酒Ⅲ'],
        ['3', '851232', '啤酒'],
        ['3', '851233', '其他酒类'],
        ['3', '851271', '软饮料'],
        ['3', '851243', '乳品'],
        ['3', '851281', '零食'],
        ['3', '851282', '烘焙食品'],
        ['3', '851242', '调味发酵品Ⅲ'],
        ['3', '851312', '棉纺'],
        ['3', '851314', '印染'],
        ['3', '851315', '辅料'],
        ['3', '851316', '其他纺织'],
        ['3', '851325', '鞋帽及其他'],
        ['3', '851326', '家纺'],
        ['3', '851329', '非运动服装'],
        ['3', '851331', '钟表珠宝'],
        ['3', '851412', '大宗用纸'],
        ['3', '851413', '特种纸'],
        ['3', '851422', '印刷'],
        ['3', '851423', '金属包装'],
        ['3', '851424', '塑料包装'],
        ['3', '851425', '纸包装'],
        ['3', '851436', '瓷砖地板'],
        ['3', '851437', '成品家居'],
        ['3', '851438', '定制家居'],
        ['3', '851439', '卫浴制品'],
        ['3', '851491', '其他家居用品'],
        ['3', '851452', '娱乐用品'],
        ['3', '851511', '原料药'],
        ['3', '851512', '化学制剂'],
        ['3', '851521', '中药Ⅲ'],
        ['3', '851522', '血液制品'],
        ['3', '851523', '疫苗'],
        ['3', '851524', '其他生物制品'],
        ['3', '851542', '医药流通'],
        ['3', '851543', '线下药店'],
        ['3', '851532', '医疗设备'],
        ['3', '851533', '医疗耗材'],
        ['3', '851534', '体外诊断'],
        ['3', '851563', '医疗研发外包'],
        ['3', '851564', '医院'],
        ['3', '851611', '火力发电'],
        ['3', '851612', '水力发电'],
        ['3', '851614', '热力服务'],
        ['3', '851616', '光伏发电'],
        ['3', '851617', '风力发电'],
        ['3', '851610', '电能综合服务'],
        ['3', '851631', '燃气Ⅲ'],
        ['3', '851782', '原材料供应链服务'],
        ['3', '851783', '中间产品及消费品供应链服务'],
        ['3', '851784', '快递'],
        ['3', '851785', '跨境物流'],
        ['3', '851786', '仓储物流'],
        ['3', '851787', '公路货运'],
        ['3', '851731', '高速公路'],
        ['3', '851721', '公交'],
        ['3', '851771', '铁路运输'],
        ['3', '851741', '航空运输'],
        ['3', '851761', '航运'],
        ['3', '851711', '港口'],
        ['3', '851811', '住宅开发'],
        ['3', '851812', '商业地产'],
        ['3', '851813', '产业地产'],
        ['3', '851831', '物业管理'],
        ['3', '852021', '贸易Ⅲ'],
        ['3', '852031', '百货'],
        ['3', '852032', '超市'],
        ['3', '852033', '多业态零售'],
        ['3', '852034', '商业物业经营'],
        ['3', '852041', '专业连锁Ⅲ'],
        ['3', '852062', '跨境电商'],
        ['3', '852063', '电商服务'],
        ['3', '852182', '检测服务'],
        ['3', '852183', '会展服务'],
        ['3', '852121', '酒店'],
        ['3', '852111', '人工景区'],
        ['3', '852112', '自然景区'],
        ['3', '852131', '旅游综合'],
        ['3', '859852', '培训教育'],
        ['3', '857821', '国有大型银行Ⅲ'],
        ['3', '857831', '股份制银行Ⅲ'],
        ['3', '857841', '城商行Ⅲ'],
        ['3', '857851', '农商行Ⅲ'],
        ['3', '851931', '证券Ⅲ'],
        ['3', '851941', '保险Ⅲ'],
        ['3', '851922', '金融控股'],
        ['3', '851927', '资产管理'],
        ['3', '852311', '综合Ⅲ'],
        ['3', '857111', '水泥制造'],
        ['3', '857112', '水泥制品'],
        ['3', '857121', '玻璃制造'],
        ['3', '857122', '玻纤制造'],
        ['3', '850615', '耐火材料'],
        ['3', '850616', '管材'],
        ['3', '850614', '其他建材'],
        ['3', '850623', '房屋建设Ⅲ'],
        ['3', '857221', '装修装饰Ⅲ'],
        ['3', '857236', '基建市政工程'],
        ['3', '857251', '园林工程'],
        ['3', '857241', '钢结构'],
        ['3', '857242', '化学工程'],
        ['3', '857243', '国际工程'],
        ['3', '857244', '其他专业工程'],
        ['3', '857261', '工程咨询服务Ⅲ'],
        ['3', '850741', '电机Ⅲ'],
        ['3', '857334', '火电设备'],
        ['3', '857336', '其他电源设备Ⅲ'],
        ['3', '857352', '光伏电池组件'],
        ['3', '857354', '光伏辅材'],
        ['3', '857355', '光伏加工设备'],
        ['3', '857362', '风电零部件'],
        ['3', '857371', '锂电池'],
        ['3', '857372', '电池化学品'],
        ['3', '857373', '锂电专用设备'],
        ['3', '857375', '蓄电池及其他电池'],
        ['3', '857381', '输变电设备'],
        ['3', '857382', '配电设备'],
        ['3', '857321', '电网自动化设备'],
        ['3', '857323', '电工仪器仪表'],
        ['3', '857344', '线缆部件及其他'],
        ['3', '850711', '机床工具'],
        ['3', '850713', '磨具磨料'],
        ['3', '850715', '制冷空调设备'],
        ['3', '850716', '其他通用设备'],
        ['3', '850731', '仪器仪表'],
        ['3', '850751', '金属制品'],
        ['3', '850725', '能源及重型设备'],
        ['3', '850728', '楼宇设备'],
        ['3', '850721', '纺织服装设备'],
        ['3', '850726', '印刷包装机械'],
        ['3', '850727', '其他专用设备'],
        ['3', '850936', '轨交设备Ⅲ'],
        ['3', '850771', '工程机械整机'],
        ['3', '850772', '工程机械器件'],
        ['3', '850781', '机器人'],
        ['3', '850782', '工控设备'],
        ['3', '850783', '激光设备'],
        ['3', '850784', '其他自动化设备'],
        ['3', '857411', '航天装备Ⅲ'],
        ['3', '857421', '航空装备Ⅲ'],
        ['3', '857431', '地面兵装Ⅲ'],
        ['3', '850935', '航海装备Ⅲ'],
        ['3', '857451', '军工电子Ⅲ'],
        ['3', '850702', '安防设备'],
        ['3', '850703', '其他计算机设备'],
        ['3', '852226', 'IT服务Ⅲ'],
        ['3', '851041', '垂直应用软件'],
        ['3', '851042', '横向通用软件'],
        ['3', '857641', '游戏Ⅲ'],
        ['3', '857651', '营销代理'],
        ['3', '857661', '影视动漫制作'],
        ['3', '857674', '门户网站'],
        ['3', '857691', '教育出版'],
        ['3', '857692', '大众出版'],
        ['3', '859951', '电视广播Ⅲ'],
        ['3', '852213', '通信工程及服务'],
        ['3', '852214', '通信应用增值服务'],
        ['3', '851024', '通信网络设备及器件'],
        ['3', '851025', '通信线缆及配套'],
        ['3', '851026', '通信终端及配件'],
        ['3', '851027', '其他通信设备'],
        ['3', '859511', '动力煤'],
        ['3', '859512', '焦煤'],
        ['3', '859521', '焦炭Ⅲ'],
        ['3', '859621', '油田服务'],
        ['3', '859622', '油气及炼化工程'],
        ['3', '859631', '炼油化工'],
        ['3', '859632', '油品石化贸易'],
        ['3', '859633', '其他石化'],
        ['3', '859711', '大气治理'],
        ['3', '859712', '水务及水治理'],
        ['3', '859713', '固废治理'],
        ['3', '859714', '综合环境治理'],
        ['3', '859721', '环保设备Ⅲ'],
        ['3', '859811', '生活用纸'],
        ['3', '859821', '化妆品制造及其他'],
        ['3', '859822', '品牌化妆品'], 
        
        #金创指数C：目前在ak.index_hist_sw和ak.index_hist_fund_sw出错
        ['C', '802610', '华夏理财数字基础设施指数'],
        ['C', '802611', '华夏理财水力发电指数'],
        ['C', '802612', '华夏理财先进农业指数'],
        
        #申万基金指数: 基础一级J1
        ['J1', '807100', '申万宏源权益基金指数'],#权益基金=股票基金，股票>=80%
        ['J1', '807200', '申万宏源债券基金指数'],#债券>=80%
        ['J1', '807300', '申万宏源混合基金指数'],#跨越多品种证券的基金，以股债混合为主，可灵活调整
        ['J1', '807400', '申万宏源货币基金指数'],

        ['J1', '807500', '申万宏源另类基金指数'],
        
        ['J1', '807600', '申万宏源组合基金指数'],#基金的基金FOF
        ['J1', '807700', '申万宏源QDII基金指数'],#国内资金投资境外证券市场
        
        #申万基金指数: 基础二级J2
        ['J2', '807110', '申万宏源主动权益基金指数'],#针对主动管理型ETF基金 
        ['J2', '807120', '申万宏源标准指数基金指数'],#针对被动跟踪型ETF基金
        ['J2', '807130', '申万宏源增强指数基金指数'],#针对指数增强型ETF基金
        ['J2', '807140', '申万宏源行业主题基金指数'],#针对行业指数ETF基金 
        
        ['J2', '807210', '申万宏源纯债指数基金指数'],#直接针对债券，不含其他种类的证券
        ['J2', '807220', '申万宏源短期纯债基金指数'],
        ['J2', '807230', '申万宏源中长期纯债基金指数'],
        ['J2', '807240', '申万宏源债券增强基金指数'],#针对债券增强型基金
        
        ['J2', '807310', '申万宏源可转债基金指数'],
        ['J2', '807320', '申万宏源混合平衡基金指数Ⅱ'],#针对混合型和平衡型基金
        ['J2', '807330', '申万宏源混合偏债基金指数'],
        
        ['J2', '807510', '申万宏源商品基金指数'],
        ['J2', '807520', '申万宏源股票多空基金指数Ⅱ'],
        ['J2', '807530', '申万宏源REITs基金指数'],
        
        ['J2', '807610', '申万宏源权益FOF基金指数'],#针对投资于股票型基金的基金
        ['J2', '807620', '申万宏源混合平衡FOF基金指数Ⅱ'],#针对混合型和平衡型FOF基金
        ['J2', '807630', '申万宏源混合偏债FOF基金指数'],
        ['J2', '807640', '申万宏源债券FOF基金指数'],
        
        ['J2', '807710', '申万宏源QDII权益基金指数'],
        ['J2', '807720', '申万宏源QDII债券基金指数'],
        
        #申万基金指数: 基础三级J3
        ['J3', '807111', '申万宏源主动权益中高仓位基金指数'],#针对中高仓位的主动股票型ETF基金
        ['J3', '807112', '申万宏源主动权益高仓位基金指数'],
        ['J3', '807113', '申万宏源主动权益灵活仓位基金指数'],
        
        ['J3', '807121', '申万宏源沪深300标准指数基金指数'],#这里的"标准"一般指被动管理型基金
        ['J3', '807122', '申万宏源中证500标准指数基金指数'],
        ['J3', '807123', '申万宏源中证1000标准指数基金指数'],
        
        ['J3', '807131', '申万宏源沪深300增强指数基金指数'],#这里的"增强"一般指主动管理型基金
        ['J3', '807132', '申万宏源中证500增强指数基金指数'],
        ['J3', '807133', '申万宏源中证1000增强指数基金指数'],
        
        ['J3', '807141', '申万宏源消费基金指数'],
        ['J3', '807142', '申万宏源医药医疗基金指数'],
        ['J3', '807143', '申万宏源周期基金指数'],
        # 周期性行业（Cyclical Industry）与经济波动相关性较强的行业
        # 典型的周期性行业包括大宗原材料（如钢铁，煤炭等），工程机械，船舶等
        # 周期性行业的特征就是产品价格呈周期性波动的，产品的市场价格是企业赢利的基础
        # 该行业中产品价格形成的基础是供求关系，而不是成本，成本只是产品最低价的稳定器，但不是决定的基础
        ['J3', '807144', '申万宏源金融地产基金指数'],
        ['J3', '807145', '申万宏源先进制造基金指数'],
        ['J3', '807146', '申万宏源科技TMT基金指数'],
        ['J3', '807147', '申万宏源北交所基金指数'],
        ['J3', '807148', '申万宏源港股通基金指数'],
        
        ['J3', '807211', '申万宏源利率债指数基金指数'],
        ['J3', '807212', '申万宏源信用债指数基金指数'],#针对信用债指数基金       
        ['J3', '807213', '申万宏源同业存单指数基金指数'],
        
        ['J3', '807221', '申万宏源1年以内短期纯债基金指数'],
        ['J3', '807222', '申万宏源其他短期纯债基金指数'],
        
        ['J3', '807231', '申万宏源利率债基金指数'],
        # 利率债，一般由中央政府、各地方政府、政策性金融机构和央行等机构发行
        # 有政府信用作隐形背书，信用风险极低，主要承担的风险为市场利率波动的风险
        ['J3', '807232', '申万宏源利率金融债基金指数'],#针对利率债和金融债基金
        ['J3', '807233', '申万宏源信用债基金指数'],#针对信用债基金（非指数基金）
        # 信用债其发行主体包括上市公司、城投平台、商业银行等其他企业
        # 信用债需要同时承担利率风险和信用风险
        # 由于承担更高的风险，信用债需要存在一定的“风险补偿”
        # 对于相同期限的债券来说，信用债的收益水平整体要高于利率债
        ['J3', '807234', '申万宏源混合纯债基金指数'],#针对混合基金和纯债基金
        
        ['J3', '807241', '申万宏源债券增强中低仓位基金指数'],#针对主动管理型的中低仓位(<=50%仓位)的债券基金
        ['J3', '807242', '申万宏源债券增强低仓位基金指数'],
        
        ['J3', '807311', '申万宏源主动可转债基金指数'],
        ['J3', '807321', '申万宏源混合平衡基金指数Ⅲ'],
        ['J3', '807331', '申万宏源混合偏债高仓位基金指数'],
        ['J3', '807332', '申万宏源混合偏债中仓位基金指数'],
        ['J3', '807333', '申万宏源混合偏债低仓位基金指数'],
        
        ['J3', '807511', '申万宏源黄金基金指数'],
        ['J3', '807521', '申万宏源股票多空基金指数Ⅲ'],
        
        ['J3', '807611', '申万宏源权益高仓位FOF基金指数'],
        ['J3', '807612', '申万宏源权益中高仓位FOF基金指数'],
        ['J3', '807621', '申万宏源混合平衡FOF基金指数Ⅲ'],
        ['J3', '807631', '申万宏源混合偏债高仓位FOF基金指数'],
        ['J3', '807632', '申万宏源混合偏债中仓位FOF基金指数'],
        ['J3', '807633', '申万宏源混合偏债低仓位FOF基金指数'],
        ['J3', '807641', '申万宏源债券增强FOF基金指数'],
        
        #基金指数：特色指数，超额情况
        ['JF', '808001', '申万宏源公募沪深300增强基金超额指数'],
        ['JF', '808002', '申万宏源公募中证500增强基金超额指数'],
        ['JF', '808003', '申万宏源公募中证1000增强基金超额指数'],
        
        
        ], columns=['type','code','name'])
    
    
    """
    另类投资基金是指投资于传统公开市场交易的权益资产、固定收益类资产和货币类资产之外投资类型的基金，
    包括房地产、商铺、矿业、能源、证券化资产、对冲基金、大宗商品、私募股权、基础设施、黄金、艺术品等领域。
    另类投资产品与传统证券投资产品具有较低的相关性，甚至呈现出负相关性；
    在证券投资组合中加入另类投资产品，可以达到获取多元化收益和分散风险的效果。
    通过投资组合的多元化，能够给投资者带来更稳定、规模更大的投资回报。
    """
    
    """
    指数增强型基金，是一种介于被动型指数基金和主动型股票基金之间的投资策略。
    它的目标是在跟踪某个市场指数（如沪深300、中证500指数）的基础上，通过运用一定的主动投资策略，
    力求实现超过该指数的投资收益。
    指数增强型基金的投资组合通常以某个市场指数为基准，投资经理会在基准指数的成分股中进行一定程度的调整，
    以期在保持与基准指数相近的风险水平的同时，实现超过基准指数的收益。
    这种调整可能包括增加或减少某些成分股的权重，投资于非指数成分股等。
    指数增强型基金的目标是在跟踪基准指数的同时实现超额收益。这种策略往往对风险控制有更强的关注，
    其投资组合会更接近基准指数；此外，指增产品通常持股数量较多，分散了个股的非系统性风险。
    因此，通常相对于主观型基金风险较低，但相对于传统的指数基金，风险略高，
    但是因为采用了增强策略，其表现相对稳定。
    """
    
    """
    增强债券基金将资金大部分投资到债券市场，小部分投资到一级（个别有二级）股票市场。
    这种投资是为了增加债券基金操作的灵活性，增强债券基金的收益率。
    一般增强债券基金多参与一级市场新股申购，待新股上市后直接卖出，以获取较高收益。
    
    增强型基金一般是主动管理型。
    """
    
    """
    混合型基金：混合型基金的投资目标是实现多种投资方式的组合，以便获得股票市场和债券市场的双重收益。
    平衡型基金：平衡型基金则更侧重于在当期收益与长期资本增值之间找到平衡点。
    
    混合型基金：一般来说，混合型基金没有固定的股债配置比例，可以根据需要随时调整，以适应市场的变化。
    平衡型基金：通常，这类基金会事先确定一个相对稳定的股债配置比例，
    如40%-60%的股票和60%-40%的债券，以保持投资组合的相对稳定。
    
    混合型基金：一般来说，混合型基金的风险和收益水平介于股票型基金和债券型基金之间。
    平衡型基金：这类基金的风险和收益状况通常介于成长型基金和收入型基金之间，既不过于激进也不过于保守。
    
    混合型基金：混合型基金适合风险承受能力较强、追求较高收益的投资者。
    这类投资者愿意承担一定的市场风险以换取较高的潜在回报。
    
    平衡型基金：平衡型基金则更适合风险承受能力适中、追求稳健回报的投资者。
    这类投资者既希望获得一定的资本增值，又注重当前的稳定收益。
    """
    
    """
    偏债型基金：以债券投资为主要方向的基金产品。
    这类基金在资产配置上，债券的比例通常高于股票等其他投资品种，呈现出“债券为主，股票为辅”的投资特征。
    偏债型基金的债券投资配置比例的中值显著大于股票资产的配置比例中值，一般两者之间的差距大于10%，
    有的甚至达到更高的比例差异（如债券占比50%-70%，股票占比20%-40%），但未达到80%。
    这种投资策略使得偏债型基金在追求稳定收益的同时，也兼顾了一定的资本增值潜力。
    偏债混合型基金的波动和预期收益一般高于纯债基金和一、二级债基，同时低于股票型和偏股型混合基金。
    因此，偏债混合型基金比较适合追求高收益，能承受一定波动的投资者。
    偏债混合型基金相比于纯债基金，能够带来较高的收益，在市场行情震荡的时候，也能带到不错的投资效果。
    
    二级债基和一级债基的区别：
    一级债基是除固定预期收益类金融工具以外，参与一级市场新股投资；
    二级债基是除固定预期收益类金融工具以外，适当参与二级市场股票买卖，也参与一级市场新股投资。
    
    由于一级债基投资于纯债和新股，而二级债基，除了这些还可以投资二级精股，
    也就是说，二级债基的投资范围要比一级债基的投资范围大一些。
    
    一级债基是高预期收益债组合打新股；二级债基是高预期收益债组合打新股精选添预期收益；
    也就是说，一级债基是纯债和新股的组合；而二级债基是纯债、新股和精选个股的组合，资产配置不同。
    
    由于投资标的和产品组成特点的不同，二级债基的风险加大了；
    一般来说，一级债基是中低风险，而二级债基是中等风险。
    """
    
    """
    股票多空基金：通过判断股票市场的走势，选择做多或做空的方式，从而获取市场盈利。
    这类基金具有较大灵活性，不论是市场上涨还是下跌，都能通过做空或做多机制获取收益。
    当基金经理认为市场将上涨时，会采取做多策略，购买股票；
    而当认为市场将下跌时，则会采取做空策略，如卖空股指期货或通过融券卖空股票等。
    
    与传统的只买股票的基金不同，这种基金能够在市场下跌时依然获利。
    在股市波动较大的情况下，股票多空基金能够更好地把握市场机会，降低风险。
    此外，由于基金管理人会主动判断市场走势并据此调整投资策略，因此能够主动管理风险。
    
    如果市场环境好，基金的投资策略和选股能力优秀，则基金的收益会较为可观。
    然而，由于股票市场的波动性较大，股票多空基金也存在一定的风险。
    投资者需要承担市场风险、流动性风险以及管理人的操作风险等。
    
    股票多空策略：在持有股票多头的同时采用股票空头进行风险对冲的投资策略，
    也就是说在其资产配中既有多头仓位，又有空头仓位。空头仓位主要是融券卖空股票。
    
    灵活对冲（又称择时对冲）：同样是持有股票多头的同时采用股票空头进行风险对冲的投资策略，
    空头仓位主要是卖空股指期货或者股票期权（股指CTA）。
    
    多头仓位和空头仓位之差即为净敞口。比如80%的多头仓位、50%的空头仓位，则净敞口是30%。
    通过净敞口的调节可以控制风险暴露，净敞口越低，风险暴露越低。
    
    股票多空策略通常控制风险敞口接近0，而灵活对冲用股指期货CTA灵活调节净敞口，与股票多空策略不完全类似。
    
    股指CTA（Commodity Trading Advisor）是一种专门从事基于股指期货的交易策略的投资顾问。
    CTA通常指的是那些管理客户资金并使用期货市场作为主要投资领域的专业投资经理。
    股指CTA则特指那些专注于股指期货的投资顾问，他们通过预测市场趋势，从而进行买卖决策。
    
    股指CTA的交易策略通常包括趋势跟踪、套利交易、市场中性策略等。
    趋势跟踪策略是股指CTA最常用的方法之一，它涉及识别和跟随市场的长期趋势。
    套利交易则涉及利用不同市场或不同时间点的价格差异来获取无风险或低风险利润。
    市场中性策略旨在通过同时进行多头和空头交易来减少市场波动的影响。
    
    股指CTA的优势在于其能够提供多样化的投资选择和风险管理工具。
    由于股指期货具有高杠杆特性，投资者可以用较少的资金控制较大的市场头寸，从而放大潜在的收益。
    同时，股指期货市场的高流动性和24小时交易特性也为CTA提供了更多的交易机会。
    
    然而，股指CTA也面临一定的风险。市场的不确定性和波动性可能导致交易损失，特别是当市场趋势与预期相反时。
    此外，高杠杆操作虽然可以放大收益，但同时也增加了潜在的损失风险。
    """
    
    """
    基金仓位是指基金投入股市或债市的资金占基金所能运用的资产的比例。
    权益中高仓位：一般指投入股票市场的仓位达到或超过50%。
    一般而言，中高仓位能增强基金的盈利能力，但也可能加大基金的风险，并降低基金应对赎回的现金准备水平。
    
    投入资金有两种算法：股票成本，股票市值。
    基金所能运用的资产也有两种算法：基金的净资产，基金能够动用的现金。
    
    通用的仓位是基金每季公布的股票市值与净值之比，特点是简单易懂，实用性较强。基金公布的季度持仓多采用此方法。
    但这种算法有一个问题:股票市值及净值中含估值增值部分,
    即股价增长数额, 并不代表基金在股价增长之前投入的实际资金。
    估值增值部分的计入，虚增了基金投入股市的资金,也加大了投资前的资金量。
    
    股票成本与扣除估值增值后的净值之比，相对复杂不易懂。
    这个算法中，股票以成本计，净值也扣除了估值增值部分。
    这个算法等于股票成本与股票成本及可用流动资金之比所计算出的仓位，
    其含义为:基金短期内可动用的资金也包括在内(银行存款加各项应收款与应付款之差)，
    反映的是基金可支配的总体资金状况，较为准确全面，季度公布的持仓较少采用，需要参见基金的中报年报。
    """
    
    """
    同业存单是商业银行、政策性银行等存款类金融机构在全国银行间市场发行的可转让记账式定期存款凭证。
    而同业存单就是商业银行、政策性银行等存款类金融机构向其他金融机构借款的凭证，
    由于银行的资金量相对较大，利率一般会高于个人存款利率，而且同业存单可以在银行间市场中流通和转让。
    
    同业存单指数基金，就是跟踪中证同业存单AAA指数（由银行间市场主体评级为AAA，
    发行期限1年以下、上市时间7天以上的同业存单组成）的指数债券基金。
    
    同业存单指数基金的特点：
    低信用风险：存单指数基金主要投资于主体评级为AAA级的同业存单，
    均为全国性商业银行等大型机构，面临的信用风险（发行主体违约风险）相对较低。
    低利率风险：指数化投资对跟踪误差有严格的要求，主动管理成分较少，
    因此采用短久期运作，久期基本和跟踪指数标的相似，面临的利率风险也较低。
    持有费率较低：同业存单指数基金不收取申购赎回费（需持有满7个自然日），
    管理费一般为0.20%，托管费一般为0.05%，销售服务费一般为0.20%，总费率为0.45%，
    相比货币基金A类（小额投资份额）费用更低（A类费率一般为0.6%左右）。
    
    同业存单指数基金和货币基金、短债基金的区别：
    存单指数基金和货币基金其实都可以大比例投资同业存单，但在久期、杠杆和估值方面有所差异。
    货币基金平均久期上限为120天，杠杆为120%，并且采用成本法估值；
    存单指数基金理论上久期可以为1年，实际上久期和存单指数近似为0.45（大约为164天），
    杠杆比例上限为140%，采用市价法估值，存在回撤风险。
    
    短债基金并不采用指数化投资，其投资范围更广，同业存单、短融、企业债、利率债均可以进行投资，
    并且在出现利率机会时，还可以通过提高20%仓位的久期获取超额收益。
    因此从收益风险比来看，存单指数基金相比短债基金久期和等级限制更为严格，其风险收益水平低于短债基金。
    
    总的来说，同业存单指数基金通过指数化投资，争取在扣除各项费用之前获得与标的指数相似的总回报，
    追求跟踪偏离度及跟踪误差的最小化，波动性相对较低，流动性较好。
    """
    
    """
    增强基金超额指数:
    这里的超额：指数增强基金采用了主动管理，其收益率与目标指数的收益率产生了差异。
    原意=指数增强基金的实际收益率 - 指数增强基金的预期收益率
    指数增强基金的预期收益率=RF+指数增强基金的贝塔*(目标指数收益率-RF)
    实际计算指数增强基金收益率相对于目标指数收益率的阿尔法值。
    简化算法：
    指数增强基金的实际收益率=Alpha+指数增强基金的贝塔 *目标指数收益率
    其中，贝塔产生的收益率来源于对目标指数的跟踪，Alpha产生的收益率来源于主动管理。
    """


    return industry

#==============================================================================
if __name__ == '__main__':
    icode='859811.SW'
    
    industry_sw_name(icode)

def industry_sw_name(icode):
    """
    功能：将申万指数代码转换为指数名称。
    输入：指数代码
    输出：指数名称
    """
    icode=icode.split('.')[0]
    
    industry=industry_sw_list()

    try:
        iname=industry[industry['code']==icode]['name'].values[0]
    except:
        #未查到
        if not icode.isdigit():
            print("  #Warning(industry_sw_name): industry name not found for",icode)
        iname=icode
   
    return iname

if __name__=='__main__':
    icode='801735'
    industry_sw_name(icode)

#==============================================================================
#实现简单中英文短语互译
#==============================================================================
if __name__ == '__main__':
    chntext='市盈率'
    engtext="PE ratio"
    engtext="P/E ratio"
    
    zh2en(chntext)
    
    en2zh(engtext)
    

def zh2en(text):
    '''英文转换成中文'''
    
    from translate import Translator
    translator = Translator(from_lang="zh", to_lang="en")
    translation = translator.translate(text)

    return translation

def en2zh(text):
    '''中文转换成英文'''
    
    from translate import Translator
    translator = Translator(from_lang="en", to_lang="zh")
    translation = translator.translate(text)
    
    return translation

if __name__ == '__main__':
    chntext='市盈率'
    engtext1="PE ratio"
    engtext2="P/E ratio"

    lang_auto(chntext)
    lang_auto(engtext1)
    lang_auto(engtext2)
    
    lang_auto(text)


def lang_auto(text):
    '''转换字符串text至当前语言环境，基于translate'''
    
    #注意：这个翻译模块只能每天提供有限单词翻译服务
    from translate import Translator
    
    lang_env=check_language()
    lang_text=detect_language(text)
    
    #字符串语言与当前环境语言相同，无需翻译，节省运行时间
    if lang_env==lang_text:
        return text
    
    provider_list=['mymemory']
    
    if lang_env=='Chinese':
        #translator = Translator(from_lang="en", to_lang="zh")
        #translator = Translator(to_lang="zh")
        translator = Translator(to_lang="zh",provider="mymemory")
    elif lang_env=='English':
        translator = Translator(to_lang="en")
    else:
        return text
    
    translation = translator.translate(text)
    
    return translation

if __name__ == '__main__':
    text='市盈率'
    text='贵州茅台'
    text='五粮液'
    text='Dividend Payout Ratio'
    text='asOfDate'
    text='Cash And Cash Equivalents'
    text='AccountsReceivableNetSalesAllowance'
    text='Accounts Receivable Net of Sales Allowance'
    text='Accounts Payable'
    
    text='经济形势分析：China, in Trillions'
    
    language_detect=True
    language_engine=['google','baidu','bing']
    
    chntext='市盈率'
    engtext1="PE ratio"
    engtext2="P/E ratio"

    lang_auto2(text)
    lang_auto2(text,language_detect=True)
    
    lang_auto2(chntext)
    lang_auto2(engtext1)
    lang_auto2(engtext2)


def auto_translate(text,translate=False,language_engine=['bing','sogou','alibaba','google']):
    """
    ===========================================================================
    功能：基于translate决定是否翻译text
    
    注意：可以通过调整language_engine更换翻译引擎，不同的翻译引擎更有特色
    谷歌的翻译引擎总体质量较好，但对财经术语的翻译较差
    阿里巴巴的翻译引擎对长句翻译不错，但翻译结果不稳定，对同一术语的翻译不稳定
    搜狗的翻译引擎处理中英文混合时容易出错
    """
    new_text=text
    if translate:
        new_text=lang_auto2(text,language_engine=language_engine)
    return new_text

def lang_auto2(text,language_detect=True,language_engine=['bing','alibaba','google','sogou']):
    '''转换字符串text至当前语言环境，基于translators，可指定翻译服务器，准确度更高'''
    
    import translators as ts
    """
    lang_env=check_language()
    
    if language_detect:
        lang_text=detect_language(text)
        
        #字符串语言与当前环境语言相同，无需翻译，节省运行时间
        if lang_env==lang_text:
            return text
    """
    # 检查翻译方向
    lang_env=check_language()
    if lang_env in ['English']:
        target_lang="en"
        source_lang="zh"
    else:
        target_lang="zh"
        source_lang="en"

    if isinstance(language_engine,str):
        language_engine=[language_engine]
    
    success=False
    for le in language_engine:
        try:
            translation = ts.translate_text(text, \
                                            from_language=source_lang,to_language=target_lang, \
                                            translator=le)
            
            # 去掉中文中的所有空格
            if target_lang=="zh":
                translation = translation.replace(' ','')
                
            success=True
            break
        except:
            continue
    
    """
    if lang_env=='Chinese':
        #translator支持baidu/bing/google
            
        for le in language_engine:
            try:
                translation = ts.translate_text(text,from_language='en',to_language='zh', translator=le)
                
                # 应对搜狗引擎中英文混合时可能的翻译错乱
                if le in ['sogou']:
                    lang_text=detect_language(translation)
                    if lang_text != lang_env:
                        text=translation
                        translation = ts.translate_text(text,from_language='en',to_language='zh', translator=le)
                # 去掉中文中的所有空格
                translation = translation.replace(' ','')
                success=True
                break
            except:
                continue
    elif lang_env=='English':
        for le in language_engine:
            try:
                translation = ts.translate_text(text,from_language='zh',to_language='en', translator=le)
                success=True
                break
            except:
                continue
    else:
        return text
    """
    
    if not success:
        translation = text
        
    return translation


if __name__ == '__main__':
    chntext='市盈率'
    engtext1="PE ratio"

    detect_language(chntext)
    detect_language(engtext)
 
def detect_language(text):
    '''判断字符串text是中文还是英文'''
    
    import re
    chinese_pattern = re.compile(r'[\u4e00-\u9fa5]')
    english_pattern = re.compile(r'[a-zA-Z]')
    
    chinese_count = len(chinese_pattern.findall(text))
    english_count = len(english_pattern.findall(text))
    total_count = chinese_count + english_count
    
    if total_count == 0:
        result='Unknown'
    
    """    
    if chinese_count > english_count:
        result='Chinese'
    elif english_count > chinese_count:
        result='English'
    else:
        result='Both'    
    """
    if chinese_count==0 and english_count>0:
        result='English'
    if chinese_count>0 and english_count==0:
        result='Chinese'
    if chinese_count>0 and english_count>0:
        result='Both'
        
    
    return result


if __name__ == '__main__':
    text='DividendPayoutRatio'
    text='CashAndCashEquivalents'
    text='asOfDate'
    
    text='GrossPPE'
    
    text='Cash And Cash Equivalents'

    words_split_yahoo(text)
 
def words_split_yahoo(text,split_improve=True):
    '''将雅虎英文财报术语拆分为带空格的词组'''

    
    #替换基于大写字母无法分词的短语
    text=text.replace("periodType","PeriodType")
    text=text.replace("Tradeand","TradeAnd")
    
    words_list=[]
    start=0
    
    for i in range(len(text)):
        c=text[i]
        
        if (c>='A' and c<='Z') or c==' ':
            words_list=words_list+[text[start:i].strip(' ')]
            start=i
    
    #添加最后一个单词
    words_list=words_list+[text[start:i+1]]
    
    special_words=['and','of','in','at','as','for','non','from']
    words_list2=[]
    for w in words_list:
        if text.index(w) == 0:
            words_list2=words_list2+[w.title()]
        elif w.lower() in special_words:
            words_list2=words_list2+[w.lower()]
        else:
            words_list2=words_list2+[w]
    
    text_new=''
    for w in words_list2:
        text_new=text_new+' '+w
    
    #若出现多个空格则替换为单个空格
    import re
    text_new=re.sub(r' +', ' ', text_new)
    
    #去掉首尾的空格
    text_new=text_new.strip(' ')
    
        
    #判断大写字母缩写合并
    prev_c1=''; prev_c2=''
    text_new2=''
    for c in text_new:
        if c>='A' and c<='Z':
            if prev_c1==' ' and (prev_c2>='A' and prev_c2<='Z'):
                text_new2=text_new2.strip(' ')+c
            else:
                text_new2=text_new2+c
        else:
            text_new2=text_new2+c
            
        prev_c2=prev_c1; prev_c1=c
    
    #弥补大写字母合并后继词的逻辑缺陷
    for upl in ['PPE']:
        text_new2=text_new2.replace(upl,upl+' ')
        text_new2=re.sub(r' +', ' ', text_new2)
        text_new2=text_new2.strip(' ')
    
    
    #替换缩写/简写/容易翻译出错的词，强行规避翻译错误。
    #注意：不影响未拆分科目名称，仅为翻译用途
    if split_improve:
        text_new3=text_new2.replace("PPE","Plant Property and Equipment")
        
        text_new3=text_new3.replace("Treasury Shares Number","Treasury Shares")
        text_new3=text_new3.replace("Ordinary Shares Number","Ordinary Shares")
        text_new3=text_new3.replace(" Gross "," and ")
        text_new3=text_new3.replace("non Current","Non-current")
        text_new3=text_new3.replace("Non Current","Non-current")
        text_new3=text_new3.replace("Short Term","Short-term")
        text_new3=text_new3.replace("Long Term","Long-term")
        text_new3=text_new3.replace("Available for Sale","Available-for-sale")
    
        text_new3=text_new3.replace(" Com "," Common ")
        text_new3=text_new3.replace(" Net "," Net of ")
        text_new3=text_new3.replace("Net Income","Net Profit")
        
        text_new3=text_new3.replace("EBITDA","XXX")
        text_new3=text_new3.replace("EBIT","Earnings before Interest and Tax")
        text_new3=text_new3.replace("XXX","EBITDA")
        
        text_new3=text_new3.replace("Tax Provision","Tax Accrued")
        text_new3=text_new3.replace("non Operating","Non-operating")
        
        text_new3=text_new3.replace("Operating Income","Operating Profit")
        text_new3=text_new3.replace("Pretax Income","Pretax Profit")
        
        text_new3=text_new3.replace("Current Provisions","Current Reserve")
        
        text_new3=text_new3.replace("Duefrom ","Due from ")
        text_new3=text_new3.replace("Dueto ","Due to ")
        
        text_new3=text_new3.replace("Investmentin ","Investment in ")
        text_new3=text_new3.replace("Diluted NIAvailto ","Diluted Net Profit Avail to ")
        text_new3=text_new3.replace(" Noncontrolling "," Non-controlling ")
        text_new3=text_new3.replace("Other Gand A","Other General and Administrative Expense")
        text_new3=text_new3.replace("Otherunder ","Other under ")
        text_new3=text_new3.replace("Mergern Acquisition","Merger and Acquisition")
        text_new3=text_new3.replace("Write Off","Write-off")
        
        text_new3=text_new3.replace("Cash Flow From ","Cash Flow from ")
        text_new3=text_new3.replace("Cash From ","Cash Flow from ")
        text_new3=text_new3.replace(" From "," from ")
        text_new3=text_new3.replace("Provisionand","Provision and")
        text_new3=text_new3.replace("Write-offof","Write-off of")
        text_new3=text_new3.replace("non Cash","non-Cash")
        text_new3=text_new3.replace("Changein","Change in")
        
    else:
        text_new3=text_new2
        
    return text_new3

#==============================================================================
if __name__ == '__main__':
    text="经济趋势分析：GDP PPP (constant international $)"
    
    source_lang="en"
    target_lang="zh"
    content_tip="宏观经济学与金融学"
    content_tip="美国上市公司财务报表"
    content_tip="香港上市公司财务报表"

def kimi_translate(text, source_lang="zh", target_lang="en", \
                   domain_tip="宏观经济学与金融学", \
                   terminology_tip="特别注意专业术语内涵翻译的专业性", \
                   special_tip="仅翻译文本，不翻译专业术语缩写词，不附带原文，不解释内容"):
    """
    ===========================================================================
    功能：使用 Kimi API 进行翻译。
    :param api_key: Kimi API 密钥
    :param text: 要翻译的文本
    :param source_lang: 源语言，默认为自动检测
    :param target_lang: 目标语言，默认为英文
    :return: 翻译结果
    """
    
    if target_lang=="en":
        target_lang="英文"
        source_lang="中文"
    else:
        target_lang="中文"
        source_lang="英文"
    
    import requests
    # 如果api_key失效，可重新申请，或付费购买
    api_key='sk-BMuqBuuYr6Hh6Ihi1SL2Vbfr7B3868QQSbTVExgalMpoYfA3'
    
    url = "https://api.moonshot.cn/v1/chat/completions"  # Kimi API 的 URL
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    payload = {
        "model": "moonshot-v1-8k",
        "messages": [
            {
                "role": "system",
                "content": f"将以下{domain_tip}文本从{source_lang}翻译为{target_lang}，{terminology_tip}，{special_tip}："
            },
            {
                "role": "user",
                "content": text
            }
        ]
    }

    response = requests.post(url, json=payload, headers=headers)
    if response.status_code == 200:
        result = response.json()
        return result["choices"][0]["message"]["content"]
    else:
        """
        import time; time.sleep(3)
        # 再试一次
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 200:
            result = response.json()
            return result["choices"][0]["message"]["content"]
        else:
            return f"Error: {response.status_code}"
        """
        return f"Error: {response.status_code}"
    
        
if __name__ == '__main__':
    text = "这是一段需要翻译的中文文本。"
    kimi_translate(text, source_lang="zh", target_lang="en")
    
    text = "经济趋势分析：Japan, in Trillions" 
    text = "GDP PPP (constant LCU)"
    text = "Broad money (% of GDP)"
    kimi_translate(text, source_lang="en", target_lang="zh",content_tip="宏观经济学与金融学")
    
    #翻译财报项目：将需要翻译的短语集合在一起，一次性调用翻译，可提高效率，之后再拆分使用
    #最好使用句号分割，避免AI联系上下文进行翻译
    text = "DilutedEPS.Debt Service Coverage.ROIC.periodType.BasicEPS.Equity Multiplier.Treasury Shares Number"
    text="Total Equity And Minority Interest.Total non Current Liabilities Net of Minority Interest"
    
    kimi_translate(text, source_lang="en", target_lang="zh",domain_tip="雅虎财经财务报表")

#==============================================================================
if __name__ == '__main__':
    # 英译中
    text_list=["GDP PPP (constant international $)","Broad money"]
    source_lang="en"; target_lang="zh"
    domain_tip="宏观经济学与金融学"
    terminology_tip="特别注意专业术语内涵翻译的专业性"
    special_tip="特别注意只翻译文本即可，不用附带原文，不用解释内容"
    
    translate_list(text_list,source_lang, target_lang)
    
    # 英译中
    text_list=["投资收益率","投资风险"]
    source_lang="zh"; target_lang="en"
    
    translate_list(text_list,source_lang, target_lang)
    
def translate_list(text_list=["GDP PPP","Broad money"],source_lang="auto", target_lang="en", \
                   domain_tip="宏观经济学与金融学", \
                   terminology_tip="特别注意专业术语内涵翻译的专业性", \
                   special_tip="特别注意只翻译文本即可，不用附带原文，不用解释内容"):
    """
    ===========================================================================
    功能：翻译列表中的内容，并按原顺序输出翻译后的列表
    主要参数：
    
    """
    # 检查列表是否为空
    if len(text_list)==0: return text_list
    
    # 将列表合成为长字符串，使用句点做分隔符
    text=''; first=True
    separator_en='.'; separator_zh='。'
    for t in text_list:
        if first:
            text=t
            first=False
        else:
            text=text+separator_en+t
            
    # 一次性翻译
    translated=kimi_translate(text, source_lang=source_lang, target_lang=target_lang, \
                       domain_tip=domain_tip, \
                       terminology_tip=terminology_tip, \
                       special_tip=special_tip)
    
    import re
    if target_lang=='zh':
        # 拆分：第1步
        text1=re.split(r'\n|。',translated)
        
        # 拆分：第2步
        text2=[]
        for t in text1:
            t1=t.split('：')
            t2=t1[0]
            """
            if len(t1)==1: t2=t1[0]
            else: t2=t1[1]
            """
            text2=text2+[t2]
            
    if target_lang=='en':
         # 拆分：第1步
        text1=translated.split('.')
         
        # 拆分：第2步
        text2=[]
        for t in text1:
            t1=t.split('：')
            t2=t1[0]
            """
            if len(t1)==1: t2=t1[0]
            else: t2=t1[1]
            """
            text2=text2+[t2]
           
            
    return text2

        
#==============================================================================
if __name__ == '__main__':
    text="经济趋势分析：GDP PPP (constant international $)"
    text="经济趋势分析：GDP PPP"
    text="经济趋势分析：Japan"
    
    auto_translate2(text,translate=True)
    
def auto_translate2(text,translate=False, \
                    domain_tip="经济学与金融学", \
                    terminology_tip="特别注意专业术语内涵翻译的专业性", \
                    special_tip="特别注意只翻译文本即可，不用附带原文，不用解释内容"):
    """
    ===========================================================================
    功能：基于translate决定是否翻译text
    
    注意：可以通过调整_tip改善翻译质量
    """
    if not translate: return text
    
    # 检查翻译方向
    lang_env=check_language()
    if lang_env in ['English']:
        target_lang="en"
        source_lang="zh"
    else:
        target_lang="zh"
        source_lang="en"
    
    new_text=text
    if translate:
        new_text=kimi_translate(text, source_lang=source_lang, target_lang=target_lang, \
                           domain_tip=domain_tip, \
                           terminology_tip=terminology_tip, \
                           special_tip=special_tip)
            
    if 'Error' in new_text or '429' in new_text:
        new_text=auto_translate(text,translate=True)
            
    return new_text

#==============================================================================
#==============================================================================
#==============================================================================
#==============================================================================
#==============================================================================
