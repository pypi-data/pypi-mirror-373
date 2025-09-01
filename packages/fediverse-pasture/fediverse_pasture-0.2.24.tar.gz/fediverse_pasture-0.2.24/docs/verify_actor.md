<!--
SPDX-FileCopyrightText: 2023,2024 Helge

SPDX-License-Identifier: CC-BY-4.0
-->

# Verifying your Actor

!!! tip
    A live version is available at [https://verify.funfedi.dev/](https://verify.funfedi.dev/).
    Usage should be self explanatory, enter a Fediverse account into the search field
    and run the verification.

By using the `verify_actor` container provided by the Fediverse Pasture,
you can test your actor implementation. The following
screenshot shows the application in action.

![Screenshot from Verifying your actor](./assets/verifying_actor.png)

If the result is shown as, you should try to repair how you
authenticate requests to the inbox. By expanding the _Options_, you can
choose to just run one of the test cases. The actor personas are detailed
[here](#actor-personas).

## Setup to test inside a container network

The following assumes that your have a container network `network` and
which to test a container inside it.

=== "docker"

    ```bash
    docker run -p 2909:80 -ti \
      --network network \
      --hostname verify \
      helgekr/pasture verify_actor verify
    ```

=== "podman"

    ```bash
    podman run -p 2909:80 -ti \
      --network network \
      --hostname verify \
      docker.io/helgekr/pasture verify_actor verify
    ```

The option `-ti` is necessary, so you can terminate the process
with `CTRL+C`. `verify` is the hostname the container will use
inside the network.

This container now exposes port 2909, so one can open the web
interface on [http://localhost:2909/](http://localhost:2909/).

!!! note
    Instructions on how to run the python server can be found
    in the documentation of the `fediverse_pasture` python package,
    i.e. [here](./reference/server.md#fediverse_pasture.server.verify_actor)

## Usage

To use `verify_actor` start your Fediverse server in a docker container
and connect it to the network `fediverse-pasture_default`. Then when
you open [http://localhost:2909/](http://localhost:2909/) you are able to
enter your actor in one of the following formats

- `user@domain`, `@user@domain`, or the URI form `acct:user@domain`
- `http://your_server/your_actor_path` representing the Actor object

`verify_actor` then fetches the actor object and sends a message
to the inbox for each of the [actor personas](#actor-personas).
The result is then displayed in a table, where a successful request
is marked with an `X`.

The  message send to the inbox is an activity chosen to be accepted by
various applications. For example, this activity has an `id` property.
This is necessary due to some applications process the activity before
answering the request.

!!! tip
    You can use the first format to verify your webfinger implementation.

### Usage with ngrok

[ngrok](https://ngrok.com/) is a service that allows you to easily
serve a local port to the internet. In order to use it with `verify_actor`,
we will first start `ngrok` via

```bash
ngrok http 2909
```

This will display an URL, of the form `https://abcd-12-34-56-68.ngrok-free.app`.
From this take the domain name, and start `verify_actor` with

=== "docker"

    ```bash
    docker run -p 2909:80 -ti \
      helgekr/pasture verify_actor abcd-12-34-56-68.ngrok-free.app
    ```

=== "podman"

    ```bash
    podman run -p 2909:80 -ti \
      docker.io/helgekr/pasture verify_actor abcd-12-34-56-68.ngrok-free.app
    ```

You should now be able to open the URL, and thus run `verify_actor` against any
active Fediverse server.

## Actor Personas

`verify_actor` tests the Actor object and the inbox, with the following
actors.

1. An actor _Alice_ using unsigned GET and POST requests.
1. An actor _Bob_ using signed GET and POST requests, whose actor object can be retrieved with a unsigned GET request.
1. An actor _Claire_ using signed GET and POST requests, whose actor object requires a signed GET request to be retrieved.
1. _Dean_ similar to Alice but no webfinger
1. _Emily_ similar to Bob but no webfinger
1. _Frank_ similar to Claire but no webfinger

!!! caution
    Actors without acct-URI associated through webfinger are currently not common
    in the Fediverse. They exist to make people aware of this possibility.

Finally, `verify_actor` uses an Application actor _actor_. _actor_'s
configuration is the same as Bob. _actor_ is used by the application
to fetch public keys to run verification. See [Public Key Fetching](./technical_notes/public_key_fetching.md)
for technical details.

In the simplest form the result is displayed as a table showing if the
GET and POST requests were successful. The expected result is that both
of Bob's and Claire's requests are successful.

Alice's POST request should fail, and Alice's GET request may fail.

## Sample Results - on itself

For the usage on itself, we will not display the results for Dean, Emily, and Frank
as the tool does not make use of webfinger. You can however observe the difference,
as `alice@pasture_verify_actor` resolves but `dean@pasture_verify_actor` does not.

### http://pasture_verify_actor/alice

| Name   | GET Actor | POST Inbox |
| ------ | --------- | ---------- |
| alice  | X         | X          |
| bob    | X         | X          |
| claire | X         | X          |

This should be expected as `alice` does not check signatures. Also, we note that
`alice` is not an example to follow.

### http://pasture_verify_actor/bob

For bob, we see that posting to the inbox becomes protected.

| Name   | GET Actor | POST Inbox |
| ------ | --------- | ---------- |
| alice  | X         |            |
| bob    | X         | X          |
| claire | X         | X          |

### http://pasture_verify_actor/claire

For claire, we see that now also getting the actor object is protected.

| Name   | GET Actor | POST Inbox |
| ------ | --------- | ---------- |
| alice  |           |            |
| bob    | X         | X          |
| claire | X         | X          |

## Sample Results - Mastodon

The following results are for the actor `acct:jumbo@mastodon41web` from the Mastodon part
of the Fediverse Pasture. The meaning of `AUTHORIZED_FETCH` is explained in the
[Mastodon documentation](https://docs.joinmastodon.org/admin/config/#authorized_fetch).
The difference between these two implementations arises from the GET requests having
to be signed with `AUTHORIZED_FETCH = True`.

When implementing a Fediverse application, one should aim for that the result with
testing with `verify_actor` looks like one of the two tables.

### AUTHORIZED_FETCH = False

| Name   | GET Actor | POST Inbox |
| ------ | --------- | ---------- |
| alice  | X         |            |
| bob    | X         | X          |
| claire | X         | X          |
| dean   | X         |            |
| emily  | X         |            |
| frank  | X         |            |

### AUTHORIZED_FETCH = True

| Name   | GET Actor | POST Inbox |
| ------ | --------- | ---------- |
| alice  |           |            |
| bob    | X         | X          |
| claire | X         | X          |
| dean   |           |            |
| emily  |           |            |
| frank  |           |            |

### Raw output

In addition to the table above, `verify_actor` also provides a raw log
of the actions that were created to create the above table.

```json
{
  "steps": [
    "Got Actor Uri bob@mastodon_web",
    "Need to resolve bob@mastodon_web to actor object id",
    "Not in account uri format",
    "Resolving acct:bob@mastodon_web using webfinger",
    "Resolved to http://mastodon_web/users/bob",
    "Running verification for alice",
    "Got inbox http://mastodon_web/users/bob/inbox",
    "Got 401 for unsigned POST",
    "Running verification for bob",
    "Got inbox http://mastodon_web/users/bob/inbox",
    "Successfully posted to inbox",
    "Running verification for claire",
    "Got inbox http://mastodon_web/users/bob/inbox",
    "Successfully posted to inbox",
    "Running verification for dean",
    "Got inbox http://mastodon_web/users/bob/inbox",
    "Got 401 for unsigned POST",
    "Running verification for emily",
    "Got inbox http://mastodon_web/users/bob/inbox",
    "Failed to post to inbox",
    "ClientResponseError(RequestInfo(url=URL('http://mastodon_web/users/bob/inbox'), method='POST', headers=, real_url=URL('http://mastodon_web/users/bob/inbox')), (), status=401, message='Unauthorized', headers=)",
    "Running verification for frank",
    "Got inbox http://mastodon_web/users/bob/inbox",
    "Failed to post to inbox",
    "ClientResponseError(RequestInfo(url=URL('http://mastodon_web/users/bob/inbox'), method='POST', headers=, real_url=URL('http://mastodon_web/users/bob/inbox')), (), status=401, message='Unauthorized', headers=)",
    "Running verification for actor",
    "Got inbox http://mastodon_web/users/bob/inbox",
    "Got 401 for unsigned POST"
  ]
}
```

## Known Implementation Challenges

I believe that getting this test case to clear is a good first
step towards being able to have a running Fediverse server. I want
to collect some challenges here, that I know people stumbled over
in order to help you debug.

1. Your server needs to be able to answer simultaneous requests in
  order to handle verification for Claire. This means that starting
  your application as the simplest development setup might not work.
2. The format for the date header is in [RFC 9110](https://www.rfc-editor.org/rfc/rfc9110#http.date). The obsolete formats are not supported.
