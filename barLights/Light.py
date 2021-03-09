import time
import math
import random

LIGHT_UNSET = -1
LIGHT_FADE = 0
LIGHT_BLINK = 1
LIGHT_NUM_EFFECTS = 2

RED = 0
GREEN = 1
BLUE = 2
WHITE = 3


class Light(object):
    address = 0
    mode = -1
    up = True
    on = False
    wait = False
    currentValue = None
    intendedColor = None
    previousColor = None
    timestamp = 0
    duration = 0
    waitDuration = 0
    nextActionTime = 0
    iterations = 0
    on_finish = None

    def __init__(self, address):
        self.address = address
        self.currentValue = [0, 0, 0, 0]
        self.intendedColor = [0, 0, 0, 0]

    @staticmethod
    def update_color(light, now):
        if light.wait:
            if now > light.nextActionTime:
                light.nextActionTime = now + light.duration
                light.wait = False
        elif light.up:
            Light.increment_color(light, now)
        else:
            Light.decrement_color(light, now)

    @staticmethod
    def increment_color(light, now):

        def get_new_color(intended_color, index, amount_left):
            return int(round(float(intended_color[index]) * amount_left / 2))

        if now > light.nextActionTime:
            light.up = False
            light.timestamp = now
            light.nextActionTime = light.timestamp + light.duration
        else:
            # amount_left = 1 - ((light.nextActionTime - now) / light.duration)
            amount_left = 1.0 - (math.cos((math.pi / 2) - ((math.pi / 2) * ((float(light.nextActionTime) - float(now)) / float(light.duration)))))
            light.currentValue[RED] = get_new_color(light.intendedColor, RED, amount_left)
            light.currentValue[GREEN] = get_new_color(light.intendedColor, GREEN, amount_left)
            light.currentValue[BLUE] = get_new_color(light.intendedColor, BLUE, amount_left)
            light.currentValue[WHITE] = get_new_color(light.intendedColor, WHITE, amount_left)

    @staticmethod
    def decrement_color(light, now):
        if now > light.nextActionTime:
            if light.iterations == 0:
                # print "light at 0  {}".format(light.address)
                if light.on_finish:
                    light.on_finish()
            else:
                # print "decrementing light {} {}".format(light.address, light.iterations)
                light.iterations += -1
                light.up = True
                light.timestamp = now
                light.nextActionTime = light.timestamp + light.waitDuration
                light.wait = True
                # light.waitDuration = random.randrange(0, 5000)
            light.currentValue = [0, 0, 0, 0]
        else:
            # amount_left = ((light.nextActionTime - now) / light.duration)
            amount_left = math.cos((math.pi / 2) - ((math.pi / 2) * ((float(light.nextActionTime) - float(now)) / float(light.duration))))
            # print "amount left {} {} {} {} ".format(amount_left, light.nextActionTime, self.now, light.duration)
            light.currentValue[RED] = int(round(light.intendedColor[RED] * amount_left / 2))
            light.currentValue[GREEN] = int(round(light.intendedColor[GREEN] * amount_left / 2))
            light.currentValue[BLUE] = int(round(light.intendedColor[BLUE] * amount_left / 2))
            light.currentValue[WHITE] = int(round(light.intendedColor[WHITE] * amount_left / 2))
