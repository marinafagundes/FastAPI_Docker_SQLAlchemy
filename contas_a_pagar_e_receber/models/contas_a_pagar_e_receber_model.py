from sqlalchemy import Boolean, Column, Date, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import relationship

from shared.database import Base

class ContasPagarReceber(Base):
    __tablename__ = "contas_a_pagar_e_receber"

    id = Column(Integer, primary_key=True, autoincrement=True)
    descricao = Column(String(30), nullable=False)
    valor = Column(Numeric(10, 2), nullable=False)
    tipo = Column(String(10), nullable=False)
    data_previsao = Column(Date, nullable=False)
    data_baixa = Column(Date, nullable=True)
    valor_baixa = Column(Numeric(10, 2), nullable=True)
    esta_baixada = Column(Boolean, nullable=False, default=False)

    # A conta pode existir sem um fornecedor/cliente associado.
    fornecedor_cliente_id = Column(
        Integer,
        ForeignKey("fornecedor_cliente.id"),
        nullable=True,
    )
    fornecedor = relationship(
        "FornecedorCliente",
        back_populates="contas",
    )
