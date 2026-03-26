import numpy as np
import json
import matplotlib.pyplot as plt
import networkx as nx
from scipy.optimize import minimize

# 用于凸优化的包
import cvxpy as cp

# 所有的超级参数放置处,避免乱飞
class SimulationConfig:
    def __init__(self, e_R, B, epsilon_max):
        # 节点数量
        self.N = 10
        # 步长
        self.Gamma = (1/(2 * self.N))

        # 引理一参数
        # 容错率参数
        self.sigma = 0.05
        # 限制的最大偏移量
        self.b = 1

        # 实验变量
        # 容忍误差
        self.e_R = e_R
        # 边预算
        self.B = B
        # 隐私上限
        # 需要传入一个长度为10的numpy数组
        self.epsilon_max = epsilon_max
        self.s = 0.01

# 拓扑&矩阵相关类
class GraphTopology:
    def __init__(self,N, edges_list):
        # 这里构建一个简单的无权图
        # edges接受一个无权图,并转换为np矩阵
        self.N = N
        # 建立无权邻接矩阵 A0 (作为掩码 Mask)
        self.A0 = np.zeros((N, N))
        for u, v in edges_list:
            # 转换为 0-based 索引 (1变0, 10变9)
            self.A0[int(u) - 1, int(v) - 1] = 1
            self.A0[int(v) - 1, int(u) - 1] = 1

        # 记录所有存在的边的位置，方便 CVXPY 约束非零边
        self.existing_edges = np.where(self.A0 == 1)

    # 接受一个权重矩阵,返回拉普拉斯矩阵
    def build_laplacian(self, W):
        # W 应该是一个 numpy 的权重矩阵 (N x N)
        # 计算每一行的和，得到度向量
        degrees = np.sum(W, axis=1)
        # 用度向量构造对角阵 D
        D = np.diag(degrees)
        # L = D - W
        return D - W

    # 计算输入矩阵L的特征值,并返回lambda_2
    def get_algebraic_connectivity(self, L):
        # 由于L在本项目中必为对称矩阵
        eigenvalues = np.linalg.eigh(L)[0]
        lambda_2 = eigenvalues[1]
        return lambda_2

class ACSOptimizer:

    def solve_subproblem_1(self, fixed_epsilon, config, topology):
        N = config.N
        W = cp.Variable((N, N), symmetric=True)
        y = cp.Variable()

        # 1. 基础约束
        constraints = [
            W >= 0,
            cp.diag(W) == 0,
            cp.sum(W) <= 2 * config.B,  # 边预算约束
            cp.multiply(W, 1 - topology.A0) == 0  # 拓扑掩码：不存在的边权重为0
        ]

        # 2. 连通度约束：y <= lambda_2(L)
        # 变换为 L + 11.T/N >> yI
        L = cp.diag(cp.sum(W, axis=1)) - W
        ones_matrix = np.ones((N, N)) / N
        constraints += [L + ones_matrix >> y * np.eye(N)]

        # 3. 误差约束 (Theorem 2)
        # 计算隐私噪声总和：Σ f(eps_i) * C_wi
        M = np.eye(N) - (np.ones((N, N)) / N)
        total_privacy_noise = 0
        for i in range(N):
            f_eps = get_f_epsilon(fixed_epsilon[i], config)
            # C_wi = wi.T * M * wi
            total_privacy_noise += f_eps * cp.quad_form(W[i, :], M)

        env_noise = (N - 1) / (N * config.Gamma) * (config.s ** 2) * N  # 环境噪声项

        # 这里的约束是：(隐私项 + 环境项) / (e_R) <= y(2 - Gamma*y)
        # y(2 - Gamma*y) 在 CVXPY 里写成 2*y - Gamma*cp.square(y)
        rhs = 2 * y - config.Gamma * cp.square(y)
        constraints += [
            (config.Gamma * 1.0 / (N * config.e_R)) * total_privacy_noise + (env_noise / config.e_R) <= rhs
        ]

        prob = cp.Problem(cp.Minimize(-y), constraints)
        prob.solve(solver=cp.SCS)  # 或者使用 ECOS
        return W.value, y.value
    # 固定W,y,使得epsilon最小化
    def solve_subproblem_2(self, fixed_W, fixed_y, config):
        N = config.N
        # 1. 预计算 C_wi 常数项
        M = np.eye(N) - (np.ones((N, N)) / N)
        C_values = np.array([fixed_W[i, :] @ M @ fixed_W[i, :].T for i in range(N)])

        # 预计算误差约束的右侧 (RHS) 和 环境噪声
        rhs = fixed_y * (2 - config.Gamma * fixed_y)
        env_noise = (N - 1) / (N * config.Gamma) * (config.s ** 2) * N

        # 2. 定义目标函数：最小化 Σ eps_i^2
        def objective(eps):
            return np.sum(eps ** 2)

        # 3. 定义误差约束函数 (SciPy 里的不等式约束默认要求 fun >= 0)
        def constraint_func(eps):
            f_eps_array = get_f_epsilon(eps, config)
            total_privacy_noise = np.sum(C_values * f_eps_array)
            # 左侧表达式
            lhs = (config.Gamma * 1.0 / (N * config.e_R)) * total_privacy_noise + (env_noise / config.e_R)
            return rhs - lhs  # 要求 rhs - lhs >= 0，即 lhs <= rhs

        constraints = {'type': 'ineq', 'fun': constraint_func}

        # 4. 定义变量边界：避免分母为0，且不超过给定的最大隐私上限

        # 强制转为float，消除类型警告
        bounds = [(1e-5, float(config.epsilon_max[i])) for i in range(N)]

        # 5. 初始猜测：从最宽松的 epsilon_max 开始
        eps0 = np.copy(config.epsilon_max)

        # 6. 一键求解
        res = minimize(objective, eps0, method='SLSQP', bounds=bounds, constraints=[constraints])

        if not res.success:
            print("  [警告] 子问题2未完美收敛:", res.message)

        return res.x
    # 控制子问题进行循环,直到两次的差值小于tol
    def run_acs(self, config, topology, max_iter=20, tol=1e-4):
        print("\n 开始执行交替凸搜索 (ACS) 算法...")
        # 初始化：以允许的最大隐私参数作为起点
        eps_current = np.copy(config.epsilon_max)

        # 记录每轮的目标函数值，方便画收敛图
        history_obj = []

        W_new, y_new = None, None  # 【新增这一行，消除IDE警告】

        for iteration in range(max_iter):
            print(f"\n--- Iteration {iteration + 1} ---")

            # 锁死 eps，去求解拓扑连通度 W 和 y
            W_new, y_new = self.solve_subproblem_1(eps_current, config, topology)

            if W_new is None or y_new is None:
                print("❌ 优化断裂：在当前设定下无法找到合法的拓扑结构 (Infeasible)。")
                print("💡 建议：尝试增大 e_R (容忍误差) 或增大 B (预算)。")
                return None, None, None

            print(f"  [Sub-1] 成功！当前网络连通度下界 y = {y_new:.5f}")

            # 锁死算出来的网络拓扑，去极限压榨隐私参数 eps
            eps_new = self.solve_subproblem_2(W_new, y_new, config)

            # 统计当前轮次的目标结果
            current_obj = np.sum(eps_new ** 2) - y_new
            history_obj.append(current_obj)
            print(f"  [Sub-2] 成功！隐私惩罚 Σeps^2 = {np.sum(eps_new ** 2):.5f}")

            # 检查是否收敛
            diff = np.linalg.norm(eps_new - eps_current)
            if diff < tol:
                print(f"\n 算法在第 {iteration + 1} 步完美收敛！")
                eps_current = eps_new
                break

            eps_current = eps_new

        return W_new, y_new, eps_current, history_obj

# 下面的是可能需要用到的工具类函数
def get_f_epsilon(eps, config):
    """计算隐私噪声系数项的平方 (σ^2相关项) - 纯数值版本"""
    k_delta = np.sqrt(2 * np.log(1.25 / config.sigma))
    term = (config.b / eps) * (k_delta + np.sqrt(k_delta ** 2 + 2 * eps))
    return term ** 2

# 下面是用来测试的测试逻辑
# 已注释
if __name__ != "__main__":
    with open("initial_edges.json", "r") as f:
        graph_topology = json.load(f)
        graph_topology = np.array(graph_topology['initial_edges'[:]])
        # print(graph_topology)
        edges = np.array(graph_topology)
        # print(edges)
        eps_max = np.array([0.4, 0.9, 0.55, 0.35, 0.8, 0.45, 0.7, 0.5, 0.52, 0.58])
        print("正在初始化环境配置...")
        # 测试参数：e_R = 16 (论文 Example 1 的中间档), B = 6
        config = SimulationConfig(e_R=16.0, B=6.0, epsilon_max=eps_max)
        topology = GraphTopology(N=config.N, edges_list=edges)
        optimizer = ACSOptimizer()

        # 启动！
        W_opt, y_opt, eps_opt, history = optimizer.run_acs(config, topology)

        if eps_opt is not None:
            print("\n 最终计算得出的各节点隐私参数 eps:")
            for i, val in enumerate(eps_opt):
                print(f"Agent {i + 1}: {val:.4f} (上限: {eps_max[i]:.4f})")
        # 绘图复现
        import draw
        draw.plot_results(W_opt, eps_opt, eps_max, config, edges)
