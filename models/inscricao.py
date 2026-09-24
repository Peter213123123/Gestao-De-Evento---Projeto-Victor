from sqlalchemy import Column, Integer, String, ForeignKey
from models.base import Base

class Inscricao(Base):
    __tablename__ = "inscricoes"

    id = Column(Integer, primary_key=True, index=True)
    id_usuario = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    id_evento = Column(Integer, ForeignKey("eventos.id"), nullable=False)
    status = Column(String, default="ativa") # ativa ou cancelada