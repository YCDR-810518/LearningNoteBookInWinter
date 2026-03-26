from matplotlib import pyplot as plt
import networkx as nx
import numpy as np

def plot_results(W, eps, eps_max, config, edges):
    """
    复现论文 Figure 2 & Figure 3 的可视化函数
    """
    N = config.N
    # 创建画布：左边画拓扑图，右边画柱状图
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))

    # --- 加权拓扑图 (Figure 2) ---
    G = nx.Graph()
    G.add_nodes_from(range(1, N + 1))

    # 添加边：只画权重显著的边 (论文阈值 10^-4)
    for i in range(N):
        for j in range(i + 1, N):
            if W[i, j] > 1e-4:
                G.add_edge(i + 1, j + 1, weight=W[i, j])

    pos = nx.spring_layout(G, seed=42)  # 固定布局方便对比

    # 节点大小：根据 eps 缩放 (eps 越小，圆圈越小)
    node_sizes = eps * 2000
    nx.draw_networkx_nodes(G, pos, node_size=node_sizes, node_color='skyblue', ax=ax1, edgecolors='black')
    nx.draw_networkx_labels(G, pos, font_size=10, ax=ax1)

    # 连线粗细：根据权重 W 缩放
    weights = [G[u][v]['weight'] * 5 for u, v in G.edges()]
    nx.draw_networkx_edges(G, pos, width=weights, edge_color='gray', alpha=0.7, ax=ax1)

    ax1.set_title(f"Co-designed Topology (e_R={config.e_R})")
    ax1.axis('off')

    # --- 隐私参数对比柱状图 (Figure 3) ---
    indices = np.arange(1, N + 1)
    bar_width = 0.35

    # 画出上限作为背景参考
    ax2.bar(indices - bar_width / 2, eps_max, bar_width, label='Max Epsilon (Constraint)', color='lightgray', alpha=0.5)
    # 画出实际优化的 eps
    ax2.bar(indices + bar_width / 2, eps, bar_width, label='Optimal Epsilon', color='teal')

    ax2.set_xlabel('Agent Index')
    ax2.set_ylabel('Epsilon (Privacy Level)')
    ax2.set_title(f'Privacy Parameters (e_R={config.e_R})')
    ax2.set_xticks(indices)
    ax2.legend()
    ax2.grid(axis='y', linestyle='--', alpha=0.7)

    plt.tight_layout()
    plt.show()


