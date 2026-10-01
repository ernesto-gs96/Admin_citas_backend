from fastapi import FastAPI, Depends
from app.core.users import fastapi_users, current_active_user
from app.core.security import auth_backend
from app.schemas.user import UserRead, UserCreate, UserUpdate
from app.models.user import User
from contextlib import asynccontextmanager
from app.db.database import engine, Base

# Esta función se ejecuta justo antes de que el servidor empiece a recibir peticiones
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Conectarse a Neon y crear todas las tablas definidas en los modelos
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield

# Añadimos el lifespan a la aplicación
app = FastAPI(title="SaaS Citas API", lifespan=lifespan)

# 1. Rutas de Login / Logout
app.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix="/api/auth/jwt",
    tags=["auth"]
)

# 2. Rutas de Registro
app.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/api/auth",
    tags=["auth"],
)

# 3. Rutas de reseteo de contraseña (olvidé mi contraseña)
app.include_router(
    fastapi_users.get_reset_password_router(),
    prefix="/api/auth",
    tags=["auth"],
)

# EJEMPLO: Una ruta privada para probar
@app.get("/api/ruta-secreta", tags=["Privado"])
async def ruta_protegida(user: User = Depends(current_active_user)):
    return {"mensaje": f"Hola {user.email}, estás autenticado y tu ID es {user.id}"}