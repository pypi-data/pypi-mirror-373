from abc import ABC, abstractmethod


class Resource(ABC):
    @classmethod
    @property
    @abstractmethod
    def unique_key(cls):
        """
        Used to identify the resources amongst a collection, both by the storage
        that handles the Resource objects and the cache that stores the resources (models etc) returned
        by this class.
        """
        raise NotImplementedError

    @classmethod
    @property
    @abstractmethod
    def resource_uri(cls):
        """
        What URI to download the resource from, keep empty if there is
        nothing to download
        """
        raise NotImplementedError

    @classmethod
    @property
    @abstractmethod
    def location_dir(cls):
        """Name of the folder the resource is stored at, generally used together with self.base_dir."""
        raise NotImplementedError

    @classmethod
    @property
    @abstractmethod
    def models(cls):
        """What models to expect from inside the downloaded resource (certain zips etc can have multiple)."""
        raise NotImplementedError

    @classmethod
    @property
    @abstractmethod
    def default_model(cls):
        """In case of multiple models, which one should be the default?"""
        raise NotImplementedError

    @abstractmethod
    def __init__(self, base_directory: str, **kwargs):
        raise NotImplementedError

    @abstractmethod
    def download_resource(self):
        """
        Process to make resource available to the user, doesn't specifically have to be
        a download but in this use case this is what happens every time.
        """
        raise NotImplementedError

    @abstractmethod
    def initialize_resource(self):
        """
        Certain resources may have set-up requirements like in the case of Tesseract which wants an env variable
        towards its models directory.
        """
        raise NotImplementedError

    @abstractmethod
    def get_resource(self, **kwargs):
        """Returns the resource specific to the class, could be a model, file etc"""
        raise NotImplementedError
