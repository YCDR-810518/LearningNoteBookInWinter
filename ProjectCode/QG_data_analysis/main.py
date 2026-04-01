import classes
import pandas as pd


with open('QG_train.csv', 'r', encoding='utf-8') as f:
    data = pd.read_csv(f)
    print(data.head())
    print(data.describe())

    # 数据预处理
    # 提取特征值
    data_feature =
    # 提取标签值
    data_label = data['target'].copy()
    print(data_feature.head())
    print(data_label.head())

