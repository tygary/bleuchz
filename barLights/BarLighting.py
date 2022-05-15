from enum import IntEnum
import time
from PixelControl import PixelControl
from ButtonController import ButtonController
from Routine import *
from Colors import Colors


NUM_PIXELS = 300

MODE_ON = 0
MODE_COLOR = 1
MODE_RAINBOW = 2
MODE_FIRE = 3
MODE_WAVE = 4
NUM_MODES = 5

ALL_PIXELS = range(0, 268)

BAR_TOP_PIXELS = range(51, 149)
BAR_BOTTOM_PIXELS = range(0, 51)
FRONT_PIXELS = range(148, 268)

FRONT_LEFT = range(250, 268)
FRONT_LEFT_MID = range(237, 250)
FRONT_MID = range(177, 237)
FRONT_RIGHT_MID = range(165, 177)
FRONT_RIGHT = range(149, 165)


class BarLighting(object):
    pixels = None
    buttons = None
    mode = 0
    on_button = False
    mode_button = False
    mode_object = None

    def __init__(self):
        self.pixels = PixelControl(NUM_PIXELS)
        self.buttons = ButtonController(self.handle_change)
        self.mode_object = None

    def handle_change(self, values):
        self.on_button = values[0] == 0

        if self.mode_button is False and values[1] is 0:
            self.change_mode()
        self.mode_button = values[1] == 0

        print "buttons changed {}".format(values)

    def change_mode(self):
        self.mode = (self.mode + 1) % NUM_MODES
        print "New Mode - {}".format(self.mode)
        if self.mode is MODE_COLOR:
            self.mode_object = PulseRoutine(self.pixels, FRONT_PIXELS, Colors.mid_green)
        elif self.mode is MODE_RAINBOW:
            self.mode_object = RainbowRoutine(self.pixels, ALL_PIXELS)
        elif self.mode is MODE_FIRE:
            self.mode_object = FireRoutine(self.pixels, ALL_PIXELS)
        elif self.mode is MODE_WAVE:
            middle_index = len(FRONT_MID)//2
            reverse_FRONT_LEFT = FRONT_LEFT[:]
            reverse_FRONT_LEFT.reverse()
            reverse_FRONT_LEFT_MID = FRONT_LEFT_MID[:]
            reverse_FRONT_LEFT_MID.reverse()
            reverse_left_FRONT_MID = FRONT_MID[middle_index:]
            reverse_left_FRONT_MID.reverse()
            self.mode_object = MultiRoutine([
                RainbowRoutine(self.pixels, BAR_TOP_PIXELS),
                RainbowRoutine(self.pixels, BAR_BOTTOM_PIXELS),
                WaveRoutine(self.pixels, reverse_FRONT_LEFT, [Colors.mid_green, Colors.mixed_blue, Colors.light_green, Colors.red], delay=1000),
                WaveRoutine(self.pixels, reverse_FRONT_LEFT_MID, [Colors.light_green, Colors.mid_green, Colors.mixed_blue, Colors.red], delay=4000),
                WaveRoutine(self.pixels, reverse_left_FRONT_MID, [Colors.mixed_blue, Colors.light_green, Colors.mid_green, Colors.red]),
                WaveRoutine(self.pixels, FRONT_MID[:middle_index], [Colors.mixed_blue, Colors.mid_green, Colors.light_green, Colors.red]),
                WaveRoutine(self.pixels, FRONT_RIGHT_MID, [Colors.light_green, Colors.mid_green, Colors.mixed_blue, Colors.red], delay=4000),
                WaveRoutine(self.pixels, FRONT_RIGHT, [Colors.mid_green, Colors.mixed_blue, Colors.light_green, Colors.red], delay=1000)
            ])
        else:
            self.mode_object = None

    def set_pixels(self, indexes, color):
        for i in indexes:
            self.pixels.setRGBW(i, color)
        self.pixels.render()

    def start(self):
        self.change_mode()
        while True:
            self.buttons.check_for_new_switch_values()
            if self.on_button:
                if self.mode is MODE_ON:
                    for i in BAR_TOP_PIXELS:
                        self.pixels.setRGBW(i, Colors.bright_white)
                    for i in BAR_BOTTOM_PIXELS:
                        self.pixels.setRGBW(i, Colors.bright_white)
                    for i in FRONT_PIXELS:
                        self.pixels.setRGBW(i, Colors.soft_white)
                elif self.mode is MODE_COLOR:
                    for i in BAR_TOP_PIXELS:
                        self.pixels.setRGBW(i, Colors.soft_white)
                    for i in BAR_BOTTOM_PIXELS:
                        self.pixels.setRGBW(i, Colors.soft_white)
                    self.mode_object.tick()
                elif self.mode is MODE_RAINBOW:
                    self.mode_object.tick()
                elif self.mode is MODE_FIRE:
                    self.mode_object.tick()
                elif self.mode is MODE_WAVE:
                    self.mode_object.tick()
            else:
                self.pixels.blackout()
                self.mode = MODE_ON
            self.pixels.render()
            # time.sleep(0.01)


bar = BarLighting()
bar.start()
