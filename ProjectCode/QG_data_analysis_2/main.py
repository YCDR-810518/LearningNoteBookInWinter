import pandas as pd
import torch
import torch.nn as nn
import torch.optim as optim
import torch_directml  # 导入 DirectML 库
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from classes import gpu_pca
from sklearn.svm import SVC
import numpy as np

# 设置 AMD 显卡设备
device = torch_directml.device()
print(f"正在使用设备: {device}")

# 假设你的 BinaryClassifier 已经定义或从 classes 导入
from classes import BinaryClassifier

# 加载数据
data = pd.read_csv('QG_train.csv')
X = data.drop('target', axis=1).values
y = data['target'].values

# 预处理
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)
print(f"数据检查 - 是否有NaN: {np.isnan(X_scaled).any()}, 是否有Inf: {np.isinf(X_scaled).any()}")

# 有 101 个样本，PCA 维度不能只设为 4！
# 降到 30-50 维，这样才能保留足够的分类信息
print("正在进行 PCA 降维...")
n_components = min(X.shape[0] - 1, 80)  # PCA 维度不能超过样本数 - 1
X_pca_tensor = gpu_pca(X_scaled, n_components, device)
print(f"PCA 完成，当前特征维度: {X_pca_tensor.shape[1]}")

"""
# 因为已经在显存里面，就不用搬了
# 准备 PyTorch 数据并搬运至显卡
print("正在将tensor搬运至显卡...")
X_tensor = torch.FloatTensor(X_pca).to(device)
print("tensor搬运完成！")
"""
print("正在将tensor搬运至显卡...")
y_tensor = torch.FloatTensor((y + 1) / 2).view(-1, 1).to(device)
print("tensor搬运完成！")

# 初始化模型并搬运至显卡
print("正在初始化模型并搬运至显卡...")
model = BinaryClassifier(input_dim=n_components).to(device)
print("模型初始化并搬运完成！")
optimizer = optim.Adam(model.parameters(), lr=0.01)
criterion = nn.BCELoss()
print("模型初始化完成！")

print("开始神经网络训练...")
# 训练神经网络
for epoch in range(200):
    optimizer.zero_grad()

    # 直接传入 X_pca_tensor，不需要再次搬运
    outputs = model(X_pca_tensor)

    loss = criterion(outputs, y_tensor)

    # L1 正则化 (GPU 加速版写法)
    l1_lambda = 0.005
    l1_loss = sum(torch.sum(torch.abs(p)) for p in model.parameters())
    loss = loss + l1_lambda * l1_loss

    loss.backward()
    optimizer.step()

print("训练完成！")

# 提取权重（需要先搬回 CPU 才能转 numpy）
weights = model.layer1.weight.detach().cpu().abs().numpy().mean(axis=0)

# 选出更多的成分，至少 10 个，才能让 SVM 有足够的信息进行分类
top_k = min(30, n_components)
top_component_indices = weights.argsort()[-top_k:][::-1]
print(f"神经网络选出的核心主成分索引: {top_component_indices}")

# SVM 预测
# SVM 是在 CPU 上运行的，所以要先搬运

# 先把整个大张量搬回 CPU，转成 numpy
X_pca_all_cpu = X_pca_tensor.detach().cpu().numpy()
# 用.copy解决内存非连续报错
X_final_for_svm = X_pca_all_cpu[:, top_component_indices].copy()
print(f"SVM 输入特征形状: {X_final_for_svm.shape}")


# 'rbf' 核通常比 'linear' 效果更好
final_svm = SVC(kernel='rbf', C=1.0)
final_svm.fit(X_final_for_svm, y)

print(f"SVM 在训练集上的预测结果前20个: {final_svm.predict(X_final_for_svm)[:20]}")
print(f"实际标签前20个: {y[:20]}")
print(f"总准确率: {final_svm.score(X_final_for_svm, y):.4f}")

"""
下面是测试程序
"""
# 加载数据
data = pd.read_csv('QG_test.csv')
X_test = data.drop('target', axis=1).values
y_test = data['target'].values

# 预处理
# scaler = StandardScaler() 这里不要重置
X_test_scaled = scaler.transform(X_test) # 注意，这里不是fit——transform，因为要用训练集的均值和方差
print(f"数据检查 - 是否有NaN: {np.isnan(X_test_scaled).any()}, 是否有Inf: {np.isinf(X_test_scaled).any()}")

X_test_pca_tensor = gpu_pca(X_test_scaled, n_components, device)

# 将数据搬回 CPU，并切片
X_test_pca_cpu = X_test_pca_tensor.detach().cpu().numpy().copy()
X_test_final = X_test_pca_cpu[:, top_component_indices].copy()

# 预测
print(f"测试集输入特征形状: {X_test_final.shape}") # 应该是 (样本数, 30)
y_test_pred = final_svm.predict(X_test_final)

print(f"SVM 在测试集上的预测结果前20个: {y_test_pred[:20]}")
print(f"实际标签前20个: {y_test[:20]}")
print(f"测试集总准确率: {final_svm.score(X_test_final, y_test):.4f}")

