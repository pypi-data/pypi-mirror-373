import click
import json
import os
import re
import subprocess
import sys
from urllib.parse import urlparse

from scp.app.sdk.cli.config import default_doc_server
from scp.app.sdk.cli.documentation import doc_create
from scp.app.sdk.cli.scp_config import SCPConfig
from scp.app.sdk.cli.utils import mapping_filenames, confirm_with_help, confirm_or_help
from scp.app.sdk.create import create_app as create_app_on_store, AppCreationException
from scp.app.sdk.template import create_app


def is_ui_plugin():
    help_text = (
        "🗒️ Information:\n"
        "   • UI Plugin are microfrontend manifest.\n"
        "   • [TODO].\n"
    )

    return confirm_with_help(
        f"👉 Would you like to have ConnectMe UI plugin(s)?",
        help_text=help_text,
        default=False
    )


def ask_registration():
    help_text = (
        "🗒️ Information:\n"
        "   • This application requires a unique ID (UUID) to continue.\n"
        f"   • You can obtain one by registering your application in the SCP Appstore Web UI.\n"
        "   • Alternatively, we can handle the registration using your default configuration.\n"
    )

    return confirm_with_help(
        f"👉 Would you like to register your application remotely?",
        help_text=help_text,
        default=True
    )


def is_valid_url(url: str) -> bool:
    """Check if a URL has a valid scheme and netloc."""
    parsed = urlparse(url)
    return all([parsed.scheme in ("http", "https"), parsed.netloc])


def get_csfe_info():
    csfe_help = (
        "🗒️ Information:\n"
        "   • A CSFE is a Communication Server Front End.\n"
        "   • It allows you to adapt Smartflow to a defined Communication Server\n"
        "   • More info at: example.com/csfe\n"
    )
    if confirm_with_help("👉 Do you want a telephony connector (CSFE)?", help_text=csfe_help, default=False):
        csfe_id = click.prompt("👉 CSFE ID", type=str)

        while True:
            csfe_url = click.prompt("👉 CSFE URL", type=str)
            if is_valid_url(csfe_url):
                break
            else:
                click.echo("❌ Invalid URL. Please enter a valid URL starting with http:// or https://")

        csfe = dict(id=csfe_id, url=csfe_url)
        return csfe
    return None


def get_icon():
    choice = click.prompt(
        "👉 Choose an icon option",
        type=click.Choice(["none", "default", "custom"], case_sensitive=False),
        default="default"
    )

    if choice == "none":
        icons = []
        click.echo("No icon will be used.")
    elif choice == "default":
        icons = ["icon.png"]
        click.echo("Using default Dstny icon: icon.png")
    else:  # custom
        while True:
            icon = click.prompt("Icon path", type=click.Path(exists=True, file_okay=True, dir_okay=False))
            icon = os.path.abspath(icon)

            if not os.path.exists(icon):
                click.secho(f"❌ Icon file {icon} does not exist.", fg='red')
                continue
            if not icon.endswith(".png"):
                click.secho("❌ Icon must be a PNG", fg='red')
                continue
            if os.path.getsize(icon) > 1_048_576:  # max: 1 MB in bytes
                click.secho("❌ Icon must be smaller than 1 MB", fg='red')
                continue

            icons = [icon]
            click.echo(f"Using custom icon: {icon}")
            break

    return icons


def _requirement():
    try:
        import click
        import jinja2
    except ImportError:
        print("Please install required packages:\n\n\tpip install click jinja2.\n")
        sys.exit(1)


def get_input(app_name=None):
    # APP information
    click.secho("🏗️ APP information", bold=True)
    if app_name:
        click.echo(f"👉 App name: {app_name}")

    else:
        app_name = click.prompt('👉 App name', type=str)
    while True:
        if re.match(r"[A-z0-9]+", app_name):
            break
        click.secho("Invalid name: it should be alphanumeric characters in lower case.", fg='red')
        app_name = click.prompt('Name', type=str)

    config = SCPConfig()
    server = config.get('scp_server')  # scp-app-store.chefhub.smartflowagent.net
    if not server or server == '' or not server.startswith("https"):
        click.echo('⚠️ Server invalid or incorrect, starting configuration module.')
        config.prompt_for_config(prompt_sam=False)

    if ask_registration():
        click.echo("🔥 Creating a new APP...")
        token = config.get('token')
        if not token:
            click.echo("⚠️ No token is configured.")
            config.prompt_and_set('token', 'token', is_url=False)
            token = config.get('token')
        click.echo(f"🌎 Your current SCP server is: {server}")
        config.prompt_and_set('scp_server', 'SCP Appstore server', is_url=True)
        server = config.get('scp_server')
        while True:
            try:
                app_id = create_app_on_store(
                    remote_server=server,
                    name=app_name,
                    id=None,
                    token=config.get('token')
                )
                break
            except AppCreationException as e:
                click.secho(f"❌ Error to create an APP on the SCP APP store: {e}.", fg='red')
                if e.status_code == 401:
                    click.echo("⚠️ Server sent a 401, please refresh your JWT token or update scp-app-store url.")
                    config.prompt_for_config(prompt_sam=False)
                else:
                    click.echo('⚠️ Server respond with an error.')
                    data = json.loads(e.response_body)
                    print(data)
                    for error in data.get("errors", []):
                        title = error.get("title")
                        detail = error.get("detail")
                        click.echo(f"{title}: {detail}")
                    sys.exit(-1)

    else:
        app_id = click.prompt('👉 APP ID', type=str)

    app_description = click.prompt('👉 Description', type=str)

    # choose file to build
    install_files = []
    if confirm_with_help(
            "👉 Do you want to include installation script (install/uninstall)?",
            help_text="   • Includes 'install' and 'uninstall'.\n"
                      "   • The install script runs when the user installs the app.\n"
                      "   • The uninstall script runs when the user removes the app.",
            default=False
    ):
        install_files = ["install", "uninstall", "schema.json"]
        icon = "icon.png"

        if confirm_or_help(
                "   • Should users provide input (e.g., configuration details) before installation?",
                help_text="     → This will create an example `schema.json` at `install/schema.json`.\n"
                          "     → An example `schema.json` will be created at `install/schema.json`.\n"
                          "     → It allows specify information for the user to input before installing the app.",
        ):
            install_files[install_files.index("schema.json")] = "example_schema.json"

        if confirm_or_help(
                "   • Do you also want to add a migration script (for app upgrades)?",
                help_text="     → A migration script will be generated at `install/migrate`.\n"
                          "     → The migration will be during upgrade of the app.\n"
                          "     → It allows to handle the data to migrate and ensure the upgrade will be smooth."
        ):
            install_files.append("migrate")

    else:
        click.echo("No installation files will be generated.")

    # icons ? 
    icons = get_icon()

    # csfe ? 
    csfe = get_csfe_info()

    # ui plugin ? 
    ui_plugin = is_ui_plugin()

    click.secho("\n✅ Setup complete!", fg="green")
    click.echo("")

    # Destination directory
    app_dir_name = app_name.lower()
    project_dirs = [
        f"{os.path.dirname(os.getcwd())}/{app_dir_name}",
        f"{os.getcwd()}/{app_dir_name}",
        f"{os.path.expanduser('~')}/{app_dir_name}",
        f"/tmp/{app_dir_name}",
    ]
    choice = {str(i + 1): v for i, v in enumerate(project_dirs)}
    choice['c'] = "Custom directory"
    c = '\n '.join([f'[{k}] {v}' for k, v in choice.items()])
    project_choose = click.prompt(
        f"Select the directory to create your app, be careful the directory will be overwritten ! \n {c}\nChoose",
        type=click.Choice(list(choice.keys()))
    )
    if project_choose == 'c':
        project_dir = click.prompt("App Directory", type=click.Path())
    else:
        project_dir = project_dirs[int(project_choose) - 1]

    # Dev information
    click.echo("")
    click.secho("🪪 Developer Information", bold=True)
    dev_username = subprocess.run(["git", "config", "user.name"], stdout=subprocess.PIPE).stdout.strip().decode()
    dev_email = subprocess.run(["git", "config", "user.email"], stdout=subprocess.PIPE).stdout.strip().decode()
    if not dev_username:
        dev_username = click.prompt('Your name', type=str)
    else:
        click.secho(f"Your name: {dev_username}")
    if not dev_email:
        dev_email = click.prompt('Your e-mail', type=str)
    else:
        click.secho(f"Your e-mail: {dev_email}")

    # Returned information
    data = dict(
        name=app_name,
        id=app_id,
        description=app_description,
        directory=project_dir,
        author=dict(
            name=dev_username,
            email=dev_email
        ),
        install_files=install_files,
        icons=icons
    )

    if csfe:
        data["csfe"] = csfe
    if ui_plugin:
        data['ui_plugins'] = ['ui_plugin.json']

    return data


def bootstrap_create(app_name=None):
    _requirement()

    data = get_input(app_name)
    app_dir = data['directory']
    click.echo("")
    click.secho(f"📂 Generating app...", bold=True)
    installed_files = create_app(**data)

    ### faire un mapping avec dict pour expliquer le bazard 
    for file in installed_files:
        if file in mapping_filenames:
            click.echo(f"  - {file}: {mapping_filenames[file]}")
    click.secho(f"✅ App created successfully at {app_dir}.", fg='green', bold=True)
    click.echo("")
    click.secho(f"➡️ Next steps:", fg='black', bold=True)
    click.secho(f"- Edit your app at {app_dir} to fit your need", fg='black', bold=True)
    click.secho(f"- Validate your app with `scp-app validate {app_dir}`", fg='black', bold=True)
    click.secho(f"👉 more info here: {default_doc_server}/apps", fg='blue', bold=True)
    click.echo("")


@click.command()
@click.argument("name", required=False)
def create(name=None):
    """
    Create a new SCP APP
    """
    if name and name == "help":
        doc_create()
        return
    bootstrap_create(app_name=name)
