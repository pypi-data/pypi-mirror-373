

import netCDF4 as nc
import numpy as np
with nc.Dataset(path) as dataNC:
    # 获取 'time' 变量
    name_data = dataNC.variables[list(dataNC.variables)[0]][:] 
    print(list(dataNC.variables))   
    # 打印时间数据
    name = list(dataNC.variables)[0]
    print(f"{name}数据:")
    print(name_data)

with nc.Dataset(path) as dataNC:
    ref = dataNC["var"][:][::-1]*100
    latArr = dataNC["lat"][:][::-1]
    lonArr = dataNC["lon"][:]

with nc.Dataset(path) as dataNC:
    ref = dataNC["var"][:] 
    latArr = dataNC["lat"][:] 
    lonArr = dataNC["lon"][:]

def readnetCDF4(path):
    with nc.Dataset(path) as dataNC:
        # 获取 'time' 变量
        name_data = dataNC.variables[list(dataNC.variables)[0]][:] 
        print(list(dataNC.variables))   
        # 打印时间数据
        name = list(dataNC.variables)[0]
        print(f"{name}数据:")
        print(name_data)
def readnetCDF4all(path):
    with nc.Dataset(path) as dataNC:
        # 获取 'time' 变量
        print("开始读取呢台CDF4数据")
        print(list(dataNC.variables))  
        for i in list(dataNC.variables):
            name_data = dataNC.variables[i][:]              
            # 打印时间数据
            name = i
            print(f"{name}数据:")
            print(name_data)
         
import pygrib
def grib(path):    
    grbs = pygrib.open(path) #"/mnt/wtx_weather_forecast/gfs_110/20231030/18/gfs.t18z.pgrb2.0p25.f002"
    for grb in grbs:
        print(grb)
import pygrib 
grbs = pygrib.open(path)
for grb in grbs:
    print(f"Message {grb.messagenumber}:")
    print(f"  Parameter: {grb.parameterName} ({grb.shortName})")
    print(f"  Level: {grb.level} ({grb.typeOfLevel})")
    print(f"  Time: {grb.validDate} (forecast time: {grb.forecastTime} hours)")
    print(f"  Grid: {grb.gridType}")
    print(f"  Values shape: {grb.values.shape}")
    print("-" * 50)    
    
path = '/mnt/wtx_weather_forecast/CMA_DATA/NAFP/EC/C1D/2024/2024112720/ECMFC1D_PRTY_1_2024112712_GLB_1_2.grib2'
# grib_ls   /mnt/wtx_weather_forecast/CMA_DATA/NAFP/EC/C1D/2024/2024112720/ECMFC1D_PRTY_1_2024112712_GLB_1_2.grib2
import pygrib as pg
with pg.open(path) as dataPG:
    # for i in dataPG:
    #     print(i)
    preInfo = dataPG.select(shortName="ptype")[0] 
    latMat,lonMat = preInfo.latlons()
    latMat = latMat[::-1]
    lonMat = lonMat[::-1]
    latArr = latMat[:,0]
    lonArr = lonMat[0]
    pre = preInfo.values
    pre = pre[::-1]

grbs = pg.open(path) #"/mnt/wtx_weather_forecast/gfs_110/20231030/18/gfs.t18z.pgrb2.0p25.f002"
for grb in grbs:
    print(grb)
grbs.close()
 
import json
import gzip
import pandas as pd
# Assuming the file is a gzipped JSON
file_path = '/mnt/wtx_weather_forecast/scx/GeoEnvData/rawData/ZW_1.gz'
with gzip.open(file_path, 'rt') as file:  # 'rt' mode to read as text
    data = json.load(file)

# Normalize JSON data into a DataFrame
df = pd.json_normalize(data)


"""

import h5py

file_path = "/mnt/wtx_weather_forecast/zhangshuo/QYDL/DATA/GPM/3B-HHR-L.MS.MRG.3IMERG.20241001-S000000-E002959.0000.V07B.HDF5"

def inspect_file(file_path):
    with h5py.File(file_path, 'r') as f:
        print("文件结构:")
        def print_objects(name, obj):
            if isinstance(obj, h5py.Dataset):
                print(f"  Dataset: {name} (Shape: {obj.shape}, Dtype: {obj.dtype})")
            elif isinstance(obj, h5py.Group):
                print(f"  Group: {name}")
        f.visititems(print_objects)

inspect_file(file_path)
 
##############################
import h5py
import numpy as np

file_path = "/mnt/wtx_weather_forecast/zhangshuo/QYDL/DATA/GPM/3B-HHR-L.MS.MRG.3IMERG.20241001-S000000-E002959.0000.V07B.HDF5"

def read_precipitation(file_path):
    with h5py.File(file_path, 'r') as f:
        # 读取降水数据（形状: (1, 3600, 1800)）
        precip = np.array(f['Grid/precipitation'][0, :, :])  # 去掉时间维度
        
        # 读取坐标
        lons = np.array(f['Grid/lon'])      # 经度 (3600,)
        lats = np.array(f['Grid/lat'])      # 纬度 (1800,)
        
        # 处理无效值
        fill_value = f['Grid/precipitation'].attrs.get('_FillValue', -9999.0)
        precip[precip == fill_value] = np.nan
        
        # 获取单位
        units = f['Grid/precipitation'].attrs.get('units', 'mm/h')
        
        return {
            "precipitation": precip,  # 形状: (3600, 1800)
            "longitude": lons,       # 经度数组
            "latitude": lats,        # 纬度数组
            "units": units           # 单位（如 mm/h）
        }

# 调用函数
data = read_precipitation(file_path)
print(f"降水数据形状: {data['precipitation'].shape}")
print(f"经度范围: {data['longitude'].min()} ~ {data['longitude'].max()}")
print(f"纬度范围: {data['latitude'].min()} ~ {data['latitude'].max()}")
  
"""


"""

path = '/mnt/wtx_weather_forecast/CMA_DATA/NAFP/EC/C1D/2024/2024112720/ECMFC1D_PRTY_1_2024112712_GLB_1_2.grib2'
# grib_ls   /mnt/wtx_weather_forecast/CMA_DATA/NAFP/EC/C1D/2024/2024112720/ECMFC1D_PRTY_1_2024112712_GLB_1_2.grib2
import pygrib as pg
with pg.open(path) as dataPG:
    # for i in dataPG:
    #     print(i)
    preInfo = dataPG.select(shortName="ptype",stepRange="0")[0] 
    latMat,lonMat = preInfo.latlons()
    latMat = latMat[::-1]
    lonMat = lonMat[::-1]
    latArr = latMat[:,0]
    lonArr = lonMat[0]
    pre = preInfo.values
    pre = pre[::-1]

path = '/mnt/wtx_weather_forecast/CMA_DATA/NAFP/EC/C1D/2024/2024112720/ECMFC1D_PRTY_1_2024112712_GLB_1_2.grib2'
# grib_ls   /mnt/wtx_weather_forecast/CMA_DATA/NAFP/EC/C1D/2024/2024112720/ECMFC1D_PRTY_1_2024112712_GLB_1_2.grib2  查看select 参数
import pygrib as pg
with pg.open(path) as dataPG:
    # for i in dataPG:
    #     print(i)
    preInfo = dataPG.select(shortName="ptype",stepRange="0")[0] 
    latMat,lonMat = preInfo.latlons()
    # latMat = latMat[::-1]
    # lonMat = lonMat[::-1]
    latArr = latMat[:,0]
    lonArr = lonMat[0]
    pre = preInfo.values
d_clip = clip(data[ivar_name], env, latArr[0], lonArr[0], 0.25)    
# d = zoom(d_clip, [4201/169,6201/249], order=1)[:-1, :-1]
data.update({'lon':lon})
data.update({'lat': lat})
return d_clip
"""

"""

import netCDF4 as nc

# 设定NetCDF文件的路径
path = 'your_file.nc'  # 请替换为您的实际文件路径

# 打开NetCDF文件
with nc.Dataset(path) as dataNC:
    # 获取所有变量的名称
    variables = dataNC.variables.keys()    
    # 输出所有变量
    print("变量列表:")
    for var in variables:
        print(var)

with nc.Dataset(path) as dataNC:
    for var_name in dataNC.variables:
        var = dataNC.variables[var_name]
        print(f"变量名称: {var_name}")
        print(f"数据类型: {var.dtype}")
        print(f"维度: {var.dimensions}")
        print(f"属性: {var.__dict__}")
        print()  # 打印空行以

# 设定NetCDF文件的路径
path = 'your_file.nc'  # 请替换为您的实际文件路径

with nc.Dataset(path) as dataNC:
    time_data = dataNC.variables['time'][:]    
    # 打印时间数据
    print("时间数据:")
    print(time_data)
    # 如果需要转换为可读的日期时间格式
    time_units = dataNC.variables['time'].units
    print(f"时间单位: {time_units}")

    # 如果单位是 "days since YYYY-MM-DD" 形式，进行转换
    if "days since" in time_units:
        base_time = nc.num2date(time_data, units=time_units)
        print("转换后的时间数据:")
        for t in base_time:
            print(t)

"""

