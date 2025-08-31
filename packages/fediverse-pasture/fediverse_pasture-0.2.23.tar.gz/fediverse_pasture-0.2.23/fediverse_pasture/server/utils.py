# SPDX-FileCopyrightText: 2023 Helge
#
# SPDX-License-Identifier: MIT

import base64
import aiohttp
import json
from typing import Tuple

from bovine.jsonld import with_external_context
from bovine.utils import parse_gmt, check_max_offset_now
from bovine.crypto.signature import Signature
from bovine.crypto.helper import sign_message
from bovine.crypto.http_signature import build_signature

from fediverse_pasture.types import Message


def find_with_item(dict_list, key_id):
    """Given a list of dictionaries, finds the dictionary with
    id = key_id"""
    for key in dict_list:
        if key.get("id") == key_id:
            return key
    return None


def public_key_owner_from_dict(
    actor: dict, key_id: str
) -> Tuple[str | None, str | None]:
    """Given an actor and key_id returns the public_key and the owner. This method directly checks the key `publicKey`"""

    public_key_data = actor.get("publicKey", {})

    if isinstance(public_key_data, list):
        if len(public_key_data) == 1:
            public_key_data = public_key_data[0]
        else:
            public_key_data = find_with_item(public_key_data, key_id)

    if not public_key_data:
        return None, None

    public_key = public_key_data.get("publicKeyPem")
    owner = public_key_data.get("owner")

    return public_key, owner


def actor_object_to_public_key(
    actor: dict, key_id: str
) -> Tuple[str | None, str | None]:
    """As [public_key_owner_from_dict][fediverse_pasture.server.utils.public_key_owner_from_dict], but applies context normalization first, then checks without out."""
    public_key, owner = public_key_owner_from_dict(with_external_context(actor), key_id)

    if public_key and owner:
        return public_key, owner

    return public_key_owner_from_dict(actor, key_id)


def build_message_signature(request, method):
    message = Message()
    message.add(f"Got {method} request")
    message.add("With headers: " + str(request.headers))

    signature_header = request.headers.get("signature")
    if not signature_header:
        return None, None, message.error("Signature header is missing")

    message.add(f"Signature header '{signature_header}'")

    try:
        signature = Signature.from_signature_header(signature_header)
    except Exception as e:
        return (
            None,
            None,
            message.error(
                [
                    "Failed to parse signature",
                    repr(e),
                ]
            ),
        )

    message.add(f"""Got fields {", ".join(signature.fields)}""")

    return message, signature, None


def validate_basic_signature_fields(message, request, signature, digest=None):
    if "(request-target)" not in signature.fields:
        return message.error("(request-target) must be a signature field")

    if "host" not in signature.fields:
        return message.error("host must be a signature field")

    if "date" not in signature.fields:
        return message.error("date must be a signature field")

    if digest:
        if "digest" not in signature.fields:
            return message.error("digest must be a signature field")

        if request.headers.get("digest")[5:] != digest[5:]:
            return message.error("Digests do not match")

    date_header = request.headers.get("date")
    message.add(f"Got date header {date_header}")

    try:
        date_parsed = parse_gmt(date_header)
    except Exception as e:
        return message.error(["Failed to parse date", repr(e)])

    if not check_max_offset_now(date_parsed):
        return message.error(["Date not within the last 5 minutes"])

    return None


async def retrieve_public_key(message, key_id, request):
    if key_id == "about:inline":
        try:
            public_key = base64.standard_b64decode(
                request.headers.get("X-Public-Key")
            ).decode("utf-8")
        except Exception:
            public_key = None
        if not public_key:
            return None, message.error(
                "Please set the header 'X-Public-Key' to provide a public key"
            )
    else:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(key_id) as response:
                    if "json" in response.headers.get("content-type"):
                        data = await response.json()
                        message.add("Got json response " + json.dumps(data, indent=2))
                        public_key, _ = actor_object_to_public_key(data, key_id)
                    else:
                        public_key = await response.text()
        except Exception as e:
            return (
                None,
                message.error(
                    [
                        "Failed to fetch public key",
                        "Use about:inline to include a public key in a header",
                        "    about:inline is expected to be base64 encoded",
                        "or make sure keyId can be resolved to a public key",
                        repr(e),
                    ]
                ),
            )
    if not public_key:
        return None, message.error("Something went wrong when retrieving public key")
    message.add(f"""Got public key "{public_key}" """)

    return public_key, None


def build_http_signature(message, signature, request, method):
    header_fields = [x for x in signature.fields if x[0] != "("]

    http_signature = build_signature(request.headers.get("host"), method, request.path)

    for x in header_fields:
        if x != "host":
            http_signature.with_field(x, request.headers.get(x))

    message.add(f"""Message to sign "{http_signature.build_message()}" """)
    message.add(f"Got key id {signature.key_id}")

    return http_signature


def validate_signature(message, request, public_key, signature, http_signature):
    try:
        result = http_signature.verify(
            public_key=public_key, signature=signature.signature
        )
    except Exception as e:
        return (
            message.error(
                [
                    "Something went wrong when verifying signature",
                    repr(e),
                ]
            ),
            401,
        )

    if not result:
        private_key = request.headers.get("X-Private-Key")

        if private_key is None:
            message.add(
                "Set X-Private-Key to your base64 encoded private key\
                        for expected signature",
            )
        else:
            message.add("Expected signature:")
            message.add(
                sign_message(
                    private_key=base64.standard_b64decode(private_key).decode("utf-8"),
                    message=http_signature.build_message(),
                )
            )

        return message.error("Invalid signature")
    else:
        message.add("SUCCESS!!!")
