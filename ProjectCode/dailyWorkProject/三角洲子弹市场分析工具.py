import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import os

# --- 1. 核心参数配置 ---
TAX_RATE = 0.132
AMMO_FILE = 'ammo_prices.csv'
MAT_FILE = 'mat_prices.csv'
OPPORTUNITY_THRESHOLD = 15.0  # 暴利预警阈值 (%)

RECIPES = {
    '45-70 Govt FTX':
        {'level': '5', 'output': 120, 'hours': 8,
         'mats': {'高级燃料': 3, '自旋型手锯': 1, '火药': 2}
        },
    '5.56x45mm M995':
        {'level': '5', 'output': 120, 'hours': 8,
         'mats': {'高级燃料': 2, '初级子弹生产零件': 2}
        },
    '7.62x39mm SUB':
        {'level': '5', 'output': 120, 'hours': 8,
         'mats': {'高级燃料': 2, '高精数显卡尺': 2, '角磨机': 1}
        },
    '7.62x51mm M80': {'level': '4', 'output': 180, 'hours': 7,
                      'mats': {'E型滤毒罐': 3, '机械破障锤': 3, '火药': 2, '低级燃料': 1}},
    '5.56x45mm M855A1': {'level': '4', 'output': 180, 'hours': 7,
                         'mats': {'E型滤毒罐': 2, '机械破障锤': 2, '初级子弹生产零件': 1, '电源': 1, '角磨机': 2}}
}


# --- 2. 通用功能 ---
def save_to_csv(data, filename):
    df = pd.read_csv(filename, encoding='utf-8-sig') if os.path.exists(filename) else pd.DataFrame()
    df = pd.concat([df, pd.DataFrame([data])], ignore_index=True)
    df.to_csv(filename, index=False, encoding='utf-8-sig')


def get_latest_prices(filename):
    if not os.path.exists(filename): return {}
    df = pd.read_csv(filename, encoding='utf-8-sig')
    if df.empty: return {}
    df['name'] = df['name'].str.strip()
    return df.sort_values('timestamp').groupby('name').last()['price'].to_dict()


# --- 3. 核心功能模块 ---

def mat_logger():
    print(f"\n{'=' * 15} 原材料价格录入 {'=' * 15}")
    latest = get_latest_prices(MAT_FILE)
    if latest: print("当前参考价:", latest)
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    name = input("材料名称 (输入'燃料'可启动换算器): ")
    if name in ['燃料', '高级燃料']:
        name = '高级燃料'
        if input("选择录入方式 (1: 直接输入, 2: 弯刀+咖啡): ") == '2':
            price = float(input("海盗弯刀价格: ")) + float(input("挂耳咖啡价格: "))
        else:
            price = float(input("直接输入燃料单价: "))
    else:
        price = float(input(f"请输入 [{name}] 当前单价: "))
    save_to_csv({'timestamp': now, 'name': name, 'price': price}, MAT_FILE)
    print("✅ 记录成功")


def ammo_logger():
    print(f"\n{'=' * 15} 子弹售价录入 {'=' * 15}")
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    for i, n in enumerate(RECIPES.keys(), 1): print(f"{i}. {n}")
    name = input("请输入子弹名称: ")
    price = float(input(f"请输入 [{name}] 当前市场售价: "))
    save_to_csv({'timestamp': now, 'name': name, 'price': price}, AMMO_FILE)
    print("✅ 记录成功")


def analyze_profit():
    mats = get_latest_prices(MAT_FILE)
    ammo_latest = get_latest_prices(AMMO_FILE)
    print(f"\n📊 即时利润分析 (税率 {TAX_RATE * 100:.1f}%)")
    print("-" * 95)
    print(f"{'子弹名称':<18} | {'单发成本':>8} | {'单发净利':>8} | {'一炉总利':>8} | {'ROI':>6} | {'建议'}")
    print("-" * 95)
    for name, info in RECIPES.items():
        try:
            cost = sum(mats[m] * qty for m, qty in info['mats'].items()) / info['output']
            net_income = ammo_latest[name] * (1 - TAX_RATE)
            profit = net_income - cost
            roi = (profit / cost) * 100

            flag = "🔥" if profit > 0 else "❄️"
            advice = "!!! 发现商机 !!!" if roi > OPPORTUNITY_THRESHOLD else "持币观望"
            if profit < 0: advice = "亏损，卖材料"

            print(
                f"{name:<18} | {cost:>12.1f} | {profit:>12.1f} | {profit * info['output']:>12.0f} | {roi:>5.1f}% {flag} | {advice}")
        except KeyError as e:
            print(f"{name:<18} | ⚠️ 缺少材料: {e}")
        except:
            print(f"{name:<18} | ⚠️ 售价未录入")


def show_charts():
    """可视化报表：售价/原材走势 + 利润柱状图 + 双向ROI气泡图"""
    plt.rcParams['font.sans-serif'] = ['SimHei'];
    plt.rcParams['axes.unicode_minus'] = False
    if not os.path.exists(AMMO_FILE) or not os.path.exists(MAT_FILE): return print("数据不足")

    # 1. 数据预处理
    def process_df(filename):
        df = pd.read_csv(filename, encoding='utf-8-sig')
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df['period'] = df['timestamp'].dt.hour.apply(lambda x: "早" if 0 <= x < 8 else "中" if 8 <= x < 16 else "晚")
        df['time_group'] = df['timestamp'].dt.strftime('%m-%d') + " " + df['period']
        return df

    df_ammo = process_df(AMMO_FILE)
    df_mat = process_df(MAT_FILE)

    # 聚合数据
    ammo_plot = df_ammo.groupby(['time_group', 'name'])['price'].mean().unstack().sort_index()
    mat_plot = df_mat.groupby(['time_group', 'name'])['price'].mean().unstack().sort_index()

    latest_mats = get_latest_prices(MAT_FILE)
    names, profits_wan, rois = [], [], []

    for name, info in RECIPES.items():
        try:
            cost = sum(latest_mats[m] * qty for m, qty in info['mats'].items()) / info['output']
            last_price = df_ammo[df_ammo['name'] == name]['price'].iloc[-1]
            net_profit_single = (last_price * (1 - TAX_RATE)) - cost
            names.append(name)
            profits_wan.append((net_profit_single * info['output']) / 10000)
            rois.append((net_profit_single / cost) * 100)
        except:
            continue

    # 2. 绘图 (四图联动)
    fig, (ax1, ax2, ax3, ax4) = plt.subplots(4, 1, figsize=(12, 20))

    # --- 图1：子弹售价走势 ---
    ammo_plot.plot(ax=ax1, marker='o', linewidth=2)
    ax1.set_title('子弹售价走势 (早/中/晚时段)');
    ax1.grid(True, alpha=0.3)

    # --- 图2：原材料价格走势 (新增) ---
    # 只显示配方中出现的关键材料，避免线条过多
    main_mats = ['高级燃料', 'E型滤毒罐', '机械破障锤', '火药']
    mat_plot[[c for c in mat_plot.columns if c in main_mats]].plot(ax=ax2, linestyle='--', marker='s')
    ax2.set_title('核心原材料价格走势');
    ax2.grid(True, alpha=0.3)

    # --- 图3：每炉利润柱状图 ---
    colors = ['#ff4d4d' if x < 0 else '#2ecc71' for x in profits_wan]
    bars = ax3.bar(names, profits_wan, color=colors, alpha=0.7)
    ax3.bar_label(bars, fmt='%.1f万', padding=3)
    ax3.axhline(y=0, color='black', linewidth=1)
    if profits_wan:
        max_idx = profits_wan.index(max(profits_wan))
        if profits_wan[max_idx] > 0:
            ax3.get_xticklabels()[max_idx].set_color('red')
            ax3.get_xticklabels()[max_idx].set_weight('bold')
    ax3.set_title('特勤处制造一次的利润 (万哈夫币)');
    ax3.set_ylabel('万')

    # --- 图4：双向ROI气泡图 (亏损/赚钱越多 气泡越大) ---
    # 气泡大小由绝对值决定，最低给个基础圆点
    bubble_sizes = [max(abs(x) * 25, 50) for x in rois]
    roi_colors = ['#e74c3c' if x < 0 else '#27ae60' for x in rois]
    ax4.scatter(names, rois, s=bubble_sizes, c=roi_colors, alpha=0.6, edgecolors="white")
    for i, txt in enumerate(rois):
        ax4.annotate(f"{txt:.1f}%", (names[i], rois[i]), ha='center', va='center', color='white', fontweight='bold',
                     fontsize=9)
    ax4.axhline(y=0, color='gray', linestyle='-')
    ax4.axhline(y=15, color='orange', linestyle='--', label='暴利线')
    ax4.set_title('投资回报率 ROI % (气泡越大代表行情越极端)');
    ax4.set_ylabel('ROI %')

    plt.tight_layout()
    # 自动保存
    folder = 'Trading_Reports'
    if not os.path.exists(folder): os.makedirs(folder)
    save_path = os.path.join(folder, f'哈夫克深度研报_{datetime.now().strftime("%m%d_%H%M")}.jpg')
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    print(f"✅ 深度研报已导出: {save_path}")
    plt.show()


if __name__ == "__main__":
    while True:
        print(f"\n{'#' * 20} 哈夫克倒爷决策终端 {'#' * 20}")
        print("1. 录入材料价 | 2. 录入子弹价 | 3. 查看利润分析 | 4. 导出可视化看板 | 5. 退出")
        c = input("请选择: ")
        if c == '1':
            mat_logger()
        elif c == '2':
            ammo_logger()
        elif c == '3':
            analyze_profit()
        elif c == '4':
            show_charts()
        elif c == '5':
            break