import torch
def apply_mask_and_select(labels, outputs):
    """
    应用掩码过滤，并选择有效的标签和输出值。    
    :param labels: 标签张量
    :param outputs: 模型输出张量
    :return: 过滤后的标签和输出
    """
    mask = labels > 0  
    filtered_labels = torch.masked_select(labels, mask)
    filtered_outputs = torch.masked_select(outputs, mask)    
    return filtered_labels, filtered_outputs
if __name__ == "__main__":
    labels = torch.tensor([1, 0, 2, -1, 3], dtype=torch.float)
    outputs = torch.tensor([1.1, 0.5, 2.1, -0.1, 2.9], dtype=torch.float)
    filtered_labels, filtered_outputs = apply_mask_and_select(labels, outputs)
    print("Filtered Labels:", filtered_labels)
    print("Filtered Outputs:", filtered_outputs)
def apply_mask(img, label ):  #有效值参与计算
    non_zero_maskimg = img > 0
    img = img * non_zero_maskimg
    non_zero_masklabel = label > 0
    label = label * non_zero_masklabel
    return img,non_zero_maskimg, label,non_zero_masklabel
     
