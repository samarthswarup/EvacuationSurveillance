import logging
import copy
import random

logger = logging.getLogger(__name__)
DO_NOTHING_PROBABILITY = 0.1

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
        for loc in pop.locations.keys():
            while pop.locations[loc]:
                pid = pop.locations[loc].pop()
                state = pop.people[pid]
                if (state["behavior"] == "E"):
                    newstate = cls.evacuation(pid, state, roads)
                    updatedPeople[pid] = newstate
                elif (state["behavior"] == "R"):
                    newstate = cls.rendezvous(pid, state, roads, pop)
                    updatedPeople[pid] = newstate
                elif (state["behavior"] == "X"):
                    newstate = cls.exited(pid, state, roads)
                    updatedPeople[pid] = newstate
                elif (state["behavior"] == "S"):
                    newstate = cls.stay(pid, state, roads)
                    updatedPeople[pid] = newstate
                elif (state["behavior"] == "W"):
                    newstate = cls.wait(pid, state, roads, pop)
                    updatedPeople[pid] = newstate
                else:
                    print("Unknown behavior " + state["behavior"] + ", PID = " + str(pid))
                
                #Get the group members at the same location and update their behavior
                #and location to match the current pid's location and behavior
                if (updatedPeople[pid]["togetherWith"]):
                    for member in updatedPeople[pid]["togetherWith"]:
                        newstate = copy.deepcopy(pop.people[member])
                        newstate["location"] = updatedPeople[pid]["location"]
                        newstate["behavior"] = updatedPeople[pid]["behavior"]
                        pop.locations[loc].remove(member)
                        updatedPeople[member] = newstate
                    
        
        # Update locations dictionary
        updatedLocations = {}
        for pid in updatedPeople.keys():
            loc = updatedPeople[pid]["location"]
            if (loc in updatedLocations):
                updatedLocations[loc].add(pid)
            else:
                updatedLocations[loc] = set()
                updatedLocations[loc].add(pid)
                
        pop.people = updatedPeople
        pop.locations = updatedLocations
                
    @classmethod
    def updateTogetherWith(cls, pop):
        """Update the togetherWith field for all agents, to keep track of agents who are in the same group
        and have met in this time step. These agents will move together henceforth"""
        logger.debug("Updating togetherWith for all agents")
        for pid in pop.people.keys():
            state = pop.people[pid]
            gid = state["groupID"]
            if gid != -1:
                if pop.people[pid]["togetherWith"]:
                    pop.people[pid]["togetherWith"].clear()
                else:
                    pop.people[pid]["togetherWith"] = set()
                groupMembers = pop.groups[gid]
                for member in groupMembers:
                    if (state["location"]==pop.people[member]["location"] and member != pid):
                        pop.people[pid]["togetherWith"].add(member)
                
    @classmethod
    def evacuation(cls, p, st, r):
        """Evacuation behavior implementation"""
        
        if (random.random() < DO_NOTHING_PROBABILITY):
            return st
        
        currentLoc = st["location"]
        if (currentLoc in r.exitNodeList):
            return st
        nextLoc = r.shortestExitPaths[currentLoc][1]
        nextSt = copy.deepcopy(st)
        nextSt["location"] = nextLoc
        return nextSt
    
    @classmethod
    def rendezvous(cls, p, st, r, pop):
        """Rendezvous behavior implementation"""

        if (random.random() < DO_NOTHING_PROBABILITY):
            return st

        nextSt = copy.deepcopy(st)

        rendezvousNode = st["rendezvousNode"]

        if (st["location"] == rendezvousNode):
            nextSt["behavior"] = "W"
            return nextSt
        
        shortestPath = r.getShortestPath(st["location"], rendezvousNode)
        nextSt["location"] = shortestPath[1]
        return nextSt
    
    @classmethod
    def exited(cls, p, st, r):
        """Exited behavior implementation"""
        return st
    
    @classmethod
    def stay(cls, p, st, r):
        """Stay method implementation"""
        return st
    
    @classmethod   
    def wait(cls, p, st, r, pop):
        if (random.random() < DO_NOTHING_PROBABILITY):
            return st

        nextSt = copy.deepcopy(st)
        gid = st["groupID"]
        
        #Get PIDs of all group members
        groupMembers = pop.groups[gid]
        
        #Find locations of all group members
        groupLocs = []
        for pid in groupMembers:
            groupLocs.append(pop.people[pid]["location"])
        
        groupSize = len(groupLocs)
        #Remove the ones at the same location as this person    
        try:
            groupLocs = [x for x in groupLocs if x != st["location"]]
        except ValueError:
            pass

        #If groupLocs is empty, all group members are at the same location
        #Change behavior to E
        if not groupLocs:
            nextSt["behavior"] = "E"
            return nextSt

        return st
        
            