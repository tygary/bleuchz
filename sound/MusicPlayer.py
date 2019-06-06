import pygame
import multiprocessing


class MusicPlayer:
    current_song = ''
    music_thread = None

    def __init__(self):
        pygame.mixer.init()

    def play_song(self, song, volume, pos=0.0, loops = 0):
        if song != self.current_song or not self.is_still_playing():
            self.stop_music()
            self.current_song = song
            #self.music_thread = multiprocessing.Process(target=self.__music_loop)
            pygame.mixer.music.load(self.current_song)
            pygame.mixer.music.set_volume(volume)
            #pygame.mixer.music.set_pos(pos)
            pygame.mixer.music.play()
            #self.music_thread.start()

    def is_still_playing(self):
        try:
            return pygame.mixer.music.get_busy() == True
        except:
            return False

    def stop_music(self):
        #if self.music_thread is not None:
        #    self.music_thread.terminate()
        pygame.mixer.music.stop()

    def get_pos(self):
        return pygame.mixer.music.get_pos()

    def set_volume(self, amount):
        pygame.mixer.music.set_volume(amount)

    def __music_loop(self):

        pygame.mixer.stop()
        pygame.mixer.music.load(self.current_song)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            continue
