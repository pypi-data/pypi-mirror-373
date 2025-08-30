
from torch.utils.data import Dataset, DataLoader
import torch
class CUDAPrefetcher1:
    """
    Use the CUDA side to accelerate data reading.

    Args:
        dataloader (DataLoader): Data loader. Combines a dataset and a sampler, and provides an iterable over the given dataset.
        device (torch.device): Specify running device.
    """

    def __init__(self, dataloader: DataLoader, device: torch.device):
        self.batch_data = None
        self.original_dataloader = dataloader
        self.device = device

        self.data = iter(dataloader)
        self.stream = torch.cuda.Stream()
        self.preload()

    def preload(self):
        """
        Load the next batch of data and move it to the specified device asynchronously.
        """
        try:
            self.batch_data = next(self.data)
        except StopIteration:
            self.batch_data = None
            return

        # Asynchronously move the data to the GPU
        with torch.cuda.stream(self.stream):
            if isinstance(self.batch_data, dict):
                self.batch_data = {
                    k: v.to(self.device, non_blocking=True)
                    if torch.is_tensor(v) else v
                    for k, v in self.batch_data.items()
                }
            elif isinstance(self.batch_data, (list, tuple)):
                self.batch_data = [
                    x.to(self.device, non_blocking=True)
                    if torch.is_tensor(x) else x
                    for x in self.batch_data
                ]
            elif torch.is_tensor(self.batch_data):
                self.batch_data = self.batch_data.to(self.device, non_blocking=True)
            else:
                raise TypeError(
                    f"Unsupported data type {type(self.batch_data)}. Ensure the dataloader outputs tensors, dicts, or lists."
                )

    def __iter__(self):
        """
        Make the object iterable by resetting the dataloader and returning self.
        """
        self.reset()
        return self

    def __next__(self):
        """
        Wait for the current stream, return the current batch, and preload the next batch.
        """
        if self.batch_data is None:
            raise StopIteration

        torch.cuda.current_stream().wait_stream(self.stream)
        batch_data = self.batch_data
        self.preload()
        return batch_data

    def reset(self):
        """
        Reset the dataloader iterator and preload the first batch.
        """
        self.data = iter(self.original_dataloader)
        self.preload()

    def __len__(self):
        """
        Return the length of the dataloader.
        """
        return len(self.original_dataloader)

#  train_data_prefetcher = CUDAPrefetcher1(degenerated_train_dataloader, device)

import torch
from torch.utils.data import DataLoader
import torch.nn.functional as F
def custom_collate_fn(batch):
    """
    Custom collate function to handle batches with varying tensor sizes by padding them to the same size.
    """
    if isinstance(batch[0], dict):
        collated = {key: custom_collate_fn([d[key] for d in batch]) for key in batch[0]}
        return collated
    elif isinstance(batch[0], torch.Tensor):
        # Find max dimensions
        max_height = max(item.shape[1] for item in batch)
        max_width = max(item.shape[2] for item in batch)

        # Pad each tensor to the same size
        padded_batch = []
        for item in batch:
            padding = (0, max_width - item.shape[2], 0, max_height - item.shape[1])
            padded_item = F.pad(item, padding, mode="constant", value=0)
            padded_batch.append(padded_item)
        return torch.stack(padded_batch)
    else:
        return batch
# device = torch.device("cuda:0")
# paired_test_dataloader = DataLoader(datasetdata,device)