from .types import ResponsesMessage as ResponsesMessage, ResponsesPart as ResponsesPart, Role as Role
from typing import Any

def convert_chat_messages_to_responses_input(messages: list[dict[str, Any]], map_system_to_developer: bool = True) -> list[ResponsesMessage]: ...
