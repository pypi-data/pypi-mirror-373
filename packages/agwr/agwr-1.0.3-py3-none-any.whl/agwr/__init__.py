"""
AGWR - 各向异性地理加权回归模型

一个用于实现各向异性地理加权回归(Anisotropic Geographically Weighted Regression)的Python包。
该包基于研究论文中的数学理论，提供了稳定、高效的AGWR模型实现。

主要功能:
- 各向异性核函数计算
- 坐标投影转换
- AGWR模型拟合和预测
- 模型诊断和评估

作者: AGWR开发团队
版本: 1.0.0
"""

from .model import AGWR
from .kernels import anisotropic_kernel, anisotropic_kernel_projected
from .utils import project_coordinates

__version__ = "1.0.0"
__author__ = "AGWR开发团队"

__all__ = [
    "AGWR",
    "anisotropic_kernel", 
    "anisotropic_kernel_projected",
    "project_coordinates"
]
