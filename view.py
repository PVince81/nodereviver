'''
@author: Vincent Petry <PVince81@yahoo.fr>
'''

import pygame
import model
from util import *

debug = False

class Display(object):
    def __init__(self, screen, gameState):
        self._screen = screen
        self._entities = []
        self._worldView = None
        self._hud = Hud(screen, gameState)
        self.selectionView = SelectionView()
        
    def setWorld(self, world):
        self.clear()
        world.dirty = True
        self._worldView = WorldView(self._screen, world)
        for entity in world.entities:
            # entities are all foes for now (except player)
            self.addEntityView(FoeView(entity))
        
    def render(self):
        self._worldView.render()
        for entity in self._entities:
            entity.render(self._screen)
        self._hud.render()
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
        # render edges
        for edge in self._world.edges:
            if edge.isMarked():
                color = (0, 255, 255)
                width = 3
            else:
                color = (192, 192, 192)
                width = 1
            pygame.draw.line(surface, color, edge.source.pos, edge.destination.pos, width )
            if edge.oneWay and edge.destination.type != model.Node.JOINT:
                # Draw arrow
                dir = unitVector(vectorDiff(edge.destination.pos, edge.source.pos))
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
        color = (255, 255, 255)
        for node in self._world.nodes:
            if node.type == model.Node.SQUARE:
                rect = (node.pos[0] - d, node.pos[1] - d, d * 2, d * 2)
                pygame.draw.rect(surface, color, rect )
                if debug:
                    textSurface = self._font.render("%i" % node.id, False, (255, 255, 0)) 
                    surface.blit(textSurface, (node.pos[0] + 2, node.pos[1] + d * 2 + 2))
        self._world.dirty = False

    def render(self):
        # pre-render level, only re-render if dirty
        if self._world.dirty:
            self._worldSurface.blit(self._background, (0, 0))
            self._rerender()
        self._screen.blit(self._worldSurface, (0, 0))        

class PlayerView():
    def __init__(self, entity):
        self._entity = entity
        
    def render(self, screen):
        color = (255, 255, 255)
        pygame.draw.circle(screen, color, (self._entity.pos), 10)

class FoeView():
    def __init__(self, entity):
        self._entity = entity
        
    def render(self, screen):
        if self._entity.foeType == 0:
            color = (255, 128, 0)
        else:
            color = (255, 0, 0)
        pygame.draw.circle(screen, color, (self._entity.pos), 10)

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

    def __init__(self, screen, gameState):
        self._screen = screen
        self._gameState = gameState
        self._surface = pygame.Surface((200, 20), 0, screen)
        self._surface.fill((0, 0, 0))
        self._font = pygame.font.SysFont('serif', 10)
        
    def _rerender(self):
        self._surface.fill((0, 0, 0))
        fontHeight = self._font.get_height()

        hudSurfaces = []
        hudSurfaces.append( self._font.render("Level: %i  Lives: %i" % (self._gameState.worldNum, self._gameState.lives), False, (255, 255, 255)) )
        #hudSurfaces.append( self._font.render("Lives: %i" % self._gameState.lives, False, (255, 255, 255)) )

        offset = 0
        for hudSurface in hudSurfaces:
            self._surface.blit(hudSurface, (0,offset))
            offset += fontHeight

    def render(self):
        if self._gameState.dirty:
           self._rerender()
           self._gameState.dirty = False
        self._screen.blit(self._surface, (0, 0))
