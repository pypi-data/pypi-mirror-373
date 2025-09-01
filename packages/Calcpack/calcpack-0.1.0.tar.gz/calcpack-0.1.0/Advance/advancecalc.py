#Program to calculate area
class Rectangle():
    def __init__(self, *args):
        self.length = args[0]
        self.breadth = args[1]
    def area(self):
        return(self.length * self.breadth)

class Square():
    def __init__(self,len):
        self.length = len
    def area(self):
        return(self.length**2)

def calculate_area(shape):
    return(shape.area())