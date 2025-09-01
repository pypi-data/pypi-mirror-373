

import numpy as np
class Bounds:
    def __init__(self, north, south, west, east):
        self.n = north  # 北边界
        self.s = south  # 南边界
        self.w = west   # 西边界
        self.e = east   # 东边界

    def __str__(self):
        return f"n:{self.n}, s:{self.s}, w:{self.w}, e:{self.e}"

def calc_idx(start_val, bound_val, step, data_len):
    idx = int(np.round(abs(start_val - bound_val) / step + 0.5, 3))
    return max(0, min(idx, data_len - 1))

def clip(data, bound_start, bound_end, step, pad=False):
    idx_start = calc_idx(data[0], bound_start, step, len(data))
    idx_end = calc_idx(data[0], bound_end, step, len(data))
    if idx_start > idx_end:
        idx_start, idx_end = idx_end, idx_start
    if pad:
        if data[idx_start] < bound_start and idx_start > 0:
            idx_start -= 1
        if data[idx_end] > bound_end and idx_end < (len(data) - 1):
            idx_end += 1
    return data[idx_start:idx_end + 1]

def clip_lat(bounds, step, pad=False):
    # 使用 np.linspace 生成纬度数组
    lat = np.linspace(90, -90, int(180 / step) + 1)  # 从 90 到 -90，步长为 step
    return clip(lat, bounds.n, bounds.s, step, pad)

def clip_lon(bounds, step, pad=False):
    # 使用 np.linspace 生成经度数组
    lon = np.linspace(-180, 180, int(360 / step) + 1)  # 从 -180 到 180，步长为 step
    return clip(lon, bounds.w, bounds.e, step, pad)
 
"""
if __name__ == "__main__":
    from shancx.Clip import Bounds,clip_lat,clip_lon
    bounds = Bounds(65, -65, 40, 170)
    lat_clipped = clip_lat(bounds, 0.04)
    print(f"Clipped Latitude Data Length: {len(lat_clipped)}")
    lon_clipped = clip_lon(bounds, 0.04)
    print(f"Clipped Longitude Data Length: {len(lon_clipped)}")
"""

 