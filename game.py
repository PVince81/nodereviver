#!/usr/bin/python
'''

@author: Vincent Petry <PVince81@yahoo.fr>
'''


import pygame
import model
import view
from config import Config
from WorldLoader import WorldLoader

class Game:
    def __init__(self, config):
        self._config = config
        self._screen = None
        self._clock = None
        self._terminated = False
        self._display = None
        self._world = None
        self._worldNum = 1
        self._player = None
        self._worldLoader = WorldLoader(self._config.dataPath) 

    def _init(self):
        pygame.init()
        flags = 0
        if self._config.fullScreen:
            flags = pygame.FULLSCREEN | pygame.HWSURFACE | pygame.DOUBLEBUF

        pygame.display.set_mode(self._config.screenSize, flags)
        pygame.display.set_caption('MiniLD33') 
        self._screen = pygame.display.get_surface()        
        self._clock = pygame.time.Clock()
        self._display = view.Display(self._screen)
        
    def _quit(self):
        pygame.quit()

    def _movePlayer(self, direction):
        if self._player.moving:
            return

        movements = [(0, -1), (0, 1), (-1, 0), (1, 0)]
        movement = movements[direction]
        # Check whether player is allowed to move to this direction
        edge = self._player.currentNode.getEdge(movement)
        if edge:
            self._player.moveAlong(edge)

    def _handleInput(self):
        for event in pygame.event.get():
            if event.type == pygame.locals.QUIT: 
                self._terminated = True
            elif event.type == pygame.locals.KEYDOWN:
                directionKeys = self._config.keymap.directions
                for direction in range(4):
                    if event.key in directionKeys[direction]:
                        self._movePlayer(direction)
                        break

            elif event.type == pygame.locals.KEYUP:
                if event.key == pygame.locals.K_ESCAPE:
                    self._terminated = True

    def _handleLogic(self):
        self._world.update()
        if self._world.hasAllEdgesMarked():
            self._worldNum += 1
            self._initWorld(self._worldNum)
    
    def _initWorld(self, worldNum):
        self._world = self._worldLoader.loadWorld(worldNum)
        self._player = model.Player()
        self._player.setCurrentNode(self._world.startNode)
        self._display.setWorld(self._world)
        self._display.addEntityView( view.PlayerView(self._player) )
        self._world.addEntity(self._player)

        # set tracking foes to track the player
        for entity in self._world.entities:
            if entity.entityType == 1 and entity.foeType == 1:
                entity.track(self._player)
        
    def run(self):
        self._init()
        self._initWorld(self._worldNum)

        while not self._terminated:
            self._handleInput()
            self._handleLogic()
            self._display.render()
            pygame.display.flip()
            self._clock.tick(self._config.fps)
            
        self._quit()
        
if __name__ == '__main__':
    game = Game(Config())
    game.run()