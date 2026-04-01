import numpy as np
class SVM:
    """
    支持向量机（二分类）的自定义实现，使用线性核和梯度下降优化
    """

    def __init__(self, C=1.0, max_iter=1000, tol=1e-3, learning_rate=0.01):
        self.C = C  # 正则化参数
        self.max_iter = max_iter  # 最大迭代次数
        self.tol = tol  # 收敛阈值
        self.learning_rate = learning_rate  # 学习率
        self.w = None  # 权重向量
        self.b = 0  # 偏置

    def fit(self, X, y):
        """
        训练 SVM 模型
        :param X: 训练数据
        :param y: 标签 (-1 或 1)
        """
        n_samples, n_features = X.shape
        self.w = np.zeros(n_features)
        self.b = 0

        for _ in range(self.max_iter):
            grad_w = self.w.copy()
            grad_b = 0
            for i in range(n_samples):
                margin = y[i] * (np.dot(self.w, X[i]) + self.b)
                if margin < 1:
                    grad_w -= self.C * y[i] * X[i]
                    grad_b -= self.C * y[i]

            self.w -= self.learning_rate * grad_w
            self.b -= self.learning_rate * grad_b

    def predict(self, X):
        """
        预测标签
        :param X: 测试数据
        :return: 预测标签 (-1 或 1)
        """
        return np.sign(np.dot(X, self.w) + self.b)


class MultiSVM:
    """
    多分类 SVM，使用一对多策略
    """

    def __init__(self, C=1.0, max_iter=1000, tol=1e-3, learning_rate=0.01):
        self.C = C
        self.max_iter = max_iter
        self.tol = tol
        self.learning_rate = learning_rate
        self.svms = []  # 存储每个类的 SVM

    def fit(self, X, y):
        """
        训练多分类 SVM
        :param X: 训练数据
        :param y: 标签 (0, 1, 2)
        """
        classes = np.unique(y)
        for cls in classes:
            y_binary = np.where(y == cls, 1, -1)
            svm = SVM(C=self.C, max_iter=self.max_iter, tol=self.tol, learning_rate=self.learning_rate)
            svm.fit(X, y_binary)
            self.svms.append((cls, svm))

    def predict(self, X):
        """
        预测多分类标签
        :param X: 测试数据
        :return: 预测标签
        """
        predictions = []
        for i in range(X.shape[0]):
            scores = [np.dot(X[i], svm.w) + svm.b for _, svm in self.svms]
            predictions.append(self.svms[np.argmax(scores)][0])
        return np.array(predictions)


def confusion_matrix(y_true, y_pred):
    """
    计算混淆矩阵
    :param y_true: 真实标签
    :param y_pred: 预测标签
    :return: 混淆矩阵和类别列表
    """
    classes = np.unique(np.concatenate([y_true, y_pred]))
    cm = np.zeros((len(classes), len(classes)), dtype=int)
    for true, pred in zip(y_true, y_pred):
        i = np.where(classes == true)[0][0]
        j = np.where(classes == pred)[0][0]
        cm[i, j] += 1
    return cm, classes


def accuracy(cm):
    """
    计算准确率
    :param cm: 混淆矩阵
    :return: 准确率
    """
    return np.trace(cm) / np.sum(cm)
class Config:
    def __init__(self, data):

        self.data = data
        self.data_feature = data.drop(['target'], axis=1).dropna(axis=1).copy()

        self.data_label = None
