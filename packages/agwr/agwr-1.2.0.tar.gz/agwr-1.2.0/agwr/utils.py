import numpy as np
from pyproj import Transformer


def create_coordinate_transformer():
    """
    创建坐标转换器，将地理坐标转换为UTM投影坐标。
    
    返回:
        pyproj.Transformer - 坐标转换器对象
    """
    # UTM Zone 50N适用于江苏省大部分地区
    transformer = Transformer.from_crs("EPSG:4326", "EPSG:32650", always_xy=True)
    return transformer


def project_coordinates(coords: np.ndarray) -> np.ndarray:
    """
    将地理坐标投影到平面坐标系
    
    参数:
        coords: np.ndarray - 形状为(n, 2)的数组，包含[经度, 纬度]坐标
    
    返回:
        np.ndarray - 形状为(n, 2)的数组，包含投影后的[x, y]坐标（米）
    """
    # 创建坐标转换器
    transformer = create_coordinate_transformer()
    
    # 提取经度和纬度
    lons = coords[:, 0]
    lats = coords[:, 1]
    
    # 执行坐标转换
    x_coords, y_coords = transformer.transform(lons, lats)
    
    # 返回投影后的坐标
    projected_coords = np.column_stack([x_coords, y_coords])
    
    return projected_coords
