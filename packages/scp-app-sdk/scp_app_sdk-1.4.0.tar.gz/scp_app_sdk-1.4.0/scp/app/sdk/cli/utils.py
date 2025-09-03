import click

filenames = [
    'manifest.yaml',
    'install/uninstall',
    'install/install',
    'install/migrate',
    'install/schema.json',
    'install/ui_plugin.json'
]

mapping_filenames = {
    "manifest.yaml": "Template for your app's metadata and configuration.",
    "install/schema.json": "JSON schema defining configuration validation.",
    "install/install": "Script executed during the install of the app.",
    "install/migrate": "Script for handling app migrations.",
    "install/uninstall": "Script executed to uninstall the app.",
    "install/ui_plugin.json": "Json file defining UI plugins for the app."
}


def confirm_with_help(message, help_text=None, default=False):
    """
    A confirm-like prompt with support for '?' to display help text.
    
    :param message: The question to ask.
    :param help_text: Optional help message shown when user types '?'.
    :param default: Default answer (True/False).
    :return: True if user confirms, False otherwise.
    """
    while True:
        default_hint = "Y/n" if default else "y/N"
        choice = click.prompt(
            f"{message} [{default_hint}/?]",
            default="y" if default else "n",
            show_default=False
        ).strip().lower()

        if choice in ("y", "yes"):
            return True
        elif choice in ("n", "no"):
            return False
        elif choice in ("?", "h", "help"):
            if help_text:
                click.echo(help_text)
            else:
                click.echo("ℹ️ No extra information available.\n")
        else:
            click.echo("❌ Invalid choice. Please answer with 'y', 'n', or '?'.\n")


def confirm_or_help(message, help_text=None):
    """
    A strict yes/no/? prompt (no defaults).
    
    :param message: The question to ask.
    :param help_text: Optional help message shown when user types '?'.
    :return: True if 'y', False if 'n'.
    """
    while True:
        choice = click.prompt(
            f"{message} [y/n/?]",
            show_default=False
        ).strip().lower()

        if choice in ("y", "yes"):
            return True
        elif choice in ("n", "no"):
            return False
        elif choice in ("?", "h", "help"):
            if help_text:
                click.echo(help_text)
            else:
                click.echo("ℹ️ No extra information available.\n")
        else:
            click.echo("❌ Invalid choice. Please answer with 'y', 'n', or '?'.\n")
