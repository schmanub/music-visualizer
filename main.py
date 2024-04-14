import math
import struct
import sys
import io

import numpy as np
import pygame as pg
from pydub import AudioSegment

# graphics.py file
import graphics

# Manuel Marchand, Ethan Dunn

pg.init()

# setup window
SCREEN_WIDTH = 1500
SCREEN_HEIGHT = 300
screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pg.RESIZABLE)
pg.display.set_caption("Music Visualizer")
text_font = pg.font.SysFont("arial", 16)
clock = pg.time.Clock()
frame_rate = 60

# function to draw text
def draw_text(text, font, color, x, y):
    img = font.render(text, True, color)
    screen.blit(img, (x, y))


# function that closes the file stream and quits the program
def end(file_stream):
    file_stream.close()
    pg.quit()
    sys.exit()


# function for generating RGB
def rgb(time):
    # 3 cos waves all 120 degrees out of phase with each other
    x = time / 500
    return (int(255 * (0.5 * (math.cos(x)) + 0.5)),
            int(255 * (0.5 * (math.cos(x + (math.pi * (2 / 3)))) + 0.5)),
            int(255 * (0.5 * (math.cos(x + (math.pi * (4 / 3)))) + 0.5)))


# converts a file stream into an array of PCM data
def pcm_to_sound(file_stream):
    before = file_stream.tell()
    temp_data = np.frombuffer(file_stream.read(), dtype=np.int16)
    file_stream.seek(before)
    return pg.mixer.Sound(temp_data)


# traps the program in a while true loop to keep everything paused
def pause(file_stream):
    draw_text("Pause", text_font, "white", screen.get_width() - 60, 10)
    pg.display.update()
    while True:
        clock.tick(frame_rate)
        for event in pg.event.get():
            if event.type == pg.QUIT:
                end(file_stream)
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_SPACE:
                    music = pcm_to_sound(file_stream)
                    screen.fill((0, 0, 0))
                    return music


# helper function for calculating where to seek when skipping forwards and backwards
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


# main function that handles the main menu
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


# wav header decoding function
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
        # call the visualizer
        visualizer(file_stream, block_size)
    else:
        print("Unsupported wav file, only 16 bit wav files are supported")
        file_stream.close()
        main_menu()


# MP3 decoding function, uses pydub
def mp3_decoder(input_file):
    audio = AudioSegment.from_mp3(input_file)
    pcm_data = audio.raw_data
    pcm_file = io.BytesIO()
    pcm_file.write(pcm_data)
    pcm_file.seek(0)
    byte_rate = audio.frame_rate * audio.channels * 2
    block_size = int(byte_rate / frame_rate)
    # call the visualizer
    visualizer(pcm_file, block_size)


# code that handles the actual visualizer graphics and IO
def visualizer(file_stream, block_size):
    # initialize local variables
    file_stream.seek(0, 2)
    length = file_stream.tell()
    file_stream.seek(0)
    inc = 10000
    graphic_screen = 0
    vol = 0.3
    music = pcm_to_sound(file_stream)
    time = pg.time.get_ticks()
    stat_time = 0
    music.play()
    stat_message = None
    # main while loop
    while True:
        # read a frame's worth of audio data
        data = file_stream.read(block_size)
        # check if we reached the end of the file
        if len(data) < block_size:
            file_stream.close()
            main_menu()
        # decode audio data
        decoded_data = np.frombuffer(data, dtype=np.int16)
        screen.fill((0, 0, 0))
        # draw the stat messages if they need to be drawn
        if stat_message is not None:
            draw_text(stat_message, text_font, "white", 10, 10)
            if stat_time < pg.time.get_ticks():
                stat_message = None
        # prepare graphics library
        wave_form = graphics.Waveform(screen, decoded_data, rgb(pg.time.get_ticks()))
        match graphic_screen:
            case 0:
                wave_form.histogram()
            case 1:
                wave_form.line()
        # py game event handling
        clock.tick(frame_rate)
        pg.display.update()
        for event in pg.event.get():
            if event.type == pg.QUIT:
                end(file_stream)
            if event.type == pg.KEYDOWN:
                # volume controls
                if event.key == pg.K_DOWN and vol > 0:
                    vol -= 0.05
                    stat_message = "-Vol: " + str(round(vol*100)) + "%"
                    stat_time = pg.time.get_ticks() + 1000
                if event.key == pg.K_UP and vol < 1:
                    vol += 0.05
                    stat_message = "+Vol: " + str(round(vol*100)) + "%"
                    stat_time = pg.time.get_ticks() + 1000
                # graphic mode switching
                if event.key == pg.K_m:
                    if graphic_screen == 0:
                        graphic_screen = 1
                    else:
                        graphic_screen = 0
                # pausing
                if event.key == pg.K_SPACE:
                    music.stop()
                    music = pause(file_stream)
                    music.play()
                # seeking left and right
                if event.key == pg.K_LEFT and time - inc > 0:
                    time -= inc
                    stat_message = "<time: " + str(round(file_stream.tell() / length * 100)) + "%"
                    stat_time = pg.time.get_ticks() + 1000
                if event.key == pg.K_RIGHT:
                    time += inc
                    stat_message = ">time: " + str(round(file_stream.tell() / length * 100)) + "%"
                    stat_time = pg.time.get_ticks() + 1000
                # additional seeking code
                if event.key == pg.K_RIGHT or event.key == pg.K_LEFT and time - inc > 0:
                    pos = miliseek(pg.time.get_ticks() - time, block_size)
                    file_stream.seek(pos)
                    music.stop()
                    music = pcm_to_sound(file_stream)
                    music.play()
            # when the window is moved we need to make sure were still in sync with the audio
            # since Windows will not run the program while its being moved but audio will keep playing
            if event.type == pg.VIDEOEXPOSE:
                pos = miliseek(pg.time.get_ticks() - time, block_size)
                file_stream.seek(pos)
        music.set_volume(vol)


# start the program
main_menu()
