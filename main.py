import math
import struct
import sys

import numpy as np
import pygame as pg
from pygame import mixer

# graphics.py file
import graphics

# Manuel Marchand, Ethan Dunn


pg.init()
mixer.init()

# setup window
SCREEN_WIDTH = 1500
SCREEN_HEIGHT = 300
screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pg.RESIZABLE)
pg.display.set_caption("Music Visualizer")
text_font = pg.font.SysFont("arial", 16)
clock = pg.time.Clock()
frame_rate = 60
mixer.music.set_volume(0.3)


def draw_text(text, font, color, x, y):
    img = font.render(text, True, color)
    screen.blit(img, (x, y))


def end(file_stream):
    file_stream.close()
    pg.quit()
    sys.exit()

def rgb(time):
    # 3 cos waves all 120 degrees out of phase with each other
    x = time / 500
    return (int(255 * (0.5 * (math.cos(x)) + 0.5)),
            int(255 * (0.5 * (math.cos(x + (math.pi * (2 / 3)))) + 0.5)),
            int(255 * (0.5 * (math.cos(x + (math.pi * (4 / 3)))) + 0.5)))


def main_menu():
    message_start = 0
    message = False
    while True:
        # handle text
        screen.fill("white")
        # centered rectangle with text inside, ensures text is always centered
        text = text_font.render("Drag a .wav into this window", True, rgb(pg.time.get_ticks()))
        text_rect = text.get_rect(center=(screen.get_width() / 2, screen.get_height() / 2))
        screen.blit(text, text_rect)
        # check for events
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()
            # a file has been dragged into the window
            elif event.type == pg.DROPFILE:
                print("File path: ", event.file)
                if not event.file.endswith(".wav"):
                    message = True
                    message_start = pg.time.get_ticks()
                else:
                    mixer.music.load(event.file)
                    wav_header(event.file)
        clock.tick()
        if message:
            # draw error on screen for 1000 ticks
            draw_text("Error", text_font, "red", 10, 40)
            if pg.time.get_ticks() > message_start + 1000:
                message = False
        pg.display.update()


def wav_header(input_file):
    # open the file in read only "r" binary mode "b"
    file_stream = open(input_file, "rb")
    header_meaning = ["RIFF", "ChunkSize", "WAVE", "fmt ", "Sub chunk1size", "audio format", "channel count",
                      "samplerate", "byte rate", "block align", "bits per sample", "data", "sub chunk 2 size"]
    header_data = struct.unpack("<IIIIIHHIIHHII", file_stream.read(44))
    # check if the file is a 16 bit pcm wave file
    if header_data[0] == 1179011410 and header_data[2] == 1163280727 and header_data[10] == 16:
        for i in range(0, len(header_data)):
            print(header_meaning[i], header_data[i])
        byte_rate = header_data[8]
        block_size = int(byte_rate / frame_rate)
        visualizer(file_stream, block_size)
    else:
        print("Unsupported wav file, only 16 bit wav files are supported")
        file_stream.close()
        main_menu()


def visualizer(file_stream, block_size):
    graphic_screen = 0
    vol = 0.3
    rect_count = 128
    mixer.music.play()
    while True:
        mixer.music.set_volume(vol)
        data = file_stream.read(block_size)

        index = str(data).find("data")
        if index != -1:
            print("YES IT DOES")

        decoded_data = np.frombuffer(data, dtype=np.int16)
        screen.fill((0, 0, 0))
        draw_text(str(clock.get_fps()), text_font, "white", 10, 10)
        if len(decoded_data) == 0:
            file_stream.close()
            main_menu()
        wave_form = graphics.Waveform(screen, decoded_data, rgb(pg.time.get_ticks()))
        match graphic_screen:
            case 0:
                wave_form.big()
            case 1:
                wave_form.tiny()
        clock.tick(frame_rate)
        pg.display.update()
        for event in pg.event.get():
            if event.type == pg.QUIT:
                end(file_stream)
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_DOWN:
                    vol -= 0.1
                if event.key == pg.K_UP:
                    vol += 0.1
                if event.key == pg.K_SPACE:
                    if graphic_screen == 0:
                        graphic_screen = 1
                    else:
                        graphic_screen = 0
            if event.type == pg.VIDEOEXPOSE:
                print("MOVING WINDOW WILL CAUSE DESYNC")


main_menu()
