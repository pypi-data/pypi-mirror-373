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
from prosuite.data_model import BaseDataset, TransformedDataset
from prosuite.quality import Parameter
from prosuite.factories.enums import *

class Transformers:

    @classmethod
    def tr_combined_filter_0(cls, feature_class_to_filter: BaseDataset, input_filters: List[BaseDataset], expression: str) -> TransformedDataset:
        """
        This transformer is an input feature filter. Input feature filters use a spatial restriction to filter the rows of the input feature class 'featureClassToFilter'.
        
        Creates a filtered feature class based on several other input feature filters that use the same 'featureClassToFilter' as this transformer. Other input feature filters are transformers with name 'TrOnly...'.
        """
        
        result = TransformedDataset("TrCombinedFilter(0)")
        result.parameters.append(Parameter("featureClassToFilter", feature_class_to_filter))
        if type(input_filters) == list:
            for element in input_filters:
                result.parameters.append(Parameter("inputFilters", element))
        elif input_filters is not None:
            result.parameters.append(Parameter("inputFilters", input_filters))
        result.parameters.append(Parameter("expression", expression))
        result.generate_name()
        return result

    @classmethod
    def tr_dissolve_0(cls, feature_class: BaseDataset, search: float = 0, neighbor_search_option: SearchOption = 0, attributes: List[str] = None, group_by: List[str] = None, constraint: str = None, create_multipart_features: bool = False) -> TransformedDataset:
        """
        Transforms line feature class 'featureClass' by dissolving connected features
        """
        
        result = TransformedDataset("TrDissolve(0)")
        result.parameters.append(Parameter("featureClass", feature_class))
        result.parameters.append(Parameter("Search", search))
        result.parameters.append(Parameter("NeighborSearchOption", neighbor_search_option))
        if type(attributes) == list:
            for element in attributes:
                result.parameters.append(Parameter("Attributes", element))
        elif attributes is not None:
            result.parameters.append(Parameter("Attributes", attributes))
        if type(group_by) == list:
            for element in group_by:
                result.parameters.append(Parameter("GroupBy", element))
        elif group_by is not None:
            result.parameters.append(Parameter("GroupBy", group_by))
        result.parameters.append(Parameter("Constraint", constraint))
        result.parameters.append(Parameter("CreateMultipartFeatures", create_multipart_features))
        result.generate_name()
        return result

    @classmethod
    def tr_footprint_0(cls, multipatch_class: BaseDataset, tolerance: float = -1, attributes: List[str] = None) -> TransformedDataset:
        """
        Transforms multipatches to polygons by taking their footprints
        """
        
        result = TransformedDataset("TrFootprint(0)")
        result.parameters.append(Parameter("multipatchClass", multipatch_class))
        result.parameters.append(Parameter("Tolerance", tolerance))
        if type(attributes) == list:
            for element in attributes:
                result.parameters.append(Parameter("Attributes", element))
        elif attributes is not None:
            result.parameters.append(Parameter("Attributes", attributes))
        result.generate_name()
        return result

    @classmethod
    def tr_geometry_to_points_0(cls, feature_class: BaseDataset, component: GeometryComponent, attributes: List[str] = None) -> TransformedDataset:
        """
        Transforms geometries to points. The transformed feature class has the attribute PartIndex and VertexIndex. These fields index from which polygon part the transformed polygon part was generated
        """
        
        result = TransformedDataset("TrGeometryToPoints(0)")
        result.parameters.append(Parameter("featureClass", feature_class))
        result.parameters.append(Parameter("component", component))
        if type(attributes) == list:
            for element in attributes:
                result.parameters.append(Parameter("Attributes", element))
        elif attributes is not None:
            result.parameters.append(Parameter("Attributes", attributes))
        result.generate_name()
        return result

    @classmethod
    def tr_intersect_0(cls, intersected: BaseDataset, intersecting: BaseDataset, result_dimension: int = -1) -> TransformedDataset:
        """
        Transforms features of 'intersected' by intersecting them with features from 'intersecting'.
        If ResultDimension is not specified, the result feature class has the same geometry dimension as the intersected feature class.
        When the result feature class matches the dimension of the intersected feature class, an IntersectionRatio attribute is added. This represents the ratio of the result geometry to the original intersected geometry:
        Polygons Features:  resultingFeature.Shape.Area \/ intersectedFeature.Shape.Area
        Line Features: resultingFeature.Shape.Length \/ intersectedFeature.Shape.Length
        (Mulit-)Point Features: resultingFeature.Shape.PointCount \/ intersectedFeature.Shape.PointCount
        """
        
        result = TransformedDataset("TrIntersect(0)")
        result.parameters.append(Parameter("intersected", intersected))
        result.parameters.append(Parameter("intersecting", intersecting))
        result.parameters.append(Parameter("ResultDimension", result_dimension))
        result.generate_name()
        return result

    @classmethod
    def tr_line_to_polygon_0(cls, closed_line_class: BaseDataset, polyline_usage: PolylineConversion = 1, attributes: List[str] = None) -> TransformedDataset:
        """
        Transforms closed lines of 'closedLineClass' to polygons
        """
        
        result = TransformedDataset("TrLineToPolygon(0)")
        result.parameters.append(Parameter("closedLineClass", closed_line_class))
        result.parameters.append(Parameter("PolylineUsage", polyline_usage))
        if type(attributes) == list:
            for element in attributes:
                result.parameters.append(Parameter("Attributes", element))
        elif attributes is not None:
            result.parameters.append(Parameter("Attributes", attributes))
        result.generate_name()
        return result

    @classmethod
    def tr_make_table_0(cls, base_table: BaseDataset, view_or_table_name: str) -> TransformedDataset:
        """
        Creates a table from an existing table or view in the database. This allows using tables that would otherwise not be usable because they have not been harvested as datasets in the data dictionary. Typical examples are:
        - Association tables in many-to-many relationship classes
        - Tables or views that are not part of the geodatabase.
        If the table is part of the geodatabase and registered as versioned it will be opened from the same version as the base table.
        """
        
        result = TransformedDataset("TrMakeTable(0)")
        result.parameters.append(Parameter("baseTable", base_table))
        result.parameters.append(Parameter("viewOrTableName", view_or_table_name))
        result.generate_name()
        return result

    @classmethod
    def tr_make_table_1(cls, base_table: BaseDataset, sql: str, object_id_field: str) -> TransformedDataset:
        """
        Creates a table from an SQL statement directly evaluated in the RDBMS. The same restrictions apply as for ArcGIS 'query layers'. For example, versioned data cannot be accessed, only the raw tables in the database including tables that are not registered as part of the geodatabase.
        """
        
        result = TransformedDataset("TrMakeTable(1)")
        result.parameters.append(Parameter("baseTable", base_table))
        result.parameters.append(Parameter("sql", sql))
        result.parameters.append(Parameter("objectIdField", object_id_field))
        result.generate_name()
        return result

    @classmethod
    def tr_multiline_to_line_0(cls, feature_class: BaseDataset, attributes: List[str] = None) -> TransformedDataset:
        """
        Transforms multipart lines to single lines. The transformed feature class has the attribute PartIndex. This field index from which line part the transformed line was generated
        """
        
        result = TransformedDataset("TrMultilineToLine(0)")
        result.parameters.append(Parameter("featureClass", feature_class))
        if type(attributes) == list:
            for element in attributes:
                result.parameters.append(Parameter("Attributes", element))
        elif attributes is not None:
            result.parameters.append(Parameter("Attributes", attributes))
        result.generate_name()
        return result

    @classmethod
    def tr_multipolygon_to_polygon_0(cls, feature_class: BaseDataset, transformed_parts: PolygonPart = 0, attributes: List[str] = None) -> TransformedDataset:
        """
        Transforms multipart polygons to single polygons. The transformed feature class has the attributes OuterRingIndex and InnerRingIndex. These fields index from which polygon part the transformed polygon was generated.
        The transformed feature class has also the attributes of 'featureClass', which can be accessed by 't0.<fieldName>'.
        """
        
        result = TransformedDataset("TrMultipolygonToPolygon(0)")
        result.parameters.append(Parameter("featureClass", feature_class))
        result.parameters.append(Parameter("TransformedParts", transformed_parts))
        if type(attributes) == list:
            for element in attributes:
                result.parameters.append(Parameter("Attributes", element))
        elif attributes is not None:
            result.parameters.append(Parameter("Attributes", attributes))
        result.generate_name()
        return result

    @classmethod
    def tr_only_contained_features_0(cls, feature_class_to_filter: BaseDataset, containing: BaseDataset, filtering_search_option: SearchOption = 0) -> TransformedDataset:
        """
        This transformer is an input feature filter. Input feature filters use a spatial restriction to filter the rows of the input feature class 'featureClassToFilter'.
        
        Creates a filtered feature class containing only the features that are contained within features from 'containing'. The resulting feature class has the same properties and attributes as 'featureClassToFilter'.
        """
        
        result = TransformedDataset("TrOnlyContainedFeatures(0)")
        result.parameters.append(Parameter("featureClassToFilter", feature_class_to_filter))
        result.parameters.append(Parameter("containing", containing))
        result.parameters.append(Parameter("FilteringSearchOption", filtering_search_option))
        result.generate_name()
        return result

    @classmethod
    def tr_only_disjoint_features_0(cls, feature_class_to_filter: BaseDataset, disjoint: BaseDataset, filtering_search_option: SearchOption = 0) -> TransformedDataset:
        """
        This transformer is an input feature filter. Input feature filters use a spatial restriction to filter the rows of the input feature class 'featureClassToFilter'.
        
        Creates a filtered feature class containing only the features that are disjoint from features from 'disjoint'. Features that intersect any feature from 'disjoint' are filtered out. The resulting feature class has the same properties and attributes as 'featureClassToFilter'.
        """
        
        result = TransformedDataset("TrOnlyDisjointFeatures(0)")
        result.parameters.append(Parameter("featureClassToFilter", feature_class_to_filter))
        result.parameters.append(Parameter("disjoint", disjoint))
        result.parameters.append(Parameter("FilteringSearchOption", filtering_search_option))
        result.generate_name()
        return result

    @classmethod
    def tr_only_intersecting_features_0(cls, feature_class_to_filter: BaseDataset, intersecting: BaseDataset, filtering_search_option: SearchOption = 0) -> TransformedDataset:
        """
        This transformer is an input feature filter. Input feature filters use a spatial restriction to filter the rows of the input feature class 'featureClassToFilter'.
        
        Creates a filtered feature class containing only the features that intersect features from 'intersecting'.  The resulting feature class has the same properties and attributes as 'featureClassToFilter'.
        """
        
        result = TransformedDataset("TrOnlyIntersectingFeatures(0)")
        result.parameters.append(Parameter("featureClassToFilter", feature_class_to_filter))
        result.parameters.append(Parameter("intersecting", intersecting))
        result.parameters.append(Parameter("FilteringSearchOption", filtering_search_option))
        result.generate_name()
        return result

    @classmethod
    def tr_polygon_to_line_0(cls, feature_class: BaseDataset, attributes: List[str] = None) -> TransformedDataset:
        """
        Transform polygon to line by taking the boundary of the polygons in 'featureClass'.
        The transformed feature class has also the attributes of 'featureClass', which can be accessed by 't0.<fieldName>'.
        """
        
        result = TransformedDataset("TrPolygonToLine(0)")
        result.parameters.append(Parameter("featureClass", feature_class))
        if type(attributes) == list:
            for element in attributes:
                result.parameters.append(Parameter("Attributes", element))
        elif attributes is not None:
            result.parameters.append(Parameter("Attributes", attributes))
        result.generate_name()
        return result

    @classmethod
    def tr_project_0(cls, feature_class: BaseDataset, target_spatial_reference_id: int, attributes: List[str] = None) -> TransformedDataset:
        """
        
        """
        
        result = TransformedDataset("TrProject(0)")
        result.parameters.append(Parameter("featureClass", feature_class))
        result.parameters.append(Parameter("targetSpatialReferenceId", target_spatial_reference_id))
        if type(attributes) == list:
            for element in attributes:
                result.parameters.append(Parameter("Attributes", element))
        elif attributes is not None:
            result.parameters.append(Parameter("Attributes", attributes))
        result.generate_name()
        return result

    @classmethod
    def tr_spatial_join_0(cls, t0: BaseDataset, t1: BaseDataset, constraint: str = None, outer_join: bool = False, neighbor_search_option: SearchOption = 0, grouped: bool = False, t0_attributes: List[str] = None, t1_attributes: List[str] = None, t1_calc_attributes: List[str] = None) -> TransformedDataset:
        """
        Transforms features of 't0' and features of 't1' to features, with shape of 't0' if they intersect.
        """
        
        result = TransformedDataset("TrSpatialJoin(0)")
        result.parameters.append(Parameter("t0", t0))
        result.parameters.append(Parameter("t1", t1))
        result.parameters.append(Parameter("Constraint", constraint))
        result.parameters.append(Parameter("OuterJoin", outer_join))
        result.parameters.append(Parameter("NeighborSearchOption", neighbor_search_option))
        result.parameters.append(Parameter("Grouped", grouped))
        if type(t0_attributes) == list:
            for element in t0_attributes:
                result.parameters.append(Parameter("T0Attributes", element))
        elif t0_attributes is not None:
            result.parameters.append(Parameter("T0Attributes", t0_attributes))
        if type(t1_attributes) == list:
            for element in t1_attributes:
                result.parameters.append(Parameter("T1Attributes", element))
        elif t1_attributes is not None:
            result.parameters.append(Parameter("T1Attributes", t1_attributes))
        if type(t1_calc_attributes) == list:
            for element in t1_calc_attributes:
                result.parameters.append(Parameter("T1CalcAttributes", element))
        elif t1_calc_attributes is not None:
            result.parameters.append(Parameter("T1CalcAttributes", t1_calc_attributes))
        result.generate_name()
        return result

    @classmethod
    def tr_table_append_0(cls, tables: List[BaseDataset]) -> TransformedDataset:
        """
        
        """
        
        result = TransformedDataset("TrTableAppend(0)")
        if type(tables) == list:
            for element in tables:
                result.parameters.append(Parameter("tables", element))
        elif tables is not None:
            result.parameters.append(Parameter("tables", tables))
        result.generate_name()
        return result

    @classmethod
    def tr_table_join_0(cls, t0: BaseDataset, t1: BaseDataset, relation_name: str, join_type: JoinType) -> TransformedDataset:
        """
        Transforms table 't0' and table 't1', which must be related by 'relationName', to a joined table
        """
        
        result = TransformedDataset("TrTableJoin(0)")
        result.parameters.append(Parameter("t0", t0))
        result.parameters.append(Parameter("t1", t1))
        result.parameters.append(Parameter("relationName", relation_name))
        result.parameters.append(Parameter("joinType", join_type))
        result.generate_name()
        return result

    @classmethod
    def tr_table_join_in_memory_0(cls, left_table: BaseDataset, right_table: BaseDataset, left_table_key: str, right_table_key: str, join_type: JoinType, many_to_many_table: BaseDataset = None, many_to_many_table_left_key: str = None, many_to_many_table_right_key: str = None) -> TransformedDataset:
        """
        Creates a joined table with the fields from 'leftTable' and 'rightTable'.
        """
        
        result = TransformedDataset("TrTableJoinInMemory(0)")
        result.parameters.append(Parameter("leftTable", left_table))
        result.parameters.append(Parameter("rightTable", right_table))
        result.parameters.append(Parameter("leftTableKey", left_table_key))
        result.parameters.append(Parameter("rightTableKey", right_table_key))
        result.parameters.append(Parameter("joinType", join_type))
        result.parameters.append(Parameter("ManyToManyTable", many_to_many_table))
        result.parameters.append(Parameter("ManyToManyTableLeftKey", many_to_many_table_left_key))
        result.parameters.append(Parameter("ManyToManyTableRightKey", many_to_many_table_right_key))
        result.generate_name()
        return result
