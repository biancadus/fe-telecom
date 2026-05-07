from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from .models import Cliente
from django.http import HttpResponse

def cadastro(request):

    if request.method == 'POST':

        nome = request.POST.get('nome')
        cpf = request.POST.get('cpf')
        telefone = request.POST.get('telefone')
        plano = request.POST.get('plano')

        Cliente.objects.create(
            nome=nome,
            cpf=cpf,
            telefone=telefone,
            plano=plano
        )

        return redirect('cadastro')
        
    return render(request, 'cadastro.html')

def login_view(request):
    return render(request, 'login.html')

def home(request):
    return HttpResponse("<h1>Sistema FE-Telecom</h1><p>O banco de dados e o servidor estão funcionando!</p>")