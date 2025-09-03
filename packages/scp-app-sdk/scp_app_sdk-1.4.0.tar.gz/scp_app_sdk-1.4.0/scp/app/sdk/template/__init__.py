import jinja2
import mimetypes
import os
import shutil
from pathlib import Path


def generate_project(context, dest_dir, src_dir=None):
    if not src_dir:
        src_dir = f'{__file__.rsplit("/", 1)[0]}/template'

    # Remove existing destination directory
    try:
        shutil.rmtree(dest_dir)
    except FileNotFoundError:
        pass

    env = jinja2.Environment(loader=jinja2.FileSystemLoader(src_dir))
    installed_files = []
    manifest_template_path = None
    manifest_dest_file = None
    icons = context.get('icons')
    install_files = context.get('install_files')
    ui_plugins = context.get('ui_plugins')

    # copy all files except manifest
    for root, _, filenames in os.walk(src_dir):
        for filename in filenames:
            # skip manifest for now
            if filename in ("manifest.yaml.j2", "manifest.yaml"):
                manifest_template_path = os.path.relpath(os.path.join(root, filename), src_dir)
                manifest_dest_file = os.path.join(dest_dir, filename.replace(".j2", ""))
                continue

            src_file_path = os.path.join(root, filename)
            src_file = "{}/{}".format(root.replace(src_dir, ""), filename)
            # strip leading slashes to avoid writing to root '/'
            dest_file = jinja2.Template(src_file.replace(src_dir, "").lstrip("/\\")).render(**context)
            root_dest_file = os.path.join(dest_dir, dest_file)

            # handle assets/icons
            if "assets" in root.split(os.sep):
                if not icons:
                    continue
                if icons == []:
                    continue
                if 'icon.png' not in icons and filename == 'icon.png':
                    continue

            # handle install files
            if "install" in root.split(os.sep):
                if install_files is not None and filename not in install_files:
                    continue
                if filename == "example_schema.json":
                    dest_file = dest_file.replace("example_schema.json", "schema.json")
                    root_dest_file = root_dest_file.replace("example_schema.json", "schema.json")

            # ensure parent directories exist
            Path(root_dest_file).parent.mkdir(parents=True, exist_ok=True)

            # copy or render templates
            mime_type, _ = mimetypes.guess_type(src_file_path)
            if mime_type and not filename.endswith(('.png', '.jpg', '.xml', '.jpeg', '.gif')):
                template = env.get_template(src_file)
                with open(root_dest_file, 'w', encoding='utf-8') as f:
                    f.write(template.render(**context))
            else:
                shutil.copy2(src_file_path, root_dest_file)

            # preserve executable permissions
            if filename in ("install", "uninstall", "migrate"):
                st = os.stat(src_file_path)
                os.chmod(root_dest_file, st.st_mode)

            # track installed files (relative to dest_dir, normalized)
            rel_dest_file = os.path.relpath(root_dest_file, dest_dir).replace("\\", "/")
            installed_files.append(rel_dest_file)

    # render manifest now that installed_files is complete
    if manifest_template_path and manifest_dest_file:
        context_copy = context.copy()
        context_copy["installed_files"] = installed_files
        context_copy[
            "has_oninstall"] = "install/install" in installed_files and "install/schema.json" in installed_files
        context_copy["has_onuninstall"] = "install/uninstall" in installed_files
        context_copy["has_onmigrate"] = "install/migrate" in installed_files

        Path(manifest_dest_file).parent.mkdir(parents=True, exist_ok=True)
        print('--------------------------------------')
        print(manifest_template_path)
        template = env.get_template(manifest_template_path)
        with open(manifest_dest_file, 'w', encoding='utf-8') as f:
            f.write(template.render(**context_copy))

        rel_manifest_file = os.path.relpath(manifest_dest_file, dest_dir).replace("\\", "/")
        installed_files.append(rel_manifest_file)

    # icons processing
    if icons and icons != []:
        assets_dir = os.path.join(dest_dir, "assets")
        Path(assets_dir).mkdir(parents=True, exist_ok=True)

        for icon_path in icons:
            if os.path.isfile(icon_path):
                dest_icon_path = os.path.join(assets_dir, os.path.basename(icon_path))
                shutil.copy2(icon_path, dest_icon_path)
                installed_files.append(os.path.relpath(dest_icon_path, dest_dir).replace("\\", "/"))

    return installed_files


def create_app(directory, src_dir=None, **kwargs):
    files = generate_project(
        context=kwargs,
        dest_dir=directory,
        src_dir=src_dir,
    )
    return files
