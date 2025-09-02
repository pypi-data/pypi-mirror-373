"""Descriptor objects we will use to compose the basic classes.

that inherit from :class:`geodesic.bases.APIObject`. They follow the
pattern <Name>Descr. Rather than simply being namespaced here, the Descr
suffix will allow them to be aligned with other objects that will be
implemented as descriptors, such as AssetSpec and Project, and such.
These, by necessity need to be implemented in separate packages and
this convention will keep things internally consistent.


These descriptors are not meant for users as they are just something internal to Geodesic objects.
Users can take advantage of the validation in them if needed, but in general this will all be taken
care of by the Geodesic objects. Each descriptor inherits from :class:`_BaseDescr` which provides
the standard `__get__()` and `__set__()` functionality. In `__set__()` it also calls a validation
function which is defined on the subclass. This allows at-set validation of things like types,
regex, or anything else needed by the subclass.

When documenting descriptors make sure always include a link to the current descriptor as the
first line of the docstring. This will allow the docs to propagate correctly to classes where the
descriptor is used.
"""

import datetime
import re
import warnings
from typing import Union
from urllib.parse import urlparse
import numpy as np
import pytz
from shapely.geometry import shape, box
from shapely.geometry.base import BaseGeometry
from shapely.wkb import loads as loads_wkb
from shapely.wkt import loads as loads_wkt
from dateutil.parser import parse
from dateutil.relativedelta import relativedelta

from geodesic.utils import datetime_to_utc
from geodesic.bases import _APIObject


class _BaseDescr:
    """base functionality of Descriptor objects for use with APIObject.

    BaseDescr adds the basic functionality we use such as the attribute name and the private_name,
    which is prefixed by an "_".

    Args:
        nested: a subfield in the object's dict to retrieve this out of. A json path,
            separated by '.'.  only object paths are supported, not full JSON paths such as list
            indices or wildcards
        doc: a custom docstring to override the default field descriptor docstring.
        default: a default value for this field
        dict_name: if the attribute name needs to be different than the name in the dictionary, it
            can be set with this. (example: `object_class` -> `class` since `class` is a
            reserved word)
        deprecated: If this field deprecated, will raise a DeprecationWarning
        optional: If True, this field is allowed to be None.
    """

    def __init__(
        self,
        nested: str = None,
        doc: str = None,
        default=None,
        dict_name=None,
        deprecated=False,
        optional=False,
    ):
        if nested is not None:
            self.nested = nested.split(".")
        else:
            self.nested = None
        self.doc = doc
        self.default = default
        self.dict_name = dict_name
        self.deprecated = deprecated
        self.optional = optional

    def __set_name__(self, owner: object, name: str):
        self.public_name = name
        self.private_name = "_" + name
        if self.dict_name is None:
            self.dict_name = self.public_name
        if self.doc is not None:
            attr = getattr(owner, name)

            new_doc = self.doc
            doc = getattr(attr, "__doc__")
            doc_link = (
                f":class:`{self.__class__.__name__}<{self.__module__}.{self.__class__.__name__}>`"
            )
            types_strings = []
            if hasattr(self, "_type"):
                for x in self._type:
                    if x is None:
                        continue
                    if x.__module__ == "builtins":
                        types_strings.append(f"{x.__name__}")
                    else:
                        types_strings.append(f":class:`{x.__name__}<{x.__module__}.{x.__name__}>`")

            accepted_types = f"{', '.join(types_strings)}"
            if doc is not None:
                new_doc = (
                    f"({accepted_types}) - {new_doc}" if accepted_types != "" else f"{new_doc}"
                )
                new_doc += "\n\n**Descriptor**:\n" + doc_link

            setattr(attr, "__doc__", new_doc)

    def __get__(self, obj: object, objtype=None) -> object:
        if obj is None:
            return self
        return self._get(obj, objtype=objtype)

    def _get(self, obj: object, objtype=None) -> object:
        raise NotImplementedError(f"_get is not implemented for {type(obj)}")

    def __set__(self, obj: object, value: object):
        if self.optional and value is None:
            return
        if self.deprecated:
            warnings.warn(
                f"field {self.public_name} is deprecated and will be removed in a future version",
                UserWarning,
            )
        self._validate(obj, value)
        self._set(obj, value)

    def _validate(self, obj: object, value: object) -> None:
        """Override for type specific validation.

        Should raise an exception if invalid, not return a bool
        """
        # No exception raised by default
        pass

    def _set(self, obj: object, value: object) -> None:
        raise NotImplementedError("_set is not implemented")

    def _attribute_error(self, objtype):
        raise AttributeError(f"'{objtype.__name__}' object has no attribute '{self.public_name}'")

    def _get_object(self, obj: object) -> object:
        """Gets a field that is nested in another dictionary object.

        Allows a descriptor to grab a property from inside a dict that is potentially many
        levels deep
        """
        if self.nested is None:
            # This will happen when checking if the class has this attribute. Return the descriptor
            if obj is None:
                return self
            return obj[self.dict_name]

        nestedObj = self.__traverse_nested_objects(obj)
        return nestedObj[self.dict_name]

    def _set_object(self, obj: object, value: object) -> None:
        """Sets a field that is nested in another dictionary object.

        If that dictionary doesn't exist, this creates it, first checking that the attribute exists
        """
        if self.nested is None:
            return obj._set_item(self.dict_name, value)

        nestedObj = self.__traverse_nested_objects(obj)

        # finally, set the nested object on the dict/APIObject requested.
        desc = getattr(nestedObj.__class__, self.public_name, None)
        if desc is not None:
            setattr(nestedObj, self.public_name, value)
        else:
            nestedObj[self.dict_name] = value

    def _set_and_return_default(self, obj, objtype):
        if self.default is None:
            self._attribute_error(objtype)
        self._set_object(obj, self.default)
        return self.default

    def __traverse_nested_objects(self, obj: object) -> object:
        """Goes through nested objects until it has traversed all nested levels.

        Returns that object, creating it and parents along the way.
        """
        for f in self.nested:
            # Does it have a descriptor for this nested field? If so, use it
            desc = getattr(obj.__class__, f, None)
            # There is a descriptor or it has this attribute, use getattr
            if desc is not None or hasattr(obj, f):
                try:
                    obj = getattr(obj, f)
                # Attribute doesn't exist, set it as an empty dict. We have to assume that
                # descriptor handles this okay but we'll get an exception otherwise, just might be
                # hard to track down.
                except Exception:
                    setattr(obj, f, {})
                    obj = getattr(obj, f)
            else:
                try:
                    obj = obj[f]
                except KeyError:
                    obj[f] = {}
                    obj = obj[f]
        return obj


class _GeometryDescr(_BaseDescr):
    """Geometry field descriptor for a geodesic.bases.APIObject.

    Args:
        bbox: a bbox attribute that will be set when the geometry is updated. This is important for
            keeping geometry/bbox in sync on objects where the bbox is always derived from a
            geometry field.

    Methods:
        __get__: returns a shapely representation of the geometry

        __set__: coerces the input into a geojson dict (__geo_interface__) and stores internally to
            the APIObject dict

    """

    def __init__(self, bbox=None, **kwargs):
        super().__init__(**kwargs)
        self.bbox = bbox
        self._type = (str, dict, bytes, BaseGeometry)

    def _get(self, obj, objtype=None) -> BaseGeometry:
        """Gets the geometry attribute of an object.

        Raises:
            AttributeError if geometry is None or doesn't exist
        """
        # Try to get the private attribute by name (e.g. '_geometry')
        g = getattr(obj, self.private_name, None)
        if g is not None:
            # Return it if it exists
            return g

        # Otherwise, extract and compute. The attribute should be a geojson geometry, so this
        # should work if it's valid
        try:
            shp = self._get_object(obj)
            shp = shape(shp)
            setattr(obj, self.private_name, shp)
        except KeyError:
            return self.default
        except Exception:
            raise ValueError(f"unable to get '{self.public_name}'")
        return shp

    def _set(self, obj: object, value: Union[object, dict, str, bytes]) -> None:
        """Sets a geometry on obj.

        Args:
            obj: the object to be modified
            value: any object implementing the __geo_interface__ convention (https://gist.github.com/sgillies/2217756),
                a dict representing an RFC 7946 GeoJSON geometry, a WKT string, or a WKB bytestring
        """
        # Reset the private attribute (e.g. "_geometry") to None
        setattr(obj, self.private_name, None)

        if value is None:
            return

        # If it's a dict, set directly
        if isinstance(value, dict):
            setval = value
        # Is it WKT?
        elif isinstance(value, str):
            shp = loads_wkt(value)
            setval = shp.__geo_interface__
        # Is it WKB?
        elif isinstance(value, bytes):
            shp = loads_wkb(value)
            setval = shp.__geo_interface__
        # Otherwise use the __geo_interface__ attr
        else:
            setval = value.__geo_interface__

        self._set_object(obj, setval)

        if self.bbox is not None:
            self.bbox.__set__(obj, self.__get__(obj).bounds)

    def _validate(self, obj: object, value: object) -> None:
        if value is None:
            return
        if isinstance(value, dict):
            # make sure value is a geojson geometry
            try:
                shp = shape(value)
                if not shp.is_valid:
                    shp = shp.buffer(0)
                    if not shp.is_valid:
                        raise ValueError("this does not appear to be a valid geometry")
            except Exception as e:
                raise ValueError("this does not appear to be a valid geometry") from e
        elif isinstance(value, str):
            # make sure value is WKT
            try:
                loads_wkt(value)
            except Exception as e:
                raise ValueError(
                    "unable to parse input string: must be well-known text (WKT)"
                ) from e
        elif isinstance(value, bytes):
            # make sure value is WKB
            try:
                loads_wkb(value)
            except Exception as e:
                raise ValueError(
                    "unable to parse input string: must be well-known binary (WKB)"
                ) from e
            # make sure value it implements __geo_interface__
        elif not hasattr(value, "__geo_interface__"):
            raise ValueError(f"invalid geometry of type '{type(value)}'")


class _BBoxDescr(_GeometryDescr):
    """BBoxDescr is a bounding box field descriptor for a :class:`geodesic.bases.APIObject`.

    Inherits from :class:`GeometeryDescr` to use its validator

    Methods:
        __get__: returns a tuple of 4 values representing corners of the bbox
            (xmin, ymin, xmax, ymax)

        __set__: coerces the input into a shapely geom before taking the bounds and stores
            internally to the APIObject dict
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._type = (tuple, list, dict, str, bytes, BaseGeometry)

    def _get(self, obj: object, objtype=None) -> tuple:
        # Try to get the private attribute by name (e.g. '_bbox')
        g = getattr(obj, self.private_name, None)
        if g is not None:
            # Return it if it exists
            return g

        # Otherwise, extract and compute. The attribute should be a list/tuple
        try:
            bbox = self._get_object(obj)
            bbox = box(*bbox)
            bbox = bbox.bounds
            setattr(obj, self.private_name, bbox)
        except KeyError:
            return self.default
        except Exception:
            raise ValueError(f"unable to get '{self.public_name}'")
        return bbox

    def _set(self, obj: object, value: Union[object, dict, str, bytes, tuple, list]) -> None:
        if value is None:
            return
        # if it's a list/tuple, set directly
        if isinstance(value, (tuple, list)):
            bbox = tuple(value)
        # If it's a dict, get shape bounds
        elif isinstance(value, dict):
            bbox = shape(value).bounds
        # Is it WKT?
        elif isinstance(value, str):
            shp = loads_wkt(value)
            bbox = shp.bounds
        # Is it WKB?
        elif isinstance(value, bytes):
            shp = loads_wkb(value)
            bbox = shp.bounds
        # Otherwise use the __geo_interface__ attr
        else:
            shp = shape(value.__geo_interface__)
            bbox = shp.bounds

        self._set_object(obj, bbox)

    def _validate(self, obj: object, value: object) -> None:
        if isinstance(value, (list, tuple)):
            if len(value) != 4:
                raise ValueError("bbox must contain exactly 4 values")
            for x in value:
                if not isinstance(x, (int, float)):
                    raise ValueError("bbox elements must be real numbers")
        else:
            super()._validate(obj, value)


class _RegexDescr(_BaseDescr):
    """RegexDescr is a field that is validated against a regex.

    Valid inputs for this field follow: **{regex}**

    Methods:
        __get__: this attribute returns the validated string

        __set__: validates a string and then sets the value in the APIObject dict
    """

    def __init__(self, regex: Union[re.Pattern, str], empty_allowed=False, **kwargs) -> None:
        super().__init__(**kwargs)
        if isinstance(regex, str):
            self.regex = re.compile(regex)
        elif isinstance(regex, re.Pattern):
            self.regex = regex
        else:
            raise TypeError("regex must be a string or a re.Pattern object")
        self.empty_allowed = empty_allowed
        self.__doc__ = self.__doc__.format(regex=self.regex.pattern)
        self._type = (str,)

    def _get(self, obj: object, objtype=None) -> str:
        try:
            return self._get_object(obj)
        except KeyError:
            return self._set_and_return_default(obj, objtype)

    def _set(self, obj: object, value: str) -> None:
        if value == "" and self.empty_allowed:
            return
        self._set_object(obj, value)

    def _validate(self, obj: object, value: str) -> None:
        if not isinstance(value, str):
            raise ValueError(f"'{self.public_name}' must be a string. Got {value} ({type(value)}).")

        match = self.regex.match(value)
        if not match and not (self.empty_allowed and value == ""):
            raise ValueError(
                f"'{self.public_name}' must match {self.regex.pattern} value:'{value}'"
            )


class _DictDescr(_BaseDescr):
    """DictDescr is a dictionary field, such as properties in a GeoJSON object.

    This set/returns a dictionary field no matter what, it doesn't raise an
    attribute error

    Methods:
        __get__: returns the dict, creating it on the base object if necessary

        __set__: sets the dictionary after validating that it is a dict
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._type = (dict,)

    def _get(self, obj: object, objtype=None) -> dict:
        try:
            d = self._get_object(obj)
        except KeyError:
            d = {}
            if self.default is not None:
                d = self.default
            self._set_object(obj, d)
        return d

    def _set(self, obj: object, value: dict):
        if value is None:
            self._set_object(obj, {})
            return
        self._set_object(obj, value)

    def _validate(self, obj: object, value: dict) -> None:
        if value is None:
            return
        if not isinstance(value, dict):
            raise ValueError(f"{self.public_name} must be a dict")


class _ListDescr(_BaseDescr):
    """ListDescr is a list field, such as links in a GeoJSON feature collection object.

    This sets/returns a list field no matter what, it doesn't raise an
    attribute error

    Args:
        item_type (tuple or type): A type or tuple of types that are allowed as the inputs to this
            descriptor.  If you also set coerce to True, then the output type of the list (when
            you do a get) will be coerced to the first element of the tuple. If you would like to
            use this to pass in one type (typeA) and return another (typeB) then item_type should
            be `(typeB, typeA)` as well as `coerce=True`.
        min_len (int): a minimum number of elements for this list
        max_len (int): a maximum number of elements for this list
        coerce_items (bool): coerce all elements to the first type in the `item_type` arg when
            setting the values of the list.

    Methods:
        __get__: returns the list, creating it on the base object if necessary

        __set__: sets the list after validating that it is a list
    """

    def __init__(self, item_type=None, min_len=None, max_len=None, coerce_items=False, **kwargs):
        super().__init__(**kwargs)
        self.item_type = item_type
        self.max_len = max_len
        self.min_len = min_len
        self.coerce_items = coerce_items
        self._type = tuple(item_type) if isinstance(item_type, (tuple, list)) else (item_type,)

    def _get(self, obj: object, objtype=None) -> list:
        try:
            d = self._get_object(obj)
        except KeyError:
            if self.default is not None:
                return self.default
            d = []
            self._set_object(obj, d)
        return d

    def _set(self, obj: object, value: list):
        if value is None:
            return self._set_object(obj, [])

        if self.item_type is not None:
            if isinstance(self.item_type, (tuple, list)):
                _type = self.item_type[0]
            else:
                _type = self.item_type
            if len(value) > 0 and issubclass(_type, _BaseDescr):
                tmp = _APIObject()
                descr_tmp = _type()
                descr_tmp.__set_name__(tmp, "tmp")
                for i, v in enumerate(value):
                    descr_tmp._set(tmp, v)
                    value[i] = tmp["tmp"]

        if self.coerce_items:
            if isinstance(self.item_type, (tuple, list)):
                _type = self.item_type[0]
            else:
                _type = self.item_type

            if len(value) > 0 and isinstance(value[0], dict):
                value = [_type(**x) for x in value]
            else:
                value = [_type(x) for x in value]

        self._set_object(obj, value)

    def _validate(self, obj: object, value: list) -> None:
        if value is None:
            return
        if not isinstance(value, list):
            raise ValueError(f"{self.public_name} must be a list, got {type(value)}")

        # len check
        if self.max_len is not None and len(value) > self.max_len:
            raise ValueError(
                f"{self.public_name} must be less than or equal to {self.max_len}"
                "elements in length"
            )
        if self.min_len is not None and len(value) < self.min_len:
            raise ValueError(
                f"{self.public_name} must be greater than or equal to {self.min_len}"
                "elements in length"
            )

        if self.item_type is not None:
            if len(value) > 0:
                if isinstance(self.item_type, (tuple, list)):
                    _type = self.item_type[0]
                else:
                    _type = self.item_type
                if issubclass(_type, _BaseDescr):
                    for v in value:
                        _type()._validate({}, v)
                elif not isinstance(value[0], self.item_type):
                    raise ValueError(f"'{self.public_name}' must be a list of {self.item_type}")


class _TupleDescr(_BaseDescr):
    """TupleDescr is a tuple field (immutable), such as image shape.

    This raises an attribute error

    Args:
        item_type (type): Type to validate all elements in this tuple against

        min_len (int): The minimum allowed length for this tuple to be instantiated

        max_len (int): The maximum allowed length for this tuple

    Methods:
        __get__: returns the tuple, creating it on the base object if necessary

        __set__: sets the tuple after validating that it is a tuple
    """

    def __init__(self, item_type=None, min_len=None, max_len=None, **kwargs):
        super().__init__(**kwargs)
        self.item_type = item_type
        self.max_len = max_len
        self.min_len = min_len
        self._type = tuple(item_type) if isinstance(item_type, (tuple, list)) else (item_type,)

    def _get(self, obj: object, objtype=None) -> tuple:
        try:
            d = self._get_object(obj)
        except KeyError:
            self._attribute_error(objtype)
        return d

    def _set(self, obj: object, value: tuple):
        self._set_object(obj, tuple(value))

    def _validate(self, obj: object, value: tuple) -> None:
        if not isinstance(value, (tuple, list)):
            raise ValueError(f"{self.public_name} must be a tuple or list, got {type(value)}")

        # len check
        if self.max_len is not None and len(value) > self.max_len:
            raise ValueError(
                f"{self.public_name} must be less than or equal to {self.max_len}"
                "elements in length"
            )
        if self.min_len is not None and len(value) < self.min_len:
            raise ValueError(
                f"{self.public_name} must be greater than or equal to {self.min_len}"
                "elements in length"
            )

        if self.item_type is not None:
            if len(value) > 0:
                if not isinstance(value[0], self.item_type):
                    raise ValueError(f"'{self.public_name}' must be a tuple of {self.item_type}")


class _DatetimeDescr(_BaseDescr):
    """DatetimeDescr is a UTC datetime field.

    This is setable through typical python datetime objects,
    numpy datetime64, or pandas.Timestamp objects, pandas datetime objects, and RFC3339 strings.

    Methods:
        __get__: returns the datetime, raise an AttributeError if missing

        __set__: sets the datetime, storing internally as an RFC3339 string
    """

    rfc3339_regex = re.compile(
        r"^((?:(\d{4}-\d{2}-\d{2})T(\d{2}:\d{2}:\d{2}(?:\.\d+)?))(Z|[\+-]\d{2}:\d{2})?)$"
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._type = (str, datetime.datetime, np.datetime64)

    def _get(self, obj: object, objtype=None) -> datetime.datetime:
        # Try to get the private attribute by name (e.g. '_datetime')
        dt = getattr(obj, self.private_name, None)
        if dt is not None:
            # Return it if it exists
            return dt

        # Otherwise, extract and compute. The attribute should be an RFC3339 string
        try:
            dt = self._get_object(obj)
            dt = parse(dt)
            dt = datetime_to_utc(dt)
            setattr(obj, self.private_name, dt)
        except KeyError:
            return self._set_and_return_default(obj, objtype)
        except Exception:
            raise ValueError(f"unable to get '{self.public_name}', ")
        return dt

    def _set(self, obj: object, value: Union[str, datetime.datetime, np.datetime64]) -> None:
        # Reset the private attribute (e.g. "_datetime") to None
        setattr(obj, self.private_name, None)

        setval = None
        if isinstance(value, str):
            setval = value
        elif isinstance(value, datetime.datetime):
            # Convert to UTC
            value = datetime_to_utc(value)
            setval = value.isoformat()
        elif isinstance(value, np.datetime64):
            dtstr = np.datetime_as_string(value, timezone=pytz.UTC)
            dt = parse(dtstr)
            setval = dt.isoformat()
        else:
            raise ValueError("unable to set value")

        self._set_object(obj, setval)

    def _validate(self, obj: object, value: object) -> None:
        if isinstance(value, str):
            if not self.rfc3339_regex.match(value):
                try:
                    parse(value)
                except Exception as e:
                    raise ValueError(
                        f"{self.public_name} is not an RFC3339 formatted datetime string"
                        "and not parsable"
                    ) from e
        elif isinstance(value, datetime.datetime):
            # Convert to UTC
            try:
                value = datetime_to_utc(value)
            # I can't think of how this could fail, but it's here just in case
            except Exception as e:
                raise ValueError(f"{self.public_name} is an invalid datetime") from e

        elif isinstance(value, np.datetime64):
            try:
                dtstr = np.datetime_as_string(value, timezone=pytz.UTC)
                parse(dtstr)
            # I can't think of how this could fail, but it's here just in case
            except Exception as e:
                raise ValueError(f"{self.public_name} is an invalid datetime64") from e
        else:
            raise ValueError(
                f"{self.public_name} is an invalid datetime, must be string, "
                "datetime.datetime or numpy.datetime64"
            )


class _TimeDeltaDescr(_BaseDescr):
    r"""_TimeDeltaDescr is represents a time delta.

    Time deltas can be formatted as:

    \d+(ms|us|ns|[YMWDhms]){1}"

    \d+ - one or more digits
    Y  - years
    M  - months
    W  - weeks
    D  - days
    h  - hours
    m  - minutes
    s  - seconds
    ms - milliseconds
    us - microseconds
    ns - nanoseconds

    If specified by a string, it must be in a single choice of time unit, or can be provided as
    a datetime.timedelta or numpy.timedelta64 (which will be formatted in whole number seconds)

    Methods:
        __get__: returns the string
        __set__: sets from a string, datetime.timedelta or numpy.timedelta64
    """

    timedelta_re = re.compile(r"^\d+(ms|us|ns|[YMWDhms]){1}")
    unit_keys_classes = {
        "Y": ("years", relativedelta),
        "M": ("months", relativedelta),
        "W": ("weeks", relativedelta),
        "D": ("days", datetime.timedelta),
        "h": ("hours", datetime.timedelta),
        "m": ("minutes", datetime.timedelta),
        "s": ("seconds", datetime.timedelta),
        "ms": ("milliseconds", datetime.timedelta),
        "us": ("microseconds", datetime.timedelta),
    }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._type = (str, datetime.timedelta, np.timedelta64)

    def _get(self, obj: object, objtype=None) -> str:
        # Try to get the private attribute by name (e.g. '_datetime')
        td = getattr(obj, self.private_name, None)
        if td is not None:
            # Return it if it exists
            return td

        try:
            td_str = self._get_object(obj)
        except Exception:
            raise AttributeError(f"unable to get '{self.public_name}', ")

        m = self.timedelta_re.match(td_str)
        unit = m.group(1)
        value = int(td_str.replace(unit, ""))

        key = None
        try:
            key, _class = self.unit_keys_classes[unit]
        except KeyError:
            key, _class = "microseconds", datetime.timedelta
            value *= 0.001

        td = _class(**{key: value})
        setattr(obj, self.private_name, td)
        return td

    def _set(self, obj: object, value: Union[str, datetime.timedelta, np.timedelta64]) -> None:
        # set the private value back to None
        setattr(obj, self.private_name, None)

        v = self._validate(obj, value)
        self._set_object(obj, v)

    def _validate(self, obj: object, value: object) -> str:
        if isinstance(value, str):
            if not self.timedelta_re.match(value):
                raise ValueError(f"string must match {self.timedelta_re.pattern}")
            return value
        elif isinstance(value, datetime.timedelta):
            return f"{int(value.total_seconds()):d}s"
        elif isinstance(value, np.timedelta64):
            return f"{int(value / np.timedelta64(1, 's')):d}s"
        raise ValueError(
            "must be a string, datetime.timedelta or numpy.timedelta64,"
            f"got {value.__class__.__name__}"
        )


class _StringDescr(_BaseDescr):
    """StringDescr is a string field, raises attribute error if the string isn't set.

    Args:
        one_of: is a list of possible values this string can be.

        coerce: stringify whatever the input

    Methods:
        __get__: returns the string

        __set__: sets the string after validating that it is a string/unicode
    """

    def __init__(self, one_of=[], coerce: bool = False, soft_one_of=[], **kwargs):
        super().__init__(**kwargs)
        self.one_of = one_of
        self.soft_one_of = soft_one_of
        self.coerce = coerce
        self._type = (str,)

    def _get(self, obj: object, objtype=None) -> str:
        try:
            return self._get_object(obj)
        except KeyError:
            return self._set_and_return_default(obj, objtype)

    def _set(self, obj: object, value: str):
        self._set_object(obj, str(value))

    def _validate(self, obj: object, value: str) -> None:
        if self.coerce:
            value = str(value)
        if not isinstance(value, str):
            raise ValueError(f"{self.public_name} must be a str")
        if self.one_of:
            if value not in self.one_of:
                raise ValueError(f'{self.public_name} must be one of {", ".join(self.one_of)}')
        elif self.soft_one_of:
            if value not in self.soft_one_of:
                warnings.warn(
                    f"{self.public_name} should be one of {', '.join(self.soft_one_of)}",
                    UserWarning,
                )


class _IntDescr(_BaseDescr):
    """IntDescr is an integer field, raises attribute error if the int isn't set.

    Methods:
        __get__: returns the int

        __set__: sets the int after validating that it is an int
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._type = (int,)

    def _get(self, obj: object, objtype=None) -> int:
        try:
            return self._get_object(obj)
        except KeyError:
            return self._set_and_return_default(obj, objtype)

    def _set(self, obj: object, value: int):
        self._set_object(obj, value)

    def _validate(self, obj: object, value: int) -> None:
        if not isinstance(value, int):
            raise ValueError(f"{self.public_name} must be an int")


class _FloatDescr(_BaseDescr):
    """FloatDescr is an float field, raises attribute error if the float isn't set.

    Methods:
        __get__: returns the float

        __set__: sets the float after validating that it is an float
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._type = (float,)

    def _get(self, obj: object, objtype=None) -> float:
        try:
            return self._get_object(obj)
        except KeyError:
            return self._set_and_return_default(obj, objtype)

    def _set(self, obj: object, value: float):
        self._set_object(obj, float(value))

    def _validate(self, obj: object, value: float) -> None:
        if not isinstance(value, (float, int)):
            raise ValueError(f"{self.public_name} must be a float")


class _NumberDescr(_BaseDescr):
    """NumberDescr is an numeric field, raises attribute error if the number isn't set.

    Methods:
        __get__: returns the number

        __set__: sets the number after validating that it is a number
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._type = (float, int, complex)

    def _get(self, obj: object, objtype=None) -> Union[float, int, complex]:
        try:
            return self._get_object(obj)
        except KeyError:
            return self._set_and_return_default(obj, objtype)

    def _set(self, obj: object, value: Union[float, int, complex]):
        self._set_object(obj, value)

    def _validate(self, obj: object, value: Union[float, int, complex]) -> None:
        if not isinstance(value, (int, float, complex)):
            raise ValueError(f"{self.public_name} must be a number")


class _BoolDescr(_BaseDescr):
    """BoolDescr is an bool field, raises attribute error if the bool isn't set.

    Methods:
        __get__: returns the bool

        __set__: sets the bool after validating that it is an bool
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._type = (bool,)

    def _get(self, obj: object, objtype=None) -> bool:
        try:
            return self._get_object(obj)
        except KeyError:
            return self._set_and_return_default(obj, objtype)

    def _set(self, obj: object, value: bool):
        self._set_object(obj, value)

    def _validate(self, obj: object, value: bool) -> None:
        if not isinstance(value, bool):
            raise ValueError(f"{self.public_name} must be a bool")


class _DatetimeIntervalDescr(_BaseDescr):
    """DatetimeIntervalDescr is a start/end.

    A Datetime interval pair which can be specified using either RFC3339 strings
    datetime.datetime, pandas.Timestamp, or numpy.datetime64

    Methods:
        __get__: returns the datetime interval as a tuple, raise an AttributeError if missing

        __set__: sets the datetime interval, storing internally as a string of the format
            '<start>/<end>' where start/end are RFC3339 formatted strings or "..". This is in
            accordance with the STAC datetime spec
    """

    rfc3339_regex = re.compile(
        r"^((?:(\d{4}-\d{2}-\d{2})T(\d{2}:\d{2}:\d{2}(?:\.\d+)?))(Z|[\+-]\d{2}:\d{2})?)$"
    )

    def __init__(self, format="string", **kwargs):
        super().__init__(**kwargs)
        if format not in ["string", "tuple", "list"]:
            raise ValueError("format must be one of 'string', 'tuple', or 'list'")
        self.format = format
        self._type = (str, tuple, list)

    def _get(self, obj: object, objtype=None) -> tuple:
        # Try to get the private attribute by name (e.g. '_datetime')
        dt = getattr(obj, self.private_name, None)
        if dt is not None:
            # Return it if it exists
            return dt

        try:
            dt = self._get_object(obj)
            if self.format == "string":
                start_str, end_str = dt.split("/")
            else:
                start_str, end_str = dt
            start = end = None
            if ".." not in start_str:
                start = parse(start_str)
                start = datetime_to_utc(start)
            if ".." not in end_str:
                end = parse(end_str)
                end = datetime_to_utc(end)

            setattr(obj, self.private_name, (start, end))
        except KeyError:
            return self._set_and_return_default(obj, objtype)
        except Exception:
            raise ValueError(f"unable to get '{self.public_name}', ")
        return (start, end)

    def _set(self, obj: object, value: object) -> None:
        setattr(obj, self.private_name, None)
        if isinstance(value, str):
            start_str, end_str = value.split("/")
            # Canonicalize the string
            if start_str != "..":
                start_str = datetime_to_utc(parse(start_str)).isoformat()
            if end_str != "..":
                end_str = datetime_to_utc(parse(end_str)).isoformat()
        else:
            start, end = value
            if isinstance(start, str):
                if start == "..":
                    if self.format == "string":
                        start_str = start
                    else:
                        start_str = None
                else:
                    start_str = datetime_to_utc(parse(start)).isoformat()
            elif isinstance(start, datetime.datetime):
                start_str = datetime_to_utc(start).isoformat()
            elif isinstance(start, np.datetime64):
                start_str = np.datetime_as_string(start, timezone=pytz.UTC)
                start_str = parse(start_str).isoformat()
            elif start is None:
                if self.format == "string":
                    start_str = ".."
                else:
                    start_str = None
            else:
                raise ValueError("error setting start datetime, invalid datetime format")

            if isinstance(end, str):
                if end == "..":
                    if self.format == "string":
                        end_str = end
                    else:
                        end_str = None
                else:
                    end_str = datetime_to_utc(parse(end)).isoformat()
            elif isinstance(end, datetime.datetime):
                end_str = datetime_to_utc(end).isoformat()
            elif isinstance(end, np.datetime64):
                end_str = np.datetime_as_string(end, timezone=pytz.UTC)
                end_str = parse(end_str).isoformat()
            elif end is None:
                if self.format == "string":
                    end_str = ".."
                else:
                    end_str = None
            else:
                raise ValueError("error setting end datetime, invalid datetime format")

        if self.format == "string":
            self._set_object(obj, f"{start_str}/{end_str}")
        elif self.format == "tuple":
            self._set_object(obj, (start_str, end_str))
        elif self.format == "list":
            self._set_object(obj, [start_str, end_str])

    def _validate(self, obj: object, value: object) -> None:
        if isinstance(value, str):
            try:
                start_str, end_str = value.split("/")

                # Are they RFC3339?
                if not self.rfc3339_regex.match(start_str) and start_str != "..":
                    try:
                        parse(start_str)
                    except Exception:
                        raise ValueError("start must be RFC3339 formatted or coercible")
                if not self.rfc3339_regex.match(end_str) and end_str != "..":
                    try:
                        parse(end_str)
                    except Exception:
                        raise ValueError("end must be RFC3339 formatted or coercible")
            except Exception as e:
                raise ValueError("datetime as a string must be of the form <start>/<end>") from e

        elif isinstance(value, (tuple, list)):
            if len(value) != 2:
                raise ValueError(
                    "Must provide a start and end datetime. "
                    "Provide None or '..' string if one end is open"
                )
            for i, t in enumerate(value):
                if isinstance(t, str):
                    if t == "":
                        raise ValueError("string must be either '..' or a valid RFC3339 datetime")
                    if t != ".." and not self.rfc3339_regex.match(t):
                        if i == 0:
                            name = "start"
                        else:
                            name = "end"
                        try:
                            parse(t)
                        except Exception:
                            raise ValueError(f"{name} must be RFC3339 formatted or coercible")

                elif not (
                    isinstance(t, datetime.datetime) or t is None or isinstance(t, np.datetime64)
                ):
                    raise ValueError(
                        "not a recognized datetime format. must be either "
                        "python datetime, numpy.datetime64, pandas.Timestamp or string"
                    )
        else:
            raise ValueError(f"invalid datetime interval format {type(value)}")


class _DTypeDescr(_BaseDescr):
    """DTypeDescr is a np.dtype field, raises attribute error if dtype is not set.

    Methods:
        __get__: returns the np.dtype

        __set__: sets the dtype after validating that it is a dtype, holds internally by its str
            representation
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._type = (np.dtype, str)

    def _get(self, obj: object, objtype=None) -> np.dtype:
        try:
            dt = self._get_object(obj)
            dt = np.dtype(dt)
            return dt
        except KeyError:
            return self._set_and_return_default(obj, objtype)

    def _set(self, obj: object, value: bool):
        dt = np.dtype(value)
        dtype_str = dt.descr[0][1]

        self._set_object(obj, dtype_str)

    def _validate(self, obj: object, value: np.dtype) -> None:
        if isinstance(value, np.dtype):
            return
        else:
            try:
                np.dtype(value)
            except Exception:
                raise ValueError(
                    f"{self.public_name} must be a np.dtype, python numeric dtype, or valid"
                    "dtype string/descriptor"
                )


class _TypeConstrainedDescr(_BaseDescr):
    """TypeConstrainedDescr creates an arbitrary field that must be constrained to a specific type.

    Args:
        type (type): the type you want to constrain this too

        coerce (bool): the stored/retrieved result will be coerced to the type (or the first type
            in a tuple of types)

    Methods:
        __get__: returns the object as is, AttributeError if missing

        __set__: sets the object as is, validating against the specified type constraint
    """

    def __init__(self, type, coerce=False, **kwargs):
        super().__init__(**kwargs)
        self._type = tuple(type) if isinstance(type, (tuple, list)) else (type,)
        self.coerce = coerce

    def _get(self, obj: object, objtype=None) -> float:
        try:
            return self._get_object(obj)
        except KeyError:
            return self._set_and_return_default(obj, objtype)

    def _set(self, obj: object, value: object):
        if self.coerce:
            if isinstance(self._type, (tuple, list)):
                _type = self._type[0]
            else:
                _type = self._type

            if isinstance(value, dict):
                value = _type(**value)
            else:
                value = _type(value)

        self._set_object(obj, value)

    def _validate(self, obj: object, value: object) -> None:
        if not isinstance(value, self._type):
            raise ValueError(f"{self.public_name} must be a {self._type}, got {type(value)}")


supported_schemes = ("http", "https")


class _URLDescr(_StringDescr):
    """A URL string that is checked to be a valid URL.

    Inherits from :class:`_StringDescr<geodesic.descriptors._StringDescr>` for all methods except
    validate.

    Methods:
        __get__: Returns the validated URL string

        __set__: Check that its a valid URL and set the URL as a string

    """

    def _validate(self, obj: object, value: str) -> None:
        super()._validate(obj, value)

        parsed = urlparse(value)
        if parsed.scheme not in supported_schemes:
            raise ValueError(
                f"only schemes {', '.join(supported_schemes)} are supported, got {parsed.scheme}"
            )

        if parsed.netloc == "":
            raise ValueError(f"url {value} had an empty network location")
