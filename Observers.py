import logging

logger = logging.getLogger(__name__)

class Observers:
    """The Observers class does the following:
    Provides a list of graph nodes that can be observed
    Provides methods that return information about the population at an observed node
    Provides a method for changing the list of graph nodes that can be observed"""
    
    def __init__(self):
        """Observers constructor."""
        pass
        
    def die(self):
        """Observers destructor."""
        pass