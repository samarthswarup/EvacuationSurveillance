import logging

logging.basicConfig(filename='testRun.log',format='%(name)s - %(levelname)s - %(message)s', level=logging.DEBUG)
logger = logging.getLogger('EvacuationSurveillance')

from SimulationRunner import SimulationRunner

SHOW_VIS = True
GROUP_TO_TRACK = 17 # Make it None if SHOW_VIS = False

logger.info('Starting simulation.')

sr = SimulationRunner(20)
sr.runSimulation(SHOW_VIS, GROUP_TO_TRACK)