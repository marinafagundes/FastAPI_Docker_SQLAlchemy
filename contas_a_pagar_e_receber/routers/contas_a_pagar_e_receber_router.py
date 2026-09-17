from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import extract
from sqlalchemy.orm import Session

from contas_a_pagar_e_receber.models.contas_a_pagar_e_receber_model import ContasPagarReceber
from contas_a_pagar_e_receber.models.fornecedor_cliente_model import FornecedorCliente
from contas_a_pagar_e_receber.routers.fornecedor_cliente_router import FornecedorClienteResponse
from shared.dependencies import get_db
from shared.exceptions import NotFound

# Cria um router específico para as operações relacionadas
# às contas a pagar e a receber
router = APIRouter(
    prefix="/contas-a-pagar-e-receber"
)

# ============================================================
# MODELOS DE DADOS DA API
# ============================================================

# Modelo usado para definir o formato dos dados que a API
# irá DEVOLVER ao cliente.

# O id faz parte da resposta porque ele é gerado pelo banco
# de dados quando uma nova conta é criada.

# Definir objeto Contas (Response) para representar a conta a pagar ou receber
# Objeto de resposta
class ContaPagarReceberResponse(BaseModel):
    id: int
    descricao: str
    valor: Decimal
    tipo: str  # "PAGAR" ou "RECEBER"
    data_baixa = datetime | None = None  # Data de baixa da conta
    valor_baixa = Decimal | None = None
    esta_baixada = bool | None = None
    fornecedor: FornecedorClienteResponse | None = None  

    # Permite que o Pydantic receba diretamente um objeto
    # do SQLAlchemy (ORM) e o transforme em uma resposta.
    # Assim, podemos retornar o objeto ContasPagarReceber
    # diretamente, sem precisar criar manualmente um
    # ContaPagarReceberResponse.
    class Config:
        orm_mode = True  # Permite que o Pydantic converta objetos ORM em dicionários

class ContaPagarReceberTipoEnum(str,Enum):
    PAGAR = "PAGAR"
    RECEBER = "RECEBER"

# Modelo usado para definir os dados que a API espera
# RECEBER do cliente ao criar uma nova conta.

# O id não é informado pelo cliente porque ele será
# gerado automaticamente pelo banco de dados.

# Definir objeto Contas (Request) para receber os dados da conta a pagar ou receber
# Objeto de requisição
class ContaPagarReceberRequest(BaseModel):
    # Não tem o id

    # Entre 3 e 30 caracteres
    descricao: str = Field(min_length=3, max_length=30)

    # Valor maior do que 0
    valor: Decimal = Field(gt=0)

    # Cria o tipo específico ENUM 
    # Para permitir apenas PAGAR ou RECEBER
    tipo: ContaPagarReceberTipoEnum

    # Id do Fornecedor ou Cliente associado à conta
    fornecedor_cliente_id: int | None = None

# ============================================================
# ROTAS
# ============================================================

# GET /contas-a-pagar-e-receber

# Retorna todas as contas cadastradas no banco de dados.

# response_model define o formato esperado da resposta:
# uma lista de objetos ContaPagarReceberResponse.

# Se tiver "/" no final, o FastAPI entende que sempre precisa ter o "/" no final da rota,
# caso contrário, não precisa do "/"
@router.get("", response_model=List[ContaPagarReceberResponse])
def listar_contas(
    db: Session = Depends(get_db)
)-> List[ContaPagarReceberResponse]:

    # Consulta a tabela ContasPagarReceber e retorna
    # todas as contas cadastradas.
    return db.query(ContasPagarReceber).all()

@router.get("/{id_da_conta_a_pagar_e_receber}", response_model=ContaPagarReceberResponse)

def obter_conta_por_id(id_da_conta_a_pagar_e_receber: int,
                       db: Session = Depends(get_db)) -> List[ContaPagarReceberResponse]:
    return busca_conta_por_id(id_da_conta_a_pagar_e_receber, db)


# POST /contas-a-pagar-e-receber

# Cria uma nova conta no banco de dados.

# status_code=201 indica que um novo recurso foi criado
# com sucesso.

# Na maioria dos métodos POST
# Se retorna algo
@router.post(
    "", 
    response_model=ContaPagarReceberResponse, 
    status_code=201
)

def criar_conta(
    conta_a_pagar_e_receber_request: ContaPagarReceberRequest, 
    db: Session = Depends(get_db)
) -> ContaPagarReceberResponse:

    valida_fornecedor(conta_a_pagar_e_receber_request.fornecedor_cliente_id, db)

    # Lógica para salvar a conta no banco de dados

    # Converte os dados recebidos pela API (Pydantic)
    # em um objeto do modelo do SQLAlchemy.
    # O ** desempacota os campos do request para que eles
    # sejam passados como argumentos do modelo.
    contas_a_pagar_e_receber = ContasPagarReceber(
        **conta_a_pagar_e_receber_request.dict()
    )

    # Adiciona o objeto à sessão do SQLAlchemy.
    # Neste momento, ele ainda não foi efetivamente
    # gravado no banco de dados.
    db.add(contas_a_pagar_e_receber)

    # Confirma a transação e grava a nova conta no banco.
    # Como a sessão não utiliza autocommit, o commit precisa
    # ser realizado explicitamente.
    db.commit()
    
    # Atualiza o objeto com os dados gerados pelo banco.
        # Por exemplo, o banco pode gerar automaticamente o id.
        # O refresh faz com que esse id seja carregado no objeto.a
    db.refresh(contas_a_pagar_e_receber)

    # Retorna a conta criada.
    # Graças ao orm_mode, o FastAPI/Pydantic consegue
    # transformar o objeto do SQLAlchemy em uma resposta
    # no formato definido por ContaPagarReceberResponse.    
    return contas_a_pagar_e_receber

# CRUD: Create, Read, Update e Delete

# Na maioria dos métodos POST
# Se retorna algo
@router.put(
    "/{id_da_conta_a_pagar_e_receber}", 
    response_model=ContaPagarReceberResponse, 
    status_code=200
)

# Acrescenta o id da conta
def atualizar_conta(
    id_da_conta_a_pagar_e_receber: int, 
    conta_a_pagar_e_receber_request: ContaPagarReceberRequest, 
    db: Session = Depends(get_db)
) -> ContaPagarReceberResponse:

    valida_fornecedor(conta_a_pagar_e_receber_request.fornecedor_cliente_id, db)

    conta_a_pagar_e_receber = busca_conta_por_id(id_da_conta_a_pagar_e_receber, db)
    conta_a_pagar_e_receber.tipo = conta_a_pagar_e_receber_request.tipo
    conta_a_pagar_e_receber.valor = conta_a_pagar_e_receber_request.valor
    conta_a_pagar_e_receber.descricao = conta_a_pagar_e_receber_request.descricao
    conta_a_pagar_e_receber.fornecedor_cliente_id = conta_a_pagar_e_receber_request.fornecedor_cliente_id

    db.add(conta_a_pagar_e_receber)
    db.commit()
    db.refresh(conta_a_pagar_e_receber)
    return conta_a_pagar_e_receber

@router.post(
    "/{id_da_conta_a_pagar_e_receber}/baixar", 
    response_model=ContaPagarReceberResponse, 
    status_code=200
)

# Acrescenta o id da conta
def baixar_conta(
    id_da_conta_a_pagar_e_receber: int, 
    db: Session = Depends(get_db)
) -> ContaPagarReceberResponse:
    
    conta_a_pagar_e_receber = busca_conta_por_id(id_da_conta_a_pagar_e_receber, db)

    if (conta_a_pagar_e_receber.esta_baixada and conta_a_pagar_e_receber.valor != conta_a_pagar_e_receber.valor_baixa):
        return conta_a_pagar_e_receber
    
    conta_a_pagar_e_receber.data_baixa = datetime.now()
    conta_a_pagar_e_receber.esta_baixada = True
    conta_a_pagar_e_receber.valor_baixa = conta_a_pagar_e_receber.valor

    db.add(conta_a_pagar_e_receber)
    db.commit()
    db.refresh(conta_a_pagar_e_receber)

    return conta_a_pagar_e_receber

@router.delete(
    "/{id_da_conta_a_pagar_e_receber}",
    status_code=204
)

def excluir_conta(
    id_da_conta_a_pagar_e_receber: int,
    db: Session = Depends(get_db)
) -> None:
    
    conta_a_pagar_e_receber = busca_conta_por_id(id_da_conta_a_pagar_e_receber, db)

    db.delete(conta_a_pagar_e_receber)
    db.commit()

def busca_conta_por_id(
    id_da_conta_a_pagar_e_receber: int, 
    db: Session
) -> ContasPagarReceber:
    
    conta_a_pagar_e_receber = db.query(ContasPagarReceber).get(id_da_conta_a_pagar_e_receber)

    if conta_a_pagar_e_receber is None:
        raise NotFound("Conta a Pagar e Receber")

    return conta_a_pagar_e_receber

def valida_fornecedor(fornecedor_cliente_id, db):
    if fornecedor_cliente_id is not None:
        conta_a_pagar_e_receber = db.query(FornecedorCliente).get(fornecedor_cliente_id)
        if conta_a_pagar_e_receber is None:
            raise HTTPException(
                status_code = 422, 
                detail = "Esse fornecedor não existe no banco de dados"
            )
