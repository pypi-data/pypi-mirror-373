import subprocess
import time


class AppVersionException(Exception):
    pass


def app_version(version):
    if subprocess.run(['git', 'describe', '--tags', '--exact-match'], capture_output=True, text=True).returncode == 128:
        current_time = int(time.time())
        version += f'.dev{current_time}'
    else:
        git_tag = subprocess.run(['git', 'describe', '--tags', '--abbrev=0'], capture_output=True, text=True)
        if git_tag.returncode != 128:
            git_version = git_tag.stdout.strip()
            if git_version != version:
                raise AppVersionException(f"The APP version '{version}' doesn't match the git version '{git_version}'")
    return version
