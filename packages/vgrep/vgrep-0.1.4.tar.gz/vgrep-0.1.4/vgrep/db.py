import chromadb
from functools import reduce
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, TYPE_CHECKING

from pydantic import BaseModel

from vgrep.file_interpreter import FileInterpreter

if TYPE_CHECKING:  # pragma: no cover - only for type hints
    from vgrep.contextualizer import Contextualizer
else:  # pragma: no cover - avoid hard dependency at runtime
    Contextualizer = Any


class QueryResult(BaseModel):
    text: str
    filename: Path
    line_start: int
    context: str


class DB:
    """Handle interactions like updates and queries to the vector DB"""

    def __init__(
        self,
        collection: chromadb.Collection,
        contextualizer: Optional[Contextualizer] = None,
    ) -> None:
        self.contextualizer = contextualizer
        self.collection = collection
        self.file_interpreter = FileInterpreter()
    
    def add(self, p: Path):
        print(f'Adding {p}')
        chunks = []
        try:
            chunks = self.file_interpreter.file_chunks(p)
            meta_base = {
                "filename": p.as_posix(),
                "last_modified": p.stat().st_mtime,
                "context": "",
            }
            context = ""
            ids_to_update = []
        except UnicodeDecodeError:
            print(f'Could not add {p}, skippin')

        for chunk in chunks:
            ids_to_update.append(chunk.metadata.id)
            if self.contextualizer:
                context = self.contextualizer.contextualize(chunk.chunk, context)
            metadata = {
                **meta_base,
                "line_start": chunk.metadata.line_start,
            }
            self.collection.add(
                documents=chunk.chunk,
                ids=chunk.metadata.id,
                metadatas=metadata,
            )

        if self.contextualizer:
            for id in ids_to_update:
                self.collection.update(id, metadatas={"context": context})

    def remove(self, p:Path):
        print(f'Removing {p}')
        self.collection.delete(where={"filename": p.as_posix()})

    def update(self, p:Path):
        self.remove(p)
        self.add(p)

    def query(self, s: str, records: int = 10) -> List[QueryResult]:
        res = self.collection.query(query_texts=[s],
                                    n_results=records)
        docs = res['documents'][0]
        metas = map(lambda x: {'filename': Path(x['filename']),
                               'line_start': x['line_start'],
                               'context': x['context']},
                    res['metadatas'][0])
        return list(map(lambda x: {'text': x[0],
                                   **(x[1])},
                        zip(docs, metas)))

    def last_modified(self, p: Path):
        filename = p.as_posix()
        res = self.collection.get(where={'filename': filename})
        return min(map(lambda x: x['last_modified'],
                       res['metadatas']))

    def all_files(self) -> Dict[Path, float]:
        '''Returns a dict of Path -> modified_time'''
        return reduce(self.__metadata_reducer__,
                      self.__iterate_files__(),
                      {})

    @classmethod
    def __metadata_reducer__(
            cls,
            acc: Dict[Path, float],
            cur: tuple[str, float]) -> Dict[Path,float]:
        cur_modified = cur[1]
        cur_file = Path(cur[0])
        acc_modified = acc.get(cur_file)
        if not acc_modified or acc_modified > cur_modified:
            acc[cur_file] = cur_modified
        
        return acc

    def __iterate_files__(self, batch_size=10) -> Iterable[tuple[str, float]]:
        total = self.collection.count()
        for i in range(0, total, batch_size):
            batch = self.collection.get(include=["metadatas"],
                                        limit=batch_size,
                                        offset=i)
            for meta in batch["metadatas"]:
                yield (meta["filename"],
                       meta["last_modified"])
    


