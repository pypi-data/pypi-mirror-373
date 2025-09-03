# *************************************************************************
#
#  Copyright (c) 2025 - Datatailr Inc.
#  All Rights Reserved.
#
#  This file is part of Datatailr and subject to the terms and conditions
#  defined in 'LICENSE.txt'. Unauthorized copying and/or distribution
#  of this file, in parts or full, via any medium is strictly prohibited.
# *************************************************************************

import importlib
import json
import base64


class dt_json:
    @staticmethod
    def dumps(obj):
        d = obj.__dict__ if hasattr(obj, "__dict__") else obj
        d["__class__"] = obj.__class__.__name__
        return json.dumps(d)

    @classmethod
    def loads(cls, json_str):
        d = json.loads(json_str)
        class_name = d.get("__class__")
        module = importlib.import_module("datatailr")
        if class_name and hasattr(module, class_name):
            target_class = getattr(module, class_name)
            obj = target_class.__new__(target_class)
            if hasattr(obj, "from_json"):
                obj.from_json(d)
                return obj
            # fallback: set attributes directly
            for k, v in d.items():
                if k != "__class__":
                    setattr(obj, k, v)
            return obj
        return d  # fallback to dict if not registered

    @classmethod
    def load(cls, json_file):
        return json.load(json_file)


def encode_json(obj) -> str:
    """
    Encode an object to a JSON string with class information.
    """
    json_str = json.dumps(
        obj, default=lambda o: o.__dict__ if hasattr(o, "__dict__") else o
    )
    return base64.b64encode(json_str.encode("utf-8")).decode("utf-8")


def is_base64(s: str) -> bool:
    try:
        # Try decoding the string
        base64.b64decode(s, validate=True)
        return True
    except (ValueError, TypeError):
        # If decoding fails, it's not valid Base64
        return False


def decode_json(encoded_str: str):
    """
    Decode a JSON string back to an object.
    """
    if is_base64(encoded_str):
        json_str = base64.b64decode(encoded_str.encode("utf-8")).decode("utf-8")
    else:
        json_str = encoded_str
    return json.loads(json_str)
