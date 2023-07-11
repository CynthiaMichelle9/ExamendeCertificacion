from django.shortcuts import get_object_or_404, redirect, render
from datetime import datetime
from django.urls import reverse_lazy
from django.views.generic import TemplateView
from .models import Producto, Pedido, Cart, Detalle, Cliente, ProductoCart
from .forms import ProductoForm, ClienteExternoForm, ClienteForm, CartForm, PedidoUsuarioForm, PedidoForm, ProductoCartForm, AgregarProductoForm, EstadoPedidoForm
from django.contrib.auth import get_user_model
from django.utils.decorators import method_decorator
from django.contrib.admin.views.decorators import staff_member_required
from django.views.generic.list import ListView
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
import contextlib
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View

User = get_user_model()

class IndexView(TemplateView):
    template_name="index.html"

    def get(self, request, *args, **kwargs):
       result = []
       if not result:
          pass
       context = {}
       return render(request, self.template_name, context=context)
    

class PedidosView(View, LoginRequiredMixin):
    template_name = "pedidos.html"

    def dispatch(self, request, *args, **kwargs):
        self.usuario = User.objects.get(id=request.user.id)
        if request.user.is_staff:
            return super().dispatch(request, *args, **kwargs)
        else:
            try:
                self.cliente = Cliente.objects.get(idusuario=self.usuario)
            except Cliente.DoesNotExist:
                alert = "Ingrese sus datos para continuar con la compra"
                messages.error(request, alert)
                return redirect("panel_usuario")
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        # Si el usuario es staff, puede ver todos los pedidos
        # en caso contrario, solo renderizara los pedidos del usuario
        if request.user.is_staff:
            pedidos = Pedido.objects.all()
        else:
            pedidos = Pedido.objects.filter(cart__idcliente=self.cliente)
        context = {'pedidos': pedidos}
        return render(request, self.template_name, context=context)

@login_required
def eliminar_pedido(request, pk):
   pedido = get_object_or_404(Pedido, pk=pk)
   if request.method == 'POST':
      if pedido.estadopedido == 'Pendiente' or pedido.estadopedido == 'En preparacion':
         pedido.estadopedido = 'Cancelado'
         send_mail(
                   'Pedido Cancelado',
                   'Su pedido ha sido cancelado',
                   settings.EMAIL_HOST_USER,
                   [pedido.cart.idcliente.email],
                   fail_silently=False,
               )
         pedido.save()
      else:
            messages.error(request, 'No se puede cancelar una vez que el pedido ha sido enviado o entregado')
      return redirect('pedidos')

@method_decorator(staff_member_required, name='dispatch')
# Ingresar productos como staff
class GestionProdView(View, LoginRequiredMixin):
    template_name = "gestion_prod.html"

    def get(self, request, *args, **kwargs):
        productos = Producto.objects.all()
        context = {'productos': productos}
        return render(request, self.template_name, context=context)

@method_decorator(staff_member_required, name='dispatch')
class IngresoProductoView(View, LoginRequiredMixin):
    template_name = "nuevo_producto.html"

    def get(self, request):
        form = ProductoForm
        context = {'form': form}
        return render(request, self.template_name, context)

    def post(self, request):
        form = ProductoForm(request.POST)
        if form.is_valid():
            producto = form.save(commit=False)
            producto.save()
            return redirect('gestionprod')

@method_decorator(staff_member_required, name='dispatch')
class CrearClienteView(View, LoginRequiredMixin):
    template_name = 'crear_cliente.html'

    def get(self, request):
        form = ClienteExternoForm()
        cart_form = CartForm()
        clientes = Cliente.objects.all()
        context = {'form': form,
                   'cart_form': cart_form,
                   'clientes': clientes}
        return render(request, self.template_name, context)

    def post(self, request):
         form = ClienteExternoForm(request.POST)
         cart_form = CartForm(request.POST)
        
         if request.POST.get('cliente_existente'):
            cliente = Cliente.objects.get(
                id=request.POST.get('cliente_existente'))
         elif form.is_valid() and cart_form.is_valid():
             cliente = form.save()
         cart =cart_form.save(commit=False)
         cart.idcliente = cliente
         cart.save()
         return redirect('agregar_productos_carro', cart_id=cart.id)


# Agrega productos al carrito recien creada como staff
class AgregarProductosCartView(View, LoginRequiredMixin):
    template_name = 'agregar_productos_carro.html'

    def calculate_subtotal(self, productos_cart):
        return sum(
            producto_cart.idproducto.precio
            * producto_cart.cantidad_deseada
            for producto_cart in productos_cart
        )

    def get(self, request, cart_id):
        cart = Cart.objects.get(id=cart_id)
        productos_cart = ProductoCart.objects.filter(
            idcart=cart)
        subtotal = self.calculate_subtotal(productos_cart)
        form = ProductoCartForm()
        context = {
            'form': form,
            'cart': cart,
            'productos_cart': productos_cart,
            'subtotal': subtotal
        }
        return render(request, self.template_name, context)

    def post(self, request, cart_id):
        cart = cart.objects.get(id=cart_id)
        form = ProductoCartForm(request.POST)
        if request.POST.get('delete'):
            product_id = request.POST.get('delete')
            ProductoCart.objects.filter(id=product_id).delete()
            return redirect('agregar_productos_cart', cart_id=cart.id)
        elif request.POST.get('regresar'):
            return redirect('crear_cliente')
        elif request.POST.get('continuar'):
            return redirect('crear_pedido', cart_id=cart_id, cliente_id=cart.idcliente.id)
        elif request.POST.get('guardar_cart'):
            return redirect('cart_detalle', cart_id)

        if form.is_valid():
            producto_cart = form.save(commit=False)
            cart = cart.objects.get(id=cart_id)
            producto = producto_cart.idproducto
            existing_product_cart = ProductoCart.objects.filter(
                idcart=cart,
                idproducto=producto
            ).first()

            if existing_product_cart:
                existing_product_cart.cantidad_deseada += producto_cart.cantidad_deseada
                existing_product_cart.save()
            else:
                producto_cart.idcart = cart
                producto_cart.save()
            return redirect('agregar_productos_cart', cart_id=cart_id)

        cart = cart.objects.get(id=cart_id)
        productos_cart = ProductoCart.objects.filter(
            idcart=cart)
        subtotal = self.calculate_subtotal(productos_cart)
        context = {
            'form': form,
            'cart': cart,
            'productos_cart': productos_cart,
            'subtotal': subtotal
        }
        return render(request, self.template_name, context)


# Crear pedido como staff
class CrearPedidoView(View, LoginRequiredMixin):
    template_name = "crear_pedido.html"
    form_class = PedidoForm
    reverse_lazy = "pedidos"

    def get(self, request, cart_id, cliente_id):
        # get subtotal from agregar_productos_cart
        cart = cart.objects.get(id=cart_id)
        cliente = Cliente.objects.get(id=cliente_id)
        productos_cart = ProductoCart.objects.filter(
            idcart=cart)
        subtotal = self.calculate_subtotal(productos_cart)
        valordespacho = 0
        if subtotal < 50000:
            valordespacho = 5990
        else:
            valordespacho = 10990
        valortotal = valordespacho + subtotal
        form = self.form_class(
            initial={'cart': cart,
                     'subtotal': subtotal,
                     'valordespacho': valordespacho,
                     'valortotal': valortotal})
        context = {
            'form': form,
            'cart': cart,
            'subtotal': subtotal,
            'cliente': cliente,
        }
        return render(request, self.template_name, context)

    def post(self, request, cart_id, cliente_id):
        form = self.form_class(request.POST)
        cart = cart.objects.get(id=cart_id)
        productos_cart = cart.productos.through.objects.filter(
            idcart=cart)
        if form.is_valid():
            pedido = form.save()
            pedido.cart_id = cart
            pedido.save()
            self.crear_detalle(cart, pedido)
            return redirect(self.reverse_lazy)
        else:
            print(form.errors)

        cart = Cart.objects.get(id=cart_id)
        cliente = Cliente.objects.get(id=cliente_id)
        productos_cart = ProductoCart.objects.filter(
            idcart=cart)
        subtotal = self.calculate_subtotal(productos_cart)
        context = {
            'form': form,
            'cart': cart,
            'subtotal': subtotal,
            'cliente': cliente,
        }
        return render(request, self.template_name, context)

    def calculate_subtotal(self, productos_cart):
        return sum(
            producto_cart.idproducto.precio
            * producto_cart.cantidad_deseada
            for producto_cart in productos_cart
        )

    def crear_detalle(self, cart, pedido):
        productos_cart = cart.productos.through.objects.filter(
            idcart=cart)
        lista = []
        for producto in productos_cart:
            if producto.idproducto.stock <= producto.cantidad_deseada:
                pass
            else:
                lista.append(producto)

        for producto_cart in lista:
            producto = get_object_or_404(
                Producto, pk=producto_cart.idproducto.id)
            cantidad_deseada = producto_cart.cantidad_deseada
            producto.stock -= cantidad_deseada
            producto.save()
            detalle = Detalle()
            detalle.pedido = pedido
            detalle.productos = producto
            detalle.cantidad = cantidad_deseada
            detalle.precio = producto.precio
            detalle.save()

# Crear pedido como usuario


class CrearPedidoUsuarioView(View, LoginRequiredMixin):
    template_name = "crear_pedido.html"
    form_class = PedidoUsuarioForm
    reverse_lazy = "pedido_detalle"

    def get(self, request, cart_id, cliente_id):
        # get subtotal from agregar_productos_cart
        cart = cart.objects.get(id=cart_id)
        cliente = Cliente.objects.get(id=cliente_id)
        productos_cart = ProductoCart.objects.filter(
            idcart=cart)
        subtotal = self.calculate_subtotal(productos_cart)
        if subtotal < 50000:
            valordespacho = 5990
        else:
            valordespacho = 0
        valortotal = valordespacho + subtotal
        form = self.form_class(
            initial={'cart': cart,
                     'subtotal': subtotal,
                     'valordespacho': valordespacho,
                     'valortotal': valortotal})
        context = {
            'form': form,
            'cart': cart,
            'subtotal': subtotal,
            'cliente': cliente
        }
        return render(request, self.template_name, context)

    def post(self, request, cart_id, cliente_id):
        form = self.form_class(request.POST)
        cart = cart.objects.get(id=cart_id)
        productos_cart = cart.productos.through.objects.filter(
            idcart=cart)
        if form.is_valid():
            pedido = form.save()
            pedido.cart_id = cart
            pedido.save()
            self.crear_detalle(cart, pedido)
            pedido_detalle = pedido.id
            return redirect(self.reverse_lazy, pedido_detalle)
        else:
            print(form.errors)

        cart = cart.objects.get(id=cart_id)
        cliente = Cliente.objects.get(id=cliente_id)
        productos_cart = ProductoCart.objects.filter(
            idcart=cart)
        subtotal = self.calculate_subtotal(productos_cart)

        context = {
            'form': form,
            'cart': cart,
            'subtotal': subtotal,
            'cliente': cliente
        }
        return render(request, self.template_name, context)

    def calculate_subtotal(self, productos_cart):
        return sum(
            producto_cart.idproducto.precio
            * producto_cart.cantidad_deseada
            for producto_cart in productos_cart
        )

    def crear_detalle(self, cart, pedido):
        productos_cart = cart.productos.through.objects.filter(
            idcart=cart)
        lista = []
        for producto in productos_cart:
            if producto.idproducto.stock <= producto.cantidad_deseada:
                pass
            else:
                lista.append(producto)

        for producto_cart in lista:
            producto = get_object_or_404(
                Producto, pk=producto_cart.idproducto.id)
            cantidad_deseada = producto_cart.cantidad_deseada
            print("STOCK INICIAL: ", producto.stock)
            producto.stock -= cantidad_deseada
            producto.save()
            print("STOCK GUARDADO: ", producto.stock)
            detalle = Detalle()
            detalle.pedido = pedido
            detalle.productos = producto
            detalle.cantidad = cantidad_deseada
            detalle.precio = producto.precio
            detalle.save()


class PedidosList(ListView, LoginRequiredMixin):
    model = Pedido
    context_object_name = 'pedidos'
    template_name = 'pedidos.html'

    def get_queryset(self):
        return super().get_queryset()


class ListaCartView(TemplateView, LoginRequiredMixin):
    template_name = "lista_cart.html"
    # Dispatch se ejecuta primero que cualquier metodo y settea variables desde el comienzo, en este caso el self.usuario a partir del request.user

    def dispatch(self, request, *args, **kwargs):
        self.usuario = User.objects.get(id=request.user.id)
        try:
            self.cliente = Cliente.objects.get(idusuario=self.usuario)
        except Cliente.DoesNotExist:
            alert = "Si desea acceder a la cart, primero debe registrar sus datos como cliente"
            messages.error(request, alert)
            return redirect("panel_usuario")
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        cart_form = CartForm()
        carts = Cart.objects.filter(idcliente=self.cliente)
        context = {"carts": carts,
                   "cliente": self.cliente,
                   'cart_form': cart_form, }
        return render(request, self.template_name, context)

    def post(self, request):
        cart_form = CartForm(request.POST)
        if request.POST.get('crear_cart'):
            if cart_form.is_valid():
                cart = cart_form.save(commit=False)
                cart.idcliente = self.cliente
                cart.save()
                return redirect('user_cart')
            return redirect('index')


class CartDetalleView(TemplateView, LoginRequiredMixin):
    template_name = "detalle_carro.html"

    def dispatch(self, request, *args, **kwargs):
        self.usuario = User.objects.get(id=request.user.id)
        try:
            self.cliente = Cliente.objects.get(idusuario=self.usuario)
        except Cliente.DoesNotExist:
            alert = "Si desea acceder a la cart, primero debe registrar sus datos como cliente"
            messages.error(request, alert)
            return redirect("panel_usuario")
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, cart_id):
        cart = cart.objects.get(id=cart_id)
        context = {"cart": cart,
                   "cliente": self.cliente}
        return render(request, self.template_name, context)

    def post(self, request, cart_id):
        cart = cart.objects.get(id=cart_id)
        if request.POST.get('delete'):
            product_id = request.POST.get('delete')
            ProductoCart.objects.filter(id=product_id).delete()
            return redirect('cart_detalle', cart_id=cart.id)
        if request.POST.get('delete_cart'):
            cart_id = request.POST.get('delete_cart')
            cart.objects.get(id=cart_id).delete()
            return redirect('user_cart')
        if request.POST.get('comprar'):
            return redirect('pedido_usuario', cart_id=cart_id, cliente_id=cart.idcliente.id)


class PanelUsuario(View, LoginRequiredMixin):
    form = ClienteForm

    def get(self, request):
        usuario = User.objects.get(id=request.user.id)
        form = self.form(initial={'email': usuario.email})
        with contextlib.suppress(Exception):
            cliente = Cliente.objects.get(idusuario=request.user.id)
            form = self.form(instance=cliente)
        context = {"form": form}
        return render(request, "panel_usuario.html", context)

    def post(self, request):
        try:
            cliente = Cliente.objects.get(idusuario=request.user.id)
            form = self.form(request.POST, instance=cliente)
        except Cliente.DoesNotExist:
            form = self.form(request.POST)

        if form.is_valid():
            cliente = form.save(commit=False)
            usuario = User.objects.get(id=request.user.id)
            cliente.idusuario = usuario
            cliente.email = usuario.email
            cliente.save()
            return redirect("index")

        context = {"form": form}
        return render(request, "panel_usuario.html", context)


class ProductList(ListView):
    model = Producto
    context_object_name = 'productos'
    ordering = ['nombre']
    template_name = "product_list.html"

    def get_queryset(self):
        return super().get_queryset()


class ProductDetail(View):
    template_name = "producto.html"

    def dispatch(self, request, *args, **kwargs):
        try:
            self.usuario = request.user
        except User.DoesNotExist:
            pass

        try:
            self.cliente = Cliente.objects.get(idusuario=self.usuario)
        except:
            pass

        try:
            self.carts = Cart.objects.filter(idcliente=self.cliente)
        except:
            pass

        return super().dispatch(request, *args, **kwargs)

    def get(self, request, pk):
        producto = get_object_or_404(Producto, pk=pk)
        precio = producto.precio
        context = {
            'producto': producto,
            'precio': precio,
        }
        if request.user.is_authenticated:
            agregar_producto_form = AgregarProductoForm(cliente=self.cliente)
            context['agregar_producto_form'] = agregar_producto_form
        return render(request, self.template_name, context)

    def post(self, request, pk):
        producto = get_object_or_404(Producto, pk=pk)
        agregar_producto_form = AgregarProductoForm(
            request.POST, cliente=self.cliente)

        if agregar_producto_form.is_valid():
            cantidad_deseada = agregar_producto_form.cleaned_data['cantidad']
            cart_seleccionada = agregar_producto_form.cleaned_data['cart']
            producto_cart, created = ProductoCart.objects.get_or_create(
                idcart=cart_seleccionada,
                idproducto=producto,
                defaults={'cantidad_deseada': cantidad_deseada}
            )
            if not created:
                producto_cart.cantidad_deseada += cantidad_deseada
                producto_cart.save()
            alert = "Producto agregado con éxito a la cart"
            messages.success(request, alert)
            return redirect('producto', pk=pk)

        context = {
            'producto': producto,
            'precio': producto.precio,
            'agregar_producto_form': agregar_producto_form,
        }
        return render(request, self.template_name, context)


class ContactView(View):
    def get(self, request):
        return render(request, 'contacto.html')


class PedidoDetalleView(View, LoginRequiredMixin):
    template_name = "detalle_pedido.html"

    def dispatch(self, request, *args, **kwargs):
        self.usuario = User.objects.get(id=request.user.id)
        if request.user.is_staff:
            return super().dispatch(request, *args, **kwargs)
        else:
            try:
                self.cliente = Cliente.objects.get(idusuario=self.usuario)
            except Cliente.DoesNotExist:
                alert = "Por favor agregué sus datos como cliente"
                messages.error(request, alert)
                return redirect("panel_usuario")
        self.pk = kwargs.get('pk')
        pedido = get_object_or_404(Pedido, pk=self.pk)
        if pedido.cart.idcliente == self.cliente:
            pass
        else:
            alert = "No tienes permiso para acceder a ese detalle"
            messages.error(request, alert)
            return redirect("panel_usuario")
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, pk):
        pedido = get_object_or_404(Pedido, pk=pk)
        context = {'pedido': pedido}
        try:
            detalle = Detalle.objects.filter(pedido=pedido)
            print("detalles  ", detalle)
            context["detalle"] = detalle
        except Detalle.DoesNotExist:
            pass
        if request.user.is_staff:
            form = EstadoPedidoForm(instance=pedido, request=request)
            context["form"] = form
        else:
            pass
        return render(request, "detalle_pedido.html", context)

    def post(self, request, pk):
        pedido = get_object_or_404(Pedido, pk=pk)
        form = EstadoPedidoForm(request.POST, instance=pedido, request=request)
        if request.POST.get('cancelar_pedido'):
            if form.is_valid():
                pedido = form.save(commit=False)
                pedido.estadopedido = 'Cancelado'
                pedido.save()
                return redirect('pedidos')
        if form.is_valid():
            pedido = form.save(commit=False)
            pedido.estadopedido = form.cleaned_data['estadopedido']
            user = pedido.cart.idcliente
            send_mail(
                'Estado de pedido',
                'El estado de su pedido ha cambiado a: ' + pedido.estadopedido,
                settings.EMAIL_HOST_USER,
                [user.email],
                fail_silently=False,
            )
            print("[DEBUG] ", user.email)
            pedido.save()
            return redirect('pedidos')