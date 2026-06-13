from django.shortcuts import render
from .models import Producto, Categoria
from django.shortcuts import render, get_object_or_404
from django.shortcuts import render, get_object_or_404, redirect

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

def ver_carrito(request):
    carrito = request.session.get('carrito', {})
    productos_carrito = []
    total = 0

    for producto_id, cantidad in carrito.items():
        producto = get_object_or_404(Producto, pk=producto_id)
        subtotal = producto.precio * cantidad
        total += subtotal
        productos_carrito.append({
            'producto': producto,
            'cantidad': cantidad,
            'subtotal': subtotal,
        })

    return render(request, 'appnexo/carrito.html', {
        'productos_carrito': productos_carrito,
        'total': total,
    })

def agregar_carrito(request, pk):
    carrito = request.session.get('carrito', {})
    carrito[str(pk)] = carrito.get(str(pk), 0) + 1
    request.session['carrito'] = carrito
    return redirect('ver_carrito')

def eliminar_carrito(request, pk):
    carrito = request.session.get('carrito', {})
    if str(pk) in carrito:
        del carrito[str(pk)]
        request.session['carrito'] = carrito
    return redirect('ver_carrito')