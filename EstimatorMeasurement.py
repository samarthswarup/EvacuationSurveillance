import random
import logging
import numpy as np
import scipy.stats as stats

logger = logging.getLogger(__name__)

class EstimatorMeasurement:

    def __init__(self):
        """EstimatorMeasurement constructor"""
        pass

    def die(self):
        """EstimatorMeasurement destructor."""
        pass

    @classmethod
    def runMeasurementStep(cls, estm, pop, roads, obs, DistMatrix, Pb):
        """Update the state of each particle using measurement data, one time step"""
        logger.debug("Measurement Step")

        """ Initialize correspondance vectors """
        cMat = np.multiply(-1,np.ones((estm.numcVec,estm.numAgents)))
        zHatNext = np.multiply(-1,np.ones((estm.numcVec,estm.numAgents)))
        alphaHatNext = np.multiply(-1,np.ones((estm.numcVec,estm.numAgents)))
        """ Build probability table of likelihood of each particle being at any given node """
        q_flat_loc = cls.buildProbabilityTable(estm, obs, DistMatrix)

        [cMat, zHatNext, alphaHatNext] = cls.initializeCV(estm, obs, roads, cMat, zHatNext, alphaHatNext, q_flat_loc, Pb)
        [cMat, zHatNext, alphaHatNext] = cls.MHresample(estm, obs, cMat, zHatNext, alphaHatNext, q_flat_loc, Pb)

        estm.zHat = np.reshape(zHatNext,estm.numParts*estm.numAgents,1).astype(int).tolist()
        estm.alphaHat = np.reshape(alphaHatNext,estm.numParts*estm.numAgents,1).tolist()
        curr_part = 0
        for agent in estm.estimator_pop:
            for particle in agent:
                particle["location"] = estm.zHat[curr_part]
                particle["alpha"] = estm.alphaHat[curr_part]
                curr_part += 1

    @classmethod
    def buildProbabilityTable(cls, estm, obs, DistMatrix):
        """Build a table of likelihoods for each particle being at any possible location
        in the network. Output the table as q_flat_loc.  Each row is a particle, with all
        particles for a given agent clustered together (and followed by a cluster of
        particles for the next agent).  Each column represents a different location in the
        network."""
        rows = estm.numAgents*estm.numParts
        cols = estm.numNodes
        q_flat_loc = np.zeros((rows,cols))

        for node in range(estm.numNodes):
            DistVec = np.array(DistMatrix[:][node]) # Distance from all nodes to identified node
            agent_to_node = DistVec[np.array(estm.zHat)]
            norm_agent_to_node = np.multiply(agent_to_node, \
                np.array(estm.alphaHat))
            qEval = np.multiply(np.exp(np.multiply(-0.5, \
                np.power(norm_agent_to_node,2))), \
                np.power(np.array(estm.alphaHat),2))
            q_flat_loc[:,node] = qEval #likelihood of each particle viewed by each sensor

        return q_flat_loc

    @classmethod
    def initializeCV(cls, estm, obs, roads, cMat, zHatNext, alphaHatNext, q_flat_loc, Pb):
        """ Run initialization of correspondance vectors & populate data structures """
        for n in range(estm.numParts):
            """Determine order in which sensor observations will be matched to agents"""
            randAssocList = cls.associationOrder(estm, obs, Pb)
            """Now perform associations in randomized order specified by RANDASSOCLIST"""
            [assocAgentList, cVec, flat_Id] = \
                cls.associateAgents(estm, obs, q_flat_loc, randAssocList)
            """For each remaining unassociated agent, sample a particle"""
            [cVec, flat_Id] = cls.unassociatedPartSamp(estm, obs, roads, \
                q_flat_loc, assocAgentList, cVec, flat_Id)

            """Store data"""
            cMat[n,:] = cVec
            zHatNext[n,:] = np.array(estm.zHat)[flat_Id.astype(int)]
            alphaHatNext[n,:] = np.array(estm.alphaHat)[flat_Id.astype(int)]
            alphaHatNext[n,assocAgentList] = float(10)

        return [cMat, zHatNext, alphaHatNext]

    @classmethod
    def MHresample(cls, estm, obs, cMat, zHatNext, alphaHatNext, q_flat_loc, Pb):            
        """ Metropolis-Hastings resampling of correspondance vectors """
        reassocP = 0.99
        mistakenIdP = 1-reassocP
        numBurn = 20
        for n in range(estm.numcVec + numBurn):
            """Select a candidate correspondence vector to replace sample with 
            uniform probability across all correspondence vectors"""
            cvId = cls.randSamp(np.divide(np.arange(0,estm.numcVec),float(estm.numcVec)))
            cVecCand = cMat[cvId,:]
            zVecCand = zHatNext[cvId,:]
            alphaVecCand = alphaHatNext[cvId,:]

            """Perform proposal action: either reassociation or mistaken ID (per reassocP)"""
            if random.random() <= reassocP: #Implement reassociation
                [cVec,zVec,alphaVec] = cls.reassociate(estm, obs, cVecCand, \
                    zVecCand, alphaVecCand, q_flat_loc, Pb)
            else: #Implement mistaken identity
                [cVec,zVec,alphaVec] = cls.mistakenIdentity(estm, cVecCand, \
                    zVecCand, alphaVecCand);

            """Store data"""
            cMat[cvId,:] = cVec
            zHatNext[cvId,:] = zVec
            alphaHatNext[cvId,:] = alphaVec

        return [cMat, zHatNext, alphaHatNext]

    @classmethod
    def associationOrder(cls, estm, obs, Pb):
        """Determine order in which particles are matched to sensors."""
        randomizedCnt = np.zeros(len(obs.sensorCount))
        """Use a binary PDF to create an estimated number of agents at each sensor
        location (given that the measure may be inaccurate due to sensor noise)"""
        for i in range(len(obs.sensorCount)):
            meas = obs.sensorCount[i]
            estRng = np.arange(meas,2*meas+2)
            likelihoodRng = stats.norm.pdf(meas,estRng,Pb)
            index = int(estRng[cls.randSamp(likelihoodRng)])
            if (index >= len(estRng)):
                index = len(estRng) - 1
            randomizedCnt[i] = int(estRng[index])

        """Randomly permute the order of the sensor associations"""
        orderedAssocList = []
        for n in range(len(obs.sensorCount)):
            for i in range(int(randomizedCnt[n])):
                orderedAssocList.append(n+1)

        estm.numAssoc = int(np.sum(randomizedCnt))
        estm.numAssoc = min(estm.numAssoc,estm.numAgents)

        randAssocList = np.random.permutation(orderedAssocList)

        return randAssocList

    @classmethod
    def associateAgents(cls, estm, obs, q_flat_loc, randAssocList):
        """Begin to populate a correspondence vector cvec and an associated particle 
        designation vector flat_Id. Also output a list of all agent IDs for 
        associated agents"""

        """Extract likelihoods for sensor nodes"""
        q_sense = q_flat_loc[:,np.array(obs.sensorNodeList)]
        """ Initialize outputs """
        cVec = np.multiply(-1,np.ones(estm.numAgents))
        flat_Id = np.zeros(estm.numAgents)
        assocAgentList = np.zeros(estm.numAgents)
        assocPartVec_flat = np.zeros(estm.numAgents*estm.numParts)

        """Perform associations in order of randAssocList"""
        for n in range(estm.numAssoc):
            sensorId = randAssocList[n]-1
            """Extract particle index (flat) for particles not yet associated"""
            unassocFlatInd = np.where(assocPartVec_flat == 0)[0]
            q_cond = q_sense[unassocFlatInd,sensorId]
            unassocIndx = cls.randSamp(q_cond)
            sampledFlatIndx = unassocFlatInd[unassocIndx]
            sampledAgentIndx = estm.agentId[sampledFlatIndx]

            """Store data"""
            cVec[sampledAgentIndx] = sensorId
            flat_Id[sampledAgentIndx] = sampledFlatIndx
            assocAgentList[sampledAgentIndx] = 1;
            PartVecIndx = np.linspace(estm.numParts*(sampledAgentIndx-1)+1, \
                estm.numParts*sampledAgentIndx,estm.numParts)
            PartVecIndx = PartVecIndx.astype(int)
            assocPartVec_flat[PartVecIndx] = 1

        assocAgentList = np.where(assocAgentList == 1)[0]

        return [assocAgentList, cVec, flat_Id]

    @classmethod
    def unassociatedPartSamp(cls,estm,obs,roads,q_flat_loc,assocAgentList,cVec,flat_Id):
        """Complete the CVEC and the FLATIDVEC for all agents, by introducing random sampling
        to obtain a particle for all unassociated agents"""

        """Create list of unassigned agents"""
        unassignedAgentList = np.setdiff1d(np.arange(0,estm.numAgents), assocAgentList)
        numUnassocAgent = estm.numAgents - estm.numAssoc

        likelihoodByPart = np.sum(q_flat_loc,1) # Total likelihood by row (i.e. by particle)
        p_unAssoc = np.divide(q_flat_loc, \
            np.transpose(np.matlib.repmat(likelihoodByPart,estm.numNodes,1)))

        p_unAssoc[:,np.array(obs.sensorNodeList)] = 0 # Unassociated agents cannot be at sensor nodes

        """Cycle through all unassociated agents, randomly samplying a particle for each,
        where the PDF over particles is weighted by the probability that each particle
        falls at a non-sensor location"""
        for i in range(numUnassocAgent-1):
            ID = unassignedAgentList[i]
            agentRows = np.where(np.array(estm.agentId) == ID)[0]
            pMat = p_unAssoc[agentRows,:] # Rows are particles, columns are locations
            pVec = np.sum(pMat,1) # Sum over all locations to get total unassoc. prob. per particle
            randPart = cls.randSamp(pVec)
            flatInd = agentRows[randPart]
            """Store Data"""
            cVec[ID] = 0
            flat_Id[ID] = flatInd

        return [cVec, flat_Id]

    @classmethod
    def reassociate(cls,estm,obs,cVecCand,zVecCand,alphaVecCand,q_flat_loc,Pb):
        cVec = cVecCand
        zVec = zVecCand
        alphaVec = alphaVecCand

        """Exclude agents from consideration that cannot be "flipped".  Do this 
        by comparing the candidate count to measured count"""
        bins = np.arange(0,len(obs.sensorNodeList)+2)
        histCand = np.histogram(cVecCand,bins)[0]

        minAllowFlag = np.zeros(len(obs.sensorNodeList))
        for i in range(len(obs.sensorNodeList)):
            if (histCand[i+1] <= obs.sensorCount[i]):
                minAllowFlag[i] = 1

        cannotFlipSensorId = np.where(minAllowFlag == 1)[0]
        cannotFlipAgentId = np.array([])
        for i in range(len(cannotFlipSensorId)):
            sensorIdVec = np.where(cVecCand == cannotFlipSensorId[i])[0]
            cannotFlipAgentId = np.append(cannotFlipAgentId,sensorIdVec)
        allowedFlipAgentId = np.setdiff1d(np.arange(0,estm.numAgents),cannotFlipAgentId)

        numAllow = len(allowedFlipAgentId)
        if numAllow == 0:
            return [cVec,zVec,alphaVec] # Do not reassociate if all agents at sensor nodes

        """Entry (agent) within candidate vector that will be re-associated, given that
        the re-association will be a flip."""
        if (numAllow == 1):
            agId = allowedFlipAgentId[0]
        else:
            sampledAgAllowedId = cls.randSamp(np.arange(0,numAllow))
            agId = allowedFlipAgentId[sampledAgAllowedId]

        """Flip current association:  If not associated with a sensor, associate; if
        associated with a sensor, then disassociate."""
        currUnassocFlag = (cVecCand[agId] == 0)
        flipNodeVector = np.zeros(estm.numNodes)
        flipNodeVector[obs.sensorNodeList] = 1
        allowedFlipIndx = np.where(flipNodeVector==currUnassocFlag)[0]

        """As basis for new association, sample a particle and location"""
        agRows = np.where(np.array(estm.agentId) == agId)[0]
        qMat = q_flat_loc[agRows,:]
        qMatFlip = qMat[:,allowedFlipIndx]
        wRows = np.sum(qMatFlip,1)
        partInd = cls.randSamp(wRows)
        wCols = qMatFlip[partInd,:]
        nodeInd = allowedFlipIndx[cls.randSamp(wCols)]

        """New sensor index after reassociation"""
        sensorIndV = np.where(np.array(obs.sensorNodeList) == nodeInd)[0]
        """If node is not a sensor node, assign sensor ID to zero (unassociated)"""
        if len(sensorIndV) == 0:
            sensorInd = 0
        else:
            sensorInd = sensorIndV[0]
        sensorInd = int(sensorInd)
        oldSensorInd = int(cVecCand[agId])
        cVecProp = cVecCand
        cVecProp[agId] = sensorInd

        """Acceptance prob. ratio due to sensing"""
        bins = np.arange(0,len(obs.sensorNodeList)+2)
        histCand = np.histogram(cVecCand,bins)[0]
        histProp = np.histogram(cVecProp,bins)[0]
        histCand = histCand[np.arange(1,len(histCand))]
        histProp = histProp[np.arange(1,len(histProp))]
        pVecCandSense = stats.norm.pdf(obs.sensorCount,histCand,Pb)
        pVecPropSense = stats.norm.pdf(obs.sensorCount,histProp,Pb)
        flippedSensorInd = max(sensorInd,oldSensorInd)
        pRatioSense = pVecPropSense[flippedSensorInd]/pVecCandSense[flippedSensorInd] # some error on this line

        """Acceptance prob. ratio due to prior"""
        nonSenseNodeList = np.setdiff1d(np.arange(0,estm.numNodes), \
            np.array(obs.sensorNodeList))
        if oldSensorInd == 0:
            senseLocCand = nonSenseNodeList
            senseLocProp = obs.sensorNodeList[sensorInd]
        else:
            senseLocCand = obs.sensorNodeList[oldSensorInd]
            senseLocProp = nonSenseNodeList
        qPriorCandFlat = q_flat_loc[agRows,:]
        qPriorCandFlat = qPriorCandFlat[:,senseLocCand]
        qPriorCand = np.sum(np.sum(qPriorCandFlat))
        qPriorPropFlat = q_flat_loc[agRows,:]
        qPriorPropFlat = qPriorPropFlat[:,senseLocProp]
        qPriorProp = np.sum(np.sum(qPriorPropFlat))
        if qPriorProp < 1e-30:
            return [cVec,zVec,alphaVec]
        pRatioPrior = np.prod(np.divide(qPriorCand,qPriorProp))

        """Acceptance test"""
        pRatio = pRatioPrior*pRatioSense
        aRatio = min(1,pRatio)
        acceptFlag = (random.random() <= aRatio)

        """Modify output if proposal replaces original candidate"""
        if acceptFlag:
            cVec[agId] = sensorInd
            flatId = agRows[partInd]
            zVec[agId] = nodeInd
            alphaVec[agId] = estm.alphaHat[flatId]
            if sensorInd > 0:
                alphaVec[agId] = 10

        return [cVec,zVec,alphaVec]

    @classmethod
    def mistakenIdentity(cls,estm,cVecCand,zVecCand,alphaVecCand):
        """Randomly select two agents and switch their associated mean and 
        distance-scaling entries. Acceptance probability is one."""
        agId1 = cls.randSamp(np.divide(np.linspace(1,estm.numAgents,estm.numAgents),estm.numAgents))
        agId2 = cls.randSamp(np.divide(np.linspace(1,estm.numAgents,estm.numAgents),estm.numAgents))

        """Switch particles for two candidates"""
        cVec = cVecCand
        cVec[agId1] = cVecCand[agId2]
        cVec[agId2] = cVecCand[agId1]
        zVec = zVecCand
        zVec[agId1] = zVecCand[agId2]
        zVec[agId2] = zVecCand[agId1]
        alphaVec = alphaVecCand
        alphaVec[agId1] = alphaVecCand[agId2]
        alphaVec[agId2] = alphaVecCand[agId1]

        return [cVec,zVec,alphaVec]

    @classmethod
    def randSamp(cls, weightVec):
        weightVecSum = float(np.sum(weightVec))
        if weightVecSum < 1e-30:
            print('weight vector is empty')
            weightVecLength = len(weightVec)
            weightVecNorm = np.divide(np.ones(weightVecLength),float(weightVecLength))
        else:
            weightVecNorm = np.divide(weightVec,weightVecSum)
        cumWeight = np.cumsum(weightVecNorm)
        randVal = random.random()
        indices = np.where(cumWeight >= randVal)[0]

        return int(np.min(indices))