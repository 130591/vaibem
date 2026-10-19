from sqlalchemy import MetaData
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
  """Base declarativa compartilhada por todos os models do domínio."""

  metadata = MetaData(schema="vaibem")