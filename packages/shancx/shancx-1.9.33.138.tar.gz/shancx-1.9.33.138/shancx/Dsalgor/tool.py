import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, Dataset
import torchvision.transforms as transforms
from torchvision import transforms
import os
from PIL import Image
import numpy as np
from tqdm import tqdm
import glob

# 简化的 ResUNet 架构
class ResUNet(nn.Module):
    def __init__(self, in_channels, out_channels):
        super(ResUNet, self).__init__()
        self.encoder = ResNetEncoder(in_channels)
        self.decoder = UNetDecoder(out_channels)
    
    def forward(self, x):
        enc_out = self.encoder(x)
        dec_out = self.decoder(enc_out)
        return dec_out

class ResNetEncoder(nn.Module):
    def __init__(self, in_channels):
        super(ResNetEncoder, self).__init__()
        self.conv1 = nn.Conv2d(in_channels, 64, kernel_size=3, padding=1)
        self.conv2 = nn.Conv2d(64, 128, kernel_size=3, padding=1)
        self.conv3 = nn.Conv2d(128, 256, kernel_size=3, padding=1)
        # 可以继续添加更多层
        
    def forward(self, x):
        x = torch.relu(self.conv1(x))
        x = torch.relu(self.conv2(x))
        x = torch.relu(self.conv3(x))
        return x

class UNetDecoder(nn.Module):
    def __init__(self, out_channels):
        super(UNetDecoder, self).__init__()
        self.upconv = nn.ConvTranspose2d(256, 128, kernel_size=2, stride=2)
        self.final_conv = nn.Conv2d(128, out_channels, kernel_size=1)
    
    def forward(self, x):
        x = self.upconv(x)
        x = self.final_conv(x)
        return x

# 自定义数据集类
class SatelliteDataset(Dataset):
    def __init__(self, image_dir, mask_dir, transform=None):
        self.image_dir = image_dir
        self.mask_dir = mask_dir
        self.image_filenames = os.listdir(image_dir)
        self.mask_filenames = os.listdir(mask_dir)
        self.transform = transform

    def __len__(self):
        return len(self.image_filenames)

    def __getitem__(self, idx):
        img_name = self.image_filenames[idx]
        mask_name = self.mask_filenames[idx]
        
        img = Image.open(os.path.join(self.image_dir, img_name)).convert("RGB")
        mask = Image.open(os.path.join(self.mask_dir, mask_name)).convert("L")  # 单通道灰度图
        
        if self.transform:
            img = self.transform(img)
            mask = self.transform(mask)
        
        return img, mask

# 数据增强与预处理
transform = transforms.Compose([
    transforms.Resize((256, 256)),  # 调整图像大小
    transforms.ToTensor(),  # 转换为Tensor并归一化到[0, 1]
])
# 加载数据集
image_dir = 'path/to/your/images'  # 输入图像路径
mask_dir = 'path/to/your/masks'    # 分割掩膜路径
dataset = SatelliteDataset(image_dir, mask_dir, transform)
dataloader = DataLoader(dataset, batch_size=8, shuffle=True)
# 定义模型、损失函数和优化器
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
model = ResUNet(in_channels=3, out_channels=1).to(device)  # 3个输入通道(RGB)，1个输出通道（二值化分割）
criterion = nn.BCEWithLogitsLoss()  # 用于二分类任务的损失函数
optimizer = optim.Adam(model.parameters(), lr=1e-4)
# 训练循环
num_epochs = 20
for epoch in range(num_epochs):
    model.train()
    running_loss = 0.0

    for imgs, masks in dataloader:
        imgs, masks = imgs.to(device), masks.to(device)

        # 正向传播
        outputs = model(imgs)
        
        # 计算损失
        loss = criterion(outputs.squeeze(1), masks.float())  # 去除多余的维度并将掩膜转换为float
        running_loss += loss.item()

        # 反向传播和优化
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

    avg_loss = running_loss / len(dataloader)
    print(f"Epoch [{epoch+1}/{num_epochs}], Loss: {avg_loss:.4f}")

# 保存训练好的模型
torch.save(model.state_dict(), 'resunet_model.pth')


"""   --------------Resunet-------------------Dataset
from torch.utils.data import DataLoader
from torch.utils.data import Dataset
class ToTensorTarget(object):
    def __call__(self, sample):
        sat_img, map_img = sample["sat_img"], sample["map_img"]

        # swap color axis because
        # numpy image: H x W x C
        # torch image: C X H X W

        return {
            "sat_img": transforms.functional.to_tensor(sat_img).permute(1,2,0),  #(H, W, C) -->transforms.functional.to_tensor(sat_img)-->(C, H, W) --.permute(1,2,0)-->(H, W, C)  H 是图像的高度,W 是宽度,C 是通道数
            "map_img": torch.from_numpy(map_img).unsqueeze(0).float(),
        }  # unsqueeze for the channel dimension
        
# 自定义数据集类
class npyDataset_regression(Dataset):
    def __init__(self, args, train=True, transform=None):
        self.train = train
        self.path = args.train if train else args.valid
        self.mask_list = glob.glob(
            os.path.join(self.path, "mask", "*.npy"), recursive=True
        )
        self.transform = transform
    def __len__(self):
        return len(self.mask_list)
    def __getitem__(self, idx):
        try:    
               maskpath = self.mask_list[idx]
               image = np.load(maskpath.replace("mask", "input")).astype(np.float32)
               image = image[-2:,:,:]
               image[image<15] = np.nan
               ### 5-15dbz
               #image[image>20] = np.nan
               #image[image<5] = np.nan
               #mean = np.float32(9.81645766)
               #std = np.float32(10.172995)
               image_mask = image[-1,:,:].copy().reshape(256,256)
               image_mask[~np.isnan(image_mask)]=1
               #tmp = image[-2,:,:].reshape((256,256)) * image_mask
               #image[-2,:,:] = tmp.reshape((1,256,256))
               mask = np.load(maskpath).astype(np.float32)  
               mask = mask * image_mask
               image[np.isnan(image)]=0
               sample = {"x_img": image, "map_img": mask}
               if self.transform:
                   sample = self.transform(sample)
                   sample['maskpath'] = maskpath
               return sample
        except Exception as e:
               print(f"Error loading data at index {index}: {str(e)}")
               # 可以选择跳过当前样本或者返回一个默认值
               print(traceback.format_exc())
               loggers.info(traceback.format_exc())
               return None

dataset = npyDataset_regression(args, transform=transforms.Compose([ToTensorTarget()]))  #=transforms.Compose([dataloader_radar10.ToTensorTarget()])
dataloader = DataLoader(dataset, batch_size=8, shuffle=True)
loader = tqdm(dataloader, desc="training")
for idx, data in enumerate(loader):
    inputs = data["x_img"].cuda()
    labels = data["map_img"].cuda()
    optimizer.zero_grad()
    outputs = model(inputs)
""" 

"""" ------------Gan-------------
import torch
import torch.nn as nn
import torch.optim as optim
from torchvision import datasets, transforms
from torchvision.utils import save_image
import os

def save_model_weights(generator, discriminator, epoch):
    torch.save(generator.state_dict(), f'generator_epoch_{epoch}.pt')
    torch.save(discriminator.state_dict(), f'discriminator_epoch_{epoch}.pt')

def load_generator_weights(generator, weights_path, device='cuda:0'):
    generator.load_state_dict(torch.load(weights_path, map_location=device))
    generator.eval()  # Ensure generator is in evaluation mode after loading weights

def generate_images(generator, num_images, device='cuda:0'):
    generator.eval()  # Set the generator to evaluation mode
    noise = torch.randn(num_images, 100).to(device)  # Generate random noise
    with torch.no_grad():
        generated_images = generator(noise).cpu()  # Generate images from noise
    return generated_images

# Generator model
class Generator(nn.Module):
    def __init__(self):
        super(Generator, self).__init__()
        self.model = nn.Sequential(
            nn.Linear(100, 256),
            nn.ReLU(),
            nn.Linear(256, 64 * 64),
            nn.Tanh()  # Output range [-1, 1]
        )

    def forward(self, x):
        return self.model(x).view(-1, 1, 64, 64)

# Discriminator model
class Discriminator(nn.Module):
    def __init__(self):
        super(Discriminator, self).__init__()
        self.model = nn.Sequential(
            nn.Flatten(),
            nn.Linear(64 * 64, 256),
            nn.ReLU(),
            nn.Linear(256, 1),
            nn.Sigmoid()  # Output [0, 1]
        )

    def forward(self, x):
        return self.model(x)

# Training function
def train_gan(generator, discriminator, g_optimizer, d_optimizer, criterion, dataloader, epochs=50, device='cuda:0'):
    for epoch in range(epochs):
        for i, (real_images, _) in enumerate(dataloader):
            batch_size = real_images.size(0)
            real_images = real_images.to(device)
            real_images = (real_images - 0.5) * 2  # Normalize to [-1, 1]

            real_labels = torch.ones(batch_size, 1).to(device)
            fake_labels = torch.zeros(batch_size, 1).to(device)

            # Train discriminator
            d_optimizer.zero_grad()

            # Real image loss
            outputs = discriminator(real_images)
            d_loss_real = criterion(outputs, real_labels)
            d_loss_real.backward()

            # Fake image loss
            noise = torch.randn(batch_size, 100).to(device)
            fake_images = generator(noise)
            outputs = discriminator(fake_images.detach())
            d_loss_fake = criterion(outputs, fake_labels)
            d_loss_fake.backward()
            d_optimizer.step()

            # Train generator
            g_optimizer.zero_grad()
            outputs = discriminator(fake_images)
            g_loss = criterion(outputs, real_labels)
            g_loss.backward()
            g_optimizer.step()

            # Print loss
            if (i + 1) % 100 == 0:
                print(f'Epoch [{epoch + 1}/{epochs}], Step [{i + 1}/{len(dataloader)}], '
                      f'D Loss: {d_loss_real.item() + d_loss_fake.item()}, G Loss: {g_loss.item()}')

        # Save generated images and model weights every 10 epochs
        if (epoch + 1) % 10 == 0:
            save_image(fake_images.detach(), f'gan_images/epoch_{epoch + 1}.png')
            save_model_weights(generator, discriminator, epoch + 1)

# Data preprocessing and loader
transform = transforms.Compose([
    transforms.Resize(64),
    transforms.ToTensor(),
    transforms.Normalize((0.5,), (0.5,)),
])

if __name__ == '__main__':
    # Set device to the first GPU (cuda:0)
    device = torch.device('cuda:1' if torch.cuda.is_available() else 'cpu')
    generator = Generator().to(device)
    discriminator = Discriminator().to(device)

    # Load dataset
    dataset = datasets.MNIST(root='data', train=True, transform=transform, download=True)
    dataloader = torch.utils.data.DataLoader(dataset, batch_size=64,num_workers=20,shuffle=True) #num_workers=10,

    # Define loss function and optimizers
    criterion = nn.BCELoss()
    g_optimizer = optim.Adam(generator.parameters(), lr=0.0002, betas=(0.5, 0.999))
    d_optimizer = optim.Adam(discriminator.parameters(), lr=0.0002, betas=(0.5, 0.999))

    # Create directory for saving images
    os.makedirs('gan_images', exist_ok=True)

    # Train GAN
    train_gan(generator, discriminator, g_optimizer, d_optimizer, criterion, dataloader, epochs=10, device=device)

    # Load generator weights (replace with actual path)
    load_generator_weights(generator, 'generator_epoch_10.pt', device=device)

    # Generate images
    generated_images = generate_images(generator, 10, device=device)

    # Save generated images
    save_image(generated_images, 'generated_images.png', nrow=10, normalize=True)


"""

"""     
######################################## diffusion modle #########################################
import os
from PIL import Image
import torch
import torch.nn as nn
import torch.optim as optim
from torchvision.transforms import Compose, ToTensor, Resize
from torchvision.utils import save_image
from torch.utils.data import DataLoader, Dataset
import numpy as np

# 自定义数据集类
class ImageDataset(Dataset):
    def __init__(self, folder_path, low_res_size=(64, 64), high_res_size=(256, 256)):
        super().__init__()
        self.image_paths = [os.path.join(folder_path, fname) for fname in os.listdir(folder_path) if fname.endswith(('png', 'jpg', 'jpeg'))]
        self.low_res_transform = Compose([
            Resize(low_res_size),
            ToTensor()
        ])
        self.high_res_transform = Compose([
            Resize(high_res_size),
            ToTensor()
        ])
    
    def __len__(self):
        return len(self.image_paths)
    
    def __getitem__(self, idx):
        image = Image.open(self.image_paths[idx]).convert("RGB")
        low_res_image = self.low_res_transform(image)
        high_res_image = self.high_res_transform(image)
        return low_res_image, high_res_image

# 定义扩散模型中的去噪网络
class DenoisingUNet(nn.Module):
    def __init__(self):
        super(DenoisingUNet, self).__init__()
        self.encoder = nn.Sequential(
            nn.Conv2d(3, 64, kernel_size=3, stride=1, padding=1),
            nn.ReLU(),
            nn.Conv2d(64, 128, kernel_size=3, stride=2, padding=1),
            nn.ReLU()
        )
        self.middle = nn.Sequential(
            nn.Conv2d(128, 128, kernel_size=3, stride=1, padding=1),
            nn.ReLU()
        )
        self.decoder = nn.Sequential(
            nn.ConvTranspose2d(128, 64, kernel_size=3, stride=2, padding=1, output_padding=1),
            nn.ReLU(),
            nn.Conv2d(64, 3, kernel_size=3, stride=1, padding=1)
        )
        
    def forward(self, x):
        encoded = self.encoder(x)
        middle = self.middle(encoded)
        decoded = self.decoder(middle)
        return decoded

# 定义扩散过程的正向和反向过程
class DiffusionModel:
    def __init__(self, denoising_model, timesteps=1000):
        self.denoising_model = denoising_model
        self.timesteps = timesteps
        self.beta_schedule = self._linear_beta_schedule()
        self.alphas = 1.0 - self.beta_schedule
        self.alpha_cumprod = torch.tensor(np.cumprod(self.alphas).astype(np.float32))  # 转为Tensor类型

    def _linear_beta_schedule(self):
        return np.linspace(1e-4, 0.02, self.timesteps).astype(np.float32)

    def forward_diffusion(self, x, t):
        alpha_t = self.alpha_cumprod[t]
        noise = torch.randn_like(x)
        return torch.sqrt(alpha_t) * x + torch.sqrt(1 - alpha_t) * noise, noise

    def reverse_diffusion(self, x, t):
        alpha_t = self.alpha_cumprod[t]
        pred_noise = self.denoising_model(x)
        return (x - torch.sqrt(1 - alpha_t) * pred_noise) / torch.sqrt(alpha_t)

# 训练函数
def train_diffusion_model(model, dataloader, epochs=50, lr=1e-4):
    optimizer = optim.Adam(model.denoising_model.parameters(), lr=lr)
    loss_fn = nn.MSELoss()
    
    for epoch in range(epochs):
        epoch_loss = 0
        for low_res, high_res in dataloader:
            high_res = high_res.to('cuda')  # 使用GPU
            low_res = low_res.to('cuda')   # 使用GPU
            t = torch.randint(0, model.timesteps, (1,)).item()  # 随机选择时间步
            noisy_image, noise = model.forward_diffusion(high_res, t)
            noisy_image = noisy_image.to('cuda')  # 确保噪声图像在GPU上
            predicted_noise = model.denoising_model(noisy_image)
            
            loss = loss_fn(predicted_noise, noise)
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            epoch_loss += loss.item()
        print(f"Epoch {epoch + 1}/{epochs}, Loss: {epoch_loss / len(dataloader)}")

# 示例：生成高分辨率图像
def generate_high_res_image(model, low_res_image):
    t = model.timesteps - 1
    x = low_res_image.to('cuda')  # 使用GPU
    for step in reversed(range(t)):
        x = model.reverse_diffusion(x, step)
    return x.cpu()  # 返回到CPU

# 主函数
if __name__ == "__main__":
    # 模型初始化
    unet = DenoisingUNet().to('cuda')  # 将模型加载到GPU
    diffusion_model = DiffusionModel(denoising_model=unet)

    # 数据集路径
    folder_path = "/mnt/wtx_weather_forecast/scx/diffdataset/output_dataset/HR"  # 替换为包含图像的文件夹路径
    dataset = ImageDataset(folder_path)
    dataloader = DataLoader(dataset, batch_size=8, shuffle=True)

    # 训练模型
    print("开始训练模型...")
    train_diffusion_model(diffusion_model, dataloader)

    # 生成高分辨率图像
    print("生成高分辨率图像...")
    low_res_input, _ = dataset[0]  # 示例图像
    low_res_input = low_res_input.unsqueeze(0)  # 增加批次维度
    high_res_output = generate_high_res_image(diffusion_model, low_res_input)
    save_image(high_res_output, "high_res_output.png")
    print("高分辨率图像已保存为 'high_res_output.png'")



"""

"""
from torch.utils.data import random_split, DataLoader, Dataset, Subset
"""

"""
##############潜在空间，gan 模型
import os
from PIL import Image
import torch
import torch.nn as nn
import torch.optim as optim
from torchvision.transforms import Compose, ToTensor, Resize
from torch.utils.data import DataLoader, Dataset
import torch.nn.functional as F

# 确保数据和模型均加载到指定 GPU 上
device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
# 自定义数据集类
class ImageDataset(Dataset):
    def __init__(self, folder_path, low_res_size=(64, 64), high_res_size=(256, 256)):
        super().__init__()
        self.image_paths = [os.path.join(folder_path, fname) for fname in os.listdir(folder_path) if fname.endswith(('png', 'jpg', 'jpeg'))]
        self.low_res_transform = Compose([
            Resize(low_res_size),
            ToTensor()
        ])
        self.high_res_transform = Compose([
            Resize(high_res_size),
            ToTensor()
        ])
    
    def __len__(self):
        return len(self.image_paths)
    
    def __getitem__(self, idx):
        image = Image.open(self.image_paths[idx]).convert("RGB")
        low_res_image = self.low_res_transform(image)
        high_res_image = self.high_res_transform(image)
        return low_res_image, high_res_image

import torch
import torch.nn as nn
import torch.optim as optim
from torchvision import transforms

# 定义潜在空间编码器
class Encoder(nn.Module):
    def __init__(self, input_dim, latent_dim):
        super(Encoder, self).__init__()
        self.encoder = nn.Sequential(
            nn.Conv2d(input_dim, 64, kernel_size=4, stride=2, padding=1),
            nn.ReLU(),
            nn.Conv2d(64, 128, kernel_size=4, stride=2, padding=1),
            nn.ReLU(),
            nn.Conv2d(128, latent_dim, kernel_size=4, stride=2, padding=1)
        )
    
    def forward(self, x):
        return self.encoder(x)

# 定义潜在空间解码器
class Decoder(nn.Module):
    def __init__(self, latent_dim, output_dim):
        super(Decoder, self).__init__()
        self.decoder = nn.Sequential(
            nn.ConvTranspose2d(latent_dim, 128, kernel_size=4, stride=2, padding=1),
            nn.ReLU(),
            nn.ConvTranspose2d(128, 64, kernel_size=4, stride=2, padding=1),
            nn.ReLU(),
            nn.ConvTranspose2d(64, output_dim, kernel_size=4, stride=2, padding=1)
        )
    
    def forward(self, x):
        return self.decoder(x)

# 定义扩散模型
class DiffusionModel(nn.Module):
    def __init__(self, latent_dim):
        super(DiffusionModel, self).__init__()
        self.diffusion = nn.Sequential(
            nn.Conv2d(latent_dim, latent_dim, kernel_size=3, stride=1, padding=1),
            nn.ReLU(),
            nn.Conv2d(latent_dim, latent_dim, kernel_size=3, stride=1, padding=1)
        )
    
    def forward(self, x):
        return self.diffusion(x)

# 定义超分辨率模块
class SuperResolution(nn.Module):
    def __init__(self, input_dim, output_dim):
        super(SuperResolution, self).__init__()
        self.sr = nn.Sequential(
            nn.Conv2d(input_dim, 64, kernel_size=3, stride=1, padding=1),
            nn.ReLU(),
            nn.Conv2d(64, 64, kernel_size=3, stride=1, padding=1),
            nn.ReLU(),
            nn.Conv2d(64, output_dim, kernel_size=3, stride=1, padding=1)
        )
    
    def forward(self, x):
        return self.sr(x)

# 定义GAN判别器
class Discriminator(nn.Module):
    def __init__(self, input_dim):
        super(Discriminator, self).__init__()
        self.discriminator = nn.Sequential(
            nn.Conv2d(input_dim, 64, kernel_size=4, stride=2, padding=1),
            nn.ReLU(),
            nn.Conv2d(64, 128, kernel_size=4, stride=2, padding=1),
            nn.ReLU(),
            nn.Conv2d(128, 1, kernel_size=4, stride=2, padding=1)
        )
    
    def forward(self, x):
        return self.discriminator(x)

# 构建模型
latent_dim = 256
input_dim = 3
output_dim = 3

encoder = Encoder(input_dim, latent_dim)
decoder = Decoder(latent_dim, output_dim)
diffusion_model = DiffusionModel(latent_dim)
super_resolution = SuperResolution(output_dim, output_dim)
discriminator = Discriminator(output_dim)

# 定义优化器和损失函数
gen_optimizer = optim.Adam(list(encoder.parameters()) + 
                           list(decoder.parameters()) + 
                           list(diffusion_model.parameters()) + 
                           list(super_resolution.parameters()), lr=1e-4)
disc_optimizer = optim.Adam(discriminator.parameters(), lr=1e-4)
mse_loss = nn.MSELoss()
bce_loss = nn.BCEWithLogitsLoss()


# 训练过程函数
def train_step(generator_parts, discriminator, optimizers, images, device):
    encoder, decoder, diffusion_model, super_resolution = generator_parts
    gen_optimizer, disc_optimizer = optimizers

    low_res_images, high_res_images = images
    low_res_images = low_res_images.to(device)
    high_res_images = high_res_images.to(device)

    # 编码
    latent = encoder(low_res_images)

    # 扩散生成
    latent_diffused = diffusion_model(latent)

    # 解码
    reconstructed = decoder(latent_diffused)

    # 超分辨率生成
    high_res_generated = super_resolution(reconstructed)

    # 调整大小以匹配
    downsampled_high_res = F.interpolate(high_res_images, size=(64, 64), mode='bilinear', align_corners=False)
    upsampled_reconstructed = F.interpolate(reconstructed, size=(256, 256), mode='bilinear', align_corners=False)

    # 生成器损失 (重建 + 超分辨率 + 对抗)
    reconstruction_loss = nn.MSELoss()(reconstructed, downsampled_high_res)
    super_res_loss = nn.MSELoss()(upsampled_reconstructed, high_res_images)
    disc_fake = discriminator(high_res_generated)
    adversarial_loss = nn.BCEWithLogitsLoss()(disc_fake, torch.ones_like(disc_fake))
    gen_loss = reconstruction_loss + super_res_loss + adversarial_loss

    gen_optimizer.zero_grad()
    gen_loss.backward()
    gen_optimizer.step()

    # 判别器损失
    disc_real = discriminator(high_res_images)
    disc_loss_real = nn.BCEWithLogitsLoss()(disc_real, torch.ones_like(disc_real))
    disc_loss_fake = nn.BCEWithLogitsLoss()(disc_fake.detach(), torch.zeros_like(disc_fake))
    disc_loss = (disc_loss_real + disc_loss_fake) / 2

    disc_optimizer.zero_grad()
    disc_loss.backward()
    disc_optimizer.step()

    return gen_loss.item(), disc_loss.item()
from shancx.Dsalgor.CudaPrefetcher1 import CUDAPrefetcher1
def save_best_model(encoder, decoder, diffusion_model, super_resolution, discriminator, epoch):
    checkpoint = {
        'encoder': encoder.state_dict(),
        'decoder': decoder.state_dict(),
        'diffusion_model': diffusion_model.state_dict(),
        'super_resolution': super_resolution.state_dict(),
        'discriminator': discriminator.state_dict(),
    }
    torch.save(checkpoint, f"best_model_epoch_{epoch+1}.pth")
    print(f"Best model saved at epoch {epoch+1}.")
# 主训练循环
if __name__ == "__main__":
    # 模型初始化
    latent_dim = 256
    input_dim = 3
    output_dim = 3

    # 加载模型至指定设备
    encoder = Encoder(input_dim, latent_dim).to(device)
    decoder = Decoder(latent_dim, output_dim).to(device)
    diffusion_model = DiffusionModel(latent_dim).to(device)
    super_resolution = SuperResolution(output_dim, output_dim).to(device)
    discriminator = Discriminator(output_dim).to(device)

    generator_parts = (encoder, decoder, diffusion_model, super_resolution)

    # 定义优化器
    gen_optimizer = optim.Adam(
        list(encoder.parameters()) + 
        list(decoder.parameters()) + 
        list(diffusion_model.parameters()) + 
        list(super_resolution.parameters()), 
        lr=1e-4
    )
    disc_optimizer = optim.Adam(discriminator.parameters(), lr=1e-4)
    optimizers = (gen_optimizer, disc_optimizer)

    # 数据加载
    folder_path = "/mnt/wtx_weather_forecast/scx/diffdataset/output_dataset/HR"  # 数据集路径
    dataset = ImageDataset(folder_path)
    dataloader = DataLoader(dataset, batch_size=8, shuffle=True)
    dataloader = CUDAPrefetcher1(dataloader,device)
    num_epochs = 3
    best_gen_loss = float('inf')  # 初始化生成器最小损失值
    # 训练参数
    for epoch in range(num_epochs):
        for images in dataloader:
            gen_loss, disc_loss = train_step(generator_parts, discriminator, optimizers, images, device)
            print(f"Epoch [{epoch+1}/{num_epochs}], Gen Loss: {gen_loss:.4f}, Disc Loss: {disc_loss:.4f}")
            # 每个epoch保存最佳模型
            if gen_loss < best_gen_loss:
                best_gen_loss = gen_loss
                # 保存最佳模型权重
                save_best_model(encoder, decoder, diffusion_model, super_resolution, discriminator, epoch)
                print("save modle")

"""