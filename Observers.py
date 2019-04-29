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
        self.movingSensors = False
        self.forceExit = False
        self.forceRendezvous = False
        
    def die(self):
        """Observers destructor."""
        pass

    def generateSensorNodes(self, roads, n, forceExit, forceRendezvous, moveSensors):
        # n is number of Sensor Nodes
        # m is max number of Nodes in Graph
        logger.debug("Generating a list of " + str(n) + " sensor nodes.")
        if moveSensors:
            self.movingSensors = True
        if forceExit:
            self.forceExit = True
        if forceRendezvous:
            self.forceRendezvous = True

        self.sensorNodeList = np.zeros(n).astype(int).tolist()
        nodeList = roads.R.nodes()
        start_rep = 0
        senseNum = 0

        if (self.forceExit):
            exitList = roads.exitNodeList
            start_rep += len(exitList)
            for i in exitList:
                self.sensorNodeList[senseNum] = i
                senseNum += 1
        if (self.forceRendezvous):
            rendezvousList = roads.rendezvousNodeList
            start_rep += len(rendezvousList)
            for i in rendezvousList:
                self.sensorNodeList[senseNum] = i
                senseNum += 1

        for i in range(senseNum,n):
            randNode = random.randint(0,len(nodeList)-1)
            while (randNode in self.sensorNodeList):
                randNode = random.randint(0,len(nodeList)-1)
            self.sensorNodeList[i] = randNode

        self.sensorCount = np.zeros(n).astype(int).tolist()
        self.trueCount = np.zeros(n).astype(int).tolist()

        logger.debug("Sensor nodes: " + str(self.sensorNodeList))
    
    def moveSensorNodes(self, roads):
        """ Randomly moves sensor nodes to a neighbouring node if mode is activated 
        Will not move forced exit or rendezvous nodes """
        start = 0
        if (self.forceExit):
            start = start + len(roads.exitNodeList)
        if (self.forceRendezvous):
            start = start + len(roads.rendezvousNodeList)
        for sensorIndx in range(start,len(self.sensorNodeList)):
            neighbors = roads.getNeighbourNodes(self.sensorNodeList[sensorIndx])
            nwNodeIndx = random.randint(0,len(neighbors)-1)
            self.sensorNodeList[sensorIndx] = neighbors[nwNodeIndx]

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