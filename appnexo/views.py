from django.shortcuts import render
from .models import Producto, Categoria

def lista_productos(request):
    productos = Producto.objects.all()
    categorias = Categoria.objects.all()
    return render(request, 'appnexo/categorias.html', {
        'productos': productos,
        'categorias': categorias,
    })