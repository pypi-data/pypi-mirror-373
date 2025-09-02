from geodesic.bases import _APIObject
from geodesic.descriptors import (
    _IntDescr,
    _TypeConstrainedDescr,
    _StringDescr,
    _DatetimeIntervalDescr,
)

time_units = [
    "milliseconds",
    "seconds",
    "minutes",
    "hours",
    "days",
    "weeks",
    "months",
    "years",
    "decades",
    "centuries",
]


class TimeEnable(_APIObject):
    datetime_field = _StringDescr(doc="datetime field")
    start_datetime_field = _StringDescr(doc="start datetime field")
    end_datetime_field = _StringDescr(doc="end datetime field")
    track_id_field = _StringDescr(doc="track id field")
    time_extent = _DatetimeIntervalDescr(doc="time extent that the servicer covers", format="tuple")
    interval = _IntDescr(doc="interval of time for a notional time slider")
    interval_units = _StringDescr(doc="units of the interval", one_of=time_units)


class ServicerSettings(_APIObject):
    time_enable = _TypeConstrainedDescr(
        (TimeEnable, dict),
        doc="time enable settings primarily used for ArcGIS",
        coerce=True,
    )
