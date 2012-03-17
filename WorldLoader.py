'''
@author: Vincent Petry <PVince81@yahoo.fr>
'''
from xml.etree import ElementTree

import model

class WorldLoader(object):
    def __init__(self, dataPath = "data/"):
        self.dataPath = dataPath
    
    def _processNodes(self, world, nodesElement):
        nodes = {}
        for nodeElement in nodesElement.iter():
            if not nodeElement.tag == "node" and not nodeElement.tag == "joint":
                continue
            id = nodeElement.get("id")
            x = int(nodeElement.get("x", 0))
            y = int(nodeElement.get("y", 0))
            nodeType = model.Node.SQUARE
            if nodeElement.tag == "joint":
                nodeType = model.Node.JOINT
            node = world.createNode((x, y), nodeType)
            if id:
                nodes[id] = node
        return nodes
    
    def _processEdges(self, world, nodes, edgesElement):
        for edgeElement in edgesElement.iter():
            if not edgeElement.tag == "edge":
                continue
            source = edgeElement.get("source")
            dest = edgeElement.get("dest")
            reverse = edgeElement.get("reverse", False)
            if nodes.has_key(source) and nodes.has_key(dest):
                world.connectNodeWithJoint(nodes[source], nodes[dest], reverse)
    
    def _processEntities(self, world, nodes, entitiesElement):
        for entityElement in entitiesElement.iter():
            startNodeId = entityElement.get("node")
            startNode = None
            if nodes.has_key(startNodeId):
                startNode = nodes[startNodeId]

            if entityElement.tag == "player":
                world.startNode = startNode
            elif entityElement.tag == "foe":
                foeType = entityElement.get("type")
                if foeType == "simple" or foeType == "0":
                    foe = world.createSimpleFoe(startNode)
                else:
                    foe = world.createTrackingFoe(startNode)          
    
    def loadWorld(self, num):
        tree = ElementTree.parse("%slevel%i.xml" % (self.dataPath, num))
        root = tree.getroot()
        world = model.World()
        for element in root.iter():
            if element.tag == "nodes":
                nodesElement = element
            elif element.tag == "edges":
                edgesElement = element
            elif element.tag == "entities":
                entitiesElement = element

        nodes = self._processNodes(world, nodesElement)
        self._processEdges(world, nodes, edgesElement)
        self._processEntities(world, nodes, entitiesElement)

        return world
