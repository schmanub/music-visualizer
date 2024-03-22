import pygame as pg
import sys
import math

# Manuel Marchand, Ethan Dunn

pg.init()

# setup window
SCREEN_WIDTH = 400
SCREEN_HEIGHT = 200
screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pg.RESIZABLE)
pg.display.set_caption("Music Visualizer")
text_font = pg.font.SysFont("arial", 20)
clock = pg.time.Clock()

bitrate_table = {
    0b00010000: 32,
    0b00100000: 40,
    0b00110000: 48,
    0b01000000: 56,
    0b01010000: 64,
    0b01100000: 80,
    0b01110000: 96,
    0b10000000: 112,
    0b10010000: 128,
    0b10100000: 160,
    0b10110000: 192,
    0b11000000: 224,
    0b11010000: 256,
    0b11100000: 320,
}

sample_rate_table = {
    0b00: 44100,
    0b01: 48000,
    0b10: 32000,
}


def draw_text(text, font, color, x, y):
    img = font.render(text, True, color)
    screen.blit(img, (x, y))


def rgb():
    m = .5
    x = pg.time.get_ticks() / 500
    return 255 * (m * (math.cos(x)) + m), 255 * (m * (math.cos(x + (math.pi * (2 / 3)))) + m), 255 * (
            m * (math.cos(x + (math.pi * (4 / 3)))) + m)


def main_menu():
    message_start = 0
    message = False
    while True:
        screen.fill("white")
        text = text_font.render("Drag an MP3 into this window", True, rgb())
        text_rect = text.get_rect(center=(screen.get_width() / 2, screen.get_height() / 2))
        screen.blit(text, text_rect)
        #draw_text("Drag an MP3 into this window", text_font, rgb(), 10, 10)
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
