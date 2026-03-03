import numpy as np
import json


# 输入的矩阵X形式（样本数，特征数）
# 输入的权重weights形式（特征数，1）
#　矩阵点积后为（结果数＝样本数，１）

class Neuron:
    def __init__(self, weights, bias, learning_rate):
        # 模型的权重
        self.weights = weights
        # 模型的偏差
        self.bias = bias
        # 模型的学习率
        self.learning_rate = learning_rate

    # 这个函数将函数的特征压缩为一个非线性方程，从而激活神经元
    def sigmoid(self, func):
        return 1 / (1 + np.exp(-func))

    # 这里的X就是输入的特征
    def feedforward(self, X):
        # 用sigmoid压缩后得出的就是一个介于0~1之间的数值，即概率
        # 压缩的是y = wx + b这个式子
        output = self.sigmoid(np.dot(X, self.weights)+ self.bias)
        return output

    def loss(self, y_true, y_pred):
        # 1. 计算每一份数据的偏差 (y_true - y_pred)
        # 2. 平方处理以施加“惩罚”并消除负号
        # 3. np.mean 会自动对矩阵求和并除以元素个数
        return np.mean((y_true - y_pred) ** 2)

    # 保存模型为.json格式
    def savemodel(self, filename):
        data = {
            'weights': self.weights.tolist(),
            'bias': self.bias.tolist(),
            'learning_rate': self.learning_rate
        }
        with open(filename, 'w') as f:
            json.dump(data, f)
        print(f'模型已成功保存至{filename}')
    #从同一目录下读取模型文件
    def loadmodel(self, filename):
        with open(filename, 'r') as f:
            data = json.load(f)
            self.weights = np.array(data['weights'])
            self.bias = np.array(data['bias'])
            self.learning_rate = float(data['learning_rate'])
        print(f'模型{filename}已经成功加载！')

    # 梯度下降算法,为权重找到最佳值
    # 这里的学习率由用户确定
    # X是特征向量，y为真实的数据集
    def gradient(self, X, y_true, learning_round,*,load = False):
        # 选择是否加载模型
        if load==True:
            print('请输入要加载的模型名字，要带后缀哦！')
            filename = input()
            self.loadmodel(filename)
        else:
            pass
        # 指定学习轮数
        for i in range(learning_round):
            # 取得当前权重下的预测值
            y_pred = self.feedforward(X)


            # 计算误差项（这里取绝对值会丢失方向）
            error = y_true - y_pred

            # 这里的X矩阵应转置后与误差相乘
            # 结果是（特征数，1）
            # 计算偏导+转置用于平均误差
            dw = (-2 * np.dot(X.T,error))/X.shape[0]
            db = np.mean(-2 * error)

            # 模型迭代
            self.weights -= self.learning_rate * dw
            self.bias -= self.learning_rate * db
            if i % 100 ==0 :
                current_loss = self.loss(y_true, y_pred)
                print(f'\n第{i}轮：\nLoss:{current_loss:.4f},weights:{self.weights[0][0]:.4f},bias:{self.bias[0]:.4f}')
        print('是否保存模型？若是请以.json后缀保存哦！(y/n)')
        choice = input()
        if choice == 'y':
            print('请输入文件名')
            filename = input()
            self.savemodel(filename)
        if choice == 'n':
            pass

    def save_model(self, filename):
        data = {
            'weights': self.weights.tolist(),
            'bias': self.bias.tolist(),
            'learning_rate': self.learning_rate
        }
        with open(filename, 'w') as f:
            json.dump(data, f)
        print(f"模型已成功保存至 {filename} ✨")

# 准备数据
np.random.seed(42) # 固定随机种子，方便复现结果
# 生成 100 行 1 列的湿度数据 (0-100%)，并归一化到 0-1 之间
X = np.random.rand(1000, 1)
# 设定规律：湿度 > 0.5 记为 1 (下雨)，否则为 0
y = (X > 0.5).astype(float)

# 初始化神经元
# 初始权重随机，偏置为 0，学习率设为 0.1
weights = np.random.randn(1, 1)
bias = np.array([0.0])
neuron = Neuron(weights, bias, learning_rate=0.1)

# 开始训练
rounds = 10000
neuron.gradient(X, y, rounds, load=True)

# 1. 生成测试数据：5个随机的湿度值
X_test = np.array([[0.2], [0.4], [0.6], [0.8], [0.1]])
# 对应的真实规律：>0.5 下雨(1), <=0.5 不下雨(0)
y_test = (X_test > 0.5).astype(float)

# 2. 用训练好的神经元进行预测
predictions = neuron.feedforward(X_test)

# 3. 打印结果对比
print("湿度值 | 预测概率 | 真实结果")
for i in range(len(X_test)):
    print(f"{X_test[i][0]:.1f}   | {predictions[i][0]:.4f}  | {int(y_test[i][0])}")