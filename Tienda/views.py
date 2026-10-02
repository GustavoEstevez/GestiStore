from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.core.exceptions import PermissionDenied
from .models import Producto, Venta, DetalleVenta, Perfil
from .forms import ProductoForm, RegistroForm


# ─── DECORADOR ADMIN ──────────────────────────────────────
def solo_admin(view_func):
    def wrapper(request, *args, **kwargs):
        try:
            if request.user.perfil.rol == 'admin':
                return view_func(request, *args, **kwargs)
        except Exception:
            pass
        raise PermissionDenied
    return wrapper


def error_403(request, exception=None):
    return render(request, 'tienda/403.html', status=403)


# ─── INICIO ───────────────────────────────────────────────
@login_required
def inicio(request):
    productos = Producto.objects.filter(activo=True).order_by('-fecha_creacion')
    destacados = productos[:8]
    total_productos = Producto.objects.filter(activo=True).count()
    categorias = Producto.CATEGORIA_CHOICES
    return render(request, 'tienda/inicio.html', {
        'destacados': destacados,
        'total_productos': total_productos,
        'categorias': categorias,
    })


# ─── AUTH ─────────────────────────────────────────────────
def registro(request):
    form = RegistroForm(request.POST or None)
    if form.is_valid():
        usuario = form.save()
        Perfil.objects.create(usuario=usuario, rol='operador')
        messages.success(request, 'Cuenta creada. Ya podés iniciar sesión.')
        return redirect('login')
    return render(request, 'tienda/registro.html', {'form': form})


# ─── PRODUCTOS ────────────────────────────────────────────
@login_required
def lista_productos(request):
    q = request.GET.get('q', '')
    categoria = request.GET.get('categoria', '')
    productos = Producto.objects.filter(activo=True)

    if q:
        productos = productos.filter(
            models_Q_nombre_descripcion(q)
        )
    if categoria:
        productos = productos.filter(categoria=categoria)

    return render(request, 'tienda/lista_productos.html', {
        'productos': productos,
        'q': q,
        'categoria_actual': categoria,
        'CATEGORIA_CHOICES': Producto.CATEGORIA_CHOICES,
    })


def models_Q_nombre_descripcion(q):
    from django.db.models import Q
    return Q(nombre__icontains=q) | Q(descripcion__icontains=q)


@login_required
def detalle_producto(request, pk):
    producto = get_object_or_404(Producto, pk=pk, activo=True)
    relacionados = Producto.objects.filter(categoria=producto.categoria, activo=True)\
        .exclude(pk=producto.pk)[:4]
    return render(request, 'tienda/detalle_producto.html', {
        'producto': producto,
        'relacionados': relacionados,
    })


@login_required
@solo_admin
def crear_producto(request):
    form = ProductoForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        form.save()
        messages.success(request, 'Producto creado.')
        return redirect('lista_productos')
    return render(request, 'tienda/form_producto.html', {'form': form, 'titulo': 'Nuevo Producto'})


@login_required
@solo_admin
def editar_producto(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    form = ProductoForm(request.POST or None, request.FILES or None, instance=producto)
    if form.is_valid():
        form.save()
        messages.success(request, 'Producto actualizado.')
        return redirect('lista_productos')
    return render(request, 'tienda/form_producto.html', {
        'form': form, 'titulo': 'Editar Producto', 'producto': producto
    })


@login_required
@solo_admin
def eliminar_producto(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    if request.method == 'POST':
        producto.activo = False
        producto.save()
        messages.success(request, 'Producto eliminado.')
        return redirect('lista_productos')
    return render(request, 'tienda/confirmar_eliminar.html', {'objeto': producto})


# ─── CARRITO ──────────────────────────────────────────────
@login_required
def agregar_carrito(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    if request.method == 'POST':
        try:
            cantidad = int(request.POST.get('cantidad', 1))
        except (ValueError, TypeError):
            cantidad = 1
        if cantidad < 1:
            cantidad = 1
        if cantidad > producto.stock:
            messages.error(request, f'Solo hay {producto.stock} unidades disponibles.')
            return redirect('detalle_producto', pk=pk)

        carrito = request.session.get('carrito', {})
        key = str(pk)
        if key in carrito:
            nueva_cantidad = carrito[key]['cantidad'] + cantidad
            if nueva_cantidad > producto.stock:
                messages.error(request, f'No podés superar el stock disponible ({producto.stock}).')
                return redirect('detalle_producto', pk=pk)
            carrito[key]['cantidad'] = nueva_cantidad
        else:
            carrito[key] = {
                'producto_id': pk,
                'producto_nombre': producto.nombre,
                'producto_precio': float(producto.precio),
                'producto_imagen': producto.imagen.url if producto.imagen else '',
                'producto_categoria': producto.get_categoria_display(),
                'cantidad': cantidad,
            }
        request.session['carrito'] = carrito
        messages.success(request, 'Producto agregado al carrito.')
        return redirect('ver_carrito')
    return redirect('detalle_producto', pk=pk)


@login_required
def ver_carrito(request):
    carrito = request.session.get('carrito', {})
    items = []
    total = 0
    for key, item in carrito.items():
        subtotal = item['producto_precio'] * item['cantidad']
        total += subtotal
        items.append({**item, 'subtotal': subtotal, 'key': key})
    return render(request, 'tienda/carrito.html', {'items': items, 'total': total})


@login_required
def eliminar_carrito(request, key):
    carrito = request.session.get('carrito', {})
    if key in carrito:
        del carrito[key]
        request.session['carrito'] = carrito
        messages.success(request, 'Producto eliminado del carrito.')
    return redirect('ver_carrito')


@login_required
def confirmar_compra(request):
    carrito = request.session.get('carrito', {})
    if not carrito:
        messages.error(request, 'Tu carrito está vacío.')
        return redirect('lista_productos')

    items = []
    total = 0
    for key, item in carrito.items():
        subtotal = item['producto_precio'] * item['cantidad']
        total += subtotal
        items.append({**item, 'subtotal': subtotal, 'key': key})

    return render(request, 'tienda/pago.html', {'items': items, 'total': total})


@login_required
def procesar_pago(request):
    if request.method != 'POST':
        return redirect('ver_carrito')

    carrito = request.session.get('carrito', {})
    if not carrito:
        return redirect('lista_productos')

    metodo = request.POST.get('metodo_pago', 'tarjeta')

    if metodo != 'transferencia':
        numero = request.POST.get('numero_tarjeta', '').replace(' ', '')
        nombre = request.POST.get('nombre_tarjeta', '')
        vencimiento = request.POST.get('vencimiento', '')
        cvv = request.POST.get('cvv', '')

        if len(numero) != 16 or not numero.isdigit():
            messages.error(request, 'El número de tarjeta debe tener 16 dígitos.')
            return redirect('confirmar_compra')
        if not nombre:
            messages.error(request, 'Ingresá el nombre del titular.')
            return redirect('confirmar_compra')
        if len(vencimiento) != 5:
            messages.error(request, 'Ingresá una fecha de vencimiento válida (MM/AA).')
            return redirect('confirmar_compra')
        if len(cvv) not in [3, 4]:
            messages.error(request, 'El CVV debe tener 3 o 4 dígitos.')
            return redirect('confirmar_compra')

    # Verificar stock y calcular total
    total = 0
    for key, item in carrito.items():
        producto = get_object_or_404(Producto, pk=item['producto_id'])
        if item['cantidad'] > producto.stock:
            messages.error(request, f'No hay stock suficiente de "{producto.nombre}".')
            return redirect('ver_carrito')
        total += producto.precio * item['cantidad']

    # Crear venta
    venta = Venta.objects.create(
        usuario=request.user,
        total=total,
        metodo_pago=metodo,
        estado='completada',
    )

    # Crear detalles y descontar stock
    for key, item in carrito.items():
        producto = get_object_or_404(Producto, pk=item['producto_id'])
        DetalleVenta.objects.create(
            venta=venta,
            producto=producto,
            cantidad=item['cantidad'],
            precio_unitario=producto.precio,
        )
        producto.stock -= item['cantidad']
        producto.save()

    request.session['carrito'] = {}
    request.session['ultima_compra'] = venta.codigo

    return redirect('compra_exitosa')


@login_required
def compra_exitosa(request):
    codigo = request.session.get('ultima_compra', '')
    venta = Venta.objects.filter(codigo=codigo).select_related('usuario').first()
    detalles = venta.detalles.select_related('producto').all() if venta else []
    return render(request, 'tienda/compra_exitosa.html', {
        'venta': venta,
        'detalles': detalles,
    })


# ─── MIS COMPRAS ──────────────────────────────────────────
@login_required
def mis_compras(request):
    ventas = Venta.objects.filter(usuario=request.user, estado='completada')\
        .prefetch_related('detalles__producto').order_by('-fecha_venta')
    return render(request, 'tienda/mis_compras.html', {'ventas': ventas})
