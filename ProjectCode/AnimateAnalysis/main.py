# 这是一个示例 Python 脚本。

# 按 ⌃R 执行或将其替换为您的代码。
# 按 双击 ⇧ 在所有地方搜索类、文件、工具窗口、操作和设置。

import pandas as pd

animateList_original = pd.read_csv('top_anime_dataset.csv')
animateList = pd.DataFrame(animateList_original)
animateList.info()
print(animateList.head(10))
print(animateList.describe())

# 从中抽出年龄分级和时间，并进行清洗
print()
print('接下来是分级,种类和时间之间的表')
print('展示的时间范围是1970-2026')
rating_time_genre = animateList[['rating','year','genres']].copy()
rating_time_genre.info()
print(rating_time_genre.head(5))
print(rating_time_genre.describe())
print(rating_time_genre[['year']])

# 观察到year存在缺失值，进行清洗
# 展示缺失的数量
print('年份存在缺失的行数为：')
print(rating_time_genre['year'].isna().sum())
print('种类存在缺失的行数为：')
print(rating_time_genre['genres'].isna().sum())

# 仅仅删去存在缺失的行
rating_time_genre_clean = rating_time_genre.dropna().copy()
print(rating_time_genre_clean.info())
print(rating_time_genre_clean.head(5))
print()

# 接下来将object(genres和rating中的数据)转为数值
# 查看rating中分级的种类
# 查看种类时加上normalize=True可以顺便查看占比
rating_counts = rating_time_genre_clean['rating'].value_counts(normalize=True)
print('年龄分级的种类及占比')
print(rating_counts)
print()

# 切分genres中的所有题材

# 切分一行中的元素为列表
from sklearn.preprocessing import MultiLabelBinarizer
rating_time_genre_clean.loc[:, 'genres_list'] = rating_time_genre_clean['genres'].str.split(', ').copy()

# 初始化工具
mlb = MultiLabelBinarizer()

# 执行转换
# fit_transform 会先学习所有题材种类，然后直接转换成 0/1 矩阵
genre_matrix = mlb.fit_transform(rating_time_genre_clean['genres_list'])

# 转换回DF
genres_df = pd.DataFrame(genre_matrix, columns=mlb.classes_, index=rating_time_genre_clean.index)

# 合并回原始数据（删除原来的字符串列，保留编码后的列）
rating_time_genre_clean_2 = pd.concat([rating_time_genre_clean[['year', 'rating']], genres_df], axis=1)
print(rating_time_genre_clean_2.head(5))

# 对rating进行编码
from sklearn.preprocessing import LabelEncoder
# from sklearn.model_selection import train_test_split

# 对 rating 进行编码
le = LabelEncoder()
rating_time_genre_clean_2['rating_encoded'] = le.fit_transform(rating_time_genre_clean_2['rating'])
print(rating_time_genre_clean_2.head(5))

# 按照年份进行重排（升序）
final_data = rating_time_genre_clean_2.sort_values(by='year', ascending=True)
print(final_data.head(10))
print('数据清洗完毕！！')

# 进行数据预处理{搞出有效的数据集}

# 首先按年份进行排序
# 确定划分的年份
split_year = 2015
final_data = final_data.drop('rating', axis=1).copy()
print('剔除了str的rating数据')
print(final_data.head(10))
train_data = final_data[final_data['year'] <= split_year]
test_data = final_data[final_data['year'] > split_year]

# 切分并转换数据类型
# 提取特征列
train_data_features = train_data.drop('rating_encoded',axis=1).copy().values
test_data_features = test_data.drop('rating_encoded',axis=1).copy().values
# 提取目标列
train_data_labels = train_data.pop('rating_encoded').copy().values
test_data_labels = test_data.pop('rating_encoded').copy().values

import torch
import numpy as np

# 构造序列（分别对训练和测试集操作）
def create_sequences(features, labels, seq_length=3):
    xs, ys = [], []
    for i in range(len(features) - seq_length):
        xs.append(features[i:(i + seq_length)])
        ys.append(labels[i + seq_length]) # 这里抓的是标签
    return torch.FloatTensor(np.array(xs)), torch.LongTensor(np.array(ys))

# 转换
X_train, y_train = create_sequences(train_data_features, train_data_labels)
X_test, y_test = create_sequences(test_data_features, test_data_labels)


print('模型初始化中....')
# 模型初始化准备
import torch.nn as nn
import torch.optim as optim

# 定义我们之前讨论过的 LSTM 序列模型结构
class AnimeTrendLSTM(nn.Module):
    def __init__(self, input_dim, hidden_dim, output_dim):
        super(AnimeTrendLSTM, self).__init__()
        # batch_first=True 表示输入数据的维度是 [batch_size, seq_len, features]
        self.lstm = nn.LSTM(input_dim, hidden_dim, batch_first=True)
        self.fc = nn.Linear(hidden_dim, output_dim)

    def forward(self, x):
        lstm_out, _ = self.lstm(x)
        # 我们只需要序列最后一个时间步的输出去预测 rating
        return self.fc(lstm_out[:, -1, :])


# 获取正确的输入和输出维度
# X_train 的形状应该是 [样本数, 序列长度, 特征数]，所以 shape[2] 是特征维度
input_dimension = X_train.shape[2]
# output_dimension 是 rating 的总类别数 (比如 G, PG, PG-13, R 等有几个)
output_dimension = len(np.unique(train_data_labels))

# 实例化 model
model = AnimeTrendLSTM(input_dim=input_dimension, hidden_dim=64, output_dim=output_dimension)

# 实例化 criterion (损失函数)
# CrossEntropyLoss 是处理多分类问题（如预测评级类别）的绝对标准
criterion = nn.CrossEntropyLoss()

# 实例化 optimizer (优化器)
# Adam 优化器负责根据 Loss 来更新模型内部的权重参数
optimizer = optim.Adam(model.parameters(), lr=0.01)



# 准备开始训练
# 构建 DataLoader (序列训练的核心)
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset
import numpy as np

train_dataset = TensorDataset(X_train, y_train)
test_dataset = TensorDataset(X_test, y_test)

train_loader = DataLoader(train_dataset, batch_size=32, shuffle=True)
test_loader = DataLoader(test_dataset, batch_size=32, shuffle=False)

# 正式开始训练
model.train()
for epoch in range(100):
    total_loss = 0
    for batch_x, batch_y in train_loader:
        optimizer.zero_grad()
        output = model(batch_x)
        loss = criterion(output, batch_y)
        loss.backward()
        optimizer.step()
        total_loss += loss.item()

    # 每 20 个 epoch 看看测试集表现，这就是寻找“反常”的时间点
    if (epoch + 1) % 20 == 0:
        model.eval()
        with torch.no_grad():
            test_output = model(X_test)
            test_loss = criterion(test_output, y_test)
        print(f"Epoch {epoch + 1}, Train Loss: {total_loss / len(train_loader):.4f}, Test Loss: {test_loss:.4f}")

        model.eval()
        with torch.no_grad():
            # 获取模型的预测结果（原始分数）
            predictions = model(X_test)

            # 将概率分数转化为分类标签 (取最大概率所在的索引)
            _, predicted_labels = torch.max(predictions, 1)

            # 计算预测正确的个数
            correct = (predicted_labels == y_test).sum().item()
            total = y_test.size(0)

            # 输出统计数据
            accuracy = 100 * correct / total
            print(f"测试集共 {total} 条数据，模型预测准确率为: {accuracy:.2f}%")

            # 纠着不放：看看哪些预测错了（定位“反常”的关键点）
            mismatches = torch.where(predicted_labels != y_test)[0]
            print(f"模型在 {len(mismatches)} 个样本上出现了判断失误。")

            # 观察前 3 个预测错误的案例
            for idx in mismatches[:3]:
                print(f"--- 反常样本分析 ---")
                print(f"真实标签: {le.inverse_transform([y_test[idx].item()])[0]}")
                print(f"模型预测: {le.inverse_transform([predicted_labels[idx].item()])[0]}")
                print(f"该样本的年份与题材: {X_test[idx].flatten()}")

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

# 将预测值和真实值整理到 DataFrame 中方便绘图
results_df = pd.DataFrame({
    'Real': le.inverse_transform(y_test.numpy()),
    'Predicted': le.inverse_transform(predicted_labels.numpy())
})

# 绘制交叉对比柱状图
plt.figure(figsize=(10, 6))
sns.countplot(data=results_df, x='Real', hue='Predicted')
plt.title("Distribution of Real vs Predicted Ratings")
plt.xlabel("Rating Level")
plt.ylabel("Count")
plt.legend(title="Predicted", bbox_to_anchor=(1.05, 1), loc='upper left')
plt.show()

# 将数据加回原始年份信息（假设你保存了 test_data 的年份）
# 假设 test_data_features 第一列是年份
seq_length = 3
years = test_data_features[seq_length:, 0]

results_df = pd.DataFrame({
    'Real': le.inverse_transform(y_test.numpy()),
    'Predicted': le.inverse_transform(predicted_labels.numpy())
})

results_df['Year'] = years # 现在长度都是 58，可以完美对齐了

# 计算每年的准确率
accuracy_by_year = results_df.groupby('Year').apply(lambda x: (x['Real'] == x['Predicted']).mean())

plt.figure(figsize=(10, 5))
accuracy_by_year.plot(kind='line', marker='o', color='red')
plt.title("Model Accuracy Trend by Year")
plt.xlabel("Year")
plt.ylabel("Accuracy")
plt.grid(True)
plt.show()

import seaborn as sns
import matplotlib.pyplot as plt

# 1. 提取所有题材列的名称（排除年份和编码列）
# 假设你的 final_data 中除了 'year' 和 'rating_encoded'，其余全是题材列
genre_columns = [col for col in final_data.columns if col not in ['year', 'rating_encoded']]

# 2. 按年份分组并求和，得到每年各题材的作品数量
genre_trends = final_data.groupby('year')[genre_columns].sum()

# 3. 【纠着不放的细节】如果题材太多，图表会失去可读性
# 我们计算每个题材的总作品数，并只取前 10 名
top_10_genres = genre_trends.sum().sort_values(ascending=False).head(5).index
plot_data = genre_trends[top_10_genres]

# 4. 开始绘图
plt.figure(figsize=(14, 8))

# 使用 Seaborn 绘制折线图
# plot_data 的 index 是年份(x轴)，columns 是题材(颜色区分)，values 是数量(y轴)
sns.lineplot(data=plot_data, linewidth=2, dashes=False)

# 优化图表展示
plt.title("Evolution of Top 10 Anime Genres (1970-2026)", fontsize=15)
plt.xlabel("Year", fontsize=12)
plt.ylabel("Number of Releases", fontsize=12)
plt.legend(title="Genres", bbox_to_anchor=(1.05, 1), loc='upper left') # 标签放在图外防止遮挡
plt.grid(True, which='both', linestyle='--', alpha=0.5)
plt.tight_layout()

plt.show()