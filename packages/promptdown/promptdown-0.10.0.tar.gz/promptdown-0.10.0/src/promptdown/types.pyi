from _typeshed import Incomplete
from typing import Literal, TypedDict

Role: Incomplete

class ResponsesPart(TypedDict):
    type: Literal['input_text']
    text: str

class ResponsesMessage(TypedDict):
    role: Role
    content: list[ResponsesPart]
