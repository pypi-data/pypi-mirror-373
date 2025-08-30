import numpy as np
import matplotlib.pyplot as plt
import datetime
from hjnwtx.colormap import cmp_hjnwtx
from mpl_toolkits.axes_grid1 import make_axes_locatable
from shancx import crDir
def radarcom(base_up, base_down, name="radar_composite",saveDir="plotRadar_composite",ty="radar_nmc"):
    now_str = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    combined_data = np.concatenate([base_up, base_down], axis=0)
    num_frames = base_up.shape[0]   
    fig, axes = plt.subplots(
        2,  # 行数(上下两层)
        num_frames,  # 列数(每层图像数量)
        figsize=(10 * num_frames, 10),   
        squeeze=False   
    )
    vmin, vmax = 0, 70
    for i in range(2):   
        for j in range(num_frames):   
            data_index = i * num_frames + j
            im = axes[i, j].imshow(
                combined_data[data_index, :, :],
                vmin=vmin,
                vmax=vmax,
                cmap=cmp_hjnwtx[ty]  #pre_tqw  radar_nmc
            )
            axes[i, j].axis('off')   
            divider = make_axes_locatable(axes[i, j])
            cax = divider.append_axes("right", size="5%", pad=0.5)
            plt.colorbar(im, cax=cax)
    plt.tight_layout()    
    outpath = f"./{saveDir}/{name}_{now_str}.png" if name=="radar_composite" else f"./{saveDir}/{name}.png"
    crDir(outpath)
    plt.savefig(outpath, bbox_inches='tight', dpi=300)
    plt.close()    
    print(f"图像已保存为: {outpath}")
 
 
#使用示例:
#draw_radar_composite(upper_data, lower_data, "my_radar_image")
#comP(base_up, base_down, name="UTCstr",vmin=150,vmax=320,cmap='summer')
#radarcomP(base_up, base_down,name="UTCstr",ty="radar_nmc")