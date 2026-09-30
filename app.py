"""
API REST simples com Flask - Comunicação entre duas máquinas na rede local.

Máquina A (servidor): 192.168.1.4, porta 5000
Máquina B (cliente):  acessa http://192.168.1.4:5000
"""

from flask import Flask, jsonify, request

# Configurações do servidor
HOST = "0.0.0.0"          # Escuta em todas as interfaces de rede da máquina
PORTA = 5000              # Porta em que a API ficará disponível
IP_SERVIDOR = "192.168.1.4"  # IP da Máquina A na rede local (usado nas respostas)

# ---------------------------------------------------------------------------
# Criação da API
# ---------------------------------------------------------------------------
# O objeto "app" representa a aplicação Flask. É nele que as rotas
# (endpoints) são registradas.
app = Flask(__name__)

# Faz o JSON exibir acentos normalmente (ex.: "João" em vez de "Jo\u00e3o").
app.json.ensure_ascii = False
# Mantém as chaves do JSON na ordem em que foram escritas no código.
app.json.sort_keys = False

# ---------------------------------------------------------------------------
# "Banco de dados" em memória
# ---------------------------------------------------------------------------
# Uma lista Python comum. Os dados existem apenas enquanto a API estiver
# rodando; ao reiniciar o servidor, a lista volta ao estado inicial.
usuarios = [
    {"id": 1, "nome": "Ana Souza", "email": "ana@email.com"},
    {"id": 2, "nome": "Carlos Lima", "email": "carlos@email.com"},
    {"id": 3, "nome": "Mariana Alves", "email": "mariana@email.com"},
]


# ---------------------------------------------------------------------------
# Definição das rotas
# ---------------------------------------------------------------------------
# O decorador @app.route associa uma URL (e um método HTTP) a uma função.
# Quando uma requisição chega nessa URL, o Flask executa a função e envia
# o valor retornado como resposta.

@app.route("/", methods=["GET"])
def status_api():
    """GET / - Informa que a API está funcionando."""
    return jsonify({
        "mensagem": "API REST funcionando",
        "status": "online",
        "servidor": IP_SERVIDOR,
        "acesso_externo": f"http://{IP_SERVIDOR}:{PORTA}",
        "porta": PORTA,
    }), 200


@app.route("/usuarios", methods=["GET"])
def listar_usuarios():
    """GET /usuarios - Retorna a lista de usuários em JSON."""
    return jsonify(usuarios), 200


@app.route("/usuarios", methods=["POST"])
def criar_usuario():
    """POST /usuarios - Cadastra um novo usuário a partir de um JSON."""

    # Recebimento de JSON:
    # request.get_json() converte o corpo da requisição (texto JSON) em um
    # dicionário Python. Com silent=True, se o corpo não for um JSON válido,
    # o resultado é None em vez de gerar um erro.
    dados = request.get_json(silent=True)

    if not isinstance(dados, dict):
        return jsonify({
            "erro": "O corpo da requisição deve ser um JSON válido."
        }), 400

    nome = str(dados.get("nome", "")).strip()
    email = str(dados.get("email", "")).strip()

    # Validação: nome e email são obrigatórios
    if not nome or not email:
        return jsonify({
            "erro": "Os campos 'nome' e 'email' são obrigatórios."
        }), 400

    # Gera um novo id (maior id existente + 1)
    novo_id = max((u["id"] for u in usuarios), default=0) + 1

    novo_usuario = {"id": novo_id, "nome": nome, "email": email}
    usuarios.append(novo_usuario)

    # HTTP 201 (Created) indica que um novo recurso foi criado com sucesso
    return jsonify(novo_usuario), 201


# ---------------------------------------------------------------------------
# Tratamento de erros
# ---------------------------------------------------------------------------
@app.errorhandler(404)
def rota_nao_encontrada(erro):
    """Retorna JSON quando a rota acessada não existe."""
    return jsonify({
        "erro": "Rota não encontrada.",
        "caminho": request.path,
    }), 404


@app.errorhandler(405)
def metodo_nao_permitido(erro):
    """Retorna JSON quando a rota existe, mas o método HTTP não é aceito."""
    return jsonify({
        "erro": "Método HTTP não permitido para esta rota.",
        "metodo": request.method,
        "caminho": request.path,
    }), 405


# ---------------------------------------------------------------------------
# Inicialização do servidor
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    print(f"Acesso local:        http://127.0.0.1:{PORTA}")
    print(f"Acesso pela rede:    http://{IP_SERVIDOR}:{PORTA}")

    # host="0.0.0.0": o servidor aceita conexões de QUALQUER interface de
    #   rede da máquina (inclusive da rede local, 192.168.1.4). Se fosse
    #   "127.0.0.1", apenas a própria Máquina A conseguiria acessar a API.
    # port=5000: porta TCP em que a API ficará escutando.
    # debug=False: modo mais seguro para uma demonstração em rede.
    app.run(host=HOST, port=PORTA, debug=False)
