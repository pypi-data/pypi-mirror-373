# -*- coding = utf-8 -*-
# @time: 2022/2/23 3:17 下午
# @Author: erazhan
# @File: sklearn_utils.py

# ----------------------------------------------------------------------------------------------------------------------
import math
from sklearn.metrics import confusion_matrix
from sklearn.metrics import accuracy_score
from sklearn.metrics import precision_score
from sklearn.metrics import recall_score
from sklearn.metrics import roc_auc_score
from sklearn.metrics import roc_curve
from sklearn.metrics import f1_score
from sklearn.metrics import auc

# ----------------------------------------------------------------------------------------------------------------------

def show_ml_metric(test_labels, predict_labels, predict_prob):
    accuracy = accuracy_score(test_labels, predict_labels)
    precision = precision_score(test_labels, predict_labels)
    recall = recall_score(test_labels, predict_labels)
    f1_measure = f1_score(test_labels, predict_labels)
    confusionMatrix = confusion_matrix(test_labels, predict_labels)
    fpr, tpr, threshold = roc_curve(test_labels, predict_prob, pos_label=1)
    Auc = auc(fpr, tpr)
    print("------------------------- ")
    print("confusion matrix:")
    print("------------------------- ")
    print("| TP: %5d | FP: %5d |" % (confusionMatrix[1, 1], confusionMatrix[0, 1]))
    print("----------------------- ")
    print("| FN: %5d | TN: %5d |" % (confusionMatrix[1, 0], confusionMatrix[0, 0]))
    print(" ------------------------- ")
    print("Accuracy:       %.2f%%" % (accuracy * 100))
    print("Recall:         %.2f%%" % (recall * 100))
    print("Precision:      %.2f%%" % (precision * 100))
    print("F1-measure:     %.2f%%" % (f1_measure * 100))
    print("AUC:            %.2f%%" % (Auc * 100))
    print("------------------------- ")
    return (Auc)


def MRR(rank_list):
    # 会受影响，数量越多，平均越小， 比如MRR(123)>MRR(1234)
    score = 0.0
    for rank in rank_list:
        score += 1 / rank
    return score / len(rank_list)


def DCG(rank_list, value_list=None, mode="ndcg"):
    """
    :param rank_list: 排名列表
    :param value_list: 评分列表
    :param mode: 分值计算模式，ndcg或mrr，mrr时与函数MRR功能相同
    :return:
    """
    score = 0.0

    if value_list is None:
        value_list = [1.0] * len(rank_list)
    else:
        assert len(rank_list) == len(value_list), "排名和评分列表元素个数必须相当"

    for rank,value in zip(rank_list,value_list):
        if mode == "ndcg":
            if rank == 1:
                score += value
            else:
                score += value / math.log(rank, 2)
        elif mode == "ndcg_plus":
            score += value/math.log(rank + 1, 2)
        elif mode == "mrr":
            score += value/rank
        else:
            raise ValueError("mode %s error"%mode)

    return score


def NDCG(rank_list,mode="ndcg"):
    """
    :param rank_list:
    :param mode:
    :return:
    计算公式参考：https://zhuanlan.zhihu.com/p/615915425
    """
    dcg_score = DCG(rank_list,mode = mode)
    best_rank_list = [i + 1 for i in range(len(rank_list))]
    idcg_score = DCG(best_rank_list,mode=mode)

    ndcg_score = dcg_score / idcg_score

    return ndcg_score

if __name__ == "__main__":

    rank_list = [1,3,4,9,13] # 真实标签的推荐位置
    res = MRR(rank_list)
    print(res)

    res = DCG(rank_list,mode='mrr')
    print(res)

    res = NDCG(rank_list)
    print(res)
