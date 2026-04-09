import networkx as nx
import matplotlib.pyplot as plt
import pytrie

G = nx.Graph()


# 定义添加线路的函数（自动计算图片中的分钟差）
def add_line_with_times(graph, stations, start_times, line_name):
    for i in range(len(stations) - 1):
        # 计算两站之间的时间差（分钟）
        t1 = int(start_times[i].split(':')[0]) * 60 + int(start_times[i].split(':')[1])
        t2 = int(start_times[i + 1].split(':')[0]) * 60 + int(start_times[i + 1].split(':')[1])
        duration = t2 - t1

        u = f"{stations[i]}_{line_name}"
        v = f"{stations[i + 1]}_{line_name}"
        graph.add_edge(u, v, weight=duration)


# --- 1号线 (参考图1.jpg) ---
l1_stations = ["罗湖", "国贸", "老街", "大剧院", "科学馆", "华强路", "岗厦", "会展中心", "购物公园", "车公庙"]
l1_times = ["06:30", "06:32", "06:33", "06:36", "06:38", "06:40", "06:43", "06:45", "06:46", "06:51"]
add_line_with_times(G, l1_stations, l1_times, "L1")

# --- 2号线 (参考图2.jpg) ---
l2_stations = ["赤湾", "蛇口港", "海上世界", "后海", "世界之窗", "景田", "福田", "市民中心", "岗厦北", "华强北",
               "大剧院"]
l2_times = ["06:30", "06:32", "06:34", "06:32", "06:31", "06:46", "06:51", "06:53", "06:55", "06:58", "07:02"]
add_line_with_times(G, l2_stations, l2_times, "L2")

# --- 4号线末班车数据 (参考图4.jpg 往福田口岸方向) ---
l4_stations = [
    "清湖", "龙华", "龙胜", "上塘", "红山", "深圳北站",
    "白石龙", "民乐", "上梅林", "莲花北", "少年宫",
    "市民中心", "会展中心", "福民"
]

l4_times = [
    "23:00", "23:02", "23:04", "23:06", "23:08", "23:10",
    "23:12", "23:14", "23:17", "23:19", "23:21",
    "23:23", "23:24", "23:26"
]  # 存在分段首发，故使用末班车数据作为替代
add_line_with_times(G, l4_stations, l4_times, "L4")

# --- 11号线 (参考图11.jpg) ---
l11_stations = ["福田", "车公庙", "红树湾南", "后海", "南山", "前海湾", "宝安", "碧海湾", "机场"]
l11_times = ["06:30", "06:33", "06:38", "06:41", "06:44", "06:30", "06:33", "06:36", "06:42"]
add_line_with_times(G, l11_stations, l11_times, "L11")

# --- 设定换乘惩罚 (统一 8 分钟) ---
transfer_penalty = 8
transfers = [
    ("车公庙", ["L1", "L7", "L9", "L11"]),
    ("福田", ["L2", "L3", "L11"]),
    ("会展中心", ["L1", "L4"]),
    ("大剧院", ["L1", "L2"]),
    ("深圳北站", ["L4", "L5"]),
    ("后海", ["L2", "L11"]),
    ("市民中心", ["L2", "L4"])
]

for station, lines in transfers:
    for i in range(len(lines)):
        for j in range(i + 1, len(lines)):
            u = f"{station}_{lines[i]}"
            v = f"{station}_{lines[j]}"
            G.add_edge(u, v, weight=transfer_penalty)





# 解决中文乱码问题（非常重要，否则节点全是方块）
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

plt.figure(figsize=(15, 10)) # 调大画布，不然节点会挤在一起
nx.draw(G, with_labels=True, node_size=800, font_size=9, node_color='lightblue')
plt.show() # 必须调用这句才能弹出窗口

# 此处让程序自主推断路径，输入起点和终点站名（不带线路信息），输出推断的轨迹
def infer_trajectory(start_station, end_station):
    # 在图中寻找所有属于该站点的虚拟节点
    start_nodes = [n for n in G.nodes() if n.startswith(start_station)]
    end_nodes = [n for n in G.nodes() if n.startswith(end_station)]

    # 寻找最短耗时路径
    best_path = None
    min_weight = float('inf')

    for s in start_nodes:
        for e in end_nodes:
            try:
                path = nx.shortest_path(G, s, e, weight='weight')
                w = nx.shortest_path_length(G, s, e, weight='weight')
                if w < min_weight:
                    min_weight = w
                    best_path = path
            except:
                continue

    # 清洗路径：把 "车公庙_L1" 还原为 "车公庙"，并去重
    clean_trajectory = []
    for p in best_path:
        station_name = p.split('_')[0]
        if not clean_trajectory or clean_trajectory[-1] != station_name:
            clean_trajectory.append(station_name)

    return clean_trajectory
