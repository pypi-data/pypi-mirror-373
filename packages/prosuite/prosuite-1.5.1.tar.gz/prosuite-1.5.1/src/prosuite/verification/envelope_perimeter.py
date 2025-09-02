class EnvelopePerimeter:
    """
    A spatial envelope defined by the bounding coordinates. The spatial reference must match the
    spatial reference of the datasets.
    """
    def __init__(self, x_min: float, y_min: float, x_max: float,  y_max: float):
        if x_min is None or x_max is None or y_min is None or y_max is None:
            raise Exception('Not all parameters are defined. Please define all envelope parameters')
        self.x_min = x_min
        self.x_max = x_max
        self.y_min = y_min
        self.y_max = y_max
