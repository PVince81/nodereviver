'''
@author: Vincent Petry <PVince81@yahoo.fr>
'''

def unitVector(vector):
    if vector[0] != 0:
        return (vector[0] / abs(vector[0]), 0)
    elif vector[1] != 0:
        return (0, vector[1] / abs(vector[1]))
    return (0, 0)

def vectorDiff(vector1, vector2):
    return (vector1[0] - vector2[0], vector1[1] - vector2[1])

class Node(object):
    SQUARE = 0
    JOINT = 1
    
    def __init__(self, pos = (0, 0), nodeType = SQUARE):
        self.type = nodeType
        self.pos = pos
        # Edges are saved in this order: up, down, left, right
        self.edges = []
    
    def connect(self, otherNode):
        '''
        Connects the current node to the other node
        and returns the generated edge
        '''
        edge = Edge(self, otherNode)
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
    
    def getOtherEdge(self, direction):
        '''
        Returns the edge NOT going in the given direction or None if none found,
        assuming that this node is a JOINT (they only have two edges)
        @param direction: direction vector 
        '''
        for edge in self.edges:
            destNode = edge.getOther(self)
            diff = unitVector(vectorDiff(destNode.pos, self.pos))
            if direction != diff:
                return edge
        return None

    def __str__(self):
        return "Node{pos=" + self.pos.__str__() + "}"

class Edge(object):
    def __init__(self, source, destination):
        self.source = source
        self.destination = destination

    def getOther(self, source):
        if source == self.source:
            return self.destination
        return self.source

    def __str__(self):
        return "Edge{source=" + self.source.__str__()  + ",destination=" + self.destination.__str__()  + "}"

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
        self.startNode = None

    def createNode(self, pos = (0, 0), nodeType = Node.SQUARE):
        node = Node(pos, nodeType)
        self.nodes.append(node)
        return node
    
    def connectNode(self, node1, node2 ):
        self.edges.append( node1.connect(node2) )

    def connectNodeWithJoint(self, node1, node2, reverse = False):
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


    @staticmethod
    def getWorld(worldNum):
        world = World()
        
        node1 = world.createNode((100, 100))
        node2 = world.createNode((200, 100))
        node3 = world.createNode((140, 160))
        node4 = world.createNode((140, 200))
        node5 = world.createNode((220, 220))
        node6 = world.createNode((70, 180))
        
        # TODO: should figure out the direction based on coordinates
        world.connectNodeWithJoint(node1, node2)
        world.connectNodeWithJoint(node1, node3)
        world.connectNodeWithJoint(node2, node3)
        world.connectNodeWithJoint(node3, node4)
        world.connectNodeWithJoint(node4, node5)
        world.connectNodeWithJoint(node2, node5, 1)
        world.connectNodeWithJoint(node4, node6, 1)
        world.connectNodeWithJoint(node6, node1)

        world.startNode = node4
        return world

class Entity(object):
    def __init__(self, currentNode = None):
        self.pos = (0, 0)
        self.setCurrentNode(currentNode)
        self.movement = (0, 0)
        self.moving = False
        self.targetNode = None
        self.destination = (0, 0)

    def moveTo(self, targetNode):
        self.targetNode = targetNode
        self.destination = targetNode.pos
        self.move(unitVector(vectorDiff(self.destination, self.pos)))
        
    def move(self, movement = (0, 0)):
        self.movement = movement
        self.moving = ( movement != (0, 0) )
        
    def update(self):
        if self.moving:
            self.pos = ( self.pos[0] + self.movement[0], self.pos[1] + self.movement[1] )
            # TODO: use target window ?
            if self.pos == self.destination:
                self.currentNode = self.targetNode
                if self.currentNode.type == Node.JOINT:
                    # need to continue along the next edge
                    edge = self.currentNode.getOtherEdge((-self.movement[0], -self.movement[1]))
                    self.moveTo( edge.getOther(self.currentNode) )
                else:                                   
                    self.moving = False
                    self.movement = (0, 0)
                    self.targetNode = None

    def setCurrentNode(self, currentNode = None):
        self.currentNode = currentNode
        if currentNode:
            self.pos = currentNode.pos
        else:
            self.pos = (0, 0)

class Player(Entity):
    def __init__(self, currentNode = None):
        Entity.__init__(self, currentNode)

