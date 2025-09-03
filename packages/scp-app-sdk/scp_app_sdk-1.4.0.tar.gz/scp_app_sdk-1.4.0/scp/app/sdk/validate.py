import json
import os

from scp.app.sdk.manifest import check_manifest as m_check_manifest, decode_manifest, MANIFEST_FILE_NAME


class InvalidAppException(Exception):
    pass


def check_manifest(dir):
    manifest_file = os.path.join(dir, MANIFEST_FILE_NAME)

    if not os.path.isfile(manifest_file):
        raise InvalidAppException(f"Manifest file not found at {manifest_file}")

    manifest = decode_manifest(manifest_file)
    m_check_manifest(manifest)
    return manifest


def check_action(actions, dir):
    if not actions:
        return

    def _check_script(path):
        script_path = os.path.join(dir, path)
        if not os.path.exists(script_path):
            raise InvalidAppException(f'Missing script {script_path}')
        if not os.access(script_path, os.X_OK):
            raise InvalidAppException(f'This script is not executable {script_path}')

    def _check_json_schema(path):
        schema_path = os.path.join(dir, path)
        if not os.path.exists(schema_path):
            raise InvalidAppException(f'Missing json schema {schema_path}')
        # TODO check if it's a valid json schema

    # On install check
    on_install = actions.get('onInstall')
    if on_install:
        _check_script(on_install.get('script'))
        _check_json_schema(on_install.get('schema'))

    # On uninstall check
    on_uninstall = actions.get('onUninstall')
    if on_uninstall:
        _check_script(on_uninstall.get('script'))

    # On migrate check
    on_migrate = actions.get('onMigrate')
    if on_migrate:
        _check_script(on_migrate.get('script'))


def check_icon(icons, dir):
    if icons:
        for icon in icons:
            src = icon.get('src')
            icon_path = os.path.join(dir, src)
            if not os.path.exists(icon_path):
                raise InvalidAppException(f'Missing icon on path {icon_path}')


def check_ui_plugins(dir):
    """
    Check if UI plugins file exists and is valid
    :param dir: App directory
    """
    plugin_path = os.path.join(dir, UI_PLUGINS_PATH)
    if os.path.exists(plugin_path):
        try:
            with open(plugin_path, 'r') as f:
                json.load(f)  # Validate JSON format
        except json.JSONDecodeError:
            raise InvalidAppException(f'Invalid UI plugins JSON file: {plugin_path}')


def validate_app(dir):
    manifest = check_manifest(dir)
    check_action(manifest.get('actions'), dir)
    check_icon(manifest.get('icons'), dir)
