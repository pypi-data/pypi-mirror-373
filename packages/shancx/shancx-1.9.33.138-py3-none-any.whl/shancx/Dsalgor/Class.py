import torch
import copy
def classify1h(pre0):
    pre = copy.deepcopy(pre0)
    pre[torch.logical_and(pre0 >= 0.1, pre0 <= 2.5)] = 1
    pre[torch.logical_and(pre0 > 2.5, pre0 <= 8)] = 2
    pre[torch.logical_and(pre0 > 8, pre0 <= 16)] = 3
    pre[torch.logical_and(pre0 > 16, pre0 <= 300)] = 4
    pre[pre0 > 300] = -1
    pre[torch.isnan(pre0)] = -1
    return pre