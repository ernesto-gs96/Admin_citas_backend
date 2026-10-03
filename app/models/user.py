from fastapi import Depends
from fastapi_users.db import SQLAlchemyBaseUserTableUUID, SQLAlchemyUserDatabase
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import Base, get_async_session

# 1. El modelo para la base de datos (hereda de Base y de la clase de FastAPI Users)
class User(SQLAlchemyBaseUserTableUUID, Base):
    pass
    # Aquí puedes añadir más columnas en el futuro, ej:
    # name = Column(String, nullable=True)

# 2. Adaptador para que FastAPI Users sepa cómo hablar con tu base de datos
async def get_user_db(session: AsyncSession = Depends(get_async_session)):
    yield SQLAlchemyUserDatabase(session, User)