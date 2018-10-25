import logging

logger = logging.getLogger(__name__)

class Behavior:
    """The Behavior class does the following:
    Provides a method for updating the locations of all the individuals at a given node
    Provides a method for updating the behavior of a given individual"""
    
    def __init__(self):
        """Behavior constructor"""
        pass
        
    def die(self):
        """Behavior destructor"""
        pass
    
    @classmethod
    def runOneStep(cls, pop, roads):
        """Update the state of each person, location by location, by one time step"""
        logger.debug("Updating one step of the simulation")
        # Update who is traveling together with whom (i.e., which agents have rendezvoused)
        cls.updateTogetherWith(pop)
        updatedPeople = {}
        updatedLocations = {}
        for loc in pop.locations.keys():
            while locations[loc]:
                pid = locations[loc].pop()
                state = pop.people[pid]
                if (state["behavior"] == "E"):
                    newstate = cls.evacuation(pid, state, roads)
                    updatedPeople[pid] = newstate
                elif (state["behavior"] == "R"):
                    newstate = cls.rendezvous(pid, state, roads, pop)
                    pop.people[pid] = newstate
                elif (state["behavior"] == "X"):
                    newstate = cls.exited(pid, state, roads)
                    pop.people[pid] = newstate
                elif (state["behavior"] == "S"):
                    newstate = cls.stay(pid, state, roads)
                    pop.people[pid] = newstate
                else:
                    print("Unknown behavior " + state["behavior"] + ", PID = " + str(pid))
        # Update locations dictionary
                
    @classmethod
    def updateTogetherWith(cls, pop):
        """Update the togetherWith field for all agents, to keep track of agents who are in the same group
        and have met in this time step. These agents will move together henceforth"""
        logger.debug("Updating togetherWith for all agents")
        for pid in pop.people.keys():
            state = pop.people[pid]
            groupMembers = pop.groups[state["groupID"]]
            for member in groupMembers:
                if (state["location"]==pop.people[member]["location"]):
                    state["togetherWith"].add(member)
                
    @classmethod
    def evacuation(cls, p, st, r):
        """Evacuation behavior implementation"""
        currentLoc = st["location"]
        if (currentLoc in r.exitNodeList):
            return st
        nextLoc = r.shortestPaths[currentLoc][1]
        st["location"] = nextLoc
        return st
    
    @classmethod
    def rendezvous(cls, p, st, r, pop):
        """Rendezvous behavior implementation"""
        if (st["location"] in r.exitNodeList):
            return st

        gid = st["groupID"]
        
        #Get PIDs of all group members
        groupMembers = pop.groups[gid]
        
        #Find locations of all group members
        groupLocs = []
        for pid in groupMembers:
            groupLocs.append(pop.people[pid]["location"])
        
        #Remove the ones at the same location as this person    
        try:
            groupLocs = [x for x in groupLocs if x != st["location"]]
        except ValueError:
            pass
        
        #If groupLocs is empty, all group members are at the same location
        #Change behavior to E
        if not groupLocs:
            st["behavior"] = "E"
            return st
        
        #Otherwise, move one step closer to the closest group member at
        #a different location
        closestLoc = -1
        shortestDist = r.getNumberOfNodes()+1
        for loc in groupLocs:
            path = r.getShortestPath(st["location"], loc)
            if (len(path) < shortestDist):
                shortestDist = len(path)
                closestLoc = loc
        
        shortestPath = r.getShortestPath(st["location"], closestLoc)
        st["location"] = shortestPath[1]
        return st
    
    @classmethod
    def exited(cls, p, st, r):
        """Exited behavior implementation"""
        return st
    
    @classmethod
    def stay(cls, p, st, r):
        """Stay method implementation"""
        return st
        
        
            