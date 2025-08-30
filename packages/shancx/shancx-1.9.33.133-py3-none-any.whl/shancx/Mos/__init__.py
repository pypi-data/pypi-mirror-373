 


import numpy as np
def start_points(size, split_size, overlap=0.0): 
    stride = int(split_size * (1 - overlap))  # 计算步长
    points = [i * stride for i in range((size - split_size) // stride + 1)]   
    if size > points[-1] + split_size:   
        points.append(size - split_size)
    return points

def weigthOverlap(overlap,radarpre,x,y,b,weight_sum):
     weight = np.ones((256, 256))
     for i in range(overlap):
         weight[:, i] = 0.5 * (1 - np.cos(np.pi * i / overlap))
         weight[:, -i-1] = 0.5 * (1 - np.cos(np.pi * i / overlap))
         weight[i, :] = np.minimum(weight[i, :], 0.5 * (1 - np.cos(np.pi * i / overlap)))
         weight[-i-1, :] = np.minimum(weight[-i-1, :], 0.5 * (1 - np.cos(np.pi * i / overlap)))
     patch = radarpre * weight
     b[x:x+256, y:y+256] = np.where(np.isnan(b[x:x+256, y:y+256]), 
                            patch, 
                            b[x:x+256, y:y+256] + patch)
     weight_sum[x:x+256, y:y+256] = np.where(np.isnan(weight_sum[x:x+256, y:y+256]), 
                                                 weight, 
                                                 weight_sum[x:x+256, y:y+256] + weight)    
     return b,weight_sum

"""
weight_sum = np.zeros_like(b)
b,weight_sum = weigthOverlap(overlap,radarpre,x,y,b,weight_sum)
b = np.divide(b, weight_sum, where=weight_sum!=0)

weight_sum = np.zeros_like(b)
overlap = 32  
x_point = start_points(sat_data[0].shape[0], 256, overlap/256)
y_point = start_points(sat_data[0].shape[1], 256, overlap/256)
"""