import torch
def L2loss(model,loss,lambda_reg =0.01):    
    l2_reg = 0.0
    for param in model.parameters():
        l2_reg += torch.norm(param)**2  # 模型参数的平方和
        print(l2_reg)
    loss += lambda_reg * l2_reg
    return loss


