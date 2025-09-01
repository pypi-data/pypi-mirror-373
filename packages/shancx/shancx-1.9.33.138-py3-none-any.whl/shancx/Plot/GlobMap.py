import matplotlib.pyplot as plt
import numpy as np
import datetime
from hjnwtx.colormap import cmp_hjnwtx  # Assuming this is your custom colormap library
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import cartopy.io.shapereader as shpreader
import os
from shancx import crDir

def Glob(array_dt=None,cd="CHN",ty="CR",colorbarflag="add"):
    if cd == "g":
        env = [-179.617020, 179.632979,-85.098871,85.051128] 
    elif cd == "US":
        env = [-132.0, -47.0, 0, 57.0]
    elif cd == "CHN":
        env = [73,134.99,12.21,54.2]   
    else:
         env = cd
    now_str = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    outpath = f"./radar_nmc/{str(cd)}_{now_str}.png"
    crDir(outpath)
    # Create figure and set the coordinate system
    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(1, 1, 1, projection=ccrs.PlateCarree())
    # Set the extent for the United States
    ax.set_extent(env, ccrs.PlateCarree())  # Adjust as needed
    # Add the US map boundaries and features
    add_glob_map(ax)    
    # Add data layers
    if  len(array_dt.shape) == 2 and ty =="pre":
        ax.imshow(array_dt, vmin=0, vmax=10, cmap=cmp_hjnwtx["pre_tqw"], transform=ccrs.PlateCarree(), extent=env)   
        if colorbarflag is not None :
           plt.colorbar(ax.images[0], ax=ax, orientation='vertical',shrink=0.7)
        plt.savefig(outpath)
    else :
        ax.imshow(array_dt, vmin=0, vmax=72, cmap=cmp_hjnwtx["radar_nmc"], transform=ccrs.PlateCarree(), extent=env)
        if colorbarflag is not None :
           plt.colorbar(ax.images[0], ax=ax, orientation='vertical',shrink=0.7)
        plt.savefig(outpath)
    plt.close(fig)

def add_glob_map(ax): 
    ax.add_feature(cfeature.COASTLINE, edgecolor='gray')
    ax.add_feature(cfeature.BORDERS, linestyle=':', edgecolor='gray')
    ax.add_feature(cfeature.LAKES, alpha=0.8)    
    # Adding state boundaries
    if os.path.exists('/home/scx/ne_10m_admin_1_states_provinces.shp'):
        states = '/home/scx/ne_10m_admin_1_states_provinces.shp'
    else:
        states = shpreader.natural_earth(resolution='10m', category='cultural', name='admin_1_states_provinces')  # Automatically download 
    states_features = shpreader.Reader(states).geometries()    
    ax.add_geometries(states_features, ccrs.PlateCarree(), facecolor='none', edgecolor='gray', linestyle=':', linewidth=0.5, alpha=0.8)
 
def GlobLonLat(array_dt=None,Lon=None,Lat=None,cd="CHN",ty="CR",colorbarflag="add"):   ###  x_coords2 维度 
    if cd == "g":
        env = [-179.617020, 179.632979,-85.098871,85.051128] 
    elif cd == "US":
        env = [-132.0, -47.0, 0, 57.0]
    elif cd == "CHN":
        env = [73,134.99,12.21,54.2]   #[73, 134.99, 12.21, 54.2] 
    else:
         env = cd    
    now_str = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    if array_dt is None :
        array_dt = np.full([4200,6200],np.nan)
    outpath = f"./radar_nmc/{str(cd)}_{now_str}.png"
    crDir(outpath)

    # Create figure and set the coordinate system
    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(1, 1, 1, projection=ccrs.PlateCarree())

    # Set the extent for the United States
    ax.set_extent(env, ccrs.PlateCarree())  # Adjust as needed

    # Add the US map boundaries and features
    add_glob_map(ax)
    
    # Add data layers
    if  len(array_dt.shape) == 2 and ty =="pre":
        ax.imshow(array_dt, vmin=0, vmax=10, cmap=cmp_hjnwtx["pre_tqw"], transform=ccrs.PlateCarree(), extent=env)   
        if colorbarflag is not None :
           plt.colorbar(ax.images[0], ax=ax, orientation='vertical',shrink=0.7)
        ax.scatter(list(Lon), list(Lat), s=0.5, c='red', marker='o', transform=ccrs.PlateCarree())
    else :
        ax.imshow(array_dt, vmin=0, vmax=72, cmap=cmp_hjnwtx["radar_nmc"], transform=ccrs.PlateCarree(), extent=env)
        ax.scatter(list(Lon), list(Lat), s=0.5, c='red', marker='o', transform=ccrs.PlateCarree())
        if colorbarflag is not None :
           plt.colorbar(ax.images[0], ax=ax, orientation='vertical',shrink=0.7)        
    plt.tight_layout()
    plt.savefig(outpath)
    plt.close(fig)

def add_us_map(ax):
    ax.add_feature(cfeature.COASTLINE, edgecolor='gray')
    ax.add_feature(cfeature.BORDERS, linestyle=':', edgecolor='gray')
    ax.add_feature(cfeature.LAKES, alpha=0.8)    
    # Adding state boundaries
    if os.path.exists('/home/scx/ne_10m_admin_1_states_provinces.shp'):
        states = '/home/scx/ne_10m_admin_1_states_provinces.shp'
    else:
        states = shpreader.natural_earth(resolution='10m', category='cultural', name='admin_1_states_provinces')  # Automatically download 
    states_features = shpreader.Reader(states).geometries()    
    ax.add_geometries(states_features, ccrs.PlateCarree(), facecolor='none', edgecolor='gray', linestyle=':', linewidth=0.5, alpha=0.8)

# Example usage
# Assuming array_dt is your data array, pass it to drawUS
# array_dt = np.random.rand(3, 100, 100)  # Example random data; replace with your actual data
# drawUS(array_dt)

def GlobLonLatPlus(array_dt=None,Lon=None,Lat=None,cd="CHN",ty="CR",name="temp",markcolor="red",outpath1=None):   ###  x_coords2 维度 
    if cd == "g":
        env = [-179.617020, 179.632979,-85.098871,85.051128] 
    elif cd == "US":
        env = [-132.0, -47.0, 0, 57.0]
    elif cd == "CHN":
        env = [73,134.99,12.21,54.2]   #[73, 134.99, 12.21, 54.2] 
    else:
         env = cd    
    now_str = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    if array_dt is None :
        array_dt = np.full([4200,6200],np.nan)
    outpath = f"./radar_nmc/{str(cd)}_{now_str}_{name}.png"
    if outpath1 is not None:
       outpath = outpath1  
    crDir(outpath)
    # Create figure and set the coordinate system
    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(1, 1, 1, projection=ccrs.PlateCarree())

    # Set the extent for the United States
    ax.set_extent(env, ccrs.PlateCarree())  # Adjust as needed

    # Add the US map boundaries and features
    add_glob_map(ax)
    
    # Add data layers
    if  len(array_dt.shape) == 2 and ty =="pre":
        ax.imshow(array_dt, vmin=0, vmax=10, cmap=cmp_hjnwtx["pre_tqw"], transform=ccrs.PlateCarree(), extent=env)   
        ax.scatter(list(Lon), list(Lat), s=0.5, c=f'{markcolor}', marker='o', transform=ccrs.PlateCarree())
        plt.colorbar(ax.images[0], ax=ax, orientation='vertical',shrink=0.7)
        plt.savefig(outpath)
    else :
        ax.imshow(array_dt, vmin=0, vmax=72, cmap=cmp_hjnwtx["radar_nmc"], transform=ccrs.PlateCarree(), extent=env)
        ax.scatter(list(Lon), list(Lat), s=0.5, c=f'{markcolor}', marker='o', transform=ccrs.PlateCarree())
        plt.colorbar(ax.images[0], ax=ax, orientation='vertical',shrink=0.7)
        plt.savefig(outpath)
    plt.close(fig)

def add_us_map(ax):
    ax.add_feature(cfeature.COASTLINE, edgecolor='gray')
    ax.add_feature(cfeature.BORDERS, linestyle=':', edgecolor='gray')
    ax.add_feature(cfeature.LAKES, alpha=0.8)    
    # Adding state boundaries
    if os.path.exists('/home/scx/ne_10m_admin_1_states_provinces.shp'):
        states = '/home/scx/ne_10m_admin_1_states_provinces.shp'
    else:
        states = shpreader.natural_earth(resolution='10m', category='cultural', name='admin_1_states_provinces')  # Automatically download 
    states_features = shpreader.Reader(states).geometries()    
    ax.add_geometries(states_features, ccrs.PlateCarree(), facecolor='none', edgecolor='gray', linestyle=':', linewidth=0.5, alpha=0.8)

# Example usage
# Assuming array_dt is your data array, pass it to drawUS
# array_dt = np.random.rand(3, 100, 100)  # Example random data; replace with your actual data
# drawUS(array_dt)

import matplotlib.font_manager as fm
zh_font_path = '/mnt/wtx_weather_forecast/scx/fonts/truetype/simhei.ttf'   
zh_font = fm.FontProperties(fname=zh_font_path)
def GlobLonLatPluss(array_dt,Lon,Lat,Lon1,Lat1,cd="CHN",ty="CR",name="temp",markcolor="red",outpath1=None):   ###  x_coords2 维度 
    if cd == "g":
        env = [-179.617020, 179.632979,-85.098871,85.051128] 
    elif cd == "US":
        env = [-132.0, -47.0, 0, 57.0]
    elif cd == "CHN":
        env = [73,134.99,12.21,54.2]   #[73, 134.99, 12.21, 54.2] 
    else:
         env = cd    
    now_str = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    outpath = f"./radar_nmc/{str(cd)}_{now_str}_{name}.png"
    array_dt = np.where(array_dt>0,array_dt,np.nan)
    if outpath1 is not None:
       outpath = outpath1  
    crDir(outpath)
    # Create figure and set the coordinate system
    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(1, 1, 1, projection=ccrs.PlateCarree())

    # Set the extent for the United States
    ax.set_extent(env, ccrs.PlateCarree())  # Adjust as needed

    # Add the US map boundaries and features
    add_glob_map(ax)    
    # Add data layers
    if  len(array_dt.shape) == 2 and ty =="pre":
        ax.imshow(array_dt, vmin=0, vmax=10, cmap=cmp_hjnwtx["pre_tqw"], transform=ccrs.PlateCarree(), extent=env)   
        ax.scatter(list(Lon), list(Lat), s=0.5, c=f'{markcolor}', marker='o', transform=ccrs.PlateCarree())
    else :
        ax.imshow(array_dt, vmin=0, vmax=72, cmap=cmp_hjnwtx["radar_nmc"], transform=ccrs.PlateCarree(), extent=env)
        sc1 = ax.scatter(list(Lon), list(Lat), s=2, c=f'blue', marker='o', transform=ccrs.PlateCarree(),edgecolor='black', linewidth=0.3,label="维天信相对彩云漏报 ")
        sc2 = ax.scatter(list(Lon1), list(Lat1), s=2, c=f'red', marker='o', transform=ccrs.PlateCarree(),edgecolor='black', linewidth=0.3,label="共同漏报 ")
        plt.colorbar(ax.images[0], ax=ax, orientation='vertical',shrink=0.8)
        plt.title(f"{name}")
        ax.legend(loc='upper left', fontsize='small', prop=zh_font)  # 您可以根据需要调整字体大小和位置
    plt.savefig(outpath)
    plt.close(fig)

def add_us_map(ax):
    ax.add_feature(cfeature.COASTLINE, edgecolor='gray')
    ax.add_feature(cfeature.BORDERS, linestyle=':', edgecolor='gray')
    ax.add_feature(cfeature.LAKES, alpha=0.8)    
    # Adding state boundaries
    if os.path.exists('/home/scx/ne_10m_admin_1_states_provinces.shp'):
        states = '/home/scx/ne_10m_admin_1_states_provinces.shp'
    else:
        states = shpreader.natural_earth(resolution='10m', category='cultural', name='admin_1_states_provinces')  # Automatically download 
    states_features = shpreader.Reader(states).geometries()    
    ax.add_geometries(states_features, ccrs.PlateCarree(), facecolor='none', edgecolor='gray', linestyle=':', linewidth=0.5, alpha=0.8)

def globPng(d2,ty=None):
    import numpy as np
    import matplotlib.pyplot as plt
    import cartopy.crs as ccrs
    import cartopy.feature as cfeature
    from hjnwtx.colormap import cmp_hjnwtx
    from shancx.Time import UTCStr
    CSTstr = UTCStr()
    data = d2[::10,::10]  # shape: (height, width)
    lat_min, lat_max = -90, 90
    lon_min, lon_max = -180, 180
    fig = plt.figure(figsize=(15, 10))
    ax = fig.add_subplot(111, projection=ccrs.PlateCarree())
    im = ax.imshow(data, 
                  extent=[lon_min, lon_max, lat_min, lat_max],
                  cmap=cmp_hjnwtx["radar_nmc"],
                  transform=ccrs.PlateCarree())
    if ty == "pre":
       im = ax.imshow(data, 
                    extent=[lon_min, lon_max, lat_min, lat_max],
                    vmin=0, 
                    vmax=10,
                    cmap=cmp_hjnwtx["pre_tqw"],
                    transform=ccrs.PlateCarree())
    ax.add_feature(cfeature.COASTLINE, linewidth=0.8, zorder=2)
    ax.add_feature(cfeature.BORDERS, linestyle=':', linewidth=0.6, zorder=2)
    ax.add_feature(cfeature.STATES, linestyle=':', linewidth=0.4, alpha=0.5, zorder=2)
    ax_pos = ax.get_position()    
    # 设置色标与主图严格对齐
    cax = fig.add_axes([
        ax_pos.x1 + 0.01,  # 主图右侧+0.01的间距
        ax_pos.y0,         # 与主图底部对齐
        0.02,              # 色标宽度
        ax_pos.height      # 与主图同高度
    ])
    
    cbar = plt.colorbar(im, cax=cax)
    cbar.set_label('Echo Intensity (dBZ)', fontsize=12, labelpad=10)
    cbar.ax.tick_params(labelsize=10)
    plt.subplots_adjust(
        left=0.05, 
        right=0.85,  # 减小right值以容纳色标
        top=0.95,
        bottom=0.125
    )
    ax.set_title('Global Radar', 
                fontsize=18, 
                pad=25, 
                weight='bold')
    ax.set_xlabel('Longitude', fontsize=12, labelpad=10)
    ax.set_ylabel('Latitude', fontsize=12, labelpad=15)
    plt.savefig(f"global_radar_aligned_{CSTstr}.png", 
               dpi=300, 
               bbox_inches='tight', 
               facecolor='white')
    plt.close()