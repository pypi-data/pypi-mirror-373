from dataclasses import dataclass, field
import inspect
from typing import Callable, ClassVar
from types import UnionType


def type_to_str(annotation) -> str:
    """
    Transforms annotation given as `types` to strings.

    Args:
        annotation: The typing annotation.

    Returns:
        Annotation as string.
    """
    if annotation is not inspect.Parameter.empty:
        if isinstance(annotation, UnionType):
            return repr(annotation)
        else:
            return annotation.__name__
    else:
        return "undefined"


@dataclass
class Parameter:
    name: str
    type: str
    default: str

    @staticmethod
    def from_signature_parameter(p: inspect.Parameter):
        param = Parameter(
            name=p.name,
            type=type_to_str(p.annotation),
            default=p.default if p.default is not inspect.Parameter.empty else "undefined",
        )
        return param

    def has_default(self):
        return self.default != "undefined"

    def to_dict(self):
        return {"name": self.name, "type": self.type, "default": self.default}

    @staticmethod
    def from_dict(d: dict):
        if "name" not in d:
            raise AttributeError("required field 'name' not in dict")

        param = Parameter(
            name=d["name"],
            type=d["type"] if "type" in d else "undefined",
            default=d["default"] if "default" in d else "undefined",
        )
        return param


@dataclass
class Capability:
    name: str
    flavor: ClassVar[str] = "undefined"

    def to_dict(self):
        return {"name": self.name, "flavor": self.flavor}

    @staticmethod
    def from_dict(d: dict):
        if "name" not in d:
            raise AttributeError("required field 'name' not in dict")
        if "flavor" not in d:
            raise AttributeError("required field 'flavor' not in dict")

        if d["flavor"] == "attribute":
            return AttributeCapability.from_dict(d)
        elif d["flavor"] == "method":
            return MethodCapability.from_dict(d)
        elif d["flavor"] == "event":
            return EventCapability.from_dict(d)
        else:
            return None


@dataclass
class AttributeCapability(Capability):
    """
    An attribute capability describes a single variable of the remote object.
    It is exposed under the name of the capability.

    Args:
        name: name of the capability
        type: data type. E.g. "str", "int", "float", "list", ...
        access: Read and/or write access. "r" for read, "w" for write, and "rw" for both
    """

    flavor: ClassVar[str] = "attribute"
    type: str
    access: str = "rw"

    def to_dict(self) -> dict:
        d = Capability.to_dict(self)
        d.update({"type": self.type, "access": self.access})
        return d

    @staticmethod
    def from_dict(d: dict) -> "AttributeCapability":
        if "name" not in d:
            raise AttributeError("required field 'type' not in dict")
        return AttributeCapability(name=d["name"], type=d["type"], access=d["access"])


@dataclass
class EventCapability(Capability):
    """
    An event capability describes the ability of a remote object to notify upon a certain event.
    """

    flavor: ClassVar[str] = "event"

    @staticmethod
    def from_dict(d: dict) -> "EventCapability":
        return EventCapability(name=d["name"])


@dataclass
class MethodCapability(Capability):
    flavor: ClassVar[str] = "method"
    parameters: list[Parameter] = field(default_factory=list)
    return_type: str = "None"

    @staticmethod
    def from_method(m: Callable, name: str | None = None) -> "MethodCapability":
        if name is None:
            name = m.__name__
        sig = inspect.signature(m)

        cap = MethodCapability(name=name)
        cap.parameters = [Parameter.from_signature_parameter(sig.parameters[pname]) for pname in sig.parameters]
        if sig.return_annotation not in (inspect.Signature.empty, None):
            cap.return_type = type_to_str(sig.return_annotation)
        return cap

    def to_signature(self) -> inspect.Signature:
        parameters = [
            inspect.Parameter(
                p.name,
                inspect.Parameter.VAR_POSITIONAL if not p.has_default() else inspect.Parameter.KEYWORD_ONLY,
                default=p.default if p.has_default() else inspect.Parameter.empty,
                annotation=p.type if p.type != "undefined" else inspect.Parameter.empty,
            )
            for p in self.parameters
        ]
        return inspect.Signature(parameters=parameters, return_annotation=self.return_type)

    def to_dict(self) -> dict:
        d = Capability.to_dict(self)
        d.update({"parameters": [p.to_dict() for p in self.parameters], "return_type": self.return_type})
        return d

    @staticmethod
    def from_dict(d: dict) -> "MethodCapability":
        """
        Generate a method capabilities object from a defining dictionary.

        Args: definition of the capability according to the standard
        """
        if "parameters" not in d:
            raise AttributeError("required field 'parameters' not in dict")

        cap = MethodCapability(name=d["name"])
        cap.parameters = [Parameter.from_dict(par) for par in d["parameters"]]
        if "return_type" in d:
            cap.return_type = d["return_type"]

        return cap

    def call_dict(self, *args, **kwargs) -> dict:
        """
        This returns a dict that assigns the given parameter to the parameters of
        ourself. It takes care that positional and keyword arguments are handled correctly

        Args:
            *args: positional arguments
            **kwargs: keyword arguments

        Returns:
            dict: dict with parameter assignments
        """
        # TODO: type checking?

        # positional arguments
        d = {self.parameters[i].name: arg for i, arg in enumerate(args)}

        # keyword arguments
        parameter_names = [p.name for p in self.parameters]
        d.update({arg_name: value for arg_name, value in kwargs.items() if arg_name in parameter_names})

        return d
