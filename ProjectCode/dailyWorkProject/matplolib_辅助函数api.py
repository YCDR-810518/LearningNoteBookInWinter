import random
import matplotlib.pyplot as plt
from pylab import mpl
import seaborn as sns
import os
os.chdir(r'D:\Documents\GitHub\LearningNoteBookInWinter\ProjectCode\dailyWorkProject')
# 设置显示中文字体
mpl.rcParams['font.sans-serif'] = ['simHei']
# 设置正常显示符号
mpl.rcParams["axes.unicode_minus"] = False

# 绘制一小时内的最高气温折线
x_axsis = range(0,60)
y_axsis_tempr_u = [random.uniform(15.0,20.0) for i in x_axsis]

# 绘制一小时内的最低气温折线
y_axsis_tempr_l = [random.uniform(5,13) for i in x_axsis]

#设置画布
plt.figure(figsize=(16,9),dpi=1200)

#color->折线的颜色
plt.plot(x_axsis,y_axsis_tempr_u,color='red',label='最高气温',linestyle='-',linewidth=3 )

#再次plot画出最低气温
plt.plot(x_axsis,y_axsis_tempr_l,color='blue',label='最低气温',linestyle='-',linewidth=3)

# 设置图例的位置
plt.legend(loc='best',fontsize=14,ncol=1 ,frameon=False)

# 散点图
# 最高气温的散点图
plt.scatter(x_axsis,y_axsis_tempr_u,color='red')
# 最低气温的散点图
plt.scatter(x_axsis,y_axsis_tempr_l,color='blue')

# 分隔的标签
x_ticks_label = [f'11点{i}分' for i in x_axsis]
plt.xticks(x_axsis[::5],x_ticks_label[::5])
y_range = range(0, 21)
plt.yticks(y_range[::1], [f"{i}℃" for i in y_range][::1])

# 设置x，y周的刻度的字体大小，主副刻度
plt.tick_params(axis='y', which='major', labelsize=15)
plt.tick_params(axis='x', which='major', labelsize=15)

# 显示网格
# linestyle是样式！
# alpha是透明度
plt.grid(True,'both',color='brown',linestyle=':',alpha=0.4)



plt.title('深圳一小时内气温图',size=20)
plt.xlabel('时间/min',size=16)
plt.ylabel('温度/℃',size=16)

# 保存图片
plt.savefig(f'sz一小时温度变化_{random.randint(0,65535)}.jpg')

# show之后图片会从内存中释放，要先保存图片再show
plt.show()