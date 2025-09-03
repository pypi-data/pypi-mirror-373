import click
import os
import sys

from scp.app.sdk.cli.documentation import doc_validate
from scp.app.sdk.validate import InvalidAppException, validate_app


def bootstrap_validate(dir):
    if not dir:
        dir = os.getcwd()
    if dir[0] != '/':
        dir = os.path.join(os.getcwd(), dir)

    # Do some checks
    try:
        validate_app(dir)
    except InvalidAppException as e:
        click.secho(f'❌ {e}', err=True, fg='red')
        sys.exit(-1)

    click.secho('✅ Your APP is valid', fg='green')
    click.secho(f"➡️ Next step:", fg='black', bold=True)
    click.secho(f"- If you have script in install/ then run your app locally with:", fg='black', bold=True)
    click.secho(f"  - `scp-app run [install|uninstall|migrate] {dir}`", fg='black', bold=True)
    click.secho(f"- Next build your app with `scp-app run build {dir}`", fg='black', bold=True)


@click.command()
@click.argument('dir', required=False, type=click.Path())
def validate(dir):
    """
    Check if the SCP APP is valid
    """
    if dir == "help" or not dir:  # that's the question 😶‍🌫️
        doc_validate()
        return
    bootstrap_validate(dir)
