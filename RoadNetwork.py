import networkx as nx
import logging
import random
from sklearn.neighbors import NearestNeighbors
import numpy as np

logger = logging.getLogger(__name__)

class RoadNetwork:
    """The RoadNetwork class does the following:
    Maintains a graph representation of the road network
    Maintains a list of shortest paths from each node to the nearest exit node"""
    
    def __init__(self, filename=None):
        """RoadNetwork constructor."""
        # self.R = nx.Graph()
        self.exitNodeList = []
        self.shortestPaths = {}
        if (filename is not None):
            self.readNetwork(filename)
        
    def die(self):
        """RaodNetwork destructor."""
        pass
        
    def generateSpatialNetwork(self, n, k, e):
        """Generate a spatially-embedded road network by choosing n
        random points in a 100x100 square and connecting each point
        to its k nearest neighbors. e exit nodes are chosen randomly."""
        logger.info("Generating a spatial network with " + str(n) + " nodes, " + str(k) +\
                    " neighbors for each node, and " + str(e) + " exit nodes.")
        
        self.R = nx.Graph()
        for i in range(n):
            self.R.add_node(i)
            self.R.nodes[i]['pos'] = [random.random()*100, random.random()*100]

        coords = [self.R.nodes[n]['pos'] for n in self.R.nodes()]
        coords_np = np.array(coords)
        nbrs = NearestNeighbors(n_neighbors=k+1, algorithm='ball_tree').fit(coords_np)
        distances, indices = nbrs.kneighbors(coords_np)
        
        for nodelist in indices:
            for i in range(1,k+1):
                self.R.add_edge(nodelist[0], nodelist[i])
                
        self.__generateExitNodes(e)
        self.__calculateShortestPaths()

        
    def generateSmallWorldNetwork(self, n, k, p, e):
        """Generate a small world road network with the given parameters:
        n: number of nodes
        k: number of neighbors each node connects to
        p: probability of shortcut edges
        e: number of exit nodes"""
        logger.info("Generating small world network with " + str(n) + " nodes, " + str(2*k) + \
                         " neighbors for each node, and " + str(p) + " as the shortcut probability.")
        numNodes = n
        neighborhoodSize = k #This is the k parameter for the newman_watts_strogatz_graph generator
        pShortcut = p #This is the p parameter for the newman_watts_strogatz_graph generator
        self.R = nx.newman_watts_strogatz_graph(numNodes, neighborhoodSize, pShortcut)
        self.__generateExitNodes(e)
        self.__calculateShortestPaths()
        
    def saveNetworkToFile(self, filename):
        """Saves the road network to the given file"""
        # nx.write_edgelist(self.R, filename, data=True)
        nx.write_gml(self.R, filename)
        logger.info("Saved the road network to file " + filename)

        
    def __generateExitNodes(self, e):
        """Use reservoir sampling to choose e random nodes as exit nodes"""
        logger.info("Marking " + str(e) + " nodes as exit nodes using reservoir sampling.")
        numExitNodes = e
        nodeNum = 0
        for n in self.R.nodes():
            if (nodeNum < numExitNodes):
                self.exitNodeList.append(n)
            elif nodeNum >= numExitNodes and random.random() < numExitNodes/float(nodeNum+1):
                replace = random.randint(0,len(self.exitNodeList)-1)
                self.exitNodeList[replace] = n
            nodeNum += 1
        
        #Add the X label to exit nodes
        for n in self.exitNodeList:
            self.R.node[n]['exit'] = 'X'
            
        logger.debug("Exit nodes: " + str(self.exitNodeList))
            
    def __readNetwork(self, filename):
        """Read in a network from the given file"""
        self.R = nx.read_edgelist(filename)
        # self.__generateExitNodes() ##### Need a new method here to populate the exitNodeList, assuming exit nodes are marked in the given file
        self.__calculateShortestPaths()
        
    def __calculateShortestPaths(self):
        """Calculates the shortest path from each node to the nearest exit node"""
        # self.logger.info("Calculating shortest paths to exit nodes.")
        logger.info("Calculating shortest paths to exit nodes.")
        for n in self.R.nodes():
            shortestPathLength = nx.number_of_nodes(self.R)+1
            for x in self.exitNodeList:
                shortestPath = nx.shortest_path(self.R, n, x)
                if (len(shortestPath) < shortestPathLength):
                    shortestPathLength = len(shortestPath)
                    self.shortestPaths[n] = shortestPath
                
    def getShortestPath(self, a, b):
        return nx.shortest_path(self.R, a, b)
    
    def getNumberOfNodes(self):
        return nx.number_of_nodes(self.R)
        
