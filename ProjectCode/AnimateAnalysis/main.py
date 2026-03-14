# 这是一个示例 Python 脚本。
from pyexpat import features

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
print('接下来是分级和时间之间的表')
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
# 划分训练集&测试集
train_data = final_data[final_data['year'] <= split_year]
test_data = final_data[final_data['year'] > split_year]

# 区分特征与训练的目标

# 放入年与种类作为特征向量X
feature_col = ['year'] + list(mlb.classes_)

# 放入

# 分出来80%用来训练，20%用来测试
print()
print('接下来是训练时间')

