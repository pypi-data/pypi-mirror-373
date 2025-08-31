<!--
SPDX-FileCopyrightText: 2023 Helge

SPDX-License-Identifier: CC-BY-4.0
-->

# The Fediverse Pasture

The goal of this python package is to provide testing tools. It
uses [bovine](https://bovine.readthedocs.io/en/latest/) for basic
Fediverse functionality.

<div class="grid cards" markdown>

- [:material-check:{ .lg .middle } __Verify your Actor__](https://verify.funfedi.dev/)

    ---

    Enables you to check your implementation of your Fediverse actor.

    [:octicons-arrow-right-24: Documentation](./verify_actor.md)

    [:octicons-arrow-right-24: Code Reference](./reference/server.md#fediverse_pasture.server.verify_actor)

- [:material-table:{ .lg .middle } __Support tables__](https://funfedi.dev/support_tables/)

    ---

    This python package together with [fediverse-pasture-inputs](https://inputs.funfedi.dev/)
    provide the basis of creating the support tables

    [:octicons-arrow-right-24: One Actor Server](./one_actor.md)

    [:octicons-arrow-right-24: Runner Reference](./reference/runner.md)

</div>

This package is more for people who either don't want to use docker
or want to modify the tooling. For example fediverse_pasture.runner
provides tools that might be helpful in testing how activities are
processed by the various Fediverse applications.

## Installation

This package can be installed from [pypi](https://pypi.org/project/fediverse-pasture/)
via

```bash
pip install fediverse-pasture
```

Instructions for usage can be found in the following sections.

## Development

Instructions to develop this python package can be found
at [codeberg.org](https://codeberg.org/funfedidev/python_fediverse_pasture).

## Funding

This code was created as part of [Fediverse Test Framework](https://nlnet.nl/project/FediverseTestFramework/).

A project funded through the [NGI0 Core](https://nlnet.nl/core) Fund,
a fund established by [NLnet](https://nlnet.nl/) with financial support from
the European Commission's [Next Generation Internet](https://ngi.eu/) programme,
under the aegis of DG Communications Networks, Content and Technology
under grant agreement No 101092990.
