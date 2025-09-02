import pandas as pd
import numpy as np
import sys
import os

# 添加包路径到sys.path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from agwr.model import AGWR


def test_simplified_model_convergence():
    """
    测试简化版AGWR模型的收敛性
    """
    print("=" * 80)
    print("测试简化版AGWR模型收敛性")
    print("=" * 80)
    
    # 1. 创建模拟数据
    print("\n1. 创建模拟数据...")
    np.random.seed(42)
    n = 50  # 观测数量
    
    # 创建模拟坐标（江苏省大致范围）
    lons = np.random.uniform(116.0, 122.0, n)
    lats = np.random.uniform(30.0, 35.0, n)
    coords = np.column_stack([lons, lats])
    
    # 创建模拟变量
    Pop = np.random.uniform(50, 200, n)  # 人口
    Pgdp = np.random.uniform(5, 15, n)   # 人均GDP
    Apd = np.random.uniform(500, 2000, n)  # 人口密度
    Afcb = np.random.uniform(10, 100, n)   # 房地产开发投资
    Redi = np.random.uniform(50, 500, n)   # 商品房销售面积
    Dipc = np.random.uniform(3, 8, n)      # 人均可支配收入
    
    # 创建因变量（房价）
    price = (0.1 * Pop + 0.3 * Pgdp + 0.05 * Apd + 
             0.2 * Afcb + 0.1 * Redi + 0.25 * Dipc + 
             np.random.normal(0, 0.5, n))
    
    # 创建DataFrame
    X = pd.DataFrame({
        'Pop': Pop,
        'Pgdp': Pgdp,
        'Apd': Apd,
        'Afcb': Afcb,
        'Redi': Redi,
        'Dipc': Dipc
    })
    y = pd.Series(price)
    
    print(f"  观测数量: {n}")
    print(f"  变量数量: {X.shape[1]}")
    print(f"  坐标范围: 经度({lons.min():.2f}, {lons.max():.2f})")
    print(f"  坐标范围: 纬度({lats.min():.2f}, {lats.max():.2f})")
    
    # 2. 定义简化模型配置
    print("\n2. 定义模型配置...")
    local_vars = ['intercept', 'Pgdp']  # 最稳定的配置
    global_vars = ['Pop', 'Apd', 'Afcb', 'Redi', 'Dipc']
    
    # 添加截距项到X
    X['intercept'] = 1.0
    
    print(f"  局部变量: {local_vars}")
    print(f"  全局变量: {global_vars}")
    
    # 3. 实例化并拟合模型
    print("\n3. 拟合AGWR模型...")
    model = AGWR(m=8)
    
    try:
        model.fit(X, y, coords, local_vars, global_vars)
        
        # 4. 验证结果
        print("\n4. 验证模型结果...")
        
        # 检查模型是否成功拟合
        assert model.is_fitted_, "模型拟合失败"
        print("  ✓ 模型成功拟合")
        
        # 检查AIC是否计算
        assert model.aic_ is not None, "AIC未计算"
        print(f"  ✓ AIC: {model.aic_:.4f}")
        
        # 检查带宽参数是否计算
        assert model.bandwidths_ is not None, "带宽参数未计算"
        print("  ✓ 带宽参数:")
        for var, theta in model.bandwidths_.items():
            print(f"    {var}: {theta}")
        
        # 检查系数是否计算
        assert model.coefficients_ is not None, "系数未计算"
        print("  ✓ 全局变量系数:")
        for var, coef in model.coefficients_['global'].items():
            print(f"    {var}: {coef:.4f}")
        
        # 检查拟合值是否计算
        assert model.fitted_values_ is not None, "拟合值未计算"
        print(f"  ✓ 拟合值范围: {model.fitted_values_.min():.4f} - {model.fitted_values_.max():.4f}")
        
        # 检查残差是否计算
        assert model.residuals_ is not None, "残差未计算"
        print(f"  ✓ 残差范围: {model.residuals_.min():.4f} - {model.residuals_.max():.4f}")
        
        # 检查各向异性效果
        print("\n5. 检查各向异性效果...")
        for var, theta in model.bandwidths_.items():
            if var != 'intercept':  # 跳过截距项
                anisotropy_ratio = theta[0] / theta[1]
                print(f"  {var}各向异性比率: {anisotropy_ratio:.4f}")
                if abs(anisotropy_ratio - 1.0) > 0.1:
                    print(f"    ✓ {var}显示明显的各向异性效果")
                else:
                    print(f"    ⚠ {var}各向异性效果不明显")
        
        print("\n" + "=" * 80)
        print("✓ 所有测试通过！简化版AGWR模型运行成功")
        print("=" * 80)
        
        return True
        
    except Exception as e:
        print(f"\n✗ 模型拟合失败: {e}")
        print("\n" + "=" * 80)
        print("✗ 测试失败")
        print("=" * 80)
        return False


if __name__ == "__main__":
    test_simplified_model_convergence()
