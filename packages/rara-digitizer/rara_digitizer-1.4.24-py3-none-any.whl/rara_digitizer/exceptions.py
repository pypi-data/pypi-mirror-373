class MultipleMETSFilesFound(Exception):
    pass


class NoMETSFileFound(Exception):
    pass


class PathNotFound(Exception):
    pass


class NotLoadedOrEmpty(Exception):
    pass


class UnsupportedFile(Exception):
    pass


class FileTypeOrStructureMismatch(Exception):
    pass


class PageOutOfRange(Exception):
    pass


class ConversionFailed(Exception):
    pass


class DuplicateResourceKey(Exception):
    pass


class InvalidResourceKey(Exception):
    pass
