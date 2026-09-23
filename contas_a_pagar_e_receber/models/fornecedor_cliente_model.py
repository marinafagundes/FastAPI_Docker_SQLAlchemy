from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from shared.database import Base

class FornecedorCliente(Base):
    __tablename__ = "fornecedor_cliente"

    id = Column(Integer, primary_key=True, autoincrement=True)
    nome = Column(String(255), nullable=False)

    contas = relationship(
        "ContasPagarReceber",
        back_populates="fornecedor",
    )
