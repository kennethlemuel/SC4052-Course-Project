from __future__ import annotations

from chief_of_staff.models import UserProfile
from chief_of_staff.storage import JsonStore


class ProfileService:
    def __init__(self, store: JsonStore) -> None:
        self.store = store

    def get_profile(self) -> UserProfile:
        return self.store.load_profile()
