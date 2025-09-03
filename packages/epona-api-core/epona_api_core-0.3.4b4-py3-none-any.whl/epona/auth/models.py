from datetime import datetime

from tortoise import fields, models


class User(models.Model):
    id = fields.IntField(primary_key=True)
    active = fields.BooleanField(default=True)
    client_id = fields.CharField(max_length=50, null=True)
    email = fields.CharField(max_length=200, null=True)
    scope = fields.TextField(has_db_field=False)
    username = fields.CharField(max_length=50, null=False)
    password_hash = fields.CharField(max_length=300, null=False)
    permissions: fields.ReverseRelation["UserPermission"]
    created_at = fields.DatetimeField(null=True, default=datetime.now())
    updated_at = fields.DatetimeField(null=True, default=datetime.now())

    def __str__(self) -> str:
        return self.username

    class Meta:
        table = "users"


class Client(models.Model):
    id = fields.IntField(primary_key=True)
    active = fields.BooleanField()
    activity_sectors_id = fields.IntField(null=False)
    full_name = fields.CharField(max_length=300, null=True)
    image_url = fields.CharField(max_length=300, null=True)
    logo_url = fields.CharField(max_length=300, null=True)
    multiple_domains = fields.BooleanField(null=True, default=False)
    name = fields.CharField(max_length=50)
    valid_domains = fields.CharField(max_length=500, null=True)
    created_at = fields.DatetimeField(null=True, default=datetime.now())
    updated_at = fields.DatetimeField(null=True, default=datetime.now())

    class Meta:
        table = "clients"


class Permission(models.Model):
    id = fields.IntField(primary_key=True)
    name = fields.CharField(max_length=50)
    description = fields.CharField(max_length=50)
    created_at = fields.DatetimeField(null=True)
    updated_at = fields.DatetimeField(null=True)

    class Meta:
        table = "permissions"


class UserPermission(models.Model):
    id = fields.IntField(primary_key=True)
    client_id = fields.CharField(max_length=50)
    entities = fields.TextField()

    permission: fields.ForeignKeyRelation[Permission] = fields.ForeignKeyField(
        "models.Permission", related_name="permission"
    )
    user: fields.ForeignKeyRelation[User] = fields.ForeignKeyField(
        "models.User", related_name="permissions"
    )

    class Meta:
        table = "users_permissions"
