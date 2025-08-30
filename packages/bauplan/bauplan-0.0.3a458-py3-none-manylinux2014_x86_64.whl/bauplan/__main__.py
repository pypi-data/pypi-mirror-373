"""
Allow bauplan to be invoked as `python -m bauplan`.
"""

import os
import sys
import sysconfig
from pathlib import Path


def find_bauplan_bin() -> Path:
    """


    Returns:
        This implementation is inspired by UV's approach to finding its binary.
        See: https://github.com/astral-sh/uv/blob/main/python/uv/_find_uv.py

    """

    # Determine the executable name based on platform
    if sys.platform == 'win32':
        bauplan_exe = 'bauplan.exe'
    else:
        bauplan_exe = 'bauplan'

    # First, check in the standard scripts directory
    scripts_dir = Path(sysconfig.get_path('scripts'))
    path = scripts_dir / bauplan_exe
    if path.is_file():
        return path

    # Check user scripts directory
    if sys.version_info >= (3, 10):
        user_scheme = sysconfig.get_preferred_scheme('user')
    elif os.name == 'nt':
        user_scheme = 'nt_user'
    elif sys.platform == 'darwin' and sys._framework:
        user_scheme = 'osx_framework_user'
    else:
        user_scheme = 'posix_user'

    user_scripts_dir = Path(sysconfig.get_path('scripts', scheme=user_scheme))
    path = user_scripts_dir / bauplan_exe
    if path.is_file():
        return path

    # Check in the package's bin directory (for development or special installs)
    pkg_root = Path(__file__).parent
    bin_paths = [
        pkg_root / 'bin' / 'bauplan-cli',  # Development location
        pkg_root / 'bin' / 'bauplan-cli.exe',  # Windows development
        pkg_root.parent / 'bin' / bauplan_exe,  # Adjacent bin directory
    ]

    for bin_path in bin_paths:
        if bin_path.is_file():
            return bin_path

    # Search in PATH as a last resort
    path_env = os.environ.get('PATH', '').split(os.pathsep)
    for directory in path_env:
        candidate = Path(directory) / bauplan_exe
        if candidate.is_file():
            return candidate

    raise FileNotFoundError(
        f'Could not find bauplan binary. Searched in: {scripts_dir}, {user_scripts_dir}, {bin_paths}, and PATH'
    )


def _detect_virtualenv() -> str:
    """
    Find the virtual environment path for the current Python executable.

    This implementation is inspired by UV's approach to finding its binary.
    See: https://github.com/astral-sh/uv/blob/main/python/uv/__main__.py

    """

    # If it's already set, then just use it
    value = os.getenv('VIRTUAL_ENV')
    if value:
        return value

    # Otherwise, check if we're in a venv
    venv_marker = os.path.join(sys.prefix, 'pyvenv.cfg')

    if os.path.exists(venv_marker):
        return sys.prefix

    return ''


def _run() -> None:
    """
    Execute the bauplan binary with all command line arguments.

    This implementation is inspired by UV's approach to finding its binary.
    See: https://github.com/astral-sh/uv/blob/main/python/uv/__main__.py

    """
    bauplan = os.fsdecode(str(find_bauplan_bin()))

    env = os.environ.copy()
    venv = _detect_virtualenv()
    if venv:
        env.setdefault('VIRTUAL_ENV', venv)

    if sys.platform == 'win32':
        import subprocess

        result = subprocess.run([bauplan, *sys.argv[1:]], env=env)
        sys.exit(result.returncode)
    else:
        os.execvpe(bauplan, [bauplan, *sys.argv[1:]], env=env)  # noqa: S606


if __name__ == '__main__':
    _run()
