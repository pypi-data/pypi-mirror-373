 

def start_points(size, split_size, overlap=0.0): 
    stride = int(split_size * (1 - overlap))  # 计算步长
    points = [i * stride for i in range((size - split_size) // stride + 1)]   
    if size > points[-1] + split_size:   
        points.append(size - split_size)
    return points

"""
    b = np.zeros(sat_data[0].shape)
    x_point = start_points(sat_data[0].shape[0], 256, 0.14)
    y_point = start_points(sat_data[0].shape[1], 256, 0.14)
    overlap1 = 17
    for x in x_point:
        for y in y_point:
            cliped = sat_data[:, x:x + 256, y:y + 256]
            img1 = cliped[np.newaxis].float()
            img1 = img1.cpu().numpy()
            img1 = np.where(np.isnan(img1), 0, img1)
            img2 = img1.reshape(1, 6, 256, 256).astype(np.float32)  # Ensure correct shape and type
            radarpre = run_onnx_inference(ort_session, img2)
            radarpre = (radarpre * 72).squeeze()
            radarpre[radarpre < 13] = 0
            radarpre = QC_ref(radarpre[None], areaTH=30)[0]

            b[x + overlap1:x + 256, y + overlap1:y + 256] = radarpre[overlap1:, overlap1:]

    return b

"""
 