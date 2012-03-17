'''
@author: Vincent Petry <PVince81@yahoo.fr>
'''

import pygame
import model

debug = False

class Display(object):
    def __init__(self, screen):
        self._screen = screen
        self._entities = []
        self._worldView = None
        
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
        
        if debug:
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
