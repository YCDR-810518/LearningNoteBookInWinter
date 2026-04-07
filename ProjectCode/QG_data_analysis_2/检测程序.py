import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC

# 1. 加载数据
# 假设训练集和测试集文件名如下，请根据实际修改
train_path = 'QG_train.csv'
test_path = 'QG_test.csv' # 假设这是你带标签的真实测试集

df_train = pd.read_csv(train_path)
df_test = pd.read_csv(test_path)

X_train_raw = df_train.iloc[:, :-1]
y_train_raw = df_train.iloc[:, -1]
X_test_raw = df_test.iloc[:, :-1]
y_test_raw = df_test.iloc[:, -1]

# 2. 识别【矛盾样本】 (相关性 > 0.95 且标签相反)
print("正在识别矛盾样本...")
corr_matrix = X_train_raw.T.corr()
upper_tri = corr_matrix.where(np.triu(np.ones(corr_matrix.shape), k=1).astype(bool))

conflict_indices = set()
for i in upper_tri.columns:
    for j in upper_tri.index:
        if upper_tri.loc[j, i] > 0.95 and y_train_raw[i] != y_train_raw[j]:
            conflict_indices.add(i)
            conflict_indices.add(j)
print(f"已锁定矛盾样本 {len(conflict_indices)} 个: {list(conflict_indices)}")

# 3. 识别【孤立样本】 (平均相关度最低的前 20 个)
print("正在识别孤立样本...")
# 注意：这里计算的是除去矛盾样本后的剩余样本的孤立程度
remaining_after_conflict = df_train.drop(index=list(conflict_indices))
row_mean_corr = corr_matrix.drop(index=list(conflict_indices), columns=list(conflict_indices)).mean()
isolated_indices = row_mean_corr.sort_values().head(10).index.tolist()
print(f"已锁定最孤立的 10 个样本: {isolated_indices}")

# 4. 执行双重提纯
final_drop_list = list(conflict_indices.union(set(isolated_indices)))
df_ultra_clean = df_train.drop(index=final_drop_list).reset_index(drop=True)
X_ultra = df_ultra_clean.iloc[:, :-1]
y_ultra = df_ultra_clean.iloc[:, -1]

print(f"\n提纯完毕！原始样本: {len(df_train)} -> 最终训练样本: {len(df_ultra_clean)}")

# 5. 预处理与训练
# 过滤掉常数项特征（全 0 或相同值的列），防止除零错误
variance_mask = X_ultra.var() > 0
X_ultra_filtered = X_ultra.loc[:, variance_mask]
X_test_filtered = X_test_raw.loc[:, variance_mask]

print(f"特征数已从 {X_train_raw.shape[1]} 自动清理常数列至 {X_ultra_filtered.shape[1]}")

# 这里我们直接从 X_ultra_filtered 开始
X = X_ultra_filtered
y = y_ultra

# 2. 初步筛选 Top 500 (降低计算复杂度)
from sklearn.feature_selection import SelectKBest, f_classif
selector = SelectKBest(score_func=f_classif, k=min(8000, X.shape[1]))
X_selected = selector.fit_transform(X, y)
selected_names = X.columns[selector.get_support()]
df_top = pd.DataFrame(X_selected, columns=selected_names)

# 3. 【核心步骤】特征间去重
print(f"正在分析 {df_top.shape[1]} 个核心特征的内耗情况...")
corr_feat = df_top.corr().abs()
upper = corr_feat.where(np.triu(np.ones(corr_feat.shape), k=1).astype(bool))

# 找出相关性大于 0.9 的特征列
to_drop_feat = [column for column in upper.columns if any(upper[column] > 0.95)]

X_final_train = df_top.drop(columns=to_drop_feat)
X_final_test = X_test_filtered[X_final_train.columns] # 测试集同步对齐

print(f"检测到高度内耗特征: {len(to_drop_feat)} 个，已剔除。")
print(f"最终用于实战的精炼特征数: {X_final_train.shape[1]}")

# 4. 预测与评估 (配合微调 C 参数)
# 既然特征精简了，我们可以把 C 调得稍微大一点，让模型更“果断”
scaler = StandardScaler()
X_train_std = scaler.fit_transform(X_final_train)
X_test_std = scaler.transform(X_final_test)

best_c = 1.0
model = SVC(kernel='linear', C=best_c, random_state=42)
model.fit(X_train_std, y_ultra)

acc = model.score(X_test_std, y_test_raw)
print("\n" + "="*30)
print(f"【去冗余版】最终测试集准确率: {acc:.4f}")
print("="*30)