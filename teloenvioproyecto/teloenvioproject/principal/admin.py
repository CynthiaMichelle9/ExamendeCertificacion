from django.contrib import admin
from .models import Cliente, Producto, Cart, Pedido, Detalle, ProductoCart
# Register your models here.
admin.site.register(Cliente)
admin.site.register(Producto)
admin.site.register(Cart)
admin.site.register(ProductoCart)
admin.site.register(Pedido)
admin.site.register(Detalle)