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
    STATUS = {
        "active": "active",
        "inactive": "inactive"
    }

    __tablename__ = 'project'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    description = Column(String, unique=True, index=True)
    workflow = Column(String, unique=True, index=True)
    status = Column(ChoiceType(STATUS), default='active')
