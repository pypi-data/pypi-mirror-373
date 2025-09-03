from __future__ import annotations

import contextlib
import logging
import os
import shutil
from pathlib import Path

from git import Repo

from exasol.nb_connector.slc import constants

LOG = logging.getLogger(__name__)
LOG.setLevel(logging.INFO)


@contextlib.contextmanager
def current_directory(dir: Path):
    """
    Changes the current working directory to the specified one and reverts
    to the previous one on exit.
    """
    previous = Path.cwd()
    os.chdir(dir)
    try:
        yield
    finally:
        os.chdir(previous)


class Workspace:
    def __init__(self, root_dir: Path):
        self.root_dir = root_dir

    @classmethod
    def for_slc(cls, name: str) -> Workspace:
        return cls(Path.cwd() / constants.WORKSPACE_DIR / name)

    def clone_slc_repo(self):
        """
        Clones the script-languages-release repository from Github into
        the target dir configured in the Secure Configuration Storage.
        """
        path = self.git_clone_path
        if path.is_dir():
            LOG.warning(f"Directory '{path}' is not empty. Skipping checkout....")
            return

        path.mkdir(parents=True, exist_ok=True)
        LOG.info(f"Cloning into {path}...")
        repo = Repo.clone_from(
            "https://github.com/exasol/script-languages-release",
            path,
            branch=constants.SLC_RELEASE_TAG,
        )
        LOG.info("Fetching submodules...")
        repo.submodule_update(recursive=True)

    @property
    def git_clone_path(self) -> Path:
        """
        Returns the path for cloning Git repository
        script-languages-container-release.
        """
        return self.root_dir / "git-clone"

    @property
    def export_path(self) -> Path:
        """
        Returns the export path for script-languages-container
        """
        return self.root_dir / "container"

    @property
    def output_path(self) -> Path:
        """
        Returns the output path containing caches and logs.
        """
        return self.root_dir / "output"

    def cleanup_output_path(self) -> None:
        """
        Remove the output path recursively.
        """
        shutil.rmtree(self.output_path)

    def cleanup_export_path(self) -> None:
        """
        Remove the export path recursively
        """
        shutil.rmtree(self.export_path)
