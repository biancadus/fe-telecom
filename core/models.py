from django.db import models


class Usuario(models.Model):
    nome = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    senha_hash = models.CharField(max_length=255)
    is_admin = models.BooleanField(default=False)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'usuarios'


class Cliente(models.Model):
    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    nome = models.CharField(max_length=150)
    telefone = models.CharField(
    max_length=20,
    unique=True,
    null=True,
    blank=True
)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'clientes'


class Contato(models.Model):
    cliente = models.ForeignKey(
        Cliente,
        on_delete=models.CASCADE
    )

    celular = models.CharField(max_length=20, unique=True)
    telefone = models.CharField(max_length=20, null=True, blank=True)
    email = models.EmailField(unique=True, null=True, blank=True)

    class Meta:
        db_table = 'contatos'
        
class Administrador(models.Model):

    nome = models.CharField(max_length=100)

    email = models.EmailField(unique=True)

    senha_hash = models.CharField(max_length=255)

    codigo_verificacao = models.CharField(
        max_length=6,
        blank=True,
        null=True
    )

    def __str__(self):
        return self.nome