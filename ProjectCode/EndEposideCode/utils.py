import pandas as pd
from pathlib import Path
import networkx as nx
import numpy as np

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


# --- 路径推断函数  ---
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


# --- 测试 ---
print(f"当前图节点数: {G.number_of_nodes()}")
print(f"从 机场东 到 罗湖 的推断路径: \n{' -> '.join(infer_trajectory('机场东', '罗湖'))}")

# 下面执行路线预测测试（时间最小化）
# 跨平台路径
data_path = Path(__file__).parent / "data"

# 使用 rglob 还可以递归搜索子文件夹下的所有 csv
all_files = list(data_path.glob("*.csv"))

df_list = [pd.read_csv(f) for f in all_files]
data = pd.concat(df_list, ignore_index=True)
print(data.info())
data = data.dropna()
print(data.info())
print(data.head())
print(data.describe())
print(data["company_name"].unique())

# 转换时间并排序（确保同一张卡的记录按先后顺序排列）
# 转换时间并排序（确保同一张卡的记录按先后顺序排列）
data['deal_date'] = pd.to_datetime(data['deal_date'])

# 只保留地铁进出站数据（排除公交消费等干扰）
df_metro = data[data['deal_type'].isin(['地铁入站', '地铁出站'])].copy()

# 严格按照卡号和交易时间排序
df_metro = df_metro.sort_values(by=['card_no', 'deal_date'])

# 利用 shift 把“下一条记录”的信息平移到“当前行”的后面
# 这样每一行就能同时看到自己和自己的下一个动作
df_metro['next_deal_type'] = df_metro.groupby('card_no')['deal_type'].shift(-1)
df_metro['next_station'] = df_metro.groupby('card_no')['station'].shift(-1)
df_metro['next_time'] = df_metro.groupby('card_no')['deal_date'].shift(-1)

# 筛选出配对，当前是“入站”，且下一次紧接着是“出站”
valid_trips = df_metro[
    (df_metro['deal_type'] == '地铁入站') &
    (df_metro['next_deal_type'] == '地铁出站')
].copy()

#  整理列名，对齐后续的代码格式
valid_trips = valid_trips.rename(columns={
    'station': 'station_in',
    'next_station': 'station_out',
    'deal_date': 'in_time',
    'next_time': 'out_time'
})

# 计算时长并清洗
valid_trips['duration_sec'] = (valid_trips['out_time'] - valid_trips['in_time']).dt.total_seconds()

# 过滤：时间在1分钟到24小时之间，且入站不等于出站，且剔除空站名
trips = valid_trips[
    (valid_trips['duration_sec'] > 60) &
    (valid_trips['duration_sec'] < 24 * 3600) &
    (valid_trips['station_in'] != valid_trips['station_out']) &
    (valid_trips['station_in'].notna()) &
    (valid_trips['station_out'].notna())
]
# 使用 pandas 统计每个 OD 对的人数（用于带着权重加入之后的节点）
trip_counts = trips.groupby(['station_in', 'station_out']).size().reset_index(name='passenger_count')
# 计算全量总流向人数（用于初始化根节点）
total_flow = trip_counts['passenger_count'].sum()

# 提取唯一的 OD 对并清理站名后缀
unique_trips = trips[['station_in', 'station_out']].drop_duplicates().copy()
unique_trips['station_in'] = unique_trips['station_in'].str.replace('站', '')
unique_trips['station_out'] = unique_trips['station_out'].str.replace('站', '')


print(f"清洗后得到的有效行程记录数: {len(trips)}")
print(f"提取的唯一 OD 对数量: {len(unique_trips)}")

# 记得清理站名，防止带“站”字匹配不到
unique_trips['station_in'] = unique_trips['station_in'].str.replace('站', '')
unique_trips['station_out'] = unique_trips['station_out'].str.replace('站', '')

# 这里此时已经清理得只剩下入站&出站对了
print(unique_trips.head())
print(unique_trips.info())


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

class TrieNode:
    __slots__ = ['location_id', 'count', 'noisy_count', 'epsilon', 'children']
    def __init__(self, location_id=None, epsilon=0.0):
        self.location_id = location_id  # 车站编号 (Root 可为 None)
        self.count = 0                  # 经过该路径的真实人数
        self.noisy_count = 0            # 加噪后的人数 (初始化为 0)
        self.epsilon = epsilon          # 该节点分配到的隐私预算
        self.children = {}              # 子节点字典: {id: TrieNode对象}

    def __repr__(self):
        return f"Node({self.location_id}, count={self.count})"

class TrajectoryTrie:
    def __init__(self, max_height, total_trajectories):
        self.max_height = max_height  # 树的最大高度 H
        # 初始化根节点，Count 为总轨迹数
        self.root = TrieNode(location_id="Root")
        self.root.count = total_trajectories

    def insert(self, trajectory, count=1): # 增加 count 参数，默认为 1
        """
        插入单条轨迹及其对应的乘客权重
        """
        current_node = self.root

        for i, loc_id in enumerate(trajectory):
            if i >= self.max_height:
                break

            if loc_id not in current_node.children:
                current_node.children[loc_id] = TrieNode(location_id=loc_id)

            # 关键修改：不再是 +1，而是累加这批路径的真实人数
            current_node = current_node.children[loc_id]
            current_node.count += count

    # 为树的每一层/每个节点分配隐私预算

    def _get_all_leaves(self, node):
        """辅助函数：获取节点 i 下属的所有叶子节点"""
        if not node.children:
            return [node]
        leaves = []
        for child in node.children.values():
            leaves.extend(self._get_all_leaves(child))
        return leaves

    def _allocate(self, i, total_epsilon):
        if not i.children:
            i.epsilon = total_epsilon
            return

        for child in i.children.values():
            self._allocate(child, total_epsilon)

        sum_val = 0
        leaves = self._get_all_leaves(i)
        for leaf in leaves:
            # 加上极小值防止除零
            sum_val += total_epsilon / (leaf.epsilon ** 3 + 1e-10)

        children_count = len(i.children)


        # 伪代码中的 i.count 应该是该节点的权重。
        # 如果直接用 140万，数字太大, 使用该节点人数占总人数的比例。
        weight = i.count / self.root.count

        i.epsilon = weight * (children_count / (sum_val ** (1 / 3) + 1e-10))

    def _normalize(self, i, coef):
        # 步骤 18: 这里的 coef 应该是用来把“权重”缩放到“0-1预算空间”的比例
        i.epsilon *= coef

        if i.children:
            for child in i.children.values():
                self._normalize(child, coef)

    def budget_allocation_workflow(self, total_epsilon):
        # 计算权重
        self._allocate(self.root, total_epsilon)

        # 计算修正系数：我们希望 Root 到任意叶子的路径和为 total_epsilon
        # 简单做法：先算一下目前 root 这一条最长路径加起来是多少
        current_path_sum = self._get_path_sum(self.root)

        # 计算缩放系数，让路径总和回归到 total_epsilon
        final_coef = total_epsilon / (current_path_sum + 1e-10)

        self._normalize(self.root, final_coef)

    def _get_path_sum(self, node):
        """辅助函数：沿着第一条路径算一下当前的预算总和"""
        if not node.children:
            return node.epsilon
        first_child = list(node.children.values())[0]
        return node.epsilon + self._get_path_sum(first_child)

    # 给树状图加入隐私噪声,修剪树枝（如果需要加入噪声的人数少于阈值）
    def apply_noise_and_prune(self, k, b):
        """
        实施 Algorithm 1 中的步骤 4-11：逐层加噪与剪枝
        k, b: 阈值参数
        """
        # 从根节点开始递归（根节点 lv=1，但在 DP 中通常从其子节点开始加噪）
        self._process_node_noise(self.root, level=1, k=k, b=b)

    def _process_node_noise(self, current_node, level, k, b):
        # 计算当前层级的隐私阈值 theta_lv
        theta_lv = k * (level ** -1) + b

        # 获取所有待处理的子节点 ID（使用 list 拷贝，因为循环中可能删除元素）
        child_ids = list(current_node.children.keys())

        for cid in child_ids:
            child = current_node.children[cid]

            # 注入拉普拉斯噪声
            # 噪声尺度为 1/epsilon_i
            noise = np.random.laplace(0, 1 / child.epsilon)
            child.noisy_count = child.count + noise

            # 剪枝逻辑 (对应伪代码步骤 8 BuildChildTree 的前置检查)
            if child.noisy_count < theta_lv:
                # 如果加噪后人数低于阈值，直接抹除该分支
                del current_node.children[cid]
            else:
                # 如果通过阈值，则递归处理下一层
                if level < self.max_height:
                    self._process_node_noise(child, level + 1, k, b)

    def get_sanitized_data(self, node=None, path=None):
        """
        输出处理后的数据集 (对应伪代码步骤 12)
        """
        if node is None:
            node = self.root
            path = []

        results = []
        for cid, child in node.children.items():
            current_path = path + [cid]
            # 记录当前路径及其安全计数
            results.append({
                "path": " -> ".join(current_path),
                "count": round(child.noisy_count, 2)
            })
            # 递归获取子路径
            results.extend(self.get_sanitized_data(child, current_path))
        return results

"""
# 这里是一些简单的测试逻辑，下面的主测试逻辑不要乱动
# 将树的最高高度设置为50,避免噪声过大
H = 50
# 计算轨迹的数量
total_count = unique_trips.shape[0]
trie = TrajectoryTrie(max_height=H, total_trajectories=total_count)
print(total_count)

# 为减少重复计算的开销，在此处加入缓存机制
path_cache = {}

for row in unique_trips.itertuples(index=False):
    pair = (row.station_in, row.station_out)

    # 如果这对路径之前算过，直接从缓存拿
    if pair not in path_cache:
        path_cache[pair] = infer_trajectory(pair[0], pair[1])

    trajectory = path_cache[pair]
    trie.insert(trajectory)
"""

# --- 数据预处理：聚合 OD 对人数 ---
# 1. 统计每个 OD 对出现的次数（即该路径的真实乘客数）
trip_counts = trips.groupby(['station_in', 'station_out']).size().reset_index(name='passenger_count')

# 2. 清理站名后缀，确保与图数据库/推断逻辑一致
trip_counts['station_in'] = trip_counts['station_in'].str.replace('站', '')
trip_counts['station_out'] = trip_counts['station_out'].str.replace('站', '')

# 3. 计算全量总流向人数（用于初始化根节点）
total_flow = trip_counts['passenger_count'].sum()

# --- 初始化阶段 ---
TOTAL_EPSILON = 1.0  # 总隐私预算
H = 20  # 树高度限制（深圳地铁路径通常在 20 站以内，设太大会稀释预算）
K, B = 5.0, 10  # 剪枝阈值参数（因为现在 count 变大了，K 和 B 也可以适当调大）

# 创建树，传入真正的总人数
trie = TrajectoryTrie(max_height=H, total_trajectories=total_flow)

# --- 核心步骤：带权重插入数据 ---
print(f"正在构建前缀树，总行程数: {total_flow}...")
path_cache = {}

for row in trip_counts.itertuples(index=False):
    pair = (row.station_in, row.station_out)
    weight = row.passenger_count  # 该路径的真实人数

    # 获取推断路径（带缓存优化）
    if pair not in path_cache:
        path_cache[pair] = infer_trajectory(pair[0], pair[1])

    # 带权重插入：路径上的每个车站 node.count 都会增加 weight
    trie.insert(path_cache[pair], count=weight)

print(f"建树完成！根节点承载总人数: {trie.root.count}")
print(f"原始节点总数（加噪前）: {len(trie.get_sanitized_data())}")

# --- 差分隐私计算阶段 ---

# 分配隐私预算 (使用你类中的权重分配逻辑)
trie.budget_allocation_workflow(total_epsilon=TOTAL_EPSILON)


# 验证预算守恒
def check_epsilon_sum(node, current_sum=0):
    if not node.children:
        print(f"路径末端预算总和: {current_sum + node.epsilon:.4f} (预期应接近 {TOTAL_EPSILON})")
        return
    first_child = list(node.children.values())[0]
    check_epsilon_sum(first_child, current_sum + node.epsilon)


print("--- 预算分配验证 ---")
check_epsilon_sum(trie.root)

# 执行加噪与剪枝
    # 注意：现在的 count 很大，K=5, B=10 意味着如果加噪后人数少于约 15 人，该分支会被切掉
trie.apply_noise_and_prune(k=K, b=B)

# --- 输出与对比 ---
sanitized_results = trie.get_sanitized_data()
print(f"--- 处理后数据展示 (前20条路径) ---")
# 按人数降序排列，看看热门路径加噪后的样子
sorted_results = sorted(sanitized_results, key=lambda x: x['count'], reverse=True)

for item in sorted_results[:20]:
    print(f"路径: {item['path']} | 加噪后人数: {item['count']}")









