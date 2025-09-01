# 加载最佳模型权重
import torch
import matplotlib.pyplot as plt
from shancx import crDir
def Fakeimage(generator,device,torchvision.utils.make_grid,):
    generator.load_state_dict(torch.load('/home/scx/train_Gan/best_generator_weights.pth'))
    # 设置模型为评估模式
    generator.eval()
    with torch.no_grad():
        fixed_noise = torch.randn(64, 100, device=device)  # 将噪声张量直接创建在 GPU 上
        fake_images = generator(fixed_noise)    
        # 检查生成图像的形状
        print(f"生成的图像形状: {fake_images.shape}")    
        # 反归一化处理
        fake_images = (fake_images + 1) / 2  # 将图像像素值从[-1, 1]映射到[0, 1]  
        print(f"图像最小值: {fake_images.min()}, 最大值: {fake_images.max()}")
        grid = torchvision.utils.make_grid(fake_images, nrow=8, normalize=True)  # 设置normalize=True以确保正确的缩放
        grid_cpu = grid.cpu().detach().numpy()
        plt.imshow(grid_cpu.transpose(1, 2, 0))  # 调整图像通道顺序为(H, W, C)
        plt.axis('off')  # 关闭坐标轴显示
        outPath = './fake_images/best_weights_fake_images.png'
        crDir(outPath)
        plt.savefig(outPath)
        plt.close()
