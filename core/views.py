from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from .models import Cliente

def cadastro_view(request):
    # Se o usuário clicou no botão (POST)
    if request.method == 'POST':
        print(f"Dados recebidos: {request.POST}")

        usuario = request.POST.get('username')
        email = request.POST.get('email')
        senha = request.POST.get('password1') # Nome que você confirmou

        if usuario and senha:
            novo_usuario = User.objects.create_user(
                username=usuario, 
                email=email, 
                password=senha
            )
        
            Cliente.objects.create(
                nome=usuario,
                email=email,
                senha=senha  # Nota: No Cliente a senha fica em texto simples se o campo for CharField
            )
            
    # Se ele apenas abriu a página (GET)
    return render(request, 'cadastro.html')

def login_view(request):
    return render(request, 'login.html')
