import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# 1.创建画布
# 参1：画布宽高比&大小 参2：dpi像素点密度
# plt.style.use('ggplot')
plt.figure(figsize=(10,5),dpi=80)


# 2.准备数据
# 一周的最低气温
# 参1，x轴数据 参2，y轴数据
plt.plot([1,2,3,4,5,6,7],[19,20,19,19,19,18,18])

plt.grid(True)

# 3.显示绘图
plt.show()