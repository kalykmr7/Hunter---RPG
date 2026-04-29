# --- ARQUIVO: .\admin.py ---
import database

def set_level_admin(nick, novo_lvl):
    """Força um nível específico e escala os atributos proporcionalmente para testes"""
    conn = database.conectar()
    cursor = conn.cursor()
    
    # Cálculos baseados na progressão do jogo
    nova_vida_max = 100 + (novo_lvl - 1) * 20
    novo_atq = 10 + (novo_lvl - 1) * 2
    nova_def = 5 + (novo_lvl - 1) * 1
    
    try:
        cursor.execute("""
            UPDATE personagens 
            SET level = ?, xp = 0, vida = ?, vida_max = ?, ataque = ?, defesa = ? 
            WHERE nick = ?
        """, (novo_lvl, nova_vida_max, nova_vida_max, novo_atq, nova_def, nick))
        
        sucesso = cursor.rowcount > 0 
        conn.commit()
        return sucesso
    except Exception as e:
        print(f"Erro ao definir nível: {e}")
        return False
    finally:
        conn.close()

def debug_tabela():
    """Função de debug para verificar estrutura do banco"""
    conn = database.conectar()
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(personagens)")
    print("COLUNAS:", cursor.fetchall())
    conn.close()