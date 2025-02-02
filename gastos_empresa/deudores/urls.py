# urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('', views.inicio, name='inicio'),
    path('registrar_gasto/', views.registrar_gasto, name='registrar_gasto'),
    path('registrar_pago/', views.registrar_pago, name='registrar_pago'),
    path('registrar_deuda/', views.registrar_deuda, name='registrar_deuda'),
    path('editar_deuda/<int:deuda_id>/', views.editar_deuda, name='editar_deuda'),
    path('consulta/', views.consulta, name='consulta'),
]