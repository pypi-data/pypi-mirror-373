from urllib.parse import urlparse

from quart import Blueprint, request

from bovine.models import JrdData, JrdLink
from bovine.utils import pydantic_to_json


nodeinfo_blueprint = Blueprint("nodeinfo", __name__)


@nodeinfo_blueprint.get("/.well-known/nodeinfo")
async def nodeinfo() -> tuple[dict, int]:
    """Returns the JRD corresponding to `/.well-known/nodeinfo`"""
    path = urlparse(request.url)
    nodeinfo = JrdLink(
        rel="http://nodeinfo.diaspora.software/ns/schema/2.0",
        href=f"{path.scheme}://{path.netloc}/.well-known/nodeinfo2_0",
    )

    return (
        pydantic_to_json(JrdData(links=[nodeinfo])),
        200,
        {"content-type": "application/jrd+json"},
    )


@nodeinfo_blueprint.get("/.well-known/nodeinfo2_0")
async def nodeinfo_response() -> dict:
    user_count = 0
    user_stat = {
        "total": user_count,
        "activeMonth": user_count,
        "activeHalfyear": user_count,
    }

    return {
        "metadata": {},
        "openRegistrations": False,
        "protocols": ["activitypub"],
        "services": {"inbound": [], "outbound": []},
        "software": {"name": "fediverse-pasture", "version": "0"},
        "usage": {"users": user_stat},
        "version": "2.0",
    }
