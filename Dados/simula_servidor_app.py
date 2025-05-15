import socket
import json

req = {
    "operacao": "listar_produtos",
    "parametros": {}
}

# req = {
#     "operacao": "cadastrar_usuario",
#     "parametros": {
#         "nome": "Hermione Granger",
#         "email": "hermione@hogwarts.com",
#         "senha": "patrono123",
#         "tipo": "cliente"  # ou vendedor
#     }
# }

# req = {
#     "operacao": "autenticar_usuario",
#     "parametros": {
#         "email": "hermione@hogwarts.com",
#         "senha": "patrono123"
#     }
# }

# req = {
#     "operacao": "buscar_usuario",
#     "parametros": {
#         "id": 1
#     }
# }

# req = {
#     "operacao": "cadastrar_loja",
#     "parametros": {
#         "nome": "Empório das Corujas",
#         "descricao": "Loja de corujas e acessórios mágicos",
#         "usuario_id": 1  # ID do usuário dono da loja
#     }
# }

# req = {
#     "operacao": "listar_lojas",
#     "parametros": {}
# }

# req = {
#     "operacao": "buscar_loja",
#     "parametros": {
#         "id": 1
#     }
# }

# req = {
#     "operacao": "cadastrar_produto",
#     "parametros": {
#         "nome": "Varinha de Sabugueiro",
#         "descricao": "A varinha mais poderosa do mundo",
#         "preco": 999.99,
#         "estoque": 5,
#         "loja_id": 1
#     }
# }

# req = {
#     "operacao": "listar_produtos",
#     "parametros": {}
# }

# req = {
#     "operacao": "buscar_produto",
#     "parametros": {
#         "id": 1
#     }
# }

# req = {
#     "operacao": "comprar_produto",
#     "parametros": {
#         "cliente_id": 1,  # ID do usuário comprador
#         "itens": [
#             {
#                 "produto_id": 1,
#                 "quantidade": 2,
#                 "preco_unitario": 999.99
#             }
#         ]
#     }
# }

# req = {
#     "operacao": "listar_compras_cliente",
#     "parametros": {
#         "cliente_id": 1
#     }
# }

# req = {
#     "operacao": "registrar_avaliacao",
#     "parametros": {
#         "usuario_id": 1,
#         "produto_id": 1,
#         "nota": 5,
#         "comentario": "Produto excelente!"
#     }
# }

# req = {
#     "operacao": "listar_avaliacoes_produto",
#     "parametros": {
#         "produto_id": 1
#     }
# }


with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect(('localhost', 5003))
    s.sendall(json.dumps(req).encode())
    resposta = s.recv(4096)
    print("Resposta:", json.loads(resposta.decode()))
