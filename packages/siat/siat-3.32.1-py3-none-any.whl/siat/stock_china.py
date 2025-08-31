# -*- coding: utf-8 -*-
"""
模块功能：借助机器学习学习方法，预测次日股票价格走势，仅适用于中国大陆股票
模型：最近邻模型
算法：借助个股过去一百个交易日的资金净流入/净流出以及大盘走势变化，进行机器学习
注意：如果在当日未收盘时运行，预测的是当日个股收盘价的走势；若在收盘后运行则预测次日走势
作者：王德宏，北京外国语大学国际商学院
日期：2021-5-13
"""
#==============================================================================
import warnings; warnings.filterwarnings('ignore')

from siat.common import *
from siat.translate import *
from siat.grafix import *
from siat.security_prices import *
from siat.security_price2 import *
#==============================================================================
# 获得个股近一百个交易日的资金净流入数据
#==============================================================================

if __name__=='__main__':
    ticker='600519.Ss'

    dfp=get_money_flowin(ticker)
    
    end='2023-6-15'
    dfp=get_money_flowin(ticker,end)

def get_money_flowin(ticker,end='latest'):
    """
    功能：抓取个股近一百个交易日的资金净流入情况，以及大盘指数的情况
    ticker：个股代码，带后缀
    标准化方法：原始数据
    注意：目前仅支持沪深股市
    """
    ticker1=ticker.upper()[:6]
    exch=ticker.upper()[7:9]
    
    import akshare as ak
    import pandas as pd
    
    #判断沪深市场
    if exch=='':
        l1=ticker[0]; market='sh'
        if l1 in ['0','2','3']: market='sz'
        #深市股票以0/2/3开头，沪市以6/9开头
    else:
        if exch=='SS':
            market='sh'
        elif exch=='SZ':
            market='sz'
        else:
            print("  #Warning(get_money_flowin): currently only support Shanghai/Shenzhen stock exchanges")
            return None
    
    #获得个股资金流动明细
    try:
        df = ak.stock_individual_fund_flow(stock=ticker1, market=market)
    except:
        print("  #Error(get_money_flowin): money flow info unavailable for",ticker)
        return None

    df['ticker']=ticker

    df['Date']=df['日期'].apply(lambda x: pd.to_datetime(x))  #不带时区的日期
    df.set_index('Date',inplace=True)
    df['date']=df['日期']
    
    df['Close']=df['收盘价'].apply(lambda x: float(x))
    df['Change%']=df['涨跌幅'].apply(lambda x: float(x))
    
    #类型转换
    df['netFlowInAmount_main']=df['主力净流入-净额'].apply(lambda x: float(x))
    df['netFlowInAmount_small']=df['小单净流入-净额'].apply(lambda x: float(x))
    df['netFlowInAmount_mid']=df['中单净流入-净额'].apply(lambda x: float(x))
    df['netFlowInAmount_big']=df['大单净流入-净额'].apply(lambda x: float(x))
    df['netFlowInAmount_super']=df['超大单净流入-净额'].apply(lambda x: float(x))
    
    # 总净流入金额：可正可负
    df['netFlowInAmount']=df['netFlowInAmount_main']+df['netFlowInAmount_small']+ \
                          df['netFlowInAmount_mid']+df['netFlowInAmount_big']+ \
                          df['netFlowInAmount_super']

    df['netFlowInRatio%_main']=df['主力净流入-净占比'].apply(lambda x: float(x))
    df['netFlowInRatio%_small']=df['小单净流入-净占比'].apply(lambda x: float(x))
    df['netFlowInRatio%_mid']=df['中单净流入-净占比'].apply(lambda x: float(x))
    df['netFlowInRatio%_big']=df['大单净流入-净占比'].apply(lambda x: float(x))
    df['netFlowInRatio%_super']=df['超大单净流入-净占比'].apply(lambda x: float(x))

    #重要：处理有缺失值的记录，确保未收盘时能预测当天的收盘价涨跌方向
    #df.dropna(inplace=True)
    df.fillna(0,inplace=True)
    
    # 对数量级巨大的金额项进行对数处理，避免其对数量级小的项形成数量级压制
    amtColList=['netFlowInAmount_main','netFlowInAmount_small','netFlowInAmount_mid', \
                'netFlowInAmount_big','netFlowInAmount_super','netFlowInAmount']
    import math
    for a in amtColList:
        # 取对数
        df[a+'_ln']=df[a].apply(lambda x: math.log(x) if x>0 else -math.log(-x) if x<0 else 0)
    
    # 删除原有金额项目
    df.drop(amtColList,axis=1,inplace=True)
    
    #去掉不用的字段
    dfdroplist=['主力净流入-净额','小单净流入-净额','中单净流入-净额','大单净流入-净额', \
                '超大单净流入-净额','主力净流入-净占比','小单净流入-净占比', \
                '中单净流入-净占比','大单净流入-净占比','超大单净流入-净占比', \
                '收盘价','涨跌幅','日期']
    df.drop(labels=dfdroplist,axis=1,inplace=True)
    
    df.sort_index(ascending=True,inplace=True)
    fromdate=df['date'].values[0]
    todate=df['date'].values[-1]
    
    #获得大盘指数和交易量
    dpindex="000001.SS"  #上证综合指数
    if market == 'sz': dpindex="399001.SZ"   #深圳成分指数
    df_dp_tmp=get_price(dpindex,fromdate,todate)
    
    df_dp_tmp['Volume_mkt']=df_dp_tmp['Volume'].apply(lambda x: math.log(x))
    df_dp_tmp['Close_mkt']=df_dp_tmp['Close']
    df_dp=df_dp_tmp[['Volume_mkt','Close_mkt']]
    
    # 获得股票交易量
    df_stk_tmp=get_price(ticker,fromdate,todate)
    df_stk_tmp['Volume_ln']=df_stk_tmp['Volume'].apply(lambda x: math.log(x))
    df_stk=df_stk_tmp[['Open','High','Low','Adj Close','Volume_ln']]

    # 合并
    df_stk_mkt=pd.merge(df_stk,df_dp,how='left',left_index=True,right_index=True) 
    
    dfp_tmp=pd.merge(df,df_stk_mkt,how='left',left_index=True,right_index=True)
    newColList=['date','Close','Change%','Adj Close','Open','High','Low','Volume_ln', \
                'netFlowInRatio%_main','netFlowInRatio%_small','netFlowInRatio%_mid', \
                'netFlowInRatio%_big','netFlowInRatio%_super', \
                'netFlowInAmount_main_ln','netFlowInAmount_small_ln','netFlowInAmount_mid_ln', \
                'netFlowInAmount_big_ln','netFlowInAmount_super_ln', 'netFlowInAmount_ln', \
                'Close_mkt','Volume_mkt']
    dfp=dfp_tmp[newColList]
    
    if end=='latest':
        dfp2=dfp
    else:
        jieguo,end2=check_date2(end)
        if not jieguo:
            dfp2=dfp
        else:
            dfp2=dfp[dfp['date'] <= end2]
    
    return dfp2


#==============================================================================
# 对特征数据进行预处理
#==============================================================================

def preprocess(X,preproctype='nop'):
    """
    功能：对特征数据X进行标准化预处理，不处理标签数据y
    df：原始数据
    preproctype：默认'nop'（不处理），
    还支持'0-1'（标准缩放法）、'min-max'（区间缩放法）和'log'（分别取对数）
    """
    typelist=['0-1','min-max','log','nop']
    if not (preproctype in typelist):
        print('  #Error(preproc): not supported for preprocess type',preproctype)
        print('  Supported preprocess types:',typelist)
        return None
    
    import pandas as pd
    collist=list(X)
    scaler_X=X.copy()
    #标准化——（0-1标准化）
    if preproctype == '0-1':
        for c in collist:
            value_min=scaler_X[c].min()
            value_max=scaler_X[c].max()
            scaler_X[c]=(scaler_X[c]-value_min)/(value_max-value_min)

    #标准化——（区间缩放法）
    if preproctype == 'min-max':
        for c in collist:
            value_mean=scaler_X[c].mean()
            value_std=scaler_X[c].std()
            scaler_X[c]=(scaler_X[c]-value_mean)/value_std

    #标准化——（对数法）
    if preproctype == 'log':
        for c in collist:
            scaler_X[c]=scaler_X[c].apply(lambda x: slog(x))

    #标准化——（不处理）
    if preproctype == 'nop': pass
        
    return scaler_X        

def slog(x):
    '''
    功能：对x取对数，正数直接取对数，负数先变为正数再取对数加负号，零不操作
    '''
    import numpy as np
    if x == np.nan: return np.nan
    if x == 0: return 0
    if x > 0: return np.log(x)
    if x < 0: return -np.log(-x)
    
if __name__=='__main__':
    scaler_X=preproc(X,preproctype='0-1')

#==============================================================================
# 构造适合机器学习的样本
#==============================================================================
if __name__=='__main__':
    ndays=1
    preCumTimes=5
    
    dfp=get_money_flowin('600519.SS')
    
    X,ydf,X_new=make_sample(dfp,ndays=1)

def make_sample(dfp,ndays=1,preCumTimes=5):
    """
    功能：构造适合机器学习的样本
    ndays：预测未来几个交易日
    preCumTimes：使用过去几倍交易日的累计数据，
    使用过去交易日的实际天数=preCumTimes * ndays
    preproctype：对特征数据进行预处理的类型
    """    
    
    preDays=ndays * preCumTimes
    
    #构造过去一段时间资金净流入累加值
    amtColList=[]
    colList=list(dfp)
    for c in colList:
        if 'Amount' in c:
            amtColList=amtColList+[c]
    
    for c in amtColList:
        dfp[c+'_cum']=dfp[c].rolling(window=preDays,min_periods=1).sum()
    
    #构造过去一段时间资金净流入比例均值
    ratioColList=[]
    for c in colList:
        if 'Ratio' in c:
            ratioColList=ratioColList+[c]
    
    for c in ratioColList:
        dfp[c+'_avg']=dfp[c].rolling(window=preDays,min_periods=1).mean()
    
    #构造过去一段时间大盘指数的均值和标准差
    mktColList=['Close_mkt','Volume_mkt']
    for c in mktColList:
        dfp[c+'_avg']=dfp[c].rolling(window=preDays,min_periods=1).mean()
        dfp[c+'_std']=dfp[c].rolling(window=preDays,min_periods=1).std()
    
    #重要：去掉前几行，此处位置敏感
    dfp1=dfp.dropna()
    if len(dfp1)==0:
        print("  #Error(make_sample): dropna caused empty dataframe, process stopped")
        return None,None
    
    #按照ndays滚动
    newColList=list(dfp1)
    newColList.remove('date')
    dfp2=dfp1[newColList]
    for c in newColList:
        dfp2[c+'_roll']=dfp2[c].rolling(window=ndays,min_periods=1).mean()
    
    newColList2=list(dfp2)
    newColList3=[]
    for c in newColList2:
        if '_roll' in c:
            newColList3=newColList3+[c]
    newColList3=newColList3+['Close','Change%']
    dfp3=dfp2[newColList3]
    
    #添加未来一个单位(ndays)的股价信息
    dfp3['Close_next']=dfp3['Close'].shift(-1)
    dfp3['Change%_next']=dfp3['Change%'].shift(-1)
    ylist=['Close_next','Change%_next']

    #供训练用的数据集
    XCollist=list(dfp3)
    for c in ylist:
        XCollist.remove(c)
    dfp4=dfp3.dropna()
    X = dfp4[XCollist]
    ydf = dfp4[ylist]    
    
    # X_new
    X_new = dfp3.tail(1)[XCollist]
    
    return X,ydf,X_new

#==============================================================================
# 训练模型，获得最优模型参数，进行预测
#==============================================================================
if __name__=='__main__':
    noday=1
    y='Close'   
    diff=0.03
    min_score=0.6
    votes=100
    max_neighbours=10
    max_RS=10
    printout=True

def train_predict_knn(X,ydf,noday=1,y='Close', \
    diff=0.03,min_score=0.6,votes=100,max_neighbours=10,max_RS=10,printout=True):
    """
    功能：训练模型，选择最优参数，预测
    X：特征矩阵
    ydf：标签矩阵
    nodays：预测未来第几天
    y：标签，默认'Close'为股价，'Change%'为涨跌幅，'Direction'为涨跌方向
    
    未用！
    """
    ylist=['Close','Change%','Direction']
    if not (y in ylist):
        print("  #Error(train_predict_knn):",y,"not within",ylist)
    clflist=['Direction']
    reglist=['Close','Change%']
    
    #拆分训练集和测试集
    from sklearn.model_selection import train_test_split   
    XX=X[: -noday]
    import numpy as np
    if noday == 1:
        X_new=np.arrary(X[-1:])
    else:
        X_new=np.arrary(X[-noday:-noday+1])
    
    yydf=ydf[: -noday]
    yy=yydf[y+'_next'+str(noday)]
    
    
    if y in clflist:
        from sklearn.neighbors import KNeighborsClassifier
    if y in reglist:
        from sklearn.neighbors import KNeighborsRegressor

    #寻找最优模型参数
    nlist=list(range(1,max_neighbours+1))
    n_num=len(nlist)
    wlist=['uniform','distance']
    mlist1=['braycurtis','canberra','correlation','dice','hamming','jaccard']
    mlist2=['kulsinski','matching','rogerstanimoto','russellrao']
    mlist3=['sokalmichener','sokalsneath','sqeuclidean','yule','chebyshev']
    mlist4=['cityblock','euclidean','minkowski','cosine']
    mlist=mlist1+mlist2+mlist3+mlist4
    rslist=list(range(0,max_RS+1))
    results=pd.DataFrame(columns=('spread','train_score','test_score', \
                                  'neighbours','weight','metric','random','pred'))
    print('\n  Searching for best parameters of knn model in',ndays,'trading days ...')
    print('    Progress: 0%, ',end='')
    for n in nlist:
        for w in wlist:
            for m in mlist:
                for rs in rslist:    
                    X_train,X_test,y_train,y_test=train_test_split(XX,yy,random_state=rs)
                    
                    if y in clflist:
                        knn1=KNeighborsClassifier(n_neighbors=n,weights=w,metric=m,n_jobs=-1)
                    if y in reglist:
                        knn1=KNeighborsClassifier(n_neighbors=n,weights=w,metric=m,n_jobs=-1)
                    knn1.fit(X_train, y_train)
                    train_score=round(knn1.score(X_train, y_train),3)
                    test_score=round(knn1.score(X_test, y_test),3)
                    
                    prediction=knn1.predict(X_new)[0]
                    spread=abs(round(train_score-test_score,3))
                    
                    row=pd.Series({'spread':spread,'train_score':train_score, \
                                   'test_score':test_score,'neighbours':n, \
                                   'weight':w,'metric':m,'random':rs,'pred':prediction})
                    try:
                        results=results.append(row,ignore_index=True)
                    except:
                        results=results._append(row,ignore_index=True)
                        
        print(int(n/n_num*100),'\b%, ',end='')
    print('done.') 
    
    #去掉严重过拟合的结果           
    r0=results[results['train_score'] < 1]
    #去掉训练集、测试集分数不过半的模型    
    r0=r0[r0['train_score'] > min_score]
    r0=r0[r0['test_score'] > min_score]
    #去掉泛化效果差的结果
    r0=r0[r0['spread'] < diff]  #限定泛化差距
    #优先查看泛化效果最优的结果
    r1=r0.sort_values(by=['spread','test_score'],ascending=[True,False])        
    #优先查看测试分数最高的结果
    r2=r0.sort_values(by=['test_score','spread'],ascending=[False,True])

    if votes > len(r2): votes=len(r2)
    r2head=r2.head(votes)    
    
    # 未完
    
#==============================================================================
# 训练，获得最优模型参数
#==============================================================================
if __name__=='__main__':
    ndays=1
    max_neighbors=10
    max_p=6
    cv=5
    rs=0

def training_knn_clf(scaler_X,ydf,ndays=1,max_neighbors=10,max_p=6,cv=5,rs=0):
    '''
    功能：对(X,y)
    scaler_X: 特征矩阵
    y：标签矩阵
    
    未用！
    '''
    
    #获得分类变量y
    ydf['nextChange%']=ydf['Change%'].shift(-ndays)
    ydf['nextDirection']=ydf['nextChange%'].apply(lambda x: 'Higher' if x>0 else 'Lower')
    y=ydf['nextDirection']
    
    #拆分训练集和测试集
    from sklearn.model_selection import train_test_split
    X_train,X_test,y_train,y_test=train_test_split(scaler_X,y,random_state=rs)
    
    #定义网格搜索参数
    param_grid = [
            {  # 遍历：非加权距离
             'weights': ['uniform'], # 参数取值范围
             'n_neighbors': [i for i in range(1,max_neighbors+1)]  # 使用其他方式如np.arange()也可以
             # 这里没有p参数
             },
            {  # 遍历：加权距离
             'weights': ['distance'],
             'n_neighbors': [i for i in range(1,max_neighbors+1)],
             'p': [i for i in range(1,max_p)]
             } ]
 
    #训练训练集
    from sklearn.neighbors import KNeighborsClassifier
    knn = KNeighborsClassifier()  # 默认参数，创建空分类器

    from sklearn.model_selection import GridSearchCV  # CV，使用交叉验证方式获得模型正确率
    grid_search = GridSearchCV(knn, param_grid,scoring='accuracy',cv=cv)  # 网格搜索参数

    #grid_search.fit(X_train, y_train)  
    grid_search.fit(X,y)  
    best_knn=grid_search.best_estimator_
    train_score=best_knn.score(X_train, y_train)
    test_score=best_knn.score(X_test, y_test)
    
    best_params=grid_search.best_params_
    """
    k=best_params['n_neighbors']
    p=best_params['p']
    w=best_params['weights']
    """
    return best_params,train_score,test_score

    
#==============================================================================
# Forecasting stock price directions by money flow in/out, using knn
#==============================================================================
if __name__=='__main__':
    ticker='600519.SS'
    ticker='000723.SZ'
    
    ndays=1
    min_score=0.9
    diff=0.01
    votes=100
    max_neighbours=10
    max_RS=10
    printout=True
    
    df=get_money_flowin(ticker,end='2023-6-15')
    decision,known_close,known_day=price_direction_knn(ticker,df,ndays=1)

def price_direction_knn(ticker,df,ndays=1,diff=0.01,min_score=0.9,votes=100,max_neighbours=10,max_RS=10,printout=True):

    """
    功能：基于个股资金流动预测次日股票涨跌方向，涨或跌
    ticker：股票代码，无后缀
    df：个股资金净流入
    ndays：预测几天后的股价涨跌方向，默认1天
    diff：泛化精度，越小越好
    min_score：最小测试分数
    votes：软表决票数
    max_neighbours：最大邻居个数
    max_RS：最大随机数种子
    """
    import pandas as pd
    
    # 判断是否周末无交易免预测
    known_day=df.tail(1)['date'].values[0]
    
    tdate=date_adjust(known_day, adjust=ndays)
    tdate_pd=pd.to_datetime(tdate)
    tdate_wd=tdate_pd.weekday()
    if tdate_wd in [5,6]:
        print("  #Warning: after",ndays,"day(s) is",tdate,"(weekend), no trading")
        decision='~'
        known_close=df.tail(1)['Close'].values[0]
        
        return decision,known_close,known_day
    
    #构造样本：标签ydf，特征矩阵X，预测X_new
    X,ydf,X_new=make_sample(df,ndays=ndays)
    
    #X_new1=X_new.head(1).values
    known_day_np=X_new.index.values[0]
    known_day_pd=pd.to_datetime(known_day_np)    
    known_day=known_day_pd.strftime("%Y-%m-%d")
    known_close=X_new['Close'].values[0]
    
    ydf['nextDirection']=ydf['Change%_next'].apply(lambda x: 1 if x>0 else -1 if x <0 else 0)
    
    #建立样本：标签序列
    y1=ydf['nextDirection'] #二分类
    #y2=df2['nextChange%']   #回归
    #y3=df2['nextClose']     #回归

    #拆分训练集和测试集：y1
    from sklearn.model_selection import train_test_split
    #引入k近邻分类模型：
    from sklearn.neighbors import KNeighborsClassifier

    #寻找最优模型参数
    nlist=list(range(1,max_neighbours+1))
    n_num=len(nlist)
    wlist=['uniform','distance']
    mlist1=['braycurtis','canberra','correlation','dice','hamming','jaccard']
    mlist2=['kulsinski','matching','rogerstanimoto','russellrao']
    mlist3=['sokalmichener','sokalsneath','sqeuclidean','yule','chebyshev']
    mlist4=['cityblock','euclidean','minkowski','cosine']
    mlist=mlist1+mlist2+mlist3+mlist4
    rslist=list(range(0,max_RS+1))
    
    results=pd.DataFrame(columns=('spread','train_score','test_score', \
                                  'neighbours','weight','metric','random','pred'))
    print('\nSearching for best parameters of knn model in',ndays,'trading days ...')
    print('  Progress: 0% ',end='')
    for n in nlist:
        for w in wlist:
            for m in mlist:
                for rs in rslist:    
                    knn1=KNeighborsClassifier(n_neighbors=n,weights=w,metric=m,n_jobs=-1)
                    X_train,X_test,y_train,y_test=train_test_split(X,y1,random_state=rs)
                    tmp=knn1.fit(X_train, y_train) #调试时去掉tmp=可跟踪模型参数
                    train_score=round(knn1.score(X_train, y_train),3)
                    test_score=round(knn1.score(X_test, y_test),3)
                    prediction=knn1.predict(X_new)[0]
                    spread=abs(round(train_score-test_score,3))
                    
                    row=pd.Series({'spread':spread,'train_score':train_score, \
                                   'test_score':test_score,'neighbours':n, \
                                   'weight':w,'metric':m,'random':rs,'pred':prediction})
                    try:
                        results=results.append(row,ignore_index=True)
                    except:
                        results=results._append(row,ignore_index=True)
                        
        print(int(n/n_num*100),'\b% ',end='')
    print('done.') 
    
    
    # 过滤训练/测试分数差的结果
    r0=results[(results['train_score']>=min_score) & (results['test_score']>=min_score)]
    # 避免min_score设置得太高导致无结果，或者数量太多
    r0_len=len(r0)
    #if r0_len==0 or r0_len > votes:
    if r0_len==0:
        train_score_max=results['train_score'].max()
        test_score_max=results['test_score'].max()
        min_score_new=min(train_score_max,test_score_max)
        r0=results[(results['train_score']>=min_score_new) & (results['test_score']>=min_score_new)]
        
        if len(r0)==0:
            spread_quantile=results['spread'].quantile(q=0.01)
            r0_spread=results[(results['spread']<spread_quantile)]
            if len(r0_spread)==0:
                r0_spread=results[(results['spread']<=spread_quantile)]

            test_score_quantile=r0_spread['test_score'].quantile(q=0.99)
            r0=r0_spread[(r0_spread['test_score']>test_score_quantile)]
            if len(r0)==0:
                r0=r0_spread[(r0_spread['test_score']>=test_score_quantile)]
                
            train_score_max=r0['train_score'].max()
            test_score_max=r0['test_score'].max()
            min_score_new=min(train_score_max,test_score_max)
            
        print("  #Warning: filtering parameter min_score has been adjusted to",min_score_new)
    
    #去掉泛化效果差的结果
    r1=r0[r0['spread'] <= diff]  #限定泛化差距
    r1_len=len(r1)
    #if r1_len==0 or r1_len>=votes:
    if r1_len==0:
        diff_new=r0['spread'].min()
        r1=r0[r0['spread'] <= diff_new]
        print("  #Warning: filtering parameter diff has been adjusted to",diff_new)
    
    
    """
    # 首选测试效果好的
    r0=results[(results['test_score']>=min_score)]
    if len(r0)==0:
        test_quantile=results['test_score'].quantile(q=0.99,interpolation='nearest')
        r0=results[(results['test_score']>test_quantile)]
        if len(r0)==0:
            r0=results[(results['test_score']>=test_quantile)]
    
        print("  #Warning: filtering parameter min_score for testing has been adjusted to",test_quantile)
    """

    """
    # 首选训练效果好的
    r0=results[(results['train_score']>=min_score) & (results['train_score']<1.0)]
    if len(r0)==0:
        r0_train=results[(results['train_score']>=results['test_score']) & results['train_score']<1.0]
        train_quantile=r0_train['train_score'].quantile(q=0.99,interpolation='nearest')
        r0=r0_train[(r0_train['train_score']>train_quantile)]
        if len(r0)==0:
            r0=r0_train[(r0_train['train_score']>=train_quantile)]
    
        print("  #Warning: filtering parameter min_score for training has been adjusted to",train_quantile)
    
    # 再选泛化效果好的
    r1=r0[(r0['spread']<=diff)]
    if len(r1)==0:
        spread_quantile=r0['spread'].quantile(q=0.05,interpolation='nearest')
        r1=r0[(r0['spread']<spread_quantile)]
        if len(r1)==0:
            r1=r0[(r0['spread']<=spread_quantile)]
    
        print("  #Warning: filtering parameter diff has been adjusted to",spread_quantile)
    """
    
    #优先查看泛化效果最优的结果：spread最小
    votes=min(votes,len(r1))
    r2=r1.sort_values(by=['spread','test_score'],ascending=[True,False]).head(votes)        
    #优先查看测试分数最高的结果：test_score最大
    r3=r2.sort_values(by=['test_score','spread'],ascending=[False,True])

    r3head=r3
    
    zhang=len(r3head[r3head['pred']==1])
    die=len(r3head[r3head['pred']==-1])
    
    decision='+'
    decision_text='HIGHER'
    if die != 0:
        if zhang >= die * 2.0: decision='2+'
        if zhang >= die * 3.0: decision='3+'
    
    if die > zhang: 
        decision='-'
        decision_text='LOWER'
        if zhang != 0:
            if die >= zhang * 2.0: decision='2-'
            if die >= zhang * 3.0: decision='3-'
    
    #if abs(zhang-die)/((zhang+die)/2) < 0.05: decision='?'
    if zhang==die: 
        decision='='
        decision_text='FLAT'

    if not printout: return decision,today_close,stoday

    print("  Model voting for stock price after "+str(ndays)+" trading days: Higher("+str(zhang)+'), Lower('+str(die)+')')
    print("  "+ticker_name(ticker,'stock')+': previously closed '+str(known_close)+' @ '+str(known_day))
    
    ndate=date_adjust(known_day,adjust=ndays)
    print("  Prediction to close at",decision_text,"price trend ("+decision+') @',ndate)
    
    return decision,known_close,known_day

    
#==============================================================================
if __name__=='__main__':
    ticker='600519.SS'
    ndays=1
    diff=0.01
    min_score=0.9
    votes=100
    max_neighbours=3
    max_RS=20
    preproctype='0-1'
    
    df=forecast_direction_knn(ticker,ndays=1)
    df=forecast_direction_knn(ticker,ndays=3)

def forecast_direction_knn(ticker,ndays=1,diff=0.01,min_score=0.9,votes=100,max_neighbours=10,max_RS=20,preproctype='0-1',end='latest'):

    """
    功能：基于个股资金流动预测未来股票涨跌方向，涨或跌
    ticker：股票代码，无后缀
    ndays：预测几天后的股价涨跌方向，默认1天
    diff：泛化精度，越小越好
    min_score：最小训练/学习分数
    votes：软表决票数，默认最大100
    max_neighbours：最大邻居个数，默认10个
    max_RS：最大随机数种子，默认最大为10
    """
    print("\nStart forecasting, it may take great time, please wait ...")
    
    #抓取个股资金净流入情况df和大盘指数情况dp
    df=get_money_flowin(ticker,end=end)
    
    #预测未来股价涨跌
    decisionlist=[]
    for nd in list(range(1,ndays+1)):
        decision,known_close,known_day=price_direction_knn(ticker,df,ndays=nd, \
                                                       diff=diff, \
                                                       min_score=min_score, \
                                                       votes=votes, \
                                                       max_neighbours=max_neighbours, \
                                                       max_RS=max_RS)
        decisionlist=decisionlist+[decision]

    print("\nStock information:",ticker_name(ticker,'stock'),'\b, closed',known_close,'@',known_day)
    for nd in list(range(1,ndays+1)):
        ndate=date_adjust(known_day, adjust=nd)
        print("Forecasting stock close price trend on",ndate,end=': ')
        pred=decisionlist[nd-1]
        if '-' in pred:
            print("LOWER,",pred)
        if '+' in pred:
            print("HIGHER,",pred)
        if '~' in pred:
            print("market closed")            
        if '=' in pred:
            print("least different")  
            
    return decisionlist,known_close,known_day


#==============================================================================
# Forecasting stock prices by money flow in/out, using knn
#==============================================================================

if __name__=='__main__':
    ticker='600519.SS'
    ticker='605011.SS'
    
    ndays=1
    diff=0.01
    min_score=0.8
    votes=100
    max_neighbours=10
    max_RS=10
    printout=True
    
    df=get_money_flowin(ticker,end='2023-6-15')
    pred_result=price_price_knn(ticker,df,ndays=1)
    pred_result=price_price_knn(ticker,df,ndays=3)

#def price_price_knn(ticker,df,ndays=1,diff=0.01,min_score=0.8,votes=100,max_neighbours=10,max_RS=20,printout=True):
def price_price_knn(ticker,df,ndays=1,max_neighbours=10,max_RS=20,printout=True):
    
    """
    功能：基于个股资金流动预测次日股票价格
    ticker：股票代码，无后缀
    df：个股资金净流入信息
    ndays：预测几天后的股价涨跌方向，默认1天
    diff：弃用。泛化精度，越小越好
    min_score：弃用。最小训练/测试分数，越大越好
    votes：弃用。软表决均值，默认100
    max_neighbours：最大邻居个数
    max_RS：最大随机数种子
    """
    import pandas as pd
 
    # 判断是否周末无交易免预测
    known_day=df.tail(1)['date'].values[0]
    
    tdate=date_adjust(known_day, adjust=ndays)
    tdate_pd=pd.to_datetime(tdate)
    tdate_wd=tdate_pd.weekday()
    if tdate_wd in [5,6]:
        print("  #Warning: after",ndays,"day(s) is",tdate,"(weekend), no trading")
        decision=0
        decision_score=0
        known_close=df.tail(1)['Close'].values[0]
        
        return decision,decision_score,known_close,known_day   
 
    #构造样本：标签ydf，特征矩阵X，预测X_new
    X,ydf,X_new=make_sample(df,ndays=ndays)
    
    known_day_np=X_new.index.values[0]
    known_day_pd=pd.to_datetime(known_day_np)    
    known_day=known_day_pd.strftime("%Y-%m-%d")
    known_close=X_new['Close'].values[0]    

    #建立样本：标签序列
    #y1=df2['nextDirection'] #二分类
    #y2=df2['nextChange%']   #回归
    y3=ydf['Close_next']      #回归

    #拆分训练集和测试集：y1
    from sklearn.model_selection import train_test_split
    #引入k近邻分类模型：
    from sklearn.neighbors import KNeighborsRegressor

    #寻找最优模型参数
    nlist=list(range(1,max_neighbours+1))
    n_num=len(nlist)
    wlist=['uniform','distance']
    mlist1=['braycurtis','canberra','correlation','dice','hamming','jaccard']
    mlist2=['kulsinski','matching','rogerstanimoto','russellrao']
    mlist3=['sokalmichener','sokalsneath','sqeuclidean','chebyshev']
    mlist4=['cityblock','euclidean','minkowski','cosine']
    mlist=mlist1+mlist2+mlist3+mlist4
    rslist=list(range(0,max_RS+1))
    
    results=pd.DataFrame(columns=('spread','train_score','test_score', \
                                  'neighbours','weight','metric','random','pred'))
    print('\nSearching for best parameters of knn model in',ndays,'trading days ...')
    print('  Progress: 0% ',end='')
    for n in nlist:
        for w in wlist:
            for m in mlist:
                for rs in rslist: 
                    try:
                        knn1=KNeighborsRegressor(n_neighbors=n,weights=w,metric=m,n_jobs=-1)
                        X_train,X_test,y_train,y_test=train_test_split(X,y3,random_state=rs)
                        tmp=knn1.fit(X_train, y_train)
                        train_score=round(knn1.score(X_train, y_train),3)
                        test_score=round(knn1.score(X_test, y_test),3)
                        prediction=knn1.predict(X_new)[0]
                    except:
                        #print("  #Bug parameters: n=",n,"w=",w,"m=",m,"rs=",rs)
                        #break
                        continue
                    spread=abs(round(train_score-test_score,3))
                    
                    row=pd.Series({'spread':spread,'train_score':train_score, \
                                   'test_score':test_score,'neighbours':n, \
                                   'weight':w,'metric':m,'random':rs,'pred':prediction})
                    try:
                        results=results.append(row,ignore_index=True)
                    except:
                        results=results._append(row,ignore_index=True)
                        
        print(int(n/n_num*100),'\b% ',end='')
    print('.') 
    
    # 过滤训练/测试分数差的结果
    """
    r0=results[(results['train_score']>=min_score) & (results['test_score']>=min_score)]
    
    # 如果最低分数设置太高
    r0_len=len(r0)
    if r0_len==0:
        train_score_max=results['train_score'].max()
        test_score_max=results['test_score'].max()
        min_score_new=min(train_score_max,test_score_max)
        r0=results[(results['train_score']>=min_score_new) & (results['test_score']>=min_score_new)]
        
        if len(r0)==0:
            spread_quantile=results['spread'].quantile(q=0.01)
            r0_spread=results[(results['spread']<spread_quantile)]
            if len(r0_spread)==0:
                r0_spread=results[(results['spread']<=spread_quantile)]

            test_score_quantile=r0_spread['test_score'].quantile(q=0.99)
            r0=r0_spread[(r0_spread['test_score']>test_score_quantile)]
            if len(r0)==0:
                r0=r0_spread[(r0_spread['test_score']>=test_score_quantile)]
                
            train_score_max=r0['train_score'].max()
            test_score_max=r0['test_score'].max()
            min_score_new=min(train_score_max,test_score_max)
            
        print("  #Warning: filtering parameter min_score has been adjusted to",min_score_new)        
    """
    
    train_score_max=results['train_score'].max()
    test_score_max=results['test_score'].max()
    min_score_new=min(train_score_max,test_score_max)
    r0=results[(results['train_score']>=min_score_new) & (results['test_score']>=min_score_new)]
    
    if len(r0)==0:
        spread_quantile=results['spread'].quantile(q=0.01)
        r0_spread=results[(results['spread']<spread_quantile)]
        if len(r0_spread)==0:
            r0_spread=results[(results['spread']<=spread_quantile)]

        test_score_quantile=r0_spread['test_score'].quantile(q=0.99)
        r0=r0_spread[(r0_spread['test_score']>test_score_quantile)]
        if len(r0)==0:
            r0=r0_spread[(r0_spread['test_score']>=test_score_quantile)]
            
        train_score_max=r0['train_score'].max()
        test_score_max=r0['test_score'].max()
        min_score_new=min(train_score_max,test_score_max)
    
    #去掉泛化效果差的结果
    """
    r1=r0[r0['spread'] <= diff]  #限定泛化差距
    r1_len=len(r1)
    
    if r1_len==0:
        diff_new=r0['spread'].min()
        r1=r0[r0['spread'] <= diff_new]
        print("  #Warning: filtering parameter diff has been adjusted to",diff_new)
    """
    
    diff_new=r0['spread'].min()
    r1=r0[r0['spread'] == diff_new]
    
    #优先查看泛化效果最优的结果：spread最小
    """
    votes=min(votes,len(r1))
    r2=r1.sort_values(by=['spread','test_score'],ascending=[True,False]).head(votes)        
    #优先查看测试分数最高的结果：test_score最大
    r3=r2.sort_values(by=['test_score','spread'],ascending=[False,True])
    """
    
    r3head=r1
    #平均股价
    decision=round(r3head['pred'].mean(),2)
    decision_score=round(r3head['test_score'].mean(),3)
    
    """
    r3head['w_pred']=r3head['pred'] * r3head['test_score']
    w_pred_sum=r3head['w_pred'].sum()
    test_score_sum=r3head['test_score'].sum()
    decision=round(w_pred_sum / test_score_sum,2)
    decision_score=round(r3head['test_score'].mean(),2)
    """
    """
    #股价中位数：偶尔出现奇怪的错误，未找到原因
    decision0=r3head['pred'].median()
    pos=list(r3head['pred']).index(decision0)
    decision_score0=list(r3head['test_score'])[pos]
    decision=round(decision0,2)
    decision_score=round(decision_score0,2)
    """
    import numpy as np
    if np.isnan(decision): decision='?'
    
    if not printout: return decision,decision_score,today_close,stoday

    print("  Model poll for stock price after "+str(ndays)+" trading days:",decision)
    print("  Last close price: "+ticker_name(ticker,'stock')+', closed '+str(known_close)+', '+str(known_day))
    
    ndate=date_adjust(known_day,adjust=ndays)
        
    print("  Prediction for stock close price on",ndate,"\b:",decision)
    
    return decision,decision_score,known_close,known_day

    
#==============================================================================
if __name__=='__main__':
    ticker='600519.SS'
    ndays=1
    max_neighbours=3
    max_RS=2
    
    forecast=forecast_price_knn(ticker,ndays=1,end='2023-6-15')
    forecast=forecast_price_knn(ticker,ndays=3,end='2023-6-15')

#def forecast_price_knn(ticker,ndays=1,diff=0.03,min_score=0.7,votes=100,max_neighbours=10,max_RS=10,end='latest'):
def forecast_price_knn(ticker,ndays=1,max_neighbours=10,max_RS=20,end='latest'):
    """
    功能：基于个股资金流动预测未来股票价格
    ticker：股票代码，无后缀
    ndays：预测几天后的股价，默认1天
    diff：弃用。泛化精度，越小越好
    min_score：弃用。最小训练/测试分数，越大越好
    votes：弃用。软表决均值，默认最大100
    max_neighbours：最大邻居个数，默认10个
    max_RS：最大随机数种子，越大越好
    
    注意：结果经常相当不靠谱！
    """
    print("\nStart forecasting, it may take great time, please wait ...")
    
    #抓取个股资金净流入情况df和大盘指数情况dp
    df=get_money_flowin(ticker,end=end)
    
    #预测未来股价涨跌
    decisionlist=[]
    confidencelist=[]
    for nd in list(range(1,ndays+1)):
        """
        decision,confidence,known_close,known_day=price_price_knn(ticker,df,ndays=nd, \
                                                              diff=diff, \
                                                              min_score=min_score, \
                                                              votes=votes, \
                                                              max_neighbours=max_neighbours, \
                                                              max_RS=max_RS)
        """
        decision,confidence,known_close,known_day=price_price_knn(ticker,df,ndays=nd, \
                                                              max_neighbours=max_neighbours, \
                                                              max_RS=max_RS)
        
        decisionlist=decisionlist+[decision]
        confidencelist=confidencelist+[confidence]

    print("\nStock information:",ticker_name(ticker,'stock'),'\b, closed',known_close,'@',known_day)

    for nd in list(range(1,ndays+1)):
        ndate=date_adjust(known_day, adjust=nd)
        pred=decisionlist[nd-1]  
        conf=confidencelist[nd-1]
        
        if (pred != 0) & (conf != 0):
            if pred != '?':
                diff=decision - known_close
                if abs(diff) < 0.05:
                    comment="MINOR difference with previous one"
                elif diff > 0:
                    comment="HIGHER than previous one"
                else:
                    comment="LOWER than previous one"
                
                print("Forecasting stock prices on",ndate,'\b:',pred,'('+str(round(conf*100,1))+'% confident)')
                print("Forecasting stock prices trend on",ndate,'\b:',comment)
            else:
                print("Forecasting stock prices on",ndate,'\b: uncertain')
        else:
            print("Forecasting stock prices on",ndate,'\b: market closed')
    
    return decisionlist,confidencelist


#==============================================================================
#==============================================================================
#==============================================================================
if __name__=='__main__':
    mid_symbol=['；','。']
    mid_symbol=['。','；']
    longtext="姓名；年龄；职业；职称。"
    print_sentence(longtext,mid_symbol='；')
    
    longtext="姓名。年龄。职业。职称。"
    print_sentence(longtext,mid_symbol='。')

def print_sentence(longtext,mid_symbol=['；','。']):
    """
    功能：将长文本分句打印，间隔符号为mid_symbol
    """
    symbol=mid_symbol[0]
    try:
        sentenceList=longtext.split(symbol)
        sentenceList.remove('')
    except:
        pass

    if len(sentenceList) == 1:
        symbol=mid_symbol[1]
        try:
            sentenceList=longtext.split(symbol)
        except:
            pass
            print("  #Error(print_sentence): middle symbol",mid_symbol,"not found in the text")
            return

    for s in sentenceList:
        
        if s == '':
            continue
        
        pos=sentenceList.index(s)
        
        if not (s[-1:]=='。'):
            s1=s+symbol
        else:
            s1=s
            
        print(s1)
            
    return
    
#==============================================================================
if __name__ =="__main__":
    ticker='000001.SZ'
    ticker='600519.SS'
    ticker='01398.HK'
    ticker='300750.SZ'

    category='shareholder'
    business_period='annual'

    financial_quarters=8
    start='2020-1-1'
    facecolor='papayawhip'
    
    prettytab=True
    tabborder=False
    tabborder=True
    
    stock_profile_china(ticker,category='profile')
    stock_profile_china(ticker,category='profile',business_period='annual')

def stock_profile_china(ticker,category='profile', \
                        business_period='recent', \
                        financial_quarters=8, \
                        start='2020-1-1', \
                            
                        #参数prettytab和tabborder弃用，保留只为了兼容性
                        prettytab=False, \
                        tabborder=False, \
                        
                        loc1='upper left',loc2='upper right', \
                        facecolor='papayawhip',font_size='16px'):
    """
    功能：介绍中国A股的主要信息，包括公司基本信息、主营信息、股东信息、财务信息、分红历史和市场估值等。
    ticker：A股股票代码
    category：信息类别，默认profile为基本信息，business为主营业务信息，shareholder为股东信息，
    financial为财务基本面，dividend为分红历史，valuation为市场估值信息。
    
    business_period：配合category='business'使用，介绍主营业务使用的财报期间，
    默认recent为最近一期（可能为季报、中报或年报），annual为使用最近的年报。
    
    financial_quarters：配合category='financial'使用，介绍财务基本面使用的季度个数，最大为8.
    start：配合category='valuation'或'dividend'使用，介绍估值/分红信息的开始日期，默认为2020-1-1。
    
    prettytab：输出表格样式，默认False使用markdown报表，True使用prettytable报表
    tabborder：prettytable报表时是否绘制边框，默认不绘制False，True绘制简单字符链接的边框，丑陋。
    
    返回值：无。
    建议运行环境：Anaconda Jupyter Notebook，其他环境未测试。
    """
    DEBUG=False
    
    #检查是否A股
    _,prefix,suffix=split_prefix_suffix(ticker)
    if not (suffix.upper() in ['SS','SZ','BJ']):
        print("  #Warning(stock_profile_china): not a stock in China for",ticker)
        return
    
    if suffix.upper() in ['SS','SH']:
        sx='SH'
    elif suffix.upper() in ['SZ']:
        sx='SZ'
    else:
        sx='BJ'
    sxticker=sx+prefix
    
    categorylist=['profile','business','shareholder','financial','dividend','valuation']
    if not (category in categorylist):
        print("  #Error(stock_detail_china): unsupported category",category)
        print("  Supported category:",categorylist)
        return
    
    ticker1=ticker[:6]
    from datetime import datetime
    
    import datetime as dt
    stoday=str(dt.date.today())
    
    yi=100000000.0
    yiyuan_name='(亿元)'
    yigu_name='(亿股)'
    
    baiwan=1000000.0
    wan=10000.0
    
    #确定表格字体大小
    titile_font_size=font_size
    heading_font_size=data_font_size=str(int(font_size.replace('px',''))-1)+'px'
    heading_font_size_small=data_font_size_small=str(int(font_size.replace('px',''))-3)+'px'

    import akshare as ak
    # 个股基本信息======================================================================================
    if any(s in category for s in ['profile','basic']): #判断category中是否包含任意子串
        
        # 个股基本信息查询1=============================================================================        
        try:
            df6=ak.stock_profile_cninfo(symbol=ticker1)  
        except:
            print("  #Warning(stock_profile_china): profile info not found or inaccessible for",ticker1)
            return
    
        # 整理信息
        dftmp=df6.copy(deep=True)
        delColList=['入选指数','办公地址','主营业务','经营范围','机构简介']
        dftmp.drop(delColList,axis=1,inplace=True)
        
        dftmp['注册资金(亿元)']=int(dftmp['注册资金'] / wan)
        newColList=['公司名称','英文名称','曾用简称','A股代码','A股简称','B股代码','B股简称','H股代码','H股简称', \
                    '所属市场','所属行业','法人代表','注册资金(亿元)','成立日期','上市日期','官方网站','电子邮箱', \
                    '联系电话','传真','注册地址','邮政编码']
        dftmp1=dftmp[newColList]
        
        dftmp2=dftmp1.T
        dftmp2.dropna(inplace=True)
        dftmp2['项目']=dftmp2.index
        dftmp2['内容']=dftmp2[0]
        dftmp3=dftmp2[['项目','内容']]
        
        dftmp3.reset_index(drop=True,inplace=True)
        
        # 个股基本信息查询2=============================================================================
        try:
            df1=ak.stock_individual_info_em(symbol=ticker1)  
        except:
            print("  #Warning(stock_profile_china): invalid code for",ticker)
            return
    
        # 整理信息
        dftmpb=df1.copy(deep=True)
        for i in range(0, len(dftmpb)): 
            item=dftmpb.iloc[i]['item'].strip()
            value=dftmpb.iloc[i]['value']
            #print(item,value)
            
            if item in ["总市值","流通市值"]:
                dftmpb.iloc[i]['value']=round(value / yi,4)
                dftmpb.iloc[i]['item']=item+yiyuan_name
            
            if item in ["总股本","流通股"]:
                dftmpb.iloc[i]['value']=round(value / yi,4)
                dftmpb.iloc[i]['item']=item+yigu_name
            
            if item in ["上市时间"]:
                dtdate=datetime.strptime(str(value),'%Y%m%d')
                dftmpb.iloc[i]['value']=dtdate.strftime('%Y-%m-%d')
        dftmpb.rename(columns={'item':'项目','value':'内容'},inplace=True)
        
        #合并
        import pandas as pd
        dftmp12=pd.concat([dftmp3,dftmpb])
        dftmp12.reset_index(drop=True,inplace=True) 
        dftmp12.set_index('项目',inplace=True)
        
        dftmp13=dftmp12.T
        try:
            newCols=['股票代码','股票简称','曾用简称','所属市场','所属行业', \
                     '上市日期','流通股(亿股)','流通市值(亿元)','总股本(亿股)','总市值(亿元)', \
                     '公司名称','英文名称','成立日期','注册资金(亿元)','法人代表', \
                     '注册地址','邮政编码','联系电话','传真','官方网站','电子邮箱']
            dftmp14=dftmp13[newCols]   
        except:
            newCols=['股票代码','股票简称','所属市场','所属行业', \
                     '上市日期','流通股(亿股)','流通市值(亿元)','总股本(亿股)','总市值(亿元)', \
                     '公司名称','英文名称','成立日期','注册资金(亿元)','法人代表', \
                     '注册地址','邮政编码','联系电话','传真','官方网站','电子邮箱']
            dftmp14=dftmp13[newCols]   
            
        dftmp15=dftmp14.T
        dftmp15.reset_index(inplace=True)
              
        titletxt=ticker_name(ticker,'stock')
        """
        if prettytab:
            pandas2prettytable(dftmp15,titletxt,firstColSpecial=False,leftColAlign='l',otherColAlign='l',tabborder=tabborder)
            print(' ','数据来源：巨潮资讯,',str(today))
        else:
            print('\n*** '+titletxt+'\n')
            print(dftmp15.to_markdown(tablefmt='Simple',index=False,colalign=['left']))
            print('\n数据来源：巨潮资讯,',str(today))
        """
        titletxt1=titletxt+"：基本信息"
        footnote='数据来源：巨潮资讯，'+str(stoday)
        df_display_CSS(df=dftmp15,titletxt=titletxt1,footnote=footnote, \
                       facecolor=facecolor,decimals=2,last_col_align='left', \
                       titile_font_size=titile_font_size,heading_font_size=heading_font_size, \
                       data_font_size=data_font_size)        
        
        print(' ')
        print("*****",titletxt+"：业务范围")
        longtext=df6.iloc[0]["主营业务"]
        print_sentence(longtext,mid_symbol=['；','。'])
            
        print("\n*****",titletxt+"：经营范围")
        longtext=df6.iloc[0]["经营范围"]
        print_sentence(longtext,mid_symbol=['；','。'])
            
        print("\n*****",titletxt+"：机构简介")
        longtext=df6.iloc[0]["机构简介"]
        print_sentence(longtext,mid_symbol=['；','。'])

    # 主营业务信息查询=============================================================================
    # 主营业务仅在年报/中报中公布，一三季报中无此信息
    import numpy as np
    if category == 'business':
        try:
            df2=ak.stock_zygc_em(symbol=sxticker)  
        except:
            print("  #Warning(stock_profile_china): fetching business info failed for",ticker)
            return
        
        df2['分类类型']=df2['分类类型'].apply(lambda x: '按业务分类' if x in [np.nan,None] else x)
        df2['报告日期']=df2['报告日期'].apply(lambda x: x.strftime("%Y-%m-%d"))
        # 整理信息
        df2['报告年度']=df2['报告日期'].apply(lambda x: x[:4])
        df2['报告月日']=df2['报告日期'].apply(lambda x: x[-5:])
        df2['报告类别']=df2['报告月日'].apply(lambda x: '年度' if x=='12-31' else '中期' if x=='06-30' else '季度')
        
        if business_period in ['annual','recent']:
            if business_period == 'annual':    #最近一期年报
                df2a=df2[df2['报告类别']=='年度'].copy(deep=True)
                df2a.reset_index(drop=True,inplace=True)
            if business_period == 'recent':    #最近一期年报/中报
                df2a=df2.copy(deep=True)

            period=df2a.head(1)['报告日期'][0]
        else:   #具体中报或年报日期
            result,business_period1=check_date2(business_period)
            if result:
                df2a=df2[df2['报告日期']==business_period1].copy(deep=True)
                if len(df2a) > 0:
                    df2a.reset_index(drop=True,inplace=True)
                    period=df2a.head(1)['报告日期'][0]
                else:
                    print("  #Warning(stock_profile_china): invalid business period for",business_period)
                    print("  Valid business_period: annual, recent, or an valid mid-term/annual report date, eg 2022-12-31 or 2022-6-30")
                    return
            else:
                print("  #Warning(stock_profile_china): invalid business period for",business_period)
                print("  Valid business_period: annual, recent, or an valid mid-term/annual report date, eg 2022-12-31 or 2022-6-30")
                return
            
        dftmp=df2[df2['报告日期']==period]
        cols1=['主营构成','主营收入','收入比例','主营成本','成本比例','主营利润','利润比例','毛利率']
        #cols2=['分类方向','分类','营业收入-同比增长','营业成本-同比增长','毛利率','毛利率-同比增长']
        
        for c in cols1:
            if c in ['主营收入','主营成本','主营利润']:
                dftmp[c]=dftmp[c].apply(lambda x: round(x/yi,2))
            if c in ['收入比例','成本比例','利润比例','毛利率']:
                dftmp[c]=dftmp[c].apply(lambda x: round(x*100,2))
                dftmp.rename(columns={c:c+'%'},inplace=True)
        
        cols1p=['主营构成','主营收入','收入比例%','主营成本','成本比例%','主营利润','利润比例%','毛利率%']
        dftmp1a=dftmp[dftmp['分类类型']=='按业务分类'][cols1p]        
        dftmp1b=dftmp[dftmp['分类类型']=='按地区分类'][cols1p]        
        
        titletxt1a=ticker_name(ticker,'stock')+'：主营业务构成，按业务分类，单位：亿元，'+period
        titletxt1b=ticker_name(ticker,'stock')+'：主营业务构成，按地区分类，单位：亿元，'+period
        """
        if prettytab:
            pandas2prettytable(dftmp1,titletxt1,firstColSpecial=True,leftColAlign='l',otherColAlign='c',tabborder=tabborder)
            print(' ','数据来源：益盟-F10,',str(today))
        else:
            print('\n*** '+titletxt1+'\n')
            print(dftmp1.to_markdown(tablefmt='Simple',index=False,colalign=['left','left','right','right','right','right','right']))
            print('\n数据来源：益盟-F10,',str(today))
        """
        footnote=''
        df_display_CSS(df=dftmp1a,titletxt=titletxt1a,footnote=footnote, \
                       first_col_align='left',second_col_align='right', \
                           facecolor=facecolor,decimals=2, \
                           titile_font_size=titile_font_size,heading_font_size=heading_font_size, \
                           data_font_size=data_font_size)

        print('')
        footnote='数据来源：东方财富，'+str(stoday)
        df_display_CSS(df=dftmp1b,titletxt=titletxt1b,footnote=footnote, \
                       first_col_align='left',second_col_align='right', \
                           facecolor=facecolor,decimals=2, \
                           titile_font_size=titile_font_size,heading_font_size=heading_font_size, \
                           data_font_size=data_font_size)

        #dftmp2=dftmp[cols2]        
        #titletxt2=ticker_name(ticker,'stock')+'：主营业务增长，'+period
        """
        if prettytab:
            pandas2prettytable(dftmp2,titletxt2,firstColSpecial=True,leftColAlign='l',otherColAlign='c',tabborder=tabborder)
            print(' ','数据来源：益盟-F10,',str(today))
        else:
            print('\n*** '+titletxt2+'\n')
            print(dftmp2.to_markdown(tablefmt='Simple',index=False,colalign=['left','left','right','right','right','right']))
            print('\n数据来源：益盟-F10,',str(today))
        """
        """
        df_display_CSS(df=dftmp2,titletxt=titletxt2,footnote=footnote, \
                       first_col_align='left',second_col_align='left', \
                           facecolor=facecolor,decimals=2, \
                           titile_font_size=titile_font_size,heading_font_size=heading_font_size, \
                           data_font_size=data_font_size)
        """
    # 历史分红信息查询=============================================================================
    """
    if category == 'dividend':
        try:
            df3=ak.stock_dividents_cninfo(symbol=ticker1)  
        except:
            try:
                # 测试是否akshare本身出现问题
                tmpdf3=ak.stock_dividents_cninfo(symbol='600519')
            except:
                # akshare本身出现问题
                print("  #Warning(stock_profile_china): problem incurred for akshare")
                print("  Try upgrade akshare using: pip install akshare --upgrade")
                print("  If same problem remains, try upgrade akshare again later")
                return
            print("  #Warning(stock_profile_china): dividend info not found for",ticker)
            return
    
        # 整理信息
        df3.fillna('',inplace=True)
        dftmp=df3.copy(deep=True)
        dftmp.drop(['实施方案公告日期','股份到账日'],axis=1,inplace=True)
        #del dftmp['分红类型']
        #del dftmp['报告时间']
        #dftmp.drop(['送股比例','转增比例','派息比例'],axis=1,inplace=True)
        
        newcols=['报告时间','送股比例','转增比例','派息比例','股权登记日','除权日','派息日','实施方案分红说明']
        dftmp1=dftmp[newcols]
        
        # 替换送转派息字段中的零为空，全局替换
        dftmp2=dftmp1.replace(0,'')
        dftmp3=dftmp2.replace('','--')

        titletxt=ticker_name(ticker)+'：股利发放历史'
        if prettytab:
            pandas2prettytable(dftmp3,titletxt,firstColSpecial=False,leftColAlign='l',otherColAlign='c',tabborder=tabborder)
            print(' ','数据来源：巨潮资讯,',str(today))
        else:
            print('\n*** '+titletxt+'\n')
            print(dftmp3.to_markdown(tablefmt='Simple',index=False,colalign=['left','center','center','right','center','center','center','left']))
            print('\n数据来源：巨潮资讯,',str(today))
    """
    #if category in ['dividend','split']:
    if any(s in category for s in ['dividend','split']):
        tickername=ticker_name(ticker,'stock')
        # 分红
        titletxt=tickername+'：分红历史'
        try:
            #df3=ak.stock_dividents_cninfo(symbol=ticker1) 
            df3=ak.stock_history_dividend_detail(symbol=ticker1, indicator="分红")
        except:
            print('')
            """
            print(titletxt)
            print("  #Warning(stock_profile_china): dividend info not found for stock",ticker)
            """
            print(f"  {tickername}：no dividend info found after {start}")
            return
        
        if len(df3)==0:
            """
            print('')
            print(titletxt)
            print("  No dividend record found for stock",ticker)
            """
            print(f"  {tickername}：no dividend info found after {start}")
            return
    
        # 整理信息
        dftmp=df3[df3['进度']=='实施']
        #dftmp.drop(['进度','红股上市日'],axis=1,inplace=True)
        dftmp.drop(['进度'],axis=1,inplace=True)
        dftmp.replace(0,'-',inplace=True)
        import numpy as np
        dftmp.replace(np.nan,'-',inplace=True)
        
        newcols=['公告日期','送股','转增','派息','股权登记日','除权除息日','红股上市日']
        dftmp3=dftmp[newcols]
        
        import pandas as pd
        startpd=pd.Timestamp(start)        
        dftmp4=dftmp3[dftmp3['公告日期'] >= startpd.date()]
        
        if len(dftmp4) == 0:      
            print(f"  {tickername}：no dividend info found after {start}")
        else:
            titletxt=ticker_name(ticker,'stock')+': '+text_lang('分红历史','Dividend History')
            """
            if prettytab:
                pandas2prettytable(dftmp3,titletxt,firstColSpecial=False,leftColAlign='l',otherColAlign='c',tabborder=tabborder)
                print('【注】送股/转增：股数/10股，派息：元(税前)/10股，数据来源：新浪财经,',str(today))
            else:
                print('\n*** '+titletxt+'\n')
                alignlist=['center']+['right']*(len(list(dftmp3))-1)
                print(dftmp3.to_markdown(tablefmt='Simple',index=False,colalign=alignlist))
                print('【注】送股/转增：股数/10股，派息：元(税前)/10股，数据来源：新浪财经,',str(today))
            """
            footnotecn='【注】送股/转增：股数/10股，派息(元，税前)/10股，数据来源：新浪财经，'+str(stoday)
            footnoteen='[Note]Stock div/capitalization/cash div(RMB, pre-tax) per 10 shares, data source: Sina Finance, '+str(stoday)
            footnote=text_lang(footnotecn,footnoteen)
            
            if check_language() == 'English':
                dftmp4.rename(columns={'公告日期':'Disclosure','送股':'Stock Div', \
                                       '转增':'Capitalization','派息':'Cash Div', \
                                       '股权登记日':'Record','除权除息日':'Ex-Dividend', \
                                       '红股上市日':'Stock Div Listing'},inplace=True)
            
            df_display_CSS(df=dftmp4,titletxt=titletxt,footnote=footnote, \
                           first_col_align='center',second_col_align='center', \
                           last_col_align='center',other_col_align='center', \

                           facecolor=facecolor,decimals=2, \
                           titile_font_size=titile_font_size,heading_font_size=heading_font_size, \
                           data_font_size=data_font_size)
            
        # 配股
        titletxt=ticker_name(ticker,'stock')+': '+text_lang('配股历史','Rights Issue History')
        try:
            df3p=ak.stock_history_dividend_detail(symbol=ticker1, indicator="配股")
        except:
            """
            print('')
            print(titletxt)
            print("  #Warning(stock_profile_china): allotment info not found for stock",ticker)
            """
            #print(f"\n  {tickername}：{start}后未找到配股信息")
            return
        
        if len(df3p)==0:
            """
            print('')
            print(titletxt)
            print("  #Warning(stock_profile_china): no allotment info found for stock",ticker)
            """
            #print(f"\n  {tickername}：{start}后未找到配股信息")
            return
    
        # 整理信息
        dftmp=df3p[df3p['基准股本']!=0]
        dftmp.drop(['基准股本','募集资金合计'],axis=1,inplace=True)
        
        newcols=['公告日期','配股方案','配股价格','股权登记日','除权日','缴款起始日','缴款终止日','配股上市日']
        dftmp3=dftmp[newcols]
        
        dftmp4=dftmp3[dftmp3['公告日期'] >= startpd.date()]
        if len(dftmp4) == 0:      
            #print(f"\n  {tickername}：{start}后未找到配股信息")
            return
        else:
            """
            if prettytab:
                pandas2prettytable(dftmp3,titletxt,firstColSpecial=False,leftColAlign='l',otherColAlign='c',tabborder=tabborder)
                print('【注】配股方案：每10股的配股数，配股价格为元。数据来源：新浪财经,',str(today))
            else:
                print('\n*** '+titletxt+'\n')
                alignlist=['center']+['right']*(len(list(dftmp3))-1)
                print(dftmp3.to_markdown(tablefmt='Simple',index=False,colalign=alignlist))
                print('【注】配股方案：每10股的配股数，配股价格为元。数据来源：新浪财经,',str(today))
            """
            footnotecn='【注】配股方案：每10股的配股数，配股价格为元。数据来源：新浪财经，'+str(stoday)
            footnoteen='Rights issue ratio: per 10 shares, subscription price in RMB, data source: Sina Finance, '+str(stoday)
            footnote=text_lang(footnotecn,footnoteen)
            
            if check_language() == 'English':
                dftmp4.rename(columns={'公告日期':'Disclosure','配股方案':'Rights Issue Ratio', \
                                       '配股价格':'Subscription Price','股权登记日':'Record', \
                                       '除权日':'Ex-Rights','缴款起始日':'Subscription Start', \
                                       '缴款终止日':'Subscription End','配股上市日':'Rights Listing'},inplace=True)
            
            df_display_CSS(df=dftmp4,titletxt=titletxt,footnote=footnote, \
                           first_col_align='center',second_col_align='center', \
                           last_col_align='center',other_col_align='center', \

                           facecolor=facecolor,decimals=2, \
                           titile_font_size=titile_font_size,heading_font_size=heading_font_size, \
                           data_font_size=data_font_size)
        

    # 主要股东信息查询=============================================================================
    #if category in ['shareholder','investor']:
    if any(s in category for s in ['shareholder','investor']):
        try:
            df4init=ak.stock_main_stock_holder(stock=ticker1)  
        except:
            print("  #Warning(stock_profile_china): shareholder info not found for",ticker)
            return
    
        # 整理信息
        # 如果最新日期的持股比例存在缺失值，宁可取次新日期。
        # 否则，若出现某机构排名前几名但持股比例缺失，则难以解释
        df4a1_10=df4init.head(10)
        if df4a1_10['持股比例'].isna().any():
            df4 = df4init.iloc[10:20]
        else:
            df4 = df4a1_10   
        
        df4.fillna(0,inplace=True)
        
        #df4['报告年度']=df4['截至日期'].apply(lambda x: x.year)
        df4['报告年度']=df4['截至日期'].apply(lambda x: x.strftime("%Y"))
        df4['报告月日']=df4['截至日期'].apply(lambda x: x.strftime("%m-%d"))
        df4['报告类别']=df4['报告月日'].apply(lambda x: '年度' if x=='12-31' else '中期' if x=='06-30' else '季度')
        
        if business_period in ['annual','recent']:
            if business_period == 'annual':    #最近一期年报
                df4a=df4[df4['报告类别']=='年度'].copy(deep=True)
                df4a.reset_index(drop=True,inplace=True)
            if business_period == 'recent':    #最近一期年报/中报
                df4a=df4.copy(deep=True)

            #period=df4a.head(1)['截至日期'][0]
            period=df4a.head(1)['截至日期'].values[0]
        else:   #具体财报日期
            result,business_period1=check_date2(business_period)
            if result:
                # 转换为字符串类型，否则比较失败
                df4['截至日期1']=df4['截至日期'].apply(lambda x:str(x))
                df4a=df4[df4['截至日期1']==business_period1].copy(deep=True)
                if len(df4a) > 0:
                    df4a.reset_index(drop=True,inplace=True)
                    period=df4a.head(1)['截至日期'][0]
                else:
                    print("  #Warning(stock_profile_china): invalid business period for",business_period)
                    print("  Valid business_period: annual, recent, or an valid mid-term/annual report date, eg 2022-12-31")
                    return
            else:
                print("  #Warning(stock_profile_china): invalid business period for",business_period)
                print("  Valid business_period: annual, recent, or an valid mid-term/annual report date, eg 2022-6-30")
                return
        
        #df4b=df4a[df4a['持股比例'] != 0]
        #df4a['持股比例'].replace(0,'unknown',inplace=True)
        #df4a['持股比例'].replace(0,'?',inplace=True)
        df4a['持股比例'].replace(0,'--',inplace=True)
        dftmp=df4a.head(10).copy(deep=True)
        
        enddate=str(dftmp.head(1)['截至日期'].values[0])
        titletxt=ticker_name(ticker,'stock')+'：十大股东（截至'+str(enddate)
        shareholder_num=dftmp.head(1)['股东总数'].values[0]
        if int(shareholder_num) > 0:
            titletxt=titletxt + '，股东总数'+str(int(shareholder_num))
        
        avg_shares=dftmp.head(1)['平均持股数'].values[0]
        if int(avg_shares) > 0:
            titletxt=titletxt + '，平均持股数'+str(int(avg_shares))
        
        titletxt=titletxt + '）'
        #titletxt=ticker_name(ticker,'stock')+'：十大股东（截至'+str(enddate)+'，股东总数'+str(int(shareholder_num))+'，平均持股数'+str(int(avg_shares))+'）'
        
        dftmp.drop(['截至日期','公告日期','股东说明','股东总数','平均持股数'],axis=1,inplace=True)
        
        #dftmp['持股数量(股)']=dftmp['持股数量(股)'].apply(lambda x: mstring2number(x))
        #dftmp['持股数量']=dftmp['持股数量'].apply(lambda x: mstring2number(x))
        dftmp['持股数量']=dftmp['持股数量'].apply(lambda x: float(x))
        #dftmp['持股数量(百万股)']=dftmp['持股数量(股)'].apply(lambda x: round(x / baiwan,2))
        dftmp['持股数量(百万股)']=dftmp['持股数量'].apply(lambda x: round(x / baiwan,2))
        
        #dftmp['持股比例(%)']=dftmp['持股比例'].apply(lambda x: mstring2number(x,'float'))
        dftmp['持股比例(%)']=dftmp['持股比例']
        
        # 检查持股比例是否异常
        check_holding=dftmp.head(1)['持股比例'].values[0]
        if check_holding ==0.0:
            print("  #Warning(stock_profile_china): shareholder holding info seems weired")
            dftmp=dftmp.replace(0,'---')
        
        #newcols=['编号','股东名称','股本性质','持股比例(%)','持股数量(百万股)']
        newcols=['编号','股东名称','股本性质','持股比例(%)']
        dftmp1=dftmp[newcols]        
        """
        if prettytab:
            pandas2prettytable(dftmp1,titletxt,firstColSpecial=False,leftColAlign='c',otherColAlign='c',tabborder=tabborder)
            print(' ','数据来源：新浪财经,',str(today))
        else:
            print('\n*** '+titletxt+'\n')
            #print(dftmp1.to_markdown(tablefmt='Simple',index=False,colalign=['center','left','left','right','right']))
            print(dftmp1.to_markdown(tablefmt='Simple',index=False,colalign=['center','left','left','right']))
            print('\n数据来源：新浪财经,',str(today))
        """
        footnote='数据来源：新浪财经，'+str(stoday)
        df_display_CSS(df=dftmp1,titletxt=titletxt,footnote=footnote, \
                       first_col_align='center',second_col_align='left', \
                       facecolor=facecolor,decimals=2, \
                       titile_font_size=titile_font_size,heading_font_size=heading_font_size, \
                       data_font_size=data_font_size)
        

    # 主要市场指标查询=============================================================================
    #if category == 'valuation':
    if any(s in category for s in ['valuation','market']):
        try:
            #df5=ak.stock_a_lg_indicator(symbol=ticker1)  
            df5=ak.stock_a_indicator_lg(symbol=ticker1)  
        except:
            print("  #Warning(stock_profile_china): valuation spyder failed or info not found for",ticker)
            return
    
        # 整理信息
        import pandas as pd
        #startpd=pd.to_datetime(start)
        startpd=pd.Timestamp(start)
        
        dftmp=df5.copy(deep=True)
        dftmp1=dftmp.set_index('trade_date')
        dftmp2=dftmp1[dftmp1.index >= startpd.date()]
        
        # 总市值转换为亿元
        dftmp2['total_mv(yi)']=dftmp2['total_mv'] / wan    #原单位为万元
        
        # 计算总市值的均值，中位数、最大最小值
        mv_mean=round(dftmp2['total_mv(yi)'].mean(),1)
        mv_median=round(dftmp2['total_mv(yi)'].median(),1)
        mv_max=round(dftmp2['total_mv(yi)'].max(),1)
        mv_min=round(dftmp2['total_mv(yi)'].min(),1)
        mv_txt="总市值(亿元)："+str(mv_min)+'-'+str(mv_max)+"，均值"+str(mv_mean)+"，中位数"+str(mv_median)
        
        titletxt=ticker_name(ticker,'stock')+'：估值与市值'
        import datetime as dt
        today=dt.date.today()
        footnote3="数据来源：乐咕乐股，"+str(stoday)
        
        # 计算市盈率的均值，中位数、最大最小值
        #va='pe'; va_name="市盈率"
        va='pe_ttm'; va_name="市盈率TTM"
        va_mean=round(dftmp2[va].mean(),1)
        va_median=round(dftmp2[va].median(),1)
        va_max=round(dftmp2[va].max(),1)
        va_min=round(dftmp2[va].min(),1)
        va_txt=va_name+"："+str(va_min)+'-'+str(va_max)+"，均值"+str(va_mean)+"，中位数"+str(va_median)
        
        footnote=va_txt+"；"+mv_txt+"\n"+footnote3
        
        # 市盈率与总市值
        if DEBUG:
            display(dftmp2)
        """
        plot2_line2(df1=dftmp2,ticker1='',colname1=va,label1=va_name, \
                    df2=dftmp2,ticker2='',colname2='total_mv(yi)',label2='总市值(亿元)', \
                    ylabeltxt='',titletxt=titletxt,footnote=footnote, \
                    date_range=True,date_freq='Q',date_fmt='%Y-%m',twinx=True, \
                    resample_freq='D', \
                    loc1=loc1,loc2=loc2, \
                    color1='red',color2='blue',facecolor=facecolor)
        """
        plot_line2(df1=dftmp2,ticker1='',colname1=va,label1=va_name, \
                   df2=dftmp2,ticker2='',colname2='total_mv(yi)',label2='总市值(亿元)', \
                   ylabeltxt='',titletxt=titletxt,footnote=footnote, \
                   twinx=True, \
                   resample_freq='D',loc1=loc1,loc2=loc2, \
                   color1='red',color2='blue',facecolor='whitesmoke')   
        
        # 计算市净率的均值，中位数、最大最小值
        va='pb'; va_name="市净率"
        va_mean=round(dftmp2[va].mean(),1)
        va_median=round(dftmp2[va].median(),1)
        va_max=round(dftmp2[va].max(),1)
        va_min=round(dftmp2[va].min(),1)
        va_txt=va_name+"："+str(va_min)+'-'+str(va_max)+"，均值"+str(va_mean)+"，中位数"+str(va_median)
        
        footnote=va_txt+"；"+mv_txt+"\n"+footnote3
        
        # 市净率与总市值
        """
        plot2_line2(dftmp2,'',va,va_name, \
                       dftmp2,'','total_mv(yi)','总市值(亿元)', \
                       '',titletxt,footnote, \
                       date_range=True,date_freq='Q',date_fmt='%Y-%m',twinx=True, \
                       resample_freq='D',loc1=loc1,loc2=loc2, \
                       color1='red',color2='blue',facecolor=facecolor)
        """
        plot_line2(df1=dftmp2,ticker1='',colname1=va,label1=va_name, \
                   df2=dftmp2,ticker2='',colname2='total_mv(yi)',label2='总市值(亿元)', \
                   ylabeltxt='',titletxt=titletxt,footnote=footnote, \
                   twinx=True, \
                   resample_freq='D',loc1=loc1,loc2=loc2, \
                   color1='red',color2='blue',facecolor='whitesmoke')   
            
        # 计算市销率的均值，中位数、最大最小值
        va='ps_ttm'; va_name="市销率TTM"
        va_mean=round(dftmp2[va].mean(),1)
        va_median=round(dftmp2[va].median(),1)
        va_max=round(dftmp2[va].max(),1)
        va_min=round(dftmp2[va].min(),1)
        va_txt=va_name+"："+str(va_min)+'-'+str(va_max)+"，均值"+str(va_mean)+"，中位数"+str(va_median)
        
        footnote=va_txt+"；"+mv_txt+"\n"+footnote3
        
        # 市销率与总市值
        """
        plot2_line2(dftmp2,'',va,va_name, \
                       dftmp2,'','total_mv(yi)','总市值(亿元)', \
                       '',titletxt,footnote, \
                       date_range=True,date_freq='Q',date_fmt='%Y-%m',twinx=True, \
                       resample_freq='D',loc1=loc1,loc2=loc2, \
                       color1='red',color2='blue',facecolor=facecolor)
        """
        plot_line2(df1=dftmp2,ticker1='',colname1=va,label1=va_name, \
                   df2=dftmp2,ticker2='',colname2='total_mv(yi)',label2='总市值(亿元)', \
                   ylabeltxt='',titletxt=titletxt,footnote=footnote, \
                   twinx=True, \
                   resample_freq='D',loc1=loc1,loc2=loc2, \
                   color1='red',color2='blue',facecolor='whitesmoke')           
        
        # 计算股息率的均值，中位数、最大最小值
        #va='dv_ratio'; va_name="股息率"
        va='dv_ttm'; va_name="股息率TTM"
        va_mean=round(dftmp2[va].mean(),1)
        va_median=round(dftmp2[va].median(),1)
        va_max=round(dftmp2[va].max(),1)
        va_min=round(dftmp2[va].min(),1)
        va_txt=va_name+"%："+str(va_min)+'-'+str(va_max)+"，均值"+str(va_mean)+"，中位数"+str(va_median)
        
        footnote=va_txt+"；"+mv_txt+"\n"+footnote3
        
        # 股息率与总市值
        """
        plot2_line2(dftmp2,'',va,va_name+'%', \
                       dftmp2,'','total_mv(yi)','总市值(亿元)', \
                       '',titletxt,footnote, \
                       date_range=True,date_freq='Q',date_fmt='%Y-%m',twinx=True, \
                       loc1=loc1,loc2=loc2, \
                       color1='red',color2='blue',facecolor=facecolor)
        """
        plot_line2(df1=dftmp2,ticker1='',colname1=va,label1=va_name+'%', \
                   df2=dftmp2,ticker2='',colname2='total_mv(yi)',label2='总市值(亿元)', \
                   ylabeltxt='',titletxt=titletxt,footnote=footnote, \
                   twinx=True, \
                   resample_freq='D',loc1=loc1,loc2=loc2, \
                   color1='red',color2='blue',facecolor='whitesmoke')           
        
        
    # 财务基本面指标查询=============================================================================
    #if category == 'financial':
    if any(s in category for s in ['financial','healthy']):
        
        try:
            df7=ak.stock_financial_analysis_indicator(symbol=ticker1) 
            #其中的日期为datetime.date object类型
            df7['日期']=df7['日期'].apply(lambda x: x.strftime("%Y-%m-%d"))
            #降序排列
            df7.sort_values(by=['日期'],ascending=False,inplace=True)
        except:
            print("  #Warning(stock_detail_china):financial info not found for",ticker)
            return

        df7['财报类别']=df7['日期'].apply(lambda x: x[5:])    
        # 注意：lambda中若使用if就同时要规定else
        df7['财报类别']=df7['财报类别'].apply(lambda x: '三季度报' if x=='09-30' else x)
        df7['财报类别']=df7['财报类别'].apply(lambda x: '中报' if x=='06-30' else x)
        df7['财报类别']=df7['财报类别'].apply(lambda x: '一季度报' if x=='03-31' else x)
        df7['财报类别']=df7['财报类别'].apply(lambda x: '年报' if x=='12-31' else x)

        # 整理信息：近两年，最多8个季度，再多会产生格式错位
        numOfQ=financial_quarters
        if numOfQ > 8:
            numOfQ=8
        
        titletxt=ticker_name(ticker,'stock')+"：主要财务信息，每股指标(元)"
        df7['加权每股收益']=df7['加权每股收益(元)']
        df7['每股收益_调整后']=df7['每股收益_调整后(元)']
        df7['扣非后每股收益']=df7['扣除非经常性损益后的每股收益(元)']
        df7['每股净资产_调整后']=df7['每股净资产_调整后(元)']
        df7['每股经营性现金流']=df7['每股经营性现金流(元)']
        df7['每股资本公积金']=df7['每股资本公积金(元)']
        df7['每股未分配利润']=df7['每股未分配利润(元)']

        colList=['日期','财报类别','加权每股收益','每股收益_调整后','扣非后每股收益', \
                  '每股净资产_调整后','每股经营性现金流','每股未分配利润']
        dftmp=df7[colList].head(numOfQ)
        
        # 为应对更多的字段，转置矩阵打印
        dftmp.set_index('日期',inplace=True)
        dftmp1=dftmp.T
        dftmp1.reset_index(inplace=True)
        dftmp1.rename(columns={'index':'项目'},inplace=True)
        """
        if prettytab:
            pandas2prettytable(dftmp1,titletxt,firstColSpecial=False,leftColAlign='l',otherColAlign='r',tabborder=tabborder)
            print(' ','数据来源：新浪财经,',str(today))
        else:
            print('\n*** '+titletxt+'\n')
            colalignList=['left','right','right','right','right','right','right','right','right']
            print(dftmp1.to_markdown(tablefmt='Simple',index=False,colalign=colalignList))
            print('\n数据来源：新浪财经,',str(today))
        """
        footnote='数据来源：新浪财经，'+str(stoday)
        df_display_CSS(df=dftmp1,titletxt=titletxt,footnote=footnote, \
                       facecolor=facecolor,decimals=2, \
                       titile_font_size=titile_font_size,heading_font_size=heading_font_size_small, \
                       data_font_size=data_font_size_small)        
        
        """
        加权平均每股收益：
        指计算时股份数用按月对总股数加权计算的数据，理由是由于公司投入的资本和资产不同，收益产生的基础也不同。

        摊薄每股收益：
        指按年末的普通股总数计算出来的每股收益，它等于净利润除以年末总股本。
        
        调整后的每股收益：又称稀释每股收益
        有的公司发行了可转债、认购权证、股票期权等，那么在计算每股收益的时候，就有调整前后了。
        调整前的，不考虑这些可能导致的股份增加；调整后，要考虑导致股份增加后的情况。
        
        稀释每股收益是以基本每股收益为基础，假设企业所有发行在外的稀释性潜在普通股均已转换为普通股，
        从而分别调整归属于普通股股东的当期净利润以及发行在外普通股的加权平均数计算而得的每股收益。
        比如某个公司有权证、可转债、即将执行的股权激励，就意味着股份有潜在的增加可能，
        为了准确评估每股收益，就必须用稀释每股收益。
        """
        
        titletxt=ticker_name(ticker,'stock')+"：主要财务信息，利润与成本"
        df7['扣非后净利润(元)']=df7['扣除非经常性损益后的净利润(元)']
        colList=['日期','财报类别','总资产利润率(%)','主营业务利润率(%)','总资产净利润率(%)','成本费用利润率(%)', \
                 '营业利润率(%)','主营业务成本率(%)','销售净利率(%)', '销售毛利率(%)','三项费用比重','非主营比重', \
                     '主营利润比重', '主营业务利润(元)', '扣非后净利润(元)']
        dftmp=df7[colList].head(numOfQ)
        
        # 去掉全列为空的字段
        dftmpCols=list(dftmp)
        for f in dftmpCols:
            fnum=len(set(dftmp[f].tolist()))
            if fnum == 1:
                del dftmp[f]
        
        dftmp['主营业务利润(百万元)']=dftmp['主营业务利润(元)'].apply(lambda x: round(float(x)/baiwan,4))
        dftmp['扣非后净利润(百万元)']=dftmp['扣非后净利润(元)'].apply(lambda x: round(float(x)/baiwan,4))
        dftmp.drop(['总资产利润率(%)','总资产净利润率(%)','主营业务利润(元)','扣非后净利润(元)'],axis=1,inplace=True)
        
        # 为应对更多的字段，转置矩阵打印
        dftmp.set_index('日期',inplace=True)
        dftmp1=dftmp.T
        dftmp1.reset_index(inplace=True)
        dftmp1.rename(columns={'index':'项目'},inplace=True)
        """
        if prettytab:
            pandas2prettytable(dftmp1,titletxt,firstColSpecial=False,leftColAlign='l',otherColAlign='r',tabborder=tabborder)
            print(' ','数据来源：新浪财经,',str(today))
        else:
            print('\n*** '+titletxt+'\n')
            colalignList=['left','right','right','right','right','right','right','right','right']
            print(dftmp1.to_markdown(tablefmt='Simple',index=False,colalign=colalignList))
            print('\n数据来源：新浪财经,',str(today))
        """
        df_display_CSS(df=dftmp1,titletxt=titletxt,footnote=footnote, \
                       facecolor=facecolor,decimals=2, \
                       titile_font_size=titile_font_size,heading_font_size=heading_font_size_small, \
                       data_font_size=data_font_size_small)        

        
        """
        总资产利润率=利润总额/平均总资产
        总资产净利润率=净利润/平均总资产
        净利润 = 利润总额 - 所得税费用
        
        通常，总资产利润率 > 总资产净利润率（不包括主营业务亏损时）
        
        成本费用利润率=利润总额/成本费用总额（即成本总额+费用总额）
        """
        
        titletxt=ticker_name(ticker,'stock')+"：主要财务信息，报酬与收益"
        colList=['日期','财报类别', '股本报酬率(%)','净资产报酬率(%)','资产报酬率(%)', '股息发放率(%)','投资收益率(%)', \
                 '净资产收益率(%)','加权净资产收益率(%)']
        dftmp=df7[colList].head(numOfQ)
        
        # 去掉全列为空的字段
        dftmpCols=list(dftmp)
        for f in dftmpCols:
            fnum=len(set(dftmp[f].tolist()))
            if fnum == 1:
                del dftmp[f]
        
        finalCols=['日期','财报类别','资产报酬率(%)','净资产报酬率(%)']
        dftmp1=dftmp[finalCols]
        
        # 为应对更多的字段，转置矩阵打印
        dftmp1.set_index('日期',inplace=True)
        dftmp2=dftmp1.T
        dftmp2.reset_index(inplace=True)
        dftmp2.rename(columns={'index':'项目'},inplace=True)
        """
        if prettytab:
            pandas2prettytable(dftmp2,titletxt,firstColSpecial=False,leftColAlign='l',otherColAlign='r',tabborder=tabborder)
            print(' ','数据来源：新浪财经,',str(today))
        else:
            print('\n*** '+titletxt+'\n')
            colalignList=['left','right','right','right','right','right','right','right','right']
            print(dftmp2.to_markdown(tablefmt='Simple',index=False,colalign=colalignList))
            print('\n数据来源：新浪财经,',str(today))
        """
        df_display_CSS(df=dftmp2,titletxt=titletxt,footnote=footnote, \
                       facecolor=facecolor,decimals=2, \
                       titile_font_size=titile_font_size,heading_font_size=heading_font_size_small, \
                       data_font_size=data_font_size_small)        

        
        """
        净资产收益率=净利润/净资产。净资产=所有者权益+少数股东权益
        
        净资产报酬率=净利润/平均净资产总额。平均净资产总额=期初期末净资产总额平均值
        
        股本报酬率/回报率=净利润/期初期末总股本的均值。股本是实收资本，而股权是股东权益。
        """
        
        titletxt=ticker_name(ticker,'stock')+"：主要财务信息，增长率"
        colList=['日期','财报类别','主营业务收入增长率(%)','净利润增长率(%)','总资产增长率(%)','净资产增长率(%)']
        dftmp=df7[colList].head(numOfQ)
        
        # 去掉全列为空的字段
        dftmpCols=list(dftmp)
        for f in dftmpCols:
            fnum=len(set(dftmp[f].tolist()))
            if fnum == 1:
                del dftmp[f]
        
        # 为应对更多的字段，转置矩阵打印
        dftmp.set_index('日期',inplace=True)
        dftmp1=dftmp.T
        dftmp1.reset_index(inplace=True)
        dftmp1.rename(columns={'index':'项目'},inplace=True)
        """
        if prettytab:
            pandas2prettytable(dftmp1,titletxt,firstColSpecial=False,leftColAlign='l',otherColAlign='r',tabborder=tabborder)
            print(' ','数据来源：新浪财经,',str(today))
        else:
            print('\n*** '+titletxt+'\n')
            colalignList=['left','right','right','right','right','right','right','right','right']
            print(dftmp1.to_markdown(tablefmt='Simple',index=False,colalign=colalignList))
            print('\n数据来源：新浪财经,',str(today))
            
        """
        df_display_CSS(df=dftmp1,titletxt=titletxt,footnote=footnote, \
                       facecolor=facecolor,decimals=2, \
                       titile_font_size=titile_font_size,heading_font_size=heading_font_size_small, \
                       data_font_size=data_font_size_small)        

        
        titletxt=ticker_name(ticker,'stock')+"：主要财务信息，资产负债分析"
        colList=['日期','财报类别','流动比率','速动比率','现金比率(%)','利息支付倍数','长期债务与营运资金比率(%)', \
                 '股东权益比率(%)','长期负债比率(%)','股东权益与固定资产比率(%)','负债与所有者权益比率(%)', \
                     '长期资产与长期资金比率(%)','资本化比率(%)','固定资产净值率(%)','资本固定化比率(%)', \
                         '产权比率(%)','清算价值比率(%)','固定资产比重(%)','资产负债率(%)','总资产(元)']
        dftmp=df7[colList].head(numOfQ)
        dftmp.rename(columns={'长期债务与营运资金比率(%)':'长期债务/营运资金(%)', \
                              '股东权益与固定资产比率(%)':'股东权益/固定资产(%)', \
                              '负债与所有者权益比率(%)':'负债/所有者权益(%)', \
                              '长期资产与长期资金比率(%)':'长期资产/长期资金(%)', \
                              '股东权益与固定资产比率(%)':'股东权益/固定资产(%)'},inplace=True)
        
        # 去掉全列为空的字段
        dftmpCols=list(dftmp)
        for f in dftmpCols:
            fnum=len(set(dftmp[f].tolist()))
            if fnum == 1:
                del dftmp[f]

        dftmp['总资产(亿元)']=dftmp['总资产(元)'].apply(lambda x: round(float(x)/yi,4))
        dftmp.drop(['总资产(元)'],axis=1,inplace=True)
        
        # 为应对更多的字段，转置矩阵打印
        dftmp.set_index('日期',inplace=True)
        dftmp1=dftmp.T
        dftmp1.reset_index(inplace=True)
        dftmp1.rename(columns={'index':'项目'},inplace=True)
        """
        if prettytab:
            pandas2prettytable(dftmp1,titletxt,firstColSpecial=False,leftColAlign='l',otherColAlign='r',tabborder=tabborder)
            print(' ','数据来源：新浪财经,',str(today))
        else:
            print('\n*** '+titletxt+'\n')
            colalignList=['left','right','right','right','right','right','right','right','right']
            print(dftmp1.to_markdown(tablefmt='Simple',index=False,colalign=colalignList))
            print('\n数据来源：新浪财经,',str(today))
        """
        df_display_CSS(df=dftmp1,titletxt=titletxt,footnote=footnote, \
                       facecolor=facecolor,decimals=2, \
                       titile_font_size=titile_font_size,heading_font_size=heading_font_size_small, \
                       data_font_size=data_font_size_small)        

        
        """
        股东权益比率（又称自有资本比率或净资产比率）是股东权益与资产总额的比率。
        固定资产净值率是指固定资产原价扣除其累计磨损额后的余额即固定资产折余价值对固定资产原价的比率。
        资本固定化比率=(资产总计-流动资产合计)/所有者权益平均余额
        固定资产比率是指固定资产与资产总额之比。
        
        """
        
        titletxt=ticker_name(ticker,'stock')+"：主要财务信息，现金流量指标（均为%）"
        colList=['日期','财报类别','经营现金净流量对销售收入比率(%)','资产的经营现金流量回报率(%)','经营现金净流量与净利润的比率(%)', \
                 '经营现金净流量对负债比率(%)','现金流量比率(%)']
        dftmp=df7[colList].head(numOfQ)
        dftmp.rename(columns={'经营现金净流量对销售收入比率(%)':'经营现金净流量/销售收入', \
                              '资产的经营现金流量回报率(%)':'资产的经营现金流量回报率', \
                              '经营现金净流量与净利润的比率(%)':'经营现金净流量/净利润', \
                              '经营现金净流量对负债比率(%)':'经营现金净流量/负债', \
                              '现金流量比率(%)':'现金流量比率'},inplace=True)
        
        # 去掉全列为空的字段
        dftmpCols=list(dftmp)
        for f in dftmpCols:
            fnum=len(set(dftmp[f].tolist()))
            if fnum == 1:
                del dftmp[f]
        
        # 为应对更多的字段，转置矩阵打印
        dftmp.set_index('日期',inplace=True)
        dftmp1=dftmp.T
        dftmp1.reset_index(inplace=True)
        dftmp1.rename(columns={'index':'项目'},inplace=True)

        """
        if prettytab:
            pandas2prettytable(dftmp1,titletxt,firstColSpecial=False,leftColAlign='l',otherColAlign='r',tabborder=tabborder)
            print(' ','数据来源：新浪财经,',str(today))
        else:
            print('\n*** '+titletxt+'\n')
            colalignList=['left','right','right','right','right','right','right','right','right']
            print(dftmp1.to_markdown(tablefmt='Simple',index=False,colalign=colalignList))
            print('\n数据来源：新浪财经,',str(today))
        """
        df_display_CSS(df=dftmp1,titletxt=titletxt,footnote=footnote, \
                       facecolor=facecolor,decimals=2, \
                       titile_font_size=titile_font_size,heading_font_size=heading_font_size_small, \
                       data_font_size=data_font_size_small)        

        """
        资产的经营现金流量回报率是经营活动产生的现金流量净额/总资产,是体现企业收现能力的指标之一。
        
        """
        
    return 


#==============================================================================
#==============================================================================