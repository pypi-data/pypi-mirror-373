# https://github.com/pytorch/examples/blob/master/imagenet/main.py
class MetricTracker(object):
    """Computes and stores the average and current value"""
    def __init__(self):
        self.reset()
    def reset(self):
        self.val = 0
        self.avg = 0
        self.sum = 0
        self.count = 0
    def update(self, val, n=1):
        self.val = val
        self.sum += val * n
        self.count += n
        self.avg = self.sum / self.count
"""
train_acc = metrics.MetricTracker()
train_acc.update(metrics.acc(outputs, labels,threshold=0.1), outputs.size(0))
train_acc.avg
"""


from tqdm import tqdm

class TrainingManager:
    def __init__(self, loader, description="Training Progress", log_file=None):
        """
        封装进度条和日志记录的训练管理类
        :param loader: 数据加载器
        :param description: 进度条描述
        :param log_file: 日志文件路径，可选
        """
        self.loader = tqdm(loader, desc=description)
        self.metrics = {}
        self.log_file = log_file
        if log_file:
            with open(log_file, 'w') as f:
                headers = "Epoch,Step," + ",".join(self.metrics.keys()) + "\n"
                f.write(headers)

    def add_metric(self, name, initial_value=0.0):
        """
        添加指标用于追踪
        :param name: 指标名称
        :param initial_value: 初始值
        """
        self.metrics[name] = Metric(initial_value)

    def update_metrics(self, **kwargs):
        """
        更新指定的指标值
        :param kwargs: 关键字参数，指标名和更新值
        """
        for name, value in kwargs.items():
            if name in self.metrics:
                self.metrics[name].update(value)

    def log_progress(self, epoch, step):
        """
        更新进度条和日志文件
        :param epoch: 当前训练轮次
        :param step: 当前训练步骤
        """
        description = f"Epoch {epoch}: " + " ".join(
            [f"{name}: {metric.avg:.4f}" for name, metric in self.metrics.items()]
        )
        self.loader.set_description(description)

        if self.log_file:
            with open(self.log_file, 'a') as f:
                line = f"{epoch},{step}," + ",".join([f"{metric.avg:.4f}" for metric in self.metrics.values()]) + "\n"
                f.write(line)

    def close(self):
        """关闭进度条"""
        self.loader.close()

class Metric:
    def __init__(self, initial_value=0.0):
        """
        用于追踪的指标
        :param initial_value: 初始值
        """
        self.total = initial_value
        self.count = 0
        self.avg = initial_value

    def update(self, value, count=1):
        """
        更新指标值
        :param value: 新增的值
        :param count: 数据数量，默认1
        """
        self.total += value * count
        self.count += count
        self.avg = self.total / self.count

# 示例代码
if __name__ == "__main__":
    # 假设 train_dataloader 是数据加载器，示例模拟100条数据
    train_dataloader = [{"sat_img": None, "map_img": None} for _ in range(100)]

    manager = TrainingManager(train_dataloader, description="Training Progress", log_file="training_log.csv")
    manager.add_metric("Loss")
    manager.add_metric("Accuracy")
    manager.add_metric("Ts")
    manager.add_metric("Fsc")
    manager.add_metric("Far")

    for epoch in range(3):  # 模拟3个epoch
        for idx, data in enumerate(manager.loader):
            # 模拟训练过程的计算
            loss_value = 0.5 + idx * 0.01
            accuracy_value = 0.8 - idx * 0.001
            ts_value = 0.7 + idx * 0.001
            fsc_value = 0.6 + idx * 0.002
            far_value = 0.2 + idx * 0.001

            # 更新指标
            manager.update_metrics(
                Loss=loss_value,
                Accuracy=accuracy_value,
                Ts=ts_value,
                Fsc=fsc_value,
                Far=far_value
            )

            # 记录进度和日志
            manager.log_progress(epoch, idx)

    # 关闭进度条
    manager.close()