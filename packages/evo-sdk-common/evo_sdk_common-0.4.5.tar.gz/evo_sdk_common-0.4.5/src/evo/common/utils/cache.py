#  Copyright © 2025 Bentley Systems, Incorporated
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#      http://www.apache.org/licenses/LICENSE-2.0
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

import shutil
import tempfile
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
from typing import TypeAlias
from uuid import uuid5

from evo.common.data import Environment
from evo.common.exceptions import StorageFileExistsError, StorageFileNotFoundError
from evo.common.interfaces import ICache

__all__ = ["Cache"]


FileName: TypeAlias = str | Path


class Cache(ICache):
    """An optional utility to manage cache directories for API data.

    The cache may be used to store transient binary data, such as files from File API or parquet files from
    the Geoscience Object API.
    """

    def __init__(self, root: FileName, mkdir: bool = False) -> None:
        """
        :param root: The root cache directory.
        :param mkdir: If True, create the cache directory if it does not exist.
        """
        match root:
            case Path():
                pass  # No conversion necessary.
            case str():
                root = Path(root)
            case _:
                raise TypeError(f"Expected a Path or str, got {root!r}")

        root = root.resolve()

        if mkdir:
            root.mkdir(parents=True, exist_ok=True)
        elif not root.exists():
            raise StorageFileNotFoundError(f"'{root}' does not exist.")

        if not root.is_dir():
            raise StorageFileExistsError(f"'{root}' is not a directory.")

        self._root = root

    @property
    def root(self) -> Path:
        """The absolute path to the root cache directory."""
        return self._root

    def get_location(self, environment: Environment, scope: str) -> Path:
        """Get the cache location for the specified environment and scope.

        :param environment: The environment used to determine the cache location.
        :param scope: The scope used to determine the cache location.

        :returns: The absolute path to the cache location.

        :raises StorageFileExistsError: If the location already exists, and it is not a directory.
        """
        cache_id = uuid5(environment.workspace_id, scope)
        storage = self.root / str(cache_id)

        try:
            storage.mkdir()
        except FileExistsError as err:
            if not storage.is_dir():
                raise StorageFileExistsError(f"'{storage}' is not a directory.") from err

        return storage

    def clear_cache(self, environment: Environment | None = None, scope: str | None = None) -> None:
        """Clear the cache for the specified environment and scope.

        If the environment and the scope is None, clear the entire cache.

        :param environment: The environment of the cache location. If None, clear the entire cache.
        :param scope: The scope of the cache location. If None, clear the entire cache.

        :raises ValueError: If either environment or scope is None, but not both.
        """
        if scope is None and environment is None:
            # Leave the root directory in place.
            targets = list(self.root.iterdir())
        elif scope is None or environment is None:
            raise ValueError("environment and scope must be specified together.")
        else:
            targets = [self.get_location(environment, scope)]

        for target in targets:
            if target.is_dir():
                shutil.rmtree(target)
            else:
                target.unlink()

    @contextmanager
    def temporary_location(self) -> Iterator[Path]:
        """Create a temporary cache directory.

        Uses tempfile.TemporaryDirectory internally to create a temporary directory within the cache root.
        The temporary directory is removed when the context manager exits.

        :returns: The absolute path to the temporary cache directory.
        """
        with tempfile.TemporaryDirectory(dir=self.root) as temp:
            yield Path(temp)
