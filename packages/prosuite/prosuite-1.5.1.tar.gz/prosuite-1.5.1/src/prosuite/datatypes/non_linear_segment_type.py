class NonLinearSegmentType:
    Bezier: tuple = ("BEZIER", 0)
    CircularArc: tuple = ("CIRCULARARC", 1)
    EllipticArc: tuple = ("ELLIPTICARC", 2)

    type_list = [Bezier, CircularArc, EllipticArc]
