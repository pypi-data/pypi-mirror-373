from abc import ABC, abstractmethod


class PrefixBase(ABC):
    @staticmethod
    @abstractmethod
    def url_prefix() -> str:
        """Common prefix URL."""
        pass

    @classmethod
    def resource_prefix(cls) -> str:
        """Common prefix for resource."""
        url_prefix = cls.url_prefix()
        if url_prefix.startswith('/'):
            return url_prefix[1:] + "-"
        else:
            raise NotImplementedError("Resource prefix cannot be taken from url_prefix")
