from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Color, Pedido, Usuario, Personalizado, Pintura, Producto, Sellador, Inspiracion, Carrito, ItemCarrito, Pedido, ItemPedido
from django.http import HttpResponse # Importa HttpResponse para casos de depuración o confirmación simple
from django.views.decorators.http import require_POST
from django.contrib.auth import authenticate, logout, login as auth_login
from django.contrib import messages
from functools import wraps
from datetime import timedelta
from django.utils import timezone
import re
from django.contrib.auth.hashers import make_password, check_password

# Create your views here.
def index_colormania(request):
    """
    Vista para la página de inicio del sistema.
    """
    return render(request, 'colormania/index.html')

def login_usuario(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password_ingresada = request.POST.get('password') # Lo que el usuario escribe

        try:
            usuario = Usuario.objects.get(email=email)
            if check_password(password_ingresada, usuario.contraseña):
                request.session['usuario_id'] = usuario.id
                request.session['usuario_nombre'] = usuario.nombre
                request.session['usuario_email'] = usuario.email
                request.session['esta_logueado'] = True  # ← bandera infalible

                messages.success(request, f'¡Bienvenido, {usuario.nombre}!')
                return redirect('index_colormania')
            else:
                messages.error(request, 'Contraseña incorrecta.')
        except Usuario.DoesNotExist:
            messages.error(request, 'Este email no está registrado.')

    return render(request, 'colormania/login_usuario.html')

def login_admin(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None and user.is_staff: 
            auth_login(request, user)
            messages.success(request, f'¡Bienvenido, administrador {user.username}!')
            return redirect('index_admin')  # ¡AQUÍ ESTÁ LA CORRECCIÓN!
            # o 'index_admin' si prefieres ese nombre
        else:
            messages.error(request, 'Usuario o contraseña de administrador incorrectos.')

    return render(request, 'colormania/login_admin.html')




def registro(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        apellido = request.POST.get('apellido')
        email = request.POST.get('email')
        telefono = request.POST.get('telefono')
        contraseña = request.POST.get('contraseña')
        confirmar_contraseña = request.POST.get('confirmar_contraseña')
        
        # Resto de campos de dirección...
        pais = request.POST.get('pais')
        estado = request.POST.get('estado')
        ciudad = request.POST.get('ciudad')
        codigo_postal = request.POST.get('codigo_postal')
        calle = request.POST.get('calle')
        num_domicilio = request.POST.get('num_domicilio')
        detalles = request.POST.get('detalles', 'INFORMACION DEL DOMICILIO')

        # ==================== VALIDACIONES DE SEGURIDAD ====================
        
        errores = []

        # 1. Longitud mínima (8 caracteres)
        if len(contraseña) < 8:
            errores.append('La contraseña debe tener al menos 8 caracteres.')

        # 2. Al menos una Mayúscula (A-Z)
        if not re.search(r'[A-Z]', contraseña):
            errores.append('La contraseña debe incluir al menos una letra MAYÚSCULA.')

        # 3. Al menos un Número (0-9)
        if not re.search(r'\d', contraseña):
            errores.append('La contraseña debe incluir al menos un NÚMERO.')

        # Si hay errores de seguridad, los mostramos y detenemos el proceso
        if errores:
            for error in errores:
                messages.error(request, error)
            return render(request, 'colormania/registro.html')

        # ===================================================================

        if contraseña != confirmar_contraseña:
            messages.error(request, 'Las contraseñas no coinciden. Por favor, inténtalo de nuevo.')
            return render(request, 'colormania/registro.html')

        if Usuario.objects.filter(email=email).exists():
            messages.error(request, 'Este email ya está registrado. ¿Ya tienes una cuenta?')
            return render(request, 'colormania/registro.html')

        try:
            nuevo_usuario = Usuario.objects.create(
                nombre=nombre,
                apellido=apellido,
                email=email,
                telefono=telefono,
                
                # AQUÍ ENCRIPTAMOS LA CONTRASEÑA ANTES DE GUARDARLA
                contraseña=make_password(contraseña), 
                
                pais=pais,
                estado=estado,
                ciudad=ciudad,
                codigo_postal=codigo_postal,
                calle=calle,
                num_domicilio=num_domicilio,
                detalles=detalles
            )
            messages.success(request, f'¡Bienvenido/a {nombre}! Tu cuenta ha sido creada exitosamente.')
            return redirect('login_usuario')
        except Exception as e:
            messages.error(request, f'Ocurrió un error al intentar registrarte: {e}')

    return render(request, 'colormania/registro.html')

def index(request):
    return render(request, 'colormania/index.html')

def lista_usuarios(request):
    usuarios = Usuario.objects.all().order_by('-id')
    
    paises_choices = Usuario._meta.get_field('pais').choices
    
    return render(request, 'colormania/admin/usuarios.html', {
        'usuarios': usuarios,
        'paises_choices': paises_choices  
    })


def index_admin(request):
    return render(request, 'colormania/admin/index_admin.html')  

def admin_pinturas(request):
    pinturas = Pintura.objects.all().order_by('-id')
    return render(request, 'colormania/admin/admin_pinturas.html', {
        'pinturas': pinturas
    })

def admin_productos(request):
    productos = Producto.objects.all().order_by('-id')
    return render(request, 'colormania/admin/admin_productos.html', {
        'productos': productos
    })

def admin_selladores(request):
    selladores = Sellador.objects.all().order_by('-id')
    return render(request, 'colormania/admin/admin_selladores.html', {
        'selladores': selladores
    })

def admin_colores(request):
    categorias = ['CALIDOS', 'FRIOS', 'VIVOS', 'PASTELES', 'GRISES']
    borrados_total = 0
    colores = Color.objects.all().order_by('id')

    for categoria in categorias:
        # Todos los colores de esta categoría, ordenados por popularidad (de mayor a menor)
        colores_ordenados = list(Color.objects.filter(tipo=categoria).order_by('-popularidad'))

        if len(colores_ordenados) > 15:
            # Guardamos los que van a ser eliminados (del puesto 16 en adelante)
            a_eliminar = colores_ordenados[15:]
            cantidad = len(a_eliminar)
            borrados_total += cantidad

            # Los eliminamos de la base de datos
            for color in a_eliminar:
                color.delete()

            # Mensaje bonito
            messages.warning(request, 
                f"Se eliminaron {cantidad} color(es) menos populares de <strong>{categoria}</strong> → solo quedan los 15 mejores")

    # Ahora cargamos los que SÍ deben mostrarse (máximo 15 por categoría)
    context = {
        'colores_calidos': Color.objects.filter(tipo='CALIDOS').order_by('-popularidad')[:15],
        'colores_frios': Color.objects.filter(tipo='FRIOS').order_by('-popularidad')[:15],
        'colores_vivos': Color.objects.filter(tipo='VIVOS').order_by('-popularidad')[:15],
        'colores_pasteles': Color.objects.filter(tipo='PASTELES').order_by('-popularidad')[:15],
        'colores_grises': Color.objects.filter(tipo='GRISES').order_by('-popularidad')[:15],
        'colores': colores,
    }

    # Mensaje final si se hizo limpieza
    if borrados_total > 0:
        messages.success(request, f"Limpieza completada: se eliminaron {borrados_total} colores en total. ¡Solo quedan los mejores!")

    return render(request, 'colormania/admin/admin_colores.html', context)

# Cerrar sesión del admin
def logout_admin(request):
    logout(request)
    messages.success(request, "¡Sesión de administrador cerrada!")
    return redirect('index_colormania')

def logout_usuario(request):
    try:
        del request.session['usuario_id']
        del request.session['usuario_nombre']
        del request.session['esta_logueado']
    except:
        pass
    messages.success(request, "¡Sesión cerrada correctamente!")
    return redirect('index_colormania')

def ver_pinturas(request):
    pinturas = Pintura.objects.all()  # Cambia por tu modelo de selladores cuando lo tengas
    return render(request, 'colormania/user/ver_pinturas.html', {'pinturas': pinturas})

def ver_selladores(request):
    selladores = Sellador.objects.all()  # Cambia por tu modelo de selladores cuando lo tengas
    return render(request, 'colormania/user/ver_selladores.html', {'selladores': selladores})

def ver_productos(request):
    productos = Producto.objects.all()  # Cambia por tu modelo real cuando lo tengas
    return render(request, 'colormania/user/ver_productos.html', {'productos': productos})

def frios(request):
    colores_frios = Color.objects.filter(tipo='FRIOS').order_by('-popularidad')
    return render(request, 'colormania/user/colores/frios.html', {'colores_frios': colores_frios})

def calidos(request):
    colores_calidos = Color.objects.filter(tipo='CALIDOS').order_by('-popularidad')
    return render(request, 'colormania/user/colores/calidos.html', {'colores_calidos': colores_calidos})

def vivos(request):
    colores_vivos = Color.objects.filter(tipo='VIVOS').order_by('-popularidad')
    return render(request, 'colormania/user/colores/vivos.html', {'colores_vivos': colores_vivos})

def pasteles(request):
    colores_pasteles = Color.objects.filter(tipo='PASTELES').order_by('-popularidad')
    return render(request, 'colormania/user/colores/pasteles.html', {'colores_pasteles': colores_pasteles})

def grises(request):
    colores_grises = Color.objects.filter(tipo='GRISES').order_by('-popularidad')
    return render(request, 'colormania/user/colores/grises.html', {'colores_grises': colores_grises})

# === CREAR USUARIO ===
def crear_usuario(request):
    if request.method == 'POST':
        Usuario.objects.create(
            nombre=request.POST['nombre'],
            apellido=request.POST['apellido'],
            email=request.POST['email'],
            telefono=request.POST.get('telefono', ''),
            contraseña=request.POST['contraseña'],
            pais=request.POST['pais'],
            estado=request.POST['estado'],
            ciudad=request.POST['ciudad'],
            codigo_postal=request.POST['codigo_postal'],
            calle=request.POST['calle'],
            num_domicilio=request.POST['num_domicilio'],
            detalles=request.POST.get('detalles', 'INFORMACION DEL DOMICILIO')
        )
        messages.success(request, "Usuario creado con éxito!")
        return redirect('lista_usuarios')
    
    paises_choices = Usuario._meta.get_field('pais').choices
    return render(request, 'colormania/admin/acciones/crear_usuario.html', {
        'paises_choices': paises_choices
    })

# === ACTUALIZAR USUARIO ===
def actualizar_usuario(request, pk):
    usuario = get_object_or_404(Usuario, pk=pk)
    
    if request.method == 'POST':
        usuario.nombre = request.POST['nombre']
        usuario.apellido = request.POST['apellido']
        usuario.email = request.POST['email']
        usuario.telefono = request.POST.get('telefono', '')
        if request.POST.get('contraseña'):
            usuario.contraseña = request.POST['contraseña']
        usuario.pais = request.POST['pais']
        usuario.estado = request.POST['estado']
        usuario.ciudad = request.POST['ciudad']
        usuario.codigo_postal = request.POST['codigo_postal']
        usuario.calle = request.POST['calle']
        usuario.num_domicilio = request.POST['num_domicilio']
        usuario.detalles = request.POST.get('detalles', usuario.detalles)
        usuario.save()
        messages.success(request, "Usuario actualizado!")
        return redirect('lista_usuarios')
    
    paises_choices = Usuario._meta.get_field('pais').choices
    return render(request, 'colormania/admin/acciones/actualizar_usuario.html', {
        'u': usuario,
        'paises_choices': paises_choices
    })

# === ELIMINAR USUARIO ===
def eliminar_usuario(request, pk):
    usuario = get_object_or_404(Usuario, pk=pk)
    if request.method == 'POST':
        usuario.delete()
        messages.success(request, "Usuario eliminado correctamente.")
        return redirect('lista_usuarios')
    
    return render(request, 'colormania/admin/acciones/eliminar_usuario.html', {
        'u': usuario
    })

def crear_color(request):
    if request.method == 'POST':
        Color.objects.create(
            codigo=request.POST['codigo'].replace('#', '').upper(),
            descripcion=request.POST['descripcion'],
            tipo=request.POST['tipo'],
            popularidad=request.POST.get('popularidad', 50)
        )
        messages.success(request, "¡Color creado con éxito!")
        return redirect('admin_colores')

    return render(request, 'colormania/admin/acciones/crear_color.html')

# === ACTUALIZAR COLOR ===
def actualizar_color(request, pk):
    color = get_object_or_404(Color, pk=pk)
    
    if request.method == 'POST':
        color.codigo = request.POST['codigo'].replace('#', '').upper()
        color.descripcion = request.POST['descripcion']
        color.tipo = request.POST['tipo']
        color.popularidad = request.POST.get('popularidad', color.popularidad)
        color.save()
        messages.success(request, "¡Color actualizado!")
        return redirect('admin_colores')

    return render(request, 'colormania/admin/acciones/actualizar_color.html', {'c': color})

# === ELIMINAR COLOR ===
def eliminar_color(request, pk):
    color = get_object_or_404(Color, pk=pk)
    
    if request.method == 'POST':
        color.delete()
        messages.success(request, "¡Color eliminado!")
        return redirect('admin_colores')

    return render(request, 'colormania/admin/acciones/eliminar_color.html', {'c': color})

def crear_sellador(request):
    if request.method == 'POST':
        sellador = Sellador.objects.create(
            nombre=request.POST['nombre'],
            descripcion=request.POST['descripcion'],
            precio=request.POST['precio'],
            stock=request.POST['stock'],
        )
        if 'foto_sellador' in request.FILES:
            sellador.foto_sellador = request.FILES['foto_sellador']
        sellador.save()
        messages.success(request, "¡Sellador creado con éxito!")
        return redirect('admin_selladores')
    
    return render(request, 'colormania/admin/acciones/crear_sellador.html')

# === ACTUALIZAR SELLADOR ===
def actualizar_sellador(request, pk):
    sellador = get_object_or_404(Sellador, pk=pk)
    
    if request.method == 'POST':
        sellador.nombre = request.POST['nombre']
        sellador.descripcion = request.POST['descripcion']
        sellador.precio = request.POST['precio']
        sellador.stock = request.POST['stock']
        if 'foto_sellador' in request.FILES:
            sellador.foto_sellador = request.FILES['foto_sellador']
        sellador.save()
        messages.success(request, "¡Sellador actualizado!")
        return redirect('admin_selladores')
    
    return render(request, 'colormania/admin/acciones/actualizar_sellador.html', {'s': sellador})

# === ELIMINAR SELLADOR ===
def eliminar_sellador(request, pk):
    sellador = get_object_or_404(Sellador, pk=pk)
    
    if request.method == 'POST':
        sellador.delete()
        messages.success(request, "¡Sellador eliminado!")
        return redirect('admin_selladores')
    
    return render(request, 'colormania/admin/acciones/eliminar_sellador.html', {'s': sellador})

def crear_producto(request):
    if request.method == 'POST':
        producto = Producto.objects.create(
            nombre=request.POST['nombre'],
            descripcion=request.POST['descripcion'],
            precio=request.POST['precio'],
            stock=request.POST['stock'],
        )
        if 'foto_producto' in request.FILES:
            producto.foto_producto = request.FILES['foto_producto']
        producto.save()
        messages.success(request, "¡Producto creado con éxito!")
        return redirect('admin_productos')
    
    return render(request, 'colormania/admin/acciones/crear_producto.html')

# === ACTUALIZAR PRODUCTO ===
def actualizar_producto(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    
    if request.method == 'POST':
        producto.nombre = request.POST['nombre']
        producto.descripcion = request.POST['descripcion']
        producto.precio = request.POST['precio']
        producto.stock = request.POST['stock']
        if 'foto_producto' in request.FILES:
            producto.foto_producto = request.FILES['foto_producto']
        producto.save()
        messages.success(request, "¡Producto actualizado!")
        return redirect('admin_productos')
    
    return render(request, 'colormania/admin/acciones/actualizar_producto.html', {'p': producto})

# === ELIMINAR PRODUCTO ===
def eliminar_producto(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    
    if request.method == 'POST':
        producto.delete()
        messages.success(request, "¡Producto eliminado!")
        return redirect('admin_productos')
    
    return render(request, 'colormania/admin/acciones/eliminar_producto.html', {'p': producto})

def crear_pintura(request):
    if request.method == 'POST':
        pintura = Pintura.objects.create(
            nombre=request.POST['nombre'],
            descripcion=request.POST['descripcion'],
            precio=request.POST['precio'],
            stock=request.POST['stock'],
        )
        if 'foto_pintura' in request.FILES:
            pintura.foto_pintura = request.FILES['foto_pintura']
        pintura.save()
        messages.success(request, "¡Pintura creada con éxito!")
        return redirect('admin_pinturas')
    
    return render(request, 'colormania/admin/acciones/crear_pintura.html')

# === ACTUALIZAR PINTURA ===
def actualizar_pintura(request, pk):
    pintura = get_object_or_404(Pintura, pk=pk)
    
    if request.method == 'POST':
        pintura.nombre = request.POST['nombre']
        pintura.descripcion = request.POST['descripcion']
        pintura.precio = request.POST['precio']
        pintura.stock = request.POST['stock']
        if 'foto_pintura' in request.FILES:
            pintura.foto_pintura = request.FILES['foto_pintura']
        pintura.save()
        messages.success(request, "¡Pintura actualizada!")
        return redirect('admin_pinturas')
    
    return render(request, 'colormania/admin/acciones/actualizar_pintura.html', {'p': pintura})

# === ELIMINAR PINTURA ===
def eliminar_pintura(request, pk):
    pintura = get_object_or_404(Pintura, pk=pk)
    
    if request.method == 'POST':
        pintura.delete()
        messages.success(request, "¡Pintura eliminada!")
        return redirect('admin_pinturas')
    
    return render(request, 'colormania/admin/acciones/eliminar_pintura.html', {'p': pintura})

def subir_inspiracion(request):
    if request.method == 'POST':
        Inspiracion.objects.create(imagen=request.FILES['imagen'])
        messages.success(request, "¡Imagen subida!")
        return redirect('admin_inspiracion')
    return render(request, 'colormania/admin/acciones/subir_inspiracion.html')

def ver_inspiracion(request):
    imagenes = Inspiracion.objects.all()
    return render(request, 'colormania/user/ver_inspiracion.html', {
        'imagenes': imagenes
    })

# Panel de administrador (ver + eliminar)
def admin_inspiracion(request):
    imagenes = Inspiracion.objects.all()
    return render(request, 'colormania/admin/admin_inspiracion.html', {
        'imagenes': imagenes
    })


# Eliminar imagen
def eliminar_inspiracion(request, pk):
    img = get_object_or_404(Inspiracion, pk=pk)
    
    if request.method == 'POST':
        img.delete()
        messages.success(request, "Imagen eliminada correctamente")
        return redirect('admin_inspiracion')
    
    return render(request, 'colormania/admin/acciones/eliminar_inspiracion.html', {'img': img})


def personalizar_pintura(request, pintura_id):
    # 1. Obtener el usuario desde la sesión (igual que en las otras vistas)
    usuario_id = request.session.get('usuario_id')
    if not usuario_id:
        messages.error(request, "Inicia sesión para personalizar.")
        return redirect('login_usuario')
    
    usuario = Usuario.objects.get(id=usuario_id)
    pintura = get_object_or_404(Pintura, id=pintura_id)

    if request.method == 'POST':
        color = request.POST.get('color')
        # Obtenemos la cantidad, si no viene, asumimos 1
        cantidad = int(request.POST.get('cantidad', 1))

        # 2. Crear el objeto Personalizado
        personalizado = Personalizado.objects.create(
            pintura=pintura,
            color=color,
            usuario=usuario
        )

        # 3. Obtener o crear el Carrito del usuario
        carrito, _ = Carrito.objects.get_or_create(usuario=usuario)

        # 4. Crear el ItemCarrito vinculado al CARRITO (NO al usuario directamente)
        #    Usamos .create() porque los personalizados suelen ser únicos por color
        ItemCarrito.objects.create(
            carrito=carrito,          # <--- AQUÍ ESTABA EL ERROR (antes decías usuario=usuario)
            personalizado=personalizado,
            cantidad=cantidad
        )

        messages.success(request, f"¡Tu {pintura.nombre} color {color} se agregó al carrito!")
        return redirect('ver_carrito')

    return render(request, 'colormania/user/personalizar.html', {
        'pintura': pintura
    })


def agregar_sellador(request, sellador_id):
    sellador = get_object_or_404(Sellador, id=sellador_id)
    
    # Verificar que haya stock
    if sellador.stock <= 0:
        messages.error(request, f"¡Lo sentimos! {sellador.nombre} está agotado.")
        return redirect('ver_selladores')  # o la página donde muestras los selladores

    # Obtener el usuario real desde la sesión
    usuario = Usuario.objects.get(id=request.session['usuario_id'])
    
    # Obtener o crear el ItemCarrito
    item_carrito, created = ItemCarrito.objects.get_or_create(
        usuario=usuario,
        defaults={
            'cantidad_productos': 0,
            'cantidad_selladores': 0,
            'cantidad_personalizados': 0
        }
    )
    
    # Agregar el sellador y aumentar cantidad
    item_carrito.selladores.add(sellador)
    item_carrito.cantidad_selladores += 1
    item_carrito.save()

    messages.success(request, f"¡{sellador.nombre} agregado al carrito!")
    return redirect('ver_carrito')

def agregar_producto(request, producto_id):  # ← ¡AQUÍ ESTABA EL ERROR!
    producto = get_object_or_404(Producto, id=producto_id)
    
    # Obtener usuario real
    usuario = Usuario.objects.get(id=request.session['usuario_id'])
    
    # Obtener o crear ItemCarrito
    item_carrito, created = ItemCarrito.objects.get_or_create(
        usuario=usuario,
        defaults={
            'cantidad_productos': 0,
            'cantidad_selladores': 0,
            'cantidad_personalizados': 0
        }
    )
    
    # Agregar producto y aumentar cantidad
    item_carrito.productos.add(producto)
    item_carrito.cantidad_productos += 1
    item_carrito.save()
    
    messages.success(request, f"¡{producto.nombre} agregado al carrito!")
    return redirect('ver_carrito')

# --- HELPER: Obtener usuario desde la sesión manual ---
def _get_usuario(request):
    usuario_id = request.session.get('usuario_id')
    if not usuario_id:
        return None
    try:
        return Usuario.objects.get(id=usuario_id)
    except Usuario.DoesNotExist:
        return None

def ver_carrito(request):
    usuario = _get_usuario(request)
    if not usuario:
        messages.error(request, "Debes iniciar sesión para ver tu carrito.")
        return redirect('login_usuario')

    # Obtener o crear el carrito del usuario
    carrito, created = Carrito.objects.get_or_create(usuario=usuario)
    
    # Esto ya filtra correctamente por usuario
    pedidos_anteriores = Pedido.objects.filter(usuario=usuario).order_by('-fecha')

    return render(request, 'colormania/user/ver_carrito.html', {
        'carrito': carrito,
        'pedidos': pedidos_anteriores  # <--- ¡ESTO FALTABA!
    })

# ==================== AGREGAR PRODUCTOS ====================
@require_POST
def agregar_producto(request, producto_id):
    usuario = _get_usuario(request)
    if not usuario:
        messages.error(request, "Inicia sesión para agregar productos.")
        return redirect('login_usuario')

    producto = get_object_or_404(Producto, id=producto_id)
    cantidad = int(request.POST.get('cantidad', 1))

    # Validar Stock
    if producto.stock < cantidad:
        messages.error(request, f"No hay suficiente stock de {producto.nombre}.")
        return redirect('ver_productos')

    carrito, _ = Carrito.objects.get_or_create(usuario=usuario)

    # Buscar si ya existe este producto en el carrito
    item, created = ItemCarrito.objects.get_or_create(
        carrito=carrito,
        producto=producto,
        defaults={'cantidad': 0} # Si es nuevo, inicia en 0 para sumar abajo
    )

    item.cantidad += cantidad
    item.save()

    messages.success(request, f"¡{producto.nombre} agregado al carrito!")
    return redirect('ver_carrito')

# ==================== AGREGAR SELLADORES ====================
@require_POST
def agregar_sellador(request, sellador_id):
    usuario = _get_usuario(request)
    if not usuario:
        messages.error(request, "Inicia sesión para agregar productos.")
        return redirect('login_usuario')

    sellador = get_object_or_404(Sellador, id=sellador_id)
    cantidad = int(request.POST.get('cantidad', 1))

    if sellador.stock < cantidad:
        messages.error(request, "Stock insuficiente.")
        return redirect('ver_selladores')

    carrito, _ = Carrito.objects.get_or_create(usuario=usuario)

    item, created = ItemCarrito.objects.get_or_create(
        carrito=carrito,
        sellador=sellador,
        defaults={'cantidad': 0}
    )

    item.cantidad += cantidad
    item.save()

    messages.success(request, f"¡{sellador.nombre} agregado al carrito!")
    return redirect('ver_carrito')

# ==================== PERSONALIZAR Y AGREGAR ====================
def procesar_personalizado(request, pintura_id):
    usuario = _get_usuario(request)
    if not usuario:
        messages.error(request, "Inicia sesión para personalizar.")
        return redirect('login_usuario')

    pintura = get_object_or_404(Pintura, id=pintura_id)

    if request.method == 'POST':
        color = request.POST.get('color') # Del input type="color"
        cantidad = int(request.POST.get('cantidad', 1))

        # 1. Crear el objeto Personalizado
        personalizado = Personalizado.objects.create(
            pintura=pintura,
            color=color,
            usuario=usuario
        )

        # 2. Agregar al carrito
        carrito, _ = Carrito.objects.get_or_create(usuario=usuario)
        
        # Siempre creamos un item nuevo para personalizados (para evitar mezclar colores)
        ItemCarrito.objects.create(
            carrito=carrito,
            personalizado=personalizado,
            cantidad=cantidad
        )

        messages.success(request, f"Pintura {pintura.nombre} ({color}) agregada.")
        return redirect('ver_carrito')

    # Si es GET, mostrar formulario
    return render(request, 'colormania/user/personalizar.html', {'pintura': pintura})

# ==================== ACCIONES DEL CARRITO ====================
def actualizar_item(request, item_id, accion):
    usuario = _get_usuario(request)
    if not usuario: return redirect('login_usuario')

    # Aseguramos que el item pertenezca al carrito del usuario (Seguridad)
    item = get_object_or_404(ItemCarrito, id=item_id, carrito__usuario=usuario)

    if accion == 'sumar':
        item.cantidad += 1
        item.save()
    elif accion == 'restar':
        item.cantidad -= 1
        if item.cantidad <= 0:
            item.delete()
        else:
            item.save()
    elif accion == 'eliminar':
        item.delete()
    
    return redirect('ver_carrito')


def realizar_pedido(request):
    usuario = _get_usuario(request) # Usamos tu helper
    if not usuario:
        return redirect('login_usuario')

    # Obtener el carrito
    try:
        carrito = Carrito.objects.get(usuario=usuario)
        if not carrito.items.exists():
            messages.error(request, "Tu carrito está vacío.")
            return redirect('ver_productos')
    except Carrito.DoesNotExist:
        return redirect('ver_productos')

    if request.method == 'POST':
        # 1. ACTUALIZAR DATOS DE DIRECCIÓN DEL USUARIO
        # El usuario puede haber corregido su dirección en el formulario
        usuario.pais = request.POST.get('pais')
        usuario.estado = request.POST.get('estado')
        usuario.ciudad = request.POST.get('ciudad')
        usuario.codigo_postal = request.POST.get('codigo_postal')
        usuario.calle = request.POST.get('calle')
        usuario.num_domicilio = request.POST.get('num_domicilio')
        usuario.detalles = request.POST.get('detalles')
        usuario.telefono = request.POST.get('telefono')
        usuario.save()

        # 2. OBTENER DATOS DE PAGO
        metodo_pago = request.POST.get('metodo_pago')
        
        # Datos opcionales de tarjeta
        numero_tarjeta = request.POST.get('numero_tarjeta')
        fecha_vencimiento = request.POST.get('fecha_vencimiento')
        # La clabe suele ser para transferencias, pero si la pides en tarjeta:
        clabe = request.POST.get('clabe') 

        # 3. CREAR EL PEDIDO
        # Calculamos fecha de llegada (ej: 7 días después)
        fecha_llegada_estimada = timezone.now().date() + timedelta(days=7)

        try:
            nuevo_pedido = Pedido.objects.create(
                usuario=usuario,
                carrito=carrito,
                metodo_pago=metodo_pago,
                total_compra=carrito.total, # Guardamos el total "congelado"
                
                # Datos de tarjeta (solo se guardan si eligió tarjeta)
                numero_tarjeta=numero_tarjeta if metodo_pago == 'TARJETA' else None,
                fecha_vencimiento=fecha_vencimiento if metodo_pago == 'TARJETA' else None,
                clabe=clabe if metodo_pago == 'TARJETA' else None,
                
                fecha_llegada=fecha_llegada_estimada,
                estado_envio="Preparando"
            )

            # 4. LIMPIEZA LÓGICA (Opcional según tu modelo de negocio)
            # Como el modelo Pedido tiene OneToOne con Carrito, este carrito queda "vinculado"
            # y no debería usarse para futuras compras. 
            # Para simplificar, aquí solo redirigimos.
            
            messages.success(request, "¡Pedido realizado con éxito!")
            return redirect('pedido_exitoso', pedido_id=nuevo_pedido.id)

        except Exception as e:
            messages.error(request, f"Ocurrió un error al procesar el pedido: {e}")

    # GET: Mostrar formulario con datos actuales
    # Pasamos las opciones del modelo para el select de país
    paises_choices = Usuario._meta.get_field('pais').choices
    
    return render(request, 'colormania/user/realizar_pedido.html', {
        'usuario': usuario,
        'carrito': carrito,
        'paises_choices': paises_choices
    })

def pedido_exitoso(request, pedido_id):
    pedido = get_object_or_404(Pedido, id=pedido_id)
    return render(request, 'colormania/user/pedido_exitoso.html', {'pedido': pedido})

def _get_usuario(request):
    usuario_id = request.session.get('usuario_id')
    if not usuario_id: return None
    try:
        return Usuario.objects.get(id=usuario_id)
    except Usuario.DoesNotExist:
        return None

def realizar_pedido(request):
    usuario = _get_usuario(request)
    if not usuario: 
        messages.error(request, "Debes iniciar sesión para finalizar la compra.")
        return redirect('login_usuario')

    # Validar que existe el carrito y tiene items
    try:
        carrito = Carrito.objects.get(usuario=usuario)
        if not carrito.items.exists():
            messages.error(request, "Tu carrito está vacío.")
            return redirect('ver_productos')
    except Carrito.DoesNotExist:
        return redirect('ver_productos')

    if request.method == 'POST':
        # 1. ACTUALIZAR INFORMACIÓN DE ENVÍO DEL USUARIO
        # Esto asegura que el pedido vaya a la dirección más reciente escrita en el formulario
        usuario.pais = request.POST.get('pais')
        usuario.estado = request.POST.get('estado')
        usuario.ciudad = request.POST.get('ciudad')
        usuario.codigo_postal = request.POST.get('codigo_postal')
        usuario.calle = request.POST.get('calle')
        usuario.num_domicilio = request.POST.get('num_domicilio')
        usuario.detalles = request.POST.get('detalles')
        usuario.telefono = request.POST.get('telefono')
        usuario.save()

        # 2. PREPARAR DATOS DEL PEDIDO
        metodo_pago = request.POST.get('metodo_pago')
        fecha_llegada_estimada = timezone.now().date() + timedelta(days=7)

        # 3. CREAR EL PEDIDO
        try:
            pedido = Pedido.objects.create(
                usuario=usuario,
                metodo_pago=metodo_pago,
                total_compra=carrito.total,
                fecha_llegada=fecha_llegada_estimada,
                estado_envio="Preparando",
                
                # Datos de pago (solo si aplica tarjeta)
                numero_tarjeta=request.POST.get('numero_tarjeta') if metodo_pago == 'TARJETA' else None,
                fecha_vencimiento=request.POST.get('fecha_vencimiento') if metodo_pago == 'TARJETA' else None,
                clabe=request.POST.get('clabe') if metodo_pago == 'TARJETA' else None,
            )

            # 4. PROCESAR ITEMS (Historial + Resta de Stock)
            for item in carrito.items.all():
                nombre_historial = "Desconocido"
                tipo_historial = "Otro"
                
                # --- LÓGICA POR TIPO DE PRODUCTO ---
                if item.producto:
                    nombre_historial = item.producto.nombre
                    tipo_historial = "Producto"
                    # Restar stock
                    if item.producto.stock >= item.cantidad:
                        item.producto.stock -= item.cantidad
                        item.producto.save()
                    else:
                        # Opcional: Manejo de error si se acabó el stock mientras compraba
                        item.producto.stock = 0
                        item.producto.save()

                elif item.sellador:
                    nombre_historial = item.sellador.nombre
                    tipo_historial = "Sellador"
                    # Restar stock
                    if item.sellador.stock >= item.cantidad:
                        item.sellador.stock -= item.cantidad
                        item.sellador.save()
                    else:
                        item.sellador.stock = 0
                        item.sellador.save()

                elif item.personalizado:
                    nombre_historial = f"{item.personalizado.pintura.nombre} ({item.personalizado.color})"
                    tipo_historial = "Personalizado"
                    # Restar stock a la PINTURA BASE
                    pintura = item.personalizado.pintura
                    if pintura.stock >= item.cantidad:
                        pintura.stock -= item.cantidad
                        pintura.save()
                    else:
                        pintura.stock = 0
                        pintura.save()

                # --- CREAR ITEM EN EL HISTORIAL DEL PEDIDO ---
                ItemPedido.objects.create(
                    pedido=pedido,
                    nombre_producto=nombre_historial,
                    precio=item.precio_unitario,
                    cantidad=item.cantidad,
                    tipo=tipo_historial
                )

            # 5. VACIAR EL CARRITO Y REDIRIGIR
            carrito.items.all().delete()
            
            messages.success(request, "¡Pedido realizado con éxito! Gracias por tu compra.")
            return redirect('pedido_exitoso', pedido_id=pedido.id)

        except Exception as e:
            messages.error(request, f"Ocurrió un error al procesar el pedido: {e}")
            # Si falla, no borramos el carrito para que pueda intentar de nuevo

    # --- MÉTODO GET: MOSTRAR FORMULARIO ---
    paises_choices = Usuario._meta.get_field('pais').choices
    return render(request, 'colormania/user/realizar_pedido.html', {
        'usuario': usuario,
        'carrito': carrito,
        'paises_choices': paises_choices
    })
def admin_pedidos(request):
    # Validar que sea admin (opcional pero recomendado)
    if not request.user.is_staff: 
        return redirect('index_colormania')

    # Obtenemos todos los pedidos ordenados por fecha (más nuevo primero)
    pedidos = Pedido.objects.all().order_by('-fecha')
    
    return render(request, 'colormania/admin/admin_pedidos.html', {
        'pedidos': pedidos
    })

def actualizar_pedido(request, pedido_id):
    # Validar admin
    if not request.user.is_staff:
        return redirect('index_colormania')

    pedido = get_object_or_404(Pedido, id=pedido_id)

    if request.method == 'POST':
        # Verificar si se presionó un botón de acción rápida
        accion_rapida = request.POST.get('accion_rapida')
        
        if accion_rapida:
            # Si presionó un botón rápido, actualizamos el estado directamente
            pedido.estado_envio = accion_rapida
            messages.success(request, f"Pedido actualizado a: {accion_rapida}")
        else:
            # Si no, guardamos lo que venga en los inputs normales
            pedido.estado_envio = request.POST.get('estado_envio')
            fecha = request.POST.get('fecha_llegada')
            
            if fecha:
                pedido.fecha_llegada = fecha
                
            messages.success(request, "Información del pedido actualizada.")

        pedido.save()
        return redirect('admin_pedidos')

    return render(request, 'colormania/admin/acciones/actualizar_pedido.html', {
        'p': pedido
    })

def eliminar_pedido(request, pedido_id):
    if not request.user.is_staff:
        return redirect('index_colormania')

    pedido = get_object_or_404(Pedido, id=pedido_id)

    if request.method == 'POST':
        pedido.delete()
        messages.success(request, f"El pedido #{pedido_id} ha sido eliminado correctamente.")
        return redirect('admin_pedidos')

    return render(request, 'colormania/admin/acciones/eliminar_pedido.html', {
        'p': pedido
    })