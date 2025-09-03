#!/usr/bin/env python
# coding: utf-8

from __future__ import absolute_import, division, print_function

import click

from scp.app.sdk.cli.cmd import build
from scp.app.sdk.cli.cmd import configure
from scp.app.sdk.cli.cmd import create
from scp.app.sdk.cli.cmd import publish
from scp.app.sdk.cli.cmd import run
from scp.app.sdk.cli.cmd import validate
from scp.app.sdk.cli.config import default_doc_server

CONTEXT_SETTINGS = dict(max_content_width=120)


@click.group(
    context_settings=CONTEXT_SETTINGS,
    help=f"""
🚀 SCP APP CLI – Your assistant to create, build, test, and publish SCP Apps.

\b
Configure SCP APP CLI:
    scp-app configure               → Configure default value to use.

\b
Typical workflow:
    scp-app create                  → Start a new SCP App project.
    scp-app validate                → Verify your app meets SCP standards.
    scp-app run                     → Run your app locally for testing.
    scp-app build /your/app/dir     → Compile & bundle your app.
    scp-app publish /dir/app.sap    → Release your app to the SCP store.

\b
Get help:
    scp-app create help             → Get help on creating an app.
    scp-app validate help           → Get help on validating an app.
    scp-app build help              → Get help on building an app.
    scp-app run help                → Get help on running an app.
    scp-app publish help            → Get help on publishing an app.

\b
For more information, you can refer to the documentation at:
👉 {default_doc_server}/apps/cli
""",
)
def cli():
    pass


cli.add_command(configure.configure)
cli.add_command(create.create)
cli.add_command(validate.validate)
cli.add_command(build.build)
cli.add_command(publish.publish)
cli.add_command(run.run)

if __name__ == "__main__":
    cli()
