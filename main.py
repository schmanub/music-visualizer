import pygame as pg
import numpy as np
import sys, math, struct

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


def int_list_to_hex(input_list):
    output_list = list()
    for item in input_list:
        output_list.append(hex(item))
    return output_list


def draw_text(text, font, color, x, y):
    img = font.render(text, True, color)
    screen.blit(img, (x, y))


def rgb():
    m = .5
    x = pg.time.get_ticks() / 500
    return int(255 * (m * (math.cos(x)) + m)), int(255 * (m * (math.cos(x + (math.pi * (2 / 3)))) + m)), int(255 * (
            m * (math.cos(x + (math.pi * (4 / 3)))) + m))


def main_menu():
    message_start = 0
    message = False
    while True:
        # handle text
        screen.fill("white")
        text = text_font.render("Drag a .wav into this window", True, rgb())
        text_rect = text.get_rect(center=(screen.get_width() / 2, screen.get_height() / 2))
        screen.blit(text, text_rect)

        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()
            elif event.type == pg.DROPFILE:
                print("File path: ", event.file)
                if not event.file.endswith(".wav"):
                    message = True
                    message_start = pg.time.get_ticks()
                else:
                    wav_visualizer(event.file)
        clock.tick()
        if message:
            draw_text("Error", text_font, "red", 10, 40)
            if pg.time.get_ticks() > message_start + 1000:
                message = False
        pg.display.update()


def wav_visualizer(input_file):
    # open the file in read only "r" binary mode "b"
    file_stream = open(input_file, "rb")
    header_meaning = ["RIFF", "ChunkSize", "WAVE", "fmt ", "Subchunk1size", "audioformat", "channelnum", "samplerate",
                      "byterate", "blockalign", "bits per sample"]
    header_data = struct.unpack("<IIIIIHHIIHH", file_stream.read(36))
    # check if the file is a 16 bit pcm wave file
    if header_data[0] == 1179011410 and header_data[2] == 1163280727 and header_data[10] == 16:
        for i in range(0, len(header_data)):
            print(header_meaning[i], header_data[i])
        data = file_stream.read()
    else:
        print("Unsupported wave file")
    file_stream.close()


main_menu()
