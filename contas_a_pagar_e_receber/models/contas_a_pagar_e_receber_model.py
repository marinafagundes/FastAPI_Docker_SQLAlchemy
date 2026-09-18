from sqlalchemy import Boolean, Column, Date, ForeignKey, Integer, String, Numeric
from sqlalchemy.orm import relationship

from shared.database import Base


class ContasPagarReceber(Base):
    __tablename__ = "contas_a_pagar_e_receber"

    id = Column(Integer, primary_key=True, autoincrement=True)
    descricao = Column(String[30])
    valor = Column(Numeric(10, 2))
    tipo = Column(String[30])  # "PAGAR" ou "RECEBER"
    data_previsao = Column(Date(), nullable=False)  # Data de previsão 
    data_baixa = Column(Date())  # Data de baixa da conta
    valor_baixa = Column(Numeric())
    esta_baixada = Column(Boolean, default=False)
    
    # Um cliente ou fornecedor pode ter várias contas a pagar ou a receber, mas cada conta pertence a apenas um cliente ou fornecedor.
    fornecedor_cliente_id = Column(Integer, ForeignKey("fornecedor_cliente.id"), nullable=False)
    fornecedor = relationship("FornecedorCliente")

