import pandas as pd
import torch
import torch.nn as nn
import torch.optim as optim
import torch_directml  # 导入 DirectML 库
from sklearn.preprocessing import StandardScaler
from sklearn.feature_selection import SelectKBest, f_classif
from sklearn.model_selection import GridSearchCV
from classes import gpu_pca
from sklearn.svm import SVC
import numpy as np
import random

# 锁定运行环境，确保结果的可复现性
def seed_everything(seed=42):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed(seed)
    # DirectML 虽无特定 seed 接口，但锁定 numpy 和 torch 核心后会稳定很多
seed_everything(42)


# 设置 AMD 显卡设备
device = torch_directml.device()
print(f"正在使用设备: {device}")

# 假设你的 BinaryClassifier 已经定义或从 classes 导入
from classes import BinaryClassifier

# 加载数据
data = pd.read_csv('QG_train.csv')
X = data.drop('target', axis=1).values
y = data['target'].values

# 压缩列的特征
col_features = 5500
selector = SelectKBest(score_func=f_classif, k=col_features)
X_reduced = selector.fit_transform(X, y)

# 预处理
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X_reduced)
print(f"数据检查 - 是否有NaN: {np.isnan(X_scaled).any()}, 是否有Inf: {np.isinf(X_scaled).any()}")

# 有 101 个样本，PCA 维度不能只设为 4！
# 降到 30-50 维，这样才能保留足够的分类信息
print("正在进行 PCA 降维...")
n_components = min(X.shape[0] - 1, 80)  # PCA 维度不能超过样本数 - 1
X_pca_tensor, all_components = gpu_pca(X_scaled, n_components, device)
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
for epoch in range(80):
    optimizer.zero_grad()

    # 直接传入 X_pca_tensor，不需要再次搬运
    outputs = model(X_pca_tensor)

    loss = criterion(outputs, y_tensor)

    # L1 正则化 (GPU 加速版写法)
    l1_lambda = 0.005  # 这个值需要调试，过大可能会过度稀疏，过小可能效果不明显
    l1_loss = sum(torch.sum(torch.abs(p)) for p in model.parameters())
    loss = loss + l1_lambda * l1_loss

    loss.backward()
    optimizer.step()

print("训练完成！")

# 提取权重（需要先搬回 CPU 才能转 numpy）
weights = model.layer1.weight.detach().cpu().abs().numpy().mean(axis=0)

# 选出更多的成分，至少 10 个，才能让 SVM 有足够的信息进行分类

# 这里的值是是测试出来的最优解
top_k = min(40, n_components)
top_component_indices = weights.argsort()[-top_k:][::-1]
print(f"神经网络选出的核心主成分索引: {top_component_indices}")

# SVM 预测
# SVM 是在 CPU 上运行的，所以要先搬运

# 先把整个大张量搬回 CPU，转成 numpy
X_pca_all_cpu = X_pca_tensor.detach().cpu().numpy()
# 用.copy解决内存非连续报错
X_final_for_svm = X_pca_all_cpu[:, top_component_indices].copy()
print(f"SVM 输入特征形状: {X_final_for_svm.shape}")

"""
# 'rbf' 核通常比 'linear' 效果更好
final_svm = SVC(kernel='rbf', C=4)
final_svm.fit(X_final_for_svm, y)

print(f"SVM 在训练集上的预测结果前20个: {final_svm.predict(X_final_for_svm)[:20]}")
print(f"实际标签前20个: {y[:20]}")
print(f"总准确率: {final_svm.score(X_final_for_svm, y):.4f}")
"""

# 只对 RBF 进行精准打击调参
param_grid = {
    'C': [ 4, 8, 10, 15],  # 以你原来的 4 为中心向外扩
    'gamma': ['scale', 'auto', 0.01, 0.05]
}

print("🚀 在原有架构上进行 RBF 精准调参...")
grid_search = GridSearchCV(
    SVC(kernel='rbf'), # 锁死 RBF 核
    param_grid,
    cv=5,
    scoring='accuracy',
    n_jobs=-1
)

grid_search.fit(X_final_for_svm, y)
final_svm = grid_search.best_estimator_

print(f"最佳 RBF 参数: {grid_search.best_params_}")
print(f"训练集 CV 得分: {grid_search.best_score_:.4f}")


"""
# --- 自动化体检开始 ---
# 定义想要尝试的参数池
param_grid = {
    'C': [0.1, 1, 2, 4, 6, 10, 20, 50],         # 惩罚系数
    'gamma': ['scale', 'auto', 0.1, 0.01, 0.001], # RBF核的宽度
    'kernel': ['rbf', 'linear']                  # 顺便测一下线性核
}

print("🚀 开始全自动参数体检 (Grid Search)...")
# cv=5 表示五折交叉验证，n_jobs=-1 表示动用所有CPU核心
grid_search = GridSearchCV(
    SVC(),
    param_grid,
    cv=5,
    scoring='accuracy',
    verbose=1,
    n_jobs=-1
)

# 在神经网络筛选后的特征上进行搜索
grid_search.fit(X_final_for_svm, y)

print(f"✅ 最佳参数组合: {grid_search.best_params_}")
print(f"最佳交叉验证准确率 (CV Score): {grid_search.best_score_:.4f}")

# 将最终胜出的模型赋值给 final_svm
final_svm = grid_search.best_estimator_
# --- 自动化体检结束 ---
"""
"""
下面是测试程序
"""
# 加载数据
data = pd.read_csv('QG_test.csv')
X_test = data.drop('target', axis=1).values
y_test = data['target'].values

# 列特征选择器已经在训练集上 fit 了，所以直接 transform 就行了
X_test_reduced = selector.transform(X_test) # 注意，这里是transform，不是fit_transform，因为要用训练集的选择器

# 预处理
# scaler = StandardScaler() 这里不要重置
X_test_scaled = scaler.transform(X_test_reduced) # 注意，这里不是fit——transform，因为要用训练集的均值和方差
print(f"数据检查 - 是否有NaN: {np.isnan(X_test_scaled).any()}, 是否有Inf: {np.isinf(X_test_scaled).any()}")

# 转换张量数据，并搬运至显卡
X_test_tensor = torch.FloatTensor(X_test_scaled).to(device)
X_test_centered = X_test_tensor - X_test_tensor.mean(dim=0)
X_test_pca_tensor = torch.mm(X_test_centered, all_components.t())
# 将数据搬回 CPU，并切片
X_test_pca_cpu = X_test_pca_tensor.detach().cpu().numpy().copy()
X_test_final = X_test_pca_cpu[:, top_component_indices].copy()

# 预测
print(f"测试集输入特征形状: {X_test_final.shape}") # 应该是 (样本数, 30)
y_test_pred = final_svm.predict(X_test_final)

print(f"SVM 在测试集上的预测结果前20个: {y_test_pred[:20]}")
print(f"实际标签前20个: {y_test[:20]}")
print(f"测试集总准确率: {final_svm.score(X_test_final, y_test):.4f}")

