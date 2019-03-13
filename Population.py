import random
import logging

logger = logging.getLogger(__name__)

class Population:
    """The Population class does the following:
    Maintains a dictionary of all individuals, where PIDs map to a dictionary of attributes
        Age
        Gender
        Location (graph node this individual is currently at)
        GroupMembers (list of group member PIDs; might not be at the same location)
        Behavior (Evacuation or Rendezvous or eXited or Stay (for little kids))
    Maintains three dicts of individuals, one for each kind of behavior
    E.g., the evacuators dict maps PIDs of individuals who are evacuating to their current graph nodes"""
    
    def __init__(self, size):
        """Population constructor."""
        self.numPeople = 0
        self.numGroups = 0
        
        self.groupSizeDistribution = { 1:0.5*size, 2:0.1*size, 3:0.06*size, 4:0.03*size}
        # self.groupSizeDistribution = { 1:5000, 2:1000, 3:600, 4:300 }
        # groupSizeDistribution = { 1:2, 2:2, 3:2, 4:2 } # for debugging
        self.people = {} # PID: { age, gender, location, groupID, behavior }
        self.groups = {} # groupID: { set of PIDs belonging to the group }
        self.locations = {} # locationID: { set of PIDs at that location }
        
        self.maxPID = -1
        self.maxGID = -1
        self.createPopulation()
        
    def die(self):
        """Population destructor."""
        pass
        
    def __createIndividuals(self, n):
        """Create agents that are not members of any groups"""
        for i in range(int(n)):
            age = random.randrange(18, 91)
            gender = random.randrange(2)
            location = -1 # unassigned
            groupID = -1 # no group
            rendezvousNode = -1 #no rendezvous behavior
            behavior = 'E'
            self.maxPID += 1
            self.people[self.maxPID] = {"age": age, "gender": gender, "location": location, \
                                        "togetherWith": None, "groupID": groupID, \
                                        "rendezvousNode": rendezvousNode, "behavior": behavior}
            self.numPeople += 1
        logger.info("Created " + str(n) + " individuals.")
            
    def __createPairs(self, n):
        """Create pairs of agents"""
        for i in range(int(n)):
            ages = []
            ages.append(random.randrange(20, 89))
            ages.append(ages[0] + random.randrange(-2, 3))
            genders = [ 0, 1 ]
            self.maxGID += 1
            
            groupSet = set()
            togetherWith = set()
            for j in range(2):
                self.maxPID += 1
                self.people[self.maxPID] = {"age": ages[j], "gender": genders[j], "location": -1, \
                                            "togetherWith":togetherWith, "groupID": self.maxGID, \
                                            "rendezvousNode": -1, "behavior": 'R'}
                groupSet.add(self.maxPID)
                self.numPeople += 1
            self.numGroups += 1
            self.groups[self.maxGID] = groupSet
        logger.info("Created " + str(n) + " groups of size 2.")
                
    def __createSize3Groups(self, n):
        """Create groups of size 3"""
        for i in range(int(n)):
            ages = []
            ages.append(random.randrange(20, 89))
            ages.append(ages[0] + random.randrange(-2, 3))
            ages.append(ages[1] - 30 + random.randrange(5))
            if (ages[2] < 0):
                ages[2] = 0
            behaviors = [ 'R', 'R' ]
            if (ages[2] < 11):
                behaviors.append('S')
            else:
                behaviors.append('R')
            
            genders = [ 0, 1, random.randrange(2) ]
            self.maxGID += 1
            
            groupSet = set()
            togetherWith = set()
            for j in range(3):
                self.maxPID += 1
                self.people[self.maxPID] = {"age": ages[j], "gender": genders[j], "location": -1, \
                                            "togetherWith":togetherWith, "groupID": self.maxGID,  \
                                            "rendezvousNode": -1, "behavior": 'R'}
                groupSet.add(self.maxPID)
                self.numPeople += 1
            self.numGroups += 1
            self.groups[self.maxGID] = groupSet
        logger.info("Created " + str(n) + " groups of size 3.")
            
    def __createSize4Groups(self, n):
        """Create groups of size 4"""
        for i in range(int(n)):
            ages = []
            ages.append(random.randrange(20, 89))
            ages.append(ages[0] + random.randrange(-2, 3))
            ages.append(ages[1] - 30 + random.randrange(5))
            if (ages[2] < 0):
                ages[2] = 0
            ages.append(ages[2] + random.randrange(-3, 4))
            if (ages[3] < 0):
                ages[3] = 0
            behaviors = [ 'R', 'R' ]
            if (ages[2] < 11):
                behaviors.append('S')
            else:
                behaviors.append('R')
            if (ages[3] < 11):
                behaviors.append('S')
            else:
                behaviors.append('R')
            
            genders = [ 0, 1, random.randrange(2), random.randrange(2) ]
            self.maxGID += 1
            
            groupSet = set()
            togetherWith = set()
            for j in range(4):
                self.maxPID += 1
                self.people[self.maxPID] = {"age": ages[j], "gender": genders[j], "location": -1, \
                                            "togetherWith":togetherWith, "groupID": self.maxGID,  \
                                            "rendezvousNode": -1, "behavior": 'R'}
                groupSet.add(self.maxPID)
                self.numPeople += 1
            self.numGroups += 1
            self.groups[self.maxGID] = groupSet
        logger.info("Created " + str(n) + " groups of size 4.")
    
    def createPopulation(self):
        """Creates the population"""
        logger.info("Creating population...")
        self.__createIndividuals(self.groupSizeDistribution[1])
        self.__createPairs(self.groupSizeDistribution[2])
        self.__createSize3Groups(self.groupSizeDistribution[3])
        self.__createSize4Groups(self.groupSizeDistribution[4])
        
    def savePopulationToFile(self, filename):
        """Saves the entire population to the given file"""
        popFile = open(filename, "w")

        popFile.write("Number of people: " + str(self.numPeople)+"\n")
        popFile.write("Number of groups: " + str(self.numGroups)+"\n")
        popFile.write("Group size distribution: " + str(self.groupSizeDistribution)+"\n")
        popFile.write("\n")
        popFile.write("People: \n")
        for pid in self.people.keys():
            popFile.write(str(pid) + ": " + str(self.people[pid]).replace('set()', '{}')+"\n")
        popFile.write("\n")
        popFile.write("Groups:\n")
        for gid in self.groups.keys():
            popFile.write(str(gid) + ": " + str(self.groups[gid])+"\n")
        popFile.write("\n")
        popFile.write("Locations:\n")
        for loc in self.locations.keys():
            if (self.locations[loc] == set()):
                popFile.write(str(loc) + ": {}\n")
            else:
                popFile.write(str(loc) + ": " + str(self.locations[loc])+"\n")
        popFile.close()
        




















