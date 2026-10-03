from app.core.config import settings
from fastapi_users.authentication import AuthenticationBackend, BearerTransport, JWTStrategy

SECRET = settings.SECRET

# Usaremos un token Bearer (que Next.js enviará en la cabecera Authorization)
bearer_transport = BearerTransport(tokenUrl="api/auth/jwt/login")

def get_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(secret=SECRET, lifetime_seconds=3600) # Token dura 1 hora

# Empaquetamos la configuración
auth_backend = AuthenticationBackend(
    name="jwt",
    transport=bearer_transport,
    get_strategy=get_jwt_strategy,
)