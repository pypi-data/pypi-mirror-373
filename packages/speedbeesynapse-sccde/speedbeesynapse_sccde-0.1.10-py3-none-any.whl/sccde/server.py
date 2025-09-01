"""Test server module."""
from __future__ import annotations

import json
import os
import signal
import subprocess
import time
from typing import TYPE_CHECKING, Optional

from .errors import SynapseNotInstalledError, SynapseStartingError
from .paths import SYNAPSE_PATH as SP

if TYPE_CHECKING:
    from pathlib import Path

CORE_STATE_FILE = 'hivecore_exec_status.json'

class TestServer:

    """Sccde test server class."""

    def __init__(self, datadir: Path, host: str, port: int):
        """Initialize."""
        self.datadir = datadir
        self._host = host
        self._port = port
        self.verbose = False
        self._cp: Optional[subprocess.Popen] = None

    def setup(self) -> None:
        """Prepare data directories."""
        if not SP.backend_python_path.exists():
            raise SynapseNotInstalledError

        cmds = [ str(SP.backend_python_path),
                 '-m', 'module.sccde_test',
                 '--setup' ]
        env = os.environ.copy()
        env['PYTHONPATH'] = str(SP.backenddir)
        env['PYTHONUTF8'] = '1'

        subprocess.run(cmds, # noqa:  S603
                       stdout=None if self.verbose else subprocess.DEVNULL,
                       stderr=None if self.verbose else subprocess.DEVNULL,
                       check=True,
                       env=env)

    def start(self) -> TestServer:
        """Start server process."""
        if not SP.backend_python_path.exists():
            raise SynapseNotInstalledError

        cmds = [ str(SP.backend_python_path),
                 '-m', 'module.sccde_test',
                 '--host', self._host,
                 '--port', str(self._port) ]
        env = os.environ.copy()
        env['PYTHONPATH'] = str(SP.backenddir)
        env['PYTHONUTF8'] = '1'

        self._cp = subprocess.Popen(cmds, # noqa:  S603
                                    stdout=None if self.verbose else subprocess.DEVNULL,
                                    stderr=None if self.verbose else subprocess.DEVNULL,
                                    env=env)

        # hivecoreプロセスがRunningになるまで待ち
        self._wait_status_running()

        return self

    def _wait_status_running(self) -> None:
        """Wait hivecore process to be running-status and return True."""
        if self._cp is None:
            return

        status_file = self.datadir / CORE_STATE_FILE
        while self._cp.poll() is None:
            if status_file.exists():
                with status_file.open('r') as fo:
                    data = json.load(fo)
                    if data['status'] == 'Running':
                        return
            time.sleep(1)

        raise SynapseStartingError(self._cp.returncode)

    def stop(self) -> None:
        """Stop and wait server process exits."""
        if self._cp is None:
            return

        self._cp.send_signal(signal.CTRL_C_EVENT if hasattr(signal, 'CTRL_C_EVENT') else signal.SIGINT)
        self._cp.wait()
        self._cp = None

    def __enter__(self): # noqa: D105
        return self

    def __exit__(self, exc_type, exc_value, traceback): # noqa: ANN001, D105
        self.stop()
        return self

