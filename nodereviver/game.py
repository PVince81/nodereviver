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
import model
import view
import sound
import time
import ui
from util import *
from config import Config
from WorldLoaderJson import WorldLoader
from model import GameState

class Game:
    titleDemo = [3,0,0,3,0,1,2,1,1,3,0,2,0,3,1,2,1,3,0,2,0,3,1,2,1,3,0,2,0,0,3,2,1,3,2,1,3,3,2,1,3,1,2,2,2,2,2,2,2,1,2,1,1,0,3,1,2,3,0,2,0,3,1,2,1,1,3,2,0,3,2,0,3,3,2,0,3,1,1,3,3,3,0,0,1,2,2,0,0,0,3,1,1,2,3,3,2,0,2,3,3,2,0,3,1,1,3,3,0,0,1,2,2,0,0,0,3,1,3,2,2,1,3,2,1,3,2,0,0,3,0,3,1,2,1,1,0,0,3,3,1,2,2,3,1,1,2]

    def __init__(self, config):
        self._config = config
        if self._config.dataPath[-1] != '/':
            self._config.dataPath += '/'
        if self._config.startLevel > 1:
            self._config.cheat = True
        self._screen = None
        self._clock = None
        self._terminated = False
        self._display = None
        self._world = None
        self._gameState = model.GameState()
        self._player = None
        self._worldLoader = WorldLoader(self._config.dataPath)

    def _init(self):
        sound.soundManager.init(self._config)
        pygame.init()
        self._initDisplay()
        pygame.display.set_caption('Node Reviver - by Vincent Petry (MiniLD#33)')
        pygame.mouse.set_visible(False)
        self._screen = pygame.display.get_surface()
        self._clock = pygame.time.Clock()
        self._display = view.Display(self._config, self._screen, self._gameState)

        if self._config.controls:
            self._gameUI = ui.GameUI(self._config)
        else:
            self._gameUI = None

        sound.soundManager.loadSounds()

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
        action = None

        if event.type == pygame.locals.QUIT:
            self._quitGame()
            return
        elif event.type == pygame.ACTIVEEVENT:
            if event.state == 2:
                self._gameState.focus = event.gain
        elif event.type == pygame.locals.KEYDOWN:
            if event.key in self._config.keymap.pause:
                action = "togglepause"
            elif event.key in self._config.keymap.start:
                mods = pygame.key.get_mods()
                if mods & pygame.locals.KMOD_ALT:
                    action = "togglefullscreen"
                else:
                    action = "start"
            elif self._gameState.state == GameState.GAME and not self._gameState.pause:
                directionKeys = self._config.keymap.directions
                for direction in range(4):
                    if event.key in directionKeys[direction]:
                        self._movePlayer(direction)
                        break
        elif event.type == pygame.locals.KEYUP:
            if event.key in self._config.keymap.quit:
                action = "back"
        elif event.type == pygame.locals.MOUSEBUTTONDOWN and event.button == 1:
            if self._gameUI:
                widget = self._gameUI.getWidgetAt(event.pos)
                if widget:
                    action = widget.action
                else:
                    action = "start"

        # TODO: use hash to function mapping ?
        if not action:
            return
        elif action == "back":
            self.onBack()
            self._gameState.pause = False
        elif action == "start":
            self._gameState.pause = False
            if self._gameState.state == GameState.TITLE:
                self._showStory()
            elif self._gameState.state == GameState.STORY:
                self._startGame()
            elif self._gameState.state == GameState.ENDGAME:
                self._startTitle()
        elif action == "togglepause":
            if self._gameState.state == GameState.GAME:
                self._gameState.pause = not self._gameState.pause
        elif action == "togglefullscreen":
            self._config.fullScreen = not self._config.fullScreen
            self._initDisplay()
        elif action == "taskswitch":
            self._taskSwitch()

        if self._gameState.state == GameState.GAME and not self._gameState.pause:
            if action == "up":
                self._movePlayer(0)
            elif action == "down":
                self._movePlayer(1)
            elif action == "left":
                self._movePlayer(2)
            elif action == "right":
                self._movePlayer(3)

    def onBack(self):
        if self._gameState.state == GameState.TITLE:
            self._quitGame()
        else:
            self._startTitle()

    def _taskSwitch(self):
        # TODO: trigger task switching, if supported
        pass

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
        state = self._gameState
        state.update()
        if state.state == GameState.NEXT_LEVEL or state.state == GameState.RESTART_LEVEL:
            if state.state == GameState.NEXT_LEVEL:
                state.worldNum += 1
                if state.worldNum > self._config.levelsCount:
                    state.setState(GameState.ENDGAME)
                    return;
            state.dirty = True
            self._initWorld(state.worldNum)
            state.setState(GameState.LEVEL_START, 1000)

        if state.state == GameState.TITLE:
            # plays title demo
            self._handleDemo()

        if state.pause:
            return

        self._gameState.elapsed += 60

        if state.state in [GameState.GAME, GameState.TITLE, GameState.LEVEL_END, GameState.LEVEL_START]:
            self._world.update()

        if state.state in [GameState.GAME, GameState.TITLE] and self._world.hasAllEdgesMarked():
            self.onLevelEnd()

        if state.state == GameState.GAME:
            # check for player collision
            for entity in self._world.entities:
                if entity == self._player:
                    continue
                dist = vectorDiff(entity.pos, self._player.pos)
                if abs(dist[0]) < 10 and abs(dist[1]) < 10:
                    self._player.die()
                    state.setState(GameState.DEAD, 1000, GameState.RESTART_LEVEL)
                    sound.soundManager.play(sound.soundManager.DEAD)

    def onLevelEnd(self):
        if self._gameState.state == GameState.TITLE:
            self._startTitle()
            return
        self._gameState.setState(GameState.LEVEL_END, 1000, GameState.NEXT_LEVEL)

    def _showStory(self):
        self._gameState.setState(GameState.STORY)

    def _startGame(self, worldNum = None):
        if worldNum == None:
            worldNum = self._config.startLevel
        self._gameState.setState(GameState.LEVEL_START, 1000)
        self._gameState.worldNum = worldNum
        self._initWorld(self._gameState.worldNum)
        sound.soundManager.enable()

    def _startTitle(self):
        self._gameState.state = GameState.TITLE
        self._initWorld(0)

    def _quitGame(self):
        self._terminated = True
        self._gameState.state = GameState.QUIT

    def _initWorld(self, worldNum):
        self._player = model.Player()
        if self._gameState.state == GameState.TITLE:
            self._player.speed = 4
            self._world = self._worldLoader.loadWorld(0)
            self._titleDemo = list(self.titleDemo)
            sound.soundManager.enable(False)
        else:
            self._world = self._worldLoader.loadWorld(worldNum)
        self._world.centerInView(self._display.context.boardSize)
        self._player.setCurrentNode(self._world.startNode)
        if self._gameUI:
            if self._gameState.state in [GameState.LEVEL_START, GameState.NEXT_LEVEL, GameState.RESTART_LEVEL]:
                self._gameUI.setControlsVisibility(True)
            else:
                self._gameUI.setControlsVisibility(False)
            self._display.setUI(self._gameUI)
        self._display.setWorld(self._world, self._player)
        self._world.addEntity(self._player)

        # set tracking foes to track the player
        for entity in self._world.entities:
            if entity.entityType == 1 and entity.foeType == 1:
                entity.track(self._player)

    def run(self):
        self._init()
        self._gameState.state = GameState.TITLE
        self._initWorld(self._gameState.worldNum)

        lastTime = pygame.time.get_ticks()
        deltaTime = 0
        # desired fps is 60
        fpsMax = 1000 / 60
        while not self._terminated:
            self._handleInput()
            if self._gameState.focus:
                # frameskip
                newTime = pygame.time.get_ticks()
                deltaTime = deltaTime + pygame.time.get_ticks() - lastTime
                updateSteps = deltaTime / fpsMax
                for x in range(updateSteps):
                    self._handleLogic()

                deltaTime = deltaTime % fpsMax
                lastTime = newTime

                if not self._gameState.pause:
                    for x in range(updateSteps):
                        self._display.update()
                    self._display.render()
                    pygame.display.flip()

            self._clock.tick(self._config.fps)

        self._quit()

if __name__ == '__main__':
    game = Game(Config())
    game.run()
