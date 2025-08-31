# SPDX-FileCopyrightText: 2023 Helge
#
# SPDX-License-Identifier: MIT

from .utils import actor_object_to_public_key

public_key_string = """-----BEGIN PUBLIC KEY-----
CONTENT
-----END PUBLIC KEY-----
"""

base_case_actor = {
    "@context": [
        "https://www.w3.org/ns/activitystreams",
        "https://w3id.org/security/v1",
    ],
    "id": "https://domain.example/actor",
    "type": "Person",
    "preferredUsername": "alice",
    "inbox": "https://domain.example/inbox",
}

key_id = "https://domain.example/actor#main-key"


def test_base_case():
    data = {
        **base_case_actor,
        "publicKey": {
            "id": key_id,
            "owner": "https://domain.example/actor",
            "publicKeyPem": public_key_string,
        },
    }
    public_key, _ = actor_object_to_public_key(data, key_id)

    assert public_key == public_key_string


def test_base_case_wrong_context():
    data = {
        **base_case_actor,
        "@context": "https://www.w3.org/ns/activitystreams",
        "publicKey": {
            "id": key_id,
            "owner": "https://domain.example/actor",
            "publicKeyPem": public_key_string,
        },
    }
    public_key, _ = actor_object_to_public_key(data, key_id)

    assert public_key == public_key_string


def test_base_case_expanded():
    data = {
        **base_case_actor,
        "@context": "https://www.w3.org/ns/activitystreams",
        "https://w3id.org/security#publicKey": {
            "id": key_id,
            "https://w3id.org/security#owner": {"id": "https://domain.example/actor"},
            "https://w3id.org/security#publicKeyPem": public_key_string,
        },
    }
    public_key, _ = actor_object_to_public_key(data, key_id)

    assert public_key == public_key_string


def test_single_item_list():
    data = {
        **base_case_actor,
        "publicKey": [
            {
                "id": key_id,
                "owner": "https://domain.example/actor",
                "publicKeyPem": public_key_string,
            }
        ],
    }
    public_key, _ = actor_object_to_public_key(data, key_id)

    assert public_key == public_key_string


def test_multi_item_list():
    data = {
        **base_case_actor,
        "publicKey": [
            {
                "id": key_id,
                "owner": "https://domain.example/actor",
                "publicKeyPem": public_key_string,
            },
            {
                "id": "https://domain.example/actor#other-key",
                "owner": "https://domain.example/actor",
                "publicKeyPem": "xxxx",
            },
        ],
    }
    public_key, _ = actor_object_to_public_key(data, key_id)

    assert public_key == public_key_string


def test_multi_item_list_no_result():
    data = {
        **base_case_actor,
        "publicKey": [
            {
                "id": "https://domain.example/actor#wrong-key",
                "owner": "https://domain.example/actor",
                "publicKeyPem": public_key_string,
            },
            {
                "id": "https://domain.example/actor#other-key",
                "owner": "https://domain.example/actor",
                "publicKeyPem": "xxxx",
            },
        ],
    }
    public_key, _ = actor_object_to_public_key(data, key_id)

    assert public_key is None
