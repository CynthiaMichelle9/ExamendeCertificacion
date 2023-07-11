from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.utils.timezone import now

User = get_user_model()

# Create your models here
class Producto(models.Model):
    nombre = models.CharField(max_length=100, null=False)
    descripcion = models.CharField(max_length=500, blank=True)
    precio = models.IntegerField(null=False)
    imagen = models.ImageField(
        upload_to='media/images', default='producto_default.png')
    stock = models.PositiveIntegerField(null=False)

    def __str__(self):
        return self.nombre
    
class Cliente(models.Model):
    idusuario = models.ForeignKey(
        User, on_delete=models.CASCADE, null=True, blank=True)
    nombre = models.CharField(max_length=50, null=False)
    apellido = models.CharField(max_length=50, null=False)
    rut = models.CharField(max_length=12, null=False)
    direccion = models.CharField(max_length=100, null=False)
    comuna = models.CharField(max_length=50, null=False)
    email = models.EmailField(max_length=50, null=False)
    telefono = models.CharField(max_length=50, null=False, blank=True)

    def __str__(self):
        return self.nombre
    

class Cart(models.Model):
    idcliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, default=None)
    nombre_cart = models.CharField(max_length=45)
    fecha = models.DateField(default=timezone.now)
    productos = models.ManyToManyField(Producto, through='ProductoCart')

    def __str__(self):
        return str(self.nombre_cart)

    def total_productos(self):
        cantidad = 0
        producto_cart = Producto.objects.filter(idcart=self)
        for producto in producto_cart:
            cantidad += producto.cantidad_deseada
        return cantidad

    def valor_total(self):
        total = 0
        producto_cart = Producto.objects.filter(idcart=self)
        for producto_cart in producto_cart:
            valor = producto_cart.cantidad_deseada * \
                producto_cart.idproducto.precio
            total += valor
        return total

class ProductoCart(models.Model):
    idcart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    idproducto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad_deseada = models.PositiveIntegerField(blank=False)

    def __str__(self):
        return f"cart: {self.idcart} - {self.idcart.idcliente.nombre}"

    def valor_total(self):
        return self.cantidad_deseada * self.idproducto.valor_unit

class Productor(models.Model):
    nombre = models.CharField(max_length=50, null=False)
    email = models.EmailField(max_length=50, null=False)
    telefono = models.CharField(max_length=50, null=False, blank=True)
    rut = models.CharField(max_length=12, null=False)
    razonsocial = models.CharField(max_length=50, null=False)
    direccion = models.CharField(max_length=100, null=False)
    comuna = models.CharField(max_length=50, null=False)
    rubro = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.nombre

class DireccionDespacho(models.Model):
    comuna = models.CharField(max_length=100)
    calle = models.CharField(max_length=100)
    numero = models.IntegerField()
    region = models.CharField(max_length=80)
    
    def __str__(self):
        return self.comuna

class Pedido(models.Model):
    METODOPAGO_CHOICES = [
        ('Transferencia', 'Transferencia'),
        ('Webpay', 'Webpay'),
        ('Tarjeta teloenvio', 'Tarjeta teloenvio')
    ]
    ESTADO_CHOICES = [
        ('Pendiente', 'Pendiente'),
        ('En preparacion', 'En preparación'),
        ('Entregado', 'Entregado'),
        ('En Despacho', 'En Despacho'),
        ('Cancelado', 'Cancelado'),
    ]

    carro = models.ForeignKey(
       Cart, null=True, blank=True, on_delete=models.SET_NULL)
    fecha = models.DateField(auto_now_add=True)
    direccion_despacho = models.ForeignKey(DireccionDespacho, on_delete=models.PROTECT)
    fecha_despacho = models.DateTimeField(null=False)
    subtotal = models.PositiveIntegerField(null=False)
    valordespacho = models.PositiveIntegerField(null=False)
    valortotal = models.PositiveIntegerField(null=False)
    metododepago = models.CharField(
        null=False, max_length=50, choices=METODOPAGO_CHOICES)
    estadopedido = models.CharField(
        null=False, max_length=50, choices=ESTADO_CHOICES)

    def __str__(self):
        return str(self.id)


class Detalle(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.PROTECT)
    productos = models.ForeignKey(Producto, on_delete=models.PROTECT)
    cantidad = models.PositiveIntegerField(null=False)
    precio = models.PositiveIntegerField(null=False)

    def cantidad_valor(self):
        return self.cantidad * self.precio

    def __str__(self):
        return f"Detalle - Pedido: {self.pedido}, Producto: {self.productos}"

