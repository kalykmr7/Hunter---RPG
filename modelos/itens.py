
# --- ARQUIVO: .\modelos\itens.py ---

# Formato: (Nome, Tipo, Subtipo, Valor_Efeito, Descrição, Preço_Gold, Chance_drop, Nivel_max)
LISTA_ITENS_MESTRE = [
    # CONSUMÍVEIS (Cura e Pet)
    ('Poção Pequena', 'consumivel', 'cura', 20, 'Recupera 20% da vida.', 50, 20, 0),
    ('Poção Média', 'consumivel', 'cura', 50, 'Recupera 50% da vida.', 150, 15, 0),
    ('Poção Grande', 'consumivel', 'cura', 85, 'Recupera 85% da vida.', 300, 8, 0),
    ('Fruta arco-íris', 'consumivel', 'pet', 5, 'Dá XP ao seu pet.', 20, 65, 0),
    ('Super-Fruta', 'consumivel', 'pet', 300, 'Uma iguaria para pets.', 500, 0, 0),
    
    # EQUIPAMENTOS (Armas e Armaduras)
    ('Facão', 'equipamento', 'arma', 5, 'Uma lâmina de corte pesado (+5 Atq).', 50, 20, 5),
    ('Set mapa 1', 'equipamento', 'conjunto', 20, 'Bonus de 20 pts nos status base', 100, 20, 5),
    ('Bússola', 'equipamento', 'acessorio', 1, 'Te ajuda a encontrar coisas valiosas, aumenta a sorte.', 150, 20, 5),
    ('Binóculos', 'equipamento', 'acessorio', 1, 'Melhora tua visão e a chance de crítico', 175, 20, 5),
    
    # MATERIAIS E DROPS (Para venda ou quests futuras)
    ('Osso Antigo', 'material', 'venda', 0, 'Um osso velho.', 15, 50, 0),
    ('Essência Mágica', 'material', 'venda', 0, 'Fragmento de energia pura.', 50, 40, 0),
    ('Mithril', 'material', 'venda', 0, 'Uma pena rígida e valiosa.', 100, 1, 0),
    ('Erva medicinal', 'material', 'venda', 0, 'Pode ser usada para fabricar poção de cura.', 100, 20, 0),
    
    # OVOS DE PETS (Nomes amigáveis e funcionais)
    ('Ovo', 'consumivel', 'ovo', 0, 'Um ovo misterioso.', 500, 0, 0),
    ('Ovo [Vila]', 'consumivel', 'ovo', 0, 'Um ovo encontrado na vila.', 500, 0, 0),
    ('Ovo [Região 1]', 'consumivel', 'ovo', 0, 'Um ovo da região 1.', 0, 0, 0),
    ('Ovo [Região 2]', 'consumivel', 'ovo', 0, 'Um ovo da região 2.', 0, 0, 0),
    ('Ovo [Região 3]', 'consumivel', 'ovo', 0, 'Um ovo da região 3.', 0, 0, 0),
    ('Ovo [Região 4]', 'consumivel', 'ovo', 0, 'Um ovo da região 4.', 0, 0, 0),
    ('Ovo [Região 5]', 'consumivel', 'ovo', 0, 'Um ovo da região 5.', 0, 0, 0),
    ('Ovo [Região 6]', 'consumivel', 'ovo', 0, 'Um ovo da região 6.', 0, 0, 0),
    ('Ovo [Região 7]', 'consumivel', 'ovo', 0, 'Um ovo da região 7.', 0, 0, 0),
    ('Ovo [Região 8]', 'consumivel', 'ovo', 0, 'Um ovo da região 8.', 0, 0, 0),
]

def buscar_dados_item(nome_item):
    """Procura o item na lista mestre e retorna seus dados (especialmente o tipo)"""
    from modelos.itens import LISTA_ITENS_MESTRE
    for item in LISTA_ITENS_MESTRE:
        # item[0] é o Nome, item[1] é o Tipo
        if item[0].lower() == nome_item.lower():
            return {"nome": item[0], "tipo": item[1]}
    return None