from enum import Enum

from fastapi import APIRouter, Depends
from decimal import Decimal
from pydantic import BaseModel, Field
from typing import List
from shared.dependencies import get_db
from sqlalchemy.orm import Session
from contas_a_pagar_e_receber.models.contas_a_pagar_e_receber_model import ContasPagarReceber

# Cria um router específico para as operações relacionadas
# às contas a pagar e a receber
router = APIRouter(
    prefix="/contas-a-pagar-e-receber", 
    tags=["Contas a Pagar e Receber"]
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
):

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
    db: Session = Depends(get_db) -> ContaPagarReceberResponse
):

    conta_a_pagar_e_receber: ContasPagarReceber = db.query(ContasPagarReceber).get(id_da_conta_a_pagar_e_receber)
    conta_a_pagar_e_receber.tipo = conta_a_pagar_e_receber_request.tipo
    conta_a_pagar_e_receber.valor = conta_a_pagar_e_receber_request.valor
    conta_a_pagar_e_receber.descricao = conta_a_pagar_e_receber_request.descricao

    db.add(conta_a_pagar_e_receber)
    db.commit()
    db.refresh(conta_a_pagar_e_receber)
    return conta_a_pagar_e_receber
