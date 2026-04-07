# PCA-主成分分析

（Principal Component Analysis）

## 核心目标

通过**基向量变换**，将高维数据映射到低维空间，同时尽可能保留原始数据中的特征（即方差）

* 如果我们把数据投影到一个方向上，数据点越分散（方差越大），说明这个方向越能代表原始数据的特征。

* 如果我们把数据投影到一个方差极小的方向上，所有点都挤在一起，我们就失去了区分这些数据的能力。

即：**PCA就是在寻找一个投影方向，使得投影后的数据方差最大**

## 来源

在电子工程或声学中，信号的**能量**通常正比于其**振幅的平方**，正好对应数学上的**方差**

* 信号->有意义，那么它的**能量**必然要**足够强**，才能被设备**捕获**或被人类**感知**。

* 噪声（如底噪、热噪声）通常是**随机的、高频的微弱震荡**。（高斯噪声）

> 所以，这里存在一个前提
>
> * 噪声的能量是**随机**且是**远远小于**信号的

### 数学本质

**信噪比（Signal-to-Noise Ratio, SNR）**

<img src="https://raw.githubusercontent.com/YCDR-810518/imageBed/main/picGo/截屏2026-04-04 16.47.51.png" alt="截屏2026-04-04 16.47.51" style="zoom:50%;" />

其中 $σ2$ 就是方差。

- 如果一个维度的方差非常大，说明在这个维度上，信号的强度远超噪声，我们可以确信这个维度是有用的。
- 如果一个维度的方差非常小，信号几乎被淹没在噪声里，那么保留这个维度对我们理解数据没有太大帮助

### 失效情况

**量纲问题：** 如果你的特征 A 是“人的年收入（几万到几十万）”，特征 B 是“人的身高（1.5 到 1.9 米）”。年收入的方差远大于身高。PCA 会倾向于认为年收入是唯一的主成分，而忽略身高。但身高可能是预测某些疾病的关键。

- *对策：* 必须先做**标准化（Standardization）**。

**小方差信号：** 有时候，最重要的信号恰恰隐藏在微小的波动中。例如，在精密仪器监测中，正常运行的数据方差可能很大，而代表“设备故障”的微弱脉冲信号方差却很小。

- *局限：* 这种情况下，PCA 可能会误把关键信号当成噪声剔除（此时**不能使用PCA**）

## 算法的具体实现逻辑

### 标准化（由于x-miu的存在，已经同时完成了去中心化的步骤）

目的：减小方差受到的**数值量级**影响

方法：将每个特征都转换成均值为 0、方差为 1 的**标准分布**



<img src="https://raw.githubusercontent.com/YCDR-810518/imageBed/main/picGo/截屏2026-04-04 18.23.55.png" alt="截屏2026-04-04 18.23.55" style="zoom:50%;" />

代码：`sklearn.preprocessing.StandardScaler`

### 计算协方差矩阵 (Covariance Matrix)

目的：展现不同维度之间的相关性

<img src="https://raw.githubusercontent.com/YCDR-810518/imageBed/main/picGo/截屏2026-04-04 18.29.49.png" alt="截屏2026-04-04 18.29.49" style="zoom:50%;" />

**特征：**

* Σ 是一个 d×d 的实对称矩阵。

* 对角线上的元素表示每个维度的方差。

* 非对角线元素表示维度间的相关性。

### 特征值分解 (Eigen-decomposition)

对协方差矩阵 Σ 进行特征分解，求解特征值 λ 和特征向量 v：

<img src="https://raw.githubusercontent.com/YCDR-810518/imageBed/main/picGo/截屏2026-04-04 18.38.24.png" alt="截屏2026-04-04 18.38.24" style="zoom:50%;" />

- **特征向量 v**：代表了数据分布的新基准方向（主成分方向）。
- **特征值 λ**：代表了数据在该方向上的方差大小。

### 选择主成分

将特征值从大到小排序，选择前 **k 个最大的特征值**对应的特征向量 {v1,v2,…,vk}。这些向量构成了变换矩阵 W∈Rd×k

### 投影到新空间

用变换矩阵将原始数据**投影到低维空间**：
$$
Y= Z⋅W
$$
此时，Y 是一个 n×k (nxn · nxk) 的矩阵，达到了降维的目的



### 纯Numpy实现代码

```python
import numpy
def pca_implementation(X, k):
    # 计算均值&方差
    mean = np.mean(X, axis=0)
    std = np.std(X, axis=0)
    # 标准化
    X_standardized = (X - mean) / std
    
    # 计算协方差矩阵
    # rowvar=False 表示每一列代表一个特征
    cov_mat = np.cov(X_standardized, rowvar=False)
    
    # 计算特征值和特征向量
    eigen_values, eigen_vectors = np.linalg.eigh(cov_mat)
    
    # 对特征值进行排序（从大到小）
    sorted_index = np.argsort(eigen_values)[::-1]
    sorted_eigenvectors = eigen_vectors[:, sorted_index]
    
    # 选择前 k 个
    eigenvector_subset = sorted_eigenvectors[:, 0:k]
    
    # 转换数据
    X_reduced = np.dot(X_standardized, eigenvector_subset)
    
    return X_reduced
```

## 总结

| **核心概念** | **说明**                                                     |
| ------------ | ------------------------------------------------------------ |
| **降维本质** | 寻找数据分布方差最大的相互正交的方向。                       |
| **信息损失** | 舍弃特征值较小的维度，认为这些维度包含的是噪声或次要信息。   |
| **前提条件** | PCA 是一种**线性**降维，如果数据具有复杂的流形结构（如 S 曲线），效果可能不如 t-SNE 或 UMAP。 |
| **解释性**   | 降维后的新特征（主成分）是原始特征的线性组合，往往失去明确的物理含义。 |
