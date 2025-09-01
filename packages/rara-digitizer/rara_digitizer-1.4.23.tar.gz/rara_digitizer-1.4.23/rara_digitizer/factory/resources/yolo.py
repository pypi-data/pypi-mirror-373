import pathlib

import environs

from rara_digitizer.factory.resources.base import Resource
from rara_digitizer.illustration_detector.yolo import YOLOImageDetector as YOLO
from rara_digitizer.utils.download import download_model

env = environs.Env()
RESOURCE_URI = env.str(
    "DIGITIZER_YOLO_MODELS_RESOURCE",
    default="https://packages.texta.ee/texta-resources/rara_models/yolo/",
)
MODELS = env.str("DIGITIZER_YOLO_MODELS", default="yolov10b-doclaynet.pt")


class YOLOImageDetector(Resource):
    unique_key = "yolo-detector"
    resource_uri = RESOURCE_URI
    location_dir = "yolo"
    models = [MODELS]
    default_model = MODELS

    def __init__(self, base_directory: str, **kwargs):
        self.base_directory = pathlib.Path(base_directory)

    def download_resource(self):
        folder_path = self.base_directory / self.location_dir
        folder_path.mkdir(parents=True, exist_ok=True)

        download_model(self.models, folder_path, self.resource_uri)

    def initialize_resource(self):
        pass

    def get_resource(self, **kwargs):
        path = (
            pathlib.Path(self.base_directory) / self.location_dir / self.default_model
        )
        detector = YOLO(str(path))
        return detector
