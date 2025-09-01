import torch
@staticmethod
def calculate_psnr(img1, img2):
    return 10. * torch.log10(1. / torch.mean((img1 - img2) ** 2))   
    """  使用方法
    psnr += self.calculate_psnr(fake_img, label).item()
    total += 1
     mean_psnr = psnr / total
    """ 