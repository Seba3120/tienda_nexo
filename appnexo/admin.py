from django.contrib import admin
from .models import Categoria, Producto, Pedido, ListaDeseos, DireccionEnvio, MetodoPago

admin.site.register(Categoria)
admin.site.register(Producto)
admin.site.register(Pedido)
admin.site.register(ListaDeseos)
admin.site.register(DireccionEnvio)
admin.site.register(MetodoPago)