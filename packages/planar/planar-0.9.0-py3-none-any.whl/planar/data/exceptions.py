"""Exceptions for the Planar data module."""


class DataError(Exception):
    """Base exception for data-related errors."""

    pass


class DatasetNotFoundError(DataError):
    """Raised when a dataset is not found."""

    pass


class DatasetAlreadyExistsError(DataError):
    """Raised when trying to create a dataset that already exists."""

    pass
