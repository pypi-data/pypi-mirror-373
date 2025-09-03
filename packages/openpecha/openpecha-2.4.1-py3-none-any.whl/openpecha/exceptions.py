class FileNotFoundError(Exception):
    """Raised when the specified file is not found."""

    pass


class EmptyFileError(Exception):
    """Raised when the specified file is empty."""

    pass


class MetaDataValidationError(Exception):
    """Raised when the metadata is not valid."""

    pass


class StamAddAnnotationError(Exception):
    """Raised when there is an error adding annotation in STAM."""

    pass


class ParseNotReadyForThisAnnotation(Exception):
    """Raised when the parser is not ready for this annotation."""

    pass


class InValidAnnotationLayerName(Exception):
    """Raised when the layer name is not associated with any Annotations"""

    pass
