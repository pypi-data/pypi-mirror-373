import abc
import orjson
import pickle


# ==-----------------------------------------------------------------------------== #
# Abstract classes                                                                  #
# ==-----------------------------------------------------------------------------== #
class Serealizer(abc.ABC):

    @abc.abstractmethod
    def dumps(self, _: dict) -> bytes:
        """Serializes Python dict to bytestring."""

        pass

    def loads(self, _: bytes) -> dict:
        """Deserealizes bytestring to Python dict."""

        pass


# ==-----------------------------------------------------------------------------== #
# Classes                                                                           #
# ==-----------------------------------------------------------------------------== #
class SerealizationError(Exception):
    """Class representing errors occurred while serialization."""

    def __init__(self, value: dict) -> None:
        super().__init__("Failed to selealize data: %s" % value.__repr__())


class DeserealizationError(Exception):
    """Class representing errors occurred while deserialization."""

    def __init__(self, value: bytes) -> None:
        super().__init__("Failed to deserealize data: %s" % value.__repr__())


class OrjsonSerealizer(Serealizer):
    """Class of high-performance serealizer / deserealized, using `orjson` package to represent Python `dict` as json bytestring or vice versa."""

    def dumps(self, value: dict) -> bytes:
        """Serializes Python dict to json bytestring."""

        try:
            return orjson.dumps(value)

        except Exception:
            raise SerealizationError(value)

    def loads(self, value: bytes) -> dict:
        """Deserealizes json bytestring to Python dict."""

        try:
            return orjson.loads(value) if value else {}

        except Exception:
            raise DeserealizationError(value)


class PickleSerealizer(Serealizer):
    """Class of universal serealizer / deserealizer, using `pickle` package to represent Python `dict` as bytestring or vice versa."""

    def dumps(self, value: dict) -> bytes:
        """Serializes Python dict to bytestring."""

        try:
            return pickle.dumps(value, pickle.HIGHEST_PROTOCOL)

        except Exception:
            raise SerealizationError(value)

    def loads(self, value: bytes) -> dict:
        """Deserealizes bytestring to Python dict."""

        try:
            return pickle.loads(value) if value else {}

        except Exception:
            raise DeserealizationError(value)
