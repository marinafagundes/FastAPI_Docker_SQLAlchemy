from datetime import date
from decimal import Decimal
from enum import Enum
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import extract
from sqlalchemy.orm import Session

from contas_a_pagar_e_receber.models.contas_a_pagar_e_receber_model import ContasPagarReceber
from contas_a_pagar_e_receber.models.fornecedor_cliente_model import FornecedorCliente
from contas_a_pagar_e_receber.routers.fornecedor_cliente_router import FornecedorClienteResponse
from shared.dependencies import get_db
from shared.exceptions import NotFound

router = APIRouter(prefix="/contas-a-pagar-e-receber", tags=["Contas"])
QUANTIDADE_PERMITIDA_POR_MES = 100

class ContaPagarReceberTipoEnum(str, Enum):
    PAGAR = "PAGAR"
    RECEBER = "RECEBER"

class ContaPagarReceberResponse(BaseModel):
    id: int
    descricao: str
    valor: Decimal
    tipo: ContaPagarReceberTipoEnum
    data_previsao: date
    data_baixa: date | None = None
    valor_baixa: Decimal | None = None
    esta_baixada: bool
    fornecedor: FornecedorClienteResponse | None = None

    model_config = ConfigDict(from_attributes=True)

class ContaPagarReceberRequest(BaseModel):
    descricao: str = Field(min_length=3, max_length=30)
    valor: Decimal = Field(gt=0)
    tipo: ContaPagarReceberTipoEnum
    fornecedor_cliente_id: int | None = None
    data_previsao: date

class PrevisaoPorMes(BaseModel):
    mes: int
    valor_total: Decimal

@router.get("", response_model=List[ContaPagarReceberResponse])
def listar_contas(db: Session = Depends(get_db)):
    return db.query(ContasPagarReceber).order_by(ContasPagarReceber.id).all()

@router.get("/previsao-gastos-do-mes", response_model=List[PrevisaoPorMes])
def previsao_gastos_do_mes(
    ano: int = Query(default_factory=lambda: date.today().year),
    db: Session = Depends(get_db),
):
    return relatorio_gastos_previstos_por_mes_de_um_ano(db, ano)

@router.get("/{id_da_conta_a_pagar_e_receber}", response_model=ContaPagarReceberResponse)
def obter_conta_por_id(
    id_da_conta_a_pagar_e_receber: int,
    db: Session = Depends(get_db),
):
    return busca_conta_por_id(id_da_conta_a_pagar_e_receber, db)

@router.post("", response_model=ContaPagarReceberResponse, status_code=201)
def criar_conta(
    conta_a_pagar_e_receber_request: ContaPagarReceberRequest,
    db: Session = Depends(get_db),
):
    valida_fornecedor(conta_a_pagar_e_receber_request.fornecedor_cliente_id, db)
    valida_se_pode_registrar_novas_contas(conta_a_pagar_e_receber_request, db)

    conta = ContasPagarReceber(**conta_a_pagar_e_receber_request.model_dump())
    db.add(conta)
    db.commit()
    db.refresh(conta)
    return conta

@router.put("/{id_da_conta_a_pagar_e_receber}", response_model=ContaPagarReceberResponse)
def atualizar_conta(
    id_da_conta_a_pagar_e_receber: int,
    conta_a_pagar_e_receber_request: ContaPagarReceberRequest,
    db: Session = Depends(get_db),
):
    valida_fornecedor(conta_a_pagar_e_receber_request.fornecedor_cliente_id, db)

    conta = busca_conta_por_id(id_da_conta_a_pagar_e_receber, db)
    for campo, valor in conta_a_pagar_e_receber_request.model_dump().items():
        setattr(conta, campo, valor)

    # Se uma conta já baixada for alterada, a baixa deixa de representar
    # o novo valor até que a conta seja baixada novamente.
    if conta.esta_baixada:
        conta.data_baixa = None
        conta.valor_baixa = None
        conta.esta_baixada = False

    db.commit()
    db.refresh(conta)
    return conta

@router.post("/{id_da_conta_a_pagar_e_receber}/baixar", response_model=ContaPagarReceberResponse)
def baixar_conta(
    id_da_conta_a_pagar_e_receber: int,
    db: Session = Depends(get_db),
):
    conta = busca_conta_por_id(id_da_conta_a_pagar_e_receber, db)

    if conta.esta_baixada:
        return conta

    conta.data_baixa = date.today()
    conta.esta_baixada = True
    conta.valor_baixa = conta.valor

    db.commit()
    db.refresh(conta)
    return conta

@router.delete("/{id_da_conta_a_pagar_e_receber}", status_code=204)
def excluir_conta(
    id_da_conta_a_pagar_e_receber: int,
    db: Session = Depends(get_db),
) -> None:
    conta = busca_conta_por_id(id_da_conta_a_pagar_e_receber, db)
    db.delete(conta)
    db.commit()

def busca_conta_por_id(id_da_conta_a_pagar_e_receber: int, db: Session) -> ContasPagarReceber:
    conta = db.get(ContasPagarReceber, id_da_conta_a_pagar_e_receber)
    if conta is None:
        raise NotFound("Conta a Pagar e Receber")
    return conta

def valida_fornecedor(fornecedor_cliente_id: int | None, db: Session) -> None:
    if fornecedor_cliente_id is None:
        return
    fornecedor = db.get(FornecedorCliente, fornecedor_cliente_id)
    if fornecedor is None:
        raise HTTPException(status_code=422, detail="Esse fornecedor não existe no banco de dados")

def valida_se_pode_registrar_novas_contas(
    request: ContaPagarReceberRequest,
    db: Session,
) -> None:
    quantidade = recupera_numero_de_registros(
        db,
        request.data_previsao.year,
        request.data_previsao.month,
    )
    if quantidade >= QUANTIDADE_PERMITIDA_POR_MES:
        raise HTTPException(status_code=422, detail="Você não pode mais lançar contas para esse mês")

def recupera_numero_de_registros(db: Session, ano: int, mes: int) -> int:
    return (
        db.query(ContasPagarReceber)
        .filter(extract("year", ContasPagarReceber.data_previsao) == ano)
        .filter(extract("month", ContasPagarReceber.data_previsao) == mes)
        .count()
    )

def relatorio_gastos_previstos_por_mes_de_um_ano(db: Session, ano: int) -> List[PrevisaoPorMes]:
    contas = (
        db.query(ContasPagarReceber)
        .filter(extract("year", ContasPagarReceber.data_previsao) == ano)
        .filter(ContasPagarReceber.tipo == ContaPagarReceberTipoEnum.PAGAR.value)
        .order_by(ContasPagarReceber.data_previsao)
        .all()
    )

    valores_por_mes: dict[int, Decimal] = {}
    for conta in contas:
        mes = conta.data_previsao.month
        valores_por_mes[mes] = valores_por_mes.get(mes, Decimal("0")) + conta.valor

    return [PrevisaoPorMes(mes=mes, valor_total=valor) for mes, valor in valores_por_mes.items()]
