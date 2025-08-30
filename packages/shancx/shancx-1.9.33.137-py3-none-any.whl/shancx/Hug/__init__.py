#!/usr/bin/python
# -*- coding: utf-8 -*-
# gdown --folder https://drive.google.com/drive/folders/1D3bf2G2o4Hv-Ale26YW18r1Wrh7oIAwK  文件夹下所有内容太
from modelscope.hub.snapshot_download import snapshot_download
model_dir = snapshot_download('', cache_dir='autodl-tmp', revision='master', ignore_file_pattern='.bn')
from datasets import load_dataset
dataset = load_dataset("ayz2/ldm_pdes", download_mode="force_redownload")
print(dataset)
# dataset.save_to_disk('/path/to/save/dataset')
for split_name, split_dataset in dataset.items():
    chunk_size = 5000  # 每片的样本数量，可根据内存大小调整
    for i in range(0, len(split_dataset), chunk_size):
        subset = split_dataset.select(range(i, min(i + chunk_size, len(split_dataset))))
        subset.save_to_disk(f"./{split_name}_chunk_{i // chunk_size}")

from huggingface_hub import hf_hub_download
from shancx import crDir
# 下载权重文件
repo_id = "ayz2/ldm_pdes"
filename = "ae_cylinder.ckpt"
crDir("/mnt/wtx_weather_forecast/scx/ldm_pdes_checkpoint")
save_dir = "/mnt/wtx_weather_forecast/scx/ldm_pdes_checkpoint"
save_path = hf_hub_download(repo_id=repo_id, filename=filename, cache_dir=save_dir)
 

print(f"权重文件已下载到: {save_path}")


from modelscope.hub.snapshot_download import snapshot_download
crDir("/mnt/wtx_weather_forecast/scx/ldm_pdes_checkpoint")
save_dir = "/mnt/wtx_weather_forecast/scx/ldm_pdes_checkpoint"
model_dir = snapshot_download('ayz2/ldm_pdes', cache_dir=save_dir, revision='master', ignore_file_pattern='.bn')     下载 ae_cylinder.ckpt"


from modelscope.hub.snapshot_download import snapshot_download
from shancx import crDir
save_dir = "/mnt/wtx_weather_forecast/scx/ldm_pdes_checkpoint"
crDir(save_dir)
model_dir = snapshot_download(
    'ayz2/ldm_pdes',
    cache_dir=save_dir,
    revision='master',
    ignore_file_pattern='.bn')
print(f"模型已下载到: {model_dir}")





from google.colab import drive
import requests
import os

# 挂载 Google Drive
drive.mount('/content/drive')
ptname = "ae_cylinder.ckpt"
# 文件下载的URL
file_url = f"https://huggingface.co/datasets/ayz2/ldm_pdes/resolve/main/{ptname}"

# Google Drive中的保存路径（修改为你想保存的位置）
output_path = "/content/drive/My Drive/{ptname}"

# 下载文件并保存到指定路径
def download_file(url, output_path):
    try:
        with requests.get(url, stream=True) as response:
            response.raise_for_status()
            with open(output_path, "wb") as file:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:  # 防止空块
                        file.write(chunk)
        print(f"文件已成功下载并保存到 Google Drive: {output_path}")
    except Exception as e:
        print(f"下载文件时出错: {e}")
download_file(file_url, output_path)

import zipfile
def unzip_file(zip_path, extract_to):
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_to)
unzip_file(output_path, os.getcwd())