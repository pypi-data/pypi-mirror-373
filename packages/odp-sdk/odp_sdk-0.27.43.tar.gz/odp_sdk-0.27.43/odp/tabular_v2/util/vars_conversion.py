import datetime
from typing import Dict, List, Union


def vars_to_json(vars: Union[Dict, List, None]) -> Union[Dict, List[Dict], None]:
    """
    Convert a dictionary of variables to a JSON-serializable dictionary which preserve datetime type
    """
    if not vars:
        return None

    def _var_to_json(value):
        if isinstance(value, str):
            return {"type": "string", "value": value}
        if isinstance(value, int):
            return {"type": "integer", "value": value}
        if isinstance(value, float):
            return {"type": "float", "value": value}
        if isinstance(value, bool):
            return {"type": "boolean", "value": value}
        if isinstance(value, datetime.datetime):
            return {"type": "datetime", "value": value.isoformat()}
        if isinstance(value, datetime.date):
            return {"type": "date", "value": value.isoformat()}
        if isinstance(value, datetime.time):
            return {"type": "time", "value": value.isoformat()}
        else:
            raise ValueError(f"unsupported type {type(value)}")

    if isinstance(vars, dict):
        return {k: _var_to_json(v) for k, v in vars.items()}
    elif isinstance(vars, list):
        return [_var_to_json(v) for v in vars]
    else:
        raise ValueError(f"unsupported type {type(vars)}")


def json_to_vars(j: Union[Dict, List[Dict], None]) -> Union[Dict, List, None]:
    """
    Convert back a JSON dict to variables
    """
    if not j:
        return None

    def _json_to_var(j):
        if j["type"] == "string":
            return j["value"]
        if j["type"] == "integer":
            return int(j["value"])
        if j["type"] == "float":
            return j["value"]
        if j["type"] == "boolean":
            return j["value"]
        if j["type"] == "datetime":
            return datetime.datetime.fromisoformat(j["value"])
        if j["type"] == "date":
            return datetime.date.fromisoformat(j["value"])
        if j["type"] == "time":
            return datetime.time.fromisoformat(j["value"])
        else:
            raise ValueError(f"unsupported type {j['type']}")

    if isinstance(j, list):
        return [_json_to_var(v) for v in j]
    elif isinstance(j, dict):
        return {k: _json_to_var(v) for k, v in j.items()}
    else:
        raise ValueError(f"unsupported type {type(j)}")
