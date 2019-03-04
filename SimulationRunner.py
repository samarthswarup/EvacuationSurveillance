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
    
    def __init__(self, maxTimeSteps, runNumber, filePath):
        """SimulationRunner constructor."""
        # self.logger = logging.getLogger(__name__ + '.SimulationRunner')
        # self.logger.info("Initializing the simulation.")
        logger.info("Initializing the simulation")
        self.pop = Population(2000)
        print("Max group ID:", self.pop.maxGID)
        self.roads = RoadNetwork()
        self.roads.generateSpatialNetwork(100, 4, 2)
        # self.roads.generateSmallWorldNetwork(100, 5, 0.1, 2)
        self.roads.saveNetworkToFile(filePath + "roadNetworkSpatial_" + str(runNumber) + ".gml")
        # self.roads.saveNetworkToFile("roadNetworkSmallWorld.gml")
        # self.behavior = Behavior()
        self.obs = Observers()
        
        self.est = Estimator()
        self.popEst = PopulationEstimate()
        
        self.maxTimeSteps = maxTimeSteps
        
        self.__setInitialLocations()
        self.pop.savePopulationToFile(filePath + 'population_' + str(runNumber) + '.txt')
        
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
    
    def writeSpatialLocations(self, fileHandle, timeStep):
        if (timeStep==0):
            fileHandle.write("time_step")
            for pid in sorted(self.pop.people.keys()):
                fileHandle.write(",x_" + str(pid) + ",y_" + str(pid))
            fileHandle.write("\n")
            
        fileHandle.write(str(timeStep))
        for pid in sorted(self.pop.people.keys()):
            x = self.roads.R.nodes[self.pop.people[pid]["location"]]["pos"][0]
            y = self.roads.R.nodes[self.pop.people[pid]["location"]]["pos"][1]
            fileHandle.write("," + str(x) + "," + str(y))
        fileHandle.write("\n")
    
    def writeGraphLocations(self, fileHandle, timeStep):
        if (timeStep==0):
            fileHandle.write("time_step")
            for pid in sorted(self.pop.people.keys()):
                fileHandle.write(",agent_" + str(pid))
            fileHandle.write("\n")
        
        fileHandle.write(str(timeStep))
        for pid in sorted(self.pop.people.keys()):
            fileHandle.write(","+str(self.pop.people[pid]["location"]))
        fileHandle.write("\n")
    
    def writeBehaviors(self, fileHandle, timeStep):
        if (timeStep==0):
            fileHandle.write("time_step")
            for pid in sorted(self.pop.people.keys()):
                fileHandle.write(",agent_" + str(pid))
            fileHandle.write("\n")
        
        fileHandle.write(str(timeStep))
        for pid in sorted(self.pop.people.keys()):
            fileHandle.write(","+self.pop.people[pid]["behavior"])
        fileHandle.write("\n")
        pass
    
    def runSimulation(self, showVisualization, groupToTrack, spatialLocationOutputFile, graphLocationOutputFile, behaviorOutputFile):
        """Update the simulation by one time step"""
        logger.info("Now starting the simulation.")
        
        if showVisualization:
            positions = nx.get_node_attributes(self.roads.R ,'pos')
            if not positions:
                positions = nx.spring_layout(self.roads.R)
            plt.figure(figsize=(7,7))
        textvar = None
        
        if spatialLocationOutputFile:
            spatialLocFile = open(spatialLocationOutputFile, "w")
            self.writeSpatialLocations(spatialLocFile, 0)
        
        if graphLocationOutputFile:
            graphLocFile = open(graphLocationOutputFile, "w")
            self.writeGraphLocations(graphLocFile, 0)
            
        if behaviorOutputFile:
            behFile = open(behaviorOutputFile, "w")
            self.writeBehaviors(behFile, 0)
        
        print("Num exited:", self.__numExited())
        for i in range(self.maxTimeSteps):
            Behavior.runOneStep(self.pop, self.roads)
            
            if (spatialLocationOutputFile):
                self.writeSpatialLocations(spatialLocFile, i+1)
            
            if (graphLocationOutputFile):
                self.writeGraphLocations(graphLocFile, i+1)
                
            if (behaviorOutputFile):
                self.writeBehaviors(behFile, i+1)
            
            print("Num exited:", self.__numExited())
            if showVisualization:
                color_map = ['blue' for n in self.roads.R.nodes()]
                labels_dict = {}
                if (groupToTrack is not None):
                    pidsToTrack = self.pop.groups[groupToTrack]
                    for pid in pidsToTrack:
                        # print("PID:", pid, "Properties:", self.pop.people[pid])
                        pidLoc = self.pop.people[pid]["location"]
                        color_map[pidLoc] = 'red'
                        if (pidLoc in labels_dict):
                            labels_dict[pidLoc] += ","+str(pid)
                        else:
                            labels_dict[pidLoc] = str(pid)
                for n in self.roads.exitNodeList:
                    color_map[n] = 'yellow'

                plt.clf()
                nx.draw(self.roads.R, pos = positions, node_color = color_map, labels = labels_dict)
                textvar=plt.figtext(0.99, 0.01, "t="+str(i), horizontalalignment='right')
                plt.pause(1)
                # input("Press Enter to continue...")
        
        if (showVisualization):
            plt.show()
        logger.info("Simulation done.")

            
        
        
    