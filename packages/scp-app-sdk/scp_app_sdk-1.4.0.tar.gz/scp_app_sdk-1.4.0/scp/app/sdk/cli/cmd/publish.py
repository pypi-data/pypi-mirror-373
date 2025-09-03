import click
import json
import os
import sys

from scp.app.sdk.build import publish_build, AppPublishException
from scp.app.sdk.cli.documentation import doc_publish
from scp.app.sdk.cli.scp_config import SCPConfig


def bootstrap_publish(file, server, token):
    config = SCPConfig()
    server = server if server else config.get('scp_server')
    token = token if token else config.get('token')

    if not file.endswith('.sap'):
        click.echo('❌ Error to publish the APP: The app must end by .sap')
        sys.exit()

    if not server or server == '' or not server.startswith("https") or not token:
        click.echo('⚠️ Server invalid or incorrect, starting configuration module.')
        config.prompt_for_config(prompt_sam=False)

    if not token:
        click.echo("⚠️ No token is configured.")
        config.prompt_and_set('token', 'token', is_url=False)
        token = config.get('token')
    while True:
        try:
            print(f"⌛ Trying to publish on SCP Appstore server: {server}")
            publish_build(file, server, token)
            break
        except AppPublishException as e:
            click.secho(f"❌ Error to publish the APP on the SCP APP store: {e}.", fg='red')
            if e.status_code == 401:
                click.echo("⚠️ Server sent a 401, please refresh your JWT token.")
                config.prompt_and_set('token', 'token', is_url=False)
                token = config.get('token')
            else:
                click.echo('⚠️ Server respond with an error.')
                data = json.loads(e.response_body)
                for error in data.get("errors", []):
                    title = error.get("title")
                    detail = error.get("detail")
                    if title and detail:
                        click.echo(f"{title}: {detail}")
                sys.exit(-1)

    click.secho(f'✅ Build {os.path.basename(file)} published on {server}', fg='green')


@click.command()
@click.argument('file', required=False, type=click.Path())
@click.option('--server', default=None, help='SCP APP store server URL')
@click.option('--token', default=None, help='JWT Token.')
def publish(file, server, token):
    """
    Publish your SCP APP build
    """
    if file == "help" or not file:
        doc_publish()
        return
    bootstrap_publish(file, server, token)
