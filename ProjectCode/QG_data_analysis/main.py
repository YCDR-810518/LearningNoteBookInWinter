import classes
import pandas as pd


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

    # 成功去除无用值
    # 接下来进行模型训练

