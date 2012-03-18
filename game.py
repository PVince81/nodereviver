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
from WorldLoader import WorldLoader, WorldSaver

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
        self._display = view.Display(self._config, self._screen, self._gameState)
        sound.soundManager.init(self._config)
        
    def _quit(self):
        sound.soundManager.release()
        pygame.quit()

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
    
    def _initWorld(self, worldNum):
        self._world = self._worldLoader.loadWorld(worldNum)
        self._world.centerInView(self._config.screenSize)
        self._player = model.Player()
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
        self._worldSaver = WorldSaver(self._config.dataPath)
        
    def _init(self):
        Game._init(self)
        pygame.display.set_caption('MiniLD33 (editor)')

    def _saveWorld(self):
        print "Saving world"
        self._worldSaver.saveWorld(self._gameState.worldNum, self._world)

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
                    self._selectedEdge = None
                    # select another
                    if mods & pygame.locals.KMOD_CTRL:                        
                        self._selectedNodes.append(node)
                    # connect
                    elif mods & (pygame.locals.KMOD_SHIFT | pygame.locals.KMOD_RSHIFT | pygame.locals.KMOD_LSHIFT) and len(self._selectedNodes) > 0:
                        for selectedNode in self._selectedNodes:
                            self._world.connectNodeWithJoint(selectedNode, node)
                        self._selectedNodes = [node]
                    else:
                        self._selectedNodes = [node]
                else:
                    self._selectedNodes = []
                    self._selectedEdge = None
                    edge = self._world.getEdgeAt(event.pos, 10)
                    if edge:
                        self._selectedEdge = edge
                self._display.selectionView.setSelection(self._selectedNodes)
                self._display.selectionView.setEdgeSelection(self._selectedEdge)

        elif event.type == pygame.locals.KEYDOWN:
            if event.key == pygame.locals.K_DELETE:
                if self._selectedEdge:
                    self._world.deleteEdge(self._selectedEdge)
                    self._selectedEdge = None
                for selectedNode in self._selectedNodes:
                    self._world.deleteNode(selectedNode)
                self._selectedNodes = []
                self._display.selectionView.setSelection(self._selectedNodes)
                self._display.selectionView.setEdgeSelection(self._selectedEdge)
                if self._player.currentNode.deleted:
                    self._player.setCurrentNode(self._world.nodes[0])
                    self._world.startNode = self._world.nodes[0]
            if event.key == pygame.locals.K_r:
                # Reverse edge
                if self._selectedEdge:
                    self._selectedEdge.reverse()
                    self._world.dirty = True
            if event.key == pygame.locals.K_d:
                view.debug = not view.debug
                self._world.dirty = True
            if event.key == pygame.locals.K_c:
                self._world.centerInView(self._config.screenSize)
            if event.key == pygame.locals.K_s:
                self._world.alignNodes()
            if event.key == pygame.locals.K_t:
                # Toggle type
                if self._selectedEdge:
                    self._selectedEdge.oneWay = not self._selectedEdge.oneWay
                for node in self._selectedNodes:
                    if node.type == model.Node.JOINT:
                        node.type = model.Node.SQUARE
                    else:
                        node.type = model.Node.JOINT
                self._world.dirty = True
            if event.key == pygame.locals.K_p:
                if len(self._selectedNodes) > 0:
                    self._player.setCurrentNode(self._selectedNodes[0])
                    self._world.startNode = self._selectedNodes[0]                    
            elif event.key == pygame.locals.K_F2:
                self._saveWorld()
                
        
    def _handleLogic(self):
        pass

if __name__ == '__main__':
    game = Game(Config())
    #game = Editor(Config())
    game.run()