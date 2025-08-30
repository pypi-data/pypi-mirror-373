#!/usr/bin/python
# -*- coding: utf-8 -*-
# @Time : 2024/10/17 上午午10:40
# @Author : shancx
# @File : __init__.py
# @email : shanhe12@163.com


import datetime
def UTC10minDiff():    
    now_utc = datetime.datetime.utcnow() 
    rounded_minute = round(now_utc.minute / 10) * 10
    if rounded_minute == 60:
        rounded_minute = 0
        now_utc += datetime.timedelta(hours=1)
    adjusted_time = now_utc.replace(minute=rounded_minute, second=0, microsecond=0)
    formatted_time = adjusted_time.strftime('%Y%m%d%H%M')
    return formatted_time

def UTCStr():    
    now_utc = datetime.datetime.utcnow() 
    now_utcstr = now_utc.strftime('%Y%m%d%H%M%S')
    return now_utcstr

def CSTStr():    
    now_cst = datetime.datetime.now() 
    now_cststr = now_cst.strftime('%Y%m%d%H%M%S')
    return now_cststr

def TimeStamp2datatime(timestamp):    
    dt_object = datetime.datetime.fromtimestamp(timestamp)
    return dt_object 
 
import calendar
def datatime2timeStamp(datetime_):  
    timestamp = calendar.timegm(datetime_.utctimetuple())
    return timestamp

def Datetime2str(datetime_):    
    formatted_time = datetime_.strftime("%Y%m%d%H%M%S")
    return formatted_time

from dateutil.relativedelta import relativedelta
def Relativedelta(T_,Th = 0,Tm=0):
 mktime = T_+relativedelta(hours=Th,minutes=Tm)
 return mktime

def nearest_hour():
    now = datetime.datetime.now()
    # 计算当前小时整点时间
    minute = now.minute
    second = now.second
    # 如果分钟数大于等于30分钟，则向上取整
    if minute >= 57:
        next_hour = now + datetime.timedelta(hours=1)
        nearest_hour = next_hour.replace(minute=0, second=0, microsecond=0)
    elif minute <= 3:
        nearest_hour = now.replace(minute=0, second=0, microsecond=0)
    else:
        nearest_hour = now
    return nearest_hour.strftime("%Y%m%d%H%M")

import pandas as pd
def gtr(sUTC,eUTC, freq='6min'):
    minute = sUTC.minute
    if minute in [15, 45]:
        start_time = sUTC + relativedelta(minutes=3)  # 15 或 45 分钟时，起始点加 3 分钟
    elif minute in [0, 30]:
        start_time = sUTC + relativedelta(minutes=6)  # 0 或 30 分钟时，起始点加 6 分钟
    else:
        raise ValueError("sUTC 的分钟数必须是 0、15、30 或 45 分钟")
    new_times = pd.date_range(start_time, eUTC, freq=freq)
    return new_times 

def gtr10min(sUTC,eUTC, freq='6min'):
    minute = sUTC.minute
    if minute in [10,40]:
        start_time = sUTC + relativedelta(minutes=2)  # 15 或 45 分钟时，起始点加 2 分钟
    elif minute in [20, 50]:
        start_time = sUTC + relativedelta(minutes=4)  # 0 或 30 分钟时，起始点加 4 分钟
    elif minute in [0, 30]:
        start_time = sUTC + relativedelta(minutes=6)   # 0 或 30 分钟时，起始点加 4 分钟
    else:
        raise ValueError("sUTC 的分钟数必须是 0、10、20、30 或40、50 分钟")
    new_times = pd.date_range(start_time, eUTC, freq=freq)
    return new_times 

import datetime as dt
import pandas as pd
def ldom(d):  # last day of month
    if d.month == 12:
        return d.replace(year=d.year+1, month=1, day=1) - dt.timedelta(days=1)
    return d.replace(month=d.month+1, day=1) - dt.timedelta(days=1)
def gen_dt(s, e, t="trn"):  # generate dates
    dr = pd.date_range(start=s, end=e, freq='1h')
    res = []    
    for d in dr:
        me = ldom(d)
        is_me = d.day >= (me.day - 1)        
        if (t == "trn" and not is_me) or (t == "val" and is_me):
            res.append(d.strftime('%Y%m%d%H%M'))    
    return res
"""
if __name__ == "__main__":
    s = dt.datetime(2023, 1, 28)
    e = dt.datetime(2023, 2, 3)    
    print("Train dt (excl month end):")
    print(gen_dt(s, e, "trn"))    
    print("\nValid dt (only month end):")
    print(gen_dt(s, e, "val"))
"""



