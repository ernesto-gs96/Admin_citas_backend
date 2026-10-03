# Admin_citas_backend

Backend para el sistema de administración de citas con FastAPI, SQLAlchemy y FastAPI Users.

---

## 🚀 Inicio Rápido

### 1. Activar entorno virtual

En Windows (PowerShell):
```powershell
.venv\Scripts\activate
```

### 2. Configurar variables de entorno (`.env`)

Copia o edita el archivo `.env` en la raíz del proyecto:

```env
DATABASE_URL='postgresql+asyncpg://...'
SECRET='tu_secreto_super_seguro_jwt'

# Configuración SMTP Gmail
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=tu_correo@gmail.com
SMTP_PASSWORD=tu_contrasena_de_aplicacion_de_16_caracteres
SMTP_FROM_NAME="SaaS Citas"
SMTP_FROM_EMAIL=tu_correo@gmail.com
SMTP_TLS=True

# URL de tu frontend (Next.js) para los enlaces de correo
FRONTEND_URL=http://localhost:3000
```

> **🔑 ¿Cómo obtener la "Contraseña de aplicación" en Gmail?**
> 1. Ve a tu [Cuenta de Google](https://myaccount.google.com/).
> 2. En el menú lateral, selecciona **Seguridad**.
> 3. En la sección *Cómo inicias sesión en Google*, asegúrate de tener activada la **Verificación en 2 pasos**.
> 4. Busca **Contraseñas de aplicaciones** (o ingresa directamente en [google.com/apppasswords](https://myaccount.google.com/apppasswords)).
> 5. Crea una contraseña con el nombre "FastAPI Backend".
> 6. Google te mostrará un código de 16 letras (ej: `abcd efgh ijkl mnop`). Copia ese código sin espacios en `SMTP_PASSWORD`.

---

### 3. Probar envío de correo SMTP

Puedes verificar rápidamente que tu configuración de Gmail funciona ejecutando:

```bash
uv run python -m app.services.email tu_correo_personal@gmail.com
```

---

### 4. Ejecutar el servidor de desarrollo

```bash
uv run fastapi dev app/main.py
```

La documentación interactiva estará disponible en:
- Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)
- Redoc: [http://localhost:8000/redoc](http://localhost:8000/redoc)

---

## 📬 Endpoints de Autenticación y Correo

| Método | Endpoint | Descripción |
| :--- | :--- | :--- |
| `POST` | `/api/auth/register` | Registra un nuevo usuario y **envía automáticamente el correo de verificación**. |
| `POST` | `/api/auth/jwt/login` | Inicia sesión y devuelve el token Bearer JWT. |
| `POST` | `/api/auth/jwt/logout` | Cierra la sesión activa. |
| `POST` | `/api/auth/request-verify-token` | Solicita un nuevo correo con token de verificación. |
| `POST` | `/api/auth/verify` | Valida el token y marca la cuenta como `is_verified=True`. |
| `POST` | `/api/auth/forgot-password` | Solicita recuperación de contraseña (envía correo con token). |
| `POST` | `/api/auth/reset-password` | Restablece la contraseña utilizando el token recibido por correo. |
| `GET` | `/api/ruta-secreta` | Ruta protegida para cualquier usuario autenticado y activo. |
| `GET` | `/api/ruta-solo-verificados` | Ruta protegida que exige obligatoriamente que el usuario esté **verificado**. |