from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.hashers import make_password
from django.contrib.auth.hashers import check_password
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.core.mail import send_mail
import random


from .models import Usuario, Cliente, Administrador, Solicitacao, Endereco

def index(request):
    return render(request, 'index.html')

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

    usuario_id = request.session.get('usuario_id')

    usuario = Usuario.objects.get(id=usuario_id)

    cliente = Cliente.objects.get(usuario=usuario)

    solicitacoes = Solicitacao.objects.filter(
        cliente=cliente
    ).order_by('-id')

    return render(request, 'areaDoCliente.html', {
        'solicitacoes': solicitacoes
})

def login_adm(request):

    if request.method == 'POST':

        email = request.POST.get('email')
        senha = request.POST.get('senha')

        try:

            adm = Administrador.objects.get(email=email)

            if check_password(senha, adm.senha_hash):

                codigo = str(random.randint(100000, 999999))

                adm.codigo_verificacao = codigo
                adm.save()

                send_mail(
                    'Código de verificação',
                    f'Seu código é: {codigo}',
                    'seuemail@gmail.com',
                    [email],
                    fail_silently=False,
                )

                request.session['adm_id_temp'] = adm.id

                return redirect('codigo_adm')

            else:

                return render(request, 'loginAdm.html', {
                    'erro': 'Senha incorreta.'
                })

        except Administrador.DoesNotExist:

            return render(request, 'loginAdm.html', {
                'erro': 'Administrador não encontrado.'
            })

    return render(request, 'loginAdm.html')

def codigo_adm(request):

    if request.method == 'POST':

        codigo = request.POST.get('codigo')

        adm_id = request.session.get('adm_id_temp')

        if not adm_id:
            return redirect('login_adm')

        adm = Administrador.objects.get(id=adm_id)

        if adm.codigo_verificacao == codigo:

            request.session['adm_id'] = adm.id
            request.session['adm_nome'] = adm.nome

            del request.session['adm_id_temp']

            return redirect('dashboard_adm')

        else:

            return render(request, 'codAdm.html', {
                'erro': 'Código inválido.'
            })

    return render(request, 'codAdm.html')

def dashboard_adm(request):

    if not request.session.get('adm_id'):
        return redirect('login_adm')

    nome = request.session.get('adm_nome')

    return render(request, 'AdminPage.html', {
        'nome': nome
    })

def recuperar_senha(request):

    if request.method == 'POST':

        email = request.POST.get('email')

        try:
            usuario = Usuario.objects.get(email=email)

        except Usuario.DoesNotExist:
            return render(request, 'recuperarSenha.html', {
                'erro': 'Email não encontrado.'
            })

        codigo = str(random.randint(100000, 999999))

        request.session['codigo_recuperacao'] = codigo
        request.session['email_recuperacao'] = email

        send_mail(
            'Código de recuperação - FETELECOM',
            f'Seu código é: {codigo}',
            settings.EMAIL_HOST_USER,
            [email],
            fail_silently=False,
        )

        return redirect('validar_codigo')

    return render(request, 'recuperarSenha.html')

def validar_codigo(request):

    if request.method == 'POST':

        codigo = request.POST.get('codigo')

        if codigo == request.session.get('codigo_recuperacao'):

            return redirect('nova_senha')

        return render(request, 'validarCodigo.html', {
            'erro': 'Código inválido.'
        })

    return render(request, 'validarCodigo.html')

def nova_senha(request):

    if request.method == 'POST':

        senha = request.POST.get('senha')
        confirmar = request.POST.get('confirmar')

        if senha != confirmar:

            return render(request, 'novaSenha.html', {
                'erro': 'As senhas não coincidem.'
            })

        email = request.session.get('email_recuperacao')

        usuario = Usuario.objects.get(email=email)

        usuario.senha_hash = make_password(senha)

        usuario.save()

        del request.session['codigo_recuperacao']
        del request.session['email_recuperacao']

        return redirect('login')

    return render(request, 'novaSenha.html')

def nova_senha(request):

    email = request.session.get('email_recuperacao')

    if not email:
        return redirect('recuperar_senha')

    if request.method == 'POST':

        nova_senha = request.POST.get('nova_senha')
        confirmar = request.POST.get('confirmar_senha')

        if nova_senha != confirmar:

            return render(request, 'novaSenha.html', {
                'erro': 'As senhas não coincidem.'
            })

        usuario = Usuario.objects.get(email=email)

        usuario.senha_hash = make_password(nova_senha)

        usuario.save()

        return render(request, 'novaSenha.html', {
            'sucesso': 'Senha atualizada com sucesso!'
        })

    return render(request, 'novaSenha.html')

def criar_solicitacao(request):

    if request.method == 'POST':

        print(request.POST)

        tipo = request.POST.get('tipo_servico')

        endereco = request.POST.get('endereco')

        data = request.POST.get('data')

        horario = request.POST.get('horario')

        porte_local = request.POST.get('porte_local')

        detalhes = request.POST.get('detalhes')

        usuario_id = request.session.get('usuario_id')

        usuario = Usuario.objects.get(id=usuario_id)

        cliente = Cliente.objects.get(usuario=usuario)

        solicitacao = Solicitacao.objects.create(

            cliente=cliente,

            tipo_servico=tipo,

            data_disponivel=data,

            horario_disponivel=horario,

            porte_local=porte_local,

            detalhes=detalhes

        )

        Endereco.objects.create(

            solicitacao=solicitacao,

            rua=endereco,

            bairro='Não informado',

            numero='S/N',

            cidade='Não informado'

        )

        return redirect('area_cliente')

    return redirect('area_cliente')

def area_cliente(request):

    usuario_id = request.session.get('usuario_id')

    usuario = Usuario.objects.get(id=usuario_id)

    cliente = Cliente.objects.get(usuario=usuario)

    solicitacoes = Solicitacao.objects.filter(
        cliente=cliente
    ).order_by('-id')

    total_solicitacoes = solicitacoes.count()

    primeiro_nome = usuario.nome.split()[0]

    return render(request, 'areaDoCliente.html', {
        'solicitacoes': solicitacoes,
        'total_solicitacoes': total_solicitacoes,
        'primeiro_nome': primeiro_nome
    })

def editar_solicitacao(request, id):

    usuario_id = request.session.get('usuario_id')

    if not usuario_id:
        return redirect('login')

    usuario = Usuario.objects.get(id=usuario_id)

    cliente = Cliente.objects.get(usuario=usuario)

    solicitacao = Solicitacao.objects.get(
        id=id,
        cliente=cliente
    )

    # impede edição se status bloquear
    if not solicitacao.pode_editar:

        messages.error(
            request,
            'Esta solicitação não pode mais ser editada.'
        )

        return redirect('area_cliente')

    endereco = Endereco.objects.get(
        solicitacao=solicitacao
    )

    if request.method == 'POST':

        solicitacao.tipo_servico = request.POST.get('tipo_servico')

        solicitacao.data_disponivel = request.POST.get('data')

        solicitacao.horario_disponivel = request.POST.get('horario')

        solicitacao.porte_local = request.POST.get('porte_local')

        solicitacao.detalhes = request.POST.get('detalhes')

        solicitacao.save()

        endereco.rua = request.POST.get('endereco')

        endereco.save()

        messages.success(
            request,
            'Solicitação atualizada com sucesso!'
        )

        return redirect('area_cliente')

    return render(request, 'editarSolicitacao.html', {
        's': solicitacao,
        'endereco': endereco
    })