### 一、 指标与公式拆解

#### 1. Figure 4: 相对误差 vs. 隐私预算 (ϵ)

- **目标**：证明在不同的隐私预算下，你们的算法依然能保持较低的查询误差。
- **变量设置**：固定树高（例如 H=10 或根据前文得出的最佳高度），遍历不同的隐私预算 ϵ∈{0.1,0.5,1.0,1.5,2.0}。
- **数学解释**：相对误差（Relative Error, RE）公式你们已经实现（定义 2）。这里主要观察随着 ϵ 的增加（加噪减少），各算法的 RE 曲线如何衰减。

#### 2. Figure 5: Top-K 频繁路径挖掘的 F-Score 效用

- **目标**：评估加噪后的数据是否保留了原始轨迹中的“骨干流量”（即最热门的出行路线）。

- **变量设置**：固定树高 H 和 ϵ（例如 ϵ=1.0），遍历不同的 K 值（如 K∈{10,20,30,40,50}）。

- **数学解释**：提取原数据和加噪数据中客流量排名前 K 的路径集合。由于原集合和预测集合大小均为 K，精准率（Precision）和召回率（Recall）在此场景下是相等的：

  <img src="https://raw.githubusercontent.com/YCDR-810518/imageBed/main/picGo/截屏2026-04-13 20.21.10.png" alt="截屏2026-04-13 20.21.10" style="zoom:50%;" />

  因此 F-Score 公式简化为：

  <img src="https://raw.githubusercontent.com/YCDR-810518/imageBed/main/picGo/截屏2026-04-13 20.20.58.png" alt="截屏2026-04-13 20.20.58" style="zoom:50%;" />

#### 3. Figure 6: 轨迹分布差异 JSD vs. 隐私预算 (ϵ)

- **目标**：测量原始数据分布与加噪后数据分布的整体相似度。JSD（Jensen-Shannon Divergence）越小，说明数据分布保留得越好。

- **变量设置**：固定树高 H，遍历不同的 ϵ。

- **数学解释**：设 P 为原路径概率分布，Q 为加噪后的路径概率分布，$M=1/2(P+Q)$。基于 KL 散度（Kullback-Leibler Divergence），JSD 定义为：

  <img src="https://raw.githubusercontent.com/YCDR-810518/imageBed/main/picGo/截屏2026-04-13 20.22.34.png" alt="截屏2026-04-13 20.22.34" style="zoom:50%;" />

#### 4. Figure 7: 相对误差 vs. 路径长度 (∣Q∣)

- **目标**：由于前缀树深层节点的预算分配是个难题，此图用于证明你们的算法在处理长路径（长途地铁出行）时，误差也不会爆炸。
- **变量设置**：固定 ϵ 和树高 H，将测试集中的路径按长度（经过的站点数）进行分组，计算每组的平均相对误差。

------

### 二、 代码落地：补充评估函数

首先，你需要在 `utils.py` 中补充计算 F-Score 和 JSD 的基础函数。请在里面加入以下代码：

Python

```python
import numpy as np
from scipy.stats import entropy

def get_top_k_paths(results, k):
    """提取 Top-K 路径集合"""
    sorted_res = sorted(results, key=lambda x: x['count'], reverse=True)
    return set([item['path'] for item in sorted_res[:k]])

def calculate_f_score(original_results, sanitized_results, k):
    """计算 Top-K 的 F-Score"""
    if k == 0: return 0.0
    real_top_k = get_top_k_paths(original_results, k)
    noisy_top_k = get_top_k_paths(sanitized_results, k)
    
    intersection = len(real_top_k.intersection(noisy_top_k))
    return intersection / k

def calculate_jsd(original_results, sanitized_results):
    """计算 Jensen-Shannon Divergence (JSD)"""
    raw_dict = {item['path']: item['count'] for item in original_results if item['count'] > 0}
    san_dict = {item['path']: item['count'] for item in sanitized_results if item['count'] > 0}
    
    all_paths = list(set(raw_dict.keys()) | set(san_dict.keys()))
    
    # 转换为频率分布
    P = np.array([raw_dict.get(p, 0.0) for p in all_paths])
    Q = np.array([san_dict.get(p, 0.0) for p in all_paths])
    
    sum_P = np.sum(P)
    sum_Q = np.sum(Q)
    
    if sum_P == 0 or sum_Q == 0:
        return 1.0 # 极端异常情况
        
    P = P / sum_P
    Q = Q / sum_Q
    
    M = 0.5 * (P + Q)
    
    # 使用 scipy.stats.entropy 计算 KL 散度
    jsd = 0.5 * entropy(P, M) + 0.5 * entropy(Q, M)
    return jsd
```

------

### 三、 执行步骤：在 `main.py` 中编排实验主循环

在 `main.py` 中，你需要设立一个新的实验编排逻辑。为了避免单次执行跑太久，建议把 Figure 4、5、6、7 的测试包裹在独立的函数里，你可以参考这种结构：

Python

```python
import matplotlib.pyplot as plt
# 记得从 utils 引入刚写的函数
from utils import calculate_f_score, calculate_jsd 

def run_extended_experiments(unique_trips, total_flow):
    EPSILONS = [0.1, 0.5, 1.0, 1.5, 2.0]
    K_VALUES = [10, 20, 30, 40, 50]
    FIXED_HEIGHT = 15 # 假设基于 Figure 3 选定的最佳树高
    FIXED_EPSILON = 1.0
    
    models = {
        "Our Algorithm": LagrangianTrie,
        "SeqPT": SeqPTTrie,         # 根据你实际的类名替换
        "SafePath": SafePathTrie    # 根据你实际的类名替换
    }
    
    # 初始化记录器
    err_vs_eps = {name: [] for name in models.keys()}
    jsd_vs_eps = {name: [] for name in models.keys()}
    fscore_vs_k = {name: [] for name in models.keys()}
    
    # ---------------------------------------------------------
    # 实验 A: 遍历 Epsilon (对应 Figure 4 和 Figure 6)
    # ---------------------------------------------------------
    print("开始测试不同 Epsilon 下的表现...")
    # 预先建立未加噪的原树作为 Baseline
    raw_trie = TrajectoryTrie(max_height=FIXED_HEIGHT, total_trajectories=total_flow)
    # (此处省略：将 unique_trips 插入 raw_trie 的代码，参考你现有的逻辑)
    raw_results = raw_trie.get_raw_data(only_leaves=False)
    
    for eps in EPSILONS:
        print(f"  当前 Epsilon: {eps}")
        for name, ModelClass in models.items():
            trie = ModelClass(max_height=FIXED_HEIGHT, total_trajectories=total_flow)
            # 插入数据...
            
            trie.allocate_budget(total_epsilon=eps)
            trie.add_noise()
            sanitized_results = trie.get_sanitized_data(only_leaves=False)
            
            # 计算 Figure 4: Relative Error
            errors = calculate_relative_error(raw_trie, sanitized_results, total_flow)
            err_vs_eps[name].append(np.nanmean(errors))
            
            # 计算 Figure 6: JSD
            jsd = calculate_jsd(raw_results, sanitized_results)
            jsd_vs_eps[name].append(jsd)
            
    # ---------------------------------------------------------
    # 实验 B: 遍历 K 值测试 F-Score (对应 Figure 5)
    # ---------------------------------------------------------
    print("\n开始测试 Top-K F-Score...")
    # 使用固定的 FIXED_EPSILON 重新加噪一组数据
    sanitized_caches = {}
    for name, ModelClass in models.items():
        trie = ModelClass(max_height=FIXED_HEIGHT, total_trajectories=total_flow)
        # 插入数据...
        trie.allocate_budget(total_epsilon=FIXED_EPSILON)
        trie.add_noise()
        sanitized_caches[name] = trie.get_sanitized_data(only_leaves=False)
        
    for k in K_VALUES:
        for name in models.keys():
            f_score = calculate_f_score(raw_results, sanitized_caches[name], k)
            fscore_vs_k[name].append(f_score)
            
    # 最后，调用你的 plot_results 画出这三张图即可
    # 可以通过改造 plot_results 函数，传入不同的 x_axis 和 ylabel 进行画图
```

### 四、 下一步建议

1. 先把基础数据跑出来，以 `print` 打印确认逻辑无误，尤其是 JSD 的值域通常在 `[0, 1]` 之间，越低说明分布越接近；F-score 同理。
2. 数据就绪后，再集中用 `matplotlib` 处理画图逻辑，统一你的 Marker、线宽和颜色（沿用你们代码里设定的红色菱形 `D` 代表你们的模型）。

逻辑梳理完毕，你可以先尝试把 `utils.py` 的指标算子加进去测一测，有问题随时交流。