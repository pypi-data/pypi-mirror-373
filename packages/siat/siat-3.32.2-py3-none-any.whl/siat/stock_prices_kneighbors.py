# -*- coding: utf-8 -*-
"""
@function: 预测美股股价，教学演示用，其他用途责任自负，仅适用于机器学习课堂案例演示
@version：v1.4，2020.4.6
@purpose: 机器学习课程案例
@author: 王德宏，北京外国语大学国际商学院
特点：加入了多进程并行处理mp，在多核电脑上可以明显提速
"""

#==============================================================================
import warnings; warnings.filterwarnings('ignore')
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
        from pandas_datareader import data
    except:
        print(".Error(get_stock_price), pls install pandas_datareader first!")
        return None
    try:
        price=data.DataReader(ticker,'yahoo',fromdate,atdate)
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
    
    print("... Predicting stock price, it may take long time, please wait ......")
    
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
    