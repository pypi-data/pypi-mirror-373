import torch

class OptimizerWithScheduler:
    def __init__(self, model, lr=0.001, step_size=40, gamma=0.1):
        """
        初始化优化器和学习率调度器。
        :param model: 要优化的模型
        :param lr: 初始学习率
        :param step_size: 调度器每隔多少个 epoch 调整学习率
        :param gamma: 调度器调整学习率的乘法因子
        """
        self.optimizer = torch.optim.Adam(model.parameters(), lr=lr)
        self.lr_scheduler = torch.optim.lr_scheduler.StepLR(
            self.optimizer, step_size=step_size, gamma=gamma
        )
    def zero_grad(self):
        self.optimizer.zero_grad()
    def step(self):
        self.optimizer.step()
    def step_scheduler(self):
        self.lr_scheduler.step()
    def get_lr(self):
        return self.optimizer.param_groups[0]['lr']
"""  
if __name__ == "__main__":
    model = torch.nn.Linear(10, 1)
    optimizer_with_scheduler = OptimizerWithScheduler(model, lr=0.001, step_size=40, gamma=0.1)
    for epoch in range(100):
        optimizer_with_scheduler.step_scheduler()
        for idx, data in enumerate(loader):
            inputs = data["sat_img"].cuda()
            labels = data["map_img"].cuda()
            optimizer_with_scheduler.zero_grad()
            loss = torch.randn(1)  # 仅为示例
            loss.backward()   
            optimizer_with_scheduler.step()  
            print(f"Epoch {epoch + 1}, Learning Rate: {optimizer_with_scheduler.get_lr()}")
"""
