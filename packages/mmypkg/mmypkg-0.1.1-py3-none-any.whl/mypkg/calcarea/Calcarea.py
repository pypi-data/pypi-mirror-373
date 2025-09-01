class Rectangle():
    def __init__(self, *args):
        self.length = args[0]
        self.breadth = args[1]
    def area(self):
        result = self.length * self.breadth
        return result
class Square():
    def __init__(self,len):
        self.length = len
    def area(self):
        result = self.length**2
        return result
def calculate_area(shape):
    return shape.area()
    

