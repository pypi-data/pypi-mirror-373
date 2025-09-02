from typing import Union

from prosuite.quality import Specification, XmlSpecification
from prosuite.verification import VerificationParameters, EnvelopePerimeter, EsriShapePerimeter, WkbPerimeter


# Note @PLU: AdvancedParameters is not loaded in __init__.py of verification because we want it to be private
#   There used to be a TODO to make this private. This is not possible in python, but we can remove it from the imports
#   in __init__.py so its not discoverable
class AdvancedParameters:
    def __init__(self, specification, output_dir, perimeter, verification_params: VerificationParameters = None) -> None:

        self.specification:  Union[Specification,
                                   XmlSpecification] = specification
        self.perimeter: Union[EnvelopePerimeter,
        EsriShapePerimeter, WkbPerimeter] = perimeter

        # Define all members with default values:
        self.output_dir: str = output_dir
        self.tile_size: int = 5000
        self.user_name: str = ''
        self.desired_parallel_processing = 0
        self.update_issues_in_verified_model = False
        self.save_verification_statistics = False
        self.report_culture_code = None

        if (verification_params):
            self.tile_size = verification_params.tile_size

            if verification_params.user_name:
                self.user_name = verification_params.user_name

            if (verification_params.report_culture_code):
                self.report_culture_code = verification_params.report_culture_code

            self.desired_parallel_processing = verification_params.desired_parallel_processing
            self.update_issues_in_verified_model = verification_params.update_issues_in_verified_model
            self.save_verification_statistics = verification_params.save_verification_statistics
