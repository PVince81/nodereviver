'''
    This file is part of nodereviver

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.

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
        self.enabled = True

    def init(self, config):
        if self._initialized:
            return
        self._initialized = True
        self._config = config
        if self._config.sound:
            pygame.mixer.pre_init(44100, -16, 2, 256)

    def loadSounds(self):
        if self._config.sound:
            #pygame.mixer.init()
            for fileName in self.FILES:
                self.sounds.append(pygame.mixer.Sound(self._config.dataPath + fileName))

    def release(self):
        if self._initialized and self._config.sound:
            pygame.mixer.quit()

    def play(self, soundIndex):
        if not self.enabled or not self._initialized or not self._config.sound:
            return
        self.sounds[soundIndex].play()

    def enable(self, enabled = True):
        self.enabled = enabled


soundManager = _SoundManager()
