import os
import typing as t


def get_authentication_token() -> t.Optional[str]:
    return os.getenv("MEILI_TOKEN")
