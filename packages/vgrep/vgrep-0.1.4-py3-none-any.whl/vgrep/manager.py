import hashlib
import inspect
import tempfile
from pathlib import Path
from typing import Callable, Optional, Any

import chromadb

from vgrep.db import DB
from vgrep.fs import FS
from vgrep.file_sync import FileSync


class Manager:
    """Coordinate the filesystem, ChromaDB and syncing."""

    def __init__(
        self,
        directory: Path,
        file_match: Optional[Callable[[Path], bool]] = None,
        db_path: Optional[Path] = None,
        embedding: Any = None,
    ) -> None:
        self.directory = Path(directory)
        base_match = file_match or (lambda p: p.is_file())
        self.db_path = (
            Path(db_path)
            if db_path
            else self._default_db_path(self.directory)
        )
        self.db_path.mkdir(parents=True, exist_ok=True)

        def combined_match(p: Path) -> bool:
            if self.db_path in p.parents or p == self.db_path:
                return False
            return base_match(p)

        self.file_match = combined_match

        chroma_settings = chromadb.Settings(anonymized_telemetry=False)
        client = chromadb.PersistentClient(path=str(self.db_path),
                                           settings=chroma_settings)
        collection = (
            client.get_or_create_collection(name="main",
                                            embedding_function=embedding)
            if embedding
            else client.get_or_create_collection(name="main")
        )

        self.db = DB(collection)
        self.fs = FS(
            [self.directory],
            self.file_match,
            prune_ignored_dirs=file_match is None,
            match_supplied=file_match is not None,
        )
        self._syncer = FileSync(self.fs, self.db)

    def _default_db_path(self,
                         directory: Path) -> Path:
        h = hashlib.sha256()
        h.update(directory.as_posix().encode())
        return Path(tempfile.gettempdir()) / f"vgrep-{h.hexdigest()}"

    def sync(self) -> None:
        """Synchronize the database with the filesystem."""
        self._syncer.sync()

    def query(self, text: str, records: int = 10):
        """Query the database."""
        return self.db.query(text, records)
