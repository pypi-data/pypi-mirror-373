# -*- coding: utf-8 -*-
"""
本模块功能：宏观经济基本面分析
所属工具包：证券投资分析工具SIAT 
SIAT：Security Investment Analysis Tool
创建日期：2025年3月9日
最新修订日期：2025年3月10日
作者：王德宏 (WANG Dehong, Peter)
作者单位：北京外国语大学国际商学院
版权所有：王德宏
用途限制：仅限研究与教学使用，不可商用！商用需要额外授权。
特别声明：作者不对使用本工具进行证券投资导致的任何损益负责！
"""
#==============================================================================
#关闭所有警告
import warnings; warnings.filterwarnings('ignore')
from siat.grafix import *
from siat.common import *
from siat.translate import *
#==============================================================================
import pandas as pd
from pandas_datareader import wb
import requests

#==============================================================================
if __name__=='__main__':
    key_words='NY.GDP.MKTP'
    key_words='per_allsp_gini_rur'
    
    search_id_only=True
    return_id_list=True
    top=20; country='CN'; max_sleep=30; start='L3Y'
    
def test_economic_indicator(key_words='NY.GDP.MKTP',top=20, \
                            country='CN',max_sleep=30,start='L3Y'):
    """
    ===========================================================================
    功能：测试某一类宏观经济指标的可用性
    参数：
    key_words：宏观经济指标类别，默认GDP系列指标'NY.GDP.MKTP'
    country：测试使用的经济体，默认中国'CN'
    max_sleep：测试指标指标之间的最大间隔秒数，默认30。若间隔时间过短可能被数据源屏蔽
    """
    print(f"*** Indicator magic={key_words}, top={top}, country={country}, start={start}:")
    id_list=indicator_wb(key_words,top=top,search_id_only=True,return_id_list=True)
    id_list_usable=id_list.copy()   #需要使用copy，不然两者始终同步
    
    #屏蔽函数内print信息输出的类
    import os, sys
    class HiddenPrints:
        def __enter__(self):
            self._original_stdout = sys.stdout
            sys.stdout = open(os.devnull, 'w')

        def __exit__(self, exc_type, exc_val, exc_tb):
            sys.stdout.close()
            sys.stdout = self._original_stdout    
    
    print(f'\nTesting the above indicators in {country}, please wait ... ...')   #空一行
    for id in id_list:
        #print(f"Testing {id} ... ...")
        print_progress_percent2(id,id_list,steps=10,leading_blanks=4)
        
        with HiddenPrints():        
            df=economy_trend2(country,indicator=id,start=start,graph=False)
            
        if df is None:
            #print(f"*** {id} deprecated or not provided for {country}")
            id_list_usable.remove(id)
        elif len(df)==0:
            #printf(f"### {id} has no data for {country}")
            id_list_usable.remove(id)
            
        sleep_random(max_sleep)

    print(f"\n*** Economic indicators available for {country}:")
    for id in id_list_usable:
        pos=id_list.index(id)+1
        print(f"{pos} {id}")
        
    return


#==============================================================================
if __name__=='__main__':
    key_words='GDP per capita'
    top=5; note=False
    
    indicator_wb(key_words='GDP',top=10,note=False)

def find_economic_indicator(key_words='GDP',top=20, \
                            note=False,translate=False,source='wb', \
                                search_id_only=False, \
                                return_id_list=False):
    """
    ===========================================================================
    功能：查找宏观经济指标代码
    参数：
    key_words：关键词，支持多关键词，使用空格隔开，默认'GDP'
    top：显示最相似的若干个指标，默认10
    note：是否显示指标的描述，默认否False
    translate：是否调用AI大模型进行翻译，若翻译可能影响反应速度，默认否False
    source：信息来源，默认'wb'
    search_id_only：是否仅仅查找指标代码，默认False；
       否则只查找指标代码，用于快速查找类似指标。
    return_id_list：是否返回指标代码列表，默认False；
       否则可用于快速检查返回的指标是否有数据、新数据或者已经deprecated
    
    注意：有时网络可能拒绝访问，可以换个时段再次进行访问
    """
    if source=='wb':
        df=indicator_wb(key_words=key_words,top=top,note=note,translate=translate, \
                        search_id_only=search_id_only,return_id_list=return_id_list)
    else:
        print("  Sorry, the source option currently only supports wb (World Bank)")
        
    return

#==============================================================================

if __name__=='__main__':
    key_words='GDP'
    key_words='NY.GDP.MKTP'
    
    top=20; note=False; translate=False
    search_id_only=True
    return_id_list=True
    
    
    
def indicator_wb(key_words='GDP',top=20,note=False,translate=False, \
                 search_id_only=False, \
                 return_id_list=False):
   """
   ============================================================================
   功能：在WB/IMF/FRED数据库中查找宏观经济指标的代码
   参数：
   key_words：可包括多个关键词，使用空格隔开，不区分大小写
   top：输出相似度最高的，默认20个
   note：是否显示每个指标的注释，默认False
   translate: 是否翻译，默认False
   search_id_only：是否仅仅查找指标代码，默认False；
       否则只查找指标代码，用于快速查找类似指标。
   return_id_list：是否返回指标代码列表，默认False；
       否则可用于快速检查返回的指标是否有数据、新数据或者已经deprecated
   
   输出：基于文本相似度，输出可能的指标代码及其简介
   
   返回值：可能的指标代码及其简介
   """
   import re

   # 拆分关键词字符串为列表
   #words_list=key_words.split(' ')
   if not search_id_only:
       words_list=re.split(r'[\s,.，]+', key_words)
   else:
       words_list=[key_words]
   
   # 循环查找每个关键词，并合成
   df=None
   for word in words_list:
       try:
           if not search_id_only:
               df_tmp=wb.search(word)
           else:
               df_tmp=wb.search('')
       except:
           #print("  Sorry, data source rejected connection, try again later")
           break
       
       # 合并
       if df is None:
           df=df_tmp
       else:
           df=pd.concat([df,df_tmp])
   
   # 未找到
   if df is None: 
       print("  Sorry, data source rejected connection, try again later")
       return
   if len(df) == 0:
       print(f"  Pity, nothing found for {key_words}")
       return
   
   # 去重
   df.drop_duplicates(subset=['id'],keep='first',inplace=True)
   
   # 去掉名称中的逗号、左右括号、美元符号和百分号，以免降低模糊匹配度
   #df['name2']=df['name'].apply(lambda x: re.sub('[(),$%]', '', x))
   if not search_id_only:
       df['name2']=df['name'].apply(lambda x: re.sub('[(),]', '', x))
       #df['name2']=df.apply(lambda x: re.sub('[(),]', '', x['name']) + ' ' + x['id'],axis=1)
   
       # 匹配相似度
       df2=fuzzy_search_wb(df,key_words=key_words,column='name2',top=top)
   else:
       df['id_tag']=df['id'].apply(lambda x: 1 if key_words.lower() in x.lower() else 0)
       df2=df[df['id_tag']==1].head(top)
       
       #note=True
   
   df2.reset_index(drop=True,inplace=True) 
   df2['seq']=df2.index + 1
   
   # 遍历输出
   if len(df2)==0:
       print(f"Sorry, no indicator found with key words: {key_words}")
       return None
       
   #print('') #空一行
   for row in df2.itertuples():
       
       print(f"{row.seq} {row.id}",end=': ')
       if not translate:
           print(f"{row.name}",end='')
       else:
           print(f"{row.name}[{lang_auto2(row.name)}]",end='')
       if row.unit != '':
           print(f", unit: {row.unit}")
       else:
           print('')
       if note:
           if row.sourceNote != '':
               print(f"{row.sourceNote}")
               if translate:
                   print(f"{lang_auto2(row.sourceNote)}")
               print('') #空一行
   
   if return_id_list:
       return list(df2['id'])
   else:
       return

#==============================================================================
if __name__=='__main__':
    key_words='GDP per capita'
    column='name'
    top=10

def fuzzy_search_wb(df,key_words='GDP per capita',column='name',top=10):
    """
    ===========================================================================
    功能：给定key_words，模糊搜索df的column字段，列出匹配度最高的10个指标及其解释
    参数：
    df：wb.search产生的指标集
    column：需要搜索的字段名，默认'id'
    key_words：需要匹配的关键词组，默认'GDP'
    top：列出模糊匹配度最高的若干个指标，默认10
    
    输出：无
    返回：指标列表
    """
    
    # 将关键词组和列中的每个值都转换为小写单词集合
    def normalize_text(text):
        return set(text.lower().split())
    
    # 应用函数并比较集合
    df["normalized_"+column] = df[column].apply(normalize_text)
    key_words_set = normalize_text(key_words)
    
    # 计算相似度（基于集合的交集和并集）
    def calculate_similarity(text_set, key_words_set):
        intersection = text_set.intersection(key_words_set)
        union = text_set.union(key_words_set)
        return len(intersection) / len(union)
    
    df["similarity"] = df["normalized_"+column].apply(lambda x: calculate_similarity(x, key_words_set))

    # 按相似度降序
    df.sort_values(['similarity'], ascending = False, inplace=True)
    
    df2=df[['id','name','unit','sourceNote']].head(top)

    return df2
        
#==============================================================================
if __name__ =="__main__":
    indicator="NY.GDP.MKTP.KN"
    indicator="6.0.GDP_current"
    indicator="XYZ123"
    
    indicator_name_wb(indicator)

def indicator_name_wb(indicator):
    """
    ===========================================================================
    功能：抓取World Bank网页上指标的名称
    indicator：WB指标名称，例如'NY.GDP.MKTP.KN'
    """
    # 优先查询本地词典
    indicator_name=economic_translate(indicator)
    
    # 查询WB网页
    if indicator_name == indicator:
        # 构造 API 请求 URL
        url = f"https://api.worldbank.org/v2/indicator/{indicator}?format=json"
        
        # 发送请求
        response = requests.get(url)
        data = response.json()
        
        # 提取指标名称
        try:
            indicator_name = data[1][0]['name']
        except:
            indicator_name = indicator
    
    return indicator_name


#==============================================================================
if __name__ =="__main__":
    ticker='CN'; show_name=True
    check_country_code('ZWE',show_name=True)
    check_country_code('ZAF',show_name=True)
    check_country_code('cn',show_name=True)
    
def check_country_code(ticker='CN',show_name=False):
    """
    ===========================================================================
    功能：检查国家代码是否支持
    ticker：国家代码
    show_name：是否显示国家名称，默认否False
    
    返回值：若国家代码在列表中，True；否则，False
    """
    country_codes=wb.country_codes
    
    elements_to_remove = ['all','ALL','All']
    country_code_list = [x for x in country_codes if x not in elements_to_remove]
    
    result=False
    if ticker in country_code_list:
        result=True
        
    if show_name:
        if result:
            indicator='NY.GDP.MKTP.KN'
            df=economy_indicator_wb(ticker=ticker,indicator=indicator, \
                                  start='2000',graph=False)
            if not (df is None):
                if len(df) >= 1:
                    country_name=df['country'].values[0]
                    print(f"Country code {ticker} refers to {country_name}")
                else:
                    print(f"Country code {ticker} found, but its name not found")
            else:
                print(f"Found country code {ticker}, but its name not found")
        else:
            print(f"Country code {ticker} not found")
    
    return result


#==============================================================================
if __name__ =="__main__":
    ticker='CN'
    indicator="NY.GDP.MKTP.KN"
    indicator="GC.XPN.TOTL.GD.ZS"
    indicator='NE.TRD.GNFS.ZS'
    
    indicator='GC.GDP.COMP.ZS' # 自制指标
    
    start='2015'; end='2025'; power=3
    
    zeroline=False
    attention_value=''; attention_value_area=''
    attention_point=''; attention_point_area=''
    average_value=False
    datatag=False; graph=True
    mark_top=True; mark_bottom=True; mark_end=True
    facecolor='whitesmoke';loc='best'
   
    
    df=economy_indicator_wb(ticker,indicator,start,end,power=3)

def economy_indicator_wb(ticker='CN',indicator='NY.GDP.MKTP.KN', \
                      start='L10Y',end='today',translate=False, \
                      zeroline=False, \
                           attention_value='',attention_value_area='', \
                           attention_point='',attention_point_area='', \
                      average_value=False, \
                      datatag=False,power=0,graph=True, \
                      mark_start=False,mark_top=False,mark_bottom=False,mark_end=True, \
                      facecolor='whitesmoke',loc='best',maxticks=30):
    """
    ===========================================================================
    功能：绘制一个国家的一个宏观经济指标走势
    参数：
    ticker：国家编码，两位,默认'CN'
    indicator：宏观经济指标，默认GDP (constant LCU)，即本币不变价格GDP
    start：开始日期，默认近十年
    end：结束日期，默认当前日期
    zeroline：是否绘制零线，默认False
    attention_value：纵轴关注值或其列表，默认无''
    attention_value_area：纵轴关注值区间强调，默认无''
    attention_point：横轴关注值或其列表，默认无''
    attention_point_area：横轴关注值区间强调，默认无''
    average_value：是否绘制均值线，默认否False
    datatag：是否标记折线中的各个数据点的数值，默认否False
    power：是否绘制趋势线，默认否0
    graph：是否绘图，默认是True
    mark_top, mark_bottom, mark_end：是否标记最高、最低和末端点：默认是True
    facecolor：背景颜色，默认'whitesmoke'
    loc：图例位置，默认自动'best'
    
    输出：图形
    返回值：数据表
    """
    import pandas as pd
    
    # 自制指标
    sm_ind_list=['GC.GDP.COMP.ZS']
    if indicator in sm_ind_list:
        sm_ind_flag=True
    else:
        sm_ind_flag=False
    
    # 检测指标是否存在，并取得指标名称
    indicator_name=indicator_name_wb(indicator)
    if indicator_name == indicator:
        print(f"  #Error(economy_indicator_wb): indicator {indicator} not found")
        return None
    
    # 日期具体化    
    start,end=start_end_preprocess(start,end)
    
    # 下载数据
    if not sm_ind_flag:
        try:
            pricedf=wb.download(indicator=indicator,country=ticker,start=start,end=end)
        except:
            print(f"  #Error(economy_indicator_wb): {indicator} not available for {ticker}")
            return None
    elif indicator == 'GC.GDP.COMP.ZS': # 针对自制指标
        indtmp1='NY.GDP.FCST.CN'    # Compensation of employees (current LCU)，CN无数据！
        indtmp2='NY.GDP.MKTP.CN'    # GDP (current LCU)
        try:
            pricetmp1=wb.download(indicator=indtmp1,country=ticker,start=start,end=end)
        except:
            print(f"  #Error(economy_indicator_wb): element {indtmp1} not available for {ticker}")
            return None
        try:
            pricetmp2=wb.download(indicator=indtmp2,country=ticker,start=start,end=end)
        except:
            print(f"  #Error(economy_indicator_wb): element {indtmp2} not available for {ticker}")
            return None
        
        # 算法=indtmp1 / indtmp2 * 100
        pricetmp=pd.merge(pricetmp1,pricetmp2,how='inner',left_on=['country','year'],
                          right_on=['country','year'])
        pricetmp[indicator]=pricetmp.apply(lambda x: round(x[indtmp1]/x[indtmp2]*100,2),axis=1)
        pricedf=pricetmp
    
    # 分离出country和year字段
    pricedf['country']=pricedf.index[0][0]
    pricedf['year']=pricedf.index
    pricedf['year']=pricedf['year'].apply(lambda x: x[1])
    
    pricedf=pricedf[['country','year',indicator]]
    pricedf.reset_index(drop=True,inplace=True)

    # 是否返回None
    if pricedf is None:
        print(f"  #Error(economy_indicator_wb): no data found on {indicator} in {ticker}")
        return None
    # 是否返回空的数据表
    if len(pricedf) == 0:
        print(f"  #Error(economy_indicator_wb): zero data found on {indicator} in {ticker}")
        return None
    # 是否返回数据表但内容均为NaN
    if pricedf[indicator].isnull().all():
        print(f"  #Error(economy_indicator_wb): all empty data found on {indicator} in {ticker}")
        return None
    # 判断非空值的个数
    if pricedf[indicator].count() == 1:
        print(f"  #Warning(economy_indicator_wb): only 1 non-empty data found on {indicator} in {ticker}")
        #return None
    
    pricedf.reset_index(drop=True,inplace=True)  
    pricedf.set_index('year',inplace=True)    
    pricedf.rename(columns={indicator:indicator_name},inplace=True)
    country=pricedf['country'].values[0]
    pricedf.sort_index(inplace=True)
    #pricedf.drop(columns='country',inplace=True)
    
    # 若不绘图则直接返回数据，不进行数量单位变换，否则后期对比可能产生数量级不一致问题
    if not graph:
        return pricedf
    
    erdf3=pricedf

    # 换算数量单位
    ind_max=erdf3[indicator_name].max()
    ind_min=erdf3[indicator_name].min()
    ind_median=erdf3[indicator_name].median()

    kilo=1000; million=kilo * 1000; billion=million * 1000
    trillion=billion * 1000; quadrillion=trillion * 1000
    
    if ind_median > quadrillion:
        unit=text_lang('单位：千万亿','in Quadrillions'); unit_amount=quadrillion
    elif ind_median > trillion:
        unit=text_lang('单位：万亿','in Trillions'); unit_amount=trillion
    elif ind_median > billion:
        unit=text_lang('单位：十亿','in Billions'); unit_amount=billion
    elif ind_median > million:
        unit=text_lang('单位：百万','in Millions'); unit_amount=million
    elif ind_median > kilo:
        unit=text_lang('单位：千','in Thousands'); unit_amount=kilo
    else:
        unit=''; unit_amount=1
        
    erdf3['unit']=unit; erdf3['unit_amount']=unit_amount
        
    if unit != '':
        erdf3[indicator_name]=erdf3[indicator_name].apply(lambda x: round(x/unit_amount,2))

    # 绘图
    # 判断是否绘制零线    
    if ind_max * ind_min <0:
        zeroline=True
    
    titletxt1=text_lang("经济分析","Economic Analysis")
    titletxt=titletxt1+': '+country_translate(country)+', '+indicator_name
    if unit != '':
        titletxt=titletxt+', '+unit
    
    import datetime; todaydt = datetime.date.today()
    sourcetxt=text_lang("数据来源：WB/IMF/FRED","Data source: World Bank")
    footnote=sourcetxt+', '+str(todaydt)
    collabel=indicator_name
    
    ylabeltxt=indicator_name
    
    # 为避免绘图出错，对空值进行插值
    erdf3.interpolate(method='linear',limit_direction='both',inplace=True)
    
    # 翻译：挪到绘图函数中
    """
    if translate:
        ylabeltxt=lang_auto2(ylabeltxt)
        titletxt=lang_auto2(titletxt)
    """
    try:
        plot_line(erdf3,indicator_name,collabel,ylabeltxt,titletxt,footnote,datatag=datatag, \
                  power=power,zeroline=zeroline, \
                  average_value=average_value, \
                      attention_value=attention_value,attention_value_area=attention_value_area, \
                      attention_point=attention_point,attention_point_area=attention_point_area, \
                  mark_top=mark_top,mark_bottom=mark_bottom, \
                  mark_start=mark_start,mark_end=mark_end, \
                  facecolor=facecolor,loc=loc,maxticks=30,translate=translate)
    except Exception as e:
        # 捕获所有异常
        print(f"  #Error(economy_indicator_wb)：{e}")
        print("  Details:")
        import traceback
        traceback.print_exc()
    
    return pricedf


#==============================================================
if __name__ =="__main__":
    ticker='CN'
    indicator=['NY.GDP.MKTP.CN','NY.GDP.MKTP.KN','NY.GDP.MKTP.CD','XYZ']
    start='2010'
    end='2025'
    
    attention_value=''; attention_value_area=''
    attention_point=''; attention_point_area=''
    band_area=''
    graph=True
    smooth=True
    loc='best'
    facecolor='whitesmoke'
    date_range=False
    date_freq=False
    annotate=False
    annotate_value=False
    mark_top=True; mark_bottom=True; mark_end=True
    maxticks=30
    
    df=economy_mindicators_wb(ticker,measures,fromdate,todate)

def economy_mindicators_wb(ticker='CN',indicator=['NY.GDP.MKTP.CN','NY.GDP.MKTP.KN'], \
                           start='L10Y',end='today', \
                               attention_value='',attention_value_area='', \
                               attention_point='',attention_point_area='', \
                               band_area='', \
                           graph=True,smooth=False,loc='best',facecolor='whitesmoke', \
                           date_range=False,date_freq=False, \
                           annotate=False,annotate_value=False, \
                           mark_start=False,mark_top=False,mark_bottom=False,mark_end=False, \
                           maxticks=30,translate=False):
    """
    ===========================================================================
    功能：单个国家，多个宏观经济指标对比
    主要参数：
    ticker：国家代码，默认'CN'
    indicator：指标代码列表，默认['NY.GDP.MKTP.CN','NY.GDP.MKTP.KN']
    start：开始日期，默认'L10Y'
    end：截止日期，默认'today'
    attention_value：纵轴关注值或其列表，默认无''
    attention_value_area：纵轴关注值区间强调，默认无''
    attention_point：横轴关注值或其列表，默认无''
    attention_point_area：横轴关注值区间强调，默认无''
    band_area：两条曲线之间强调，默认无''
    graph：是否绘图，默认True
    loc：图例位置，默认自动'best'
    facecolor：画布背景颜色，默认'whitesmoke'
    annotate：是否在曲线末端标注，默认否False
    annotate_value：是否标注曲线末端值，默认否False
    mark_start, mark_top, mark_bottom, mark_end：是否标注起始值、最大、最小、末端值，默认否
    maxticks=30：限制横轴刻度最大数量
    
    date_range=False：指定开始结束日期绘图
    date_freq=False：指定横轴日期间隔，例如'D'、'2D'、'W'、'M'等，横轴一般不超过25个标注，否则会重叠
    
    输出：图形
    返回值：数据表
    """
    DEBUG=False
    
    measures=indicator
    fromdate,todate=start_end_preprocess(start,end)
    
    #处理ticker，允许1个
    if isinstance(ticker,list):
        if len(ticker) >= 1:
            ticker=ticker[0]
        else:
            print("  #Error(economy_mindicators_wb): need at least 1 country to continue")
            return None

    #处理measures，允许多个
    if isinstance(measures,str):
        measures=[measures]

    #屏蔽函数内print信息输出的类
    import os, sys
    class HiddenPrints:
        def __enter__(self):
            self._original_stdout = sys.stdout
            sys.stdout = open(os.devnull, 'w')

        def __exit__(self, exc_type, exc_val, exc_tb):
            sys.stdout.close()
            sys.stdout = self._original_stdout

    df=pd.DataFrame(); have_data=False
    indicator_list=[]
    for m in measures:
        print(f"  Searching indicator {m} ... ...")

        with HiddenPrints():
            dftmp=economy_indicator_wb(ticker=ticker,indicator=m, \
                                  start=fromdate,end=todate, \
                                  graph=False)
        if dftmp is None:
            print(f"  #Warning(economy_mindicators_wb): none found for {m} with {ticker}")
            continue
            #return None
        if len(dftmp) ==0:
            print(f"  #Warning(economy_mindicators_wb): empty record found on {m} for {ticker}")
            continue   
            #return None
        
        have_data=True
        
        country=dftmp['country'].values[0]
        dftmp.drop(columns=['country'],inplace=True)
        indicator_name=list(dftmp)[0]
        
        if m in band_area:
            band_area = [indicator_name if x == m else x for x in band_area]
        
        indicator_list=indicator_list+[indicator_name]
        
        if len(df)==0:
            df=dftmp
        else:
            df=pd.merge(df,dftmp,left_index=True,right_index=True)

    # 若不绘图则直接返回数据
    pricedf=df.copy()
    if not graph: return pricedf

    if not have_data:
        #print(f"  #Error(economy_mindicators_wb): no record found on {indicator} for {ticker}")
        return None
        
    # 绘图
    titletxt=text_lang("经济趋势分析","Economic Trend Analysis")+': '+country_translate(country)    

    y_label=text_lang('经济指标',"Economic Indicator")
    import datetime; todaydt = datetime.date.today()
    footnote2=text_lang("数据来源：WB/IMF/FRED","Data source: World Bank")+', '+str(todaydt)

    # 处理数量级问题
    max_val=min_val=0
    for c in list(df):
        max_tmp=df[c].max(); min_tmp=df[c].min()
        if max_val < max_tmp: max_val = max_tmp
        if min_val > min_tmp: min_val = min_tmp
    ind_median=(max_val + min_val) / 2
    
    kilo=1000; million=kilo * 1000; billion=million * 1000
    trillion=billion * 1000; quadrillion=trillion * 1000
    
    if ind_median > quadrillion:
        unit=text_lang('单位：千万亿','in Quadrillions'); unit_amount=quadrillion
    elif ind_median > trillion:
        unit=text_lang('单位：万亿','in Trillions'); unit_amount=trillion
    elif ind_median > billion:
        unit=text_lang('单位：十亿','in Billions'); unit_amount=billion
    elif ind_median > million:
        unit=text_lang('单位：百万','in Millions'); unit_amount=million
    elif ind_median > kilo:
        unit=text_lang('单位：千','in Thousands'); unit_amount=kilo
    else:
        unit=''; unit_amount=1    
    
    for c in list(df):
        df[c]=df[c].apply(lambda x: round(x/unit_amount,2) if x >= unit_amount else round(x/unit_amount,4))
    
    x_label=footnote2
    if unit != '':
        titletxt=titletxt+', '+unit
            
    x_label=footnote2

    axhline_value=0; axhline_label=''
    above_zero=0; below_zero=0
    for c in list(df):
        c_max=df[c].max(); c_min=df[c].min()
        try:
            if c_max>0 or c_min>0: above_zero+=1
            if c_max<0 or c_min<0: below_zero+=1                
        except: continue
        
    if above_zero>0 and below_zero>0: #有正有负
        if DEBUG:
            print("DEBUG: draw axhline=0")
        axhline_value=0
        axhline_label=text_lang('零线',"Zeroline")
    
    # 为避免绘图出错，对空值进行插值
    df.interpolate(method='linear',limit_direction='both',inplace=True)

    # 翻译指标名称
    for c in list(df):
        df.rename(columns={c:economic_translate(c)},inplace=True)
    
    draw_lines2(df,y_label,x_label,axhline_value,axhline_label,titletxt, \
               data_label=False,resample_freq='1D',smooth=smooth, \
               date_range=date_range,date_freq=date_freq,date_fmt='%Y-%m-%d', \
                    attention_value=attention_value,attention_value_area=attention_value_area, \
                    attention_point=attention_point,attention_point_area=attention_point_area, \
               annotate=annotate,annotate_value=annotate_value, \
               mark_start=mark_start,mark_top=mark_top,mark_bottom=mark_bottom,mark_end=mark_end, \
                   facecolor=facecolor, \
               band_area=band_area,loc=loc,maxticks=maxticks,translate=translate)

    return pricedf


#==============================================================================
if __name__ =="__main__":
    tickers=['CN','US','JP']
    indicator='NY.GDP.MKTP.PP.CD'    
    start='L20Y'; end='today'
    
    attention_value=''; attention_value_area=''
    attention_point=''; attention_point_area=''
    axhline_value=0; axhline_label=''
    preprocess='none'; linewidth=1.5
    scaling_option='start'
    plus_sign=False
    graph=True; loc='best'; facecolor='whitesmoke'
    annotate=False; annotate_value=False
    smooth=True
    mark_top=True; mark_bottom=True; mark_end=False
    maxticks=30    
    
    
    
def economy_mtickers_wb(ticker=['CN','US','JP'],indicator='NY.GDP.MKTP.PP.CD', \
                       start='L15Y',end='today', \
                        attention_value='',attention_value_area='', \
                        attention_point='',attention_point_area='', \
                      axhline_value=0,axhline_label='', \
                      preprocess='none',linewidth=1.5, \
                      scaling_option='start', \
                      plus_sign=False, \
                      graph=True,facecolor='whitesmoke', \
                      band_area='',loc='best', \
                      annotate=False,annotate_value=False, \
                      smooth=False, \
                      mark_start=False,mark_top=True,mark_bottom=True,mark_end=False, \
                      maxticks=30,translate=False):
    """
    ===========================================================================
    功能：比较并绘制多个国家的单宏观经济指标曲线
    主要参数：
    ticker：国家代码，默认['CN','US','JP']
    indicator：宏观经济指标，默认'NY.GDP.MKTP.PP.CD'，即GDP PPP
    start：开始日期，默认'L20Y'
    end：截止日期，默认'today'
    attention_value：纵轴关注值或其列表，默认无''
    attention_value_area：纵轴关注区间强调，默认无''
    attention_point：横轴关注值或其列表，默认无''
    attention_point_area：横轴关注区间强调，默认无''
    preprocess：数据预处理，默认无'none'
    linewidth：曲线宽度，默认1.5
    scaling_option：数据缩放方法，默认'start'
    plus_sign：在缩放处理时，纵轴刻度是否带加减号，默认否False
    graph：是否绘图，默认是True
    loc：图例位置，默认自动处理'best'
    facecolor：画布背景颜色，默认'whitesmoke'
    annotate：是否标注曲线末端，默认否False
    annotate_value：是否标注曲线末端数值，默认否False
    mark_top：是否标注最大值，默认是True
    mark_bottom：是否标注最小值，默认是True
    mark_end：是否标注曲线末端值，默认否False
    maxticks：设定横轴刻度数量最大值，默认30
    
    注意：
    ticker中须含有2个及以上国家代码，
    indicator为单一指标，
    axhline_label不为空时绘制水平线
    
    preprocess：是否对绘图数据进行预处理，仅适用于指标数量级差异较大的数据，
    不适用于比例、比率和百分比等数量级较为一致的指标。
        standardize: 标准化处理，(x - mean(x))/std(x)
        normalize: 归一化处理，(x - min(x))/(max(x) - min(x))
        logarithm: 对数处理，np.log(x)
        scaling：缩放处理，五种选项scaling_option
        （mean均值，min最小值，start开始值，percentage相对每条曲线起点值的百分比，
        change%相对每条曲线起点值变化的百分比）
        change%方式的图形更接近于持有收益率(Exp Ret%)，设为默认的缩放方式。
    
    """
    DEBUG=False
    
    tickers=ticker; measure=indicator
    start,end=start_end_preprocess(start,end)
    
    tickers=upper_ticker(tickers)
    if not isinstance(tickers,list):
        tickers=[tickers]
    
    # 去掉重复代码：有必要，重复代码将导致后续处理出错KeyError: 0！
    tickers=list(set(tickers))

    if isinstance(measure,list):
        measure=measure[0]
    
    #屏蔽函数内print信息输出的类
    import os, sys
    class HiddenPrints:
        def __enter__(self):
            self._original_stdout = sys.stdout
            sys.stdout = open(os.devnull, 'w')

        def __exit__(self, exc_type, exc_val, exc_tb):
            sys.stdout.close()
            sys.stdout = self._original_stdout
    
    #循环获取指标
    #import pandas as pd
    #from functools import reduce

    dfs=pd.DataFrame(); have_data=False
    country_list=[]
    for t in tickers:
        print(f"  Looking for {measure} info in {t} ... ...")
        with HiddenPrints():
            df_tmp=economy_indicator_wb(ticker=t,indicator=measure, \
                                  start=start,end=end,graph=False)
        if df_tmp is None:
            print(f"  #Warning(economy_mticker_wb): {measure} info not found in {t}")
            continue
        if len(df_tmp)==0:
            print(f"  #Warning(economy_mticker_wb): zero info found for {measure} in {t}")
            continue

        have_data=True

        country=df_tmp['country'].values[0]
        country_list=country_list+[country]
        df_tmp.drop(columns=['country'],inplace=True)
        indicator_name=list(df_tmp)[0]
        
        if DEBUG:
            print(f"DEBUG: t={t}, band_area={band_area}, df_tmp={list(df_tmp)}")
            
        if t in band_area:
            band_area = [country if x == t else x for x in band_area]
         
        df_tmp.rename(columns={indicator_name:country},inplace=True)

        if len(dfs)==0:
            dfs=df_tmp
        else:
            dfs=pd.concat([dfs,df_tmp],axis=1,join='outer')
    
    # 翻译band_area
    band_area=[country_translate(x) for x in band_area]        
    
    if dfs is None:
        print(f"  #Error(economy_mticker_wb): no records found for {measure}")
        return None
    if len(dfs)==0:
        print(f"  #Error(economy_mticker_wb): zero records found for {measure}")
        return None

    # 若不绘图则返回原始数据
    pricedf=dfs.copy()
    if not graph: return pricedf

    if not have_data:
        #print(f"  #Error(economy_mticker_wb): no record found on {indicator} for {ticker}")
        return None

    # 绘图
    titletxt=text_lang("经济分析","Economic Analysis")+': '+indicator_name    
    #y_label=indicator_name
    y_label=text_lang("经济指标","Economic Indicator")
    
    import datetime; todaydt = datetime.date.today()
    footnote2=text_lang("数据来源：WB/IMF/FRED","Data source: WB/IMF/FRED")+', '+str(todaydt)

    # 处理数量级问题
    max_val=min_val=0
    for c in list(dfs):
        max_tmp=dfs[c].max(); min_tmp=dfs[c].min()
        if max_val < max_tmp: max_val = max_tmp
        if min_val > min_tmp: min_val = min_tmp
    ind_median=(max_val + min_val) / 2
    
    kilo=1000; million=kilo * 1000; billion=million * 1000
    trillion=billion * 1000; quadrillion=trillion * 1000
    
    if ind_median > quadrillion:
        unit=text_lang('单位：千万亿','in Quadrillions'); unit_amount=quadrillion
    elif ind_median > trillion:
        unit=text_lang('单位：万亿','in Trillions'); unit_amount=trillion
    elif ind_median > billion:
        unit=text_lang('单位：十亿','in Billions'); unit_amount=billion
    elif ind_median > million:
        unit=text_lang('单位：百万','in Millions'); unit_amount=million
    elif ind_median > kilo:
        unit=text_lang('单位：千','in Thousands'); unit_amount=kilo
    else:
        unit=''; unit_amount=1    
    
    for c in list(dfs):
        dfs[c]=dfs[c].apply(lambda x: round(x/unit_amount,2) if x >= unit_amount else round(x/unit_amount,4))

    x_label=footnote2
        
    if preprocess == 'scaling' and scaling_option == 'change%':
        title_txt2=text_lang("增减幅度%","Change%")
        titletxt=titletxt+', '+title_txt2            
        axhline_value=0
        axhline_label="零线"
    else:
        if unit != '' and preprocess == 'none':
            titletxt=titletxt+', '+unit

    # 为避免出错，对空值进行插值
    dfs.interpolate(method='linear',limit_direction='both',inplace=True)
    # 标准化处理
    try:
        dfs2,axhline_label,x_label,y_label,plus_sign=df_preprocess(dfs,measure, \
                axhline_label=axhline_label,x_label=x_label,y_label=y_label, \
                preprocess=preprocess,scaling_option=scaling_option)
    except:
        print("  #Error(economy_mticker_wb): preprocess failed, returning dfs for further check")
        return dfs

    if DEBUG:
        print("DEBUG: dfs2=",list(dfs2))
        
    above_zero=0; below_zero=0
    for c in list(dfs2):
        c_max=dfs2[c].max(); c_min=dfs2[c].min()
        try:
            if c_max>0 or c_min>0: above_zero+=1
            if c_max<0 or c_min<0: below_zero+=1
        except: continue

    if DEBUG:
        print("DEBUG: above_zero=",above_zero,'below_zero=',below_zero)
    
    if above_zero>0 and below_zero>0: #有正有负
        if axhline_label=='':
            axhline_label='零线'

    # 翻译国家名称
    for c in list(dfs2):
        dfs2.rename(columns={c:country_translate(c)},inplace=True)

    draw_lines(dfs2,y_label,x_label,axhline_value,axhline_label,titletxt, \
               data_label=False,resample_freq='D',smooth=smooth,linewidth=linewidth, \
               band_area=band_area,loc=loc, \
                    attention_value=attention_value,attention_value_area=attention_value_area, \
                    attention_point=attention_point,attention_point_area=attention_point_area, \
               annotate=annotate,annotate_value=annotate_value,plus_sign=plus_sign, \
               mark_start=mark_start,mark_top=mark_top,mark_bottom=mark_bottom,mark_end=mark_end, \
                   facecolor=facecolor, \
               maxticks_enable=False,maxticks=10, \
               translate=translate)

    return pricedf

#==============================================================================


def economy_trend2(ticker='CN',indicator='NY.GDP.MKTP.KN', \
                   start='L10Y',end='today',translate=False, \
                   attention_value='',attention_value_area='', \
                   attention_point='',attention_point_area='', \
                   mark_start=False,mark_top=False,mark_bottom=False,mark_end=False, \
                   graph=True,facecolor='whitesmoke',loc='best',maxticks=30, \
                   
                   zeroline=False,average_value=False, \
                   datatag=False,power=0, \
                   
                   annotate=False,annotate_value=False,smooth=False, \
                       
                   band_area='',date_range=False,date_freq=False, \
                       
                   axhline_value=0,axhline_label='', \
                   preprocess='none',linewidth=1.5, \
                   scaling_option='start', \
                   plus_sign=False, \
                   ):
    """
    功能：分析宏观经济指标，支持单国家单指标、多国家单指标、单国家多指标
    主要公共参数：
    ticker：国家编码，两位或三位ISO编码，默认'CN'
    indicator：宏观经济指标，默认GDP (constant LCU)，即本币不变价格GDP
    start：开始日期，默认近十年
    end：结束日期，默认当前日期
    attention_value：纵轴关注值或其列表，默认无''
    attention_value_area：纵轴关注值区间强调，默认无''
    attention_point：横轴关注值或其列表，默认无''
    attention_point_area：横轴关注值区间强调，默认无''        
    graph：是否绘图，默认是True
    mark_start, mark_top, mark_bottom, mark_end：是否标记开始点、最高、最低和末端点：默认否False
    facecolor：背景颜色，默认'whitesmoke'
    loc：图例位置，默认自动'best'

    仅支持单国家单指标的参数：
    zeroline：是否绘制零线，默认False        
    average_value：是否绘制均值线，默认否False
    datatag：是否标记折线中的各个数据点的数值，默认否False
    power：是否绘制趋势线，默认否0    
    
    支持多国家单指标、单国家多指标的参数：
    annotate：是否在曲线末端标注，默认否False
    annotate_value：是否标注曲线末端值，默认否False    
    
    仅支持单国家多指标的参数：
    band_area：两条曲线之间强调，默认无''
    date_range：指定开始结束日期绘图，默认False
    date_freq：指定横轴日期间隔，默认False。
        可指定'D'、'2D'、'W'、'M'等，横轴一般不超过25个标注，否则会重叠    
    
    仅支持多国家单指标的参数：
    preprocess：数据预处理，默认无'none'
    scaling_option：数据缩放方法，默认'start'，仅当preprocess为非'none'时有效
    plus_sign：在缩放处理时，纵轴刻度是否带加减号，默认否False    
    linewidth：曲线宽度，默认1.5

    输出：绘图
    返回值：数据表
    
    其他：套壳函数    
    """
    # 判断ticker个数
    ticker_num=0
    if isinstance(ticker,str): 
        ticker_num=1
        ticker=ticker.upper()
        if not check_country_code(ticker=ticker,show_name=False):
            print(f"  #Warning(economy_trend2): country code {ticker} not found")
            return None
        
    if isinstance(ticker,list):
        ticker=[x.upper() for x in ticker]
        for t in ticker:
            if not check_country_code(ticker=t,show_name=False):
                ticker.remove(t)
                print(f"  #Warning(economy_trend2): country code {t} not found")
        if len(ticker)==0:
            return None
        
        if len(ticker)==1: 
            ticker_num=1
            ticker=ticker[0]
        else:
            ticker_num=len(ticker)
    
    # 判断indicator个数
    indicator_num=0
    if isinstance(indicator,str): indicator_num=1
    if isinstance(indicator,list):
        if len(indicator)==1: 
            indicator_num=1
            indicator=indicator[0]
        else:
            indicator_num=len(indicator)
            
    # 单国家+单指标
    if ticker_num==1 and indicator_num==1:
        df=economy_indicator_wb(ticker=ticker,indicator=indicator, \
                                start=start,end=end,translate=translate, \
                                attention_value=attention_value, \
                                attention_value_area=attention_value_area, \
                                attention_point=attention_point, \
                                attention_point_area=attention_point_area, \
                                mark_top=mark_top,mark_bottom=mark_bottom, \
                                mark_start=mark_start,mark_end=mark_end, \
                                graph=graph,facecolor=facecolor,loc=loc,maxticks=maxticks, \
                                
                                power=power,average_value=average_value, \
                                zeroline=zeroline,datatag=datatag)
        return df
            
    # 多国家：仅使用第一个指标
    if ticker_num > 1:
        df=economy_mtickers_wb(ticker=ticker,indicator=indicator, \
                               start=start,end=end,translate=translate, \
                               attention_value=attention_value, \
                               attention_value_area=attention_value_area, \
                               attention_point=attention_point, \
                               attention_point_area=attention_point_area, \
                               mark_top=mark_top,mark_bottom=mark_bottom, \
                               mark_start=mark_start,mark_end=mark_end, \
                               graph=graph,loc=loc,facecolor=facecolor,maxticks=maxticks, \
                               band_area=band_area, \
                               annotate=annotate,annotate_value=annotate_value,smooth=smooth, \
                                   
                               preprocess=preprocess,scaling_option=scaling_option, \
                               plus_sign=plus_sign,linewidth=linewidth, \
                               axhline_value=axhline_value,axhline_label=axhline_label)
        return df
            
    # 单国家：使用多个指标
    if ticker_num == 1 and indicator_num > 1:
        df=economy_mindicators_wb(ticker=ticker,indicator=indicator, \
                                  start=start,end=end,translate=translate, \
                                  attention_value=attention_value, \
                                  attention_value_area=attention_value_area, \
                                  attention_point=attention_point, \
                                  attention_point_area=attention_point_area, \
                                  mark_top=mark_top,mark_bottom=mark_bottom, \
                                      mark_start=mark_start,mark_end=mark_end, \
                                  graph=graph,facecolor=facecolor,loc=loc,maxticks=maxticks, \
                                      
                                  annotate=annotate,annotate_value=annotate_value,smooth=smooth, \
                                      
                                  band_area=band_area, \
                                  date_range=date_range,date_freq=date_freq)
        return df

    print(" #Warning: need at least 1 country and at leats 1 indicator")
    
    return None    
    
    
#==============================================================================
#==============================================================================
#==============================================================================
#==============================================================================
#==============================================================================
#==============================================================================


def economic_translate(indicator):
    """
    ===========================================================================
    功能：翻译宏观经济指标术语
    参数：
    indicator: 指标编码，主要是世界银行编码。
    注意：部分编码已放弃，可能无数据或无最新数据。
    返回值：是否找到，基于语言环境为中文或英文解释。
    语言环境判断为check_language()
    
    数据结构：['指标编码','中文解释','英文解释']
    """
    DEBUG=False
    
    import pandas as pd
    trans_dict=pd.DataFrame([
        
        # NE.CON.PRVT:最终消费支出-家庭及NPISH===================================
        ['NE.CON.PRVT.CD','家庭及NPISH最终消费(美元现价)',
         'Household & NPISHs Final Consumption (current US$)',
         'Households and NPISHs Final consumption expenditure (current US$)'],
        
        ['NE.CON.PRVT.CN','家庭及NPISH最终消费(本币现价)',
         'Household & NPISHs Final Consumption (current LCU)',
         'Households and NPISHs Final consumption expenditure (current LCU)'],

        ['NE.CON.PRVT.CN.AD','家庭及NPISH最终消费(统计口径调整后，本币现价)',
         'Household & NPISHs Final Consumption (linked series, current LCU)',
         'Households and NPISHs Final consumption expenditure: linked series (current LCU)'],
        
        ['NE.CON.PRVT.KD','家庭及NPISH最终消费(2015美元不变价格)',
         'Household & NPISHs Final Consumption (constant 2015 US$)',
         'Households and NPISHs Final consumption expenditure (constant 2015 US$)'],

        ['NE.CON.PRVT.KD.ZG','家庭及NPISH最终消费(年增速%)',
         'Household & NPISHs Final Consumption (annual % growth)',
         'Households and NPISHs Final consumption expenditure (annual % growth)'],
        
        ['NE.CON.PRVT.KN','家庭及NPISH最终消费(本币不变价格)',
         'Household & NPISHs Final Consumption (constant LCU)',
         'Households and NPISHs Final consumption expenditure (constant LCU)'],

        ['NE.CON.PRVT.PC.KD','人均家庭及NPISH最终消费(2015美元不变价格)',
         'Household & NPISHs Final Consumption per capita (constant 2015 US$)',
         'Households and NPISHs Final consumption expenditure per capita (constant 2015 US$)'],

        ['NE.CON.PRVT.PC.KD.ZG','人均家庭及NPISH最终消费(年增速%)',
         'Household & NPISHs Final Consumption per capita growth (annual %)',
         'Households and NPISHs Final consumption expenditure per capita growth (annual %)'],

        ['NE.CON.PRVT.PP.CD','家庭及NPISH最终消费(购买力平价，国际美元现价)',
         'Household & NPISHs Final Consumption (PPP, current intl $)',
         'Households and NPISHs Final consumption expenditure, PPP (current international $)'],

        ['NE.CON.PRVT.PP.KD','家庭及NPISH最终消费(购买力平价，2021国际美元不变价格)',
         'Household & NPISHs Final Consumption (PPP, constant 2021 intl $)',
         'Households and NPISHs Final consumption expenditure, PPP (constant 2021 international $)'],

        ['NE.CON.PRVT.ZS','家庭及NPISH最终消费支出(占GDP%)',
         'Household & NPISHs Final Consumption (GDP%)',
         'Households and NPISHs Final consumption expenditure (% of GDP)'],
        
        # 币种指标：CD=current US$, KD=constant 2015 US$, CN=current LCU
        # KN=constant LCU, ZS=% of GDP, PC=per capita, PP=PPP
        
        # NE.CON.GOVT:最终消费支出-政府=========================================
        ['NE.CON.GOVT.CD','政府最终消费支出(美元现价)',
         'Government final consumption expenditure (current US$)',
         'General government final consumption expenditure (current US$)'],

        ['NE.CON.GOVT.CN','政府最终消费支出(本币现价)',
         'Government final consumption expenditure (current LCU)',
         'General government final consumption expenditure (current LCU)'],

        ['NE.CON.GOVT.ZS','政府最终消费支出(占GDP%)',
         'Government final consumption expenditure (% of GDP)',
         'General government final consumption expenditure (% of GDP)'],
        
        # NE.CON.TOTL:最终消费支出总计==========================================
        ['NE.CON.TOTL.CD','最终消费支出总计(美元现价)',
         'Final consumption expenditure (current US$)',
         'Final consumption expenditure (current US$)'],

        ['NE.CON.TOTL.CN','最终消费支出总计(本币现价)',
         'Final consumption expenditure (current LCU)',
         'Final consumption expenditure (current LCU)'],

        ['NE.CON.TOTL.KD','最终消费支出总计(2015美元不变价格)',
         'Final consumption expenditure (constant 2015 US$)',
         'Final consumption expenditure (constant 2015 US$)'],

        ['NE.CON.TOTL.KD.ZG','最终消费支出总计年增速%(2015美元不变价格)',
         'Final consumption expenditure (annual % growth)',
         'Final consumption expenditure (annual % growth)'],

        ['NE.CON.TOTL.KN','最终消费支出总计(本币不变价格)',
         'Final consumption expenditure (constant LCU)',
         'Final consumption expenditure (constant LCU)'],

        ['NE.CON.TOTL.ZS','最终消费支出总计(占GDP%)',
         'Final consumption expenditure (% of GDP)',
         'Final consumption expenditure (% of GDP)'],

        #######################################################################
        # NE.CON.TOTL.CD：最终消费支出，包括家庭、非营利机构为家庭服务的支出（NPISHs）以及政府消费支出。
        # 它反映了经济中所有部门的消费总支出。
        # 涵盖家庭、政府以及非营利机构为家庭服务的支出，是一个全面的消费指标。
        # 用于分析一个国家或地区的整体消费水平和消费结构，了解消费在经济中的地位和作用。
        # NE.CON.TETC.CD：最终消费支出（总额），通常与 NE.CON.TOTL.CD 类似。
        #
        # NE.CON.PRVT.CD：家庭和非营利机构为家庭服务的最终消费支出，主要反映私人部门的消费情况。
        # 仅包括家庭和非营利机构为家庭服务的消费支出，不包含政府消费支出。
        # 用于研究私人消费在经济增长中的贡献，分析家庭消费行为和消费趋势。
        # NE.CON.PETC.CD：私人最终消费支出，通常与 NE.CON.PRVT.CD 类似。
        #
        # NE.CON.GOVT.CD：政府最终消费支出，反映政府在提供公共服务和进行行政管理等方面的消费支出。
        # 仅包括政府的消费支出，不包含家庭和非营利机构的支出。
        # 用于分析政府消费支出在经济中的作用，了解政府在公共服务和行政管理方面的投入。
        #
        # NE.CON.TOTL.CD = NE.CON.PRVT.CD + NE.CON.GOVT.CD
        #======================================================================
        
        # NY.GDP.MKTP：国内生产总值GDP总量=======================================
        ['NY.GDP.MKTP.CD','GDP(美元现价)',
         'GDP (current US$)',
         'GDP (current US$)'],
        
        ['NY.GDP.MKTP.CN','GDP(本币现价)',
         'GDP (current LCU)',
         'GDP (current LCU)'],
         
        ['NY.GDP.MKTP.CN.AD','GDP(统计口径调整后，本币现价)',
         'GDP: linked series (current LCU)',
         'GDP: linked series (current LCU)'],       
         
        ['NY.GDP.MKTP.KD','GDP(2015美元不变价格)',
         'GDP (constant 2015 US$)',
         'GDP (constant 2015 US$)'],          
         
        ['NY.GDP.MKTP.KD.ZG','GDP年增速%(2015美元不变价格)',
         'GDP growth (annual %, constant 2015 US$)',
         'GDP growth (annual %, constant 2015 US$)'],          
         
        ['NY.GDP.MKTP.KN','GDP(本币不变价格)',
         'GDP (constant LCU)',
         'GDP (constant LCU)'],            
         
        ['NY.GDP.MKTP.PP.CD','GDP(购买力平价，国际美元现价)',
         'GDP, PPP (current international $)',
         'GDP, PPP (current international $)'],   
         
        ['NY.GDP.MKTP.PP.KD','GDP(购买力平价，2021国际美元不变价格)',
         'GDP, PPP (constant 2021 international $)',
         'GDP, PPP (constant 2021 international $)'],  
        
        # NY.GDP.PCAP：国内生产总值GDP人均=======================================
        ['NY.GDP.PCAP.CD','人均GDP(美元现价)',
         'GDP per capita (current US$)',
         'GDP per capita (current US$)'],

        ['NY.GDP.PCAP.CN','人均GDP(本币现价)',
         'GDP per capita (current LCU)',
         'GDP per capita (current LCU)'],        

        ['NY.GDP.PCAP.KD','人均GDP(2015美元不变价格)',
         'GDP per capita (constant 2015 US$)',
         'GDP per capita (constant 2015 US$)'],   

        ['NY.GDP.PCAP.KD.ZG','人均GDP年增速%(2015美元不变价格)',
         'GDP per capita growth (annual %, constant 2015 US$)',
         'GDP per capita growth (annual %, constant 2015 US$)'],  

        ['NY.GDP.PCAP.KN','人均GDP(本币不变价格)',
         'GDP per capita (constant LCU)',
         'GDP per capita (constant LCU)'],  

        ['NY.GDP.PCAP.PP.CD','人均GDP(购买力平价，国际美元现价)',
         'GDP per capita, PPP (current international $)',
         'GDP per capita, PPP (current international $)'],  

        ['NY.GDP.PCAP.PP.KD','人均GDP(购买力平价，2021国际美元不变价格)',
         'GDP per capita, PPP (constant 2021 international $)',
         'GDP per capita, PPP (constant 2021 international $)'],  
        
        # NY.GNP.MKTP：国民总收入GNI总量=======================================
        ['NY.GNP.MKTP.CD','GNI(美元现价)',
         'GNI (current US$)',
         'GNI (current US$)'],
        
        ['NY.GNP.MKTP.CN','GNI(本币现价)',
         'GNI (current LCU)',
         'GNI (current LCU)'],
         
        ['NY.GNP.MKTP.CN.AD','GNI(统计口径调整后，本币现价)',
         'GNI: linked series (current LCU)',
         'GNI: linked series (current LCU)'],       
         
        ['NY.GNP.MKTP.KD','GNI(2015美元不变价格)',
         'GNI (constant 2015 US$)',
         'GNI (constant 2015 US$)'],          
         
        ['NY.GNP.MKTP.KD.ZG','GNI年增速%(2015美元不变价格)',
         'GNI growth (annual %, constant 2015 US$)',
         'GNI growth (annual %, constant 2015 US$)'],          
         
        ['NY.GNP.MKTP.KN','GNI(本币不变价格)',
         'GNI (constant LCU)',
         'GNI (constant LCU)'],            
         
        ['NY.GNP.MKTP.PP.CD','GNI(购买力平价，国际美元现价)',
         'GNI(PPP, current international $)',
         'GNI(PPP, current international $)'],   
         
        ['NY.GNP.MKTP.PP.KD','GNI(购买力平价，2021国际美元不变价格)',
         'GNI(PPP, constant 2021 international $)',
         'GNI(PPP, constant 2021 international $)'],  
        
        # NY.GNP.PCAP：GNI人均=======================================
        ['NY.GNP.PCAP.CD','人均GNI(美元现价)',
         'GNI per capita (current US$)',
         'GNI per capita (current US$)'],

        ['NY.GNP.PCAP.CN','人均GNI(本币现价)',
         'GNI per capita (current LCU)',
         'GNI per capita (current LCU)'],        

        ['NY.GNP.PCAP.KD','人均GNI(2015美元不变价格)',
         'GNI per capita (constant 2015 US$)',
         'GNI per capita (constant 2015 US$)'],   

        ['NY.GNP.PCAP.KD.ZG','人均GNI年增速%(2015美元不变价格)',
         'GNI per capita growth (annual %, constant 2015 US$)',
         'GNI per capita growth (annual %, constant 2015 US$)'],  

        ['NY.GNP.PCAP.KN','人均GNI(本币不变价格)',
         'GNI per capita (constant LCU)',
         'GNI per capita (constant LCU)'],  

        ['NY.GNP.PCAP.PP.CD','人均GNI(购买力平价，国际美元现价)',
         'GNI per capita, PPP (current international $)',
         'GNI per capita, PPP (current international $)'],  

        ['NY.GNP.PCAP.PP.KD','人均GNI(购买力平价，2021国际美元不变价格)',
         'GNI per capita, PPP (constant 2021 international $)',
         'GNI per capita, PPP (constant 2021 international $)'],  
        
        #######################################################################
        #“International $”（国际美元）是一种标准化的货币单位，用于消除汇率差异，
        #使不同国家的经济指标（如 GDP）在购买力平价（PPP）基础上更具可比性。
        #它帮助我们更真实地了解各国居民的生活水平。
        #
        #在 GDP per capita, PPP（按购买力平价计算的人均 GDP）中，
        #使用“国际美元”可以更真实地反映一个国家居民的实际生活水平。
        #
        #例如，如果一个国家的 GDP per capita, PPP 是 20,000 国际美元，
        #这意味着该国居民的平均购买力相当于美国居民用 20,000 美元的购买力。
        #在这种情况下，1 国际美元的购买力等于在美国用 1 美元的购买力。
        #
        #再比如，如果一个同样的汉堡在美国售价为 5 美元，在印度售价为 200 卢比，
        #那么根据 PPP 理论，1 美元应该等于 40 卢比（200 卢比 / 5 美元）。
        #
        #为了计算国际美元，需要对各国商品和服务的价格进行比较，并根据其在经济中的重要性分配权重。
        #例如，食品、住房、交通等商品和服务的权重可能更高。
        #######################################################################
        
        # GFDD.DM：证券市场-股票、权益与债券=====================================
        ['CM.MKT.LCAP.GD.ZS','国内上市公司市值占GDP%',
         'Market cap of domestic listed companies to GDP (%)',
         'Market cap of domestic listed companies to GDP (%)'],        
        
        ['GFDD.DM.01','股票市场总市值占GDP%',
         'Stock market capitalization to GDP (%)',
         'Stock market capitalization to GDP (%)'],

        ['GFDD.DM.02','股票市场当年交易额占GDP%',
         'Stock market total value traded to GDP (%)',
         'Stock market total value traded to GDP (%)'],
        # 经济意义：
        # 市场流动性：该指标越高，表明股票市场的流动性越强，交易越活跃。高流动性通常意味着市场参与者更容易买卖股票，市场效率较高。
        # 经济开放程度：较高的交易总值占GDP比重通常反映出一个国家或地区的经济开放程度较高，资本市场较为发达。
        # 金融体系发达程度：该指标还可以反映一个国家或地区的金融体系是否发达，以及股票市场在金融体系中的地位。
        # 市场波动性：在某些情况下，过高的交易总值占GDP比重可能反映出市场波动性较大，投资者情绪较为活跃。
        #
        # 实际应用：
        # 比较不同国家的股票市场活跃程度：通过比较不同国家的指标，可以了解各国股票市场的相对活跃程度。
        
        ['GFDD.DM.03','未清偿的国内非政府债务证券占GDP%',
         'Outstanding domestic private debt securities to GDP (%)',
         'Outstanding domestic private debt securities to GDP (%)'],
        # 债务证券是政府、公司和金融机构发行的债券和票据等债务工具
        # 未清偿的国内私人债务证券占GDP的百分比。
        # 该指标反映了国内私人部门（包括公司和金融机构）发行的债务证券在经济中的比重。
        # 经济意义：
        # 金融市场发达程度：该指标越高，表明一个国家或地区的金融市场越发达，私人部门通过债务证券融资的能力越强。
        # 经济风险：较高的私人债务证券占GDP比重可能反映出较高的经济风险，特别是在债务水平超过经济承受能力的情况下。
        # 债务可持续性：该指标可以帮助评估私人部门债务的可持续性，了解债务水平是否与经济增长相匹配。
        
        ['GFDD.DM.04','未清偿的国内政府债务证券占GDP%',
         'Outstanding domestic public debt securities to GDP (%)',
         'Outstanding domestic public debt securities to GDP (%)'],
        # 经济意义
        # 公共债务水平：该指标反映了政府的债务负担，特别是通过国内市场融资的债务水平。
        # 债务可持续性：较高的公共债务证券占GDP比重可能反映出较高的债务风险，尤其是在债务水平超过经济承受能力的情况下。
        # 财政政策的稳健性：该指标可以用来评估一个国家的财政政策是否稳健，以及政府是否有能力偿还其债务。
        # 经济风险：公共债务水平的高低可以反映一个国家的经济风险，尤其是在国际金融市场波动或经济衰退时。
        
        ['GFDD.DM.05','未清偿的国际非政府债务证券占GDP%',
         'Outstanding international private debt securities to GDP (%)',
         'Outstanding international private debt securities to GDP (%)'],
        # 经济意义：
        # 国际融资能力：该指标反映了私人部门在国际市场上融资的能力，较高的比重通常表明一个国家的私人部门能够更有效地利用国际资本。
        # 经济开放程度：较高的国际私人债务证券占GDP比重通常表明一个国家的经济开放程度较高，与国际资本市场的联系较为紧密。
        # 经济风险：较高的国际私人债务证券占GDP比重可能反映出较高的经济风险，尤其是在国际金融市场波动或经济衰退时。
        # 债务可持续性：该指标可以帮助评估私人部门国际债务的可持续性，了解债务水平是否与经济增长相匹配。
        # 资本流动：该指标可以反映国际资本流动的趋势，帮助分析资本流入和流出的动态。
        #
        # 实际应用：
        # 比较不同国家的国际融资能力：通过比较不同国家的“Outstanding international private debt securities to GDP (%)”，可以了解各国私人部门在国际市场上融资的相对能力。
        
        ['GFDD.DM.06','未清偿的国际政府债务证券占GDP%',
         'Outstanding international public debt securities to GDP (%)',
         'Outstanding international public debt securities to GDP (%)'],
        
        ['GFDD.DM.07','国际债务发行总额占GDP%',
         'International debt issues to GDP (%)',
         'International debt issues to GDP (%)'],
        
        ['GFDD.DM.08','发行权益工具吸引外资形成的经济责任总额占GDP%',
         'Gross portfolio equity liabilities to GDP (%)',
         'Gross portfolio equity liabilities to GDP (%)'],
        
        ['GFDD.DM.09','通过权益工具持有的国际资产总额占GDP%',
         'Gross portfolio equity assets to GDP (%)',
         'Gross portfolio equity assets to GDP (%)'],
        
        ['GFDD.DM.10','发行债务工具吸引外资形成的经济责任总额占GDP%',
         'Gross portfolio debt liabilities to GDP (%)',
         'Gross portfolio debt liabilities to GDP (%)'],
        
        ['GFDD.DM.11','通过债务工具持有的国际资产总额占GDP%',
         'Gross portfolio debt assets to GDP (%)',
         'Gross portfolio debt assets to GDP (%)'],
        # 注意：总额Gross与净额Net的区别
        ['GFDD.DM.12','银团贷款发行量占GDP%',
         'Syndicated loan issuance volume to GDP (%)',
         'Syndicated loan issuance volume to GDP (%)'],
        
        ['GFDD.DM.13','公司债券发行量占GDP%',
         'Corporate bond issuance volume to GDP (%)',
         'Corporate bond issuance volume to GDP (%)'],
        
        ['GFDD.DM.14','银团贷款的平均到期年限',
         'Syndicated loan average maturity (years)',
         'Syndicated loan average maturity (years)'],
        
        ['GFDD.DM.15','公司债券的平均到期年限',
         'Corporate bond average maturity (years)',
         'Corporate bond average maturity (years)'],
        
        ['GFDD.DM.16','金融科技和大型科技公司提供的信贷流量占GDP%',
         'Credit flows by fintech and bigtech companies to GDP (%)',
         'Credit flows by fintech and bigtech companies to GDP (%)'],
        # 经济意义:
        # 金融创新：该指标反映了金融科技和大型科技公司在信贷市场中的活跃程度，较高的比重通常表明金融创新较为活跃。
        # 金融包容性：较高的信贷流量占GDP比重可能表明金融科技和大型科技公司正在帮助提高金融包容性，为更多人提供信贷服务。
        # 经济活力：该指标可以反映一个国家或地区的经济活力，特别是在金融技术和科技创新方面的活力。
        # 监管挑战：较高的信贷流量可能带来监管挑战，因为金融科技和大型科技公司可能不受传统银行监管的约束。
        # 市场竞争力：该指标可以帮助评估金融科技和大型科技公司与传统银行之间的竞争力。
        #
        # 实际应用:
        # 比较不同国家的金融创新程度：通过比较不同国家的“Credit flows by fintech and bigtech companies to GDP (%)”，可以了解各国在金融创新方面的相对程度。
        # 评估金融包容性：该指标可以用来评估一个国家的金融包容性，特别是金融科技和大型科技公司在提供信贷服务方面的作用。
        
        # FM.LBL.BMNY：广义货币M2===============================================
        ['FM.LBL.BMNY.CN','广义货币(本币现价)',
         'Broad money (current LCU)',
         'Broad money (current LCU)'],
        
        ['FM.LBL.BMNY.ZG','广义货币年增速%',
         'Broad money growth (annual %)',
         'Broad money growth (annual %)'],
        
        ['FM.LBL.MQMY.XD','货币流通速度(GDP/M2)',
         'Income velocity of money (GDP/M2)',
         'Income velocity of money (GDP/M2)'], 
        
        ['FM.LBL.BMNY.GD.ZS','广义货币(占GDP%)',
         'Broad money (% of GDP)',
         'Broad money (% of GDP)'],

        ['FM.LBL.BMNY.IR.ZS','广义货币供应量与总储备的比率',
         'Broad money to total reserves ratio',
         'Broad money to total reserves ratio'],
        # total reserves：总储备，FI.RES.TOTL.CD，指外汇储备和其他国际储备资产。
        # 即央行持有的外汇储备、黄金储备、国际货币基金组织（IMF）特别提款权（SDR）等可动用的国际储备资产总和。
        # 用于衡量一个国家 货币供应量 相对于其 外汇储备和其他国际储备资产 的充足程度的指标，反映该国应对资本外流或货币危机的能力。
        #
        # 经济意义与用途：
        # 衡量货币体系的脆弱性：
        # 比率越高，说明广义货币规模远超储备资产，可能面临资本外流时央行干预能力不足的风险（例如外汇储备无法覆盖货币兑换需求）。
        # 典型案例：1997年亚洲金融危机中，泰国、韩国等国因该比率过高（外汇储备不足），导致本币大幅贬值。
        # 评估货币政策与汇率稳定性：
        # 高比率可能表明：
        # 央行依赖资本管制或外债来维持汇率稳定；
        # 若遭遇市场恐慌（如外资撤离），本币贬值压力加大。
        # 国际比较与预警指标：
        # 新兴市场通常关注该比率，因其资本流动波动性大。
        # 经验阈值：若比率超过 5倍（500%），可能被视为风险较高（需结合外债、经常账户等指标综合判断）。
        #
        # 与“M2/GDP”对比：“M2/GDP”反映经济货币化程度，而“M2/总储备”侧重外部风险。
        
        # 国际贸易==============================================================
        ['TM.TAX.MRCH.SM.AR.ZS','所有商品的实际平均关税%',
         'Tariff rate, applied, simple mean, all products (%)',
         'Tariff rate, applied, simple mean, all products (%)'],

        ['TM.TAX.MRCH.SM.FN.ZS','所有商品的最惠国平均关税%',
         'Tariff rate, most favored nation, simple mean, all products (%)',
         'Tariff rate, most favored nation, simple mean, all products (%)'],
        # 注意：最惠国关税是从最惠国进口商品名义上的最高关税水平，不是实际水平。
        # 这里是简单平均！
        # 因此，实际关税水平很可能低于最惠国名义关税水平。原因在于：
        # 最惠国待遇（MFN）与特殊关税安排：
        # 最惠国待遇（MFN）：最惠国待遇是世界贸易组织（WTO）框架下的基本原则之一，要求成员方给予任何一个成员方的优惠，必须自动给予所有其他成员方。因此，'TM.TAX.MRCH.SM.FN.ZS' 反映的是中国对最惠国待遇下的商品征收的关税水平。
        # 特殊关税安排：中国与其他国家或地区之间可能存在自由贸易协定（FTA）、关税优惠协定或其他特殊贸易安排，这些安排允许某些商品享受比最惠国税率更低的关税甚至零关税。这些特殊安排下的商品关税水平被反映在实际关税水平指标'TM.TAX.MRCH.SM.AR.ZS'中。
        # 关税配额制度：
        # 关税配额：中国可能对某些商品实施关税配额制度，即在一定配额内享受较低的关税税率，超过配额部分则按较高税率征收。这种制度使得实际关税水平低于最惠国税率。
        # 非关税壁垒的影响：
        # 非关税壁垒：虽然非关税壁垒（如进口配额、技术标准、卫生检疫要求等）不直接降低关税水平，但它们可能间接影响实际关税水平。例如，某些商品可能因为非关税壁垒而进口量较少，从而使得实际关税收入占比较低。
        
        ['TM.TAX.MRCH.WM.AR.ZS','所有商品的实际加权平均关税%',
         'Tariff rate, applied, weighted mean, all products (%)',
         'Tariff rate, applied, weighted mean, all products (%)'],

        ['TM.TAX.MRCH.WM.FN.ZS','所有商品的最惠国加权平均关税%',
         'Tariff rate, most favored nation, weighted mean, all products (%)',
         'Tariff rate, most favored nation, weighted mean, all products (%)'],

        ['NE.EXP.GNFS.ZS','出口商品和服务占GDP%',
         'Exports of goods and services (% of GDP)',
         'Exports of goods and services (% of GDP)'],

        ['NE.IMP.GNFS.CD','进口商品和服务总金额(美元现价)',
         'Imports of goods and services (current US$)',
         'Imports of goods and services (current US$)'],

        ['NE.EXP.GNFS.CD','出口商品和服务总金额(美元现价)',
         'Exports of goods and services (current US$)',
         'Exports of goods and services (current US$)'],

        ['NE.IMP.GNFS.ZS','进口商品和服务占GDP%',
         'Imports of goods and services (% of GDP)',
         'Imports of goods and services (% of GDP)'],

        ['NE.TRD.GNFS.ZS','国际贸易占GDP%',
         'Trade % of GDP',
         'Trade % of GDP'],
        # 用来分析一个国家对国际贸易的依赖程度。
        # 高贸易占比通常表明一个国家的经济结构以出口和进口为主，而低贸易占比可能表明经济更依赖国内消费或投资。
        
        # 贫困和贫富分化========================================================
        ['SI.POV.GINI','基尼指数',
         'Gini index',
         'Gini index'],
        # 基尼指数：0-100，用于衡量收入或财富分配的不平等程度。
        # 0表示完全平等，100表示完全不平等。基尼系数高通常意味着贫富差距较大。
        # 注意不是基尼系数（0-1）。
        
        # 薪酬=================================================================
        ['GC.GDP.COMP.ZS','劳动者薪酬占GDP%',
         'Compensation of employees (% of GDP)',
         'Compensation of employees (% of GDP)'],
        # 自制指标：= GC.XPN.COMP.ZS: Compensation of employees (% of expense)
        # x GC.XPN.TOTL.GD.ZS: Expense (% of GDP) / 100。
        # 或 = GC.XPN.COMP.CN: Compensation of employees (current LCU)
        # / NY.GDP.MKTP.CN: GDP (current LCU) * 100.
        
        # 储蓄=================================================================
        ['NY.GNS.ICTR.ZS','国民储蓄总额占GDP%',
         'Gross savings (% of GDP)',
         'Gross savings (% of GDP)'],
        # 国民储蓄：一国居民和政府的总储蓄，包含国内储蓄和来自国外的净收入
        # 包含国际要素：计入来自国外的净要素收入（如投资收益、侨汇）。

        ['NY.GDS.TOTL.ZS','国内储蓄总额占GDP%',
         'Gross Domestic Savings (% of GDP)',
         'Gross Domestic Savings (% of GDP)'],
        # 国内储蓄：仅统计国内经济主体（家庭、企业、政府）的储蓄，不包含国外净收入。
        # 仅限国内：不涉及国际收入或支出。
        
        # 投资=================================================================
        ['NE.GDI.TOTL.ZS','总资本形成占GDP%',
         'Gross capital formation (% of GDP)',
         'Gross capital formation (% of GDP)'],
        # 又名Gross domestic investment国内总投资，包括政府、企业和家庭的投资
        
        ['NE.GDI.FTOT.ZS','总固定资本形成占GDP%',
         'Gross fixed capital formation (% of GDP)',
         'Gross fixed capital formation (% of GDP)'],
        # 又名Gross domestic fixed investment国内固定资产总投资，包括政府、企业和家庭的投资
        
        ['BX.KLT.DINV.WD.GD.ZS','外国直接投资净额占GDP%',
         'Foreign direct investment, net inflows (% of GDP)',
         'Foreign direct investment, net inflows (% of GDP)'],
        # 等于FDI流入 - FDI流出
        
        # 政府财政==============================================================
        ['GC.REV.XGRT.GD.ZS','政府总收入(不含国际赠款)占GDP%',
         'Revenue, excluding grant (% of GDP)',
         'Revenue, excluding grant (% of GDP)'],
        # 包括税收和非税收入
        
        ['SH.XPD.GHED.GD.ZS','政府卫生支出占GDP%',
         'Government health expenditure (% of GDP)',
         'Domestic general government health expenditure (% of GDP)'],
        # 包括税收和非税收入
        
        ['SH.XPD.GHED.CH.ZS','政府卫生支出占当前卫生支出%',
         'Government health expenditure (% of health expenditure)',
         'Domestic general government health expenditure (% of current health expenditure)'],
        # 包括税收和非税收入
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        ], columns=['indicator','cword','eword','original_eword'])

    found=False; result=indicator
    try:
        dict_word=trans_dict[trans_dict['indicator']==indicator.upper()]
        found=True
    except:
        #未查到翻译词汇，返回原词
        pass
    
    if dict_word is None:
        found=False    
    elif len(dict_word) == 0:
        found=False
    
    if found:
        lang=check_language()
        
        if DEBUG:
            print(f"DEBUG: indicator={indicator}, lang={lang}, dict_word={dict_word}")
        
        if lang == 'Chinese':
            result=dict_word['cword'].values[0]
        else:
            result=dict_word['eword'].values[0]
            
    return result

if __name__=='__main__': 
    indicator='NE.CON.PRVT.CD'
    indicator='NE.CON.PRVT.KD'

    indicator='NE.CON.PRVT.CN'
    indicator='NE.CON.PRVT.KN'
    
    result=economic_translate(indicator)
    economic_translate(indicator)[1]

#==============================================================================


def country_translate(country):
    """
    ===========================================================================
    功能：翻译国家名称
    参数：
    country: 国家名称英文，并非国家代码。
    返回值：是否找到，基于语言环境为中文或英文解释。
    语言环境判断为check_language()
    
    数据结构：['国家名称英文','国家名称中文','国家代码2位','国家代码3位']
    """
    
    import pandas as pd
    trans_dict=pd.DataFrame([
        
        ['China','中国','CN','CHN'],
        ['United States','美国','US','USA'],
        ['Japan','日本','JP','JPN'],
        ['Germany','德国','DE','DEU'],
        ['India','印度','IN','IND'],
        ['Brazil','巴西','BR','BRA'],
        
        ['France','法国','FR','FRA'],
        ['United Kingdom','英国','GB','GBR'],
        ['Russian Federation','俄罗斯','RU','RUS'],
        ['Canada','加拿大','CA','CAN'],
        ['Australia','澳大利亚','AU','AUS'],
        ['Korea, Rep.','韩国','KR','KOR'],
        
        ['Italy','意大利','IT','ITA'],
        ['Mexico','墨西哥','MX','MEX'],
        ['South Africa','南非','ZA','ZAF'],
        ['Saudi Arabia','沙特阿拉伯','SA','SAU'],
        ['Indonesia','印度尼西亚','ID','IDN'],
        ['Turkiye','土耳其','TR','TUR'],
        
        ['Argentina','阿根廷','AR','ARG'],
        ['Egypt','埃及','EG','EGY'],
        ['European Union','欧盟','EU','EUU'],
        ['Hong Kong SAR, China','中国香港','HK','HKG'],
        ['Taiwan, China','中国台湾','TW','TWN'],
        ['World','全球','1W','WLD'],
        
        ['Singapore','新加坡','SG','SGP'],
        ['Malaysia','马来西亚','MY','MYS'],
        ['Thailand','泰国','TH','THA'],
        ['Israel','以色列','IL','ISR'],
        ['Vietnam','越南','VN','VNM'],
        ['Philippines','菲律宾','PH','PHL'],
        ['Brunei','文莱','BN','BRN'],
        ['Cambodia','柬埔寨','KH','KHM'],
        
        ['Laos','老挝','LA','LAO'],
        ['Myanmar','缅甸','MM','MMR'],
        
        
        
        
        
        ], columns=['ecountry','ccountry','country code2','country code3'])

    found=False; result=country
    try:
        dict_word=trans_dict[trans_dict['ecountry']==country]
        found=True
    except:
        #未查到翻译词汇，返回原词
        pass
    
    if dict_word is None:
        found=False    
    elif len(dict_word) == 0:
        found=False
    
    if found:
        lang=check_language()
        if lang == 'Chinese':
            result=dict_word['ccountry'].values[0]
        else:
            #result=dict_word['ecountry'].values[0]
            pass
            
    return result

if __name__=='__main__': 
    country='China'
    country='United States'
    
    result=country_translate(country)

#==============================================================================
    