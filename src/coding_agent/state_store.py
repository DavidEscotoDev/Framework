from __future__ import annotations
from typing import Optional
from .state import SharedState

class StateStore:
    def __init__(self):
        self._states: dict[str, SharedState] = {}

    async def save(self, state: SharedState):
        self._states[state.request_id] = state

    async def get(self, request_id: str) -> Optional[SharedState]:
        return self._states.get(request_id)

    async def delete(self, request_id: str):
        self._states.pop(request_id, None)

    async def list_ids(self) -> list[str]:
        return list(self._states.keys())
