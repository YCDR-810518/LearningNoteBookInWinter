# 这是一个示例 Python 脚本。
#from curses.ascii import isdigit

# 按 Shift+F10 执行或将其替换为您的代码。
# 按 双击 Shift 在所有地方搜索类、文件、工具窗口、操作和设置。

raw_data = ["85", "92", "ERROR", "105", "78", "WARNING", "99", "120"]

# 清洗
cleaned_data = [int(x) for x in raw_data if x.isdigit()]
print(f'清洗后的数据：{cleaned_data}')

#过滤
filed_data = list(filter(lambda x: x >= 80, cleaned_data))
print(f'过滤后的数据；{filed_data}')

#归一化
ultimate_data = []
for x in filed_data:
    ultimate_data.append((x - min(filed_data)) / (max(filed_data) - min(filed_data)))
print(ultimate_data)

#初始化空列表
ultimate_data_Dict = {'核心过载':[],'运转正常':[]}
for x in ultimate_data:
    if x>0.9:
        ultimate_data_Dict['核心过载'].append(float(x))
    else:
        ultimate_data_Dict['运转正常'].append(float(x))

print(ultimate_data_Dict)