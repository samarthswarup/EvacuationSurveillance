import logging

logger = logging.getLogger(__name__)

class Estimator:
    """The Estimator does the following:
    Creates the PopulationEstimate
    Provides hooks where methods for estimation can be plugged in"""
    
    def __init__(self):
        """Estimator constructor."""
        pass
        
    def die(self):
        """Estimator destructor."""
        pass