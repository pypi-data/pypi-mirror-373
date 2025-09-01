<!--
SPDX-FileCopyrightText: 2023 Helge

SPDX-License-Identifier: CC-BY-4.0
-->

# Public Key Fetching

In this technical note, I want to illustrate what happens when
fetching public keys. I will use the names from
[Verifying your Actor](../verify_actor.md).
As a reminder, Alice requires no HTTP Signatures to be present
and thus does not check them. Bob only checks signatures for POST
requests. Finally, Claire checks HTTP Signatures for GET requests.
We will assume that the Remote participant mirrors Alice's, Bob's,
and Claire's behavior.

The number of requests required for Bob and Claire may seem high.
Deployed Fediverse applications will have mechanisms for key caching,
so the actual number of requests for Alice, Bob, and Claire will be
the same.

## Alice: No public key fetching

```mermaid
sequenceDiagram
    box
    Actor Alice
    Participant Alice's App
    end
    box
    Participant Remote App
    Actor Remote
    end

    Alice->>+Remote: GET actor
    Remote->>+Alice: Here's my Profile
```

## Bob: Key fetch for post

We discuss posting to the inbox here, instead of a GET request.
The behavior of a GET request is the same as Alice.

```mermaid
sequenceDiagram
    box
    Actor Bob
    Participant Bob's App
    end
    box
    Participant Remote App
    Actor Remote
    end

    Bob->>+Remote: signed POST to Inbox
    Remote App->>+Bob: GET for Bob's public key
    Bob->>+Remote App: Here's my public key
    Remote->>+Bob: Message accepted
```

## Claire: Requiring signatures for GET

The case of Claire's POST is the same as Claire's GET. One should furthermore
note that the Application Actors to not check the signature on the GET to
retrieve their public keys. If such a signature check was done, the process
would be thrown into an infinite loop.

```mermaid
sequenceDiagram
    box
    Actor Claire
    Participant Claire's App
    end
    box
    Participant Remote App
    Actor Remote
    end

    Claire->>+Remote: signed GET actor
    Remote App->>+Claire: Signed GET for Claire's public key
    Claire's App->>+Remote App: Signed GET for Remote App's public key
    Remote App->>+Claire's App: Here's my public key
    Claire->>+Remote App: Here's my public key
    Remote->>+Claire: Here's my Profile
```
