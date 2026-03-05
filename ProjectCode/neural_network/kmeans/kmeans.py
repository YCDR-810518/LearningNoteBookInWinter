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
    def train(self, X):
        # 初始化质心
        random_indices = np.random.choice(X.shape[0], size=self.K, replace=False)
        self.centroids = X[random_indices].astype(float)  # 确保是浮点数以便计算

        while True:
            # 分类 (调用classify)
            labels = self.classify(X)

            # 计算新质心 (利用均值函数)
            centroids_new = np.zeros_like(self.centroids)
            for k in range(self.K):
                points_in_k = X[labels == k]
                if len(points_in_k) > 0:
                    centroids_new[k] = np.mean(points_in_k, axis=0)

            # 判定是否收敛 (纠着微小差异不放)
            # 使用 allclose 判断两组坐标是否已经足够接近
            if np.allclose(self.centroids, centroids_new):
                break

            self.centroids = centroids_new.copy()  # 更新质心
        print("训练完成！")


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