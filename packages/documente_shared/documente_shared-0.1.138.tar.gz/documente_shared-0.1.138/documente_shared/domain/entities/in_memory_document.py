import base64
from typing import Optional
from dataclasses import dataclass

from documente_shared.application.files import get_filename_from_path, remove_extension, remove_slash_from_path


@dataclass
class InMemoryDocument(object):
    file_path: Optional[str] = None
    file_bytes: Optional[bytes] = None
    file_base64: Optional[str] = None

    def __post_init__(self):
        if not self.file_path:
            return
        if self.file_base64 and not self.file_bytes:
            self.file_bytes = base64.b64decode(self.file_base64)
        elif self.file_bytes and not self.file_base64:
            self.file_base64 = base64.b64encode(self.file_bytes).decode()


    @property
    def is_valid(self) -> bool:
        return bool(self.file_path and self.file_bytes)

    @property
    def has_content(self) -> bool:
        return bool(self.file_bytes or self.file_base64)

    @property
    def file_name(self) -> Optional[str]:
        return get_filename_from_path(self.file_path) if self.file_path else None

    @property
    def raw_file_name(self) -> str:
        return remove_extension(self.file_name)

    @property
    def file_key(self) -> Optional[str]:
        return remove_slash_from_path(self.file_path)

    @property
    def is_procesable(self) -> bool:
        return self.is_valid and self.has_content

    @property
    def to_dict(self) -> dict:
        return {
            "file_path": self.file_path,
            "file_base64": self.file_base64,
        }

    @property
    def to_queue_dict(self) -> dict:
        return {
            "file_path": self.file_path,
        }

    @classmethod
    def from_dict(cls, data: dict):
        file_bytes = data.get("file_bytes")
        file_base64 = data.get("file_base64")

        if file_bytes and not file_base64:
            file_base64 = base64.b64encode(file_bytes).decode()

        if file_base64 and not file_bytes:
            file_bytes = base64.b64decode(file_base64)

        return cls(
            file_path=data.get("file_path"),
            file_bytes=file_bytes,
            file_base64=file_base64,
        )
