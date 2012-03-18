#!/usr/bin/python
'''
@author: Vincent Petry <PVince81@yahoo.fr>
'''

import pygame
import model
import view
import sound
from util import *
from config import Config
from WorldLoader import WorldLoader

class Game:
    titleDemo = [3,0,0,3,0,1,2,1,1,3,0,2,0,3,1,2,1,3,0,2,0,3,1,2,1,3,0,2,0,0,3,2,1,3,2,1,3,3,2,1,3,1,2,2,2,2,2,2,2,1,2,1,1,0,3,1,2,3,0,2,0,3,1,2,1,1,3,2,0,3,2,0,3,3,2,0,3,1,1,3,3,3,0,0,1,2,2,0,0,0,3,1,1,2,3,3,2,0,2,3,3,2,0,3,1,1,3,3,0,0,1,2,2,0,0,0,3,1,3,2,2,1,3,2,1,3,2,0,0,3,0,3,1,2,1,1,0,0,3,3,1,2,2,3,1,1,2]
    
    def __init__(self, config):
        self._config = config
        self._screen = None
        self._clock = None
        self._terminated = False
        self._display = None
        self._world = None
        self._gameState = model.GameState()
        self._player = None
        self._worldLoader = WorldLoader(self._config.dataPath)

    def _init(self):
        pygame.init()
        self._initDisplay()
        pygame.display.set_caption('Node Reviver - by Vincent Petry (MiniLD#33)') 
        self._screen = pygame.display.get_surface()
        self._clock = pygame.time.Clock()
        self._display = view.Display(self._config, self._screen, self._gameState)
        sound.soundManager.init(self._config)

    def _quit(self):
        sound.soundManager.release()
        pygame.quit()
        
    def _initDisplay(self):
        flags = 0
        if self._config.fullScreen:
            flags = pygame.FULLSCREEN | pygame.HWSURFACE | pygame.DOUBLEBUF

        pygame.display.set_mode(self._config.screenSize, flags)

    def _movePlayer(self, direction):
        if self._player.moving:
            return

        movements = [(0, -1), (0, 1), (-1, 0), (1, 0)]
        movement = movements[direction]
        # Check whether player is allowed to move to this direction
        edge = self._player.currentNode.getEdgeByDirection(movement)
        if edge:
            self._player.moveAlong(edge)

    def _handleInputEvent(self, event):
        if event.type == pygame.locals.QUIT: 
            self._terminated = True
        elif event.type == pygame.locals.KEYDOWN:
            if event.key in self._config.keymap.pause:
                self._gameState.pause = not self._gameState.pause
            elif event.key == pygame.locals.K_RETURN:
                mods = pygame.key.get_mods()
                if mods & pygame.locals.KMOD_ALT:
                    self._config.fullScreen = not self._config.fullScreen
                    self._initDisplay()
                elif self._gameState.title: 
                    self._startGame()
            elif not self._gameState.title and not self._gameState.pause:
                directionKeys = self._config.keymap.directions
                for direction in range(4):
                    if event.key in directionKeys[direction]:
                        self._movePlayer(direction)
                        break

        elif event.type == pygame.locals.KEYUP:
            if event.key == pygame.locals.K_ESCAPE:
                if self._gameState.title:
                    self._terminated = True
                else:
                    self._startTitle()

    def _handleInput(self):
        for event in pygame.event.get():
            self._handleInputEvent(event)

    def _handleDemo(self):
        if self._player.moving:
            return
        
        nextDirection = self._titleDemo[0]
        self._titleDemo = self._titleDemo[1:]
        self._movePlayer(nextDirection)
        
    def _handleLogic(self):
        if self._gameState.title:
            # plays title demo
            self._handleDemo()            
        
        if self._gameState.pause:
            return
        
        self._world.update()
        if self._world.hasAllEdgesMarked():
            self._gameState.worldNum += 1
            self._gameState.dirty = True
            self._initWorld(self._gameState.worldNum)

        # check for player collision
        for entity in self._world.entities:
            if entity == self._player:
                continue            
            dist = vectorDiff(entity.pos, self._player.pos)
            if abs(dist[0]) < 10 and abs(dist[1]) < 10:
                self._player.die()
                sound.soundManager.play(sound.soundManager.DEAD)

        if self._player.dead:
            if self._gameState.lives > 0:
                self._gameState.lives -= 1
                self._gameState.dirty = True
                self._initWorld(self._gameState.worldNum)
            else:
                # TODO: game over screen
                self._terminated = True
    
    def _startGame(self):
        self._gameState.title = False
        self._gameState.worldNum = 1
        self._initWorld(self._gameState.worldNum)

    def _startTitle(self):
        self._gameState.title = True
        self._initWorld(0)

    def _initWorld(self, worldNum):
        self._player = model.Player()
        if self._gameState.title:
            self._player.speed = 4
            self._world = self._worldLoader.loadWorld(0)
            self._titleDemo = list(self.titleDemo)
        else:
            self._world = self._worldLoader.loadWorld(worldNum)
        self._world.centerInView(self._config.screenSize)
        self._player.setCurrentNode(self._world.startNode)
        self._display.setWorld(self._world, self._player)
        self._display.addEntityView( view.PlayerView(self._player) )
        self._world.addEntity(self._player)

        # set tracking foes to track the player
        for entity in self._world.entities:
            if entity.entityType == 1 and entity.foeType == 1:
                entity.track(self._player)

    def run(self):
        self._init()
        self._gameState.title = True
        self._initWorld(self._gameState.worldNum)

        while not self._terminated:
            self._handleInput()
            self._handleLogic()
            self._display.render()
            pygame.display.flip()
            self._clock.tick(self._config.fps)
            
        self._quit()

if __name__ == '__main__':
    game = Game(Config())
    #game = Editor(Config())
    game.run()