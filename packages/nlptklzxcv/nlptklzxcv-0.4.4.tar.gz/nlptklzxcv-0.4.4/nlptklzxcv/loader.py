import importlib.resources as resources

def get_text(filename: str) -> str:
    """Read a text file bundled in the library's data folder."""
    file_path = resources.files("nlptklzxcv.data") / filename
    return file_path.read_text(encoding="utf-8")