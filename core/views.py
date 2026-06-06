from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.core.mail import send_mail, EmailMultiAlternatives
from django.db.models import Count, Q
from django.db.models.functions import TruncMonth
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404
import random

from .models import Usuario, Cliente, Administrador, Solicitacao, Endereco, Notificacao

def index(request):
    return render(request, 'index.html')

def logout_view(request):
    logout(request)
    request.session.flush()
    return redirect('login')

def cadastro(request):
    if request.method == 'POST':
        nome = request.POST.get('nome')
        email = request.POST.get('email')
        senha = request.POST.get('senha')
        confirmar = request.POST.get('confirmar_senha')
        telefone = request.POST.get('telefone')

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
    if not usuario_id:
        return redirect('login')
    try:
        cliente = Cliente.objects.select_related('usuario').get(usuario_id=usuario_id)
        usuario = cliente.usuario
    except Cliente.DoesNotExist:
        return redirect('login')
    
    solicitacoes_base = Solicitacao.objects.filter(cliente=cliente)

    total_solicitacoes = solicitacoes_base.count()
    em_analise = solicitacoes_base.filter(status='Em análise').count()  
    agendadas = solicitacoes_base.filter(status='Agendada').count()
    concluidas = solicitacoes_base.filter(status='Concluída').count()
    canceladas = solicitacoes_base.filter(status='Cancelada').count()

    solicitacoes_listagem = solicitacoes_base.order_by('-id')

    termo_busca = request.GET.get('busca', '').strip()
    status_filtro = request.GET.get('status_filtro', '').strip()

    if termo_busca:
        if termo_busca.isdigit():
            solicitacoes_listagem = solicitacoes_listagem.filter(Q(id=int(termo_busca)))
        else:
            solicitacoes_listagem = solicitacoes_listagem.filter(
                Q(tipo_servico__icontains=termo_busca) | Q(porte_local__icontains=termo_busca)
            )

    if status_filtro:
        solicitacoes_listagem = solicitacoes_listagem.filter(status=status_filtro)

    primeiro_nome = usuario.nome.split()[0]
    notificacoes = cliente.notificacoes.all()[:20]
    nao_lidas = cliente.notificacoes.filter(lida=False).count()

    return render(request, 'areaDoCliente.html', {
        'solicitacoes': solicitacoes_listagem,
        'total_solicitacoes': total_solicitacoes,
        'em_analise': em_analise,         
        'agendadas': agendadas,            
        'concluidas': concluidas,
        'canceladas': canceladas,
        'primeiro_nome': primeiro_nome,
        'termo_busca': termo_busca,
        'status_atual': status_filtro,   
        'notificacoes': notificacoes,
        'nao_lidas': nao_lidas,
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

                # CORREÇÃO: Utiliza o remetente dinâmico configurado no settings.py
                send_mail(
                    'Código de verificação',
                    f'Seu código é: {codigo}',
                    settings.DEFAULT_FROM_EMAIL,
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

    contagens = Solicitacao.objects.aggregate(
        para_analisar=Count('id', filter=Q(status='Recebida')),
        agendadas=Count('id', filter=Q(status='Agendada')),
        em_andamento=Count('id', filter=Q(status='Em andamento')),
        concluidas=Count('id', filter=Q(status='Concluída')),
        canceladas=Count('id', filter=Q(status='Cancelada'))
    )

    solicitacoes_mes = (
        Solicitacao.objects
        .annotate(mes=TruncMonth('criado_em'))
        .values('mes')
        .annotate(total=Count('id'))
        .order_by('mes')
    )

    meses = []
    totais = []

    for item in solicitacoes_mes:
        meses.append(item['mes'].strftime('%b/%Y'))
        totais.append(item['total'])

    tipos_servico = (
        Solicitacao.objects
        .values('tipo_servico')
        .annotate(total=Count('id'))
        .order_by('-total')
    )

    tipos = []
    totais_tipos = []

    for item in tipos_servico:
        tipos.append(item['tipo_servico'])
        totais_tipos.append(item['total'])

    return render(request, 'adminPage.html', {
        'nome': nome,
        'para_analisar': contagens['para_analisar'],
        'agendadas': contagens['agendadas'],
        'em_andamento': contagens['em_andamento'],
        'concluidas': contagens['concluidas'],
        'canceladas': contagens['canceladas'],
        'grafico_mensal': zip(meses, totais),
        'grafico_tipos': zip(tipos, totais_tipos),
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

        # CORREÇÃO: Alinhado para DEFAULT_FROM_EMAIL
        send_mail(
            'Código de recuperação - FETELECOM',
            f'Seu código é: {codigo}',
            settings.DEFAULT_FROM_EMAIL,
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

        request.session.pop('codigo_recuperacao', None)
        request.session.pop('email_recuperacao', None)

        messages.success(request, 'Senha updated com sucesso!')
        return redirect('login')

    return render(request, 'novaSenha.html')

def criar_solicitacao(request):
    if request.method == 'POST':
        tipo = request.POST.get('tipo_servico')
        rua = request.POST.get('rua')
        bairro = request.POST.get('bairro')
        numero = request.POST.get('numero')
        cidade = request.POST.get('cidade')
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
            rua=rua,
            bairro=bairro,
            numero=numero,
            cidade=cidade
        )

        return redirect('area_cliente')

def editar_solicitacao(request, id):
    usuario_id = request.session.get('usuario_id')

    if not usuario_id:
        return redirect('login')

    usuario = Usuario.objects.get(id=usuario_id)
    cliente = Cliente.objects.get(usuario=usuario)
    solicitacao = Solicitacao.objects.get(id=id, cliente=cliente)

    if not solicitacao.pode_editar:
        messages.error(request, 'Esta solicitação não pode mais ser editada.')
        return redirect('area_cliente')

    endereco = Endereco.objects.get(solicitacao=solicitacao)

    if request.method == 'POST':
        solicitacao.tipo_servico = request.POST.get('tipo_servico')
        solicitacao.data_disponivel = request.POST.get('data')
        solicitacao.horario_disponivel = request.POST.get('horario')
        solicitacao.porte_local = request.POST.get('porte_local')
        solicitacao.detalhes = request.POST.get('detalhes')
        solicitacao.save()

        endereco.rua = request.POST.get('rua')
        endereco.numero = request.POST.get('numero')
        endereco.bairro = request.POST.get('bairro')
        endereco.cidade = request.POST.get('cidade')
        endereco.save()

        messages.success(request, 'Solicitação atualizada com sucesso!')
        return redirect('area_cliente')

    return render(request, 'editarSolicitacao.html', {
        's': solicitacao,
        'endereco': endereco
    })

def clientes_adm(request):
    if not request.session.get('adm_id'):
        return redirect('login_adm')

    clientes = Cliente.objects.select_related('usuario').all().order_by('id')
    busca = request.GET.get('busca', '').strip()
    filtro = request.GET.get('filtro', '').strip()

    if busca:
        if filtro == 'id' and busca.isdigit():
            clientes = clientes.filter(id=int(busca))
        elif filtro == 'nome':
            clientes = clientes.filter(nome__icontains=busca)
        elif filtro == 'email':
            clientes = clientes.filter(usuario__email__icontains=busca)
        elif filtro == 'telefone':
            clientes = clientes.filter(telefone__icontains=busca)

    paginator = Paginator(clientes, 5)
    page_number = request.GET.get('page')
    clientes_page = paginator.get_page(page_number)

    return render(request, 'adminPage2.html', {
        'clientes': clientes_page,
        'busca': busca,
        'filtro': filtro
    })

def excluir_cliente(request, id):
    if not request.session.get('adm_id'):
        return redirect('login_adm')

    cliente = Cliente.objects.get(id=id)
    usuario = cliente.usuario
    cliente.delete()

    if usuario:
        usuario.delete()

    return redirect('clientes_adm')

def solicitacoes_adm(request):
    if not request.session.get('adm_id'):
        return redirect('login_adm')

    solicitacoes = (
        Solicitacao.objects
        .select_related('cliente', 'endereco')
        .all()
        .order_by('id')
    )

    busca = request.GET.get('busca', '').strip()
    filtro = request.GET.get('filtro', '').strip()
    data = request.GET.get('data', '').strip()

    if filtro == 'data' and data:
        solicitacoes = solicitacoes.filter(data_disponivel=data)
    elif busca:
        if filtro == 'id' and busca.isdigit():
            solicitacoes = solicitacoes.filter(id=int(busca))
        elif filtro == 'cliente':
            solicitacoes = solicitacoes.filter(cliente__nome__icontains=busca)
        elif filtro == 'status':
            solicitacoes = solicitacoes.filter(status__icontains=busca)
        elif filtro == 'servico':
            solicitacoes = solicitacoes.filter(tipo_servico__icontains=busca)
        elif filtro == 'endereco':
            solicitacoes = solicitacoes.filter(endereco__rua__icontains=busca)
        elif filtro == 'horario':
            solicitacoes = solicitacoes.filter(horario_disponivel__icontains=busca)

    paginator = Paginator(solicitacoes, 5)
    page_number = request.GET.get('page')
    solicitacoes_page = paginator.get_page(page_number)

    return render(request, 'adminPage3.html', {
        'solicitacoes': solicitacoes_page,
        'busca': busca,
        'filtro': filtro,
        'data': data
    })

def editar_solicitacao_adm(request, id):
    if not request.session.get('adm_id'):
        return redirect('login_adm')

    solicitacao = get_object_or_404(Solicitacao, id=id)
    endereco = Endereco.objects.get(solicitacao=solicitacao)

    if request.method == 'POST':
        solicitacao.tipo_servico = request.POST.get('tipo_servico')
        solicitacao.data_disponivel = request.POST.get('data')
        solicitacao.horario_disponivel = request.POST.get('horario')
        solicitacao.porte_local = request.POST.get('porte_local')
        solicitacao.detalhes = request.POST.get('detalhes')
        solicitacao.save()

        Notificacao.objects.create(
            cliente=solicitacao.cliente,
            titulo='Solicitação atualizada',
            mensagem=f'Os dados da solicitação #{solicitacao.id} foram atualizados pela equipe.'
        )

        endereco.rua = request.POST.get('rua')
        endereco.bairro = request.POST.get('bairro')
        endereco.numero = request.POST.get('numero')
        endereco.cidade = request.POST.get('cidade')
        endereco.save()

        return redirect('solicitacoes_adm')

    return render(request, 'editarSolicitacaoAdm.html', {
        's': solicitacao,
        'endereco': endereco
    })

def excluir_solicitacao(request, id):
    if not request.session.get('adm_id'):
        return redirect('login_adm')

    solicitacao = get_object_or_404(Solicitacao, id=id)
    solicitacao.delete()
    return redirect('solicitacoes_adm')

def alterar_status(request, id):
    if not request.session.get('adm_id'):
        return redirect('login_adm')

    solicitacao = get_object_or_404(
        Solicitacao.objects.select_related('cliente__usuario'),
        id=id
    )

    if request.method != 'POST':
        return redirect('solicitacoes_adm')

    novo_status = request.POST.get('status')

    if novo_status == solicitacao.status:
        messages.info(request, 'O status selecionado já é o status atual da solicitação.')
        return redirect('solicitacoes_adm')

    status_antigo = solicitacao.status
    solicitacao.status = novo_status
    solicitacao.save()

    Notificacao.objects.create(
        cliente=solicitacao.cliente,
        titulo='Status updated',
        mensagem=f'Sua solicitação #{solicitacao.id} foi alterada para "{novo_status}".'
    )

    try:
        email_cliente = solicitacao.cliente.usuario.email
        nome_cliente = solicitacao.cliente.nome
        assunto = 'Atualização de Solicitação'

        texto = f"""
Olá, {nome_cliente}!
O status da sua solicitação #{solicitacao.id} foi atualizado.

Status anterior: {status_antigo}
Novo status: {novo_status}

Acesse o portal da FETELECOM para visualizar mais detalhes.
Atenciosamente,
Equipe FETELECOM
        """

        html = f"""
        <html>
        <body style="font-family: Arial, sans-serif;">
            <h2>Atualização da Solicitação #{solicitacao.id}</h2>
            <p>Olá, <strong>{nome_cliente}</strong>!</p>
            <p>O status da sua solicitação foi atualizado.</p>
            <table style="border-collapse: collapse; margin: 15px 0;">
                <tr>
                    <td style="padding: 8px;"><strong>Status anterior:</strong></td>
                    <td style="padding: 8px;">{status_antigo}</td>
                </tr>
                <tr>
                    <td style="padding: 8px;"><strong>Novo status:</strong></td>
                    <td style="padding: 8px;">{novo_status}</td>
                </tr>
            </table>
            <p>Para visualizar informações completas, acesse o portal da FETELECOM.</p>
            <p>Atenciosamente,<br><strong>Equipe FETELECOM</strong></p>
        </body>
        </html>
        """

        # CORREÇÃO: Alinhado para settings.DEFAULT_FROM_EMAIL
        email = EmailMultiAlternatives(
            subject=assunto,
            body=texto,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[email_cliente]
        )
        email.attach_alternative(html, "text/html")
        email.send()

        messages.success(request, f'Status alterado para "{novo_status}" e email enviado ao cliente.')
    except Exception as erro:
        messages.warning(request, f'Status atualizado, mas ocorreu um erro ao enviar o email: {erro}')

    return redirect('solicitacoes_adm')

def marcar_notificacoes_lidas(request):
    usuario_id = request.session.get('usuario_id')
    cliente = Cliente.objects.get(usuario_id=usuario_id)
    cliente.notificacoes.filter(lida=False).update(lida=True)
    return redirect('area_cliente')

def enviar_contato(request):
    if request.method == "POST":
        nome = request.POST.get("nome")
        email = request.POST.get("email")
        mensagem = request.POST.get("mensagem")

        # CORREÇÃO: Alinhado para settings.DEFAULT_FROM_EMAIL
        send_mail(
            subject=f"Contato do site - {nome}",
            message=f"Nome: {nome}\nEmail: {email}\n\nMensagem:\n{mensagem}",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=["fetelecomservices@gmail.com"],
            fail_silently=False
        )
        messages.success(request, "Mensagem enviada com sucesso!", extra_tags="contato")

    return redirect("index")