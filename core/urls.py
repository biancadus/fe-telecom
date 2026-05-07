from django.contrib import admin
from django.urls import path
from core.views import home, cadastro  # Importe todas as suas views aqui

urlpatterns = [
    path('admin/', admin.site.urls),    # O correto para o admin é admin.site.urls
    path('', home, name='home'),       # Página inicial
    path('cadastro/', cadastro, name='cadastro'), # Sua página de cadastro
]