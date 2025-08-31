<!--
SPDX-FileCopyrightText: 2023 Helge

SPDX-License-Identifier: CC-BY-4.0
-->

# Signing with HTTP Signatures

By using the `pasture_http_signature` container provided by the Fediverse Pasture,
you can test your HTTP Signature implementation for signing messages. This
means you can send a HTTP request, and the server `pasture_http_signature` will tell
you if your signature is correct and if not, help you debug your implementation.

## Getting started

=== "Docker"

    You can use the docker image [helgekr/pasture](https://hub.docker.com/repository/docker/helgekr/pasture/general) to run http signatures via

    ```bash
    docker run -p 2917:80 -ti helgekr/pasture http_signature
    ```

=== "Podman"

    You can use the docker image [helgekr/pasture](https://hub.docker.com/repository/docker/helgekr/pasture/general) to run http signatures via

    ```bash
    podman run -p 2917:80 -ti docker.io/helgekr/pasture http_signature
    ```

=== "Fediverse Pasture"

    You can install the Fediverse pasture via

    ```bash
    git clone https://codeberg.org/helge/funfedidev.git
    cd fediverse-pasture
    ```

    Then in your Fediverse Pasture installation, run

    ```bash
    docker compose --file pasture.yml up pasture_http_signature
    ```

    I recommend running this in non daemon mode, so it is easy to see the
    log output. By running, the following you can connect a docker container
    running the command line to the pasture.

    ```bash
    docker run -ti --network fediverse-pasture_default alpine
    ```

    You can check if the network is setup correctly by running `ping pasture_http_signature`.
    By following the above step to connect your development container
    to the docker network, you are now ready to test your HTTP Signature
    implementation.

### Information on HTTP Signatures

HTTP Signatures are implemented in the Fediverse as described in
the Blog Post and IETF draft from 2018 found in the [References](#references).
One should note that the current IETF proposal for signing HTTP
messages uses a different format.

## Features

The point of the `pasture_http_signature` application is to provide feedback, when
implementing HTTP Signature. For this, it answers to the two requests

=== "Docker"

    ```http
    GET http://localhost:2917/
    POST http://localhost:2917/
    ```

=== "Podman"

    ```http
    GET http://localhost:2917/
    POST http://localhost:2917/
    ```

=== "Fediverse Pasture"

    ```http
    GET http://pasture_http_signature/
    POST http://pasture_http_signature/
    ```

`pasture_http_signature` answers with status code 200, if the request is correctly
signed and otherwise 401. In both cases, a JSON body is send along providing
information about the validation of the signature. The JSON has the key
`steps` containing an array of strings describing the successful validation
steps, and possible another array `error` describing what went wrong.

### Validation details

It is assumed that the fields being signed container

- `(request-target)`
- `host`
- `date`
- and for POST requests only `digest`.

If the algorithm is not specified, it is assumed to be `rsa-sha256`.

### Public Key Fetching

There are three options to specify the `keyId` property in the signature
header.

1. `keyId="about:inline"` then the public key is decoded from the `X-Public-Key` request header
1. The keyId can be resolved to a text document. Then this is assumed to include a PEM encoded public key
1. The keyId resolves to an Actor object. Then the publicKey is determined as it would be in ActivityPub usage. Note, this key retrievel is done with an unsigned HTTP request.

These options are provided to make developing new algorithms easier. Options 1 and 2 should
not be used in production, as they do not let one determine the owner of the key. So the
HTTP signature cannot be used as a means of authentication.

The format of the `X-Public-Key` header is a base64 encoded pem encoded public key.
This means that the public key

```text
-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAwI+SUFAJToTe1Kdo1j0k
4vS9eMhE12+61pxK3zU9tBHHdTo1uywFciSVpqmdyLY3p2rrfP3I5OptqidKCI0T
oRknfwN1o0sM1VDhcnQuvlDZYsCAXpIBcSuzlemnHezFrJxrdm4TM+hr27iHKb0U
r7fHVpvQ+UC9dmtQDSm2EC6aLi2BF5QHxjZdIa1erAJFdcoLSx5AoTyQuGzrcWUb
Iwr9Xkc7g0InzI3sd/KdapNMB6ULyP23/Wz/CMjCuWPzB7gu5+tlzXbD+NWz5BFy
FytVqewSZxBx/G6zaK/lILVyq7QXEF8bKcfUs/LEkULEchi7qMzEJyQ09ELXfTFL
SwIDAQAB
-----END PUBLIC KEY-----
```

would be turned into the header

```text
X-Public-Key: LS0tLS1CRUdJTiBQVUJMSUMgS0VZLS0tLS0KTUlJQklqQU5CZ2txaGtpRzl3MEJBUUVGQUFPQ0FROEFNSUlCQ2dLQ0FRRUF3SStTVUZBSlRvVGUxS2RvMWowawo0dlM5ZU1oRTEyKzYxcHhLM3pVOXRCSEhkVG8xdXl3RmNpU1ZwcW1keUxZM3AycnJmUDNJNU9wdHFpZEtDSTBUCm9Sa25md04xbzBzTTFWRGhjblF1dmxEWllzQ0FYcElCY1N1emxlbW5IZXpGckp4cmRtNFRNK2hyMjdpSEtiMFUKcjdmSFZwdlErVUM5ZG10UURTbTJFQzZhTGkyQkY1UUh4alpkSWExZXJBSkZkY29MU3g1QW9UeVF1R3pyY1dVYgpJd3I5WGtjN2cwSW56STNzZC9LZGFwTk1CNlVMeVAyMy9Xei9DTWpDdVdQekI3Z3U1K3RselhiRCtOV3o1QkZ5CkZ5dFZxZXdTWnhCeC9HNnphSy9sSUxWeXE3UVhFRjhiS2NmVXMvTEVrVUxFY2hpN3FNekVKeVEwOUVMWGZURkwKU3dJREFRQUIKLS0tLS1FTkQgUFVCTElDIEtFWS0tLS0tCg==
```

## Python Quick Test with bovine library

!!! warning "Illustration"
    This is meant to illustrate usage of the \`http_signature container.
    It is not meant as an example to follow.

We will use the setup given by

```bash
docker compose --file pasture.yml up pasture_http_signature
docker run -ti --network fediverse-pasture_default python:3.11-alpine /bin/sh
```

We can now install [bovine](https://bovine.readthedocs.io/en/latest/) and
check it's implementation against `http_signature`. We can now start
python with async support via

```bash
pip install bovine
python -masyncio
```

In the python REPL, we can now run

```python
>>> import base64, bovine
>>> public, private = bovine.crypto.generate_rsa_public_private_key()
>>> actor = bovine.BovineActor({"account_url": "localhost", "public_key_url": "about:inline", "private_key": private})
>>> await actor.init()
>>> public64 = base64.standard_b64encode(public.encode('utf-8')).decode('utf-8')
>>> response = await actor.client.get('http://pasture_http_signature/', headers={'X-Public-Key': public64})
>>> response.status
200
>>> await response.json()
{
  "steps": [
    "Got get request",
    "Signature header 'keyId=\"about:inline\",algorithm=\"rsa-sha256\",headers=\"(request-target) host date accept\",signature=\"1l....==\"'",
    "Got fields (request-target), host, date, accept",
    "Got date header Sun, 17 Sep 2023 17:09:18 GMT",
    "Message to sign \"(request-target): get /\nhost: pasture_http_signature\ndate: Sun, 17 Sep 2023 17:09:18 GMT\naccept: application/activity+json\" ",
    "Got key id about:inline",
    "Got public key \"-----BEGIN PUBLIC KEY-----\nMIIB....AB\n-----END PUBLIC KEY-----\n\" ",
    "SUCCESS!!!"
  ]
}
```

We should note that by setting the keyId to the special uri `about:inline`, we
trigger a mechanism inside `pasture_http_signature` that fetches the public key from
the `X-Public-Key` header. This mechanism is meant to make the early steps of
implementing HTTP Signature easier. As one doesn't have to worry about providing
an URL, where the public key can be fetched.

Similarly, when passing the private key in the `X-Private-Key` header, one can
use it to get the expected value of the signature computed. Both fields take
as value the PEM encoded public key, then again base64 encoded.

## References

- Section HTTP Signatures in [How to implement a basic ActivityPub server](https://blog.joinmastodon.org/2018/06/how-to-implement-a-basic-activitypub-server/) on the Mastodon Blog by Eugen Rochko.
- [Signing HTTP Messages Draft Number 10](https://datatracker.ietf.org/doc/html/draft-cavage-http-signatures-10) by Cavage and Sporny
- [HTTP Message Signatures](https://datatracker.ietf.org/doc/draft-ietf-httpbis-message-signatures/) by Backmann, Richter, and Sporny
