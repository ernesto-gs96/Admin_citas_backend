import logging
import uuid
from typing import Optional
from fastapi import Depends, Request
from fastapi_users import BaseUserManager, FastAPIUsers, UUIDIDMixin, exceptions

from app.models.user import User, get_user_db
from app.core.security import auth_backend, SECRET
from app.services.email import send_verification_email, send_reset_password_email

logger = logging.getLogger("app.users")

class UserManager(UUIDIDMixin, BaseUserManager[User, uuid.UUID]):
    reset_password_token_secret = SECRET
    verification_token_secret = SECRET
    reset_password_token_lifetime_seconds = 3600    # 1 hora de validez
    verification_token_lifetime_seconds = 86400    # 24 horas de validez

    async def on_after_register(self, user: User, request: Optional[Request] = None):
        """
        Se ejecuta automáticamente cuando un nuevo usuario se registra.
        Dispara la solicitud de verificación para enviar el correo con el token.
        """
        logger.info(f"¡Nuevo usuario registrado! Email: {user.email}")
        try:
            await self.request_verify(user, request)
        except exceptions.UserAlreadyVerified:
            logger.info(f"El usuario {user.email} ya estaba verificado.")
        except Exception as e:
            logger.error(f"Error al solicitar verificación automática para {user.email}: {e}")

    async def on_after_request_verify(
        self, user: User, token: str, request: Optional[Request] = None
    ):
        """
        Se ejecuta al solicitar la verificación (tanto tras el registro como por solicitud manual).
        Envía el correo de verificación vía SMTP de Gmail.
        """
        logger.info(f"Enviando correo de verificación a {user.email}...")
        await send_verification_email(user.email, token)

    async def on_after_verify(self, user: User, request: Optional[Request] = None):
        """
        Se ejecuta cuando el usuario verifica exitosamente su correo electrónico.
        """
        logger.info(f"¡El usuario {user.email} ha verificado su cuenta exitosamente!")

    async def on_after_forgot_password(
        self, user: User, token: str, request: Optional[Request] = None
    ):
        """
        Se ejecuta cuando un usuario solicita recuperar su contraseña.
        Envía el correo con el enlace y token de recuperación.
        """
        logger.info(f"Enviando correo de recuperación de contraseña a {user.email}...")
        await send_reset_password_email(user.email, token)

    async def on_after_reset_password(
        self, user: User, request: Optional[Request] = None
    ):
        """
        Se ejecuta cuando la contraseña ha sido actualizada exitosamente.
        """
        logger.info(f"¡El usuario {user.email} ha restablecido su contraseña exitosamente!")

async def get_user_manager(user_db=Depends(get_user_db)):
    yield UserManager(user_db)

# ¡La instancia principal de FastAPI Users!
fastapi_users = FastAPIUsers[User, uuid.UUID](
    get_user_manager,
    [auth_backend],
)

# Dependencia para proteger rutas: sólo usuarios activos
current_active_user = fastapi_users.current_user(active=True)

# Dependencia para proteger rutas que exigen además que el correo esté verificado
current_verified_user = fastapi_users.current_user(active=True, verified=True)