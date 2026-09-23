from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from contas_a_pagar_e_receber.models.contas_a_pagar_e_receber_model import ContasPagarReceber
from contas_a_pagar_e_receber.routers.contas_a_pagar_e_receber_router import ContaPagarReceberResponse
from shared.dependencies import get_db

router = APIRouter(prefix="/fornecedor-cliente", tags=["Fornecedor/Cliente"])

@router.get(
    "/{id_do_fornecedor_cliente}/contas-a-pagar-e-receber",
    response_model=List[ContaPagarReceberResponse],
)
def obter_contas_de_um_fornecedor_cliente_por_id(
    id_do_fornecedor_cliente: int,
    db: Session = Depends(get_db),
):
    return (
        db.query(ContasPagarReceber)
        .filter_by(fornecedor_cliente_id=id_do_fornecedor_cliente)
        .order_by(ContasPagarReceber.id)
        .all()
    )
