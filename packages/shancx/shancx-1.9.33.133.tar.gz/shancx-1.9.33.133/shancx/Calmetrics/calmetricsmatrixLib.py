# coding=utf-8

from sklearn.metrics import confusion_matrix
import numpy as np
import copy
def prep_clf(obs, pre, thresholdR=None, thresholdF=None):
    if thresholdR is not None and thresholdF is not None:
        obs = np.where(obs >= thresholdR, 1, 0)
        pre = np.where(pre >= thresholdF, 1, 0)
    # True positive (TP)
    hits = np.sum((obs == 1) & (pre == 1))
    # False negative (FN)
    misses = np.sum((obs == 1) & (pre == 0))
    # False positive (FP)
    falsealarms = np.sum((obs == 0) & (pre == 1))
    # True negative (TN)
    correctnegatives = np.sum((obs == 0) & (pre == 0))
    return hits, misses, falsealarms, correctnegatives
def precision(obs, pre, thresholdR=None, thresholdF=None):
    TP, FN, FP, TN = prep_clf(obs=obs, pre = pre, thresholdR=thresholdR, thresholdF=thresholdF)
    return TP / (TP + FP+10e-5)
def recall(obs, pre, thresholdR=None, thresholdF=None):
    TP, FN, FP, TN = prep_clf(obs=obs, pre = pre, thresholdR=thresholdR, thresholdF=thresholdF)
    return TP / (TP + FN+10e-5)
def ACC(obs, pre, thresholdR=None, thresholdF=None):
    TP, FN, FP, TN = prep_clf(obs=obs, pre = pre, thresholdR=thresholdR, thresholdF=thresholdF)
    return (TP + TN) / (TP + TN + FP + FN)
def F1(obs, pre, thresholdR=None, thresholdF=None):   
    precision_socre = precision(obs, pre, thresholdR=thresholdR, thresholdF=thresholdF)
    recall_score = recall(obs, pre, thresholdR=thresholdR, thresholdF=thresholdF)
    return 2 * ((precision_socre * recall_score) / (precision_socre + recall_score+10e-5))
def TS(obs, pre, thresholdR=None, thresholdF=None):
    hits, misses, falsealarms, correctnegatives = prep_clf(obs=obs, pre = pre, thresholdR=thresholdR, thresholdF=thresholdF)
    return hits/(hits + falsealarms + misses+10e-5)
def ETS(obs, pre, thresholdR=None, thresholdF=None): 
    hits, misses, falsealarms, correctnegatives = prep_clf(obs=obs, pre = pre,
                                                           thresholdR=thresholdR, thresholdF=thresholdF)
    num = (hits + falsealarms) * (hits + misses)
    den = hits + misses + falsealarms + correctnegatives
    Dr = num / den
    ETS = (hits - Dr) / (hits + misses + falsealarms - Dr)
    return ETS
def FAR(obs, pre, thresholdR=None, thresholdF=None):   
    hits, misses, falsealarms, correctnegatives = prep_clf(obs=obs, pre = pre,
                                                           thresholdR=thresholdR, thresholdF=thresholdF)
    return falsealarms / (hits + falsealarms+10e-5)
def PO(obs, pre, thresholdR=None, thresholdF=None):  
    hits, misses, falsealarms, correctnegatives = prep_clf(obs=obs, pre = pre,
                                                           thresholdR=thresholdR, thresholdF=thresholdF)
    return misses / (hits + misses+10e-5)
def POD(obs, pre, thresholdR=None, thresholdF=None):
    hits, misses, falsealarms, correctnegatives = prep_clf(obs=obs, pre = pre,
                                                           thresholdR=thresholdR, thresholdF=thresholdF)
    return hits / (hits + misses)
def BIAS(obs, pre, thresholdR = 0.1, thresholdF=None):
    hits, misses, falsealarms, correctnegatives = prep_clf(obs=obs, pre = pre,
                                                           thresholdR=thresholdR, thresholdF=thresholdF)
    return (hits + falsealarms) / (hits + misses)
def HSS(obs, pre, thresholdR=None, thresholdF=None):   
    hits, misses, falsealarms, correctnegatives = prep_clf(obs=obs, pre = pre,
                                                           thresholdR=thresholdR, thresholdF=thresholdF)
    HSS_num = 2 * (hits * correctnegatives - misses * falsealarms)
    HSS_den = (misses**2 + falsealarms**2 + 2*hits*correctnegatives +
               (misses + falsealarms)*(hits + correctnegatives))
    return HSS_num / HSS_den
def BSS(obs, pre, threshold=None): 
    if threshold is not None:  
        obs = np.where(obs >= threshold, 1, 0)
        pre = np.where(pre >= threshold, 1, 0)
    obs = obs.flatten()
    pre = pre.flatten()
    return np.sqrt(np.mean((obs - pre) ** 2))
def MAE(obs, pre):
    obs = obs.flatten()
    pre = pre.flatten()
    return np.mean(np.abs(pre - obs))
def RMSE(obs, pre):
    obs = obs.flatten()
    pre = pre.flatten()
    return np.sqrt(np.mean((obs - pre) ** 2))
def sun_rain_Matrix(o, f, threshold=None):
    if threshold is not None:  
        o = np.where(o >= 0.1, 1, 0)
        f = np.where(f >= threshold, 1, 0)
    c_matrix = confusion_matrix(o, f, labels=[0, 1])
    return c_matrix
def CY_classify(pre0):
    # < 0.031 < 0.0606    无雨／雪
    # 0.031~0.25 0.0606~0.8989   小雨／雪
    # 0.25~0.35  0.8989~2.8700   中雨／雪
    # 0.35~0.48  2.8700~12.8638  大雨／雪
    # >= 0.48 >= 12.8638  暴雨／雪
    pre = copy.deepcopy(pre0)
    pre[pre0 < 0.031] = 0
    pre[(pre0 >= 0.031)&(pre0 < 0.25)] = 1
    pre[(pre0 >= 0.25)&(pre0 < 0.35)] = 2
    pre[(pre0 >= 0.35)&(pre0 < 0.48)] = 3
    pre[(pre0 >= 0.48)&(pre0 < 9990)] = 4
    pre[pre0 > 9990] = -1
    pre[np.isnan(pre0)] = -1
    return pre
def pre1h_Matrix(obs, fore,mode):
    try:
        if len(obs) == 0:
            return np.zeros([5,5])
        else:
            o = classify1h(obs)
            if mode=="WTX":
                f = classify1h(fore)
                c_matrix = confusion_matrix(o, f, labels=[0, 1,2,3,4])
                return c_matrix
            else:
                f = CY_classify(fore)
                c_matrix = confusion_matrix(o, f, labels=[0, 1, 2, 3, 4])
                return c_matrix
    except Exception as e:
        print(e)    
def classify1h(pre0):
    pre = copy.deepcopy(pre0)
    pre[pre0 < 0.1] = 0
    pre[np.logical_and(pre0 >= 0.1, pre0 <= 2.5)] = 1
    pre[np.logical_and(pre0 > 2.5, pre0 <= 8)] = 2
    pre[np.logical_and(pre0 > 8, pre0 <= 16)] = 3
    pre[np.logical_and(pre0 > 16, pre0 <= 9990)] = 4
    pre[pre0 > 9990] = -1
    pre[np.isnan(pre0)] = -1
    return pre

def calsmhsTS(mat):
    tsList = []
    for i in range(1, 5):
        ts = mat[i, i] / (np.sum(mat[:i, i]) + np.sum(mat[i, :i + 1]))
        tsList.append(np.round(ts, 3))
    print(f"小雨:{tsList[0]},中雨:{tsList[1]},大雨:{tsList[2]},暴雨:{tsList[3]}")
    return {"小雨":tsList[0],"中雨":tsList[1],"大雨":tsList[2],"暴雨":tsList[3]}

"""
cm1_C = sun_rain_Matrix(df["PRE1_r"].values, df["PRE1_c"].values)
F1h =TS( df[f"PRE{i}_r"],df[f"PRE{i}_c"],thresholdF=thresholdF)
F1hm =TS(df[f"PRE{i}_r"],df[f"PRE{i}_w"])
TSV[i]=[np.round(F1h,3),np.round(F1hm,3)]
"""

"""
cm1_C_pre1h = pre1h_Matrix(df["PRE1_r"].values, df["PRE1_c"].values,"CY")  
calsmhsTS(cm1_C_pre1h)
"""