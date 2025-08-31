<!--
SPDX-FileCopyrightText: 2023 Helge

SPDX-License-Identifier: CC-BY-4.0
-->

# Verifying your Actor

This tool allows one to verify that an ActivityPub Actor satisfies the
basic requirements for one:

- The Actor object can be retrieved with a GET request
- One can post to the Actor's Inbox using a POST request

A sequence of tests are run to verify behavior with respect to varying
scenarios of query behavior. The variation affects which requests
use HTTP Signatures and if the requesting actor has an acct-uri
associated through webfinger.

## Command line usage

::: mkdocs-click
    :module: fediverse_pasture.verify_actor
    :command: verify_actor
    :prog_name: python -m fediverse_pasture.verify_actor

One should note that the `domain` parameter can be different from the
one used to query the application. This means that if one opens
this application using `http://localhost:2909`, the application will
use the domain given by domain to identify the actors making requests.

## Exported methods

::: fediverse_pasture.verify_actor
