# -*- coding: utf-8 -*-
"""
本模块功能：期权定价理论计算函数包
所属工具包：证券投资分析工具SIAT 
SIAT：Security Investment Analysis Tool
创建日期：2020年7月16日
最新修订日期：2020年8月5日
作者：王德宏 (WANG Dehong, Peter)
作者单位：北京外国语大学国际商学院
作者邮件：wdehong2000@163.com
版权所有：王德宏
用途限制：仅限研究与教学使用，不可商用！商用需要额外授权。
特别声明：作者不对使用本工具进行证券投资导致的任何损益负责！
"""
#==============================================================================
#统一屏蔽一般性警告
import warnings; warnings.filterwarnings("ignore")    
from siat.common import *
from siat.translate import *
from siat.grafix import *
from siat.security_prices import *
from siat.security_trend2 import *
from siat.yf_name import *
#==============================================================================
import matplotlib.pyplot as plt

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
    direction='call'


def bs_pricing(S0,X,Days,r0,sigma,direction='call',printout=True):
    """
    功能：计算无红利支付的欧式期权B-S定价模型，默认看涨期权
    注意：
    S0：标的物资产的当前价格，X为其行权价
    sigma：标的物资产价格收益率的年化标准差
    r0：年化无风险利率（程序中会转化为连续计算的无风险利率）
    Days：距离到期日的天数（程序中会转换为距离到期日的年数=距离到期日的天数/365）
    """
    
    direction=direction.upper()
    
    if direction=='CALL':
       C0=bs_call(S0,X,Days,r0,sigma,printout=printout) 
    else:
       C0=bs_put(S0,X,Days,r0,sigma,printout=printout) 
    
    
    return C0
    
#==============================================================================

def bs_call(S0,X,Days,r0,sigma,printout=True):
    """
    功能：计算无红利支付的欧式期权B-S定价模型，看涨期权
    注意：
    S0：标的物资产的当前价格，X为其行权价
    sigma：标的物资产价格收益率的年化标准差
    r0：年化无风险利率（需要转化为连续计算的无风险利率）
    Days：距离到期日的天数，需要转换为距离到期日的年数=距离到期日的天数/365
    """
    from scipy import stats
    from numpy import log,exp,sqrt
    
    #Days为距离到期日的日历日天数
    T=Days/365.
    r=log(r0+1)
    
    d1=(log(S0/X)+(r+sigma*sigma/2.)*T)/(sigma*sqrt(T))
    d2=d1-sigma*sqrt(T)
    
    C0=S0*stats.norm.cdf(d1)-X*exp(-r*T)*stats.norm.cdf(d2)
    
    if not printout: return C0
    print("\n===== Black-Scholes期权定价 =====")
    print("适用情形： 欧式期权，标的资产无红利收益")
    print("标的资产行权价:",X)
    print("标的资产现价  :",S0)
    print("标的资产的年化波动率:",round(sigma,4))    
    print("距离到期日的年数    :",round(T,4))
    print("连续计算的无风险利率:",round(r*100,4),'\b%')
    print("看涨期权的预期价格  :",round(C0,4))
    
    return C0
    
if __name__=='__main__':
    S0=40
    X=42
    Days=183
    r0=0.03
    sigma=0.02
    C0=bs_call(40,42,183,0.015,0.02)

#==============================================================================
def bsm_call(S0,X,Days,r0,sigma,Days1=0,div1=0,printout=True):
    """
    功能：计算有红利支付的欧式期权B-S定价模型，看涨期权
    注意：
    S0：标的物资产的当前价格，X为其行权价
    sigma：标的物资产价格收益率的年化标准差
    r0：年化无风险利率（需要转化为连续计算的无风险利率）
    Days：距离到期日的天数，需要转换为距离到期日的年数=距离到期日的天数/365
    Days1：红利发放时距离到期日的天数，需要转换为年数
    div1：红利金额
    """
    from numpy import log,exp
    #Days1为距离到期日的日历日天数
    T=Days/365.
    T1=Days1/365.
    r=log(r0+1)    
    #调整标的物当前价
    S=S0-exp(-r*T1)*div1
    
    #调用BS模型计算
    C=bs_call(S,X,Days,r0,sigma,printout=False)

    if not printout: return C
    print("\n=== Black-Scholes-Merton期权定价 ===")
    print("适用情形： 欧式期权，标的资产有红利收益")
    print("标的资产行权价:",X)
    print("标的资产现价  :",S0)
    print("标的资产的年化波动率  :",round(sigma,4))    
    print("距离到期日的年数      :",round(T,4))
    print("连续计算的无风险利率  :",round(r,4)*100,'\b%')    
    print("红利及距离到期日的年数:",div1,"@",round(T1,4))
    print("看涨期权的预期价格    :",round(C,4))
    
    return C
    
if __name__=='__main__':
    S0=42
    X=40
    Days=183
    r0=0.03
    sigma=0.02
    dv1=1.5
    Days1=183
    C=bsm_call(42,40,183,0.015,0.02,183,1.5)
    C0=bsm_call(42,40,183,0.015,0.23)

#==============================================================================
def bs_put(S0,X,Days,r0,sigma,printout=True):
    """
    功能：计算无红利支付的欧式期权B-S定价模型，看跌期权
    注意：
    S0：标的物资产的当前价格，X为其行权价
    sigma：标的物资产价格收益率的年化标准差
    r0：年化无风险利率（需要转化为连续计算的无风险利率）
    Days：距离到期日的天数，需要转换为距离到期日的年数=距离到期日的天数/365
    """
    from scipy import stats
    from numpy import log,exp,sqrt
    
    #Days为距离到期日的日历日天数
    T=Days/365.
    r=log(r0+1)
    
    d1=(log(S0/X)+(r+sigma*sigma/2.)*T)/(sigma*sqrt(T))
    d2=d1-sigma*sqrt(T)
    
    P0=-S0*stats.norm.cdf(-d1)+X*exp(-r*T)*stats.norm.cdf(-d2)

    if not printout: return P0
    print("\n===== Black-Scholes期权定价 =====")
    print("适用情形： 欧式期权，标的资产无红利收益")
    print("标的资产行权价:",X)
    print("标的资产现价  :",S0)
    print("标的资产的年化波动率:",round(sigma,4))    
    print("距离到期日的年数    :",round(T,4))
    print("连续计算的无风险利率:",round(r*100,4),'\b%')
    print("看跌期权的预期价格  :",round(P0,4))
    
    return P0
    
if __name__=='__main__':
    S0=40
    X=42
    Days=183
    r0=0.03
    sigma=0.02
    P0=bs_put(40,42,183,0.015,0.02)    

#==============================================================================
def bsm_put(S0,X,Days,r0,sigma,Days1=0,div1=0,printout=True):
    """
    功能：计算有红利支付的欧式期权B-S定价模型，看跌期权
    注意：
    S0：标的物资产的当前价格，X为其行权价
    sigma：标的物资产价格收益率的年化标准差
    r0：年化无风险利率（需要转化为连续计算的无风险利率）
    Days：距离到期日的天数，需要转换为距离到期日的年数=距离到期日的天数/365
    Days1：红利发放时距离到期日的天数，需要转换为年数
    div1：红利金额
    """
    from numpy import log,exp,sqrt
    
    #Days为距离到期日的日历日天数
    T=Days/365.
    T1=Days1/365.
    r=log(r0+1)
    
    S=S0-exp(-r*T1)*div1
    
    #调用BS模型计算
    P=bs_put(S,X,Days,r0,sigma,printout=False)

    if not printout: return P
    print("\n=== Black-Scholes-Merton期权定价 ===")
    print("适用情形： 欧式期权，标的资产有红利收益")
    print("标的资产行权价:",X)
    print("标的资产现价  :",S0)
    print("标的资产的年化波动率  :",round(sigma,4))    
    print("距离到期日的年数      :",round(T,4))
    print("连续计算的无风险利率  :",round(r,4)*100,'\b%')
    print("红利及距离到期日的年数:",div1,"@",round(T1,2))
    print("看跌期权的预期价格    :",round(P,4))
    
    return P
    
if __name__=='__main__':
    S0=42
    X=40
    Days=183
    r0=0.03
    sigma=0.02
    P=bsm_put(42,40,183,0.015,0.23,90,1.5)   
    P0=bsm_put(42,40,183,0.015,0.23)

#==============================================================================
def bsm_put_aprice(Srange,X,Days,r0,sigma,Days1=0,div1=0,graph=True):
    """
    功能：计算有红利支付的欧式期权BSM定价模型，看跌期权，当前价格为变化范围
    注意：
    Srange：标的物资产的当前价格范围，默认20等分后作为横轴绘图
    X：期权的行权价
    sigma：标的物资产价格收益率的年化标准差
    r0：年化无风险利率（需要转化为连续计算的无风险利率）
    Days：距离到期日的天数，需要转换为距离到期日的年数=距离到期日的天数/365
    Days1：红利发放时距离到期日的天数，需要转换为年数
    div1：红利金额
    """
    #通用修改点
    trange=Srange
    #检查是否为列表
    if not isinstance(trange,list):
        print("#Error(bsm_put_aprice): target is not a range,",trange)
        return
    if len(trange) < 2:
        print("#Error(bsm_put_aprice): not enough range for target,",trange)
        return        
    
    #确定起始位置和间隔大小
    tstart=trange[0]; tend=trange[1]
    if len(trange) >=3: tstep=trange[2]    
    else: tstep=(tend-tstart)/20.
    #横轴点列表
    import numpy as np
    tlist=np.arange(tstart,tend+tstep,tstep)

    #循环计算各点数值
    import pandas as pd
    df=pd.DataFrame(columns=['Option Price','Asset Price','Strike Price', \
                             'Days to Maturity','Annual RF', \
                             'Annual Sigma','Div to Maturity','Dividend'])
    for t in tlist:
        #通用修改点
        op=bsm_put(t,X,Days,r0,sigma,Days1,div1,printout=False)
        s=pd.Series({'Option Price':op,'Asset Price':t,'Strike Price':X, \
                     'Days to Maturity':Days,'Annual RF':r0, \
                     'Annual Sigma':sigma,'Div to Maturity':Days1, \
                     'Dividend':div1})
        try:
            df=df.append(s,ignore_index=True)
        except:
            df=df._append(s,ignore_index=True)
    #通用修改点
    df2=df.set_index(['Asset Price'])  
    if not graph: return df2      
    
    #绘图
    #通用修改点
    colname='Option Price'; collabel='看跌期权'
    ylabeltxt='期权价格'
    titletxt='期权价格的变化趋势图'
    #通用修改点
    fn1='标的物市场价格'
    fn2='\n[期权信息]行权价='+str(X)+', 距离到期天数='+str(Days)
    fn3='\n年化无风险利率%='+str(round(r0*100.,2))+', 年化波动率%='+str(round(sigma*100.,2))
    if div1==0:
        fn4='\n本产品无红利收益'
    else:
        fn4='\n发放红利时间距离到期天数='+str(Days1)+', 红利='+str(div1)
    footnote=fn1+fn2+fn3+fn4
    plot_line(df2,colname,collabel,ylabeltxt,titletxt,footnote)
    
    return df2
    
if __name__=='__main__':
    Srange=[30,50,1]
    X=40
    Days=183
    r0=0.03
    sigma=0.02
    Days1=0
    div1=0
    pdf=bsm_put_aprice(Srange,40,183,0.015,0.23,90,1.5)    

#==============================================================================
def bsm_call_aprice(Srange,X,Days,r0,sigma,Days1=0,div1=0,graph=True):
    """
    功能：计算有红利支付的欧式期权BSM定价模型，看涨期权，当前价格为变化范围
    注意：
    Srange：标的物资产的当前价格范围，默认20等分后作为横轴绘图
    X：期权的行权价
    sigma：标的物资产价格收益率的年化标准差
    r0：年化无风险利率（需要转化为连续计算的无风险利率）
    Days：距离到期日的天数，需要转换为距离到期日的年数=距离到期日的天数/365
    Days1：红利发放时距离到期日的天数，需要转换为年数
    div1：红利金额
    """
    #通用修改点
    trange=Srange
    #检查是否为列表
    if not isinstance(trange,list):
        print("#Error(bsm_call_aprice): target is not a range,",trange)
        return
    if len(trange) < 2:
        print("#Error(bsm_call_aprice): not enough range for target,",trange)
        return        
    
    #确定起始位置和间隔大小
    tstart=trange[0]; tend=trange[1]
    if len(trange) >=3: tstep=trange[2]    
    else: tstep=(tend-tstart)/20.
    #横轴点列表
    import numpy as np
    tlist=np.arange(tstart,tend+tstep,tstep)

    #循环计算各点数值
    import pandas as pd
    df=pd.DataFrame(columns=['Option Price','Asset Price','Strike Price', \
                             'Days to Maturity','Annual RF', \
                             'Annual Sigma','Div to Maturity','Dividend'])
    for t in tlist:
        #通用修改点
        op=bsm_call(t,X,Days,r0,sigma,Days1,div1,printout=False)
        s=pd.Series({'Option Price':op,'Asset Price':t,'Strike Price':X, \
                     'Days to Maturity':Days,'Annual RF':r0, \
                     'Annual Sigma':sigma,'Div to Maturity':Days1, \
                     'Dividend':div1})
        try:
            df=df.append(s,ignore_index=True)
        except:
            df=df._append(s,ignore_index=True)
    #通用修改点
    df2=df.set_index(['Asset Price'])  
    if not graph: return df2      
    
    #绘图
    #通用修改点
    colname='Option Price'; collabel='看涨期权'
    ylabeltxt='期权价格'
    titletxt='期权价格的变化趋势图'
    #通用修改点
    fn1='标的物市场价格'
    fn2='\n[期权信息]行权价='+str(X)+', 距离到期天数='+str(Days)
    fn3='\n年化无风险利率%='+str(round(r0*100.,2))+', 年化波动率%='+str(round(sigma*100.,2))
    if div1==0:
        fn4='\n本产品无红利收益'
    else:
        fn4='\n发放红利时间距离到期天数='+str(Days1)+', 红利='+str(div1)
    footnote=fn1+fn2+fn3+fn4
    plot_line(df2,colname,collabel,ylabeltxt,titletxt,footnote)
    
    return df2
    
if __name__=='__main__':
    Srange=[30,50,1]
    X=40
    Days=183
    r0=0.03
    sigma=0.02
    Days1=0
    div1=0
    cdf=bsm_call_aprice(Srange,40,183,0.015,0.23,90,1.5)    

#==============================================================================
def bsm_aprice(Srange,X,Days,r0,sigma,Days1=0,div1=0,graph=True):
    """
    功能：计算有红利支付的欧式期权BSM定价模型，看涨/看跌期权，当前价格为变化范围
    注意：
    Srange：标的物资产的当前价格范围，默认20等分后作为横轴绘图
    X：期权的行权价
    sigma：标的物资产价格收益率的年化标准差
    r0：年化无风险利率（需要转化为连续计算的无风险利率）
    Days：距离到期日的天数，需要转换为距离到期日的年数=距离到期日的天数/365
    Days1：红利发放时距离到期日的天数，需要转换为年数
    div1：红利金额
    """
    #通用修改点
    trange=Srange
    #检查是否为列表
    if not isinstance(trange,list):
        print("#Error(bsm_aprice): target is not a range,",trange)
        return
    if len(trange) < 2:
        print("#Error(bsm_aprice): not enough range for target,",trange)
        return        
    
    #看涨期权
    df1=bsm_call_aprice(Srange,X,Days,r0,sigma,Days1=0,div1=0,graph=False)
    #看跌期权
    df2=bsm_put_aprice(Srange,X,Days,r0,sigma,Days1=0,div1=0,graph=False)     
    
    #绘图
    #通用修改点
    ticker1='看涨期权'; colname1='Option Price'; label1='期权-C-'+str(X)
    ticker2='看跌期权'; colname2='Option Price'; label2='期权-P-'+str(X)
    ylabeltxt='期权价格'
    titletxt='期权价格的变化趋势图'
    #通用修改点
    fn1='标的物市场价格-->'
    fn2='\n[期权信息]行权价='+str(X)+', 距离到期天数='+str(Days)
    fn3='\n年化无风险利率%='+str(round(r0*100.,2))+', 年化波动率%='+str(round(sigma*100.,2))
    if div1==0:
        fn4='\n本产品无红利收益'
    else:
        fn4='\n发放红利时间距离到期天数='+str(Days1)+', 红利='+str(div1)
    footnote=fn1+fn2+fn3+fn4
    plot_line2_coaxial(df1,ticker1,colname1,label1, \
                       df2,ticker2,colname2,label2, \
                    ylabeltxt,titletxt,footnote)
    return
    
if __name__=='__main__':
    Srange=[30,50,1]
    X=40
    Days=183
    r0=0.03
    sigma=0.02
    Days1=0
    div1=0
    bsm_aprice(Srange,40,183,0.015,0.23,90,1.5)  
    bsm_aprice([30,50],40,183,0.015,0.23,90,1.5)  

#==============================================================================
def bsm_put_maturity(S0,X,Dayrange,r0,sigma,Days1=0,div1=0,graph=True):
    """
    功能：计算有红利支付的欧式期权BSM定价模型，看跌期权，距离到期日天数为变化范围
    注意：
    S0：标的物资产的当前价格
    X：期权的行权价
    sigma：标的物资产价格收益率的年化标准差
    r0：年化无风险利率（需要转化为连续计算的无风险利率）
    Dayrange：距离到期日的天数范围，默认变化间隔为20分之一取整
    Days1：红利发放时距离到期日的天数，需要转换为年数
    div1：红利金额
    """
    #通用修改点
    trange=Dayrange
    #检查是否为列表
    if not isinstance(trange,list):
        print("#Error(bsm_put_maturity): target is not a range,",trange)
        return
    if len(trange) < 2:
        print("#Error(bsm_put_maturity): not enough range for target,",trange)
        return        
    
    #确定起始位置和间隔大小
    tstart=int(trange[0]); tend=int(trange[1])
    if len(trange) >=3: tstep=trange[2]    
    else: tstep=int((tend-tstart)/20)
    #横轴点列表
    #import numpy as np
    tlist=range(tstart,tend+tstep,tstep)

    #循环计算各点数值
    import pandas as pd
    df=pd.DataFrame(columns=['Option Price','Asset Price','Strike Price', \
                             'Days to Maturity','Annual RF', \
                             'Annual Sigma','Div to Maturity','Dividend'])
    for t in tlist:
        #通用修改点
        op=bsm_put(S0,X,t,r0,sigma,Days1,div1,printout=False)
        s=pd.Series({'Option Price':op,'Asset Price':S0,'Strike Price':X, \
                     'Days to Maturity':t,'Annual RF':r0, \
                     'Annual Sigma':sigma,'Div to Maturity':Days1, \
                     'Dividend':div1})
        try:
            df=df.append(s,ignore_index=True)
        except:
            df=df._append(s,ignore_index=True)
    #通用修改点
    df2=df.set_index(['Days to Maturity'])  
    if not graph: return df2      
    
    #绘图
    #通用修改点
    colname='Option Price'; collabel='看跌期权'
    ylabeltxt='期权价格'
    titletxt='期权价格的变化趋势图'
    #通用修改点
    fn1='<--距离到期日的天数'
    fn2='\n[期权信息]行权价='+str(X)+', 标的物市价='+str(S0)
    fn3='\n年化无风险利率%='+str(round(r0*100.,2))+', 年化波动率%='+str(round(sigma*100.,2))
    if div1==0:
        fn4='\n本产品无红利收益'
    else:
        fn4='\n发放红利时间距离到期天数='+str(Days1)+', 红利='+str(div1)
    footnote=fn1+fn2+fn3+fn4
    plot_line(df2,colname,collabel,ylabeltxt,titletxt,footnote)
    
    return df2
    
if __name__=='__main__':
    S0=42
    X=40
    Dayrange=[200,50]
    r0=0.015
    sigma=0.23
    Days1=90
    div1=1.5
    pdf=bsm_put_maturity(42,40,[200,50],0.015,0.23,90,1.5)    

#==============================================================================
def bsm_call_maturity(S0,X,Dayrange,r0,sigma,Days1=0,div1=0,graph=True):
    """
    功能：计算有红利支付的欧式期权BSM定价模型，看涨期权，距离到期日天数为变化范围
    注意：
    S0：标的物资产的当前价格
    X：期权的行权价
    sigma：标的物资产价格收益率的年化标准差
    r0：年化无风险利率（需要转化为连续计算的无风险利率）
    Dayrange：距离到期日的天数范围，默认变化间隔为20分之一取整
    Days1：红利发放时距离到期日的天数，需要转换为年数
    div1：红利金额
    """
    #通用修改点
    trange=Dayrange
    #检查是否为列表
    if not isinstance(trange,list):
        print("#Error(bsm_call_maturity): target is not a range,",trange)
        return
    if len(trange) < 2:
        print("#Error(bsm_call_maturity): not enough range for target,",trange)
        return        
    
    #确定起始位置和间隔大小
    tstart=int(trange[0]); tend=int(trange[1])
    if len(trange) >=3: tstep=trange[2]    
    else: tstep=int((tend-tstart)/20)
    #横轴点列表
    #import numpy as np
    tlist=range(tstart,tend+tstep,tstep)

    #循环计算各点数值
    import pandas as pd
    df=pd.DataFrame(columns=['Option Price','Asset Price','Strike Price', \
                             'Days to Maturity','Annual RF', \
                             'Annual Sigma','Div to Maturity','Dividend'])
    for t in tlist:
        #通用修改点
        op=bsm_call(S0,X,t,r0,sigma,Days1,div1,printout=False)
        s=pd.Series({'Option Price':op,'Asset Price':S0,'Strike Price':X, \
                     'Days to Maturity':t,'Annual RF':r0, \
                     'Annual Sigma':sigma,'Div to Maturity':Days1, \
                     'Dividend':div1})
        try:
            df=df.append(s,ignore_index=True)
        except:
            df=df._append(s,ignore_index=True)
    #通用修改点
    df2=df.set_index(['Days to Maturity'])  
    if not graph: return df2      
    
    #绘图
    #通用修改点
    colname='Option Price'; collabel='看涨期权'
    ylabeltxt='期权价格'
    titletxt='期权价格的变化趋势图'
    #通用修改点
    fn1='<--距离到期日的天数'
    fn2='\n[期权信息]行权价='+str(X)+', 标的物市价='+str(S0)
    fn3='\n年化无风险利率%='+str(round(r0*100.,2))+', 年化波动率%='+str(round(sigma*100.,2))
    if div1==0:
        fn4='\n本产品无红利收益'
    else:
        fn4='\n发放红利时间距离到期天数='+str(Days1)+', 红利='+str(div1)
    footnote=fn1+fn2+fn3+fn4
    plot_line(df2,colname,collabel,ylabeltxt,titletxt,footnote)
    
    return df2
    
if __name__=='__main__':
    S0=42
    X=40
    Dayrange=[200,50]
    r0=0.015
    sigma=0.23
    Days1=90
    div1=1.5
    cdf=bsm_call_maturity(42,40,[200,50],0.015,0.23,90,1.5)    

#==============================================================================
if __name__=='__main__':
    S0=42
    X=40
    Dayrange=[200,50]
    r0=0.015
    sigma=0.23
    Days1=90
    div1=1.5

def bsm_maturity(S0,X,Dayrange,r0,sigma,Days1=0,div1=0,graph=True):
    """
    功能：计算有红利支付的欧式期权BSM定价模型，看涨/看跌期权，距离到期日天数为变化范围
    注意：
    S0：标的物资产的当前价格
    X：期权的行权价
    sigma：标的物资产价格收益率的年化标准差
    r0：年化无风险利率（需要转化为连续计算的无风险利率）
    Dayrange：距离到期日的天数范围，默认间隔为20分之一取证
    Days1：红利发放时距离到期日的天数，需要转换为年数
    div1：红利金额
    """
    #通用修改点
    trange=Dayrange
    #检查是否为列表
    if not isinstance(trange,list):
        print("#Error(bsm_maturity): target is not a range,",trange)
        return
    if len(trange) < 2:
        print("#Error(bsm_maturity): not enough range for target,",trange)
        return        
    
    #看涨期权
    df1=bsm_call_maturity(S0,X,Dayrange,r0,sigma,Days1=0,div1=0,graph=False)
    df1.sort_index(ascending=False, inplace=True)
    #看跌期权
    df2=bsm_put_maturity(S0,X,Dayrange,r0,sigma,Days1=0,div1=0,graph=False)
    df2.sort_index(ascending=False, inplace=True)  
    #合并
    import pandas as pd
    df=pd.merge(df1,df2,how='inner',left_index=True,right_index=True,sort=True)
    #df['到期日']=df.index
    #df.sort_values('到期日',ascending=False,inplace=True)
    
    #绘图    
    plt.title('期权价格的变化趋势图')
    plt.ylabel('期权价格')
    
    df['Option Price_x'].plot(label='看涨期权',ls='-')
    df['Option Price_y'].plot(label='看跌期权',ls='-.')
    
    fn1='距离到期日的天数-->'
    fn2='\n[期权信息]行权价='+str(X)+', 标的物市价='+str(S0)
    fn3='\n年化无风险利率%='+str(round(r0*100.,2))+', 年化波动率%='+str(round(sigma*100.,2))
    if div1==0: fn4='\n本产品无红利收益'
    else: fn4='\n发放红利时间距离到期天数='+str(Days1)+', 红利='+str(div1)
    footnote=fn1+fn2+fn3+fn4
    plt.xlabel(footnote)  
    
    #让横轴逆序从大到小显示，正常顺序为从小到大
    plt.gca().invert_xaxis()
    plt.legend()
    
    plt.gca().set_facecolor('whitesmoke')
    plt.show()    
    
    return
    
if __name__=='__main__':
    S0=42
    X=40
    Dayrange=[200,50]
    r0=0.015
    sigma=0.23
    Days1=90
    div1=1.5
    bsm_maturity(S0,40,[200,5],0.015,0.23,90,1.5)  
    bsm_maturity(42,40,[50,200],0.015,0.23,90,1.5)  

#==============================================================================
def bsm_put_sigma(S0,X,Days,r0,sigmarange,Days1=0,div1=0,graph=True):
    """
    功能：计算有红利支付的欧式期权BSM定价模型，看跌期权，年化波动率为变化范围
    注意：
    S0：标的物资产的当前价格
    X：期权的行权价
    sigmarange：标的物资产价格收益率的年化标准差范围，默认为区间的20分之一作为间隔
    r0：年化无风险利率（需要转化为连续计算的无风险利率）
    Days：距离到期日的天数
    Days1：红利发放时距离到期日的天数，需要转换为年数
    div1：红利金额
    """
    #通用修改点
    trange=sigmarange
    #检查是否为列表
    if not isinstance(trange,list):
        print("#Error(bsm_put_sigma): target is not a range,",trange)
        return
    if len(trange) < 2:
        print("#Error(bsm_put_sigma): not enough range for target,",trange)
        return        
    
    #确定起始位置和间隔大小
    tstart=trange[0]; tend=trange[1]
    if len(trange) >=3: tstep=trange[2]    
    else: tstep=(tend-tstart)/20.
    #横轴点列表
    import numpy as np
    tlist=np.arange(tstart,tend+tstep,tstep)

    #循环计算各点数值
    import pandas as pd
    df=pd.DataFrame(columns=['Option Price','Asset Price','Strike Price', \
                             'Days to Maturity','Annual RF', \
                             'Annual Sigma','Div to Maturity','Dividend'])
    for t in tlist:
        #通用修改点
        op=bsm_put(S0,X,Days,r0,t,Days1,div1,printout=False)
        s=pd.Series({'Option Price':op,'Asset Price':S0,'Strike Price':X, \
                     'Days to Maturity':Days,'Annual RF':r0, \
                     'Annual Sigma':t,'Div to Maturity':Days1, \
                     'Dividend':div1})
        try:
            df=df.append(s,ignore_index=True)
        except:
            df=df._append(s,ignore_index=True)
    #通用修改点
    df2=df.set_index(['Annual Sigma'])  
    if not graph: return df2      
    
    #绘图
    #通用修改点
    colname='Option Price'; collabel='看跌期权'
    ylabeltxt='期权价格'
    titletxt='期权价格的变化趋势图'
    #通用修改点
    fn1='波动率-->'
    fn2='\n[期权信息]行权价='+str(X)+', 标的物市价='+str(S0)
    fn3='\n年化无风险利率%='+str(round(r0*100.,2))+', 距离到期日天数='+str(Days)
    if div1==0:
        fn4='\n本产品无红利收益'
    else:
        fn4='\n发放红利时间距离到期天数='+str(Days1)+', 红利='+str(div1)
    footnote=fn1+fn2+fn3+fn4
    plot_line(df2,colname,collabel,ylabeltxt,titletxt,footnote)
    
    return df2
    
if __name__=='__main__':
    S0=42
    X=40
    Days=183
    r0=0.015
    sigmarange=[0.1,0.4]
    Days1=90
    div1=1.5
    pdf=bsm_put_sigma(42,40,183,0.015,[0.1,0.4],90,1.5)    


#==============================================================================
def bsm_call_sigma(S0,X,Days,r0,sigmarange,Days1=0,div1=0,graph=True):
    """
    功能：计算有红利支付的欧式期权BSM定价模型，看涨期权，年化波动率为变化范围
    注意：
    S0：标的物资产的当前价格
    X：期权的行权价
    sigmarange：标的物资产价格收益率的年化标准差范围，默认为区间的20分之一作为间隔
    r0：年化无风险利率（需要转化为连续计算的无风险利率）
    Days：距离到期日的天数
    Days1：红利发放时距离到期日的天数，需要转换为年数
    div1：红利金额
    """
    #通用修改点
    trange=sigmarange
    #检查是否为列表
    if not isinstance(trange,list):
        print("#Error(bsm_call_sigma): target is not a range,",trange)
        return
    if len(trange) < 2:
        print("#Error(bsm_call_sigma): not enough range for target,",trange)
        return        
    
    #确定起始位置和间隔大小
    tstart=trange[0]; tend=trange[1]
    if len(trange) >=3: tstep=trange[2]    
    else: tstep=(tend-tstart)/20.
    #横轴点列表
    import numpy as np
    tlist=np.arange(tstart,tend+tstep,tstep)

    #循环计算各点数值
    import pandas as pd
    df=pd.DataFrame(columns=['Option Price','Asset Price','Strike Price', \
                             'Days to Maturity','Annual RF', \
                             'Annual Sigma','Div to Maturity','Dividend'])
    for t in tlist:
        #通用修改点
        op=bsm_call(S0,X,Days,r0,t,Days1,div1,printout=False)
        s=pd.Series({'Option Price':op,'Asset Price':S0,'Strike Price':X, \
                     'Days to Maturity':Days,'Annual RF':r0, \
                     'Annual Sigma':t,'Div to Maturity':Days1, \
                     'Dividend':div1})
        try:
            df=df.append(s,ignore_index=True)
        except:
            df=df._append(s,ignore_index=True)
    #通用修改点
    df2=df.set_index(['Annual Sigma'])  
    if not graph: return df2      
    
    #绘图
    #通用修改点
    colname='Option Price'; collabel='看涨期权'
    ylabeltxt='期权价格'
    titletxt='期权价格的变化趋势图'
    #通用修改点
    fn1='波动率-->'
    fn2='\n[期权信息]行权价='+str(X)+', 标的物市价='+str(S0)
    fn3='\n年化无风险利率%='+str(round(r0*100.,2))+', 距离到期日天数='+str(Days)
    if div1==0:
        fn4='\n本产品无红利收益'
    else:
        fn4='\n发放红利时间距离到期天数='+str(Days1)+', 红利='+str(div1)
    footnote=fn1+fn2+fn3+fn4
    plot_line(df2,colname,collabel,ylabeltxt,titletxt,footnote)
    
    return df2
    
if __name__=='__main__':
    S0=42
    X=40
    Days=183
    r0=0.015
    sigmarange=[0.1,0.4]
    Days1=90
    div1=1.5
    cdf=bsm_call_sigma(42,40,183,0.015,[0.1,0.4],90,1.5)  

#==============================================================================
def bsm_sigma(S0,X,Days,r0,sigmarange,Days1=0,div1=0,graph=True):
    """
    功能：计算有红利支付的欧式期权BSM定价模型，看涨/看跌期权，波动率为变化范围
    注意：
    S0：标的物资产的当前价格
    X：期权的行权价
    sigmarange：标的物资产价格收益率的年化标准差范围
    r0：年化无风险利率（需要转化为连续计算的无风险利率）
    Days：距离到期日的天数
    Days1：红利发放时距离到期日的天数，需要转换为年数
    div1：红利金额
    """
    #通用修改点
    trange=sigmarange
    #检查是否为列表
    if not isinstance(trange,list):
        print("#Error(bsm_sigma): target is not a range,",trange)
        return
    if len(trange) < 2:
        print("#Error(bsm_sigma): not enough range for target,",trange)
        return        
    
    #看涨期权
    df1=bsm_call_sigma(S0,X,Days,r0,sigmarange,Days1=0,div1=0,graph=False)
    df1.sort_index(ascending=True, inplace=True)
    #看跌期权
    df2=bsm_put_sigma(S0,X,Days,r0,sigmarange,Days1=0,div1=0,graph=False)
    df2.sort_index(ascending=True, inplace=True)  
    
    #绘制双线图
    titletxt='期权价格的变化趋势图'
    colname1='Option Price'; label1='看涨期权'
    colname2='Option Price'; label2='看跌期权'
    ylabeltxt='期权价格'
    
    fn1='波动率-->'
    fn2='\n[期权信息]行权价='+str(X)+', 标的物市价='+str(S0)
    fn3='\n年化无风险利率%='+str(round(r0*100.,2))+', 距离到期日天数='+str(Days)
    if div1==0: fn4='\n本产品无红利收益'
    else: fn4='\n发放红利时间距离到期天数='+str(Days1)+', 红利='+str(div1)
    footnote=fn1+fn2+fn3+fn4
    
    plot_2lines(df1,colname1,label1,df2,colname2,label2, \
                ylabeltxt,titletxt,footnote)
    
    return
    
if __name__=='__main__':
    S0=42
    X=40
    Days=183
    r0=0.015
    sigmarange=[0.1,0.4]
    Days1=90
    div1=1.5
    bsm_sigma(42,40,183,0.015,[0.1,0.4],90,1.5)  

#==============================================================================
def iv_call_bsm(aop,S0,X,Days,r0,Days1=0,div1=0,precision=0.01,printout=True):
    """
    功能：基于BSM模型，二分迭代法，计算隐含波动率，看涨期权
    aop：实际期权价格
    S0：标的物当前市价
    X：标的物行权价
    Days：距离到期日的天数
    r0：年华无风险利率
    Days1：预期红利收益发放日期距离到期日的天数，默认=0
    div1：预期红利收益金额，默认=0
    printout：是否显示计算结果，默认=True
    """
    k=1
    volLow=0.001    #设置波动率的最低值
    volHigh=1.0     #设置波动率的最高值
    
    #波动率最低值对应的期权价格
    #cLow=bsCall(S,X,T,r,volLow)
    cLow=bsm_call(S0,X,Days,r0,volLow,Days1,div1,printout=False)
    
    #波动率最高值对应的期权价格
    #cHigh=bsCall(S,X,T,r,volHigh)  
    cHigh=bsm_call(S0,X,Days,r0,volHigh,Days1,div1,printout=False)
    
    #防止出现死循环
    if cLow > aop or cHigh < aop: 
        print("#Error(iv_call_bsm): Option price not reasonable,",aop)
        return None        
        #raise ValueError    
    
    while k ==1:
        #cLow=bsCall(S,X,T,r,volLow)
        cLow=bsm_call(S0,X,Days,r0,volLow,Days1,div1,printout=False)
        #cHigh=bsCall(S,X,T,r,volHigh)
        cHigh=bsm_call(S0,X,Days,r0,volHigh,Days1,div1,printout=False)
        
        #取波动率的高低均值
        volMid=(volLow+volHigh)/2.0
        #cMid=bsCall(S,X,T,r,volMid) 
        cMid=bsm_call(S0,X,Days,r0,volMid,Days1,div1,printout=False)
        
        #满足期权价格误差精度要求（0.01以下）则结束循环
        if abs(cHigh-cLow) < precision: k=2
        #否则，缩小范围，继续循环
        elif cMid>aop: volHigh=volMid
        else: volLow=volMid        
    
    iv=round(volMid,4)
    if not printout: return iv
    
    #显示
    print("\n=== 隐含波动率: 二叉树迭代 ===")
    print("看涨期权:")
    print("  期权现价        :",aop)
    print("  标的资产现价    :",S0)
    print("  标的资产行权价  :",X)
    print("  距离到期日的天数:",Days)
    if not (div1 == 0):
        print("  预期红利                :",div1)
        print("  红利发放距离到期日的天数:",Days1)
    print("隐含波动率:")
    print("  预计的年化波动率  :",iv)
    print("  对应的期权价格范围:",round(cLow,3),'-',round(cHigh,3))
    print("  迭代精度          :",precision)
    return iv

#==============================================================================
def iv_put_bsm(aop,S0,X,Days,r0,Days1=0,div1=0,precision=0.01,printout=True):
    """
    功能：基于BSM模型，二分迭代法，计算隐含波动率，看跌期权
    aop：实际期权价格
    S0：标的物当前市价
    X：标的物行权价
    Days：距离到期日的天数
    r0：年华无风险利率
    Days1：预期红利收益发放日期距离到期日的天数，默认=0
    div1：预期红利收益金额，默认=0
    printout：是否显示计算结果，默认=True
    """
    k=1
    volLow=0.001    #设置波动率的最低值
    volHigh=1.0     #设置波动率的最高值
    
    #波动率最低值对应的期权价格
    #cLow=bsCall(S,X,T,r,volLow)
    cLow=bsm_put(S0,X,Days,r0,volLow,Days1,div1,printout=False)
    
    #波动率最高值对应的期权价格
    #cHigh=bsCall(S,X,T,r,volHigh)  
    cHigh=bsm_put(S0,X,Days,r0,volHigh,Days1,div1,printout=False)
    
    #防止出现死循环
    if cLow > aop or cHigh < aop: 
        print("#Error(iv_put_bsm): Option price not reasonable,",aop)
        return None
        #raise ValueError    
    
    while k ==1:
        #cLow=bsCall(S,X,T,r,volLow)
        cLow=bsm_put(S0,X,Days,r0,volLow,Days1,div1,printout=False)
        #cHigh=bsCall(S,X,T,r,volHigh)
        cHigh=bsm_put(S0,X,Days,r0,volHigh,Days1,div1,printout=False)
        
        #取波动率的高低均值
        volMid=(volLow+volHigh)/2.0
        #cMid=bsCall(S,X,T,r,volMid) 
        cMid=bsm_put(S0,X,Days,r0,volMid,Days1,div1,printout=False)
        
        #满足期权价格误差精度要求（precision）则结束循环
        if abs(cHigh-cLow) < precision: k=2
        #否则，缩小范围，继续循环
        elif cMid>aop: volHigh=volMid
        else: volLow=volMid        
    
    iv=round(volMid,4)
    if not printout: return iv
    
    #显示
    print("\n=== 隐含波动率: 二叉树迭代 ===")
    print("看跌期权:")
    print("  期权现价        :",aop)
    print("  标的资产现价    :",S0)
    print("  标的资产行权价  :",X)
    print("  距离到期日的天数:",Days)
    if not (div1 == 0):
        print("  预期红利                :",div1)
        print("  红利发放距离到期日的天数:",Days1)
    print("隐含波动率:")
    print("  预计的年化波动率  :",iv)
    print("  对应的期权价格范围:",round(cLow,3),'-',round(cHigh,3))
    print("  迭代精度          :",precision)

    return iv

#==============================================================================
def binomial_american_call(S0,X,Days,r0,sigma,q0=0,steps=200,printout=True):
    """
    功能：计算有红利支付的美式期权二叉树定价模型，看涨期权
    注意：
    S0：标的物资产的当前价格
    X为其行权价
    Days：距离到期日的天数，需要转换为距离到期日的年数=距离到期日的天数/365
    r0：年化无风险利率（需要转化为连续计算的无风险利率）
    sigma：标的物资产价格收益率的年化标准差
    q0：年化红利收益率，由于美式期权可能提前行权，故不考虑发放日期
    steps：二叉树的步骤
    """
    from numpy import log,exp
    
    #Days1为距离到期日的日历日天数
    t=Days/365.
    r=log(r0+1)  
    q=log(q0+1)
    #调整标的物当前价
    S=S0    

    import numpy as np
    u=np.exp(sigma*np.sqrt(t/steps)); d=1/u
	
    P=(np.exp((r-q)*t/steps)-d)/(u-d)
    prices=np.zeros(steps+1)
    c_values=np.zeros(steps+1)
    prices[0]=S*d**steps
    c_values[0]=np.maximum(prices[0]-X,0)
	
    for i in range(1,steps+1):
        prices[i]=prices[i-1]*(u**2)
        c_values[i]=np.maximum(prices[i]-X,0)
	
    for j in range(steps,0,-1):
        for i in range(0,j):
            prices[i]=prices[i+1]*d
            #c_values[i]=np.maximum((P*c_values[i+1]+(1-P)*c_values[i])/np.exp(r*t/steps),prices[i]-X)
            c_values[i]=np.maximum((P*c_values[i+1]+(1-P)*c_values[i])/np.exp((r-q)*t/steps),prices[i]-X)
    C=round(c_values[0],2)

    if not printout: return C
    print("\n===== 二叉树期权定价 =====")
    print("适用情形： 美式期权，标的资产有红利")
    print("标的资产行权价        :",X)
    print("标的资产现价          :",S0)
    print("标的资产年化波动率    :",round(sigma,4))    
    print("距离到期日的年数      :",round(t,2))
    print("连续计算的无风险收益率:",round(r,4)*100,'\b%')
    print("连续计算的红利率      :",round(q,4)*100,'\b%')
    print("二叉树迭代步数        :",steps)
    print("看涨期权的预期价格    :",round(C,4))    
    
    return C

#==============================================================================
def binomial_american_put(S0,X,Days,r0,sigma,q0=0,steps=200,printout=True):
    """
    功能：计算有红利支付的美式期权二叉树定价模型，看跌期权
    注意：
    S0：标的物资产的当前价格
    X为其行权价
    Days：距离到期日的天数，需要转换为距离到期日的年数=距离到期日的天数/365
    r0：年化无风险利率（需要转化为连续计算的无风险利率）
    sigma：标的物资产价格收益率的年化标准差
    q0：年化红利收益率，由于美式期权可能提前行权，故不考虑发放日期
    steps：二叉树的步骤
    """
    from numpy import log,exp
    
    #Days1为距离到期日的日历日天数
    t=Days/365.
    r=log(r0+1)  
    q=log(q0+1)
    #调整标的物当前价
    S=S0   
    
    import numpy as np
    u=np.exp(sigma*np.sqrt(t/steps))
    d=1/u
    P=(np.exp((r-q)*t/steps)-d)/(u-d)
    prices=np.zeros(steps+1)
    c_values=np.zeros(steps+1)
    prices[0]=S*d**steps
    c_values[0]=np.maximum(X-prices[0],0)

    for i in range(1,steps+1):
        prices[i]=prices[i-1]*(u**2)
        c_values[i]=np.maximum(X-prices[i],0)

    for j in range(steps,0,-1):
        for i in range(0,j):
            prices[i]=prices[i+1]*d
            #c_values[i]=np.maximum((P*c_values[i+1]+(1-P)*c_values[i])/np.exp(r*t/steps),X-prices[i])#检查是否提前行权
            c_values[i]=np.maximum((P*c_values[i+1]+(1-P)*c_values[i])/np.exp((r-q)*t/steps),X-prices[i])#检查是否提前行权
    C=round(c_values[0],2)

    if not printout: return C
    print("\n===== 二叉树期权定价 =====")
    print("适用情形： 美式期权，标的资产有红利")
    print("标的资产行权价        :",X)
    print("标的资产现价          :",S0)
    print("标的资产年化波动率    :",round(sigma,4))    
    print("距离到期日的年数      :",round(t,2))
    print("连续计算的无风险收益率:",round(r,4)*100,'\b%')
    print("连续计算的红利率      :",round(q,4)*100,'\b%')
    print("二叉树迭代步数        :",steps)
    print("看跌期权的预期价格    :",round(C,4)) 

    return C

#==============================================================================
#==============================================================================
#==============================================================================
#==============================================================================
if __name__=='__main__':
    ticker="AAPL"
    ticker="SPY"

def option_maturity(ticker,printout=True):
    """
    功能：获得期权的各个到期日期
    注意：目前yfinance无法使用，股票期权链功能暂时不可用，可尝试yahooquery？
    """
    """
    if not test_yahoo_access():
        print("  #Warning(option_maturity): failed to access data source Yahoo Finance")
        return None
    """
    import yfinance as yf
    # yf.__version__
    
    opt = yf.Ticker(ticker)
    
    #获得期权的各个到期日
    try:
        exp_dates=opt.options
    except:
        print("  #Error(option_maturity): failed to get option maturity dates for underlying",ticker)
        print("  Reasons: either",ticker,"does not exist or Yahoo Finance is currently inaccessible")
        return None
    
    datelist=list(exp_dates)
    if not printout:
        return datelist
    
    tname=get_stock_name1_en(ticker)
    
    #显示结果
    print("\n===== 期权的时间序列 =====")
    print("标的资产:",tname)
    print("到期日期:")
    
    num=len(datelist)
    for d in datelist:
        print(d,end='  ')
        pos=datelist.index(d)+1
        if (pos % 4 ==0) or (pos==num): print(' ')
    
    print("总计:",num,"个日期")
    import datetime
    today = datetime.date.today()    
    print("\n*** 数据来源: 雅虎财经,",today)
    
    return datelist

if __name__=='__main__':
    ticker='AAPL'
    datelist=option_maturity(ticker)
    datelist=option_maturity('AAPL')
    datelist=option_maturity('000001.SS')

#================================================================
if __name__=='__main__':
    ticker="AAPL"
    maturity_date="2025-2-21"

def option_chain(ticker,maturity_date='today',printout=True):
    """
    功能：获得期权的各个到期日期，并列出某个到期日的期权合约
    """
    mdate=maturity_date
    
    if mdate=='today':
        import datetime as dt; stoday=dt.date.today()
        mdate=str(stoday)
    
    import yfinance as yf
    opt = yf.Ticker(ticker)
            
    #处理称为规范日期
    from datetime import datetime
    mdate2 = datetime.strptime(mdate, '%Y-%m-%d')
    mdate3 = datetime.strftime(mdate2,'%Y-%m-%d')
    
    #获得一个到期日的所有期权合约
    try:
        optlist = opt.option_chain(mdate3)
    except:
        if printout:
            print("  #Error(option_chain): failed to get option chain for",ticker,'\b@',mdate)
        return None,None    
    
    opt_call=optlist.calls
    opt_call['underlyingAsset']=ticker
    opt_call['optionType']='Call'
    
    inttodate=lambda x: int2date(x)
    opt_call['date']=opt_call['lastTradeDate'].apply(inttodate)
    opt_call['maturity']=mdate3
    
    collist=['contractSymbol','underlyingAsset','optionType','date', \
             'maturity','strike','lastPrice','impliedVolatility','volume', \
             'inTheMoney','currency']
    opt_call2=opt_call[collist].copy()
    num_call=len(opt_call2)
    num_call_ITM=len(opt_call2[opt_call2['inTheMoney']==True])
    num_call_OTM=num_call-num_call_ITM
    
    strike_min=min(opt_call2['strike'])
    strike_max=max(opt_call2['strike'])
    currency=opt_call2['currency'][0]
    
    opt_put=optlist.puts
    opt_put['underlyingAsset']=ticker
    opt_put['optionType']='Put'
    opt_put['date']=opt_put['lastTradeDate'].apply(inttodate)
    opt_put['maturity']=mdate3
    opt_put2=opt_put[collist].copy()
    num_put=len(opt_put2)
    num_put_ITM=len(opt_put2[opt_put2['inTheMoney']==True])
    num_put_OTM=num_put-num_put_ITM
    
    if not printout:
        return  opt_call2, opt_put2
    
    tname=get_stock_name1_en(ticker)
    
    print("\n===== 期权链的结构 =====")
    print("标的资产:",tname)
    print("到期日期:",mdate)
    print("看涨期权:",num_call)
    print("    实值/虚值:",num_call_ITM,'/',num_call_OTM)
    print("看跌期权:",num_put)
    print("    实值/虚值:",num_put_ITM,'/',num_put_OTM)
    print("最低/最高行权价:",strike_min,'/',strike_max,currency)
    
    import datetime
    stoday = datetime.date.today()    
    print("\n*数据来源: 雅虎财经,",stoday)
    
    #设置绘图数据
    df1=opt_call2.copy()
    df1.sort_values(by=['strike'],axis=0,ascending=[True],inplace=True) 
    df1.set_index(['strike'],inplace=True)
    df1['exercise']=df1.index
    colname1='lastPrice'; label1='看涨期权价格'
    
    df2=opt_put2.copy()
    df2.sort_values(by=['strike'],axis=0,ascending=[True],inplace=True) 
    df2.set_index(['strike'],inplace=True)
    df2['exercise']=df2.index
    colname2='lastPrice'; label2='看跌期权价格'  
    
    ylabeltxt='期权价格('+currency+')'
    titletxt="期权价格与标的行权价格的关系"
    footnote="标的行权价("+currency+") -->\n"+ \
        "标的资产: "+tname+ \
        ", "+"到期日: "+mdate+ \
        "\n数据来源: 雅虎财经, "+str(stoday)
        
    #绘图        
    import matplotlib.pyplot as plt    
    plt.plot(df1.index,df1[colname1],color='red',linestyle='-',linewidth=1.5, \
             label=label1)        

    plt.plot(df2.index,df2[colname2],color='blue',linestyle='-',linewidth=1.5, \
             label=label2) 
        
    plt.ylabel(ylabeltxt,fontsize=ylabel_txt_size)    
    plt.xlabel(footnote,fontsize=xlabel_txt_size)        
    plt.title(titletxt,fontsize=title_txt_size)        
    plt.legend(fontsize=legend_txt_size)
    plt.show()    

        
    return  opt_call2, opt_put2

if __name__=='__main__':
    ticker='AAPL'    
    mdate='2022-6-17'    
    dfc,dfp=option_chain(ticker,mdate)

#==============================================================================
if __name__ =="__main__":
    ticker='AAPL'
    lastndays=7

#def predict_stock_trend_by_option(ticker,lastndays=7,power=4):
def market_prospect_via_option(ticker,lastdays=7):    
    """
    功能：根据期权行权价及交易量预测标的物价格
    注意：本函数与price_prospect_via_option内容基本一致，图示方式略有不同
    """
    lastndays=lastdays
    
    DEBUG=False
    try:
        datelist=option_maturity(ticker,printout=False)
    except:
        print("  #Error(predict_stock_price_by_option): option info not found for",ticker)
    if datelist is None:
        print("  #Warning(predict_stock_price_by_option): options not found for",ticker)
        return None
    print("\nFound options with",len(datelist),"maturity dates for",ticker)

    import pandas as pd
    df=pd.DataFrame(columns=['Ticker','Date','WA Strike','Total Options', \
                             'Calls in Total%','OTM in Calls%','OTM Calls in Total%', \
                             'Puts in Total%','OTM in Puts%','OTM Puts in Total%'])    
    for d in datelist:
        print_progress_percent2(d,datelist,steps=5,leading_blanks=4)
        
        if DEBUG: print("Processing options matured on",d)
        opt_call,opt_put=option_chain(ticker,d,printout=False)
        
        numofcalls=len(opt_call)
        opt_call_otm=opt_call[opt_call['inTheMoney']==False]
        numofotmcalls=len(opt_call_otm)
        
        numofputs=len(opt_put)
        opt_put_otm=opt_put[opt_put['inTheMoney']==False]
        numofotmputs=len(opt_put_otm)
        
        totalopts=numofcalls+numofputs
        
        callsintotal=round(numofcalls/totalopts*100,2)
        if numofcalls != 0:
            otmincalls=round(numofotmcalls/numofcalls*100,2)
        else:
            otmincalls=0
        otmcallsintotal=round(numofotmcalls/totalopts*100,2)
        
        putsintotal=round(numofputs/totalopts*100,2)
        if numofputs != 0:
            otminputs=round(numofotmputs/numofputs*100,2)
        else:
            otminputs=0
        otmputsintotal=round(numofotmputs/totalopts*100,2)
        
        opts=pd.concat([opt_call,opt_put])
        opts.sort_values('date',ascending=False,inplace=True)
        lasttradedate=list(opts['date'])[0]
        lastndate=date_adjust(lasttradedate, adjust=-lastndays)
        
        #取最近几天的期权交易
        opts2=opts[opts['date']>=lastndate] 
        opts2.dropna(inplace=True)
        wa_strike=round(((opts2['strike']*opts2['volume']).sum())/(opts2['volume'].sum()),2)
        
        s=pd.Series({'Ticker':ticker,'Date':d,'WA Strike':wa_strike, \
                     'Total Options':totalopts, \
                     'Calls in Total%':callsintotal,'OTM in Calls%':otmincalls,'OTM Calls in Total%':otmcallsintotal, \
                     'Puts in Total%':putsintotal,'OTM in Puts%':otminputs,'OTM Puts in Total%':otmputsintotal})
        try:
            df=df.append(s,ignore_index=True)
        except:
            df=df._append(s,ignore_index=True)

    #建立日期索引
    todatetime=lambda x:pd.to_datetime(x)
    df['date']=df['Date'].apply(todatetime)
    df2=df.set_index(['date'])  
    
    #绘图1：Calls vs Puts比例
    import datetime
    today = datetime.date.today()    
    
    colname1='Calls in Total%'
    label1='Calls in Total%'
    colname2='Puts in Total%'
    label2='Puts in Total%'
    ylabeltxt='Percentage'
    titletxt="Option Comparison: "+ticker+", Calls vs Puts"

    footnote="Source: Yahoo Finance, "+str(today)
    plot_line2(df2,ticker,colname1,label1, \
               df2,ticker,colname2,label2, \
               ylabeltxt,titletxt,footnote)
    
    #绘图2：OTM Calls vs OTM Puts相对比例
    colname1='OTM in Calls%'
    label1='OTM in Calls%'
    colname2='OTM in Puts%'
    label2='OTM in Puts%'
    ylabeltxt='Percentage'
    titletxt="Option Relative Proportion Comparison\n("+ticker+", OTM Calls vs OTM Puts)"

    footnote="Source: Yahoo Finance, "+str(today)
    plot_line2(df2,ticker,colname1,label1, \
               df2,ticker,colname2,label2, \
               ylabeltxt,titletxt,footnote)
    
    #绘图3：OTM Calls vs OTM Puts绝对比例
    colname1='OTM Calls in Total%'
    label1='OTM Calls in Total%'
    colname2='OTM Puts in Total%'
    label2='OTM Puts in Total%'
    ylabeltxt='Percentage'
    titletxt="Option Absolute Proportion Comparison\n("+ticker+", OTM Calls vs OTM Puts)"

    footnote="Source: Yahoo Finance, "+str(today)
    plot_line2(df2,ticker,colname1,label1, \
               df2,ticker,colname2,label2, \
               ylabeltxt,titletxt,footnote)

    #绘图4：标的物价格预测
    df2x=df2.drop(df2[df2['Total Options']<=1].index)
    """
    colname='WA Strike'
    collabel='Predicted Price'
    ylabeltxt=''
    titletxt="Predicting Prices via Options: "+ticker
    footnote="Source: Yahoo Finance, "+str(today)
    plot_line(df2x,colname,collabel,ylabeltxt,titletxt,footnote,power=power)
    """
    
    #打印预测结果
    compotm=lambda x:compare_otm(x)
    df2x['Trend']=df2x.apply(compotm,axis=1)  #axis=1表示按行操作
    """
    collist=['Date','Trend','WA Strike','Total Options','Calls in Total%','OTM in Calls%', \
            'Puts in Total%','OTM in Puts%']
    """
    collist=['Date','Trend','Total Options','Calls in Total%','Puts in Total%', \
             'OTM in Calls%','OTM in Puts%','OTM Calls in Total%','OTM Puts in Total%']
    df3=df2x[collist]
    df3.rename(columns={'Total Options':'TotalOptions'}, inplace = True)
    df3.rename(columns={'Calls in Total%':'Calls%','Puts in Total%':'Puts%'}, inplace = True)
    df3.rename(columns={'OTM in Calls%':'OTMinCalls%','OTM in Puts%':'OTMinPuts%'}, inplace = True)
    df3.rename(columns={'OTM Calls in Total%':'OTM Calls/Total%','OTM Puts in Total%':'OTM Puts/Total%'}, inplace = True)
    
    """
    print("\n ======= Predicting Price Trend via Option Configuration: "+ticker+" =======")
    #设置打印对齐
    pd.set_option('display.max_columns', 1000)
    pd.set_option('display.width', 1000)
    pd.set_option('display.max_colwidth', 1000)
    pd.set_option('display.unicode.ambiguous_as_wide', True)
    pd.set_option('display.unicode.east_asian_width', True)
    print(df3.to_string(index=False))
    """
    #lastdate,lastprice=get_last_close1(ticker)
    prices_tmp=security_trend(ticker,graph=False)
    lastdate=str(prices_tmp.tail(1).index.values[0].date())
    lastprice=str(prices_tmp.tail(1).Close.values[0])
    """
    print(" Note:")
    print("   1) Recent price:",lastprice,"\b,",lastdate,'\b.')
    print("   2) +(-) predicts higher(lower) price than recent, ++(--) for more likely, +/- for undetermined trend.")
    print("   3) Option trade period: recent "+str(lastndays)+" days. No stock splits in the period. Dates with only 1 option removed.")
    #print("   4) Removed those samples with only one option, if any.")
    print(" "+footnote+'.')
    """
    tname=get_stock_name1_en(ticker,short_name=True)
    titletxt="Predicting Price Trend via Option Configuration: "+tname
    footnote1="Note:\n"
    footnote2="1. Recent price: "+lastprice+", "+lastdate+'\n'
    footnote3="2. +(-) predicts higher(lower) price than recent, ++(--) more likely, +/- undetermined\n"
    footnote4="3. Period: recent "+str(lastndays)+" days. No stock splits in the period. Removed dates with 1 option only\n"
    footnote9=footnote1+footnote2+footnote3+footnote4+footnote    
    
    df_display_CSS(df3,titletxt=titletxt,footnote=footnote9,facecolor='papayawhip',decimals=2, \
           first_col_align='left',second_col_align='right', \
           last_col_align='right',other_col_align='right', \
           titile_font_size='15px',heading_font_size='13px', \
           data_font_size='13px')
    
    return df2




#================================================================
if __name__=='__main__':
    intdate=1604350755

def int2date(intdate):
    """
    功能：将数字转换为日期，10位数字为秒级，13位的为毫秒级
    输入：使用10位或13位整数表示的日期时间
    返回：yyyy-mm-dd hh:mm:ss
    """
    import time
    intstr=str(intdate)

    if len(intstr) == 10:
        tupTime = time.localtime(intdate)   #秒时间戳
        #standardTime = time.strftime("%Y-%m-%d %H:%M:%S", tupTime)
        standardTime = time.strftime("%Y-%m-%d", tupTime)
        return standardTime    

    if len(intstr)==13:
        timeNum=intdate     #毫秒时间戳
        timeTemp = float(timeNum/1000)
        tupTime = time.localtime(timeTemp)
        #standardTime = time.strftime("%Y-%m-%d %H:%M:%S", tupTime)
        standardTime = time.strftime("%Y-%m-%d", tupTime)
        return standardTime

    #直接为日期时间结构
    standardTime = intdate.strftime("%Y-%m-%d")
    return standardTime

if __name__=='__main__':
    intdate1=1604349847
    int2date(intdate1)
    
    intdate2=1566366547705
    int2date(intdate2)
    
    import pandas as pd
    intdate3=pd.to_datetime('2020-11-03')
    int2date(intdate3)
#==============================================================================
#==============================================================================
def compare_otm(row,spread=1.0):
    """
    功能：比较OTM Call vs OTM Put的绝对比例大小，赋值+/-
    输入：df的一行
    输出：+/-
    """
    if row['OTM Calls in Total%'] > row['OTM Puts in Total%']:
        result='+'
        if (row['Calls in Total%'] > row['Puts in Total%']) and ((row['OTM in Calls%'] > row['OTM in Puts%'])):
                result='++'
    
    if row['OTM Calls in Total%'] < row['OTM Puts in Total%']:
        result='-'
        if (row['Calls in Total%'] < row['Puts in Total%']) and ((row['OTM in Calls%'] < row['OTM in Puts%'])):
                result='--'

    if abs(row['OTM Calls in Total%'] - row['OTM Puts in Total%']) < spread:
        result='+/-'

    return result

#==============================================================================
def call_timevalue(row):
    """
    功能：计算看涨期权的时间价值
    输入：df的一行
    输出：期权的时间价值
    """
    #是否实值期权
    if row['inTheMoney']:
        tv=row['lastPrice']-row['lastSPrice']+row['strike']
    else:
        tv=row['lastPrice']
    return tv

def put_timevalue(row):
    """
    功能：计算看跌期权的时间价值
    输入：df的一行
    输出：期权的时间价值
    """
    #是否实值期权
    if row['inTheMoney']:
        tv=row['lastPrice']+row['lastSPrice']-row['strike']
    else:
        tv=row['lastPrice']
    return tv

#==============================================================================   

if __name__ =="__main__":
    ticker='AAPL'
    lastndays=2

def price_prospect_via_option(ticker,lastdays=7,cutoff=[1.1,5.0,10.0]):    
    """
    功能：根据股票期权预测标的物价格
    算法：
    1、计算虚值看涨/看跌期权数量比例
    2、计算虚值看涨/看跌期权交易金额比例
    3、若虚值看涨期权占优，为看涨，并据此估计未来标的物价格；
    4、若虚值看跌期权占优，为看跌，并据此估计未来标的物价格；
    5、否则，为不明确
    返回：期权明细
    """
    lastndays=lastdays
    
    DEBUG=False
    print("Searching option chain for",ticker,'...',end='')
    
    try:
        datelist=option_maturity(ticker,printout=False)
    except:
        print("\n  #Warning(price_prospect_via_option): option info not found for",ticker)
        return None
    if datelist is None:
        print("\n  #Warning(price_prospect_via_option): options not found for",ticker)
        return None
    print("found",len(datelist),"maturity dates of options")

    #最新的标的物价格
    #print("Searching recent close price for",ticker,'...',end='')
    try:
        #lastsdate,lastsprice=get_last_close1(ticker)
        prices_tmp=security_trend(ticker,graph=False)
        lastsdate=str(prices_tmp.tail(1).index.values[0].date())
        lastsprice=str(prices_tmp.tail(1).Close.values[0])

    except:
        print("\n  #Error(price_prospect_via_option): failed in retrieving close price for",ticker)
        return None
    if (lastsdate is None) or (lastsprice is None):
        print("\n  #Error(price_prospect_via_option): retrieving close price failed for",ticker)
        return None
    if DEBUG: print(lastsprice,'\b,',lastsdate)

    import pandas as pd
    df=pd.DataFrame(columns=['Ticker','Date','Trend','Estimated Price', \
                             'OTM Volume Call/Put','OTM Amount Call/Put','Spot Date','Spot Price'])    
    for d in datelist:
        print_progress_percent2(d,datelist,steps=5,leading_blanks=4)
        
        if DEBUG: print("Analyzing options matured on",d,'...')
        opt_call,opt_put=option_chain(ticker,d,printout=False)
        
        if (opt_call is None) or (opt_put is None):
            if DEBUG:
                print("  #Warning(price_prospect_via_option): failed in retrieving options matured on",d)
            """
            break
            return None        
            """
            continue
        
        if (len(opt_call) == 0) or (len(opt_put) == 0):
            if DEBUG:
                print("  #Warning(price_prospect_via_option): retrieved zero options matured on",d)
            """
            break
            return None     
            """
            continue
            
        currency=list(opt_call['currency'])[0]
        
        ##########处理看涨期权##########
        if DEBUG: print("  Call volume: ",end='')
        opt_call['lastSDate']=lastsdate
        opt_call['lastSPrice']=lastsprice
        
        #去掉无交易的期权
        opt_call.dropna(inplace=True)
        #只保留过去lastndays日历日的交易
        lasttdate=max(list(opt_call['date']))
        fromtdate=date_adjust(lasttdate, adjust=-lastndays)        
        opt_call=opt_call[opt_call['date'] >= fromtdate]    
        numofcalls=sum(opt_call['volume'])
        
        """
        #计算期权的时间价值：不一致，无法进一步利用
        calltv=lambda x:call_timevalue(x)
        opt_call['timeValue']=opt_call.apply(calltv,axis=1)  #axis=1表示按行操作
        """
        
        #计算虚值期权的交易数量、交易金额和加权价格
        opt_call_otm=opt_call[opt_call['inTheMoney']==False]
        numofotmcalls=sum(opt_call_otm['volume'])
        amtofotmcalls=round(sum(opt_call_otm['lastPrice']*opt_call_otm['volume']),2)
        avopofotmcalls=round((amtofotmcalls/numofotmcalls),2)
        if DEBUG: print("total",int(numofcalls),'\b, OTM',int(numofotmcalls),end='')

        #基于加权价格判断行权价
        opt_call_otm.sort_values('lastPrice',ascending=True,inplace=True)
        strikelist=list(opt_call_otm['strike'])
        lastPricelist=list(opt_call_otm['lastPrice'])+[avopofotmcalls]
        lastPricelist=sorted(lastPricelist,reverse=False)
        avoppos=lastPricelist.index(avopofotmcalls)
        if avoppos > 0:
            op1=lastPricelist[avoppos-1]
            strike1=strikelist[avoppos-1]
            op2=lastPricelist[avoppos+1]
            strike2=strikelist[avoppos]            
            avspofotmcalls=round(min(strike1,strike2)+abs(strike1-strike2)*((avopofotmcalls-min(op1,op2))/abs(op1-op2)),2)
        else:
            avspofotmcalls=strikelist[avoppos]
        if DEBUG: print(", done!")
        
        ##########处理看跌期权##########
        if DEBUG: print("  Put volume: ",end='')
        opt_put['lastSDate']=lastsdate
        opt_put['lastSPrice']=lastsprice
        
        #去掉无交易的期权
        opt_put.dropna(inplace=True)
        #只保留过去lastndays日历日的交易
        lasttdate=max(list(opt_put['date']))
        fromtdate=date_adjust(lasttdate, adjust=-lastndays)        
        opt_put=opt_put[opt_put['date'] >= fromtdate] 
        numofputs=sum(opt_put['volume'])
        
        """        
        #计算期权的时间价值：不一致，无法进一步利用
        puttv=lambda x:put_timevalue(x)
        opt_put['timeValue']=opt_put.apply(puttv,axis=1)  #axis=1表示按行操作
        """
        
        #计算虚值期权的交易数量、交易金额和加权价格
        opt_put_otm=opt_put[opt_put['inTheMoney']==False]
        numofotmputs=sum(opt_put_otm['volume'])
        amtofotmputs=round(sum(opt_put_otm['lastPrice']*opt_put_otm['volume']),2)
        avopofotmputs=round((amtofotmputs/numofotmputs),2)
        if DEBUG: print("total",int(numofputs),'\b, OTM',int(numofotmputs),end='')

        #基于加权价格判断行权价
        opt_put_otm.sort_values('lastPrice',ascending=True,inplace=True)
        strikelist=list(opt_put_otm['strike'])
        lastPricelist=list(opt_put_otm['lastPrice'])+[avopofotmputs]
        lastPricelist=sorted(lastPricelist,reverse=False)
        avoppos=lastPricelist.index(avopofotmputs)
        if avoppos > 0:
            op1=lastPricelist[avoppos-1]
            strike1=strikelist[avoppos-1]
            op2=lastPricelist[avoppos+1]
            strike2=strikelist[avoppos]            
            avspofotmputs=round(min(strike1,strike2)+abs(strike1-strike2)*((avopofotmputs-min(op1,op2))/abs(op1-op2)),2)
        else:
            avspofotmputs=strikelist[avoppos]            
        if DEBUG: print(", done!")

        #比较虚值看涨/看跌期权的数量和交易金额
        if DEBUG: print("  Evaluating price trend ...",end='')
        rateqty=round(numofotmcalls/numofotmputs,2)  
        rateamt=round(amtofotmcalls/amtofotmputs,2)
        trend='+/-'
        star1=cutoff[0]; star2=cutoff[1]; star3=cutoff[2]
        #加强判断：以rateamt为主，结合rateqty
        if (rateqty > 1.0) and (rateamt > star1):
            trend='+'
        if (rateqty < 1.0) and (rateamt < 1.0/star1):
            trend='-'        
        if (rateqty > star2) and (rateamt > star2):
            trend='++'
        if (1/rateqty > star2) and (1/rateamt > star2):
            trend='--'          
        if (rateqty > star3) and (rateamt > star3):
            trend='+++'
        if (1/rateqty > star3) and (1/rateamt > star3):
            trend='---'          
        
        estsprice=lastsprice
        if (trend[0] == '+') and (trend != '+/-'):
            estsprice=avspofotmcalls
        if trend[0]=='-':
            estsprice=avspofotmputs
        if trend == '+/-':
            estsprice=(avspofotmcalls + avspofotmputs)/2.0
        
        s=pd.Series({'Ticker':ticker,'Date':d,'Trend':trend,'Estimated Price':estsprice, \
            'OTM Volume Call/Put':rateqty,'OTM Amount Call/Put':rateamt,'Spot Date':lastsdate,'Spot Price':lastsprice})
        try:
            df=df.append(s,ignore_index=True)
        except:
            df=df._append(s,ignore_index=True)
        if DEBUG: print(", done!")

    #建立日期索引
    todatetime=lambda x:pd.to_datetime(x)
    df['date']=df['Date'].apply(todatetime)
    df2=df.set_index(['date'])  
    
    tname=get_stock_name1_en(ticker,short_name=True)
    
    #绘图1：虚值Calls vs Puts数量比例
    import datetime
    stoday = datetime.date.today()    
    
    df2['Benchmark']=1.0
    colname1='OTM Volume Call/Put'
    label1='虚值看涨/看跌期权合约数量比例'
    colname2='Benchmark'
    label2='等比例线'
    ylabeltxt='比例'
    titletxt="期权链中的合约数量: "+tname+", 虚值看涨/看跌期权比例"

    footnote="数据来源：雅虎财经, "+str(stoday)
    plot_line2(df2,ticker,colname1,label1, \
               df2,ticker,colname2,label2, \
               ylabeltxt,titletxt,footnote)
    
    #绘图2：OTM Calls vs OTM Puts交易金额比例
    colname1='OTM Amount Call/Put'
    label1='虚值看涨/看跌期权交易金额比例'
    titletxt="期权链中的交易金额: "+tname+", 虚值看涨/看跌期权比例"

    plot_line2(df2,ticker,colname1,label1, \
               df2,ticker,colname2,label2, \
               ylabeltxt,titletxt,footnote)
    
    #绘图3：预测的标的物价格
    df2['Benchmark']=lastsprice
    colname1='Estimated Price'
    label1='预期价格'
    colname2='Benchmark'
    label2='当前价格'
    ylabeltxt='价格('+currency+')'
    titletxt="期权链与标的价格预期: "+tname

    plot_line2(df2,ticker,colname1,label1, \
               df2,ticker,colname2,label2, \
               ylabeltxt,titletxt,footnote)
    
    #打印预测结果
    collist=['Date','Trend','Estimated Price','OTM Volume Call/Put','OTM Amount Call/Put']
    df3=df2[collist]
    """
    print("\n ======= 基于期权链结构的股票走势和价格预期: "+tname+" =======")
    #设置打印对齐
    pd.set_option('display.max_columns', 1000)
    pd.set_option('display.width', 1000)
    pd.set_option('display.max_colwidth', 1000)
    pd.set_option('display.unicode.ambiguous_as_wide', True)
    pd.set_option('display.unicode.east_asian_width', True)
    df3.columns=['日期','标的物价格走势','标的物价格预期','虚值看涨/看跌合约数量比例','虚值看涨/看跌交易金额比例']
    print(df3.to_string(index=False))
    
    print(" 注:")
    print(" 1) 当前价格: "+currency+str(lastsprice),"\b,",lastsdate,'\b.')
    print(" 2) +(-)表示价格将比当前变高(低), +/-表示趋势不明朗.")
    print(" 3) 期权交易样本期间: 最近"+str(lastndays)+"个日历日，且期间内未发生分拆.")
    print(" 4) 价格估计可能随时变化，越远期的估计可能准确度越欠佳.")
    print(" "+footnote+'.')
    """
    titletxt="期权链与标的价格预期: "+tname
    footnote1="注:\n"
    footnote2="1、当前价格: "+currency+str(lastsprice)+", "+lastsdate+'\n'
    footnote3="2、+(-)表示价格将比当前变高(低), +/-表示趋势不明朗\n"
    footnote4="3、期权交易样本期间: 最近"+str(lastndays)+"个日历日，且期间内未发生分拆\n"
    footnote5="4) 价格价格估计可能随时变化，越远期的估计可能准确度越欠佳\n"
    
    footnote9=footnote1+footnote2+footnote3+footnote4+footnote5+footnote
    
    df_display_CSS(df3,titletxt=titletxt,footnote=footnote9,facecolor='papayawhip',decimals=2, \
               first_col_align='left',second_col_align='right', \
               last_col_align='right',other_col_align='right', \
               titile_font_size='15px',heading_font_size='13px', \
               data_font_size='13px')
    
    return df2

if __name__ =="__main__":
    df=stock_trend_by_option('AAPL',7)

#==============================================================================
#==============================================================================   
#==============================================================================   
#==============================================================================

#==============================================================================








