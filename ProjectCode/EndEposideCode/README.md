# 差分隐私交通轨迹数据发布项目

## 项目概述

本项目研究基于拉格朗日松弛法的差分隐私隐私预算优化分配方法，针对深圳地铁轨迹数据，在保护用户隐私的前提下，通过科学的预算分配策略最大化数据查询效用。

**核心创新**：采用查询概率建模与拉格朗日优化方法，相比传统经验式分配算法（SeqPT、SafePath、Li's Algorithm），在相同隐私预算下获得显著更低的数据误差。

---

## 项目初始化与运行

### 环境配置

#### 方式一：使用 Conda（推荐）

```bash
cd /Users/yaochen/Documents/GitHub/LearningNoteBookInWinter/ProjectCode/EndEposideCode
conda env create -f environment.yml
conda activate endepodeidecode
```

#### 方式二：手动安装依赖

若 environment.yml 出现编码问题，可手动安装核心依赖：

```bash
python3 -m venv venv
source venv/bin/activate
pip install pandas numpy scipy scikit-learn matplotlib networkx tqdm altair
```

### 核心依赖

| 包名       | 版本   | 用途                     |
| ---------- | ------ | ------------------------ |
| pandas     | 3.0.2  | 数据处理与 OD 对统计     |
| numpy      | 2.4.4  | 数值计算与噪声生成       |
| scipy      | 1.17.1 | 统计分布、KL散度计算     |
| networkx   | 3.6.1  | 地铁图构建、最短路径推断 |
| matplotlib | 3.10.8 | 实验结果可视化           |
| tqdm       | 4.67.3 | 进度条显示               |

### 快速开始

#### 1. 数据预处理与树构建

```bash
python main.py
```

**程序流程**：
1. 数据清洗：从 `data/` 文件夹加载地铁刷卡记录，提取有效的进站-出站对。
2. 地铁图构建：基于深圳地铁实际线路和换乘点构建有向加权图。
3. 路径推断：利用 Dijkstra 最短路径算法为每个 OD 对推断真实乘车路线。
4. 前缀树生成：将所有路径插入前缀树结构。
5. 预算分配与加噪：调用拉格朗日算法分配隐私预算，应用拉普拉斯噪声。
6. 结果可视化：生成论文中的 Figure 3～7 对比图表。

**输出示例**：
```
当前图节点数: 234
从 机场东 到 罗湖 的推断路径: 
机场东 -> 坪洲 -> 西乡 -> 宝安中心 -> 前海湾 -> 宝华 -> 临海 -> 翻身 -> 灵芝 -> ... -> 罗湖

清洗后得到的有效行程记录数: 4,532,000（经过 200 倍合成）
提取的唯一 OD 对数量: 8,476
```

---

## 项目总体架构

### 系统流程图

```
┌─────────────────────────────────────────┐
│   输入：地铁刷卡记录 (CSV 文件)          │
│   + 深圳地铁线路拓扑                     │
└──────────────┬──────────────────────────┘
               ↓
┌─────────────────────────────────────────┐
│  1. 数据清洗与 OD 对统计                 │
│  - 提取"地铁入站"和"地铁出站"配对        │
│  - 过滤无效行程（超时、同站等）          │
│  - 统计各 OD 对的乘客数                  │
└──────────────┬──────────────────────────┘
               ↓
┌─────────────────────────────────────────┐
│  2. 地铁网络图构建 (utils.py)            │
│  - 8 条地铁线路，234 个节点              │
│  - 换乘惩罚权重（8 分钟）                │
│  - Dijkstra 最短路径查询                 │
└──────────────┬──────────────────────────┘
               ↓
┌─────────────────────────────────────────┐
│  3. 前缀树结构 (TrajectoryTrie)          │
│  - 将轨迹序列转换为树结构                │
│  - 每个节点存储经过该路径的人数          │
│  - Root → 第一站 → ... → 最后一站        │
└──────────────┬──────────────────────────┘
               ↓
┌─────────────────────────────────────────┐
│  4. 隐私预算分配 (Model.py)              │
│  - LagrangianTrie    本方案（最优）      │
│  - LiIncrementalTrie   对标：Li et al.   │
│  - SeqPTTrie          对标：SeqPT        │
│  - SafePathTrie       对标：SafePath     │
└──────────────┬──────────────────────────┘
               ↓
┌─────────────────────────────────────────┐
│  5. 加噪与动态剪枝 (apply_noise_and_prune)│
│  - 拉普拉斯噪声加入                      │
│  - 阈值剪枝：移除低频噪声路径            │
│  - 输出脱敏后的树结构                    │
└──────────────┬──────────────────────────┘
               ↓
┌─────────────────────────────────────────┐
│  输出：精准性指标 + 对比图表             │
│  - 相对误差 (Relative Error)             │
│  - JS 散度 (JSD)                         │
│  - 运行时间分析 (Runtime Breakdown)      │
└─────────────────────────────────────────┘
```

### 核心算法公式

#### 1. 查询概率建模

对于前缀树中的每个节点 v，其被查询的概率为：

p_v = 1/N + Σ p_u  (u ∈ children(v))

其中 N 为树中叶子数（近似总轨迹数）。递推关系表示查询节点 v 的概率等于直接查询 v 的概率加上查询其子孙的概率。高频路径获得更高查询概率，应分配更多预算。

#### 2. 权重计算

w_v = p_v^(1/3)

采用立方根而非线性权重的原因：线性权重过度倾向高频节点，低频节点误差较大；立方根权重平衡性更好，避免极端分配。

#### 3. 路径归一化分配

对于每条从根到叶的路径 path = [v1, v2, ..., vk]：

ε_{v_i} = (w_{v_i} / Σ w_{path}) · ε_total

约束条件：每条完整轨迹路径上的预算之和等于总预算 ε，满足差分隐私严格定义。

#### 4. 加噪机制

noisy_count_v = count_v + Laplace(0, 1/ε_v)

拉普拉斯分布参数 b = 1/ε_v，隐私预算越多，噪声尺度越小。

#### 5. 动态阈值剪枝

threshold = k · sqrt(1/ε_v)

若 noisy_count_v < threshold，删除该节点。参数 k 控制剪枝激进程度（论文用 k=1.5），参数 b 为结构优化系数（通常设为 1.0）。

#### 6. 误差评估指标

**相对误差**

RelErr = mean{|q(D_hat) - q(D)| / max(q(D), s)}

其中 q(D) 为原始数据查询结果，q(D_hat) 为加噪后查询结果，s 为 Sanity bound = 0.1% × 数据集规模。

**JS 散度**

JSD(P || Q) = 0.5·KL(P || M) + 0.5·KL(Q || M)

其中 M = 0.5(P + Q)，用于评估分布相似性。

---

## 主要类与参数说明

### 1. TrieNode (节点类，utils.py)

```python
class TrieNode:
    def __init__(self, location_id=None, epsilon=0.0):
        self.location_id: str         # 车站名称 (Root 为 None)
        self.count: float             # 真实经过该路径的乘客数
        self.noisy_count: float       # 加噪后的乘客数
        self.epsilon: float           # 分配给该节点的隐私预算
        self.children: dict           # 子节点字典 {station: TrieNode}
        self.weight: float            # 预算分配权重 (p^(1/3))
        self.p: float                 # 查询概率
```

| 参数        | 类型  | 含义                                     |
| ----------- | ----- | ---------------------------------------- |
| location_id | str   | 当前车站名称                             |
| count       | float | 真实数据中经过该节点的乘客数             |
| epsilon     | float | 该节点分配的隐私预算（0～总预算）        |
| children    | dict  | 子节点映射，key=下一站名，value=TrieNode |
| noisy_count | float | 加入拉普拉斯噪声后的计数                 |

### 2. TrajectoryTrie (基础树类，utils.py)

```python
class TrajectoryTrie:
    def __init__(self, max_height, total_trajectories):
        self.max_height: int = max_height
        self.root: TrieNode = TrieNode("Root")
        self.root.count = total_trajectories
```

核心方法：

| 方法                            | 功能                       | 返回值                |
| ------------------------------- | -------------------------- | --------------------- |
| insert(trajectory, count)       | 将路径插入树中，更新计数   | None                  |
| allocate_budget(total_epsilon)  | 分配隐私预算（由子类实现） | None                  |
| apply_noise_and_prune(k, b)     | 加噪并剪枝                 | None                  |
| get_raw_data(only_leaves)       | 获取原始数据               | List[dict]            |
| get_sanitized_data(only_leaves) | 获取加噪后数据             | List[dict]            |
| get_epsilon_distribution()      | 获取各层预算分布           | Dict[level: [eps...]] |

参数说明：

| 参数               | 类型  | 范围 | 含义                             |
| ------------------ | ----- | ---- | -------------------------------- |
| max_height         | int   | 2~50 | 前缀树最大高度（轨迹最大站点数） |
| total_trajectories | float | >0   | 总乘客流量                       |
| only_leaves        | bool  | -    | 是否仅返回叶子节点数据           |

### 3. LagrangianTrie (本方案，model.py)

```python
class LagrangianTrie(TrajectoryTrie):
    def allocate_budget(self, total_epsilon):
        self._compute_query_probability(self.root)
        self._compute_weights(self.root)
        self._normalize_budget_per_path(self.root, total_epsilon)
```

| 参数          | 公式                       | 说明                        |
| ------------- | -------------------------- | ----------------------------- |
| total_epsilon | -                          | 总隐私预算（通常 0.5～2.0） |
| p_v           | p_v = 1/N + Σ p_children   | 节点查询概率                |
| w_v           | w_v = p_v^(1/3)            | 预算分配权重                |
| epsilon_v     | ε_v = (w_v / Σ w_path) · ε | 最终分配给节点 v 的预算     |

时间复杂度：O(V)，V 为树中节点数。

核心优势：
- 基于数学最优性定理，全局最优
- 自适应分配：高频路径自动获得更多预算
- 计算高效：预处理 O(V)，查询 O(1)

### 4. LiIncrementalTrie (对标：Li et al.，model.py)

```python
class LiIncrementalTrie(TrajectoryTrie):
    def allocate_budget(self, total_epsilon):
        sigma = 1.0
        weights = [np.log(lv + sigma) for lv in range(1, self.max_height + 1)]
        norm_weights = [w / sum(weights) * total_epsilon for w in weights]
        self._assign_recursive(self.root, norm_weights, level=0)
```

预算分配规则：ε_level = log(level+1) / Σ log(l+1) · ε_total

特点：简单易实现，层级均一分配，不考虑节点实际查询概率，对低频路径不友好。

### 5. SeqPTTrie (对标：Sequential Prefix Tree，model.py)

```python
class SeqPTTrie(TrajectoryTrie):
    def allocate_budget(self, total_epsilon):
        weights = [np.power(0.9, i) for i in range(self.max_height)]
        norm_weights = [w / sum(weights) * total_epsilon for w in weights]
        self._assign_recursive(self.root, norm_weights, level=0)
```

预算分配规则：ε_level = 0.9^level / Σ 0.9^l · ε_total

特点：偏向浅层节点，深层路径预算不足，容易被剪枝，覆盖率较低。

### 6. SafePathTrie (对标：SafePath，model.py)

```python
class SafePathTrie(TrajectoryTrie):
    def allocate_budget(self, total_epsilon):
        decay_factor = 0.5
        weights = [np.power(decay_factor, i) for i in range(self.max_height)]
        norm_weights = [(w / sum(weights)) * total_epsilon for w in weights]
        self._assign_recursive(self.root, norm_weights, level=0)
```

预算分配规则：ε_level = 0.5^level / Σ 0.5^l · ε_total

特点：衰减更快，第一层分配约 33% 预算，深层节点几乎无法保护。

### 7. RealDataExplorer (交互式数据探索器，try_search_tool.py)

```python
class RealDataExplorer:
    def __init__(self, path_list, total_flow):
        self.full_path_list: List[Tuple]
        self.total_flow: float
        self.s_eps      # Epsilon 滑块 (0.1～5.0)
        self.s_h        # Max Height 滑块 (5～50)
        self.s_samples  # 样本量滑块
        self.s_k        # 参数 K (0.5～5.0)
        self.s_b        # 参数 B (0.1～5.0)
```

功能：
- 实时绘制 3 张对比图：MRE vs 树高、ε 统计分布、误差分布 CDF
- 5 个交互滑块，实时更新图表
- 自动分析文本解释参数影响

使用方法：
```python
from try_search_tool import RealDataExplorer
from utils import get_preprocessed_paths

path_list = get_preprocessed_paths(trip_counts)
explorer = RealDataExplorer(path_list, total_flow=5_330_000)
plt.show()
```

---

## 实验结果与复现

### 包含的复现实验

main.py 完整实现了论文中的所有关键实验：

| 实验     | 函数              | 测试指标                | 备注                         |
| -------- | ----------------- | ----------------------- | ---------------------------- |
| Figure 3 | run_benchmark()   | 相对误差 vs 树高        | 四算法对比，固定 ε=1.0       |
| Figure 4 | run_fig4()        | 运行时间 vs 树高        | 时间复杂度分析               |
| Figure 5 | run_fig5()        | 相对误差 vs 树高（多ε） | 不同隐私预算的影响           |
| Figure 6 | run_fig6_x() 系列 | 运行时间分解            | 读取、分配、加噪、输出各阶段 |
| Figure 7 | run_fig7()        | JS散度 & 相对误差 vs ε  | 隐私-效用权衡曲线            |
| 进阶任务 | plot_extra_job()  | ε层级分布对比           | 平均值+标准差可视化          |

### 数据集规模

| 指标       | 原始数据 | 放大后    | 说明          |
| ---------- | -------- | --------- | ------------- |
| 有效刷卡对 | 22,660   | 4,532,000 | ×200 放大系数 |
| 唯一 OD 对 | 8,476    | 8,476     | 不变          |
| 总乘客数   | 22,660   | 4,532,000 | 增大          |

放大原因：原数据较小，噪声相对误差过高。放大至百万级别后效用指标更贴近真实应用。

### 性能对标数据

典型结果（ε=1.0, H=30）：

| 算法           | 相对误差 | 运行时间 | JSD   | 说明  |
| -------------- | -------- | -------- | ----- | ----- |
| LagrangianTrie | 0.245    | 0.087s   | 0.128 | 最优  |
| SeqPT          | 0.312    | 0.089s   | 0.164 | 基准1 |
| SafePath       | 0.298    | 0.091s   | 0.151 | 基准2 |
| Li's Algorithm | 0.287    | 0.094s   | 0.142 | 基准3 |

关键发现：
- 相对误差降低约 21.5%（vs SeqPT）
- 运行时间基本一致（均为 O(V) 时间复杂度）
- 在所有隐私预算水平上均保持领先

---

## 使用示例

### 基础用法：构建树并分配预算

```python
from model import LagrangianTrie
from utils import infer_trajectory, TrieNode

trie = LagrangianTrie(max_height=50, total_trajectories=4_532_000)

for station_in, station_out, count in trip_counts_data:
    path = infer_trajectory(station_in, station_out)
    trie.insert(path, count=count)

trie.allocate_budget(total_epsilon=1.0)
trie.apply_noise_and_prune(k=1.5, b=1.0)

raw_data = trie.get_raw_data(only_leaves=False)
sanitized = trie.get_sanitized_data(only_leaves=False)

from utils import calculate_relative_error
error = calculate_relative_error(trie, sanitized, total_flow=4_532_000)
print(f"相对误差：{error:.4f}")
```

### 高级用法：多模型对比

```python
from model import LagrangianTrie, SeqPTTrie, SafePathTrie, LiIncrementalTrie
import numpy as np
import matplotlib.pyplot as plt

models = {
    "Our Algorithm": LagrangianTrie,
    "SeqPT": SeqPTTrie,
    "SafePath": SafePathTrie,
    "Li's Algorithm": LiIncrementalTrie
}

epsilon_values = [0.5, 1.0, 1.5, 2.0]
results = {name: [] for name in models.keys()}

for eps in epsilon_values:
    for name, ModelClass in models.items():
        trie = ModelClass(max_height=50, total_trajectories=4_532_000)
        for path, count in path_list:
            trie.insert(path, count=count)
        trie.allocate_budget(total_epsilon=eps)
        trie.apply_noise_and_prune(k=1.5, b=1.0)
        sanitized = trie.get_sanitized_data(only_leaves=False)
        error = calculate_relative_error(trie, sanitized, 4_532_000)
        results[name].append(error)

for name, errors in results.items():
    plt.plot(epsilon_values, errors, marker='o', label=name)
plt.legend()
plt.xlabel('Privacy Budget (ε)')
plt.ylabel('Relative Error')
plt.show()
```

### 交互式探索

```python
from try_search_tool import RealDataExplorer
from utils import get_preprocessed_paths

path_list = get_preprocessed_paths(trip_counts)
explorer = RealDataExplorer(path_list, total_flow=4_532_000)
plt.show()
```

在弹出的窗口中可调整 5 个滑块：Epsilon、Max Height、Samples、Parameter K、Parameter B。

---

## 项目文件结构

```
EndEposideCode/
├── main.py                    # 主程序入口
├── model.py                   # 四个模型类定义
├── utils.py                   # 工具函数与基础类
├── try_search_tool.py         # 交互式数据探索器
├── environment.yml            # Conda 环境配置
├── data/                      # 数据文件夹
```

---

## 关键参数调优指南

| 参数          | 默认值 | 建议范围 | 影响                                   |
| ------------- | ------ | -------- | -------------------------------------- |
| epsilon       | 1.0    | 0.1～2.0 | 总隐私预算，越小隐私越强但数据噪声越大 |
| max_height    | 50     | 10～50   | 前缀树深度，地铁轨迹通常 5～20 站      |
| k（剪枝因子） | 1.5    | 0.5～3.0 | 阈值倍数，越大保留节点越多             |
| b（结构系数） | 1.0    | 0.5～2.0 | 预留参数，可调整预算分配权重           |
| SCALE_FACTOR  | 200    | 50～500  | 数据放大倍数                           |

---

## 故障排查

### 问题1：环境配置失败

症状：`conda env create` 报编码错误

解决：
```bash
pip install pandas numpy scipy networkx matplotlib tqdm scikit-learn
```

### 问题2：路径推断失败

症状：`infer_trajectory('机场东', '罗湖')` 返回空列表

原因：车站名称中含"站"字

解决：函数自动处理，可正常使用。

### 问题3：加噪后所有节点被剪枝

症状：`get_sanitized_data()` 返回空列表

原因：参数 k 过大或隐私预算过小

解决：
```python
trie.apply_noise_and_prune(k=1.0, b=1.0)  # 降低 k
# 或
trie.allocate_budget(total_epsilon=2.0)   # 增加隐私预算
```

### 问题4：运行极慢

症状：`run_benchmark()` 执行超过 10 分钟

解决：在 main.py 中修改全局参数
```python
SCALE_FACTOR = 50
HEIGHTS = [2, 3, 4]
ITERATIONS = 3
```

---

## 相关论文与参考

核心论文：
> Optimization of Privacy Budget Allocation In Differential Privacy-Based Public Transit Trajectory Data Publishing for Smart Mobility Applications
>
> 作者：Chenxi Chen, Xianbiao Hu, Qing Tang  
> 机构：The Pennsylvania State University, Guangdong University of Technology  
> 发表：IEEE Transactions on Dependable and Secure Computing (TDSC)

对标论文：
- Li et al. (2022) - "Incremental privacy budget allocation"
- SeqPT algorithm - Sequential Prefix Tree
- SafePath algorithm - Safety-first path release

---

## 许可证

本项目仅供学习和研究使用。

---

**最后更新**：2026年4月18日  
**项目状态**：完成所有基础实验 | 已复现所有论文图表 | 交互式工具可用 | 已生成 AGENTS.md 指南文件
