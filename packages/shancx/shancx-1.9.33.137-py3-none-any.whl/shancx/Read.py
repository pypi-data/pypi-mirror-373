import pygrib
import numpy as np
import pandas as pd
def readGrib(file_path, target_param=None):
    try:
        with pygrib.open(file_path) as grbs:
            field_info = []
            for grb in grbs:
                field_info.append({
                                   'messageNumber': grb.messagenumber,
                                   'parameterName': getattr(grb, 'parameterName', 'N/A'),
                                   'shortName': getattr(grb, 'shortName', 'N/A'),
                                   'level': getattr(grb, 'level', -999),
                                   'typeOfLevel': getattr(grb, 'typeOfLevel', 'N/A'),
                                   'validDate': getattr(grb, 'validDate', 'N/A'),
                                   'units': getattr(grb, 'units', 'N/A'),
                                   'shape': grb.values.shape
                                 })             
            if target_param:
                try:
                    grb = grbs.select(shortName=target_param)[0]
                except:
                    try:
                        grb = grbs.select(parameterName=target_param)[0]
                    except:
                        raise ValueError(f"未找到参数: {target_param}")
            else:
                grb = grbs[1]
            data = grb.values
            lats, lons = grb.latlons()            
            return {
                'data': data,
                'lats': lats,
                'lons': lons,
                'metadata': {
                    'parameterName': grb.parameterName,
                    'level': grb.level,
                    'validDate': grb.validDate,
                    'units': grb.units
                }
            }            
    except Exception as e:
        print(f"GRIB读取错误: {str(e)}")
        return None
if __name__ == "__main__":
    path = "/mnt/wtx_weather_forecast/CMA_DATA/NAFP/EC/C1D/2024/2024112720/ECMFC1D_PRTY_1_2024112712_GLB_1_2.grib2"
    result = readGrib(path)    
    if result:
        print("\n数据矩阵形状:", result['data'].shape)
        print("经度范围:", np.min(result['lons']), "~", np.max(result['lons']))
        print("纬度范围:", np.min(result['lats']), "~", np.max(result['lats']))
        print("参数单位:", result['metadata']['units'])
        """
        latArr = latMat[:,0]
        lonArr = lonMat[0]
        """    
import yaml
def _load_config(config_path: str) :
    """加载YAML配置文件"""
    print(f"load config file Get configuration parameters: {config_path}")
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    return config