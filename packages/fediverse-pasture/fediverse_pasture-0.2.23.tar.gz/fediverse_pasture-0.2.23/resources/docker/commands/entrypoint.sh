#!/bin/sh

# SPDX-FileCopyrightText: 2024-2025 Helge
#
# SPDX-License-Identifier: MIT


PASTURE_INIT_FILE="pasture_init_file"

if [ ! -e $PASTURE_INIT_FILE ]; then
    touch $PASTURE_INIT_FILE
    python -m fediverse_pasture.one_actor --only_generate_config
fi

PATH=$PATH:/opt/pasture

exec "$@"
