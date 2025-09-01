import pandas as pd
from sqlalchemy import create_engine 
import datetime
"""
enginestr = 'postgresql://postgres:{}@{}:{}/exam_data'.format(passwd,ip,port)

"""
def get_create_engine(enginestr):
    engine = create_engine(enginestr)
    return engine
engine = get_create_engine(enginestr)
# 创建一个示例 DataFrame
def data_column_lower(exam_data):
    exam_data.columns = [col.lower() for col in exam_data.columns]
    return exam_data
def data_column_upper(exam_data):
    exam_data.columns = [col.upper() for col in exam_data.columns]
    return exam_data
def get_current_time_format():
    now = datetime.datetime.now()
    formatted_now = now.strftime('%Y-%m-%d %H:%M:%S')    
    return formatted_now  
def write_to_postgresql(df):        
    # 将 DataFrame 写入 PostgreSQL 表中
    df.to_sql('weather_data_test', if_exists='replace', index=False,con=engine)    
def read_from_postgresql():
    df_from_sql = pd.read_sql('qurey sql', con=engine)
    return df_from_sql

def databasequerystr(sCST, eCST,tb =table):
    sCSTStr = sCST.strftime('%Y%m%d%H%M')
    eCSTStr = eCST.strftime('%Y%m%d%H%M')
    if len(eCSTStr)!=12 or len(eCSTStr) !=12:
        raise Exception("The time format is incorrect")
    timerange = list({sCSTStr,eCSTStr})
    if tb =="1":
        if len(timerange) == 1 :
           querystr = f" SELECT * FROM {table1} where datetime1 = '{sCSTStr}'"
        else:
           querystr = f" SELECT * FROM {table1} where datetime1 >='{sCSTStr}' and datetime1 <'{eCSTStr}' " 
    else:
        if len(timerange) == 1 :
           querystr = f" SELECT * FROM {table} where datetime = '{sCSTStr}'"
        else:
           querystr = f" SELECT * FROM {table} where datetime >='{sCSTStr}' and datetime <'{eCSTStr}' " 
    return querystr  

querystr = databasequerystr(sCST, eCST)
with engine.connect() as connection:
     df1d = pd.read_sql(querystr, con=connection) 
df1d = pd.read_sql(querystr, con=engine)
engine.dispose() 



from postsql.baseconfig import *
from shancx import loggers as logger
import argparse
import datetime
import pandas as pd

def options():
    parser = argparse.ArgumentParser(description='examdatabasedata')
    parser.add_argument('--times', type=str, default='202411100000,202411101000') 
    config= parser.parse_args()
    print(config)
    config.times = config.times.split(",")
    if len(config.times) == 1:
        config.times = [config.times[0], config.times[0]]
    config.times = [datetime.datetime.strptime(config.times[0], "%Y%m%d%H%M"),
                    datetime.datetime.strptime(config.times[1], "%Y%m%d%H%M")]
    return config
if __name__ == '__main__':
    cfg = options()
    sCST = cfg.times[0]
    eCST = cfg.times[-1]
    querystr = databasequerystr(sCST, eCST)
    df1d = pd.read_sql(querystr, con=engine) 
    print()

"""
SELECT pg_size_pretty(pg_total_relation_size('your_table_name')) AS total_size
ftp://ftp.ncdc.noaa.gov/pub/data/noaa/isd-lite/
tgftp.nws.noaa.gov
/data/observations/metar/decoded 
ftp://ftp.cpc.ncep.noaa.gov/precip/cmorph/
https://www.ncei.noaa.gov/data/global-hourly/access/2024/
ftp://ftp.cpc.ncep.noaa.gov      路径文件  /precip/CMORPH2/CMORPH2NRT/DATA/2024  全球25公里 逐30min 卫星 降雨 nc文件
"""