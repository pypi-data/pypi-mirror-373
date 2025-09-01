import cv2
import numpy as np
def removeSmallPatches(binary_mask, min_pixels=50, min_area=40):
    binary_mask = (binary_mask > 0).astype(np.uint8)
    num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(
        binary_mask, connectivity=8
    )    
    output_mask = np.zeros_like(binary_mask)    
    for i in range(1, num_labels):
        pixel_count = stats[i, cv2.CC_STAT_AREA]        
        if pixel_count < min_pixels:
            continue
        component_mask = (labels == i).astype(np.uint8)
        contours, _ = cv2.findContours(component_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)        
        if contours:
            contour = contours[0]
            area = cv2.contourArea(contour)            
            if area < min_area:
                continue        
        output_mask[labels == i] = 255    
    return output_mask

"""
mask = removeSmallPatches(b, min_pixels=50, min_area=40)
data = np.where(mask, data, 0)
filtered_data = np.full([256,256],0)
filtered_data[mask] = e[mask]
"""

import cv2
import numpy as np
from concurrent.futures import ThreadPoolExecutor
def process_block_optimized(args):
    block, coords, min_pixels, min_area = args
    y, x, y_end, x_end = coords    
    num_labels, labels, stats, _ = cv2.connectedComponentsWithStats(block, 8)
    result = np.zeros_like(block)    
    valid_labels = []
    for i in range(1, num_labels):
        if stats[i, cv2.CC_STAT_AREA] >= min_pixels:
            valid_labels.append(i)   
    for i in valid_labels:
        component_mask = (labels == i).astype(np.uint8)
        contours, _ = cv2.findContours(component_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)        
        if contours and cv2.contourArea(contours[0]) >= min_area:
            result[labels == i] = 255    
    return result, coords
def removeSmallPatches_fast(binary_mask, min_pixels=100, min_area=40, num_workers=3):
    binary_mask = (binary_mask > 0).astype(np.uint8)
    h, w = binary_mask.shape
    output = np.zeros_like(binary_mask)
    block_size = 2000    
    blocks = []
    for y in range(0, h, block_size):
        for x in range(0, w, block_size):
            y_end, x_end = min(y+block_size, h), min(x+block_size, w)
            block = binary_mask[y:y_end, x:x_end]
            blocks.append((block, (y, x, y_end, x_end), min_pixels, min_area))    
    with ThreadPoolExecutor(num_workers) as executor:
        for result, (y, x, y_end, x_end) in executor.map(process_block_optimized, blocks):
            output[y:y_end, x:x_end] = result    
    return output

"""
mask = removeSmallPatches(b, min_pixels=50, min_area=40)
data = np.where(mask, data, 0)
filtered_data = np.full([256,256],0)
filtered_data[mask] = e[mask]
"""