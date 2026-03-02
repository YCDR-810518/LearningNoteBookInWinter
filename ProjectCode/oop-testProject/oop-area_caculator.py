import math
# 引入这个库，可以保证基类下的所有子类都实现该抽象方法
from abc import ABC, abstractmethod

# 下面是一个抽象基类，规定了每个子类要实现的方法，否则无法实例化
class Shape(ABC):
    #类变量区，属于类本身，被所有类&实例共享
    #创建的形状总数
    shape_num = 0
    # 这里放的是初始化需要传入的参数，若为self则不用传参
    def __init__(self):
        Shape.shape_num +=1
        # 空操作位符，留着占位置，否则会报错
        pass
    # 封装好公开接口，留给用户调用
    @classmethod
    @abstractmethod
    def count(cls):
        return cls.shape_num

    @abstractmethod
    def area(self):
        pass

class Circle(Shape):
    circ_num = 0
    def __init__(self, radius):
        Circle.circ_num += 1
        super().__init__()
        self.radius = radius
    #伪装属性，用@property修饰器
    @property
    def area(self):
        return math.pi * (self.radius ** 2)
    @classmethod
    def count(cls):
        return cls.circ_num

class Rectangle(Shape):
    rect_num = 0
    def __init__(self, width, height):
        Rectangle.rect_num += 1
        super().__init__()
        self.width = width
        self.height = height
    @property
    def area(self):
        if self.width <= 0 or self.height <= 0:
            raise ValueError
        return self.width * self.height
    @classmethod
    def count(cls):
        return cls.rect_num


