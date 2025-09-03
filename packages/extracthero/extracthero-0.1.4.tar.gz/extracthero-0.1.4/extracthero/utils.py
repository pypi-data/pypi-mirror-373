def load_html(path: str) -> str:
    """Read a local HTML file and return its contents as a string (UTF-8)."""
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()