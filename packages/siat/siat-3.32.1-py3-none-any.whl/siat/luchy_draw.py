# -*- coding: utf-8 -*-

"""
本模块功能：幸运抽奖，仅限课堂案例演示用
创建日期：2024年6月29日
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

import pandas as pd
import pickle
import random
import datetime
import time
import os
from IPython.display import display_html, HTML
 
#==============================================================================

def current_dir(printout=True):
    """
    功能：找出当前路径
    """
    
    current_path = os.getcwd()
    
    if printout:
        print(f"[Current path] {current_path}")
        
    return current_path

#==============================================================================
if __name__=='__main__':
    file_path="S:\北外工作-24春\小学期-人大\学生名单\student_list.xlsx"
    pickle_path="student_list.pkl"
    
    existing(file_path)
    existing(pickle_path)
    

def existing(file_path):
    """
    功能：检查文件file_path是否存在，不带路径时检查当前目录
    """
    # 检查文件是否存在
    if os.path.exists(file_path):
        if os.path.isfile(file_path):
            return True
        else:
            return False
    else:
        return False    

#==============================================================================
if __name__=='__main__':
    text="A B C"
    text_color='red'
    text_size=12
    delay=1
    
    typewriter(text,text_color='red',text_size=12,delay=1)      

def typewriter(text,text_color='blue',text_size=12,delay=3):
    """
    功能：居中显示带颜色的大字体
    """    
    from IPython.display import display_html
    
    time.sleep(delay)
    
    text_html="<center><font size="+str(text_size)+" color="+text_color+">"+text
    display_html(text_html, raw=True)

    return

#==============================================================================

def pickle_write(df,pickle_path,overlap_confirm=True):
    
    ok2go=True
    
    if overlap_confirm:
        cur_dir=current_dir(printout=False)
        
        prompt=pickle_path+" already exists in "+cur_dir+", overwrite it?"
        file_exist=existing(pickle_path)
        if file_exist:
            #是否覆盖已经存在的文件
            yes=read_yes_no(prompt, default=None)
            if not yes:
                ok2go=False
    
    if ok2go:
        with open(pickle_path, 'wb') as pickle_file:
            # 使用pickle模块的dump函数写入对象
            pickle.dump(df,pickle_file)   
            
    return

if __name__=='__main__':
    course="SICS RUC24"
    file_path="S:\北外工作-24春\小学期-人大\学生名单\student_list.xlsx"
    pickle_path="student_list.pkl"
    skiprows=1
    column='Name'
    
    draw_limit=2
    absent_limit=2
    pass_limit=2
    
    lucky_draw_header_create(course,file_path, \
                                 skiprows=1,column='Name',draw_limit=2, \
                                     absent_limit=2,pass_limit=2)
    pickle_read(pickle_path=course+' header.pkl')        
    
    
def lucky_draw_header_create(course,file_path, \
                             skiprows=1,column='Name',draw_limit=2, \
                             absent_limit=2,pass_limit=2):
    """
    功能：创建随机点名头文件，存储随机点名的参数信息
    """
    
    pickle_path=course+" detail.pkl"
    header_path=course+" header.pkl"
    cur_dir=current_dir(printout=False)
    
    header_dict={'course':course,'file_path':file_path,'pickle_path':pickle_path, \
                'skiprows':skiprows,'column':column,'draw_limit':draw_limit, \
                'absent_limit':absent_limit,'pass_limit':pass_limit}  
        
    pickle_write(header_dict,header_path)
    print(header_path,"is created in",cur_dir)
    
    return

if __name__=='__main__':
    course="SICS RUC24"
    
    lucky_draw_header_modify(course,draw_limit=3) 
    pickle_read(pickle_path=course+' header.pkl')

def lucky_draw_header_modify(course,file_path="current",pickle_path="current", \
                             skiprows="current",column="current",draw_limit="current", \
                             absent_limit="current",pass_limit="current"):
    
    header_path=course+" header.pkl"
    header_dict=pickle_read(header_path) 
    cur_dir=current_dir(printout=False)
    
    if file_path !='current':
        header_dict['file_path']=file_path
    else:
        file_path=header_dict['file_path']
    
    if pickle_path !='current':
        header_dict['pickle_path']=pickle_path
    else:
        pickle_path=header_dict['pickle_path']
        
    if skiprows !='current':
        header_dict['skiprows']=skiprows
    else:
        skiprows=header_dict['skiprows']
    
    if column !='current':
        header_dict['column']=column
    else:
        column=header_dict['column']
    
    if draw_limit !='current':
        header_dict['draw_limit']=draw_limit
    else:
        draw_limit=header_dict['draw_limit']
    
    if absent_limit !='current':
        header_dict['absent_limit']=absent_limit
    else:
        absent_limit=header_dict['absent_limit']
    
    if pass_limit !='current':
        header_dict['pass_limit']=pass_limit
    else:
        pass_limit=header_dict['pass_limit']
    
    header_dict={'course':course,'file_path':file_path,'pickle_path':pickle_path, \
                'skiprows':skiprows,'column':column,'draw_limit':draw_limit, \
                'absent_limit':absent_limit,'pass_limit':pass_limit}  
        
    pickle_write(header_dict,header_path,overlap_confirm=False)
    print(header_path,"is modified in",cur_dir)
    
    return

#==============================================================================
if __name__=='__main__':
    course="SICS RUC24"
    lucky_draw_detail_create(course)
    pickle_read(course+" detail.pkl")

    
def lucky_draw_detail_create(course):
    """
    功能：创建随机点名明细文件，记录随机点名的过程
    """
    #读取参数信息
    header_path=course+" header.pkl"
    header_dict=pickle_read(header_path) 
    detail_path=header_dict['pickle_path']
    cur_dir=current_dir(printout=False)

    #读取学生名单
    df = pd.read_excel(header_dict['file_path'],skiprows=header_dict['skiprows'])  
    df1=df[[header_dict['column']]].copy()  

    todaydt = str(datetime.date.today())
    df1['Date']=todaydt
    df1['Lucky']=0
    df1['Absent']=0
    df1['Pass']=0
    
    #排序
    df1.sort_values(by=[header_dict['column'],'Date','Lucky','Absent','Pass'],inplace=True)
    df1.reset_index(drop=True,inplace=True)
    df1.index=df1.index + 1
    
    pickle_write(df1,detail_path)
    print(detail_path,"is created in",cur_dir)
        
    return

if __name__=='__main__':
    course="SICS RUC24"
    
    lucky_draw_detail_add(course,name="Liu Chixin")
    lucky_draw_detail_add(course,name=["Liu Chixin","Zhang San Feng","Li Si Ye"])
    
    pickle_read(course+" detail.pkl")


def lucky_draw_detail_add(course,name):
    """
    功能：在随机点名明细文件中增加一个名字，支持批量增加
    """
    #读取参数信息
    header_path=course+" header.pkl"
    header_dict=pickle_read(header_path) 
    
    #读取明细文件
    detail_path=header_dict['pickle_path']
    df=pickle_read(detail_path) 

    todaydt = str(datetime.date.today())

    if isinstance(name,str):
        name=[name]

    added=False        
    for n in name:
        #重名检查
        if n in list(df[header_dict['column']]):
            print(n,"is already in file, no need to add")
            continue
    
        #增加名单
        added=True
        row=pd.Series({header_dict['column']:n,'Date':todaydt,'Lucky':0,'Absent':0,'Pass':0})
        try:
            df=df.append(row,ignore_index=True)        
        except:
            df=df._append(row,ignore_index=True)
            
        print(n,"is added into file")

    #写回明细文件
    if added:
        pickle_write(df,detail_path,overlap_confirm=False)
        
    return

#==============================================================================
if __name__=='__main__':
    course="SICS RUC24"
    
    lucky_draw_detail_remove(course,name="Liu Chixin")
    lucky_draw_detail_remove(course,name=["Liu Chixin","Zhang San Feng","Li Si Ye"])
    pickle_read(course+" detail.pkl")


def lucky_draw_detail_remove(course,name):
    """
    功能：在随机点名明细文件中删除一个名字的所有记录，支持批量删除
    """
    #读取参数信息
    header_path=course+" header.pkl"
    header_dict=pickle_read(header_path) 
    
    #读取明细文件
    detail_path=header_dict['pickle_path']
    df=pickle_read(detail_path) 
    
    if isinstance(name,str):
        name=[name]

    found=False        
    for n in name:
        #检查是否存在
        if n not in list(df[header_dict['column']]):
            print(n,"is not in file, no need to remove")
            continue
        
        found=True
        #删除该名字的所有记录
        to_drop = df[df[header_dict['column']] == n].index
        df.drop(to_drop, inplace=True)
        
        print(n,"is removed from file")
    
    #写回明细文件
    if found:
        pickle_write(df,detail_path,overlap_confirm=False)
        
    return

#==============================================================================
if __name__=='__main__':
    course="SICS RUC24"
    lucky_color="blue"
    


def random_draw(course,lucky_color="blue"):
    """
    随机点名，并记录
    draw_limit：整个课程每人最多几次抽签机会
    absent_limit：整个课程每人最多缺席几次，超过就丧失抽签资格
    pass_limit：整个课程每人最多可以pass几次，超过就丧失抽签资格
    """
    #读取参数信息
    header_path=course+" header.pkl"
    header_dict=pickle_read(header_path) 
    
    #读取明细文件
    detail_path=header_dict['pickle_path']
    df=pickle_read(detail_path) 
    
    #点名名单
    column=header_dict['column']
    alist=list(set(list(df[column])))    
    
    found=False
    todaydt = str(datetime.date.today())
    draw_limit=header_dict['draw_limit']
    absent_limit=header_dict['absent_limit']
    pass_limit=header_dict['pass_limit']
    column=header_dict['column']
    
    prompt="*** Is the lucky person here on site?"
    prompt2="*** Does the lucky person expect to pass?"
    prompt3="*** Continue lucky draw?"
    
    while True:
        while True:
            aname=random_select(alist)
            
            adf=df[df[column]==aname]
            atimes=adf['Lucky'].sum()
            aonsite=adf['Absent'].sum()
            apass=adf['Pass'].sum()
            
            if atimes < draw_limit and aonsite <= absent_limit and apass < pass_limit:
                #检查今日是否被抽中过
                drew_today=False
                try:
                    adf_today=adf[adf['Date']==todaydt]
                    if len(adf_today) > 0:
                        if adf_today['Lucky'].sum() > 0:
                            #有当日记录，且被抽中过（排除当日刚刚加入课程的情形）
                            drew_today=True
                except: pass
                
                if not drew_today:                    
                    found=True
                    break
                else: continue
            else:
                continue

        if not found:  
            #循环完毕，无合适人选
            print("Congratulations! all person has been lucky for",draw_limit,"times")
        else:
            typewriter(text=aname,text_color=lucky_color,text_size=12,delay=1)
            
            #是否到场
            onsite=read_yes_no(prompt)
            if onsite: absent=0
            else: absent=1
            
            #是否pass
            onpass=False
            bpass=0
            if onsite:            
                onpass=read_yes_no(prompt2)
                #是否pass
                if onpass: bpass=1
            
            #只要抽中，不论是否到场都记录
            row=pd.Series({column:aname,'Date':todaydt,'Lucky':1,'Absent':absent,'Pass':bpass})
            try:
                df=df.append(row,ignore_index=True)        
            except:
                df=df._append(row,ignore_index=True)
                            
            if onsite and not onpass:
                proceed=read_yes_no(prompt3)
                if not proceed:
                    #到场且不pass，结束本轮抽签
                    print("=== Lucky draw ends!")
                    break
            else:
                #未到场或pass，继续抽签
                continue
    
    df.sort_values(by=[column,'Date'],inplace=True)
    pickle_write(df,detail_path,overlap_confirm=False)
    
    return

#==============================================================================
#==============================================================================
if __name__=='__main__':
    file_path="S:\北外工作-24春\小学期-人大\学生名单\student_list.xlsx"
    
    draw_limit=2
    absent_limit=2
    pass_limit=2

    
    lucky_draw_initialize(file_path,skiprows=1,column='Name',pickle_path="student_list.pkl")
    
def lucky_draw_initialize(file_path,skiprows=1,column='Name',pickle_path="student_list.pkl"):
    """
    功能：读入带有指定路径的Excel文件file_path，跳过前skiprows行
    Excel文件结构：抽奖名单字段为'Name'，字段位于第2行
    输出：存入pickle文件student_list.pkl
    废弃！！！
    """
    
    df = pd.read_excel(file_path,skiprows=skiprows)  
    
    df1=df[[column]].copy()  
    
    todaydt = str(datetime.date.today())
    df1['Date']=todaydt
    df1['Lucky']=0
    df1['Absent']=0
    df1['Answer']=0
    
    #排序
    df1.sort_values(by=[column,'Date','Lucky','Absent','Answer'],inplace=True)
    df1.reset_index(drop=True,inplace=True)
    
    pickle_write(df1,pickle_path)
    
    return

#==============================================================================
if __name__=='__main__':
    pickle_path="SICS RUC24 detail.pkl"
    
    df=pickle_read(pickle_path)

def pickle_read(pickle_path):   
    with open(pickle_path,'rb') as pickle_file:
        df = pickle.load(pickle_file)
    return df


#==============================================================================
if __name__=='__main__':
    alist=["A","B","C","D"]
    
    for i in range(4):
        print(random_select(alist))


def random_select(alist):
    return random.choice(alist)

#==============================================================================

if __name__=='__main__':
    prompt="Is the lucky person here in class?"
    
    read_yes_no(prompt)

    
def read_yes_no(prompt, default=None):
    if default is None:
        prompt += " [yes/no] "
    else:
        prompt += " [yes/no] (default: %s) " % ('yes' if default else 'no')
    while True:
        user_input = input(prompt).lower()
        if user_input in ['', 'yes', 'y', 'true']:
            return True
        elif user_input in ['no', 'n', 'false']:
            return False
        elif user_input == '' and default is not None:
            return default
        else:
            print("Please enter 'yes' or 'no' (or 'y'/'n').")
            
    return

#==============================================================================
if __name__=='__main__':
    draw_limit=2
    absent_limit=2
    column='Name'
    pickle_path="student_list.pkl"
    
    lucky_draw()
    df=pickle_read(pickle_path)
    

def lucky_draw(draw_limit=2,absent_limit=2,column='Name',pickle_path="student_list.pkl"):
    """
    draw_limit=2：整个课程每人最多2次抽签机会
    absent_limit=2：整个课程每人最多缺席2次，超过就丧失抽签资格
    废弃！
    """
    df=pickle_read(pickle_path)

    alist=list(set(list(df[column])))    
    
    found=False
    todaydt = str(datetime.date.today())
    prompt="*** Is the lucky person here on site?"
    prompt2="*** Does the lucky person expect to pass?"
    prompt3="*** Continue luck draw?"
    
    while True:
        while True:
            aname=random_select(alist)
            
            adf=df[df[column]==aname]
            atimes=adf['Lucky'].sum()
            aonsite=adf['Absent'].sum()
            
            if atimes < draw_limit and aonsite <= absent_limit:
                #检查今日是否被抽中过
                drew_today=False
                try:
                    adf_today=adf[adf['Date']==todaydt]
                    if len(adf_today) > 0:
                        if adf_today['Lucky'].sum() > 0 or adf_today['Absent'].sum() > 0:
                            drew_today=True
                except: pass
                
                if not drew_today:                    
                    found=True
                    break
                else: continue
            else:
                continue

        if not found:  
            print("Congratulations! all person has been lucky for",limit,"times")
        else:
            """
            print("\nThe lucky person is ",end='')
            typewriter(aname,delay=1) 
            """
            typewriter(text=aname,text_color='blue',text_size=12,delay=1)
            
            #print('')
            onsite=read_yes_no(prompt)
            #是否到场
            if onsite: absent=0
            else: absent=1
            
            onpass=False; answer=0
            if onsite:            
                onpass=read_yes_no(prompt2)
                #是否pass
                if onpass: answer=0
                else: answer=1 
            
            #只要抽中，不论是否到场都记录
            row=pd.Series({column:aname,'Date':todaydt,'Lucky':1,'Absent':absent,'Answer':answer})
            try:
                df=df.append(row,ignore_index=True)        
            except:
                df=df._append(row,ignore_index=True)
                            
            if onsite and not onpass:
                #到场且不pass，结束本轮抽签
                proceed=read_yes_no(prompt3)
                if not proceed:
                    break
            else:
                #未到场或pass，继续抽签
                continue
    
    df.sort_values(by=[column,'Date'],inplace=True)
    pickle_write(df,pickle_path)
    
    return

#==============================================================================
#==============================================================================
#==============================================================================
#==============================================================================        







    


#==============================================================================#==============================================================================
#==============================================================================#==============================================================================
#==============================================================================#==============================================================================

#==============================================================================
