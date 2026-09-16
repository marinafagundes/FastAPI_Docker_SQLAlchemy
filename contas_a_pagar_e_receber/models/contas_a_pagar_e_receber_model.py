from sqlalchemy import Column, ForeignKey, Integer, String, Numeric
from sqlalchemy.orm import relationship

from shared.database import Base


class ContasPagarReceber(Base):
    __tablename__ = "contas_a_pagar_e_receber"

    id = Column(Integer, primary_key=True, autoincrement=True)
    descricao = Column(String[30])
    valor = Column(Numeric(10, 2))
    tipo = Column(String[30])  # "PAGAR" ou "RECEBER"

    # Um cliente ou fornecedor pode ter várias contas a pagar ou a receber, mas cada conta pertence a apenas um cliente ou fornecedor.
    fornecedor_cliente_id = Column(Integer, ForeignKey("fornecedores_clientes.id"), nullable=False)
    fornecedor = relationship("FornecedorCliente")

