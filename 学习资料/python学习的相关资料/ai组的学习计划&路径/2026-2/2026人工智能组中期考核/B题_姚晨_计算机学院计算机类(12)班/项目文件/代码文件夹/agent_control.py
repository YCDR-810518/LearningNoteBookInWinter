import json
import PFC_main as pfc
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation



# 下面这些是在没有误差注入下的
def simulate_formation(W, target_coords, config, steps=300, dt=0.1):
    """
    极简阵型演化模拟
    W: 优化后的权重矩阵 (N x N)
    target_coords: 目标阵型的坐标 (N x 2)
    """
    N = config.N
    # 先测试，后面会替换为所提供的初始位置
    current_pos = None
    # 提供的初始位置
    with open("initial_position.json", "r") as f:
        initial_position = json.load(f)
        current_pos = np.array(initial_position["initial_positions"])
        print(current_pos)

    # 用于记录轨迹
    traj = [current_pos.copy()]

    # 2. 迭代演化
    for _ in range(steps):
        vel = np.zeros((N, 2))
        for i in range(N):
            for j in range(N):
                if W[i, j] > 1e-4:
                    # 计算相对位置误差
                    actual_diff = current_pos[i] - current_pos[j]
                    desired_diff = target_coords[i] - target_coords[j]
                    # 速度 = - 权重 * 误差
                    vel[i] -= W[i, j] * (actual_diff - desired_diff)

        # 更新位置
        current_pos += vel * dt
        traj.append(current_pos.copy())

    return np.array(traj)



"""
    使用 plt中的Animation 制作动图
    traj: 模拟产生的轨迹数据 (steps, N, 2)
    W: 权重矩阵，用于绘制节点间的连线
"""
def animate_formation(traj, W, config, interval=50,filename='agent_control.mp4'):

    N = config.N
    fig, ax = plt.subplots(figsize=(8, 8))

    # 设置坐标轴范围（根据轨迹自动调整，留一点边距）
    all_x, all_y = traj[:, :, 0], traj[:, :, 1]
    ax.set_xlim(np.min(all_x) - 1, np.max(all_x) + 1)
    ax.set_ylim(np.min(all_y) - 1, np.max(all_y) + 1)
    ax.set_title("Real-time Formation Evolution")
    ax.grid(True, linestyle='--', alpha=0.6)

    # 初始化绘图对象
    # 轨迹线
    lines = [ax.plot([], [], alpha=0.3, label=f'Agent {i + 1}' if i < 3 else "")[0] for i in range(N)]
    # 当前点位置
    scat = ax.scatter([], [], s=100, edgecolors='k', zorder=3)
    # 节点间的连线（只连权重显著的边）
    connection_lines = []
    for i in range(N):
        for j in range(i + 1, N):
            if W[i, j] > 1e-3:
                conn, = ax.plot([], [], color='gray', alpha=0.2, lw=W[i, j] * 2)
                connection_lines.append((i, j, conn))

    def init():
        for line in lines:
            line.set_data([], [])
        for _, _, conn in connection_lines:
            conn.set_data([], [])
        scat.set_offsets(np.empty((0, 2)))
        return lines + [scat] + [c[2] for c in connection_lines]

    def update(frame):
        # 更新每个智能体的轨迹
        for i in range(N):
            lines[i].set_data(traj[:frame, i, 0], traj[:frame, i, 1])

        # 更新当前点位置
        current_pos = traj[frame]
        scat.set_offsets(current_pos)

        # 更新节点间的物理连线
        for i, j, conn in connection_lines:
            conn.set_data([current_pos[i, 0], current_pos[j, 0]],
                          [current_pos[i, 1], current_pos[j, 1]])

        return lines + [scat] + [c[2] for c in connection_lines]

    # 创建动画
    ani = animation.FuncAnimation(
        fig, update, frames=len(traj), init_func=init,
        interval=interval, blit=True, repeat=False
    )

    plt.legend(loc='upper right')

    # 用来保存动图，先保存，再展示，否则会阻塞窗口
    ani.save(filename, writer='ffmpeg')

    plt.show()



# 根据论文写的作为初始边
with open("initial_edges.json", "r") as f:
    graph_topology = json.load(f)
    graph_topology = np.array(graph_topology['initial_edges'[:]])
    edges = np.array(graph_topology)
    eps_max = np.array([0.4, 0.9, 0.55, 0.35, 0.8, 0.45, 0.7, 0.5, 0.52, 0.58])
    print("正在初始化环境配置...")

    # 测试参数：e_R = 16, B = 6
    config = pfc.SimulationConfig(e_R=16.0, B=6.0, epsilon_max=eps_max)
    topology = pfc.GraphTopology(N=config.N, edges_list=edges)
    optimizer = pfc.ACSOptimizer()

    # 启动！
    W_opt, y_opt, eps_opt, history = optimizer.run_acs(config, topology)
    # --- 测试运行 ---
    if eps_opt is not None:
        # 假设一个简单的圆形阵型作为目标坐标
        theta = np.linspace(0, 2 * np.pi, 10, endpoint=False)

        circle_targets = np.column_stack([np.cos(theta), np.sin(theta)]) * 4

        # 模拟
        trajectories = simulate_formation(W_opt, circle_targets, config)
        # 画图
        animate_formation(trajectories, W_opt, config)

# 下面这些是在没有误差注入下的
def simulate_formation(W, target_coords, config, steps=300, dt=0.1):
    """
    极简阵型演化模拟
    W: 优化后的权重矩阵 (N x N)
    target_coords: 目标阵型的坐标 (N x 2)
    """
    N = config.N
    # 先测试，后面会替换为所提供的初始位置
    current_pos = None
    # 提供的初始位置
    with open("initial_position.json", "r") as f:
        initial_position = json.load(f)
        current_pos = np.array(initial_position["initial_positions"])
        print(current_pos)

    # 用于记录轨迹
    traj = [current_pos.copy()]

    # 2. 迭代演化
    for _ in range(steps):
        vel = np.zeros((N, 2))
        for i in range(N):
            for j in range(N):
                if W[i, j] > 1e-4:
                    # 计算相对位置误差
                    actual_diff = current_pos[i] - current_pos[j]
                    desired_diff = target_coords[i] - target_coords[j]
                    # 速度 = - 权重 * 误差
                    vel[i] -= W[i, j] * (actual_diff - desired_diff)

        # 更新位置
        current_pos += vel * dt
        traj.append(current_pos.copy())

    return np.array(traj)

"""
用于指定特定的agent对全图进行注入攻击
dt:时间步长
u_attack:注入的误差大小
config:相关的参数大小
target_coords:最终要形成的图案形状
"""
def simulate_formation_with_attack(W, target_coords, config, u_attack=0.1, steps=1000, dt=0.05):
    N = config.N
    # 加载初始位置
    with open("initial_position.json", "r") as f:
        data = json.load(f)
        current_pos = np.array(data["initial_positions"])

    traj = [current_pos.copy()]

    for _ in range(steps):
        vel = np.zeros((N, 2))
        for i in range(N):
            for j in range(N):
                if W[i, j] > 1e-4:
                    actual_diff = current_pos[i] - current_pos[j]
                    desired_diff = target_coords[i] - target_coords[j]
                    vel[i] -= W[i, j] * (actual_diff - desired_diff)

            # 注入攻击
            # 假设 Agent 1 发生故障，注入 X 方向的恒定偏差
            if i == 0:
                vel[i] += np.array([u_attack, 0])

        current_pos += vel * dt
        traj.append(current_pos.copy())

    # 计算稳态误差 e_ss: 最后时刻实际相对距离与目标的平均偏差
    final_pos = traj[-1]
    errors = []
    for i in range(N):
        for j in range(N):
            if W[i, j] > 1e-4:
                err = np.linalg.norm((final_pos[i] - final_pos[j]) - (target_coords[i] - target_coords[j]))
                errors.append(err)

    e_ss = np.mean(errors)
    return np.array(traj), e_ss

"""
对比注入攻击前后的区别
启动多轮对比流程，观察其稳定性
epsilon_scales:这个变量标定了不同的隐私预算水平
"""
def run_compare_task(edges):
    u_attack_list = np.linspace(0, 2.0, 5)
    epsilon_scales = [0.1, 0.5, 1.0, 10.0]

    # 显式创建一个 Figure 专门画曲线图
    fig_curve, ax_curve = plt.subplots(figsize=(10, 6))

    for eps_val in epsilon_scales:
        current_eps_max = np.ones(10) * eps_val
        config = pfc.SimulationConfig(e_R=16.0, B=10.0, epsilon_max=current_eps_max)
        topology = pfc.GraphTopology(N=config.N, edges_list=edges)
        optimizer = pfc.ACSOptimizer()
        W_opt, _, _, _ = optimizer.run_acs(config, topology)

        if W_opt is None: continue

        ess_values = []
        for ua in u_attack_list:
            _, e_ss = simulate_formation_with_attack(W_opt, circle_targets, config, u_attack=ua)
            ess_values.append(e_ss)

        # 使用 ax_curve 明确指定画在曲线图上
        ax_curve.plot(u_attack_list, ess_values, 'o-', label=f'eps={eps_val}')

        # 生成动图
        traj, _ = simulate_formation_with_attack(W_opt, circle_targets, config, u_attack=1.0)
        animate_formation(traj, W_opt, config, filename=f'attack_eps_control_{eps_val}.mp4')

    # 在 ax_curve 上设置细节
    ax_curve.set_title("Steady-state Error $e_{ss}$ vs Attack Intensity $u_{attack}$")
    ax_curve.set_xlabel("$u_{attack}$")
    ax_curve.set_ylabel("$e_{ss}$")
    ax_curve.legend()  # 这次肯定能找到了
    ax_curve.grid(True)

    # 保存并展示曲线图
    fig_curve.savefig("analysis_curve.jpg")
    plt.show()  # 最后统一展示

"""
    使用 plt中的Animation 制作动图
    traj: 模拟产生的轨迹数据 (steps, N, 2)
    W: 权重矩阵，用于绘制节点间的连线
"""
def animate_formation(traj, W, config, interval=50,filename='agent_control.mp4'):

    N = config.N
    fig, ax = plt.subplots(figsize=(8, 8))

    # 设置坐标轴范围（根据轨迹自动调整，留一点边距）
    all_x, all_y = traj[:, :, 0], traj[:, :, 1]
    ax.set_xlim(np.min(all_x) - 1, np.max(all_x) + 1)
    ax.set_ylim(np.min(all_y) - 1, np.max(all_y) + 1)
    ax.set_title("Real-time Formation Evolution")
    ax.grid(True, linestyle='--', alpha=0.6)

    # 初始化绘图对象
    # 轨迹线
    lines = [ax.plot([], [], alpha=0.3, label=f'Agent {i + 1}' if i < 3 else "")[0] for i in range(N)]
    # 当前点位置
    scat = ax.scatter([], [], s=100, edgecolors='k', zorder=3)
    # 节点间的连线（只连权重显著的边）
    connection_lines = []
    for i in range(N):
        for j in range(i + 1, N):
            if W[i, j] > 1e-3:
                conn, = ax.plot([], [], color='gray', alpha=0.2, lw=W[i, j] * 2)
                connection_lines.append((i, j, conn))

    def init():
        for line in lines:
            line.set_data([], [])
        for _, _, conn in connection_lines:
            conn.set_data([], [])
        scat.set_offsets(np.empty((0, 2)))
        return lines + [scat] + [c[2] for c in connection_lines]

    def update(frame):
        # 更新每个智能体的轨迹
        for i in range(N):
            lines[i].set_data(traj[:frame, i, 0], traj[:frame, i, 1])

        # 更新当前点位置
        current_pos = traj[frame]
        scat.set_offsets(current_pos)

        # 更新节点间的物理连线
        for i, j, conn in connection_lines:
            conn.set_data([current_pos[i, 0], current_pos[j, 0]],
                          [current_pos[i, 1], current_pos[j, 1]])

        return lines + [scat] + [c[2] for c in connection_lines]

    # 创建动画
    ani = animation.FuncAnimation(
        fig, update, frames=len(traj), init_func=init,
        interval=interval, blit=True, repeat=False
    )

    plt.legend(loc='upper right')

    # 用来保存动图，先保存，再展示，否则会阻塞窗口
    ani.save(filename, writer='ffmpeg')

    plt.show()



# 根据论文写的作为初始边
with open("initial_edges.json", "r") as f:
    graph_topology = json.load(f)
    graph_topology = np.array(graph_topology['initial_edges'[:]])
    edges = np.array(graph_topology)
    eps_max = np.array([0.4, 0.9, 0.55, 0.35, 0.8, 0.45, 0.7, 0.5, 0.52, 0.58])
    print("正在初始化环境配置...")

    # 测试参数：e_R = 16, B = 6
    config = pfc.SimulationConfig(e_R=16.0, B=6.0, epsilon_max=eps_max)
    topology = pfc.GraphTopology(N=config.N, edges_list=edges)
    optimizer = pfc.ACSOptimizer()

    # 启动！
    W_opt, y_opt, eps_opt, history = optimizer.run_acs(config, topology)
    # --- 测试运行 ---
    if eps_opt is not None:
        # 假设一个简单的圆形阵型作为目标坐标
        theta = np.linspace(0, 2 * np.pi, 10, endpoint=False)

        circle_targets = np.column_stack([np.cos(theta), np.sin(theta)]) * 4

        # 模拟
        trajectories = simulate_formation(W_opt, circle_targets, config)
        # 画图
        animate_formation(trajectories, W_opt, config)

    print("启动错误注入的对比实验")
    run_compare_task(edges)
    print("错误注入实验完成✅，对应的视频/GIF动图在同目录下已经生成")
