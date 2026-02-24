# 这是一个示例 Python 脚本。

# 按 Shift+F10 执行或将其替换为您的代码。
# 按 双击 Shift 在所有地方搜索类、文件、工具窗口、操作和设置。

import numpy as np
matrix_1 = np.array([[0,1,2,3],
                     [4,5,6,7],
                     [8,9,10,11]])
print(matrix_1)
# 显示维度信息
print(f'数组维度：{matrix_1.ndim}')
# 显示详细形状信息
print(f'数组形状:{matrix_1.shape}')
# 显示类型信息
print(f'数组类型：{matrix_1.dtype}')

# 将数组转置
matrix_1_T = matrix_1.T
print(matrix_1_T)
print(f'转置后的数组形状：{matrix_1_T.shape}')

# 下面进行数组的展平操作

# flatten方法
matrix_1_f = matrix_1.flatten()
print(f'\n展平后的数组：\n{matrix_1_f}')
# 显示维度信息
print(f'数组维度：{matrix_1_f.ndim}')
# 显示详细形状信息
print(f'数组形状:{matrix_1_f.shape}')

# 修改展平后的数组
matrix_1_f = [ 0 ,1, 2 ]
print(f'\n修改展平后的数组后原数组\n{matrix_1}')
print(f'修改后的展平数组\n{matrix_1_f}')

# 用reshape方法对数组进行处理

# 展平数组
matrix_1_r_f = matrix_1.reshape(-1,order='A')
print(f'\n用reshape方法自动推断长度，展开为一维数组\n{matrix_1_r_f}')
# 显示维度信息
print(f'数组维度：{matrix_1_r_f.ndim}')
# 显示详细形状信息
print(f'数组形状:{matrix_1_r_f.shape}')

# 重塑数组的形状
matrix_1_r_f = matrix_1.reshape((2,2,-1),order='A')
print(f'\n用reshape方法自动推断维度数，重塑为三维数组\n{matrix_1_r_f}')
# 显示维度信息
print(f'数组维度：{matrix_1_r_f.ndim}')
# 显示详细形状信息
print(f'数组形状:{matrix_1_r_f.shape}')