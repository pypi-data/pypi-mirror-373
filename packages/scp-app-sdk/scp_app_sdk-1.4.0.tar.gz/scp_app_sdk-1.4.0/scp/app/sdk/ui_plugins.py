import json
import os
from typing import List, Dict

UI_PLUGINS_PATH = 'install/ui-plugins.json'


def get_ui_plugins(directory: str) -> List[Dict]:
    """
    Get UI plugins from the app manifest and load their configurations
    :param directory: Directory path of where the app/build is located
    :return: List of UI plugin configurations
    """
    plugin_path = os.path.join(directory, UI_PLUGINS_PATH)

    if not os.path.exists(plugin_path):
        print(f"[DEBUG] UI plugins file not found at: {plugin_path}")
        return []

    try:
        with open(plugin_path, 'r') as f:
            plugins = json.load(f)
            print(f"[DEBUG] Loaded UI plugins: {plugins}")
            return plugins
    except Exception as e:
        print(f"[ERROR] Failed to load UI plugins file {plugin_path}: {str(e)}")
        return []
