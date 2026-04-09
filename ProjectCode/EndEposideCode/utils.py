import matplotlib.pyplot as plt
import pytrie
import pandas as pd
from pathlib import Path
import networkx as nx

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


# --- 4. 路径推断函数 (逻辑保持不变) ---
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
data_path = Path(__file__).parent / "data" / "1_14.csv"
data = pd.read_csv(data_path)
print(data.info())
data = data.dropna()
print(data.info())
print(data.head())
print(data.describe())
print(data["company_name"].unique())

# 转换时间并排序（确保同一张卡的记录按先后顺序排列）
data['deal_date'] = pd.to_datetime(data['deal_date'])

# 进行出入站匹配，拆分相关的数据表
# 预处理
# 拆表
ins_raw = data[data['deal_type'] == '地铁入站'].copy()
outs_raw = data[data['deal_type'] == '地铁出站'].copy()

# 排序并重命名时间列
ins = ins_raw.sort_values('deal_date').rename(columns={'deal_date': 'in_time'})
outs = outs_raw.sort_values('deal_date').rename(columns={'deal_date': 'out_time'})

# 使用 merge_asof 关联
trips = pd.merge_asof(
    ins,
    outs,
    left_on='in_time',
    right_on='out_time',
    by='card_no',
    direction='forward',
    suffixes=('_in', '_out')
)

# 清洗
trips = trips.dropna(subset=['station_out'])
trips['duration_sec'] = (trips['out_time'] - trips['in_time']).dt.total_seconds()

# 过滤：时间在1分钟到5小时之间，且入站不等于出站
trips = trips[(trips['duration_sec'] > 60) &
              (trips['duration_sec'] < 5 * 3600) &
              (trips['station_in'] != trips['station_out'])]

print(trips.head())
print(trips.info())

# 提取唯一的 OD 对，减少重复计算
unique_trips = trips[['station_in', 'station_out']].drop_duplicates()

# 记得清理站名，防止带“站”字匹配不到
unique_trips['station_in'] = unique_trips['station_in'].str.replace('站', '')
unique_trips['station_out'] = unique_trips['station_out'].str.replace('站', '')

# 找出哪些行程导致了空路径
unique_trips['path'] = unique_trips.apply(
    lambda x: infer_trajectory(x['station_in'], x['station_out']), axis=1
)

fail_trips = unique_trips[unique_trips['path'].map(len) == 0]
print("路径推断失败的样本：")
print(fail_trips)






