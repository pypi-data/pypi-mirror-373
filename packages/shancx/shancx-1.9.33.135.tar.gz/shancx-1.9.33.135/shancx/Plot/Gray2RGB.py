 
import cv2
import numpy as np

def main():
    with open('./gsmap_nrt.20241023.0300.dat', 'rb') as f:
        img = np.frombuffer(f.read(), np.uint8)
        
        print(f"Array size: {img.size}")  # 输出数组大小
        
        channels = 3
        total_pixels = img.size // channels  # 总像素数
        
        # 尝试不同的宽度，找到合适的高度
        for width in [5400, 4800, 640]:  # 可以尝试不同的宽度
            if total_pixels % width == 0:
                height = total_pixels // width
                try:
                    # 转换为三维数组
                    img_3d = img.reshape((height, width, channels))
                    
                    # 确保数据类型为 uint8
                    img_3d = img_3d.astype(np.uint8)

                    # 保存图像
                    cv2.imwrite('./img.png', img_3d)  
                    print(f"Successfully reshaped to {height}x{width}x{channels} and saved as img.png")
                    break  # 成功重塑后退出循环
                except ValueError:
                    print(f"Failed to reshape with width {width}.")
        else:
            print("Could not find a suitable width to reshape the array.")

# if __name__ == '__main__':  
#     main()


from matplotlib.colors import ListedColormap
from PIL import Image
import matplotlib.pyplot as plt
import datetime
from shancx import crDir
import os 
from hjnwtx.colormap import cmp_hjnwtx
import numpy as np

cmp = {}
newcolorsAU = np.array([
    [245,245,255,255],
    [180,180,255,255],
    [120,120,255,255],
    [20,20,255, 255],
    [0,216,195, 255],
    [0,150,144, 255],
    [0,102,102,255],
    [255,255,0,255],
    [255,200,0,255],
    [255,150,0,255],
    [255,100,0,255],
    [255,0,0,255],
    [200,0,0,255],
    [120,0,0,255],
    [40,0,0,255]])/255
cmp["radar_AU"] = ListedColormap(newcolorsAU)


def drawimg(array_dt):
    now_str = datetime.datetime.now().strftime("%Y%m%d%H%M%S") 
    if len(array_dt.shape)==2:
            plt.imshow(array_dt,vmin=0,vmax=75,cmap=cmp_hjnwtx["radar_nmc"])
            plt.colorbar() 
            outpath = f"./temp_RGB_{now_str}.png"
            crDir(outpath)  
            plt.savefig(outpath)
            plt.close()   

def PlotRardar(path): 
            imgMap = Image.open(path) 
            imgMap = imgMap.convert('L')
            # 转换为 NumPy 数组
            # imgS_array = np.array(imgSource)                
            imgM_array = np.array(imgMap)                
            imgM_arrayf = np.where(imgM_array>0,imgM_array,np.nan)
            drawimg(imgM_arrayf)

PlotRardar("./img.png")
