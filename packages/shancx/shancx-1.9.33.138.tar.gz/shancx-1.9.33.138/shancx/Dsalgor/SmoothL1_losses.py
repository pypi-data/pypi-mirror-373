import torch
import torch.nn.functional as F
import torch.nn as nn
def smoothL1_loss(x, y):
    smoothL1loss = nn.SmoothL1Loss()
    return smoothL1loss(x, y)
def compute_smoothL1_losses(x,y, y_label):
    """
    计算每个标签类别的 Smooth L1 损失。    
    参数:
    - x (torch.Tensor): 预测值。
    - y (torch.Tensor): 真实值。
    - y_label (torch.Tensor): 标签值，用于选择对应类别的预测和真实值。    
    返回:
    - smoothL1_losses (list): 包含每个类别的 Smooth L1 损失值的列表。
    """
    smoothL1_losses = []
    for label_value in range(1, 5):
        mask = y_label == label_value
        x_masked = torch.masked_select(x, mask)
        y_masked = torch.masked_select(y, mask)
        if x_masked.numel() > 0:
            smoothL1_val = smoothL1_loss(x_masked, y_masked) #, reduction='mean'
            smoothL1_losses.append(smoothL1_val) 
        else:
            smoothL1_losses.append(torch.tensor(0.0))        #增强逻辑   
    return smoothL1_losses
