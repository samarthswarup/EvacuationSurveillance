import random
import logging
import copy
import math
from Behavior import Behavior

logger = logging.getLogger(__name__)
DO_NOTHING_PROBABILITY = 0.1

class EstimatorBehavior:

    def __init__(self):
        """EstimatorBehavior constructor"""
        pass

    def die(self):
        """EstimatorBehavior destructor."""
        pass
    
    @classmethod
    def runPredictionStep(cls, estm, pop, roads, P_transition):
        """Update the state of each particle using prediction, one time step"""
        logger.debug("Running one prediction step for particles")

        updatedEstimator = []
        pid = 0
        for agent in estm.estimator_pop:
            updatedAgent = []
            ppid = 0
            for particle in agent:
                state = particle
                if (state["behavior"] == "E"):
                    newstate = Behavior.evacuation(pid, state, roads)
                    updatedAgent.append(newstate)
                elif (state["behavior"] == "R"):
                    newstate = Behavior.rendezvous(pid, state, roads, pop)
                    updatedAgent.append(newstate)
                elif (state["behavior"] == "X"):
                    newstate = Behavior.exited(pid, state, roads)
                    updatedAgent.append(newstate)
                elif (state["behavior"] == "S"):
                    newstate = Behavior.stay(pid, state, roads)
                    updatedAgent.append(newstate)
                elif (state["behavior"] == "W"):
                    [newstate, P_transition] = cls.estimator_wait(pid, state, roads, pop, P_transition)
                    updatedAgent.append(newstate)
                else:
                    print("Unknown behavior " + state["behavior"] + ", PID = " + str(pid))
                ppid += 1
            updatedEstimator.append(updatedAgent)
            pid += 1

        logger.debug("Updating estimator population.")
        estm.estimator_pop = updatedEstimator
        cls.updateHatVec(estm)

        return P_transition

    @classmethod   
    def estimator_wait(cls, p, st, r, pop, P_tr):
        """ Uses a probability to determine whether a given particle
        will continue to wait at a rendezvous node"""
        if (random.random() < DO_NOTHING_PROBABILITY):
            return [st, P_tr]

        P_0 = 0.10
        P_tr = (1-P_0)*P_tr + P_0

        if (random.random() <= P_tr):
            nextSt = copy.deepcopy(st)
            nextSt["behavior"] = "E"
            return [nextSt, P_tr]

        return [st, P_tr]

    @classmethod
    def updateHatVec(cls, estm):
        """ Updates estimator location and alpha vectors """
        curr_part = 0
        for agent in estm.estimator_pop:
            for particle in agent:
                estm.zHat[curr_part] = particle["location"]
                estm.alphaHat[curr_part] = particle["alpha"]
                estm.bHat[curr_part] = particle["behavior"]
                curr_part += 1