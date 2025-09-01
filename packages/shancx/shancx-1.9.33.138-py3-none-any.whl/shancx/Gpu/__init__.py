#!/usr/bin/python
# -*- coding: utf-8 -*-
# @Time : 2024/10/17 上午午10:40
# @Author : shancx
# @File : __init__.py
# @email : shanhe12@163.com
import torch
def CheckGpuPlus(num=1):
    if torch.cuda.is_available():
        print(f"CUDA is available. Number of GPUs available: {torch.cuda.device_count()}")
        
        for i in range(torch.cuda.device_count()):
            print(f"GPU {i}: {torch.cuda.get_device_name(i)}")
        device = torch.device(f'cuda:{num}' if torch.cuda.is_available() else 'cpu')   
        return device
    else:
        print("CUDA is not available. Using CPU.")
        return None

#pd.concat(filter(None, results))
#valid_results = [df for df in results if isinstance(df, pd.DataFrame) and not df.empty]

import os
def visDevices(device_ids):
    if isinstance(device_ids, int):
        device_ids = str(device_ids)
    elif isinstance(device_ids, list):
        device_ids = ",".join(map(str, device_ids))
    os.environ["CUDA_VISIBLE_DEVICES"] = device_ids
    if torch.cuda.is_available():
        print(f"Visible GPUs: {device_ids}")
        print(f"Current visible GPUs: {os.environ.get('CUDA_VISIBLE_DEVICES')}")
        for device_id in device_ids.split(","):
            if not torch.cuda.device(int(device_id)):
                print(f"Warning: GPU {device_id} is not available.")
    else:
        print("No GPU available. Using CPU.")

import torch
import torch.nn as nn

def multiGpu(model, gpu_ids):
    # 检查是否有可用的 GPU
    if not torch.cuda.is_available():
        print("CUDA is not available. Using CPU.")
        device = torch.device("cpu")
        return model.to(device), device
    device = torch.device(f"cuda:{gpu_ids[0]}")
    if len(gpu_ids) > 1:
        print(f"Using {len(gpu_ids)} GPUs: {gpu_ids}")
        model = nn.DataParallel(model, device_ids=gpu_ids)
    else:
        print(f"Using GPU: {gpu_ids[0]}")
    model = model.to(device)
    return model, device