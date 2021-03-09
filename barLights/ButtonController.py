import RPi.GPIO as GPIO

class ButtonController(object):
    POWER_BUTTON_PIN = 22
    MODE_BUTTON_PIN = 32

    pins = [POWER_BUTTON_PIN, MODE_BUTTON_PIN]
    currentValues = [1, 1]
    callback = None

    def __init__(self, callback):
        for pin in self.pins:
            self.setup_pin(pin)
        self.callback = callback

    def setup_pin(self, pin):
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.remove_event_detect(pin)

    def on_power_toggle(self, callback):
        self.add_event_detection(self.POWER_BUTTON_PIN, callback, True)

    def on_mode_change(self, callback):
        self.add_event_detection(self.MODE_BUTTON_PIN, callback, True)

    def add_event_detection(pin, callback, bothdirections=False):
        try:
            GPIO.add_event_detect(pin, GPIO.FALLING, callback=callback)
            if bothdirections:
                GPIO.add_event_detect(pin, GPIO.RISING, callback=callback)
        except RuntimeError:
            try:
                GPIO.remove_event_detect(pin)
                GPIO.add_event_detect(pin, GPIO.FALLING, callback=callback)
                if bothdirections:
                    GPIO.add_event_detect(pin, GPIO.RISING, callback=callback)
            except RuntimeError:
                pass

    def check_for_new_switch_values(self):
        changed = False
        newValues = [1, 1]
        for i in range(2):
            newValues[i] = GPIO.input(self.pins[i])
            if newValues[i] != self.currentValues[i]:
                changed = True
                self.currentValues[i] = newValues[i]

        if changed:
            self.callback(self.currentValues)