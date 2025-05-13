import sqlite3

def iniciar_banco():
    con = sqlite3.connect("dados.db")
    cur = con.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS produtos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        preco REAL,
        estoque INTEGER
    )""")
    cur.execute("""CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE,
        senha TEXT
    )""")
    con.commit()
    con.close()

def listar_produtos():
    con = sqlite3.connect("dados.db")
    cur = con.cursor()
    cur.execute("SELECT * FROM produtos")
    dados = cur.fetchall()
    con.close()
    return {"status": "ok", "dados": [dict(zip(["id", "nome", "preco", "estoque"], p)) for p in dados]}

def cadastrar_produto(nome, preco, estoque):
    con = sqlite3.connect("dados.db")
    cur = con.cursor()
    cur.execute("INSERT INTO produtos (nome, preco, estoque) VALUES (?, ?, ?)", (nome, preco, estoque))
    con.commit()
    con.close()
    return {"status": "ok", "mensagem": "Produto cadastrado"}

def autenticar_usuario(email, senha):
    con = sqlite3.connect("dados.db")
    cur = con.cursor()
    cur.execute("SELECT * FROM usuarios WHERE email=? AND senha=?", (email, senha))
    usuario = cur.fetchone()
    con.close()
    if usuario:
        return {"status": "ok", "dados": {"id": usuario[0], "email": usuario[1]}}
    else:
        return {"status": "erro", "mensagem": "Usuário ou senha inválidos"}
