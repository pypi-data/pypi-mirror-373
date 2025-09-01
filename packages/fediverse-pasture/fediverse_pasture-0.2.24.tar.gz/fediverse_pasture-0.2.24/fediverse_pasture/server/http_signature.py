# SPDX-FileCopyrightText: 2023 Helge
#
# SPDX-License-Identifier: MIT

from quart import request, Blueprint


from bovine.crypto.helper import content_digest_sha256
from .utils import (
    validate_basic_signature_fields,
    retrieve_public_key,
    build_message_signature,
    build_http_signature,
    validate_signature,
)


http_signature_blueprint = Blueprint("http_signature", __name__)


@http_signature_blueprint.get("/")
async def get_handler():
    message, signature, error_dict = build_message_signature(request, "get")

    if error_dict:
        return error_dict, 401

    error_dict = validate_basic_signature_fields(message, request, signature)

    if error_dict:
        return error_dict, 401

    http_signature = build_http_signature(message, signature, request, "get")
    public_key, error_dict = await retrieve_public_key(
        message, signature.key_id, request
    )

    if error_dict:
        return error_dict, 401

    error_dict = validate_signature(
        message, request, public_key, signature, http_signature
    )

    if error_dict:
        return error_dict, 401

    return message.response, 200, {"content-type": "application/json"}


@http_signature_blueprint.post("/")
async def post_handler():
    message, signature, error_dict = build_message_signature(request, "post")

    if error_dict:
        return error_dict, 401

    body = await request.get_data()
    body_str = body.decode("utf-8")
    message.add(f"Got body: '{body_str}'")
    digest = content_digest_sha256(body)
    message.add(f"Computed digest {digest}")

    error_dict = validate_basic_signature_fields(
        message, request, signature, digest=digest
    )

    if error_dict:
        return error_dict, 401

    http_signature = build_http_signature(message, signature, request, "post")
    public_key, error_dict = await retrieve_public_key(
        message, signature.key_id, request
    )

    if error_dict:
        return error_dict, 401

    error_dict = validate_signature(
        message, request, public_key, signature, http_signature
    )

    if error_dict:
        return error_dict, 401

    return message.response, 202, {"content-type": "application/json"}
