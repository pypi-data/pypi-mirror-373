# 层次分析法: AHP: Analytic Hierarchy Process

import numpy as np
from typing import Literal


def check_consistency(
        A: np.ndarray
):
    """
    一致性检验

    n个指标
    :param A: 形状(n, n)
    :return:
    """
    n = A.shape[0]

    # 计算所有 特征值, 特征向量
    eigen_values, eigen_vectors = np.linalg.eig(A)
    max_eigen_value = np.max(eigen_values)

    # 一致性指标
    CI = (max_eigen_value - n) / (n - 1)

    RI_list = [0, 0.0001, 0.52, 0.89, 1.12, 1.26, 1.36, 1.41, 1.46, 1.49, 1.52, 1.54, 1.56, 1.58, 1.59]
    # 查表即可
    RI = RI_list[n - 1]

    # 一致性比例
    CR = CI / RI

    if CR < 0.1:
        print(f"[通过] CR={np.abs(CR):.3f}<0.1 -> 判断矩阵A的一致性可以接受")
    else:
        raise ValueError("注意, CR>0.1, 所以判断矩阵A需要修改")


def mean(A: np.ndarray):
    n = A.shape[0]

    stand_A = A / np.sum(A, axis=0)

    sum_A = np.sum(stand_A, axis=1)

    weights = sum_A / n

    return weights  # (n,)


def geo_mean(A: np.ndarray):
    n = A.shape[0]

    prod_A = np.prod(A, axis=1)  # prod: product: 乘积
    prod_A = prod_A ** (1 / n)  # 开根号n

    weights = prod_A / np.sum(prod_A)  # 归一化

    return weights  # (n,)


def eigen(A: np.ndarray):
    n = A.shape[0]

    # 所有特征值eig_values, 所有特征向量eig_vectors
    # 注意: numpy.linalg.eig 返回的特征向量eig_vectors是以`列向量`形式排列的
    eig_values, eig_vectors = np.linalg.eig(A)
    # 去掉复数部分
    eig_values = np.abs(eig_values)
    eig_vectors = np.real(eig_vectors)

    # 找到最大特征值
    max_index = np.argmax(eig_values)
    # 及其对应的特征向量
    max_vector = eig_vectors[:, max_index]

    weights = max_vector / np.sum(max_vector)

    return weights  # (n,)


def b_analytic_hierarchy_process(
        A: np.ndarray,
        mode: Literal["mean", "geo_mean", "eigen"]
) -> np.ndarray:
    """
    层次分析法: AHP: analytic hierarchy process
    -> 得到各个指标的权重

    n个指标
    :param A: 判断矩阵, 形状(n, n)
    :param mode: 层次分析法的模式,
                包括"mean"(算术平均法), "geo_mean"(几何平均法), "eigen"(特征值法)
    :return: 各个指标的权重, 形状(n,)
    """
    # 一致性检验
    check_consistency(A)

    match mode:
        case "mean":  # 算术平均法
            weights = mean(A)
        case "geo_mean":  # 几何平均法
            weights = geo_mean(A)
        case "eigen":  # 特征值法
            weights = eigen(A)
        # 除此之外
        case _:
            raise ValueError("mode参数错误")

    return weights


b_AHP = b_analytic_hierarchy_process


if __name__ == '__main__':
    import numpy as np

    A = np.array([
        [1, 2, 3, 5],
        [1 / 2, 1, 1 / 2, 2],
        [1 / 3, 2, 1, 2],
        [1 / 5, 1 / 2, 1 / 2, 1]
    ])
    weights = b_AHP(A, "mean")
    print(weights)
    weights = b_AHP(A, "geo_mean")
    print(weights)
    weights = b_AHP(A, "eigen")
    print(weights)
