import re


def camel_to_snake_key(name: str) -> str:
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()

def camel_to_snake(data: dict | list) -> dict | list:
    if isinstance(data, dict):
        return {camel_to_snake_key(k): camel_to_snake(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [camel_to_snake(item) for item in data]
    else:
        return data