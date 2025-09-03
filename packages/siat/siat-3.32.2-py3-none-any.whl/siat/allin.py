# -*- coding: utf-8 -*-
"""
功能：一次性引入SIAT的所有模块
作者：王德宏，北京外国语大学国际商学院
版权：2022(C) 仅限教学使用，商业使用需要授权
联络：wdehong2000@163.com
"""

# 资产流动性
from siat.assets_liquidity import *

# 贝塔系数调整方法
from siat.beta_adjustment import *
from siat.beta_adjustment_china import *

# 债券
from siat.bond import *

# 资本资产定价模型
from siat.capm_beta import *
from siat.capm_beta2 import *

# 数字货币
from siat.cryptocurrency import *

# 宏观经济
from siat.economy import *
from siat.economy2 import *


# ESG
from siat.esg import *

# 资产定价-多因子模型
from siat.fama_french import *

# 财务报表：雅虎源
from siat.financial_statements import *

# 财务分析：雅虎源
from siat.financials import *

# 财务分析：雅虎源
from siat.financials2 import *

# 财务报表：雅虎源
from siat.fin_stmt2_yahoo import *

# 财务分析：中国
from siat.financials_china import *

# 财务分析：中国，资产负债结构分析
from siat.financials_china2 import *

# 中国的基金
from siat.fund_china import *

# 中国的期货（内盘与部分外盘）
from siat.future_china import *

# 中国的期权
from siat.option_china import *

# 资产的持有风险
from siat.holding_risk import *

# 投资组合理论
#from siat.markowitz import *
from siat.markowitz2 import *

# 投资组合理论自助式示意图
#from siat.markowitz_simple import *

# 期权定价
from siat.option_pricing import *

# 风险调整收益
from siat.risk_adjusted_return import *
from siat.risk_adjusted_return2 import *

# 风险评估
from siat.risk_evaluation import *

# 中国的行业分析
from siat.sector_china import *

# 股票/行业指数估值：美股，港股，A股，波兰股，指数
from siat.valuation import *

# 中国股票/市场估值
from siat.valuation_china import *

# 获取证券价格与计算
from siat.security_prices import *
from siat.security_price2 import *
from siat.other_indexes import *

# 股票分析
from siat.stock import *

# 股票趋势分析，集成函数
from siat.security_trend2 import *

# 中国的股票
from siat.stock_china import *

# 中国股票市场概况
from siat.market_china import *

# 证券交易-套壳
from siat.transaction import *

# 持有资产风险-模型验证
from siat.var_model_validation import *

# 跨种类比较分析
from siat.compare_cross import *

# 机器学习-课程案例
#from siat.ml_cases import *
#from siat.stock_advice_linear import *

# 股票技术分析
from siat.stock_technical import *

# 事件研究法
from siat.event_study import *

# 2FA: Google Authenticator
from siat.google_authenticator import *

# 提问记录
from siat.luchy_draw import *

# 搜索全球上市公司的英文名称，需要访问雅虎
from siat.yf_name import *

# Save to PDF：实验中
from siat.save2pdf import *

# Save to docx：实验中
from siat.save2docx import *

# pdf widgets：拆分，转换，实验中
from siat.pdf_process import *

# 量化投资策略与回测，实验中
from siat.quantitative import *


