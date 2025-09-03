import importlib.resources

def get_text(filename: str) -> str:
    """Read a text file bundled in the library's data folder."""
    with importlib.resources.open_text("nlptkl.data", filename) as f:
        return f.read()
