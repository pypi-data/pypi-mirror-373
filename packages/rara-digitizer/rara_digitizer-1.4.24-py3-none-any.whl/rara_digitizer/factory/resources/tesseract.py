import os
import pathlib
import environs


from rara_digitizer.factory.resources.base import Resource
from rara_digitizer.utils.download import download_model

env = environs.Env()
RESOURCE = env.str(
    "DIGITIZER_TESSERACT_MODELS_RESOURCE",
    default="https://packages.texta.ee/texta-resources/rara_models/tesseract/",
)
MODELS = env.list(
    "DIGITIZER_TESSERACT_MODELS",
    default=[
        "Cyrillic.traineddata",
        "Latin.traineddata",
        "eng.traineddata",
        "est_frak.traineddata",
        "osd.traineddata",
    ],
)


class TesseractModels(Resource):
    unique_key = "tesseract"
    resource_uri = RESOURCE
    location_dir = "tesseract"
    models = MODELS
    default_model = ""

    def __init__(self, base_directory: str, **kwargs):
        self.base_directory = pathlib.Path(base_directory)

    def download_resource(self):
        folder_path = self.base_directory / self.location_dir
        folder_path.mkdir(parents=True, exist_ok=True)

        download_model(self.models, folder_path, self.resource_uri)

    def initialize_resource(self):
        ### SET TESSERACT DATA DIR
        os.environ["TESSDATA_PREFIX"] = str(self.base_directory / self.location_dir)

    def get_resource(self, **kwargs):
        pass
