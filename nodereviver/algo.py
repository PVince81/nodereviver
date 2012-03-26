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
import model

class PathFinder:
    '''
    A* path finding algorithm
    '''
    def __init__(self):
        self.sourceNode = None
        self.goal = None

    def h(self, source, target):
        return abs(source.pos[0] - target.pos[0] + source.pos[1] - target.pos[1])

    def lowest(self, list, scores):
        min = 999999999999
        curNode = None
        for node in list:
            score = scores[node] 
            if score < min:
                curNode = node
                min = score
        return curNode

    def findShortestPath(self, start, goal):
        '''
        Finds the shortest path from sourceNode to goal.
        @return: array of node's starting edges to follow to reach the target
        '''
        # THANKS WIKIPEDIA!
        closedset = set()
        openset = set([start])
        self.came_from = {}

        g_score = {}
        h_score = {}
        f_score = {}
        # Cost from start along best known path.
        g_score[start] = 0
        h_score[start] = self.h(start, goal)
        # // Estimated total cost from start to goal through y.
        f_score[start] = g_score[start] + h_score[start]

        while len(openset) > 0:
            # the node in openset having the lowest f_score[] value
            current = self.lowest(openset, f_score)
            if current == goal:
                return self.reconstruct_path(start, goal)

            openset.remove(current)
            closedset.add(current)
            for edge in current.getOutgoingEdges():
                neighbor = edge.getOther(current)
                if neighbor in closedset:
                    continue
                tentative_g_score = g_score[current] + edge.length
     
                if neighbor not in openset:
                    openset.add(neighbor)
                    h_score[neighbor] = self.h(neighbor, goal)
                    tentative_is_better = True
                elif tentative_g_score < g_score[neighbor]:
                    tentative_is_better = True
                else:
                    tentative_is_better = False

                if tentative_is_better:
                    self.came_from[neighbor] = edge
                    g_score[neighbor] = tentative_g_score
                    f_score[neighbor] = g_score[neighbor] + h_score[neighbor]

        return None

    def reconstruct_path(self, sourceNode, node):
        path = []
        while self.came_from.has_key(node):
            edge = self.came_from[node]
            path.append(edge)
            node = edge.getOther(node)
        path.reverse()
        
        # remove joint nodes
        finalEdges = []
        node = sourceNode
        for edge in path:
            if node.type != model.Node.JOINT:
                finalEdges.append(edge)
            node = edge.getOther(node)

        return finalEdges

    def getPathNodes(self, sourceNode, edges):
        nodes = [sourceNode]
        node = sourceNode
        for edge in edges:
            nodes.append(node)
            print node
            print edge
            node = edge.getOther(node)
        nodes.append(node)
        return nodes

    def printPath(self, sourceNode, edges):
        node = sourceNode
        for edge in edges:
            print node
            print edge
            node = edge.getOther(node)
        print node
