import numpy as np
from typing import Literal

# L2归一化
def l2_normalize(A, mod:Literal["v", "h"]):
    n, m = A.shape

    # 行向量归一化
    if mod == "h":
        return A / np.sqrt(np.sum(A*A, axis=1))
    # 列向量归一化
    elif mod == "v":
        return A / np.sqrt(np.sum(A*A, axis=0))
    else:
        raise ValueError("axis should be 0 or 1")
