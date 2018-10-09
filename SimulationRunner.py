import random
import logging

logger = logging.getLogger(__name__)

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
        self.roads = RoadNetwork() 
        self.roads.generateSmallWorldNetwork(100, 5, 0.1, 5)
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
            
    def runSimulation(self):
        """Update the simulation by one time step"""
        logger.info("Now starting the simulation.")
        
        for i in range(self.maxTimeSteps):
            Behavior.runOneStep(self.pop, self.roads)
        logger.info("Simulation done.")

            
        
        
    