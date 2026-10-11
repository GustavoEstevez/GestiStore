# AmpereStore (GestiStore)

AmpereStore es una **tienda de tecnología y componentes** desarrollada con **Django**. Permite
gestionar un catálogo de productos, que los clientes compren a través de un carrito y que los
administradores controlen el inventario y vean el historial completo de ventas de cada usuario.

---

## 🚀 Cómo iniciar el proyecto

El proyecto se levanta desde **PowerShell** con el script `iniciar_red.ps1`, que configura los
hosts permitidos y la IP/puerto con los que se publicará la aplicación en la red local, además de
usar esa misma dirección en los enlaces que se envían por email.

```powershell
powershell -ExecutionPolicy Bypass -File .\iniciar_red.ps1 "IP_DE_TU_PC"
```

Ejemplo:

```powershell
powershell -ExecutionPolicy Bypass -File .\iniciar_red.ps1 "192.168.1.25"
```

Opcionalmente se puede indicar otro puerto (por defecto `8000`):

```powershell
powershell -ExecutionPolicy Bypass -File .\iniciar_red.ps1 "192.168.1.25" 8080
```

El script levanta el servidor con `python manage.py runserver 0.0.0.0:<puerto>`, por lo que la
aplicación queda accesible desde otros dispositivos de la red usando `http://<IP>:<puerto>`.

> Para detener el servidor presioná **Ctrl + C**.

Si solo querés ejecutarlo de forma local (sin exponerlo en la red), alcanza con:

```powershell
python manage.py runserver
```

---

## 🧰 Tecnologías

- **Python 3**
- **Django** (con SQLite como base de datos)
- **HTML / CSS** con plantillas de Django
- **PowerShell** para el arranque en red
- **SMTP (Gmail)** para el envío de correos

---

## 📁 Estructura del proyecto

```
GestiStore/
├── GestiStore/            # Configuración del proyecto
│   ├── settings.py        # Ajustes (base de datos, email, static, etc.)
│   ├── urls.py            # URLs raíz (admin, login, recuperación de contraseña)
│   └── wsgi.py / asgi.py
├── Tienda/                # Aplicación principal
│   ├── models.py          # Perfil, Producto, Venta, DetalleVenta
│   ├── views.py           # Toda la lógica de las vistas
│   ├── forms.py           # Formularios (producto, registro, login)
│   ├── urls.py            # URLs de la tienda
│   ├── emails.py          # Envío de código de login y comprobantes
│   ├── admin.py           # Registro de modelos en el admin de Django
│   ├── migrations/        # Migraciones de la base de datos
│   ├── static/            # CSS, imágenes
│   └── Templates/         # Plantillas HTML
├── iniciar_red.ps1        # Script de arranque en red (PowerShell)
├── manage.py
├── db.sqlite3             # Base de datos SQLite
└── .env                   # Variables de entorno (credenciales de email)
```

---

## ✨ Funcionalidades

### Autenticación y seguridad
- **Registro** de usuarios con validación de email único.
- **Inicio de sesión en dos pasos (2FA)**: primero usuario + contraseña y luego un **código de 6
  dígitos enviado por email** (vence a los 10 minutos, máximo 5 intentos y reenvío limitado a 60 s).
- **Recuperación de contraseña** por email con enlaces temporales (valen 1 hora).

### Roles de usuario
- **Operador (cliente):** navega el catálogo, agrega productos al **carrito**, realiza compras y
  consulta **Mis Compras**.
- **Administrador:** no usa carrito ni "Mis compras". En su lugar tiene el **Historial de ventas**,
  ve todas las compras de todos los usuarios, y puede **crear, editar y eliminar** productos.

### Catálogo y compras
- Catálogo con **buscador** y **filtro por categoría**.
- Detalle de producto con productos relacionados.
- Carrito de compras (guardado en sesión) y **checkout** con validación.
- Métodos de pago: tarjeta de crédito, débito y transferencia.
- Al confirmar la compra se **descuenta el stock** de forma atómica y se genera un **código de venta**
  (`GS-XXXXXXXX`).
- Se envía un **comprobante de compra por email** al usuario.

### Panel de administración
- Historial de ventas **agrupado por usuario**, con total gastado y cantidad de compras.
- CRUD completo de productos desde la propia tienda.
- Admin de Django disponible en `/admin/`.

---

## 🗂️ Modelos

| Modelo | Descripción |
|---|---|
| **Perfil** | Extiende al `User` de Django con el rol: `admin` u `operador`. |
| **Producto** | Nombre, descripción, precio, stock, categoría, imagen, peso y estado (`activo`). |
| **Venta** | Compra de un usuario: total, método de pago, estado y código único. |
| **DetalleVenta** | Ítems de cada venta: producto, cantidad, precio unitario y subtotal. |

### Categorías de productos
Informática, Componente PC, Periféricos y Gaming, Redes y Conectividad, Celulares y Accesorios,
Cables y Adaptadores, Electrónica y Desarrollo, Seguridad y Domótica, Lectores de Tarjetas y Otros.

---

## ⚙️ Requisitos previos

- Python 3 instalado.
- Django instalado:
  ```powershell
  pip install django
  ```
- Una cuenta de Gmail (o servidor SMTP) para el envío de correos.

---

## 🔧 Configuración

Las credenciales de correo se leen desde un archivo `.env` en la raíz del proyecto (no se sube al
repositorio). Ejemplo de contenido:

```env
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=true
EMAIL_HOST_USER=tu-correo@gmail.com
EMAIL_HOST_PASSWORD=tu-clave-de-aplicacion
DEFAULT_FROM_EMAIL=AmpereStore <tu-correo@gmail.com>
```

> Para Gmail se recomienda usar una **contraseña de aplicación**, no la contraseña normal.

---

## 🛠️ Puesta en marcha (primera vez)

```powershell
# 1. Aplicar las migraciones
python manage.py migrate

# 2. (Opcional) Crear un superusuario de Django
python manage.py createsuperuser
```

Luego iniciar el servidor con el script de red (ver más arriba) o con `python manage.py runserver`.

---

## 🧪 Tests

```powershell
python manage.py test Tienda
```

---

## 🔗 Rutas principales

| Ruta | Descripción | Acceso |
|---|---|---|
| `/` | Inicio | Autenticado |
| `/login/` | Inicio de sesión | Público |
| `/registro/` | Registro de usuario | Público |
| `/productos/` | Catálogo de productos | Autenticado |
| `/carrito/` | Carrito de compras | Operador |
| `/mis-compras/` | Historial de compras propias | Operador |
| `/ventas/` | Historial de todas las ventas | Admin |
| `/admin/` | Panel de administración de Django | Admin |

---

## 📌 Nota

El proyecto es una **demo**, por lo que `DEBUG` está en `True` y el `ALLOWED_HOSTS` se ajusta según
la IP indicada al ejecutar `iniciar_red.ps1`. Para producción habría que configurar variables de
entorno, un servidor SMTP propio y una base de datos más robusta.
