from django.shortcuts import render
from .models import Producto, Categoria, Pedido, ListaDeseos, DireccionEnvio, MetodoPago, DetallePedido
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
    busqueda = request.GET.get("busqueda")

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
            "busqueda": busqueda,
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
        for producto_id, cantidad in carrito.items():
            producto = get_object_or_404(Producto, pk=producto_id)
            DetallePedido.objects.create(
                pedido=pedido,
                producto=producto,
                cantidad=cantidad,
                precio=producto.precio
            )
            producto.stock -= cantidad
            producto.save()
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
    ultimo_pedido = (
        Pedido.objects.filter(usuario=request.user).order_by("-fecha").first()
    )
    productos = Producto.objects.all()[:4]
    return render(
        request,
        "appnexo/confirmacion.html",
        {
            "productos": productos,
            "pedido": ultimo_pedido,
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
    return render(
        request,
        "appnexo/lista_deseos.html",
        {
            "deseos": deseos,
        },
    )

@login_required
def agregar_deseos(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    ListaDeseos.objects.get_or_create(usuario=request.user, producto=producto)
    return redirect("lista_deseos")

@login_required
def eliminar_deseos(request, pk):
    deseo = get_object_or_404(ListaDeseos, pk=pk, usuario=request.user)
    deseo.delete()
    return redirect("lista_deseos")

@login_required
def mis_pedidos(request):
    pedidos = Pedido.objects.filter(usuario=request.user).order_by("-fecha")
    return render(
        request,
        "appnexo/mis_pedidos.html",
        {
            "pedidos": pedidos,
        },
    )

@login_required
def cambiar_contrasena(request):
    if request.method == "POST":
        contrasena_actual = request.POST["contrasena_actual"]
        contrasena_nueva = request.POST["contrasena_nueva"]
        contrasena_confirmar = request.POST["contrasena_confirmar"]

        if not request.user.check_password(contrasena_actual):
            messages.error(request, "La contraseña actual es incorrecta")
        elif contrasena_nueva != contrasena_confirmar:
            messages.error(request, "Las contraseñas nuevas no coinciden")
        else:
            request.user.set_password(contrasena_nueva)
            request.user.save()
            messages.success(
                request, "Contraseña cambiada correctamente, inicia sesión nuevamente"
            )
            return redirect("login")

    return render(request, "appnexo/cambiar_contrasena.html")

@login_required
def direcciones_envio(request):
    direcciones = DireccionEnvio.objects.filter(usuario=request.user)
    return render(
        request,
        "appnexo/direcciones_envio.html",
        {
            "direcciones": direcciones,
        },
    )

@login_required
def agregar_direccion(request):
    if request.method == "POST":
        DireccionEnvio.objects.create(
            usuario=request.user,
            nombre=request.POST["nombre"],
            apellido=request.POST["apellido"],
            calle=request.POST["calle"],
            ciudad=request.POST["ciudad"],
            pais=request.POST["pais"],
            codigo_postal=request.POST["codigo_postal"],
            telefono=request.POST["telefono"],
        )
        messages.success(request, "Dirección agregada correctamente")
        return redirect("direcciones_envio")
    return render(request, "appnexo/agregar_direccion.html")


@login_required
def eliminar_direccion(request, pk):
    direccion = get_object_or_404(DireccionEnvio, pk=pk, usuario=request.user)
    direccion.delete()
    return redirect("direcciones_envio")


@login_required
def metodos_pago(request):
    metodos = MetodoPago.objects.filter(usuario=request.user)
    return render(
        request,
        "appnexo/metodos_pago.html",
        {
            "metodos": metodos,
        },
    )

@login_required
def agregar_metodo_pago(request):
    if request.method == "POST":
        MetodoPago.objects.create(
            usuario=request.user,
            tipo=request.POST["tipo"],
            nombre_titular=request.POST["nombre_titular"],
            ultimos_digitos=request.POST.get("ultimos_digitos", ""),
        )
        messages.success(request, "Método de pago agregado correctamente")
        return redirect("metodos_pago")
    return render(request, "appnexo/agregar_metodo_pago.html")


@login_required
def eliminar_metodo_pago(request, pk):
    metodo = get_object_or_404(MetodoPago, pk=pk, usuario=request.user)
    metodo.delete()
    return redirect("metodos_pago")

@staff_member_required
def panel_productos(request):
    productos = Producto.objects.all()
    return render(request, 'appnexo/panel/panel_productos.html', {
        'productos': productos,
    })

@staff_member_required
def panel_crear_producto(request):
    categorias = Categoria.objects.all()
    if request.method == 'POST':
        Producto.objects.create(
            nombre=request.POST['nombre'],
            descripcion=request.POST['descripcion'],
            precio=request.POST['precio'],
            imagen=request.FILES.get('imagen'),
            talla=request.POST['talla'],
            color=request.POST['color'],
            categoria=Categoria.objects.get(pk=request.POST['categoria']),
            marca=request.POST['marca'],
            stock=request.POST['stock'],
        )
        messages.success(request, 'Producto creado correctamente')
        return redirect('panel_productos')
    return render(request, 'appnexo/panel/panel_crear_producto.html', {
        'categorias': categorias,
    })

@staff_member_required
def panel_editar_producto(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    categorias = Categoria.objects.all()
    if request.method == 'POST':
        producto.nombre = request.POST['nombre']
        producto.descripcion = request.POST['descripcion']
        producto.precio = request.POST['precio']
        producto.talla = request.POST['talla']
        producto.color = request.POST['color']
        producto.categoria = Categoria.objects.get(pk=request.POST['categoria'])
        producto.marca = request.POST['marca']
        producto.stock = request.POST['stock']
        if request.FILES.get('imagen'):
            producto.imagen = request.FILES['imagen']
        producto.save()
        messages.success(request, 'Producto actualizado correctamente')
        return redirect('panel_productos')
    return render(request, 'appnexo/panel/panel_editar_producto.html', {
        'producto': producto,
        'categorias': categorias,
    })

@staff_member_required
def panel_eliminar_producto(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    producto.delete()
    messages.success(request, 'Producto eliminado correctamente')
    return redirect('panel_productos')

@staff_member_required
def panel_pedidos(request):
    pedidos = Pedido.objects.all().order_by('-fecha')
    return render(request, 'appnexo/panel/panel_pedidos.html', {
        'pedidos': pedidos,
    })

@staff_member_required
def panel_cambiar_estado_pedido(request, pk):
    pedido = get_object_or_404(Pedido, pk=pk)
    if request.method == 'POST':
        pedido.estado = request.POST['estado']
        pedido.save()
        messages.success(request, 'Estado del pedido actualizado correctamente')
    return redirect('panel_pedidos')

@staff_member_required
def panel_clientes(request):
    clientes = User.objects.filter(is_staff=False)
    return render(request, 'appnexo/panel/panel_clientes.html', {
        'clientes': clientes,
    })

@staff_member_required
def panel_categorias(request):
    categorias = Categoria.objects.all()
    if request.method == 'POST':
        Categoria.objects.create(nombre=request.POST['nombre'])
        messages.success(request, 'Categoría creada correctamente')
        return redirect('panel_categorias')
    return render(request, 'appnexo/panel/panel_categorias.html', {
        'categorias': categorias,
    })

@staff_member_required
def panel_eliminar_categoria(request, pk):
    categoria = get_object_or_404(Categoria, pk=pk)
    categoria.delete()
    messages.success(request, 'Categoría eliminada correctamente')
    return redirect('panel_categorias')