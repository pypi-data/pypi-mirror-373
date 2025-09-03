"""
Created on 15 Jul 2025

@author: ph1jb
"""

from models.base import Base
from sqlalchemy.sql.schema import Column
from sqlalchemy.sql.sqltypes import String, LargeBinary


class Cache(Base):
    __tablename__ = "cache"

    name = Column(String(255), primary_key=True)
    data = Column(LargeBinary)
