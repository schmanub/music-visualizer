import pygame as pg


def map_range(range1: tuple, range2: tuple, value):
    slope = (range2[1] - range2[0]) / (range1[1] - range1[0])
    return range2[0] + slope * (value - range1[0])


class Waveform:
    def __init__(self, screen, spect_data, color):
        self.screen = screen
        self.spect_data = spect_data
        self.color = color

    def big(self):
        rect_count = len(self.spect_data)
        interval = self.screen.get_width() / rect_count
        # rectangle drawing part
        for i in range(0, rect_count):
            value = map_range((-32768, 32768), (0, 1), self.spect_data[i])
            height = value * self.screen.get_height()
            rect = (i * interval, (self.screen.get_height() - height) / 2, interval, height)
            pg.draw.rect(self.screen, self.color, rect)

    def tiny(self):
        rect_count = len(self.spect_data)
        interval = self.screen.get_width() / rect_count
        # rectangle drawing part
        for i in range(0, rect_count):
            value = map_range((-32768, 32768), (0, 1), self.spect_data[i])
            height = value * self.screen.get_height()
            rect = (i * interval, height, interval, 10)
            pg.draw.rect(self.screen, self.color, rect)

