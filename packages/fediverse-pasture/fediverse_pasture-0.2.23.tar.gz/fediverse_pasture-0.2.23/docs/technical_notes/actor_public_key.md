<!--
SPDX-FileCopyrightText: 2023 Helge

SPDX-License-Identifier: CC-BY-4.0
-->

# Retrieving the Public Key from an ActivityPub Actor

This technical note describes the mechanism to resolve the public key from
the actor object. The `fediverse_python` library and its tests can be consulted
to inspect implementation details.

!!! caution
    The strategy outlined here is somewhat permissive. Choices in a production
    application can be different.

## Outline of the strategy by example

Taking the first example from [How to implement a basic ActivityPub server](https://blog.joinmastodon.org/2018/06/how-to-implement-a-basic-activitypub-server/) as

```json
{
  "@context": [
    "https://www.w3.org/ns/activitystreams",
    "https://w3id.org/security/v1"
  ],
  "id": "https://domain.example/actor",
  "type": "Person",
  "preferredUsername": "alice",
  "inbox": "https://domain.example/inbox",
  "publicKey": {
    "id": "https://domain.example/actor#main-key",
    "owner": "https://domain.example/actor",
    "publicKeyPem": "-----BEGIN PUBLIC KEY-----...-----END PUBLIC KEY-----"
  }
}
```

one can determine the basic strategy:

```python
public_key_pem = actor["publicKey"]["publicKeyPem"]
```

### Multiple Keys

The ActivityPub Actor object is a JSON-LD object. This means that `publicKey` is
not actually single valued, but could be a set. So something such as the following
is possible

```json
{
  "@context": [
    "https://www.w3.org/ns/activitystreams",
    "https://w3id.org/security/v1"
  ],
  "id": "https://domain.example/actor",
  "type": "Person",
  "preferredUsername": "alice",
  "inbox": "https://domain.example/inbox",
  "publicKey": [
    {
      "id": "https://domain.example/actor#main-key",
      "owner": "https://domain.example/actor",
      "publicKeyPem": "-----BEGIN PUBLIC KEY-----...-----END PUBLIC KEY-----"
    },
    {
      "id": "https://domain.example/actor#other-key",
      "owner": "https://domain.example/actor",
      "publicKeyPem": "-----BEGIN PUBLIC KEY-----...-----END PUBLIC KEY-----"
    }
  ]
}
```

If `publicKey` is a set, the elements will be inspected and the key with
`id` matching `keyId` from the HTTP Signature will be chosen.

### JSON-LD @context ambiguity

The `@context` property can verify between implementations.
Using the [JSON-LD Playground](https://json-ld.org/playground/), one can see
that the following JSON-LD is equivalent to our original one. Unfortunately,
our strategy to retrieve the public key does not work.

```json
{
  "@context": "https://www.w3.org/ns/activitystreams",
  "id": "https://domain.example/actor",
  "type": "Person",
  "inbox": "https://domain.example/inbox",
  "https://w3id.org/security#publicKey": {
    "id": "https://domain.example/actor#main-key",
    "https://w3id.org/security#owner": {
      "id": "https://domain.example/actor"
    },
    "https://w3id.org/security#publicKeyPem": "-----BEGIN PUBLIC KEY-----...-----END PUBLIC KEY-----"
  },
  "preferredUsername": "alice"
}
```

In order to get around this, we will compact the JSON documents against
the `@context` given by

```json
["https://www.w3.org/ns/activitystreams", "https://w3id.org/security/v1"]
```

### Incorrect JSON-LD terms

Finally, we wish to allow for incorrect usage of JSON-LD. This means that
the following example should also lead to the public key.

```json
{
  "@context": "https://www.w3.org/ns/activitystreams",
  "id": "https://domain.example/actor",
  "type": "Person",
  "preferredUsername": "alice",
  "inbox": "https://domain.example/inbox",
  "publicKey": {
    "id": "https://domain.example/actor#main-key",
    "owner": "https://domain.example/actor",
    "publicKeyPem": "-----BEGIN PUBLIC KEY-----...-----END PUBLIC KEY-----"
  }
}
```

## References

- [How to implement a basic ActivityPub server](https://blog.joinmastodon.org/2018/06/how-to-implement-a-basic-activitypub-server/) on the Mastodon Blog by Eugen Rochko.
