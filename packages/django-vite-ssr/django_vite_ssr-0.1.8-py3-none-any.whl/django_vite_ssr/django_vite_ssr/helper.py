from pathlib import Path
import json
from typing import TypedDict, List, Optional

class ViteConfigDict(TypedDict):
    """
    Vite configuration dictionary.
    """


    dir: str
    """
    Directory where the Django is located.
    """

    name: str
    """
    Name of the Django project.
    """

def get_package_path():
    return Path.cwd()

def configure_apps(config_dict: ViteConfigDict) -> bool:
    package_path = get_package_path()
    manifest_path = package_path / "configurations.manifest.json"

    if not manifest_path.exists():
        configs: List[ViteConfigDict] = []
    else:
        with open(manifest_path, "r", encoding="utf-8") as f:
            try:
                configs = json.load(f)
            except json.JSONDecodeError:
                configs = []

    configs.append(config_dict)

    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(configs, f, indent=2)
    return True

def get_config() -> Optional[ViteConfigDict]:
    package_path = get_package_path()
    manifest_path = package_path / "configurations.manifest.json"
    if not manifest_path.exists():
        return None
    with open(manifest_path, "r", encoding="utf-8") as f:
        try:
            configs: List[ViteConfigDict] = json.load(f)
        except json.JSONDecodeError:
            return None
    if configs:
        return configs[0]
    return

