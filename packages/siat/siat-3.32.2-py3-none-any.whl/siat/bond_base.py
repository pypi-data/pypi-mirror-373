# -*- coding: utf-8 -*-
"""
本模块功能：债券，基础层函数
所属工具包：证券投资分析工具SIAT 
SIAT：Security Investment Analysis Tool
创建日期：2020年1月8日
最新修订日期：2020年5月10日
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
def macD0(cr,ytm,fv,nterms):
    """
    功能：计算债券的麦考莱久期期数
    输入参数：
    1、每期票面利率cr
    2、每期到期收益率ytm，市场利率，贴现率
    3、票面价值fv
    3、到期期数nterms
    输出：麦考莱久期的期数（不一定是年数）
    """
    #生成期数序列
    import pandas as pd
    t=pd.Series(range(1,(nterms+1)))
    
    #计算未来票息和面值的现值
    p=sum(cr*fv/(1+ytm)**t)+fv/(1+ytm)**len(t)
    #计算未来票息和面值的加权现值
    wp=sum(cr*fv*t/(1+ytm)**t)+fv*len(t)/(1+ytm)**len(t)
    
    return wp/p    

if __name__=='__main__':
    cr=0.08/2; ytm=0.1/2; nterms=6; fv=100
    print(macD0(cr,ytm,fv,nterms))
#==============================================================================
def macD(cr,ytm,nyears,ctimes=2,fv=100):
    """
    功能：计算债券的麦考莱久期年数
    输入参数：
    1、年票面利率cr
    2、年到期收益率ytm，市场利率，贴现率
    3、到期年数nyears
    4、每年付息次数ctimes
    5、票面价值fv
    输出：麦考莱久期（年数）
    """
    
    #转换为每期付息的参数
    c=cr/ctimes; y=ytm/ctimes; F=fv; n=nyears*ctimes
    
    #计算麦考莱久期期数
    d=macD0(c,y,F,n)
    #转换为麦考莱久期年数：年数=期数/每年付息次数
    D=round(d/ctimes,4)
    
    return D                    

if __name__=='__main__':
    cr=0.08; ytm=0.1; nyears=3; ctimes=2; fv=100
    print(macD(cr,ytm,nyears))

#==============================================================================
def MD0(cr,ytm,fv,nterms):
    """
    功能：计算债券的修正久期期数
    输入参数：
    1、每期票面利率cr
    2、每期到期收益率ytm，市场利率，贴现率
    3、票面价值fv
    4、到期期数nterms
    输出：修正久期期数（不一定是年数）
    """
    #修正麦考莱久期
    md=macD0(cr,ytm,fv,nterms)/(1+ytm)
    
    return md

if __name__=='__main__':
    cr=0.08/2; ytm=0.1/2; nterms=6; fv=100
    print(MD0(cr,ytm,fv,nterms))    
    
#==============================================================================
def MD(cr,ytm,nyears,ctimes=2,fv=100):
    """
    功能：计算债券的修正久期年数
    输入参数：
    1、年票面利率cr
    2、年到期收益率ytm，市场利率，贴现率
    3、到期年数nyears
    4、每年付息次数ctimes
    5、票面价值fv
    输出：修正久期（年数）
    """
    
    #转换为每期付息的参数
    c=cr/ctimes; y=ytm/ctimes; F=fv; n=nyears*ctimes
    
    #计算久期期数
    d=MD0(c,y,F,n)
    #转换为久期年数：年数=期数/每年付息次数
    D=round(d/ctimes,4)
    
    return D                    

if __name__=='__main__':
    cr=0.08; ytm=0.1; nyears=3; ctimes=2; fv=100
    print(MD(cr,ytm,nyears))


    
#==============================================================================
def DD0(cr,ytm,fv,nterms):
    """
    功能：计算债券的美元久期期数
    输入参数：
    1、每期票面利率cr
    2、每期到期收益率ytm，市场利率，贴现率
    3、票面价值fv
    4、到期期数nterms
    输出：美元久期期数（不一定是年数）
    """
    #生成期数序列
    import pandas as pd
    t=pd.Series(range(1,(nterms+1)))
    
    #计算现值
    p=sum(cr*fv/(1+ytm)**t)+fv/(1+ytm)**len(t)
    #美元久期期数
    dd=MD0(cr,ytm,fv,nterms)*p
    
    return dd

if __name__=='__main__':
    cr=0.08/2; ytm=0.1/2; nterms=6; fv=100
    print(DD0(cr,ytm,fv,nterms))    
    
#==============================================================================    
def DD(cr,ytm,nyears,ctimes=2,fv=100):
    """
    功能：计算债券的美元久期年数
    输入参数：
    1、年票面利率cr
    2、年到期收益率ytm，市场利率，贴现率
    3、到期年数nyears
    4、每年付息次数ctimes
    5、票面价值fv
    输出：美元久期（金额）
    """
    
    #转换为每期付息的参数
    c=cr/ctimes; y=ytm/ctimes; F=fv; n=nyears*ctimes
    
    #计算久期期数
    d=DD0(c,y,F,n)
    #转换为久期年数：年数=期数/每年付息次数
    D=round(d/ctimes,2)
    
    return D                    

if __name__=='__main__':
    cr=0.08; ytm=0.1; nyears=3; ctimes=2; fv=100
    print(DD(cr,ytm,nyears))

#==============================================================================    
def ED0(cr,ytm,fv,nterms,per):
    """
    功能：计算债券的有效久期期数
    输入参数：
    1、每期票面利率cr
    2、每期到期收益率ytm，市场利率，贴现率
    3、票面价值fv
    4、到期期数nterms
    5、到期收益率的变化幅度，1个基点=0.01%=0.0001
    输出：有效久期期数（不一定是年数）
    """
    #生成期数序列
    import pandas as pd
    t=pd.Series(range(1,(nterms+1)))
    
    #计算到期收益率变化前的现值
    p0=sum(cr*fv/(1+ytm)**t)+fv/(1+ytm)**len(t)
    #计算到期收益率增加一定幅度后的现值
    p1=sum(cr*fv/(1+ytm+per)**t)+fv/(1+ytm+per)**len(t)
    #计算到期收益率减少同等幅度后的现值
    p2=sum(cr*fv/(1+ytm-per)**t)+fv/(1+ytm-per)**len(t)
    #久期期数
    try:
        ed=(p2-p1)/(2*p0*per)
    except:
        print("  #Error(ED0): float division by zero")
        print("  p2=",p2,', p1=',p1,', p0=',p0,', per=',per)
        return None
    
    return ed

if __name__=='__main__':
    cr=0.08/2; ytm=0.1/2; nterms=6; fv=100; per=0.001/2
    print(ED0(cr,ytm,fv,nterms,per))    
    
#==============================================================================    
def ED(cr,ytm,nyears,peryear,ctimes=2,fv=100):
    """
    功能：计算债券的有效久期年数
    输入参数：
    1、年票面利率cr
    2、年到期收益率ytm，市场利率，贴现率
    3、到期年数nyears
    4、年到期收益率变化幅度peryear
    5、每年付息次数ctimes
    6、票面价值fv
    输出：有效久期（年数）
    """
    
    #转换为每期付息的参数
    c=cr/ctimes; y=ytm/ctimes; per=peryear/ctimes; F=fv; n=nyears*ctimes
    
    #计算久期期数
    d=ED0(c,y,F,n,per)
    #转换为久期年数：年数=期数/每年付息次数
    D=round(d/ctimes,4)
    
    return D                    

if __name__=='__main__':
    cr=0.08; ytm=0.1; nyears=3; ctimes=2; fv=100; peryear=0.001
    print(ED(cr,ytm,nyears,peryear))
    
    cr=0.095; ytm=0.1144; nyears=8; ctimes=2; fv=1000; peryear=0.0005
    print(ED(cr,ytm,nyears,peryear))    
#==============================================================================    
def CFD0(cr,ytm,fv,nterms):
    """
    功能：计算债券的封闭式久期期数
    输入参数：
    1、每期票面利率cr
    2、每期到期收益率ytm，市场利率，贴现率
    3、票面价值fv
    4、到期期数nterms
    输出：久期期数（不一定是年数）
    """
    #生成期数序列
    import pandas as pd
    t=pd.Series(range(1,(nterms+1)))
    
    #计算到期收益率变化前的现值
    p=sum(cr*fv/(1+ytm)**t)+fv/(1+ytm)**len(t)
    
    #计算分子第1项
    nm1=(cr*fv) * ((1+ytm)**(nterms+1)-(1+ytm)-ytm*nterms) / ((ytm**2)*((1+ytm)**nterms))
    #计算分子第2项
    nm2=fv*(nterms/((1+ytm)**nterms))
    
    #计算封闭式久期
    cfd=(nm1+nm2)/p
    
    return cfd

if __name__=='__main__':
    cr=0.095/2; ytm=0.1144/2; nterms=16; fv=1000
    print(CFD0(cr,ytm,fv,nterms))    
#==============================================================================    
def CFD(cr,ytm,nyears,ctimes=2,fv=100):
    """
    功能：计算债券的封闭式年数
    输入参数：
    1、年票面利率cr
    2、年到期收益率ytm，市场利率，贴现率
    3、到期年数nyears
    4、每年付息次数ctimes
    5、票面价值fv
    输出：久期（年数）
    """
    
    #转换为每期付息的参数
    c=cr/ctimes; y=ytm/ctimes; F=fv; n=nyears*ctimes
    
    #计算久期期数
    d=CFD0(c,y,F,n)
    #转换为久期年数：年数=期数/每年付息次数
    cfd=round(d/ctimes,4)
    
    return cfd                    

if __name__=='__main__':
    cr=0.08; ytm=0.1; nyears=3; ctimes=2; fv=100
    print(CFD(cr,ytm,nyears))
#==============================================================================    
def C0(cr,ytm,fv,nterms):
    """
    功能：计算债券的凸度期数
    输入参数：
    1、每期票面利率cr
    2、每期到期收益率ytm，市场利率，贴现率
    3、票面价值fv
    4、到期期数nterms
    输出：到期收益率变化幅度为per时债券价格的变化幅度
    """    
    #生成期数序列
    import pandas as pd
    t=pd.Series(range(1,(nterms+1)))
    
    #计算未来现金流的现值
    p=sum(cr*fv/(1+ytm)**t)+fv/(1+ytm)**len(t)
    #计算未来现金流的加权现值：权重为第t期的(t**2+t)
    w2p=sum(cr*fv*(t**2+t)/(1+ytm)**t)+fv*(len(t)**2+len(t))/(1+ytm)**len(t)
    #计算凸度
    c0=w2p/(p*(1+ytm)**2)
    
    return c0

if __name__=='__main__':
    cr=0.08/2; ytm=0.1/2; nterms=6; fv=100
    print(C0(cr,ytm,fv,nterms)) 
#==============================================================================    
def convexity(cr,ytm,nyears,ctimes=2,fv=100):
    """
    功能：计算债券的凸度年数
    输入参数：
    1、年票面利率cr
    2、年到期收益率ytm，市场利率，贴现率
    3、到期年数nyears
    4、每年付息次数ctimes
    5、票面价值fv
    输出：凸度（年数）
    """
    #转换为每期付息的参数
    c=cr/ctimes; y=ytm/ctimes; F=fv; n=nyears*ctimes
    
    #计算凸度期数
    c=C0(c,y,F,n)
    #转换为凸度年数：年数=期数/每年付息次数**2
    cyears=round(c/ctimes**2,4)
    
    return cyears                    

if __name__=='__main__':
    cr=0.08; ytm=0.1; nyears=3; ctimes=2; fv=100
    print(convexity(cr,ytm,nyears))
#==============================================================================
if __name__=='__main__':
    coupon_rate=0.07
    maturity_years=8
    ytm=0.06
    coupon_times=2
    par_value=100
    rate_diff=0.005
    
    dp=interest_rate_risk(coupon_rate,maturity_years,ytm,rate_diff)

def interest_rate_risk(coupon_rate,maturity_years,ytm,rate_diff, \
                       coupon_times=2,par_value=100,printout=True):
    """
    功能：若市场利率变化(上升/下降)rate_change(Δr)，导致债券市价的变化率(ΔP/P)
    原理：债券市场价格的久期与凸度展开公式
    注意：套壳函数ytm_risk
    """
    
    value=ytm_risk(cr=coupon_rate,ytm=ytm,nyears=maturity_years, \
                   bpyear=rate_diff,ctimes=coupon_times,fv=par_value)
    
    if printout:
        calc_durations(coupon_rate,maturity_years,ytm,
                          coupon_times=coupon_times,par_value=par_value, \
                          mtypes=['macaulay_duration','convexity'])
        
        if (rate_diff !=0) and (value !=0):
            print("\n***利率变化带来的风险")
        
        if rate_diff > 0:
            arrow='↑'
        elif rate_diff < 0:
            arrow='↓'
        else:
            arrow=' '
        if rate_diff !=0:    
            print("市场利率变化(基点):",int(rate_diff*10000),arrow)
        
        if value > 0:
            arrow2='↑'
        elif value < 0:
            arrow2='↓'
        else:
            arrow2=' '
        if value !=0:    
            print("债券市价的变化率  :",round(value*100,2),'\b% '+arrow2)
    
    return value

#==============================================================================    
def ytm_risk(cr,ytm,nyears,bpyear,ctimes=2,fv=100):
    """
    功能：计算债券的利率风险，即市场利率（到期收益率）变动将带来的债券价格变化率
    输入参数：
    1、年票面利率cr
    2、年到期收益率ytm，市场利率，贴现率
    3、到期年数nyears
    4、年华市场利率（到期收益率）变化的幅度bpyear(小数，不是基点)
    5、每年付息次数ctimes
    6、票面价值fv
    输出：到期收益率变化幅度导致的债券价格变化率
    """
    #转换为每期付息的参数
    c=cr/ctimes; y=ytm/ctimes; F=fv; n=nyears*ctimes
    
    #计算到期收益率变化对债券价格的影响：第1部分
    b0=-MD0(c,y,F,n)/2*bpyear
    #计算到期收益率变化对债券价格的影响：第2部分
    b1=(0.5*C0(c,y,F,n)/ctimes**2)*bpyear**2
    #债券价格的变化率
    p_pct=round(b0+b1,4)
        
    return p_pct

if __name__=='__main__':
    cr=0.08; ytm=0.1; nyears=3; bpyear=0.01
    print(ytm_risk(cr,ytm,nyears,bpyear))        

#==============================================================================    
#==============================================================================    
def interbank_bond_issue_detail(fromdate,todate):
    """
    功能：获得银行间债券市场发行明细
    输入：开始日期fromdate，截止日期todate
    """
    #检查期间的合理性
    result,start,end=check_period(fromdate, todate)
    if result is None:
        print("  #Error(interbank_bond_issue_detail), invalid period:",fromdate,todate)
        return None
    
    #####银行间市场的债券发行数据
    import akshare as ak
    #获得债券发行信息第1页
    print("\n...Searching for bond issuance: ",end='')
    bond_issue=ak.get_bond_bank(page_num=1)    

    import pandas as pd
    from datetime import datetime
    #获得债券发行信息后续页
    maxpage=999
    for pn in range(2,maxpage):
        print_progress_bar(pn,2,maxpage)
        try:
            #防止中间一次失败导致整个过程失败
            bi=ak.get_bond_bank(page_num=pn)
            try:
                bond_issue=bond_issue.append(bi)
            except:
                bond_issue=bond_issue._append(bi)
        except:
            #后续的网页已经变得无法抓取
            print("...Unexpected get_bond_bank(interbank_bond_issue_detail), page_num",pn)
            break        
        
        #判断是否超过了开始日期
        bistartdate=bi.tail(1)['releaseTime'].values[0]
        bistartdate2=pd.to_datetime(bistartdate)
        if bistartdate2 < start: break
    print(" Done!")        
    
    #删除重复项，按日期排序
    bond_issue.drop_duplicates(keep='first',inplace=True)
    bond_issue.sort_values(by=['releaseTime'],ascending=[False],inplace=True)    
    #转换日期项
    lway1=lambda x: datetime.strptime(x,'%Y-%m-%d %H:%M:%S')
    bond_issue['releaseTime2']=bond_issue['releaseTime'].apply(lway1)    
    
    #提取年月日信息
    lway2=lambda x: x.year
    bond_issue['releaseYear']=bond_issue['releaseTime2'].map(lway2).astype('str')
    lway3=lambda x: x.month
    bond_issue['releaseMonth']=bond_issue['releaseTime2'].map(lway3).astype('str')
    lway4=lambda x: x.day
    bond_issue['releaseDay']=bond_issue['releaseTime2'].map(lway4).astype('str')
    lway5=lambda x: x.weekday() + 1
    bond_issue['releaseWeekDay']=bond_issue['releaseTime2'].map(lway5).astype('str')
    lway6=lambda x: x.date()
    bond_issue['releaseDate']=bond_issue['releaseTime2'].map(lway6).astype('str')
    
    #过滤日期
    bond_issue=bond_issue.reset_index(drop = True)
    bond_issue1=bond_issue.drop(bond_issue[bond_issue['releaseTime2']<start].index)
    bond_issue1=bond_issue1.reset_index(drop = True)
    bond_issue2=bond_issue1.drop(bond_issue1[bond_issue1['releaseTime2']>end].index)
    bond_issue2=bond_issue2.reset_index(drop = True)
    #转换字符串到金额
    bond_issue2['issueAmount']=bond_issue2['firstIssueAmount'].astype('float64')
    
    return bond_issue2
    
if __name__=='__main__':
    fromdate='2020-4-25'    
    todate='2020-4-28'
    ibbi=interbank_bond_issue_detail(fromdate,todate)
    
#==============================================================================
#==============================================================================
#==============================================================================
# 演示久期、凸度的影响因素
#==============================================================================
if __name__=='__main__':
    coupon_rate=0.07
    maturity_years=8
    ytm=0.06
    coupon_times=2
    par_value=100
    rate_change=0.0001
    mtype='macaulay_duration'
    
    calc_macaulay(coupon_rate,maturity_years,ytm,mtype='macaulay_duration')
    calc_macaulay(coupon_rate,maturity_years,ytm,mtype='modified_duration')
    calc_macaulay(coupon_rate,maturity_years,ytm,mtype='dollar_duration')
    calc_macaulay(coupon_rate,maturity_years,ytm,mtype='efficient_duration') 
    calc_macaulay(coupon_rate,maturity_years,ytm,mtype='closed_form_duration')
    calc_macaulay(coupon_rate,maturity_years,ytm,mtype='convexity')   
    
    calc_macaulay(0.1,3,0.12,1,1000,'macaulay_duration')
    calc_macaulay(0.1,3,0.05,1,1000,'macaulay_duration')
    calc_macaulay(0.1,3,0.20,1,1000,'macaulay_duration')    
    
    calc_macaulay(0.08,3,0.1,2,100,'closed_form_duration')    

    calc_macaulay(0.08,3,0.1,2,100,'modified_duration') 
    calc_macaulay(0.08,3,0.1,2,100,'dollar_duration')

    calc_macaulay(0.095,8,0.1144,2,1000,'efficient_duration',rate_change=0.0005)

    calc_macaulay(0.08,3,0.1,2,100,'convexity')

def calc_macaulay(coupon_rate,maturity_years,ytm,
                  coupon_times=2,par_value=100, \
                  mtype='macaulay_duration', \
                  rate_change=0.001):
    """
    功能：统一计算各种久期和凸度
    输入参数：
    coupon_rate：债券的票面年利率
    maturity_years：距离到期的年数，需要折算
    ytm：年到期收益率，可作为折现率
    coupon_times=2：每年付息次数
    par_value=100：债券面值
    rate_change=0：利率变化，专用于有效久期
    mtype='macaulay'：麦考利久期macaulay_duration，修正久期modified_duration，
    美元久期dollar_duration，有效久期efficient_duration，
    封闭久期closed_form_duration，凸度convexity
    printout=False：是否打印结果
    """
    
    # 检查计算类型
    mtypelist=['macaulay_duration','modified_duration','dollar_duration', \
               'efficient_duration','closed_form_duration','convexity']
    if not (mtype in mtypelist):
        print("  #Error(calc_macaulay): unsupported duration/convexity",mtype)
        print("  Supported duration/convexity:",mtypelist)
        return None
    
    value=999
    # 麦考利久期：返回久期年数
    if mtype=='macaulay_duration':
        value=macD(cr=coupon_rate,ytm=ytm,nyears=maturity_years, \
                   ctimes=coupon_times,fv=par_value)
    
    # 修正久期：返回年数
    if mtype=='modified_duration':
        value=MD(cr=coupon_rate,ytm=ytm,nyears=maturity_years, \
                 ctimes=coupon_times,fv=par_value)
    
    # 美元久期：返回金额
    if mtype=='dollar_duration':
        #DD(cr,ytm,nyears,ctimes=2,fv=100)
        value=DD(cr=coupon_rate,ytm=ytm,nyears=maturity_years, \
                 ctimes=coupon_times,fv=par_value)
    
    # 有效久期：返回年数
    if mtype=='efficient_duration':
        #ED(cr,ytm,nyears,peryear,ctimes=2,fv=100)
        value=ED(cr=coupon_rate,ytm=ytm,nyears=maturity_years, \
                 peryear=rate_change, \
                 ctimes=coupon_times,fv=par_value)
    
    # 封闭久期：返回年数
    if mtype=='closed_form_duration':
        #CFD(cr,ytm,nyears,ctimes=2,fv=100)
        value=CFD(cr=coupon_rate,ytm=ytm,nyears=maturity_years, \
                 ctimes=coupon_times,fv=par_value)
    
    # 凸度：返回年数
    if mtype=='convexity':
        #convexity(cr,ytm,nyears,ctimes=2,fv=100)
        value=convexity(cr=coupon_rate,ytm=ytm,nyears=maturity_years, \
                 ctimes=coupon_times,fv=par_value)
    
    if value==999:
        print("  #Error(calc_macaulay): no valid result calculated!")
        return None
    
    return value
            

#==============================================================================
if __name__=='__main__':
    coupon_rate=0.08
    maturity_years=3
    ytm=0.1
    coupon_times=2
    par_value=100
    rate_change=0.0005
    
    calc_durations(coupon_rate,maturity_years,ytm)

"""
def calc_durations(coupon_rate,maturity_years,ytm,
                  coupon_times=2,par_value=100, \
                  mtypes=['macaulay_duration','modified_duration', \
                  'dollar_duration'], \
                  rate_change=0.001):
"""
def calc_durations(coupon_rate,maturity_years,ytm,
                  coupon_times=1,par_value=100, \
                  mtypes=['macaulay_duration'], \
                  rate_change=0.001):
    """
    功能：一次性计算常见的久期，并打印
    注意：默认仅处理麦考利久期。若要处理其他久期，可以规定mtypes列表中的选项
    """
    
    mtypes_all=['macaulay_duration','modified_duration', \
                'efficient_duration','closed_form_duration','dollar_duration', \
                'convexity']
    mtypes_all_cn=['麦考利久期(年数):','修正久期(年数)  :', \
                '有效久期(年数)  :','封闭久期(年数)  :','美元久期(金额)  :', \
                '凸度(年数)      :']
    
    #print("\n===== 久期计算 =====")
    print("\n***债券信息")
    print("面值            :",par_value)
    print("票面利率(年化)  :",round(coupon_rate*100,2),'\b%')
    print("每年付息次数    :",coupon_times)
    print("到期时间(年数)  :",maturity_years)
    print("到期收益率(年化):",round(ytm*100,2),'\b%')
    
    if 'efficient_duration' in mtypes:
        print("假如年利率变化(基点):",rate_change*10000)
    
    print("\n***计算结果")
    for mt in mtypes:
        value=calc_macaulay(coupon_rate,maturity_years,ytm,
                            coupon_times,par_value, \
                            mtype=mt, \
                            rate_change=rate_change)
    
        pos=mtypes_all.index(mt)
        value_label=mtypes_all_cn[pos]
        
        print(value_label,value)
        
    return

#==============================================================================


def calc_convexity(coupon_rate,maturity_years,ytm,
                  coupon_times=1,par_value=100):
    """
    功能：用于计算债券的凸度，并打印
    注意：套壳函数calc_durations
    """
    calc_durations(coupon_rate,maturity_years,ytm,
                      coupon_times=coupon_times,par_value=par_value, \
                      mtypes=['convexity'])
        
    return

#==============================================================================
# 久期与凸度影响因素的展示
#==============================================================================
if __name__=='__main__':
    coupon_rate=0.1
    maturity_years=3
    ytm=0.12
    coupon_times=1
    par_value=1000
    mtype='macaulay_duration'
    change_type='coupon_rate'
    coupon_rate_change=[-250,-200,-150,-100,-50,50,100,150,200,250]
    maturity_years_change=[-5,-4,-3,-2,-1,1,2,3,4,5,6,7,8,9,10]
    ytm_change=[-100,-80,-60,-40,-20,20,40,60,80,100]
    coupon_times_list=[1,2,4,6,12,24]
    
    df=macaulay_theorem(coupon_rate,maturity_years,ytm,coupon_times,mtype='macaulay_duration')
    df=macaulay_theorem(coupon_rate,maturity_years,ytm,coupon_times,change_type='maturity_years')
    df=macaulay_theorem(coupon_rate,maturity_years,ytm,coupon_times,change_type='ytm')
    df=macaulay_theorem(coupon_rate,maturity_years,ytm,coupon_times,change_type='coupon_times')
    
    mtype='modified_duration'
    df=macaulay_theorem(coupon_rate,maturity_years,ytm,coupon_times,mtype='modified_duration')
    df=macaulay_theorem(coupon_rate,maturity_years,ytm,coupon_times,mtype='dollar_duration')
    df=macaulay_theorem(coupon_rate,maturity_years,ytm,coupon_times,mtype='efficient_duration')
    df=macaulay_theorem(coupon_rate,maturity_years,ytm,coupon_times,mtype='closed_form_duration')
    df=macaulay_theorem(coupon_rate,maturity_years,ytm,coupon_times,mtype='convexity')

def macaulay_theorem(
                    coupon_rate,
                    maturity_years,
                    ytm,
                    coupon_times=2,
                    par_value=1000,
                    mtype='macaulay_duration',#麦考利久期
                    change_type='coupon_rate',   #变化的因素
                    #coupon_rate_change=[-250,-200,-150,-100,-50,50,100,150,200,250],#基点
                    coupon_rate_change=[-100,-80,-60,-40,-20,20,40,60,80,100],#基点
                    maturity_years_change=[-5,-4,-3,-2,-1,1,2,3,4,5,6,7,8,9,10],#到期年数
                    ytm_change=[-100,-80,-60,-40,-20,20,40,60,80,100],#基点
                    coupon_times_list=[1,2,4,6,12,24],#每年票息发放次数
                    ):

    """
    功能：绘制久期/凸度受到各种因素变化的影响：票息率，到期年数，市场利率，每年票息次数
    """
    
    # 检查计算类型
    mtype_list=['macaulay_duration','modified_duration','dollar_duration', \
               'efficient_duration','closed_form_duration','convexity']
    if not (mtype in mtype_list):
        print("  #Error(macaulay_theorem): unsupported duration/convexity",mtype)
        print("  Supported:",mtype_list)
        return None
    
    # 检查因素项目
    change_type_list=['coupon_rate','maturity_years','ytm','coupon_times']
    if not (change_type in change_type_list):
        print("  #Error(macaulay_theorem): unsupported risk factor",change_type)
        print("  Supported:",change_type_list)
        return None
    
    # 其他检查
    if mtype=='efficient_duration' and change_type!='ytm':
        print("  #Warning(macaulay_theorem): 有效久期仅适用于到期收益率(市场利率)的变化")
        return None
    
    import pandas as pd
    df=pd.DataFrame(columns=('coupon_rate','maturity_years', \
                             'ytm','coupon_times','par_value',mtype))
    # 计算因素未改变时的久期或凸度
    p0=calc_macaulay(coupon_rate=coupon_rate,maturity_years=maturity_years, \
                     ytm=ytm,coupon_times=coupon_times,par_value=par_value, \
                     mtype=mtype,rate_change=0)
    s=pd.Series({'coupon_rate':coupon_rate,'maturity_years':maturity_years, \
                 'ytm':ytm,'coupon_times':coupon_times,'par_value':par_value, \
                 mtype:p0})
    try:
        df=df.append(s, ignore_index=True)
    except:
        df=df._append(s, ignore_index=True)

    # 改变风险因素1：票息率
    if change_type == 'coupon_rate':
        factor_list=[]
        for f in coupon_rate_change:
            f1=round(coupon_rate + f/10000,4)
            if f1 <= 0: continue
            factor_list=factor_list + [f1]
            
        for f1 in factor_list:
            p1=calc_macaulay(coupon_rate=f1,maturity_years=maturity_years, \
                             ytm=ytm,coupon_times=coupon_times,par_value=par_value, \
                             mtype=mtype,rate_change=0)
            s=pd.Series({'coupon_rate':f1,'maturity_years':maturity_years, \
                         'ytm':ytm,'coupon_times':coupon_times,'par_value':par_value, \
                         mtype:p1})
            try:
                df=df.append(s, ignore_index=True)
            except:
                df=df._append(s, ignore_index=True)
                
        #按照升序排序
        df.sort_values(by=[change_type],ascending=[True],inplace=True)
        #指定索引
        df.reset_index(drop=True,inplace=True)
        
        # 变化百分比：限coupon_rate和ytm
        df['coupon_rate%']=df['coupon_rate'].apply(lambda x:round(x*100,2))
        df['ytm%']=df['ytm'].apply(lambda x:round(x*100,2))
        
        # 绘图，横轴数值转换为字符串，以便逐点显示
        df['coupon_rate%_str']=df['coupon_rate%'].astype(str)
        plt.plot(df['coupon_rate%_str'],df[mtype],color='red',marker='o')
        
        # 绘制竖线
        xpos=str(round(coupon_rate*100,2))
        ymax=df[mtype]
        ymin=min(df[mtype])
        plt.vlines(x=xpos,ymin=ymin,ymax=p0,ls=":",colors="blue")

        titletxt="债券的利率风险：票息率变化的影响"
        footnote1='票息率%' 

    # 改变风险因素2：到期年数
    if change_type == 'maturity_years':
        factor_list=[]
        for f in maturity_years_change:
            f1=maturity_years + f
            if f1 <= 0: continue
            factor_list=factor_list + [f1]
            
        for f1 in factor_list:
            p1=calc_macaulay(coupon_rate=coupon_rate,maturity_years=f1, \
                             ytm=ytm,coupon_times=coupon_times,par_value=par_value, \
                             mtype=mtype,rate_change=0)
            s=pd.Series({'coupon_rate':coupon_rate,'maturity_years':f1, \
                         'ytm':ytm,'coupon_times':coupon_times,'par_value':par_value, \
                         mtype:p1})
            try:
                df=df.append(s, ignore_index=True)
            except:
                df=df._append(s, ignore_index=True)
                
        #按照升序排序
        df.sort_values(by=[change_type],ascending=[True],inplace=True)
        #指定索引
        df.reset_index(drop=True,inplace=True)
        
        # 变化百分比：限coupon_rate和ytm
        df['coupon_rate%']=df['coupon_rate'].apply(lambda x:round(x*100,2))
        df['ytm%']=df['ytm'].apply(lambda x:round(x*100,2))
        
        # 绘图，横轴数值转换为字符串，以便逐点显示
        df['maturity_years_str']=df['maturity_years'].astype(str)
        plt.plot(df['maturity_years_str'],df[mtype],color='red',marker='o')
        
        # 绘制竖线
        xpos=str(maturity_years)+'.0' #为匹配字符串形式的年数
        ymax=df[mtype]
        ymin=min(df[mtype])
        plt.vlines(x=xpos,ymin=ymin,ymax=p0,ls=":",colors="blue")

        titletxt="债券的利率风险：到期年数变化的影响"
        footnote1='到期年数' 

    # 改变风险因素3：市场利率/到期收益率
    if change_type == 'ytm':
        factor_list=[]
        for f in ytm_change:
            f1=round(ytm + f/10000,4)
            if f1 <= 0: continue
            factor_list=factor_list + [f1]
            
        for f1 in factor_list:
            p1=calc_macaulay(coupon_rate=coupon_rate,maturity_years=maturity_years, \
                             ytm=f1,coupon_times=coupon_times,par_value=par_value, \
                             mtype=mtype,rate_change=0)
            s=pd.Series({'coupon_rate':coupon_rate,'maturity_years':maturity_years, \
                         'ytm':f1,'coupon_times':coupon_times,'par_value':par_value, \
                         mtype:p1})
            try:
                df=df.append(s, ignore_index=True)
            except:
                df=df._append(s, ignore_index=True)
                
        #按照升序排序
        df.sort_values(by=[change_type],ascending=[True],inplace=True)
        #指定索引
        df.reset_index(drop=True,inplace=True)
        
        # 变化百分比：限coupon_rate和ytm
        df['coupon_rate%']=df['coupon_rate'].apply(lambda x:round(x*100,2))
        df['ytm%']=df['ytm'].apply(lambda x:round(x*100,2))
        
        # 绘图，横轴数值转换为字符串，以便逐点显示
        df['ytm%_str']=df['ytm%'].astype(str)
        plt.plot(df['ytm%_str'],df[mtype],color='red',marker='o')
        
        # 绘制竖线
        xpos=str(round(ytm*100,2))
        ymax=df[mtype]
        ymin=min(df[mtype])
        plt.vlines(x=xpos,ymin=ymin,ymax=p0,ls=":",colors="blue")

        titletxt="债券的利率风险：市场利率(到期收益率)的影响"
        footnote1='市场利率%' 

    # 改变风险因素4：年付息次数
    if change_type == 'coupon_times':
        factor_list=[]
        for f in coupon_times_list:
            f1=f
            if f1 <= 0: continue
            factor_list=factor_list + [f1]
            
        for f1 in factor_list:
            p1=calc_macaulay(coupon_rate=coupon_rate,maturity_years=maturity_years, \
                             ytm=ytm,coupon_times=f1,par_value=par_value, \
                             mtype=mtype,rate_change=0)
            s=pd.Series({'coupon_rate':coupon_rate,'maturity_years':maturity_years, \
                         'ytm':ytm,'coupon_times':f1,'par_value':par_value, \
                         mtype:p1})
            try:
                df=df.append(s, ignore_index=True)
            except:
                df=df._append(s, ignore_index=True)
                
        #按照升序排序
        df.sort_values(by=[change_type],ascending=[True],inplace=True)
        #指定索引
        df.reset_index(drop=True,inplace=True)
        
        # 变化百分比：限coupon_rate和ytm
        df['coupon_rate%']=df['coupon_rate'].apply(lambda x:round(x*100,2))
        df['ytm%']=df['ytm'].apply(lambda x:round(x*100,2))
        
        # 绘图，横轴数值转换为字符串，以便逐点显示
        df['coupon_times_str']=df['coupon_times'].astype(str)
        plt.plot(df['coupon_times_str'],df[mtype],color='red',marker='o')
        
        # 绘制竖线
        xpos=str(coupon_times)+'.0' #为匹配字符串形式的年数
        ymax=df[mtype]
        ymin=min(df[mtype])
        plt.vlines(x=xpos,ymin=ymin,ymax=p0,ls=":",colors="blue")

        titletxt="债券的利率风险：年付息次数变化的影响"
        footnote1='年付息次数' 


    # 绘图标题和脚注   
    mtype_list_cn=['麦考利久期','修正久期','美元久期','有效久期','封闭久期','凸度']
    mpos=mtype_list.index(mtype)
    ylabel_txt=mtype_list_cn[mpos]
    
    plt.ylabel(ylabel_txt,fontsize=ylabel_txt_size)
    footnote2="\n"+"债券面值"+str(par_value)+"，票面利率"+str(round(coupon_rate*100,2))+"%，"
    footnote3="每年付息次数"+str(coupon_times)+"，到期年数"+str(maturity_years)
    footnote4="，到期收益率"+str(round(ytm*100,2))+"%"

    footnote=footnote1+footnote2+footnote3+footnote4
    plt.title(titletxt,fontsize=title_txt_size,fontweight='bold')
    plt.xlabel(footnote,fontsize=xlabel_txt_size)    
    plt.xticks(rotation=30)

    plt.gca().set_facecolor('whitesmoke')        
    plt.show(); plt.close()
    
    return df



#==============================================================================
#==============================================================================
#==============================================================================


