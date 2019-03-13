import logging
import random
import numpy as np
import matplotlib.pyplot as plt

logger = logging.getLogger(__name__)

class Observers:
    """The Observers class does the following:
    Provides a list of graph nodes that can be observed
    Provides methods that return information about the population at an observed node
    Provides a method for changing the list of graph nodes that can be observed"""
    
    def __init__(self):
        """Observers constructor."""
        self.sensorNodeList = []
        self.sensorCount = []
        self.trueCount = []
        
    def die(self):
        """Observers destructor."""
        pass

    def generateSensorNodes(self, roads, n, forceExit):
        # n is number of Sensor Nodes
        # m is max number of Nodes in Graph
        logger.debug("Generating a list of " + str(n) + " sensor nodes.")

        self.sensorNodeList = np.zeros(n).astype(int).tolist()
        nodeList = roads.R.nodes()
        nodeNum = 0
        senseNum = 0

        for i in nodeList:
            if (nodeNum < n):
                self.sensorNodeList[senseNum] = i
                senseNum += 1
            elif nodeNum >= n and random.random() < n/float(nodeNum+1):
                replace = random.randint(0,n-1)
                self.sensorNodeList[replace] = i
            nodeNum += 1

        if (forceExit):
            replace = 0
            exitList = roads.exitNodeList
            for i in exitList:
                if i in self.sensorNodeList:
                    continue
                while self.sensorNodeList[replace] in exitList:
                    replace += 1
                self.sensorNodeList[replace] = i
                replace += 1

        self.sensorCount = np.zeros(n).astype(int).tolist()
        self.trueCount = np.zeros(n).astype(int).tolist()

        logger.debug("Sensor nodes: " + str(self.sensorNodeList))
    
    def noisyMeasurementModel(self, population, Pb):
        """ Records number of agents at sensor node locations & adds noise to simulate a sensor """
        logger.debug("Measuring agents present at each sensor & applying" \
            " binomial distribution to account for noise")
        nodeNum = 0
        for loc in self.sensorNodeList:
            if (loc in population.locations):
                self.trueCount[nodeNum] = len(population.locations[loc])
            else:
                self.trueCount[nodeNum] = 0
            self.sensorCount[nodeNum] = np.random.binomial(self.trueCount[nodeNum],Pb)
            nodeNum += 1