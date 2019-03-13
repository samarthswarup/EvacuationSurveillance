import logging
from SimulationRunner import SimulationRunner

RUN_NUMBER = 0
FILE_PATH = 'data/'
#SHOW_SIM_VIS = True
#RUN_ESTIMATOR = False
#SHOW_ESTIMATOR_VIS = False # If RUN_ESTIMATOR = False, this does not matter
GROUP_TO_TRACK = 17 # If SHOW_VIS = False, this does not matter
SPATIAL_LOCATION_FILE = FILE_PATH + 'spatial_locations_' + str(RUN_NUMBER) + '.txt' # Make it None if you don't want agent spatial locations to be written to file
GRAPH_LOCATION_FILE = FILE_PATH + 'graph_locations_' + str(RUN_NUMBER) + '.txt' # Make it None if you don't want agent graph locations to be written to file
BEHAVIOR_FILE = FILE_PATH + 'behaviors_' + str(RUN_NUMBER) + '.txt' # Make it None if you don't want agent behaviors to be written to file
OBSERVERS_FILE = FILE_PATH + 'observers_' + str(RUN_NUMBER) + '.txt' # Make it None if you don't want sensor observations to be written to file
PARTICLES_FILE = FILE_PATH + 'particle_locations_' + str(RUN_NUMBER) + '.txt' # Make it None if you don't want particle graph locations to be written to file

logging.basicConfig(filename=FILE_PATH + 'testRun.log',format='%(name)s - %(levelname)s - %(message)s', level=logging.DEBUG)
logger = logging.getLogger('EvacuationSurveillance')
logger.info('Starting simulation.')

sr = SimulationRunner(20, RUN_NUMBER, FILE_PATH)
sr.runSimulation(GROUP_TO_TRACK, SPATIAL_LOCATION_FILE, GRAPH_LOCATION_FILE, BEHAVIOR_FILE, OBSERVERS_FILE, PARTICLES_FILE)