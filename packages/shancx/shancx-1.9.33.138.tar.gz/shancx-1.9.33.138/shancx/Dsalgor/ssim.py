import torch
import torch.nn as nn
import torch.nn.functional as F
from shancx.Dsalgor.structural_similarity import MSSSIMLoss
import torch.nn as nn
class LossFunctions():

    def __init__(self,
                device='cpu'
                ):

        self.device = device

        # self.alpha = 0.15
        self.alpha = 0.3
        self.w_fact = 0.01    
        self.w_exponent = 0.05 
        self.data_range = 1                             #0.15
        # self.scale_pos = hparam.scale_pos
        # self.scale_neg = hparam.scale_neg
        self.w_fact = torch.Tensor([self.w_fact]).to(device)          #0.001
        self.w_exponent = torch.Tensor([self.w_exponent]).to(device)  #0.038
        # self.w_exponent = nn.Parameter(torch.Tensor([self.w_exponent]).to(device))
        self.data_range = self.data_range                             #1
        self.zero = torch.Tensor([0]).to(self.device)
        self.one = torch.Tensor([1]).to(self.device)
    def mse(self, output, target):
        """ Mean Squared Error Loss """

        criterion = torch.nn.MSELoss()
        loss = criterion(output, target)
        return loss
    def msssim(self, output, target):
        """ Multi-Scale Structural Similarity Index Loss """
        criterion = MSSSIMLoss(data_range=self.data_range)
        loss = criterion(output, target)
        return loss
    def msssim_weighted_mse(self, output, target):
        """ MS-SSIM with Weighted Mean Squared Error Loss """
        weights = torch.minimum(self.one, self.w_fact*torch.exp(self.w_exponent*target))
        criterion = MSSSIMLoss(data_range=self.data_range)
        loss = self.alpha*(weights * (output - target) ** 2).mean() \
             + (1.-self.alpha)*criterion(output, target)
        return loss


    def mse_mae(self, output, target):
        """ Combined Mean Squared Error and Mean Absolute Error Loss """
        loss = (1.-self.alpha)*((output - target) ** 2).mean() \
               + self.alpha*(abs(output - target)).mean()
        return loss

    def weighted_mse(self, output, target):
        """ Weighted Mean Squared Error Loss """
        weights = torch.minimum(self.one, self.w_fact*torch.exp(self.w_exponent*target))
        loss = (weights * (output - target) ** 2).mean()
        return loss
    def mae_weighted_mse(self, output, target):
        """ Weighted Mean Squared Error and Mean Absolute Error Loss """
        weights = torch.minimum(self.one, self.w_fact*torch.exp(self.w_exponent*target))
        loss = self.alpha*(weights * (output - target) ** 2).mean() \
             + (1.-self.alpha)*(torch.abs(output - target)).mean()
        return loss
"""
if __name__ == '__main__':
    losses = LossFunctions(device=device)
    cost = getattr(losses, "msssim_weighted_mse")   #"msssim_weighted_mse"
    loss = cost(yhat, y) 

"""
