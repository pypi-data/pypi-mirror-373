import xarray as xr
import numpy as np
def convert_longitude(nc_input_path, nc_output_path):
    ds = xr.open_dataset(nc_input_path)
    lon = 'lon'
    if lon not in ds.coords:
        raise ValueError("输入文件中没有'lon'坐标")
    ds[lon] = xr.where(ds[lon] > 180, ds[lon] - 360, ds[lon])
    ds = ds.sortby(lon)
    ds = ds.sortby('lat', ascending=False)
    ds.to_netcdf(nc_output_path)
    print(f"成功将数据转换并保存到 {nc_output_path}")
convert_longitude('CMORPH2_0.25deg-30min_202410160100.RT.nc', 'CMORPH2_0.25deg-30min_202410160100.RT_N.nc')

import netCDF4 as nc
import numpy as np
with nc.Dataset(path) as dataNC:
    hourlyPrecipRateGC = dataNC["hourlyPrecipRateGC"][:] 
    latArr = dataNC["Latitude"][:]  
    lonArr = dataNC["Longitude"][:] 
    latArr_flipped = latArr[::-1]
    hourlyPrecipRateGC_flipped = hourlyPrecipRateGC[::-1, :]

with nc.Dataset(path) as dataNC:
    ref = dataNC["var"][:][::-1]  # 读取数据并翻转第一个维度（通常是纬度）
    latArr = dataNC["lat"][:][::-1]  # 翻转纬度数组
    lonArr = dataNC["lon"][:]  # 


import netCDF4 as nc
with nc.Dataset(path) as dataNC:
    # 翻转数据的纬度维度
    ref = dataNC["var"][:][::-1]  # 假设第一个维度是纬度    
    # 翻转纬度数组
    latArr = dataNC["lat"][:][::-1]    
    # 经度转换：从 [0, 359] 转换为 [-179, 179]
    lonArr = dataNC["lon"][:]
    lonArr = ((lonArr + 180) % 360) - 180  # 将 [0, 359] 转换为 [-180, 180)    
    # 排序经度数组，并相应调整数据
    lon_order = lonArr.argsort()  # 获取排序索引
    lonArr = lonArr[lon_order]    # 按照索引重新排序经度数组
    ref = ref[:, lon_order]       # 重新排序数据的经度维度
