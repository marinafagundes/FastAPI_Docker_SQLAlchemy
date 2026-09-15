import uvicorn
from fastapi import FastAPI

from contas_a_pagar_e_receber.routers import contas_a_pagar_e_receber_router
from shared.exceptions import NotFound
from shared.exceptions_handler import not_found_exception_handler

# from shared.database import engine, Base

# Informar qual modelo deve ser criado no banco de dados
# from contas_a_pagar_e_receber.models.contas_a_pagar_e_receber_model import ContasPagarReceber

# Criar as tabelas no banco de dados
# A partir da inicialização do app, o FastAPI vai criar as tabelas no banco de dados
# Problema: reinicia o banco sempre que reinicia as migrações
# Base.metadata.drop_all(bind=engine)
# Base.metadata.create_all(bind=engine)

app = FastAPI()

@app.get("/")
def oi_eu_sou_programador():
# Alternativamente:
# def oi_eu_sou_programador() -> str:
# Indica que o retorno será uma string
    return "Oi, eu sou programador!"

# Incluir rotas
app.include_router(contas_a_pagar_e_receber_router.router)

# Incluir Exception Handler
app.add_exception_handler(NotFound, not_found_exception_handler)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)