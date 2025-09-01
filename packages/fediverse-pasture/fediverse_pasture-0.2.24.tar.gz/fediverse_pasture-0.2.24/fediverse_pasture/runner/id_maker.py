from secrets import token_urlsafe
from collections.abc import Callable

from urllib.parse import urljoin


def create_make_id_for_actor_id(actor_id: str) -> Callable[..., str]:
    def make_id(activity: bool = False) -> str:
        prefix = "/activity/" if activity else "/object/"

        return urljoin(actor_id, f"{prefix}{token_urlsafe(8)}")

    return make_id
