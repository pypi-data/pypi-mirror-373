from abc import ABC, abstractmethod
from logging import Logger
from pathlib import Path
from typing import Optional

from amberflow.primitives import dirpath_t, _run_command, filepath_t

__all__ = ("BaseDataMover", "RsyncMover")


class BaseDataMover(ABC):
    """Abstract base class for data transfer strategies."""

    __slots__ = ("_initialized",)
    err_msg = f"'{__name__}' instances are immutable."

    def __init__(self, *args, **kwargs) -> None:
        super().__setattr__("_initialized", False)

    def __setattr__(self, key, val):
        if self._initialized:
            raise AttributeError(self.err_msg)
        return super().__setattr__(key, val)

    def __delattr__(self, key):
        raise AttributeError(self.err_msg)

    @abstractmethod
    def upload(self, local_path: dirpath_t, remote_path: dirpath_t, logger: Logger, **kwargs) -> None:
        """Uploads data from a local path to a remote path."""
        pass

    @abstractmethod
    def download(self, remote_path: dirpath_t, local_path: dirpath_t, logger: Logger, **kwargs) -> None:
        """Downloads data from a remote path to a local path."""
        pass


class RsyncMover(BaseDataMover):
    """Data mover that uses rsync over SSH."""

    remote_server: str
    keyfile: Path

    __slots__ = BaseDataMover.__slots__ + ("remote_server", "keyfile")

    def __init__(self, remote_server: str, keyfile: Optional[filepath_t] = None) -> None:
        super().__init__()
        super().__setattr__("remote_server", remote_server)
        super().__setattr__("keyfile", keyfile)
        super().__setattr__("_initialized", True)

    def upload(self, local_path: dirpath_t, remote_path: dirpath_t, logger: Logger, **kwargs) -> None:
        src = f"{local_path}/"
        dest = f"{self.remote_server}:{remote_path}/"
        self._run_rsync(src, dest, logger, **kwargs)

    def download(self, remote_path: dirpath_t, local_path: dirpath_t, logger: Logger, **kwargs) -> None:
        src = f"{self.remote_server}:{remote_path}/"
        dest = f"{local_path}/"
        self._run_rsync(src, dest, logger, **kwargs)

    @staticmethod
    def _run_rsync(src: str, dest: str, logger: Logger, **kwargs):
        exclude = kwargs.get("exclude")
        # cmd_list = ["rsync", "-avzu", "--delete"]
        cmd_list = ["rsync", "-avzu"]
        if exclude:
            for item in exclude:
                cmd_list.append(f"--exclude='{item}'")
        cmd_list.extend([src, dest])

        cmd_str = " ".join(cmd_list)
        logger.debug(f"Running rsync:\n{cmd_str}")
        _run_command(cmd_str, cwd=Path.cwd(), logger=logger, check=True)
