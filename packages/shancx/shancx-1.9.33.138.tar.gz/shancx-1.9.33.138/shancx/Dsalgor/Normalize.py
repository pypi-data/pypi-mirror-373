 
from torchvision.transforms import Resize# Function to calculate valid size based on scale factor
def get_valid_size(size, scale_factor=2):
    return size - (size % scale_factor)
# Function to resize a high-resolution image to a low-resolution image
def resize_to_low_res(high_res_image, scale_factor):
    _, width, height = high_res_image.size()    
    # Get valid width and height divisible by the scale factor
    width = get_valid_size(width, scale_factor)
    height = get_valid_size(height, scale_factor)    
    # Crop the high-res image to the valid dimensions
    high_res_image = high_res_image[:, :width, :height]    
    # Create the low-res image by resizing the high-res image
    low_res_image = Resize((width // scale_factor, height // scale_factor))(high_res_image)    
    return low_res_image
"""

cuda-version              11.8                 hcce14f8_3
cudatoolkit               11.8.0               h6a678d5_0
cudnn                     8.9.2.26               cuda11_0
nvidia-cuda-cupti-cu12    12.1.105                 pypi_0    pypi
nvidia-cuda-nvrtc-cu12    12.1.105                 pypi_0    pypi
nvidia-cuda-runtime-cu12  12.1.105                 pypi_0    pypi
nvidia-cudnn-cu12         8.9.2.26                 pypi_0    pypi
mqpf conda install pytorch  torchvision torchaudio  cudatoolkit=11.8 -c pytorch  
conda install cudnn=8.9.2.26 cudatoolkit=11.8 
resunet pip install torch==2.4.0  torchvision    torchaudio
conda install cudnn==8.9.2.26 cudatoolkit==11.8.0
conda install pytorch=2.2.2 torchvision torchaudio cudatoolkit=11.8 -c pytorch
resunet pip install torch==2.4.0  torchvision    torchaudio
pip install protobuf==3.20

my-envmf1
torch                     2.3.0                    pypi_0    pypi
torchvision               0.18.0                   pypi_0    pypi

RES:
torch                     2.4.0                    pypi_0    pypi
torchaudio                2.2.2                 py311_cpu    pytorch
torchsummary              1.5.1                    pypi_0    pypi
torchvision               0.19.0                   pypi_0    pypi

mqpf:
torch                     2.3.1                    pypi_0    pypi
torchaudio                2.3.1                    pypi_0    pypi
torchvision               0.18.1                   pypi_0    pypi
onnxruntime-gpu           1.16.0
onnx                      1.15.0 
numpy                     1.26.4

vllm:
torch                     2.1.2                    pypi_0    pypi
torchvision               0.15.1+cu118             pypi_0    pypi
vllm                      0.2.7                    pypi_0    pypi

import torch
print("CUDA available:", torch.cuda.is_available())
print("CUDA version:", torch.version.cuda)
print("GPU device:", torch.cuda.get_device_name(0) if torch.cuda.is_available() else "No GPU")
nvidia-smi 
nvcc --version
系统已经检测到物理 GPU（NVIDIA GeForce RTX 4090）和 NVIDIA 驱动，同时安装了 CUDA 12.1。然而，PyTorch 没有正确检测到 GPU，可能是因为 PyTorch 版本与 CUDA 驱动不兼容，或者环境变量未正确配置。

pip install torch==2.3.1    torchvision==0.18.1  

"""
