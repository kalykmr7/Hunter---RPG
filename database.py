import os
import sqlite3
from datetime import datetime

# Caminho do banco
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "hunter_game.db")

def conectar():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row 
    return conn

def criar_tabela():
    conn = conectar()
    cursor = conn.cursor()
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
            ataque INTEGER DEFAULT 10,
            defesa INTEGER DEFAULT 5,
            sorte INTEGER DEFAULT 1,
            pet_nome TEXT,
            pet_vida INTEGER,
            pet_ataque INTEGER,
            pet_defesa INTEGER,
            pet_agilidade INTEGER,
            ultimo_login TEXT,
            pet_imagem TEXT,
            mapa_atual INTEGER DEFAULT 0,
            mithril INTEGER DEFAULT 0
        )
    ''')
    conn.commit()
    conn.close()

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

def atualizar_estrutura_banco():
    conn = conectar()
    cursor = conn.cursor()
    # Adiciona colunas novas caso não existam (migração segura)
    colunas = [("mapa_atual", "INTEGER DEFAULT 0"), ("mithril", "INTEGER DEFAULT 0"), ("ultimo_login", "TEXT"), ("pet_imagem", "TEXT")]
    for nome, tipo in colunas:
        try:
            cursor.execute(f"ALTER TABLE personagens ADD COLUMN {nome} {tipo}")
        except sqlite3.OperationalError:
            pass
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
    """Aumenta o nível e melhora os atributos do caçador"""
    conn = conectar()
    cursor = conn.cursor()
    
    # 1. Busca os dados atuais
    cursor.execute("SELECT level, xp, vida, ataque, defesa FROM personagens WHERE user_id = ?", (user_id,))
    jogador = cursor.fetchone()
    
    if jogador:
        novo_lvl = jogador['level'] + 1
        sobra_xp = jogador['xp'] - 100 # Mantém o que passou de 100
        nova_vida = jogador['vida'] + 20 # Ganha +20 de vida máxima
        novo_atq = jogador['ataque'] + 2  # Ganha +2 de ataque
        nova_def = jogador['defesa'] + 1  # Ganha +1 de defesa
        
        # 2. Atualiza o banco
        cursor.execute("""
            UPDATE personagens 
            SET level = ?, xp = ?, vida = ?, ataque = ?, defesa = ? 
            WHERE user_id = ?
        """, (novo_lvl, max(0, sobra_xp), nova_vida, novo_atq, nova_def, user_id))
        
        conn.commit()
        conn.close()
        return {
            "level": novo_lvl,
            "vida": nova_vida,
            "ataque": novo_atq,
            "defesa": nova_def
        }
    conn.close()
    return None