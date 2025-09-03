# window/open.py (ұсынылатын құрылым)
import pygame
from pygame.locals import FULLSCREEN, QUIT

def create_screen():
    pygame.init()
    return pygame.display.set_mode((0,0), FULLSCREEN)

def main_loop(draw_callback=None, fps=60):
    screen = create_screen()
    clock = pygame.time.Clock()
    running = True
    while running:
        screen.fill((255,255,255))
        for ev in pygame.event.get():
            if ev.type == QUIT:
                running = False
        if draw_callback:
            draw_callback(screen)
        pygame.display.flip()
        clock.tick(fps)

if __name__ == "__main__":
    main_loop()