import networkx as nx
import numpy as np
from scipy.stats import entropy
import math

G = nx.Graph()


# --- 简化后的添加线路函数 ---
def add_line(graph, stations, line_name, weight=2):
    """统一将站间距设为 2 分钟"""
    # 统一去掉名称中的“站”字，防止匹配失败
    stations = [s.replace('站', '') for s in stations]
    for i in range(len(stations) - 1):
        u = f"{stations[i]}_{line_name}"
        v = f"{stations[i + 1]}_{line_name}"
        graph.add_edge(u, v, weight=weight)


# --- 补全后的全线站点数据 (基于 2018 地图) ---

# 1号线 (罗湖 - 机场东)
l1_stations = [
    "罗湖", "国贸", "老街", "大剧院", "科学馆", "华强路", "岗厦", "会展中心", "购物公园", "香蜜湖",
    "车公庙", "竹子林", "侨城东", "华侨城", "世界之窗", "白石洲", "高新园", "深圳大学", "桃园", "大新",
    "鲤鱼门", "前海湾", "新安", "宝安中心", "宝体", "坪洲", "西乡", "固戍", "后瑞", "机场东"
]

# 2号线 (赤湾 - 新秀)
l2_stations = [
    "赤湾", "蛇口港", "海上世界", "水湾", "东角头", "湾厦", "海月", "登良", "后海", "科苑",
    "红树湾", "世界之窗", "侨城北","深康", "安托山", "侨香", "香蜜", "香梅北", "景田", "莲花西", "福田",
    "市民中心", "岗厦北", "华强北", "燕南", "大剧院", "湖贝", "黄贝岭", "新秀"
]

# 3号线 (益田 - 双龙)
l3_stations = [
    "益田", "石厦", "购物公园", "福田", "少年宫", "莲花村", "华新", "通新岭", "红岭", "老街",
    "晒布", "翠竹", "田贝", "水贝", "草埔", "布吉", "木棉湾", "大芬", "丹竹头", "六约",
    "塘坑", "横岗", "永湖", "荷坳", "大运", "爱联", "吉祥", "龙城广场", "南联", "双龙"
]

# 4号线 (清湖 - 福田口岸)
l4_stations = [
    "清湖", "龙华", "龙胜", "上塘", "红山", "深圳北", "白石龙", "民乐",
    "上梅林", "莲花北", "少年宫", "市民中心", "会展中心", "福民", "福田口岸"
]

# 5号线 (黄贝岭 - 前海湾)
l5_stations = [
    "黄贝岭", "怡景", "太安", "布心", "百鸽笼", "布吉", "长龙", "下水径", "上水径", "杨美",
    "坂田", "五和", "民治", "深圳北", "长岭陂", "塘朗", "大学城", "西丽", "留仙洞", "兴东",
    "洪浪北", "灵芝", "翻身", "宝安中心", "宝华", "临海", "前海湾"
]

# 7号线 (西丽湖 - 太安)
l7_stations = [
    "西丽湖", "西丽", "茶光", "珠光", "龙井", "桃源村", "深云", "安托山", "农林", "车公庙",
    "上沙", "沙尾", "石厦", "皇岗村", "福民", "皇岗口岸", "赤尾", "华强南", "华强北", "华新",
    "黄木岗", "八卦岭", "红岭北", "笋岗", "洪湖", "田贝", "太安"
]

# 9号线 (红树湾南 - 文锦)
l9_stations = [
    "文锦", "向西村", "人民南", "鹿丹村", "红岭南", "红岭", "园岭", "红岭北", "泥岗", "银湖",
    "孖岭", "上梅林", "梅村", "下梅林", "梅景", "景田", "香梅", "车公庙", "下沙", "深圳湾公园",
    "深湾", "红树湾南"
]

# 11号线 (福田 - 碧头)
l11_stations = [
    "福田", "车公庙", "红树湾南", "后海", "南山", "前海湾", "宝安", "碧海湾", "机场",
    "机场北", "福永", "桥头", "塘尾", "马鞍山", "沙井", "后亭", "松岗", "碧头"
]

# 批量添加线路
for line, name in [(l1_stations, "L1"), (l2_stations, "L2"), (l3_stations, "L3"),
                   (l4_stations, "L4"), (l5_stations, "L5"), (l7_stations, "L7"),
                   (l9_stations, "L9"), (l11_stations, "L11")]:
    add_line(G, line, name)

# --- 完整的换乘配置 ---
transfer_penalty = 8
transfers = [
    ("车公庙", ["L1", "L7", "L9", "L11"]), ("福田", ["L2", "L3", "L11"]), ("前海湾", ["L1", "L5", "L11"]),
    ("世界之窗", ["L1", "L2"]), ("大剧院", ["L1", "L2"]), ("会展中心", ["L1", "L4"]),
    ("购物公园", ["L1", "L3"]), ("老街", ["L1", "L3"]), ("宝安中心", ["L1", "L5"]),
    ("市民中心", ["L2", "L4"]), ("少年宫", ["L3", "L4"]), ("福民", ["L4", "L7"]),
    ("深圳北", ["L4", "L5"]), ("上梅林", ["L4", "L9"]), ("后海", ["L2", "L11"]),
    ("景田", ["L2", "L9"]), ("安托山", ["L2", "L7"]), ("华强北", ["L2", "L7"]),
    ("黄贝岭", ["L2", "L5"]), ("布吉", ["L3", "L5"]), ("田贝", ["L3", "L7"]),
    ("华新", ["L3", "L7"]), ("石厦", ["L3", "L7"]), ("红岭", ["L3", "L9"]),
    ("西丽", ["L5", "L7"]), ("太安", ["L5", "L7"]), ("红岭北", ["L7", "L9"]),
    ("红树湾南", ["L9", "L11"])
]

for station, lines in transfers:
    for i in range(len(lines)):
        for j in range(i + 1, len(lines)):
            u, v = f"{station}_{lines[i]}", f"{station}_{lines[j]}"
            if G.has_node(u) and G.has_node(v):
                G.add_edge(u, v, weight=transfer_penalty)


# 路径推断函数
def infer_trajectory(start_station, end_station):
    # 自动移除输入中的“站”字
    start_station, end_station = start_station.replace('站', ''), end_station.replace('站', '')
    start_nodes = [n for n in G.nodes() if n.startswith(start_station)]
    end_nodes = [n for n in G.nodes() if n.startswith(end_station)]

    if not start_nodes or not end_nodes: return []

    best_path = None
    min_weight = float('inf')
    for s in start_nodes:
        for e in end_nodes:
            try:
                path = nx.shortest_path(G, s, e, weight='weight')
                w = nx.shortest_path_length(G, s, e, weight='weight')
                if w < min_weight:
                    min_weight, best_path = w, path
            except:
                continue

    if not best_path: return []

    clean_trajectory = []
    for p in best_path:
        name = p.split('_')[0]
        if not clean_trajectory or clean_trajectory[-1] != name:
            clean_trajectory.append(name)
    return clean_trajectory




"""
# 已经将所有数据都测试完毕，均通过了测试，于是我就将此段测试逻辑注释掉了
# 找出哪些行程导致了空路径
unique_trips['path'] = unique_trips.apply(
    lambda x: infer_trajectory(x['station_in'], x['station_out']), axis=1
)

fail_trips = unique_trips[unique_trips['path'].map(len) == 0]
print("路径推断失败的样本：")
print(fail_trips)
"""

# 从路线图的数据中构建树状图
# 定义树中的节点对象，规定相关需要用到的参数

"""
location_id: 车站编号
count: 经过该路径的真实人数
noisy_count: 加噪后的人数（初始化为 0）
epsilon: 该节点分配到的隐私预算（由算法计算）
children: 子节点列表
"""
# 准备提取拉格朗日特殊方法，让这里的树结构成为通用的基类
class TrieNode:
    # __slots__ = ['location_id', 'count', 'noisy_count', 'epsilon', 'children']
    def __init__(self, location_id=None, epsilon=0.0):
        self.location_id = location_id  # 车站编号 (Root 可为 None)
        self.count = 0                  # 经过该路径的真实人数
        self.noisy_count = 0            # 加噪后的人数 (初始化为 0)
        self.epsilon = epsilon          # 该节点分配到的隐私预算
        self.children = {}              # 子节点字典: {id: TrieNode对象}

    def __repr__(self):
        return f"Node({self.location_id}, count={self.count})"


class TrajectoryTrie:
    """
    这里放的是树的生成算法
    主要功能:
    1. 将地铁的路线图转换为树状图
    2. 将数据载入
    3. 为所有的差分隐私模型提供加噪算法
    """
    def __init__(self, max_height, total_trajectories):
        self.max_height = max_height
        self.root = TrieNode(location_id="Root")
        self.root.count = total_trajectories
        self.score = 0.0
    def insert(self, trajectory, count=1):
        current_node = self.root
        for i, loc_id in enumerate(trajectory):
            if i >= self.max_height: break
            if loc_id not in current_node.children:
                current_node.children[loc_id] = TrieNode(location_id=loc_id)
            current_node = current_node.children[loc_id]
            current_node.count += count

    def allocate_budget(self, total_epsilon):
        """抽象方法：由子类实现具体的预算分配算法"""
        raise NotImplementedError

    def apply_noise_and_prune(self, k, b):
        """通用加噪流程：所有模型共享此逻辑"""
        self._process_node_noise(self.root, level=1, k=k, b=b)

    def _process_node_noise(self, current_node, level, k, b):
        child_ids = list(current_node.children.keys())

        for cid in child_ids:
            child = current_node.children[cid]

            # 防止 ε 太小导致爆炸
            epsilon = max(child.epsilon, 1e-3)
            scale = 1.0 / epsilon

            noise = np.random.laplace(0, scale)
            child.noisy_count = max(0, child.count + noise)

            # 动态阈值（核心）
            threshold = k * math.sqrt(scale)

            if child.noisy_count < threshold:
                del current_node.children[cid]
            elif level < self.max_height:
                self._process_node_noise(child, level + 1, k, b)
    def get_raw_data(self, node=None, path=None, only_leaves=True):
        if node is None: node, path = self.root, []
        results = []
        for cid, child in node.children.items():
            current_path = path + [cid]
            if not only_leaves or not child.children:
                results.append({"path": " -> ".join(current_path), "count": child.count})
            results.extend(self.get_raw_data(child, current_path, only_leaves))
        return results

    def get_sanitized_data(self, node=None, path=None, only_leaves=False):
        if node is None: node, path = self.root, []
        results = []
        for cid, child in node.children.items():
            current_path = path + [cid]
            # 判定是否为叶子节点：没有子节点了
            is_leaf = len(child.children) == 0

            if not only_leaves or is_leaf:
                results.append({
                    "path": " -> ".join(current_path),
                    "count": round(child.noisy_count, 2)
                })

            if not is_leaf:
                results.extend(self.get_sanitized_data(child, current_path, only_leaves))
        return results




def calculate_relative_error(original_trie, sanitized_results, total_flow):
    """
    这是根据定义2写出来的模型评估函数
    original_trie: 原始数据的树对象（未加噪）
    sanitized_results: 处理后得到的路径列表 [{"path": "...", "count": ...}]
    total_count: 数据集总行程数
    """
    # 计算 sanity bound (s) = 0.1% of dataset size
    s = 0.001 * total_flow

    errors = []
    # 获取原始的所有计数查询结果 (q(D))
    raw_data = {item['path']: item['count'] for item in original_trie.get_raw_data(only_leaves=False)}
    sanitized_data = {item['path']: item['count'] for item in sanitized_results}

    # 遍历所有路径计算误差
    all_paths = set(raw_data.keys()) | set(sanitized_data.keys())
    for path in all_paths:
        q_D = raw_data.get(path, 0)
        q_D_hat = sanitized_data.get(path, 0)

        # 按照公式：|q(D_hat) - q(D)| / max(q(D), s)
        error = abs(q_D_hat - q_D) / max(q_D, s)
        errors.append(error)

    return np.mean(errors) if errors else 0




def get_preprocessed_paths(trip_counts_df):
    """
    将 OD 统计数据转换为 (路径, 权重) 的列表
    """
    print("正在进行路径推断预处理...")
    preprocessed = []
    path_cache = {}  # 缓存，避免重复调用 Dijkstra

    for row in trip_counts_df.itertuples():
        start, end = row.station_in, row.station_out
        count = row.passenger_count

        pair = (start, end)
        if pair not in path_cache:
            # 调用你原有的 infer_trajectory
            path_cache[pair] = infer_trajectory(start, end)

        path = path_cache[pair]
        if path:
            preprocessed.append((path, count))

    print(f"预处理完成，共计 {len(preprocessed)} 条唯一路径。")
    return preprocessed



def calculate_jsd(original_results, sanitized_results):
    """
    计算 Jensen-Shannon Divergence (JSD) 以评估分布相似性
    original_results: 原始数据列表 [{"path": "...", "count": ...}]
    sanitized_results: 加噪后数据列表 [{"path": "...", "count": ...}]
    """
    # 转换为字典格式方便对齐，并过滤非正数（熵计算要求分量为正）
    raw_dict = {item['path']: max(0, item['count']) for item in original_results}
    san_dict = {item['path']: max(0, item['count']) for item in sanitized_results}

    # 获取并集路径，确保两个分布在相同的维度（Sample Space）上对比
    all_paths = list(set(raw_dict.keys()) | set(san_dict.keys()))

    # 构建频率向量 P 和 Q
    P = np.array([raw_dict.get(p, 0.0) for p in all_paths])
    Q = np.array([san_dict.get(p, 0.0) for p in all_paths])

    # 归一化为概率分布（概率总和为 1）
    sum_P = np.sum(P)
    sum_Q = np.sum(Q)

    if sum_P == 0: return 1.0  # 原始数据为空的极端情况
    P = P / sum_P

    # 如果加噪后所有路径都被剪枝了（sum_Q为0），JSD 趋向于最大值
    if sum_Q == 0: return 1.0
    Q = Q / sum_Q

    # 计算 M = 0.5 * (P + Q)
    M = 0.5 * (P + Q)

    # JSD(P||Q) = 0.5 * KL(P||M) + 0.5 * KL(Q||M)
    # scipy.stats.entropy(P, M) 默认计算的就是 KL 散度
    js_divergence = 0.5 * entropy(P, M) + 0.5 * entropy(Q, M)

    return js_divergence
import matplotlib.pyplot as plt


def plot_figure_6_combined(res1, res2, res3, res4):
    """
    res1: run_fig6_1 的返回值 (单个点的 Breakdown)
    res2: run_fig6_1_3 的返回值 (随 K 变化)
    res3: run_fig6_1_4 的返回值 (随 B 变化)
    res4: run_fig6_2 的返回值 (随 Epsilon 变化)
    """
    # 设置全局参数范围（需与你测试函数中的一致）
    K_RANGE = [0.5, 0.75, 1.0, 1.25, 1.5]
    B_RANGE = [0, 1, 2, 3, 4, 5]
    EPS_RANGE = [0.5, 0.75, 1.0, 1.25, 1.5]

    fig, axes = plt.subplots(2, 2, figsize=(14, 11))
    plt.subplots_adjust(wspace=0.25, hspace=0.3)

    # 颜色风格定义 (论文常用配色)
    colors = ['#4A90E2', '#50E3C2', '#F5A623', '#D0021B']
    stages = ["Reading", "Allocation", "Sanitization", "Writing"]
    line_style = {"color": "red", "marker": "o", "linewidth": 2, "markersize": 8}

    # --- (a) Subplot 1: Runtime Breakdown ---
    ax = axes[0, 0]
    bottom = 0
    # 取 res1 列表中的第一个值（因为 res1 只有一个点）
    for i, stage in enumerate(stages):
        val = res1[stage][0]
        ax.bar(['Our Algorithm'], [val], bottom=bottom, label=stage, color=colors[i], width=0.4)
        bottom += val
    ax.set_ylabel('Runtime (s)', fontsize=12)
    ax.set_title('(a) k=1.5, b=1, ε=1', fontsize=13)
    ax.legend(loc='upper right', frameon=True)

    # --- (b) Subplot 2: Runtime vs. K ---
    ax = axes[0, 1]
    ax.plot(K_RANGE, res2["Total"], **line_style)
    ax.set_xlabel('Parameter k', fontsize=12)
    ax.set_ylabel('Total Runtime (s)', fontsize=12)
    ax.set_title('(b) b=1, ε=1', fontsize=13)

    # --- (c) Subplot 3: Runtime vs. B ---
    ax = axes[1, 0]
    ax.plot(B_RANGE, res3["Total"], **{**line_style, "marker": "s"})  # 使用方块 marker
    ax.set_xlabel('Parameter b', fontsize=12)
    ax.set_ylabel('Total Runtime (s)', fontsize=12)
    ax.set_title('(c) k=1.5, ε=1', fontsize=13)

    # --- (d) Subplot 4: Runtime vs. Epsilon ---
    ax = axes[1, 1]
    ax.plot(EPS_RANGE, res4["Total"], **{**line_style, "marker": "^"})  # 使用三角 marker
    ax.set_xlabel('Privacy Budget (ε)', fontsize=12)
    ax.set_ylabel('Total Runtime (s)', fontsize=12)
    ax.set_title('(d) k=1.5, b=1', fontsize=13)

    # 统一优化所有子图的网格线
    for row in axes:
        for a in row:
            a.grid(True, linestyle=':', alpha=0.6)

    plt.suptitle('Figure 6: Computational Efficiency Analysis', fontsize=16, fontweight='bold')
    plt.show()
# 运行实验，支持参数化，返回各算法误差、节点数和JSD
def run_experiment_with_params(trajectory_data, total_flow, params):
    """
    使用给定参数运行实验，返回每个算法的误差、节点数和JSD。
    trajectory_data: 轨迹数据 (path, count) 的列表
    total_flow: 总流量
    params: 参数字典，包括 epsilon, height, k, b
    返回:
        results: 字典，包含每个算法的误差、节点数和JSD
    """
    epsilon = params['epsilon']
    height = params['height']
    k = params['k']
    b = params['b']

    # 初始化模型
    models = {
        "Our Algorithm": LagrangianTrie(height, total_flow),
        "Li's Algorithm": LiIncrementalTrie(height, total_flow),
        "SeqPT": SeqPTTrie(height, total_flow),
        "SafePath": SafePathTrie(height, total_flow)
    }

    # 插入数据
    for name, trie in models.items():
        for path, count in trajectory_data:
            trie.insert(path, count=count)

    # 分配预算并加噪剪枝
    results = {}
    for name, trie in models.items():
        try:
            trie.allocate_budget(epsilon)
            trie.apply_noise_and_prune(k=k, b=b)

            # 获取加噪后的数据
            sanitized_data = trie.get_sanitized_data(only_leaves=False)

            # 计算误差、节点数和JSD
            raw_trie = TrajectoryTrie(max_height=height, total_trajectories=total_flow)
            for path, count in trajectory_data:
                raw_trie.insert(path, count=count)
            raw_data = raw_trie.get_raw_data(only_leaves=False)

            error = calculate_relative_error(raw_trie, sanitized_data, total_flow)
            jsd = calculate_jsd(raw_data, sanitized_data)
            node_count = len(sanitized_data)

            results[name] = {
                'error': error,
                'jsd': jsd,
                'nodes': node_count
            }
        except Exception as e:
            # 如果算法失败，记录为 NaN
            results[name] = {
                'error': float('nan'),
                'jsd': float('nan'),
                'nodes': 0
            }
    return results