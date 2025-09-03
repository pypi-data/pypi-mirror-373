import click

bar_length = 50
from scp.app.sdk.cli.utils import mapping_filenames, filenames
from scp.app.sdk.cli.config import default_doc_server


def ops_documentation(step, bypass_prompt=False):
    mapping = {
        "create": [doc_create, 'Application creation'],
        "build": [doc_build, 'Build creation'],
        "validate": [doc_validate, 'Validate creation'],
        "run": [doc_run, 'Run creation'],
        "publish": [doc_publish, 'Publish creation'],
    }
    if bypass_prompt:
        mapping[step][0]()
        return

    ans = click.confirm(f"Do you want additional documentation about the {mapping[step][1]}?", default=False)
    if ans:
        mapping[step][0]()


def doc_create():
    def manifest():
        click.echo(
            "\n📜 Additional documentation about the manifest.yaml \n\n"
            "The manifest file is the core of your app, defining its metadata, actions, and icons.\n"
            "You can edit it to customize your app's behavior and appearance.\n"

            "Key sections of the manifest:\n"
            "- `id`: A unique identifier for your app. It should be in reverse domain name notation (e.g., com.example.myapp).\n"
            "- `name`: The display name of your app.\n"
            "- `description`: A brief description of what your app does.\n"
            "- `version`: The version of your app, following semantic versioning (e.g., 1.0.0).\n"
            "- `authors`: A list of authors or contributors to the app.\n"
            "- `icons`: A list of icons representing your app in various sizes and formats.\n"
            "- `tags`: Keywords associated with your app to help users find it.\n"
            "- `csfe`: Configuration settings for the app, such as SIP accounts or other parameters.\n"
            "- `actions`: Defines the main entry points of your app, including scripts to run and parameters they accept.\n\n"
            "For more details on each field and how to structure your manifest, refer to the documentation at:\n"
            f"👉 {default_doc_server}/apps/cli\n\n"
        )

    def install():
        click.echo(
            "\n📜 Additional documentation about the install script \n\n"
            "The `install/install` script is used to set up the configuration of your app. "
            "You can define there a CSFE configuration to set, for example:\n"
            "- SIP username and password\n"
            "- Proxy to use\n"
            "- Other configuration parameters needed by your app.\n"
        )

    def migrate():
        click.echo(
            "\n📜 Additional documentation about the migrate script \n\n"
            "The `install/migrate.py` script is used to handle migrations when your app is updated. "
            "You can define there how to handle changes in the app's configuration or data. "
            "For example, you can add new fields to the configuration or remove old fields that no longer match your needs.\n"
        )

    def uninstall():
        click.echo(
            "\n📜 Additional documentation about the uninstall script \n\n"
            "The `install/uninstall` script is used to clean up the app's configuration when it is uninstalled.\n"
        )

    def schema():
        click.echo(
            "\n📜 Additional documentation about the schema.json \n\n"
            "JSON Schema standard is used as a enabling tools to validate its structure and contents accordingly.\n"
            "The schema file defines the configuration parameters that users need to provide before installing the app.\n"
            "It ensures that the input provided by users is valid and meets the required criteria.\n"
        )

    click.echo(
        "\n📚 Additional documentation for APP creation\n\n"
        "If you arrived here, you probably want to know more about how to customize your APP.\n\n"

        "In the root of your newly created APP, you will find multiple files:\n"
    )

    for file in filenames:
        if file in mapping_filenames:
            click.echo(f"  - {file}: {mapping_filenames[file]}")

    manifest()
    install()
    migrate()
    uninstall()
    schema()
    click.echo("")
    click.echo(
        "📒 The `install` directory contains scripts that will be executed during the app's lifecycle\n\n"

        "For more information about app creation, you can refer to the documentation at:\n"
        f"👉 {default_doc_server}/apps/cli\n\n"
    )


def doc_build():
    click.echo(
        "\n📚 Additional documentation for APP build\n\n"
        "If you arrived here, you probably want to know more about the 'build' of APPs.\n\n"

        "The build process is responsible for packaging your app into a format that can be deployed and run on the SCP platform.\n"
        "It typically will bundle your app in to a '.sap' file, which contains all the necessary files and metadata for your app.\n\n"

        "The content of the build is what you have defined during the creation of your app, such as the manifest, install scripts, and other resources.\n\n"
    )


def doc_validate():
    click.echo(
        "\n📚 Additional documentation for APP validation\n\n"
        "If you arrived here, you probably want to know more about the 'validation' of APPs.\n\n"

        "The validation process checks if your app meets the required standards and guidelines for SCP apps.\n"
        "It ensures that your app is correctly structured, has the necessary metadata, and follows best practices.\n\n"

        "For more information about app validation, you can refer to the documentation at:\n"
        f"👉 {default_doc_server}/apps/cli\n\n"
    )


def doc_run():
    click.echo(
        "\n📚 Additional documentation for APP run\n\n"
        "If you arrived here, you probably want to know more about running your app locally.\n\n"

        "The run command allows you to test your app in a local environment before building it to the SCP platform.\n"
        "It simulates the execution of your app, allowing you to verify its behavior and functionality.\n\n"

        "For more information about running apps, you can refer to the documentation at:\n"
        f"👉 {default_doc_server}/apps/cli\n\n"
    )


def doc_publish():
    click.echo(
        "\n📚 Additional documentation for APP publish\n\n"
        "If you arrived here, you probably want to know more about publishing your app to the SCP platform.\n\n"

        "The publish command is used to release your app to the SCP store, making it available for users to install and use.\n"
        "It packages your app and uploads it to the SCP platform, where it can be discovered and installed by others.\n\n"

        "For more information about publishing apps, you can refer to the documentation at:\n"
        f"👉 {default_doc_server}/apps/cli\n\n"
    )
