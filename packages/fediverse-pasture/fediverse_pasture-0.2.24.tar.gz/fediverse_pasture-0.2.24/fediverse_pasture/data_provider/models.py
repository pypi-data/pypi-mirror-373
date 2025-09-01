# SPDX-FileCopyrightText: 2023 Helge
#
# SPDX-License-Identifier: MIT

from pydantic import BaseModel, Field
from typing import List


class ActorKeyPair(BaseModel):
    """Represents a key pair for the actor"""

    name: str = Field(
        description="""Name of the key used in the key id in the form `key_id = f"{actor_id}#{name}"`"""
    )
    public: str = Field(description="""The PEM encoded public key""")
    private: str = Field(description="""The PEM encoded private key""")


class ActorData(BaseModel):
    """Represents an Actor"""

    actor_name: str = Field(
        description="""The name of the actor used in the actor_id"""
    )
    key_pairs: List[ActorKeyPair] = Field([], description="""List of keys""")
    user_part: str | None = Field(
        None,
        description="""User as part of the acct-uri for webfinger, None means webfinger lookup is not possible""",
    )

    summary: str = Field("", description="""Summary part of actor profile""")

    requires_signed_get_for_actor: bool = Field(
        False, description="""If true, validates the signature on `GET /actor`"""
    )
    requires_signed_post_for_inbox: bool = Field(
        False, description="""If true, validates the signature on `POST /inbox`"""
    )
