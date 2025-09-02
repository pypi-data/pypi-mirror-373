from dataclasses import dataclass
from pathlib import Path

from edri.utility.shared_memory_pipe import SharedMemoryPipe


@dataclass
class File:
    file_name: str | None
    mime_type: str
    path: Path | SharedMemoryPipe
