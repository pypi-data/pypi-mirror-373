import datetime
import json
import logging
import types
from decimal import Decimal
from enum import Enum
from typing import Any, Callable, Dict, Type, Union, _GenericAlias
from uuid import UUID


class Field:
    def __init__(self, default_factory=None):
        self.default_factory = default_factory


class PrivateAttr:
    def __init__(self, val):
        self.val = val


class SecretStr:
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return "********"

    def __str__(self):
        return "********"

    def __eq__(self, other):
        return self.value == other

    def __ne__(self, other):
        return self.value != other

    def __hash__(self):
        return hash(self.value)

    def get_secret_value(self):
        return self.value


class BaseModel:
    def __init__(self, **kwargs):
        mn = type(self).__name__
        attrs = _attrs(self.__class__)
        for name, typ in attrs.items():
            if name in kwargs:
                val = kwargs.get(name)
                logging.debug("field %s.%s in kwargs: %s", mn, name, val)
            else:
                logging.debug("field %s.%s not in kwargs", mn, name)
                val = getattr(self, name, None)
                if isinstance(val, Field):
                    val = val.default_factory()
                if isinstance(val, PrivateAttr):
                    setattr(self, name, val.val)
                    continue
            if typ == PrivateAttr:
                continue
            if typ == SecretStr:
                if not isinstance(val, SecretStr):
                    val = SecretStr(str(val))

            subtype = typ
            if isinstance(typ, types.GenericAlias):
                subtype = typ.__args__[0]
            if isinstance(typ, _GenericAlias):
                subtype = typ.__args__[0]

            if subtype == UUID:
                if val is None:
                    pass
                elif not isinstance(val, UUID):
                    val = UUID(str(val))

            if subtype == datetime.datetime:
                if val is None:
                    val = None
                elif not isinstance(val, datetime.datetime):
                    val = datetime.datetime.fromisoformat(str(val))

            if BaseModel in getattr(subtype, "__mro__", []):
                logging.debug("field %s.%s is BaseModel: %s", mn, name, typ)
                if isinstance(val, dict):
                    val = subtype(**val)
            elif not _is_type(val, typ) and not _is_type(val, Any):
                raise ValueError(f"field {mn}.{name} value {val} is not of type {typ} but of type {type(val)}")

            setattr(self, name, val)

    def json(self, exclude_unset=False, **kwargs):
        return json.dumps(self, cls=JSONCodec, skipkeys=exclude_unset, **kwargs)

    def dict(self, exclude_unset=False):
        res_dict = self.__dict__.copy()
        for k, v in self.__dict__.items():
            if isinstance(v, BaseModel):
                res_dict[k] = v.dict(exclude_unset)
            if k.startswith("_"):
                res_dict.pop(k)
            if exclude_unset and v is None:
                res_dict.pop(k)
        return res_dict

    def __str__(self):
        return str(self.json())

    def __repr__(self):
        return str(self.json())

    def __iter__(self):
        return iter(self.dict().items())

    def __eq__(self, other):
        if not isinstance(other, BaseModel):
            return False
        return self.json() == other.json()


def _attrs(cls):
    attrs = {}
    # check for order
    for x in cls.__mro__:
        if hasattr(x, "__annotations__"):
            for name, typ in x.__annotations__.items():
                attrs.setdefault(name, typ)
    return attrs


def _is_type(val, typ) -> bool:
    if isinstance(typ, list):
        # logging.info("_is_type(%s, list %s)", val, typ)
        for t in typ:
            if _is_type(val, t):
                return True
        return False
    if isinstance(typ, (types.GenericAlias, _GenericAlias)):  # supported in all python versions?
        if typ.__origin__ is Union:
            return any(_is_type(val, t) for t in typ.__args__)
        typ = typ.__origin__  # we only bother to check the main type, not the parametrized ones
    try:
        if typ is Any:
            return True
        if isinstance(val, typ):
            return True
    except Exception as e:
        if isinstance(val, SecretStr):
            logging.warning("is_type(%s, %s) failed: %s", "SensitiveInformation", typ, e)
        else:
            logging.warning("is_type(%s, %s) failed: %s", val, typ, e)
        return True
    return False


class JSONCodec(json.JSONEncoder, json.JSONDecoder):
    encoders_by_type: Dict[Type[Any], Callable[[Any], Any]] = {
        bytes: lambda o: o.decode(),
        datetime.date: lambda d: d.isoformat(),
        datetime.datetime: lambda dt: dt.isoformat(),
        datetime.time: lambda t: t.isoformat(),
        datetime.timedelta: lambda td: td.total_seconds(),
        Decimal: lambda x: int(x) if x.as_tuple().exponent >= 0 else float(x),
        Enum: lambda o: o.value,
        SecretStr: str,
        set: list,
        UUID: str,
    }

    def default(self, obj):
        if isinstance(obj, BaseModel):
            return obj.dict(exclude_unset=self.skipkeys)

        for typ, encoder in self.encoders_by_type.items():
            if isinstance(obj, typ):
                return encoder(obj)
        raise TypeError(f"Object of type '{obj.__class__.__name__}' is not JSON serializable")
