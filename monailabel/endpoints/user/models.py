from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship
from monailabel.database import Base

# class Scope(Base):
#     __tablename__ = 'scope'
#     id = Column(Integer, primary_key=True, index=True)
#     scope = Column(String, unique=True, index=True)
#     users = relationship("User", back_populates="scope")

class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    full_name = Column(String, index=True)
    disabled = Column(Boolean, default=True)
    # scopes = relationship("Scope", back_populates="user")