# -*- coding: utf-8 -*-
"""
作者：王德宏
功能：测试ml_cases中的函数功能，仅限测试用
"""

from siat import *
dfprice=get_stock_price('MSFT','3/24/2022', '1/1/2015')
dfprice.head(5)
dfprice.tail(3)

dfprice[dfprice.Date == '2019-03-20']
dfprice[(dfprice.Date>='2019-03-11') & (dfprice.Date<='2019-03-15')]

X,y,ndprice=make_price_sample(dfprice,1,240,20)

from sklearn.model_selection import train_test_split
X_train,X_test,y_train,y_test= train_test_split(X,y,random_state=0)

from sklearn.neighbors import KNeighborsRegressor
reg=KNeighborsRegressor(n_neighbors=10,weights='distance')

reg.fit(X_train,y_train)
reg.score(X_train,y_train)
reg.score(X_test,y_test)

X_new=ndprice[0,0:20]
y_new=reg.predict(X_new)

print(y_new)

get_stock_price('MSFT', '3/25/2022', '3/24/2022')

bestmodel,bestk,bestscore_train,bestscore_test=bestKN(X,y)
print(bestk,bestscore_train,bestscore_test)

y_new=bestmodel.predict(X_new)
print(y_new)

bestmodel,bestk,bestscore_train,bestscore_test,bestrate=bestKN2(X,y)
print(bestk,bestscore_train,bestscore_test,bestrate)

y_new=bestmodel.predict(X_new)
print(y_new)


bestmodel,bestf,bestk,bestscore_train,bestscore_test=bestFN(dfprice,1,240)
print(bestf,bestk,bestscore_train,bestscore_test)
X_new=ndprice[0,0:bestf]
y_new=bestmodel.predict(X_new)
print(y_new)

bestmodel,bestf,bestk,bestscore_train,bestscore_test,bestrate=bestFN2(dfprice,1,240)
print(bestf,bestk,bestscore_train,bestscore_test)
X_new=ndprice[0,0:bestf]
y_new=bestmodel.predict(X_new)
print(y_new)

fprice,fprice2=forecast_stock_price2(dfprice,1,240)
forecast_stock_price('MSFT','2022-3-24',1)
