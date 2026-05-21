from django.contrib import admin
from django.urls import path
from .views import cadastro, login_view

urlpatterns = [
    path('cadastro/', cadastro, name='cadastro'),
    path('login/', login_view, name='login'),
]