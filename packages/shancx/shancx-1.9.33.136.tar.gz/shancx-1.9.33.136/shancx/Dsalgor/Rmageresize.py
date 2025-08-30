import torch
from torchvision.transforms import Resize
from torchvision.transforms.functional import InterpolationMode
import numpy as np

def image_resize(image, scale_factor, antialiasing=True):
    """
    Resize the input image with a specified scale factor using torchvision's Resize.

    Args:
        image (np.ndarray or torch.Tensor): Input image of shape (H, W, C) or (C, H, W).
        scale_factor (float): Scale factor to resize the image.
        antialiasing (bool): Whether to use antialiasing (default: True).

    Returns:
        Resized image in the same format as input (NumPy or PyTorch Tensor).
    """
    # Check if input is NumPy array
    numpy_type = isinstance(image, np.ndarray)

    # Handle missing values for NumPy arrays
    if numpy_type:
        image = np.nan_to_num(image)  # Replace NaNs with 0
        if image.ndim == 3:  # (H, W, C)
            image = torch.from_numpy(image.transpose(2, 0, 1)).float()  # Convert to (C, H, W)
        elif image.ndim == 2:  # (H, W)
            image = torch.from_numpy(image[None, :, :]).float()  # Convert to (C, H, W)

    # Calculate new dimensions
    _, in_h, in_w = image.shape  # Assuming (C, H, W) format
    out_h, out_w = int(in_h * scale_factor), int(in_w * scale_factor)

    # Perform resizing
    mode = InterpolationMode.BICUBIC if antialiasing else InterpolationMode.NEAREST
    resize_transform = Resize((out_h, out_w), interpolation=mode)
    resized_image = resize_transform(image)

    # Convert back to NumPy array if input was NumPy
    if numpy_type:
        resized_image = resized_image.numpy().transpose(1, 2, 0)  # Convert back to (H, W, C)

    return resized_image
# resized_image = image_resize(image, scale_factor, antialiasing)

# Example for loading image data and processing NaNs
def process_image(file_path, scale_factor, antialiasing=True):
    """
    Load an image from a file, handle NaN values, and resize it.

    Args:
        file_path (str): Path to the image file (e.g., .npy for NumPy arrays).
        scale_factor (float): Scale factor for resizing.
        antialiasing (bool): Use antialiasing during resizing (default: True).

    Returns:
        Resized image as a NumPy array.
    """
    # Load the image from a .npy file
    image = np.load(file_path)
    image[np.isnan(image)] = 0  # Replace NaN values with 0

    # Resize the image
    resized_image = image_resize(image, scale_factor, antialiasing)
    return resized_image
if __name__=="__main__":
    import matplotlib.pyplot as plt

    # Path to a NumPy array image file
    file_path = 'example.npy'  # Replace with your .npy file path

    # Resize the image
    scale_factor = 0.5  # Downscale by 50%
    resized_image = process_image(file_path, scale_factor)

    # Display the resized image
    plt.title("Resized Image")
    plt.imshow(resized_image.astype(np.uint8))
    plt.axis("off")
    plt.show()