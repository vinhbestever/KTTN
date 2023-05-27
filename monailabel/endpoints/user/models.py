from sqlalchemy import Column, Integer, String, Boolean, types
from sqlalchemy.orm import relationship
from monailabel.database import Base

class ChoiceType(types.TypeDecorator):
    impl = types.String

    def __init__(self, choices, **kw):
        self.choices = dict(choices)
        super(ChoiceType, self).__init__(**kw)

    def process_bind_param(self, value, dialect):
        return [k for k, v in self.choices.items() if v == value][0]

    def process_result_value(self, value, dialect):
        return self.choices[value]

class User(Base):
    SCOPES = {
        "admin": "admin",
        "user": "user"
    }

    __tablename__ = 'user'
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    full_name = Column(String, index=True)
    disabled = Column(Boolean, default=True)
    scopes = Column(ChoiceType(SCOPES), default='user')
