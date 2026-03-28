# 将生成的代码分批次复制到https://flowchart.js.org/即可查看
from pyflowchart import Flowchart

code = None

# 读取你写的 agent_control.py
with open('agent_control.py', 'r', encoding='utf-8') as f:
    code = f.read()

# 转换
fc = Flowchart.from_code(code)
print('下面是主函数的相关逻辑')
print(fc.flowchart()) # 这一步会输出 flowchart.js 语法，你可以把它贴到任何支持的编辑器

with open('agent_control.py', 'r', encoding='utf-8') as f:
    code = f.read()

fc = Flowchart.from_code(code)
print('下面是控制函数的相关逻辑')
print(fc.flowchart()) # 这一步会输出 flowchart.js 语法，你可以把它贴到任何支持的编辑器

with open('draw.py', 'r', encoding='utf-8') as f:
    code = f.read()

fc = Flowchart.from_code(code)
print('下面是绘图函数的相关逻辑')
print(fc.flowchart()) # 这一步会输出 flowchart.js 语法，你可以把它贴到任何支持的编辑器

