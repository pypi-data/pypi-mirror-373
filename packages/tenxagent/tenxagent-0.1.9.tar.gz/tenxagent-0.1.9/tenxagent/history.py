# in tenxagent/history.py

from collections import defaultdict
from typing import List
from .schemas import Message

class InMemoryHistoryStore:
    """A simple thread-safe, in-memory message history store using standard Message format."""
    def __init__(self):
        self._history = defaultdict(list)

    async def get_messages(self, session_id: str) -> List[Message]:
        return self._history[session_id][:] # Return a copy

    async def add_message(self, session_id: str, message: Message):
        self._history[session_id].append(message)

    async def clear_history(self, session_id: str):
        if session_id in self._history:
            del self._history[session_id]