
import matplotlib.pyplot as plt
import datetime
from hjnwtx.colormap import cmp_hjnwtx
import os
import numpy as np 

from pathlib import Path
def MDir(path):
    path_obj = Path(path)
    directory = path_obj.parent if path_obj.suffix else path_obj
    directory.mkdir(parents=True, exist_ok=True)

import datetime
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable
def plotRadar(array_dt, ty="CR", temp="temp"):
    now_str = datetime.datetime.now().strftime("%Y%m%d%H%M%S")    
    if len(array_dt.shape) == 2 and ty == "pre":
        fig, ax = plt.subplots()
        im = ax.imshow(array_dt, vmin=0, vmax=10, cmap=cmp_hjnwtx["pre_tqw"])        
        # 创建与图像高度一致的colorbar
        divider = make_axes_locatable(ax)
        cax = divider.append_axes("right", size="5%", pad=0.05)
        plt.colorbar(im, cax=cax)        
        outpath = f"./radar_nmc/{temp}{now_str}.png"
        MDir(outpath)
        plt.savefig(outpath)
        plt.close()    
    else:
        fig, ax = plt.subplots()
        im = ax.imshow(array_dt, vmin=0, vmax=72, cmap=cmp_hjnwtx["radar_nmc"])        
        # 创建与图像高度一致的colorbar
        divider = make_axes_locatable(ax)
        cax = divider.append_axes("right", size="5%", pad=0.05)
        plt.colorbar(im, cax=cax)        
        outpath = f"./radar_nmc/{temp}_{now_str}.png"
        MDir(outpath)
        plt.savefig(outpath)
        plt.close()



def plotRadar3(array_dt, ty="CR", temp="temp"):
    now_str = datetime.datetime.now().strftime("%Y%m%d%H%M%S") 
    if len(array_dt.shape) == 3:
        for i, img_ch_nel in enumerate(array_dt):
            fig, ax = plt.subplots()
            im = ax.imshow(img_ch_nel, vmin=0, vmax=10, cmap=cmp_hjnwtx["radar_nmc"])            
            divider = make_axes_locatable(ax)
            cax = divider.append_axes("right", size="5%", pad=0.05)
            plt.colorbar(im, cax=cax)            
            outpath = f"./radar_nmc/{temp}{now_str}.png"
            MDir(outpath)
            plt.savefig(outpath)
            plt.close()


            
def plotRadarcoor(array_dt, temp="temp"):
    now_str = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    y_coords2, x_coords2 = np.where(array_dt > 0)
    
    def plot_and_save(image, path):
        plt.imshow(image, vmin=0, vmax=10, cmap=cmp_hjnwtx["radar_nmc"])
        for (x, y) in zip(x_coords2, y_coords2):
            plt.plot(x, y, 'ro', markersize=25)  # Increase point size
            plt.text(x, y, f'{(image[y, x] * 6):.1f}', color='white', fontsize=12, ha='center', va='center')  # Label the corresponding value
        plt.colorbar()
        MDir(path)
        plt.savefig(path)
        plt.close()    
    if len(array_dt.shape) == 3:
        for i, img_ch_nel in enumerate(array_dt): 
            plot_and_save(img_ch_nel, f"./radar_nmc/{temp}_{now_str}.png")
    elif len(array_dt.shape) == 2:
        plt.imshow(array_dt, vmin=0, vmax=100, cmap=cmp_hjnwtx["pre_tqw"])
        plot_and_save(array_dt, f"./radar_nmc/{temp}_{now_str}.png")
