# API de Contas a Pagar e Receber

Projeto de estudos de uma API REST construída com **FastAPI**, **SQLAlchemy**, **Pydantic**, **Alembic**, **pytest** e suporte a **PostgreSQL/SQLite**.

## 1. Objetivo

A API permite:

- cadastrar clientes/fornecedores;
- cadastrar contas a pagar e a receber;
- consultar contas;
- atualizar e excluir contas;
- associar uma conta a um cliente/fornecedor;
- baixar uma conta;
- limitar a 100 contas por mês;
- gerar um relatório de gastos previstos por mês.

## 2. Arquitetura

```text
main.py
├── contas_a_pagar_e_receber/
│   ├── models/       # tabelas SQLAlchemy
│   └── routers/      # endpoints e schemas Pydantic
└── shared/
    ├── database.py   # engine, sessão e Base
    ├── dependencies.py
    └── exceptions*.py
```

Fluxo básico de uma requisição:

```text
Cliente HTTP
   ↓
FastAPI Router
   ↓
Pydantic valida os dados
   ↓
SQLAlchemy executa a operação
   ↓
Banco de dados
   ↓
Pydantic serializa a resposta
```

## 3. Requisitos

- Python 3.12+ (o projeto foi preparado para Python 3.14)
- pip
- PostgreSQL, se quiser estudar a integração com PostgreSQL
- Docker, opcional

## 4. Instalação local

```bash
python -m venv .venv
source .venv/bin/activate       # Linux/macOS
# .venv\Scripts\activate      # Windows

pip install -r requirements.txt
cp .env.example .env
```

Se não alterar o `.env`, a aplicação usa SQLite em `app.db`.

Para PostgreSQL, defina:

```env
SQLALCHEMY_DATABASE_URL=postgresql+psycopg2://usuario:senha@localhost:5432/nome_do_banco
```

## 5. Executar

```bash
uvicorn main:app --reload
```

Documentação interativa:

- `/docs` — Swagger UI
- `/redoc` — ReDoc

## 6. Principais endpoints

| Método | Endpoint | Finalidade |
|---|---|---|
| GET | `/` | Health check |
| GET | `/fornecedor-cliente` | Lista clientes/fornecedores |
| POST | `/fornecedor-cliente` | Cria cliente/fornecedor |
| GET | `/fornecedor-cliente/{id}` | Busca por ID |
| PUT | `/fornecedor-cliente/{id}` | Atualiza |
| DELETE | `/fornecedor-cliente/{id}` | Exclui |
| GET | `/contas-a-pagar-e-receber` | Lista contas |
| POST | `/contas-a-pagar-e-receber` | Cria conta |
| GET | `/contas-a-pagar-e-receber/{id}` | Busca conta |
| PUT | `/contas-a-pagar-e-receber/{id}` | Atualiza conta |
| DELETE | `/contas-a-pagar-e-receber/{id}` | Exclui conta |
| POST | `/contas-a-pagar-e-receber/{id}/baixar` | Efetua baixa |
| GET | `/contas-a-pagar-e-receber/previsao-gastos-do-mes?ano=2022` | Relatório anual |
| GET | `/fornecedor-cliente/{id}/contas-a-pagar-e-receber` | Contas de um cliente/fornecedor |

## 7. Conceitos para estudar

### FastAPI

- `APIRouter`: organiza endpoints por domínio.
- `Depends`: injeta dependências, como a sessão do banco.
- `response_model`: documenta e valida o formato da resposta.
- `HTTPException`: retorna erros HTTP controlados.
- OpenAPI: o FastAPI gera a documentação automaticamente.

### Pydantic

Existem dois modelos principais:

- **Request**: dados recebidos pela API.
- **Response**: dados devolvidos pela API.

Exemplo:

```python
class ContaPagarReceberRequest(BaseModel):
    descricao: str = Field(min_length=3, max_length=30)
    valor: Decimal = Field(gt=0)
    tipo: ContaPagarReceberTipoEnum
    data_previsao: date
```

Isso faz com que entradas inválidas sejam rejeitadas antes de chegar à lógica de negócio.

### SQLAlchemy

`Base` é a classe-base dos modelos ORM. Cada classe representa uma tabela.

A relação entre `FornecedorCliente` e `ContasPagarReceber` é:

```text
FornecedorCliente 1 ─────── N ContasPagarReceber
```

Uma conta pode existir sem fornecedor/cliente associado, por isso a chave estrangeira é opcional.

### CRUD

- **Create** → POST
- **Read** → GET
- **Update** → PUT
- **Delete** → DELETE

### Baixa

A baixa registra:

- `data_baixa`;
- `valor_baixa`;
- `esta_baixada`.

Se uma conta já baixada for alterada, a baixa é invalidada para evitar que o valor baixado fique diferente do valor atual.

### Regra de negócio

O sistema permite no máximo **100 contas por mês**, independentemente de serem contas a pagar ou receber.

## 8. Testes

Execute:

```bash
pytest -q
```

Os testes usam SQLite e sobrescrevem a dependência `get_db`, mantendo os testes isolados do banco configurado para a aplicação.

## 9. Migrações com Alembic

O Alembic deve ser usado para versionar alterações do banco.

Com uma URL configurada no ambiente:

```bash
alembic revision --autogenerate -m "descricao da alteracao"
alembic upgrade head
```

Não use `Base.metadata.drop_all()` em produção. Isso destrói as tabelas.

## 10. Docker

Construir:

```bash
docker build -t contas-api .
```

Executar:

```bash
docker run --rm -p 8000:8000 contas-api
```

Em produção, passe a variável `SQLALCHEMY_DATABASE_URL` por variável de ambiente ou secret.

## 11. Problemas importantes encontrados e corrigidos

1. **Erro de sintaxe** em `data_baixa = date | None = None`.
2. `data_previsao` estava sendo atribuído em vez de anotado como campo Pydantic.
3. `fornecedor_cliente_id` era opcional na API, mas obrigatório no banco.
4. O endpoint de relatório não retornava o resultado da função.
5. O parâmetro `ano` não estava definido corretamente como parâmetro de consulta.
6. Havia URLs de teste sem `f-string`, então `{id}` era enviado literalmente.
7. Alguns testes esperavam `fornecedor_cliente_id` na resposta, enquanto o schema devolvia o objeto `fornecedor`.
8. Havia uma asserção contraditória no teste de fornecedor inválido.
9. `httpx2` foi corrigido para `httpx`.
10. O projeto não carregava automaticamente o `.env`.
11. O `Dockerfile` usava porta 80 enquanto a aplicação local usava 8000.
12. O código antigo misturava padrões de Pydantic 1 e 2; os schemas foram atualizados para Pydantic 2.
13. `Query.get()` foi substituído por `Session.get()`.
14. O README foi ampliado para servir como material de revisão.

## 12. Segurança

Não versione `.env` nem senhas reais. Use `.env.example` apenas como modelo.

Se uma senha real já foi publicada em um repositório Git, considere essa credencial comprometida e faça sua rotação.

## 13. Roteiro de estudo sugerido

1. HTTP e métodos REST.
2. FastAPI e rotas.
3. Pydantic e validação.
4. SQLAlchemy ORM.
5. Relacionamentos 1:N.
6. Injeção de dependência com `Depends`.
7. Testes de integração com `TestClient`.
8. Tratamento de exceções.
9. Migrações com Alembic.
10. Docker e variáveis de ambiente.
11. Separação entre router, service e repository.
12. Autenticação e autorização.

O projeto foi mantido propositalmente simples para que cada camada possa ser estudada antes de adicionar abstrações.
