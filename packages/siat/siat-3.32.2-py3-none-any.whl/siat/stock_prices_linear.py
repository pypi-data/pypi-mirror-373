# -*- coding: utf-8 -*-
"""
@function: 预测美股股价，教学演示用，其他用途责任自负
@model：线性模型，ols, righe, lasso, elasticnet
@version：v1.0，2019.4.4
@purpose: 仅限机器学习课程案例使用
@author: 王德宏，北京外国语大学国际商学院
"""

#=====================================================================
def get_stock_price(ticker,atdate,fromdate):
    """
    功能：抓取美股股价
    输出：指定美股的收盘价格序列，最新日期的股价排列在前
    ticker:美股股票代码
    atdate:当前日期，既可以是今天日期，也可以是一个历史日期，datetime类型
    fromdate:样本开始日期，尽量远的日期，以便取得足够多的原始样本，类型同atdate
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
    dfprice=get_stock_price('MSFT','4/3/2019','1/1/2015')
    dfprice.head(5)
    dfprice.tail(3)
    dfprice[dfprice.Date == '2019-03-29']
    dfprice[(dfprice.Date>='2019-03-20') & (dfprice.Date<='2019-03-29')]


#=====================================================================
def make_price_sample(dfprice,n_nextdays=1,n_samples=240,n_features=20):
    """
    功能：生成指定股票的价格样本
    ticker:美股股票代码
    n_nextdays:预测从atdate开始未来第几天的股价，默认为1
    n_samples:需要生成的样本个数，默认240个(一年的平均交易天数)
    n_features:使用的特征数量，默认20个(一个月的平均交易天数)
    """
    
    #提取收盘价，Series类型
    closeprice=dfprice.Close
    
    #将closeprice转换为机器学习需要的ndarray类型ndprice
    import numpy as np
    ndprice=np.asmatrix(closeprice,dtype=None)
    
    #生成第一个标签样本：标签矩阵y(形状：n_samples x 1)
    import numpy as np
    y=np.asmatrix(ndprice[0,0])
    #生成第一个特征样本：特征矩阵X(形状：n_samples x n_features)    
    X=ndprice[0,n_nextdays:n_features+n_nextdays]
    
    #生成其余的标签样本和特征样本 
    for i in range(1,n_samples):
        y_row=np.asmatrix(ndprice[0,i])
        y=np.append(y,y_row,axis=0)
    
        X_row=ndprice[0,(n_nextdays+i):(n_features+n_nextdays+i)]
        X=np.append(X,X_row,axis=0)
    
    return X,y,ndprice

if __name__=='__main__':
    fdprice=get_stock_price('MSFT','4/3/2019','1/1/2015')
    X,y,ndprice=make_price_sample(fdprice,1,240,20)
    y[:5]    
    y[2:5]  #第1行的序号为0
    X[:5]
    X[:-5]
    X[3-1,2-1]


#=====================================================================
def bestR1(X,y):
    """
    功能：给定特征矩阵和标签，使用岭回归，返回最优的alpha参数和模型
    最优策略：测试集分数最高，不管过拟合问题
    """
    
    import numpy as np
    #将整个样本随机分割为训练集和测试集
    from sklearn.model_selection import train_test_split
    X_train,X_test,y_train,y_test=train_test_split(X,y,random_state=0)

    #初始化alpha，便于判断上行下行方向
    alphalist=[0.001,0.0011,0.00999,0.01,0.01001,0.999,1,1.01, \
               9.99,10,10.01,99,100,101,999,1000,1001,10000]    
    
    from sklearn.linear_model import RidgeCV
    reg=RidgeCV(alphas=alphalist,cv=5,fit_intercept=True,normalize=True)

    reg.fit(X_train, y_train)
    score_train=reg.score(X_train, y_train)		
    score_test=reg.score(X_test, y_test)		
    alpha=reg.alpha_
    #print("%.5f, %.5f, %.5f"%(alpha,score_train,score_test))

    #确定alpha参数的优化范围
    if alpha in [0.001,0.01,1,2,10,100,1000,10000]:
        #print("%.5f, %.5f, %.5f"%(alpha,score_train,score_test))
        return reg,alpha,score_train,score_test

    if 0.001 < alpha < 0.01:
        alphalist1=np.arange(0.001,0.01,0.0005)
    if 0.01 < alpha < 1:
        alphalist1=np.arange(0.01,1,0.005)
    if 1 < alpha < 10:
        alphalist1=np.arange(1,10,0.01)
    if 10 < alpha < 100:
        alphalist1=np.arange(10,100,0.1)
    if 100 < alpha < 1000:
        alphalist1=np.arange(100,1000,1)
    if 1000 < alpha < 10000:
        alphalist1=np.arange(1000,10000,10)

    reg1=RidgeCV(alphas=alphalist1,cv=5,fit_intercept=True,normalize=True)
    reg1.fit(X_train, y_train)
    score1_train=reg1.score(X_train,y_train)		
    score1_test =reg1.score(X_test, y_test)		
    alpha1=reg1.alpha_
    
    #print("%.5f, %.5f, %.5f"%(alpha1,score1_train,score1_test))
    return reg1,alpha1,score1_train,score1_test
    

if __name__=='__main__':
    dfprice=get_stock_price('MSFT','4/3/2019','1/1/2015')    
    X,y,ndprice=make_price_sample(dfprice,1,240,20)  
    
    model,alpha,score_train,score_test=bestR1(X,y)
    print("%.5f, %.5f, %.5f"%(alpha,score_train,score_test))
    #结果：0.045，0.9277，0.8940
            
    X_new=ndprice[0,0:20]
    y_new=model.predict(X_new)
    print("%.2f"%y_new)  
    #结果：119.43
#=====================================================================
def bestL1(X,y):
    """
    功能：给定特征矩阵和标签，使用拉索回归，返回最优的alpha参数和模型
    最优策略：测试集分数最高，不管过拟合问题
    """
    import numpy as np
    #将整个样本随机分割为训练集和测试集
    from sklearn.utils import column_or_1d
    y=column_or_1d(y,warn=False)
    from sklearn.model_selection import train_test_split
    X_train,X_test,y_train,y_test=train_test_split(X,y,random_state=0)


    #初始alpha，便于判断上行下行方向
    alphalist=[0.001,0.0011,0.00999,0.01,0.01001,0.999,1,1.01,1.99,2,2.01, \
               9.99,10,10.01,99,100,101,999,1000,1001,10000]

    from sklearn.linear_model import LassoCV
    reg=LassoCV(alphas=alphalist,max_iter=10**6, \
                cv=5,fit_intercept=True,normalize=True)
    reg.fit(X_train, y_train)
    score_train=reg.score(X_train,y_train)		
    score_test =reg.score(X_test, y_test)		
    alpha=reg.alpha_
    #print("Step0: %.4f, %.5f, %.5f"%(alpha,score_train,score_test))

    #确定alpha参数的优化范围
    if alpha in [0.001,0.01,1,2,10,100,1000,10000]:
        #print("Step01: %.5f, %.5f, %.5f"%(alpha,score_train,score_test))
        return reg,alpha,score_train,score_test

    if 0.001 < alpha < 0.01:
        alphalist1=np.arange(0.0015,0.01,0.0005)

    if 0.01 < alpha < 1:
        alphalist1=np.arange(0.015,1,0.005)

    if 1 < alpha < 10:
        alphalist1=np.arange(1.01,10,0.01)

    if 10 < alpha < 100:
        alphalist1=np.arange(10.1,100,0.1)

    if 100 < alpha < 1000:
        alphalist1=np.arange(101,1000,1)

    if 1000 < alpha < 10000:
        alphalist1=np.arange(1010,10000,10)

    reg1=LassoCV(alphas=alphalist1,cv=5,fit_intercept=True,normalize=True)
    reg1.fit(X_train, y_train)
    score1_train=reg1.score(X_train,y_train)		
    score1_test =reg1.score(X_test, y_test)		
    alpha1=reg1.alpha_
    #print("Step1: %.4f, %.5f, %.5f"%(alpha1,score1_train,score1_test))
    return reg1,alpha1,score1_train,score1_test

if __name__=='__main__':
    dfprice=get_stock_price('MSFT','4/3/2019','1/1/2015')    
    X,y,ndprice=make_price_sample(dfprice,1,240,20)  
    
    model,alpha,score_train,score_test=bestL1(X,y)
    print("%.5f, %.5f, %.5f"%(alpha,score_train,score_test))
    #结果：0.015，0.9284，0.9043
            
    X_new=ndprice[0,0:20]
    y_new=model.predict(X_new)
    print("%.2f"%y_new) 
    #结果：119.37

#=====================================================================

def bestEN2(X,y,maxalpha=2):
    """
    功能：给定特征矩阵和标签，使用弹性网络回归，返回最优的alpha参数和模型
    最优策略：利用ElasticNetCV筛选机制，速度慢
    """
    #将整个样本随机分割为训练集和测试集
    from sklearn.utils import column_or_1d
    y=column_or_1d(y,warn=False)
    
    from sklearn.model_selection import train_test_split
    X_train,X_test,y_train,y_test=train_test_split(X,y,random_state=66)
    
    #限定参数范围
    import numpy as np
    alphalist=np.arange(0.01,maxalpha,0.01)
    l1list   =np.arange(0.01,1,0.01)

    from sklearn.linear_model import ElasticNetCV
    reg=ElasticNetCV(alphas=alphalist,l1_ratio=l1list)
    
    reg.fit(X_train, y_train)
    score_train=reg.score(X_train,y_train)		
    score_test =reg.score(X_test, y_test)		
    alpha=reg.alpha_
    l1ratio=reg.l1_ratio_    
    
    return reg,alpha,l1ratio,score_train,score_test

if __name__=='__main__':
    dfprice=get_stock_price('MSFT','4/3/2019','1/1/2015')    
    X,y,ndprice=make_price_sample(dfprice,1,240,20)  
    
    model,alpha,l1ratio,score_train,score_test=bestEN2(X,y)
    print("%.5f, %.5f, %.5f, %.5f"%(alpha,l1ratio,score_train,score_test))
    #结果：0.42，0.99，0.9258，0.9174
            
    X_new=ndprice[0,0:20]
    y_new=model.predict(X_new)
    print("%.2f"%y_new) 
    #结果：119.60
 
#=======    
   
#==============================================================================

def bestEN3(X,y):
    """
    功能：给定特征矩阵和标签，使用弹性网络回归，返回最优的alpha参数和模型
    最优策略：利用cv交叉验证，速度快
    算法贡献者：徐乐欣(韩语国商)
    """
    import numpy as np
    #将整个样本随机分割为训练集和测试集
    from sklearn.utils import column_or_1d
    y=column_or_1d(y,warn=False)
    from sklearn.model_selection import train_test_split
    X_train,X_test,y_train,y_test=train_test_split(X,y,random_state=66)
    
    from sklearn.linear_model import ElasticNetCV
    #reg=ElasticNetCV(cv=5, random_state=0)
    #reg.fit(X,y)
    
    l1list=np.arange(0.01,1,0.01)
    ENet=ElasticNetCV(alphas=None, copy_X=True, cv=5, eps=0.001, \
                      fit_intercept=True,l1_ratio=l1list, max_iter=8000, \
                      n_alphas=100, n_jobs=None,normalize=True, \
                      positive=False, precompute='auto', random_state=0, \
                      selection='cyclic', tol=0.0001, verbose=0)
    ENet.fit(X_train, y_train)
    score_train=ENet.score(X_train, y_train)		
    score_test=ENet.score(X_test, y_test)		
    alpha=ENet.alpha_
    l1ratio=ENet.l1_ratio_
    #print("S1: %.5f, %.5f, %.5f, %.5f"%(alpha,l1ratio,score_train,score_test))    

    return ENet,alpha,l1ratio,score_train,score_test

if __name__=='__main__':
    dfprice=get_stock_price('MSFT','4/3/2019','1/1/2015')    
    X,y,ndprice=make_price_sample(dfprice,1,240,20)  
    
    model,alpha,l1ratio,score_train,score_test=bestEN3(X,y)
    print("%.5f, %.5f, %.5f, %.5f"%(alpha,l1ratio,score_train,score_test))
    #结果：0.005836，0.99，0.925，0.9194
            
    X_new=ndprice[0,0:20]
    y_new=model.predict(X_new)
    print("%.2f"%y_new) 
    #结果：119.48
#==============================================================================


def bestEN1(X,y,maxalpha=2):
    """
    功能：给定特征矩阵和标签，使用弹性网络回归，返回最优的alpha参数和模型
    最优策略：对alpha和l1_ratio进行暴力枚举，搜索最高测试集分数，速度中等
    算法贡献者：徐乐欣(韩语国商)
    """
    
    #将整个样本随机分割为训练集和测试集
    from sklearn.utils import column_or_1d
    y=column_or_1d(y,warn=False)
    from sklearn.model_selection import train_test_split
    X_train,X_test,y_train,y_test=train_test_split(X,y,random_state=66)
    
    #设立初始测试集分数门槛
    king_score=0.6
    from sklearn.linear_model import ElasticNet

    #限定参数范围
    import numpy as np
    alphalist=np.arange(0.01,maxalpha,0.01)
    l1list   =np.arange(0.01,1,0.01)

    for i in alphalist:
        for j in l1list:
            reg=ElasticNet(alpha=i,l1_ratio=j)
            reg.fit(X_train,y_train)
            temp_score=reg.score(X_test,y_test)
            if temp_score > king_score:
                king_score=temp_score
                alpha=i
                l1ratio=j
                score_train=reg.score(X_train,y_train)
                score_test=temp_score
                model=reg
    
    return model,alpha,l1ratio,score_train,score_test

if __name__=='__main__':
    dfprice=get_stock_price('MSFT','4/3/2019','1/1/2015')    
    X,y,ndprice=make_price_sample(dfprice,1,240,20)  
    
    model,alpha,l1ratio,score_train,score_test=bestEN1(X,y)
    print("%.5f, %.5f, %.5f, %.5f"%(alpha,l1ratio,score_train,score_test))
    #结果：1.31，0.56，0.9241，0.9196
            
    X_new=ndprice[0,0:20]
    y_new=model.predict(X_new)
    print("%.2f"%y_new) 
    #结果：119.36
#==============================================================================






#==============================================================================
    