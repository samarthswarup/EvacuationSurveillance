import logging

logging.basicConfig(filename='testRun.log',format='%(name)s - %(levelname)s - %(message)s', level=logging.DEBUG)
logger = logging.getLogger('EvacuationSurveillance')

from SimulationRunner import SimulationRunner

SHOW_VIS = True
GROUP_TO_TRACK = 17 # Make it None if SHOW_VIS = False
SPATIAL_LOCATION_FILE = 'spatial_locations.txt' # Make it None if you don't want agent spatial locations to be written to file
GRAPH_LOCATION_FILE = 'graph_locations.txt' # Make it None if you don't want agent graph locations to be written to file
BEHAVIOR_FILE = 'behaviors.txt' # Make it None if you don't want agent behaviors to be written to file

logger.info('Starting simulation.')

sr = SimulationRunner(20)
sr.runSimulation(SHOW_VIS, GROUP_TO_TRACK, SPATIAL_LOCATION_FILE, GRAPH_LOCATION_FILE, BEHAVIOR_FILE)