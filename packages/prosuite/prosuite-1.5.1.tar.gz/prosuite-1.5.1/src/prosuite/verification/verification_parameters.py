class VerificationParameters():
    """
    Contains all parameters that can be passed to a verification.
    """
    def __init__(self, tile_size: int = 5000, user_name: str = None) -> None:
        #:
        self.tile_size: int = tile_size
        """
        The size (in meter) for testing quality conditions.
        """
        #:
        self.user_name: str = user_name
        """
        The executing user which will be used in issue features.
        """
        #:
        self.desired_parallel_processing: int = 0
        """
        The desired number of parallel worker processes to be used if the server allows parallel processing.
        """
        #:
        self.update_issues_in_verified_model = False
        """
        If True, the issues will be updated in the error datasets of the verified model.
        """
        #:
        self.save_verification_statistics = False
        """
        If True, the verification statistics will be saved into the Data Dictionary database.
        """
        #:
        self.objects_to_verify = dict()
        """
        A dictionary containing the dataset IDs and the object IDs to be verified. The dataset ID can be looked up in the Data Dictionary Editor -> Data -> Data Models -> Dataset -> Properties.  Use the method add_objects_to_verify to add a list of IDs for a specific dataset.
        """
        #:
        self.report_culture_code = None
        """
        The culture code that determines the language of the report. If None, the culture code of the machine of the server will be used. 
        Examples: 'de-CH', 'de-DE', 'de-AT', 'en-GB'
        """

    def add_objects_to_verify(self, dataset_id: int, object_ids: list):
        """
        Adds a dataset and a list of object IDs to the objects to be verified.

        :param dataset_id: The dataset ID containing the selected datasets The id can be look up in the DataDictionaryEditor -> Data -> Data Models -> Dataset -> Properties.
        :type dataset_id: int
        :param object_ids: A list of feature-object IDs from the dataset to be verified.
        :type object_ids: list
        """
        self.objects_to_verify[dataset_id] = object_ids
