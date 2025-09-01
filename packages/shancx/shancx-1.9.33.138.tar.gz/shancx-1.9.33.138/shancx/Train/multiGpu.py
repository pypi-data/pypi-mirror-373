
import torch
import torch.nn as nn

def multiGpu(model, gpu_ids):
    # 检查是否有可用的 GPU
    if not torch.cuda.is_available():
        print("CUDA is not available. Using CPU.")
        device = torch.device("cpu")
        return model.to(device), device
    device = torch.device(f"cuda:{gpu_ids[0]}")
    if len(gpu_ids) > 1:
        print(f"Using {len(gpu_ids)} GPUs: {gpu_ids}")
        model = nn.DataParallel(model, device_ids=gpu_ids)
    else:
        print(f"Using GPU: {gpu_ids[0]}")
    model = model.to(device)
    return model, device

    """
    model = MyModel()
    gpu_ids = [5, 6, 7]
    model, device = setup_multi_gpu(model, gpu_ids)
    print(f"Model is on device: {device}")
    data = torch.randn(10, 3, 224, 224).to(device)
    output = model(data)
    """