import click
import configparser
import os

from scp.app.sdk.cli.config import default_scp_server, default_sam_server
from scp.app.sdk.cli.server import scp_app_store_server
from scp.app.sdk.cli.utils import confirm_with_help


class SCPConfig:
    """Manages SCP App configuration stored in ~/.scp-app-config"""

    DEFAULTS = {
        'scp_server': default_scp_server,
        'sam_server': default_sam_server,
        'token': ''
    }

    def __init__(self):
        self.config_path = os.path.expanduser("~/.scp-app-config")
        self.config_dir = os.path.dirname(self.config_path)
        self.config = configparser.ConfigParser()

        os.makedirs(self.config_dir, exist_ok=True)

        if not os.path.exists(self.config_path):
            self.config['DEFAULT'] = self.DEFAULTS
            self.save()
        else:
            self.config.read(self.config_path)

    def get(self, key):
        return self.config['DEFAULT'].get(key, '')

    def set(self, key, value):
        self.config['DEFAULT'][key] = value
        self.save()

    def save(self):
        with open(self.config_path, 'w') as f:
            self.config.write(f)

    def check_servers(self, check_scp=True, check_sam=True):
        click.echo("⌛ Testing server connections...")
        scp_server = self.get('scp_server')
        sam_server = self.get('sam_server')
        token = self.get('token')

        if check_scp and not scp_app_store_server(scp_server, token):
            click.secho("❌ SCP Appstore server unreachable", fg="red")
            return False

        if check_sam and not scp_app_store_server(sam_server, token):
            click.secho("❌ SAM server unreachable", fg="red")
            return False

        return True

    def prompt_and_set(self, key, label, is_url):
        if confirm_with_help(
                f"👉 Do you want to edit {label} ?",
                help_text="   • This will override the default configuration.\n"
                          "   • You should change only if you know what you're doing\n",
                default=False
        ):
            value = click.prompt(f"👉 Enter your {label}", type=str)
            if is_url:
                self.set(key, value.rstrip("/"))
            else:
                self.set(key, value)
            click.secho(f"✅ {label} saved successfully!", fg="green")

    def prompt_for_config(self, prompt_scp=True, prompt_sam=True):
        token = click.prompt("👉 Enter your JWT token", type=str, hide_input=True)
        self.set('token', token)

        if prompt_scp:
            self.prompt_and_set("scp_server", "SCP Appstore server", is_url=True)
        if prompt_sam:
            self.prompt_and_set("sam_server", "SAM server", is_url=True)

        for _ in range(3):
            if self.check_servers(check_scp=prompt_scp, check_sam=prompt_sam):
                click.secho("\n✅ Configuration saved successfully!", fg="green", bold=True)
                return
            click.echo("\n❌ Invalid configuration. Please try again.\n")
            self.prompt_for_config(prompt_scp, prompt_sam)

        raise click.ClickException("Configuration failed after multiple attempts.")
