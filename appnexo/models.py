from django.db import models
from django.contrib.auth.models import User

class Categoria(models.Model):
    nombre = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre

class Producto(models.Model):
    TALLAS = [
        ('XS', 'XS'),
        ('S', 'S'),
        ('M', 'M'),
        ('L', 'L'),
        ('XL', 'XL'),
        ('XXL', 'XXL'),
    ]

    nombre = models.CharField(max_length=200)
    descripcion = models.TextField()
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    imagen = models.ImageField(upload_to='productos/')
    talla = models.CharField(max_length=3, choices=TALLAS)
    color = models.CharField(max_length=50)
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE)
    marca = models.CharField(max_length=100)
    stock = models.IntegerField(default=0)

    def __str__(self):
        return self.nombre
    
class Pedido(models.Model):
    ESTADOS = [
        ('pendiente', 'Pendiente'),
        ('en_proceso', 'En Proceso'),
        ('completado', 'Completado'),
        ('cancelado', 'Cancelado'),
    ]

    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    fecha = models.DateTimeField(auto_now_add=True)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    estado = models.CharField(max_length=20, choices=ESTADOS, default='pendiente')

    def __str__(self):
        return f'Pedido #{self.pk} - {self.usuario.email}'
    
class ListaDeseos(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('usuario', 'producto')

    def __str__(self):
        return f'{self.usuario.email} - {self.producto.nombre}'
    
class DireccionEnvio(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    calle = models.CharField(max_length=200)
    ciudad = models.CharField(max_length=100)
    pais = models.CharField(max_length=100)
    codigo_postal = models.CharField(max_length=20)
    telefono = models.CharField(max_length=20)
    predeterminada = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.nombre} {self.apellido} - {self.ciudad}'
    
    class MetodoPago(models.Model):
        TIPOS = [('tarjeta', 'Tarjeta de Crédito/Débito'),
             ('paypal', 'PayPal'),
             ('transferencia', 'Transferencia Bancaria'),]

    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    tipo = models.CharField(max_length=20, choices=[('tarjeta', 'Tarjeta de Crédito/Débito'), 
                                                    ('paypal', 'PayPal'), 
                                                    ('transferencia', 'Transferencia Bancaria')])
    nombre_titular = models.CharField(max_length=100)
    ultimos_digitos = models.CharField(max_length=4, blank=True)
    predeterminado = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.tipo} - {self.nombre_titular}'
