from django.shortcuts import render
from .models import Producto, Categoria, Pedido
from django.shortcuts import render, get_object_or_404
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required


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

@login_required
def perfil(request):
    if request.method == 'POST':
        nombre = request.POST['nombre']
        email = request.POST['email']
        telefono = request.POST.get('telefono', '')
        request.user.first_name = nombre
        request.user.email = email
        request.user.save()
        messages.success(request, 'Perfil actualizado correctamente')
        return redirect('perfil')
    return render(request, 'appnexo/perfil.html')

def contacto(request):
    if request.method == 'POST':
        nombre = request.POST['nombre']
        apellido = request.POST['apellido']
        email = request.POST['email']
        mensaje = request.POST['mensaje']
        messages.success(request, 'Mensaje enviado correctamente, te contactaremos pronto.')
        return redirect('contacto')
    return render(request, 'appnexo/contacto.html')

@login_required
def pago(request):
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

    if request.method == 'POST':
        request.session['carrito'] = {}
        return redirect('confirmacion')

    return render(request, 'appnexo/pago.html', {
        'productos_carrito': productos_carrito,
        'total': total,
    })

def confirmacion(request):
    productos = Producto.objects.all()[:4]
    return render(request, 'appnexo/confirmacion.html', {
        'productos': productos,
    })

@staff_member_required
def panel(request):
    total_ventas = sum(p.total for p in Pedido.objects.filter(estado='completado'))
    pedidos_pendientes = Pedido.objects.filter(estado='pendiente').count()
    nuevos_clientes = User.objects.count()
    productos_sin_stock = Producto.objects.filter(stock=0).count()
    ultimos_pedidos = Pedido.objects.all().order_by('-fecha')[:5]
    productos = Producto.objects.all()[:5]

    return render(request, 'appnexo/panel.html', {
        'total_ventas': total_ventas,
        'pedidos_pendientes': pedidos_pendientes,
        'nuevos_clientes': nuevos_clientes,
        'productos_sin_stock': productos_sin_stock,
        'ultimos_pedidos': ultimos_pedidos,
        'productos': productos,
    })

def inicio(request):
    productos_destacados = Producto.objects.all()[:8]
    categorias = Categoria.objects.all()
    return render(request, 'appnexo/inicio.html', {
        'productos_destacados': productos_destacados,
        'categorias': categorias,
    })