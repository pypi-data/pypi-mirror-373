#!/usr/bin/python
# -*- coding: utf-8 -*-
# @Time : 2024/10/17 上午午10:40
# @Author : shancx
# @File : __init__.py
# @email : shanhe12@163.com

import numpy as np
def getmask(df,col = 'PRE1_r'):
    df[col] = df[col].mask(df[col] >= 9999, np.nan)     
    df = df.dropna()
    return df

def Type(df_,col = 'stationID'):
    df_['stationID'] = df_['stationID'].astype("str")
    return df_
def Dtype(df_):
    dftypes = df_.dtypes
    print(dftypes)
    return dftypes

# 如果env_rang的定义是 (北界, 南界, 西界, 东界)
def getrange(df,env_rang=None):
    north, south, west, east = env_rang
    filtered_data = df[
        (df["Lat"] < north) & 
        (df["Lat"] > south) & 
        (df["Lon"] > west) & 
        (df["Lon"] < east)
    ]
    return filtered_data

#pd.concat(filter(None, results))
#valid_results = [df for df in results if isinstance(df, pd.DataFrame) and not df.empty]
