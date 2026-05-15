import os
import sqlite3
from datetime import datetime, timedelta
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
            critico INTEGER DEFAULT 1,
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
    
    # Tabela de Pets dos Jogadores (Permite múltiplos pets por usuário)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS pets_jogador (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            nome TEXT,
            level INTEGER DEFAULT 1,
            xp INTEGER DEFAULT 0,
            vida INTEGER,
            ataque INTEGER,
            defesa INTEGER,
            agilidade INTEGER,
            imagem TEXT,
            equipado INTEGER DEFAULT 0,
            FOREIGN KEY(user_id) REFERENCES personagens(user_id)
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

    # 3. Tabela Mestre de Itens Mestre
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS itens_mestre (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT UNIQUE,
            tipo TEXT,
            subtipo TEXT,
            valor_efeito INTEGER DEFAULT 0,
            descricao TEXT,
            preco_gold INTEGER DEFAULT 0,
            chance_drop INTEGER DEFAULT 0,
            nivel_max INTEGER DEFAULT 0
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


def criar_tabela_incubadora():
    """Cria a tabela para monitorar ovos chocando."""
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS incubacao_ativa (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            ovo_nome TEXT,
            tempo_final TEXT -- Salvaremos a data/hora final como string
        )
    ''')
    conn.commit()
    conn.close()
    
    
def criar_tabelas_adicionais():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS masmorras_mestre (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            mapa_id INTEGER,
            andar INTEGER, -- 1, 2 ou 3
            nome TEXT,
            vida INTEGER,
            ataque INTEGER,
            defesa INTEGER,
            xp_recompensa INTEGER,
            gold_recompensa INTEGER,
            imagem TEXT
        )
    ''')
    conn.commit()
    conn.close()



def popular_dados_iniciais():
    """Lê os arquivos de modelos e popula o banco de dados"""
    conn = conectar()
    cursor = conn.cursor()
    
    # Criação da tabela de Masmorra se não existir
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS masmorras_mestre (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            mapa_id INTEGER,
            andar INTEGER,
            nome TEXT,
            vida INTEGER,
            ataque INTEGER,
            defesa INTEGER,
            xp_recompensa INTEGER,
            gold_recompensa INTEGER
        )
    ''')

    # 1. ITENS MESTRE
    cursor.executemany("""
        INSERT OR REPLACE INTO itens_mestre (nome, tipo, subtipo, valor_efeito, descricao, preco_gold, chance_drop, nivel_max) 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, LISTA_ITENS_MESTRE)

    # 2. MONSTROS MESTRE
    cursor.executemany("""
        INSERT OR REPLACE INTO monstros_mestre (nome, mapa_id, vida, ataque, defesa, xp_recompensa, gold_recompensa, imagem) 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, LISTA_MONSTROS_MESTRE)

    # 3. CHEFES DE MASMORRA (Novos dados)
    # Formato: (Mapa_ID, Andar, Nome, Vida, Ataque, Defesa, XP, Gold)
    from modelos.inimigos import LISTA_BOSS_MASMORRAS
    # Como tiramos a imagem por enquanto, filtramos a lista
    boss_dados = [(b[0], b[1], b[2], b[3], b[4], b[5], b[6], b[7]) for b in LISTA_BOSS_MASMORRAS]
    
    cursor.execute("DELETE FROM masmorras_mestre") # Limpa para atualizar valores de balanceamento
    cursor.executemany("""
        INSERT INTO masmorras_mestre (mapa_id, andar, nome, vida, ataque, defesa, xp_recompensa, gold_recompensa)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, boss_dados)

    # 4. DROPS
    cursor.execute("DELETE FROM drops_mapas")
    cursor.executemany("""
        INSERT INTO drops_mapas (mapa_id, item_nome, chance) 
        VALUES (?, ?, ?)
    """, LISTA_DROPS_MAPAS)

    conn.commit()
    conn.close()
    
    
def atualizar_estrutura_atributos():
    """Força a atualização dos atributos e agora o Estilo do Item (categorias) no banco de dados."""
    conn = conectar()
    cursor = conn.cursor()
    
    # Garante que as colunas essenciais existem na tabela principal de equipamentos
    cursor.execute("PRAGMA table_info(itens_mestre)")
    colunas = [info[1] for info in cursor.fetchall()]
    
    if "atributo_bonus" not in colunas:
        cursor.execute("ALTER TABLE itens_mestre ADD COLUMN atributo_bonus TEXT DEFAULT NULL")
    
    # Nova coluna para segregar estilos de uso na parte visual de Acessórios!
    if "estilo_acessorio" not in colunas:
        cursor.execute("ALTER TABLE itens_mestre ADD COLUMN estilo_acessorio TEXT DEFAULT NULL")
        print("✅ Coluna 'estilo_acessorio' adicionada em 'itens_mestre'.")

    # Mapeamento atualizado do sistema para evitar perdas!
    # No futuro, basta vir aqui e inserir (exemplo: 'Anel de Fogo': {'attr': 'ataque', 'estilo': 'anel'})
    mapeamento_atributos = {
        'Bússola': {'attr': 'sorte', 'estilo': 'bussola'},
        'Binóculos': {'attr': 'critico', 'estilo': 'binoculos'}
    }
    
    # Atualiza forçadamente (isso protege também quem já instalou os updates velhos de se beneficiarem disso)
    for nome, config in mapeamento_atributos.items():
        cursor.execute("""
            UPDATE itens_mestre 
            SET atributo_bonus = ?, estilo_acessorio = ? 
            WHERE nome = ?
        """, (config['attr'], config['estilo'], nome))
    
    print("✅ Estrutura de Atributos e Estilos verificada e forçada no DB.")
    conn.commit()
    conn.close()


def equipar_desequipar_db(user_id, item_id):
    conn = conectar()
    cursor = conn.cursor()
    
    # Encontramos a posição e formato visual da linha do inventário real.
    cursor.execute("SELECT item_nome, equipado FROM inventario WHERE id = ?", (item_id,))
    item_inv = cursor.fetchone()
    
    if not item_inv:
        conn.close()
        return False, "Item não encontrado."

    item_nome = item_inv['item_nome']
    
    # >> MODIFICAÇÃO CHAVE AQUI: O banco me manda também a classe isolada de "estilo" desse acessório
    cursor.execute("SELECT subtipo, estilo_acessorio FROM itens_mestre WHERE nome = ?", (item_nome,))
    dados_mestre = cursor.fetchone()
    subtipo = dados_mestre['subtipo']
    estilo_alvo = dados_mestre['estilo_acessorio']
    
    # MAPEAMENTO DE SLOTS DAS COLUNAS (Fixo nas demais opções normais de UI do DB antigo).
    mapeamento = {
        "arma": "arma_equipada",
        "armadura": "armadura_equipada",
        "conjunto": "set_equipado",
        "acessorio": "acessorio_equipado"
    }

    if subtipo not in mapeamento:
        conn.close()
        return False, "Este tipo de item não pode ser equipado."

    coluna_perso = mapeamento[subtipo]

    # --- Rota A: Estamos tentando REMOVER / Desequipar o Item atual.
    if item_inv['equipado'] == 1:
        cursor.execute("UPDATE inventario SET equipado = 0 WHERE id = ?", (item_id,))
        
        # Só limpar se o campo da velha matriz for singleplayer de equipamento total (uma única var pro UI):
        if subtipo != 'acessorio':
            cursor.execute(f"UPDATE personagens SET {coluna_perso} = 'Nenhuma' WHERE user_id = ?", (user_id,))
            
        msg = f"Você desequipou {item_nome}."
        
    # --- Rota B: Estamos querendo INSTALAR esse item e ativar bônus dele.
    else:
        
        if subtipo != 'acessorio':
            # Antiga estrutura funcional segura do sistema Sênior para retirar espada a, inserir espada B!
            cursor.execute("""
                UPDATE inventario SET equipado = 0 
                WHERE user_id = ? AND item_nome IN (SELECT nome FROM itens_mestre WHERE subtipo = ?)
            """, (user_id, subtipo))
            
            # Aqui gravamos por ser algo único por slot exato visual 
            cursor.execute(f"UPDATE personagens SET {coluna_perso} = ? WHERE user_id = ?", (item_nome, user_id))
            
        else:
            # MAGIA EXCLUSIVA DA REGRA (ACESSÓRIOS): 
            # Retire equipado DESTA MOCHILA que SEJAM exatamente DESSE ESTILO especificado pelo alvo ! (Se existir)!
            if estilo_alvo: 
                cursor.execute("""
                    UPDATE inventario SET equipado = 0 
                    WHERE user_id = ? AND equipado = 1 AND item_nome IN (
                        SELECT nome FROM itens_mestre WHERE estilo_acessorio = ?
                    )
                """, (user_id, estilo_alvo))
            
            # Substituí por aviso genérico a antiga forma pra salvar integridade de DB antigas da aplicação:
            cursor.execute(f"UPDATE personagens SET {coluna_perso} = 'Múltiplos Equipados' WHERE user_id = ?", (user_id,))

        # Confirme e vire a var de Equipado como ativa global!
        cursor.execute("UPDATE inventario SET equipado = 1 WHERE id = ?", (item_id,))
        msg = f"Você equipou {item_nome}!"

    conn.commit()
    conn.close()
    return True, msg


    
    
def get_drop_aleatorio(mapa_id):
    """Sorteia itens normais baseados apenas na chance do mapa/item."""
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT item_nome, chance FROM drops_mapas WHERE mapa_id = ?", (mapa_id,))
    drops_regionais = cursor.fetchall()
    cursor.execute("SELECT nome as item_nome, chance_drop as chance FROM itens_mestre WHERE chance_drop > 0")
    drops_globais = cursor.fetchall()
    conn.close()

    todas_as_chances = list(drops_regionais) + list(drops_globais)
    if not todas_as_chances: return None

    import random
    random.shuffle(todas_as_chances)
    for item in todas_as_chances:
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


def atualizar_estrutura_banco():
    """Verifica e adiciona colunas faltantes em todas as tabelas de forma segura."""
    conn = conectar()
    cursor = conn.cursor()
    
    # --- ATUALIZAÇÕES NA TABELA: personagens ---
    colunas_personagens = {
        "vida_max": "INTEGER DEFAULT 100",
        "pet_xp": "INTEGER DEFAULT 0",
        "pet_level": "INTEGER DEFAULT 1",
        "mochila_slots": "INTEGER DEFAULT 10",
        "pet_equipado": "INTEGER DEFAULT 0",
        "arma_equipada": "TEXT DEFAULT 'Nenhuma'",
        "armadura_equipada": "TEXT DEFAULT 'Nenhuma'",
        "critico": "INTEGER DEFAULT 1",
        "set_equipado": "TEXT DEFAULT 'Nenhuma'",
        "acessorio_equipado": "TEXT DEFAULT 'Nenhuma'",
        "mithril": "INTEGER DEFAULT 0"
    }
    
    cursor.execute("PRAGMA table_info(personagens)")
    existentes_p = [info[1] for info in cursor.fetchall()]
    
    for nome, tipo in colunas_personagens.items():
        if nome not in existentes_p:
            cursor.execute(f"ALTER TABLE personagens ADD COLUMN {nome} {tipo}")
            print(f"✅ Coluna '{nome}' adicionada em 'personagens'.")

    # --- ATUALIZAÇÕES NA TABELA: inventario ---
    colunas_inventario = {
        "equipado": "INTEGER DEFAULT 0",
        "nivel_refino": "INTEGER DEFAULT 0"
    }
    
    cursor.execute("PRAGMA table_info(inventario)")
    existentes_inv = [info[1] for info in cursor.fetchall()]
    
    for nome, tipo in colunas_inventario.items():
        if nome not in existentes_inv:
            cursor.execute(f"ALTER TABLE inventario ADD COLUMN {nome} {tipo}")
            print(f"✅ Coluna '{nome}' adicionada em 'inventario'.")

    # --- ATUALIZAÇÕES NA TABELA: itens_mestre ---
    cursor.execute("PRAGMA table_info(itens_mestre)")
    existentes_mestre = [info[1] for info in cursor.fetchall()]
    if "nivel_max" not in existentes_mestre:
        cursor.execute("ALTER TABLE itens_mestre ADD COLUMN nivel_max INTEGER DEFAULT 0")
        print("✅ Coluna 'nivel_max' adicionada em 'itens_mestre'.")
    
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


def curar_personagem_custom(user_id, valor_hp):
    """Cura o personagem para um valor específico (usado para aplicar bônus de Set/Pet)"""
    conn = conectar()
    cursor = conn.cursor()
    # Define a vida atual como o valor total (com bônus) passado
    cursor.execute("UPDATE personagens SET vida = ? WHERE user_id = ?", (valor_hp, user_id))
    conn.commit()
    conn.close()


def adicionar_item_inventario(user_id, item_nome, tipo, qtd=1):
    """Adiciona itens. Apenas EQUIPAMENTOS ocupam slots na mochila."""
    conn = conectar()
    cursor = conn.cursor()

    # 1. Se for EQUIPAMENTO, verificamos o limite de slots
    if tipo == 'equipamento':
        cursor.execute("SELECT mochila_slots FROM personagens WHERE user_id = ?", (user_id,))
        limite_slots = cursor.fetchone()['mochila_slots']

        # Conta quantos equipamentos o jogador já possui
        cursor.execute("SELECT COUNT(*) as ocupados FROM inventario WHERE user_id = ? AND tipo = 'equipamento'", (user_id,))
        slots_ocupados = cursor.fetchone()['ocupados']

        if slots_ocupados + qtd > limite_slots:
            conn.close()
            return False, f"🎒 Mochila cheia! ({slots_ocupados}/{limite_slots})"

        # Insere cada equipamento como uma linha única (para permitir encantamentos/status individuais no futuro)
        for _ in range(qtd):
            cursor.execute(
                "INSERT INTO inventario (user_id, item_nome, tipo, quantidade, equipado) VALUES (?, ?, ?, 1, 0)",
                (user_id, item_nome, tipo)
            )
    
    # 2. Se for MATERIAL ou CONSUMÍVEL, não ocupa slot e acumula (stack)
    else:
        cursor.execute("SELECT quantidade FROM inventario WHERE user_id = ? AND item_nome = ?", (user_id, item_nome))
        item_existente = cursor.fetchone()
        
        if item_existente:
            cursor.execute("UPDATE inventario SET quantidade = quantidade + ? WHERE user_id = ? AND item_nome = ?", (qtd, user_id, item_nome))
        else:
            cursor.execute("INSERT INTO inventario (user_id, item_nome, tipo, quantidade) VALUES (?, ?, ?, ?)", (user_id, item_nome, tipo, qtd))

    conn.commit()
    conn.close()
    return True, "Item adicionado!"

def get_inventario(user_id):
    """Busca todos os itens, incluindo o ID único e o nível de refino."""
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, item_nome, quantidade, tipo, equipado, nivel_refino FROM inventario WHERE user_id = ?", 
        (user_id,)
    )
    itens = cursor.fetchall() 
    
    conn.close()
    return itens

def calcular_xp_necessario(level):
    """Calcula quanto XP o jogador precisa para sair do level atual e ir para o próximo"""
    # Lvl 1: 100 XP
    # Lvl 2: 100 + (1 * 150) = 250 XP
    # Lvl 3: 100 + (2 * 150) = 400 XP...
    return 100 + (level - 1) * 175

def usar_pocao_cura(user_id, item_nome, cura_quantidade):
    """Diminui o item da mochila e cura o jogador considerando os bônus de equipamentos."""
    conn = conectar()
    cursor = conn.cursor()

    # 1. Busca o jogador bruto e aplica os bônus para saber a VIDA MÁXIMA REAL
    jogador_bruto = get_jogador(user_id)
    if not jogador_bruto:
        conn.close()
        return False, "Jogador não encontrado."
    
    # Aplicamos os bônus (Pet + Itens) para ter o teto real de cura
    jogador = aplicar_bonus_geral(dict(jogador_bruto))

    # 2. Busca o item (ignora maiúsculas no SQL)
    cursor.execute(
        "SELECT quantidade, item_nome FROM inventario WHERE user_id = ? AND item_nome = ? COLLATE NOCASE", 
        (user_id, item_nome)
    )
    item = cursor.fetchone()

    if not item:
        conn.close()
        return False, f"Você não possui {item_nome}!"

    # CHECAGEM CORRIGIDA: Usa o vida_max com bônus
    if jogador['vida'] >= jogador['vida_max']:
        conn.close()
        return False, "Sua vida já está cheia!"

    # 3. Consome o item
    nome_real = item['item_nome']
    if item['quantidade'] > 1:
        cursor.execute("UPDATE inventario SET quantidade = quantidade - 1 WHERE user_id = ? AND item_nome = ?", (user_id, nome_real))
    else:
        cursor.execute("DELETE FROM inventario WHERE user_id = ? AND item_nome = ?", (user_id, nome_real))

    # 4. Aplica a cura limitada ao máximo real
    nova_vida = min(jogador['vida'] + cura_quantidade, jogador['vida_max'])
    cursor.execute("UPDATE personagens SET vida = ? WHERE user_id = ?", (nova_vida, user_id))

    conn.commit()
    conn.close()
    return True, f"Curado! ❤️ {nova_vida}/{jogador['vida_max']}"


def calcular_xp_pet(level):
    """Calcula o XP necessário para o próximo nível do pet"""
    # Lvl 1: 50 | Lvl 2: 100 | Lvl 3: 150...
    return 50 + (level - 1) * 200

def dar_xp_pet(user_id, pet_id, item_nome, xp_por_unidade, qtd):
    """Dá XP a um pet específico e processa level ups"""
    conn = conectar()
    cursor = conn.cursor()

    # 1. Busca os dados do pet específico
    cursor.execute("""
        SELECT nome, xp, level, vida, ataque, defesa, agilidade, equipado 
        FROM pets_jogador WHERE id = ? AND user_id = ?
    """, (pet_id, user_id))
    pet = cursor.fetchone()

    if not pet:
        conn.close()
        return False, "Pet não encontrado."

    # 2. Verifica estoque de comida
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

    # 4. Lógica de XP e Level Up (Regra: 50 + (Lvl-1) * 50)
    xp_ganho_total = xp_por_unidade * qtd
    novo_xp = (pet['xp'] or 0) + xp_ganho_total
    novo_lvl = pet['level']
    n_vida, n_atq, n_def, n_agi = pet['vida'], pet['ataque'], pet['defesa'], pet['agilidade']
    
    levels_ganhos = 0
    while True:
        xp_necessario = 50 + (novo_lvl - 1) * 50
        if novo_xp >= xp_necessario:
            novo_xp -= xp_necessario
            novo_lvl += 1
            levels_ganhos += 1
            # Aumenta atributos (Ajuste conforme seu balanceamento)
            n_vida += 2; n_atq += 1; n_def += 1; n_agi += 1
        else:
            break

    # 5. Atualiza a tabela de pets
    cursor.execute("""
        UPDATE pets_jogador 
        SET xp = ?, level = ?, vida = ?, ataque = ?, defesa = ?, agilidade = ?
        WHERE id = ?
    """, (novo_xp, novo_lvl, n_vida, n_atq, n_def, n_agi, pet_id))

    # 6. SE ESTIVER EQUIPADO: Sincroniza com a tabela personagens
    if pet['equipado'] == 1:
        cursor.execute("""
            UPDATE personagens 
            SET pet_level = ? WHERE user_id = ?
        """, (novo_lvl, user_id))

    conn.commit()
    conn.close()
    
    msg = f"Seu pet ganhou {xp_ganho_total} de XP! ✨"
    if levels_ganhos > 0:
        msg += f"\n🌟 EVOLUÇÃO! Lvl {novo_lvl}!"
    
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
    """Aplica o bônus de 10% nos atributos corretos se o pet estiver equipado"""
    # Verificamos se o jogador existe e se o pet_equipado está como 1
    if jogador and jogador.get('pet_equipado') == 1:
        nome_pet = jogador.get('pet_nome')
        
        # 10% de bônus baseados nos status atuais do jogador
        if nome_pet == "Tartaruga filhote":
            # Aumenta a Defesa (usamos a chave 'defesa' que existe no banco)
            jogador['defesa'] = int(jogador['defesa'] * 1.10)
            
        elif nome_pet == "Lobo filhote":
            # Aumenta o Ataque (usamos a chave 'ataque' que existe no banco)
            jogador['ataque'] = int(jogador['ataque'] * 1.10)
            
        elif nome_pet == "Falcão filhote":
            # Aumenta a Vida Máxima (usamos a chave 'vida_max' que existe no banco)
            jogador['vida_max'] = int(jogador['vida_max'] * 1.10)
            
    return jogador


def get_pets_jogador(user_id):
    """Busca todos os pets que o jogador possui"""
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM pets_jogador WHERE user_id = ?", (user_id,))
    pets = cursor.fetchall()
    conn.close()
    return pets

def equipar_pet_db(user_id, pet_id):
    """Equipa um pet e atualiza a tabela personagens para manter a UI funcionando"""
    conn = conectar()
    cursor = conn.cursor()
    
    # 1. Desequipa todos na tabela de pets
    cursor.execute("UPDATE pets_jogador SET equipado = 0 WHERE user_id = ?", (user_id,))
    
    # 2. Equipa o pet alvo
    cursor.execute("UPDATE pets_jogador SET equipado = 1 WHERE id = ? AND user_id = ?", (pet_id, user_id))
    
    # 3. BUSCA OS DADOS DO NOVO PET PARA SINCRONIZAR
    cursor.execute("SELECT nome, imagem FROM pets_jogador WHERE id = ?", (pet_id,))
    pet_info = cursor.fetchone()
    
    if pet_info:
        # Atualiza a tabela personagens (Onde a função exibir_mapa olha)
        cursor.execute("""
            UPDATE personagens 
            SET pet_nome = ?, pet_imagem = ?, pet_equipado = 1 
            WHERE user_id = ?
        """, (pet_info['nome'], pet_info['imagem'], user_id))
        
    conn.commit()
    conn.close()
    return True


def adicionar_novo_pet(user_id, pet_modelo):
    """Adiciona um pet novo e sincroniza com a tabela personagens se for o primeiro"""
    conn = conectar()
    cursor = conn.cursor()
    
    # Verifica se é o primeiro pet do jogador
    cursor.execute("SELECT COUNT(*) as total FROM pets_jogador WHERE user_id = ?", (user_id,))
    total = cursor.fetchone()['total']
    primeiro = 1 if total == 0 else 0
    
    # 1. Insere na tabela de coleção
    cursor.execute("""
        INSERT INTO pets_jogador (user_id, nome, vida, ataque, defesa, agilidade, imagem, equipado)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (user_id, pet_modelo['nome'], pet_modelo['vida'], pet_modelo['ataque'], 
          pet_modelo['defesa'], pet_modelo['agilidade'], pet_modelo['imagem'], primeiro))
    
    # 2. SE FOR O PRIMEIRO: Sincroniza com a tabela 'personagens' para os botões aparecerem
    if primeiro:
        cursor.execute("""
            UPDATE personagens 
            SET pet_nome = ?, pet_imagem = ?, pet_equipado = 1 
            WHERE user_id = ?
        """, (pet_modelo['nome'], pet_modelo['imagem'], user_id))
    
    conn.commit()
    conn.close()
    return True


def get_pet_por_id(pet_id):
    """Busca os detalhes de um pet específico na tabela pets_jogador"""
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM pets_jogador WHERE id = ?", (pet_id,))
    pet = cursor.fetchone()
    conn.close()
    return pet



def calcular_bonus_equipamentos(user_id):
    """Calcula os status somando TODOS os equipamentos equipados."""
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT i.nivel_refino, m.subtipo, m.valor_efeito, m.nome, m.atributo_bonus
        FROM inventario i
        JOIN itens_mestre m ON i.item_nome = m.nome
        WHERE i.user_id = ? AND i.equipado = 1
    """, (user_id,))
    
    itens_equipados = cursor.fetchall()
    conn.close()

    # Dicionário base de bônus
    bonus = {"ataque": 0, "defesa": 0, "vida_max": 0, "sorte": 0, "critico": 0}

    for item in itens_equipados:
        sub = item['subtipo']
        val = item['valor_efeito'] + ((item['nivel_refino'] or 0) * 2)

        if sub == 'arma': 
            bonus['ataque'] += val
        elif sub == 'armadura': 
            bonus['defesa'] += val
        elif sub == 'conjunto':
            bonus['ataque'] += val
            bonus['defesa'] += val
            bonus['vida_max'] += (val * 2)
        elif sub == 'acessorio':
            # Proteção Sênior: Verifica se attr existe E é válido no dicionário
            attr = item['atributo_bonus']
            if attr and attr in bonus:
                bonus[attr] += val
            else:
                print(' ')
            
    return bonus



def aplicar_bonus_geral(jogador_bruto):
    """Aplica bônus de Equipamentos e o bônus progressivo dos Pets (+0.5% a cada 2 níveis)."""
    jogador = dict(jogador_bruto)
    user_id = jogador['user_id']

    # 1. BÔNUS DE EQUIPAMENTOS (Armas, Armaduras, Sets)
    bonus_itens = calcular_bonus_equipamentos(user_id)
    jogador['ataque'] += bonus_itens['ataque']
    jogador['defesa'] += bonus_itens['defesa']
    jogador['vida_max'] += bonus_itens['vida_max']
    jogador['sorte'] += bonus_itens['sorte']
    jogador['critico'] = (jogador.get('critico') or 1) + bonus_itens['critico']

    # 2. BÔNUS DE PET (Sistemas Progressivos - Regra 3)
    if jogador.get('pet_equipado') == 1:
        nome_p = jogador.get('pet_nome')
        lvl_p = jogador.get('pet_level', 1)
        
        # Calcula a escala: a cada 2 níveis, ganha 0.005 (0.5%)
        # Lvl 1 e 2: escala 0 | Lvl 3 e 4: escala 1...
        escala = (lvl_p - 1) // 2
        bonus_adicional = escala * 0.005
        
        # Bônus Base: 10% (1.10) para Raros e 2% (1.02) para Iniciais
        # Vamos identificar se é inicial pelo nome (como no seu modelos/monstros.py)
        iniciais = ["Falcão filhote", "Lobo filhote", "Tartaruga filhote"]
        base = 1.02 if nome_p in iniciais else 1.10
        
        multiplicador_final = base + bonus_adicional

        # Aplicação dos bônus conforme o tipo de Pet
        if nome_p in ["Falcão filhote", "Sentinela de Marfim"]:
            jogador['vida_max'] = int(jogador['vida_max'] * multiplicador_final)
            
        elif nome_p in ["Lobo filhote", "Raposa de Cinza"]:
            jogador['ataque'] = int(jogador['ataque'] * multiplicador_final)
            
        elif nome_p in ["Tartaruga filhote", "Escudeiro de Casca"]:
            jogador['defesa'] = int(jogador['defesa'] * multiplicador_final)
            
        elif nome_p == "Serpente de Lodo":
            jogador['sorte'] = int(jogador['sorte'] * multiplicador_final)
            
        elif nome_p == "Coruja de Vidro Astral":
            jogador['critico'] = int(jogador['critico'] * multiplicador_final)
            
    return jogador


def desequipar_pet_completo_db(user_id):
    """Desequipa o pet, mas mantém os dados básicos para a UI não quebrar"""
    conn = conectar()
    cursor = conn.cursor()
    
    # 1. Desequipa todos na coleção
    cursor.execute("UPDATE pets_jogador SET equipado = 0 WHERE user_id = ?", (user_id,))
    
    # 2. Na tabela personagens, apenas marcamos como desequipado (0)
    # Mantemos o nome ou limpamos, mas o 'jogador_possui_pets' agora manda na UI
    cursor.execute("""
        UPDATE personagens 
        SET pet_equipado = 0 
        WHERE user_id = ?
    """, (user_id,))
    
    conn.commit()
    conn.close()
    return True


def jogador_possui_pets(user_id):
    """Verifica se o jogador tem pelo menos um pet na coleção (equipado ou não)"""
    conn = conectar()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT COUNT(*) as total FROM pets_jogador WHERE user_id = ?", (user_id,))
        resultado = cursor.fetchone()
        possui = resultado['total'] > 0 if resultado else False
        return possui
    except Exception as e:
        print(f"Erro ao verificar posse de pets: {e}")
        return False
    finally:
        conn.close()
        
        
def vender_item_db(user_id, item_id, vender_tudo=False):
    """Remove o item e adiciona gold, considerando o nível de melhoria para o preço."""
    conn = conectar()
    cursor = conn.cursor()
    
    # Busca detalhes do item e preço mestre
    cursor.execute("""
        SELECT i.item_nome, i.quantidade, i.nivel_refino, i.equipado, m.preco_gold 
        FROM inventario i
        JOIN itens_mestre m ON i.item_nome = m.nome
        WHERE i.id = ? AND i.user_id = ?
    """, (item_id, user_id))
    item = cursor.fetchone()

    if not item:
        conn.close()
        return False, "Item não encontrado."
    
    if item['equipado'] == 1:
        conn.close()
        return False, "Você não pode vender algo que está usando!"

    # --- Lógica de Valorização ---
    qtd_a_vender = item['quantidade'] if vender_tudo else 1
    
    valor_base = int(item['preco_gold'] * 0.7)
    bonus_melhoria = (item['nivel_refino'] or 0) * 150 # Cada +1 adiciona 150 gold ao valor
    
    valor_total = (valor_base + bonus_melhoria) * qtd_a_vender

    # --- Processo de Venda ---
    if vender_tudo or item['quantidade'] <= 1:
        cursor.execute("DELETE FROM inventario WHERE id = ?", (item_id,))
    else:
        cursor.execute("UPDATE inventario SET quantidade = quantidade - 1 WHERE id = ?", (item_id,))

    cursor.execute("UPDATE personagens SET gold = gold + ? WHERE user_id = ?", (valor_total, user_id))
    
    conn.commit()
    conn.close()
    return True, f"💰 Vendido por {valor_total} Gold!"


def get_todos_equipados(user_id):
    """Busca todos os itens que o jogador está vestindo no momento (Arma, Armadura, Set)"""
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT i.id, i.item_nome, i.nivel_refino, m.valor_efeito, m.subtipo
        FROM inventario i
        JOIN itens_mestre m ON i.item_nome = m.nome
        WHERE i.user_id = ? AND i.equipado = 1
    """, (user_id,))
    itens = cursor.fetchall()
    conn.close()
    return itens

def get_item_por_id_forja(item_id):
    """Busca um item específico pelo ID para mostrar na tela de confirmação da forja"""
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT i.id, i.item_nome, i.nivel_refino, m.valor_efeito, m.subtipo
        FROM inventario i
        JOIN itens_mestre m ON i.item_nome = m.nome
        WHERE i.id = ?
    """, (item_id,))
    item = cursor.fetchone()
    conn.close()
    return item

def executar_refino_db(user_id, item_id, custo_gold):
    """Aumenta o refino se o jogador tiver gold e não tiver atingido o limite do item."""
    conn = conectar()
    cursor = conn.cursor()
    
    # Busca dados do item e o limite dele
    cursor.execute("""
        SELECT i.nivel_refino, m.nivel_max, p.gold 
        FROM inventario i
        JOIN itens_mestre m ON i.item_nome = m.nome
        JOIN personagens p ON p.user_id = i.user_id
        WHERE i.id = ? AND i.user_id = ?
    """, (item_id, user_id))
    dados = cursor.fetchone()

    if not dados:
        conn.close()
        return False, "Erro ao buscar dados do item."

    if dados['gold'] < custo_gold:
        conn.close()
        return False, "Ouro insuficiente! 💰"

    if dados['nivel_refino'] >= dados['nivel_max']:
        conn.close()
        return False, f"⚠️ Este item já atingiu o nível máximo (+{dados['nivel_max']})!"

    # Executa o refino
    cursor.execute("UPDATE inventario SET nivel_refino = nivel_refino + 1 WHERE id = ?", (item_id,))
    cursor.execute("UPDATE personagens SET gold = gold - ? WHERE user_id = ?", (custo_gold, user_id))
    
    conn.commit()
    conn.close()
    return True, "✨ Forja concluída com sucesso!"


def criar_tabela_missoes():
    """Cria a estrutura para missões diárias"""
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS missoes_diarias (
            user_id INTEGER,
            tipo TEXT,
            progresso INTEGER DEFAULT 0,
            objetivo INTEGER,
            recompensa_gold INTEGER,
            reivindicada INTEGER DEFAULT 0,
            data_missao TEXT,
            PRIMARY KEY (user_id, tipo)
        )
    ''')
    conn.commit()
    conn.close()

def get_ou_criar_missoes(user_id):
    """Busca as missões do dia. Se a data mudou, reseta o progresso."""
    conn = conectar()
    cursor = conn.cursor()
    hoje = datetime.now().strftime("%Y-%m-%d")
    
    # NOVAS MISSÕES DEFINIDAS AQUI
    # Formato: (tipo, objetivo, recompensa_gold)
    missoes_def = [
        ('caca', 50, 500),       # Caçar 5 monstros
        ('gold', 300, 500),     # Ganhar 300 gold em caça
        ('pocao', 3, 150),       # Usar 3 poções em combate
        ('forja', 2, 500),      # Realizar 1 refino no ateliê
        ('venda', 5, 250),       # Vender 5 itens no ateliê
        ('alimentar', 10, 180)  # Dar 10 frutas para o pet
    ]
    
    missoes_finais = []
    for tipo, obj, rec in missoes_def:
        cursor.execute("SELECT * FROM missoes_diarias WHERE user_id = ? AND tipo = ?", (user_id, tipo))
        m = cursor.fetchone()
        
        if not m or m['data_missao'] != hoje:
            cursor.execute("""
                INSERT OR REPLACE INTO missoes_diarias 
                (user_id, tipo, progresso, objetivo, recompensa_gold, reivindicada, data_missao)
                VALUES (?, ?, 0, ?, ?, 0, ?)
            """, (user_id, tipo, obj, rec, hoje))
            conn.commit()
            cursor.execute("SELECT * FROM missoes_diarias WHERE user_id = ? AND tipo = ?", (user_id, tipo))
            m = cursor.fetchone()
            
        missoes_finais.append(dict(m))
        
    conn.close()
    return missoes_finais


def atualizar_progresso_missao(user_id, tipo, valor=1):
    """Aumenta o progresso de uma missão específica (se não estiver reivindicada)"""
    conn = conectar()
    cursor = conn.cursor()
    hoje = datetime.now().strftime("%Y-%m-%d")
    
    cursor.execute("""
        UPDATE missoes_diarias 
        SET progresso = progresso + ? 
        WHERE user_id = ? AND tipo = ? AND data_missao = ? AND reivindicada = 0
    """, (valor, user_id, tipo, hoje))
    
    conn.commit()
    conn.close()

def reivindicar_missao_db(user_id, tipo):
    """Dá a recompensa e marca como concluída"""
    conn = conectar()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM missoes_diarias WHERE user_id = ? AND tipo = ?", (user_id, tipo))
    missao = cursor.fetchone()
    
    if missao and missao['progresso'] >= missao['objetivo'] and missao['reivindicada'] == 0:
        cursor.execute("UPDATE missoes_diarias SET reivindicada = 1 WHERE user_id = ? AND tipo = ?", (user_id, tipo))
        cursor.execute("UPDATE personagens SET gold = gold + ? WHERE user_id = ?", (missao['recompensa_gold'], user_id))
        conn.commit()
        conn.close()
        return True, f"💰 Você recebeu {missao['recompensa_gold']} Gold!"
    
    conn.close()
    return False, "Missão ainda não concluída ou já resgatada."


def sortear_ovo_diario(user_id, mapa_id):
    """Sorteia o drop de um ovo nomeado pela Região do mapa."""
    jogador_bruto = get_jogador(user_id)
    jogador = aplicar_bonus_geral(dict(jogador_bruto))
    sorte = jogador.get('sorte', 0)
    
    # 5% de chance base + bônus de sorte
    chance = 5 + (sorte * 0.5) 
    
    import random
    if random.uniform(1, 100) <= chance:
        if mapa_id == 0: return "Ovo [Vila]"
        return f"Ovo [Região {mapa_id}]"
    
    return None

def get_ovos_jogador(user_id):
    """Busca apenas itens do subtipo 'ovo' no inventário do jogador."""
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT i.id, i.item_nome, i.quantidade 
        FROM inventario i
        JOIN itens_mestre m ON i.item_nome = m.nome
        WHERE i.user_id = ? AND m.subtipo = 'ovo'
    """, (user_id,))
    ovos = cursor.fetchall()
    conn.close()
    return ovos


def iniciar_incubacao_db(user_id, ovo_nome, horas):
    """Registra o início do processo de chocar."""
    tempo_final = datetime.now() + timedelta(hours=horas)
    tempo_str = tempo_final.strftime("%Y-%m-%d %H:%M:%S")
    
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO incubacao_ativa (user_id, ovo_nome, tempo_final) VALUES (?, ?, ?)",
        (user_id, ovo_nome, tempo_str)
    )
    conn.commit()
    conn.close()

def get_incubacoes_ativas(user_id):
    """Busca TODOS os ovos que o jogador está chocando no momento."""
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM incubacao_ativa WHERE user_id = ?", (user_id,))
    res = cursor.fetchall() 
    conn.close()
    return res

def remover_incubacao_por_id(incubacao_id):
    """Remove um registro específico da incubadora pelo seu ID único."""
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM incubacao_ativa WHERE id = ?", (incubacao_id,))
    conn.commit()
    conn.close()
    
    
def consumir_materiais_alquimia(user_id, ingredientes, custo_gold):
    """
    Verifica se o jogador possui Gold e todos os materiais. Consome se tiver.
    ingredientes: Lista de tuplas [('Item A', qtd), ('Item B', qtd)]
    """
    conn = conectar()
    cursor = conn.cursor()
    
    try:
        # 1. Verifica Gold
        cursor.execute("SELECT gold FROM personagens WHERE user_id = ?", (user_id,))
        gold_atual = cursor.fetchone()['gold']
        if gold_atual < custo_gold:
            conn.close()
            return False, "Ouro insuficiente para a transmutação! 💰"

        # 2. Verifica Materiais
        for nome_item, qtd_necessaria in ingredientes:
            cursor.execute(
                "SELECT quantidade FROM inventario WHERE user_id = ? AND item_nome = ? COLLATE NOCASE", 
                (user_id, nome_item)
            )
            resultado = cursor.fetchone()
            if not resultado or resultado['quantidade'] < qtd_necessaria:
                conn.close()
                return False, f"Faltam ingredientes: {nome_item} 📦"

        # 3. Consome Gold
        cursor.execute("UPDATE personagens SET gold = gold - ? WHERE user_id = ?", (custo_gold, user_id))

        # 4. Consome Itens
        for nome_item, qtd_necessaria in ingredientes:
            cursor.execute("""
                UPDATE inventario SET quantidade = quantidade - ? 
                WHERE user_id = ? AND item_nome = ? COLLATE NOCASE
            """, (qtd_necessaria, user_id, nome_item))
            
            # Limpa itens com quantidade 0
            cursor.execute("DELETE FROM inventario WHERE user_id = ? AND item_nome = ? AND quantidade <= 0", (user_id, nome_item))
        
        conn.commit()
        return True, "Materiais transmutados com sucesso!"
    except Exception as e:
        print(f"Erro na alquimia (DB): {e}")
        return False, "Erro arcano no banco de dados."
    finally:
        conn.close()
        
        
def get_boss_masmorra(mapa_id, andar):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM masmorras_mestre WHERE mapa_id = ? AND andar = ?", (mapa_id, andar))
    boss = cursor.fetchone()
    conn.close()
    return boss