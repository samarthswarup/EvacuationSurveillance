import logging

logging.basicConfig(filename='testRun.log',format='%(name)s - %(levelname)s - %(message)s', level=logging.DEBUG)
logger = logging.getLogger('EvacuationSurveillance')

from SimulationRunner import SimulationRunner

logger.info('Starting simulation.')

sr = SimulationRunner(2)
sr.runSimulation()