# SPDX-FileCopyrightText: 2023 Helge
#
# SPDX-License-Identifier: MIT

from tortoise.models import Model
from tortoise import fields


class TestRecord(Model):
    id = fields.IntField(primary_key=True)
    test_name = fields.CharField(max_length=255)
    application_name = fields.CharField(max_length=255)

    data = fields.JSONField()

    class Meta:
        unique_together = (("test_name", "application_name"),)
