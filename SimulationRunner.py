import random
import logging

logger = logging.getLogger(__name__)

import networkx as nx
import matplotlib.pyplot as plt
import RoadNetwork
from Population import Population
from RoadNetwork import RoadNetwork
from Behavior import Behavior
from Observers import Observers
from Estimator import Estimator
from EstimatorBehavior import EstimatorBehavior
from EstimatorMeasurement import EstimatorMeasurement

class SimulationRunner:
    """The SimulationRunner does the following:
     Creates the RoadNetwork
     Creates the Population
     Creates the Observers
     Creates the Estimator
     Runs the simulation and the estimator"""
    
    def __init__(self, maxTimeSteps, runNumber, filePath):
        """SimulationRunner constructor."""
        # self.logger = logging.getLogger(__name__ + '.SimulationRunner')
        # self.logger.info("Initializing the simulation.")
        logger.info("Initializing the simulation")
        self.maxTimeSteps = maxTimeSteps
        self.pop = Population(100)
        self.roads = RoadNetwork()
        self.roads.generateSpatialNetwork(100, 4, 2, 3)
        self.roads.saveNetworkToFile(filePath + "roadNetworkSpatial_" + str(runNumber) + ".gml")

        self.obs = Observers()
        forceExit = False
        forceRendezvous = False
        moveSensors = True # If true, forceExit & forceRendezvous forced to false
        self.obs.generateSensorNodes(self.roads,8,forceExit,forceRendezvous,moveSensors)
        
        self.__setInitialLocations()
        self.__setRendezvousNodes()
        self.pop.savePopulationToFile(filePath + 'population_' + str(runNumber) + '.txt')

        self.estimator = Estimator()
        self.estimator.createEstimatorPopulation(self.pop,50)
        self.estimator.randomizeParticles(self.roads,0.2)
        self.estimator.saveEstimatorFile(filePath + 'estimator_population_' + str(runNumber) + '.txt')

        print("Max group ID:", self.pop.maxGID)
        print("Exit Nodes:", self.roads.exitNodeList)
        print("Rendezvous Nodes:", self.roads.rendezvousNodeList)

        groupsFile = open(filePath + 'groups_' + str(runNumber) + '.txt', "w")
        self.writeGroups(groupsFile)

        keylocs = open(filePath + 'key_locations_' + str(runNumber) + '.txt', "w")
        self.writeKeyLocations(keylocs)

        nodesFile = open(filePath + 'node_locations_' + str(runNumber) + '.txt', "w")
        self.writeNodeLocations(nodesFile)

        edgesFile = open(filePath + 'edge_locations_' + str(runNumber) + '.txt', "w")
        self.writeEdgeLocations(edgesFile)

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
    
    def __setRendezvousNodes(self):
        """Assign rendezvous node location for each group on the road network"""
        logger.info("Assigning random rendezvous node location to all groups.")
        num_nodes = len(self.roads.rendezvousNodeList)-1
        for gid in self.pop.groups.keys():
            num = random.randint(0,num_nodes)
            theirRendezvous = self.roads.rendezvousNodeList[num]
            for pid in self.pop.groups[gid]:
                self.pop.people[pid]['rendezvousNode'] = theirRendezvous
            
    def __numAgentsExited(self):
        e = 0
        exits = self.roads.exitNodeList
        for pid in self.pop.people.keys():
            if self.pop.people[pid]["location"] in exits:
                e += 1
        return e

    def __numPartExited(self):
        e = 0
        exits = self.roads.exitNodeList
        for agent in self.estimator.estimator_pop:
            for particle in agent:
                if particle["location"] in exits:
                    e += 1
        return e
    
    def writeNodeLocations(self, fileHandle):
        fileHandle.write("nodeId,x_coord,y_coord,[1 (normal) / 2 (exit) / 3 (rendezvous) ]\n")
        for node in self.roads.R.nodes():
            x = self.roads.R.nodes[node]['pos'][0]
            y = self.roads.R.nodes[node]['pos'][1]
            node_type = 1
            if node in self.roads.exitNodeList:
                node_type = 2
            elif node in self.roads.rendezvousNodeList:
                node_type = 3
            # elif node in self.obs.sensorNodeList:
            #     node_type = 4
            fileHandle.write(str(node) + "," + str(x) + "," + str(y) + "," + str(node_type))
            fileHandle.write("\n")

    def writeEdgeLocations(self, fileHandle):
        fileHandle.write("edge_source_x,edge_source_y,edge_target_x,edge_target_y\n")
        for edge in self.roads.R.edges():
            source_node = edge[0]
            source_x = self.roads.R.nodes[source_node]['pos'][0]
            source_y = self.roads.R.nodes[source_node]['pos'][1]
            target_node = edge[1]
            target_x = self.roads.R.nodes[target_node]['pos'][0]
            target_y = self.roads.R.nodes[target_node]['pos'][1]
            fileHandle.write(str(source_x) + "," + str(source_y) + "," + str(target_x) + "," + str(target_y))
            fileHandle.write("\n")

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

    def writeKeyLocations(self, fileHandle):
        # fileHandle.write("sensors")
        # for i in self.obs.sensorNodeList:
        #     fileHandle.write(","+str(i))
        # fileHandle.write("\n")

        fileHandle.write("exit_nodes")
        for i in self.roads.exitNodeList:
            fileHandle.write(","+str(i))
        fileHandle.write("\n")

        fileHandle.write("rendezvous_nodes")
        for i in self.roads.rendezvousNodeList:
            fileHandle.write(","+str(i))
        fileHandle.write("\n")

    def writeGroups(self, fileHandle):
        fileHandle.write("groupId,rendezvousNode,agentId,agentId,...\n")
        for gid in self.pop.groups.keys():
            write_rendez = True
            fileHandle.write(str(gid))
            for pid in self.pop.groups[gid]:
                if write_rendez:
                    fileHandle.write("," + str(self.pop.people[pid]['rendezvousNode']))
                    write_rendez = False
                fileHandle.write("," + str(pid))
            fileHandle.write("\n")

    def writeSensorObservations(self, fileHandle, timeStep):
        if (timeStep==0):
            fileHandle.write("time_step")
            for i in range(len(self.obs.sensorNodeList)):
                fileHandle.write(",loc_" + str(i))
                fileHandle.write(",sensor_" + str(i))
                fileHandle.write(",true_" + str(i))
            fileHandle.write("\n")
        
        fileHandle.write(str(timeStep))
        for i in range(len(self.obs.sensorNodeList)):
            fileHandle.write(","+str(self.obs.sensorNodeList[i]))
            fileHandle.write(","+str(self.obs.sensorCount[i]))
            fileHandle.write(","+str(self.obs.trueCount[i]))
        fileHandle.write("\n")

    def writeParticleLocations(self, fileHandle, timeStep):
        if (timeStep==0):
            fileHandle.write("time_step")
            fileHandle.write("\n")
            fileHandle.write("agent_X")
            for i in range(len(self.estimator.estimator_pop[0])):
                fileHandle.write(",particle_" + str(i+1))
            fileHandle.write("\n\n")
        
        fileHandle.write(str(timeStep))
        fileHandle.write("\n")
        for pid in sorted(self.pop.people.keys()):
            fileHandle.write(str(pid))
            for particle in self.estimator.estimator_pop[pid]:
                fileHandle.write("," + str(particle["location"]))
            fileHandle.write("\n")
        fileHandle.write("\n\n")

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
    
    def runSimulation(self, groupToTrack, spatialLocationOutputFile, \
        graphLocationOutputFile, behaviorOutputFile, observersOutputFile, \
        particlesOutputFile):
        """Update the simulation by one time step"""
        logger.info("Now starting the simulation.")
        showSimVis = False
        runEstimator = False
        showEstimatorVis = False
        """ User input for estimator and visuals """
        while(True):
            Input = raw_input('Show Visual? (T/F) :: ')
            if Input.lower() == 't':
                showSimVis = True
                break
            elif Input.lower() == 'f':
                showSimVis = False
                break
        while(True):
            Input = raw_input('Run Estimator? (T/F) :: ')
            if Input.lower() == 't':
                runEstimator = True
                while(True):
                    Input = raw_input('Show Estimator Visual? (T/F) :: ')
                    if Input.lower() == 't':
                        showEstimatorVis = True
                        break
                    elif Input.lower() == 'f':
                        showEstimatorVis = False
                        break
                break
            elif Input.lower() == 'f':
                runEstimator = False
                break

        if (showSimVis or (runEstimator and showEstimatorVis)):
            positions = nx.get_node_attributes(self.roads.R ,'pos')
            if not positions:
                positions = nx.spring_layout(self.roads.R)
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

        if observersOutputFile:
            obsFile = open(observersOutputFile, 'w')
            self.writeSensorObservations(obsFile, 0)

        if particlesOutputFile:
            partFile = open(particlesOutputFile, 'w')
            self.writeParticleLocations(partFile, 0)

        if (groupToTrack is not None):
            pidsToTrack = self.pop.groups[groupToTrack]
            agent_colors = []
            for pid in pidsToTrack:
                color = '#' + "%06x" % random.randint(0, 0xFFFFFF)
                agent_colors.append('red')

        DistMatrix = self.roads.buildDistMatrix()
        P_tr = 0 # initial transition probability for particles at rendezvous nodes
        Pb = 0.9
        for i in range(self.maxTimeSteps):
            Behavior.runOneStep(self.pop, self.roads)
            if runEstimator:
                """ Run estimator prediction and measurement steps """
                self.obs.noisyMeasurementModel(self.pop, self.roads, Pb)
                if (observersOutputFile):
                    self.writeSensorObservations(obsFile,i+1)

                P_tr = EstimatorBehavior.runPredictionStep(self.estimator, \
                    self.pop, self.roads, P_tr)
                EstimatorMeasurement.runMeasurementStep(self.estimator, \
                    self.pop, self.roads, self.obs, DistMatrix, Pb)
                if (particlesOutputFile):
                    self.writeParticleLocations(partFile, i+1)
            
            if (spatialLocationOutputFile):
                self.writeSpatialLocations(spatialLocFile, i+1)
            
            if (graphLocationOutputFile):
                self.writeGraphLocations(graphLocFile, i+1)
                
            if (behaviorOutputFile):
                self.writeBehaviors(behFile, i+1)
            
            print("Num agents exited:", self.__numAgentsExited())
            if runEstimator:
                print("Num particles exited:", self.__numPartExited())
            if showSimVis:
                plt.figure(1,figsize=(7,7))
                plt.clf()

                color_map = ['#99CCFF' for n in self.roads.R.nodes()]
                labels_dict = {}
                pid_count = 0
                if (groupToTrack is not None):
                    for pid in pidsToTrack:
                        #print("PID:", pid, "Properties:", self.pop.people[pid])
                        pidLoc = self.pop.people[pid]["location"]
                        color_map[pidLoc] = agent_colors[pid_count]
                        if (pidLoc in labels_dict):
                            labels_dict[pidLoc] += ", " + str(pid)
                        else:
                            labels_dict[pidLoc] = str(pid)
                        pid_count += 1
                for n in self.roads.exitNodeList:
                    color_map[n] = 'yellow'
                    #labels_dict[n] = str(n)
                for n in self.roads.rendezvousNodeList:
                    color_map[n] = 'purple'
                    #labels_dict[n] = str(n)

                nx.draw(self.roads.R, \
                    pos = positions, \
                    node_color = color_map, \
                    labels = labels_dict, \
                    font_size = 10, \
                    node_size = 200)
                textvar=plt.figtext(0.99, 0.01, "t = " + str(i), horizontalalignment='right')
                textvar=plt.figtext(0.5, 0.95, "Evacuation Simulation Actual Locations", horizontalalignment='center')
                
                if (not runEstimator) or (runEstimator and not showEstimatorVis):
                    plt.pause(0.1)

            if runEstimator and showEstimatorVis:
                plt.figure(2,figsize=(7,7))
                plt.clf()

                p_color_map = ['#99CCFF' for n in self.roads.R.nodes()]
                p_node_map = [50 for n in self.roads.R.nodes()]
                p_labels_dict = {}
                pid_count = 0
                for pid in pidsToTrack:
                    for particle in self.estimator.estimator_pop[pid]:
                        pidLoc = particle["location"]
                        if p_color_map[pidLoc] in agent_colors:
                            p_node_map[pidLoc] += 10
                        p_color_map[pidLoc] = agent_colors[pid_count]
                        count = 1 + (p_node_map[pidLoc]-50)/10
                        p_labels_dict[pidLoc] = str(count)
                    pid_count += 1
                for n in self.roads.exitNodeList:
                    p_color_map[n] = 'yellow'
                for n in self.roads.rendezvousNodeList:
                    p_color_map[n] = 'purple'
                for n in self.obs.sensorNodeList:
                    p_color_map[n] = 'green'

                nx.draw(self.roads.R, \
                    pos = positions, \
                    node_color = p_color_map, \
                    labels = p_labels_dict, \
                    font_size = 10, \
                    font_color = 'white', \
                    node_size = p_node_map)
                textvar=plt.figtext(0.99, 0.01, "t = " + str(i), horizontalalignment='right')
                textvar=plt.figtext(0.5, 0.95, "Estimated Position (Particle Filter)", horizontalalignment='center')
                plt.pause(0.01)
        
        if (showSimVis or (runEstimator and showEstimatorVis)):
            plt.show()
        logger.info("Simulation done.")
