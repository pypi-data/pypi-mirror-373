from marshmallow import Schema, fields, validate


class ActionOnInstall(Schema):
    schema = fields.String(
        description="Path to the json schema in the zip file",
        required=False,
        example='install/schema.json'
    )
    script = fields.String(
        description="Path (relative patch in the zip file) to the install script executed when the end user setup the app.",
        required=True,
        example='install/install.py'
    )


class ActionOnRemove(Schema):
    script = fields.String(
        description="Path (relative patch in the zip file) to the uninstall script executed when the end user remove the app.",
        required=True,
        example='install/uninstall.py'
    )


class ActionOnMigrate(Schema):
    script = fields.String(
        description="Path (relative patch in the zip file) to the migration script executed when the end user migrates/upgrades the app.",
        required=True,
        example='install/migrate'
    )


class Actions(Schema):
    onInstall = fields.Nested(
        ActionOnInstall,
        description="Action during the installation of the APP by the end user",
        required=False
    )
    onUninstall = fields.Nested(
        ActionOnRemove,
        description="Action during the uninstall of the APP by the end user",
        required=False
    )
    onMigrate = fields.Nested(
        ActionOnMigrate,
        description="Action during the migration of the APP by the end user",
        required=False
    )


class Author(Schema):
    name = fields.String(
        description="Author name",
        required=True,
        example='John Doe'
    )
    email = fields.String(
        description="Author email",
        required=True,
        example='john.doe@dstny.com'
    )


class Icon(Schema):
    src = fields.String(
        description="Icon path",
        required=True,
        example='images/icon.png',
        default='images/icon.png'
    )
    type = fields.String(
        description="Encoding type",
        required=True,
        example="image/png",
        validate=validate.OneOf(
            ["image/png"]  # add more type if needed
        )
    )


class CSFE(Schema):
    id = fields.String(
        description="CSFE ID",
        required=True,
        example='dstny'
    )
    uri = fields.Url(
        description="URL to CSFE API",
        required=True,
        example='http://dstny.csfe:8980'
    )


class UiPlugin(Schema):
    src = fields.String(
        description="Path to the UI plugin manifest file",
        required=True,
        example='ui/plugin-manifest.json'
    )
    name = fields.String(
        description="Name of the UI plugin",
        required=True,
        example='my-awesome-plugin'
    )


class Manifest(Schema):
    manifest_version = fields.String(
        description="Version of the manifest",
        required=True,
        example='1.0.0',
        validate=validate.Regexp(
            r'^\d+\.\d+\.\d+$',
            error="Invalid version format, must be X.Y.Z"
        )
    )

    id = fields.String(
        description="The unique identifier of the APP. It will be given to you during the APP creation on the SCP APP store",
        required=True,
        example='e4c9f92e-93e2-4920-81d5-3925de1a8e90'
    )

    name = fields.String(
        description="The name of APP. It should be unique and match the APP name.",
        required=True,
        example='Dstny APP'
    )

    description = fields.String(
        description="APP description",
        required=False,
        example='This is the first Dstny APP'
    )

    version = fields.String(
        description="APP version",
        required=True,
        example='1.0.0'
    )

    authors = fields.List(
        fields.Nested(Author),
        description="List of authors",
        required=True
    )
    icons = fields.List(
        fields.Nested(Icon),
        description="List of icons",
    )
    tags = fields.List(
        fields.String(
            description="Tag",
            required=True,
            example='dstny'
        ),
        description="List of tags",
        required=True
    )
    csfe = fields.List(
        fields.Nested(CSFE),
        description="CSFE used for the APP",
        required=False
    )

    actions = fields.Nested(
        Actions,
        description="Action performed during the APP events",
        required=False,
    )

    ui_plugins = fields.List(
        fields.Nested(UiPlugin),
        description="List of UI plugins",
        required=False
    )
