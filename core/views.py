from django.shortcuts import render
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.models import User
from django.shortcuts import render, redirect



def cadastro_view(request):
    if request.method == 'POST':
        nome = request.POST.get('username')
        email = request.POST.get('email')
        senha = request.POST.get('password1')

        # CRITICAL: Aqui é onde o dado entra no banco
        if nome and email and senha:
            # create_user já faz o hash da senha automaticamente
            User.objects.create_user(username=nome, email=email, password=senha)
            messages.success(request, "Usuário criado!")
            return redirect('login') 
        
    return render(request, 'cadastro.html')