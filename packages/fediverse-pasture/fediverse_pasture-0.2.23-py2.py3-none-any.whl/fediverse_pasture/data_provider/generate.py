# SPDX-FileCopyrightText: 2023 Helge
#
# SPDX-License-Identifier: MIT

from bovine.crypto import generate_rsa_public_private_key


from .models import ActorData, ActorKeyPair


def generate_key_pair(name: str) -> ActorKeyPair:
    public, private = generate_rsa_public_private_key()

    return ActorKeyPair(name=name, public=public, private=private)


def generate_one_actor():
    key_pair = generate_key_pair("main")

    return ActorData(actor_name="actor", user_part="actor", key_pairs=[key_pair])


def generate_possible_actors():
    result = []

    for (
        name,
        user_part,
        requires_signed_get_for_actor,
        requires_signed_post_for_inbox,
    ) in [
        ("alice", "alice", False, False),
        ("bob", "bob", False, True),
        ("claire", "claire", True, True),
        ("dean", None, False, False),
        ("emily", None, False, True),
        ("frank", None, True, True),
    ]:
        key_pair = generate_key_pair("main")

        summary = f"""user_part={user_part}
requires_signed_get_for_actor={requires_signed_get_for_actor},
requires_signed_post_for_inbox={requires_signed_post_for_inbox},
"""

        result.append(
            ActorData(
                actor_name=name,
                summary=summary,
                user_part=user_part,
                key_pairs=[key_pair],
                requires_signed_get_for_actor=requires_signed_get_for_actor,
                requires_signed_post_for_inbox=requires_signed_post_for_inbox,
            )
        )

    return result
