import pathlib

from rara_text_evaluator.quality_evaluator import QualityEvaluator as QE

from rara_digitizer.factory.resources.base import Resource


class QualityEvaluator(Resource):
    unique_key = "quality-evaluator"
    resource_uri = ""
    location_dir = ""
    models = [""]
    default_model = ""

    def __init__(self, base_directory: str, **kwargs):
        self.base_directory = pathlib.Path(base_directory)

    def download_resource(self):
        pass

    def initialize_resource(self):
        pass

    def get_resource(self, **kwargs):
        evaluator = QE(**kwargs)
        return evaluator
