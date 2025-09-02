class WkbPerimeter:
    """
    A polygon in the OGC well-known-binary format. For example, in ArcPy the geometry's WKB
    property could be used to acquire this format.
    """
    def __init__(self, wkb: bytes):
        self.wkb = wkb
