from MusicPlayer import MusicPlayer
from LeverInputController import LeverInputController
import time

class MusicControlSystem(object):
    pins = [31, 33, 35, 37]
    player = MusicPlayer()
    currentValues = [1, 1, 1, 1]
    wasPlaying = False
    leverController = None
    ambient_pos = 0.0

    def __init__(self):
        self.leverController = LeverInputController(self.handle_change)
        self.player.set_volume(0.4)
        self.player.play_song('/home/pi/bluechz/sound/LabAmbient.ogg', 0.25)

    def handle_change(self, values):
        try:
            print 'Triggered currentValues={}'.format(values)
            play = False
            for i in range(4):
                if values[i] == 0:
                    play = True

            if not self.wasPlaying:
                self.ambient_pos = self.player.get_pos()

            if play:
                volume = 0.99
                self.wasPlaying = True
                if values[0] == 0:
                        self.player.play_song('/home/pi/bluechz/sound/Success! - Blue Sky.ogg', volume)
                elif values[1] == 0:
                        self.player.play_song('/home/pi/bluechz/sound/Failure 3 - Escape Velocity.ogg', volume)
                elif values[2] == 0:
                        self.player.play_song('/home/pi/bluechz/sound/Failure 1 - Time Warp.ogg', volume)
                elif values[3] == 0:
                        self.player.play_song('/home/pi/bluechz/sound/Intro Spiel.ogg', volume)
            else:
                self.player.stop_music()
                self.player.play_song('/home/pi/bluechz/sound/LabAmbient.ogg', 0.35, loops=10)
                self.wasPlaying = False
        except RuntimeError:
            print 'got an error!'

time.sleep(5)


control = MusicControlSystem()

while True:
    control.leverController.check_for_new_switch_values()
    continue
