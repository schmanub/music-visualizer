import math
import struct
import sys

import numpy as np
import pygame as pg
from pygame import mixer

# Manuel Marchand, Ethan Dunn

pg.init()
mixer.init()
mixer.music.set_volume(0.2)


# setup window
SCREEN_WIDTH = 700
SCREEN_HEIGHT = 300
screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pg.RESIZABLE)
pg.display.set_caption("Music Visualizer")
text_font = pg.font.SysFont("arial", 20)
clock = pg.time.Clock()
frame_rate = 60


def map_range(range1: tuple, range2: tuple, val):
    slope = (range2[1] - range2[0]) / (range1[1] - range1[0])
    return range2[0] + slope * (val - range1[0])


def draw_text(text, font, color, x, y):
    img = font.render(text, True, color)
    screen.blit(img, (x, y))


def end(file_stream):
    file_stream.close()
    pg.quit()
    sys.exit()


def rgb():
    m = .5
    x = pg.time.get_ticks() / 500
    return int(255 * (m * (math.cos(x)) + m)), int(255 * (m * (math.cos(x + (math.pi * (2 / 3)))) + m)), int(255 * (
            m * (math.cos(x + (math.pi * (4 / 3)))) + m))


def spectrum_analysis(spect_data, rect_count):
    length = len(spect_data)
    #for i in range(0, length):

    interval = screen.get_width() / rect_count
    bin_width = 65536 / rect_count
    #print(bin_width)
    for i in range(0, rect_count):
        value = map_range((-32768, 32768), (0, 1), spect_data[i])
        print(value)
        height = value * screen.get_height()
        pg.draw.rect(screen, rgb(), (i * interval, (screen.get_height() - height) / 2, interval, height))


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
        sample_rate = header_data[7]
        # bytes per sample = byte rate / sample rate
        # bytespsample = int(byte_rate/sample_rate)
        # block_size2 = int(bytespsample * (sample_rate/60))
        block_size = int(byte_rate / frame_rate)
        visualizer(file_stream, block_size)
    else:
        print("Unsupported wav file, only 16 bit wav files are supported")
        file_stream.close()
        main_menu()


def visualizer(file_stream, block_size):
    mixer.music.play()
    rect_count = 128
    while True:
        try:
            data = file_stream.read(block_size)
        except:
            end(file_stream)
        decoded_data = np.frombuffer(data, dtype=np.int16)
        # stereo = np.split(decoded_data, 2)
        screen.fill((0, 0, 0))
        spectrum_analysis(decoded_data, rect_count)
        clock.tick(frame_rate)
        pg.display.update()
        for event in pg.event.get():
            if event.type == pg.QUIT:
                end(file_stream)


main_menu()
