'''
@author: Vincent Petry <PVince81@yahoo.fr>
'''

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

class Edge(object):
    def __init__(self, source, destination):
        self.source = source
        self.destination = destination

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
        
        return world
    