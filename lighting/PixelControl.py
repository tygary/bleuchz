import time
from rpi_ws281x import *

class PixelControl(object):
    # LED strip configuration:
    LED_COUNT      = 300     # Number of LED pixels.
    LED_PIN        = 18      # GPIO pin connected to the pixels (18 uses PWM!).
    #LED_PIN        = 10      # GPIO pin connected to the pixels (10 uses SPI /dev/spidev0.0).
    LED_FREQ_HZ    = 800000  # LED signal frequency in hertz (usually 800khz)
    LED_DMA        = 10      # DMA channel to use for generating signal (try 10)
    LED_BRIGHTNESS = 255     # Set to 0 for darkest and 255 for brightest
    LED_INVERT     = False   # True to invert the signal (when using NPN transistor level shift)
    LED_CHANNEL    = 0       # set to '1' for GPIOs 13, 19, 41, 45 or 53
    strip = None

    def __init__(self, ledCount):
        self.LED_COUNT = ledCount
        self.strip = Adafruit_NeoPixel(self.LED_COUNT, self.LED_PIN, self.LED_FREQ_HZ, self.LED_DMA, self.LED_INVERT, self.LED_BRIGHTNESS, self.LED_CHANNEL)
        self.strip.begin()

    def setColor(self, channel, color):
        self.strip.setPixelColor(channel, Color(color[0], color[1], color[2]))
        #self.strip.show()

    def blackout(self):
        for i in range(self.strip.numPixels()):
            self.strip.setPixelColor(i, [0,0,0])
        self.strip.show()

    def render(self):
        self.strip.show()

# try:
#     num = 1
#     #while True:
#     colorWipe(strip, Color(0,0,0))
#     rainbowCycle(strip)
#     #strip.setPixelColor(0, Color(255,50,50))
#     #strip.show()
#     #num += 1
# except KeyboardInterrupt:
#     colorWipe(strip, Color(0,0,0), 10)
