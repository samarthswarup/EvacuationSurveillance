import random
import logging

logger = logging.getLogger(__name__)

import networkx as nx
import matplotlib.pyplot as plt
import RoadNetwork
from Population import Population
from RoadNetwork import RoadNetwork
from Behavior import Behavior
from PopulationEstimate import PopulationEstimate
from Estimator import Estimator
from Observers import Observers

class SimulationRunner:
    """The SimulationRunner does the following:
     Creates the RoadNetwork
     Creates the Population
     Creates the Observers
     Creates the Estimator
     Runs the simulation and the Estimator"""
    
    def __init__(self, maxTimeSteps):
        """SimulationRunner constructor."""
        # self.logger = logging.getLogger(__name__ + '.SimulationRunner')
        # self.logger.info("Initializing the simulation.")
        logger.info("Initializing the simulation")
        self.pop = Population(100)
        print("Max group ID:", self.pop.maxGID)
        self.roads = RoadNetwork() 
        self.roads.generateSmallWorldNetwork(100, 5, 0.1, 2)
        self.roads.saveNetworkToFile("roadNetwork.net")
        # self.behavior = Behavior()
        self.obs = Observers()
        
        self.est = Estimator()
        self.popEst = PopulationEstimate()
        
        self.maxTimeSteps = maxTimeSteps
        
        self.__setInitialLocations()
        
    def die(self):
        """SimulationRunner destructor."""
        pass
    
    def __setInitialLocations(self):
        """Assign initial location for each agent on the road network"""
        logger.info("Assigning random initial locations to all agents.")
        locs = list(self.roads.R.nodes())
        for loc in locs:
            self.pop.locations[loc] = set()
        numLocs = len(locs)
        for pid in self.pop.people.keys():
            r = random.randrange(numLocs)
            self.pop.people[pid]["location"] = locs[r]
            self.pop.locations[locs[r]].add(pid)
            
            
    def __numExited(self):
        e = 0
        for loc in self.roads.exitNodeList:
            if (loc in self.pop.locations):
                e += len(self.pop.locations[loc])
        return e
    
    def runSimulation(self, showVisualization, groupToTrack):
        """Update the simulation by one time step"""
        logger.info("Now starting the simulation.")
        
        if showVisualization:
            positions = nx.spring_layout(self.roads.R)
        textvar = None
        
        print("Num exited:", self.__numExited())
        for i in range(self.maxTimeSteps):
            Behavior.runOneStep(self.pop, self.roads)
            print("Num exited:", self.__numExited())
            if showVisualization:
                color_map = ['blue' for n in self.roads.R.nodes()]
                labels_dict = {}
                pidsToTrack = self.pop.groups[groupToTrack]
                for pid in pidsToTrack:
                    pidLoc = self.pop.people[pid]["location"]
                    color_map[pidLoc] = 'red'
                    if (pidLoc in labels_dict):
                        labels_dict[pidLoc] += ","+str(pid)
                    else:
                        labels_dict[pidLoc] = str(pid)
                for n in self.roads.exitNodeList:
                    color_map[n] = 'yellow'

                plt.figure(figsize=(7,7))
                nx.draw(self.roads.R, pos = positions, node_color = color_map, labels = labels_dict)
                if textvar:
                    textvar.remove()
                textvar=plt.figtext(0.99, 0.01, "t="+str(i), horizontalalignment='right')
                plt.pause(1)
                input("Press Enter to continue...")
        
        if (showVisualization):
            plt.show()
        logger.info("Simulation done.")

            
        
        
    