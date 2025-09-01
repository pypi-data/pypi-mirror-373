#!/usr/bin/python
# -*- coding: utf-8 -*-
import torch
import torchvision.transforms as transforms
import cv2
import numpy as np
from typing import List, Tuple
from PIL import Image
import os
class ImageProcessor:
    """Handles image preprocessing and transformations"""
    
    def __init__(self):
        self.transform = transforms.Compose([
            transforms.Resize(256),
            transforms.CenterCrop(224),
            transforms.ToTensor(),
            transforms.Normalize(
                mean=[0.485, 0.456, 0.406],
                std=[0.229, 0.224, 0.225]
            )
        ])
        
    def preprocess_image(self, image_path: str) -> torch.Tensor:
        """Load and preprocess image for model input"""
        try:
            if not os.path.exists(image_path):
                raise FileNotFoundError(f"Image file not found at {image_path}")
                
            image = cv2.imread(image_path)
            if image is None:
                raise ValueError(f"Unable to read image at {image_path}")
                
            # Convert BGR to RGB
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            # Convert to PIL Image for torchvision transforms
            image = Image.fromarray(image)
            return self.transform(image).unsqueeze(0)
        except Exception as e:
            print(f"Error processing image: {e}")
            raise

# if __name__ == "__main__":
#     image_path = "./space_shuttle.jpg"
#     image_processor = ImageProcessor()
#     input_tensor = image_processor.preprocess_image(image_path)

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

    """
    model = MyModel()
    gpu_ids = [5, 6, 7]
    model, device = setup_multi_gpu(model, gpu_ids)
    print(f"Model is on device: {device}")
    data = torch.randn(10, 3, 224, 224).to(device)
    output = model(data)
    """

