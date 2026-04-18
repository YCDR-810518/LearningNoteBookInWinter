import matplotlib.pyplot as plt
import networkx as nx


def plot_trie_top_n(trie, max_level=5):
    """
    绘制前缀树的前 N 层。
    注意：这里的 trie 是你在主程序中实例化并 insert 数据后的 TrajectoryTrie 对象。
    """
    T = nx.DiGraph()

    # 递归遍历树，构建适合 NetworkX 绘图的 DiGraph
    def build_nx_tree(node, current_level, parent_id=None):
        if current_level > max_level:
            return

        # 极其重要：树的不同分支可能有同名节点(比如不同路线都经过'车公庙')
        # 必须用内存地址 id(node) 保证节点的唯一性，否则图会首尾相接变成环
        node_id = f"{node.location_id}_{id(node)}"

        # subset 属性用于后续的 multipartite_layout 分层排版
        T.add_node(node_id, label=str(node.location_id), subset=current_level)

        if parent_id:
            T.add_edge(parent_id, node_id)

        for child in node.children.values():
            build_nx_tree(child, current_level + 1, node_id)

    print(f"正在提取树的前 {max_level} 层数据...")
    build_nx_tree(trie.root, 0)

    # 如果前5层节点还是太多，建议对子节点进行切片限制
    print(f"提取完成，共获取 {T.number_of_nodes()} 个节点。")

    plt.figure(figsize=(20, 10))

    # 核心排版：利用 multipartite_layout 按层级(subset)横向排布
    pos = nx.multipartite_layout(T, subset_key="subset", align="horizontal")

    # 提取标签
    labels = nx.get_node_attributes(T, 'label')

    # 绘制
    nx.draw(T, pos,
            node_size=800,
            node_color='#50E3C2',
            edge_color='gray',
            with_labels=True,
            labels=labels,
            font_size=9,
            font_family='SimHei',
            arrows=False)  # Trie的流向很明确，省略箭头会让画面更干净

    plt.title(f"Trajectory Trie Structure (Top {max_level} Levels)", fontsize=16)
    plt.tight_layout()
    plt.show()


def plot_subway_network(graph):
    plt.figure(figsize=(16, 12))

    # 使用 kamada_kawai_layout 能让网状图节点分布更均匀整齐
    print("正在计算网络图布局，请稍候...")
    pos = nx.kamada_kawai_layout(graph)

    # 绘制节点和边
    nx.draw_networkx_nodes(graph, pos, node_size=30, node_color='skyblue', alpha=0.8)
    nx.draw_networkx_edges(graph, pos, edge_color='gray', alpha=0.5)

    # 考虑到节点太多，名字重叠会很乱，这里只给少部分重点换乘站打标签
    # 提取换乘站（度数较高的节点）
    transfer_stations = [n for n, d in graph.degree() if d > 2]
    labels = {n: n.split('_')[0] for n in transfer_stations}  # 去掉线路后缀，只保留站名

    nx.draw_networkx_labels(graph, pos, labels=labels, font_size=8, font_family='SimHei')

    plt.title("Shenzhen Subway Network Graph", fontsize=16, fontweight='bold')
    plt.axis('off')  # 隐藏坐标轴
    plt.tight_layout()
    plt.show()
