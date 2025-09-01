import numpy as np
from netCDF4 import Dataset
from scipy.spatial import cKDTree
import os

def fill_missing_idw(variable, lat, lon, power=2, max_neighbors=8):
    filled_variable = variable.copy()
    ny, nx = variable.shape
    if isinstance(variable, np.ma.MaskedArray):
        known_mask = ~variable.mask
        missing_mask = variable.mask
        known_values = variable.data[known_mask]
    else:
        known_mask = ~np.isnan(variable)
        missing_mask = np.isnan(variable)
        known_values = variable[known_mask]
    known_points = np.column_stack((lon[known_mask], lat[known_mask]))
    missing_points = np.column_stack((lon[missing_mask], lat[missing_mask]))
    if len(known_points) == 0:
        print("There are no known points available for interpolation.")
        return filled_variable
    if len(missing_points) == 0:
        print("There are no missing points to fill.")
        return filled_variable
    tree = cKDTree(known_points)
    distances, indexes = tree.query(missing_points, k=max_neighbors)
    if distances.size == 0 or indexes.size == 0:
        print("There are no valid neighbor points for interpolation.")
        return filled_variable
    if max_neighbors == 1:
        distances = distances[:, np.newaxis]
        indexes = indexes[:, np.newaxis]
    with np.errstate(divide='ignore'): 
        weights = 1 / distances**power
    weights[~np.isfinite(weights)] = 0  
    weight_sums = np.sum(weights, axis=1)
    weight_sums[weight_sums == 0] = 1  
    interpolated_values = np.sum(weights * known_values[indexes], axis=1) / weight_sums
    exact_matches = distances[:, 0] == 0
    if np.any(exact_matches):
        interpolated_values[exact_matches] = known_values[indexes[exact_matches, 0]]
    filled_variable[missing_mask] = interpolated_values
    n_filled = np.sum(~missing_mask)
    print(f"尝试填补了 {len(missing_points)} 个缺失点，成功填补了 {n_filled} 个。")    
    return filled_variable
def process_nc_file(input_path, output_path):
    with Dataset(input_path, 'r') as src:
        with Dataset(output_path, 'w', format=src.file_format) as dst:
            dst.setncatts({attr: src.getncattr(attr) for attr in src.ncattrs()})
            for dim_name, dim in src.dimensions.items():
                dst.createDimension(dim_name, len(dim) if not dim.isunlimited() else None)
            for var_name, var in src.variables.items():
                fill_value = getattr(var, '_FillValue', None)
                dst_var = dst.createVariable(var_name, var.datatype, var.dimensions, fill_value=fill_value)
                dst_var.setncatts({attr: var.getncattr(attr) for attr in var.ncattrs()})
                data = var[:]
                if var_name in ['CR']:
                    if data.ndim == 3: 
                        filled_data = np.ma.array(data) 
                        lat = src.variables['lat'][:]
                        lon = src.variables['lon'][:]
                        for t in range(data.shape[0]):
                            print(f"Processing time index {t} for variable {var_name}")
                            var_data = data[t, :, :]
                            if not isinstance(var_data, np.ma.MaskedArray):
                                var_data = np.ma.masked_where(np.isnan(var_data), var_data)
                            filled_var = fill_missing_idw(var_data, lat, lon)
                            filled_data[t, :, :] = filled_var
                        fill_val = getattr(var, '_FillValue', np.nan)
                        dst_var[:] = filled_data.filled(fill_val)
                    else:
                        raise ValueError(f"Variable {var_name} 维度不符合预期，预期为 3D 但实际为 {data.ndim}D。")
                else:
                    dst_var[:] = data
    print(f"The data after filling has been saved to {output_path}")
if __name__ == "__main__":
    input_nc = "/mnt/wtx_weather_forecast/scx/WTX_DATA/RADA/MQPF_1204_diffu12/2024/20240908/MSP2_WTX_AIW_REF_L88_CHN_202409080448_00000-00300-00006.nc"
    output_nc = "1aaa_filled.nc"
    if not os.path.exists(input_nc):
        print(f"输入文件 {input_nc} 不存在。")
    else:
        process_nc_file(input_nc, output_nc)
