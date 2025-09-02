# AGWR - 各向异性地理加权回归模型

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![PyPI version](https://badge.fury.io/py/agwr.svg)](https://badge.fury.io/py/agwr)

一个用于实现各向异性地理加权回归(Anisotropic Geographically Weighted Regression)的Python包。该包基于研究论文中的数学理论，提供了稳定、高效的AGWR模型实现。

## 功能特点

- **各向异性核函数**: 支持方向性距离计算和各向异性带宽参数
- **坐标投影**: 自动将地理坐标投影到平面坐标系以获得准确的距离计算
- **模型拟合**: 使用最大似然估计和L-BFGS-B优化算法
- **智能初始化**: 利用MGWR带宽选择器提供智能初始参数
- **模型诊断**: 提供AIC、残差分析等诊断工具
- **易于使用**: 简洁的API设计，类似scikit-learn的使用方式

## 安装

### 从PyPI安装（推荐）

```bash
pip install agwr
```

### 从源码安装

```bash
git clone https://github.com/agwr-team/agwr.git
cd agwr
pip install -e .
```

## 依赖要求

- Python >= 3.8
- numpy >= 1.20.0
- pandas >= 1.3.0
- scipy >= 1.7.0
- pyproj >= 3.0.0
- mgwr >= 2.1.0

## 快速开始

### 基本用法

```python
import pandas as pd
import numpy as np
from agwr import AGWR

# 准备数据
data = pd.DataFrame({
    'price': [1.2, 1.5, 1.8, 2.1, 1.9],  # 房价（万元/平方米）
    'pop': [100, 150, 200, 250, 180],     # 人口（万人）
    'gdp': [8, 10, 12, 15, 11],           # 人均GDP（万元）
    'density': [1000, 1200, 1500, 1800, 1300]  # 人口密度（人/平方公里）
})

# 地理坐标（经度，纬度）
coords = np.array([
    [116.4, 39.9],  # 北京
    [121.5, 31.2],  # 上海
    [113.3, 23.1],  # 广州
    [114.1, 22.5],  # 深圳
    [118.8, 32.0]   # 南京
])

# 定义变量类型
local_vars = ['intercept', 'gdp']      # 局部变量
global_vars = ['pop', 'density']       # 全局变量

# 添加截距项
data['intercept'] = 1.0

# 创建并拟合模型
model = AGWR(m=3)  # 使用3个空间节点
model.fit(data, data['price'], coords, local_vars, global_vars)

# 查看结果
print(f"AIC: {model.aic_:.4f}")
print("带宽参数:")
for var, theta in model.bandwidths_.items():
    print(f"  {var}: {theta}")

print("全局变量系数:")
for var, coef in model.coefficients_['global'].items():
    print(f"  {var}: {coef:.4f}")
```

### 高级用法

```python
# 使用自定义初始参数
model = AGWR(m=8)

# 拟合模型
model.fit(X, y, coords, local_vars, global_vars)

# 检查各向异性效果
for var, theta in model.bandwidths_.items():
    if var != 'intercept':
        anisotropy_ratio = theta[0] / theta[1]
        print(f"{var}各向异性比率: {anisotropy_ratio:.4f}")

# 获取拟合值和残差
fitted_values = model.fitted_values_
residuals = model.residuals_

# 进行预测（需要实现）
# predictions = model.predict(X_new, coords_new)
```

## 模型理论

AGWR模型基于以下数学公式：

### 各向异性核函数

```
K(h, θ) = exp(-∑(h²/θ))
```

其中：
- `h` 是方向性距离向量 `[h_u, h_v]`
- `θ` 是各向异性带宽向量 `[θ_u, θ_v]`

### 重构参数化方法

模型使用重构参数化方法来表示空间变化的系数：

```
β(x) = ∑ᵢ γᵢ bᵢ(x)
```

其中 `bᵢ(x)` 是基函数，`γᵢ` 是节点系数。

### 负对数似然函数

```
L = (n/2) log(2πσ²) + RSS/(2σ²)
```

其中 `RSS` 是残差平方和。

## API参考

### AGWR类

#### 初始化参数

- `m` (int): 重构方法的空间节点数量，默认为8

#### 主要方法

- `fit(X, y, coords, local_vars, global_vars)`: 拟合模型
- `predict(X, coords)`: 进行预测（待实现）

#### 属性

- `aic_`: Akaike信息准则
- `bandwidths_`: 各向异性带宽参数
- `coefficients_`: 模型系数
- `fitted_values_`: 拟合值
- `residuals_`: 残差
- `is_fitted_`: 模型是否已拟合

### 工具函数

- `anisotropic_kernel(h, theta)`: 计算各向异性核函数值
- `anisotropic_kernel_projected(coord1, coord2, theta)`: 使用投影坐标计算核函数
- `project_coordinates(coords)`: 将地理坐标投影到平面坐标系

## 测试

运行测试套件：

```bash
cd agwr_package
python -m pytest tests/
```

或者运行单个测试：

```bash
python tests/test_model.py
```

## 贡献

欢迎贡献代码！请遵循以下步骤：

1. Fork本仓库
2. 创建功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 创建Pull Request

## 许可证

本项目采用MIT许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 引用

如果您在研究中使用了AGWR包，请引用相关论文：

```bibtex
@article{agwr2024,
  title={各向异性地理加权回归模型研究},
  author={AGWR开发团队},
  journal={空间统计学报},
  year={2024}
}
```

## 联系方式

- 项目主页: https://github.com/agwr-team/agwr
- 问题反馈: https://github.com/agwr-team/agwr/issues
- 邮箱: agwr@example.com

## 更新日志

### v1.0.0 (2024-01-01)
- 初始版本发布
- 实现基本的AGWR模型
- 支持各向异性核函数
- 提供坐标投影功能
- 包含完整的测试套件
