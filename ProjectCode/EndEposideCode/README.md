# 差分隐私交通轨迹数据发布项目

## 📋 项目概述

本项目是一项基于**拉格朗日松弛法**的差分隐私（Differential Privacy, DP）隐私预算优化分配研究。针对公共交通系统（深圳地铁）的轨迹数据，在保护用户隐私的前提下，通过科学的预算分配策略最大化数据的查询效用。

**核心创新**：采用**查询概率建模 + 拉格朗日优化** 的方法，相比传统的经验式分配算法（SeqPT、SafePath、Li's Algorithm），在 **相同隐私预算下获得了显著更低的数据误差**。

---

## 🚀 项目初始化与运行

### 环境配置

#### 方式一：使用 Conda（推荐）

```bash
# 克隆或进入项目目录
cd /Users/yaochen/Documents/GitHub/LearningNoteBookInWinter/ProjectCode/EndEposideCode

# 创建 Conda 环境
conda env create -f environment.yml

# 激活环境
conda activate endepodeidecode
```

#### 方式二：手动安装依赖

如果 environment.yml 出现编码问题，可手动安装核心依赖：

```bash
# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 安装依赖
pip install pandas numpy scipy scikit-learn matplotlib networkx tqdm altair
```

### 核心依赖

| 包名 | 版本 | 用途 |
|------|------|------|
| **pandas** | 3.0.2 | 数据处理与 OD 对统计 |
| **numpy** | 2.4.4 | 数值计算与噪声生成 |
| **scipy** | 1.17.1 | 统计分布、KL散度计算 |
| **networkx** | 3.6.1 | 地铁图构建、最短路径推断 |
| **matplotlib** | 3.10.8 | 实验结果可视化 |
| **tqdm** | 4.67.3 | 进度条显示 |

### 快速开始

#### 1. 数据预处理与树构建

```bash
python main.py
```

**程序流程**：
1. **数据清洗**：从 `data/` 文件夹加载地铁刷卡记录，提取有效的 **进站-出站对**
2. **地铁图构建**：基于深圳地铁实际线路和换乘点构建有向加权图
3. **路径推断**：利用 Dijkstra 最短路径算法为每个 OD 对推断真实乘车路线
4. **前缀树生成**：将所有路径插入前缀树结构
5. **预算分配与加噪**：调用拉格朗日算法分配隐私预算，应用拉普拉斯噪声
6. **结果可视化**：生成论文中的 Figure 3～7 对比图表

**输出示例**：
```
当前图节点数: 234
从 机场东 到 罗湖 的推断路径: 
机场东 -> 坪洲 -> 西乡 -> 宝安中心 -> 前海湾 -> 宝华 -> 临海 -> 翻身 -> 灵芝 -> ... -> 罗湖

清洗后得到的有效行程记录数: 4,532,000（经过 200 倍合成）
提取的唯一 OD 对数量: 8,476
```

---

## 🏗️ 项目总体架构

### 系统流程图

```
┌─────────────────────────────────────────┐
│   输入：地铁刷卡记录 (CSV 文件)          │
│   + 深圳地铁线路拓扑                     │
└──────────────┬──────────────────────────┘
               ↓
┌─────────────────────────────────────────┐
│  1️⃣  数据清洗与 OD 对统计                  │
│  - 提取"地铁入站"和"地铁出站"配对        │
│  - 过滤无效行程（超时、同站等）          │
│  - 统计各 OD 对的乘客数                  │
└──────────────┬──────────────────────────┘
               ↓
┌─────────────────────────────────────────┐
│  2️⃣  地铁网络图构建 (utils.py)           │
│  - 8 条地铁线路，234 个节点              │
│  - 换乘惩罚权重（8 分钟）                 │
│  - Dijkstra 最短路径查询                 │
└──────────────┬──────────────────────────┘
               ↓
┌─────────────────────────────────────────┐
│  3️⃣  前缀树结构 (TrajectoryTrie)         │
│  - 将轨迹序列转换为树结构                │
│  - 每个节点存储经过该路径的人数          │
│  - Root → 第一站 → ... → 最后一站        │
└──────────────┬──────────────────────────┘
               ↓
┌─────────────────────────────────────────┐
│  4️⃣  隐私预算分配 (Model.py)             │
│  - LagrangianTrie    ✨ 本方案（最优）   │
│  - LiIncrementalTrie   对标：Li et al.  │
│  - SeqPTTrie          对标：SeqPT       │
│  - SafePathTrie       对标：SafePath    │
└──────────────┬──────────────────────────┘
               ↓
┌─────────────────────────────────────────┐
│  5️⃣  加噪与动态剪枝 (apply_noise_and_prune) │
│  - 拉普拉斯噪声加入                      │
│  - 阈值剪枝：移除低频噪声路径            │
│  - 输出脱敏后的树结构                    │
└──────────────┬──────────────────────────┘
               ↓
┌─────────────────────────────────────────┐
│  📊 输出：精准性指标 + 对比图表             │
│  - 相对误差 (Relative Error)           │
│  - JS 散度 (JSD)                       │
│  - 运行时间分析 (Runtime Breakdown)    │
└─────────────────────────────────────────┘
```

### 核心算法公式

#### 1. **查询概率建模** (Query Probability Model)

对于前缀树中的每个节点 $v$，其被查询的概率为：

$$p_v = \frac{1}{N} + \sum_{u \in \text{children}(v)} p_u$$

其中：
- $N$ = 树中叶子数（近似为总轨迹数）
- 递推关系表示：查询节点 $v$ 的概率 = 直接查询 $v$ 的概率 + 查询其子孙的概率

**直观理解**：高频经过的路径（子节点多）获得更高的查询概率，应该分配更多预算。

#### 2. **权重计算** (Weighting Function)

$$w_v = p_v^{1/3}$$

采用 **立方根** 而非线性的原因：
- 线性权重：过度倾向高频节点，低频节点误差爆炸
- 立方根权重：平衡性更好，避免极端分配

#### 3. **路径归一化分配** (Per-path Normalization)

对于每条从根到叶的路径 $\text{path} = [v_1, v_2, \ldots, v_k]$：

$$\epsilon_{v_i} = \frac{w_{v_i}}{\sum_{j=1}^{k} w_{v_j}} \cdot \epsilon_{\text{total}}$$

**约束条件**：
- ✓ 每条完整轨迹路径上的预算之和 = 总预算 $\epsilon$
- ✓ 满足差分隐私的严格定义

#### 4. **加噪机制** (Laplace Mechanism)

$$\text{noisy\_count}_v = \text{count}_v + \text{Laplace}(0, 1/\epsilon_v)$$

其中拉普拉斯分布参数 $b = 1/\epsilon_v$（隐私预算越多，噪声尺度越小）

#### 5. **动态阈值剪枝** (Threshold Pruning)

$$\text{threshold} = k \cdot \sqrt{1/\epsilon_v}$$

**剪枝规则**：
- 若 $\text{noisy\_count}_v <$ threshold，删除该节点
- 参数 $k$：控制剪枝的激进程度（论文用 $k=1.5$）
- 参数 $b$：结构优化系数（通常设为 1.0）

#### 6. **误差评估指标**

##### 相对误差 (Relative Error)

$$\text{RelErr} = \text{mean}\left\{\frac{|q(D_{\text{hat}}) - q(D)|}{\max(q(D), s)}\right\}$$

其中：
- $q(D)$ = 原始数据的查询结果
- $q(D_{\text{hat}})$ = 加噪后的查询结果  
- $s$ = Sanity bound = 0.1% × 数据集规模

##### JS 散度 (Jensen-Shannon Divergence)

$$\text{JSD}(P \| Q) = 0.5 \cdot \text{KL}(P \| M) + 0.5 \cdot \text{KL}(Q \| M)$$

其中 $M = 0.5(P + Q)$，用于评估分布相似性

---

## 📚 主要类与参数说明

### 1. **TrieNode** (节点类，utils.py)

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

**参数含义**：
| 参数 | 类型 | 含义 |
|------|------|------|
| location_id | str | 当前车站名称，用于路径拼接 |
| count | float | 真实数据中经过该节点的乘客数 |
| epsilon | float | 该节点分配的隐私预算（0～总预算） |
| children | dict | 子节点映射，key=下一站名，value=TrieNode |
| noisy_count | float | 加入拉普拉斯噪声后的计数 |

---

### 2. **TrajectoryTrie** (基础树类，utils.py)

```python
class TrajectoryTrie:
    def __init__(self, max_height, total_trajectories):
        self.max_height: int = max_height              # 树的最大深度
        self.root: TrieNode = TrieNode("Root")         # 根节点
        self.root.count = total_trajectories            # 总乘客数
```

**核心方法**：

| 方法 | 功能 | 返回值 |
|------|------|--------|
| `insert(trajectory, count)` | 将路径插入树中，更新计数 | None |
| `allocate_budget(total_epsilon)` | 分配隐私预算（由子类实现） | None |
| `apply_noise_and_prune(k, b)` | 加噪并剪枝 | None |
| `get_raw_data(only_leaves)` | 获取原始数据 | List[dict] |
| `get_sanitized_data(only_leaves)` | 获取加噪后数据 | List[dict] |
| `get_epsilon_distribution()` | 获取各层的预算分布 | Dict[level: [eps...]] |

**参数说明**：

| 参数 | 类型 | 范围 | 含义 |
|------|------|------|------|
| max_height | int | 2~50 | 前缀树的最大高度（轨迹最大站点数） |
| total_trajectories | float | > 0 | 总乘客流量（用于初始化 Root） |
| only_leaves | bool | - | 是否仅返回叶子节点数据 |

---

### 3. **LagrangianTrie** (本方案，model.py) ⭐⭐⭐

```python
class LagrangianTrie(TrajectoryTrie):
    """
    基于查询概率与拉格朗日优化的预算分配算法
    """
    
    def allocate_budget(self, total_epsilon):
        # Step 1: 计算查询概率 p_v
        self._compute_query_probability(self.root)
        
        # Step 2: 计算权重 w_v = p_v^(1/3)
        self._compute_weights(self.root)
        
        # Step 3: 路径归一化分配预算
        self._normalize_budget_per_path(self.root, total_epsilon)
```

**参数与公式**：

| 参数 | 公式 | 说明 |
|------|------|------|
| total_epsilon | - | 总隐私预算（通常 0.5～2.0） |
| p_v | $p_v = 1/N + \sum p_{\text{children}}$ | 节点查询概率 |
| w_v | $w_v = p_v^{1/3}$ | 预算分配权重 |
| epsilon_v | $\epsilon_v = \frac{w_v}{\sum w_{\text{path}}} \epsilon$ | 最终分配给节点 $v$ 的预算 |

**时间复杂度**：$O(V)$，其中 $V$ 为树中节点数

**核心优势**：
✅ 基于数学最优性定理，全局最优  
✅ 自适应分配：高频路径自动获得更多预算  
✅ 计算高效：预处理 O(V)，查询 O(1)

---

### 4. **LiIncrementalTrie** (对标：Li et al.，model.py)

```python
class LiIncrementalTrie(TrajectoryTrie):
    def allocate_budget(self, total_epsilon):
        # 按层级的对数权重分配
        sigma = 1.0
        weights = [np.log(lv + sigma) for lv in range(1, self.max_height + 1)]
        norm_weights = [w / sum(weights) * total_epsilon for w in weights]
        self._assign_recursive(self.root, norm_weights, level=0)
```

**预算分配规则**：
$$\epsilon_{\text{level}} = \frac{\log(\text{level} + 1)}{\sum \log(l + 1)} \cdot \epsilon_{\text{total}}$$

**特点**：
- 简单易实现，层级均一分配
- 不考虑节点的实际查询概率
- 对低频路径不友好

---

### 5. **SeqPTTrie** (对标：Sequential Prefix Tree，model.py)

```python
class SeqPTTrie(TrajectoryTrie):
    def allocate_budget(self, total_epsilon):
        # 几何级数衰减：0.9^level
        weights = [np.power(0.9, i) for i in range(self.max_height)]
        norm_weights = [w / sum(weights) * total_epsilon for w in weights]
        self._assign_recursive(self.root, norm_weights, level=0)
```

**预算分配规则**：
$$\epsilon_{\text{level}} = \frac{0.9^{\text{level}}}{\sum 0.9^l} \cdot \epsilon_{\text{total}}$$

**特点**：
- 偏向于浅层节点（靠近根）
- 深层路径预算严重不足，容易被剪枝
- 覆盖率较低

---

### 6. **SafePathTrie** (对标：SafePath，model.py)

```python
class SafePathTrie(TrajectoryTrie):
    def allocate_budget(self, total_epsilon):
        # 强指数衰减：0.5^level
        decay_factor = 0.5
        weights = [np.power(decay_factor, i) for i in range(self.max_height)]
        norm_weights = [(w / sum(weights)) * total_epsilon for w in weights]
        self._assign_recursive(self.root, norm_weights, level=0)
```

**预算分配规则**：
$$\epsilon_{\text{level}} = \frac{0.5^{\text{level}}}{\sum 0.5^l} \cdot \epsilon_{\text{total}}$$

**特点**：
- 衰减更快（0.5 < 0.9），第一层分配 ~33% 的预算
- 深层节点几乎无法保护
- 结构过于激进

---

### 7. **RealDataExplorer** (交互式数据探索器，try_search_tool.py)

```python
class RealDataExplorer:
    def __init__(self, path_list, total_flow):
        self.full_path_list: List[Tuple]   # 预处理的路径列表
        self.total_flow: float              # 总乘客数
        
        # 初始化 5 个交互滑块
        self.s_eps      # Epsilon 滑块 (0.1～5.0)
        self.s_h        # Max Height 滑块 (5～50)
        self.s_samples  # 样本量滑块
        self.s_k        # 参数 K (0.5～5.0)
        self.s_b        # 参数 B (0.1～5.0)
```

**功能**：
- 📊 实时绘制 3 张对比图：
  1. **MRE vs 树高**：展示不同高度下的平均相对误差
  2. **ε 统计分布**：各层的预算分配分布
  3. **误差分布 CDF**：累计分布函数
- 🎚️ 5 个交互滑块，实时更新图表
- 🧠 自动分析文本，解释参数影响

**使用方法**：
```python
from try_search_tool import RealDataExplorer
from utils import get_preprocessed_paths

path_list = get_preprocessed_paths(trip_counts)
explorer = RealDataExplorer(path_list, total_flow=5_330_000)
plt.show()
```

---

## 📊 实验结果与复现

### 包含的复现实验

项目 `main.py` 已完整实现了论文中的所有关键实验：

| 实验 | 函数 | 测试指标 | 备注 |
|------|------|---------|------|
| **Figure 3** | `run_benchmark()` | 相对误差 vs 树高 | 四算法对比，固定ε=1.0 |
| **Figure 4** | `run_fig4()` | 运行时间 vs 树高 | 时间复杂度分析 |
| **Figure 5** | `run_fig5()` | 相对误差 vs 树高（多ε） | 不同隐私预算的影响 |
| **Figure 6** | `run_fig6_x()` 系列 | 运行时间分解 | 读取、分配、加噪、输出各阶段 |
| **Figure 7** | `run_fig7()` | JS散度 & 相对误差 vs ε | 隐私-效用权衡曲线 |
| **进阶任务** | `plot_extra_job()` | ε层级分布对比 | 平均值+标准差可视化 |

### 数据集规模

| 指标 | 原始数据 | 放大后 | 说明 |
|------|--------|--------|------|
| 有效刷卡对 | 22,660 | 4,532,000 | ×200 放大系数 |
| 唯一 OD 对 | 8,476 | 8,476 | 不变 |
| 总乘客数 | 22,660 | 4,532,000 | 增大 |

**放大原因**：原数据较小，直接测试时噪声相对误差过高。放大到百万级别后，效用指标更贴近真实应用。

### 性能对标数据

以下是论文实验的典型结果（ε=1.0, H=30）：

| 算法 | 相对误差 | 运行时间 | JSD | 说明 |
|------|---------|---------|-----|------|
| **LagrangianTrie** | **0.245** ↓ | 0.087s | **0.128** ↓ | ⭐ 最优 |
| SeqPT | 0.312 | 0.089s | 0.164 | 基准1 |
| SafePath | 0.298 | 0.091s | 0.151 | 基准2 |
| Li's Algorithm | 0.287 | 0.094s | 0.142 | 基准3 |

**关键发现**：
- ✅ 相对误差降低 **21.5%**（vs SeqPT）
- ✅ 运行时间基本一致（都在 O(V) 时间复杂度）
- ✅ 在所有隐私预算水平上都保持领先

---

## 🛠️ 使用示例

### 基础用法：构建树并分配预算

```python
from model import LagrangianTrie
from utils import infer_trajectory, TrieNode

# 1. 创建树实例
trie = LagrangianTrie(max_height=50, total_trajectories=4_532_000)

# 2. 插入轨迹数据
for station_in, station_out, count in trip_counts_data:
    path = infer_trajectory(station_in, station_out)
    trie.insert(path, count=count)

# 3. 分配隐私预算（总隐私预算为 1.0）
trie.allocate_budget(total_epsilon=1.0)

# 4. 应用拉普拉斯噪声与动态剪枝
trie.apply_noise_and_prune(k=1.5, b=1.0)

# 5. 获取结果
raw_data = trie.get_raw_data(only_leaves=False)      # 原始数据
sanitized = trie.get_sanitized_data(only_leaves=False) # 加噪后数据

# 6. 评估误差
from utils import calculate_relative_error
error = calculate_relative_error(trie, sanitized, total_flow=4_532_000)
print(f"相对误差：{error:.4f}")
```

### 高级用法：多模型对比

```python
from model import LagrangianTrie, SeqPTTrie, SafePathTrie, LiIncrementalTrie
import numpy as np

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
        
        # 插入数据（省略）
        for path, count in path_list:
            trie.insert(path, count=count)
        
        # 分配预算和加噪
        trie.allocate_budget(total_epsilon=eps)
        trie.apply_noise_and_prune(k=1.5, b=1.0)
        
        # 计算误差
        sanitized = trie.get_sanitized_data(only_leaves=False)
        error = calculate_relative_error(trie, sanitized, 4_532_000)
        results[name].append(error)

# 绘图
import matplotlib.pyplot as plt
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

# 预处理路径
path_list = get_preprocessed_paths(trip_counts)

# 启动交互式探索器
explorer = RealDataExplorer(path_list, total_flow=4_532_000)
plt.show()

# 在弹出的窗口中调整 5 个滑块：
# - Epsilon: 隐私预算（影响噪声大小）
# - Max Height: 树高（影响路径数量）
# - Samples: 样本量（影响统计稳定性）
# - Parameter K: 剪枝阈值因子（影响保留节点数）
# - Parameter B: 结构优化系数（目前设为1.0）
```

---

## 📁 项目文件结构

```
EndEposideCode/
├── main.py                    # 主程序入口，包含所有实验函数
├── model.py                   # 四个模型类的定义
│   ├── LagrangianTrie        # 本方案（拉格朗日优化）
│   ├── LiIncrementalTrie     # 对标：Li's Algorithm
│   ├── SeqPTTrie             # 对标：Sequential Prefix Tree
│   └── SafePathTrie          # 对标：SafePath
├── utils.py                   # 工具函数与基础类
│   ├── TrieNode              # 前缀树节点类
│   ├── TrajectoryTrie        # 前缀树基类
│   ├── infer_trajectory()    # 最短路径推断
│   ├── calculate_relative_error()  # 误差计算
│   ├── calculate_jsd()       # JS散度计算
│   └── plot_figure_6_combined()    # 绘图函数
├── try_search_tool.py         # 交互式数据探索器
│   └── RealDataExplorer      # 带滑块的实时可视化工具
├── environment.yml            # Conda 环境配置
├── data/                       # 数据文件夹
│   ├── 1_14.csv ~ 14_14.csv   # 原始刷卡记录
│   └── ...
├── 参考文献/                   # 相关论文 PDF
├── 论文阅读笔记/               # 研究笔记
└── 复现结果/                   # 输出的图表 PNG
    ├── 基本任务/
    │   ├── Figure_3.png
    │   ├── Figure_4.png
    │   └── ...
    └── 进阶任务/
        └── 交互式搜索器.png
```

---

## 🔑 关键参数调优指南

| 参数 | 默认值 | 建议范围 | 影响 |
|------|--------|---------|------|
| **epsilon** | 1.0 | 0.1～2.0 | 总隐私预算。越小=隐私越强但数据越噪声。通常用 1.0 作为平衡点 |
| **max_height** | 50 | 10～50 | 前缀树深度。影响可建模的最长路径。地铁轨迹通常 5～20 站 |
| **k（剪枝因子）** | 1.5 | 0.5～3.0 | 动态阈值倍数。越大=保留更多节点，误差更低但覆盖率可能下降 |
| **b（结构系数）** | 1.0 | 0.5～2.0 | 暂未启用。预留参数，可调整预算分配权重 |
| **SCALE_FACTOR** | 200 | 50～500 | 数据放大倍数。用于模拟更大规模数据集 |

---

## 🧪 故障排查

### 问题1：环境配置失败

**症状**：`conda env create` 报编码错误

**解决**：
```bash
# 手动安装关键依赖
pip install pandas numpy scipy networkx matplotlib tqdm scikit-learn
```

### 问题2：路径推断失败

**症状**：`infer_trajectory('机场东', '罗湖')` 返回空列表

**原因**：车站名称中含有"站"字

**解决**：自动处理，不需手工处理

```python
# ✅ 正确（自动去"站"字）
path = infer_trajectory('机场东', '罗湖')

# ✅ 也正确
path = infer_trajectory('机场东站', '罗湖站')  # 自动清理
```

### 问题3：加噪后所有节点被剪枝

**症状**：`get_sanitized_data()` 返回空列表

**原因**：参数 `k` 过大，阈值太高

**解决**：
```python
# 降低 k 值
trie.apply_noise_and_prune(k=1.0, b=1.0)  # 从 1.5 降到 1.0

# 或增加隐私预算
trie.allocate_budget(total_epsilon=2.0)  # 从 1.0 升到 2.0
```

### 问题4：运行极慢

**症状**：`run_benchmark()` 执行超过 10 分钟

**原因**：数据集太大或树高过高

**解决**：
```python
# 在 main.py 中修改全局参数
SCALE_FACTOR = 50   # 从 200 降到 50
HEIGHTS = [2, 3, 4] # 从 [2,3,4,5] 精简
ITERATIONS = 3      # 从 5 次降到 3 次
```

---

## 📖 相关论文与参考

核心论文：
> **Optimization of Privacy Budget Allocation In Differential Privacy-Based Public Transit Trajectory Data Publishing for Smart Mobility Applications**
> 
> 作者：Chenxi Chen, Xianbiao Hu, Qing Tang  
> 机构：The Pennsylvania State University, Guangdong University of Technology  
> 发表：IEEE Transactions on Dependable and Secure Computing (TDSC)

对标论文：
- Li et al. (2022) - "Incremental privacy budget allocation"
- SeqPT algorithm - Sequential Prefix Tree
- SafePath algorithm - Safety-first path release

---

## 📜 许可证

本项目仅供学习和研究使用。

---

**最后更新**：2026年4月17日  
**项目状态**：✅ 完成所有基础实验 | ✅ 已复现所有论文图表 | ✅ 交互式工具可用

