
# --- ARQUIVO: .\modelos\itens.py ---

# Formato: (Nome, Tipo, Subtipo, Valor_Efeito, Descrição, Preço_Gold)
LISTA_ITENS_MESTRE = [
    # CONSUMÍVEIS (Cura e Pet)
    ('Poção Pequena', 'consumivel', 'cura', 20, 'Recupera 20% da vida.', 50),
    ('Poção Média', 'consumivel', 'cura', 50, 'Recupera 50% da vida.', 150),
    ('Poção Grande', 'consumivel', 'cura', 85, 'Recupera 85% da vida.', 300),
    ('Maçã', 'consumivel', 'pet', 10, 'Dá XP ao seu pet.', 20),
    
    # EQUIPAMENTOS (Armas e Armaduras)
    ('Espada de Madeira', 'equipamento', 'arma', 5, 'Uma espada simples (+5 Atq).', 100),
    ('Armadura de Couro', 'equipamento', 'armadura', 3, 'Proteção básica (+3 Def).', 120),
    ('Facão', 'equipamento', 'arma', 10, 'Uma lâmina de corte pesado (+10 Atq).', 200),
    
    # MATERIAIS E DROPS (Para venda ou quests futuras)
    ('Osso Antigo', 'material', 'venda', 0, 'Um osso velho que pode ser vendido.', 15),
    ('Essência Mágica', 'material', 'venda', 0, 'Fragmento de energia pura.', 50),
    ('Pena de Wyvern', 'material', 'venda', 0, 'Uma pena rígida e valiosa.', 100),
]