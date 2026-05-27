from django.contrib import admin
from django.urls import path, include
from . import views

from .views import (
    cadastro,
    login_view,
    area_cliente,
    login_adm,
    codigo_adm,
    dashboard_adm,
    recuperar_senha,
    validar_codigo,
    nova_senha,
    criar_solicitacao,
    index,
    clientes_adm,
    excluir_cliente,
    solicitacoes_adm
)

urlpatterns = [
    path('', views.index, name='index'),
    path('cadastro/', cadastro, name='cadastro'),
    path('login/', login_view, name='login'),

    path('loginAdm/', login_adm, name='login_adm'),
    path('codAdm/', codigo_adm, name='codigo_adm'),
    path('adminPage/', dashboard_adm, name='dashboard_adm'),

    path('recuperarSenha/', recuperar_senha, name='recuperar_senha'),

    path('validarCodigo/', validar_codigo, name='validar_codigo'),

    path('novaSenha/', nova_senha, name='nova_senha'),

    path(
    'criar-solicitacao/',
    views.criar_solicitacao,
    name='criar_solicitacao'
    ),

    path(
        'areaDoCliente/',
        views.area_cliente,
        name='area_cliente'
    ),

    path(
    'editar-solicitacao/<int:id>/',
    views.editar_solicitacao,
    name='editar_solicitacao'
    ),

    path(
    'adminPage2/',
    views.clientes_adm,
    name='clientes_adm'
    ),

    path(
    'excluir-cliente/<int:id>/',
    views.excluir_cliente,
    name='excluir_cliente'
    ),

    path(
    'adminPage3/',
    views.solicitacoes_adm,
    name='solicitacoes_adm'
    ),

    path(
    'editar-solicitacao-adm/<int:id>/',
    views.editar_solicitacao_adm,
    name='editar_solicitacao_adm'
    ),

    path(
        'excluir-solicitacao/<int:id>/',
        views.excluir_solicitacao,
        name='excluir_solicitacao'
    ),

    path(
        'alterar-status/<int:id>/',
        views.alterar_status,
        name='alterar_status'
    ),
]