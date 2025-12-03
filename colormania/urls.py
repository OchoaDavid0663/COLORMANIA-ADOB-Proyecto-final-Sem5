from django.urls import path
from . import views
urlpatterns = [
    path('', views.index_colormania, name='index_colormania'),
    
    path('login-usuario/', views.login_usuario, name='login_usuario'),
    path('logout/', views.logout_usuario, name='logout_usuario'),
    path('registro/', views.registro, name='registro'), 
    
    path('admin-login/', views.login_admin, name='login_admin'),
    
    path('index-admin/', views.index_admin, name='index_admin'),
    path('admin-logout/', views.logout_admin, name='logout_admin'),
    
    path('pinturas/', views.ver_pinturas, name='ver_pinturas'),
    path('selladores/', views.ver_selladores, name='ver_selladores'),
    path('productos/', views.ver_productos, name='ver_productos'),
    
    path('colores-frios/', views.frios, name='frios'),
    path('colores-calidos/', views.calidos, name='calidos'),
    path('colores-vivos/', views.vivos, name='vivos'),
    path('colores-pasteles/', views.pasteles, name='pasteles'),
    path('colores-grises/', views.grises, name='grises'),

    path('usuarios/', views.lista_usuarios, name='lista_usuarios'),
    path('usuarios/crear/', views.crear_usuario, name='crear_usuario'),
    path('usuarios/<int:pk>/actualizar/', views.actualizar_usuario, name='actualizar_usuario'),
    path('usuarios/<int:pk>/eliminar/', views.eliminar_usuario, name='eliminar_usuario'),

    path('admin-colores/', views.admin_colores, name='admin_colores'),  # ← tu página actual
    path('admin-colores/crear/', views.crear_color, name='crear_color'),
    path('admin-colores/<int:pk>/actualizar/', views.actualizar_color, name='actualizar_color'),
    path('admin-colores/<int:pk>/eliminar/', views.eliminar_color, name='eliminar_color'),

    path('admin-selladores/', views.admin_selladores, name='admin_selladores'),
    path('admin-selladores/crear/', views.crear_sellador, name='crear_sellador'),
    path('admin-selladores/<int:pk>/actualizar/', views.actualizar_sellador, name='actualizar_sellador'),
    path('admin-selladores/<int:pk>/eliminar/', views.eliminar_sellador, name='eliminar_sellador'),

    path('admin-productos/', views.admin_productos, name='admin_productos'),
    path('admin-productos/crear/', views.crear_producto, name='crear_producto'),
    path('admin-productos/<int:pk>/actualizar/', views.actualizar_producto, name='actualizar_producto'),
    path('admin-productos/<int:pk>/eliminar/', views.eliminar_producto, name='eliminar_producto'),

    path('admin-pinturas/', views.admin_pinturas, name='admin_pinturas'),
    path('admin-pinturas/crear/', views.crear_pintura, name='crear_pintura'),
    path('admin-pinturas/<int:pk>/actualizar/', views.actualizar_pintura, name='actualizar_pintura'),
    path('admin-pinturas/<int:pk>/eliminar/', views.eliminar_pintura, name='eliminar_pintura'),

    path('inspiracion/', views.ver_inspiracion, name='ver_inspiracion'),
    path('admin-inspiracion/', views.admin_inspiracion, name='admin_inspiracion'),
    path('admin-inspiracion/subir/', views.subir_inspiracion, name='subir_inspiracion'),
    path('admin-inspiracion/<int:pk>/eliminar/', views.eliminar_inspiracion, name='eliminar_inspiracion'),

    path('personalizar/<int:pintura_id>/', views.personalizar_pintura, name='personalizar_pintura'),
    path('agregar-sellador/<int:sellador_id>/', views.agregar_sellador, name='agregar_sellador'),
    path('agregar-producto/<int:producto_id>/', views.agregar_producto, name='agregar_producto'),

    path('mi-carrito/', views.ver_carrito, name='ver_carrito'),
    
    path('agregar-producto/<int:producto_id>/', views.agregar_producto, name='agregar_producto'),
    path('agregar-sellador/<int:sellador_id>/', views.agregar_sellador, name='agregar_sellador'),
    path('personalizar/<int:pintura_id>/', views.procesar_personalizado, name='personalizar_pintura'),

    path('carrito/item/<int:item_id>/<str:accion>/', views.actualizar_item, name='actualizar_item'),
    path('realizar-pedido/', views.realizar_pedido, name='realizar_pedido'),
    path('pedido-exitoso/<int:pedido_id>/', views.pedido_exitoso, name='pedido_exitoso'),

    path('admin-pedidos/', views.admin_pedidos, name='admin_pedidos'),
    path('admin-pedidos/actualizar/<int:pedido_id>/', views.actualizar_pedido, name='actualizar_pedido'),
    path('admin-pedidos/eliminar/<int:pedido_id>/', views.eliminar_pedido, name='eliminar_pedido'),
]