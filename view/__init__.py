'''
@author: Vincent Petry <PVince81@yahoo.fr>
'''

import pygame
import model

class Display(object):
    def __init__(self, screen):
        self._screen = screen
        self._entities = []
        
    def setWorld(self, world):
        # pre-render level
        self._worldView = WorldView(world)
        self._worldSurface = self._screen.copy()
        self._worldView.render(self._worldSurface)
        
    def render(self):
        self._screen.blit(self._worldSurface, (0, 0))
        for entity in self._entities:
            entity.render(self._screen)
        pass

    def addEntity(self, entity):
        self._entities.append(entity)

class WorldView(object):
    '''
    '''

    def __init__(self, world):
        self._world = world
        
    def render(self, screen):
        color = (255, 255, 255)
        # render edges
        for edge in self._world.edges:
            pygame.draw.line(screen, color, edge.source.pos, edge.destination.pos )

        # render nodes
        d = 5
        for node in self._world.nodes:
            if node.type == model.Node.SQUARE:
                rect = (node.pos[0] - d, node.pos[1] - d, d * 2, d * 2)
                pygame.draw.rect(screen, color, rect )

class PlayerView():
    def __init__(self, player):
        self._player = player
        
    def render(self, screen):
        color = (255, 255, 255)
        pygame.draw.circle(screen, color, (self._player.pos), 10)
