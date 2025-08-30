import json
from typing import Optional


def read_config(filename: Optional[str]) -> dict:
    if not filename:
        return dict()
    if filename.endswith(".json"):
        return _read_json(filename)
    else:
        return _read_poni(filename)


def _read_json(filename: str) -> dict:
    with open(filename, "r") as fp:
        return json.load(fp)


def _read_poni(filename: str) -> dict:
    options = dict()
    with open(filename, "r") as f:
        for line in f:
            if not line or line.startswith("#"):
                continue
            key, sep, value = line.partition(":")
            if not sep or not value:
                continue
            try:
                value = json.loads(value.strip())
            except json.JSONDecodeError:
                value = value.strip()
            except Exception:
                continue
            options[_parse_poni_key(key)] = value
    return options


def _parse_poni_key(k: str) -> str:
    new_key = k.strip().lower()
    if new_key == "distance":
        return "dist"
    return new_key
