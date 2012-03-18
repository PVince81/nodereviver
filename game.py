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
        self._gameState = model.GameState()
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
        self._display = view.Display(self._screen, self._gameState)
        
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

    def _handleInputEvent(self, event):
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

    def _handleInput(self):
        for event in pygame.event.get():
            self._handleInputEvent(event)

    def _handleLogic(self):
        self._world.update()
        if self._world.hasAllEdgesMarked():
            self._gameState.worldNum += 1
            self._gameState.dirty = True
            self._initWorld(self._gameState.worldNum)
        if self._player.dead:
            self._gameState.lives -= 1
            self._gameState.dirty = True
            self._initWorld(self._gameState.worldNum)
    
    def _initWorld(self, worldNum):
        self._world = self._worldLoader.loadWorld(worldNum)
        self._world.centerInView(self._config.screenSize)
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
        self._initWorld(self._gameState.worldNum)

        while not self._terminated:
            self._handleInput()
            self._handleLogic()
            self._display.render()
            pygame.display.flip()
            self._clock.tick(self._config.fps)
            
        self._quit()

class Editor(Game):
    def __init__(self, config):
        Game.__init__(self, config)
        self._selectedNodes = []
        self._selectedEdge = None
        
    def _init(self):
        Game._init(self)
        pygame.display.set_caption('MiniLD33 (editor)')
        
    def _handleInputEvent(self, event):
        Game._handleInputEvent(self, event)
        mods = pygame.key.get_mods()
        if event.type == pygame.locals.MOUSEBUTTONDOWN:
            if event.button == 3:
                # add node
                pos = (event.pos[0] / 20 * 20, event.pos[1] / 20 * 20)
                node = self._world.getNodeAt(event.pos, 15)
                if not node:
                    node = self._world.createNode(pos)
                self._selectedNodes = [node]
                self._display.selectionView.setSelection(self._selectedNodes)
            elif event.button == 1:
                # select or drag node
                node = self._world.getNodeAt(event.pos, 10)
                if node:
                    # select another
                    if mods & pygame.locals.KMOD_CTRL:                        
                        self._selectedNodes.append(node)
                    # connect
                    elif mods & pygame.locals.KMOD_SHIFT & len(self._selectedNodes) > 0:
                        for selectedNode in self._selectedNodes:
                            self._world.connectNodeWithJoint(selectedNode, node)
                        self._selectedNodes = [node]
                    else:
                        self._selectedNodes = [node]
                else:
                    self._selectedNodes = []
                self._display.selectionView.setSelection(self._selectedNodes)
        elif event.type == pygame.locals.KEYDOWN:
            if event.key == pygame.locals.K_DELETE:
                for selectedNode in self._selectedNodes:
                    self._world.deleteNode(selectedNode)
                self._selectedNodes = []
                self._display.selectionView.setSelection(self._selectedNodes)
        
    def _handleLogic(self):
        pass

if __name__ == '__main__':
    game = Game(Config())
    #game = Editor(Config())
    game.run()