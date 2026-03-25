import numpy as np
import json
import matplotlib.pyplot as plt
import networkx as nx

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
    def solve_subproblem_1(self, fixed_epsilon):
        pass
    # 固定W,y,使得epsilon最小化
    def solve_subproblem_2(self, fixed_W, fixed_y):
        pass
    # 控制子问题进行循环,直到两次的差值小于tol
    def run_acs(self, max_iter=50, tol=1e-4):
        pass
with open("initial_position.json", "r") as read_file:
    initial_position = json.load(read_file)
    initial_position = np.array(initial_position)
    print(initial_position)