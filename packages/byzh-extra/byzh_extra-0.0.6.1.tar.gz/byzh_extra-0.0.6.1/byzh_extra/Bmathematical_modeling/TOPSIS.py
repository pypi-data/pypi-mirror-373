# 优劣解距离法: TOPSIS: Technique for Order Preference by Similarity an Ideal Solution
import numpy as np
from typing import Literal
from byzh_core.Butils import b_validate_params

from .math_utils import l2_normalize

def minTomax(x):  # 极小型处理方法
    max_x = np.max(x)
    array = max_x - x
    return array


def midTomax(x, bestx):  # 中间型处理方法
    delta_x = np.abs(x - bestx)
    M = max(delta_x)
    if M == 0:
        M = 1
    array = 1 - delta_x / M

    return array

def rangeTomax(x, lowx, highx):  # 区间型处理方法
    M = max(lowx - min(x), max(x) - highx)
    if M == 0:
        M = 1

    array = []
    for i in range(len(x)):
        if x[i] < lowx:
            array.append(1 - (lowx - x[i]) / M)
        elif x[i] <= highx:
            array.append(1)
        else:
            array.append(1 - (x[i] - highx) / M)
    array = np.array(array)

    return array

def max_better_normalization(
        A: np.ndarray,
        kind: list
):
    """
    矩阵正向化
    按列来
    :param A:
    :return:
    """
    def get_str(element):
        if isinstance(element, (tuple, list)):
            return element[0]
        elif isinstance(element, str):
            return element
        else:
            raise ValueError("kind参数错误")

    # 检查
    n, m = A.shape
    assert len(kind) == m, "kind参数长度与矩阵列数不一致"

    # 正向化
    result = A.copy().astype(float)
    for i in range(m):
        element = kind[i]
        # 极大型
        if get_str(element) == "max_better":
            continue
        # 极小型
        elif get_str(element) == "min_better":
            result[:, i] = minTomax(result[:, i])
        # 中间型
        elif get_str(element) == "mid_better":
            bestA = element[1]
            result[:, i] = midTomax(result[:, i], bestA)
        # 区间型
        elif get_str(element) == "interval_better":
            lowA, highA = element[1], element[2]
            result[:, i] = rangeTomax(result[:, i], lowA, highA)
        else:
            raise ValueError("kind参数错误")

    return result



@b_validate_params({
    "A": np.ndarray,
    "kind": {
        "type": list(
            Literal[
                "max_better",
                "min_better",
                ("mid_better", 'mid_num'),
                ("interval_better", 'low_num', 'high_num')
            ]
        ),
        "example": ["max_better", ("mid_better", 165), "min_better", ("interval_better", 90, 100)]
    }
})
def b_topsis(
        A: np.ndarray,
        kind: list
):
    """
    优劣解距离法: TOPSIS: Technique for Order Preference by Similarity an Ideal Solution
    -> 获得各候选项的得分

    n个候选项
    m个指标
    :param A:
    :param kind: 各指标的正向化类型
    :return:
    """
    n, m = A.shape

    # 正向化
    A = max_better_normalization(A, kind)

    # l2归一化(列)
    A = l2_normalize(A, "v")

    # 每个指标的 最大值, 最小值集
    A_max = np.max(A, axis=0)  # (m,)
    A_min = np.min(A, axis=0)  # (m,)

    # 每个候选项与之的距离
    d_z = np.sqrt(np.sum((A - A_max) ** 2, axis=1))  # (n,)
    d_f = np.sqrt(np.sum((A - A_min) ** 2, axis=1))  # (n,)

    # 每个候选项的得分
    s = d_f / (d_z + d_f)
    score = 100 * s / sum(s)  # 换为百分制

    return score

if __name__ == '__main__':

    A = np.array([
        [9, 10, 175, 120],
        [8, 7, 164, 80],
        [6, 3, 157, 90]
    ])

    score = b_topsis(
        A,
        ["max_better", "min_better", ("mid_better", 165), ("interval_better", 90, 100)]
    )

    print(score)