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
from prosuite.quality import Parameter, Condition
from prosuite.data_model import BaseDataset
from prosuite.factories.enums import *

class Conditions:

    @classmethod
    def qa3d_constant_z_0(cls, feature_class: BaseDataset, tolerance: float) -> Condition:
        """
        Finds all points in 'featureClass' with a Z range larger than 'tolerance'
        """
        
        result = Condition("Qa3dConstantZ(0)")
        result.parameters.append(Parameter("featureClass", feature_class))
        result.parameters.append(Parameter("tolerance", tolerance))
        result.generate_name()
        return result

    @classmethod
    def qa_border_sense_0(cls, polyline_class: BaseDataset, clockwise: bool) -> Condition:
        """
        Finds features that are not involved in valid rings:
        Checks if features in 'polylineClass' build rings and if the features in a ring are directed in clockwise \/ counterclockwise direction
        """
        
        result = Condition("QaBorderSense(0)")
        result.parameters.append(Parameter("polylineClass", polyline_class))
        result.parameters.append(Parameter("clockwise", clockwise))
        result.generate_name()
        return result

    @classmethod
    def qa_border_sense_1(cls, polyline_classes: List[BaseDataset], clockwise: bool) -> Condition:
        """
        Finds features that are not involved in valid rings:
        Checks if features in 'polylineClasses' build rings and if the features in a ring are directed in clockwise \/ counterclockwise direction
        
        Remark: The feature classes in 'polylineClasses' must have the same spatial reference.
        """
        
        result = Condition("QaBorderSense(1)")
        if type(polyline_classes) == list:
            for element in polyline_classes:
                result.parameters.append(Parameter("polylineClasses", element))
        elif polyline_classes is not None:
            result.parameters.append(Parameter("polylineClasses", polyline_classes))
        result.parameters.append(Parameter("clockwise", clockwise))
        result.generate_name()
        return result

    @classmethod
    def qa_centroids_0(cls, polyline_class: BaseDataset, point_class: BaseDataset) -> Condition:
        """
        Finds errors in point-line-polygon topology:
        Checks if there is exactly one point from 'pointClass' within each polygon built by the features of 'polylineClass'
        
        Remark: The feature classes in 'polylineClass' and 'pointClass' must have the same spatial reference.
        The features of 'polylineClass' are not checked for intersections. Use QaLineIntersect to check
        """
        
        result = Condition("QaCentroids(0)")
        result.parameters.append(Parameter("polylineClass", polyline_class))
        result.parameters.append(Parameter("pointClass", point_class))
        result.generate_name()
        return result

    @classmethod
    def qa_centroids_1(cls, polyline_class: BaseDataset, point_class: BaseDataset, constraint: str) -> Condition:
        """
        Finds errors in point-line-polygon topology:
        Checks if there is exactly one point from 'pointClass' within each polygon built by the features of 'polylineClass'
        
        Remark: The feature classes in 'polylineClass' and 'pointClass' must have the same spatial reference.
        The features of 'polylineClass' are not checked for intersections. Use QaLineIntersect to check
        """
        
        result = Condition("QaCentroids(1)")
        result.parameters.append(Parameter("polylineClass", polyline_class))
        result.parameters.append(Parameter("pointClass", point_class))
        result.parameters.append(Parameter("constraint", constraint))
        result.generate_name()
        return result

    @classmethod
    def qa_centroids_2(cls, polyline_classes: List[BaseDataset], point_classes: List[BaseDataset]) -> Condition:
        """
        Finds errors in point-line-polygon topology:
        Checks if there is exactly one point from 'pointClasses' within each polygon built by the features of 'polylineClasses'
        
        Remark: All feature classes in 'polylineClasses' and 'pointClasses' must have the same spatial reference.
        The features of 'polylineClasses' are not checked for intersections. Use QaLineIntersect to check
        """
        
        result = Condition("QaCentroids(2)")
        if type(polyline_classes) == list:
            for element in polyline_classes:
                result.parameters.append(Parameter("polylineClasses", element))
        elif polyline_classes is not None:
            result.parameters.append(Parameter("polylineClasses", polyline_classes))
        if type(point_classes) == list:
            for element in point_classes:
                result.parameters.append(Parameter("pointClasses", element))
        elif point_classes is not None:
            result.parameters.append(Parameter("pointClasses", point_classes))
        result.generate_name()
        return result

    @classmethod
    def qa_centroids_3(cls, polyline_classes: List[BaseDataset], point_classes: List[BaseDataset], constraint: str) -> Condition:
        """
        Finds errors in point-line-polygon topology:
        Checks if there is exactly one point from 'pointClasses' within each polygon built by the features of 'polylineClasses'
        
        Remark: All feature classes in 'polylineClasses' and 'pointClasses' must have the same spatial reference.
        The features of 'polylineClasses' are not checked for intersections. Use QaLineIntersect to check
        """
        
        result = Condition("QaCentroids(3)")
        if type(polyline_classes) == list:
            for element in polyline_classes:
                result.parameters.append(Parameter("polylineClasses", element))
        elif polyline_classes is not None:
            result.parameters.append(Parameter("polylineClasses", polyline_classes))
        if type(point_classes) == list:
            for element in point_classes:
                result.parameters.append(Parameter("pointClasses", element))
        elif point_classes is not None:
            result.parameters.append(Parameter("pointClasses", point_classes))
        result.parameters.append(Parameter("constraint", constraint))
        result.generate_name()
        return result

    @classmethod
    def qa_constraint_0(cls, table: BaseDataset, constraint: str) -> Condition:
        """
        Finds all rows in 'table' that do not fulfill 'constraint'
        """
        
        result = Condition("QaConstraint(0)")
        result.parameters.append(Parameter("table", table))
        result.parameters.append(Parameter("constraint", constraint))
        result.generate_name()
        return result

    @classmethod
    def qa_contained_points_count_0(cls, polygon_class: BaseDataset, point_class: BaseDataset, expected_point_count: int, relevant_point_condition: str, polyline_usage: PolylineUsage = 0) -> Condition:
        """
        Finds polygons or polylines with an invalid number of contained points
        """
        
        result = Condition("QaContainedPointsCount(0)")
        result.parameters.append(Parameter("polygonClass", polygon_class))
        result.parameters.append(Parameter("pointClass", point_class))
        result.parameters.append(Parameter("expectedPointCount", expected_point_count))
        result.parameters.append(Parameter("relevantPointCondition", relevant_point_condition))
        result.parameters.append(Parameter("PolylineUsage", polyline_usage))
        result.generate_name()
        return result

    @classmethod
    def qa_contained_points_count_1(cls, polygon_class: BaseDataset, point_class: BaseDataset, minimum_point_count: int, maximum_point_count: int, relevant_point_condition: str, polyline_usage: PolylineUsage = 0) -> Condition:
        """
        Finds polygons or polylines with an invalid number of contained points
        """
        
        result = Condition("QaContainedPointsCount(1)")
        result.parameters.append(Parameter("polygonClass", polygon_class))
        result.parameters.append(Parameter("pointClass", point_class))
        result.parameters.append(Parameter("minimumPointCount", minimum_point_count))
        result.parameters.append(Parameter("maximumPointCount", maximum_point_count))
        result.parameters.append(Parameter("relevantPointCondition", relevant_point_condition))
        result.parameters.append(Parameter("PolylineUsage", polyline_usage))
        result.generate_name()
        return result

    @classmethod
    def qa_contained_points_count_2(cls, polygon_class: BaseDataset, point_class: BaseDataset, minimum_point_count: int, maximum_point_count: int, relevant_point_condition: str, count_point_on_polygon_border: bool, polyline_usage: PolylineUsage = 0) -> Condition:
        """
        Finds polygons or polylines with an invalid number of contained points
        """
        
        result = Condition("QaContainedPointsCount(2)")
        result.parameters.append(Parameter("polygonClass", polygon_class))
        result.parameters.append(Parameter("pointClass", point_class))
        result.parameters.append(Parameter("minimumPointCount", minimum_point_count))
        result.parameters.append(Parameter("maximumPointCount", maximum_point_count))
        result.parameters.append(Parameter("relevantPointCondition", relevant_point_condition))
        result.parameters.append(Parameter("countPointOnPolygonBorder", count_point_on_polygon_border))
        result.parameters.append(Parameter("PolylineUsage", polyline_usage))
        result.generate_name()
        return result

    @classmethod
    def qa_contained_points_count_3(cls, polygon_classes: List[BaseDataset], point_classes: List[BaseDataset], expected_point_count: int, relevant_point_condition: str, polyline_usage: PolylineUsage = 0) -> Condition:
        """
        Finds polygons or polylines with an invalid number of contained points
        """
        
        result = Condition("QaContainedPointsCount(3)")
        if type(polygon_classes) == list:
            for element in polygon_classes:
                result.parameters.append(Parameter("polygonClasses", element))
        elif polygon_classes is not None:
            result.parameters.append(Parameter("polygonClasses", polygon_classes))
        if type(point_classes) == list:
            for element in point_classes:
                result.parameters.append(Parameter("pointClasses", element))
        elif point_classes is not None:
            result.parameters.append(Parameter("pointClasses", point_classes))
        result.parameters.append(Parameter("expectedPointCount", expected_point_count))
        result.parameters.append(Parameter("relevantPointCondition", relevant_point_condition))
        result.parameters.append(Parameter("PolylineUsage", polyline_usage))
        result.generate_name()
        return result

    @classmethod
    def qa_contained_points_count_4(cls, polygon_classes: List[BaseDataset], point_classes: List[BaseDataset], minimum_point_count: int, maximum_point_count: int, relevant_point_condition: str, count_point_on_polygon_border: bool, polyline_usage: PolylineUsage = 0) -> Condition:
        """
        Finds polygons or polylines with an invalid number of contained points
        """
        
        result = Condition("QaContainedPointsCount(4)")
        if type(polygon_classes) == list:
            for element in polygon_classes:
                result.parameters.append(Parameter("polygonClasses", element))
        elif polygon_classes is not None:
            result.parameters.append(Parameter("polygonClasses", polygon_classes))
        if type(point_classes) == list:
            for element in point_classes:
                result.parameters.append(Parameter("pointClasses", element))
        elif point_classes is not None:
            result.parameters.append(Parameter("pointClasses", point_classes))
        result.parameters.append(Parameter("minimumPointCount", minimum_point_count))
        result.parameters.append(Parameter("maximumPointCount", maximum_point_count))
        result.parameters.append(Parameter("relevantPointCondition", relevant_point_condition))
        result.parameters.append(Parameter("countPointOnPolygonBorder", count_point_on_polygon_border))
        result.parameters.append(Parameter("PolylineUsage", polyline_usage))
        result.generate_name()
        return result

    @classmethod
    def qa_contains_other_0(cls, contains: List[BaseDataset], is_within: List[BaseDataset]) -> Condition:
        """
        Finds all features in 'isWithin' that are not contained by any feature in 'contains'
        Remarks: All feature classes in 'contains' and 'isWithin' must have the same spatial reference
        """
        
        result = Condition("QaContainsOther(0)")
        if type(contains) == list:
            for element in contains:
                result.parameters.append(Parameter("contains", element))
        elif contains is not None:
            result.parameters.append(Parameter("contains", contains))
        if type(is_within) == list:
            for element in is_within:
                result.parameters.append(Parameter("isWithin", element))
        elif is_within is not None:
            result.parameters.append(Parameter("isWithin", is_within))
        result.generate_name()
        return result

    @classmethod
    def qa_contains_other_1(cls, contains: BaseDataset, is_within: BaseDataset) -> Condition:
        """
        Finds all features in 'isWithin' that are not contained by any feature in 'contains'
        Remarks: All feature classes in 'contains' and 'isWithin' must have the same spatial reference
        """
        
        result = Condition("QaContainsOther(1)")
        result.parameters.append(Parameter("contains", contains))
        result.parameters.append(Parameter("isWithin", is_within))
        result.generate_name()
        return result

    @classmethod
    def qa_contains_other_2(cls, contains: List[BaseDataset], is_within: List[BaseDataset], is_containing_condition: str, report_individual_parts: bool) -> Condition:
        """
        Finds all features in 'isWithin' that are not contained by any feature in 'contains' for which a given condition is fulfilled.
        Remarks: All feature classes in 'contains' and 'isWithin' must have the same spatial reference
        """
        
        result = Condition("QaContainsOther(2)")
        if type(contains) == list:
            for element in contains:
                result.parameters.append(Parameter("contains", element))
        elif contains is not None:
            result.parameters.append(Parameter("contains", contains))
        if type(is_within) == list:
            for element in is_within:
                result.parameters.append(Parameter("isWithin", element))
        elif is_within is not None:
            result.parameters.append(Parameter("isWithin", is_within))
        result.parameters.append(Parameter("isContainingCondition", is_containing_condition))
        result.parameters.append(Parameter("reportIndividualParts", report_individual_parts))
        result.generate_name()
        return result

    @classmethod
    def qa_contains_other_3(cls, contains: BaseDataset, is_within: BaseDataset, is_containing_condition: str, report_individual_parts: bool) -> Condition:
        """
        Finds all features in 'isWithin' that are not contained by any feature in 'contains' for which a given condition is fulfilled.
        Remarks: All feature classes in 'contains' and 'isWithin' must have the same spatial reference
        """
        
        result = Condition("QaContainsOther(3)")
        result.parameters.append(Parameter("contains", contains))
        result.parameters.append(Parameter("isWithin", is_within))
        result.parameters.append(Parameter("isContainingCondition", is_containing_condition))
        result.parameters.append(Parameter("reportIndividualParts", report_individual_parts))
        result.generate_name()
        return result

    @classmethod
    def qa_coplanar_rings_0(cls, feature_class: BaseDataset, coplanarity_tolerance: float, include_associated_parts: bool) -> Condition:
        """
        Finds multipatch or polygon rings where its points are not coplanar
        """
        
        result = Condition("QaCoplanarRings(0)")
        result.parameters.append(Parameter("featureClass", feature_class))
        result.parameters.append(Parameter("coplanarityTolerance", coplanarity_tolerance))
        result.parameters.append(Parameter("includeAssociatedParts", include_associated_parts))
        result.generate_name()
        return result

    @classmethod
    def qa_crosses_other_0(cls, crossed: List[BaseDataset], crossing: List[BaseDataset]) -> Condition:
        """
        Finds all features in 'crossingClasses' that are crossing any features of 'crossedClasses'
        
        Remark: All feature classes in 'crossingClasses' and 'crossedClasses' must have the same spatial reference.
        """
        
        result = Condition("QaCrossesOther(0)")
        if type(crossed) == list:
            for element in crossed:
                result.parameters.append(Parameter("crossed", element))
        elif crossed is not None:
            result.parameters.append(Parameter("crossed", crossed))
        if type(crossing) == list:
            for element in crossing:
                result.parameters.append(Parameter("crossing", element))
        elif crossing is not None:
            result.parameters.append(Parameter("crossing", crossing))
        result.generate_name()
        return result

    @classmethod
    def qa_crosses_other_1(cls, crossed: BaseDataset, crossing: BaseDataset) -> Condition:
        """
        Finds all features in 'crossingClass' that are crossing any features of 'crossedClass'
        
        Remark: The feature classes in 'crossingClass' and 'crossedClass' must have the same spatial reference.
        """
        
        result = Condition("QaCrossesOther(1)")
        result.parameters.append(Parameter("crossed", crossed))
        result.parameters.append(Parameter("crossing", crossing))
        result.generate_name()
        return result

    @classmethod
    def qa_crosses_other_2(cls, crossed_classes: List[BaseDataset], crossing_classes: List[BaseDataset], valid_relation_constraint: str) -> Condition:
        """
        Finds all features in 'crossingClasses' that are crossing any features of 'crossedClasses', and for which a given constraint is not fulfilled.
        
        Remark: All feature classes in 'crossingClasses' and 'crossedClasses' must have the same spatial reference.
        """
        
        result = Condition("QaCrossesOther(2)")
        if type(crossed_classes) == list:
            for element in crossed_classes:
                result.parameters.append(Parameter("crossedClasses", element))
        elif crossed_classes is not None:
            result.parameters.append(Parameter("crossedClasses", crossed_classes))
        if type(crossing_classes) == list:
            for element in crossing_classes:
                result.parameters.append(Parameter("crossingClasses", element))
        elif crossing_classes is not None:
            result.parameters.append(Parameter("crossingClasses", crossing_classes))
        result.parameters.append(Parameter("validRelationConstraint", valid_relation_constraint))
        result.generate_name()
        return result

    @classmethod
    def qa_crosses_other_3(cls, crossed_class: BaseDataset, crossing_class: BaseDataset, valid_relation_constraint: str) -> Condition:
        """
        Finds all features in 'crossingClass' that are crossing any features of 'crossedClass', and for which a given constraint is not fulfilled.
        
        Remark: The feature classes in 'crossingClass' and 'crossedClass' must have the same spatial reference.
        """
        
        result = Condition("QaCrossesOther(3)")
        result.parameters.append(Parameter("crossedClass", crossed_class))
        result.parameters.append(Parameter("crossingClass", crossing_class))
        result.parameters.append(Parameter("validRelationConstraint", valid_relation_constraint))
        result.generate_name()
        return result

    @classmethod
    def qa_crosses_self_0(cls, feature_classes: List[BaseDataset]) -> Condition:
        """
        Finds all features in 'featureClasses' that are crossing any features of 'featureClasses'
        """
        
        result = Condition("QaCrossesSelf(0)")
        if type(feature_classes) == list:
            for element in feature_classes:
                result.parameters.append(Parameter("featureClasses", element))
        elif feature_classes is not None:
            result.parameters.append(Parameter("featureClasses", feature_classes))
        result.generate_name()
        return result

    @classmethod
    def qa_crosses_self_1(cls, feature_class: BaseDataset) -> Condition:
        """
        Finds all features in 'featureClass' that are crossing any features of 'featureClass'
        """
        
        result = Condition("QaCrossesSelf(1)")
        result.parameters.append(Parameter("featureClass", feature_class))
        result.generate_name()
        return result

    @classmethod
    def qa_crosses_self_2(cls, feature_classes: List[BaseDataset], valid_relation_constraint: str) -> Condition:
        """
        Finds all features in 'featureClasses' that are crossing any features of 'featureClasses', and for which a given constraint is not fulfilled.
        """
        
        result = Condition("QaCrossesSelf(2)")
        if type(feature_classes) == list:
            for element in feature_classes:
                result.parameters.append(Parameter("featureClasses", element))
        elif feature_classes is not None:
            result.parameters.append(Parameter("featureClasses", feature_classes))
        result.parameters.append(Parameter("validRelationConstraint", valid_relation_constraint))
        result.generate_name()
        return result

    @classmethod
    def qa_crosses_self_3(cls, feature_class: BaseDataset, valid_relation_constraint: str) -> Condition:
        """
        Finds all features in 'featureClass' that are crossing any features of 'featureClass', and for which a given constraint is not fulfilled.
        """
        
        result = Condition("QaCrossesSelf(3)")
        result.parameters.append(Parameter("featureClass", feature_class))
        result.parameters.append(Parameter("validRelationConstraint", valid_relation_constraint))
        result.generate_name()
        return result

    @classmethod
    def qa_curve_0(cls, feature_class: BaseDataset, allowed_non_linear_segment_types: List[NonLinearSegmentType] = 0, group_issues_by_segment_type: bool = False) -> Condition:
        """
        Finds segments in 'featureClass' that are not straight lines
        """
        
        result = Condition("QaCurve(0)")
        result.parameters.append(Parameter("featureClass", feature_class))
        if type(allowed_non_linear_segment_types) == list:
            for element in allowed_non_linear_segment_types:
                result.parameters.append(Parameter("AllowedNonLinearSegmentTypes", element))
        elif allowed_non_linear_segment_types is not None:
            result.parameters.append(Parameter("AllowedNonLinearSegmentTypes", allowed_non_linear_segment_types))
        result.parameters.append(Parameter("GroupIssuesBySegmentType", group_issues_by_segment_type))
        result.generate_name()
        return result

    @classmethod
    def qa_dangle_count_0(cls, polyline_class: BaseDataset, dangle_count_expression: str, tolerance: float) -> Condition:
        """
        Finds polyline features with a dangle count for which a given dangle count expression is not fulfilled. Dangles are defined as polyline end points that are not (within a specified tolerance) coincident with end points of other polylines.
        """
        
        result = Condition("QaDangleCount(0)")
        result.parameters.append(Parameter("polylineClass", polyline_class))
        result.parameters.append(Parameter("dangleCountExpression", dangle_count_expression))
        result.parameters.append(Parameter("tolerance", tolerance))
        result.generate_name()
        return result

    @classmethod
    def qa_dangle_count_1(cls, polyline_classes: List[BaseDataset], dangle_count_expressions: List[str], tolerance: float) -> Condition:
        """
        Finds polyline features with a dangle count for which a given dangle count expression is not fulfilled. Dangles are defined as polyline end points that are not (within a specified tolerance) coincident with end points of other polylines.
        """
        
        result = Condition("QaDangleCount(1)")
        if type(polyline_classes) == list:
            for element in polyline_classes:
                result.parameters.append(Parameter("polylineClasses", element))
        elif polyline_classes is not None:
            result.parameters.append(Parameter("polylineClasses", polyline_classes))
        if type(dangle_count_expressions) == list:
            for element in dangle_count_expressions:
                result.parameters.append(Parameter("dangleCountExpressions", element))
        elif dangle_count_expressions is not None:
            result.parameters.append(Parameter("dangleCountExpressions", dangle_count_expressions))
        result.parameters.append(Parameter("tolerance", tolerance))
        result.generate_name()
        return result

    @classmethod
    def qa_date_fields_without_time_0(cls, table: BaseDataset) -> Condition:
        """
        Finds rows with date fields having non-zero time parts. All date fields of the table are checked.
        """
        
        result = Condition("QaDateFieldsWithoutTime(0)")
        result.parameters.append(Parameter("table", table))
        result.generate_name()
        return result

    @classmethod
    def qa_date_fields_without_time_1(cls, table: BaseDataset, date_field_name: str) -> Condition:
        """
        Finds rows that have non-zero time parts in a specified date field.
        """
        
        result = Condition("QaDateFieldsWithoutTime(1)")
        result.parameters.append(Parameter("table", table))
        result.parameters.append(Parameter("dateFieldName", date_field_name))
        result.generate_name()
        return result

    @classmethod
    def qa_date_fields_without_time_2(cls, table: BaseDataset, date_field_names: List[str]) -> Condition:
        """
        Finds rows that have non-zero time parts in a given list of date fields.
        """
        
        result = Condition("QaDateFieldsWithoutTime(2)")
        result.parameters.append(Parameter("table", table))
        if type(date_field_names) == list:
            for element in date_field_names:
                result.parameters.append(Parameter("dateFieldNames", element))
        elif date_field_names is not None:
            result.parameters.append(Parameter("dateFieldNames", date_field_names))
        result.generate_name()
        return result

    @classmethod
    def qa_duplicate_geometry_self_0(cls, feature_class: BaseDataset) -> Condition:
        """
        Finds features with equal geometries in a feature class. Geometries for which the difference geometry is empty are considered duplicates. Z and M values are therefore ignored, and the XY tolerance of the spatial reference is applied.
        """
        
        result = Condition("QaDuplicateGeometrySelf(0)")
        result.parameters.append(Parameter("featureClass", feature_class))
        result.generate_name()
        return result

    @classmethod
    def qa_duplicate_geometry_self_1(cls, feature_class: BaseDataset, valid_duplicate_constraint: str) -> Condition:
        """
        Finds features with equal geometries in a feature class for which a given constraint is not fulfilled. Geometries for which the difference geometry is empty are considered duplicates. Z and M values are therefore ignored, and the XY tolerance of the spatial reference is applied.
        """
        
        result = Condition("QaDuplicateGeometrySelf(1)")
        result.parameters.append(Parameter("featureClass", feature_class))
        result.parameters.append(Parameter("validDuplicateConstraint", valid_duplicate_constraint))
        result.generate_name()
        return result

    @classmethod
    def qa_duplicate_geometry_self_2(cls, feature_class: BaseDataset, valid_duplicate_constraint: str, report_single_error_per_duplicate_set: bool) -> Condition:
        """
        Finds features with equal geometries in a feature class for which a given constraint is not fulfilled. Geometries for which the difference geometry is empty are considered duplicates. Z and M values are therefore ignored, and the XY tolerance of the spatial reference is applied. Optionally, duplicates can be reported as a single error for the entire set of features that have an equal geometry.
        """
        
        result = Condition("QaDuplicateGeometrySelf(2)")
        result.parameters.append(Parameter("featureClass", feature_class))
        result.parameters.append(Parameter("validDuplicateConstraint", valid_duplicate_constraint))
        result.parameters.append(Parameter("reportSingleErrorPerDuplicateSet", report_single_error_per_duplicate_set))
        result.generate_name()
        return result

    @classmethod
    def qa_edge_match_bordering_lines_0(cls, line_class1: BaseDataset, border_class1: BaseDataset, line_class2: BaseDataset, border_class2: BaseDataset, search_distance: float, line_class1_border_match_condition: str = None, line_class2_border_match_condition: str = None, bordering_line_match_condition: str = None, bordering_line_attribute_constraint: str = None, bordering_line_equal_attributes: str = None, bordering_line_equal_attribute_options: List[str] = None, report_individual_attribute_constraint_violations: bool = False, is_bordering_line_attribute_constraint_symmetric: bool = False, allow_disjoint_candidate_feature_if_borders_are_not_coincident: bool = False, allow_no_feature_within_search_distance: bool = False, allow_non_coincident_end_points_on_border: bool = False, allow_disjoint_candidate_feature_if_attribute_constraints_are_fulfilled: bool = False) -> Condition:
        """
        Finds sections of polylines that follow along the border and have no suitable coincident polyline on the other side of the border that fulfills defined attribute matching rules.
        
        Different border representations may be used for the respective sides, i.e. the borders are not required to be exactly coincident for this test to be applicable.
        
        The border features may be stored either in two separate border feature classes, or in a common border feature class containing the borders for different areas. When using a common border feature class, the bordering polyline features are associated to their corresponding border by means of SQL expressions (‘LineClass1BorderMatchCondition’, ‘LineClass2BorderMatchCondition’). If the bordering polyline features are also stored in common feature classes, then the polyline feature pairs belonging to opposite sides of the border are also identified by an SQL expression (‘BorderingLineMatchCondition’). Using common feature classes for the border features\/bordering polyline features in conjunction with the match conditions allows to verify borders between more than two areas using a single quality condition.
        
        Only polyline features that have at least a partial linear intersection with the border geometry of their side are considered as candidates for bordering polylines. The identification of polylines that are close to, but not exactly snapped to border geometries is possible using proximity tests.
        
        Based on a single polyline feature class per side.
        """
        
        result = Condition("QaEdgeMatchBorderingLines(0)")
        result.parameters.append(Parameter("lineClass1", line_class1))
        result.parameters.append(Parameter("borderClass1", border_class1))
        result.parameters.append(Parameter("lineClass2", line_class2))
        result.parameters.append(Parameter("borderClass2", border_class2))
        result.parameters.append(Parameter("searchDistance", search_distance))
        result.parameters.append(Parameter("LineClass1BorderMatchCondition", line_class1_border_match_condition))
        result.parameters.append(Parameter("LineClass2BorderMatchCondition", line_class2_border_match_condition))
        result.parameters.append(Parameter("BorderingLineMatchCondition", bordering_line_match_condition))
        result.parameters.append(Parameter("BorderingLineAttributeConstraint", bordering_line_attribute_constraint))
        result.parameters.append(Parameter("BorderingLineEqualAttributes", bordering_line_equal_attributes))
        if type(bordering_line_equal_attribute_options) == list:
            for element in bordering_line_equal_attribute_options:
                result.parameters.append(Parameter("BorderingLineEqualAttributeOptions", element))
        elif bordering_line_equal_attribute_options is not None:
            result.parameters.append(Parameter("BorderingLineEqualAttributeOptions", bordering_line_equal_attribute_options))
        result.parameters.append(Parameter("ReportIndividualAttributeConstraintViolations", report_individual_attribute_constraint_violations))
        result.parameters.append(Parameter("IsBorderingLineAttributeConstraintSymmetric", is_bordering_line_attribute_constraint_symmetric))
        result.parameters.append(Parameter("AllowDisjointCandidateFeatureIfBordersAreNotCoincident", allow_disjoint_candidate_feature_if_borders_are_not_coincident))
        result.parameters.append(Parameter("AllowNoFeatureWithinSearchDistance", allow_no_feature_within_search_distance))
        result.parameters.append(Parameter("AllowNonCoincidentEndPointsOnBorder", allow_non_coincident_end_points_on_border))
        result.parameters.append(Parameter("AllowDisjointCandidateFeatureIfAttributeConstraintsAreFulfilled", allow_disjoint_candidate_feature_if_attribute_constraints_are_fulfilled))
        result.generate_name()
        return result

    @classmethod
    def qa_edge_match_bordering_lines_1(cls, line_classes1: List[BaseDataset], border_class1: BaseDataset, line_classes2: List[BaseDataset], border_class2: BaseDataset, search_distance: float, line_class1_border_match_condition: str = None, line_class2_border_match_condition: str = None, bordering_line_match_condition: str = None, bordering_line_attribute_constraint: str = None, bordering_line_equal_attributes: str = None, bordering_line_equal_attribute_options: List[str] = None, report_individual_attribute_constraint_violations: bool = False, is_bordering_line_attribute_constraint_symmetric: bool = False, allow_disjoint_candidate_feature_if_borders_are_not_coincident: bool = False, allow_no_feature_within_search_distance: bool = False, allow_non_coincident_end_points_on_border: bool = False, allow_disjoint_candidate_feature_if_attribute_constraints_are_fulfilled: bool = False) -> Condition:
        """
        Finds sections of polylines that follow along the border and have no suitable coincident polyline on the other side of the border that fulfills defined attribute matching rules.
        
        Different border representations may be used for the respective sides, i.e. the borders are not required to be exactly coincident for this test to be applicable.
        
        The border features may be stored either in two separate border feature classes, or in a common border feature class containing the borders for different areas. When using a common border feature class, the bordering polyline features are associated to their corresponding border by means of SQL expressions (‘LineClass1BorderMatchCondition’, ‘LineClass2BorderMatchCondition’). If the bordering polyline features are also stored in common feature classes, then the polyline feature pairs belonging to opposite sides of the border are also identified by an SQL expression (‘BorderingLineMatchCondition’). Using common feature classes for the border features\/bordering polyline features in conjunction with the match conditions allows to verify borders between more than two areas using a single quality condition.
        
        Only polyline features that have at least a partial linear intersection with the border geometry of their side are considered as candidates for bordering polylines. The identification of polylines that are close to, but not exactly snapped to border geometries is possible using proximity tests.
        
        Based on a list of polyline feature classes per side.
        """
        
        result = Condition("QaEdgeMatchBorderingLines(1)")
        if type(line_classes1) == list:
            for element in line_classes1:
                result.parameters.append(Parameter("lineClasses1", element))
        elif line_classes1 is not None:
            result.parameters.append(Parameter("lineClasses1", line_classes1))
        result.parameters.append(Parameter("borderClass1", border_class1))
        if type(line_classes2) == list:
            for element in line_classes2:
                result.parameters.append(Parameter("lineClasses2", element))
        elif line_classes2 is not None:
            result.parameters.append(Parameter("lineClasses2", line_classes2))
        result.parameters.append(Parameter("borderClass2", border_class2))
        result.parameters.append(Parameter("searchDistance", search_distance))
        result.parameters.append(Parameter("LineClass1BorderMatchCondition", line_class1_border_match_condition))
        result.parameters.append(Parameter("LineClass2BorderMatchCondition", line_class2_border_match_condition))
        result.parameters.append(Parameter("BorderingLineMatchCondition", bordering_line_match_condition))
        result.parameters.append(Parameter("BorderingLineAttributeConstraint", bordering_line_attribute_constraint))
        result.parameters.append(Parameter("BorderingLineEqualAttributes", bordering_line_equal_attributes))
        if type(bordering_line_equal_attribute_options) == list:
            for element in bordering_line_equal_attribute_options:
                result.parameters.append(Parameter("BorderingLineEqualAttributeOptions", element))
        elif bordering_line_equal_attribute_options is not None:
            result.parameters.append(Parameter("BorderingLineEqualAttributeOptions", bordering_line_equal_attribute_options))
        result.parameters.append(Parameter("ReportIndividualAttributeConstraintViolations", report_individual_attribute_constraint_violations))
        result.parameters.append(Parameter("IsBorderingLineAttributeConstraintSymmetric", is_bordering_line_attribute_constraint_symmetric))
        result.parameters.append(Parameter("AllowDisjointCandidateFeatureIfBordersAreNotCoincident", allow_disjoint_candidate_feature_if_borders_are_not_coincident))
        result.parameters.append(Parameter("AllowNoFeatureWithinSearchDistance", allow_no_feature_within_search_distance))
        result.parameters.append(Parameter("AllowNonCoincidentEndPointsOnBorder", allow_non_coincident_end_points_on_border))
        result.parameters.append(Parameter("AllowDisjointCandidateFeatureIfAttributeConstraintsAreFulfilled", allow_disjoint_candidate_feature_if_attribute_constraints_are_fulfilled))
        result.generate_name()
        return result

    @classmethod
    def qa_edge_match_bordering_points_0(cls, point_class1: BaseDataset, border_class1: BaseDataset, point_class2: BaseDataset, border_class2: BaseDataset, search_distance: float, point_class1_border_match_condition: str = None, point_class2_border_match_condition: str = None, bordering_point_match_condition: str = None, bordering_point_attribute_constraint: str = None, is_bordering_point_attribute_constraint_symmetric: bool = False, bordering_point_equal_attributes: str = None, bordering_point_equal_attribute_options: List[str] = None, report_individual_attribute_constraint_violations: bool = False, coincidence_tolerance: float = 0, allow_disjoint_candidate_feature_if_borders_are_not_coincident: bool = False, allow_no_feature_within_search_distance: bool = False, allow_disjoint_candidate_feature_if_attribute_constraints_are_fulfilled: bool = False) -> Condition:
        """
        Finds points located on the border which have no coincident corresponding point for the opposite side of the border that fulfills defined attribute matching rules.
        
        Different border representations may be used for the respective sides, i.e. the borders are not required to be exactly coincident for this test to be applicable.
        
        The border features may be stored either in two separate border feature classes, or in a common border feature class containing the borders for different areas. When using a common border feature class, the point features are associated to their corresponding border by means of SQL expressions (‘PointClass1BorderMatchCondition’, ‘PointClass2BorderMatchCondition’). If the bordering point features are also stored in common feature classes, then the point feature pairs belonging to opposite sides of the border are also identified by an SQL expression (‘BorderingPointMatchCondition’). Using common feature classes for the border features\/bordering point features in conjunction with the match conditions allows to verify borders between more than two areas using a single quality condition.
        
        Only point features located exactly on the border geometry of their side are considered as candidates for bordering points. The identification of points that are close to, but not exactly snapped to border geometries is possible using proximity tests.
        
        Based on a single point feature class per side.
        """
        
        result = Condition("QaEdgeMatchBorderingPoints(0)")
        result.parameters.append(Parameter("pointClass1", point_class1))
        result.parameters.append(Parameter("borderClass1", border_class1))
        result.parameters.append(Parameter("pointClass2", point_class2))
        result.parameters.append(Parameter("borderClass2", border_class2))
        result.parameters.append(Parameter("searchDistance", search_distance))
        result.parameters.append(Parameter("PointClass1BorderMatchCondition", point_class1_border_match_condition))
        result.parameters.append(Parameter("PointClass2BorderMatchCondition", point_class2_border_match_condition))
        result.parameters.append(Parameter("BorderingPointMatchCondition", bordering_point_match_condition))
        result.parameters.append(Parameter("BorderingPointAttributeConstraint", bordering_point_attribute_constraint))
        result.parameters.append(Parameter("IsBorderingPointAttributeConstraintSymmetric", is_bordering_point_attribute_constraint_symmetric))
        result.parameters.append(Parameter("BorderingPointEqualAttributes", bordering_point_equal_attributes))
        if type(bordering_point_equal_attribute_options) == list:
            for element in bordering_point_equal_attribute_options:
                result.parameters.append(Parameter("BorderingPointEqualAttributeOptions", element))
        elif bordering_point_equal_attribute_options is not None:
            result.parameters.append(Parameter("BorderingPointEqualAttributeOptions", bordering_point_equal_attribute_options))
        result.parameters.append(Parameter("ReportIndividualAttributeConstraintViolations", report_individual_attribute_constraint_violations))
        result.parameters.append(Parameter("CoincidenceTolerance", coincidence_tolerance))
        result.parameters.append(Parameter("AllowDisjointCandidateFeatureIfBordersAreNotCoincident", allow_disjoint_candidate_feature_if_borders_are_not_coincident))
        result.parameters.append(Parameter("AllowNoFeatureWithinSearchDistance", allow_no_feature_within_search_distance))
        result.parameters.append(Parameter("AllowDisjointCandidateFeatureIfAttributeConstraintsAreFulfilled", allow_disjoint_candidate_feature_if_attribute_constraints_are_fulfilled))
        result.generate_name()
        return result

    @classmethod
    def qa_edge_match_bordering_points_1(cls, point_classes1: List[BaseDataset], border_class1: BaseDataset, point_classes2: List[BaseDataset], border_class2: BaseDataset, search_distance: float, point_class1_border_match_condition: str = None, point_class2_border_match_condition: str = None, bordering_point_match_condition: str = None, bordering_point_attribute_constraint: str = None, is_bordering_point_attribute_constraint_symmetric: bool = False, bordering_point_equal_attributes: str = None, bordering_point_equal_attribute_options: List[str] = None, report_individual_attribute_constraint_violations: bool = False, coincidence_tolerance: float = 0, allow_disjoint_candidate_feature_if_borders_are_not_coincident: bool = False, allow_no_feature_within_search_distance: bool = False, allow_disjoint_candidate_feature_if_attribute_constraints_are_fulfilled: bool = False) -> Condition:
        """
        Finds points located on the border which have no coincident corresponding point for the opposite side of the border that fulfills defined attribute matching rules.
        
        Different border representations may be used for the respective sides, i.e. the borders are not required to be exactly coincident for this test to be applicable.
        
        The border features may be stored either in two separate border feature classes, or in a common border feature class containing the borders for different areas. When using a common border feature class, the point features are associated to their corresponding border by means of SQL expressions (‘PointClass1BorderMatchCondition’, ‘PointClass2BorderMatchCondition’). If the bordering point features are also stored in common feature classes, then the point feature pairs belonging to opposite sides of the border are also identified by an SQL expression (‘BorderingPointMatchCondition’). Using common feature classes for the border features\/bordering point features in conjunction with the match conditions allows to verify borders between more than two areas using a single quality condition.
        
        Only point features located exactly on the border geometry of their side are considered as candidates for bordering points. The identification of points that are close to, but not exactly snapped to border geometries is possible using proximity tests.
        
        Based on a list of point feature classes per side.
        """
        
        result = Condition("QaEdgeMatchBorderingPoints(1)")
        if type(point_classes1) == list:
            for element in point_classes1:
                result.parameters.append(Parameter("pointClasses1", element))
        elif point_classes1 is not None:
            result.parameters.append(Parameter("pointClasses1", point_classes1))
        result.parameters.append(Parameter("borderClass1", border_class1))
        if type(point_classes2) == list:
            for element in point_classes2:
                result.parameters.append(Parameter("pointClasses2", element))
        elif point_classes2 is not None:
            result.parameters.append(Parameter("pointClasses2", point_classes2))
        result.parameters.append(Parameter("borderClass2", border_class2))
        result.parameters.append(Parameter("searchDistance", search_distance))
        result.parameters.append(Parameter("PointClass1BorderMatchCondition", point_class1_border_match_condition))
        result.parameters.append(Parameter("PointClass2BorderMatchCondition", point_class2_border_match_condition))
        result.parameters.append(Parameter("BorderingPointMatchCondition", bordering_point_match_condition))
        result.parameters.append(Parameter("BorderingPointAttributeConstraint", bordering_point_attribute_constraint))
        result.parameters.append(Parameter("IsBorderingPointAttributeConstraintSymmetric", is_bordering_point_attribute_constraint_symmetric))
        result.parameters.append(Parameter("BorderingPointEqualAttributes", bordering_point_equal_attributes))
        if type(bordering_point_equal_attribute_options) == list:
            for element in bordering_point_equal_attribute_options:
                result.parameters.append(Parameter("BorderingPointEqualAttributeOptions", element))
        elif bordering_point_equal_attribute_options is not None:
            result.parameters.append(Parameter("BorderingPointEqualAttributeOptions", bordering_point_equal_attribute_options))
        result.parameters.append(Parameter("ReportIndividualAttributeConstraintViolations", report_individual_attribute_constraint_violations))
        result.parameters.append(Parameter("CoincidenceTolerance", coincidence_tolerance))
        result.parameters.append(Parameter("AllowDisjointCandidateFeatureIfBordersAreNotCoincident", allow_disjoint_candidate_feature_if_borders_are_not_coincident))
        result.parameters.append(Parameter("AllowNoFeatureWithinSearchDistance", allow_no_feature_within_search_distance))
        result.parameters.append(Parameter("AllowDisjointCandidateFeatureIfAttributeConstraintsAreFulfilled", allow_disjoint_candidate_feature_if_attribute_constraints_are_fulfilled))
        result.generate_name()
        return result

    @classmethod
    def qa_edge_match_crossing_areas_0(cls, area_class1: BaseDataset, border_class1: BaseDataset, area_class2: BaseDataset, border_class2: BaseDataset, search_distance: float, bounding_classes1: List[BaseDataset], bounding_classes2: List[BaseDataset], area_class1_border_match_condition: str = None, area_class1_bounding_feature_match_condition: str = None, area_class2_bounding_feature_match_condition: str = None, area_class2_border_match_condition: str = None, crossing_area_match_condition: str = None, crossing_area_attribute_constraint: str = None, is_crossing_area_attribute_constraint_symmetric: bool = False, crossing_area_equal_attributes: str = None, crossing_area_equal_attribute_options: List[str] = False, report_individual_attribute_constraint_violations: bool = False, allow_no_feature_within_search_distance: bool = False, allow_disjoint_candidate_feature_if_borders_are_not_coincident: bool = False, allow_disjoint_candidate_feature_if_attribute_constraints_are_fulfilled: bool = False) -> Condition:
        """
        Finds polygons that touch the border and have no suitable connecting polygon on the other side of the border that fulfills defined attribute matching rules.
        
        Different border representations may be used for the respective sides, i.e. the borders are not required to be exactly coincident for this test to be applicable.
        
        The border features may be stored either in two separate border feature classes, or in a common border feature class containing the borders for different areas. When using a common border feature class, the crossing polygon features are associated to their corresponding border by means of SQL expressions (‘AreaClass1BorderMatchCondition’, ‘AreaClass2BorderMatchCondition’). If the crossing polygon features are also stored in common feature classes, then the polygon feature pairs belonging to opposite sides of the border are also identified by an SQL expression (‘CrossingAreaMatchCondition’). Using common feature classes for the border features\/crossing polygon features in conjunction with these match conditions allows to verify borders between more than two areas using a single quality condition.
        
        Only polygon features that have at least a partial linear intersection of their boundary with the border geometry of their side are considered as candidates for crossing polygons. The identification of polygons that are close to, but not exactly snapped to border geometries is possible using proximity tests.
        
        Based on a single polygon feature class per side.
        """
        
        result = Condition("QaEdgeMatchCrossingAreas(0)")
        result.parameters.append(Parameter("areaClass1", area_class1))
        result.parameters.append(Parameter("borderClass1", border_class1))
        result.parameters.append(Parameter("areaClass2", area_class2))
        result.parameters.append(Parameter("borderClass2", border_class2))
        result.parameters.append(Parameter("searchDistance", search_distance))
        if type(bounding_classes1) == list:
            for element in bounding_classes1:
                result.parameters.append(Parameter("boundingClasses1", element))
        elif bounding_classes1 is not None:
            result.parameters.append(Parameter("boundingClasses1", bounding_classes1))
        if type(bounding_classes2) == list:
            for element in bounding_classes2:
                result.parameters.append(Parameter("boundingClasses2", element))
        elif bounding_classes2 is not None:
            result.parameters.append(Parameter("boundingClasses2", bounding_classes2))
        result.parameters.append(Parameter("AreaClass1BorderMatchCondition", area_class1_border_match_condition))
        result.parameters.append(Parameter("AreaClass1BoundingFeatureMatchCondition", area_class1_bounding_feature_match_condition))
        result.parameters.append(Parameter("AreaClass2BoundingFeatureMatchCondition", area_class2_bounding_feature_match_condition))
        result.parameters.append(Parameter("AreaClass2BorderMatchCondition", area_class2_border_match_condition))
        result.parameters.append(Parameter("CrossingAreaMatchCondition", crossing_area_match_condition))
        result.parameters.append(Parameter("CrossingAreaAttributeConstraint", crossing_area_attribute_constraint))
        result.parameters.append(Parameter("IsCrossingAreaAttributeConstraintSymmetric", is_crossing_area_attribute_constraint_symmetric))
        result.parameters.append(Parameter("CrossingAreaEqualAttributes", crossing_area_equal_attributes))
        if type(crossing_area_equal_attribute_options) == list:
            for element in crossing_area_equal_attribute_options:
                result.parameters.append(Parameter("CrossingAreaEqualAttributeOptions", element))
        elif crossing_area_equal_attribute_options is not None:
            result.parameters.append(Parameter("CrossingAreaEqualAttributeOptions", crossing_area_equal_attribute_options))
        result.parameters.append(Parameter("ReportIndividualAttributeConstraintViolations", report_individual_attribute_constraint_violations))
        result.parameters.append(Parameter("AllowNoFeatureWithinSearchDistance", allow_no_feature_within_search_distance))
        result.parameters.append(Parameter("AllowDisjointCandidateFeatureIfBordersAreNotCoincident", allow_disjoint_candidate_feature_if_borders_are_not_coincident))
        result.parameters.append(Parameter("AllowDisjointCandidateFeatureIfAttributeConstraintsAreFulfilled", allow_disjoint_candidate_feature_if_attribute_constraints_are_fulfilled))
        result.generate_name()
        return result

    @classmethod
    def qa_edge_match_crossing_areas_1(cls, area_classes1: List[BaseDataset], border_class1: BaseDataset, area_classes2: List[BaseDataset], border_class2: BaseDataset, search_distance: float, bounding_classes1: List[BaseDataset], bounding_classes2: List[BaseDataset], area_class1_border_match_condition: str = None, area_class1_bounding_feature_match_condition: str = None, area_class2_bounding_feature_match_condition: str = None, area_class2_border_match_condition: str = None, crossing_area_match_condition: str = None, crossing_area_attribute_constraint: str = None, is_crossing_area_attribute_constraint_symmetric: bool = False, crossing_area_equal_attributes: str = None, crossing_area_equal_attribute_options: List[str] = False, report_individual_attribute_constraint_violations: bool = False, allow_no_feature_within_search_distance: bool = False, allow_disjoint_candidate_feature_if_borders_are_not_coincident: bool = False, allow_disjoint_candidate_feature_if_attribute_constraints_are_fulfilled: bool = False) -> Condition:
        """
        Finds polygons that touch the border and have no suitable connecting polygon on the other side of the border that fulfills defined attribute matching rules.
        
        Different border representations may be used for the respective sides, i.e. the borders are not required to be exactly coincident for this test to be applicable.
        
        The border features may be stored either in two separate border feature classes, or in a common border feature class containing the borders for different areas. When using a common border feature class, the crossing polygon features are associated to their corresponding border by means of SQL expressions (‘AreaClass1BorderMatchCondition’, ‘AreaClass2BorderMatchCondition’). If the crossing polygon features are also stored in common feature classes, then the polygon feature pairs belonging to opposite sides of the border are also identified by an SQL expression (‘CrossingAreaMatchCondition’). Using common feature classes for the border features\/crossing polygon features in conjunction with these match conditions allows to verify borders between more than two areas using a single quality condition.
        
        Only polygon features that have at least a partial linear intersection of their boundary with the border geometry of their side are considered as candidates for crossing polygons. The identification of polygons that are close to, but not exactly snapped to border geometries is possible using proximity tests.
        
        Based on a list of polygon feature classes per side.
        """
        
        result = Condition("QaEdgeMatchCrossingAreas(1)")
        if type(area_classes1) == list:
            for element in area_classes1:
                result.parameters.append(Parameter("areaClasses1", element))
        elif area_classes1 is not None:
            result.parameters.append(Parameter("areaClasses1", area_classes1))
        result.parameters.append(Parameter("borderClass1", border_class1))
        if type(area_classes2) == list:
            for element in area_classes2:
                result.parameters.append(Parameter("areaClasses2", element))
        elif area_classes2 is not None:
            result.parameters.append(Parameter("areaClasses2", area_classes2))
        result.parameters.append(Parameter("borderClass2", border_class2))
        result.parameters.append(Parameter("searchDistance", search_distance))
        if type(bounding_classes1) == list:
            for element in bounding_classes1:
                result.parameters.append(Parameter("boundingClasses1", element))
        elif bounding_classes1 is not None:
            result.parameters.append(Parameter("boundingClasses1", bounding_classes1))
        if type(bounding_classes2) == list:
            for element in bounding_classes2:
                result.parameters.append(Parameter("boundingClasses2", element))
        elif bounding_classes2 is not None:
            result.parameters.append(Parameter("boundingClasses2", bounding_classes2))
        result.parameters.append(Parameter("AreaClass1BorderMatchCondition", area_class1_border_match_condition))
        result.parameters.append(Parameter("AreaClass1BoundingFeatureMatchCondition", area_class1_bounding_feature_match_condition))
        result.parameters.append(Parameter("AreaClass2BoundingFeatureMatchCondition", area_class2_bounding_feature_match_condition))
        result.parameters.append(Parameter("AreaClass2BorderMatchCondition", area_class2_border_match_condition))
        result.parameters.append(Parameter("CrossingAreaMatchCondition", crossing_area_match_condition))
        result.parameters.append(Parameter("CrossingAreaAttributeConstraint", crossing_area_attribute_constraint))
        result.parameters.append(Parameter("IsCrossingAreaAttributeConstraintSymmetric", is_crossing_area_attribute_constraint_symmetric))
        result.parameters.append(Parameter("CrossingAreaEqualAttributes", crossing_area_equal_attributes))
        if type(crossing_area_equal_attribute_options) == list:
            for element in crossing_area_equal_attribute_options:
                result.parameters.append(Parameter("CrossingAreaEqualAttributeOptions", element))
        elif crossing_area_equal_attribute_options is not None:
            result.parameters.append(Parameter("CrossingAreaEqualAttributeOptions", crossing_area_equal_attribute_options))
        result.parameters.append(Parameter("ReportIndividualAttributeConstraintViolations", report_individual_attribute_constraint_violations))
        result.parameters.append(Parameter("AllowNoFeatureWithinSearchDistance", allow_no_feature_within_search_distance))
        result.parameters.append(Parameter("AllowDisjointCandidateFeatureIfBordersAreNotCoincident", allow_disjoint_candidate_feature_if_borders_are_not_coincident))
        result.parameters.append(Parameter("AllowDisjointCandidateFeatureIfAttributeConstraintsAreFulfilled", allow_disjoint_candidate_feature_if_attribute_constraints_are_fulfilled))
        result.generate_name()
        return result

    @classmethod
    def qa_edge_match_crossing_lines_0(cls, line_class1: BaseDataset, border_class1: BaseDataset, line_class2: BaseDataset, border_class2: BaseDataset, search_distance: float, minimum_error_connection_line_length: float = 0, maximum_end_point_connection_distance: float = 0, line_class1_border_match_condition: str = None, line_class2_border_match_condition: str = None, crossing_line_match_condition: str = None, crossing_line_attribute_constraint: str = None, is_crossing_line_attribute_constraint_symmetric: bool = False, crossing_line_equal_attributes: str = None, crossing_line_equal_attribute_options: List[str] = None, report_individual_attribute_constraint_violations: bool = False, coincidence_tolerance: float = 0, allow_no_feature_within_search_distance: bool = False, ignore_attribute_constraints_if_three_or_more_connected: bool = False, allow_no_feature_within_search_distance_if_connected_on_same_side: bool = True, allow_disjoint_candidate_feature_if_borders_are_not_coincident: bool = False, ignore_neighbor_lines_with_border_connection_outside_search_distance: bool = True, allow_end_points_connecting_to_interior_of_valid_neighbor_line: bool = False, ignore_end_points_of_bordering_lines: bool = True, allow_disjoint_candidate_feature_if_attribute_constraints_are_fulfilled: bool = False) -> Condition:
        """
        Finds lines that end on the border which have no suitable connecting neighbor line on the other side of the border.
        
        Different border representations may be used for the respective sides, i.e. the borders are not required to be exactly coincident for this test to be applicable.
        
        The border features may be stored either in two separate border feature classes, or in a common border feature class containing the borders for different areas. When using a common border feature class, the crossing polyline features are associated to their corresponding border by means of SQL expressions (‘LineClass1BorderMatchCondition’, ‘LineClass2BorderMatchCondition’). If the crossing polyline features are also stored in common feature classes, then the polyline feature pairs belonging to opposite sides of the border are also identified by an SQL expression (‘CrossingLineMatchCondition’). Using common feature classes for the border features\/crossing polyline features in conjunction with the match conditions allows to verify borders between more than two areas using a single quality condition.
        
        Only polyline features that have at least one end point located exactly on the border geometry of their side are considered as candidates for crossing polylines. The identification of polyline end points that are close to, but not exactly snapped to border geometries is possible using proximity tests.
        
        Based on a single polyline feature class per side.
        """
        
        result = Condition("QaEdgeMatchCrossingLines(0)")
        result.parameters.append(Parameter("lineClass1", line_class1))
        result.parameters.append(Parameter("borderClass1", border_class1))
        result.parameters.append(Parameter("lineClass2", line_class2))
        result.parameters.append(Parameter("borderClass2", border_class2))
        result.parameters.append(Parameter("searchDistance", search_distance))
        result.parameters.append(Parameter("MinimumErrorConnectionLineLength", minimum_error_connection_line_length))
        result.parameters.append(Parameter("MaximumEndPointConnectionDistance", maximum_end_point_connection_distance))
        result.parameters.append(Parameter("LineClass1BorderMatchCondition", line_class1_border_match_condition))
        result.parameters.append(Parameter("LineClass2BorderMatchCondition", line_class2_border_match_condition))
        result.parameters.append(Parameter("CrossingLineMatchCondition", crossing_line_match_condition))
        result.parameters.append(Parameter("CrossingLineAttributeConstraint", crossing_line_attribute_constraint))
        result.parameters.append(Parameter("IsCrossingLineAttributeConstraintSymmetric", is_crossing_line_attribute_constraint_symmetric))
        result.parameters.append(Parameter("CrossingLineEqualAttributes", crossing_line_equal_attributes))
        if type(crossing_line_equal_attribute_options) == list:
            for element in crossing_line_equal_attribute_options:
                result.parameters.append(Parameter("CrossingLineEqualAttributeOptions", element))
        elif crossing_line_equal_attribute_options is not None:
            result.parameters.append(Parameter("CrossingLineEqualAttributeOptions", crossing_line_equal_attribute_options))
        result.parameters.append(Parameter("ReportIndividualAttributeConstraintViolations", report_individual_attribute_constraint_violations))
        result.parameters.append(Parameter("CoincidenceTolerance", coincidence_tolerance))
        result.parameters.append(Parameter("AllowNoFeatureWithinSearchDistance", allow_no_feature_within_search_distance))
        result.parameters.append(Parameter("IgnoreAttributeConstraintsIfThreeOrMoreConnected", ignore_attribute_constraints_if_three_or_more_connected))
        result.parameters.append(Parameter("AllowNoFeatureWithinSearchDistanceIfConnectedOnSameSide", allow_no_feature_within_search_distance_if_connected_on_same_side))
        result.parameters.append(Parameter("AllowDisjointCandidateFeatureIfBordersAreNotCoincident", allow_disjoint_candidate_feature_if_borders_are_not_coincident))
        result.parameters.append(Parameter("IgnoreNeighborLinesWithBorderConnectionOutsideSearchDistance", ignore_neighbor_lines_with_border_connection_outside_search_distance))
        result.parameters.append(Parameter("AllowEndPointsConnectingToInteriorOfValidNeighborLine", allow_end_points_connecting_to_interior_of_valid_neighbor_line))
        result.parameters.append(Parameter("IgnoreEndPointsOfBorderingLines", ignore_end_points_of_bordering_lines))
        result.parameters.append(Parameter("AllowDisjointCandidateFeatureIfAttributeConstraintsAreFulfilled", allow_disjoint_candidate_feature_if_attribute_constraints_are_fulfilled))
        result.generate_name()
        return result

    @classmethod
    def qa_edge_match_crossing_lines_1(cls, line_classes1: List[BaseDataset], border_class1: BaseDataset, line_classes2: List[BaseDataset], border_class2: BaseDataset, search_distance: float, minimum_error_connection_line_length: float = 0, maximum_end_point_connection_distance: float = 0, line_class1_border_match_condition: str = None, line_class2_border_match_condition: str = None, crossing_line_match_condition: str = None, crossing_line_attribute_constraint: str = None, is_crossing_line_attribute_constraint_symmetric: bool = False, crossing_line_equal_attributes: str = None, crossing_line_equal_attribute_options: List[str] = None, report_individual_attribute_constraint_violations: bool = False, coincidence_tolerance: float = 0, allow_no_feature_within_search_distance: bool = False, ignore_attribute_constraints_if_three_or_more_connected: bool = False, allow_no_feature_within_search_distance_if_connected_on_same_side: bool = True, allow_disjoint_candidate_feature_if_borders_are_not_coincident: bool = False, ignore_neighbor_lines_with_border_connection_outside_search_distance: bool = True, allow_end_points_connecting_to_interior_of_valid_neighbor_line: bool = False, ignore_end_points_of_bordering_lines: bool = True, allow_disjoint_candidate_feature_if_attribute_constraints_are_fulfilled: bool = False) -> Condition:
        """
        Finds lines that end on the border which have no suitable connecting neighbor line on the other side of the border.
        
        Different border representations may be used for the respective sides, i.e. the borders are not required to be exactly coincident for this test to be applicable.
        
        The border features may be stored either in two separate border feature classes, or in a common border feature class containing the borders for different areas. When using a common border feature class, the crossing polyline features are associated to their corresponding border by means of SQL expressions (‘LineClass1BorderMatchCondition’, ‘LineClass2BorderMatchCondition’). If the crossing polyline features are also stored in common feature classes, then the polyline feature pairs belonging to opposite sides of the border are also identified by an SQL expression (‘CrossingLineMatchCondition’). Using common feature classes for the border features\/crossing polyline features in conjunction with the match conditions allows to verify borders between more than two areas using a single quality condition.
        
        Only polyline features that have at least one end point located exactly on the border geometry of their side are considered as candidates for crossing polylines. The identification of polyline end points that are close to, but not exactly snapped to border geometries is possible using proximity tests.
        
        Based on a list of polyline feature classes per side.
        """
        
        result = Condition("QaEdgeMatchCrossingLines(1)")
        if type(line_classes1) == list:
            for element in line_classes1:
                result.parameters.append(Parameter("lineClasses1", element))
        elif line_classes1 is not None:
            result.parameters.append(Parameter("lineClasses1", line_classes1))
        result.parameters.append(Parameter("borderClass1", border_class1))
        if type(line_classes2) == list:
            for element in line_classes2:
                result.parameters.append(Parameter("lineClasses2", element))
        elif line_classes2 is not None:
            result.parameters.append(Parameter("lineClasses2", line_classes2))
        result.parameters.append(Parameter("borderClass2", border_class2))
        result.parameters.append(Parameter("searchDistance", search_distance))
        result.parameters.append(Parameter("MinimumErrorConnectionLineLength", minimum_error_connection_line_length))
        result.parameters.append(Parameter("MaximumEndPointConnectionDistance", maximum_end_point_connection_distance))
        result.parameters.append(Parameter("LineClass1BorderMatchCondition", line_class1_border_match_condition))
        result.parameters.append(Parameter("LineClass2BorderMatchCondition", line_class2_border_match_condition))
        result.parameters.append(Parameter("CrossingLineMatchCondition", crossing_line_match_condition))
        result.parameters.append(Parameter("CrossingLineAttributeConstraint", crossing_line_attribute_constraint))
        result.parameters.append(Parameter("IsCrossingLineAttributeConstraintSymmetric", is_crossing_line_attribute_constraint_symmetric))
        result.parameters.append(Parameter("CrossingLineEqualAttributes", crossing_line_equal_attributes))
        if type(crossing_line_equal_attribute_options) == list:
            for element in crossing_line_equal_attribute_options:
                result.parameters.append(Parameter("CrossingLineEqualAttributeOptions", element))
        elif crossing_line_equal_attribute_options is not None:
            result.parameters.append(Parameter("CrossingLineEqualAttributeOptions", crossing_line_equal_attribute_options))
        result.parameters.append(Parameter("ReportIndividualAttributeConstraintViolations", report_individual_attribute_constraint_violations))
        result.parameters.append(Parameter("CoincidenceTolerance", coincidence_tolerance))
        result.parameters.append(Parameter("AllowNoFeatureWithinSearchDistance", allow_no_feature_within_search_distance))
        result.parameters.append(Parameter("IgnoreAttributeConstraintsIfThreeOrMoreConnected", ignore_attribute_constraints_if_three_or_more_connected))
        result.parameters.append(Parameter("AllowNoFeatureWithinSearchDistanceIfConnectedOnSameSide", allow_no_feature_within_search_distance_if_connected_on_same_side))
        result.parameters.append(Parameter("AllowDisjointCandidateFeatureIfBordersAreNotCoincident", allow_disjoint_candidate_feature_if_borders_are_not_coincident))
        result.parameters.append(Parameter("IgnoreNeighborLinesWithBorderConnectionOutsideSearchDistance", ignore_neighbor_lines_with_border_connection_outside_search_distance))
        result.parameters.append(Parameter("AllowEndPointsConnectingToInteriorOfValidNeighborLine", allow_end_points_connecting_to_interior_of_valid_neighbor_line))
        result.parameters.append(Parameter("IgnoreEndPointsOfBorderingLines", ignore_end_points_of_bordering_lines))
        result.parameters.append(Parameter("AllowDisjointCandidateFeatureIfAttributeConstraintsAreFulfilled", allow_disjoint_candidate_feature_if_attribute_constraints_are_fulfilled))
        result.generate_name()
        return result

    @classmethod
    def qa_empty_not_null_text_fields_0(cls, table: BaseDataset) -> Condition:
        """
        Finds empty strings in non-nullable text fields
        """
        
        result = Condition("QaEmptyNotNullTextFields(0)")
        result.parameters.append(Parameter("table", table))
        result.generate_name()
        return result

    @classmethod
    def qa_empty_not_null_text_fields_1(cls, table: BaseDataset, not_null_text_fields: List[str]) -> Condition:
        """
        Finds empty or NULL strings in a list of text fields
        """
        
        result = Condition("QaEmptyNotNullTextFields(1)")
        result.parameters.append(Parameter("table", table))
        if type(not_null_text_fields) == list:
            for element in not_null_text_fields:
                result.parameters.append(Parameter("notNullTextFields", element))
        elif not_null_text_fields is not None:
            result.parameters.append(Parameter("notNullTextFields", not_null_text_fields))
        result.generate_name()
        return result

    @classmethod
    def qa_export_tables_0(cls, tables: List[BaseDataset], file_gdb_path: str, export_tile_ids: bool = False, export_tiles: bool = False) -> Condition:
        """
        Export 'tables' to a newly created file geodatabase
        """
        
        result = Condition("QaExportTables(0)")
        if type(tables) == list:
            for element in tables:
                result.parameters.append(Parameter("tables", element))
        elif tables is not None:
            result.parameters.append(Parameter("tables", tables))
        result.parameters.append(Parameter("fileGdbPath", file_gdb_path))
        result.parameters.append(Parameter("ExportTileIds", export_tile_ids))
        result.parameters.append(Parameter("ExportTiles", export_tiles))
        result.generate_name()
        return result

    @classmethod
    def qa_extent_0(cls, feature_class: BaseDataset, limit: float) -> Condition:
        """
        Finds all features in 'featureClass' where the largest extension of the bounding box is larger than 'limit'
        """
        
        result = Condition("QaExtent(0)")
        result.parameters.append(Parameter("featureClass", feature_class))
        result.parameters.append(Parameter("limit", limit))
        result.generate_name()
        return result

    @classmethod
    def qa_extent_1(cls, feature_class: BaseDataset, limit: float, per_part: bool) -> Condition:
        """
        Finds all features or feature parts in 'featureClass' where the largest extension of the bounding box is larger than 'limit'.
        """
        
        result = Condition("QaExtent(1)")
        result.parameters.append(Parameter("featureClass", feature_class))
        result.parameters.append(Parameter("limit", limit))
        result.parameters.append(Parameter("perPart", per_part))
        result.generate_name()
        return result

    @classmethod
    def qa_flow_logic_0(cls, polyline_class: BaseDataset) -> Condition:
        """
        Finds all (From\/To-) points in 'polylineClass', that are not coincident with exactly one From-point
        """
        
        result = Condition("QaFlowLogic(0)")
        result.parameters.append(Parameter("polylineClass", polyline_class))
        result.generate_name()
        return result

    @classmethod
    def qa_flow_logic_1(cls, polyline_classes: List[BaseDataset]) -> Condition:
        """
        Finds all (From\/To-) points in 'polylineClasses', that are not coincident with exactly one From-point
        
        Remark: The feature classes in 'polylineClasses' must have the same spatial reference.
        """
        
        result = Condition("QaFlowLogic(1)")
        if type(polyline_classes) == list:
            for element in polyline_classes:
                result.parameters.append(Parameter("polylineClasses", element))
        elif polyline_classes is not None:
            result.parameters.append(Parameter("polylineClasses", polyline_classes))
        result.generate_name()
        return result

    @classmethod
    def qa_flow_logic_2(cls, polyline_classes: List[BaseDataset], flip_expressions: List[str]) -> Condition:
        """
        Finds all (From\/To-) points in 'polylineClasses', that are not coincident with exactly one From-point. From\/To-Points are determined by 'flipExpressions'.
        
        Remark: The feature classes in 'polylineClasses' must have the same spatial reference.
        """
        
        result = Condition("QaFlowLogic(2)")
        if type(polyline_classes) == list:
            for element in polyline_classes:
                result.parameters.append(Parameter("polylineClasses", element))
        elif polyline_classes is not None:
            result.parameters.append(Parameter("polylineClasses", polyline_classes))
        if type(flip_expressions) == list:
            for element in flip_expressions:
                result.parameters.append(Parameter("flipExpressions", element))
        elif flip_expressions is not None:
            result.parameters.append(Parameter("flipExpressions", flip_expressions))
        result.generate_name()
        return result

    @classmethod
    def qa_flow_logic_3(cls, polyline_classes: List[BaseDataset], flip_expressions: List[str], allow_multiple_outgoing_lines: bool) -> Condition:
        """
        Finds all (From\/To-) points in 'polylineClasses', that are not coincident with exactly one From-point. From\/To-Points are determined by 'flipExpressions'.
        
        Remark: The feature classes in 'polylineClasses' must have the same spatial reference.
        """
        
        result = Condition("QaFlowLogic(3)")
        if type(polyline_classes) == list:
            for element in polyline_classes:
                result.parameters.append(Parameter("polylineClasses", element))
        elif polyline_classes is not None:
            result.parameters.append(Parameter("polylineClasses", polyline_classes))
        if type(flip_expressions) == list:
            for element in flip_expressions:
                result.parameters.append(Parameter("flipExpressions", element))
        elif flip_expressions is not None:
            result.parameters.append(Parameter("flipExpressions", flip_expressions))
        result.parameters.append(Parameter("allowMultipleOutgoingLines", allow_multiple_outgoing_lines))
        result.generate_name()
        return result

    @classmethod
    def qa_foreign_key_0(cls, table: BaseDataset, foreign_key_field: str, referenced_table: BaseDataset, referenced_key_field: str) -> Condition:
        """
        Finds rows that have a key value that does not refer to a value in a referenced table.
        """
        
        result = Condition("QaForeignKey(0)")
        result.parameters.append(Parameter("table", table))
        result.parameters.append(Parameter("foreignKeyField", foreign_key_field))
        result.parameters.append(Parameter("referencedTable", referenced_table))
        result.parameters.append(Parameter("referencedKeyField", referenced_key_field))
        result.generate_name()
        return result

    @classmethod
    def qa_foreign_key_1(cls, table: BaseDataset, foreign_key_fields: List[str], referenced_table: BaseDataset, referenced_key_fields: List[str]) -> Condition:
        """
        Finds rows that have a key value combination that does not refer to a value combination in a referenced table.
        """
        
        result = Condition("QaForeignKey(1)")
        result.parameters.append(Parameter("table", table))
        if type(foreign_key_fields) == list:
            for element in foreign_key_fields:
                result.parameters.append(Parameter("foreignKeyFields", element))
        elif foreign_key_fields is not None:
            result.parameters.append(Parameter("foreignKeyFields", foreign_key_fields))
        result.parameters.append(Parameter("referencedTable", referenced_table))
        if type(referenced_key_fields) == list:
            for element in referenced_key_fields:
                result.parameters.append(Parameter("referencedKeyFields", element))
        elif referenced_key_fields is not None:
            result.parameters.append(Parameter("referencedKeyFields", referenced_key_fields))
        result.generate_name()
        return result

    @classmethod
    def qa_foreign_key_2(cls, table: BaseDataset, foreign_key_fields: List[str], referenced_table: BaseDataset, referenced_key_fields: List[str], reference_is_error: bool) -> Condition:
        """
        Finds rows that have a key value combination that does not refer to a value combination in a referenced table. Optionally, an existing reference can be treated as an error.
        """
        
        result = Condition("QaForeignKey(2)")
        result.parameters.append(Parameter("table", table))
        if type(foreign_key_fields) == list:
            for element in foreign_key_fields:
                result.parameters.append(Parameter("foreignKeyFields", element))
        elif foreign_key_fields is not None:
            result.parameters.append(Parameter("foreignKeyFields", foreign_key_fields))
        result.parameters.append(Parameter("referencedTable", referenced_table))
        if type(referenced_key_fields) == list:
            for element in referenced_key_fields:
                result.parameters.append(Parameter("referencedKeyFields", element))
        elif referenced_key_fields is not None:
            result.parameters.append(Parameter("referencedKeyFields", referenced_key_fields))
        result.parameters.append(Parameter("referenceIsError", reference_is_error))
        result.generate_name()
        return result

    @classmethod
    def qa_full_coincidence_0(cls, feature_class: BaseDataset, reference: BaseDataset, near: float, is3_d: bool, ignore_neighbor_conditions: List[str] = None) -> Condition:
        """
        Finds all line parts in 'featureClass' that are further than 'near' from any feature of 'reference'
        
        Remark: The feature classes in 'featureClass' and 'reference' must have the same spatial reference.
        """
        
        result = Condition("QaFullCoincidence(0)")
        result.parameters.append(Parameter("featureClass", feature_class))
        result.parameters.append(Parameter("reference", reference))
        result.parameters.append(Parameter("near", near))
        result.parameters.append(Parameter("is3D", is3_d))
        if type(ignore_neighbor_conditions) == list:
            for element in ignore_neighbor_conditions:
                result.parameters.append(Parameter("IgnoreNeighborConditions", element))
        elif ignore_neighbor_conditions is not None:
            result.parameters.append(Parameter("IgnoreNeighborConditions", ignore_neighbor_conditions))
        result.generate_name()
        return result

    @classmethod
    def qa_full_coincidence_1(cls, feature_class: BaseDataset, reference: BaseDataset, near: float, is3_d: bool, tile_size: float, ignore_neighbor_conditions: List[str] = None) -> Condition:
        """
        Finds all line parts in 'featureClass' that are further than 'near' from any feature of 'reference'
        
        Remark: The feature classes in 'featureClass' and 'reference' must have the same spatial reference.
        """
        
        result = Condition("QaFullCoincidence(1)")
        result.parameters.append(Parameter("featureClass", feature_class))
        result.parameters.append(Parameter("reference", reference))
        result.parameters.append(Parameter("near", near))
        result.parameters.append(Parameter("is3D", is3_d))
        result.parameters.append(Parameter("tileSize", tile_size))
        if type(ignore_neighbor_conditions) == list:
            for element in ignore_neighbor_conditions:
                result.parameters.append(Parameter("IgnoreNeighborConditions", element))
        elif ignore_neighbor_conditions is not None:
            result.parameters.append(Parameter("IgnoreNeighborConditions", ignore_neighbor_conditions))
        result.generate_name()
        return result

    @classmethod
    def qa_full_coincidence_2(cls, feature_class: BaseDataset, references: List[BaseDataset], near: float, is3_d: bool, ignore_neighbor_conditions: List[str] = None) -> Condition:
        """
        Finds all line parts in 'featureClass' that are further than 'near' from any feature of 'references'
        
        Remark: All feature classes in 'featureClass' and 'references' must have the same spatial reference.
        """
        
        result = Condition("QaFullCoincidence(2)")
        result.parameters.append(Parameter("featureClass", feature_class))
        if type(references) == list:
            for element in references:
                result.parameters.append(Parameter("references", element))
        elif references is not None:
            result.parameters.append(Parameter("references", references))
        result.parameters.append(Parameter("near", near))
        result.parameters.append(Parameter("is3D", is3_d))
        if type(ignore_neighbor_conditions) == list:
            for element in ignore_neighbor_conditions:
                result.parameters.append(Parameter("IgnoreNeighborConditions", element))
        elif ignore_neighbor_conditions is not None:
            result.parameters.append(Parameter("IgnoreNeighborConditions", ignore_neighbor_conditions))
        result.generate_name()
        return result

    @classmethod
    def qa_full_coincidence_3(cls, feature_class: BaseDataset, references: List[BaseDataset], near: float, is3_d: bool, tile_size: float, ignore_neighbor_conditions: List[str] = None) -> Condition:
        """
        Finds all line parts in 'featureClass' that are further than 'near' from any feature of 'references'
        
        Remark: All feature classes in 'featureClass' and 'references' must have the same spatial reference.
        """
        
        result = Condition("QaFullCoincidence(3)")
        result.parameters.append(Parameter("featureClass", feature_class))
        if type(references) == list:
            for element in references:
                result.parameters.append(Parameter("references", element))
        elif references is not None:
            result.parameters.append(Parameter("references", references))
        result.parameters.append(Parameter("near", near))
        result.parameters.append(Parameter("is3D", is3_d))
        result.parameters.append(Parameter("tileSize", tile_size))
        if type(ignore_neighbor_conditions) == list:
            for element in ignore_neighbor_conditions:
                result.parameters.append(Parameter("IgnoreNeighborConditions", element))
        elif ignore_neighbor_conditions is not None:
            result.parameters.append(Parameter("IgnoreNeighborConditions", ignore_neighbor_conditions))
        result.generate_name()
        return result

    @classmethod
    def qa_full_coincidence_4(cls, feature_class: BaseDataset, references: List[BaseDataset], near: float, ignore_neighbor_conditions: List[str] = None) -> Condition:
        """
        Finds all line parts in 'featureClass' that are further than 'near' from any feature of 'references'
        
        Remark: All feature classes in 'featureClass' and 'references' must have the same spatial reference.
        """
        
        result = Condition("QaFullCoincidence(4)")
        result.parameters.append(Parameter("featureClass", feature_class))
        if type(references) == list:
            for element in references:
                result.parameters.append(Parameter("references", element))
        elif references is not None:
            result.parameters.append(Parameter("references", references))
        result.parameters.append(Parameter("near", near))
        if type(ignore_neighbor_conditions) == list:
            for element in ignore_neighbor_conditions:
                result.parameters.append(Parameter("IgnoreNeighborConditions", element))
        elif ignore_neighbor_conditions is not None:
            result.parameters.append(Parameter("IgnoreNeighborConditions", ignore_neighbor_conditions))
        result.generate_name()
        return result

    @classmethod
    def qa_full_coincidence_5(cls, feature_class: BaseDataset, references: List[BaseDataset], near: float, tile_size: float, ignore_neighbor_conditions: List[str] = None) -> Condition:
        """
        Finds all line parts in 'featureClass' that are further than 'near' from any feature of 'references'
        
        Remark: All feature classes in 'featureClass' and 'references' must have the same spatial reference.
        """
        
        result = Condition("QaFullCoincidence(5)")
        result.parameters.append(Parameter("featureClass", feature_class))
        if type(references) == list:
            for element in references:
                result.parameters.append(Parameter("references", element))
        elif references is not None:
            result.parameters.append(Parameter("references", references))
        result.parameters.append(Parameter("near", near))
        result.parameters.append(Parameter("tileSize", tile_size))
        if type(ignore_neighbor_conditions) == list:
            for element in ignore_neighbor_conditions:
                result.parameters.append(Parameter("IgnoreNeighborConditions", element))
        elif ignore_neighbor_conditions is not None:
            result.parameters.append(Parameter("IgnoreNeighborConditions", ignore_neighbor_conditions))
        result.generate_name()
        return result

    @classmethod
    def qa_gdb_constraint_0(cls, table: BaseDataset) -> Condition:
        """
        Finds all rows in 'table' that do not fulfill the attribute rules that are defined in the geodatabase
        
        Remark: IAttributeRule.Validate() is used to check the rows.
        """
        
        result = Condition("QaGdbConstraint(0)")
        result.parameters.append(Parameter("table", table))
        result.generate_name()
        return result

    @classmethod
    def qa_gdb_release_0(cls, table: BaseDataset, expected_version: str) -> Condition:
        """
        Verifies that the geodatabase release for a given table corresponds to a specified version.
        """
        
        result = Condition("QaGdbRelease(0)")
        result.parameters.append(Parameter("table", table))
        result.parameters.append(Parameter("expectedVersion", expected_version))
        result.generate_name()
        return result

    @classmethod
    def qa_gdb_release_1(cls, table: BaseDataset, minimum_version: str, maximum_version: str) -> Condition:
        """
        Verifies that the geodatabase release for a given table corresponds to a specified version range. The version range may be open on one side, by specifying only one of minimumVersion and maximumVersion.
        """
        
        result = Condition("QaGdbRelease(1)")
        result.parameters.append(Parameter("table", table))
        result.parameters.append(Parameter("minimumVersion", minimum_version))
        result.parameters.append(Parameter("maximumVersion", maximum_version))
        result.generate_name()
        return result

    @classmethod
    def qa_gdb_topology_1(cls, feature_classes: List[BaseDataset]) -> Condition:
        """
        Finds all geodatabase topology errors in the topologies referenced by 'featureClasses'.
        
        Remark: If a topology has not been previously validated, the dirty areas are reported as issues.
        The reported issues are copies of the error features of the topology's error features.
        """
        
        result = Condition("QaGdbTopology(1)")
        if type(feature_classes) == list:
            for element in feature_classes:
                result.parameters.append(Parameter("featureClasses", element))
        elif feature_classes is not None:
            result.parameters.append(Parameter("featureClasses", feature_classes))
        result.generate_name()
        return result

    @classmethod
    def qa_geometry_constraint_0(cls, feature_class: BaseDataset, geometry_constraint: str, per_part: bool) -> Condition:
        """
        Finds all features in 'featureClass' whose geometry (or geometry parts) do not fulfill 'geometryConstraint'
        """
        
        result = Condition("QaGeometryConstraint(0)")
        result.parameters.append(Parameter("featureClass", feature_class))
        result.parameters.append(Parameter("geometryConstraint", geometry_constraint))
        result.parameters.append(Parameter("perPart", per_part))
        result.generate_name()
        return result

    @classmethod
    def qa_group_connected_0(cls, polyline_class: BaseDataset, group_by: List[str], allowed_shape: ShapeAllowed, report_individual_gaps: bool = False, ignore_gaps_longer_than: float = -1, complete_groups_outside_test_area: bool = False) -> Condition:
        """
        Find errors in checking if polylines of 'polylineClass' with same attributes are connected. Reports disjoint line groups with ErrorReporting.ReferToFirstPart.
        """
        
        result = Condition("QaGroupConnected(0)")
        result.parameters.append(Parameter("polylineClass", polyline_class))
        if type(group_by) == list:
            for element in group_by:
                result.parameters.append(Parameter("groupBy", element))
        elif group_by is not None:
            result.parameters.append(Parameter("groupBy", group_by))
        result.parameters.append(Parameter("allowedShape", allowed_shape))
        result.parameters.append(Parameter("ReportIndividualGaps", report_individual_gaps))
        result.parameters.append(Parameter("IgnoreGapsLongerThan", ignore_gaps_longer_than))
        result.parameters.append(Parameter("CompleteGroupsOutsideTestArea", complete_groups_outside_test_area))
        result.generate_name()
        return result

    @classmethod
    def qa_group_connected_1(cls, polyline_classes: List[BaseDataset], group_by: List[str], value_separator: str, allowed_shape: ShapeAllowed, error_reporting: GroupErrorReporting, minimum_error_connection_line_length: float, report_individual_gaps: bool = False, ignore_gaps_longer_than: float = -1, complete_groups_outside_test_area: bool = False) -> Condition:
        """
        Find errors in checking if polylines of 'polylineClasses' with same attributes are connected
        """
        
        result = Condition("QaGroupConnected(1)")
        if type(polyline_classes) == list:
            for element in polyline_classes:
                result.parameters.append(Parameter("polylineClasses", element))
        elif polyline_classes is not None:
            result.parameters.append(Parameter("polylineClasses", polyline_classes))
        if type(group_by) == list:
            for element in group_by:
                result.parameters.append(Parameter("groupBy", element))
        elif group_by is not None:
            result.parameters.append(Parameter("groupBy", group_by))
        result.parameters.append(Parameter("valueSeparator", value_separator))
        result.parameters.append(Parameter("allowedShape", allowed_shape))
        result.parameters.append(Parameter("errorReporting", error_reporting))
        result.parameters.append(Parameter("minimumErrorConnectionLineLength", minimum_error_connection_line_length))
        result.parameters.append(Parameter("ReportIndividualGaps", report_individual_gaps))
        result.parameters.append(Parameter("IgnoreGapsLongerThan", ignore_gaps_longer_than))
        result.parameters.append(Parameter("CompleteGroupsOutsideTestArea", complete_groups_outside_test_area))
        result.generate_name()
        return result

    @classmethod
    def qa_group_constraints_0(cls, table: BaseDataset, group_by_expression: str, distinct_expression: str, max_distinct_count: int, limit_to_tested_rows: bool, exists_row_group_filters: List[str] = None) -> Condition:
        """
        Checks if the number of distinct values of an expression (which may be a single field or a more complex expression involving field concatenation, value translation, substring extraction etc.) within groups defined by a 'group by' expression (which also may be a single field or a more complex expression on fields) does not exceed an allowed maximum value.
        """
        
        result = Condition("QaGroupConstraints(0)")
        result.parameters.append(Parameter("table", table))
        result.parameters.append(Parameter("groupByExpression", group_by_expression))
        result.parameters.append(Parameter("distinctExpression", distinct_expression))
        result.parameters.append(Parameter("maxDistinctCount", max_distinct_count))
        result.parameters.append(Parameter("limitToTestedRows", limit_to_tested_rows))
        if type(exists_row_group_filters) == list:
            for element in exists_row_group_filters:
                result.parameters.append(Parameter("ExistsRowGroupFilters", element))
        elif exists_row_group_filters is not None:
            result.parameters.append(Parameter("ExistsRowGroupFilters", exists_row_group_filters))
        result.generate_name()
        return result

    @classmethod
    def qa_group_constraints_1(cls, tables: List[BaseDataset], group_by_expressions: List[str], distinct_expressions: List[str], max_distinct_count: int, limit_to_tested_rows: bool, exists_row_group_filters: List[str] = None) -> Condition:
        """
        Checks if the number of distinct values of an expression (which may be a single field or a more complex expression involving field concatenation, value translation, substring extraction etc.) within groups defined by a 'group by' expression (which also may be a single field or a more complex expression on fields) does not exceed an allowed maximum value.
        
        Example:
        Table A with Field 'KeyA' with a row KeyA = 5
        Table B with Field 'KeyB' with a row KeyB = 5
        
        Test with QaGroupConstraint({A,B}, {KeyA,KeyB}, {'name A', 'name B'}, 1, false).
        
        The row of table A and the row of table B belong to the same group, 5, evaluated by the corresponding groupByExpressions. In this group there are 2 distinct values, 'name A' from the row in table A and 'name B' from the row in table B. So the group 5 will be reported as error, because only 1  distinct value (see maxDistinctCount) is allowed.
        
        
        """
        
        result = Condition("QaGroupConstraints(1)")
        if type(tables) == list:
            for element in tables:
                result.parameters.append(Parameter("tables", element))
        elif tables is not None:
            result.parameters.append(Parameter("tables", tables))
        if type(group_by_expressions) == list:
            for element in group_by_expressions:
                result.parameters.append(Parameter("groupByExpressions", element))
        elif group_by_expressions is not None:
            result.parameters.append(Parameter("groupByExpressions", group_by_expressions))
        if type(distinct_expressions) == list:
            for element in distinct_expressions:
                result.parameters.append(Parameter("distinctExpressions", element))
        elif distinct_expressions is not None:
            result.parameters.append(Parameter("distinctExpressions", distinct_expressions))
        result.parameters.append(Parameter("maxDistinctCount", max_distinct_count))
        result.parameters.append(Parameter("limitToTestedRows", limit_to_tested_rows))
        if type(exists_row_group_filters) == list:
            for element in exists_row_group_filters:
                result.parameters.append(Parameter("ExistsRowGroupFilters", element))
        elif exists_row_group_filters is not None:
            result.parameters.append(Parameter("ExistsRowGroupFilters", exists_row_group_filters))
        result.generate_name()
        return result

    @classmethod
    def qa_group_constraints_2(cls, tables: List[BaseDataset], group_by_expressions: List[str], distinct_expressions: List[str], min_distinct_count: int, max_distinct_count: int, limit_to_tested_rows: bool, exists_row_group_filters: List[str] = None) -> Condition:
        """
        Checks if the number of distinct values of an expression (which may be a single field or a more complex expression involving field concatenation, value translation, substring extraction etc.) within groups defined by a 'group by' expression (which also may be a single field or a more complex expression on fields) does not exceed an allowed maximum value.
        
        Example:
        Table A with Field 'KeyA' with a row KeyA = 5
        Table B with Field 'KeyB' with a row KeyB = 5
        
        Test with QaGroupConstraint({A,B}, {KeyA,KeyB}, {'name A', 'name B'}, 1, false).
        
        The row of table A and the row of table B belong to the same group, 5, evaluated by the corresponding groupByExpressions. In this group there are 2 distinct values, 'name A' from the row in table A and 'name B' from the row in table B. So the group 5 will be reported as error, because only 1  distinct value (see maxDistinctCount) is allowed.
        
        
        """
        
        result = Condition("QaGroupConstraints(2)")
        if type(tables) == list:
            for element in tables:
                result.parameters.append(Parameter("tables", element))
        elif tables is not None:
            result.parameters.append(Parameter("tables", tables))
        if type(group_by_expressions) == list:
            for element in group_by_expressions:
                result.parameters.append(Parameter("groupByExpressions", element))
        elif group_by_expressions is not None:
            result.parameters.append(Parameter("groupByExpressions", group_by_expressions))
        if type(distinct_expressions) == list:
            for element in distinct_expressions:
                result.parameters.append(Parameter("distinctExpressions", element))
        elif distinct_expressions is not None:
            result.parameters.append(Parameter("distinctExpressions", distinct_expressions))
        result.parameters.append(Parameter("minDistinctCount", min_distinct_count))
        result.parameters.append(Parameter("maxDistinctCount", max_distinct_count))
        result.parameters.append(Parameter("limitToTestedRows", limit_to_tested_rows))
        if type(exists_row_group_filters) == list:
            for element in exists_row_group_filters:
                result.parameters.append(Parameter("ExistsRowGroupFilters", element))
        elif exists_row_group_filters is not None:
            result.parameters.append(Parameter("ExistsRowGroupFilters", exists_row_group_filters))
        result.generate_name()
        return result

    @classmethod
    def qa_horizontal_segments_0(cls, feature_class: BaseDataset, limit: float, tolerance: float) -> Condition:
        """
        Finds almost horizontal segments: Find segments with a slope angle smaller than 'limit', but larger than 'tolerance'.
        """
        
        result = Condition("QaHorizontalSegments(0)")
        result.parameters.append(Parameter("featureClass", feature_class))
        result.parameters.append(Parameter("limit", limit))
        result.parameters.append(Parameter("tolerance", tolerance))
        result.generate_name()
        return result

    @classmethod
    def qa_interior_intersects_other_0(cls, feature_class: BaseDataset, related_class: BaseDataset, valid_intersection_geometry_constraint: str = None) -> Condition:
        """
        Finds features in 'relatedClass' that have an interior intersection with a feature in 'featureClass'
        """
        
        result = Condition("QaInteriorIntersectsOther(0)")
        result.parameters.append(Parameter("featureClass", feature_class))
        result.parameters.append(Parameter("relatedClass", related_class))
        result.parameters.append(Parameter("ValidIntersectionGeometryConstraint", valid_intersection_geometry_constraint))
        result.generate_name()
        return result

    @classmethod
    def qa_interior_intersects_other_1(cls, feature_class: BaseDataset, related_class: BaseDataset, constraint: str, valid_intersection_geometry_constraint: str = None) -> Condition:
        """
        Finds pairs of features in 'featureClass' vs. 'relatedClass' that have an interior intersection, and for which a given constraint is not fulfilled.
        """
        
        result = Condition("QaInteriorIntersectsOther(1)")
        result.parameters.append(Parameter("featureClass", feature_class))
        result.parameters.append(Parameter("relatedClass", related_class))
        result.parameters.append(Parameter("constraint", constraint))
        result.parameters.append(Parameter("ValidIntersectionGeometryConstraint", valid_intersection_geometry_constraint))
        result.generate_name()
        return result

    @classmethod
    def qa_interior_intersects_other_2(cls, feature_classes: List[BaseDataset], related_classes: List[BaseDataset], valid_intersection_geometry_constraint: str = None) -> Condition:
        """
        Finds pairs of features in 'featureClasses' vs. 'relatedClasses' that have an interior intersection.
        """
        
        result = Condition("QaInteriorIntersectsOther(2)")
        if type(feature_classes) == list:
            for element in feature_classes:
                result.parameters.append(Parameter("featureClasses", element))
        elif feature_classes is not None:
            result.parameters.append(Parameter("featureClasses", feature_classes))
        if type(related_classes) == list:
            for element in related_classes:
                result.parameters.append(Parameter("relatedClasses", element))
        elif related_classes is not None:
            result.parameters.append(Parameter("relatedClasses", related_classes))
        result.parameters.append(Parameter("ValidIntersectionGeometryConstraint", valid_intersection_geometry_constraint))
        result.generate_name()
        return result

    @classmethod
    def qa_interior_intersects_other_3(cls, feature_classes: List[BaseDataset], related_classes: List[BaseDataset], constraint: str, valid_intersection_geometry_constraint: str = None) -> Condition:
        """
        Finds pairs of features in 'featureClasses' vs. 'relatedClasses' that have an interior intersection, and for which a given constraint is not fulfilled.
        """
        
        result = Condition("QaInteriorIntersectsOther(3)")
        if type(feature_classes) == list:
            for element in feature_classes:
                result.parameters.append(Parameter("featureClasses", element))
        elif feature_classes is not None:
            result.parameters.append(Parameter("featureClasses", feature_classes))
        if type(related_classes) == list:
            for element in related_classes:
                result.parameters.append(Parameter("relatedClasses", element))
        elif related_classes is not None:
            result.parameters.append(Parameter("relatedClasses", related_classes))
        result.parameters.append(Parameter("constraint", constraint))
        result.parameters.append(Parameter("ValidIntersectionGeometryConstraint", valid_intersection_geometry_constraint))
        result.generate_name()
        return result

    @classmethod
    def qa_interior_intersects_self_0(cls, feature_class: BaseDataset, valid_intersection_geometry_constraint: str = None) -> Condition:
        """
        Finds all pairs of features in a feature class with intersecting interiors.
        """
        
        result = Condition("QaInteriorIntersectsSelf(0)")
        result.parameters.append(Parameter("featureClass", feature_class))
        result.parameters.append(Parameter("ValidIntersectionGeometryConstraint", valid_intersection_geometry_constraint))
        result.generate_name()
        return result

    @classmethod
    def qa_interior_intersects_self_1(cls, feature_class: BaseDataset, constraint: str, valid_intersection_geometry_constraint: str = None) -> Condition:
        """
        Finds all pairs of features in a feature class with intersecting interiors, and for which a given constraint is not fulfilled.
        """
        
        result = Condition("QaInteriorIntersectsSelf(1)")
        result.parameters.append(Parameter("featureClass", feature_class))
        result.parameters.append(Parameter("constraint", constraint))
        result.parameters.append(Parameter("ValidIntersectionGeometryConstraint", valid_intersection_geometry_constraint))
        result.generate_name()
        return result

    @classmethod
    def qa_interior_intersects_self_2(cls, feature_classes: List[BaseDataset], valid_intersection_geometry_constraint: str = None) -> Condition:
        """
        Finds all pairs of features in a list of feature classes with intersecting interiors.
        """
        
        result = Condition("QaInteriorIntersectsSelf(2)")
        if type(feature_classes) == list:
            for element in feature_classes:
                result.parameters.append(Parameter("featureClasses", element))
        elif feature_classes is not None:
            result.parameters.append(Parameter("featureClasses", feature_classes))
        result.parameters.append(Parameter("ValidIntersectionGeometryConstraint", valid_intersection_geometry_constraint))
        result.generate_name()
        return result

    @classmethod
    def qa_interior_intersects_self_3(cls, feature_classes: List[BaseDataset], constraint: str, valid_intersection_geometry_constraint: str = None) -> Condition:
        """
        Finds all pairs of features in a list of feature classes with intersecting interiors, and for which a given constraint is not fulfilled.
        """
        
        result = Condition("QaInteriorIntersectsSelf(3)")
        if type(feature_classes) == list:
            for element in feature_classes:
                result.parameters.append(Parameter("featureClasses", element))
        elif feature_classes is not None:
            result.parameters.append(Parameter("featureClasses", feature_classes))
        result.parameters.append(Parameter("constraint", constraint))
        result.parameters.append(Parameter("ValidIntersectionGeometryConstraint", valid_intersection_geometry_constraint))
        result.generate_name()
        return result

    @classmethod
    def qa_interior_intersects_self_4(cls, feature_classes: List[BaseDataset], constraint: str, report_intersections_as_multipart: bool, valid_intersection_geometry_constraint: str = None) -> Condition:
        """
        Finds all pairs of features in a list of feature classes with intersecting interiors, and for which a given constraint is not fulfilled. Optionally, all intersections between two features can be reported as one error with multipart error geometry.
        """
        
        result = Condition("QaInteriorIntersectsSelf(4)")
        if type(feature_classes) == list:
            for element in feature_classes:
                result.parameters.append(Parameter("featureClasses", element))
        elif feature_classes is not None:
            result.parameters.append(Parameter("featureClasses", feature_classes))
        result.parameters.append(Parameter("constraint", constraint))
        result.parameters.append(Parameter("reportIntersectionsAsMultipart", report_intersections_as_multipart))
        result.parameters.append(Parameter("ValidIntersectionGeometryConstraint", valid_intersection_geometry_constraint))
        result.generate_name()
        return result

    @classmethod
    def qa_interior_rings_0(cls, polygon_class: BaseDataset, maximum_interior_ring_count: int, ignore_inner_rings_larger_than: float = -1, report_individual_rings: bool = False, report_only_smallest_rings_exceeding_maximum_count: bool = True) -> Condition:
        """
        Finds interior rings of polygon features that exceed a given maximum ring count. Optionally, only inner rings that are smaller than a specified area are reported.
        """
        
        result = Condition("QaInteriorRings(0)")
        result.parameters.append(Parameter("polygonClass", polygon_class))
        result.parameters.append(Parameter("maximumInteriorRingCount", maximum_interior_ring_count))
        result.parameters.append(Parameter("IgnoreInnerRingsLargerThan", ignore_inner_rings_larger_than))
        result.parameters.append(Parameter("ReportIndividualRings", report_individual_rings))
        result.parameters.append(Parameter("ReportOnlySmallestRingsExceedingMaximumCount", report_only_smallest_rings_exceeding_maximum_count))
        result.generate_name()
        return result

    @classmethod
    def qa_intersection_matrix_other_0(cls, feature_classes: List[BaseDataset], related_classes: List[BaseDataset], intersection_matrix: str) -> Condition:
        """
        Finds all features in 'featureClasses' that have a given spatial relationship with features in 'relatedClasses'. The spatial relationship of the error cases is defined by a 9IM intersection matrix.
        
        Remark: All feature classes in 'featureClasses' and 'relatedClasses' must have the same spatial reference.
        """
        
        result = Condition("QaIntersectionMatrixOther(0)")
        if type(feature_classes) == list:
            for element in feature_classes:
                result.parameters.append(Parameter("featureClasses", element))
        elif feature_classes is not None:
            result.parameters.append(Parameter("featureClasses", feature_classes))
        if type(related_classes) == list:
            for element in related_classes:
                result.parameters.append(Parameter("relatedClasses", element))
        elif related_classes is not None:
            result.parameters.append(Parameter("relatedClasses", related_classes))
        result.parameters.append(Parameter("intersectionMatrix", intersection_matrix))
        result.generate_name()
        return result

    @classmethod
    def qa_intersection_matrix_other_1(cls, feature_classes: List[BaseDataset], related_classes: List[BaseDataset], intersection_matrix: str, constraint: str) -> Condition:
        """
        Finds all features in 'featureClasses' that have a given spatial relationship with features in 'relatedClasses', and for which a given constraint is not fulfilled. The spatial relationship of the error cases is defined by a 9IM intersection matrix.
        
        Remark: All feature classes in 'featureClasses' and 'relatedClasses' must have the same spatial reference.
        """
        
        result = Condition("QaIntersectionMatrixOther(1)")
        if type(feature_classes) == list:
            for element in feature_classes:
                result.parameters.append(Parameter("featureClasses", element))
        elif feature_classes is not None:
            result.parameters.append(Parameter("featureClasses", feature_classes))
        if type(related_classes) == list:
            for element in related_classes:
                result.parameters.append(Parameter("relatedClasses", element))
        elif related_classes is not None:
            result.parameters.append(Parameter("relatedClasses", related_classes))
        result.parameters.append(Parameter("intersectionMatrix", intersection_matrix))
        result.parameters.append(Parameter("constraint", constraint))
        result.generate_name()
        return result

    @classmethod
    def qa_intersection_matrix_other_2(cls, feature_class: BaseDataset, related_class: BaseDataset, intersection_matrix: str) -> Condition:
        """
        Finds all features in 'featureClass' that have a given spatial relationship with features in 'relatedClass'. The spatial relationship of the error cases is defined by a 9IM intersection matrix.
        
        Remark: The feature classes in 'featureClass' and 'relatedClass' must have the same spatial reference.
        """
        
        result = Condition("QaIntersectionMatrixOther(2)")
        result.parameters.append(Parameter("featureClass", feature_class))
        result.parameters.append(Parameter("relatedClass", related_class))
        result.parameters.append(Parameter("intersectionMatrix", intersection_matrix))
        result.generate_name()
        return result

    @classmethod
    def qa_intersection_matrix_other_3(cls, feature_class: BaseDataset, related_class: BaseDataset, intersection_matrix: str, constraint: str) -> Condition:
        """
        Finds all features in 'featureClass' that have a given spatial relationship with features in 'relatedClass', and for which a given constraint is not fulfilled. The spatial relationship of the error cases is defined by a 9IM intersection matrix.
        
        Remark: The feature classes in 'featureClass' and 'relatedClass' must have the same spatial reference.
        """
        
        result = Condition("QaIntersectionMatrixOther(3)")
        result.parameters.append(Parameter("featureClass", feature_class))
        result.parameters.append(Parameter("relatedClass", related_class))
        result.parameters.append(Parameter("intersectionMatrix", intersection_matrix))
        result.parameters.append(Parameter("constraint", constraint))
        result.generate_name()
        return result

    @classmethod
    def qa_intersection_matrix_other_4(cls, feature_classes: List[BaseDataset], related_classes: List[BaseDataset], intersection_matrix: str, constraint: str, valid_intersection_dimensions: str) -> Condition:
        """
        Finds all features in 'featureClass' that have a given spatial relationship with features in 'relatedClass', and for which a given constraint is not fulfilled. The spatial relationship of the error cases is defined by a 9IM intersection matrix. A list of valid intersection dimensions can be specified. Any parts of the intersection geometry (according to the 9IM intersection matrix) with a dimension that is included in this list are not reported as errors.
        
        Remark: The feature classes in 'featureClass' and 'relatedClass' must have the same spatial reference.
        """
        
        result = Condition("QaIntersectionMatrixOther(4)")
        if type(feature_classes) == list:
            for element in feature_classes:
                result.parameters.append(Parameter("featureClasses", element))
        elif feature_classes is not None:
            result.parameters.append(Parameter("featureClasses", feature_classes))
        if type(related_classes) == list:
            for element in related_classes:
                result.parameters.append(Parameter("relatedClasses", element))
        elif related_classes is not None:
            result.parameters.append(Parameter("relatedClasses", related_classes))
        result.parameters.append(Parameter("intersectionMatrix", intersection_matrix))
        result.parameters.append(Parameter("constraint", constraint))
        result.parameters.append(Parameter("validIntersectionDimensions", valid_intersection_dimensions))
        result.generate_name()
        return result

    @classmethod
    def qa_intersection_matrix_self_0(cls, feature_classes: List[BaseDataset], intersection_matrix: str) -> Condition:
        """
        Finds all features in 'featureClasses' that have a given spatial relationship with other features in 'featureClasses' (including the feature class of the feature to be tested). The spatial relationship of the error cases is defined by a 9IM intersection matrix.
        
        Remark: The feature classes in 'featureClasses' must have the same spatial reference.
        """
        
        result = Condition("QaIntersectionMatrixSelf(0)")
        if type(feature_classes) == list:
            for element in feature_classes:
                result.parameters.append(Parameter("featureClasses", element))
        elif feature_classes is not None:
            result.parameters.append(Parameter("featureClasses", feature_classes))
        result.parameters.append(Parameter("intersectionMatrix", intersection_matrix))
        result.generate_name()
        return result

    @classmethod
    def qa_intersection_matrix_self_1(cls, feature_classes: List[BaseDataset], intersection_matrix: str, constraint: str) -> Condition:
        """
        Finds all features in 'featureClasses' that have a given spatial relationship with other features in 'featureClasses' (including the feature class of the feature to be tested), and for which a given constraint is not fulfilled. The spatial relationship of the error cases is defined by a 9IM intersection matrix.
        
        Remark: The feature classes in 'featureClasses' must have the same spatial reference.
        """
        
        result = Condition("QaIntersectionMatrixSelf(1)")
        if type(feature_classes) == list:
            for element in feature_classes:
                result.parameters.append(Parameter("featureClasses", element))
        elif feature_classes is not None:
            result.parameters.append(Parameter("featureClasses", feature_classes))
        result.parameters.append(Parameter("intersectionMatrix", intersection_matrix))
        result.parameters.append(Parameter("constraint", constraint))
        result.generate_name()
        return result

    @classmethod
    def qa_intersection_matrix_self_2(cls, feature_class: BaseDataset, intersection_matrix: str) -> Condition:
        """
        Finds all features in 'featureClass' that have a given spatial relationship with other features in 'featureClass'. The spatial relationship of the error cases is defined by a 9IM intersection matrix.
        """
        
        result = Condition("QaIntersectionMatrixSelf(2)")
        result.parameters.append(Parameter("featureClass", feature_class))
        result.parameters.append(Parameter("intersectionMatrix", intersection_matrix))
        result.generate_name()
        return result

    @classmethod
    def qa_intersection_matrix_self_3(cls, feature_class: BaseDataset, intersection_matrix: str, constraint: str) -> Condition:
        """
        Finds all features in 'featureClass' that have a given spatial relationship with other features in 'featureClass', and for which a given constraint is not fulfilled. The spatial relationship of the error cases is defined by a 9IM intersection matrix.
        """
        
        result = Condition("QaIntersectionMatrixSelf(3)")
        result.parameters.append(Parameter("featureClass", feature_class))
        result.parameters.append(Parameter("intersectionMatrix", intersection_matrix))
        result.parameters.append(Parameter("constraint", constraint))
        result.generate_name()
        return result

    @classmethod
    def qa_intersection_matrix_self_4(cls, feature_classes: List[BaseDataset], intersection_matrix: str, constraint: str, valid_intersection_dimensions: str) -> Condition:
        """
        Finds all features in 'featureClass' that have a given spatial relationship with other features in 'featureClass', and for which a given constraint is not fulfilled. The spatial relationship of the error cases is defined by a 9IM intersection matrix. A list of valid intersection dimensions can be specified. Any parts of the intersection geometry (according to the 9IM intersection matrix) with a dimension that is included in this list are not reported as errors.
        """
        
        result = Condition("QaIntersectionMatrixSelf(4)")
        if type(feature_classes) == list:
            for element in feature_classes:
                result.parameters.append(Parameter("featureClasses", element))
        elif feature_classes is not None:
            result.parameters.append(Parameter("featureClasses", feature_classes))
        result.parameters.append(Parameter("intersectionMatrix", intersection_matrix))
        result.parameters.append(Parameter("constraint", constraint))
        result.parameters.append(Parameter("validIntersectionDimensions", valid_intersection_dimensions))
        result.generate_name()
        return result

    @classmethod
    def qa_intersects_other_0(cls, intersected: List[BaseDataset], intersecting: List[BaseDataset], report_intersections_as_multipart: bool = True, valid_intersection_geometry_constraint: str = None) -> Condition:
        """
        Finds all features in 'intersectingClasses' that intersect by any features of 'intersectedClasses'
        
        Remark: All feature classes in 'intersectedClasses' and 'intersectingClasses' must have the same spatial reference.
        """
        
        result = Condition("QaIntersectsOther(0)")
        if type(intersected) == list:
            for element in intersected:
                result.parameters.append(Parameter("intersected", element))
        elif intersected is not None:
            result.parameters.append(Parameter("intersected", intersected))
        if type(intersecting) == list:
            for element in intersecting:
                result.parameters.append(Parameter("intersecting", element))
        elif intersecting is not None:
            result.parameters.append(Parameter("intersecting", intersecting))
        result.parameters.append(Parameter("ReportIntersectionsAsMultipart", report_intersections_as_multipart))
        result.parameters.append(Parameter("ValidIntersectionGeometryConstraint", valid_intersection_geometry_constraint))
        result.generate_name()
        return result

    @classmethod
    def qa_intersects_other_1(cls, intersected: BaseDataset, intersecting: BaseDataset, report_intersections_as_multipart: bool = True, valid_intersection_geometry_constraint: str = None) -> Condition:
        """
        Finds all features in 'intersectingClass' that intersect by any features of 'intersectedClass'
        
        Remark: The feature classes in 'intersectedClass' and 'intersectingClass' must have the same spatial reference.
        """
        
        result = Condition("QaIntersectsOther(1)")
        result.parameters.append(Parameter("intersected", intersected))
        result.parameters.append(Parameter("intersecting", intersecting))
        result.parameters.append(Parameter("ReportIntersectionsAsMultipart", report_intersections_as_multipart))
        result.parameters.append(Parameter("ValidIntersectionGeometryConstraint", valid_intersection_geometry_constraint))
        result.generate_name()
        return result

    @classmethod
    def qa_intersects_other_2(cls, intersected_classes: List[BaseDataset], intersecting_classes: List[BaseDataset], valid_relation_constraint: str, report_intersections_as_multipart: bool = True, valid_intersection_geometry_constraint: str = None) -> Condition:
        """
        Finds all features in 'intersectingClasses' that intersect by any features of 'intersectedClasses', and for which a given constraint is not fulfilled.
        
        Remark: All feature classes in 'intersectedClasses' and 'intersectingClasses' must have the same spatial reference.
        """
        
        result = Condition("QaIntersectsOther(2)")
        if type(intersected_classes) == list:
            for element in intersected_classes:
                result.parameters.append(Parameter("intersectedClasses", element))
        elif intersected_classes is not None:
            result.parameters.append(Parameter("intersectedClasses", intersected_classes))
        if type(intersecting_classes) == list:
            for element in intersecting_classes:
                result.parameters.append(Parameter("intersectingClasses", element))
        elif intersecting_classes is not None:
            result.parameters.append(Parameter("intersectingClasses", intersecting_classes))
        result.parameters.append(Parameter("validRelationConstraint", valid_relation_constraint))
        result.parameters.append(Parameter("ReportIntersectionsAsMultipart", report_intersections_as_multipart))
        result.parameters.append(Parameter("ValidIntersectionGeometryConstraint", valid_intersection_geometry_constraint))
        result.generate_name()
        return result

    @classmethod
    def qa_intersects_other_3(cls, intersected_class: BaseDataset, intersecting_class: BaseDataset, valid_relation_constraint: str, report_intersections_as_multipart: bool = True, valid_intersection_geometry_constraint: str = None) -> Condition:
        """
        Finds all features in 'intersectingClass' that intersect by any features of 'intersectedClass', and for which a given constraint is not fulfilled.
        
        Remark: The feature classes in 'intersectedClass' and 'intersectingClass' must have the same spatial reference.
        """
        
        result = Condition("QaIntersectsOther(3)")
        result.parameters.append(Parameter("intersectedClass", intersected_class))
        result.parameters.append(Parameter("intersectingClass", intersecting_class))
        result.parameters.append(Parameter("validRelationConstraint", valid_relation_constraint))
        result.parameters.append(Parameter("ReportIntersectionsAsMultipart", report_intersections_as_multipart))
        result.parameters.append(Parameter("ValidIntersectionGeometryConstraint", valid_intersection_geometry_constraint))
        result.generate_name()
        return result

    @classmethod
    def qa_intersects_self_0(cls, feature_class: BaseDataset, report_intersections_as_multipart: bool = True, valid_intersection_geometry_constraint: str = None, geometry_components: List[GeometryComponent] = 0) -> Condition:
        """
        Finds all features in 'featureClass' that intersect any feature in 'featureClass'
        """
        
        result = Condition("QaIntersectsSelf(0)")
        result.parameters.append(Parameter("featureClass", feature_class))
        result.parameters.append(Parameter("ReportIntersectionsAsMultipart", report_intersections_as_multipart))
        result.parameters.append(Parameter("ValidIntersectionGeometryConstraint", valid_intersection_geometry_constraint))
        if type(geometry_components) == list:
            for element in geometry_components:
                result.parameters.append(Parameter("GeometryComponents", element))
        elif geometry_components is not None:
            result.parameters.append(Parameter("GeometryComponents", geometry_components))
        result.generate_name()
        return result

    @classmethod
    def qa_intersects_self_1(cls, feature_classes: List[BaseDataset], report_intersections_as_multipart: bool = True, valid_intersection_geometry_constraint: str = None, geometry_components: List[GeometryComponent] = 0) -> Condition:
        """
        Finds all features in 'featureClasses' that intersect any feature in 'featureClasses'
        """
        
        result = Condition("QaIntersectsSelf(1)")
        if type(feature_classes) == list:
            for element in feature_classes:
                result.parameters.append(Parameter("featureClasses", element))
        elif feature_classes is not None:
            result.parameters.append(Parameter("featureClasses", feature_classes))
        result.parameters.append(Parameter("ReportIntersectionsAsMultipart", report_intersections_as_multipart))
        result.parameters.append(Parameter("ValidIntersectionGeometryConstraint", valid_intersection_geometry_constraint))
        if type(geometry_components) == list:
            for element in geometry_components:
                result.parameters.append(Parameter("GeometryComponents", element))
        elif geometry_components is not None:
            result.parameters.append(Parameter("GeometryComponents", geometry_components))
        result.generate_name()
        return result

    @classmethod
    def qa_intersects_self_2(cls, feature_classes: List[BaseDataset], valid_relation_constraint: str, report_intersections_as_multipart: bool = True, valid_intersection_geometry_constraint: str = None, geometry_components: List[GeometryComponent] = 0) -> Condition:
        """
        Finds all features in 'featureClasses' that intersect any feature in 'featureClasses', and for which a given constraint is not fulfilled.
        """
        
        result = Condition("QaIntersectsSelf(2)")
        if type(feature_classes) == list:
            for element in feature_classes:
                result.parameters.append(Parameter("featureClasses", element))
        elif feature_classes is not None:
            result.parameters.append(Parameter("featureClasses", feature_classes))
        result.parameters.append(Parameter("validRelationConstraint", valid_relation_constraint))
        result.parameters.append(Parameter("ReportIntersectionsAsMultipart", report_intersections_as_multipart))
        result.parameters.append(Parameter("ValidIntersectionGeometryConstraint", valid_intersection_geometry_constraint))
        if type(geometry_components) == list:
            for element in geometry_components:
                result.parameters.append(Parameter("GeometryComponents", element))
        elif geometry_components is not None:
            result.parameters.append(Parameter("GeometryComponents", geometry_components))
        result.generate_name()
        return result

    @classmethod
    def qa_intersects_self_3(cls, feature_class: BaseDataset, valid_relation_constraint: str, report_intersections_as_multipart: bool = True, valid_intersection_geometry_constraint: str = None, geometry_components: List[GeometryComponent] = 0) -> Condition:
        """
        Finds all features in 'featureClass' that intersect any feature in 'featureClass', and for which a given constraint is not fulfilled.
        """
        
        result = Condition("QaIntersectsSelf(3)")
        result.parameters.append(Parameter("featureClass", feature_class))
        result.parameters.append(Parameter("validRelationConstraint", valid_relation_constraint))
        result.parameters.append(Parameter("ReportIntersectionsAsMultipart", report_intersections_as_multipart))
        result.parameters.append(Parameter("ValidIntersectionGeometryConstraint", valid_intersection_geometry_constraint))
        if type(geometry_components) == list:
            for element in geometry_components:
                result.parameters.append(Parameter("GeometryComponents", element))
        elif geometry_components is not None:
            result.parameters.append(Parameter("GeometryComponents", geometry_components))
        result.generate_name()
        return result

    @classmethod
    def qa_is_covered_by_other_0(cls, covering: List[BaseDataset], covered: List[BaseDataset], covering_class_tolerances: List[float] = 0, valid_uncovered_geometry_constraint: str = None) -> Condition:
        """
        Finds all features in 'covered' that are not fully covered by the features in 'covering'
        
        Remarks: All feature classes in 'covered' and 'covering' must have the same spatial reference.
        """
        
        result = Condition("QaIsCoveredByOther(0)")
        if type(covering) == list:
            for element in covering:
                result.parameters.append(Parameter("covering", element))
        elif covering is not None:
            result.parameters.append(Parameter("covering", covering))
        if type(covered) == list:
            for element in covered:
                result.parameters.append(Parameter("covered", element))
        elif covered is not None:
            result.parameters.append(Parameter("covered", covered))
        if type(covering_class_tolerances) == list:
            for element in covering_class_tolerances:
                result.parameters.append(Parameter("CoveringClassTolerances", element))
        elif covering_class_tolerances is not None:
            result.parameters.append(Parameter("CoveringClassTolerances", covering_class_tolerances))
        result.parameters.append(Parameter("ValidUncoveredGeometryConstraint", valid_uncovered_geometry_constraint))
        result.generate_name()
        return result

    @classmethod
    def qa_is_covered_by_other_1(cls, covering: BaseDataset, covered: BaseDataset, covering_class_tolerances: List[float] = 0, valid_uncovered_geometry_constraint: str = None) -> Condition:
        """
        Finds all features in 'covered' that are not fully covered by the features in 'covering'
        
        Remarks: The feature classes in 'covered' and 'covering' must have the same spatial reference.
        """
        
        result = Condition("QaIsCoveredByOther(1)")
        result.parameters.append(Parameter("covering", covering))
        result.parameters.append(Parameter("covered", covered))
        if type(covering_class_tolerances) == list:
            for element in covering_class_tolerances:
                result.parameters.append(Parameter("CoveringClassTolerances", element))
        elif covering_class_tolerances is not None:
            result.parameters.append(Parameter("CoveringClassTolerances", covering_class_tolerances))
        result.parameters.append(Parameter("ValidUncoveredGeometryConstraint", valid_uncovered_geometry_constraint))
        result.generate_name()
        return result

    @classmethod
    def qa_is_covered_by_other_2(cls, covering: List[BaseDataset], covered: List[BaseDataset], is_covering_condition: str, covering_class_tolerances: List[float] = 0, valid_uncovered_geometry_constraint: str = None) -> Condition:
        """
        Finds all features in 'covered' that are not fully covered by the features in 'covering' for which a given condition is fulfilled
        
        Remarks: All feature classes in 'covered' and 'covering' must have the same spatial reference.
        """
        
        result = Condition("QaIsCoveredByOther(2)")
        if type(covering) == list:
            for element in covering:
                result.parameters.append(Parameter("covering", element))
        elif covering is not None:
            result.parameters.append(Parameter("covering", covering))
        if type(covered) == list:
            for element in covered:
                result.parameters.append(Parameter("covered", element))
        elif covered is not None:
            result.parameters.append(Parameter("covered", covered))
        result.parameters.append(Parameter("isCoveringCondition", is_covering_condition))
        if type(covering_class_tolerances) == list:
            for element in covering_class_tolerances:
                result.parameters.append(Parameter("CoveringClassTolerances", element))
        elif covering_class_tolerances is not None:
            result.parameters.append(Parameter("CoveringClassTolerances", covering_class_tolerances))
        result.parameters.append(Parameter("ValidUncoveredGeometryConstraint", valid_uncovered_geometry_constraint))
        result.generate_name()
        return result

    @classmethod
    def qa_is_covered_by_other_3(cls, covering: BaseDataset, covered: BaseDataset, is_covering_condition: str, covering_class_tolerances: List[float] = 0, valid_uncovered_geometry_constraint: str = None) -> Condition:
        """
        Finds all features in 'covered' that are not fully covered by the features in 'covering' for which a given condition is fulfilled
        
        Remarks: All feature classes in 'covered' and 'covering' must have the same spatial reference.
        """
        
        result = Condition("QaIsCoveredByOther(3)")
        result.parameters.append(Parameter("covering", covering))
        result.parameters.append(Parameter("covered", covered))
        result.parameters.append(Parameter("isCoveringCondition", is_covering_condition))
        if type(covering_class_tolerances) == list:
            for element in covering_class_tolerances:
                result.parameters.append(Parameter("CoveringClassTolerances", element))
        elif covering_class_tolerances is not None:
            result.parameters.append(Parameter("CoveringClassTolerances", covering_class_tolerances))
        result.parameters.append(Parameter("ValidUncoveredGeometryConstraint", valid_uncovered_geometry_constraint))
        result.generate_name()
        return result

    @classmethod
    def qa_is_covered_by_other_4(cls, covering: List[BaseDataset], covering_geometry_components: List[GeometryComponent], covered: List[BaseDataset], covered_geometry_components: List[GeometryComponent], is_covering_condition: str, covering_class_tolerances: List[float] = 0, valid_uncovered_geometry_constraint: str = None) -> Condition:
        """
        Finds all features in 'covered' for which the specified geometry components are not fully covered by the specified geometry component of features in 'covering'.
        
        The following geometry components are supported:
        
        - EntireGeometry: the original feature geometry
        - Boundary: supported for polygons and polylines. For polylines, the boundary consists of the start\/end points of all parts. For polygons, it corresponds to the outlines of all polygon rings.
        - Vertices: supported for polygons, polylines, multipatches and multiparts. The vertices of the geometry.
        - LineEndPoints: supported for polylines. The start and end point of the entire polyline, i.e. the start point of the first path and the end point of the last path.
        - LineStartPoint: supported for polylines. The start point of the entire polyline, i.e. the start point of the first path.
        - LineEndPoint: supported for polylines. The end point of the entire polyline, i.e. the end point of the last path.
        - Centroid: supported for polygons. The centroid point of the entire polygon.
        - LabelPoint: supported for polygons. The label point of the entire polygon.
        - InteriorVertices: supported for polylines. All line vertices except the start and end point of the entire polyline.
        
        The number of geometry components in the list must be either 0 (in which case 'EntireGeometry' is used as default), 1 (in which case that component is used for all feature classes in the list) or equal to the number of feature classes. In that case, the components are assigned to the feature classes by their index position in the list.
        """
        
        result = Condition("QaIsCoveredByOther(4)")
        if type(covering) == list:
            for element in covering:
                result.parameters.append(Parameter("covering", element))
        elif covering is not None:
            result.parameters.append(Parameter("covering", covering))
        if type(covering_geometry_components) == list:
            for element in covering_geometry_components:
                result.parameters.append(Parameter("coveringGeometryComponents", element))
        elif covering_geometry_components is not None:
            result.parameters.append(Parameter("coveringGeometryComponents", covering_geometry_components))
        if type(covered) == list:
            for element in covered:
                result.parameters.append(Parameter("covered", element))
        elif covered is not None:
            result.parameters.append(Parameter("covered", covered))
        if type(covered_geometry_components) == list:
            for element in covered_geometry_components:
                result.parameters.append(Parameter("coveredGeometryComponents", element))
        elif covered_geometry_components is not None:
            result.parameters.append(Parameter("coveredGeometryComponents", covered_geometry_components))
        result.parameters.append(Parameter("isCoveringCondition", is_covering_condition))
        if type(covering_class_tolerances) == list:
            for element in covering_class_tolerances:
                result.parameters.append(Parameter("CoveringClassTolerances", element))
        elif covering_class_tolerances is not None:
            result.parameters.append(Parameter("CoveringClassTolerances", covering_class_tolerances))
        result.parameters.append(Parameter("ValidUncoveredGeometryConstraint", valid_uncovered_geometry_constraint))
        result.generate_name()
        return result

    @classmethod
    def qa_is_covered_by_other_5(cls, covering: List[BaseDataset], covering_geometry_components: List[GeometryComponent], covered: List[BaseDataset], covered_geometry_components: List[GeometryComponent], is_covering_condition: str, allowed_uncovered_percentage: float, covering_class_tolerances: List[float] = 0, valid_uncovered_geometry_constraint: str = None) -> Condition:
        """
        Finds all features in 'covered' for which the specified geometry components are not sufficiently covered by the specified geometry component of features in 'covering'. An allowed uncovered percentage may be specified.
        
        The following geometry components are supported:
        
        - EntireGeometry: the original feature geometry
        - Boundary: supported for polygons and polylines. For polylines, the boundary consists of the start\/end points of all parts. For polygons, it corresponds to the outlines of all polygon rings.
        - Vertices: supported for polygons, polylines, multipatches and multiparts. The vertices of the geometry.
        - LineEndPoints: supported for polylines. The start and end point of the entire polyline, i.e. the start point of the first path and the end point of the last path.
        - LineStartPoint: supported for polylines. The start point of the entire polyline, i.e. the start point of the first path.
        - LineEndPoint: supported for polylines. The end point of the entire polyline, i.e. the end point of the last path.
        - Centroid: supported for polygons. The centroid point of the entire polygon.
        - LabelPoint: supported for polygons. The label point of the entire polygon.
        - InteriorVertices: supported for polylines. All line vertices except the start and end point of the entire polyline.
        
        The number of geometry components in the list must be either 0 (in which case 'EntireGeometry' is used as default), 1 (in which case that component is used for all feature classes in the list) or equal to the number of feature classes. In that case, the components are assigned to the feature classes by their index position in the list.
        """
        
        result = Condition("QaIsCoveredByOther(5)")
        if type(covering) == list:
            for element in covering:
                result.parameters.append(Parameter("covering", element))
        elif covering is not None:
            result.parameters.append(Parameter("covering", covering))
        if type(covering_geometry_components) == list:
            for element in covering_geometry_components:
                result.parameters.append(Parameter("coveringGeometryComponents", element))
        elif covering_geometry_components is not None:
            result.parameters.append(Parameter("coveringGeometryComponents", covering_geometry_components))
        if type(covered) == list:
            for element in covered:
                result.parameters.append(Parameter("covered", element))
        elif covered is not None:
            result.parameters.append(Parameter("covered", covered))
        if type(covered_geometry_components) == list:
            for element in covered_geometry_components:
                result.parameters.append(Parameter("coveredGeometryComponents", element))
        elif covered_geometry_components is not None:
            result.parameters.append(Parameter("coveredGeometryComponents", covered_geometry_components))
        result.parameters.append(Parameter("isCoveringCondition", is_covering_condition))
        result.parameters.append(Parameter("allowedUncoveredPercentage", allowed_uncovered_percentage))
        if type(covering_class_tolerances) == list:
            for element in covering_class_tolerances:
                result.parameters.append(Parameter("CoveringClassTolerances", element))
        elif covering_class_tolerances is not None:
            result.parameters.append(Parameter("CoveringClassTolerances", covering_class_tolerances))
        result.parameters.append(Parameter("ValidUncoveredGeometryConstraint", valid_uncovered_geometry_constraint))
        result.generate_name()
        return result

    @classmethod
    def qa_is_covered_by_other_6(cls, covering: List[BaseDataset], covering_geometry_components: List[GeometryComponent], covered: List[BaseDataset], covered_geometry_components: List[GeometryComponent], is_covering_conditions: List[str], allowed_uncovered_percentage: float, covering_class_tolerances: List[float] = 0, valid_uncovered_geometry_constraint: str = None) -> Condition:
        """
        Finds all features in 'covered' for which the specified geometry components are not sufficiently covered by the specified geometry component of features in 'covering'. An allowed uncovered percentage may be specified.
        
        The following geometry components are supported:
        
        - EntireGeometry: the original feature geometry
        - Boundary: supported for polygons and polylines. For polylines, the boundary consists of the start\/end points of all parts. For polygons, it corresponds to the outlines of all polygon rings.
        - Vertices: supported for polygons, polylines, multipatches and multiparts. The vertices of the geometry.
        - LineEndPoints: supported for polylines. The start and end point of the entire polyline, i.e. the start point of the first path and the end point of the last path.
        - LineStartPoint: supported for polylines. The start point of the entire polyline, i.e. the start point of the first path.
        - LineEndPoint: supported for polylines. The end point of the entire polyline, i.e. the end point of the last path.
        - Centroid: supported for polygons. The centroid point of the entire polygon.
        - LabelPoint: supported for polygons. The label point of the entire polygon.
        - InteriorVertices: supported for polylines. All line vertices except the start and end point of the entire polyline.
        
        The number of geometry components in the list must be either 0 (in which case 'EntireGeometry' is used as default), 1 (in which case that component is used for all feature classes in the list) or equal to the number of feature classes. In that case, the components are assigned to the feature classes by their index position in the list.
        """
        
        result = Condition("QaIsCoveredByOther(6)")
        if type(covering) == list:
            for element in covering:
                result.parameters.append(Parameter("covering", element))
        elif covering is not None:
            result.parameters.append(Parameter("covering", covering))
        if type(covering_geometry_components) == list:
            for element in covering_geometry_components:
                result.parameters.append(Parameter("coveringGeometryComponents", element))
        elif covering_geometry_components is not None:
            result.parameters.append(Parameter("coveringGeometryComponents", covering_geometry_components))
        if type(covered) == list:
            for element in covered:
                result.parameters.append(Parameter("covered", element))
        elif covered is not None:
            result.parameters.append(Parameter("covered", covered))
        if type(covered_geometry_components) == list:
            for element in covered_geometry_components:
                result.parameters.append(Parameter("coveredGeometryComponents", element))
        elif covered_geometry_components is not None:
            result.parameters.append(Parameter("coveredGeometryComponents", covered_geometry_components))
        if type(is_covering_conditions) == list:
            for element in is_covering_conditions:
                result.parameters.append(Parameter("isCoveringConditions", element))
        elif is_covering_conditions is not None:
            result.parameters.append(Parameter("isCoveringConditions", is_covering_conditions))
        result.parameters.append(Parameter("allowedUncoveredPercentage", allowed_uncovered_percentage))
        if type(covering_class_tolerances) == list:
            for element in covering_class_tolerances:
                result.parameters.append(Parameter("CoveringClassTolerances", element))
        elif covering_class_tolerances is not None:
            result.parameters.append(Parameter("CoveringClassTolerances", covering_class_tolerances))
        result.parameters.append(Parameter("ValidUncoveredGeometryConstraint", valid_uncovered_geometry_constraint))
        result.generate_name()
        return result

    @classmethod
    def qa_is_covered_by_other_7(cls, covering: List[BaseDataset], covering_geometry_components: List[GeometryComponent], covered: List[BaseDataset], covered_geometry_components: List[GeometryComponent], is_covering_conditions: List[str], allowed_uncovered_percentage: float, area_of_interest_classes: List[BaseDataset], covering_class_tolerances: List[float] = 0, valid_uncovered_geometry_constraint: str = None) -> Condition:
        """
        Finds all features in 'covered' for which the specified geometry components are not sufficiently covered by the specified geometry component of features in 'covering', within an (optional) area of interest defined by polygons from 'areaOfInterestClasses'. An allowed uncovered percentage may be specified.
        
        The following geometry components are supported:
        
        - EntireGeometry: the original feature geometry
        - Boundary: supported for polygons and polylines. For polylines, the boundary consists of the start\/end points of all parts. For polygons, it corresponds to the outlines of all polygon rings.
        - Vertices: supported for polygons, polylines, multipatches and multiparts. The vertices of the geometry.
        - LineEndPoints: supported for polylines. The start and end point of the entire polyline, i.e. the start point of the first path and the end point of the last path.
        - LineStartPoint: supported for polylines. The start point of the entire polyline, i.e. the start point of the first path.
        - LineEndPoint: supported for polylines. The end point of the entire polyline, i.e. the end point of the last path.
        
        The number of geometry components in the list must be either 0 (in which case 'EntireGeometry' is used as default), 1 (in which case that component is used for all feature classes in the list) or equal to the number of feature classes. In that case, the components are assigned to the feature classes by their index position in the list.
        """
        
        result = Condition("QaIsCoveredByOther(7)")
        if type(covering) == list:
            for element in covering:
                result.parameters.append(Parameter("covering", element))
        elif covering is not None:
            result.parameters.append(Parameter("covering", covering))
        if type(covering_geometry_components) == list:
            for element in covering_geometry_components:
                result.parameters.append(Parameter("coveringGeometryComponents", element))
        elif covering_geometry_components is not None:
            result.parameters.append(Parameter("coveringGeometryComponents", covering_geometry_components))
        if type(covered) == list:
            for element in covered:
                result.parameters.append(Parameter("covered", element))
        elif covered is not None:
            result.parameters.append(Parameter("covered", covered))
        if type(covered_geometry_components) == list:
            for element in covered_geometry_components:
                result.parameters.append(Parameter("coveredGeometryComponents", element))
        elif covered_geometry_components is not None:
            result.parameters.append(Parameter("coveredGeometryComponents", covered_geometry_components))
        if type(is_covering_conditions) == list:
            for element in is_covering_conditions:
                result.parameters.append(Parameter("isCoveringConditions", element))
        elif is_covering_conditions is not None:
            result.parameters.append(Parameter("isCoveringConditions", is_covering_conditions))
        result.parameters.append(Parameter("allowedUncoveredPercentage", allowed_uncovered_percentage))
        if type(area_of_interest_classes) == list:
            for element in area_of_interest_classes:
                result.parameters.append(Parameter("areaOfInterestClasses", element))
        elif area_of_interest_classes is not None:
            result.parameters.append(Parameter("areaOfInterestClasses", area_of_interest_classes))
        if type(covering_class_tolerances) == list:
            for element in covering_class_tolerances:
                result.parameters.append(Parameter("CoveringClassTolerances", element))
        elif covering_class_tolerances is not None:
            result.parameters.append(Parameter("CoveringClassTolerances", covering_class_tolerances))
        result.parameters.append(Parameter("ValidUncoveredGeometryConstraint", valid_uncovered_geometry_constraint))
        result.generate_name()
        return result

    @classmethod
    def qa_line_connection_field_values_0(cls, line_class: BaseDataset, line_field: str, line_field_values_constraint: LineFieldValuesConstraint, point_class: BaseDataset, point_field: str, point_field_values_constraint: PointFieldValuesConstraint) -> Condition:
        """
        Checks constraints for the distinct values of fields from connected line and point features at a location.
        """
        
        result = Condition("QaLineConnectionFieldValues(0)")
        result.parameters.append(Parameter("lineClass", line_class))
        result.parameters.append(Parameter("lineField", line_field))
        result.parameters.append(Parameter("lineFieldValuesConstraint", line_field_values_constraint))
        result.parameters.append(Parameter("pointClass", point_class))
        result.parameters.append(Parameter("pointField", point_field))
        result.parameters.append(Parameter("pointFieldValuesConstraint", point_field_values_constraint))
        result.generate_name()
        return result

    @classmethod
    def qa_line_connection_field_values_1(cls, line_classes: List[BaseDataset], line_fields: List[str], line_field_values_constraint: LineFieldValuesConstraint, point_class: BaseDataset, point_field: str, point_field_values_constraint: PointFieldValuesConstraint) -> Condition:
        """
        Checks constraints for the distinct values of fields from connected line and point features at a location.
        """
        
        result = Condition("QaLineConnectionFieldValues(1)")
        if type(line_classes) == list:
            for element in line_classes:
                result.parameters.append(Parameter("lineClasses", element))
        elif line_classes is not None:
            result.parameters.append(Parameter("lineClasses", line_classes))
        if type(line_fields) == list:
            for element in line_fields:
                result.parameters.append(Parameter("lineFields", element))
        elif line_fields is not None:
            result.parameters.append(Parameter("lineFields", line_fields))
        result.parameters.append(Parameter("lineFieldValuesConstraint", line_field_values_constraint))
        result.parameters.append(Parameter("pointClass", point_class))
        result.parameters.append(Parameter("pointField", point_field))
        result.parameters.append(Parameter("pointFieldValuesConstraint", point_field_values_constraint))
        result.generate_name()
        return result

    @classmethod
    def qa_line_connection_field_values_2(cls, line_class: BaseDataset, line_field: str, line_field_values_constraint: LineFieldValuesConstraint, point_class: BaseDataset) -> Condition:
        """
        Checks constraints for the distinct values of fields from connected lines at a location.
        """
        
        result = Condition("QaLineConnectionFieldValues(2)")
        result.parameters.append(Parameter("lineClass", line_class))
        result.parameters.append(Parameter("lineField", line_field))
        result.parameters.append(Parameter("lineFieldValuesConstraint", line_field_values_constraint))
        result.parameters.append(Parameter("pointClass", point_class))
        result.generate_name()
        return result

    @classmethod
    def qa_line_connection_field_values_3(cls, line_classes: List[BaseDataset], line_fields: List[str], line_field_values_constraint: LineFieldValuesConstraint, point_class: BaseDataset, point_field: str, point_field_values_constraint: PointFieldValuesConstraint, allowed_points_expression: str) -> Condition:
        """
        Checks constraints for the distinct values of fields from connected lines at a location.
        """
        
        result = Condition("QaLineConnectionFieldValues(3)")
        if type(line_classes) == list:
            for element in line_classes:
                result.parameters.append(Parameter("lineClasses", element))
        elif line_classes is not None:
            result.parameters.append(Parameter("lineClasses", line_classes))
        if type(line_fields) == list:
            for element in line_fields:
                result.parameters.append(Parameter("lineFields", element))
        elif line_fields is not None:
            result.parameters.append(Parameter("lineFields", line_fields))
        result.parameters.append(Parameter("lineFieldValuesConstraint", line_field_values_constraint))
        result.parameters.append(Parameter("pointClass", point_class))
        result.parameters.append(Parameter("pointField", point_field))
        result.parameters.append(Parameter("pointFieldValuesConstraint", point_field_values_constraint))
        result.parameters.append(Parameter("allowedPointsExpression", allowed_points_expression))
        result.generate_name()
        return result

    @classmethod
    def qa_line_connection_field_values_4(cls, line_classes: List[BaseDataset], line_fields: List[str], line_field_values_constraint: LineFieldValuesConstraint, point_classes: List[BaseDataset], point_fields: List[str], point_field_values_constraint: PointFieldValuesConstraint, allowed_points_expressions: List[str]) -> Condition:
        """
        Checks constraints for the distinct values of fields from connected lines at a location.
        """
        
        result = Condition("QaLineConnectionFieldValues(4)")
        if type(line_classes) == list:
            for element in line_classes:
                result.parameters.append(Parameter("lineClasses", element))
        elif line_classes is not None:
            result.parameters.append(Parameter("lineClasses", line_classes))
        if type(line_fields) == list:
            for element in line_fields:
                result.parameters.append(Parameter("lineFields", element))
        elif line_fields is not None:
            result.parameters.append(Parameter("lineFields", line_fields))
        result.parameters.append(Parameter("lineFieldValuesConstraint", line_field_values_constraint))
        if type(point_classes) == list:
            for element in point_classes:
                result.parameters.append(Parameter("pointClasses", element))
        elif point_classes is not None:
            result.parameters.append(Parameter("pointClasses", point_classes))
        if type(point_fields) == list:
            for element in point_fields:
                result.parameters.append(Parameter("pointFields", element))
        elif point_fields is not None:
            result.parameters.append(Parameter("pointFields", point_fields))
        result.parameters.append(Parameter("pointFieldValuesConstraint", point_field_values_constraint))
        if type(allowed_points_expressions) == list:
            for element in allowed_points_expressions:
                result.parameters.append(Parameter("allowedPointsExpressions", element))
        elif allowed_points_expressions is not None:
            result.parameters.append(Parameter("allowedPointsExpressions", allowed_points_expressions))
        result.generate_name()
        return result

    @classmethod
    def qa_line_group_constraints_0(cls, network_feature_classes: List[BaseDataset], min_gap: float, min_group_length: float, min_dangle_length: float, group_by: List[str], value_separator: str = None, group_conditions: List[str] = None, min_gap_to_other_group_type: float = 0, min_dangle_length_continued: float = 0, min_dangle_length_at_fork_continued: float = 0, min_dangle_length_at_fork: float = 0, min_gap_to_same_group_type_covered: float = 0, min_gap_to_same_group_type_at_fork: float = 0, min_gap_to_same_group_type_at_fork_covered: float = 0, min_gap_to_other_group_type_at_fork: float = 0, min_gap_to_same_group: float = 0) -> Condition:
        """
        Find errors in checking if connected polylines of 'networkFeatureClasses' with same attributes related to 'groupBy' meet the conditions defined by the parameters
        """
        
        result = Condition("QaLineGroupConstraints(0)")
        if type(network_feature_classes) == list:
            for element in network_feature_classes:
                result.parameters.append(Parameter("networkFeatureClasses", element))
        elif network_feature_classes is not None:
            result.parameters.append(Parameter("networkFeatureClasses", network_feature_classes))
        result.parameters.append(Parameter("minGap", min_gap))
        result.parameters.append(Parameter("minGroupLength", min_group_length))
        result.parameters.append(Parameter("minDangleLength", min_dangle_length))
        if type(group_by) == list:
            for element in group_by:
                result.parameters.append(Parameter("groupBy", element))
        elif group_by is not None:
            result.parameters.append(Parameter("groupBy", group_by))
        result.parameters.append(Parameter("ValueSeparator", value_separator))
        if type(group_conditions) == list:
            for element in group_conditions:
                result.parameters.append(Parameter("GroupConditions", element))
        elif group_conditions is not None:
            result.parameters.append(Parameter("GroupConditions", group_conditions))
        result.parameters.append(Parameter("MinGapToOtherGroupType", min_gap_to_other_group_type))
        result.parameters.append(Parameter("MinDangleLengthContinued", min_dangle_length_continued))
        result.parameters.append(Parameter("MinDangleLengthAtForkContinued", min_dangle_length_at_fork_continued))
        result.parameters.append(Parameter("MinDangleLengthAtFork", min_dangle_length_at_fork))
        result.parameters.append(Parameter("MinGapToSameGroupTypeCovered", min_gap_to_same_group_type_covered))
        result.parameters.append(Parameter("MinGapToSameGroupTypeAtFork", min_gap_to_same_group_type_at_fork))
        result.parameters.append(Parameter("MinGapToSameGroupTypeAtForkCovered", min_gap_to_same_group_type_at_fork_covered))
        result.parameters.append(Parameter("MinGapToOtherGroupTypeAtFork", min_gap_to_other_group_type_at_fork))
        result.parameters.append(Parameter("MinGapToSameGroup", min_gap_to_same_group))
        result.generate_name()
        return result

    @classmethod
    def qa_line_intersect_0(cls, polyline_classes: List[BaseDataset], allowed_interior_intersections: AllowedLineInteriorIntersections = 0) -> Condition:
        """
        Finds all features in 'polylineClasses' that cross any other feature in 'polylineClasses'
        
        Remark: The feature classes in 'polylineClasses' must have the same spatial reference.
        """
        
        result = Condition("QaLineIntersect(0)")
        if type(polyline_classes) == list:
            for element in polyline_classes:
                result.parameters.append(Parameter("polylineClasses", element))
        elif polyline_classes is not None:
            result.parameters.append(Parameter("polylineClasses", polyline_classes))
        result.parameters.append(Parameter("AllowedInteriorIntersections", allowed_interior_intersections))
        result.generate_name()
        return result

    @classmethod
    def qa_line_intersect_1(cls, polyline_class: BaseDataset, allowed_interior_intersections: AllowedLineInteriorIntersections = 0) -> Condition:
        """
        Finds all features in 'polylineClass' that cross any other feature in 'polylineClass'
        """
        
        result = Condition("QaLineIntersect(1)")
        result.parameters.append(Parameter("polylineClass", polyline_class))
        result.parameters.append(Parameter("AllowedInteriorIntersections", allowed_interior_intersections))
        result.generate_name()
        return result

    @classmethod
    def qa_line_intersect_2(cls, polyline_classes: List[BaseDataset], valid_relation_constraint: str, allowed_interior_intersections: AllowedLineInteriorIntersections = 0) -> Condition:
        """
        Finds all features in 'polylineClasses' that cross any other feature in 'polylineClasses', and for which a given constraint is not fulfilled.
        
        Remark: The feature classes in 'polylineClasses' must have the same spatial reference.
        """
        
        result = Condition("QaLineIntersect(2)")
        if type(polyline_classes) == list:
            for element in polyline_classes:
                result.parameters.append(Parameter("polylineClasses", element))
        elif polyline_classes is not None:
            result.parameters.append(Parameter("polylineClasses", polyline_classes))
        result.parameters.append(Parameter("validRelationConstraint", valid_relation_constraint))
        result.parameters.append(Parameter("AllowedInteriorIntersections", allowed_interior_intersections))
        result.generate_name()
        return result

    @classmethod
    def qa_line_intersect_3(cls, polyline_class: BaseDataset, valid_relation_constraint: str, allowed_interior_intersections: AllowedLineInteriorIntersections = 0) -> Condition:
        """
        Finds all features in 'polylineClass' that cross any other feature in 'polylineClass', and for which a given constraint is not fulfilled.
        """
        
        result = Condition("QaLineIntersect(3)")
        result.parameters.append(Parameter("polylineClass", polyline_class))
        result.parameters.append(Parameter("validRelationConstraint", valid_relation_constraint))
        result.parameters.append(Parameter("AllowedInteriorIntersections", allowed_interior_intersections))
        result.generate_name()
        return result

    @classmethod
    def qa_line_intersect_4(cls, polyline_classes: List[BaseDataset], valid_relation_constraint: str, allowed_endpoint_interior_intersections: AllowedEndpointInteriorIntersections, report_overlaps: bool, allowed_interior_intersections: AllowedLineInteriorIntersections = 0) -> Condition:
        """
        Finds all features in 'polylineClasses' that have invalid point intersections with any other feature in 'polylineClasses', and for which a given constraint is not fulfilled. Invalid point intersections are points where lines cross, and where end points of one line have an unallowed intersection with the interior of the other line. Optionally, linear intersections are also reported (based on the Overlaps relation between the line geometries). Without this option, only point intersections are reported.
        """
        
        result = Condition("QaLineIntersect(4)")
        if type(polyline_classes) == list:
            for element in polyline_classes:
                result.parameters.append(Parameter("polylineClasses", element))
        elif polyline_classes is not None:
            result.parameters.append(Parameter("polylineClasses", polyline_classes))
        result.parameters.append(Parameter("validRelationConstraint", valid_relation_constraint))
        result.parameters.append(Parameter("allowedEndpointInteriorIntersections", allowed_endpoint_interior_intersections))
        result.parameters.append(Parameter("reportOverlaps", report_overlaps))
        result.parameters.append(Parameter("AllowedInteriorIntersections", allowed_interior_intersections))
        result.generate_name()
        return result

    @classmethod
    def qa_line_intersect_angle_0(cls, polyline_classes: List[BaseDataset], limit: float, is3d: bool, angular_unit: AngleUnit = 0) -> Condition:
        """
        Finds all intersection between lines of 'polylineClasses' where the intersection angle is smaller than 'limit'
        
        Remark: The feature classes in 'polylineClasses' must have the same spatial reference.
        """
        
        result = Condition("QaLineIntersectAngle(0)")
        if type(polyline_classes) == list:
            for element in polyline_classes:
                result.parameters.append(Parameter("polylineClasses", element))
        elif polyline_classes is not None:
            result.parameters.append(Parameter("polylineClasses", polyline_classes))
        result.parameters.append(Parameter("limit", limit))
        result.parameters.append(Parameter("is3d", is3d))
        result.parameters.append(Parameter("AngularUnit", angular_unit))
        result.generate_name()
        return result

    @classmethod
    def qa_line_intersect_angle_2(cls, polyline_classes: List[BaseDataset], limit: float, angular_unit: AngleUnit = 0) -> Condition:
        """
        Finds all intersection between lines of 'polylineClasses' where the intersection angle is smaller than 'limit'
        
        Remark: The feature classes in 'polylineClasses' must have the same spatial reference.
        """
        
        result = Condition("QaLineIntersectAngle(2)")
        if type(polyline_classes) == list:
            for element in polyline_classes:
                result.parameters.append(Parameter("polylineClasses", element))
        elif polyline_classes is not None:
            result.parameters.append(Parameter("polylineClasses", polyline_classes))
        result.parameters.append(Parameter("limit", limit))
        result.parameters.append(Parameter("AngularUnit", angular_unit))
        result.generate_name()
        return result

    @classmethod
    def qa_line_intersect_angle_3(cls, polyline_class: BaseDataset, limit: float, angular_unit: AngleUnit = 0) -> Condition:
        """
        Finds all intersection between lines of 'polylineClasses' where the intersection angle is smaller than 'limit'
        
        Remark: The feature classes in 'polylineClasses' must have the same spatial reference.
        """
        
        result = Condition("QaLineIntersectAngle(3)")
        result.parameters.append(Parameter("polylineClass", polyline_class))
        result.parameters.append(Parameter("limit", limit))
        result.parameters.append(Parameter("AngularUnit", angular_unit))
        result.generate_name()
        return result

    @classmethod
    def qa_line_intersect_z_0(cls, polyline_classes: List[BaseDataset], limit: float, minimum_z_difference_expression: str = None, maximum_z_difference_expression: str = None) -> Condition:
        """
        Finds intersections of features in 'polylineClasses' where the height difference is smaller than 'limit'
        
        Remark: The feature classes in 'polylineClasses' must have the same spatial reference.
        """
        
        result = Condition("QaLineIntersectZ(0)")
        if type(polyline_classes) == list:
            for element in polyline_classes:
                result.parameters.append(Parameter("polylineClasses", element))
        elif polyline_classes is not None:
            result.parameters.append(Parameter("polylineClasses", polyline_classes))
        result.parameters.append(Parameter("limit", limit))
        result.parameters.append(Parameter("MinimumZDifferenceExpression", minimum_z_difference_expression))
        result.parameters.append(Parameter("MaximumZDifferenceExpression", maximum_z_difference_expression))
        result.generate_name()
        return result

    @classmethod
    def qa_line_intersect_z_1(cls, polyline_class: BaseDataset, limit: float, minimum_z_difference_expression: str = None, maximum_z_difference_expression: str = None) -> Condition:
        """
        Finds intersections of features in 'polylineClass' where the height difference is smaller than 'limit'
        """
        
        result = Condition("QaLineIntersectZ(1)")
        result.parameters.append(Parameter("polylineClass", polyline_class))
        result.parameters.append(Parameter("limit", limit))
        result.parameters.append(Parameter("MinimumZDifferenceExpression", minimum_z_difference_expression))
        result.parameters.append(Parameter("MaximumZDifferenceExpression", maximum_z_difference_expression))
        result.generate_name()
        return result

    @classmethod
    def qa_line_intersect_z_2(cls, polyline_class: BaseDataset, limit: float, constraint: str, minimum_z_difference_expression: str = None, maximum_z_difference_expression: str = None) -> Condition:
        """
        Finds intersections of features in 'polylineClass' where the height difference is smaller than 'limit' and 'constraint' is not fulfilled
        """
        
        result = Condition("QaLineIntersectZ(2)")
        result.parameters.append(Parameter("polylineClass", polyline_class))
        result.parameters.append(Parameter("limit", limit))
        result.parameters.append(Parameter("constraint", constraint))
        result.parameters.append(Parameter("MinimumZDifferenceExpression", minimum_z_difference_expression))
        result.parameters.append(Parameter("MaximumZDifferenceExpression", maximum_z_difference_expression))
        result.generate_name()
        return result

    @classmethod
    def qa_line_intersect_z_3(cls, polyline_classes: List[BaseDataset], limit: float, constraint: str, minimum_z_difference_expression: str = None, maximum_z_difference_expression: str = None) -> Condition:
        """
        Finds intersections of features in 'polylineClasses' where the height difference is smaller than 'limit' and 'constraint' is not fulfilled
        
        Remark: The feature classes in 'polylineClasses' must have the same spatial reference.
        """
        
        result = Condition("QaLineIntersectZ(3)")
        if type(polyline_classes) == list:
            for element in polyline_classes:
                result.parameters.append(Parameter("polylineClasses", element))
        elif polyline_classes is not None:
            result.parameters.append(Parameter("polylineClasses", polyline_classes))
        result.parameters.append(Parameter("limit", limit))
        result.parameters.append(Parameter("constraint", constraint))
        result.parameters.append(Parameter("MinimumZDifferenceExpression", minimum_z_difference_expression))
        result.parameters.append(Parameter("MaximumZDifferenceExpression", maximum_z_difference_expression))
        result.generate_name()
        return result

    @classmethod
    def qa_line_intersect_z_4(cls, polyline_classes: List[BaseDataset], minimum_z_difference: float, maximum_z_difference: float, constraint: str, minimum_z_difference_expression: str = None, maximum_z_difference_expression: str = None) -> Condition:
        """
        Finds intersections of features in 'polylineClasses' where the height difference is smaller than 'minimum' or larger than 'maximum' or 'constraint' is not fulfilled
        
        Remark: The feature classes in 'polylineClasses' must have the same spatial reference.
        """
        
        result = Condition("QaLineIntersectZ(4)")
        if type(polyline_classes) == list:
            for element in polyline_classes:
                result.parameters.append(Parameter("polylineClasses", element))
        elif polyline_classes is not None:
            result.parameters.append(Parameter("polylineClasses", polyline_classes))
        result.parameters.append(Parameter("minimumZDifference", minimum_z_difference))
        result.parameters.append(Parameter("maximumZDifference", maximum_z_difference))
        result.parameters.append(Parameter("constraint", constraint))
        result.parameters.append(Parameter("MinimumZDifferenceExpression", minimum_z_difference_expression))
        result.parameters.append(Parameter("MaximumZDifferenceExpression", maximum_z_difference_expression))
        result.generate_name()
        return result

    @classmethod
    def qa_max_area_0(cls, polygon_class: BaseDataset, limit: float) -> Condition:
        """
        Finds all polygons in 'polygonClass' with areas larger than 'limit'
        """
        
        result = Condition("QaMaxArea(0)")
        result.parameters.append(Parameter("polygonClass", polygon_class))
        result.parameters.append(Parameter("limit", limit))
        result.generate_name()
        return result

    @classmethod
    def qa_max_area_1(cls, polygon_class: BaseDataset, limit: float, per_part: bool) -> Condition:
        """
        Finds all parts in 'polygonClass' with areas larger than 'limit'. Parts are defined by perPart
        """
        
        result = Condition("QaMaxArea(1)")
        result.parameters.append(Parameter("polygonClass", polygon_class))
        result.parameters.append(Parameter("limit", limit))
        result.parameters.append(Parameter("perPart", per_part))
        result.generate_name()
        return result

    @classmethod
    def qa_max_length_0(cls, feature_class: BaseDataset, limit: float, is3_d: bool) -> Condition:
        """
        Finds all lines in 'featureClass' with length larger than 'limit'
        """
        
        result = Condition("QaMaxLength(0)")
        result.parameters.append(Parameter("featureClass", feature_class))
        result.parameters.append(Parameter("limit", limit))
        result.parameters.append(Parameter("is3D", is3_d))
        result.generate_name()
        return result

    @classmethod
    def qa_max_length_1(cls, feature_class: BaseDataset, limit: float) -> Condition:
        """
        Finds all lines in 'featureClass' with length larger than 'limit'
        """
        
        result = Condition("QaMaxLength(1)")
        result.parameters.append(Parameter("featureClass", feature_class))
        result.parameters.append(Parameter("limit", limit))
        result.generate_name()
        return result

    @classmethod
    def qa_max_length_2(cls, feature_class: BaseDataset, limit: float, is3_d: bool, per_part: bool) -> Condition:
        """
        Finds all lines in 'featureClass' with length larger than 'limit'
        """
        
        result = Condition("QaMaxLength(2)")
        result.parameters.append(Parameter("featureClass", feature_class))
        result.parameters.append(Parameter("limit", limit))
        result.parameters.append(Parameter("is3D", is3_d))
        result.parameters.append(Parameter("perPart", per_part))
        result.generate_name()
        return result

    @classmethod
    def qa_max_slope_0(cls, feature_class: BaseDataset, limit: float, angular_unit: AngleUnit = 0) -> Condition:
        """
        Finds all segments in 'featureClass' where the slope is larger than 'limit'
        """
        
        result = Condition("QaMaxSlope(0)")
        result.parameters.append(Parameter("featureClass", feature_class))
        result.parameters.append(Parameter("limit", limit))
        result.parameters.append(Parameter("AngularUnit", angular_unit))
        result.generate_name()
        return result

    @classmethod
    def qa_max_vertex_count_0(cls, feature_class: BaseDataset, limit: float, per_part: bool) -> Condition:
        """
        Finds polygon\/polyline\/multipoint features or feature parts with a vertex count larger than 'limit'
        """
        
        result = Condition("QaMaxVertexCount(0)")
        result.parameters.append(Parameter("featureClass", feature_class))
        result.parameters.append(Parameter("limit", limit))
        result.parameters.append(Parameter("perPart", per_part))
        result.generate_name()
        return result

    @classmethod
    def qa_measures_0(cls, feature_class: BaseDataset) -> Condition:
        """
        Finds vertices or segments with undefined (NaN) M values.
        """
        
        result = Condition("QaMeasures(0)")
        result.parameters.append(Parameter("featureClass", feature_class))
        result.generate_name()
        return result

    @classmethod
    def qa_measures_1(cls, feature_class: BaseDataset, invalid_value: float) -> Condition:
        """
        Finds vertices or segments with an invalid M value.
        """
        
        result = Condition("QaMeasures(1)")
        result.parameters.append(Parameter("featureClass", feature_class))
        result.parameters.append(Parameter("invalidValue", invalid_value))
        result.generate_name()
        return result

    @classmethod
    def qa_measures_at_points_0(cls, point_class: BaseDataset, expected_m_value_expression: str, line_classes: List[BaseDataset], search_distance: float, m_tolerance: float, line_m_source: LineMSource, require_line: bool) -> Condition:
        """
        Finds points on 'lineClasses' whose m-Values differ from the neighboring 'pointClass'-point
        
        Remark: All feature classes in 'pointClass' and 'lineClasses' must have the same spatial reference.
        """
        
        result = Condition("QaMeasuresAtPoints(0)")
        result.parameters.append(Parameter("pointClass", point_class))
        result.parameters.append(Parameter("expectedMValueExpression", expected_m_value_expression))
        if type(line_classes) == list:
            for element in line_classes:
                result.parameters.append(Parameter("lineClasses", element))
        elif line_classes is not None:
            result.parameters.append(Parameter("lineClasses", line_classes))
        result.parameters.append(Parameter("searchDistance", search_distance))
        result.parameters.append(Parameter("mTolerance", m_tolerance))
        result.parameters.append(Parameter("lineMSource", line_m_source))
        result.parameters.append(Parameter("requireLine", require_line))
        result.generate_name()
        return result

    @classmethod
    def qa_measures_at_points_1(cls, point_class: BaseDataset, expected_m_value_expression: str, line_classes: List[BaseDataset], search_distance: float, m_tolerance: float, line_m_source: LineMSource, require_line: bool, ignore_undefined_expected_m_value: bool, match_expression: str) -> Condition:
        """
        Finds points on 'lineClasses' whose m-Values differ from the neighboring 'pointClass'-point
        
        Remark: All feature classes in 'pointClass' and 'lineClasses' must have the same spatial reference.
        """
        
        result = Condition("QaMeasuresAtPoints(1)")
        result.parameters.append(Parameter("pointClass", point_class))
        result.parameters.append(Parameter("expectedMValueExpression", expected_m_value_expression))
        if type(line_classes) == list:
            for element in line_classes:
                result.parameters.append(Parameter("lineClasses", element))
        elif line_classes is not None:
            result.parameters.append(Parameter("lineClasses", line_classes))
        result.parameters.append(Parameter("searchDistance", search_distance))
        result.parameters.append(Parameter("mTolerance", m_tolerance))
        result.parameters.append(Parameter("lineMSource", line_m_source))
        result.parameters.append(Parameter("requireLine", require_line))
        result.parameters.append(Parameter("ignoreUndefinedExpectedMValue", ignore_undefined_expected_m_value))
        result.parameters.append(Parameter("matchExpression", match_expression))
        result.generate_name()
        return result

    @classmethod
    def qa_min_angle_0(cls, polyline_class: BaseDataset, limit: float, is3_d: bool, angular_unit: AngleUnit = 0) -> Condition:
        """
        Finds all pair of (From\/To-) points in 'polylineClass' where the angle built by the lines is smaller than 'limit'
        """
        
        result = Condition("QaMinAngle(0)")
        result.parameters.append(Parameter("polylineClass", polyline_class))
        result.parameters.append(Parameter("limit", limit))
        result.parameters.append(Parameter("is3D", is3_d))
        result.parameters.append(Parameter("AngularUnit", angular_unit))
        result.generate_name()
        return result

    @classmethod
    def qa_min_angle_1(cls, polyline_classes: List[BaseDataset], limit: float, is3_d: bool, angular_unit: AngleUnit = 0) -> Condition:
        """
        Finds all pair of (From\/To-) points in 'polylineClasses' where the angle built by the lines is smaller than 'limit'
        
        Remark: The feature classes in 'polylineClasses' must have the same spatial reference.
        """
        
        result = Condition("QaMinAngle(1)")
        if type(polyline_classes) == list:
            for element in polyline_classes:
                result.parameters.append(Parameter("polylineClasses", element))
        elif polyline_classes is not None:
            result.parameters.append(Parameter("polylineClasses", polyline_classes))
        result.parameters.append(Parameter("limit", limit))
        result.parameters.append(Parameter("is3D", is3_d))
        result.parameters.append(Parameter("AngularUnit", angular_unit))
        result.generate_name()
        return result

    @classmethod
    def qa_min_angle_2(cls, polyline_classes: List[BaseDataset], limit: float, angular_unit: AngleUnit = 0) -> Condition:
        """
        Finds all pair of (From\/To-) points in 'polylineClasses' where the angle built by the lines is smaller than 'limit'
        
        Remark: The feature classes in 'polylineClasses' must have the same spatial reference.
        """
        
        result = Condition("QaMinAngle(2)")
        if type(polyline_classes) == list:
            for element in polyline_classes:
                result.parameters.append(Parameter("polylineClasses", element))
        elif polyline_classes is not None:
            result.parameters.append(Parameter("polylineClasses", polyline_classes))
        result.parameters.append(Parameter("limit", limit))
        result.parameters.append(Parameter("AngularUnit", angular_unit))
        result.generate_name()
        return result

    @classmethod
    def qa_min_area_0(cls, polygon_class: BaseDataset, limit: float) -> Condition:
        """
        Finds all polygons in 'polygonClass' with areas smaller than 'limit'. Features with empty geometries are not tested.
        """
        
        result = Condition("QaMinArea(0)")
        result.parameters.append(Parameter("polygonClass", polygon_class))
        result.parameters.append(Parameter("limit", limit))
        result.generate_name()
        return result

    @classmethod
    def qa_min_area_1(cls, polygon_class: BaseDataset, limit: float, per_part: bool) -> Condition:
        """
        Finds all parts in 'polygonClass' with areas smaller than 'limit'. Parts are defined by perPart. Features with empty geometries are not tested.
        """
        
        result = Condition("QaMinArea(1)")
        result.parameters.append(Parameter("polygonClass", polygon_class))
        result.parameters.append(Parameter("limit", limit))
        result.parameters.append(Parameter("perPart", per_part))
        result.generate_name()
        return result

    @classmethod
    def qa_min_intersect_0(cls, polygon_classes: List[BaseDataset], limit: float) -> Condition:
        """
        Finds all area overlaps between two features in 'polygonClasses', where the overlapping area is smaller than 'limit'
        
        Remark: The feature classes in 'polygonClasses' must have the same spatial reference.
        """
        
        result = Condition("QaMinIntersect(0)")
        if type(polygon_classes) == list:
            for element in polygon_classes:
                result.parameters.append(Parameter("polygonClasses", element))
        elif polygon_classes is not None:
            result.parameters.append(Parameter("polygonClasses", polygon_classes))
        result.parameters.append(Parameter("limit", limit))
        result.generate_name()
        return result

    @classmethod
    def qa_min_intersect_1(cls, polygon_class: BaseDataset, limit: float) -> Condition:
        """
        Finds all area overlaps between two features in 'polygonClass', where the overlapping area is smaller than 'limit'
        """
        
        result = Condition("QaMinIntersect(1)")
        result.parameters.append(Parameter("polygonClass", polygon_class))
        result.parameters.append(Parameter("limit", limit))
        result.generate_name()
        return result

    @classmethod
    def qa_min_length_0(cls, feature_class: BaseDataset, limit: float, is3_d: bool) -> Condition:
        """
        Finds all lines in 'featureClass' with length smaller than 'limit'
        """
        
        result = Condition("QaMinLength(0)")
        result.parameters.append(Parameter("featureClass", feature_class))
        result.parameters.append(Parameter("limit", limit))
        result.parameters.append(Parameter("is3D", is3_d))
        result.generate_name()
        return result

    @classmethod
    def qa_min_length_1(cls, feature_class: BaseDataset, limit: float) -> Condition:
        """
        Finds all lines in 'featureClass' with length smaller than 'limit'
        """
        
        result = Condition("QaMinLength(1)")
        result.parameters.append(Parameter("featureClass", feature_class))
        result.parameters.append(Parameter("limit", limit))
        result.generate_name()
        return result

    @classmethod
    def qa_min_length_2(cls, feature_class: BaseDataset, limit: float, is3_d: bool, per_part: bool) -> Condition:
        """
        Finds all lines in 'featureClass' with length smaller than 'limit'
        """
        
        result = Condition("QaMinLength(2)")
        result.parameters.append(Parameter("featureClass", feature_class))
        result.parameters.append(Parameter("limit", limit))
        result.parameters.append(Parameter("is3D", is3_d))
        result.parameters.append(Parameter("perPart", per_part))
        result.generate_name()
        return result

    @classmethod
    def qa_min_mean_segment_length_0(cls, feature_class: BaseDataset, limit: float, per_part: bool) -> Condition:
        """
        Finds polygon\/polyline features or feature parts with an average segment length smaller than 'limit'
        """
        
        result = Condition("QaMinMeanSegmentLength(0)")
        result.parameters.append(Parameter("featureClass", feature_class))
        result.parameters.append(Parameter("limit", limit))
        result.parameters.append(Parameter("perPart", per_part))
        result.generate_name()
        return result

    @classmethod
    def qa_min_mean_segment_length_1(cls, feature_class: BaseDataset, limit: float, per_part: bool, is3_d: bool) -> Condition:
        """
        Finds polygon\/polyline features or feature parts with an average segment length smaller than 'limit'
        """
        
        result = Condition("QaMinMeanSegmentLength(1)")
        result.parameters.append(Parameter("featureClass", feature_class))
        result.parameters.append(Parameter("limit", limit))
        result.parameters.append(Parameter("perPart", per_part))
        result.parameters.append(Parameter("is3D", is3_d))
        result.generate_name()
        return result

    @classmethod
    def qa_min_node_distance_0(cls, feature_class: BaseDataset, near: float, is3_d: bool) -> Condition:
        """
        Finds all pair of (From\/To-) points of 'featureClass' closer than 'near'
        """
        
        result = Condition("QaMinNodeDistance(0)")
        result.parameters.append(Parameter("featureClass", feature_class))
        result.parameters.append(Parameter("near", near))
        result.parameters.append(Parameter("is3D", is3_d))
        result.generate_name()
        return result

    @classmethod
    def qa_min_node_distance_1(cls, feature_classes: List[BaseDataset], near: float, is3_d: bool) -> Condition:
        """
        Finds all pair of (From\/To-) points of 'featureClasses' closer than 'near'
        
        Remark: The feature classes in 'featureClasses' must have the same spatial reference.
        """
        
        result = Condition("QaMinNodeDistance(1)")
        if type(feature_classes) == list:
            for element in feature_classes:
                result.parameters.append(Parameter("featureClasses", element))
        elif feature_classes is not None:
            result.parameters.append(Parameter("featureClasses", feature_classes))
        result.parameters.append(Parameter("near", near))
        result.parameters.append(Parameter("is3D", is3_d))
        result.generate_name()
        return result

    @classmethod
    def qa_min_node_distance_2(cls, feature_class: BaseDataset, near: float, tolerance: float, is3_d: bool) -> Condition:
        """
        Finds all pair of (From\/To-) points of 'featureClass' closer than 'near'. Pairs closer than 'tolerance' are considered coincident
        """
        
        result = Condition("QaMinNodeDistance(2)")
        result.parameters.append(Parameter("featureClass", feature_class))
        result.parameters.append(Parameter("near", near))
        result.parameters.append(Parameter("tolerance", tolerance))
        result.parameters.append(Parameter("is3D", is3_d))
        result.generate_name()
        return result

    @classmethod
    def qa_min_node_distance_3(cls, feature_classes: List[BaseDataset], near: float, tolerance: float, is3_d: bool) -> Condition:
        """
        Finds all pair of (From\/To-) points of 'featureClasses' closer than 'near'. Pairs closer than 'tolerance' are considered coincident
        
        Remark: The feature classes in 'featureClasses' must have the same spatial reference.
        """
        
        result = Condition("QaMinNodeDistance(3)")
        if type(feature_classes) == list:
            for element in feature_classes:
                result.parameters.append(Parameter("featureClasses", element))
        elif feature_classes is not None:
            result.parameters.append(Parameter("featureClasses", feature_classes))
        result.parameters.append(Parameter("near", near))
        result.parameters.append(Parameter("tolerance", tolerance))
        result.parameters.append(Parameter("is3D", is3_d))
        result.generate_name()
        return result

    @classmethod
    def qa_min_node_distance_4(cls, feature_class: BaseDataset, near: float, max_z_difference: float) -> Condition:
        """
        Finds all pair of (From\/To-) points of 'featureClass' closer than 'near' and find all coincident pairs with z-coordinate difference larger than 'maxZDifference'
        """
        
        result = Condition("QaMinNodeDistance(4)")
        result.parameters.append(Parameter("featureClass", feature_class))
        result.parameters.append(Parameter("near", near))
        result.parameters.append(Parameter("maxZDifference", max_z_difference))
        result.generate_name()
        return result

    @classmethod
    def qa_min_node_distance_5(cls, feature_classes: List[BaseDataset], near: float, max_z_difference: float) -> Condition:
        """
        Finds all pair of (From\/To-) points of 'featureClasses' closer than 'near' and find all coincident pairs with z-coordinate difference larger than 'maxZDifference'
        
        Remark: The feature classes in 'featureClasses' must have the same spatial reference.
        """
        
        result = Condition("QaMinNodeDistance(5)")
        if type(feature_classes) == list:
            for element in feature_classes:
                result.parameters.append(Parameter("featureClasses", element))
        elif feature_classes is not None:
            result.parameters.append(Parameter("featureClasses", feature_classes))
        result.parameters.append(Parameter("near", near))
        result.parameters.append(Parameter("maxZDifference", max_z_difference))
        result.generate_name()
        return result

    @classmethod
    def qa_min_node_distance_6(cls, feature_class: BaseDataset, near: float, tolerance: float, max_z_difference: float) -> Condition:
        """
        Finds all pair of (From\/To-) points of 'featureClass' closer than 'near' and find all coincident pairs with z-coordinate difference larger than 'maxZDifference'. Pairs closer than 'tolerance' are considered coincident
        """
        
        result = Condition("QaMinNodeDistance(6)")
        result.parameters.append(Parameter("featureClass", feature_class))
        result.parameters.append(Parameter("near", near))
        result.parameters.append(Parameter("tolerance", tolerance))
        result.parameters.append(Parameter("maxZDifference", max_z_difference))
        result.generate_name()
        return result

    @classmethod
    def qa_min_node_distance_7(cls, feature_classes: List[BaseDataset], near: float, tolerance: float, max_z_difference: float) -> Condition:
        """
        Finds all pair of (From\/To-) points of 'featureClasses' closer than 'near' and find all coincident pairs with z-coordinate difference larger than 'maxZDifference'. Pairs closer than 'tolerance' are considered coincident
        """
        
        result = Condition("QaMinNodeDistance(7)")
        if type(feature_classes) == list:
            for element in feature_classes:
                result.parameters.append(Parameter("featureClasses", element))
        elif feature_classes is not None:
            result.parameters.append(Parameter("featureClasses", feature_classes))
        result.parameters.append(Parameter("near", near))
        result.parameters.append(Parameter("tolerance", tolerance))
        result.parameters.append(Parameter("maxZDifference", max_z_difference))
        result.generate_name()
        return result

    @classmethod
    def qa_min_node_distance_8(cls, feature_classes: List[BaseDataset], near: float) -> Condition:
        """
        Finds all pair of (From\/To-) points of 'featureClasses' closer than 'near'
        
        Remark: The feature classes in 'featureClasses' must have the same spatial reference.
        """
        
        result = Condition("QaMinNodeDistance(8)")
        if type(feature_classes) == list:
            for element in feature_classes:
                result.parameters.append(Parameter("featureClasses", element))
        elif feature_classes is not None:
            result.parameters.append(Parameter("featureClasses", feature_classes))
        result.parameters.append(Parameter("near", near))
        result.generate_name()
        return result

    @classmethod
    def qa_min_node_distance_9(cls, feature_class: BaseDataset, near: float, tolerance: float, max_z_difference: float, valid_relation_constraint: str) -> Condition:
        """
        Finds all pair of (From\/To-) points of 'featureClass' closer than 'near' and find all coincident pairs with z-coordinate difference larger than 'maxZDifference'. Pairs closer than 'tolerance' are considered coincident. No error is reported for point pairs that fulfill a defined constraint.
        """
        
        result = Condition("QaMinNodeDistance(9)")
        result.parameters.append(Parameter("featureClass", feature_class))
        result.parameters.append(Parameter("near", near))
        result.parameters.append(Parameter("tolerance", tolerance))
        result.parameters.append(Parameter("maxZDifference", max_z_difference))
        result.parameters.append(Parameter("validRelationConstraint", valid_relation_constraint))
        result.generate_name()
        return result

    @classmethod
    def qa_min_node_distance_10(cls, feature_classes: List[BaseDataset], near: float, tolerance: float, max_z_difference: float, valid_relation_constraint: str) -> Condition:
        """
        Finds all pair of (From\/To-) points of 'featureClasses' closer than 'near' and find all coincident pairs with z-coordinate difference larger than 'maxZDifference'. Pairs closer than 'tolerance' are considered coincident. No error is reported for point pairs that fulfill a defined constraint.
        """
        
        result = Condition("QaMinNodeDistance(10)")
        if type(feature_classes) == list:
            for element in feature_classes:
                result.parameters.append(Parameter("featureClasses", element))
        elif feature_classes is not None:
            result.parameters.append(Parameter("featureClasses", feature_classes))
        result.parameters.append(Parameter("near", near))
        result.parameters.append(Parameter("tolerance", tolerance))
        result.parameters.append(Parameter("maxZDifference", max_z_difference))
        result.parameters.append(Parameter("validRelationConstraint", valid_relation_constraint))
        result.generate_name()
        return result

    @classmethod
    def qa_min_node_distance_11(cls, feature_class: BaseDataset, near: float, tolerance: float, is3_d: bool, valid_relation_constraint: str) -> Condition:
        """
        Finds all pair of (From\/To-) points of 'featureClass' closer than 'near'. Pairs closer than 'tolerance' are considered coincident. No error is reported for point pairs that fulfill a defined constraint.
        """
        
        result = Condition("QaMinNodeDistance(11)")
        result.parameters.append(Parameter("featureClass", feature_class))
        result.parameters.append(Parameter("near", near))
        result.parameters.append(Parameter("tolerance", tolerance))
        result.parameters.append(Parameter("is3D", is3_d))
        result.parameters.append(Parameter("validRelationConstraint", valid_relation_constraint))
        result.generate_name()
        return result

    @classmethod
    def qa_min_node_distance_12(cls, feature_classes: List[BaseDataset], near: float, tolerance: float, is3_d: bool, valid_relation_constraint: str) -> Condition:
        """
        Finds all pair of (From\/To-) points of 'featureClasses' closer than 'near'. Pairs closer than 'tolerance' are considered coincident. No error is reported for point pairs that fulfill a defined constraint.
        
        Remark: The feature classes in 'featureClasses' must have the same spatial reference.
        """
        
        result = Condition("QaMinNodeDistance(12)")
        if type(feature_classes) == list:
            for element in feature_classes:
                result.parameters.append(Parameter("featureClasses", element))
        elif feature_classes is not None:
            result.parameters.append(Parameter("featureClasses", feature_classes))
        result.parameters.append(Parameter("near", near))
        result.parameters.append(Parameter("tolerance", tolerance))
        result.parameters.append(Parameter("is3D", is3_d))
        result.parameters.append(Parameter("validRelationConstraint", valid_relation_constraint))
        result.generate_name()
        return result

    @classmethod
    def qa_min_seg_angle_0(cls, feature_class: BaseDataset, limit: float, is3_d: bool, use_tangents: bool = False, angular_unit: AngleUnit = 0) -> Condition:
        """
        Finds all consecutive segments in 'featureClass' where the angle between two segments is smaller than 'limit'
        """
        
        result = Condition("QaMinSegAngle(0)")
        result.parameters.append(Parameter("featureClass", feature_class))
        result.parameters.append(Parameter("limit", limit))
        result.parameters.append(Parameter("is3D", is3_d))
        result.parameters.append(Parameter("UseTangents", use_tangents))
        result.parameters.append(Parameter("AngularUnit", angular_unit))
        result.generate_name()
        return result

    @classmethod
    def qa_min_seg_angle_1(cls, feature_class: BaseDataset, limit: float, use_tangents: bool = False, angular_unit: AngleUnit = 0) -> Condition:
        """
        Finds all consecutive segments in 'featureClass' where the angle between two segments is smaller than 'limit'
        """
        
        result = Condition("QaMinSegAngle(1)")
        result.parameters.append(Parameter("featureClass", feature_class))
        result.parameters.append(Parameter("limit", limit))
        result.parameters.append(Parameter("UseTangents", use_tangents))
        result.parameters.append(Parameter("AngularUnit", angular_unit))
        result.generate_name()
        return result

    @classmethod
    def qa_monotonic_measures_0(cls, line_class: BaseDataset, allow_constant_values: bool) -> Condition:
        """
        Finds non-monotonic sequences in M values
        """
        
        result = Condition("QaMonotonicMeasures(0)")
        result.parameters.append(Parameter("lineClass", line_class))
        result.parameters.append(Parameter("allowConstantValues", allow_constant_values))
        result.generate_name()
        return result

    @classmethod
    def qa_monotonic_measures_1(cls, line_class: BaseDataset, allow_constant_values: bool, expected_monotonicity: MonotonicityDirection, flip_expression: str) -> Condition:
        """
        Finds non-monotonic sequences in M values for a given direction
        """
        
        result = Condition("QaMonotonicMeasures(1)")
        result.parameters.append(Parameter("lineClass", line_class))
        result.parameters.append(Parameter("allowConstantValues", allow_constant_values))
        result.parameters.append(Parameter("expectedMonotonicity", expected_monotonicity))
        result.parameters.append(Parameter("flipExpression", flip_expression))
        result.generate_name()
        return result

    @classmethod
    def qa_monotonic_z_0(cls, line_class: BaseDataset, allow_constant_values: bool = True, expected_monotonicity: MonotonicityDirection = 0, flip_expression: str = None) -> Condition:
        """
        Finds non-monotonic sequences in Z values
        """
        
        result = Condition("QaMonotonicZ(0)")
        result.parameters.append(Parameter("lineClass", line_class))
        result.parameters.append(Parameter("AllowConstantValues", allow_constant_values))
        result.parameters.append(Parameter("ExpectedMonotonicity", expected_monotonicity))
        result.parameters.append(Parameter("FlipExpression", flip_expression))
        result.generate_name()
        return result

    @classmethod
    def qa_mp_allowed_part_types_0(cls, multi_patch_class: BaseDataset, allow_rings: bool, allow_triangle_fans: bool, allow_triangle_strips: bool, allow_triangles: bool) -> Condition:
        """
        Finds all geometry parts of 'multipatchClass' that not allowed part types
        """
        
        result = Condition("QaMpAllowedPartTypes(0)")
        result.parameters.append(Parameter("multiPatchClass", multi_patch_class))
        result.parameters.append(Parameter("allowRings", allow_rings))
        result.parameters.append(Parameter("allowTriangleFans", allow_triangle_fans))
        result.parameters.append(Parameter("allowTriangleStrips", allow_triangle_strips))
        result.parameters.append(Parameter("allowTriangles", allow_triangles))
        result.generate_name()
        return result

    @classmethod
    def qa_mp_constant_point_ids_per_ring_0(cls, multi_patch_class: BaseDataset, include_inner_rings: bool) -> Condition:
        """
        Find rings where the pointIds of its points are not constant
        """
        
        result = Condition("QaMpConstantPointIdsPerRing(0)")
        result.parameters.append(Parameter("multiPatchClass", multi_patch_class))
        result.parameters.append(Parameter("includeInnerRings", include_inner_rings))
        result.generate_name()
        return result

    @classmethod
    def qa_mp_footprint_holes_0(cls, multi_patch_class: BaseDataset, inner_ring_handling: InnerRingHandling, horizontal_z_tolerance: float = 0, resolution_factor: float = 1, minimum_area: float = -1, report_vertical_patches_not_completely_within_footprint: bool = True) -> Condition:
        """
        Find multipatch features where footprints have inner rings
        """
        
        result = Condition("QaMpFootprintHoles(0)")
        result.parameters.append(Parameter("multiPatchClass", multi_patch_class))
        result.parameters.append(Parameter("innerRingHandling", inner_ring_handling))
        result.parameters.append(Parameter("HorizontalZTolerance", horizontal_z_tolerance))
        result.parameters.append(Parameter("ResolutionFactor", resolution_factor))
        result.parameters.append(Parameter("MinimumArea", minimum_area))
        result.parameters.append(Parameter("ReportVerticalPatchesNotCompletelyWithinFootprint", report_vertical_patches_not_completely_within_footprint))
        result.generate_name()
        return result

    @classmethod
    def qa_mp_horizontal_azimuths_0(cls, multi_patch_class: BaseDataset, near_angle: float, azimuth_tolerance: float, horizontal_tolerance: float, per_ring: bool) -> Condition:
        """
        Find all horizontal segments of a multipatch feature where their azimuth's differ less than 'nearAngle' but more than 'azimuthTolerance'
        """
        
        result = Condition("QaMpHorizontalAzimuths(0)")
        result.parameters.append(Parameter("multiPatchClass", multi_patch_class))
        result.parameters.append(Parameter("nearAngle", near_angle))
        result.parameters.append(Parameter("azimuthTolerance", azimuth_tolerance))
        result.parameters.append(Parameter("horizontalTolerance", horizontal_tolerance))
        result.parameters.append(Parameter("perRing", per_ring))
        result.generate_name()
        return result

    @classmethod
    def qa_mp_horizontal_heights_0(cls, multi_patch_class: BaseDataset, near_height: float, height_tolerance: float) -> Condition:
        """
        Find all horizontal segment pairs of a multipatch feature where their heights differ less than 'nearHeight' but more than 'heightTolerance'
        """
        
        result = Condition("QaMpHorizontalHeights(0)")
        result.parameters.append(Parameter("multiPatchClass", multi_patch_class))
        result.parameters.append(Parameter("nearHeight", near_height))
        result.parameters.append(Parameter("heightTolerance", height_tolerance))
        result.generate_name()
        return result

    @classmethod
    def qa_mp_horizontal_perpendicular_0(cls, multi_patch_class: BaseDataset, near_angle: float, azimuth_tolerance: float, horizontal_tolerance: float, connected_only: bool, connected_tolerance: float) -> Condition:
        """
        Find all horizontal segment pairs of a multipatch feature where their azimuth's differ less than 'nearAngle' from 90° but more than 'azimuthTolerance'
        """
        
        result = Condition("QaMpHorizontalPerpendicular(0)")
        result.parameters.append(Parameter("multiPatchClass", multi_patch_class))
        result.parameters.append(Parameter("nearAngle", near_angle))
        result.parameters.append(Parameter("azimuthTolerance", azimuth_tolerance))
        result.parameters.append(Parameter("horizontalTolerance", horizontal_tolerance))
        result.parameters.append(Parameter("connectedOnly", connected_only))
        result.parameters.append(Parameter("connectedTolerance", connected_tolerance))
        result.generate_name()
        return result

    @classmethod
    def qa_mp_non_intersecting_ring_footprints_0(cls, multi_patch_class: BaseDataset, allow_intersections_for_different_point_ids: bool, resolution_factor: float = 1) -> Condition:
        """
        Finds multipatch features having rings whose 2D footprints have an interior intersection. Optionally, intersections of footprint interiors can be allowed for rings having different, unique point ids.
        """
        
        result = Condition("QaMpNonIntersectingRingFootprints(0)")
        result.parameters.append(Parameter("multiPatchClass", multi_patch_class))
        result.parameters.append(Parameter("allowIntersectionsForDifferentPointIds", allow_intersections_for_different_point_ids))
        result.parameters.append(Parameter("ResolutionFactor", resolution_factor))
        result.generate_name()
        return result

    @classmethod
    def qa_mp_single_part_footprint_0(cls, multi_patch_class: BaseDataset, resolution_factor: float = 100) -> Condition:
        """
        Finds multipatch features with a 2D footprint that consists of more than one disjoint part.
        """
        
        result = Condition("QaMpSinglePartFootprint(0)")
        result.parameters.append(Parameter("multiPatchClass", multi_patch_class))
        result.parameters.append(Parameter("ResolutionFactor", resolution_factor))
        result.generate_name()
        return result

    @classmethod
    def qa_mp_vertex_not_near_face_0(cls, multi_patch_class: BaseDataset, vertex_classes: List[BaseDataset], minimum_distance_above: float, minimum_distance_below: float, coplanarity_tolerance: float = 0, report_non_coplanarity: bool = False, ignore_non_coplanar_faces: bool = False, verify_within_feature: bool = False, point_coincidence: float = 0, edge_coincidence: float = 0, plane_coincidence: float = -1, minimum_slope_degrees: float = 0) -> Condition:
        """
        Finds vertices of 'vertexClasses' that are not far enough above or below the faces of 'multiPatchClass'
        """
        
        result = Condition("QaMpVertexNotNearFace(0)")
        result.parameters.append(Parameter("multiPatchClass", multi_patch_class))
        if type(vertex_classes) == list:
            for element in vertex_classes:
                result.parameters.append(Parameter("vertexClasses", element))
        elif vertex_classes is not None:
            result.parameters.append(Parameter("vertexClasses", vertex_classes))
        result.parameters.append(Parameter("minimumDistanceAbove", minimum_distance_above))
        result.parameters.append(Parameter("minimumDistanceBelow", minimum_distance_below))
        result.parameters.append(Parameter("CoplanarityTolerance", coplanarity_tolerance))
        result.parameters.append(Parameter("ReportNonCoplanarity", report_non_coplanarity))
        result.parameters.append(Parameter("IgnoreNonCoplanarFaces", ignore_non_coplanar_faces))
        result.parameters.append(Parameter("VerifyWithinFeature", verify_within_feature))
        result.parameters.append(Parameter("PointCoincidence", point_coincidence))
        result.parameters.append(Parameter("EdgeCoincidence", edge_coincidence))
        result.parameters.append(Parameter("PlaneCoincidence", plane_coincidence))
        result.parameters.append(Parameter("MinimumSlopeDegrees", minimum_slope_degrees))
        result.generate_name()
        return result

    @classmethod
    def qa_mp_vertical_faces_0(cls, multi_patch_class: BaseDataset, near_angle: float, tolerance_angle: float) -> Condition:
        """
        Finds patches in a multipatch that are almost vertical 
        """
        
        result = Condition("QaMpVerticalFaces(0)")
        result.parameters.append(Parameter("multiPatchClass", multi_patch_class))
        result.parameters.append(Parameter("nearAngle", near_angle))
        result.parameters.append(Parameter("toleranceAngle", tolerance_angle))
        result.generate_name()
        return result

    @classmethod
    def qa_multipart_0(cls, feature_class: BaseDataset) -> Condition:
        """
        Find all multipart features in 'featureClass'
        """
        
        result = Condition("QaMultipart(0)")
        result.parameters.append(Parameter("featureClass", feature_class))
        result.generate_name()
        return result

    @classmethod
    def qa_multipart_1(cls, feature_class: BaseDataset, single_ring: bool) -> Condition:
        """
        Find all multipart features in 'featureClass'
        """
        
        result = Condition("QaMultipart(1)")
        result.parameters.append(Parameter("featureClass", feature_class))
        result.parameters.append(Parameter("singleRing", single_ring))
        result.generate_name()
        return result

    @classmethod
    def qa_must_be_near_other_0(cls, feature_class: BaseDataset, near_classes: List[BaseDataset], maximum_distance: float, relevant_relation_condition: str, error_distance_format: str = None) -> Condition:
        """
        Finds all features in 'featureClass' that are not closer than 'maximumDistance' to any feature of 'nearClasses', or for which nearby features in 'nearClasses' do exist, but a given comparison constraint is not fulfilled.
        Note that errors can be reported only for features that are completely within the verified extent. Features that extend beyond the verified extent may have valid neighbors outside of the searched extent, and are therefore ignored.
        """
        
        result = Condition("QaMustBeNearOther(0)")
        result.parameters.append(Parameter("featureClass", feature_class))
        if type(near_classes) == list:
            for element in near_classes:
                result.parameters.append(Parameter("nearClasses", element))
        elif near_classes is not None:
            result.parameters.append(Parameter("nearClasses", near_classes))
        result.parameters.append(Parameter("maximumDistance", maximum_distance))
        result.parameters.append(Parameter("relevantRelationCondition", relevant_relation_condition))
        result.parameters.append(Parameter("ErrorDistanceFormat", error_distance_format))
        result.generate_name()
        return result

    @classmethod
    def qa_must_intersect_matrix_other_0(cls, feature_class: BaseDataset, other_feature_class: BaseDataset, intersection_matrix: str, relevant_relation_condition: str) -> Condition:
        """
        Finds all features in 'featureClass' that do not have a given spatial relationship with any feature in 'otherFeatureClass', or for which a given constraint is not fulfilled. The required spatial relationship is defined by a 9IM intersection matrix.
        
        Remark: The feature classes in 'featureClass' and 'relatedClass' must have the same spatial reference.
        """
        
        result = Condition("QaMustIntersectMatrixOther(0)")
        result.parameters.append(Parameter("featureClass", feature_class))
        result.parameters.append(Parameter("otherFeatureClass", other_feature_class))
        result.parameters.append(Parameter("intersectionMatrix", intersection_matrix))
        result.parameters.append(Parameter("relevantRelationCondition", relevant_relation_condition))
        result.generate_name()
        return result

    @classmethod
    def qa_must_intersect_matrix_other_1(cls, feature_class: BaseDataset, other_feature_class: BaseDataset, intersection_matrix: str, relevant_relation_condition: str, required_intersection_dimensions: str, unallowed_intersection_dimensions: str) -> Condition:
        """
        Finds all features in 'featureClass' that do not have a given spatial relationship with any feature in 'otherFeatureClass', or for which a given constraint is not fulfilled. The required spatial relationship is defined by a 9IM intersection matrix. Optionally, the required and unallowed intersection dimensions may be defined. 
        
        Remark: The feature classes in 'featureClass' and 'relatedClass' must have the same spatial reference.
        """
        
        result = Condition("QaMustIntersectMatrixOther(1)")
        result.parameters.append(Parameter("featureClass", feature_class))
        result.parameters.append(Parameter("otherFeatureClass", other_feature_class))
        result.parameters.append(Parameter("intersectionMatrix", intersection_matrix))
        result.parameters.append(Parameter("relevantRelationCondition", relevant_relation_condition))
        result.parameters.append(Parameter("requiredIntersectionDimensions", required_intersection_dimensions))
        result.parameters.append(Parameter("unallowedIntersectionDimensions", unallowed_intersection_dimensions))
        result.generate_name()
        return result

    @classmethod
    def qa_must_intersect_matrix_other_2(cls, feature_classes: List[BaseDataset], other_feature_classes: List[BaseDataset], intersection_matrix: str, relevant_relation_condition: str) -> Condition:
        """
        Finds all features in 'featureClasses' that do not have a given spatial relationship with any feature in 'otherFeatureClasses', or for which a given constraint is not fulfilled. The required spatial relationship is defined by a 9IM intersection matrix.
        
        Remark: The feature classes in 'featureClass' and 'relatedClass' must have the same spatial reference.
        """
        
        result = Condition("QaMustIntersectMatrixOther(2)")
        if type(feature_classes) == list:
            for element in feature_classes:
                result.parameters.append(Parameter("featureClasses", element))
        elif feature_classes is not None:
            result.parameters.append(Parameter("featureClasses", feature_classes))
        if type(other_feature_classes) == list:
            for element in other_feature_classes:
                result.parameters.append(Parameter("otherFeatureClasses", element))
        elif other_feature_classes is not None:
            result.parameters.append(Parameter("otherFeatureClasses", other_feature_classes))
        result.parameters.append(Parameter("intersectionMatrix", intersection_matrix))
        result.parameters.append(Parameter("relevantRelationCondition", relevant_relation_condition))
        result.generate_name()
        return result

    @classmethod
    def qa_must_intersect_matrix_other_3(cls, feature_classes: List[BaseDataset], other_feature_classes: List[BaseDataset], intersection_matrix: str, relevant_relation_condition: str, required_intersection_dimensions: str, unallowed_intersection_dimensions: str) -> Condition:
        """
        Finds all features in 'featureClasses' that do not have a given spatial relationship with any feature in 'otherFeatureClasses', or for which a given constraint is not fulfilled. The required spatial relationship is defined by a 9IM intersection matrix. Optionally, the required and unallowed intersection dimensions may be defined. 
        
        Remark: The feature classes in 'featureClass' and 'relatedClass' must have the same spatial reference.
        """
        
        result = Condition("QaMustIntersectMatrixOther(3)")
        if type(feature_classes) == list:
            for element in feature_classes:
                result.parameters.append(Parameter("featureClasses", element))
        elif feature_classes is not None:
            result.parameters.append(Parameter("featureClasses", feature_classes))
        if type(other_feature_classes) == list:
            for element in other_feature_classes:
                result.parameters.append(Parameter("otherFeatureClasses", element))
        elif other_feature_classes is not None:
            result.parameters.append(Parameter("otherFeatureClasses", other_feature_classes))
        result.parameters.append(Parameter("intersectionMatrix", intersection_matrix))
        result.parameters.append(Parameter("relevantRelationCondition", relevant_relation_condition))
        result.parameters.append(Parameter("requiredIntersectionDimensions", required_intersection_dimensions))
        result.parameters.append(Parameter("unallowedIntersectionDimensions", unallowed_intersection_dimensions))
        result.generate_name()
        return result

    @classmethod
    def qa_must_intersect_other_0(cls, feature_class: BaseDataset, other_feature_class: BaseDataset, relevant_relation_condition: str) -> Condition:
        """
        Finds features that don't intersect any other feature in another feature class
        """
        
        result = Condition("QaMustIntersectOther(0)")
        result.parameters.append(Parameter("featureClass", feature_class))
        result.parameters.append(Parameter("otherFeatureClass", other_feature_class))
        result.parameters.append(Parameter("relevantRelationCondition", relevant_relation_condition))
        result.generate_name()
        return result

    @classmethod
    def qa_must_intersect_other_1(cls, feature_classes: List[BaseDataset], other_feature_classes: List[BaseDataset], relevant_relation_condition: str) -> Condition:
        """
        Finds features that don't intersect any feature in a list of other feature classes
        """
        
        result = Condition("QaMustIntersectOther(1)")
        if type(feature_classes) == list:
            for element in feature_classes:
                result.parameters.append(Parameter("featureClasses", element))
        elif feature_classes is not None:
            result.parameters.append(Parameter("featureClasses", feature_classes))
        if type(other_feature_classes) == list:
            for element in other_feature_classes:
                result.parameters.append(Parameter("otherFeatureClasses", element))
        elif other_feature_classes is not None:
            result.parameters.append(Parameter("otherFeatureClasses", other_feature_classes))
        result.parameters.append(Parameter("relevantRelationCondition", relevant_relation_condition))
        result.generate_name()
        return result

    @classmethod
    def qa_must_touch_other_0(cls, feature_class: BaseDataset, other_feature_class: BaseDataset, relevant_relation_condition: str) -> Condition:
        """
        Finds features that don't touch any other feature in another feature class
        """
        
        result = Condition("QaMustTouchOther(0)")
        result.parameters.append(Parameter("featureClass", feature_class))
        result.parameters.append(Parameter("otherFeatureClass", other_feature_class))
        result.parameters.append(Parameter("relevantRelationCondition", relevant_relation_condition))
        result.generate_name()
        return result

    @classmethod
    def qa_must_touch_other_1(cls, feature_classes: List[BaseDataset], other_feature_classes: List[BaseDataset], relevant_relation_condition: str) -> Condition:
        """
        Finds features in a list of feature classes that don't touch any other feature in another list of feature classes
        """
        
        result = Condition("QaMustTouchOther(1)")
        if type(feature_classes) == list:
            for element in feature_classes:
                result.parameters.append(Parameter("featureClasses", element))
        elif feature_classes is not None:
            result.parameters.append(Parameter("featureClasses", feature_classes))
        if type(other_feature_classes) == list:
            for element in other_feature_classes:
                result.parameters.append(Parameter("otherFeatureClasses", element))
        elif other_feature_classes is not None:
            result.parameters.append(Parameter("otherFeatureClasses", other_feature_classes))
        result.parameters.append(Parameter("relevantRelationCondition", relevant_relation_condition))
        result.generate_name()
        return result

    @classmethod
    def qa_must_touch_self_0(cls, feature_class: BaseDataset, relevant_relation_condition: str) -> Condition:
        """
        Finds features that don't touch any other feature in the same feature class
        """
        
        result = Condition("QaMustTouchSelf(0)")
        result.parameters.append(Parameter("featureClass", feature_class))
        result.parameters.append(Parameter("relevantRelationCondition", relevant_relation_condition))
        result.generate_name()
        return result

    @classmethod
    def qa_must_touch_self_1(cls, feature_classes: List[BaseDataset], relevant_relation_condition: str) -> Condition:
        """
        Finds features in a list of feature classes that don't touch any other feature in the same list of feature classes
        """
        
        result = Condition("QaMustTouchSelf(1)")
        if type(feature_classes) == list:
            for element in feature_classes:
                result.parameters.append(Parameter("featureClasses", element))
        elif feature_classes is not None:
            result.parameters.append(Parameter("featureClasses", feature_classes))
        result.parameters.append(Parameter("relevantRelationCondition", relevant_relation_condition))
        result.generate_name()
        return result

    @classmethod
    def qa_neighbour_areas_0(cls, polygon_class: BaseDataset, constraint: str) -> Condition:
        """
        Finds all touching features in 'polygonClass' that do not fulfill 'constraint'
        """
        
        result = Condition("QaNeighbourAreas(0)")
        result.parameters.append(Parameter("polygonClass", polygon_class))
        result.parameters.append(Parameter("constraint", constraint))
        result.generate_name()
        return result

    @classmethod
    def qa_neighbour_areas_1(cls, polygon_class: BaseDataset, constraint: str, allow_point_intersection: bool) -> Condition:
        """
        Finds all touching features in 'polygonClass' that do not fulfill 'constraint'. Optionally allows to ignore polygon pairs that intersect in points only.
        """
        
        result = Condition("QaNeighbourAreas(1)")
        result.parameters.append(Parameter("polygonClass", polygon_class))
        result.parameters.append(Parameter("constraint", constraint))
        result.parameters.append(Parameter("allowPointIntersection", allow_point_intersection))
        result.generate_name()
        return result

    @classmethod
    def qa_neighbour_areas_2(cls, polygon_class: BaseDataset, allow_point_intersection: bool) -> Condition:
        """
        Finds all touching features in 'polygonClass' for which all values of editable attributes are equal. Optionally allows to ignore polygon pairs that intersect in points only.
        """
        
        result = Condition("QaNeighbourAreas(2)")
        result.parameters.append(Parameter("polygonClass", polygon_class))
        result.parameters.append(Parameter("allowPointIntersection", allow_point_intersection))
        result.generate_name()
        return result

    @classmethod
    def qa_neighbour_areas_3(cls, polygon_class: BaseDataset, allow_point_intersection: bool, fields_string: str, field_list_type: FieldListType) -> Condition:
        """
        Finds all touching features in 'polygonClass' for which the values of a defined list of fields are equal. This field list can be defined by a concatenated string of either relevant or ignored fields. Optionally allows to ignore polygon pairs that intersect in points only.
        """
        
        result = Condition("QaNeighbourAreas(3)")
        result.parameters.append(Parameter("polygonClass", polygon_class))
        result.parameters.append(Parameter("allowPointIntersection", allow_point_intersection))
        result.parameters.append(Parameter("fieldsString", fields_string))
        result.parameters.append(Parameter("fieldListType", field_list_type))
        result.generate_name()
        return result

    @classmethod
    def qa_neighbour_areas_4(cls, polygon_class: BaseDataset, allow_point_intersection: bool, fields: List[str], field_list_type: FieldListType) -> Condition:
        """
        Finds all touching features in 'polygonClass' for which the values of a defined list of fields are equal. This field list can be defined by a list of either relevant or ignored fields. Optionally allows to ignore polygon pairs that intersect in points only.
        """
        
        result = Condition("QaNeighbourAreas(4)")
        result.parameters.append(Parameter("polygonClass", polygon_class))
        result.parameters.append(Parameter("allowPointIntersection", allow_point_intersection))
        if type(fields) == list:
            for element in fields:
                result.parameters.append(Parameter("fields", element))
        elif fields is not None:
            result.parameters.append(Parameter("fields", fields))
        result.parameters.append(Parameter("fieldListType", field_list_type))
        result.generate_name()
        return result

    @classmethod
    def qa_no_boundary_loops_0(cls, polygon_class: BaseDataset) -> Condition:
        """
        Finds all boundary loops (closed 'bays' in polygon boundaries or multipatch rings) in a polygon or multipatch feature class and reports them as polygon errors.
        """
        
        result = Condition("QaNoBoundaryLoops(0)")
        result.parameters.append(Parameter("polygonClass", polygon_class))
        result.generate_name()
        return result

    @classmethod
    def qa_no_boundary_loops_1(cls, polygon_class: BaseDataset, error_geometry: BoundaryLoopErrorGeometry) -> Condition:
        """
        Finds all boundary loops (closed 'bays' in polygon boundaries or multipatch rings) in a polygon or multipatch feature class and reports them optionally as polygon errors or as point errors identifying the location where the boundary loop starts\/ends.
        """
        
        result = Condition("QaNoBoundaryLoops(1)")
        result.parameters.append(Parameter("polygonClass", polygon_class))
        result.parameters.append(Parameter("errorGeometry", error_geometry))
        result.generate_name()
        return result

    @classmethod
    def qa_no_boundary_loops_2(cls, polygon_class: BaseDataset, error_geometry: BoundaryLoopErrorGeometry, area_relation: BoundaryLoopAreaRelation, area_limit: float) -> Condition:
        """
        Finds all boundary loops (closed 'bays' in polygon boundaries or multipatch rings) in a polygon or multipatch feature class and reports them optionally as polygon errors or as point errors identifying the location where the boundary loop starts\/ends. 
        
        Optionally, loops larger or smaller than a given area limit can be ignored. This can be useful together with 'errorGeometry' to report loop start points specifically for large loops (in addition to reporting the loop polygons reported by a separate test), where it would otherwise be tedious to locate this start point visually.
        """
        
        result = Condition("QaNoBoundaryLoops(2)")
        result.parameters.append(Parameter("polygonClass", polygon_class))
        result.parameters.append(Parameter("errorGeometry", error_geometry))
        result.parameters.append(Parameter("areaRelation", area_relation))
        result.parameters.append(Parameter("areaLimit", area_limit))
        result.generate_name()
        return result

    @classmethod
    def qa_no_closed_paths_0(cls, poly_line_class: BaseDataset) -> Condition:
        """
        Finds closed paths (loops) in polyline features
        """
        
        result = Condition("QaNoClosedPaths(0)")
        result.parameters.append(Parameter("polyLineClass", poly_line_class))
        result.generate_name()
        return result

    @classmethod
    def qa_node_line_coincidence_0(cls, node_class: BaseDataset, near_classes: List[BaseDataset], near: float, coincidence_tolerance: float = -1) -> Condition:
        """
        Finds nodes in 'nodeClass' that are not coincident with any feature in 'nearClasses', but are within 'near' of at least one feature in 'nearClasses'
        """
        
        result = Condition("QaNodeLineCoincidence(0)")
        result.parameters.append(Parameter("nodeClass", node_class))
        if type(near_classes) == list:
            for element in near_classes:
                result.parameters.append(Parameter("nearClasses", element))
        elif near_classes is not None:
            result.parameters.append(Parameter("nearClasses", near_classes))
        result.parameters.append(Parameter("near", near))
        result.parameters.append(Parameter("CoincidenceTolerance", coincidence_tolerance))
        result.generate_name()
        return result

    @classmethod
    def qa_node_line_coincidence_1(cls, node_class: BaseDataset, near_classes: List[BaseDataset], near: float, ignore_near_endpoints: bool, coincidence_tolerance: float = -1) -> Condition:
        """
        Finds nodes in 'nodeClass' that are not coincident with any feature in 'nearClasses', but are within 'near' of at least one feature in 'nearClasses'. Optionally, only nodes near an edge but no end point are reported. This permits avoiding multiple errors when applying other tests to check for minimum node distance.
        """
        
        result = Condition("QaNodeLineCoincidence(1)")
        result.parameters.append(Parameter("nodeClass", node_class))
        if type(near_classes) == list:
            for element in near_classes:
                result.parameters.append(Parameter("nearClasses", element))
        elif near_classes is not None:
            result.parameters.append(Parameter("nearClasses", near_classes))
        result.parameters.append(Parameter("near", near))
        result.parameters.append(Parameter("ignoreNearEndpoints", ignore_near_endpoints))
        result.parameters.append(Parameter("CoincidenceTolerance", coincidence_tolerance))
        result.generate_name()
        return result

    @classmethod
    def qa_node_line_coincidence_2(cls, node_class: BaseDataset, near_classes: List[BaseDataset], near: float, ignore_near_endpoints: bool, is3_d: bool, coincidence_tolerance: float = -1) -> Condition:
        """
        Finds nodes in 'nodeClass' that are not coincident with any feature in 'nearClasses', but are within 'near' of at least one feature in 'nearClasses'. Optionally, only nodes near an edge but no end point are reported. This permits avoiding multiple errors when applying other tests to check for minimum node distance.
        """
        
        result = Condition("QaNodeLineCoincidence(2)")
        result.parameters.append(Parameter("nodeClass", node_class))
        if type(near_classes) == list:
            for element in near_classes:
                result.parameters.append(Parameter("nearClasses", element))
        elif near_classes is not None:
            result.parameters.append(Parameter("nearClasses", near_classes))
        result.parameters.append(Parameter("near", near))
        result.parameters.append(Parameter("ignoreNearEndpoints", ignore_near_endpoints))
        result.parameters.append(Parameter("is3D", is3_d))
        result.parameters.append(Parameter("CoincidenceTolerance", coincidence_tolerance))
        result.generate_name()
        return result

    @classmethod
    def qa_node_line_coincidence_3(cls, node_class: BaseDataset, near_classes: List[BaseDataset], near_tolerances: List[float], within_polyline_tolerance: float, ignore_near_endpoints: bool, is3_d: bool, coincidence_tolerance: float = -1) -> Condition:
        """
        Finds nodes in 'nodeClass' that are not coincident with any feature in 'nearClasses', but are within 'near' of at least one feature in 'nearClasses'. Optionally, individual tolerances can be specified for each feature class in 'nearClasses', and for testing within multiple polyline paths in 'nodeClass'. Optionally, only nodes near an edge but no end point are reported. This permits avoiding multiple errors when applying other tests to check for minimum node distance.
        """
        
        result = Condition("QaNodeLineCoincidence(3)")
        result.parameters.append(Parameter("nodeClass", node_class))
        if type(near_classes) == list:
            for element in near_classes:
                result.parameters.append(Parameter("nearClasses", element))
        elif near_classes is not None:
            result.parameters.append(Parameter("nearClasses", near_classes))
        if type(near_tolerances) == list:
            for element in near_tolerances:
                result.parameters.append(Parameter("nearTolerances", element))
        elif near_tolerances is not None:
            result.parameters.append(Parameter("nearTolerances", near_tolerances))
        result.parameters.append(Parameter("withinPolylineTolerance", within_polyline_tolerance))
        result.parameters.append(Parameter("ignoreNearEndpoints", ignore_near_endpoints))
        result.parameters.append(Parameter("is3D", is3_d))
        result.parameters.append(Parameter("CoincidenceTolerance", coincidence_tolerance))
        result.generate_name()
        return result

    @classmethod
    def qa_no_gaps_0(cls, polygon_class: BaseDataset, sliver_limit: float, max_area: float) -> Condition:
        """
        Finds areas in 'polygonClass' with no covering features ( = gaps)
        """
        
        result = Condition("QaNoGaps(0)")
        result.parameters.append(Parameter("polygonClass", polygon_class))
        result.parameters.append(Parameter("sliverLimit", sliver_limit))
        result.parameters.append(Parameter("maxArea", max_area))
        result.generate_name()
        return result

    @classmethod
    def qa_no_gaps_1(cls, polygon_classes: List[BaseDataset], sliver_limit: float, max_area: float) -> Condition:
        """
        Finds areas that are not covered by any feature out of 'polygonClasses' ( = gaps)
        """
        
        result = Condition("QaNoGaps(1)")
        if type(polygon_classes) == list:
            for element in polygon_classes:
                result.parameters.append(Parameter("polygonClasses", element))
        elif polygon_classes is not None:
            result.parameters.append(Parameter("polygonClasses", polygon_classes))
        result.parameters.append(Parameter("sliverLimit", sliver_limit))
        result.parameters.append(Parameter("maxArea", max_area))
        result.generate_name()
        return result

    @classmethod
    def qa_no_gaps_2(cls, polygon_class: BaseDataset, sliver_limit: float, max_area: float, subtile_width: float, find_gaps_below_tolerance: bool) -> Condition:
        """
        Finds areas in 'polygonClass' with no covering features ( = gaps)
        """
        
        result = Condition("QaNoGaps(2)")
        result.parameters.append(Parameter("polygonClass", polygon_class))
        result.parameters.append(Parameter("sliverLimit", sliver_limit))
        result.parameters.append(Parameter("maxArea", max_area))
        result.parameters.append(Parameter("subtileWidth", subtile_width))
        result.parameters.append(Parameter("findGapsBelowTolerance", find_gaps_below_tolerance))
        result.generate_name()
        return result

    @classmethod
    def qa_no_gaps_3(cls, polygon_classes: List[BaseDataset], sliver_limit: float, max_area: float, subtile_width: float, find_gaps_below_tolerance: bool) -> Condition:
        """
        Finds areas that are not covered by any feature out of 'polygonClasses' ( = gaps)
        """
        
        result = Condition("QaNoGaps(3)")
        if type(polygon_classes) == list:
            for element in polygon_classes:
                result.parameters.append(Parameter("polygonClasses", element))
        elif polygon_classes is not None:
            result.parameters.append(Parameter("polygonClasses", polygon_classes))
        result.parameters.append(Parameter("sliverLimit", sliver_limit))
        result.parameters.append(Parameter("maxArea", max_area))
        result.parameters.append(Parameter("subtileWidth", subtile_width))
        result.parameters.append(Parameter("findGapsBelowTolerance", find_gaps_below_tolerance))
        result.generate_name()
        return result

    @classmethod
    def qa_no_gaps_4(cls, polygon_classes: List[BaseDataset], sliver_limit: float, max_area: float, area_of_interest_classes: List[BaseDataset]) -> Condition:
        """
        Finds areas inside polygons in 'areaOfInterestClasses' that are not covered by any feature out of 'polygonClasses' ( = gaps)
        """
        
        result = Condition("QaNoGaps(4)")
        if type(polygon_classes) == list:
            for element in polygon_classes:
                result.parameters.append(Parameter("polygonClasses", element))
        elif polygon_classes is not None:
            result.parameters.append(Parameter("polygonClasses", polygon_classes))
        result.parameters.append(Parameter("sliverLimit", sliver_limit))
        result.parameters.append(Parameter("maxArea", max_area))
        if type(area_of_interest_classes) == list:
            for element in area_of_interest_classes:
                result.parameters.append(Parameter("areaOfInterestClasses", element))
        elif area_of_interest_classes is not None:
            result.parameters.append(Parameter("areaOfInterestClasses", area_of_interest_classes))
        result.generate_name()
        return result

    @classmethod
    def qa_no_gaps_5(cls, polygon_classes: List[BaseDataset], sliver_limit: float, max_area: float, subtile_width: float, find_gaps_below_tolerance: bool, area_of_interest_classes: List[BaseDataset]) -> Condition:
        """
        Finds areas inside polygons in 'areaOfInterestClasses' that are not covered by any feature out of 'polygonClasses' ( = gaps)
        """
        
        result = Condition("QaNoGaps(5)")
        if type(polygon_classes) == list:
            for element in polygon_classes:
                result.parameters.append(Parameter("polygonClasses", element))
        elif polygon_classes is not None:
            result.parameters.append(Parameter("polygonClasses", polygon_classes))
        result.parameters.append(Parameter("sliverLimit", sliver_limit))
        result.parameters.append(Parameter("maxArea", max_area))
        result.parameters.append(Parameter("subtileWidth", subtile_width))
        result.parameters.append(Parameter("findGapsBelowTolerance", find_gaps_below_tolerance))
        if type(area_of_interest_classes) == list:
            for element in area_of_interest_classes:
                result.parameters.append(Parameter("areaOfInterestClasses", element))
        elif area_of_interest_classes is not None:
            result.parameters.append(Parameter("areaOfInterestClasses", area_of_interest_classes))
        result.generate_name()
        return result

    @classmethod
    def qa_non_empty_geometry_0(cls, feature_class: BaseDataset) -> Condition:
        """
        Finds all features in 'featureClass' with null or empty geometries.
        """
        
        result = Condition("QaNonEmptyGeometry(0)")
        result.parameters.append(Parameter("featureClass", feature_class))
        result.generate_name()
        return result

    @classmethod
    def qa_non_empty_geometry_1(cls, feature_class: BaseDataset, dont_filter_polycurves_by_zero_length: bool) -> Condition:
        """
        Finds all features in 'featureClass' with null or empty geometries.
        """
        
        result = Condition("QaNonEmptyGeometry(1)")
        result.parameters.append(Parameter("featureClass", feature_class))
        result.parameters.append(Parameter("dontFilterPolycurvesByZeroLength", dont_filter_polycurves_by_zero_length))
        result.generate_name()
        return result

    @classmethod
    def qa_not_near_0(cls, feature_class: BaseDataset, near: float, min_length: float, is3_d: bool, ignore_neighbor_condition: str = None) -> Condition:
        """
        Finds all line sections longer than 'minLength' in 'featureClass' that are closer than 'near' to any other line in 'featureClass'.
        """
        
        result = Condition("QaNotNear(0)")
        result.parameters.append(Parameter("featureClass", feature_class))
        result.parameters.append(Parameter("near", near))
        result.parameters.append(Parameter("minLength", min_length))
        result.parameters.append(Parameter("is3D", is3_d))
        result.parameters.append(Parameter("IgnoreNeighborCondition", ignore_neighbor_condition))
        result.generate_name()
        return result

    @classmethod
    def qa_not_near_1(cls, feature_class: BaseDataset, near: float, min_length: float, is3_d: bool, tile_size: float, ignore_neighbor_condition: str = None) -> Condition:
        """
        Finds all line sections longer than 'minLength' in 'featureClass' that are closer than 'near' to any other line in 'featureClass'.
        """
        
        result = Condition("QaNotNear(1)")
        result.parameters.append(Parameter("featureClass", feature_class))
        result.parameters.append(Parameter("near", near))
        result.parameters.append(Parameter("minLength", min_length))
        result.parameters.append(Parameter("is3D", is3_d))
        result.parameters.append(Parameter("tileSize", tile_size))
        result.parameters.append(Parameter("IgnoreNeighborCondition", ignore_neighbor_condition))
        result.generate_name()
        return result

    @classmethod
    def qa_not_near_2(cls, feature_class: BaseDataset, reference: BaseDataset, near: float, min_length: float, is3_d: bool, ignore_neighbor_condition: str = None) -> Condition:
        """
        Finds all line sections in 'featureClass' longer than 'minLength' that are closer than 'near' to any line in 'reference'.
        
        Remark: The feature classes in 'featureClass' and 'reference' must have the same spatial reference.
        """
        
        result = Condition("QaNotNear(2)")
        result.parameters.append(Parameter("featureClass", feature_class))
        result.parameters.append(Parameter("reference", reference))
        result.parameters.append(Parameter("near", near))
        result.parameters.append(Parameter("minLength", min_length))
        result.parameters.append(Parameter("is3D", is3_d))
        result.parameters.append(Parameter("IgnoreNeighborCondition", ignore_neighbor_condition))
        result.generate_name()
        return result

    @classmethod
    def qa_not_near_3(cls, feature_class: BaseDataset, reference: BaseDataset, near: float, min_length: float, is3_d: bool, tile_size: float, ignore_neighbor_condition: str = None) -> Condition:
        """
        Finds all line sections in 'featureClass' longer than 'minLength' that are closer than 'near' to any line in 'reference'.
        
        Remark: The feature classes in 'featureClass' and 'reference' must have the same spatial reference.
        """
        
        result = Condition("QaNotNear(3)")
        result.parameters.append(Parameter("featureClass", feature_class))
        result.parameters.append(Parameter("reference", reference))
        result.parameters.append(Parameter("near", near))
        result.parameters.append(Parameter("minLength", min_length))
        result.parameters.append(Parameter("is3D", is3_d))
        result.parameters.append(Parameter("tileSize", tile_size))
        result.parameters.append(Parameter("IgnoreNeighborCondition", ignore_neighbor_condition))
        result.generate_name()
        return result

    @classmethod
    def qa_not_near_4(cls, feature_class: BaseDataset, near: float, min_length: float, ignore_neighbor_condition: str = None) -> Condition:
        """
        Finds all line sections longer than 'minLength' in 'featureClass' that are closer than 'near' to any other line in 'featureClass'.
        """
        
        result = Condition("QaNotNear(4)")
        result.parameters.append(Parameter("featureClass", feature_class))
        result.parameters.append(Parameter("near", near))
        result.parameters.append(Parameter("minLength", min_length))
        result.parameters.append(Parameter("IgnoreNeighborCondition", ignore_neighbor_condition))
        result.generate_name()
        return result

    @classmethod
    def qa_not_near_5(cls, feature_class: BaseDataset, near: float, min_length: float, tile_size: float, ignore_neighbor_condition: str = None) -> Condition:
        """
        Finds all line sections longer than 'minLength' in 'featureClass' that are closer than 'near' to any other line in 'featureClass'.
        """
        
        result = Condition("QaNotNear(5)")
        result.parameters.append(Parameter("featureClass", feature_class))
        result.parameters.append(Parameter("near", near))
        result.parameters.append(Parameter("minLength", min_length))
        result.parameters.append(Parameter("tileSize", tile_size))
        result.parameters.append(Parameter("IgnoreNeighborCondition", ignore_neighbor_condition))
        result.generate_name()
        return result

    @classmethod
    def qa_not_near_6(cls, feature_class: BaseDataset, reference: BaseDataset, near: float, min_length: float, ignore_neighbor_condition: str = None) -> Condition:
        """
        Finds all line sections in 'featureClass' longer than 'minLength' that are closer than 'near' to any line in 'reference'.
        
        Remark: The feature classes in 'featureClass' and 'reference' must have the same spatial reference.
        """
        
        result = Condition("QaNotNear(6)")
        result.parameters.append(Parameter("featureClass", feature_class))
        result.parameters.append(Parameter("reference", reference))
        result.parameters.append(Parameter("near", near))
        result.parameters.append(Parameter("minLength", min_length))
        result.parameters.append(Parameter("IgnoreNeighborCondition", ignore_neighbor_condition))
        result.generate_name()
        return result

    @classmethod
    def qa_not_near_7(cls, feature_class: BaseDataset, reference: BaseDataset, near: float, min_length: float, tile_size: float, ignore_neighbor_condition: str = None) -> Condition:
        """
        Finds all line sections in 'featureClass' longer than 'minLength' that are closer than 'near' to any line in 'reference'.
        
        Remark: The feature classes in 'featureClass' and 'reference' must have the same spatial reference.
        """
        
        result = Condition("QaNotNear(7)")
        result.parameters.append(Parameter("featureClass", feature_class))
        result.parameters.append(Parameter("reference", reference))
        result.parameters.append(Parameter("near", near))
        result.parameters.append(Parameter("minLength", min_length))
        result.parameters.append(Parameter("tileSize", tile_size))
        result.parameters.append(Parameter("IgnoreNeighborCondition", ignore_neighbor_condition))
        result.generate_name()
        return result

    @classmethod
    def qa_no_touching_parts_0(cls, feature_class: BaseDataset) -> Condition:
        """
        Finds points in polygon or polyline features where parts of the same feature touch
        """
        
        result = Condition("QaNoTouchingParts(0)")
        result.parameters.append(Parameter("featureClass", feature_class))
        result.generate_name()
        return result

    @classmethod
    def qa_orphan_node_0(cls, point_classes: List[BaseDataset], polyline_classes: List[BaseDataset]) -> Condition:
        """
        Finds all points in 'pointClasses' that are neither From- nor To-point of any feature in 'polylineClasses' and line end points without any point
        
        Remark: All feature classes in 'pointClasses' and 'polylineClasses' must have the same spatial reference.
        """
        
        result = Condition("QaOrphanNode(0)")
        if type(point_classes) == list:
            for element in point_classes:
                result.parameters.append(Parameter("pointClasses", element))
        elif point_classes is not None:
            result.parameters.append(Parameter("pointClasses", point_classes))
        if type(polyline_classes) == list:
            for element in polyline_classes:
                result.parameters.append(Parameter("polylineClasses", element))
        elif polyline_classes is not None:
            result.parameters.append(Parameter("polylineClasses", polyline_classes))
        result.generate_name()
        return result

    @classmethod
    def qa_orphan_node_1(cls, point_class: BaseDataset, polyline_class: BaseDataset) -> Condition:
        """
        Finds all points in 'pointClass' that are neither From- nor To-point of any feature in 'polylineClass' and line end points without any point
        
        Remark: The feature classes in 'pointClass' and 'polylineClass' must have the same spatial reference.
        """
        
        result = Condition("QaOrphanNode(1)")
        result.parameters.append(Parameter("pointClass", point_class))
        result.parameters.append(Parameter("polylineClass", polyline_class))
        result.generate_name()
        return result

    @classmethod
    def qa_orphan_node_2(cls, point_classes: List[BaseDataset], polyline_classes: List[BaseDataset], error_type: OrphanErrorType) -> Condition:
        """
        Finds all points in 'pointClasses' that are neither From- nor To-point of any feature in 'polylineClasses' and\/or line end points without any point
        Performs the tests defined in 'errorType'.
        
        Remark: All feature classes in 'pointClasses' and 'polylineClasses' must have the same spatial reference.
        """
        
        result = Condition("QaOrphanNode(2)")
        if type(point_classes) == list:
            for element in point_classes:
                result.parameters.append(Parameter("pointClasses", element))
        elif point_classes is not None:
            result.parameters.append(Parameter("pointClasses", point_classes))
        if type(polyline_classes) == list:
            for element in polyline_classes:
                result.parameters.append(Parameter("polylineClasses", element))
        elif polyline_classes is not None:
            result.parameters.append(Parameter("polylineClasses", polyline_classes))
        result.parameters.append(Parameter("errorType", error_type))
        result.generate_name()
        return result

    @classmethod
    def qa_orphan_node_3(cls, point_class: BaseDataset, polyline_class: BaseDataset, error_type: OrphanErrorType) -> Condition:
        """
        Finds all points in 'pointClass' that are neither From- nor To-point of any feature in 'polylineClass' and\/or line end points without any point
        Performs the tests defined in 'errorType'.
        
        Remark: The feature classes in 'pointClass' and 'polylineClass' must have the same spatial reference.
        """
        
        result = Condition("QaOrphanNode(3)")
        result.parameters.append(Parameter("pointClass", point_class))
        result.parameters.append(Parameter("polylineClass", polyline_class))
        result.parameters.append(Parameter("errorType", error_type))
        result.generate_name()
        return result

    @classmethod
    def qa_overlaps_other_0(cls, overlapped: List[BaseDataset], overlapping: List[BaseDataset]) -> Condition:
        """
        Finds features in 'overlappingClasses' overlapping with any feature in 'overlappedClasses'
        
        Remark: All feature classes in 'overlappedClasses' and 'overlappingClasses' must have the same spatial reference.
        """
        
        result = Condition("QaOverlapsOther(0)")
        if type(overlapped) == list:
            for element in overlapped:
                result.parameters.append(Parameter("overlapped", element))
        elif overlapped is not None:
            result.parameters.append(Parameter("overlapped", overlapped))
        if type(overlapping) == list:
            for element in overlapping:
                result.parameters.append(Parameter("overlapping", element))
        elif overlapping is not None:
            result.parameters.append(Parameter("overlapping", overlapping))
        result.generate_name()
        return result

    @classmethod
    def qa_overlaps_other_1(cls, overlapped: BaseDataset, overlapping: BaseDataset) -> Condition:
        """
        Finds features in 'overlappingClass' overlapping with any feature in 'overlappedClass'
        
        Remark: The feature classes 'overlappedClass' and 'overlappingClass' must have the same spatial reference.
        """
        
        result = Condition("QaOverlapsOther(1)")
        result.parameters.append(Parameter("overlapped", overlapped))
        result.parameters.append(Parameter("overlapping", overlapping))
        result.generate_name()
        return result

    @classmethod
    def qa_overlaps_other_2(cls, overlapped_classes: List[BaseDataset], overlapping_classes: List[BaseDataset], valid_relation_constraint: str) -> Condition:
        """
        Finds features in 'overlappingClasses' overlapping with any feature in 'overlappedClasses', and for which a given constraint is not fulfilled.
        
        Remark: All feature classes in 'overlappedClasses' and 'overlappingClasses' must have the same spatial reference.
        """
        
        result = Condition("QaOverlapsOther(2)")
        if type(overlapped_classes) == list:
            for element in overlapped_classes:
                result.parameters.append(Parameter("overlappedClasses", element))
        elif overlapped_classes is not None:
            result.parameters.append(Parameter("overlappedClasses", overlapped_classes))
        if type(overlapping_classes) == list:
            for element in overlapping_classes:
                result.parameters.append(Parameter("overlappingClasses", element))
        elif overlapping_classes is not None:
            result.parameters.append(Parameter("overlappingClasses", overlapping_classes))
        result.parameters.append(Parameter("validRelationConstraint", valid_relation_constraint))
        result.generate_name()
        return result

    @classmethod
    def qa_overlaps_other_3(cls, overlapped_class: BaseDataset, overlapping_class: BaseDataset, valid_relation_constraint: str) -> Condition:
        """
        Finds features in 'overlappingClass' overlapping with any feature in 'overlappedClass', and for which a given constraint is not fulfilled.
        
        Remark: The feature classes 'overlappedClass' and 'overlappingClass' must have the same spatial reference.
        """
        
        result = Condition("QaOverlapsOther(3)")
        result.parameters.append(Parameter("overlappedClass", overlapped_class))
        result.parameters.append(Parameter("overlappingClass", overlapping_class))
        result.parameters.append(Parameter("validRelationConstraint", valid_relation_constraint))
        result.generate_name()
        return result

    @classmethod
    def qa_overlaps_self_0(cls, feature_class: BaseDataset) -> Condition:
        """
        Finds all features in 'featureClass' that overlap any feature in 'featureClass'
        """
        
        result = Condition("QaOverlapsSelf(0)")
        result.parameters.append(Parameter("featureClass", feature_class))
        result.generate_name()
        return result

    @classmethod
    def qa_overlaps_self_1(cls, feature_classes: List[BaseDataset]) -> Condition:
        """
        Finds all features in 'featureClasses' that overlap any feature in 'featureClasses'
        """
        
        result = Condition("QaOverlapsSelf(1)")
        if type(feature_classes) == list:
            for element in feature_classes:
                result.parameters.append(Parameter("featureClasses", element))
        elif feature_classes is not None:
            result.parameters.append(Parameter("featureClasses", feature_classes))
        result.generate_name()
        return result

    @classmethod
    def qa_overlaps_self_2(cls, feature_classes: List[BaseDataset], valid_relation_constraint: str) -> Condition:
        """
        Finds all features in 'featureClasses' that overlap any feature in 'featureClasses', and for which a given constraint is not fulfilled.
        """
        
        result = Condition("QaOverlapsSelf(2)")
        if type(feature_classes) == list:
            for element in feature_classes:
                result.parameters.append(Parameter("featureClasses", element))
        elif feature_classes is not None:
            result.parameters.append(Parameter("featureClasses", feature_classes))
        result.parameters.append(Parameter("validRelationConstraint", valid_relation_constraint))
        result.generate_name()
        return result

    @classmethod
    def qa_overlaps_self_3(cls, feature_class: BaseDataset, valid_relation_constraint: str) -> Condition:
        """
        Finds all features in 'featureClass' that overlap any feature in 'featureClass', and for which a given constraint is not fulfilled.
        """
        
        result = Condition("QaOverlapsSelf(3)")
        result.parameters.append(Parameter("featureClass", feature_class))
        result.parameters.append(Parameter("validRelationConstraint", valid_relation_constraint))
        result.generate_name()
        return result

    @classmethod
    def qa_part_coincidence_other_0(cls, feature_class: BaseDataset, reference: BaseDataset, near: float, min_length: float, is3_d: bool, ignore_neighbor_condition: str = None) -> Condition:
        """
        Find line sections longer than 'minLength' in 'featureClass', that lie nearer than 'near' to lines in 'reference' but are not coincident.
        
        Remark: All feature classes in 'featureClass' and 'reference' must have the same spatial reference.
        """
        
        result = Condition("QaPartCoincidenceOther(0)")
        result.parameters.append(Parameter("featureClass", feature_class))
        result.parameters.append(Parameter("reference", reference))
        result.parameters.append(Parameter("near", near))
        result.parameters.append(Parameter("minLength", min_length))
        result.parameters.append(Parameter("is3D", is3_d))
        result.parameters.append(Parameter("IgnoreNeighborCondition", ignore_neighbor_condition))
        result.generate_name()
        return result

    @classmethod
    def qa_part_coincidence_other_1(cls, feature_class: BaseDataset, reference: BaseDataset, near: float, min_length: float, is3_d: bool, tile_size: float, ignore_neighbor_condition: str = None) -> Condition:
        """
        Find line sections longer than 'minLength' in 'featureClass', that lie nearer than 'near' to lines in 'reference' but are not coincident.
        
        Remark: All feature classes in 'featureClass' and 'reference' must have the same spatial reference.
        """
        
        result = Condition("QaPartCoincidenceOther(1)")
        result.parameters.append(Parameter("featureClass", feature_class))
        result.parameters.append(Parameter("reference", reference))
        result.parameters.append(Parameter("near", near))
        result.parameters.append(Parameter("minLength", min_length))
        result.parameters.append(Parameter("is3D", is3_d))
        result.parameters.append(Parameter("tileSize", tile_size))
        result.parameters.append(Parameter("IgnoreNeighborCondition", ignore_neighbor_condition))
        result.generate_name()
        return result

    @classmethod
    def qa_part_coincidence_other_2(cls, feature_class: BaseDataset, reference: BaseDataset, near: float, min_length: float, ignore_neighbor_condition: str = None) -> Condition:
        """
        Find line sections longer than 'minLength' in 'featureClass', that lie nearer than 'near' to lines in 'reference' but are not coincident.
        
        Remark: All feature classes in 'featureClass' and 'reference' must have the same spatial reference.
        """
        
        result = Condition("QaPartCoincidenceOther(2)")
        result.parameters.append(Parameter("featureClass", feature_class))
        result.parameters.append(Parameter("reference", reference))
        result.parameters.append(Parameter("near", near))
        result.parameters.append(Parameter("minLength", min_length))
        result.parameters.append(Parameter("IgnoreNeighborCondition", ignore_neighbor_condition))
        result.generate_name()
        return result

    @classmethod
    def qa_part_coincidence_other_3(cls, feature_class: BaseDataset, reference: BaseDataset, near: float, min_length: float, tile_size: float, ignore_neighbor_condition: str = None) -> Condition:
        """
        Find line sections longer than 'minLength' in 'featureClass', that lie nearer than 'near' to lines in 'reference' but are not coincident.
        
        Remark: All feature classes in 'featureClass' and 'reference' must have the same spatial reference.
        """
        
        result = Condition("QaPartCoincidenceOther(3)")
        result.parameters.append(Parameter("featureClass", feature_class))
        result.parameters.append(Parameter("reference", reference))
        result.parameters.append(Parameter("near", near))
        result.parameters.append(Parameter("minLength", min_length))
        result.parameters.append(Parameter("tileSize", tile_size))
        result.parameters.append(Parameter("IgnoreNeighborCondition", ignore_neighbor_condition))
        result.generate_name()
        return result

    @classmethod
    def qa_part_coincidence_other_4(cls, feature_class: BaseDataset, reference: BaseDataset, near: float, connected_min_length: float, disjoint_min_length: float, is3_d: bool, tile_size: float, coincidence_tolerance: float, ignore_neighbor_condition: str = None) -> Condition:
        """
        Find line sections longer than a specified minimum length in 'featureClass', that lie nearer than 'near' to lines in 'reference' but are not coincident. The minimum length can be defined separately for line pairs that are connected ('connectedMinLength') or disjoint ('disjointMinLength'). A coincidence tolerance can be specified to indicate a maximum allowed offset between the lines at which they are still considered to be coincident.
        
        Remark: All feature classes in 'featureClass' and 'reference' must have the same spatial reference.
        """
        
        result = Condition("QaPartCoincidenceOther(4)")
        result.parameters.append(Parameter("featureClass", feature_class))
        result.parameters.append(Parameter("reference", reference))
        result.parameters.append(Parameter("near", near))
        result.parameters.append(Parameter("connectedMinLength", connected_min_length))
        result.parameters.append(Parameter("disjointMinLength", disjoint_min_length))
        result.parameters.append(Parameter("is3D", is3_d))
        result.parameters.append(Parameter("tileSize", tile_size))
        result.parameters.append(Parameter("coincidenceTolerance", coincidence_tolerance))
        result.parameters.append(Parameter("IgnoreNeighborCondition", ignore_neighbor_condition))
        result.generate_name()
        return result

    @classmethod
    def qa_part_coincidence_self_0(cls, feature_class: BaseDataset, near: float, min_length: float, is3_d: bool, ignore_neighbor_conditions: List[str] = None) -> Condition:
        """
        Find line sections longer than 'minLength' in 'featureClass', where 2 non-coincident lines lie nearer than 'near' but are not coincident.
        """
        
        result = Condition("QaPartCoincidenceSelf(0)")
        result.parameters.append(Parameter("featureClass", feature_class))
        result.parameters.append(Parameter("near", near))
        result.parameters.append(Parameter("minLength", min_length))
        result.parameters.append(Parameter("is3D", is3_d))
        if type(ignore_neighbor_conditions) == list:
            for element in ignore_neighbor_conditions:
                result.parameters.append(Parameter("IgnoreNeighborConditions", element))
        elif ignore_neighbor_conditions is not None:
            result.parameters.append(Parameter("IgnoreNeighborConditions", ignore_neighbor_conditions))
        result.generate_name()
        return result

    @classmethod
    def qa_part_coincidence_self_1(cls, feature_class: BaseDataset, near: float, min_length: float, is3_d: bool, tile_size: float, ignore_neighbor_conditions: List[str] = None) -> Condition:
        """
        Find line sections longer than 'minLength' in 'featureClass', where 2 non-coincident lines lie nearer than 'near' but are not coincident.
        """
        
        result = Condition("QaPartCoincidenceSelf(1)")
        result.parameters.append(Parameter("featureClass", feature_class))
        result.parameters.append(Parameter("near", near))
        result.parameters.append(Parameter("minLength", min_length))
        result.parameters.append(Parameter("is3D", is3_d))
        result.parameters.append(Parameter("tileSize", tile_size))
        if type(ignore_neighbor_conditions) == list:
            for element in ignore_neighbor_conditions:
                result.parameters.append(Parameter("IgnoreNeighborConditions", element))
        elif ignore_neighbor_conditions is not None:
            result.parameters.append(Parameter("IgnoreNeighborConditions", ignore_neighbor_conditions))
        result.generate_name()
        return result

    @classmethod
    def qa_part_coincidence_self_2(cls, feature_classes: List[BaseDataset], near: float, min_length: float, is3_d: bool, ignore_neighbor_conditions: List[str] = None) -> Condition:
        """
        Find line sections longer than 'minLength' in 'featureClasses', where 2 non-coincident lines lie nearer than 'near', but are not coincident.
        
        Remark: All feature classes in 'featureClasses' must have the same spatial reference.
        """
        
        result = Condition("QaPartCoincidenceSelf(2)")
        if type(feature_classes) == list:
            for element in feature_classes:
                result.parameters.append(Parameter("featureClasses", element))
        elif feature_classes is not None:
            result.parameters.append(Parameter("featureClasses", feature_classes))
        result.parameters.append(Parameter("near", near))
        result.parameters.append(Parameter("minLength", min_length))
        result.parameters.append(Parameter("is3D", is3_d))
        if type(ignore_neighbor_conditions) == list:
            for element in ignore_neighbor_conditions:
                result.parameters.append(Parameter("IgnoreNeighborConditions", element))
        elif ignore_neighbor_conditions is not None:
            result.parameters.append(Parameter("IgnoreNeighborConditions", ignore_neighbor_conditions))
        result.generate_name()
        return result

    @classmethod
    def qa_part_coincidence_self_3(cls, feature_classes: List[BaseDataset], near: float, min_length: float, is3_d: bool, tile_size: float, ignore_neighbor_conditions: List[str] = None) -> Condition:
        """
        Find line sections longer than 'minLength' in 'featureClasses', where 2 non-coincident lines lie nearer than 'near', but are not coincident.
        
        Remark: All feature classes in 'featureClasses' must have the same spatial reference.
        """
        
        result = Condition("QaPartCoincidenceSelf(3)")
        if type(feature_classes) == list:
            for element in feature_classes:
                result.parameters.append(Parameter("featureClasses", element))
        elif feature_classes is not None:
            result.parameters.append(Parameter("featureClasses", feature_classes))
        result.parameters.append(Parameter("near", near))
        result.parameters.append(Parameter("minLength", min_length))
        result.parameters.append(Parameter("is3D", is3_d))
        result.parameters.append(Parameter("tileSize", tile_size))
        if type(ignore_neighbor_conditions) == list:
            for element in ignore_neighbor_conditions:
                result.parameters.append(Parameter("IgnoreNeighborConditions", element))
        elif ignore_neighbor_conditions is not None:
            result.parameters.append(Parameter("IgnoreNeighborConditions", ignore_neighbor_conditions))
        result.generate_name()
        return result

    @classmethod
    def qa_part_coincidence_self_4(cls, feature_classes: List[BaseDataset], near: float, min_length: float, ignore_neighbor_conditions: List[str] = None) -> Condition:
        """
        Find line sections longer than 'minLength' in 'featureClasses', where 2 non-coincident lines lie nearer than 'near', but are not coincident.
        
        Remark: All feature classes in 'featureClasses' must have the same spatial reference.
        """
        
        result = Condition("QaPartCoincidenceSelf(4)")
        if type(feature_classes) == list:
            for element in feature_classes:
                result.parameters.append(Parameter("featureClasses", element))
        elif feature_classes is not None:
            result.parameters.append(Parameter("featureClasses", feature_classes))
        result.parameters.append(Parameter("near", near))
        result.parameters.append(Parameter("minLength", min_length))
        if type(ignore_neighbor_conditions) == list:
            for element in ignore_neighbor_conditions:
                result.parameters.append(Parameter("IgnoreNeighborConditions", element))
        elif ignore_neighbor_conditions is not None:
            result.parameters.append(Parameter("IgnoreNeighborConditions", ignore_neighbor_conditions))
        result.generate_name()
        return result

    @classmethod
    def qa_part_coincidence_self_5(cls, feature_classes: List[BaseDataset], near: float, min_length: float, tile_size: float, ignore_neighbor_conditions: List[str] = None) -> Condition:
        """
        Find line sections longer than 'minLength' in 'featureClasses', where 2 non-coincident lines lie nearer than 'near', but are not coincident.
        
        Remark: All feature classes in 'featureClasses' must have the same spatial reference.
        """
        
        result = Condition("QaPartCoincidenceSelf(5)")
        if type(feature_classes) == list:
            for element in feature_classes:
                result.parameters.append(Parameter("featureClasses", element))
        elif feature_classes is not None:
            result.parameters.append(Parameter("featureClasses", feature_classes))
        result.parameters.append(Parameter("near", near))
        result.parameters.append(Parameter("minLength", min_length))
        result.parameters.append(Parameter("tileSize", tile_size))
        if type(ignore_neighbor_conditions) == list:
            for element in ignore_neighbor_conditions:
                result.parameters.append(Parameter("IgnoreNeighborConditions", element))
        elif ignore_neighbor_conditions is not None:
            result.parameters.append(Parameter("IgnoreNeighborConditions", ignore_neighbor_conditions))
        result.generate_name()
        return result

    @classmethod
    def qa_part_coincidence_self_6(cls, feature_classes: List[BaseDataset], near: float, connected_min_length: float, disjoint_min_length: float, is3_d: bool, tile_size: float, coincidence_tolerance: float, ignore_neighbor_conditions: List[str] = None) -> Condition:
        """
        Find line sections longer than a specified minimum length in 'featureClasses', where 2 non-coincident lines lie nearer than 'near', but are not coincident. The minimum length can be defined separately for line pairs that are connected ('connectedMinLength') or disjoint ('disjointMinLength'). A coincidence tolerance can be specified to indicate a maximum allowed offset between the lines at which they are still considered to be coincident.
        
        Remark: All feature classes in 'featureClasses' must have the same spatial reference.
        """
        
        result = Condition("QaPartCoincidenceSelf(6)")
        if type(feature_classes) == list:
            for element in feature_classes:
                result.parameters.append(Parameter("featureClasses", element))
        elif feature_classes is not None:
            result.parameters.append(Parameter("featureClasses", feature_classes))
        result.parameters.append(Parameter("near", near))
        result.parameters.append(Parameter("connectedMinLength", connected_min_length))
        result.parameters.append(Parameter("disjointMinLength", disjoint_min_length))
        result.parameters.append(Parameter("is3D", is3_d))
        result.parameters.append(Parameter("tileSize", tile_size))
        result.parameters.append(Parameter("coincidenceTolerance", coincidence_tolerance))
        if type(ignore_neighbor_conditions) == list:
            for element in ignore_neighbor_conditions:
                result.parameters.append(Parameter("IgnoreNeighborConditions", element))
        elif ignore_neighbor_conditions is not None:
            result.parameters.append(Parameter("IgnoreNeighborConditions", ignore_neighbor_conditions))
        result.generate_name()
        return result

    @classmethod
    def qa_point_not_near_0(cls, point_class: BaseDataset, reference_class: BaseDataset, limit: float, allow_coincident_points: bool = False, geometry_components: List[GeometryComponent] = 0, valid_relation_constraints: List[str] = None, minimum_error_line_length: float = -1) -> Condition:
        """
        Finds points in 'pointClass' that are closer than 'limit' to feature geometries (or geometry components) in 'referenceClass'. 
        """
        
        result = Condition("QaPointNotNear(0)")
        result.parameters.append(Parameter("pointClass", point_class))
        result.parameters.append(Parameter("referenceClass", reference_class))
        result.parameters.append(Parameter("limit", limit))
        result.parameters.append(Parameter("AllowCoincidentPoints", allow_coincident_points))
        if type(geometry_components) == list:
            for element in geometry_components:
                result.parameters.append(Parameter("GeometryComponents", element))
        elif geometry_components is not None:
            result.parameters.append(Parameter("GeometryComponents", geometry_components))
        if type(valid_relation_constraints) == list:
            for element in valid_relation_constraints:
                result.parameters.append(Parameter("ValidRelationConstraints", element))
        elif valid_relation_constraints is not None:
            result.parameters.append(Parameter("ValidRelationConstraints", valid_relation_constraints))
        result.parameters.append(Parameter("MinimumErrorLineLength", minimum_error_line_length))
        result.generate_name()
        return result

    @classmethod
    def qa_point_not_near_1(cls, point_class: BaseDataset, reference_classes: List[BaseDataset], limit: float, allow_coincident_points: bool = False, geometry_components: List[GeometryComponent] = 0, valid_relation_constraints: List[str] = None, minimum_error_line_length: float = -1) -> Condition:
        """
        Finds points in 'pointClass' that are closer than 'limit' to feature geometries (or geometry components) in 'referenceClasses'.
        """
        
        result = Condition("QaPointNotNear(1)")
        result.parameters.append(Parameter("pointClass", point_class))
        if type(reference_classes) == list:
            for element in reference_classes:
                result.parameters.append(Parameter("referenceClasses", element))
        elif reference_classes is not None:
            result.parameters.append(Parameter("referenceClasses", reference_classes))
        result.parameters.append(Parameter("limit", limit))
        result.parameters.append(Parameter("AllowCoincidentPoints", allow_coincident_points))
        if type(geometry_components) == list:
            for element in geometry_components:
                result.parameters.append(Parameter("GeometryComponents", element))
        elif geometry_components is not None:
            result.parameters.append(Parameter("GeometryComponents", geometry_components))
        if type(valid_relation_constraints) == list:
            for element in valid_relation_constraints:
                result.parameters.append(Parameter("ValidRelationConstraints", element))
        elif valid_relation_constraints is not None:
            result.parameters.append(Parameter("ValidRelationConstraints", valid_relation_constraints))
        result.parameters.append(Parameter("MinimumErrorLineLength", minimum_error_line_length))
        result.generate_name()
        return result

    @classmethod
    def qa_point_not_near_2(cls, point_class: BaseDataset, reference_classes: List[BaseDataset], search_distance: float, point_distance_expression: str, reference_distance_expressions: List[str], allow_coincident_points: bool = False, geometry_components: List[GeometryComponent] = 0, valid_relation_constraints: List[str] = None, minimum_error_line_length: float = -1) -> Condition:
        """
        Finds points in 'pointClass' that are closer to feature geometries (or geometry components) in 'referenceClasses' than the sum of distances derived from attribute expressions for the point feature and a reference feature.
        """
        
        result = Condition("QaPointNotNear(2)")
        result.parameters.append(Parameter("pointClass", point_class))
        if type(reference_classes) == list:
            for element in reference_classes:
                result.parameters.append(Parameter("referenceClasses", element))
        elif reference_classes is not None:
            result.parameters.append(Parameter("referenceClasses", reference_classes))
        result.parameters.append(Parameter("searchDistance", search_distance))
        result.parameters.append(Parameter("pointDistanceExpression", point_distance_expression))
        if type(reference_distance_expressions) == list:
            for element in reference_distance_expressions:
                result.parameters.append(Parameter("referenceDistanceExpressions", element))
        elif reference_distance_expressions is not None:
            result.parameters.append(Parameter("referenceDistanceExpressions", reference_distance_expressions))
        result.parameters.append(Parameter("AllowCoincidentPoints", allow_coincident_points))
        if type(geometry_components) == list:
            for element in geometry_components:
                result.parameters.append(Parameter("GeometryComponents", element))
        elif geometry_components is not None:
            result.parameters.append(Parameter("GeometryComponents", geometry_components))
        if type(valid_relation_constraints) == list:
            for element in valid_relation_constraints:
                result.parameters.append(Parameter("ValidRelationConstraints", element))
        elif valid_relation_constraints is not None:
            result.parameters.append(Parameter("ValidRelationConstraints", valid_relation_constraints))
        result.parameters.append(Parameter("MinimumErrorLineLength", minimum_error_line_length))
        result.generate_name()
        return result

    @classmethod
    def qa_point_not_near_3(cls, point_class: BaseDataset, reference_classes: List[BaseDataset], search_distance: float, point_distance_expression: str, reference_distance_expressions: List[str], reference_right_side_distances: List[str], reference_flip_expressions: List[str], allow_coincident_points: bool = False, geometry_components: List[GeometryComponent] = 0, valid_relation_constraints: List[str] = None, minimum_error_line_length: float = -1) -> Condition:
        """
        Finds points in 'pointClass' that are closer to feature geometries (or geometry components) in 'referenceClasses' than the sum of distances derived from attribute expressions for the point feature and a reference feature. The reference feature distances can be defined for both sides of line features or polygon boundaries, with the option to swap left \/ right sides (as defined by the line direction) based on an attribute expression or constant.
        """
        
        result = Condition("QaPointNotNear(3)")
        result.parameters.append(Parameter("pointClass", point_class))
        if type(reference_classes) == list:
            for element in reference_classes:
                result.parameters.append(Parameter("referenceClasses", element))
        elif reference_classes is not None:
            result.parameters.append(Parameter("referenceClasses", reference_classes))
        result.parameters.append(Parameter("searchDistance", search_distance))
        result.parameters.append(Parameter("pointDistanceExpression", point_distance_expression))
        if type(reference_distance_expressions) == list:
            for element in reference_distance_expressions:
                result.parameters.append(Parameter("referenceDistanceExpressions", element))
        elif reference_distance_expressions is not None:
            result.parameters.append(Parameter("referenceDistanceExpressions", reference_distance_expressions))
        if type(reference_right_side_distances) == list:
            for element in reference_right_side_distances:
                result.parameters.append(Parameter("referenceRightSideDistances", element))
        elif reference_right_side_distances is not None:
            result.parameters.append(Parameter("referenceRightSideDistances", reference_right_side_distances))
        if type(reference_flip_expressions) == list:
            for element in reference_flip_expressions:
                result.parameters.append(Parameter("referenceFlipExpressions", element))
        elif reference_flip_expressions is not None:
            result.parameters.append(Parameter("referenceFlipExpressions", reference_flip_expressions))
        result.parameters.append(Parameter("AllowCoincidentPoints", allow_coincident_points))
        if type(geometry_components) == list:
            for element in geometry_components:
                result.parameters.append(Parameter("GeometryComponents", element))
        elif geometry_components is not None:
            result.parameters.append(Parameter("GeometryComponents", geometry_components))
        if type(valid_relation_constraints) == list:
            for element in valid_relation_constraints:
                result.parameters.append(Parameter("ValidRelationConstraints", element))
        elif valid_relation_constraints is not None:
            result.parameters.append(Parameter("ValidRelationConstraints", valid_relation_constraints))
        result.parameters.append(Parameter("MinimumErrorLineLength", minimum_error_line_length))
        result.generate_name()
        return result

    @classmethod
    def qa_point_on_line_0(cls, point_class: BaseDataset, near_classes: List[BaseDataset], near: float) -> Condition:
        """
        Finds all points in 'pointClass' not nearer than 'near' to any feature of 'nearClasses'
        
        Remark: All feature classes in 'pointClass' and 'nearClasses' must have the same spatial reference.
        """
        
        result = Condition("QaPointOnLine(0)")
        result.parameters.append(Parameter("pointClass", point_class))
        if type(near_classes) == list:
            for element in near_classes:
                result.parameters.append(Parameter("nearClasses", element))
        elif near_classes is not None:
            result.parameters.append(Parameter("nearClasses", near_classes))
        result.parameters.append(Parameter("near", near))
        result.generate_name()
        return result

    @classmethod
    def qa_pseudo_nodes_1(cls, polyline_class: BaseDataset, ignore_fields: List[str], valid_pseudo_node: BaseDataset, ignore_loop_endpoints: bool = False) -> Condition:
        """
        Finds pseudo nodes: Finds all endpoints in 'polylineClass', that correspond to exactly 2 From-\/To-points of 'polylineClass', the attributes values of the involved features do not differ and they are not separated by a point out of 'validPseudoNode'
        
        Remark: The feature classes in 'validPseudoNode' and 'polylineClass' must have the same spatial reference.
        """
        
        result = Condition("QaPseudoNodes(1)")
        result.parameters.append(Parameter("polylineClass", polyline_class))
        if type(ignore_fields) == list:
            for element in ignore_fields:
                result.parameters.append(Parameter("ignoreFields", element))
        elif ignore_fields is not None:
            result.parameters.append(Parameter("ignoreFields", ignore_fields))
        result.parameters.append(Parameter("validPseudoNode", valid_pseudo_node))
        result.parameters.append(Parameter("IgnoreLoopEndpoints", ignore_loop_endpoints))
        result.generate_name()
        return result

    @classmethod
    def qa_pseudo_nodes_3(cls, polyline_class: BaseDataset, ignore_fields: List[str], ignore_loop_endpoints: bool = False) -> Condition:
        """
        Finds pseudo nodes: Finds all endpoints in 'polylineClass', that correspond to exactly 2 From-\/To-points and the attributes values of the involved features do not differ
        """
        
        result = Condition("QaPseudoNodes(3)")
        result.parameters.append(Parameter("polylineClass", polyline_class))
        if type(ignore_fields) == list:
            for element in ignore_fields:
                result.parameters.append(Parameter("ignoreFields", element))
        elif ignore_fields is not None:
            result.parameters.append(Parameter("ignoreFields", ignore_fields))
        result.parameters.append(Parameter("IgnoreLoopEndpoints", ignore_loop_endpoints))
        result.generate_name()
        return result

    @classmethod
    def qa_pseudo_nodes_4(cls, polyline_classes: List[BaseDataset], ignore_field_lists: List[str], valid_pseudo_nodes: List[BaseDataset], ignore_loop_endpoints: bool = False) -> Condition:
        """
        Finds pseudo nodes: Finds all endpoints in 'polylineClasses', that correspond to exactly 2 From-\/To-points of 'polylineClasses', the two involved features belong to the same feature class, the attributes values of the involved features do not differ and they are not separated by a point out of 'validPseudoNodes' 
        
        Remark: All feature classes in 'polylineClasses' and 'validPseudoNodes' must have the same spatial reference.
        """
        
        result = Condition("QaPseudoNodes(4)")
        if type(polyline_classes) == list:
            for element in polyline_classes:
                result.parameters.append(Parameter("polylineClasses", element))
        elif polyline_classes is not None:
            result.parameters.append(Parameter("polylineClasses", polyline_classes))
        if type(ignore_field_lists) == list:
            for element in ignore_field_lists:
                result.parameters.append(Parameter("ignoreFieldLists", element))
        elif ignore_field_lists is not None:
            result.parameters.append(Parameter("ignoreFieldLists", ignore_field_lists))
        if type(valid_pseudo_nodes) == list:
            for element in valid_pseudo_nodes:
                result.parameters.append(Parameter("validPseudoNodes", element))
        elif valid_pseudo_nodes is not None:
            result.parameters.append(Parameter("validPseudoNodes", valid_pseudo_nodes))
        result.parameters.append(Parameter("IgnoreLoopEndpoints", ignore_loop_endpoints))
        result.generate_name()
        return result

    @classmethod
    def qa_pseudo_nodes_5(cls, polyline_classes: List[BaseDataset], ignore_field_lists: List[str], ignore_loop_endpoints: bool = False) -> Condition:
        """
        Finds pseudo nodes: Finds all endpoints in 'polylineClasses', that correspond to exactly 2 From-\/To-points of 'polylineClasses', the two involved features belong to the same feature class and the attributes values of the involved features do not differ
        
        Remark: The feature classes in 'polylineClasses' must have the same spatial reference.
        """
        
        result = Condition("QaPseudoNodes(5)")
        if type(polyline_classes) == list:
            for element in polyline_classes:
                result.parameters.append(Parameter("polylineClasses", element))
        elif polyline_classes is not None:
            result.parameters.append(Parameter("polylineClasses", polyline_classes))
        if type(ignore_field_lists) == list:
            for element in ignore_field_lists:
                result.parameters.append(Parameter("ignoreFieldLists", element))
        elif ignore_field_lists is not None:
            result.parameters.append(Parameter("ignoreFieldLists", ignore_field_lists))
        result.parameters.append(Parameter("IgnoreLoopEndpoints", ignore_loop_endpoints))
        result.generate_name()
        return result

    @classmethod
    def qa_regular_expression_0(cls, table: BaseDataset, pattern: str, field_name: str, field_list_type: FieldListType = 1) -> Condition:
        """
        Finds rows with values that do not match a defined regular expression
        """
        
        result = Condition("QaRegularExpression(0)")
        result.parameters.append(Parameter("table", table))
        result.parameters.append(Parameter("pattern", pattern))
        result.parameters.append(Parameter("fieldName", field_name))
        result.parameters.append(Parameter("FieldListType", field_list_type))
        result.generate_name()
        return result

    @classmethod
    def qa_regular_expression_1(cls, table: BaseDataset, pattern: str, field_names: List[str], field_list_type: FieldListType = 1) -> Condition:
        """
        Finds rows with values that do not match a defined regular expression
        """
        
        result = Condition("QaRegularExpression(1)")
        result.parameters.append(Parameter("table", table))
        result.parameters.append(Parameter("pattern", pattern))
        if type(field_names) == list:
            for element in field_names:
                result.parameters.append(Parameter("fieldNames", element))
        elif field_names is not None:
            result.parameters.append(Parameter("fieldNames", field_names))
        result.parameters.append(Parameter("FieldListType", field_list_type))
        result.generate_name()
        return result

    @classmethod
    def qa_regular_expression_2(cls, table: BaseDataset, pattern: str, field_name: str, match_is_error: bool, field_list_type: FieldListType = 1) -> Condition:
        """
        Finds rows with values that do not match a defined regular expression. Optionally, a match can be considered an error.
        """
        
        result = Condition("QaRegularExpression(2)")
        result.parameters.append(Parameter("table", table))
        result.parameters.append(Parameter("pattern", pattern))
        result.parameters.append(Parameter("fieldName", field_name))
        result.parameters.append(Parameter("matchIsError", match_is_error))
        result.parameters.append(Parameter("FieldListType", field_list_type))
        result.generate_name()
        return result

    @classmethod
    def qa_regular_expression_3(cls, table: BaseDataset, pattern: str, field_names: List[str], match_is_error: bool, field_list_type: FieldListType = 1) -> Condition:
        """
        Finds rows with values that do not match a defined regular expression. Optionally, a match can be considered an error.
        """
        
        result = Condition("QaRegularExpression(3)")
        result.parameters.append(Parameter("table", table))
        result.parameters.append(Parameter("pattern", pattern))
        if type(field_names) == list:
            for element in field_names:
                result.parameters.append(Parameter("fieldNames", element))
        elif field_names is not None:
            result.parameters.append(Parameter("fieldNames", field_names))
        result.parameters.append(Parameter("matchIsError", match_is_error))
        result.parameters.append(Parameter("FieldListType", field_list_type))
        result.generate_name()
        return result

    @classmethod
    def qa_regular_expression_4(cls, table: BaseDataset, pattern: str, field_name: str, match_is_error: bool, pattern_description: str, field_list_type: FieldListType = 1) -> Condition:
        """
        Finds rows with values that do not match a defined regular expression. Optionally, a match can be considered an error.
        """
        
        result = Condition("QaRegularExpression(4)")
        result.parameters.append(Parameter("table", table))
        result.parameters.append(Parameter("pattern", pattern))
        result.parameters.append(Parameter("fieldName", field_name))
        result.parameters.append(Parameter("matchIsError", match_is_error))
        result.parameters.append(Parameter("patternDescription", pattern_description))
        result.parameters.append(Parameter("FieldListType", field_list_type))
        result.generate_name()
        return result

    @classmethod
    def qa_regular_expression_5(cls, table: BaseDataset, pattern: str, field_names: List[str], match_is_error: bool, pattern_description: str, field_list_type: FieldListType = 1) -> Condition:
        """
        Finds rows with values that do not match a defined regular expression. Optionally, a match can be considered an error.
        """
        
        result = Condition("QaRegularExpression(5)")
        result.parameters.append(Parameter("table", table))
        result.parameters.append(Parameter("pattern", pattern))
        if type(field_names) == list:
            for element in field_names:
                result.parameters.append(Parameter("fieldNames", element))
        elif field_names is not None:
            result.parameters.append(Parameter("fieldNames", field_names))
        result.parameters.append(Parameter("matchIsError", match_is_error))
        result.parameters.append(Parameter("patternDescription", pattern_description))
        result.parameters.append(Parameter("FieldListType", field_list_type))
        result.generate_name()
        return result

    @classmethod
    def qa_required_fields_0(cls, table: BaseDataset, required_field_names: List[str]) -> Condition:
        """
        Finds rows with null values for a given list of required fields
        """
        
        result = Condition("QaRequiredFields(0)")
        result.parameters.append(Parameter("table", table))
        if type(required_field_names) == list:
            for element in required_field_names:
                result.parameters.append(Parameter("requiredFieldNames", element))
        elif required_field_names is not None:
            result.parameters.append(Parameter("requiredFieldNames", required_field_names))
        result.generate_name()
        return result

    @classmethod
    def qa_required_fields_1(cls, table: BaseDataset, required_field_names: List[str], allow_empty_strings: bool) -> Condition:
        """
        Finds rows with null values for a given list of required fields
        """
        
        result = Condition("QaRequiredFields(1)")
        result.parameters.append(Parameter("table", table))
        if type(required_field_names) == list:
            for element in required_field_names:
                result.parameters.append(Parameter("requiredFieldNames", element))
        elif required_field_names is not None:
            result.parameters.append(Parameter("requiredFieldNames", required_field_names))
        result.parameters.append(Parameter("allowEmptyStrings", allow_empty_strings))
        result.generate_name()
        return result

    @classmethod
    def qa_required_fields_2(cls, table: BaseDataset, required_field_names: List[str], allow_empty_strings: bool, allow_missing_fields: bool) -> Condition:
        """
        Finds rows with null values for a given list of required fields
        """
        
        result = Condition("QaRequiredFields(2)")
        result.parameters.append(Parameter("table", table))
        if type(required_field_names) == list:
            for element in required_field_names:
                result.parameters.append(Parameter("requiredFieldNames", element))
        elif required_field_names is not None:
            result.parameters.append(Parameter("requiredFieldNames", required_field_names))
        result.parameters.append(Parameter("allowEmptyStrings", allow_empty_strings))
        result.parameters.append(Parameter("allowMissingFields", allow_missing_fields))
        result.generate_name()
        return result

    @classmethod
    def qa_required_fields_3(cls, table: BaseDataset, required_field_names_string: str, allow_empty_strings: bool, allow_missing_fields: bool) -> Condition:
        """
        Finds rows with null values for a given list of required fields
        """
        
        result = Condition("QaRequiredFields(3)")
        result.parameters.append(Parameter("table", table))
        result.parameters.append(Parameter("requiredFieldNamesString", required_field_names_string))
        result.parameters.append(Parameter("allowEmptyStrings", allow_empty_strings))
        result.parameters.append(Parameter("allowMissingFields", allow_missing_fields))
        result.generate_name()
        return result

    @classmethod
    def qa_required_fields_4(cls, table: BaseDataset, allow_empty_strings: bool) -> Condition:
        """
        Finds rows with null values for a given list of required fields
        """
        
        result = Condition("QaRequiredFields(4)")
        result.parameters.append(Parameter("table", table))
        result.parameters.append(Parameter("allowEmptyStrings", allow_empty_strings))
        result.generate_name()
        return result

    @classmethod
    def qa_route_measures_continuous_0(cls, polyline_class: BaseDataset, route_id_field: str) -> Condition:
        """
        Finds discontinuities in the M values at connections between line features of the same route.
            
        The connecting end points of lines within the same route must have the same M values, otherwise an error is reported. M values with a difference smaller than the M tolerance of the spatial reference are considered equal.
        """
        
        result = Condition("QaRouteMeasuresContinuous(0)")
        result.parameters.append(Parameter("polylineClass", polyline_class))
        result.parameters.append(Parameter("routeIdField", route_id_field))
        result.generate_name()
        return result

    @classmethod
    def qa_route_measures_continuous_1(cls, polyline_classes: List[BaseDataset], route_id_fields: List[str]) -> Condition:
        """
        Finds discontinuities in the M values at connections between line features of the same route.
            
        The connecting end points of lines within the same route must have the same M values, otherwise an error is reported. M values with a difference smaller than the M tolerance of the spatial reference are considered equal.
        """
        
        result = Condition("QaRouteMeasuresContinuous(1)")
        if type(polyline_classes) == list:
            for element in polyline_classes:
                result.parameters.append(Parameter("polylineClasses", element))
        elif polyline_classes is not None:
            result.parameters.append(Parameter("polylineClasses", polyline_classes))
        if type(route_id_fields) == list:
            for element in route_id_fields:
                result.parameters.append(Parameter("routeIdFields", element))
        elif route_id_fields is not None:
            result.parameters.append(Parameter("routeIdFields", route_id_fields))
        result.generate_name()
        return result

    @classmethod
    def qa_route_measures_unique_0(cls, polyline_class: BaseDataset, route_id_field: str) -> Condition:
        """
        Finds segment sequences within line features belonging to the same route that have the same measure values. Both non-unique measure ranges from different features, and non-unique measures within a single feature (due to non-monotonic measures) are reported.
        """
        
        result = Condition("QaRouteMeasuresUnique(0)")
        result.parameters.append(Parameter("polylineClass", polyline_class))
        result.parameters.append(Parameter("routeIdField", route_id_field))
        result.generate_name()
        return result

    @classmethod
    def qa_route_measures_unique_1(cls, polyline_classes: List[BaseDataset], route_id_fields: List[str]) -> Condition:
        """
        Finds segment sequences within line features belonging to the same route that have the same measure values. Both non-unique measure ranges from different features, and non-unique measures within a single feature (due to non-monotonic measures) are reported.
        """
        
        result = Condition("QaRouteMeasuresUnique(1)")
        if type(polyline_classes) == list:
            for element in polyline_classes:
                result.parameters.append(Parameter("polylineClasses", element))
        elif polyline_classes is not None:
            result.parameters.append(Parameter("polylineClasses", polyline_classes))
        if type(route_id_fields) == list:
            for element in route_id_fields:
                result.parameters.append(Parameter("routeIdFields", element))
        elif route_id_fields is not None:
            result.parameters.append(Parameter("routeIdFields", route_id_fields))
        result.generate_name()
        return result

    @classmethod
    def qa_row_count_0(cls, table: BaseDataset, minimum_row_count: int, maximum_row_count: int) -> Condition:
        """
        Determines if the number of rows in a table is within an expected range
        """
        
        result = Condition("QaRowCount(0)")
        result.parameters.append(Parameter("table", table))
        result.parameters.append(Parameter("minimumRowCount", minimum_row_count))
        result.parameters.append(Parameter("maximumRowCount", maximum_row_count))
        result.generate_name()
        return result

    @classmethod
    def qa_row_count_1(cls, table: BaseDataset, reference_tables: List[BaseDataset], minimum_value_offset: str, maximum_value_offset: str) -> Condition:
        """
        Determines if the number of rows in a table is within an expected range, defined based on offsets from the row count in one or more reference tables. This can be used to check if a copy \/ append operation from one or more source tables to a target table was successful.
        """
        
        result = Condition("QaRowCount(1)")
        result.parameters.append(Parameter("table", table))
        if type(reference_tables) == list:
            for element in reference_tables:
                result.parameters.append(Parameter("referenceTables", element))
        elif reference_tables is not None:
            result.parameters.append(Parameter("referenceTables", reference_tables))
        result.parameters.append(Parameter("minimumValueOffset", minimum_value_offset))
        result.parameters.append(Parameter("maximumValueOffset", maximum_value_offset))
        result.generate_name()
        return result

    @classmethod
    def qa_schema_field_aliases_0(cls, table: BaseDataset, maximum_length: int, expected_case: ExpectedCase, require_unique_alias_names: bool, allow_custom_system_field_alias: bool) -> Condition:
        """
        Finds fields with invalid alias names.
        """
        
        result = Condition("QaSchemaFieldAliases(0)")
        result.parameters.append(Parameter("table", table))
        result.parameters.append(Parameter("maximumLength", maximum_length))
        result.parameters.append(Parameter("expectedCase", expected_case))
        result.parameters.append(Parameter("requireUniqueAliasNames", require_unique_alias_names))
        result.parameters.append(Parameter("allowCustomSystemFieldAlias", allow_custom_system_field_alias))
        result.generate_name()
        return result

    @classmethod
    def qa_schema_field_aliases_1(cls, table: BaseDataset, maximum_length: int, expected_case: ExpectedCase, require_unique_alias_names: bool, allow_custom_system_field_alias: bool, expected_difference: ExpectedStringDifference) -> Condition:
        """
        Finds fields with invalid alias names.
        """
        
        result = Condition("QaSchemaFieldAliases(1)")
        result.parameters.append(Parameter("table", table))
        result.parameters.append(Parameter("maximumLength", maximum_length))
        result.parameters.append(Parameter("expectedCase", expected_case))
        result.parameters.append(Parameter("requireUniqueAliasNames", require_unique_alias_names))
        result.parameters.append(Parameter("allowCustomSystemFieldAlias", allow_custom_system_field_alias))
        result.parameters.append(Parameter("expectedDifference", expected_difference))
        result.generate_name()
        return result

    @classmethod
    def qa_schema_field_domain_coded_values_0(cls, table: BaseDataset, maximum_name_length: int, unique_names_constraint: UniqueStringsConstraint, minimum_value_count: int, minimum_non_equal_name_value_count: int, allow_empty_name: bool) -> Condition:
        """
        Finds coded value domains referenced from a table that have invalid coded values lists.
        """
        
        result = Condition("QaSchemaFieldDomainCodedValues(0)")
        result.parameters.append(Parameter("table", table))
        result.parameters.append(Parameter("maximumNameLength", maximum_name_length))
        result.parameters.append(Parameter("uniqueNamesConstraint", unique_names_constraint))
        result.parameters.append(Parameter("minimumValueCount", minimum_value_count))
        result.parameters.append(Parameter("minimumNonEqualNameValueCount", minimum_non_equal_name_value_count))
        result.parameters.append(Parameter("allowEmptyName", allow_empty_name))
        result.generate_name()
        return result

    @classmethod
    def qa_schema_field_domain_descriptions_0(cls, table: BaseDataset, maximum_length: int, require_unique_descriptions: bool, target_workspace_table: BaseDataset) -> Condition:
        """
        Finds domains with invalid domain descriptions.
        """
        
        result = Condition("QaSchemaFieldDomainDescriptions(0)")
        result.parameters.append(Parameter("table", table))
        result.parameters.append(Parameter("maximumLength", maximum_length))
        result.parameters.append(Parameter("requireUniqueDescriptions", require_unique_descriptions))
        result.parameters.append(Parameter("targetWorkspaceTable", target_workspace_table))
        result.generate_name()
        return result

    @classmethod
    def qa_schema_field_domain_descriptions_1(cls, table: BaseDataset, maximum_length: int, require_unique_descriptions: bool) -> Condition:
        """
        Finds domains with invalid domain descriptions.
        """
        
        result = Condition("QaSchemaFieldDomainDescriptions(1)")
        result.parameters.append(Parameter("table", table))
        result.parameters.append(Parameter("maximumLength", maximum_length))
        result.parameters.append(Parameter("requireUniqueDescriptions", require_unique_descriptions))
        result.generate_name()
        return result

    @classmethod
    def qa_schema_field_domain_name_regex_0(cls, table: BaseDataset, pattern: str, match_is_error: bool, pattern_description: str) -> Condition:
        """
        Finds domains referenced from a table whose names do not match a defined regular expression.
        """
        
        result = Condition("QaSchemaFieldDomainNameRegex(0)")
        result.parameters.append(Parameter("table", table))
        result.parameters.append(Parameter("pattern", pattern))
        result.parameters.append(Parameter("matchIsError", match_is_error))
        result.parameters.append(Parameter("patternDescription", pattern_description))
        result.generate_name()
        return result

    @classmethod
    def qa_schema_field_domain_names_0(cls, table: BaseDataset, expected_prefix: str, maximum_length: int, must_contain_field_name: bool, expected_case: ExpectedCase) -> Condition:
        """
        Finds domains referenced from a table that have invalid names.
        """
        
        result = Condition("QaSchemaFieldDomainNames(0)")
        result.parameters.append(Parameter("table", table))
        result.parameters.append(Parameter("expectedPrefix", expected_prefix))
        result.parameters.append(Parameter("maximumLength", maximum_length))
        result.parameters.append(Parameter("mustContainFieldName", must_contain_field_name))
        result.parameters.append(Parameter("expectedCase", expected_case))
        result.generate_name()
        return result

    @classmethod
    def qa_schema_field_domains_0(cls, table: BaseDataset) -> Condition:
        """
        Finds domains referenced from a table that are not valid for the referencing field (due to a data type mismatch).
        """
        
        result = Condition("QaSchemaFieldDomains(0)")
        result.parameters.append(Parameter("table", table))
        result.generate_name()
        return result

    @classmethod
    def qa_schema_field_name_regex_0(cls, table: BaseDataset, pattern: str, match_is_error: bool, pattern_description: str) -> Condition:
        """
        Finds field names that do not match a defined regular expression.
        """
        
        result = Condition("QaSchemaFieldNameRegex(0)")
        result.parameters.append(Parameter("table", table))
        result.parameters.append(Parameter("pattern", pattern))
        result.parameters.append(Parameter("matchIsError", match_is_error))
        result.parameters.append(Parameter("patternDescription", pattern_description))
        result.generate_name()
        return result

    @classmethod
    def qa_schema_field_names_0(cls, table: BaseDataset, maximum_length: int, expected_case: ExpectedCase, unique_substring_length: int) -> Condition:
        """
        Finds fields with invalid names.
        """
        
        result = Condition("QaSchemaFieldNames(0)")
        result.parameters.append(Parameter("table", table))
        result.parameters.append(Parameter("maximumLength", maximum_length))
        result.parameters.append(Parameter("expectedCase", expected_case))
        result.parameters.append(Parameter("uniqueSubstringLength", unique_substring_length))
        result.generate_name()
        return result

    @classmethod
    def qa_schema_field_properties_0(cls, table: BaseDataset, field_name: str, expected_field_type: esriFieldType, expected_field_length: int, expected_alias_name: str, expected_domain_name: str, field_is_optional: bool) -> Condition:
        """
        Verifies if a field has expected properties
        """
        
        result = Condition("QaSchemaFieldProperties(0)")
        result.parameters.append(Parameter("table", table))
        result.parameters.append(Parameter("fieldName", field_name))
        result.parameters.append(Parameter("expectedFieldType", expected_field_type))
        result.parameters.append(Parameter("expectedFieldLength", expected_field_length))
        result.parameters.append(Parameter("expectedAliasName", expected_alias_name))
        result.parameters.append(Parameter("expectedDomainName", expected_domain_name))
        result.parameters.append(Parameter("fieldIsOptional", field_is_optional))
        result.generate_name()
        return result

    @classmethod
    def qa_schema_field_properties_from_table_0(cls, table: BaseDataset, field_specifications_table: BaseDataset, match_alias_name: bool) -> Condition:
        """
        Verifies that fields have expected properties based on a list of field specifications defined in another table. The field specifications table can be filtered to a subset of rows relevant for the verified table.
        """
        
        result = Condition("QaSchemaFieldPropertiesFromTable(0)")
        result.parameters.append(Parameter("table", table))
        result.parameters.append(Parameter("fieldSpecificationsTable", field_specifications_table))
        result.parameters.append(Parameter("matchAliasName", match_alias_name))
        result.generate_name()
        return result

    @classmethod
    def qa_schema_reserved_field_name_properties_0(cls, table: BaseDataset, reserved_names_table: BaseDataset, reserved_name_field_name: str, reserved_reason_field_name: str, valid_name_field_name: str, field_specifications_table: BaseDataset) -> Condition:
        """
        Finds fields that have a reserved field name, based on a table containing reserved names, and optionally a reason why a name is reserved and a valid name that should be used instead.
        """
        
        result = Condition("QaSchemaReservedFieldNameProperties(0)")
        result.parameters.append(Parameter("table", table))
        result.parameters.append(Parameter("reservedNamesTable", reserved_names_table))
        result.parameters.append(Parameter("reservedNameFieldName", reserved_name_field_name))
        result.parameters.append(Parameter("reservedReasonFieldName", reserved_reason_field_name))
        result.parameters.append(Parameter("validNameFieldName", valid_name_field_name))
        result.parameters.append(Parameter("fieldSpecificationsTable", field_specifications_table))
        result.generate_name()
        return result

    @classmethod
    def qa_schema_reserved_field_names_0(cls, table: BaseDataset, reserved_names: List[str]) -> Condition:
        """
        Finds fields that have a reserved field name, based on a list of reserved names.
        """
        
        result = Condition("QaSchemaReservedFieldNames(0)")
        result.parameters.append(Parameter("table", table))
        if type(reserved_names) == list:
            for element in reserved_names:
                result.parameters.append(Parameter("reservedNames", element))
        elif reserved_names is not None:
            result.parameters.append(Parameter("reservedNames", reserved_names))
        result.generate_name()
        return result

    @classmethod
    def qa_schema_reserved_field_names_1(cls, table: BaseDataset, reserved_names_string: str) -> Condition:
        """
        Finds fields that have a reserved field name, based on a concatenated string of reserved names.
        """
        
        result = Condition("QaSchemaReservedFieldNames(1)")
        result.parameters.append(Parameter("table", table))
        result.parameters.append(Parameter("reservedNamesString", reserved_names_string))
        result.generate_name()
        return result

    @classmethod
    def qa_schema_reserved_field_names_2(cls, table: BaseDataset, reserved_names_table: BaseDataset, reserved_name_field_name: str, reserved_reason_field_name: str, valid_name_field_name: str) -> Condition:
        """
        Finds fields that have a reserved field name, based on a table containing reserved names, and optionally a reason why a name is reserved and a valid name that should be used instead.
        """
        
        result = Condition("QaSchemaReservedFieldNames(2)")
        result.parameters.append(Parameter("table", table))
        result.parameters.append(Parameter("reservedNamesTable", reserved_names_table))
        result.parameters.append(Parameter("reservedNameFieldName", reserved_name_field_name))
        result.parameters.append(Parameter("reservedReasonFieldName", reserved_reason_field_name))
        result.parameters.append(Parameter("validNameFieldName", valid_name_field_name))
        result.generate_name()
        return result

    @classmethod
    def qa_schema_spatial_reference_0(cls, feature_class: BaseDataset, reference_feature_class: BaseDataset, compare_x_y_precision: bool, compare_z_precision: bool, compare_m_precision: bool, compare_tolerances: bool, compare_vertical_coordinate_systems: bool, compare_x_y_domain_origin: bool = False, compare_z_domain_origin: bool = False, compare_m_domain_origin: bool = False, compare_x_y_resolution: bool = False, compare_z_resolution: bool = False, compare_m_resolution: bool = False) -> Condition:
        """
        Checks if the spatial reference of a feature class is exactly (including domain, tolerance and resolution) equal to the spatial reference of a reference feature class.
        """
        
        result = Condition("QaSchemaSpatialReference(0)")
        result.parameters.append(Parameter("featureClass", feature_class))
        result.parameters.append(Parameter("referenceFeatureClass", reference_feature_class))
        result.parameters.append(Parameter("compareXYPrecision", compare_x_y_precision))
        result.parameters.append(Parameter("compareZPrecision", compare_z_precision))
        result.parameters.append(Parameter("compareMPrecision", compare_m_precision))
        result.parameters.append(Parameter("compareTolerances", compare_tolerances))
        result.parameters.append(Parameter("compareVerticalCoordinateSystems", compare_vertical_coordinate_systems))
        result.parameters.append(Parameter("CompareXYDomainOrigin", compare_x_y_domain_origin))
        result.parameters.append(Parameter("CompareZDomainOrigin", compare_z_domain_origin))
        result.parameters.append(Parameter("CompareMDomainOrigin", compare_m_domain_origin))
        result.parameters.append(Parameter("CompareXYResolution", compare_x_y_resolution))
        result.parameters.append(Parameter("CompareZResolution", compare_z_resolution))
        result.parameters.append(Parameter("CompareMResolution", compare_m_resolution))
        result.generate_name()
        return result

    @classmethod
    def qa_schema_spatial_reference_1(cls, feature_class: BaseDataset, spatial_reference_xml: str, compare_x_y_precision: bool, compare_z_precision: bool, compare_m_precision: bool, compare_tolerances: bool, compare_vertical_coordinate_systems: bool, compare_x_y_domain_origin: bool = False, compare_z_domain_origin: bool = False, compare_m_domain_origin: bool = False, compare_x_y_resolution: bool = False, compare_z_resolution: bool = False, compare_m_resolution: bool = False) -> Condition:
        """
        Checks if the spatial reference of a feature class is exactly (including domain, tolerance and resolution) equal to the spatial reference defined in an spatial reference xml string.
        """
        
        result = Condition("QaSchemaSpatialReference(1)")
        result.parameters.append(Parameter("featureClass", feature_class))
        result.parameters.append(Parameter("spatialReferenceXml", spatial_reference_xml))
        result.parameters.append(Parameter("compareXYPrecision", compare_x_y_precision))
        result.parameters.append(Parameter("compareZPrecision", compare_z_precision))
        result.parameters.append(Parameter("compareMPrecision", compare_m_precision))
        result.parameters.append(Parameter("compareTolerances", compare_tolerances))
        result.parameters.append(Parameter("compareVerticalCoordinateSystems", compare_vertical_coordinate_systems))
        result.parameters.append(Parameter("CompareXYDomainOrigin", compare_x_y_domain_origin))
        result.parameters.append(Parameter("CompareZDomainOrigin", compare_z_domain_origin))
        result.parameters.append(Parameter("CompareMDomainOrigin", compare_m_domain_origin))
        result.parameters.append(Parameter("CompareXYResolution", compare_x_y_resolution))
        result.parameters.append(Parameter("CompareZResolution", compare_z_resolution))
        result.parameters.append(Parameter("CompareMResolution", compare_m_resolution))
        result.generate_name()
        return result

    @classmethod
    def qa_schema_spatial_reference_2(cls, feature_class: BaseDataset, reference_feature_class: BaseDataset, compare_used_precisions: bool, compare_tolerances: bool, compare_vertical_coordinate_systems: bool, compare_x_y_domain_origin: bool = False, compare_z_domain_origin: bool = False, compare_m_domain_origin: bool = False, compare_x_y_resolution: bool = False, compare_z_resolution: bool = False, compare_m_resolution: bool = False) -> Condition:
        """
        Checks if the spatial reference of 'featureClass' is exactly (including domain, tolerance and resolution) equal to the spatial reference of 'referenceFeatureClass'.
        """
        
        result = Condition("QaSchemaSpatialReference(2)")
        result.parameters.append(Parameter("featureClass", feature_class))
        result.parameters.append(Parameter("referenceFeatureClass", reference_feature_class))
        result.parameters.append(Parameter("compareUsedPrecisions", compare_used_precisions))
        result.parameters.append(Parameter("compareTolerances", compare_tolerances))
        result.parameters.append(Parameter("compareVerticalCoordinateSystems", compare_vertical_coordinate_systems))
        result.parameters.append(Parameter("CompareXYDomainOrigin", compare_x_y_domain_origin))
        result.parameters.append(Parameter("CompareZDomainOrigin", compare_z_domain_origin))
        result.parameters.append(Parameter("CompareMDomainOrigin", compare_m_domain_origin))
        result.parameters.append(Parameter("CompareXYResolution", compare_x_y_resolution))
        result.parameters.append(Parameter("CompareZResolution", compare_z_resolution))
        result.parameters.append(Parameter("CompareMResolution", compare_m_resolution))
        result.generate_name()
        return result

    @classmethod
    def qa_schema_spatial_reference_3(cls, feature_class: BaseDataset, spatial_reference_xml: str, compare_used_precisions: bool, compare_tolerances: bool, compare_vertical_coordinate_systems: bool, compare_x_y_domain_origin: bool = False, compare_z_domain_origin: bool = False, compare_m_domain_origin: bool = False, compare_x_y_resolution: bool = False, compare_z_resolution: bool = False, compare_m_resolution: bool = False) -> Condition:
        """
        Checks if the spatial reference of 'featureClass' is exactly (including domain, tolerance and resolution) equal to the spatial reference defined in 'spatialReferenceXml' string.
        """
        
        result = Condition("QaSchemaSpatialReference(3)")
        result.parameters.append(Parameter("featureClass", feature_class))
        result.parameters.append(Parameter("spatialReferenceXml", spatial_reference_xml))
        result.parameters.append(Parameter("compareUsedPrecisions", compare_used_precisions))
        result.parameters.append(Parameter("compareTolerances", compare_tolerances))
        result.parameters.append(Parameter("compareVerticalCoordinateSystems", compare_vertical_coordinate_systems))
        result.parameters.append(Parameter("CompareXYDomainOrigin", compare_x_y_domain_origin))
        result.parameters.append(Parameter("CompareZDomainOrigin", compare_z_domain_origin))
        result.parameters.append(Parameter("CompareMDomainOrigin", compare_m_domain_origin))
        result.parameters.append(Parameter("CompareXYResolution", compare_x_y_resolution))
        result.parameters.append(Parameter("CompareZResolution", compare_z_resolution))
        result.parameters.append(Parameter("CompareMResolution", compare_m_resolution))
        result.generate_name()
        return result

    @classmethod
    def qa_segment_length_0(cls, feature_class: BaseDataset, limit: float, is3_d: bool) -> Condition:
        """
        Find all segments in 'featureClass' smaller than 'limit'
        """
        
        result = Condition("QaSegmentLength(0)")
        result.parameters.append(Parameter("featureClass", feature_class))
        result.parameters.append(Parameter("limit", limit))
        result.parameters.append(Parameter("is3D", is3_d))
        result.generate_name()
        return result

    @classmethod
    def qa_segment_length_1(cls, feature_class: BaseDataset, limit: float) -> Condition:
        """
        Find all segments in 'featureClass' smaller than 'limit'
        """
        
        result = Condition("QaSegmentLength(1)")
        result.parameters.append(Parameter("featureClass", feature_class))
        result.parameters.append(Parameter("limit", limit))
        result.generate_name()
        return result

    @classmethod
    def qa_simple_geometry_0(cls, feature_class: BaseDataset) -> Condition:
        """
        Finds all features in 'featureClass' with non-simple geometries
        """
        
        result = Condition("QaSimpleGeometry(0)")
        result.parameters.append(Parameter("featureClass", feature_class))
        result.generate_name()
        return result

    @classmethod
    def qa_simple_geometry_1(cls, feature_class: BaseDataset, allow_non_planar_lines: bool) -> Condition:
        """
        Finds all features in 'featureClass' with non-simple geometries. Optionally ignores non-planar (self-intersecting) lines
        """
        
        result = Condition("QaSimpleGeometry(1)")
        result.parameters.append(Parameter("featureClass", feature_class))
        result.parameters.append(Parameter("allowNonPlanarLines", allow_non_planar_lines))
        result.generate_name()
        return result

    @classmethod
    def qa_simple_geometry_2(cls, feature_class: BaseDataset, allow_non_planar_lines: bool, tolerance_factor: float) -> Condition:
        """
        Finds all features in 'featureClass' with non-simple geometries. Optionally ignores non-planar (self-intersecting) lines, and allows specifying a custom factor for reducing the spatial reference xy tolerance used in the detection of non-simple geometries.
        """
        
        result = Condition("QaSimpleGeometry(2)")
        result.parameters.append(Parameter("featureClass", feature_class))
        result.parameters.append(Parameter("allowNonPlanarLines", allow_non_planar_lines))
        result.parameters.append(Parameter("toleranceFactor", tolerance_factor))
        result.generate_name()
        return result

    @classmethod
    def qa_sliver_polygon_0(cls, polygon_class: BaseDataset, limit: float) -> Condition:
        """
        Finds all sliver polygons in 'polygonClass'
        """
        
        result = Condition("QaSliverPolygon(0)")
        result.parameters.append(Parameter("polygonClass", polygon_class))
        result.parameters.append(Parameter("limit", limit))
        result.generate_name()
        return result

    @classmethod
    def qa_sliver_polygon_1(cls, polygon_class: BaseDataset, limit: float, max_area: float) -> Condition:
        """
        Finds all sliver polygons in 'polygonClass'
        """
        
        result = Condition("QaSliverPolygon(1)")
        result.parameters.append(Parameter("polygonClass", polygon_class))
        result.parameters.append(Parameter("limit", limit))
        result.parameters.append(Parameter("maxArea", max_area))
        result.generate_name()
        return result

    @classmethod
    def qa_smooth_0(cls, feature_class: BaseDataset, limit: float, angular_unit: AngleUnit = 0) -> Condition:
        """
        Finds all segments in 'featureClass' where the discretized second derivative of the slope angle exceeds 'limit'. This means that there are to abrupt changes in the slope angle.
        """
        
        result = Condition("QaSmooth(0)")
        result.parameters.append(Parameter("featureClass", feature_class))
        result.parameters.append(Parameter("limit", limit))
        result.parameters.append(Parameter("AngularUnit", angular_unit))
        result.generate_name()
        return result

    @classmethod
    def qa_topo_not_near_0(cls, feature_class: BaseDataset, near: float, min_length: float, is3_d: bool, crossing_min_length_factor: float = -1, not_reported_condition: str = None, ignore_neighbor_condition: str = None, junction_coincidence_tolerance: float = 0, connection_mode: ConnectionMode = 1, unconnected_line_cap_style: LineCapStyle = 0, ignore_loops_within_near_distance: bool = False, ignore_inconsistent_line_symbol_ends: bool = False, allow_coincident_sections: bool = False, right_side_nears: List[str] = None, end_cap_style: LineCapStyle = 0, junction_is_end_expression: str = None) -> Condition:
        """
        Finds all line sections longer than 'minLength' in 'featureClass' that are closer than 'near' to any other line in 'featureClass'.
        """
        
        result = Condition("QaTopoNotNear(0)")
        result.parameters.append(Parameter("featureClass", feature_class))
        result.parameters.append(Parameter("near", near))
        result.parameters.append(Parameter("minLength", min_length))
        result.parameters.append(Parameter("is3D", is3_d))
        result.parameters.append(Parameter("CrossingMinLengthFactor", crossing_min_length_factor))
        result.parameters.append(Parameter("NotReportedCondition", not_reported_condition))
        result.parameters.append(Parameter("IgnoreNeighborCondition", ignore_neighbor_condition))
        result.parameters.append(Parameter("JunctionCoincidenceTolerance", junction_coincidence_tolerance))
        result.parameters.append(Parameter("ConnectionMode", connection_mode))
        result.parameters.append(Parameter("UnconnectedLineCapStyle", unconnected_line_cap_style))
        result.parameters.append(Parameter("IgnoreLoopsWithinNearDistance", ignore_loops_within_near_distance))
        result.parameters.append(Parameter("IgnoreInconsistentLineSymbolEnds", ignore_inconsistent_line_symbol_ends))
        result.parameters.append(Parameter("AllowCoincidentSections", allow_coincident_sections))
        if type(right_side_nears) == list:
            for element in right_side_nears:
                result.parameters.append(Parameter("RightSideNears", element))
        elif right_side_nears is not None:
            result.parameters.append(Parameter("RightSideNears", right_side_nears))
        result.parameters.append(Parameter("EndCapStyle", end_cap_style))
        result.parameters.append(Parameter("JunctionIsEndExpression", junction_is_end_expression))
        result.generate_name()
        return result

    @classmethod
    def qa_topo_not_near_1(cls, feature_class: BaseDataset, near: float, min_length: float, is3_d: bool, tile_size: float, crossing_min_length_factor: float = -1, not_reported_condition: str = None, ignore_neighbor_condition: str = None, junction_coincidence_tolerance: float = 0, connection_mode: ConnectionMode = 1, unconnected_line_cap_style: LineCapStyle = 0, ignore_loops_within_near_distance: bool = False, ignore_inconsistent_line_symbol_ends: bool = False, allow_coincident_sections: bool = False, right_side_nears: List[str] = None, end_cap_style: LineCapStyle = 0, junction_is_end_expression: str = None) -> Condition:
        """
        Finds all line sections longer than 'minLength' in 'featureClass' that are closer than 'near' to any other line in 'featureClass'.
        """
        
        result = Condition("QaTopoNotNear(1)")
        result.parameters.append(Parameter("featureClass", feature_class))
        result.parameters.append(Parameter("near", near))
        result.parameters.append(Parameter("minLength", min_length))
        result.parameters.append(Parameter("is3D", is3_d))
        result.parameters.append(Parameter("tileSize", tile_size))
        result.parameters.append(Parameter("CrossingMinLengthFactor", crossing_min_length_factor))
        result.parameters.append(Parameter("NotReportedCondition", not_reported_condition))
        result.parameters.append(Parameter("IgnoreNeighborCondition", ignore_neighbor_condition))
        result.parameters.append(Parameter("JunctionCoincidenceTolerance", junction_coincidence_tolerance))
        result.parameters.append(Parameter("ConnectionMode", connection_mode))
        result.parameters.append(Parameter("UnconnectedLineCapStyle", unconnected_line_cap_style))
        result.parameters.append(Parameter("IgnoreLoopsWithinNearDistance", ignore_loops_within_near_distance))
        result.parameters.append(Parameter("IgnoreInconsistentLineSymbolEnds", ignore_inconsistent_line_symbol_ends))
        result.parameters.append(Parameter("AllowCoincidentSections", allow_coincident_sections))
        if type(right_side_nears) == list:
            for element in right_side_nears:
                result.parameters.append(Parameter("RightSideNears", element))
        elif right_side_nears is not None:
            result.parameters.append(Parameter("RightSideNears", right_side_nears))
        result.parameters.append(Parameter("EndCapStyle", end_cap_style))
        result.parameters.append(Parameter("JunctionIsEndExpression", junction_is_end_expression))
        result.generate_name()
        return result

    @classmethod
    def qa_topo_not_near_2(cls, feature_class: BaseDataset, reference: BaseDataset, near: float, min_length: float, is3_d: bool, crossing_min_length_factor: float = -1, not_reported_condition: str = None, ignore_neighbor_condition: str = None, junction_coincidence_tolerance: float = 0, connection_mode: ConnectionMode = 1, unconnected_line_cap_style: LineCapStyle = 0, ignore_loops_within_near_distance: bool = False, ignore_inconsistent_line_symbol_ends: bool = False, allow_coincident_sections: bool = False, right_side_nears: List[str] = None, end_cap_style: LineCapStyle = 0, junction_is_end_expression: str = None) -> Condition:
        """
        Finds all line sections in 'featureClass' longer than 'minLength' that are closer than 'near' to any line in 'reference'.
        
        Remark: The feature classes in 'featureClass' and 'reference' must have the same spatial reference.
        """
        
        result = Condition("QaTopoNotNear(2)")
        result.parameters.append(Parameter("featureClass", feature_class))
        result.parameters.append(Parameter("reference", reference))
        result.parameters.append(Parameter("near", near))
        result.parameters.append(Parameter("minLength", min_length))
        result.parameters.append(Parameter("is3D", is3_d))
        result.parameters.append(Parameter("CrossingMinLengthFactor", crossing_min_length_factor))
        result.parameters.append(Parameter("NotReportedCondition", not_reported_condition))
        result.parameters.append(Parameter("IgnoreNeighborCondition", ignore_neighbor_condition))
        result.parameters.append(Parameter("JunctionCoincidenceTolerance", junction_coincidence_tolerance))
        result.parameters.append(Parameter("ConnectionMode", connection_mode))
        result.parameters.append(Parameter("UnconnectedLineCapStyle", unconnected_line_cap_style))
        result.parameters.append(Parameter("IgnoreLoopsWithinNearDistance", ignore_loops_within_near_distance))
        result.parameters.append(Parameter("IgnoreInconsistentLineSymbolEnds", ignore_inconsistent_line_symbol_ends))
        result.parameters.append(Parameter("AllowCoincidentSections", allow_coincident_sections))
        if type(right_side_nears) == list:
            for element in right_side_nears:
                result.parameters.append(Parameter("RightSideNears", element))
        elif right_side_nears is not None:
            result.parameters.append(Parameter("RightSideNears", right_side_nears))
        result.parameters.append(Parameter("EndCapStyle", end_cap_style))
        result.parameters.append(Parameter("JunctionIsEndExpression", junction_is_end_expression))
        result.generate_name()
        return result

    @classmethod
    def qa_topo_not_near_3(cls, feature_class: BaseDataset, reference: BaseDataset, near: float, min_length: float, is3_d: bool, tile_size: float, crossing_min_length_factor: float = -1, not_reported_condition: str = None, ignore_neighbor_condition: str = None, junction_coincidence_tolerance: float = 0, connection_mode: ConnectionMode = 1, unconnected_line_cap_style: LineCapStyle = 0, ignore_loops_within_near_distance: bool = False, ignore_inconsistent_line_symbol_ends: bool = False, allow_coincident_sections: bool = False, right_side_nears: List[str] = None, end_cap_style: LineCapStyle = 0, junction_is_end_expression: str = None) -> Condition:
        """
        Finds all line sections in 'featureClass' longer than 'minLength' that are closer than 'near' to any line in 'reference'.
        
        Remark: The feature classes in 'featureClass' and 'reference' must have the same spatial reference.
        """
        
        result = Condition("QaTopoNotNear(3)")
        result.parameters.append(Parameter("featureClass", feature_class))
        result.parameters.append(Parameter("reference", reference))
        result.parameters.append(Parameter("near", near))
        result.parameters.append(Parameter("minLength", min_length))
        result.parameters.append(Parameter("is3D", is3_d))
        result.parameters.append(Parameter("tileSize", tile_size))
        result.parameters.append(Parameter("CrossingMinLengthFactor", crossing_min_length_factor))
        result.parameters.append(Parameter("NotReportedCondition", not_reported_condition))
        result.parameters.append(Parameter("IgnoreNeighborCondition", ignore_neighbor_condition))
        result.parameters.append(Parameter("JunctionCoincidenceTolerance", junction_coincidence_tolerance))
        result.parameters.append(Parameter("ConnectionMode", connection_mode))
        result.parameters.append(Parameter("UnconnectedLineCapStyle", unconnected_line_cap_style))
        result.parameters.append(Parameter("IgnoreLoopsWithinNearDistance", ignore_loops_within_near_distance))
        result.parameters.append(Parameter("IgnoreInconsistentLineSymbolEnds", ignore_inconsistent_line_symbol_ends))
        result.parameters.append(Parameter("AllowCoincidentSections", allow_coincident_sections))
        if type(right_side_nears) == list:
            for element in right_side_nears:
                result.parameters.append(Parameter("RightSideNears", element))
        elif right_side_nears is not None:
            result.parameters.append(Parameter("RightSideNears", right_side_nears))
        result.parameters.append(Parameter("EndCapStyle", end_cap_style))
        result.parameters.append(Parameter("JunctionIsEndExpression", junction_is_end_expression))
        result.generate_name()
        return result

    @classmethod
    def qa_topo_not_near_4(cls, feature_class: BaseDataset, near: float, min_length: float, crossing_min_length_factor: float = -1, not_reported_condition: str = None, ignore_neighbor_condition: str = None, junction_coincidence_tolerance: float = 0, connection_mode: ConnectionMode = 1, unconnected_line_cap_style: LineCapStyle = 0, ignore_loops_within_near_distance: bool = False, ignore_inconsistent_line_symbol_ends: bool = False, allow_coincident_sections: bool = False, right_side_nears: List[str] = None, end_cap_style: LineCapStyle = 0, junction_is_end_expression: str = None) -> Condition:
        """
        Finds all line sections longer than 'minLength' in 'featureClass' that are closer than 'near' to any other line in 'featureClass'.
        """
        
        result = Condition("QaTopoNotNear(4)")
        result.parameters.append(Parameter("featureClass", feature_class))
        result.parameters.append(Parameter("near", near))
        result.parameters.append(Parameter("minLength", min_length))
        result.parameters.append(Parameter("CrossingMinLengthFactor", crossing_min_length_factor))
        result.parameters.append(Parameter("NotReportedCondition", not_reported_condition))
        result.parameters.append(Parameter("IgnoreNeighborCondition", ignore_neighbor_condition))
        result.parameters.append(Parameter("JunctionCoincidenceTolerance", junction_coincidence_tolerance))
        result.parameters.append(Parameter("ConnectionMode", connection_mode))
        result.parameters.append(Parameter("UnconnectedLineCapStyle", unconnected_line_cap_style))
        result.parameters.append(Parameter("IgnoreLoopsWithinNearDistance", ignore_loops_within_near_distance))
        result.parameters.append(Parameter("IgnoreInconsistentLineSymbolEnds", ignore_inconsistent_line_symbol_ends))
        result.parameters.append(Parameter("AllowCoincidentSections", allow_coincident_sections))
        if type(right_side_nears) == list:
            for element in right_side_nears:
                result.parameters.append(Parameter("RightSideNears", element))
        elif right_side_nears is not None:
            result.parameters.append(Parameter("RightSideNears", right_side_nears))
        result.parameters.append(Parameter("EndCapStyle", end_cap_style))
        result.parameters.append(Parameter("JunctionIsEndExpression", junction_is_end_expression))
        result.generate_name()
        return result

    @classmethod
    def qa_topo_not_near_5(cls, feature_class: BaseDataset, near: float, min_length: float, tile_size: float, crossing_min_length_factor: float = -1, not_reported_condition: str = None, ignore_neighbor_condition: str = None, junction_coincidence_tolerance: float = 0, connection_mode: ConnectionMode = 1, unconnected_line_cap_style: LineCapStyle = 0, ignore_loops_within_near_distance: bool = False, ignore_inconsistent_line_symbol_ends: bool = False, allow_coincident_sections: bool = False, right_side_nears: List[str] = None, end_cap_style: LineCapStyle = 0, junction_is_end_expression: str = None) -> Condition:
        """
        Finds all line sections longer than 'minLength' in 'featureClass' that are closer than 'near' to any other line in 'featureClass'.
        """
        
        result = Condition("QaTopoNotNear(5)")
        result.parameters.append(Parameter("featureClass", feature_class))
        result.parameters.append(Parameter("near", near))
        result.parameters.append(Parameter("minLength", min_length))
        result.parameters.append(Parameter("tileSize", tile_size))
        result.parameters.append(Parameter("CrossingMinLengthFactor", crossing_min_length_factor))
        result.parameters.append(Parameter("NotReportedCondition", not_reported_condition))
        result.parameters.append(Parameter("IgnoreNeighborCondition", ignore_neighbor_condition))
        result.parameters.append(Parameter("JunctionCoincidenceTolerance", junction_coincidence_tolerance))
        result.parameters.append(Parameter("ConnectionMode", connection_mode))
        result.parameters.append(Parameter("UnconnectedLineCapStyle", unconnected_line_cap_style))
        result.parameters.append(Parameter("IgnoreLoopsWithinNearDistance", ignore_loops_within_near_distance))
        result.parameters.append(Parameter("IgnoreInconsistentLineSymbolEnds", ignore_inconsistent_line_symbol_ends))
        result.parameters.append(Parameter("AllowCoincidentSections", allow_coincident_sections))
        if type(right_side_nears) == list:
            for element in right_side_nears:
                result.parameters.append(Parameter("RightSideNears", element))
        elif right_side_nears is not None:
            result.parameters.append(Parameter("RightSideNears", right_side_nears))
        result.parameters.append(Parameter("EndCapStyle", end_cap_style))
        result.parameters.append(Parameter("JunctionIsEndExpression", junction_is_end_expression))
        result.generate_name()
        return result

    @classmethod
    def qa_topo_not_near_6(cls, feature_class: BaseDataset, reference: BaseDataset, near: float, min_length: float, crossing_min_length_factor: float = -1, not_reported_condition: str = None, ignore_neighbor_condition: str = None, junction_coincidence_tolerance: float = 0, connection_mode: ConnectionMode = 1, unconnected_line_cap_style: LineCapStyle = 0, ignore_loops_within_near_distance: bool = False, ignore_inconsistent_line_symbol_ends: bool = False, allow_coincident_sections: bool = False, right_side_nears: List[str] = None, end_cap_style: LineCapStyle = 0, junction_is_end_expression: str = None) -> Condition:
        """
        Finds all line sections in 'featureClass' longer than 'minLength' that are closer than 'near' to any line in 'reference'.
        
        Remark: The feature classes in 'featureClass' and 'reference' must have the same spatial reference.
        """
        
        result = Condition("QaTopoNotNear(6)")
        result.parameters.append(Parameter("featureClass", feature_class))
        result.parameters.append(Parameter("reference", reference))
        result.parameters.append(Parameter("near", near))
        result.parameters.append(Parameter("minLength", min_length))
        result.parameters.append(Parameter("CrossingMinLengthFactor", crossing_min_length_factor))
        result.parameters.append(Parameter("NotReportedCondition", not_reported_condition))
        result.parameters.append(Parameter("IgnoreNeighborCondition", ignore_neighbor_condition))
        result.parameters.append(Parameter("JunctionCoincidenceTolerance", junction_coincidence_tolerance))
        result.parameters.append(Parameter("ConnectionMode", connection_mode))
        result.parameters.append(Parameter("UnconnectedLineCapStyle", unconnected_line_cap_style))
        result.parameters.append(Parameter("IgnoreLoopsWithinNearDistance", ignore_loops_within_near_distance))
        result.parameters.append(Parameter("IgnoreInconsistentLineSymbolEnds", ignore_inconsistent_line_symbol_ends))
        result.parameters.append(Parameter("AllowCoincidentSections", allow_coincident_sections))
        if type(right_side_nears) == list:
            for element in right_side_nears:
                result.parameters.append(Parameter("RightSideNears", element))
        elif right_side_nears is not None:
            result.parameters.append(Parameter("RightSideNears", right_side_nears))
        result.parameters.append(Parameter("EndCapStyle", end_cap_style))
        result.parameters.append(Parameter("JunctionIsEndExpression", junction_is_end_expression))
        result.generate_name()
        return result

    @classmethod
    def qa_topo_not_near_7(cls, feature_class: BaseDataset, reference: BaseDataset, near: float, min_length: float, tile_size: float, crossing_min_length_factor: float = -1, not_reported_condition: str = None, ignore_neighbor_condition: str = None, junction_coincidence_tolerance: float = 0, connection_mode: ConnectionMode = 1, unconnected_line_cap_style: LineCapStyle = 0, ignore_loops_within_near_distance: bool = False, ignore_inconsistent_line_symbol_ends: bool = False, allow_coincident_sections: bool = False, right_side_nears: List[str] = None, end_cap_style: LineCapStyle = 0, junction_is_end_expression: str = None) -> Condition:
        """
        Finds all line sections in 'featureClass' longer than 'minLength' that are closer than 'near' to any line in 'reference'.
        
        Remark: The feature classes in 'featureClass' and 'reference' must have the same spatial reference.
        """
        
        result = Condition("QaTopoNotNear(7)")
        result.parameters.append(Parameter("featureClass", feature_class))
        result.parameters.append(Parameter("reference", reference))
        result.parameters.append(Parameter("near", near))
        result.parameters.append(Parameter("minLength", min_length))
        result.parameters.append(Parameter("tileSize", tile_size))
        result.parameters.append(Parameter("CrossingMinLengthFactor", crossing_min_length_factor))
        result.parameters.append(Parameter("NotReportedCondition", not_reported_condition))
        result.parameters.append(Parameter("IgnoreNeighborCondition", ignore_neighbor_condition))
        result.parameters.append(Parameter("JunctionCoincidenceTolerance", junction_coincidence_tolerance))
        result.parameters.append(Parameter("ConnectionMode", connection_mode))
        result.parameters.append(Parameter("UnconnectedLineCapStyle", unconnected_line_cap_style))
        result.parameters.append(Parameter("IgnoreLoopsWithinNearDistance", ignore_loops_within_near_distance))
        result.parameters.append(Parameter("IgnoreInconsistentLineSymbolEnds", ignore_inconsistent_line_symbol_ends))
        result.parameters.append(Parameter("AllowCoincidentSections", allow_coincident_sections))
        if type(right_side_nears) == list:
            for element in right_side_nears:
                result.parameters.append(Parameter("RightSideNears", element))
        elif right_side_nears is not None:
            result.parameters.append(Parameter("RightSideNears", right_side_nears))
        result.parameters.append(Parameter("EndCapStyle", end_cap_style))
        result.parameters.append(Parameter("JunctionIsEndExpression", junction_is_end_expression))
        result.generate_name()
        return result

    @classmethod
    def qa_topo_not_near_8(cls, feature_class: BaseDataset, near: float, near_expression: str, connected_min_length_factor: float, default_unconnected_min_length_factor: float, is3_d: bool, crossing_min_length_factor: float = -1, not_reported_condition: str = None, ignore_neighbor_condition: str = None, junction_coincidence_tolerance: float = 0, connection_mode: ConnectionMode = 1, unconnected_line_cap_style: LineCapStyle = 0, ignore_loops_within_near_distance: bool = False, ignore_inconsistent_line_symbol_ends: bool = False, allow_coincident_sections: bool = False, right_side_nears: List[str] = None, end_cap_style: LineCapStyle = 0, junction_is_end_expression: str = None) -> Condition:
        """
        
        """
        
        result = Condition("QaTopoNotNear(8)")
        result.parameters.append(Parameter("featureClass", feature_class))
        result.parameters.append(Parameter("near", near))
        result.parameters.append(Parameter("nearExpression", near_expression))
        result.parameters.append(Parameter("connectedMinLengthFactor", connected_min_length_factor))
        result.parameters.append(Parameter("defaultUnconnectedMinLengthFactor", default_unconnected_min_length_factor))
        result.parameters.append(Parameter("is3D", is3_d))
        result.parameters.append(Parameter("CrossingMinLengthFactor", crossing_min_length_factor))
        result.parameters.append(Parameter("NotReportedCondition", not_reported_condition))
        result.parameters.append(Parameter("IgnoreNeighborCondition", ignore_neighbor_condition))
        result.parameters.append(Parameter("JunctionCoincidenceTolerance", junction_coincidence_tolerance))
        result.parameters.append(Parameter("ConnectionMode", connection_mode))
        result.parameters.append(Parameter("UnconnectedLineCapStyle", unconnected_line_cap_style))
        result.parameters.append(Parameter("IgnoreLoopsWithinNearDistance", ignore_loops_within_near_distance))
        result.parameters.append(Parameter("IgnoreInconsistentLineSymbolEnds", ignore_inconsistent_line_symbol_ends))
        result.parameters.append(Parameter("AllowCoincidentSections", allow_coincident_sections))
        if type(right_side_nears) == list:
            for element in right_side_nears:
                result.parameters.append(Parameter("RightSideNears", element))
        elif right_side_nears is not None:
            result.parameters.append(Parameter("RightSideNears", right_side_nears))
        result.parameters.append(Parameter("EndCapStyle", end_cap_style))
        result.parameters.append(Parameter("JunctionIsEndExpression", junction_is_end_expression))
        result.generate_name()
        return result

    @classmethod
    def qa_topo_not_near_9(cls, feature_class: BaseDataset, reference: BaseDataset, near: float, connected_min_length_factor: float, default_unconnected_min_length_factor: float, is3_d: bool, crossing_min_length_factor: float = -1, not_reported_condition: str = None, ignore_neighbor_condition: str = None, junction_coincidence_tolerance: float = 0, connection_mode: ConnectionMode = 1, unconnected_line_cap_style: LineCapStyle = 0, ignore_loops_within_near_distance: bool = False, ignore_inconsistent_line_symbol_ends: bool = False, allow_coincident_sections: bool = False, right_side_nears: List[str] = None, end_cap_style: LineCapStyle = 0, junction_is_end_expression: str = None) -> Condition:
        """
        Finds all line sections in 'featureClass' longer than 'minLength' that are closer than 'near' to any line in 'reference'.
        
        Remark: The feature classes in 'featureClass' and 'reference' must have the same spatial reference.
        """
        
        result = Condition("QaTopoNotNear(9)")
        result.parameters.append(Parameter("featureClass", feature_class))
        result.parameters.append(Parameter("reference", reference))
        result.parameters.append(Parameter("near", near))
        result.parameters.append(Parameter("connectedMinLengthFactor", connected_min_length_factor))
        result.parameters.append(Parameter("defaultUnconnectedMinLengthFactor", default_unconnected_min_length_factor))
        result.parameters.append(Parameter("is3D", is3_d))
        result.parameters.append(Parameter("CrossingMinLengthFactor", crossing_min_length_factor))
        result.parameters.append(Parameter("NotReportedCondition", not_reported_condition))
        result.parameters.append(Parameter("IgnoreNeighborCondition", ignore_neighbor_condition))
        result.parameters.append(Parameter("JunctionCoincidenceTolerance", junction_coincidence_tolerance))
        result.parameters.append(Parameter("ConnectionMode", connection_mode))
        result.parameters.append(Parameter("UnconnectedLineCapStyle", unconnected_line_cap_style))
        result.parameters.append(Parameter("IgnoreLoopsWithinNearDistance", ignore_loops_within_near_distance))
        result.parameters.append(Parameter("IgnoreInconsistentLineSymbolEnds", ignore_inconsistent_line_symbol_ends))
        result.parameters.append(Parameter("AllowCoincidentSections", allow_coincident_sections))
        if type(right_side_nears) == list:
            for element in right_side_nears:
                result.parameters.append(Parameter("RightSideNears", element))
        elif right_side_nears is not None:
            result.parameters.append(Parameter("RightSideNears", right_side_nears))
        result.parameters.append(Parameter("EndCapStyle", end_cap_style))
        result.parameters.append(Parameter("JunctionIsEndExpression", junction_is_end_expression))
        result.generate_name()
        return result

    @classmethod
    def qa_topo_not_near_10(cls, feature_class: BaseDataset, reference: BaseDataset, near: float, feature_class_near: str, reference_near: str, connected_min_length_factor: float, default_unconnected_min_length_factor: float, is3_d: bool, crossing_min_length_factor: float = -1, not_reported_condition: str = None, ignore_neighbor_condition: str = None, junction_coincidence_tolerance: float = 0, connection_mode: ConnectionMode = 1, unconnected_line_cap_style: LineCapStyle = 0, ignore_loops_within_near_distance: bool = False, ignore_inconsistent_line_symbol_ends: bool = False, allow_coincident_sections: bool = False, right_side_nears: List[str] = None, end_cap_style: LineCapStyle = 0, junction_is_end_expression: str = None) -> Condition:
        """
        Finds all line sections in 'featureClass' longer than 'minLength' that are closer than 'near' to any line in 'reference'.
        
        Remark: The feature classes in 'featureClass' and 'reference' must have the same spatial reference.
        """
        
        result = Condition("QaTopoNotNear(10)")
        result.parameters.append(Parameter("featureClass", feature_class))
        result.parameters.append(Parameter("reference", reference))
        result.parameters.append(Parameter("near", near))
        result.parameters.append(Parameter("featureClassNear", feature_class_near))
        result.parameters.append(Parameter("referenceNear", reference_near))
        result.parameters.append(Parameter("connectedMinLengthFactor", connected_min_length_factor))
        result.parameters.append(Parameter("defaultUnconnectedMinLengthFactor", default_unconnected_min_length_factor))
        result.parameters.append(Parameter("is3D", is3_d))
        result.parameters.append(Parameter("CrossingMinLengthFactor", crossing_min_length_factor))
        result.parameters.append(Parameter("NotReportedCondition", not_reported_condition))
        result.parameters.append(Parameter("IgnoreNeighborCondition", ignore_neighbor_condition))
        result.parameters.append(Parameter("JunctionCoincidenceTolerance", junction_coincidence_tolerance))
        result.parameters.append(Parameter("ConnectionMode", connection_mode))
        result.parameters.append(Parameter("UnconnectedLineCapStyle", unconnected_line_cap_style))
        result.parameters.append(Parameter("IgnoreLoopsWithinNearDistance", ignore_loops_within_near_distance))
        result.parameters.append(Parameter("IgnoreInconsistentLineSymbolEnds", ignore_inconsistent_line_symbol_ends))
        result.parameters.append(Parameter("AllowCoincidentSections", allow_coincident_sections))
        if type(right_side_nears) == list:
            for element in right_side_nears:
                result.parameters.append(Parameter("RightSideNears", element))
        elif right_side_nears is not None:
            result.parameters.append(Parameter("RightSideNears", right_side_nears))
        result.parameters.append(Parameter("EndCapStyle", end_cap_style))
        result.parameters.append(Parameter("JunctionIsEndExpression", junction_is_end_expression))
        result.generate_name()
        return result

    @classmethod
    def qa_touches_other_0(cls, touching: List[BaseDataset], touched: List[BaseDataset], valid_touch_geometry_constraint: str = None) -> Condition:
        """
        Finds all features in 'touchedClasses' that are touched by features in 'touchingClasses'
        """
        
        result = Condition("QaTouchesOther(0)")
        if type(touching) == list:
            for element in touching:
                result.parameters.append(Parameter("touching", element))
        elif touching is not None:
            result.parameters.append(Parameter("touching", touching))
        if type(touched) == list:
            for element in touched:
                result.parameters.append(Parameter("touched", element))
        elif touched is not None:
            result.parameters.append(Parameter("touched", touched))
        result.parameters.append(Parameter("ValidTouchGeometryConstraint", valid_touch_geometry_constraint))
        result.generate_name()
        return result

    @classmethod
    def qa_touches_other_1(cls, touching: BaseDataset, touched: BaseDataset, valid_touch_geometry_constraint: str = None) -> Condition:
        """
        Finds all features in 'touchedClass' that are touched by features in 'touchingClass'
        """
        
        result = Condition("QaTouchesOther(1)")
        result.parameters.append(Parameter("touching", touching))
        result.parameters.append(Parameter("touched", touched))
        result.parameters.append(Parameter("ValidTouchGeometryConstraint", valid_touch_geometry_constraint))
        result.generate_name()
        return result

    @classmethod
    def qa_touches_other_2(cls, touching: List[BaseDataset], touched: List[BaseDataset], valid_relation_constraint: str, valid_touch_geometry_constraint: str = None) -> Condition:
        """
        Finds all features in 'touchedClasses' that are touched by features in 'touchingClasses', and for which a given constraint is not fulfilled.
        """
        
        result = Condition("QaTouchesOther(2)")
        if type(touching) == list:
            for element in touching:
                result.parameters.append(Parameter("touching", element))
        elif touching is not None:
            result.parameters.append(Parameter("touching", touching))
        if type(touched) == list:
            for element in touched:
                result.parameters.append(Parameter("touched", element))
        elif touched is not None:
            result.parameters.append(Parameter("touched", touched))
        result.parameters.append(Parameter("validRelationConstraint", valid_relation_constraint))
        result.parameters.append(Parameter("ValidTouchGeometryConstraint", valid_touch_geometry_constraint))
        result.generate_name()
        return result

    @classmethod
    def qa_touches_other_3(cls, touching: BaseDataset, touched: BaseDataset, valid_relation_constraint: str, valid_touch_geometry_constraint: str = None) -> Condition:
        """
        Finds all features in 'touchedClass' that are touched by features in 'touchingClass', and for which a given constraint is not fulfilled.
        """
        
        result = Condition("QaTouchesOther(3)")
        result.parameters.append(Parameter("touching", touching))
        result.parameters.append(Parameter("touched", touched))
        result.parameters.append(Parameter("validRelationConstraint", valid_relation_constraint))
        result.parameters.append(Parameter("ValidTouchGeometryConstraint", valid_touch_geometry_constraint))
        result.generate_name()
        return result

    @classmethod
    def qa_touches_self_0(cls, feature_classes: List[BaseDataset], valid_touch_geometry_constraint: str = None) -> Condition:
        """
        Finds all features in 'featureClasses' that are touched by other features in 'featureClasses'
        """
        
        result = Condition("QaTouchesSelf(0)")
        if type(feature_classes) == list:
            for element in feature_classes:
                result.parameters.append(Parameter("featureClasses", element))
        elif feature_classes is not None:
            result.parameters.append(Parameter("featureClasses", feature_classes))
        result.parameters.append(Parameter("ValidTouchGeometryConstraint", valid_touch_geometry_constraint))
        result.generate_name()
        return result

    @classmethod
    def qa_touches_self_1(cls, feature_class: BaseDataset, valid_touch_geometry_constraint: str = None) -> Condition:
        """
        Finds all features in 'featureClass' that are touched by other features in 'featureClass'
        """
        
        result = Condition("QaTouchesSelf(1)")
        result.parameters.append(Parameter("featureClass", feature_class))
        result.parameters.append(Parameter("ValidTouchGeometryConstraint", valid_touch_geometry_constraint))
        result.generate_name()
        return result

    @classmethod
    def qa_touches_self_2(cls, feature_classes: List[BaseDataset], valid_relation_constraint: str, valid_touch_geometry_constraint: str = None) -> Condition:
        """
        Finds all features in 'featureClasses' that are touched by other features in 'featureClasses', and for which a given constraint is not fulfilled.
        """
        
        result = Condition("QaTouchesSelf(2)")
        if type(feature_classes) == list:
            for element in feature_classes:
                result.parameters.append(Parameter("featureClasses", element))
        elif feature_classes is not None:
            result.parameters.append(Parameter("featureClasses", feature_classes))
        result.parameters.append(Parameter("validRelationConstraint", valid_relation_constraint))
        result.parameters.append(Parameter("ValidTouchGeometryConstraint", valid_touch_geometry_constraint))
        result.generate_name()
        return result

    @classmethod
    def qa_touches_self_3(cls, feature_class: BaseDataset, valid_relation_constraint: str, valid_touch_geometry_constraint: str = None) -> Condition:
        """
        Finds all features in 'featureClass' that are touched by other features in 'featureClass', and for which a given constraint is not fulfilled.
        """
        
        result = Condition("QaTouchesSelf(3)")
        result.parameters.append(Parameter("featureClass", feature_class))
        result.parameters.append(Parameter("validRelationConstraint", valid_relation_constraint))
        result.parameters.append(Parameter("ValidTouchGeometryConstraint", valid_touch_geometry_constraint))
        result.generate_name()
        return result

    @classmethod
    def qa_trimmed_text_fields_0(cls, table: BaseDataset) -> Condition:
        """
        Finds rows with text fields having leading or trailing whitespace characters. All text fields of the table are checked. Fields with only whitespace characters are also reported.
        """
        
        result = Condition("QaTrimmedTextFields(0)")
        result.parameters.append(Parameter("table", table))
        result.generate_name()
        return result

    @classmethod
    def qa_trimmed_text_fields_1(cls, table: BaseDataset, allowed_white_space_only_count: int) -> Condition:
        """
        Finds rows with text fields having leading or trailing whitespace characters. All text fields of the table are checked. For fields that contain only whitespace, a maximum number of allowed whitespace characters can specified.
        """
        
        result = Condition("QaTrimmedTextFields(1)")
        result.parameters.append(Parameter("table", table))
        result.parameters.append(Parameter("allowedWhiteSpaceOnlyCount", allowed_white_space_only_count))
        result.generate_name()
        return result

    @classmethod
    def qa_trimmed_text_fields_2(cls, table: BaseDataset, text_field_name: str) -> Condition:
        """
        Finds rows that have leading or trailing whitespace characters in a specified text field. An error is reported also if the field contains only whitespace characters.
        """
        
        result = Condition("QaTrimmedTextFields(2)")
        result.parameters.append(Parameter("table", table))
        result.parameters.append(Parameter("textFieldName", text_field_name))
        result.generate_name()
        return result

    @classmethod
    def qa_trimmed_text_fields_3(cls, table: BaseDataset, allowed_white_space_only_count: int, text_field_name: str) -> Condition:
        """
        Finds rows that have leading or trailing whitespace characters in a specified text field. If the field contains only whitespace, a maximum number of allowed whitespace characters can specified.
        """
        
        result = Condition("QaTrimmedTextFields(3)")
        result.parameters.append(Parameter("table", table))
        result.parameters.append(Parameter("allowedWhiteSpaceOnlyCount", allowed_white_space_only_count))
        result.parameters.append(Parameter("textFieldName", text_field_name))
        result.generate_name()
        return result

    @classmethod
    def qa_trimmed_text_fields_4(cls, table: BaseDataset, allowed_white_space_only_count: int, text_field_names: List[str]) -> Condition:
        """
        Finds rows that have leading or trailing whitespace characters in a given list of text fields. If the field contains only whitespace, a maximum number of allowed whitespace characters can specified.
        """
        
        result = Condition("QaTrimmedTextFields(4)")
        result.parameters.append(Parameter("table", table))
        result.parameters.append(Parameter("allowedWhiteSpaceOnlyCount", allowed_white_space_only_count))
        if type(text_field_names) == list:
            for element in text_field_names:
                result.parameters.append(Parameter("textFieldNames", element))
        elif text_field_names is not None:
            result.parameters.append(Parameter("textFieldNames", text_field_names))
        result.generate_name()
        return result

    @classmethod
    def qa_trimmed_text_fields_5(cls, table: BaseDataset, allowed_white_space_only_count: int, text_field_names_string: str, field_list_type: FieldListType) -> Condition:
        """
        Finds rows that have leading or trailing whitespace characters in a given list of text fields. The field list can be defined by a concatenated string of either relevant or ignored fields. If the field contains only whitespace, a maximum number of allowed whitespace characters can specified.
        """
        
        result = Condition("QaTrimmedTextFields(5)")
        result.parameters.append(Parameter("table", table))
        result.parameters.append(Parameter("allowedWhiteSpaceOnlyCount", allowed_white_space_only_count))
        result.parameters.append(Parameter("textFieldNamesString", text_field_names_string))
        result.parameters.append(Parameter("fieldListType", field_list_type))
        result.generate_name()
        return result

    @classmethod
    def qa_trimmed_text_fields_6(cls, table: BaseDataset, allowed_white_space_only_count: int, text_field_names: List[str], field_list_type: FieldListType) -> Condition:
        """
        Finds rows that have leading or trailing whitespace characters in a given list of text fields. The field list can be defined by a list of either relevant or ignored fields. If the field contains only whitespace, a maximum number of allowed whitespace characters can specified.
        """
        
        result = Condition("QaTrimmedTextFields(6)")
        result.parameters.append(Parameter("table", table))
        result.parameters.append(Parameter("allowedWhiteSpaceOnlyCount", allowed_white_space_only_count))
        if type(text_field_names) == list:
            for element in text_field_names:
                result.parameters.append(Parameter("textFieldNames", element))
        elif text_field_names is not None:
            result.parameters.append(Parameter("textFieldNames", text_field_names))
        result.parameters.append(Parameter("fieldListType", field_list_type))
        result.generate_name()
        return result

    @classmethod
    def qa_unique_0(cls, table: BaseDataset, unique: str) -> Condition:
        """
        Finds rows in 'table' for which the values in the field(s) defined by 'unique' are not unique
        """
        
        result = Condition("QaUnique(0)")
        result.parameters.append(Parameter("table", table))
        result.parameters.append(Parameter("unique", unique))
        result.generate_name()
        return result

    @classmethod
    def qa_unique_1(cls, table: BaseDataset, unique: str, max_rows: int) -> Condition:
        """
        Finds rows in 'table' for which the values in the field(s) defined by 'unique' are not unique
        """
        
        result = Condition("QaUnique(1)")
        result.parameters.append(Parameter("table", table))
        result.parameters.append(Parameter("unique", unique))
        result.parameters.append(Parameter("maxRows", max_rows))
        result.generate_name()
        return result

    @classmethod
    def qa_unique_2(cls, tables: List[BaseDataset], uniques: List[str]) -> Condition:
        """
        Finds rows in 'tables' for which the values in the field(s) defined by 'uniques' are not unique across all tables
        """
        
        result = Condition("QaUnique(2)")
        if type(tables) == list:
            for element in tables:
                result.parameters.append(Parameter("tables", element))
        elif tables is not None:
            result.parameters.append(Parameter("tables", tables))
        if type(uniques) == list:
            for element in uniques:
                result.parameters.append(Parameter("uniques", element))
        elif uniques is not None:
            result.parameters.append(Parameter("uniques", uniques))
        result.generate_name()
        return result

    @classmethod
    def qa_unreferenced_rows_0(cls, referenced_table: BaseDataset, referencing_tables: List[BaseDataset], relations: List[str]) -> Condition:
        """
        Finds rows in a table that are not referenced by any row in a collection of referencing tables
        """
        
        result = Condition("QaUnreferencedRows(0)")
        result.parameters.append(Parameter("referencedTable", referenced_table))
        if type(referencing_tables) == list:
            for element in referencing_tables:
                result.parameters.append(Parameter("referencingTables", element))
        elif referencing_tables is not None:
            result.parameters.append(Parameter("referencingTables", referencing_tables))
        if type(relations) == list:
            for element in relations:
                result.parameters.append(Parameter("relations", element))
        elif relations is not None:
            result.parameters.append(Parameter("relations", relations))
        result.generate_name()
        return result

    @classmethod
    def qa_valid_coordinate_fields_0(cls, feature_class: BaseDataset, x_coordinate_field_name: str, y_coordinate_field_name: str, z_coordinate_field_name: str, xy_tolerance: float, z_tolerance: float, culture: str, allow_x_y_field_values_for_undefined_shape: bool = False, allow_z_field_value_for_undefined_shape: bool = False, allow_missing_z_field_value_for_defined_shape: bool = False, allow_missing_x_y_field_value_for_defined_shape: bool = False) -> Condition:
        """
        Finds features with attributes for XY and\/or Z coordinate values whose values differ significantly from the coordinates of the feature. 
        """
        
        result = Condition("QaValidCoordinateFields(0)")
        result.parameters.append(Parameter("featureClass", feature_class))
        result.parameters.append(Parameter("xCoordinateFieldName", x_coordinate_field_name))
        result.parameters.append(Parameter("yCoordinateFieldName", y_coordinate_field_name))
        result.parameters.append(Parameter("zCoordinateFieldName", z_coordinate_field_name))
        result.parameters.append(Parameter("xyTolerance", xy_tolerance))
        result.parameters.append(Parameter("zTolerance", z_tolerance))
        result.parameters.append(Parameter("culture", culture))
        result.parameters.append(Parameter("AllowXYFieldValuesForUndefinedShape", allow_x_y_field_values_for_undefined_shape))
        result.parameters.append(Parameter("AllowZFieldValueForUndefinedShape", allow_z_field_value_for_undefined_shape))
        result.parameters.append(Parameter("AllowMissingZFieldValueForDefinedShape", allow_missing_z_field_value_for_defined_shape))
        result.parameters.append(Parameter("AllowMissingXYFieldValueForDefinedShape", allow_missing_x_y_field_value_for_defined_shape))
        result.generate_name()
        return result

    @classmethod
    def qa_valid_date_values_0(cls, table: BaseDataset, minimum_date_value: datetime, maximum_date_value: datetime) -> Condition:
        """
        Finds rows with date field values that are invalid or outside a defined date range
        """
        
        result = Condition("QaValidDateValues(0)")
        result.parameters.append(Parameter("table", table))
        result.parameters.append(Parameter("minimumDateValue", minimum_date_value))
        result.parameters.append(Parameter("maximumDateValue", maximum_date_value))
        result.generate_name()
        return result

    @classmethod
    def qa_valid_date_values_1(cls, table: BaseDataset, minimum_date_value: datetime, maximum_date_value: datetime, date_field_names: List[str]) -> Condition:
        """
        Finds rows with date values from a given list of date fields that are invalid or outside a defined date range
        """
        
        result = Condition("QaValidDateValues(1)")
        result.parameters.append(Parameter("table", table))
        result.parameters.append(Parameter("minimumDateValue", minimum_date_value))
        result.parameters.append(Parameter("maximumDateValue", maximum_date_value))
        if type(date_field_names) == list:
            for element in date_field_names:
                result.parameters.append(Parameter("dateFieldNames", element))
        elif date_field_names is not None:
            result.parameters.append(Parameter("dateFieldNames", date_field_names))
        result.generate_name()
        return result

    @classmethod
    def qa_valid_date_values_2(cls, table: BaseDataset, minimum_date_value: datetime, maximum_date_value: datetime, date_field_names_string: str) -> Condition:
        """
        Finds rows with date values from a given list of date fields that are invalid or outside a defined date range. The list of date fields can be defined by a concatenated string of field names
        """
        
        result = Condition("QaValidDateValues(2)")
        result.parameters.append(Parameter("table", table))
        result.parameters.append(Parameter("minimumDateValue", minimum_date_value))
        result.parameters.append(Parameter("maximumDateValue", maximum_date_value))
        result.parameters.append(Parameter("dateFieldNamesString", date_field_names_string))
        result.generate_name()
        return result

    @classmethod
    def qa_valid_date_values_3(cls, table: BaseDataset, minimum_date_value: datetime, maximum_date_time_relative_to_now: str) -> Condition:
        """
        Finds rows with date field values that are invalid or outside a defined date range. The maximum date value can be specified relative to the current date\/time
        """
        
        result = Condition("QaValidDateValues(3)")
        result.parameters.append(Parameter("table", table))
        result.parameters.append(Parameter("minimumDateValue", minimum_date_value))
        result.parameters.append(Parameter("maximumDateTimeRelativeToNow", maximum_date_time_relative_to_now))
        result.generate_name()
        return result

    @classmethod
    def qa_valid_date_values_4(cls, table: BaseDataset, minimum_date_value: datetime, maximum_date_time_relative_to_now: str, date_field_names_string: str) -> Condition:
        """
        Finds rows with date values from a given list of date fields that are invalid or outside a defined date range. The list of date fields can be defined by a concatenated string of field names. The maximum date value can be specified relative to the current date\/time
        """
        
        result = Condition("QaValidDateValues(4)")
        result.parameters.append(Parameter("table", table))
        result.parameters.append(Parameter("minimumDateValue", minimum_date_value))
        result.parameters.append(Parameter("maximumDateTimeRelativeToNow", maximum_date_time_relative_to_now))
        result.parameters.append(Parameter("dateFieldNamesString", date_field_names_string))
        result.generate_name()
        return result

    @classmethod
    def qa_valid_date_values_5(cls, table: BaseDataset, minimum_date_time_relative_to_now: str, maximum_date_value: datetime, date_field_names_string: str) -> Condition:
        """
        Finds rows with date values from a given list of date fields that are invalid or outside a defined date range. The list of date fields can be defined by a concatenated string of field names. The minimum date value can be specified relative to the current date\/time
        """
        
        result = Condition("QaValidDateValues(5)")
        result.parameters.append(Parameter("table", table))
        result.parameters.append(Parameter("minimumDateTimeRelativeToNow", minimum_date_time_relative_to_now))
        result.parameters.append(Parameter("maximumDateValue", maximum_date_value))
        result.parameters.append(Parameter("dateFieldNamesString", date_field_names_string))
        result.generate_name()
        return result

    @classmethod
    def qa_valid_date_values_6(cls, table: BaseDataset, minimum_date_time_relative_to_now: str, maximum_date_time_relative_to_now: str, date_field_names_string: str) -> Condition:
        """
        Finds rows with date values from a given list of date fields that are invalid or outside a defined date range. The list of date fields can be defined by a concatenated string of field names. The minimum and maximum date values can be specified relative to the current date\/time
        """
        
        result = Condition("QaValidDateValues(6)")
        result.parameters.append(Parameter("table", table))
        result.parameters.append(Parameter("minimumDateTimeRelativeToNow", minimum_date_time_relative_to_now))
        result.parameters.append(Parameter("maximumDateTimeRelativeToNow", maximum_date_time_relative_to_now))
        result.parameters.append(Parameter("dateFieldNamesString", date_field_names_string))
        result.generate_name()
        return result

    @classmethod
    def qa_valid_non_linear_segments_0(cls, feature_class: BaseDataset) -> Condition:
        """
        Finds features with invalid non-linear segments. Currently, circular arcs that degenerated to a line and therefore have no center point are found.
        """
        
        result = Condition("QaValidNonLinearSegments(0)")
        result.parameters.append(Parameter("featureClass", feature_class))
        result.generate_name()
        return result

    @classmethod
    def qa_valid_non_linear_segments_1(cls, feature_class: BaseDataset, minimum_chord_height: float) -> Condition:
        """
        Finds features with invalid non-linear segments. Currently, circular arcs that degenerated to a line and therefore have no center point are found. Additionally, circular arcs with a chord height smaller than a specified value may be identified.
        """
        
        result = Condition("QaValidNonLinearSegments(1)")
        result.parameters.append(Parameter("featureClass", feature_class))
        result.parameters.append(Parameter("minimumChordHeight", minimum_chord_height))
        result.generate_name()
        return result

    @classmethod
    def qa_valid_urls_0(cls, table: BaseDataset, url_expression: str, maximum_parallel_tasks: int = 1) -> Condition:
        """
        Checks field values in 'table' for valid URLs. The URLs can be stored in a single field or it can be the result of a SQL expression referencing one or more fields. Supported are HTTP or file system URLs (UNC paths or paths to mapped drives). FTP URLs are not supported yet
        """
        
        result = Condition("QaValidUrls(0)")
        result.parameters.append(Parameter("table", table))
        result.parameters.append(Parameter("urlExpression", url_expression))
        result.parameters.append(Parameter("MaximumParallelTasks", maximum_parallel_tasks))
        result.generate_name()
        return result

    @classmethod
    def qa_value_0(cls, table: BaseDataset, fields: List[str]) -> Condition:
        """
        Finds all rows in 'table' with invalid data types. This can be the case for GUID-values. The test itself checks all datatypes
        """
        
        result = Condition("QaValue(0)")
        result.parameters.append(Parameter("table", table))
        if type(fields) == list:
            for element in fields:
                result.parameters.append(Parameter("fields", element))
        elif fields is not None:
            result.parameters.append(Parameter("fields", fields))
        result.generate_name()
        return result

    @classmethod
    def qa_vertex_coincidence_0(cls, feature_class: BaseDataset, point_tolerance: float = -1, edge_tolerance: float = -1, require_vertex_on_nearby_edge: bool = True, coincidence_tolerance: float = 0, is3_d: bool = False, z_tolerance: float = 0, z_coincidence_tolerance: float = 0, report_coordinates: bool = False) -> Condition:
        """
        Finds vertices for which there is no coincident vertex and\/or edge within the geometry of features of a given feature class.
        """
        
        result = Condition("QaVertexCoincidence(0)")
        result.parameters.append(Parameter("featureClass", feature_class))
        result.parameters.append(Parameter("PointTolerance", point_tolerance))
        result.parameters.append(Parameter("EdgeTolerance", edge_tolerance))
        result.parameters.append(Parameter("RequireVertexOnNearbyEdge", require_vertex_on_nearby_edge))
        result.parameters.append(Parameter("CoincidenceTolerance", coincidence_tolerance))
        result.parameters.append(Parameter("Is3D", is3_d))
        result.parameters.append(Parameter("ZTolerance", z_tolerance))
        result.parameters.append(Parameter("ZCoincidenceTolerance", z_coincidence_tolerance))
        result.parameters.append(Parameter("ReportCoordinates", report_coordinates))
        result.generate_name()
        return result

    @classmethod
    def qa_vertex_coincidence_other_0(cls, feature_class: BaseDataset, related_class: BaseDataset, point_tolerance: float = -1, edge_tolerance: float = -1, require_vertex_on_nearby_edge: bool = True, coincidence_tolerance: float = 0, z_tolerance: float = 0, z_coincidence_tolerance: float = 0, is3_d: bool = False, bidirectional: bool = True, report_coordinates: bool = False) -> Condition:
        """
        Finds vertices for which there is no coincident vertex and\/or edge in nearby features of another feature class.
        """
        
        result = Condition("QaVertexCoincidenceOther(0)")
        result.parameters.append(Parameter("featureClass", feature_class))
        result.parameters.append(Parameter("relatedClass", related_class))
        result.parameters.append(Parameter("PointTolerance", point_tolerance))
        result.parameters.append(Parameter("EdgeTolerance", edge_tolerance))
        result.parameters.append(Parameter("RequireVertexOnNearbyEdge", require_vertex_on_nearby_edge))
        result.parameters.append(Parameter("CoincidenceTolerance", coincidence_tolerance))
        result.parameters.append(Parameter("ZTolerance", z_tolerance))
        result.parameters.append(Parameter("ZCoincidenceTolerance", z_coincidence_tolerance))
        result.parameters.append(Parameter("Is3D", is3_d))
        result.parameters.append(Parameter("Bidirectional", bidirectional))
        result.parameters.append(Parameter("ReportCoordinates", report_coordinates))
        result.generate_name()
        return result

    @classmethod
    def qa_vertex_coincidence_other_1(cls, feature_classes: List[BaseDataset], related_classes: List[BaseDataset], point_tolerance: float = -1, edge_tolerance: float = -1, require_vertex_on_nearby_edge: bool = True, coincidence_tolerance: float = 0, z_tolerance: float = 0, z_coincidence_tolerance: float = 0, is3_d: bool = False, bidirectional: bool = True, report_coordinates: bool = False) -> Condition:
        """
        Finds vertices for which there is no coincident vertex and\/or edge in nearby features of a given list of other feature classes.
        """
        
        result = Condition("QaVertexCoincidenceOther(1)")
        if type(feature_classes) == list:
            for element in feature_classes:
                result.parameters.append(Parameter("featureClasses", element))
        elif feature_classes is not None:
            result.parameters.append(Parameter("featureClasses", feature_classes))
        if type(related_classes) == list:
            for element in related_classes:
                result.parameters.append(Parameter("relatedClasses", element))
        elif related_classes is not None:
            result.parameters.append(Parameter("relatedClasses", related_classes))
        result.parameters.append(Parameter("PointTolerance", point_tolerance))
        result.parameters.append(Parameter("EdgeTolerance", edge_tolerance))
        result.parameters.append(Parameter("RequireVertexOnNearbyEdge", require_vertex_on_nearby_edge))
        result.parameters.append(Parameter("CoincidenceTolerance", coincidence_tolerance))
        result.parameters.append(Parameter("ZTolerance", z_tolerance))
        result.parameters.append(Parameter("ZCoincidenceTolerance", z_coincidence_tolerance))
        result.parameters.append(Parameter("Is3D", is3_d))
        result.parameters.append(Parameter("Bidirectional", bidirectional))
        result.parameters.append(Parameter("ReportCoordinates", report_coordinates))
        result.generate_name()
        return result

    @classmethod
    def qa_vertex_coincidence_other_2(cls, feature_classes: List[BaseDataset], related_classes: List[BaseDataset], allowed_non_coincidence_condition: str, point_tolerance: float = -1, edge_tolerance: float = -1, require_vertex_on_nearby_edge: bool = True, coincidence_tolerance: float = 0, z_tolerance: float = 0, z_coincidence_tolerance: float = 0, is3_d: bool = False, bidirectional: bool = True, report_coordinates: bool = False) -> Condition:
        """
        Finds vertices for which there is no coincident vertex and\/or edge in nearby features of a given list of other feature classes. If an optional constraint is fulfilled for a pair of features, non-coincidence of vertices is allowed for these features.
        """
        
        result = Condition("QaVertexCoincidenceOther(2)")
        if type(feature_classes) == list:
            for element in feature_classes:
                result.parameters.append(Parameter("featureClasses", element))
        elif feature_classes is not None:
            result.parameters.append(Parameter("featureClasses", feature_classes))
        if type(related_classes) == list:
            for element in related_classes:
                result.parameters.append(Parameter("relatedClasses", element))
        elif related_classes is not None:
            result.parameters.append(Parameter("relatedClasses", related_classes))
        result.parameters.append(Parameter("allowedNonCoincidenceCondition", allowed_non_coincidence_condition))
        result.parameters.append(Parameter("PointTolerance", point_tolerance))
        result.parameters.append(Parameter("EdgeTolerance", edge_tolerance))
        result.parameters.append(Parameter("RequireVertexOnNearbyEdge", require_vertex_on_nearby_edge))
        result.parameters.append(Parameter("CoincidenceTolerance", coincidence_tolerance))
        result.parameters.append(Parameter("ZTolerance", z_tolerance))
        result.parameters.append(Parameter("ZCoincidenceTolerance", z_coincidence_tolerance))
        result.parameters.append(Parameter("Is3D", is3_d))
        result.parameters.append(Parameter("Bidirectional", bidirectional))
        result.parameters.append(Parameter("ReportCoordinates", report_coordinates))
        result.generate_name()
        return result

    @classmethod
    def qa_vertex_coincidence_self_0(cls, feature_class: BaseDataset, point_tolerance: float = -1, edge_tolerance: float = -1, require_vertex_on_nearby_edge: bool = True, coincidence_tolerance: float = 0, is3_d: bool = False, verify_within_feature: bool = False, z_tolerance: float = 0, z_coincidence_tolerance: float = 0, report_coordinates: bool = False) -> Condition:
        """
        Finds vertices for which there is no coincident vertex and\/or edge in nearby features of a given feature class.
        """
        
        result = Condition("QaVertexCoincidenceSelf(0)")
        result.parameters.append(Parameter("featureClass", feature_class))
        result.parameters.append(Parameter("PointTolerance", point_tolerance))
        result.parameters.append(Parameter("EdgeTolerance", edge_tolerance))
        result.parameters.append(Parameter("RequireVertexOnNearbyEdge", require_vertex_on_nearby_edge))
        result.parameters.append(Parameter("CoincidenceTolerance", coincidence_tolerance))
        result.parameters.append(Parameter("Is3D", is3_d))
        result.parameters.append(Parameter("VerifyWithinFeature", verify_within_feature))
        result.parameters.append(Parameter("ZTolerance", z_tolerance))
        result.parameters.append(Parameter("ZCoincidenceTolerance", z_coincidence_tolerance))
        result.parameters.append(Parameter("ReportCoordinates", report_coordinates))
        result.generate_name()
        return result

    @classmethod
    def qa_vertex_coincidence_self_1(cls, feature_classes: List[BaseDataset], point_tolerance: float = -1, edge_tolerance: float = -1, require_vertex_on_nearby_edge: bool = True, coincidence_tolerance: float = 0, is3_d: bool = False, verify_within_feature: bool = False, z_tolerance: float = 0, z_coincidence_tolerance: float = 0, report_coordinates: bool = False) -> Condition:
        """
        Finds vertices for which there is no coincident vertex and\/or edge in nearby features of a given list of feature classes.
        """
        
        result = Condition("QaVertexCoincidenceSelf(1)")
        if type(feature_classes) == list:
            for element in feature_classes:
                result.parameters.append(Parameter("featureClasses", element))
        elif feature_classes is not None:
            result.parameters.append(Parameter("featureClasses", feature_classes))
        result.parameters.append(Parameter("PointTolerance", point_tolerance))
        result.parameters.append(Parameter("EdgeTolerance", edge_tolerance))
        result.parameters.append(Parameter("RequireVertexOnNearbyEdge", require_vertex_on_nearby_edge))
        result.parameters.append(Parameter("CoincidenceTolerance", coincidence_tolerance))
        result.parameters.append(Parameter("Is3D", is3_d))
        result.parameters.append(Parameter("VerifyWithinFeature", verify_within_feature))
        result.parameters.append(Parameter("ZTolerance", z_tolerance))
        result.parameters.append(Parameter("ZCoincidenceTolerance", z_coincidence_tolerance))
        result.parameters.append(Parameter("ReportCoordinates", report_coordinates))
        result.generate_name()
        return result

    @classmethod
    def qa_vertex_coincidence_self_2(cls, feature_classes: List[BaseDataset], allowed_non_coincidence_condition: str, point_tolerance: float = -1, edge_tolerance: float = -1, require_vertex_on_nearby_edge: bool = True, coincidence_tolerance: float = 0, is3_d: bool = False, verify_within_feature: bool = False, z_tolerance: float = 0, z_coincidence_tolerance: float = 0, report_coordinates: bool = False) -> Condition:
        """
        Finds vertices for which there is no coincident vertex and\/or edge in nearby features of a given list of feature classes. If an optional constraint is fulfilled for a pair of features, non-coincidence of vertices is allowed for these features.
        """
        
        result = Condition("QaVertexCoincidenceSelf(2)")
        if type(feature_classes) == list:
            for element in feature_classes:
                result.parameters.append(Parameter("featureClasses", element))
        elif feature_classes is not None:
            result.parameters.append(Parameter("featureClasses", feature_classes))
        result.parameters.append(Parameter("allowedNonCoincidenceCondition", allowed_non_coincidence_condition))
        result.parameters.append(Parameter("PointTolerance", point_tolerance))
        result.parameters.append(Parameter("EdgeTolerance", edge_tolerance))
        result.parameters.append(Parameter("RequireVertexOnNearbyEdge", require_vertex_on_nearby_edge))
        result.parameters.append(Parameter("CoincidenceTolerance", coincidence_tolerance))
        result.parameters.append(Parameter("Is3D", is3_d))
        result.parameters.append(Parameter("VerifyWithinFeature", verify_within_feature))
        result.parameters.append(Parameter("ZTolerance", z_tolerance))
        result.parameters.append(Parameter("ZCoincidenceTolerance", z_coincidence_tolerance))
        result.parameters.append(Parameter("ReportCoordinates", report_coordinates))
        result.generate_name()
        return result

    @classmethod
    def qa_within_box_0(cls, feature_class: BaseDataset, x_min: float, y_min: float, x_max: float, y_max: float) -> Condition:
        """
        Finds features that are not fully within a specified box
        """
        
        result = Condition("QaWithinBox(0)")
        result.parameters.append(Parameter("featureClass", feature_class))
        result.parameters.append(Parameter("xMin", x_min))
        result.parameters.append(Parameter("yMin", y_min))
        result.parameters.append(Parameter("xMax", x_max))
        result.parameters.append(Parameter("yMax", y_max))
        result.generate_name()
        return result

    @classmethod
    def qa_within_box_1(cls, feature_class: BaseDataset, x_min: float, y_min: float, x_max: float, y_max: float, report_only_outside_parts: bool) -> Condition:
        """
        Finds features that are not fully within a specified box
        """
        
        result = Condition("QaWithinBox(1)")
        result.parameters.append(Parameter("featureClass", feature_class))
        result.parameters.append(Parameter("xMin", x_min))
        result.parameters.append(Parameter("yMin", y_min))
        result.parameters.append(Parameter("xMax", x_max))
        result.parameters.append(Parameter("yMax", y_max))
        result.parameters.append(Parameter("reportOnlyOutsideParts", report_only_outside_parts))
        result.generate_name()
        return result

    @classmethod
    def qa_within_z_range_0(cls, feature_class: BaseDataset, minimum_z_value: float, maximum_z_value: float) -> Condition:
        """
        Finds features with Z values outside of a defined range.
        
        - Supported for points, lines, polygons, multipoints and multipatches.
        - For lines and polygons, individual errors are reported for consecutive segments (or parts of segments) exceeding the same boundary of the Z range.
        - For multipoints and multipatches, one error is reported for all points exceeding the same boundary of the Z range.
        """
        
        result = Condition("QaWithinZRange(0)")
        result.parameters.append(Parameter("featureClass", feature_class))
        result.parameters.append(Parameter("minimumZValue", minimum_z_value))
        result.parameters.append(Parameter("maximumZValue", maximum_z_value))
        result.generate_name()
        return result

    @classmethod
    def qa_within_z_range_1(cls, feature_class: BaseDataset, minimum_z_value: float, maximum_z_value: float, allowed_z_values: List[float]) -> Condition:
        """
        Finds features with Z values outside of a defined range, and allowing for special values outside the defined range (e.g. -9999).
        
        - Supported for points, lines, polygons, multipoints and multipatches.
        - For lines and polygons, individual errors are reported for consecutive segments (or parts of segments) exceeding the same boundary of the Z range.
        - For multipoints and multipatches, one error is reported for all points exceeding the same boundary of the Z range.
        """
        
        result = Condition("QaWithinZRange(1)")
        result.parameters.append(Parameter("featureClass", feature_class))
        result.parameters.append(Parameter("minimumZValue", minimum_z_value))
        result.parameters.append(Parameter("maximumZValue", maximum_z_value))
        if type(allowed_z_values) == list:
            for element in allowed_z_values:
                result.parameters.append(Parameter("allowedZValues", element))
        elif allowed_z_values is not None:
            result.parameters.append(Parameter("allowedZValues", allowed_z_values))
        result.generate_name()
        return result

    @classmethod
    def qa_z_difference_other_0(cls, feature_class: BaseDataset, related_class: BaseDataset, limit: float, z_comparison_method: ZComparisonMethod, z_relation_constraint: str, relevant_relation_condition: str = None, minimum_z_difference_expression: str = None, maximum_z_difference_expression: str = None, use_distance_from_reference_ring_plane: bool = False, reference_ring_plane_coplanarity_tolerance: float = 0, ignore_non_coplanar_reference_rings: bool = False) -> Condition:
        """
        Finds features where the Z difference to features from another feature class is less than 'limit'
        """
        
        result = Condition("QaZDifferenceOther(0)")
        result.parameters.append(Parameter("featureClass", feature_class))
        result.parameters.append(Parameter("relatedClass", related_class))
        result.parameters.append(Parameter("limit", limit))
        result.parameters.append(Parameter("zComparisonMethod", z_comparison_method))
        result.parameters.append(Parameter("zRelationConstraint", z_relation_constraint))
        result.parameters.append(Parameter("RelevantRelationCondition", relevant_relation_condition))
        result.parameters.append(Parameter("MinimumZDifferenceExpression", minimum_z_difference_expression))
        result.parameters.append(Parameter("MaximumZDifferenceExpression", maximum_z_difference_expression))
        result.parameters.append(Parameter("UseDistanceFromReferenceRingPlane", use_distance_from_reference_ring_plane))
        result.parameters.append(Parameter("ReferenceRingPlaneCoplanarityTolerance", reference_ring_plane_coplanarity_tolerance))
        result.parameters.append(Parameter("IgnoreNonCoplanarReferenceRings", ignore_non_coplanar_reference_rings))
        result.generate_name()
        return result

    @classmethod
    def qa_z_difference_other_1(cls, feature_classes: List[BaseDataset], related_classes: List[BaseDataset], limit: float, z_comparison_method: ZComparisonMethod, z_relation_constraint: str, relevant_relation_condition: str = None, minimum_z_difference_expression: str = None, maximum_z_difference_expression: str = None, use_distance_from_reference_ring_plane: bool = False, reference_ring_plane_coplanarity_tolerance: float = 0, ignore_non_coplanar_reference_rings: bool = False) -> Condition:
        """
        Finds features where the Z difference to features from a list of other feature classes is less than 'limit'
        """
        
        result = Condition("QaZDifferenceOther(1)")
        if type(feature_classes) == list:
            for element in feature_classes:
                result.parameters.append(Parameter("featureClasses", element))
        elif feature_classes is not None:
            result.parameters.append(Parameter("featureClasses", feature_classes))
        if type(related_classes) == list:
            for element in related_classes:
                result.parameters.append(Parameter("relatedClasses", element))
        elif related_classes is not None:
            result.parameters.append(Parameter("relatedClasses", related_classes))
        result.parameters.append(Parameter("limit", limit))
        result.parameters.append(Parameter("zComparisonMethod", z_comparison_method))
        result.parameters.append(Parameter("zRelationConstraint", z_relation_constraint))
        result.parameters.append(Parameter("RelevantRelationCondition", relevant_relation_condition))
        result.parameters.append(Parameter("MinimumZDifferenceExpression", minimum_z_difference_expression))
        result.parameters.append(Parameter("MaximumZDifferenceExpression", maximum_z_difference_expression))
        result.parameters.append(Parameter("UseDistanceFromReferenceRingPlane", use_distance_from_reference_ring_plane))
        result.parameters.append(Parameter("ReferenceRingPlaneCoplanarityTolerance", reference_ring_plane_coplanarity_tolerance))
        result.parameters.append(Parameter("IgnoreNonCoplanarReferenceRings", ignore_non_coplanar_reference_rings))
        result.generate_name()
        return result

    @classmethod
    def qa_z_difference_other_2(cls, feature_class: BaseDataset, related_class: BaseDataset, minimum_z_difference: float, maximum_z_difference: float, z_comparison_method: ZComparisonMethod, z_relation_constraint: str, relevant_relation_condition: str = None, minimum_z_difference_expression: str = None, maximum_z_difference_expression: str = None, use_distance_from_reference_ring_plane: bool = False, reference_ring_plane_coplanarity_tolerance: float = 0, ignore_non_coplanar_reference_rings: bool = False) -> Condition:
        """
        Finds features where the Z difference to another feature is not between 'minimumZDifference' and 'maximumZDifference'
        """
        
        result = Condition("QaZDifferenceOther(2)")
        result.parameters.append(Parameter("featureClass", feature_class))
        result.parameters.append(Parameter("relatedClass", related_class))
        result.parameters.append(Parameter("minimumZDifference", minimum_z_difference))
        result.parameters.append(Parameter("maximumZDifference", maximum_z_difference))
        result.parameters.append(Parameter("zComparisonMethod", z_comparison_method))
        result.parameters.append(Parameter("zRelationConstraint", z_relation_constraint))
        result.parameters.append(Parameter("RelevantRelationCondition", relevant_relation_condition))
        result.parameters.append(Parameter("MinimumZDifferenceExpression", minimum_z_difference_expression))
        result.parameters.append(Parameter("MaximumZDifferenceExpression", maximum_z_difference_expression))
        result.parameters.append(Parameter("UseDistanceFromReferenceRingPlane", use_distance_from_reference_ring_plane))
        result.parameters.append(Parameter("ReferenceRingPlaneCoplanarityTolerance", reference_ring_plane_coplanarity_tolerance))
        result.parameters.append(Parameter("IgnoreNonCoplanarReferenceRings", ignore_non_coplanar_reference_rings))
        result.generate_name()
        return result

    @classmethod
    def qa_z_difference_other_3(cls, feature_classes: List[BaseDataset], related_classes: List[BaseDataset], minimum_z_difference: float, maximum_z_difference: float, z_comparison_method: ZComparisonMethod, z_relation_constraint: str, relevant_relation_condition: str = None, minimum_z_difference_expression: str = None, maximum_z_difference_expression: str = None, use_distance_from_reference_ring_plane: bool = False, reference_ring_plane_coplanarity_tolerance: float = 0, ignore_non_coplanar_reference_rings: bool = False) -> Condition:
        """
        Finds features where the Z difference to features from a list of other feature classes is not between 'minimumZDifference' and 'maximumZDifference'
        """
        
        result = Condition("QaZDifferenceOther(3)")
        if type(feature_classes) == list:
            for element in feature_classes:
                result.parameters.append(Parameter("featureClasses", element))
        elif feature_classes is not None:
            result.parameters.append(Parameter("featureClasses", feature_classes))
        if type(related_classes) == list:
            for element in related_classes:
                result.parameters.append(Parameter("relatedClasses", element))
        elif related_classes is not None:
            result.parameters.append(Parameter("relatedClasses", related_classes))
        result.parameters.append(Parameter("minimumZDifference", minimum_z_difference))
        result.parameters.append(Parameter("maximumZDifference", maximum_z_difference))
        result.parameters.append(Parameter("zComparisonMethod", z_comparison_method))
        result.parameters.append(Parameter("zRelationConstraint", z_relation_constraint))
        result.parameters.append(Parameter("RelevantRelationCondition", relevant_relation_condition))
        result.parameters.append(Parameter("MinimumZDifferenceExpression", minimum_z_difference_expression))
        result.parameters.append(Parameter("MaximumZDifferenceExpression", maximum_z_difference_expression))
        result.parameters.append(Parameter("UseDistanceFromReferenceRingPlane", use_distance_from_reference_ring_plane))
        result.parameters.append(Parameter("ReferenceRingPlaneCoplanarityTolerance", reference_ring_plane_coplanarity_tolerance))
        result.parameters.append(Parameter("IgnoreNonCoplanarReferenceRings", ignore_non_coplanar_reference_rings))
        result.generate_name()
        return result

    @classmethod
    def qa_z_difference_self_0(cls, feature_class: BaseDataset, limit: float, z_comparison_method: ZComparisonMethod, z_relation_constraint: str, minimum_z_difference_expression: str = None, maximum_z_difference_expression: str = None) -> Condition:
        """
        Finds features where the Z difference to another feature is less than 'limit'
        """
        
        result = Condition("QaZDifferenceSelf(0)")
        result.parameters.append(Parameter("featureClass", feature_class))
        result.parameters.append(Parameter("limit", limit))
        result.parameters.append(Parameter("zComparisonMethod", z_comparison_method))
        result.parameters.append(Parameter("zRelationConstraint", z_relation_constraint))
        result.parameters.append(Parameter("MinimumZDifferenceExpression", minimum_z_difference_expression))
        result.parameters.append(Parameter("MaximumZDifferenceExpression", maximum_z_difference_expression))
        result.generate_name()
        return result

    @classmethod
    def qa_z_difference_self_1(cls, feature_classes: List[BaseDataset], limit: float, z_comparison_method: ZComparisonMethod, z_relation_constraint: str, minimum_z_difference_expression: str = None, maximum_z_difference_expression: str = None) -> Condition:
        """
        Finds features where the Z difference to another feature within a list of feature classes is less than 'limit'
        """
        
        result = Condition("QaZDifferenceSelf(1)")
        if type(feature_classes) == list:
            for element in feature_classes:
                result.parameters.append(Parameter("featureClasses", element))
        elif feature_classes is not None:
            result.parameters.append(Parameter("featureClasses", feature_classes))
        result.parameters.append(Parameter("limit", limit))
        result.parameters.append(Parameter("zComparisonMethod", z_comparison_method))
        result.parameters.append(Parameter("zRelationConstraint", z_relation_constraint))
        result.parameters.append(Parameter("MinimumZDifferenceExpression", minimum_z_difference_expression))
        result.parameters.append(Parameter("MaximumZDifferenceExpression", maximum_z_difference_expression))
        result.generate_name()
        return result

    @classmethod
    def qa_z_difference_self_2(cls, feature_class: BaseDataset, minimum_z_difference: float, maximum_z_difference: float, z_comparison_method: ZComparisonMethod, z_relation_constraint: str, minimum_z_difference_expression: str = None, maximum_z_difference_expression: str = None) -> Condition:
        """
        Finds features where the Z difference to another feature is not between 'minimumZDifference' and 'maximumZDifference'
        """
        
        result = Condition("QaZDifferenceSelf(2)")
        result.parameters.append(Parameter("featureClass", feature_class))
        result.parameters.append(Parameter("minimumZDifference", minimum_z_difference))
        result.parameters.append(Parameter("maximumZDifference", maximum_z_difference))
        result.parameters.append(Parameter("zComparisonMethod", z_comparison_method))
        result.parameters.append(Parameter("zRelationConstraint", z_relation_constraint))
        result.parameters.append(Parameter("MinimumZDifferenceExpression", minimum_z_difference_expression))
        result.parameters.append(Parameter("MaximumZDifferenceExpression", maximum_z_difference_expression))
        result.generate_name()
        return result

    @classmethod
    def qa_z_difference_self_3(cls, feature_classes: List[BaseDataset], minimum_z_difference: float, maximum_z_difference: float, z_comparison_method: ZComparisonMethod, z_relation_constraint: str, minimum_z_difference_expression: str = None, maximum_z_difference_expression: str = None) -> Condition:
        """
        Finds features where the Z difference to another feature within a list of feature classes is not between 'minimumZDifference' and 'maximumZDifference'
        """
        
        result = Condition("QaZDifferenceSelf(3)")
        if type(feature_classes) == list:
            for element in feature_classes:
                result.parameters.append(Parameter("featureClasses", element))
        elif feature_classes is not None:
            result.parameters.append(Parameter("featureClasses", feature_classes))
        result.parameters.append(Parameter("minimumZDifference", minimum_z_difference))
        result.parameters.append(Parameter("maximumZDifference", maximum_z_difference))
        result.parameters.append(Parameter("zComparisonMethod", z_comparison_method))
        result.parameters.append(Parameter("zRelationConstraint", z_relation_constraint))
        result.parameters.append(Parameter("MinimumZDifferenceExpression", minimum_z_difference_expression))
        result.parameters.append(Parameter("MaximumZDifferenceExpression", maximum_z_difference_expression))
        result.generate_name()
        return result

    @classmethod
    def qa_constraints_list_factory(cls, table: BaseDataset, constraints_table: BaseDataset, expression_field: str, expression_is_error: bool, description_field: str) -> Condition:
        """
        Finds rows in 'table' based on a list of expressions defined in another table. The expression table can be filtered to a subset of expressions relevant for the verified table.
        """
        
        result = Condition("QaConstraintsListFactory")
        result.parameters.append(Parameter("table", table))
        result.parameters.append(Parameter("constraintsTable", constraints_table))
        result.parameters.append(Parameter("expressionField", expression_field))
        result.parameters.append(Parameter("expressionIsError", expression_is_error))
        result.parameters.append(Parameter("descriptionField", description_field))
        result.generate_name()
        return result

    @classmethod
    def qa_dangle_factory(cls, polyline_classes: List[BaseDataset]) -> Condition:
        """
        Finds all start\/end points in 'polylineClasses' that connect to no other start\/end point
        Remark: The feature classes in 'polylineClasses' must have the same spatial reference
        """
        
        result = Condition("QaDangleFactory")
        if type(polyline_classes) == list:
            for element in polyline_classes:
                result.parameters.append(Parameter("polylineClasses", element))
        elif polyline_classes is not None:
            result.parameters.append(Parameter("polylineClasses", polyline_classes))
        result.generate_name()
        return result

    @classmethod
    def qa_dataset_constraint_factory(cls, table: BaseDataset, constraint: List[str]) -> Condition:
        """
        Finds all rows in 'table' that do not fulfill the constraints
        """
        
        result = Condition("QaDatasetConstraintFactory")
        result.parameters.append(Parameter("table", table))
        if type(constraint) == list:
            for element in constraint:
                result.parameters.append(Parameter("constraint", element))
        elif constraint is not None:
            result.parameters.append(Parameter("constraint", constraint))
        result.generate_name()
        return result

    @classmethod
    def qa_gdb_constraint_factory(cls, table: BaseDataset, allow_null_values_for_coded_value_domains: bool = True, allow_null_values_for_range_domains: bool = True, fields: List[str] = None) -> Condition:
        """
        Finds all rows in 'table' that do not fulfill the attribute rules that are defined in the geodatabase
        """
        
        result = Condition("QaGdbConstraintFactory")
        result.parameters.append(Parameter("table", table))
        result.parameters.append(Parameter("AllowNullValuesForCodedValueDomains", allow_null_values_for_coded_value_domains))
        result.parameters.append(Parameter("AllowNullValuesForRangeDomains", allow_null_values_for_range_domains))
        if type(fields) == list:
            for element in fields:
                result.parameters.append(Parameter("Fields", element))
        elif fields is not None:
            result.parameters.append(Parameter("Fields", fields))
        result.generate_name()
        return result

    @classmethod
    def qa_line_connection(cls, feature_classes: List[BaseDataset], rules: List[str]) -> Condition:
        """
        Finds all connected features in 'featureClasses' that do not correspond with the 'rules'.
        'featureClasses' can consist of line and point featureclasses. 'rules' are checked at all distinct points that exist as start\/endpoint (line featureclasses) or points (point featureclasses).
        Remark: the feature classes in 'featureClasses' must have the same spatial reference. 
        The rules are processed in ordered direction. 
        If the involved features correspond to no rule, they are reported.
        
        One rule consists out of one expression for each featureClass.
        Each expression is either null or has a selection expression.
        Additionally, a expression can have variable declarations separated by ";". 
        Optionally, one expression of a rule can have count condition (separeted by ";"), where the declared variables can be checked. 
        
        A selection expression is a constraint on the corresponding featureclass (Example: "ObjektArt IN (x,y)"). If any feature connected at a point does not fulfill the selection expression for the corresponding featureclass, the corresponding rule is considered invalid and the next rules are checked for validity.
        
        A variable expression is formatted "<variablename>:<count expression>" (Example: "v1:Objektart=r"). The value of the variable is equal the count of the features at a point that fulfill the <count expression> (for the corresponding feature Class).
        For polyline featureclasses, an additional attribute "_StartsIn" is available in the count expression. The attribute value is true, if the FromPoint of the polyline lies at the point, and false, if the ToPoint lies at the point. Remark: If the FromPoint and ToPoint of a polyline are coincident, the polyline corresponds to two features in that point, one with _StartsIn=true and one with _StartsIn=false.  
        
        A count expression checks if the variables fulfill a condition (Example: "v1 =1 AND v2=1", where v1, v2 are declared variables). If the count expression is false, the corresponding rule is considered invalid and the next rules are checked for validity. A count expression can \/should use all variables declared in any expression of the corresponding rule. If a variable is not use in the count expression, the variable can be ommitted.
        
        Example:
        featureClasses: A, B
        rules:
        {
          { "ObjektArt IN (x,y)", "ObjektArt IN (u,v)" }, 
              \/\/ Meaning: all involved features belong either to A with ObjektArt in (x,y) or to B with ObjektArt in (u,v)
        
          { "ObjektArt = z", null },
             \/\/ Meaning: No B-Feature must touch any A-Feature with ObjektArt = z
        
          { null, "ObjektArt = t" },
             \/\/ Meaning: no A-Feature must touch any B-Feature with ObjektArt = t
        
          { "true;v1:ObjektArt=r;v2:Objektart=s;", "ObjektArt in (u,v);v1 =1 AND v2=1" }
             \/\/ Meaning: all feature of A and the features of B in (u,v) can be involved. Additionally, the count of A.ObjektArt =r must be 1 and the count of A.ObjektArt=s must be 1
        }
        """
        
        result = Condition("QaLineConnection")
        if type(feature_classes) == list:
            for element in feature_classes:
                result.parameters.append(Parameter("featureClasses", element))
        elif feature_classes is not None:
            result.parameters.append(Parameter("featureClasses", feature_classes))
        if type(rules) == list:
            for element in rules:
                result.parameters.append(Parameter("rules", element))
        elif rules is not None:
            result.parameters.append(Parameter("rules", rules))
        result.generate_name()
        return result

    @classmethod
    def qa_rel_constraint(cls, relation_tables: List[BaseDataset], relation: str, join: JoinType, constraint: List[str], apply_filter_expressions_in_database: bool = False) -> Condition:
        """
        Finds all rows in the joined table that do not fulfill 'constraint'
        """
        
        result = Condition("QaRelConstraint")
        if type(relation_tables) == list:
            for element in relation_tables:
                result.parameters.append(Parameter("relationTables", element))
        elif relation_tables is not None:
            result.parameters.append(Parameter("relationTables", relation_tables))
        result.parameters.append(Parameter("relation", relation))
        result.parameters.append(Parameter("join", join))
        if type(constraint) == list:
            for element in constraint:
                result.parameters.append(Parameter("constraint", element))
        elif constraint is not None:
            result.parameters.append(Parameter("constraint", constraint))
        result.parameters.append(Parameter("ApplyFilterExpressionsInDatabase", apply_filter_expressions_in_database))
        result.generate_name()
        return result

    @classmethod
    def qa_rel_group_connected(cls, relation_tables: List[BaseDataset], relation: str, join: JoinType, group_by: List[str], allowed_shape: ShapeAllowed, report_individual_gaps: bool = False, ignore_gaps_longer_than: float = -1, complete_groups_outside_test_area: bool = False, error_reporting: GroupErrorReporting = 1) -> Condition:
        """
        Find errors in checking if polylines of a joined table with same attributes are connected
        """
        
        result = Condition("QaRelGroupConnected")
        if type(relation_tables) == list:
            for element in relation_tables:
                result.parameters.append(Parameter("relationTables", element))
        elif relation_tables is not None:
            result.parameters.append(Parameter("relationTables", relation_tables))
        result.parameters.append(Parameter("relation", relation))
        result.parameters.append(Parameter("join", join))
        if type(group_by) == list:
            for element in group_by:
                result.parameters.append(Parameter("groupBy", element))
        elif group_by is not None:
            result.parameters.append(Parameter("groupBy", group_by))
        result.parameters.append(Parameter("allowedShape", allowed_shape))
        result.parameters.append(Parameter("ReportIndividualGaps", report_individual_gaps))
        result.parameters.append(Parameter("IgnoreGapsLongerThan", ignore_gaps_longer_than))
        result.parameters.append(Parameter("CompleteGroupsOutsideTestArea", complete_groups_outside_test_area))
        result.parameters.append(Parameter("ErrorReporting", error_reporting))
        result.generate_name()
        return result

    @classmethod
    def qa_rel_group_constraints(cls, relation_tables: List[BaseDataset], relation: str, join: JoinType, group_by_expression: str, distinct_expression: str, max_distinct_count: int, limit_to_tested_rows: bool, exists_row_group_filter: str = None) -> Condition:
        """
        Checks if the number of distinct values of an expression (which may be a single field or a more complex expression involving field concatenation, value translation, substring extraction etc.) within groups defined by a 'group by' expression (which also may be a single field or a more complex expression on fields) does not exceed an allowed maximum value. The expressions are evaluated in a joined view of two tables.
        """
        
        result = Condition("QaRelGroupConstraints")
        if type(relation_tables) == list:
            for element in relation_tables:
                result.parameters.append(Parameter("relationTables", element))
        elif relation_tables is not None:
            result.parameters.append(Parameter("relationTables", relation_tables))
        result.parameters.append(Parameter("relation", relation))
        result.parameters.append(Parameter("join", join))
        result.parameters.append(Parameter("groupByExpression", group_by_expression))
        result.parameters.append(Parameter("distinctExpression", distinct_expression))
        result.parameters.append(Parameter("maxDistinctCount", max_distinct_count))
        result.parameters.append(Parameter("limitToTestedRows", limit_to_tested_rows))
        result.parameters.append(Parameter("ExistsRowGroupFilter", exists_row_group_filter))
        result.generate_name()
        return result

    @classmethod
    def qa_rel_line_group_constraints(cls, relation_tables: List[BaseDataset], relation: str, join: JoinType, min_gap: float, min_group_length: float, min_dangle_length: float, group_by: str, group_condition: str = None, value_separator: str = None, min_gap_to_other_group_type: float = 0, min_dangle_length_continued: float = 0, min_dangle_length_at_fork_continued: float = 0, min_dangle_length_at_fork: float = 0, min_gap_to_same_group_type_covered: float = 0, min_gap_to_same_group_type_at_fork: float = 0, min_gap_to_same_group_type_at_fork_covered: float = 0, min_gap_to_other_group_type_at_fork: float = 0, min_gap_to_same_group: float = 0) -> Condition:
        """
        Find errors in checking if connected polylines of a joined table with same attributes related to 'groupBy' meet the conditions defined by the parameters
        """
        
        result = Condition("QaRelLineGroupConstraints")
        if type(relation_tables) == list:
            for element in relation_tables:
                result.parameters.append(Parameter("relationTables", element))
        elif relation_tables is not None:
            result.parameters.append(Parameter("relationTables", relation_tables))
        result.parameters.append(Parameter("relation", relation))
        result.parameters.append(Parameter("join", join))
        result.parameters.append(Parameter("minGap", min_gap))
        result.parameters.append(Parameter("minGroupLength", min_group_length))
        result.parameters.append(Parameter("minDangleLength", min_dangle_length))
        result.parameters.append(Parameter("groupBy", group_by))
        result.parameters.append(Parameter("GroupCondition", group_condition))
        result.parameters.append(Parameter("ValueSeparator", value_separator))
        result.parameters.append(Parameter("MinGapToOtherGroupType", min_gap_to_other_group_type))
        result.parameters.append(Parameter("MinDangleLengthContinued", min_dangle_length_continued))
        result.parameters.append(Parameter("MinDangleLengthAtForkContinued", min_dangle_length_at_fork_continued))
        result.parameters.append(Parameter("MinDangleLengthAtFork", min_dangle_length_at_fork))
        result.parameters.append(Parameter("MinGapToSameGroupTypeCovered", min_gap_to_same_group_type_covered))
        result.parameters.append(Parameter("MinGapToSameGroupTypeAtFork", min_gap_to_same_group_type_at_fork))
        result.parameters.append(Parameter("MinGapToSameGroupTypeAtForkCovered", min_gap_to_same_group_type_at_fork_covered))
        result.parameters.append(Parameter("MinGapToOtherGroupTypeAtFork", min_gap_to_other_group_type_at_fork))
        result.parameters.append(Parameter("MinGapToSameGroup", min_gap_to_same_group))
        result.generate_name()
        return result

    @classmethod
    def qa_rel_must_be_near_other(cls, relation_tables: List[BaseDataset], relation: str, join: JoinType, near_classes: List[BaseDataset], maximum_distance: float, relevant_relation_condition: str, error_distance_format: str = None) -> Condition:
        """
        Finds all features in a joined table that are not closer than 'maximumDistance' to any feature of 'nearClasses', or for which nearby features in 'nearClasses' do exist, but a given comparison constraint is not fulfilled.
        Note that errors can be reported only for features that are completely within the verified extent. Features that extend beyond the verified extent may have valid neighbors outside of the searched extent, and are therefore ignored.
        """
        
        result = Condition("QaRelMustBeNearOther")
        if type(relation_tables) == list:
            for element in relation_tables:
                result.parameters.append(Parameter("relationTables", element))
        elif relation_tables is not None:
            result.parameters.append(Parameter("relationTables", relation_tables))
        result.parameters.append(Parameter("relation", relation))
        result.parameters.append(Parameter("join", join))
        if type(near_classes) == list:
            for element in near_classes:
                result.parameters.append(Parameter("nearClasses", element))
        elif near_classes is not None:
            result.parameters.append(Parameter("nearClasses", near_classes))
        result.parameters.append(Parameter("maximumDistance", maximum_distance))
        result.parameters.append(Parameter("relevantRelationCondition", relevant_relation_condition))
        result.parameters.append(Parameter("ErrorDistanceFormat", error_distance_format))
        result.generate_name()
        return result

    @classmethod
    def qa_rel_regular_expression(cls, relation_tables: List[BaseDataset], relation: str, join: JoinType, pattern: str, field_names: List[str], match_is_error: bool = False, pattern_description: str = None) -> Condition:
        """
        Finds all rows in the joined table that do not fulfill 'constraint'
        """
        
        result = Condition("QaRelRegularExpression")
        if type(relation_tables) == list:
            for element in relation_tables:
                result.parameters.append(Parameter("relationTables", element))
        elif relation_tables is not None:
            result.parameters.append(Parameter("relationTables", relation_tables))
        result.parameters.append(Parameter("relation", relation))
        result.parameters.append(Parameter("join", join))
        result.parameters.append(Parameter("pattern", pattern))
        if type(field_names) == list:
            for element in field_names:
                result.parameters.append(Parameter("fieldNames", element))
        elif field_names is not None:
            result.parameters.append(Parameter("fieldNames", field_names))
        result.parameters.append(Parameter("MatchIsError", match_is_error))
        result.parameters.append(Parameter("PatternDescription", pattern_description))
        result.generate_name()
        return result

    @classmethod
    def qa_rel_unique(cls, relation_tables: List[BaseDataset], relation: str, join: JoinType, unique: str, max_rows: int) -> Condition:
        """
        Find all none unique rows in a joined table
        """
        
        result = Condition("QaRelUnique")
        if type(relation_tables) == list:
            for element in relation_tables:
                result.parameters.append(Parameter("relationTables", element))
        elif relation_tables is not None:
            result.parameters.append(Parameter("relationTables", relation_tables))
        result.parameters.append(Parameter("relation", relation))
        result.parameters.append(Parameter("join", join))
        result.parameters.append(Parameter("unique", unique))
        result.parameters.append(Parameter("maxRows", max_rows))
        result.generate_name()
        return result

    @classmethod
    def qa_topo_not_near_poly_factory(cls, feature_class: BaseDataset, reference: BaseDataset, reference_subtypes: List[int], featuresubtype_rules: List[str]) -> Condition:
        """
        Find features of 'featureClass' that intersect 'reference' when buffered according to 'featuresubtypeRules'.
        
        Remark: For line ends that are not coincident to any other line end (=dangles), a flat end buffer is used.
        
        Remark: The configuration can be exported\/imported to\/from a csv-File for easier configuration.
        if <referenceSubtypes> and <featuresubtypeRules> are empty, a matrix with all available subtypes is created when exporting the quality condition.
        """
        
        result = Condition("QaTopoNotNearPolyFactory")
        result.parameters.append(Parameter("featureClass", feature_class))
        result.parameters.append(Parameter("reference", reference))
        if type(reference_subtypes) == list:
            for element in reference_subtypes:
                result.parameters.append(Parameter("referenceSubtypes", element))
        elif reference_subtypes is not None:
            result.parameters.append(Parameter("referenceSubtypes", reference_subtypes))
        if type(featuresubtype_rules) == list:
            for element in featuresubtype_rules:
                result.parameters.append(Parameter("featuresubtypeRules", element))
        elif featuresubtype_rules is not None:
            result.parameters.append(Parameter("featuresubtypeRules", featuresubtype_rules))
        result.generate_name()
        return result
