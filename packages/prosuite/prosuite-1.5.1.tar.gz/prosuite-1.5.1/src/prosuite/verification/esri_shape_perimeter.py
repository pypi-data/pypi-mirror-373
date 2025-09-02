class EsriShapePerimeter:
    """
    A polygon in the Esri shape buffer format.
    """
    def __init__(self, esri_shape: bytes):
        self.esri_shape = esri_shape
