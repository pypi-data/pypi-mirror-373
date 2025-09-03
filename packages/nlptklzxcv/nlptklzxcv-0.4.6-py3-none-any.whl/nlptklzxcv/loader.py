import importlib.resources as resources

def get_text(filename: str) -> str:
    """Read a text file bundled in the library's data folder."""
    # Try modern API (Python 3.9+)
    if hasattr(resources, "files"):
        file_path = resources.files("nlptklzxcv.data") / filename
        return file_path.read_text(encoding="utf-8")
    # Fallback for Python < 3.9
    return resources.read_text("nlptklzxcv.data", filename, encoding="utf-8")
