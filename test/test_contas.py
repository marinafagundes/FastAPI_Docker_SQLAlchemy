from decimal import Decimal

from contas_a_pagar_e_receber.routers.contas_a_pagar_e_receber_router import QUANTIDADE_PERMITIDA_POR_MES

def conta(descricao="Aluguel", valor=1000, tipo="PAGAR", data="2026-01-10", fornecedor_cliente_id=None):
    payload = {
        "descricao": descricao,
        "valor": valor,
        "tipo": tipo,
        "data_previsao": data,
    }
    if fornecedor_cliente_id is not None:
        payload["fornecedor_cliente_id"] = fornecedor_cliente_id
    return payload

def test_criar_e_listar_contas(client):
    criada = client.post("/contas-a-pagar-e-receber", json=conta()).json()

    assert criada["id"] == 1
    assert criada["descricao"] == "Aluguel"
    assert criada["data_previsao"] == "2026-01-10"
    assert criada["esta_baixada"] is False

    resposta = client.get("/contas-a-pagar-e-receber")
    assert resposta.status_code == 200
    assert len(resposta.json()) == 1

def test_criar_conta_com_fornecedor(client):
    fornecedor = client.post("/fornecedor-cliente", json={"nome": "Casa da Música"}).json()
    resposta = client.post(
        "/contas-a-pagar-e-receber",
        json=conta("Curso", 250, fornecedor_cliente_id=fornecedor["id"]),
    )

    assert resposta.status_code == 201
    assert resposta.json()["fornecedor"] == fornecedor

def test_fornecedor_inexistente_retorna_422(client):
    resposta = client.post(
        "/contas-a-pagar-e-receber",
        json=conta(fornecedor_cliente_id=1001),
    )
    assert resposta.status_code == 422
    assert resposta.json()["detail"] == "Esse fornecedor não existe no banco de dados"

def test_buscar_atualizar_e_excluir_conta(client):
    criada = client.post("/contas-a-pagar-e-receber", json=conta()).json()
    id_conta = criada["id"]

    assert client.get(f"/contas-a-pagar-e-receber/{id_conta}").status_code == 200

    atualizada = client.put(
        f"/contas-a-pagar-e-receber/{id_conta}",
        json=conta(valor=111),
    )
    assert atualizada.status_code == 200
    assert Decimal(str(atualizada.json()["valor"])) == Decimal("111.00")

    removida = client.delete(f"/contas-a-pagar-e-receber/{id_conta}")
    assert removida.status_code == 204
    assert client.get(f"/contas-a-pagar-e-receber/{id_conta}").status_code == 404

def test_id_inexistente_retorna_404(client):
    assert client.get("/contas-a-pagar-e-receber/100").status_code == 404
    assert client.put("/contas-a-pagar-e-receber/100", json=conta()).status_code == 404
    assert client.delete("/contas-a-pagar-e-receber/100").status_code == 404

def test_validacoes_da_conta(client):
    assert client.post("/contas-a-pagar-e-receber", json=conta(descricao="A")).status_code == 422
    assert client.post("/contas-a-pagar-e-receber", json=conta(descricao="A" * 31)).status_code == 422
    assert client.post("/contas-a-pagar-e-receber", json=conta(valor=0)).status_code == 422
    assert client.post("/contas-a-pagar-e-receber", json=conta(valor=-1)).status_code == 422
    assert client.post("/contas-a-pagar-e-receber", json=conta(tipo="INVALIDO")).status_code == 422

def test_baixar_conta(client):
    criada = client.post("/contas-a-pagar-e-receber", json=conta(valor=333)).json()
    resposta = client.post(f"/contas-a-pagar-e-receber/{criada['id']}/baixar")

    assert resposta.status_code == 200
    assert resposta.json()["esta_baixada"] is True
    assert Decimal(str(resposta.json()["valor_baixa"])) == Decimal("333.00")
    assert resposta.json()["data_baixa"] is not None

def test_alterar_conta_baixada_invalida_a_baixa_anterior(client):
    criada = client.post("/contas-a-pagar-e-receber", json=conta(valor=333)).json()
    id_conta = criada["id"]
    client.post(f"/contas-a-pagar-e-receber/{id_conta}/baixar")

    atualizada = client.put(
        f"/contas-a-pagar-e-receber/{id_conta}",
        json=conta(valor=444),
    )
    assert atualizada.json()["esta_baixada"] is False
    assert atualizada.json()["valor_baixa"] is None

    baixada_novamente = client.post(f"/contas-a-pagar-e-receber/{id_conta}/baixar")
    assert Decimal(str(baixada_novamente.json()["valor_baixa"])) == Decimal("444.00")

def test_limite_mensal(client):
    for _ in range(QUANTIDADE_PERMITIDA_POR_MES):
        resposta = client.post("/contas-a-pagar-e-receber", json=conta())
        assert resposta.status_code == 201

    ultima = client.post("/contas-a-pagar-e-receber", json=conta())
    assert ultima.status_code == 422
    assert ultima.json()["detail"] == "Você não pode mais lançar contas para esse mês"

def test_relatorio_de_gastos_por_mes(client):
    for mes in range(1, 13):
        for _ in range(2):
            client.post(
                "/contas-a-pagar-e-receber",
                json=conta(valor=10, tipo="PAGAR", data=f"2026-{mes:02d}-01"),
            )
        client.post(
            "/contas-a-pagar-e-receber",
            json=conta(valor=999, tipo="RECEBER", data=f"2026-{mes:02d}-02"),
        )

    resposta = client.get("/contas-a-pagar-e-receber/previsao-gastos-do-mes?ano=2026")
    assert resposta.status_code == 200
    resultados = resposta.json()
    assert len(resultados) == 12
    assert all(Decimal(str(item["valor_total"])) == Decimal("20.00") for item in resultados)

def test_relatorio_sem_registros(client):
    resposta = client.get("/contas-a-pagar-e-receber/previsao-gastos-do-mes?ano=1990")
    assert resposta.status_code == 200
    assert resposta.json() == []
