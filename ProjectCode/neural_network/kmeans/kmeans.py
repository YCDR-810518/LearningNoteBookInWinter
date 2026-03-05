import numpy as np
from anaconda_project.internal.cli.console_utils import print_status_errors

class Kmeans:
    def __init__(self, K):
        # 初始要设定的分类数（质心）
        self.K = K
        # 具体的质心
        self.centroids = []

    # 用来训练的函数
    # 传入的是代表了整个数据集的矩阵
    def train(self, X, max_iters=100):
        # 1. 随机初始化
        if X.shape[0] < self.K:
            raise ValueError("样本量不足")

        idx = np.random.choice(X.shape[0], self.K, replace=False)
        self.centroids = X[idx].astype(float)

        for i in range(max_iters):
            # 2. 归类 (利用你的逻辑)
            labels = self.classify(X)

            # 3. 更新质心
            new_centroids = np.zeros_like(self.centroids)
            for k in range(self.K):
                cluster_points = X[labels == k]

                if len(cluster_points) > 0:
                    new_centroids[k] = np.mean(cluster_points, axis=0)
                else:
                    # 揪住那个反常：处理空簇 (策略 B)
                    new_centroids[k] = X[np.random.choice(X.shape[0])]

            # 4. 判断收敛：微小的反常也是发现。如果质心位置完全不变，则退出
            if np.allclose(self.centroids, new_centroids):
                print(f"在第 {i} 次迭代时发现规律：质心已稳定。")
                break

            self.centroids = new_centroids.copy()


    # 质点的质心计算及归类函数
    # 接受X作为全体样本点
    # 返回一个标签集
    def classify(self, X):
        if X.shape[0] == 0:
            raise ValueError('未选取初始质点')
        if self.K == 0:
            raise ValueError('X不存在可以使用的样本')

        # 这里生成了一个全零的集合
        # 储存了每个点对应的质心索引
        labels = np.zeros(X.shape[0])
        for idx, i in enumerate(X):
            # 计算距离
            D = np.sqrt(np.sum((self.centroids - i) ** 2, axis=1))
            # 找到最近质心的编号
            closest_idx = np.argmin(D)
            # 归类到簇中
            labels[idx] = closest_idx
        return labels


# 准备数据
X = np.array([[2,3], [5,8], [1,7], [8,2], [9,4], [1,1]])
model = Kmeans(K=2)
model.train(X)
print("最终质心：\n", model.centroids)