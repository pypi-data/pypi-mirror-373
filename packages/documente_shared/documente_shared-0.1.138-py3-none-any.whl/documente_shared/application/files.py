from os import path
from typing import Tuple, Optional


def split_file_params(filepath: str) -> Tuple[str, str, str]:
    folder_path = path.dirname(filepath)
    filename = path.splitext(path.basename(filepath))[0]
    extension = path.splitext(filepath)[1]
    extension = extension.replace('.', '')
    return folder_path, filename, extension


def get_filename_from_path(file_path: Optional[str]) -> Optional[str]:
    if not file_path:
        return None
    return path.basename(file_path)


def remove_slash_from_path(file_path: str) -> str:
    if file_path and file_path.startswith('/'):
        return file_path[1:]
    return file_path

def remove_extension(filename: str) -> str:
    if filename and '.' in filename:
        return filename.rsplit('.', 1)[0]
    return filename
