# -*- coding: utf-8 -*-
"""
本模块功能：计算财务报表比例，应用层，仅用于中国大陆上市的企业
所属工具包：证券投资分析工具SIAT 
SIAT：Security Investment Analysis Tool
创建日期：2020年9月8日
最新修订日期：2024年4月21日
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
#==============================================================================
#本模块的公共引用
from siat.common import *
from siat.translate import *
from siat.grafix import *
from siat.beta_adjustment_china import *
from siat.financials_china2 import *
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
import pandas as pd
import akshare as ak

#SUFFIX_LIST_CN=['SS','SZ','BJ','NQ']
#==============================================================================
#==============================================================================
if __name__=='__main__':
    ticker="603589.SS"
    ticker='002415.SZ'
    
    ticker='000002.SZ'
    ticker='601398.SS'
    ticker='600791.SS'
    
    ticker="601375.SS"
    ticker="600305.SS"
    
    akfs=get_fin_stmt_ak(ticker)
    
def get_fin_stmt_ak(ticker):
    """
    从akshare获取财务报表数据，合成df，限于中国A股
    获取的项目：所有原始项目
    注意：抓取所有的报表，不过滤日期
    
    注意：需要akshare版本1.9.59及以上，字段有变化
    """
    print("  Searching financial statements for",ticker,"...")
    #是否中国股票
    result,prefix,suffix=split_prefix_suffix(ticker)
    if not (suffix in SUFFIX_LIST_CN):
        print("  #Error(get_fin_stmt_ak): not a stock in China",ticker)
        return None        
    
    #抓取三大报表
    import akshare as ak
    import time
    try:
        fbs = ak.stock_financial_report_sina(stock=prefix, symbol="资产负债表")
    except:
        time.sleep(3)
        try:
            fbs = ak.stock_financial_report_sina(stock=prefix, symbol="资产负债表")
        except:
            print("  #Error(get_fin_stmt_ak): balance sheet currently inaccessible for",ticker,'\b, try later')
            return None        
        
    try:
        fis = ak.stock_financial_report_sina(stock=prefix, symbol="利润表")
    except:
        time.sleep(3)
        try:
            fis = ak.stock_financial_report_sina(stock=prefix, symbol="利润表")
        except:
            print("  #Error(get_fin_stmt_ak): income statement currently inaccessible for",ticker,'\b, try later')
            return None        
        
    try:
        fcf = ak.stock_financial_report_sina(stock=prefix, symbol="现金流量表")
    except:
        time.sleep(3)
        try:
            fcf = ak.stock_financial_report_sina(stock=prefix, symbol="现金流量表")
        except:
            print("  #Error(get_fin_stmt_ak): cashflow statement currently inaccessible for",ticker,'\b, try later')
            return None        
    
    #若报表为空，则返回
    if fbs is None:
        print("  #Warning(get_fin_stmt_ak): balance sheets inaccessible for",ticker)
        return None 
    if fis is None:
        print("  #Warning(get_fin_stmt_ak): income statements inaccessible for",ticker)
        return None 
    if fcf is None:
        print("  #Warning(get_fin_stmt_ak): cash flow statements inaccessible for",ticker)
        return None 
    
    #若报表无数据，则返回
    if len(fbs)==0:
        print("  #Warning(get_fin_stmt_ak): zero record of balance sheets found for",ticker)
        return None  
    if len(fis)==0:
        print("  #Warning(get_fin_stmt_ak): zero record of income statements found for",ticker)
        return None        
    if len(fcf)==0:
        print("  #Warning(get_fin_stmt_ak): zero record of cash flow found for",ticker)
        return None  
        
    # 报告日/报表日期
    rptdate=list(fbs)[0]    #报告日
    
    fbs1=fbs.drop_duplicates(subset=[rptdate],keep='first')
    fbs1.sort_values(by=[rptdate],ascending=True,inplace=True)
    fbs1['date']=pd.to_datetime(fbs1[rptdate])
    fbs1.set_index('date',inplace=True)
    
    fis1=fis.drop_duplicates(subset=[rptdate],keep='first')
    fis1.sort_values(by=[rptdate],ascending=True,inplace=True)
    fis1['date']=pd.to_datetime(fis1[rptdate])
    fis1.set_index('date',inplace=True)
    
    dropcollist=['报告日','数据源','公告日期','更新日期']
    try:
        fis1.drop(labels=dropcollist,axis=1,inplace=True)
    except:
        pass
    
    fcf1=fcf.drop_duplicates(subset=[rptdate],keep='first')
    fcf1.sort_values(by=[rptdate],ascending=True,inplace=True)
    fcf1['date']=pd.to_datetime(fcf1[rptdate])
    fcf1.set_index('date',inplace=True)
    try:
        fcf1.drop(labels=dropcollist,axis=1,inplace=True)
    except:
        pass

    #合成：内连接
    fs1=pd.merge(fbs1,fis1,how='inner',left_index=True,right_index=True)
    fs2=pd.merge(fs1,fcf1,how='inner',left_index=True,right_index=True)
    
    if len(fs2) == 0:
        print("  #Warning(get_fin_stmt_ak): zero reports found for",ticker)
        return None
    #按照日期升序排序
    fs2.sort_index(inplace=True)

    #数据清洗：删除因两次合并可能产生的重复列
    dup_col_list=[]
    for c in fs2.columns:
        if '_y' in c:
            dup_col_list=dup_col_list+[c]
            
            c2=c[:-2]
            c2y=c2+'_x'
            fs2.rename(columns={c2y:c2},inplace=True)
            
    fs2.drop(labels= dup_col_list, axis=1, inplace=True)
    
    #数据清洗：将空值替换为0
    fs3=fs2.fillna('0')
    
    #数据清洗：转换数值类型
    for i in fs3.columns:
        try:
            fs3[i]=fs3[i].astype('float')
        except:
            pass
    
    fs3['ticker']=ticker
    fs3['endDate']=fs3.index.strftime('%Y-%m-%d')
    
    # 删除重复的列
    fs3t=fs3.T
    fs3t['check']=fs3t.index  #给每行增加不同，防止drop_duplicates误删除
    fs3td=fs3t.drop_duplicates(subset=['check'],keep='first')
    
    # 删除含有check的行和check列
    #fs3td1=fs3td[fs3td.index != 'check']
    fs3td.drop("check", axis=1, inplace=True)
    
    fs4=fs3td.T
    """
    fs4=fs3.T.drop_duplicates(keep='first').T
    """
    
    fs4.fillna(0,inplace=True)
    #以下专门针对银行业报表
    import numpy as np
    fslist=list(fs4)
    
    #银行资产负债表
    if not ('货币资金' in fslist):
        fs4['货币资金']=fs4['现金及存放中央银行款项']

    if not ('预收款项' in fslist):
        fs4['预收款项']=fs4['预收账款']
    
    if not ('实收资本(或股本)' in fslist):
        if '股本' in fslist:
            fs4['实收资本(或股本)']=fs4['股本']
        if '实收资本净额' in fslist:
            fs4['实收资本(或股本)']=fs4['实收资本净额']
            
    
    if not ('流动资产合计' in fslist):
        if '其他资产' in fslist:
            fs4['流动资产合计']=fs4['资产总计']-fs4['固定资产合计']-fs4['无形资产']-fs4['商誉']-fs4['递延税款借项']-fs4['其他资产']
        else:
            fs4['流动资产合计']=fs4['资产总计']-fs4['固定资产合计']-fs4['无形资产']-fs4['商誉']-fs4['递延税款借项']

    if not ('速动资产合计' in fslist):
        if not('存货' in fslist) and ('存货净额' in fslist):
            fs4['存货']=fs4['存货净额']
        
        fs4['速动资产合计']=fs4['流动资产合计']-fs4['存货']

    if not ('流动负债合计' in fslist):
        if not ('应付债券' in fslist) and ('应付债券款' in fslist):
            fs4['应付债券']=fs4['应付债券款']
            
        if not ('递延所得税负债' in fslist) and ('递延税款贷项' in fslist):
            fs4['递延所得税负债']=fs4['递延税款贷项'] 
            
        if '其他负债' in fslist:
            fs4['流动负债合计']=fs4['负债合计']-fs4['应付债券']-fs4['递延所得税负债']-fs4['其他负债']
        else:
            fs4['流动负债合计']=fs4['负债合计']-fs4['应付债券']-fs4['递延所得税负债']

    #银行利润表
    if not ('营业总收入' in fslist):
        fs4['营业总收入']=fs4['营业收入']+fs4['加:营业外收入']
    
    if not ('营业成本' in fslist):
        fs4['营业成本']=fs4['营业支出']

    if not ('营业总成本' in fslist):
        fs4['营业总成本']=fs4['营业成本']+fs4['减:营业外支出']

    if not ('归母净利润' in fslist):
        for gm in ['归属于母公司的净利润','归属于母公司所有者的净利润','归属于母公司所有者的综合收益总额']:
            try:
                fs4['归母净利润']=fs4[gm]
                break
            except:
                continue

    if not ('销售费用' in fslist):
        fs4['销售费用']=0

    if not ('管理费用' in fslist):
        fs4['管理费用']=fs4['业务及管理费用']
        
    #银行现金流量表
    if not ('经营活动现金流入' in fslist):
        fs4['经营活动现金流入']= fs4['经营活动现金流入小计']   
    
    if not ('经营活动现金流出' in fslist):
        fs4['经营活动现金流出']= fs4['经营活动现金流出小计']   
    
    if not ('经营活动现金流净额' in fslist):
        fs4['经营活动现金流净额']= fs4['经营活动产生的现金流量净额']     
    
    #现金分析比率
    if not ('销售现金比率%' in fslist):
        #fs4['销售现金比率%']=round((fs4['经营活动现金流入'] / fs4['营业总收入'])*100,2)           
        fs4['销售现金比率%']=fs4.apply(lambda x: round((x['经营活动现金流入'] / x['营业总收入'])*100,2) if x['营业总收入'] !=0 else np.nan,axis=1)
        
    if not ('现金购销比率%' in fslist):
        #fs4['现金购销比率%']=round((fs4['经营活动现金流出'] / fs4['经营活动现金流入'])*100,2)
        fs4['现金购销比率%']=fs4.apply(lambda x: round((x['经营活动现金流出'] / x['经营活动现金流入'])*100,2) if x['经营活动现金流入'] !=0 else np.nan,axis=1)           
        
    if not ('营业现金回笼率%' in fslist):
        #fs4['营业现金回笼率%']=round((fs4['经营活动现金流入'] / fs4['营业总收入'])*100,2)          
        fs4['营业现金回笼率%']=fs4.apply(lambda x: round((x['经营活动现金流入'] / x['营业总收入'])*100,2) if x['营业总收入'] !=0 else np.nan,axis=1)
        
    if not ('短期现金偿债能力%' in fslist):
        #fs4['短期现金偿债能力%']=round((fs4['经营活动现金流净额'] / fs4['流动负债合计'])*100,2)
        try:
            fs4['短期现金偿债能力%']=fs4.apply(lambda x: round((x['经营活动现金流净额'] / x['流动负债合计'])*100,2) if x['流动负债合计'] !=0 else np.nan,axis=1)        
        except:
            fs4['短期现金偿债能力%']=np.nan
        
    if not ('长期现金偿债能力%' in fslist):
        #fs4['长期现金偿债能力%']=round((fs4['经营活动现金流净额'] / fs4['负债合计'])*100,2)     
        try:
            fs4['长期现金偿债能力%']=fs4.apply(lambda x: round((x['经营活动现金流净额'] / x['负债合计'])*100,2) if x['负债合计'] !=0 else np.nan,axis=1)
        except:
            fs4['长期现金偿债能力%']==np.nan

    if not ('流通股股数' in fslist):
        for gs in ['实收资本(或股本)','股本']:
            try:
                fs4['流通股股数']=fs4[gs]
                break
            except:
                continue
        
    if not ('现金支付股利能力(元)' in fslist):
        #fs4['现金支付股利能力(元)']=round((fs4['经营活动现金流净额'] / fs4['流通股股数'])*100,2)          
        fs4['现金支付股利能力(元)']=fs4.apply(lambda x: round((x['经营活动现金流净额'] / x['流通股股数'])*100,2) if x['流通股股数'] !=0 else np.nan,axis=1)

    if not ('所有者权益合计' in fslist):
        for loe in ['资产总计','资产合计']:
            try:
                fs4['所有者权益合计']=fs4[loe] - fs4['负债合计']
                break
            except:
                continue
        
    if not ('现金综合支付能力%' in fslist):
        #fs4['现金综合支付能力%']=round((fs4['经营活动现金流净额'] / fs4['所有者权益合计'])*100,2)
        fs4['现金综合支付能力%']=fs4.apply(lambda x: round((x['经营活动现金流净额'] / x['所有者权益合计'])*100,2) if x['所有者权益合计'] !=0 else np.nan,axis=1)

    if not ('支付给(为)职工支付的现金' in fslist):
        fs4['支付给(为)职工支付的现金']=fs4['支付给职工以及为职工支付的现金']

    if not ('支付给职工的现金比率%' in fslist):
        #fs4['支付给职工的现金比率%']=round((fs4['支付给(为)职工支付的现金'] / fs4['经营活动现金流入'])*100,2)
        fs4['支付给职工的现金比率%']=fs4.apply(lambda x: round((x['支付给(为)职工支付的现金'] / x['经营活动现金流入'])*100,2) if x['经营活动现金流入'] !=0 else np.nan,axis=1)
        
    if not ('盈利现金比率%' in fslist):
        #fs4['盈利现金比率%']=round((fs4['经营活动现金流净额'] / fs4['净利润'])*100,2)
        fs4['盈利现金比率%']=fs4.apply(lambda x: round((x['经营活动现金流净额'] / x['净利润'])*100,2) if x['净利润'] !=0 else np.nan,axis=1)
        
    if not ('现金流入流出比率%' in fslist):
        #fs4['现金流入流出比率%']=round((fs4['经营活动现金流入'] / fs4['经营活动现金流出'])*100,2)
        fs4['现金流入流出比率%']=fs4.apply(lambda x: round((x['经营活动现金流入'] / x['经营活动现金流出'])*100,2) if x['经营活动现金流出'] !=0 else np.nan,axis=1)
        
    if not ('资产现金回收率%' in fslist):
        #fs4['资产现金回收率%']=round((fs4['经营活动现金流净额'] / fs4['资产总计'])*100,2)
        fs4['资产现金回收率%']=fs4.apply(lambda x: round((x['经营活动现金流净额'] / x['资产总计'])*100,2) if x['资产总计'] !=0 else np.nan,axis=1)
 
 
    return fs4

"""
['流动资产', '货币资金', '交易性金融资产', '衍生金融资产', '应收票据及应收账款',
 '应收票据', '应收账款', '应收款项融资', '预付款项', '其他应收款(合计)', '应收利息',
 '应收股利', '其他应收款', '买入返售金融资产', '存货', '划分为持有待售的资产',
 '一年内到期的非流动资产', '待摊费用', '待处理流动资产损益', '其他流动资产',
 '流动资产合计',
 '非流动资产', '发放贷款及垫款', '可供出售金融资产', '持有至到期投资', '长期应收款',
 '长期股权投资', '投资性房地产', '在建工程(合计)', '在建工程', '工程物资',
 '固定资产及清理(合计)', '固定资产净额', '固定资产清理', '生产性生物资产',
 '公益性生物资产', '油气资产', '使用权资产', '无形资产', '开发支出', '商誉',
 '长期待摊费用', '递延所得税资产', '其他非流动资产', 
 '非流动资产合计',
 '资产总计',
 '流动负债', '短期借款', '交易性金融负债', '应付票据及应付账款', '应付票据',
 '应付账款', '预收款项', '应付手续费及佣金', '应付职工薪酬', '应交税费',
 '其他应付款(合计)', '应付利息', '应付股利', '其他应付款', '预提费用', '一年内的递延收益',
 '应付短期债券', '一年内到期的非流动负债', '其他流动负债',
 '流动负债合计',
 '非流动负债', '长期借款', '应付债券', '租赁负债', '长期应付职工薪酬', '长期应付款(合计)',
 '长期应付款', '专项应付款', '预计非流动负债', '递延所得税负债', '长期递延收益',
 '其他非流动负债',
 '非流动负债合计',
 '负债合计',
 '所有者权益', '实收资本(或股本)', '资本公积', '减：库存股', '其他综合收益',
 '专项储备', '盈余公积', '一般风险准备', '未分配利润', '归属于母公司股东权益合计',
 '所有者权益(或股东权益)合计',
 '负债和所有者权益(或股东权益)总计',
 
 '营业总收入', '营业收入',
 '营业总成本', '营业成本', '营业税金及附加', '销售费用', '管理费用', '研发费用',
 '资产减值损失', '公允价值变动收益', '投资收益', '其中:对联营企业和合营企业的投资收益',
 '汇兑收益',
 '营业利润', '加:营业外收入', '减：营业外支出', '其中：非流动资产处置损失',
 '四、利润总额', '减：所得税费用',
 '净利润', '归属于母公司所有者的净利润', '少数股东损益',
 '每股收益', '基本每股收益(元/股)', '稀释每股收益(元/股)',
 '其他综合收益',
 '综合收益总额', '归属于母公司所有者的综合收益总额', '归属于少数股东的综合收益总额',
 '报表日期', '单位',
 
 '经营活动产生的现金流量', '销售商品、提供劳务收到的现金', '收到的税费返还',
 '收到的其他与经营活动有关的现金', '经营活动现金流入小计', '购买商品、接受劳务支付的现金',
 '支付给职工以及为职工支付的现金', '支付的各项税费', '支付的其他与经营活动有关的现金',
 '经营活动现金流出小计', '经营活动产生的现金流量净额',
 '投资活动产生的现金流量', '收回投资所收到的现金', '取得投资收益所收到的现金',
 '处置固定资产、无形资产和其他长期资产所收回的现金净额',
 '处置子公司及其他营业单位收到的现金净额', '收到的其他与投资活动有关的现金',
 '投资活动现金流入小计',
 '购建固定资产、无形资产和其他长期资产所支付的现金', '投资所支付的现金',
 '取得子公司及其他营业单位支付的现金净额', '支付的其他与投资活动有关的现金',
 '投资活动现金流出小计',
 '投资活动产生的现金流量净额',
 '筹资活动产生的现金流量', '吸收投资收到的现金', '其中：子公司吸收少数股东投资收到的现金',
 '取得借款收到的现金', '发行债券收到的现金', '收到其他与筹资活动有关的现金',
 '筹资活动现金流入小计',
 '偿还债务支付的现金', '分配股利、利润或偿付利息所支付的现金',
 '其中：子公司支付给少数股东的股利、利润', '支付其他与筹资活动有关的现金',
 '筹资活动现金流出小计',
 '筹资活动产生的现金流量净额',
 '汇率变动对现金及现金等价物的影响',
 '现金及现金等价物净增加额', '加:期初现金及现金等价物余额',
 '期末现金及现金等价物余额',
 
 '附注',
 '净利润',
 '未确认的投资损失', '资产减值准备',
 '固定资产折旧、油气资产折耗、生产性物资折旧', '无形资产摊销', '长期待摊费用摊销',
 '待摊费用的减少', '预提费用的增加', '处置固定资产、无形资产和其他长期资产的损失',
 '固定资产报废损失', '公允价值变动损失', '递延收益增加（减：减少）', '预计负债',
 '投资损失', '递延所得税资产减少', '递延所得税负债增加', '存货的减少',
 '经营性应收项目的减少', '经营性应付项目的增加', '已完工尚未结算款的减少(减:增加)',
 '已结算尚未完工款的增加(减:减少)',
 '其他',
 '经营活动产生现金流量净额',
 '债务转为资本', '一年内到期的可转换公司债券', '融资租入固定资产',
 '现金的期末余额', '现金的期初余额',
 '现金等价物的期末余额', '现金等价物的期初余额',
 '现金及现金等价物的净增加额',
 
 'ticker',
 'endDate']
"""

if __name__=='__main__':
    fstmt=get_fin_stmt_ak('600519.SS')    

#==============================================================================
if __name__=='__main__':
    endDate="2020-12-31"
    top=10
    
def liability_rank_china(endDate='latest',top=5):
    """
    获得某个报表日期资产负债率排行榜，限于中国A股
    获取的项目：所有原始项目
    注意：
    """
    error_flag=False

    #获取最近的报表日期
    if endDate == 'latest':
        import datetime; endDate=datetime.date.today()
    else:
        #检查日期
        valid_date=check_date(endDate)
        if not valid_date:
            error_flag=True
            print("  #Error(liability_rank_china): invalid date",endDate)
    if error_flag: return None
    
    start=date_adjust(endDate, adjust=-365)
    fs_dates=cvt_fs_dates(start,endDate,'all')
    endDate=fs_dates[-1:][0]
    
    #获取A股名单：代码，简称
    print("  Searching assets info of all A shares, it may take several hours ...")
    import akshare as ak
    a_shares= ak.stock_info_a_code_name()
    a_len=len(a_shares)
    print('\b'*99,' Collected China A-share stocks, altogether',a_len)
    
    #遍历所有A股上市公司的资产负债表，计算资产负债率
    a_share_codes=list(a_shares['code'])
    liab_df=pd.DataFrame()
    for t in a_share_codes:
        #抓取资产负债表
        try:
            #df= ak.stock_financial_report_sina(stock=t, symbol="资产负债表")
            # 上述命令运行一定次数（不到300次）后出错，无法继续！
            df = ak.stock_financial_analysis_indicator(stock=t)
        except:
            print("  #Warning(liability_rank_china): failed to get liability info of",t)
            continue
        sub1=df[df.index == endDate]
        sub2=sub1[['资产负债率(%)']]
        sub2['股票代码']=t
        try:
            liab_df=liab_df.append(sub2)
        except:
            liab_df=liab_df._append(sub2)
        
        #显示进度
        print_progress_percent2(t,a_share_codes,steps=10,leading_blanks=4)

    
    #获取全体股票的业绩报表，指定截止日期
    print('\b'*99," Retrieved financial info of",len(liab_df),"stocks ended on",endDate)
    #转换日期格式
    ak_date=convert_date_ts(endDate)
    a_share_perf= ak.stock_em_yjbb(date=ak_date)
    a_share_industry=a_share_perf[['股票代码','股票简称','所处行业']]
    
    #合成
    liab_df['资产负债率(%)']=round(liab_df['资产负债率(%)'].astype('float'),2)
    alr_info_tmp=pd.merge(liab_df,a_share_industry,how='left',on='股票代码')
    alr_cols=['股票简称','股票代码','资产负债率(%)','所处行业']
    alr_info=alr_info_tmp[alr_cols]
    
    #后续处理：排序，找出资产负债率最低、最高的企业和行业
    alr_info.sort_values(by=['资产负债率(%)'],ascending=True,inplace=True)
    firm_top_lowest=alr_info.head(top)
    alr_info.sort_values(by=['资产负债率(%)'],ascending=False,inplace=True)
    firm_top_highest=alr_info.head(top)
    
    agg_cols={'资产负债率(%)':['mean','median']}
    group_df=alr_info.groupby('所处行业').agg(agg_cols)
    group_df.columns=['均值%','中位数%']
    group_df['均值%']=round(group_df['均值%'],2)
    group_df['中位数%']=round(group_df['中位数%'],2)
    
    group_df.sort_values(by=['均值%'],ascending=True,inplace=True)
    industry_lowest=group_df.head(top5)
    group_df.sort_values(by=['均值%'],ascending=False,inplace=True)
    industry_highest=group_df.head(top5)

    
    #设置打印对齐
    pd.set_option('display.max_columns', 1000)
    pd.set_option('display.width', 1000)
    pd.set_option('display.max_colwidth', 1000)
    pd.set_option('display.unicode.ambiguous_as_wide', True)
    pd.set_option('display.unicode.east_asian_width', True)    
    
    #打印：负债率最低最高的企业
    print("\n=== 企业排名：资产负债率，前"+str(top)+"名最低，截止"+endDate+" ===")
    print(firm_top_lowest.to_string(index=False))
    print("\n=== 企业排名：资产负债率，前"+str(top)+"名最高，截止"+endDate+" ===")
    print(firm_top_highest.to_string(index=False))

    #打印：负债率最低最高的行业
    print("\n=== 行业排名：资产负债率，前"+str(top)+"名最低，截止"+endDate+" ===")
    print(industry_top_lowest.to_string(index=False))
    print("\n=== 行业排名：资产负债率，前"+str(top)+"名最高，截止"+endDate+" ===")
    print(industry_top_highest.to_string(index=False))

    import datetime; today=datetime.date.today()
    print("\n*** 数据来源：sina/EM，"+str(today))
    
    return alr_info,group_df
    
if __name__=='__main__':
    liability_rank_china(endDate='2020-12-31')
#==============================================================================
if __name__=='__main__':
    ticker='603589.SS'
    start='2018-1-1'
    end='2022-12-31'
    period_type='all'

def calc_dupont_china(ticker,start,end,period_type='all'):
    """
    功能：计算股票ticker的杜邦分析项目，基于财报期末数直接计算，仅限于中国A股
    """
    fsr2=get_fin_stmt_ak(ticker)
    if fsr2 is None:
        print("  #Error(calc_dupont_china): failed to retrieved reports for",ticker)
        return None   
    
    fsr3=fsr2[(fsr2['endDate'] >= start) & (fsr2['endDate'] <= end)]
    
    #字段变换与计算
    #oelist=['所有者权益(或股东权益)合计','所有者权益合计','归属于母公司股东权益合计']
    oelist=['所有者权益(或股东权益)合计','所有者权益合计']
    for oe in oelist:
        try:
            fsr3['ROE']=fsr3['净利润']/fsr3[oe]
            break
        except:
            continue
    """    
    try:
        oe='所有者权益(或股东权益)合计'
        fsr3['ROE']=fsr3['净利润']/fsr3[oe]
    except:
        oe='所有者权益合计'
        fsr3['ROE']=fsr3['净利润']/fsr3[oe]
    """    
        
    try:    
        tor='营业总收入'
        fsr3['Profit Margin']=fsr3['净利润']/fsr3[tor]
    except:
        tor='营业收入'
        fsr3['Profit Margin']=fsr3['净利润']/fsr3[tor]
    fsr3['Total Assets Turnover']=fsr3[tor]/fsr3['资产总计']
    fsr3['Equity Multiplier']=fsr3['资产总计']/fsr3[oe]
    
    dpidf=fsr3[['ticker','endDate','ROE','Profit Margin','Total Assets Turnover','Equity Multiplier']]    
    dpidf['pROE']=dpidf['Profit Margin']*dpidf['Total Assets Turnover']*dpidf['Equity Multiplier']
    
    return dpidf

if __name__=='__main__':
    df1=calc_dupont_china('600519.SS','2018-1-1','2021-12-31')
    df2=calc_dupont_china('600519.SS','2018-1-1','2021-12-31',period_type='annual')

#==============================================================================
if __name__=='__main__':
    ticker='600606.SS'
    start='2018-1-1'
    end='2021-11-24'
    period_type='all'

def calc_dupont_china_indicator(ticker,start,end,period_type='all'):
    """
    功能：计算股票ticker的杜邦分析项目，基于新浪、东方财富的财报指标抓取，仅限于中国A股
    """
    rates=['ROE','Profit Margin','Total Assets Turnover','Debts to Assets']
    rdf_list=prepare_fin_rate1tmr_china(ticker,rates,start,end,period_type)
    
    for rdf in rdf_list:
        if rdf is None:
            print("  #Error(calc_dupont_china): failed to retrieved reports for",ticker)
            return None   
        if len(rdf) == 0:
            print("  #Error(calc_dupont_china): zero record retrieved reports for",ticker)
            return None   
    
    #取出各项指标
    df_roe=rdf_list[rates.index('ROE')]
    df_roe['ROE']=df_roe['净资产收益率(%)']/100
    
    df_pm=rdf_list[rates.index('Profit Margin')]
    df_pm['Profit Margin']=df_pm['销售净利率(%)']/100
    
    df_tat=rdf_list[rates.index('Total Assets Turnover')]
    df_tat['Total Assets Turnover']=df_tat['总资产周转率(次)']
    
    df_em=rdf_list[rates.index('Debts to Assets')]
    df_em['Equity Multiplier']=1/(1-df_em['资产负债率(%)']/100)
    
    #多个数据表合并：合并列
    fsr=pd.concat([df_roe,df_pm,df_tat,df_em],axis=1,sort=True,join='inner')
    cols=['ROE','Profit Margin','Total Assets Turnover','Equity Multiplier']
    fsr2=fsr[cols]
    fsr2['ticker']=ticker
    fsr2['endDate']=fsr2.index.strftime('%Y-%m-%d')
    
    fsr2['month']=fsr2.index.month
    fsr2['periodType']=fsr2['month'].apply(lambda x: '年报' if x==12 else('中报' if x==6 else '季报'))
    
    #检查是否符合杜邦公式
    #fsr2['pROE']=fsr2['Profit Margin']*fsr2['Total Assets Turnover']*fsr2['Equity Multiplier']
    #注意：实际财务指标计算中，由于ROE和Profit Margin等指标中可能蕴含了加加减减等各种调整，ROE并非一定遵从杜邦公式
    
    return fsr2

if __name__=='__main__':
    df1=calc_dupont_china('600519.SS','2018-1-1','2021-12-31')
    df2=calc_dupont_china('600519.SS','2018-1-1','2021-12-31',period_type='annual')


#==============================================================================
if __name__=='__main__':
    tickerlist=['603589.SS','600519.SS','000002.SZ']
    fsdate='2022-12-31'
    scale1 = 10
    scale2 = 10
    hatchlist=['.', 'o', '\\']

def compare_dupont_china(tickerlist,fsdate='latest',scale1 = 10,scale2 = 10, \
                         hatchlist=['.', 'o', '\\'],printout=True,sort='PM', \
                         facecolor='papayawhip',font_size='16px',
                         loc='best'):
    """
    功能：获得tickerlist中每只股票的杜邦分析项目，绘制柱状叠加比较图
    tickerlist：股票代码列表，建议在10只以内
    fsdate：财报日期，默认为最新一期季报/年报，也可规定具体日期，格式：YYYY-MM-DD
    scale1：用于放大销售净利率，避免与权益乘数数量级不一致导致绘图难看问题，可自行调整
    scale2：用于放大总资产周转率，避免与权益乘数数量级不一致导致绘图难看问题，可自行调整
    hatchlist：绘制柱状图的纹理，用于黑白打印时区分，可自定义，
    可用的符号：'-', '+', 'x', '\\', '*', 'o', 'O', '.'    
    """
    error_flag=False
    if fsdate in ['latest','annual','quarterly']:
        import datetime as dt; end=str(dt.date.today())
        start=date_adjust(end, adjust=-365)
    else:
        valid=check_date(fsdate)
        if valid:
            end=fsdate
            start=date_adjust(end, adjust=-365)
        else:
            error_flag=True
    if error_flag: return None

    ticker = '公司'
    name1 = '销售净利率'
    name2 = '总资产周转率'
    name3 = '权益乘数'
    name4 = '净资产收益率'
    name5 = '财报日期'
    
    dpidflist,dpilist,fsdatelist,fstypelist=[],[],[],[]
    name1list,name2list,name3list,name4list,name5list,name6list=[],[],[],[],[],[]
    newtickerlist=[]
    for t in tickerlist:
        try:
            dpidf=calc_dupont_china(t,start,end)
            #dpidf=calc_dupont_china_indicator(t,start,end)
        except:
            print("  #Warning(compare_dupont_china): failed to get financial info for",t)
            continue
        if dpidf is None:
            print("  #Warning(compare_dupont_china): financial statements not found for",t,'@',fsdate)
            continue
        if len(dpidf)==0:
            print("  #Warning(compare_dupont_china): financial statements not available for",t,'@',fsdate)
            continue
        dpi=dpidf.tail(1)
        
        newtickerlist=newtickerlist+[t]
        dpidflist=dpidflist+[dpidf]
        dpilist=dpilist+[dpi]
        fsdatelist=fsdatelist+[dpi['endDate'][0]]
        
        name1list=name1list+[dpi['Profit Margin'][0]*scale1]
        name2list=name2list+[dpi['Total Assets Turnover'][0]*scale2]
        name3list=name3list+[dpi['Equity Multiplier'][0]]
        name4list=name4list+[dpi['ROE'][0]]
        name5list=name5list+[dpi['endDate'][0]]
    
    tickerlist=newtickerlist
    raw_data = {ticker:tickerlist,
            name1:name1list,
            name2:name2list,
            name3:name3list,
            name4:name4list,
            name5:name5list,
            }

    df = pd.DataFrame(raw_data,columns=[ticker,name1,name2,name3,name4,name5])
    if len(df)==0:
        print('')
        print("  #Error(compare_dupont_china): no data to plot dupont identity bar chart.")
        print("  If the stock code is correct, you may suffer from anti-spyder from data source. Try later")
        return None
    
    if sort=='PM':
        df.sort_values(name1,ascending=False,inplace=True)
    elif sort=='TAT':
        df.sort_values(name2,ascending=False,inplace=True)
    elif sort=='EM':
        df.sort_values(name3,ascending=False,inplace=True)
    else:
        df.sort_values(name1,ascending=False,inplace=True)
    
    num=len(df['公司'])
    for i in range(num):
        code=df.loc[i,'公司']
        df.loc[i,'公司']=ticker_name(code,'stock').replace("(A股)",'')
    
    #f,ax1 = plt.subplots(1,figsize=(10,5))
    f,ax1 = plt.subplots(1,figsize=(12.8,6.4))
    w = 0.75
    x = [i+1 for i in range(len(df[name1]))]
    #tick_pos = [i+(w/2.) for i in x]
    tick_pos = [i for i in x]

    ax1.bar(x,df[name3],width=w,bottom=[i+j for i,j in zip(df[name1],df[name2])], \
            label=name3,alpha=0.5,color='green',hatch=hatchlist[0], \
            edgecolor='black',align='center')
    ax1.bar(x,df[name2],width=w,bottom=df[name1],label=name2,alpha=0.5,color='red', \
            hatch=hatchlist[1], edgecolor='black',align='center')
    ax1.bar(x,df[name1],width=w,label=name1,alpha=0.5,color='blue', \
            hatch=hatchlist[2], edgecolor='black',align='center')

    #判断是否绘制零线
    pm_max=df[name1].max(); pm_min=df[name1].min()
    if pm_max * pm_min < 0:
        plt.axhline(y=0,ls=":",c="black",linewidth=2,label='')
    
    plt.xticks(tick_pos,df[ticker])
    plt.ylabel("杜邦分析分解项目")
    
    try:
        endDate=df['财报日期'].values[0]        
    except:
        print("  #Error(compare_dupont_china): no fs date records to illustrate")
        return None
            
    footnote='【财报日期】'+endDate
        
    import datetime; today=datetime.date.today()
    footnote1="【图示放大比例】"+name1+'：x'+str(scale1)+'，'+name2+'：x'+str(scale2)
    footnote2=footnote+'\n'+footnote1+'\n'+"数据来源：sina/EM，"+str(today)
    plt.xlabel(footnote2)
    
    plt.legend(loc=loc)
    
    titletxt1="杜邦分析对比图："
    if sort=='PM':
        titletxt2="按照"+name1+"降序排列"
    elif sort=='TAT':
        titletxt2="按照"+name2+"降序排列"
    else:
        titletxt2="按照"+name3+"降序排列"
            
    plt.title(titletxt1+titletxt2)
    plt.xlim([min(tick_pos)-w,max(tick_pos)+w])
    
    plt.gca().set_facecolor('whitesmoke')
    plt.show()    
    
    if printout:
        df[name1]=df[name1]/scale1
        df[name2]=df[name2]/scale2
        
        cols=['销售净利率','总资产周转率','权益乘数','净资产收益率']
        for c in cols:
            df[c]=df[c].apply(lambda x: round(x,4))
        
        """
        #设置打印对齐
        pd.set_option('display.max_columns', 1000)
        pd.set_option('display.width', 1000)
        pd.set_option('display.max_colwidth', 1000)
        pd.set_option('display.unicode.ambiguous_as_wide', True)
        pd.set_option('display.unicode.east_asian_width', True)  
        
        print("===== 杜邦分析分项数据表 =====")
        print("*** 数据来源：sina/EM，"+str(today))
        """
        title_txt="杜邦分析分项数据表："+titletxt2
        footnote0="1、表中各个上市公司的财报日期可能存在差异，但均为可获得(已公布)的最新财报"
        footnote1="2、表中数值基于期末数字直接计算，而非期初期末均值，可能与公告数字存在差异。"
        footnote2="*** 数据来源：sina/EM，"+str(today)
        footnote=footnote0+'\n'+footnote1+'\n'+footnote2

        #确定表格字体大小
        titile_font_size=font_size
        heading_font_size=data_font_size=str(int(font_size.replace('px',''))-1)+'px'   
     
        #print(df.to_string(index=False))
        #df_directprint(df,title_txt,footnote)
        df_display_CSS(df=df,titletxt=title_txt,footnote=footnote, \
                       facecolor=facecolor,decimals=4, \
                   titile_font_size=titile_font_size,heading_font_size=heading_font_size, \
                   data_font_size=data_font_size)
        
        
    #合并所有历史记录
    alldf=pd.concat(dpidflist)
    alldf.dropna(inplace=True)
    #del alldf['pROE']
    
    """
    allnum=len(alldf)
    for i in range(allnum):
        code=alldf.loc[i,'periodType']
        if code == '3M': alldf.loc[i,'periodType']='Quarterly'
        else: alldf.loc[i,'periodType']='Annual'    
    """
    return alldf

if __name__=='__main__':
    tickerlist=['600606.SS','600519.SS','000002.SZ'] 
    df=compare_dupont_china(tickerlist,fsdate='latest',scale1 = 100,scale2 = 10)   

#==============================================================================
#==============================================================================
# 以上基于财报期末数字直接构造，以下基于获取的财务指标构造================================
#==============================================================================
#==============================================================================
if __name__=='__main__':
    ticker="600606.SS" 

def get_fin_abstract_ak(ticker):
    """
    从akshare获取财报摘要，限于中国A股
    获取的项目：所有原始项目
    注意：不过滤日期
    """
    print("  Searching financial abstract for",ticker,"...")

    #是否中国股票
    result,prefix,suffix=split_prefix_suffix(ticker)
    if not (suffix in SUFFIX_LIST_CN):
        print("  #Warning(get_fin_abstract_ak): not a stock in China",ticker)
        return None        
    
    #财务报告摘要
    try:
        df1 = ak.stock_financial_abstract(stock=prefix)
    except:
        print("  #Warning(get_fin_abstract_ak): no financial information found for",ticker)
        return None
    """
    ['截止日期','每股净资产-摊薄/期末股数','每股现金流','每股资本公积金','固定资产合计',
     '流动资产合计','资产总计','长期负债合计','主营业务收入','财务费用','净利润']
    """
    if df1 is None:
        print("  #Warning(get_fin_abstract_ak): reports inaccessible for",ticker)
        return None
    
    if len(df1) == 0:
        print("  #Warning(get_fin_abstract_ak): zero reports found for",ticker)
        return None
    
    #数据清洗：去掉数值中的“元”字
    for c in df1.columns:
        try:
            df1[c]=df1[c].apply(lambda x: str(x).replace('元',''))
        except:
            continue

    #数据清洗：将空值替换为0
    df1b=df1.fillna('0')
    df2=df1b.replace('nan','0')
    
    #数据清洗：转换数值类型
    for c in df2.columns:
        try:
            df2[c]=df2[c].astype('float')
        except:
            continue

    #设置索引
    df2['date']=pd.to_datetime(df2['截止日期'])
    df2.set_index('date',inplace=True)
    #按照日期升序排序
    df2.sort_index(inplace=True)
    
    df2['ticker']=ticker
    df2['endDate']=df2.index.strftime('%Y-%m-%d')
    
    return df2

if __name__=='__main__':
    fabs=get_fin_abstract_ak('600519.SS')    

#==============================================================================
if __name__=='__main__':
    ticker="600606.SS" 
    
def get_fin_indicator_ak(ticker):
    """
    从akshare获取财报重要指标，限于中国A股，历史数据
    获取的项目：所有原始项目
    注意：不过滤日期
    """
    print('\b'*99," Searching financial indicators for",ticker,"...")

    #是否中国股票
    result,prefix,suffix=split_prefix_suffix(ticker)
    if not (suffix in SUFFIX_LIST_CN):
        print("  #Warning(get_fin_indicator_ak): not a stock in China",ticker)
        return None        
    
    #财务报告重要指标
    try:
        df1 = ak.stock_financial_analysis_indicator(stock=prefix)
        print('\b'*99," Calculating financial indicators for the above stock ...")
    except:
        print('\b'*99," #Warning(get_fin_indicator_ak): failed to get financial info for",ticker)
        return None
    """
    ['摊薄每股收益(元)','加权每股收益(元)','每股收益_调整后(元)','扣除非经常性损益后的每股收益(元)',
     '每股净资产_调整前(元)','每股净资产_调整后(元)','调整后的每股净资产(元)',
     '每股经营性现金流(元)',
     '每股资本公积金(元)','每股未分配利润(元)',
     '总资产利润率(%)','总资产净利润率(%)','资产报酬率(%)',
     '主营业务利润率(%)','成本费用利润率(%)','营业利润率(%)','主营业务成本率(%)','销售净利率(%)',
     '股本报酬率(%)','净资产报酬率(%)','净资产收益率(%)','加权净资产收益率(%)',
     '投资收益率(%)',
     '主营业务收入增长率(%)','净利润增长率(%)','净资产增长率(%)','总资产增长率(%)',
     '销售毛利率(%)','主营业务利润(元)',
     '三项费用比重',
     '非主营比重','主营利润比重','股息发放率(%)',
     '扣除非经常性损益后的净利润(元)',
     '应收账款周转率(次)','应收账款周转天数(天)','存货周转天数(天)','存货周转率(次)',
     '固定资产周转率(次)','总资产周转率(次)','总资产周转天数(天)','流动资产周转率(次)',
     '流动资产周转天数(天)','股东权益周转率(次)','流动比率','速动比率','现金比率(%)',
     '利息支付倍数','长期债务与营运资金比率(%)','股东权益比率(%)','长期负债比率(%)',
     '股东权益与固定资产比率(%)','负债与所有者权益比率(%)','长期资产与长期资金比率(%)',
     '资本化比率(%)','固定资产净值率(%)','资本固定化比率(%)','产权比率(%)',
     '清算价值比率(%)','固定资产比重(%)','资产负债率(%)','总资产(元)',
     '经营现金净流量对销售收入比率(%)','资产的经营现金流量回报率(%)',
     '经营现金净流量与净利润的比率(%)','经营现金净流量对负债比率(%)','现金流量比率(%)',
     '短期股票投资(元)','短期债券投资(元)','短期其它经营性投资(元)',
     '长期股票投资(元)','长期债券投资(元)','长期其它经营性投资(元)',
     '1年以内应收帐款(元)','1-2年以内应收帐款(元)','2-3年以内应收帐款(元)',
     '3年以内应收帐款(元)',
     '1年以内预付货款(元)','1-2年以内预付货款(元)','2-3年以内预付货款(元)',
     '3年以内预付货款(元)',
     '1年以内其它应收款(元)','1-2年以内其它应收款(元)','2-3年以内其它应收款(元)',
     '3年以内其它应收款(元)']
    """
    if df1 is None:
        print('\b'*99," #Warning(get_fin_indicator_ak): reports inaccessible for",ticker)
        return None
    
    if len(df1) == 0:
        print('\b'*99," #Warning(get_fin_indicator_ak): zero reports found for",ticker)
        return None
    
    #设置索引    
    df1['截止日期']=df1.index
    df1['date']=pd.to_datetime(df1['截止日期'])
    df1.set_index('date',inplace=True)
    #按照日期升序排序
    df1.sort_index(inplace=True)
    
    #数据清洗：将空值替换为0
    df1b=df1.fillna('0')
    #数据清洗：将"--"值替换为0
    df2=df1b.replace('--','0')
    
    #数据清洗：转换数值类型
    for c in df2.columns:
        try:
            df2[c]=df2[c].astype('float')
        except:
            continue
    
    df2['ticker']=ticker
    df2['endDate']=df2.index.strftime('%Y-%m-%d')
    
    return df2

if __name__=='__main__':
    find=get_fin_indicator_ak('600606.SS')    

#==============================================================================
if __name__=='__main__':
    ticker="600606.SS" 
    endDate="2020-12-31"
    
def get_fin_performance_ak(ticker,endDate):
    """
    从akshare获取业绩报表，限于中国A股
    获取的项目：所有原始项目
    注意：不过滤日期
    """
    #是否中国股票
    result,prefix,suffix=split_prefix_suffix(ticker)
    if not (suffix in SUFFIX_LIST_CN):
        print("  #Warning(get_fin_performance_ak): not a stock in China",ticker)
        return None        
    
    #转换日期格式
    ak_date=convert_date_ts(endDate)
    print('\b'*99," Retrieving financial performance for",ticker,'ended on',endDate)
    #获取全体股票的业绩报表，指定截止日期
    df1 = ak.stock_em_yjbb(date=ak_date)
    """
    ['序号', '股票代码', '股票简称', '每股收益', '营业收入-营业收入', '营业收入-同比增长',
     '营业收入-季度环比增长', '净利润-净利润', '净利润-同比增长', '净利润-季度环比增长',
     '每股净资产', '净资产收益率', '每股经营现金流量', '销售毛利率',
     '所处行业', '最新公告日期']
    """
    print('\b'*99," Calculating financial performance in the above period ...")
    
    if df1 is None:
        print("  #Warning(get_fin_performance_ak): reports inaccessible for",ticker)
        return None
    if len(df1) == 0:
        print("  #Warning(get_fin_performance_ak): zero reports found for",ticker)
        return None
    
    #删除B股股票，只保留A股
    df1a = df1.drop(df1[df1['股票简称'].str.contains('B')].index)
    
    #按照股票代码升序+最新公告日期降序排序
    df1b=df1a.sort_values(by=['股票代码','最新公告日期'],ascending=[True,False])
    #去掉重复记录，保留第一条
    df1c=df1b.drop_duplicates(subset=['股票代码'],keep='first')

    #替换行业
    df1c['所处行业']=df1c['所处行业'].apply(lambda x: '其他行业' if x == 'None' else x)
    
    #数据清洗：将空值替换为0
    df1d=df1c.fillna('0')
    #数据清洗：将"--"值替换为0
    df1e=df1d.replace('--','0')
    df2=df1e.replace('nan','0')
    
    #修改列名
    df2.rename(columns={'营业收入-营业收入':'营业收入','净利润-净利润':'净利润'},inplace=True) 
    
    #数据清洗：转换数值类型
    for c in df2.columns:
        if c == '股票代码': continue
        try:
            df2[c]=df2[c].astype('float')
        except:
            continue
    
    #设置索引    
    df2['截止日期']=endDate
    df2['date']=pd.to_datetime(df2['截止日期'])
    df2.set_index('date',inplace=True)
    
    df2['ticker']=df2['股票代码']
    df2['endDate']=df2.index.strftime('%Y-%m-%d')
    df2['最新公告日期']=df2['最新公告日期'].apply(lambda x: x[:11])
    
    #筛选特定股票的数据
    tickerdf=df2[df2['ticker'] == prefix]
    industry=tickerdf['所处行业'].values[0]
    df_industry=df2[df2['所处行业'] == industry]
    num_industry=len(df_industry)
    
    rates_industry=['每股收益','营业收入','营业收入-同比增长','营业收入-季度环比增长',
                    '净利润','净利润-同比增长','净利润-季度环比增长','每股净资产',
                    '净资产收益率','每股经营现金流量','销售毛利率']
    for r in rates_industry:
        i_min=df_industry[r].min()
        i_max=df_industry[r].max()
        i_avg=df_industry[r].mean()
        i_med=df_industry[r].median()
        
        tickerdf[r+"-行业最小值"]=i_min
        tickerdf[r+"-行业最大值"]=i_max
        tickerdf[r+"-行业均值"]=i_avg
        tickerdf[r+"-行业中位数"]=i_med
        
        x=tickerdf[r].values[0]
        x_quantile=arg_percentile(df_industry[r], x)
        tickerdf[r+"-行业分位数"]=x_quantile*100
        
        if r in ['营业收入','净利润']:
            i_sum=df_industry[r].sum()
            tickerdf[r+"-占行业份额"]=tickerdf[r]/i_sum*100
    tickerdf['同行数量']=num_industry
    
    #排序字段
    cols=list(tickerdf)
    cols.sort(reverse=False)
    tickerdf2=tickerdf[cols]
    
    return tickerdf2

"""
['endDate', 'ticker',
 '净利润', '净利润-占行业份额', '净利润-行业中位数', '净利润-行业分位数', '净利润-行业均值', 
 '净利润-行业最大值', '净利润-行业最小值',
 
 '净利润-同比增长', '净利润-同比增长-行业中位数', '净利润-同比增长-行业分位数',
 '净利润-同比增长-行业均值', '净利润-同比增长-行业最大值', '净利润-同比增长-行业最小值',
 
 '净利润-季度环比增长', '净利润-季度环比增长-行业中位数', '净利润-季度环比增长-行业分位数',
 '净利润-季度环比增长-行业均值', '净利润-季度环比增长-行业最大值', 
 '净利润-季度环比增长-行业最小值',
 
 '净资产收益率', '净资产收益率-行业中位数', '净资产收益率-行业分位数', '净资产收益率-行业均值',
 '净资产收益率-行业最大值', '净资产收益率-行业最小值',
 '序号', '截止日期', '所处行业', '最新公告日期',
 
 '每股净资产', '每股净资产-行业中位数', '每股净资产-行业分位数', '每股净资产-行业均值',
 '每股净资产-行业最大值', '每股净资产-行业最小值',
 
 '每股收益', '每股收益-行业中位数', '每股收益-行业分位数', '每股收益-行业均值',
 '每股收益-行业最大值', '每股收益-行业最小值',
 
 '每股经营现金流量', '每股经营现金流量-行业中位数', '每股经营现金流量-行业分位数',
 '每股经营现金流量-行业均值', '每股经营现金流量-行业最大值', '每股经营现金流量-行业最小值',
 '股票代码', '股票简称',
 
 '营业收入', '营业收入-占行业份额', '营业收入-行业中位数', '营业收入-行业分位数', '营业收入-行业均值', '营业收入-行业最大值',
 '营业收入-行业最小值',

 '营业收入-同比增长', '营业收入-同比增长-行业中位数', '营业收入-同比增长-行业分位数',
 '营业收入-同比增长-行业均值', '营业收入-同比增长-行业最大值', '营业收入-同比增长-行业最小值',
 
 '营业收入-季度环比增长', '营业收入-季度环比增长-行业中位数', '营业收入-季度环比增长-行业分位数',
 '营业收入-季度环比增长-行业均值', '营业收入-季度环比增长-行业最大值',
 '营业收入-季度环比增长-行业最小值',
 
 '销售毛利率', '销售毛利率-行业中位数', '销售毛利率-行业分位数', '销售毛利率-行业均值',
 '销售毛利率-行业最大值', '销售毛利率-行业最小值']
"""

if __name__=='__main__':
    fpfm=get_fin_performance_ak('600519.SS','2020-12-31')    

#==============================================================================
    
def industry_name_em():
    """
    功能：从东方财富获取行业分类名称，限于中国A股
    """
    #获取最近的报表日期
    import datetime; today=datetime.date.today()
    start=date_adjust(today, adjust=-365)
    fs_dates=cvt_fs_dates(start,today,'all')
    endDate=fs_dates[-1:][0]

    #转换日期格式
    ak_date=convert_date_ts(endDate)
    print('\b'*99," Retrieving EM industry names ended on",endDate)
    #获取全体股票的业绩报表，指定截止日期
    df1 = ak.stock_em_yjbb(date=ak_date)
    """
    ['序号', '股票代码', '股票简称', '每股收益', '营业收入-营业收入', '营业收入-同比增长',
     '营业收入-季度环比增长', '净利润-净利润', '净利润-同比增长', '净利润-季度环比增长',
     '每股净资产', '净资产收益率', '每股经营现金流量', '销售毛利率',
     '所处行业', '最新公告日期']
    """
    print('\b'*99," Summerizing industry names for the above period ...")

    #替换行业
    df1c['所处行业']=df1c['所处行业'].apply(lambda x: '其他行业' if x == 'None' else x)

    industry_list=list(set(list(df2['所处行业'])))  
    try:
        industry_list.remove('0')
    except: pass

    #对列表中的中文字符串排序
    from pypinyin import pinyin, Style
    industry_list.sort(key = lambda keys:[pinyin(i, style=Style.TONE3) for i in keys])

    print("\n===== 行业分类：东方财富 =====\n")
    n=0
    for i in industry_list:
        n=n+1
        print(i,end=' ')
        if n==5:
            n=0
            print('')
    if n <5: print('')
    #import datetime; today=datetime.date.today()
    print("\n***来源：东方财富,",endDate)
    
    return industry_list    

if __name__=='__main__':
    df=industry_name_em()
#==============================================================================
if __name__=='__main__':
    industry="银行"
    rate="营业收入"
    top=5
    
def industry_rank_em(industry="银行",rate="oper revenue",top=5):
    """
    功能：从东方财富获取最新行业排名前几名，按照财务指标，限于中国A股
    """
    #获取最近的报表日期
    import datetime; today=datetime.date.today()
    start=date_adjust(today, adjust=-365)
    fs_dates=cvt_fs_dates(start,today,'all')
    endDate=fs_dates[-1:][0]

    rate_check=['eps','oper revenue','oper revenue growth','net earnings', 
                'earnings growth','naps','rona','oper cfps', 'gross margin']
    rate_cols=['每股收益','营业收入','营业收入-同比增长','净利润', 
                '净利润-同比增长','每股净资产','净资产收益率', 
                '每股经营现金流量', '销售毛利率']
    if not (rate in rate_check):
        print("  #Warning(industry_rank_em): unsupported financial rate",rate)
        print("  Supported ranking rates:",rate_check)
        return None
    
    #转换日期格式
    ak_date=convert_date_ts(endDate)
    print('\b'*99," Retrieving EM industry names ended on",endDate)
    #获取全体股票的业绩报表，指定截止日期
    df1 = ak.stock_em_yjbb(date=ak_date)
    """
    ['序号', '股票代码', '股票简称', '每股收益', '营业收入-营业收入', '营业收入-同比增长',
     '营业收入-季度环比增长', '净利润-净利润', '净利润-同比增长', '净利润-季度环比增长',
     '每股净资产', '净资产收益率', '每股经营现金流量', '销售毛利率',
     '所处行业', '最新公告日期']
    """
    print('\b'*99," Summerizing stock performance for industry",industry,'by',rate)
    
    #删除B股股票，只保留A股
    df1a = df1.drop(df1[df1['股票简称'].str.contains('B')].index)
    
    #按照所处行业升序
    df1b=df1a.sort_values(by=['所处行业','股票代码'],ascending=[True,False])
    #去掉重复记录，保留第一条
    df1c=df1b.drop_duplicates(subset=['股票代码'],keep='first')

    #替换行业
    df1c['所处行业']=df1c['所处行业'].apply(lambda x: '其他行业' if x == 'None' else x)
    
    #数据清洗：将空值替换为0
    df1d=df1c.fillna('0')
    #数据清洗：将"--"值替换为0
    df1e=df1d.replace('--','0')
    df2=df1e.replace('nan','0')
    
    #修改列名
    df2.rename(columns={'营业收入-营业收入':'营业收入','净利润-净利润':'净利润'},inplace=True) 
    
    #数据清洗：转换数值类型
    for c in df2.columns:
        if c == '股票代码': continue
        try:
            df2[c]=round(df2[c].astype('float'),2)
        except:
            continue
    
    #设置索引    
    df2['截止日期']=endDate
    df2['date']=pd.to_datetime(df2['截止日期'])
    df2.set_index('date',inplace=True)
    
    df2['ticker']=df2['股票代码']
    df2['endDate']=df2.index.strftime('%Y-%m-%d')
    df2['最新公告日期']=df2['最新公告日期'].apply(lambda x: x[:11])

    #筛选特定行业的股票
    industry_check=list(set(list(df2['所处行业'])))
    if not (industry in industry_check):
        print("  #Warning(industry_rank_em): unsupported em industry name",industry)
        print("  See supported industry by command: df=industry_name_em()")
        return None
        
    df3=df2[df2['所处行业'] == industry]
    rpos=rate_check.index(rate)
    rate=rate_cols[rpos]    #将财务指标名称从英文转为中文
    
    cols=['股票代码','股票简称','最新公告日期']+[rate]
    df_industry=df3[cols]
    i_min=df_industry[rate].min()
    i_max=df_industry[rate].max()
    i_avg=df_industry[rate].mean()
    i_med=df_industry[rate].median()
    i_sum=df_industry[rate].sum()
    num_industry=len(df_industry)
    
    ticker_list=list(df_industry['股票代码'])
    ticker_result=pd.DataFrame()
    for t in ticker_list:
        tickerdf=df_industry[df_industry['股票代码'] == t]
        x=tickerdf[rate].values[0]
        x_quantile=arg_percentile(df_industry[rate], x)
        tickerdf[rate+"-行业分位数%"]=x_quantile*100
        
        if rate in ['营业收入','净利润']:
            tickerdf[rate+"-占行业份额%"]=tickerdf[rate]/i_sum*100
            
        try:
            ticker_result=ticker_result.append(tickerdf)
        except:
            ticker_result=ticker_result._append(tickerdf)
    
    #排序：降序
    ticker_result["排名"]=ticker_result[rate].rank(ascending=False).astype('int')
    ticker_result.sort_values(by=rate,ascending=False,inplace=True) 
    for c in ticker_result.columns:
        try:
            ticker_result[c]=ticker_result[c].apply(lambda x: simple_number(x))
        except:
            continue
    
    #打印
    pd.set_option('display.max_columns', 1000)
    pd.set_option('display.width', 1000)
    pd.set_option('display.max_colwidth', 1000)
    pd.set_option('display.unicode.ambiguous_as_wide', True)
    pd.set_option('display.unicode.east_asian_width', True)
    
    if top > 0:
        rank_prefix="前"
        topn=top
        printdf=ticker_result.head(topn)
    else:
        rank_prefix="后"
        topn=-top
        printdf=ticker_result.tail(topn)
    
    print("\n===== 行业排名："+rate+"，"+rank_prefix+str(topn)+"名"+" =====")
    print("行业内企业个数 ：",num_industry)
    print("行业最小/最大值：",simple_number(i_min),'/',simple_number(i_max))
    print("行业均值/中位数：",simple_number(i_avg),'/',simple_number(i_med))
    print('')
    print(printdf.to_string(index=False))
    
    return ticker_result  

if __name__=='__main__':
    df=industry_rank_em("银行","oper revenue",top=10)
    df=industry_rank_em("银行","oper revenue",top=-10)
    
    df=industry_rank_em("银行","?",top=-10)
    
    df=industry_rank_em("银行",'eps',top=20)
    df=industry_rank_em("银行",'eps',top=-25)
    df=industry_rank_em("银行",'naps',top=20)
    df=industry_rank_em("银行",'oper cfps',top=20)
    
    df=industry_rank_em("银行",'rona',top=20)
    
    df=industry_rank_em("银行",'oper revenue growth',top=5)
    df=industry_rank_em("银行",'earnings growth',top=5)

#==============================================================================
if __name__=='__main__':
    industry="银行"
    tickers=['600036.SS','000001.SZ','601328.SS','601939.SS','601288.SS','601398.SS','601988.SS']
    rates=['eps','naps','oper cfps','oper revenue growth','earnings growth']
    
    tickers=''
    
def industry_rank_em2(tickers,rates=['eps','naps'],industry="银行",top=10):
    """
    功能：从东方财富获取某些股票在某些财务指标方面的行业排名，限于中国A股
    注意：当tickers为''时列出排名前或后top的股票
    """
    error_flag=False
    #获取最近的报表日期
    import datetime; today=datetime.date.today()
    start=date_adjust(today, adjust=-365)
    fs_dates=cvt_fs_dates(start,today,'all')
    endDate=fs_dates[-1:][0]

    if isinstance(tickers,str): tickers_selected=[tickers]
    elif isinstance(tickers,list): tickers_selected=tickers
    else:
        print("  #Warning(industry_rank_em2): unsupported stock codes",tickers)
        print("  Supporting a stock code or a list of stock codes")
        error_flag=True
    if error_flag: return
    
    stocks_selected=[]
    for t in tickers_selected:
        #是否中国股票
        result,prefix,suffix=split_prefix_suffix(t)
        if not (suffix in SUFFIX_LIST_CN) and not (tickers == ''):
            print("  #Warning(industry_rank_em2): not a stock in China",t)
            error_flag=True
        stocks_selected=stocks_selected+[prefix]
    if error_flag: return
    
    rate_check=['eps','oper revenue','oper revenue growth','net earnings', 
                'earnings growth','naps','rona','oper cfps', 'gross margin']
    rate_cols=['每股收益','营业收入','营业收入-同比增长','净利润', 
                '净利润-同比增长','每股净资产','净资产收益率', 
                '每股经营现金流量', '销售毛利率']
    if isinstance(rates,str): rate_list=[rates]
    elif isinstance(rates,list): rate_list=rates
    else:
        print("  #Warning(industry_rank_em2): unsupported financial rates",rates)
        print("  Supporting a financial rate or a list of rates as follows:",rate_check)
        error_flag=True
    if error_flag: return
    
    for rate in rate_list:
        if not (rate in rate_check):
            print("  #Warning(industry_rank_em2): unsupported financial rate",rate)
            print("  Supported ranking rates:",rate_check)
            error_flag=True
    if error_flag: return
    
    #转换日期格式
    ak_date=convert_date_ts(endDate)
    print('\b'*99," Retrieving EM industry names ended on",endDate)
    #获取全体股票的业绩报表，指定截止日期
    df1 = ak.stock_em_yjbb(date=ak_date)
    """
    ['序号', '股票代码', '股票简称', '每股收益', '营业收入-营业收入', '营业收入-同比增长',
     '营业收入-季度环比增长', '净利润-净利润', '净利润-同比增长', '净利润-季度环比增长',
     '每股净资产', '净资产收益率', '每股经营现金流量', '销售毛利率',
     '所处行业', '最新公告日期']
    """
    print('\b'*99," Summerizing stock performance for industry",industry,'by',rate)
    
    #删除B股股票，只保留A股
    df1a = df1.drop(df1[df1['股票简称'].str.contains('B')].index)
    
    #按照所处行业升序
    df1b=df1a.sort_values(by=['所处行业','股票代码'],ascending=[True,False])
    #去掉重复记录，保留第一条
    df1c=df1b.drop_duplicates(subset=['股票代码'],keep='first')

    #替换行业
    df1c['所处行业']=df1c['所处行业'].apply(lambda x: '其他行业' if x == 'None' else x)
    
    #数据清洗：将空值替换为0
    df1d=df1c.fillna('0')
    #数据清洗：将"--"值替换为0
    df1e=df1d.replace('--','0')
    df2=df1e.replace('nan','0')
    
    #修改列名
    df2.rename(columns={'营业收入-营业收入':'营业收入','净利润-净利润':'净利润'},inplace=True) 
    
    #数据清洗：转换数值类型
    for c in df2.columns:
        if c == '股票代码': continue
        try:
            df2[c]=round(df2[c].astype('float'),2)
        except:
            continue
    
    #设置索引    
    df2['截止日期']=endDate
    df2['date']=pd.to_datetime(df2['截止日期'])
    df2.set_index('date',inplace=True)
    
    df2['ticker']=df2['股票代码']
    df2['endDate']=df2.index.strftime('%Y-%m-%d')
    df2['最新公告日期']=df2['最新公告日期'].apply(lambda x: x[:11])

    #检查是否支持特定行业
    industry_check=list(set(list(df2['所处行业'])))
    if not (industry in industry_check):
        print("  #Warning(industry_rank_em2): unsupported em industry name",industry)
        print("  See supported industry by command: df=industry_name_em()")
        error_flag=True
    if error_flag: return
    
    df3=df2[df2['所处行业'] == industry]

    #筛选特定行业的股票
    for r in rate_list:
        rpos=rate_check.index(r)
        rate=rate_cols[rpos]
        
        cols=['股票代码','股票简称','最新公告日期']+[rate]
        df_industry=df3[cols]
        i_min=df_industry[rate].min()
        i_max=df_industry[rate].max()
        i_avg=df_industry[rate].mean()
        i_med=df_industry[rate].median()
        i_sum=df_industry[rate].sum()
        num_industry=len(df_industry)
        
        ticker_list=list(df_industry['股票代码'])
        ticker_result=pd.DataFrame()
        for t in ticker_list:
            tickerdf=df_industry[df_industry['股票代码'] == t]
            x=tickerdf[rate].values[0]
            x_quantile=arg_percentile(df_industry[rate], x)
            tickerdf[rate+"-行业分位数%"]=x_quantile*100
            
            if rate in ['营业收入','净利润']:
                tickerdf[rate+"-占行业份额%"]=tickerdf[rate]/i_sum*100
                
            try:
                ticker_result=ticker_result.append(tickerdf)
            except:
                ticker_result=ticker_result._append(tickerdf)
        
        #排序：降序
        ticker_result["排名"]=ticker_result[rate].rank(ascending=False).astype('int')
        ticker_result.sort_values(by=rate,ascending=False,inplace=True) 
        for c in ticker_result.columns:
            try:
                ticker_result[c]=ticker_result[c].apply(lambda x: simple_number(x))
            except:
                continue
        
        #打印
        pd.set_option('display.max_columns', 1000)
        pd.set_option('display.width', 1000)
        pd.set_option('display.max_colwidth', 1000)
        pd.set_option('display.unicode.ambiguous_as_wide', True)
        pd.set_option('display.unicode.east_asian_width', True)
        
        if (len(stocks_selected) >= 1) and not (tickers == ''):
            printdf=ticker_result[ticker_result['股票代码'].isin(stocks_selected)]
        else:
            if top > 0:
                printdf=ticker_result.head(top)
            else:
                printdf=ticker_result.tail(-top)
        
        print("\n===== 行业排名："+industry+'，'+rate+" =====")
        print("行业内企业个数 ：",num_industry)
        print("行业最小/最大值：",simple_number(i_min),'/',simple_number(i_max))
        print("行业均值/中位数：",simple_number(i_avg),'/',simple_number(i_med))
        print('')
        print(printdf.to_string(index=False))
    
    return  

if __name__=='__main__':
    industry="银行"
    tickers1=['600036.SS','000001.SZ','601009.SS','001227.SZ']
    tickers2=['601328.SS','601939.SS','601288.SS','601398.SS','601988.SS']
    rates=['eps','naps','oper cfps','oper revenue growth','earnings growth']

    industry_rank_em2(tickers1+tickers2,rates,industry)
    industry_rank_em2('',rates,industry,top=5)  #每项指标的行业前几名
    
#==============================================================================
def simple_number(number):
    """
    功能：将数字表示为易读的字符化数值，并截取小数点
    """
    
    if number < 0.001:
        number1=round(number,5)
        suff=''  
    
    if number < 1:
        number1=round(number,4)
        suff=''  

    if number >= 1:
        number1=round(number,2)
        suff=''
    
    if number >= 10000:
        number1=round(number/10000,2)
        suff='万'

    if number >= 1000000:
        number1=round(number/1000000,2)
        suff='百万'

    if number >= 100000000:
        number1=round(number/100000000,2)
        suff='亿'        

    if number >= 1000000000000:
        number1=round(number/1000000000000,2)
        suff='万亿'        
        
    number2=str(number1)+suff
    
    return number2

if __name__=='__main__':
    simple_number(0.03257)
    simple_number(0.58726)
    simple_number(1.3289)
    simple_number(13283.569)
    simple_number(1234569874123)
#==============================================================================

if __name__=='__main__':
    tickers=["600606.SS","600606.SS"] 
    endDate="2020-12-31"
    
def get_fin_performance_akm(tickers,endDate):
    """
    从akshare获取业绩报表，多个股票，1个截止日期，限于中国A股
    获取的项目：所有原始项目
    注意：
    """

    #是否中国股票
    prefix_list=[]
    for t in tickers:
        result,prefix,suffix=split_prefix_suffix(t)
        if not (suffix in SUFFIX_LIST_CN):
            print("  #Warning(get_fin_performance_akm): not a stock in China",t)
            return None  
        prefix_list=prefix_list+[prefix]
    
    #转换日期格式
    ak_date=convert_date_ts(endDate)
    print('\b'*99," Retrieving financial performance ended on",endDate)
    #获取全体股票的业绩报表，指定截止日期
    df1 = ak.stock_em_yjbb(date=ak_date)
    print('\b'*99," Calculating financial performance for the above period")
    
    if df1 is None:
        print("  #Warning(get_fin_performance_akm): reports inaccessible for",endDate)
        return None
    if len(df1) == 0:
        print("  #Warning(get_fin_performance_akm): zero reports found for",endDate)
        return None
    
    #删除B股股票，只保留A股
    df1a = df1.drop(df1[df1['股票简称'].str.contains('B')].index)
    
    #按照股票代码升序+最新公告日期降序排序
    df1b=df1a.sort_values(by=['股票代码','最新公告日期'],ascending=[True,False])
    #去掉重复记录，保留第一条
    df1c=df1b.drop_duplicates(subset=['股票代码'],keep='first')

    #替换行业
    df1c['所处行业']=df1c['所处行业'].apply(lambda x: '其他行业' if x == 'None' else x)
    
    #数据清洗：将空值替换为0
    df1d=df1c.fillna('0')
    #数据清洗：将"--"值替换为0
    df1e=df1d.replace('--','0')
    df2=df1e.replace('nan','0')
    
    #修改列名
    df2.rename(columns={'营业收入-营业收入':'营业收入','净利润-净利润':'净利润'},inplace=True) 
    
    #数据清洗：转换数值类型
    for c in df2.columns:
        if c == '股票代码': continue
        try:
            df2[c]=df2[c].astype('float')
        except:
            continue
    
    #设置索引    
    df2['截止日期']=endDate
    df2['date']=pd.to_datetime(df2['截止日期'])
    df2.set_index('date',inplace=True)
    
    df2['ticker']=df2['股票代码']
    df2['endDate']=df2.index.strftime('%Y-%m-%d')
    df2['最新公告日期']=df2['最新公告日期'].apply(lambda x: x[:11])
    
    #筛选特定股票的数据
    mtdf=pd.DataFrame()
    for prefix in prefix_list:
        tickerdf=df2[df2['ticker'] == prefix]
        industry=tickerdf['所处行业'].values[0]
        df_industry=df2[df2['所处行业'] == industry]
        num_industry=len(df_industry)
        
        rates_industry=['每股收益','营业收入','营业收入-同比增长','营业收入-季度环比增长',
                        '净利润','净利润-同比增长','净利润-季度环比增长','每股净资产',
                        '净资产收益率','每股经营现金流量','销售毛利率']
        for r in rates_industry:
            i_min=df_industry[r].min()
            i_max=df_industry[r].max()
            i_avg=df_industry[r].mean()
            i_med=df_industry[r].median()
            
            tickerdf[r+"-行业最小值"]=i_min
            tickerdf[r+"-行业最大值"]=i_max
            tickerdf[r+"-行业均值"]=i_avg
            tickerdf[r+"-行业中位数"]=i_med
            
            x=tickerdf[r].values[0]
            x_quantile=arg_percentile(df_industry[r], x)
            tickerdf[r+"-行业分位数"]=x_quantile*100
            
            if r in ['营业收入','净利润']:
                i_sum=df_industry[r].sum()
                tickerdf[r+"-占行业份额"]=tickerdf[r]/i_sum*100
        tickerdf['同行数量']=num_industry
        
        #排序字段
        cols=list(tickerdf)
        cols.sort(reverse=False)
        tickerdf2=tickerdf[cols]
        
        #加入结果数据表，用于返回
        try:
            mtdf=mtdf.append(tickerdf2)
        except:
            mtdf=mtdf._append(tickerdf2)
    
    return mtdf

if __name__=='__main__':
    tickers=["600519.SS","600606.SS"] 
    mtdf=get_fin_performance_akm(tickers,'2020-12-31')
    
#==============================================================================
if __name__=='__main__':
    fin_rate="Current Ratio"
    prompt=False

def cvt_fin_rate(fin_rate,prompt=False,printout=True):
    """
    功能：查表获得财务指标的计算来源以及字段名称
    """
    
    #财务指标结构字典
    rate_dict={
        #数据源函数：get_fin_indicator_ak
        "diluted eps":("get_fin_indicator_ak","摊薄每股收益(元)"),
        "weighted eps":("get_fin_indicator_ak","加权每股收益(元)"),
        "adjusted eps":("get_fin_indicator_ak","每股收益_调整后(元)"),
        "recurring eps":("get_fin_indicator_ak","扣除非经常性损益后的每股收益(元)"),
        
        "naps":("get_fin_indicator_ak","每股净资产_调整前(元)"),
        "net assets per share":("get_fin_indicator_ak","每股净资产_调整前(元)"),
        "adjusted naps":("get_fin_indicator_ak","每股净资产_调整后(元)"),
        "capital reserve per share":("get_fin_indicator_ak","每股资本公积金(元)"),
        "undistributed profit per share":("get_fin_indicator_ak","每股未分配利润(元)"),
        
        "roa":("get_fin_indicator_ak","资产报酬率(%)"),
        
        "reward on shareholder equity":("get_fin_indicator_ak","股本报酬率(%)"),
        "reward on net assets":("get_fin_indicator_ak","净资产报酬率(%)"),
        "return on net assets":("get_fin_indicator_ak","净资产收益率(%)"),
        "rona":("get_fin_indicator_ak","净资产收益率(%)"),
        "weighted return on net assets":("get_fin_indicator_ak","加权净资产收益率(%)"),
        "weighted rona":("get_fin_indicator_ak","加权净资产收益率(%)"),
        "return on investment":("get_fin_indicator_ak","投资收益率(%)"),
        "roi":("get_fin_indicator_ak","投资收益率(%)"),
        
        "profit margin":("get_fin_indicator_ak","销售净利率(%)"),
        "gross margin":("get_fin_indicator_ak","销售毛利率(%)"),
        "oper profit share":("get_fin_indicator_ak","主营利润比重"),
        "payout ratio":("get_fin_indicator_ak","股息发放率(%)"),
        "roi":("get_fin_indicator_ak","投资收益率(%)"),
        
        "oper revenue growth":("get_fin_indicator_ak","主营业务收入增长率(%)"),
        "profit margin growth":("get_fin_indicator_ak","净利润增长率(%)"),
        "net assets growth":("get_fin_indicator_ak","净资产增长率(%)"),
        "total assets growth":("get_fin_indicator_ak","总资产增长率(%)"),
        
        "receivables turnover":("get_fin_indicator_ak","应收账款周转率(次)"),
        "inventory turnover":("get_fin_indicator_ak","存货周转率(次)"),
        "fixed assets turnover":("get_fin_indicator_ak","固定资产周转率(次)"),
        "total assets turnover":("get_fin_indicator_ak","总资产周转率(次)"),
        "current assets turnover":("get_fin_indicator_ak","流动资产周转率(次)"),
        "equity assets turnover":("get_fin_indicator_ak","股东权益周转率(次)"),
        
        "current ratio":("get_fin_indicator_ak","流动比率"),
        "quick ratio":("get_fin_indicator_ak","速动比率"),
        "cash ratio":("get_fin_indicator_ak","现金比率(%)"),
        "tie":("get_fin_indicator_ak","利息支付倍数"),
        "times interest earned":("get_fin_indicator_ak","利息支付倍数"),
        "equity to assets":("get_fin_indicator_ak","股东权益比率(%)"),
        "ltd%":("get_fin_indicator_ak","长期负债比率(%)"),
        "long-term debts%":("get_fin_indicator_ak","长期负债比率(%)"),
        "debts to equity":("get_fin_indicator_ak","负债与所有者权益比率(%)"),
        "liabilities to equity":("get_fin_indicator_ak","产权比率(%)"),
        "capitalization%":("get_fin_indicator_ak","资本化比率(%)"),
        "ppe residual":("get_fin_indicator_ak","固定资产净值率(%)"),
        "tangible assets to debts":("get_fin_indicator_ak","清算价值比率(%)"),
        "fixed assets%":("get_fin_indicator_ak","固定资产比重(%)"),
        "debts to assets":("get_fin_indicator_ak","资产负债率(%)"),
        "cash flow ratio":("get_fin_indicator_ak","现金流量比率(%)"),
        "cashflow ratio":("get_fin_indicator_ak","现金流量比率(%)"),
        "net oper cashflow to revenue":("get_fin_indicator_ak","经营现金净流量对销售收入比率(%)"),

        #数据源函数：get_fin_performance_ak，百分比
        "net earnings":("get_fin_performance_ak","净利润"),
        "earnings industry share":("get_fin_performance_ak","净利润-占行业份额"),
        "earnings industry quantile":("get_fin_performance_ak","净利润-行业分位数"),
        "earnings growth":("get_fin_performance_ak","净利润-同比增长"),
        "earnings growth industry quantile":("get_fin_performance_ak","净利润-同比增长-行业分位数"),

        "roe":("get_fin_performance_ak","净资产收益率"),
        "roe industry quantile":("get_fin_performance_ak","净资产收益率-行业分位数"),
        "naps":("get_fin_performance_ak","每股净资产"),
        "naps industry quantile":("get_fin_performance_ak","每股净资产-行业分位数"),
        "eps":("get_fin_performance_ak","每股收益"),
        "eps industry quantile":("get_fin_performance_ak","每股收益-行业分位数"),

        "oper cfps":("get_fin_performance_ak","每股经营现金流量"),
        "oper cfps industry quantile":("get_fin_performance_ak","每股经营现金流量-行业分位数"),
        
        "oper revenue":("get_fin_performance_ak","营业收入"),
        "oper revenue industry share":("get_fin_performance_ak","营业收入-占行业份额"),
        "oper revenue industry quantile":("get_fin_performance_ak","营业收入-行业分位数"),
        "oper revenue growth":("get_fin_performance_ak","营业收入-同比增长"),
        "oper revenue growth industry quantile":("get_fin_performance_ak","营业收入-同比增长-行业分位数"),

        "gross margin industry quantile":("get_fin_performance_ak","销售毛利率-行业分位数"),

        #数据源函数：get_fin_abstract_ak
        "diluted naps":("get_fin_abstract_ak","每股净资产-摊薄/期末股数"),
        "cfps":("get_fin_abstract_ak","每股现金流"),
        }

    #是否需要提示？
    if prompt or (fin_rate in ['?','？']):
        promptdf=pd.DataFrame(columns=('财务指标代码', '财务指标名称'))
        key_list=rate_dict.keys()   
        for k in key_list:
            #print(k)
            result=rate_dict.get(k)
            (source,name_cn)=result
            s=pd.Series({'财务指标代码':k, '财务指标名称':name_cn})
            try:
                promptdf=promptdf.append(s, ignore_index=True)
            except:
                promptdf=promptdf._append(s, ignore_index=True)
        promptdf.sort_values('财务指标代码',ascending=True,inplace=True)   

        #打印对齐   
        if printout:
            pd.set_option('display.max_columns', 1000)
            pd.set_option('display.width', 1000)
            pd.set_option('display.max_colwidth', 1000)
            pd.set_option('display.unicode.ambiguous_as_wide', True)
            pd.set_option('display.unicode.east_asian_width', True)
            print(promptdf.to_string(index=False))
            return None,None
        else:
            return promptdf,None
        
    #搜索字典
    rate=fin_rate.lower()
    result=rate_dict.get(rate)
    if result is None:
        return None,None
    (source,name_cn)=result
    
    return source,name_cn

if __name__=='__main__':
    cvt_fin_rate("?",prompt=True)
    cvt_fin_rate("Current Ratio")
    cvt_fin_rate("Quick Ratio")
#==============================================================================
def arg_percentile(series, x):
    """
    功能：求x在序列series中的分位数
    """
    import numpy as np
    # 分位数的启始区间
    a, b = 0, 1
    while True:
        # m是a、b的终点
        m = (a+b)/2
        # 可以打印查看求解过程
        # print(np.percentile(series, 100*m), x)
        if np.percentile(series, 100*m) >= x:
            b = m
        elif np.percentile(series, 100*m) < x:
            a = m
        # 如果区间左右端点足够靠近，则退出循环。
        if np.abs(a-b) <= 0.000001:
            break
    return m

#==============================================================================
if __name__=='__main__':
    start='2020-1-1'
    end='2021-6-30'
    period_type='all'
    period_type='annual'
    period_type='quarterly'
    period_type='semiannual'

def cvt_fs_dates(start,end,period_type='all'):
    """
    功能：基于年报类型给出期间内财报的各个截止日期列表
    """
    #检查期间的合理性
    valid,start1,end1=check_period(start,end)
    if not valid:
        print("  #Warning(get_fs_dates): invalid period",start,end)
        return None
    
    #构造所有年报日期
    start_year=start1.year
    end_year=end1.year
    
    fs_dates_all=[]
    q1_str='-03-31'; q2_str='-06-30'; q3_str='-09-30'; q4_str='-12-31'
    for y in range(start_year,end_year+1):
        #print(y)
        fs_dates_all=fs_dates_all+[str(y)+q1_str,str(y)+q2_str,str(y)+q3_str,str(y)+q4_str]
    
    #过滤年报日期
    fs_dates=[]
    for d in fs_dates_all:
        dd=pd.to_datetime(d)
        #print(dd,start1,end1)
        if (dd < start1) or (dd > end1): continue
        
        #区分年报季报
        dd_month=dd.month
        if period_type == 'annual':
            if not (dd_month == 12): continue
        if period_type == 'semiannual':
            if not (dd_month in [6,12]): continue
        
        fs_dates=fs_dates+[d]  
              
    return fs_dates

if __name__=='__main__':
    cvt_fs_dates('2020-7-1','2021-10-1')
    cvt_fs_dates('2020-7-1','2021-10-1',period_type='annual')
    cvt_fs_dates('2020-7-1','2021-10-1',period_type='semiannual')
    cvt_fs_dates('2020-7-1','2021-10-1',period_type='quarterly')
    
#==============================================================================
if __name__=='__main__':
    ticker="600606.SS" 
    rate1='ROA'
    rate2='Oper Revenue Industry Share'
    start='2020-1-1'
    end='2021-6-30'
    period_type='all'
    
    period_type='annual'
    period_type='quarterly'
    period_type='semiannual'
    
def prepare_fin_rate1t2r_china(ticker,rate1,rate2,start,end,period_type='all'):
    """
    功能：准备财务准备，1个股票，2个指标，限于中国A股
    注意：过滤期间，过滤财报类型
    
    """
    #检查期间的合理性
    valid,start1,end1=check_period(start,end)
    if not valid:
        print("  #Warning(prepare_fin_rate1t2r_china): invalid period",start,end)
        return None,None

    #是否中国股票
    result,prefix,suffix=split_prefix_suffix(ticker)
    if not (suffix in SUFFIX_LIST_CN):
        print("  #Warning(prepare_fin_rate1t2r_china): not a stock in China",ticker)
        return None,None        

    #检查指标是否支持
    fin_rates,_=cvt_fin_rate('?',prompt=True,printout=False)
    rate_list=list(fin_rates['财务指标代码'])
    if not (rate1.lower() in rate_list):
        print("  #Warning(prepare_fin_rate1t2r_china): unsupported financial rate",rate1)
        return None,None
    if not (rate2.lower() in rate_list):
        print("  #Warning(prepare_fin_rate1t2r_china): unsupported financial rate",rate2)
        return None,None    
    #--------------------------------------------------------------------------
    func1,name1=cvt_fin_rate(rate1)
    func2,name2=cvt_fin_rate(rate2)

    if func1 == 'get_fin_indicator_ak':
        find1=get_fin_indicator_ak(ticker)
        ratedf1=find1[['ticker',name1]]
        if func2 == func1:
            ratedf2=find1[['ticker',name2]]

    if func1 == 'get_fin_abstract_ak':
        fabs1=get_fin_abstract_ak(ticker)
        ratedf1=fabs1[['ticker',name1]]
        if func2 == func1:
            ratedf2=fabs1[['ticker',name2]]

    if func1 == 'get_fin_performance_ak':
        fs_dates=cvt_fs_dates(start,end,period_type)
        #合成各个财报日期
        fpfm1=pd.DataFrame()
        for enddate in fs_dates:
            tmp=get_fin_performance_ak(ticker,enddate)
            try:
                fpfm1=fpfm1.append(tmp)
            except:
                fpfm1=fpfm1._append(tmp)
        ratedf1=fpfm1[['ticker',name1,'股票简称','所处行业','同行数量']]
        if func2 == func1:
            ratedf2=fpfm1[['ticker',name2,'股票简称','所处行业','同行数量']]
    
    #若ratedf2尚未定义
    if not ('ratedf2' in locals().keys()):
        if func2 == 'get_fin_indicator_ak':
            find2=get_fin_indicator_ak(ticker)
            ratedf2=find2[['ticker',name2]]
            
        if func2 == 'get_fin_abstract_ak':
            fabs2=get_fin_abstract_ak(ticker)
            ratedf2=fabs2[['ticker',name2]]

        if func2 == 'get_fin_performance_ak':
            fs_dates=cvt_fs_dates(start,end,period_type)
            #合成各个财报日期
            fpfm2=pd.DataFrame()
            for enddate in fs_dates:
                tmp=get_fin_performance_ak(ticker,enddate)
                try:
                    fpfm2=fpfm2.append(tmp)
                except:
                    fpfm2=fpfm2._append(tmp)
            ratedf2=fpfm2[['ticker',name2,'股票简称','所处行业','同行数量']]
            
    #过滤起始日期：
    ratedf1b=ratedf1[(ratedf1.index >= start1) & (ratedf1.index <= end1)]
    ratedf2b=ratedf2[(ratedf2.index >= start1) & (ratedf2.index <= end1)]

    #过滤年报类型
    ratedf1b['month']=ratedf1b.index.month
    if period_type == 'annual':
        ratedf1c=ratedf1b[ratedf1b['month'] == 12]
    elif period_type == 'semiannual':
        ratedf1c=ratedf1b[ratedf1b['month'].isin([6,12])]
    else:
        ratedf1c=ratedf1b
    del ratedf1c['month']
    
    ratedf2b['month']=ratedf2b.index.month
    if period_type == 'annual':
        ratedf2c=ratedf2b[ratedf2b['month'] == 12]
        
    elif period_type == 'semiannual':
        ratedf2c=ratedf2b[ratedf2b['month'].isin([6,12])]
    else:
        ratedf2c=ratedf2b
    del ratedf2c['month']

    print("  Retrieved",len(ratedf1c),rate1,"and",len(ratedf2c),rate2,"records for",ticker)

    return ratedf1c,ratedf2c

if __name__=='__main__':
    ticker='600519.SS'
    start='2021-5-1'
    end='2021-11-30'
    df1=prepare_fin_rate1t2r_china(ticker,'ROA','ROE',start,end,period_type='all')
    df2=prepare_fin_rate1t2r_china(ticker,'ROA','CFPS',start,end,period_type='all') 
    df3=prepare_fin_rate1t2r_china(ticker,'ROA','Oper Revenue Industry Share',start,end,period_type='all') 
#==============================================================================
if __name__=='__main__':
    ticker='600519.SS'
    start='2021-5-1'
    end='2021-11-30'
    period_type='all'

def prepare_fin_rate1tmr_china(ticker,rates,start,end,period_type='all'):
    """
    功能：准备财务准备，1个股票，多个指标，限于中国A股
    注意：过滤期间，过滤财报类型
    
    """
    #检查期间的合理性
    valid,start1,end1=check_period(start,end)
    if not valid:
        print("  #Warning(prepare_fin_rate1tmr_china): invalid period",start,end)
        return None

    #是否中国股票
    result,prefix,suffix=split_prefix_suffix(ticker)
    if not (suffix in SUFFIX_LIST_CN):
        print("  #Warning(prepare_fin_rate1tmr_china): not a stock in China",ticker)
        return None       
    
    #检查是否多个指标
    if isinstance(rates,str):
        mrate_list=[rates]
    elif isinstance(rates,list):
        mrate_list=rates
    else:
        print("  #Warning(prepare_fin_rate1tmr_china): invalid financial rate/rate list",rates)
        return None       
    
    #检查指标是否支持
    sup_fin_rates,_=cvt_fin_rate('?',prompt=True,printout=False)
    sup_rate_list=list(sup_fin_rates['财务指标代码'])
    for r in mrate_list:
        if not (r.lower() in sup_rate_list):
            print("  #Warning(prepare_fin_rate1tmr_china): unsupported financial rate",r)
            return None
    #--------------------------------------------------------------------------
    #逐个检查财务指标，若不存在则抓取，若存在则直接利用，避免重复抓取
    rdf_list=[]
    for r in mrate_list:
        func,name=cvt_fin_rate(r)
        if func == 'get_fin_indicator_ak':
            if not ('find' in locals().keys()):
                find=get_fin_indicator_ak(ticker)
            rdf=find[['ticker',name]]
    
        if func == 'get_fin_abstract_ak':
            if not ('fabs' in locals().keys()):
                fabs=get_fin_abstract_ak(ticker)
            rdf=fabs[['ticker',name]]
    
        if func == 'get_fin_performance_ak':
            if not ('fpfm' in locals().keys()):
                fs_dates=cvt_fs_dates(start,end,period_type)
                #合成各个财报日期
                fpfm=pd.DataFrame()
                for enddate in fs_dates:
                    tmp=get_fin_performance_ak(ticker,enddate)
                    try:
                        fpfm=fpfm.append(tmp)
                    except:
                        fpfm=fpfm._append(tmp)
            rdf=fpfm[['ticker',name,'股票简称','所处行业','同行数量']]
        
        rdf_list=rdf_list+[rdf]
            
    rdf_list1=[]
    for rdf in rdf_list:
        #过滤起始日期：
        rdf1=rdf[(rdf.index >= start1) & (rdf.index <= end1)]

        #过滤年报类型
        rdf1['month']=rdf1.index.month
        if period_type == 'annual':
            rdf1b=rdf1[rdf1['month'] == 12]
        elif period_type == 'semiannual':
            rdf1b=rdf1[rdf1['month'].isin([6,12])]
        else:
            rdf1b=rdf1
        del rdf1b['month']
        print("  Retrieved",len(rdf1b),"records for",ticker,list(rdf1b)[1])
        
        rdf_list1=rdf_list1+[rdf1b]

    return rdf_list1

if __name__=='__main__':
    ticker='600519.SS'
    start='2021-5-1'
    end='2021-11-30'
    rates=['oper profit share','Oper Revenue Industry Share','earnings industry share']
    df1=prepare_fin_rate1tmr_china(ticker,['ROA','ROE'],start,end,period_type='all')
    df2=prepare_fin_rate1tmr_china(ticker,['ROA','CFPS'],start,end,period_type='all') 
    df3=prepare_fin_rate1tmr_china(ticker,rates,start,end,period_type='all') 
#==============================================================================
if __name__=='__main__':
    tickers=['600519.SS','600606.SS']
    rate='oper revenue industry share'
    start='2021-5-1'
    end='2021-11-30'
    period_type='all'

def prepare_fin_ratemt1r_china(tickers,rate,start,end,period_type='all'):
    """
    功能：准备财务指标，多个股票，1个指标，限于中国A股
    注意：过滤期间，过滤财报类型
    
    """
    #检查期间的合理性
    valid,start1,end1=check_period(start,end)
    if not valid:
        print("  #Warning(prepare_fin_ratemt1r_china): invalid period",start,end)
        return None
    
    #检查是否多个股票
    if isinstance(tickers,str):
        mticker_list=[tickers]
    elif isinstance(tickers,list):
        mticker_list=tickers
    else:
        print("  #Warning(prepare_fin_ratemt1r_china): invalid stock/stock list",tickers)
        return None       

    #是否中国股票
    prefix_list=[]
    for t in mticker_list:
        result,prefix,suffix=split_prefix_suffix(t)
        if not (suffix in SUFFIX_LIST_CN):
            print("  #Warning(prepare_fin_ratemt1r_china): not a stock in China",ticker)
            return None  
        prefix_list=prefix_list+[prefix]
        
    #检查指标是否支持
    sup_fin_rates,_=cvt_fin_rate('?',prompt=True,printout=False)
    sup_rate_list=list(sup_fin_rates['财务指标代码'])
    if not (rate.lower() in sup_rate_list):
        print("  #Warning(prepare_fin_ratemt1r_china): unsupported financial rate",rate)
        print("  Check supported financial rates? use command rates=cvt_fin_rate('?')")
        return None
    #--------------------------------------------------------------------------
    #逐个检查股票指标，若不存在则抓取，若存在则直接利用，避免重复抓取
    func,name=cvt_fin_rate(rate)
    rdf_list=[]
    if func in ['get_fin_indicator_ak','get_fin_abstract_ak']:
        for t in mticker_list:
            if func == 'get_fin_indicator_ak':
                find=get_fin_indicator_ak(t)
                rdf=find[['ticker',name]]
        
            if func == 'get_fin_abstract_ak':
                fabs=get_fin_abstract_ak(t)
                rdf=fabs[['ticker',name]]
            
            rdf_list=rdf_list+[rdf]

    #为了避免重复抓取，将此段独立出来
    if func == 'get_fin_performance_ak':
        fs_dates=cvt_fs_dates(start,end,period_type)
        #合成各个财报日期
        fpfm=pd.DataFrame()
        for enddate in fs_dates:
            tmp=get_fin_performance_akm(mticker_list,enddate)
            try:
                fpfm=fpfm.append(tmp)
            except:
                fpfm=fpfm._append(tmp)
        
        #处理各个rdf进入列表
        for prefix in prefix_list:
            rdf=fpfm[fpfm['ticker'] == prefix]
            rdf2=rdf[['ticker',name,'股票简称','所处行业','同行数量']]
            rdf_list=rdf_list+[rdf2]
            
    rdf_list1=[]
    for rdf in rdf_list:
        #过滤起始日期：
        rdf1=rdf[(rdf.index >= start1) & (rdf.index <= end1)]

        #过滤年报类型
        rdf1['month']=rdf1.index.month
        if period_type == 'annual':
            rdf1b=rdf1[rdf1['month'] == 12]
        elif period_type == 'semiannual':
            rdf1b=rdf1[rdf1['month'].isin([6,12])]
        else:
            rdf1b=rdf1
        del rdf1b['month']
        
        rdf_list1=rdf_list1+[rdf1b]

    return rdf_list1

if __name__=='__main__':
    tickers=['600519.SS','600606.SS','000002.SZ']
    start='2020-5-1'
    end='2021-11-30'
    df1=prepare_fin_ratemt1r_china(tickers,'ROA',start,end,period_type='all')
    df2=prepare_fin_ratemt1r_china(tickers,'Profit Margin Growth',start,end,period_type='all') 
    df3=prepare_fin_ratemt1r_china(tickers,'oper revenue industry share',start,end,period_type='annual') 

#==============================================================================
def cn_codetranslate(ticker):
    """
    功能：将中国股票代码转换为股票简称
    注意：既能转换带后缀的股票代码，也能转换不带后缀的股票代码
    """
    result,prefix,suffix=split_prefix_suffix(ticker)
    if suffix in SUFFIX_LIST_CN:
        name=ticker_name(ticker,'stock')

    if suffix =='':
        for s in SUFFIX_LIST_CN:
            ticker_try=ticker+'.'+s
            name=ticker_name(ticker_try,'stock')
            print('\b'*99," Looking for the short name of stock",ticker)
            if not (name == ticker_try): break
        
    return name

if __name__=='__main__':
    cn_codetranslate('600519.SS')
    cn_codetranslate('600519')
        
#==============================================================================

if __name__=='__main__':
    tickers=['600519.SS','000858.SZ','600779.SS',]
    rate='oper revenue industry share'
    start='2021-5-1'
    end='2021-11-30'
    period_type='all'

def print_fin_ratemt1r_china(tickers,rate,start,end,period_type='all'):
    """
    功能：打印财务指标，多个股票，1个指标，限于中国A股
    注意：过滤期间，过滤财报类型
    """
    rdf_list=prepare_fin_ratemt1r_china(tickers,rate,start,end,period_type)
    
    _,rate_name=cvt_fin_rate(rate)
    rdf_all=pd.DataFrame()
    #rdf=rdf_list[0]
    for rdf in rdf_list:
        t=rdf['ticker'].values[0]
        df_tmp=rdf[[rate_name]]
        df_tmp.rename(columns={rate_name:t},inplace=True)
        df_tmpt=df_tmp.T
        try:
            rdf_all=rdf_all.append(df_tmpt)
        except:
            rdf_all=rdf_all._append(df_tmpt)
    
    rdf_all['股票代码']=rdf_all.index
    rdf_all['股票简称']=rdf_all['股票代码'].apply(lambda x: cn_codetranslate(x))
    
    cols=list(rdf_all)
    for c in cols:
        try:
            cs=c.strftime("%Y-%m-%d")
            rdf_all[cs]=round(rdf_all[c],2)
            del rdf_all[c]
        except:
            continue
    
    #设置打印对齐
    pd.set_option('display.max_columns', 1000)
    pd.set_option('display.width', 1000)
    pd.set_option('display.max_colwidth', 1000)
    pd.set_option('display.unicode.ambiguous_as_wide', True)
    pd.set_option('display.unicode.east_asian_width', True)    
    
    print("\n===== 财务指标对比："+rate_name+" =====")
    print(rdf_all.to_string(index=False))
    
    import datetime; today=datetime.date.today()
    print("\n*** 数据来源：sina/EM，"+str(today))
    
    return rdf_all
    
if __name__=='__main__':
    tickers=['600519.SS','000858.SZ','600779.SS',]
    rate='oper revenue industry share'
    start='2021-5-1'
    end='2021-11-30'
    
    df=print_fin_ratemt1r_china(tickers,rate,start,end,period_type='all')        
#==============================================================================
#==============================================================================
#==============================================================================
if __name__ == '__main__':
    tickers=['600606.SS','600519.SS']
    items='Current Ratio'
    start='2020-1-1'
    end='2021-11-30'
    period_type='annual'

    datatag=False
    power=0
    zeroline=False
    twinx=False

def compare_history_china(tickers,items,start,end,period_type='annual', \
                    datatag=False,power=0,zeroline=False,twinx=False):
    """
    功能：比较一只股票两个指标或两只股票一个指标的时序数据，绘制折线图
    datatag=False: 不将数值标记在图形旁
    zeroline=False：不绘制水平零线
    twinx=False：单纵轴
    """
    error_flag=False
    
    #检查股票个数
    if isinstance(tickers,str): 
        ticker_num=1; ticker1=tickers
    elif isinstance(tickers,list):
        ticker_num=len(tickers)
        if ticker_num >= 1:
            ticker1=tickers[0]
        if ticker_num >= 2:
            ticker2=tickers[1]
        if ticker_num == 0:
            print("  #Error(compare_history_china): no stock code found",tickers)
            error_flag=True

    #检查指标个数
    item_num=1
    if isinstance(items,list): 
        if len(items) >= 1: 
            item1=items[0]
        if len(items) >= 2: 
            item2=items[1]
            item_num=2
        if len(items) == 0: 
            print("  #Error(compare_history_china): no analytical item found",items)
            error_flag=True
    else:
        item1=items
        
    if error_flag: return None,None        
    
    #判断比较模式
    if (ticker_num == 1) and (item_num == 1): mode='T1I1'
    if (ticker_num == 1) and (item_num == 2): mode='T1I2'
    if (ticker_num == 2): mode='T2I1'
    
    #抓取数据
    if mode in ['T1I1','T1I2']:
        rdf_list1=prepare_fin_rate1tmr_china(ticker1,items,start,end,period_type)
        if rdf_list1 is None: error_flag=True
        else:
            for rdf in rdf_list1:
                if rdf is None: error_flg=True
                if len(rdf) == 0: error_flag=True
            if not error_flag:
                df1=rdf_list1[0]
                try: df2=rdf_list1[1]
                except: pass
    if mode in ['T2I1']:
        rdf_list2=prepare_fin_ratemt1r_china(tickers,item1,start,end,period_type)
        if rdf_list2 is None: error_flag=True
        else:
            for rdf in rdf_list2:
                if rdf is None: error_flag=True
                if len(rdf) == 0: error_flag=True
            if not error_flag:
                df1=rdf_list2[0]
                df2=rdf_list2[1]

    if error_flag: 
        print("  #Error(compare_history_china): info not found for",tickers,"on",items)
        return None,None        

    #绘图：T1I1，单折线
    import datetime; today=datetime.date.today()
    footnote9="数据来源: sina/EM, "+str(today)
    if mode == 'T1I1':
        _,colname=cvt_fin_rate(item1)
        #collabel=ectranslate(item1)
        collabel=colname
        ylabeltxt=''
        titletxt=ticker_name(ticker1,'stock')+": 财务指标历史"
        
        colmin=round(df1[colname].min(),2)
        colmax=round(df1[colname].max(),2)
        colmean=round(df1[colname].mean(),2)
        footnote=collabel+"："+ \
            str(colmin)+" - "+str(colmax)+ \
            "，均值"+str(colmean)+'\n'+footnote9
        plot_line(df1,colname,collabel,ylabeltxt,titletxt,footnote, \
                  datatag=datatag,power=power,zeroline=zeroline,resample_freq='1M')
        return df1,None

    #绘图：T1I2，单股票双折线
    if mode == 'T1I2':
        _,colname1=cvt_fin_rate(item1)
        label1=colname1
        _,colname2=cvt_fin_rate(item2)
        label2=colname2
        ylabeltxt=''
        titletxt="财务指标历史"

        colmin1=round(df1[colname1].min(),2)
        colmax1=round(df1[colname1].max(),2)
        colmean1=round(df1[colname1].mean(),2)
        colmin2=round(df2[colname2].min(),2)
        colmax2=round(df2[colname2].max(),2)
        colmean2=round(df2[colname2].mean(),2)
        footnote1=label1+"："+ \
            str(colmin1)+" - "+str(colmax1)+"，均值"+str(colmean1)
        footnote2=label2+"："+ \
            str(colmin2)+" - "+str(colmax2)+"，均值"+str(colmean2)
        footnote=footnote1+'\n'+footnote2+'\n'+footnote9
        
        plot_line2(df1,ticker1,colname1,label1, \
               df2,ticker1,colname2,label2, \
               ylabeltxt,titletxt,footnote, \
               power=power,zeroline=zeroline,twinx=twinx,resample_freq='1M')
        return df1,df2

    #绘图：T2I1，双股票双折线，单指标
    if mode == 'T2I1':
        _,colname1=cvt_fin_rate(item1)
        label1=colname1
        colname2=colname1
        label2=label1
        ylabeltxt=''
        titletxt="财务指标历史"

        colmin1=round(df1[colname1].min(),2)
        colmax1=round(df1[colname1].max(),2)
        colmean1=round(df1[colname1].mean(),2)
        colmin2=round(df2[colname2].min(),2)
        colmax2=round(df2[colname2].max(),2)
        colmean2=round(df2[colname2].mean(),2)
        footnote1=ticker_name(ticker1,'stock')+"："+ \
            str(colmin1)+" - "+str(colmax1)+"，均值"+str(colmean1)
        footnote2=ticker_name(ticker2,'stock')+"："+ \
            str(colmin2)+" - "+str(colmax2)+"，均值"+str(colmean2)
        footnote=footnote1+'\n'+footnote2+'\n'+footnote9
        
        plot_line2(df1,ticker1,colname1,label1, \
               df2,ticker2,colname2,label2, \
               ylabeltxt,titletxt,footnote, \
               power=power,zeroline=zeroline,twinx=twinx,resample_freq='1M')    
    
        return df1,df2    
    
if __name__ == '__main__':
    tickers=['600606.SS','000002.SZ']
    items=['Current Ratio','Quick Ratio']
    df1,df2=compare_history_china('600606.SS','Current Ratio','2020-1-1','2021-12-13',period_type='all')
    df1,df2=compare_history_china('600606.SS',items,'2020-1-1','2021-12-13',period_type='all')
    df1,df2=compare_history_china(tickers,'Current Ratio','2020-1-1','2021-12-13',period_type='all')
    
    df1,df2=compare_history_china(tickers,'?','2020-1-1','2021-12-13')
    
    rates=['Earnings Industry Share','Oper Revenue Industry Share']
    df1,df2=compare_history_china('600519.SS',rates,'2015-1-1','2021-12-13',period_type='annual')
    df1,df2=compare_history_china('600519.SS',rates,'2015-1-1','2021-12-13',period_type='semiannual')
    
    df1,df2=compare_history_china(['600519.SS','000858.SZ'],'Earnings Industry Share','2015-1-1','2021-12-13',period_type='annual')
    df1,df2=compare_history_china(['600519.SS','000858.SZ'],'Oper Revenue Industry Share','2015-1-1','2021-12-13',period_type='annual')

#==============================================================================
if __name__ == '__main__':
    tickers=['600519.SS','600606.SS','000002.SZ']
    itemk='ROE'
    endDate='latest'
    datatag=True
    tag_offset=0.01
    graph=True
    axisamp=1.3

def compare_snapshot_china(tickers,itemk,endDate='latest',datatag=True,tag_offset=0.01,graph=True,axisamp=1.3):
    """
    功能：比较多个股票的快照数据，绘制水平柱状图，仅限中国A股
    itemk需要通过对照表转换为内部的item
    datatag=True: 将数值标记在图形旁
    tag_offset=0.01：标记的数值距离图形的距离，若不理想可以手动调节，可为最大值1%-5%
    """
    error_flag=False
    
    #检查股票代码列表
    if not isinstance(tickers,list): 
        print("  #Warning(compare_snapshot_china): need more stock codes in",tickers)
        error_flag=True
    if len(tickers) < 2:
        print("  #Warning(compare_snapshot_china): need more stock codes in",tickers)
        error_flag=True
    if error_flag: return None
    
    #检查指标是否支持
    fin_rates,_=cvt_fin_rate('?',prompt=True,printout=False)
    rate_list=list(fin_rates['财务指标代码'])
    if not (itemk.lower() in rate_list):
        print("  #Warning(compare_snapshot_china): unsupported financial rate",itemk)
        error_flag=True
    if error_flag: return None

    #获取最近的报表日期
    if endDate == 'latest':
        import datetime; endDate=datetime.date.today()
    else:
        #检查日期
        valid_date=check_date(endDate)
        if not valid_date:
            error_flag=True
            print("  #Warning(compare_snapshot_china): invalid date",endDate)
    if error_flag: return None
    
    start=date_adjust(endDate, adjust=-365)
    fs_dates=cvt_fs_dates(start,endDate,'all')
    endDate=fs_dates[-1:][0]
    
    #依次获得各个股票的指标  
    rdf_list=prepare_fin_ratemt1r_china(tickers,itemk,endDate,endDate,period_type='all')
    #合成
    df=pd.DataFrame(columns=('ticker','item','value','name'))
    for rdf in rdf_list:
        cols=list(rdf)
        t=rdf['ticker'].values[0]
        item=cols[1]
        value=rdf[item].values[0]
        name=ticker_name(t,'stock')
        if name == t:
            name=rdf[cols[2]].values[0]
        row=pd.Series({'ticker':t,'item':item,'value':value,'name':name})
        try:
            df=df.append(row,ignore_index=True)
        except:
            df=df._append(row,ignore_index=True)
    
    if len(df) == 0:
        print("  #Error(compare_snapshot_china): stock info not found in",tickers)
        error_flag=True
    if error_flag: return None
    
    #处理小数点
    try:
        df['value']=round(df['value'],3)    
    except:
        pass
    df.sort_values(by='value',ascending=False,inplace=True)
    df['key']=df['name']
    df.set_index('key',inplace=True)    
    
    #绘图
    if graph:
        print("...Calculating and drawing graph, please wait ...")
        colname='value'
        titletxt="企业横向对比: 业绩指标快照"
        import datetime; today=datetime.date.today()
        footnote=item+" -->"+ \
            "\n报表截止日期："+endDate+ \
            "\n数据来源: sina/EM, "+str(today)
        plot_barh(df,colname,titletxt,footnote,datatag=datatag,tag_offset=tag_offset,axisamp=axisamp)
    
    return df

if __name__ == '__main__':
    df=compare_snapshot(tickers,itemk)

#==============================================================================
if __name__ == '__main__':
    tickers=['600519.SS','600606.SS','000002.SZ']
    endDate='latest'
    graph=True
    axisamp=7
    
def compare_tax_china(tickers,endDate='latest',datatag=True,tag_offset=0.01,graph=True,axisamp=1.3):
    """
    功能：比较公司最新的实际所得税率
    """
    error_flag=False
    
    #检查股票代码列表
    if not isinstance(tickers,list): 
        print("  #Warning(compare_tax_china): need more stock codes in",tickers)
        error_flag=True
    if len(tickers) < 2:
        print("  #Warning(compare_tax_china): need more stock codes in",tickers)
        error_flag=True
    if error_flag: return None

    #获取最近的报表日期
    if endDate == 'latest':
        import datetime; endDate=datetime.date.today()
    else:
        #检查日期
        valid_date=check_date(endDate)
        if not valid_date:
            error_flag=True
            print("  #Warning(compare_tax_china): invalid date",endDate)
    if error_flag: return None
    
    start=date_adjust(endDate, adjust=-365)
    fs_dates=cvt_fs_dates(start,endDate,'all')
    endDate=fs_dates[-1:][0]
    
    #获取实际所得税率
    df=pd.DataFrame(columns=('ticker','name','date','tax rate%'))
    for t in tickers:
        try:
            df0=prepare_hamada_ak(t,endDate,endDate,period_type='all')
        except:
            print("  #Error(compare_tax_china): failed to get financial info for",t)
            continue
        df1=df0.tail(1)
        name=ticker_name(t,'stock')
        reportdate=df1.index[0]
        taxrate=df1['tax rate'][0]
        row=pd.Series({'ticker':t,'name':name,'date':reportdate,'tax rate%':round(taxrate*100,2)})
        try:
            df=df.append(row,ignore_index=True)
        except:
            df=df._append(row,ignore_index=True)
    
    df.sort_values(by='tax rate%',ascending=False,inplace=True)
    df['key']=df['name']
    df.set_index('key',inplace=True)      
    #绘图
    if graph:
        print("  Calculating and drawing graph, please wait ...")
        colname='tax rate%'
        titletxt="企业横向对比: 实际所得税率"
        import datetime; today=datetime.date.today()
        itemk="实际所得税率%"
        footnote=ectranslate(itemk)+" -->"+ \
            "\n报表截止日期："+endDate+ \
            "\n数据来源: sina/EM, "+str(today)
        plot_barh(df,colname,titletxt,footnote,datatag=datatag,tag_offset=tag_offset,axisamp=axisamp)
    return df


#==============================================================================
if __name__ == '__main__':
    ticker='600519.SS'
    endDate='2021-09-30'

def calc_igr_sgr_china(ticker,endDate):

    rates=['ROE','ROA','Payout Ratio']
    rdf_list=prepare_fin_rate1tmr_china(ticker,rates,endDate,endDate,period_type='all')
    if rdf_list is None: return None,None
    
    roe=rdf_list[0]['净资产收益率'].values[0]/100
    roa=rdf_list[1]['资产报酬率(%)'].values[0]/100
    try:
        b=1-rdf_list[2]['股息发放率(%)'].values[0]/100
    except:
        b=1-0

    igr=round(roa*b/(1-roa*b),4)
    sgr=round(roe*b/(1-roe*b),4)
    
    return igr,sgr


#==============================================================================
if __name__ == '__main__':
    tickers=['600519.SS','600606.SS','000002.SZ']
    endDate='latest'
    graph=True
    axisamp1=1.3
    axisamp2=1.6

def compare_igr_sgr_china(tickers,endDate='latest',graph=True,axisamp1=1.3,axisamp2=1.6):
    """
    功能：比较公司的IGR和SGR
    """
    error_flag=False
    
    #检查股票代码列表
    if not isinstance(tickers,list): 
        print("  #Warning(compare_igr_sgr_china): need more stock codes in",tickers)
        error_flag=True
    if len(tickers) < 2:
        print("  #Warning(compare_igr_sgr_china): need more stock codes in",tickers)
        error_flag=True
    if error_flag: return None

    #获取最近的报表日期
    if endDate == 'latest':
        import datetime; endDate=datetime.date.today()
    else:
        #检查日期
        valid_date=check_date(endDate)
        if not valid_date:
            error_flag=True
            print("  #Warning(compare_igr_sgr_china): invalid date",endDate)
    if error_flag: return None
    
    start=date_adjust(endDate, adjust=-365)
    fs_dates=cvt_fs_dates(start,endDate,'all')
    endDate=fs_dates[-1:][0]
    
    #逐个获取公司信息
    df=pd.DataFrame(columns=('ticker','name','date','IGR%','SGR%'))
    for t in tickers:
        try:
            igr,sgr=calc_igr_sgr_china(t,endDate)
        except:
            print("  #Warning(compare_igr_sgr_china): stock info not available for",t)
            continue
        if igr is None or sgr is None: 
            print("  #Warning(compare_igr_sgr_china): no stock info found for",t)
            continue
        name=ticker_name(t,'stock')
        row=pd.Series({'ticker':t,'name':name,'IGR%':round(igr*100,2),'SGR%':round(sgr*100,2)})
        try:
            df=df.append(row,ignore_index=True)
        except:
            df=df._append(row,ignore_index=True)
    
    #绘制IGR
    df.sort_values(by='IGR%',ascending=False,inplace=True)
    df['key']=df['name']
    df.set_index('key',inplace=True)      
    #绘图
    if graph:
        colname='IGR%'
        titletxt="企业横向对比: 内部增长潜力"
        import datetime; today=datetime.date.today()
        itemk="(不依赖外部融资的)内部增长率(IGR)%"
        footnote=ectranslate(itemk)+" -->"+ \
            "\n报表截止日期："+endDate+ \
            "\n数据来源: sina/EM, "+str(today)
        plot_barh(df,colname,titletxt,footnote,axisamp=axisamp1)   
    
    #绘制SGR
    df.sort_values(by='SGR%',ascending=False,inplace=True)
    df['key']=df['name']
    df.set_index('key',inplace=True)      
    #绘图
    if graph:
        print("...Calculating and drawing graph, please wait ...")
        colname='SGR%'
        titletxt="企业横向对比: 可持续增长潜力"
        import datetime; today=datetime.date.today()
        itemk="(不增加财务杠杆的)可持续增长率(SGR)%"
        footnote=ectranslate(itemk)+" -->"+ \
            "\n报表截止日期："+endDate+ \
            "\n数据来源: sina/EM, "+str(today)
        plot_barh(df,colname,titletxt,footnote,axisamp=axisamp2)         
    return df
#==============================================================================
if __name__=='__main__':
    ticker="600519.SS" 
    ticker="601398.SS"
    ticker='000002.SZ'
    
    fsdate='2022-12-31'
    
    g=dupont_decompose_china(ticker,fsdate)

def dupont_decompose_china(ticker,fsdate,gview=False,facecolor='papayawhip'):
    """
    功能：杜邦分析分解图
    ticker: 股票代码
    fsdate： 财报日期
    gview: False为嵌入式显示，True为分离式显示
    """
    #检查日期
    result,fspd,_=check_period(fsdate,fsdate)
    if not result:
        print("  #Error(dupont_decompose_china): invalid date",fsdate)
        return None
    
    #获取财报
    fs=get_fin_stmt_ak(ticker)
    if fs is None:
        print("  #Error(dupont_decompose_china): failed to access financial stmts for",ticker)
        return None
    
    fs1=fs[fs.index==fspd]
    if len(fs1)==0:
        print("  #Error(dupont_decompose_china): financial statements not found for",ticker,'@',fsdate)
        return None

    #亿元
    yi=100000000

    company_name=ticker_name(ticker,'stock')
    # 定义杜邦分解项目变量
    
    roe='【'+company_name+'】\n('+fsdate+')\n'+'净资产收益率'
    try:
        totalOEValue=round(fs1['所有者权益(或股东权益)合计'].values[0] / yi,1)
    except:
        try:
            totalOEValue=round(fs1['股东权益合计'].values[0] / yi,1)
        except:
            totalOEValue=round(fs1['所有者权益合计'].values[0] / yi,1)
        
    roa='总资产净利率'
    em='权益乘数'
    pm='销售净利率'
    tat='总资产周转率'
    
    debtRatio='资产负债率'
    totalLiabValue=round(fs1['负债合计'].values[0] / yi,1)
    
    netProfit='净利润'
    netProfitValue=round(fs1['净利润'].values[0] / yi,1)
    roePct=round(netProfitValue / totalOEValue *100,2)
    
    sales='销售收入'
    try:
        salesValue=round(fs1['营业总收入'].values[0] / yi,1)
    except:
        salesValue=round(fs1['营业收入'].values[0] / yi,1)
        
    pmPct=round(netProfitValue / salesValue *100,2)
    
    totalAssets='资产总额'
    totalAssetsValue=round(fs1['资产总计'].values[0] / yi,1)
    tatValue=round(salesValue / totalAssetsValue *100,2)
    emValue=round(totalAssetsValue / totalOEValue,2)
    debtRatioPct=round(totalLiabValue / totalAssetsValue *100,2)
    roaPct=round(netProfitValue / totalAssetsValue *100,2)
    
    totalCosts='成本费用'
    try:
        totalCostsValue=round(fs1['营业总成本'].values[0] / yi,1)
    except:
        totalCostsValue=round(fs1['营业支出'].values[0] / yi,1)
    
    currentAssets='流动资产'
    try:
        currentAssetsValue=round(fs1['流动资产合计'].values[0] / yi,1)
    except:
        try:
            currentAssetsValue=round((fs1['现金及存放中央银行款项'].values[0] \
                                    + fs1['存放同业款项'].values[0] \
                                    + fs1['拆出资金'].values[0] \
                                    + fs1['贵金属'].values[0] \
                                    + fs1['交易性金融资产'].values[0] \
                                    + fs1['衍生金融工具资产'].values[0] \
                                    + fs1['买入返售金融资产'].values[0] \
                                    + fs1['应收利息'].values[0] \
                                    )/ yi,1)
        except:
            currentAssetsValue=round((fs1['货币资金'].values[0] \
                                    + fs1['拆出资金'].values[0] \
                                    + fs1['交易性金融资产'].values[0] \
                                    + fs1['衍生金融资产'].values[0] \
                                    + fs1['买入返售金融资产'].values[0] \
                                    + fs1['应收保费'].values[0] \
                                    + fs1['应收利息'].values[0] \
                                    + fs1['应收分保账款'].values[0] \
                                    + fs1['应收分保未到期责任准备金'].values[0] \
                                    + fs1['应收分保未决赔款准备金'].values[0] \
                                    + fs1['应收分保寿险责任准备金'].values[0] \
                                    + fs1['应收分保长期健康险责任准备金'].values[0] \
                                    )/ yi,1)
        
    LTAssets='非流动资产'
    try:
        LTAssetsValue=round(fs1['非流动资产合计'].values[0] / yi,1)
    except:
        try:
            LTAssetsValue=round((fs1['发放贷款及垫款'].values[0] \
                               + fs1['代理业务资产'].values[0] \
                               + fs1['可供出售金融资产'].values[0] \
                               + fs1['持有至到期投资'].values[0] \
                               + fs1['长期股权投资'].values[0] \
                               + fs1['应收投资款项'].values[0] \
                               + fs1['固定资产合计'].values[0] \
                               + fs1['无形资产'].values[0] \
                               + fs1['商誉'].values[0] \
                               + fs1['递延税款借项'].values[0] \
                               + fs1['投资性房地产'].values[0] \
                               + fs1['其他资产'].values[0] \
                                    )/ yi,1)
        except:
            LTAssetsValue=round((fs1['保户质押贷款'].values[0] \
                               + fs1['存出资本保证金'].values[0] \
                               + fs1['可供出售金融资产'].values[0] \
                               + fs1['持有至到期投资'].values[0] \
                               + fs1['长期股权投资'].values[0] \
                               + fs1['应收款项类投资'].values[0] \
                               + fs1['固定资产'].values[0] \
                               + fs1['无形资产'].values[0] \
                               + fs1['商誉'].values[0] \
                               + fs1['独立账户资产'].values[0] \
                               + fs1['递延所得税资产'].values[0] \
                               + fs1['投资性房地产'].values[0] \
                               + fs1['定期存款'].values[0] \
                               + fs1['其他资产'].values[0] \
                                    )/ yi,1)
            
    salesCosts='营业\\n成本'
    try:
        salesCostsValue=round(fs1['营业成本'].values[0] / yi,1)
    except:
        salesCostsValue=round(fs1['营业支出'].values[0] / yi,1)
    
    periodExpenses='期间\\n费用'
    salesExpenses='销售\\n费用'
    try:
        salesExpensesValue=round(fs1['销售费用'].values[0] / yi,1)
    except:
        salesExpensesValue=0.0
    
    mgmtExpenses='管理\\n费用'
    try:
        mgmtExpensesValue=round(fs1['管理费用'].values[0] / yi,1)
    except:
        mgmtExpensesValue=round(fs1['业务及管理费用'].values[0] / yi,1)
    
    rndExpenses='研发\\n费用'
    rndExpensesValue=round(fs1['研发费用'].values[0] / yi,1)
    """
    #是否中国股票
    result,prefix,suffix=split_prefix_suffix(ticker)
    if not (suffix in SUFFIX_LIST_CN):
        print("  #Error(dupont_decompose_china): not a stock in China",ticker)
        return None        
    
    #财务报告摘要
    try:
        fsabs = ak.stock_financial_abstract(prefix)
    except:
        print("  #Warning(dupont_decompose_china): financial summary not found for",ticker)
        return None
    """
    financialExpenses='财务\\n费用'
    try:
        financialExpensesValue=round((fs1['财务费用'].values[0])/ yi,1)
    except:
        financialExpensesValue=round(fs1['应付利息'].values[0] / yi,1)
    
    taxExpenses='税金'
    try:
        taxExpensesValue=round((fs1['营业税金及附加'].values[0] + fs1['所得税费用'].values[0]) / yi,1)
    except:
        try:
            taxExpensesValue=round((fs1['营业税金及附加'].values[0] + fs1['减:所得税'].values[0]) / yi,1)
        except:
            taxExpensesValue=round((fs1['营业税金及附加'].values[0] + fs1['减:所得税费用'].values[0]) / yi,1)
        
    """
    otherExpenses='其他支出'
    otherExpensesVaue=round((fs1['开发支出'].values[0] + fs1['减：营业外支出'].values[0]) / yi,1)
    """
    monetaryFunds='货币\\n资金'
    try:
        monetaryFundsValue=round(fs1['货币资金'].values[0] / yi,1)
    except:
        monetaryFundsValue=round(fs1['现金及存放中央银行款项'].values[0] / yi,1)
    
    securityAssets='金融\\n资产'
    try:
        securityAssetsValue=round((fs1['交易性金融资产'].values[0] + \
                                   fs1['衍生金融资产'].values[0] + \
                                   fs1['买入返售金融资产'].values[0]) / yi,1)
    except:
        securityAssetsValue=round((fs1['交易性金融资产'].values[0] + \
                                   fs1['衍生金融工具资产'].values[0] + \
                                   fs1['买入返售金融资产'].values[0]) / yi,1)
        
    ar_prepaid='应收\\n与\\n预付'
    accountReceivables='应收\\n款项'
    try:
        accountReceivablesValue=round((fs1['应收票据及应收账款'].values[0] + fs1['其他应收款(合计)'].values[0]) / yi,1)  
    except:
        try:
            accountReceivablesValue=round((fs1['应收保费'].values[0] + \
                                           fs1['应收利息'].values[0] + \
                                           fs1['应收分保账款'].values[0] + \
                                           fs1['应收分保未到期责任准备金'].values[0] + \
                                           fs1['应收分保未决赔款准备金'].values[0] + \
                                           fs1['应收分保寿险责任准备金'].values[0] + \
                                           fs1['应收分保长期健康险责任准备金'].values[0]) / yi,1)
        except:    
            accountReceivablesValue=round((fs1['应收利息'].values[0] + \
                                           fs1['应收投资款项'].values[0]) / yi,1)
    
    prepaid='预付\\n款项'
    try:
        prepaidValue=round(fs1['预付款项'].values[0] / yi,1)
    except:
        prepaidValue=0.0
    
    inventory='存货'
    try:
        inventoryValue=round(fs1['存货'].values[0] / yi,1)
    except:
        inventoryValue=0.0
    
    otherCurrentAssets='其他\\n流动\\n资产'
    try:
        otherCurrentAssetsValue=round(fs1['其他流动资产'].values[0] / yi,1)
    except:
        otherCurrentAssetsValue=0.0
    
    fixedAssets='固定\\n资产'
    try:
        fixedAssetsValue=round(fs1['固定资产及清理合计'].values[0] / yi,1)
    except:
        try:
            fixedAssetsValue=round(fs1['固定资产合计'].values[0] / yi,1)
        except:
            fixedAssetsValue=round(fs1['固定资产'].values[0] / yi,1)
    
    LTInvestment='长期\\n投资'
    try:
        LTInvestmentValue=round((fs1['发放贷款及垫款'].values[0] + \
                            fs1['可供出售金融资产'].values[0] + \
                            fs1['持有至到期投资'].values[0] + \
                           #fs1['长期应收款'].values[0] + \
                            fs1['长期股权投资'].values[0] + \
                            fs1['投资性房地产'].values[0] + \
                            fs1['在建工程(合计)'].values[0]) / yi,1)
    except:
        try:
            LTInvestmentValue=round((fs1['发放贷款及垫款'].values[0] + \
                                fs1['可供出售金融资产'].values[0] + \
                               #fs1['持有至到期投资'].values[0] + \
                               #fs1['长期应收款'].values[0] + \
                                fs1['长期股权投资'].values[0] + \
                                fs1['投资性房地产'].values[0]) / yi,1)
        except:
            LTInvestmentValue=round((#fs1['保户质押贷款'].values[0] + \
                                     fs1['可供出售金融资产'].values[0] + \
                                    #fs1['持有至到期投资'].values[0] + \
                                     fs1['长期股权投资'].values[0] + \
                                     fs1['投资性房地产'].values[0]) / yi,1)
            
    intangibleAssets='无形\\n资产'
    intangibleAssetsValue=round(fs1['无形资产'].values[0] / yi,1)
    
    deferredAssets='递延\\n资产'
    try:
        deferredAssetsValue=round(fs1['递延所得税资产'].values[0] / yi,1)
    except:
        deferredAssetsValue=round(fs1['递延税款借项'].values[0] / yi,1)
    
    goodwill='商誉'
    goodwillValue=round(fs1['商誉'].values[0] / yi,1)

    #合成具体的分解项目
    roe=roe+'\n'+str(roePct)+'%'
    roa=roa+'\n'+str(roaPct)+'%'
    em=em+'\n'+str(emValue)
    pm=pm+'\n'+str(pmPct)+'%'
    tat=tat+'\n'+str(tatValue)

    netProfit=netProfit+'\n'+str(netProfitValue)
    totalAssets=totalAssets+'\n'+str(totalAssetsValue)
    totalCosts=totalCosts+'\n'+str(totalCostsValue)
    sales=sales+'\n'+str(salesValue)
    currentAssets=currentAssets+'\n'+str(currentAssetsValue)
    LTAssets=LTAssets+'\n'+str(LTAssetsValue)
    
    salesCosts=salesCosts+'\n'+str(salesCostsValue)
    taxExpenses=taxExpenses+'\n'+str(taxExpensesValue)
    
    salesExpenses=salesExpenses+'\n'+str(salesExpensesValue)
    mgmtExpenses=mgmtExpenses+'\n'+str(mgmtExpensesValue)
    financialExpenses=financialExpenses+'\n'+str(financialExpensesValue)
    rndExpenses=rndExpenses+'\n'+str(rndExpensesValue)

    monetaryFunds=monetaryFunds+'\n'+str(monetaryFundsValue)
    securityAssets=securityAssets+'\n'+str(securityAssetsValue)
    accountReceivables=accountReceivables+'\n'+str(accountReceivablesValue)
    prepaid=prepaid+'\n'+str(prepaidValue)
    inventory=inventory+'\n'+str(inventoryValue)

    fixedAssets=fixedAssets+'\n'+str(fixedAssetsValue)
    LTInvestment=LTInvestment+'\n'+str(LTInvestmentValue)
    intangibleAssets=intangibleAssets+'\n'+str(intangibleAssetsValue)

    #下面字段：“序号”、“父单位”、“父单位层级”、“子单位”、“子单位层级”、“父单位持股比例”
    #注意：最后面的空格字段为必须，否则显示顺序不受控
    L=[
        [1, roe, 1, roa, 2, ' '],
        [2, roe, 1, em, 2, ' '],
        [3, roa, 2, pm, 3, ' '],
        [4, roa, 2, tat, 3, ' '],
        [5, pm, 3, netProfit, 4, ' '],
        [6, pm, 3, sales, 4, ' '],
        [7, netProfit, 4, sales, 5, ' '],
        [8, netProfit, 4, totalCosts, 5, ' '],
        [9, totalCosts, 5, salesCosts, 6, ' '],
        
        [10, totalCosts, 5, periodExpenses, 6, ' '],
        [11, periodExpenses, 6, salesExpenses, 7, ' '],
        [12, periodExpenses, 6, mgmtExpenses, 7, ' '],
        [13, periodExpenses, 6, financialExpenses, 7, ' '],
        [14, periodExpenses, 6, rndExpenses, 7, ' '],
        
        [15, totalCosts, 5, taxExpenses, 6, ' '],
        
        [16, tat, 3, sales, 4, ' '],
        [17, tat, 3, totalAssets, 4, ' '],
        [18, totalAssets, 4, currentAssets, 5, ' '],
        [19, totalAssets, 4, LTAssets, 5, ' '],
        
        [20, currentAssets, 5, monetaryFunds, 6, ' '],
        [21, currentAssets, 5, securityAssets, 6, ' '],
        
        [22, currentAssets, 5, ar_prepaid, 6, ' '],
        [23, ar_prepaid, 6, accountReceivables, 7, ' '],        
        [24, ar_prepaid, 6, prepaid, 7, ' '],
        
        [25, currentAssets, 5, inventory, 10, ' '],
       #[26, currentAssets, 5, otherCurrentAssets, 11, ' '],
        
        [27, LTAssets, 5, fixedAssets, 6, ' '],
        [28, LTAssets, 5, LTInvestment, 6, ' '],
        [29, LTAssets, 5, intangibleAssets, 6, ' '],
       #[30, LTAssets, 5, deferredAssets, 6, ' '],
       #[31, LTAssets, 5, goodwill, 6, ' '],
        
    ]    
    
    dic={}
    father_name_list=[]
    child_name_list=[]
    equity_portion_list=[]
    for i1 in range(len(L)):
        
        M=L[i1]
        father_name=M[1]
        try:
            father_name_list.append(M[1])
            father_layer=M[2]
            child_name=M[3]
            child_name_list.append(M[3])
            child_layer=M[4]
            equity_portion=M[5]
            equity_portion_list.append(M[5])
        except:
            father_name_list._append(M[1])
            father_layer=M[2]
            child_name=M[3]
            child_name_list._append(M[3])
            child_layer=M[4]
            equity_portion=M[5]
            equity_portion_list._append(M[5])
        
        #debug使用
        #print(i1,M,father_name,father_layer,child_name,child_layer,equity_portion)
        
        for x in father_name:
            dic[father_name]=father_layer   #生成父单位名称和对应的层级（用字典考虑去重）
        
        for y in child_name:
            dic[child_name]=child_layer     #将子单位名称和对应的层级也添加到字典中
            
    name_layer_list = sorted(dic.items(), key=lambda x: x[1]) #对字典按值（value）进行排序（默认由小到大）
    
    u=[]
    for z in name_layer_list:
        company_name=z[0]
        layer=z[1]
        try:
            u.append(z[1])
        except:
            u._append(z[1])
    number_of_layers=max(u) #计算出层数
    
    from graphviz import Digraph
    #按各公司的层数生产分层的节点：
    g=Digraph(name=ticker_name(ticker,'stock')+fsdate)
    
    for key in dic:
        for n in range(number_of_layers+1):
            if dic[key]==n:
                with g.subgraph() as layer_n:
                    layer_n.attr(rank='same')
                    layer_n.node(name=key,color='blue',shape='box', \
                                 fontname='Microsoft YaHei',fontsize='11', \
                                     nodesranksep='0.5',nodesnodesep='0.5')
    
    #生产各节点间的连线：
    for i2 in range(len(L)):
        g.edge(father_name_list[i2],child_name_list[i2],label=equity_portion_list[i2], \
               color='red',fontname='Microsoft Yahei',edgeweight='1.0',fontsize='11')
    
    if gview:
        # 分离式显示，便于多图对比
        g.view()  
    else:
        # 嵌入式显示
        display(g)
    
    #打印信息
    if not gview:
        print("\n注:",ticker_name(ticker,'stock'),"\b，金额单位：亿元，财报日期:",fsdate)
        print("1、为避免图示过大，这里未列出所有分解项目")
        print("2、金融机构报表与普通企业结构不同，此处仅为约算")
        print("3、应收款项包括应收账款、应收利息、应收保费以及应收票据等")
        print("4、递延资产为递延所得税资产或借项")
        print("5、税金包括营业税金及附加以及所得税费用")
        print("6、此处金融资产主要为交易性金融资产、衍生金融资产和买入返售金融资产")
        print("7、此处长期投资包括贷款及垫款、可供出售金融资产、持有至到期投资、长期股权投资、投资性房地产等")
        print("8、注意：图中比率和比值均为基于财报期末数值直接计算，并非基于期初期末均值，可能与公告数字存在差异。")

    return g

if __name__=='__main__':
    ticker="600519.SS" 
    fsdate='2022-12-31'
    
    g=dupont_decompose_china(ticker,fsdate)

#==============================================================================
if __name__=='__main__':
    tickers=['000002.SZ','601398.SS']
    fsdates=['2022-12-31','2021-12-31']
    

def get_fin_summary_china_original(tickers,fsdates):
    """
    功能：获得A股财报摘要，进行数据整理
    输出：
    1、项目列表：不带(元)、(次)、(%)等后缀括弧
    2、数量级变换：(元)-->(亿元)，并相应修改字段名
    
    废弃！
    """

    import pandas as pd
    df=pd.DataFrame()
    # 获得股票
    for t in tickers:
        _,t1,_=split_prefix_suffix(t)
        dft=ak.stock_financial_abstract(t1)
        
        dft['ticker']=t
        
        if len(df)==0:
            df=dft
        else:
            df=pd.concat([df,dft])

    # 遍历
    collist=list(df)
    colremove=['选项','指标','ticker']
    for cr in colremove:
        collist.remove(cr)
    noamtlist=["率","每股","周转","乘数",'/']
    yiyuan=100000000
    
    for index,row in df.iterrows():
        #print(index,row)
        # 金额变为亿元，不含"率"、"每股"、"周转"、"乘数"

        if '率' in row['指标']:
            if not ('周转率' in row['指标']):
                df.at[index,'指标']=row['指标']+'(%)'
                for d in collist:
                    df.at[index,d] = round(row[d],2)
                continue
            
        if '/' in row['指标']:
            df.at[index,'指标']=row['指标']+'(%)'
            for d in collist:
                df.at[index,d] = round(row[d],2)
            continue
        
        if '每股' in row['指标']:
            df.at[index,d] = round(row[d],2)
            continue
     
        # 元变换为亿元
        for d in collist:
            df.at[index,d] = round(row[d] / yiyuan,1)
            df.at[index,'指标']=row['指标']+'(亿元)'
    
    # 填充nan为零
    df.fillna('-',inplace=True)

    # 改变日期格式
    for c in collist:
        try:
            c1=pd.to_datetime(c)
            c2=c1.strftime("%Y-%m-%d")
        except:
            continue
        df.rename(columns={c:c2},inplace=True)
        
    # 过滤财报日期
    fsdates2=[]
    for d in fsdates:
        d1=pd.to_datetime(d)
        d2=d1.strftime("%Y-%m-%d")
        fsdates2=fsdates2 + [d2]
        
    collistnew=colremove+fsdates2
    fsdf=df[collistnew]
    
    return fsdf

#==============================================================================
if __name__=='__main__':
    astr='存货周转天数'
    substrlist=['乘数','每股','/','周转']
    str_contain_any_substr(astr,substrlist)


def str_contain_any_substr(astr,substrlist):
    """
    功能：判断astr是否含有子串列表substrlist之一
    """
    result=False
    for sub in substrlist:
        if sub in astr:
            result=True
            
    return result

#==============================================================================
if __name__=='__main__':
    ticker='600305.SS'
    fsdates=['2023-6-30','2022-6-30','2021-6-30']
    
    ticker='002352.SZ'
    fsdates=['2024-12-31','2023-12-31','2022-12-31']
    
    fsdf1=get_fin_summary_1ticker_china(ticker,fsdates)

def get_fin_summary_1ticker_china(ticker,fsdates):
    """
    功能：获得A股财报摘要，进行数据整理，单一股票
    输出：
    1、数量级变换：(元)-->(亿元)，并相应修改字段名
    """

    import pandas as pd
    # 过滤财报日期
    fsdates2=[]
    for d in fsdates:
        d1=pd.to_datetime(d)
        d2=d1.strftime("%Y-%m-%d")
        fsdates2=fsdates2 + [d2]
    fsdates3=sorted(fsdates2,reverse=True)
    
    yiyuan=float(1e+08)
    
    # 获得股票所有财报数据
    print("  Retrieving financial abstract of",ticker,'... ...')
    _,t1,_=split_prefix_suffix(ticker)
    dft=ak.stock_financial_abstract(t1)
    
    #akshare错误更正：此处的“营业成本”其实为“营业总成本”
    if ("营业成本" in list(dft['指标'])) and not ("营业总成本" in list(dft['指标'])):
        dft.loc[dft['指标']=="营业成本","指标"]="营业总成本"
        
    # 处理金额单位和百分号字段
    # 选项-指标对照表
    option_indicator_df=dft[['选项','指标']]
    option_indicator_df.set_index('指标',inplace=True)
    
    # 变换日期格式为YYYY-MM-DD
    collist=list(dft)
    for c in collist:
        try:
            c1=pd.to_datetime(c)
            c2=c1.strftime("%Y-%m-%d")
        except:
            continue
        dft.rename(columns={c:c2},inplace=True)
    
    # 过滤财报日期    
    try:
        dft2=dft[['选项','指标']+fsdates3]
    except:
        print("  #Warning(get_fin_summary_1ticker_china): fin stmt of",fsdates3[0],"unavailable for",ticker+'('+ticker_name(ticker,'stock')+')')
        return None
    
    # 金额变换：元-->亿元，小数位截取
    dft2=dft2.drop(labels=['选项'],axis=1)
    # 去掉重复行，非常重要！！！
    dft2b=dft2.drop_duplicates (keep='first')
    
    dft2b.set_index('指标',inplace=True)
    
    dft2t=dft2b.T
    
    noneamtlist=['乘数','每股','/','周转','率','天数']
    collist2=list(dft2t)
    
    for c in collist2:
        
        if not str_contain_any_substr(c,noneamtlist):
            dft2t[c]=dft2t[c] / yiyuan
        
        if ('/' in c) and ('现金' in c):
            dft2t[c]=dft2t[c] * 100.0
        
        dft2t[c]=dft2t[c].apply(lambda x: round(x,2))    
        
    # 标记字段后缀
    dft3=dft2t.T
    dft3['指标2']=dft3.index
    dft3t=dft3.T
    collist3=list(dft3t)
    for c in collist3:
        # 判断顺序不可颠倒
        if str_contain_any_substr(c,['乘数','周转']):
            continue
        if str_contain_any_substr(c,['率']):
            dft3t.rename(columns={c:c+'%'},inplace=True)
            continue
        if str_contain_any_substr(c,['每股']):
            dft3t.rename(columns={c:c+'(元)'},inplace=True)
            continue
        if str_contain_any_substr(c,['/']):
            dft3t.rename(columns={c:c+'(%)'},inplace=True)
            continue
    
        # 其余的字段：元变换为亿元
        dft3t.rename(columns={c:c+'(亿元)'},inplace=True)
        
    # 检查字段改名情况
    collist3t=list(dft3t)
    
    # 回填指标选项类型
    dft4=dft3t.T
    dft5=dft4.reset_index()
    dft5.set_index('指标2',inplace=True)
    dft6=dft5.merge(option_indicator_df,how='left',left_index=True, right_index=True) 
     
    dft7=dft6.reset_index(drop=True) 
     
    dft7['ticker']=ticker
        
    # 填充nan为零
    dft7.fillna('-',inplace=True)
    
    return dft7

#==============================================================================
if __name__=='__main__':
    tickers=['000002.SZ','601398.SS']
    fsdates=['2022-12-31','2021-12-31','2020-12-31']
    
    fsdfm=get_fin_summary_china(tickers,fsdates)
    

def get_fin_summary_china(tickers,fsdates):
    """
    功能：获得A股财报摘要，进行数据整理
    输出：
    1、数量级变换：(元)-->(亿元)，并相应修改字段名
    """

    import pandas as pd
    # 过滤财报日期
    fsdates2=[]
    for d in fsdates:
        d1=pd.to_datetime(d)
        d2=d1.strftime("%Y-%m-%d")
        fsdates2=fsdates2 + [d2]
    fsdates3=list(set(fsdates2))
    fsdates4=sorted(fsdates3,reverse=True)
    
    df=pd.DataFrame()
    
    # 获得多只股票财报
    for t in tickers:
        # 抓取一只股票的财报
        dft=get_fin_summary_1ticker_china(t,fsdates4)
        if dft is None: 
            continue
        
        if len(df)==0:
            df=dft
        else:
            df=pd.concat([df,dft])
    
    return df

if __name__=='__main__':
    tickers=['000002.SZ','601398.SS']
    fsdates=['2022-12-31','2021-12-31','2020-12-31']

    tickers='000002.SZ'
    fsdates=['2022-12-31','2021-12-31','2020-12-31']   
    
    tickers=['000002.SZ','600048.SS','001979.SZ','600325.SS','000069.SZ','600383.SS','600895.SS','601155.SS']
    fsdates='2022-12-31'
    
    tickers=['002373.SZ', '002279.SZ', '002368.SZ', '600410.SS', '603927.SS', '002405.SS']
    fsdates='2023-12-31'
    
    
def compare_fin_summary_china(tickers,fsdates,facecolor='whitesmoke',font_size='16px'):
    """
    功能：分类别显示财报摘要中的指标
    """  
    DEBUG=False      
    
    # 检查股票列表
    if isinstance(tickers,str):
        tickers=[tickers]
    tickers=list(tickers) #强制转换
    if len(tickers)==0:
        print("  #Error(compare_fin_summary_china): need at least one stock in",tickers)
        return None
    
    # 检查财报日期列表
    if isinstance(fsdates,str):
        fsdates=[fsdates]
    if len(fsdates)==0:
        print("  #Error(compare_fin_summary_china): need at least one date in",fsdates)
        return None
    
    for d in fsdates:
        result,_,_=check_period(d,d)
        if not result:
            print("  #Error(compare_fin_summary_china): invalid date",d)
            return None
        
    # 获取财报数据
    print("Searching for financial statements, please wait ...")
    fsdf=get_fin_summary_china(tickers,fsdates)
    
    # 不改变列表顺序去重
    tickerlist=list(fsdf['ticker'])
    tickers_found=sorted(list(set(tickerlist)),key=tickerlist.index)
    
    #optionlist=list(fsdf['选项'])
    #typelist=sorted(list(set(optionlist)),key=optionlist.index)
    typelist=['常用指标','每股指标','营运能力','盈利能力','收益质量','成长能力','财务风险']
    # 手工设定项目显示顺序，使其看起来更合理
    typedict={'常用指标':
              ['营业总收入(亿元)','营业总成本(亿元)',
               '净利润(亿元)','扣非净利润(亿元)','归母净利润(亿元)',
               '毛利率%','销售净利率%','期间费用率%',  
               '基本每股收益(元)','总资产报酬率(ROA)%','净资产收益率(ROE)%', 
               '经营现金流量净额(亿元)','每股现金流(元)',
               '股东权益合计(净资产)(亿元)','每股净资产(元)',
               '资产负债率%','商誉(亿元)',],
              
              '每股指标':
              ['每股营业总收入(元)',#'每股营业收入(元)',
               '每股息税前利润(元)','基本每股收益(元)','稀释每股收益(元)',
               '每股净资产_最新股数(元)','摊薄每股净资产_期末股数(元)','调整每股净资产_期末股数(元)', 
               '每股未分配利润(元)','每股留存收益(元)','每股盈余公积金(元)','每股资本公积金(元)',
               '每股现金流量净额(元)','每股经营现金流(元)','每股企业自由现金流量(元)','每股股东自由现金流量(元)',],
              
              '营运能力':
              ['总资产周转率','总资产周转天数',
               '流动资产周转天数','流动资产周转率', 
               '存货周转率','存货周转天数',
               '应收账款周转率','应收账款周转天数','应付账款周转率',],
              
              '盈利能力': 
              ['毛利率%','营业利润率%','息税前利润率%','销售净利率%','成本费用利润率%',
              '总资产净利率_平均%','总资产净利率_平均(含少数股东损益)%', 
              '总资产报酬率%', '总资本回报率%','息前税后总资产报酬率_平均%', 
              '净资产收益率(ROE)%','净资产收益率_平均%','净资产收益率_平均_扣除非经常损益%', 
              '摊薄净资产收益率%','摊薄净资产收益率_扣除非经常损益%', 
              '投入资本回报率%',],
              
              '收益质量':
              ['销售成本率%','成本费用率%','期间费用率%','所得税/利润总额(%)',
               '经营性现金净流量/营业总收入(%)','经营活动净现金/销售收入(%)', 
               '经营活动净现金/归属母公司的净利润(%)',], 
              
              '成长能力':
              ['营业总收入(亿元)','营业总收入增长率%',
               '净利润(亿元)','扣非净利润(亿元)', 
               '归母净利润(亿元)','归属母公司净利润增长率%',],
              
              '财务风险':
              ['流动比率%','速动比率%','保守速动比率%','现金比率%','资产负债率%',
               '权益乘数','权益乘数(含少数股权的净资产)','产权比率%',],
              }

    # 注释
    notesdict={'常用指标': \
               '注：\n'+ \
               '毛利率=毛利润 / 营业(总)收入 ×100% \n'+ \
               '毛利润=营业(总)收入-营业(总)成本 \n'+ \
               '销售净利率=净利润 / 营业(总)收入 ×100% \n'+ \
               '期间费用率=期间费用 / 营业(总)收入 ×100%，期间费用包括管理费用，销售费用和财务费用。 \n', \
              
              '每股指标': \
               '注：\n'+ \
               '稀释每股指标:假设企业所有发行在外的稀释性潜在普通股期间内均转换为普通股，导致普通股股数增加 \n'+ \
               '潜在普通股：赋予其持有者在报告期或以后享有取得普通股权利的金融工具或者其他合同，如可转债、认股权证、股份期权等 \n'+ \
               '摊薄每股指标：使用期末数值计算，而非期初期末均值，其结果更能反应期末情况，可能大于、小于或等于每股指标 \n'+ \
               '调整后每股净资产的意义：考虑了净资产的流动性和变现能力，更加具有谨慎性或稳健性 \n'+ \
               '调整后每股净资产=（年度末股东权益-三年以上的应收款项净额-待摊费用-长期待摊费用）/年度末普通股股份总数 \n'+ \
               '应收款项净额：包括应收帐款、其他应收款、预付帐款、应收股利、应收利息、应收补贴款 \n'+ \
               '留存收益：指企业从历年实现的利润中提取或形成的留存于企业的内部积累，包括盈余公积和未分配利润两类 \n'+ \
               '盈余公积：指从税后利润中提取的、存留于企业内部、具有特定用途的收益积累，包括法定盈余公积和任意盈余公积 \n'+ \
               '盈余公积的用途：可用于企业职工福利设施的支出、弥补亏损、扩大生产经营、转增资本（或股本）或派送新股等 \n'+ \
               '法定盈余公积：指企业按照公司法等法律规定的比例(例如10%)从净利润中提取的盈余公积 \n'+ \
               '任意盈余公积：指企业经股东大会或类似机构批准按照规定的比例从净利润中提取的盈余公积，其提取比例由企业自行确定 \n'+ \
               '未分配利润：指企业实现的净利润经过弥补亏损、提取盈余公积和向投资者分配利润后留存在企业的、历年结存的利润 \n'+ \
               '资本公积金：指由资本原因形成的公积金，如发行股份溢价、资产重估增值、接受捐赠等，用于转增股本，不得用于弥补亏损 \n'+ \
               '自由现金流=企业经营活动现金流-资本性支出，用来衡量实际持有的在不影响企业生存时可回报股东(债权人）的最大现金额 \n'+ \
               '(企业)自由现金流可以理解为归属于股东与债权人的最大现金流，而股东(股权)自由现金流则是归属于股东的最大现金流。 \n', \

              '营运能力': \
               '注：\n'+ \
               '指标周转率/周转次数：营业(总)收入 / 指标的起初期末均值。一般来说数值越大越好 \n'+ \
               '指标周转天数：360/周转率(或周转次数)。一般来说数值越小越好 \n'+ \
               '注意：本表指标主要针对非金融行业，部分指标不适用于金融行业。 \n', \
              
              '盈利能力': 
               '注：\n'+ \
               '毛利润=营业(总)收入-营业(总)成本 \n'+ \
               '营业利润=毛利润-营业税金及附加-期间费用-资产减值损失+公允价值变动损益+投资损益 \n'+ \
               '营业利润率=营业利润 / 营业(总)收入 x100% \n'+ \
               '营业利润率的意义：不考虑营业外收支和所得税费用时，反映主营业务创造利润能力，比毛利率更能反映盈利能力 \n'+ \
               '成本费用利润率=利润总额 / 成本费用总额 ×100%，反映付出一单位成本可以获取多少利润，即获取利润的效率 \n'+ \
               '利润总额=营业利润+营业外收入-营业外支出 \n'+ \
               '成本费用总额=营业成本+营业税金及附加+期间费用+资产减值损失 \n'+ \
               '总资产净利率：这里默认使用总资产期初期末平均值，=净利润 / 总资产期初期末平均值 \n'+ \
               '总资产净利率_平均(含少数股东损益)：即在扣除少数股东损益之前的总资产净利率 \n'+ \
               '少数股东损益：指公司合并报表的子公司中其它非控股股东享有的损益 \n'+ \
               '总资产报酬率=息税前利润 / 总资产期初期末均值 ×100%，即（利润总额+利息支出） / 平均总资产 ×100% \n'+ \
               '总资本回报率(收益率)（Return of Total Capital）=(利润总额+借入资本利息) / 总资本 x100%， \n'+ \
               '总资本回报率(收益率)反映企业总资本的收益能力，从经营者的立场观察，自有资本和借入资本没有区分的必要 \n'+ \
               '在借入资本利息中，除去利息支出、贴现费用、企业借债利息外，还应包括公司债券折价摊销数额在内 \n'+ \
               '息前税后总资产报酬率=息前税后利润 / 总资产期初期末均值 ×100% \n'+ \
               '净资产收益率(ROE)=净利润 / 净资产期初期末均值 ×100% \n'+ \
               '摊薄净资产收益率=净利润 / 净资产期末数值 ×100%，强调期末情况 \n'+ \
               '投入资本回报率(ROIC，Return Of Invested Capital)=息税前利润(EBIT) x (1-税率) / 投入资本 x100% \n'+ \
               '息税前利润(EBIT)=营业收入–营业成本–营业费用+营业外收入支出(或是税前净利+利息费用) \n'+ \
               '投入资本（Invested Capital）=流动资产–流动负债+不动产与厂房设备净额+无形资产及商誉，注意与总资本不同 \n'+ \
               '投入资本回报率的意义：更多地从投资而非财务角度看，每单位投资的资本所能赚取息税前利润的多少。 \n', \
              
              '收益质量':
               '注：\n'+ \
               '销售成本率=营业(总)成本 / 营业(总)收入 x100%，=1-毛利润 \n'+ \
               '成本费用率=(营业(总)成本+期间费用) / 营业(总)收入 x100%，=销售成本率+期间费用率，表示企业的成本费用控制能力 \n'+ \
               '期间费用率=期间费用 / 营业(总)收入 x100% \n',
              
              '成长能力':
              '注：\n'+ \
               '扣费(后)净利润=净利润-非经常性损益，即扣除了偶然的不可持续或不常发生的收益，可持续性强，可大于或小于净利润 \n'+ \
               '归属母公司净利润：简称归母净利润，指合并报表中归属母公司(上市公司)的利润，不包括子公司中非控股股东的利润。 \n',
              
              '财务风险':
               '注：\n'+ \
               '保守速动比率：又称超速动比率，=(现金+短期证券投资+应收账款净额)/流动负债，比速动比能够更好地评价短期偿债能力 \n'+ \
               '应收账款净额:指应收账款和其他应收款减去备抵坏账的净额，实质即为信誉高客户的应收款净额 \n'+ \
               '产权比率(equity ratio)=负债总额 / 所有者权益总额(净资产) x100%，从一个方面说明企业长期偿债能力，越高越弱 \n'+ \
               '说明：本表指标主要针对非金融普通企业，部分指标不完全适用于金融行业。 \n\n'+ \
               '注意：财报比率统计口径可能存在差异(例如采用期末/期初期末均值/期间加权等)，但不影响同一指标的可比性。',
              }        
    
    #确定表格字体大小
    titile_font_size=font_size
    heading_font_size=data_font_size=str(int(font_size.replace('px',''))-1)+'px'     
        
    # 一只股票情形：多日期
    if len(tickers_found) == 1:
        ticker1=tickers[0]
        """
        titletxt="\n===== 上市公司财务报表摘要："+ticker_name(ticker1)+" ====="    
        print(titletxt)    
        """
        titletxt=ticker_name(ticker1,'stock')+'：'+"财报摘要"
        
        fsdf1=fsdf[fsdf['ticker']==ticker1]
        for ty in typelist:
            dft=fsdf1[fsdf1['选项']==ty]
            #print(list(dft['指标']))
            
            # 自定义排序
            dft["指标"]=dft["指标"].astype('category').cat.set_categories(typedict[ty])
            dft.sort_values(by='指标',inplace=True)
            
            dft.reset_index(drop=True,inplace=True)
            dft.index=dft.index + 1
            dft2=dft.drop(labels=['选项','ticker'],axis=1)
            
            """
            print("\n***",ty+'：')
            colalign=['center','left']+['right']*(len(list(dft2)) - 1)
            print(dft2.to_markdown(tablefmt='Simple',index=True,colalign=colalign))
            print(notesdict[ty])
            """
            titletxt1=titletxt+'，'+ty
            
            if DEBUG:
                if ty == "每股指标":
                    print(dft2['指标'])
                    display(dft2)
            dft4=dft2.dropna(subset=['指标'])

            df_display_CSS(df=dft4,titletxt=titletxt1,footnote=notesdict[ty], \
                           facecolor=facecolor,decimals=2, \
                   titile_font_size=titile_font_size,heading_font_size=heading_font_size, \
                   data_font_size=data_font_size)
    
    # 多只股票情形：单日期
    import pandas as pd
    fsdates2=[]
    for fsd in fsdates:
        fsd2=pd.to_datetime(fsd)
        fsd3=fsd2.strftime("%Y-%m-%d")
        fsdates2=fsdates2+[fsd3]
    fsdates3=sorted(fsdates2,reverse=True)                
    
    if len(tickers_found) > 1:
        """
        titletxt="\n===== 上市公司财务报表摘要对比：报表日期"+fsdates3[0]+" ====="
        print('\n'+titletxt)    
        """
        #titletxt="财报摘要：报表日"+fsdates3[0]
        titletxt="财报摘要："+fsdates3[0]
        
        mdf=pd.DataFrame()
        for t in tickers_found:
            dft=fsdf[fsdf['ticker']==t]
            
            try:
                dft2=dft[['选项','指标',fsdates3[0]]]
                dft2.rename(columns={fsdates3[0]:ticker_name(t,'stock')},inplace=True)
            except:
                print("  #Error(compare_fin_summary_china): fin stmt of",t,'not found on',fsdates3[0])
                return None
            
            if len(mdf) == 0:
                mdf=dft2
            else:
                mdf=mdf.merge(dft2,left_on=['选项','指标'], right_on=['选项','指标'])
        
        for ty in typelist:
            dft=mdf[mdf['选项']==ty]
            
            # 自定义排序
            dft["指标"]=dft["指标"].astype('category').cat.set_categories(typedict[ty])
            dft.sort_values(by='指标',inplace=True)
            
            dft.reset_index(drop=True,inplace=True)
            dft.index=dft.index + 1
            dft2=dft.drop(labels=['选项'],axis=1)
            """
            print("\n***",ty+'：')
            colalign=['center','left']+['right']*(len(list(dft2)) - 1)
            print(dft2.to_markdown(tablefmt='Simple',index=True,colalign=colalign))
            print(notesdict[ty])
            """
            titletxt1=titletxt+'，'+ty
            dft4=dft2.dropna(subset=['指标'])
            
            df_display_CSS(df=dft4,titletxt=titletxt1,footnote=notesdict[ty], \
                           facecolor=facecolor,decimals=2, \
                   titile_font_size=titile_font_size,heading_font_size=heading_font_size, \
                   data_font_size=data_font_size)
            
    return dft2

#==============================================================================
#==============================================================================
if __name__=='__main__':
    ticker='000002.SZ'
    fsdates=['2022-12-31','2021-12-31','2020-12-31']
    
    fsdf1=get_fin_indicator_1ticker_china(ticker,fsdates)

def get_fin_indicator_1ticker_china(ticker,fsdates):
    """
    功能：获得A股财报指标，进行数据整理，单一股票
    输出：
    1、数量级变换：(元)-->(亿元)，并相应修改字段名
    """

    import pandas as pd
    # 过滤财报日期
    if isinstance(fsdates,str):
        fsdates=[fsdates]
        
    fsdates2=[]
    for d in fsdates:
        d1=pd.to_datetime(d)
        d2=d1.strftime("%Y-%m-%d")
        fsdates2=fsdates2 + [d2]
    fsdates3=sorted(fsdates2,reverse=True)
    start_year=fsdates3[-1][:4]
    
    # 亿元
    yiyuan=float(1e+08)
    
    # 获得股票所有财报数据
    _,t1,_=split_prefix_suffix(ticker)
    try:
        dft=ak.stock_financial_analysis_indicator(t1,start_year=start_year)
        dft['日期']=dft['日期'].apply(lambda x: x.strftime("%Y-%m-%d"))
        dft.sort_values(by=['日期'],ascending=False,inplace=True)
    except:
        print("  #Error(get_fin_indicator_1ticker_china): no info found for",ticker)
        return None        
    
    # 过滤财报日期 
    fsdate_field=list(dft)[0]
    dft2=dft[dft[fsdate_field].isin(fsdates3)]
    if len(dft2) < len(fsdates3):
        print("  #Warning(get_fin_indicator_1ticker_china): info of some dates unavailable for",ticker+'('+ticker_name(ticker,'stock')+')')
    if len(dft2) ==0:
        print("  #Error(get_fin_indicator_1ticker_china): no info found for",ticker+'('+ticker_name(ticker,'stock')+') on',fsdates)
        return None

    # 去掉重复行
    dft2b=dft2.drop_duplicates (keep='first')
    dft3=dft2b.replace('--',0)
    
    # 金额变换：元-->亿元，小数位截取
    collist3=list(dft3)
    for c in collist3:
        c1=c
        try:
            dft3[c]=dft3[c].astype(float)
            if ('元' in c) and not ('每股' in c):
                dft3[c]=dft3[c] / yiyuan
                c1=c.replace('元','亿元')
                dft3.rename(columns={c:c1},inplace=True)
                
            if ('比重' in c) and not ('%' in c):
                c1=c+'(%)'
                dft3.rename(columns={c:c1},inplace=True)
                
            dft3[c1]=dft3[c1].apply(lambda x: round(x,2))   
        except:
            pass
       
    # 检查字段改名情况
    collist3b=list(dft3)
    
    # 回填指标选项类型
    dft4=dft3.set_index(fsdate_field)
    dft4t=dft4.T
    dft5=dft4t.reset_index()
    dft5.index=dft5.index + 1
    dft5.rename(columns={'index':'指标'},inplace=True)
    
    # 去重
    dft5=dft5.drop_duplicates (keep='first')
    
    dft5['ticker']=ticker
        
    # 填充nan为零
    dft5.fillna(0,inplace=True)
    dft5.replace(0,'-',inplace=True)
    
    # 指标分类
    retstrlist=['利润率','毛利率','成本率','净利率','报酬率','比重','股息','收益率','增长率']
    debtstrlist=['流动比','速动比','现金比','倍数','负债','债务','权益','产权','清算']
    
    dft5['选项']=''
    for index,row in dft5.iterrows():
        # 改变顺序要谨慎
        if ('每股' in row['指标']) and (row['选项'] == ''):
            #row['选项']='每股指标'
            dft5.loc[index,'选项']='每股指标'
            
        if ('周转' in row['指标']) and (row['选项'] == ''):
            #row['选项']='营运能力'
            dft5.loc[index,'选项']='营运能力'
            
        if ('应收' in row['指标']) and (row['选项'] == ''):
            #row['选项']='应收账款'  
            dft5.loc[index,'选项']='应收账款'
            
        if ('预付' in row['指标']) and (row['选项'] == ''):
            #row['选项']='预付账款' 
            dft5.loc[index,'选项']='预付账款'
            
        if str_contain_any_substr(row['指标'],debtstrlist) and (row['选项'] == ''):
            #row['选项']='偿债能力'  
            dft5.loc[index,'选项']='偿债能力'
            
        if ('现金' in row['指标']) and (row['选项'] == ''):
            #row['选项']='现金指标'  
            dft5.loc[index,'选项']='现金指标'
            
        if ('亿元' in row['指标']) and (row['选项'] == ''):
            #row['选项']='规模指标' 
            dft5.loc[index,'选项']='规模指标'   
        """    
        if ('亿元' in row['指标']) and (row['选项'] == ''):
            #row['选项']='规模指标'  
            dft5.loc[index,'选项']='规模指标'                
        """    
        if str_contain_any_substr(row['指标'],retstrlist) and (row['选项'] == ''):
            #row['选项']='利润回报' 
            dft5.loc[index,'选项']='利润回报' 
            
        if (row['选项'] == ''):
            #row['选项']='其他指标'  
            dft5.loc[index,'选项']='其他指标'
    
    return dft5

#==============================================================================
if __name__=='__main__':
    tickers=['000002.SZ','601398.SS']
    fsdates=['2022-12-31','2021-12-31','2020-12-31']
    
    fsdfm=get_fin_indicator_china(tickers,fsdates)
    

def get_fin_indicator_china(tickers,fsdates):
    """
    功能：获得A股财报指标，进行数据整理
    输出：
    1、数量级变换：(元)-->(亿元)，并相应修改字段名
    """

    import pandas as pd
    # 过滤财报日期
    fsdates2=[]
    for d in fsdates:
        d1=pd.to_datetime(d)
        d2=d1.strftime("%Y-%m-%d")
        fsdates2=fsdates2 + [d2]
    fsdates3=list(set(fsdates2))
    fsdates4=sorted(fsdates3,reverse=True)
    
    df=pd.DataFrame()
    # 获得多只股票财报
    for t in tickers:
        # 抓取一只股票的财报
        dft=get_fin_indicator_1ticker_china(t,fsdates4)
        if dft is None: 
            continue
        
        if len(df)==0:
            df=dft
        else:
            df=pd.concat([df,dft])
    
    return df

#==============================================================================

if __name__=='__main__':
    tickers=['000002.SZ','601398.SS']
    fsdates=['2022-12-31','2021-12-31','2020-12-31']
    
    tickers=['000002.SZ','600048.SS','001979.SZ','600325.SS','000069.SZ','600383.SS','600895.SS','601155.SS']
    fidf=compare_fin_indicator_china(tickers,fsdates)
    
    tickers='601615.SS'
    fsdates=['2022-12-31',
         '2021-12-31',
         '2020-12-31',
         '2019-12-31',
         '2018-12-31',
        ]
    
def compare_fin_indicator_china(tickers,fsdates,facecolor='papayawhip',font_size='16px'):
    """
    功能：分类别显示财报摘要中的指标
    """        
    
    # 检查股票列表
    if isinstance(tickers,str):
        tickers=[tickers]
    tickers=list(tickers) #强制转换
    if len(tickers)==0:
        print("  #Error(compare_fin_indicator_china): need at least one stock in",tickers)
        return None
    
    # 检查财报日期列表
    if isinstance(fsdates,str):
        fsdates=[fsdates]
    if len(fsdates)==0:
        print("  #Error(compare_fin_indicator_china): need at least one date in",fsdates)
        return None
    
    for d in fsdates:
        result,_,_=check_period(d,d)
        if not result:
            print("  #Error(compare_fin_indicator_china): invalid date",d)
            return None
        
    # 获取财报数据
    print("  Searching for financial statements, please wait ...")
    fsdf=get_fin_indicator_china(tickers,fsdates)
    if fsdf is None:
        print("  #Error(compare_fin_indicator_china): none record found for above tickers on",fsdates[0])
        print("  Reasons: either wrong tickers or dates, or blocked by data source, try later")
        return None        
    if len(fsdf) == 0:
        print("  #Warning(compare_fin_indicator_china): zero recrod found for above tickers on",fsdates[0])
        print("  Reasons: wrong tickers or dates, or blocked by data source, try later")
        return None 
    
    # 不改变列表顺序去重
    tickerlist=list(fsdf['ticker'])
    tickers_found=sorted(list(set(tickerlist)),key=tickerlist.index)
    
    #optionlist=list(fsdf['选项'])
    #typelist=sorted(list(set(optionlist)),key=optionlist.index)
    typelist=['规模指标','利润回报','每股指标','营运能力','现金指标','偿债能力','应收账款','预付账款','其他指标']
    """
    # 按照指定的选项顺序排序
    fsdf['选项'] = fsdf['选项'].astype('category')
    fsdf['选项'].cat.reorder_categories(typelist, inplace=True)
    fsdf.sort_values('选项', inplace=True)
    """
    """
    # 列出每个选项的科目
    fsdf1=fsdf[fsdf['ticker']==tickers[0]]
    dictlist={}
    for ty in typelist:
        tmpdf=fsdf1[fsdf1['选项']==ty]
        tmplist=list(tmpdf['指标'])
        dictlist[ty]=tmplist
        
    """
    # 手工设定项目显示顺序，使其看起来更合理
    typedict={'规模指标': [
              '总资产(亿元)',
              '短期股票投资(亿元)','短期债券投资(亿元)','短期其它经营性投资(亿元)',
              '长期股票投资(亿元)','长期债券投资(亿元)','长期其它经营性投资(亿元)',
              '主营业务利润(亿元)','扣除非经常性损益后的净利润(亿元)',
              ],
        
              '利润回报': [
              '销售毛利率(%)','主营业务利润率(%)','营业利润率(%)','销售净利率(%)','成本费用利润率(%)',  
              '主营业务成本率(%)','三项费用比重(%)',
              #'主营利润比重(%)','非主营比重(%)','固定资产比重(%)',
              '主营利润比重(%)','固定资产比重(%)',
              '总资产利润率(%)','总资产净利润率(%)','资产报酬率(%)',
              '净资产收益率(%)','加权净资产收益率(%)','净资产报酬率(%)','投资收益率(%)','股本报酬率(%)','股息发放率(%)',
              '总资产增长率(%)','净资产增长率(%)','主营业务收入增长率(%)','净利润增长率(%)',
              ],
             
             '每股指标': [
              '加权每股收益(元)','扣除非经常性损益后的每股收益(元)','摊薄每股收益(元)','每股收益_调整后(元)',
              '每股净资产_调整前(元)','每股净资产_调整后(元)',#'调整后的每股净资产(元)',
              '每股未分配利润(元)','每股资本公积金(元)',
              '每股经营性现金流(元)',
              ],
             
             '营运能力': [
              '总资产周转率(次)','总资产周转天数(天)',   
              '应收账款周转率(次)','应收账款周转天数(天)',
              '存货周转率(次)','存货周转天数(天)',
              '流动资产周转率(次)','流动资产周转天数(天)',
              '固定资产周转率(次)',
              '股东权益周转率(次)'
              ],
             
             '现金指标': [
              '现金流量比率(%)',   
              '经营现金净流量对销售收入比率(%)',
              '资产的经营现金流量回报率(%)',
              '经营现金净流量与净利润的比率(%)',
              ],
             
             '偿债能力': [
              '流动比率','速动比率','现金比率(%)','利息支付倍数',
              '资产负债率(%)','长期负债比率(%)','股东权益比率(%)','产权比率(%)','负债与所有者权益比率(%)',
              '长期债务与营运资金比率(%)','股东权益与固定资产比率(%)','清算价值比率(%)',
              '经营现金净流量对负债比率(%)'],
             
             '应收账款': [
              '1年以内应收帐款(亿元)','1-2年以内应收帐款(亿元)',
              '2-3年以内应收帐款(亿元)','3年以内应收帐款(亿元)',
              '1年以内其它应收款(亿元)','1-2年以内其它应收款(亿元)',
              '2-3年以内其它应收款(亿元)','3年以内其它应收款(亿元)'],
             
             '预付账款': [
              '1年以内预付货款(亿元)','1-2年以内预付货款(亿元)', 
              '2-3年以内预付货款(亿元)','3年以内预付货款(亿元)'],
             
             '其他指标': [
              '长期资产与长期资金比率(%)', 
              '资本化比率(%)', 
              '固定资产净值率(%)', 
              '资本固定化比率(%)']}
    
    # 注释
    notesdict={'规模指标': \
               '注：\n'+ \
               '短期=一年以内，长期=一年以上 \n'+ \
               '非经常性损益=非经常性或偶然活动带来的损益，一般不可持续。 \n', \
              
              '利润回报': \
               '注：\n'+ \
               '销售毛利率=毛利率=毛利润/营业(总)收入*100%，毛利润=营业(总)收入-营业(总)成本 \n'+ \
               '主营业务利润率=主营业务利润/主营业务收入*100%，主营业务利润=主营业务收入-主营业务成本-主营业务税金及附加 \n'+ \
               '营业利润率=营业利润/营业(总)收入*100%，营业利润=主营业务利润+其他业务利润-期间费用+其他损益 \n'+ \
               '其他业务利润=其他业务收入-其它业务支出-其他业务税金及附加，期间费用=销售费用+管理费用+财务费用 \n'+ \
               '其他损益=-资产减值损失+公允价值变动损益(损失为负数)+投资损益(损失为负数)+资产处置损益(损失为负数) \n'+ \
               '利润总额=主营营业利润+非主营营业利润+投资损益+营业外收入支出净额 \n'+ \
               '销售净利率=净利润率=净利润/营业(总)收入*100%，净利润=利润总额-所得税费用 \n'+ \
               '成本费用利润率=利润总额/成本费用总额*100%，成本费用总额=营业(总)成本+营业税金及附加+期间费用+资产减值损失 \n'+ \
               '主营业务收入成本率=主营业务成本/主营业务收入*100% \n'+ \
               '三项费用比重=(管理费用+营业费用+财务费用)/营业(总)收入*100% \n'+ \
               '主营利润比重=主营业务利润/利润总额×100% \n'+ \
               '非主营比重=非主营业务利润/利润总额×100% \n'+ \
               '固定资产比重=固定资产/资产总额*100% \n'+ \
               '总资产利润率=利润总额/资产总额*100%，总资产净利润率(ROA)=净利润/资产总额*100% \n'+ \
               '资产报酬率=息税前利润/资产总额*100%，息税前利润(EBIT)=净利润+所得税费用+利息费用 \n'+ \
               '净资产收益率(ROE)=净利润/净资产*100%，净资产=资产总额-负债总额 \n'+ \
               '加权净资产收益率=净利润/加权平均净资产*100%，加权平均净资产含期间内净资产增减(如发新股、债转股或分红)情况 \n'+ \
               '净资产报酬率=息税前利润/加权平均净资产*100% \n'+ \
               '投资报酬率=投资回报率(ROI)=利润总额/投资总额*100%，投资总额=短期投资+长期投资 \n'+ \
               '股本报酬率=净利润/股东股本总数*100%，相当于股东股本按面值1元计算 \n'+ \
               '股息发放率=股利支付率=股利/净利润*100%，反映公司的股利分配政策，比例高表明公司不需更多的资金进行再投入。 \n', \

              '每股指标': \
               '注：\n'+ \
               '每股收益=净利润/流通股数量，其中流通股数量按期初期末均值计算 \n'+ \
               '扣除非经常性损益后的每股收益=扣除非经常性损益后的净利润/流通股数量 \n'+ \
               '加权每股收益=净利润/加权流通股数量，加权流通股数量含期间内流通股数量的变化(增发新股、送股、转增股本或配股等) \n'+ \
               '摊薄每股收益=净利润/期末流通股数量 \n'+ \
               '调整后每股收益=调整后净利润/流通股数量，其中调整后净利润考虑了长期账龄的应收款项成为呆坏账对净利润的影响 \n'+ \
               '稀释后每股收益=净利润/稀释后流通股数量，假设企业的可转债、认股权证、股票期权等期间内均转换为普通股的情形 \n'+ \
               '每股净资产(调整前)=净资产/流通股数量，调整后指标则考虑了其流动性和变现能力，扣除了长期应收款项和(长期)待摊费用 \n'+ \
               '每股未分配利润=未分配利润/流通股数量，未分配利润指净利润经过弥补亏损、提取盈余公积和分红后留存在企业的利润累积 \n'+ \
               '每股资本公积金=资本公积金/流通股数量，资本公积金含发行股份的溢价、资产重估增值、接受捐赠等，仅可用于转增股本。 \n', \
              
              '营运能力': 
               '注：\n'+ \
               '指标周转率/周转次数：营业(总)收入/指标的起初期末均值，从企业自身角度来说越大越好，但若对供应商则可能相反 \n'+ \
               '指标周转天数：360/周转率(或周转次数)，从企业自身角度来说越小越好，但若涉及供应商则可能相反 \n'+ \
               '注意：本表指标主要针对非金融行业，部分指标不适用于金融行业。 \n', \
              
              '现金指标':
               '注：\n'+ \
               '现金流量比率=经营活动产生的现金净流量/期末流动负债*100%，反映企业短期偿债能力 \n'+ \
               '经营现金净流量对销售收入比率=销售现金比率，与赊销政策有关，若企业有虚假收入，也会使该指标过低 \n'+ \
               '资产的经营现金流量回报率=经营现金流量净额/总资产*100%,体现企业经营活动的收现能力 \n'+ \
               '经营现金净流量与净利润的比率=净现比=经营现金流量净额/净利润*100%。比率越大,企业盈利质量越高。 \n',
               
              '偿债能力':
               '注：\n'+ \
               '流动比率=流动资产/流动负债，反映企业的短期偿债能力，属于宽松指标 \n'+ \
               '速动比率=(流动资产-存货)/流动负债，反映企业的短期偿债能力，属于较严的指标 \n'+ \
               '现金比率=(货币资金+短期有价证券)/流动负债*100%，反映企业的短期偿债能力，属于严厉的指标 \n'+ \
               '利息支付倍数=利息保障倍数=税息前利润/利息费用*100%，衡量偿付借款利息的能力 \n'+ \
               '长期负债比率=资本化比率=长期负债/资产总额*100% \n'+ \
               '股东权益比率=自有资本比率=净资产比率=股东权益/资产总额*100% \n'+ \
               '产权比率=长期负债/所有者权益(股东权益)*100% \n'+ \
               '长期债务与营运资金比率=长期债务/营运资金*100%，反映偿还债务能力，通常长期债务不应超过营运资金 \n'+ \
               '营运资金=流动资产-流动负债 \n'+ \
               '股东权益与固定资产比率=股东权益总额÷固定资产总额×100%，衡量公司财务结构稳定性，越大越稳定 \n'+ \
               '清算价值比率=有形资产/负债总额*100%，反映公司清偿全部债务的能力 \n'+ \
               '经营现金净流量对负债比率=现金流量负债比=经营活动现金流量净额/负债总额*100%，比率越高，财务弹性越好。 \n',
              
              '应收账款':
               '注：\n'+ \
               '使用账龄法对应收账款/其他应收款分类 \n'+ \
               '一般而言，应收款项的账龄越长，成为呆坏账的可能性就越大。 \n',
              
              '预付账款':
               '注：\n'+ \
               '一般而言，预付款项数额越大，企业在供应链中的地位越低 \n'+ \
               '一般而言，预付款项的账龄越长，企业在供应链中的地位越低。 \n',
              
              '其他指标':
                '注：\n'+ \
               '长期资产与长期资金比率=非流动资产/(长期负债+股东权益)*100%，长期资金少，流动负债较多，财务风险较大 \n'+ \
               '资本化比率=长期负债/(长期负债+股东权益)*100%，指标值越小，负债的资本化程度就越低，长期偿债压力就越小 \n'+ \
               '固定资产净值率=(固定资产原值-累计折旧)/固定资产原值*100%，反映企业全部固定资产平均新旧程度 \n'+ \
               '资本固定化比率=非流动资产/净资产*100%，若超过100%说明固定资产资金投入超过自身能力，易造成财务状况恶化。\n',
              }        

    #确定表格字体大小
    titile_font_size=font_size
    heading_font_size=data_font_size=str(int(font_size.replace('px',''))-1)+'px'
    
    # 标记选项类型
    typedict_keys=list(typedict.keys())
    for index,row in fsdf.iterrows():
        for k in typedict_keys:
            if row['指标'] in typedict[k]:
                fsdf.loc[index,'选项']=k
        
    # 一只股票情形：多日期
    if len(tickers_found) == 1:
        ticker1=tickers[0]
        """
        titletxt="\n===== 上市公司主要财务比率和重要指标："+ticker_name(ticker1)+" ====="    
        print(titletxt)    
        """
        titletxt="主要财务比率和指标："+ticker_name(ticker1,'stock')
        
        fsdf1=fsdf[fsdf['ticker']==ticker1]
        for ty in typelist:
            dft=fsdf1[fsdf1['选项']==ty]
            #dft=fsdf1[fsdf1['选项'].apply(lambda x: x in typedict[ty])]
            #print(list(dft['指标']))
            
            # 自定义排序
            try:
                tmplist=typedict[ty]
                dft2=dft[dft['指标'].isin(tmplist)]
                
                tmplist2=sorted(list(set(tmplist)),key=tmplist.index)
                dft2["指标"]=dft2["指标"].astype('category').cat.set_categories(tmplist2)
            except:
                print("#set_categories error",ty)
                print(typedict[ty])
                pass
            
            dft2.sort_values(by='指标',inplace=True)
            
            dft2.reset_index(drop=True,inplace=True)
            dft2.index=dft2.index + 1
            dft3=dft2.drop(labels=['选项','ticker'],axis=1)
            """
            print("\n***",ty+'：')
            colalign=['center','left']+['right']*(len(list(dft3)) - 1)
            print(dft3.to_markdown(tablefmt='Simple',index=True,colalign=colalign))
            print(notesdict[ty])
            """
            """
            注意：若dft3为空，则会出现错误：list assignment index out of range
            无论如何修改colalign都没用
            """
            titletxt1=titletxt+'，'+ty
            
            df_display_CSS(df=dft3,titletxt=titletxt1,footnote=notesdict[ty], \
                           facecolor=facecolor,decimals=2, \
                   titile_font_size=titile_font_size,heading_font_size=heading_font_size, \
                   data_font_size=data_font_size)
        
        return dft3
            
    # 多只股票情形：单日期
    if len(tickers_found) > 1:
    
        import pandas as pd
        fsdates2=[]
        for fsd in fsdates:
            fsd2=pd.to_datetime(fsd)
            fsd3=fsd2.strftime("%Y-%m-%d")
            fsdates2=fsdates2+[fsd3]
        fsdates3=sorted(fsdates2,reverse=True)                
    
        mdf=pd.DataFrame()
        for t in tickers_found:
            dft=fsdf[fsdf['ticker']==t]
            
            try:
                dft2=dft[['选项','指标',fsdates3[0]]]
                dft2.rename(columns={fsdates3[0]:ticker_name(t,'stock')},inplace=True)
            except:
                print("  #Error(compare_fin_summary_china): fin stmt of",fsdates3[0],'not found for',t)
                return None
            
            if len(mdf) == 0:
                mdf=dft2
            else:
                mdf=mdf.merge(dft2,how='outer',left_on=['选项','指标'], right_on=['选项','指标'])
        """
        titletxt="\n===== 上市公司财务报表主要比率和重要项目对比：报表日期"+fsdates3[0]+" ====="
        print('\n'+titletxt)    
        """
        #titletxt="主要财务比率和指标：报表日"+fsdates3[0]
        titletxt="主要财务比率和指标："+fsdates3[0]
        
        for ty in typelist:
            dft=mdf[mdf['选项']==ty]
            
            # 自定义排序
            tmplist=typedict[ty]
            dft2=dft[dft['指标'].isin(tmplist)]
            
            tmplist2=sorted(list(set(tmplist)),key=tmplist.index)
            dft2["指标"]=dft2["指标"].astype('category').cat.set_categories(tmplist2)
            dft2.sort_values(by='指标',inplace=True)
            
            dft2.reset_index(drop=True,inplace=True)
            dft2.index=dft2.index + 1
            dft3=dft2.drop(labels=['选项'],axis=1)
            """
            print("\n***",ty+'：')
            colalign=['center','left']+['right']*(len(list(dft3))-2)
            print(dft3.to_markdown(tablefmt='Simple',index=True,colalign=colalign))
            print(notesdict[ty])
            """
            titletxt1=titletxt+'，'+ty
            df_display_CSS(df=dft3,titletxt=titletxt1,footnote=notesdict[ty], \
                           facecolor=facecolor,decimals=2, \
                   titile_font_size=titile_font_size,heading_font_size=heading_font_size, \
                   data_font_size=data_font_size)
    
        return dft3

#==============================================================================
#==============================================================================
if __name__ == '__main__':
    fsdf=get_fin_stmt_ak('601398.SS')
    account_entry='资产总计'
    
    fsdf1=fs_entry_begin_china(fsdf,account_entry=account_entry,suffix='_期初')

def fs_entry_begin_china(fsdf,account_entry='资产总计',suffix='_期初'):
    """
    功能：以上年年报期末科目数值作为本期年报和季报的期初，仅适用于akshare大陆财报！
    """
    import pandas as pd
    import numpy as np
    #获取年报日期
    ar_mm_dd='12-31'
    
    fsdf['asOfDate_pd']=fsdf.index
    fsdf['Date_y4']=fsdf['asOfDate_pd'].apply(lambda x: pd.to_datetime(x).strftime("%Y"))
    fsdf['Date_begin_pd']=fsdf['Date_y4'].apply(lambda x: pd.to_datetime(str(int(x)-1)+'-'+ar_mm_dd))
    
    asOfDate_pd_list=list(fsdf['asOfDate_pd'])
    entry_begin=lambda x: fsdf[fsdf['asOfDate_pd']==x][account_entry].values[0] if x in asOfDate_pd_list else np.nan
    fsdf[account_entry+suffix]=fsdf['Date_begin_pd'].apply(entry_begin)
    
    fsdf.drop(['asOfDate_pd','Date_y4','Date_begin_pd'],axis=1,inplace=True)
    
    return fsdf
#==============================================================================
#==============================================================================
#==============================================================================
