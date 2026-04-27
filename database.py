import os
import sqlite3
from datetime import datetime
from config import DB_NAME

# Caminho do banco
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, DB_NAME)

def conectar():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row 
    return conn

# --- ARQUIVO: .\database.py ---

def criar_tabela():
    """Cria a estrutura inicial do banco de dados"""
    conn = conectar()
    cursor = conn.cursor()
    
    # 1. Tabela de Personagens
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS personagens (
            id INTEGER PRIMARY KEY AUTOINCREMENT, 
            user_id INTEGER,
            nick TEXT UNIQUE,
            genero TEXT,
            senha TEXT,
            gold INTEGER DEFAULT 100,
            jogo_iniciado INTEGER DEFAULT 0,
            level INTEGER DEFAULT 1,
            xp INTEGER DEFAULT 0,
            vida INTEGER DEFAULT 100,
            vida_max INTEGER DEFAULT 100,
            ataque INTEGER DEFAULT 10,
            defesa INTEGER DEFAULT 5,
            sorte INTEGER DEFAULT 1,
            pet_nome TEXT,
            pet_vida INTEGER,
            pet_ataque INTEGER,
            pet_defesa INTEGER,
            pet_agilidade INTEGER,
            pet_xp INTEGER DEFAULT 0,
            pet_level INTEGER DEFAULT 1,
            ultimo_login TEXT,
            pet_imagem TEXT,
            mapa_atual INTEGER DEFAULT 0,
            mithril INTEGER DEFAULT 0,
            mochila_slots INTEGER DEFAULT 10
        )
    ''')

    # 2. Tabela de Inventário
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS inventario (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            item_nome TEXT,
            quantidade INTEGER DEFAULT 1,
            tipo TEXT,
            FOREIGN KEY(user_id) REFERENCES personagens(user_id)
        )
    ''')

    # 3. Tabela Mestre de Itens
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS itens_mestre (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT UNIQUE,
            tipo TEXT,
            subtipo TEXT,
            valor_efeito INTEGER DEFAULT 0,
            descricao TEXT,
            preco_gold INTEGER DEFAULT 0
        )
    ''')

    # 4. Tabela Mestre de Monstros
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS monstros_mestre (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT UNIQUE,
            mapa_id INTEGER,
            vida INTEGER,
            ataque INTEGER,
            defesa INTEGER,
            xp_recompensa INTEGER,
            gold_recompensa INTEGER,
            imagem TEXT
        )
    ''')

    # 5. Tabela de Drops (RECRIAÇÃO FORÇADA)
    # Se a tabela existir mas estiver errada, o atualizar_estrutura_banco vai resolver.
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS drops_monstros (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            monstro_nome TEXT,
            item_nome TEXT,
            chance INTEGER,
            qtd_min INTEGER DEFAULT 1,
            qtd_max INTEGER DEFAULT 1
        )
    ''')
    
    conn.commit()
    conn.close()
    

# --- ARQUIVO: .\database.py ---

def popular_dados_iniciais():
    """Popula o banco com o bestiário expandido e novos drops"""
    conn = conectar()
    cursor = conn.cursor()

    # 1. ITENS MESTRE (Catálogo)
    itens = [
        ('Poção Pequena', 'consumivel', 'cura', 20, 'Recupera 20% da vida.', 50),
        ('Poção Média', 'consumivel', 'cura', 50, 'Recupera 50% da vida.', 150),
        ('Poção Grande', 'consumivel', 'cura', 85, 'Recupera 85% da vida.', 300),
        ('Maçã', 'consumivel', 'pet', 10, 'Dá XP ao seu pet.', 20),
        ('Espada de Madeira', 'equipamento', 'arma', 5, 'Uma espada simples (+5 Atq).', 100),
        ('Armadura de Couro', 'equipamento', 'armadura', 3, 'Proteção básica (+3 Def).', 120),
        ('Osso Antigo', 'material', 'venda', 0, 'Um osso velho que pode ser vendido.', 15),
        ('Essência Mágica', 'material', 'venda', 0, 'Fragmento de energia pura.', 50)
    ]
    cursor.executemany("""
        INSERT OR IGNORE INTO itens_mestre (nome, tipo, subtipo, valor_efeito, descricao, preco_gold) 
        VALUES (?, ?, ?, ?, ?, ?)
    """, itens)

    # 2. MONSTROS MESTRE (Expandido para os Mapas 1 a 8)
    # Formato: (Nome, Mapa_ID, Vida, Ataque, Defesa, XP, Gold, Imagem)
    monstros = [
        # MAPA 1: Acampamento do Pioneiro (Lvl 1)
        ('Barata', 1, 30, 6, 2, 15, 10, 'barata.png'),
        ('Aranha', 1, 45, 9, 3, 25, 20, 'aranha.png'),
        ('Centopéia', 1, 35, 7, 2, 18, 12, 'centopeia.png'),

        # MAPA 2: Bosque Queimado (Lvl 4)
        ('Esqueleto Carbonizado', 2, 70, 15, 6, 45, 35, 'esqueleto.png'),
        ('Lobo de Fogo', 2, 85, 18, 5, 55, 45, 'lobo_fogo.png'),
        ('Espírito das Cinzas', 2, 60, 22, 2, 50, 40, 'espirito_cinzas.png'),

        # MAPA 3: Ponte dos Suspiros (Lvl 6)
        ('Fantasma Errante', 3, 100, 25, 8, 80, 60, 'fantasma.png'),
        ('Gárgula de Pedra', 3, 150, 20, 15, 95, 75, 'gargula.png'),

        # MAPA 4: Tumba do Caçador Ancião (Lvl 8)
        ('Zumbi Reanimado', 4, 180, 30, 12, 130, 100, 'zumbi.png'),
        ('Sombra Faminta', 4, 140, 45, 5, 150, 120, 'sombra.png'),

        # MAPA 5: Cachoeira da Serenidade (Lvl 10)
        ('Naga Guerreira', 5, 250, 40, 20, 200, 180, 'naga.png'),
        ('Caranguejo Blindado', 5, 350, 30, 35, 220, 190, 'caranguejo.png'),

        # MAPA 6: Desfiladeiro do Eco (Lvl 12)
        ('Wyvern Jovem', 6, 400, 60, 25, 350, 300, 'wyvern.png'),
        ('Harpias Famintas', 6, 300, 75, 15, 320, 280, 'harpia.png'),

        # MAPA 7: Pico do Observador (Lvl 14)
        ('Gigante da Montanha', 7, 800, 90, 50, 600, 550, 'gigante.png'),
        ('Elemental do Ar', 7, 500, 120, 20, 650, 600, 'elemental.ar.png'),

        # MAPA 8: Portal das Montanhas (Lvl 16)
        ('Guardião do Portal', 8, 1200, 150, 80, 1200, 1000, 'guardiao.png'),
        ('Quimera Infernal', 8, 1000, 180, 60, 1500, 1200, 'quimera.png')
    ]
    cursor.executemany("""
        INSERT OR IGNORE INTO monstros_mestre (nome, mapa_id, vida, ataque, defesa, xp_recompensa, gold_recompensa, imagem) 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, monstros)

    # 3. DROPS (Definindo recompensas para os novos monstros)
    # Formato: (Monstro, Item, Chance, Min, Max)
    drops = [
        # Drops Mapa 1
        ('Barata', 'Maçã', 40, 1),
        ('Aranha', 'Poção Pequena', 25, 1),
        ('Centopéia', 'Maçã', 30, 1),

        # Drops Mapa 2
        ('Esqueleto Carbonizado', 'Osso Antigo', 60, 1),
        ('Lobo de Fogo', 'Poção Pequena', 30, 1),
        ('Espírito das Cinzas', 'Essência Mágica', 15, 1),

        # Drops Mapa 3
        ('Fantasma Errante', 'Essência Mágica', 40, 1),
        ('Gárgula de Pedra', 'Poção Média', 20, 1),

        # Drops Mapas Superiores (Exemplos)
        ('Zumbi Reanimado', 'Poção Média', 40, 1),
        ('Naga Guerreira', 'Poção Grande', 15, 1),
        ('Guardião do Portal', 'Poção Grande', 100, 1)
    ]
    cursor.executemany("""
        INSERT OR IGNORE INTO drops_monstros (monstro_nome, item_nome, chance, qtd_min) 
        VALUES (?, ?, ?, ?)
    """, drops)

    conn.commit()
    conn.close()
    print("✅ Bestiário e Catálogo de itens atualizados com sucesso!")
    
    
    
def get_monstro_aleatorio(mapa_id):
    """Busca um monstro aleatório do mapa específico no banco de dados"""
    conn = conectar()
    cursor = conn.cursor()
    # ORDER BY RANDOM() é uma forma eficiente do SQLite sortear uma linha
    cursor.execute("SELECT * FROM monstros_mestre WHERE mapa_id = ? ORDER BY RANDOM() LIMIT 1", (mapa_id,))
    monstro = cursor.fetchone()
    conn.close()
    return monstro

def get_drops_monstro(monstro_nome):
    """Busca todos os itens que um monstro específico pode dropar"""
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM drops_monstros WHERE monstro_nome = ?", (monstro_nome,))
    drops = cursor.fetchall()
    conn.close()
    return drops

    

def salvar_personagem(telegram_id, nick, genero, senha):
    conn = conectar()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO personagens (user_id, nick, genero, senha)
            VALUES (?, ?, ?, ?)
        """, (telegram_id, nick, genero, senha))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def reivindicar_login_diario(nick):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT ultimo_login, gold FROM personagens WHERE nick = ?", (nick,))
    resultado = cursor.fetchone()
    
    if not resultado:
        conn.close()
        return False, "❌ Personagem não encontrado."

    data_ultimo = resultado['ultimo_login']
    gold_atual = resultado['gold']
    hoje = datetime.now().strftime("%Y-%m-%d")

    if data_ultimo == hoje:
        conn.close()
        return False, "❌ Você já resgatou seu bônus hoje!"

    novo_gold = gold_atual + 100
    cursor.execute("UPDATE personagens SET gold = ?, ultimo_login = ? WHERE nick = ?", (novo_gold, hoje, nick))
    conn.commit()
    conn.close()
    return True, f"✅ Bônus resgatado! Gold atual: {novo_gold}"

def get_jogador(user_id):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM personagens WHERE user_id = ?", (user_id,))
    jogador = cursor.fetchone()
    conn.close()
    return jogador

def buscar_personagem_por_nick(nick):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM personagens WHERE nick = ?", (nick,))
    jogador = cursor.fetchone()
    conn.close()
    return jogador

def atualizar_mapa_personagem(user_id, mapa_id):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("UPDATE personagens SET mapa_atual = ? WHERE user_id = ?", (mapa_id, user_id))
    conn.commit()
    conn.close()

def resetar_localizacao(user_id):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("UPDATE personagens SET mapa_atual = 0 WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()

# --- ARQUIVO: .\database.py ---

def atualizar_estrutura_banco():
    """Corrige colunas faltantes e resolve problemas de compatibilidade"""
    conn = conectar()
    cursor = conn.cursor()
    
    # Adicionar colunas na tabela personagens caso não existam
    colunas_personagens = [
        ("vida_max", "INTEGER DEFAULT 100"),
        ("pet_xp", "INTEGER DEFAULT 0"),
        ("pet_level", "INTEGER DEFAULT 1"),
        ("mochila_slots", "INTEGER DEFAULT 10")
    ]
    
    for nome, tipo in colunas_personagens:
        try:
            cursor.execute(f"ALTER TABLE personagens ADD COLUMN {nome} {tipo}")
        except sqlite3.OperationalError:
            pass

    # --- RESET DA TABELA DE DROPS SE ESTIVER ERRADA ---
    # Vamos verificar se a coluna monstro_nome existe. Se não, deletamos e criamos de novo.
    cursor.execute("PRAGMA table_info(drops_monstros)")
    colunas = [col[1] for col in cursor.fetchall()]
    
    if "monstro_nome" not in colunas and len(colunas) > 0:
        print("⚠️ Corrigindo tabela drops_monstros...")
        cursor.execute("DROP TABLE drops_monstros")
        cursor.execute('''
            CREATE TABLE drops_monstros (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                monstro_nome TEXT,
                item_nome TEXT,
                chance INTEGER,
                qtd_min INTEGER DEFAULT 1,
                qtd_max INTEGER DEFAULT 1
            )
        ''')
            
    conn.commit()
    conn.close()
    
    
# Mantive as funções de debug para você usar se precisar
def debug_tabela():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(personagens)")
    print("COLUNAS:", cursor.fetchall())
    conn.close()
    
    
def subir_de_nivel(user_id):
    """Aumenta o nível e melhora os atributos, expandindo a Vida Máxima"""
    conn = conectar()
    cursor = conn.cursor()
    
    # 1. Busca os dados atuais (incluindo a nova coluna vida_max)
    cursor.execute("SELECT level, xp, vida, vida_max, ataque, defesa FROM personagens WHERE user_id = ?", (user_id,))
    jogador = cursor.fetchone()
    
    if jogador:
        lvl_atual = jogador['level']
        xp_atual = jogador['xp']
        xp_necessario = calcular_xp_necessario(lvl_atual)
        
        # Cálculos de upgrade
        novo_lvl = lvl_atual + 1
        sobra_xp = max(0, xp_atual - xp_necessario)
        
        # Aumentamos o LIMITE de vida (vida_max)
        nova_vida_max = jogador['vida_max'] + 20 
        
        # Restauramos a vida atual para o novo máximo (Cura completa no Level Up)
        nova_vida_atual = nova_vida_max 
        
        novo_atq = jogador['ataque'] + 2  
        nova_def = jogador['defesa'] + 1  
        
        # 2. Atualiza o banco com as novas colunas
        cursor.execute("""
            UPDATE personagens 
            SET level = ?, xp = ?, vida = ?, vida_max = ?, ataque = ?, defesa = ? 
            WHERE user_id = ?
        """, (novo_lvl, sobra_xp, nova_vida_atual, nova_vida_max, novo_atq, nova_def, user_id))
        
        conn.commit()
        conn.close()
        
        return {
            "level": novo_lvl,
            "vida_max": nova_vida_max,
            "ataque": novo_atq,
            "defesa": nova_def
        }
    
    conn.close()
    return None


def adicionar_item_inventario(user_id, item_nome, tipo, qtd=1):
    """Adiciona um item. Se for consumível, não ocupa slot de mochila."""
    conn = conectar()
    cursor = conn.cursor()

    # 1. Verifica se o jogador já tem esse item (para empilhar/stack)
    cursor.execute(
        "SELECT quantidade FROM inventario WHERE user_id = ? AND item_nome = ?", 
        (user_id, item_nome)
    )
    item_existente = cursor.fetchone()

    if item_existente:
        # Se já existe, apenas aumentamos a quantidade (independente do tipo)
        nova_qtd = item_existente['quantidade'] + qtd
        cursor.execute(
            "UPDATE inventario SET quantidade = ? WHERE user_id = ? AND item_nome = ?",
            (nova_qtd, user_id, item_nome)
        )
        conn.commit()
        conn.close()
        return True, "Item empilhado!"

    # 2. SE O ITEM É NOVO:
    # Se for CONSUMÍVEL, ele entra direto, sem checar limite de slots
    if tipo == 'consumivel':
        cursor.execute(
            "INSERT INTO inventario (user_id, item_nome, tipo, quantidade) VALUES (?, ?, ?, ?)",
            (user_id, item_nome, tipo, qtd)
        )
        conn.commit()
        conn.close()
        return True, "Consumível adicionado!"

    # 3. SE NÃO FOR CONSUMÍVEL (Equipamentos, Ovos, etc): Checa limite
    # Contamos apenas itens que NÃO são consumíveis
    cursor.execute(
        "SELECT COUNT(*) as total FROM inventario WHERE user_id = ? AND tipo != 'consumivel'", 
        (user_id,)
    )
    total_ocupado = cursor.fetchone()['total']

    cursor.execute("SELECT mochila_slots FROM personagens WHERE user_id = ?", (user_id,))
    limite = cursor.fetchone()['mochila_slots']

    if total_ocupado >= limite:
        conn.close()
        return False, "Mochila de equipamentos cheia!"

    # Se tem espaço, adiciona o item de slot
    cursor.execute(
        "INSERT INTO inventario (user_id, item_nome, tipo, quantidade) VALUES (?, ?, ?, ?)",
        (user_id, item_nome, tipo, qtd)
    )
    conn.commit()
    conn.close()
    return True, "Equipamento adicionado!"

def get_inventario(user_id):
    """Busca todos os itens que o jogador possui na mochila"""
    conn = conectar()
    cursor = conn.cursor()
    
    # Buscamos o nome, a quantidade e o tipo de cada item do usuário
    cursor.execute(
        "SELECT item_nome, quantidade, tipo FROM inventario WHERE user_id = ?", 
        (user_id,)
    )
    itens = cursor.fetchall() # fetchall() traz a lista completa
    
    conn.close()
    return itens

def calcular_xp_necessario(level):
    """Calcula quanto XP o jogador precisa para sair do level atual e ir para o próximo"""
    # Lvl 1: 100 XP
    # Lvl 2: 100 + (1 * 150) = 250 XP
    # Lvl 3: 100 + (2 * 150) = 400 XP...
    return 100 + (level - 1) * 150

def usar_pocao_cura(user_id, item_nome, cura_quantidade):
    """Diminui o item da mochila e cura o jogador"""
    conn = conectar()
    cursor = conn.cursor()

    # 1. Busca vida atual e máxima
    cursor.execute("SELECT vida, vida_max FROM personagens WHERE user_id = ?", (user_id,))
    jogador = cursor.fetchone()

    # 2. Busca o item (ignora maiúsculas no SQL)
    cursor.execute(
        "SELECT quantidade, item_nome FROM inventario WHERE user_id = ? AND item_nome = ? COLLATE NOCASE", 
        (user_id, item_nome)
    )
    item = cursor.fetchone()

    if not item:
        conn.close()
        return False, "Você não possui este item!"

    if jogador['vida'] >= jogador['vida_max']:
        conn.close()
        return False, "Sua vida já está cheia!"

    # 3. Consome o item
    nome_real = item['item_nome']
    if item['quantidade'] > 1:
        cursor.execute("UPDATE inventario SET quantidade = quantidade - 1 WHERE user_id = ? AND item_nome = ?", (user_id, nome_real))
    else:
        cursor.execute("DELETE FROM inventario WHERE user_id = ? AND item_nome = ?", (user_id, nome_real))

    # 4. Aplica a cura
    nova_vida = min(jogador['vida'] + cura_quantidade, jogador['vida_max'])
    cursor.execute("UPDATE personagens SET vida = ? WHERE user_id = ?", (nova_vida, user_id))

    conn.commit()
    conn.close()
    return True, f"Curado! ❤️ {nova_vida}/{jogador['vida_max']}"


def calcular_xp_pet(level):
    """Calcula o XP necessário para o próximo nível do pet"""
    # Lvl 1: 50 | Lvl 2: 100 | Lvl 3: 150...
    return 50 + (level - 1) * 200

def dar_xp_pet(user_id, item_nome, xp_por_unidade, qtd):
    """Dá XP ao Pet e processa level ups com custo progressivo"""
    conn = conectar()
    cursor = conn.cursor()

    # 1. Busca os dados atuais
    cursor.execute("""
        SELECT pet_nome, pet_xp, pet_level, pet_vida, pet_ataque, pet_defesa, pet_agilidade 
        FROM personagens WHERE user_id = ?
    """, (user_id,))
    jogador = cursor.fetchone()

    if not jogador or not jogador['pet_nome']:
        conn.close()
        return False, "Você ainda não possui um pet."

    # 2. Verifica estoque
    cursor.execute("SELECT quantidade FROM inventario WHERE user_id = ? AND item_nome = ?", (user_id, item_nome))
    item = cursor.fetchone()
    
    if not item or item['quantidade'] < qtd:
        conn.close()
        return False, f"Você não tem {qtd}x {item_nome}."

    # 3. Consome itens
    if item['quantidade'] > qtd:
        cursor.execute("UPDATE inventario SET quantidade = quantidade - ? WHERE user_id = ? AND item_nome = ?", (qtd, user_id, item_nome))
    else:
        cursor.execute("DELETE FROM inventario WHERE user_id = ? AND item_nome = ?", (user_id, item_nome))

    # 4. Lógica de XP Progressivo
    xp_ganho_total = xp_por_unidade * qtd
    novo_xp = (jogador['pet_xp'] or 0) + xp_ganho_total
    novo_lvl = jogador['pet_level'] if jogador['pet_level'] else 1
    
    n_vida, n_atq, n_def, n_agi = jogador['pet_vida'], jogador['pet_ataque'], jogador['pet_defesa'], jogador['pet_agilidade']
    
    levels_ganhos = 0
    # O custo (threshold) agora muda a cada nível que o pet sobe
    while True:
        xp_necessario = calcular_xp_pet(novo_lvl)
        if novo_xp >= xp_necessario:
            novo_xp -= xp_necessario
            novo_lvl += 1
            levels_ganhos += 1
            n_vida += 1; n_atq += 1; n_def += 1; n_agi += 1
        else:
            break

    cursor.execute("""
        UPDATE personagens 
        SET pet_xp = ?, pet_level = ?, pet_vida = ?, pet_ataque = ?, pet_defesa = ?, pet_agilidade = ?
        WHERE user_id = ?
    """, (novo_xp, novo_lvl, n_vida, n_atq, n_def, n_agi, user_id))

    conn.commit()
    conn.close()
    
    msg = f"Seu pet ganhou {xp_ganho_total} de XP! ✨"
    if levels_ganhos > 0:
        msg += f"\n\n🌟 EVOLUÇÃO! Subiu {levels_ganhos} nível(is)! (Agora Lvl {novo_lvl})"
    
    return True, msg


# --- ARQUIVO: .\database.py ---

def set_level_admin(nick, novo_lvl):
    """Força um nível específico e escala os atributos proporcionalmente para testes"""
    conn = conectar()
    cursor = conn.cursor()
    
    # Cálculos baseados na progressão do jogo:
    # Vida: 100 + 20 por nível extra
    nova_vida_max = 100 + (novo_lvl - 1) * 20
    # Ataque: 10 + 2 por nível extra
    novo_atq = 10 + (novo_lvl - 1) * 2
    # Defesa: 5 + 1 por nível extra
    nova_def = 5 + (novo_lvl - 1) * 1
    
    try:
        cursor.execute("""
            UPDATE personagens 
            SET level = ?, xp = 0, vida = ?, vida_max = ?, ataque = ?, defesa = ? 
            WHERE nick = ?
        """, (novo_lvl, nova_vida_max, nova_vida_max, novo_atq, nova_def, nick))
        
        sucesso = cursor.rowcount > 0 # Verifica se algum nick foi alterado
        conn.commit()
        return sucesso
    except Exception as e:
        print(f"Erro ao definir nível: {e}")
        return False
    finally:
        conn.close()


