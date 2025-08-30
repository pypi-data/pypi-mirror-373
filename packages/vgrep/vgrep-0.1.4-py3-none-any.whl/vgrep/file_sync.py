from vgrep.db import DB
from vgrep.fs import FS
from pathlib import Path
from typing import Dict, Set


class FileSync:
    """Maintains the filesystem and db in sync"""
    def __init__(self,
                 filesystem: FS,
                 database: DB):
        self.database = database
        self.filesystem = filesystem

    def sync(self):
        fs_files = self.filesystem.all_files_modifications()
        db_files = self.database.all_files()
        fs_files_set = set(fs_files.keys())
        db_files_set = set(db_files.keys())
        self.update(self.database, db_files, fs_files)
        self.add(self.database, db_files_set, fs_files_set)
        self.remove(self.database,  db_files_set, fs_files_set)

    @classmethod
    def add(cls,
            db: DB,
            db_files: Set[Path],
            fs_files: Set[Path]):
        for path in fs_files - db_files:
            db.add(path)

    @classmethod
    def update(cls,
               db: DB,
               db_files: Dict[Path, float],
               fs_files: Dict[Path, float]):
        for db_path, db_modified in db_files.items():
            fs_modified = fs_files.get(db_path)
            if fs_modified and fs_modified > db_modified:
                db.update(db_path)

    @classmethod
    def remove(cls,
               db: DB,
               db_files: Set[Path],
               fs_files: Set[Path]):
        for path in db_files - fs_files:
            db.remove(path)
