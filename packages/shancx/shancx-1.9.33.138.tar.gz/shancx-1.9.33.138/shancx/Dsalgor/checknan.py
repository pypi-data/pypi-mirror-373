import torch
import numpy as np

def checkData(data, name="data"):
    if isinstance(data, torch.Tensor):
        # 检查 Tensor 数据
        has_nan = torch.isnan(data).any().item()
        has_inf = torch.isinf(data).any().item()
        print(f"torch.isnan(data).any() {torch.isnan(data).any()} torch.isinf(data).any() {torch.isinf(data).any()} ")
    elif isinstance(data, np.ndarray):
        # 检查 NumPy 数据
        has_nan = np.isnan(data).any()
        has_inf = np.isinf(data).any()
        print(f"np.isnan(data).any() {np.isnan(data).any()} np.isinf(data).any() {np.isinf(data).any()} ")
    else:
        raise TypeError(f"Unsupported data type: {type(data)}. Expected torch.Tensor or numpy.ndarray.")

    # 如果有 NaN 或 Inf，打印日志并返回 False
    if has_nan or has_inf:
        print(f"{name} contains NaN or Inf values!" 
              f"has_nan: {has_nan}, has_inf: {has_inf}")
        return False
    return True
    """  训练循环跳过
            if not check_data(data, "data") or not check_data(label, "label"):
            logger.info("# 跳过异常数据")
            continue  # 跳过异常数据
    """