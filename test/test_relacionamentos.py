def test_listar_contas_de_um_fornecedor(client):
    fornecedor1 = client.post("/fornecedor-cliente", json={"nome": "Casa da Música"}).json()
    fornecedor2 = client.post("/fornecedor-cliente", json={"nome": "Adde Treinamento"}).json()

    payload = {
        "descricao": "Curso de Python",
        "valor": 1000.5,
        "tipo": "PAGAR",
        "fornecedor_cliente_id": fornecedor2["id"],
        "data_previsao": "2026-01-10",
    }
    client.post("/contas-a-pagar-e-receber", json=payload)

    payload["fornecedor_cliente_id"] = fornecedor1["id"]
    client.post("/contas-a-pagar-e-receber", json=payload)

    payload["descricao"] = "Outro curso"
    client.post("/contas-a-pagar-e-receber", json=payload)

    resposta1 = client.get(f"/fornecedor-cliente/{fornecedor1['id']}/contas-a-pagar-e-receber")
    resposta2 = client.get(f"/fornecedor-cliente/{fornecedor2['id']}/contas-a-pagar-e-receber")

    assert resposta1.status_code == 200
    assert resposta2.status_code == 200
    assert len(resposta1.json()) == 2
    assert len(resposta2.json()) == 1

def test_fornecedor_sem_contas_retorna_lista_vazia(client):
    fornecedor = client.post("/fornecedor-cliente", json={"nome": "Casa da Música"}).json()
    resposta = client.get(f"/fornecedor-cliente/{fornecedor['id']}/contas-a-pagar-e-receber")

    assert resposta.status_code == 200
    assert resposta.json() == []
