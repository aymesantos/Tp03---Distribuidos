from banco_dados import iniciar_banco
import sqlite3
import os

if __name__ == "__main__":
    iniciar_banco()
    print("Banco de dados e tabelas criados com sucesso!")

    DB_PATH = os.path.join(os.path.dirname(__file__), "dados.db")
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()

    # Inserir usuários
    cur.execute("INSERT INTO usuarios (nome, email, senha, tipo) VALUES (?, ?, ?, ?)", ("Harry Potter", "harry@hogwarts.com", "senha123", "cliente"))
    cur.execute("INSERT INTO usuarios (nome, email, senha, tipo) VALUES (?, ?, ?, ?)", ("Hermione Granger", "hermione@hogwarts.com", "senha123", "cliente"))
    cur.execute("INSERT INTO usuarios (nome, email, senha, tipo) VALUES (?, ?, ?, ?)", ("Loja do Dumbledore", "dumbledore@hogwarts.com", "senha123", "vendedor"))

    # Inserir loja
    cur.execute("INSERT INTO lojas (nome, descricao, usuario_id) VALUES (?, ?, ?)", ("Beco Diagonal", "Loja de artigos mágicos", 3))

    # Inserir produtos (com categoria)
    cur.execute("INSERT INTO produtos (nome, descricao, preco, estoque, loja_id, categoria) VALUES (?, ?, ?, ?, ?, ?)", ("Varinha de Sabugueiro", "A varinha mais poderosa do mundo.", 150.0, 10, 1, "Varinhas"))
    cur.execute("INSERT INTO produtos (nome, descricao, preco, estoque, loja_id, categoria) VALUES (?, ?, ?, ?, ?, ?)", ("Capa da Invisibilidade", "Fique invisível quando quiser.", 200.0, 5, 1, "Vestes"))
    cur.execute("INSERT INTO produtos (nome, descricao, preco, estoque, loja_id, categoria) VALUES (?, ?, ?, ?, ?, ?)", ("Livro de Poções Avançadas", "Receitas de poções para N.I.E.M.s.", 80.0, 7, 1, "Livros"))

    con.commit()
    con.close()
    print("Dados de exemplo inseridos com sucesso!") 