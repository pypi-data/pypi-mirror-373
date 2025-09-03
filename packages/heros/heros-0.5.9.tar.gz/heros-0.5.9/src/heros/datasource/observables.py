from .types import DatasourceReturnValue
from typing import Optional


def lambdify(expression: str, globals_dict: dict | None = None):
    """
    Turn a string into a lambda function with the given globals.
    By default it enables a set of numpy functions in the expression. Further functions can be added by providing
    it in ``globals_dict``.
    """
    import numpy as np

    globals_dict = {} if globals_dict is None else globals_dict
    np_functions = [
        "sin",
        "cos",
        "tan",
        "arcsin",
        "arccos",
        "arctan",
        "hypot",
        "arctan2",
        "sinh",
        "cosh",
        "tanh",
        "arcsinh",
        "arccosh",
        "exp",
        "exp2",
        "log",
        "log10",
        "log2",
        "log1p",
        "logaddexp",
        "logaddexp2",
        "i0",
        "sinc",
        "power",
        "sqrt",
    ]
    glob = {key: value for key, value in np.__dict__.items() if key in np_functions}
    glob.update(globals_dict)
    try:
        return eval("lambda x:" + expression, glob)
    except Exception:
        return None


class BoundaryChecker:
    """
    Check whether the observed value is in it's boundaries.
    Therefore provide an integer feedback with rising importance where boundary = 0 says that everything is fine.
    1, 2, 3 correspond to higher warning / error or fault situations.

    """

    def __init__(self, boundaries: list):
        self.boundaries = boundaries

    def _check_bounds(self, value):
        try:
            for i, (lower, upper) in enumerate(self.boundaries):
                if value >= lower and value <= upper:
                    return i
        except Exception:
            pass

        return len(self.boundaries)

    def __call__(self, return_value: DatasourceReturnValue):
        # Do the actual boundary check here...
        if len(self.boundaries) > 0:
            return_value.inbound = self._check_bounds(return_value.value)
        return return_value


class Converter:
    def __init__(self, conversion_code: str, unit: Optional[str] = None):
        self._conversion_code = conversion_code
        self._convert_lambda = lambdify(conversion_code)
        self._unit = unit

    def __call__(self, return_value: DatasourceReturnValue):
        return_value.unit = self._unit if self._unit is not None else return_value.raw_unit
        if self._convert_lambda is not None:
            # Do the actual conversion here
            return_value.value = self._convert_lambda(return_value.raw_value)
            return_value["calibrated"] = True
        return return_value


class Observable:
    def __init__(self, id, definition: dict):
        self._id = id
        self.definition = definition
        self._boundary_checker = BoundaryChecker(definition.get("boundaries", []))
        self._converter = Converter(definition.get("conversion", None), definition.get("unit", None))

    @property
    def id(self):
        return self._id

    def process(self, return_value: DatasourceReturnValue):
        return self._boundary_checker(self._converter(return_value))


class ObservableProcessor:
    """
    An ObservableProcessor takes a configuration dict for multiple observables when it is instantiated.
    An object of this class can be called with a :class:DataSourceReturnSet as an argument.
    """

    def __init__(self, obs_def: dict):
        self.observables = [Observable(id, definition) for id, definition in obs_def.items()]
        self.observables_ids = [obs.id for obs in self.observables]

    def __call__(self, datasource_return_set):
        for return_value in datasource_return_set:
            if return_value.id not in self.observables_ids:
                continue

            obs = self.observables[self.observables_ids.index(return_value.id)]
            obs.process(return_value)

        return datasource_return_set
