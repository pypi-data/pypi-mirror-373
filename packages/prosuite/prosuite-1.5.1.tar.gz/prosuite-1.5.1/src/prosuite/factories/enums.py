__author__ = "The ProSuite Authors"
__copyright__ = "Copyright 2021-2025, The ProSuite Authors"
__license__ = "MIT"
__version__ = "1.5.1.0"
__maintainer__ = "Dira GeoSystems"
__email__ = "programmers@dirageosystems.ch"
__date__  = "01.09.2025"
__status__ = "Production"


from datetime import datetime
from typing import List


# Enums referenced in conditions:

from enum import Enum
class PolylineUsage(Enum):
    AsIs = 0
    AsPolygonIfClosedElseAsPolyline = 1
    AsPolygonIfClosedElseIgnore = 2
    AsPolygonIfClosedElseReportIssue = 3

class NonLinearSegmentType(Enum):
    Bezier = 0
    CircularArc = 1
    EllipticArc = 2

class ShapeAllowed(Enum):
    NoValue = 0
    Cycles = 1
    Branches = 2
    CyclesAndBranches = 3
    InsideBranches = 4
    All = 7

class GroupErrorReporting(Enum):
    ReferToFirstPart = 1
    ShortestGaps = 2
    CombineParts = 4

class GeometryComponent(Enum):
    EntireGeometry = 0
    Boundary = 1
    Vertices = 2
    LineEndPoints = 3
    LineStartPoint = 4
    LineEndPoint = 5
    Centroid = 6
    LabelPoint = 7
    InteriorVertices = 8

class LineFieldValuesConstraint(Enum):
    NoConstraint = 0
    AllEqual = 1
    AllEqualOrValidPointExists = 2
    AtLeastTwoDistinctValuesIfValidPointExists = 3
    UniqueOrValidPointExists = 4

class PointFieldValuesConstraint(Enum):
    NoConstraint = 0
    AllEqualAndMatchAnyLineValue = 1
    AllEqualAndMatchMostFrequentLineValue = 2

class AllowedLineInteriorIntersections(Enum):
    NoValue = 0
    AtVertexOnBothLines = 1

class AllowedEndpointInteriorIntersections(Enum):
    All = 0
    Vertex = 1
    NoValue = 2

class AngleUnit(Enum):
    Radiant = 0
    Degree = 1

class LineMSource(Enum):
    Nearest = 0
    VertexPreferred = 1
    VertexRequired = 2

class MonotonicityDirection(Enum):
    Any = 0
    Increasing = 1
    Decreasing = 2

class InnerRingHandling(Enum):
    NoValue = 0
    IgnoreInnerRings = 1
    IgnoreHorizontalInnerRings = 2

class FieldListType(Enum):
    IgnoredFields = 0
    RelevantFields = 1

class BoundaryLoopErrorGeometry(Enum):
    LoopPolygon = 0
    LoopStartPoint = 1

class BoundaryLoopAreaRelation(Enum):
    IgnoreSmallerOrEqual = 0
    IgnoreLarger = 1

class OrphanErrorType(Enum):
    Both = 1
    OrphanedPoint = 2
    EndPointWithoutPoint = 3

class ExpectedCase(Enum):
    Any = 0
    AllUpper = 1
    AllLower = 2
    Mixed = 3
    NotAllUpper = 4
    NotAllLower = 5

class ExpectedStringDifference(Enum):
    Any = 0
    CaseSensitiveDifference = 1
    CaseInsensitiveDifference = 2

class UniqueStringsConstraint(Enum):
    NoValue = 0
    UniqueExactCase = 1
    UniqueAnyCase = 2

class esriFieldType(Enum):
    esriFieldTypeSmallInteger = 0
    esriFieldTypeInteger = 1
    esriFieldTypeSingle = 2
    esriFieldTypeDouble = 3
    esriFieldTypeString = 4
    esriFieldTypeDate = 5
    esriFieldTypeOID = 6
    esriFieldTypeGeometry = 7
    esriFieldTypeBlob = 8
    esriFieldTypeRaster = 9
    esriFieldTypeGUID = 10
    esriFieldTypeGlobalID = 11
    esriFieldTypeXML = 12
    esriFieldTypeBigInteger = 13

class ConnectionMode(Enum):
    EndpointOnEndpoint = 0
    EndpointOnVertex = 1
    VertexOnVertex = 2

class LineCapStyle(Enum):
    Round = 0
    Butt = 1

class ZComparisonMethod(Enum):
    BoundingBox = 0
    IntersectionPoints = 1

class JoinType(Enum):
    InnerJoin = 1
    LeftJoin = 2
    RightJoin = 3

class ShapeAllowed(Enum):
    NoValue = 0
    Cycles = 1
    Branches = 2
    CyclesAndBranches = 3
    InsideBranches = 4
    All = 7

class GroupErrorReporting(Enum):
    ReferToFirstPart = 1
    ShortestGaps = 2
    CombineParts = 4

class SearchOption(Enum):
    Tile = 0
    All = 1

class GeometryComponent(Enum):
    EntireGeometry = 0
    Boundary = 1
    Vertices = 2
    LineEndPoints = 3
    LineStartPoint = 4
    LineEndPoint = 5
    Centroid = 6
    LabelPoint = 7
    InteriorVertices = 8

class PolylineConversion(Enum):
    AsIs = 0
    AsPolygonIfClosedElseIgnore = 1

class PolygonPart(Enum):
    SinglePolygons = 0
    OuterRings = 1
    InnerRings = 2
    AllRings = 3

class SearchOption(Enum):
    Tile = 0
    All = 1

class SearchOption(Enum):
    Tile = 0
    All = 1

class JoinType(Enum):
    InnerJoin = 1
    LeftJoin = 2
    RightJoin = 3


