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
from xml.etree import ElementTree as ET

import model

class WorldLoader(object):
    def __init__(self, dataPath = "data/"):
        self.dataPath = dataPath

    def _processNodes(self, world, nodesElement):
        nodes = {}
        for nodeElement in nodesElement.getchildren():
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
        for edgeElement in edgesElement.getchildren():
            if not edgeElement.tag == "edge":
                continue
            source = edgeElement.get("source")
            dest = edgeElement.get("dest")
            reverse = edgeElement.get("reverse", False)
            oneWay = edgeElement.get("oneway", False)
            if not nodes.has_key(source):
                print "Warning: source node %i not found" % source
            elif not nodes.has_key(dest):
                print "Warning: dest node %i not found" % dest
            else:
                world.connectNodeWithJoint(nodes[source], nodes[dest], reverse, oneWay)

    def _processEntities(self, world, nodes, entitiesElement):
        for entityElement in entitiesElement.getchildren():
            startNodeId = entityElement.get("node")
            startNode = None
            if nodes.has_key(startNodeId):
                startNode = nodes[startNodeId]

            if entityElement.tag == "player":
                world.startNode = startNode
            elif entityElement.tag == "foe":
                foeType = entityElement.get("type")
                if foeType == "simple" or foeType == "0":
                    world.createSimpleFoe(startNode)
                else:
                    world.createTrackingFoe(startNode)

    def loadWorld(self, num):
        tree = ET.parse("%slevel%i.xml" % (self.dataPath, num))
        root = tree.getroot()
        world = model.World()
        for element in root.getchildren():
            if element.tag == "nodes":
                nodesElement = element
            elif element.tag == "edges":
                edgesElement = element
            elif element.tag == "entities":
                entitiesElement = element
            elif element.tag == "title":
                world.title = element.text
            elif element.tag == "subtitle":
                world.subtitle = element.text
            elif element.tag == "endtext":
                world.endtext = element.text

        nodes = self._processNodes(world, nodesElement)
        self._processEdges(world, nodes, edgesElement)
        self._processEntities(world, nodes, entitiesElement)

        return world

class WorldSaver(object):
    def __init__(self, dataPath = "data/"):
        self.dataPath = dataPath

    def saveWorld(self, num, world):
        filename = "%slevel%i_editor.xml" % (self.dataPath, num)
        root = ET.Element("level")
        if world.title:
            titleElement = ET.SubElement(root, "title")
            titleElement.text = world.title
        if world.subtitle:
            titleElement = ET.SubElement(root, "subtitle")
            titleElement.text = world.subtitle
        if world.endtext:
            titleElement = ET.SubElement(root, "endtext")
            titleElement.text = world.endtext
        nodesElement = ET.SubElement(root, "nodes")
        edgesElement = ET.SubElement(root, "edges")
        entitiesElement = ET.SubElement(root, "entities")

        nodeId = 1

        for node in world.nodes:
            tagName = "node"
            if node.type == model.Node.JOINT:
                tagName = "joint"
                if len(node.edges) == 0:
                    # ignore orphaned joints
                    continue
            ET.SubElement(nodesElement, tagName, {"id": str(nodeId), "x": str(node.pos[0]), "y": str(node.pos[1])})
            node.id = nodeId
            nodeId += 1
        for edge in world.edges:
            edgeElement = ET.SubElement(edgesElement, "edge", {"source": str(edge.source.id), "dest": str(edge.destination.id)})
            #if edge.reverse:
            #   edgeElement.set("reverse", "true")
            if edge.oneWay:
                edgeElement.set("oneway", "true")

        ET.SubElement(entitiesElement, "player", {"node": str(world.startNode.id)})
        for entity in world.entities:
            if entity.entityType == 1:
                foeElement = ET.SubElement(entitiesElement, "foe", {"node": str(entity.currentNode.id)})
                if entity.foeType == 0:
                    foeElement.set("type", "simple")
                else:
                    foeElement.set("type", "tracking")

        tree = ET.ElementTree(root)
        tree.write(filename)
