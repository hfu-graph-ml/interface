from typing import TypeAlias


class Err:
    def __init__(self, message: str) -> None:
        self.message = message


Error: TypeAlias = Err | None
