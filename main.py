import math
import struct
import sys
import io

import numpy as np
import pygame as pg
from pygame import mixer
from pydub import AudioSegment

# graphics.py file
import graphics

# Manuel Marchand, Ethan Dunn


pg.init()

# ensure a sound device is connected
while True:
    try:
        mixer.init()
        break
    except:
        print("NO SOUND DEVICE FOUND")

# setup window
SCREEN_WIDTH = 1500
SCREEN_HEIGHT = 300
screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pg.RESIZABLE)
pg.display.set_caption("Music Visualizer")
text_font = pg.font.SysFont("arial", 16)
clock = pg.time.Clock()
frame_rate = 60
mixer.music.set_volume(0.3)
type = None


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


def pcm_to_sound(file_stream):
    before = file_stream.tell()
    temp_data = np.frombuffer(file_stream.read(), dtype=np.int16)
    file_stream.seek(before)
    return pg.mixer.Sound(temp_data)


def pause(file_stream):
    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                end(file_stream)
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_SPACE:
                    music = pcm_to_sound(file_stream)
                    return music


def miliseek(time, block_size):
    fpmili = frame_rate / 1000
    pos = int((pg.time.get_ticks() - time) * fpmili * block_size)
    remainder = pos % 4
    if remainder != 0:
        if remainder <= 2:
            pos = pos - remainder
        else:
            pos = pos + (4 - remainder)
    if pos < 0:
        pos = 0
    return pos


def main_menu():
    message_start = 0
    message = False
    while True:
        # handle text
        screen.fill("white")
        # centered rectangle with text inside, ensures text is always centered
        text = text_font.render("Drag a .wav or .mp3 into this window", True, rgb(pg.time.get_ticks()))
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
                if event.file.endswith(".wav"):
                    wav_header(event.file)
                elif event.file.endswith(".mp3"):
                    mp3_decoder(event.file)
                else:
                    message = True
                    message_start = pg.time.get_ticks()
        clock.tick()
        if message:
            # draw error on screen for 1000 ticks
            draw_text("Wrong file type", text_font, "red", 10, 40)
            if pg.time.get_ticks() > message_start + 1000:
                message = False
        pg.display.update()


def wav_header(input_file):
    # open the file in read only "r" binary mode "b"
    file_stream = open(input_file, "rb")
    header_meaning = ["RIFF", "ChunkSize", "WAVE", "fmt ", "Sub chunk1size", "audio format", "channel count",
                      "samplerate", "byte rate", "block align", "bits per sample", "data", "sub chunk 2 size"]
    # H = short int, I = long int
    header_data = struct.unpack("<IIIIIHHIIHHII", file_stream.read(44))
    # check if the file is a 16 bit pcm wave file
    if header_data[0] == 1179011410 and header_data[2] == 1163280727 and header_data[10] == 16:
        for i in range(0, len(header_data)):
            print(header_meaning[i], header_data[i])
        byte_rate = header_data[8]
        block_size = int(byte_rate / frame_rate)
        print(block_size)
        visualizer(file_stream, block_size)
    else:
        print("Unsupported wav file, only 16 bit wav files are supported")
        file_stream.close()
        main_menu()


def mp3_decoder(input_file):
    audio = AudioSegment.from_mp3(input_file)
    pcm_data = audio.raw_data
    pcm_file = io.BytesIO()
    pcm_file.write(pcm_data)
    pcm_file.seek(0)
    byte_rate = audio.frame_rate * audio.channels * 2
    block_size = int(byte_rate / frame_rate)
    visualizer(pcm_file, block_size)


def visualizer(file_stream, block_size):
    file_stream.seek(0, 2)
    length = file_stream.tell()
    file_stream.seek(0)
    inc = 10000
    graphic_screen = 0
    vol = 0.3
    music = pcm_to_sound(file_stream)
    time = pg.time.get_ticks()
    music.play()
    while True:
        mixer.music.set_volume(vol)
        data = file_stream.read(block_size)
        decoded_data = np.frombuffer(data, dtype=np.int16)
        screen.fill((0, 0, 0))
        draw_text(str(round(file_stream.tell() / length * 100)) + "%", text_font, "white", 10, 10)
        if len(decoded_data) == 0:
            file_stream.close()
            main_menu()
        wave_form = graphics.Waveform(screen, decoded_data, rgb(pg.time.get_ticks()))
        match graphic_screen:
            case 0:
                wave_form.histogram()
            case 1:
                wave_form.line()
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
                if event.key == pg.K_m:
                    if graphic_screen == 0:
                        graphic_screen = 1
                    else:
                        graphic_screen = 0
                if event.key == pg.K_SPACE:
                    music.stop()
                    music = pause(file_stream)
                    music.play()
                if event.key == pg.K_LEFT and time - inc > 0:
                    time -= inc
                if event.key == pg.K_RIGHT:
                    time += inc
                if event.key == pg.K_RIGHT or event.key == pg.K_LEFT and time - inc > 0:
                    pos = miliseek(pg.time.get_ticks() - time, block_size)
                    file_stream.seek(pos)
                    music.stop()
                    music = pcm_to_sound(file_stream)
                    music.play()

            if event.type == pg.VIDEOEXPOSE:
                pos = miliseek(pg.time.get_ticks() - time, block_size)
                file_stream.seek(pos)


main_menu()
