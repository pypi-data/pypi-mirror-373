import torch
import numpy as np
import matplotlib.pyplot as plt
# from mpl_toolkits.mplot3d import Axes3D 
from shancx import crDir
def plot3DJU(x,path="./3D_test1.png"):
    data = x.cpu().numpy()  if x.is_cuda else x[:,:,:].numpy()    
    data = data[:, ::5, ::5]
    x1 = np.arange(data.shape[0])  # x轴的范围，取决于data的第一个维度
    y1 = np.arange(data.shape[1])  # y轴的范围，取决于data的第二个维度
    z1 = np.arange(data.shape[2])  # z轴的范围，取决于data的第三个维度
    x1, y1, z1 = np.meshgrid(x1, y1, z1)
    x1_flat = x1.flatten()
    y1_flat = y1.flatten()
    z1_flat = z1.flatten()
    colors = data.flatten()
    fig = plt.figure(figsize=(10, 7))
    ax = fig.add_subplot(111, projection='3d')
    scatter = ax.scatter(x1_flat, y1_flat, z1_flat, c=colors, cmap='viridis')
    ax.set_title("3D Scatter Plot of Shape (400, 640, 400)")
    plt.colorbar(scatter)
    outpath = path
    crDir(outpath)
    plt.savefig(outpath)
    plt.close()