# -*- coding: utf-8 -*-
"""
本模块功能：股票技术分析 technical analysis
所属工具包：证券投资分析工具SIAT 
SIAT：Security Investment Analysis Tool
创建日期：2023年1月27日
最新修订日期：2025年1月31日
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
from siat.grafix import *
from siat.security_prices import *
from siat.security_price2 import *
from siat.stock import *
from siat.valuation import *
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

import mplfinance as mpf

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

#设置绘图风格：关闭网格虚线
plt.rcParams['axes.grid']=False

#==============================================================================
#==============================================================================
#==============================================================================

if __name__ =="__main__":
    RSI_days=[6,24]
    
    OBV_days=5
    
    MA_days=[5,20]; MACD_fastperiod=12; MACD_slowperiod=26; MACD_signalperiod=9
    
    KDJ_fastk_period=5; KDJ_slowk_period=3; KDJ_slowk_matype=0; KDJ_slowd_period=3
    KDJ_slowd_matype=0
    
    VOL_fastperiod=5; VOL_slowperiod=10
    
    PSY_days=12
    
    ARBR_days=26
    
    CR_day=16; CR_madays=[5,10,20]
    
    EMV_day=14; EMV_madays=9
    
    BOLL_days=20; BOLL_nbdevup=2; BOLL_nbdevdn=2; BOLL_matype=0
    
    TRIX_day=12; TRIX_madays=20
    
    DMA_fastperiod=10; DMA_slowperiod=50; DMA_madays=10
    
    BIAS_days=[6,12,24]
    
    CCI_days=[6,12]
    
    WR_days=[10,6]
    
    ROC_day=12; ROC_madays=6
    
    DMI_DIdays=14; DMI_ADXdays=6
    
    ticker='AAPL'
    
    start='2024-3-1'; end='2024-4-12'; ahead_days=30*3
    start1=date_adjust(start,adjust=-ahead_days)
    
    df=get_price(ticker,start1,end)
    ta=calc_technical(df,start,end)
    
    df1,found=get_price_1ticker_mixed(ticker=ticker,fromdate=start1,todate=end)
    ta=calc_technical(df1,start,end)
    
    ta=calc_technical(df,start,end)
    
    #OBV: 纵轴数量级大(千万)，判断是否加零线(有正有负)，如加零线则不加均值线，不加零线时判断是否可加均值线
    df_ta[['obv','obv_ma']].plot(title=ticker_name(ticker)+': '+'能量潮OBV')
    
    #SAR: 纵轴数量级不大
    df_ta[['sar']].plot(title=ticker_name(ticker)+': '+'抛物转向SAR')    
    
    #VOL: 纵轴数量级大，无零线，可加均值线
    df_ta[['vol5','vol10']].plot(title=ticker_name(ticker)+': '+'成交量VOL')    
    
    #ARBR: 纵轴数量级不大，无零线，无均值线
    df_ta[['ar','br']].plot(title=ticker_name(ticker)+': '+'人气与意愿ARBR')    
    
    #CR: 纵轴数量级不大，无零线
    df_ta[['cr','crma5','crma10','crma20']].plot(title=ticker_name(ticker)+': '+'能力与意愿CR')   
    df_ta[['cr','crma5','crma20']].plot(title=ticker_name(ticker)+': '+'能力与意愿CR')
    df_ta[['cr']].plot(title=ticker_name(ticker)+': '+'能力与意愿CR')
    
    #EMV: 纵轴数量级大
    df_ta[['em','emv','emva']].plot(title=ticker_name(ticker)+': '+'简易波动EMV') 
    df_ta[['em','emv']].plot(title=ticker_name(ticker)+': '+'简易波动EMV')      
    
    #TRIX: 纵轴数量级不大
    df_ta[['trix','trma']].plot(title=ticker_name(ticker)+': '+'三重指数平滑TRIX')      
    
    #DMA: 纵轴数量级不大
    df_ta[['dma']].plot(title=ticker_name(ticker)+': '+'均线差DMA')      
    
    #BIAS: 纵轴数量级不大
    df_ta[['bias','bias2','bias3']].plot(title=ticker_name(ticker)+': '+'乖离率BIAS')  
    df_ta[['bias']].plot(title=ticker_name(ticker)+': '+'乖离率BIAS')  
    
    #CCI: 纵轴数量级不大
    df_ta[['cci']].plot(title=ticker_name(ticker)+': '+'顺势CCI')  
    
    #W%R: 纵轴数量级不大
    df_ta[['wr6','wr10']].plot(title=ticker_name(ticker)+': '+'威廉W%R')      
    
    #ROC: 纵轴数量级不大
    df_ta[['roc','rocma']].plot(title=ticker_name(ticker)+': '+'变动速率ROC') 
    
    #DMI: 纵轴数量级不大
    df_ta[['pdi','mdi','adx','adxr']].plot(title=ticker_name(ticker)+': '+'趋向DMI') 
    df_ta[['pdi','mdi']].plot(title=ticker_name(ticker)+': '+'趋向DMI')
    df_ta[['adx','adxr']].plot(title=ticker_name(ticker)+': '+'趋向DMI') 
    
    #PSY: 纵轴数量级不大
    df_ta[['psy']].plot(title=ticker_name(ticker)+': '+'心理线PSY') 

    
    
def calc_technical(df,start,end,technical='MACD', \
                   
        RSI_days=[14], \
        OBV_days=[5], \
            
        MA_days=[5,20],EMA_days=[5,20], \
        MACD_fastperiod=12,MACD_slowperiod=26,MACD_signalperiod=9, \
            
        KDJ_fastk_period=9,KDJ_slowk_period=5,KDJ_slowk_matype=1,KDJ_slowd_period=5,KDJ_slowd_matype=1, \
            
        VOL_fastperiod=5,VOL_slowperiod=10, \
        PSY_days=[12], \
        ARBR_days=[26], \
        CR_day=16,CR_madays=[5,10,20], \
        EMV_day=14,EMV_madays=[9], \
            
        BOLL_day=20,BOLL_nbdevup=2,BOLL_nbdevdn=2,BOLL_matype=0, \
            
        DMA_fastperiod=10,DMA_slowperiod=50,DMA_madays=[10], \
            
        TRIX_day=12,TRIX_madays=[20], \
        BIAS_days=[6,12,24], \
        CCI_days=[6,12], \
        WR_days=[10,6], \
        ROC_day=12,ROC_madays=[6], \
        DMI_DIdays=[14],DMI_ADXdays=[6], \
            
        MFI_day=14,MFI_madays=[6], \
            
        #提出选择12日或25日，移动均线为10日            
        MOM_day=12,MOM_madays=6, \
            
        #需要显示SAR
        SAR_day=4,SAR_madays=[5,20], \
            
        #需要显示BETA
        BETA_day=5,BETA_madays=[5,20], \
        
        #需要显示TSF
        TSF_day=14,TSF_madays=[5,20], \
            
        #需要显示AD
        AD_madays=[5], \
        
        #不建议使用复权价，因为最高最低价和开盘价没有复权价！
        indicator='Close', \
        more_details=False):
    """
    功能：计算股票的技术分析指标
    输入：df，四种股价Open/Close/High/Low，成交量Volume
    输出：df
    支持的指标：
    RSI、OBV、MACD、 KDJ、 SAR、  VOL、 PSY、 ARBR、 CR、 EMV、 
    BOLL、 TRIX、 DMA、 BIAS、 CCI、 W%R、 ROC、 DMI
    
    注意：indicator='Close'为不使用复权价，'Adj Close'为前复权价（需要指定source='yahoo'）
    """
    if indicator not in ['Close','Adj Close']:
        print("  #Error(calc_technical): unsupported indicator",indicator)
        print("  Supported indicator: Close, Adj Close")
        
        return None
    
    # 导入需要的包
    try:
        import talib  
    except:
        print("  #Error(calc_technical): lack of necessary package - talib")
        talib_install_method()
        return None
    
    #用于对比，检查是否有计算结果的指标加入
    dfcols_original=list(df)
    
    #=========== RSI，相对强弱指标Relative Strength Index
    """
    计算公式：RSI有两种计算方法：
        第一种方法：
        假设A为N日内收盘价涨幅的正数之和，B为N日内收盘价涨幅的负数之和再乘以（-1），
        这样，A和B均为正，将A，B代入RSI计算公式，则：
        RSI(N) = A ÷ （A + B） × 100
        第二种方法：
        RS(相对强度) = N日内收盘价涨数和之均值 ÷ N日内收盘价跌数和之均值
        RSI = 100 - 100 ÷ （1+RS）
        
    指标解读：
    80-100 极强 卖出
    50-80 强 观望，谨慎卖出
    30-50 弱 观望，谨慎买入
    0-30 极弱 买入        
    """
    if technical=='RSI':
    
        if not isinstance(RSI_days,list):
            RSI_days=[RSI_days]
        for d in RSI_days:
            df['rsi'+str(d)] = talib.RSI(df[indicator], timeperiod=d)
        #注意：rsi1没有意义
    
    #=========== OBV：能量潮
    """
    OBV的英文全称是：On Balance Volume，是由美国的投资分析家Joe Granville所创。
    该指标通过统计成交量变动的趋势来推测股价趋势。
    OBV指标所谓股市人气，指投资者活跃在股市上的程度。
    如果买卖双方交易热情高，股价、成交量就上升，股市气氛则热烈。
    因此，利用股价和股票成交量的指标来反映人气的兴衰，就形成了OBV指标。
    
    OBV = 前一天的OBV ± 当日成交量
    说明：（当日收盘价高于前日收盘价，成交量定位为正值，取加号；
    当日收盘价低于前日收盘价，成交量定义为负值，取减号；二者相等计为0）
    
    指标解读：
    1、当股价上升而OBV线下降，表示买盘无力，股价可能会回跌。
    2、股价下降时而OBV线上升，表示买盘旺盛，逢低接手强股，股价可能会止跌回升。
    3、OBV线缓慢上升，表示买气逐渐加强，为买进信号。
    4、OBV线急速上升时，表示力量将用尽为卖出信号。
    5、OBV线从正的累积数转为负数时，为下跌趋势，应该卖出持有股票。反之，OBV线从负的累积数转为正数时，应该买进股票。
    6、OBV线最大的用处，在于观察股市盘局整理后，何时会脱离盘局以及突破后的未来走势，OBV线变动方向是重要参考指数，其具体的数值并无实际意义。    
    
    缺点
    OBV指标是建立在国外成熟市场上的经验总结。
    用在内地股市坐庄的股票上就不灵了，这时股价涨得越高成交量反而越少。
    这是因为主力控盘较重，股价在上涨过程中没有获利筹码加以兑现，所以此时股票会涨得很“疯”，但成交量并不增加，OBV自然就无法发挥作用。
    另外，涨跌停板的股票也会导致指标失真。
    由于内地股市采用了涨跌停板的限制，很多股票在连续涨停的时候，由于股民预期后市会继续大涨，往往会持股观望，导致出现越涨越无量的现象。
    因此，对于那些达到涨跌停板的股票，OBV指标也无法正常发挥作用。    
    
    """
    if technical=='OBV':
    
        df['obv'] = talib.OBV(df[indicator],df['Volume'])
        
        if not isinstance(OBV_days,list):
            OBV_days=[OBV_days]
        for d in OBV_days:    
            df['obv_ma'+str(d)] = talib.MA(df['obv'],timeperiod=d)
        
        if not more_details:    
            df.drop(columns = ['obv'],inplace=True)
    
    #=========== MA: 简单、加权移动平均
    """
    MA，又称移动平均线，是借助统计处理方式将若干天的股票价格加以平均，然后连接成一条线，用以观察股价趋势。
    移动平均线通常有3日、6日、10日、12日、24日、30日、72日、200日、288日、13周、26周、52周等等，不一而足，
    其目的在取得某一段期间的平均成本，而以此平均成本的移动曲线配合每日收盘价的线路变化分析某一期间多空的优劣形势，
    以研判股价的可能变化。
    一般来说，现行价格在平均价之上，意味着市场买力（需求）较大，行情看好；
    反之，行情价在平均价之下，则意味着供过于求，卖压显然较重，行情看淡。    
    """
    if technical=='MA':
    
        if not isinstance(MA_days,list):
            MA_days=[MA_days]
        
        for d in MA_days:
            df['ma'+str(d)] = talib.MA(df[indicator],timeperiod=d)

    if technical=='EMA':
    
        if not isinstance(EMA_days,list):
            EMA_days=[EMA_days]
        
        for d in EMA_days:
            df['ema'+str(d)] = talib.EMA(df[indicator],timeperiod=d)    
            
    #=========== MACD：指数平滑异同平均线
    """
    计算方法：快速时间窗口设为12日，慢速时间窗口设为26日，DIF参数设为9日
        3.1) 计算指数平滑移动平均值（EMA）
        12日EMA的计算公式为：
        EMA(12) = 昨日EMA(12)  ×  11 ÷ 13 + 今日收盘价 × 2 ÷ 13
        26日EMA的计算公式为：
        EMA(26) = 昨日EMA(26) × 25 ÷ 27 + 今日收盘价 × 2 ÷ 27
        
        3.2) 计算离差值（DIF）
        DIF = 今日EMA(12) – 今日EMA(26)
        
        3.3) 计算DIF的9日DEA
        根据差值计算其9日的DEA，即差值平均
        今日DEA = 昨日DEA × 8 ÷ 10 + 今日DIF × 2 ÷ 10    
    
    形态解读：
        1.DIF、DEA均为正，DIF向上突破DEA，买入信号。
        2.DIF、DEA均为负，DIF向下跌破DEA，卖出信号。
        3.DEA线与K线发生背离，行情反转信号。
        4.分析MACD柱状线，由红变绿(正变负)，卖出信号；由绿变红，买入信号。
        
    MACD一则去掉移动平均线频繁的假讯号缺陷，二则能确保移动平均线最大的战果。
        1. MACD金叉：DIF由下向上突破DEM，为买入信号。
        2. MACD死叉：DIF由上向下突破DEM，为卖出信号。
        3. MACD绿转红：MACD值由负变正，市场由空头转为多头。
        4. MACD红转绿：MACD值由正变负，市场由多头转为空头。        
    """
    if technical=='MACD':
    
        df['DIF'],df['DEA'],df['MACD']=talib.MACD(df[indicator], \
                                    fastperiod=MACD_fastperiod, \
                                    slowperiod=MACD_slowperiod, \
                                    signalperiod=MACD_signalperiod)

    #=========== KDJ: 随机指标
    """
    计算公式：
        1) 以日KDJ数值的计算为例
        N日RSV = (CN – LN)÷(HN-LN) ×100
        说明：CN为第N日收盘价；LN为N日内的最低价；HN为N日内的最高价，RSV值始终在1~100间波动
        2) 计算K值与D值
        当日K值 = 2/3 × 前一日K值 + 1/3 × 当日RSV
        当日D值 = 2/3 × 前一日D值 + 1/3 × 当日K值
        如果没有前一日K值与D值，则可分别用50来代替
        3) 计算J值
        J = 3D – 2K    
    
    指标解读：
        多头区域，空头区域
        金叉，死叉
    """
    if technical=='KDJ':
    
        df['kdj_k'],df['kdj_d'] = talib.STOCH(df['High'],df['Low'],df[indicator], \
                            fastk_period=KDJ_fastk_period,
                            slowk_period=KDJ_slowk_period, 
                            slowk_matype=KDJ_slowk_matype, 
                            slowd_period=KDJ_slowd_period, 
                            slowd_matype=KDJ_slowd_matype)
        df['kdj_j'] = 3*df['kdj_k'] - 2*df['kdj_d']

    #=========== SAR: 抛物转向
    """
    计算过程：
        1）先选定一段时间判断为上涨或下跌
        2）如果是看涨，则第一天的SAR值必须是近期内的最低价；
        如果是看跌，则第一天的SAR值必须是近期的最高价。
        3）第二天的SAR值，则为第一天的最高价（看涨时）或是最低价（看跌时）与第一天的SAR值的差距乘上加速因子，
        再加上第一天的SAR值就可以求得。
        4）每日的SAR值都可用上述方法类推，公式归纳如下：
        SAR(N) = SAR(N-1) + AF × [(EP(N-1) – SAR(N-1))]
        SAR(N) = 第N日的SAR值
        SAR(N-1) = 第(N-1)日的SAR值
        说明：AF表示加速因子；EP表示极点价，如果是看涨一段期间，则EP为这段时间的最高价，
        如果是看跌一段期间，则EP为这段时间的最低价；EP(N-1)等于第(N-1)日的极点价
        5）加速因子第一次取0.02，假若第一天的最高价比前一天的最高价还高，则加速因子增加0.02，
        如无新高则加速因子沿用前一天的数值，但加速因子最高不能超过0.2。反之，下跌也类推
        6）如果是看涨期间，计算出某日的SAR值比当日或前一日的最低价高，则应以当日或前一日的最低价为某日之SAR值；
        如果是看跌期间，计算某日的SAR值比当日或前一日的最高价低，则应以当日或前一日的最高价为某日的SAR值。
        7）SAR指标基准周期的参数为2，如2日、2周、2月等，其计算周期的参数变动范围为2~8
        8）SAR指标在股价分析系统的主图上显示为“O”形点状图。    
    """
    if technical=='SAR':
    
        df['sar'] = talib.SAR(df['High'],df['Low'])
        
        if not isinstance(SAR_madays,list):
            SAR_madays=[SAR_madays]
        for d in SAR_madays:    
            df['sar_ma'+str(d)] = df['sar'].rolling(window=d).mean()    
            
        #需要显示SAR?
        """
        if not more_details:
            #不保留指标本身
            df.drop(columns = ['sar'],inplace=True) 
        """
    #=========== VOL: 成交量
    """
    柱状图是成交量，两条曲线是成交量的移动平均    
    """
    if technical=='VOL':
    
        df['vol'+str(VOL_fastperiod)] = talib.MA(df['Volume'],timeperiod=VOL_fastperiod)
        df['vol'+str(VOL_slowperiod)] = talib.MA(df['Volume'],timeperiod=VOL_slowperiod)
    
    #=========== PSY: 心理线
    """
    计算公式：
    PSY(N) = A/N × 100
    说明：N为天数，A为在这N天之中股价上涨的天数    
    """
    if technical=='PSY':
    
        df['ext_0'] = df[indicator]-df[indicator].shift(1)
        df['ext_1'] = 0
        df.loc[df['ext_0']>0,'ext_1'] = 1
        
        if not isinstance(PSY_days,list):
            PSY_days=[PSY_days]
        for d in PSY_days:    
            df['ext_2'] = df['ext_1'].rolling(window=d).sum()
            df['psy'+str(d)] = (df['ext_2']/float(d))*100
        
        df.drop(columns = ['ext_0','ext_1','ext_2'],inplace=True) 
    
    #=========== ARBR: 人气和意愿指标, AR为人气指标，BR为买卖意愿指标
    """
    计算公式：
    AR(N) = N日内（H-O）之和 ÷ N日内（O-L）之和 × 100
    说明：H表示当天最高价；L表示当天最低价；O表示当天开盘价；N表示设定的时间参数，一般原始参数日缺省值为26日
    BR(N) = N日内（H-CY）之和 ÷ N日内（CY-L）之和 × 100
    说明：H表示当天最高价；L表示当天最低价；CY表示前一交易日的收盘价，N表示设定的时间参数，一般原始参数缺省值为26日    
    """
    if technical=='ARBR':
    
        df['h_o'] = df['High'] - df['Open']
        df['o_l'] = df['Open'] - df['Low']
        
        if not isinstance(ARBR_days,list):
            ARBR_days=[ARBR_days]
        for d in ARBR_days:    
            df['h_o_sum'] = df['h_o'].rolling(window=d).sum()
            df['o_l_sum'] = df['o_l'].rolling(window=d).sum()
            df['ar'+str(d)] = (df['h_o_sum']/df['o_l_sum'])*100
        
        
        df['h_c'] = df['High'] - df[indicator]
        df['c_l'] = df[indicator] - df['Low']
        for d in ARBR_days:    
            df['h_c_sum'] = df['h_c'].rolling(window=d).sum()
            df['c_l_sum'] = df['c_l'].rolling(window=d).sum()
            df['br'+str(d)] = (df['h_c_sum']/df['c_l_sum'])*100
    
        df.drop(columns = ['h_o','o_l','h_o_sum','o_l_sum','h_c','c_l','h_c_sum','c_l_sum'],inplace=True) 

    #=========== CR: 带状能力线或中间意愿指标
    """
    计算过程：
    1）计算中间价，取以下四种中一种，任选：
    中间价 = （最高价 + 最低价）÷2
    中间价 = （最高价 + 最低价 + 收盘价）÷3
    中间价 = （最高价 + 最低价 + 开盘价 + 收盘价）÷4
    中间价 = （2倍的开盘价 + 最高价 + 最低价）÷4
    2）计算CR:
    CR = N日内（当日最高价 – 上个交易日的中间价）之和 ÷ N日内（上个交易日的中间价 – 当日最低价）之和
    说明：N为设定的时间周期参数，一般原始参数日设定为26日
    3）计算CR值在不同时间周期内的移动平均值：这三条移动平均曲线分别为MA1 MA2 MA3,时间周期分别为5日 10日 20日    
    """
    if technical=='CR':
    
        df['m_price'] = (df['High'] + df['Low'])/2
        df['h_m'] = df['High']-df['m_price'].shift(1)
        df['m_l'] = df['m_price'].shift(1)-df['Low']
        
        df['h_m_sum'] = df['h_m'].rolling(window=CR_day).sum()
        df['m_l_sum'] = df['m_l'].rolling(window=CR_day).sum()
        df['cr'] = (df['h_m_sum']/df['m_l_sum'])*100
        
        for d in CR_madays:
            df['cr_ma'+str(d)] = talib.MA(df['cr'],timeperiod=d)
        
        df.drop(columns = ['m_price','h_m','m_l','h_m_sum','m_l_sum'],inplace=True)
        if not more_details:
            df.drop(columns = ['cr'],inplace=True) 
    
    #=========== EMV: 简易波动指标
    """
    计算方法：
    1）先计算出三个因子A B C的数值。
    A = (当日最高价 + 当日最低价)÷2
    B = (上个交易日最高价 + 上个交易日最低价) ÷2
    C = 当日最高价 – 当日最低价
    2）求出EM数值
    EM = (A-B) ×C÷当日成交额
    3）求出EMV数值
    EMV = EM数值的N个交易日之和，N为时间周期，一般设为14日
    4）求出EMV的移动平均值EMVA
    EMVA = EMV的M日移动平均值，M一般设置9日    
    """
    if technical=='EMV':
    
        df['a'] = (df['High']+df['Low'])/2
        df['b'] = (df['High'].shift(1)+df['Low'].shift(1))/2
        df['c'] = df['High'] - df['Low']
        df['Amount']=df[indicator]*df['Volume']
        df['em'] = (df['a']-df['b'])*df['c']/df['Amount']
        
        df['emv'] = df['em'].rolling(window=EMV_day).sum()
        
        if not isinstance(EMV_madays,list):
            EMV_madays=[EMV_madays]
        for d in EMV_madays:    
            df['emv_ma'+str(d)] = talib.MA(df['emv'],timeperiod=d)
    
        df.drop(columns = ['a','b','c','em'],inplace=True) 
    
    #=========== BOLL: 布林线指标
    """
    计算公式：
        中轨线 = N日的移动平均线
        上轨线 = 中轨线 + 两倍的标准差
        下轨线 = 中轨线 – 两倍的标准差
    计算过程：
        1）先计算出移动平均值MA
        MA = N日内的收盘价之和÷N
        2）计算出标准差MD的平方
        MD的平方 = 每个交易日的（收盘价-MA）的N日累加之和的两次方 ÷ N
        3）求出MD
        MD = （MD的平方）的平方根
        4）计算MID、UPPER、LOWER的数值
        MID = (N-1)日的MA
        UPPER = MID + 2×MD
        LOWER = MID – 2×MD
        说明：N一般原始参数日缺省值为20日    
    
    指标解读：
        BOLL指标即布林线指标，其利用统计原理，求出股价的标准差及其信赖区间，
        从而确定股价的波动范围及未来走势，利用波带显示股价的安全高低价位，因而也被称为布林带。
        其上下限范围不固定，随股价的滚动而变化。布林指标股价波动在上限和下限的区间之内，
        这条带状区的宽窄，随着股价波动幅度的大小而变化，股价涨跌幅度加大时，带状区变宽，
        涨跌幅度狭小盘整时，带状区则变窄。    
    """
    if technical=='Bollinger':
    
        df['upper'],df['mid'],df['lower'] = talib.BBANDS(df[indicator], \
                    timeperiod=BOLL_day, \
                    nbdevup=BOLL_nbdevup,nbdevdn=BOLL_nbdevdn,matype=BOLL_matype)                     
    
    #=========== TRIX：三重指数平滑移动平均指标
    """
    
    """
    if technical=='TRIX':
    
        df['trix'] = talib.TRIX(df[indicator],timeperiod=TRIX_day)
        
        if not isinstance(TRIX_madays,list):
            TRIX_madays=[TRIX_madays]
        for d in TRIX_madays:    
            df['trix_ma'+str(d)] = talib.MA(df['trix'],timeperiod=d)    
        """
        if not more_details:
            #不保留TRIX
            df.drop(columns = ['trix'],inplace=True) 
        """
    #=========== DMA: 平均线差
    """
    计算公式：
    DDD(N) = N日短期平均值 – M日长期平均值
    AMA(N) = DDD的N日短期平均值
    计算过程：
    以求10日、50日为基准周期的DMA指标为例
    1）求出周期不等的两条移动平均线MA之间的差值
    DDD(10) = MA10 – MA50
    2）求DDD的10日移动平均数值
    DMA(10) = DDD(10)÷10
    """   
    if technical=='DMA':
    
        df['ma_shortperiod'] = talib.MA(df[indicator],timeperiod=DMA_fastperiod)
        df['ma_longperiod'] = talib.MA(df[indicator],timeperiod=DMA_slowperiod)
        df['ddd'] = df['ma_shortperiod'] - df['ma_longperiod']
        
        if not isinstance(DMA_madays,list):
            DMA_madays=[DMA_madays]
        for d in DMA_madays:    
            df['dma_ma'+str(d)] = talib.MA(df['ddd'],timeperiod=d)    
        #注意：dma1似乎没有意义
        
        df.drop(columns = ['ma_shortperiod','ma_longperiod','ddd'],inplace=True) 
    
    #=========== BIAS: 乖离率
    """
    N日BIAS = （当日收盘价 – N日移动平均价）÷N日移动平均价×100
    
    指标解读：
    6日BIAS＞＋5％，是卖出时机；＜-5％，为买入时机。
    12日BIAS＞＋6％是卖出时机；＜-5.5％,为买入时机。
    24日BIAS＞＋9％是卖出时机；＜－8％，为买入时机。
    """
    if technical=='BIAS':
    
        if not isinstance(BIAS_days,list):
            BIAS_days=[BIAS_days]
        for d in BIAS_days:  
            df['ma'] = talib.MA(df[indicator],timeperiod=d)
            df['bias'+str(d)] = ((df[indicator]-df['ma'])/df['ma'])*100
        
        df.drop(columns = ['ma'],inplace=True) 

    #=========== CCI: 顺势指标
    """
    计算过程：
    CCI(N日) = （TP-MA）÷MD÷0.015
    说明：TP = （最高价+最低价+收盘价）÷3；
    MA=最近N日收盘价的累计之和÷N；
    MD=最近N日（MA-收盘价）的累计之和÷N；
    0.015为计算系数；N为计算周期，默认为14天
    """ 
    if technical=='CCI':
        """
        df['cci'] = talib.CCI(df['High'],df['Low'],df[indicator],timeperiod=CCI_days)
        
        if not isinstance(CCI_madays,list):
            CCI_madays=[CCI_madays]
        for d in CCI_madays:    
            df['cci_ma'+str(d)] = df['cci'].rolling(window=d).mean()
            
        #需要显示CCI?
        if not more_details:
            #不保留指标本身
            df.drop(columns = ['cci'],inplace=True) 
        """
        if not isinstance(CCI_days,list):
            CCI_days=[CCI_days]
            
        for d in CCI_days:    
            df['cci'+str(d)] = talib.CCI(df['High'],df['Low'],df[indicator],timeperiod=d)
        
        
    #=========== W%R: 威廉指标   
    """
    N日W%R = [(Hn-Ct)/(Hn-Ln)]*100
    Ct是计算日的收盘价；Hn/Ln为包括计算日当天的N周期内的最高（低）价  
    
    指标解读：
        威廉指标(William's %R) 原理：用当日收盘价在最近一段时间股价分布的相对位置来描述超买和超卖程度。
        算法：N日内最高价与当日收盘价的差，除以N日内最高价与最低价的差，结果放大100倍。
        参数：N 统计天数 一般取14天
        用法：
        1.低于30，超买，即将见顶，应及时卖出 
        2.高于80，超卖，即将见底，应伺机买进 
        3.与RSI、MTM指标配合使用，效果更好    
    """
    if technical=='W%R':
    
        if not isinstance(WR_days,list):
            WR_days=[WR_days]
        for d in WR_days:
            df['h_10'] = df['High'].rolling(window=d).max()
            df['l_10'] = df['Low'].rolling(window=d).min()
            df['wr'+str(d)] = ((df['h_10']-df[indicator])/(df['h_10']-df['l_10']))*100
    
        df.drop(columns = ['h_10','l_10'],inplace=True) 
    
    #=========== ROC: 变动速率指标
    """
    计算过程：
    1）计算出ROC数值
    ROC = (当日收盘价 – N日前收盘价)÷N日前收盘价×100
    说明：N一般取值为12日
    2）计算ROC移动平均线（ROCMA）数值
    ROCMA = ROC的M日数值之和÷M
    说明：M一般取值为6日    
    """
    if technical=='ROC':
    
        df['roc'] = talib.ROC(df[indicator],timeperiod=ROC_day)
        
        if not isinstance(ROC_madays,list):
            ROC_madays=[ROC_madays]
        for d in ROC_madays:    
            df['roc_ma'+str(d)] = talib.MA(df['roc'],timeperiod=d)  
        
        if not more_details:
            #不保留roc
            df.drop(columns = ['roc'],inplace=True) 
        
    #=========== DMI: 趋向指标
    """
    pdi: 正向DI
    mdi: 负向DI
    """ 
    if technical=='DMI':
    
        if not isinstance(DMI_DIdays,list):
            DMI_DIdays=[DMI_DIdays]
        for d in DMI_DIdays:    
            df['pdi'+str(d)] = talib.PLUS_DI(df['High'],df['Low'],df[indicator],timeperiod=d)
            df['mdi'+str(d)] = talib.MINUS_DI(df['High'],df['Low'],df[indicator],timeperiod=d)
            
        if not isinstance(DMI_ADXdays,list):
            DMI_ADXdays=[DMI_ADXdays]
        for d in DMI_ADXdays:    
            df['adx'+str(d)] = talib.ADX(df['High'],df['Low'],df[indicator],timeperiod=d)
            df['adxr'+str(d)] = talib.ADXR(df['High'],df['Low'],df[indicator],timeperiod=d)    
    
    #=========== MFI：资金流动指标
    """
    
    """
    if technical=='MFI':
    
        df['mfi'] = talib.MFI(df['High'],df['Low'],df[indicator],df['Volume'],timeperiod=MFI_day)
        if not isinstance(MFI_madays,list):
            MFI_madays=[MFI_madays]
        for d in MFI_madays:    
            df['mfi_ma'+str(d)] = df['mfi'].rolling(window=d).mean()
        """
        if not more_details:
            #不保留指标本身
            df.drop(columns = ['mfi'],inplace=True) 
        """
    #=========== MOM：动量指标
    """
    
    """
    if technical=='MOM':
    
        df['mom'] = talib.MOM(df[indicator],timeperiod=MOM_day)
        if not isinstance(MOM_madays,list):
            MOM_madays=[MOM_madays]
        for d in MOM_madays:    
            df['mom_ma'+str(d)] = df['mom'].rolling(window=d).mean()   
        """
        if not more_details:
            #不保留指标本身
            df.drop(columns = ['mom'],inplace=True) 
        """
    #=========== BETA：贝塔系数
    """
    动态贝塔系数？
    """
    if technical=='BETA':
    
        df['beta'] = talib.BETA(df['High'],df['Low'],timeperiod=BETA_day)
        
        if not isinstance(BETA_madays,list):
            BETA_madays=[BETA_madays]
        for d in BETA_madays:    
            df['beta_ma'+str(d)] = df['beta'].rolling(window=d).mean()   
    
        if not more_details:
            #不保留指标本身
            df.drop(columns = ['beta'],inplace=True) 
    
    #=========== TSF：时间序列预测
    """
    
    """
    if technical=='TSF':
    
        df['tsf'] = talib.TSF(df[indicator],timeperiod=TSF_day)
        
        if not isinstance(TSF_madays,list):
            TSF_madays=[TSF_madays]
        for d in TSF_madays:    
            df['tsf_ma'+str(d)] = df['tsf'].rolling(window=d).mean()   
    
        if not more_details:
            #不保留指标本身
            df.drop(columns = ['tsf'],inplace=True) 
    
    #=========== AD：量价指标
    """
    
    """
    if technical=='AD':
    
        df['ad'] = talib.AD(df['High'],df['Low'],df[indicator],df['Volume'])
        
        if not isinstance(AD_madays,list):
            AD_madays=[AD_madays]
        for d in AD_madays:    
            df['ad_ma'+str(d)] = df['ad'].rolling(window=d).mean()   
        """
        if not more_details:
            #不保留指标本身
            df.drop(columns = ['ad'],inplace=True) 
        """

    
    #过滤日期===================================================================
    _,startpd,endpd=check_period(start,end)
    df1=df[(df.index >= startpd) & (df.index <= endpd)]
    
    #检查是否加入了计算结果的指标
    dfcols=list(df)
    if len(dfcols) > len(dfcols_original):
        calculated=True
    else:
        calculated=False
    
    return df1,calculated


#==============================================================================
#==============================================================================
#==============================================================================

if __name__ =="__main__":
    ticker='600519.SS'
    start='2022-6-1'
    end='2022-6-30'
    
    MA_days=[5,20]
    EMA_days=[5,20]
    
    MACD_fastperiod=12
    MACD_slowperiod=26
    MACD_signalperiod=9
    
    loc1='upper left'
    loc2='center right'
    
    resample_freq='H'
    smooth=True
    linewidth=1.5
    graph=['MA']
    graph=['EMA']
    graph=['MACD']
    printout=True

def security_MACD(ticker,start='default',end='default', \
             MA_days=[5,20],EMA_days=[5,20], \
             MACD_fastperiod=12,MACD_slowperiod=26,MACD_signalperiod=9, \
             resample_freq='6H',smooth=True,linewidth=1.5, \
             loc1='lower left',loc2='lower right', \
             graph=['ALL'],printout=True,ticker_type='auto',source='auto', \
             price_line_color='red',facecolor='k'):
    """
    套壳函数：可用于股票、交易所债券、交易所基金、部分期货期权(限美股)
    """
    df=stock_MACD(ticker=ticker,start=start,end=end, \
                 MA_days=MA_days,EMA_days=EMA_days, \
                 MACD_fastperiod=MACD_fastperiod,MACD_slowperiod=MACD_slowperiod, \
                 MACD_signalperiod=MACD_signalperiod, \
                 resample_freq=resample_freq,smooth=smooth,linewidth=linewidth, \
                 loc1=loc1,loc2=loc2, \
                 graph=graph,printout=printout,ticker_type=ticker_type,source=source, \
                 price_line_color=price_line_color,facecolor=facecolor)
    return df
    
    
def stock_MACD(ticker,start='default',end='default', \
             MA_days=[5,20],EMA_days=[5,20], \
             MACD_fastperiod=12,MACD_slowperiod=26,MACD_signalperiod=9, \
             resample_freq='H',smooth=True,linewidth=1.5, \
             loc1='lower left',loc2='lower right', \
             graph=['ALL'],printout=True,ticker_type='auto',source='auto', \
             price_line_color='blue',facecolor='white'):
    """
    功能：计算股票的技术分析指标MACD
    输入：df，四种股价Open/Close/High/Low，成交量Volume
    输出：df
    含有指标：
    MA5、MA20、MACD_fastperiod、 MACD_slowperiod、MACD_signalperiod
    """
    
    #=========== 导入需要的包
    try:
        import talib  
    except:
        print("  #Error(stock_MACD): lack of necessary module - ta-lib")
        talib_install_method()        
        return None
    
    #=========== 日期转换与检查
    # 检查日期：截至日期
    import datetime as dt; today=dt.date.today()
    if end in ['default','today']:
        end=today
    else:
        validdate,end=check_date2(end)
        if not validdate:
            print("  #Warning(stock_MACD): invalid date for",end)
            end=today

    # 检查日期：开始日期
    if start in ['default']:
        start=date_adjust(end,adjust=-31)
    else:
        validdate,start=check_date2(start)
        if not validdate:
            print("  #Warning(stock_MACD): invalid date for",start)
            start=date_adjust(todate,adjust=-31)
    
    #=========== 获取股价和成交量数据
    result,startpd,endpd=check_period(start,end)
    
    days_list=MA_days+EMA_days+[MACD_fastperiod]+[MACD_slowperiod]+[MACD_signalperiod]
    max_days=max(days_list)
    start1=date_adjust(start,adjust=-max_days * 3)
    
    #df=get_price(ticker,start1,end)
    df,found=get_price_1ticker_mixed(ticker=ticker,fromdate=start1,todate=end,ticker_type=ticker_type,source=source)
    if df is None:
        print("  #Error(stock_MACD): no info found for",ticker,"from",start,"to",end)
        return None
    if len(df)==0:
        print("  #Error(stock_MACD): zero record found for",ticker,"from",start,"to",end)
        return None   
    
    #=========== MA: 简单、加权移动平均
    """
    MA，又称移动平均线，是借助统计处理方式将若干天的股票价格加以平均，然后连接成一条线，用以观察股价趋势。
    移动平均线通常有3日、6日、10日、12日、24日、30日、72日、200日、288日、13周、26周、52周等等，不一而足，
    其目的在取得某一段期间的平均成本，而以此平均成本的移动曲线配合每日收盘价的线路变化分析某一期间多空的优劣形势，
    以研判股价的可能变化。
    一般来说，现行价格在平均价之上，意味着市场买力（需求）较大，行情看好；
    反之，行情价在平均价之下，则意味着供过于求，卖压显然较重，行情看淡。    
    """
    #if ('MA' in graph) or ('ALL' in graph):
    if (graph in ['MA',['MA']]) or ('ALL' in graph):    
        MA_cols=[]
        for mad in MA_days:
            col='MA'+str(mad)+text_lang('简单移动均线',' Simple MA Line')
            MA_cols=MA_cols+[col]
            df[col] = talib.MA(df['Close'],timeperiod=mad)
        
        # MA快慢线交叉
        dft=df.copy()
        dft['datepd']=dft.index
        dft['日期']=dft['datepd'].apply(lambda x: x.strftime("%Y-%m-%d"))
        
        dft['short-long']=dft[MA_cols[0]]-dft[MA_cols[1]]
        dft['sign']=dft['short-long'].apply(lambda x: 1 if x>0 else -1)
        dft['sign_cross']=dft['sign']-dft['sign'].shift(1)
        dft['交叉类型']=dft['sign_cross'].apply(lambda x: '上穿' if x > 0 else '下穿' if x < 0 else '')
        dft2=dft[dft['sign_cross'] != 0]
        dft3=dft2[(dft2.index >= startpd) & (dft2.index <= endpd)] 
        dft3.dropna(inplace=True)
            
        # 限定日期范围
        df1=df[(df.index >= startpd) & (df.index <= endpd)]    
    
        y_label=text_lang("价格","Price")
        import datetime as dt; today=dt.date.today()    
        source=text_lang("数据来源：Sina/Yahoo/Stooq，","Data source: Sina/Yahoo/Stooq, ")+str(today)
        footnote=text_lang("MA参数：","MA days=")+str(MA_days)
        x_label=footnote+'\n'+source
        
        axhline_value=0
        axhline_label=''
    
        # 简单移动均线MA绘图：moving average
        df2=df1[['Close']+MA_cols]
        df2.rename(columns={'Close':text_lang('收盘价','Close')},inplace=True)
        
        title_txt=text_lang("证券技术分析：","Technical Analysis: ")+ticker_name(ticker,ticker_type)+text_lang("，简单移动均线",", Simple MA Line")
        
        print("  Rendering graphics ...")
        draw_lines(df2,y_label,x_label,axhline_value,axhline_label,title_txt, \
                   data_label=False,resample_freq=resample_freq,smooth=smooth, \
                       linewidth=linewidth*2,facecolor=facecolor,bold_column=text_lang('收盘价','Close'))        
    
        if printout:
            if len(dft3)!=0:            
                print(text_lang("\n== 简单移动均线交叉 ==","\n== Simple MA Line =="))
                alignlist=['left','center']
                print(dft3[['日期','交叉类型']].to_markdown(index=False,tablefmt='plain',colalign=alignlist))
            else:
                print("  Note: no cross of lines incurred for",ticker,"from",start,"to",end)

    # 指数移动均线EMA绘图：exponential moving average
    """
    MA是用每天的收盘价来计算简单的平均值，
    而EMA是需要给每天的最高最低等价位数值做一个权重处理后，再平均计算，
    所以，EMA更具有平均价值一些。
    EMA最大特点也是由于它的计算方式导致的，因为后期的k线价格在计算均价时，比重更大，
    所以相同参数EMA比MA更加贴近行情，更加平滑，产生的变盘信号、交易信号也更加激进？
    EMA的变盘信号：熊市转牛市，比MA迟钝？牛市转熊市，比MA敏感？    
    """
    if ('EMA' in graph) or ('ALL' in graph):
        EMA_cols=[]
        for mad in EMA_days:
            col='EMA'+str(mad)+text_lang('指数移动均线',' Exponential MA Line')
            EMA_cols=EMA_cols+[col]
            df[col] = talib.EMA(df['Close'],timeperiod=mad)
        
        # EMA快慢线交叉
        dft=df.copy()
        dft['datepd']=dft.index
        dft['日期']=dft['datepd'].apply(lambda x: x.strftime("%Y-%m-%d"))
        
        dft['short-long']=dft[EMA_cols[0]]-dft[EMA_cols[1]]
        dft['sign']=dft['short-long'].apply(lambda x: 1 if x>0 else -1)
        dft['sign_cross']=dft['sign']-dft['sign'].shift(1)
        dft['交叉类型']=dft['sign_cross'].apply(lambda x: '上穿' if x > 0 else '下穿' if x < 0 else '')
        dft2=dft[dft['sign_cross'] != 0]
        dft3=dft2[(dft2.index >= startpd) & (dft2.index <= endpd)] 
        dft3.dropna(inplace=True)
            
        # 限定日期范围
        df1=df[(df.index >= startpd) & (df.index <= endpd)]    
    
        y_label=text_lang("价格","Price")
        import datetime as dt; today=dt.date.today()    
        source=text_lang("数据来源：Sina/Yahoo/Stooq，","Data source: Sina/Yahoo/Stooq, ")+str(today)
        footnote=text_lang("EMA参数：","EMA days=")+str(EMA_days)
        x_label=footnote+'\n'+source
        
        axhline_value=0
        axhline_label=''
        
        df3=df1[['Close']+EMA_cols]
        df3.rename(columns={'Close':text_lang('收盘价','Close')},inplace=True)
        title_txt=text_lang("证券技术分析：","Technical Analysis: ")+ticker_name(ticker,ticker_type)+text_lang("，指数移动平均线","Exponential MA Line")
        draw_lines(df3,y_label,x_label,axhline_value,axhline_label,title_txt, \
                   data_label=False,resample_freq=resample_freq,smooth=smooth, \
                       linewidth=linewidth*2,facecolor=facecolor,bold_column=text_lang('收盘价','Close'))        

        if printout:
            if len(dft3)!=0:            
                print(text_lang("\n== 指数移动平均线交叉 ==","\n== Exponential MA Line Cross =="))
                alignlist=['left','center']
                print(dft3[['日期','交叉类型']].to_markdown(index=False,tablefmt='plain',colalign=alignlist))
            else:
                print("  Note: no cross of lines incurred for",ticker,"from",start,"to",end)
        
    #=========== MACD：指数平滑异同平均线
    """
    计算方法：快速时间窗口设为12日，慢速时间窗口设为26日，DIF参数设为9日
        3.1) 计算指数平滑移动平均值（EMA）
        12日EMA的计算公式为：
        EMA(12) = 昨日EMA(12)  ×  11 ÷ 13 + 今日收盘价 × 2 ÷ 13
        26日EMA的计算公式为：
        EMA(26) = 昨日EMA(26) × 25 ÷ 27 + 今日收盘价 × 2 ÷ 27
        
        3.2) 计算离差值（DIF）
        DIF = 今日EMA(12) – 今日EMA(26)
        
        3.3) 计算DIF的9日DEA
        根据差值计算其9日的DEA，即差值平均
        今日DEA = 昨日DEA × 8 ÷ 10 + 今日DIF × 2 ÷ 10    
    
    形态解读：
        1.DIF、DEA均为正，DIF向上突破DEA，买入信号。
        2.DIF、DEA均为负，DIF向下跌破DEA，卖出信号。
        3.DEA线与K线发生背离，行情反转信号。
        4.分析MACD柱状线，由红变绿(正变负)，卖出信号；由绿变红，买入信号。
        
    MACD一则去掉移动平均线频繁的假讯号缺陷，二则能确保移动平均线最大的战果。
        1. MACD金叉：DIF由下向上突破DEM，为买入信号。
        2. MACD死叉：DIF由上向下突破DEM，为卖出信号。
        3. MACD绿转红：MACD值由负变正，市场由空头转为多头。
        4. MACD红转绿：MACD值由正变负，市场由多头转为空头。        
    """
    if ('MACD' in graph) or ('ALL' in graph):
        df['DIF'],df['DEA'],df['MACD']=talib.MACD(df['Close'], \
                                    fastperiod=MACD_fastperiod, \
                                    slowperiod=MACD_slowperiod, \
                                    signalperiod=MACD_signalperiod)
        
        # DIF/DEA快慢线交叉
        dft=df.copy()
        dft['datepd']=dft.index
        dft['日期']=dft['datepd'].apply(lambda x: x.strftime("%Y-%m-%d"))
        
        dft['short-long']=dft['DIF']-dft['DEA']
        dft['sign']=dft['short-long'].apply(lambda x: 1 if x>0 else -1)
        dft['sign_cross']=dft['sign']-dft['sign'].shift(1)
        dft['交叉类型']=dft['sign_cross'].apply(lambda x: '上穿' if x > 0 else '下穿' if x < 0 else '')
        dft2=dft[dft['sign_cross'] != 0]
        dft3=dft2[(dft2.index >= startpd) & (dft2.index <= endpd)] 
        dft3.dropna(inplace=True)
            
        # 限定日期范围
        df1=df[(df.index >= startpd) & (df.index <= endpd)]    
        
        # MACD绘图
        print('') #空一行
        
        df4=df1[['Close','DIF','DEA','MACD']]
        df4.rename(columns={'Close':'收盘价','DIF':'快线DIF','DEA':'慢线DEA','MACD':'柱线MACD'},inplace=True)
        title_txt=text_lang("证券技术分析：","Technical Analysis: ")+ticker_name(ticker,ticker_type)+"，MACD"
        
        import datetime as dt; today=dt.date.today()    
        source=text_lang("数据来源：Sina/Yahoo/Stooq，","Data source: Sina/Yahoo/Stooq, ")+str(today)
        
        #设置绘图风格：关闭网格虚线
        plt.rcParams['axes.grid']=False
        
        # 设置绘图区的背景颜色为黑色
        fig=plt.figure()
        ax=fig.add_subplot(111)
        #ax.patch.set_facecolor('black')
        ax.patch.set_facecolor(color=facecolor)
        
        # 绘制曲线
        ax.plot(df4['快线DIF'],label=text_lang('快线DIF','DIF(Fast line)'),linewidth=linewidth,color='orange',ls='--')
        ax.plot(df4['慢线DEA'],label=text_lang('慢线DEA','DEA(Slow line)'),linewidth=linewidth,color='green',ls='-.')
        
        # 绘制红绿柱子
        """
        MACD指标由三部分组成，分别是：DIF (差离值)、 DEA (差离值平均数)和BAR(柱状线)，
        DIF在图中用白线表示，称为“快线”，DEA在图中用黄线表示，称为“慢线”，
        最早的MACD只有这两条快慢线，通过两条曲线的聚合和分离来判断市场状况。
        后来随着MACD的广泛运用，又引入了柱状线(BAR)，俗称“红绿柱”。
        红绿柱表示的是快线与慢线之间的距离，对指标实质没有影响，只是为了更便于观察和使用指标。    
        """
        macd_plus=df4[df4['柱线MACD']>=0]
        macd_minus=df4[df4['柱线MACD']<=0]
        ax.bar(macd_plus.index,macd_plus['柱线MACD'],color='red',alpha=0.5)
        ax.bar(macd_minus.index,macd_minus['柱线MACD'],color='green',label=text_lang('柱线MACD','MACD(Bar chart)'),alpha=0.5)
        
        # 绘制水平辅助线
        #plt.axhline(y=0,label='指标零线',color='cyan',linestyle=':',linewidth=linewidth*2) 
        plt.axhline(y=0,label='',color='cyan',linestyle=':',linewidth=linewidth*2) 
        
        # 设置左侧坐标轴
        ax.set_ylabel(text_lang('DIF/DEA/MACD指标','DIF/DEA/MACD'),fontsize=ylabel_txt_size)
        
        footnote="MACD days="+str([MACD_fastperiod,MACD_slowperiod,MACD_signalperiod])
        x_label=footnote+'\n'+source
        ax.set_xlabel(x_label,fontsize=xlabel_txt_size)
        ax.legend(loc=loc1,fontsize=legend_txt_size)
        
        # 绘制股价在右侧
        #绘证券2：建立第二y轴
        
        #插值平滑
        if smooth:
            try:
                df5=df_smooth_manual(df4,resample_freq=resample_freq)
            except:
                df5=df4
        else:
            df5=df4
        
        ax2 = ax.twinx()
        ax2.plot(df5['收盘价'],label=text_lang('收盘价','Close'),linewidth=linewidth*2,color=price_line_color,ls='-')
        
        # 右侧坐标轴标记
        ax2.set_ylabel(text_lang('收盘价','Close'),fontsize=ylabel_txt_size)
        ax2.legend(loc=loc2,fontsize=legend_txt_size)
        
        # 图示标题
        plt.title(title_txt,fontweight='bold',fontsize=title_txt_size)
        #plt.xticks(rotation=30)
        plt.gcf().autofmt_xdate() # 优化标注（自动倾斜）
        #plt.legend(loc='best',fontsize=legend_txt_size)
        plt.show()

        if printout:
            if len(dft3)!=0:
                print(text_lang("\n== DIF与DEA交叉 ==","\n== Cross of DIF and DEA"))
                alignlist=['left','center']
                print(dft3[['日期','交叉类型']].to_markdown(index=False,tablefmt='plain',colalign=alignlist))
            else:
                print("  Note: no cross of lines incurred for",ticker,"from",start,"to",end)
    
    return df1

#==============================================================================
#==============================================================================
#==============================================================================
if __name__ =="__main__":
    talib_install_method()

 
def is_64bit_os():
    import platform
    if platform.machine().endswith('64'):
        bits='64'
    else:
        bits='32'
        
    return bits+'-bit'

def talib_install_method():
    """
    功能：提示必需的talib安装方法
    """
    print("  Warning: the classical method may not work properly:")
    print("    pip install TA-Lib\n")
    print("  Installation method: for Windows")
    print("    Step1. Check your Python version and your OS")
    print("      Your Python version:",check_python_version(),"\b, your OS:",is_64bit_os(),check_os())
    
    print("    Step2. Search TA_lib whl file for your OS and Python version")
    print("      e.g. Find the one free of charge from github, ... ...\n")
    print("    Step3. Download the file to a local folder in your computer")
    print("    Step4. Directly install the .whl file from the local folder by:")
    print("      pip install ta_lib_whl_file_name")

    print("\n  Installation method: for Mac")
    print("    Step1. brew install ta-lib")
    print("    Step2. pip install ta-lib")
    
    print("\n  Important: after installing ta-lib, RESTART your Jupyter.")
    
    return
#==============================================================================

if __name__ =="__main__":
    ticker='600519.SS'
    start='2022-1-1'
    end='2022-12-31'
    
    RSI_days=[6,12,24]
    RSI_lines=[20,50,80]
    
    loc1='upper left'
    loc2='center right'
    
    resample_freq='H'
    smooth=True
    linewidth=1.5
    graph=['ALL']
    printout=True

def security_RSI(ticker,start='default',end='default', \
             RSI_days=[6,14,24],RSI_lines=[30,50,70], \
             resample_freq='6H',smooth=True,linewidth=1.5, \
             loc1='lower left',loc2='lower right', \
             graph=['ALL'],printout=True,ticker_type='auto',source='auto', \
             price_line_color='red',facecolor='k'):
    """
    套壳函数，除了股票，还可用于交易所债券和交易所基金（如ETF和REITS）
    """
    df=stock_RSI(ticker=ticker,start=start,end=end, \
                 RSI_days=RSI_days,RSI_lines=RSI_lines, \
                 resample_freq=resample_freq,smooth=smooth,linewidth=linewidth, \
                 loc1=loc1,loc2=loc2, \
                 graph=graph,printout=printout,ticker_type=ticker_type,source=source, \
                 price_line_color=price_line_color,facecolor=facecolor)
    return df

    
def stock_RSI(ticker,start='default',end='default', \
             RSI_days=[6,14,24],RSI_lines=[30,50,70], \
             resample_freq='H',smooth=True,linewidth=1.5, \
             loc1='lower left',loc2='lower right', \
             graph=['ALL'],printout=True,ticker_type='auto',source='auto', \
             price_line_color='blue',facecolor='white'):
    """
    功能：计算股票的技术分析指标RSI
    输入：df，四种股价Open/Close/High/Low，成交量Volume
    输出：df
    含有指标：
    RSI1(快速线，周线，黄色)、RSI2(中速线，双周线，紫色)、RSI3(慢速线，月线，白色)
    """
    
    #=========== 导入需要的包
    try:
        import talib  
    except:
        print("  #Error(stock_RSI): lack of necessary module - ta-lib")
        talib_install_method()
        return None
    
    #=========== 日期转换与检查
    # 检查日期：截至日期
    import datetime as dt; today=dt.date.today()
    if end in ['default','today']:
        end=today
    else:
        validdate,end=check_date2(end)
        if not validdate:
            print("  #Warning(stock_RSI): invalid date for",end)
            end=today

    # 检查日期：开始日期
    if start in ['default']:
        start=date_adjust(end,adjust=-31)
    else:
        validdate,start=check_date2(start)
        if not validdate:
            print("  #Warning(stock_RSI): invalid date for",start)
            start=date_adjust(todate,adjust=-31)
    
    #=========== 获取股价和成交量数据
    result,startpd,endpd=check_period(start,end)
    
    days_list=RSI_days
    max_days=max(days_list)
    start1=date_adjust(start,adjust=-max_days * 3)
    
    #df=get_price(ticker,start1,end)
    df,found=get_price_1ticker_mixed(ticker=ticker,fromdate=start1,todate=end,ticker_type=ticker_type,source=source)
    if df is None:
        print("  #Error(stock_RSI): no info found for",ticker,"from",start,"to",end)
        return None
    if len(df)==0:
        print("  #Error(stock_RSI): zero record found for",ticker,"from",start,"to",end)
        return None   
    
    #============ 计算RSI 
    if len(RSI_days) < 3:
        print("  #Warning(stock_RSI): RSI_days parameter needs 3 different days")
        return None
        
    #df['rsi'] = talib.RSI(df['Close'], timeperiod=RSI_days)
    RSI_cols=[]
    RSI_seq=1
    for mad in RSI_days:
        col='RSI'+str(RSI_seq)
        RSI_cols=RSI_cols+[col]
        df[col] = talib.RSI(df['Close'],timeperiod=mad)
        RSI_seq=RSI_seq+1
    
    df['datepd']=df.index
    df['日期']=df['datepd'].apply(lambda x: x.strftime("%Y-%m-%d"))
    del df['datepd']
    
    # RSI1/RSI3快慢线交叉
    dft1=df.copy()
    dft1['short-long']=dft1['RSI1']-dft1['RSI3']
    dft1['sign']=dft1['short-long'].apply(lambda x: 1 if x>0 else -1)
    dft1['sign_cross']=dft1['sign']-dft1['sign'].shift(1)
    dft1['RSI1/3交叉类型']=dft1['sign_cross'].apply(lambda x: '上穿' if x > 0 else '下穿' if x < 0 else '')
    dft1b=dft1[dft1['sign_cross'] != 0]
    dft1c=dft1b[(dft1b.index >= startpd) & (dft1b.index <= endpd)] 
    dft1c.dropna(inplace=True)
    
    # RSI2/RSI3快慢线交叉
    dft2=df.copy()
    dft2['short-long']=dft2['RSI2']-dft2['RSI3']
    dft2['sign']=dft2['short-long'].apply(lambda x: 1 if x>0 else -1)
    dft2['sign_cross']=dft2['sign']-dft2['sign'].shift(1)
    dft2['RSI2/3交叉类型']=dft2['sign_cross'].apply(lambda x: '上穿' if x > 0 else '下穿' if x < 0 else '')
    dft2b=dft2[dft2['sign_cross'] != 0]
    dft2c=dft2b[(dft2b.index >= startpd) & (dft2b.index <= endpd)] 
    dft2c.dropna(inplace=True)
        
    # RSI限定日期范围
    df1=df[(df.index >= startpd) & (df.index <= endpd)]    

    if len(graph) != 0:
        
        # RSI绘图
        df4=df1[['Close']+RSI_cols]
        df4.rename(columns={'Close':'收盘价'},inplace=True)
        title_txt=text_lang("证券技术分析：","Technical Analysis: ")+ticker_name(ticker,ticker_type)+text_lang("，RSI",", RSI")
        
        import datetime as dt; today=dt.date.today()    
        source=text_lang("数据来源：Sina/Yahoo/Stooq，","Data source: Sina/Yahoo/Stooq, ")+str(today)
        footnote=text_lang("RSI参数：","RSI days=")+str(RSI_days)
        x_label=footnote+'\n'+source
        
        # 设置绘图区的背景颜色为黑色
        fig=plt.figure()
        ax=fig.add_subplot(111)
        ax.patch.set_facecolor(color=facecolor)
        
        # 绘制曲线
        if ('RSI1' in graph) or ('ALL' in graph):
            ax.plot(df4['RSI1'],label=text_lang('快速线RSI1','RSI1(Fast line)'),linewidth=linewidth,color='orange',ls='--')
        if ('RSI2' in graph) or ('ALL' in graph):
            ax.plot(df4['RSI2'],label=text_lang('中速线RSI2','RSI2(Mid line)'),linewidth=linewidth,color='purple',ls='-.')
        if ('RSI3' in graph) or ('ALL' in graph):
            ax.plot(df4['RSI3'],label=text_lang('慢速线RSI3','RSI3(Slow line)'),linewidth=linewidth,color='gray',ls=':')
        
        # 绘制水平辅助线
        #hl_linestyle_list=['dashed','-.','dotted']
        hl_linestyle_list=['dotted','dotted','dotted','dotted','dotted','dotted']
        #plt.axhline(y=0,label='指标零线',color='cyan',linestyle=':',linewidth=linewidth*2) 
        for hl in RSI_lines:
            pos=RSI_lines.index(hl)
            hl_ls=hl_linestyle_list[pos]
            plt.axhline(y=hl,label='',color='cyan',linestyle=hl_ls,linewidth=linewidth) 
        
        # 设置左侧坐标轴
        ax.set_ylabel(text_lang('RSI指标','RSI'),fontsize=ylabel_txt_size)
        ax.set_xlabel(x_label,fontsize=xlabel_txt_size)
        ax.legend(loc=loc1,fontsize=legend_txt_size)
        
        # 绘制股价在右侧
        #绘证券2：建立第二y轴
        
        #插值平滑
        if smooth:
            print("  Smoothening curves directly ...")
            try:
                df5=df_smooth_manual(df4,resample_freq=resample_freq)
            except:
                df5=df4
        else:
            df5=df4
        
        ax2 = ax.twinx()
        ax2.plot(df5['收盘价'],label=text_lang('收盘价','Close'),linewidth=linewidth*2, \
                 color=price_line_color,ls='-',alpha=0.5)
        
        # 右侧坐标轴标记
        ax2.set_ylabel(text_lang('收盘价','Close'),fontsize=ylabel_txt_size)
        ax2.legend(loc=loc2,fontsize=legend_txt_size)
        
        # 图示标题
        plt.title(title_txt,fontweight='bold',fontsize=title_txt_size)
        #plt.xticks(rotation=30)
        plt.gcf().autofmt_xdate() # 优化标注（自动倾斜）
        #plt.legend(loc='best',fontsize=legend_txt_size)
        plt.show()

        if printout:
            if (('RSI1' in graph) & ('RSI3' in graph)) or ('ALL' in graph):
                if len(dft1c)!=0:
                    print(text_lang("\n=== RSI1与RSI3的交叉点 ===","\n=== Cross of RSI1 & RSI3"))
                    alignlist=['left','center']
                    print(dft1c[['日期','RSI1/3交叉类型']].to_markdown(index=False,tablefmt='plain',colalign=alignlist))
                else:
                    print("  Note: no RSI1/3 cross of lines incurred for",ticker,"from",start,"to",end)
        
            if (('RSI2' in graph) & ('RSI3' in graph)) or ('ALL' in graph):
                if len(dft2c)!=0:
                    print(text_lang("\n=== RSI2与RSI3的交叉点 ===","\n=== Cross of RSI2 & RSI3"))
                    alignlist=['left','center']
                    print(dft2c[['日期','RSI2/3交叉类型']].to_markdown(index=False,tablefmt='plain',colalign=alignlist))
                else:
                    print("  Note: no RSI2/3 cross of lines incurred for",ticker,"from",start,"to",end)
                    
            if 'RSI1' in graph:
                df1_rsi1=df1[['日期','RSI1','Close']][(df1['RSI1'] < RSI_lines[0]) | (df1['RSI1'] > RSI_lines[2])]
                df1_rsi1['标记']=df1_rsi1['RSI1'].apply(
                    lambda x: 'Oversold' if x < RSI_lines[0]
                              else 'Overbought' if x > RSI_lines[2] else '')
                
                if len(df1_rsi1) != 0:
                    print(text_lang("\n=== RSI1(快速线)：超买超卖区域 ===","\n=== RSI1: Overbought/Oversold"))
                    alignlist=['center','center','center','center']
                    print(df1_rsi1.to_markdown(index=False,tablefmt='plain',colalign=alignlist))
                else:
                    print("  Note: no RSI1 overbought / oversold area found for",ticker,"from",start,"to",end)
                    
            if 'RSI2' in graph:
                df1_rsi2=df1[['日期','RSI2','Close']][(df1['RSI2'] < RSI_lines[0]) | (df1['RSI2'] > RSI_lines[2])]
                df1_rsi2['标记']=df1_rsi2['RSI2'].apply(
                    lambda x: 'Oversold' if x < RSI_lines[0]
                              else 'Overbought' if x > RSI_lines[2] else '')
                
                if len(df1_rsi2) != 0:
                    print(text_lang("\n=== RSI2(中速线)：超买超卖区域 ===","\n=== RSI2: Overbought/Oversold"))
                    alignlist=['center','center','center','center']
                    print(df1_rsi2.to_markdown(index=False,tablefmt='plain',colalign=alignlist))
                else:
                    print("  Note: no RSI2 overbought / oversold area found for",ticker,"from",start,"to",end)
                    
            if 'RSI3' in graph:
                df1_rsi3=df1[['日期','RSI3','Close']][(df1['RSI3'] < RSI_lines[0]) | (df1['RSI3'] > RSI_lines[2])]
                df1_rsi3['标记']=df1_rsi3['RSI3'].apply(
                    lambda x: 'Oversold' if x < RSI_lines[0]
                              else 'Overbought' if x > RSI_lines[2] else '')
                
                if len(df1_rsi3) != 0:
                    print(text_lang("\n=== RSI3(慢速线)：超买超卖区域 ===","\n=== RSI3: Overbought/Oversold"))
                    alignlist=['center','center','center','center']
                    print(df1_rsi3.to_markdown(index=False,tablefmt='plain',colalign=alignlist))
                else:
                    print("  Note: no RSI3 overbought / oversold area found for",ticker,"from",start,"to",end)
    
    return df1       
#==============================================================================
#==============================================================================
#==============================================================================

def findout_cross(df,start,end,fast_line,slow_line):
    """
    功能：技术分析，找出fast_line与slow_line两条线交叉的记录，并给出交叉类型：上穿，下穿
    """
    
    dft1=df.copy()
    dft1['short-long']=dft1[fast_line]-dft1[slow_line]
    dft1['sign']=dft1['short-long'].apply(lambda x: 1 if x>0 else -1)
    dft1['sign_cross']=dft1['sign']-dft1['sign'].shift(1)
    dft1['交叉类型']=dft1['sign_cross'].apply(lambda x: '上穿' if x > 0 else '下穿' if x < 0 else '')
    dft1b=dft1[dft1['sign_cross'] != 0]
    
    result,startpd,endpd=check_period(start,end)
    dft1c=dft1b[(dft1b.index >= startpd) & (dft1b.index <= endpd)] 
    
    dft1c.dropna(inplace=True)
    
    return dft1c

#==============================================================================
#==============================================================================
#==============================================================================


if __name__ =="__main__":
    ticker='600519.SS'
    start='2010-1-1'
    end='2022-12-31'
    
    KDJ_days=[9,3,3]
    matypes=[0,0]
    
    loc1='upper left'
    loc2='center right'
    
    resample_freq='H'
    smooth=True
    linewidth=1.5
    
    graph=['ALL']
    printout=True
    
    graph=False

def security_KDJ(ticker,start='default',end='default', \
             KDJ_days=[9,3,3],matypes=[0,0],KDJ_lines=[20,50,80], \
             resample_freq='6H',smooth=True,linewidth=1.5, \
             loc1='lower left',loc2='lower right', \
             graph=['ALL'],printout=True,ticker_type='auto',source='auto', \
             price_line_color='blue',facecolor='white'):
    """
    套壳函数
    """
    df=stock_KDJ(ticker=ticker,start=start,end=end, \
                 KDJ_days=KDJ_days,matypes=matypes,KDJ_lines=KDJ_lines, \
                 resample_freq=resample_freq,smooth=smooth,linewidth=linewidth, \
                 loc1=loc1,loc2=loc2, \
                 graph=graph,printout=printout,ticker_type=ticker_type,source=source, \
                 price_line_color=price_line_color,facecolor=facecolor)
    return df

    
def stock_KDJ(ticker,start='default',end='default', \
             KDJ_days=[9,3,3],matypes=[0,0],KDJ_lines=[20,50,80], \
             resample_freq='H',smooth=True,linewidth=1.5, \
             loc1='lower left',loc2='lower right', \
             graph=['ALL'],printout=True,ticker_type='auto',source='auto', \
             price_line_color='blue',facecolor='white'):
    """
    功能：计算股票的技术分析指标KDJ
    输入：df，四种股价Open/Close/High/Low，成交量Volume
    输出：df
    含有指标：
    K线(快速线，黄色)、D线(慢速线，绿色)、J线(差额，紫色)
    """
    
    #=========== 导入需要的包
    try:
        import talib  
    except:
        print("  #Error(stock_KDJ): lack of necessary module - talib")
        talib_install_method()
        return None

    if graph=="ALL":
        graph=['K','D','J']
    
    #=========== 日期转换与检查
    # 检查日期：截至日期
    import datetime as dt; today=dt.date.today()
    if end in ['default','today']:
        end=today
    else:
        validdate,end=check_date2(end)
        if not validdate:
            print("  #Warning(stock_KDJ): invalid date for",end)
            end=today

    # 检查日期：开始日期
    if start in ['default']:
        start=date_adjust(end,adjust=-31)
    else:
        validdate,start=check_date2(start)
        if not validdate:
            print("  #Warning(stock_KDJ): invalid date for",start)
            start=date_adjust(todate,adjust=-31)
    
    #=========== 获取股价和成交量数据
    result,startpd,endpd=check_period(start,end)
    
    days_list=KDJ_days
    max_days=max(days_list)
    start1=date_adjust(start,adjust=-max_days * 3)
    
    #df=get_price(ticker,start1,end)
    df,found=get_price_1ticker_mixed(ticker=ticker,fromdate=start1,todate=end,ticker_type=ticker_type,source=source)
    if df is None:
        print("  #Error(stock_RSI): no info found for",ticker,"from",start,"to",end)
        return None
    if len(df)==0:
        print("  #Error(stock_RSI): zero record found for",ticker,"from",start,"to",end)
        return None   
    
    df['datepd']=df.index
    df['日期']=df['datepd'].apply(lambda x: x.strftime("%Y-%m-%d"))
    del df['datepd']
    
    #============ 计算KDJ
    """
    df['kdj_k'],df['kdj_d'] = talib.STOCH(df['High'],df['Low'],df['Close'], \
                        fastk_period=KDJ_fastk_period,
                        slowk_period=KDJ_slowk_period, 
                        slowk_matype=KDJ_slowk_matype, 
                        slowd_period=KDJ_slowd_period, 
                        slowd_matype=KDJ_slowd_matype)
    df['kdj_j'] = 3*df['kdj_k'] - 2*df['kdj_d']    
    """
    KDJ_cols=['K','D','J']
    df['K'],df['D'] = talib.STOCH(df['High'],df['Low'],df['Close'], \
                        fastk_period=KDJ_days[0],
                        slowk_period=KDJ_days[1], 
                        slowk_matype=matypes[0], 
                        slowd_period=KDJ_days[2], 
                        slowd_matype=matypes[1])
    df['J'] = 3*df['K'] - 2*df['D']    
    
    # 限制J线在0-100之间
    if graph:
        df['J']=df['J'].apply(lambda x:100 if x>100 else 0 if x<0 else x)
    
    if not graph:
        return df
    
    # J/K线交叉
    """
    dft1=df.copy()
    dft1['short-long']=dft1['J']-dft1['K']
    dft1['sign']=dft1['short-long'].apply(lambda x: 1 if x>0 else -1)
    dft1['sign_cross']=dft1['sign']-dft1['sign'].shift(1)
    dft1['J/K线交叉类型']=dft1['sign_cross'].apply(lambda x: '上穿' if x > 0 else '下穿' if x < 0 else '')
    dft1b=dft1[dft1['sign_cross'] != 0]
    dft1c=dft1b[(dft1b.index >= startpd) & (dft1b.index <= endpd)] 
    dft1c.dropna(inplace=True)
    """
    dft1c=findout_cross(df,start,end,'J','K')
    
    # J/D线交叉
    """
    dft2=df.copy()
    dft2['short-long']=dft2['J']-dft2['D']
    dft2['sign']=dft2['short-long'].apply(lambda x: 1 if x>0 else -1)
    dft2['sign_cross']=dft2['sign']-dft2['sign'].shift(1)
    dft2['J/D线交叉类型']=dft2['sign_cross'].apply(lambda x: '上穿' if x > 0 else '下穿' if x < 0 else '')
    dft2b=dft2[dft2['sign_cross'] != 0]
    dft2c=dft2b[(dft2b.index >= startpd) & (dft2b.index <= endpd)] 
    dft2c.dropna(inplace=True)
    """
    dft2c=findout_cross(df,start,end,'J','D')
    
    # K/D线交叉
    dft3c=findout_cross(df,start,end,'K','D')
        
    # 限定日期范围
    df1=df[(df.index >= startpd) & (df.index <= endpd)]    

    if len(graph) != 0:
        
        # 绘图
        df4=df1[['Close']+KDJ_cols]
        df4.rename(columns={'Close':'收盘价'},inplace=True)
        title_txt=text_lang("证券技术分析：","Technical Analysis: ")+ticker_name(ticker,ticker_type)+text_lang("，KDJ",", KDJ")
        
        import datetime as dt; today=dt.date.today()    
        source=text_lang("数据来源：Sina/Yahoo/Stooq，","Data source: Sina/Yahoo/Stooq, ")+str(today)
        footnote=text_lang("KDJ参数：","KDJ days=")+str(KDJ_days)
        x_label=footnote+'\n'+source
        
        # 设置绘图区的背景颜色为黑色
        fig=plt.figure()
        ax=fig.add_subplot(111)
        ax.patch.set_facecolor(color=facecolor)
        
        # 绘制曲线
        if ('K' in graph) or ('ALL' in graph):
            ax.plot(df4['K'],label=text_lang('快速线K','K(Fast line)'),linewidth=linewidth,color='orange',ls='--')
        if ('D' in graph) or ('ALL' in graph):
            ax.plot(df4['D'],label=text_lang('慢速线D','D(Slow line)'),linewidth=linewidth,color='green',ls='-.')
        if ('J' in graph) or ('ALL' in graph):
            ax.plot(df4['J'],label=text_lang('超快线J','J(Faster line)'),linewidth=linewidth,color='purple',ls=':')
        
        # 绘制水平辅助线: 某些情况下不绘制，以便展现KDJ线细节
        maxK=df4['K'].max()
        maxD=df4['D'].max()
        maxJ=df4['J'].max()
        maxKDJ=max(maxK,maxD,maxJ)

        minK=df4['K'].min()
        minD=df4['D'].min()
        minJ=df4['J'].min()
        minKDJ=min(minK,minD,minJ)
        
        """
        hl_linestyle_list=['dashed','dashed','-.','dotted','dotted']
        hl_color_list=['red','red','white','cyan','cyan']
        """
        hl_linestyle_list=['dotted','dotted','dotted','dotted','dotted']
        hl_color_list=['cyan','cyan','cyan','cyan','cyan']
        
        #plt.axhline(y=0,label='指标零线',color='cyan',linestyle=':',linewidth=linewidth*2) 
        for hl in KDJ_lines:
            draw=True
            if (hl > maxKDJ):
                draw=False
            if (hl < minKDJ):
                draw=False
            
            if draw:
                pos=KDJ_lines.index(hl)
                hl_ls=hl_linestyle_list[pos]
                hl_color=hl_color_list[pos]
                plt.axhline(y=hl,label='',color=hl_color,linestyle=hl_ls,linewidth=linewidth) 
        
        # 设置左侧坐标轴
        ax.set_ylabel(text_lang('KDJ指标','KDJ'),fontsize=ylabel_txt_size)
        ax.set_xlabel(x_label,fontsize=xlabel_txt_size)
        ax.legend(loc=loc1,fontsize=legend_txt_size)
        
        # 设置纵轴刻度
        from matplotlib.pyplot import MultipleLocator
        y_major_locator=MultipleLocator(10)
        ax.yaxis.set_major_locator(y_major_locator)
        #ax.set_ylim(-5,105)
        
        # 绘制股价在右侧
        #绘证券2：建立第二y轴
        
        #插值平滑
        if smooth:
            print("  Smoothening curves directly ...")
            try:
                df5=df_smooth_manual(df4,resample_freq=resample_freq)
            except:
                df5=df4
        else:
            df5=df4
        
        ax2 = ax.twinx()
        ax2.plot(df5['收盘价'],label=text_lang('收盘价','Close'),linewidth=linewidth*2, \
                 color=price_line_color,ls='-',alpha=0.5)
        
        # 右侧坐标轴标记
        ax2.set_ylabel(text_lang('收盘价','Close'),fontsize=ylabel_txt_size)
        ax2.legend(loc=loc2,fontsize=legend_txt_size)
        
        # 图示标题
        plt.title(title_txt,fontweight='bold',fontsize=title_txt_size)
        #plt.xticks(rotation=30)
        plt.gcf().autofmt_xdate() # 优化标注（自动倾斜）
        #plt.legend(loc='best',fontsize=legend_txt_size)
        plt.show()

        if printout:
            alignlist=['left','center']
            if (('J' in graph) & ('K' in graph)) or ('ALL' in graph):
                if len(dft1c)!=0:
                    print(text_lang("\n**** J线与K线的交叉点","\n**** Cross of J & K Lines"))
                    print(dft1c[['日期','交叉类型']].to_markdown(index=False,tablefmt='plain',colalign=alignlist))
                else:
                    print("  Note: no J/K cross of lines incurred for",ticker,"from",start,"to",end)
 
            if (('J' in graph) & ('D' in graph)) or ('ALL' in graph):
                if len(dft2c)!=0:
                    print(text_lang("\n**** J线与D线的交叉点","\n**** Cross of J & D Lines"))
                    alignlist=['left','center']
                    print(dft2c[['日期','交叉类型']].to_markdown(index=False,tablefmt='plain',colalign=alignlist))
                else:
                    print("  Note: no J/D cross of lines incurred for",ticker,"from",start,"to",end)
 
            if (('K' in graph) & ('D' in graph)) or ('ALL' in graph):
                if len(dft3c)!=0:
                    print(text_lang("\n**** K线与D线的交叉点","\n**** Cross of K & D Lines"))
                    alignlist=['left','center']
                    print(dft3c[['日期','交叉类型']].to_markdown(index=False,tablefmt='plain',colalign=alignlist))
                else:
                    print("  Note: no K/D cross of lines incurred for",ticker,"from",start,"to",end)
    
            # 超买超卖区域   
            if 'K' in graph:
                df1_K=df1[['日期','K','Close']][(df1['K'] < KDJ_lines[0]) | (df1['K'] > KDJ_lines[2])]
                df1_K['标记']=df1_K['K'].apply(
                    lambda x: 'Oversold' if x < KDJ_lines[0]
                              else 'Overbought' if x > KDJ_lines[2] else '')
                
                if len(df1_K) != 0:
                    print(text_lang("\n=== K线(快速线)：超买超卖区域 ===","\n=== K Line: Overbought/Oversold"))
                    alignlist=['center','center','center','center']
                    print(df1_K.to_markdown(index=False,tablefmt='plain',colalign=alignlist))
                else:
                    print("  Note: no K line overbought / oversold area found for",ticker,"from",start,"to",end)
    
            if 'D' in graph:
                df1_D=df1[['日期','D','Close']][(df1['D'] < KDJ_lines[0]) | (df1['D'] > KDJ_lines[2])]
                df1_D['标记']=df1_D['D'].apply(
                    lambda x: 'Oversold' if x < KDJ_lines[0]
                              else 'Overbought' if x > KDJ_lines[2] else '')
                
                if len(df1_D) != 0:
                    print(text_lang("\n=== D线(慢速线)：超买超卖区域 ===","\n=== D Line: Overbought/Oversold"))
                    alignlist=['center','center','center','center']
                    print(df1_D.to_markdown(index=False,tablefmt='plain',colalign=alignlist))
                else:
                    print("  Note: no D line overbought / oversold area found for",ticker,"from",start,"to",end)
    
    return df1       
#==============================================================================
#==============================================================================
#==============================================================================

if __name__ =="__main__":
    ticker='600519.SS'
    start='2020-1-1'
    end='2022-12-31'
    
    past_days=1
    momemtum_days=0
    future_days=1
    
    threshhold=0.001
    
    df=stock_KDJ(ticker,start,end,graph=False)
    
def price_trend_technical(df, \
                    past_days=1,momemtum_days=1,future_days=1, \
                    threshhold=0.001):
    """
    功能：检查技术结果中每日股价的变化趋势：上涨，下跌，振荡，转折
    past_days: 当前日期前几个交易日的算术收益率天数
    momemtum_days: 股价发生变化的惯性天数，从当前日期开始计算
    future_days: 当前日期未来几个交易日的算术收益率天数，从当前日期+惯性天数开始计算
    threshhold: 股价算术收益率变化的最低门槛，
    不小于threshhold：上涨，+；
    小于-threshhold：下跌，-；
    其余：振荡，~
    
    注意：可能存在尚不明了的问题！！！
    """  
    
    cols=list(df)
    cols.remove('Close')
    cols1=cols+['Close']
    df1=df[cols1]    
    
    df1['Close_past']=df1['Close'].shift(past_days)
    df1['ret_past']=df1['Close'] - df1['Close_past']
    
    # +=上涨，~=振荡，-=下跌
    df1['trend_past']=df1['ret_past'].apply(lambda x:'+' if x >= threshhold else 
                                            '-' if x <= -threshhold 
                                            else '~' if -threshhold < x < threshhold
                                            else '')
    if momemtum_days != 0:
        df1['Close_mom']=df1['Close'].shift(-momemtum_days)
    else:
        df1['Close_mom']=df1['Close']
        
    df1['Close_future']=df1['Close'].shift(-momemtum_days-future_days)
    df1['ret_future']=df1['Close_future'] - df1['Close_mom']
    df1['trend_future']=df1['ret_future'].apply(lambda x:'+' if x >= threshhold 
                                                else '-' if x <= -threshhold 
                                                else '~' if -threshhold < x < threshhold
                                                else '')

    df1['trend_past2future']=''
    df1['trend_past2future']=df1.apply(lambda x: 
                                       '+2+' if (x['trend_past']=='+') & (x['trend_future']=='+') 
                                       else x['trend_past2future'],axis=1)
    df1['trend_past2future']=df1.apply(lambda x: 
                                       '-2-' if (x['trend_past']=='-') & (x['trend_future']=='-') 
                                       else x['trend_past2future'],axis=1)
    df1['trend_past2future']=df1.apply(lambda x: 
                                       '~2~' if (x['trend_past']=='~') & (x['trend_future']=='~') 
                                       else x['trend_past2future'],axis=1)
    
    df1['trend_past2future']=df1.apply(lambda x: 
                                       '+2-' if (x['trend_past']=='+') & (x['trend_future']=='-') 
                                       else x['trend_past2future'],axis=1)
    df1['trend_past2future']=df1.apply(lambda x: 
                                       '+2~' if (x['trend_past']=='+') & (x['trend_future']=='~') 
                                       else x['trend_past2future'],axis=1)
        
    df1['trend_past2future']=df1.apply(lambda x: 
                                       '-2+' if (x['trend_past']=='-') & (x['trend_future']=='+') 
                                       else x['trend_past2future'],axis=1)
    df1['trend_past2future']=df1.apply(lambda x: 
                                       '-2~' if (x['trend_past']=='-') & (x['trend_future']=='~') 
                                       else x['trend_past2future'],axis=1)
        
    df1['trend_past2future']=df1.apply(lambda x: 
                                       '~2+' if (x['trend_past']=='~') & (x['trend_future']=='+') 
                                       else x['trend_past2future'],axis=1)
    df1['trend_past2future']=df1.apply(lambda x: 
                                       '~2-' if (x['trend_past']=='~') & (x['trend_future']=='-') 
                                       else x['trend_past2future'],axis=1)

    
    tempcols=['Close_past','ret_past','Close_mom','Close_future','ret_future']
    df1.drop(tempcols, axis=1, inplace=True)
    
    # 记录参数
    df1['past_days']=past_days
    df1['momemtum_days']=momemtum_days
    df1['future_days']=future_days
    df1['threshhold']=threshhold
    
    return df1
    
    
#==============================================================================
#==============================================================================

if __name__ =="__main__":
    
    ticker='600519.SS'
    start='2020-1-1'
    end='2022-12-31'
    df=stock_KDJ(ticker,start,end,graph=False)
    
    df1=price_trend_technical(df)
    KDJ_values=[20,20,10]
    J_days=3
    JvsK='above'
    JKcross='bottom up'
    value_type='ceiling'
    
    otc1,dfs1=check_KDJ_market(df1,start,end,KDJ_values=[50,50,50],value_type='floor')
    otc2,dfs2=check_KDJ_market(df1,start,end,KDJ_values=[80,80,100],J_days=3,value_type='floor')
    dfs_down=dfs2[dfs2['trend_future']=='-']
    
    otp1,dfs1=check_KDJ_market(df1,start,end,KDJ_values=[50,50,50],value_type='ceiling')
    otp2,dfs2=check_KDJ_market(df1,start,end,KDJ_values=[20,20,0],J_days=3,value_type='ceiling')
    dfs_up=dfs2[dfs2['trend_future']=='+']


def check_KDJ_market(df1,start,end,KDJ_values=[50,50,50],J_days=1,JvsK='any',JKcross='any',
                     value_type='ceiling'):
    """
    功能：检查KDJ计算结果中，多头/空头市场的股价趋势比例
    start,end：日期范围
    value_type='ceiling'：K、D、J值位于KDJ_values=[50,50,50]以下，假设为空头市场
    value_type='floor'：K、D、J值位于KDJ_values=[50,50,50]以上，假设为多头市场
    
    注意：可能存在尚不明了的问题！！！
    """
    import pandas as pd
    
    ticker=df1['ticker'].values[0]
    past_days=df1['past_days'].values[0]   
    momemtum_days=df1['momemtum_days'].values[0]   
    future_days=df1['future_days'].values[0]   
    threshhold=df1['threshhold'].values[0]   
    
    # J值的持续天数
    if J_days > 1:
        for jj in range(1,J_days):
            df1['J_'+str(jj)]=df1['J'].shift(jj)
    
    result,startpd,endpd=check_period(start,end)
    df2=df1[(df1.index >= startpd) & (df1.index <=endpd)]
    df2=df2[df2['trend_future'] != '']
    
    # 多头市场：KDJ值的下限floor；空头市场：KDJ值的上限ceiling
    if value_type == 'floor':
        df3=df2[(df2['K'] > KDJ_values[0]) & 
                (df2['D'] > KDJ_values[1]) & 
                (df2['J'] > KDJ_values[2])]
        if J_days > 1:
            for jj in range(1,J_days):
                #print('jj=',jj)
                df3=df3[df3['J_'+str(jj)] > KDJ_values[2]]
    elif value_type == 'ceiling':
        df3=df2[(df2['K'] < KDJ_values[0]) & 
                (df2['D'] < KDJ_values[1]) & 
                (df2['J'] < KDJ_values[2])]
        if J_days > 1:
            for jj in range(1,J_days):
                #print('jj=',jj)
                df3=df3[df3['J_'+str(jj)] < KDJ_values[2]]
    else:
        pass
    
    # J/K线上下位置
    if JvsK=='above':
        df3=df3[df3['J'] > df3['K']]
    elif JvsK=='below':
        df3=df3[df3['J'] < df3['K']]  
    else:
        pass
    
    # J/K线交叉
    if JKcross in ['bottom up','top down']:
        df3cross=findout_cross(df3,start,end,'J','K')
        df3cross2=pd.DataFrame(df3cross['交叉类型'])
        
        import pandas as pd
        df3=pd.merge(df3,df3cross2,how='inner',left_index=True,right_index=True)
        
        if JKcross == 'bottom up':
            df3=df3[df3['交叉类型']=='上穿']
        elif JKcross == 'top down':
            df3=df3[df3['交叉类型']=='下穿']
        else:
            pass
    
    if len(df3)==0:
        print("  #Warning(check_KDJ_market): no designated signals found for",ticker,"from",start,'to',end)
        return None,None
    
    # 未来上涨、下跌、振荡的比例
    df4a=df3[df3['trend_future'] == '+']
    pcta=len(df4a)/len(df3)
    df4b=df3[df3['trend_future'] == '-']
    pctb=len(df4b)/len(df3)
    df4c=df3[df3['trend_future'] == '~']
    pctc=len(df4c)/len(df3)

    # 未来转为下跌、上涨的比例
    df4d=df3[df3['trend_past2future'].isin(['+2-','~2-'])]
    pctd=len(df4d)/len(df3)
    df4e=df3[df3['trend_past2future'].isin(['-2+','~2+'])]
    pcte=len(df4e)/len(df3)
    
    import pandas as pd
    outcome=pd.DataFrame()
    
    row=pd.Series({'ticker':ticker,'start':start,'end':end, \
                   'K value':KDJ_values[0],'D value':KDJ_values[1],'J value':KDJ_values[2],
                   'J days':J_days,'JvsK':JvsK,'JKcross':JKcross,
                   'value type':value_type, \
                   'past_days':past_days,'momemtum_days':momemtum_days,'future_days':future_days,
                   'threshhold':threshhold, \
                   'future up ratio':pcta,'future down ratio':pctb,'future vibrate ratio':pctc, \
                   't2- ratio':pctd,'t2+ ratio':pcte})
    try:
        outcome=outcome.append(row,ignore_index=True)
    except:
        outcome=outcome._append(row,ignore_index=True)         
    
    return outcome,df3

#==============================================================================
#==============================================================================
if __name__ =="__main__":
    ticker='600518.SS'
    start='2013-1-1'
    end='2022-12-31'
    
    KDJ_days=[9,3,3]
    matypes=[0,0]
    
    past_days=1
    momemtum_days=0
    future_days=1
    threshhold=0.001
    
    KDJ_values=[50,50,50]
    J_days=1
    JvsK='above'
    JKcross='bottom up'
    
    value_type='floor'
    
    # 多头市场与空头市场
    dfs1=backtest_KDJ(ticker,start,end,KDJ_values=[50,50,50],value_type='floor')
    dfs2=backtest_KDJ(ticker,start,end,KDJ_values=[50,50,50],value_type='ceiling')
    
    # 超买区：茅台买家众多，即使在超买区，下跌趋势也比较有限
    dfs3=backtest_KDJ(ticker,start,end,KDJ_values=[80,80,80],value_type='floor')
    dfs4=backtest_KDJ(ticker,start,end,KDJ_values=[80,80,90],value_type='floor')
    dfs4=backtest_KDJ(ticker,start,end,KDJ_values=[80,80,90],J_days=3,value_type='floor')
     
    # 超卖区
    dfs12=backtest_KDJ(ticker,start,end,KDJ_values=[20,20,10],value_type='ceiling')
    dfs15=backtest_KDJ(ticker,start,end,KDJ_values=[20,20,0],J_days=3,value_type='ceiling')
   
    # K线在D线上方/下方
    dfs21=backtest_KDJ(ticker,start,end,KDJ_values=[50,50,50],JvsK='above',value_type='floor')
    dfs22=backtest_KDJ(ticker,start,end,KDJ_values=[50,50,50],JvsK='below',value_type='floor')
    
   # K/D线交叉
    dfs31=backtest_KDJ(ticker,start,end,KDJ_values=[50,50,50],JKcross='top down',value_type='floor')
    dfs32=backtest_KDJ(ticker,start,end,KDJ_values=[50,50,50],JKcross='bottom up',value_type='floor') 
    dfs32=backtest_KDJ(ticker,start,end,KDJ_values=[20,20,10],JKcross='bottom up',value_type='ceiling') 

    # 高位死叉
    dfs33=backtest_KDJ(ticker,start,end,KDJ_values=[80,80,90],JKcross='top down',value_type='floor')
    
    # 低位金叉
    dfs34=backtest_KDJ(ticker,start,end,KDJ_values=[20,20,10],JKcross='bottom up',value_type='ceiling')

def backtest_KDJ(ticker,start,end,
                      KDJ_days=[9,3,3],matypes=[0,0],
                      past_days=3,momemtum_days=0,future_days=3,threshhold=0.005,
                      KDJ_values=[50,50,50],J_days=1,JvsK='any',JKcross='any',
                      value_type='floor'):
    """
    功能：验证KDJ指标对股价未来走势判断的准确度概率
    
    注意：可能存在尚不明了的问题！！！
    """
    # 计算KDJ指标
    df=stock_KDJ(ticker,start,end,KDJ_days=KDJ_days,matypes=matypes,graph=False)
    total_obs=len(df)
    
    # 计算股价波动率，约等于1，无法作为threshhold使用
    #=df['Close'].std() / df['Close'].mean()
    
    # 计算某一日期前后的股价走势及其变化
    df1=price_trend_technical(df,
                              past_days=past_days,
                              momemtum_days=momemtum_days,future_days=future_days,
                              threshhold=threshhold)
    
    # KDJ特定情景：股价走势情形概率
    checkdf,dfs=check_KDJ_market(df1,start,end,
                                 KDJ_values=KDJ_values,J_days=J_days,
                                 JvsK=JvsK,JKcross=JKcross,
                                 value_type=value_type)
    if checkdf is None:
        #print("  #Warning(backtest_KDJ): no KDJ signals found for",ticker)
        print("  Possible reasons: conditions are too strict, or period is too short")
        return None
    
    if value_type == 'floor':
        rel=' > '
    elif value_type == 'ceiling':
        rel=' < '
    else:
        rel=' ? '
        
    signals1="K"+rel+str(KDJ_values[0])+', D'+rel+str(KDJ_values[1])+', J'+rel+str(KDJ_values[2])
    
    signals2=''
    if J_days > 1:
        signals2='\n    J值条件至少持续'+str(J_days)+'个交易日' 
    
    signals3=''
    if JvsK=='above':
        signals3='\n    J线在K线上方'
    elif JvsK=='below':
        signals3='\n    J线在K线下方'
    else:
        pass
    
    signals4=''
    if JKcross=='bottom up':
        signals4='\n    J/K线出现金叉'
    elif JKcross=='top down':
        signals4='\n    J/K线出现死叉'
    else:
        pass
        
    signals=signals1 +signals2 +signals3 +signals4
    print_KDJ_result(checkdf,dfs,signals,ticker,start,end,total_obs,JKcross,
                     past_days,momemtum_days,future_days,threshhold)
    """
    market_upward=dfs[dfs['trend_future']=='+']
    market_downward=dfs[dfs['trend_future']=='-']
    market_vibrate=dfs[dfs['trend_future']=='~']
    market_upturn=dfs[dfs['trend_past2future'].isin(['~2+','-2+'])]
    market_downturn=dfs[dfs['trend_past2future'].isin(['~2-','+2-'])]
    """
    return dfs    



#==============================================================================
def print_KDJ_result(checkdf,dfs,KDJ_signals,
                     ticker,start,end,total_obs,JKcross,
                     past_days,momemtum_days,future_days,threshhold):
    """
    功能：打印KDJ验证结果
    注意：KDJ_signals需要提前编辑条件字符串输入，例如"K > 80, D > 80, J > 100且至少持续3个交易日"
    """
    
    print("\n*** KDJ研判价格趋势：回溯验证，"+ticker_name(ticker))
    print("  "+start+'至'+end+'，共计'+str(total_obs)+'个样本')
    
    print("  KDJ信号：期间内出现"+str(len(dfs))+'次')
    print("    "+KDJ_signals)
    
    print("  验证参数:")
    print("    之前趋势期间："+str(past_days)+'个交易日')
    
    if momemtum_days > 0:
        print("    滞后变化/提前反应：滞后"+str(momemtum_days)+'个交易日')
    elif momemtum_days == 0:
        print("    滞后变化/提前反应：无，立即变化")
    else:
        print("    滞后变化/提前反应：提前"+str(momemtum_days)+'个交易日')
        
    print("    之后趋势期间："+str(future_days)+'个交易日')
    print("    股价变化过滤门限："+str(threshhold*100)+'%')
    
    print("  回溯检验结果:")
    print("    之后出现价格上涨趋势的比例:",round(checkdf['future up ratio'].values[0]*100,1),'\b%')
    print("    之后出现价格下跌趋势的比例:",round(checkdf['future down ratio'].values[0]*100,1),'\b%')
    print("    之后出现价格振荡情形的比例:",round(checkdf['future vibrate ratio'].values[0]*100,1),'\b%')    
    
    """
    if JKcross =='bottom up':
        print("    出现JD金叉后价格上涨的比例:",round(checkdf['t2+ ratio'].values[0]*100,1),'\b%')
    elif JKcross =='top down':
        print("    出现JK死叉后价格下跌的比例:",round(checkdf['t2- ratio'].values[0]*100,1),'\b%')
    else:
        pass
    """
    
    return
#==============================================================================
#==============================================================================    
if __name__ =="__main__":
    ticker='600519.SS'
    fromdate='2023-1-1'
    todate='2023-6-25'
    boll_days=20
    graph=True
    smooth=False
    loc='best'
    date_range=False
    date_freq=False
    annotate=False

def security_Bollinger(ticker,start='default',end='default',boll_days=20, \
                         graph=True,smooth=True,loc='best', \
                         date_range=False,date_freq=False,annotate=False, \
                         ticker_type='auto',source='auto',facecolor='white'):
    """
    套壳函数，为了与security_MACD/RSI/KDJ保持相似
    """
    df=stock_Bollinger(ticker=ticker,start=start,end=end,boll_days=boll_days, \
                             graph=graph,smooth=smooth,loc=loc, \
                             date_range=date_range,date_freq=date_freq, \
                             annotate=annotate,ticker_type=ticker_type,source=source,facecolor=facecolor)
    return df

def stock_Bollinger(ticker,start='default',end='default',boll_days=20, \
                         graph=True,smooth=True,loc='best', \
                         date_range=False,date_freq=False,annotate=False, \
                         mark_end=True,ticker_type='auto',source='auto',facecolor='white'):
    """
    套壳函数，为了与stock_MACD/RSI/KDJ保持相似
    """
    
    #=========== 日期转换与检查
    # 检查日期：截至日期
    import datetime as dt; today=dt.date.today()
    if end in ['default','today']:
        end=today
    else:
        validdate,end=check_date2(end)
        if not validdate:
            print("  #Warning(stock_Bollinger): invalid date for",end)
            end=today

    # 检查日期：开始日期
    if start in ['default']:
        start=date_adjust(end,adjust=-31)
    else:
        validdate,start=check_date2(start)
        if not validdate:
            print("  #Warning(stock_Bollinger): invalid date for",start)
            start=date_adjust(todate,adjust=-31)

    df=security_bollinger(ticker=ticker,fromdate=start,todate=end,boll_days=boll_days, \
                             graph=graph,smooth=smooth,loc=loc, \
                             date_range=date_range,date_freq=date_freq,annotate=annotate, \
                             mark_end=mark_end,ticker_type=ticker_type,source=source,facecolor=facecolor)
    return df


def security_bollinger(ticker,fromdate,todate,boll_days=20, \
                         graph=True,smooth=True,loc='best', \
                         date_range=False,date_freq=False,annotate=False, \
                         mark_end=True,ticker_type='auto',source='auto',facecolor='white'):
    """
    功能：单个证券，绘制布林带
    date_range=False：指定开始结束日期绘图
    date_freq=False：指定横轴日期间隔，例如'D'、'2D'、'W'、'M'等，横轴一般不超过25个标注，否则会重叠
    
    解释布林带：
    1、上线：压力线；下线：支撑线；均线：中界线
    2、上下限之间：置信区间+/-2std
    3、价格由下向上穿越下线时，可视为买进信号；价格由下向上穿越中间线时，则有可能加速上行，是加仓买进的信号。
    4、价格在中界线与上线之间波动运行时为多头市场，可持多或加码；价格长时间在中界线与上线间运行后，由上往下跌破中间线为卖出信号。
    5、价格在中界线与下线之间向下波动运行时为空头市场，可持空或加抛。
    """
    # 提前开始日期
    fromdate1=date_adjust(fromdate,adjust=-365*1)
    
    try:
        #pricedf=get_price(ticker,fromdate1,todate)
        pricedf,found=get_price_1ticker_mixed(ticker=ticker,fromdate=fromdate1, \
                                        todate=todate,ticker_type=ticker_type,source=source)
    except:
        print("  #Error(security_bollinger): price info not found for",ticker)
        return None
    if found not in ['Found']:
        print("  #Error(security_bollinger): ticker info either inaccessible or not found for",ticker)
        return None
        
    # 滚动均值与标准差
    pricedf['bmiddle']=pricedf["Close"].rolling(window=boll_days).mean()
    pricedf['bsd']=pricedf["Close"].rolling(window=boll_days).std()
    pricedf['bupper']=pricedf["bmiddle"] + pricedf['bsd']*2
    pricedf['blower']=pricedf["bmiddle"] - pricedf['bsd']*2
    
    df=pricedf[['bupper','bmiddle','blower','Close']]
    df.rename(columns={'bupper':text_lang('上线(阻力线)','Upper Line'),'bmiddle':text_lang('中线(均线)','Mid Line'),'blower':text_lang('下线(支撑线)','Lower Line'),'Close':text_lang('收盘价','Close')},inplace=True)

    # 截取时间段
    result,start,end=check_period(fromdate,todate)
    df1=df[(df.index >= start) & (df.index <= end)]

    y_label=text_lang('价格',"Price")
    import datetime; today = datetime.date.today()
    x_label=text_lang("数据来源：Sina/EM/Stooq/Yahoo，","Data source: Sina/EM/Stooq/Yahoo, ")+str(today)

    axhline_value=0
    axhline_label=''
    title_txt=text_lang("证券技术分析：","Technical Analysis: ")+ticker_name(ticker,ticker_type)+text_lang("，布林带",", Bollinger Band")         
    
    """
        draw_lines(df1,y_label,x_label,axhline_value,axhline_label,title_txt, \
                   data_label=False,resample_freq='H',smooth=smooth,loc=loc,annotate=annotate)
    """
    #plt.rcParams['axes.facecolor']='gray'
    colorlist=['orange','black','purple','red']
    lslist=['--',':','-.','-']
    lwlist=[2.0,2.0,2.0,2.5]
    draw_lines2(df1,y_label,x_label,axhline_value,axhline_label,title_txt, \
               data_label=False,resample_freq='6H',smooth=smooth, \
               date_range=date_range,date_freq=date_freq,date_fmt='%Y-%m-%d', \
               colorlist=colorlist,lslist=lslist,lwlist=lwlist, \
               band_area=[text_lang('上线(阻力线)','Upper Line'),text_lang('下线(支撑线)','Lower Line')], \
               mark_end=mark_end,loc=loc,facecolor=facecolor)

    return df1

#==============================================================================
#==============================================================================    
if __name__ =="__main__":
    ticker='600809.SS'
    start='2013-11-06'
    end='2024-02-29'
    boll_years=7
    graph=True
    smooth=False
    loc='best'
    date_range=False
    date_freq=False
    annotate=False
    
    indicator='PE'

def security_Bubble(ticker,start='default',end='default',boll_years=7, \
                    indicator='MV', \
                    graph=True,smooth=True,loc='best', \
                    date_range=False,date_freq=False,annotate=False, \
                    mark_end=True,facecolor='whitesmoke'):
    """
    套壳函数，为了与security_MACD/RSI/KDJ保持相似
    """
    
    #=========== 日期转换与检查
    # 检查日期：截至日期
    import datetime as dt; todaydt=dt.date.today()
    if end in ['default','today']:
        end=todaydt
    else:
        validdate,end=check_date2(end)
        if not validdate:
            print("  #Warning(security_Bubble): invalid date for",end)
            end=todaydt

    # 检查日期：开始日期
    if start in ['default']:
        start=date_adjust(end,adjust=-31)
    else:
        validdate,start=check_date2(start)
        if not validdate:
            print("  #Warning(security_Bubble): invalid date for",start)
            start=date_adjust(todate,adjust=-31)

    df=security_bubble(ticker=ticker,fromdate=start,todate=end,boll_years=boll_years, \
                       indicator=indicator, \
                       graph=graph,smooth=smooth,loc=loc, \
                       date_range=date_range,date_freq=date_freq,annotate=annotate, \
                       mark_end=mark_end,facecolor=facecolor)
    return df

if __name__ =="__main__":
    ticker='600519.SS'
    ticker='AAPL'
    fromdate='2023-7-3'
    todate='2024-2-21'
    boll_years=7
    indicator='MV'

def security_bubble(ticker,fromdate,todate,boll_years=7, \
                    indicator='MV', \
                    graph=True,smooth=True,loc='best', \
                    date_range=False,date_freq=False,annotate=False, \
                    mark_end=True,facecolor='whitesmoke'):
    """
    功能：单个证券，绘制估值布林带(MV, PE, PB)
    date_range=False：指定开始结束日期绘图
    date_freq=False：指定横轴日期间隔，例如'D'、'2D'、'W'、'M'等，横轴一般不超过25个标注，否则会重叠
    
    解释布林带：
    1、上线：压力线；下线：支撑线；均线：中界线
    2、上下限之间：置信区间+/-2std，2倍标准差的含义是落在此区间内的概率不低于95%！
    3、估值由下向上穿越下线时，可视为买进信号；估值由下向上穿越中间线时，则有可能加速上行，是加仓买进的信号。
    4、估值在中界线与上线之间波动运行时为多头市场，可持多或加码；估值长时间在中界线与上线间运行后，由上往下跌破中间线为卖出信号。
    5、估值在中界线与下线之间向下波动运行时为空头市场，可持空或加抛。
    """
    if not isinstance(ticker,str):
        print("  #Warning(security_bubble): not a valid stock code format for",ticker)
        return None
    
    if indicator.lower()=='mv':
        indicatorname='市值(十亿)'
    elif indicator.lower()=='pe':
        indicatorname='市盈率'
    elif indicator.lower()=='pb':
        indicatorname='市净率' 
    elif indicator.lower()=='roe':
        indicatorname='净资产回报率'         
    else:
        print("  #Error(security_bubble): unsupported valuation indicator for",indicator)
        return None
    
    # 提前开始日期
    fromdate1=date_adjust(fromdate,adjust=-365*boll_years)
    
    try:
        val=get_valuation(ticker,indicator,fromdate1,todate)
        colname=list(val[indicator])[0]
        pricedf=val[indicator]
        pricedf.rename(columns={colname:indicator},inplace=True)
    except:
        print("  #Error(security_bubble): valuation info not found for",ticker,'on',indicator)
        return None

    # 滚动均值与标准差
    #注意：A股估值数据为非日频，港股/美股/波兰股为日频
    day0=pricedf.index[0].strftime("%Y-%m-%d")
    day1=pricedf.index[-1].strftime("%Y-%m-%d")
    day_diff=calculate_days(day0,day1)
    annualTradeDays=len(pricedf) / (day_diff/365)
    #boll_days=int(boll_years*annualTradeDays+0.5)
    boll_days=int(boll_years*annualTradeDays)
    """
    _,_,suffix=split_prefix_suffix(ticker)
    if suffix in ['SS','SZ','BJ']:
        boll_days=int(boll_years*annualTradeDays)
    else:
        boll_days=boll_years*252
    """    
    if boll_days >= len(pricedf):
        boll_years=int(len(pricedf)/annualTradeDays)
        boll_days=int(boll_years*annualTradeDays)
        
    record_left=len(pricedf)-boll_days
    
    if record_left < 65:#一个季度
        boll_years=boll_years-1
        #boll_days=boll_years*252
        boll_days=int(boll_years*annualTradeDays)
        record_left=len(pricedf)-boll_days
        
    pricedf_left=pricedf.tail(record_left)
    start_left=pricedf_left.index[0].strftime('%Y-%m-%d')
        
    pricedf['bmiddle']=pricedf[indicator].rolling(window=boll_days).mean()
    pricedf['bsd']=pricedf[indicator].rolling(window=boll_days).std()
    pricedf['bupper']=pricedf["bmiddle"] + pricedf['bsd']*2
    pricedf['blower']=pricedf["bmiddle"] - pricedf['bsd']*2
    
    df=pricedf[['bupper','bmiddle','blower',indicator]]
        
    df.rename(columns={'bupper':'上线(阻力线)','bmiddle':'中线(均线)','blower':'下线(支撑线)',indicator:indicatorname},inplace=True)

    # 截取时间段
    result,start,end=check_period(fromdate,todate)
    start1=date_adjust(start,adjust=-10)
    if start_left > start1:
        start1=start_left
        
    df1=df[(df.index >= start1) & (df.index <= end)]

    y_label=indicatorname
    import datetime; today = datetime.date.today()
    x_label="数据来源：Sina/EM/Stooq/Yahoo，"+str(today)+"，估值前置窗口期"+str(boll_years)+"年"

    axhline_value=0
    axhline_label=''
    title_txt="证券估值趋势布林带："+ticker_name(ticker)            
    
    """
        draw_lines(df1,y_label,x_label,axhline_value,axhline_label,title_txt, \
                   data_label=False,resample_freq='H',smooth=smooth,loc=loc,annotate=annotate)
    """
    #plt.rcParams['axes.facecolor']='gray'
    colorlist=['orange','black','purple','red']
    lslist=['--',':','-.','-']
    lwlist=[2.0,2.0,2.0,2.5]
    draw_lines2(df1,y_label,x_label,axhline_value,axhline_label,title_txt, \
               data_label=False,resample_freq='6H',smooth=smooth, \
               date_range=date_range,date_freq=date_freq,date_fmt='%Y-%m-%d', \
               colorlist=colorlist,lslist=lslist,lwlist=lwlist, \
               band_area=['上线(阻力线)','下线(支撑线)'],loc=loc, \
               mark_end=mark_end,facecolor=facecolor)

    return df1

#==============================================================================
if __name__ =="__main__":
    ticker='600519.SS'
    ticker='600809.SS'
    start='MRH'
    start='L10Y'
    end='default'
    
    start='2023-1-1'
    end='2024-2-20'
    
    boll_years=7
    technical='MV'
    technical='Bollinger'
    indicator='PE'

def security_technical(ticker,technical=['MACD'],indicator='Close', \
                       start='default',end='default', \
                       MA_days=[5,20],EMA_days=[5,20], \
                       MACD_fastperiod=12,MACD_slowperiod=26,MACD_signalperiod=9, \
                             
                       #RSI参数个数必须为3个，否则出错
                       RSI_days=[6,14,24],RSI_lines=[30,50,70], \
                       KDJ_days=[9,3,3],matypes=[0,0],KDJ_lines=[20,50,80], \
                       boll_days=20,boll_years=7, \
                             
                       resample_freq='1D',smooth=True,linewidth=1.5, \
                       loc1='best',loc2='best', \
                       graph=['ALL'],printout=False, \
                       date_range=False,date_freq=False,annotate=False, \
                       ticker_type='auto',source='auto', \
                       price_line_color='blue', \
                       facecolor='white'):
    
    """
    ===========================================================================
    功能：技术分析指标的深度分析，适用于MACD/RSI/KDJ/Bollinger，支持金叉/死叉分析等。
    支持的产品：全球股票，债券（限中国内地的上市债券），基金（支持中国和美国的上市基金）。
    主要参数：
    ticker：证券代码
    technical：技术分析指标，仅支持'MACD'、'RSI'、'KDJ'、'Bollinger'，可一次指定多个。
    start/end：起止日期。支持简洁方式，仅需使用start指定近期的期间长度。简洁方式如下：
        mrw（近1周），l2w（近2周），l3w（近3周），mrm（近1个月），l2m（近2个月），
        mrq（近3个月），mrh（近6个月），mry（近1年），l2y（近2年），l3y（近3年），
        l5y（近5年），l8y（近8年），l10y（近10年），l20y（近20年），l30y（近30年），
        ytd（今年以来）
    技术分析指标的参数，可手动调节，默认如下：
        MACD_fastperiod=12,MACD_slowperiod=26,MACD_signalperiod=9
        MA_days=[5,20],EMA_days=[5,20]
        RSI_days=[6,12,24],RSI_lines=[20,50,80]
        KDJ_days=[9,3,3],matypes=[0,0],KDJ_lines=[20,50,80]
        boll_days=20,boll_years=7
    loc1/loc2：第1和第2图例的位置，默认'best'。如果发生重合或位置不合适，可手动调节。
    graph：显示的结果图，默认'ALL'。分析MACD时若只希望看到MACD图，可指定'MACD'。
    annotate：是否希望将图例标示在曲线末端，默认False，防止标示文字重叠。
    ticker_type：证券种类，默认'auto'。可强制指定股票'stock'、债券'bond'、基金'fund'。
    source：证券价格数据源，默认'auto'。若指定'yahoo'需要特别连接互联网。
    price_line_color：价格曲线颜色，默认'red'。
    facecolor：背景颜色，默认黑色。
        注意：白色背景可能遮盖部分曲线，不建议；
        黑色背景可能与布林带中线文字标示颜色冲突，可手动指定其他颜色，例如'whitesmoke'。
    
    其他说明：套壳函数security_MACD/RSI/KDJ/Bollinger
    """
    
    # 检查日期：如有错误自动更正
    fromdate,todate=start_end_preprocess(start=start,end=end)

    # 打补丁
    if technical in ['MA','EMA','MACD']:
        graph = technical
        technical = 'MACD'

    # 检查类别   
    if isinstance(technical,str):
        technical1=[technical]
    else:
        technical1=technical
    
    technical_list=['MACD','RSI','KDJ','Bollinger']   
    technical1 = [x.upper() for x in technical1]
    technical1 = [x.replace('BOLLINGER','Bollinger') if 'BOLLINGER' in x else x for x in technical1]
    
    for t in technical1:
        if t not in technical_list:
            print("  Warning(security_technical): unsupported technical pattern",t)
            print("  Supported patterns:",technical_list)
            return None
    
    #检查布林带的指标
    if isinstance(indicator,str):
        indicator1=[indicator]
    else:
        indicator1=indicator
    
    indicator_list1=['MV','PE','PB','Close','ROE']   
    indicator1 = [x.upper() for x in indicator1]
    indicator1 = [x.replace('CLOSE','Close') if 'CLOSE' in x else x for x in indicator1]
    
    for t in indicator1:
        if t not in indicator_list1:
            print("  Warning(security_technical): unsupported Bollinger indicator",t)
            print("  Supported Bollinger indicator:",indicator_list1) 
            return None
    
    # 检查绘图种类
    if isinstance(graph,str):
        graph1=[graph]
    else:
        graph1=graph
            
    if 'MACD' in technical1:
        df=security_MACD(ticker=ticker,start=fromdate,end=todate, \
             MA_days=MA_days,EMA_days=EMA_days, \
             MACD_fastperiod=MACD_fastperiod,MACD_slowperiod=MACD_slowperiod,MACD_signalperiod=MACD_signalperiod, \
             resample_freq=resample_freq,smooth=smooth,linewidth=linewidth, \
             loc1=loc1,loc2=loc2, \
             graph=graph1,printout=printout,ticker_type=ticker_type,source=source, \
             price_line_color=price_line_color,facecolor=facecolor)
       
    if 'RSI' in technical1:
        df=security_RSI(ticker=ticker,start=fromdate,end=todate, \
             RSI_days=RSI_days,RSI_lines=RSI_lines, \
             resample_freq=resample_freq,smooth=smooth,linewidth=linewidth, \
             loc1=loc1,loc2=loc2, \
             graph=graph1,printout=printout,ticker_type=ticker_type,source=source, \
             price_line_color=price_line_color,facecolor=facecolor)

    if 'KDJ' in technical1:
        df=security_KDJ(ticker=ticker,start=fromdate,end=todate, \
             KDJ_days=KDJ_days,matypes=matypes,KDJ_lines=KDJ_lines, \
             resample_freq=resample_freq,smooth=smooth,linewidth=linewidth, \
             loc1=loc1,loc2=loc2, \
             graph=graph1,printout=printout,ticker_type=ticker_type,source=source, \
             price_line_color=price_line_color,facecolor=facecolor)

    if 'Bollinger' in technical1 and 'Close' in indicator1:
        df=security_Bollinger(ticker=ticker,start=fromdate,end=todate,boll_days=boll_days, \
                         graph=True,smooth=smooth,loc=loc1, \
                         date_range=date_range,date_freq=date_freq,annotate=annotate, \
                         ticker_type=ticker_type,source=source,facecolor=facecolor)

    """
    if 'Bollinger' in technical1 and 'MV' in indicator1:
        df=security_Bubble(ticker=ticker,start=fromdate,end=todate,boll_years=boll_years, \
                            indicator='MV', \
                            graph=True,smooth=smooth,loc=loc1, \
                            date_range=date_range,date_freq=date_freq,annotate=annotate)

    if 'Bollinger' in technical1 and 'PE' in indicator1:
        df=security_Bubble(ticker=ticker,start=fromdate,end=todate,boll_years=boll_years, \
                            indicator='PE', \
                            graph=True,smooth=smooth,loc=loc1, \
                            date_range=date_range,date_freq=date_freq,annotate=annotate)            

    if 'Bollinger' in technical1 and 'PB' in indicator1:
        df=security_Bubble(ticker=ticker,start=fromdate,end=todate,boll_years=boll_years, \
                            indicator='PB', \
                            graph=True,smooth=smooth,loc=loc1, \
                            date_range=date_range,date_freq=date_freq,annotate=annotate)            

    if 'Bollinger' in technical1 and 'ROE' in indicator1:
        df=security_Bubble(ticker=ticker,start=fromdate,end=todate,boll_years=boll_years, \
                            indicator='ROE', \
                            graph=True,smooth=smooth,loc=loc1, \
                            date_range=date_range,date_freq=date_freq,annotate=annotate)              
    """
    
    if 'Bollinger' in technical1:
        vallist=['MV','PE','PB','ROE']
        #if val in vallist and val in indicator1: #只能处理股票估值，无需ticker_type
        if any(val in indicator1 for val in vallist):
            val=list(set(indicator1).intersection(set(vallist)))[0] #找出2个列表中第1个共同元素
            df=security_Bubble(ticker=ticker,start=fromdate,end=todate,boll_years=boll_years, \
                                indicator=val, \
                                graph=True,smooth=smooth,loc=loc1, \
                                date_range=date_range,date_freq=date_freq,annotate=annotate,facecolor=facecolor)
    
    return df

#==============================================================================
#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
if __name__ =="__main__":
    RSI_days=[6,24]
    OBV_days=[5,10]
    MA_days=[5,20]; EMA_days=[5,20]
    MACD_fastperiod=12; MACD_slowperiod=26; MACD_signalperiod=9
    KDJ_fastk_period=5; KDJ_slowk_period=3; KDJ_slowk_matype=0; KDJ_slowd_period=3; KDJ_slowd_matype=0
    VOL_fastperiod=5; VOL_slowperiod=10
    PSY_days=12
    ARBR_days=26
    CR_day=16; CR_madays=[5,10,20]
    EMV_day=14; EMV_madays=9
    BOLL_day=20; BOLL_nbdevup=2; BOLL_nbdevdn=2; BOLL_matype=0
    TRIX_day=12; TRIX_madays=20
    DMA_fastperiod=10; DMA_slowperiod=50; DMA_madays=10
    BIAS_days=[6,12,24]
    CCI_days=[6,12]
    WR_days=[10,6]
    ROC_day=12; ROC_madays=6
    DMI_DIdays=14; DMI_ADXdays=6
    MFI_day=14; MFI_madays=[6]
    MOM_day=12; MOM_madays=6
    SAR_day=4; SAR_madays=[5,20]
    BETA_day=5; BETA_madays=[5,20]
    TSF_day=14; TSF_madays=[5,10]
    AD_madays=[5]
    
    
    ticker='002594.SZ';ticker_type='auto'
    start='2024-5-1'; end='2024-6-13'; ahead_days=30*8
    technical='BIAS'; indicator='Close'
    
    attention_values=[0,25,50,75]
    more_details=True
    ticker_type='auto'; source='auto'
    ahead_days=30*8
    resample_freq='6H'; smooth=True;linewidth=1.5
    date_range=False; date_freq=False; annotate=False
    graph=['ALL']; printout=False
    loc1='best'; loc2='best'
        
    facecolor=['whitesmoke','papayawhip']
    price_line_style='dotted'; price_line_color='red'; price_line_width=5; price_line_marker='.'
    marker_sizes=[30,120,250]
    
    df=security_technical2(ticker='AAPL',start='2024-5-1',end='2024-6-20', \
                           technical='CR',more_details=True,loc1='upper left',loc2='lower right')
    
    tlist=['RSI','OBV','MACD','KDJ','VOL','PSY','ARBR','CR','EMV','Bollinger', \
           'TRIX','DMA','BIAS','CCI','W%R','ROC','DMI']
    for t in tlist:
        df=security_technical2(ticker,start,end,technical=t,loc1='lower left',loc2='lower right')
    
def security_technical2(ticker,start='default',end='default',technical='MACD', \
                            
        #不建议使用复权价，因为最高最低价开盘价不易获取到复权价！    
        indicator='Close', \
            
        #显示指标本身，如果原来未显示的话
        more_details=False, \
            
        #显示关注值水平线，每个指标不同，可自定义多个关注值
        attention_values=[], \

        ticker_type='auto',source='auto', \
        
        #指标的默认参数
        RSI_days=[6,14], \
            
        OBV_days=[5,10], \
        
        MA_days=[5,20],EMA_days=[5,20], \
            
        MACD_fastperiod=12,MACD_slowperiod=26,MACD_signalperiod=9, \
        
        KDJ_fastk_period=9,KDJ_slowk_period=5,KDJ_slowk_matype=1,KDJ_slowd_period=5,KDJ_slowd_matype=1, \
        
        VOL_fastperiod=5,VOL_slowperiod=10, \
            
        PSY_days=[6,12], \
            
        ARBR_days=[26], \
            
        CR_day=30,CR_madays=[10,20,40,60], \
            
        EMV_day=14,EMV_madays=[9], \
        
        BOLL_day=20,BOLL_nbdevup=2,BOLL_nbdevdn=2,BOLL_matype=0, \
        
        DMA_fastperiod=10,DMA_slowperiod=50,DMA_madays=[10], \
        
        TRIX_day=12,TRIX_madays=[20], \
            
        BIAS_days=[6,12,24], \
            
        CCI_days=[6,12], \
            
        WR_days=[13,34,89], \
            
        ROC_day=12,ROC_madays=[65,12,18], \
            
        DMI_DIdays=7,DMI_ADXdays=6, \
        
        #资金流：
        MFI_day=14,MFI_madays=[6], \
            
        MOM_day=12,MOM_madays=6, \
            
        #需要显示SAR
        SAR_day=4,SAR_madays=[5,20], \
            
        #需要显示BETA
        BETA_day=5,BETA_madays=[5,20], \
        
        #需要显示TSF
        TSF_day=14,TSF_madays=[5,10], \
            
        #需要显示AD
        AD_madays=[], \
        
        #数据提前量，用于前置计算指标的移动平均值   
        ahead_days=30*8, \
            
        #指标线的绘图参数
        resample_freq='2H',smooth=True,linewidth=1.5, \
        date_range=False,date_freq=False, \
            
        #启用，替代loc1图例
        annotate=True, \
        
        #除了MACD外，其他指标均应为ALL
        graph=['ALL'], \
        printout=False, \
        loc1='best',loc2='best', \
        
        #图形上下半区的背景颜色
        facecolor=['whitesmoke','papayawhip'], \
            
        #价格线的绘图参数
        #price_line_style=(0,(1,1)), \
        price_line_style=(0,(3,1,1,1,1,1)), \
        price_line_color=['red','green'], \
        price_line_width=1,price_line_marker='o', \
        #marker_sizes=[30,120,250], \
        marker_sizes=[0,0,0],
        ):
    """
    ===========================================================================
    功能：技术分析指标的短线德宏图，建议两个月内，适合观察日差价和价量关系变化，图示简洁。
    主要参数：
    ticker：证券代码，除美股外需要交易所后缀，例如港股小米'01810.HK'，美股苹果'AAPL'
    start：开始日期，格式YYYY-MM-DD，默认一个月前
    end：结束日期，格式与start相同，默认已收盘的最近交易日
    technical：技术分析指标，默认为MACD，单次仅可指定一个指标。支持的指标如下：
        Bollinger：布林带
        MACD：移动异同平均线
        RSI：相对强弱
        KDJ：随机指标
        OBV：能量潮
        SAR：抛物线/停损转向指标
        VOL：成交量指标
        ARBR：人气(AR)/意愿(BR)指标
        CR：中间意愿指标
        EMV：简易波动
        TRIX：三重指数平滑均线
        DMA：均线差
        BIAS：乖离率
        CCI：顺势指标
        W%R：威廉超买/超卖指标
        ROC：变动率
        DMI：动向指标
        PSY：心理线
        MFI：资金流向指标
        MOM：动量指标
        BETA：移动贝塔系数
        TSF：时间序列分析
        AD：集散指标
        MA：简单移动平均
        EMA：指数移动平均

    RSI_days：默认[6,14]        
    OBV_days：默认[5,10]    
    MA_days：默认[5,20]
    EMA_days：默认[5,20]；EMV_day：默认14：EMV_madays：默认[9]    
    MACD_fastperiod：默认12；MACD_slowperiod：默认26；MACD_signalperiod：默认9      
    KDJ_fastk_period：默认9；KDJ_slowk_period：默认5；KDJ_slowk_matype：默认1
    KDJ_slowd_period：默认5；KDJ_slowd_matype：默认1    
    VOL_fastperiod：默认5；VOL_slowperiod：默认10        
    PSY_days：默认[6,12]        
    ARBR_days：默认[26]        
    CR_day：默认30；CR_madays：默认[10,20,40,60]    
    BOLL_day：默认20；BOLL_nbdevup：默认2；BOLL_nbdevdn：默认2；BOLL_matype：默认0    
    DMA_fastperiod：默认10；DMA_slowperiod：默认50；DMA_madays：默认[10]
    TRIX_day：默认12；TRIX_madays：默认[20]        
    BIAS_days：默认[6,12,24]        
    CCI_days：默认[6,12]        
    WR_days：默认[13,34,89]        
    ROC_day：默认12；ROC_madays：默认[65,12,18]        
    DMI_DIdays：默认7；DMI_ADXdays：默认6    
    MFI_day：默认14；MFI_madays：默认[6]
    MOM_day：默认12；MOM_madays：默认6        
    SAR_day：默认4；SAR_madays：默认[5,20]        
    BETA_day：默认5；BETA_madays：默认[5,20]    
    TSF_day：默认14；TSF_madays：默认[5,10]        
    AD_madays：默认[]
    
    more_details：显示指标本身，如果原来未显示的话。默认不显示
    attention_values：显示关注值水平线，每个技术指标可能不同，可使用列表自定义多个关注值
    ticker_type：证券类别，默认'auto'。如果识别错误,可强制指定'stock'、'bond'、'fund'
    source：证券价格来源，默认'auto'。特殊来源可自行指定

    loc1：第1个图例的位置，默认'best'。当annotate=True时被替代
    loc2：第2个图例的位置，默认'best'。可手动指定9个位置，例如'upper left'左上角等
    facecolor：图形上下半区的背景颜色，默认['whitesmoke','papayawhip']
    attention_values：关注的阈值，默认[0,25,50,75,100], 可以自定义
    
    下列指标可以使用强化指令security_technical：MACD、RSI、KDJ、Bollinger
    """
    # 检查ta-lib是否安装，避免浪费后续的处理
    try:
        import talib  
    except:
        print("  #Error(security_technical2): lack of necessary package - talib")
        talib_install_method()
        return None
    
    #检查证券代码
    if not isinstance(ticker,str):
        print("  #Warning(security_technical2): not a security code for",ticker)
        return None        

    #检查indicator
    if indicator not in ['Open','Close','High','Low','Adj Close']:
        print("  #Warning(security_technical2): not a valid price type for",indicator)
        return None        
        
    #检查日期：如有错误自动更正
    fromdate,todate=start_end_preprocess(start=start,end=end)
    
    #检查指标类别
    tech_list={'Bollinger':text_lang('布林带','Bollinger Band'), \
               'MACD':text_lang('移动异同平均线','Moving Average Convergence Divergence'), \
               'RSI':text_lang('相对强弱','Relative Strength Index'), \
               'KDJ':text_lang('随机指标','Stochastics'), \
               'OBV':text_lang('能量潮','On-Balance-Volume'), \
               'SAR':text_lang('抛物线/停损转向指标','Stop and Reverse Indicator'), \
               'VOL':text_lang('成交量指标','Volume Indicator'), \
               'ARBR':text_lang('人气(AR)意愿(BR)指标','Emotion AR & Willingness BR'), \
               'CR':text_lang('中间意愿指标','Commodity Channel Index Reversal'), \
               'EMV':text_lang('简易波动','Ease of Movement Value'), \
               'TRIX':text_lang('三重指数平滑均线','Triple Exponentially Smoothed Moving Average'), \
               'DMA':text_lang('均线差','Difference in Moving Averages'), \
               'BIAS':text_lang("乖离率",'Bias Indicator'), \
               'CCI':text_lang('顺势指标','Commodity Channel Index'), \
               'W%R':text_lang('威廉超买/超卖指标','William Overbought/Oversold Index'), \
               'ROC':text_lang('变动率','Rate of Change'), \
               'DMI':text_lang('动向指标','Directional Movement Index'), \
               'PSY':text_lang('心理线','Phycholoigical Line'), \
               'MFI':text_lang('资金流向指标','Money Flow Index'), \
               'MOM':text_lang('动量指标','Momentum'), \
               'BETA':text_lang("移动贝塔系数",'Moving Beta Coefficient'), \
               'TSF':text_lang("时间序列分析",'Time Series Forecasting'), \
               'AD':text_lang('集散指标','Accumulation/Distribution'), \
               'MA':text_lang('简单移动平均','Moving Average'), \
               'EMA':text_lang('指数移动平均','Exponential Moving Average')}

    technical1=technical
    if isinstance(technical,list):
        technical1=technical[0]
    technical1=technical1.upper()
    if technical1 == 'BOLLINGER': technical1=technical1.title()

    if technical1 not in list(tech_list):
        print("  #Warning(security_technical2): unsupported technical pattern",technical)
        print("  Supported patterns:",list(tech_list))
        return None        
        
    #抓取抓取价格数据
    fromdate1=date_adjust(fromdate,adjust=-ahead_days)
    if 'Adj' in indicator.title():
        adjust='Adj_only' #最高最低价开盘收盘价均为复权价
    else:
        adjust=''
        
    price,found=get_price_1ticker_mixed(ticker=ticker,fromdate=fromdate1,adjust=adjust, \
                                        todate=todate,ticker_type=ticker_type,fill=False,source=source)

    if found not in ['Found']:
        print("  #Warning(security_technical2): no prices found for",ticker,'as type',ticker_type)
        return None        

    #当日涨跌
    price['up_down']=price['Close']-price['Open']
    price['up_down_abs']=abs(price['up_down'])
    
    #分位数
    import numpy as np
    q70=np.percentile(price['up_down_abs'],70)
    q30=np.percentile(price['up_down_abs'],30)
    
    small_size=marker_sizes[0]; mid_size=marker_sizes[1]; big_size=marker_sizes[2]
    price['marker_size']=price['up_down_abs'].apply(lambda x: big_size if x>=q70 else mid_size if x>=q30 else small_size)
    
    #计算技术指标
    df,calculated=calc_technical(price,fromdate,todate,technical=technical, \
                          
            RSI_days=RSI_days, \
            OBV_days=OBV_days, \
                
            MA_days=MA_days,EMA_days=EMA_days, \
                
            MACD_fastperiod=MACD_fastperiod,MACD_slowperiod=MACD_slowperiod,MACD_signalperiod=MACD_signalperiod, \
                
            KDJ_fastk_period=KDJ_fastk_period,KDJ_slowk_period=KDJ_slowk_period, \
            KDJ_slowk_matype=KDJ_slowk_matype,KDJ_slowd_period=KDJ_slowd_period,KDJ_slowd_matype=KDJ_slowd_matype, \
                
            VOL_fastperiod=VOL_fastperiod,VOL_slowperiod=VOL_slowperiod, \
                
            PSY_days=PSY_days, \
            ARBR_days=ARBR_days, \
            CR_day=CR_day,CR_madays=CR_madays, \
            EMV_day=EMV_day,EMV_madays=EMV_madays, \
                
            BOLL_day=BOLL_day,BOLL_nbdevup=BOLL_nbdevup,BOLL_nbdevdn=BOLL_nbdevdn,BOLL_matype=BOLL_matype, \
                
            DMA_fastperiod=DMA_fastperiod,DMA_slowperiod=DMA_slowperiod,DMA_madays=DMA_madays, \
                
            TRIX_day=TRIX_day,TRIX_madays=TRIX_madays, \
            BIAS_days=BIAS_days, \
            CCI_days=CCI_days, \
            WR_days=WR_days, \
            ROC_day=ROC_day,ROC_madays=ROC_madays, \
            DMI_DIdays=DMI_DIdays,DMI_ADXdays=DMI_ADXdays, \
                
            MFI_day=MFI_day,MFI_madays=MFI_madays, \
            MOM_day=MOM_day,MOM_madays=MOM_madays, \
                
            #需要显示SAR
            SAR_day=SAR_day,SAR_madays=SAR_madays, \
                
            #需要显示BETA
            BETA_day=BETA_day,BETA_madays=BETA_madays, \
            
            #需要显示TSF
            TSF_day=TSF_day,TSF_madays=TSF_madays, \
                
            #需要显示AD
            AD_madays=AD_madays, \
            
            indicator=indicator, \
            more_details=more_details)

    #技术指标的绘图线
    tech_line_default={'RSI':['rsi'],
                    'OBV':['obv'],
                    'MACD':['DIF','DEA'],
                    'KDJ':['kdj'],
                    'SAR':['sar'],
                    'VOL':['vol'],
                    'PSY':['psy'],
                    'ARBR':['ar','br'],
                    'CR':['cr'],
                    'EMV':['emv'],
                    'Bollinger':['upper','mid','lower'],
                    'TRIX':['trix'],
                    'BIAS':['bias'],
                    'CCI':['cci'],
                    'W%R':['wr'],
                    'ROC':['roc'],
                    'DMI':['pdi','mdi'],
                    'DMA':['dma'],
                    'MFI':['mfi'],
                    'MOM':['mom'],
                    'BETA':['beta'],
                    'TSF':['tsf'],
                    'AD':['ad'],
                    'MA':['ma'],'EMA':['ema'],
                    }
        
    #检查计算结果：有问题？
    if not calculated:
        print("  #Warning(security_technical2): unsupported technical parameter",technical)
        print("  Supported technical parameters:")
        printlist(sorted(list(tech_line_default.keys())),numperline=11,beforehand='  ',separator=' ')
        return None
    
    #绘图数值缩放比例，以便使指标数量级与股价更加协调
    magnitude_list={'RSI':[1,''],
                    'OBV':[1/1000000,text_lang('百万','in millions')],
                    'MACD':[1,''],
                    'KDJ':[1,''],
                    'SAR':[1,''],
                    'VOL':[1/1000000,text_lang('百万','in millions')],
                    'PSY':[1,''],
                    'ARBR':[1,''],
                    'CR':[1,''],
                    'EMV':[1000000000,text_lang('十亿分之一','in 1 billionth')],
                    'Bollinger':[1,''],
                    'TRIX':[100,text_lang('百分之一','%')],
                    'BIAS':[1,''],
                    'CCI':[1,''],
                    'W%R':[1,''],
                    'ROC':[1,''],
                    'DMI':[1,''],
                    'DMA':[1,''],
                    'MA':[1,''],
                    'EMA':[1,''],
                    'MFI':[1,''],
                    'MOM':[1,''],
                    'BETA':[1,''],
                    'TSF':[1,''],
                    'AD':[1/1000000,text_lang('百万','in millions')],
                    'Volume':[1/1000000,text_lang('百万','in millions')]}

    mag_times=magnitude_list[technical1][0]
    mag_label=magnitude_list[technical1][1]
    
    if  'ALL' in graph or 'all' in graph or 'All' in graph:
        tech_line_prefix=tech_line_default[technical1]
    else:
        if not isinstance(graph,list):
            tech_line_prefix=[graph]
        else:
            tech_line_prefix=graph
        
    tech_line_collist=[]
    df_collist=list(df)
    for p in tech_line_prefix:
        for c in df_collist:
            if p in c:
                tech_line_collist=tech_line_collist+[c]
    #去掉重复项
    tech_line_collist=list(set(tech_line_collist))
    #去掉误选项
    if technical1 == 'ARBR':
        remove_cols=[]; remove_item='sar'
        for c in tech_line_collist:
            if remove_item in c:
                tech_line_collist.remove(c)

    #改变测度
    for c in tech_line_collist:
        df[c]=df[c] * mag_times

    df['Volume']=df['Volume'] * magnitude_list['Volume'][0]
    
    #字段排序
    #tech_line_collist.sort()
    if 'marker_size' in tech_line_collist:
        df1=df[tech_line_collist+[indicator,'Volume','up_down']]
    else: 
        df1=df[tech_line_collist+[indicator,'Volume','up_down','marker_size']]
    
    #绘图----------------------------------------------------------------------
    print('') #距离上条信息空一行
    
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    #import matplotlib.gridspec as gridspec
    
    # 创建两行的布局，上半部分高度为4，下半部分高度为1
    fig = plt.figure(figsize=(14,9))
    
    if isinstance(facecolor,str):
        facecolor1=facecolor2=facecolor
    elif isinstance(facecolor,list):
        if len(facecolor) >= 2:
            facecolor1=facecolor[0]
            facecolor2=facecolor[1]
        elif len(facecolor) == 1:
            facecolor1=facecolor2=facecolor[0]
    else:
        facecolor1='whitesmoke'; facecolor2='papayawhip'
    
    gs = fig.add_gridspec(2, 1, height_ratios=[4, 1], hspace=0.05)
    ax = fig.add_subplot(gs[0])
    try:
        ax.set_facecolor(facecolor1)
    except:
        ax.set_facecolor('whitesmoke')

    ax3 = fig.add_subplot(gs[1], sharex=ax)
    try:
        ax3.set_facecolor(facecolor2)
    except:
        ax3.set_facecolor('papayawhip')
        
    color_list=['k','g','b','c','m','yellowgreen','tomato','lime','orange','deepskyblue']
    
    if isinstance(attention_values,int):
        attention_values=[attention_values]
    attention_draws=[False] * len(attention_values)

    for l in tech_line_collist:
        if l == 'marker_size': continue
        
        labeltxt=l.upper()
        if labeltxt =='DEA':
            labeltxt=text_lang('慢线(DEA)','DEA (Slow line)')
        if labeltxt =='DIF':
            labeltxt=text_lang('快线(DIF)','DIF (Fast line)')            
            
        axline, = ax.plot(df1.index,df1[l],label=labeltxt)
        last_line_color = axline.get_color()
        
        if annotate:
            df_end=df1.tail(1)
            # df_end[c]必须为数值类型，否则可能出错
            y_end = df_end[l].min()    # 末端的y坐标
            x_end = df_end[l].idxmin() # 末端值的x坐标 
            """
            if annotate_value: #在标记曲线名称的同时标记其末端数值
                y1=str(int(y_end)) if abs(y_end) >= 100 else str(round(y_end,2)) if abs(y_end) >= 10 else str(round(y_end,3))
                plt.annotate(text=c+':'+y1, 
                             xy=(x_end, y_end),
                             xytext=(x_end, y_end),color=last_line_color)
            else:
                plt.annotate(text=c, 
                             xy=(x_end, y_end),
                             xytext=(x_end, y_end),color=last_line_color)        
            """
            ax.annotate(text=''+l.upper(), 
                         xy=(x_end, y_end),
                         xytext=(x_end, y_end),color=last_line_color,fontsize=legend_txt_size)        
            
        #判断是否绘制关注线
        lmax=df1[l].max(); lmin=df1[l].min()
        
        for al in attention_values:
            pos=attention_values.index(al)
            
            line_al=False
            if (lmax >= al) and (al >= lmin): 
                line_al=True
            
            #如果需要绘制关注线，且尚未绘制过，则绘制
            if line_al and not attention_draws[pos]:
                ax.axhline(y=attention_values[pos],ls='dotted',c=color_list[pos],linewidth=1)

                attention_draws[pos]=True
        
    ylabeltxt1=technical1+text_lang('指标',' indicators ')
    if mag_label != '':
        ylabeltxt1=ylabeltxt1+'('+mag_label+')'
    ax.set_ylabel(ylabeltxt1,fontsize=ylabel_txt_size)
    
    #对图例项目排序
    if not annotate:
        # 获取图例句柄和标签
        handles, labels = ax.get_legend_handles_labels()
         
        # 指定显示顺序
        labels_sorted = sort_list_by_len(labels,reverse=False)
        handles_sorted = []
        for l in labels_sorted:
            pos=labels.index(l)
            h=handles[pos]
            handles_sorted =handles_sorted +[h]
         
        # 在指定位置添加新的图例，并按照指定顺序显示
        ax.legend(handles=handles_sorted,labels=labels_sorted,loc=loc1,fontsize=legend_txt_size)
        #ax.legend(loc=loc1,fontsize=legend_txt_size)
    
    interval=int(len(df1)/10)+1
    ax.xaxis.set_major_locator(mdates.DayLocator(interval=interval))  # 隔interval天一个标记
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    #ax.autoscale_view()

    #区分涨跌颜色：红涨绿跌
    df1up=df1[df1['up_down'] >= 0]
    df1down=df1[df1['up_down'] < 0]

    #绘制收盘价
    if isinstance(price_line_color,str):
        price_line_color1=price_line_color2=price_line_color
    elif isinstance(price_line_color,list):
        if len(price_line_color) >= 2:
            price_line_color1=price_line_color[0]
            price_line_color2=price_line_color[1]
        elif len(price_line_color) == 1:
            price_line_color1=price_line_color2=price_line_color[0]
    else:
        price_line_color1='red'; price_line_color2='green'

    import numpy as np 
    df1['segment'] = (np.sign(df1['up_down'].shift(1)) != np.sign(df1['up_down'])).cumsum()
    seg_list=list(set(list(df1['segment'])))
    
    ax2 = ax.twinx()
    ylabeltxt2=ectranslate(indicator)
    ax2.set_ylabel(ylabeltxt2,fontsize=ylabel_txt_size)

    #细灰线先画出轮廓
    ax2.plot(df1.index,df1[indicator],label=ylabeltxt2, \
             linestyle=price_line_style,color='k',lw=2)   

    #不同颜色绘制涨跌价格线
    first_time=True; second_time=False
    for seg in seg_list:
        df1seg=df1[df1['segment']==seg]
        if df1seg['up_down'].values[0] >=0:
            seg_color=price_line_color1
            #labeltxt=ylabeltxt2+'(当日↑)'
            #labeltxt=ylabeltxt2+'(当日阳线)'
            labeltxt=text_lang('当日↑','Bullish day')
        else:
            seg_color=price_line_color2
            #labeltxt=ylabeltxt2+'(当日↓)'
            #labeltxt=ylabeltxt2+'(当日阴线)'
            labeltxt=text_lang('当日↓','Bearish day')
            
        if first_time:
            first_time=False; second_time=True
        elif second_time:
            second_time=False
        else:
            labeltxt=''
            
        ax2.scatter(df1seg.index,df1seg[indicator], \
                    s=df1seg['marker_size'], \
                    label=labeltxt, \
                    linestyle=':',color=seg_color,lw=price_line_width,marker=price_line_marker,alpha=0.5)   
    
    ax2.legend(loc=loc2,fontsize=legend_txt_size)
    
    #绘制交易量柱状图
    ax3.bar(df1up.index,df1up['Volume'],color=price_line_color1)
    ax3.bar(df1down.index,df1down['Volume'],color=price_line_color2)
    
    ax3.set_ylabel(text_lang("交易量(百万股)","Volume (in millions)"),fontsize=ylabel_txt_size -4)
    
    footnote1=text_lang("\n注：","\nNote: ")
    footnote2=text_lang("价格曲线端点大中小对应当日涨跌幅度的高中低情形。","The node sizes in curve refelct the amplitudes of close-open price changes in a day\n")
    footnote3=text_lang("横轴日期上的空白处为非交易日。\n","The blank areas of bars are non-trading days. ")
    
    import datetime; todaydt = str(datetime.date.today())
    footnote4=text_lang("数据来源：新浪/Stooq/Yahoo等，","Data source: Sina/Stooq/Yahoo, ")+todaydt+text_lang("统计",'')
    
    footnote=footnote1+footnote2+footnote3+footnote4
    ax3.set_xlabel(footnote,fontsize=ylabel_txt_size -2)
    
    #fig.text(0.5, 0.04, 'x', ha='center')
    plt.subplots_adjust(hspace=0.2)
    
    titletxt=ticker_name(ticker)+': '+text_lang(tech_list[technical1]+technical1,technical1+' ('+tech_list[technical1]+')')
    plt.title(titletxt,fontweight='bold',fontsize=title_txt_size)
    
    plt.gcf().autofmt_xdate()
    #fig.autofmt_xdate()
    
    plt.show(); plt.close()
    
    return df


#==============================================================================
#==============================================================================
#==============================================================================    

    