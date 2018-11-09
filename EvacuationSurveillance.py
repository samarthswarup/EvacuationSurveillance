import logging

logging.basicConfig(filename='testRun.log',format='%(name)s - %(levelname)s - %(message)s', level=logging.DEBUG)
logger = logging.getLogger('EvacuationSurveillance')

from SimulationRunner import SimulationRunner

RUN_NUMBER = 0
SHOW_VIS = True
GROUP_TO_TRACK = 17 # Make it None if SHOW_VIS = False
SPATIAL_LOCATION_FILE = 'spatial_locations_' + str(RUN_NUMBER) + '.txt' # Make it None if you don't want agent spatial locations to be written to file
GRAPH_LOCATION_FILE = 'graph_locations_' + str(RUN_NUMBER) + '.txt' # Make it None if you don't want agent graph locations to be written to file
BEHAVIOR_FILE = 'behaviors_' + str(RUN_NUMBER) + '.txt' # Make it None if you don't want agent behaviors to be written to file

logger.info('Starting simulation.')

sr = SimulationRunner(20, RUN_NUMBER)
sr.runSimulation(SHOW_VIS, GROUP_TO_TRACK, SPATIAL_LOCATION_FILE, GRAPH_LOCATION_FILE, BEHAVIOR_FILE)