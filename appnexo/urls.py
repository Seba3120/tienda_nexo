from django.urls import path
from . import views

urlpatterns = [
    path("", views.inicio, name="inicio"),
    path("categorias/", views.lista_productos, name="categorias"),
    path("promociones/", views.promociones, name="promociones"),
    path("producto/<int:pk>/", views.detalle_producto, name="detalle_producto"),
    path("carrito/", views.ver_carrito, name="ver_carrito"),
    path("carrito/agregar/<int:pk>/", views.agregar_carrito, name="agregar_carrito"),
    path("carrito/eliminar/<int:pk>/", views.eliminar_carrito, name="eliminar_carrito"),
    path("login/", views.iniciar_sesion, name="login"),
    path("registro/", views.registrarse, name="registro"),
    path("logout/", views.cerrar_sesion, name="logout"),
    path("perfil/", views.perfil, name="perfil"),
    path("contacto/", views.contacto, name="contacto"),
    path("pago/", views.pago, name="pago"),
    path("confirmacion/", views.confirmacion, name="confirmacion"),
    path("panel/", views.panel, name="panel"),
    path("deseos/", views.lista_deseos, name="lista_deseos"),
    path("deseos/agregar/<int:pk>/", views.agregar_deseos, name="agregar_deseos"),
    path("deseos/eliminar/<int:pk>/", views.eliminar_deseos, name="eliminar_deseos"),
    path('mis-pedidos/', views.mis_pedidos, name='mis_pedidos'),
    path('cambiar-contrasena/', views.cambiar_contrasena, name='cambiar_contrasena'),
]
