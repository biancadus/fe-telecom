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
    index
)

urlpatterns = [
    path('', views.index, name='index'),
    path('cadastro/', cadastro, name='cadastro'),
    path('login/', login_view, name='login'),

    path('admin-login/', login_adm, name='login_adm'),
    path('admin-codigo/', codigo_adm, name='codigo_adm'),
    path('dashboard-admin/', dashboard_adm, name='dashboard_adm'),

    path('recuperar-senha/', recuperar_senha, name='recuperar_senha'),

    path('validar-codigo/', validar_codigo, name='validar_codigo'),

    path('nova-senha/', nova_senha, name='nova_senha'),

    path(
    'criar-solicitacao/',
    views.criar_solicitacao,
    name='criar_solicitacao'
    ),

     path(
        'area-cliente/',
        views.area_cliente,
        name='area_cliente'
    ),
]