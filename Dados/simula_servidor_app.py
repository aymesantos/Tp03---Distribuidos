import socket
import json

req = {
    "operacao": "listar_produtos",
    "parametros": {}
}

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect(('localhost', 5003))
    s.sendall(json.dumps(req).encode())
    resposta = s.recv(4096)
    print("Resposta:", json.loads(resposta.decode()))
