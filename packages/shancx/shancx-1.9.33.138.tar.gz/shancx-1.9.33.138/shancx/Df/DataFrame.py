import numpy as np
def getmask(df,col = 'PRE1_r'):
    df[col] = df[col].mask(df[col] >= 9999, np.nan)     
    df = df.dropna()
    return df
def Type(df_,col = 'stationID'):
    df_['stationID'] = df_['stationID'].astype("str")
    return df_
def Startswith(df,column_name,value):
    df = df[df[f'{column_name}'].astype(str).str.startswith(f"{value}")].reset_index()
    return df
def Startswith1(df,column_name,value):
    df = df[~df[f'{column_name}'].astype(str).str.startswith(f"{value}")].reset_index()
    return df
def Drop_duplicates(realDF,col):
    realDF = realDF.drop_duplicates(subset=f"{col}").reset_index()
    return realDF
 