import pandas as pd
import numpy as np
import sys
import os

# 添加包路径到sys.path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from agwr.model import AGWR


def test_simple_model():
    """
    测试最简单的AGWR模型
    """
    print("=" * 80)
    print("测试简单AGWR模型")
    print("=" * 80)
    
    # 1. 创建更简单的模拟数据
    print("\n1. 创建简单模拟数据...")
    np.random.seed(42)
    n = 20  # 更少的观测数量
    
    # 创建模拟坐标
    lons = np.random.uniform(116.0, 122.0, n)
    lats = np.random.uniform(30.0, 35.0, n)
    coords = np.column_stack([lons, lats])
    
    # 创建更简单的变量
    Pop = np.random.uniform(50, 200, n)  # 人口
    Pgdp = np.random.uniform(5, 15, n)   # 人均GDP
    
    # 创建因变量（房价）
    price = 0.1 * Pop + 0.3 * Pgdp + np.random.normal(0, 0.5, n)
    
    # 创建DataFrame
    X = pd.DataFrame({
        'Pop': Pop,
        'Pgdp': Pgdp
    })
    y = pd.Series(price)
    
    print(f"  观测数量: {n}")
    print(f"  变量数量: {X.shape[1]}")
    
    # 2. 定义最简单的模型配置
    print("\n2. 定义模型配置...")
    local_vars = ['intercept']  # 只有截距项作为局部变量
    global_vars = ['Pop', 'Pgdp']  # 其他都是全局变量
    
    # 添加截距项到X
    X['intercept'] = 1.0
    
    print(f"  局部变量: {local_vars}")
    print(f"  全局变量: {global_vars}")
    
    # 3. 实例化并拟合模型
    print("\n3. 拟合AGWR模型...")
    model = AGWR(m=3)  # 使用更少的节点
    
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
        
        print("\n" + "=" * 80)
        print("✓ 简单AGWR模型测试通过！")
        print("=" * 80)
        
        return True
        
    except Exception as e:
        print(f"\n✗ 模型拟合失败: {e}")
        print("\n" + "=" * 80)
        print("✗ 测试失败")
        print("=" * 80)
        return False


if __name__ == "__main__":
    test_simple_model()
