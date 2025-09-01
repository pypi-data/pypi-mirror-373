import torch
def p_sample_loop(model,shape,n_steps,betas,one_minus_alphas_bar_sqrt):
    cur_x = torch.randn(shape)
    x_seq = [cur_x]
    for i in reversed(range(n_steps)):
        cur_x = p_sample(model,cur_x,i,betas,one_minus_alphas_bar_sqrt)
        x_seq.append(cur_x)
    return x_seq

def p_sample(model,x,t,betas,one_minus_alphas_bar_sqrt):
    t = torch.tensor([t])    
    coeff = betas[t] / one_minus_alphas_bar_sqrt[t]    
    eps_theta = model(x,t)    
    mean = (1/(1-betas[t]).sqrt())*(x-(coeff*eps_theta))    
    z = torch.randn_like(x)
    sigma_t = betas[t].sqrt()    
    sample = mean + sigma_t * z    
    return (sample)