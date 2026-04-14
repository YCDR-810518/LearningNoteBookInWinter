# AGENTS.md

## 项目概述
这是一个差分隐私轨迹数据发布的研究项目，实现地铁乘客轨迹数据的隐私保护算法。代码库重现论文中的实验，使用前缀树结构发布隐私保护的轨迹数据。

## 架构
- **核心结构**：基于前缀树（trie）的轨迹数据表示
- **基类**：`utils.py` 中的 `TrajectoryTrie` 处理树构建、噪声注入和剪枝
- **算法变体**：`model.py` 中四个 DP 预算分配策略：
  - `LagrangianTrie`：基于查询概率的拉格朗日优化分配
  - `LiIncrementalTrie`：对数层级权重
  - `SeqPTTrie`：几何衰减（0.9 因子）
  - `SafePathTrie`：强指数衰减（0.5 因子）

## 数据流
1. 从 `data/` 目录加载 CSV 行程数据
2. 预处理：过滤地铁行程，提取 OD 对，使用 NetworkX 图推断最短路径
3. 构建 trie 并插入轨迹数据
4. 按算法分配隐私预算
5. 应用拉普拉斯噪声 + 动态剪枝（阈值 = k * sqrt(1/ε)）
6. 评估：与原始数据比较相对误差，计算 Jensen-Shannon 散度

## 关键工作流
- **运行实验**：执行 `main.py` 重现图 3-7
- **数据放大**：使用 `main.py` 中的 `SCALE_FACTOR = 200` 进行合成数据放大
- **路径推断**：调用 `utils.py` 中的 `infer_trajectory(start, end)` 获取最短路径
- **评估**：使用 `calculate_relative_error()` 和 `calculate_jsd()` 计算指标

## 约定
- **参数**：默认 ε=1.0, k=1.5, b=1.0, 高度=[2,3,4,5]
- **站名**：匹配时去除 "站" 后缀（例如 "罗湖" 而非 "罗湖站"）
- **噪声**：拉普拉斯噪声 scale = 1/ε，裁剪为非负
- **剪枝**：基于噪声 scale 的动态阈值，移除低计数节点
- **绘图**：使用 `plot_results()` 保持一致样式，包括算法特定的颜色/标记

## 依赖
- **环境**：使用 `environment.yml` 设置 conda 环境
- **图**：`utils.py` 中的 NetworkX 图 `G` 包含深圳地铁拓扑及换乘惩罚
- **关键导入**：pandas, numpy, matplotlib, scipy, tqdm, networkx

## 集成点
- **数据输入**：`data/` 中的 CSV 文件，列包括 card_no, deal_date, station, deal_type
- **路径缓存**：使用 `get_preprocessed_paths()` 避免重复 Dijkstra 调用
- **跨组件**：trie 节点引用轨迹计数，算法修改每个节点的 ε 分配

## 高级功能
- **交互式探索器**：计划用于图 8 - 可调节 ε, 高度, k, b, query_samples 参数
- **运行时分析**：图 6 分解计算时间为读取/分配/消毒/写入阶段
- **基准比较**：始终与 Li's、SeqPT 和 SafePath 算法比较