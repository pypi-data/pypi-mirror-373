#!/usr/bin/python
# -*- coding: utf-8 -*-
# @Time : 2024/10/17 上午午10:40
# @Author : shancx
# @File : __init__.py
# @email : shanhe12@163.com
from shancx import crDir
import matplotlib.pyplot as plt
import datetime
def plotGrey(img,name="plotGrey", saveDir="plotGrey",cmap='gray', title='Image'):
    now_str = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    img = img.squeeze()  # 去掉 batch 维度并转换为 numpy 数组
    plt.imshow(img, cmap='gray')
    plt.title(f"Image ")
    plt.axis('off')  # 不显示坐标轴
    outpath = f'./{saveDir}/{name}_{now_str}.png' if name=="plotGrey" else f"./{saveDir}/{name}.png"
    crDir(outpath)
    plt.savefig(outpath)
    plt.close()

import matplotlib.pyplot as plt
from shancx import crDir
import datetime
def plotMat(matrix,name='plotMat',saveDir="plotMat",title='Matrix Plot', xlabel='X-axis', ylabel='Y-axis', color_label='Value', cmap='viridis'):
    now_str = datetime.datetime.now().strftime("%Y%m%d%H%M%S")    
    plt.imshow(matrix, cmap=cmap, origin='upper', aspect='auto')
    plt.colorbar(label=color_label)
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.tight_layout()
    outpath = f'./{saveDir}/{name}_{now_str}.png' if name=="plotMat" else f"./{saveDir}/{name}.png"
    crDir(outpath)
    plt.savefig(outpath)
    plt.close()

import datetime
from hjnwtx.colormap import cmp_hjnwtx
from shancx import crDir
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable
def plotRadar(array_dt,name="plotRadar", saveDir="plotRadar",ty="CR"):
    now_str = datetime.datetime.now().strftime("%Y%m%d%H%M%S")    
    # array_dt[array_dt<=0] = np.nan 
    if len(array_dt.shape) == 2 and ty == "pre":
        fig, ax = plt.subplots()
        im = ax.imshow(array_dt, vmin=0, vmax=10, cmap=cmp_hjnwtx["pre_tqw"])        
        # 创建与图像高度一致的colorbar
        divider = make_axes_locatable(ax)
        cax = divider.append_axes("right", size="5%", pad=0.05)
        plt.colorbar(im, cax=cax)   
        fig.tight_layout()     
        outpath = f"./{saveDir}/{name}_pre_{now_str}.png" if name=="plotRadar" else f"./{saveDir}/{name}.png"
        crDir(outpath)
        plt.savefig(outpath)
        plt.close()     
    else:
        fig, ax = plt.subplots()
        im = ax.imshow(array_dt, vmin=0, vmax=72, cmap=cmp_hjnwtx["radar_nmc"])        
        divider = make_axes_locatable(ax)
        cax = divider.append_axes("right", size="5%", pad=0.05)
        plt.colorbar(im, cax=cax)   
        fig.tight_layout()     
        outpath = f"./{saveDir}/{name}_CR_{now_str}.png" if name=="plotRadar" else f"./{saveDir}/{name}.png"
        crDir(outpath)
        plt.savefig(outpath)
        plt.close()
 

import matplotlib.pyplot as plt
import numpy as np
import datetime
import os
from mpl_toolkits.axes_grid1 import make_axes_locatable
from hjnwtx.colormap import cmp_hjnwtx 
def plotA2b(a, b, name='plotA2b', saveDir="plotA2b", title='plotA2b Plot',class1 = "class",class2 = "class",ty="CR" ):
    now_str = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    cmap=cmp_hjnwtx["radar_nmc"] if ty == "CR" else 'summer'
    sublen = a.shape[0]
    fig, axes = plt.subplots(2, sublen, figsize=(20, 6))  
    for i in range(sublen):
        im_a = axes[0, i].imshow(a[i], cmap=cmap)
        axes[0, i].axis('off')
        axes[0, i].set_title(f'{class1}[{i}]')        
        divider_a = make_axes_locatable(axes[0, i])   
        cax_a = divider_a.append_axes("right", size="5%", pad=0.1)  
        cbar_a = fig.colorbar(im_a, cax=cax_a)   
        cbar_a.ax.tick_params(labelsize=8)   
    for i in range(sublen):
        im_b = axes[1, i].imshow(b[i], cmap=cmap)
        axes[1, i].axis('off')
        axes[1, i].set_title(f'{class2}[{i}]')        
        divider_b = make_axes_locatable(axes[1, i])   
        cax_b = divider_b.append_axes("right", size="5%", pad=0.1)   
        cbar_b = fig.colorbar(im_b, cax=cax_b)   
        cbar_b.ax.tick_params(labelsize=8)  
    plt.tight_layout()
    plt.subplots_adjust(top=0.9, bottom=0.1, hspace=0.05, wspace=0.1)  
    outpath = f'./{saveDir}/{name}_{now_str}.png'
    os.makedirs(os.path.dirname(outpath), exist_ok=True)
    plt.savefig(outpath, bbox_inches='tight', pad_inches=0.05)  
    plt.close()

import matplotlib.pyplot as plt
import os
def plotScatter(df1,saveDir="plotScatter"):
    now_str = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    plt.figure(figsize=(10, 8))   
    plt.scatter(
        df1["Lon"],  
        df1["Lat"],  
        s=25,        
        alpha=0.6,   
        edgecolor="black",   
        linewidth=0.5       
    )
    plt.title("Scatter Plot of Latitude vs Longitude", fontsize=14)
    plt.xlabel("Longitude", fontsize=12)
    plt.ylabel("Latitude", fontsize=12)
    plt.tight_layout()  
    os.makedirs(saveDir, exist_ok=True)
    plt.savefig(f"./{saveDir}/plotScatter_{now_str}.png", dpi=300, bbox_inches="tight")  
    plt.close()

import matplotlib.pyplot as plt
import os
def plotScatter1(true,pre,saveDir="plotScatter"):
    now_str = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    plt.figure(figsize=(10, 8))   
    plt.scatter(
        true,  
        pre,  
        s=25,        
        alpha=0.6,   
        edgecolor="black",   
        linewidth=0.5       
    )
    plt.title("Scatter Plot of Ture Pre", fontsize=14)
    plt.xlabel("Longitude", fontsize=12)
    plt.ylabel("Latitude", fontsize=12)
    plt.tight_layout()  
    os.makedirs(saveDir, exist_ok=True)
    plt.savefig(f"./{saveDir}/plotScatter1_{now_str}.png", dpi=300, bbox_inches="tight")  
    plt.close()

import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable
from shancx import crDir
import os
def plotVal( epoch=0,*datasets, title=["input","prediction","truth"], saveDir="plotVal", cmap='summer'):
    num_datasets = len(datasets)
    title = title or [f"data{i}" for i in range(num_datasets)]
    ncols = int(np.ceil(np.sqrt(num_datasets)))
    nrows = int(np.ceil(num_datasets / ncols))    
    fig, axes = plt.subplots(nrows, ncols, figsize=(12, 8))
    axes = axes.flatten()    
    for i, (data, t) in enumerate(zip(datasets, title)):
        im = axes[i].matshow(data, cmap=cmap)   #Paired  viridis  
        divider = make_axes_locatable(axes[i])
        cax = divider.append_axes("right", size="5%", pad=0.05)
        fig.colorbar(im, cax=cax)
        axes[i].set_title(t)    
    for j in range(i + 1, len(axes)):
        fig.delaxes(axes[j])    
    fig.tight_layout()
    os.makedirs(saveDir, exist_ok=True)
    filename = f"{saveDir}/epoch_{epoch}.png"
    plt.savefig(filename)
    plt.close(fig) 

    """   使用方法
        if total >= 3:
            break
    if epoch % 2 == 0:                    
       plotVal(epoch,   inputs[0]  --->example shape 为(256,256)
               inputs, 
               pre, 
               targets
               )  
    if epoch % 2 == 0: 
       plotVal(epoch,    
           data[0][0].detach().cpu().numpy().squeeze(),  # 使用 detach()
           output[0][0].detach().cpu().numpy().squeeze(),  # 使用 detach()
           label[0][0].detach().cpu().numpy().squeeze(),  # 使用 detach()
           title=["input", "prediction", "groundtruth"], 
           saveDir="plot_train_dir"
       )
    """
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable
from shancx import crDir
import os

def plotValplus(epoch=0, *datasets, title=["input", "prediction", "truth"], saveDir="plotValplus", cmap='summer'):
    num_datasets = len(datasets)
    title = title or [f"data{i}" for i in range(num_datasets)]
    ncols = int(np.ceil(np.sqrt(num_datasets)))
    nrows = int(np.ceil(num_datasets / ncols))
    
    fig, axes = plt.subplots(nrows, ncols, figsize=(12, 8))
    axes = axes.flatten()
    
    for i, (data, t) in enumerate(zip(datasets, title)):
        # if np.isnan(data).any():
        #    print(f"Warning: NaN values found in dataset. Replacing NaN with 0.")
        # data = np.nan_to_num(data, nan=0.0)
        im = axes[i].matshow(data, cmap=cmap, vmin=np.nanmin(data), vmax=np.nanmax(data))
        axes[i].set_xticks([])
        axes[i].set_yticks([])
        divider = make_axes_locatable(axes[i])
        cax = divider.append_axes("right", size="5%", pad=0.05)
        cbar = fig.colorbar(im, cax=cax, ticks=np.linspace(np.nanmin(data), np.nanmax(data), 15))
        cbar.set_ticks(np.linspace(np.nanmin(data), np.nanmax(data), 15))        
        axes[i].set_title(t)    
    for j in range(i + 1, len(axes)):
        fig.delaxes(axes[j])    
    fig.tight_layout()    
    os.makedirs(saveDir, exist_ok=True)
    filename = f"{saveDir}/epoch_{epoch}.png"
    plt.savefig(filename)
    plt.close(fig)
    """   使用方法
    if total >= 3:
        break
    if epoch % 2 == 0: 
       plotVal(epoch,    
           data[0][0].detach().cpu().numpy().squeeze(),  # 使用 detach()
           output[0][0].detach().cpu().numpy().squeeze(),  # 使用 detach()
           label[0][0].detach().cpu().numpy().squeeze(),  # 使用 detach()
           title=["input", "prediction", "groundtruth"], 
           saveDir="plot_train_dir"
       )
    """

import numpy as np
import matplotlib
matplotlib.use("Agg") 
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable
from hjnwtx.colormap import cmp_hjnwtx
from shancx import crDir
import os
def plot_dataset(ax, data, title, cmap, vmin, vmax):
    """
    Helper function to plot a single dataset on a given axis.
    """
    im = ax.matshow(data, cmap=cmap, vmin=vmin, vmax=vmax)    
    # Remove axis ticks
    ax.set_xticks([])
    ax.set_yticks([])    
    # Add colorbar
    divider = make_axes_locatable(ax)
    cax = divider.append_axes("right", size="5%", pad=0.05)
    cbar = plt.colorbar(im, cax=cax, ticks=np.linspace(vmin, vmax, 15))
    cbar.set_ticks(np.linspace(vmin, vmax, 15))    
    # Set title
    ax.set_title(title)    
    return im

def plotValplus1(epoch=0, *datasets, title=["input", "prediction", "truth"], saveDir="plotValplus", cmap='summer'):
    """
    Main function to plot multiple datasets in a grid layout.
    """
    plt.ioff()  
    num_datasets = len(datasets)
    title = title or [f"data{i}" for i in range(num_datasets)]
    ncols = int(np.ceil(np.sqrt(num_datasets)))
    nrows = int(np.ceil(num_datasets / ncols))    
    # Create subplots
    fig, axes = plt.subplots(nrows, ncols, figsize=(12, 8))
    axes = axes.flatten()    
    # Plot each dataset
    for i, (data, t) in enumerate(zip(datasets, title)):
        if i != 0:
            vmin, vmax = 0, 70
            cmap_used = cmp_hjnwtx["radar_nmc"]
            plot_dataset(axes[i], data, t, cmap_used, vmin, vmax)
        else:
            # vmin, vmax = 150, 300
            cmap_used = cmap  #        
            plot_dataset(axes[i], data, t, cmap_used,np.min(data),np.max(data))    
    # Remove unused subplots
    for j in range(i + 1, len(axes)):
        fig.delaxes(axes[j])    
    # Adjust layout and save the figure
    fig.tight_layout()
    os.makedirs(saveDir, exist_ok=True)
    filename = f"{saveDir}/epoch_{epoch}.png"
    plt.savefig(filename)
    plt.close(fig) 


import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable
import numpy as np
import os
import datetime
import pandas as pd 
from multiprocessing import Pool
import argparse
from itertools import product
import glob 
def calculate_colorbar_range(data):
    vmin = int(np.nanmin(data))
    vmax = int(np.nanmax(data))
    return vmin, vmax
def plot_grid_data(data, titles=None, save_dir="plots", name="temp",
                   cmap="viridis", vmin=None, vmax=None):
    if not isinstance(data, np.ndarray) or data.ndim != 3:
        raise ValueError("输入数据必须为三维numpy数组 [num_images, height, width]")    
    num_images = data.shape[0]
    titles = titles or [f"Data {i}" for i in range(num_images)]
    if vmin is None or vmax is None:
        vmin, vmax = calculate_colorbar_range(data)
    ncols = int(np.ceil(np.sqrt(num_images)))
    nrows = int(np.ceil(num_images / ncols))
    fig, axes = plt.subplots(nrows, ncols, figsize=(ncols * 3, nrows * 3))
    axes = axes.ravel()
    for i in range(num_images):
        ax = axes[i]
        im = ax.imshow(data[i], cmap=cmap, vmin=vmin, vmax=vmax)
        ax.set_title(titles[i])
        ax.axis('off')        
        divider = make_axes_locatable(ax)
        cax = divider.append_axes("right", size="5%", pad=0.05)
        cbar = plt.colorbar(im, cax=cax,
                          ticks=np.linspace(vmin, vmax, 15),  
                          format='%.1f')   
        cbar.ax.tick_params(labelsize=6)   
    for j in range(num_images, len(axes)):
        axes[j].axis('off')
    plt.tight_layout()
    os.makedirs(save_dir, exist_ok=True)
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    filename = f"{name}_{timestamp}.png"
    plt.savefig(os.path.join(save_dir, filename), dpi=300)
    plt.close()
def drawpic_com(basedata, save_dir="plots", name="temp", cmap="summer"): 
    data_all = basedata[:,::2,::2]
    if isinstance(name, str):
        print("name str")
        titles = [f"channel_{i+1} {name}" for i in range(basedata.shape[0])]  
    else:
        titles = [f"{i}" for i in name.strftime("%Y%m%d%H%M%S")]
        name = name.strftime("%Y%m%d%H%M%S")[0]
    plot_grid_data(
        data=data_all,
        titles=titles,
        name=name,
        save_dir=save_dir,
        cmap=cmap
    ) 

"""
drawpic_com(Data_con, save_dir="plots_H9", name=timeList )
"""

import os
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
class trainingVis:
    def __init__(self, args=None, dataset_key_map=None, root_path="./"):
        self.args = args
        self.dataset_key_map = dataset_key_map
        self.root_path = root_path
        self.record = {
            "train_loss": [],
            "train_psnr": [],
            "val_loss": [],
            "val_psnr": [],
        }
        self.x_epoch = []
        self.output_dir = self._get_output_dir()
    def _get_output_dir(self):
        """生成输出目录路径并创建目录"""
        output_dir = os.path.join(
            self.root_path,
            "Rec",
            # "weights_dir",
            # self.dataset_key_map[self.args.dataset_key],
            "trainvalViscure",
        )
        os.makedirs(output_dir, exist_ok=True)
        return output_dir
    def _plot_curve(self, ax, x, y_train, y_val, y_label, train_color="blue", val_color="red"):
        """绘制单条曲线并优化坐标轴显示"""
        if y_train is not None:
            ax.plot(x, y_train, marker='o', linestyle='-', color=train_color, label="Train")
        if y_val is not None:
            ax.plot(x, y_val, marker='o', linestyle='-', color=val_color, label="Val")        
        # 设置坐标轴标签和格式
        ax.set_xlabel("Epoch", fontsize=10)
        ax.set_ylabel(y_label, fontsize=10)
        ax.set_title(f"{y_label} Curve", fontsize=12)        
        # 配置x轴刻度（确保整数显示）
        ax.xaxis.set_major_locator(MaxNLocator(integer=True))
        plt.setp(ax.get_xticklabels(), rotation=30, ha='right', fontsize=8)        
        # 配置y轴刻度
        ax.yaxis.set_major_locator(MaxNLocator(nbins=6))
        plt.setp(ax.get_yticklabels(), fontsize=8)        
        # 添加图例
        ax.legend(loc="upper right", fontsize=8)
    def draw_curve(self, epoch=None, train_loss=None, train_psnr=None, val_loss=None, val_psnr=None):
        """动态绘制训练曲线并根据数据存在性调整布局"""
        self.record["train_loss"].append(train_loss)
        self.record["val_loss"].append(val_loss)
        self.x_epoch.append(epoch)        
        has_psnr = train_psnr is not None and val_psnr is not None
        if has_psnr:
            self.record["train_psnr"].append(train_psnr)
            self.record["val_psnr"].append(val_psnr)
        else:
            self.record["train_psnr"].append(None)
            self.record["val_psnr"].append(None)
        fig = plt.figure(figsize=(10, 4.5) if has_psnr else (6, 4.5))
        plt.subplots_adjust(wspace=0.3 if has_psnr else 0)        
        ax0 = fig.add_subplot(111 if not has_psnr else 121)        
        # 如果只有train_loss数据存在
        if train_loss is not None and val_loss is None:
            self._plot_curve(ax0
                             ,self.x_epoch
                             ,self.record["train_loss"]
                             ,None
                             ,"Loss"
                             ,train_color="blue"
                             ,val_color="red"
                             )        
        elif val_loss is not None and train_loss is None:
            self._plot_curve(ax0, 
                             self.x_epoch, 
                             None, 
                             self.record["val_loss"], 
                             "Loss", 
                             train_color="blue", 
                             val_color="red"
                             )
        else:
            self._plot_curve(ax0, 
                             self.x_epoch, 
                             self.record["train_loss"], 
                             self.record["val_loss"], 
                             "Loss", train_color="blue", 
                             val_color="red"
                             )
        if has_psnr:
            ax1 = fig.add_subplot(122)
            self._plot_curve(ax1, 
                             self.x_epoch, 
                             self.record["train_psnr"], 
                             self.record["val_psnr"], 
                             "PSNR", 
                             train_color="orange", 
                             val_color="grey"
                             )
        plt.tight_layout()
        fig.savefig(
            os.path.join(self.output_dir, f"train_{epoch}.jpg"),
            dpi=300,
            bbox_inches="tight",
            pad_inches=0.1
        )
        plt.close(fig)
        """
        vis3 = TrainingVis(root_path="./Rec3")
        vis4 = TrainingVis(root_path="./Rec4")
        vis5 = TrainingVis(root_path="./Rec5")
        for epoch in range(t.epoch, t.epoch + args.num_epochs):
            train_loss, train_psnr = t.train(epoch)
            val_loss, val_psnr = t.val(epoch)
            if (epoch + 1) % 3 == 0:
                # t.draw_curve(fig, epoch, train_loss, train_psnr, val_loss, val_psnr)
                vis.draw_curve(epoch, train_loss, train_psnr, val_loss, val_psnr)
                vis1.draw_curve(epoch, train_loss,val_loss)
                vis2.draw_curve(epoch, train_loss,val_loss,train_psnr,val_psnr)
                vis3.draw_curve(epoch, train_loss,val_loss,train_psnr,val_psnr)
                vis4.draw_curve(epoch, train_loss)
                vis5.draw_curve(epoch, val_loss)
        ------------------------
        from shancx.Plot import trainingVis
        vis= trainingVis(root_path="./Rec3")  
        if (epoch + 1) % 3== 0:     
            vis.draw_curve(epoch, epoch_loss.detach().cpu().numpy(),epoch_val_loss.detach().cpu().numpy())
        """

class trainingVisplus:
    def __init__(self, args=None, dataset_key_map=None, root_path="./"):
        self.args = args
        self.dataset_key_map = dataset_key_map
        self.root_path = root_path
        self.record = {
            "train_loss": [],
            "train_psnr": [],
            "train_acc": [],
            "val_loss": [],
            "val_psnr": [],
            "val_acc": [],
        }
        self.x_epoch = []
        self.output_dir = self._get_output_dir()

    def _get_output_dir(self):
        """生成输出目录路径并创建目录"""
        output_dir = os.path.join(
                                  self.root_path,
                                  "Rec",
                                  "trainvalViscure",
                                 )
        os.makedirs(output_dir, exist_ok=True)
        return output_dir

    def _plot_curve(
                    self, 
                    ax, 
                    x, 
                    y_train, 
                    y_val, 
                    y_label, 
                    train_color="blue", 
                    val_color="red"
                    ):
        """绘制单条曲线并优化坐标轴显示"""
        if y_train is not None:
            ax.plot(x, y_train, 
                    marker='o', 
                    linestyle='-', 
                    color=train_color, 
                    label="Train"
                    )
        if y_val is not None:
            ax.plot(x, y_val, 
                    marker='o', 
                    linestyle='-', 
                    color=val_color, 
                    label="Val"
                    )
        # 设置坐标轴标签和格式
        ax.set_xlabel("Epoch", fontsize=10)
        ax.set_ylabel(y_label, fontsize=10)
        ax.set_title(f"{y_label} Curve", fontsize=12)
        # 配置x轴刻度（确保整数显示）
        ax.xaxis.set_major_locator(MaxNLocator(integer=True))
        plt.setp(ax.get_xticklabels(), rotation=30, ha='right', fontsize=8)
        # 配置y轴刻度
        ax.yaxis.set_major_locator(MaxNLocator(nbins=6))
        plt.setp(ax.get_yticklabels(), fontsize=8)
        # 添加图例
        ax.legend(loc="upper right", fontsize=8)

    def draw_curve(
                   self, epoch=None, 
                   train_loss=None, 
                   train_psnr=None, 
                   val_loss=None, 
                   val_psnr=None, 
                   train_acc=None, 
                   val_acc=None
                   ):
        """动态绘制训练曲线并根据数据存在性调整布局"""
        # 更新训练记录
        self.record["train_loss"].append(train_loss)
        self.record["val_loss"].append(val_loss)
        self.x_epoch.append(epoch)

        # 有条件地更新PSNR和Acc记录
        has_psnr = train_psnr is not None and val_psnr is not None
        has_acc = train_acc is not None and val_acc is not None

        if has_psnr:
            self.record["train_psnr"].append(train_psnr)
            self.record["val_psnr"].append(val_psnr)
        else:
            # 用None占位保持数据对齐
            self.record["train_psnr"].append(None)
            self.record["val_psnr"].append(None)

        if has_acc:
            self.record["train_acc"].append(train_acc)
            self.record["val_acc"].append(val_acc)
        else:
            # 用None占位保持数据对齐
            self.record["train_acc"].append(None)
            self.record["val_acc"].append(None)

        # 创建自适应布局的画布
        num_plots = 1 + int(has_psnr) + int(has_acc)
        fig_width = 4 * num_plots  # 每个子图宽度为4
        fig = plt.figure(figsize=(fig_width, 4.5))
        plt.subplots_adjust(wspace=0.3)

        # 绘制Loss曲线
        ax0 = fig.add_subplot(1, num_plots, 1)
        self._plot_curve(
                         ax0, 
                         self.x_epoch, 
                         self.record["train_loss"], 
                         self.record["val_loss"], 
                         "Loss", 
                         train_color="blue", 
                         val_color="red"
                         )

        # 绘制PSNR曲线（如果存在）
        if has_psnr:
            ax1 = fig.add_subplot(1, num_plots, 2)
            self._plot_curve(
                             ax1, 
                             self.x_epoch, 
                             self.record["train_psnr"], 
                             self.record["val_psnr"], 
                             "PSNR", 
                             train_color="orange", 
                             val_color="grey"
                             )

        # 绘制Acc曲线（如果存在）
        if has_acc:
            ax2 = fig.add_subplot(1, num_plots, num_plots)
            self._plot_curve(
                             ax2, 
                             self.x_epoch, 
                             self.record["train_acc"], 
                             self.record["val_acc"],
                             "Accuracy", 
                             train_color="grey", 
                             val_color="purple"
                             )

        # 优化布局并保存
        plt.tight_layout()
        fig.savefig(
            os.path.join(self.output_dir, f"train_{epoch}.jpg"),
            dpi=300,
            bbox_inches="tight",
            pad_inches=0.1
        )
        plt.close(fig)
        """

        vis1= trainingVisplus(root_path="./Rec4") 
        for epoch in range(t.epoch, t.epoch + args.num_epochs):
            train_loss, train_psnr = t.train(epoch)
            val_loss, val_psnr = t.val(epoch)
            if (epoch + 1) % 3 == 0:
            vis1.draw_curve(epoch=epoch, 
                            train_loss=epoch_loss.detach().cpu().numpy(), 
                            val_loss=epoch_val_loss.detach().cpu().numpy(),  
                            train_acc=epoch_accuracy, 
                            val_acc=epoch_val_accuracy
                            )

        """

# @staticmethod
# def calculate_psnr(img1, img2):
#     return 10. * torch.log10(1. / torch.mean((img1 - img2) ** 2))   
    """  使用方法
    psnr += self.calculate_psnr(fake_img, label).item()
    total += 1
     mean_psnr = psnr / total
    """ 

from hjnwtx.colormap import cmp_hjnwtx
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable
import numpy as np
import os
import datetime
def calculate_colorbar_range(data):
    """计算色标范围"""
    valid_data = data[~np.isnan(data)]
    vmin = int(np.min(valid_data))
    vmax = int(np.max(valid_data))
 
    return vmin, vmax
def plot_grid_data(data, titles=None, saveDir="plots", name="temp",
                   cmap="viridis", vmin=None, vmax=None):
    if not isinstance(data, np.ndarray) or data.ndim != 3:
        raise ValueError("输入数据必须为三维numpy数组 [num_images, height, width]")    
    num_images = data.shape[0]
    titles = titles or [f"Data {i}" for i in range(num_images)]    
    # 计算色标范围
    if vmin is None or vmax is None:
        vmin, vmax = calculate_colorbar_range(data)    
    # 计算子图布局
    ncols = int(np.ceil(np.sqrt(num_images)))
    nrows = int(np.ceil(num_images / ncols))    
    # 创建子图
    fig, axes = plt.subplots(nrows, ncols, figsize=(ncols * 3, nrows * 3))
    axes = axes.ravel()
    for i in range(num_images):
        if i==int(num_images-1):
            vmin = 0
            vmax = 70
            ax = axes[i]
            im = ax.imshow(data[i], cmap=cmp_hjnwtx["radar_nmc"], vmin=vmin, vmax=vmax) #cmp_hjnwtx["radar_nmc"]
        else:
            vmin = 190
            vmax = 300
            ax = axes[i]
            im = ax.imshow(data[i], cmap=cmap, vmin=vmin, vmax=vmax)
        ax.set_title(titles[i])
        ax.axis('off')        
        # 添加色标
        divider = make_axes_locatable(ax)
        cax = divider.append_axes("right", size="5%", pad=0.05)
        cbar = plt.colorbar(im, cax=cax,
                          ticks=np.linspace(vmin, vmax, 15),  # 增加刻度密度
                          format='%.1f')  # 设置数值格式
        cbar.ax.tick_params(labelsize=6)  # 调整刻度文字大小    
    # 隐藏空子图
    for j in range(num_images, len(axes)):
        axes[j].axis('off')    
    # 保存图像
    plt.tight_layout()
    os.makedirs(saveDir, exist_ok=True)
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    filename = f"{name}_{timestamp}.png"
    plt.savefig(os.path.join(saveDir, filename), dpi=300)
    plt.close()
def plotTr(base_up, base_down, name="plotTr", saveDir="plotTr",  cmap="summer"): #viridis
    """
    组合数据并调用绘图函数    
    Args:
        base_up: 上部数据数组 [shape_len, H, W]
        base_down: 下部数据数组 [1, H, W]
        shape_len: 上部数据数量
        name: 输出文件名前缀
        cmap: 颜色映射
    """  
    # 合并数据并生成标题
    data_all = np.concatenate([base_up, base_down], axis=0)
    titles = [f"B_{i}" for i in range(base_up.shape[0])] + [f"radar_{i+1}" for i in range(base_down.shape[0])]    
    # 调用绘图函数
    plot_grid_data(
        data=data_all,
        titles=titles,
        name=name,
        saveDir=saveDir,
        cmap=cmap
    ) 
    """ 
    if __name__ == "__main__":
        base_up = np.random.rand(10, 50, 50) * 70
        base_down = np.random.rand(1, 50, 50) * 70
        plotTr(base_up, base_down, name="radar_plot") #   radar_mask.detach().cpu().numpy()  tensor转numpy 
    """

import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from mpl_toolkits.axes_grid1 import make_axes_locatable
def plotBorder(matrix,name='plotBorder',saveDir="plotBorder",extent=None,title='Matrix Plot', xlabel='X-axis', ylabel='Y-axis', color_label='Value', cmap='viridis'):
    # 地理范围 (lat_min, lat_max, lon_min, lon_max)  #[0,57,-132.0,-47] NA
    if extent is None:  
        lat_min, lat_max = -3, 13
        lon_min, lon_max = -0, 28
    else:
        lat_min, lat_max, lon_min, lon_max = extent
    # 创建地图
    now_str = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    fig = plt.figure(figsize=(12, 8))
    ax = fig.add_subplot(1, 1, 1, projection=ccrs.PlateCarree())
    ax.set_extent([lon_min, lon_max, lat_min, lat_max], crs=ccrs.PlateCarree())
    im = ax.imshow(
        matrix,
        extent=[lon_min, lon_max, lat_min, lat_max],
        origin='upper',  # 卫星数据通常 origin='upper'
        cmap='viridis',  # 选择合适的 colormap
        transform=ccrs.PlateCarree()
    )
    ax.add_feature(cfeature.COASTLINE, linewidth=0.5)
    ax.add_feature(cfeature.BORDERS, linestyle=':', linewidth=0.5)
    # 添加美国州边界（50m 分辨率）
    states = cfeature.NaturalEarthFeature(
        category='cultural',
        name='admin_1_states_provinces_lines',
        scale='50m',
        facecolor='none'
    )
    ax.add_feature(states, edgecolor='red', linewidth=0.5)
    divider = make_axes_locatable(ax)
    cax = divider.append_axes("right", size="5%", pad=0.1, axes_class=plt.Axes)
    cbar = plt.colorbar(im, cax=cax, label='Data Values')
    ax.set_title('Sat data Boundaries', fontsize=14)
    plt.tight_layout()  # 优化布局
    outpath = f'./{saveDir}/{name}_{now_str}.png' if name=="plotBorder" else f"./{saveDir}/{name}.png"
    crDir(outpath)
    plt.savefig(outpath)
    plt.close()