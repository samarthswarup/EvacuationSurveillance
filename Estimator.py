import random
import logging
import copy
from Behavior import Behavior

logger = logging.getLogger(__name__)
DO_NOTHING_PROBABILITY = 0.1

class Estimator:
    """The Estimator class does the following:
    Maintains a dictionary of all individuals, where PIDs map to a dictionary of attributes
        Age
        Gender
        Particles: List of n particles representing different state values for each agent
        Alpha: List of n corresponding inverse-length scale, initialized to 1/5
        GroupMembers (list of group member PIDs; might not be at the same location)
        Behavior (Evacuation or Rendezvous or eXited or Stay (for little kids))"""

    def __init__(self):
        self.estimator_pop = []

        self.agentId = []
        self.zHat = []
        self.alphaHat = []

        self.numAgents = -1
        self.numParts = -1
        self.numcVec = -1
        self.numAssoc = -1
        self.numNodes = -1

    def die(self):
        """Estimator destructor."""
        pass

    def createEstimatorPopulation(self, pop, n):
        # n is number of particles to create for each agent
        self.numAgents = 0
        self.numParts = n
        self.numcVec = n
        for pid in pop.people.keys():
            particles = []
            for i in range(n):
                self.agentId.append(pid)
                particles.append(copy.deepcopy(pop.people[pid]))
            self.estimator_pop.append(particles)
            self.numAgents += 1

    def randomizeParticles(self, roads, m):
        # m is initial alpha param (inverse-length scale))

        locs = list(roads.R.nodes())
        self.numNodes = len(roads.R.nodes)
        numLocs = len(locs)

        for agent in self.estimator_pop:
            for particle in agent:
                r = random.randrange(numLocs)
                particle["location"] = r
                particle["alpha"] = m
                self.zHat.append(r)
                self.alphaHat.append(m)

    def saveEstimatorFile(self, filename):
        """Saves the entire estimator population to the given file"""
        estimatorFile = open(filename, "w")

        estimatorFile.write("People: \n")
        pid = 0
        for agent in self.estimator_pop:
            estimatorFile.write(str(pid) + ": {" + "\n")
            estimatorFile.write("\tAge: " + str(agent[1]["age"]) + "\n")
            estimatorFile.write("\tGender: " + str(agent[1]["gender"]) + "\n")
            estimatorFile.write("\tGroupID: " + str(agent[1]["groupID"]) + "\n")
            estimatorFile.write("\tRendezvousNode: " + str(agent[1]["rendezvousNode"]) + "\n")
            estimatorFile.write("\tBehavior: " + str(agent[1]["behavior"]) + "\n")
            estimatorFile.write("]\n\tParticle Locations:\n\t[ ")
            for particle in agent:
                estimatorFile.write(str(particle["location"]) + ", ")
            estimatorFile.write("]\n\tAssociated Alphas:\n\t[ ")
            for particle in agent:
                estimatorFile.write(str(particle["alpha"]) + ", ")
            estimatorFile.write("]\n\n")
            pid += 1

        estimatorFile.close()