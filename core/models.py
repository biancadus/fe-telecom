from django.db import models

class Cliente(models.Model):
    PLANOS = [
        ('FIBRA', 'Fibra Óptica'),
        ('RADIO', 'Via Rádio'),
    ]
    
    nome = models.CharField(max_length=100)
    cpf = models.CharField(max_length=14, unique=True)
    telefone = models.CharField(max_length=15)
    plano = models.CharField(max_length=10, choices=PLANOS, default='FIBRA')
    ativo = models.BooleanField(default=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nome