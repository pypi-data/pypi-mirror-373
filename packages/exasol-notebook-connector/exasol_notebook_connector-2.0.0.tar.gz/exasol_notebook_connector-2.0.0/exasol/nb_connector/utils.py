from pathlib import Path
from typing import Optional


def upward_file_search(file_name: str) -> str:
    """
    Looks for a specified file starting from the current directory upward the file hierarchy.
    Hence, the last place to find the file is the root.

    Returns the full path of the file if found.
    Otherwise, raises a ValueError exception.
    """

    dir = Path().resolve()
    while dir.name:
        maybe_file = dir / file_name
        if maybe_file.is_file():
            return str(maybe_file)
        dir = dir.parent
    raise ValueError(f"Cannot find {file_name}")


def optional_str_to_bool(value: Optional[str]) -> Optional[bool]:
    """
    Converts an optional string value to an optional boolean.
    None, '' => None.
    Case-insensitive "y", "yes", "true" => True
    Case-insensitive "n", "no", "false" => False
    Any other value cause a ValueError exception.
    """
    if not value:
        return None

    mapping = {
        "y": True,
        "yes": True,
        "true": True,
        "n": False,
        "no": False,
        "false": False,
    }
    key = value.lower()

    try:
        result = mapping[key]
    except KeyError as ex:
        raise ValueError("Invalid boolean value " + value) from ex

    return result
