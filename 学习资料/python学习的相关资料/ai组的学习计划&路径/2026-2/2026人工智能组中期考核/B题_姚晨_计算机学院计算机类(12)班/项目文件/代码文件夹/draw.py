from matplotlib import pyplot as plt
import networkx as nx
import numpy as np
# 从主函数加载类
from PFC_main import SimulationConfig, GraphTopology, ACSOptimizer

def plot_results(W, eps, eps_max, config):
    """
    复现论文 Figure 2 & Figure 3 的可视化函数
    连线上标注具体的权重值
    """
    N = config.N
    # 创建画布：左边画拓扑图，右边画柱状图
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(18, 7)) # 稍微调宽一点，容纳标注

    # 左图：加权拓扑图 (Figure 2)
    G = nx.Graph()
    G.add_nodes_from(range(1, N + 1))

    # 添加边：只画权重显著的边 (论文阈值 10^-4)
    # 并将具体的权重值塞进 'label' 属性里，方便后面画图调用
    for i in range(N):
        for j in range(i + 1, N):
            weight_val = W[i, j]
            if weight_val > 1e-4:
                G.add_edge(i + 1, j + 1, weight=weight_val, label=f"{weight_val:.2f}")

    # 使用 fixed layout 方便对比，spring_layout 的 seed 必须固定
    pos = nx.spring_layout(G, seed=42)

    # 根据 eps 缩放 (eps 越小，圆圈越小)
    node_sizes = eps*eps * 20000
    nx.draw_networkx_nodes(G, pos, node_size=node_sizes, node_color='skyblue', ax=ax1, edgecolors='black')
    nx.draw_networkx_labels(G, pos, font_size=10, ax=ax1, font_family='sans-serif')

    # 画连线，根据权重 W 缩放粗细
    weights = [G[u][v]['weight'] * 6 for u, v in G.edges()] # 稍微加粗一点
    nx.draw_networkx_edges(G, pos, width=weights, edge_color='gray', alpha=0.5, ax=ax1)

    # 在连线上加入具体的权重值标注
    # nx.get_edge_attributes 用于获取在 add_edge 时设置的 'label'

    edge_labels = nx.get_edge_attributes(G, 'label')
    nx.draw_networkx_edge_labels(
        G, pos,
        edge_labels=edge_labels,
        font_size=8,          # 标注字体小一点，防止拥挤
        font_color='black',   # 标注颜色
        font_family='sans-serif',
        label_pos=0.5,        # 标注在连线中间
        ax=ax1,
        rotate=False         # 数字垂直横向
    )

    ax1.set_title(f"Co-designed Topology (Tolerance $e_R$={config.e_R})\nNode Size $\propto \epsilon$, Edge Width $\propto W$")
    ax1.axis('off')
    ax1.margins(0.1) # 增加边缘边距，防止数字和节点溢出

    # 右图：隐私参数对比柱状图 (Figure 3)
    # 这部分逻辑不变
    indices = np.arange(1, N + 1)
    bar_width = 0.35

    ax2.bar(indices - bar_width / 2, eps_max, bar_width, label='Max Epsilon (Constraint)', color='lightgray', alpha=0.5)
    ax2.bar(indices + bar_width / 2, eps, bar_width, label='Optimal Epsilon', color='teal')

    ax2.set_xlabel('Agent Index')
    ax2.set_ylabel('Epsilon (Privacy Level)')
    ax2.set_title(f'Privacy Parameters (e_R={config.e_R})')
    ax2.set_xticks(indices)
    ax2.legend()
    ax2.grid(axis='y', linestyle='--', alpha=0.7)

    plt.tight_layout()
    # 保存图片为高质量 JPG，dpi=900 适合打印
    plt.savefig(f"Fig_{config.e_R}e_R.jpg", dpi=900, facecolor='w', edgecolor='black')
    plt.show()

# 多项数据的对比图描述

def run_comparison_experiment(eps_max, edges):
    # 定义实验的误差梯度
    e_R_list = [8.0, 16.0, 64.0]
    results = []

    # 初始化基础环境
    print("开始运行对比图：e_R = [8, 16, 64] ...")

    for er in e_R_list:
        print(f"\n[实验中] 正在计算 e_R = {er} 的最优解...")
        config = SimulationConfig(e_R=er, B=6.0, epsilon_max=eps_max)
        topology = GraphTopology(N=config.N, edges_list=edges)
        optimizer = ACSOptimizer()

        W_opt, y_opt, eps_opt, _ = optimizer.run_acs(config, topology, max_iter=15)

        if eps_opt is not None:
            results.append({
                'e_R': er,
                'W': W_opt,
                'y': y_opt,
                'eps': eps_opt
            })

    # --- 开始绘制全套对比图 (Figure 3 Style) ---
    fig, axes = plt.subplots(1, 3, figsize=(18, 5), sharey=True)
    indices = np.arange(1, 11)
    bar_width = 0.35

    for i, res in enumerate(results):
        ax = axes[i]
        # 背景：隐私上限
        ax.bar(indices - bar_width / 2, eps_max, bar_width, label='Upper Bound', color='lightgray', alpha=0.4)
        # 前景：当前 e_R 下的最优 eps
        ax.bar(indices + bar_width / 2, res['eps'], bar_width, label=f'Opt (e_R={res["e_R"]})', color='teal')

        ax.set_title(f"Tolerance $e_R$ = {res['e_R']}\nAvg $\epsilon$: {np.mean(res['eps']):.3f}")
        ax.set_xlabel('Agent Index')
        if i == 0: ax.set_ylabel('Privacy Level $\epsilon$')
        ax.set_xticks(indices)
        ax.legend()

    plt.suptitle("Privacy-Accuracy Trade-off Analysis", fontsize=16, y=1.05)
    plt.tight_layout()
    plt.savefig("figure5.jpg",dpi=300,facecolor='w', edgecolor='black')
    plt.show()

