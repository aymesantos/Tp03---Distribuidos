import socket
import json

class Cliente:
    def __init__(self, host='localhost', porta=5000):
        self.host = host
        self.porta = porta
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.host, self.porta))
        
    def enviar_mensagem(self, mensagem):
        try:
            # Serializa a mensagem para JSON
            mensagem_json = json.dumps(mensagem)
            # Envia a mensagem como bytes
            self.socket.sendall(mensagem_json.encode('utf-8'))
        except Exception as e:
            print(f"Erro ao enviar mensagem: {e}")
        
    def receber_mensagem(self):
        try:
            # Recebe a resposta do servidor
            resposta = self.socket.recv(1024)
            # Desserializa a resposta recebida de JSON para dicionário Python
            return json.loads(resposta.decode('utf-8'))
        except Exception as e:
            print(f"Erro ao receber mensagem: {e}")
            return None
        
    def login(self, email, senha):
        mensagem = {'acao': 'login', 'email': email, 'senha': senha}
        self.enviar_mensagem(mensagem)
        return self.receber_mensagem()

    def cadastro(self, nome, casa, email, senha, tipo_bruxo):
        mensagem = {'acao': 'cadastro', 'nome': nome, 'casa': casa, 'email': email, 'senha': senha, 'tipo_bruxo': tipo_bruxo}
        self.enviar_mensagem(mensagem)
        return self.receber_mensagem()

