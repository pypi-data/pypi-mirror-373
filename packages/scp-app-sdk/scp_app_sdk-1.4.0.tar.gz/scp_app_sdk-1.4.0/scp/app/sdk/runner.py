import asyncio
import json
import os
import sys

from scp.app.sdk.manifest import MANIFEST_FILE_NAME, decode_manifest


class AdvancedHTTPError(Exception):
    def __init__(self, status=500, title=None, detail=None):
        self.status = status
        self.title = title or "Error"
        self.detail = detail
        super().__init__(f"{status} {title}: {detail}")


class RunScriptException(AdvancedHTTPError):

    def __init__(self, status=500, message=None):
        super(RunScriptException, self).__init__(status=status, title="Run script error", detail=message)


class NoScriptException(RunScriptException):
    pass


async def _run_script(directory: str, script_path: str, inputs=None, env=None, args=None):
    """
    Run a script on the build.
    :param directory: The directory to the build
    :param script_path: Path of the script to run.
    :param inputs: Dictionary of inputs to pass to the script.
    :param env: Dictionary of environment variables to pass to the script.
    :param args: Dictionary of arguments to pass to the script.
    :return: output of the script
    """
    e = os.environ.copy()
    e['SCP_APP_BUILD_DIR'] = directory
    if env:
        e.update(env)

    if not os.path.exists(script_path):
        raise RunScriptException(
            message='Install folder does not exist'
        )

    cmd = ' '.join([script_path] + (args if args else []))
    print(f"Execution script: {script_path} with args: {args} with inputs: {inputs}")
    process = await asyncio.create_subprocess_shell(
        cmd=cmd,
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        env=e
    )
    try:
        stdout, stderr = await process.communicate(input=json.dumps(inputs).encode())
    except Exception as e:
        raise RunScriptException(message=f'Unexpected run script error: {str(e)}')

    if process.returncode != 0:
        raise RunScriptException(
            message=f'Run script failed with return code={process.returncode}\n {stderr}\n{stdout}'
        )

    return stdout


async def _run_manifest_script(actions, directory, input=None, manifest=None, env=None, args=None):
    if not manifest:
        print(f"manifest filename: {MANIFEST_FILE_NAME}")
        print(f"directory: {directory}")
        manifest = decode_manifest(os.path.join(directory, MANIFEST_FILE_NAME))

    if 'actions' not in manifest or actions not in manifest['actions']:
        raise NoScriptException(message=f'Action not found in manifest: {actions}')

    install_path = os.path.join(directory, manifest['actions'][actions]['script'])
    out = await _run_script(directory, str(install_path), input, env, args)
    return out


async def run_install(directory, input, manifest=None, env=None):
    """
    Run install script of the build.
    :param directory: Directory path of where the app/build is located
    :param input: Dictionary of inputs to pass to the script.
    :param manifest: App manifest (not mandatory)
    :param env: Additional environment variables
    :return: output of the script
    """
    # TODO It should be nice to have the migration version as argument
    return await _run_manifest_script('onInstall', directory, input, manifest=manifest, env=env)


async def run_uninstall(directory, manifest=None, input=None, env=None):
    """
    Run install script of the build.
    :param directory: Directory path of where the app/build is located
    :param manifest: App manifest (not mandatory)
    :param env: Additional environment variables
    :return: output of the script
    """
    # TODO It should be nice to have the migration version as argument
    return await _run_manifest_script('onUninstall', directory, input, manifest=manifest, env=env)


async def run_migrate(directory, input, manifest=None, env=None):
    """
    Run migration script of the build.
    :param directory: Directory path of where the app/build is located
    :param input: Dictionary of inputs to pass to the script.
    :param manifest: App manifest (not mandatory)
    :param env: Additional environment variables
    :return: output of the script
    """
    if not manifest:
        manifest = decode_manifest(os.path.join(directory, MANIFEST_FILE_NAME))
    if manifest is None or 'actions' not in manifest or 'onMigrate' not in manifest['actions']:
        # no migrate script found in manifest: return unmodified configuration (input)
        return input
    # TODO It should be nice to have the migration version as argument
    return json.loads(await _run_manifest_script('onMigrate', directory, input, manifest=manifest, env=env))
