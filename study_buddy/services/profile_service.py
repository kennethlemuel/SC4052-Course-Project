from __future__ import annotations

from study_buddy.models import UserProfile
from study_buddy.storage import JsonStore


class ProfileService:
    def __init__(self, store: JsonStore) -> None:
        self.store = store

    def get_profile(self) -> UserProfile:
        return self.store.load_profile()
