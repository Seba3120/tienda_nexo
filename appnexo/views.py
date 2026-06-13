from django.shortcuts import render
from .models import Producto, Categoria
from django.shortcuts import render, get_object_or_404

def lista_productos(request):
    productos = Producto.objects.all()
    categorias = Categoria.objects.all()
    return render(request, 'appnexo/categorias.html', {
        'productos': productos,
        'categorias': categorias,
    })

def detalle_producto(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    productos_relacionados = Producto.objects.exclude(pk=pk)[:4]
    return render(request, 'appnexo/detalle.html', {
        'producto': producto,
        'productos_relacionados': productos_relacionados,
    })