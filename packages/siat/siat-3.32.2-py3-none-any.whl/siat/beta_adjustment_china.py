# -*- coding: utf-8 -*-

"""
版权：王德宏，北京外国语大学国际商学院
功能：计算CAPM模型贝塔系数的滨田调整，仅限于中国股票
版本：2021-11-22
"""

#==============================================================================
#关闭所有警告
import warnings; warnings.filterwarnings('ignore')
from siat.common import *
from siat.translate import *
from siat.grafix import *
from siat.security_prices import *
from siat.security_price2 import *
from siat.beta_adjustment import *
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
    ticker="600606.SS" 
    start='2015-1-1'
    end='2021-12-31'
    period_type='annual'
    period_type='quarterly'
    period_type='all'
    
def prepare_hamada_is_ak(ticker,start,end,period_type='all'):
    """
    从akshare获取利润表数据
    获取的项目：所得税费用，税前利润
    """

    #是否中国股票
    result,prefix,suffix=split_prefix_suffix(ticker)
    if not (suffix in ['SS','SZ']):
        print("  #Error(prepare_hamada_is_ak): not a stock in China",ticker)
        return None        
    
    #抓取利润表
    import akshare as ak
    try:
        fs = ak.stock_financial_report_sina(stock=prefix, symbol="利润表")
    except:
        print("  #Error(prepare_hamada_is_ak): no income stmt available for",ticker)
        return None        
    
    fs1=fs.drop_duplicates(subset=['报表日期'],keep='first') #去重
    fs1.sort_values(by=['报表日期'],ascending=True,inplace=True)   #升序排序
    
    #重建索引，排序
    fs1['date']=pd.to_datetime(fs1['报表日期'])
    fs1.set_index('date',inplace=True)

    #提取需要的项目：所得税费用，税前利润
    fs1['Income Tax Expense']=fs1['减：所得税费用'].astype('float')
    fs1['Income Before Tax']=fs1['四、利润总额'].astype('float')
    fs1['Net Income']=fs1['五、净利润'].astype('float')
    fs2=fs1[['Income Before Tax','Income Tax Expense','Net Income']].copy()
    #fs2['Profit Margin']=fs2['Income Before Tax']-fs2['Income Tax Expense']
    
    #过滤日期和类型
    valid,start1,end1=check_period(start,end)
    if not valid:
        print("  #Warning(prepare_hamada_is_ak): invalid period",start,end)
        fs3=fs2
    else:
        fs2a=fs2[fs2.index >=start1]
        fs3=fs2a[fs2a.index <=end1]
    
    fs3['Year']=fs3.index.year
    fs3['Month']=fs3.index.month
    period_type=period_type.lower()
    if period_type=='annual':
        fs4=fs3[fs3['Month']==12]
    else:
        fs4=fs3
    fs5=fs4[['Income Before Tax','Income Tax Expense','Net Income']]
    
    return fs5

if __name__=='__main__':
    prepare_hamada_is_ak('600519.SS','2018-1-1','2020-12-31')    
    prepare_hamada_is_ak('600519.SS','2010-1-1','2020-12-31',period_type='annual')

#==============================================================================
if __name__=='__main__':
    ticker="600519.SS" 
    start='2015-1-1'
    end='2021-12-31'
    period_type='annual'
    period_type='quarterly'
    period_type='all'
    
def prepare_hamada_bs_ak(ticker,start,end,period_type='all'):
    """
    从akshare获取资产负债表数据
    获取的项目：负债合计，股东权益合计
    """

    #是否中国股票
    result,prefix,suffix=split_prefix_suffix(ticker)
    if not (suffix in ['SS','SZ']):
        print("  #Error(prepare_hamada_is_ak): not a stock in China",ticker)
        return None        
    
    #抓取资产负债表
    import akshare as ak
    try:
        fs = ak.stock_financial_report_sina(stock=prefix, symbol="资产负债表")
    except:
        print("  #Error(prepare_hamada_bs_ak): no balance sheet available for",ticker)
        return None        
    
    fs1=fs.drop_duplicates(subset=['报表日期'],keep='first') #去重
    fs1.sort_values(by=['报表日期'],ascending=True,inplace=True)   #升序排序
    
    #重建索引，排序
    fs1['date']=pd.to_datetime(fs1['报表日期'])
    fs1.set_index('date',inplace=True)

    #提取需要的项目：所得税费用，税前利润
    fs1['Total Liab']=fs1['负债合计'].astype('float')
    fs1['Total Stockholder Equity']=fs1['所有者权益(或股东权益)合计'].astype('float')
    fs1['Total Assets']=fs1['资产总计'].astype('float')
    fs2=fs1[['Total Liab','Total Stockholder Equity','Total Assets']].copy()
    #fs2['Total Assets2']=fs2['Total Liab']+fs2['Total Stockholder Equity']
    
    #过滤日期和类型
    valid,start1,end1=check_period(start,end)
    if not valid:
        print("  #Warning(prepare_hamada_is_ak): invalid period",start,end)
        fs3=fs2
    else:
        fs2a=fs2[fs2.index >=start1]
        fs3=fs2a[fs2a.index <=end1]
    
    fs3['Year']=fs3.index.year
    fs3['Month']=fs3.index.month
    period_type=period_type.lower()
    if period_type=='annual':
        fs4=fs3[fs3['Month']==12]
    else:
        fs4=fs3
    fs5=fs4[['Total Liab','Total Stockholder Equity','Total Assets']]
    
    return fs5

if __name__=='__main__':
    prepare_hamada_bs_ak('600519.SS','2018-1-1','2020-12-31')    
    prepare_hamada_bs_ak('600519.SS','2010-1-1','2020-12-31',period_type='annual')

#==============================================================================
if __name__ =="__main__":
    ticker='600606.SS'
    start='2017-1-1'
    end='2020-9-30'
    period_type='all'

def prepare_hamada_ak(ticker,start,end,period_type='all'):
    """
    功能：从akshare下载财报数据，计算hamada模型需要的因子
    局限：只能下载中国股票的财报
    输入：股票代码
    输出：
        寻找数据项：所得税费用，税前利润，计算实际税率；
        总负债，所有者权益，计算财务杠杆
    数据框, CFLB，贝塔Lev对贝塔Unlev的倍数
    年度列表
    """
    print("  Searching for financial information for",ticker,"...")
    
    #利润表
    is1=prepare_hamada_is_ak(ticker,start,end,period_type)

    is1['tax rate']=is1['Income Tax Expense']/is1['Income Before Tax']
    import pandas as pd
    tax=pd.DataFrame(is1['tax rate'])

    #资产负债表
    bs1=prepare_hamada_bs_ak(ticker,start,end,period_type)

    bs1['lev ratio']=bs1['Total Liab']/bs1["Total Stockholder Equity"]
    lev=pd.DataFrame(bs1['lev ratio'])
    
    #合成，计算
    fac=pd.merge(lev,tax,how='left',left_index=True,right_index=True)
    fac['CFLB%']=1/(1+(1/fac['lev ratio'])*(1/abs(1-fac['tax rate'])))*100
    fac['lev_unlev']=1+fac['lev ratio']*(1-fac['tax rate'])
    
    fac['ticker']=ticker

    return fac

if __name__ =="__main__":
    prepare_hamada_ak("600519.SS",'2018-1-1','2020-12-31')
    prepare_hamada_ak("600519.SS",'2018-1-1','2020-12-31','all')

#==============================================================================
if __name__ =="__main__":
    stkcd='600519.SS'
    mktidx='000001.SS'
    start='2010-1-1'
    end='2020-12-31'

def get_beta_hamada_china_v0(stkcd,mktidx,start,end,printout=True,graph=True):
    """
    函数功能：使用Hamada(1972)方法，计算无杠杆贝塔系数
    输入参数：
    stkcd: 股票代码
    mktidx: 指数代码
    输出数据：显示CAPM市场模型回归的beta, 以及调整后的beta系数
    返回数据：CAPM的beta, Hamada beta，CFLB(债务融资对CAPM beta系数的贡献率)
    注：本函数废弃
    """
    
    #计算Hamada参数，并返回可用的年度列表
    fac=prepare_hamada_ak(stkcd,start,end,period_type='annual')
    if fac is None:
        print("#Error(get_beta_hamada_china): no financial info available for",stkcd)
        return None
    fac['year']=fac.index.strftime("%Y")
    yearlist=list(fac['year'])
        
    #读取股价并准备好收益率数据
    try:
        R=prepare_capm(stkcd,mktidx,start,end)
    except:
        print("  #Error(get_beta_hamada_china): preparing CAPM data failed!")
        print("  Info:",stkcd,mktidx,yearlist)              
        return None

    if (R is None):
        print("  #Error(get_beta_hamada_china): no CAPM beta calculated")
        return None
    if (len(R) == 0):
        print("  #Error(get_beta_hamada_china): no CAPM beta available")
        return None
    
    R=R.dropna()
    
    #用于保存beta(CAPM)和beta(Hamada)
    import pandas as pd
    betas=pd.DataFrame(columns=('Year','Beta(CAPM)','Beta(Unlevered)','CFLB%', \
                                'lev ratio','tax rate'))

    from scipy import stats    
    for year in yearlist:
        r=R[R['Year']==year]
        if len(r) != 0:   
            output=stats.linregress(r['Close_x'],r['Close_y'])
            (beta_capm,alpha,r_value,p_value,std_err)=output               
            
            #Hamada无杠杆因子
            lev_unlev=fac[fac['year']==year]['lev_unlev'].values[0]
            beta_hamada=beta_capm/lev_unlev
            cflb=fac[fac['year']==year]['CFLB%'].values[0]            
            
            lev_ratio=fac[fac['year']==year]['lev ratio'].values[0]
            tax_rate=fac[fac['year']==year]['tax rate'].values[0]
            row=pd.Series({'Year':year,'Beta(CAPM)':beta_capm, \
                           'Beta(Unlevered)':beta_hamada,'CFLB%':cflb, \
                            'lev ratio':lev_ratio,'tax rate':tax_rate})
            try:
                betas=betas.append(row,ignore_index=True)
            except:
                betas=betas._append(row,ignore_index=True)

    betas.set_index(["Year"], inplace=True)

    import datetime as dt; today=dt.date.today()
    if printout == True: 
        pd.set_option('display.max_columns', 1000)
        pd.set_option('display.width', 1000)
        pd.set_option('display.max_colwidth', 1000)
        print("\n=有杠杆（CAPM）对比无杠杆（Unlevered）贝塔系数=")
        betas1=betas[['Beta(CAPM)','Beta(Unlevered)','CFLB%']]
        print(betas1)
        print("\n*** 数据来源：新浪，"+str(today))
        
    if graph == True:
        model="有/无杠杆贝塔系数趋势对比"
        draw2_betas(model,mktidx,stkcd,betas)
        
        #绘制CFLB
        if len(betas)<=1: return betas
        
        plt.plot(betas['CFLB%'],marker='o',color='red',lw=3,label='CFLB%')
        
        cflb_mean=betas['CFLB%'].mean()
        plt.axhline(y=cflb_mean,color='b',linestyle=':',label='均值线') 
        
        title1=ticker_name(stkcd)+": 财务杠杆对贝塔系数的贡献度(CFLB)"+ \
            "\n(基于"+ticker_name(mktidx)+")"
        plt.title(title1,fontsize=12,fontweight='bold')
        plt.ylabel("CFLB%",fontsize=12,fontweight='bold')
        
        
        footnote="注：CFLB均值="+str(round(cflb_mean,2))+'%\n数据来源：新浪，'+str(today)
        plt.xlabel(footnote)
        
        plt.grid(ls='-.')
        #查看可用的样式：print(plt.style.available)
        #样式：bmh(好),classic,ggplot(好，图大)，tableau-colorblind10，
        #样式：seaborn-bright，seaborn-poster，seaborn-whitegrid
        plt.style.use('bmh')
        plt.legend(loc='best')
        plt.gcf().autofmt_xdate() # 优化标注（自动倾斜）
        plt.gca().set_facecolor('whitesmoke')
        
        #plt.xticks(rotation=30)
        plt.show()         

    return betas
    
if __name__=='__main__':
    betas=get_beta_hamada_china('000002.SZ','399001.SZ','2000-1-1','2021-12-31')

#==============================================================================
def draw_hamada_factors_china(stkcd,mktidx,betas):
    """
    功能：绘制Hamada模型因子的变化折线图，企业实际所得税税率，资产负债率，CFLB
    """
    if len(betas)<=1: return
    
    #计算资产负债率：由 D/E到 D/(A=D+E)
    betas['Debt/Assets%']=1/(1+1/(betas['lev ratio']/100))*100

    #fig=plt.figure(figsize=(12.8,6.4))
    fig=plt.figure()
    ax1=fig.add_subplot(111)
    ax1.plot(betas['CFLB%'],marker='o',color='green',lw=3,label='CFLB%')
    ax1.plot(betas['Debt/Assets%'],marker='o',color='red',lw=2,ls='--', \
             label='资产负债率%')
    ax1.set_ylabel("CFLB%, 资产负债率%")
    ax1.legend(loc='upper left') 
    ax1.set_xticklabels(betas.index,rotation=45)
    
    ax2=ax1.twinx()
    ax2.plot(betas['tax rate'],marker='o',color='black',lw=2,ls='-.', \
             label='实际税率%')
    ax2.set_ylabel('实际税率%')  
    ax2.legend(loc='lower right')
    ax2.set_xticklabels(betas.index,rotation=45)
    
    title1=ticker_name(stkcd)+": 滨田因子对贝塔系数的影响"+ \
            "\n(基于"+ticker_name(mktidx)+")"
    plt.title(title1,fontsize=12,fontweight='bold')
    plt.style.use('ggplot')
    
    plt.gca().set_facecolor('whitesmoke')
    plt.show()     
    
    return

if __name__ =="__main__":
    draw_hamada_factors_china('000002.SZ','399001.SZ',betas)
#==============================================================================
#==============================================================================
#==============================================================================
if __name__ =="__main__":
    stkcd='600606.SS'
    mktidx='000001.SS'
    start='2018-1-1'
    end='2021-9-30'
    period_type='all'

def get_beta_hamada_china(stkcd,mktidx,start,end,period_type='all', \
                           printout=True,graph=True):
    """
    函数功能：使用Hamada(1972)方法，计算无杠杆贝塔系数，绘图，仅限于中国股票
    输入参数：
    stkcd: 股票代码
    mktidx: 指数代码
    输出数据：显示CAPM市场模型回归的beta, 以及调整后的beta系数
    返回数据：CAPM的beta, Hamada beta，CFLB(债务融资对CAPM beta系数的贡献率)
    特点：既能处理年报，也能处理季报
    """
    
    #计算Hamada参数，并返回可用的年度列表
    fac=prepare_hamada_ak(stkcd,start,end,period_type)
    if fac is None:
        print("  #Error(get_beta_hamada_china2): no financial info available for",stkcd)
        return None
    
    datecvt=lambda x: str(x.strftime("%Y-%m-%d"))
    fac['fsdate']=fac.index.date
    fac['fsdate']=fac['fsdate'].apply(datecvt)
        
    #读取股价并准备好收益率数据
    try:
        R=prepare_capm(stkcd,mktidx,start,end)
    except:
        print("  #Error(get_beta_hamada_china): preparing CAPM data failed for",stkcd,mktidx)
        return None
    if R is None:
        print("  #Error(get_beta_hamada_china): info in CAPM inaccessible for",stkcd,mktidx)
        return None
    if len(R) == 0:
        print("  #Error(get_beta_hamada_china): zero record found in CAPM for",stkcd,mktidx)
        return None    
    
    R=R.dropna()
    R['prcdate']=R.index.date
    R['prcdate']=R['prcdate'].apply(datecvt)
    
    #用于保存beta(CAPM)和beta(Hamada)
    import pandas as pd
    betas=pd.DataFrame(columns=('Date','Beta(CAPM)','Beta(Unlevered)','CFLB%'))
    fsdatelist=list(fac['fsdate'])
    from scipy import stats    
    for d in fsdatelist:
        dstart=date_adjust(d,adjust=-365)
        r=R[R['prcdate'] >= dstart]
        r=r[r['prcdate'] <= d]
        if len(r) != 0:   
            output=stats.linregress(r['Close_x'],r['Close_y'])
            (beta_capm,alpha,r_value,p_value,std_err)=output               
            
            #Hamada无杠杆因子
            lev_unlev=fac[fac['fsdate']==d]['lev_unlev'].values[0]
            beta_hamada=beta_capm/lev_unlev
            cflb=fac[fac['fsdate']==d]['CFLB%'].values[0]            

            row=pd.Series({'Date':d,'Beta(CAPM)':beta_capm, \
                           'Beta(Unlevered)':beta_hamada,'CFLB%':cflb})
            try:
                betas=betas.append(row,ignore_index=True)
            except:
                betas=betas._append(row,ignore_index=True)
    betas.set_index(["Date"], inplace=True)

    #打印
    import datetime as dt; today=dt.date.today()
    if printout == True: 
        pd.set_option('display.max_columns', 1000)
        pd.set_option('display.width', 1000)
        pd.set_option('display.max_colwidth', 1000)
        print("\n=有杠杆（CAPM）对比无杠杆（Unlevered）贝塔系数=")
        print(betas)
        print("\n*** 数据来源：新浪，"+str(today))
    
    #绘图：两种杠杆对比图，CFLB图
    if graph == True:
        if len(betas)<=1: 
            print("  #Notice(get_beta_hamada_china): too few info for graphics of",stkcd)
            return betas
        
        #图1：绘制Hamada对比图
        titletxt=ticker_name(stkcd)+"：CAPM/无杠杆贝塔系数对比"
        import datetime; today = datetime.date.today()
        footnote="注: 基于"+ticker_name(mktidx)
        footnote2="\n数据来源: 新浪,"+str(today)
        #draw2_betas(model,mktidx,stkcd,betas)
        plot_2lines(betas,'Beta(CAPM)','CAPM贝塔系数', \
                betas,'Beta(Unlevered)','无杠杆贝塔系数', \
                '贝塔系数',titletxt,footnote+footnote2,hline=1,vline=0,resample_freq='H')
        
        #图2：绘制CFLB单图
        """
        plt.plot(betas['CFLB%'],marker='o',color='red',lw=3,label='CFLB%')
        """
        #均值
        cflb_avg=betas['CFLB%'].mean()
        cflb_avg_txt='，CFLB%均值为'+str(round(cflb_avg,1))+'%'
        """
        plt.axhline(y=cflb_avg,color='b',linestyle=':',label=cflb_avg_txt)
        
        #plt.title(title1,fontsize=12,fontweight='bold')
        plt.title(title1)
        #plt.ylabel("CFLB %",fontsize=12,fontweight='bold')
        plt.xlabel(footnote+footnote2)
        
        plt.grid(ls='-.')
        #查看可用的样式：print(plt.style.available)
        #样式：bmh(好),classic,ggplot(好，图大)，tableau-colorblind10，
        #样式：seaborn-bright，seaborn-poster，seaborn-whitegrid
        plt.style.use('bmh')
        plt.gcf().autofmt_xdate() # 优化标注（自动倾斜）
        plt.legend(loc='best')
        plt.show(); plt.close()
        """
        titletxt=ticker_name(stkcd)+": 财务杠杆对于贝塔系数的贡献度(CFLB)"
        plot_line(betas,'CFLB%','CFLB%','财务杠杆对于贝塔系数的贡献度%',titletxt, \
                  footnote+cflb_avg_txt+footnote2,power=6)
        
        #图3：绘制CFLB+财务杠杆双图
        df1=betas; df2=fac.set_index(["fsdate"])
        ticker1=ticker2=stkcd
        colname1='CFLB%'; colname2='lev ratio'
        label1='CFLB%'; label2='财务杠杆'
        titletxt=ticker_name(stkcd)+": CFLB与财务杠杆之间的关系"
        footnote='注: 这里的财务杠杆使用的是负债/所有者权益'
        
        plot_line2_twinx(df1,ticker1,colname1,label1,df2,ticker2,colname2,label2, \
        titletxt,footnote+footnote2)
        
        #图4：绘制CFLB+税率双图
        #df1=betas; df2=fac.set_index(["fsdate"])
        #ticker1=ticker2=stkcd
        colname1='CFLB%'; colname2='tax rate'
        label1='CFLB%'; label2='实际税率'
        titletxt=ticker_name(stkcd)+": CFLB与税率之间的关系"
        footnote='注: 这里使用的是实际税率'
        
        plot_line2_twinx(df1,ticker1,colname1,label1,df2,ticker2,colname2,label2, \
        titletxt,footnote+footnote2)
            
    return betas
    
if __name__=='__main__':
    betas1=get_beta_hamada_china('000002.SZ','399001.SZ','2010-1-1','2021-12-31','annual')

#==============================================================================
#==============================================================================
#==============================================================================












    