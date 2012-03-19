'''
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

class Display(object):
    def __init__(self, config, screen, gameState):
        self._screen = screen
        self._entities = []
        self._worldView = None
        self._titleScreen = TitleScreen(screen)
        self._gameState = gameState
        self._hud = Hud(screen, gameState)
        self.selectionView = SelectionView()
        self._edgeView = EdgeView()
        # UGLY, I know... but I'm tired to pass everything along 
        global _spriteSurface
        global _gameState
        _gameState = gameState
        _spriteSurface = pygame.image.load(config.dataPath + "sprites.png")
        #_spriteSurface = _spriteSurface.convert_alpha(screen)
        _spriteSurface = _spriteSurface.convert(screen)
        _spriteSurface.set_colorkey((0, 0, 0), pygame.RLEACCEL)
        
    def setWorld(self, world, player):
        self.clear()
        world.dirty = True
        self._world = world
        self._player = player
        self._worldView = WorldView(self._screen, world)
        for entity in world.entities:
            # entities are all foes for now (except player)
            self.addEntityView(FoeView(entity))
        self._hud.setTitle(world.title, world.subtitle, world.endtext)
        
    def render(self):
        self._worldView.render()
        self._hud.render()
        self._edgeView.update(self._player.currentEdge)
        self._edgeView.render(self._screen)
        for entity in self._entities:
            entity.render(self._screen)
        if self._gameState.state == GameState.TITLE:
            self._titleScreen.render()
        self.selectionView.render(self._screen)

    def addEntityView(self, entityView):
        self._entities.append(entityView)
        
    def clear(self):
        self._entities = []

class WorldView(object):
    '''
    '''

    def __init__(self, screen, world):
        self._screen = screen
        self._world = world
        self._background = self._screen.copy()
        self._background.fill((0, 0, 0))
        self._worldSurface = self._screen.copy()
        
        self._font = pygame.font.SysFont('serif', 10)
        
    def _rerender(self):
        surface = self._worldSurface
        surface.lock()
        # render edges
        for edge in self._world.edges:
            width = 4
            if edge.isMarked():
                color = (0, 255, 255)
            else:
                color = (128, 128, 128)

            # HACK: pygame.draw.line doesn't apply the width around the position,
            # so need to shift it manually
            posSource = vectorAdd(edge.source.pos, (-1, -1))
            posDest = vectorAdd(edge.destination.pos, (-1, -1))
            
            pygame.draw.line(surface, color, posSource, posDest, width )
            if edge.oneWay and edge.destination.type != model.Node.JOINT:
                # Draw arrow
                dir = unitVector(vectorDiff(posDest, posSource))
                # go back a few pixels because of the node size,
                # this is the arrow head's position
                pos = vectorAdd(edge.destination.pos, vectorFactor(dir, -6))
                # go back further for the back of the arrow
                pos1 = vectorAdd(pos, vectorFactor(dir, -5))
                pos2 = pos1
                pos1 = vectorAdd(pos1, vectorFactor(vectorSwap(dir), 5))
                pos2 = vectorAdd(pos2, vectorFactor(vectorSwap(dir), -5))
                pygame.draw.line(surface, color, pos, pos1, width )
                pygame.draw.line(surface, color, pos, pos2, width )
            
            if debug:
                textSurface = self._font.render("%i" % edge.length, False, (0, 128, 128))
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
                    color = (255, 255, 0)
                else:
                    color = (255, 255, 255)
                rect = (node.pos[0] - d, node.pos[1] - d, d * 2, d * 2)
                pygame.draw.rect(surface, color, rect )
                if debug:
                    textSurface = self._font.render("%i" % node.id, False, (255, 255, 0)) 
                    surface.blit(textSurface, (node.pos[0] + 2, node.pos[1] + d * 2 + 2))
        self._world.dirty = False
        surface.unlock()

    def render(self):
        # pre-render level, only re-render if dirty
        if self._world.dirty:
            self._worldSurface.blit(self._background, (0, 0))
            self._rerender()
        self._screen.blit(self._worldSurface, (0, 0))        

class EdgeView(object):
    def __init__(self, edge = None):
        self.edge = edge
        self.angleStep = 2.0 * math.pi / 60.0 
    
    def update(self, edge):
        if self.edge != edge:
            self.edge = edge
            self.angle = 0
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
        color = (255, 255, 255)
        for node in self.nodes:
            rect = (node.pos[0] - d, node.pos[1] - d, d * 2, d * 2)
            pygame.draw.rect(screen, color, rect )

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

class PlayerView():
    rect = pygame.Rect(0, 0, 20, 20)

    def __init__(self, entity):
        self._entity = entity
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
            if not _gameState.pause:
                particle.update()
            particle.render(screen)
        screen.unlock()
        
    def render(self, screen):
        #color = (0, 0, 0)
        #pygame.draw.circle(screen, color, (self._entity.pos), 10)
        offset = (-10,-10)
        alpha = 255
        if _gameState.state == GameState.LEVEL_START:
            alpha = int(_gameState.getProgress() * 255)
        elif _gameState.state == GameState.LEVEL_END:
            alpha = 255 - int(_gameState.getProgress() * 255)
        elif _gameState.state == GameState.DEAD:
            offset = vectorAdd(offset, (random.randint(-3, 3), random.randint(-3, 3)))
            alpha = 255 - int(_gameState.getProgress() * 255)

        _spriteSurface.set_alpha(alpha)
        pos = vectorAdd(self._entity.pos, offset)
        screen.blit(_spriteSurface, pos, self.rect )
        if self._entity.currentEdge and not self._entity.currentEdge.marked:
            # Marking in progress
            self._makeParticles()
        self._renderParticles(screen)
        _spriteSurface.set_alpha(255)

class FoeView():
    rect0 = pygame.Rect(20, 0, 20, 20)
    rect1 = pygame.Rect(40, 0, 20, 20)
    
    def __init__(self, entity):
        self._entity = entity
        
    def render(self, screen):
        if self._entity.foeType == 0:
            rect = self.rect0
        else:
            rect = self.rect1
        pos = vectorAdd(self._entity.pos, (-10, -10))
        screen.blit(_spriteSurface, pos, rect )

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

def makeTextSurfaces(text, font, color = (255, 255, 255)):
    if not text:
        return []
    surfaces = []
    rows = text.split("\\n")
    for row in rows:
        surfaces.append( font.render(row, False, color) )
    return surfaces

def blitTextSurfaces(targetSurface, surfaces, offsetY, fontHeight):
    offset = 0
    for surface in surfaces:
        offset = int(targetSurface.get_width() / 2 - surface.get_width() / 2)            
        targetSurface.blit(surface, (offset, offsetY))
        offsetY += fontHeight
    return offsetY

class Hud(object):
    '''
    '''

    def __init__(self, screen, gameState):
        self._screen = screen
        self._gameState = gameState        
        self._font = pygame.font.SysFont('monospace', 20)
        self._font2 = pygame.font.SysFont('monospace', 15)
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
            titleString = "%i) %s was hacked." % (self._gameState.worldNum, self._title)
        else:
            titleString = "%i) They hacked something" % self._gameState.worldNum

        self._titleSurfaces = makeTextSurfaces(titleString, self._font, (0, 255, 0))

        if self._subtitle:
            subtitleString = "Please fix it...\\n" + self._subtitle
        else:
            subtitleString = "Please revive its nodes !"

        self._subtitleSurfaces = makeTextSurfaces(subtitleString, self._font2, (0, 192, 0))
        self._endtextSurfaces = makeTextSurfaces(self._endtext, self._font2, (255, 255, 0))

    def render(self):
        if self._gameState.state == GameState.TITLE:
            return

        offsetY = blitTextSurfaces(self._screen, self._titleSurfaces, 10, self._font.get_height())
        
        if self._gameState.state == GameState.LEVEL_END and self._endtext:
            offsetY = self._screen.get_height() - self._font2.get_height() * len(self._endtextSurfaces) - 10
            blitTextSurfaces(self._screen, self._endtextSurfaces, offsetY, self._font2.get_height())
        else:
            offsetY = self._screen.get_height() - self._font2.get_height() * len(self._subtitleSurfaces) - 10
            blitTextSurfaces(self._screen, self._subtitleSurfaces, offsetY, self._font2.get_height())

        if self._lastScore != self._gameState.score:
            self._lastScore = self._gameState.score
            self._scoreSurface = self._font.render("%i" % self._lastScore, False, (0, 192, 0))
        self._screen.blit(self._scoreSurface, (0, self._screen.get_height() - self._font.get_height()))

class TitleScreen(object):
    def __init__(self, screen):
        self._screen = screen
        self._font = pygame.font.SysFont('monospace', 18)
        fontHeight = self._font.get_height()
        self._textSurface = self._font.render("Press ENTER to start playing", False, (0, 192, 0))
        self._text2Surface = self._font.render("By Vincent Petry (for MiniLD #33)", False, (0, 192, 0))
        rect = self._textSurface.get_rect()
        screenRect = screen.get_rect()
        self._pos = (screenRect[2] / 2 - rect[2] / 2, 195)
        rect = self._text2Surface.get_rect()
        self._pos2 = (screenRect[2] - rect[2] - 20, screenRect[3] - fontHeight - 20) 

    def render(self):
        self._screen.blit(self._textSurface, self._pos)
        self._screen.blit(self._text2Surface, self._pos2)
