# -*- coding: utf-8 -*-
"""
本模块功能：演示量化投资案例
所属工具包：证券投资分析工具SIAT 
SIAT：Security Investment Analysis Tool
创建日期：2025年8月27日
最新修订日期：2025年8月28日
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
from siat.translate import *
from siat.security_trend2 import *
from siat.grafix import *

#==============================================================================
import pandas as pd
import numpy as np
#==============================================================================

#==============================================================================

def add_slippage(price, slippage=0.001):
    """
    模拟滑点，返回加入滑点后的价格，通用。
    参数:
    - price: 当前价格
    - slippage: 滑点的幅度，默认为0.1%（即0.001）
    
    返回：
    - 加入滑点后的价格
    """
    seed = 42
    np.random.seed(seed)
    
    slippage_factor = 1 + slippage * np.random.randn()  # 使用正态分布模拟滑点
    return price * slippage_factor

#==============================================================================

def calculate_transaction_fee(price, position, fee_rate=0.0005):
    """
    计算交易费用：含手续费、佣金、过户费和印花税，通用。
    参数:
    - price: 当前价格
    - position: 当前持仓量
    - fee_rate: 交易费率（默认为0.05%）
    
    返回：
    - 交易费用
    """
    return abs(position * price) * fee_rate  # 计算买入或卖出所需的交易费用

#==============================================================================
# 高低点策略
# 注意：本策略中的price_type可以使用Close、Adj Close或Open
#==============================================================================
if __name__=='__main__':
    ticker="600519.SS"
    
    # 样本期间
    fromdate="2010-1-1"
    todate="2025-6-30"
    
    prices,found=get_price_1ticker(ticker,fromdate,todate)
    
    signals=strategy_highlow(prices, window=252, price_type="Close")
    print(signals[signals != 0])
    signals.loc["2010-03-01":"2010-03-10"]
    signals.loc["2010-3-1":"2010-3-10"]

def strategy_highlow(prices, window=252, \
                     
                     strategy_name="", \
                     initial_balance=1000000, slippage=0.001, fee_rate=0.0005, \
                     min_shares=100, \
                     price_type="Close"):
    """
    专用策略名称：高低点策略，对于每个交易日产生三种信号：不操作0，买入1，卖出-1
    观察窗口期：window
    策略函数：当股价不高于最近窗口期最低点时买入，不低于最近窗口期最高点时卖出
    参数:
    - prices: 收盘价数据，pandas DataFrame
    - window: 计算窗口期的滑动窗口，默认为252个交易日（52周）
    - price_type: 可用收盘价Close、调整收盘价Adj Close或开盘价Open
    
    返回:
    - signals: 序列，买入卖出信号的Series，1为买入，-1为卖出，0为不操作
    """
    # 计算窗口期的最高价和最低价
    prices['window_high'] = prices[price_type].rolling(window=window).max()
    prices['window_low'] = prices[price_type].rolling(window=window).min()
    
    # 初始化信号列
    signals = np.zeros(len(prices))
    
    # 买入信号：收盘价低于最近窗口期最低价
    signals[prices[price_type] <= prices['window_low']] = 1  # 买入信号
    
    # 卖出信号：收盘价高于最近窗口期最高价
    signals[prices[price_type] >= prices['window_high']] = -1  # 卖出信号
    
    return pd.Series(signals, index=prices.index)

#==============================================================================
# 金叉死叉策略
# 注意：本策略中的price_type可以使用Close、Open和Adj Close，但需要对KDJ进行处理
#==============================================================================

# 计算MACD
def calculate_macd(prices, short_window=12, long_window=26, signal_window=9, \
                   price_type="Close"):
    short_ema = prices[price_type].ewm(span=short_window, adjust=False).mean()
    long_ema = prices[price_type].ewm(span=long_window, adjust=False).mean()
    macd = short_ema - long_ema
    signal = macd.ewm(span=signal_window, adjust=False).mean()
    histogram = macd - signal
    return macd, signal, histogram

# 计算RSI
def calculate_rsi(prices, window=14, price_type="Close"):
    delta = prices[price_type].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

# 计算KDJ：有分红时需要特别处理
def calculate_adj_high_low(prices):
    """
    核心逻辑是：
    同一时间点的复权比例对所有价格（开盘价、最高价、最低价、收盘价）是相同的，
    因此可以通过 Adj Close 与 Close 的比值得到复权系数，
    再应用到 High 和 Low 上
    """
    """
    计算前复权最高价(Adj High)和前复权最低价(Adj Low)
    
    参数:
        prices: pandas DataFrame，需包含以下列：
            - Close: 原始收盘价
            - Adj Close: 前复权收盘价
            - High: 原始最高价
            - Low: 原始最低价
    
    返回:
        新增 Adj High 和 Adj Low 列的 DataFrame
    """
    # 复制原始数据避免修改源数据
    df = prices.copy()
    
    # 计算复权系数：前复权收盘价 / 原始收盘价
    # 处理除数为0的情况（极少数极端情况）
    df['adj_factor'] = df['Adj Close'] / df['Close'].replace(0, pd.NA)
    
    # 计算前复权最高价和最低价
    df['Adj High'] = df['High'] * df['adj_factor']
    df['Adj Low'] = df['Low'] * df['adj_factor']
    
    # 移除临时计算的复权系数列（可选）
    df = df.drop(columns=['adj_factor'])
    
    return df 
   

def calculate_kdj(prices, window=14, price_type="Close"):
    
    # 不使用调整收盘价
    if not ("Adj" in price_type):
        low_min = prices['Low'].rolling(window=window).min()
        high_max = prices['High'].rolling(window=window).max()
        rsv = (prices[price_type] - low_min) / (high_max - low_min) * 100
        k = rsv.ewm(com=2, adjust=False).mean()
        d = k.ewm(com=2, adjust=False).mean()
        j = 3 * k - 2 * d
    
    # 使用调整收盘：考虑红利再投资
    else:
        prices=calculate_adj_high_low(prices)
        low_min = prices['Adj Low'].rolling(window=window).min()
        high_max = prices['Adj High'].rolling(window=window).max()
        rsv = (prices[price_type] - low_min) / (high_max - low_min) * 100
        k = rsv.ewm(com=2, adjust=False).mean()
        d = k.ewm(com=2, adjust=False).mean()
        j = 3 * k - 2 * d
        
            
    return k, d, j


def strategy_cross(prices, MACD=True, RSI=True, KDJ=True):
    # 金叉死叉策略
    # 计算指标：MACD、RSI、KDJ必须至少有一个为True
    
    macd, signal, histogram = calculate_macd(prices)
    rsi = calculate_rsi(prices)
    k, d, j = calculate_kdj(prices)
    
    # 策略条件：MACD、RSI和KDJ出现低位金叉时买入
    buy_signal = True
    if MACD:
        buy_signal = buy_signal & (macd > signal)
    if RSI:
        buy_signal = buy_signal & (rsi < 30)
    if KDJ:
        buy_signal = buy_signal & (k > d) & (j > k)
    #buy_signal = (macd > signal) & (rsi < 30) & (k > d) & (j > k)


    # MACD、RSI和KDJ出现高位死叉时卖出
    sell_signal = True
    if MACD:
        sell_signal = sell_signal & (macd < signal)
    if RSI:
        sell_signal = sell_signal & (rsi > 70)
    if KDJ:
        sell_signal = sell_signal & (k < d) & (j < k)

    #sell_signal = (macd < signal) & (rsi > 70) & (k < d) & (j < k)
    
    signals = pd.Series(0, index=prices.index)  # 初始化信号列
    signals[buy_signal] = 1  # 买入信号
    signals[sell_signal] = -1  # 卖出信号
    
    return signals

#==============================================================================
#==============================================================================
#==============================================================================
if __name__=='__main__':
        
    # 回测期间
    start="2015-1-1"
    end  ="2024-12-31"
    
    price_type="Close"
    initial_balance=1000000
    slippage=0.001
    fee_rate=0.0005
    min_shares=100
    printout=True
    
    equity_curve=backtest(prices, signals, start, end)


def backtest(prices, signals, \
             start, end, \
             RF=0, \
             strategy_name="", \
             initial_balance=1000000, slippage=0.001, fee_rate=0.0005, \
             min_shares=100, \
             price_type="Close", \
                 
             printout=True):
    """
    通用回测策略，模拟买入卖出过程，计算账户余额和持仓情况，考虑滑点和手续费
    每次买卖的股票数量设定为最小单位（如100股），且股票数量必须为整数
    
    交易时点：遇到买入点，全仓；遇到卖出点，空仓
    
    prices：股价
    signals：交易信号
    start：回测区间开始日期
    end：回测区间结束日期
    initial_balance：期初资金量，默认1,000,000元。如果只有十万元，甚至无法购买一手贵州茅台
    slippage：滑点比例，默认0.001，即0.1%
    fee_rate：交易费用率，默认0.0005，即0.05%
    min_shares：最小交易单位，默认100股
    printout：是否打印结果True
    """
    
    if signals.empty:
        print("交易信号为空，无法回测")
        return [initial_balance]
    
    prices2=prices[start:end]
    signals2=signals[start:end]
    
    balance = initial_balance  # 初始资金
    position = 0  # 初始持仓
    equity_curve = []  # 记录每个时间点的净值

    # 遍历每个交易日，模拟交易
    trade_activity=False
    first_trade=True
    
    for i in range(1, len(prices2)):
        current_price = prices2[price_type].iloc[i]
        price_with_slippage = add_slippage(current_price, slippage)  # 考虑滑点后的价格
        transaction_fee = calculate_transaction_fee(price_with_slippage, position, fee_rate)  # 计算交易费用

        trddate=prices2.index[i]
        trddate=trddate.strftime("%Y-%m-%d")

        # 买入信号：当信号为1时，买入
        if signals2[i] == 1 and position == 0:  # 只有当前没有持仓时才可以买入
            # 计算买入股数，确保股票数量不小于min_shares，并且是整数
            max_shares_to_buy = balance / price_with_slippage  # 根据当前余额计算可以买入的最大股数
            shares_to_buy = max(int(max_shares_to_buy), min_shares)  # 股票数量必须为整数，且大于等于 min_shares

            # 确保买入时余额足够
            if shares_to_buy * price_with_slippage + transaction_fee <= balance:
                # 买入股票并更新余额和持仓
                position = shares_to_buy
                balance -= shares_to_buy * price_with_slippage + transaction_fee  # 扣除买入费用和滑点

                # 打印交易信息
                if printout:
                    trade_activity=True
                    if first_trade:
                        first_trade=False
                        print(f"*** 交易活动：{start} 至 {end}")
                    
                    print(f"  买入：{trddate}，股价：{current_price:.2f}，买入股数：{shares_to_buy}，余额：{balance:.2f}，持仓：{position}")
            else:
                if printout:
                    print(f"  资金不足，无法买入：{trddate}，股价：{current_price:.2f}，当前余额：{balance:.2f}")

        # 卖出信号：当信号为-1时，卖出
        elif signals2[i] == -1 and position > 0:  # 只有当前有持仓时才可以卖出
            # 卖出股票并更新余额
            balance += position * price_with_slippage - transaction_fee  # 卖出后得到余额，扣除滑点和手续费
            shares_sold = position
            position = 0  # 清空持仓

            # 打印交易信息
            if printout:
                trade_activity=True
                print(f"  卖出：{trddate}，股价：{current_price:.2f}，卖出股数：{shares_sold}，余额：{balance:.2f}，持仓：{position}")

        # 计算当前时点的净值
        equity = balance + position * price_with_slippage
        equity_curve.append(equity)

    # 返回净值序列
    equity_curve = pd.Series(equity_curve, index=prices2.index[1:])
    
    if trade_activity:
        print('') #空一行
        metrics=calculate_metrics(prices, equity_curve, start, end, RF=RF, \
                                  strategy_name=strategy_name, \
                                  initial_balance=initial_balance, \
                                  slippage=slippage, fee_rate=fee_rate, \
                                  min_shares=min_shares, price_type=price_type, \
                                      printout=printout)
            
    else:
        print("无交易活动，无法进行回测")
    
    return equity_curve

#==============================================================================


def calculate_metrics(prices, equity_curve, \
                      start, end, \
                      RF=0, \
                          
                    strategy_name="", \
                    initial_balance=1000000, slippage=0.001, fee_rate=0.0005, \
                    min_shares=100, \
                    price_type="Close", \
                      printout=True):
    """
    功能：计算累计收益率、年化收益率、最大回撤、夏普比率、胜率和盈亏比
    累计收益率：回测期间内资产增长的比例。
    年化收益率 (CAGR)：复合年化增长率。
    最大回撤 (Max Drawdown)：在回测期间资产从最高点到最低点的最大跌幅。
    夏普比率 (Sharpe Ratio)：衡量单位风险的超额收益，通常用资产收益率减去无风险利率，再除以收益的标准差。
    胜率：策略在回测期间盈利的交易次数占总交易次数的比例。
    盈亏比：盈利交易的平均收益和亏损交易的平均损失的比值。
    """
    prices2=prices[start:end]
    
    # 计算回测期的年数
    start_date = pd.to_datetime(start)
    end_date = pd.to_datetime(end)
    period_years = (end_date - start_date).days / 365.25

    # 计算累计收益率
    cumulative_return = (equity_curve.iloc[-1] / equity_curve.iloc[0]) - 1
    
    # 计算年化收益率 (CAGR)
    cagr = (equity_curve.iloc[-1] / equity_curve.iloc[0]) ** (1 / period_years) - 1
    
    # 计算最大回撤
    peak = equity_curve.cummax()
    drawdown = (equity_curve - peak) / peak
    max_drawdown = drawdown.min()

    # 计算夏普比率 (假设使用日频率)
    daily_returns = equity_curve.pct_change().dropna()
    excess_returns = daily_returns - RF / 252  # 252个交易日
    sharpe_ratio = excess_returns.mean() / excess_returns.std() * np.sqrt(252)
    
    # 计算胜率和盈亏比
    daily_returns_price = prices2[price_type].pct_change().dropna()
    
    # 计算胜率
    winning_trades = daily_returns_price[daily_returns_price > 0].count()
    losing_trades = daily_returns_price[daily_returns_price < 0].count()
    win_rate = winning_trades / (winning_trades + losing_trades) if (winning_trades + losing_trades) > 0 else 0

    # 计算盈亏比（胜利交易的平均收益与亏损交易的平均损失的比）
    if winning_trades > 0:
        avg_win = daily_returns_price[daily_returns_price > 0].mean()
    else:
        avg_win = 0  # 如果没有盈利交易，设为0
    
    if losing_trades > 0:
        avg_loss = daily_returns_price[daily_returns_price < 0].mean()
    else:
        avg_loss = 0  # 如果没有亏损交易，设为0
    
    if avg_loss != 0:
        profit_loss_ratio = avg_win / abs(avg_loss)
    else:
        #profit_loss_ratio = np.nan  # 如果没有亏损交易，盈亏比无法计算
        profit_loss_ratio = "没有亏损交易，无盈亏比"

    metrics= {
        '累计收益率': cumulative_return,
        '年化收益率 (CAGR)': cagr,
        '最大回撤': max_drawdown,
        '夏普比率': sharpe_ratio,
        '胜率': win_rate,
        '盈亏比': profit_loss_ratio
        }
    
    if printout:
        # 输出结果
        print(f"*** {strategy_name}回测结果：{start} 至 {end}")
        
        ticker=prices2['ticker'].values[0]
        print(f"  股票：{ticker_name(ticker)}")
        for metric, value in metrics.items():
            if isinstance(value,float):
                if metric == "夏普比率":
                    print(f"  {metric}: {value:.4f}")
                else:
                    print(f"  {metric}: {value*100:.2f}%")
            else:
                print(f"  {metric}: {value}")
        

    return metrics


if __name__ =="__main__":
    # 示例数据
    prices = pd.Series([100, 105, 110, 115, 120])  # 假设的股价数据
    equity_curve = pd.Series([100, 110, 120, 115, 125])  # 假设的回测资产值
    start = '2020-01-01'
    end = '2023-01-01'
    RF = 0.02  # 无风险利率 (年化)
    
    # 计算绩效指标
    metrics = calculate_metrics(start_date, end_date, prices, equity_curve, RF)
    
    # 输出结果
    for metric, value in metrics.items():
        print(f"{metric}: {value:.4f}")

#==============================================================================
if __name__ =="__main__":
    
    df=strategy_trend(ticker, prices, equity_curve, 
                    start, end, \
                    twinx=True, strategy_name="高低点策略")
    
def strategy_trend(prices, equity_curve, 
                    start, end, \
                    twinx=True, \
                    loc1='upper left',loc2='upper right', \
                    facecolor='whitesmoke', \
                     
                     strategy_name="", \
                     initial_balance=1000000, slippage=0.001, fee_rate=0.0005, \
                     min_shares=100, \
                     price_type="Close"):
    """
    可视化回测结果：绘制账户余额的变化曲线
    参数:
    - prices: 收盘价数据
    - equity_curve: 回测的账户余额曲线
    """
    ticker=prices['ticker'].values[0]
    titletxt="量化策略回测："+ticker_name(ticker)
    
    footnote1="注：资产净值横线表示持币观望"
    if strategy_name != "":
        titletxt=titletxt + "，"+strategy_name
    
    ending_balance=round(equity_curve[-1],2)
    if ending_balance > initial_balance:
        sign='+'
    elif ending_balance < initial_balance:
        sign='-'
    else:
        sign=''
        
    change=str(round(abs(ending_balance/initial_balance-1)*100,2))+'%'
    footnote2="期初资金量"+str(initial_balance)+ \
                ", 滑点"+str(slippage*100)+"%"+ \
                ", 费率"+str(fee_rate*100)+"%"+ \
                ", 最小交易股数"+str(min_shares)+ \
                ", 期末资产净值"+str(ending_balance)+" ("+sign+change+")"
    footnote='\n' + footnote1 + '\n' + footnote2

    df1=pd.DataFrame(equity_curve)
    ticker1=""
    colname1=0
    label1="资产净值"
    
    df2=prices[start:end]
    ticker2=''
    colname2=price_type
    label2="股价"
    
    ylabeltxt=''
    
    plot_line2(df1,ticker1,colname1,label1, \
                   df2,ticker2,colname2,label2, \
                   ylabeltxt,titletxt,footnote, \
                   twinx=twinx, \
                   loc1=loc1,loc2=loc2, \
                   facecolor=facecolor)
    
    return df1, df2
#==============================================================================

def month_count(start, end):
    # 计算期间的月数
    
    start = pd.to_datetime(start)
    end = pd.to_datetime(end)
    months = (end.year - start.year) * 12 + (end.month - start.month) + 1
    return months

if __name__ =="__main__":
    # 示例
    month_count("2007-01-01", "2025-06-30") #222
    month_count("2023-01-01", "2025-06-30") #30
    month_count("2018-01-01", "2023-12-31") #72
    month_count("2016-01-01", "2022-12-31") #84
    month_count("2019-01-01", "2024-12-31") #72
    month_count("2021-09-01", "2022-06-30") #10

#==============================================================================
#==============================================================================




















