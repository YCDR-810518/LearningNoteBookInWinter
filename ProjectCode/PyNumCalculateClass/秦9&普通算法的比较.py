# 这是一个示例 Python 脚本。

# 按 ⌃R 执行或将其替换为您的代码。
# 按 双击 ⇧ 在所有地方搜索类、文件、工具窗口、操作和设置。


class Calculate:
    def __init__(self, num_start, num_end, x):
        self.num_start = num_start
        self.num_end = num_end
        self.x = x

    def qin_method(self):
        result = self.num_end + 1
        for i in range(self.num_end, self.num_start, -1):
            result = result * self.x + i
        return result

    def normal_method(self):
        result = 0
        if self.x < 1:
            # 逆向计算：从 n 到 0
            # 此时为了效率，应该先算出最高的幂，然后每次除以 x (但除法有精度风险)
            for i in range(self.num_end, self.num_start-1, -1):
                result += (i + 1) * (self.x ** i)
        else:
            # 正向计算：从 0 到 n
            for i in range(self.num_start, self.num_end+1):
                result += (i + 1) * (self.x ** i)

        return result

# 实例化
x1 = 0.1
x2 = 1
x3 = 2

start = 0
end = 100000

t1 = Calculate(start, end, x1)
t2 = Calculate(start, end, x2)
t3 = Calculate(start, end, x3)

import time
def speed(obj, x):
    t_1 = time.perf_counter()
    n1 = obj.qin_method()
    t_2 = time.perf_counter()
    t_3 = time.perf_counter()
    n2 = obj.normal_method()
    t_4 = time.perf_counter()
    print(f'数字{x},在用秦氏方法计算用时{(t_2-t_1)*1000:.4f}ms')
    print(f'结果为：{n1}')
    print(f'数字{x},在用普通方法计算用时{(t_4 - t_3) * 1000:.4f}ms')
    print(f'结果为：{n2}')

speed(t1, x1)
speed(t2, x2)
speed(t3, x3)

from decimal import Decimal
big_int = t3.qin_method()
formatted_str = f"{Decimal(big_int):.10E}"
print(formatted_str)
