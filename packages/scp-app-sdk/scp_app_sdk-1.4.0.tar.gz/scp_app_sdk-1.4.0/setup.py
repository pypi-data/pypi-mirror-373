#!/usr/bin/env python3
# coding: utf-8

import re, sys, os, subprocess, time
from pathlib import Path
from setuptools import setup, find_namespace_packages

def get_version():
    pkg_info = Path(__file__).parent / "PKG-INFO"
    if pkg_info.exists():
        with pkg_info.open(encoding="utf-8") as fp:
            matches = re.search(r"^Version: (.*)$", fp.read(), re.MULTILINE)
            if not matches:
                raise RuntimeError("Could not parse PKG-INFO for version.")
            return matches.group(1)
        
    changelog = Path(__file__).parent / "CHANGELOG.md"
    content = changelog.read_text(encoding="utf-8")
    fmatch = re.search(r"## \[(\d+\.\d+\.\d+)\]", content)
    if not fmatch:
        raise RuntimeError("Cannot find version in CHANGELOG.md")

    version = fmatch.group(1)


    try:
        if sys.argv[1] != 'install' and subprocess.run(
            ['git', 'describe', '--tags', '--exact-match'],
            check=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        ).returncode == 128:
            curtime = int(time.time())
            print(f'No git tag found or not installing, adding .dev{curtime} to version.')
            version += f'.dev{curtime}'
    except subprocess.CalledProcessError as e:
        print(e)
        pass

    return version


def get_long_description():
    root = Path(__file__).parent
    readme = (root / "README.md").read_text(encoding="utf-8") if (root / "README.md").exists() else ""
    changelog = (root / "CHANGELOG.md").read_text(encoding="utf-8") if (root / "CHANGELOG.md").exists() else ""
    return readme + "\n\n" + changelog

if __name__ == '__main__':
    setup(
        name='scp-app-sdk',
        version=get_version(),
        description='SCP APP SDK',
        long_description=get_long_description(),
        long_description_content_type="text/markdown",
        author='Dstny',
        python_requires='>=3.7',
        packages=find_namespace_packages(include=['scp.app.*']),
        include_package_data=True,
        entry_points={
            'console_scripts': [
                'scp-app = scp.app.sdk.cli.__main__:cli'
            ],
        },
        install_requires=[
            "marshmallow==3.*",
            "marshmallow-oneofschema==3.*",
            "click==8.*",
            "jinja2==3.*",
            "requests==2.*",
            "PyYAML==6.*",
        ],
    )
