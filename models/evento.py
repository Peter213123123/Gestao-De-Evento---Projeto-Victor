from sqlalchemy import Column, Integer, String, Date
from models.base import Base

class Evento(Base):
    __tablename__ = "eventos"

    id = Column(Integer, primary_key=True, index=True)
    titulo = Column(String, index=True, nullable=False)
    descricao = Column(String)
    data_evento = Column(Date, nullable=False)
    capacidade = Column(Integer, nullable=False)