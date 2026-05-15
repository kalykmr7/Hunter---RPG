# Aqui vou deixar as informaçõs sobre os todos os monstros do game

import random

pets = [
    # --- PETS INICIAIS (BASEADOS NOS MODELOS EXISTENTES) ---
    {"nome": "Falcão filhote", "vida": 45, "ataque": 4, "defesa": 2, "agilidade": 8, "imagem": "pet_falcao_filhote.png", "bonus": "+2% HP Máximo", "raridade": "Comum", "mapa_origem": 0},
    {"nome": "Lobo filhote", "vida": 40, "ataque": 5, "defesa": 3, "agilidade": 5, "imagem": "pet_lobo_filhote.png", "bonus": "+2% de Ataque", "raridade": "Comum", "mapa_origem": 0},
    {"nome": "Tartaruga filhote", "vida": 60, "ataque": 2, "defesa": 5, "agilidade": 1, "imagem": "pet_tartaruga_filhote.png", "bonus": "+2% de Defesa", "raridade": "Comum", "mapa_origem": 0},

    # --- PETS TEMÁTICOS DOS MAPAS (RARIDADE RARO) ---
    {
        "nome": "Escudeiro de Casca", "vida": 50, "ataque": 3, "defesa": 6, "agilidade": 2, 
        "imagem": "pet_escudeiro_casca.jpg", "bonus": "+10% de Defesa", "raridade": "Raro", "mapa_origem": 1
    },
    {
        "nome": "Raposa de Cinza", "vida": 42, "ataque": 7, "defesa": 3, "agilidade": 6, 
        "imagem": "pet_raposa_cinza.jpg", "bonus": "+10% de Ataque", "raridade": "Raro", "mapa_origem": 2
    },
    {
        "nome": "Morcego de Ébano", "vida": 38, "ataque": 6, "defesa": 2, "agilidade": 10, 
        "imagem": "pet_morcego_ebano.jpg", "bonus": "+10% de XP", "raridade": "Raro", "mapa_origem": 3
    },
    {
        "nome": "Serpente de Lodo", "vida": 55, "ataque": 4, "defesa": 5, "agilidade": 4, 
        "imagem": "pet_serpente_lodo.jpg", "bonus": "+10% Sorte", "raridade": "Raro", "mapa_origem": 4
    },
    {
        "nome": "Escorpião de Bronze", "vida": 48, "ataque": 8, "defesa": 4, "agilidade": 5, 
        "imagem": "pet_escorpiao_bronze.jpg", "bonus": "+10% de Gold", "raridade": "Raro", "mapa_origem": 5
    },
    {
        "nome": "Draco de Mica", "vida": 52, "ataque": 5, "defesa": 6, "agilidade": 7, 
        "imagem": "pet_draco_mica.jpg", "bonus": "+10% de Mithril Encontrado", "raridade": "Raro", "mapa_origem": 6
    },
    {
        "nome": "Coruja de Vidro Astral", "vida": 50, "ataque": 6, "defesa": 5, "agilidade": 12, 
        "imagem": "pet_coruja_astral.jpg", "bonus": "+10% de Critico", "raridade": "Raro", "mapa_origem": 7
    },
    {
        "nome": "Sentinela de Marfim", "vida": 70, "ataque": 9, "defesa": 9, "agilidade": 3, 
        "imagem": "pet_sentinela_marfim.jpg", "bonus": "+10% de Vida", "raridade": "Raro", "mapa_origem": 8
    }
]

def sortear_pet(mapa_id=0):
    """
    Sorteia um pet. 
    Se o mapa_id for passado (maior que 0), tenta dar o pet da região.
    Se mapa_id for 0 (como no cadastro), dá um dos iniciais.
    """
    # Lista filtrada
    raro_do_mapa = [p for p in pets if p['mapa_origem'] == mapa_id and p['raridade'] == "Raro"]
    
    # No cadastro ou mapas iniciais, chance fixa nos Pets Iniciais
    if mapa_id == 0 or not raro_do_mapa:
        iniciais = [p for p in pets if p['raridade'] == "Comum"]
        return random.choice(iniciais)
    
    # Em mapas específicos: 30% de vir o Pet Raro do Mapa, senão um inicial
    if random.randint(1, 100) <= 30:
        return random.choice(raro_do_mapa)
    else:
        iniciais = [p for p in pets if p['raridade'] == "Comum"]
        return random.choice(iniciais)

def buscar_modelo_pet(nome_procurado):
    """Procura um pet na lista de modelos pelo nome exato"""
    for p in pets:
        if p['nome'].lower() == nome_procurado.lower():
            return p
    return None