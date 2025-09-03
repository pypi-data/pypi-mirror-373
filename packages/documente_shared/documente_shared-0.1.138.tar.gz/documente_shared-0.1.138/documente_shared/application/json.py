import re
from typing import Any

import unicodedata
from unidecode import unidecode


def underscoreize(data: Any) -> Any:
    if isinstance(data, dict):
        new_dict = {}
        for key, value in data.items():
            new_key = re.sub(r"(?<!^)(?=[A-Z])", "_", key).lower()
            new_dict[new_key] = underscoreize(value)
        return new_dict
    elif isinstance(data, list):
        return [underscoreize(item) for item in data]
    else:
        return data


def safe_format(data: Any) -> Any:
    if isinstance(data, dict):
        new_dict = {}
        for key, value in data.items():
            new_key = unidecode(key.replace(" ", "_"))
            new_dict[new_key] = safe_format(value)
        return new_dict
    elif isinstance(data, list):
        return [safe_format(item) for item in data]
    else:
        return data


def normalize_key(key: str) -> str:
    normalized = unicodedata.normalize('NFC', key)
    underscored = re.sub(r'\s+', '_', normalized)
    return underscored


def normalize_dict_keys(data: dict) -> dict:
    return {normalize_key(k): v for k, v in data.items()}


def normalize_list_keys(data: list) -> list:
    return [normalize_dict_keys(item) for item in data]
