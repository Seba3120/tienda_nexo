from django.urls import path
from . import views

urlpatterns = [
    path('categorias/', views.lista_productos, name='categorias'),
    path('producto/<int:pk>/', views.detalle_producto, name='detalle_producto'),
]
