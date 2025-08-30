import numpy as np
from shancx.Calmetrics.metrics import Metrics
def cal_metrics(obs_v,pre_v):
    metrics = Metrics(obs_v.ravel(), pre_v.ravel())
    ts_score = np.around(metrics.cal_ts(),4)
    accuracy = np.around(metrics.cal_acc(),4)
    pod = np.around(metrics.cal_pod(),4)
    fnr = np.around(metrics.cal_fnr(),4)
    far = np.around(metrics.cal_far(),4)
    return ts_score,accuracy,pod,fnr,far

"""
ts_score, accuracy, pod, fnr, far = cal_metrics(obs_v,pre_v)  两个是维度一致的二维数组
"""