from contextvars import ContextVar

from planar.files.storage.base import Storage

storage_var: ContextVar[Storage] = ContextVar("storage")


def get_storage() -> Storage:
    """Get the current storage context."""
    return storage_var.get()


def set_storage(storage: Storage) -> None:
    """Set the current storage context."""
    storage_var.set(storage)
