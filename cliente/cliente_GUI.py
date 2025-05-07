import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QPushButton,
    QLineEdit, QTabWidget, QFormLayout, QMessageBox, QComboBox, QFileDialog,
    QListWidget, QHBoxLayout, QInputDialog
)
from PyQt6.QtGui import QPixmap
from cliente import ClienteSocket

class InterfaceCliente(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("BecoDiagonal")
        self.setGeometry(100, 100, 800, 600)

        self.cliente_socket = ClienteSocket()

        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        # Abas do sistema
        self.login_tab = QWidget()
        self.cadastro_tab = QWidget()
        self.loja_tab = QWidget()
        self.minha_loja_tab = QWidget()

        # Adicionando as abas ao TabWidget
        self.tabs.addTab(self.login_tab, "Login")
        self.tabs.addTab(self.cadastro_tab, "Cadastro")
        self.tabs.addTab(self.loja_tab, "Loja")
        self.tabs.addTab(self.minha_loja_tab, "Minha Loja")

        # Ocultando a barra de abas e mostrando apenas a aba de login inicialmente
        self.tabs.tabBar().setVisible(False)
        self.tabs.setCurrentWidget(self.login_tab)

        self.usuario_atual = None
        self.foto_perfil_path = ""

        self.setup_login_tab()
        self.setup_cadastro_tab()
        self.setup_loja_tab()
        self.setup_minha_loja_tab()

    def setup_login_tab(self):
        layout = QFormLayout()
        self.email_input = QLineEdit()
        self.senha_input = QLineEdit()
        self.senha_input.setEchoMode(QLineEdit.EchoMode.Password)

        layout.addRow("Email:", self.email_input)
        layout.addRow("Senha:", self.senha_input)

        login_button = QPushButton("Entrar")
        login_button.clicked.connect(self.realizar_login)
        layout.addRow(login_button)

        cadastrar_button = QPushButton("Cadastrar")
        cadastrar_button.clicked.connect(self.ir_para_cadastro)  # Função para ir para a aba de cadastro
        layout.addRow(cadastrar_button)

        self.login_tab.setLayout(layout)

    def ir_para_cadastro(self):
        self.tabs.setCurrentWidget(self.cadastro_tab)  # Vai para a aba de Cadastro

    def realizar_login(self):
        email = self.email_input.text().strip()
        senha = self.senha_input.text().strip()

        if not email or not senha:
            QMessageBox.warning(self, 'Campos obrigatórios', 'Preencha o email e a senha.')
            return

        resposta = self.cliente_socket.enviar({'acao': 'login', 'email': email, 'senha': senha})
        if resposta.get('status') == 'ok':
            self.usuario_atual = resposta.get('usuario')
            QMessageBox.information(self, 'Sucesso', 'Login realizado com sucesso!')
            self.tabs.setCurrentWidget(self.loja_tab)  # Vai para a tela de Loja
        else:
            QMessageBox.warning(self, 'Erro', 'Credenciais inválidas.')

    def setup_cadastro_tab(self):
        self.cadastro_layout = QVBoxLayout()
        self.cadastro_form = QFormLayout()

        self.nome_input = QLineEdit()
        self.email_cad_input = QLineEdit()
        self.senha_cad_input = QLineEdit()
        self.senha_cad_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.tipo_bruxo_input = QComboBox()
        self.tipo_bruxo_input.addItems(["Nascido Trouxa", "Sangue Puro", "Aborto"])

        self.foto_button = QPushButton("Selecionar Foto de Perfil")
        self.foto_button.clicked.connect(self.selecionar_foto)

        self.cadastro_form.addRow("Nome:", self.nome_input)
        self.cadastro_form.addRow("Email:", self.email_cad_input)
        self.cadastro_form.addRow("Senha:", self.senha_cad_input)
        self.cadastro_form.addRow("Tipo de Bruxo:", self.tipo_bruxo_input)
        self.cadastro_form.addRow(self.foto_button)

        cadastrar_button = QPushButton("Cadastrar")
        cadastrar_button.clicked.connect(self.realizar_cadastro)
        self.cadastro_layout.addLayout(self.cadastro_form)
        self.cadastro_layout.addWidget(cadastrar_button)
        self.cadastro_tab.setLayout(self.cadastro_layout)

    def selecionar_foto(self):
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(self, 'Selecionar Imagem', '', 'Imagens (*.png *.jpg *.jpeg)')
        if file_path:
            self.foto_perfil_path = file_path

    def realizar_cadastro(self):
        dados = {
            'acao': 'cadastro',
            'nome': self.nome_input.text().strip(),
            'email': self.email_cad_input.text().strip(),
            'senha': self.senha_cad_input.text().strip(),
            'tipo_bruxo': self.tipo_bruxo_input.currentText(),
            'foto_perfil': self.foto_perfil_path
        }
        resposta = self.cliente_socket.enviar(dados)
        if resposta.get('status') == 'sucesso':
            QMessageBox.information(self, 'Sucesso', 'Cadastro realizado com sucesso!')
            self.tabs.setCurrentWidget(self.login_tab)  # Vai para a tela de Login após cadastro
        else:
            QMessageBox.warning(self, 'Erro', 'Não foi possível cadastrar.')

    def setup_loja_tab(self):
        layout = QVBoxLayout()
        self.lista_produtos = QListWidget()
        atualizar_btn = QPushButton("Atualizar Produtos")
        atualizar_btn.clicked.connect(self.atualizar_produtos)

        comprar_btn = QPushButton("Comprar Produto Selecionado")
        comprar_btn.clicked.connect(self.comprar_produto)

        layout.addWidget(self.lista_produtos)
        layout.addWidget(atualizar_btn)
        layout.addWidget(comprar_btn)
        self.loja_tab.setLayout(layout)

    def atualizar_produtos(self):
        resposta = self.cliente_socket.enviar({'acao': 'listar_produtos'})
        self.lista_produtos.clear()
        self.produtos_map = {}
        if resposta.get('status') == 'sucesso':
            for p in resposta.get('produtos', []):
                item = f"{p['nome']} - R${p['preco']} ({p['quantidade']} unid.)"
                self.lista_produtos.addItem(item)
                self.produtos_map[item] = p

    def comprar_produto(self):
        item = self.lista_produtos.currentItem()
        if item:
            produto = self.produtos_map[item.text()]
            quantidade, ok = QInputDialog.getInt(self, 'Quantidade', 'Quantas unidades deseja comprar?', 1, 1, produto['quantidade'])
            if ok:
                dados = {'acao': 'comprar', 'produto_id': produto['id'], 'quantidade': quantidade}
                resposta = self.cliente_socket.enviar(dados)
                if resposta.get('status') == 'sucesso':
                    QMessageBox.information(self, 'Sucesso', 'Compra realizada!')
                    self.atualizar_produtos()
                else:
                    QMessageBox.warning(self, 'Erro', 'Não foi possível realizar a compra.')

    def setup_minha_loja_tab(self):
        layout = QVBoxLayout()

        criar_loja_btn = QPushButton("Criar Loja")
        criar_loja_btn.clicked.connect(self.criar_loja)

        criar_produto_btn = QPushButton("Criar Produto")
        criar_produto_btn.clicked.connect(self.criar_produto)

        self.lista_meus_produtos = QListWidget()
        atualizar_btn = QPushButton("Atualizar Meus Produtos")
        atualizar_btn.clicked.connect(self.atualizar_meus_produtos)

        layout.addWidget(criar_loja_btn)
        layout.addWidget(criar_produto_btn)
        layout.addWidget(self.lista_meus_produtos)
        layout.addWidget(atualizar_btn)
        self.minha_loja_tab.setLayout(layout)

    def criar_loja(self):
        nome_loja, ok = QInputDialog.getText(self, 'Criar Loja', 'Nome da Loja:')
        if ok and nome_loja:
            dados = {'acao': 'criar_loja', 'nome_loja': nome_loja}
            resposta = self.cliente_socket.enviar(dados)
            if resposta.get('status') == 'sucesso':
                QMessageBox.information(self, 'Sucesso', 'Loja criada!')
            else:
                QMessageBox.warning(self, 'Erro', 'Erro ao criar loja.')

    def criar_produto(self):
        nome, ok1 = QInputDialog.getText(self, 'Nome do Produto', 'Nome:')
        preco, ok2 = QInputDialog.getDouble(self, 'Preço', 'Preço:', 0, 0)
        quantidade, ok3 = QInputDialog.getInt(self, 'Quantidade', 'Quantidade:', 1, 1)

        if ok1 and ok2 and ok3:
            dados = {'acao': 'criar_produto', 'nome': nome, 'preco': preco, 'quantidade': quantidade, 'disponivel': True}
            resposta = self.cliente_socket.enviar(dados)
            if resposta.get('status') == 'sucesso':
                QMessageBox.information(self, 'Sucesso', 'Produto criado!')
                self.atualizar_meus_produtos()
            else:
                QMessageBox.warning(self, 'Erro', 'Erro ao criar produto.')

    def atualizar_meus_produtos(self):
        resposta = self.cliente_socket.enviar({'acao': 'meus_produtos'})
        self.lista_meus_produtos.clear()
        if resposta.get('status') == 'sucesso':
            for p in resposta.get('produtos', []):
                status = 'Disponível' if p.get('disponivel') else 'Pausado'
                item = f"{p['nome']} - R${p['preco']} ({p['quantidade']} unid.) [{status}]"
                self.lista_meus_produtos.addItem(item)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    janela = InterfaceCliente()
    janela.show()
    sys.exit(app.exec())


