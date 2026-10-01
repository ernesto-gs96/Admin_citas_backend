import os
from dotenv import load_dotenv
from fastapi_users.authentication import AuthenticationBackend, BearerTransport, JWTStrategy

# Esto busca el archivo .env e inserta las variables en la memoria
load_dotenv() 

SECRET = os.getenv("SECRET") # Debería venir de tu archivo .env

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