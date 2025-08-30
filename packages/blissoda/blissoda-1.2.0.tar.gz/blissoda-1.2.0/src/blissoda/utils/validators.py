from pathlib import Path


def is_file(filename: str) -> str:
    filepath = Path(filename)
    if not filepath.exists():
        raise ValueError(f"File {filename} does not exist")
    if not filepath.is_file():
        raise ValueError(f"{filename} is not a file")
    return str(filepath)
