from __future__ import annotations

from tortoise import fields, models

from epona.common import create_suuid


class Geometry(models.Model):
    suuid = fields.CharField(primary_key=True, max_length=13, default=create_suuid())
    id_entity = fields.CharField(max_length=13, null=False)
    entity_name = fields.CharField(max_length=20, null=False)
    representation = fields.CharField(max_length=20, null=True)
    geom_type = fields.CharField(max_length=20, null=False)
    zoom = fields.IntField(null=True)

    class Meta:
        table = "geometries"
