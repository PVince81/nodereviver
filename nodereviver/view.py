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
import random
import math
from util import *
from model import GameState

debug = False

_spriteSurface = None
_gameState = None

_storyText = ["Oh noes ! Our super-expensive equipment     ",
"has been hacked !",
"  ",
"All internal nodes have been disconnected",
"and security drones have been reprogrammed against us !",
"         ",
"We hired you for your particular talent",
"with dealing with this kind of situation.",
"         ",
"So your mission is...            ",
"to reconnect all nodes of our appliances...",
"         ",
"I mean valuable equipment",
"            ",
"Which we need to get some work done in here...",
"   ",
"Good luck and beware of the drones !",
"                                               ",
"And if you die we'll replace you...              ",
"I mean... you can try again.  ",
""]

_endGameText = ["Congratulations !!!",
"You have reactivated all of our company's equipment",
"which means we can resume work now...",
"By the way, our bank account has been hacked as well",
"beyond repair... so you'll have to wait",
"for a while until you get your check...",
"    ",
"    ",
"    ",
"Cup of coffee ? How many sugars ?"
"    ",
"    ",
"    ",
"You finished the game in %time%.",
"     ",
"                                           ",
"Thank you for playing Node Reviver (MiniLD #33)",
""]

_cheatEndGameText = ["Well, it seems you haven't fixed everything...",
"Please start again, this time from the very beginning !",
"     ",
"Clever you, using command line arguments !!!",
"     ",
"                       ",
"But I like your attitude !",
"     ",
"Thank you for playing Node Reviver (MiniLD #33)",
""]
_sprites = [
    # 0 Player
    pygame.Rect(0, 0, 20, 20),
    # 1 Foe 1
    pygame.Rect(20, 0, 20, 20),
    # 2 Foe 2
    pygame.Rect(40, 0, 20, 20),
    # 3 Arrow up
    pygame.Rect(60, 12, 12, 6),
    # 4 Arrow down
    pygame.Rect(72, 12, 12, 6),
    # 5 Arrow left
    pygame.Rect(66, 0, 6, 12),
    # 6 Arrow right
    pygame.Rect(60, 0, 6, 12),
    # 7 Arrow up active
    pygame.Rect(84, 12, 12, 6),
    # 8 Arrow down active
    pygame.Rect(96, 12, 12, 6),
    # 9 Arrow left active
    pygame.Rect(90, 0, 6, 12),
    # 10 Arrow right active
    pygame.Rect(84, 0, 6, 12),
    # 11 Node normal
    pygame.Rect(96, 0, 10, 10),
    # 12 Node active
    pygame.Rect(106, 0, 10, 10)
]

SPRITE_PLAYER = 0
SPRITE_FOE1 = 1
SPRITE_FOE2 = 2
SPRITE_ARROW_UP = 3
SPRITE_ARROW_DOWN = 4
SPRITE_ARROW_LEFT = 5
SPRITE_ARROW_RIGHT = 6
SPRITE_ARROW_UP_ACTIVE = 7
SPRITE_ARROW_DOWN_ACTIVE = 8
SPRITE_ARROW_LEFT_ACTIVE = 9
SPRITE_ARROW_RIGHT_ACTIVE = 10
SPRITE_NODE_NORMAL = 11
SPRITE_NODE_ACTIVE = 12

def drawSprite(surface, spriteIndex, pos, alpha = 255):
    _spriteSurface.set_alpha(alpha)
    surface.blit(_spriteSurface, pos, _sprites[spriteIndex] )

def makeTextSurfaces(text, font, color = (255, 255, 255)):
    if not text:
        return []
    surfaces = []
    if type(text) == "list":
        rows = text
    else:
        rows = text.split("\\n")
    for row in rows:
        surfaces.append( font.render(row, False, color) )
    return surfaces

def blitTextSurfaces(targetSurface, surfaces, fontHeight, globalOffset = (0, 0), centerInViewport = None):
    offsetY = globalOffset[1]
    if centerInViewport:
        for surface in surfaces:
            if surface:
                offset = globalOffset[0] + int(centerInViewport[0] / 2 - surface.get_width() / 2)
                targetSurface.blit(surface, (offset, offsetY))
            offsetY += fontHeight
    else:
        for surface in surfaces:
            if surface:
                targetSurface.blit(surface, (globalOffset[0], offsetY))
            offsetY += fontHeight

    return offsetY

def drawLine(surface, color, src, dest, width = 1):
    if src[0] > dest[0] or src[1] > dest[1]:
        aux = src
        src = dest
        dest = aux
    width -= 1
    pos1 = vectorAdd(src, (-width, -width))
    pos2 = vectorAdd(dest, (width, width))
    pygame.draw.rect(surface, color, (pos1[0], pos1[1], pos2[0] - pos1[0], pos2[1] - pos1[1]))

class ViewContext(object):
    def __init__(self, config, screen, gameState):
        self.config = config
        # Size of the game board (world + texts), without UI
        if config.controls:
            # Restrict the board to the left of the screen to allow some
            # space for the UI
            self.boardSize = (640, 480)
        else:
            # No UI, just center
            self.boardSize = (screen.get_width(), screen.get_height())
        self.screen = screen
        self.gameState = gameState
        fontFile = "DejaVuSansMono.ttf"
        self.smallFont = pygame.font.Font(config.dataPath + fontFile, 10)
        self.normalFont = pygame.font.Font(config.dataPath + fontFile, 12)
        self.mediumFont = pygame.font.Font(config.dataPath + fontFile, 15)
        self.bigFont = pygame.font.Font(config.dataPath + fontFile, 18)
        self.biggerFont = pygame.font.Font(config.dataPath + fontFile, 20)

class Display(object):
    def __init__(self, config, screen, gameState):
        self.context = ViewContext(config, screen, gameState)
        if config.cheat:
            global _endGameText
            _endGameText = _cheatEndGameText
        self._background = screen.copy()
        self._background.fill((0, 0, 0))
        self._entities = []
        self._worldView = None
        self._titleScreen = TitleScreen(self.context)
        self._gameState = gameState
        self._hud = Hud(self.context)
        self._uiSurface = None
        self._ui = None
        self._story = Story(self.context, _storyText)
        self._endStory = None
        self.selectionView = SelectionView()
        self._edgeView = EdgeView()

        # UGLY, I know... but I'm tired to pass everything along
        global _spriteSurface
        global _gameState
        _gameState = gameState
        _spriteSurface = pygame.image.load(config.dataPath + "sprites.png")
        #_spriteSurface = _spriteSurface.convert_alpha(screen)
        _spriteSurface = _spriteSurface.convert(screen)
        _spriteSurface.set_colorkey((255, 0, 255), pygame.RLEACCEL)

    def setUI(self, ui):
        if ui:
            self._ui = ui
            self._ui.dirty = True
        else:
            self._uiSurface = None

    def setWorld(self, world, player):
        self.clear()
        world.dirty = True
        self._world = world
        self._player = player
        self._worldView = WorldView(self.context, world)
        for entity in world.entities:
            # entities are all foes for now (except player)
            self.addEntityView(FoeView(entity))
        self._hud.setTitle(world.title, world.subtitle, world.endtext)
        if self._ui:
            self._ui.dirty = True
        if self._uiSurface:
            self._worldView.setBackground(self._uiSurface)

    def renderUI(self):
        # TODO: move to separate class ?
        if not self._ui or not self._ui.dirty:
            return
        self._ui.dirty = False
        surface = self.context.screen.copy()
        surface.fill((0, 0, 0))
        ui = self._ui

        for widget in ui.widgets:
            if not widget.visible:
                continue
            pygame.draw.rect(surface, (80, 80, 80), widget.rect, 1)
            if widget.text:
                textSurface = self.context.normalFont.render(widget.text, False, (80, 80, 80))
                pos = ( widget.rect[0] + widget.rect[2] / 2 - textSurface.get_width() / 2,
                        widget.rect[1] + widget.rect[3] / 2 - textSurface.get_height() / 2 )
                surface.blit(textSurface, pos)
        self._uiSurface = surface
        if self._worldView:
            self._worldView.setBackground(self._uiSurface)

    def render(self):
        surface = self.context.screen
        if _gameState.state == GameState.QUIT:
            surface.blit(self._background, (0,0))
            textSurface = self.context.bigFont.render("Caught signal SIGKILL...", False, (0, 192, 0))
            surface.blit(textSurface, (10, 10))
            return
        elif _gameState.state == GameState.STORY:
            surface.blit(self._background, (0,0))
            self._story.render(surface)
            return
        elif _gameState.state == GameState.ENDGAME:
            surface.blit(self._background, (0,0))
            self._endStory.render(surface)
            return
        self.renderUI()
        self._worldView.render()
        self._hud.render()
        self._edgeView.render(surface)
        for entity in self._entities:
            entity.render(surface)
        if self._gameState.state == GameState.TITLE:
            self._titleScreen.render()
        self.selectionView.render(surface)

    def update(self):
        if _gameState.state == GameState.STORY:
            self._story.update()
            return
        elif _gameState.state == GameState.ENDGAME:
            if self._endStory == None:
                a = []
                timeString = makeTimeString(self._gameState.elapsed)
                for text in _endGameText:
                    a.append(text.replace("%time%", timeString))
                self._endStory = Story(self.context, a)

            self._endStory.update()
            return
        self._edgeView.update(self._player.currentEdge)
        for entity in self._entities:
            entity.update()

    def addEntityView(self, entityView):
        self._entities.append(entityView)

    def clear(self):
        self._entities = []

class WorldView(object):
    '''
    '''

    def __init__(self, context, world):
        self._context = context
        self._world = world
        self._background = self._context.screen.copy()
        self._background.fill((0, 0, 0))
        self._worldSurface = self._context.screen.copy()

    def setBackground(self, background):
        self._background = background
        self._world.dirty = True

    def _rerender(self):
        surface = self._worldSurface
        # render edges
        for edge in self._world.edges:
            width = 3
            if edge.isMarked():
                color = (0, 255, 255)
            else:
                color = (128, 128, 128)

            # HACK: pygame.draw.line doesn't apply the width around the position,
            # so need to shift it manually
            drawLine(surface, color, edge.source.pos, edge.destination.pos, width )
            if edge.oneWay and edge.destination.type != model.Node.JOINT:
                # Draw arrow
                dir = unitVector(vectorDiff(edge.destination.pos, edge.source.pos))
                # I used to calculate this, but time is against me now,
                # so just hard-coding it
                if dir[0] == 0:
                    if dir[1] < 0:
                        spriteIndex = SPRITE_ARROW_UP
                        offset = (-6, 4)
                    else:
                        spriteIndex = SPRITE_ARROW_DOWN
                        offset = (-6, -10)
                else:
                    if dir[0] < 0:
                        spriteIndex = SPRITE_ARROW_LEFT
                        offset = (4, -6)
                    else:
                        spriteIndex = SPRITE_ARROW_RIGHT
                        offset = (-10, -6)
                if edge.isMarked():
                    spriteIndex += 4
                pos = vectorAdd(edge.destination.pos, offset)
                drawSprite(surface, spriteIndex, pos)

            if debug:
                textSurface = self._context.normalFont.render("%i" % edge.length, False, (0, 128, 128))
                x1 = edge.source.pos[0]
                x2 = edge.destination.pos[0]
                y = edge.source.pos[1]
                if x1 == x2:
                    x = x1 + 5
                    y1 = edge.source.pos[1]
                    y2 = edge.destination.pos[1]
                    if y1 > y2:
                        aux = y1
                        y1 = y2
                        y2 = aux
                    y = y1 + (y2 - y1) / 2 - 10
                else:
                    if x1 > x2:
                        aux = x1
                        x1 = x2
                        x2 = aux
                    x = x1 + (x2 - x1) / 2 - 10
                surface.blit(textSurface, (x, y))

        # render nodes
        d = 5
        for node in self._world.nodes:
            if node.type == model.Node.SQUARE:
                if node.marked:
                    spriteIndex = SPRITE_NODE_ACTIVE
                else:
                    spriteIndex = SPRITE_NODE_NORMAL
                pos = (node.pos[0] - d, node.pos[1] - d)
                drawSprite(surface, spriteIndex, pos)
                if debug:
                    textSurface = self._context.normalFont.render("%i" % node.id, False, (255, 255, 0))
                    surface.blit(textSurface, (node.pos[0] + 2, node.pos[1] + d * 2 + 2))
        self._world.dirty = False

    def render(self):
        # pre-render level, only re-render if dirty
        if self._world.dirty:
            self._worldSurface.blit(self._background, (0, 0))
            self._rerender()
        self._context.screen.blit(self._worldSurface, (0, 0))

class EdgeView(object):
    def __init__(self, edge = None):
        self.edge = edge

    def update(self, edge):
        if self.edge != edge:
            self.edge = edge
            if self.edge:
                self.nodes = [node for node in [edge.source, edge.destination] if node.type != model.Node.JOINT]
                self.posSource = vectorAdd(edge.source.pos, (-1, -1))
                self.posDest = vectorAdd(edge.destination.pos, (-1, -1))

    def render(self, screen):
        if not self.edge or self.edge.marked:
            return
        ratio = (float(self.edge.markedLength) / self.edge.length)
        if ratio > 1.0:
            ratio = 1.0
        # from 192 to 0
        colorValue1 = 128 * int(1.0 - ratio)
        # from 192 to 255
        colorValue2 = 128 + int((255-128) * ratio)
        color = (colorValue1, colorValue2, colorValue2)
        width = 4

        pygame.draw.line(screen, color, self.posSource, self.posDest, width )

        d = 5
        for node in self.nodes:
            if node.type == model.Node.SQUARE:
                if node.marked:
                    spriteIndex = SPRITE_NODE_ACTIVE
                else:
                    spriteIndex = SPRITE_NODE_NORMAL
                pos = (node.pos[0] - d, node.pos[1] - d)
                drawSprite(screen, spriteIndex, pos)

class Story(object):
    rowDelay = 10

    def __init__(self, context, text):
        self._font = context.bigFont
        font2 = context.biggerFont
        self._pressEnterSurface = font2.render("Press ENTER to continue", False, (0, 255, 0))
        self._textIndex = 0
        self._rowIndex = 0
        self._text = text
        self._textSurfaces = [None]
        self._currentText = ""
        self._delay = 0

    def update(self):
        if self._delay > 0:
            self._delay -= 1
            return
        self._delay = random.randint(0, 4)

        if self._rowIndex >= len(self._text):
            return
        if self._textIndex < len(self._text[self._rowIndex]):
            self._currentText += self._text[self._rowIndex][self._textIndex]
            self._textIndex += 1
        elif self._rowIndex < len(self._text):
            self._textSurfaces[self._rowIndex] = self._font.render(self._currentText, False, (0, 255, 0))
            self._rowIndex += 1
            self._textIndex = 0
            self._currentText = ""
            self._delay = self.rowDelay
            self._textSurfaces.append(None)
        else:
            return

        self._textSurfaces[self._rowIndex] = self._font.render(self._currentText, False, (0, 192, 0))

    def render(self, screen):
        fontHeight = self._font.get_height()
        offsetY = blitTextSurfaces(screen, self._textSurfaces, fontHeight, (10, 10))
        # cursor
        if self._textSurfaces[-1]:
            pygame.draw.rect(screen, (0, 255, 0), (10 + self._textSurfaces[-1].get_width(), offsetY - fontHeight, fontHeight / 2 - 2, fontHeight - 2))
            screen.blit(self._pressEnterSurface, (screen.get_width() / 2 - self._pressEnterSurface.get_width() / 2, screen.get_height() - fontHeight * 2))

class Particle(object):
    def __init__(self, pos = (0,0)):
        self.pos = pos
        self.visible = False
        self.movement = (0, 0)
        self.lifeTime = 0
        self.size = 3

    def update(self):
        self.lifeTime -= 1
        if self.lifeTime <= 0:
            self.visible = False
        self.pos = vectorAdd(self.pos, self.movement)
        # decelerate
        self.movement = vectorFactor(self.movement, 0.95)
        self.size = self.size * 0.9

    def render(self, screen):
        d = int(self.size)
        colorValue = int(self.lifeTime / 60.0 * 255.0)
        color = (0, colorValue, colorValue)
        rect = (int(self.pos[0]) - d, int(self.pos[1]) - d, d * 2, d * 2)
        pygame.draw.rect(screen, color, rect)

    def reset(self):
        self.lifeTime = 60 # one second
        self.size = 3
        self.visible = True

class EntityView(object):
    def __init__(self, entity):
        self._entity = entity

    def update(self):
        pass

    def render(self):
        pass

class PlayerView(EntityView):
    def __init__(self, entity):
        EntityView.__init__(self, entity)
        self._particles = []
        while len(self._particles) < 40:
            particle = Particle()
            particle.visible = False
            self._particles.append(particle)

    def _makeParticles(self):
        toRevive = 1
        for particle in self._particles:
            if toRevive == 0:
                break
            if not particle.visible:
                # revive it
                particle.reset()
                particle.movement = (random.random() * 4.0 - 2.0, random.random() * 4.0 - 2.0)
                particle.pos = self._entity.pos
                toRevive -= 1

    def _renderParticles(self, screen):
        screen.lock()
        for particle in self._particles:
            if not particle.visible:
                continue
            particle.render(screen)
        screen.unlock()

    def update(self):
        if _gameState.pause:
            return

        if self._entity.currentEdge and not self._entity.currentEdge.marked:
            # Marking in progress
            self._makeParticles()

        # update particle position
        for particle in self._particles:
            if not particle.visible:
                continue
            particle.update()

    def render(self, screen):
        offset = (-10,-10)
        alpha = 255
        if _gameState.state == GameState.LEVEL_START:
            alpha = int(_gameState.getProgress() * 255)
        elif _gameState.state == GameState.LEVEL_END:
            alpha = 255 - int(_gameState.getProgress() * 255)
        elif _gameState.state == GameState.DEAD:
            offset = vectorAdd(offset, (random.randint(-3, 3), random.randint(-3, 3)))
            alpha = 255 - int(_gameState.getProgress() * 255)

        self._renderParticles(screen)
        pos = vectorAdd(self._entity.pos, offset)
        drawSprite(screen, SPRITE_PLAYER, pos, alpha)

class FoeView(EntityView):
    def __init__(self, entity):
        EntityView.__init__(self, entity)

    def render(self, screen):
        if self._entity.foeType == 0:
            sprite = SPRITE_FOE1
        else:
            sprite = SPRITE_FOE2
        pos = vectorAdd(self._entity.pos, (-10, -10))
        drawSprite(screen, sprite, pos)

class SelectionView():
    def __init__(self):
        self._nodes = []
        self._edge = None

    def setSelection(self, selection):
        self._nodes = selection

    def setEdgeSelection(self, edge):
        self._edge = edge

    def render(self, screen):
        color = (255, 255, 0)
        for selectedNode in self._nodes:
            if selectedNode.type == model.Node.JOINT:
                d = 3
            else:
                d = 8
            rect = (selectedNode.pos[0] - d, selectedNode.pos[1] - d, d * 2, d * 2)
            pygame.draw.rect(screen, color, rect )

        if self._edge:
            pygame.draw.line(screen, color, self._edge.source.pos, self._edge.destination.pos, 1 )

class Hud(object):
    '''
    '''

    def __init__(self, context):
        self._context = context
        self._gameState = context.gameState
        self._font = context.biggerFont
        self._font2 = context.mediumFont
        self._title = None
        self._subtitle = None
        self._endtext = None
        self._dirty = False
        self._lastScore = None
        self._scoreSurface = None
        self._titleSurfaces = []
        self._subtitleSurfaces = []
        self._endtextSurfaces = []

    def setTitle(self, title = None, subtitle = None, endtext = None):
        self._title = title
        self._subtitle = subtitle
        self._endtext = endtext
        self._dirty = True
        self._updateTextSurfaces()

    def setSubtitle(self, subtitle):
        self._subtitle = subtitle
        self._dirty = True

    def _updateTextSurfaces(self):
        if self._title:
            titleString = "%i) %s" % (self._gameState.worldNum, self._title)
        else:
            titleString = "Level %i" % self._gameState.worldNum

        self._titleSurfaces = makeTextSurfaces(titleString, self._font, (0, 255, 0))

        if self._subtitle:
            subtitleString = self._subtitle
        else:
            subtitleString = ""

        self._subtitleSurfaces = makeTextSurfaces(subtitleString, self._font2, (0, 192, 0))
        self._endtextSurfaces = makeTextSurfaces(self._endtext, self._font2, (255, 255, 0))

    def render(self):
        if self._gameState.state == GameState.TITLE:
            return

        offsetY = blitTextSurfaces(self._context.screen, self._titleSurfaces, self._font.get_height(), (0, 10), self._context.boardSize)

        if self._gameState.state == GameState.LEVEL_END and self._endtext:
            offsetY = self._context.boardSize[1] - self._font2.get_height() * len(self._endtextSurfaces) - 10
            blitTextSurfaces(self._context.screen, self._endtextSurfaces, self._font2.get_height(), (0, offsetY), self._context.boardSize)
        else:
            offsetY = self._context.boardSize[1] - self._font2.get_height() * len(self._subtitleSurfaces) - 10
            blitTextSurfaces(self._context.screen, self._subtitleSurfaces, self._font2.get_height(), (0, offsetY), self._context.boardSize)

        #if self._lastScore != self._gameState.score:
        #    self._lastScore = self._gameState.score
        #    self._scoreSurface = self._font.render("%i" % self._lastScore, False, (0, 192, 0))
        #self._screen.blit(self._scoreSurface, (0, self._screen.get_height() - self._font.get_height()))

class TitleScreen(object):
    def __init__(self, context):
        self._screen = context.screen
        self._font = context.bigFont
        self._font2 = context.normalFont
        fontHeight = self._font.get_height()
        self._textSurface = self._font.render("Press ENTER to start playing", False, (0, 192, 0))
        self._text2Surface = self._font2.render("Copyright \xa9 2012 Vincent Petry (for MiniLD #33)", False, (0, 192, 0))
        rect = self._textSurface.get_rect()
        screenRect = context.screen.get_rect()
        self._pos = (context.boardSize[0] / 2 - rect[2] / 2, 195)
        rect = self._text2Surface.get_rect()
        self._pos2 = (context.boardSize[0] - rect[2] - 20, screenRect[3] - fontHeight - 20)

    def render(self):
        self._screen.blit(self._textSurface, self._pos)
        self._screen.blit(self._text2Surface, self._pos2)
