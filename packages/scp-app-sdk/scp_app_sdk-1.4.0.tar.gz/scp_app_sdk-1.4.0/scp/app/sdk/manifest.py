import jinja2
import marshmallow
import os
import pprint
import yaml

from scp.app.sdk.schema.manifest import Manifest as ManifestSchema

MANIFEST_FILE_NAME = 'manifest.yaml'


class InvalidManifestException(Exception):
    pass


def decode_manifest(file=None, dir=None):
    """
    Decode the manifest file
    :param file: Path of the manifest file
    :param dir: APP directory (don't mention the file in that case)
    :return: Manifest content
    """
    if dir:
        file = os.path.join(dir, MANIFEST_FILE_NAME)

    # Check if the manifest exist
    if not os.path.exists(file):
        raise InvalidManifestException(f'Manifest not found on this path {file}')

    # Validate the structure of the manifest
    try:
        with open(file, 'r') as f:
            data = yaml.safe_load(f)
    except yaml.YAMLError as e:
        raise InvalidManifestException(f'The manifest is not a valid YAML file')

    return data


def check_manifest(manifest):
    """
    Detect error in manifest.
    :param manifest: manifest content
    """
    try:
        return ManifestSchema().load(manifest)
    except marshmallow.ValidationError as e:
        raise InvalidManifestException(f'Some errors in the manifest:\n {pprint.pformat(e.messages)}')


def is_valid_manifest(manifest) -> bool:
    try:
        check_manifest(manifest)
    except InvalidManifestException as e:
        return False
    return True


def app_manifest():
    """
    Loads the application manifest

    :return: manifest content
    """
    script_directory = os.environ.get('SCP_APP_BUILD_DIR')
    manifest_file = os.path.join(script_directory, MANIFEST_FILE_NAME)

    with open(manifest_file, 'r') as file:
        manifest = yaml.safe_load(file)

    return manifest


def render_manifest(manifest_template, env):
    """
    Render manifest template (Jinja2 template). Evaluate the manifest with then env variables.
    :param manifest_template: Manifest content in Jinja2 format
    :param env: Environment variables
    :return: Manifest evaluated
    """
    template = jinja2.Template(manifest_template)
    rendered_content = template.render(env)
    return rendered_content
