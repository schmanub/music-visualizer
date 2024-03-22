import pygame as pg
import sys

# Manuel Marchand, Ethan Dunn

pg.init()

# setup window
screen = pg.display.set_mode((400, 200))
pg.display.set_caption("Music Visualizer")
text_font = pg.font.SysFont("arial", 20)
clock = pg.time.Clock()


def draw_text(text, font, color, x, y):
    img = font.render(text, True, color)
    screen.blit(img, (x, y))


def main_menu():
    message_start = 0
    message = False
    while True:
        screen.fill("white")
        draw_text("Drag an MP3 into this window", text_font, 0, 10, 10)
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()
            elif event.type == pg.DROPFILE:
                print("File path: ", event.file)
                if not event.file.endswith(".mp3"):
                    message = True
                    message_start = pg.time.get_ticks()
                else:
                    file_stream = open(event.file, "rb")
                    print(file_stream.read(100))
        clock.tick(60)
        if message:
            draw_text("Thats not an MP3!", text_font, "red", 10, 40)
            if pg.time.get_ticks() > message_start + 1000:
                message = False
        pg.display.update()


main_menu()
