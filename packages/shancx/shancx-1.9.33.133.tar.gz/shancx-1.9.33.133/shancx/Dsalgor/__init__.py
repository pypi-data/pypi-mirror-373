#!/usr/bin/python
# -*- coding: utf-8 -*-
# @Time : 2024/10/17 上午午10:40
# @Author : shancx
# @File : __init__.py
# @email : shanhe12@163.com
 
def quick_sort(arr):
    if len(arr) <= 1:
        return arr
    pivot = arr[len(arr) // 2]
    left = [x for x in arr if x < pivot]
    middle = [x for x in arr if x == pivot]
    right = [x for x in arr if x > pivot]
    return quick_sort(left) + middle + quick_sort(right)
def sort_dict_by_key(d):
    sorted_dict = {key: d[key] for key in sorted(d.keys())}
    return sorted_dict
from tqdm import tqdm
class TrainingManager:
    def __init__(self, loader, desc="Training Progress", log_file=None):
        self.loader = tqdm(loader, desc=desc)
        self.metrics = {}
        self.log_file = log_file
        if log_file:
            with open(log_file, 'w') as f:
                headers = "Epoch,Step," + ",".join(self.metrics.keys()) + "\n"
                f.write(headers)
    def add_metric(self, name, initial_value=0.0):
        self.metrics[name] = Metric(initial_value)        ###用的另外一个更新类计算均值的
    def update_metrics(self, **kwargs):
        for name, value in kwargs.items(): #param kwargs: 关键字参数，指标名和更新值
            if name in self.metrics:
                self.metrics[name].update(value)
    def log_progress(self, epoch, step):
        description = f"Epoch {epoch}: " + " ".join(
            [f"{name}: {metric.avg:.4f}" for name, metric in self.metrics.items()]
        )
        self.loader.set_description(description)
        if self.log_file:
            with open(self.log_file, 'a') as f:
                line = f"{epoch},{step}," + ",".join([f"{metric.avg:.4f}" for metric in self.metrics.values()]) + "\n"
                f.write(line)
    """ 
    description = f"Epoch {epoch}: " + " ".join(
            [f"{name}: {metric.avg:.4f}" for name, metric in self.metrics.items()]
        )
    def log_progress1(self,description):
        self.loader.set_description(description)
    """
    def close(self):
        self.loader.close()
class Metric:
    def __init__(self, initial_value=0.0):
        self.total = initial_value
        self.count = 0
        self.avg = initial_value
    def update(self, value, count=1):
        self.total += value * count
        self.count += count
        self.avg = self.total / self.count
if __name__ == "__main__":
    train_dataloader = [{"sat_img": None, "map_img": None} for _ in range(100)]
    manager = TrainingManager(train_dataloader, description="Training Progress", log_file="training_log.csv")
    manager.add_metric("Loss")
    manager.add_metric("Accuracy")
    manager.add_metric("Ts")
    manager.add_metric("Fsc")
    manager.add_metric("Far")
    for epoch in range(3):  # 模拟3个epoch
        for idx, data in enumerate(manager.loader):
            loss_value = 0.5 + idx * 0.01
            accuracy_value = 0.8 - idx * 0.001
            ts_value = 0.7 + idx * 0.001
            fsc_value = 0.6 + idx * 0.002
            far_value = 0.2 + idx * 0.001
            manager.update_metrics(
                Loss=loss_value,
                Accuracy=accuracy_value,
                Ts=ts_value,
                Fsc=fsc_value,
                Far=far_value
            )
            manager.log_progress(epoch, idx)
    manager.close()