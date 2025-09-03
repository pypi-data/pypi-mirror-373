import click
import requests
import urllib3
from urllib.parse import urlparse

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)  # to remove when going to production


def _server_reachable(server, token=None):
    headers = {}
    if token:
        headers['Authorization'] = f"Bearer {token}" if not 'Bearer' in token else token

    try:
        r = requests.get(f"{server}/api/v1/version", headers=headers, verify=False, timeout=5)
    except Exception as e:
        print(f"Error connecting to server {server}: {e}")
        return False

    return r.status_code == 200


def scp_app_store_server(server=None, token=None):
    if not server:
        click.echo("⚠️  No server provided.")
        return False

    parsed = urlparse(server)

    if not parsed.scheme:
        server = "https://" + server
        parsed = urlparse(server)

    netloc = parsed.netloc if parsed.netloc else parsed.path
    server = f"https://{netloc}"

    server = server.rstrip("/")

    if not _server_reachable(server, token):
        click.echo(f"⚠️  Server {server} is not reachable, url or token invalid please try again.")
        return False

    return server
