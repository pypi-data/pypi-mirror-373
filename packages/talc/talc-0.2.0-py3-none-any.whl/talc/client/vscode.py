import os
import platform
from pathlib import Path
from typing import Optional


def get_vscode_settings_path() -> Optional[Path]:
    system = platform.system()
    if system == "Windows":
        appdata = os.environ.get("APPDATA")
        if appdata:
            return Path(appdata) / "Code" / "User" / "settings.json"
    elif system == "Darwin":  # macOS
        home = Path.home()
        return (
            home / "Library" / "Application Support" / "Code" / "User" / "settings.json"
        )
    elif system == "Linux":
        home = Path.home()
        return home / ".config" / "Code" / "User" / "settings.json"
    else:
        return None
