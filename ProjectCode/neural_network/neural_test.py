import numpy as np

class Neuron:
    def __init__(self, input_size):
        # 1. 初始化参数 (使用正则化的思想，初始值不宜过大)
        self.W = np.random.randn(input_size, 1) * 0.01
        self.b = 0.0

    def sigmoid(self, z):
        return 1 / (1 + np.exp(-z))

    def forward(self, X):
        # 矩阵乘法：z = XW + b
        # X shape: (n_samples, input_size)
        # W shape: (input_size, 1)
        self.X = X
        self.z = np.dot(X, self.W) + self.b
        self.a = self.sigmoid(self.z)
        return self.a

    # 这里是反向传播
    def backward(self, y_true, learning_rate=0.1):
        # 计算偏导数 (梯度)
        # 假设 Loss 是均方误差，这里简化为 (a - y)
        m = self.X.shape[0]  # 样本数量

        # dz 是损失对 z 的偏导
        dz = self.a - y_true

        # dW 是损失对 W 的偏导：(1/m) * X^T * dz
        # np.dot(self.X.T, dz) 实现了矩阵的偏导累加
        dW = (1 / m) * np.dot(self.X.T, dz)

        # db 是损失对 b 的偏导
        db = (1 / m) * np.sum(dz)

        # 更新参数 (最简单的梯度下降)
        self.W -= learning_rate * dW
        self.b -= learning_rate * db