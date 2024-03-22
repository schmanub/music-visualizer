import pygame as pg
import sys

# Manuel Marchand, Ethan Dunn

pg.init()

# setup window
screen = pg.display.set_mode((500, 500))
pg.display.set_caption("Music Visualizer")

while True:
    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            sys.exit()