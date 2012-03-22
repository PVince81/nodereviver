from game import Game
from WorldLoader import WorldSaver
import pygame
import view
import model
from config import Config
from model import GameState
from algo import PathFinder

class Editor(Game):
    def __init__(self, config):
        Game.__init__(self, config)
        self._selectedNodes = []
        self._selectedEdge = None
        self._worldSaver = WorldSaver(self._config.dataPath)
        
    def _init(self):
        Game._init(self)
        pygame.display.set_caption('Node Reviver Editor - by Vincent Petry')

    def _saveWorld(self):
        print "Saving world"
        self._worldSaver.saveWorld(self._gameState.worldNum, self._world)

    def _movePlayer(self, direction):
        if self._gameState.state == GameState.EDITOR:
            return
        Game._movePlayer(self, direction)

    def _handleInputEvent(self, event):
        Game._handleInputEvent(self, event)
        if self._gameState.state != GameState.EDITOR:
            return
        
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
            if event.key == pygame.locals.K_PAGEUP:
                if self._gameState.worldNum > 1:
                    self._gameState.worldNum -= 1
                    self._gameState.dirty = True
                    self._initWorld(self._gameState.worldNum)
            if event.key == pygame.locals.K_PAGEDOWN:
                if self._gameState.worldNum < Game.levelsCount:
                    self._gameState.worldNum += 1
                    self._gameState.dirty = True
                    self._initWorld(self._gameState.worldNum)
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
            elif event.key == pygame.locals.K_F5:
                # TODO: need to clone the current level instead of reloading!
                self._startGame(self._gameState.worldNum)
            elif event.key == pygame.locals.K_x:
                self._testPathFinder()

    def _testPathFinder(self):
        if len(self._selectedNodes) == 0:
            return
        # Test the pathfinding algo from player to selection
        pathfinder = PathFinder()
        print "Path finder from %i to %i" % (self._player.currentNode.id, self._selectedNodes[0].id )
        path = pathfinder.findShortestPath(self._player.currentNode, self._selectedNodes[0])
        pathfinder.printPath(self._player.currentNode, path)
        self._selectedNodes = pathfinder.getPathNodes(self._player.currentNode, path)
        self._display.selectionView.setSelection(self._selectedNodes)

    def _handleLogic(self):
        if self._gameState.state == GameState.EDITOR:
            pass
        Game._handleLogic(self)

    def onLevelEnd(self):
        self._gameState.setState(GameState.LEVEL_END, self._config.fps, GameState.RESTART_LEVEL);

    def onBack(self):
        if self._gameState.state == GameState.EDITOR:
            self._terminated = True
        else:
            self._gameState.setState(GameState.EDITOR)

    def run(self):
        self._init()
        self._gameState.state = model.GameState.EDITOR
        self._initWorld(self._gameState.worldNum)

        while not self._terminated:
            self._handleInput()
            self._handleLogic()
            self._display.render()
            pygame.display.flip()
            self._clock.tick(self._config.fps)
            
        self._quit()

if __name__ == '__main__':
    game = Editor(Config())
    game.run()