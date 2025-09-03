from dataclasses import fields, is_dataclass, MISSING
from typing import get_type_hints, get_origin, get_args

from loguru import logger as log


def json_to_dataclass(cls, data: dict):
    if not is_dataclass(cls):
        raise TypeError("Expected a dataclass type")

    log.debug(data)

    result = {}
    hints = get_type_hints(cls)

    for f in fields(cls):
        name = f.name
        typ = hints.get(name, f.type)

        if name in data:
            val = data[name]

            # handle nested dataclass
            if is_dataclass(typ) and isinstance(val, dict):
                result[name] = json_to_dataclass(typ, val)

            # handle list[dataclass]
            elif get_origin(typ) is list:
                inner_args = get_args(typ)
                if inner_args:  # Check if there are type arguments
                    inner_type = inner_args[0]
                    if is_dataclass(inner_type) and isinstance(val, list):
                        result[name] = [json_to_dataclass(inner_type, v) if isinstance(v, dict) else v for v in val]
                    else:
                        result[name] = val
                else:
                    # Handle List without type arguments
                    result[name] = val

            else:
                result[name] = val

        elif f.default is not MISSING:
            result[name] = f.default
        elif f.default_factory is not MISSING:
            result[name] = f.default_factory()
        else:
            # Log warning instead of raising error
            log.warning(f"Missing required field '{name}' for {cls.__name__}, using None")
            result[name] = None

    return cls(**result)


import json
import re


def from_str_extract_json(text: str) -> dict:
    match = re.search(r'\{.*}', text, re.DOTALL)
    return json.loads(match.group()) if match else {}
