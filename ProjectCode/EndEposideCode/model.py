import numpy as np
from utils import TrajectoryTrie

# 将各个模型的模块拆分出来

class LagrangianTrie(TrajectoryTrie):
    """
    基于 Query Probability + Lagrangian 优化
    """

    def allocate_budget(self, total_epsilon):
        # 计算 query probability p_i
        self._compute_query_probability(self.root)

        # 计算权重 w_i = p_i^(1/3)
        self._compute_weights(self.root)

        # 按“每条路径归一化”分配 ε（满足约束）
        self._normalize_budget_per_path(self.root, total_epsilon)

    # -----------------------------
    # 计算 p_i
    # -----------------------------
    def _compute_query_probability(self, node):
        """
        自底向上计算：
        p_i = 1/N + sum(child p_j)

        简化：N 用叶子数近似（工程常用 trick）
        """
        if not node.children:
            node.p = 1.0
            return node.p

        node.p = 1.0 + sum(
            self._compute_query_probability(child)
            for child in node.children.values()
        )
        return node.p

    # -----------------------------
    #  ε_i ∝ p_i^(1/3)
    # -----------------------------
    def _compute_weights(self, node):
        node.weight = np.power(node.p, 1.0 / 3.0)

        for child in node.children.values():
            self._compute_weights(child)

    # -----------------------------
    #  路径归一化（关键！！）
    # -----------------------------
    def _normalize_budget_per_path(self, root, total_epsilon):
        """
        对每条 root->leaf 路径：
        ε_i = w_i / sum(w_path) * total_epsilon
        """

        def dfs(node, path):
            path.append(node)

            if not node.children:
                # 叶子：执行归一化
                total_weight = sum(n.weight for n in path if n != root)

                if total_weight == 0:
                    total_weight = 1e-6

                for n in path:
                    if n == root:
                        continue
                    n.epsilon = (n.weight / total_weight) * total_epsilon

            else:
                for child in node.children.values():
                    dfs(child, path)

            path.pop()

        dfs(root, [])

class LiIncrementalTrie(TrajectoryTrie):
    def allocate_budget(self, total_epsilon):
        sigma = 1.0
        weights = [np.log(lv + sigma) for lv in range(1, self.max_height + 1)]
        total_weight = sum(weights)
        norm_weights = [w / total_weight * total_epsilon for w in weights]

        self._assign_recursive(self.root, norm_weights, level=0)

    def _assign_recursive(self, node, weights, level):
        if level >= self.max_height: return
        for child in node.children.values():
            child.epsilon = weights[level]
            self._assign_recursive(child, weights, level + 1)

class SeqPTTrie(TrajectoryTrie):
    def allocate_budget(self, total_epsilon):
        # SeqPT 的经典做法是按照几何级数或者特定的层级权重分配
        # 越往深层，分配的预算可能越少（因为它假设长路径的敏感度更高）
        weights = [np.power(0.9, i) for i in range(self.max_height)]
        norm_weights = [w / sum(weights) * total_epsilon for w in weights]

        self._assign_recursive(self.root, norm_weights, level=0)

    def _assign_recursive(self, node, weights, level):
        if level >= self.max_height: return
        for child in node.children.values():
            child.epsilon = weights[level]
            self._assign_recursive(child, weights, level + 1)


class SafePathTrie(TrajectoryTrie):
    """
    SafePath 算法模型 (Baseline)
    核心逻辑：采用强力指数衰减分配预算，优先保证靠近根节点的高层路径不被噪声误删。
    """

    def allocate_budget(self, total_epsilon):
        # SafePath 通常使用比 SeqPT (0.9) 更小的衰减因子（如 0.5 或更小）
        # 这样第一层会分到近一半的预算，第二层分到剩余的一半，以此类推
        decay_factor = 0.5

        # 计算每一层的权重
        weights = [np.power(decay_factor, i) for i in range(self.max_height)]

        # 归一化权重，确保所有层级加起来等于 total_epsilon
        sum_weights = sum(weights)
        norm_weights = [(w / sum_weights) * total_epsilon for w in weights]

        # 递归为树中节点赋值
        self._assign_recursive(self.root, norm_weights, level=0)

    def _assign_recursive(self, node, weights, level):
        """
        递归分配预算：
        node: 当前节点
        weights: 预计算好的各层预算列表
        level: 当前层级索引（0 对应根节点的子节点，即轨迹的第一个点）
        """
        if level >= self.max_height:
            return

        for child in node.children.values():
            # 为当前层级的节点分配对应的预算
            child.epsilon = weights[level]

            # 向下递归处理子节点
            if child.children:
                self._assign_recursive(child, weights, level + 1)

    def __repr__(self):
        return f"SafePathTrie(max_height={self.max_height})"