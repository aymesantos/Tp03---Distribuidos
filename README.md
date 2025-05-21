# 🧙‍♂️ BecoDiagonal

**BecoDiagonal** é um marketplace especializado na compra e venda de produtos mágicos, voltado para a comunidade bruxa.  
Inspirado no universo de Harry Potter, o sistema permite que usuários cadastrados criem suas próprias lojas, anunciem produtos e realizem transações de forma simplificada e segura.

O marketplace oferece categorias específicas de produtos mágicos, incluindo poções, varinhas, livros de magia, acessórios encantados e criaturas mágicas, promovendo a interação entre compradores e vendedores.

---

## ⚙️ Tecnologias Utilizadas

- Linguagem Python  
- PyQt6 para a interface gráfica  
- API de sockets TCP para comunicação cliente-servidor  
- Banco de dados SQLite para armazenamento  

---

## 📋 Requisitos Funcionais

O sistema possui os seguintes requisitos principais:

- **RF001**: Cadastro de usuário com nome, casa de Hogwarts, email, senha e tipo de bruxo (nasceu trouxa, bruxo ou aborto).  
- **RF002**: Login com email e senha.  
- **RF003**: Nome de usuário deve conter apenas letras e números, 3 a 20 caracteres, com pelo menos uma letra.  
- **RF004**: Senha com no mínimo 8 caracteres (letras e números).  
- **RF005**: Visualização da loja e itens listados.  
- **RF006**: Cada loja gerida por um vendedor, podendo adicionar múltiplos itens.  
- **RF007**: Criação e personalização de loja (nome, descrição, categoria).  
- **RF008**: Edição das informações da loja.  
- **RF009**: Criação de anúncios de produtos com título, descrição e preço.  
- **RF010**: Ativar, pausar ou desativar anúncios a qualquer momento.  
- **RF011**: Visualização detalhada dos anúncios.  
- **RF012**: Compra de produtos, carrinho de compras e finalização do pagamento.  
- **RF013**: Gerenciamento do status dos produtos (vendido, disponível, pausado).  
- **RF014**: Histórico de compras e vendas detalhado.  
- **RF015**: Pagamento em galeões, moeda mágica do sistema.  

---

## 🏗️ Estrutura e Desenvolvimento

O BecoDiagonal foi desenvolvido usando uma arquitetura em camadas, dividindo o sistema em partes físicas e lógicas para melhor organização e manutenção:

- **Camadas Físicas:**  
  - **Cliente:** Interface gráfica em Python com PyQt6, onde o usuário interage.  
  - **Servidor de Aplicação:** Gerencia comunicação e regras de negócio (arquivo `servidor.py`).  
  - **Servidor de Dados:** Gerencia o banco de dados SQLite e responde às consultas (arquivo `servidor_dados.py`).  

- **Camadas Lógicas:**  
  - Apresentação (interface com o usuário)  
  - Negócio (regras do sistema)  
  - Plataforma (infraestrutura e dados)  

### Organização dos Arquivos

- `/cliente/` - Código do cliente e interface gráfica (ex: `clienteGUI.py`)  
- `/servidor/` - Código do servidor de aplicação (`servidor.py`)  
- `/Dados/` - Código do servidor de dados (`servidor_dados.py`)  

---

## 🚀 Como Executar

### Pré-requisitos

- Python 3 instalado na máquina  
- Biblioteca PyQt6 instalada (instale com `pip install PyQt6`)

### Passos para execução

1. Abra o terminal.
2. Navegue até a pasta principal do projeto
3. Execute o comando:

   ```bash
   make
   ```

Isso iniciará a aplicação automaticamente.

---

## 🎯 Funcionalidades Principais

O sistema está dividido em quatro áreas funcionais:

* **Gestão de Usuários:** Cadastro, login, perfil (com nome, casa e tipo de bruxo).
* **Gestão de Lojas:** Criação, visualização e personalização das lojas mágicas.
* **Gestão de Produtos:** Criação, edição, ativação/desativação e listagem de produtos com categorias.
* **Sistema de Compras:** Carrinho, finalização de compra com pagamento em galeões e histórico de transações.


## 📚 Sobre o Projeto

Este trabalho foi desenvolvido para a disciplina de Sistemas Distribuídos da faculdade. Ele aborda a comunicação via sockets TCP, arquitetura cliente-servidor e desenvolvimento de interfaces gráficas em Python com PyQt6, além do uso de banco de dados SQLite para persistência de dados.



