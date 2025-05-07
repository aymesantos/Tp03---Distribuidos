import socket
import json

class ClienteSocket:
    def __init__(self, host='localhost', port=12345):
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.conectar()

    def conectar(self):
        try:
            self.sock.connect((self.host, self.port))
            print("Conectado ao servidor!")
        except Exception as e:
            print(f"Erro ao conectar ao servidor: {e}")

    def enviar(self, dados):
        try:
            dados_json = json.dumps(dados)
            self.sock.sendall(f"{len(dados_json):<10}".encode())
            self.sock.sendall(dados_json.encode())
            print(f"Dados enviados: {dados}")
            return self.receber()
        except Exception as e:
            print(f"Erro ao enviar dados: {e}")
            return {'status': 'erro', 'mensagem': str(e)}

    def receber(self):
        try:
            tamanho = int(self.sock.recv(10).decode())
            dados = self.sock.recv(tamanho).decode()
            dados_json = json.loads(dados)
            print(f"Dados recebidos: {dados_json}")
            return dados_json
        except Exception as e:
            print(f"Erro ao receber dados: {e}")
            return {'status': 'erro', 'mensagem': str(e)}

    def fechar(self):
        self.sock.close()
        print("Conexão encerrada com o servidor.")

