from typing import Any

from rara_text_evaluator.quality_evaluator import QualityEvaluator
from transformers import ViTFeatureExtractor, ViTForImageClassification

from ..exceptions import DuplicateResourceKey, InvalidResourceKey
from ..factory.resources.base import Resource
from ..illustration_detector.yolo import YOLOImageDetector
from ..utils.load_class import load_class

DEFAULT_RESOURCES = [
    "rara_digitizer.factory.resources.yolo.YOLOImageDetector",
    "rara_digitizer.factory.resources.image_classificator.ImageClassifier",
    "rara_digitizer.factory.resources.image_classificator.ImageFeatureExtractor",
    "rara_digitizer.factory.resources.quality_evaluator.QualityEvaluator",
    "rara_digitizer.factory.resources.tesseract.TesseractModels",
]


class ResourceManager:

    def __init__(
            self,
            base_dir: str = "./models",
            resources: list[str | Any] = DEFAULT_RESOURCES,
            autodownload_true: bool = True,
            initialize_immediately: bool = True,
    ):
        """
        Helper class for handling various resources needed by different tools and components
        including download, setup and returning the object in question.

        Parameters
        ----------
        base_dir : str
            Path to the directory that holds all the resource files.

        resources : list[str | Resource]
            Either a list of a dot notated path to a class object or instances of a Resource subclass to initialize
            on creation.

        autodownload_true: bool
            Whether to start downloading the files for resources automatically when initializing the ResourceManager.

        initialize_immediately: bool
            Whether to load all the given resources into memory immediately after initialization, if set to false,
            resources need to be initialized through the self.initialize_resources or self.initialize_resource methods.
        """
        self.base_dir = base_dir
        self.autodownload_true = autodownload_true
        self.initialize_immediately = initialize_immediately
        self._resources = resources
        self.initialized_resources = {}
        self.resource_cache = {}

        if self.initialize_immediately:
            self.initialize_resources()

    def add_resource(self, resource: Resource) -> None:
        """
        Allows users to add custom resources during run-time whenever needed
        """
        self.initialize_resource(resource)

    def get_resource(self, key: str, **kwargs) -> Any:
        # Check the resource is initialized and available for use.
        resource: Resource | None = self.initialized_resources.get(key, None)
        if resource is None:
            raise InvalidResourceKey("Resource with given key doesn't exist!")

        # Create a new key along with stringified kwargs to support caching
        # multiple alternative models.
        resource_key = f"{key}_{str(kwargs)}"

        # Using the resource key, keep tabs of already initialized models etc
        # using the dict cache.

        if resource_key not in self.resource_cache:
            self.resource_cache[resource_key] = resource.get_resource(**kwargs)
        return self.resource_cache[resource_key]

    def initialize_resource(self, resource: Resource) -> None:
        if self.autodownload_true:
            resource.download_resource()

        resource.initialize_resource()

        if resource.unique_key not in self.initialized_resources:
            self.initialized_resources[resource.unique_key] = resource
        else:
            raise DuplicateResourceKey(
                "Resource with given key already exists, please ensure the keys are unique!"
            )

    def initialize_resources(self) -> None:
        for resource in self._resources:
            if isinstance(resource, str):
                resource: Resource = load_class(resource)(self.base_dir)

            self.initialize_resource(resource)

    # Helper functions to make access for specific resources cleaner inside
    # the tool classes. Another option would be to call out get_resource() directly
    # from the tool classes but this seemed prettier to do for now at least.
    def image_processor(self, **kwargs) -> YOLOImageDetector:
        return self.get_resource("yolo-detector", **kwargs)

    def image_classifier(self, **kwargs) -> ViTForImageClassification:
        return self.get_resource("image-classifier", **kwargs)

    def image_feature_extractor(self, **kwargs) -> ViTFeatureExtractor:
        return self.get_resource("image-feature-extractor", **kwargs)

    def quality_evaluator(self, **kwargs) -> QualityEvaluator:
        return self.get_resource("quality-evaluator", **kwargs)
