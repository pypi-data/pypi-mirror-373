import re
from typing import List
from urllib.parse import urlencode


def to_camel_case(value) -> str:
    """
    Converts a snake case string to camel case

    :param value: The string to convert

    :returns: str

    >>> to_camel_case("snake_case")
    'snakeCase'
    """
    content: List[str] = value.title().split('_')
    content[0] = content[0].lower()
    return "".join(content)


def to_snake_case(value: str) -> str:
    """
    Converts a camel case string to snake case.

    :param value: The string to convert.

    :returns: str

    >>> to_snake_case("CamelCase")
    'camel_case'
    """
    value = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', value)
    value = re.sub('__([A-Z])', r'_\1', value)
    value = re.sub('([a-z0-9])([A-Z])', r'\1_\2', value)
    return value.lower()


def encode_url_params(d: dict, doseq: bool = True, remove_keys: List[str] = [], to_camel: bool = True) -> str:
    """
    Encodes the keys and values of a dictionary to url formatted string.

    :param d: The dictionary to encode.
    :param doseq: If any values in the query arg are sequences and doseq is true, each
    sequence element is converted to a separate parameter.
    :param remove_keys: Any keys to remove from the dictionary.
    :param to_camel: Convert snake case to camel case

    :returns: str
    """
    remove_keys.append('self')
    filtered = {}
    for k, v in d.items():
        if v is not None and k not in remove_keys:
            if '_' in k and to_camel:
                filtered[to_camel_case(k)] = v
            else:
                filtered[k] = v

    return f'?{urlencode(filtered, doseq)}'


if __name__ == "__main__":
    import doctest

    doctest.testmod()
