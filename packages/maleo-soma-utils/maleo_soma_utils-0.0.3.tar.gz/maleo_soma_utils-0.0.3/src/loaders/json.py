import json
from pathlib import Path
from typing import Union, Any


def from_path(path: Union[Path, str]) -> Any:
    file_path = Path(path)

    if not file_path.is_file():
        raise FileNotFoundError(f"File not found: {file_path}")

    try:
        with open(file_path, "r") as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in path {path}: {str(e)}")
    except Exception as e:
        raise ValueError(f"Failed to load json from path {path}: {str(e)}")


def from_string(string: str) -> Any:
    return json.loads(string)
