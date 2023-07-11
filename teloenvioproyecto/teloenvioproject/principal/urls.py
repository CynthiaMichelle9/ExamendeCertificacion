from django.urls import path
from .views import IndexView, PedidosView, GestionProdView, IngresoProductoView, CrearClienteView, AgregarProductosCartView, CrearPedidoView, PanelUsuario, ProductList, ProductDetail, ContactView, ListaCartView, CartDetalleView, PedidoDetalleView, CrearPedidoUsuarioView, eliminar_pedido

urlpatterns = [
    path('', IndexView.as_view(template_name='index.html'), name='home'),
    path('pedidos', PedidosView.as_view(), name='pedidos'),
    path('gestion', GestionProdView.as_view(), name="gestionprod"),
    path('nuevo_producto', IngresoProductoView.as_view(), name="nuevo_producto"),
    path('crear_cliente/', CrearClienteView.as_view(), name="crear_cliente"),
    path('agregar_productos_cart/<int:cart_id>/',
         AgregarProductosCartView.as_view(), name="agregar_productos_cart"),
    path('crear_pedido/<int:cart_id>/<int:cliente_id>/',
         CrearPedidoView.as_view(), name='crear_pedido'),
    path('panel_usuario/', PanelUsuario.as_view(), name="panel_usuario"),
    path('productos', ProductList.as_view(), name='productos'),
    path('producto/<int:pk>/', ProductDetail.as_view(), name='producto'),
    path('contacto/', ContactView.as_view(), name="contacto"),
    path('mis_cart/', ListaCartView.as_view(), name="user_cart"),
    path('cart_detalle/<int:cart_id>/',
         CartDetalleView.as_view(), name="cart_detalle"),
    path('pedido_detalle/<int:pk>/',
         PedidoDetalleView.as_view(), name="pedido_detalle"),
    path('pedido_usuario/<int:cart_id>/<int:cliente_id>',
         CrearPedidoUsuarioView.as_view(), name="pedido_usuario"),
    path('pedido_detalle/<int:pk>/eliminar/',
         eliminar_pedido, name="eliminar_pedido")
]
