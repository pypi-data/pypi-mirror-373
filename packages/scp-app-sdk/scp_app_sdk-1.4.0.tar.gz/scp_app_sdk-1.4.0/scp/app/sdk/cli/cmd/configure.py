import click

from scp.app.sdk.cli.scp_config import SCPConfig


def bootstrap_config():
    """
    Bootstrap the SCP App configuration.
    """
    config = SCPConfig()
    click.secho(f"SCP Appstore server: {config.get('scp_server')}", fg='blue')
    click.secho(f"SAM server: {config.get('sam_server')}", fg='blue')
    click.secho(f"JWT Token: {config.get('token')}", fg='blue')

    if click.confirm("👉 Are you ready to create or update the default configuration file?", default=True):
        configurator = SCPConfig()
        configurator.prompt_for_config()


@click.command()
def configure():
    """Interactive configuration for SCP App."""
    click.echo("""
📚  SCP APP Configure

✨ Tip: You can find the configuration file at `~/.scp-app-config` where your preferences are stored.
""")
    bootstrap_config()
