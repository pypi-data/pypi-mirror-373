import matplotlib.pyplot as plt
import datetime
from hjnwtx.colormap import cmp_hjnwtx
import time
import os
import time
import shutil
 
from dateutil.relativedelta import relativedelta
import glob
from config import logger
import argparse
import pandas as pd 
import re
import netCDF4 as nc 
from multiprocessing import Pool
from itertools import product
import numpy as np
import copy
import traceback

 
from multiprocessing import Process, Queue
 
import io
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import cartopy.io.shapereader as shpreader
from hjnwtx.mkNCHJN import mkDir

shape_ = (1, 5701, 8501)
def add_china_map(ax):
    # 在地图上添加地形特征
    ax.add_feature(cfeature.COASTLINE, edgecolor='gray')
    ax.add_feature(cfeature.BORDERS, linestyle=':', edgecolor='gray')
    ax.add_feature(cfeature.LAKES, alpha=0.8)
    # 添加省份轮廓
    provinces = shpreader.natural_earth(resolution='10m', category='cultural', name='admin_1_states_provinces')
    provinces_features = shpreader.Reader(provinces).geometries()
    ax.add_geometries(provinces_features, ccrs.PlateCarree(), facecolor='none', edgecolor='gray', linestyle=':', linewidth=0.5, alpha=0.8)
 
def draw_subplot(args):
    env = [-132.0, -47.0, 0, 57.0]
    index, tp, vmax, vmin, cmap,time_index, name = args
    # print(time_index)
    # logger.info(f"Processing index: {index}")
    # logger.info(time_index)
    fig, ax = plt.subplots(figsize=(10, 10))

    # 创建绘图和设置坐标系
    # fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(1, 1, 1, projection=ccrs.PlateCarree())

    # 设置图像显示的范围
    ax.set_extent(env, ccrs.PlateCarree())  # 根据需要调整

    # 添加中国地图的边界和特征，包括省份轮廓
    add_china_map(ax)
    tp = np.where(tp >= 0.1, tp, np.nan)
    ax.imshow(tp, vmin=0, vmax=10, cmap=cmp_hjnwtx["pre_tqw"], transform=ccrs.PlateCarree(), extent=env, alpha=1) 

    # ax.imshow(tp, vmax=vmax, vmin=vmin, cmap=cmap)
    ax.axis('off')
    # ax.text(0.5, 0.5, str(index), transform=ax.transAxes, color='white', fontsize=20, ha='center', va='center')
    ax.text(0.95, 0.95, f'{time_index}', transform=ax.transAxes, color='white', fontsize=20, ha='right', va='bottom')
    ax.text(0.925, 0.925, f'{str(index)}', transform=ax.transAxes, color='white', fontsize=20, ha='right', va='top')
    fig.tight_layout()

    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)   
    plt.close(fig)
    return (index, buf)   #返回两个数为元组
 
# 修改读取部分
def drawpic(tp, Count,timeList, name="temp"):
    vmax = 70
    vmin = 0
    cmap = cmp_hjnwtx["radar_nmc"]
    args_list = [ (index, tp[index, :, :], vmax, vmin, cmap,timeList[index], name)  for index in range(2 * Count)]
    
    with Pool(31) as pool:
        results = pool.map(draw_subplot, args_list)
    
    buffers = [result[1] for result in results]
    combined_fig, axs = plt.subplots(2, Count, figsize=(10 * Count, 20))
    for i in range(2):
        for j in range(Count):
            index = i * Count + j
            ax = axs[i, j]
            ax.imshow(plt.imread(buffers[index]), cmap=cmap)
            ax.axis('off')
    
    now_str = datetime.datetime.now().strftime("%Y%m%d%H%M")
    plt.tight_layout()
    outpath = f"./{timeList[0].strftime('%Y%m%d%H%M')}_MQPF/{name}_{now_str}.png"
    mkDir(outpath)
    plt.savefig(outpath)
    plt.close(combined_fig)


 
BASE_TARGET_PATH = "/mnt/wtx_weather_forecast/WTX_DATA/RADA/MQPF_GLB"   #/mnt/wtx_weather_forecast/WTX_DATA/RADA/MQPF_PMSC
# BASE_TARGET_PATH = "/mnt/wtx_weather_forecast/WTX_DATA/RADA/MQPF_PMSC"   #/mnt/wtx_weather_forecast/WTX_DATA/RADA/MQPF_PMSC

def get_mqpf_paths(UCTstr):
    year = UCTstr[:4]
    date = UCTstr[:8]
    mqpfPath_pattern = os.path.join(BASE_TARGET_PATH,year, date,f"MSP2_WTX_AIW_QPF_L88_NA_{UCTstr}_00000-00300-00006.nc")  #MSP2_WTX_AIW_QPF_L88_NA_202410222254_00000-00300-00006.nc
    # mqpfPath_pattern = os.path.join(BASE_TARGET_PATH,year, date,f"MSP2_WTX_AIW_MQPF_L88_CHN_{UCTstr}_00000-00300-00006.nc")
 
    return mqpfPath_pattern  

def map_data(conf):
    CST = conf[0]
    UCT = CST + relativedelta(hours=-8)
    UCTstr = UCT.strftime("%Y%m%d%H%M")
    mqpfPath_pattern = get_mqpf_paths(UCTstr)
    mqpfPath_list = glob.glob(mqpfPath_pattern)
    if len(mqpfPath_list) == 0:
        data_loss = re.findall(r"(2024\d{8}?)",mqpfPath_pattern)
        print("data_loss",data_loss)
        print("data_loss_path",mqpfPath_pattern)
        tj_list.append(data_loss[0]) 
        return np.full(shape_, np.nan)
    else:
        try:
            with nc.Dataset(mqpfPath_list[0]) as dataNC:
                mqpf = dataNC.variables["MQPF"][:]
                mqpf = mqpf[:1]
                if mqpf.shape != shape_:
                    logger.info(mqpf.shape )
                    logger.info(mqpfPath_list[0])
                    print("mqpf shape error",mqpf.shape)
                    mqpf = mqpf[:,:-1, :-1]
                    if mqpf.shape != shape_:
                       return np.full(shape_, np.nan)      
                    else:
                        return mqpf          
                print("mqpf",UCTstr,mqpf.shape)
            tj_list1.append(mqpfPath_pattern)
            return mqpf
        except Exception as e:
            print(traceback.format_exc())
            return np.full(shape_, np.nan)
 
def options():
    parser = argparse.ArgumentParser(description='plot radar')
    # parser.add_argument('--times', type=str, default='202406290000,202406300000')
    parser.add_argument('--times', type=str, default='202407310000,202408010000')
    parser.add_argument('--pac', type=str, default='100000')
    # parser.add_argument('--combine', action='store_true', default=False)
    parser.add_argument('--combine',action='store_true',default=False)
    parser.add_argument('--isDebug',action='store_true',default=False)
    parser.add_argument('--isDraw',action='store_true',default=False)
    parser.add_argument('--freq', type=str, default="1h")
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
    sCST = cfg.times[0]
    eCST = cfg.times[-1]
    sCSTstr = sCST.strftime("%Y%m%d")
    tj_list = []
    tj_list1= []
    start = datetime.datetime.now()
    logger.info(f"{sCST}")    
    logger.info(f"{eCST}")    
    logger.info(f"PNG")    
    timeList = pd.date_range(sCST,eCST,freq="360s",inclusive="left")
    # for CST in timeList:  
    productList = product(timeList)
    with Pool(31) as p:
         Data = p.map(map_data,productList)
    end = datetime.datetime.now()
    print(start-end)
    Data_con = np.concatenate(Data,axis=0) 
    loss_len = 240 - Data_con.shape[0]
    sCSTstr = sCST.strftime("%Y%m%d")
    eCSTstr = eCST.strftime("%Y%m%d")
    # Data_con1 = Data_con.filled()  
    # np.save(f"data_{sCSTstr}_{eCSTstr}.npy",Data_con1) 
    Data_con_120 = copy.copy(Data_con)
    drawpic(Data_con_120[:int(len(Data_con_120)/2)], int(len(Data_con_120)/4),timeList[:int(len(Data_con_120)/2)],name=f"temp120_{sCSTstr}_loss_{loss_len}_")
    print("done 120")
    end1 = datetime.datetime.now()
    print(end1-end)
    Data_con_240 = copy.copy(Data_con)
    print(Data_con_240[120:].shape)
    drawpic(Data_con_120[int(len(Data_con_120)/2):], int(len(Data_con_120)/4),timeList[int(len(Data_con_120)/2):],name=f"temp120_240_{sCSTstr}_{loss_len}_")
    print(datetime.datetime.now()-end1)
    print("done 120-240") 
    logger.info("success")
 

#  "/mnt/wtx_weather_forecast/WTX_DATA/RADA/MQPF/2024/20240704/MSP2_WTX_AIW_REF_L88_CHN_202407040324_00000-00300-00006.nc"

