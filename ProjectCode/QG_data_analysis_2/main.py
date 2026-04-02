import classes
import pandas as pd
import torch
import torch.nn as nn
import torch.optim as optim
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA

with open('QG_train.csv', 'r', encoding='utf-8') as f:
    data = pd.read_csv(f)
    print(data.head())
    print(data.describe())

    # 数据预处理
    # 提取特征值
    data_feature = data.drop('target', axis=1).copy()

    # 提取标签值
    data_label = data['target'].copy()

    # 查看是否成功去除无用值
    print(data_feature.head())
    print(data_label.head())
"""
    # 成功去除无用值
    # 接下来进行模型训练
    X = data_feature.values
    y = data_label.values

    # 标准化（压缩为自然分布，防止维度过高导致svm模型失效）
    # 将sklearn中的方法实例化
    scaler = StandardScaler()
    # 将X转换
    X_scaled = scaler.fit_transform(X)
    print(X_scaled.shape)

    # 强制降维，避免噪声过高撑爆模型
    # PCA方法将10000个特征压缩为200个
    pca = PCA(n_components=200)
    X_processed = pca.fit_transform(X_scaled)

    # 将X，Y转换为适合torch的张量tensor
    X_tensor = torch.FloatTensor(X_processed)
    # 将标签 -1 转换为 0，1 保持不变（PyTorch 交叉熵常用 0/1）
    y_tensor = torch.FloatTensor((y + 1) / 2).view(-1, 1)

    # 从类加载模型，并输入需要搞到权重的特征向量
    # input_dim=X_processed.shape[1]:输入的特征向量维度数
    model = BinaryClassifier(input_dim=X_processed.shape[1])

    # 简单地训练这个简单的神经模型
    criterion = nn.BCELoss()  # 二分类交叉熵损失
    # lr：学习率
    optimizer = optim.Adam(model.parameters(), lr=0.001)

    # 训练循环（简化版）
    for epoch in range(100):
        optimizer.zero_grad()
        outputs = model(X_tensor)
        loss = criterion(outputs, y_tensor)
        # L1正则化，防止一些过低的权重不滚蛋
        loss = loss + 0.01 * torch.norm(model.layer1.weight, 1)
        loss.backward()
        optimizer.step()
    # 取得权重
    # 第一层权重(128,200)
    weights = model.layer1.weight.data.abs().numpy()
    # 对 128 个隐藏单元的权重求平均，得到 200 个特征各自的得分
    importance_scores = weights.mean(axis=0)

    # 找出得分最高的前 20 个特征索引
    top_20_features = importance_scores.argsort()[-20:][::-1]
    print(f"最重要的特征索引: {top_20_features}")

    weights = model.layer1.weight.data.abs().numpy().mean(axis=0)
    # 假设我们只选最重要的 50 个特征
    top_indices = weights.argsort()[-50:]

    # 从原始 10000 维数据中，只切出这 50 列
    X_train_reduced = X_scaled[:, top_indices]

    # 用 SVM 进行最终预测
    from sklearn.svm import SVC

    final_svm = SVC(kernel='linear')  # 或者 'rbf'
    final_svm.fit(X_train_reduced, y)  # 这里的输入只有 50 维了

    print("SVM 训练完成！它只使用了选出的 50 个核心特征。")
"""