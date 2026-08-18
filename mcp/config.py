from pathlib import Path


# MCP'nin erişmesine izin verilen klasörler
ALLOWED_PATHS = [
    Path.home() / "Desktop",
    Path.home() / "Documents",
    Path.home() / "Downloads",
]