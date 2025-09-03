from time import time as get_timestamp


def ensure_string(x):
    return x.decode() if isinstance(x, bytes) else str(x)


class DatasourceReturnValue(dict):
    """
    A structure to store data returned from a single entity in a datasource.
    A datasource can return multiple entities at once. In this case many DatasourceReturnValues are stored in
    a :class:`DatasourceReturnSet`.

    Default return values from datasource. They can be converted using a calibration.
     :param raw_value: (float)
     :param raw_unit: (str[10])
     :param time: (int) creation time of the rawValue.
    """

    @property
    def id(self):
        return self.get("id", None)

    @property
    def raw_value(self):
        return self.get("raw_value", None)

    @raw_value.setter
    def raw_value(self, value):
        self["raw_value"] = value

    @property
    def raw_unit(self):
        return self.get("raw_unit", None)

    @raw_unit.setter
    def raw_unit(self, value):
        self["raw_unit"] = value

    @property
    def value(self):
        """(float) value in specified units."""
        if self.get("calibrated"):
            return self.get("value", None)
        else:
            return self.get("raw_value", None)

    @value.setter
    def value(self, value):
        self["value"] = value

    @property
    def unit(self):
        """SI Unit of the current tuple."""
        if self.get("calibrated"):
            return self.get("unit", None)
        else:
            return self.get("raw_unit", None)

    @unit.setter
    def unit(self, value):
        self["unit"] = value

    @property
    def time(self):
        return self.get("time", 0)

    @property
    def inbound(self):
        """
        Boundary level (int) -1=unbound, 0=ok, 1=warn,error, fault
        """
        return self.get("inbound", -1)

    @inbound.setter
    def inbound(self, value):
        self["inbound"] = value

    def __init__(
        self,
        id: str = None,
        time: float = None,
        value: float = None,
        unit: str = None,
        raw_value: float = None,
        raw_unit: str = None,
        inbound: int = -1,
        calibrated: bool = False,
        **kwargs,
    ):
        kwargs.update(
            {
                "id": id,
                "value": value,
                "unit": ensure_string(unit),
                "inbound": inbound,
                "time": time if time is not None else get_timestamp(),
                "raw_value": raw_value,
                "raw_unit": ensure_string(raw_unit),
                "calibrated": calibrated,
            }
        )
        dict.__init__(self, **kwargs)

    def __str__(self):
        return "%.3f: %s %s (inbound=%i)" % (self.time, self.value, self.unit, self.inbound)

    def __repr__(self):
        return "DatasourceReturnValue(%s)" % (dict.__repr__(self))


class DatasourceReturnSet(tuple):
    """
    Collection of multiple :class:`DatasourceReturnValue`.
    """

    @staticmethod
    def from_data(data):
        """
        We try to build a DatasourceReturnSet by guessing the data format from the following options:
            * [FLOAT, FLOAT, ..] -> A list of raw_values
            * [(FLOAT, STR), (FLOAT, STR), ..] -> a list of (raw_value, raw_unit) tuples
            * {STR: FLOAT, STR: FLOAT, ..} -> a dict with id: raw_value
            * {STR: (FLOAT, STR), STR: (FLOAT, STR), ...} a dict with id: (raw_value, raw_unit)
            * FLOAT -> raw_value
            * (FLOAT, STR) -> (raw_value, raw_unit)
        """
        if isinstance(data, list):
            if all(
                [
                    (isinstance(d, list) or isinstance(d, tuple)) and len(d) == 2 and isinstance(d[0], float)
                    for d in data
                ]
            ):
                return DatasourceReturnSet(
                    [
                        DatasourceReturnValue(id=str(i), raw_value=value, raw_unit=unit)
                        for i, (value, unit) in enumerate(data)
                    ]
                )
            else:
                return DatasourceReturnSet(
                    [DatasourceReturnValue(id=str(i), raw_value=value) for i, value in enumerate(data)]
                )
        elif isinstance(data, dict):
            datatuple = []
            for id, d in data.items():
                if (isinstance(d, list) or isinstance(d, tuple)) and len(d) == 2:
                    datatuple.append(DatasourceReturnValue(id=id, raw_value=d[0], raw_unit=d[1]))
                else:
                    datatuple.append(DatasourceReturnValue(id=id, raw_value=d))
            return DatasourceReturnSet(datatuple)
        elif isinstance(data, tuple) and len(data) == 2:
            return DatasourceReturnSet([DatasourceReturnValue(id="0", raw_value=data[0], raw_unit=data[1])])
        else:
            return DatasourceReturnSet([DatasourceReturnValue(id="0", raw_value=data)])
