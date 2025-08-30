#!/usr/bin/python
# -*- coding: utf-8 -*-
# @Time : 2025/03/14 下午19:22
# @Author : shancx
# @File : __init__.py
# @email : shanhe12@163.com


from torch.utils.tensorboard import SummaryWriter
from datetime import datetime
class Boardlogger:
    def __init__(self, log_dir=None): self.writer = SummaryWriter(log_dir or f'runs/{datetime.now().strftime("%Y%m%d_%H%M%S")}')
    def log(self, tag, value, step): self.writer.add_scalar(tag, value, step)
    def close(self): self.writer.close()
"""
Board = Boardlogger()
Board.log('Train/Loss', 0.1, 1)  # 记录训练损失
Board.log('Val/IoU', 0.8, 1)     # 记录验证 IoU
Board.close()
tensorboard --logdir=runs --port=6006 --bind_all    进入到训练目录文件夹下 启动才可以 

from torch.utils.tensorboard import SummaryWriter
writer = SummaryWriter(f'runs/{datetime.now().strftime("%Y%m%d_%H%M%S")}')
writer.add_scalar('Train/Loss', loss.item(), epoch * len(train_loader) + i)
writer.close()
""" 

 