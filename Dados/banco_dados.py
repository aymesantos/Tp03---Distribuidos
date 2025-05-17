import sqlite3

def iniciar_banco():
    con = sqlite3.connect("dados.db")
    cur = con.cursor()
    # Usuários
    cur.execute("""CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT,
        email TEXT UNIQUE,
        senha TEXT,
        tipo TEXT
    )""")
    # Lojas
    cur.execute("""CREATE TABLE IF NOT EXISTS lojas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        descricao TEXT,
        usuario_id INTEGER,
        FOREIGN KEY(usuario_id) REFERENCES usuarios(id)
    )""")
    # Produtos
    cur.execute("""CREATE TABLE IF NOT EXISTS produtos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        descricao TEXT,
        preco REAL,
        estoque INTEGER,
        loja_id INTEGER,
        FOREIGN KEY(loja_id) REFERENCES lojas(id)
    )""")
    # Compras
    cur.execute("""CREATE TABLE IF NOT EXISTS compras (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario_id INTEGER,
        data TEXT,
        status TEXT,
        FOREIGN KEY(usuario_id) REFERENCES usuarios(id)
    )""")
    # Itens da compra
    cur.execute("""CREATE TABLE IF NOT EXISTS itens_compra (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        compra_id INTEGER,
        produto_id INTEGER,
        quantidade INTEGER,
        preco_unitario REAL,
        FOREIGN KEY(compra_id) REFERENCES compras(id),
        FOREIGN KEY(produto_id) REFERENCES produtos(id)
    )""")
    # Avaliações
    cur.execute("""CREATE TABLE IF NOT EXISTS avaliacoes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario_id INTEGER,
        produto_id INTEGER,
        nota INTEGER,
        comentario TEXT,
        data TEXT,
        FOREIGN KEY(usuario_id) REFERENCES usuarios(id),
        FOREIGN KEY(produto_id) REFERENCES produtos(id)
    )""")
    con.commit()
    con.close()

def listar_produtos():
    con = sqlite3.connect("dados.db")
    cur = con.cursor()
    cur.execute("SELECT * FROM produtos")
    dados = cur.fetchall()
    con.close()
    return {"status": "ok", "dados": [dict(zip(["id", "nome", "descricao", "preco", "estoque", "loja_id"], p)) for p in dados]}

def cadastrar_produto(nome, descricao, preco, estoque, loja_id):
    con = sqlite3.connect("dados.db")
    cur = con.cursor()
    cur.execute("INSERT INTO produtos (nome, descricao, preco, estoque, loja_id) VALUES (?, ?, ?, ?, ?)", (nome, descricao, preco, estoque, loja_id))
    con.commit()
    produto_id = cur.lastrowid
    con.close()
    return {"status": "ok", "id": produto_id}

def autenticar_usuario(email, senha):
    con = sqlite3.connect("dados.db")
    cur = con.cursor()
    cur.execute("SELECT * FROM usuarios WHERE email=? AND senha=?", (email, senha))
    usuario = cur.fetchone()
    con.close()
    if usuario:
        return {"status": "ok", "usuario": {"id": usuario[0], "nome": usuario[1], "email": usuario[2], "tipo": usuario[4]}}
    else:
        return {"status": "erro", "mensagem": "Usuário ou senha inválidos"}

def cadastrar_usuario(nome, email, senha, tipo):
    con = sqlite3.connect("dados.db")
    cur = con.cursor()
    cur.execute("INSERT INTO usuarios (nome, email, senha, tipo) VALUES (?, ?, ?, ?)", (nome, email, senha, tipo))
    con.commit()
    usuario_id = cur.lastrowid
    con.close()
    return {"status": "ok", "id": usuario_id}

def buscar_usuario(usuario_id):
    con = sqlite3.connect("dados.db")
    cur = con.cursor()
    cur.execute("SELECT * FROM usuarios WHERE id=?", (usuario_id,))
    usuario = cur.fetchone()
    con.close()
    if usuario:
        return {"status": "ok", "usuario": {"id": usuario[0], "nome": usuario[1], "email": usuario[2], "tipo": usuario[4]}}
    else:
        return {"status": "erro", "mensagem": "Usuário não encontrado"}

def cadastrar_loja(nome, descricao, usuario_id):
    con = sqlite3.connect("dados.db")
    cur = con.cursor()
    cur.execute("INSERT INTO lojas (nome, descricao, usuario_id) VALUES (?, ?, ?)", (nome, descricao, usuario_id))
    con.commit()
    loja_id = cur.lastrowid
    con.close()
    return {"status": "ok", "id": loja_id}

def listar_lojas():
    con = sqlite3.connect("dados.db")
    cur = con.cursor()
    cur.execute("SELECT * FROM lojas")
    lojas = cur.fetchall()
    con.close()
    return {"status": "ok", "lojas": [dict(zip(["id", "nome", "descricao", "usuario_id"], l)) for l in lojas]}

def buscar_loja(loja_id):
    con = sqlite3.connect("dados.db")
    cur = con.cursor()
    cur.execute("SELECT * FROM lojas WHERE id=?", (loja_id,))
    loja = cur.fetchone()
    con.close()
    if loja:
        return {"status": "ok", "loja": dict(zip(["id", "nome", "descricao", "usuario_id"], loja))}
    else:
        return {"status": "erro", "mensagem": "Loja não encontrada"}

def registrar_compra(usuario_id, data, status, itens):
    con = sqlite3.connect("dados.db")
    cur = con.cursor()
    # Verifica estoque de todos os itens antes de registrar a compra
    for item in itens:
        cur.execute("SELECT estoque FROM produtos WHERE id=?", (item["produto_id"],))
        result = cur.fetchone()
        if not result:
            con.close()
            return {"status": "erro", "mensagem": f'Produto id {item["produto_id"]} não encontrado'}
        estoque_atual = result[0]
        if estoque_atual < item["quantidade"]:
            con.close()
            return {"status": "erro", "mensagem": f'Estoque insuficiente para o produto id {item["produto_id"]}'}
    # Se todos os estoques forem suficientes, registra a compra
    cur.execute("INSERT INTO compras (usuario_id, data, status) VALUES (?, ?, ?)", (usuario_id, data, status))
    compra_id = cur.lastrowid
    for item in itens:
        cur.execute("INSERT INTO itens_compra (compra_id, produto_id, quantidade, preco_unitario) VALUES (?, ?, ?, ?)", (compra_id, item["produto_id"], item["quantidade"], item["preco_unitario"]))
        cur.execute("UPDATE produtos SET estoque = estoque - ? WHERE id = ?", (item["quantidade"], item["produto_id"]))
    con.commit()
    con.close()
    return {"status": "ok", "id": compra_id}

def listar_compras_usuario(usuario_id):
    con = sqlite3.connect("dados.db")
    cur = con.cursor()
    cur.execute("SELECT * FROM compras WHERE usuario_id=?", (usuario_id,))
    compras = cur.fetchall()
    resultado = []
    for compra in compras:
        cur.execute("SELECT produto_id, quantidade, preco_unitario FROM itens_compra WHERE compra_id=?", (compra[0],))
        itens = cur.fetchall()
        resultado.append({
            "id": compra[0],
            "usuario_id": compra[1],
            "data": compra[2],
            "status": compra[3],
            "itens": [dict(zip(["produto_id", "quantidade", "preco_unitario"], i)) for i in itens]
        })
    con.close()
    return {"status": "ok", "compras": resultado}

def registrar_avaliacao(usuario_id, produto_id, nota, comentario, data):
    con = sqlite3.connect("dados.db")
    cur = con.cursor()
    cur.execute("INSERT INTO avaliacoes (usuario_id, produto_id, nota, comentario, data) VALUES (?, ?, ?, ?, ?)", (usuario_id, produto_id, nota, comentario, data))
    con.commit()
    avaliacao_id = cur.lastrowid
    con.close()
    return {"status": "ok", "id": avaliacao_id}

def listar_avaliacoes_produto(produto_id):
    con = sqlite3.connect("dados.db")
    cur = con.cursor()
    cur.execute("SELECT * FROM avaliacoes WHERE produto_id=?", (produto_id,))
    avaliacoes = cur.fetchall()
    con.close()
    return {"status": "ok", "avaliacoes": [dict(zip(["id", "usuario_id", "produto_id", "nota", "comentario", "data"], a)) for a in avaliacoes]}
