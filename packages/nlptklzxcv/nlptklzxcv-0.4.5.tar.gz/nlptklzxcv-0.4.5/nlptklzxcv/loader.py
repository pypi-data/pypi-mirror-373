import importlib.resources as resources

def get_text(filename: str) -> str:
    """Read a text file bundled in the library's data folder."""
    try:
        # For Python 3.9+ (new API)
        file_path = resources.files("nlptklzxcv.data") / filename
        return file_path.read_text(encoding="utf-8")
    except AttributeError:
        # For Python 3.8 (fallback API)
        return resources.read_text("nlptklzxcv.data", filename, encoding="utf-8")
