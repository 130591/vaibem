from apps.api.src.config import settings
from sqlalchemy.ext.asyncio import (
  AsyncSession,
  async_sessionmaker,
  create_async_engine,
)

engine = create_async_engine(
  settings.database_url,
  echo=settings.database_echo,
)


SessionLocal = async_sessionmaker(
  engine,
  class_=AsyncSession,
  expire_on_commit=False,
)