from fastapi.testclient import TestClient
from main import app  # Certifique-se de que o objeto principal do FastAPI se chama 'app' no seu main.py

client = TestClient(app)

# Passo 1: Escrever testes automatizados cobrindo fluxos de login bem-sucedidos e com falhas.[span_3](start_span)[span_3](end_span)
def test_login_sucesso():
    # Simulando um login de sucesso (Ajuste a rota e os dados para bater com o seu BD)
    response = client.post("/login", data={"username": "admin@email.com", "password": "senha_admin"})
    
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"

def test_login_falha_senha_incorreta():
    # Simulando um login com falha
    response = client.post("/login", data={"username": "admin@email.com", "password": "senha_errada"})
    
    # O sistema deve rejeitar retornando 401
    assert response.status_code == 401

# Passo 3: Escrever testes verificando o retorno 401 em chamadas sem token.[span_4](start_span)[span_4](end_span)
def test_acesso_sem_token_retorna_401():
    # Tentando acessar uma rota protegida (ex: criar evento) sem enviar o token no cabeçalho
    response = client.post("/eventos", json={"titulo": "Evento Teste", "capacidade": 100})
    
    # Deve retornar erro de não autenticado
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"

# Passo 2: Escrever testes que provem que um usuário recebe 403 ao acessar rotas proibidas para o seu perfil.[span_5](start_span)[span_5](end_span)
def test_participante_acessando_rota_proibida_retorna_403():
    # 1. Fazemos login com um usuário de perfil "Participante"
    login_response = client.post("/login", data={"username": "participante@email.com", "password": "senha_participante"})
    
    # Se o login falhar no teste, ele quebra aqui antes de testar o 403
    assert login_response.status_code == 200, "O login do participante falhou no teste."
    
    token = login_response.json().get("access_token")
    headers = {"Authorization": f"Bearer {token}"}
    
    # 2. O Participante tenta criar um evento (ação restrita a Organizador/Admin)
    payload_evento = {
        "titulo": "Evento Clandestino",
        "capacidade": 50
    }
    response = client.post("/eventos", headers=headers, json=payload_evento)
    
    # 3. O sistema deve reconhecer o token, mas bloquear a ação por falta de permissão
    assert response.status_code == 403
