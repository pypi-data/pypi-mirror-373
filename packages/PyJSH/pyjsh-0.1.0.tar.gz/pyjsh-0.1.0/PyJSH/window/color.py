#project2/PyJSH/window/color.py
from pygame import *
class Color:
    def __init__(self):
        self.black=(0,0,0)
        self.white=(255,255,255)
        self.red=(255,0,0)
        self.green=(0,255,0)
        self.blue=(0,0,255)
    def to_bgcolor(self,color):
        display.set_mode((0,0),FULLSCREEN).fill(color)
COLOR=Color()