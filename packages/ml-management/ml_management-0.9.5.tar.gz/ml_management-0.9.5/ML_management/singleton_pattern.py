"""Module with singleton metaclass."""


class Singleton(type):
    """Metaclass for singleton classes."""

    _instances = {}

    def __call__(cls, *args, **kwargs):
        """Call on class instance creating."""
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]
