import pygame as pg
from numpy.fft import fft
import numpy as np


# function that maps ranges
def map_range(range1: tuple, range2: tuple, value):
    slope = (range2[1] - range2[0]) / (range1[1] - range1[0])
    return range2[0] + slope * (value - range1[0])


class Waveform:
    def __init__(self, screen, spect_data, color):
        self.screen = screen
        self.spect_data = spect_data
        self.color = color
        self.rect_count = 128

    def line(self):
        xy = list()
        length = len(self.spect_data)
        interval = self.screen.get_width() / length
        # create all points to draw lines between for wave form
        for i in range(0, length):
            value = map_range((-32768, 32767), (0, self.screen.get_height()), self.spect_data[i])
            xy.append((interval * i, value))
        # actually draw them
        pg.draw.lines(self.screen, self.color, False, xy, 2)

    def histogram(self):
        space = 5
        # calculating space between rectangle
        interval = self.screen.get_width() / self.rect_count
        interval2 = ((self.screen.get_width()) / (self.rect_count + space))
        # use fourier transforms to visualize the data
        data = abs(fft(self.spect_data, self.rect_count, -1, "ortho"))
        normalized_data = data / np.linalg.norm(data)
        # actually draw the bars
        for i in range(0, self.rect_count):
            height = normalized_data[i] * (self.screen.get_height() * 8)
            rect = (i * (interval + space), self.screen.get_height() - height, interval2, height)
            pg.draw.rect(self.screen, self.color, rect)
