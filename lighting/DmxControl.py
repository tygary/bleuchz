from lib.DmxPy import DmxPy
import time

class DmxControl(object):
    dmx = None

    def __init__(self):
        self.dmx = DmxPy('/dev/ttyUSB0')

    def setLight(self, channelStart, color):
        self.dmx.setChannel(channelStart, color[0])
        self.dmx.setChannel(channelStart + 1, color[1])
        self.dmx.setChannel(channelStart + 2, color[2])
        #print "set light {} to color {}".format(channelStart, color)

    def setParCan(self, channelStart, color):
        self.dmx.setChannel(channelStart, color[0])
        self.dmx.setChannel(channelStart + 1, color[1])
        self.dmx.setChannel(channelStart + 2, color[2])
        self.dmx.setChannel(channelStart + 3, 255)
        self.dmx.setChannel(channelStart + 4, 255)

    def setDimmer(self, channel, brightness):
        self.dmx.setChannel(channel, brightness)

    def render(self):
        self.dmx.render()

    def blackout(self):
        self.dmx.blackout()
        self.dmx.render()

    def setBlackLight(self, channelStart, brightness):
        # Blacklight channels
        # 1  -  0 for dmx control
        # 2  -  0 for full color?
        # 3  -  Speed.  Set to 0?
        # 4  -  Total Brightness 0-255
        # 5  -  Red
        # 6  -  Green
        # 7  -  Blue
        self.dmx.setChannel(channelStart, 0)
        self.dmx.setChannel(channelStart+1, 0)
        self.dmx.setChannel(channelStart+2, 0)
        self.dmx.setChannel(channelStart+3, brightness)
        self.dmx.setChannel(channelStart+4, 255)
        self.dmx.setChannel(channelStart+5, 255)
        self.dmx.setChannel(channelStart+6, 255)
