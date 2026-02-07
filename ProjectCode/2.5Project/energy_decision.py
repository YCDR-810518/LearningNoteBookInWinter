import json
with open('energy_data.json', 'r', encoding='utf-8') as f:
    data_s = json.load(f)
    print(type(data_s))
print(json.dumps(data_s, indent=4, ensure_ascii=False))

# 多层嵌套，要先拆包
# 顺便清洗过滤数据
def plain_structure(data):
    num_list = []
    # 判断当前这层的类型
    if isinstance(data, list):
        for item in data:
            num_list.extend(plain_structure(item))
    elif isinstance(data, dict):
        for value in data.values():
            num_list.extend(plain_structure(value))
    else:
        clean_data = str(data).strip().strip('\r').replace(' ', '').replace(',', '.')
        try:
            num_list.append(int(clean_data,0))
        except (ValueError,TypeError):
            try:
                num_list.append(float(clean_data))
            except (ValueError,TypeError):
                pass
    return num_list

data_cleaned = plain_structure(data_s)
print(data_cleaned)

import math
# 数据的进一步过滤
# 无穷的出现，导致我的最大值-最小值也是一个无穷，还有nan值混入其中，需要进一步过滤
data_cleaned_deep_1 = [x for x in data_cleaned if math.isfinite(x)]
print(data_cleaned_deep_1)

# 再次过滤，清除异常数据
limit = 5000
data_cleaned_deep_2 = [x for x in data_cleaned_deep_1 if abs(x) < limit]

# 保留大于80的数字并进行归一化
ultimate_data = []
for x in data_cleaned_deep_2:
    if x >= 80:
        ultimate_data.append((x - min(data_cleaned_deep_2)) / (max(data_cleaned_deep_2) - min(data_cleaned_deep_2)))
print(ultimate_data)

import matplotlib.pyplot as plt

plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
plt.rcParams['axes.unicode_minus'] = False    # 用来正常显示负号

plt.hist(ultimate_data, bins=50) # 画直方图看分布
plt.xlabel(f"核心运载温度水平[归一化到0-1区间]")
plt.ylabel('出现的频率')
plt.show()