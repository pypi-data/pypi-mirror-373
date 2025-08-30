
import torchvision.models as models
from torch import nn
import torch
from torchvision.models import vgg19
# Define VGG Loss
class VGGLoss(nn.Module):
    def __init__(self, weights_path=None,device =None):
        super().__init__()
        self.vgg = models.vgg19(pretrained=False).features[:35].eval().to(device)
        if weights_path:
            pretrained_weights = torch.load(weights_path)
            self.vgg.load_state_dict(pretrained_weights, strict=False)
        self.vgg[0] = nn.Conv2d(1, 64, kernel_size=3, stride=1, padding=1).to(device)
        for param in self.vgg.parameters():
            param.requires_grad = False
        self.loss = nn.MSELoss()
    def forward(self, input, target):
        input_features = self.vgg(input)
        target_features = self.vgg(target)
        return self.loss(input_features, target_features)
"""
vgg_loss = VGGLoss(weights_path="/mnt/wtx_weather_forecast/scx/stat/sat/sat2radar/vgg19-dcbb9e9d.pth").to(device)
""" 
 
import torch
import torch.nn as nn
import torch.nn.functional as F
from segment_anything import sam_model_registry

class SAMLoss(nn.Module):
    def __init__(self, model_type='vit_b', checkpoint_path=None, input_size=1024):
        """
        SAM-based perceptual loss with resolution handling
        
        Args:
            model_type (str): SAM model type (vit_b, vit_l, vit_h)
            checkpoint_path (str): Path to SAM checkpoint weights
            input_size (int): Target input size for SAM (default 1024)
        """
        super().__init__()
        self.input_size = input_size        
        # Initialize SAM model
        self.sam = sam_model_registry[model_type](checkpoint=None)        
        # Load pretrained weights if provided
        if checkpoint_path:
            state_dict = torch.load(checkpoint_path)
            self.sam.load_state_dict(state_dict)        
        # Use image encoder only and freeze parameters
        self.image_encoder = self.sam.image_encoder.eval()
        for param in self.image_encoder.parameters():
            param.requires_grad = False            
        # Define loss function
        self.loss = nn.MSELoss()        
        # Normalization parameters
        self.register_buffer('mean', torch.tensor([0.485, 0.456, 0.406]).view(1, 3, 1, 1))
        self.register_buffer('std', torch.tensor([0.229, 0.224, 0.225]).view(1, 3, 1, 1))
        
    def preprocess(self, x):
        """
        Preprocess input to match SAM requirements:
        1. Convert to 3-channel if needed
        2. Normalize using ImageNet stats
        3. Resize to target size
        """
        if x.shape[1] == 1:
            x = x.expand(-1, 3, -1, -1)  # More memory efficient than repeat        
        # Normalize
        x = (x - self.mean) / self.std        
        # Resize
        if x.shape[-2:] != (self.input_size, self.input_size):
            x = F.interpolate(x, size=(self.input_size, self.input_size), 
                             mode='bilinear', align_corners=False)        
        return x        
    def forward(self, input, target):
        # Preprocess
        input = self.preprocess(input)
        target = self.preprocess(target)        
        # Process in batches if needed
        batch_size = 4  # Adjust based on your GPU memory
        input_features = []
        target_features = []        
        with torch.no_grad():
            for i in range(0, input.size(0), batch_size):
                input_batch = input[i:i+batch_size]
                target_batch = target[i:i+batch_size]                
                input_features.append(self.image_encoder(input_batch))
                target_features.append(self.image_encoder(target_batch))        
        return self.loss(torch.cat(input_features), torch.cat(target_features))

 
import torch
import torch.nn as nn
import torch.nn.functional as F
from segment_anything import sam_model_registry
 

class SAMLoss(nn.Module):
    def __init__(self, model_type='vit_b', checkpoint_path=None):
        super().__init__()
        # 初始化 SAM 并加载预训练权重
        self.sam = sam_model_registry[model_type](checkpoint=None)
        if checkpoint_path:
            state_dict = torch.load(checkpoint_path)
            self.sam.load_state_dict(state_dict)
        
        # 提取 image_encoder 并冻结
        self.image_encoder = self.sam.image_encoder.eval()
        for param in self.image_encoder.parameters():
            param.requires_grad = False
        
        # 获取 patch_size（通常为16）
        self.patch_size = self.image_encoder.patch_embed.proj.kernel_size[0]
        
        # 保存原始 pos_embed 供动态调整
        self.original_pos_embed = self.image_encoder.pos_embed
        
        # 归一化参数
        self.register_buffer('mean', torch.tensor([0.485, 0.456, 0.406]).view(1, 3, 1, 1))
        self.register_buffer('std', torch.tensor([0.229, 0.224, 0.225]).view(1, 3, 1, 1))
        
        self.loss = nn.MSELoss()

    def adjust_pos_embed(self, x):
        """
        动态调整 pos_embed 以匹配输入尺寸
        Args:
            x: 输入张量 (B, C, H, W)
        """
        B, _, H, W = x.shape
        # 计算当前特征图的分辨率（H/patch_size, W/patch_size）
        h, w = H // self.patch_size, W // self.patch_size
        
        # 如果 pos_embed 尺寸不匹配，则进行插值
        if (h, w) != self.original_pos_embed.shape[1:3]:
            # 插值 pos_embed 到目标尺寸 (1, h, w, C) -> (1, C, h, w) -> 插值 -> 恢复形状
            pos_embed = self.original_pos_embed.permute(0, 3, 1, 2)  # (1, C, H_orig, W_orig)
            pos_embed = F.interpolate(
                pos_embed,
                size=(h, w),
                mode='bilinear',
                align_corners=False
            ).permute(0, 2, 3, 1)  # (1, h, w, C)
            
            # 用 nn.Parameter 包装调整后的 pos_embed
            self.image_encoder.pos_embed = nn.Parameter(pos_embed, requires_grad=False)
        else:
            self.image_encoder.pos_embed = self.original_pos_embed
    def preprocess(self, x):
        """预处理：通道扩展 + 归一化 + 尺寸调整"""
        if x.shape[1] == 1:
            x = x.expand(-1, 3, -1, -1)  # 单通道→三通        
        # 归一化
        x = (x - self.mean) / self.std        
        # 确保尺寸是 patch_size 的整数倍
        B, C, H, W = x.shape
        H_new = (H // self.patch_size) * self.patch_size
        W_new = (W // self.patch_size) * self.patch_size
        if H != H_new or W != W_new:
            x = F.interpolate(
                x,
                size=(H_new, W_new),
                mode='bilinear',
                align_corners=False
            )
        return x
    def forward(self, input, target):
        # 预处理
        input = self.preprocess(input)
        target = self.preprocess(target)
        
        # 动态调整 pos_embed
        self.adjust_pos_embed(input)
        
        # 计算特征
        with torch.no_grad():
            input_feat = self.image_encoder(input)
            target_feat = self.image_encoder(target)
        
        return self.loss(input_feat, target_feat)

# saml = SAMLoss(checkpoint_path = "/path/to/sam_vit_b_01ec64.pth.1").to(device)


import torch
import torch.nn as nn
from torchvision import models
class WeightedVGGLoss(nn.Module):
    def __init__(self, weights_path=None, device=None, apply_weighting=True):
        super().__init__()
        self.device = device
        self.apply_weighting = apply_weighting
        self.vgg = models.vgg19(pretrained=False).features[:35].eval().to(device)        
        if weights_path:
            pretrained_weights = torch.load(weights_path)
            self.vgg.load_state_dict(pretrained_weights, strict=False)
        self.vgg[0] = nn.Conv2d(1, 64, kernel_size=3, stride=1, padding=1).to(device)
        for param in self.vgg.parameters():
            param.requires_grad = False
        self.mse_loss = nn.MSELoss()
    def custom_weight_4d(self, target):
        EPS = 1e-6
        segments = [
            [10, 20, 0.5, 0.1], [20, 30, 0.4, 0.12],
            [30, 40, 0.3, 0.14], [40, 50, 0.2, 0.16],
            [50, 60, 0.1, 0.18], [60, 70, 0.05, 0.2]
        ]
        weights = torch.full_like(target, 0.1)
        for start, end, steepness, base_w in segments:
            mask = (target >= start) & (target < end)
            x = ((target - start) / (end - start + EPS)).clamp(0, 1)
            delta_w = (1.0 - base_w) * (0.7 - steepness)
            seg_weights = base_w + delta_w * (x / (x + steepness*(1 - x) + EPS))
            weights = torch.where(mask, seg_weights, weights)
        weights[target >= 70] = 1.0
        return weights
    def forward(self, input, target):
        input_features = self.vgg(input)
        target_features = self.vgg(target)
        if self.apply_weighting:
            weights = self.custom_weight_4d(target_features.detach())
            loss = torch.mean(weights * (input_features - target_features)**2)
        else:
            loss = self.mse_loss(input_features, target_features)            
        return loss
# vgg_loss = WeightedVGGLoss(weights_path="/mnt/wtx_weather_forecast/scx/stat/sat/sat2radar/vgg19-dcbb9e9d.pth",device=device).to(device)

import torch
import torch.nn as nn
import torch.nn.functional as F
class WeightedL1Loss(nn.Module):
    def __init__(self, segment_ranges=None, device=None):
        super().__init__()
        self.device = device
        self.segment_ranges = segment_ranges or [
            (10, 20, 0.5, 0.1), (20, 30, 0.4, 0.12),
            (30, 40, 0.3, 0.14), (40, 50, 0.2, 0.16),
            (50, 60, 0.1, 0.18), (60, 70, 0.05, 0.2)
        ]
    def compute_weights(self, target):
        EPS = 1e-6
        weights = torch.full_like(target, 0.1)  # 默认权重0.1        
        for start, end, steepness, base_w in self.segment_ranges:
            mask = (target >= start) & (target < end)
            x = ((target - start) / (end - start + EPS)).clamp(0, 1)
            delta_w = (1.0 - base_w) * (0.7 - steepness)
            seg_weights = base_w + delta_w * (x / (x + steepness*(1 - x) + EPS))
            weights = torch.where(mask, seg_weights, weights)        
        weights[target >= 70] = 1.0
        return weights
    def forward(self, output, target):
        """
        非降维(reduction='none')计算流程:
        1. 计算逐元素L1损失
        2. 生成动态权重矩阵
        3. 返回加权损失张量（保持输入维度）
        """
        # 保持维度的L1损失 (B,C,H,W)
        l1_loss = F.l1_loss(output, target, reduction='none')        
        weights = self.compute_weights(target.detach())  # 切断梯度  
        # weighted_loss = torch.mean(weights * l1_loss)   
        weighted_loss =  weights * l1_loss  
        return weighted_loss
# L1loss = WeightedL1Loss(device= device)

import torch
import torch.nn as nn
import torch.nn.functional as F
from segment_anything import sam_model_registry
class SAMLoss1(nn.Module):
    def __init__(self, model_type='vit_b', checkpoint_path=None):
        super().__init__()
        self.sam = sam_model_registry[model_type](checkpoint=None)
        if checkpoint_path:
            state_dict = torch.load(checkpoint_path)
            self.sam.load_state_dict(state_dict)        
        self.image_encoder = self.sam.image_encoder.eval()
        for param in self.image_encoder.parameters():
            param.requires_grad = False        
        self.patch_size = self.image_encoder.patch_embed.proj.kernel_size[0]        
        self.original_pos_embed = self.image_encoder.pos_embed        
        self.register_buffer('mean', torch.tensor([0.485, 0.456, 0.406]).view(1, 3, 1, 1))
        self.register_buffer('std', torch.tensor([0.229, 0.224, 0.225]).view(1, 3, 1, 1))        
        self.loss = nn.MSELoss()
    def adjust_pos_embed(self, x):
        """
        动态调整 pos_embed 以匹配输入尺寸
        Args:
            x: 输入张量 (B, C, H, W)
        """
        B, _, H, W = x.shape
        h, w = H // self.patch_size, W // self.patch_size        
        if (h, w) != self.original_pos_embed.shape[1:3]:
            pos_embed = self.original_pos_embed.permute(0, 3, 1, 2)  # (1, C, H_orig, W_orig)
            pos_embed = F.interpolate(
                pos_embed,
                size=(h, w),
                mode='bilinear',
                align_corners=False
            ).permute(0, 2, 3, 1)  # (1, h, w, C)            
            self.image_encoder.pos_embed = nn.Parameter(pos_embed, requires_grad=False)
        else:
            self.image_encoder.pos_embed = self.original_pos_embed
    def preprocess(self, x):
        """预处理：通道扩展 + 归一化 + 尺寸调整"""
        if x.shape[1] == 1:
            x = x.expand(-1, 3, -1, -1)  # 单通道→三通道
        x = (x - self.mean) / self.std        
        B, C, H, W = x.shape
        H_new = (H // self.patch_size) * self.patch_size
        W_new = (W // self.patch_size) * self.patch_size
        if H != H_new or W != W_new:
            x = F.interpolate(
                x,
                size=(H_new, W_new),
                mode='bilinear',
                align_corners=False
            )
        return x
    def forward(self, input, target):
        input = self.preprocess(input)
        target = self.preprocess(target)        
        self.adjust_pos_embed(input)        
        with torch.no_grad():
            input_feat = self.image_encoder(input)
            target_feat = self.image_encoder(target)        
        return self.loss(input_feat, target_feat)   

import torch
import torch.nn as nn
import torch.nn.functional as F
from segment_anything import sam_model_registry
class SAMLoss2(nn.Module):
    def __init__(self, model_type='vit_b', checkpoint_path=None):
        super().__init__()
        self.sam = sam_model_registry[model_type](checkpoint=None)
        if checkpoint_path:
            state_dict = torch.load(checkpoint_path)
            self.sam.load_state_dict(state_dict)        
        self.image_encoder = self.sam.image_encoder.eval()
        for param in self.image_encoder.parameters():
            param.requires_grad = False        
        self.patch_size = self.image_encoder.patch_embed.proj.kernel_size[0]       
        self.original_pos_embed = self.image_encoder.pos_embed        
        self.loss = nn.MSELoss()
    def adjust_pos_embed(self, x):
        """
        动态调整 pos_embed 以匹配输入尺寸
        Args:
            x: 输入张量 (B, C, H, W)
        """
        B, _, H, W = x.shape
        h, w = H // self.patch_size, W // self.patch_size        
        if (h, w) != self.original_pos_embed.shape[1:3]:
            pos_embed = self.original_pos_embed.permute(0, 3, 1, 2)  # (1, C, H_orig, W_orig)
            pos_embed = F.interpolate(
                pos_embed,
                size=(h, w),
                mode='bilinear',
                align_corners=False
            ).permute(0, 2, 3, 1)  # (1, h, w, C)            
            self.image_encoder.pos_embed = nn.Parameter(pos_embed, requires_grad=False)
        else:
            self.image_encoder.pos_embed = self.original_pos_embed
    def preprocess(self, x):
        """预处理：仅通道扩展 + 尺寸调整（跳过归一化）"""
        if x.shape[1] == 1:
            x = x.expand(-1, 3, -1, -1)  # 单通道→三通道        
        B, C, H, W = x.shape
        H_new = (H // self.patch_size) * self.patch_size
        W_new = (W // self.patch_size) * self.patch_size
        if H != H_new or W != W_new:
            x = F.interpolate(
                x,
                size=(H_new, W_new),
                mode='bilinear',
                align_corners=False
            )
        return x
    def forward(self, input, target):
        # 预处理（input和target均不归一化）
        input = self.preprocess(input)
        target = self.preprocess(target)        
        # 动态调整 pos_embed
        self.adjust_pos_embed(input)        
        # 计算特征
        with torch.no_grad():
            input_feat = self.image_encoder(input)
            target_feat = self.image_encoder(target)        
        return self.loss(input_feat, target_feat)
#saml = SAMLoss(checkpoint_path = "/mnt/wtx_weather_forecast/scx/stat/sat/sat2radar/sam_vit_b_01ec64.pth.1").to(device)