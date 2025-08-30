
def iou(inputs,targets,thresholds=[0, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 80]):
    ts_sum = 0
    for i in range(len(thresholds)):
        inputs_copy = inputs.flatten().copy()   # nputs_copy = inputs.flatten().clone()
        targets_copy = targets.flatten().copy()
        inputs_copy[inputs.flatten() < thresholds[i]] = 0
        inputs_copy[inputs.flatten() >= thresholds[i]] = 1
        targets_copy[targets.flatten() < thresholds[i]] = 0
        targets_copy[targets.flatten() >= thresholds[i]] = 1
        intersection = (inputs_copy.flatten() * targets_copy).sum()
        total = (inputs_copy.flatten() + targets_copy).sum()
        union = total - intersection
        iou = (intersection + 1e-16)/ (union + 1e-16)
        ts_sum += iou
    return ts_sum/len(thresholds)
import torch

def iouPlus(inputs, targets, thresholds=[0, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 80]):
    inputs_flat = inputs.flatten()  # 提前展平
    targets_flat = targets.flatten()
    ts_sum = 0

    for threshold in thresholds:
        # 根据阈值二值化
        inputs_bin = (inputs_flat >= threshold).float()
        targets_bin = (targets_flat >= threshold).float()

        # 计算交集和并集
        intersection = (inputs_bin * targets_bin).sum()
        union = inputs_bin.sum() + targets_bin.sum() - intersection

        # 计算 IoU
        iou = (intersection + 1e-16) / (union + 1e-16)
        ts_sum += iou

    # 返回平均 IoU
    return ts_sum / len(thresholds)
def IouOrder(inputs,targets,thresholds=[15]):
    lower_threshold = thresholds[0]
    upper_threshold = thresholds[1]
    inputs_copy = (inputs.flatten() >= lower_threshold) & (inputs.flatten() <= upper_threshold)
    targets_copy = (targets.flatten() >= lower_threshold) & (targets.flatten() <= upper_threshold)
    inputs_copy = inputs_copy.astype(int)
    targets_copy = targets_copy.astype(int)
    intersection = (inputs_copy.flatten() * targets_copy).sum()
    total = (inputs_copy.flatten() + targets_copy).sum()
    union = total - intersection
    iou = (intersection + 1e-16)/ (union + 1e-16)
    return iou

def iouMask(inputs, targets, mask, thresholds=[0, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 80],type=None):
    # 检查输入类型
    is_tensor = type
    # 确保 inputs, targets, mask_data 在同一设备上
    targets = targets 
    mask_data = mask     
    # 生成 mask：mask_data == 0 的区域为 True    
    # 展平 inputs, targets, mask
    inputs_flat = inputs.flatten()
    targets_flat = targets.flatten()
    mask_flat = mask.flatten()    
    # 只计算 mask 区域的 IoU
    if is_tensor:
        inputs_flat = inputs_flat[mask_flat]  # 只保留 mask 为 True 的区域
        targets_flat = targets_flat[mask_flat]
    else:
        inputs_flat = inputs_flat[mask_flat == 1]  # 只保留 mask 为 1 的区域
        targets_flat = targets_flat[mask_flat == 1]    
    ts_sum = 0.0    
    for threshold in thresholds:
        if is_tensor:
            inputs_bin = (inputs_flat >= threshold).float()
            targets_bin = (targets_flat >= threshold).float()
        else:
            inputs_bin = (inputs_flat >= threshold).astype(float)
            targets_bin = (targets_flat >= threshold).astype(float)
        intersection = (inputs_bin * targets_bin).sum()
        union = inputs_bin.sum() + targets_bin.sum() - intersection
        iou = (intersection + 1e-16) / (union + 1e-16)
        ts_sum += iou
    return ts_sum / len(thresholds)
 