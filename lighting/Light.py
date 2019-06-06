
LIGHT_UNSET = -1
LIGHT_FADE = 0
LIGHT_BLINK = 1
LIGHT_NUM_EFFECTS = 2


class Light(object):
    address = 0
    mode = -1
    up = True
    on = False
    wait = False
    currentValue = [0, 0, 0]
    intendedColor = [0, 0, 0]
    previousColor = [0, 0, 0]
    timestamp = 0
    duration = 0
    waitDuration = 0
    nextActionTime = 0
    iterations = 0


    def __init__(self, address):
        self.address = address
