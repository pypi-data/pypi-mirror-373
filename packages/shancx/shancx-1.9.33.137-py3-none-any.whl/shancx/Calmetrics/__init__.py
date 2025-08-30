#!/usr/bin/python
# -*- coding: utf-8 -*-
import os 
# constants
__author__ = 'shancx'
 
__author_email__ = 'shanhe12@163.com'
# @Time : 2025/08/19 下午11:31
# @Author : shanchangxi
# @File : Calmetrics.py 
from sklearn.metrics import mean_squared_error, r2_score
from scipy.stats import pearsonr
import numpy as np
def calculate_metrics(y_true, y_pred):
    # Calculate metrics
    correlation, _ = pearsonr(y_true, y_pred)
    rmse = np.sqrt(mean_squared_error(y_true, y_pred))
    mask = y_true != 0
    y_true = y_true[mask]
    y_pred = y_pred[mask]
    mape = np.mean(np.abs((y_true - y_pred) / y_true)) * 100
    r2 = r2_score(y_true, y_pred)
    rmse = f"{rmse:0.4f}"
    correlation = f"{correlation:0.4f}"
    mape = f"{mape:0.4f}"
    r2 = f"{r2:0.4f}"
    return rmse,correlation,mape,r2
    