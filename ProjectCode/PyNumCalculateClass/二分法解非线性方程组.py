import numpy as np
class Calculator:
    def __init__(self, a, x_up, x_low):
        self.a = a
        self.x_up = x_up
        self.x_low = x_low
        self.LIMIT = 1e-20

    def func(self, x):
        return x * x - self.a

    def result(self):
        iter((self.x_up, self.x_low))
        iter_ = 0
        while (self.x_up - self.x_low)*(self.x_up - self.x_low) > self.LIMIT:
            center = (self.x_low + self.x_up)/2
            iter_ += 1
            if self.func(center) > 0 :
                self.x_up = center
                print(f'第{iter_-1}次:')
                print(f'上限：{self.x_up} 下限{self.x_low},函数中值大于0')
            if self.func(center) < 0 :
                self.x_low = center
                print(f'第{iter_-1}次:')
                print(f'上限：{self.x_up} 下限{self.x_low},函数中值小于0')
        print(f'结果为：{((self.x_up+self.x_low)/2)}')


test = Calculator(2, 1.5, 1.4)

test.result()





