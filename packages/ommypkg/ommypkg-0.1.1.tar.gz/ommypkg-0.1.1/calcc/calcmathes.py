#Program to calculate
class Calculator():
    def __init__(self):
        self.result = 0
    def add(self,*args):
        self.result = 0
        for i in args:
            self.result += i
        return self.result
    def multiply(self,*args):
        self.result = 1
        for i in args:
            self.result *= i
        return self.result
