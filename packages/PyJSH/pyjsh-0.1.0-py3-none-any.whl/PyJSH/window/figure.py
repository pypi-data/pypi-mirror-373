#project2/PyJSH/window/figure.py
import pygame
from pygame.locals import FULLSCREEN

class Figure:
    def __init__(self, model, color, scale, position):
        self.model = model
        self.color = color
        self.scale = scale
        self.position = position

        # Терезе ашамыз
        self.screen = pygame.display.set_mode((0, 0), FULLSCREEN)

    def draw(self):
        rect = pygame.Rect(self.position[0], self.position[1], self.scale[0], self.scale[1])
        pygame.draw.rect(self.screen, self.color, rect)  # тіктөртбұрыш мысал үшін
        pygame.display.flip()