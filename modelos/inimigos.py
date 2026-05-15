# Aqui ficam os monstos a serem caçados.


# Formato: (Nome, Mapa_ID, Vida, Ataque, Defesa, XP, Gold, Imagem)
LISTA_MONSTROS_MESTRE = [
    # MAPA 1: Acampamento do Pioneiro (Lvl 1)
    ('Borboleta', 1, 25, 10, 1, 12, 8, 'borboleta.png'),
    ('Centopéia', 1, 26, 6, 10, 15, 10, 'centopeia.png'),
    ('Grilo', 1, 27, 4, 1, 10, 5, 'grilo.png'),
    ('Barata', 1, 28, 7, 2, 10, 12, 'barata.png'),
    ('Aranha', 1, 30, 9, 3, 12, 20, 'aranha.png'),

    # MAPA 2: Bosque Queimado (Lvl 4)
    ('Cinzelha', 2, 35, 10, 4, 13, 25, 'cinzelha.jpg'),
    ('Lobo Calcinado', 2, 36, 11, 4, 14, 28, 'lobo_calcinado.jpg'),
    ('Tronco Fumegante', 2, 37, 12, 5, 15, 30, 'tronco.jpg'),
    ('Mariposa de Fuligem', 2, 38, 13, 5, 16, 32, 'mariposa.jpg'),
    ('Serpe Braseira', 2, 40, 15, 6, 17, 33, 'naja.jpg'),

    # MAPA 3: Ponte dos Suspiros (Lvl 6)
    ('Eco Perdido', 3, 45, 18, 8, 18, 50, 'eco.jpg'),
    ('Gárgula Rachada', 3, 46, 19, 9, 19, 52, 'gargula.jpg'),
    ('Vulto do Abismo', 3, 47, 20, 9, 20, 55, 'vulto.jpg'),
    ('Corvo de Musgo', 3, 48, 21, 10, 21, 56, 'corvo.jpg'),
    ('Guardião da Ponte', 3, 50, 23, 12, 22, 57, 'guardiao.jpg'),

    # MAPA 4: Tumba do Caçador Ancião (Lvl 8)
    ('Esqueleto Arqueiro', 4, 55, 26, 14, 23, 58, 'esqueleto.jpg'),
    ('Cão Espectral', 4, 56, 27, 15, 24, 59, 'cao.jpg'),
    ('Estátua Animada', 4, 57, 28, 16, 25, 60, 'estatua.jpg'),
    ('Caçador Penitente', 4, 58, 29, 17, 26, 61, 'cacador.jpg'),
    ('Rei Caçador Ancião', 4, 60, 32, 20, 27, 62, 'espirito.jpg'),

    # MAPA 5: Cachoeira da Serenidade (Lvl 10)
    ('Ninfa da Água', 5, 65, 35, 22, 30, 63, 'ninfa.jpg'),
    ('Carpa Cristalina', 5, 66, 36, 23, 31, 64, 'carpa.jpg'),
    ('Limo Vivo', 5, 67, 37, 24, 32, 65, 'limo.jpg'),
    ('Libélula Carnívora', 5, 68, 38, 25, 33, 66, 'libelula.jpg'),
    ('Elemental do Lago', 5, 75, 42, 28, 34, 67, 'elemental.jpg'),

    # MAPA 6: Desfiladeiro do Eco (Lvl 12)
    ('Morcego Sônico', 6, 80, 45, 30, 40, 68, 'morcego.png'),
    ('Golem de Sedimento', 6, 82, 46, 35, 42, 69, 'golem.png'),
    ('Cabrito Rupestre', 6, 84, 47, 32, 44, 70, 'cabrito.png'),
    ('Víbora de Quartzo', 6, 86, 48, 33, 46, 71, 'vibora.png'),
    ('Águia de Mica', 6, 95, 55, 38, 48, 72, 'aguia.png'),

    # MAPA 7: Pico do Observador (Lvl 14)
    ('Coruja Astral', 7, 105, 60, 40, 52, 73, 'coruja.png'),
    ('Autômato de Bronze', 7, 108, 62, 45, 54, 74, 'automato.png'),
    ('Lobo do Gelo Eterno', 7, 110, 64, 42, 56, 75, 'lobo.png'),
    ('Fragmento de Cometa', 7, 115, 68, 44, 58, 76, 'fragmento.png'),
    ('Oráculo Congelado', 7, 130, 75, 50, 60, 77, 'oraculo.png'),

    # MAPA 8: Portal das Montanhas Brancas (Lvl 16)
    ('Sentinela Rúnica', 8, 145, 85, 55, 64, 78, 'sentinela.png'),
    ('Serpente de Aurora', 8, 150, 90, 60, 66, 79, 'serpente_aurora.png'),
    ('Eco do Pioneiro', 8, 155, 95, 65, 68, 80, 'eco_pioneiro.jpg'),
    ('Golem do Portal', 8, 160, 100, 80, 70, 81, 'golem_portal.jpg'),
    ('Guardião das Montanhas Brancas', 8, 200, 130, 100, 90, 82, 'guardiao_montanhas.jpg'),
]


# Formato: (Mapa_ID, Andar, Nome, Vida, Ataque, Defesa, XP, Gold, Imagem)
LISTA_BOSS_MASMORRAS = [
    # Masmorra 1: Ruínas do Acampamento (Recomendado Lvl 10)
    (1, 1, "Guarda Esqueleto", 150, 45, 30, 150, 200, "boss_andar1.png"),
    (1, 2, "Cavalheiro Sombrio", 300, 60, 45, 300, 400, "boss_andar2.png"),
    (1, 3, "General Decaído", 600, 85, 65, 1000, 1500, "boss_andar3.png"),
]




# Itens que podem cair em cada mapa. 
# Formato: (Mapa_ID, Item_Nome, Chance_Global)
# A chance global é a probabilidade de cair QUALQUER item ao matar um monstro.

LISTA_DROPS_MAPAS = [
    # Drops Mapas Iniciais (1 e 2)
    (1, 'Fruta Arco-íris', 60),
    (1, 'Poção Pequena', 15),
    (1, 'Carapaça Resistente', 50),
    (1, 'Essência Mágica', 10),
    (1, 'Mithril', 1),

    (2, 'Fruta Arco-íris', 60),
    (2, 'Poção Pequena', 20),
    (2, 'Osso Carbonizado', 20),
    (2, 'Essência Mágica', 10),
    (2, 'Mithril', 1),

    # Drops Mapas Intermediários (3, 4 e 5)
    (3, 'Fruta Arco-íris', 60),
    (3, 'Poção Pequena', 20),
    (3, 'Essência Mágica', 10),
    (3, 'Pedra Afiada', 20),
    (3, 'Mithril', 1),

    (4, 'Fruta Arco-íris', 60),
    (4, 'Poção Média', 20),
    (4, 'Essência Mágica', 15),
    (4, 'Lamina Antiga', 20),
    (4, 'Mithril', 1),
    
    (5, 'Fruta Arco-íris', 60),
    (5, 'Poção Média', 25),
    (5, 'Poção Grande', 5),
    (5, 'Essência Mágica', 20),
    (5, 'Lagrima Elemental', 20),
    (5, 'Mithril', 1),

    # Drops Mapas Avançados (6, 7 e 8)
    (6, 'Fruta Arco-íris', 60),
    (6, 'Poção Grande', 15),
    (6, 'Essência Mágica', 25),
    (6, 'Fragmento de Cristal', 25),
    (6, 'Mithril', 1),

    (7, 'Fruta Arco-íris', 60),
    (7, 'Poção Grande', 20),
    (7, 'Estalactite', 20),
    (7, 'Mithril', 1),
    
    (8, 'Fruta Arco-íris', 60),
    (8, 'Poção Grande', 30),
    (8, 'Essência Mágica', 30),
    (8, 'Runa Antiga', 20),
    (8, 'Mithril', 1),
]