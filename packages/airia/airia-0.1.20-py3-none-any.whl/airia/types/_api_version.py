from enum import Enum


class ApiVersion(Enum):
    """Enum for API Versions."""

    V1 = "v1"
    V2 = "v2"

    @classmethod
    def as_list(cls):
        """Return a list of all API Version values."""
        return [version.value for version in cls]
