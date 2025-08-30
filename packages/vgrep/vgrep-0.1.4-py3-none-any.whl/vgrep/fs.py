from pathlib import Path
from typing import Callable, Dict, List, Optional

import pathspec


DEFAULT_IGNORE_PATTERNS = [".venv",
                           ".env",
                           "__pycache__",
                           "**/*~",
                           "**/#*#"]


class FS:
    """Handles filesystem operations"""

    def __init__(
        self,
        files: List[Path],
        file_match: Optional[Callable[[Path], bool]] = None,
        ignore_file: str = ".vgrepignore",
        prune_ignored_dirs: bool = True,
        match_supplied: bool = False,
    ):
        self.files = files
        self.file_match = file_match or (lambda p: p.is_file())
        self.prune_ignored_dirs = prune_ignored_dirs
        self.match_supplied = match_supplied

        self._ignore_specs: Dict[Path, pathspec.PathSpec] = {}
        for root in self.files:
            patterns = list(DEFAULT_IGNORE_PATTERNS)
            if root.is_dir():
                for name in [".gitignore", ignore_file]:
                    ignore_path = root / name
                    if ignore_path.is_file():
                        patterns.extend(ignore_path.read_text().splitlines())
            self._ignore_specs[root] = pathspec.PathSpec.from_lines(
                "gitwildmatch", patterns
            )

    def all_files_modifications(self) -> Dict[Path, float]:
        """Returns a dict of Path -> modification time"""
        return {
            p: self.file_timestamp(p)
            for p in sum(map(self.all_files_recur, self.files), [])
        }

    def _ignored(self, path: Path, root: Path) -> bool:
        spec = self._ignore_specs.get(root)
        if spec is None:
            return False
        rel = path.relative_to(root)
        rel_str = rel.as_posix()
        if path.is_dir():
            rel_str += "/"
        return spec.match_file(rel_str)

    def all_files_recur(self, path: Path, root: Optional[Path] = None) -> List[Path]:
        """Returns all files in `path`"""
        root = root or path

        if self._ignored(path, root):
            if self.match_supplied and self.file_match(path):
                pass
            elif path.is_dir():
                if self.prune_ignored_dirs:
                    return []
            else:
                return []

        if path.is_file():
            return [path] if self.file_match(path) else []
        elif path.is_dir():
            return sum(
                (self.all_files_recur(p, root) for p in path.iterdir()),
                [],
            )
        else:
            return []

    @staticmethod
    def file_timestamp(path: Path) -> float:
        return path.stat().st_mtime

    @staticmethod
    def to_path(filepath: str) -> Path:
        return Path(filepath)

