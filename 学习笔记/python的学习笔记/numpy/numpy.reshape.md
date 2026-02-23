# numpy.reshape
```python
numpy.reshape(a, /, shape, order='C', *, copy=None)
```

作用：在不改变的情况下，重新改变数组的形状

## 参数说明：

* a-> 类数组
  用来改变形状的数组
* shape-> 要改变成的形状（int/tupule of int）
  新的形状应当与原来的形状**兼容**
  * 整数->长度为该整数的一维数组
  * 整数元组—>注意元素个数匹配
  * 形状的某个维度可以为 -1->自动推断
* order->{'C','F','A'}***可选***
  * 'C'->按照类似C语言的索引顺序读取&写入元素，最后一个轴索引变化最快，第一个轴索引变化最慢
  * “F”->按照类似 Fortran 的索引顺序读取/写入元素，第一个索引变化最快，最后一个索引变化最慢
  * “A”表示如果数组在内存中`a`是 Fortran*连续的*，则使用类似 Fortran 的索引顺序读取/写入元素；否则，使用类似 C 的顺序
* copy->bool,***可选* **默认为None**（不可以作为参数传入！）**在后面用.copy()进行复制！
  * 如果为真`True`，则复制数组数据。
  * 如果为`None`假，则仅当需要时才会进行复制`order`。
  * 对于假，如果无法避免复制，则会`False`引发异常。

## 返回值

如果可能，这将创建一个新的**视图对象**

* 注意！对重塑后的视图对象进行改动时，会导致原数组发生变化

否则，将创建一个副本。

请**注意**，无法保证返回数组的*内存布局（C 或 Fortran 连续布局）。*

## 相关程序实践

```python
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
```

```shell
C:\Users\Administrator\.local\bin\uv.exe run D:/Documents/GitHub/LearningNoteBookInWinter/学习笔记/python的学习笔记/dailyWorkProject/.venv/Scripts/python.exe D:\Documents\GitHub\LearningNoteBookInWinter\学习笔记\python的学习笔记\dailyWorkProject\2.8Project.py 

用reshape方法自动推断长度，展开为一维数组
[ 0  1  2  3  4  5  6  7  8  9 10 11]
数组维度：1
数组形状:(12,)

用reshape方法自动推断维度数，重塑为三维数组
[[[ 0  1  2]
  [ 3  4  5]]

 [[ 6  7  8]
  [ 9 10 11]]]
数组维度：3
数组形状:(2, 2, 3)

进程已结束，退出代码为 0

```

