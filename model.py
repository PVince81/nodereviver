'''
@author: Vincent Petry <PVince81@yahoo.fr>
'''
import random

def unitVector(vector):
    if vector[0] != 0:
        return (vector[0] / abs(vector[0]), 0)
    elif vector[1] != 0:
        return (0, vector[1] / abs(vector[1]))
    return (0, 0)

def vectorDiff(vector1, vector2):
    return (vector1[0] - vector2[0], vector1[1] - vector2[1])

def vectorMult(vector1, vector2):
    return (vector1[0] * vector2[0], vector1[1] * vector2[1])


class PathFinder:
    def __init__(self):
        self.path = None
        self.pathLength = 0
        self.shortestPath = None
        self.shortestPathLength = None
        self.edges = None
        self.shortestPathEdges = None
        self.sourceNode = None
        self.targetNode = None

    def findShortestPath(self, sourceNode, targetNode):
        '''
        Finds the shortest path from sourceNode to targetNode.
        @return: array of node's starting edges to follow to reach the target
        '''
        self.path = list()
        self.pathLength = 0
        self.edges = list()
        self.shortestPath = None
        self.shortestPathEdges = []
        self.shortestPathLength = None
        self.sourceNode = sourceNode
        self.targetNode = targetNode
        self.path.append(sourceNode)
        self._exploreNode(sourceNode)

        # remove joint nodes
        finalEdges = []
        node = sourceNode
        for edge in self.shortestPathEdges:
            if node.type != Node.JOINT:
                finalEdges.append(edge)
            node = edge.getOther(node)

        return finalEdges

    def _exploreNode(self, node):
        if self.shortestPathLength and self.pathLength >= self.shortestPathLength:
            return False

        if node == self.targetNode:
            self.shortestPath = list(self.path)
            self.shortestPathEdges = list(self.edges)
            self.shortestPathLength = self.pathLength
            return True

        for edge in node.edges:
            nextNode = edge.getOther(node)
            if not nextNode in self.path:
                self.path.append(nextNode)
                self.edges.append(edge)
                self.pathLength += edge.length
                self._exploreNode(nextNode)
                self.pathLength -= edge.length
                self.edges.pop()
                self.path.pop()
        return False
    
    def printPath(self, sourceNode, edges):
        node = sourceNode
        for edge in edges:
            print node
            print edge
            node = edge.getOther(node)
        print node

pathFinder = PathFinder()

_nextNodeId = 1
class Node(object):
    SQUARE = 0
    JOINT = 1
    
    def __init__(self, world, pos = (0, 0), nodeType = SQUARE):
        global _nextNodeId
        self.id = _nextNodeId
        _nextNodeId += 1
        self.world = world
        self.type = nodeType
        self.pos = pos
        # Edges are saved in this order: up, down, left, right
        self.edges = []
    
    def connect(self, otherNode):
        '''
        Connects the current node to the other node
        and returns the generated edge
        '''
        edge = Edge(self.world, self, otherNode)
        self.edges.append(edge)
        otherNode.edges.append(edge)
        return edge

    def getEdge(self, direction):
        '''
        Returns the edge going in the given direction or None if none found.
        @param direction: direction vector 
        '''
        for edge in self.edges:
            destNode = edge.getOther(self)
            diff = unitVector(vectorDiff(destNode.pos, self.pos))
            if direction == diff:
                return edge
        return None
    
    def getOtherEdge(self, sourceEdge):
        for edge in self.edges:
            if edge != sourceEdge:
                return edge
        return None
        
    def getNextNode(self, edge):
        '''
        Returns the next node following the path along the given edge.
        @param edge edge to use as direction 
        '''
        nextNode = edge.getOther(self)
        while nextNode.type == Node.JOINT and nextNode != self:
            nextNode = nextNode.getNextNode(nextNode.getOtherEdge(edge))

        return nextNode
    
    def __str__(self):
        typeString = "S"
        if self.type == Node.JOINT:
            typeString = "J"
        return "Node{id=%i,pos=%s,type=%s}" % (self.id, self.pos.__str__(), typeString)

_nextEdgeId = 1
class Edge(object):
    def __init__(self, world, source, destination):
        global _nextEdgeId
        self.id = _nextEdgeId
        _nextEdgeId += 1
        self.world = world
        self.source = source
        self.destination = destination
        self.marked = False
        diff = vectorDiff(source.pos, destination.pos)
        if diff[0] != 0:
            self.length = abs(diff[0])
        else:
            self.length = abs(diff[1])

    def getOther(self, source):
        if source == self.source:
            return self.destination
        return self.source

    def isMarked(self):
        return self.marked

    def setMarked(self, marked):
        if self.marked != marked:
            self.marked = True
            self.world.markedEdges += 1
            self.world.dirty = True

    def __str__(self):
        return "Edge{id=%i,src=%s,dst=%s,len=%i}" % (self.id, self.source.__str__(), self.destination.__str__(), self.length)

class World(object):
    '''
    World
    '''
    UP = 0
    DOWN = 1
    LEFT = 2
    RIGHT = 3

    def __init__(self):
        self.nodes = []
        self.edges = []
        self.entities = []
        self.startNode = None
        self.dirty = False
        self.markedEdges = 0
        global _nextEdgeId
        global _nextNodeId
        _nextEdgeId = 1
        _nextNodeId = 1
    
    def update(self):
        for entity in self.entities:
            entity.update()
        
    def addEntity(self, entity):
        self.entities.append(entity)

    def createSimpleFoe(self, startNode):
        foe = SimpleFoe(startNode)
        self.entities.append(foe)
        self.dirty = True

    def createTrackingFoe(self, startNode):
        foe = TrackingFoe(startNode)
        self.entities.append(foe)
        self.dirty = True

    def createNode(self, pos = (0, 0), nodeType = Node.SQUARE):
        node = Node(self, pos, nodeType)
        self.nodes.append(node)
        self.dirty = True
        return node

    def deleteNode(self, node):
        self.nodes.remove(node)
        for edge in list(node.edges):
            self.deleteEdge(edge)
        self.dirty = True
            
    def deleteEdge(self, edge):
        if edge.source:
            edge.source.edges.remove(edge)
        if edge.destination:
            edge.destination.edges.remove(edge)
        self.edges.remove(edge)
        self.dirty = True

    def connectNode(self, node1, node2 ):
        self.dirty = True
        self.edges.append( node1.connect(node2) )

    def connectNodeWithJoint(self, node1, node2, reverse = False):
        self.dirty = True
        if node1.pos[0] == node2.pos[0] or node1.pos[1] == node2.pos[1]:
            self.edges.append( node1.connect(node2) )
        else:
            if reverse:
                angleNode = self.createNode((node2.pos[0], node1.pos[1]), Node.JOINT)
            else:
                angleNode = self.createNode((node1.pos[0], node2.pos[1]), Node.JOINT)
            self.nodes.append(angleNode)
            self.edges.append(node1.connect(angleNode))
            self.edges.append(node2.connect(angleNode))

    def getNodeAt(self, pos, margin = 5):
        for node in self.nodes:
            dist = vectorDiff(node.pos, pos)
            if abs(dist[0]) <= margin and abs(dist[1]) <= margin:
                return node
        return None 

    def hasAllEdgesMarked(self):
        return self.markedEdges == len(self.edges)

class Entity(object):
    entityType = -1
    def __init__(self, currentNode = None):
        self.pos = (0, 0)
        self.currentNode = None
        self.currentEdge = None
        self.setCurrentNode(currentNode)
        self.movement = (0, 0)
        self.moving = False
        self.targetNode = None
        self.destination = (0, 0)
        self.speed = 1
        self.dead = False

    def die(self):
        self.dead = True

    def moveTo(self, targetNode):
        self.targetNode = targetNode
        self.destination = targetNode.pos
        self.move(unitVector(vectorDiff(self.destination, self.pos)))

    def moveAlong(self, targetEdge):
        self.currentEdge = targetEdge
        self.moveTo( targetEdge.getOther(self.currentNode) )

    def move(self, movement = (0, 0)):
        self.movement = movement
        self.moving = ( movement != (0, 0) )

    def update(self):
        if self.moving:
            self.pos = ( self.pos[0] + self.movement[0] * self.speed, self.pos[1] + self.movement[1] * self.speed )
            distance = vectorDiff(self.destination, self.pos)
            if ( self.movement[0] != 0 and abs(distance[0]) < self.speed ) or ( self.movement[1] != 0 and abs(distance[1]) < self.speed ):
                self.pos = self.targetNode.pos
                self.currentNode = self.targetNode
                self.onEdgeComplete(self.currentEdge)
                if self.currentNode.type == Node.JOINT:
                    # need to continue along the next edge
                    edge = self.currentNode.getOtherEdge(self.currentEdge)
                    self.moveAlong( edge )
                else:                                   
                    self.moving = False
                    self.movement = (0, 0)
                    self.targetNode = None
                    self.currentEdge = None

    def getFinalTargetNode(self):
        if not self.moving:
            return None
        if self.targetNode.type == Node.JOINT:
            return self.currentNode.getNextNode(self.currentEdge)
        return self.targetNode
        
    def onEdgeComplete(self, edge):
        pass

    def setCurrentNode(self, currentNode = None):
        self.currentNode = currentNode
        if currentNode:
            self.pos = currentNode.pos
        else:
            self.pos = (0, 0)

class Player(Entity):
    entityType = 0
    def __init__(self, currentNode = None):
        Entity.__init__(self, currentNode)
        self.speed = 2
        
    def onEdgeComplete(self, edge):
        edge.setMarked(True)

class Foe(Entity):
    entityType = 1
    def __init__(self, currentNode = None):
        Entity.__init__(self, currentNode)

class SimpleFoe(Foe):
    '''
    Simple foe that randomly changes direction.
    '''
    foeType = 0
    def __init__(self, currentNode = None):
        Foe.__init__(self, currentNode)
        self.speed = 1
        self.lastEdge = None

    def update(self):
        if self.moving:
            Foe.update(self)
        else:
            # find path
            index = random.randint(0, len(self.currentNode.edges) - 1)
            nextEdge = self.currentNode.edges[index]
            if nextEdge == self.lastEdge:
                if index >= len(self.currentNode.edges) - 1:
                    nextEdge = self.currentNode.edges[0]
                else:
                    nextEdge = self.currentNode.edges[index + 1]
            self.moveAlong(nextEdge)  

    def onEdgeComplete(self, edge):
        self.lastEdge = edge

class TrackingFoe(Foe):
    '''
    Foe that tracks another entity (the player) and finds the shortest path.
    '''
    foeType = 1

    def __init__(self, currentNode = None, trackedEntity = None):
        Foe.__init__(self, currentNode)
        self.speed = 1
        self._trackedEntity = trackedEntity
        self._path = []
        self._sleepTicks = 0

    def track(self, trackedEntity):
        self._trackedEntity = trackedEntity
        self._path = []

    def update(self):
        if self._sleepTicks > 0:
            self._sleepTicks -= 1
            return
        elif self.moving:
            Foe.update(self)
        else:
            # find path to player
            if len(self._path) > 0:
                nextEdge = self._path[0]
                self._path = self._path[1:]
                self.moveAlong(nextEdge)
            elif random.randint(0, 5) == 0:
                # sleep for a second
                self._sleepTicks = 60
            elif self._trackedEntity and ( self._trackedEntity.currentNode != self.currentNode or self._trackedEntity.currentNode != self.targetNode):
                targetNode = self._trackedEntity.currentNode
                if self._trackedEntity.moving:
                    # directly go to that entity's target
                    targetNode = self._trackedEntity.getFinalTargetNode()
                if targetNode != self.currentNode:
                    self._path = pathFinder.findShortestPath(self.currentNode, targetNode)

        dist = vectorDiff(self._trackedEntity.pos, self.pos)
        if abs(dist[0]) < 10 and abs(dist[1]) < 10:
            self._trackedEntity.die()

class GameState(object):
    def __init__(self):
        self.score = 0
        self.lives = 5
        self.worldNum = 1
        self.dirty = True
