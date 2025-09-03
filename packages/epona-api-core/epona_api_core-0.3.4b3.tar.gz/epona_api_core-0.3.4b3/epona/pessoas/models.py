from datetime import datetime

from tortoise import fields, models

from epona.common import create_suuid


class Pessoa(models.Model):
    suuid = fields.CharField(max_length=13, default=create_suuid(), primary_key=True)
    cadastro = fields.CharField(null=True, max_length=20)
    client_id = fields.CharField(max_length=50, null=True)
    cpf_cnpj = fields.CharField(max_length=15)
    documento = fields.CharField(max_length=20, null=True)
    email = fields.CharField(max_length=100, null=True)
    licenciavel = fields.BooleanField(default=False)
    matriz = fields.BooleanField(default=False)
    nome = fields.CharField(max_length=100)
    nome_fantasia = fields.CharField(max_length=100, null=True)
    pessoa_id = fields.IntField(null=True)
    pessoa_suuid = fields.CharField(max_length=13, null=True)
    tipo = fields.CharField(max_length=20)
    tipo_cadastro = fields.CharField(max_length=20, null=True)
    tipo_documento = fields.CharField(max_length=20, null=True)
    created_at = fields.DatetimeField(null=True, default=datetime.now())
    updated_at = fields.DatetimeField(null=True, default=datetime.now())

    def __str__(self):
        return self.suuid

    class Meta:
        table = "pessoa"


class InfoContato(models.Model):
    suuid = fields.CharField(max_length=13, default=create_suuid(), primary_key=True)
    client_id = fields.CharField(max_length=50)
    email = fields.CharField(max_length=50, null=True)
    pessoa_suuid = fields.CharField(max_length=13, null=False)
    telefone = fields.CharField(max_length=50, null=True)
    tipo = fields.CharField(max_length=20, null=True)
    created_at = fields.DatetimeField(default=datetime.utcnow(), null=True)

    def __str__(self):
        return self.suuid

    class Meta:
        table = "info_contato"
