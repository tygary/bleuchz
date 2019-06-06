import time, math
import random

from DmxControl import DmxControl
from PixelControl import PixelControl
from LeverInputController import LeverInputController
from Light import *


ON = 0
CLOSING_EYE = 1
OFF = 2
OPENING_EYE = 3
RED = 0
GREEN = 1
BLUE = 2

AMBIENT_LEVER = 0
PARTY_LEVER = 1
CAVE_LEVER = 2
PUPPET_LEVER = 3

LAB_MODE_DIM = 0
LAB_MODE_BRIGHT = 1
LAB_MODE_PARTY = 2

NUM_PANEL_LIGHTS = 300

MAIN_COLOR = 0
ACCENT_COLOR_1 = 1
ACCENT_COLOR_2 = 2
ACCENT_COLOR_3 = 3


class LightingControlSystem(object):
    dmx = DmxControl()
    pixel = PixelControl(NUM_PANEL_LIGHTS)
    leverValues = [1, 1, 1, 1]
    leverController = None
    now = None

    dmxInsideLights = [128, 129]
    dmxOutsideLight = 130
    dmxPedestalLight = 1
    dmxStaticBlackLight = 131
    dmxBlackLights = [17, 10]
    dmxParCan = 98
    dmxSignLight = 4
    dmxPuppetEyes = [34, 37, 40, 43, 46, 49, 52]
    dmxPuppetMushrooms = [1, 1, 1, 1]

    def __init__(self):
        self.leverController = LeverInputController(self.handle_change)
        self.initPanels()

    def handle_change(self, values):
        self.leverValues = values
        print "lever changed {}".format(values)

    def start(self):
        while True:
            self.now = int(round(time.time() * 1000))
            self.leverController.check_for_new_switch_values()

            self.processEyes()
            self.processCavePanels()
            self.processCaveBlackLights()
            self.processLab()
            self.dmx.setLight(self.dmxSignLight, [0, 0, 50])
            self.dmx.setDimmer(self.dmxOutsideLight, 200)

            self.dmx.render()
            self.pixel.render()
            self.pixel.render()
            # Do it twice because otherwise it glitches???
            time.sleep(0.01)
            continue


    # ------------------------------ Lab Lights ----------------------------------------
    left = True
    lab_delay = 200
    lab_timestamp = 0
    lab_mode = 0
    lab_pedestal_up = True
    lab_pedestal_timestamp = 0
    lab_pedestal_fade_time = 100

    def processLab(self):
        if self.leverValues[PARTY_LEVER] == 0:
            if self.lab_mode is not LAB_MODE_PARTY:
                print "party lab mode"
                self.lab_mode = LAB_MODE_PARTY
                self.lab_pedestal_timestamp = self.now
                self.lab_pedestal_up = True

            if self.now < self.lab_pedestal_timestamp + self.lab_pedestal_fade_time:
                if self.lab_pedestal_up:
                    brightness = 100 + ((self.now - self.lab_pedestal_timestamp)/self.lab_pedestal_fade_time * 155)
                    self.dmx.setLight(self.dmxPedestalLight, [brightness, brightness, brightness])
                else:
                    brightness = 100 + (155 - ((self.now - self.lab_pedestal_timestamp)/self.lab_pedestal_fade_time * 155))
                    self.dmx.setLight(self.dmxPedestalLight, [brightness, brightness, brightness])
            else:
                self.lab_pedestal_up = not self.lab_pedestal_up
                self.lab_pedestal_timestamp = self.now

            if self.now > (self.lab_delay + self.lab_timestamp):
                if self.left:
                    self.dmx.setDimmer(self.dmxInsideLights[0], 0)
                    self.dmx.setDimmer(self.dmxInsideLights[1], 255)
                    self.dmx.setLight(self.dmxParCan, [255, 0, 0])
                    self.left = False
                else:
                    self.dmx.setDimmer(self.dmxInsideLights[0], 255)
                    self.dmx.setDimmer(self.dmxInsideLights[1], 0)
                    self.dmx.setLight(self.dmxParCan, [0, 0, 0])
                    self.left = True
                self.lab_timestamp = self.now
        elif self.leverValues[AMBIENT_LEVER] == 0:
            if self.lab_mode is not LAB_MODE_BRIGHT:
                print "bright lab mode"
                self.dmx.setLight(self.dmxPedestalLight, [0, 0, 50])
                self.dmx.setDimmer(self.dmxInsideLights[0], 255)
                self.dmx.setDimmer(self.dmxInsideLights[1], 255)
                self.dmx.setLight(self.dmxParCan, [100, 0, 100])
                self.lab_mode = LAB_MODE_BRIGHT
        else:
            if self.lab_mode is not LAB_MODE_DIM:
                print "dim lab mode"
                self.dmx.setLight(self.dmxPedestalLight, [0, 0, 10])
                self.dmx.setDimmer(self.dmxInsideLights[0], 0)
                self.dmx.setDimmer(self.dmxInsideLights[1], 0)
                self.dmx.setLight(self.dmxParCan, [50, 0, 0])
                self.lab_mode = LAB_MODE_DIM

    # ------------------------------ END Lab Lights ----------------------------------------

    # ------------------------------ Cave Panels ----------------------------------------

    cave_panel_lights = [Light] * NUM_PANEL_LIGHTS

    def initPanels(self):
        for i in range(NUM_PANEL_LIGHTS):
            self.cave_panel_lights[i] = Light(i+1)

    def processCavePanels(self):
        for i in range(len(self.cave_panel_lights)):
            light = self.cave_panel_lights[i]

            if self.leverValues[CAVE_LEVER]:  # off
                self.pixel.setColor(light.address, [0, 0, 0])
            else:
                # print "processing {} - {} {} {}".format(light.address, light.currentValue[0], light.currentValue[1], light.currentValue[2])
                if light.mode == LIGHT_UNSET:
                    self.pickNewLightMode(light)
                if light.mode == LIGHT_FADE:
                    if light.wait:
                        if self.now > (light.timestamp + light.waitDuration):
                            light.wait = False
                            light.timestamp = self.now
                    elif light.up:
                        self.setNewIncrementingLightColor(light)
                    else:
                        self.setNewDecrementingLightColor(light)
                elif light.mode == LIGHT_BLINK:
                    if self.now > light.nextActionTime:
                        if light.on:
                            light.currentValue = light.previousColor
                            light.on = False
                            light.iterations += -1

                            if light.iterations == 0:
                                self.pickNewLightMode(light)
                        else:
                            light.currentValue = light.intendedColor
                            light.on = True
                        light.timestamp = self.now
                        light.nextActionTime = light.timestamp + light.duration
                self.pixel.setColor(light.address, light.currentValue)

    def pickNewLightMode(self, light):
        rand = random.randrange(0, 100)
        if rand > 90:
            light.mode = LIGHT_BLINK
        else:
            light.mode = LIGHT_FADE

        if light.mode == LIGHT_FADE:
            colorBias = random.randrange(0, 1000)
            colorIndex = 0
            breakNum1 = 700
            breakNum2 = 900
            if colorBias < breakNum1:
                colorIndex = MAIN_COLOR
            elif colorBias >= breakNum1 and colorBias < breakNum2:
                colorIndex = ACCENT_COLOR_1
            else:
                colorIndex = ACCENT_COLOR_2

            light.intendedColor = self.getNewLightColor(colorIndex)
            light.duration = random.randrange(1000, 7000)
            light.iterations = random.randrange(1, 3)
            light.up = True
            light.timestamp = self.now
            light.nextActionTime = light.timestamp + light.duration
        elif light.mode == LIGHT_BLINK:
            light.intendedColor = self.getNewLightColor(MAIN_COLOR)
            light.previousColor = self.getNewLightColor(ACCENT_COLOR_3)
            light.currentValue = light.previousColor
            light.on = False
            light.iterations = random.randrange(5, 10)
            light.timestamp = self.now
            light.duration = random.randrange(100, 700)

    cavePanelCurrentColor = [0, 0, 255]
    cavePanelNextColor = [0, 0, 255]
    cavePanelFlashColor = [0, 0, 0]
    cavePanelColorTimestamp = 0
    cavePanelColorDuration = 0
    cavePanelColorSchemeIndex = 0
    cavePanelColorSchemeIndexNew = 0
    cavePanelColorTransitioning = False

    cavePanelColorSchemes = [
        [[0, 81, 140], [0, 164, 229], [0, 61, 81], [0, 162, 216]],  # blues
        [[63, 168, 204], [117, 86, 124], [207, 255, 145], [109, 249, 186]],  # blue green purple
        [[189, 51, 7], [235, 161, 11], [140, 163, 8], [242, 187, 12]],  # red orange yellow green
        [[160, 26, 125], [49, 24, 71], [236, 64, 103], [239, 93, 96]],  # pinks
        [[15, 163, 177], [247, 160, 114], [237, 222, 164], [255, 155, 66]],  # blue orange yellow
        [[178, 247, 239], [247, 214, 224], [123, 223, 242], [242, 181, 212]],  # cotton candy
        [[178, 255, 158], [29, 211, 176], [60, 22, 66], [175, 252, 65]],  # greens
    ]

    def getNewLightColor(self, colorIndex):
        if self.now > (self.cavePanelColorTimestamp + self.cavePanelColorDuration):
            if self.cavePanelColorTransitioning:
                print "Finished Transitioning Color Scheme"
                self.cavePanelColorTransitioning = False
                self.cavePanelColorSchemeIndex = self.cavePanelColorSchemeIndexNew
                self.cavePanelColorDuration = random.randrange(8000, 30000)
                self.cavePanelColorTimestamp = self.now
            else:
                self.cavePanelColorTransitioning = True
                self.cavePanelColorSchemeIndexNew = random.randrange(0, len(self.cavePanelColorSchemes))
                self.cavePanelColorDuration = random.randrange(3000, 8000)
                self.cavePanelColorTimestamp = self.now
                print "Switching to color scheme {}".format(self.cavePanelColorSchemeIndexNew)

        colorScheme = self.cavePanelColorSchemes[self.cavePanelColorSchemeIndex]
        if self.cavePanelColorTransitioning:
            finish_time = self.cavePanelColorTimestamp + self.cavePanelColorDuration
            colorBias = int(round((1.0 - ((float(finish_time) - float(self.now)) / float(self.cavePanelColorDuration))) * 1000))
            colorChance = random.randrange(0, 1000)
            if colorChance > colorBias:
                colorScheme = self.cavePanelColorSchemes[self.cavePanelColorSchemeIndex]
            else:
                colorScheme = self.cavePanelColorSchemes[self.cavePanelColorSchemeIndexNew]

        return colorScheme[colorIndex]

    def setNewDecrementingLightColor(self, light):
        if self.now > light.nextActionTime:
            if light.iterations == 0:
                # print "light at 0  {}".format(light.address)
                self.pickNewLightMode(light)
            else:
                # print "decrementing light {} {}".format(light.address, light.iterations)
                light.iterations += -1
                light.up = True
                light.timestamp = self.now
                light.nextActionTime = light.timestamp + (2 * light.duration)
                light.wait = True
                light.waitDuration = random.randrange(0, 5000)
            light.currentValue = [0, 0, 0]
        else:

            amount_left = math.cos((math.pi / 2) - ((math.pi / 2) * ((float(light.nextActionTime) - float(self.now)) / float(light.duration))))
            # print "amount left {} {} {} {} ".format(amount_left, light.nextActionTime, self.now, light.duration)
            light.currentValue[RED] = int(round(light.intendedColor[RED] * amount_left / 2))
            light.currentValue[GREEN] = int(round(light.intendedColor[GREEN] * amount_left / 2))
            light.currentValue[BLUE] = int(round(light.intendedColor[BLUE] * amount_left / 2))
            # print "decremented to {} {} {}".format(light.currentValue[0], light.currentValue[1], light.currentValue[2])

    def setNewIncrementingLightColor(self, light):
        if self.now > light.nextActionTime:
            light.up = False
            light.timestamp = self.now
            light.nextActionTime = light.timestamp + light.duration
        else:
            amount_left = 1.0 - (math.cos((math.pi / 2) - ((math.pi / 2) * ((float(light.nextActionTime) - float(self.now)) / float(light.duration)))))
            # amount_left = math.cos((math.pi / 2)  - ((math.pi / 2) * ((float(light.nextActionTime) - float(self.now)) / float(light.duration))))
            # print "amount left {} {} {} {} ".format(amount_left, light.nextActionTime, self.now, light.duration)
            light.currentValue[RED] = int(round(float(light.intendedColor[RED]) * amount_left / 2))
            light.currentValue[GREEN] = int(round(float(light.intendedColor[GREEN]) * amount_left / 2))
            light.currentValue[BLUE] = int(round(float(light.intendedColor[BLUE]) * amount_left / 2))
            # print "incremented to {} {} {}".format(light.currentValue[0], light.currentValue[1], light.currentValue[2])

    # ------------------------------ END Cave Panels ------------------------------------------

    # ------------------------------ Cave Black lights ----------------------------------------

    blackLightValue = 0
    blackLightUp = True
    blackLightDuration = 2000
    blackLightTimestamp = 0
    blackLightRunning = False

    def processCaveBlackLights(self):
        if self.leverValues[CAVE_LEVER]:
            self.dmx.setDimmer(self.dmxStaticBlackLight, 0)
        else:
            self.dmx.setDimmer(self.dmxStaticBlackLight, 255)

        if self.leverValues[PUPPET_LEVER]:
            self.dmx.setBlackLight(self.dmxBlackLights[0], 0)
            self.dmx.setBlackLight(self.dmxBlackLights[1], 0)

        else:
            if not self.blackLightRunning:
                self.blackLightRunning = True
                self.blackLightUp = True
                self.blackLightTimestamp = self.now
                self.blackLightDuration = random.randrange(500, 2000)
            finish_time = self.blackLightTimestamp + self.blackLightDuration
            if self.blackLightUp:
                if self.now > finish_time:
                    self.blackLightUp = False
                    self.blackLightTimestamp = self.now

                amount_left = 1.0 - ((float(finish_time) - float(self.now)) / float(self.blackLightDuration))
                self.blackLightValue = int(round(amount_left * 200.0)) + 55
                self.dmx.setBlackLight(self.dmxBlackLights[0], self.blackLightValue)
                self.dmx.setBlackLight(self.dmxBlackLights[1], self.blackLightValue)
            else:
                if self.now > finish_time:
                    self.blackLightRunning = False
                amount_left = ((float(finish_time) - float(self.now)) / float(self.blackLightDuration))
                self.blackLightValue = int(round(amount_left * 200.0)) + 55
                self.dmx.setBlackLight(self.dmxBlackLights[0], self.blackLightValue)
                self.dmx.setBlackLight(self.dmxBlackLights[1], self.blackLightValue)

    # ------------------------------ END Cave Black Light -------------------------------------

    # ------------------------------ Puppet Eyes ----------------------------------------

    # Eyes
    # 0 - Eye Middle
    # 1 - Eye Left Top
    # 2 - Eye Left Mid
    # 3 - Eye Left Bottom
    # 4 - Eye Right Top
    # 5 - Eye Right Mid
    # 6 - Eye Right Bottom
    eye_operation = [0, 0, 0, 0, 0, 0, 0]
    eye_delay = [0, 0, 0, 0, 0, 0, 0]
    eye_timestamp = [0, 0, 0, 0, 0, 0, 0]
    eye_duration = [2000, 2000, 2000, 2000, 2000, 2000, 2000]
    eye_color = [[100, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0]]

    def processEyes(self):
        if self.leverValues[PUPPET_LEVER]:
            for addr in self.dmxPuppetEyes:
                self.dmx.setLight(addr, [0,0,0])
        else:
            allOn = True
            allOff = True

            # print "eye delays = {}".format(self.eye_delay)

            for i in range(7):
                if self.eye_operation[i] != ON:
                    allOn = False
                if self.eye_operation[i] != OFF:
                    allOff = False
                self.updateEye(i)

            if allOn:
                for i in range(7):
                    self.eye_operation[i] = CLOSING_EYE
                    if i < 4:
                        self.eye_duration[i] = 100 + random.randrange(0, 1000)
                        self.eye_delay[i] = 40 + random.randrange(0, 15)
                    else:
                        firstEye = i - 3
                        self.eye_duration[i] = self.eye_duration[firstEye]
                        self.eye_delay[i] = self.eye_delay[firstEye]

            if allOff:
                for i in range(7):
                    self.eye_operation[i] = OPENING_EYE
                    if i < 4:
                        self.eye_delay[i] = 2 + random.randrange(0, 4)
                        self.eye_duration[i] = random.randrange(0, 1000)
                    else:
                        firstEye = i - 3
                        self.eye_delay[i] = self.eye_delay[firstEye]
                        self.eye_duration[i] = self.eye_duration[firstEye]

                    # pick the new eye color from the increment
                    color_choice = random.randrange(0, 3)
                    red = random.randrange(0, 200 if color_choice == RED else 100)
                    green = random.randrange(0, 200 if color_choice == GREEN else 100)
                    blue = random.randrange(0, 200 if color_choice == BLUE else 100)

                    red = int(float(red) * (40.0/255.0))
                    green = int(float(green) * (40.0/255.0))
                    blue = int(float(blue) * (40.0/255.0))
                    self.eye_color[i][RED] = red
                    self.eye_color[i][GREEN] = green
                    self.eye_color[i][BLUE] = blue
                    self.eye_timestamp[i] = self.now

    def updateEye(self, addr):
        if self.eye_delay[addr] > 0:
            self.eye_delay[addr] += -1
            if self.eye_delay[addr] == 0:
                self.eye_timestamp[addr] = self.now
        elif self.eye_operation[addr] == CLOSING_EYE:
            red = self.getNewDecrementingEyeColor(addr, RED)
            green = self.getNewDecrementingEyeColor(addr, GREEN)
            blue = self.getNewDecrementingEyeColor(addr, BLUE)

            self.dmx.setLight(self.dmxPuppetEyes[addr], [red, green, blue])

            finished = red == 0 and green == 0 and blue == 0
            if finished:
                # switch to opening
                self.eye_operation[addr] = OFF
        elif self.eye_operation[addr] == OPENING_EYE:
            red = self.getNewIncrementingEyeColor(addr, RED)
            green = self.getNewIncrementingEyeColor(addr, GREEN)
            blue = self.getNewIncrementingEyeColor(addr, BLUE)

            self.dmx.setLight(self.dmxPuppetEyes[addr], [red, green, blue])
            finished = red >= self.eye_color[addr][RED] and green >= self.eye_color[addr][GREEN] and blue >= self.eye_color[addr][BLUE]
            if finished:
                self.eye_operation[addr] = ON

    def getNewDecrementingEyeColor(self, addr, color):
        finish_time = self.eye_timestamp[addr] + self.eye_duration[addr]
        if self.now > finish_time:
            return 0
        else:
            amount_left = ((float(finish_time) - float(self.now)) / float(self.eye_duration[addr]))
            return int(round(self.eye_color[addr][color] * amount_left))

    def getNewIncrementingEyeColor(self, addr, color):
        finish_time = self.eye_timestamp[addr] + self.eye_duration[addr]
        if self.now > finish_time:
            return self.eye_color[addr][color]
        else:
            amount_left = 1.0 - ((float(finish_time) - float(self.now)) / float(self.eye_duration[addr]))
            return int(round(float(self.eye_color[addr][color]) * amount_left))

    # ------------------------------ END Puppet Eyes ----------------------------------------

    # def colorWipe(strip, color, wait_ms=50):
    #     """Wipe color across display a pixel at a time."""
    #     for i in range(strip.numPixels()):
    #         strip.setPixelColor(i, color)
    #         strip.show()
    #         time.sleep(wait_ms/1000.0)
    #
    # def wheel(pos):
    #     """Generate rainbow colors across 0-255 positions."""
    #     if pos < 85:
    #         return Color(pos * 3, 255 - pos * 3, 0)
    #     elif pos < 170:
    #         pos -= 85
    #         return Color(255 - pos * 3, 0, pos * 3)
    #     else:
    #         pos -= 170
    #         return Color(0, pos * 3, 255 - pos * 3)
    #
    # def rainbow(strip, wait_ms=20, iterations=1):
    #     """Draw rainbow that fades across all pixels at once."""
    #     for j in range(256*iterations):
    #         for i in range(strip.numPixels()):
    #             strip.setPixelColor(i, wheel((i+j) & 255))
    #         strip.show()
    #         time.sleep(wait_ms/1000.0)
    #
    # def rainbowCycle(strip, wait_ms=100, iterations=5):
    #     """Draw rainbow that uniformly distributes itself across all pixels."""
    #     for j in range(256*iterations):
    #         for i in range(strip.numPixels()):
    #             strip.setPixelColor(i, wheel((int(i * 256 / strip.numPixels()) + j) & 255))
    #         strip.show()
    #         time.sleep(wait_ms/1000.0)
    #


control = LightingControlSystem()
control.start()

while True:
    continue
