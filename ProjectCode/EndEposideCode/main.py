import pandas as pd
from pathlib import Path
from utils import G
import time
from utils import  get_preprocessed_paths, plot_figure_6_combined, calculate_jsd, infer_trajectory

r_t_start = time.perf_counter()

# 清洗逻辑
print(f"当前图节点数: {G.number_of_nodes()}")
print(f"从 机场东 到 罗湖 的推断路径: \n{' -> '.join(infer_trajectory('机场东', '罗湖'))}")

# 下面执行路线预测测试（时间最小化）
# 跨平台路径
data_path = Path(__file__).parent / "data"

# 使用 rglob 还可以递归搜索子文件夹下的所有 csv
all_files = list(data_path.glob("*.csv"))

df_list = [pd.read_csv(f, dtype={'card_no': str, 'deal_date': str, 'station': str, 'deal_type': str}) for f in all_files]
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


# ====================== 合成数据放大（强烈推荐） ======================
SCALE_FACTOR = 200          # 可调：50 倍 ≈ 1650 万行程（接近论文量级）
                           # 想更大就改成 100 / 200

trip_counts['passenger_count'] = (trip_counts['passenger_count'] * SCALE_FACTOR).astype(int)
total_flow = int(total_flow * SCALE_FACTOR)

print(f"✅ 合成数据放大完成！当前 total_flow = {total_flow:,}（原 {total_flow//SCALE_FACTOR:,}）")
print(f"   trip_counts 最大流量: {trip_counts['passenger_count'].max():,}")
# =====================================================================


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
r_t_end = time.perf_counter()
read_time = r_t_end - r_t_start

# 拆分之后的主清洗逻辑运行正常!
# 下面是绘图的复现
import matplotlib.pyplot as plt
import copy
import numpy as np
from tqdm import tqdm  # 建议安装：pip install tqdm 用于查看进度
from model import LagrangianTrie, LiIncrementalTrie, SeqPTTrie, SafePathTrie
from utils import calculate_relative_error, TrajectoryTrie, infer_trajectory

# 实验超参数配置
EPSILON = 1.0  # 总隐私预算 (对应图3的设定)
K_VAL = 1.5  # 剪枝参数 k
B_VAL = 1.0  # 剪枝参数 b
HEIGHTS = [2,3,4,5 ]  # X轴：树高度
ITERATIONS = 5  # 每组实验跑5次取平均，消除拉普拉斯噪声的随机性干扰


def run_benchmark(trip_counts, total_flow):
    """
    进行全模型对比实验
    trip_counts: 包含 'station_in', 'station_out', 'passenger_count' 的 DataFrame
    total_flow: 总乘客数 (用于 Root 节点和 sanity bound 计算)
    """

    # 初始化结果存储
    results = {
        "Our Algorithm": [],
        "Li's Algorithm": [],
        "SeqPT": [],
        "SafePath": []
    }

    # 预处理：先算出所有 OD 对的路径轨迹，避免在循环里重复调用 infer_trajectory
    print("正在预计算路径轨迹...")
    trajectory_data = []
    for row in tqdm(trip_counts.itertuples(index=False), total=len(trip_counts)):
        path = infer_trajectory(row.station_in, row.station_out)
        if path:
            trajectory_data.append((path, row.passenger_count))

    # 核心评估循环
    for h in HEIGHTS:
        print(f"\n正在测试树高度 H = {h}")

        # 构建当前高度的“原始基准树”
        base_trie = TrajectoryTrie(max_height=h, total_trajectories=total_flow)
        for path, count in trajectory_data:
            base_trie.insert(path, count=count)

        # 获取原始数据的查询结果 q(D)
        # only_leaves=False 表示评估所有路径前缀的准确性
        raw_queries = base_trie.get_raw_data(only_leaves=False)

        # 临时存储各模型在当前高度下的误差
        h_errors = {name: [] for name in results.keys()}

        for i in range(ITERATIONS):
            # 定义参与测试的模型实例
            models = {
                "Our Algorithm": LagrangianTrie(h, total_flow),
                "Li's Algorithm": LiIncrementalTrie(h, total_flow),
                "SeqPT": SeqPTTrie(h, total_flow),
                "SafePath": SafePathTrie(h, total_flow)
            }

            for name, m in models.items():
                # 使用 deepcopy 快速复制原始树结构，无需重新 insert 140万数据
                m.root = copy.deepcopy(base_trie.root)

                try:
                    # 分配预算 -> 加噪剪枝
                    m.allocate_budget(EPSILON)
                    m.apply_noise_and_prune(k=K_VAL, b=B_VAL)

                    # 获取加噪后的数据并计算相对误差
                    sanitized_data = m.get_sanitized_data(only_leaves=False)
                    print(f"DEBUG: {name} 存活节点数: {len(sanitized_data)}")  # 看看你的算法存活了多少节点
                    err = calculate_relative_error(base_trie, sanitized_data, total_flow)
                    h_errors[name].append(err)
                except Exception as e:
                    # 如果 SeqPT 崩溃（节点全被剪掉），记录为无效
                    h_errors[name].append(np.nan)

        # 计算并保存平均误差
        for name in results.keys():
            avg_err = np.nanmean(h_errors[name])
            results[name].append(avg_err)
            print(f"  [{name}] 平均相对误差: {avg_err:.4f}")

    # 绘制复现图表
    plot_results(results,
                 x_vals=HEIGHTS,
                 x_label='Prefix Tree Height',
                 y_label='Average Relative Error',
                 title='Figure 3: Impact of Tree Height')


def run_fig4(path_list, total_flow):
    """
    复现 Figure 4: 树最大高度与运行时间的关系
    """
    HEIGHTS = [10, 20, 30, 40]  # 可调：根据实际情况调整高度范围
    FIXED_EPSILON = 1.0

    # 初始化结果存储
    # 假设你有这四个算法，如果没有可以先注释掉
    models = {
        "Our Algorithm": LagrangianTrie,
        "Li's Algorithm": LiIncrementalTrie,
        "SeqPT": SeqPTTrie,
        "SafePath": SafePathTrie
    }

    runtime_results = {name: [] for name in models.keys()}

    for h in HEIGHTS:
        print(f"正在测试高度 H = {h}...")
        for name, ModelClass in models.items():
            start_time = time.time()

            # 初始化树
            trie = ModelClass(max_height=h, total_trajectories=total_flow)

            # 插入轨迹数据 (path_list 是预处理好的 (path, count) 元组)
            for path, count in path_list:
                trie.insert(path, count=count)

            # 配预算
            trie.allocate_budget(total_epsilon=FIXED_EPSILON)

            # 执行加噪 (模拟完整发布流程)
            trie.apply_noise_and_prune(k=K_VAL, b=B_VAL)

            end_time = time.time()
            duration = end_time - start_time

            runtime_results[name].append(duration)
            print(f"  - {name} 耗时: {duration:.4f}s")
    plot_results(results=runtime_results,
                 x_vals = HEIGHTS,
                 x_label='Prefix Tree Height',
                 y_label='Runtime(sec)',
                 title='(fig4)Runtime comparison under different heights')


def run_fig5():
    # 参数设置
    HEIGHTS = [10, 20, 30, 40]  # 树高度范围
    EPSILONS = [0.5, 0.75, 1.0, 1.25]  # 不同的折线

    # 预处理路径数据（只算一次最短路，极大提升速度）
    print("正在预处理路径数据...")
    path_list = get_preprocessed_paths(trip_counts)

    # 结果容器：{ "Eps=0.5": [err1, err2...], "Eps=1.0": [...] }
    results = {f"Epsilon = {eps}": [] for eps in EPSILONS}

    # 实验循环
    for eps in EPSILONS:
        print(f"\n正在测试预算 Epsilon = {eps}")

        for h in HEIGHTS:
            # 建立原始树基准（每个高度的原始树结构不同，必须重新建）
            raw_trie = TrajectoryTrie(max_height=h, total_trajectories=total_flow)
            for path, count in path_list:
                raw_trie.insert(path, count=count)

            # 建立你的算法模型
            trie = LagrangianTrie(max_height=h, total_trajectories=total_flow)
            for path, count in path_list:
                trie.insert(path, count=count)

            # 分配预算并加噪
            trie.allocate_budget(total_epsilon=eps)
            trie.apply_noise_and_prune(k=K_VAL, b=B_VAL)

            # 获取结果并计算误差
            sanitized_results = trie.get_sanitized_data(only_leaves=False)
            err = calculate_relative_error(raw_trie, sanitized_results, total_flow)

            results[f"Epsilon = {eps}"].append(err)
            print(f"  Height {h}: Error = {err:.4f}")

    # 绘图
    # 这里不用之前的 plot_results，因为那个函数是按算法名配色的
    # 直接在这里画不同 epsilon 的折线，X 轴是 HEIGHTS，Y 轴是误差
    plt.figure(figsize=(8, 6))
    markers = ['o', 's', 'D', '^']
    for i, (label, y_vals) in enumerate(results.items()):
        plt.plot(HEIGHTS, y_vals, label=label, marker=markers[i % len(markers)], linewidth=2)

    plt.xlabel('Prefix Tree Height', fontsize=12)
    plt.ylabel('Average Relative Error', fontsize=12)
    plt.title('Figure 5: Error vs Height under Different Epsilon')
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.legend()
    plt.show()

def run_fig6_1(_trip_counts, _total_flow,reading_time):
    # 第一次使用默认参数

    # 存储结果结构：{ "Reading": [], "Allocation": [], ... }
    # 这里以第四个子图（Epsilon 变化）为例，其他子图同理
    results = {
        "Reading": [], "Allocation": [], "Sanitization": [], "Writing": [], "Total": []
    }
    t_start = time.perf_counter()

    # Reading & Preprocessing
    t0 = time.perf_counter()
    path_list = get_preprocessed_paths(trip_counts)
    t_read = time.perf_counter() - t0 + reading_time

    # Initialization & Allocation
    t1 = time.perf_counter()
    trie = LagrangianTrie(max_height=50, total_trajectories=_total_flow)
    for path, count in path_list: trie.insert(path, count=count)
    trie.allocate_budget(total_epsilon=1.0)  # 固定预算
    t_alloc = time.perf_counter() - t1

    # Sanitization (Noise)
    t2 = time.perf_counter()
    trie.apply_noise_and_prune(k=1.5, b=1)  # 实验参数
    t_san = time.perf_counter() - t2

    # Writing
    t3 = time.perf_counter()
    _ = trie.get_sanitized_data()
    t_write = time.perf_counter() - t3

    t_total = time.perf_counter() - t_start + reading_time

    # 记录数据
    results["Reading"].append(t_read)
    results["Allocation"].append(t_alloc)
    results["Sanitization"].append(t_san)
    results["Writing"].append(t_write)
    results["Total"].append(t_total)

    return results

def run_fig6_2(_trip_counts, _total_flow,reading_time):
    # 定义要测试的参数范围
    K_RANGE = [0.5, 0.75, 1.0, 1.25, 1.5]
    B_RANGE = [0, 1, 2, 3, 4, 5]
    EPS_RANGE = [0.5, 0.75, 1.0, 1.25, 1.5]

    # 存储结果结构：{ "Reading": [], "Allocation": [], ... }
    # 这里以第四个子图（Epsilon 变化）为例，其他子图同理
    results = {
        "Reading": [], "Allocation": [], "Sanitization": [], "Writing": [], "Total": []
    }

    path_list = get_preprocessed_paths(trip_counts)
    for eps in EPS_RANGE:
        t_start = time.perf_counter()

        # Reading & Preprocessing
        t0 = time.perf_counter()

        t_read = time.perf_counter() - t0 + reading_time

        # Initialization & Allocation
        t1 = time.perf_counter()
        trie = LagrangianTrie(max_height=50, total_trajectories=_total_flow)
        for path, count in path_list: trie.insert(path, count=count)
        trie.allocate_budget(total_epsilon=eps)
        t_alloc = time.perf_counter() - t1

        # Sanitization (Noise)
        t2 = time.perf_counter()
        trie.apply_noise_and_prune(k=1.5, b=1)  # 实验参数
        t_san = time.perf_counter() - t2

        # Writing
        t3 = time.perf_counter()
        _ = trie.get_sanitized_data()
        t_write = time.perf_counter() - t3

        t_total = time.perf_counter() - t_start + reading_time

        # 记录数据
        results["Reading"].append(t_read)
        results["Allocation"].append(t_alloc)
        results["Sanitization"].append(t_san)
        results["Writing"].append(t_write)
        results["Total"].append(t_total)


    return results


def run_fig6_1_3(_trip_counts, _total_flow, reading_time):
    # 定义要测试的参数范围
    K_RANGE = [0.5, 0.75, 1.0, 1.25, 1.5]
    B_RANGE = [0, 1, 2, 3, 4, 5]
    EPS_RANGE = [0.5, 0.75, 1.0, 1.25, 1.5]

    # 存储结果结构：{ "Reading": [], "Allocation": [], ... }
    # 这里以第四个子图（Epsilon 变化）为例，其他子图同理
    results = {
        "Reading": [], "Allocation": [], "Sanitization": [], "Writing": [], "Total": []
    }

    path_list = get_preprocessed_paths(trip_counts)
    for k in K_RANGE:
        t_start = time.perf_counter()

        # Reading & Preprocessing
        t0 = time.perf_counter()

        t_read = time.perf_counter() - t0 + reading_time

        # Initialization & Allocation
        t1 = time.perf_counter()
        trie = LagrangianTrie(max_height=50, total_trajectories=_total_flow)
        for path, count in path_list: trie.insert(path, count=count)
        trie.allocate_budget(total_epsilon=1.0)  # 固定预算
        t_alloc = time.perf_counter() - t1

        # Sanitization (Noise)
        t2 = time.perf_counter()
        trie.apply_noise_and_prune(k=k, b=1)  # 实验参数
        t_san = time.perf_counter() - t2

        # Writing
        t3 = time.perf_counter()
        _ = trie.get_sanitized_data()
        t_write = time.perf_counter() - t3

        t_total = time.perf_counter() - t_start + reading_time

        # 记录数据
        results["Reading"].append(t_read)
        results["Allocation"].append(t_alloc)
        results["Sanitization"].append(t_san)
        results["Writing"].append(t_write)
        results["Total"].append(t_total)

    return results
def run_fig6_1_4(_trip_counts, _total_flow, reading_time):
    # 定义要测试的参数范围
    K_RANGE = [0.5, 0.75, 1.0, 1.25, 1.5]
    B_RANGE = [0, 1, 2, 3, 4, 5]
    EPS_RANGE = [0.5, 0.75, 1.0, 1.25, 1.5]

    # 存储结果结构：{ "Reading": [], "Allocation": [], ... }
    # 这里以第四个子图（Epsilon 变化）为例，其他子图同理
    results = {
        "Reading": [], "Allocation": [], "Sanitization": [], "Writing": [], "Total": []
    }

    path_list = get_preprocessed_paths(trip_counts)
    for b in B_RANGE:
        t_start = time.perf_counter()

        # Reading & Preprocessing
        t0 = time.perf_counter()

        t_read = time.perf_counter() - t0 + reading_time

        # Initialization & Allocation
        t1 = time.perf_counter()
        trie = LagrangianTrie(max_height=50, total_trajectories=_total_flow)
        for path, count in path_list: trie.insert(path, count=count)
        trie.allocate_budget(total_epsilon=1.0)  # 固定预算
        t_alloc = time.perf_counter() - t1

        # Sanitization (Noise)
        t2 = time.perf_counter()
        trie.apply_noise_and_prune(k=1.5, b=b)  # 实验参数
        t_san = time.perf_counter() - t2

        # Writing
        t3 = time.perf_counter()
        _ = trie.get_sanitized_data()
        t_write = time.perf_counter() - t3

        t_total = time.perf_counter() - t_start + reading_time

        # 记录数据
        results["Reading"].append(t_read)
        results["Allocation"].append(t_alloc)
        results["Sanitization"].append(t_san)
        results["Writing"].append(t_write)
        results["Total"].append(t_total)

    return results


def run_fig7(total_flow, path_list):
    EPSILONS = [0.1, 0.5, 1.0, 1.5, 2.0]

    models = {
        "Our Algorithm": LagrangianTrie,
        "Li's Algorithm": LiIncrementalTrie,
        "SeqPT": SeqPTTrie,
        "SafePath": SafePathTrie
    }
    # 初始化结果容器
    jsd_results = {name: [] for name in models.keys()}
    err_results = {name: [] for name in models.keys()}

    # 获取原始数据分布 (作为 JSD 和 Relative Error 的基准)
    raw_trie = LagrangianTrie(max_height=50, total_trajectories=total_flow)
    for path, count in path_list: raw_trie.insert(path, count=count)
    raw_results = raw_trie.get_raw_data(only_leaves=False)

    for eps in EPSILONS:
        for name, ModelClass in models.items():
            trie = ModelClass(max_height=50, total_trajectories=total_flow)
            for path, count in path_list: trie.insert(path, count=count)

            # 加噪与剪枝 (固定 k, b)
            trie.allocate_budget(total_epsilon=eps)
            trie.apply_noise_and_prune(k=1.5, b=1)
            san_results = trie.get_sanitized_data(only_leaves=False)

            # 计算 JSD
            jsd = calculate_jsd(raw_results, san_results)
            jsd_results[name].append(jsd)

            # 计算 Relative Error
            errs = calculate_relative_error(raw_trie, san_results, total_flow)
            err_results[name].append(np.nanmean(errs))

    return jsd_results, err_results, EPSILONS

def plot_results(results, x_vals, x_label='Epsilon', y_label='Average Relative Error', title='Experiment Result'):
    """
    通用绘图函数
    results: 字典 { "算法名": [误差列表] }
    x_vals: X 轴对应的数值列表 (如 EPSILONS 或 K_VALUES)
    """
    plt.figure(figsize=(8, 6))

    # 颜色和样式配置
    configs = {
        "Our Algorithm": {"color": "red", "marker": "D", "linewidth": 2},
        "SeqPT": {"color": "black", "marker": "^", "linewidth": 1.5},
        "SafePath": {"color": "blue", "marker": "s", "linewidth": 1.5},
        "Li's Algorithm": {"color": "purple", "marker": "x", "linewidth": 1.5}
    }

    for name, y_vals in results.items():
        # 确保只画出非 NaN 的点
        # 修复 IndexError：使用传入的 x_vals 而不是全局变量 HEIGHTS
        valid_x = [x_vals[i] for i, e in enumerate(y_vals) if not np.isnan(e)]
        valid_y = [e for e in y_vals if not np.isnan(e)]

        config = configs.get(name, {"color": None, "marker": "o", "linewidth": 1})

        plt.plot(valid_x, valid_y, label=name,
                 color=config["color"],
                 marker=config["marker"],
                 linewidth=config["linewidth"])

    plt.xlabel(x_label, fontsize=12)
    plt.ylabel(y_label, fontsize=12)
    plt.title(title)
    plt.legend()
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.show()




# 测试的主逻辑，相关的具体测试代码都放在上面了
if __name__ == "__main__":
    # 确保 trip_counts 和 total_flow 已经生成
    # 这个标准测试是用在横向比对各种模型效果的时候用的（复现fig3）
    run_benchmark(trip_counts, total_flow)

    # 这个测试是用在评估树高度对运行时间影响的时候用的（复现fig4）
    # 需要先预处理出 path_list（(path, count) 元组列表
    # total_flow是总流量，用来处理root节点的
    path_list = get_preprocessed_paths(trip_counts)
    run_fig4(path_list, total_flow)

    # 这个测试是用在评估不同预算,不同树高对误差影响的时候用的（复现fig5）
    # 使用的模型是拉格朗日松弛算法, 依赖上面的path_list和total_flow
    run_fig5()

    # fig6组图绘制(这四次都是完整地跑完的哦)
    res1 = run_fig6_1(trip_counts, total_flow, read_time)
    res2 = run_fig6_1_3(trip_counts, total_flow, read_time)
    res3 = run_fig6_1_4(trip_counts, total_flow, read_time)
    res4 = run_fig6_2(trip_counts, total_flow, read_time)

    # 绘图
    plot_figure_6_combined(res1, res2, res3, res4)

    # fig7的图片绘制
    jsd_res, err_res, eps_vals = run_fig7(total_flow, path_list)
    plot_results(jsd_res, x_vals=eps_vals, x_label='Epsilon', y_label='JSD', title='(a) JSD vs Epsilon')
    plot_results(err_res, x_vals=eps_vals, x_label='Epsilon', y_label='Relative Error', title='(b) Relative Error vs Epsilon')