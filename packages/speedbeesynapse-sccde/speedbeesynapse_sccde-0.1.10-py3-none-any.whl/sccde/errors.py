"""Errors definition."""
from pathlib import Path

# ruff: noqa: D101, D105, D107

class SccdeError(Exception):
    def __str__(self) -> str:
        args_str = ' '.join([str(x) for x in self.args])
        return f'{self.__class__.__name__}: {args_str}'


class AlreadyInitializedError(SccdeError):
    def __init__(self, path: Path):
        self.path = path
    def __str__(self) -> str:
        return f'The directory {self.path} is initialized for SCCDE already.'


class NotInitializedError(SccdeError):
    def __init__(self, path: Path):
        self.path = path
    def __str__(self) -> str:
        return f'The directory {self.path} is not initialized for SCCDE yet.'


class SccInfoNotWritableError(SccdeError):
    def __init__(self, info_path: Path):
        self.info_path = info_path
    def __str__(self) -> str:
        return f'Could not write data into {self.info_path}.'


class SynapseNotInstalledError(SccdeError):
    def __str__(self) -> str:
        return 'SpeeDBee Synapse not found in this system.'


class SynapseStartingError(SccdeError):
    def __init__(self, returncode: int):
        self.returncode = returncode
    def __str__(self) -> str:
        return f'SpeeDBee Synapse process exits unexpectedly with code[{self.returncode}]'


class UnknownPlatformError(SccdeError):
    def __str__(self) -> str:
        return 'This platform is not supported.'
