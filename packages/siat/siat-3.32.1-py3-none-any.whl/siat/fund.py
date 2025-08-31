# -*- coding: utf-8 -*-
"""
本模块功能：基金，本模块已弃用！！！被fund_china.py替代
所属工具包：证券投资分析工具SIAT 
SIAT：Security Investment Analysis Tool
创建日期：2020年10月17日
最新修订日期：2020年10月18日
作者：王德宏 (WANG Dehong, Peter)
作者单位：北京外国语大学国际商学院
版权所有：王德宏
用途限制：仅限研究与教学使用，不可商用！商用需要额外授权。
特别声明：作者不对使用本工具进行证券投资导致的任何损益负责！
"""

#==============================================================================
#关闭所有警告
import warnings; warnings.filterwarnings('ignore')
from siat.bond_base import *
#==============================================================================
if __name__=='__main__':
    txt='QDII-指数'

def strlen(txt):
    """
    功能：计算中英文混合字符串的实际长度
    """
    lenTxt = len(txt) 
    lenTxt_utf8 = len(txt.encode('utf-8')) 
    size = int((lenTxt_utf8 - lenTxt)/2 + lenTxt)    

    return size

#==============================================================================
def check_period(fromdate, todate):
    """
    功能：根据开始/结束日期检查日期与期间的合理性
    输入参数：
    fromdate：开始日期。格式：YYYY-MM-DD
    enddate：开始日期。格式：YYYY-MM-DD
    输出参数：
    validity：期间合理性。True-合理，False-不合理
    start：开始日期。格式：datetime类型
    end：结束日期。格式：datetime类型
    """
    import pandas as pd
    
    #测试开始日期的合理性
    try:
        start=pd.to_datetime(fromdate)
    except:
        print("*** 错误#1(check_period)，无效的日期:",fromdate)
        return None, None, None         
    
    #测试结束日期的合理性
    try:
        end=pd.to_datetime(todate)
    except:
        print("*** 错误#2(check_period)，无效的日期:",todate)
        return None, None, None          
    
    #测试日期期间的合理性
    if start > end:
        print("*** 错误#3(check_period)，无效的日期期间: 从",fromdate,"至",todate)
        return None, None, None     

    return True, start, end

if __name__ =="__main__":
    check_period('2020-1-1','2020-2-4')
    check_period('2020-1-1','2010-2-4')

#==============================================================================

#==============================================================================

if __name__=='__main__':
    fund_type='全部类型'

def pof_list_china(fund_type='全部类型',printout=True):
    """
    功能：抓取公募基金列表，按照基金类型列表，按照基金名称拼音排序
    """
    print("Searching for publicly offering fund (POF) information in China ...")
    import akshare as ak
    
    #基金基本信息：基金代码，基金简称，基金类型
    df = ak.fund_em_fund_name()
    df.sort_values(by=['拼音全称'],na_position='first',inplace=True)
    df.drop_duplicates(subset=['基金代码','基金类型'], keep='first',inplace=True)    
    
    #获取基金类型列表，并去掉重复项
    typelist=list(set(list(df['基金类型'])))
    #判断类型是否支持
    if fund_type not in typelist+['全部类型']:
        print("#Error(fund_list_china): unsupported fund type:",fund_type)
        print("Supported fund_type:",typelist+['全部类型'])
        return None

    #摘取选定的基金类型
    if fund_type != '全部类型':
        df2=df[df['基金类型']==fund_type]
    else:
        df2=df
    df3=df2[['基金简称','基金代码','基金类型']]
    df3.reset_index(drop=True,inplace=True) 
    
    #打印种类数量信息    
    if printout:
        num=len(df3)
        if fund_type != '全部类型':
            print("共找到",num,"支基金,","类型为"+fund_type)
            return df3
        
        print("\n======= 中国公募基金种类概况 =======")
        print("公募基金总数：","{:,}".format(num))
        print("其中包括：")
        
        typelist.sort(reverse=False)
        maxlen=0
        for t in typelist:
            tlen=strlen(t)
            if tlen > maxlen: maxlen=tlen
        maxlen=maxlen+1
        
        for t in typelist:
            tlen=strlen(t)
            n=len(df[df['基金类型']==t])
            prefix=' '*4+t+' '*(maxlen-tlen)+':'
            print(prefix,"{:,}".format(n),"\b,",round(n/num*100,2),'\b%')

        import datetime
        todaydt = datetime.date.today()
        print("来源：东方财富/天天基金,",todaydt)
        
    return df3

if __name__=='__main__':
    df=pof_list_china()

#==============================================================================
if __name__=='__main__':
    info_type='单位净值'
    fund_type='全部类型'

def oef_rank_china(info_type='单位净值',fund_type='全部类型'):
    """
    功能：中国开放式基金排名，单位净值，累计净值，手续费
    """
    typelist=['单位净值','累计净值','手续费']
    if info_type not in typelist:
        print("#Error(oef_rank_china): unsupported info type",info_type)
        print("Supported info type:",typelist)
        return None
    
    print("Searching for open-ended fund (OEF) information in China ...")
    import akshare as ak   
    
    #获取开放式基金实时信息
    df1 = ak.fund_em_open_fund_daily()
    collist=list(df1)
    nvname1=collist[2]
    nvdate=nvname1[:10]
    nvname2=collist[3]
    #修改列名
    df1.rename(columns={nvname1:'单位净值',nvname2:'累计净值'}, inplace=True) 
    #df1a=df1.drop(df1[df1['单位净值']==''].index)
    #df1b=df1a.drop(df1a[df1a['累计净值']==''].index)
    df1c=df1[['基金代码','基金简称','单位净值','累计净值','申购状态','赎回状态','手续费']]
    
    
    #获取所有公募基金类型信息
    df2 = ak.fund_em_fund_name()
    df2a=df2[['基金代码','基金类型']]
    
    #合成基金类型信息
    import pandas as pd
    df = pd.merge(df1c,df2a,on = ['基金代码'],how='left')
    #过滤基金类型
    if fund_type != '全部类型':
        fundtypelist=list(set(list(df['基金类型'])))
        if fund_type not in fundtypelist:
            print("#Error(oef_rank_china): unsupported fund type",fund_type)
            print("Supported fund type:",fundtypelist)
            return None
        df=df[df['基金类型']==fund_type]    
    
    if info_type == '单位净值':
        df.sort_values(by=['单位净值'],ascending=False,inplace=True)
        dfprint=df[['基金简称','基金代码','基金类型','单位净值','累计净值','手续费']]
        print("\n===== 中国开放式基金排名：单位净值最高前十名 =====")
    
    if info_type == '累计净值':
        df.sort_values(by=['累计净值'],ascending=False,inplace=True)
        dfprint=df[['基金简称','基金代码','基金类型','累计净值','单位净值','手续费']]
        print("\n===== 中国开放式基金排名：累计净值最高前十名 =====")        
    
    if info_type == '手续费':
        df.sort_values(by=['手续费'],ascending=False,inplace=True)
        dfprint=df[['基金简称','基金代码','基金类型','手续费']]
        print("\n===== 中国开放式基金排名：手续费最高前十名 =====")          
        
    #设置打印对齐
    pd.set_option('display.max_columns', 1000)
    pd.set_option('display.width', 1000)
    pd.set_option('display.max_colwidth', 1000)
    pd.set_option('display.unicode.ambiguous_as_wide', True)
    pd.set_option('display.unicode.east_asian_width', True)
    
    dfprint.dropna(inplace=True)
    dfprint.reset_index(drop=True,inplace=True)
    dfprint10=dfprint.head(10)
    #print(dfprint10.to_string(index=False))
    print(dfprint10)
    print("  共找到披露净值信息的开放式基金数量:",len(dfprint),'\b. ',end='')
    print("基金类型:",fund_type)
    
    print("  净值日期:",nvdate,'\b. ',end='')
    import datetime
    todaydt = datetime.date.today()
    print("  来源：东方财富/天天基金,",todaydt)        
    
    return df

if __name__=='__main__':
     df=oef_rank_china(info_type='单位净值')
     df=oef_rank_china(info_type='累计净值')
     df=oef_rank_china(info_type='手续费')

#==============================================================================
if __name__=='__main__':
    fund='519035'
    fromdate='2020-1-1'
    todate='2020-10-16'
    trend_type='净值'
    power=0
    twinx=False
    zeroline=False

def oef_trend_china(fund,fromdate,todate,trend_type='净值',power=0):
    """
    功能：开放式基金业绩趋势，单位净值，累计净值，近三个月收益率，同类排名，总排名
    """
    #检查走势类型
    trendlist=["净值","收益率","排名"]
    if trend_type not in trendlist:
        print("#Error(oef_trend_china): unsupported trend type:",trend_type)
        print("Supported trend types:",trendlist)
        return None
    
    #检查日期
    result,start,end=check_period(fromdate,todate)
    if not result:
        print("#Error(oef_trend_china): invalid date period:",fromdate,todate)
        return None
    """
    #转换日期格式
    import datetime
    startdate=datetime.datetime.strftime(start,"%Y-%m-%d")
    enddate=str(datetime.datetime.strftime(end,"%Y-%m-%d"))
    """
    print("Searching for open-ended fund (OEF) trend info in China ...")
    import akshare as ak   

    #开放式基金-历史数据
    import datetime; todaydt = datetime.date.today()
    source="来源：东方财富/天天基金"
    import siat.grafix as grf
    
    #绘制单位/累计净值对比图
    if trend_type == '净值':
        df1 = ak.fund_em_open_fund_info(fund=fund, indicator="单位净值走势")
        df1.rename(columns={'x':'date','y':'单位净值'}, inplace=True)
        df1['日期']=df1['date']
        df1.set_index(['date'],inplace=True) 
        
        df2 = ak.fund_em_open_fund_info(fund=fund, indicator="累计净值走势")
        df2.rename(columns={'x':'date','y':'累计净值'}, inplace=True)
        df2.set_index(['date'],inplace=True)       
        
        #合并
        import pandas as pd
        df = pd.merge(df1,df2,left_index=True,right_index=True,how='inner')
        dfp=df[(df['日期'] >= start)]
        dfp=dfp[(dfp['日期'] <= end)]
        
        #绘制双线图
        ticker1=fund; colname1='单位净值';label1='单位净值'
        ticker2=fund; colname2='累计净值';label2='累计净值'
        ylabeltxt='人民币元'
        titletxt="开放式基金的净值趋势："+fund
        
        footnote=source+', '+str(todaydt)
        grf.plot_line2(dfp,ticker1,colname1,label1, \
               dfp,ticker2,colname2,label2, \
               ylabeltxt,titletxt,footnote,power=power)
        return df
    
    #绘制累计收益率单线图
    if trend_type == '收益率':
        df = ak.fund_em_open_fund_info(fund=fund, indicator="累计收益率走势")
        df.rename(columns={'x':'date','y':'累计收益率'}, inplace=True)
        df['日期']=df['date']
        df.set_index(['date'],inplace=True) 
        dfp=df[(df['日期'] >= start)]
        dfp=dfp[(dfp['日期'] <= end)]        
    
        colname='累计收益率'; collabel='累计收益率%'
        ylabeltxt=''
        titletxt="开放式基金的累计收益率趋势："+fund
        footnote=source+', '+str(todaydt)
        grf.plot_line(dfp,colname,collabel,ylabeltxt,titletxt,footnote,power=power)    
        return df
    
    #绘制同类排名图：近三个月收益率
    if trend_type == '排名':
        df1 = ak.fund_em_open_fund_info(fund=fund, indicator="同类排名走势")
        df1.rename(columns={'x':'date','y':'同类排名','sc':'总排名'}, inplace=True)
        df1['日期']=df1['date']
        df1.set_index(['date'],inplace=True) 
        
        df2 = ak.fund_em_open_fund_info(fund=fund, indicator="同类排名百分比")
        df2.rename(columns={'x':'date','y':'同类排名百分比'}, inplace=True)
        df2.set_index(['date'],inplace=True)       
        
        #合并
        import pandas as pd
        df = pd.merge(df1,df2,left_index=True,right_index=True,how='inner')
        dfp=df[(df['日期'] >= start)]
        dfp=dfp[(dfp['日期'] <= end)]

        #绘制双线图：同类排名
        ticker1=fund; colname1='同类排名';label1='同类排名'
        ticker2=fund; colname2='同类排名百分比';label2='同类排名百分比'
        ylabeltxt=''
        titletxt="开放式基金的近三个月收益率排名趋势："+fund
        footnote=source+', '+str(todaydt)
        grf.plot_line2(dfp,ticker1,colname1,label1, \
               dfp,ticker2,colname2,label2, \
               ylabeltxt,titletxt,footnote,power=power,twinx=True)
        
        #    
        ticker2=fund; colname2='总排名';label2='开放式基金总排名'    
        grf.plot_line2(dfp,ticker1,colname1,label1, \
               dfp,ticker2,colname2,label2, \
               ylabeltxt,titletxt,footnote,power=power,twinx=True)            
        
        return df
    
#==============================================================================
if __name__=='__main__':
    pass

def mmf_rank_china():
    """
    功能：中国货币型基金排名，7日年化收益率%
    """
    
    print("Searching for money market fund (OEF) information in China ...")
    import akshare as ak   
    
    #获取货币型基金实时信息
    df = ak.fund_em_money_fund_daily()
    collist=list(df)
    nvname=collist[6]
    nvdate=nvname[:10]
    #修改列名
    df.rename(columns={nvname:'7日年化%'}, inplace=True) 
    #dfa=df.drop(df[df['7日年化%']==''].index)
    dfb=df[['基金代码','基金简称','7日年化%','成立日期','基金经理','手续费']]
    
    dfb.sort_values(by=['7日年化%'],ascending=False,inplace=True)
    dfprint=dfb[['基金简称','基金代码','7日年化%','基金经理','手续费']]
    print("\n======= 中国货币型基金排名：7日年化收益率最高前十名 =======")
        
    #设置打印对齐
    import pandas as pd
    pd.set_option('display.max_columns', 1000)
    pd.set_option('display.width', 1000)
    pd.set_option('display.max_colwidth', 1000)
    pd.set_option('display.unicode.ambiguous_as_wide', True)
    pd.set_option('display.unicode.east_asian_width', True)
    
    dfprint.dropna(inplace=True)
    dfprint.reset_index(drop=True,inplace=True)
    dfprint10=dfprint.head(10)
    #print(dfprint10.to_string(index=False))
    print(dfprint10)
    print("共找到披露收益率信息的货币型基金数量:",len(dfprint))
    
    print("收益率日期:",nvdate,'\b. ',end='')    
    import datetime
    todaydt = datetime.date.today()
    print("来源：东方财富/天天基金,",todaydt)        
    
    return df

if __name__=='__main__':
     df=mmf_rank_china()

#==============================================================================
if __name__=='__main__':
    fund='320019'
    fromdate='2020-1-1'
    todate='2020-10-16'
    power=0

def mmf_trend_china(fund,fromdate,todate,power=0):
    """
    功能：货币型基金业绩趋势，7日年化收益率
    """
    
    #检查日期
    result,start,end=check_period(fromdate,todate)
    if not result:
        print("#Error(mmf_trend_china): invalid date period:",fromdate,todate)
        return None
    import datetime
    startdate=datetime.datetime.strftime(start,"%Y-%m-%d")
    enddate=str(datetime.datetime.strftime(end,"%Y-%m-%d"))
    
    print("Searching for money market fund (MMF) trend info in China ...")
    import akshare as ak   

    #基金历史数据
    import datetime; dt = datetime.date.today()
    source="来源：东方财富/天天基金"
    import siat.grafix as grf
    
    #绘制收益率单线图
    df = ak.fund_em_money_fund_info(fund)
    df.sort_values(by=['净值日期'],ascending=True,inplace=True)
    df['7日年化%']=df['7日年化收益率'].astype("float")
    
    import pandas as pd
    df['date']=pd.to_datetime(df['净值日期'])
    df.set_index(['date'],inplace=True) 
    
    dfp = df[(df.index >= startdate)]
    dfp = dfp[(dfp.index <= enddate)]        
    
    colname='7日年化%'; collabel='7日年化%'
    ylabeltxt=''
    titletxt="货币型基金的7日年化收益率趋势："+fund
    footnote=source+', '+str(todaydt)
    grf.plot_line(dfp,colname,collabel,ylabeltxt,titletxt,footnote,power=power)    
    
    return df
    
    
#==============================================================================
#==============================================================================
#==============================================================================
#以下信息专注于中国内地基金信息，来源于akshare，暂时废弃！
#==============================================================================
#==============================================================================
def fund_member_china():
    """
    爬虫来源地址：https://zhuanlan.zhihu.com/p/97487003
    功能：获取中国证券投资基金业协会-会员机构综合查询
    返回：单次返回当前时刻所有历史数据
    处理：
    1、按照“机构（会员）名称”排序
    2、按照“机构（会员）名称”+“会员代表”去掉重复
    3、可解析出：公募基金管理公司，私募基金管理人
    """
    import akshare as ak
    
    #XXX会员机构综合查询
    df = ak.amac_member_info()
    
    #XXX私募基金管理人综合查询
    df = ak.amac_manager_info()
    
    #XXX证券公司私募基金子公司管理人信息
    df = ak.amac_member_sub_info()
    
    #XXX私募基金管理人基金产品
    df = ak.amac_fund_info()
    
    #XXX证券公司集合资管产品
    df = ak.amac_securities_info()
    
    #XXX证券公司直投基金：
    #中国证券投资基金业协会-信息公示-私募基金管理人公示-基金产品公示-证券公司直投基金
    df = ak.amac_aoin_info()
    
    #XXX证券公司私募投资基金
    df = ak.amac_fund_sub_info()
    
    #XXX基金公司及子公司集合资管产品
    #中国证券投资基金业协会-信息公示-私募基金管理人公示-基金产品公示-基金公司及子公司集合资管产品
    df = ak.amac_fund_account_info()
    
    #XXX期货公司集合资管产品
    #中国证券投资基金业协会-信息公示-私募基金管理人公示-基金产品公示-期货公司集合资管产品
    df = ak.amac_futures_info()
    
    #某个ETF基金的历史行情
    df = ak.fund_etf_hist_sina(symbol="sz169103")
    
    #==========================================================================
    #以下为公募数据：
    #爬虫来源地址：https://my.oschina.net/akshare/blog/4341149
    #XXX开放式基金净值：
    #基金代码，基金简称，单位净值，累计净值，申购状态，赎回状态，手续费
    df = ak.fund_em_daily()
    
    #XXX基金信息：单位净值走势
    df = ak.fund_em_info(fund="710001", indicator="单位净值走势")
    
    #XXX基金信息：累计净值走势
    df = ak.fund_em_info(fund="710001", indicator="累计净值走势")
    
    #XXX基金信息：累计收益率走势
    df = ak.fund_em_info(fund="710001", indicator="累计收益率走势")
    
    #XXX基金信息：同类排名走势
    #y：同类型排名-每日近三月排名
    #sc：总排名-每日近三月排名
    df = ak.fund_em_info(fund="710001", indicator="同类排名走势")
    
    #XXX基金信息：同类排名百分比，同类型排名-每日近3月收益排名百分比
    df = ak.fund_em_info(fund="710001", indicator="同类排名百分比")
    
    #XXX基金信息：分红送配详情
    df = ak.fund_em_info(fund="161606", indicator="分红送配详情")
    
    #XXX基金信息：拆分详情
    df = ak.fund_em_info(fund="161606", indicator="拆分详情")
    
    #基金净值估算数据，当前获取在交易日的所有基金的净值估算数据
    #爬虫来源：https://zhuanlan.zhihu.com/p/140478554?from_voters_page=true
    #信息内容：基金代码，基金类型，单位净值，基金名称
    df = ak.fund_em_value_estimation()
    
    #基金持股：获取个股的基金持股数据
    #爬虫来源：https://my.oschina.net/akshare/blog/4428824
    #持股的基金类型：symbol="基金持仓"; choice of {"基金持仓", "QFII持仓", "社保持仓", "券商持仓", "保险持仓", "信托持仓"}
    #返回：单次返回指定 symbol 和 date 的所有历史数据
    df = ak.stock_report_fund_hold(symbol="基金持仓", date="20200630")
    
    ###Fama-French三因子回归A股实证（附源码）
    #代码来源：https://mp.weixin.qq.com/s?__biz=MzU5NDY0NDM2NA==&mid=2247486057&idx=1&sn=0fb3f8558da4e55789ce340c03b648cc&chksm=fe7f568ac908df9c22bae8b52207633984ec91ef7b2728eea8c6a75089b8f2db284e3d611775&scene=21#wechat_redirect

    ###Carhart四因子模型A股实证（附源码）
    #代码来源：https://my.oschina.net/akshare/blog/4340998
    
    #==========================================================================
    ###其他公募基金实时/历史行情
    #爬虫来源：https://cloud.tencent.com/developer/article/1624480
    #基金基本信息：基金代码，基金简称，基金类型
    df = ak.fund_em_fund_name()
    
    #开放式基金-实时数据
    df = ak.fund_em_open_fund_daily()
    
    #开放式基金-历史数据
    df = ak.fund_em_open_fund_info(fund="710001", indicator="单位净值走势")
    df = ak.fund_em_open_fund_info(fund="710001", indicator="累计净值走势")
    df = ak.fund_em_open_fund_info(fund="710001", indicator="累计收益率走势")
    df = ak.fund_em_open_fund_info(fund="710001", indicator="同类排名走势")
    df = ak.fund_em_open_fund_info(fund="710001", indicator="同类排名百分比")
    df = ak.fund_em_open_fund_info(fund="161606", indicator="分红送配详情")
    df = ak.fund_em_open_fund_info(fund="161606", indicator="拆分详情")
    
    #货币型基金-实时数据
    #基金代码，基金简称，当前交易日-单位净值，7日年化收益率，成立日期，基金经理，手续费
    df = ak.fund_em_money_fund_daily()
    
    #货币型基金-历史数据
    #净值日期，7日年化收益率，申购状态，赎回状态
    df = ak.fund_em_money_fund_info(fund="000009")
    
    #理财型基金-实时数据
    #基金代码，基金简称，当前交易日-7日年化收益率，封闭期，申购状态
    df = ak.fund_em_financial_fund_daily()
    
    #理财型基金-历史数据
    #净值日期，7日年化收益率，申购状态，赎回状态
    df = ak.fund_em_financial_fund_info(fund="000134")
    
    #分级基金-实时数据
    #基金代码，基金简称，单位净值，累计净值，市价，折价率，手续费
    df = ak.fund_em_graded_fund_daily()
    
    #分级基金-历史数据
    #净值日期，7日年化收益率，申购状态，赎回状态
    df = ak.fund_em_graded_fund_info(fund="150232")
    
    #场内交易基金ETF-实时数据
    #基金代码，基金简称，类型，当前交易日-单位净值，当前交易日-累计净值，市价，折价率
    df = ak.fund_em_etf_fund_daily()
    
    #场内交易基金-历史数据
    #净值日期，单位净值，累计净值，日增长率%，申购状态，申购状态
    df = ak.fund_em_etf_fund_info(fund="511280")
    
    ###抓取沪深股市所有指数关联的公募基金列表（含ETF、增强、分级等）
    #代码来源：https://blog.csdn.net/leeleilei/article/details/106124894
    
    ###pyecharts绘制可伸缩蜡烛图
    #代码地址：https://segmentfault.com/a/1190000021999451?utm_source=sf-related
    



























