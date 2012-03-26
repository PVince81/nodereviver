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
import pygame.locals

class KeyMap:
    def __init__(self):
        self.up = [pygame.locals.K_UP, pygame.locals.K_w, pygame.locals.K_KP8]
        self.down = [pygame.locals.K_DOWN, pygame.locals.K_x, pygame.locals.K_KP2]
        self.left = [pygame.locals.K_LEFT, pygame.locals.K_a, pygame.locals.K_KP4]
        self.right = [pygame.locals.K_RIGHT, pygame.locals.K_d, pygame.locals.K_KP6]
        self.pause = [pygame.locals.K_PAUSE, pygame.locals.K_p]
        self.directions = [self.up, self.down, self.left, self.right]
        self.start = [pygame.locals.K_RETURN, pygame.locals.K_KP_ENTER]

class Config:
    def __init__(self):
        self.fullScreen = False
        self.screenSize = (640, 480)
        self.fps = 60
        self.keymap = KeyMap()
        self.dataPath = "data/"
        self.sound = False
        self.startLevel = 1
        self.levelsCount = 12
        self.cheat = False
