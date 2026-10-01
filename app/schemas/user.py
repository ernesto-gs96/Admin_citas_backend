import uuid
from fastapi_users import schemas

class UserRead(schemas.BaseUser[uuid.UUID]):
    pass
    # Si agregaste 'name' al modelo de BD, ponlo aquí también

class UserCreate(schemas.BaseUserCreate):
    pass

class UserUpdate(schemas.BaseUserUpdate):
    pass