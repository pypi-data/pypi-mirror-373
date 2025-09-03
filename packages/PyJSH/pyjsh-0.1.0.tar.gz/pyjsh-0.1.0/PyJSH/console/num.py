#project2/PyJSH/console/num.py
class Num:
    def __init__(self, math):
        self.math = math
        self.value = eval(math)  

    def __str__(self):
        return str(self.value)    # print(...) осыны қолданады

    def __repr__(self):
        return f"Num({self.math!r}) = {self.value}"