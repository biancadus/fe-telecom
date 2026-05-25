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

class Solicitacao(models.Model):

    STATUS_CHOICES = [
        ('Recebida', 'Recebida'),
        ('Em análise', 'Em análise'),
        ('Agendada', 'Agendada'),
        ('Em andamento', 'Em andamento'),
        ('Concluída', 'Concluída'),
        ('Cancelada', 'Cancelada'),
    ]

    cliente = models.ForeignKey(
        'Cliente',
        on_delete=models.CASCADE
    )

    tipo_servico = models.CharField(max_length=100)

    data_disponivel = models.DateField()

    horario_disponivel = models.TimeField()

    porte_local = models.CharField(max_length=20)

    status = models.CharField(
        max_length=30,
        choices=STATUS_CHOICES,
        default='Recebida'
    )

    detalhes = models.TextField()

    criado_em = models.DateTimeField(auto_now_add=True)

    concluido_em = models.DateTimeField(
        null=True,
        blank=True
    )

    @property
    def pode_editar(self):

        status_bloqueados = [
            'Agendada',
            'Em andamento',
            'Concluída',
            'Cancelada'
        ]

        return self.status not in status_bloqueados

    def __str__(self):
        return f'Solicitação #{self.id}'

class Endereco(models.Model):

    solicitacao = models.OneToOneField(
        Solicitacao,
        on_delete=models.CASCADE
    )

    rua = models.CharField(max_length=255)

    bairro = models.CharField(max_length=255)

    numero = models.CharField(max_length=20)

    complemento = models.CharField(
        max_length=150,
        blank=True,
        null=True
    )

    cidade = models.CharField(max_length=100)

    def __str__(self):
        return self.rua