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
rating_time_genre_clean = rating_time_genre.dropna()
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
from

print('数据清洗完毕！！')


# 进行数据预处理{搞出有效的数据集}
# 首先按年份进行排序


# 分出来80%用来训练，20%用来测试
print()
print('接下来是训练时间')

