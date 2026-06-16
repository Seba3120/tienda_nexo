from django.shortcuts import render
from .models import Producto, Categoria, Pedido, ListaDeseos
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

    # Filtros
    categoria_id = request.GET.get("categoria")
    talla = request.GET.get("talla")
    orden = request.GET.get("orden")
    color = request.GET.get("color")
    marca = request.GET.get("marca")
    precio_min = request.GET.get("precio_min")
    precio_max = request.GET.get("precio_max")
    busqueda = request.GET.get('busqueda')

    if categoria_id:
        productos = productos.filter(categoria__id=categoria_id)
    if talla:
        productos = productos.filter(talla=talla)
    if orden == "precio_asc":
        productos = productos.order_by("precio")
    elif orden == "precio_desc":
        productos = productos.order_by("-precio")
    elif orden == "nombre":
        productos = productos.order_by("nombre")
    if color:
        productos = productos.filter(color__icontains=color)
    if marca:
        productos = productos.filter(marca__icontains=marca)
    if precio_min:
        productos = productos.filter(precio__gte=precio_min)
    if precio_max:
        productos = productos.filter(precio__lte=precio_max)
    if busqueda:
        productos = productos.filter(nombre__icontains=busqueda)

    # Obtener valores unicos para los filtros
    colores = Producto.objects.values_list("color", flat=True).distinct()
    marcas = Producto.objects.values_list("marca", flat=True).distinct()
    tallas = ["XS", "S", "M", "L", "XL", "XXL"]

    return render(
        request,
        "appnexo/categorias.html",
        {
            "productos": productos,
            "categorias": categorias,
            "colores": colores,
            "marcas": marcas,
            "tallas": tallas,
            'busqueda': busqueda,
        },
    )


def detalle_producto(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    productos_relacionados = Producto.objects.exclude(pk=pk)[:4]
    return render(
        request,
        "appnexo/detalle.html",
        {
            "producto": producto,
            "productos_relacionados": productos_relacionados,
        },
    )


def ver_carrito(request):
    carrito = request.session.get("carrito", {})
    productos_carrito = []
    total = 0

    for producto_id, cantidad in carrito.items():
        producto = get_object_or_404(Producto, pk=producto_id)
        subtotal = producto.precio * cantidad
        total += subtotal
        productos_carrito.append(
            {
                "producto": producto,
                "cantidad": cantidad,
                "subtotal": subtotal,
            }
        )

    return render(
        request,
        "appnexo/carrito.html",
        {
            "productos_carrito": productos_carrito,
            "total": total,
        },
    )


def agregar_carrito(request, pk):
    carrito = request.session.get("carrito", {})
    carrito[str(pk)] = carrito.get(str(pk), 0) + 1
    request.session["carrito"] = carrito
    return redirect("ver_carrito")


def eliminar_carrito(request, pk):
    carrito = request.session.get("carrito", {})
    if str(pk) in carrito:
        del carrito[str(pk)]
        request.session["carrito"] = carrito
    return redirect("ver_carrito")


def iniciar_sesion(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        usuario = authenticate(request, username=username, password=password)
        if usuario is not None:
            login(request, usuario)
            return redirect("categorias")
        else:
            messages.error(request, "Usuario o contraseña incorrectos")
    return render(request, "appnexo/login.html")


def registrarse(request):
    if request.method == "POST":
        nombre = request.POST["nombre"]
        email = request.POST["email"]
        password = request.POST["password"]
        if User.objects.filter(username=email).exists():
            messages.error(request, "Ya existe una cuenta con ese correo")
        else:
            usuario = User.objects.create_user(
                username=email, email=email, password=password, first_name=nombre
            )
            login(request, usuario)
            return redirect("categorias")
    return render(request, "appnexo/login.html")


def cerrar_sesion(request):
    logout(request)
    return redirect("categorias")


@login_required
def perfil(request):
    if request.method == "POST":
        nombre = request.POST["nombre"]
        email = request.POST["email"]
        telefono = request.POST.get("telefono", "")
        request.user.first_name = nombre
        request.user.email = email
        request.user.save()
        messages.success(request, "Perfil actualizado correctamente")
        return redirect("perfil")
    return render(request, "appnexo/perfil.html")


def contacto(request):
    if request.method == "POST":
        nombre = request.POST["nombre"]
        apellido = request.POST["apellido"]
        email = request.POST["email"]
        mensaje = request.POST["mensaje"]
        messages.success(
            request, "Mensaje enviado correctamente, te contactaremos pronto."
        )
        return redirect("contacto")
    return render(request, "appnexo/contacto.html")


@login_required
def pago(request):
    carrito = request.session.get("carrito", {})
    productos_carrito = []
    total = 0

    for producto_id, cantidad in carrito.items():
        producto = get_object_or_404(Producto, pk=producto_id)
        subtotal = producto.precio * cantidad
        total += subtotal
        productos_carrito.append(
            {
                "producto": producto,
                "cantidad": cantidad,
                "subtotal": subtotal,
            }
        )

    if request.method == "POST":
        pedido = Pedido.objects.create(
            usuario=request.user,
            total=total,
            estado='pendiente'
        )
        request.session['carrito'] = {}
        return redirect('confirmacion')

    return render(
        request,
        "appnexo/pago.html",
        {
            "productos_carrito": productos_carrito,
            "total": total,
        },
    )


def confirmacion(request):
    productos = Producto.objects.all()[:4]
    return render(
        request,
        "appnexo/confirmacion.html",
        {
            "productos": productos,
        },
    )


@staff_member_required
def panel(request):
    total_ventas = sum(p.total for p in Pedido.objects.filter(estado="completado"))
    pedidos_pendientes = Pedido.objects.filter(estado="pendiente").count()
    nuevos_clientes = User.objects.count()
    productos_sin_stock = Producto.objects.filter(stock=0).count()
    ultimos_pedidos = Pedido.objects.all().order_by("-fecha")[:5]
    productos = Producto.objects.all()[:5]

    return render(
        request,
        "appnexo/panel.html",
        {
            "total_ventas": total_ventas,
            "pedidos_pendientes": pedidos_pendientes,
            "nuevos_clientes": nuevos_clientes,
            "productos_sin_stock": productos_sin_stock,
            "ultimos_pedidos": ultimos_pedidos,
            "productos": productos,
        },
    )


def inicio(request):
    productos_destacados = Producto.objects.all()[:8]
    categorias = Categoria.objects.all()
    return render(
        request,
        "appnexo/inicio.html",
        {
            "productos_destacados": productos_destacados,
            "categorias": categorias,
        },
    )


def promociones(request):
    productos = Producto.objects.all()
    return render(
        request,
        "appnexo/promociones.html",
        {
            "productos": productos,
        },
    )

@login_required
def lista_deseos(request):
    deseos = ListaDeseos.objects.filter(usuario=request.user)
    return render(request, 'appnexo/lista_deseos.html', {
        'deseos': deseos,
    })

@login_required
def agregar_deseos(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    ListaDeseos.objects.get_or_create(usuario=request.user, producto=producto)
    return redirect('lista_deseos')

@login_required
def eliminar_deseos(request, pk):
    deseo = get_object_or_404(ListaDeseos, pk=pk, usuario=request.user)
    deseo.delete()
    return redirect('lista_deseos')

@login_required
def mis_pedidos(request):
    pedidos = Pedido.objects.filter(usuario=request.user).order_by('-fecha')
    return render(request, 'appnexo/mis_pedidos.html', {
        'pedidos': pedidos,
    })