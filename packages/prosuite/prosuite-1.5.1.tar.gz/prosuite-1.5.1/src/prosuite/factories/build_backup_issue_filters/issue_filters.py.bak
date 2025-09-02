__author__ = "The ProSuite Authors"
__copyright__ = "Copyright 2021-2025, The ProSuite Authors"
__license__ = "MIT"
__version__ = "1.5.0.2"
__maintainer__ = "Dira GeoSystems"
__email__ = "programmers@dirageosystems.ch"
__date__  = "17.06.2025"
__status__ = "Production"


from datetime import datetime
from typing import List
from prosuite.quality import Parameter
from prosuite.quality import IssueFilter
from prosuite.data_model import BaseDataset
from prosuite.factories.enums import *

class IssueFilters:

    @classmethod
    def if_all_0(cls, filter: bool = True) -> IssueFilter:
        """
        Filters all issues, if 'Filter' = true (default). If 'Filter' = false, no issue is filtered
        """
        
        result = IssueFilter("IfAll(0)")
        result.parameters.append(Parameter("Filter", filter))
        result.generate_name()
        return result

    @classmethod
    def if_intersecting_0(cls, feature_class: BaseDataset) -> IssueFilter:
        """
        Filters issues that intersect any feature in a 'featureClass'
        """
        
        result = IssueFilter("IfIntersecting(0)")
        result.parameters.append(Parameter("featureClass", feature_class))
        result.generate_name()
        return result

    @classmethod
    def if_involved_rows_0(cls, constraint: str, tables: List[BaseDataset] = None) -> IssueFilter:
        """
        Filters issues where any involved row fulfills 'constraint'
        """
        
        result = IssueFilter("IfInvolvedRows(0)")
        result.parameters.append(Parameter("constraint", constraint))
        if type(tables) == list:
            for element in tables:
                result.parameters.append(Parameter("Tables", element))
        elif tables is not None:
            result.parameters.append(Parameter("Tables", tables))
        result.generate_name()
        return result

    @classmethod
    def if_near_0(cls, feature_class: BaseDataset, near: float) -> IssueFilter:
        """
        Filters issues that are completely near any feature of 'featureClass'
        """
        
        result = IssueFilter("IfNear(0)")
        result.parameters.append(Parameter("featureClass", feature_class))
        result.parameters.append(Parameter("near", near))
        result.generate_name()
        return result

    @classmethod
    def if_within_0(cls, feature_class: BaseDataset) -> IssueFilter:
        """
        Filters issues that are completely within any feature in a 'featureClass'
        """
        
        result = IssueFilter("IfWithin(0)")
        result.parameters.append(Parameter("featureClass", feature_class))
        result.generate_name()
        return result
