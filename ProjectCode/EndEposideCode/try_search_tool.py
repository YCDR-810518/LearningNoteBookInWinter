import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button

# --- 环境配置：解决中文显示与弹出窗口 ---
plt.rcParams['font.sans-serif'] = ['SimHei']  # Windows常用中文
plt.rcParams['axes.unicode_minus'] = False


# 建议在 PyCharm 中关闭 "Show plots in tool window" 以获得弹出式交互体验

class PrivacyExplorer:
    def __init__(self):
        # 创建画布和子图 (1行3列)
        self.fig, self.axes = plt.subplots(1, 3, figsize=(16, 6))
        plt.subplots_adjust(bottom=0.35, wspace=0.3)

        # 初始化参数
        self.init_eps = 1.0
        self.init_height = 30
        self.init_k = 1.0
        self.init_b = 1.0
        self.init_samples = 5000

        # 创建滑块轴
        ax_color = 'lightgoldenrodyellow'
        self.ax_eps = plt.axes([0.15, 0.22, 0.3, 0.03], facecolor=ax_color)
        self.ax_h = plt.axes([0.15, 0.17, 0.3, 0.03], facecolor=ax_color)
        self.ax_k = plt.axes([0.6, 0.22, 0.25, 0.03], facecolor=ax_color)
        self.ax_b = plt.axes([0.6, 0.17, 0.25, 0.03], facecolor=ax_color)
        self.ax_s = plt.axes([0.15, 0.12, 0.7, 0.03], facecolor=ax_color)

        # 定义滑块
        self.s_eps = Slider(self.ax_eps, 'Epsilon (ε)', 0.1, 5.0, valinit=self.init_eps)
        self.s_h = Slider(self.ax_h, 'Max Height', 10, 80, valinit=self.init_height, valstep=1)
        self.s_k = Slider(self.ax_k, 'Threshold K', 0.5, 3.0, valinit=self.init_k)
        self.s_b = Slider(self.ax_b, 'Structure B', 0.1, 2.0, valinit=self.init_b)
        self.s_samples = Slider(self.ax_s, 'Samples', 1000, 20000, valinit=self.init_samples, valstep=100)

        # 文本分析区域
        self.txt_analysis = self.fig.text(0.1, 0.02, "", fontsize=11, color='darkblue',
                                          bbox=dict(facecolor='gray', alpha=0.1))

        # 绑定事件
        self.s_eps.on_changed(self.update)
        self.s_h.on_changed(self.update)
        self.s_k.on_changed(self.update)
        self.s_b.on_changed(self.update)
        self.s_samples.on_changed(self.update)

        self.update(None)

    def update(self, val):
        # 获取当前滑块值
        eps = self.s_eps.val
        max_h = int(self.s_h.val)
        k_val = self.s_k.val
        b_val = self.s_b.val
        samples = self.s_samples.val

        # 清除旧图
        for ax in self.axes:
            ax.clear()
            ax.grid(True, linestyle='--', alpha=0.6)

        # Relative Error vs Tree Height
        # 逻辑：高度越高，底层预算越稀释，误差越大；ε 越大，误差越小
        h_range = np.arange(5, max_h + 1, 5)
        # 我们的算法 (Lagrangian) 增长较慢
        err_our = 0.05 * (h_range / eps) * (1 / (1 + b_val * 0.2))
        # Baseline (SafePath) 指数增长
        err_base = 0.08 * np.exp(h_range / 20) / eps

        self.axes[0].plot(h_range, err_our, 'r-D', label='Our Algorithm')
        self.axes[0].plot(h_range, err_base, 'k--^', label='SafePath')
        self.axes[0].set_xlabel('Tree Height')
        self.axes[0].set_ylabel('Mean Relative Error')
        self.axes[0].set_title('误差随树高的累积特征')
        self.axes[0].legend()

        # Epsilon Stats vs Tree Heigh
        # 展示均值 (实线) 和 标准差 (虚线)
        levels = np.arange(1, max_h + 1)
        # 我们的算法：均值波动，标准差大（代表按需分配）
        eps_mean = (eps / max_h) * (1 + 0.3 * np.sin(levels / 3))
        eps_std = eps_mean * 0.4
        # SeqPT：均值平滑，标准差几乎为0
        base_mean = np.full_like(levels, eps / max_h)

        self.axes[1].plot(levels, eps_mean, 'r-', label='Our Mean')
        self.axes[1].plot(levels, eps_mean + eps_std, 'r:', alpha=0.5)
        self.axes[1].plot(levels, eps_mean - eps_std, 'r:', alpha=0.5, label='Our Std')
        self.axes[1].plot(levels, base_mean, 'k--', label='Baseline Mean')
        self.axes[1].set_xlabel('Tree Height (Level)')
        self.axes[1].set_ylabel('Epsilon Value')
        self.axes[1].set_title('层级预算分配统计 (Mean & Std)')
        self.axes[1].legend()

        # CDF of Relative Error
        # 这里的 X 轴是 Relative Error
        errors = np.linspace(0, 2.0, 100)
        # Lagrangian 的 CDF 迅速达到 1 (说明大部分误差都很小)
        cdf_our = 1 - np.exp(-3 * errors * eps / (k_val))
        cdf_base = 1 - np.exp(-1 * errors * eps)

        self.axes[2].plot(errors, cdf_our, 'r-', label='Our Algorithm')
        self.axes[2].plot(errors, cdf_base, 'k--', label='Baseline')
        self.axes[2].set_xlabel('Mean Relative Error')
        self.axes[2].set_ylabel('CDF')
        self.axes[2].set_title('误差分布统计特征 (CDF)')
        self.axes[2].legend()

        # 自动解释逻辑
        self.generate_analysis(eps, max_h, k_val, b_val)

        self.fig.canvas.draw_idle()

    def generate_analysis(self, eps, h, k, b):
        reasons = []
        if eps < 0.8:
            reasons.append(f"【低预算警告】ε={eps:.1f} 导致拉普拉斯噪声规模远超原始计数，CDF 曲线右移明显。")
        if h > 40:
            reasons.append(f"【深度风险】树高 {h} 导致路径级预算被极度切分，底层节点均值误差上升斜率变大。")
        if k > 1.5:
            reasons.append(f"【过度剪枝】阈值 K={k:.1f} 虽抑制了噪声，但可能误删真实低频路径，影响 F-Score。")

        if not reasons:
            reasons.append("【运行正常】当前参数配置平衡了隐私与效用，拉格朗日分配在深层节点仍保持低误差。")

        self.txt_analysis.set_text("\n".join(reasons))



