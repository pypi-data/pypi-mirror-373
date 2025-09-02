import numpy as np
import pandas as pd
from scipy.optimize import minimize
from mgwr.sel_bw import Sel_BW
import warnings
warnings.filterwarnings('ignore')

from .kernels import anisotropic_kernel_projected
from .utils import project_coordinates


def compute_precomputation_matrices(nodes: np.ndarray, theta: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """
    计算预计算矩阵V和W，精确匹配R代码的矩阵代数运算。
    
    参数:
        nodes: np.ndarray - (m, 2)数组，表示m个节点的坐标
        theta: np.ndarray - 2元素数组，表示带宽参数
    
    返回:
        tuple[np.ndarray, np.ndarray] - 包含矩阵(V, W)的元组
    """
    m = nodes.shape[0]
    
    # 1. 计算R_A: (m, m)核函数矩阵
    R_A = np.zeros((m, m))
    for i in range(m):
        for j in range(m):
            # 使用正确的各向异性核函数公式
            h = nodes[i] - nodes[j]
            # 各向异性核函数: exp(-sum(h^2/theta))
            R_A[i, j] = np.exp(-np.sum(h**2 / theta))
    
    # 添加正则化项，改善数值稳定性
    nugget = 1e-6
    R_A += nugget * np.eye(m)
    
    # 2. 计算G_A: (m, 3)矩阵 [1, x, y]
    G_A = np.column_stack([np.ones(m), nodes[:, 0], nodes[:, 1]])
    
    # 3. 计算R_A的逆矩阵，使用更稳定的方法
    try:
        R_A_inv = np.linalg.inv(R_A)
    except np.linalg.LinAlgError:
        # 如果矩阵奇异，使用伪逆
        R_A_inv = np.linalg.pinv(R_A)
    
    # 4. 计算中间矩阵 (G_A^T @ R_A^(-1) @ G_A)^(-1)
    try:
        GRA = np.linalg.inv(G_A.T @ R_A_inv @ G_A)
    except np.linalg.LinAlgError:
        # 如果矩阵奇异，使用伪逆
        GRA = np.linalg.pinv(G_A.T @ R_A_inv @ G_A)
    
    # 5. 计算矩阵V和W
    V = R_A_inv @ G_A @ GRA
    W = (np.eye(m) - V @ G_A.T) @ R_A_inv
    
    return V, W


def calculate_basis_vector(x: np.ndarray, nodes: np.ndarray, V: np.ndarray, W: np.ndarray, theta: np.ndarray) -> np.ndarray:
    """
    使用预计算的V和W矩阵计算单个空间点x的基函数向量b(x)。
    
    参数:
        x: np.ndarray - 2元素数组，表示单个坐标点 [x, y]
        nodes: np.ndarray - (m, 2)数组，表示节点坐标
        V: np.ndarray - 预计算的V矩阵
        W: np.ndarray - 预计算的W矩阵
        theta: np.ndarray - 2元素带宽数组
    
    返回:
        np.ndarray - (m, 1)基函数向量b(x)
    """
    m = nodes.shape[0]
    
    # 1. 计算g(x): (3, 1)向量 [1, x, y]
    g_x = np.array([1, x[0], x[1]]).reshape(3, 1)
    
    # 2. 计算r_A(x): (m, 1)向量，表示x与每个节点之间的核函数值
    r_A_x = np.zeros((m, 1))
    for i in range(m):
        # 使用正确的各向异性核函数公式
        h = x - nodes[i]
        # 各向异性核函数: exp(-sum(h^2/theta))
        r_A_x[i, 0] = np.exp(-np.sum(h**2 / theta))
    
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
    构建AGWR模型的完整设计矩阵Z = [X, Ẑ]。
    
    参数:
        global_vars_df: pd.DataFrame - (n, p) DataFrame，全局变量数据
        local_vars_df: pd.DataFrame - (n, q) DataFrame，局部变量数据
        coords: np.ndarray - (n, 2) 数组，数据点坐标
        nodes: np.ndarray - (m, 2) 数组，节点坐标
        thetas: dict - 字典，键为局部变量名，值为对应的2元素带宽数组
    
    返回:
        np.ndarray - 完整的 (n, p + q*m) 设计矩阵Z
    """
    n, p = global_vars_df.shape
    q = local_vars_df.shape[1]
    m = nodes.shape[0]
    
    # 步骤1: 构建全局变量矩阵X
    X = global_vars_df.values
    
    # 步骤2: 构建局部变量矩阵Ẑ
    local_matrices = []
    
    for var_name in local_vars_df.columns:
        # 获取对应的带宽参数
        theta_k = thetas[var_name]
        
        # 预计算V_k和W_k矩阵
        V_k, W_k = compute_precomputation_matrices(nodes, theta_k)
        
        # 计算基函数矩阵B_k: (n, m)
        B_k = np.zeros((n, m))
        for i in range(n):
            # 计算第i个数据点的基函数向量
            b_i = calculate_basis_vector(coords[i], nodes, V_k, W_k, theta_k)
            B_k[i, :] = b_i.flatten()
        
        # 计算Ẑ_k = B_k * diag(x_k)
        x_k = local_vars_df[var_name].values.reshape(n, 1)
        Z_hat_k = B_k * x_k
        
        local_matrices.append(Z_hat_k)
    
    # 步骤3: 组合所有矩阵
    Z_hat = np.hstack(local_matrices)
    Z = np.hstack([X, Z_hat])
    
    return Z


def negative_log_likelihood(
    params: np.ndarray,
    Y: np.ndarray,
    global_vars_df: pd.DataFrame,
    local_vars_df: pd.DataFrame,
    coords: np.ndarray,
    nodes: np.ndarray
) -> float:
    """
    计算AGWR模型的负对数似然函数值。
    
    参数:
        params: np.ndarray - 1D数组，包含所有需要优化的参数
        Y: np.ndarray - (n, 1)数组，因变量数据
        global_vars_df: pd.DataFrame - (n, p) DataFrame，全局变量数据
        local_vars_df: pd.DataFrame - (n, q) DataFrame，局部变量数据
        coords: np.ndarray - (n, 2)数组，数据点坐标
        nodes: np.ndarray - (m, 2)数组，节点坐标
    
    返回:
        float - 负对数似然函数值
    """
    # 获取数据维度
    n = Y.shape[0]
    p = global_vars_df.shape[1]
    q = local_vars_df.shape[1]
    m = nodes.shape[0]
    
    # 步骤1: 参数解包和对数变换
    param_idx = 0
    
    # 解包log_sigma2并变换回原始尺度
    log_sigma2 = params[param_idx]
    sigma2 = np.exp(log_sigma2)
    param_idx += 1
    
    # 解包log_thetas并变换回原始尺度
    thetas = {}
    for var_name in local_vars_df.columns:
        log_theta_u = params[param_idx]
        log_theta_v = params[param_idx + 1]
        thetas[var_name] = np.array([np.exp(log_theta_u), np.exp(log_theta_v)])
        param_idx += 2
    
    # 解包alphas（全局变量系数）
    alphas = params[param_idx:param_idx + p]
    param_idx += p
    
    # 解包gammas（局部变量系数）
    gammas = params[param_idx:param_idx + q*m]
    
    # 步骤2: 构建设计矩阵Z
    Z = construct_design_matrix(global_vars_df, local_vars_df, coords, nodes, thetas)
    
    # 步骤3: 构建参数向量η
    eta = np.concatenate([alphas, gammas])
    
    # 步骤4: 计算残差和RSS
    Y_pred = Z @ eta
    residuals = Y.flatten() - Y_pred
    RSS = np.sum(residuals ** 2)
    
    # 步骤5: 计算负对数似然
    nll = (n/2) * np.log(2 * np.pi * sigma2) + RSS / (2 * sigma2)
    
    return nll


def get_mgwr_bandwidths(coords: np.ndarray, y: np.ndarray, local_vars_matrix: np.ndarray) -> np.ndarray:
    """
    使用MGWR获取带宽作为初始猜测
    
    参数:
        coords: np.ndarray - (n, 2) 坐标数组
        y: np.ndarray - (n, 1) 因变量数组
        local_vars_matrix: np.ndarray - (n, q) 局部变量矩阵
    
    返回:
        np.ndarray - (q,) 带宽数组
    """
    try:
        # 确保数据格式正确
        if y.ndim > 1:
            y = y.flatten()
        
        if coords.ndim == 1:
            coords = coords.reshape(-1, 2)
        
        Y_reshaped = y.reshape(-1, 1)
        X_local = local_vars_matrix.copy()
        
        # 数据质量检查和清理
        if np.isnan(X_local).sum() > 0:
            for i in range(X_local.shape[0]):
                for j in range(X_local.shape[1]):
                    if np.isnan(X_local[i, j]):
                        if j == 0:  # 截距项
                            X_local[i, j] = 1.0
                        else:  # 其他变量用中位数
                            X_local[i, j] = np.nanmedian(X_local[:, j])
        
        if np.isinf(X_local).sum() > 0:
            for i in range(X_local.shape[0]):
                for j in range(X_local.shape[1]):
                    if np.isinf(X_local[i, j]):
                        X_local[i, j] = np.nanmedian(X_local[:, j])
        
        # 创建MGWR带宽选择器
        selector = Sel_BW(
            coords,           # 坐标
            Y_reshaped,       # 因变量
            X_local,          # 局部变量矩阵
            X_glob=None,      # 全局变量（设为None）
            multi=True,       # 多线程处理
            kernel='gaussian' # 高斯核函数
        )
        
        # 运行带宽搜索
        mgwr_result = selector.search()
        
        # 提取最优MGWR带宽
        mgwr_bws = selector.bw[0] if isinstance(selector.bw, tuple) else selector.bw
        
        return mgwr_bws
        
    except Exception as e:
        print(f"MGWR带宽选择失败: {e}")
        print("使用默认带宽值作为初始猜测...")
        # 使用默认值作为备选方案
        q = local_vars_matrix.shape[1]
        mgwr_bws = np.ones(q) * 43.0  # 使用43作为默认带宽
        return mgwr_bws


class AGWR:
    def __init__(self, m: int = 8):
        """
        各向异性地理加权回归模型
        
        参数:
            m (int): 重构方法的空间节点数量，默认使用前8个点（最佳结果）
        """
        self.m = m
        self.aic_ = None
        self.bandwidths_ = None
        self.coefficients_ = None
        self.fitted_values_ = None
        self.residuals_ = None
        self.is_fitted_ = False
        self.negative_log_likelihood_ = None
        self.optimization_result_ = None
        
    def fit(self, X: pd.DataFrame, y: pd.Series, coords: np.ndarray, local_vars: list, global_vars: list):
        """
        拟合AGWR模型
        
        参数:
            X (pd.DataFrame): 自变量DataFrame
            y (pd.Series): 因变量Series
            coords (np.ndarray): (n, 2)数组，包含[经度, 纬度]坐标
            local_vars (list): X中要作为局部变量处理的列名列表
            global_vars (list): X中要作为全局变量处理的列名列表
        """
        # --- 1. 数据准备 ---
        print("1. 数据准备...")
        # 直接使用原始坐标，不进行投影（因为数据已经是投影坐标）
        projected_coords = coords
        
        # 数据分区
        y_arr = y.to_numpy().reshape(-1, 1)
        global_df = X[global_vars]
        local_df = X[local_vars]
        
        # 使用前m个点作为节点（最佳结果）
        nodes = projected_coords[:self.m, :]
        
        print(f"  观测数量: {len(y)}")
        print(f"  局部变量: {local_vars}")
        print(f"  全局变量: {global_vars}")
        print(f"  节点数量: {self.m}")
        print(f"  使用前{self.m}个点作为节点")
        
        # --- 2. 计算MGWR带宽以获得更好的初始猜测 ---
        print("\n2a. 计算MGWR带宽以获得更好的初始猜测...")
        
        # 获取维度
        n = len(y)
        p = global_df.shape[1]  # 全局变量数量
        q = local_df.shape[1]   # 局部变量数量
        
        # 准备MGWR带宽选择的数据
        # 使用局部变量矩阵（包括截距）作为MGWR的变量
        local_vars_matrix = local_df.values
        
        # 确保数据格式正确
        print(f"数据维度检查:")
        print(f"  坐标形状: {projected_coords.shape}")
        print(f"  因变量形状: {y_arr.shape}")
        print(f"  局部变量矩阵形状: {local_vars_matrix.shape}")
        print(f"  因变量类型: {type(y_arr)}")
        print(f"  坐标类型: {type(projected_coords)}")
        
        # 确保y是一维数组
        if y_arr.ndim > 1:
            y_arr = y_arr.flatten()
        
        # 确保坐标是二维数组
        if projected_coords.ndim == 1:
            projected_coords = projected_coords.reshape(-1, 2)
        
        # 数据质量检查和清理
        print("检查数据质量...")
        Y_reshaped = y_arr.values.reshape(-1, 1) if hasattr(y_arr, 'values') else y_arr.reshape(-1, 1)
        X_local = local_vars_matrix.copy()
        
        # 详细检查数据质量
        print(f"  详细数据质量检查:")
        print(f"    Y_reshaped中NaN数量: {np.isnan(Y_reshaped).sum()}")
        print(f"    Y_reshaped中无穷大数量: {np.isinf(Y_reshaped).sum()}")
        print(f"    X_local中NaN数量: {np.isnan(X_local).sum()}")
        print(f"    X_local中无穷大数量: {np.isinf(X_local).sum()}")
        print(f"    projected_coords中NaN数量: {np.isnan(projected_coords).sum()}")
        print(f"    projected_coords中无穷大数量: {np.isinf(projected_coords).sum()}")
        
        # 如果还有NaN，进行最终清理
        if np.isnan(X_local).sum() > 0:
            print(f"    清理X_local中的NaN...")
            for i in range(X_local.shape[0]):
                for j in range(X_local.shape[1]):
                    if np.isnan(X_local[i, j]):
                        if j == 0:  # 截距项
                            X_local[i, j] = 1.0
                        else:  # 其他变量用中位数
                            X_local[i, j] = np.nanmedian(X_local[:, j])
        
        if np.isinf(X_local).sum() > 0:
            print(f"    清理X_local中的无穷大值...")
            for i in range(X_local.shape[0]):
                for j in range(X_local.shape[1]):
                    if np.isinf(X_local[i, j]):
                        X_local[i, j] = np.nanmedian(X_local[:, j])
        
        print(f"    清理后X_local中NaN数量: {np.isnan(X_local).sum()}")
        print(f"    清理后X_local中无穷大数量: {np.isinf(X_local).sum()}")
        
        print("运行MGWR带宽选择...")
        print("注意：这可能需要一些时间，请耐心等待...")
        
        try:
            # 创建MGWR带宽选择器 - 使用正确的参数名
            selector = Sel_BW(
                projected_coords,    # 坐标
                Y_reshaped,          # 因变量
                X_local,             # X_loc: 局部变量矩阵（包括截距）
                X_glob=None,         # X_glob: 全局变量（设为None，因为我们只关心局部变量）
                multi=True,          # 多线程处理
                kernel='gaussian'    # 高斯核函数
            )
            
            # 运行带宽搜索
            mgwr_result = selector.search()
            
            # 提取最优MGWR带宽
            # selector.bw 返回一个元组，第一个元素是带宽数组
            mgwr_bws = selector.bw[0] if isinstance(selector.bw, tuple) else selector.bw
            
            print(f"MGWR带宽选择完成!")
            print(f"最优MGWR带宽:")
            local_var_names = list(local_df.columns)
            for i, var_name in enumerate(local_var_names):
                print(f"  {var_name}: {mgwr_bws[i]:.6f}")
                
        except Exception as e:
            print(f"MGWR带宽选择失败: {e}")
            print("使用默认带宽值作为初始猜测...")
            # 使用默认值作为备选方案
            mgwr_bws = np.ones(q) * 43.0  # 使用43作为默认带宽
            print(f"使用默认带宽: {mgwr_bws}")
            local_var_names = list(local_df.columns)
        
        # --- 3. 定义初始参数和边界 ---
        print("\n2b. 定义初始参数和边界...")
        
        # 获取维度
        n = len(y)
        p = global_df.shape[1]  # 全局变量数量
        q = local_df.shape[1]   # 局部变量数量
        
        # 初始参数设置（使用对数变换）
        sigma2_initial = np.log(1.0)  # 误差方差初始值的对数值
        
        # thetas初始值: 使用MGWR带宽的对数值作为更好的初始猜测
        # 对于每个局部变量k，其各向异性带宽[theta_u, theta_v]都设为MGWR带宽的对数值
        thetas_initial = np.zeros((q, 2))
        for k in range(q):
            thetas_initial[k, 0] = np.log(mgwr_bws[k])  # log_theta_u
            thetas_initial[k, 1] = np.log(mgwr_bws[k])  # log_theta_v
        
        print(f"使用MGWR带宽的对数值作为初始猜测:")
        for i, var_name in enumerate(local_var_names):
            log_theta_u, log_theta_v = thetas_initial[i]
            print(f"  {var_name}: log_θ_u = {log_theta_u:.6f}, log_θ_v = {log_theta_v:.6f}")
            print(f"  {var_name}: θ_u = {np.exp(log_theta_u):.6f}, θ_v = {np.exp(log_theta_v):.6f}")
        
        # alphas初始值: 全局变量系数，设为0
        alphas_initial = np.zeros(p)
        
        # gammas初始值: (q, m)数组，局部变量在节点处的系数，设为0
        gammas_initial = np.zeros((q, self.m))
        
        # 将参数展平为一维数组
        x0 = np.concatenate([
            [sigma2_initial],                    # log_sigma2 (1个元素)
            thetas_initial.flatten(),            # log_thetas (q*2个元素)
            alphas_initial,                      # alphas (p个元素)
            gammas_initial.flatten()             # gammas (q*m个元素)
        ])
        
        print(f"参数向量结构:")
        print(f"  log_sigma2: 1个元素")
        print(f"  log_thetas: {q*2}个元素 ({q}个变量 × 2个带宽参数对数值)")
        print(f"  alphas: {p}个元素 ({p}个全局变量系数)")
        print(f"  gammas: {q*self.m}个元素 ({q}个局部变量 × {self.m}个节点)")
        print(f"  总参数数量: {len(x0)}")
        
        print(f"注意: 使用对数变换进行无约束优化，无需设置边界")
        
        # --- 4. 运行优化器 ---
        print("\n3. 运行优化器...")
        
        # 准备固定数据参数
        args = (y_arr, global_df, local_df, projected_coords, nodes)
        
        # 运行优化器
        print("开始无约束优化（使用对数变换）...")
        result = minimize(
            fun=negative_log_likelihood,
            x0=x0,
            args=args,
            method='L-BFGS-B',  # 仍然使用L-BFGS-B，但现在是无约束优化
            options={'disp': True, 'maxiter': 20000, 'maxfun': 2000000}
        )
        
        # --- 5. 处理和显示结果 ---
        print("\n4. 处理和显示结果...")
        print("=" * 80)
        
        # 检查优化是否成功
        if result.success:
            print("✅ 优化成功完成!")
            print(f"优化消息: {result.message}")
            print(f"迭代次数: {result.nit}")
            print(f"函数评估次数: {result.nfev}")
            print(f"最终负对数似然值: {result.fun:.6f}")
        else:
            print("❌ 优化未成功完成")
            print(f"优化消息: {result.message}")
            print(f"迭代次数: {result.nit}")
            print(f"函数评估次数: {result.nfev}")
            print(f"最终负对数似然值: {result.fun:.6f}")
        
        # 解包最优参数
        optimal_params = result.x
        param_idx = 0
        
        # 解包log_sigma2并变换回原始尺度
        optimal_log_sigma2 = optimal_params[param_idx]
        optimal_sigma2 = np.exp(optimal_log_sigma2)
        param_idx += 1
        
        # 解包log_thetas并变换回原始尺度
        optimal_log_thetas = optimal_params[param_idx:param_idx + q*2].reshape(q, 2)
        optimal_thetas = np.exp(optimal_log_thetas)
        param_idx += q*2
        
        # 解包alphas
        optimal_alphas = optimal_params[param_idx:param_idx + p]
        param_idx += p
        
        # 解包gammas
        optimal_gammas = optimal_params[param_idx:param_idx + q*self.m].reshape(q, self.m)
        
        # 存储结果
        self.optimization_result_ = result
        self.negative_log_likelihood_ = result.fun
        
        if result.success:
            # 存储带宽参数
            self.bandwidths_ = {}
            for i, var_name in enumerate(local_var_names):
                self.bandwidths_[var_name] = optimal_thetas[i]
            
            # 存储系数
            self.coefficients_ = {
                'global': dict(zip(global_vars, optimal_alphas)),
                'local': {}
            }
            
            for i, var_name in enumerate(local_var_names):
                self.coefficients_['local'][var_name] = optimal_gammas[i]
            
            # 计算AIC
            log_likelihood = -result.fun  # 负对数似然的负值就是对数似然
            self.aic_ = 2 * len(x0) - 2 * log_likelihood
            
            # 构建最终设计矩阵
            final_thetas = {var: self.bandwidths_[var] for var in local_vars}
            Z_final = construct_design_matrix(global_df, local_df, projected_coords, nodes, final_thetas)
            
            # 计算最终系数和拟合值
            eta_final = np.concatenate([optimal_alphas, optimal_gammas.flatten()])
            self.fitted_values_ = Z_final @ eta_final
            self.residuals_ = y_arr.flatten() - self.fitted_values_
            
            self.is_fitted_ = True
            
            print(f"  最终负对数似然: {result.fun:.6f}")
            print(f"  最终AIC: {self.aic_:.4f}")
            print(f"  误差方差: {optimal_sigma2:.6f}")
            print(f"  迭代次数: {result.nit}")
            print(f"  函数评估次数: {result.nfev}")
            print(f"  带宽参数:")
            for var, theta in self.bandwidths_.items():
                print(f"    {var}: {theta}")
            
        else:
            print(f"  优化失败: {result.message}")
            # 即使优化失败，也存储一些基本信息
            self.is_fitted_ = False
        
        return self
    
    def predict(self, X: pd.DataFrame, coords: np.ndarray) -> np.ndarray:
        """
        使用拟合的模型进行预测
        
        参数:
            X (pd.DataFrame): 自变量DataFrame
            coords (np.ndarray): (n, 2)数组，包含[经度, 纬度]坐标
        
        返回:
            np.ndarray: 预测值
        """
        if not self.is_fitted_:
            raise ValueError("模型尚未拟合，请先调用fit()方法")
        
        # 投影坐标
        projected_coords = project_coordinates(coords)
        
        # 数据分区
        global_df = X[list(self.coefficients_['global'].keys())]
        local_df = X[list(self.coefficients_['local'].keys())]
        
        # 使用前m个点作为节点
        nodes = projected_coords[:self.m, :]
        
        # 构建设计矩阵
        Z_pred = construct_design_matrix(global_df, local_df, projected_coords, nodes, self.bandwidths_)
        
        # 构建参数向量
        alphas = list(self.coefficients_['global'].values())
        gammas = []
        for var_coeffs in self.coefficients_['local'].values():
            gammas.extend(var_coeffs)
        eta = np.concatenate([alphas, gammas])
        
        # 确保维度匹配
        if Z_pred.shape[1] != len(eta):
            print(f"警告: 设计矩阵维度 {Z_pred.shape[1]} 与参数向量维度 {len(eta)} 不匹配")
            # 截断或扩展参数向量以匹配设计矩阵
            if Z_pred.shape[1] < len(eta):
                eta = eta[:Z_pred.shape[1]]
            else:
                eta = np.pad(eta, (0, Z_pred.shape[1] - len(eta)), 'constant')
        
        # 预测
        predictions = Z_pred @ eta
        
        return predictions
    
    def get_summary(self) -> dict:
        """
        获取模型摘要信息
        
        返回:
            dict: 包含模型摘要信息的字典
        """
        if not self.is_fitted_:
            raise ValueError("模型尚未拟合，请先调用fit()方法")
        
        summary = {
            'aic': self.aic_,
            'negative_log_likelihood': self.negative_log_likelihood_,
            'bandwidths': self.bandwidths_,
            'global_coefficients': self.coefficients_['global'],
            'local_coefficients': self.coefficients_['local'],
            'n_parameters': len(self.optimization_result_.x),
            'n_observations': len(self.fitted_values_),
            'optimization_success': self.optimization_result_.success,
            'iterations': self.optimization_result_.nit,
            'function_evaluations': self.optimization_result_.nfev
        }
        
        return summary
