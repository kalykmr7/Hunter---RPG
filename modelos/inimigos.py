# Aqui ficam os monstos a serem caçados.


# Formato: (Nome, Mapa_ID, Vida, Ataque, Defesa, XP, Gold, Imagem)
LISTA_MONSTROS_MESTRE = [
    # MAPA 1: Acampamento do Pioneiro (Lvl 1)
    ('Borboleta', 1, 25, 5, 1, 12, 8, 'borboleta.png'),
    ('Centopéia', 1, 26, 6, 2, 15, 10, 'centopeia.png'),
    ('Grilo', 1, 27, 4, 1, 10, 5, 'grilo.png'),
    ('Barata', 1, 28, 7, 2, 18, 12, 'barata.png'),
    ('Aranha', 1, 30, 9, 3, 25, 20, 'aranha.png'),

    # MAPA 2: Bosque Queimado (Lvl 4)
    ('Cinzelha', 2, 60, 15, 5, 40, 30, 'cinzelha.jpg'),
    ('Lobo Calcinado', 2, 80, 18, 6, 50, 40, 'lobo_calcinado.jpg'),
    ('Tronco Fumegante', 2, 100, 12, 10, 55, 45, 'tronco.jpg'),
    ('Mariposa de Fuligem', 2, 55, 22, 3, 45, 35, 'mariposa.jpg'),
    ('Serpe Braseira', 2, 120, 25, 8, 70, 60, 'naja.jpg'),

    # MAPA 3: Ponte dos Suspiros (Lvl 6)
    ('Eco Perdido', 3, 110, 30, 10, 85, 70, 'eco_perdido.png'),
    ('Gárgula Rachada', 3, 160, 25, 15, 100, 80, 'gargula.png'),
    ('Vulto do Abismo', 3, 100, 40, 5, 110, 90, 'vulto.png'),
    ('Corvo de Musgo', 3, 90, 35, 8, 80, 65, 'corvo.png'),
    ('Guardião da Ponte', 3, 250, 45, 20, 180, 150, 'guardiao_ponte.png'),

    # MAPA 4: Tumba do Caçador Ancião (Lvl 8)
    ('Esqueleto Arqueiro', 4, 150, 50, 15, 150, 120, 'arqueiro.png'),
    ('Cão Espectral', 4, 180, 55, 12, 170, 140, 'cao_espectral.png'),
    ('Estátua Animada', 4, 300, 40, 30, 200, 160, 'estatua.png'),
    ('Caçador Penitente', 4, 220, 65, 18, 250, 200, 'cacador_penitente.png'),
    ('Rei Caçador Ancião', 4, 500, 80, 40, 500, 400, 'rei_anciao.png'),

    # MAPA 5: Cachoeira da Serenidade (Lvl 10)
    ('Ninfa d’Água', 5, 280, 75, 25, 350, 300, 'ninfa.png'),
    ('Carpa Cristalina', 5, 200, 60, 40, 300, 250, 'carpa.png'),
    ('Limo Vivo', 5, 400, 50, 50, 380, 320, 'limo.png'),
    ('Libélula de Orvalho', 5, 250, 90, 20, 400, 350, 'libelula.png'),
    ('Elemental do Lago', 5, 650, 110, 60, 700, 600, 'elemental_lago.png'),

    # MAPA 6: Desfiladeiro do Eco (Lvl 12)
    ('Morcego Sônico', 6, 450, 130, 40, 800, 700, 'morcego.png'),
    ('Golem de Sedimento', 6, 850, 100, 100, 950, 850, 'golem_sedimento.png'),
    ('Cabrito Rupestre', 6, 500, 140, 50, 850, 750, 'cabrito.png'),
    ('Víbora de Quartzo', 6, 600, 160, 60, 1000, 900, 'vibora.png'),
    ('Roc dos Picos', 6, 1200, 200, 80, 1500, 1200, 'roc.png'),

    # MAPA 7: Pico do Observador (Lvl 14)
    ('Coruja Astral', 7, 800, 220, 70, 1800, 1500, 'coruja_astral.png'),
    ('Autômato de Bronze', 7, 1500, 180, 150, 2200, 1800, 'automato.png'),
    ('Lobo do Gelo Eterno', 7, 1200, 250, 100, 2000, 1700, 'lobo_gelo.png'),
    ('Fragmento de Cometa', 7, 900, 300, 80, 2500, 2000, 'cometa.png'),
    ('Oráculo Congelado', 7, 2000, 350, 120, 4000, 3500, 'oraculo.png'),

    # MAPA 8: Portal das Montanhas Brancas (Lvl 16)
    ('Sentinela Rúnica', 8, 2500, 400, 200, 5500, 4500, 'sentinela.png'),
    ('Serpente de Aurora', 8, 2200, 500, 150, 6000, 5000, 'serpente_aurora.png'),
    ('Eco do Pioneiro', 8, 3000, 450, 250, 7000, 6000, 'eco_pioneiro.png'),
    ('Golem do Portal', 8, 5000, 350, 400, 8500, 7500, 'golem_portal.png'),
    ('Guardião das Montanhas Brancas', 8, 8000, 600, 500, 15000, 12000, 'guardiao_montanhas.png'),
]


# Itens que podem cair em cada mapa. 
# Formato: (Mapa_ID, Item_Nome, Chance_Global)
# A chance global é a probabilidade de cair QUALQUER item ao matar um monstro.
LISTA_DROPS_MAPAS = [
    # Drops Mapas Iniciais (1 e 2)
    (1, 'Maçã', 20),
    (1, 'Poção Pequena', 15),
    (1, 'Osso Antigo', 10),

    (2, 'Poção Pequena', 20),
    (2, 'Maçã', 15),
    (2, 'Osso Antigo', 20),
    (2, 'Essência Mágica', 5),

    # Drops Mapas Intermediários (3, 4 e 5)
    (3, 'Poção Média', 15),
    (3, 'Essência Mágica', 10),
    (3, 'Osso Antigo', 20),

    (4, 'Poção Média', 20),
    (4, 'Essência Mágica', 15),
    (4, 'Espada de Madeira', 2), # Raridade!

    (5, 'Poção Média', 25),
    (5, 'Poção Grande', 5),
    (5, 'Essência Mágica', 20),

    # Drops Mapas Avançados (6, 7 e 8)
    (6, 'Poção Grande', 15),
    (6, 'Pena de Wyvern', 10),
    (6, 'Essência Mágica', 25),

    (7, 'Poção Grande', 20),
    (7, 'Pena de Wyvern', 15),
    (7, 'Armadura de Couro', 2), # Raro!

    (8, 'Poção Grande', 30),
    (8, 'Pena de Wyvern', 25),
    (8, 'Essência Mágica', 30),
]