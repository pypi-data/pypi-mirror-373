
import matplotlib as mpl 
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import geopandas as gpd
from cartopy.mpl.ticker import LongitudeFormatter,LatitudeFormatter
import numpy as np
from shancx import crDir
def plot_fig(cr,nclat,nclon,fig_title,datatype=None,savepath=None,font_path=None,shp_file=None):
    figpath = f"{savepath}/fig/{fig_title.split('_')[1][:4]}/{fig_title.split('_')[1][:8]}/{fig_title.split('_')[1][:12]}/{fig_title}.PNG"
    # if not os.path.exists(figpath):
    lonmin = np.min(nclon)
    lonmax = np.max(nclon)
    latmin = np.min(nclat)
    latmax = np.max(nclat)
    myfont = mpl.font_manager.FontProperties(fname = font_path, size = 12) 
    fig = plt.figure(figsize=(6,6))
    ax = plt.axes(projection=ccrs.PlateCarree())
    ax.set_xticks(np.arange(lonmin, lonmax + 0.1, 15))
    ax.set_yticks(np.arange(latmin, latmax + 0.1, 10))
    ax.set_xlim([lonmin, lonmax])
    ax.set_ylim([latmin, latmax])
    ax.xaxis.set_major_formatter(LongitudeFormatter()) #刻度格式转换为经纬度样式                       
    ax.yaxis.set_major_formatter(LatitudeFormatter())
    ax.tick_params(axis = 'both',labelsize = 10)
    shp = gpd.read_file(shp_file).boundary
    shp.plot(ax=ax, edgecolor='grey', linewidth=0.7)
    ax.set_title(fig_title, fontsize = 12, loc='center',fontproperties = myfont) 
    if datatype == 'radar':
        clevels = [0,10, 20, 30, 40, 50, 60, 70]
        colors = ['#62e6eaff','#00d72eff','#fefe3fff','#ff9a29ff','#d70e15ff','#ff1cecff','#af91edff']
        # colors = ["#449ded", "#62e6ea", "#68f952", "#0000ff"]
    elif datatype == 'rain':  
        clevels = [0.1, 2.5, 8, 16,200]
        colors = ["#a6f28f", "#3dba3d", "#61b8ff", "#0000ff"]
    cs = plt.contourf(nclon, nclat, cr, levels=clevels, colors=colors)    
    cb = plt.colorbar(cs, fraction=0.022)
    cb.set_ticks(clevels[:-1])
    cb.set_ticklabels([str(level) for level in clevels[:-1]],fontproperties = myfont)
    for label in ax.get_xticklabels() + ax.get_yticklabels():
        label.set_fontproperties(myfont)
    crDir(figpath)
    plt.savefig(figpath, dpi=300, bbox_inches='tight') 
    print(f"{fig_title.split('_')[0]}绘制完成: {figpath}")
    plt.close()
"""
font_path = './shp/微软雅黑.ttf'
myfont = mpl.font_manager.FontProperties(fname = font_path, size = 12) 
UTCstr="202508280000"
shp_file = "./shp/province_9south.shp"
savepath = f"./FY4BBIG"
fig_title = f"卫星反演雷达回波_{UTCstr}"
# base[20:1070,75:1625] = satCR
plot_fig(data,result['lats'],result['lons'],fig_title,datatype="radar")
"""


