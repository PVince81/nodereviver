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
try:
    import json
except:
    import simplejson as json

import model

class WorldLoader(object):
    def __init__(self, dataPath = "data/"):
        self.dataPath = dataPath

    def _processNodes(self, world, nodesElement):
        nodes = {}
        for nodeElement in nodesElement:
            if not nodeElement["type"] == "node" and not nodeElement["type"] == "joint":
                continue
            nodeId = nodeElement["id"]
            x = int(nodeElement["x"])
            y = int(nodeElement["y"])
            nodeType = model.Node.SQUARE
            if nodeElement["type"] == "joint":
                nodeType = model.Node.JOINT
            node = world.createNode((x, y), nodeType)
            if nodeId:
                nodes[nodeId] = node
        return nodes

    def _processEdges(self, world, nodes, edgesElement):
        for edgeElement in edgesElement:
            source = int(edgeElement["source"])
            dest = int(edgeElement["dest"])
            reverse = edgeElement.has_key("reverse") and edgeElement["reverse"]
            oneWay = edgeElement.has_key("oneway") and edgeElement["oneway"]
            if not nodes.has_key(source):
                print "Warning: source node %i not found" % source
            elif not nodes.has_key(dest):
                print "Warning: dest node %i not found" % dest
            else:
                world.connectNodeWithJoint(nodes[source], nodes[dest], reverse, oneWay)

    def _processEntities(self, world, nodes, entitiesElement):
        for entityElement in entitiesElement:
            startNodeId = int(entityElement["node"])
            startNode = None
            if nodes.has_key(startNodeId):
                startNode = nodes[startNodeId]
            if entityElement["type"] == "player":
                world.startNode = startNode
            elif entityElement["type"] == "foe":
                foeType = entityElement["foeType"]
                if foeType == "simple" or foeType == "0":
                    world.createSimpleFoe(startNode)
                else:
                    world.createTrackingFoe(startNode)

    def loadWorld(self, num):
        f = open("%slevel%i.json" % (self.dataPath, num), 'r')
        root = json.load(f)
        f.close()

        world = model.World()
        if root.has_key("title"):
            world.title = root["title"]
        if root.has_key("subtitle"):
            world.subtitle = root["subtitle"]
        if root.has_key("endtext"):
            world.endtext = root["endtext"]

        nodes = self._processNodes(world, root["nodes"])
        self._processEdges(world, nodes, root["edges"])
        self._processEntities(world, nodes, root["entities"])

        return world

class WorldSaver(object):
    def __init__(self, dataPath = "data/"):
        self.dataPath = dataPath

    def saveWorld(self, num, world):
        filename = "%slevel%i_editor.json" % (self.dataPath, num)
        output = {}
        if world.title:
            output["title"] = world.title
        if world.subtitle:
            output["subtitle"] = world.subtitle
        if world.endtext:
            output["endtext"] = world.endtext

        nodesElement = output["nodes"] = []
        edgesElement = output["edges"] = []
        entitiesElement = output["entities"] = []

        nodeId = 1

        for node in world.nodes:
            nodeType = "node"
            if node.type == model.Node.JOINT:
                nodeType = "joint"
                if len(node.edges) == 0:
                    # ignore orphaned joints
                    continue
            nodesElement.append({"id": nodeId, "type": nodeType, "x": str(node.pos[0]), "y": str(node.pos[1])})
            node.id = nodeId
            nodeId += 1
        for edge in world.edges:
            edgeElement = {"source": str(edge.source.id), "dest": str(edge.destination.id)}
            edgesElement.append(edgeElement)
            #if edge.reverse:
            #   edgeElement.set("reverse", "true")
            if edge.oneWay:
                edgeElement["oneway"] = True

        entitiesElement.append({"type": "player", "node": str(world.startNode.id)})
        for entity in world.entities:
            if entity.entityType == 1:
                foeElement = {"type": "foe", "node": str(entity.currentNode.id)}
                entitiesElement.append(foeElement)
                if entity.foeType == 0:
                    foeElement["foeType"] = "simple"
                else:
                    foeElement["foeType"] = "tracking"

        f = open(filename, 'w')
        json.dump(output, f, indent=4)
        f.close()

