from sqlalchemy import Column, Integer, String, Numeric
from sqlalchemy.orm import relationship

from shared.database import Base


class FornecedorCliente(Base):
    __tablename__ = "fornecedores_clientes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    nome = Column(String[255])

    