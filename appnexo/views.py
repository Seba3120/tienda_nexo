from django.shortcuts import render
from .models import Producto, Categoria
from django.shortcuts import render, get_object_or_404
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages

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

def iniciar_sesion(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        usuario = authenticate(request, username=username, password=password)
        if usuario is not None:
            login(request, usuario)
            return redirect('categorias')
        else:
            messages.error(request, 'Usuario o contraseña incorrectos')
    return render(request, 'appnexo/login.html')

def registrarse(request):
    if request.method == 'POST':
        nombre = request.POST['nombre']
        email = request.POST['email']
        password = request.POST['password']
        if User.objects.filter(username=email).exists():
            messages.error(request, 'Ya existe una cuenta con ese correo')
        else:
            usuario = User.objects.create_user(username=email, email=email, password=password, first_name=nombre)
            login(request, usuario)
            return redirect('categorias')
    return render(request, 'appnexo/login.html')

def cerrar_sesion(request):
    logout(request)
    return redirect('categorias')