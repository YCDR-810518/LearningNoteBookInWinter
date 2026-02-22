# 这是一个示例 Python 脚本。

# 按 Shift+F10 执行或将其替换为您的代码。
# 按 双击 Shift 在所有地方搜索类、文件、工具窗口、操作和设置。
class Animal:
    #这里是调用内置方法进行类的初始化
    def __init__(self, name):
        self.__name = name
    # 这里给所有子类留下了一个获取名称的接口
    def get_name(self):
        return self.__name
    def speak(self):
        print(f"我的名字是{self.get_name()}，尚未分配具体的叫声QAQ")
class Dog(Animal):
    #对speak方法进行重写
    def speak(self):
        print(f"汪呜，本汪的名字是{self.get_name()}汪! ")
class Cat(Animal):
    def speak(self):
        print(f"喵呜，🐱的名字是{self.get_name()}喵！")
cat_1 = Cat("大橘")
cat_1.speak()
dog_1 = Dog("大黄")
dog_1.speak()