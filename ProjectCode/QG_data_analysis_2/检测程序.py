import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# 1. 加载数据
df = pd.read_csv('QG_test.csv', header=None, low_memory=False)
# 提取 100 行 x 10000 列的特征数据
data = df.iloc[1:101, :10000].apply(pd.to_numeric, errors='coerce').fillna(0).values
labels = df.iloc[1:101, 10000].astype(int).values

# 2. 设置画布
fig, ax = plt.subplots(figsize=(12, 6))
ax.set_xlim(0, np.max(data))  # X轴为数值（位置）
ax.set_ylim(-2, 2)  # Y轴仅做分类展示，1 在上，-1 在下
ax.set_title("Collaborative Design Particle System (Time: 0ms)")
ax.set_xlabel("Value (Position)")
ax.set_yticks([1, -1])
ax.set_yticklabels(['Label 1 (Normal)', 'Label -1 (Anomaly)'])

# 初始化两组粒子
# s是大小，alpha是透明度
scat_pos = ax.scatter([], [], c='green', s=30, label='Normal (1)', alpha=0.6)
scat_neg = ax.scatter([], [], c='red', s=30, label='Anomaly (-1)', alpha=0.6)
ax.legend()


# 3. 动画更新函数
def update(frame):
    # 获取当前毫秒（列）的所有行数值
    current_values = data[:, frame]

    # 筛选 1 和 -1 的位置
    pos_x = current_values[labels == 1]
    neg_x = current_values[labels == -1]

    # 设置 Y 轴位置（稍微加点随机抖动 jitter，防止粒子重叠看不清数量）
    pos_y = np.ones(len(pos_x)) + np.random.uniform(-0.2, 0.2, len(pos_x))
    neg_y = -np.ones(len(neg_x)) + np.random.uniform(-0.2, 0.2, len(neg_x))

    # 更新粒子位置
    scat_pos.set_offsets(np.c_[pos_x, pos_y])
    scat_neg.set_offsets(np.c_[neg_x, neg_y])

    ax.set_title(f"Collaborative Design Particle System (Time: {frame}ms)")
    return scat_pos, scat_neg


# 4. 创建动画
# frames=1000 仅演示前1000ms，全量请设为 10000
# interval=20 代表每帧间隔 20ms
ani = FuncAnimation(fig, update, frames=1000, interval=20, blit=True)

plt.show()

# 如果需要保存为 mp4
# ani.save('collaboration_dynamic.mp4', writer='ffmpeg', fps=30)