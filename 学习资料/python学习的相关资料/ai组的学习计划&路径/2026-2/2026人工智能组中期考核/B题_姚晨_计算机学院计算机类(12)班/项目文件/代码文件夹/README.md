# 这个文件夹是项目代码文件夹
 下面是论文复现代码的相关内容

## 环境依赖配置（锁定代码运行环境）
### 解释器
* python虚拟环境解释器 3.14.0

## 依赖和包的版本都放在requirement.txt中了

##
## 核心算法框架设计（避免代码混乱，参数乱飞）
### 参数（尤其是超参数）&配置
1. ```SimulationConfig```
* **功能**:集中管理所有参数
* **所需的参数**:
  * 节点数量```N```
  * 步长```gamma```
  * **引理一的参数**:
    * ```sigma_i```
    * ```b_i```
  * 实验变量:
    * 容忍误差 ```e_R```
    * 边预算 ```B```
2. `GraphTopology` (拓扑与矩阵工具类)
* 功能：处理所有与图论、拉普拉斯矩阵和连通度相关的底层线性代数运算。
* 核心方法：
  * ```__init__(self, N, edges)```：输入节点数和初始连通边，构建无权图 $\mathcal{G}_0$。
  * `build_laplacian(self, W)`：输入计算出的权重矩阵 $W$，返回加权拉普拉斯矩阵 $L$。
  * `get_algebraic_connectivity(self, L)`：计算矩阵特征值，返回 $\lambda_2$（用于验证最后的结果是否满足 $y$ 的约束）
3. `ACSOptimizer` (交替凸搜索核心类)
* 功能：论文最核心的算法 2，封装使用 cvxpy 构建和求解优化问题的逻辑。
* 核心方法：
  * `solve_subproblem_1(self, fixed_epsilon)`：
    * 变量：权重矩阵 $W$（需声明为对称矩阵且对角线为 0）、辅助标量 $y$。
    * 约束：$W \ge 0$、不存在的边权重必须为 0、$\text{Tr}(L) \le 2B$、$y \le \lambda_2(L)$、以及替换了固定 $\epsilon$ 后的误差约束（定理 2 不等式）。
    * 目标：最大化 $y$（即最小化 $-y$）。
  * `solve_subproblem_2(self, fixed_W, fixed_y)`：
    * 变量：隐私参数向量 $\epsilon$。
    * 约束：$0 < \epsilon \le \epsilon^{max}$、以及替换了固定 $W$ 后的误差约束。
    * 目标：最小化 $\sum \epsilon_i^2$。
  * `run_acs(self, max_iter=50, tol=1e-4)`：
    * 控制上述两个子问题在 while 循环中交替运行，直到目标函数的两次差值小于 tol，实现收敛。
    * tol:标志了会不会视为收敛
    * max_iter最大轮数