
    
import os 
from pathlib import Path
def CurPath():
    current_file_path = os.path.abspath(__file__) 
    current_folder_path = os.path.dirname(current_file_path)
    parent = Path(__file__).parent
    return current_folder_path,parent

import sys
def CurPathplus():
    # 获取当前执行文件的绝对路径
    current_file_path = os.path.abspath(sys.argv[0])
    current_folder_path = os.path.dirname(current_file_path)
    return current_folder_path

from pathlib import Path 
def RootFilePaths(root_path=None):
    root_dir = Path(f'{root_path}')
    npy_files = list(root_dir.rglob('*.*'))
    return npy_files
""" 
import gzip
with gzip.open(file_path=None, 'rt') as file:
    first_line = file.readline()
"""

"""
CSV

import gzip
import csv
with gzip.open(file_path, 'rt') as file:
    reader = csv.reader(file)
    for row in reader:
        print(row)

XML

import gzip
import xml.etree.ElementTree as ET
with gzip.open(file_path, 'rt') as file:
    tree = ET.parse(file)
    root = tree.getroot()
    for child in root:
        print(child.tag, child.attrib)

YAML        

import gzip
import yaml
with gzip.open(file_path, 'rt') as file:
    data = yaml.safe_load(file)
    print(data)

TEXT

import gzip
with gzip.open(file_path, 'rt') as file:
    for line in file:
        print(line.strip())

"""
 
"""   model 2
import matplotlib.pyplot as plt
import datetime
import time
import os
import time
import shutil 
from dateutil.relativedelta import relativedelta
import glob
import argparse
from multiprocessing import Pool
from itertools import product
import pandas as pd  
import numpy as np
import copy
import traceback  
from shancx.NN import _loggers
logger = _loggers()
from shancx import crDir,Mul_sub

base_source_dir = "/mnt/wtx_weather_forecast/CMA_DATA/NAFP/EC/C1D/2023/2023123120/"
base_source_dir = "/mnt/wtx_weather_forecast/CMA_DATA/NAFP/EC/C1D"
# 目标文件夹路径
target_dir = "/mnt/wtx_weather_forecast/scx/CMA_DATA/NAFP/EC/C1D/2023/2023123120/"
base_target_dir = "/mnt/wtx_weather_forecast/scx/CMA_DATA/NAFP/EC/C1D"

def map_data(conf):
    UCT = conf[0]
    # UCT = CST + relativedelta(hours=-8)
    UCTstr = UCT.strftime("%Y%m%d%H%M") 
    # 文件名
    file_name = "ECMFC1D_WIV_100"
    source_dir = f"{base_source_dir}/{UCTstr[:4]}/{UCTstr[:10]}/*"
    target_dir = f"{base_target_dir}/{UCTstr[:4]}/{UCTstr[:10]}"
    crDir(target_dir)
    source_fileL = [i for i in glob.glob(source_dir) if "ECMFC1D_WIV_100"  in  i ]
    if not source_fileL:
        return
    source_file = source_fileL[0]
    filename = os.path.basename(source_file)
    target_file = f"{target_dir}/{filename}"
    if os.path.exists(target_file):
        print(f"目标文件已存在: {target_file}")
    else:
        try:
            shutil.copy(source_file, target_dir)
            print(f"文件已成功复制到: {target_file}")
            logger.info(f"文件已成功复制到: {source_file} ---> {target_file}")
        except Exception as e:
            print(f"复制文件时出错: {traceback.format_exc()}")
            logger.error(f"复制文件时出错: {traceback.format_exc()}")
def options():
    parser = argparse.ArgumentParser(description='scx')
    # parser.add_argument('--times', type=str, default='202406290000,202406300000')
    parser.add_argument('--times', type=str, default='202407210000,202407220000')
    parser.add_argument('--pac', type=str, default='100000')
    # parser.add_argument('--combine', action='store_true', default=False)
    parser.add_argument('--combine',action='store_true',default=False)
    parser.add_argument('--isDebug',action='store_true',default=False)
    parser.add_argument('--isDraw',action='store_true',default=False)
    parser.add_argument('--freq', type=str, default="1H")
    parser.add_argument('--tag',type=str, default=datetime.datetime.now().strftime("%Y%m%d%H%M"))
    config= parser.parse_args()
    print(config)
    config.times = config.times.split(",")
    config.pac = config.pac.split(",")
    if len(config.times) == 1:
        config.times = [config.times[0], config.times[0]]
    config.times = [datetime.datetime.strptime(config.times[0], "%Y%m%d%H%M"),
                    datetime.datetime.strptime(config.times[1], "%Y%m%d%H%M")]
    return config
if __name__ == '__main__':
    cfg = options()
    sUTC = cfg.times[0] + relativedelta(hours=-8)
    eUTC = cfg.times[-1] + relativedelta(hours=-8)
    sUTCstr = sUTC.strftime("%Y%m%d")
    cfg = options()
    # 假设 cfg.times[0] 和 cfg.times[-1] 是 datetime 对象 
    # 生成每天的时间序列
    date_range = pd.date_range(start=sUTC.date(), end=eUTC.date(), freq="D")
    # 生成每天 08:00 和 20:00 的时间点
    timeList = []
    for date in date_range:
        timeList.append(date.replace(hour=8, minute=0, second=0, microsecond=0))
        timeList.append(date.replace(hour=20, minute=0, second=0, microsecond=0))

    # 过滤超出范围的时间点
    timeList1 = [t for t in timeList if sUTC <= t <= eUTC]
    logger.info(timeList1)
    # for CST in timeList: 
    try: 
        Mul_sub(map_data,[timeList1],31)
    except Exception as e:
        print(traceback.format_exc())
"""

