'''
@author: Vincent Petry <PVince81@yahoo.fr>
'''

import pygame.locals

class KeyMap:
    def __init__(self):
        self.up = [pygame.locals.K_UP, pygame.locals.K_w]
        self.down = [pygame.locals.K_DOWN, pygame.locals.K_x]
        self.left = [pygame.locals.K_LEFT, pygame.locals.K_a]
        self.right = [pygame.locals.K_RIGHT, pygame.locals.K_d]
        self.directions = [self.up, self.down, self.left, self.right]

class Config:
    def __init__(self):
        self.fullScreen = False
        self.screenSize = (800, 600)
        self.fps = 60
        self.keymap = KeyMap()