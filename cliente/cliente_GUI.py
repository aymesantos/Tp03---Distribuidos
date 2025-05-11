import sys
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit,QListWidget,QStackedWidget, QPushButton,QHBoxLayout, QMessageBox, QComboBox
from cliente import Cliente
import re # Importando o módulo re para expressões regulares

class JanelaLogin(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.adjustSize()
        self.cliente = Cliente()

    def initUI(self):
        self.setWindowTitle('BecoDiagonal - Login')
        
        layout = QVBoxLayout()
        
        self.email_input = QLineEdit(self)
        self.email_input.setPlaceholderText('Email')
        layout.addWidget(self.email_input)
        
        self.senha_input = QLineEdit(self)
        self.senha_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.senha_input.setPlaceholderText('Senha')
        layout.addWidget(self.senha_input)
        
        self.login_btn = QPushButton('Entrar', self)
        self.login_btn.clicked.connect(self.realizar_login)
        layout.addWidget(self.login_btn)
        
        self.cadastro_btn = QPushButton('Criar conta', self)
        self.cadastro_btn.clicked.connect(self.ir_para_cadastro)
        layout.addWidget(self.cadastro_btn)
        
        self.setLayout(layout)
        self.show()

    def realizar_login(self):
        email = self.email_input.text().strip()
        senha = self.senha_input.text()

        if not email or not senha:
            QMessageBox.warning(self, 'Erro', 'Preencha todos os campos!')
            return

        resposta = self.cliente.login(email, senha)

        if resposta:
            if resposta.get('status') == 'sucesso':
                QMessageBox.information(self, 'Sucesso', 'Login realizado com sucesso!')
            elif resposta.get('erro') == 'senha_incorreta':
                QMessageBox.warning(self, 'Erro', 'Senha incorreta!')
            elif resposta.get('erro') == 'usuario_nao_encontrado':
                QMessageBox.warning(self, 'Erro', 'Usuário não encontrado!')
            else:
                QMessageBox.warning(self, 'Erro', 'Erro no login.')
        else:
            QMessageBox.warning(self, 'Erro', 'Erro de conexão com o servidor.')

    def ir_para_cadastro(self):
        self.close()
        self.janela_cadastro = JanelaCadastro()
        self.janela_cadastro.show()

#### Tela de Cadastro

class JanelaCadastro(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.cliente = Cliente()

    def initUI(self):
        self.setWindowTitle('BecoDiagonal - Cadastro')
        
        layout = QVBoxLayout()
        
        self.nome_input = QLineEdit(self)
        self.nome_input.setPlaceholderText('Nome')
        layout.addWidget(self.nome_input)
        
        self.casa_input = QComboBox(self)
        self.casa_input.addItems(["Grifinória", "Sonserina", "Lufa-Lufa", "Corvinal"])
        layout.addWidget(self.casa_input)
        
        self.email_input = QLineEdit(self)
        self.email_input.setPlaceholderText('Email')
        layout.addWidget(self.email_input)
        
        self.senha_input = QLineEdit(self)
        self.senha_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.senha_input.setPlaceholderText('Senha')
        layout.addWidget(self.senha_input)
        
        self.tipo_bruxo_input = QComboBox(self)
        self.tipo_bruxo_input.addItems(["Nascido Trouxa", "Bruxo", "Aborto"])
        layout.addWidget(self.tipo_bruxo_input)
        
        self.cadastro_btn = QPushButton('Criar Conta', self)
        self.cadastro_btn.clicked.connect(self.realizar_cadastro)
        layout.addWidget(self.cadastro_btn)
        
        self.setLayout(layout)
        self.show()

    def realizar_cadastro(self):
        nome = self.nome_input.text().strip()
        casa = self.casa_input.currentText() 
        email = self.email_input.text().strip()
        senha = self.senha_input.text()
        tipo_bruxo = self.tipo_bruxo_input.currentText()

        # Verificações locais (cliente)
        if not all([nome, casa, email, senha, tipo_bruxo]):
            QMessageBox.warning(self, 'Erro', 'Preencha todos os campos!')
            return

        if not re.match(r'^[A-Za-z0-9 ]{4,20}$', nome):
            QMessageBox.warning(self, 'Erro', 'Nome deve ter entre 4 e 20 caracteres e conter apenas letras, números e espaços.')
            return

        if len(senha) < 8:
            QMessageBox.warning(self, 'Erro', 'A senha deve ter no mínimo 8 caracteres.')
            return

        if not re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email):
            QMessageBox.warning(self, 'Erro', 'Email inválido.')
            return

        # Envia dados para o servidor
        resposta = self.cliente.cadastro(nome, casa, email, senha, tipo_bruxo)

        # Trata resposta do servidor
        if resposta:
            if resposta.get('status') == 'sucesso':
                QMessageBox.information(self, 'Sucesso', 'Cadastro realizado com sucesso!')
                self.close()
                self.janela_login = JanelaLogin()
                self.janela_login.show()
            elif resposta.get('erro') == 'email_ja_cadastrado':
                QMessageBox.warning(self, 'Erro', 'Email já cadastrado.')
            else:
                QMessageBox.warning(self, 'Erro', 'Erro no cadastro, tente novamente!')
        else:
            QMessageBox.warning(self, 'Erro', 'Erro de conexão com o servidor.')
            
class JanelaMarketplace(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.cliente = Cliente()

    def initUI(self):
        self.setWindowTitle('BecoDiagonal - Marketplace')
        self.setGeometry(200, 200, 800, 600)  # Tamanho da janela inicial
        
        # Layout principal
        main_layout = QVBoxLayout()
        
        # Menu de navegação
        menu_layout = QHBoxLayout()
        self.visualizar_loja_btn = QPushButton('Visualizar Loja', self)
        self.adicionar_produto_btn = QPushButton('Adicionar Produto', self)
        self.carrinho_btn = QPushButton('Carrinho', self)
        self.sair_btn = QPushButton('Sair', self)

        # Conectar os botões às funções
        self.visualizar_loja_btn.clicked.connect(self.visualizar_loja)
        self.adicionar_produto_btn.clicked.connect(self.adicionar_produto)
        self.carrinho_btn.clicked.connect(self.visualizar_carrinho)
        self.sair_btn.clicked.connect(self.sair)

        # Adicionando os botões ao menu
        menu_layout.addWidget(self.visualizar_loja_btn)
        menu_layout.addWidget(self.adicionar_produto_btn)
        menu_layout.addWidget(self.carrinho_btn)
        menu_layout.addWidget(self.sair_btn)
        
        # Layout da área principal (stacked widget)
        self.stack = QStackedWidget(self)
        self.stack.addWidget(self.create_loja_view())
        self.stack.addWidget(self.create_adicionar_produto_view())
        self.stack.addWidget(self.create_carrinho_view())
        
        # Layout final
        main_layout.addLayout(menu_layout)
        main_layout.addWidget(self.stack)
        
        self.setLayout(main_layout)
        self.show()

    def create_loja_view(self):
        # Tela para visualizar a loja (listar produtos)
        loja_widget = QWidget()
        loja_layout = QVBoxLayout()
        
        self.produtos_lista = QListWidget()
        # Exemplo de produtos listados
        self.produtos_lista.addItem("Produto 1 - R$ 50,00")
        self.produtos_lista.addItem("Produto 2 - R$ 75,00")
        self.produtos_lista.addItem("Produto 3 - R$ 100,00")
        
        loja_layout.addWidget(QLabel('Produtos Disponíveis'))
        loja_layout.addWidget(self.produtos_lista)
        
        loja_widget.setLayout(loja_layout)
        return loja_widget

    def create_adicionar_produto_view(self):
        # Tela para adicionar um novo produto
        adicionar_produto_widget = QWidget()
        adicionar_produto_layout = QVBoxLayout()
        
        # Adicionar campos para título, descrição e preço do produto
        adicionar_produto_layout.addWidget(QLabel('Título do Produto:'))
        # Aqui você pode adicionar os campos como QLineEdit para título, preço, etc.
        # Exemplo:
        self.produto_titulo_input = QLineEdit()
        adicionar_produto_layout.addWidget(self.produto_titulo_input)
        
        # Botão para adicionar o produto
        adicionar_produto_btn = QPushButton('Adicionar Produto', self)
        adicionar_produto_btn.clicked.connect(self.adicionar_produto_ao_sistema)
        adicionar_produto_layout.addWidget(adicionar_produto_btn)
        
        adicionar_produto_widget.setLayout(adicionar_produto_layout)
        return adicionar_produto_widget

    def create_carrinho_view(self):
        # Tela do carrinho de compras
        carrinho_widget = QWidget()
        carrinho_layout = QVBoxLayout()
        
        carrinho_layout.addWidget(QLabel('Carrinho de Compras'))
        self.produtos_no_carrinho = QListWidget()
        # Adicionar produtos ao carrinho (exemplo)
        self.produtos_no_carrinho.addItem("Produto 1 - R$ 50,00")
        
        carrinho_layout.addWidget(self.produtos_no_carrinho)
        
        carrinho_widget.setLayout(carrinho_layout)
        return carrinho_widget
    
    def visualizar_loja(self):
        self.stack.setCurrentIndex(0)  # Exibir a visualização da loja

    def adicionar_produto(self):
        self.stack.setCurrentIndex(1)  # Exibir a tela de adicionar produto

    def visualizar_carrinho(self):
        self.stack.setCurrentIndex(2)  # Exibir o carrinho

    def adicionar_produto_ao_sistema(self):
        # Função para adicionar o produto ao sistema (exemplo simples)
        titulo_produto = self.produto_titulo_input.text()
        if titulo_produto:
            self.produtos_lista.addItem(f"{titulo_produto} - R$ 100,00")  # Exemplo de produto adicionado
            QMessageBox.information(self, 'Produto Adicionado', 'Produto adicionado com sucesso!')
            self.produto_titulo_input.clear()  # Limpar o campo após adicionar
        else:
            QMessageBox.warning(self, 'Erro', 'Por favor, preencha o título do produto.')

    def sair(self):
        # Função para sair do sistema
        self.close()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    janela_login = JanelaLogin()  # A primeira tela que será aberta é o login
    sys.exit(app.exec())


