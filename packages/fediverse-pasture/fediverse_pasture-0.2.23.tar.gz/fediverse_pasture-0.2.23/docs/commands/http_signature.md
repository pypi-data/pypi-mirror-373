<!--
SPDX-FileCopyrightText: 2023 Helge

SPDX-License-Identifier: CC-BY-4.0
-->

# Signing with HTTP Signatures

Provides a server to test HTTP Signatures against. The usage is simple
make a GET or POST request to the `/` endpoint to verify your signature implementation.

## Command line usage

::: mkdocs-click
    :module: fediverse_pasture.http_signature
    :command: http_signature
    :prog_name: python -m fediverse_pasture.http_signature
