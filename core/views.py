from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.hashers import make_password
from django.contrib.auth.hashers import check_password

from .models import Usuario, Cliente


def cadastro(request):

    if request.method == 'POST':

        nome = request.POST.get('nome')
        email = request.POST.get('email')
        senha = request.POST.get('senha')
        confirmar = request.POST.get('confirmar_senha')
        telefone = request.POST.get('telefone')

        #para o telefone salvar 11999999999 no banco ao invés de (11) 99999-9999
        telefone = ''.join(filter(str.isdigit, telefone))

        if senha != confirmar:
            messages.error(request, 'As senhas não coincidem')
            return redirect('cadastro')

        if Usuario.objects.filter(email=email).exists():

            return render(request, 'cadastro.html', {
                'erro': 'Este email já está cadastrado.'
            })

        if Cliente.objects.filter(telefone=telefone).exists():

            return render(request, 'cadastro.html', {
                'erro': 'Este telefone já está cadastrado.'
            })

        usuario = Usuario.objects.create(
            nome=nome,
            email=email,
            senha_hash=make_password(senha)
        )

        Cliente.objects.create(
            usuario=usuario,
            nome=nome,
            telefone=telefone
        )

        messages.success(request, 'Conta criada com sucesso')

        return redirect('login')

    return render(request, 'cadastro.html')


def login_view(request):

    if request.method == 'POST':

        email = request.POST.get('email')
        senha = request.POST.get('senha')

        try:
            usuario = Usuario.objects.get(email=email)

            if check_password(senha, usuario.senha_hash):

                # cria sessão
                request.session['usuario_id'] = usuario.id
                request.session['usuario_nome'] = usuario.nome

                return redirect('area_cliente')

            else:
                return render(request, 'login.html', {
                    'erro': 'Senha incorreta.'
                })

        except Usuario.DoesNotExist:

            return render(request, 'login.html', {
                'erro': 'Email não encontrado.'
            })

    return render(request, 'login.html')

def area_cliente(request):

    if not request.session.get('usuario_id'):
        return redirect('login')

    nome = request.session.get('usuario_nome')

    return render(request, 'areaDoCliente.html', {
        'nome': nome
    })