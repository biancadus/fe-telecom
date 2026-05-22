from django.contrib import admin
from django.urls import path

from .views import (
    cadastro,
    login_view,
    area_cliente,
    login_adm,
    codigo_adm,
    dashboard_adm,
    recuperar_senha,
    validar_codigo,
    nova_senha
)

urlpatterns = [
    path('cadastro/', cadastro, name='cadastro'),
    path('login/', login_view, name='login'),
    path('area-cliente/', area_cliente, name='area_cliente'),

    path('admin-login/', login_adm, name='login_adm'),
    path('admin-codigo/', codigo_adm, name='codigo_adm'),
    path('dashboard-admin/', dashboard_adm, name='dashboard_adm'),

    path('recuperar-senha/', recuperar_senha, name='recuperar_senha'),

    path('validar-codigo/', validar_codigo, name='validar_codigo'),

    path('nova-senha/', nova_senha, name='nova_senha'),
]