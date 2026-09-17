from typing import List

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from contas_a_pagar_e_receber.models.fornecedor_cliente_model import FornecedorCliente
from shared.dependencies import get_db
from shared.exceptions import NotFound

# Cria um router específico para as operações relacionadas
# às contas a pagar e a receber
router = APIRouter(
    prefix="/fornecedor-cliente"
)

# ============================================================
# MODELOS DE DADOS DA API
# ============================================================

# Modelo usado para definir o formato dos dados que a API
# irá DEVOLVER ao cliente.

# O id faz parte da resposta porque ele é gerado pelo banco
# de dados quando uma nova conta é criada.

# Definir objeto FornecedorCliente (Response) para representar o fornecedor ou cliente
# Objeto de resposta
class FornecedorClienteResponse(BaseModel):
    id: int
    nome: str

    # Permite que o Pydantic receba diretamente um objeto
    # do SQLAlchemy (ORM) e o transforme em uma resposta.
    # Assim, podemos retornar o objeto ContasPagarReceber
    # diretamente, sem precisar criar manualmente um
    # ContaPagarReceberResponse.
    class Config:
        orm_mode = True  # Permite que o Pydantic converta objetos ORM em dicionários

# Modelo usado para definir os dados que a API espera
# RECEBER do cliente ao criar uma nova conta.

# O id não é informado pelo cliente porque ele será
# gerado automaticamente pelo banco de dados.

# Definir objeto FornecedorCliente (Request) para receber os dados do fornecedor ou cliente
# Objeto de requisição
class FornecedorClienteRequest(BaseModel):
    # Não tem o id

    # Entre 3 e 30 caracteres
    nome: str = Field(min_length=3, max_length=255)

# CRUD: Create, Read, Update e Delete

# ============================================================
# ROTAS
# ============================================================

# GET /fornecedor-cliente

# Retorna todos os fornecedores e clientes cadastrados no banco de dados.

# response_model define o formato esperado da resposta:
# uma lista de objetos FornecedorClienteResponse.

# Se tiver "/" no final, o FastAPI entende que sempre precisa ter o "/" no final da rota,
# caso contrário, não precisa do "/"
# Método idempotente: mesmo pedido sempre retorna o mesmo resultado
@router.get("", response_model=List[FornecedorClienteResponse])
def listar_fornecedor_cliente(
    db: Session = Depends(get_db)
)-> List[FornecedorClienteResponse]:

    # Consulta a tabela FornecedorCliente e retorna
    # todas as contas cadastradas.
    return db.query(FornecedorCliente).all()

# Recuperar apenas um recurso
@router.get(
    "/{id_do_fornecedor_cliente}", 
    response_model=FornecedorClienteResponse
)
def obter_fornecedor_cliente_por_id(
    id_do_fornecedor_cliente: int,
    db: Session = Depends(get_db)
)-> List[FornecedorClienteResponse]:

    # Consulta a tabela FornecedorCliente e retorna
    # todas as contas cadastradas.
   
    return busca_fornecedor_cliente_por_id(id_do_fornecedor_cliente, db)

# POST /fornecedor-cliente

# Cria uma nova conta no banco de dados.

# status_code=201 indica que um novo recurso foi criado
# com sucesso.

# Na maioria dos métodos POST
# Se retorna algo

# Não é um método idempotente,
# Ou seja, mesmo pedido retorna respostas diferentes
# Já que cada pedido cria um item novo 
@router.post(
    "", 
    response_model=FornecedorClienteResponse, 
    status_code=201
)

def criar_fornecedor_cliente(
    fornecedor_cliente_request: FornecedorClienteRequest, 
    db: Session = Depends(get_db)
) -> FornecedorClienteResponse:

    # Lógica para salvar o fornecedor ou cliente no banco de dados

    # Converte os dados recebidos pela API (Pydantic)
    # em um objeto do modelo do SQLAlchemy.
    # O ** desempacota os campos do request para que eles
    # sejam passados como argumentos do modelo.
    fornecedor_cliente = FornecedorCliente(
        **fornecedor_cliente_request.dict()
    )

    # Adiciona o objeto à sessão do SQLAlchemy.
    # Neste momento, ele ainda não foi efetivamente
    # gravado no banco de dados.
    db.add(fornecedor_cliente)

    # Confirma a transação e grava a nova conta no banco.
    # Como a sessão não utiliza autocommit, o commit precisa
    # ser realizado explicitamente.
    db.commit()
    
    # Atualiza o objeto com os dados gerados pelo banco.
        # Por exemplo, o banco pode gerar automaticamente o id.
        # O refresh faz com que esse id seja carregado no objeto.a
    db.refresh(fornecedor_cliente)

    # Retorna a conta criada.
    # Graças ao orm_mode, o FastAPI/Pydantic consegue
    # transformar o objeto do SQLAlchemy em uma resposta
    # no formato definido por FornecedorClienteResponse.    
    return fornecedor_cliente

# No método PUT, passa o ID também
# O método PUT substitui todo o conteúdo do id atualizado
# É idempotente
# Observação: caso queira substituir parcialmente o conteúdo.
# O método correto é PATCH
@router.put(
    "/{id_do_fornecedor_cliente}", 
    response_model=FornecedorClienteResponse, 
    status_code=200
)

def atualizar_fornecedor_cliente(
    id_do_fornecedor_cliente: int, 
    fornecedor_cliente_request: FornecedorClienteRequest, 
    db: Session = Depends(get_db)
) -> FornecedorClienteResponse:

    fornecedor_cliente = busca_fornecedor_cliente_por_id(id_do_fornecedor_cliente, db)
    fornecedor_cliente.nome = fornecedor_cliente_request.nome


    db.add(fornecedor_cliente)
    db.commit()
    db.refresh(fornecedor_cliente)
    return fornecedor_cliente

# No método DELETE, não há response model
# Também precisa passar o id
# É idempotente
@router.delete(
    "/{id_do_fornecedor_cliente}", 
    status_code=204
)

def excluir_fornecedor_cliente(
    id_do_fornecedor_cliente: int, 
    db: Session = Depends(get_db)
) -> None:

    fornecedor_cliente = busca_fornecedor_cliente_por_id(id_do_fornecedor_cliente, db)
    db.delete(fornecedor_cliente)

    db.commit()

# RESUMO:
# GET: recuperar dados
# POST: criar novos recursos
# PUT: atualizações completas
# PATCH: atualizações parciais
# DELETE: remover recursos
# OUTRAS OPERAÇÕES: HEAD (recupera apenas cabeçalhos), OPTIONS (descreve opções de comunicação para um recurso)
# Dica de consulta: guia belgium bank rest API github

def busca_fornecedor_cliente_por_id(
    id_do_fornecedor_cliente: int, 
    db: Session
) -> FornecedorCliente:
    fornecedor_cliente: FornecedorCliente = db.query(FornecedorCliente).get(id_do_fornecedor_cliente)

    if fornecedor_cliente is None:
        raise NotFound("Fornecedor Cliente")
    
    return fornecedor_cliente