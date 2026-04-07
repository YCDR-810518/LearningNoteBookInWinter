import matplotlib.pyplot as plt
import matplotlib

# 彻底解决中文乱码和负号问题
plt.rcParams['font.sans-serif'] = ['Noto Sans CJK SC', 'Arial Unicode MS', 'SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

# 数据（来自国家统计局70个大中城市商品住宅销售价格指数月报）
months = ['2025年12月', '2026年1月', '2026年2月']

# 新建商品住宅（新房）环比变化（%）
new_first  = [-0.5, -0.3,  0.0]   # 一线
new_second = [-0.4, -0.3, -0.2]   # 二线
new_third  = [-0.6, -0.4, -0.3]   # 三线

# 二手住宅（二手房）环比变化（%）
sec_first  = [-0.8, -0.5, -0.1]   # 一线
sec_second = [-0.7, -0.5, -0.4]   # 二线
sec_third  = [-0.9, -0.6, -0.5]   # 三线

# 创建图表
fig, axs = plt.subplots(2, 1, figsize=(14, 10))

# 图1：新房环比
axs[0].plot(months, new_first,  'b-o', linewidth=2.5, markersize=6, label='一线城市 新房')
axs[0].plot(months, new_second, 'b--s', linewidth=2.5, markersize=6, label='二线城市 新房')
axs[0].plot(months, new_third,  'b:^', linewidth=2.5, markersize=6, label='三线城市 新房')
axs[0].set_title('新建商品住宅（新房）环比变化（%）', fontsize=15, pad=15)
axs[0].set_ylabel('环比变化 (%)', fontsize=13)
axs[0].legend(fontsize=12, loc='best')
axs[0].grid(True, linestyle='--', alpha=0.7)

# 图2：二手房环比
axs[1].plot(months, sec_first,  'r-o', linewidth=2.5, markersize=6, label='一线城市 二手房')
axs[1].plot(months, sec_second, 'r--s', linewidth=2.5, markersize=6, label='二线城市 二手房')
axs[1].plot(months, sec_third,  'r:^', linewidth=2.5, markersize=6, label='三线城市 二手房')
axs[1].set_title('二手住宅（二手房）环比变化（%）', fontsize=15, pad=15)
axs[1].set_ylabel('环比变化 (%)', fontsize=13)
axs[1].legend(fontsize=12, loc='best')
axs[1].grid(True, linestyle='--', alpha=0.7)

plt.suptitle('国家统计局70个大中城市商品住宅销售价格指数趋势（2025.12 - 2026.02）\n'
             '数据来源：国家统计局官网每月发布的70城房价指数公报',
             fontsize=16, y=0.98)

plt.tight_layout(rect=[0, 0, 1, 0.94])
plt.show()