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
from .game import Game
from .WorldLoaderJson import WorldSaver
import pygame
from . import view
from . import model
from .config import Config
from .model import GameState
from .algo import PathFinder
import copy

class Editor(Game):
    GRID_SIZE = 20

    def __init__(self, config):
        Game.__init__(self, config)
        self._selectedNodes = []
        self._selectedEdge = None
        self._selectedEntity = None
        self._config.cheat = True
        self._worldSaver = WorldSaver(self._config.dataPath)
        self._playtestActive = False
        self._playtestWorld = None
        self._editorWorld = None
        self._editorPlayer = None

    def _init(self):
        Game._init(self)
        # The editor uses keys as shortcuts, not for entering text. With some
        # SDL/Pygame combinations active text input (IME) suppresses KEYDOWN
        # events for letters and the number row while special keys still work.
        if hasattr(pygame.key, "stop_text_input"):
            pygame.key.stop_text_input()
        pygame.display.set_caption('Node Reviver Editor - by Vincent Petry')
        pygame.mouse.set_visible(True)
        self._gameUI = None

    def _saveWorld(self):
        filename = self._worldSaver.saveWorld(
            self._gameState.worldNum, self._world
        )
        print("Saved world to %s" % filename)

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
                self._selectedEntity = None
                pos = self._snapToGrid(event.pos)
                node = self._world.getNodeAt(event.pos, 15)
                if not node:
                    node = self._world.createNode(pos)
                self._selectedNodes = [node]
                self._display.selectionView.setSelection(self._selectedNodes)
                self._display.selectionView.setEntitySelection(None)
            elif event.button == 1:
                # select node
                node = self._world.getNodeAt(event.pos, 10)
                entity = self._getFoeAt(event.pos)
                if entity and not mods & pygame.locals.KMOD_CTRL:
                    self._selectedEntity = entity
                    self._selectedNodes = []
                    self._selectedEdge = None
                elif node:
                    self._selectedEntity = None
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
                    self._selectedEntity = None
                    self._selectedNodes = []
                    self._selectedEdge = None
                    edge = self._world.getEdgeAt(event.pos, 10)
                    if edge:
                        self._selectedEdge = edge
                self._display.selectionView.setSelection(self._selectedNodes)
                self._display.selectionView.setEdgeSelection(self._selectedEdge)
                self._display.selectionView.setEntitySelection(
                    self._selectedEntity
                )

        # Drag and drop is intentionally disabled. Moving a single node freely
        # can turn the editor's horizontal/vertical L-shaped edges diagonal.
        # Re-enable only together with logic that rebuilds the affected joints.

        elif event.type == pygame.locals.KEYDOWN:
            print("KEYDOWN key=%r unicode=%r name=%r scancode=%r" % (
                getattr(event, "key", None),
                getattr(event, "unicode", None),
                pygame.key.name(event.key),
                getattr(event, "scancode", None)
            ))
            if event.key == pygame.locals.K_PAGEUP:
                if self._gameState.worldNum > 1:
                    self._gameState.worldNum -= 1
                    self._gameState.dirty = True
                    self._initWorld(self._gameState.worldNum)
            if event.key == pygame.locals.K_PAGEDOWN:
                if self._gameState.worldNum < self._config.levelsCount:
                    self._gameState.worldNum += 1
                    self._gameState.dirty = True
                    self._initWorld(self._gameState.worldNum)
            if event.key == pygame.locals.K_DELETE:
                if self._selectedEntity:
                    if self._selectedEntity in self._world.entities:
                        self._world.entities.remove(self._selectedEntity)
                        self._world.dirty = True
                    print("Deleted foe")
                    self._selectedEntity = None
                    self._refreshWorldDisplay()
                else:
                    if self._selectedEdge:
                        self._world.deleteEdge(self._selectedEdge)
                        self._selectedEdge = None
                    for selectedNode in self._selectedNodes:
                        self._world.deleteNode(selectedNode)
                    self._selectedNodes = []
                    self._display.selectionView.setSelection(self._selectedNodes)
                    self._display.selectionView.setEdgeSelection(self._selectedEdge)
                    if self._player.currentNode.deleted:
                        if self._world.nodes:
                            startNode = self._world.nodes[0]
                        else:
                            boardSize = self._display.context.boardSize
                            startNode = self._world.createNode(
                                (boardSize[0] // 40 * 20, boardSize[1] // 40 * 20)
                            )
                        self._player.setCurrentNode(startNode)
                        self._world.startNode = startNode
            if self._isLetterKey(event, "f"):
                self._placeFoe(bool(mods & pygame.locals.KMOD_SHIFT))
            if self._isLetterKey(event, "r"):
                self._repairInvalidEdges()
            if self._isLetterKey(event, "d"):
                view.debug = not view.debug
                self._world.dirty = True
            if self._isLetterKey(event, "c"):
                self._world.centerInView(self._config.screenSize)
            if self._isLetterKey(event, "s"):
                self._world.alignNodes()
            if self._isLetterKey(event, "t"):
                print("T pressed; selected nodes: %i; selected edge: %s" % (
                    len(self._selectedNodes),
                    self._selectedEdge.id if self._selectedEdge else "none"
                ))
                self._toggleSelectedType()
            if self._isLetterKey(event, "p"):
                self._setStartNodeFromSelection()
            elif event.key == pygame.locals.K_F2:
                self._saveWorld()
            elif event.key == pygame.locals.K_F5:
                self._startPlaytest()
            elif self._isLetterKey(event, "x"):
                self._testPathFinder()

    def _isLetterKey(self, event, letter):
        """Match letter keys across pygame/Python versions and modifiers."""
        unicodeValue = getattr(event, "unicode", "")
        if unicodeValue and unicodeValue.lower() == letter:
            return True
        if event.key in (ord(letter.lower()), ord(letter.upper())):
            return True
        if pygame.key.name(event.key).lower() == letter:
            return True

        # SDL scancodes identify the physical letter keys independently of
        # keyboard layout and the keycode behavior of the pygame version.
        letterScancodes = {
            "c": 6,
            "d": 7,
            "f": 9,
            "p": 19,
            "r": 21,
            "s": 22,
            "t": 23,
            "x": 27
        }
        return getattr(event, "scancode", None) == letterScancodes[letter]

    def _getFoeAt(self, pos):
        for entity in reversed(self._world.entities):
            if entity.entityType != model.Foe.entityType:
                continue
            if (abs(entity.pos[0] - pos[0]) <= 10 and
                    abs(entity.pos[1] - pos[1]) <= 10):
                return entity
        return None

    def _placeFoe(self, tracking):
        if not self._selectedNodes:
            print("F ignored: no node selected")
            return
        node = self._selectedNodes[0]
        if node.deleted or node.type != model.Node.SQUARE:
            print("F ignored: node %i is not a regular node" % node.id)
            return

        if tracking:
            self._world.createTrackingFoe(node)
            foeType = "tracking"
        else:
            self._world.createSimpleFoe(node)
            foeType = "simple"
        self._refreshWorldDisplay()
        print("Placed %s foe on node %i" % (foeType, node.id))

    def _refreshWorldDisplay(self):
        self._display.setWorld(self._world, self._player)
        self._display.selectionView.setSelection(self._selectedNodes)
        self._display.selectionView.setEdgeSelection(self._selectedEdge)
        self._display.selectionView.setEntitySelection(self._selectedEntity)

    def _snapToGrid(self, pos):
        return tuple(
            coordinate // self.GRID_SIZE * self.GRID_SIZE
            for coordinate in pos
        )

    def _renderNodePlacementPreview(self):
        if self._gameState.state != GameState.EDITOR:
            return

        pos = self._snapToGrid(pygame.mouse.get_pos())
        if any(node.pos == pos for node in self._world.nodes):
            return

        pygame.draw.rect(
            self._screen,
            (96, 96, 96),
            (pos[0] - 5, pos[1] - 5, 10, 10),
            1
        )

    def _repairInvalidEdges(self):
        connectedNodes = self._connectNodesOnOverlappingEdges()
        invalidEdges = []
        connectedPairs = set()

        for edge in list(self._world.edges):
            source = edge.source
            destination = edge.destination
            reason = None

            if (source not in self._world.nodes or
                    destination not in self._world.nodes or
                    source.deleted or destination.deleted):
                reason = "missing or deleted endpoint"
            elif source is destination or source.pos == destination.pos:
                reason = "overlapping endpoints"
            else:
                dx = abs(destination.pos[0] - source.pos[0])
                dy = abs(destination.pos[1] - source.pos[1])
                pair = frozenset((source, destination))
                if dx and dy:
                    reason = "diagonal edge"
                elif dx + dy < self.GRID_SIZE:
                    reason = "shorter than one grid cell"
                elif pair in connectedPairs:
                    reason = "duplicate edge"
                else:
                    connectedPairs.add(pair)
                    edge.length = dx + dy

            if reason:
                invalidEdges.append((edge, reason))

        for edge, reason in invalidEdges:
            print("Repair: removing edge %i (%s)" % (edge.id, reason))
            self._world.deleteEdge(edge)
            if self._selectedEdge is edge:
                self._selectedEdge = None

        if invalidEdges:
            self._display.selectionView.setEdgeSelection(self._selectedEdge)
        print("Repair complete: connected %i node(s), removed %i invalid edge(s)" % (
            connectedNodes, len(invalidEdges)
        ))
        self._repairPlayerStart()

    def _connectNodesOnOverlappingEdges(self):
        connectedNodes = 0

        for edge in list(self._world.edges):
            source = edge.source
            destination = edge.destination
            if (source not in self._world.nodes or
                    destination not in self._world.nodes):
                continue

            horizontal = source.pos[1] == destination.pos[1]
            vertical = source.pos[0] == destination.pos[0]
            if not horizontal and not vertical:
                continue

            nodesOnEdge = []
            for node in self._world.nodes:
                if node is source or node is destination or node.deleted:
                    continue
                if horizontal:
                    onLine = (
                        node.pos[1] == source.pos[1] and
                        min(source.pos[0], destination.pos[0]) < node.pos[0] <
                        max(source.pos[0], destination.pos[0])
                    )
                else:
                    onLine = (
                        node.pos[0] == source.pos[0] and
                        min(source.pos[1], destination.pos[1]) < node.pos[1] <
                        max(source.pos[1], destination.pos[1])
                    )
                if onLine:
                    nodesOnEdge.append(node)

            if not nodesOnEdge:
                continue

            nodesOnEdge.sort(key=lambda node: (
                abs(node.pos[0] - source.pos[0]) +
                abs(node.pos[1] - source.pos[1])
            ))
            pathNodes = [source] + nodesOnEdge + [destination]
            oneWay = edge.oneWay
            print("Repair: splitting edge %i at node(s) %s" % (
                edge.id, ", ".join(str(node.id) for node in nodesOnEdge)
            ))
            self._world.deleteEdge(edge)
            if self._selectedEdge is edge:
                self._selectedEdge = None
            for startNode, endNode in zip(pathNodes, pathNodes[1:]):
                self._world.connectNodeWithJoint(
                    startNode, endNode, False, oneWay
                )
            connectedNodes += len(nodesOnEdge)

        if connectedNodes:
            self._display.selectionView.setEdgeSelection(self._selectedEdge)
        return connectedNodes

    def _repairPlayerStart(self):
        startNode = self._world.startNode
        if (startNode in self._world.nodes and not startNode.deleted and
                startNode.type == model.Node.SQUARE):
            print("Repair: player start node %i is valid" % startNode.id)
            return

        if startNode in self._world.nodes:
            startIndex = self._world.nodes.index(startNode)
        else:
            startIndex = -1

        orderedNodes = (
            self._world.nodes[startIndex + 1:] +
            self._world.nodes[:startIndex + 1]
        )
        nextStartNode = next((
            node for node in orderedNodes
            if not node.deleted and node.type == model.Node.SQUARE
        ), None)

        if nextStartNode is None:
            print("Repair: no valid player start node found")
            return

        self._world.startNode = nextStartNode
        self._player.setCurrentNode(nextStartNode)
        self._world.dirty = True
        print("Repair: player start moved to node %i" % nextStartNode.id)

    def _setStartNodeFromSelection(self):
        if not self._selectedNodes:
            print("P ignored: no node selected")
            return

        node = self._selectedNodes[0]
        if node.deleted or node.type != model.Node.SQUARE:
            print("P ignored: node %i is not a valid regular node" % node.id)
            return

        self._world.startNode = node
        self._player.setCurrentNode(node)
        self._world.dirty = True
        print("Player start set to node %i" % node.id)

    def _toggleSelectedType(self):
        if self._selectedEdge:
            self._selectedEdge.oneWay = not self._selectedEdge.oneWay
            self._world.dirty = True
            print("Edge %i one-way: %s" % (
                self._selectedEdge.id, self._selectedEdge.oneWay
            ))
            return

        if not self._selectedNodes:
            print("T ignored: no node or edge selected")
            return

        for node in self._selectedNodes:
            oldType = node.type
            if node.type == model.Node.JOINT:
                node.type = model.Node.SQUARE
            else:
                node.type = model.Node.JOINT
            typeNames = {
                model.Node.SQUARE: "node",
                model.Node.JOINT: "joint"
            }
            print("Node %i changed: %s -> %s" % (
                node.id, typeNames[oldType], typeNames[node.type]
            ))
        self._world.dirty = True

    def _testPathFinder(self):
        if len(self._selectedNodes) == 0:
            return
        # Test the pathfinding algo from player to selection
        pathfinder = PathFinder()
        print("Path finder from %i to %i" % (self._player.currentNode.id, self._selectedNodes[0].id ))
        path = pathfinder.findShortestPath(self._player.currentNode, self._selectedNodes[0])
        pathfinder.printPath(self._player.currentNode, path)
        self._selectedNodes = pathfinder.getPathNodes(self._player.currentNode, path)
        self._display.selectionView.setSelection(self._selectedNodes)

    def _handleLogic(self):
        Game._handleLogic(self)
        if (self._playtestActive and
                self._gameState.state == GameState.EDITOR):
            self._stopPlaytest()

    def onLevelEnd(self):
        self._gameState.setState(
            GameState.LEVEL_END, 1000, GameState.EDITOR
        )

    def onBack(self):
        if self._gameState.state == GameState.EDITOR:
            self._terminated = True
        elif self._playtestActive:
            self._stopPlaytest()
        else:
            self._gameState.setState(GameState.EDITOR)

    def _startPlaytest(self):
        """Play a temporary copy without changing the editor's world."""
        self._editorWorld = self._world
        self._editorPlayer = self._player
        self._playtestWorld = copy.deepcopy(self._world)
        self._playtestActive = True
        self._startGame(self._gameState.worldNum)

    def _stopPlaytest(self):
        self._playtestActive = False
        self._playtestWorld = None
        self._world = self._editorWorld
        self._player = self._editorPlayer
        self._editorWorld = None
        self._editorPlayer = None
        self._gameState.setState(GameState.EDITOR)
        self._display.setWorld(self._world, self._player)
        self._display.selectionView.setSelection(self._selectedNodes)
        self._display.selectionView.setEdgeSelection(self._selectedEdge)

    def _initWorld(self, worldNum):
        if not self._playtestActive:
            Game._initWorld(self, worldNum)
            return

        # Use a fresh copy for every retry so deaths cannot alter the editor
        # level or reload an older version from disk.
        self._world = copy.deepcopy(self._playtestWorld)
        self._world.entities = [
            entity for entity in self._world.entities
            if entity.entityType != model.Player.entityType
        ]
        self._player = model.Player(self._world.startNode)
        self._world.centerInView(self._display.context.boardSize)
        self._display.setWorld(self._world, self._player)
        self._world.addEntity(self._player)

        for entity in self._world.entities:
            if entity.entityType == 1 and entity.foeType == 1:
                entity.track(self._player)

    def run(self):
        self._init()
        self._gameState.state = model.GameState.EDITOR
        self._initWorld(self._gameState.worldNum)

        while not self._terminated:
            self._handleInput()
            self._handleLogic()
            self._display.render()
            self._renderNodePlacementPreview()
            pygame.display.flip()
            self._clock.tick(self._config.fps)

        self._quit()

if __name__ == '__main__':
    game = Editor(Config())
    game.run()
