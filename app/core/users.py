import uuid
from typing import Optional
from fastapi import Depends, Request
from fastapi_users import BaseUserManager, FastAPIUsers, UUIDIDMixin

from app.models.user import User, get_user_db
from app.core.security import auth_backend, SECRET

class UserManager(UUIDIDMixin, BaseUserManager[User, uuid.UUID]):
    reset_password_token_secret = SECRET
    verification_token_secret = SECRET

    # Puedes ejecutar código automático cuando alguien se registra
    async def on_after_register(self, user: User, request: Optional[Request] = None):
        print(f"¡Nuevo usuario registrado! Email: {user.email}")

    async def on_after_forgot_password(self, user: User, token: str, request: Optional[Request] = None):
        print(f"El usuario {user.email} solicitó recuperar contraseña. Token: {token}")
        # Aquí enviarías un email real usando SendGrid o Resend

async def get_user_manager(user_db=Depends(get_user_db)):
    yield UserManager(user_db)

# ¡La instancia principal de FastAPI Users!
fastapi_users = FastAPIUsers[User, uuid.UUID](
    get_user_manager,
    [auth_backend],
)

# Dependencia para proteger rutas (sólo usuarios logueados)
current_active_user = fastapi_users.current_user(active=True)