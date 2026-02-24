# matplotlib 2d科学绘图工具

## 使用matplotlib的速查表

![handout-beginner](https://raw.githubusercontent.com/YCDR-810518/imageBed/main/2026/02/upgit_20260223_1771844898.png)

开发2D图表

**用于数据挖掘的辅助工具**

## 绘图基础步骤

1. 导入模块

```
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
```

2. 图形绘制流程

   2.1. 创建画布`plt.figure()`

   * ![image-20260223195502112](https://raw.githubusercontent.com/YCDR-810518/imageBed/main/2026/02/upgit_20260223_1771847702.png)

     `figsize`:指定图的长宽

     `dpi`:指定图的清晰度

     返回：`fig对象`

   2.2. 绘制图像 `plt.figure(x,y)`

   * 以折线图为例

   2.3. 显示图像 ```plt.show()```

3. 折线图绘制示例

## 图像结构示意图

![image-20200528144651404](https://yxy-biubiubiu.github.io/image/image-20200528144651404.png)

axes:绘图区 figure:画布

grid:网格 tick:刻度

## 给图像添加辅助功能

### 设置形状的颜色&风格

| 颜色 | 代码 | 线型 | 代码 | 标记 | 代码 |
| ---- | ---- | ---- | ---- | ---- | ---- |
| 蓝   | ‘b’  | 实线 | ‘-’  | 点   | ‘.’  |
| 绿   | ‘g’  | 虚线 | ‘–’  | x    | ‘x’  |
| 红   | ‘r’  | 虚点 | ‘-.’ | 圆圈 | ‘o’  |
| 青   | ‘c’  | 点线 | ‘:’  | 三角 | ‘v’  |
| 紫   | ‘p’  |      |      | 方块 | ‘s’  |
| 黄   | ‘y’  |      |      | 星   | ‘*’  |
| 黑   | ‘k’  |      |      | 加号 | ‘+’  |
| 白   | ‘w’  |      |      | 菱形 | ‘D’  |

甚至可以将color=’k’, linestyle=’-‘缩写为’-k’

### 通用绘图参数

| Artist通用属性 | 作用                                                         |
| -------------- | ------------------------------------------------------------ |
| alpha          | 透明度，0为透明，1为不透明                                   |
| clip_box       | 裁剪框                                                       |
| clip_on        | 是否裁剪                                                     |
| clip_path      | 裁剪路径                                                     |
| label          | 文本标签                                                     |
| transform      | 坐标转换(绘制带地图投影的图形需要)                           |
| visible        | 是否可见/隐藏(通常用于隐藏Spines，也就是隐藏掉边框)          |
| zorder         | 绘图顺序(用于设置多图层的绘图顺序，比如先填色，再打点，再加图例) |

最常用的alpha，label，transform，visible，zorder。

### 添加自定义的刻度值

* `plt.xticks(x,**kwargs)`
* `plt.yticks(y,**kwargs)`

![image-20260224121012186](https://raw.githubusercontent.com/YCDR-810518/imageBed/main/2026/02/upgit_20260224_1771906212.png)

```python
# 分隔的标签
x_ticks_label = [f'11点{i}分' for i in x_axsis]
y_range = range(15, 21)
#这里前后的步长（分隔的长度）要对应
plt.xticks(x_axsis[::5],x_ticks_label[::5])
plt.yticks(y_range[::1], [f"{i}℃" for i in y_range][::1])
```

### 刻度线的样式修改

* `tick_params`

**基础用法**

```python
plt.tick_params(axis='y', which='major', labelsize=15)
```

 **详细拆解：**

- **`axis='both'`**: 指定作用于哪个轴。可以是 `'x'`、`'y'` 或者 `'both'`（同时修改 X 轴和 Y 轴）。
- **`which='major'`**: 指定作用于哪种刻度。Matplotlib 分为**主刻度（major）和次刻度（minor）**。默认显示的通常都是主刻度。
- **`labelsize=14`**: 设置刻度标签的**字体大小**

**进阶用法**

| **参数**               | **作用**           | **示例**                    |
| ---------------------- | ------------------ | --------------------------- |
| **`labelcolor`**       | 刻度文字的颜色     | `labelcolor='red'`          |
| **`color`**            | 刻度线本身的颜色   | `color='blue'`              |
| **`direction`**        | 刻度线朝内还是朝外 | `direction='in'` 或 `'out'` |
| **`width` / `length`** | 刻度线的粗细和长度 | `width=2, length=6`         |

### 中文字体显示问题

在python脚本中动态设置matplotlibrc

![image-20260224112825283](https://raw.githubusercontent.com/YCDR-810518/imageBed/main/2026/02/upgit_20260224_1771903705.png)

字体更改后导致坐标轴部分字符无法正常显示，需更改axes.unicode_minus参数

![image-20260224113019849](https://raw.githubusercontent.com/YCDR-810518/imageBed/main/2026/02/upgit_20260224_1771903819.png)

```python
from pylab import mpl
# 设置显示中文字体
mpl.rcParams['font.sans-serif'] = ['simHei']
# 设置正常显示符号
mpl.rcParams["axes.unicode_minus"] = False
```

### 添加网格

**True/False** 表示是否隐藏 **color** 网格颜色

**linestyle**是样式 **alpha**是透明度

```python
# 显示网格
# linestyle是样式！
# alpha是透明度
plt.grid(True,'both',color='brown',linestyle=':',alpha=0.4)
```

### 描述信息的添加

```python
# 添加标题
plt.title('深圳一小时内气温图',size=20)

# 添加x,y轴上的说明标签
plt.xlabel('时间/min',size=16)
plt.ylabel('温度/℃',size=16)
```

标题的设置同样也可以添加一些参数：

**loc**: {‘center’, ‘left’, ‘right’},设置标题显示的位置

pad: 设置标题距离图像上边缘距离

fontsize: 设置字体大小

color: 设置字体颜色



### 图例常用参数详解

`plt.legend()` 有几个非常实用的参数，可以帮你精细控制图例的外观：

- **`loc` (位置)**: 控制图例放在哪。
  - 常用取值：`'best'`（自动找空位）、`'upper right'`（右上）、`'lower left'`（左下）、`'center'`（正中）。
- **`fontsize` (字号)**: 设置图例里的文字大小。
- **`shadow` (阴影)**: 设置为 `True` 可以让图例框带一点立体阴影效果。
- **`ncol` (列数)**: 如果你有好几个图例，想让它们横着排，可以设置 `ncol=2`。
- **`frameon` (边框)**: 设置为 `False` 可以去掉图例周围的方框。

### 图片保存

```python
# 保存图片
plt.savefig('sz一小时温度变化.jpg')
```

**注意**！在show之后图片会从内存中释放，要先保存图片！

### 完整过程

```python
import random
import matplotlib.pyplot as plt
from pylab import mpl
# 设置显示中文字体
mpl.rcParams['font.sans-serif'] = ['simHei']
# 设置正常显示符号
mpl.rcParams["axes.unicode_minus"] = False

# 绘制一小时内的气温图
x_axsis = range(0,60)
y_axsis_tempr = [random.uniform(15.0,20.0) for i in x_axsis]

#设置画布
plt.figure(figsize=(16,7),dpi=100)

#color->折线的颜色
plt.plot(x_axsis,y_axsis_tempr,color='blue')

#散点图
plt.scatter(x_axsis,y_axsis_tempr,color='red')

# 分隔的标签
x_ticks_label = [f'11点{i}分' for i in x_axsis]
plt.xticks(x_axsis[::5],x_ticks_label[::5])
y_range = range(15, 21)
plt.yticks(y_range[::1], [f"{i}℃" for i in y_range][::1])
# 设置x，y周的刻度的字体大小，主副刻度
plt.tick_params(axis='y', which='major', labelsize=15)
plt.tick_params(axis='x', which='minor', labelsize=14)

# 显示网格
# linestyle是样式！
# alpha是透明度
plt.grid(True,'both',color='brown',linestyle=':',alpha=0.4)



plt.title('深圳一小时内气温图',size=20)
plt.xlabel('时间/min',size=16)
plt.ylabel('温度/℃',size=16)

# 保存图片
plt.savefig('sz一小时温度变化.jpg')

# show之后图片会从内存中释放，要先保存图片再show
plt.show()
```