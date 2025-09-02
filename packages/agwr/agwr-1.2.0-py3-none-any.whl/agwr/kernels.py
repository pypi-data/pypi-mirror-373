import numpy as np


def projected_distance_vector(coord1: np.ndarray, coord2: np.ndarray) -> np.ndarray:
    """
    计算两个投影坐标点之间的方向性距离向量（公里）。
    
    参数:
        coord1: np.ndarray - 2元素数组，表示第一个点的投影坐标 [x, y]（米）
        coord2: np.ndarray - 2元素数组，表示第二个点的投影坐标 [x, y]（米）
    
    返回:
        np.ndarray - 2元素数组，表示方向性距离向量 [dx, dy]（公里）
    
    注意:
        - 输入坐标应该是投影坐标系中的 [x, y] 坐标（米）
        - 返回的距离向量保持方向性，单位为公里
    """
    # 计算X和Y方向的距离（米）
    dx = coord1[0] - coord2[0]  # X方向距离（米）
    dy = coord1[1] - coord2[1]  # Y方向距离（米）
    
    # 转换为公里
    dx_km = dx / 1000.0
    dy_km = dy / 1000.0
    
    return np.array([dx_km, dy_km])


def anisotropic_kernel(h: np.ndarray, theta: np.ndarray) -> float:
    """
    计算各向异性高斯核函数值。
    
    该函数实现了公式: exp(-sum(h**2 / theta))
    其中h是地理距离向量，theta是各向异性带宽向量。
    
    参数:
        h: np.ndarray - 2元素数组，表示地理距离向量 [distance_u, distance_v]
           distance_u是u方向的地理距离（公里），distance_v是v方向的地理距离（公里）
        theta: np.ndarray - 2元素数组，表示各向异性带宽 [theta_u, theta_v]
               theta_u和theta_v可以不同，实现各向异性效果（单位：公里）
    
    返回:
        float - 计算得到的核函数权重值
    
    示例:
        >>> h = np.array([10.5, 20.3])  # 10.5公里和20.3公里的距离
        >>> theta = np.array([50.0, 100.0])  # 50公里和100公里的带宽
        >>> result = anisotropic_kernel(h, theta)
        >>> print(f"核函数值: {result:.6f}")
    """
    # 步骤1: 对h向量进行逐元素平方
    h_squared = h ** 2
    
    # 步骤2: 将平方结果除以theta向量（逐元素除法）
    # 结果: [(distance_u**2 / theta_u), (distance_v**2 / theta_v)]
    h_squared_over_theta = h_squared / theta
    
    # 步骤3: 对结果向量求和，然后计算其负值的指数
    kernel_value = np.exp(-np.sum(h_squared_over_theta))
    
    return kernel_value


def anisotropic_kernel_projected(coord1: np.ndarray, coord2: np.ndarray, theta: np.ndarray) -> float:
    """
    使用投影坐标计算各向异性高斯核函数值。
    
    参数:
        coord1: np.ndarray - 2元素数组，表示第一个点的投影坐标 [x, y]（米）
        coord2: np.ndarray - 2元素数组，表示第二个点的投影坐标 [x, y]（米）
        theta: np.ndarray - 2元素数组，表示各向异性带宽 [theta_u, theta_v]（公里）
    
    返回:
        float - 计算得到的核函数权重值
    """
    # 计算方向性距离向量（公里）
    h = projected_distance_vector(coord1, coord2)
    
    # 使用各向异性核函数计算权重
    return anisotropic_kernel(h, theta)
