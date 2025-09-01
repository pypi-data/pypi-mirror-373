import numpy as np
from scipy.interpolate import griddata
def getPoint(field,lats=None,lons=None,obs_lats=None,obs_lons=None):
    lon_mesh, lat_mesh = np.meshgrid(lons, lats)
    grid_points = np.column_stack([lon_mesh.ravel(), lat_mesh.ravel()])
    interp_values = griddata(grid_points, field.ravel(), (obs_lons, obs_lats), method='linear')
    valid_mask = ~np.isnan(interp_values)
    return interp_values[valid_mask]
"""
nlat, nlon = background.shape
lons = np.linspace(-180, 180, nlon, endpoint=False)
lats = np.linspace(90, -90, nlat)
obs_lats = df["lat"]
obs_lons = df["lon"]
"""  
from scipy.spatial import cKDTree
def mask_KDTree(grid_lon, grid_lat, lon_points, lat_points, step_lonlat=0.2):
    grid_shape = grid_lon.shape
    grid_coords = np.column_stack((grid_lon.ravel(), grid_lat.ravel()))
    thunder_points = np.column_stack((lon_points, lat_points))
    tree = cKDTree(thunder_points)
    indices = tree.query_ball_point(grid_coords, r = step_lonlat)
    mask_flat = np.zeros(len(grid_coords), dtype=int)
    for i, neighbors in enumerate(indices):
        if len(neighbors) >= 1:
            mask_flat[i] = 1
    mask_flat = mask_flat.reshape(grid_shape)
    return mask_flat

"""
lon_points = df_sta['lon']
lat_points = df_sta['lat']
grid_lon = th.lon.data
grid_lat = th.lat.data
grid_lon,grid_lat = np.meshgrid(grid_lon, grid_lat)  
grid_marked = mask_KDTree(grid_lon, grid_lat, lon_points, lat_points, step_lonlat=0.5) step_lonlat 度数 0.01代表1公里
"""