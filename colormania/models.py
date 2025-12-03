from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal


# ==================== CATALOGOS (Tus modelos originales) ====================

class Sellador(models.Model):
    nombre = models.CharField(max_length=100)
    foto_sellador = models.ImageField(upload_to='img_selladores/', blank=True, null=True)
    descripcion = models.CharField(max_length=250)
    precio = models.DecimalField(max_digits=20, decimal_places=2)
    stock = models.IntegerField()

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = "Sellador"
        verbose_name_plural = "Selladores"

class Producto(models.Model):
    nombre = models.CharField(max_length=100)
    foto_producto = models.ImageField(upload_to='img_productos/', blank=True, null=True)
    descripcion = models.CharField(max_length=250)
    precio = models.DecimalField(max_digits=20, decimal_places=2)
    stock = models.IntegerField()

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = "Producto"
        verbose_name_plural = "Productos"

class Pintura(models.Model):
    nombre = models.CharField(max_length=100)
    foto_pintura = models.ImageField(upload_to='img_pinturas/', blank=True, null=True)
    descripcion = models.CharField(max_length=250)
    precio = models.DecimalField(max_digits=20, decimal_places=2)
    stock = models.IntegerField()

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = "Pintura"
        verbose_name_plural = "Pinturas"

class Personalizado(models.Model):
    pintura = models.ForeignKey(Pintura, on_delete=models.CASCADE, related_name='personalizados')
    color = models.CharField(max_length=50) 
    # El usuario es opcional aquí, pero útil si guardan sus diseños
    usuario = models.ForeignKey('Usuario', on_delete=models.CASCADE, null=True, blank=True)
    
    # IMPORTANTE: Un personalizado debe tener precio base (el de la pintura)
    # o un precio calculado. Usaremos una propiedad para acceder al precio de la pintura.
    
    @property
    def precio(self):
        return self.pintura.precio

    def __str__(self):
        return f"{self.pintura.nombre} - {self.color}"

    class Meta:
        verbose_name = "Personalizado"
        verbose_name_plural = "Personalizados"
        ordering = ['-id']

class Inspiracion(models.Model):
    imagen = models.ImageField(upload_to='inspiracion/')
    
    def __str__(self):
        return f"Imagen {self.id}"

    class Meta:
        ordering = ['-id']


class Usuario(models.Model):
    nombre = models.CharField(max_length=50)
    apellido = models.CharField(max_length=50)
    email = models.EmailField(max_length=100)
    telefono = models.CharField(max_length=15)
    contraseña = models.CharField(max_length=128) 
    pais = models.CharField(max_length=30, choices=[
        ('MEXICO', 'Mexico'),
        ('ESTADOS UNIDOS', 'Estados Unidos'),
        ('GUATEMALA', 'Guatemala'),
        ('EL SALVADOR', 'El Salvador'),
        ('HONDURAS', 'Honduras'),
        ('COSTA RICA', 'Costa Rica'),
        ('PANAMA', 'Panama'),
    ])
    estado = models.CharField(max_length=50)
    ciudad = models.CharField(max_length=50)
    codigo_postal = models.CharField(max_length=10)
    calle = models.CharField(max_length=50)
    num_domicilio = models.CharField(max_length=10)
    detalles = models.CharField(max_length=250, default='INFORMACION DEL DOMICILIO')

    def __str__(self):
        return f"{self.nombre} {self.apellido}"

    class Meta:
        verbose_name = "Usuario"
        verbose_name_plural = "Usuarios"


# ==================== LÓGICA DEL CARRITO (MODIFICADA) ====================

class Carrito(models.Model):
    usuario = models.OneToOneField('Usuario', on_delete=models.CASCADE, related_name='carrito')
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    # Calculamos el total sumando los subtotales de los items hijos
    @property
    def total(self):
        total = sum(item.subtotal for item in self.items.all())
        return total

    def __str__(self):
        return f"Carrito de {self.usuario}"

    class Meta:
        verbose_name = "Carrito"
        verbose_name_plural = "Carritos"


class ItemCarrito(models.Model):
    # Relación inversa: Un carrito tiene muchos items
    carrito = models.ForeignKey(Carrito, on_delete=models.CASCADE, related_name='items')
    
    # Punteros a los diferentes tipos de productos (SOLO UNO debe llenarse)
    producto = models.ForeignKey(Producto, on_delete=models.SET_NULL, null=True, blank=True)
    sellador = models.ForeignKey(Sellador, on_delete=models.SET_NULL, null=True, blank=True)
    personalizado = models.ForeignKey(Personalizado, on_delete=models.SET_NULL, null=True, blank=True)
    
    cantidad = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])

    # Propiedad para obtener el objeto real sin importar cuál sea
    @property
    def objeto_relacionado(self):
        if self.producto: return self.producto
        if self.sellador: return self.sellador
        if self.personalizado: return self.personalizado
        return None

    # Propiedad para obtener el precio unitario dinámicamente
    @property
    def precio_unitario(self):
        obj = self.objeto_relacionado
        return obj.precio if obj else Decimal(0)

    # Propiedad para calcular el subtotal (precio * cantidad)
    @property
    def subtotal(self):
        return self.precio_unitario * self.cantidad

    def __str__(self):
        obj = self.objeto_relacionado
        nombre = obj.nombre if obj and hasattr(obj, 'nombre') else 'Item Personalizado'
        # Para personalizado usamos el nombre de la pintura
        if self.personalizado:
            nombre = f"{self.personalizado.pintura.nombre} ({self.personalizado.color})"
            
        return f"{self.cantidad}x {nombre}"

    class Meta:
        verbose_name = "Item del Carrito"
        verbose_name_plural = "Items del Carrito"



class Color(models.Model):
    codigo = models.CharField(max_length=50)
    descripcion = models.CharField(max_length=250)
    tipo = models.CharField(max_length=30, choices=[
        ('CALIDOS', 'Calidos'),
        ('FRIOS', 'Frios'),
        ('GRISES', 'Grises'),
        ('PASTELES', 'Pasteles'),
        ('VIVOS', 'Vivos'),
    ])
    popularidad = models.IntegerField()

    def __str__(self):
        return f"{self.codigo}"

    class Meta:
        verbose_name = "Color"
        verbose_name_plural = "Colores"

class ItemPedido(models.Model):
    pedido = models.ForeignKey('Pedido', on_delete=models.CASCADE, related_name='items')
    
    # Guardamos los datos como TEXTO para que si borras el producto original,
    # el historial de ventas no se rompa.
    nombre_producto = models.CharField(max_length=150)
    precio = models.DecimalField(max_digits=20, decimal_places=2)
    cantidad = models.PositiveIntegerField(default=1)
    
    # Opcional: Para saber qué era (Producto, Sellador, etc)
    tipo = models.CharField(max_length=50, blank=True)
    
    def __str__(self):
        return f"{self.cantidad}x {self.nombre_producto}"

# 2. Modifica el modelo Pedido
class Pedido(models.Model):
    METODOS_PAGO = [
        ('TARJETA', 'Tarjeta'),
        ('MERCADO_PAGO', 'Mercado Pago'),
        ('OXXO', 'Oxxo'),
    ]

    usuario = models.ForeignKey('Usuario', on_delete=models.CASCADE, related_name='pedidos')
    
    # --- CAMBIO IMPORTANTE: Quitamos la relación OneToOne con Carrito ---
    # Ya no necesitamos el campo 'carrito' aquí porque los items se guardarán en ItemPedido
    
    metodo_pago = models.CharField(max_length=30, choices=METODOS_PAGO)
    total_compra = models.DecimalField(max_digits=20, decimal_places=2)
    fecha = models.DateTimeField(auto_now_add=True)
    # Datos de pago y envío (igual que antes)...
    numero_tarjeta = models.CharField(max_length=19, blank=True, null=True)
    clabe = models.CharField(max_length=18, blank=True, null=True)
    fecha_vencimiento = models.CharField(max_length=5, blank=True, null=True)
    fecha_llegada = models.DateField(null=True, blank=True)
    estado_envio = models.CharField(max_length=50, default="Pendiente")

    def __str__(self):
        return f"Pedido {self.id} - {self.usuario} - ${self.total_compra}"

    class Meta:
        verbose_name = "Pedido"
        verbose_name_plural = "Pedidos"
        ordering = ['-fecha']