import socket
import threading
import json

class ServidorSocket:
    def __init__(self, host='127.0.0.1', porta=12345):
        self.host = host
        self.porta = porta
        self.servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.servidor.bind((self.host, self.porta))
        self.servidor.listen(5)
        print(f"Servidor iniciado em {self.host}:{self.porta}")

    def iniciar(self):
        while True:
            cliente, endereco = self.servidor.accept()
            print(f"Cliente conectado: {endereco}")
            cliente_thread = threading.Thread(target=self.tratar_cliente, args=(cliente,))
            cliente_thread.start()

    def tratar_cliente(self, cliente):
        while True:
            dados = cliente.recv(1024)
            if not dados:
                break

            dados = dados.decode('utf-8')
            requisicao = json.loads(dados)
            resposta = self.processar_requisicao(requisicao)

            cliente.sendall(json.dumps(resposta).encode('utf-8'))
        cliente.close()

    def processar_requisicao(self, requisicao):
        acao = requisicao.get('acao')

        if acao == 'login':
            email = requisicao.get('email')
            senha = requisicao.get('senha')
            if email == 'teste@teste.com' and senha == 'senha123':
                return {'status': 'ok', 'usuario': {'nome': 'Teste', 'email': email}}
            else:
                return {'status': 'erro'}
        
        elif acao == 'cadastro':
            return {'status': 'sucesso'}

        elif acao == 'listar_produtos':
            produtos = [
                {'id': 1, 'nome': 'Varinha', 'preco': 100, 'quantidade': 10},
                {'id': 2, 'nome': 'Poção', 'preco': 50, 'quantidade': 5}
            ]
            return {'status': 'sucesso', 'produtos': produtos}
        
        elif acao == 'comprar':
            return {'status': 'sucesso'}

        elif acao == 'criar_loja':
            return {'status': 'sucesso'}

        elif acao == 'criar_produto':
            return {'status': 'sucesso'}

        elif acao == 'meus_produtos':
            produtos = [
                {'nome': 'Varinha', 'preco': 100, 'quantidade': 5, 'disponivel': True},
                {'nome': 'Poção', 'preco': 50, 'quantidade': 2, 'disponivel': False}
            ]
            return {'status': 'sucesso', 'produtos': produtos}

        return {'status': 'erro'}

if __name__ == "__main__":
    servidor = ServidorSocket()
    servidor.iniciar()
