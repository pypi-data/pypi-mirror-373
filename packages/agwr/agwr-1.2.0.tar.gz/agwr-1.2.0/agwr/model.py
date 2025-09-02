import numpy as np
import pandas as pd
from scipy.optimize import minimize
from mgwr.sel_bw import Sel_BW

from .kernels import anisotropic_kernel_projected
from .utils import project_coordinates


def compute_precomputation_matrices(nodes: np.ndarray, theta: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """
    计算预计算矩阵V和W，完全匹配原始成功脚本的实现。
    
    参数:
        nodes: np.ndarray - (m, 2)数组，表示m个节点的坐标（米单位）
        theta: np.ndarray - 2元素数组，表示带宽参数（公里单位）
    
    返回:
        tuple[np.ndarray, np.ndarray] - 包含矩阵(V, W)的元组
    """
    m = nodes.shape[0]
    
    # 1. 计算R_A: (m, m)核函数矩阵
    R_A = np.zeros((m, m))
    for i in range(m):
        for j in range(m):
            # 使用简化的核函数，完全匹配原始脚本
            h = nodes[i] - nodes[j]  # 距离向量（米）
            R_A[i, j] = np.exp(-h @ h * theta[0])  # 使用第一个theta值
    
    # 添加正则化项
    nugget = 1e-8
    R_A += nugget * np.eye(m)
    
    # 2. 计算G_A: (m, 3)矩阵 [1, x, y]
    G_A = np.column_stack([np.ones(m), nodes[:, 0], nodes[:, 1]])
    
    # 3. 计算R_A的逆矩阵
    R_A_inv = np.linalg.inv(R_A)
    
    # 4. 计算中间矩阵 (G_A^T @ R_A^(-1) @ G_A)^(-1)
    GRA = np.linalg.inv(G_A.T @ R_A_inv @ G_A)
    
    # 5. 计算矩阵V和W
    V = R_A_inv @ G_A @ GRA
    W = (np.eye(m) - V @ G_A.T) @ R_A_inv
    
    return V, W


def calculate_basis_vector(x: np.ndarray, nodes: np.ndarray, V: np.ndarray, W: np.ndarray, theta: np.ndarray) -> np.ndarray:
    """
    计算基函数向量b(x)，完全匹配原始成功脚本的实现。
    
    参数:
        x: np.ndarray - 2元素数组，表示目标点的坐标（米单位）
        nodes: np.ndarray - (m, 2)数组，表示m个节点的坐标（米单位）
        V: np.ndarray - (m, 3)矩阵，预计算的V矩阵
        W: np.ndarray - (m, m)矩阵，预计算的W矩阵
        theta: np.ndarray - 2元素数组，表示带宽参数（公里单位）
    
    返回:
        np.ndarray - (m, 1)基函数向量
    """
    m = nodes.shape[0]
    
    # 1. 计算g(x): (3, 1)向量 [1, x, y]
    g_x = np.array([1, x[0], x[1]]).reshape(3, 1)
    
    # 2. 计算r_A(x): (m, 1)向量，表示x与每个节点之间的核函数值
    r_A_x = np.zeros((m, 1))
    for i in range(m):
        # 使用简化的核函数，完全匹配原始脚本
        h = x - nodes[i]  # 距离向量（米）
        r_A_x[i, 0] = np.exp(-h @ h * theta[0])  # 使用第一个theta值
    
    # 3. 计算基函数向量: b(x) = V @ g_x + W @ r_A_x
    b_x = V @ g_x + W @ r_A_x
    
    return b_x


def construct_design_matrix(
    global_vars_df: pd.DataFrame,
    local_vars_df: pd.DataFrame,
    coords: np.ndarray,
    nodes: np.ndarray,
    thetas: dict
) -> np.ndarray:
    """
    构建AGWR模型的完整设计矩阵Z = [X, Ẑ]，完全匹配原始成功脚本的实现。
    
    参数:
        global_vars_df: pd.DataFrame - (n, p) DataFrame，全局变量数据
        local_vars_df: pd.DataFrame - (n, q) DataFrame，局部变量数据
        coords: np.ndarray - (n, 2) 数组，数据点坐标（米单位）
        nodes: np.ndarray - (m, 2) 数组，节点坐标（米单位）
        thetas: dict - 字典，键为局部变量名，值为对应的2元素带宽数组（公里单位）
    
    返回:
        np.ndarray - (n, p + q*m) 设计矩阵
    """
    n = len(coords)
    p = global_vars_df.shape[1]
    q = local_vars_df.shape[1]
    m = len(nodes)
    
    # 初始化设计矩阵
    Z = np.zeros((n, p + q * m))
    
    # 1. 添加全局变量部分 X
    Z[:, :p] = global_vars_df.values
    
    # 2. 添加局部变量部分 Ẑ
    col_idx = p
    for var_name in local_vars_df.columns:
        theta = thetas[var_name]
        
        # 预计算V和W矩阵
        V, W = compute_precomputation_matrices(nodes, theta)
        
        # 为每个观测点计算基函数向量
        for i in range(n):
            b_x = calculate_basis_vector(coords[i], nodes, V, W, theta)
            Z[i, col_idx:col_idx + m] = b_x.flatten()
        
        col_idx += m
    
    return Z


def negative_log_likelihood(params, y, global_vars_df, local_vars_df, coords, nodes):
    """
    计算AGWR模型的负对数似然函数，完全匹配原始成功脚本的实现。
    
    参数:
        params: np.ndarray - 参数向量
        y: np.ndarray - 因变量
        global_vars_df: pd.DataFrame - 全局变量数据
        local_vars_df: pd.DataFrame - 局部变量数据
        coords: np.ndarray - 坐标数据（米单位）
        nodes: np.ndarray - 节点坐标（米单位）
    
    返回:
        float - 负对数似然值
    """
    try:
        # 解包参数
        param_idx = 0
        
        # log_sigma2
        log_sigma2 = params[param_idx]
        sigma2 = np.exp(log_sigma2)
        param_idx += 1
        
        # log_thetas
        q = local_vars_df.shape[1]
        log_thetas = params[param_idx:param_idx + q * 2]
        thetas_array = np.exp(log_thetas)
        param_idx += q * 2
        
        # alphas (全局系数)
        p = global_vars_df.shape[1]
        alphas = params[param_idx:param_idx + p]
        param_idx += p
        
        # gammas (局部系数)
        m = len(nodes)
        gammas_array = params[param_idx:param_idx + q * m]
        gammas = gammas_array.reshape(q, m)
        
        # 构建thetas字典
        thetas = {}
        local_vars = list(local_vars_df.columns)
        for i, var_name in enumerate(local_vars):
            thetas[var_name] = thetas_array[i*2:(i+1)*2]
        
        # 构建设计矩阵
        Z = construct_design_matrix(global_vars_df, local_vars_df, coords, nodes, thetas)
        
        # 计算系数向量
        gammas_flat = gammas.flatten()
        eta = np.concatenate([alphas, gammas_flat])
        
        # 计算预测值
        y_pred = Z @ eta
        
        # 计算残差
        residuals = y.flatten() - y_pred
        
        # 计算负对数似然
        n = len(y)
        log_likelihood = -0.5 * n * np.log(2 * np.pi * sigma2) - 0.5 * np.sum(residuals**2) / sigma2
        
        return -log_likelihood
        
    except Exception as e:
        # 如果计算失败，返回一个很大的值
        return 1e10


class AGWR:
    """
    各向异性地理加权回归模型，完全基于原始成功脚本的实现。
    """
    
    def __init__(self, m=8, max_iter=5000):
        """
        初始化AGWR模型。
        
        参数:
            m: int - 空间节点数量
            max_iter: int - 最大迭代次数
        """
        self.m = m
        self.max_iter = max_iter
        self.model_ = None
        self.aic_ = None
        self.bandwidths_ = None
        self.coefficients_ = None
        
    def _calculate_mgwr_bandwidths(self, y: np.ndarray, local_df: pd.DataFrame, coords: np.ndarray) -> np.ndarray:
        """
        使用MGWR带宽选择获得高质量的初始带宽猜测，完全匹配原始脚本的实现。
        
        参数:
            y: np.ndarray - 因变量
            local_df: pd.DataFrame - 局部变量数据
            coords: np.ndarray - 投影坐标（米单位）
        
        返回:
            np.ndarray - MGWR带宽数组（公里单位）
        """
        try:
            # 准备MGWR输入数据（使用与原始脚本相同的方法）
            Y_reshaped = y.reshape(-1, 1) if y.ndim == 1 else y
            X_local = local_df.to_numpy()
            coords_py = coords.copy()  # 直接使用投影坐标（米单位）
            
            # 确保坐标是二维数组
            if coords_py.ndim == 1:
                coords_py = coords_py.reshape(-1, 2)
            
            # 使用Sel_BW进行MGWR带宽选择（与原始脚本保持一致）
            selector = Sel_BW(
                coords_py,      # 投影坐标（米单位，与原始脚本一致）
                Y_reshaped,     # 因变量
                X_local,        # 局部变量矩阵
                multi=True,     # 多线程处理
                constant=True   # 包含截距项
            )
            
            # 运行带宽搜索
            selector.search(verbose=False)
            
            # 提取最优MGWR带宽
            mgwr_bws = selector.bw[0] if isinstance(selector.bw, tuple) else selector.bw
            
            # 确保返回numpy数组
            if not isinstance(mgwr_bws, np.ndarray):
                mgwr_bws = np.array([mgwr_bws] * local_df.shape[1])
            
            return mgwr_bws
            
        except Exception as e:
            print(f"  MGWR初始化失败: {e}")
            print("  使用默认带宽估计...")
            # 返回默认带宽值（公里单位）
            default_bws = np.array([0.5] * local_df.shape[1])
            return default_bws
    
    def fit(self, y, global_vars_df, local_vars_df, coords):
        """
        拟合AGWR模型，完全匹配原始成功脚本的实现。
        
        参数:
            y: array-like - 因变量
            global_vars_df: pd.DataFrame - 全局变量数据
            local_vars_df: pd.DataFrame - 局部变量数据
            coords: array-like - 坐标数据（可以是经纬度或投影坐标）
        """
        print("1. 数据准备...")
        
        # 数据预处理
        y_arr = np.array(y).flatten()
        if isinstance(coords, pd.DataFrame):
            coords = coords.values
        coords = np.array(coords)
        
        # 如果坐标是经纬度格式，进行投影转换
        if coords.shape[1] == 2 and np.max(coords[:, 0]) > 180:
            # 已经是投影坐标
            projected_coords = coords
        else:
            # 需要投影转换
            projected_coords = project_coordinates(coords)
        
        print(f"  观测数量: {len(y_arr)}")
        print(f"  局部变量: {list(local_vars_df.columns)}")
        print(f"  全局变量: {list(global_vars_df.columns)}")
        
        # 节点选择（与原始脚本一致）
        n_obs = len(projected_coords)
        if n_obs >= self.m:
            indices = np.linspace(0, n_obs-1, self.m, dtype=int)
            nodes = projected_coords[indices, :]
        else:
            nodes = projected_coords.copy()
            self.m = n_obs
        
        print(f"  节点数量: {self.m}")
        
        print("2. 获取MGWR智能初始带宽估计...")
        
        # 使用MGWR带宽选择获得初始猜测
        try:
            mgwr_bws = self._calculate_mgwr_bandwidths(y_arr, local_vars_df, projected_coords)
            print(f"  MGWR带宽选择成功: {mgwr_bws}")
        except Exception as e:
            print(f"  MGWR初始化失败: {e}")
            print("  使用默认带宽估计...")
            # 使用默认带宽值（公里单位）
            mgwr_bws = np.array([0.5] * local_vars_df.shape[1])
        
        print("3. 设置优化参数...")
        
        # 计算参数维度
        p = global_vars_df.shape[1]  # 全局变量数量
        q = local_vars_df.shape[1]   # 局部变量数量
        
        # 参数向量结构：
        # [log_sigma2, log_theta_1_u, log_theta_1_v, ..., log_theta_q_u, log_theta_q_v, 
        #  alpha_1, ..., alpha_p, 
        #  gamma_1_1, gamma_1_2, ..., gamma_1_m, 
        #  gamma_2_1, gamma_2_2, ..., gamma_2_m,
        #  ...,
        #  gamma_q_1, gamma_q_2, ..., gamma_q_m]
        
        # 初始参数设置
        log_sigma2_init = np.array([np.log(1.0)])  # 初始误差方差对数值
        
        # 使用MGWR带宽作为初始猜测，转换为对数形式
        log_thetas_init = []
        local_vars = list(local_vars_df.columns)
        for i, var_name in enumerate(local_vars):
            mgwr_bw = mgwr_bws[i] if i < len(mgwr_bws) else 0.5
            # 将MGWR带宽转换为两个方向的对数带宽
            log_thetas_init.extend([np.log(mgwr_bw), np.log(mgwr_bw)])
        log_thetas_init = np.array(log_thetas_init)
        
        # 初始系数（设为0）
        alphas_init = np.zeros(p)
        gammas_init = np.zeros(q * self.m)
        
        # 组装初始参数向量
        x0 = np.concatenate([log_sigma2_init, log_thetas_init, alphas_init, gammas_init])
        
        print(f"  参数数量: {len(x0)}")
        print(f"  初始参数向量长度: {len(x0)}")
        
        # 准备优化函数的参数
        args = (y_arr.reshape(-1, 1), global_vars_df, local_vars_df, projected_coords, nodes)
        
        print("4. 运行优化...")
        print("开始AGWR模型优化，这可能需要几分钟...")
        
        try:
            # 使用L-BFGS-B方法进行优化
            result = minimize(
                negative_log_likelihood,
                x0,
                args=args,
                method='L-BFGS-B',
                options={'maxiter': self.max_iter, 'maxfun': 10000, 'disp': True}
            )
            
            print(f"\n优化完成!")
            print(f"  收敛状态: {result.success}")
            print(f"  迭代次数: {result.nit}")
            print(f"  函数调用次数: {result.nfev}")
            print(f"  最终负对数似然值: {result.fun:.6f}")
            
            if not result.success:
                print(f"  警告: 优化未完全收敛")
                print(f"  错误信息: {result.message}")
                raise Exception(f"优化失败: {result.message}")
            
            print("5. 处理优化结果...")
            
            # 解包最优参数
            optimal_params = result.x
            param_idx = 0
            
            # 解包log_sigma2
            optimal_log_sigma2 = optimal_params[param_idx]
            optimal_sigma2 = np.exp(optimal_log_sigma2)
            param_idx += 1
            
            # 解包log_thetas
            optimal_log_thetas = optimal_params[param_idx:param_idx + q*2]
            optimal_thetas_array = np.exp(optimal_log_thetas)
            param_idx += q*2
            
            # 解包alphas
            optimal_alphas = optimal_params[param_idx:param_idx + p]
            param_idx += p
            
            # 解包gammas
            optimal_gammas_array = optimal_params[param_idx:param_idx + q*self.m]
            optimal_gammas = optimal_gammas_array.reshape(q, self.m)
            
            # 计算AIC
            k = len(optimal_params)  # 总参数数量
            logL = -result.fun  # 最终对数似然值
            aic = 2 * k - 2 * logL
            
            # 计算模型拟合统计量
            thetas_dict = {}
            for i, var_name in enumerate(local_vars):
                thetas_dict[var_name] = optimal_thetas_array[i*2:(i+1)*2]
            
            # 使用最优参数重新构建设计矩阵
            X_opt = construct_design_matrix(global_vars_df, local_vars_df, projected_coords, nodes, thetas_dict)
            
            # 计算预测值
            gammas_flat = optimal_gammas.flatten()
            eta_opt = np.concatenate([optimal_alphas, gammas_flat])
            y_pred = X_opt @ eta_opt
            
            # 计算R²和RMSE
            ss_res = np.sum((y_arr - y_pred.flatten()) ** 2)
            ss_tot = np.sum((y_arr - np.mean(y_arr)) ** 2)
            r_squared = 1 - (ss_res / ss_tot)
            rmse = np.sqrt(np.mean((y_arr - y_pred.flatten()) ** 2))
            
            # 存储结果
            self.model_ = {
                'optimal_params': optimal_params,
                'sigma2': optimal_sigma2,
                'thetas': thetas_dict,
                'alphas': optimal_alphas,
                'gammas': optimal_gammas,
                'nodes': nodes,
                'projected_coords': projected_coords,
                'global_vars_df': global_vars_df,
                'local_vars_df': local_vars_df,
                'y_pred': y_pred,
                'r_squared': r_squared,
                'rmse': rmse,
                'log_likelihood': logL
            }
            
            self.aic_ = aic
            self.bandwidths_ = thetas_dict
            self.coefficients_ = {
                'global': dict(zip(global_vars_df.columns, optimal_alphas)),
                'local': dict(zip(local_vars, optimal_gammas))
            }
            
            print(f"✅ AGWR模型拟合成功!")
            print(f"  AIC: {aic:.2f}")
            print(f"  R²: {r_squared:.4f}")
            print(f"  RMSE: {rmse:.4f}")
            
        except Exception as e:
            print(f"❌ AGWR模型拟合失败: {e}")
            self.model_ = None
            self.aic_ = None
            self.bandwidths_ = None
            self.coefficients_ = None
            raise
    
    def predict(self, global_vars_df, local_vars_df, coords):
        """
        使用拟合的AGWR模型进行预测。
        
        参数:
            global_vars_df: pd.DataFrame - 全局变量数据
            local_vars_df: pd.DataFrame - 局部变量数据
            coords: array-like - 坐标数据
        
        返回:
            np.ndarray - 预测值
        """
        if self.model_ is None:
            raise ValueError("模型尚未拟合，请先调用fit方法")
        
        # 数据预处理
        if isinstance(coords, pd.DataFrame):
            coords = coords.values
        coords = np.array(coords)
        
        # 如果坐标是经纬度格式，进行投影转换
        if coords.shape[1] == 2 and np.max(coords[:, 0]) > 180:
            # 已经是投影坐标
            projected_coords = coords
        else:
            # 需要投影转换
            projected_coords = project_coordinates(coords)
        
        # 构建设计矩阵
        X_pred = construct_design_matrix(
            global_vars_df, 
            local_vars_df, 
            projected_coords, 
            self.model_['nodes'], 
            self.model_['thetas']
        )
        
        # 计算预测值
        gammas_flat = self.model_['gammas'].flatten()
        eta = np.concatenate([self.model_['alphas'], gammas_flat])
        y_pred = X_pred @ eta
        
        return y_pred