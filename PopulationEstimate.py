import logging

logger = logging.getLogger(__name__)

class PopulationEstimate:
    """The PopulationEstimate does the following:
    Maintains a dictionary of all individuals, where PIDs map to estimated locations (graph nodes)
    Provides methods for aggregating over the estimate, e.g., for determining the number of individuals at each graph node"""
    
    def __init__(self):
        """PopulationEstimate constructor."""
        pass
        
    def die(self):
        """PopulationEstimate destructor."""
        pass