'''
@author: Vincent Petry <PVince81@yahoo.fr>
'''
import pygame

class _SoundManager:
    MOVE = 0
    DEAD = 1
    DRAW = 2
    FILES = [
        "move.wav",
        "dead.wav",
        "draw.wav"
    ]
    
    def __init__(self):
        self.sounds = []
        self._initialized = False

    def init(self, config):
        if self._initialized:
            return
        self._initialized = True
        self._config = config
        if self._config.sound:
            pygame.mixer.init(22050, -16, 1, 1024)
            for fileName in self.FILES:
                self.sounds.append(pygame.mixer.Sound(self._config.dataPath + fileName))

    def release(self):
        if self._initialized and self._config.sound:
            pygame.mixer.quit()

    def play(self, soundIndex):
        if not self._initialized or not self._config.sound:
            return
        self.sounds[soundIndex].play()

soundManager = _SoundManager()