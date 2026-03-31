import pandas as pd
import numpy as np
from classes import KMeans, MultiSVM, confusion_matrix, accuracy

def main():
    """
    主程序：加载数据、训练模型、评估性能、生成报告
    """
    # 加载鸢尾花数据集
    url = "https://archive.ics.uci.edu/ml/machine-learning-databases/iris/iris.data"
    columns = ['sepal_length', 'sepal_width', 'petal_length', 'petal_width', 'species']
    df = pd.read_csv(url, header=None, names=columns)
    
    # 映射物种到数字标签
    species_map = {'Iris-setosa': 0, 'Iris-versicolor': 1, 'Iris-virginica': 2}
    df['species'] = df['species'].map(species_map)
    
    X = df.iloc[:, :-1].values  # 特征
    y = df['species'].values    # 标签
    
    # 数据标准化
    X = (X - X.mean(axis=0)) / X.std(axis=0)
    
    print("数据加载完成。数据集大小：", X.shape)
    
    # K-Means 聚类
    print("\n开始 K-Means 聚类...")
    kmeans = KMeans(k=3)
    kmeans.fit(X)
    kmeans_purity = kmeans.evaluate(X, y)
    print(f"K-Means 聚类纯度: {kmeans_purity:.4f}")
    
    # SVM 分类
    print("\n开始 SVM 分类...")
    svm = MultiSVM()
    svm.fit(X, y)
    y_pred_svm = svm.predict(X)
    cm, classes = confusion_matrix(y, y_pred_svm)
    svm_accuracy = accuracy(cm)
    print(f"SVM 分类准确率: {svm_accuracy:.4f}")
    print("混淆矩阵:")
    print(cm)
    
    # 生成报告
    print("\n生成详细报告...")
    generate_report(kmeans_purity, svm_accuracy, cm)
    print("报告已生成：report.md")

def generate_report(kmeans_purity, svm_accuracy, cm):
    """
    生成 Markdown 格式的中文报告
    """
    with open('report.md', 'w', encoding='utf-8') as f:
        f.write("# K-Means 聚类与 SVM 分类模型对比报告\n\n")
        
        f.write("## SVM 算法原理\n\n")
        f.write("支持向量机 (SVM) 是一种监督学习算法，用于分类和回归任务。它通过找到一个超平面来最大化类别之间的间隔，从而实现分类。\n\n")
        
        f.write("### 基本原理\n\n")
        f.write("对于二分类问题，SVM 试图找到一个超平面 w·x + b = 0，使得正类和负类的间隔最大化。间隔定义为 2 / ||w||。\n\n")
        f.write("优化目标是：\n\n")
        f.write("min 1/2 ||w||^2 + C Σ max(0, 1 - y_i (w·x_i + b))\n\n")
        f.write("其中 C 是正则化参数，控制间隔和错误分类的权衡。\n\n")
        
        f.write("### 核技巧\n\n")
        f.write("通过核函数，可以将数据映射到更高维空间，实现非线性分类。本实现使用线性核。\n\n")
        
        f.write("### 优化算法\n\n")
        f.write("使用梯度下降优化上述目标函数。\n\n")
        
        f.write("### 适用场景\n\n")
        f.write("SVM 适用于高维数据、小样本数据、非线性问题。优点：泛化能力强，鲁棒性好。缺点：计算复杂度高，不适合大规模数据。\n\n")
        
        f.write("## 模型对比\n\n")
        f.write("### K-Means vs SVM\n\n")
        f.write("- **监督 vs 无监督**：K-Means 是无监督聚类，SVM 是监督分类。\n")
        f.write("- **适用场景**：K-Means 用于探索性数据分析，SVM 用于预测。\n")
        f.write("- **优缺点**：K-Means 简单快速，但对初始值敏感；SVM 准确但计算慢。\n")
        f.write("- **在本数据集上的表现**：K-Means 纯度 {:.4f}，SVM 准确率 {:.4f}。\n\n".format(kmeans_purity, svm_accuracy))
        
        f.write("### 评估结果\n\n")
        f.write("K-Means 聚类纯度: {:.4f}\n\n".format(kmeans_purity))
        f.write("SVM 分类准确率: {:.4f}\n\n".format(svm_accuracy))
        f.write("SVM 混淆矩阵:\n\n")
        f.write("```\n")
        f.write(str(cm))
        f.write("\n```\n\n")
        
        f.write("## 鸢尾花数据集特点\n\n")
        f.write("- **特征相关性**：花瓣长度和宽度高度相关，萼片相关性较低。\n")
        f.write("- **类别可分性**：山鸢尾与其他两类线性可分，变色鸢尾和维吉尼亚鸢尾有重叠。\n")
        f.write("- **数据分布**：150 个样本，4 个特征，3 个类别。\n")

if __name__ == "__main__":
    main()
