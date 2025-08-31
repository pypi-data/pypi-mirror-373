# -*- coding: utf-8 -*-

"""
本模块功能：机器学习课程演示案例和基础函数，仅限课堂案例演示用
创建日期：2022年3月25日
最新修订日期：
作者：王德宏 (WANG Dehong, Peter)
作者单位：北京外国语大学国际商学院
用途限制：仅限研究与教学使用，不可商用！商用需要额外授权。
特别声明：作者不对使用本工具进行证券投资导致的任何损益负责！
"""

#==============================================================================
#关闭所有警告
import warnings; warnings.filterwarnings('ignore')
import warnings; warnings.filterwarnings('ignore')
from siat.common import *
from siat.translate import *
from siat.grafix import *
from siat.security_prices import *

#==============================================================================
def ml_demo_iris_matrix():
    """
    功能：机器学习开门课程的演示案例，显示影响鸢尾花品种识别的矩阵图
    输入：无
    显示：鸢尾花花萼/花瓣长宽特征对于品种分类的影响
    输出：无
    """
    
    #设置绘图时的汉字显示 
    import matplotlib.pyplot as plt
    plt.rcParams['font.sans-serif'] = ['FangSong'] 
    plt.rcParams['axes.unicode_minus'] = False 
    
    #装入鸢尾花数据集
    from sklearn.datasets import load_iris
    iris_dataset = load_iris()
    
    #分割样本为两部分：训练集和测试集
    from sklearn.model_selection import train_test_split 
    X_train, X_test, y_train, y_test = train_test_split(iris_dataset.data, iris_dataset.target, random_state=0)
        
    #为了绘图需要，将样本转换成数据表格式
    import pandas as pd
    iris_dataframe = pd.DataFrame(X_train, columns=iris_dataset.feature_names)
    iris_dataframe.rename(columns={'sepal length (cm)':'花萼长(厘米)','sepal width (cm)':'花萼宽(厘米)','petal length (cm)':'花瓣长(厘米)','petal width (cm)':'花瓣宽(厘米)'}, inplace = True)
    
    #绘制训练集的散点图，观察特征值对于标签的区分度
    import mglearn
    import pandas.plotting as pdp
    #figsize为画布大小，marker为散点形状，s为散点大小，alpha为透明度，bins为直方图的条数，cmap为调色板(colormap)，c为着色对象（根据着色对象的不同值着不同颜色）
    grr = pdp.scatter_matrix(iris_dataframe, c=y_train, figsize=(15, 15), marker='o',hist_kwds={'bins': 20}, s=60, alpha=.8, cmap=mglearn.cm3)
    #换个调色板试试：红绿粉色
    grr = pdp.scatter_matrix(iris_dataframe, c=y_train, figsize=(15, 15), marker='o',hist_kwds={'bins': 20}, s=60, alpha=.8, cmap=plt.cm.gist_rainbow)
    #再换个调色板试试：蓝绿锗色
    grr = pdp.scatter_matrix(iris_dataframe, c=y_train, figsize=(15, 15), marker='o',hist_kwds={'bins': 20}, s=60, alpha=.8, cmap='jet')

    return


if __name__=='__main__':
    ml_demo_iris_matrix()

if __name__=='__main__':
    n_neighbors=5
    weights='uniform'
    algorithm='auto'
    leaf_size=30
    p=2
    metric='minkowski'
    metric_params=None
    n_jobs=None
    
def ml_demo_iris_learn(n_neighbors=5,weights='uniform',algorithm='auto', \
                       leaf_size=30,p=2,metric='minkowski',metric_params=None,n_jobs=None):
    """
    功能：机器学习开门课程的演示案例，学习鸢尾花品种识别
    输入：无
    显示：学习效果，有无过拟合
    输出：学习后的模型，用于预测未知的鸢尾花品种
    注意：需要安装mglearn轮子
    """
    print("\n  开始进行鸢尾花品种识别 ... ...")
    
    #设置绘图时的汉字显示 
    import matplotlib.pyplot as plt
    plt.rcParams['font.sans-serif'] = ['FangSong'] 
    plt.rcParams['axes.unicode_minus'] = False 
    
    #装入鸢尾花数据集
    print("  装入供学习的鸢尾花品种样本 ...")
    from sklearn.datasets import load_iris
    iris_dataset = load_iris()
    print("  鸢尾花品种样本总数:",len(iris_dataset.data))
    print("  鸢尾花品种名称:",iris_dataset.target_names)
    print("  鸢尾花特征名称:",iris_dataset.feature_names)
    
    #分割样本为两部分：训练集和测试集
    print("\n  将鸢尾花品种样本按3:1随机拆分训练集和测试集 ...")
    from sklearn.model_selection import train_test_split 
    X_train, X_test, y_train, y_test = train_test_split(iris_dataset.data, iris_dataset.target, random_state=0)
    print("  训练集/测试集样本总数:",len(y_train.data),'/',len(y_test.data))

    
    # 引入最近邻分类模型：
    from sklearn.neighbors import KNeighborsClassifier
    #将模型实例化(初始化)
    print("\n  开始学习训练集：使用最近邻模型 ...")
    knn = KNeighborsClassifier(n_neighbors=n_neighbors,weights=weights, \
            algorithm=algorithm,leaf_size=leaf_size,p=p,metric=metric, \
                metric_params=metric_params,n_jobs=n_jobs)
    print("  模型的邻居个数、权重、距离测度:",n_neighbors,'\b,',weights,'\b,',metric)
        
    #让模型“学习”训练集增长“见识”，以便能够识别未知的鸢尾花品种（回归+拟合）
    knn.fit(X_train, y_train)
    
    #学习结果成绩：97.32%
    train_score=knn.score(X_train, y_train)
    print("  训练集学习完毕，识别率:",round(train_score,4))
    
    #使用测试集评估模型的“学习成绩”：
    test_score=knn.score(X_test, y_test)
    print("  使用未知的测试集进行检验，识别率:",round(test_score,4))

    #返回模型
    return knn

if __name__=='__main__':
    model=knn
    new_iris=[5,2.9,1,0.2]
    
def ml_demo_iris_check(model,new_iris):
    """
    功能：基于已学习的模型model，预测一株鸢尾花new_iris属于什么品种
    输入：模型，新鸢尾花的数据[花萼长,花萼宽,花瓣长,花瓣宽]
    显示：预测的品种名称
    """
    print("\n  开始进行鸢尾花品种识别 ... ...")
    print("  新鸢尾花的特征：花萼花瓣长宽为",new_iris)
    
    #构造一株新鸢尾花的特征数据
    import numpy as np
    X_new = np.array([new_iris])

    #利用机器学习的经验进行品种识别
    prediction = model.predict(X_new)
    probability = model.predict_proba(X_new)
    
    #显示识别的结果：鸢尾花的品种名称
    iris_names=['setosa','versicolor','virginica']
    id=prediction[0]
    iris_name=iris_names[id]
    print("  基于机器学习的结果，判断该鸢尾花的品种:",iris_name)
    print("  判断该鸢尾花品种的把握度:",probability[0,0]*100,'\b%')
    
    return
    
if __name__=='__main__':
    knn=ml_demo_iris_learn()   
    ml_demo_iris_check(knn,new_iris)


#==============================================================================
#定义函数：欧几里得距离
from math import *
def eculidean_distance(xi, xj):    
    distance = sqrt(sum(pow(a - b, 2) for a, b in zip(xi, xj)))
    return distance

if __name__ =="__main__":
    #示例：结果为3.873
    xi = [1, 3, 2, 4]
    xj = [2, 5, 3, 1]
    print(eculidean_distance(xi, xj))  

#定义函数：曼哈顿距离
def manhattan_distance(xi, xj):
    distance = sum(abs(a - b) for a, b in zip(xi, xj))
    return distance

if __name__ =="__main__":
    #示例：结果为7
    xi = [1, 3, 2, 4]
    xj = [2, 5, 3, 1]
    print(manhattan_distance(xi, xj))   

#定义函数：闵可夫斯基距离
def minkowski_distance(xi, xj, p):
    sumval = sum(pow(abs(a - b), p) for a, b in zip(xi, xj))
    mi = 1/ float(p)
    distance = sumval ** mi
    return distance

if __name__ =="__main__":
    #示例：结果为3.332
    xi = [1, 3, 2, 4]
    xj = [2, 5, 3, 1]
    print(minkowski_distance(xi, xj, 3))   

#定义函数：切比雪夫距离，相当于空间曼哈顿距离
def chebyshev_distance(xi, xj):
    distance = max(abs(a - b) for a, b in zip(xi, xj))
    return distance

if __name__ =="__main__":
    #示例：结果为3
    xi = [1, 3, 2, 4]
    xj = [2, 5, 3, 1]
    print(chebyshev_distance(xi, xj)) 

#定义函数：余弦相似度  
import numpy as np
def cosine_similarity(xi, xj):    
    numerator = sum(map(float, xi * xj))    
    #求向量(矩阵)的范数：np.linalg.norm
    denominator = np.linalg.norm(xi) * np.linalg.norm(xj) 
    similarity = numerator / float(denominator)  
    return similarity

if __name__ =="__main__":
    # 示例：结果为1，是相同的两个向量
    xi = np.array([3, 4, 1, 5])
    xj = np.array([3, 4, 1, 5])
    print(cosine_similarity(xi, xj)) 


#距离的通用算法：pdist
def universal_distance(xi,xj,option='minkowski',p=3):
    """
    功能：统一的距离算法
    """
    #支持的距离选项
    option_list = [
                    'braycurtis', 
                    'canberra', 
                    'chebyshev', #切比雪夫距离
                    'cityblock', #曼哈顿距离
                    'correlation', 
                    'cosine', #余弦相似度
                    'dice', 
                    'euclidean', #欧几里得距离
                    'hamming', 
                    'jaccard', 
                    'jensenshannon', 
                    'kulsinski', 
                    'mahalanobis', #著名的马氏距离
                    'matching', 
                    'minkowski', #闵可夫斯基距离, 有p参数
                    'rogerstanimoto', 
                    'russellrao', 
                    'seuclidean', #标准化欧几里得距离
                    'sokalmichener', 
                    'sokalsneath', 
                    'sqeuclidean', 
                    'yule']  
    if not (option in option_list):
        print("  不支持的距离测度方法:",option)
        print("  支持的距离测度方法:",option_list)
        return
    
    from scipy.spatial.distance import pdist
    X=np.vstack([xi, xj])
    distance=pdist(X, option, parm)   
    
    return distance


#==============================================================================
#==============================================================================
#==============================================================================

def get_stock_price(ticker,atdate,fromdate):
    """
    功能：抓取股票收盘价
    输出：指定股票的收盘价格序列，最新日期的股价排列在前
    ticker:股票代码
    atdate:当前日期，既可以是今天日期，也可以是一个历史日期，datetime类型
    fromdate:样本开始日期，尽量远的日期，以便取得足够多的原始样本，类型同atdate
    """
    #抓取股票价格
    try:
        price=get_price(ticker,fromdate,atdate)
    except:
        print(".Error(get_stock_price), failed to capture stock prices:",ticker,fromdate,atdate)
        return None    
    #去掉比起始日期更早的样本
    #price=price[price.index >= fromdate]

    #按日期降序排序，近期的价格排在前面
    sortedprice=price.sort_index(axis=0,ascending=False)

    #提取日期和星期几
    sortedprice['Date']=sortedprice.index.strftime("%Y-%m-%d")
    sortedprice['Weekday']=sortedprice.index.weekday+1
    
    #生成输出数据格式：日期，星期几，收盘价
    dfprice=sortedprice[['Date','Weekday','Close']]
    
    return dfprice
    

if __name__=='__main__':
    ticker='MSFT'
    atdate='4/2/2020'
    fromdate='1/1/2015'    
    dfprice=get_stock_price('MSFT','4/2/2020','1/1/2015')
    dfprice.head(5)
    dfprice.tail(3)
    dfprice[dfprice.Date == '2019-03-29']
    dfprice[(dfprice.Date>='2019-03-20') & (dfprice.Date<='2019-03-29')]


#==============================================================================
def make_price_sample(dfprice,n_nextdays=1,n_samples=252,n_features=21):
    """
    功能：生成指定股票的价格样本
    ticker:股票代码
    n_nextdays:预测从atdate开始未来第几天的股价，默认为1
    n_samples:需要生成的样本个数，默认252个(一年的平均交易天数)
    n_features:使用的特征数量，默认21个(一个月的平均交易天数)
    """
    #检查样本数量是否够用
    n_req=n_features+n_nextdays+n_samples
    if len(dfprice) < n_req:
        print(".Error(make_price_sample), need more number of stock prices!")
        print("...There are only",len(dfprice),"obs in the stock price file")
        print("...But, I need at least",n_req,"obs to make ML samples")
        return None,None,None
    
    #提取收盘价，Series类型
    closeprice=dfprice.Close
    
    #转换为机器学习需要的ndarray类型
    import numpy as np
    ndprice=np.asmatrix(closeprice,dtype=None)
    
    #生成第一个标签样本：标签矩阵y(形状：n_samples x 1)
    y=np.asmatrix(ndprice[0,0])
    #生成第一个特征样本：特征矩阵X(形状：n_samples x n_features)    
    X=ndprice[0,n_nextdays:n_features+n_nextdays]
    
    #生成其余的标签样本和特征样本 
    for i in range(1,n_samples):
        #加入到标签矩阵中
        y_row=np.asmatrix(ndprice[0,i])
        y=np.append(y,y_row,axis=0)
        #加入到特征矩阵中
        X_row=ndprice[0,(n_nextdays+i):(n_features+n_nextdays+i)]
        X=np.append(X,X_row,axis=0)
    
    return X,y,ndprice

if __name__=='__main__':
    dfprice=get_stock_price('LK','4/3/2020','1/1/2015')
    X,y,ndprice=make_price_sample(dfprice,1,200,21)
    y[:5]    
    y[2:5]  #第1行的序号为0
    X[:5]
    X[:-5]
    X[3-1,2-1]


#==============================================================================
def bestKN(X,y,maxk=10,random_state=0):
    """
    功能：给定特征矩阵和标签，返回最优的邻居个数(默认最大为10)和模型
    最优策略：测试集分数最高，不管过拟合问题
    """
    #随机分割样本为训练集和测试集
    from sklearn.model_selection import train_test_split
    X_train,X_test,y_train,y_test=train_test_split(X,y,random_state=random_state)
        
    #引用k近邻模型的预测器(Regressor)
    from sklearn.neighbors import KNeighborsRegressor
    bestk=1
    reg=KNeighborsRegressor(n_neighbors=bestk,weights='distance',n_jobs=-1)
    reg.fit(X_train,y_train)
    bestmodel=reg
    bestscore_train=bestmodel.score(X_train,y_train)
    bestscore_test =bestmodel.score(X_test,y_test)       
    
    for k in range(2,(maxk+1)):
        reg=KNeighborsRegressor(n_neighbors=k,weights='distance',n_jobs=-1)
        reg.fit(X_train,y_train)
        score_train=reg.score(X_train,y_train)
        score_test =reg.score(X_test,y_test) 
                
        if score_test > bestscore_test:
            bestk=k
            bestscore_train=score_train
            bestscore_test =score_test
            bestmodel=reg
    
    return bestmodel,bestk,bestscore_train,bestscore_test

if __name__=='__main__':
    dfprice=get_stock_price('MSFT','4/3/2019','1/1/2015')    
    X,y,ndprice=make_price_sample(dfprice,1,240,20)    
    bestmodel,bestk,bestscore_train,bestscore_test=bestKN(X,y)
    print(bestk,bestscore_train,bestscore_test)


#==============================================================================
def bestFN(dfprice,n_nextdays=1,n_samples=252,maxFN=252,random_state=0):
    """
    功能：给定股价序列，试验最优的特征个数(默认最大为60)和模型
    最优策略：测试集分数最高，不管过拟合问题
    """
    #试验起点：1个特征个数
    bestf=1
    X,y,ndprice=make_price_sample(dfprice,n_nextdays,n_samples,bestf)
    #测试给定特征个数时的最优邻居个数
    bestmodel,bestk,bestscore_train,bestscore_test=bestKN(X,y,random_state=random_state)
    
    #特征个数增长的步长
    n_step=1
    for f in range(2,maxFN+1,n_step): 
        if len(dfprice) < (n_nextdays+n_samples+f): break
        X,y,ndprice=make_price_sample(dfprice,n_nextdays,n_samples,f)
        model,k,score_train,score_test=bestKN(X,y,random_state=random_state)
        
        if score_test > bestscore_test:
            bestf=f
            bestk=k
            bestscore_train=score_train
            bestscore_test =score_test
            bestmodel=model
    
    #返回测试集效果最好的模型、特征个数、邻居个数、成绩
    return bestmodel,bestf,bestk,bestscore_train,bestscore_test

if __name__=='__main__':
    dfprice=get_stock_price('MSFT','4/4/2020','1/1/2015')   
    bestmodel,bestf,bestk,bestscore_train,bestscore_test= \
        bestFN(dfprice,1,252)
    
    print("best f=",bestf,",best k=",bestk, \
          "\nbest score on train=",bestscore_train, \
          "\nbest score on test=",bestscore_test)  


#==============================================================================
def bestKN2(X,y,maxk=10,random_state=0):
    """
    功能：给定特征矩阵和标签，返回最优的邻居个数(默认最大为10)和模型
    最优策略2：训练集和测试集分数最接近，希望控制过拟合和欠拟合问题
    """
    #随机分割样本为训练集和测试集
    from sklearn.model_selection import train_test_split
    X_train,X_test,y_train,y_test=train_test_split(X,y,random_state=random_state)
        
    #引用k近邻模型的预测器(Regressor)
    from sklearn.neighbors import KNeighborsRegressor
    bestk=1
    reg=KNeighborsRegressor(n_neighbors=bestk,weights='distance',n_jobs=-1)
    reg.fit(X_train,y_train)
    bestmodel=reg
    bestscore_train=reg.score(X_train,y_train)
    bestscore_test =reg.score(X_test,y_test)
    
    import numpy as np
    bestrate=np.abs(bestscore_train / bestscore_test -1)
    
    for k in range(2,(maxk+1)):
        reg=KNeighborsRegressor(n_neighbors=k,weights='distance',n_jobs=-1)
        reg.fit(X_train,y_train)
        score_train=reg.score(X_train,y_train)
        score_test =reg.score(X_test,y_test)
        rate=np.abs(score_train / score_test -1)
        
        if rate < bestrate:
            bestk=k
            bestrate=rate
            bestscore_train=score_train
            bestscore_test =score_test
            bestmodel=reg
    return bestmodel,bestk,bestscore_train,bestscore_test,bestrate

if __name__=='__main__':
    dfprice=get_stock_price('MSFT','3/27/2019','1/1/2015')    
    X,y,ndprice=make_price_sample(dfprice,1,252,21)   
    
    bestmodel,bestk,bestscore_train,bestscore_test=bestKN(X,y)
    print("best k=",bestk,"\nbest score on train=",bestscore_train, \
          ",best score on test=",bestscore_test)
    
    bestmodel,bestk,bestscore_train,bestscore_test,bestrate=bestKN2(X,y)
    print("best k=",bestk,"\nbest score on train=",bestscore_train, \
          ",best score on test=",bestscore_test)


  
#==============================================================================
def bestFN2(dfprice,n_nextdays=1,n_samples=252,maxFN=252,random_state=0):
    """
    功能：给定股价序列，试验最优的特征个数(默认最大为252)和模型
    最优策略2：训练集和测试集分数最接近，希望控制过拟合和欠拟合问题
    """
    #试验起点：1个特征个数
    bestf=1
    X,y,ndprice=make_price_sample(dfprice,n_nextdays,n_samples,bestf)
    #测试给定特征个数时的最优邻居个数
    bestmodel,bestk,bestscore_train,bestscore_test,bestrate=bestKN2(X,y,random_state=random_state)
    
    #特征个数增长的步长
    n_step=1
    for f in range(2,maxFN+1,n_step): 
        if len(dfprice) < (n_nextdays+n_samples+f): break
        X,y,ndprice=make_price_sample(dfprice,n_nextdays,n_samples,f)
        model,k,score_train,score_test,rate=bestKN2(X,y,random_state=random_state)
        
        if rate < bestrate:
            bestf=f
            bestk=k
            bestscore_train=score_train
            bestscore_test =score_test
            bestrate=rate
            bestmodel=model
    
    #返回测试集效果最好的模型、特征个数、邻居个数、成绩
    return bestmodel,bestf,bestk,bestscore_train,bestscore_test,bestrate

if __name__=='__main__':
    dfprice=get_stock_price('MSFT','3/27/2019','1/1/2015')   
    bestmodel,bestf,bestk,bestscore_train,bestscore_test= \
        bestFN(dfprice,1,252)    
    print("best f=",bestf,",best k=",bestk, \
          "\nbest score on train=",bestscore_train, \
          "\nbest score on test=",bestscore_test)  

    bestmodel,bestf,bestk,bestscore_train,bestscore_test= \
        bestFN2(ndprice,1,252)    
    print("best f=",bestf,",best k=",bestk, \
          "\nbest score on train=",bestscore_train, \
          "\nbest score on test=",bestscore_test)  

#==============================================================================
def isdate(adate):
    """
    功能：根据日期的合理性
    输入参数：
    adate：日期。格式：YYYY-MM-DD
    输出：无
    返回：有效/无效日期（True/False）
    """
    import pandas as pd
    #测试开始日期的合理性
    try: adatedt=pd.to_datetime(adate)
    except: return False
    else: return True
    
#==============================================================================
def date_adjust(basedate, adjust=0):
    """
    功能：将给定日期向前或向后调整特定的天数
    输入：基础日期，需要调整的天数。
    basedate: 基础日期。
    adjust：需要调整的天数，负数表示向前调整，正数表示向后调整。
    输出：调整后的日期。
    """
    #检查基础日期的合理性
    import pandas as pd    
    try:
        bd=pd.to_datetime(basedate)
    except:
        print("*** 错误#1(date_adjust)，无效的日期:",basedate)
        return None

    #调整日期
    from datetime import timedelta
    nd = bd+timedelta(days=adjust)    
    
    #重新提取日期
    newdate=nd.date()   
    return str(newdate)
 
if __name__ =="__main__":
    basedate='2020-3-17' 
    adjust=-365    
    newdate = date_adjust(basedate, adjust)
    print(newdate)    
    
#==============================================================================
def forecast_stock_price(ticker,atdate,n_nextdays,n_samples=252, \
                         maxk=20,maxFN=252,random_state=0,printout=True):
    """
    功能：预测未来第几天的股票收盘价，执行FN和FN2优化策略
    """
    #检查日期的合理性
    if not isdate(atdate):
        print(".Error(forecast_stock_price), invalid date:",atdate)
        return None
    
    print("..Predicting stock price, it may take long time, please wait ......")
    
    #设定起始日期：
    nyears=int((n_nextdays + n_samples + maxFN + 1)/252)+2
    start=date_adjust(atdate,-366*nyears)
    
    #抓取股价数据
    dfprice=get_stock_price(ticker,atdate,start)
    if dfprice is None:
        print(".Error(forecast_stock_price), failed to capture stock prices:",ticker)
        return None        
    if len(dfprice) < (n_nextdays + n_samples + maxFN + 1):
        print(".Error(forecast_stock_price), insufficient number of stock prices!")
        return None     
    
    #生成机器学习样本1: 确定最佳特征个数bestf，不管过拟合/欠拟合问题
    bestmodel1,bestf1,bestk1,bestscore_train1,bestscore_test1= \
        bestFN(dfprice,n_nextdays,n_samples,random_state=random_state)
    X,y,ndprice=make_price_sample(dfprice,n_nextdays,n_samples,bestf1)
    
    #基于最新特征样本X_new，预测第n_nextdays的股价    
    X_new1=ndprice[0,0:bestf1]
    y_new1=bestmodel1.predict(X_new1)

    
    #生成机器学习样本2: 确定最佳特征个数bestf，考虑过拟合/欠拟合问题
    bestmodel2,bestf2,bestk2,bestscore_train2,bestscore_test2,bestrate2= \
        bestFN2(dfprice,n_nextdays,n_samples)
    X,y,ndprice=make_price_sample(dfprice,n_nextdays,n_samples,bestf2)
    X_new2=ndprice[0,0:bestf2]
    y_new2=bestmodel2.predict(X_new2)

    
    #最终决定：以最大测试成绩为优先
    if bestscore_test1 <= bestscore_test2:
        predicted_y=y_new2[0,0]
        bestscore_train=bestscore_train2
        bestscore_test=bestscore_test2
        bestfeature=bestf2
        bestk=bestk2
    else:
        predicted_y=y_new1[0,0]
        bestscore_train=bestscore_train1
        bestscore_test=bestscore_test1
        bestfeature=bestf1
        bestk=bestk1
    if printout:
        print("    Forecasted price:%10.2f" % predicted_y)
        print("    Best score on train:",round(bestscore_train,4))
        print("    Best score on test:",round(bestscore_test,4))        
        print("    Best number of features:",bestfeature)
        print("    Best number of neighbors:",bestk)
        
    return predicted_y,bestscore_train,bestscore_test,bestfeature,bestk

 
if __name__ =="__main__":
    ticker='MSFT'
    atdate="2020-4-2"
    n_nextdays=1
    info=forecast_stock_price(ticker,atdate,n_nextdays)
    print(info)  

#==============================================================================
def forecast_stock_price2(dfprice,n_nextdays,n_samples=252, \
                         maxk=20,maxFN=252,random_state=0):
    """
    功能：预测未来第几天的股票收盘价，执行FN和FN2优化策略，单一随机数种子
    """
    #生成机器学习样本1: 确定最佳特征个数bestf，不管过拟合/欠拟合问题
    bestmodel1,bestf1,bestk1,bestscore_train1,bestscore_test1= \
        bestFN(dfprice,n_nextdays,n_samples,random_state=random_state)
    X,y,ndprice=make_price_sample(dfprice,n_nextdays,n_samples,bestf1)
    
    #基于最新特征样本X_new，预测第n_nextdays的股价    
    X_new1=ndprice[0,0:bestf1]
    y_new1=bestmodel1.predict(X_new1)

    
    #生成机器学习样本2: 确定最佳特征个数bestf，考虑过拟合/欠拟合问题
    bestmodel2,bestf2,bestk2,bestscore_train2,bestscore_test2,bestrate2= \
        bestFN2(dfprice,n_nextdays,n_samples)
    X,y,ndprice=make_price_sample(dfprice,n_nextdays,n_samples,bestf2)
    X_new2=ndprice[0,0:bestf2]
    y_new2=bestmodel2.predict(X_new2)
    
    #最终决定：以最大测试成绩为优先
    if bestscore_test1 <= bestscore_test2:
        predicted_y=y_new2[0,0]
        bestscore_train=bestscore_train2
        bestscore_test=bestscore_test2
        bestfeature=bestf2
        bestk=bestk2
    else:
        predicted_y=y_new1[0,0]
        bestscore_train=bestscore_train1
        bestscore_test=bestscore_test1
        bestfeature=bestf1
        bestk=bestk1
        
    return round(predicted_y,2),round(bestscore_train,4), \
        round(bestscore_test,4),bestfeature,bestk

 
if __name__ =="__main__":
    ticker='MSFT'
    atdate="2020-4-2"
    n_nextdays=1
    dfprice=get_stock_price('MSFT','4/2/2020','1/1/2015')
    info=forecast_stock_price2(dfprice,n_nextdays)
    print(info)  

#==============================================================================
def weighted_median(df,colname,colweight):
    """
    功能：求加权中位数
    输入：数据表df, 需要求中位数的列名colname, 权重所在的列名colweight
    返回：50%中位数数值
    """
    from statsmodels.stats.weightstats import DescrStatsW
    wdf = DescrStatsW(df[colname], weights=df[colweight], ddof=1) 

    if len(df) >= 3:
        wmedianlist=list(wdf.quantile([0.50]))
        wmedian=wmedianlist[0]    
    elif len(df) == 2:
        wmedian=(df[colname][0]*df[colweight][0]+df[colname][1]*df[colweight][1])/(df[colweight][0]+df[colweight][1])
    elif len(df) == 1:
        wmedian=df[colname][0]
    else:
        return None
    
    return wmedian

if __name__ =="__main__":
    import pandas as pd
    df=pd.DataFrame({ 'x':range(1,3), 'wt':range(1,3) })
    colname='x'
    colweight='wt'
    weighted_median(df,colname,colweight)

#==============================================================================
def second2time(seconds):
    """
    功能：将秒数转换为时分秒
    输入：秒数
    返回：时分秒，字符串
    """
    hours=int(seconds/3600)
    minutes=int((seconds-hours*3600)/60)
    
    if seconds >= 60:
        decm=1
    elif seconds >= 10:
        decm=1
    elif seconds >= 0.1:
        decm=2
    else:
        decm=4
    miaos=round(seconds-hours*3600-minutes*60,decm)
    timestr=str(hours)+":"+str(minutes)+":"+str(miaos)
    
    return timestr

if __name__ =="__main__":
    second2time(590.58963)
    second2time(65.456321)
    second2time(35.75698)
    second2time(5.75698)
    second2time(0.75698)
    second2time(0.00098)
#==============================================================================
def save_to_excel(df,excelfile="myfile01.xlsx",sheetname="Sheet1"):
    """
    函数功能：将df保存到当前目录下的Excel文件。
    如果未指定Excel文件则默认为"myfile.xls"
    如果Excel文件不存在则创建文件并保存到指定的sheetname；如果未指定sheetname则默
    认为"First"
    如果Excel文件存在但sheetname不存在则增加sheetname并保存df内容，原有sheet内容
    不变；
    如果Excel文件和sheetname都存在则追加df内容到已有sheet的末尾
    输入参数：
    df: 数据框
    excelfile: Excel文件名，不带目录，后缀为.xls或.xlsx
    sheetname：Excel文件中的sheet名
    输出：
    保存df到Excel文件
    无返回数据
    注意：如果df中含有以文本表示的数字，写入到Excel会被自动转换为数字类型保存。
    从Excel中读出后为数字类型，因此将会与df的类型不一致
    """
    #取得df字段列表
    dflist=list(df)
    #合成完整的带目录的文件名
    filename=excelfile
    
    import pandas as pd
    try:
        file1=pd.ExcelFile(excelfile)
    except:
        #不存在excelfile文件，直接写入
        df.to_excel(filename,sheet_name=sheetname, \
                       header=True,encoding='utf-8')
        print("*** Results saved in",filename,"@ sheet",sheetname)
        return
    else:
        #已存在excelfile文件，先将所有sheet的内容读出到dict中        
        dict=pd.read_excel(file1, None)
    file1.close()
    
    #获得所有sheet名字
    sheetlist=list(dict.keys())
    #检查新的sheet名字是否已存在
    try:
        pos=sheetlist.index(sheetname)
    except:
        #不存在重复
        dup=False
    else:
        #存在重复，合并内容
        dup=True
        #合并之前可能需要对df中以字符串表示的数字字段进行强制类型转换.astype('int')
        df1=dict[sheetlist[pos]][dflist]
        dfnew=pd.concat([df1,df],axis=0,ignore_index=True)        
        dict[sheetlist[pos]]=dfnew
    
    #将原有内容写回excelfile    
    result=pd.ExcelWriter(filename)
    for s in sheetlist:
        df1=dict[s][dflist]
        df1.to_excel(result,s,header=True,index=True,encoding='utf-8')
    #写入新内容
    if not dup: #sheetname未重复
        df.to_excel(result,sheetname,header=True,index=True,encoding='utf-8')
    try:
        result.save()
        result.close()
    except:
        print("... Error(save_to_excel): writing file failed",filename,"@ sheet",sheetname)
        print("Information:",filename)  
        return
    print("*** Results saved in",filename,"@ sheet",sheetname)
    
    return    


#==============================================================================
def forecast_stock_price_rs(ticker,atdate,n_nextdays=1,n_samples=252, \
                         maxk=20,maxFN=252,random_state=0,maxRS=9, \
                         excelfile="myfile01.xlsx",sheetname="Sheet1"):
    """
    功能：预测未来第几天的股票收盘价，试验随机数种子策略
    输入参数：
        1、ticker: 股票代码
        2、atdate: 当前日期，可以是今天或以前的一天
        3、n_nextdays: 以atdate为基准向前推进几个交易日，预测该日期的股价
        4、n_samples: 生成机器学习用的样本中的最大观察数目。
           跨年的样本有助于模型学习季节性效应，3年的样本效果好于2年，
           2年的样本效果好于1年
        5、maxk：试探的最大邻居个数
        6、maxFN：试探的最大特征个数
        7、random_state: 开始试探时的随机数种子
        8、maxRS: 用于试探的最大的随机数种子
        9、excelfile：保存文件的名字
        10、sheetname：Excel文件的sheet名字
    输出：每次迭代取得更好的测试集分数时，输出模型参数和预测的股价
    返回：最优测试集的模型参数及预测的股价，以及各个迭代最优结果下预测的股价的
         加权中位数，权重为各个测试集分数。    
    """
    #检查日期的合理性
    if not isdate(atdate):
        print(".Error(forecast_stock_price_rs), invalid date:",atdate)
        return None
    
    #开始计时
    print("\n... Predicting stock price, it may take very long time, please wait ......")
    import time
    time0 = time.perf_counter()
    
    #设定起始日期：
    nyears=int((n_nextdays + n_samples + maxFN + 1)/252)+2
    start=date_adjust(atdate,-366*nyears)
    
    #抓取股价数据
    dfprice=get_stock_price(ticker,atdate,start)
    if dfprice is None:
        print(".Error(forecast_stock_price_rs), failed to capture stock prices:",ticker)
        return None        
    if len(dfprice) < (n_nextdays + n_samples + maxFN + 1):
        print(".Error(forecast_stock_price_rs), insufficient number of stock prices!")
        return None     

    #设置测试集分数起点
    bestscore_test=0.0
    #建立结果表结构
    import pandas as pd
    result=pd.DataFrame(columns=('ticker','atdate','n_nextdays','n_samples', \
                                 'random_state','pred_y','bestscore_train', \
                                 'bestscore_test','bestfeature','bestk'))
    #倒序随机数种子，便于尽快看到最优结果
    rslist=list(range(random_state,maxRS+1))
    rslist.reverse()
    #开始逐一试探各个随机数种子的最佳分数
    for rs in rslist: 
        print("... Testing random seed:",rs)
        pred_y0,bestscore_train0,bestscore_test0,bestfeature0,bestk0= \
            forecast_stock_price2(dfprice,n_nextdays=n_nextdays, \
                            n_samples=n_samples,maxk=maxk, \
                            maxFN=maxFN,random_state=rs)
            
        #记录中间结果
        row=pd.Series({'ticker':ticker,'atdate':atdate,'n_nextdays':n_nextdays, \
            'n_samples':n_samples,'random_state':rs,'pred_y':pred_y0, \
            'bestscore_train':bestscore_train0,'bestscore_test':bestscore_test0, \
            'bestfeature':bestfeature0,'bestk':bestk0})
        result=result.append(row,ignore_index=True)  
        
        #更新最佳纪录
        if bestscore_test < bestscore_test0:
            pred_y=pred_y0
            bestscore_train=bestscore_train0
            bestscore_test=bestscore_test0
            bestfeature=bestfeature0
            bestk=bestk0
            
            print("    Predicted stock price   :",pred_y)
            print("    Best score on train     :",bestscore_train)
            print("    Best score on test      :",bestscore_test)        
            print("    Best number of features :",bestfeature)
            print("    Best number of neighbors:",bestk,"\n")
    
    #再度显示中间结果
    pd.set_option('display.unicode.ambiguous_as_wide', True)
    pd.set_option('display.unicode.east_asian_width', True)
    pd.set_option('display.width', 180) # 设置打印宽度(**重要**)
    print("... Summary:") 
    print(result.to_string(index=False))
    print("\n... Result by highest score on test:",result['pred_y'][-1].values[0])
    
    #计算运行时间
    time1 = time.perf_counter()
    elapsed=time1 - time0
    print("... Total elapsed time is",second2time(elapsed))

    save_to_excel(result,excelfile,sheetname)
    print("... Results saved in an Excel file:",excelfile,"@sheet",sheetname)
    
    return result
 
if __name__ =="__main__":
    ticker='MSFT'
    atdate="2020-4-5"
    n_nextdays=1
    maxRS=1
    info=forecast_stock_price_rs(ticker,atdate,n_nextdays,maxRS=maxRS)
    print(info.to_string(index=False))

#==============================================================================
def multisummary(result,notes='',top=5):
    """
    功能：计算其加权中位数
    输入参数：
        1、result: 各个随机数种子下的最优预测值
        2、top: 采用测试分数最高的几个结果参加加权中位数计算
    输出：加权中位数
    返回：预测的股价的加权中位数，权重为各个测试集分数。    
    """
    
    #检查文件是否为空
    if len(result)==0:
        print("... Error(multisummary), No data recieved!")
        return None
    
    #排序: 升序
    result.sort_values(by=["bestscore_test","bestfeature"],ascending=[True,True],inplace=True)

    #对预测的股价取加权中位数
    if len(result) < top: top=len(result)
    topdata=result.tail(top)
    pred_y_wmedian=round(weighted_median(topdata,'pred_y','bestscore_test'),2)
    
    #显示详细结果
    import pandas as pd
    pd.set_option('display.unicode.ambiguous_as_wide', True)
    pd.set_option('display.unicode.east_asian_width', True)
    pd.set_option('display.width', 180) # 设置打印宽度(**重要**)
    
    print("\n... Summary:",notes) 
    print(result.to_string(index=False)) 
    hsotest=round(result.tail(1)['pred_y'].values[0],2)
    if notes == 'final':
        print("\n... Predicted price by highest score on test:",hsotest)
        print("... Predicted in median weighted by score on test:",pred_y_wmedian)

    return hsotest,pred_y_wmedian
 
if __name__ =="__main__":
    wmprice=multisummary(result,top=5)

#==============================================================================
def forecast_stock_price3(dfprice,n_nextdays=1,n_samples=252*3, \
                         maxk=20,maxFN=252*3,random_state=0):
    """
    功能：预测未来第几天的股票收盘价，试验单个随机数种子策略。可作为独立进程
    输入参数：
        1、dfprice: 抓取的股价数据集
        2、n_nextdays: 以atdate为基准向前推进几个交易日，预测该日期的股价
        3、n_samples: 生成机器学习用的样本中的最大观察数目。
           跨年的样本有助于模型学习季节性效应，3年的样本效果好于2年，
           2年的样本效果好于1年
        4、maxk：试探的最大邻居个数
        5、maxFN：试探的最大特征个数
        6、random_state: 随机数种子
    输出：单次迭代取得更好的测试集分数时，输出模型参数和预测的股价
    返回：最优测试集的模型参数及预测的股价。    
    """
    #显示进程号
    import multiprocessing as mp
    pname=mp.current_process().name
    print("... Starting sub-process",pname,"with random_state",random_state)
    
    #试探一个随机数种子的最佳分数
    pred_y0,bestscore_train0,bestscore_test0,bestfeature0,bestk0= \
            forecast_stock_price2(dfprice,n_nextdays=n_nextdays, \
                            n_samples=n_samples,maxk=maxk, \
                            maxFN=maxFN,random_state=random_state)
    #记录中间结果
    import pandas as pd                
    row=pd.Series({'random_state':random_state,'pred_y':pred_y0, \
        'bestscore_train':bestscore_train0,'bestscore_test':bestscore_test0, \
        'bestfeature':bestfeature0,'bestk':bestk0})
    
    print("... Endting sub-process",pname)
    return row
 
if __name__ =="__main__":
    ticker='MSFT'
    atdate="2020-4-5"
    n_nextdays=1
    random_state=0
    info=forecast_stock_price3(dfprice,n_nextdays,random_state=random_state)
    print(info)

#==============================================================================
def forecast_stock_price_mp(ticker,atdate,n_nextdays=1,n_samples=252*3, \
                         maxk=20,maxFN=252*3,random_state=0,maxRS=9,top=5):
    """
    功能：预测未来第几天的股票收盘价，试验随机数种子策略，多进程
    输入参数：
        1、ticker: 股票代码
        2、atdate: 当前日期，可以是今天或以前的一天
        3、n_nextdays: 以atdate为基准向前推进几个交易日，预测该日期的股价
        4、n_samples: 生成机器学习用的样本中的最大观察数目。
           跨年的样本有助于模型学习季节性效应，3年的样本效果好于2年，
           2年的样本效果好于1年
        5、maxk：试探的最大邻居个数
        6、maxFN：试探的最大特征个数
        7、random_state: 开始试探时的随机数种子
        8、maxRS: 用于试探的最大的随机数种子
        9、top: 最后中参与计算加权中位数的个数
    输出：每次迭代取得更好的测试集分数时，输出模型参数和预测的股价
    返回：最优测试集的模型参数及预测的股价，以及各个迭代最优结果下预测的股价的
         加权中位数，权重为各个测试集分数。    
    """
    #调试开关
    DEBUG=True
    
    #检查日期的合理性
    if not isdate(atdate):
        print(".Error(forecast_stock_price_rs), invalid date:",atdate)
        return None
    
    #开始信息
    print("\n... Predicting stock price by knn model ......")
    print("    Stock:",ticker)
    print("    Observation date:",atdate)
    print("    Number of trading day(s) being predicted:",n_nextdays)
    print("    Max number of historical prices used:",n_samples)
    print("    Max number of features used in knn:",maxFN)
    print("    Max number of neighbors used in knn:",maxk)
    print("    Max number of obs used in weighted meadian:",top)
    print("    WARNING: It may take long time, please wait ......")
    #开始计时
    import time; time0 = time.perf_counter()
    
    print("\n... Capturing historical stock prices ......",end='')
    #设定起始日期：
    nyears=int((n_nextdays + n_samples + maxFN + 1)/252)+1
    start=date_adjust(atdate,-366*nyears)
    #抓取股价数据
    dfprice=get_stock_price(ticker,atdate,start)
    if dfprice is None:
        print("\n    Error(forecast_stock_price_mp), failed to capture stock prices:",ticker)
        return None        
    if len(dfprice) < (n_nextdays + n_samples + maxFN + 1):
        print("\n    Error(forecast_stock_price_mp), insufficient number of stock prices!")
        return None     
    print(", done!")
    print("   ",len(dfprice),"historical stock prices captured")
    
    print("... Start machine-learning using knn model in multiprocessing ......")
    #倒序随机数种子，便于尽快看到最优结果
    rslist=list(range(random_state,maxRS+1)); rslist.reverse()
    jobnum=len(rslist)
    
    #电脑CPU核心数
    import os; cores=os.cpu_count()
    print("    There are",cores,"core(s) inside the cpu of this computer")
    #确定进程池大小
    if cores <= 4: procnum=cores+1
    else: procnum=cores
    #确定多进程分组组数
    groupnum=int(jobnum / procnum); remain=jobnum % procnum
    if remain > 0: groupnum+=1
    group=list(range(groupnum))

    #建立数据集：记录各个进程输出结果
    import pandas as pd
    result=pd.DataFrame(columns=('random_state','pred_y','bestscore_train', \
                                 'bestscore_test','bestfeature','bestk')) 
    #分组多任务
    import multiprocessing as mp
    for g in group:
        grpstart=g*procnum; grpend=(g+1)*procnum
        if grpend > jobnum: grpend=jobnum
    
        #创建进程池
        timep0 = time.perf_counter()
        pool=mp.Pool(processes=procnum)
        print("\n... Pool",g,"created with max capacity of",procnum,"processes in parallel")
        #建立多进程
        mptasks=[pool.apply_async(forecast_stock_price3,args=(dfprice,n_nextdays, \
                  n_samples,maxk,maxFN,i,)) for i in list(range(grpstart,grpend))]
        pool.close()
        pool.join()
        
        #记录组内各个最佳结果
        for res in mptasks:
            row=res.get()
            result=result.append(row,ignore_index=True)
        print("    Completed processes for random_state",list(range(grpstart,grpend)))
        h0,wmp0=multisummary(result[grpstart:grpend+1],notes="Pool "+str(g),top=top)
        #计算组内运行时间
        timep1 = time.perf_counter(); elapsedp=timep1 - timep0
        print("    Elapsed time in Pool",g,"is",second2time(elapsedp))        
    
    #排序最后结果
    result.sort_values(by=['bestscore_test'],ascending=True,inplace=True)

    #显示结果
    hsotest,wmprice=multisummary(result,'final',top)

    #计算总体运行时间
    time1 = time.perf_counter(); elapsed=time1 - time0
    print("\n... Total elapsed time is",second2time(elapsed))
    
    return hsotest,wmprice
 
if __name__ =="__main__":
    ticker='MSFT'
    atdate="2020-4-5"
    n_nextdays=1
    minRS=0
    maxRS=2
    predicted_prices=forecast_stock_price_mp(ticker,atdate,n_nextdays, \
                    random_state=minRS,maxRS=maxRS)

#==============================================================================
#==============================================================================
#==============================================================================

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
#==============================================================================
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

#==============================================================================

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
#==============================================================================

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
        print(".Error: sum of all shares in the portfolio is not 1")
        return None
    
    #抓取股票价格
    price=get_prices_portfolio(tickerlist,sharelist,atdate,fromdate)
    
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


#==============================================================================#==============================================================================
#==============================================================================#==============================================================================
#==============================================================================#==============================================================================

#==============================================================================
