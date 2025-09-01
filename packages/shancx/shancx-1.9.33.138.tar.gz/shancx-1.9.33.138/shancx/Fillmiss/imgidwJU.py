import numpy as np
from scipy.spatial import cKDTree
import matplotlib.pyplot as plt
def fill_missing_idw(image, power=2, max_neighbors=8):
    filled_image = image.copy()
    known_mask = ~np.isnan(image)
    missing_mask = np.isnan(image)
    known_points = np.column_stack(np.where(known_mask))
    missing_points = np.column_stack(np.where(missing_mask))
    known_values = image[known_mask]
    if len(missing_points) == 0:
        print("There are no missing points to fill.")
        return filled_image
    tree = cKDTree(known_points)
    distances, indexes = tree.query(missing_points, k=max_neighbors)
    with np.errstate(divide='ignore'): 
        weights = 1 / distances**power
    weights[~np.isfinite(weights)] = 0  
    weight_sums = np.sum(weights, axis=1)
    weight_sums[weight_sums == 0] = 1  
    interpolated_values = np.sum(weights * known_values[indexes], axis=1) / weight_sums
    for i, (x, y) in enumerate(missing_points):
        filled_image[x, y] = interpolated_values[i]
    return filled_image
def test_fill_missing_idw():
    np.random.seed(42)
    image = np.random.rand(20, 20)
    image[5:10, 5:10] = np.nan  
    plt.figure(figsize=(12, 6))
    plt.subplot(1, 2, 1)
    plt.imshow(image, cmap='viridis', interpolation='none')
    plt.title("before")
    plt.colorbar()
    plt.savefig("before.png")
    filled_image = fill_missing_idw(image, power=2, max_neighbors=8)
    plt.subplot(1, 2, 2)
    plt.imshow(filled_image, cmap='viridis', interpolation='none')
    plt.title("uper")
    plt.colorbar()

    plt.tight_layout()
    plt.savefig("uper.png")
    plt.show()

if __name__ == "__main__":
    test_fill_missing_idw()
