import pygame as pg
from menu import Game_process
from constants import FPS

pg.init() 
pg.mixer.init() 

def game_loop():
    running = True
    game = Game_process()
    clock = pg.time.Clock() 
    while running:
        clock.tick(FPS)
        game.state()
        pg.display.update()

if __name__ == '__main__':
    game_loop()