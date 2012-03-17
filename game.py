#!/usr/bin/python
'''

@author: Vincent Petry <PVince81@yahoo.fr>
'''


import pygame
import random
import math
from pygame.locals import *
from pygame import Surface
import model
import view

class Config:
    def __init__(self):
        self.fullScreen = False
        self.screenSize = (800, 600)
        self.fps = 60
        

class Game:
    def __init__(self, config):
        self._config = config
        
    def _init(self):
        pygame.init();
        flags = 0
        if self._config.fullScreen:
            flags = pygame.FULLSCREEN | pygame.HWSURFACE | pygame.DOUBLEBUF

        pygame.display.set_mode(self._config.screenSize, flags)
        pygame.display.set_caption('MiniLD33') 
        self._screen = pygame.display.get_surface()
        self._terminated = False
        self._clock = pygame.time.Clock()
        self._display = view.Display(self._screen);
        
    def _quit(self):
        pygame.quit();
        
    def _handleInput(self):
        for event in pygame.event.get():
            if event.type == QUIT: 
                self._terminated = True
            elif event.type == KEYUP:
                if event.key == K_ESCAPE:
                    self._terminated = True

    def _handleLogic(self):
        pass
    
    def _initWorld(self, worldNum):
        self._world = model.World.getWorld(worldNum)
        self._display.setWorld(self._world)
        
    def run(self):
        self._init()
        self._initWorld(0)
        while not self._terminated:
            self._handleInput();
            self._handleLogic();
            self._display.render()
            pygame.display.flip()
            self._clock.tick(self._config.fps)
            
        self._quit()
        

if __name__ == '__main__':
    config = Config()
    game = Game(config)
    game.run()