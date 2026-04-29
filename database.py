import os
import sqlite3
from datetime import datetime
from config import DB_NAME
from modelos.itens import LISTA_ITENS_MESTRE
from modelos.inimigos import LISTA_MONSTROS_MESTRE, LISTA_DROPS_MAPAS

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
            defesa INTEGER DEFAULT 10,
            sorte INTEGER DEFAULT 1,
            pet_equipado INTEGER DEFAULT 0,
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

    # Atualizando a tabela de drops para ser por MAPA
    cursor.execute('DROP TABLE IF EXISTS drops_monstros')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS drops_mapas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            mapa_id INTEGER,
            item_nome TEXT,
            chance INTEGER
        )
    ''')
    conn.commit()
    conn.close()
    


def popular_dados_iniciais():
    """Lê os arquivos de modelos e popula o banco de dados"""
    conn = conectar()
    cursor = conn.cursor()

    # 1. ITENS MESTRE
    cursor.executemany("""
        INSERT OR REPLACE INTO itens_mestre (nome, tipo, subtipo, valor_efeito, descricao, preco_gold) 
        VALUES (?, ?, ?, ?, ?, ?)
    """, LISTA_ITENS_MESTRE)

    # 2. MONSTROS MESTRE
    cursor.executemany("""
        INSERT OR REPLACE INTO monstros_mestre (nome, mapa_id, vida, ataque, defesa, xp_recompensa, gold_recompensa, imagem) 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, LISTA_MONSTROS_MESTRE)

    # Popular a nova tabela de drops por mapa
    cursor.execute("DELETE FROM drops_mapas") # Limpa para atualizar
    cursor.executemany("""
        INSERT INTO drops_mapas (mapa_id, item_nome, chance) 
        VALUES (?, ?, ?)
    """, LISTA_DROPS_MAPAS)

    conn.commit()
    conn.close()
    print("✅ Banco de dados sincronizado com os arquivos de modelos!")
    

def get_drop_aleatorio(mapa_id):
    """Sorteia um item baseado nos drops disponíveis para o mapa atual"""
    conn = conectar()
    cursor = conn.cursor()
    # Busca todos os possíveis drops configurados para este mapa
    cursor.execute("SELECT item_nome, chance FROM drops_mapas WHERE mapa_id = ?", (mapa_id,))
    possibilidades = cursor.fetchall()
    conn.close()

    if not possibilidades:
        return None

    # Embaralha para não beneficiar sempre o primeiro da lista
    import random
    lista_temp = list(possibilidades)
    random.shuffle(lista_temp)

    for item in lista_temp:
        # Se o número sorteado for menor ou igual à chance (ex: 20%), o item cai
        if random.randint(1, 100) <= item['chance']:
            return item['item_nome']
    
    return None
    
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
    conn.row_factory = sqlite3.Row 
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
    
    # 1. Definindo as colunas que PRECISAM existir na tabela personagens
    colunas_necessarias = {
        "vida_max": "INTEGER DEFAULT 100",
        "pet_xp": "INTEGER DEFAULT 0",
        "pet_level": "INTEGER DEFAULT 1",
        "mochila_slots": "INTEGER DEFAULT 10",
        "pet_equipado": "INTEGER DEFAULT 0" # <--- Adicionamos aqui!
    }
    
    # Verifica quais colunas já existem
    cursor.execute("PRAGMA table_info(personagens)")
    colunas_existentes = [info[1] for info in cursor.fetchall()]
    
    # Adiciona apenas as que faltam
    for nome, tipo in colunas_necessarias.items():
        if nome not in colunas_existentes:
            try:
                cursor.execute(f"ALTER TABLE personagens ADD COLUMN {nome} {tipo}")
                print(f"DEBUG DB: Coluna '{nome}' criada com sucesso.")
            except sqlite3.OperationalError as e:
                print(f"DEBUG DB: Erro ao criar coluna {nome}: {e}")

    # --- RESET DA TABELA DE DROPS (MANTENHA A SUA LÓGICA) ---
    cursor.execute("PRAGMA table_info(drops_monstros)")
    colunas = [col[1] for col in cursor.fetchall()]
    
    if "monstro_nome" not in colunas and len(colunas) > 0:
        print("⚠️ Corrigindo tabela drops_monstros...")
        cursor.execute("DROP TABLE IF EXISTS drops_monstros")
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
        nova_def = jogador['defesa'] + 2  
        
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



def curar_personagem_total(user_id):
    """Restaura 100% da vida do jogador instantaneamente"""
    conn = conectar()
    cursor = conn.cursor()
    # O SQL abaixo iguala a coluna 'vida' ao valor que estiver na 'vida_max'
    cursor.execute("UPDATE personagens SET vida = vida_max WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()
    
    
def get_status_com_bonus(user_id):
    """Calcula os status do jogador somando o bônus do pet equipado"""
    jogador = get_jogador(user_id)
    if not jogador or not jogador['pet_equipado']:
        return jogador
    
    # Exemplo: Pet Tartaruga dá +10% de Defesa
    if jogador['pet_nome'] == "Tartaruga filhote":
        jogador['defesa'] = int(jogador['defesa'] * 1.10)
    
    # Adicione outros pets aqui conforme necessário
    return jogador


def get_jogador_com_bonus(user_id):
    """Busca o jogador e aplica os bônus se o pet estiver equipado"""
    jogador = get_jogador(user_id)
    if jogador and jogador['pet_equipado'] == 1:
        # Exemplo: Tartaruga = +10% Defesa
        if jogador['pet_nome'] == "Tartaruga filhote":
            jogador['defesa'] = int(jogador['defesa'] * 1.10)
        # Exemplo: Lobo = +10% Ataque
        elif jogador['pet_nome'] == "Lobo filhote":
            jogador['ataque'] = int(jogador['ataque'] * 1.10)
        # Exemplo: Falcão = +10% Agilidade (ou outro atributo)
        elif jogador['pet_nome'] == "Falcão filhote":
            pass # Adicione sua lógica aqui
            
    return jogador


def aplicar_bonus_pet(jogador):
    """Aplica o bônus se o pet estiver equipado e retorna o objeto modificado"""
    print(f"DEBUG: Aplicando bônus para pet: {jogador.get('pet_nome')}, Equipado: {jogador.get('pet_equipado')}")
    if jogador and jogador['pet_equipado'] == 1:
        nome = jogador['pet_nome']
        
        # 10% de bônus baseados nos status atuais
        if nome == "Tartaruga filhote":
            jogador['defesa_max'] += int(jogador['defesa_max'] * 0.10)
        elif nome == "Lobo filhote":
            jogador['ataque_max'] += int(jogador['ataque'] * 0.10)
        elif nome == "Falcão filhote":
            jogador['vida_max'] += int(jogador['vida'] * 0.10)
            
    return jogador


