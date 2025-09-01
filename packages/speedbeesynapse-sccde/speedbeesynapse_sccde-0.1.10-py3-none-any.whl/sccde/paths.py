"""Synapse path."""
import sys
from pathlib import Path

from .errors import UnknownPlatformError


class __SynapsePath:

    """Path manager."""

    @property
    def progdir(self) -> Path:
        """Return program directory path."""
        if sys.platform == 'win32':
            return Path('C:\\Program Files\\SALTYSTER\\SpeeDBeeSynapse')
        if sys.platform == 'linux':
            return Path('/usr/local/speedbeesynapse')
        raise UnknownPlatformError

    @property
    def datadir(self) -> Path:
        """Return data directory path."""
        if sys.platform == 'win32':
            return Path('C:\\ProgramData\\SALTYSTER\\SpeeDBeeSynapse')
        if sys.platform == 'linux':
            return Path('/var/speedbeesynapse')
        raise UnknownPlatformError

    @property
    def backenddir(self) -> Path:
        """Return backend libexec directory path."""
        return self.progdir / 'libexec'

    @property
    def backend_python_path(self) -> Path:
        """Return python executable path in venv for backend."""
        if sys.platform == 'win32':
            return self.progdir / 'python3\\python.exe'
        if sys.platform == 'linux':
            return self.progdir / 'webui_backend_venv/bin/python3'
        raise UnknownPlatformError


SYNAPSE_PATH = __SynapsePath()
