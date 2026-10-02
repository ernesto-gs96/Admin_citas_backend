from fastapi import FastAPI, Depends
from app.core.users import fastapi_users, current_active_user, current_verified_user
from app.core.security import auth_backend
from app.schemas.user import UserRead, UserCreate, UserUpdate
from app.models.user import User
from contextlib import asynccontextmanager
from app.db.database import engine, Base

# Esta función se ejecuta justo antes de que el servidor empiece a recibir peticiones
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Conectarse a la BD y crear todas las tablas definidas en los modelos si no existen
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield

# Añadimos el lifespan a la aplicación
app = FastAPI(title="SaaS Citas API", lifespan=lifespan)

# 1. Rutas de Login / Logout
# requires_verification=True: Impide iniciar sesión a usuarios que no hayan verificado su correo
app.include_router(
    fastapi_users.get_auth_router(auth_backend, requires_verification=True),
    prefix="/api/auth/jwt",
    tags=["auth"]
)

# 2. Rutas de Registro (dispara automáticamente el envío de correo de verificación)
app.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/api/auth",
    tags=["auth"],
)

# 3. Rutas de reseteo de contraseña (/forgot-password y /reset-password)
app.include_router(
    fastapi_users.get_reset_password_router(),
    prefix="/api/auth",
    tags=["auth"],
)

# 4. Rutas de verificación de correo (/request-verify-token y /verify)
app.include_router(
    fastapi_users.get_verify_router(UserRead),
    prefix="/api/auth",
    tags=["auth"],
)

# EJEMPLO: Rutas privadas protegidas (requieren usuario autenticado, activo y verificado)
@app.get("/api/ruta-secreta", tags=["Privado"])
async def ruta_protegida(user: User = Depends(current_active_user)):
    return {
        "mensaje": f"Hola {user.email}, estás autenticado y tu correo está verificado.",
        "user_id": str(user.id),
        "is_verified": user.is_verified,
    }

@app.get("/api/ruta-solo-verificados", tags=["Privado"])
async def ruta_solo_verificados(user: User = Depends(current_verified_user)):
    return {
        "mensaje": f"Hola {user.email}, tu correo está verificado y tienes acceso completo.",
        "is_verified": user.is_verified,
    }