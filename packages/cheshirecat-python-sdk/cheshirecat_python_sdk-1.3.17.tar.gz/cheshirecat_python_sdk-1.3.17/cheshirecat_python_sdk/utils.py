import os
from typing import Dict, Type, TypeVar, BinaryIO, Tuple
import magic

T = TypeVar("T")


def deserialize(data: Dict, cls: Type[T]) -> T:
    return cls(**data)


def file_attributes(filename: str, file: BinaryIO) -> Tuple[str, BinaryIO, str]:
    current_pos = file.tell()

    mime = magic.Magic(mime=True)
    content_type = mime.from_buffer(file.read(2048))

    file.seek(current_pos)

    return os.path.basename(filename), file, content_type
