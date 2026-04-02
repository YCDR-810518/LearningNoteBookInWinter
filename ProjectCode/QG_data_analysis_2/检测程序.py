import pandas as pd
import torch
import torch_directml
from classes import gpu_pca

device = torch_directml.device()


# 加载数据
data = pd.read_csv('QG_train.csv')
X = data.drop('target', axis=1).values
y = data['target'].values



# 执行降维
n_k = 100
X_pca_gpu = gpu_pca(X, n_k, device)

print(f"GPU PCA 完成！输出形状: {X_pca_gpu.shape}")
