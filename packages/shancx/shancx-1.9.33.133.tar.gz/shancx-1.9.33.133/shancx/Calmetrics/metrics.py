import numpy as np
class Metrics:
    def __init__(self, true_values, forecast_values):
        """
        初始化Metrics类，传入真值和预测值
        :param true_values: 实际观测值，二值化数据
        :param forecast_values: 预测结果，二值化数据
        """
        self.true_values = true_values
        self.forecast_values = forecast_values

    def cal_confusion_matrix(self):
        """
        计算混淆矩阵的四个要素: TP, TN, FP, FN
        :return: 返回TP, TN, FP, FN
        """
        TP = np.sum((self.true_values == 1) & (self.forecast_values == 1))  # True Positive
        TN = np.sum((self.true_values == 0) & (self.forecast_values == 0))  # True Negative
        FP = np.sum((self.true_values == 0) & (self.forecast_values == 1))  # False Positive
        FN = np.sum((self.true_values == 1) & (self.forecast_values == 0))  # False Negative
        
        return TP, TN, FP, FN

    def cal_ts(self):
        """
        计算TS评分
        :return: TS评分
        """
        TP, TN, FP, FN = self.cal_confusion_matrix()
        ts_score = TP / (TP + FP + FN) if (TP + FP + FN) > 0 else np.nan
        return ts_score

    def cal_acc(self):
        """
        计算准确率
        :return: 准确率
        """
        TP, TN, FP, FN = self.cal_confusion_matrix()
        accuracy = (TP + TN) / (TP + TN + FP + FN) if (TP + TN + FP + FN) > 0 else np.nan
        return accuracy

    def cal_pod(self):  
        """  
        计算命中率(Probability of Detection, POD)
        :return: 命中率(POD)
        """  
        TP, TN, FP, FN = self.cal_confusion_matrix()  
        pod = TP / (TP + FN) if (TP + FN) > 0 else np.nan  
        return pod


    def cal_fnr(self):
            """
            计算漏报率（False Negative Rate, FNR）
            :return: 漏报率（FNR）
            """
            TP, TN, FP, FN = self.cal_confusion_matrix()
            fnr = FN / (TP + FN) if (TP + FN) > 0 else np.nan
            return fnr

    def cal_far(self):
        """
        计算空报率（False Alarm Rate, FAR）
        :return: 空报率（FAR）
        """
        TP, TN, FP, FN = self.cal_confusion_matrix()
        far = FP / (TP + FP) if (TP + FP) > 0 else np.nan
        return far

        