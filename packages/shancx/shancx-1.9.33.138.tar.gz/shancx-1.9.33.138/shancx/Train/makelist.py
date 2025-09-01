
def save_results(results, output_file, mode='w',title="input_path,tar_path"):  
    with open(output_file, mode) as f:
        if mode == 'w':  
            f.write(f"{title}\n")
        for result in results:
            f.write(f"{result['input_path']},{result['tar_path']}\n")
"""
output_file = "rmse_results.txt"
save_results([], output_file, mode='w')
result = {
          'input_path': input_path ,
          'tar_path': tar_path 
          }
save_results([result], output_file, mode='a')  

df = pd.read_csv(csv_file, sep=" ",header=None)   
sample_list = df.values.tolist()
self.paths = {
    "input_path": [l[0] for l in self.sample_list],
    "gt_path": [l[1] for l in self.sample_list]
}
"""    
import os
import numpy as np
import pandas as pd
import glob
import datetime
from shancx import Mul_sub_S,Mul_sub 
from shancx import crDir
def getcheckdata(conf):
    satPath = conf[0]
    radar_dir_path = conf[1]
    sat_imin = conf[2]
    try:
        satdata = np.load(satPath)
        radarpth = glob.glob(f"{radar_dir_path}/{sat_imin[:4]}/{sat_imin[:8]}/CR_{satPath.split('/')[-1][4:-4]}*.npy")[0]
        radardata = np.load(radarpth)
        if radardata.shape != satdata.shape :
            return  
        df = pd.DataFrame({'sat_path': [satPath], 'radar_path': [radarpth] })
        return df
    except Exception as e:
        print(f"{satPath} can not load succeed: {e}")
        return None
def generateList(conf):
    sat_dir_path, radar_dir_path, sat_imin= conf
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
import argparse
import datetime
import pandas as pd
def options():
    parser = argparse.ArgumentParser(description='examdatabasedata')
    parser.add_argument('--times', type=str, default='202502010000,202506220000') 
    parser.add_argument('--flag', type=str, default='val') 
    config= parser.parse_args()
    print(config)
    config.times = config.times.split(",")
    if len(config.times) == 1:
        config.times = [config.times[0], config.times[0]]
    config.times = [datetime.datetime.strptime(config.times[0], "%Y%m%d%H%M"),
                    datetime.datetime.strptime(config.times[1], "%Y%m%d%H%M")]
    return config
"""
if __name__ == '__main__':
    cfg = options()
    sUTC = cfg.times[0]
    eUTC = cfg.times[-1]
    flag = cfg.flag     
    sat_dir_path ="./"
    radar_dir_path = f"./"
    timelist = pd.date_range(sUTC, eUTC, t=f"{flag}")
    timeListfliter = timelist[timelist.month.isin([1,4,7,10])&(timelist.day<=15)]
    savepath = f'/mnt/wtx_weather_forecast/SAT/GOES18train_N/0624_1' 
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
        crDir(savepath)
        train_df.to_csv(f"{savepath}/df_train.csv", index=False, sep=',')
        print(f"train_df {len(train_df)}")
        print('complete!!!') 
        print(savepath)
    if  flag == "val":
        valid_df = pd.concat(dataLs)  
        crDir(savepath)
        valid_df.to_csv(f"{savepath}/df_valid.csv", index=False, sep=',')
        print(f"valid_df {len(valid_df)}")
        print('complete!!!')
        print(savepath)   
        

"""
"""
import os
import numpy as np
import pandas as pd
import glob
import datetime
from shancx import Mul_sub_S,Mul_sub 
from shancx import crDir
def getcheckdata(conf):
    inputPath = conf[0]
    target_dir_path = conf[1]
    imin = conf[2]
    try:
        inputdata = np.load(inputPath)
        targetpth = glob.glob(f"{target_dir_path}/{imin[:4]}/{imin[:8]}/analy_{inputPath.split('/')[-1][3:-4]}*.npy")[0]
        targetdata = np.load(targetpth)
        if inputdata.shape != targetdata.shape :
            return  
        df = pd.DataFrame({'inputPath': [inputPath], 'targetpth': [targetpth] })
        return df
    except Exception as e:
        print(f"{inputPath} can not load succeed: {e}")
        return None
def generateList(conf):
    imin,input_dir_path, target_dir_path= conf
    imin = imin.strftime("%Y%m%d%H%M")
    targetpath = glob.glob(f"{input_dir_path}/{imin[:4]}/{imin[:8]}/EC_{imin}_*.npy")
    targetpath.sort()
    if targetpath:
        datas = []
        for path in targetpath:
            data = getcheckdata( (path,target_dir_path,imin))
            datas.append(data)
        datass = [i for i in datas if i is not None ]
        if datass :
            df = pd.concat(datass)
            return df
    else:
            return None 
import argparse
import datetime
import pandas as pd
def options():
    parser = argparse.ArgumentParser(description='examdatabasedata')
    parser.add_argument('--times', type=str, default='202505210030,202505210130') 
    parser.add_argument('--flag', type=str, default='val') 
    parser.add_argument('--freq', type=str, default="1h") 
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
    freq = cfg.freq     
    input_dir_path ="/mnt/wtx_weather_forecast/scx/smart_grid/train/clip_EC"
    target_dir_path = f"/mnt/wtx_weather_forecast/scx/smart_grid/train/analy_1_256"
    timelist = pd.date_range(sUTC, eUTC, freq=f"{freq}")
    timeListfliter = timelist[timelist.month.isin([1,4,5,7,10])]
    timeListfliter = list(timeListfliter)
    savepath = f'/mnt/wtx_weather_forecast/SAT/downscale/0901' 
    crDir(savepath)
    # 调用方法    1.split_time   2. timelist  3. 路径
 
    dataL = Mul_sub(generateList,[ timeListfliter,[input_dir_path] , [target_dir_path]] )          
    dataLs = [i for i in dataL if i is not None]  
    pd.concat(dataLs).to_csv('train.txt', sep=' ', index=False)
    a = pd.read_csv("./train.txt",sep=" ").values.tolist()
"""
        
 