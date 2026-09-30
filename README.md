# API REST com Flask — Comunicação entre duas máquinas na rede local

## Objetivo

Demonstrar a comunicação entre duas máquinas de uma mesma rede local por meio de uma API REST simples:

- **Máquina A (servidor)**: executa a API em Python/Flask. IP `192.168.1.4`, porta `5000`.
- **Máquina B (cliente)**: outro computador da mesma rede, que acessa a API em `http://192.168.1.4:5000`.

Os dados ficam apenas em memória (uma lista Python). Não há banco de dados, autenticação nem Docker.

## Estrutura do projeto

```
iot_trabalho/
├── app.py            # Código da API
├── requirements.txt  # Dependências (apenas Flask)
└── README.md         # Este arquivo
```

## Endpoints

| Método | Rota        | Descrição                                   |
|--------|-------------|---------------------------------------------|
| GET    | `/`         | Informa que a API está funcionando          |
| GET    | `/usuarios` | Lista os usuários cadastrados               |
| POST   | `/usuarios` | Cadastra um usuário (`nome` e `email`)      |

Rotas inexistentes retornam **HTTP 404** em JSON.

## Requisitos

- Windows 11
- Python 3.8 ou superior (com `pip`)
- Máquina A e Máquina B conectadas na mesma rede local

### Instalando o Python (caso ainda não tenha)

1. Baixe em <https://www.python.org/downloads/>.
2. Na instalação, **marque a opção "Add python.exe to PATH"**.
3. Feche e abra novamente o terminal e confira:

```powershell
python --version
```

## Instalando as dependências

No PowerShell, dentro da pasta do projeto:

```powershell
cd C:\Users\willa\iot_trabalho
python -m pip install -r requirements.txt
```

## Executando a API no Windows 11

```powershell
python app.py
```

Saída esperada (semelhante a):

```
Acesso local:        http://127.0.0.1:5000
Acesso pela rede:    http://192.168.1.4:5000
 * Serving Flask app 'app'
 * Running on all addresses (0.0.0.0)
 * Running on http://127.0.0.1:5000
 * Running on http://192.168.1.4:5000
```

Deixe esse terminal aberto enquanto a API estiver em uso. Para parar, pressione `Ctrl + C`.

### Liberando a porta 5000 no Firewall do Windows

Na primeira execução, o Windows pode exibir um alerta do Firewall. Marque **"Redes privadas"** e clique em **Permitir acesso**.

Se o alerta não aparecer e a Máquina B não conseguir conectar, abra o PowerShell **como Administrador** e execute:

```powershell
New-NetFirewallRule -DisplayName "API Flask 5000" -Direction Inbound -Protocol TCP -LocalPort 5000 -RemoteAddress LocalSubnet -Action Allow -Profile Any
```

Essa regra libera a porta 5000 apenas para dispositivos da mesma rede local (`LocalSubnet`), mesmo que a rede esteja marcada como "Pública".

Para remover a regra depois da apresentação (também como Administrador):

```powershell
Remove-NetFirewallRule -DisplayName "API Flask 5000"
```

## Testando localmente (na Máquina A)

Abra **outro** terminal (o primeiro continua rodando a API).

> No PowerShell, use `curl.exe` (e não apenas `curl`, que no PowerShell é um apelido para outro comando).

Navegador: acesse <http://localhost:5000> e <http://localhost:5000/usuarios>.

PowerShell:

```powershell
curl.exe http://localhost:5000/
curl.exe http://localhost:5000/usuarios
```

## Acessando a partir da Máquina B

Na Máquina B, basta trocar `localhost` pelo IP da Máquina A: **`192.168.1.4`**.

Navegador: <http://192.168.1.4:5000> e <http://192.168.1.4:5000/usuarios>.

Antes, se quiser, teste a conectividade:

```powershell
ping 192.168.1.4
Test-NetConnection 192.168.1.4 -Port 5000
```

(`TcpTestSucceeded : True` indica que a porta 5000 está acessível.)

## Exemplos de requisições com curl

### GET /

```
curl http://192.168.1.4:5000/
```

Resposta (HTTP 200):

```json
{
  "mensagem": "API REST funcionando",
  "status": "online",
  "servidor": "192.168.1.4",
  "acesso_externo": "http://192.168.1.4:5000",
  "porta": 5000
}
```

### GET /usuarios

```
curl http://192.168.1.4:5000/usuarios
```

Resposta (HTTP 200):

```json
[
  { "id": 1, "nome": "Ana Souza", "email": "ana@email.com" },
  { "id": 2, "nome": "Carlos Lima", "email": "carlos@email.com" },
  { "id": 3, "nome": "Mariana Alves", "email": "mariana@email.com" }
]
```

### POST /usuarios

As aspas mudam conforme o terminal usado:

**Prompt de Comando (cmd) do Windows:**

```cmd
curl -i -X POST http://192.168.1.4:5000/usuarios -H "Content-Type: application/json" -d "{\"nome\": \"Joao\", \"email\": \"joao@email.com\"}"
```

**PowerShell** (usando o comando nativo `Invoke-RestMethod`, mais simples que o curl aqui):

```powershell
Invoke-RestMethod -Method Post -Uri http://192.168.1.4:5000/usuarios -ContentType "application/json; charset=utf-8" -Body '{"nome": "João", "email": "joao@email.com"}'
```

**Linux / macOS (bash):**

```bash
curl -i -X POST http://192.168.1.4:5000/usuarios -H "Content-Type: application/json" -d '{"nome": "João", "email": "joao@email.com"}'
```

Resposta (HTTP 201 Created):

```json
{
  "id": 4,
  "nome": "João",
  "email": "joao@email.com"
}
```

Depois disso, um novo `GET /usuarios` mostrará o usuário adicionado.

### POST com dados incompletos

```cmd
curl -i -X POST http://192.168.1.4:5000/usuarios -H "Content-Type: application/json" -d "{\"nome\": \"Joao\"}"
```

Resposta (HTTP 400 Bad Request):

```json
{
  "erro": "Os campos 'nome' e 'email' são obrigatórios."
}
```

### Rota inexistente

```
curl -i http://192.168.1.4:5000/produtos
```

Resposta (HTTP 404 Not Found):

```json
{
  "erro": "Rota não encontrada.",
  "caminho": "/produtos"
}
```

## Por que usar `0.0.0.0` e não `127.0.0.1`?

- `127.0.0.1` (localhost) é o endereço de **loopback**: só existe dentro da própria máquina. Um servidor escutando nesse endereço aceita conexões **apenas da Máquina A**; a Máquina B receberia "conexão recusada".
- `0.0.0.0` significa "**todas as interfaces de rede**" da máquina. Assim, o servidor aceita conexões pelo loopback (`127.0.0.1`) **e** pela placa de rede (`192.168.1.4`), permitindo que a Máquina B acesse a API.

Resumindo: `0.0.0.0` é o endereço em que o servidor **escuta**; `192.168.1.4` é o endereço que o cliente **usa para acessar**.

## Observações

- Os dados são mantidos em memória: ao reiniciar a API, os usuários cadastrados via POST são perdidos.
- O servidor embutido do Flask é adequado para desenvolvimento e demonstrações, não para produção.
- Se o IP da Máquina A mudar (ex.: o roteador atribuir outro via DHCP), confira com `ipconfig` e use o novo IP.
