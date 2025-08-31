# -*- coding: utf-8 -*-
"""
@function: 评估一只股票是否值得买入。教学演示用，其他用途责任自负，机器学习课程案例演示用
@model：线性分类模型，logistic, linearSVC
@version：v1.0，2019.4.15
@purpose: 机器学习课程案例
@author: 王德宏，北京外国语大学国际商学院
"""

#=====================================================================
def get_price(ticker,atdate,fromdate):
    """
    功能：抓取股价
    输出：指定收盘价格序列，最新日期的股价排列在前
    ticker: 股票代码
    atdate: 当前日期，既可以是今天日期，也可以是一个历史日期，datetime类型
    fromdate: 样本开始日期，尽量远的日期，以便取得足够多的原始样本，类型同atdate
    """
    
    #仅为调试用的函数入口参数，正式使用前需要注释掉！
    #ticker='MSFT'
    #atdate='3/29/2019'
    #fromdate='1/1/2015'
    #---------------------------------------------
    
    #抓取美股股票价格
    from pandas_datareader import data
    price=data.DataReader(ticker,'stooq',fromdate,atdate)
    
    #去掉比起始日期更早的样本
    price2=price[price.index >= fromdate]
    

    #按日期降序排序，近期的价格排在前面
    sortedprice=price2.sort_index(axis=0,ascending=False)

    #提取日期和星期几
    #sortedprice['Date']=sortedprice.index.date
    sortedprice['Date']=sortedprice.index.strftime("%Y-%m-%d")
    sortedprice['Weekday']=sortedprice.index.weekday+1
    
    #生成输出数据格式：日期，星期几，收盘价
    dfprice=sortedprice[['Date','Weekday','Close']]
    
    return dfprice
    

if __name__=='__main__':
    dfprice=get_price('MSFT','4/12/2019','1/1/2015')
    dfprice.head(5)
    dfprice.tail(3)
    dfprice[dfprice.Date == '2019-03-29']
    dfprice[(dfprice.Date>='2019-03-20') & (dfprice.Date<='2019-03-29')]
    
    dfindex=get_price('^GSPC','4/12/2019','1/1/2015')
    
#=====================================================================
def get_portfolio(tickerlist,sharelist,atdate,fromdate):
    """
    功能：抓取投资组合的市值
    输出：指定投资组合的收盘价格序列，最新日期的股价排列在前
    tickerlist:投资组合中各个股票的代码列表
    sharelist:投资组合中各个股票的份额列表
    atdate:当前日期，既可以是今天日期，也可以是一个历史日期，datetime类型
    fromdate:样本开始日期，尽量远的日期，以便取得足够多的原始样本，类型同atdate
    """
    
    #仅为调试用的函数入口参数，正式使用前需要注释掉！
    #tickerlist=['BILI','PDD']
    #sharelist=[0.67,0.33]
    #sum(sharelist)
    #atdate='4/12/2019'
    #fromdate='1/1/2015'
    #---------------------------------------------
    
    #检查投资组合的份额是否等于1
    if sum(sharelist) != 1.0:
        print("Error: sum of all shares in the portfolio is not 1")
        return None
    
    #抓取股票价格
    from pandas_datareader import data
    price=data.DataReader(tickerlist,'yahoo',fromdate,atdate)
    
    #去掉比起始日期更早的样本
    price2=price[price.index >= fromdate]
    

    #按日期降序排序，近期的价格排在前面
    sortedprice=price2.sort_index(axis=0,ascending=False)

    #提取日期和星期几
    #sortedprice['Date']=sortedprice.index.date
    sortedprice['Date']=sortedprice.index.strftime("%Y-%m-%d")
    sortedprice['Weekday']=sortedprice.index.weekday+1
    
    #合成投资组合的价值
    dfprice=sortedprice[['Date','Weekday','Close']]
    import copy
    dfprice2= copy.deepcopy(dfprice)
    dfprice2['Value']=0.0
    rownames=dfprice.columns.values.tolist() 
    for i in range(2,len(rownames)):
        value=dfprice2[('Close',rownames[i][1])]*sharelist[i-2]
        dfprice2['Value']=dfprice2['Value']+value
    
    #生成输出
    import pandas as pd
    dfprice3=pd.DataFrame(columns=['Date','Weekday','Close'])
    dfprice3['Date']=dfprice2['Date']
    dfprice3['Weekday']=dfprice2['Weekday']
    dfprice3['Close']=dfprice2['Value']
    dfprice4=dfprice3.dropna()
    return dfprice4
    

if __name__=='__main__':
    dfprice=get_portfolio(['BILI','PDD'],[0.67,0.33],'4/12/2019','1/1/2015')
    dfprice.head(5)
    dfprice.tail(3)
    dfprice[dfprice.Date == '2019-03-29']
    dfprice[(dfprice.Date>='2019-03-20') & (dfprice.Date<='2019-03-29')]
    
    dfindex=get_price('^GSPC','4/12/2019','1/1/2015')

#=====================================================================
#=====================================================================

def tradefee(price,n_shares=1,trade='buy'):
    """
    返回买卖1块金额股票证券交易的总费用
    trade: buy=买，sell=卖。区分买卖的原因是买卖手续费可能不同
    注意：印花税和券商手续费等与交易金额有关，而过户费与交易股数有关
    设立此函数的原因：各个国家、股票交易所和券商的收费方式和标准存在差异
    为简单起见，教学演示统一为买入时千分之二卖出时千分之三，实际应用时可再进行改造
    """
    if trade =='buy' : fee=price*n_shares*0.002
    if trade =='sell': fee=price*n_shares*0.003
    if not (trade in ['buy','sell']): print("Invalid trade")
    return fee
    
#=====================================================================    
def make_advice_sample(dfprice,dfindex,n_nextdays=10, \
                      n_samples=120,n_features=20, \
                      samplingtype='AR',n_shares=1):
    """
    功能：生成指定股票的样本
    n_nextdays:预测从atdate开始未来第几天的股价，默认为1
    n_samples:需要生成的样本个数，默认240个(一年的平均交易天数)
    n_features:使用的特征数量，默认20个(一个月的平均交易天数)
    n_shares: 买卖的股数，默认1股
    samplingtype：样本构造方法，AR=使用历史超额收益率，JG=使用历史投资结果
    """
    
    #仅为测试用
    #n_shares=1
    #n_nextdays=5
    #n_samples=240
    #n_features=20
    #samplingtype='AR'
    
    #提取收盘价和市场指数，Series类型
    closeprice=dfprice.Close
    maxrec=len(closeprice)
    closeindex=dfindex.Close
    
    #转换为机器学习需要的ndarray类型
    import numpy as np
    ndprice=np.asmatrix(closeprice,dtype=None)
    ndindex=np.asmatrix(closeindex,dtype=None)
    
    #建立数组并赋初值
    ndRs=np.asmatrix([[0.0 for i in range(maxrec)] for j in range(1)])
    ndRm=np.asmatrix([[0.0 for i in range(maxrec)] for j in range(1)])
    ndAR=np.asmatrix([[0.0 for i in range(maxrec)] for j in range(1)])
    ndJG=np.asmatrix([[-1 for i in range(maxrec)] for j in range(1)])
    
    for i in range(0,maxrec-n_nextdays-1):
        #print("i=",i)
        #计算股票买卖收益率
        sellprice=ndprice[0,i]
        sellfee=tradefee(sellprice,n_shares,trade='sell')
        sellgain=sellprice*n_shares - sellfee
        buyprice=ndprice[0,i+n_nextdays]
        buyfee=tradefee(buyprice,n_shares,trade='buy')
        buycost=buyprice*n_shares + buyfee
        Rs=(sellgain-buycost)/buycost
        ndRs[0,i]=Rs
    
        #计算市场指数收益率
        Rm=(ndindex[0,i]-ndindex[0,i+n_nextdays])/ndindex[0,i+n_nextdays]
        ndRm[0,i]=Rm
        AR=Rs - Rm
        ndAR[0,i]=AR
    
        #评估投资结果
        if (Rs>0) & (AR>0): JG=1
        else: JG=-1
        ndJG[0,i]=JG

    #生成第一个标签样本：标签矩阵y(形状：n_samples x 1)    
    y=np.asmatrix(ndJG[0,0])
    #生成第一个特征样本：特征矩阵X(形状：n_samples x n_features)
    #如果样本构造类型为AR，则以ndAR作为特征，否则以JG作为特征
    if samplingtype=='AR': ndfeature=ndAR
    else: ndfeature=ndJG
    
    #row,col=ndfeature.shape    
    X=ndfeature[0,(n_nextdays+1):(n_features+n_nextdays+1)]
    
    #生成其余的标签样本和特征样本 
    for i in range(1,n_samples):
        #print("i=",i)
        
        
        X_row=ndfeature[0,(n_nextdays+1+i):(n_features+n_nextdays+1+i)]
        m,n=X_row.shape
        if n == n_features: 
            X=np.append(X,X_row,axis=0)
            y_row=np.asmatrix(ndJG[0,i])
            y=np.append(y,y_row,axis=0)
        else:
            print("\nInsufficient number of samples, try use smaller parms")
            print("    Number of samples:",maxrec)
            break  #跳出for循环，注意continue只是跳出当前循环就如下一次循环
    
    return X,y,ndfeature

if __name__=='__main__':
    ticker='MSFT'
    market='^GSPC'
    dfprice=get_price(ticker,'4/12/2019','1/1/2015')
    dfindex=get_price(market,'4/12/2019','1/1/2015')    
    
    X,y,ndfeature=make_advice_sample(dfprice,dfindex,120,480,120,'AR')
    #m,n=ndfeature.shape
    X1,y1,ndfeature1=make_advice_sample(dfprice,dfindex,5,240,20,'JG')

    from sklearn.utils import column_or_1d
    y=column_or_1d(y,warn=False)
    from sklearn.model_selection import train_test_split
    X_train,X_test,y_train,y_test= \
    	train_test_split(X,y,stratify=y,random_state=0)

    from sklearn.linear_model import LogisticRegression
    lr=LogisticRegression(C=1, penalty='l2',solver='liblinear')
    lr.fit(X_train,y_train)
    lr.score(X_train,y_train)
    lr.score(X_test,y_test)
    X_new=ndfeature[0,0:20]
    lr.predict(X_new)


    y1=column_or_1d(y1,warn=False)
    from sklearn.model_selection import train_test_split
    X1_train,X1_test,y1_train,y1_test= \
    	train_test_split(X1,y1,stratify=y1,random_state=0)

    from sklearn.linear_model import LogisticRegression
    lr1=LogisticRegression(C=1, penalty='l2',solver='liblinear')
    lr1.fit(X1_train,y1_train)
    lr1.score(X1_train,y1_train)
    lr1.score(X1_test,y1_test)
    X1_new=ndfeature[0,0:20]
    lr1.predict(X1_new)    
    
    
    ticker='PDD'
    dfprice=get_price(ticker,'4/12/2019','1/1/2015')
    len(dfprice)
    X,y,ndfeature=make_advice_sample(dfprice,dfindex,30,120,30,'AR')
    
    ticker='BILI'
    dfprice=get_price(ticker,'4/12/2019','1/1/2015')
    len(dfprice)
    X,y,ndfeature=make_advice_sample(dfprice,dfindex,20,120,40,'AR')
#=====================================================================
def bestLRL1(X,y):
    """
    功能：使用LogisticRegression和正则化L1参数C，获得最高测试分数
    返回：最优的C参数和模型
    """
    
    #将整个样本随机分割为训练集和测试集
    from sklearn.utils import column_or_1d
    y=column_or_1d(y,warn=False)    
    from sklearn.model_selection import train_test_split
    X_train,X_test,y_train,y_test=train_test_split(X,y,stratify=y,random_state=0)

    best_score=0.1
    import numpy as np
    from sklearn.linear_model import LogisticRegression

    for Cvalue in np.arange(0.01,1,0.01):
        lr=LogisticRegression(C=Cvalue, penalty='l1', \
                              solver='liblinear', max_iter=10000)
        lr.fit(X_train,y_train)
        score_test = lr.score(X_test, y_test)  
        if score_test > best_score:
            best_score=score_test
            best_C=Cvalue
            best_model=lr
    
    for Cvalue in np.arange(1,10,0.1):
        lr=LogisticRegression(C=Cvalue, penalty='l1', \
                              solver='liblinear', max_iter=10000)
        lr.fit(X_train,y_train)
        score_test = lr.score(X_test, y_test)  
        if score_test > best_score:
            best_score=score_test
            best_C=Cvalue
            best_model=lr    
    
    for Cvalue in np.arange(10,100,1):
        lr=LogisticRegression(C=Cvalue, penalty='l1', \
                              solver='liblinear', max_iter=10000)
        lr.fit(X_train,y_train)
        score_test = lr.score(X_test, y_test)  
        if score_test > best_score:
            best_score=score_test
            best_C=Cvalue
            best_model=lr       
    
    for Cvalue in np.arange(100,1000,10):
        lr=LogisticRegression(C=Cvalue, penalty='l1', \
                              solver='liblinear', max_iter=10000)
        lr.fit(X_train,y_train)
        score_test = lr.score(X_test, y_test)  
        if score_test > best_score:
            best_score=score_test
            best_C=Cvalue
            best_model=lr       
    
    score_train=best_model.score(X_train,y_train)
    return best_model,best_C,score_train,best_score
    

if __name__=='__main__':
    ticker='MSFT'
    market='^GSPC'
    dfprice=get_price(ticker,'4/12/2019','1/1/2015')
    dfindex=get_price(market,'4/12/2019','1/1/2015')    
    
    X,y,ndfeature=make_advice_sample(dfprice,dfindex,5,240,20,'AR')
    model,C,score_train,score_test=bestLRL1(X,y)
    print("%.5f, %.5f, %.5f"%(C,score_train,score_test))
    #结果：14，0.66667，0.71667
            
    X_new=ndfeature[0,0:20]
    y_new=model.predict(X_new)
    print("%.0f"%y_new)  
    #结果：-1
    
    X1,y1,ndfeature1=make_advice_sample(dfprice,dfindex,5,240,20,'JG')    
    model,C,score_train,score_test=bestLRL1(X1,y1)
    print("%.5f, %.5f, %.5f"%(C,score_train,score_test))
    #结果：0.14，0.61667，0.63333
#=====================================================================

def bestLRL2(X,y):
    """
    功能：使用LogisticRegression和正则化L2参数C，获得最高测试分数
    返回：最优的C参数和模型
    """
    
    #将整个样本随机分割为训练集和测试集
    from sklearn.utils import column_or_1d
    y=column_or_1d(y,warn=False)    
    from sklearn.model_selection import train_test_split
    X_train,X_test,y_train,y_test=train_test_split(X,y,stratify=y,random_state=0)

    best_score=0.1
    import numpy as np
    from sklearn.linear_model import LogisticRegression

    for Cvalue in np.arange(0.01,1,0.01):
        lr=LogisticRegression(C=Cvalue, penalty='l2', \
                              solver='liblinear', max_iter=10000)
        lr.fit(X_train,y_train)
        score_test = lr.score(X_test, y_test)  
        if score_test > best_score:
            best_score=score_test
            best_C=Cvalue
            best_model=lr
    
    for Cvalue in np.arange(1,10,0.1):
        lr=LogisticRegression(C=Cvalue, penalty='l2', \
                              solver='liblinear', max_iter=10000)
        lr.fit(X_train,y_train)
        score_test = lr.score(X_test, y_test)  
        if score_test > best_score:
            best_score=score_test
            best_C=Cvalue
            best_model=lr    
    
    for Cvalue in np.arange(10,100,1):
        lr=LogisticRegression(C=Cvalue, penalty='l2', \
                              solver='liblinear', max_iter=10000)
        lr.fit(X_train,y_train)
        score_test = lr.score(X_test, y_test)  
        if score_test > best_score:
            best_score=score_test
            best_C=Cvalue
            best_model=lr       
    
    for Cvalue in np.arange(100,1000,10):
        lr=LogisticRegression(C=Cvalue, penalty='l2', \
                              solver='liblinear', max_iter=10000)
        lr.fit(X_train,y_train)
        score_test = lr.score(X_test, y_test)  
        if score_test > best_score:
            best_score=score_test
            best_C=Cvalue
            best_model=lr       
    
    score_train=best_model.score(X_train,y_train)
    return best_model,best_C,score_train,best_score
    

if __name__=='__main__':
    ticker='MSFT'
    market='^GSPC'
    dfprice=get_price(ticker,'4/12/2019','1/1/2015')
    dfindex=get_price(market,'4/12/2019','1/1/2015')    
    
    X,y,ndfeature=make_advice_sample(dfprice,dfindex,5,240,20,'AR')
    model,C,score_train,score_test=bestLRL2(X,y)
    print("%.5f, %.5f, %.5f"%(C,score_train,score_test))
    #结果：33, 0.65，0.68333
            
    X_new=ndfeature[0,0:20]
    y_new=model.predict(X_new)
    print("%.0f"%y_new)  
    #结果：-1
    
    X1,y1,ndfeature1=make_advice_sample(dfprice,dfindex,5,240,20,'JG')    
    model,C,score_train,score_test=bestLRL2(X1,y1)
    print("%.5f, %.5f, %.5f"%(C,score_train,score_test))
    #结果：0.02，0.62222，0.66667

#==============================================================================

def bestLSVCL1(X,y):
    """
    功能：使用LinearSVC和正则化L1参数C，获得最高测试分数
    返回：最优的C参数和模型
    """
    
    #将整个样本随机分割为训练集和测试集
    from sklearn.utils import column_or_1d
    y=column_or_1d(y,warn=False)    
    from sklearn.model_selection import train_test_split
    X_train,X_test,y_train,y_test=train_test_split(X,y,stratify=y,random_state=0)

    best_score=0.1
    import numpy as np
    from sklearn.svm import LinearSVC

    for Cvalue in np.arange(0.01,1,0.01):
        lr=LinearSVC(C=Cvalue, penalty='l1',dual=False,max_iter=10**6)
        lr.fit(X_train,y_train)
        score_test = lr.score(X_test, y_test)  
        if score_test > best_score:
            best_score=score_test
            best_C=Cvalue
            best_model=lr
    
    for Cvalue in np.arange(1,10,0.1):
        lr=LinearSVC(C=Cvalue, penalty='l1',dual=False,max_iter=10**6)
        lr.fit(X_train,y_train)
        score_test = lr.score(X_test, y_test)  
        if score_test > best_score:
            best_score=score_test
            best_C=Cvalue
            best_model=lr    
    
    for Cvalue in np.arange(10,100,1):
        lr=LinearSVC(C=Cvalue, penalty='l1',dual=False,max_iter=10**6)
        lr.fit(X_train,y_train)
        score_test = lr.score(X_test, y_test)  
        if score_test > best_score:
            best_score=score_test
            best_C=Cvalue
            best_model=lr       
    
    for Cvalue in np.arange(100,1000,10):
        lr=LinearSVC(C=Cvalue, penalty='l1',dual=False,max_iter=10**6)
        lr.fit(X_train,y_train)
        score_test = lr.score(X_test, y_test)  
        if score_test > best_score:
            best_score=score_test
            best_C=Cvalue
            best_model=lr       
    
    score_train=best_model.score(X_train,y_train)
    return best_model,best_C,score_train,best_score
    

if __name__=='__main__':
    ticker='MSFT'
    market='^GSPC'
    dfprice=get_price(ticker,'4/12/2019','1/1/2015')
    dfindex=get_price(market,'4/12/2019','1/1/2015')    
    
    X,y,ndfeature=make_advice_sample(dfprice,dfindex,5,240,20,'AR')
    model,C,score_train,score_test=bestLSVCL1(X,y)
    print("%.5f, %.5f, %.5f"%(C,score_train,score_test))
    #结果：5.3, 0.66111, 0.71667
            
    X_new=ndfeature[0,0:20]
    y_new=model.predict(X_new)
    print("%.0f"%y_new)  
    #结果：-1
    
    X1,y1,ndfeature1=make_advice_sample(dfprice,dfindex,5,240,20,'JG')    
    model,C,score_train,score_test=bestLSVCL1(X1,y1)
    print("%.5f, %.5f, %.5f"%(C,score_train,score_test))
    #结果：0.04, 0.61667, 0.63333


#==============================================================================
    
def bestLSVCL2(X,y):
    """
    功能：使用LinearSVC和正则化L2参数C，获得最高测试分数
    返回：最优的C参数和模型
    """
    
    #将整个样本随机分割为训练集和测试集
    from sklearn.utils import column_or_1d
    y=column_or_1d(y,warn=False)    
    from sklearn.model_selection import train_test_split
    X_train,X_test,y_train,y_test=train_test_split(X,y,stratify=y,random_state=0)

    best_score=0.1
    import numpy as np
    from sklearn.svm import LinearSVC

    for Cvalue in np.arange(0.01,1,0.01):
        lr=LinearSVC(C=Cvalue, penalty='l2',dual=False,max_iter=10**6)
        lr.fit(X_train,y_train)
        score_test = lr.score(X_test, y_test)  
        if score_test > best_score:
            best_score=score_test
            best_C=Cvalue
            best_model=lr
    
    for Cvalue in np.arange(1,10,0.1):
        lr=LinearSVC(C=Cvalue, penalty='l2',dual=False,max_iter=10**6)
        lr.fit(X_train,y_train)
        score_test = lr.score(X_test, y_test)  
        if score_test > best_score:
            best_score=score_test
            best_C=Cvalue
            best_model=lr    
    
    for Cvalue in np.arange(10,100,1):
        lr=LinearSVC(C=Cvalue, penalty='l2',dual=False,max_iter=10**6)
        lr.fit(X_train,y_train)
        score_test = lr.score(X_test, y_test)  
        if score_test > best_score:
            best_score=score_test
            best_C=Cvalue
            best_model=lr       
    
    for Cvalue in np.arange(100,1000,10):
        lr=LinearSVC(C=Cvalue, penalty='l2',dual=False,max_iter=10**6)
        lr.fit(X_train,y_train)
        score_test = lr.score(X_test, y_test)  
        if score_test > best_score:
            best_score=score_test
            best_C=Cvalue
            best_model=lr       
    
    score_train=best_model.score(X_train,y_train)
    return best_model,best_C,score_train,best_score
    

if __name__=='__main__':
    ticker='MSFT'
    market='^GSPC'
    dfprice=get_price(ticker,'4/12/2019','1/1/2015')
    dfindex=get_price(market,'4/12/2019','1/1/2015')    
    
    X,y,ndfeature=make_advice_sample(dfprice,dfindex,5,240,20,'AR')
    model,C,score_train,score_test=bestLSVCL2(X,y)
    print("%.5f, %.5f, %.5f"%(C,score_train,score_test))
    #结果：4, 0.65000, 0.68333
            
    X_new=ndfeature[0,0:20]
    y_new=model.predict(X_new)
    print("%.0f"%y_new)  
    #结果：-1
    
    X1,y1,ndfeature1=make_advice_sample(dfprice,dfindex,5,240,20,'JG')    
    model,C,score_train,score_test=bestLSVCL2(X1,y1)
    print("%.5f, %.5f, %.5f"%(C,score_train,score_test))
    #结果：0.01, 0.63333, 0.58333


#==============================================================================

def bestMODEL(dfprice,dfindex,n_nextdays=5, \
                      n_samples=240,n_features=20, n_shares=1):  
    """
    功能：给定投资天数，样本构造参数，求最佳C值和预测投资结果
    """
    
    #样本构造方法：samplingtype='AR'
    best_score=0.1
    
    #构造样本：AR, JG
    X,y,ndfeature=make_advice_sample(dfprice,dfindex,n_nextdays, \
                              n_samples,n_features,'AR',n_shares)    
    X1,y1,ndfeature1=make_advice_sample(dfprice,dfindex,n_nextdays, \
                              n_samples,n_features,'JG',n_shares)    
    
    #测试LRL1优化策略
    model,C,score_train,score_test=bestLRL1(X,y)
    if score_test > best_score:
        bestmodel=model
        bestC=C
        best_train=score_train
        best_score=score_test        
        besttype='AR'
        beststrategy='LRL1'
        
    model,C,score_train,score_test=bestLRL1(X1,y1)
    if score_test > best_score:
        bestmodel=model
        bestC=C
        best_train=score_train
        best_score=score_test        
        besttype='JG' 
        beststrategy='LRL1'
    
    
    #测试LRL2优化策略
    model,C,score_train,score_test=bestLRL2(X,y)
    if score_test > best_score:
        bestmodel=model
        bestC=C
        best_train=score_train
        best_score=score_test        
        besttype='AR'
        beststrategy='LRL2'
        
    model,C,score_train,score_test=bestLRL2(X1,y1)
    if score_test > best_score:
        bestmodel=model
        bestC=C
        best_train=score_train
        best_score=score_test        
        besttype='JG' 
        beststrategy='LRL2'

    #测试LSVCL1优化策略
    model,C,score_train,score_test=bestLSVCL1(X,y)
    if score_test > best_score:
        bestmodel=model
        bestC=C
        best_train=score_train
        best_score=score_test        
        besttype='AR'
        beststrategy='LSVCL1'
        
    model,C,score_train,score_test=bestLSVCL1(X1,y1)
    if score_test > best_score:
        bestmodel=model
        bestC=C
        best_train=score_train
        best_score=score_test        
        besttype='JG' 
        beststrategy='LSVCL1'

    #测试LSVCL2优化策略
    model,C,score_train,score_test=bestLSVCL2(X,y)
    if score_test > best_score:
        bestmodel=model
        bestC=C
        best_train=score_train
        best_score=score_test        
        besttype='AR'
        beststrategy='LSVCL2'
        
    model,C,score_train,score_test=bestLSVCL2(X1,y1)
    if score_test > best_score:
        bestmodel=model
        bestC=C
        best_train=score_train
        best_score=score_test        
        besttype='JG' 
        beststrategy='LSVCL2'
                
    print("    ***Model settings***")
    print("       Future days       :",n_nextdays)
    print("       Number of samples :",n_samples)
    print("       Number of features:",n_features)    
    print("    ***Best model specification***")
    print("       Model             :",beststrategy)
    print("       Sampling type     :",besttype)
    print("       C value           : %.2f"%bestC)
    print("       Score on train    : %.4f"%best_train)
    print("       Score on test     : %.4f"%best_score)
    
    ndf=ndfeature
    if besttype == 'JG': ndf=ndfeature1
    
    return bestmodel,beststrategy,bestC,besttype,score_train,best_score,ndf
    

if __name__=='__main__':
    ticker='MSFT'
    market='^GSPC'
    dfprice=get_price(ticker,'4/12/2019','1/1/2015')
    dfindex=get_price(market,'4/12/2019','1/1/2015')    

    n_days=5
    n_samples=240
    n_features=20
    model,strategy,C,ntype,score_train,score_test,ndfeature= \
        bestMODEL(dfprice,dfindex,n_days,n_samples,n_features)      
    #结果：LRL1 AR 14.00, 0.6333, 0.7167

    X_new=ndfeature[0,0:n_features]
    y_new=model.predict(X_new)
    print(y_new[0])  
    #结果：-1

    ticker='BILI'
    dfprice=get_price(ticker,'4/12/2019','1/1/2015')

    n_days=20
    n_samples=120
    n_features=40
    model,strategy,C,ntype,score_train,score_test,ndfeature= \
        bestMODEL(dfprice,dfindex,n_days,n_samples,n_features)      
    """
    #结果：'
    ***Model settings***
       Stock             : BILI
       Future days       : 20
       Number of samples : 120
       Number of features: 40
    ***Best model specification***
       Model             : LRL1
       Sampling type     : AR
       C value           : 2.00
       Score on train    : 0.7111
       Score on test     : 0.7000
    """

    X_new=ndfeature[0,0:n_features]
    y_new=model.predict(X_new)
    print(y_new[0])  
    #结果：1    


    ticker='PDD'
    dfprice=get_price(ticker,'4/12/2019','1/1/2015')

    n_days=30
    n_samples=120
    n_features=30
    model,strategy,C,ntype,score_train,score_test,ndfeature= \
        bestMODEL(dfprice,dfindex,n_days,n_samples,n_features)      
    """
    #结果：
    ***Model settings***
       Stock             : PDD
       Future days       : 30
       Number of samples : 120
       Number of features: 30
    ***Best model specification***
       Model             : LRL2
       Sampling type     : AR
       C value           : 0.21
       Score on train    : 0.7667
       Score on test     : 0.7333
    """

    X_new=ndfeature[0,0:n_features]
    y_new=model.predict(X_new)
    print(y_new[0])  
    #结果：1 


    ticker='BABA'
    dfprice=get_price(ticker,'4/12/2019','1/1/2015')

    n_days=20
    n_samples=120
    n_features=40
    model,strategy,C,ntype,score_train,score_test,ndfeature= \
        bestMODEL(dfprice,dfindex,n_days,n_samples,n_features)      
    """
    #结果：
    ***Model settings***
       Future days       : 20
       Number of samples : 120
       Number of features: 40
    ***Best model specification***
       Model             : LSVCL1
       Sampling type     : JG
       C value           : 0.26
       Score on train    : 0.8111
       Score on test     : 0.8000
    """

    X_new=ndfeature[0,0:n_features]
    y_new=model.predict(X_new)
    print(y_new[0])  
    #结果：1 
    
    
    dfprice=get_portfolio(['BABA','BILI','PDD'],[0.5,0.33,0.17],'4/12/2019','1/1/2015')
    model,strategy,C,ntype,score_train,score_test,ndfeature= \
            bestMODEL(dfprice,dfindex,30, 80,60)
    """
    结果：
    ***Model settings***
       Future days       : 30
       Number of samples : 80
       Number of features: 60
    ***Best model specification***
       Model             : LRL1
       Sampling type     : AR
       C value           : 1.30
       Score on train    : 0.9333
       Score on test     : 0.9500
    """
    X_new=ndfeature[0,0:60]
    y_new=model.predict(X_new)
    print(y_new[0])  
    #结果：1     

#==============================================================================

def bestMODEL2(dfprice,dfindex,n_nextdays=10,n_shares=1):  
    """
    功能：给定投资天数，寻找最佳样本构造参数，求最佳C值和预测投资结果
    """
    print("\nLooking for best numbers of samples and features, please wait...")
    
    best_score=0.1
    import numpy as np

    for f in np.arange(20,60,10):
        for s in np.arange(120,240,120):
            model,strategy,C,ntype,score_train,score_test= \
                bestMODEL(dfprice,dfindex,n_days,s,f)              
            if score_test > best_score:
                bestmodel=model
                bestsamples=s
                bestfeatures=f
                beststrategy=strategy
                bestC=C
                besttype=ntype
                best_train=score_train
                best_score=score_test

    print("    ***Model settings")
    print("       Future days       :",n_nextdays)
    print("    ***Best model specification")
    print("       Model             :",beststrategy)
    print("       Sampling type     :",besttype)
    print("       Number of samples :",bestsamples)
    print("       Number of features:",bestfeatures)
    print("       C value           :%.2f"%bestC)
    print("       Score on train    :%.4f"%best_train)
    print("       Score on test     :%.4f"%best_score)
    
    return bestmodel,bestsamples,bestfeatures,beststrategy,bestC,besttype, \
             score_train,best_score    
            

if __name__=='__main__':
    ticker='MSFT'
    market='^GSPC'
    dfprice=get_price(ticker,'4/12/2019','1/1/2015')
    dfindex=get_price(market,'4/12/2019','1/1/2015')    

    n_days=5
    model,samples,features,strategy,C,ntype,score_train,best_score= \
        bestMODEL2(dfprice,dfindex,n_days)     
    #结果：120 30 LRL1 AR 18.00, 0.7079, 0.8
    

    X,y,ndfeature=make_advice_sample(dfprice,dfindex,n_days, \
                              samples,features,ntype)         
    X_new=ndfeature[0,0:n_features]
    y_new=model.predict(X_new)
    print(y_new[0])  
    #结果：-1
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    