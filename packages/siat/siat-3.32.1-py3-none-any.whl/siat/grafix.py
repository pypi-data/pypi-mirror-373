# -*- coding: utf-8 -*-
"""
本模块功能：绘制折线图，单线，双线，多线
所属工具包：证券投资分析工具SIAT 
SIAT：Security Investment Analysis Tool
创建日期：2020年9月16日
最新修订日期：2020年9月16日
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
from siat.common import *
from siat.translate import *

#==============================================================================
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdate
#import matplotlib.font_manager as fm
#==============================================================================

#设置刻度线风格：in，out，inout
plt.rcParams['xtick.direction'] = 'inout'  # 将x轴的刻度线方向设置向内
plt.rcParams['ytick.direction'] = 'inout'  # 将y轴的刻度方向设置向内内

#统一设定绘制的图片大小：数值为英寸，1英寸=100像素
#plt.rcParams['figure.figsize']=(12.8,7.2)
plt.rcParams['figure.figsize']=(12.8,6.4)
plt.rcParams['figure.dpi']=300
plt.rcParams['font.size'] = 13
plt.rcParams['xtick.labelsize']=11 #横轴字体大小
plt.rcParams['ytick.labelsize']=11 #纵轴字体大小

plt.rcParams['figure.facecolor']='whitesmoke' #背景颜色
#plt.rcParams['axes.facecolor']='whitesmoke' #背景颜色
#plt.figure(facecolor='whitesmoke')

title_txt_size=16
ylabel_txt_size=12
xlabel_txt_size=12
legend_txt_size=12
annotate_size=11

if check_language() == "English":
    title_txt_size=20
    ylabel_txt_size=16
    xlabel_txt_size=16
    legend_txt_size=16
    annotate_size=13

#设置绘图风格：网格虚线
plt.rcParams['axes.grid']=False
#plt.rcParams['grid.color']='steelblue'
#plt.rcParams['grid.linestyle']='dashed'
#plt.rcParams['grid.linewidth']=0.5


#设置x，y 的主刻度定位器
#from matplotlib.pyplot import MultipleLocator


#处理绘图汉字乱码问题
import sys; czxt=sys.platform
if czxt in ['win32','win64']:
    #设置中文字体
    """
    plt.rcParams['font.sans-serif'] = ['SimHei']  # 设置默认字体
    mpfrc={'font.family': 'SimHei'}
    """
    plt.rcParams['font.sans-serif'] = ['SimHei']  # 设置默认字体
    mpfrc={'font.family': 'SimHei'}
    
    if check_language() == "English":
        #设置英文字体
        plt.rcParams['font.sans-serif'] = ['Times New Roman']  # 设置默认字体
        mpfrc={'font.family': 'Times New Roman'}
        
if czxt in ['darwin']: #MacOSX
    plt.rcParams['font.family']= ['Heiti TC']
    mpfrc={'font.family': 'Heiti TC'}

if czxt in ['linux']: #website Jupyter
    plt.rcParams['font.family']= ['Heiti TC']
    mpfrc={'font.family':'Heiti TC'}

# 解决保存图像时'-'显示为方块的问题
plt.rcParams['axes.unicode_minus'] = False 
#==============================================================================
if __name__ =="__main__":
    df0=get_price('000001.SS','2023-1-1','2024-3-22')
    df0=get_price('sz149995','2020-1-1','2024-3-31')
    df0,_=get_price_1ticker('sz149976',fromdate='2024-1-1',todate='2024-4-6',fill=True)
    
    colname='Close'
    collabel='Close'
    ylabeltxt='Close'
    titletxt='Title'
    footnote='footnote'
    datatag=False
    power=0
    zeroline=False
    average_value=False
    resample_freq='D'
    loc='best'
    date_range=False
    date_freq=False
    date_fmt='%Y-%m-%d'
    mark_top=True
    mark_bottom=True
    
    plot_line(df0,colname,collabel,ylabeltxt,titletxt,footnote,mark_top=True,mark_bottom=True)

def plot_line(df0,colname,collabel,ylabeltxt,titletxt,footnote,datatag=False, \
              power=0,zeroline=False, \
              attention_value='',attention_value_area='', \
              attention_point='',attention_point_area='', \
              average_value=False, \
                  
              resample_freq='D',loc='best', \
              date_range=False,date_freq=False,date_fmt='%Y-%m-%d', \
              mark_start=False,mark_top=True,mark_bottom=True,mark_end=True, \
              facecolor='whitesmoke',maxticks=15,translate=False):
    """
    功能：绘制折线图。如果power=0不绘制趋势图，否则绘制多项式趋势图
    假定：数据表有索引，且已经按照索引排序
    输入：数据表df，数据表中的列名colname，列名的标签collabel；y轴标签ylabeltxt；
    标题titletxt，脚注footnote；是否在图中标记数据datatag；趋势图的多项式次数power
    mark_top,mark_bottom：是否标记最高最低点
    输出：折线图
    返回值：无
    注意1：需要日期类型作为df索引
    注意2：date_freq不为False时，必须设置date_range=True，否则无法完成日期设置！
    """
    DEBUG=False
    
    import pandas as pd
    
    #空值判断
    if len(df0) ==0:
        print ("  #Warning(plot_line): no data to plot.")
        return
    
    #插值平滑：未填充时
    #if 'filled' not in list(df0):
    try:
        df0x=df0[[colname]].astype('float')
        df=df_smooth_manual(df0x,resample_freq=resample_freq)
    except:
        df=df0
    #else: df=df0
    
    print('')
    #先绘制折线图
    date_start=df.index[0]
    date_end=df.index[-1]
    ax=plt.gca()
    
    if date_range and not date_freq:
        ax.xaxis.set_major_formatter(mdate.DateFormatter(date_fmt))
        plt.xticks(pd.date_range(date_start,date_end))
    if not date_range and date_freq:
        ax.xaxis.set_major_formatter(mdate.DateFormatter(date_fmt))
        plt.xticks(pd.date_range(freq=date_freq))
    if date_range and date_freq:
        ax.xaxis.set_major_formatter(mdate.DateFormatter(date_fmt))
        plt.xticks(pd.date_range(date_start,date_end,freq=date_freq))

    if ylabeltxt != '' or ylabeltxt == "stooq_MB":
        collabel=''
        if ylabeltxt == "stooq_MB":
            ylabeltxt=''

    lwadjust=linewidth_adjust(df)
    
    #if 'filled' not in list(df):
    if translate:
        collabel=lang_auto2(collabel)
        
    if DEBUG: print(f"df.index: {df.index}")
    plt.plot(df.index,df[colname],'-',label=collabel, \
             linestyle='-',color='blue', linewidth=lwadjust)
    """
    else:
        #区分实际有数据部分和填充部分
        df_raw=df[df['filled'] == False] #原有数据
        df_filled=df[df['filled'] != False] #填充的数据
        
        plt.plot(df_filled.index,df_filled[colname],'-',label=collabel, \
                 linestyle=':',color='black', linewidth=lwadjust)
        
        plt.plot(df_raw.index,df_raw[colname],'-',label=collabel, \
                 linestyle='-',color='blue', linewidth=lwadjust)
    """        
    haveLegend=True
    if collabel == '':
        haveLegend=False
    
    #绘制数据标签
    if datatag:
        mark_start=False; mark_top=False; mark_bottom=False; mark_end=False
        for x, y in zip(df.index, df[colname]):
            plt.text(x,y*1.001,'%.2f' % y,ha='center',va='bottom',color='black')        

    #标记最高点/最低点
    if mark_top or mark_bottom:
        df_mark=df[[colname]].copy() #避免影响原df
        df_mark.sort_values(by=colname,ascending=False,inplace=True)
        
        high_poit=df_mark[colname].head(1).values[0]
        low_poit=df_mark[colname].tail(1).values[0]
        high_low=high_poit - low_poit
        if mark_top:
            df_mark_top=df_mark[:1]
            for x, y in zip(df_mark_top.index, df_mark_top[colname]):
                #plt.text(x,y+0.1,'%.2f' % y,ha='center',va='bottom',color='red')
                #y1=round(y+high_low*0.01,2)
                y1=y+high_low*0.01
                #s='%.0f' if y >= 100 else '%.2f'
                s='%.1f' if abs(y) >= 100 else '%.2f' if abs(y) >= 1 else '%.4f' 
                plt.text(x,y1,s % y,ha='right',va='bottom',color='red')
                """
                s='%.0f' if y >= 100 else '%.2f'
                plt.text(x,y,s % y,ha='right',va='bottom',color='red')
                """
                plt.scatter(x,y, color='red',marker='8',s=70)
            
        if mark_bottom:
            df_mark_bottom=df_mark[-1:]
            for x, y in zip(df_mark_bottom.index, df_mark_bottom[colname]):
                #plt.text(x,y-0.1,'%.2f' % y,ha='center',va='bottom',color='black')  
                #y1=round(y-high_low*0.055,2) #标记位置对应y1的底部
                y1=y-high_low*0.050 #标记位置对应y1的底部
                #s='%.0f' if y >= 100 else '%.2f'
                #s='%.2f' if abs(y) >= 100 else '%.2f' if abs(y) >= 10 else '%.4f'
                s='%.1f' if abs(y) >= 100 else '%.2f' if abs(y) >= 1 else '%.4f'
                #plt.text(x,y1,s % y,ha='center',va='bottom',color='seagreen')
                plt.text(x,y1,s % y,ha='right',va='bottom',color='seagreen')
                plt.scatter(x,y, color='seagreen',marker='8',s=70)

    #标记曲线开始数值
    if mark_start:
        df_start=df.head(1)
        y_start = df_start[colname].min()    # 开始的y坐标
        x_start = df_start[colname].idxmin() # 开始值的x坐标 
        
        #y1=str(int(y_end)) if y_end >= 100 else str(round(y_end,2))
        y1=str(round(y_start,1)) if abs(y_start) >= 100 else str(round(y_start,2)) if abs(y_start) >= 1 else str(round(y_start,3)) 
        plt.annotate(text=y1, 
                     xy=(x_start, y_start),
                     xytext=(x_start, y_start*0.998),fontsize=annotate_size,ha='right',va='center')
        # 特别注意：这里的left/right与实际图示的方向正好相反！！！

    #标记曲线末端数值
    if mark_end:
        df_end=df.tail(1)
        y_end = df_end[colname].min()    # 末端的y坐标
        x_end = df_end[colname].idxmin() # 末端值的x坐标 
        
        #y1=str(int(y_end)) if y_end >= 100 else str(round(y_end,2))
        y1=str(round(y_end,1)) if abs(y_end) >= 100 else str(round(y_end,2)) if abs(y_end) >= 1 else str(round(y_end,3)) 
        plt.annotate(text=' '+y1, 
                     xy=(x_end, y_end),
                     xytext=(x_end, y_end*0.998),fontsize=annotate_size,ha='left',va='center')
    
    #是否绘制水平线
    if isinstance(zeroline,bool):#若zeroline为True
        if zeroline: 
            hline=0
            #plt.axhline(y=hline,ls=":",c="green",linewidth=2,label="零线")
            plt.axhline(y=hline,ls=":",c="black",linewidth=2,label='')
            haveLegend=False
    else:
        #不再必要，被attention_value的逻辑替代
        if isinstance(zeroline,float) or isinstance(zeroline,int):
            hline=zeroline
            plt.axhline(y=hline,ls=":",c="darkorange",linewidth=3,label=text_lang("关注值","Attention"))
            haveLegend=True
            footnote=footnote + text_lang("，关注值",", Attention ")+str(hline)

    #用于关注值的颜色列表
    atv_color_list=["lightgray","paleturquoise","wheat","khaki","fuchsia","cyan","mistyrose","dodgerblue","magenta","lightseagreen"]
    #用于关注点的颜色列表
    atp_color_list=["crimson","dodgerblue","magenta","lightseagreen","chocolate","violet","orchid","paleturquoise","wheat","khaki"]

    if not attention_value=='':
        haveLegend=True
        
        if isinstance(attention_value,int) or isinstance(attention_value,float):
            atv_list=[attention_value]
        elif isinstance(attention_value,list):
            atv_list=attention_value
        else:
            atv_list=[]
        if not atv_list==[] and not atv_list==['']:
            for at in atv_list:
                pos=atv_list.index(at)
                color=atv_color_list[pos]
                plt.axhline(y=at,ls=":",c=color,linewidth=2,label=text_lang("关注值","Attention value ")+str(at))

    if not attention_value_area=='':
        if isinstance(attention_value_area,list) and len(attention_value_area)>=2:
            plt.fill_between(df.index,attention_value_area[0],attention_value_area[1],color='lightgray',alpha=0.5)
    
    import pandas as pd
    from datetime import datetime; date_format="%Y-%m-%d" 
    if not attention_point=='':
        haveLegend=True
        
        if isinstance(attention_point,str) or isinstance(attention_point,int) or isinstance(attention_point,float):
            atp_list=[attention_point]
        elif isinstance(attention_point,list):
            atp_list=attention_point
        else:
            atp_list=[]
        #去重，不打乱原来的顺序
        atp_list=list(dict.fromkeys(atp_list))
            
        if not atp_list==[] and not atp_list==['']:
            
            for at in atp_list:
                pos=atp_list.index(at)
                color=atp_color_list[pos]
                
                #判断是否日期字符串
                try:
                    #at=datetime.strptime(at, date_format)
                    atpd=pd.to_datetime(at)
                except:
                    atpd=at
                    
                if DEBUG: print(f"atpd={atpd}")
                    
                try:
                    at_str=atpd.strftime('%Y-%m-%d')
                except:
                    at_str=atpd
                #plt.axvline(x=atpd,ls=":",c=color,linewidth=1.5,label=text_lang("关注点","Attention point ")+str(at))
                plt.axvline(x=atpd,ls=":",c=color,linewidth=1.5,label=text_lang("关注点","Attention point ")+at_str)

    if not attention_point_area=='':
        if isinstance(attention_point_area,list) and len(attention_point_area)>=2:
            apa_list=[]
            for ap in attention_point_area:
                try:
                    #ap=datetime.strptime(ap, date_format)
                    appd=pd.to_datetime(ap)
                except:
                    appd=ap
                apa_list=apa_list+[appd]
                
            yaxis_data=plt.ylim()
            
            if DEBUG: 
                print(f"yaxis_data={yaxis_data}")
                print(f"apa_list[0]={apa_list[0]}")
                print(f"apa_list[1]={apa_list[1]}")
            plt.fill_betweenx(yaxis_data,apa_list[0],apa_list[1],color='powderblue',alpha=0.5)

    if average_value:
        haveLegend=True
        
        av=df[colname].mean()
        #av=str(round(av,2)) if av < 100 else str(int(av))
        #av=str(int(av)) if abs(av) >= 100 else str(round(av,2)) if abs(av) >= 10 else str(round(av,3))
        avstr=str(int(av)) if abs(av) >= 100 else str(round(av,2)) if abs(av) >= 10 else str(round(av,3))
        plt.axhline(y=av,ls="dashed",c="blueviolet",linewidth=2,label=text_lang("本期间均值","Periodic mean ")+avstr)
        #footnote=footnote + "，均值"+av
        #footnote=text_lang("注：期间均值","Note: Periodic mean ")+av+"; "+footnote
    
    #绘制趋势线
    #print("--Debug(plot_line): power=",power)
    if power > 0:
        trend_txt=text_lang('趋势线','Trend line')
        if power > 100: power=100
        try:
            #生成行号，借此将横轴的日期数量化，以便拟合
            df['id']=range(len(df))
        
            #设定多项式拟合，power为多项式次数
            import numpy as np
            parameter = np.polyfit(df.id, df[colname], power)
            f = np.poly1d(parameter)
            plt.plot(df.index, f(df.id),"r--", label=trend_txt,linewidth=1)
            
            haveLegend=True
        except: 
            print("  #Warning(plot_line): failed to converge trend line, try a smaller power.")
    
    if ylabeltxt != '' or average_value or isinstance(zeroline,bool):
        if haveLegend:
            plt.legend(loc=loc,fontsize=legend_txt_size)
    
    # 使用 AutoDateLocator 自动选择最佳间隔，目的是显示最后一个日期，亲测有效！！！
    import matplotlib.dates as mdates
    ax.xaxis.set_major_locator(mdates.AutoDateLocator(maxticks=maxticks))
    
    plt.gcf().autofmt_xdate(ha="center") # 优化标注（自动倾斜）
    try:
        plt.gca().set_facecolor(facecolor) #设置画布背景颜色
    except:
        print("  #Warning(plot_line): color",facecolor,"is unsupported, changed to default setting")
        plt.gca().set_facecolor("whitesmoke")
    
    if '基金' in titletxt and '收盘价' in ylabeltxt and not ('基金指数' in titletxt):
        ylabeltxt=ylabeltxt.replace('收盘价','单位净值')

    if translate:
        ylabeltxt=lang_auto2(ylabeltxt)
        footnote=lang_auto2(footnote)
        titletxt=lang_auto2(titletxt)
        
    plt.ylabel(ylabeltxt,fontsize=ylabel_txt_size)
    plt.xlabel(footnote,fontsize=xlabel_txt_size,ha='center')
    plt.title(titletxt,fontweight='bold',fontsize=title_txt_size)
    
    if haveLegend:
        plt.legend(loc=loc,fontsize=legend_txt_size)
        
    plt.show()
    plt.close()
    
    return


#==============================================================================
if __name__ =="__main__":
    df1=df2=option_comm_china(symbol='黄金期权',contract='au2508',printout=False,graph=False)
    
    ticker1='看涨期权'; ticker2='看跌期权' 
    colname1='最新价C'; colname2='最新价P'
    label1=label2=ylabeltxt='价格'
    twinx=True
    
    power=0
    datatag1=False
    datatag2=False
    yscalemax=5
    zeroline=False
    twinx=False
    yline=999
    xline=999
    resample_freq='D'
    
    attention_value_area=''; attention_point_area=''
    loc1='best'; loc2='best'
    color1='red'; color2='blue'; facecolor='whitesmoke'; maxticks=20

def plot_line2(df1,ticker1,colname1,label1, \
               df2,ticker2,colname2,label2, \
               ylabeltxt,titletxt,footnote, \
               power=0,datatag1=False,datatag2=False,yscalemax=5, \
               zeroline=False, \
                   twinx=False, \
                   yline=999,attention_value_area='', \
                   xline=999,attention_point_area='', \
               resample_freq='D',loc1='best',loc2='best', \
               color1='red',color2='blue',facecolor='whitesmoke', \
                   maxticks=20):
    """
    功能：绘制两个证券的折线图。如果power=0不绘制趋势图，否则绘制多项式趋势图
    假定：数据表有索引，且已经按照索引排序
    输入：
    证券1：数据表df1，证券代码ticker1，列名1，列名标签1；
    证券2：数据表df2，证券代码ticker2，列名2，列名标签2；
    标题titletxt，脚注footnote；是否在图中标记数据datatag；趋势图的多项式次数power
    输出：默认绘制同轴折线图，若twinx=True则绘制双轴折线图
    返回值：无
    注意：需要日期类型作为df索引
    """
    DEBUG=False
    
    #空值判断
    if len(df1) ==0:
        print ("  #Warning(plot_line2): no data to plot df1.")
    if len(df2) ==0:
        print ("  #Warning(plot_line2): no data to plot df2.")
    if (len(df1) ==0) and (len(df2) ==0):
        pass
        return
    
    if DEBUG:
        print("In plot_line2")
        print("Going to plot_line2_coaxial")
        print("yline=",yline,"; xline=",xline)
    
    if power > 100: power=100
    
    #if not twinx:
    if twinx == True: # 双轴会图
        plot_line2_twinx(df1,ticker1,colname1,label1, \
                         df2,ticker2,colname2,label2, \
                         titletxt,footnote,power,datatag1,datatag2, \
                         resample_freq=resample_freq, \
                             xline=xline,attention_point_area=attention_point_area, \
                         loc1=loc1,loc2=loc2, \
                         color1=color1,color2=color2,facecolor=facecolor, \
                             maxticks=maxticks)
    elif twinx == False: # twinx == False # 正常绘图           
        plot_line2_coaxial(df1,ticker1,colname1,label1, \
                df2,ticker2,colname2,label2, \
                ylabeltxt,titletxt,footnote,power,datatag1,datatag2,zeroline, \
                    yline=yline,attention_value_area=attention_value_area, \
                    xline=xline,attention_point_area=attention_point_area, \
                resample_freq=resample_freq, \
                loc1=loc1,loc2=loc2, \
                color1=color1,color2=color2,facecolor=facecolor, \
                    maxticks=maxticks)
            
    elif 'LR' in twinx.upper(): # 左右双图
        plot_line2_LR(df1,ticker1,colname1,label1, \
                         df2,ticker2,colname2,label2, \
                         titletxt,footnote,power,datatag1,datatag2, \
                         resample_freq=resample_freq, \
                             xline=xline,attention_point_area=attention_point_area, \
                         loc1=loc1,loc2=loc2, \
                         color1=color1,color2=color2,facecolor=facecolor, \
                             maxticks=maxticks)
    elif 'UD' in twinx.upper(): # 上下双图
        plot_line2_UD(df1,ticker1,colname1,label1, \
                         df2,ticker2,colname2,label2, \
                         titletxt,footnote,power,datatag1,datatag2, \
                         resample_freq=resample_freq, \
                             xline=xline,attention_point_area=attention_point_area, \
                         loc1=loc1,loc2=loc2, \
                         color1=color1,color2=color2,facecolor=facecolor, \
                             maxticks=maxticks)
        
    else: # twinx == False # 正常绘图           
        plot_line2_coaxial(df1,ticker1,colname1,label1, \
                df2,ticker2,colname2,label2, \
                ylabeltxt,titletxt,footnote,power,datatag1,datatag2,zeroline, \
                    yline=yline,attention_value_area=attention_value_area, \
                    xline=xline,attention_point_area=attention_point_area, \
                resample_freq=resample_freq, \
                loc1=loc1,loc2=loc2, \
                color1=color1,color2=color2,facecolor=facecolor, \
                    maxticks=maxticks)
            
    return


#==============================================================================
def plot2_line2(df1,ticker1,colname1,label1, \
               df2,ticker2,colname2,label2, \
               ylabeltxt,titletxt,footnote, \
               power=0,datatag1=False,datatag2=False,yscalemax=5, \
               zeroline=False,twinx=False, \
                   yline=999,attention_value_area='', \
                   xline=999,attention_point_area='', \
               resample_freq='D',loc1='best',loc2='best', \
               date_range=False,date_freq=False,date_fmt='%Y-%m-%d', \
               color1='red',color2='blue',facecolor='whitesmoke', \
                   maxticks=20):
    """
    注意：可能有bug，twinx=True时左纵坐标轴和横坐标轴标记可能发生重叠！!!暂不建议使用
    facecolor不起作用
    目前的解决方案：改用函数plot_line2
    
    功能：绘制两个证券的折线图。如果power=0不绘制趋势图，否则绘制多项式趋势图
    假定：数据表有索引，且已经按照索引排序
    输入：
    证券1：数据表df1，证券代码ticker1，列名1，列名标签1；
    证券2：数据表df2，证券代码ticker2，列名2，列名标签2；
    标题titletxt，脚注footnote；是否在图中标记数据datatag；趋势图的多项式次数power
    输出：默认绘制同轴折线图，若twinx=True则绘制双轴折线图
    返回值：无
    注意：需要日期类型作为df索引
    
    date_range：表示绘图横轴是否需要尽量绘制开始和结束日期
    date_freq：定义绘图横轴的日期间隔，False表示自动间隔，'1Y'表示以1年为单位间隔,
               '1M'表示间隔一个月，'3M'表示间隔3个月等
    date_fmt：定义绘图横轴日期的格式，'%Y-%m-%d'表示YYYY-mm-dd，'%Y-%m'表示YYYY-mm，
               '%Y'表示YYYY
    """
    #空值判断
    if len(df1) ==0:
        print ("  #Warning(plot2_line2): no data to plot df1.")
    if len(df2) ==0:
        print ("  #Warning(plot2_line2): no data to plot df2.")
    if (len(df1) ==0) and (len(df2) ==0):
        return
    
    if power > 100: power=100
    
    if not twinx:            
        plot_line2_coaxial2(df1,ticker1,colname1,label1, \
                            df2,ticker2,colname2,label2, \
                ylabeltxt,titletxt,footnote,power,datatag1,datatag2,zeroline, \
                    yline=yline,attention_value_area=attention_value_area, \
                    xline=xline,attention_point_area=attention_point_area, \
                resample_freq=resample_freq, \
                loc1=loc1,loc2=loc2, \
                date_range=date_range,date_freq=date_freq,date_fmt=date_fmt, \
                color1=color1,color2=color2,facecolor=facecolor, \
                    maxticks=maxticks)
    else:
        plot_line2_twinx2(df1,ticker1,colname1,label1, \
                         df2,ticker2,colname2,label2, \
                         titletxt,footnote,power,datatag1,datatag2, \
                             xline,attention_point_area=attention_point_area, \
                         resample_freq=resample_freq, \
                         loc1=loc1,loc2=loc2, \
                         date_range=date_range,date_freq=date_freq,date_fmt=date_fmt, \
                         color1=color1,color2=color2,facecolor=facecolor, \
                             maxticks=maxticks)
            
    return


#==============================================================================


def plot_line2_coaxial(df01,ticker1,colname1,label1, \
                       df02,ticker2,colname2,label2, \
                       ylabeltxt,titletxt,footnote, \
                       power=0,datatag1=False,datatag2=False,zeroline=False, \
                           yline=999,attention_value_area='', \
                           xline=999,attention_point_area='', \
                       resample_freq='D', \
                       loc1='best',loc2='best', \
                       color1='red',color2='blue',facecolor='whitesmoke', \
                       ticker_type='auto',maxticks=15):
    """
    功能：绘制两个证券的折线图。如果power=0不绘制趋势图，否则绘制多项式趋势图
    假定：数据表有索引，且已经按照索引排序
    输入：
    证券1：数据表df1，证券代码ticker1，列名1，列名标签1；
    证券2：数据表df2，证券代码ticker2，列名2，列名标签2；
    标题titletxt，脚注footnote；是否在图中标记数据datatag；趋势图的多项式次数power
    输出：绘制同轴折线图
    返回值：无
    注意：需要日期类型作为df索引
    """
    DEBUG=False
    
    import pandas as pd

    #插值平滑：如果横轴不为日期型时不可平滑，否则数据会丢失！
    if not isinstance(maxticks,bool):    
        try:
            df01x=df01[[colname1]].astype('float')
            df1=df_smooth_manual(df01x,resample_freq=resample_freq)
        except:
            df1=df01
        try:
            df02x=df02[[colname2]].astype('float')
            df2=df_smooth_manual(df02x,resample_freq=resample_freq)
        except:
            df2=df02
    else:
        df1=df01; df2=df02            
    
    #预处理ticker_type
    ticker_type_list=ticker_type_preprocess_mticker_mixed([ticker1,ticker2],ticker_type)    
    
    #证券1：先绘制折线图
    
    if ticker1 == '':
        label1txt=label1
    else:
        if label1 == '':
            label1txt=ticker_name(ticker1,ticker_type_list[0])
        else:
            label1txt=ticker_name(ticker1,ticker_type_list[0])+'('+label1+')'    
    
    lwadjust=linewidth_adjust(df1)
    
    x = pd.to_datetime(df1.index)
    y = pd.to_numeric(df1[colname1], errors='coerce')
    plt.plot(x,y,'-',label=label1txt, \
             linestyle='-',linewidth=lwadjust,color=color1)
    
    #证券1：绘制数据标签
    if datatag1:
        for x, y in zip(df1.index, df1[colname1]):
            plt.text(x,y+0.1,'%.2f' % y,ha='center',va='bottom',color='black')        

    #是否绘制水平0线
    df_max=max([df1[colname1].max(),df2[colname2].max()])
    df_min=min([df1[colname1].min(),df2[colname2].min()])
    if df_max * df_min >=0: #同正同负
        zeroline=False
    else:
        zeroline=True

    #if zeroline and ((min(df1[colname1]) < 0) or (min(df2[colname2]) < 0)):
    if zeroline:
        plt.axhline(y=0,ls=":",c="black",linewidth=2)

    if DEBUG:
        print("In plot_line2_coaxial:")
        print("yline=",yline,"; xline=",xline)
        
    #是否绘制水平线
    if yline != 999:
        attention_value=yline
        
        #用于关注值的颜色列表
        atv_color_list=["lightgray","paleturquoise","wheat","khaki","lightsage"]     
        
        if isinstance(attention_value,int) or isinstance(attention_value,float):
            atv_list=[attention_value]
        elif isinstance(attention_value,list):
            atv_list=attention_value
        else:
            atv_list=[]

        if DEBUG:
            print("atv_list=",atv_list)
            
        if not atv_list==[] and not atv_list==['']:
            for at in atv_list:
                pos=atv_list.index(at)
                color=atv_color_list[pos]
                plt.axhline(y=at,ls=":",c=color,linewidth=2,label=text_lang("关注值","Attention value ")+str(at))        

    if not attention_value_area=='':
        if isinstance(attention_value_area,list) and len(attention_value_area)>=2:
            plt.fill_between(df1.index,attention_value_area[0],attention_value_area[1],color='lightgray',alpha=0.5)

    #是否绘制垂直线
    import pandas as pd
    from datetime import datetime; date_format="%Y-%m-%d"
    if xline != 999:
        attention_point=xline
        #用于关注点的颜色列表
        atp_color_list=["crimson","dodgerblue","magenta","lightseagreen","chocolate"]
        
        if isinstance(attention_point,str) or isinstance(attention_point,int) or isinstance(attention_point,float):
            atp_list=[attention_point]
        elif isinstance(attention_point,list):
            atp_list=attention_point
        else:
            atp_list=[]
            
        #去重，不打乱原来的顺序
        atp_list=list(dict.fromkeys(atp_list))
        
        if not atp_list==[] and not atp_list==['']:
            
            for at in atp_list:
                pos=atp_list.index(at)
                color=atp_color_list[pos]
                
                #判断是否日期字符串
                try:
                    at=datetime.strptime(at, date_format)
                    atpd=pd.to_datetime(at)
                except:
                    atpd=at

                if DEBUG:
                    print("atpd=",atpd)
                    
                try:
                    at_str=atpd.strftime('%Y-%m-%d')
                except:
                    at_str=atpd
                plt.axvline(x=atpd,ls=":",c=color,linewidth=1.5,label=text_lang("关注点","Attention point ")+at_str)        

    if not attention_point_area=='':
        if isinstance(attention_point_area,list) and len(attention_point_area)>=2:
            apa_list=[]
            for ap in attention_point_area:
                try:
                    ap=datetime.strptime(ap, date_format)
                    appd=pd.to_datetime(ap)
                except:
                    appd=ap
                apa_list=apa_list+[appd]
                
            yaxis_data=plt.ylim()
            plt.fill_betweenx(yaxis_data,apa_list[0],apa_list[1],color='powderblue',alpha=0.5)
    
    #绘证券1：制趋势线
    if power > 0:
        trend_txt=text_lang('趋势线','Trend line')
            
        try:
            #生成行号，借此将横轴的日期数量化，以便拟合
            df1['id']=range(len(df1))
        
            #设定多项式拟合，power为多项式次数
            import numpy as np
            parameter = np.polyfit(df1.id, df1[colname1], power)
            f = np.poly1d(parameter)
            
            if ticker1 == '':
                label1txt=''
            else:
                label1txt=ticker_name(ticker1,ticker_type_list[0])+"("+trend_txt+")"            
                    
            #plt.plot(df1.index, f(df1.id),"g--", label=label1txt,linewidth=1)
            plt.plot(df1.index, f(df1.id),"g--", label='',linewidth=1)
        except: pass
    
    #证券2：先绘制折线图
    if ticker2 == '':
        label2txt=label2
    else:
        if label2 == '':
            label2txt=ticker_name(ticker2,ticker_type_list[1])
        else:
            label2txt=ticker_name(ticker2,ticker_type_list[1])+'('+label2+')'    
    
    lwadjust=linewidth_adjust(df2)
    
    x = pd.to_datetime(df2.index)
    y = pd.to_numeric(df2[colname2], errors='coerce')

    plt.plot(x,y,'-',label=label2txt, \
             linestyle='-.',linewidth=lwadjust,color=color2)
    #证券2：绘制数据标签
    if datatag2:
        for x, y in zip(df2.index, df2[colname2]):
            plt.text(x,y+0.1,'%.2f' % y,ha='center',va='bottom',color='black')        
        
    #绘证券2：制趋势线
    if power > 0:
        lang=check_language()
        trend_txt='趋势线'
        if lang == 'English':
            trend_txt='Trend line'    
            
        try:
            #生成行号，借此将横轴的日期数量化，以便拟合
            df2['id']=range(len(df2))
        
            #设定多项式拟合，power为多项式次数
            import numpy as np
            parameter = np.polyfit(df2.id, df2[colname2], power)
            f = np.poly1d(parameter)
            
            if ticker2 == '':
                label2txt=''
            else:
                label2txt=ticker_name(ticker2,ticker_type_list[1])+"("+trend_txt+")"            
                    
            #plt.plot(df2.index, f(df2.id),"r--", label=label2txt,linewidth=1)
            plt.plot(df2.index, f(df2.id),"r--", label='',linewidth=1)
        except: pass
    
    # 同轴绘图时，loc2未用上！
    plt.legend(loc=loc1,fontsize=legend_txt_size)
    
    # 使用 AutoDateLocator 自动选择最佳间隔，目的是显示最后一个日期，亲测有效！！！
    if not isinstance(maxticks,bool):    
        import matplotlib.dates as mdates
        try:
            ax=plt.gca()
            ax.xaxis.set_major_locator(mdates.AutoDateLocator(maxticks=maxticks))    
        except:
            pass
        
        plt.gcf().autofmt_xdate(ha="center") # 优化标注（自动倾斜）
        
    try:
        plt.gca().set_facecolor(facecolor)
    except:
        print("  #Warning(plot_line2_coaxial): color",facecolor,"is unsupported, changed to default setting")
        plt.gca().set_facecolor("whitesmoke")
    
    plt.ylabel(ylabeltxt,fontsize=ylabel_txt_size)
    plt.xlabel(footnote,fontsize=xlabel_txt_size,ha='center')
    plt.title(titletxt,fontweight='bold',fontsize=title_txt_size)
    plt.show()
    plt.close()
    
    return

if __name__ =="__main__":
    df1 = get_price('000002.SZ', '2020-1-1', '2020-3-16')
    df2 = get_price('600266.SS', '2020-1-1', '2020-3-16')
    ticker1='000002.SZ'; ticker2='600266.SS'
    colname1='Close'; colname2='Close'
    label1="收盘价"; label2="收盘价"
    ylabeltxt="价格"
    plot_line2_coaxial(df1,'000002.SZ','High','最高价', \
        df1,'000002.SZ','Low','最低价',"价格", \
        "证券价格走势对比图","数据来源：新浪/stooq")
    plot_line2_coaxial(df1,'000002.SZ','Open','开盘价', \
        df1,'000002.SZ','Close','收盘价',"价格", \
        "证券价格走势对比图","数据来源：新浪/stooq")

    plot_line2_coaxial(df2,'600266.SS','Open','开盘价', \
        df2,'600266.SS','Close','收盘价',"价格", \
        "证券价格走势对比图","数据来源：新浪/stooq")

#==============================================================================
def plot_line2_coaxial2(df01,ticker1,colname1,label1, \
                       df02,ticker2,colname2,label2, \
                       ylabeltxt,titletxt,footnote, \
                       power=0,datatag1=False,datatag2=False,zeroline=False, \
                           yline=999,attention_value_area='', \
                           xline=999,attention_point_area='', \
                       resample_freq='D', \
                       loc1='best',loc2='best', \
                       date_range=False,date_freq=False,date_fmt='%Y-%m-%d', \
                       color1='red',color2='blue',facecolor='whitesmoke', \
                       ticker_type='auto', \
                           maxticks=15):
    """
    功能：绘制两个证券的折线图。如果power=0不绘制趋势图，否则绘制多项式趋势图
    假定：数据表有索引，且已经按照索引排序
    输入：
    证券1：数据表df1，证券代码ticker1，列名1，列名标签1；
    证券2：数据表df2，证券代码ticker2，列名2，列名标签2；
    标题titletxt，脚注footnote；是否在图中标记数据datatag；趋势图的多项式次数power
    输出：绘制同轴折线图
    返回值：无
    注意：需要日期类型作为df索引
    """
    import pandas as pd
    DEBUG=False
    
    #插值平滑：对于df索引为非日期型的不能进行插值平滑，否则会丢失数据！！！
    if not isinstance(maxticks,bool):    
        try:
            df01x=df01[[colname1]].astype('float')
            df1=df_smooth_manual(df01x,resample_freq=resample_freq)
        except:
            df1=df01
        try:
            df02x=df02[[colname2]].astype('float')
            df2=df_smooth_manual(df02x,resample_freq=resample_freq)
        except:
            df2=df02
    else:
        df1=df01; df2=df02
        
    #预处理ticker_type
    ticker_type_list=ticker_type_preprocess_mticker_mixed([ticker1,ticker2],ticker_type)    
        
    #证券1：先绘制折线图
    if ticker1 == '':
        label1txt=label1
    else:
        if label1 == '':
            label1txt=ticker_name(ticker1,ticker_type_list[0])
        else:
            label1txt=ticker_name(ticker1,ticker_type_list[0])+'('+label1+')'    

    ax=plt.gca()    
    date_start=df1.index[0]
    date_end=df1.index[-1]
    import pandas as pd
    
    if date_range and not date_freq:
        ax.xaxis.set_major_formatter(mdate.DateFormatter(date_fmt))
        plt.xticks(pd.date_range(date_start,date_end))
    if not date_range and date_freq:
        ax.xaxis.set_major_formatter(mdate.DateFormatter(date_fmt))
        plt.xticks(pd.date_range(freq=date_freq))
    if date_range and date_freq:
        ax.xaxis.set_major_formatter(mdate.DateFormatter(date_fmt))
        plt.xticks(pd.date_range(date_start,date_end,freq=date_freq))    

    lwadjust=linewidth_adjust(df1)
    plt.plot(df1.index,df1[colname1],'-',label=label1txt, \
             linestyle='-',linewidth=lwadjust,color=color1)
    #证券1：绘制数据标签
    if datatag1:
        for x, y in zip(df1.index, df1[colname1]):
            plt.text(x,y+0.1,'%.2f' % y,ha='center',va='bottom',color='black')        

    #是否绘制水平0线
    if zeroline and ((min(df1[colname1]) < 0) or (min(df2[colname2]) < 0)):
        plt.axhline(y=0,ls=":",c="black",linewidth=2.5)

    """
    #是否绘制水平线
    if yline != 999:
        plt.axhline(y=yline,ls=":",c="black",linewidth=2.5)        

    #是否绘制垂直线
    if xline != 999:
        plt.axvline(x=xline,ls=":",c="black",linewidth=2.5)   
    """
    #是否绘制水平线
    if yline != 999:
        attention_value=yline
        
        #用于关注值的颜色列表
        atv_color_list=["lightgray","paleturquoise","wheat","khaki","lightsage"]     
        
        if isinstance(attention_value,int) or isinstance(attention_value,float):
            atv_list=[attention_value]
        elif isinstance(attention_value,list):
            atv_list=attention_value
        else:
            atv_list=[]

        if DEBUG:
            print("atv_list=",atv_list)
            
        if not atv_list==[] and not atv_list==['']:
            for at in atv_list:
                pos=atv_list.index(at)
                color=atv_color_list[pos]
                plt.axhline(y=at,ls=":",c=color,linewidth=2,label=text_lang("关注值","Attention value ")+str(at))        

    if not attention_value_area=='':
        if isinstance(attention_value_area,list) and len(attention_value_area)>=2:
            plt.fill_between(df1.index,attention_value_area[0],attention_value_area[1],color='lightgray',alpha=0.5)

    #是否绘制垂直线
    import pandas as pd
    from datetime import datetime; date_format="%Y-%m-%d"
    if xline != 999:
        attention_point=xline
        #用于关注点的颜色列表
        atp_color_list=["crimson","dodgerblue","magenta","lightseagreen","chocolate"]
        
        if isinstance(attention_point,str) or isinstance(attention_point,int) or isinstance(attention_point,float):
            atp_list=[attention_point]
        elif isinstance(attention_point,list):
            atp_list=attention_point
        else:
            atp_list=[]
        #去重，不打乱原来的顺序
        atp_list=list(dict.fromkeys(atp_list))
            
        if not atp_list==[] and not atp_list==['']:
            
            for at in atp_list:
                pos=atp_list.index(at)
                color=atp_color_list[pos]
                
                #判断是否日期字符串
                try:
                    at=datetime.strptime(at, date_format)
                    atpd=pd.to_datetime(at)
                except:
                    atpd=at

                if DEBUG:
                    print("atpd=",atpd)
                    
                try:
                    at_str=atpd.strftime('%Y-%m-%d')
                except:
                    at_str=atpd
                #plt.axvline(x=atpd,ls=":",c=color,linewidth=1.5,label=text_lang("关注点","Attention point ")+str(at))
                plt.axvline(x=atpd,ls=":",c=color,linewidth=1.5,label=text_lang("关注点","Attention point ")+at_str)

    if not attention_point_area=='':
        if isinstance(attention_point_area,list) and len(attention_point_area)>=2:
            apa_list=[]
            for ap in attention_point_area:
                try:
                    ap=datetime.strptime(ap, date_format)
                    appd=pd.to_datetime(ap)
                except:
                    appd=ap
                apa_list=apa_list+[appd]
                
            yaxis_data=plt.ylim()
            plt.fill_betweenx(yaxis_data,apa_list[0],apa_list[1],color='powderblue',alpha=0.5)    
    
    
    #绘证券1：制趋势线
    if power > 0:
        lang=check_language()
        trend_txt='趋势线'
        if lang == 'English':
            trend_txt='Trend line'        
        
        try:
            #生成行号，借此将横轴的日期数量化，以便拟合
            df1['id']=range(len(df1))
        
            #设定多项式拟合，power为多项式次数
            import numpy as np
            parameter = np.polyfit(df1.id, df1[colname1], power)
            f = np.poly1d(parameter)
            
            if ticker1 == '':
                label1txt=''
            else:
                label1txt=ticker_name(ticker1,ticker_type_list[0])+"("+trend_txt+")"            
            plt.plot(df1.index, f(df1.id),"g--", label=label1txt,linewidth=1)
        except: pass
    
    #证券2：先绘制折线图
    if ticker2 == '':
        label2txt=label2
    else:
        if label2 == '':
            label2txt=ticker_name(ticker2,ticker_type_list[1])
        else:
            label2txt=ticker_name(ticker2,ticker_type_list[1])+'('+label2+')'    

    date_start=df2.index[0]
    date_end=df2.index[-1]
    if date_range and not date_freq:
        ax.xaxis.set_major_formatter(mdate.DateFormatter(date_fmt))
        plt.xticks(pd.date_range(date_start,date_end))
    if not date_range and date_freq:
        ax.xaxis.set_major_formatter(mdate.DateFormatter(date_fmt))
        plt.xticks(pd.date_range(freq=date_freq))
    if date_range and date_freq:
        ax.xaxis.set_major_formatter(mdate.DateFormatter(date_fmt))
        plt.xticks(pd.date_range(date_start,date_end,freq=date_freq))

    lwadjust=linewidth_adjust(df2)
    plt.plot(df2.index,df2[colname2],'-',label=label2txt, \
             linestyle='-.',linewidth=lwadjust,color=color2)
    #证券2：绘制数据标签
    if datatag2:
        for x, y in zip(df2.index, df2[colname2]):
            plt.text(x,y+0.1,'%.2f' % y,ha='center',va='bottom',color='black')        
        
    #绘证券2：制趋势线
    if power > 0:
        lang=check_language()
        trend_txt='趋势线'
        if lang == 'English':
            trend_txt='Trend line'        
        
        try:
            #生成行号，借此将横轴的日期数量化，以便拟合
            df2['id']=range(len(df2))
        
            #设定多项式拟合，power为多项式次数
            import numpy as np
            parameter = np.polyfit(df2.id, df2[colname2], power)
            f = np.poly1d(parameter)
            
            if ticker2 == '':
                label2txt=''
            else:
                label2txt=ticker_name(ticker2,ticker_type_list[1])+"("+trend_txt+")"            
            plt.plot(df2.index, f(df2.id),"r--", label=label2txt,linewidth=1)
        except: pass
    
    # 同轴绘图时，loc1/loc2未用上！
    plt.legend(loc=loc1,fontsize=legend_txt_size)
    
    # 使用 AutoDateLocator 自动选择最佳间隔，目的是显示最后一个日期，亲测有效！！！
    if not isinstance(maxticks,bool):    
        import matplotlib.dates as mdates
        ax.xaxis.set_major_locator(mdates.AutoDateLocator(maxticks=maxticks))    
        
        plt.gcf().autofmt_xdate(ha="center") # 优化标注（自动倾斜）
    try:
        plt.gca().set_facecolor(facecolor)
    except:
        print("  #Warning(plot_line2_coaxial2): color",facecolor,"is unsupported, changed to default setting")
        plt.gca().set_facecolor("whitesmoke")  
        
    plt.ylabel(ylabeltxt,fontsize=ylabel_txt_size)
    plt.xlabel(footnote,fontsize=xlabel_txt_size,ha='center')
    plt.title(titletxt,fontweight='bold',fontsize=title_txt_size)
    plt.show()
    plt.close()
    
    return

#==============================================================================
if __name__ =="__main__":
    df01=df1; df02=df2
    maxticks=False    
    
def plot_line2_twinx(df01,ticker1,colname1,label1, \
                     df02,ticker2,colname2,label2, \
                     titletxt,footnote,power=0,datatag1=False,datatag2=False, \
                     resample_freq='D', \
                         xline=999,attention_point_area='', \
                     loc1='upper left',loc2='lower left', \
                     color1='red',color2='blue',facecolor='whitesmoke', \
                     ticker_type='auto', \
                         maxticks=15):
    """
    功能：绘制两个证券的折线图。如果power=0不绘制趋势图，否则绘制多项式趋势图
    假定：数据表有索引，且已经按照索引排序
    输入：
    证券1：数据表df1，证券代码ticker1，列名1，列名标签1；
    证券2：数据表df2，证券代码ticker2，列名2，列名标签2；
    标题titletxt，脚注footnote；是否在图中标记数据datatag；趋势图的多项式次数power
    输出：绘制双轴折线图
    返回值：无
    注意：需要日期类型作为df索引
    """
    DEBUG=False
    
    #plt.rcParams['axes.grid']=False
    
    #插值平滑
    if not isinstance(maxticks,bool):
        try:
            df01x=df01[[colname1]].astype('float')
            df1=df_smooth_manual(df01x,resample_freq=resample_freq)
        except:
            df1=df01
        try:
            df02x=df02[[colname2]].astype('float')
            df2=df_smooth_manual(df02x,resample_freq=resample_freq)
        except:
            df2=df02
    else:
        df1=df01; df2=df02
    
    #预处理ticker_type
    ticker_type_list=ticker_type_preprocess_mticker_mixed([ticker1,ticker2],ticker_type)        
    
    #证券1：绘制折线图，双坐标轴
    fig = plt.figure()
    ax = fig.add_subplot(111)
    try:
        fig.gca().set_facecolor(facecolor)
    except:
        print("  #Warning(plot_line2_twinx): color",facecolor,"is unsupported, changed to default setting")
        fig.gca().set_facecolor("whitesmoke") 
    
    if ticker1 == '':
        label1txt=label1
    else:
        if label1 == '':
            label1txt=ticker_name(ticker1,ticker_type_list[0])
        else:
            label1txt=ticker_name(ticker1,ticker_type_list[0])+'('+label1+')'   
            
    lwadjust=linewidth_adjust(df1)
    ax.plot(df1.index,df1[colname1],'-',label=label1txt, \
             linestyle='-',color=color1,linewidth=lwadjust)   
        
    #证券1：绘制数据标签
    if datatag1:
        for x, y in zip(df1.index, df1[colname1]):
            ax.text(x,y+0.1,'%.2f' % y,ha='center',va='bottom',color='black')

    #绘制关注点
    import pandas as pd
    from datetime import datetime; date_format="%Y-%m-%d"
    if xline != 999:
        attention_point=xline
        
        #用于关注点的颜色列表
        atp_color_list=["crimson","dodgerblue","magenta","lightseagreen","chocolate"]  
        
        if isinstance(attention_point,str) or isinstance(attention_point,int) or isinstance(attention_point,float):
            atp_list=[attention_point]
        elif isinstance(attention_point,list):
            atp_list=attention_point
        else:
            atp_list=[]
        #去重，不打乱原来的顺序
        atp_list=list(dict.fromkeys(atp_list))

        if DEBUG:
            print("In plot_line2_twinx")
            print("atp_list=",atp_list)
            
        if not atp_list==[] and not atp_list==['']:
            
            for at in atp_list:
                pos=atp_list.index(at)
                color=atp_color_list[pos]
                
                #判断是否日期字符串
                try:
                    at=datetime.strptime(at, date_format)
                    atpd=pd.to_datetime(at)
                except:
                    atpd=at
                    
                try:
                    at_str=atpd.strftime('%Y-%m-%d')
                except:
                    at_str=atpd
                plt.axvline(x=atpd,ls=":",c=color,linewidth=1.5,label=text_lang("关注点","Attention point ")+at_str)        

    if not attention_point_area=='':
        if isinstance(attention_point_area,list) and len(attention_point_area)>=2:
            apa_list=[]
            for ap in attention_point_area:
                try:
                    ap=datetime.strptime(ap, date_format)
                    appd=pd.to_datetime(ap)
                except:
                    appd=ap
                apa_list=apa_list+[appd]
                
            yaxis_data=plt.ylim()
            plt.fill_betweenx(yaxis_data,apa_list[0],apa_list[1],color='powderblue',alpha=0.5)

    #绘证券1：制趋势线
    if power > 0:
        lang=check_language()
        trend_txt='趋势线'
        if lang == 'English':
            trend_txt='Trend line'        
        
        #生成行号，借此将横轴的日期数量化，以便拟合
        df1['id']=range(len(df1))
        
        #设定多项式拟合，power为多项式次数
        import numpy as np
        parameter = np.polyfit(df1.id, df1[colname1], power)
        f = np.poly1d(parameter)

        if ticker1 == '':
            label1txt=''
        else:
            label1txt=ticker_name(ticker1,ticker_type_list[0])+"("+trend_txt+")"
        ax.plot(df1.index, f(df1.id),"r--", label=label1txt,linewidth=1)

    #绘证券2：建立第二y轴
    ax2 = ax.twinx()
    
    if ticker2 == '':
        label2txt=label2
    else:
        if label2 == '':
            label2txt=ticker_name(ticker2,ticker_type_list[1])
        else:
            label2txt=ticker_name(ticker2,ticker_type_list[1])+'('+label2+')'   
            
    lwadjust=linewidth_adjust(df2)
    ax2.plot(df2.index,df2[colname2],'-',label=label2txt, \
             linestyle='-.',color=color2,linewidth=lwadjust)
    #证券2：绘制数据标签
    if datatag2:
        for x, y in zip(df2.index, df2[colname2]):
            ax2.text(x,y+0.1,'%.2f' % y,ha='center',va='bottom',color='black')
    
    #绘证券2：制趋势线
    if power > 0:
        lang=check_language()
        trend_txt='趋势线'
        if lang == 'English':
            trend_txt='Trend line'           
        
        #生成行号，借此将横轴的日期数量化，以便拟合
        df2['id']=range(len(df2))
        
        #设定多项式拟合，power为多项式次数
        import numpy as np
        parameter = np.polyfit(df2.id, df2[colname2], power)
        f = np.poly1d(parameter)

        if ticker2 == '':
            label2txt=''
        else:
            label2txt=ticker_name(ticker2,ticker_type_list[1])+"("+trend_txt+")"
        ax2.plot(df2.index, f(df2.id),"c--", label=label2txt,linewidth=1)        
        
    ax.set_xlabel(footnote,fontsize=xlabel_txt_size,ha='center')
    
    if ticker1 == '':
        label1txt=label1
    else:
        if label1 == "":
            label1txt=ticker_name(ticker1,ticker_type_list[0])
        else:
            label1txt=label1+'('+ticker_name(ticker1,ticker_type_list[0])+')'
    ax.set_ylabel(label1txt,fontsize=ylabel_txt_size)
    ax.legend(loc=loc1,fontsize=legend_txt_size)
    
    if ticker2 == '':
        label2txt=label2
    else:
        if label2 == "":
            label2txt=ticker_name(ticker2,ticker_type_list[1])
        else:
            label2txt=label2+'('+ticker_name(ticker2,ticker_type_list[1])+')'
    ax2.set_ylabel(label2txt,fontsize=ylabel_txt_size)
    ax2.legend(loc=loc2,fontsize=legend_txt_size)

    # 使用 AutoDateLocator 自动选择最佳间隔，目的是显示最后一个日期，亲测有效！！！
    if not isinstance(maxticks,bool):
        import matplotlib.dates as mdates
        ax.xaxis.set_major_locator(mdates.AutoDateLocator(maxticks=maxticks))
        ax2.xaxis.set_major_locator(mdates.AutoDateLocator(maxticks=maxticks))
        
        #自动优化x轴标签
        plt.gcf().autofmt_xdate(ha="center") # 优化标注（自动倾斜）
        
    plt.title(titletxt,fontweight='bold',fontsize=title_txt_size)
    plt.show()
    
    return


if __name__ =="__main__":
    df1 = get_price('000002.SZ', '2020-1-1', '2020-3-16')
    df2 = get_price('600266.SS', '2020-1-1', '2020-3-16')
    ticker1='000002.SZ'; ticker2='600266.SS'
    colname1='Close'; colname2='Close'
    label1="收盘价"; label2="收盘价"
    ylabeltxt="价格"
    plot_line2_twinx(df1,'000002.SZ','Close','收盘价', \
        df2,'600266.SS','Close','收盘价', \
        "证券价格走势对比图","数据来源：新浪/stooq")

    plot_line2_LR(df1,'000002.SZ','Close','收盘价', \
        df2,'600266.SS','Close','收盘价', \
        "证券价格走势对比图","数据来源：新浪/stooq",power=3)

#==============================================================================
def plot_line2_LR(df01,ticker1,colname1,label1, \
                  df02,ticker2,colname2,label2, \
                  titletxt,footnote,power=0, \
                      datatag1=False,datatag2=False, \
                      resample_freq='D', \
                      xline=999,attention_point_area='', \
                  loc1='upper left',loc2='lower left', \
                      color1='red',color2='blue',facecolor='whitesmoke', \
                      ticker_type='auto', \
                      maxticks=15):
    """
    功能：绘制两个证券或指标的左右折线图。如果power=0不绘制趋势图，否则绘制多项式趋势图
    假定：数据表有索引，且已经按照索引排序
    输入：
    证券1：数据表df1，证券代码ticker1，列名1，列名标签1；
    证券2：数据表df2，证券代码ticker2，列名2，列名标签2；
    标题titletxt，脚注footnote；是否在图中标记数据datatag；趋势图的多项式次数power
    输出：绘制左右并列折线图
    返回值：无
    注意：需要日期类型作为df索引
    """
    DEBUG=False
    
    #plt.rcParams['axes.grid']=False
    
    #插值平滑：若df索引为非日期型，不能进行插值平滑
    if not isinstance(maxticks,bool):    
        try:
            df01x=df01[[colname1]].astype('float')
            df1=df_smooth_manual(df01x,resample_freq=resample_freq)
        except:
            df1=df01
        try:
            df02x=df02[[colname2]].astype('float')
            df2=df_smooth_manual(df02x,resample_freq=resample_freq)
        except:
            df2=df02
    else:
        df1=df01; df2=df02            
    
    #预处理ticker_type
    ticker_type_list=ticker_type_preprocess_mticker_mixed([ticker1,ticker2],ticker_type)        
    
    #创建画布：绘制折线图，左右双子图
    fig, (ax, ax2) = plt.subplots(1, 2)
    
    #设置主标题
    #plt.suptitle(titletxt,fontweight='bold',fontsize=title_txt_size, y=1.01)  # y参数调整垂直位置
    plt.suptitle(titletxt,fontweight='bold',fontsize=title_txt_size)
    
    # 绘制左子图================================================================
    #设置画布背景颜色
    try:
        ax.set_facecolor(facecolor)
    except:
        print("  #Warning(plot_line2_twinx): color",facecolor,"is unsupported")
        facecolor="whitesmoke"
        ax.set_facecolor(facecolor) 
    
    # 设置折线标签
    if ticker1 == '':
        label1txt=label1
    else:
        if label1 == '':
            label1txt=ticker_name(ticker1,ticker_type_list[0])
        else:
            label1txt=ticker_name(ticker1,ticker_type_list[0])+'('+label1+')'   

    # 设置子图标题
    if ticker1 != ticker2:
        ax.set_title(label1txt,fontsize=xlabel_txt_size)
    else:
        ax.set_title(ectranslate(colname1),fontsize=xlabel_txt_size)

    # 绘图        
    lwadjust=linewidth_adjust(df1)
    """
    ax.plot(df1.index,df1[colname1],'-',label=label1txt, \
             linestyle='-',color=color1,linewidth=lwadjust)   
    """  
    ax.plot(df1.index,df1[colname1],'-', \
             linestyle='-',color=color1,linewidth=lwadjust)   

    #证券1：绘制数据标签
    if datatag1:
        for x, y in zip(df1.index, df1[colname1]):
            ax.text(x,y+0.1,'%.2f' % y,ha='center',va='bottom',color='black')

    #绘制关注点
    import pandas as pd
    from datetime import datetime; date_format="%Y-%m-%d"
    if xline != 999:
        attention_point=xline
        
        #用于关注点的颜色列表
        atp_color_list=["crimson","dodgerblue","magenta","lightseagreen","chocolate"]  
        
        if isinstance(attention_point,str) or isinstance(attention_point,int) or isinstance(attention_point,float):
            atp_list=[attention_point]
        elif isinstance(attention_point,list):
            atp_list=attention_point
        else:
            atp_list=[]
        #去重，不打乱原来的顺序
        atp_list=list(dict.fromkeys(atp_list))

        if DEBUG:
            print("In plot_line2_twinx")
            print("atp_list=",atp_list)
            
        if not atp_list==[] and not atp_list==['']:
            
            for at in atp_list:
                pos=atp_list.index(at)
                color=atp_color_list[pos]
                
                #判断是否日期字符串
                try:
                    at=datetime.strptime(at, date_format)
                    atpd=pd.to_datetime(at)
                except:
                    atpd=at
                    
                try:
                    at_str=atpd.strftime('%Y-%m-%d')
                except:
                    at_str=atpd
                #ax.axvline(x=atpd,ls=":",c=color,linewidth=1.5,label=text_lang("关注点","Attention point ")+str(at))  
                ax.axvline(x=atpd,ls=":",c=color,linewidth=1.5,label=text_lang("关注点","Attention point ")+at_str)        

    if not attention_point_area=='':
        if isinstance(attention_point_area,list) and len(attention_point_area)>=2:
            apa_list=[]
            for ap in attention_point_area:
                try:
                    ap=datetime.strptime(ap, date_format)
                    appd=pd.to_datetime(ap)
                except:
                    appd=ap
                apa_list=apa_list+[appd]
                
            yaxis_data=plt.ylim()
            ax.fill_betweenx(yaxis_data,apa_list[0],apa_list[1],color='powderblue',alpha=0.5)

    #绘证券1：制趋势线
    if power > 0:
        lang=check_language()
        trend_txt='趋势线'
        if lang == 'English':
            trend_txt='Trend line'        
        
        #生成行号，借此将横轴的日期数量化，以便拟合
        df1['id']=range(len(df1))
        
        #设定多项式拟合，power为多项式次数
        import numpy as np
        parameter = np.polyfit(df1.id, df1[colname1], power)
        f = np.poly1d(parameter)

        if ticker1 == '':
            label1txt=''
        else:
            label1txt=ticker_name(ticker1,ticker_type_list[0])+"("+trend_txt+")"
        ax.plot(df1.index, f(df1.id),"r--", label=label1txt,linewidth=1)

    # 纵轴标签
    #ax.set_ylabel(label1txt,fontsize=ylabel_txt_size)
    #ax.legend(loc=loc1,fontsize=legend_txt_size)

    # 横轴标签
    #ax.set_xlabel(text_lang("日期","Date"),fontsize=xlabel_txt_size,ha='center')

    #绘图右图===================================================================
    #设置画布背景颜色
    ax2.set_facecolor(facecolor)

    # 折线标签
    if ticker2 == '':
        label2txt=label2
    else:
        if label2 == '':
            label2txt=ticker_name(ticker2,ticker_type_list[1])
        else:
            label2txt=ticker_name(ticker2,ticker_type_list[1])+'('+label2+')'   

    # 设置子图标题
    if ticker1 != ticker2:
        ax2.set_title(label2txt,fontsize=xlabel_txt_size)
    else:
        ax2.set_title(ectranslate(colname2),fontsize=xlabel_txt_size)
    
    # 绘图        
    lwadjust=linewidth_adjust(df2)
    """
    ax2.plot(df2.index,df2[colname2],'-',label=label2txt, \
             linestyle='-.',color=color2,linewidth=lwadjust)
    """  
    ax2.plot(df2.index,df2[colname2],'-', \
             linestyle='-.',color=color2,linewidth=lwadjust)

    #证券2：绘制数据标签
    if datatag2:
        for x, y in zip(df2.index, df2[colname2]):
            ax2.text(x,y+0.1,'%.2f' % y,ha='center',va='bottom',color='black')
    
    #绘证券2：制趋势线
    if power > 0:
        lang=check_language()
        trend_txt='趋势线'
        if lang == 'English':
            trend_txt='Trend line'           
        
        #生成行号，借此将横轴的日期数量化，以便拟合
        df2['id']=range(len(df2))
        
        #设定多项式拟合，power为多项式次数
        import numpy as np
        parameter = np.polyfit(df2.id, df2[colname2], power)
        f = np.poly1d(parameter)

        if ticker2 == '':
            label2txt=''
        else:
            label2txt=ticker_name(ticker2,ticker_type_list[1])+"("+trend_txt+")"
        ax2.plot(df2.index, f(df2.id),"c--", label=label2txt,linewidth=1)        
    
    # 纵轴标签
    #ax2.set_ylabel(label2txt,fontsize=ylabel_txt_size)
    #ax2.legend(loc=loc2,fontsize=legend_txt_size)

    # 横轴标签
    #ax2.set_xlabel(text_lang("日期","Date"),fontsize=xlabel_txt_size,ha='center')
    
    #自动优化x轴标签
    #ax2.autofmt_xdate(ha="center") # 优化标注（自动倾斜）
    
    # 共同脚注==================================================================
    fig.text(0.5,-0.01,footnote,ha='center',fontsize=xlabel_txt_size,color='gray')
    #plt.xlabel(footnote,ha='center',fontsize=xlabel_txt_size,color='gray')
    
    # 自动倾斜横轴日期
    if not isinstance(maxticks,bool):    
        fig.autofmt_xdate(ha="center")
    
    # 调整布局防止重叠
    plt.tight_layout()        
    plt.show()
    
    return


#==============================================================================
def plot_line2_UD(df01,ticker1,colname1,label1, \
                  df02,ticker2,colname2,label2, \
                  titletxt,footnote,power=0, \
                      datatag1=False,datatag2=False, \
                      resample_freq='D', \
                      xline=999,attention_point_area='', \
                  loc1='upper left',loc2='lower left', \
                      color1='red',color2='blue',facecolor='whitesmoke', \
                      ticker_type='auto', \
                      maxticks=15):
    """
    功能：绘制两个证券或指标的上下折线图。如果power=0不绘制趋势图，否则绘制多项式趋势图
    假定：数据表有索引，且已经按照索引排序
    输入：
    证券1：数据表df1，证券代码ticker1，列名1，列名标签1；
    证券2：数据表df2，证券代码ticker2，列名2，列名标签2；
    标题titletxt，脚注footnote；是否在图中标记数据datatag；趋势图的多项式次数power
    输出：绘制上下并列折线图
    返回值：无
    注意：需要日期类型作为df索引
    """
    DEBUG=False
    
    #plt.rcParams['axes.grid']=False
    
    #插值平滑
    if not isinstance(maxticks,bool):    
        try:
            df01x=df01[[colname1]].astype('float')
            df1=df_smooth_manual(df01x,resample_freq=resample_freq)
        except:
            df1=df01
        try:
            df02x=df02[[colname2]].astype('float')
            df2=df_smooth_manual(df02x,resample_freq=resample_freq)
        except:
            df2=df02
    else:
        df1=df01; df2=df02            
    
    #预处理ticker_type
    ticker_type_list=ticker_type_preprocess_mticker_mixed([ticker1,ticker2],ticker_type)        
    
    #创建画布：绘制折线图，上下双子图
    fig, (ax, ax2) = plt.subplots(2, 1)
    
    #设置主标题
    #plt.suptitle(titletxt,fontweight='bold',fontsize=title_txt_size, y=1.01)  # y参数调整垂直位置
    plt.suptitle(titletxt,fontweight='bold',fontsize=title_txt_size)
    
    # 绘制左子图================================================================
    #设置画布背景颜色
    try:
        ax.set_facecolor(facecolor)
    except:
        print("  #Warning(plot_line2_twinx): color",facecolor,"is unsupported")
        facecolor="whitesmoke"
        ax.set_facecolor(facecolor) 
    
    # 设置折线标签
    if ticker1 == '':
        label1txt=label1
    else:
        if label1 == '':
            label1txt=ticker_name(ticker1,ticker_type_list[0])
        else:
            label1txt=ticker_name(ticker1,ticker_type_list[0])+'('+label1+')'   

    # 设置子图标题
    """
    if ticker1 != ticker2:
        ax.set_title(label1txt,fontsize=xlabel_txt_size)
    else:
        ax.set_title(ectranslate(colname1),fontsize=xlabel_txt_size)
    """
    # 绘图        
    lwadjust=linewidth_adjust(df1)
    """
    ax.plot(df1.index,df1[colname1],'-',label=label1txt, \
             linestyle='-',color=color1,linewidth=lwadjust)   
    """  
    ax.plot(df1.index,df1[colname1],'-', \
             linestyle='-',color=color1,linewidth=lwadjust)   

    #证券1：绘制数据标签
    if datatag1:
        for x, y in zip(df1.index, df1[colname1]):
            ax.text(x,y+0.1,'%.2f' % y,ha='center',va='bottom',color='black')

    #绘制关注点
    import pandas as pd
    from datetime import datetime; date_format="%Y-%m-%d"
    if xline != 999:
        attention_point=xline
        
        #用于关注点的颜色列表
        atp_color_list=["crimson","dodgerblue","magenta","lightseagreen","chocolate"]  
        
        if isinstance(attention_point,str) or isinstance(attention_point,int) or isinstance(attention_point,float):
            atp_list=[attention_point]
        elif isinstance(attention_point,list):
            atp_list=attention_point
        else:
            atp_list=[]
        #去重，不打乱原来的顺序
        atp_list=list(dict.fromkeys(atp_list))

        if DEBUG:
            print("In plot_line2_twinx")
            print("atp_list=",atp_list)
            
        if not atp_list==[] and not atp_list==['']:
            
            for at in atp_list:
                pos=atp_list.index(at)
                color=atp_color_list[pos]
                
                #判断是否日期字符串
                try:
                    at=datetime.strptime(at, date_format)
                    atpd=pd.to_datetime(at)
                except:
                    atpd=at
                    
                try:
                    at_str=atpd.strftime('%Y-%m-%d')
                except:
                    at_str=atpd
                #ax.axvline(x=atpd,ls=":",c=color,linewidth=1.5,label=text_lang("关注点","Attention point ")+str(at))  
                ax.axvline(x=atpd,ls=":",c=color,linewidth=1.5,label=text_lang("关注点","Attention point ")+at_str)        

    if not attention_point_area=='':
        if isinstance(attention_point_area,list) and len(attention_point_area)>=2:
            apa_list=[]
            for ap in attention_point_area:
                try:
                    ap=datetime.strptime(ap, date_format)
                    appd=pd.to_datetime(ap)
                except:
                    appd=ap
                apa_list=apa_list+[appd]
                
            yaxis_data=plt.ylim()
            ax.fill_betweenx(yaxis_data,apa_list[0],apa_list[1],color='powderblue',alpha=0.5)

    #绘证券1：制趋势线
    if power > 0:
        lang=check_language()
        trend_txt='趋势线'
        if lang == 'English':
            trend_txt='Trend line'        
        
        #生成行号，借此将横轴的日期数量化，以便拟合
        df1['id']=range(len(df1))
        
        #设定多项式拟合，power为多项式次数
        import numpy as np
        parameter = np.polyfit(df1.id, df1[colname1], power)
        f = np.poly1d(parameter)

        if ticker1 == '':
            label1txt=''
        else:
            label1txt=ticker_name(ticker1,ticker_type_list[0])+"("+trend_txt+")"
        ax.plot(df1.index, f(df1.id),"r--", label=label1txt,linewidth=1)

    # 纵轴标签
    if ticker1 != ticker2:
        ax.set_ylabel(label1txt,fontsize=ylabel_txt_size)
    else:
        ax.set_ylabel(ectranslate(colname1),fontsize=ylabel_txt_size)
    #ax.legend(loc=loc1,fontsize=legend_txt_size)

    # 横轴标签
    #ax.set_xlabel(text_lang("日期","Date"),fontsize=xlabel_txt_size,ha='center')

    #绘图右图===================================================================
    #设置画布背景颜色
    ax2.set_facecolor(facecolor)

    # 折线标签
    if ticker2 == '':
        label2txt=label2
    else:
        if label2 == '':
            label2txt=ticker_name(ticker2,ticker_type_list[1])
        else:
            label2txt=ticker_name(ticker2,ticker_type_list[1])+'('+label2+')'   

    # 设置子图标题
    """
    if ticker1 != ticker2:
        ax2.set_title(label2txt,fontsize=xlabel_txt_size)
    else:
        ax2.set_title(ectranslate(colname2),fontsize=xlabel_txt_size)
    """
    # 绘图        
    lwadjust=linewidth_adjust(df2)
    """
    ax2.plot(df2.index,df2[colname2],'-',label=label2txt, \
             linestyle='-.',color=color2,linewidth=lwadjust)
    """  
    ax2.plot(df2.index,df2[colname2],'-', \
             linestyle='-.',color=color2,linewidth=lwadjust)

    #证券2：绘制数据标签
    if datatag2:
        for x, y in zip(df2.index, df2[colname2]):
            ax2.text(x,y+0.1,'%.2f' % y,ha='center',va='bottom',color='black')
    
    #绘证券2：制趋势线
    if power > 0:
        lang=check_language()
        trend_txt='趋势线'
        if lang == 'English':
            trend_txt='Trend line'           
        
        #生成行号，借此将横轴的日期数量化，以便拟合
        df2['id']=range(len(df2))
        
        #设定多项式拟合，power为多项式次数
        import numpy as np
        parameter = np.polyfit(df2.id, df2[colname2], power)
        f = np.poly1d(parameter)

        if ticker2 == '':
            label2txt=''
        else:
            label2txt=ticker_name(ticker2,ticker_type_list[1])+"("+trend_txt+")"
        ax2.plot(df2.index, f(df2.id),"c--", label=label2txt,linewidth=1)        
    
    # 纵轴标签
    if ticker1 != ticker2:
        ax2.set_ylabel(label2txt,fontsize=ylabel_txt_size)
    else:
        ax2.set_ylabel(ectranslate(colname2),fontsize=ylabel_txt_size)
    #ax2.legend(loc=loc2,fontsize=legend_txt_size)

    # 横轴标签
    #ax2.set_xlabel(text_lang("日期","Date"),fontsize=xlabel_txt_size,ha='center')
    
    #自动优化x轴标签
    #ax2.autofmt_xdate(ha="center") # 优化标注（自动倾斜）
    
    # 共同脚注==================================================================
    fig.text(0.5,-0.01,footnote,ha='center',fontsize=xlabel_txt_size,color='gray')
    #plt.xlabel(footnote,ha='center',fontsize=xlabel_txt_size,color='gray')
    
    # 自动倾斜横轴日期
    if not isinstance(maxticks,bool):    
        fig.autofmt_xdate(ha="center")
    
    # 调整布局防止重叠
    plt.tight_layout()        
    plt.show()
    
    return

#==============================================================================
def plot_line2_twinx2(df01,ticker1,colname1,label1, \
                      df02,ticker2,colname2,label2, \
                      titletxt,footnote,power=0,datatag1=False,datatag2=False, \
                          xline=999,attention_point_area='', \
                      resample_freq='D',loc1='upper left',loc2='lower left', \
                      date_range=False,date_freq=False,date_fmt='%Y-%m-%d', \
                      color1='red',color2='blue',facecolor='whitesmoke', \
                      ticker_type='auto', \
                          maxticks=15):
    """
    功能：绘制两个证券的折线图。如果power=0不绘制趋势图，否则绘制多项式趋势图
    假定：数据表有索引，且已经按照索引排序
    输入：
    证券1：数据表df1，证券代码ticker1，列名1，列名标签1；
    证券2：数据表df2，证券代码ticker2，列名2，列名标签2；
    标题titletxt，脚注footnote；是否在图中标记数据datatag；趋势图的多项式次数power
    输出：绘制双轴折线图
    返回值：无
    注意：需要日期类型作为df索引
    """
    import pandas as pd
    #plt.rcParams['axes.grid']=False

    #插值平滑
    if not isinstance(maxticks,bool):    
        try:
            df01x=df01[[colname1]].astype('float')
            df1=df_smooth_manual(df01x,resample_freq=resample_freq)
        except:
            df1=df01
        try:
            df02x=df02[[colname2]].astype('float')
            df2=df_smooth_manual(df02x,resample_freq=resample_freq)
        except:
            df2=df02
    else:
        df1=df01; df2=df02            

    #预处理ticker_type
    ticker_type_list=ticker_type_preprocess_mticker_mixed([ticker1,ticker2],ticker_type)
        
    #证券1：绘制折线图，双坐标轴
    fig = plt.figure()
    try:
        fig.gca().set_facecolor(facecolor)
    except:
        print("  #Warning(plot_line2_twinx2): color",facecolor,"is unsupported, changed to default setting")
        fig.gca().set_facecolor("whitesmoke") 
    
    ax = fig.add_subplot(111)

    if ticker1 == '':
        label1txt=label1
    else:
        if label1 == '':
            label1txt=ticker_name(ticker1,ticker_type_list[0])
        else:
            label1txt=ticker_name(ticker1,ticker_type_list[0])+'('+label1+')'    
        
    date_start=df1.index[0]
    date_end=df1.index[-1]
    
    if date_range and not date_freq:
        ax.xaxis.set_major_formatter(mdate.DateFormatter(date_fmt))
        plt.xticks(pd.date_range(date_start,date_end))
    if not date_range and date_freq:
        ax.xaxis.set_major_formatter(mdate.DateFormatter(date_fmt))
        plt.xticks(pd.date_range(freq=date_freq))
    if date_range and date_freq:
        ax.xaxis.set_major_formatter(mdate.DateFormatter(date_fmt))
        plt.xticks(pd.date_range(date_start,date_end,freq=date_freq))    
    
    lwadjust=linewidth_adjust(df1)        
    ax.plot(df1.index,df1[colname1],'-',label=label1txt, \
             linestyle='-',color=color1,linewidth=lwadjust)   
    #证券1：绘制数据标签
    if datatag1:
        for x, y in zip(df1.index, df1[colname1]):
            ax.text(x,y+0.1,'%.2f' % y,ha='center',va='bottom',color='black')

    #绘制关注点
    import pandas as pd
    from datetime import datetime; date_format="%Y-%m-%d"
    if xline != 999:
        attention_point=xline
        
        #用于关注点的颜色列表
        atp_color_list=["crimson","dodgerblue","magenta","lightseagreen","chocolate"]  
        
        if isinstance(attention_point,str) or isinstance(attention_point,int) or isinstance(attention_point,float):
            atp_list=[attention_point]
        elif isinstance(attention_point,list):
            atp_list=attention_point
        else:
            atp_list=[]
        #去重，不打乱原来的顺序
        atp_list=list(dict.fromkeys(atp_list))

        if DEBUG:
            print("In plot_line2_twinx")
            print("atp_list=",atp_list)
            
        if not atp_list==[] and not atp_list==['']:
            
            for at in atp_list:
                pos=atp_list.index(at)
                color=atp_color_list[pos]
                
                #判断是否日期字符串
                try:
                    at=datetime.strptime(at, date_format)
                    atpd=pd.to_datetime(at)
                except:
                    atpd=at
                    
                try:
                    at_str=atpd.strftime('%Y-%m-%d')
                except:
                    at_str=atpd
                #plt.axvline(x=atpd,ls=":",c=color,linewidth=1.5,label=text_lang("关注点","Attention point ")+str(at))    
                plt.axvline(x=atpd,ls=":",c=color,linewidth=1.5,label=text_lang("关注点","Attention point ")+at_str)        

    if not attention_point_area=='':
        if isinstance(attention_point_area,list) and len(attention_point_area)>=2:
            apa_list=[]
            for ap in attention_point_area:
                try:
                    ap=datetime.strptime(ap, date_format)
                    appd=pd.to_datetime(ap)
                except:
                    appd=ap
                apa_list=apa_list+[appd]
                
            yaxis_data=plt.ylim()
            plt.fill_betweenx(yaxis_data,apa_list[0],apa_list[1],color='powderblue',alpha=0.5)


    #绘证券1：制趋势线
    if power > 0:
        lang=check_language()
        trend_txt='趋势线'
        if lang == 'English':
            trend_txt='Trend line'           
        
        #生成行号，借此将横轴的日期数量化，以便拟合
        df1['id']=range(len(df1))
        
        #设定多项式拟合，power为多项式次数
        import numpy as np
        parameter = np.polyfit(df1.id, df1[colname1], power)
        f = np.poly1d(parameter)

        if ticker1 == '':
            label1txt=''
        else:
            label1txt=ticker_name(ticker1,ticker_type_list[0])+"("+trend_txt+")"
        ax.plot(df1.index, f(df1.id),"r--", label=label1txt,linewidth=1)
        
    ax.set_xlabel(footnote,fontsize=xlabel_txt_size,ha='center')
    
    if ticker1 == '':
        label1txt=label1
    else:
        if label1 == "":
            label1txt=ticker_name(ticker1,ticker_type_list[0])
        else:
            label1txt=label1+'('+ticker_name(ticker1,ticker_type_list[0])+')'
    ax.set_ylabel(label1txt,fontsize=ylabel_txt_size)
    ax.legend(loc=loc1,fontsize=legend_txt_size)

    #绘证券2：建立第二y轴
    ax2 = ax.twinx()
    
    if ticker2 == '':
        label2txt=label2
    else:
        if label2 == '':
            label2txt=ticker_name(ticker2,ticker_type_list[1])
        else:
            label2txt=ticker_name(ticker2,ticker_type_list[1])+'('+label2+')'    
        
    date_start=df2.index[0]
    date_end=df2.index[-1]
    if date_range and not date_freq:
        ax2.xaxis.set_major_formatter(mdate.DateFormatter(date_fmt))
        plt.xticks(pd.date_range(date_start,date_end))
    if not date_range and date_freq:
        ax2.xaxis.set_major_formatter(mdate.DateFormatter(date_fmt))
        plt.xticks(pd.date_range(freq=date_freq))
    if date_range and date_freq:
        ax2.xaxis.set_major_formatter(mdate.DateFormatter(date_fmt))
        plt.xticks(pd.date_range(date_start,date_end,freq=date_freq))        
    
    lwadjust=linewidth_adjust(df2)        
    ax2.plot(df2.index,df2[colname2],'-',label=label2txt, \
             linestyle='-.',color=color2,linewidth=lwadjust)
    #证券2：绘制数据标签
    if datatag2:
        for x, y in zip(df2.index, df2[colname2]):
            ax2.text(x,y+0.1,'%.2f' % y,ha='center',va='bottom',color='black')
    
    #绘证券2：制趋势线
    if power > 0:
        lang=check_language()
        trend_txt='趋势线'
        if lang == 'English':
            trend_txt='Trend line'           
        
        #生成行号，借此将横轴的日期数量化，以便拟合
        df2['id']=range(len(df2))
        
        #设定多项式拟合，power为多项式次数
        import numpy as np
        parameter = np.polyfit(df2.id, df2[colname2], power)
        f = np.poly1d(parameter)

        if ticker2 == '':
            label2txt=''
        else:
            label2txt=ticker_name(ticker2,ticker_type_list[1])+"("+trend_txt+")"
        
        ax2.plot(df2.index, f(df2.id),"c--", label=label2txt,linewidth=1)        
    
    if ticker2 == '':
        label2txt=label2
    else:
        if label2 == "":
            label2txt=ticker_name(ticker2,ticker_type_list[1])
        else:
            label2txt=label2+'('+ticker_name(ticker2,ticker_type_list[1])+')'
    ax2.set_ylabel(label2txt,fontsize=ylabel_txt_size)
    ax2.legend(loc=loc2,fontsize=legend_txt_size)

    # 使用 AutoDateLocator 自动选择最佳间隔，目的是显示最后一个日期，亲测有效！！！
    import matplotlib.dates as mdates
    ax.xaxis.set_major_locator(mdates.AutoDateLocator(maxticks=maxticks))
    ax2.xaxis.set_major_locator(mdates.AutoDateLocator(maxticks=maxticks))
    
    #自动优化x轴标签
    #格式化时间轴标注
    #plt.gca().xaxis.set_major_formatter(mdate.DateFormatter('%y-%m-%d')) 
    if not isinstance(maxticks,bool):    
        plt.gcf().autofmt_xdate(ha="center") # 优化标注（自动倾斜）
        
    plt.title(titletxt,fontweight='bold',fontsize=title_txt_size)
    plt.show()
    
    return

#==============================================================================
if __name__ =="__main__":
    df0=security_trend(['PDD','JD'],annotate=True,graph=False)
    
    y_label=''; x_label='Footnote'
    axhline_value=0; axhline_label=''
    title_txt='Title'
    data_label=False
    resample_freq='D'; smooth=True
    linewidth=1.5
    loc='best'
    annotate=True; annotate_value=True
    plus_sign=False
    attention_value=''; attention_value_area=''
    attention_point=''; attention_point_area=''
    mark_top=False; mark_bottom=False; mark_end=False
    ticker_type='auto'
    facecolor='whitesmoke'


def draw_lines(df0,y_label,x_label,axhline_value,axhline_label,title_txt, \
               data_label=False,resample_freq='D',smooth=False, \
                   linewidth=1.5, \
               band_area='',loc='best', \
                   annotate=False,annotate_value=False,plus_sign=False, \
                attention_value='',attention_value_area='', \
                attention_point='',attention_point_area='', \
               mark_start=False,mark_top=False,mark_bottom=False,mark_end=False, \
               ticker_type='auto',facecolor='whitesmoke', \
                   maxticks_enable=True,maxticks=15, \
               translate=False, \
                   precision=2,power=0, \
                bold_column = ''):
    """
    函数功能：根据df的内容绘制折线图
    输入参数：
    df：数据框。有几个字段就绘制几条折现。必须索引，索引值将作为X轴标记点
    要求：df的索引为pandas的datetime日期型
    axhline_label: 水平辅助线标记。如果为空值则不绘制水平辅助线
    axhline_value: 水平辅助线的y轴位置
    y_label：y轴标记
    x_label：x轴标记
    title_txt：标题。如需多行，中间用\n分割
    
    输出：
    绘制折线图
    无返回数据
    注意：需要日期类型作为df索引
    """
    DEBUG=False
    if DEBUG:
        print(f"band_area={band_area}")
        print(f"df0={df0}")

    
    if DEBUG:
        print("annotate=",annotate,"annotate_value=",annotate_value)
        print("mark_top=",mark_top,"mark_bottom=",mark_bottom)
        print(df0)
    
    #空值判断
    if len(df0) ==0:
        print ("  #Warning(draw_lines): no data to plot.")
        return
    
    #插值平滑
    if smooth and not isinstance(maxticks,bool):
        #print("  Rendering graphics ...")
        try:
            df=df_smooth_manual(df0,resample_freq=resample_freq)
        except:
            df=df0
    else:
        df=df0
        
    #取得df字段名列表
    collist=df.columns.values.tolist()  
    if len(collist) > 16:
        print ("  #Warning(draw_lines): too many columns to draw lines, max 16 lines")
        return
    
    lslist=['-','--','-.',':','-','--','-.',':','-','--','-.',':','-','--','-.',':',]
    #mklist=[',','d','_','.','o','v','^','<','>','1','2','3','4','s','p','*','h','H','+','x','D']
    mklist=[',',',',',',',',',',',',',',',',',',',',',',',',',',',',',',',',',',',',',',',',',']
    
    # 所有字段转换为数值类型，以防万一
    for c in collist:
        try:
            df[c]=df[c].astype('float')
        except:
            del df[c]
    
    # 计算所有列中的最大最小差距，所有列必须为数值型！
    dfmax=df.max().max(); dfmin=df.min().min()
    high_low=dfmax - dfmin
    
    # 将末端值最大的排在第一列，优先绘图
    dftt=df.T
    lastrow=list(dftt)[-1]
    dftt.sort_values(lastrow,ascending=False,inplace=True)
    df2=dftt.T
    
    # 最上层线标志
    firstline=True
    
    #绘制折线图
    ax=plt.gca()
    print('')
    y_end_list=[]    
    for c in collist:
        pos=collist.index(c)
        try:
            lsc=lslist[pos]
        except:
            print("  #Bug(draw_lines): lslist=",lslist,",pos=",pos)
        mkc=mklist[pos]
        
        # 连接折线中非交易日的断开区间
        import pandas as pd
        dfg=pd.DataFrame(df2[c]).copy(deep=True)
        
        # 慎用dropna
        #dfg=dfg.dropna(inplace=True)
        if dfg is None:
            print("  #Error(draw_lines): null dataframe for graphics in column",c)
            continue
        if len(dfg)==0:
            print("  #Error(draw_lines): no data for graphics in column",c)
            continue
        
        #plt.plot(dfg,label=c,linewidth=linewidth,ls=lsc,marker=mkc,markersize=3)
        lwadjust=linewidth_adjust(dfg)
        
        """
        if not annotate:
            
            #注意：许多传入的df字段名已经不是证券代码，此处调用codetranslate将会导致
            #股票名称字典重新下载，耗费时间，且出现黄条。
            #建议：在调用draw_lines之前，先调用codetranslate，将证券代码翻译为证券名称。
            #本函数仅负责绘图，不负责翻译证券名称。
            
            #plt.plot(dfg,label=codetranslate(c),linewidth=linewidth,ls=lsc,marker=mkc,markersize=3)
            plt.plot(dfg,label=c,linewidth=lwadjust,ls=lsc,marker=mkc,markersize=3)
        else:
            #plt.plot(dfg[c],label=codetranslate(c),linewidth=linewidth,ls=lsc,marker=mkc,markersize=3)
            #plt.plot(dfg,label=codetranslate(c),linewidth=linewidth,ls=lsc,marker=mkc,markersize=3)
            plt.plot(dfg,label=c,linewidth=lwadjust,ls=lsc,marker=mkc,markersize=3)
        """  
        if not annotate or c in ["平均值","中位数"]:
            if c in ["平均值","中位数"]:
                clabel=c+str(round(dfg[c].values[0],2))
            else:
                clabel=c
                
            if (c != bold_column):
                plt.plot(dfg,label=auto_translate2(clabel,translate),linewidth=lwadjust,ls=lsc,marker=mkc,markersize=3)
            else:
                plt.plot(dfg,label=auto_translate2(clabel,translate),linewidth=lwadjust*2,ls=lsc,marker=mkc,markersize=3)
        else:
            if (c != bold_column):
                plt.plot(dfg,linewidth=lwadjust,ls=lsc,marker=mkc,markersize=3)
            else:
                plt.plot(dfg,linewidth=lwadjust*2,ls=lsc,marker=mkc,markersize=3)
            
        lines = plt.gca().lines
        last_line_color = lines[-1].get_color()
        
        if annotate and (c not in ["平均值","中位数"]):
            mark_end=False
            df_end=dfg.tail(1)
            # df_end[c]必须为数值类型，否则可能出错
            if DEBUG:
                print(f"=== c: {type(c)}, {c}")
                print(f"=== df_end[c]: {type(df_end[c])}, {df_end[c]}")
            
            y_end = df_end[c].min()    # 末端的y坐标
            if not isinstance(y_end,float):
                # 需要强制提取数值，因其可能为Series类型
                print(f"=== y_end: {type(y_end)}, {y_end}")
                y_end = y_end.iloc[0]
                
            x_end = df_end[c].idxmin() # 末端值的x坐标 
            #import pandas as pd; import datetime
            if isinstance(x_end, pd.Series):
                # 需要强制提取数值，因其可能为Series类型
                if DEBUG:
                    print(f"=== x_end: {type(x_end)}, {x_end}")
                    
                x_end = x_end.iloc[0]
            
            if annotate_value: #在标记曲线名称的同时标记其末端数值
                #y1=str(int(y_end)) if y_end >= 100 else str(round(y_end,2))
                y1=str(round(y_end,2)) if abs(y_end) >= 100 else str(round(y_end,precision)) if abs(y_end) >= 1 else str(round(y_end,precision))
                plt.annotate(text=' '+auto_translate2(c,translate)+': '+y1, 
                             xy=(x_end, y_end),
                             xytext=(x_end, y_end),fontsize=annotate_size,
                             color=last_line_color)
            else:
                plt.annotate(text=' '+auto_translate2(c,translate), 
                             xy=(x_end, y_end),
                            #xytext=(x_end, y_end),fontsize=9)
                             xytext=(x_end, y_end),fontsize=annotate_size,
                             color=last_line_color)
                
        #plt.plot(df[c],label=c,linewidth=1.5,marker=mkc,markersize=3)
        #为折线加数据标签
        if data_label==True:
            mark_top=False; mark_bottom=False; mark_end=False
            for a,b in zip(dfg.index,df2[c]):
                plt.text(a,b+0.02,str(round(b,2)), \
                         ha='center',va='bottom',fontsize=7)

        #标记最高点/最低点
        if (mark_top or mark_bottom) and (c not in ["平均值","中位数"]):
            df_mark=dfg[[c]].copy() #避免影响原df
            df_mark.dropna(inplace=True)
            df_mark.sort_values(by=c,ascending=False,inplace=True)
            
            if mark_top:
                df_mark_top=df_mark[:1]
                for x, y in zip(df_mark_top.index, df_mark_top[c]):
                    #y1=round(y+high_low*0.01,2)
                    y1=y+high_low*0.01
                    #s='%.0f' if y >= 100 else '%.2f'
                    s='%.1f' if abs(y) >= 100 else '%.2f' if abs(y) >= 1 else '%.4f'
                    #plt.text(x,y1,s % y,ha='center',va='bottom',color='red')
                    plt.text(x,y1,s % y,ha='right',va='bottom',color=last_line_color)
                    plt.scatter(x,y, color='red',marker='8',s=70)
                
            if mark_bottom:
                df_mark_bottom=df_mark[-1:]
                for x, y in zip(df_mark_bottom.index, df_mark_bottom[c]):
                    #y1=round(y-high_low*0.055,2) #标记位置对应y1的底部
                    y1=y-high_low*0.050 #标记位置对应y1的底部
                    #s='%.0f' if y >= 100 else '%.2f'
                    s='%.1f' if abs(y) >= 100 else '%.2f' if abs(y) >= 1 else '%.4f'
                    #plt.text(x,y1,s % y,ha='center',va='bottom',color='seagreen')
                    plt.text(x,y1,s % y,ha='right',va='bottom',color=last_line_color)
                    plt.scatter(x,y, color='seagreen',marker='8',s=70)

        #标记曲线开始数值
        if mark_start and (c not in ["平均值","中位数"]):
            df_end=dfg.head(1)
            y_end = df_end[c].min()    # 开始的y坐标
            x_end = df_end[c].idxmin() # 开始值的x坐标 
            
            #y1=str(int(y_end)) if y_end >= 100 else str(round(y_end,2))
            y1=str(round(y_end,1)) if abs(y_end) >= 100 else str(round(y_end,precision)) if abs(y_end) >= 1 else str(round(y_end,precision))
            plt.annotate(text=' '+y1, 
                         xy=(x_end, y_end),
                         xytext=(x_end, y_end*0.998),fontsize=annotate_size,
                         color=last_line_color,ha='right',va='center')

        #标记曲线末端数值
        if mark_end and (c not in ["平均值","中位数"]):
            df_end=dfg.tail(1)
            y_end = df_end[c].min()    # 末端的y坐标
            x_end = df_end[c].idxmin() # 末端值的x坐标 
            
            #y1=str(int(y_end)) if y_end >= 100 else str(round(y_end,2))
            y1=str(round(y_end,1)) if abs(y_end) >= 100 else str(round(y_end,precision)) if abs(y_end) >= 1 else str(round(y_end,precision))
            plt.annotate(text=' '+y1, 
                         xy=(x_end, y_end),
                         xytext=(x_end, y_end*0.998),fontsize=annotate_size,
                         color=last_line_color,ha='left',va='center')
            
        #绘制趋势线
        if (power > 0) and (len(list(dfg)) == 1):
            trend_txt=text_lang('趋势线','Trend line')
            if power > 100: power=100
            
            try:
                #生成行号，借此将横轴的日期数量化，以便拟合
                dfg['id']=range(len(dfg))
            
                #设定多项式拟合，power为多项式次数
                """
                import numpy as np
                parameter = np.polyfit(dfg.id, dfg[list(dfg)[0]], power)
                f = np.poly1d(parameter)
                plt.plot(dfg.index, f(dfg.id),"r--", label=trend_txt,linewidth=1)
                """
                from numpy.polynomial import Polynomial
                x = dfg['id']
                y = dfg[list(dfg)[0]]
                p = Polynomial.fit(x, y, deg=power)
                plt.plot(dfg.index, p(x), "r--", label=trend_txt, linewidth=1)

            except Exception as e:
                print(f"  #Warning(draw_lines): Polynomial.fit failed — {e}")

            """
            except: 
                print(f"  #Warning(draw_lines): failed to converge trend line, try a smaller power.")        
            """
            
    #用于关注值的颜色列表
    atv_color_list=["lightgray","paleturquoise","wheat","khaki","lightsage","hotpink","mediumslateblue"]
    #用于关注点的颜色列表
    atp_color_list=["crimson","dodgerblue","magenta","lightseagreen","chocolate","hotpink","mediumslateblue"]

    if not attention_value=='':
        if isinstance(attention_value,int) or isinstance(attention_value,float):
            atv_list=[attention_value]
        elif isinstance(attention_value,list):
            atv_list=attention_value
        else:
            atv_list=[]
        if not atv_list==[] and not atv_list==['']:
            for at in atv_list:
                pos=atv_list.index(at)
                color=atv_color_list[pos]
                plt.axhline(y=at,ls=":",c=color,linewidth=2,label=text_lang("关注值","Attention value ")+str(at))

    if not attention_value_area=='':
        if isinstance(attention_value_area,list) and len(attention_value_area)>=2:
            plt.fill_between(dfg.index,attention_value_area[0],attention_value_area[1],color='lightgray',alpha=0.5)

    #绘制曲线之间的带状区域
    if DEBUG:
        print(f"dfg={dfg}")
        
    if band_area != '' and isinstance(band_area,list) and len(band_area)>=2:
        upper_line=band_area[0]; lower_line=band_area[1]
        if upper_line not in collist:
            upper_line=ectranslate(upper_line)
            lower_line=ectranslate(lower_line)
            
            if upper_line not in collist:
                upper_line=ticker_name(upper_line)
                lower_line=ticker_name(lower_line)
                
                if upper_line not in collist:
                    upper_line=None
                    lower_line=None
                
        if not (upper_line is None) and not (lower_line is None):
            try:
                plt.fill_between(df2.index,df2[upper_line],df2[lower_line],df2[upper_line] > df2[lower_line],color='aquamarine',alpha=0.5,label='',interpolate=True)
                plt.fill_between(df2.index,df2[upper_line],df2[lower_line],df2[upper_line] < df2[lower_line],color='lightcoral',alpha=0.5,label='',interpolate=True)
            except:
                print(f"  #Warning(draw_lines): band area elements {upper_line} or {lower_line} not found")
                
    import pandas as pd  
    from datetime import datetime; date_format="%Y-%m-%d"
    from datetime import datetime; date_format="%Y-%m-%d"      
    if not attention_point=='':
        if isinstance(attention_point,str) or isinstance(attention_point,int) or isinstance(attention_point,float):
            atp_list=[attention_point]
        elif isinstance(attention_point,list):
            atp_list=attention_point
        else:
            atp_list=[]
        #去重，不打乱原来的顺序
        atp_list=list(dict.fromkeys(atp_list))
            
        if not atp_list==[] and not atp_list==['']:
            
            for at in atp_list:
                try:
                    pos=atp_list.index(at)
                    color=atp_color_list[pos]
                except:
                    print("*** in draw_lines:")
                    print("atp_list={0},at={1},pos={2}".format(atp_list,at,pos))
                    print("atp_color_list={0}".format(atp_color_list))
                    
                    color=atp_color_list[-1]
                
                try:
                    #判断是否日期字符串
                    at=datetime.strptime(at, date_format)
                    #若是日期字符串
                    atpd=pd.to_datetime(at)
                except:
                    #不是日期字符串
                    atpd=at
                
                """
                #纵轴最小值                    
                yaxis_min=plt.ylim()[0]
                arrow_dx=0
                #各曲线在关注点的最大值
                point_max=dfg.loc[atpd].max()
                arrow_dy=point_max - yaxis_min
                
                if DEBUG:
                    print("*** In draw_lines:")
                    print("dfg.loc[atpd]",dfg.loc[atpd].values)
                    print("yaxis_min=",yaxis_min)
                    print("point_max=",point_max)
                    print("arrow_dy=",arrow_dy)

                plt.arrow(atpd,yaxis_min,arrow_dx,arrow_dy,ls=':',lw=2,fc=color,ec=color,alpha=0.5,shape='full', \
                          width=0.05,length_includes_head=True)
                """
                    
                try:
                    at_str=atpd.strftime('%Y-%m-%d')
                except:
                    at_str=atpd
                #plt.axvline(x=atpd,ls=":",c=color,linewidth=1.5,label=text_lang("关注点","Attention point ")+str(at))
                plt.axvline(x=atpd,ls=":",c=color,linewidth=1.5,label=text_lang("关注点","Attention point ")+at_str)

    if not attention_point_area=='':
        if isinstance(attention_point_area,list) and len(attention_point_area)>=2:
            apa_list=[]
            for ap in attention_point_area:
                try:
                    ap=datetime.strptime(ap, date_format)
                    appd=pd.to_datetime(ap)
                except:
                    appd=ap
                apa_list=apa_list+[appd]
                
            yaxis_data=plt.ylim()
            plt.fill_betweenx(yaxis_data,apa_list[0],apa_list[1],color='powderblue',alpha=0.5)
                
    #绘制水平辅助线
    if axhline_label !="":
        if '零线' in axhline_label:
            axhline_label=''
            
        max_values = df2.max(numeric_only=True); global_max_values=max_values.max()
        min_values = df2.min(numeric_only=True); global_min_values=min_values.min()
        if global_max_values >= axhline_value and global_min_values <= axhline_value:
            plt.axhline(y=axhline_value,label=auto_translate2(axhline_label,translate),color='black',linestyle=':',linewidth=2)  
        #plt.axhline(y=axhline_value,color='purple',linestyle=':',linewidth=1.5)
    
    #坐标轴标记
    y_label_t=ectranslate(y_label)
    plt.ylabel(auto_translate2(y_label_t,translate),fontweight='bold',fontsize=ylabel_txt_size)
    
    x_label_t=ectranslate(x_label)
    if x_label != "":
        plt.xlabel(auto_translate2(x_label_t,translate),fontweight='bold',fontsize=xlabel_txt_size,ha='center')
    #图示标题
    plt.title(auto_translate2(title_txt,translate),fontweight='bold',fontsize=title_txt_size)
    
    if not isinstance(maxticks,bool):    
        if maxticks_enable:
            # 使用 AutoDateLocator 自动选择最佳间隔，目的是显示最后一个日期，亲测有效！！！
            import matplotlib.dates as mdates
            ax.xaxis.set_major_locator(mdates.AutoDateLocator(maxticks=maxticks))   
    
        plt.gcf().autofmt_xdate(ha="center") # 优化标注（自动倾斜）
    try:
        plt.gca().set_facecolor(facecolor)
    except:
        print("  #Warning(draw_lines): color",facecolor,"is unsupported, changed to default setting")
        plt.gca().set_facecolor("whitesmoke") 
        
    # 若不绘制annotate，则绘制图例
    #if not annotate:
    #检查是否存在可绘制的标签，若有则绘制
    if DEBUG:
        have_label=False
        for line in plt.gca().lines:
            print(f"  DEBUG: plt.gca().lines, line={line.get_label()}")
            if line.get_label() != '':
                have_label=True
    
    #plt.legend没有图例标签时会提示信息No artists...
    if not annotate or attention_value !='' or attention_point !='':
        plt.legend(loc=loc,fontsize=legend_txt_size)
        
    """
    if any([line.get_label() != '' for line in plt.gca().lines]):
        tuli=plt.legend(loc=loc,fontsize=legend_txt_size)
        if DEBUG:
            print(f"  DEBUG: result of plt.legend is {tuli}")
    """
    if plus_sign:
        # 尝试改变纵轴刻度格式：给正数添加正号+，以便突出显示增减幅度
        import matplotlib.ticker as ticker
        ax = plt.gca()
        bare0 = lambda y, pos: ('%+g' if y>0 else '%g')%y
        #bare0 = lambda y, pos: ('%+g％' if y>0 else '%g％')%y #此处％为全角，无法适配英文环境，放弃！
        ax.yaxis.set_major_formatter(ticker.FuncFormatter(bare0))
    
    plt.show()
    
    return    
    
if __name__=='__main__':
    title_txt="Stock Risk \nCAPM Beta Trends"
    draw_lines(df,"market line",1.0,"Beta coefficient","",title_txt)    

#==============================================================================
def draw_lines2(df0,y_label,x_label,axhline_value,axhline_label,title_txt, \
                data_label=False,resample_freq='1D',smooth=True, \
                date_range=False,date_freq=False,date_fmt='%Y-%m-%d', \
                colorlist=[],lslist=[],lwlist=[], \
                #指定纵轴两个变量之间的区域
                band_area='',loc='best', \
                    attention_value='', \
                    #指定纵轴两个数值之间的区域
                    attention_value_area='', \
                    attention_point='', \
                    #指定两个横轴之间的区域
                    attention_point_area='', \
                annotate=False,annotate_value=False, \
                mark_start=False,mark_top=False,mark_bottom=False,mark_end=False, \
                facecolor='whitesmoke',maxticks=20,translate=False):
    """
    函数功能：根据df的内容绘制折线图
    输入参数：
    df：数据框。有几个字段就绘制几条折现。必须索引，索引值将作为X轴标记点
    要求：df的索引为pandas的datetime日期型
    axhline_label: 水平辅助线标记。如果为空值则不绘制水平辅助线
    axhline_value: 水平辅助线的y轴位置
    y_label：y轴标记
    x_label：x轴标记
    title_txt：标题。如需多行，中间用\n分割
    
    smooth=True：默认进行曲线平滑处理，对于部分长期停牌的股票/债券，应选择不进行平滑处理False，否则曲线会严重失真。
    
    输出：
    绘制折线图
    无返回数据
    注意：需要日期类型作为df索引
    
    band_area=''：默认为空，否则为列表，第1个值为带状区域上边沿字段，第2个值为带状区域下边沿字段
    """
    import pandas as pd
    
    DEBUG=False
    if DEBUG:
        print(f"band_area={band_area}")
        print(f"df0={df0}")
    
    #空值判断
    if len(df0) ==0:
        print ("  #Warning(draw_lines): no data to plot.")
        return
    
    #插值平滑
    if smooth and not isinstance(maxticks,bool):
        print("  Smoothening curves ...")
        try:
            df=df_smooth_manual(df0,resample_freq=resample_freq)
        except:
            df=df0
    else:
        df=df0

    # 所有字段转换为数值类型，以防万一
    for c in list(df):
        try:
            df[c]=df[c].astype('float')
        except:
            del df[c]

   # 计算所有列中的最大最小差距，假设所有列均为数值型！
    dfmax=df.max().max(); dfmin=df.min().min()
    high_low=dfmax - dfmin

    #定义横轴标签：显示完整开始、结束日期
    if not isinstance(maxticks,bool):    
        ax=plt.gca()    
        date_start=df.index[0]
        date_end=df.index[-1]
        if date_range and not date_freq:
            ax.xaxis.set_major_formatter(mdate.DateFormatter(date_fmt))
            plt.xticks(pd.date_range(date_start,date_end))
        if not date_range and date_freq:
            ax.xaxis.set_major_formatter(mdate.DateFormatter(date_fmt))
            plt.xticks(pd.date_range(freq=date_freq))
        if date_range and date_freq:
            ax.xaxis.set_major_formatter(mdate.DateFormatter(date_fmt))
            plt.xticks(pd.date_range(date_start,date_end,freq=date_freq))    
        
    #取得df字段名列表
    collist=df.columns.values.tolist()  
    collist3=collist[:3] #专用于绘制布林带，取前3个字段
    
    if lslist==[]:
        lslist=['-','--','-.',':','-','--','-.',':','-','--','-.',':','-','--','-.',':',]
    if colorlist==[]:
        colorlist=['blue','tomato','green','chocolate','darksage','cyan','blueviolet','violet','darkcyan','gold','wheat','silver','darkred','brown','coral','pink',]

    print('')        
    #绘制折线图    
    for c in collist:
        pos=collist.index(c)
        try:
            lcolor=colorlist[pos]
        except:
            lcolor=''
        try:
            lls=lslist[pos]
        except:
            lls=''
        try:
            llw=lwlist[pos]
        except:
            llw=linewidth_adjust(df)
        
        if (lcolor !='') and (lls !=''):
            if not annotate:
                plt.plot(df[c],label=auto_translate2(c,translate),linewidth=llw,ls=lls,color=lcolor)
            else:
                plt.plot(df[c],linewidth=llw,ls=lls,color=lcolor)
        elif (lcolor !=''):
            if not annotate:
                plt.plot(df[c],label=auto_translate2(c,translate),linewidth=llw,color=lcolor)
            else:
                plt.plot(df[c],linewidth=llw,color=lcolor)
        else:
            if not annotate:
                plt.plot(df[c],label=auto_translate2(c,translate),linewidth=llw)
            else:
                plt.plot(df[c],linewidth=llw)
            
        lines = plt.gca().lines; last_line_color = lines[-1].get_color()
        
        #为折线加数据标签
        if data_label==True:
            mark_top=False; mark_bottom=False; mark_end=False
            for a,b in zip(df.index,df[c]):
                plt.text(a,b+0.02,str(round(b,2)), \
                         ha='center',va='bottom',fontsize=7)

        #标记最高点/最低点
        if mark_top or mark_bottom:
            df_mark=df[[c]].copy() #避免影响原df
            df_mark.dropna(inplace=True)
            df_mark.sort_values(by=c,ascending=False,inplace=True)
            
            if mark_top:
                df_mark_top=df_mark[:1]
                for x, y in zip(df_mark_top.index, df_mark_top[c]):
                    #y1=round(y+high_low*0.01,2)
                    y1=y+high_low*0.01
                    #s='%.0f' if y >= 100 else '%.2f'
                    s='%.1f' if abs(y) >= 100 else '%.2f' if abs(y) >= 1 else '%.4f'
                    #plt.text(x,y1,s % y,ha='center',va='bottom',color='red')
                    plt.text(x,y1,s % y,ha='right',va='bottom',color=last_line_color)
                    plt.scatter(x,y, color='red',marker='8',s=70)
                
            if mark_bottom:
                df_mark_bottom=df_mark[-1:]
                for x, y in zip(df_mark_bottom.index, df_mark_bottom[c]):
                    #y1=round(y-high_low*0.055,2) #标记位置对应y1的底部
                    y1=y-high_low*0.050 #标记位置对应y1的底部
                    #s='%.0f' if y >= 100 else '%.2f'
                    s='%.1f' if abs(y) >= 100 else '%.2f' if abs(y) >= 1 else '%.4f'
                    #plt.text(x,y1,s % y,ha='center',va='bottom',color='seagreen')
                    plt.text(x,y1,s % y,ha='right',va='bottom',color=last_line_color)
                    plt.scatter(x,y, color='seagreen',marker='8',s=70)
    
        #曲线末端标记：不建议用于布林带
        if annotate:
            df_end=df.tail(1)
            y_end = df_end[c].min()    # 末端的y坐标
            x_end = df_end[c].idxmin() # 末端值的x坐标 
            
            if annotate_value: #在标记曲线名称的同时标记其末端数值
                #y1=str(int(y_end)) if y_end >= 100 else str(round(y_end,2))
                y1=str(int(y_end)) if abs(y_end) >= 100 else str(round(y_end,2)) if abs(y_end) >= 10 else str(round(y_end,4))
                plt.annotate(text=auto_translate2(c,translate)+': '+y1, 
                             xy=(x_end, y_end),
                             xytext=(x_end, y_end),fontsize=annotate_size,
                             color=last_line_color)
            else:
                plt.annotate(text=auto_translate2(c,translate), 
                             xy=(x_end, y_end),
                             xytext=(x_end, y_end),fontsize=annotate_size,
                             color=last_line_color)

        #标记曲线开始数值
        if mark_start:
            df_start=df.head(1)
            y_start = df_start[c].min()    # 开始的y坐标
            x_start = df_start[c].idxmin() # 开始值的x坐标 
            
            #y1=str(int(y_end)) if y_end >= 100 else str(round(y_end,2))
            y1=str(round(y_start,1)) if abs(y_start) >= 100 else str(round(y_start,2)) if abs(y_start) >= 1 else str(round(y_start,3)) 
            plt.annotate(text=y1, 
                         xy=(x_start, y_start),
                         xytext=(x_start, y_start*0.998),fontsize=annotate_size,ha='right',va='center')
            # 特别注意：这里的left/right与实际图示的方向正好相反！！！
    
        #处理布林带的mark_end，仅标记上中下线
        if mark_end & (c in collist3):
            df_end=df.tail(1)
            y_end = df_end[c].min()    # 末端的y坐标
            x_end = df_end[c].idxmin() # 末端值的x坐标 
            
            #y1=str(int(y_end)) if y_end >= 100 else str(round(y_end,2))
            y1=str(round(y_end,1)) if abs(y_end) >= 100 else str(round(y_end,2)) if abs(y_end) >= 1 else str(round(y_end,3))
            plt.annotate(text=y1, 
                         xy=(x_end, y_end),
                         xytext=(x_end, y_end),fontsize=annotate_size,
                         color=last_line_color)
        
    #绘制带状区域
    if band_area != '' and isinstance(band_area,list) and len(band_area)>=2:
        upper_line=band_area[0]; lower_line=band_area[1]
        if upper_line not in collist:
            upper_line=ectranslate(upper_line)
            lower_line=ectranslate(lower_line)
            
            if upper_line not in collist:
                upper_line=ticker_name(upper_line)
                lower_line=ticker_name(lower_line)
                
                if upper_line not in collist:
                    upper_line=None
                    lower_line=None
                
        if not (upper_line is None) and not (lower_line is None):
            try:
                """
                plt.fill_between(df.index,df[upper_line],df[lower_line],color='moccasin',alpha=0.5,label='',where=df[upper_line]>=df[lower_line])
                plt.fill_between(df.index,df[upper_line],df[lower_line],color='aquamarine',alpha=0.5,label='',where=df[upper_line]<=df[lower_line])
                """
                #plt.fill_between(df.index,df[upper_line],df[lower_line],color='aquamarine',alpha=0.5,label='')
                plt.fill_between(df.index,df[upper_line],df[lower_line],df[upper_line] > df[lower_line],color='aquamarine',alpha=0.5,label='',interpolate=True)
                plt.fill_between(df.index,df[upper_line],df[lower_line],df[upper_line] < df[lower_line],color='lightcoral',alpha=0.5,label='',interpolate=True)
                #plt.fill_between(df.index,df[upper_line],df[lower_line],df[upper_line] == df[lower_line],color='lightgray',alpha=0.5,label='')
            except:
                print(f"  #Warning(draw_lines2): lack of data for either {upper_line} or {lower_line}")
                #return None
                
    #绘制水平辅助线
    if axhline_label !="":
        if DEBUG:
            print("DEBUG: draw axhline_label=",axhline_label)
        
        if "零线" in axhline_label:
            plt.axhline(y=axhline_value,color='black',linestyle='--',linewidth=2)  
        else:
            plt.axhline(y=axhline_value,label=axhline_label,color='black',linestyle='--',linewidth=2)  

    #用于关注值的颜色列表
    atv_color_list=["lightgray","paleturquoise","wheat","khaki","lightsage"]
    #用于关注点的颜色列表
    atp_color_list=["crimson","dodgerblue","magenta","lightseagreen","chocolate"]

    if not attention_value=='':
        if isinstance(attention_value,int) or isinstance(attention_value,float):
            atv_list=[attention_value]
        elif isinstance(attention_value,list):
            atv_list=attention_value
        else:
            atv_list=[]
        if not atv_list==[] and not atv_list==['']:
            for at in atv_list:
                pos=atv_list.index(at)
                color=atv_color_list[pos]
                plt.axhline(y=at,ls=":",c=color,linewidth=2,label=text_lang("关注值","Attention value ")+str(at))

    if not attention_value_area=='':
        if isinstance(attention_value_area,list) and len(attention_value_area)>=2:
            plt.fill_between(df.index,attention_value_area[0],attention_value_area[1],color='lightgray',alpha=0.5)
        
    import pandas as pd
    from datetime import datetime; date_format="%Y-%m-%d" 
    if not attention_point=='':
        if isinstance(attention_point,str) or isinstance(attention_point,int) or isinstance(attention_point,float):
            atp_list=[attention_point]
        elif isinstance(attention_point,list):
            atp_list=attention_point
        else:
            atp_list=[]
        #去重，不打乱原来的顺序
        atp_list=list(dict.fromkeys(atp_list))
            
        if not atp_list==[] and not atp_list==['']:
            for at in atp_list:
                pos=atp_list.index(at)
                color=atp_color_list[pos]
                
                #判断是否日期字符串
                try:
                    at=datetime.strptime(at, date_format)
                    atpd=pd.to_datetime(at)
                except:
                    atpd=at
                    
                try:
                    at_str=atpd.strftime('%Y-%m-%d')
                except:
                    at_str=atpd
                    
                #plt.axvline(x=atpd,ls=":",c=color,linewidth=1.5,label=text_lang("关注点","Attention point ")+str(at))
                plt.axvline(x=atpd,ls=":",c=color,linewidth=1.5,label=text_lang("关注点","Attention point ")+at_str)

    if not attention_point_area=='':
        if isinstance(attention_point_area,list) and len(attention_point_area)>=2:
            apa_list=[]
            for ap in attention_point_area:
                try:
                    ap=datetime.strptime(ap, date_format)
                    appd=pd.to_datetime(ap)
                except:
                    appd=ap
                apa_list=apa_list+[appd]
                
            yaxis_data=plt.ylim()
            plt.fill_betweenx(yaxis_data,apa_list[0],apa_list[1],color='powderblue',alpha=0.5)
    
    #坐标轴标记
    plt.ylabel(auto_translate2(y_label,translate),fontweight='bold',fontsize=ylabel_txt_size)
    if x_label != "":
        plt.xlabel(auto_translate2(x_label,translate),fontweight='bold',fontsize=xlabel_txt_size,ha='center')
    #图示标题
    plt.title(auto_translate2(title_txt,translate),fontweight='bold',fontsize=title_txt_size)
    
    # 使用 AutoDateLocator 自动选择最佳间隔，目的是显示最后一个日期，亲测有效！！！
    if not isinstance(maxticks,bool):    
        import matplotlib.dates as mdates
        ax.xaxis.set_major_locator(mdates.AutoDateLocator(maxticks=maxticks))   
        
        plt.gcf().autofmt_xdate(ha="center") # 优化标注（自动倾斜）
    try:
        plt.gca().set_facecolor(facecolor)
    except:
        print("  #Warning(draw_lines2): color",facecolor,"is unsupported, changed to default setting")
        plt.gca().set_facecolor("whitesmoke") 
        
    #if not annotate:
    #plt.legend没有图例标签时会提示信息No artists...
    if not annotate or attention_value !='' or attention_point !='':
        plt.legend(loc=loc,fontsize=legend_txt_size)
        
    #设置绘图风格：关闭网格虚线
    plt.rcParams['axes.grid']=False
        
    plt.show()
    
    return    

#==============================================================================
def plot_barh(df,colname,titletxt,footnote,datatag=True, \
              colors=['r','g','b','c','m','y','aquamarine','dodgerblue', \
              'deepskyblue','silver'],tag_offset=0.01,axisamp=1.3, \
              facecolor='whitesmoke'):
    """
    功能：绘制水平单值柱状图，并可标注数据标签。
    输入：数据集df；列名colname；标题titletxt；脚注footnote；
    是否绘制数据标签datatag，默认是；柱状图柱子色彩列表。
    输出：水平柱状图
    """
    #空值判断
    if len(df) ==0:
        print ("  #Warning(plot_barh): no data to plot.")
        return

    plt.barh(df.index,df[colname],align='center',color=colors,alpha=0.8)
    coltxt=ectranslate(colname)
    plt.xlabel(footnote,fontsize=xlabel_txt_size,ha='center')
    plt.title(titletxt,fontweight='bold',fontsize=title_txt_size)
    
    #xmin=int(min(df[colname]))
    xmin0=min(df[colname])
    if xmin0 > 0:
        xmin=xmin0*0.8
    else:
        xmin=xmin0*1.05
    #xmax=(int(max(df[colname]))+1)*1.1
    xmax0=max(df[colname])
    if not (xmax0 == 0):
        scale_max=abs((xmax0-xmin0)/xmax0)*axisamp  #经验值放大倍数
        xmax=xmax0*scale_max
    else:
        scale_max=abs((xmax0-xmin0))*axisamp
        xmax=xmax0+scale_max
    
    """
    if xmax0 > 0:
        xmax=xmax0*1.8
    else:
        xmax=xmax0*1.2
    """
    plt.xlim([xmin,xmax])
    
    tag_off=tag_offset * xmax
    for x,y in enumerate(list(df[colname])):
        #plt.text(y+0.1,x,'%s' % y,va='center')
        plt.text(y+tag_off,x,'%s' % y,va='center')

    """
    yticklist=list(df.index)
    yticknames=[]
    for yt in yticklist:
        ytname=codetranslate(yt)
        yticknames=yticknames+[ytname]
    """
    yticknames=list(df.index)
    plt.yticks(df.index,yticknames)

    try:
        plt.gca().set_facecolor(facecolor)
    except:
        print("  #Warning(plot_barh): color",facecolor,"is unsupported, changed to default setting")
        plt.gca().set_facecolor("whitesmoke") 
        
    plt.show(); plt.close()
    
    return

#==============================================================================
if __name__=='__main__':
    import pandas as pd
    df = pd.read_excel('S:/QTEMP/px_test.xlsx',header=0, index_col=0)  
    
    colname='Exp Ret%'
    titletxt="This is a title"
    footnote="This is a footnote"

def plot_barh2(df,colname,titletxt,footnote,facecolor='lightblue'):
    """
    功能：绘制水平单值柱状图，并在外侧标注数据标签。
    输入：数据集df；列名colname；标题titletxt；脚注footnote；
    输出：水平柱状图
    注意：在Spyder中可能工作不正常，使用plotly_express.bar
    """
    #空值判断
    if len(df) ==0:
        print ("  #Warning(plot_barh): no data to plot.")
        return

    #改造df
    df['ycolname']=df.index
    df['xcolname']=df[colname]
    xlabel=colname+'颜色棒'
    df[xlabel]=df[colname]

    #import plotly_express as px
    import plotly.express as px
    
    fig=px.bar(data_frame = df, 
               y='ycolname', #纵轴绘制的字段
               x=colname, #横轴绘制的字段
               color=xlabel, #基于df中xlabel字段的数值大小配色，并将xlabel作为颜色棒顶部的标注
               orientation='h', #绘制水平直方图
               text=colname, #在直方图顶端标数字
               labels={'ycolname':'',colname:footnote,xlabel:''} #将字段改名作为纵轴、横轴或颜色棒的标注
        )
    
    fig.update_coloraxes(showscale=False)  # 隐藏颜色条
    
    fig.update_traces(textposition='outside',#直方图顶端的数值标在外侧
                      ) 
    
    fig.update_layout(
        title={
            'text': titletxt,   # 标题名称
            'y':0.95,  # 位置，坐标轴的长度看做1
            'x':0.5,
            'xanchor': 'center',   # 相对位置
            'yanchor': 'top'},
        plot_bgcolor=facecolor, #设置画布背景颜色
        coloraxis_showscale=False, #彻底移除颜色条，需要升级plotly！
        )
    
    fig.show()
    
    return

if __name__=='__main__':
    plot_barh2(df,colname,titletxt,footnote)
#==============================================================================

#==============================================================================
#==============================================================================
def plot_2lines(df01,colname1,label1, \
                df02,colname2,label2, \
                ylabeltxt,titletxt,footnote,hline=0,vline=0,resample_freq='D', \
                date_range=False,date_freq=False,date_fmt='%Y-%m-%d', \
                facecolor='whitesmoke', \
                    maxticks=15):
    """
    功能：绘制两个证券的折线图。如果hline=0不绘制水平虚线，vline=0不绘制垂直虚线
    假定：数据表有日期索引，且已经按照索引排序
    输入：
    证券1：数据表df1，列名1，列名标签1；
    证券2：数据表df2，列名2，列名标签2；
    标题titletxt，脚注footnote
    输出：绘制同轴折线图
    
    若date_range=True，尽量在横轴上标注日期的起止时间
    若date_freq不为False，可以为类似于'3m'或'1Y'等
    date_fmt可以为'%Y-%m-%d'或'%Y-%m'或'%Y'等
    
    返回值：无
    """
    import pandas as pd
    
    #空值判断
    if len(df01) ==0:
        print ("  #Warning(plot_2lines): no data to plot df01.")
    if len(df02) ==0:
        print ("  #Warning(plot_2lines): no data to plot df02.")   
    if (len(df01) ==0) and (len(df02) ==0):
        return

    #插值平滑
    if not isinstance(maxticks,bool):    
        try:
            df01x=df01[[colname1]].astype('float')
            df1=df_smooth_manual(df01x,resample_freq=resample_freq)
        except:
            df1=df01
            
        try:
            df02x=df02[[colname2]].astype('float')        
            df2=df_smooth_manual(df02x,resample_freq=resample_freq)
        except:
            df2=df02
    else:
        df1=df01; df2=df02            
    
    plt.title(titletxt,fontweight='bold',fontsize=title_txt_size)
    
    #证券1：先绘制折线图
    if not isinstance(maxticks,bool):    
        date_start=df1.index[0]
        date_end=df1.index[-1]
        if date_range and not date_freq:
            ax=plt.gca()
            ax.xaxis.set_major_formatter(mdate.DateFormatter(date_fmt))
            plt.xticks(pd.date_range(date_start,date_end))
        if not date_range and date_freq:
            ax=plt.gca()
            ax.xaxis.set_major_formatter(mdate.DateFormatter(date_fmt))
            plt.xticks(pd.date_range(freq=date_freq))
        if date_range and date_freq:
            ax=plt.gca()
            ax.xaxis.set_major_formatter(mdate.DateFormatter(date_fmt))
            plt.xticks(pd.date_range(date_start,date_end,freq=date_freq))
    
    lwadjust=linewidth_adjust(df1)
    plt.plot(df1.index,df1[colname1],label=label1,linestyle='-',linewidth=lwadjust)
    
    #证券2：先绘制折线图
    if not isinstance(maxticks,bool):    
        date_start=df2.index[0]
        date_end=df2.index[-1]
        if date_range and not date_freq:
            ax=plt.gca()
            ax.xaxis.set_major_formatter(mdate.DateFormatter(date_fmt))
            plt.xticks(pd.date_range(date_start,date_end))
        if not date_range and date_freq:
            ax=plt.gca()
            ax.xaxis.set_major_formatter(mdate.DateFormatter(date_fmt))
            plt.xticks(pd.date_range(freq=date_freq))
        if date_range and date_freq:
            ax=plt.gca()
            ax.xaxis.set_major_formatter(mdate.DateFormatter(date_fmt))
            plt.xticks(pd.date_range(date_start,date_end,freq=date_freq))
    
    lwadjust=linewidth_adjust(df2)        
    plt.plot(df2.index,df2[colname2],label=label2,linestyle='-.',linewidth=lwadjust)
    
    #是否绘制水平虚线
    if not (hline == 0):
        plt.axhline(y=hline,ls=":",c="black")
    #是否绘制垂直虚线
    if not (vline == 0):
        plt.axvline(x=vline,ls=":",c="black")
    
    plt.ylabel(ylabeltxt,fontsize=ylabel_txt_size)
    plt.xlabel(footnote,fontsize=xlabel_txt_size,ha='center')
    plt.legend(loc='best',fontsize=legend_txt_size)
    
    # 使用 AutoDateLocator 自动选择最佳间隔，目的是显示最后一个日期，亲测有效！！！
    if not isinstance(maxticks,bool):  
        import matplotlib.dates as mdates
        ax=plt.gca()
        ax.xaxis.set_major_locator(mdates.AutoDateLocator(maxticks=maxticks))

        plt.gcf().autofmt_xdate(ha="center") # 优化标注（自动倾斜）
    try:
        plt.gca().set_facecolor(facecolor)
    except:
        print("  #Warning(plot_2lines): color",facecolor,"is unsupported, changed to default setting")
        plt.gca().set_facecolor("whitesmoke")   
        
    plt.show()
    
    return

if __name__ =="__main__":
    df1=bsm_call_maturity(42,40,[50,200],0.015,0.23,90,1.5)
    df2=bsm_put_maturity(42,40,[50,200],0.015,0.23,90,1.5)
    ticker1='A'; colname1='Option Price'; label1='A1'
    ticker2='B'; colname2='Option Price'; label2='B2'
    ylabeltxt='ylabel'; titletxt='title'; footnote='\n\n\n\n4lines'
    power=0; datatag1=False; datatag2=False; zeroline=False
    
#==============================================================================
def df_smooth(df):
    """
    功能：对df中的数值型样本进行插值，以便绘制的折线图相对平滑。
    要求：df的索引为pandas的datetime日期型
    注意1：如果样本数量较多，例如多于100个，平滑效果不明显。
    注意2：order阶数仅对'spline'和'polynomial'方法有效，其中'polynomial'方法的阶数只能为奇数。
    """
    
    # df索引项若非日期型，不适合采用本函数进行插值
    import pandas as pd
    if not pd.api.types.is_datetime64_any_dtype(df.index):
        return df
    
    #如果样本个数多于100个，其实没必要进行平滑，因为看不出效果
    if len(df) >= 100: return df
    
    #定义重采样频率
    """
    常用的采样频率：
    H: hourly, BH: business hour, T: minutely, S: secondly, B: business day, W: weekly, 
    SM: semi-month end, SMS: semi-month start, 
    BMS: business month start,BM: business month end,
    BQ: business quarter end, BQS: business quarter start,
    BA/BY: business year end, BAS/BYS: business year start.    
    
    例如：
    df2=df.resample('2D').sum()
    df2=df.resample('W').mean()
    """
    #将索引转换为Datetimeindex，不然resample会失败
    df['date']=pd.to_datetime(df.index)
    df.set_index('date',inplace=True)
    
    #重新采样
    rflag=False
    freqlist=['H','B','W','M','Q']
    for f in freqlist:
        try:
            #dfh=df.resample(f).ffill()
            dfh=df.resample(f)
        except:
            continue
        else:
            rflag=True
            break
    
    if not rflag: 
        #print('  #Warning(df_smooth): resampling failed for frequency',freqlist)
        dfh=df
    
    #重采样后插值
    methodlist=['pchip','nearest','cubic','quadratic','slinear','linear','zero','time','index', \
            'piecewise_polynomial','akima','from_derivatives','spline','polynomial']
    methodlist_order=['spline','polynomial']
    order=3
    for method in methodlist:
        if method in methodlist_order:
            try:
                dfm=dfh.interpolate(method=method,order=order)
            except:
                #print('  #Warning(df_smooth): interpolate failed for method',method,'with order',order)
                #若出错就原样返回
                return df
            else: break
        else:
            try:
                dfm=dfh.interpolate(method=method)
            except:
                #print('  #Warning(df_smooth): interpolate failed for method',method)
                return df
            else: break
    
    #成功返回经过重采样的df
    return dfm        
    
        
#==============================================================================
def df_smooth_manual(df,method='linear',resample_freq='D',order=3):
    """
    功能：对df中的第一个数值列样本进行插值，以便绘制的折线图相对平滑。
    要求：df的索引为pandas的datetime日期型
    注意1：如果样本数量较多，例如多于100个，平滑效果不明显。
    注意2：order阶数仅对'spline'和'polynomial'方法有效，其中'polynomial'方法的阶数只能为奇数。
    注意3：pchip方法经常失败，可改为cubic
    """
    
    # df索引项若非日期型，不适合采用本函数进行插值
    import pandas as pd
    if not pd.api.types.is_datetime64_any_dtype(df.index):
        return df
    
    #如果样本个数多于100个，没必要进行平滑，完全看不出效果
    if len(df) >= 100: return df
    
    #检查插值方法是否支持
    methodlist=['quadratic','cubic','slinear','linear','zero','nearest','time','index', \
            'piecewise_polynomial','pchip','akima','from_derivatives','spline','polynomial']
    if not (method in methodlist): return df
    
    #定义重采样频率
    """
    常用的采样频率：
    H: hourly, BH: business hour, T: minutely, S: secondly, B: business day, W: weekly, 
    SM: semi-month end, SMS: semi-month start, 
    BMS: business month start,BM: business month end,
    BQ: business quarter end, BQS: business quarter start,
    BA/BY: business year end, BAS/BYS: business year start.    
    
    例如：
    df2=df.resample('2D').sum()
    df2=df.resample('W').mean()
    """
    #将索引转换为Datetimeindex，不然resample会失败
    try:
        df['date']=pd.to_datetime(df.index)
    except:
        return df
    df.set_index('date',inplace=True)    
    
    #重新采样
    try:
        dfh=df.resample(resample_freq)
    except:
        print('  #Warning(df_smooth): resampling failed for frequency',resample_freq)
        return df
    
    #重采样后插值(不然太多nan)：是否methodlist_o里面的特别插值方法
    methodlist_o=['spline','polynomial']
    if method in methodlist_o:
        try:
            dfm=dfh.interpolate(method=method,order=order)
        except:
            print('  #Warning(df_smooth_manual): interpolate failed for method',method,'with order',order)
            #若出错就原样返回
            return df
        #成功返回经过重采样的df
        return dfm
    
    #重采样后插值：其他插值方法
    try:
        dfm=dfh.interpolate(method=method)
    except:
        #print('  #Warning(df_smooth_manual): interpolate failed for method',method)
        #print('  Possible reason: interpolating row must be int or float instead of string')
        """
        #改为cubic方法
        if not (method == 'cubic'):
            try:
                dfm=dfh.interpolate(method='cubic')
            except:
                print('  #Warning(df_smooth_manual): interpolate failed for method cubic')    
                return df
        else:
            return df
        """
        return df
    
    # check whether dfm becomes empty
    if len(dfm)==0:
        return df
    else:
        return dfm        
#==============================================================================
if __name__=='__main__':
    wid=5
    mu=0
    sd=1
    obs_num=100
    
def plot_norm(mu,sd,graph='pdf',obs_num=100,facecolor='whitesmoke'):
    """
    绘制正态分布图形
    mu:均值
    sd:标准差
    graph:图形种类,pdf,cdf,ppf
    """
    if not (graph in ['pdf','cdf','ppf']):
        print("  #Warning(plot_norm): support pdf/cdf/ppf only")
        return
    
    #计算概率密度:连续分布用pdf,离散分布用pmf
    import scipy.stats as st
    import numpy as np
    
    if graph=='pdf':
        wid=4*sd+mu
        X=np.linspace(-wid,wid,obs_num)
        y_pdf=st.norm.pdf(X,mu,sd) 
    
    if graph=='cdf':
        wid=3*sd+mu
        X=np.linspace(-wid,wid,obs_num)        
        y_cdf=st.norm.cdf(X,mu,sd)
        
    if graph=='ppf':
        X=np.linspace(0,1,obs_num)
        y_ppf=st.norm.ppf(X,mu,sd)

    #绘图
    if graph=='pdf':
        plt.plot(X,y_pdf,c="red",label='pdf')
    if graph=='cdf':
        plt.plot(X,y_cdf,c="blue",label='cdf')
    if graph=='ppf':
        plt.plot(X,y_ppf,c="green",label='ppf')
    
    if graph=='pdf':
        wid1=5*sd+mu
        wid2=1*sd+mu
        plt.xticks(np.arange(-wid,wid1,wid2))
        plt.xlabel('分位点',fontsize=xlabel_txt_size,ha='center') #x轴文本
        plt.yticks(np.arange(0,0.45,0.05))
        plt.ylabel('概率密度',fontsize=ylabel_txt_size) #y轴文本

    if graph=='cdf':
        wid1=3.5*sd+mu
        wid2=0.5*sd+mu        
        plt.xticks(np.arange(-wid,wid1,wid2))
        plt.xlabel('分位点',fontsize=xlabel_txt_size,ha='center') #x轴文本
        plt.yticks(np.arange(0,1.1,0.1))
        plt.ylabel('累积概率密度',fontsize=ylabel_txt_size) #y轴文本

    if graph=='ppf':
        wid=2.5*sd+mu
        wid1=3*sd+mu
        wid2=0.5*sd+mu
        plt.yticks(np.arange(-wid,wid1,wid2))
        plt.ylabel('分位点',fontsize=ylabel_txt_size) #y轴文本
        plt.xticks(np.arange(0,1.1,0.1))
        plt.xlabel('累积概率密度',fontsize=xlabel_txt_size,ha='center') #x轴文本        
        
    plt.title('正态分布示意图: $\mu$=%.1f, $\sigma$=%.1f'%(mu,sd),fontweight='bold',fontsize=title_txt_size) #标题
    plt.tight_layout()
    #plt.grid() #网格
    plt.legend(loc='best',fontsize=legend_txt_size)
    
    try:
        plt.gca().set_facecolor(facecolor)
    except:
        print("  #Warning(plot_norm): color",facecolor,"is unsupported, changed to default setting")
        plt.gca().set_facecolor("whitesmoke")  
        
    plt.show() #显示图形
    
    return

if __name__=='__main__':
    plot_norm(4,mu,sd,graph='pdf')
    plot_norm(3,mu,sd,graph='cdf')
    plot_norm(3,mu,sd,graph='ppf')        
    
#==============================================================================    
#==============================================================================

if __name__=='__main__':
    firstColSpecial=True
    colWidth=0.1
    tabScale=2
    figsize=(12.8,6.4)
    cellLoc='right'
    fontsize=10

    firstColSpecial=False
    cellLoc='center'
    auto_len=True
    
    df=market_detail_china(category='price')
    pandas2plttable(df)

def pandas2plttable(df,titletxt,firstColSpecial=True,colWidth=0.1,tabScale=2,cellLoc='right', \
                    figsize=(12.8,6.4),fontsize=13,auto_len=False,title_x=0.5):
    """
    功能：将一个df转换为matplotlib表格格式，打印图形表格，适应性广
    firstColSpecial：第一列是否特殊处理，默认True
    
    注意1：引入表格的字段不包括索引字段
    """  
    
    #列名列表
    col=list(df)
    numOfCol=len(col)
    
    # 第一列长度取齐处理
    if firstColSpecial:
        #第一列的最长长度
        firstcol=col[0]
        maxlen=0
        for f in firstcol:
            flen=hzlen(f.strip())
            if flen > maxlen:
                maxlen=flen
        
        #将第一列内容的长度取齐
        df[col[0]]=df[col[0]].apply(lambda x:equalwidth(x.strip(),maxlen=maxlen,extchar=' ',endchar=' '))    
    
    #设置每列的宽度
    col_len_list=[]
    col_len_list_rel=[]
    if auto_len:
        
        # 计算每列的相对宽度
        for c in col:
            heading_len=hzlen(c.strip())
            df['col_len']=df[c].apply(lambda x: hzlen(x.strip()))
            field_len=df['col_len'].max()
            col_len=max([heading_len,field_len])
            
            col_len_list=col_len_list+[col_len]

        col_len_min=min(col_len_list)
        for l in col_len_list:
            rel_len=l / col_len_min               
            col_len_list_rel=col_len_list_rel+[round(rel_len*colWidth,3)]
            
        del df['col_len']
    
    
    #表格里面的具体值
    vals=[]
    for i in range(0,len(df)): 
        vals=vals+[list(df.iloc[i])]
    
    plt.figure(figsize=figsize)
    
    if not auto_len:
        tab = plt.table(cellText=vals, 
                      colLabels=col, 
                      loc='best', 
                      cellLoc=cellLoc)
    else:
        tab = plt.table(cellText=vals, 
                      colLabels=col, 
                      colWidths=col_len_list_rel,
                      loc='best', 
                      rowLoc='center',
                      cellLoc=cellLoc)
            
    
    tab.scale(1,tabScale)   #让表格纵向扩展tabScale倍数
    
    # 试验参数：查询tab对象的属性使用dir(tab)
    tab.auto_set_font_size(False)
    tab.set_fontsize(fontsize)
    
    if auto_len:
        tab.auto_set_column_width(True)    #此功能有bug，只能对前几列起作用
    
    plt.axis('off')         #关闭plt绘制纵横轴线
    
    #plt.xlabel(footnote,fontsize=xlabel_txt_size)
    if not auto_len:
        plt.title(titletxt,fontweight='bold',fontsize=title_txt_size)
    else:
        plt.title(titletxt,fontweight='bold',fontsize=title_txt_size,x=title_x)
    
    plt.gca().set_facecolor('whitesmoke')
    
    plt.show()

    return

#==============================================================================

if __name__=='__main__':
    firstColSpecial=True
    colWidth=0.1
    tabScale=2
    figsize=(10,6)
    cellLoc='right'
    fontsize=10

    firstColSpecial=False
    cellLoc='center'
    auto_len=True
    
    df=market_detail_china(category='price')
    pandas2plttable(df)

def pandas2plttable2(df,titletxt,firstColSpecial=True,cellLoc='right'):
    """
    功能：将一个df转换为matplotlib表格格式，打印图形表格，适应性广，自动适应列宽和字体大小
    firstColSpecial：第一列是否特殊处理，默认True
    
    注意1：引入表格的字段不包括索引字段
    """  
    
    df.fillna('',inplace=True)
    
    #列名列表
    col=list(df)
    numOfCol=len(col)
    
    # 第一列长度取齐处理
    if firstColSpecial:
        
        #第一列的最长长度
        firstcol=col[0]
        maxlen=0
        for f in df[firstcol]:
            flen=hzlen(f)
            if flen > maxlen:
                maxlen=flen
        
        #将第一列内容的长度取齐
        extchar='.'
        df[firstcol]=df[firstcol].apply(lambda x: str(x) + extchar*(maxlen-hzlen(x)))    
    
    
    #表格里面的具体值
    vals=[]
    for i in range(0,len(df)): 
        vals=vals+[list(df.iloc[i])]
    
    plt.figure()
    
    tab = plt.table(cellText=vals, 
                  colLabels=col, 
                  loc='best', 
                  rowLoc='center',
                  cellLoc=cellLoc)
    
    #tab.scale(1,tabScale)   #让表格纵向扩展tabScale倍数
    
    # 试验参数：查询tab对象的属性使用dir(tab)
    tab.auto_set_font_size(True)
    
    tab.auto_set_column_width(True)    #此功能有bug，只能对前几列起作用
    
    plt.axis('off')         #关闭plt绘制纵横轴线
    
    plt.title(titletxt)
    
    plt.gca().set_facecolor('whitesmoke')
    
    plt.show()

    return


#==============================================================================    
#==============================================================================








