import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "dados.db")

def iniciar_banco():
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    # Usuários
    cur.execute("""CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT,
        email TEXT UNIQUE,
        senha TEXT,
        tipo TEXT,
        casa TEXT
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
        categoria TEXT,
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
    # Carrinho
    cur.execute("""CREATE TABLE IF NOT EXISTS carrinho (
        email TEXT,
        produto_id INTEGER,
        quantidade INTEGER,
        PRIMARY KEY (email, produto_id),
        FOREIGN KEY(produto_id) REFERENCES produtos(id)
    )""")
    con.commit()
    con.close()

def listar_produtos_db(param=None):
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.execute("SELECT * FROM produtos WHERE estoque > 0")
    dados = cur.fetchall()
    con.close()
    return {"status": "ok", "dados": [dict(zip(["id", "nome", "descricao", "preco", "estoque", "loja_id", "categoria"], p)) for p in dados]}

def cadastrar_produto_db(nome, descricao, preco, estoque, loja_id, categoria):
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.execute("INSERT INTO produtos (nome, descricao, preco, estoque, loja_id, categoria) VALUES (?, ?, ?, ?, ?, ?)", (nome, descricao, preco, estoque, loja_id, categoria))
    con.commit()
    produto_id = cur.lastrowid
    con.close()
    return {"status": "ok", "id": produto_id}

def autenticar_usuario(email, senha):
    print(f"[DEBUG] Tentando autenticar: email={email}, senha={senha}")
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.execute("SELECT * FROM usuarios WHERE email=? AND senha=?", (email, senha))
    usuario = cur.fetchone()
    print(f"[DEBUG] Resultado da consulta: {usuario}")
    con.close()
    if usuario:
        print(f"[DEBUG] Usuário autenticado com sucesso: {usuario}")
        return {"status": "ok", "usuario": {"id": usuario[0], "nome": usuario[1], "email": usuario[2], "tipo": usuario[4]}}
    else:
        print("[DEBUG] Usuário ou senha inválidos")
        return {"status": "erro", "mensagem": "Usuário ou senha inválidos"}

def cadastrar_usuario(nome, email, senha, tipo, casa):
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.execute("INSERT INTO usuarios (nome, email, senha, tipo, casa) VALUES (?, ?, ?, ?, ?)", (nome, email, senha, tipo, casa))
    con.commit()
    usuario_id = cur.lastrowid
    con.close()
    return {"status": "ok", "id": usuario_id}

def buscar_usuario(usuario_id):
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.execute("SELECT * FROM usuarios WHERE id=?", (usuario_id,))
    usuario = cur.fetchone()
    con.close()
    if usuario:
        return {"status": "ok", "usuario": {"id": usuario[0], "nome": usuario[1], "email": usuario[2], "tipo": usuario[4], "casa": usuario[5]}}
    else:
        return {"status": "erro", "mensagem": "Usuário não encontrado"}

def cadastrar_loja_db(nome, descricao, usuario_id):
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.execute("INSERT INTO lojas (nome, descricao, usuario_id) VALUES (?, ?, ?)", (nome, descricao, usuario_id))
    con.commit()
    loja_id = cur.lastrowid
    con.close()
    return {"status": "ok", "id": loja_id}

def listar_lojas_db(param=None):
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.execute("SELECT * FROM lojas")
    lojas = cur.fetchall()
    con.close()
    return {"status": "ok", "lojas": [dict(zip(["id", "nome", "descricao", "usuario_id"], l)) for l in lojas]}

def buscar_loja(loja_id):
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.execute("SELECT * FROM lojas WHERE id=?", (loja_id,))
    loja = cur.fetchone()
    con.close()
    if loja:
        return {"status": "ok", "loja": dict(zip(["id", "nome", "descricao", "usuario_id"], loja))}
    else:
        return {"status": "erro", "mensagem": "Loja não encontrada"}

def registrar_compra(usuario_id, data, status, itens):
    con = sqlite3.connect(DB_PATH)
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
    con = sqlite3.connect(DB_PATH)
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
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.execute("INSERT INTO avaliacoes (usuario_id, produto_id, nota, comentario, data) VALUES (?, ?, ?, ?, ?)", (usuario_id, produto_id, nota, comentario, data))
    con.commit()
    avaliacao_id = cur.lastrowid
    con.close()
    return {"status": "ok", "id": avaliacao_id}

def listar_avaliacoes_produto(produto_id):
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.execute("SELECT * FROM avaliacoes WHERE produto_id=?", (produto_id,))
    avaliacoes = cur.fetchall()
    con.close()
    return {"status": "ok", "avaliacoes": [dict(zip(["id", "usuario_id", "produto_id", "nota", "comentario", "data"], a)) for a in avaliacoes]}

def listar_vendas_vendedor(usuario_id):
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    # Buscar lojas do vendedor
    cur.execute("SELECT id FROM lojas WHERE usuario_id=?", (usuario_id,))
    lojas = [row[0] for row in cur.fetchall()]
    if not lojas:
        con.close()
        return {"status": "ok", "vendas": []}
    # Buscar produtos dessas lojas
    cur.execute(f"SELECT id FROM produtos WHERE loja_id IN ({','.join(['?']*len(lojas))})", lojas)
    produtos = [row[0] for row in cur.fetchall()]
    if not produtos:
        con.close()
        return {"status": "ok", "vendas": []}
    # Buscar itens vendidos desses produtos
    cur.execute(f"SELECT compra_id, produto_id, quantidade, preco_unitario FROM itens_compra WHERE produto_id IN ({','.join(['?']*len(produtos))})", produtos)
    itens = cur.fetchall()
    vendas = []
    for compra_id, produto_id, quantidade, preco_unitario in itens:
        # Buscar dados da compra
        cur.execute("SELECT usuario_id, data, status FROM compras WHERE id=?", (compra_id,))
        compra = cur.fetchone()
        if compra:
            vendas.append({
                "compra_id": compra_id,
                "produto_id": produto_id,
                "quantidade": quantidade,
                "preco_unitario": preco_unitario,
                "cliente_id": compra[0],
                "data": compra[1],
                "status": compra[2]
            })
    con.close()
    return {"status": "ok", "vendas": vendas}

def editar_produto(produto_id, nome, descricao, preco, estoque):
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.execute("UPDATE produtos SET nome=?, descricao=?, preco=?, estoque=? WHERE id=?", (nome, descricao, preco, estoque, produto_id))
    con.commit()
    con.close()
    return {"status": "ok"}

def adicionar_produto_carrinho(email, produto_id, quantidade=1):
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    # Verifica se já existe o produto no carrinho
    cur.execute("SELECT quantidade FROM carrinho WHERE email=? AND produto_id=?", (email, produto_id))
    row = cur.fetchone()
    if row:
        # Atualiza para a quantidade escolhida
        cur.execute("UPDATE carrinho SET quantidade = ? WHERE email=? AND produto_id=?", (quantidade, email, produto_id))
    else:
        cur.execute("INSERT INTO carrinho (email, produto_id, quantidade) VALUES (?, ?, ?)", (email, produto_id, quantidade))
    con.commit()
    con.close()
    return {"status": "ok"}

def visualizar_carrinho(email):
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.execute("SELECT produto_id, quantidade FROM carrinho WHERE email=?", (email,))
    itens = cur.fetchall()
    con.close()
    return {"status": "ok", "carrinho": [{"produto_id": pid, "quantidade": qtd} for pid, qtd in itens]}

def remover_produto_carrinho(email, produto_id=None):
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    if produto_id is None:
        cur.execute("DELETE FROM carrinho WHERE email=?", (email,))
    else:
        cur.execute("DELETE FROM carrinho WHERE email=? AND produto_id=?", (email, produto_id))
    con.commit()
    con.close()
    return {"status": "ok"}

def buscar_usuario_por_email(email):
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.execute("SELECT * FROM usuarios WHERE email=?", (email,))
    usuario = cur.fetchone()
    con.close()
    if usuario:
        return {"status": "ok", "usuario": {"id": usuario[0], "nome": usuario[1], "email": usuario[2], "tipo": usuario[4], "casa": usuario[5]}}
    else:
        return {"status": "erro", "mensagem": "Usuário não encontrado"}
