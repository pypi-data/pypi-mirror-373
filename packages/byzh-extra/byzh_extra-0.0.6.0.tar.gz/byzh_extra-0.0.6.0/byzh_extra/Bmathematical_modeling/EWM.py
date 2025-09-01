# 熵权法: EWM: Entropy Weight Method
import numpy as np
from .math_utils import l2_normalize

def mylog(p: np.ndarray): # 使0的log为0
    # 如果某个值为0, 则加上1
    result = np.log(p + (p == 0))
    return result

def b_entropy_weight(X: np.ndarray):
    """
    熵权法: EWM: Entropy Weight Method
    -> 得到指标的权重

    n个候选项
    m个指标
    :param X:
    :return:
    """
    n, m = X.shape

    # l2归一化
    X = l2_normalize(X, "v")

    # 计算每个指标的信息效用值d
    D = np.zeros(m)
    for i in range(m):
        x = X[:, i]
        # 第i个指标下, 每个样本的比重
        p = x / np.sum(x)
        # 熵值
        e = -np.sum(p * mylog(p)) / np.log(n)
        # 信息效用值
        D[i] = 1 - e

    # 熵权
    weights = D / np.sum(D)

    return weights

b_EWM = b_entropy_weight

if __name__ == '__main__':
    X = np.array([
        [9, 0, 0, 0],
        [8, 3, 0.9, 0.5],
        [6, 7, 0.2, 1]
    ])

    weights = b_entropy_weight(X)

    print(weights)