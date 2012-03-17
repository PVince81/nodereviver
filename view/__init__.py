'''
@author: Vincent Petry <PVince81@yahoo.fr>
'''

import pygame
import model

class Display(object):
    def __init__(self, screen):
        self._screen = screen
        self._entities = []
        self._worldView = None
        
    def setWorld(self, world):
        world.dirty = True
        self._worldView = WorldView(self._screen, world)
        
    def render(self):
        self._worldView.render()
        for entity in self._entities:
            entity.render(self._screen)

    def addEntity(self, entity):
        self._entities.append(entity)
        
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

        # render nodes
        d = 5
        color = (255, 255, 255)
        for node in self._world.nodes:
            if node.type == model.Node.SQUARE:
                rect = (node.pos[0] - d, node.pos[1] - d, d * 2, d * 2)
                pygame.draw.rect(surface, color, rect )
        self._world.dirty = False

    def render(self):
        # pre-render level, only re-render if dirty
        if self._world.dirty:
            self._worldSurface.blit(self._background, (0, 0))
            self._rerender()
        self._screen.blit(self._worldSurface, (0, 0))        

class PlayerView():
    def __init__(self, player):
        self._player = player
        
    def render(self, screen):
        color = (255, 255, 255)
        pygame.draw.circle(screen, color, (self._player.pos), 10)
