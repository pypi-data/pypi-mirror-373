import pathlib

import environs
from transformers import ViTForImageClassification, ViTFeatureExtractor

from rara_digitizer.factory.resources.base import Resource
from rara_digitizer.utils.download import download_model

env = environs.Env()
RESOURCE_URI = env.str(
    "DIGITIZER_IMG_CLF_MODELS_RESOURCE",
    default="https://packages.texta.ee/texta-resources/rara_models/image_classifier/",
)
MODELS = env.str("DIGITIZER_IMG_CLF_MODELS	", default="image_classifier.zip")
FEATURE_EXTRACTOR_CONFIG = env.str(
    "DIGITIZER_IMG_CLF_PREPROCESS_CONFIGS", default="vit_preprocessor_config.json"
)


class ImageClassifier(Resource):
    unique_key = "image-classifier"
    resource_uri = RESOURCE_URI
    location_dir = "image_classifier"
    models = [MODELS]
    default_model = ""

    def __init__(self, base_directory: str, **kwargs):
        self.base_directory = pathlib.Path(base_directory)

    def download_resource(self):
        folder_path = self.base_directory / self.location_dir
        folder_path.mkdir(parents=True, exist_ok=True)

        download_model(self.models, folder_path, self.resource_uri)

    def initialize_resource(self):
        pass

    def get_resource(self, **kwargs):
        custom_model_path = kwargs.get("path", None)

        custom_model_path = pathlib.Path(custom_model_path) / "model" if custom_model_path else None
        default_path = pathlib.Path(self.base_directory) / self.location_dir / "image_classifier"

        set_path = custom_model_path or default_path
        detector = ViTForImageClassification.from_pretrained(str(set_path))
        return detector


class ImageFeatureExtractor(Resource):
    unique_key = "image-feature-extractor"
    resource_uri = RESOURCE_URI
    location_dir = "image_classifier"
    models = [MODELS]
    default_model = ""

    def __init__(self, base_directory: str, **kwargs):
        self.base_directory = pathlib.Path(base_directory)

    def download_resource(self):
        folder_path = self.base_directory / self.location_dir
        folder_path.mkdir(parents=True, exist_ok=True)

        download_model(self.models, folder_path, self.resource_uri)

    def initialize_resource(self):
        pass

    def get_resource(self, **kwargs):
        custom_model_path = kwargs.get("path", None)

        if custom_model_path:
            custom_model_path = pathlib.Path(custom_model_path) / "components" / "image_processor" / "preprocessor_config.json"

        default_path = pathlib.Path(self.base_directory) / self.location_dir / FEATURE_EXTRACTOR_CONFIG

        set_path = custom_model_path or default_path
        detector = ViTFeatureExtractor.from_pretrained(str(set_path))
        return detector
