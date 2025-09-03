from uuid import uuid4


def create_suuid() -> str:
    _uuid = str(uuid4())
    return f"{_uuid[:8]}-{_uuid[-4:]}"
