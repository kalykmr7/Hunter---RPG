
    
    # Comando no bot: set_level [nick] [numero] >> para dar lvl ao personagem
    # Comando no bot: darpet [nick] [nome do pet] >> para dar um dos pets
    # /dar kalyk 1 ovo [Região 1] = para um ovo de um mapa especifico
    # /dar kalyk 1 ovo = para dar um ovo de pet comum
    # /dar Recruta 50 Fruta Arco-íris (Dará 50 fruta ao jogador Recruta).
    # /dar Recruta 1 Poção pequena (Dará uma poção).
    # /dar Recruta 1 Espada de Madeira (Dará a espada).
    # /dar [nick] 5000 Gold (Dará gold)
    # /dar [nikc] 5000 mithril dará mithril

import database
from modelos.itens import buscar_dados_item

def set_level_admin(nick, novo_lvl):
    """Força um nível e escala atributos."""
    conn = database.conectar()
    cursor = conn.cursor()
    
    nova_vida_max = 100 + (novo_lvl - 1) * 20
    novo_atq = 10 + (novo_lvl - 1) * 2
    nova_def = 5 + (novo_lvl - 1) * 1
    
    try:
        cursor.execute("""
            UPDATE personagens 
            SET level = ?, xp = 0, vida = ?, vida_max = ?, ataque = ?, defesa = ?, critico = ?
            WHERE nick = ? COLLATE NOCASE
        """, (novo_lvl, nova_vida_max, nova_vida_max, novo_atq, nova_def, 1, nick))
        
        sucesso = cursor.rowcount > 0 
        conn.commit()
        return sucesso
    except Exception as e:
        print(f"Erro ao definir nível: {e}")
        return False
    finally:
        conn.close()

def dar_recurso_admin(nick, tipo, quantidade):
    """Adiciona Gold ou Mithril diretamente via comando admin."""
    conn = database.conectar()
    cursor = conn.cursor()
    
    if tipo not in ['gold', 'mithril']:
        conn.close()
        return False, "Tipo inválido."

    cursor.execute(f"UPDATE personagens SET {tipo} = {tipo} + ? WHERE nick = ? COLLATE NOCASE", (quantidade, nick))
    
    sucesso = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return sucesso, f"✅ {quantidade} de {tipo} entregues a {nick}."

def dar_item_admin(nick, item_nome, quantidade):
    """Lógica administrativa para entrega de itens por Nick."""
    jogador = database.buscar_personagem_por_nick(nick)
    if not jogador:
        return False, "Jogador não encontrado."
    
    dados_item = buscar_dados_item(item_nome)
    if not dados_item:
        return False, "Item não existe nos modelos."

    # Chama a função de inventário que já tem a trava de slots
    sucesso, msg = database.adicionar_item_inventario(jogador['user_id'], dados_item['nome'], dados_item['tipo'], quantidade)
    return sucesso, msg

def debug_tabela():
    """Função de debug para verificar estrutura do banco"""
    conn = database.conectar()
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(personagens)")
    # print("COLUNAS:", cursor.fetchall()) # Opcional silenciar no console
    conn.close()