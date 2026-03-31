import numpy as np
import pandas as pd

class DataProcessor:
    """
    数据处理器类，用于加载和预处理红酒质量数据集。
    包括加载CSV文件、编码类别变量、处理缺失值和标准化特征。
    """
    
    def load_data(self, path):
        """
        从指定路径加载CSV数据集。
        
        参数:
        path (str): CSV文件的路径。
        
        返回:
        pd.DataFrame: 加载的数据框。
        """
        return pd.read_csv(path)
    
    def preprocess(self, df):
        """
        预处理数据框，包括编码类别变量、填充缺失值和标准化数值特征。
        
        参数:
        df (pd.DataFrame): 输入的数据框。
        
        返回:
        pd.DataFrame: 预处理后的数据框。
        """
        # 编码类别变量：将'type'列的'white'映射为0，'red'映射为1
        df['type'] = df['type'].map({'white': 0, 'red': 1})
        # 处理缺失值：使用每列的均值填充缺失值，仅对数值列
        df.fillna(df.mean(numeric_only=True), inplace=True)
        # 标准化特征：对除'quality'外的所有特征进行z-score标准化，避免除零错误
        features = df.drop('quality', axis=1)
        df[features.columns] = (features - features.mean()) / (features.std() + 1e-8)
        return df

class LinearRegression:
    """
    线性回归类，使用梯度下降法从头实现线性回归模型。
    用于预测连续目标变量，如红酒质量评分。
    """
    
    def __init__(self, learning_rate=0.1, epochs=10000):
        """
        初始化线性回归模型。
        
        参数:
        learning_rate (float): 梯度下降的学习率，默认0.1。
        epochs (int): 训练的迭代次数，默认10000。
        """
        self.lr = learning_rate
        self.epochs = epochs
        self.weights = None
        self.bias = None
    
    def fit(self, X, y):
        """
        使用梯度下降法训练线性回归模型。
        
        参数:
        X (np.ndarray): 特征矩阵，形状为(n_samples, n_features)。
        y (np.ndarray): 目标向量，形状为(n_samples,)。
        """
        n_samples, n_features = X.shape
        # 初始化权重和偏置为零
        self.weights = np.zeros(n_features)
        self.bias = 0
        # 进行梯度下降迭代
        for _ in range(self.epochs):
            # 计算预测值
            y_pred = np.dot(X, self.weights) + self.bias
            # 计算权重梯度：(1/n) * X.T * (y_pred - y)
            dw = (1 / n_samples) * np.dot(X.T, (y_pred - y))
            # 计算偏置梯度：(1/n) * sum(y_pred - y)
            db = (1 / n_samples) * np.sum(y_pred - y)
            # 更新权重和偏置
            self.weights -= self.lr * dw
            self.bias -= self.lr * db
    
    def predict(self, X):
        """
        使用训练好的模型进行预测。
        
        参数:
        X (np.ndarray): 特征矩阵，形状为(n_samples, n_features)。
        
        返回:
        np.ndarray: 预测的连续值，形状为(n_samples,)。
        """
        return np.dot(X, self.weights) + self.bias

class LogisticRegression:
    """
    逻辑回归类，使用梯度下降法从头实现逻辑回归模型。
    用于二分类任务，如区分好坏红酒。
    """
    
    def __init__(self, learning_rate=0.1, epochs=10000):
        """
        初始化逻辑回归模型。
        
        参数:
        learning_rate (float): 梯度下降的学习率，默认0.1。
        epochs (int): 训练的迭代次数，默认10000。
        """
        self.lr = learning_rate
        self.epochs = epochs
        self.weights = None
        self.bias = None
    
    def sigmoid(self, z):
        """
        Sigmoid激活函数，将线性输出转换为概率。
        
        参数:
        z (np.ndarray): 线性模型输出。
        
        返回:
        np.ndarray: Sigmoid后的概率值，范围[0,1]。
        """
        return 1 / (1 + np.exp(-z))
    
    def fit(self, X, y):
        """
        使用梯度下降法训练逻辑回归模型，优化交叉熵损失。
        
        参数:
        X (np.ndarray): 特征矩阵，形状为(n_samples, n_features)。
        y (np.ndarray): 二分类目标向量，形状为(n_samples,)，值为0或1。
        """
        n_samples, n_features = X.shape
        # 初始化权重和偏置为零
        self.weights = np.zeros(n_features)
        self.bias = 0
        # 进行梯度下降迭代
        for _ in range(self.epochs):
            # 计算线性模型输出
            linear_model = np.dot(X, self.weights) + self.bias
            # 计算预测概率
            y_pred = self.sigmoid(linear_model)
            # 计算权重梯度：(1/n) * X.T * (y_pred - y)
            dw = (1 / n_samples) * np.dot(X.T, (y_pred - y))
            # 计算偏置梯度：(1/n) * sum(y_pred - y)
            db = (1 / n_samples) * np.sum(y_pred - y)
            # 更新权重和偏置
            self.weights -= self.lr * dw
            self.bias -= self.lr * db
    
    def predict(self, X):
        """
        使用训练好的模型进行预测，返回二分类结果。
        
        参数:
        X (np.ndarray): 特征矩阵，形状为(n_samples, n_features)。
        
        返回:
        list: 预测的类别，0或1。
        """
        linear_model = np.dot(X, self.weights) + self.bias
        y_pred = self.sigmoid(linear_model)
        # 阈值0.5进行分类
        return [1 if i > 0.5 else 0 for i in y_pred]

def mse(y_true, y_pred):
    """
    计算均方误差（MSE）。
    
    参数:
    y_true (np.ndarray): 真实值。
    y_pred (np.ndarray): 预测值。
    
    返回:
    float: MSE值。
    """
    return np.mean((y_true - y_pred) ** 2)

def accuracy(y_true, y_pred):
    """
    计算准确率。
    
    参数:
    y_true (np.ndarray): 真实标签。
    y_pred (np.ndarray): 预测标签。
    
    返回:
    float: 准确率，范围[0,1]。
    """
    return np.mean(y_true == y_pred)
