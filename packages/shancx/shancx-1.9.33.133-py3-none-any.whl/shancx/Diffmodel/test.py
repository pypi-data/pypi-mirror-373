import torch
import torch.nn as nn
import torch.nn.functional as F
import matplotlib.pyplot as plt
import numpy as np
from sklearn.datasets import make_s_curve
import matplotlib.pyplot as plt
from shancx import crDir
s_curve, _ = make_s_curve(10**4, noise=0.1)
s_curve = s_curve[:, [0, 2]] / 10.0
dataset = torch.Tensor(s_curve).float()
num_steps = 100
# Define the beta schedule
betas = torch.linspace(-6, 6, num_steps)
betas = torch.sigmoid(betas) * (0.5e-2 - 1e-5) + 1e-5
alphas = 1 - betas
alphas_prod = torch.cumprod(alphas, 0)
alphas_prod_p = torch.cat([torch.tensor([1]).float(), alphas_prod[:-1]], 0)
alphas_bar_sqrt = torch.sqrt(alphas_prod)
one_minus_alphas_bar_log = torch.log(1 - alphas_prod)
one_minus_alphas_bar_sqrt = torch.sqrt(1 - alphas_prod)
assert alphas.shape == alphas_prod.shape == alphas_prod_p.shape == \
       alphas_bar_sqrt.shape == one_minus_alphas_bar_log.shape == \
       one_minus_alphas_bar_sqrt.shape
class MLPDiffusion(nn.Module):
    def __init__(self, n_steps, num_units=128):
        super(MLPDiffusion, self).__init__()
        self.linears = nn.ModuleList([
            nn.Linear(2, num_units),
            nn.ReLU(),
            nn.Linear(num_units, num_units),
            nn.ReLU(),
            nn.Linear(num_units, num_units),
            nn.ReLU(),
            nn.Linear(num_units, 2),
        ])
        self.step_embeddings = nn.ModuleList([
            nn.Embedding(n_steps, num_units),
            nn.Embedding(n_steps, num_units),
            nn.Embedding(n_steps, num_units),
        ])
    
    def forward(self, x, t):
        for idx, embedding_layer in enumerate(self.step_embeddings):
            t_embedding = embedding_layer(t)
            x = self.linears[2 * idx](x)
            x += t_embedding
            x = self.linears[2 * idx + 1](x)
        x = self.linears[-1](x)
        return x
import torch
import torch.nn as nn
import torch
import torch.nn as nn
class UNetDiffusion(nn.Module):
    def __init__(self, n_steps, num_units=128):
        super(UNetDiffusion, self).__init__()
        self.encoder1 = nn.Sequential(
            nn.Linear(2, num_units),
            nn.ReLU(),
            nn.Linear(num_units, num_units),
            nn.ReLU()
        )
        self.encoder2 = nn.Sequential(
            nn.Linear(num_units, num_units * 2),
            nn.ReLU(),
            nn.Linear(num_units * 2, num_units * 2),
            nn.ReLU()
        )
        self.encoder3 = nn.Sequential(
            nn.Linear(num_units * 2, num_units * 4),
            nn.ReLU(),
            nn.Linear(num_units * 4, num_units * 4),
            nn.ReLU()
        )
        self.decoder3 = nn.Sequential(
            nn.Linear(num_units * 4, num_units * 2),
            nn.ReLU(),
            nn.Linear(num_units * 2, num_units * 2),
            nn.ReLU()
        )
        self.decoder2 = nn.Sequential(
            nn.Linear(num_units * 2, num_units),
            nn.ReLU(),
            nn.Linear(num_units, num_units),
            nn.ReLU()
        )
        self.decoder1 = nn.Sequential(
            nn.Linear(num_units, 2), 
        )
        self.step_embeddings = nn.ModuleList([
            nn.Embedding(n_steps, num_units),
            nn.Embedding(n_steps, num_units),
            nn.Embedding(n_steps, num_units),
        ])

    def forward(self, x, t):
        # 对每个时间步 t，获取时间嵌入并将其加到输入特征中
        for idx, embedding_layer in enumerate(self.step_embeddings):
            t_embedding = embedding_layer(t)  # 获取当前时间步的嵌入向量
            if idx == 0:
                x = self.encoder1(x)
            elif idx == 1:
                x = self.encoder2(x)
            else:
                x = self.encoder3(x)
            x += t_embedding  # 将时间步的嵌入加到当前层输出
            if idx == 0:
                x = self.encoder1(x)
            elif idx == 1:
                x = self.encoder2(x)
            else:
                x = self.encoder3(x)
        # 解码器：逐层恢复
        x = self.decoder3(x)
        x = self.decoder2(x)
        x = self.decoder1(x)
        
        return x
def downsample_image(x, scale_factor=0.5, device=None):
    result = x * scale_factor
    return result
def p_sample(model, x, t, betas, one_minus_alphas_bar_sqrt, device):
    t = torch.tensor([t]).to(device)  # Move t to device
    # betas = betas.to(device)
    # one_minus_alphas_bar_sqrt = one_minus_alphas_bar_sqrt.to(device)

    coeff = betas[t].to(device) / one_minus_alphas_bar_sqrt[t].to(device)
    eps_theta = model(x, t)

    mean = (1 / (1 - betas[t]).sqrt()) * (x - (coeff * eps_theta))
    z = torch.randn_like(x).to(device)
    sigma_t = betas[t].sqrt()

    sample = mean + sigma_t * z
    return sample 
def p_sample_loop(model, shape, n_steps, betas, one_minus_alphas_bar_sqrt, device):
    betas = betas.to(device)
    one_minus_alphas_bar_sqrt = one_minus_alphas_bar_sqrt.to(device)
    cur_x = torch.randn(shape).to(device)  # Move initial x to device
    x_seq = [cur_x]
    for i in reversed(range(n_steps)):
        cur_x = p_sample(model, cur_x, i, betas, one_minus_alphas_bar_sqrt, device)
        x_seq.append(cur_x)
    return x_seq
def diffusion_loss_fn(model, x_0, alphas_bar_sqrt, one_minus_alphas_bar_sqrt, n_steps, device):
    x_0 = x_0.to(device)
    alphas_bar_sqrt = alphas_bar_sqrt.to(device)
    one_minus_alphas_bar_sqrt = one_minus_alphas_bar_sqrt.to(device)

    batch_size = x_0.shape[0]
    t = torch.randint(0, n_steps, size=(batch_size // 2,)).to(device)
    t = torch.cat([t, n_steps - 1 - t], dim=0)
    t = t.unsqueeze(-1)

    a = alphas_bar_sqrt[t].to(device)
    aml = one_minus_alphas_bar_sqrt[t].to(device)

    e = torch.randn_like(x_0).to(device)
    x = x_0 * a + e * aml

    output = model(x, t.squeeze(-1))
    return (e - output).square().mean()
def super_resolution_loss(model, x_0, alphas_bar_sqrt, one_minus_alphas_bar_sqrt, n_steps, lr_scale=0.5, device=None):
    x_0 = x_0.to(device)
    lr_x_0 = downsample_image(x_0, scale_factor=lr_scale, device=device)
    
    loss = diffusion_loss_fn(model, lr_x_0, alphas_bar_sqrt, one_minus_alphas_bar_sqrt, n_steps, device=device).mean()
    
    reconstructed_x_0 = model(lr_x_0, torch.tensor([n_steps - 1]).to(device))
    mse_loss = F.mse_loss(reconstructed_x_0, x_0).mean()

    return (loss + mse_loss).mean()
device = torch.device("cuda:1" if torch.cuda.is_available() else "cpu")
# model = MLPDiffusion(n_steps=100).to(device)
# optimizer = torch.optim.Adam(model.parameters(), lr=1e-3)
model = UNetDiffusion(n_steps=100).to(device)
optimizer = torch.optim.Adam(model.parameters(), lr=1e-3)
# Training Loop
num_epoch = 4000
for t in range(num_epoch):
    for idx, batch_x in enumerate(torch.utils.data.DataLoader(dataset, batch_size=2, shuffle=True)):
        batch_x = batch_x.to(device)
        loss = super_resolution_loss(model, batch_x, alphas_bar_sqrt, one_minus_alphas_bar_sqrt, num_steps, device=device)
        optimizer.zero_grad()
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        optimizer.step()
    if t % 100 == 0:
        print(f'Epoch {t}, Loss: {loss.item()}')

        # Sampling and visualization
        x_seq = p_sample_loop(model, dataset.shape, num_steps, betas, one_minus_alphas_bar_sqrt, device)
        
        fig, axs = plt.subplots(1, 10, figsize=(28, 3))
        for i in range(1, 11):            
            if x_seq[i * 10] is not None:
                cur_x = x_seq[i * 10].detach().cpu()
                axs[i - 1].scatter(cur_x[:, 0], cur_x[:, 1], color='red', edgecolor='white')
                axs[i - 1].set_axis_off()
                axs[i - 1].set_title(f'$q(\\mathbf{{x}}_{{{i * 10}}})$')
            else:
                print(f"Warning: x_seq[{i * 10}] is None.")
        plt.tight_layout()   
        outpath = f'./pngresult/{t}_Epoch_scatter_plot.png'
        crDir(outpath)
        plt.savefig(outpath, dpi=300)   
