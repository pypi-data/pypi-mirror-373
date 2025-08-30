
import netCDF4 as nc
import numpy as np
def getPoint(pre, df, lat0, lon0, resolution, decimal=1):
    latIdx = ((lat0 - df["Lat"]) / resolution + 0.5).astype(np.int64)
    lonIdx = ((df["Lon"] - lon0) / resolution + 0.5).astype(np.int64)
    return pre[...,latIdx, lonIdx].round(decimals=decimal)
def Get_Lat_Lon_QPF(path,Lon_data,Lat_data):
    with nc.Dataset(path) as dataNC:
        latArr = dataNC["lat"][:]
        lonArr = dataNC["lon"][:]
        if "AIW_QPF" in  path:
            pre = dataNC[list(dataNC.variables.keys())[3]][:]    
        elif "AIW_REF" in path:
            pre = dataNC[list(dataNC.variables.keys())[4]][:]   
    data = getPoint(pre , {"Lon":Lon_data,"Lat":Lat_data} , latArr[0], lonArr[0], 0.01)
    data = getPoint(pre , {"Lon":Lon_data,"Lat":Lat_data} , latArr[0], lonArr[0], 0.01)
    return data

"""   pip index  设置
mkdir .pip 进入文件夹  vim pip.conf  粘贴保存
[global]
index_url=https://pypi.tuna.tsinghua.edu.cn/simple
"""
"""
zoom插值
from scipy.ndimage import zoom
d = zoom(d_clip, [4201/169,6201/249], order=1)[:-1, :-1]
"""
"""
import multiprocessing
multiprocessing.set_start_method('fork', force=True)   #fork  #spawn

"""

"""  区域切割
import xarray as xr
ds = xr.open_dataset(a)
# # 定义经纬度范围
# lon_min, lon_max = 72.0, 136.96
# lat_min, lat_max = 6.04, 54.0
# 定义经纬度范围
ds = ds.sortby('latitude') 
lon_min, lon_max = 73, 134.99
lat_min, lat_max = 12.21, 54.2  #[73,134.99,12.21,54.2] 
# 现在可以进行数据截取
subset = ds.sel(longitude=slice(lon_min, lon_max), latitude=slice(lat_min, lat_max))   # 
H9 = subset["data"][::-1,:]

longitude_values = subset['longitude'].values
latitude_values = subset['latitude'].values

print("裁剪后的经度范围：", longitude_values.min(), longitude_values.max())
print("裁剪后的纬度范围：", latitude_values.min(), latitude_values.max())

# 裁剪后的数据信息
data_values = subset['data'].values
data_attrs = subset['data'].attrs

print("裁剪后的数据形状：", subset['data'].shape)
print("裁剪后的数据值：", data_values)
print("数据的属性信息：", data_attrs)

"""
###用于回算
"""
from main import makeAll,options
from multiprocessing import Pool
import datetime
from config import logger,output
import time
import pandas as pd
import os
from itertools import product
import threading
from shancx import Mul_sub
def excuteCommand(conf):
    cmd = conf[0]
    print(cmd)
    os.system(cmd)

if __name__ == '__main__':
    cfg = options()
    isPhase = cfg.isPhase
    isDebug = cfg.isDebug
    sepSec = cfg.sepSec
    gpu = cfg.gpu
    pool = cfg.pool
    isOverwrite = cfg.isOverwrite
    timeList = pd.date_range(cfg.times[0], cfg.times[-1], freq=f"{sepSec}s")
    logger.info(f"时间段check {timeList}")
    gpuNum = 2
    eachGPU = 4
    makeListUTC = []
    for UTC in timeList:
        UTCStr = UTC.strftime("%Y%m%d%H%M")
        outpath = f"{output}/{UTCStr[:4]}/{UTCStr[:8]}/MSP2_WTX_AIW_QPF_L88_CHN_{UTCStr}_00000-00300-00006.nc"
        if not os.path.exists(outpath) or not os.path.exists(outpath.replace("_QPF_","_REF_"))  or isOverwrite:
            makeListUTC.append(UTC)
    [print(element) for element in makeListUTC]
    phaseCMD = "--isPhase" if isPhase else ""
    debugCMD = "--isDebug" if isDebug else ""
    OverwriteCMD = "--isOverwrite"
    gpuCMD = f"--gpu={gpu}"
    # cmdList = list(map(lambda x:f"python main.py --times={x.strftime('%Y%m%d%H%M')} {phaseCMD} {debugCMD} {OverwriteCMD} {gpuCMD}",makeListUTC))
    cmdList = list(map(lambda x:f"python main.py --times={x.strftime('%Y%m%d%H%M')} {phaseCMD} {debugCMD} {gpuCMD}",makeListUTC))
    if cmdList:
        Mul_sub(excuteCommand, [cmdList], pool)
    else: 
        print("cmdList is empty, skipping the call.")
        raise ValueError("cmdList is empty, cannot execute command.")
CUDA_LAUNCH_BLOCKING=1 python makeHis.py --times 202410010048,202410110048 --gpu=0 --isDebug --sepSec 3600 --pool 5
CUDA_LAUNCH_BLOCKING=1 python makeHis1.py --times 202410010048,202410110048 --gpu=0 --isDebug --sepSec 3600 --pool 5
"""
"""
import shutil
def GetMulData(conf):
    UTC = conf[0]
    UTCStr = UTC.strftime("%Y%m%d%H%M%S") 
    outpath = f"{GradarNA}/{UTCStr[:4]}/{UTCStr[:8]}/"
    # if os.path.exists(outpath):
    #     print(f"outpath {outpath} is existed ")
    #     return 
    path = f"{GLobradar}/{UTCStr[:4]}/{UTCStr[:8]}/CR_NA_{UTCStr[:12]}.nc" 
    if not os.path.exists(path):
        print(f"outpath {path} is not existsing ")
        return False
    else:
        crDir(outpath)        
    try:
        shutil.copy(path, outpath)  # 自动保留文件名
        print(f"文件已复制到: {outpath}")
        return True
    except Exception as e:
        print(f"复制失败: {e}")
        return False
"""
###用于循环出日报
"""
#!/bin/bash
start_date="20241001"
end_date="20241101"
tag="scx/MQPF_Gan5_default_1112N"
current_date=$(date -d "$start_date" +%Y%m%d)
end_date=$(date -d "$end_date" +%Y%m%d)
while [ "$current_date" != "$end_date" ]; do
    start_time="$current_date"0000
    end_time="$current_date"2359
    python makeDOC_newv2.py --times $start_time,$end_time --tag $tag
    current_date=$(date -d "$current_date + 1 day" +%Y%m%d)
done
python makeDOC_newv2.py --times $end_date"0000",$end_date"2359" --tag $tag
"""
"""
frile name :launch.json
args:
{
    "version": "0.2.0",
    "configurations": [   
        {
            "name": "Python: Current File",
            "type": "debugpy",
            "request": "launch",
            "program": "${file}",
            "console": "integratedTerminal",
            "cwd": "${fileDirname}",
            "purpose": ["debug-in-terminal"],
            "justMyCode": false,
            "args": [  
                "--times", "202409160000,202409180000" 
            ]
        }
    ]
}

{
    "version": "0.2.0",
    "configurations": [   

        {
            "name": "Python: Current File",
            "type": "debugpy",
            "request": "launch",
            "program": "${file}",
            "console": "integratedTerminal",
            "cwd": "${fileDirname}",
            "purpose": ["debug-in-terminal"],
            "justMyCode": false,
            "args": [
            "--times", "202410010042,202410020042",
            "--isDebug" ,
            "--isOverwrite", 
            "--sepSec", "3600",
            "--gpu", "0"
            ]
        }
    ]
}

"""

"""
import importlib
def get_obj_from_str(class_path: str):
    module_name, class_name = class_path.rsplit('.', 1)    
    module = importlib.import_module(module_name)    
    return getattr(module, class_name)
config = {
    "target": "torch.nn.Linear",  # 类路径
    "params": {                  # 参数字典
        "in_features": 128,
        "out_features": 64
    }
}

# 使用配置字典动态实例化对象
target_class = get_obj_from_str(config["target"])  # 获取类（torch.nn.Linear）
model = target_class(**config.get("params", dict()))  # 使用解包的参数实例化

# 打印结果
print(model)

import torch
import torch.nn as nn
linear = nn.Linear(in_features=128, out_features=64, bias=True)配置字典动态传参
"""

"""
ImportError: /lib64/libc.so.6: version `GLIBC_2.28' not found (required by /home/scx1/miniconda3/envs/mqpf/lib/python3.10/site-packages/lxml/etree.cpython-310-x86_64-linux-gnu.so)
pip uninstall lxml
pip install lxml
"""
"""
001  key: "ee90f313-17b2-4e3d-84b8-3f9c290fa596"
002  far_po "f490767c-27bc-4424-9c75-2b33644171e2"
003  数据监控 "4c43f4bd-d984-416d-ac82-500df5e3ed86"
sendMESplus("测试数据",base=user_info)
"""

'''
from multiprocessing import Pool
'''
'''
 ##定義一個streamHandler
# print_handler = logging.StreamHandler()  
# print_handler.setFormatter(formatter) 
# loggers.addHandler(print_handler)
'''
'''
# @Time : 2023/09/27 下午8:52
# @Author : shanchangxi
# @File : util_log.py
import time
import logging  
from logging import handlers
 
logger = logging.getLogger()
logger.setLevel(logging.INFO) 
log_name =  'project_tim_tor.log'
logfile = log_name
time_rotating_file_handler = handlers.TimedRotatingFileHandler(filename=logfile, when='D', encoding='utf-8')
time_rotating_file_handler.setLevel(logging.INFO)   
formatter = logging.Formatter("%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s")
time_rotating_file_handler.setFormatter(formatter)
logger.addHandler(time_rotating_file_handler)
print_handler = logging.StreamHandler()   
print_handler.setFormatter(formatter)   
logger.addHandler(print_handler)
'''
'''
###解决方法  pip install torch==2.4.0  torchvision    torchaudio三个同时安装  python 3.12  解决cuda启动不了的问题
Res网络
'''
'''
import concurrent.futures
from itertools import product
def task(args):
    args1,args2  = args
    print( f"Task ({args1}, {args2}) , result")
    return (args1,args2,5)

def Mul_sub(task, pro):
    product_list = product(*pro)
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [executor.submit(task, item) for item in product_list]
    results = [future.result() for future in concurrent.futures.as_completed(futures)]   
    return results
res = Mul_sub(task, [[1, 23, 4, 5], ["n"]])
print("res")
print(res)
'''

"""
find /mnt/wtx_weather_forecast/scx/SpiderGLOBPNGSource -type f -name "*.png" -mtime +3 -exec rm {} \;
-mtime 选项后面的数值代表天数。
+n 表示“超过 n 天”，即查找最后修改时间在 n 天之前的文件。
"""
"""
from shancx.SN import UserManager,sendMESplus
from shancx._info import users 
M = UserManager(info=users)
user_info = M.get_user("003") 
sendMESplus("测试数据",base=user_info)
"""
"""
https://api.map.baidu.com/lbsapi/getpoint/index.html  坐标
[global]
index-url = https://pypi.tuna.tsinghua.edu.cn/simple   pip.conf
python setup.py sdist bdist_wheel
twine upload dist/*
"""
"""   与循环搭配使用   
    for key,value in dictflag.items():
        try:
            pac = all_df1[all_df1['PAC'].str.startswith(f'{key}')]
            acctoal,acctoalEC,matEC,mat,rate_Lift_ratiotsEC,outpath= metriacfunall(pac)
            if not len(matEC.shape) == (2,2):
               continue             
            docdataset =  mkdataset2TS(acctoal,acctoalEC,matEC,mat, rate_Lift_ratiotsEC,outpath)
    
        except Exception as e:
            print(traceback.format_exc())  
            continue
"""

"""

cuda-version              11.8                 hcce14f8_3
cudatoolkit               11.8.0               h6a678d5_0
cudnn                     8.9.2.26               cuda11_0
nvidia-cuda-cupti-cu12    12.1.105                 pypi_0    pypi
nvidia-cuda-nvrtc-cu12    12.1.105                 pypi_0    pypi
nvidia-cuda-runtime-cu12  12.1.105                 pypi_0    pypi
nvidia-cudnn-cu12         8.9.2.26                 pypi_0    pypi
mqpf conda install pytorch  torchvision torchaudio  cudatoolkit=11.8 -c pytorch  
conda install cudnn=8.9.2.26 cudatoolkit=11.8 
resunet pip install torch==2.4.0  torchvision    torchaudio
conda install cudnn==8.9.2.26 cudatoolkit==11.8.0
conda install pytorch=2.2.2 torchvision torchaudio cudatoolkit=11.8 -c pytorch
resunet pip install torch==2.4.0  torchvision    torchaudio
pip install protobuf==3.20

my-envmf1
torch                     2.3.0                    pypi_0    pypi
torchvision               0.18.0                   pypi_0    pypi

RES:
torch                     2.4.0                    pypi_0    pypi
torchaudio                2.2.2                 py311_cpu    pytorch
torchsummary              1.5.1                    pypi_0    pypi
torchvision               0.19.0                   pypi_0    pypi

mqpf:
torch                     2.3.1                    pypi_0    pypi
torchaudio                2.3.1                    pypi_0    pypi
torchvision               0.18.1                   pypi_0    pypi
onnxruntime-gpu           1.16.0
onnx                      1.15.0 
numpy                     1.26.4

vllm:
torch                     2.1.2                    pypi_0    pypi
torchvision               0.15.1+cu118             pypi_0    pypi
vllm                      0.2.7                    pypi_0    pypi

import torch
print("CUDA available:", torch.cuda.is_available())
print("CUDA version:", torch.version.cuda)
print("GPU device:", torch.cuda.get_device_name(0) if torch.cuda.is_available() else "No GPU")
nvidia-smi 
nvcc --version
系统已经检测到物理 GPU（NVIDIA GeForce RTX 4090）和 NVIDIA 驱动，同时安装了 CUDA 12.1。然而，PyTorch 没有正确检测到 GPU，可能是因为 PyTorch 版本与 CUDA 驱动不兼容，或者环境变量未正确配置。

pip install torch==2.3.1    torchvision==0.18.1  

conda install -c conda-forge cudatoolkit=11.8 --force-reinstall   解决报错
ls $CONDA_PREFIX/lib/libcublasLt.so.11
:ProviderLibrary::Get() [ONNXRuntimeError] : 1 : FAIL : Failed to load library libonnxruntime_providers_cuda.so with error: libcublasLt.so.11: cannot open shared object file: No such file or directory
export LD_LIBRARY_PATH=$CONDA_PREFIX/lib:$LD_LIBRARY_PATH
"""
"""
conda env export > environment.yml
conda env create -f /path/to/destination/environment.yml
conda activate your_env_name

conda install -c conda-forge conda-pack
conda pack -n aiw -o my_env.tar.gz
mkdir -p my_env
tar -xzf my_env.tar.gz -C my_env
source my_env/bin/activate
"""
"""
定时任务

MAILTO="shanhe12@163.com"

""" 
"""
vgg_loss = VGGLoss(weights_path="/mnt/wtx_weather_forecast/scx/stat/sat/sat2radar/vgg19-dcbb9e9d.pth").to(device)
SAMloss = SAMLoss(model_type='vit_b', checkpoint_path='/mnt/wtx_weather_forecast/scx/stat/sat/sat2radar/sam_vit_b_01ec64.pth.1').to(device)
"""

"""
sdata = xr.open_dataset(sat_paths)
sdata["time"] = sUTC
edata = xr.open_dataset(sat_pathe)
edata["time"] = UTC
sdata = sdata.assign_coords(time=sUTC)
edata = edata.assign_coords(time=UTC)
添加维度和更新已有维度数据
sdata = xr.open_dataset(sat_paths).rename({"time": "old_time"})
edata = xr.open_dataset(sat_pathe).rename({"time": "old_time"})
# 现在可以安全添加新时间坐标
sdata = sdata.assign_coords(time=sUTC)
edata = edata.assign_coords(time=UTC)
UTC = datetime.datetime.strptime(self.nowDate, "%Y%m%d%H%M")  注意时间格式
"""
"""
#sudo mkdir -p /mnt/wtx_weather_forecast/GeoEnvData/rawData/MeteoL/Himawari/H9
#sudo mount -t nfs nfs.300s.ostor:/mnt/ifactory_public/AWS_data/AWS_data/Himawari /mnt/wtx_weather_forecast/GeoEnvData/rawData/MeteoL/Himawari/H9  
"""

"""
groups
sudo gpasswd -d user sudo  # 从 sudo 组移除用户 "user"
id
sudo usermod -u 1001 user
sudo usermod -g 1001 user
sudo chown -R 新用户名:新组名 目录名/

sudo find / -user 1015 -exec chown 1001 {} \;

more  /etc/passwd
vim 修改 /etc/passwd

"""
"""
    latArr = np.linspace(env.n, env.s, int(round((env.n - env.s) / 0.02)) + 1)
    lonArr = np.linspace(env.w, env.e, int(round((env.e - env.w) / 0.02)) + 1)
"""
"""
find /mnt/wtx_weather_forecast/SAT/H9/Radar_ncSEAS/trainNN/2025/ -mindepth 2 -maxdepth 2 -type d
find /mnt/wtx_weather_forecast/SAT/H9/Radar_ncSEAS/trainNN/2025/ -mindepth 2 -maxdepth 2 -type d -exec rm -rf {} +
find /mnt/wtx_weather_forecast/SAT/H9/Radar_ncSEAS/trainNN/2025/ -mindepth 2 -maxdepth 2 -type d -not -name "important" -exec rm -rf {} +
find /mnt/wtx_weather_forecast/SAT/H9/Radar_ncSEAS/trainNN/2025/202[0-9][0-9][0-9][0-9]/ -mindepth 1 -maxdepth 1 -type d -exec rm -rf {} +
"""
"""
sudo chmod -R 777 /mnt/wtx_weather_forecast/scx/MSG/MSG_Data

"""

"""


import os
import numpy as np
import pandas as pd
import glob
import datetime
from hjnwtx.mkNCHJN import mkDir
from shancx import Mul_sub_S,Mul_sub
from shancx.Plot import plotRadar,plotMat,plotA2b
from shancx.Time import gen_dt

# from shancx.Time import timeCycle
from shancx import crDir
from config import staMSGtrain0611,crMSGtrain0611
from shancx.wait import check_nans
# 将 getcheckdata 移到模块顶层
satflag = "MSG"
def getcheckdata(conf):
    iph = conf[0]
    radar_dir_path = conf[1]
    sat_imin = conf[2]
    try:
        satdata = np.load(iph)
        radarpth = glob.glob(f"{radar_dir_path}/{sat_imin[:4]}/{sat_imin[:8]}/CR_{iph.split('/')[-1][4:-4]}*.npy")[0]
        radardata = np.load(radarpth)
        if radardata.shape != (1, 256, 256) or satdata.shape != (6, 256, 256) :
            return 
        if np.nanmean(radardata) > 20  or np.nanmean(satdata) > 280 :
            plotMat(satdata[0],name=f"satdata{satflag}_{sat_imin}")
            plotRadar(satdata[0],name=f"radar{satflag}_{sat_imin}")
            return 
        flagnan = check_nans(satdata,threshold=0)
        if flagnan:
            # plotA2b(satdata[:3],satdata[3:])
            radio = np.isnan(satdata).sum()/satdata.size    
            if radio>0.0001 and radio <0.01:
                plotA2b(satdata[:3],satdata[3:],saveDir="plotA2bN")
            return                
                
        df = pd.DataFrame({'sat_path': [iph], 'radar_path': [radarpth] })
        return df
    except Exception as e:
        print(f"{iph} can not load succeed: {e}")
        return None

def generateList(conf):
    sat_dir_path, radar_dir_path, sat_imin= conf
    if True:
        satpath = glob.glob(f"{sat_dir_path}/{sat_imin[:4]}/{sat_imin[:8]}/SAT_{sat_imin}_*.npy")
        satpath.sort()
        if satpath:
            datas = []
            for path in satpath:
                data = getcheckdata( (path,radar_dir_path,sat_imin))
                datas.append(data)
            datass = [i for i in datas if i is not None ]
            if datass :
                df = pd.concat(datass)
                return df
        else:
            return None    

import datetime as dt
import pandas as pd
def ldom(d):  # last day of month
    if d.month == 12:
        return d.replace(year=d.year+1, month=1, day=1) - dt.timedelta(days=1)
    return d.replace(month=d.month+1, day=1) - dt.timedelta(days=1)
import datetime as dt
import pandas as pd
def ldomN(d):  # last day of month
    USTstr = d.strftime('%Y%m%d%H%M')
    datag = f"{sat_dir_path}/{USTstr[:4]}/{USTstr[:6]}*"
    datapath = glob.glob(datag)[-2:]
    datar = []
    if datapath:
        for i in datapath:
            daytime1 = i.split("/")[-1]
            daytime=  datetime.datetime.strptime(daytime1, "%Y%m%d")
            daytime = daytime.day
            datar.append(daytime)
    return datar
 
def gen_dt(s, e, t="trn",freq='30min'):  # generate dates
    dr = pd.date_range(start=s, end=e, freq=freq)
    res = []    
    for d in dr:
        me = ldomN(d) if t == "val" else ldom(d)
        is_me = d.day in me    
        if (t == "trn" and not is_me) or (t == "val" and is_me):
            res.append(d.strftime('%Y%m%d%H%M'))    
    return res

import argparse
import datetime
import pandas as pd
def options():
    parser = argparse.ArgumentParser(description='examdatabasedata')
    parser.add_argument('--times', type=str, default='202501010000,202506060000') 
    parser.add_argument('--flag', type=str, default='val') 
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
    sUTC = cfg.times[0]
    eUTC = cfg.times[-1]
    flag = cfg.flag 
    sat_dir_path = staMSGtrain0611
    radar_dir_path = f"{crMSGtrain0611}_256"  
    timelist = gen_dt(sUTC, eUTC, t=f"{flag}")
    # start_time = datetime.datetime(2024,6,5,1)
    # end_time =   datetime.datetime(2024,6,5,5)
    # timelist = gen_dt(start_time, end_time, t=f"{flag}")
    savepath = f'/mnt/wtx_weather_forecast/SAT/MSG/MSGtrain_N/0611' 
    crDir(savepath)

    # 调用方法    1.split_time   2. timelist  3. 路径
    dataL = Mul_sub(generateList,[ [sat_dir_path]
                          , [radar_dir_path]
                          , timelist
                          ] 
            )            
    dataLs = [i for i in dataL if i is not None]    
    if  flag =="trn":
        train_df = pd.concat(dataLs) 
        mkDir(savepath)
        train_df.to_csv(f"{savepath}/df_train.csv", index=False, sep=',')
        print(f"train_df {len(train_df)}")
        print('complete!!!') 
        print(savepath)
    if  flag == "val":
        valid_df = pd.concat(dataLs)  
        mkDir(savepath)
        valid_df.to_csv(f"{savepath}/df_valid.csv", index=False, sep=',')
        print(f"valid_df {len(valid_df)}")
        print('complete!!!')
        print(savepath)

"""

"""
def map_fun(conf):
        UTC = conf[0]
        logger.info(UTC)
        try :
            dP = drawPng(UTC)
            if not dP.envList is None:
                for i, env in enumerate(dP.envList):
                    CR = dP.CR[:,::4,::4]
                    CRc = clip(CR, env, dP.latArr[0], dP.lonArr[0], 0.04)
                    latArrc = clipLat(dP.latArr, env, 0.04)
                    lonArrc = clipLon(dP.lonArr, env, 0.04)
                    CRc[CRc < 5] = np.nan
                    statDt = clip(dP.df_Mat[:,:-1,:-1], env, dP.latArr[0], dP.lonArr[0], 0.04)
                    dP.makeDS(CRc,statDt, env,cfg.size)
        except Exception as e:
            logger.error(f"{UTC} error {e}")            
            logger.info(traceback.format_exc())
            print(traceback.format_exc())
        return 
        
        

    def getCheckArea(self, eps):
        '''
        split area
        :param UTC:
        :param eps:
        :return:
        '''

        ret, img_thre = cv2.threshold(self.CR[0][::4,::4], 1, 255, cv2.THRESH_BINARY)
        img_thre = img_thre.astype(np.uint8)
        contours, hierarchy = cv2.findContours(img_thre, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
        validcontours = list(filter(lambda x: len(x) > 35, contours))
        logger.info(f"回波连通域{len(validcontours)}个")
        xyList = []
        for v in validcontours:
            # print(validcontours[i])
            xy = np.asarray(v).squeeze()
            xyList.append(xy)
            # plt.plot(xy[:,0],CR.shape[0]-xy[:,1])
        #
        # plt.show()
        xyList = np.concatenate(xyList)

        rectangles = testDBscan(xyList, eps)
        envList = []
        for r in rectangles:
            [(wI, sI), (eI, nI)] = r
            # plt.imshow(CR[sI:nI, wI:eI])
            # plt.show()
            n = np.round(self.latArr[0] - sI * 0.04, 2)
            s = np.round(self.latArr[0] - nI * 0.04, 2)
            w = np.round(self.lonArr[0] + wI * 0.04, 2)
            e = np.round(self.lonArr[0] + eI * 0.04, 2)
            env = envelope(n, s, w, e)
            # CRc = clip(CR,en,latArr[0],lonArr[0],0.01)
            # plt.imshow(CRc)
            # plt.show()
            envList.append(env)
        logger.info(f"最终区域{len(envList)}个")
        return envList


class drawPng():
    def __init__(self, UTC):
        self.UTC = UTC
        self.UTCStr = UTC.strftime("%Y%m%d%H%M")
        self.eps = 20
        self.CR, self.latArr, self.lonArr = self.getCR()
        self.envCHN = envelope(54.2, 12.21, 73, 134.99)
        self.envList = None
        self.df_Mat = self.makeStat()
        if not self.CR is None:
            self.envList = self.getCheckArea(self.eps)

"""
"""
conda install conda-forge::cudatoolkit==11.8.0
"""
"""
# 删除 scx 用户（同时删除家目录）
sudo userdel -r scx
# 再删除 scx 组
sudo groupdel scx
# 重新创建组（GID=1015）
sudo groupadd -g 1015 scx
# 重新创建用户（UID=1015，GID=1015）
sudo useradd -u 1015 -g scx -m -s /bin/bash scx
# 设置密码
sudo passwd scx
# 赋予 sudo 权限
sudo usermod -aG sudo scx
2. 如果不想删除用户，可以修改用户的主组
bash
# 查看 scx 用户当前的主组
id scx
# 修改 scx 用户的主组为其他组（如 users）
sudo usermod -g users scx
# 现在可以删除 scx 组
sudo groupdel scx
# 重新创建 scx 组（GID=1015）
sudo groupadd -g 1015 scx
# 修改 scx 用户的主组回 scx
sudo usermod -g scx scx
验证
bash
id scx
预期输出：
text
uid=1015(scx) gid=1015(scx) groups=1015(scx),27(sudo)

groupmod -g 1016 scx
sudo usermod -u 1015 scx
# 修改用户的主组（GID）
sudo usermod -g scx scx
# 确保家目录权限正确
sudo chown -R scx:scx /home/scx
"""
"""
    from hjnwtx.mkNCHJN import dataClass, mkNCCommonUni,envelope,timeSeq,mkDir
    env = envelope(35,10,108,125)
    step = 0.01
    latArr = np.linspace(env.n, env.s, int(round((env.n - env.s) / step)) + 1)
    lonArr = np.linspace(env.w, env.e, int(round((env.e - env.w) / step)) + 1) 
    a = np.full([2501, 1701], np.nan)
    # a = torch.full([2501, 1701], float('nan'))
        
    a[:2280,:] = CR  CR  shape (2280,1701)  a shape  (3501,1701) 
    a[:2280, :] = np.maximum(a[:2280, :], CR[:2280, :])  
"""
"""
find . -type d -empty -delete
find  /mnt/wtx_weather_forecast/scx/GOES -type f -name "*.txt" -mmin +300 -delete ;
"""
"""
82.export TERMINFO=/lib/terminfo
81.ERROR: Failed to initialize `curses` (setupterm: could not find terminfo database)
"""
"""
mask = (mask_data == 0).to(device)
"""