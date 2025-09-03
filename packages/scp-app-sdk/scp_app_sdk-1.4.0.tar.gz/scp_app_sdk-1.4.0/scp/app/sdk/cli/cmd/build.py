import click
import os
import shutil
import sys
import uuid
from pathlib import Path

from scp.app.sdk.build import build_app, BuildAppException, render_app
from scp.app.sdk.cli.documentation import doc_build
from scp.app.sdk.validate import validate_app, InvalidAppException


def bootstrap_build(app_dir=None, build_dir=None, env=None):
    if not app_dir:
        app_dir = os.getcwd()
    if app_dir[0] != '/':
        app_dir = os.path.join(os.getcwd(), app_dir)
    if not os.path.isdir(app_dir):
        click.secho(f'❌ Directory {app_dir} does not exist', bold=True, fg='red')
        sys.exit(-1)
    if not build_dir:
        build_dir = os.path.join(app_dir, 'build')

    # Render the APP
    tmp_app_dir = os.path.join(build_dir, f"tmp{str(uuid.uuid4())}")
    try:
        render_app(app_dir, tmp_app_dir, env)
    except BuildAppException as e:
        click.secho(f'❌ {e}', err=True, fg='red')
        shutil.rmtree(tmp_app_dir)
        sys.exit(-1)

    # Validate the APP
    try:
        validate_app(tmp_app_dir)
    except InvalidAppException as e:
        click.secho(f'❌ APP validation issue\n {e}', err=True, fg='red')
        shutil.rmtree(tmp_app_dir)
        sys.exit(-1)

    # Build the APP
    try:
        build_path = build_app(source_dir=tmp_app_dir, destination_dir=build_dir)
    except BuildAppException as e:
        click.secho(f'❌ {e}', err=True, fg='red')
        shutil.rmtree(tmp_app_dir)
        sys.exit(-1)

    shutil.rmtree(tmp_app_dir)
    click.secho(f'✅ APP build created: {build_path}', fg='green')
    click.secho(f"➡️ Next step:", fg='black', bold=True)
    click.secho(f"- Publish your app with `scp-app publish {build_path}`", fg='black', bold=True)


@click.command()
@click.argument('app_dir', required=False, type=click.Path())
@click.argument('build_dir', required=False, type=click.Path())
@click.option("--env", default=None, show_default=True, help="Specify the environment (default: local)")
def build(app_dir, build_dir, env):
    """
    Build the SCP APP
    """
    if (app_dir in ("help", None) and build_dir is None) or (build_dir == "help"):
        doc_build()
        return
    bootstrap_build(app_dir, build_dir, env)
