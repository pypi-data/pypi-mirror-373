from langchain_text_splitters import RecursiveCharacterTextSplitter
from pydantic import BaseModel
from typing import Generator
from pathlib import Path
from hashlib import md5


class TextChunkMetadata(BaseModel):
    line_start: int
    id: str


class TextChunkWithMetadata(BaseModel):
    chunk: str
    metadata: TextChunkMetadata


class FileInterpreter:
    """Understands how to split files into text and associate the
    correct metadata.

    """

    def __init__(self, size: int = 3000, overlap: int = 500):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=size,
            chunk_overlap=overlap,
            length_function=len,
            add_start_index=True)

    def file_chunks(self,
                    p: Path) -> Generator[TextChunkWithMetadata, None, None]:
        """Yield TextChunkWithMetadata objects for the given file."""
        # Some files (such as system info pages) may not be valid UTF-8 which
        # would previously cause ``UnicodeDecodeError`` when reading.  Open the
        # file with ``errors='ignore'`` so that undecodable bytes are skipped and
        # indexing can continue.
        with open(p, encoding="utf-8", errors="ignore") as f:
            text = f.read()

        # Use `create_documents` so that we get the start index of each chunk.
        documents = self.text_splitter.create_documents([text])

        for idx, doc in enumerate(documents):
            chunk = doc.page_content
            start_index = doc.metadata.get("start_index", 0)
            line_start = text.count("\n", 0, start_index)
            id = chunk_id(chunk, p, idx)
            chunk_meta = TextChunkMetadata(line_start=line_start, id=id)
            yield TextChunkWithMetadata(chunk=chunk, metadata=chunk_meta)


def chunk_id(s: str, path: Path, idx: int) -> str:
    together = s + path.as_posix()
    return f'{md5(together.encode()).hexdigest()}:{idx}'
