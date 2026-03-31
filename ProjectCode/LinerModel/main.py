import classes as cl

# 数据处理
processor = cl.DataProcessor()
df = processor.load_data('winequalityN.csv')
df = processor.preprocess(df)

# 划分训练和测试集
train_size = int(0.8 * len(df))
train_df = df[:train_size]
test_df = df[train_size:]

X_train = train_df.drop('quality', axis=1).values
y_train_linear = train_df['quality'].values
y_train_logistic = (train_df['quality'] > 6).astype(int).values

X_test = test_df.drop('quality', axis=1).values
y_test_linear = test_df['quality'].values
y_test_logistic = (test_df['quality'] > 6).astype(int).values

# 线性回归
linear = cl.LinearRegression()
linear.fit(X_train, y_train_linear)
y_pred_linear = linear.predict(X_test)
mse_val = cl.mse(y_test_linear, y_pred_linear)
print(f"线性回归MSE: {mse_val}")

# 逻辑回归
logistic = cl.LogisticRegression()
logistic.fit(X_train, y_train_logistic)
y_pred_logistic = logistic.predict(X_test)
acc = cl.accuracy(y_test_logistic, y_pred_logistic)
print(f"逻辑回归准确率: {acc}")

# 模型比较
print("模型比较: 线性回归用于回归预测质量评分，逻辑回归用于二分类好坏酒。线性回归MSE较低表示预测准确，逻辑回归准确率高表示分类效果好。")

