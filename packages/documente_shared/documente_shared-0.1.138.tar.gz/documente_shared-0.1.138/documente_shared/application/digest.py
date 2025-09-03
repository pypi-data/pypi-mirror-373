import hashlib


def get_file_digest(file_bytes: bytes) -> str:
     sha256_hash = hashlib.sha256()
     sha256_hash.update(file_bytes)
     return sha256_hash.hexdigest()
